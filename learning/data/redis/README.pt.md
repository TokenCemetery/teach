---
title: Redis
description: "Use o Redis pelo que ele é: o modelo de memória, eviction, persistência e os padrões que o usam mal em silêncio"
type: topic
---

# Aprendizado: Redis

Seja capaz de identificar onde um sistema existente está usando mal o Redis em silêncio, como um cache tratado como store ou um lock que não é um lock, e de projetar do zero um uso correto em vez disso.

**Última lição:** [17. ACLs e protected mode](lessons/0017-acls-and-protected-mode.md)

## O sucesso se parece com isto

- Dado o uso do Redis por um sistema existente, identificar se ele trata um cache como store durável, implementa um lock incorretamente ou roda um keyspace sem limite, e dizer o que quebra por causa disso.
- Projetar do zero um uso correto do Redis (keyspace limitado, política de eviction adequada, lock distribuído de verdade) para um novo caso de uso.
- Comparar as garantias de persistência do Redis (RDB/AOF) com a durabilidade apoiada no WAL do Postgres, e dizer quando recorrer ao Redis em vez de um banco de dados é a decisão certa e quando é um antipadrão.
- Raciocinar sobre Redis Cluster/Sentinel no nível das concessões que o clustering introduz, sem precisar operar um.

## Restrições

- Não pressupõe experiência prévia com Redis.

## Fora do escopo

- Operar uma instância do Postgres em produção: veja [`data/postgres`](../../data/postgres/), referenciado para a comparação em vez de repetido.

## O arco

Dez etapas, do eviction ao controle de acesso. Uma etapa leva várias lições e as fronteiras são flexíveis; o que torna uma etapa concluída é a capacidade, não a contagem de lições.

| Etapa | Lições | Cobre | Concluída quando |
|---|---|---|---|
| 1. Memória e eviction | 0001 | Por que o Redis faz eviction de chaves, afinal, e o antipadrão que decorre de esquecer isso | Consegue explicar o efeito de uma política de eviction sobre uma dada carga de trabalho |
| 2. Persistência | 0002 a 0003 | RDB e AOF, e como a durabilidade deles se compara ao WAL do Postgres | Consegue dizer quando recorrer ao Redis em vez de um banco de dados é certo e quando é um antipadrão |
| 3. Locks distribuídos | 0004 a 0005 | Erros de locking ingênuo, Redlock, a crítica de Kleppmann | Consegue projetar, ou rejeitar corretamente, um lock distribuído baseado no Redis |
| 4. Antipadrões de cache contra store | 0006 a 0007 | Cache-aside, um cache tratado como store durável, um keyspace sem limite | Dado um sistema existente, consegue identificar o mau uso e dizer o que quebra |
| 5. Clustering | 0008 | Redis Cluster e Sentinel, as concessões que o clustering introduz | Consegue raciocinar sobre os trade-offs do clustering sem precisar operar um |
| 6. Tipos de dados e o seu modelo de custo | 0009 a 0010 | Strings, hashes, lists, sets, sorted sets, bitmaps, HyperLogLog, e como escolher entre eles | Consegue escolher uma estrutura de dados para um caso de uso declarado e explicar quanto ela custa |
| 7. Mensageria e expiração | 0011 a 0012 | Pub/Sub contra streams, consumer groups comparados aos do Kafka, expiração de chaves lazy contra ativa | Consegue escolher o mecanismo de mensageria certo para um caso de uso e explicar como uma chave de fato sai do Redis |
| 8. Transações e scripting | 0013 a 0014 | `MULTI`/`EXEC`, locking otimista com `WATCH`, scripting em Lua, Redis Functions | Consegue construir uma sequência check-then-act que seja de fato segura, e explicar o que torna atômica a liberação de um lock |
| 9. Desempenho e operação | 0015 a 0016 | Custo de ida e volta, pipelining, connection pooling, `INFO`/`SLOWLOG`/latency monitor/`MEMORY USAGE`, `SCAN` contra `KEYS` | Consegue reduzir o custo de rede de um cliente tagarela e diagnosticar o comportamento real de uma instância sem travá-la |
| 10. Controle de acesso | 0017 | Protected mode, ACLs, categorias de comandos, o usuário padrão | Consegue restringir o que uma conexão não autenticada e um usuário autenticado podem fazer, cada um |

## Lições

Siga estas na ordem.

