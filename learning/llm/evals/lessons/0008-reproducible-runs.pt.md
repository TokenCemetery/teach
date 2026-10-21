---
title: "8. Execuções reproduzíveis"
description: "Por que o mesmo eval pode produzir números diferentes em execuções diferentes, e o que um resultado confiável precisa registrar junto com a pontuação"
type: lesson
---

# Lição 8. Execuções reproduzíveis

**Ligação com a missão:** Este é o ponto culminante da etapa 4: um harness (lição 7) é só metade do trabalho. O número que ele produz só é confiável depois que sua variância de uma execução para outra é compreendida e o que o produziu está registrado, que é o que faz uma comparação posterior significar alguma coisa.
**Fonte principal:** [Repositório: lm-evaluation-harness, EleutherAI](https://github.com/EleutherAI/lm-evaluation-harness)
**Pré-requisitos:** [Lição 7](0007-eval-frameworks-and-harness.md), [Contaminação de dados](../GLOSSARY.md)

## Aquecimento

1. ▢ Nomeie as quatro etapas que todo harness de eval tem.

<details markdown="1"><summary>Verificação</summary>

Carregar o conjunto de eval held-out, gerar as saídas do modelo, avaliá-las com a métrica ou o juiz escolhido e agregar as pontuações por exemplo em um número-resumo.

</details>

2. ▢ Quando uma equipe deve recorrer ao openai/evals em vez do lm-evaluation-harness?

<details markdown="1"><summary>Verificação</summary>

Ao avaliar uma capacidade específica da missão que nenhum benchmark padronizado existente cobre, já que o openai/evals foi feito para definir um eval customizado como código, enquanto o lm-evaluation-harness foi feito para executar configurações de benchmarks já existentes.

</details>

## Saiba isto

### Por que o mesmo eval pode dar dois números diferentes

Um modelo amostrado com temperatura diferente de zero produz completions diferentes em execuções diferentes, mesmo contra o prompt idêntico, o que significa pontuações por exemplo diferentes e um número agregado diferente a cada execução do eval, sem que nada de errado tenha acontecido. Se a avaliação também usa um juiz LLM (etapa 3), isso acrescenta uma segunda camada de ruído de amostragem sobre a variância do próprio modelo sob teste. Nada disso é um bug do harness; é o harness reportando fielmente um processo estocástico, e significa que o número de uma única execução é uma amostra de uma distribuição, e não um fato fixo sobre o modelo.

### O trade-off do determinismo

Definir a temperatura como 0 (decodificação greedy) remove a aleatoriedade do lado da geração e torna as execuções muito mais repetíveis, o que é atraente para um eval cuja avaliação depende de reprodutibilidade exata, como o exact match. O custo: a decodificação greedy pode não refletir como o modelo de fato se comporta em produção, se o sistema implantado amostra com temperatura diferente de zero. Um eval executado inteiramente em greedy pode estar medindo um modo que o sistema real raramente usa. Onde o comportamento implantado de fato amostra, a abordagem mais honesta é executar várias amostras por exemplo na temperatura de produção (a mesma ideia que o pass@k da lição 4 usou para código) e reportar a dispersão entre elas, e não apenas o valor pontual de uma única execução.

### Uma seed ajuda, mas não garante resultados idênticos

Fixar uma seed aleatória para a geração reduz a variância entre execuções na mesma configuração, mas não é garantia de resultados idênticos bit a bit entre hardwares diferentes, versões de biblioteca diferentes ou composições de batch diferentes, já que a computação em ponto flutuante não é perfeitamente associativa em todos esses casos. Uma seed é um controle real e útil, mas não absoluto; tratar "fixamos uma seed" como prova de que duas execuções são diretamente comparáveis é exagerar o que uma seed pode prometer.

### O que torna um número reportado defensável depois

Um número sozinho, sem nada sobre como foi produzido, não pode ser comparado com honestidade a um número posterior, de uma nova execução, de um checkpoint diferente ou de um ciclo de eval diferente: qualquer diferença entre eles pode ser uma mudança real ou apenas variância do pipeline, e nada em uma pontuação nua consegue dizer qual. Um resultado defensável registra, junto com a pontuação, o que de fato a produziu: a seed aleatória usada, a temperatura de geração, as versões do modelo e do framework, a versão do conjunto de eval e, quando várias amostras foram executadas, a dispersão entre elas, e não apenas sua média. É disso que uma comparação posterior, ou a decisão de go/no-go que a etapa 5 constrói, de fato precisa para ser honesta sobre se uma diferença observada reflete o modelo ou o ruído.

## Prática

1. ▢ Uma equipe executa o mesmo eval contra o mesmo modelo duas vezes, na temperatura 0.7, e obtém duas pontuações agregadas diferentes. Isso é evidência de que o harness está quebrado? Por que sim ou por que não?

<details markdown="1"><summary>Verificação</summary>

Não. Uma temperatura diferente de zero torna a geração estocástica, então completions diferentes, e portanto pontuações por exemplo diferentes, são esperadas entre execuções, mesmo sem nada de errado. O harness está reportando fielmente um processo estocástico; o número de uma única execução é uma amostra, e não um fato fixo.

</details>

2. ▢ O que definir a temperatura como 0 para um eval traz, e o que custa, se o sistema implantado de fato amostra na temperatura 0.7?

<details markdown="1"><summary>Verificação</summary>

Traz repetibilidade: a decodificação greedy remove a aleatoriedade do lado da geração, então as execuções ficam muito mais consistentes. Custa realismo: o eval está medindo um modo de decodificação (greedy) que o sistema real raramente usa, então o resultado pode não refletir como o modelo de fato se comporta quando implantado a 0.7.

</details>

3. ▢ Por que fixar uma seed aleatória não garante que duas execuções de eval produzirão resultados idênticos?

<details markdown="1"><summary>Dica</summary>

Pense no que mais poderia diferir entre duas execuções além da seed.

</details>

<details markdown="1"><summary>Verificação</summary>

Uma seed controla a aleatoriedade dentro de uma dada configuração, mas a computação em ponto flutuante não é perfeitamente associativa entre hardwares, versões de biblioteca ou composições de batch diferentes, então essas diferenças ainda podem produzir resultados diferentes mesmo com a mesma seed. Uma seed é um controle real, não uma garantia absoluta de saída idêntica bit a bit.

</details>

4. ▢ A equipe A reporta uma pontuação de eval de 72,3 para um modelo. Um mês depois, a equipe B reexecuta "o mesmo eval" no mesmo modelo e obtém 69,8, sem nenhuma informação de seed, temperatura ou versão registrada da execução original da equipe A. O que se pode concluir com honestidade da diferença de 2,5 pontos?

<details markdown="1"><summary>Verificação</summary>

Muito pouco, por si só. Sem saber a temperatura, a seed, as versões do modelo e do framework e a versão do conjunto de eval que a equipe A usou, não há como dizer se a diferença reflete uma mudança real (um checkpoint diferente, uma versão diferente do conjunto de eval) ou a variância comum de amostragem entre execuções. A conclusão honesta é que a comparação ainda não é significativa até que os detalhes de produção das duas execuções sejam conhecidos e igualados, ou até que a variância entre execuções repetidas seja medida diretamente.

</details>

5. ▢ Qual afirmação é verdadeira sobre o que torna defensável um número de eval reportado?

    - a) A pontuação de uma única execução basta por si só, desde que o harness tenha rodado sem erros
    - b) A pontuação deve ser reportada junto com o que a produziu (seed, temperatura, versões, versão do conjunto de eval) e, quando relevante, sua dispersão entre várias execuções
    - c) Definir uma seed aleatória garante resultados idênticos em qualquer hardware ou versão de biblioteca
    - d) A decodificação greedy deve sempre ser usada em evals, independentemente da temperatura de amostragem real do sistema implantado

