---
title: 24. Quando o conselho de sempre está errado
description: Reconheça quando o conselho padrão de prompting falha para um modelo ou tarefa e resolva a disputa a partir da fonte primária
type: lesson
---

# Lição 24. Quando o conselho de sempre está errado

**Ligação com a missão:** A trilha termina em confiar que você tome a decisão sobre um prompt e a explique a outra pessoa. Conselhos de prompting se espalham como slogans, e um slogan é verdadeiro para alguns modelos, tarefas e datas e falso para outros. Esta lição é o método para descobrir quais.
**Fonte principal:** [Paper: "When 'A Helpful Assistant' Is Not Really Helpful: Personas in System Prompts Do Not Improve Performances of Large Language Models", Zheng et al., 2023](https://arxiv.org/abs/2311.10054)
**Pré-requisitos:** [Lição 2](0002-system-prompts-and-roles.md), [Lição 7](0007-few-shot-biases.md), [Lição 10](0010-prompting-reasoning-models.md), [Lição 18](0018-a-regression-set-for-a-prompt.md), [Lição 23](0023-reviewing-a-production-prompt.md)

## Aquecimento

1. ▢ Por que o prompt para um modelo de raciocínio dá objetivos e restrições em vez de passos roteirizados?

<details markdown="1"><summary>Verificação</summary>

O modelo já produz a sua própria fase de raciocínio, então um plano escrito à mão pode limitá-lo a um caminho pior do que ele mesmo encontraria. Diga o que a resposta precisa satisfazer e deixe que ele decida como chegar lá.

</details>

2. ▢ O que os exemplos few-shot ensinam principalmente, segundo a lição 6?

<details markdown="1"><summary>Verificação</summary>

O formato, o espaço de rótulos e a distribuição das entradas, mais do que a correção de cada rótulo. É por isso que escolhê-los por cobertura e ordem importa mais do que polir cada um.

</details>

3. ▢ O que vai em um conjunto de regressão, e para que ele serve em uma disputa sobre um prompt?

<details markdown="1"><summary>Verificação</summary>

Entradas construídas principalmente a partir de falhas reais, cada uma com uma verificação sobre a saída. Em uma disputa ele é o terreno neutro: duas pessoas discutindo a partir de papers diferentes podem executar nele o prompt de sua preferência e comparar.

</details>

## Saiba isto

### O método

Um slogan como "dê um papel ao modelo" ou "sempre adicione uma instrução de passo a passo" chega sem as suas condições. O método para decidir se ele vale para você tem quatro passos:

1. **Encontre a fonte primária.** Não o post de blog que a cita. O paper ou a documentação do fornecedor, lidos para ver o que foi de fato medido.
2. **Confira o modelo e a data.** Quais modelos, qual tarefa, qual ano. Um conselho de 2022 sobre uma família de modelos pode não descrever o modelo que você chama hoje, e o guia de um fornecedor descreve os modelos desse fornecedor.
3. **Confira o que a afirmação cobre.** Acurácia em perguntas factuais não é tom. Um resultado em classificação curta não é um resultado em redação.
4. **Teste no seu conjunto de regressão.** Se a fonte e o seu caso puderem diferir, o resultado que decide é o seu (lições 18 e 19).

Cada um dos casos abaixo aplica isso. Nenhum diz que o conselho de sempre está sempre errado. Cada um diz o que a fonte primária sustenta.

### Caso 1: "Dê um papel ao modelo"

O guia da Anthropic diz: "Setting a role in the system prompt focuses Claude's behavior and tone for your use case" (definir um papel no system prompt focaliza o comportamento e o tom do Claude para o seu caso de uso) ([Anthropic: prompting best practices](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/claude-prompting-best-practices)). Zheng et al. testaram se personas ajudam em tarefas objetivas. Eles selecionaram 162 papéis em 6 tipos de relação interpessoal e 8 domínios de especialização e testaram 4 famílias de LLMs em 2.410 perguntas factuais. A conclusão deles: adicionar uma persona "does not improve model performance across a range of questions compared to the control setting where no persona is added" (não melhora o desempenho do modelo em um conjunto de perguntas em comparação com o cenário de controle em que nenhuma persona é adicionada). O gênero, o tipo e o domínio da persona ainda podem mudar a acurácia, então o efeito "can be largely random" (pode ser em grande parte aleatório), e escolher automaticamente a melhor persona para uma pergunta foi "often no better than random selection" (muitas vezes não melhor que uma seleção aleatória).

Os dois não se contradizem, porque afirmam coisas diferentes: tom e comportamento contra acurácia em perguntas factuais. A leitura que sobrevive aos dois: mantenha um papel quando quiser uma voz ou um escopo, não espere que ele torne os fatos mais precisos, e quando alguém disser que uma persona "melhora a acurácia", peça o teste. Os modelos do paper são os de 2023, então a parte datada da resposta é "para aqueles modelos e aquelas perguntas".

### Caso 2: "Think step by step"

A frase vem do resultado de raciocínio zero-shot (Kojima et al., 2022, listado em [Recursos](../RESOURCES.md)), que é anterior aos modelos com thinking embutido. Para um modelo que pensa antes de responder, o guia atual da Anthropic recomenda o hábito oposto: "A prompt like 'think thoroughly' often produces better reasoning than a hand-written step-by-step plan" (um prompt como "pense com profundidade" muitas vezes produz um raciocínio melhor do que um plano passo a passo escrito à mão), e para vários modelos nomeados ele diz para confiar no thinking embutido, porque um prompt que pede ao modelo para escrever o seu raciocínio "may be declined" (pode ser recusado). Ele mantém o chain-of-thought manual como alternativa apenas para quando o thinking está desligado. A lição 10 cobre a mecânica.

A disputa a resolver é, portanto, "qual modelo, com thinking ligado ou desligado". A resposta vem da documentação do próprio modelo, datada, e depois do seu conjunto de regressão.

### Caso 3: "Grite as regras importantes"

Ênfase em maiúsculas é uma forma comum de destacar uma regra. O guia da Anthropic diz que os modelos mais recentes são "more responsive to the system prompt than previous models" (mais responsivos ao system prompt do que os modelos anteriores), e que prompts escritos para reduzir o undertriggering "may now overtrigger" (podem agora causar overtriggering). A correção dele: "dial back any aggressive language" (reduza qualquer linguagem agressiva), então onde você poderia ter escrito "CRITICAL: You MUST use this tool when...", use "Use this tool when...". O guia nomeia o Claude Opus 4.5 e o Claude Opus 4.6 para isso, e o exemplo trata de uso de ferramentas.

Leia o escopo. A afirmação é sobre dois modelos nomeados e sobre o acionamento de ferramentas, não "maiúsculas nunca funcionam". Um prompt escrito para um modelo mais antigo e levado para um mais novo é o caso em que a ênfase herdada vale ser testada, tendo a versão simples como comparação. A lição 23 lista a redação enfática como um custo a questionar pelo mesmo motivo.

### Caso 4: "Mais exemplos é melhor"

O guia da Anthropic recomenda incluir de 3 a 5 exemplos e fazê-los relevantes, diversos e estruturados. Dois papers acrescentam o que uma contagem não consegue dizer. Lu et al. mostram que "the order in which the samples are provided can make the difference between near state-of-the-art and random guess performance" (a ordem em que as amostras são fornecidas pode fazer a diferença entre um desempenho próximo do estado da arte e um palpite aleatório), que isso vale "across model sizes" (entre tamanhos de modelo), e que uma boa permutação para um modelo não é transferível para outro. Sclar et al. constatam que a sensibilidade à formatação "remains even when increasing... the number of few-shot examples" (permanece mesmo ao aumentar... o número de exemplos few-shot).

Então a contagem não é a alavanca que o slogan sugere. Os mesmos exemplos em outra ordem, ou em outro formato, podem importar tanto quanto adicionar mais, e uma ordenação ajustada em um modelo não passa para o seguinte. Trate ordem e formato como variáveis a testar, que é a conclusão da lição 7 tornada mais forte.

### Resolvendo em uma conversa

Dois engenheiros citam o mesmo paper. Não escolha o mais confiante, e não parta a diferença no meio. Peça quatro coisas: a passagem, os modelos e a data, o que foi medido e uma execução no conjunto de regressão. Se a afirmação e o seu caso coincidem, a fonte se aplica. Se não coincidem, a fonte não é evidência sobre o seu caso, e a execução é.

## Prática

1. ▢ Um colega diz "Zheng et al. provaram que papéis são inúteis, então apague a linha do papel de todo system prompt". O que o paper sustenta, e o que você faria?

<details markdown="1"><summary>Verificação</summary>

O paper relata que adicionar uma persona não melhorou o desempenho em 2.410 perguntas factuais em 4 famílias de LLMs, em comparação com nenhuma persona. Ele não mede tom nem escopo, e relata que o efeito varia conforme a persona, não que seja zero para todo caso. Então "inútil para acurácia factual naqueles modelos" é sustentado, e "apague em todo lugar" não é. Execute o prompt com e sem o papel no conjunto de regressão e apague a linha apenas onde os números não mostrarem nada, já que removê-la também economiza tokens.

</details>

2. ▢ Você herda um prompt que diz "CRITICAL: you MUST call the search tool before every answer", ajustado em um modelo mais antigo, e o modelo mais novo agora busca até para perguntas triviais. Qual ação segue a fonte?

    - a) Testar uma versão simples "Use the search tool when" contra a redação antiga
    - b) Adicionar uma segunda regra em maiúsculas dizendo para não buscar em perguntas triviais
    - c) Voltar para o modelo mais antigo e manter a redação como está
    - d) Remover a instrução e esperar que o modelo mais novo deduza a política

