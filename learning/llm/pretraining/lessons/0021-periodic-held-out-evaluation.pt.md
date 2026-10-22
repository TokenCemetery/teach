---
title: "21. Avaliação held-out periódica"
description: "A loss de treinamento diz que o modelo está se ajustando aos próprios dados de treinamento; só uma verificação held-out diz algo sobre o resto"
type: lesson
---

# Lição 21. Avaliação held-out periódica

**Ligação com a missão:** "Consegue ler um dashboard de treinamento e dizer se a execução está no caminho certo" é a célula "Concluída quando" desta etapa em O arco. A Lição 20 cobriu o acompanhamento dos sinais internos da própria execução de treinamento; esta lição cobre a verificação de checkpoints salvos contra algo que a loss de treinamento não consegue dizer e entrega essa medição para onde ela é ensinada por inteiro.
**Fonte principal:** [Artigo científico: "Scaling Language Models: Methods, Analysis & Insights from Training Gopher", Rae et al., 2021](https://arxiv.org/abs/2112.11446)
**Pré-requisitos:** [Lição 20](0020-reading-a-loss-curve.md), [Dados held-out](../../evals/GLOSSARY.md)

## Aquecimento

1. ▢ Por que um loss scalar caindo em direção a zero, ou uma norma de ativações disparando, poderia avisar mais cedo da instabilidade do que a própria curva de loss de treinamento?

<details markdown="1"><summary>Verificação</summary>

Esses são sintomas do problema numérico subjacente se desenvolvendo, que podem aparecer antes de ele crescer o bastante para perturbar visivelmente a curva de loss; quando um spike fica claramente visível na própria loss, o problema pode já estar se formando há algum tempo.

</details>

2. ▢ Por que um dashboard que acompanha a loss, a norma do gradiente e um sinal de estabilidade só é útil na prática se for monitorado com frequência?

<details markdown="1"><summary>Verificação</summary>

Porque falhas e instabilidades são eventos frequentes e rotineiros em escala (etapa 8), então um problema pego tarde custa muito mais progresso perdido do que o mesmo problema pego cedo.

</details>

## Saiba isto

### O que a loss de treinamento não consegue dizer

A loss de treinamento mede quão bem um modelo se ajusta aos batches específicos em que está sendo treinado no momento. Uma loss de treinamento que diminui suavemente é necessária para uma execução saudável, mas não é o mesmo que o modelo ser bom em qualquer coisa que uma pessoa de fora do loop de treinamento realmente vá pedir a ele, e não diz absolutamente nada sobre se essa melhora se sustentaria em texto em que o modelo nunca foi treinado. Uma curva de loss de treinamento de aparência perfeitamente saudável ainda pode estar por cima de um modelo que está discretamente sofrendo overfitting em peculiaridades específicas da sua própria mistura de treinamento.

### Como foi a própria avaliação periódica do Gopher

Rae et al. não esperaram o treinamento terminar para verificar isso. Eles relatam curvas de avaliação calculadas periodicamente durante o treinamento, em quatro benchmarks de modelagem de linguagem (Wikitext103, LAMBADA, Curation Corpus e C4) que filtraram explicitamente para fora do conjunto de treinamento de antemão, justamente para que uma boa pontuação neles não pudesse ser explicada pelo fato de o modelo simplesmente ter visto aquele texto exato durante o treinamento. Verificar um benchmark assim periodicamente, e não só uma vez no final, é o que realmente permite a uma equipe pegar um problema, um bug no pipeline de dados, uma regressão por uma mudança de configuração, uma divergência inesperada de capacidade, enquanto a execução ainda está em andamento e ainda dá para fazer algo a respeito, em vez de descobri-lo só depois de o orçamento de compute completo já ter sido gasto.

### Por que "filtrado do conjunto de treinamento" faz um trabalho real

A expressão que Rae et al. usam, benchmarks "explicitamente filtrados do conjunto de treinamento", é a mesma ideia em torno da qual a Lição 1 do material de pipeline de dados desta trilha foi construída, aplicada à avaliação em vez do treinamento: uma pontuação só significa algo sobre generalização se o modelo não pudesse tê-la acertado por ter memorizado o texto exato que está sendo testado. É precisamente isso que **dados held-out** significa, e é um tópico grande o bastante, com os seus próprios caminhos de contaminação, métodos de detecção e técnicas de design, para ter uma trilha inteira construída em torno dele.

### Onde isto passa o bastão

O `llm/evals` é dono da metodologia de avaliação por inteiro: como construir um conjunto held-out que resista à contaminação, o que torna uma métrica confiável e como transformar um número em uma decisão defensável. A única reivindicação desta trilha sobre esse material é a feita nesta lição: uma execução de pré-treinamento precisa de verificações periódicas contra dados held-out, em checkpoints salvos, e não apenas no final. Para tudo além disso, a folha [Dados Held-Out e Contaminação](../../evals/reference/held-out-data-and-contamination.md) de `llm/evals` é a que se deve ler a seguir, e não uma reexplicação dela aqui.

## Prática

1. ▢ A loss de treinamento de um modelo vem diminuindo suavemente durante toda a execução. Isso, por si só, diz se o modelo se sai bem em tarefas que ele não foi treinado diretamente para ajustar?

<details markdown="1"><summary>Verificação</summary>

Não. A loss de treinamento mede o ajuste aos próprios batches de treinamento do modelo; uma loss de treinamento que diminui suavemente é necessária para uma execução saudável, mas não diz por si só nada sobre o desempenho em dados ou tarefas em que o modelo não foi treinado, que é para o que serve uma avaliação held-out.

</details>

2. ▢ Por que Rae et al. filtraram explicitamente Wikitext103, LAMBADA, Curation Corpus e C4 para fora do conjunto de treinamento do Gopher antes de usá-los como benchmarks de avaliação periódica?

<details markdown="1"><summary>Verificação</summary>

Para que uma boa pontuação nesses benchmarks não pudesse ser explicada pelo fato de o modelo simplesmente ter visto e memorizado aquele texto exato durante o treinamento. Um benchmark em que o modelo foi treinado não consegue distinguir capacidade genuína de memorização, e é isso que faz de um benchmark held-out uma evidência significativa de um jeito que um contaminado não é.

</details>

3. ▢ O que avaliar periodicamente durante o treinamento, e não apenas uma vez no final, realmente traz a uma equipe, dado o quanto uma execução de treinamento completa é cara?

    - a) Não tem vantagem sobre uma única avaliação no final; o resultado final é o que importa
    - b) Permite que um bug, uma regressão ou uma divergência de capacidade seja pego e potencialmente tratado enquanto a execução ainda está em andamento, em vez de descoberto só depois de o orçamento de compute completo já ter sido gasto
    - c) Substitui por completo a necessidade de dados held-out
    - d) Só importa para execuções de treinamento muito curtas

