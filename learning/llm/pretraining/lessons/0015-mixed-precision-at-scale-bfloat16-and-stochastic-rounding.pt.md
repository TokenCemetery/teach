---
title: "15. Precisão mista em escala: bfloat16 e stochastic rounding"
description: "Um formato numérico com o intervalo do fp32 mas menos precisão, e o que custa atualizar parâmetros diretamente nele"
type: lesson
---

# Lição 15. Precisão mista em escala: bfloat16 e stochastic rounding

**Ligação com a missão:** "Dada uma curva de loss, consegue dizer se um spike é recuperável ou exige recomeçar de um checkpoint anterior" é a célula "Concluída quando" desta etapa em O arco, e começa pelo formato numérico em que a execução de treinamento sequer está rodando. A Lição 16 cobre diretamente os loss spikes; a Lição 17 cobre o schedule de learning rate.
**Fonte principal:** [Artigo científico: "Scaling Language Models: Methods, Analysis & Insights from Training Gopher", Rae et al., 2021](https://arxiv.org/abs/2112.11446)
**Pré-requisitos:** [Lição 14](0014-combining-all-three-when-tensor-and-pipeline-parallelism-earn-their-cost.md)

## Aquecimento

1. ▢ Segundo Narayanan et al., por que o paralelismo de tensor é melhor confinado a um único nó, enquanto o paralelismo de pipeline tolera ser espalhado por nós?

<details markdown="1"><summary>Verificação</summary>

O paralelismo de tensor precisa de um all-reduce caro para cada camada, o que exige a interconexão mais rápida disponível para continuar eficiente. O paralelismo de pipeline só passa ativações entre um punhado de fronteiras de estágio, usando uma comunicação ponto a ponto muito mais barata, que não engarrafa a computação inteira nem em links mais lentos e de maior distância.

</details>

## Saiba isto

### Duas formas de encaixar um número de 32 bits em 16 bits

Um número de ponto flutuante de 32 bits (`fp32`) divide os seus bits entre um intervalo (o expoente) e uma precisão (a mantissa, os dígitos depois do um inicial). Dois formatos diferentes de 16 bits comprimem isso de maneiras diferentes. O `fp16` mantém 10 bits de mantissa, mas apenas 5 bits de expoente, trocando muito do intervalo do `fp32` por precisão extra dentro de um intervalo mais estreito; um gradiente muito grande ou muito pequeno pode causar overflow ou underflow nele. O **`bfloat16`** (`bf16`) faz a troca oposta: mantém os 8 bits de expoente completos do `fp32`, então tem o mesmo intervalo dinâmico, mas só 7 bits de mantissa, então é mais grosseiro dentro desse intervalo. Esse intervalo mais largo é exatamente o motivo de o bf16 tender a ser mais tolerante durante o treinamento: os valores grandes ou minúsculos que aparecem em gradientes e ativações em escala têm menos chance de causar overflow ou underflow nele.

### O que o Gopher de fato fez com ele

Rae et al. descrevem o uso do bfloat16 especificamente para reduzir a memória e aumentar o throughput de treinamento, mas não o aplicaram de modo uniforme a todos os tamanhos de modelo que treinaram. Os modelos menores que 7,1 bilhões de parâmetros foram treinados com precisão mista comum: parâmetros `fp32`, ativações `bf16`. Os dois maiores modelos, o de 7,1B e o próprio Gopher (280B), foram além e usaram `bf16` tanto para os parâmetros quanto para as ativações, e não apenas para as ativações.

### Por que parâmetros em bf16 precisam de tratamento especial

Atualizar diretamente um parâmetro armazenado em bf16 esbarra em um problema que o treinamento de precisão mista comum evita mantendo uma cópia mestra em `fp32`: a precisão mais grosseira do bf16 significa que uma atualização pequena pode simplesmente sumir no arredondamento, se for menor que a distância entre valores bf16 representáveis adjacentes perto do valor atual do parâmetro. Rae et al. tratam isso com **stochastic rounding**: em vez de sempre arredondar um valor para o valor bf16 representável mais próximo (o que descartaria silenciosamente as atualizações pequenas de forma enviesada e em uma só direção), o stochastic rounding arredonda para cima ou para baixo com uma probabilidade proporcional a quão perto o valor verdadeiro está de cada vizinho, de modo que uma atualização pequena não se perde por completo; ela é preservada em média ao longo de muitos passos, mesmo que o arredondamento de qualquer passo isolado seja aleatório. Rae et al. são explícitos em dizer que isso não resolve o problema por completo: relatam que o stochastic rounding não recupera por inteiro o desempenho do treinamento de precisão mista comum, uma limitação honesta e não uma solução limpa.

## Prática

1. ▢ Um valor de gradiente durante o treinamento é incomumente grande, grande o bastante para preocupar quanto a overflow numérico. Qual formato de 16 bits, fp16 ou bf16, tem mais chance de representá-lo sem overflow, e por quê?

<details markdown="1"><summary>Verificação</summary>

bf16. Ele mantém os mesmos 8 bits de expoente do fp32, dando-lhe o mesmo intervalo dinâmico, então um valor grande que estouraria o intervalo mais estreito do expoente de 5 bits do fp16 tem menos chance de estourar o bf16.

</details>

2. ▢ Por que atualizar um parâmetro armazenado diretamente em bf16 (em vez de manter uma cópia mestra em fp32) corre o risco de perder silenciosamente atualizações pequenas?

<details markdown="1"><summary>Verificação</summary>

O bf16 tem só 7 bits de mantissa, então é grosseiro dentro do seu intervalo; uma atualização pequena pode ser menor que a distância entre valores bf16 representáveis adjacentes perto do valor atual do parâmetro, e arredondar para o valor representável mais próximo simplesmente a descartaria.

</details>

3. ▢ Como o stochastic rounding trata isso e que limitação Rae et al. relataram mesmo depois de usá-lo?

<details markdown="1"><summary>Verificação</summary>

O stochastic rounding arredonda para cima ou para baixo com uma probabilidade proporcional a quão perto o valor verdadeiro está de cada valor representável vizinho, em vez de sempre arredondar para o mais próximo, então uma atualização pequena é preservada em média ao longo de muitos passos, e não descartada toda vez. Mesmo assim, Rae et al. constataram que ele não recupera por inteiro o desempenho do treinamento de precisão mista comum.

</details>

4. ▢ Quais dos tamanhos de modelo do Gopher usaram bf16 tanto para os parâmetros quanto para as ativações, segundo Rae et al.?

    - a) Todos os tamanhos de modelo que treinaram
    - b) Apenas os modelos menores que 7,1 bilhões de parâmetros
    - c) Apenas o modelo de 7,1B e o modelo Gopher de 280B
    - d) Nenhum; o bf16 foi usado apenas para as ativações em todos os tamanhos

