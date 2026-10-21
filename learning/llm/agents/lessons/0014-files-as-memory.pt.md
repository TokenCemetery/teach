---
title: "14. Arquivos como memória"
description: "Usar arquivos duráveis como a forma mais simples de memória entre execuções para agentes"
type: lesson
---

# Lição 14. Arquivos como memória

**Ligação com a missão:** Diagnosticar um agente que falha a partir da trajetória, em vez de acrescentar mais uma instrução ao prompt, construindo sistemas em que a memória do agente é inspecionável e o harness pode curar o que persiste.
**Fonte principal:** [Article: "Effective Context Engineering for AI Agents", Anthropic Engineering](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents)
**Pré-requisitos:** [Lição 13](0013-scratchpad-versus-memory.md)

## Aquecimento

1. ▢ Você inicia um agente com uma transcrição nova pela segunda vez. O que a transcrição vazia diz a você?

<details markdown="1"><summary>Verificação</summary>

Que o agente está começando uma nova execução sem memória da execução anterior, a menos que o harness tenha carregado fatos de volta de propósito antes de o loop começar.

</details>

2. ▢ Um agente escreveu notas em um arquivo durante sua última execução. Se você quer que essas notas influenciem o comportamento do agente na nova execução, o que o harness precisa fazer?

<details markdown="1"><summary>Verificação</summary>

O harness precisa ler o arquivo, ou partes relevantes dele, e incluir o conteúdo no contexto inicial ou no prompt da nova execução, para que o modelo possa vê-lo e agir sobre ele.

</details>

## Saiba isto

Escrever fatos em um arquivo simples, ou em um armazenamento durável parecido, que o harness relê em uma execução posterior é a forma mais simples que funciona de memória entre execuções. O padrão é direto: dê ao agente uma ferramenta para escrever uma nota, um arquivo markdown, um registro JSON ou um pequeno log estruturado, e, no início de uma execução posterior, o harness lê as partes relevantes desse arquivo de volta para a nova transcrição antes de o loop começar.

Isso é deliberadamente simples e inspecionável em comparação com, digamos, um banco de dados vetorial. Uma pessoa pode abrir o arquivo e ler exatamente o que o agente "lembra". Você pode editá-lo à mão se precisar. Pode ver entradas obsoletas ou erradas e corrigi-las sem retreinar nada.

O risco é real, porém. Um agente que continua acrescentando a um arquivo de memória sem nunca podar ou atualizar acumula, com o tempo, notas obsoletas ou contraditórias. Uma nota que era verdadeira no mês passado pode ser falsa hoje. Dois fatos diferentes podem se contradizer. Esse é o mesmo problema de context rot que as lições 10 e 11 trataram para uma transcrição crescendo dentro de uma única execução. A memória precisa da mesma curadoria ativa: revisão periódica, arquivamento de entradas antigas, consolidação de duplicatas, remoção de fatos que não se aplicam mais.

Um esclarecimento importante: a recuperação sob demanda, da lição 11, buscando detalhes de um corpus de documentos ou de trabalho anterior por meio de busca, não é o mesmo que memória, embora ambas envolvam "trazer texto para o contexto". A recuperação responde à pergunta "o que é relevante para esta consulta específica agora?" pesquisando um corpus grande. A memória é um conjunto pequeno e deliberadamente curado de fatos que o agente, ou quem o projetou, decidiu que vale a pena levar adiante independentemente da consulta atual. Um assistente de código pode recuperar exemplos do trabalho passado do usuário para ilustrar um estilo, mas também precisa de uma memória que diga "o usuário prefere async/await a callbacks" como um fato permanente, e não como resultado de consulta. O corpus de recuperação serve para responder perguntas específicas; o arquivo de memória serve para o contexto permanente.

A ressalva honesta de [Effective Context Engineering for AI Agents](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents) é esta: a memória de agentes entre execuções é uma área mais nova e menos assentada. Os sistemas de produção para memória entre execuções ainda estão evoluindo. Esta lição cobre o padrão baseado em arquivos, que é simples e inspecionável por pessoas, mas não necessariamente a abordagem definitiva que o seu sistema de produção usará daqui a anos.

## Prática

1. ▢ Um agente está ajudando um usuário a aprender a cozinhar. O agente anota que o usuário não gosta de coentro e sugere receitas sem ele. Quando você reinicia o agente no dia seguinte para uma nova sessão de culinária, o harness deve carregar de volta a nota sobre o coentro a partir do arquivo de memória?

