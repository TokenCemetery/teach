---
title: "37. Revisando o design de agente de outra pessoa"
description: "Como avaliar um sistema de agente de forma sistemática e como resolver uma afirmação em disputa voltando à fonte primária"
type: lesson
---

# Lição 37. Revisando o design de agente de outra pessoa

**Ligação com a missão:** Ter a confiança para revisar o design de agente de outra pessoa e resolver afirmações em disputa sobre ele consultando as fontes primárias, e não escolhendo um lado por padrão nem dividindo a diferença de forma vaga.
**Fonte principal:** [Article: "Building Effective Agents", Anthropic Engineering](https://www.anthropic.com/engineering/building-effective-agents)
**Pré-requisitos:** [Lição 36](0036-when-not-to-build-an-agent.md)

## Aquecimento

1. ▢ O que o espectro de autonomia da Lição 2 testa para distinguir entre um workflow e um agente?

<details markdown="1"><summary>Verificação</summary>

Se o fluxo de controle é decidido de antemão pelo desenvolvedor, ou decidido em tempo de execução pelo modelo. Não o número de ferramentas, a complexidade ou quantas chamadas ao modelo estão envolvidas, mas quem escolheu o caminho.

</details>

2. ▢ Da Lição 35, qual é uma maneira de um framework reduzir o custo de rodar um agente em produção em comparação com escrever o harness do zero?

<details markdown="1"><summary>Verificação</summary>

Colocar em cache o contexto estável (definições de ferramenta, system prompt) para que tarefas repetidas não reenviem esses tokens, implementar estado durável para que uma execução interrompida possa ser retomada, oferecer tracing e tratamento de erros embutidos que levariam tempo para ligar à mão. O framework compra tempo até a confiabilidade e redução de custo ao preço de flexibilidade ou de lock-in de fornecedor.

</details>

## Saiba isto

### O checklist de revisão: as etapas em ordem

Ao revisar um design de agente proposto ou existente, percorra-o pelas etapas desta trilha em ordem, fazendo a mesma pergunta em cada etapa: esta escolha é justificada, e está documentada?

#### Etapa 1-2: Espectro de autonomia e fluxo de controle

Onde este sistema fica no espectro de autonomia? É um único prompt, um workflow fixado pelo desenvolvedor ou um agente dirigido pelo modelo? Procure a afirmação na proposta ou na documentação. Se a afirmação é apenas "isto é um agente" sem explicar por que a autonomia é necessária, pergunte o que a alternativa de caminho fixo teria custado. Um bom design não apenas nomeia a escolha; ele a defende.

#### Etapa 3-4: Superfície de ferramentas e schema

As ferramentas são nomeadas e descritas de um jeito que o raciocínio de um modelo achará útil? A Lição 8 ensinou que descrições de ferramenta são superfície de prompt, e não documentação de API. Os nomes das ferramentas devem descrever o que a ferramenta faz da perspectiva do modelo, e não o endpoint subjacente. As descrições dos parâmetros devem ajudar o modelo a decidir o que passar, e não apenas documentar o schema técnico. O conjunto de ferramentas é enxuto (evitando o inchaço da Lição 9), ou acumulou ferramentas que raramente são usadas?

#### Etapa 5-6: Estratégia de contexto e memória

Para uma tarefa de longa duração, qual é a estratégia? O design distingue entre scratchpad (a transcrição corrente dentro de um turno) e memória entre execuções (fatos persistidos entre execuções)? A Lição 11 ensinou a compactação; o design tem um plano de como encurtar a transcrição conforme ela cresce? Se a tarefa envolve aprender fatos e levá-los adiante, há um mecanismo de memória nomeado, ou o design está dependendo apenas da transcrição?

#### Etapa 7: Reflexão e retries

Quando um passo falha, o design planeja um retry, e inclui reflexão explícita (o agente raciocinando em linguagem natural sobre por que falhou antes de tentar de novo)? Ou apenas faz loop e espera que o modelo se corrija? A Lição 17 ensinou que silêncio não é aprendizado; um agente bem projetado reflete depois da falha.

#### Etapa 8: Decisão multiagente

Se o design é multiagente, ele justifica essa escolha contra a alternativa de um agente único? A Lição 19 ensinou o custo de coordenação: um sistema orquestrador-worker multiplica tokens e fragmenta o contexto entre os workers. O design deve nomear o benefício específico que justifica esse custo. O benefício é paralelismo (tempo de relógio), isolamento de contexto (a transcrição de cada worker se mantém limpa) ou genuína independência das subtarefas? E esse benefício se aplica a esta tarefa específica?

#### Etapa 14: Segurança e a tríade

O agente lê conteúdo não confiável? Acessa dados privados? Tem comunicação externa? A Lição 31 ensinou que as três condições juntas o tornam explorável. O design deve nomear quais condições estão presentes e quais não estão, ou como o design remove deliberadamente pelo menos uma. Se o design tem as três mas não reconhece isso, é um sinal de alerta.

#### Etapa 15: Custo e durabilidade

Alguém estimou o custo em tokens por tarefa concluída? Esse custo é aceitável? Se o sistema usa um framework, a escolha do framework é justificada, ou foi escolhida por padrão? A Lição 33 ensinou que o custo real por tarefa inclui retries e amplificação de tokens. Um bom design nomeia uma estimativa de custo, mesmo que a estimativa seja aproximada.

### A habilidade específica: resolver uma afirmação em disputa pela fonte primária

Esta trilha apresentou a você dois relatos críveis e opostos sobre sistemas multiagente. A Lição 18 descreveu padrões orquestrador-worker e seus benefícios. A Lição 19 apresentou o argumento da Cognition de que a maioria dos sistemas multiagente não vale o custo e de que um único agente com ferramentas melhores muitas vezes vence.

Os dois relatos estão corretos para seus próprios domínios. Um revisor que tenha apenas lembrado pela metade os dois pode escolher um lado por reflexo ("li que agentes únicos são sempre melhores, então este design multiagente está errado") ou dividir a diferença de forma vaga ("multiagente às vezes é bom"). Nenhum dos dois faz a conversa avançar.

A habilidade de fato é voltar às fontes primárias e conferir se as circunstâncias específicas do design correspondem às condições em que o argumento daquela fonte se sustenta.

O "How We Built Our Multi-Agent Research System", da Anthropic, descreve um sistema multiagente que funcionou. As condições que o fizeram funcionar, pela leitura desse artigo, incluem: as subtarefas eram genuinamente independentes (cada pesquisador focava um ângulo separado), o paralelismo dava um benefício real em tempo de relógio (os resultados precisavam ser sintetizados sob pressão de tempo) e a equipe investiu pesadamente em orquestração para manter a comunicação limpa entre os workers.

O "Don't Build Multi-Agents", da Cognition, argumenta que o custo não vale a pena para a maioria das tarefas. As condições que tornam o argumento deles mais forte incluem: quando as subtarefas compartilham contexto ou se refinam mutuamente, quando você tem tempo e orçamento de contexto para um único agente explorar caminhos em série e quando a sobrecarga de coordenação é alta em relação ao problema.

Agora você está revisando um design. A proposta diz: "Estamos construindo um sistema de pesquisa com um orquestrador e três workers pesquisadores em paralelo." Antes de aceitar ou rejeitar o multiagente, pergunte:

- Os três ângulos de pesquisa são genuinamente independentes, ou compartilham contexto e se refinam mutuamente?
- Existe um prazo real em tempo de relógio, ou você tem tempo para um agente explorar os três ângulos em série?
- A equipe orçou o trabalho de orquestração, ou a coordenação é um detalhe deixado para depois?
- Quanto um único agente com ferramentas mais amplas custaria em tokens em comparação com o sistema multiagente?

As circunstâncias reais do design determinam o argumento de qual fonte se aplica. O trabalho de um revisor não é arbitrar entre as duas fontes, mas rastrear se a situação do design corresponde às condições em que o argumento de uma fonte fica mais forte ou mais fraco. Se o design não tem resposta a essas perguntas, ele ainda não resolveu a questão pela fonte primária; apenas afirmou a escolha.

### O que uma boa revisão de design realiza

Uma boa revisão não diz "isto é bom" nem "isto é ruim". Ela diz:

"Este design escolhe X porque Y. Rastreei essa escolha até a etapa Z da trilha, onde estas perguntas se aplicam. O design responde a estas perguntas com clareza e deixa estas em aberto. Antes de se comprometer, a equipe deve resolver as perguntas em aberto ou documentar os riscos."

Uma revisão que nomeia perguntas específicas sem resposta é mais útil do que uma que dá aprovado ou reprovado. Ela dá à equipe algo para fazer. Também dá a você alavancagem: você pode fazer perguntas de acompanhamento por escrito e cobrar do design afirmações específicas, em vez de apenas expressar ceticismo.

## Prática

1. ▢ Você está revisando um design de um agente que processa documentos financeiros. O design diz que o agente terá acesso a: uma ferramenta para ler documentos do armazenamento em nuvem, uma ferramenta para consultar um banco de dados de clientes em busca do histórico de transações e uma ferramenta para registrar relatórios em um log de auditoria. O design não discute segurança. Usando o arcabouço da Lição 31, que perguntas você deve fazer?

<details markdown="1"><summary>Verificação</summary>

As três condições da tríade letal estão presentes: o agente lê conteúdo não confiável (documentos financeiros enviados), acessa dados privados (histórico de transações dos clientes) e pode comunicar-se com o exterior (registrar relatórios de auditoria). Uma boa revisão pergunta: As três condições da tríade são necessárias? O design pode remover pelo menos uma? Por exemplo, o agente pode ler documentos sem registrar relatórios diretamente, redigindo os relatórios para aprovação humana? Ou pode evitar tocar o banco de dados de clientes trabalhando apenas com dados resumidos? O design deve ou justificar por que as três são necessárias, ou documentar os controles de segurança específicos (portões de aprovação, log de auditoria, sandboxing) que mitigam o risco.

</details>

2. ▢ Um design propõe um orquestrador com dois workers paralelos: um pesquisa produtos concorrentes, o outro pesquisa as necessidades dos clientes. Os workers então reportam as descobertas a uma analista humana que as sintetiza. Você suspeita que a alternativa de agente único poderia ser mais barata. Que pergunta da Lição 19 você deve fazer para testar essa suspeita?

<details markdown="1"><summary>Dica</summary>

Pense no que o orquestrador está fazendo neste design e se há uma tarefa que o agente único não conseguiria fazer tão bem ou tão depressa.

</details>

<details markdown="1"><summary>Verificação</summary>

Estime o custo em tokens: dois agentes workers mais a sobrecarga do orquestrador, comparados com um agente pesquisando os dois ângulos em série. Os dois workers paralelos terminam mais depressa do que um agente em série (benefício do paralelismo)? Ou o agente único, mantendo as duas linhas de pesquisa em uma transcrição, as integra com mais eficácia (benefício de coerência de contexto)? Se os workers terminam mais depressa mas o multiplicador de custo em tokens é alto, e a analista humana não tem restrição de tempo, o agente único vence. Se os pesquisadores precisam de resultados com urgência e o paralelismo economiza horas, o multiagente justifica o custo. O design deveria ter feito esse cálculo; se não fez, você encontrou uma pergunta em aberto.

</details>

3. ▢ Você está revisando a definição de uma ferramenta para um agente. A ferramenta se chama query_customer_database e sua descrição é: "Connect to the customer database and execute any SQL query provided by the user."

    - a) Esta é uma ferramenta bem projetada porque é maximamente flexível
    - b) Esta ferramenta viola o privilégio mínimo; deveria ser redesenhada para executar apenas consultas específicas e pré-autorizadas
    - c) Esta ferramenta é aceitável porque o agente não vai usá-la de forma indevida se o system prompt disser para não fazer isso
    - d) Esta ferramenta é aceitável desde que o agente não tenha capacidade de comunicação externa

