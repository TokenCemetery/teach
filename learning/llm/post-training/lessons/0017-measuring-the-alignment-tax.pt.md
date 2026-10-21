---
title: "17. Medindo o alignment tax"
description: "O imposto não aparece em todo lugar ao mesmo tempo, e um eixo chegou a medir uma melhora em vez disso"
type: lesson
---

# Lição 17. Medindo o alignment tax

**Ligação com a missão:** "Saber separar um ganho genuíno de capacidade de um artefato de reward hacking ou de viés do juiz" é o item de O sucesso se parece com isto a que esta etapa serve. Esta lição cobre como o alignment tax é de fato medido, e não só o que ele é; a lição 18 cobre a detecção de reward hacking depois que o treinamento termina e passa o bastão para `llm/evals` para a metodologia completa.
**Fonte principal:** [Artigo científico: "Training language models to follow instructions with human feedback", Ouyang et al., 2022](https://arxiv.org/abs/2203.02155)
**Pré-requisitos:** [Lição 16](0016-rlaif-how-well-ai-feedback-actually-matches-human-feedback.md), [Alignment tax](../GLOSSARY.md)

## Aquecimento

1. ▢ O que é o direct-RLAIF (d-RLAIF), e como o seu desempenho se comparou ao do RLAIF canônico, segundo Lee et al.?

<details markdown="1"><summary>Verificação</summary>

Uma técnica que pula o treinamento de um reward model separado, consultando diretamente um modelo de linguagem pronto para uso para obter uma pontuação de recompensa durante o RL. Lee et al. constataram que ela alcançou desempenho melhor do que o RLAIF canônico, e não meramente desempenho comparável a um custo menor.

</details>

2. ▢ Em qual das três tarefas que Lee et al. testaram o RLAIF superou o RLHF, e não apenas o igualou?

<details markdown="1"><summary>Verificação</summary>

Geração de diálogo inofensivo.

</details>

## Saiba isto

### O imposto não é um número; é um conjunto de medições separadas

A lição 1 apresentou o alignment tax como um custo real e medido, sem detalhar como ele é de fato medido. Ouyang et al. o fizeram executando o seu modelo alinhado contra uma bateria de benchmarks públicos de PLN existentes e comparando o resultado com o base model não alinhado, em cada benchmark separadamente, em vez de condensar tudo em uma única cifra de imposto. Eles relatam regressões específicas em certos benchmarks, notadamente SQuAD, DROP, HellaSwag e a tradução de francês para inglês do WMT 2015 e, o que é importante, **nenhuma mudança significativa** em outros dois que também checaram, Winogender e CrowSPairs (benchmarks relacionados a viés). O imposto apareceu em alguns eixos e em outros não; tratá-lo como um custo uniforme teria escondido esse padrão.

### O alinhamento também produziu um ganho medido, e não só um custo

A mesma bateria de avaliação incluía um eixo em que o treinamento de alinhamento se mediu como uma melhora, e não como um custo: usando o dataset RealToxicityPrompts, Ouyang et al. relatam que o InstructGPT gerou cerca de 25% menos saídas tóxicas do que o GPT-3 quando solicitado a ser respeitoso. Um balanço justo do que o treinamento de alinhamento fez com as capacidades medidas de um modelo precisa incluir esse tipo de resultado ao lado das regressões; relatar só o imposto e ignorar onde o mesmo treinamento ajudou seria tão enganoso quanto relatar imposto nenhum.

### A correção, e o que ela não custou

A lição 6 já nomeou o mecanismo: misturar as atualizações do PPO com atualizações que aumentam a verossimilhança da distribuição original de pré-treinamento (PPO-ptx) reduziu muito as regressões medidas em SQuAD, DROP, HellaSwag e WMT. Ouyang et al. são específicos ao dizer que essa recuperação ocorreu **sem comprometer as pontuações de preferência dos rotuladores**, ou seja, a correção não simplesmente trocou os ganhos de alinhamento de volta pelo desempenho perdido nos benchmarks; ambos foram medidos, separadamente, e a correção melhorou um sem custar visivelmente o outro.

### Uma checagem de generalização diferente e mais difícil de fraudar: rotuladores held-out

Além das regressões em benchmarks, Ouyang et al. fazem uma checagem voltada a uma pergunta diferente: o comportamento alinhado do modelo se generaliza além das pessoas específicas cujas preferências o moldaram, ou ele apenas aprendeu a agradar os rotuladores particulares dos seus dados de treinamento? Eles testam isso com **rotuladores held-out**, pessoas que não contribuíram com nenhum dado usado para treinar o modelo, e constatam que esses rotuladores held-out ainda preferiram as saídas do InstructGPT. É a mesma ideia de fundo para a qual `llm/pretraining` e `llm/evals` usam dados held-out: um resultado só significa o que diz significar se não puder ter sido produzido simplesmente por um ajuste aos dados (ou às pessoas) específicos que moldaram o treinamento.

## Prática

1. ▢ Ouyang et al. relatam regressões em SQuAD, DROP, HellaSwag e na tradução do WMT, mas nenhuma mudança significativa em Winogender e CrowSPairs. O que tratar o alignment tax como um único número geral teria escondido sobre esse resultado?

<details markdown="1"><summary>Verificação</summary>

Que o imposto não se aplicou uniformemente; apareceu com clareza em alguns benchmarks e de forma alguma em outros. Um único número condensado apresentaria esse padrão desigual como se fosse um custo consistente em todas as capacidades.

</details>

2. ▢ Por que a redução de 25% nas saídas tóxicas importa para um relato justo do alignment tax, em vez de relatar apenas as regressões em SQuAD/DROP/HellaSwag/WMT?

<details markdown="1"><summary>Verificação</summary>

Porque o treinamento de alinhamento ajudou de forma mensurável nesse eixo em vez de custar alguma coisa; relatar apenas as regressões e omitir esse resultado subestimaria o que o treinamento de fato fez, do mesmo modo que relatar imposto nenhum o superestimaria.

</details>

3. ▢ O que, especificamente, Ouyang et al. verificaram sobre a correção do PPO-ptx para o alignment tax, além de simplesmente reduzir as regressões nos benchmarks?

<details markdown="1"><summary>Verificação</summary>

Que ela fez isso sem comprometer as pontuações de preferência dos rotuladores; a recuperação do desempenho nos benchmarks não foi paga devolvendo os ganhos de alinhamento sobre os quais o PPO-ptx foi acrescentado.

</details>

4. ▢ Por que testar com rotuladores held-out, pessoas que não contribuíram com dados de treinamento, responde a uma pergunta diferente da que as medições de regressão em benchmarks respondem?

<details markdown="1"><summary>Verificação</summary>

As regressões em benchmarks medem se capacidades específicas pioraram. Os rotuladores held-out testam se o comportamento alinhado do modelo de fato se generaliza para preferências além das pessoas específicas que moldaram o treinamento, em vez de apenas se ajustar de perto a esse grupo em particular; um resultado que valesse só para os rotuladores originais não sustentaria a mesma alegação de generalização.

</details>

## Prática no mundo real

- [ ] Encontre um relatório técnico de pós-treinamento publicado e verifique se ele relata tanto regressões quanto melhoras em uma bateria de benchmarks, ou apenas uma direção. Anote quais benchmarks, se houver, não mostraram mudança significativa.
- [ ] Leia o parágrafo do artigo do InstructGPT (linkado acima) que descreve o experimento com rotuladores held-out e escreva uma frase dizendo que resultado teria feito você duvidar de que o alinhamento do modelo se generalizou além dos rotuladores do seu treinamento.
- [ ] Amanhã: sem olhar adiante, escreva uma previsão de uma frase para a lição 18: dado que um reward model ou um juiz de IA pode ser burlado (lição 5), o que avaliar um modelo alinhado *finalizado*, depois que o treinamento acabou, precisaria checar que uma comparação entre PM de treino e PM de teste durante o treinamento não conseguiria?

## Para ir além

- [Artigo científico: "Training language models to follow instructions with human feedback", Ouyang et al., 2022](https://arxiv.org/abs/2203.02155)
- [Recursos](../RESOURCES.md)

---

Não ficou claro? Releia a fonte principal no topo, já que esta lição a comprime e é na compressão que o entendimento escapa. Consulte o [glossário](../GLOSSARY.md) para qualquer termo que pareceu escorregadio.

Se o problema é a lição em si, e não o material, isso é um defeito: [abra uma issue](https://github.com/TokenCemetery/teach/issues).
