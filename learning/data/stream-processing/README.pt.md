---
title: Stream Processing
description: "Processe um stream com o Kafka Streams: topologias, estado, janelas e joins, e quanto uma topologia custa antes de chegar à produção"
type: topic
---

# Aprendizado: Processamento de Streams

Seja capaz de construir, testar e executar uma aplicação Kafka Streams que dê a resposta certa quando os registros chegam atrasados, fora de ordem ou duas vezes, e de dizer, a partir da sua topologia, quais tópicos internos, qual estado e qual tempo de recuperação ela vai custar antes de chegar à produção.

**Última lição:** [20. Mudando uma topologia da qual outros dependem](lessons/0020-changing-a-topology-others-depend-on.md)

## O sucesso se parece com isto

- Explicar, a partir da dualidade stream-tabela, como um tópico, um changelog e uma KTable se relacionam, e prever o que uma topologia emite para uma entrada declarada.
- Construir uma topologia com a DSL, ler a saída de `describe()` e nomear cada tópico interno que ela cria, e por quê.
- Escolher um state store para uma operação com estado e dizer como o seu estado é reconstruído quando a instância que o mantém morre.
- Escolher uma janela e um período de carência para uma pergunta baseada em tempo, e dizer quais registros atrasados ela descarta e quando emite um resultado.
- Escolher um join para duas entradas, torná-las co-particionadas ou dizer por que uma GlobalKTable dispensa essa necessidade, e prever a saída do join.
- Dizer o que `exactly_once_v2` garante e o que deixa de fora, e dimensionar as tarefas, as threads, as instâncias e as réplicas standby de uma aplicação para um tempo de recuperação declarado.
- Testar uma topologia com `TopologyTestDriver` e operar uma aplicação em execução a partir das suas métricas, dos seus estados e dos seus handlers de exceção.
- Decidir entre Kafka Streams, um consumidor simples, Flink e ksqlDB para uma carga de trabalho, revisar a topologia de outra pessoa e mudar uma topologia em execução sem quebrar o seu estado nem os seus consumidores downstream.

## Restrições

- Pressupõe Java funcional e o log como [`data/kafka`](../../data/kafka/) o ensina: partições, consumer groups, garantias de entrega, retenção e compaction. Estas lições apontam para lá em vez de derivar qualquer parte disso de novo.
- Kafka Streams é o único engine ensinado. Os exemplos usam a DSL Java e a Processor API do Apache Kafka 4.3.
- Padrões e protocolos mudam entre versões. Onde uma lição cita um deles, ela nomeia a página de documentação ou o KIP de onde ele veio, e o leitor deve conferir essa página para saber o valor atual.

## Fora do escopo

- O próprio log: partições, consumer groups, semântica de entrega, o custo das transações, retenção e compaction, Kafka Connect e Schema Registry. Veja [`data/kafka`](../../data/kafka/), sobre o qual esta trilha se apoia.
- Falha parcial e consistência como teoria: veja [`architecture/distributed-systems`](../../architecture/distributed-systems/). Esta trilha ensina apenas o que a recuperação de state stores e o rebalanceamento mudam para uma aplicação Streams.
- Apache Flink, Spark Structured Streaming e ksqlDB como assuntos. A etapa 8 os compara com o Kafka Streams como candidatos para uma carga de trabalho; ela não ensina a executá-los.
- A linguagem Java: veja [`programming/java`](../../programming/java/).
- Carregar um stream em um data warehouse analítico: veja [`data/warehouses`](../../data/warehouses/).

## O arco

Oito etapas, da dualidade stream-tabela ao julgamento. Uma etapa leva várias lições e as fronteiras são flexíveis; o que torna uma etapa concluída é a capacidade, não a contagem de lições.