<details markdown="1"><summary>Verificação</summary>

a). O guia da Anthropic descreve esse overtriggering para modelos mais novos nomeados e aconselha reduzir a linguagem agressiva, então a redação simples é a candidata, e o conjunto de regressão decide. b) empilha ênfase sobre ênfase. c) joga fora o modelo mais novo. d) remove uma política de que você pode precisar, e sem teste.

</details>

3. ▢ Um post de blog diz "adicione 'think step by step' a todo prompt". Você usa um modelo com thinking embutido ligado. Dê as duas primeiras verificações que você faz antes de mexer no prompt.

<details markdown="1"><summary>Verificação</summary>

Primeiro, encontre o resultado original e veja que modelos e que ano ele cobre: o paper de raciocínio zero-shot é de 2022, anterior aos modelos com thinking embutido. Segundo, leia a documentação do seu modelo: o guia da Anthropic recomenda instruções gerais em vez de passos prescritos com thinking ligado, e diz que pedir um raciocínio escrito pode ser recusado em alguns modelos nomeados. Depois teste com e sem a frase no conjunto de regressão, porque o guia é o relato de um fornecedor sobre os próprios modelos.

</details>

4. ▢ Seu prompt tem cinco exemplos com o rótulo raro por último, e a acurácia muda quando você os embaralha. Que fonte previu isso, e o que isso muda no conselho de usar de 3 a 5 exemplos?

