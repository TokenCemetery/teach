---
title: "23. Métricas que significam alguma coisa"
description: "A loss seleciona checkpoints; as métricas da tarefa tomam decisões"
type: lesson
---

# Lição 23. Métricas que significam alguma coisa

**Ligação com a missão:** "Provar que funcionou" está na missão. Um número que você não consegue defender não é prova.
**Fonte principal:** [Artigo científico: "Judging LLM-as-a-Judge with MT-Bench and Chatbot Arena", Zheng et al., arXiv:2306.05685](https://arxiv.org/abs/2306.05685)
**Pré-requisitos:** [Lição 22](0022-contamination-and-held-out-design.md), [Lição 12](0012-reading-a-training-run.md)

## Aquecimento

1. ▢ Por que três divisões, e não duas?

<details markdown="1"><summary>Verificação</summary>

Selecionar contra um conjunto é se ajustar a ele. A validação absorve a sua seleção; o teste fica intocado para poder dar uma estimativa não enviesada.

</details>

2. ▢ Aproximadamente quantos exemplos held-out para detectar uma diferença de 2 pontos?

<details markdown="1"><summary>Verificação</summary>

Milhares. A exigência cresce de forma quadrática à medida que a diferença diminui.

</details>

3. ▢ Nomeie duas coisas que a loss não enxerga.

<details markdown="1"><summary>Verificação</summary>

Se as gerações são utilizáveis e se as capacidades fora da distribuição da tarefa se degradaram.

</details>

## Saiba isto

### Por que a loss não é a métrica

A loss de entropia cruzada em dados held-out é genuinamente útil: é barata, é estável e é a coisa certa para acompanhar durante uma execução. Não é uma medida de se o modelo faz o seu trabalho.

A loss mede a surpresa de próximo token contra uma única continuação de referência específica. Portanto ela penaliza uma resposta correta formulada de outro jeito e recompensa uma errada e fluente. Dois modelos com a mesma loss held-out podem diferir substancialmente em utilidade, e a direção não é previsível.

**Use a loss para seleção de checkpoints. Use uma métrica da tarefa para decisões.**

### Escolhendo pelo formato da tarefa

| Formato da tarefa | Métrica | Atenção a |
|---|---|---|
| Classificação | Acurácia; precisão e recall por classe; F1 | O desbalanceamento de classes torna a acurácia sem sentido |
| Extração | Exact match no campo; F1 sobre spans | Normalize antes de comparar |
| Saída estruturada | Taxa de validade do schema, depois correção por campo | Duas falhas separadas, meça as duas |
| Código | Execução contra testes | Passar nos testes, e não se parecer com a referência |
| Geração de texto livre | Pontuação por rubrica, julgada por humano ou por modelo | O caso difícil; veja abaixo |
| Adjacente à recuperação | Groundedness, acurácia de citações | A fluência mascara afirmações sem sustentação |

Note o que está faltando: para qualquer coisa com uma resposta verificável, **verifique a resposta.** Execute o código. Valide o schema. Compare o campo extraído. Essas verificações são baratas, objetivas e muito melhores do que qualquer pontuação de similaridade.

### Sobre métricas de similaridade de superfície

BLEU, ROUGE e seus parentes medem a sobreposição de n-gramas com uma referência. Foram feitas para tradução automática e sumarização, e para tarefas de seguimento de instruções são fracas: uma resposta correta formulada de outro jeito pontua mal, e uma resposta errada que reaproveita o vocabulário da referência pontua bem.

Use-as apenas quando a sobreposição for de fato o que lhe importa, e nunca como única métrica. Se você se pegar otimizando ROUGE em uma tarefa que não é sumarização, pare.

### Saída estruturada: duas falhas, dois números

Para JSON ou qualquer schema, reporte sempre os dois:

1. **Validade.** Fez parse e satisfez o schema?
2. **Correção.** Dado que fez parse, os valores estão certos?

Colapsar os dois esconde qual problema você tem. Um modelo com 99% de validade e 60% de correção precisa de dados melhores. Um com 60% de validade e 95% de correção precisa de treinamento de formato, ou de decodificação restrita no momento do serving, o que pode fazer o problema desaparecer sem nenhum retreinamento.

### Modelo como juiz, usado com cuidado

Para saída de texto livre, fazer um modelo forte pontuar contra uma rubrica costuma ser a única opção escalável. Funciona, e tem vieses documentados que você precisa controlar:

- **Viés de posição.** Os juízes favorecem a resposta apresentada primeiro. Mitigue randomizando a ordem e, na comparação pareada, avaliando as duas ordens.
- **Viés de verbosidade.** Respostas mais longas pontuam mais, independentemente da qualidade. Observe se o seu fine-tune simplesmente ficou mais prolixo.
- **Autopreferência.** Os juízes tendem a favorecer textos parecidos com a sua própria saída.
- **Sensibilidade à rubrica.** Pequenas mudanças na redação da rubrica deslocam as pontuações de forma material.

O passo inegociável: **calibre o juiz contra rótulos humanos.** Pontue 50 a 100 exemplos você mesmo, execute o juiz nos mesmos e meça a concordância. Se a concordância é ruim, os números do juiz são decoração. Se é boa, você conquistou o direito de escalá-lo, e tem um número que quantifica o quanto confiar nele.

Uma configuração concreta e robusta: comparação pareada entre a saída do base e a do fine-tuned, nas duas ordens, com uma rubrica nomeando os critérios específicos que importam para você, reportada como taxa de vitórias. O julgamento pareado é mais confiável do que a pontuação absoluta, que deriva.

### Reporte a incerteza ou não reporte nada

Um único número sem dispersão não é um resultado. Padrão mínimo:

- **Intervalos de confiança** na métrica. Para uma proporção, use bootstrap ou um intervalo binomial.
- **Várias seeds** ao comparar configurações de treinamento, já que a variância de execução para execução costuma ser maior do que o efeito.
- **Comparação pareada** em exemplos idênticos (Lição 22).
- **O n** sobre o qual o número é calculado, declarado.

"71.2 versus 70.8" não é uma constatação. "71.2 ± 2.1 versus 70.8 ± 1.9 sobre n=340, três seeds" é uma constatação, e a constatação é que você não detectou uma diferença.

### Leia as saídas

Qualquer que seja a sua métrica, leia uma amostra de gerações reais todas as vezes, incluindo as falhas. As métricas comprimem, e o que elas comprimem e descartam costuma ser justamente o que você precisava saber: o modelo começou a recusar, ou a emitir um preâmbulo, ou a truncar, ou a responder uma pergunta sutilmente diferente. Nenhum agregado revela isso. Dez minutos de leitura revelam.

## Prática

1. ▢ Dois modelos têm loss held-out idêntica. Um pode ser substancialmente mais útil?

<details markdown="1"><summary>Verificação</summary>

Sim. A loss mede a concordância com uma única continuação de referência, então penaliza respostas corretas formuladas de outro jeito e recompensa as erradas e fluentes.

Loss igual é compatível com uma grande diferença de desempenho na tarefa, em qualquer direção. É por isso que a loss seleciona checkpoints e as métricas da tarefa tomam decisões.

</details>

2. ▢ O seu modelo emite JSON. Quais dois números você reporta, e por que não um?

<details markdown="1"><summary>Verificação</summary>

A taxa de validade do schema e a correção por campo entre as saídas válidas.

Um número combinado esconde qual problema você tem. Validade alta com correção baixa é um problema de dados; validade baixa com correção alta é um problema de formatação que a decodificação restrita pode resolver sem retreinar.

</details>

3. ▢ A pontuação do juiz do seu fine-tune subiu de 6.2 para 7.1. O comprimento médio das respostas subiu de 90 para 340 tokens. Preocupação?

<details markdown="1"><summary>Verificação</summary>

Sim: viés de verbosidade. Os juízes favorecem de forma confiável respostas mais longas independentemente da qualidade, então boa parte desse ganho pode ser comprimento.

Controle isso: compare em comprimentos igualados, instrua o juiz explicitamente a desconsiderar o comprimento, ou confira se os usuários de fato preferem a saída mais longa. A pontuação sozinha não distingue "melhor" de "mais longo".

</details>

4. ▢ Qual métrica avalia melhor um fine-tune de geração de código?

    - a) ROUGE contra a implementação de referência fornecida
    - b) Execução contra uma suíte de testes de cada problema
    - c) Loss de entropia cruzada held-out nos tokens de código
    - d) Um juiz modelo pontuando legibilidade e correção