<details markdown="1"><summary>Verificação</summary>

**b)** Registrar os detalhes de produção e, onde há amostragem, a dispersão entre execuções é o que permite a uma comparação posterior distinguir uma mudança real de ruído. (a) é falsa: um número isolado não pode ser comparado a nada depois sem saber o que o produziu. (c) é falsa: uma seed reduz, mas não elimina, a variância entre hardwares ou versões diferentes. (d) é falsa: a decodificação greedy abre mão de realismo quando o sistema implantado de fato amostra, o que é um custo real, e não uma escolha gratuita.

</details>

## Prática no mundo real

- [ ] Para um eval que você executa, verifique se o harness dele hoje registra a seed, a temperatura e as versões do modelo/framework junto com a pontuação, e adicione o que estiver faltando.
- [ ] Se o seu eval amostra com temperatura diferente de zero, execute-o várias vezes (ou várias amostras por exemplo) e registre a dispersão entre as execuções, e não apenas um número.
- [ ] Amanhã: encontre um resultado de eval passado que você ou sua equipe reportou e verifique se foi registrado o bastante junto com ele para saber se uma futura nova execução seria diretamente comparável.

## Para ir além

- [Repositório: lm-evaluation-harness, EleutherAI](https://github.com/EleutherAI/lm-evaluation-harness)
- [Repositório: openai/evals, OpenAI](https://github.com/openai/evals)
- [Recursos](../RESOURCES.md)

---

Não ficou claro? Releia a fonte principal no topo, já que esta lição a comprime e é na compressão que o entendimento escapa. Consulte o [glossário](../GLOSSARY.md) para qualquer termo que pareceu escorregadio.

Se o problema é a lição em si, e não o material, isso é um defeito: [abra uma issue](https://github.com/TokenCemetery/teach/issues).
