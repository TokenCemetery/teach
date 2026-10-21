---
title: "9. ZeRO estágios 1 e 2: particionando o estado do otimizador e os gradientes"
description: "Remover de graça as cópias redundantes do paralelismo de dados, antes que o custo de comunicação precise crescer"
type: lesson
---

# Lição 9. ZeRO estágios 1 e 2: particionando o estado do otimizador e os gradientes

**Ligação com a missão:** "Explicar o que o ZeRO/FSDP particionam, por que o paralelismo de dados sozinho fica sem memória antes de ficar sem compute e quando o paralelismo de tensor ou de pipeline vale o seu custo de comunicação" é o quarto item em O sucesso se parece com isto. Esta lição cobre os dois primeiros dos três estágios do ZeRO; a Lição 10 cobre o terceiro.
**Fonte principal:** [Artigo científico: "ZeRO: Memory Optimizations Toward Training Trillion Parameter Models", Rajbhandari et al., 2019](https://arxiv.org/abs/1910.02054)
**Pré-requisitos:** [Lição 8](0008-why-data-parallelism-alone-runs-out-of-memory.md)

## Aquecimento

1. ▢ No Adam de precisão mista, quais são os cinco custos de memória por parâmetro que somam 16 bytes por parâmetro?

<details markdown="1"><summary>Verificação</summary>

Uma cópia fp16 dos parâmetros (2 bytes), uma cópia fp16 dos gradientes (2 bytes) e uma cópia fp32 de cada um dos parâmetros, do momento e da variância mantidos pelo otimizador (4 bytes cada), totalizando 16 bytes.

</details>

2. ▢ O paralelismo de dados comum reduz algum desses 16 bytes por dispositivo à medida que mais dispositivos são adicionados?

<details markdown="1"><summary>Verificação</summary>

Não. Cada dispositivo guarda 16 bytes por parâmetro completos e idênticos, independentemente de quantos outros dispositivos existam; adicionar dispositivos adiciona mais cópias redundantes, e não uma pegada menor por dispositivo.

</details>

## Saiba isto

### A redundância que o ZeRO remove

A Lição 8 estabeleceu que todo dispositivo de dados paralelos guarda uma cópia completa e idêntica do estado do otimizador, dos gradientes e dos parâmetros. A ideia central do ZeRO é que essa redundância é desnecessária: entre `Nd` dispositivos de dados paralelos, só precisa existir uma cópia completa desse estado no total, dividida em `Nd` pedaços, um pedaço por dispositivo, com cada dispositivo reconstruindo ou recebendo o pedaço que não guarda apenas no momento em que ele é de fato necessário. Rajbhandari et al. chamam isso de ZeRO-DP e o definem como três estágios que podem ser habilitados cumulativamente, cada um particionando mais uma parte dos estados do modelo do que o anterior.

### Estágio 1: particionando o estado do otimizador

**`P_os`** (particionamento do estado do otimizador) divide apenas o estado do otimizador, a maior fatia individual dos 16 bytes por parâmetro (a cópia fp32 dos parâmetros, o momento e a variância: 12 dos 16 bytes), entre os `Nd` dispositivos, de modo que cada dispositivo guarde apenas `1/Nd` dele em vez do todo. Rajbhandari et al. relatam que só isso dá uma redução de memória de 4x, com o **mesmo volume de comunicação do paralelismo de dados comum**: nenhum dado adicional precisa se mover entre os dispositivos além do que o all-reduce de gradientes já exigia, porque o estado do otimizador só é necessário localmente, no momento em que cada dispositivo aplica a sua própria fatia da atualização.

### Estágio 2: particionando também os gradientes

**`P_os+g`** adiciona o particionamento dos gradientes sobre o estágio 1: cada dispositivo só mantém a fatia do gradiente de que precisa para atualizar a sua própria fatia do estado do otimizador e dos parâmetros, em vez de guardar o gradiente completo de cada parâmetro do modelo. Essa é uma extensão natural da mesma ideia, já que um dispositivo que é dono de apenas `1/Nd` do estado do otimizador só precisa de `1/Nd` do gradiente para atualizá-lo. Rajbhandari et al. relatam que isso alcança uma redução de memória de 8x, de novo com o **mesmo volume de comunicação do paralelismo de dados comum**: as operações de reduce-scatter e all-gather em que isso reestrutura o all-reduce movem a mesma quantidade total de dados que um all-reduce padrão moveria, apenas endereçadas ao dispositivo que de fato precisa de cada fatia em vez de transmitir o todo para todos.

### Por que esses dois estágios são quase um almoço grátis

Os dois estágios removem redundância real de memória sem somar nenhum custo de comunicação além do que o paralelismo de dados já pagava. Isso é possível porque o estado do otimizador e os gradientes só são necessários ao dispositivo responsável por atualizar a fatia correspondente dos parâmetros; nada mais no forward ou no backward pass precisa lê-los. O estágio 3, que particiona os próprios parâmetros, não pode fazer a mesma afirmação, porque o forward e o backward pass de cada dispositivo precisam de todos os parâmetros, e não só dos que ele possui. A Lição 10 cobre o que isso custa.

## Prática

1. ▢ Um modelo de 7 bilhões de parâmetros é treinado com o estágio 1 do ZeRO (`P_os`) em 8 dispositivos de dados paralelos. Aproximadamente quantos bytes por parâmetro cada dispositivo guarda agora para o estado do otimizador, em comparação com os 12 bytes por parâmetro (parâmetros fp32, momento, variância) que guardaria sem particionamento?

<details markdown="1"><summary>Dica</summary>

O estágio 1 divide o estado do otimizador igualmente entre todos os `Nd` dispositivos.

</details>

<details markdown="1"><summary>Verificação</summary>

1.5 byte por parâmetro (`12 / 8`), abaixo dos 12 bytes completos que cada dispositivo guardaria de outra forma. Os parâmetros fp16 e os gradientes fp16 (4 bytes no total) não são afetados só pelo estágio 1.

</details>

2. ▢ Qual destas descreve melhor por que os estágios 1 e 2 do ZeRO não aumentam o volume de comunicação além do paralelismo de dados comum?

    - a) Eles pulam por completo a etapa de sincronização de gradientes
    - b) O estado do otimizador e os gradientes só são necessários localmente, pelo dispositivo responsável pela fatia correspondente, então reestruturar quem guarda o quê não exige mover mais dados no total
    - c) Eles só funcionam em modelos pequenos, em que o custo de comunicação não importa
    - d) Eles comprimem os gradientes antes de enviá-los, trocando acurácia por largura de banda

