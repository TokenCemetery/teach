---
title: "18. Reward hacking depois do fato"
description: "Um reward model held-out consegue pegar a deriva durante o treinamento; um modelo finalizado precisa de outro tipo de checagem"
type: lesson
---

# Lição 18. Reward hacking depois do fato

**Ligação com a missão:** "Saber separar um ganho genuíno de capacidade de um artefato de reward hacking ou de viés do juiz" é o item de O sucesso se parece com isto a que esta etapa serve, e esta lição o encerra, passando a metodologia completa para `llm/evals` em vez de reafirmá-la.
**Fonte principal:** [LLM-as-Judge](../../evals/reference/llm-as-judge.md) (a folha de referência de `llm/evals` sobre design de prompt, calibração e viés)
**Pré-requisitos:** [Lição 17](0017-measuring-the-alignment-tax.md), [Recusa excessiva](../../evals/GLOSSARY.md)

## Aquecimento

1. ▢ Por que Ouyang et al. testaram o InstructGPT contra rotuladores held-out, pessoas que não contribuíram com nenhum dado de treinamento?

<details markdown="1"><summary>Verificação</summary>

Para checar se o comportamento alinhado do modelo se generaliza além das pessoas específicas cujas preferências moldaram o treinamento, em vez de apenas se ajustar de perto a esse grupo em particular.

</details>

2. ▢ O que a redução de 25% nas saídas tóxicas acrescentou a um relato justo do alignment tax, além das regressões em SQuAD/DROP/HellaSwag/WMT?

<details markdown="1"><summary>Verificação</summary>

Evidência de que o treinamento de alinhamento ajudou de forma mensurável em pelo menos um eixo, e não só custou alguma coisa; um relato justo precisa das duas direções, e não apenas das regressões.

</details>

## Saiba isto

### Uma pergunta diferente da checagem em tempo de treinamento

A divergência entre PM de treino e PM de teste da lição 5 é uma checagem feita *durante* o treinamento, comparando uma policy com um reward model contra o qual ela nunca foi otimizada. Avaliar um modelo alinhado *finalizado* faz uma pergunta relacionada, mas distinta: dados apenas o modelo e as suas pontuações de avaliação, sem um segundo reward model para comparar, como saber se uma pontuação alta reflete melhora genuína e não um artefato de como a própria avaliação foi construída?

### Um sintoma concreto: a recusa excessiva

O `llm/evals` nomeia uma falha específica e bem documentada de que essa pergunta trata de fato: a **recusa excessiva**, um modelo que se recusa a atender um prompt que na verdade é seguro, tipicamente porque ele se parece superficialmente com um inseguro. Um modelo que recusa de forma agressiva pode pontuar de forma enganosamente boa em um benchmark de segurança construído em sua maior parte com prompts inseguros, já que recusar quase tudo parece idêntico a um modelo genuinamente cuidadoso nesse teste específico, enquanto falha silenciosamente no conjunto muito maior de prompts seguros que deveria ter respondido. Essa é a falha de evasão generalizada da lição 5 e da lição 15, vista do lado da avaliação e não do lado do treinamento: um eval no estilo red-team que só checa prompts inseguros não consegue detectá-la, porque a recusa excessiva é uma falha nos prompts seguros que o eval nunca perguntou.

### O viés do juiz é o mesmo problema, um nível acima

Quando uma avaliação usa um modelo, em vez de um benchmark fixo, para julgar saídas (uma configuração cada vez mais comum da qual as próprias lições de RLAIF e de Constitutional AI desta trilha já dependem), esse juiz pode ser enganado de maneiras específicas: preferindo respostas mais longas independentemente da qualidade, ou sendo influenciado por qual resposta por acaso é mostrada primeiro. A referência de `llm/evals` sobre o design de LLM-as-judge cobre esses modos de falha, e as checagens de calibração que os pegam, por completo. Uma pontuação alta atribuída por um juiz só é tão confiável quanto a calibração do próprio juiz contra esses vieses conhecidos; um juiz não calibrado pode ser burlado por uma policy de um jeito que parece, visto de fora, exatamente como melhora genuína.

