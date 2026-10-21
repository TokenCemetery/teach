---
title: "8. Por que só o paralelismo de dados fica sem memória"
description: "Contar exatamente o que um otimizador Adam de precisão mista guarda por parâmetro e onde isso bate em um muro"
type: lesson
---

# Lição 8. Por que só o paralelismo de dados fica sem memória

**Ligação com a missão:** "Explicar o que o ZeRO/FSDP particionam, por que o paralelismo de dados sozinho fica sem memória antes de ficar sem compute e quando o paralelismo de tensor ou de pipeline vale o seu custo de comunicação" é o quarto item em O sucesso se parece com isto. A Lição 7 cobriu como o paralelismo de dados mantém idêntica a cópia de cada dispositivo; esta lição conta exatamente quanto custa "cada dispositivo guarda uma cópia completa" e onde isso quebra.
**Fonte principal:** [Artigo científico: "ZeRO: Memory Optimizations Toward Training Trillion Parameter Models", Rajbhandari et al., 2019](https://arxiv.org/abs/1910.02054)
**Pré-requisitos:** [Lição 7](0007-data-parallelism-and-gradient-all-reduce.md)

## Aquecimento

1. ▢ No paralelismo de dados, qual operação mantém idêntica a cópia do modelo de cada dispositivo após cada passo do otimizador?

<details markdown="1"><summary>Verificação</summary>

O all-reduce: o gradiente local de cada dispositivo é calculado em média com os de todos os dispositivos antes de qualquer dispositivo aplicar uma atualização, de modo que todo dispositivo aplica o mesmo gradiente médio a uma cópia inicial idêntica dos pesos.

</details>

2. ▢ Adicionar mais dispositivos de dados paralelos reduz a quantidade de memória de que um único dispositivo precisa para guardar o modelo? Por que sim ou por que não?

<details markdown="1"><summary>Verificação</summary>

Não. Cada dispositivo ainda guarda uma cópia completa dos parâmetros, dos gradientes e do estado do otimizador, exatamente como se estivesse treinando sozinho; mais dispositivos significam mais cópias dessa mesma pegada, e não uma pegada menor por dispositivo.

</details>

## Saiba isto

### O que "uma cópia completa do modelo" realmente contém

A Lição 7 disse que todo dispositivo de dados paralelos guarda uma cópia completa dos parâmetros, dos gradientes e do estado do otimizador, sem contar quanto isso custa. O treinamento de precisão mista, a abordagem padrão para treinar modelos grandes, torna a conta concreta. Usando o Adam como otimizador, Rajbhandari et al. contam, por parâmetro (`Ψ` denota a contagem de parâmetros):

- uma cópia `fp16` dos parâmetros, usada no forward e no backward pass: 2 bytes por parâmetro
- uma cópia `fp16` dos gradientes: 2 bytes por parâmetro
- uma cópia `fp32` dos parâmetros, mantida pelo otimizador para atualizações numericamente estáveis: 4 bytes por parâmetro
- uma cópia `fp32` do momento do Adam: 4 bytes por parâmetro
- uma cópia `fp32` da variância do Adam: 4 bytes por parâmetro

Isso soma 16 bytes por parâmetro, e de cada um deles todo dispositivo de dados paralelos guarda uma cópia completa, independentemente de quantos outros dispositivos também guardam uma cópia idêntica.

### Onde isso bate em um muro

Para um modelo de 1,5 bilhão de parâmetros (o tamanho do GPT-2), 16 bytes por parâmetro dão 24 GB só para esses estados do modelo, bem acima dos 3 GB que seriam necessários para guardar apenas os parâmetros `fp16` sozinhos, e isso antes de contar as ativações (os valores intermediários mantidos do forward pass para calcular os gradientes no backward pass), que Rajbhandari et al. estimam separadamente em cerca de 60 GB para esse mesmo modelo com comprimento de sequência de 1.024 e batch size de 32. Rajbhandari et al. enunciam diretamente o limite resultante: "o paralelismo de dados básico não reduz a memória por dispositivo e fica sem memória para modelos com mais de 1,4B de parâmetros nas GPUs da geração atual com 32 GB de memória." Uma GPU de 32 GB fica sem espaço antes de ficar sem qualquer outra coisa, em um modelo pouco maior que o GPT-2, usando cada um dos muitos dispositivos que o paralelismo de dados pode adicionar.

### O formato da solução

Todo dispositivo no paralelismo de dados comum guarda uma cópia idêntica e totalmente redundante dos mesmos 16Ψ bytes de estados do modelo. Essa redundância é exatamente o que uma estratégia diferente pode remover: em vez de cada dispositivo guardar tudo, cada dispositivo poderia guardar apenas a sua própria fatia dos estados do modelo, reconstruindo ou comunicando o que não guarda, somente quando de fato for necessário para um cálculo. Essa é a ideia que a etapa 5 retoma diretamente, sob o nome ZeRO.

## Prática

1. ▢ Usando o detalhamento de 16 bytes por parâmetro, de quanta memória só os estados do modelo precisariam para um modelo de 7 bilhões de parâmetros treinado em precisão mista com Adam?

<details markdown="1"><summary>Dica</summary>

Multiplique a contagem de parâmetros por 16 bytes e depois converta bytes em gigabytes.

</details>

<details markdown="1"><summary>Verificação</summary>

Cerca de 112 GB (`7 × 10^9 × 16` bytes ≈ `1.12 × 10^11` bytes ≈ 112 GB). Isso é só estados do modelo, bem além de uma única GPU de 32 GB ou mesmo de 80 GB, antes de contar as ativações.

</details>

2. ▢ Qual destas explica melhor por que o paralelismo de dados sozinho não consegue encaixar um modelo arbitrariamente grande, não importa quantos dispositivos sejam adicionados?

    - a) A largura de banda de comunicação entre os dispositivos acaba saturando
    - b) Cada dispositivo guarda uma cópia completa e redundante do mesmo custo de memória por parâmetro, então adicionar dispositivos adiciona mais cópias em vez de reduzir a necessidade de qualquer dispositivo individual
    - c) A própria operação de all-reduce consome uma quantidade de memória proporcional ao tamanho do modelo
    - d) Modelos maiores sempre produzem gradientes maiores, que estouram a representação em fp16