<details markdown="1"><summary>Verificação</summary>

**c)** Apenas os dois maiores modelos. Os modelos menores que 7,1B usaram precisão mista comum, parâmetros fp32 com ativações bf16, conforme a descrição de (b), e é por isso que (a) e (d) estão ambas erradas: as ativações bf16 foram usadas de forma ampla, mas os parâmetros bf16 foram reservados para os dois maiores modelos.

</details>

## Prática no mundo real

- [ ] Encontre onde um framework de treinamento a que você tenha acesso expõe uma escolha entre fp16 e bf16 (muitos listam os dois como opções para treinamento de precisão mista). Anote o que a documentação diz sobre quando preferir um ou outro e confira com o raciocínio de intervalo dinâmico desta lição.
- [ ] Procure o layout exato de bits (sinal, expoente, mantissa) do fp32, do fp16 e do bf16 e confirme por conta própria que o bf16 e o fp32 compartilham a mesma largura de expoente enquanto o fp16 não.
- [ ] Amanhã: sem olhar adiante, escreva uma previsão de uma frase para a Lição 16: dado que os dois maiores modelos do Gopher precisaram do tratamento numérico mais cuidadoso, você esperaria que loss spikes e instabilidades se tornassem mais ou menos comuns à medida que o tamanho do modelo cresce, e por quê?

## Para ir além

- [Artigo científico: "Scaling Language Models: Methods, Analysis & Insights from Training Gopher", Rae et al., 2021](https://arxiv.org/abs/2112.11446)
- [Recursos](../RESOURCES.md)

---

Não ficou claro? Releia a fonte principal no topo, já que esta lição a comprime e é na compressão que o entendimento escapa. Consulte o [glossário](../GLOSSARY.md) para qualquer termo que pareceu escorregadio.

Se o problema é a lição em si, e não o material, isso é um defeito: [abra uma issue](https://github.com/TokenCemetery/teach/issues).