### Por que isto passa o bastão em vez de reafirmar

Projetar um prompt de juiz, checar a calibração de um juiz e medir a concordância de um juiz com avaliadores humanos são o assunto próprio de `llm/evals`, coberto lá com a profundidade que esta trilha não precisa repetir. O que esta trilha possui é mais restrito e específico do pós-treinamento: saber que a avaliação de um pipeline de pós-treinamento está exposta exatamente a esse risco, reconhecer um sintoma concreto como a recusa excessiva quando ele aparece e tratar uma pontuação suspeitamente alta de segurança ou de preferência com o mesmo ceticismo que a comparação entre PM de treino e PM de teste da lição 5 já modelou durante o treinamento.

## Prática

1. ▢ Um benchmark de segurança composto inteiramente por prompts inseguros relata que um modelo recusa 98% deles, uma pontuação aparentemente excelente. O que esse benchmark, por si só, deixa de dizer sobre o modelo?

<details markdown="1"><summary>Verificação</summary>

Se o modelo também recusa prompts que na verdade são seguros. Um benchmark construído apenas com prompts inseguros não consegue detectar a recusa excessiva, já que um modelo que recusa quase tudo parece idêntico a um genuinamente cuidadoso nesse teste específico.

</details>

2. ▢ Por que um modelo recusar um prompt realmente seguro é uma falha genuinamente diferente de um jailbreak bem-sucedido?

<details markdown="1"><summary>Verificação</summary>

Um jailbreak é o modelo deixar de recusar algo que deveria ter recusado; a recusa excessiva é o modelo recusar algo que não deveria ter recusado. São falhas em direções opostas, e um eval construído para pegar uma (um benchmark red-team, só de prompts inseguros) não consegue detectar a outra.

</details>

3. ▢ Uma avaliação usa um modelo de linguagem como juiz para pontuar qual de duas saídas de modelos alinhados é melhor. O que esta lição diz que você deve checar antes de confiar em uma grande diferença entre as pontuações de dois modelos?

<details markdown="1"><summary>Verificação</summary>

Se o próprio juiz está calibrado contra vieses conhecidos (como favorecer respostas mais longas ou a resposta que aparece primeiro), segundo o material de LLM-as-judge de `llm/evals`; um juiz não calibrado pode ser burlado de um jeito que produz uma diferença de pontuação que parece melhora genuína, mas não é.

</details>

## Prática no mundo real

- [ ] Leia a folha de referência [LLM-as-Judge](../../evals/reference/llm-as-judge.md) de `llm/evals` e identifique uma checagem de calibração que ela recomenda e que você aplicaria a uma avaliação de pós-treinamento antes de confiar nos seus resultados.
- [ ] Encontre uma avaliação de segurança publicada para um modelo alinhado e verifique se ela relata uma taxa de recusa excessiva em prompts seguros, além de uma taxa de recusa em prompts inseguros. Anote qual das duas, se alguma, está faltando.
- [ ] Amanhã: para uma avaliação a que você tenha acesso ou possa imaginar (um benchmark de segurança, uma configuração de juiz de preferência), cite um sintoma concreto, como a recusa excessiva ou um viés conhecido de juiz, que você checaria antes de confiar em uma pontuação de destaque dela.

## Para ir além

- [LLM-as-Judge](../../evals/reference/llm-as-judge.md): a folha de referência de `llm/evals` sobre design de prompt, calibração e viés
- [Recursos](../RESOURCES.md)

---

A etapa 9 cobriu a separação entre um ganho genuíno de alinhamento e um artefato, durante o treinamento e depois do fato. A etapa 10 encerra o arco: escolher entre tudo o que esta trilha cobriu, para um orçamento declarado, e defender essa escolha.

Não ficou claro? Releia a fonte principal no topo, já que esta lição a comprime e é na compressão que o entendimento escapa. Consulte o [glossário](../GLOSSARY.md) para qualquer termo que pareceu escorregadio.

Se o problema é a lição em si, e não o material, isso é um defeito: [abra uma issue](https://github.com/TokenCemetery/teach/issues).