<details markdown="1"><summary>Verificação</summary>

**b)** é o ganho prático direto: pegar um problema cedo, enquanto ainda há orçamento de compute para responder a ele, em vez de descobrir só depois de a execução estar completa. (a) ignora isso por completo. (c) inverte a relação; a avaliação periódica ainda precisa ser held-out para significar algo. (d) é o contrário, já que uma execução mais longa e mais cara tem mais a perder com um problema pego tarde.

</details>

## Prática no mundo real

- [ ] Encontre como um framework de treinamento ou uma configuração de acompanhamento de experimentos a que você tenha acesso agenda a avaliação periódica durante o treinamento (um intervalo de avaliação medido em passos ou tokens é comum) e anote quais benchmarks ou métricas ele avalia por padrão.
- [ ] Leia a folha de referência [Dados Held-Out e Contaminação](../../evals/reference/held-out-data-and-contamination.md) de `llm/evals` e identifique qual dos seus dois caminhos de contaminação (absorção no pré-treinamento ou overfitting iterativo) é aquele contra o qual a expressão "explicitamente filtrados do conjunto de treinamento" do Gopher protege.
- [ ] Amanhã: para uma execução de pré-treinamento hipotética à sua escolha, decida um intervalo de avaliação (com que frequência, em tokens ou passos, você conferiria o desempenho held-out) e nomeie um benchmark ou conjunto held-out contra o qual o conferiria, e por quê.

## Para ir além

- [Artigo científico: "Scaling Language Models: Methods, Analysis & Insights from Training Gopher", Rae et al., 2021](https://arxiv.org/abs/2112.11446)
- `llm/evals`: [Dados Held-Out e Contaminação](../../evals/reference/held-out-data-and-contamination.md)
- [Recursos](../RESOURCES.md)

---

A etapa 9 cobriu acompanhar uma execução enquanto ela acontece, tanto as suas entranhas quanto os seus checkpoints contra algo externo. A etapa 10 fecha o arco: decidir se vale a pena rodar uma dessas e defender essa decisão diante de outra pessoa.

Não ficou claro? Releia a fonte principal no topo, já que esta lição a comprime e é na compressão que o entendimento escapa. Consulte o [glossário](../GLOSSARY.md) para qualquer termo que pareceu escorregadio.

Se o problema é a lição em si, e não o material, isso é um defeito: [abra uma issue](https://github.com/TokenCemetery/teach/issues).
