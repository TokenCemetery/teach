---
title: "13. Paralelismo de pipeline: dividindo as camadas do modelo"
description: "Atribuir camadas consecutivas a dispositivos diferentes e o tempo ocioso que isso custa no início e no fim de cada batch"
type: lesson
---

# Lição 13. Paralelismo de pipeline: dividindo as camadas do modelo

**Ligação com a missão:** "Explicar o que o ZeRO/FSDP particionam, por que o paralelismo de dados sozinho fica sem memória antes de ficar sem compute e quando o paralelismo de tensor ou de pipeline vale o seu custo de comunicação" é o quarto item em O sucesso se parece com isto. A Lição 12 cobriu dividir o próprio cálculo de uma camada entre dispositivos; esta lição cobre dividir as camadas do modelo entre dispositivos.
**Fonte principal:** [Artigo científico: "Efficient Large-Scale Language Model Training on GPU Clusters Using Megatron-LM", Narayanan et al., 2021](https://arxiv.org/abs/2104.04473)
**Pré-requisitos:** [Lição 12](0012-tensor-parallelism-splitting-a-layers-matrices.md)

## Aquecimento

1. ▢ Na divisão do MLP do paralelismo de tensor, por que dividir a primeira matriz de pesos ao longo das colunas, e não das linhas, evita precisar de uma etapa de sincronização antes de aplicar a `GeLU`?

<details markdown="1"><summary>Verificação</summary>

Uma divisão por colunas divide a dimensão de saída, então a fatia do resultado de cada dispositivo já é completa e correta; uma divisão por linhas dividiria a dimensão sobre a qual se soma, deixando cada dispositivo com apenas uma soma parcial, e a `GeLU` não pode ser aplicada corretamente a uma soma parcial, já que é não linear.

</details>

## Saiba isto

### Dividir a profundidade do modelo, e não a largura de uma única camada

O **paralelismo de pipeline** adota uma terceira abordagem, diferente tanto do ZeRO (etapa 5) quanto do paralelismo de tensor (Lição 12): em vez de dividir o que uma camada qualquer calcula, ele particiona as próprias camadas do modelo entre dispositivos. Para um modelo construído a partir do mesmo bloco transformer repetido muitas vezes, isso é direto: cada dispositivo, ou **estágio de pipeline**, recebe uma sequência contígua e de tamanho igual de camadas do transformer, e o forward pass de um exemplo de treinamento atravessa os dispositivos em sequência, estágio por estágio, do jeito que uma linha de montagem física leva uma peça de estação em estação.

### Por que um batch é dividido em micro-batches

Se um batch inteiro tivesse de passar por completo pelo estágio 1 antes de o estágio 2 poder começar qualquer trabalho com ele, todos os estágios menos um ficariam ociosos quase o tempo todo; não haveria nada de pipeline nisso. A abordagem de Narayanan et al. divide em vez disso um batch em **micro-batches** menores e faz a execução deles em pipeline: enquanto o estágio 1 trabalha no micro-batch 2, o estágio 2 pode estar trabalhando ao mesmo tempo na saída do micro-batch 1, do mesmo jeito que uma linha de montagem real tem várias peças em andamento nas suas estações ao mesmo tempo, em vez de terminar uma peça por completo antes de começar a próxima.

### A bolha do pipeline

Mesmo com os micro-batches escalonados pelo pipeline, há um tempo ocioso inevitável no início de um batch, antes de todo estágio ter algo para trabalhar, e no fim, depois que o último micro-batch saiu dos estágios iniciais e só os estágios finais ainda têm trabalho para terminar. Narayanan et al. chamam esse tempo ocioso de **bolha do pipeline**, e ele é um custo genuíno: quanto mais estágios de pipeline, mais desse tempo ocioso se acumula em relação à computação útil, a menos que se usem micro-batches suficientes por batch para manter o pipeline mais cheio por mais tempo entre o enchimento e o esvaziamento inevitáveis em cada ponta.

### Por que o pipeline precisa de flushes periódicos

Uma sutileza com que Narayanan et al. têm cuidado: o pipeline ingênuo, executado puramente por throughput e sem nenhuma outra restrição, pode deixar o backward pass de um micro-batch ver uma versão diferente, já atualizada, dos pesos em relação à que o seu próprio forward pass usou, se outros micro-batches mais adiante no pipeline tiverem terminado o passo do otimizador primeiro. Isso quebra o significado síncrono comum de um passo de treinamento, em que cada exemplo de um batch deve ver um único conjunto consistente de pesos ao longo do seu próprio forward e backward pass. Para manter essa garantia com exatidão, Narayanan et al. introduzem **flushes de pipeline** periódicos: pontos em que o pipeline pode esvaziar por completo e o passo do otimizador de todos os dispositivos acontece junto, sincronizado, antes de os micro-batches do próximo batch começarem a encher o pipeline de novo. Esse flush também é onde a bolha descrita acima de fato ocorre; é o preço pago para manter a semântica síncrona do otimizador em vez de deixar as versões dos pesos derivarem entre os micro-batches.

## Prática

1. ▢ Um modelo com 8 camadas de transformer é dividido em 4 estágios de pipeline, 2 camadas cada. Se um batch inteiro tivesse de completar totalmente o estágio 1 antes de o estágio 2 poder começar qualquer trabalho, o que aconteceria com os estágios 2 a 4 enquanto o estágio 1 trabalha?

<details markdown="1"><summary>Verificação</summary>

Eles ficariam ociosos, já que nenhum deles teria nada para calcular até o estágio 1 terminar o batch inteiro e passar a sua saída adiante. Esse é exatamente o problema que dividir um batch em micro-batches pretende evitar.

</details>

2. ▢ Qual destas descreve melhor o que é a bolha do pipeline?

    - a) A memória extra usada para armazenar ativações nas fronteiras dos estágios do pipeline
    - b) Tempo ocioso no início e no fim de um batch, enquanto o pipeline enche ou esvazia, que não adiciona computação útil
    - c) O atraso de comunicação entre um all-reduce do paralelismo de tensor e a multiplicação de matrizes seguinte
    - d) Uma pausa deliberada inserida para deixar os dispositivos esfriarem entre os batches

