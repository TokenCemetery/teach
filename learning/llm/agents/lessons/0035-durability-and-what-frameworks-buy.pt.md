---
title: "35. Durabilidade e o que um framework oferece"
description: "A execução durável e retomável de agentes como problema de engenharia, o que os frameworks oferecem concretamente e um princípio de decisão para adotar um"
type: lesson
---

# Lição 35. Durabilidade e o que um framework oferece

**Ligação com a missão:** Decidir se escreve você mesmo um harness de agente ou adota um framework, com base em que garantias você realmente precisa para o deployment.
**Fonte principal:** [Article: "Building Effective Agents", Anthropic Engineering](https://www.anthropic.com/engineering/building-effective-agents)
**Pré-requisitos:** [Lição 34](0034-prompt-caching-and-concurrency.md), [Harness](../GLOSSARY.md)

## Aquecimento

1. ▢ Da Lição 7, você aprendeu que, como a transcrição é todo o estado de um agente, retomar uma execução significa devolver ao modelo a transcrição salva. O que isso significa em termos de uma execução ser "retomável em princípio"?

<details markdown="1"><summary>Verificação</summary>

Em princípio, qualquer execução de agente é retomável porque a transcrição captura tudo o que o agente sabe. Se você salva a transcrição depois de cada turno e acontece uma falha, pode carregar a transcrição salva, anexar o último turno que falhou ou ficou incompleto e continuar. A transcrição é todo o estado, então a retomada não exige mais nada.

</details>

2. ▢ Da Lição 33, você aprendeu que um orçamento de custo por tarefa soma o custo completo de todas as tentativas, retries e reflexões até uma tarefa ter sucesso. Se um agente cai no meio da execução e você precisa reiniciar do começo, como isso afeta o orçamento de custo por tarefa?

<details markdown="1"><summary>Verificação</summary>

O reinício acrescenta ao orçamento uma tentativa completa adicional. Se um agente cai no turno 15 de uma execução de 30 turnos, você perdeu 15 turnos de trabalho e precisa pagar de novo pelos 30 turnos. O orçamento de custo por tarefa agora é aproximadamente dobrado (duas execuções completas de 30 turnos em vez de uma). Essa é uma penalidade de custo significativa, e é por isso que a durabilidade (evitar falhas e retomar automaticamente do último estado salvo) importa para o controle de custos.

</details>

## Saiba isto

### Durabilidade é distinta de retomabilidade em princípio

A Lição 7 estabeleceu que execuções de agente são retomáveis em princípio: a transcrição é o estado. Mas "retomável em princípio" e "retomável em produção" são coisas diferentes. A retomabilidade em princípio diz "se uma pessoa salva a transcrição manualmente e reinicia o agente, ele continuará". A durabilidade em produção diz:

- A transcrição é persistida automaticamente em armazenamento durável (um banco de dados, um sistema de arquivos com backups, e não só memória) depois de cada turno.
- Se o processo cai, o último estado persistido é carregado automaticamente e a execução é retomada sem intervenção manual.
- Se vários agentes rodam de forma concorrente, o estado de cada um é rastreado de forma independente, de modo que uma queda em um não perde trabalho em outro.
- Se uma chamada de ferramenta estoura o tempo ou a rede falha, o agente tenta de novo ou desfaz com elegância, sem deixar estado parcial.

Esse trabalho de infraestrutura é distinto do próprio loop do agente (Lição 6). O loop não se importa com durabilidade; apenas processa o que recebe. O harness (o código ao redor do loop) precisa construir a durabilidade como uma preocupação explícita.

### Como são quedas e falhas sem durabilidade

Sem estado durável, estes são os modos de falha:

- Queda do processo no meio da execução: toda a transcrição do agente se perde (se estava apenas em memória). O usuário precisa reiniciar a tarefa do começo. O orçamento de custo por tarefa é dobrado.
- Timeout de rede em uma chamada de ferramenta: o harness não sabe se a ferramenta teve sucesso ou falhou. Pode tentar de novo, pode não tentar. A transcrição pode ter um resultado anexado, ou pode não ter, dependendo do tratamento de erros do harness. O estado fica inconsistente.
- O agente trava esperando o resultado de uma ferramenta: o processo fica preso e precisa ser encerrado manualmente. Nenhum checkpoint é salvo. A execução inteira se perde.
- Vários agentes rodando de forma concorrente, um cai: os outros agentes continuam, mas não há visibilidade de qual parte do sistema falhou nem de como retomar o que falhou.

Cada um desses é um problema real de deployment. "Execução durável" é a prática de construir sistemas que tratam essas falhas de forma automática e correta.

### O que um framework oferece concretamente

Quando você adota um framework para o desenvolvimento de agentes, ele costuma incluir algumas ou todas estas garantias:

**Estado durável e checkpointing automático.** O framework persiste automaticamente a transcrição (e qualquer estado do agente) em armazenamento durável depois de cada turno. Se o processo cai, a execução seguinte carrega automaticamente o último checkpoint e retoma dali. Você não precisa escrever a lógica de persistência.

**Fluxo de controle em grafo.** Em vez de escrever um loop à mão (Lição 6), você descreve a estrutura do agente como um grafo: "Depois deste passo, se o resultado é X, vá para cá; se Y, vá para lá." O framework cuida do fluxo de controle e da persistência, de modo que você foca nos nós (os passos) em vez de no loop em si. Isso é útil para agentes com ramificações complexas ou lógica condicional.

**Políticas embutidas de retry e backoff.** Quando uma chamada de ferramenta falha (um erro de rede, um timeout, um limite de taxa), o framework tem uma estratégia de retry configurada: esperar um pouco, tentar de novo, backoff exponencial. Você não precisa implementar retries no seu próprio harness.

**Tracing e observabilidade integrados.** O framework gera automaticamente os traces estruturados da Lição 29: eventos com marcas de tempo, spans, metadados sobre cada passo. Você pode consultar esse trace sem ligá-lo você mesmo. Alguns frameworks se integram a backends de observabilidade (como um serviço de tracing) para que você veja as execuções do agente em um painel.

**Rollback e compensação.** Alguns frameworks permitem definir ações compensatórias: se o passo A teve sucesso mas o passo B falhou, desfazer A automaticamente. Isso é útil para agentes que fazem mudanças em sistemas externos e precisam se recuperar se passos posteriores falham.

Nem todos os frameworks oferecem todas essas coisas. Alguns são mínimos (checkpointing mais retries). Alguns são abrangentes (tudo isso e mais). O princípio de decisão (abaixo) é sobre quais capacidades você realmente precisa.

### O que os frameworks NÃO oferecem

É importante ser claro sobre o que os frameworks não resolvem:

- O loop do agente em si continua o mesmo (da Lição 6). O framework não torna o loop mais simples nem mais rápido; apenas o envolve com durabilidade e observabilidade.
- O custo em tokens não é reduzido por usar um framework. Um framework não torna os agentes mais baratos; torna-os mais confiáveis e observáveis.
- A qualidade de raciocínio do agente não é melhorada por um framework. Um framework não torna o modelo melhor em decisões; você ainda precisa projetar as ferramentas, os prompts e o planejamento (Lições 8, 9, 16) você mesmo.
- O framework não é neutro. Adotar um framework compromete você com suas abstrações (fluxo de controle em grafo, seu formato de configuração, seu modelo de observabilidade, suas restrições de deployment). Trocar de framework depois é caro.

### O princípio de decisão: quando adotar um framework

O artigo "Building Effective Agents" observa que muitas equipes constroem primeiro um loop mínimo de agente (Lição 6) e só mais tarde percebem que precisam de durabilidade. A decisão de adotar um framework deve se basear em se as garantias do framework resolvem um problema de deployment que você tem, e não em se escrever o loop pareceu difícil (o loop é a parte fácil).

Adote um framework quando:

- **Você precisa de execução durável.** Seus agentes vão rodar por tempo suficiente (ou ser importantes o bastante) para que perder trabalho em quedas seja inaceitável. Um loop simples sem persistência não é adequado para tarefas de produção.
- **Você precisa de observabilidade em escala.** Você tem vários agentes rodando de forma concorrente e precisa ver o que cada um está fazendo, rastrear falhas e correlacionar logs. Um harness baseado em instruções de print não vai escalar.
- **Você tem fluxo de controle complexo.** Seu agente precisa de ramificação condicional ou loops (por exemplo, "se esta condição, chame este conjunto de ferramentas; senão chame este outro conjunto"). O modelo em grafo de um framework é mais limpo do que condicionais escritas à mão.
- **Você quer retry e backoff embutidos.** Você está chamando APIs externas que podem falhar temporariamente e quer que o framework trate os retries automaticamente com backoff exponencial. Escrever isso você mesmo é tedioso e propenso a erros.

NÃO adote um framework quando:

- **Você está experimentando.** Em pesquisa ou prototipagem, um loop simples é mais rápido de iterar do que aprender um framework. Volte à decisão do framework quando a abordagem estiver estável.
- **Seu agente é simples.** Um único agente com algumas chamadas de ferramenta e um objetivo direto não precisa da complexidade de um framework. Um loop mais um arquivo de transcrição pode ser tudo de que você precisa.
- **Você tem restrições incomuns de deployment.** Alguns frameworks pressupõem ambientes específicos (nuvem, Docker etc.) ou têm características de desempenho que não se encaixam nas suas restrições. Você pode precisar de um harness customizado.
- **O framework é imaturo ou fortemente acoplado a um fornecedor.** Os padrões de execução durável ainda estão evoluindo. Alguns frameworks são bem estabelecidos e documentados (procure avaliações e deployments em produção); outros não. E alguns são fortemente acoplados à API de um fornecedor, o que limita sua flexibilidade depois.

### Como avaliar um framework

Se você decide adotar um framework, estas são as perguntas a fazer:

- Ele suporta checkpointing e retomada? Com que frequência? A granularidade do checkpoint (por turno, por tentativa, por tarefa) é a de que você precisa?
- Que observabilidade ele oferece? Você consegue consultar traces? Consegue integrar com o seu logging e monitoramento existentes?
- Que abstrações de fluxo de controle ele suporta? Combinam com a estrutura do seu agente, ou você teria de entortar o agente para caber?
- Qual é o modo de falha se o framework cair? Você consegue recuperar suas transcrições e continuar sem o framework?
- Como ele lida com concorrência? Vários agentes conseguem rodar de forma independente sem interferir uns nos outros?
- Que lock-in de fornecedor existe? Se você precisar trocar depois, quanto trabalho seria?

A última pergunta é importante: não existe uma única fonte autoritativa e neutra quanto a fornecedor para execução durável de agentes, como existe, por exemplo, para a especificação do MCP (Lição 20). Os padrões de execução durável estão documentados principalmente nos guias dos próprios frameworks. Então trate esta lição como o vocabulário e o arcabouço de decisão, e não como uma comparação de frameworks. Ao avaliar um framework específico, leia a documentação dele para entender suas garantias específicas.

### A história de ponta a ponta: do loop à produção

Eis o arco de um sistema de agente típico:

1. **Desenvolvimento (Lição 6).** Escreva um loop que envia a transcrição ao modelo e executa ferramentas. É rápido de prototipar.
2. **Teste (Lição 29).** Construa traces e diagnóstico para entender o que seu agente está fazendo, quando falha e por quê. Aprenda onde seu agente é frágil.
3. **Otimização (Lições 10-34).** Implemente gerenciamento de contexto, prompt caching, melhor planejamento. Reduza o custo em tokens e a latência.
4. **Deployment.** Agora você precisa decidir: como é a produção? Se é uma tarefa avulsa ou um experimento, um script mais um arquivo de transcrição pode bastar. Se é um serviço atendendo usuários, um loop simples não é adequado. Você precisa de durabilidade, observabilidade, políticas de retry e um jeito de acompanhar muitos agentes concorrentes. É aqui que entra a decisão do framework.

Um framework não é o começo; é a resposta para "quem constrói e mantém a camada de durabilidade e observabilidade?" Você a constrói você mesmo (um harness customizado mais infraestrutura), ou adota a resposta de um framework (aceita suas abstrações e restrições). Ambas são escolhas legítimas. A decisão do framework não é "consigo escrever um loop de agente" (a Lição 6 já respondeu que sim). A pergunta é "quero construir eu mesmo essa infraestrutura de produção, ou adotar a solução de um framework existente?"

## Prática

1. ▢ Você está rodando um agente para processar 1.000 tickets de suporte ao cliente. Cada ticket leva 20 turnos de um agente para ser tratado. Se o agente cai no turno 10 do ticket 500 e você não tem checkpointing, quantos turnos no total são perdidos ou desperdiçados?

<details markdown="1"><summary>Verificação</summary>

Você perde 10 turnos de trabalho no ticket 500. Quando o processo reinicia, você precisa rodar o ticket inteiro de novo desde o começo, desperdiçando mais 20 turnos. Você também precisa rodar de novo os tickets 1-499 (que foram concluídos mas ainda estão em memória/perdidos se o processo caiu). Se você tivesse checkpointing, salvaria depois de cada ticket, então perder um ticket custa 20 turnos, e não mais. Para 1.000 tickets * 20 turnos = 20.000 turnos no total. Sem checkpointing, uma queda no meio de uma tarefa desperdiça aproximadamente 10.000 turnos (metade do trabalho restante mais rodar de novo a tarefa que caiu). É por isso que a durabilidade importa para tarefas em larga escala.

</details>

2. ▢ Você tem duas opções para o seu sistema de agentes: a Opção A é escrever um harness customizado com durabilidade (checkpointing, retries, observabilidade). Isso leva 2 semanas para construir e depurar. A Opção B é adotar um framework existente (que cuida de tudo isso para você) e gastar 1 semana aprendendo-o. Os dois sistemas vão rodar a mesma lógica de agente. Por que a Opção B ainda poderia ser mais cara no longo prazo?

<details markdown="1"><summary>Dica</summary>

Pense em flexibilidade, manutenção e no que acontece se seus requisitos mudam ou se você quer trocar de sistema.

</details>

<details markdown="1"><summary>Verificação</summary>

A Opção B compromete você com as abstrações e a implementação do framework. Se seus requisitos mudam (por exemplo, você precisa de um fluxo de controle diferente ou de um backend de armazenamento diferente), você fica restringido pelo que o framework suporta. Se quiser trocar de framework depois, precisa portar todas as definições e workflows dos seus agentes. A Opção A (harness customizado) é mais flexível, mas mais cara no início e de manter. O trade-off é: a Opção B economiza tempo no início, mas prende você; a Opção A custa mais no início, mas dá flexibilidade de longo prazo. O ponto de equilíbrio depende das suas expectativas sobre quanto tempo o sistema vai rodar e quão provável é que os requisitos mudem.

</details>

3. ▢ Você está avaliando dois frameworks para o desenvolvimento de agentes. O Framework X oferece checkpointing e retries, mas nenhuma observabilidade integrada (você precisa ligar o tracing você mesmo). O Framework Y oferece tudo isso mais um construtor de fluxo de controle em grafo, mas exige que todos os agentes sejam definidos em sua DSL proprietária. Qual framework você deve escolher se sua principal preocupação é evitar retrabalho quando um agente cai e retomar automaticamente?

    - a) Framework X, porque é mais simples e obriga você a aprender menos.
    - b) Framework Y, porque sua observabilidade integrada ajudará a depurar quedas mais depressa.
    - c) Qualquer um oferece o recurso central de checkpointing de que você precisa; a escolha depende das suas outras restrições.
    - d) Nenhum; você deve construir um harness customizado para não ficar preso.

