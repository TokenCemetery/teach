---
title: "10. ZeRO estágio 3 e FSDP: particionando também os parâmetros"
description: "Particionar os próprios parâmetros significa reconstruí-los sob demanda, e esse é o primeiro custo disso"
type: lesson
---

# Lição 10. ZeRO estágio 3 e FSDP: particionando também os parâmetros

**Ligação com a missão:** "Explicar o que o ZeRO/FSDP particionam, por que o paralelismo de dados sozinho fica sem memória antes de ficar sem compute e quando o paralelismo de tensor ou de pipeline vale o seu custo de comunicação" é o quarto item em O sucesso se parece com isto. A Lição 9 cobriu os dois estágios que particionam de graça o estado do otimizador e os gradientes; esta lição cobre o terceiro, que particiona os próprios parâmetros, e a sua API real.
**Fonte principal:** [Documentação: "Fully Sharded Data Parallel", PyTorch](https://pytorch.org/docs/stable/fsdp.html)
**Pré-requisitos:** [Lição 9](0009-zero-stage-1-and-2-partitioning-optimizer-state-and-gradients.md)

## Aquecimento

1. ▢ Que redução de memória o estágio 2 do ZeRO (`P_os+g`) dá e a que custo de comunicação em relação ao paralelismo de dados comum?

<details markdown="1"><summary>Verificação</summary>

Uma redução de memória de 8x, com o mesmo volume de comunicação do paralelismo de dados comum: nenhum dado extra precisa se mover, já que o estado do otimizador e os gradientes só são necessários localmente, pelo dispositivo responsável pela fatia correspondente.

</details>

2. ▢ Por que o estado do otimizador e os gradientes podem ser particionados sem comunicação adicional, de um jeito que o assunto desta lição não pode?

<details markdown="1"><summary>Verificação</summary>

Porque apenas o dispositivo responsável por uma dada fatia dos parâmetros precisa do estado do otimizador ou do gradiente dessa fatia. O forward e o backward pass de cada dispositivo, ao contrário, precisam de todos os parâmetros do modelo, e não só dos que ele possui, e é isso que a Lição 10 precisa levar em conta.

</details>

## Saiba isto

### A última peça: particionando os parâmetros

**`P_os+g+p`**, o terceiro estágio do ZeRO, particiona os próprios parâmetros além do estado do otimizador e dos gradientes que o estágio 2 já particiona: cada dispositivo guarda em repouso apenas `1/Nd` dos parâmetros, em vez de uma cópia completa. Rajbhandari et al. relatam que a redução de memória desse estágio escala linearmente com o grau de dados paralelos `Nd`: dividir em 64 dispositivos rende uma redução de memória de 64x, e é isso que faz o resultado principal deles funcionar: eles estimam que um modelo de um trilhão de parâmetros em Adam de precisão mista precisa de cerca de 16 terabytes para os seus estados do modelo, que divididos entre 1.024 GPUs dão cerca de 16 GB por dispositivo, confortavelmente dentro de uma GPU de 32 GB.

Essa redução não é de graça como os estágios 1 e 2 eram. O forward e o backward pass de cada dispositivo ainda precisam de todos os parâmetros, e não só dos `1/Nd` que ele guarda, então os parâmetros que um dispositivo não guarda precisam ser reconstruídos a partir dos outros dispositivos no momento em que são necessários e depois descartados de novo assim que aquele cálculo termina. Rajbhandari et al. relatam que isso custa um aumento modesto de 50% no volume de comunicação em relação ao paralelismo de dados comum, em troca de uma redução de memória que continua escalando à medida que mais dispositivos são adicionados, em vez de estacionar em 8x como os estágios 1 e 2.

### O mecanismo: reunir sob demanda e depois liberar

O padrão que o estágio 3 usa é: guarde em repouso apenas a sua própria fatia dos parâmetros; logo antes de uma camada precisar dos seus parâmetros completos para um cálculo de forward ou backward, faça um **all-gather** dos pedaços que faltam dos outros dispositivos para reconstruir temporariamente o tensor de parâmetros completo; quando o cálculo dessa camada terminar, libere a cópia reconstruída e volte a guardar apenas a sua própria fatia. É a mesma operação coletiva de all-gather de qualquer outro caso, apenas acionada com muito mais frequência, uma vez por camada por passada, e não uma vez por passo de treinamento como a sincronização de gradientes no paralelismo de dados comum.

### FSDP: a mesma ideia, como uma API real

O `FullyShardedDataParallel` do PyTorch, comumente abreviado como **FSDP**, implementa exatamente esse padrão, e a sua própria documentação diz isso diretamente: ela se descreve como "inspirada no ... estágio 3 do ZeRO do DeepSpeed". Envolver um módulo em FSDP particiona os seus parâmetros entre os dispositivos de dados paralelos e, durante o forward e o backward pass, o FSDP substitui os parâmetros do módulo por visões reconstruídas, reunidas sob demanda, o mesmo padrão de reunir e depois liberar que esta lição acabou de descrever em abstrato. O FSDP também expõe estratégias de particionamento mais leves, que particionam apenas os gradientes e o estado do otimizador deixando os parâmetros sem partição, que é o mesmo tradeoff que o estágio 2 faz, e não o do estágio 3: menos memória economizada, mas nenhum tráfego extra de all-gather de parâmetros durante cada forward e backward pass.

## Prática

1. ▢ Usando o escalonamento relatado do estágio 3 do ZeRO, que redução de memória uma equipe deve esperar ao dividir os parâmetros, os gradientes e o estado do otimizador de um modelo entre 32 dispositivos?

<details markdown="1"><summary>Verificação</summary>

Cerca de 32x, já que Rajbhandari et al. relatam que a redução de memória do estágio 3 escala linearmente com o grau de dados paralelos `Nd` (64 dispositivos dão 64x no exemplo deles, então 32 dispositivos dão aproximadamente a metade disso).

</details>

2. ▢ Por que particionar os próprios parâmetros exige comunicação extra que particionar o estado do otimizador e os gradientes não exigia?

    - a) Os parâmetros são armazenados em uma precisão numérica diferente, mais cara de transmitir
    - b) O forward e o backward pass de cada dispositivo precisam do conjunto completo de parâmetros, e não só da fatia que ele possui, então as fatias que faltam têm de ser reunidas de outros dispositivos sob demanda
    - c) O particionamento de parâmetros exige um protocolo de rede mais lento que o particionamento de gradientes
    - d) Na verdade ele não exige comunicação extra; o número de 50% do artigo é de outra comparação

