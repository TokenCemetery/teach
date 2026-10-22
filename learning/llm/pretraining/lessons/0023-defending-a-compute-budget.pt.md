---
title: "23. Defendendo um orçamento de compute"
description: "Um plano de pré-treinamento é uma aposta feita de muitas decisões separadas, e defendê-lo significa defender cada uma nos seus próprios termos"
type: lesson
---

# Lição 23. Defendendo um orçamento de compute

**Ligação com a missão:** "Decidir se uma tarefa declarada pede pré-treinamento, pré-treinamento continuado ou fine-tuning de um modelo base existente e defender a escolha pelo custo" é o item de O sucesso se parece com isto que a etapa 10 fecha. A Lição 22 cobriu quando o pré-treinamento é a decisão errada; esta lição cobre a defesa do plano quando ele de fato é a decisão certa.
**Fonte principal:** [Artigo científico: "Training Compute-Optimal Large Language Models", Hoffmann et al., 2022](https://arxiv.org/abs/2203.15556)
**Pré-requisitos:** [Lição 22](0022-pretraining-is-usually-the-wrong-default.md)

## Aquecimento

1. ▢ Segundo Gururangan et al., o pré-treinamento adaptativo ao domínio ajuda mais, menos ou aproximadamente o mesmo, conforme o domínio-alvo já estivesse próximo dos dados de treinamento originais do modelo base?

<details markdown="1"><summary>Verificação</summary>

Ajuda mais justamente quando o domínio-alvo não estava já bem representado no pré-treinamento original do modelo base; alvos já próximos do domínio original se beneficiam menos, já que o modelo base os cobre razoavelmente bem.

</details>

2. ▢ Nomeie uma razão legítima para pré-treinar do zero em vez de adaptar um modelo existente, segundo a Lição 22.

<details markdown="1"><summary>Verificação</summary>

Qualquer uma entre: o idioma ou domínio-alvo está tão distante dos dados de treinamento e do tokenizer de todos os modelos base disponíveis que a adaptação não consegue fechar a distância, um requisito de licenciamento ou de proveniência descarta todos os modelos base disponíveis ou uma mudança deliberada de arquitetura para a qual um checkpoint existente não pode ser adaptado.

</details>

## Saiba isto

### Um plano de pré-treinamento não é um número só

Quando o pré-treinamento é de fato a decisão certa, defendê-lo diante de quem controla o orçamento significa defender mais do que uma única cifra de custo total. Cada etapa anterior desta trilha produziu uma peça desse plano, e cada peça é uma afirmação que pode ser conferida, e contestada, nos seus próprios termos:

- **A razão tokens por parâmetro (etapa 3).** A contagem de parâmetros e de tokens planejada fica perto da faixa de aproximadamente 20 a 25 tokens por parâmetro de Hoffmann et al. para o orçamento de compute escolhido, ou se inclina para a alocação de Kaplan et al., pesada em parâmetros e comparativamente leve em dados? Um plano que se afasta da faixa compute-optimal precisa de uma razão declarada, e não de silêncio.
- **O pipeline de dados (etapas 1 e 2).** A contagem de tokens é alcançável a partir de um corpus que de fato foi obtido, deduplicado e filtrado por qualidade, ou ela supõe dados que ainda não existem na escala e na qualidade necessárias?
- **O plano de paralelismo (etapas 4 a 6).** A contagem de dispositivos do plano, a estratégia de particionamento e qualquer divisão de paralelismo de tensor ou de pipeline correspondem à interconexão real do hardware, segundo o raciocínio da própria Lição 14, ou supõem padrões de comunicação que o hardware não consegue sustentar com eficiência?
- **O plano de estabilidade e monitoramento (etapas 7 a 9).** O plano diz qual precisão, qual clipping e qual schedule serão usados e inclui checkpointing frequente o bastante, e monitoramento minucioso o bastante, para as taxas de falha que a própria evidência da etapa 8 mostrou serem normais nessa escala, e não excepcionais?

### Por que agrupar isso tudo em um número convida a pergunta errada

Um orçamento apresentado apenas como um custo total convida exatamente uma pergunta em troca: dá para torná-lo mais barato. Um orçamento apresentado como as afirmações específicas acima convida um conjunto de perguntas mais útil: essa razão tokens por parâmetro é de fato compute-optimal para o objetivo declarado, os dados existem para sustentá-la, o plano de paralelismo corresponde ao hardware e a execução está protegida contra a taxa de falha que uma execução dessa duração deve esperar. Defender cada afirmação separadamente é também o que torna possível dizer, com honestidade, onde o plano é incerto (uma fonte de dados não comprovada, uma suposição de interconexão não verificada) em vez de apresentar confiança uniforme em um plano que não a tem.

### O que "defensável" não significa

Defender um orçamento de compute não significa garantir que a execução de treinamento terá sucesso na primeira tentativa, nem que um comitê de revisão precise aprová-lo. Significa que todo número importante do plano remonta a uma razão declarada, fundamentada no material que esta trilha cobriu, de modo que uma contestação a qualquer um deles ("por que essa razão", "por que essa divisão de paralelismo", "por que esse intervalo de checkpoint") tenha uma resposta diferente de "é o que sempre fazemos".

## Prática

1. ▢ Um plano de pré-treinamento proposto treina um modelo de 30 bilhões de parâmetros com 200 bilhões de tokens. Usando a faixa de aproximadamente 20 a 25 tokens por parâmetro da etapa 3, a razão desse plano está dentro ou fora dessa faixa e que pergunta de acompanhamento isso levanta?

<details markdown="1"><summary>Dica</summary>

Divida a contagem de tokens pela contagem de parâmetros e compare com a faixa.

</details>

<details markdown="1"><summary>Verificação</summary>

Cerca de 6.7 tokens por parâmetro (`200 / 30`), bem abaixo da faixa de aproximadamente 20 a 25. Isso levanta a pergunta de acompanhamento sobre por que o plano treina com comparativamente poucos dados em relação ao seu tamanho, o mesmo padrão subtreinado que a Lição 6 diagnosticou no GPT-3, e se esse afastamento da faixa compute-optimal é deliberado e justificado ou simplesmente não examinado.

</details>

2. ▢ Uma equipe apresenta um orçamento de pré-treinamento como uma única cifra total em dólares, sem nenhum detalhamento adicional. Segundo esta lição, qual é o principal problema de apresentá-lo assim?

    - a) Um único número é sempre impreciso
    - b) Ele convida apenas "dá para torná-lo mais barato" em troca, em vez de revelar quais afirmações específicas (razão, dados, paralelismo, plano de estabilidade) são de fato sólidas ou frágeis
    - c) Os revisores não conseguem entender cifras em dólares
    - d) É ilegal apresentar um orçamento assim