<details markdown="1"><summary>Verificação</summary>

**b)** é o limite real que esta lição traça, diretamente a partir da pegada de memória redundante por dispositivo. (a) é uma preocupação real no treinamento distribuído, mas é um custo de tempo de comunicação, e não o muro de capacidade de memória de que esta lição trata. (c) e (d) não são o mecanismo que os autores do ZeRO identificam.

</details>

3. ▢ Rajbhandari et al. afirmam que o paralelismo de dados básico fica sem memória para modelos com mais de 1,4B de parâmetros em GPUs com 32 GB de memória. Segundo o detalhamento de 16 bytes por parâmetro, de quanta memória aproximadamente só os estados de um modelo de 1,4B de parâmetros precisariam, e como isso se compara à cifra de 32 GB quando as ativações são somadas?

<details markdown="1"><summary>Verificação</summary>

Cerca de 22,4 GB só para os estados do modelo (`1.4 × 10^9 × 16` bytes ≈ `2.24 × 10^10` bytes). Isso já deixa menos de 10 GB de uma GPU de 32 GB para as ativações, que o exemplo do GPT-2 da lição estimou em cerca de 60 GB com um comprimento de sequência e um batch size modestos, bem acima do que sobra.

</details>

## Prática no mundo real

- [ ] Escolha a contagem de parâmetros de um modelo aberto publicado e, usando a fórmula de 16 bytes por parâmetro, estime o seu requisito de memória de estados do modelo sob Adam de precisão mista. Compare essa estimativa com os tamanhos de memória de GPU comumente usados para treinamento (24, 40, 80 GB são cifras típicas para comparar).
- [ ] Leia o parágrafo do artigo do ZeRO (linkado acima) que descreve a memória residual (ativações, buffers temporários, fragmentação de memória) e escreva uma frase que a distinga da memória dos estados do modelo que esta lição contou.
- [ ] Amanhã: sem olhar adiante, escreva uma previsão de uma frase para a etapa 5: se o problema é que todo dispositivo guarda uma cópia completa e redundante dos mesmos 16Ψ bytes, o que uma solução que remove a redundância teria de fazer em vez disso e o que teria de comunicar para compensar o fato de não guardar mais tudo localmente?

## Para ir além

- [Artigo científico: "ZeRO: Memory Optimizations Toward Training Trillion Parameter Models", Rajbhandari et al., 2019](https://arxiv.org/abs/1910.02054)
- [Recursos](../RESOURCES.md)

---

A etapa 4 estabeleceu que a redundância do paralelismo de dados, e não o seu compute, é o que acaba primeiro. A etapa 5 retoma isso diretamente: o que o ZeRO e o FSDP de fato particionam para removê-la.

Não ficou claro? Releia a fonte principal no topo, já que esta lição a comprime e é na compressão que o entendimento escapa. Consulte o [glossário](../GLOSSARY.md) para qualquer termo que pareceu escorregadio.

Se o problema é a lição em si, e não o material, isso é um defeito: [abra uma issue](https://github.com/TokenCemetery/teach/issues).
