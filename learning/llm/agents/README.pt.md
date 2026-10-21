---
title: Agentes de LLM
description: "Construa o loop você mesmo: ferramentas, contexto, memória e saber quando um agente é a resposta errada"
type: topic
---

# Aprendizado: Agentes de LLM

Seja capaz de construir você mesmo um loop de agente, de decidir se uma dada tarefa precisa de um agente ou de um workflow fixo e de diagnosticar um agente que falha a partir da trajetória dele, em vez de acrescentar mais uma instrução ao prompt.

**Última lição:** [0037. Revisando o design de agente de outra pessoa](lessons/0037-reviewing-someone-elses-agent-design.md)

## O sucesso se parece com isto

- Escrever o loop de agente para uma tarefa dada e nomear o que cada mensagem do contexto está fazendo e o que encerra o loop.
- Escolher entre um único prompt, um workflow fixo e um agente para uma dada tarefa, e defender a escolha contra o custo da opção rejeitada.
- Projetar a superfície de ferramentas de um agente: nomes, descrições, formatos de retorno e a fronteira de permissão que decide o que ele pode fazer sem supervisão.
- Diagnosticar um agente que falha a partir da trajetória, nomeando a causa (um loop, contexto envenenado, uma ferramenta mal especificada, uma condição de parada errada) em vez de refazer o prompt ao acaso.
- Explicar por que um agente que lê conteúdo não confiável não pode ser protegido apenas por instruções no prompt, e projetar a fronteira que de fato se sustenta.
- Orçar o custo em tokens e a latência de um loop agêntico e dizer de qual parte do loop vem a amplificação.

## Restrições

- Neutro quanto a provedor. Loops, schemas de ferramentas e fluxo de controle são dados em pseudocódigo parecido com Python, para que o material sobreviva à rotatividade das APIs de chamada de ferramentas que torna obsoleta a maior parte do que se escreve sobre agentes.
- Os formatos na rede são a exceção, porque o aspecto de uma mensagem de chamada de ferramenta na rede é um fato, e não um algoritmo. Um par real e capturado de requisição e resposta é mostrado, e um segundo provedor aparece apenas como a diferença em relação a ele.
- Nenhum framework é pressuposto nem ensinado. O que um framework oferece (estado durável, fluxo de controle em grafo, retomada) é coberto uma vez, perto do fim, como uma decisão e não como um tutorial.
- As práticas são mais de inspeção do que de construção: ler um trace real, um schema de ferramenta real, um manifesto real de servidor MCP e marcar a fronteira de permissão de um agente que já está em execução.
- Pressupõe familiaridade com o que é um modelo de linguagem e conforto para ler código parecido com Python. Não exige experiência prévia na construção de agentes.

## Fora do escopo

- Avaliação como disciplina: veja [`llm/evals`](../../llm/evals/) (a lição 0013 cobre trajetórias, sucesso da tarefa contra acurácia por passo e `pass^k`). Aqui entra só como a única capacidade de que quem constrói agentes precisa, com um link em vez de uma repetição.
- Internos do pipeline de recuperação: veja [`llm/rag`](../../llm/rag/). A recuperação aparece aqui como uma ferramenta que o agente chama, e não como chunking, embedding e reranking.
- Internos de serving e inferência: veja [`llm/inference`](../../llm/inference/) para latência, batching e decodificação restrita.
- Treinar um modelo para usar ferramentas: veja [`llm/finetuning`](../../llm/finetuning/).
- Retries, idempotência e falha parcial como problemas de sistemas distribuídos: veja [`architecture/distributed-systems`](../../architecture/distributed-systems/). Cobertos aqui apenas pelo que faz uma chamada de ferramenta diferir de uma chamada remota comum.
- Prompting como assunto (instruções, exemplos, raciocínio, saída estruturada, templates e medir uma mudança de prompt): veja [`llm/prompting`](../../llm/prompting/). Esta trilha mantém as descrições de ferramentas, a injeção com ferramentas e o caching sob concorrência, e aponta para lá para prompting em geral.

## O arco

Dezesseis etapas, de nenhum conhecimento prévio até o julgamento sênior. Não é uma lista de lições: uma etapa leva várias lições e as fronteiras são flexíveis.