<details markdown="1"><summary>Verificação</summary>

**b)** é o problema real que esta lição levanta: agrupar todas as decisões em um número esconde quais partes do plano são bem sustentadas e quais são suposições e convida uma conversa muito menos útil do que defender cada afirmação convidaria. (a), (c) e (d) não são o raciocínio que esta lição dá.

</details>

3. ▢ Nomeie as quatro categorias de afirmação em que esta lição diz que um plano de pré-treinamento defensável deve ser dividido.

<details markdown="1"><summary>Verificação</summary>

A razão tokens por parâmetro, o pipeline de dados (obtenção, deduplicação, filtragem de qualidade), o plano de paralelismo casado com a interconexão do hardware e o plano de estabilidade e monitoramento (precisão, clipping, schedule, frequência de checkpointing).

</details>

## Prática no mundo real

- [ ] Encontre um relatório técnico publicado de um modelo pré-treinado aberto e veja quantas das quatro categorias de afirmação desta lição ele de fato declara explicitamente (razão, pipeline de dados, plano de paralelismo, plano de estabilidade e monitoramento). Anote as que ele deixa sem declarar.
- [ ] Para um orçamento de compute à sua escolha, escreva as quatro categorias como um plano curto em tópicos, com uma frase de justificativa para cada, do jeito que esta lição defende que um orçamento defensável deve ser apresentado.
- [ ] Amanhã: escolha um dos seus quatro tópicos da prática anterior e anote que evidência, desta trilha ou de outro lugar, você apontaria se alguém contestasse aquela afirmação específica.

## Para ir além

- [Artigo científico: "Training Compute-Optimal Large Language Models", Hoffmann et al., 2022](https://arxiv.org/abs/2203.15556)
- [Recursos](../RESOURCES.md)

---

Não ficou claro? Releia a fonte principal no topo, já que esta lição a comprime e é na compressão que o entendimento escapa. Consulte o [glossário](../GLOSSARY.md) para qualquer termo que pareceu escorregadio.

Se o problema é a lição em si, e não o material, isso é um defeito: [abra uma issue](https://github.com/TokenCemetery/teach/issues).