<details markdown="1"><summary>Verificação</summary>

**b)** é o mecanismo real: ao contrário do estado do otimizador e dos gradientes, de que só o dispositivo dono precisa, os parâmetros são necessários a todos os dispositivos para o cálculo de forward e backward de cada camada, então um all-gather precisa reconstruir as fatias que um dispositivo não guarda. (a), (c) e (d) não descrevem a razão real.

</details>

3. ▢ Uma equipe escolhe a estratégia `SHARD_GRAD_OP` do FSDP do PyTorch em vez de `FULL_SHARD`. A qual estágio do ZeRO isso corresponde e que tradeoff ela faz em relação a `FULL_SHARD`?

<details markdown="1"><summary>Dica</summary>

`SHARD_GRAD_OP` deixa os parâmetros sem partição e expostos na sua forma completa, particionando apenas os gradientes e o estado do otimizador.

</details>

<details markdown="1"><summary>Verificação</summary>

Corresponde ao estágio 2 do ZeRO. Economiza menos memória que `FULL_SHARD` (estágio 3), já que os parâmetros não são particionados, mas também evita o tráfego extra de all-gather de que o estágio 3 precisa para reconstruir os parâmetros sob demanda durante cada forward e backward pass.

</details>

## Prática no mundo real

- [ ] Leia a documentação do FSDP do PyTorch (linkada acima) e encontre a descrição do que acontece com os parâmetros de um módulo envolvido durante o forward pass. Escreva uma frase ligando isso ao padrão de "reunir e depois liberar" que esta lição descreve.
- [ ] Usando o exemplo de um trilhão de parâmetros e 1.024 GPUs desta lição (cerca de 16 TB de estados do modelo, 16 GB por dispositivo), refaça o mesmo cálculo para um modelo de 100 bilhões de parâmetros dividido entre 64 dispositivos e verifique se ele cabe confortavelmente em uma GPU de 80 GB.
- [ ] Amanhã: encontre um exemplo de configuração (na documentação do FSDP ou do DeepSpeed) que defina uma estratégia de particionamento explicitamente e identifique a qual estágio do ZeRO essa configuração específica corresponde, usando as descrições desta lição e da Lição 9 do que cada estágio particiona.

## Para ir além

- [Artigo científico: "ZeRO: Memory Optimizations Toward Training Trillion Parameter Models", Rajbhandari et al., 2019](https://arxiv.org/abs/1910.02054)
- [Recursos](../RESOURCES.md)

---

Não ficou claro? Releia a fonte principal no topo, já que esta lição a comprime e é na compressão que o entendimento escapa. Consulte o [glossário](../GLOSSARY.md) para qualquer termo que pareceu escorregadio.

Se o problema é a lição em si, e não o material, isso é um defeito: [abra uma issue](https://github.com/TokenCemetery/teach/issues).