<details markdown="1"><summary>Verificação</summary>

Sim. A preferência é um fato permanente sobre o usuário que vale entre sessões. O harness deve ler o arquivo de memória no início e incluir "o usuário não gosta de coentro" no contexto inicial, para que o modelo possa usá-lo ao gerar novas receitas.

</details>

2. ▢ Durante uma execução, um agente escreve em um scratchpad "arquivos verificados até agora: api.py, utils.py, config.py" para evitar reanalisá-los. A execução termina. Essa entrada do scratchpad deve ser salva no arquivo de memória entre execuções?

<details markdown="1"><summary>Dica</summary>

Essa informação em particular, a lista de arquivos verificados nesta execução específica, precisa seguir adiante para execuções futuras, ou foi apenas uma contabilidade útil dentro de uma tarefa?

</details>

<details markdown="1"><summary>Verificação</summary>

Provavelmente não, a menos que a tarefa se estenda por várias execuções do agente. Se cada revisão de código é uma tarefa nova e independente, a lista de arquivos verificados na Execução A não é relevante para a Execução B. Salvar cada entrada do scratchpad entulharia o arquivo de memória com detalhes efêmeros. Uma boa heurística: só salve fatos na memória se uma execução futura for precisar deles.

</details>

3. ▢ Você nota que o arquivo de memória do agente agora contém conselhos conflitantes: "o usuário prefere tabs" e "o usuário prefere espaços", escritos com semanas de diferença. O que você deve fazer?

    - a) Apagar o arquivo de memória inteiro para o agente começar do zero.
    - b) Revisar e editar manualmente o arquivo para corrigir a contradição.
    - c) Adicionar uma nova ferramenta ao agente para que ele resolva conflitos automaticamente.
    - d) Ignorar, já que o modelo vai descobrir qual é o atual.

<details markdown="1"><summary>Verificação</summary>

**b)** Revisar e editar manualmente o arquivo. A curadoria da memória é uma responsabilidade humana. Você precisa entender qual entrada está obsoleta, corrigi-la ou removê-la e manter o arquivo limpo e autoritativo. Apagar o arquivo inteiro perde outros fatos valiosos. Automatizar a resolução de conflitos sem julgamento humano corre o risco de codificar a preferência errada. O modelo não deveria ter de adivinhar nem raciocinar sobre contradições na própria memória.

</details>

4. ▢ Como um sistema de memória baseado em arquivos difere de um sistema de recuperação que pesquisa um corpus do trabalho passado do agente?

<details markdown="1"><summary>Verificação</summary>

Um sistema de recuperação responde "o que do meu trabalho passado é relevante para esta consulta?" e traz material com base em correspondência por palavra-chave ou semântica. Um sistema de memória guarda um pequeno conjunto de fatos permanentes que o harness carrega independentemente da consulta. A memória é curada e durável; a recuperação é guiada pela consulta. Você pode recuperar exemplos de código passados quando o usuário pergunta "mostre como resolvi isto antes", mas você lembra que "o usuário prefere async/await" como uma preferência permanente o tempo todo.

</details>

## Prática no mundo real

- [ ] Se você tem um agente que roda mais de uma vez, verifique se o harness carrega algum fato armazenado antes da primeira chamada ao modelo. Se não, adicione um print ou log para ver o que está acontecendo no momento de início da execução.
- [ ] Projete um formato simples de arquivo de memória para uma tarefa que você conhece bem. Que fatos você escreveria? Como você saberia quando atualizar ou remover uma entrada?
- [ ] Amanhã: Construa um agente de uma execução que escreve um fato em um arquivo de memória, em qualquer formato: JSON, markdown ou texto simples. Depois construa uma segunda execução do mesmo agente que lê esse arquivo e o usa. Sem banco de dados vetorial, sem busca, apenas armazenamento durável e carregamento gerenciado pelo harness.

## Para ir além

- [Article: "Effective Context Engineering for AI Agents", Anthropic Engineering](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents)
- [Recursos](../RESOURCES.md)

---

Não ficou claro? Releia a fonte principal no topo, já que esta lição a comprime e é na compressão que o entendimento escapa. Consulte o [glossário](../GLOSSARY.md) para qualquer termo que pareceu escorregadio.

Se o problema é a lição em si, e não o material, isso é um defeito: [abra uma issue](https://github.com/TokenCemetery/teach/issues).
