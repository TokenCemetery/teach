---
title: "9. Significância estatística contra ruído"
description: "Por que uma diferença de pontuação precisa ser medida contra o ruído que poderia produzi-la por acaso, e por que a comparação pareada vence tratar duas pontuações como independentes"
type: lesson
---

# Lição 9. Significância estatística contra ruído

**Ligação com a missão:** A decisão de go/no-go da etapa 5 só é tão boa quanto saber se uma diferença de pontuação observada é real; esta lição dá as ferramentas que respondem a isso, construindo diretamente sobre o ponto da lição 8 de que o número de uma única execução carrega seu próprio ruído.
**Fonte principal:** [Docs: "Define success criteria and build evaluations", Claude Platform Docs](https://platform.claude.com/docs/en/test-and-evaluate/develop-tests)
**Pré-requisitos:** [Lição 8](0008-reproducible-runs.md), [Contaminação de dados](../GLOSSARY.md)

## Aquecimento

1. ▢ Por que o mesmo eval, executado duas vezes com temperatura diferente de zero, pode produzir duas pontuações agregadas diferentes sem que nada esteja errado?

<details markdown="1"><summary>Verificação</summary>

Amostrar com temperatura diferente de zero torna a geração estocástica, então completions diferentes, e portanto pontuações por exemplo diferentes, são esperadas entre execuções. O número de uma única execução é uma amostra de uma distribuição, e não um fato fixo sobre o modelo.

</details>

2. ▢ O que deve ser registrado junto com uma pontuação de eval reportada para tornar significativa uma comparação posterior?

<details markdown="1"><summary>Verificação</summary>

A seed aleatória, a temperatura de geração, as versões do modelo e do framework, a versão do conjunto de eval e, quando várias amostras foram executadas, a dispersão entre elas, e não apenas sua média.

</details>

## Saiba isto

### Uma diferença de pontuação não é automaticamente uma diferença real

Uma nova variante de modelo pontua 76% contra 70% de uma baseline no mesmo conjunto de eval. Essa diferença de seis pontos parece uma melhoria, mas a lição 8 já estabeleceu que a pontuação de uma única execução carrega seu próprio ruído de amostragem. A pergunta que esta lição responde: uma diferença de seis pontos é maior que o ruído que poderia produzi-la só por acaso, ou é exatamente o tipo de variação que duas execuções do mesmo modelo poderiam mostrar entre si?

### O tamanho da amostra define quanto ruído esperar

Para uma pontuação do tipo passa/falha sobre *N* exemplos, com uma taxa real de aprovação *p*, o erro padrão da proporção medida é aproximadamente `sqrt(p(1−p)/N)`. Uma taxa de aprovação de 0,70 sobre 100 exemplos tem um erro padrão de cerca de `sqrt(0.70 × 0.30 / 100) ≈ 0.046`, ou aproximadamente 4,6 pontos percentuais; uma taxa de aprovação de 0,76 sobre os mesmos 100 exemplos tem um erro padrão de cerca de 4,3 pontos. Uma diferença de seis pontos entre duas estimativas, cada uma com cerca de quatro a cinco pontos de ruído, não é obviamente maior do que o acaso sozinho poderia produzir; mais exemplos encolheriam cada erro padrão (ele cai com `sqrt(N)`), apertando a estimativa e facilitando distinguir uma diferença real do ruído.

### A comparação pareada é a ferramenta mais afiada

Tratar as duas pontuações como proporções independentes, como a estimativa acima fez, joga fora informação que na verdade está disponível: quando os mesmos exemplos de eval passam tanto pela baseline quanto pela nova variante, você sabe não só quantos cada uma acertou, mas quais exemplos específicos cada uma acertou ou errou. Uma **comparação pareada** olha para os exemplos em que os dois modelos discordam (um acertou e o outro não), em vez de olhar para as duas taxas de aprovação brutas separadamente. Isso anula a dificuldade em nível de exemplo, que afeta os dois modelos por igual, uma pergunta que todo modelo tende a acertar ou que todo modelo tende a errar não contribui em nada para saber se um modelo é de fato melhor que o outro, e torna uma diferença real mais fácil de detectar com a mesma quantidade de dados do que comparar duas proporções independentes.

![Uma grade dois por dois cruzando se a baseline acertou ou errou um exemplo com se a variante acertou ou errou. Os dois acertaram e os dois erraram são as células de concordância, mostradas em cinza: elas se anulam. Baseline acertou e variante errou, e baseline errou e variante acertou, são as células de discordância, mostradas na cor de destaque: uma comparação pareada conta apenas essas.](images/paired-comparison-grid.svg)

### O que "ainda não significativo" quer dizer para uma decisão de go/no-go

Uma diferença que não é claramente maior que o ruído não é evidência de ausência de diferença; é evidência de que ainda não há informação suficiente para dizer. A resposta honesta é executar mais exemplos (encolhendo o erro padrão) ou executar um teste de significância pareado adequado sobre as discordâncias, e não tratar uma pontuação numericamente maior como prova de melhoria por si só.

## Prática

1. ▢ Um modelo baseline passa em 70 de 100 exemplos de eval; uma nova variante passa em 76 de 100. Calcule o erro padrão aproximado de cada proporção e diga se a diferença de seis pontos parece claramente maior que o ruído combinado.

<details markdown="1"><summary>Dica</summary>

Use `sqrt(p(1−p)/N)` para cada proporção separadamente, com N = 100.

</details>

<details markdown="1"><summary>Verificação</summary>

Baseline: `sqrt(0.70 × 0.30 / 100) ≈ 0.046`, cerca de 4,6 pontos. Nova variante: `sqrt(0.76 × 0.24 / 100) ≈ 0.043`, cerca de 4,3 pontos. Cada estimativa individualmente carrega cerca de quatro a cinco pontos de ruído, então uma diferença de seis pontos não é claramente maior do que esse ruído combinado poderia produzir por acaso; é sugestiva, não conclusiva, só com 100 exemplos.

</details>

2. ▢ Por que usar um conjunto de eval maior (mais exemplos) torna uma diferença real de pontuação mais fácil de distinguir do ruído?

<details markdown="1"><summary>Verificação</summary>

O erro padrão de uma proporção cai com `sqrt(N)`, então um N maior encolhe o ruído de cada estimativa. Uma diferença que parecia ambígua contra o ruído de 100 exemplos pode se tornar claramente maior que o ruído quando medida contra, digamos, 1.000 exemplos, sem que a verdadeira diferença de fundo tenha mudado.

</details>

3. ▢ Os mesmos 100 exemplos de eval passam por uma baseline e por uma nova variante. Por que olhar quais exemplos específicos cada modelo acertou ou errou (uma comparação pareada) é mais poderoso do que apenas comparar as duas taxas de aprovação brutas, 70% e 76%, como números independentes?

<details markdown="1"><summary>Verificação</summary>

Comparar taxas de aprovação brutas trata cada pontuação como se viesse de uma amostra sem relação, descartando o fato de que os mesmos exemplos foram usados nos dois casos. Uma comparação pareada olha, em vez disso, onde os dois modelos discordam, anulando a dificuldade em nível de exemplo que afeta os dois por igual (uma pergunta que todo modelo acerta ou que todo modelo erra não diz nada sobre qual modelo é melhor), o que torna uma diferença real detectável com menos dados do que uma comparação de proporções independentes exige.

</details>

4. ▢ Uma equipe observa uma diferença de pontuação entre duas variantes de modelo que acaba não sendo claramente maior que o ruído estimado. Qual é a conclusão honesta, e quais são duas formas de obter uma resposta mais clara?

<details markdown="1"><summary>Verificação</summary>

A conclusão honesta é que ainda não há informação suficiente para dizer se a diferença é real, e não que não há diferença. Duas formas de esclarecer: executar o eval em mais exemplos, o que encolhe o erro padrão de cada estimativa, ou executar um teste de significância pareado adequado sobre os exemplos específicos em que as duas variantes discordam, em vez de comparar as duas taxas de aprovação brutas como números independentes.

</details>

5. ▢ Qual afirmação é verdadeira sobre julgar se uma diferença de pontuação de eval é real?

    - a) Qualquer diferença positiva entre duas pontuações conta como evidência de melhoria, independentemente do tamanho da amostra
    - b) Uma diferença deve ser julgada contra o ruído que o tamanho da amostra poderia produzir por acaso, e uma comparação pareada usa os dados de forma mais eficiente do que tratar as pontuações como independentes
    - c) A significância estatística só importa para métricas específicas da tarefa, não para pontuações de LLM-as-judge
    - d) Um conjunto de eval maior nunca pode mudar se uma dada diferença parece significativa

