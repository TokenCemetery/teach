---
title: "16. Loss spikes e as instabilidades do próprio otimizador"
description: "O mesmo spike pode vir de um batch ruim ou do próprio otimizador, e distingui-los exige uma comparação controlada"
type: lesson
---

# Lição 16. Loss spikes e as instabilidades do próprio otimizador

**Ligação com a missão:** "Dada uma curva de loss, consegue dizer se um spike é recuperável ou exige recomeçar de um checkpoint anterior" é o item de O sucesso se parece com isto que esta etapa atende. Esta lição cobre de onde um loss spike pode realmente vir e a mitigação padrão; a Lição 17 cobre o schedule que molda o treinamento em torno dele.
**Fonte principal:** [Artigo científico: "Scaling Language Models: Methods, Analysis & Insights from Training Gopher", Rae et al., 2021](https://arxiv.org/abs/2112.11446)
**Pré-requisitos:** [Lição 15](0015-mixed-precision-at-scale-bfloat16-and-stochastic-rounding.md), [Loss spike](../GLOSSARY.md)

## Aquecimento

1. ▢ Por que o intervalo de expoente mais largo do bf16 o torna mais tolerante durante o treinamento do que o fp16, mesmo que o bf16 tenha menos precisão?

<details markdown="1"><summary>Verificação</summary>

O bf16 mantém os 8 bits de expoente completos do fp32, dando-lhe o mesmo intervalo dinâmico do fp32, então valores grandes ou pequenos que aparecem em gradientes e ativações em escala têm menos chance de causar overflow ou underflow nele, mesmo que ele represente valores com menos precisão dentro desse intervalo do que o fp16.

</details>

2. ▢ Que limitação Rae et al. relataram mesmo depois de usar stochastic rounding nas atualizações de parâmetros em bf16?

<details markdown="1"><summary>Verificação</summary>

O stochastic rounding não recupera por inteiro o desempenho do treinamento de precisão mista comum; é uma mitigação, e não uma solução completa.

</details>

## Saiba isto

### Um loss spike não anuncia a própria causa

Um **loss spike**, um aumento súbito e acentuado da loss de treinamento no meio de uma execução, pode vir de mais de um lugar: um único batch incomumente difícil ou malformado, um problema de precisão numérica como os que a Lição 15 descreveu ou algo no próprio otimizador que se torna instável na escala em que se treina. Ler um spike na curva de loss diz que ele aconteceu; não diz por si só qual dessas coisas o causou, e a resposta certa, um reinício, uma mudança de hiperparâmetro ou nada, depende de saber qual foi.

### Um caso concreto: Adafactor contra Adam em escala

Rae et al. dão um exemplo trabalhado exatamente desse tipo de investigação. O Adafactor é um otimizador que usa menos memória que o Adam, o que importa diretamente para o orçamento de memória que a Lição 8 contou: uma pegada menor de estado do otimizador poderia significar encaixar um modelo maior, ou encaixar o mesmo modelo com menos particionamento. Em escalas menores, Rae et al. constataram que o pré-treinamento com Adafactor era estável e de bom desempenho. Com 7,1 bilhões de parâmetros, isso deixou de valer: eles observaram divergências de loss ao treinar com Adafactor que não tinham visto com 1,4 bilhão de parâmetros, mesmo que a execução com Adafactor tenha usado uma learning rate máxima menor (`6 × 10^-5`) do que o baseline estável com Adam com que foi comparada (`1.2 × 10^-4`). Uma learning rate menor é normalmente a primeira coisa a tentar contra a instabilidade; aqui não foi suficiente, e foi isso que permitiu a Rae et al. concluir que a instabilidade vinha do próprio otimizador nessa escala, e não simplesmente de a learning rate estar alta demais.

### A mitigação padrão: clipping pela norma global do gradiente

Seja qual for a causa subjacente de uma instabilidade, a mitigação mais direta que Rae et al. usam é o **gradient clipping** pela norma global: calcular a norma (a magnitude geral) do vetor de gradiente completo sobre todos os parâmetros do modelo e, se essa norma exceder um limite escolhido, reescalar o gradiente inteiro para baixo, proporcionalmente, de modo que a sua norma seja exatamente igual ao limite, antes que o passo do otimizador o use. Isso restringe o tamanho que a atualização de um único passo pode ter, não importa o que tenha produzido um gradiente incomumente grande. Rae et al. usam um valor de clipping de 1 para a maioria dos seus modelos, mas o reduzem para 0,25 especificamente para os dois maiores, o modelo de 7,1B e o próprio Gopher, para maior estabilidade, um exemplo direto e concreto de apertar essa salvaguarda à medida que a escala aumenta em vez de deixá-la fixa.

## Prática

1. ▢ Uma equipe observa um loss spike no meio de uma execução de treinamento. Nomeie duas causas subjacentes diferentes descritas nesta lição que poderiam produzir o mesmo spike visível.

<details markdown="1"><summary>Verificação</summary>

Quaisquer duas entre: um único batch incomumente difícil ou malformado, um problema de precisão numérica (como um overflow ou um problema de arredondamento no treinamento em bf16) ou uma instabilidade vinda do próprio otimizador que se torna instável na escala em que se treina.

</details>

2. ▢ Por que baixar a learning rate não estabilizou a execução de 7,1B com Adafactor e o que Rae et al. concluíram dessa falha?

<details markdown="1"><summary>Dica</summary>

A execução com Adafactor já usava uma learning rate menor que a do baseline estável com Adam com que foi comparada.

</details>

<details markdown="1"><summary>Verificação</summary>

A execução com Adafactor usou uma learning rate máxima de `6 × 10^-5`, menor que a `1.2 × 10^-4` do baseline estável com Adam, e ainda assim mostrou instabilidades. Como uma learning rate menor não resolveu, Rae et al. concluíram que a instabilidade vinha do próprio otimizador nessa escala, e não simplesmente de uma learning rate alta demais.

</details>

3. ▢ O que o clipping pela norma global do gradiente realmente faz com um gradiente cuja norma excede o limite de clipping?

    - a) Descarta esse gradiente por completo e pula o passo do otimizador daquele batch
    - b) Reescala o vetor de gradiente inteiro proporcionalmente para que a sua norma seja igual ao limite
    - c) Arredonda os valores do gradiente para um formato de menor precisão
    - d) Baixa permanentemente a learning rate pelo resto do treinamento