<details markdown="1"><summary>Verificação</summary>

Lu et al. mostram que só a ordem dos exemplos pode mover os resultados entre perto do estado da arte e perto do acaso, e que uma boa ordem para um modelo não é transferível para outro. O conselho sobre a contagem continua um ponto de partida, mas não basta: a ordem e o formato fazem parte do comportamento do prompt, então registre a ordem que passou e teste-a de novo quando o snapshot do modelo mudar (lição 16).

</details>

5. ▢ Escreva as três perguntas que você faria antes de aceitar "personas melhoram a acurácia" em uma revisão de design, e o único resultado que decidiria isso para o seu produto.

<details markdown="1"><summary>Verificação</summary>

Em quais modelos e em quais perguntas isso foi medido? A linha de base era um prompt sem persona? A medida era acurácia ou tom? O que decide para o seu produto é uma comparação pareada no seu conjunto de regressão do prompt com e sem a persona, com a diferença julgada contra o ruído entre execuções (lição 19). Uma fonte que não corresponde a nenhuma das suas condições é contexto, não evidência.

</details>

## Prática no mundo real

- [ ] Escolha um conselho de prompting que você segue sem saber a fonte e rastreie-o até um paper ou um documento de fornecedor. Anote os modelos, a data e o que foi medido.
- [ ] Pegue uma persona ou instrução enfática em um prompt que você mantém e escreva a comparação de dois prompts que a testaria, mesmo que ainda não a execute.
- [ ] Amanhã: execute essa comparação em um conjunto de regressão, ou esboce cinco casos para um, e registre o resultado nas notas de mudança do prompt.

## Para ir além

- [Checklist de Revisão de Prompt](../reference/prompt-review-checklist.md)
- [Paper: "When 'A Helpful Assistant' Is Not Really Helpful: Personas in System Prompts Do Not Improve Performances of Large Language Models", Zheng et al., 2023](https://arxiv.org/abs/2311.10054)
- [Docs: "Prompting best practices", Claude Platform Docs](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/claude-prompting-best-practices)
- [Paper: "Fantastically Ordered Prompts and Where to Find Them", Lu et al., 2021](https://arxiv.org/abs/2104.08786)
- [Recursos](../RESOURCES.md)

---

Este é o fim da trilha, e o hábito para o qual ela foi construída é o desta lição: um prompt é uma afirmação sobre um modelo, então descubra de onde a afirmação vem, confira o que ela cobriu e teste-a nos seus próprios casos antes de defendê-la perante qualquer outra pessoa.

Não ficou claro? Releia a fonte principal no topo, pois esta lição a comprime e é na compressão que o entendimento se perde. Consulte o [glossário](../GLOSSARY.md) para qualquer termo que tenha parecido escorregadio.

Se a lição em si é que não está clara, e não o material, isso é um defeito: [abra uma issue](https://github.com/TokenCemetery/teach/issues).