<details markdown="1"><summary>Verificação</summary>

**c)** Os dois frameworks oferecem checkpointing e retomada automática, que é a sua principal preocupação. As diferenças (observabilidade, DSL) são secundárias. Se você precisa de observabilidade integrada ou gosta do modelo em grafo, o Framework Y pode valer o lock-in. Se prefere ligar a observabilidade você mesmo ou já tem código de agente em Python/Go/etc., o Framework X serve. Nenhum está errado; depende das suas outras restrições. A opção a está errada porque a simplicidade sozinha não é o fator decisivo. A opção b confunde observabilidade (bom de ter) com durabilidade (o requisito que você declarou). A opção d não está errada (um harness customizado sempre dá flexibilidade), mas foge da pergunta; se a durabilidade é importante, você precisa de alguma solução, e a decisão é se essa solução é um framework ou customizada.

</details>

4. ▢ Você construiu um agente usando um loop simples (Lição 6) sem persistência. O agente funciona bem nos testes. Agora você quer implantá-lo em produção para atender requisições reais de usuários. Qual é a infraestrutura mínima que você precisa acrescentar antes de poder dizer com confiança que o agente é durável em produção?

<details markdown="1"><summary>Verificação</summary>

No mínimo: (1) Persistência automática da transcrição em armazenamento durável (um banco de dados ou sistema de arquivos com backups) depois de cada turno do loop. (2) Carregamento automático da última transcrição persistida ao reiniciar o processo, para que o agente retome do último checkpoint, e não do começo. (3) Tratamento de erros elegante nas chamadas de ferramenta: se uma ferramenta estoura o tempo ou devolve um erro, o agente ou tenta de novo com uma política de backoff, ou registra a falha explicitamente na transcrição (para que o estado seja consistente). (4) Para agentes concorrentes, cada agente precisa ter sua própria transcrição e seu próprio checkpoint isolados. Essas quatro peças transformam um loop de desenvolvimento em algo que consegue sobreviver a quedas e atender tráfego de produção.