<details markdown="1"><summary>Verificação</summary>

**b)** é exatamente o mecanismo: reescalonamento proporcional para trazer a norma até o limite, e não um descarte, uma mudança de precisão ou uma mudança permanente de schedule. (a), (c) e (d) descrevem, cada uma, uma intervenção diferente e sem relação.

</details>

4. ▢ Rae et al. usam um valor de clipping de 1 para a maioria dos tamanhos de modelo, mas o reduzem para 0,25 especificamente para o modelo de 7,1B e o Gopher (280B). O que essa escolha concreta ilustra sobre como as salvaguardas de estabilidade são definidas?

<details markdown="1"><summary>Verificação</summary>

Que uma salvaguarda como o gradient clipping não é necessariamente uma constante fixa em todas as escalas; aqui ela foi apertada especificamente para os maiores modelos, onde o risco de instabilidade era maior, em vez de deixada no mesmo valor usado para execuções menores e mais estáveis.

</details>

## Prática no mundo real

- [ ] Encontre onde o gradient clipping é exposto como opção de configuração em um framework de treinamento a que você tenha acesso e anote o seu valor de clipping padrão, se algum estiver definido.
- [ ] Leia o parágrafo do artigo do Gopher (linkado acima) que descreve a comparação Adafactor contra Adam e escreva uma frase dizendo que evidência, especificamente, descartou "a learning rate era simplesmente alta demais" como explicação.
- [ ] Amanhã: sem olhar adiante, escreva uma previsão de uma frase para a Lição 17: dado que Rae et al. fazem o warm-up da learning rate lentamente no começo do treinamento em vez de começar imediatamente no valor máximo, que problema começar com a learning rate cheia em uma rede recém-inicializada e não treinada poderia causar?

## Para ir além

- [Artigo científico: "Scaling Language Models: Methods, Analysis & Insights from Training Gopher", Rae et al., 2021](https://arxiv.org/abs/2112.11446)
- [Recursos](../RESOURCES.md)

---

Não ficou claro? Releia a fonte principal no topo, já que esta lição a comprime e é na compressão que o entendimento escapa. Consulte o [glossário](../GLOSSARY.md) para qualquer termo que pareceu escorregadio.

Se o problema é a lição em si, e não o material, isso é um defeito: [abra uma issue](https://github.com/TokenCemetery/teach/issues).