| Etapa | Lições | Cobre | Concluída quando |
| --- | --- | --- | --- |
| 1. O que é um agente | 0001 a 0002 | O loop, agente contra workflow contra chain, o espectro de autonomia | Consegue classificar um sistema e dizer se "agente" é a palavra certa para ele |
| 2. Mecânica de chamada de ferramentas | 0003 a 0005 | O formato na rede de uma chamada de ferramenta, schemas de parâmetros, quem executa o quê, chamadas paralelas, erros devolvidos como resultados | Consegue ler uma troca bruta de chamada de ferramenta e dizer o que cada mensagem fez |
| 3. O loop do zero | 0006 a 0007 | Escrever o loop, condições de parada, a transcrição como todo o estado do agente | Consegue escrever um loop de agente e defender onde ele para |
| 4. Design de ferramentas como prompt engineering | 0008 a 0009 | Nomes e descrições como superfície de prompt, formatos de retorno, custo em tokens dos resultados, inchaço do conjunto de ferramentas | Consegue projetar uma superfície de ferramentas e dizer por que cada descrição está redigida como está |
| 5. Gerenciamento de contexto | 0010 a 0012 | A janela como o orçamento central: truncamento, compactação, recuperação sob demanda, subagentes como isolamento de contexto | Consegue planejar o que sai do contexto, e quando, em uma tarefa de longa duração |
| 6. Memória e estado | 0013 a 0014 | Scratchpad dentro da execução contra memória entre execuções, arquivos como memória, por que recuperação não é memória | Consegue escolher onde um dado fato vive e dizer o que acontece quando a execução termina |
| 7. Planejamento e reflexão | 0015 a 0017 | ReAct, plan-then-execute, autocrítica, decomposição, o que os modelos de raciocínio mudaram | Consegue escolher um padrão de planejamento para uma tarefa e nomear o que ele custa em tokens e latência |
| 8. Multiagente | 0018 a 0019 | Orquestrador e worker, handoff, fan-out, custo de coordenação, quando um agente com ferramentas melhores vence | Consegue dizer se um segundo agente compra algo que o primeiro não poderia ter recebido |
| 9. Protocolos e interoperabilidade | 0020 a 0021 | Ferramentas, recursos, prompts e transportes do MCP, formatos de function calling dos provedores, descoberta de ferramentas em escala | Consegue ler o manifesto de um servidor MCP e dizer o que ele expõe e o que não padroniza |
| 10. Ambientes de execução | 0022 a 0023 | Sandboxing, execução de código como ferramenta, acesso ao sistema de arquivos, portões de aprovação com humano no loop | Consegue posicionar a fronteira do sandbox para um conjunto declarado de ferramentas |
| 11. Computer use e agentes de navegador | 0024 a 0026 | Screenshots como observações, grounding de uma ação em uma coordenada, o problema da confiabilidade | Consegue dizer por que um agente que dirige a tela falha de forma diferente de um que chama ferramentas |
| 12. Modos de falha e observabilidade | 0027 a 0029 | Loops, envenenamento de contexto, erros de ferramenta em cascata, argumentos alucinados, tracing e replay de trajetória | Dada uma trajetória, consegue nomear o passo culpado em vez de refazer o prompt |
| 13. Avaliando um agente | 0030 a 0030 | Resultado contra trajetória, confiabilidade com tentativas repetidas, o que os benchmarks de agentes realmente medem | Consegue dizer o que medir para um dado agente e entregar o resto a `llm/evals` |
| 14. Segurança | 0031 a 0032 | Injeção de prompt como o problema definidor dos agentes, a tríade letal, privilégio mínimo, o confused deputy, a cadeia de suprimentos do MCP | Consegue projetar uma fronteira de permissão que se sustenta quando o agente lê conteúdo hostil |
| 15. Produção, custo e o que os frameworks oferecem | 0033 a 0035 | Amplificação de tokens, prompt caching, concorrência, durabilidade e retomabilidade, custo por tarefa concluída | Consegue orçar o custo de um loop e dizer qual garantia de framework um deployment realmente precisa |
| 16. Julgamento | 0036 a 0037 | Quando não construir um agente, revisar o design de agente de outra pessoa e nomear o que uma escolha custa, resolver uma afirmação em disputa pela fonte primária | Tem a confiança para tomar a decisão e explicá-la a outra pessoa |

## Lições

Siga estas na ordem.

