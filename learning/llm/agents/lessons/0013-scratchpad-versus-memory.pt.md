---
title: "13. Scratchpad contra memória"
description: "A diferença entre as notas que um agente mantém durante uma execução e os fatos de que precisa entre várias execuções"
type: lesson
---

# Lição 13. Scratchpad contra memória

**Ligação com a missão:** Diagnosticar um agente que falha a partir da trajetória, em vez de acrescentar mais uma instrução ao prompt, entendendo que informação persiste entre execuções e qual some quando uma execução termina.
**Fonte principal:** [Article: "Effective Context Engineering for AI Agents", Anthropic Engineering](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents)
**Pré-requisitos:** [Lição 12](0012-sub-agents-as-context-isolation.md), [Trajetória](../GLOSSARY.md)

## Aquecimento

1. ▢ O que uma trajetória registra?

<details markdown="1"><summary>Verificação</summary>

O registro completo e ordenado de uma execução de agente: cada mensagem enviada ao modelo, cada chamada de ferramenta que o modelo fez e cada resultado que o harness anexou de volta.

</details>

2. ▢ Quando você inicia um subagente para cuidar de um trabalho delimitado, o subagente vê a transcrição completa do pai?

<details markdown="1"><summary>Verificação</summary>

Não. O subagente recebe sua própria transcrição nova, com histórico vazio. Ele pode receber um resumo ou um contexto específico que o agente pai lhe passa como prompt inicial, mas não herda a trajetória completa do pai.

</details>

## Saiba isto

Um **scratchpad** é, na prática, só parte da transcrição, ou uma nota que o agente escreve e relê dentro de uma única execução. Durante uma tarefa longa, o agente pode usar um scratchpad para acompanhar um total parcial, um plano de vários passos ou descobertas intermediárias, para que o modelo não precise rederivá-los a cada turno. O scratchpad é efêmero: quando o harness para o loop e a execução termina, o scratchpad vive na trajetória, mas em nenhum outro lugar. Se você inicia uma nova execução de agente uma hora depois para continuar o trabalho, o scratchpad se foi.

É aqui que se instala uma confusão comum. Um agente manteve um scratchpad durante uma execução e "lembrou" de algo. Esse mesmo agente, reiniciado do zero, não vai lembrar. O modelo pode usar o mesmo nome para a ferramenta ou o arquivo do scratchpad, mas o conteúdo se foi porque a execução se foi.

A **memória entre execuções** é fundamentalmente diferente. Uma nova execução começa com a transcrição vazia, então tudo o que o modelo precisa saber de uma execução anterior tem de viver em algum lugar fora de qualquer trajetória individual e ser carregado de volta, de propósito, quando a próxima execução começa. O harness lê de um armazenamento durável, um arquivo, um banco de dados ou um sistema de recuperação, antes de o loop começar, e coloca os fatos relevantes no prompt inicial ou no contexto para que o modelo possa agir sobre eles.

Aqui está um exemplo concreto: Um agente está fazendo a revisão de código de um pull request grande. Durante a execução de uma hora, ele mantém um scratchpad listando todo arquivo que já verificou, de modo que, quando o modelo considera um novo arquivo, pode dar uma olhada no scratchpad e evitar reanalisar um trabalho já feito. O scratchpad é parte da transcrição. Quando a execução termina, a revisão está concluída e o scratchpad é arquivado como parte da trajetória.

Agora imagine um cenário diferente: Um assistente de código ajuda um único usuário a escrever código em muitas sessões separadas ao longo de semanas. O usuário tem forte preferência por um certo estilo de código, convenção de nomes e biblioteca. Se o assistente é reiniciado a cada sessão, ele começa sem nenhum conhecimento dessas preferências. O assistente precisa de memória entre execuções: um arquivo ou nota que o harness lê no início de cada sessão e que diz "O usuário prefere X, usa Y, evita Z." Esse fato não está em nenhuma trajetória individual; ele é guardado de forma durável e carregado no início da execução.

A ideia-chave de [Effective Context Engineering for AI Agents](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents) é que esses são dois mecanismos separados. Um scratchpad é uma ferramenta ou artefato que o agente manipula durante uma execução. A memória entre execuções é uma camada de dados fora do loop do agente, gerenciada pelo harness.