| Etapa | Lições | Cobre | Concluída quando |
|---|---|---|---|
| 1. Streams e tabelas | 0001 a 0002 | A dualidade stream-tabela, tópicos compactados como tabelas, o que uma aplicação Streams executa e onde | Consegue dizer se um tópico é lido como stream ou como tabela, e o que uma aplicação Streams acrescenta a um consumidor |
| 2. Topologias | 0003 a 0004 | A DSL, sources, processors e sinks, `describe()`, Serdes, operações sem estado, mudanças de chave e tópicos de reparticionamento | Consegue ler uma topologia e nomear cada tópico interno que ela cria |
| 3. Estado | 0005 a 0007 | State stores, tópicos de changelog, agregações, atualizações de KTable, o cache de registros, a Processor API e os punctuators | Consegue escolher um store para uma etapa com estado e dizer como o seu estado sobrevive à morte de uma instância |
| 4. Tempo e janelas | 0008 a 0010 | Tempo do evento, tempo de processamento e stream time, extratores de timestamp, janelas tumbling, hopping, sliding e de sessão, períodos de carência, supressão | Consegue escolher uma janela e um período de carência para uma pergunta e dizer quais registros ela descarta |
| 5. Joins | 0011 a 0012 | Joins stream-tabela e com GlobalKTable, co-particionamento, joins stream-stream com janela, joins tabela-tabela e por chave estrangeira | Consegue escolher um join para duas entradas e prever o que ele emite |
| 6. Garantias e escala | 0013 a 0015 | `exactly_once_v2`, tarefas, threads e instâncias, rebalanceamento, restauração de estado, réplicas standby e warmup, o protocolo de rebalanceamento streams | Consegue dizer o que o exactly-once cobre e dimensionar uma aplicação para um tempo de recuperação declarado |
| 7. Testes e operação | 0016 a 0017 | `TopologyTestDriver`, métricas, estados do cliente e das threads, handlers de exceção, interactive queries, as ferramentas de operação | Consegue testar uma topologia sem um broker e dizer pelas métricas se uma aplicação em execução está saudável |
| 8. Julgamento | 0018 a 0020 | Streams contra um consumidor simples, Flink e ksqlDB, revisar uma topologia, mudar uma topologia da qual outros dependem, resolver uma disputa pela fonte | Tem a confiança para tomar a decisão e explicá-la a outra pessoa |

## Lições

Siga estas na ordem.

