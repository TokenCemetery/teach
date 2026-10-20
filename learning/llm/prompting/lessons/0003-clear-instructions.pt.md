---
title: "3. Instruções claras"
description: "Escreva uma instrução que um novato capaz conseguiria seguir: contexto, a tarefa, as restrições e como é o resultado pronto"
type: lesson
---

# Lição 3. Instruções claras

**Ligação com a missão:** A maioria dos prompts que falham não enganou nem confundiu o modelo: eram pedidos subespecificados, então a melhoria mais barata em qualquer prompt é dizer o que um estranho capaz precisaria saber.
**Fonte principal:** [Docs: "Prompting best practices", Claude Platform Docs](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/claude-prompting-best-practices#be-clear-and-direct)
**Pré-requisitos:** [Lição 2](0002-system-prompts-and-roles.md), [Prompt zero-shot](../GLOSSARY.md)

## Aquecimento

1. ▢ Uma linha diz "Reply in at most three sentences." Ela pertence ao system prompt ou ao turno do usuário, e por quê?

<details markdown="1"><summary>Verificação</summary>

Ao system prompt, porque ela deve valer em toda requisição, e não apenas nesta.

</details>

2. ▢ O prompt renderizado de um chat termina com o marcador de papel do assistente. O que o modelo faz a partir dali?

<details markdown="1"><summary>Verificação</summary>

Ele continua a sequência de tokens a partir desse ponto, e é assim que escreve a resposta.

</details>

## Saiba isto

### O teste do colega

O guia da Anthropic pede que você pense no modelo como um funcionário brilhante, mas novo, que não tem contexto sobre as suas normas e fluxos de trabalho. A regra de ouro do guia: mostre o seu prompt a um colega com contexto mínimo sobre a tarefa e peça que ele o siga. Se ele ficaria confuso, o modelo também ficará.

O modelo não pode perguntar o que você quis dizer, então tudo o que você omite ele preenche com um palpite. O guia também diz que, se você quer um comportamento do tipo "além do esperado", deve pedi-lo explicitamente em vez de contar com o modelo para inferi-lo a partir de um prompt vago.

### Quatro partes de uma instrução clara

| Parte | Responde | Exemplo |
|---|---|---|
| Contexto | Para quem é isto, e por que importa? | "These summaries go to busy support managers who read on their phones." |
| Tarefa | O que exatamente deve ser feito? | "Summarise the ticket below." |
| Restrições | Quais limites se aplicam? | "At most 40 words. No customer names." |
| Como é o resultado pronto | Como você saberá que funcionou? | "A manager can decide whether to open the ticket from the summary alone." |

O guia da Anthropic diz que dar a motivação por trás de uma instrução, como o motivo pelo qual um comportamento importa, pode ajudar o modelo a entregar respostas mais direcionadas. A orientação de design de prompts do Google também lista restrições e formato de resposta como coisas a especificar. "Como é o resultado pronto" é a parte que mais costuma faltar, e também é a parte de que você precisará mais adiante, quando testar uma mudança de prompt contra um conjunto de regressão.

### Diga o que fazer e numere os passos que devem acontecer em ordem

O guia da Anthropic recomenda dizer ao modelo o que fazer em vez do que não fazer: em vez de "Do not use markdown", escreva "Your response should be composed of smoothly flowing prose paragraphs." Ele também sugere passos numerados em sequência quando a ordem ou a completude dos passos importa.

### Antes e depois

```text
Summarise this ticket.
```

```text
You are helping a support team triage tickets. The summaries are read by managers on their phones, who decide from the summary alone whether to open the ticket.
Summarise the ticket below in at most 40 words, in plain prose, leaving out customer names. State the problem first and the customer's requested outcome last.
```

O segundo prompt é mais longo porque carrega contexto, restrições e um propósito. O comprimento extra é informação, e não enfeite.

## Prática

1. ▢ Nomeie as quatro partes de uma instrução clara desta lição e, para o prompt "Write a product description.", diga quais estão faltando.

<details markdown="1"><summary>Verificação</summary>

Contexto, tarefa, restrições e como é o resultado pronto. O prompt tem apenas uma tarefa, e vaga. Faltam: para quem é a descrição e onde ela aparece, seus limites de tamanho e tom e o padrão que ela precisa atingir.

</details>

2. ▢ Reescreva "Don't write long answers." para que diga ao modelo o que fazer em vez disso.

<details markdown="1"><summary>Verificação</summary>

Por exemplo: "Answer in two or three sentences." Ela nomeia o comportamento desejado e dá um limite mensurável, o que também a torna verificável. Uma instrução negativa diz o que evitar, mas deixa o modelo adivinhar a alternativa.

</details>

3. ▢ Qual reescrita de "Make this email better" é a mais clara?

    - a) Improve this email so that it reads more professionally, clearly and persuasively overall
    - b) Rewrite this email for an upset customer in under 120 words, apologising first
    - c) Fix any problems in this email and make it sound good to the reader
    - d) Edit this email as an expert writer would, with attention to quality

<details markdown="1"><summary>Verificação</summary>

**b)** Ela nomeia o público, um limite de tamanho e um requisito de ordem, então outra pessoa poderia verificar o resultado. (a), (c) e (d) reformulam "melhor" em outras palavras sem dizer o que melhor significa.

</details>

4. ▢ Preveja, depois execute. Escolha uma tarefa que você faz com frequência, como "Write a short bio." Escreva o prompt em cinco palavras e envie. Preveja três coisas que a resposta vai errar para o seu propósito, depois reescreva o prompt com as quatro partes e envie de novo. Quais das suas três previsões foram corrigidas, e quais problemas apareceram que você não previu?

<details markdown="1"><summary>Dica</summary>

Entregue primeiro o prompt de cinco palavras a um colega de trabalho. Tudo o que ele perguntaria a você é o que o modelo está adivinhando.

</details>

<details markdown="1"><summary>Verificação</summary>

Resultados típicos: a primeira resposta adivinha o público, o tamanho e o tom. A segunda remove esses palpites, mas pode introduzir um problema novo, muitas vezes uma restrição que entra em conflito com outra. Guarde as duas respostas: a diferença entre elas é a primeira comparação que você pode mostrar a alguém, e a lição 18 transforma esse hábito em um conjunto de regressão.

</details>

## Prática no mundo real

- [ ] Pegue um prompt que você enviou esta semana e que teve uma resposta decepcionante e marque quais entre contexto, tarefa, restrições e como é o resultado pronto ele não tinha.
- [ ] Entregue um prompt que você escreveu a um colega sem nenhum conhecimento prévio e pergunte o que ele teria de adivinhar. Acrescente uma linha para cada palpite.
- [ ] Amanhã: troque um "don't" de um prompt que você usa por uma instrução positiva e compare as respostas sobre a mesma entrada.

## Para ir além

- [Docs: "Prompt design strategies", Gemini API, Google](https://ai.google.dev/gemini-api/docs/prompting-strategies): a orientação de um segundo fornecedor sobre restrições e formato de resposta.
- [Anatomia do Prompt](../reference/prompt-anatomy.md)
- [Recursos](../RESOURCES.md)

---

Não ficou claro? Releia a fonte principal no topo, já que esta lição a comprime e é na compressão que o entendimento escapa. Consulte o [glossário](../GLOSSARY.md) para qualquer termo que pareceu escorregadio.

Se o problema é a lição em si, e não o material, isso é um defeito: [abra uma issue](https://github.com/TokenCemetery/teach/issues).