<details markdown="1"><summary>Verificação</summary>

**b)** Tanto o raciocínio de ruído contra tamanho de amostra quanto a vantagem da comparação pareada são exatamente o que esta lição cobre. (a) é falsa: uma diferença menor que o ruído estimado não é evidência sólida, seja qual for o seu sinal. (c) é falsa: o mesmo raciocínio estatístico se aplica a qualquer pontuação agregada, não importa como foi avaliada. (d) é falsa: o erro padrão encolhe com `sqrt(N)`, então um conjunto de eval maior pode transformar uma diferença ambígua em uma clara.

</details>

## Prática no mundo real

- [ ] Para uma diferença de pontuação que você observou entre duas variantes de modelo, estime o erro padrão de cada proporção usando a fórmula desta lição e verifique se a diferença é claramente maior que o ruído combinado.
- [ ] Se você tiver resultados por exemplo das duas variantes no mesmo conjunto de eval, olhe os exemplos em que elas discordam e conte-os, como primeiro passo para uma comparação pareada.
- [ ] Amanhã: decida, para um eval que importa para você, se o tamanho atual da amostra é grande o bastante para detectar o tamanho de melhoria que de fato importaria para uma decisão de go/no-go.

## Para ir além

- [Docs: "Define success criteria and build evaluations", Claude Platform Docs](https://platform.claude.com/docs/en/test-and-evaluate/develop-tests)
- [Recursos](../RESOURCES.md)

---

Não ficou claro? Releia a fonte principal no topo, já que esta lição a comprime e é na compressão que o entendimento escapa. Consulte o [glossário](../GLOSSARY.md) para qualquer termo que pareceu escorregadio.

Se o problema é a lição em si, e não o material, isso é um defeito: [abra uma issue](https://github.com/TokenCemetery/teach/issues).