| # | Lição | Ensina |
|---|---|---|
| [0001](lessons/0001-streams-and-tables.md) | Streams e tabelas | Por que um stream de mudanças e uma tabela de valores atuais são duas visões dos mesmos dados, e como um tópico guarda qualquer um dos dois |
| [0002](lessons/0002-a-streams-app-is-a-library.md) | Uma aplicação Streams é uma biblioteca | O que roda quando uma aplicação Kafka Streams inicia: consumidores, produtores e estado local dentro do seu próprio processo, sem um cluster próprio |
| [0003](lessons/0003-the-dsl-and-topologies.md) | A DSL e as topologias | Como as chamadas da DSL constroem uma topologia de sources, processors e sinks, e como lê-la a partir de `describe()` |
| [0004](lessons/0004-stateless-operations-and-repartitioning.md) | Operações sem estado e reparticionamento | Quais operações transformam um registro por vez, e qual mudança de chave faz a próxima etapa com estado escrever um tópico de reparticionamento |
| [0005](lessons/0005-state-stores-and-changelog-topics.md) | State stores e tópicos de changelog | Onde uma operação com estado guarda o seu estado, e como um tópico de changelog compactado permite que outra instância o reconstrua |
| [0006](lessons/0006-aggregations-ktables-and-the-record-cache.md) | Agregações, KTables e o cache de registros | Por que uma KTable emite um stream de atualizações em vez de respostas finais, e como o cache de registros e o intervalo de commit decidem quantas |
| [0007](lessons/0007-the-processor-api.md) | A Processor API | Quando descer abaixo da DSL para um processor próprio, com o seu próprio store e punctuator, e pelo que você passa a responder |
| [0008](lessons/0008-event-time-processing-time-and-stream-time.md) | Tempo do evento, tempo de processamento e stream time | Qual relógio uma operação Streams segue, de onde vem o timestamp de um registro e por que o stream time só anda para a frente |
| [0009](lessons/0009-windowed-aggregations.md) | Agregações com janelas | Como as janelas tumbling, hopping, sliding e de sessão agrupam registros por tempo, e qual pergunta cada uma responde |
| [0010](lessons/0010-late-data-grace-periods-and-suppression.md) | Dados atrasados, períodos de carência e supressão | Por quanto tempo uma janela aceita registros fora de ordem, o que acontece com os que chegam depois e como emitir apenas um resultado final |
| [0011](lessons/0011-stream-table-joins-and-co-partitioning.md) | Joins stream-tabela e co-particionamento | Como um stream enriquece cada registro a partir de uma tabela, por que os dois lados precisam estar co-particionados e quando uma GlobalKTable elimina essa necessidade |
| [0012](lessons/0012-stream-stream-and-table-table-joins.md) | Joins stream-stream e tabela-tabela | Como um join com janela emparelha eventos de dois streams, e como os joins de tabelas, incluindo os joins por chave estrangeira, mantêm um resultado atualizado |
| [0013](lessons/0013-exactly-once-in-kafka-streams.md) | Exactly-once no Kafka Streams | O que `exactly_once_v2` torna atômico entre leituras, estado e escritas, e quais efeitos colaterais ele não consegue cobrir |
| [0014](lessons/0014-tasks-threads-and-scaling-out.md) | Tarefas, threads e escala horizontal | Como partições viram tarefas, como as tarefas se distribuem entre threads e instâncias e o que limita o paralelismo de uma aplicação |
| [0015](lessons/0015-rebalancing-restoration-and-standby-replicas.md) | Rebalanceamento, restauração e réplicas standby | O que acontece com o estado quando uma tarefa se move, e como as réplicas standby e warmup encurtam o tempo em que ele fica indisponível |
| [0016](lessons/0016-testing-with-topologytestdriver.md) | Testando com TopologyTestDriver | Como testar a saída, o estado e o comportamento no tempo de uma topologia em um teste unitário sem broker |
| [0017](lessons/0017-operating-and-monitoring-a-streams-app.md) | Operando e monitorando uma aplicação Streams | As métricas, os estados e os handlers de exceção que dizem se uma aplicação em execução está saudável, e o que fazer quando não está |
| [0018](lessons/0018-when-kafka-streams-is-the-wrong-tool.md) | Quando o Kafka Streams é a ferramenta errada | Quando um consumidor simples, o Flink ou o ksqlDB se encaixam melhor em uma carga de trabalho do que uma aplicação Streams, e como defender a decisão |
| [0019](lessons/0019-reviewing-someone-elses-topology.md) | Revisando a topologia de outra pessoa | Como revisar uma topologia Streams e nomear o que cada escolha custa em tópicos internos, estado e corretude |
| [0020](lessons/0020-changing-a-topology-others-depend-on.md) | Mudando uma topologia da qual outros dependem | Como mudar a topologia de uma aplicação em execução sem corromper o seu estado nem quebrar os consumidores downstream, e como resolver uma afirmação contestada pela fonte |

## Referência

- [Glossário](GLOSSARY.md): termos canônicos deste tópico
- [Recursos](RESOURCES.md): fontes confiáveis, cada uma anotada com o que cobre
- [Operações da DSL](reference/dsl-operations.md): cada operação da DSL por tipo de entrada e de saída, se ela mantém estado e se ela reparticiona
- [State stores](reference/state-stores.md): tipos de store, configurações de changelog, o cache de registros e como o estado é restaurado
- [Tempo e janelas](reference/time-and-windows.md): os três relógios, os quatro tipos de janela, os períodos de carência e quando cada um emite
- [Joins](reference/joins.md): a matriz de joins, com janelas, co-particionamento e o que cada join emite
- [Configuração](reference/configuration.md): as configurações que decidem garantias, latência, paralelismo e recuperação, com os seus valores padrão
- [Operação](reference/operations.md): as métricas a observar, os estados do cliente e das threads, os handlers de exceção e as ferramentas de operação
- [Revisão de topologia](reference/topology-review.md): um checklist para revisar uma topologia, a decisão de ferramenta e as mudanças de topologia seguras e inseguras

## Como isto funciona

Cada lição é curta e autocontida. Os gabaritos ficam recolhidos: primeiro lembre, depois abra. A prática no mundo real importa mais do que a leitura, e espaçá-la é o ponto. Tudo o que ainda estiver confuso no fim de uma lição vale ser perseguido até a fonte primária antes de seguir adiante.