<details markdown="1"><summary>Verificação</summary>

**b)** é o mecanismo real: nenhum dispositivo precisa da fatia de estado do otimizador ou de gradientes de outro dispositivo durante o forward ou o backward pass, apenas no seu próprio passo de atualização. (a) é falsa; a sincronização continua acontecendo, apenas remodelada em reduce-scatter e all-gather. (c) e (d) descrevem mecanismos que esses dois estágios não usam.

</details>

3. ▢ Uma equipe quer a maior redução de memória que o ZeRO pode oferecer sem nenhum aumento no volume de comunicação em relação ao paralelismo de dados comum. Qual estágio deve usar e que redução de memória ele dá?

<details markdown="1"><summary>Verificação</summary>

O estágio 2 (`P_os+g`), dando uma redução de memória de 8x com o mesmo volume de comunicação do paralelismo de dados comum. O estágio 3 vai além em memória, mas é aquele para o qual Rajbhandari et al. relatam um aumento no volume de comunicação.

</details>

## Prática no mundo real

- [ ] Encontre a documentação da configuração de ZeRO ou FSDP de um framework de treinamento (as estratégias de particionamento do FSDP do PyTorch ou as configurações de estágio do ZeRO do DeepSpeed) e identifique qual opção de configuração corresponde ao estágio 1 e qual ao estágio 2.
- [ ] Usando o detalhamento de 16 bytes por parâmetro, calcule a memória por dispositivo para os estados do modelo de um modelo de 13 bilhões de parâmetros no estágio 2, em 8 dispositivos, e compare com o mesmo modelo sem nenhum particionamento do ZeRO.
- [ ] Amanhã: sem olhar adiante, escreva uma previsão de uma frase para a Lição 10: se o forward e o backward pass de cada dispositivo precisam de todos os parâmetros, e não só dos que ele possui, o que um dispositivo que particiona os próprios parâmetros teria de fazer de diferente do que os estágios 1 e 2 fazem?

## Para ir além

- [Artigo científico: "ZeRO: Memory Optimizations Toward Training Trillion Parameter Models", Rajbhandari et al., 2019](https://arxiv.org/abs/1910.02054)
- [Recursos](../RESOURCES.md)

---

Não ficou claro? Releia a fonte principal no topo, já que esta lição a comprime e é na compressão que o entendimento escapa. Consulte o [glossário](../GLOSSARY.md) para qualquer termo que pareceu escorregadio.

Se o problema é a lição em si, e não o material, isso é um defeito: [abra uma issue](https://github.com/TokenCemetery/teach/issues).