<details markdown="1"><summary>Verificação</summary>

**b)** Execução contra uma suíte de testes de cada problema.

O código tem um critério objetivo de correção, então use-o. As métricas de sobreposição recompensam se parecer com a referência, e não funcionar; a loss tem o mesmo problema; um juiz é um desvio desnecessário quando você pode simplesmente executar o código.

</details>

5. ▢ Qual passo único conquista o direito de confiar em um juiz modelo em escala?

<details markdown="1"><summary>Verificação</summary>

Calibrá-lo contra rótulos humanos, pontuando 50 a 100 exemplos você mesmo e medindo a concordância com o juiz nos mesmos itens.

Sem isso, os números do juiz não estão validados. Com isso, você tem tanto a justificativa quanto um grau quantificado de confiança.

</details>

6. ▢ O fine-tune do seu classificador reporta 94% de acurácia. O que você precisa saber antes de acreditar que isso significa alguma coisa?

<details markdown="1"><summary>Verificação</summary>

A distribuição de classes. Se 94% dos exemplos pertencem a uma classe, um modelo que sempre chuta essa classe pontua 94% e não aprendeu nada.

Reporte precisão e recall por classe, ou uma métrica balanceada. A acurácia em dados desbalanceados é um dos números mais enganosos em uso comum.

</details>

## Prática no mundo real

- [ ] Escolha a sua métrica principal e escreva um parágrafo defendendo por que ela mede o que importa para você. Nomeie o que ela deixa passar.
- [ ] Calcule um intervalo de confiança na sua métrica atual. Decida se o seu conjunto held-out sustenta a comparação que você quer.
- [ ] Se usar um juiz modelo: rotule à mão 50 exemplos, execute o juiz nos mesmos e reporte a concordância.
- [ ] Amanhã: leia vinte gerações reais, incluindo toda falha. Anote uma coisa que a métrica não disse a você.

## Para ir além

- [Artigo científico: "Judging LLM-as-a-Judge with MT-Bench and Chatbot Arena", Zheng et al., arXiv:2306.05685](https://arxiv.org/abs/2306.05685)
- [Código: lm-evaluation-harness, EleutherAI](https://github.com/EleutherAI/lm-evaluation-harness)
- [Lição 24. O conjunto de regressão](0024-the-regression-suite.md)

---

Não ficou claro? Releia a fonte principal no topo, já que esta lição a comprime e é na compressão que o entendimento escapa. Consulte o [glossário](../GLOSSARY.md) para qualquer termo que pareceu escorregadio.

Se o problema é a lição em si, e não o material, isso é um defeito: [abra uma issue](https://github.com/TokenCemetery/teach/issues).