</details>

## Prática no mundo real

- [ ] Revise a documentação de um framework de agentes de produção (por exemplo, LangGraph, CrewAI, os Managed Agents da Anthropic ou outro framework que você conheça). Anote as garantias específicas de durabilidade que ele oferece: o que é persistido, com que frequência e como a recuperação é tratada?
- [ ] Projete a camada de durabilidade para um agente simples. Escreva as peças que você precisaria construir: checkpointing (o quê e quando), retomada (como e quando), tratamento de erros (retries, backoff), observabilidade (o que registrar em log). Estime quantas linhas de código isso levaria para construir e testar corretamente.
- [ ] Amanhã: Esboce uma tarefa hipotética de agente e estime seus requisitos de deployment. Um loop simples mais um arquivo de transcrição seria aceitável para o seu caso de uso, ou você precisaria de durabilidade e observabilidade no nível de framework? Anote a decisão e o raciocínio.

## Para ir além

- [Article: "Building Effective Agents", Anthropic Engineering](https://www.anthropic.com/engineering/building-effective-agents)
- [Recursos](../RESOURCES.md)

---

Não ficou claro? Releia a fonte principal no topo, já que esta lição a comprime e é na compressão que o entendimento escapa. Consulte o [glossário](../GLOSSARY.md) para qualquer termo que pareceu escorregadio.

Se o problema é a lição em si, e não o material, isso é um defeito: [abra uma issue](https://github.com/TokenCemetery/teach/issues).