<details markdown="1"><summary>Verificação</summary>

**b)** Esta ferramenta viola o privilégio mínimo e deve ser redesenhada. Ela concede ao agente acesso amplo ao banco de dados, o que viola o princípio da Lição 32 de que cada ferramenta deve se restringir exatamente ao que precisa. A opção (a) está errada: flexibilidade para o desenvolvedor não é o mesmo que um bom design de ferramenta. A opção (c) está errada: a Lição 31 ensinou que instruções de prompt não são uma defesa confiável contra a injeção de prompt; a defesa é arquitetural. A opção (d) está errada: remover a comunicação externa quebraria uma condição da tríade, mas a ferramenta ainda teria escopo excessivo em relação ao que um agente realmente precisa. Um design melhor: uma ferramenta chamada get_customer_orders que recebe um customer_id e devolve os pedidos dele, sem nenhum vetor de injeção de SQL.

</details>

4. ▢ Uma equipe está revisando duas propostas para a mesma tarefa. Proposta A: um único agente com acesso a busca na web, execução de código e ferramentas de documentação. Proposta B: um orquestrador com três workers (especialista em busca, especialista em código, especialista em documentação), cada um com uma ferramenta. A equipe leu a Lição 19 e está dividida. Dois engenheiros defendem que a Proposta A é melhor porque "a Cognition diz que agentes únicos vencem". Dois defendem que a Proposta B é melhor porque "o sistema de pesquisa da Anthropic usou multiagente". Pedem que você resolva isso. Qual deve ser o seu primeiro passo?