<details markdown="1"><summary>Verificação</summary>

**b)** é exatamente como Narayanan et al. a nomeiam. (a) descreve um custo real do pipeline, mas não a bolha especificamente. (c) descreve uma preocupação do paralelismo de tensor, e não do paralelismo de pipeline. (d) não é uma razão real para o tempo ocioso.

</details>

3. ▢ Por que os flushes periódicos do pipeline importam para a correção, e não só para o throughput?

<details markdown="1"><summary>Dica</summary>

Pergunte o que poderia dar errado para o backward pass de um micro-batch específico se outros micro-batches mais adiante no pipeline já tivessem disparado um passo do otimizador.

</details>

<details markdown="1"><summary>Verificação</summary>

Sem um flush, o backward pass de um micro-batch poderia ver uma versão diferente, já atualizada, dos pesos em relação à que o seu próprio forward pass usou, se outros micro-batches completassem o passo do otimizador primeiro. Isso quebra a semântica síncrona do otimizador, em que cada exemplo de um batch deve ver um único conjunto consistente de pesos ao longo do seu próprio forward e backward pass. Um flush deixa o pipeline esvaziar e o passo do otimizador de todos os dispositivos acontecer junto, preservando essa garantia ao custo da bolha.

</details>

4. ▢ Uma equipe aumenta o número de micro-batches por batch sem mudar o número de estágios de pipeline. Que efeito isso teria na fração de tempo perdida para a bolha do pipeline?

<details markdown="1"><summary>Verificação</summary>

Reduziria a fração de tempo perdida para a bolha, já que o custo fixo de enchimento e esvaziamento é diluído em mais computação útil de micro-batches entre as pontas. A bolha em si não desaparece, mas se torna uma parcela menor do tempo total gasto por batch.

</details>

## Prática no mundo real

- [ ] Desenhe, no papel, quatro estágios de pipeline e quatro micro-batches e esboce uma linha do tempo mostrando qual estágio trabalha em qual micro-batch a cada passo de tempo, incluindo as células ociosas no início e no fim que representam a bolha.
- [ ] Leia a seção do artigo do Megatron-LM (linkado acima) que descreve os flushes de pipeline e escreva uma frase com as suas próprias palavras distinguindo o que um flush garante do que os micro-batches sozinhos garantem.
- [ ] Amanhã: sem olhar adiante, escreva uma previsão de uma frase para a Lição 14: dado que o paralelismo de tensor precisa de um all-reduce para cada camada enquanto o paralelismo de pipeline só precisa passar ativações entre um punhado de fronteiras de estágio, qual dos dois você esperaria que tolerasse melhor uma conexão de rede mais lenta e de maior distância entre os dispositivos?

## Para ir além

- [Artigo científico: "Efficient Large-Scale Language Model Training on GPU Clusters Using Megatron-LM", Narayanan et al., 2021](https://arxiv.org/abs/2104.04473)
- [Recursos](../RESOURCES.md)

---

Não ficou claro? Releia a fonte principal no topo, já que esta lição a comprime e é na compressão que o entendimento escapa. Consulte o [glossário](../GLOSSARY.md) para qualquer termo que pareceu escorregadio.

Se o problema é a lição em si, e não o material, isso é um defeito: [abra uma issue](https://github.com/TokenCemetery/teach/issues).