| # | Lição | Ensina |
|---|---|---|
| [0001](lessons/0001-the-agent-loop.md) | O loop do agente | O que faz de um sistema um agente e o ciclo de quatro passos que roda por baixo de um |
| [0002](lessons/0002-agent-workflow-or-prompt.md) | Agente, workflow ou apenas um prompt | Onde uma tarefa fica no espectro de autonomia e como defender a escolha |
| [0003](lessons/0003-the-wire-format-of-a-tool-call.md) | O formato na rede de uma chamada de ferramenta | Como uma chamada de ferramenta e seu resultado realmente aparecem no protocolo entre o seu harness e o provedor do modelo |
| [0004](lessons/0004-schemas-and-who-executes.md) | Schemas de parâmetros e quem executa o quê | Como schemas JSON restringem o que um modelo pode enviar e a diferença entre ferramentas de cliente e de servidor |
| [0005](lessons/0005-parallel-calls-and-errors-as-results.md) | Chamadas paralelas e erros como resultados | Como um modelo pode pedir várias ferramentas de uma vez e por que erros de ferramenta são resultados, e não exceções |
| [0006](lessons/0006-writing-the-loop.md) | Escrevendo o loop | Construir o loop do agente a partir de pseudocódigo e escolher as condições de parada de propósito |
| [0007](lessons/0007-the-transcript-as-state.md) | A transcrição como estado | Entender que a transcrição é a única memória persistente do agente entre turnos |
| [0008](lessons/0008-naming-and-describing-a-tool.md) | Nomeando e descrevendo uma ferramenta | O nome e a descrição de uma ferramenta são o que o modelo lê para decidir quando e como chamá-la |
| [0009](lessons/0009-return-shapes-and-tool-set-bloat.md) | Formatos de retorno e inchaço do conjunto de ferramentas | O valor de retorno de uma ferramenta custa orçamento de contexto, e ferramentas demais prejudicam a capacidade do modelo de escolher corretamente |
| [0010](lessons/0010-the-context-window-as-budget.md) | A janela de contexto como orçamento | A janela de contexto é um recurso finito que o harness cura ativamente ao longo do tempo, e não um log inerte |
| [0011](lessons/0011-compaction-and-retrieval-on-demand.md) | Compactação e recuperação sob demanda | Duas estratégias para manter o contexto de um agente de longa duração dentro do orçamento preservando o que ainda importa |
| [0012](lessons/0012-sub-agents-as-context-isolation.md) | Subagentes como isolamento de contexto | Iniciar um subagente isola o trabalho exploratório longo do orçamento de contexto do pai |
| [0013](lessons/0013-scratchpad-versus-memory.md) | Scratchpad contra memória | A diferença entre as notas que um agente mantém durante uma execução e os fatos de que precisa entre várias execuções |
| [0014](lessons/0014-files-as-memory.md) | Arquivos como memória | Usar arquivos duráveis como a forma mais simples de memória entre execuções para agentes |
| [0015](lessons/0015-react-interleaving-reasoning-and-acting.md) | ReAct: intercalando raciocínio e ação | O padrão de juntar passos curtos de raciocínio a cada ação, para que o modelo possa observar e se adaptar |
| [0016](lessons/0016-plan-then-execute-and-decomposition.md) | Plan-then-execute e decomposição | O planejamento explícito de antemão como alternativa ao ReAct, quando usá-lo e como lidar com o replanejamento |
| [0017](lessons/0017-self-critique-and-reasoning-models.md) | Autocrítica e o que os modelos de raciocínio mudaram | O loop de reflexão como uma etapa explícita, seus custos e como o raciocínio interno estendido afeta quando usá-lo |
| [0018](lessons/0018-orchestrator-and-worker.md) | Orquestrador e worker | Projetar um sistema multiagente em que um agente planeja e delega e os workers executam em paralelo |
| [0019](lessons/0019-coordination-cost.md) | Custo de coordenação | Entender por que construir vários agentes é mais caro do que um único agente bem equipado e como decidir quando o ganho de paralelismo compensa o custo |
| [0020](lessons/0020-mcp-tools-resources-and-prompts.md) | MCP: ferramentas, recursos e prompts | O Model Context Protocol como uma interface padronizada para harnesses de agente descobrirem e invocarem ferramentas externas, lerem dados e usarem templates |
| [0021](lessons/0021-provider-formats-and-discovery-at-scale.md) | Formatos de provedor e descoberta de ferramentas em escala | Como o MCP e os formatos de rede específicos de provedor são camadas separadas e por que carregar toda ferramenta no contexto não escala para muitos servidores conectados |
| [0022](lessons/0022-sandboxing-and-approval-gates.md) | Sandboxing e portões de aprovação | Fronteiras de execução e pontos de verificação humanos que protegem contra erros do modelo |
| [0023](lessons/0023-code-execution-as-a-tool.md) | Execução de código como ferramenta | Dar a um agente uma única ferramenta de execução de código em sandbox em vez de muitas ferramentas individuais e estreitas |
| [0024](lessons/0024-screenshots-as-observations.md) | Screenshots como observações | Como agentes de computer use observam a tela como imagem e não como dados estruturados, e por que a estrutura do loop continua valendo |
| [0025](lessons/0025-grounding-an-action-to-a-coordinate.md) | Grounding de uma ação em uma coordenada | Por que traduzir uma intenção visual em uma coordenada de pixel é mais difícil e mais frágil do que um argumento tipado de chamada de ferramenta |
| [0026](lessons/0026-why-browser-agents-fail-differently.md) | Por que agentes de navegador falham de forma diferente | Agentes que dirigem a tela falham de maneiras que os agentes que chamam ferramentas não falham, e por que o WebArena criou um benchmark para medir e estudar essas falhas |
| [0027](lessons/0027-loops-and-context-poisoning.md) | Loops e envenenamento de contexto | Dois modos de falha visíveis em uma trajetória, loops repetitivos e envenenamento silencioso de contexto, e como reconhecer cada um |
| [0028](lessons/0028-cascading-tool-errors.md) | Erros de ferramenta em cascata e argumentos alucinados | Um erro de ferramenta levando a decisões erradas, entrando em espiral de confusão, e argumentos bem tipados mas falsos que schemas não conseguem pegar |
| [0029](lessons/0029-tracing-and-trajectory-replay.md) | Tracing e replay de trajetória | Usar convenções de trace neutras quanto a fornecedor para capturar execuções de agente e reproduzir trajetórias para percorrer falhas passo a passo |
| [0030](lessons/0030-evaluating-an-agent.md) | Avaliando um agente | Medir o sucesso do agente no nível do resultado contra o nível da trajetória, e por que uma única execução bem-sucedida não significa que o agente é confiável |
| [0031](lessons/0031-prompt-injection-and-the-lethal-trifecta.md) | Injeção de prompt e a tríade letal | Como agentes que leem conteúdo não confiável se tornam exploráveis e por que só o prompting não os protege |
| [0032](lessons/0032-least-privilege-and-the-confused-deputy.md) | Privilégio mínimo e o confused deputy | Como restringir as capacidades do agente para que a injeção de prompt cause dano contido em vez de uma brecha catastrófica |
| [0033](lessons/0033-token-amplification-and-cost.md) | Amplificação de tokens e custo por tarefa concluída | Por que sistemas agênticos consomem muito mais tokens por tarefa concluída do que um único prompt consumiria, e como orçar isso |
| [0034](lessons/0034-prompt-caching-and-concurrency.md) | Prompt caching e concorrência | Como o caching reduz o custo em tokens por tarefa e como a concorrência aumenta o throughput, e por que confundir os dois é um erro de orçamento |
| [0035](lessons/0035-durability-and-what-frameworks-buy.md) | Durabilidade e o que um framework oferece | A execução durável e retomável de agentes como problema de engenharia, o que os frameworks oferecem concretamente e um princípio de decisão para adotar um |
| [0036](lessons/0036-when-not-to-build-an-agent.md) | Quando não construir um agente | O julgamento para decidir se uma tarefa realmente precisa de um agente e a disciplina de dizer não quando ele não vale o custo |
| [0037](lessons/0037-reviewing-someone-elses-agent-design.md) | Revisando o design de agente de outra pessoa | Como avaliar um sistema de agente de forma sistemática e como resolver uma afirmação em disputa voltando à fonte primária |

## Referência

- [Glossário](GLOSSARY.md): termos canônicos deste tópico
- [Recursos](RESOURCES.md): fontes confiáveis

## Como isto funciona

Cada lição é curta e autocontida. Os gabaritos ficam recolhidos: primeiro lembre, depois abra. A prática no mundo real importa mais do que a leitura, e espaçá-la é o ponto. Tudo o que ainda estiver confuso no fim de uma lição vale ser perseguido até a fonte primária antes de seguir adiante.