## Prática

1. ▢ Um agente está resolvendo um problema de matemática de vários passos. Durante a execução, ele escreve suas notas de trabalho em um arquivo de scratchpad. No final, anexa a resposta final a um arquivo de resultados. Dias depois, você inicia o mesmo agente de novo com um problema diferente. O que ainda estará lá?

    - a) As notas do scratchpad.
    - b) O arquivo de resultados.
    - c) Os dois, porque ambos são arquivos.
    - d) Nenhum dos dois, porque os arquivos são limpos a cada execução.

<details markdown="1"><summary>Verificação</summary>

**b)** O arquivo de resultados ainda estará lá porque é armazenamento durável fora da execução. As notas do scratchpad, mesmo tendo sido escritas em um arquivo, só são relevantes para a execução antiga e não são carregadas automaticamente na nova transcrição. Se o agente precisa dessas notas antigas na nova execução, o harness precisa lê-las de propósito e incluí-las no prompt inicial.

</details>

2. ▢ Você está projetando um agente que precisa lembrar os nomes dos arquivos que já processou. Você usaria um scratchpad ou memória entre execuções?

<details markdown="1"><summary>Dica</summary>

Pense se a informação é usada dentro de uma única execução ou entre várias execuções separadas.

</details>

<details markdown="1"><summary>Verificação</summary>

Se todos os arquivos são processados em uma única execução longa, um scratchpad basta. O agente consulta o scratchpad a cada vez e evita reprocessar. Se o trabalho é dividido entre várias execuções do agente, talvez reiniciado a cada dia ou uma execução por requisição do usuário, então você precisa de memória entre execuções para que uma nova execução veja o que foi feito antes.

</details>

3. ▢ Qual é a razão fundamental de um agente reiniciado com um harness novo não conseguir ver as notas que escreveu em um scratchpad na execução anterior?

<details markdown="1"><summary>Verificação</summary>

Porque o scratchpad é parte da transcrição, e uma nova execução começa com a transcrição vazia. A trajetória antiga é arquivada, mas não é carregada na nova execução. Para tornar o conteúdo do scratchpad visível em uma nova execução, o harness teria de lê-lo do armazenamento e inseri-lo no prompt inicial, o que o move de scratchpad para memória deliberada entre execuções.

</details>

4. ▢ Você está construindo um agente que ajuda um usuário a gerenciar uma lista pessoal de tarefas. O agente adiciona tarefas, conclui-as e filtra por tag. A lista de tarefas deve ser um scratchpad, local a uma execução, ou memória entre execuções, persistida entre execuções? Por quê?

<details markdown="1"><summary>Verificação</summary>

Memória entre execuções. Uma lista de tarefas precisa persistir além de uma sessão. Se o usuário inicia o agente amanhã e pede "mostre minhas tarefas", o agente precisa ainda ver a lista de hoje. Um scratchpad sumiria quando a execução terminasse, e os dados do usuário se perderiam.

</details>

## Prática no mundo real

- [ ] Gaste dois minutos percorrendo o código do seu próprio agente. Encontre onde o harness cria uma transcrição nova, vazia ou só com um prompt inicial. Anote o que você vê.
- [ ] Procure qualquer "memória" ou "estado" que seu agente salva atualmente. Ele é carregado pelo harness antes de o loop começar, ou só referenciado durante a execução? Se é só durante a execução, é um scratchpad. Se é carregado no início, é memória entre execuções.
- [ ] Amanhã: Encontre ou escreva um uso de scratchpad, em que um agente escreve uma nota, a relê e então a execução termina. Separadamente, encontre ou imagine um uso entre execuções, em que um agente precisa de um fato da execução da semana passada para responder à pergunta de hoje.

## Para ir além

- [Article: "Effective Context Engineering for AI Agents", Anthropic Engineering](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents)
- [Recursos](../RESOURCES.md)

---

Não ficou claro? Releia a fonte principal no topo, já que esta lição a comprime e é na compressão que o entendimento escapa. Consulte o [glossário](../GLOSSARY.md) para qualquer termo que pareceu escorregadio.

Se o problema é a lição em si, e não o material, isso é um defeito: [abra uma issue](https://github.com/TokenCemetery/teach/issues).