| # | Lição | Ensina |
|---|---|---|
| [0001](lessons/0001-memory-and-eviction.md) | Memória e eviction | Por que o Redis faz eviction de chaves, afinal, e o antipadrão que decorre de esquecer isso |
| [0002](lessons/0002-rdb-snapshotting.md) | Snapshots RDB | O que um snapshot RDB de fato captura, e a janela de perda de dados que o seu intervalo de gravação deixa aberta |
| [0003](lessons/0003-aof-and-wal-comparison.md) | AOF e a comparação com o WAL | Como a política de fsync do AOF define a sua janela de perda de dados, e por que mesmo a configuração comum mais forte do Redis troca mais durabilidade por velocidade do que o Postgres troca por padrão |
| [0004](lessons/0004-naive-locking-mistakes.md) | Erros de locking ingênuo | Por que SET NX PX sozinho não é um lock distribuído, e os dois modos de falha que o quebram em condições reais |
| [0005](lessons/0005-redlock-and-kleppmanns-critique.md) | Redlock e a crítica de Kleppmann | O que o Redlock de fato corrige no lock ingênuo, o que a crítica de Kleppmann mostra que ele ainda não corrige e como decidir se um lock no Redis é sequer a ferramenta certa |
| [0006](lessons/0006-cache-aside-and-the-store-anti-pattern.md) | Cache-aside e o antipadrão do store | Como é o uso correto do cache-aside, e a forma específica pela qual um cache vira em silêncio o sistema de registro quando esse padrão é ignorado |
| [0007](lessons/0007-unbounded-keyspace-and-spotting-misuse.md) | O antipadrão do keyspace sem limite e como identificar o mau uso | Como um keyspace cresce sem limite quando ninguém define um TTL nem uma política de eviction, e um checklist para identificar isso e o antipadrão do store em um sistema existente |
| [0008](lessons/0008-cluster-and-sentinel.md) | Redis Cluster e Sentinel | As concessões que o sharding do Redis Cluster e o failover automático do Sentinel introduzem, cada um, analisadas sem precisar operar nenhum dos dois |
| [0009](lessons/0009-strings-hashes-and-lists.md) | Strings, hashes e lists | As três estruturas de dados centrais que o Redis de fato armazena, e quanto cada uma custa para ler, escrever e crescer |
| [0010](lessons/0010-sets-sorted-sets-and-probabilistic-structures.md) | Sets, sorted sets e estruturas probabilísticas | Escolher uma estrutura de dados para um caso de uso, da pertinência exata a uma contagem aproximada que quase não custa nada manter |
| [0011](lessons/0011-streams-and-pubsub-as-messaging.md) | Streams e Pub/Sub como superfície de mensageria | Duas formas de o Redis mover mensagens entre clientes, e por que só uma delas é segura para construir uma fila |
| [0012](lessons/0012-key-expiration-lazy-vs-active.md) | Expiração de chaves: lazy contra ativa | Por que o TTL de uma chave chegar a zero não a remove da memória por si só, e os dois mecanismos que acabam removendo |
| [0013](lessons/0013-multi-exec-and-optimistic-locking-with-watch.md) | MULTI/EXEC e locking otimista com WATCH | Enfileirar vários comandos para rodar sem interrupção, e detectar que um valor mudou por baixo de você antes de agir sobre ele |
| [0014](lessons/0014-lua-scripting-and-redis-functions.md) | Scripting em Lua e Redis Functions | O mecanismo que de fato torna segura a liberação de um lock, executando uma verificação e uma ação como um único passo atômico |
| [0015](lessons/0015-pipelining-round-trip-cost-and-connection-pooling.md) | Pipelining, custo de ida e volta e connection pooling | Por que N comandos sequenciais custam N idas e voltas pela rede mesmo que cada um execute em microssegundos, e as duas correções distintas |
| [0016](lessons/0016-operational-visibility.md) | Visibilidade operacional | As ferramentas que mostram o que uma instância do Redis está de fato fazendo, e o único comando que já causou mais indisponibilidades do que quase qualquer outro |
| [0017](lessons/0017-acls-and-protected-mode.md) | ACLs e protected mode | Como o Redis impede que uma instância não autenticada seja sequer alcançável, e delimita o que um cliente autenticado de fato tem permissão para fazer |

## Referência

- [Glossário](GLOSSARY.md): termos canônicos deste tópico
- [Recursos](RESOURCES.md): fontes confiáveis
- [Persistência](reference/persistence.md): o que RDB e AOF prometem cada um, a janela exata de perda que cada política de fsync deixa e o que a própria documentação do Redis diz sobre igualar a durabilidade de um banco de dados
- [Locks distribuídos](reference/distributed-locks.md): o lock ingênuo e os seus dois furos, o algoritmo do Redlock com a aritmética de validade e a única pergunta que decide se algum dos dois é a ferramenta certa
- [Antipadrões de cache contra store](reference/cache-vs-store-anti-patterns.md): cache-aside feito corretamente, as duas formas pelas quais um cache deixa de ser um cache e as configurações de eviction que decidem qual falha você recebe
- [Clustering](reference/clustering.md): o que os slots do Cluster tiram de você, as configurações que decidem se um cluster degradado serve ou para, e por que o quórum do Sentinel não controla o failover

## Como isto funciona

Cada lição é curta e autocontida. Os gabaritos ficam recolhidos: primeiro lembre, depois abra. A prática no mundo real importa mais do que a leitura, e espaçá-la é o ponto. Tudo o que ainda estiver confuso no fim de uma lição vale ser perseguido até a fonte primária antes de seguir adiante.