<details markdown="1"><summary>Verificação</summary>

Voltar às fontes primárias, e não aos resumos lembrados pela metade. Releia os dois artigos e identifique as condições específicas que cada um descreve: quais eram as características da tarefa, o orçamento de contexto, a pressão de tempo e a complexidade de coordenação em cada fonte? Depois examine a Proposta A e a Proposta B contra essas condições. Elas correspondem melhor às condições de agente único ou de multiagente? As próprias propostas descrevem as características da tarefa e justificam sua escolha contra essas condições? Sua revisão deve dizer algo como: "A Proposta B corresponde às condições em que o sistema de pesquisa da Anthropic teve sucesso (subtarefas independentes, prazo em tempo de relógio), se conseguir justificar o custo de coordenação. A Proposta A corresponde ao cenário da Cognition (trabalho de refinamento de contexto, orçamento de tempo aberto), se o menu de ferramentas do agente único for amplo o bastante para evitar a sobrecarga de decisão de ferramenta." O trabalho não é arbitrar entre as fontes, mas aplicar cada uma à tarefa específica.

</details>

## Prática no mundo real

- [ ] Encontre um sistema que você usa ou conhece que se descreve como um agente. Tente mapeá-lo contra o checklist desta lição: onde ele fica no espectro de autonomia? As ferramentas são descritas para o raciocínio do modelo ou como documentação de API? Ele discute segurança? Anote os itens do checklist que o sistema aborda com clareza e quais deixa em silêncio.
- [ ] Escolha uma afirmação da Lição 19 que a Cognition ou a Anthropic faz sobre sistemas multiagente. Releia a fonte e identifique as condições específicas em que essa afirmação se sustenta. Anote: que características da tarefa tornam a afirmação verdadeira ou falsa? Como você testaria essa afirmação em um sistema que está projetando?
- [ ] Amanhã: Revise o design de agente de outra pessoa (do trabalho, de um projeto de código aberto ou de uma proposta técnica). Use o checklist desta lição. Anote uma pergunta em aberto para cada etapa que o design não aborda por completo. Compartilhe a revisão com o autor do design e veja se suas perguntas coincidem com as preocupações dele.

## Para ir além

- [Article: "Building Effective Agents", Anthropic Engineering](https://www.anthropic.com/engineering/building-effective-agents)
- [Recursos](../RESOURCES.md)

---

Não ficou claro? Releia a fonte principal no topo, já que esta lição a comprime e é na compressão que o entendimento escapa. Consulte o [glossário](../GLOSSARY.md) para qualquer termo que pareceu escorregadio.

Se o problema é a lição em si, e não o material, isso é um defeito: [abra uma issue](https://github.com/TokenCemetery/teach/issues).
