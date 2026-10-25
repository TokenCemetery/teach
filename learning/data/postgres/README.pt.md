---
title: Postgres
description: "Opere o Postgres: o WAL, vacuum e bloat, replicação e quanto custa manter um índice"
type: topic
---

# Aprendizado: Postgres

Seja capaz de operar uma instância do Postgres em execução, auto-hospedada ou gerenciada, e de diagnosticar bloat, atraso de replicação ou um failover que demora a se recuperar em vez de chutar uma correção, além de projetar desde o início o armazenamento, a replicação e a manutenção de índices para um novo deployment.

**Última lição:** [18. Particionamento e TOAST](lessons/0018-partitioning-and-toast.md)

## O sucesso se parece com isto

- Dada uma tabela com bloat ou uma réplica atrasada, diagnosticar a causa a partir da mecânica do WAL, do autovacuum e da replicação, e não por tentativa e erro.
- Projetar o armazenamento, a topologia de replicação e a manutenção de índices para um novo deployment e defender cada escolha.
- Explicar do que um serviço gerenciado (no estilo RDS) protege você e do que não protege, em comparação com operar a instância você mesmo.
- Contabilizar quanto custa ao banco de dados manter um índice vetorial (pgvector), em conexão com a escolha do pgvector como store em `llm/rag`.

## Restrições

- Pressupõe familiaridade básica com SQL (veja `programming/sql` para a linguagem em si); não exige experiência prévia em administração de banco de dados.
- Cobre tanto a operação auto-hospedada quanto o que muda em um serviço gerenciado.

## Fora do escopo

- Consultas, planos de consulta, design de schema e semântica de isolamento: veja [`programming/sql`](../../programming/sql/), referenciado em vez de repetido. Esta trilha é dona da instância em execução, não da linguagem.
- Cargas analíticas em um data warehouse colunar, e quando ele deve assumi-las no lugar do Postgres: veja [`data/warehouses`](../../data/warehouses/), cuja etapa de julgamento toma essa decisão.

## O arco

Doze etapas, da durabilidade à manutenção em nível de tabela em escala. Uma etapa leva várias lições e as fronteiras são flexíveis; o que torna uma etapa concluída é a capacidade, não a contagem de lições.

| Etapa | Lições | Cobre | Concluída quando |
|---|---|---|---|
| 1. O write-ahead log | 0001 | O mecanismo de durabilidade sobre o qual todo o resto desta trilha é construído | Consegue explicar como o WAL torna um crash recuperável |
| 2. Vacuum e bloat | 0002 a 0003 | Internos do autovacuum, MVCC e dead tuples, diagnóstico e ajuste de bloat | Consegue diagnosticar uma tabela com bloat a partir da mecânica do vacuum e do WAL |
| 3. Replicação | 0004 a 0006 | Streaming replication, replication slots, failover, diagnóstico de atraso | Consegue diagnosticar uma réplica atrasada e projetar uma topologia de replicação |
| 4. Índices e o custo de mantê-los | 0007 a 0008 | Custo de manutenção de B-tree/GiST/GIN, quanto custa manter um índice pgvector | Consegue projetar um plano de manutenção de índices e contabilizar o custo do pgvector |
| 5. Gerenciado contra auto-hospedado | 0009 a 0010 | Do que um serviço gerenciado no estilo RDS protege você, e do que não protege | Consegue explicar a fronteira do serviço gerenciado e defender uma escolha de operação |
| 6. Backup e point-in-time recovery | 0011 | Base backups, arquivamento contínuo do WAL, `recovery_target_time` e por que um restore não testado não é um backup verificado | Consegue projetar e defender uma estratégia de backup que de fato reconstrói um banco de dados funcional quando testada |
| 7. Configuração e ajuste de memória | 0012 | `shared_buffers`, `work_mem`, `maintenance_work_mem`, ajuste de checkpoints | Consegue dimensionar essas configurações contra a concorrência real em vez de um teste isolado de uma única consulta |
| 8. Monitoramento | 0013 | `pg_stat_activity`, wait events, `pg_stat_statements`, o log do servidor | Consegue escolher a superfície de monitoramento certa (estado ao vivo dos backends, custo agregado das consultas ou um evento registrado em log) para um dado sintoma |
| 9. Gerenciamento de conexões | 0014 | `max_connections`, o custo de um processo por conexão, os modos de pooling session/transaction/statement do PgBouncer | Consegue escolher um modo de pooling que corresponda ao que a aplicação de fato depende, em vez de adotar por padrão o mais eficiente |
| 10. Replicação lógica e upgrades de versão principal | 0015 a 0016 | Publications e subscriptions, a restrição de DDL da replicação lógica, os modos de transferência do `pg_upgrade`, o caminho de upgrade com pouco downtime via replicação lógica | Consegue escolher e defender um caminho de upgrade (`pg_upgrade` in-place ou cutover por replicação lógica) para um orçamento de downtime declarado |
| 11. Roles, privilégios e row-level security | 0017 | Roles contra a divisão entre usuário e grupo que outros sistemas fazem, as opções INHERIT/SET da associação, GRANTs em nível de tabela, row-level security e o seu bypass padrão para o dono | Consegue projetar um layout de roles e de políticas de RLS e dizer por que habilitar o RLS sozinho não restringe o dono da tabela |
| 12. Particionamento e TOAST | 0018 | Particionamento por range/list/hash, partition pruning, exclusão em massa sem bloat, TOAST e as suas quatro estratégias de armazenamento | Consegue projetar um layout de partições para gerenciar o ciclo de vida sem bloat e contabilizar a estratégia de armazenamento de uma coluna grande |

## Lições

Siga estas na ordem.

| # | Lição | Ensina |
|---|---|---|
| [0001](lessons/0001-the-write-ahead-log.md) | O write-ahead log | O mecanismo de durabilidade sobre o qual todo o resto desta trilha é construído |
| [0002](lessons/0002-mvcc-and-dead-tuples.md) | MVCC e dead tuples | Por que um UPDATE ou DELETE nunca remove nada imediatamente, e por que isso deixa dead tuples para o vacuum limpar |
| [0003](lessons/0003-bloat-diagnosis-and-autovacuum-tuning.md) | Diagnóstico de bloat e ajuste do autovacuum | Como medir o bloat, por que o autovacuum fica para trás e a ordem de diagnóstico que encontra a causa real em vez de chutar |
| [0004](lessons/0004-streaming-replication-and-slots.md) | Streaming replication e replication slots | Como um standby de fato se conecta e alcança o primário, e o que um replication slot garante que o streaming puro não garante |
| [0005](lessons/0005-failover-mechanics.md) | A mecânica do failover | O que acontece quando um standby é promovido, por que um antigo primário não pode simplesmente voltar ao cluster e o trade-off de perda de dados que a replicação síncrona limita |
| [0006](lessons/0006-diagnosing-replication-lag.md) | Diagnosticando o atraso de replicação | Por que o atraso de recebimento e o atraso de aplicação são medidas diferentes, e a ordem de diagnóstico que descobre qual deles está de fato acontecendo |
| [0007](lessons/0007-index-maintenance-cost.md) | Custo de manutenção de B-tree, GiST e GIN | Por que todo índice torna as escritas mais caras, e como B-tree, GiST e GIN pagam esse custo cada um de um jeito |
| [0008](lessons/0008-what-a-pgvector-index-costs.md) | Quanto custa manter um índice pgvector | O custo em disco, em tempo de construção e em memória permanente que um índice vetorial acrescenta além dos vetores brutos que ele indexa |
| [0009](lessons/0009-what-managed-shields-you-from.md) | Do que um serviço gerenciado protege você | O que a automação no estilo RDS de fato remove, e por que tudo das lições anteriores ainda precisa ser entendido por baixo dela |
| [0010](lessons/0010-defending-an-operating-choice.md) | Defendendo uma escolha de operação | Um design de deployment resolvido que cita uma decisão e um custo específicos de cada etapa, em vez de pressupor uma resposta padrão |
| [0011](lessons/0011-backup-and-point-in-time-recovery.md) | Backup e point-in-time recovery | Um base backup e um arquivo contínuo do WAL juntos permitem reconstruir qualquer momento desde o backup, e não apenas o momento em que o próprio backup foi feito, e um restore não testado não é um backup verificado |
| [0012](lessons/0012-configuration-and-memory-tuning.md) | Configuração e ajuste de memória | shared_buffers, work_mem e maintenance_work_mem respondem cada um a uma pergunta diferente sobre memória, e o mais frequentemente mal ajustado é aquele que se multiplica em silêncio por quantas operações estiverem de fato rodando ao mesmo tempo |
| [0013](lessons/0013-monitoring-activity-statements-and-the-log.md) | Monitoramento: atividade, statements e o log | Uma visão ao vivo do que cada backend está fazendo agora, uma visão agregada do que está de fato custando mais ao servidor ao longo do tempo e um log que nomeia exatamente atrás do que uma consulta travada está bloqueada são três perguntas diferentes |
| [0014](lessons/0014-connection-management-and-pgbouncer.md) | Gerenciamento de conexões e PgBouncer | Toda conexão do Postgres é um processo completo do sistema operacional, e é por isso que um pooler costuma ser necessário, e os três modos de pooling do PgBouncer trocam, cada um de um jeito, a corretude em nível de sessão pela eficiência da reutilização |
| [0015](lessons/0015-logical-replication-publications-and-subscriptions.md) | Replicação lógica, publications e subscriptions | A streaming replication envia o WAL bruto para construir uma cópia idêntica do cluster inteiro; a replicação lógica decodifica essas mesmas mudanças em eventos em nível de linha que um subscriber pode aplicar seletivamente, entre versões principais, ao custo de nunca replicar DDL por conta própria |
| [0016](lessons/0016-major-version-upgrades-and-pg-upgrade.md) | Upgrades de versão principal e pg_upgrade | Os modos de transferência mais rápidos do pg_upgrade compram a sua velocidade abrindo mão da possibilidade de simplesmente reverter, e a replicação lógica oferece uma troca genuinamente diferente, downtime quase zero, ao custo de tratar o DDL à mão durante toda a migração |
| [0017](lessons/0017-roles-privileges-and-row-level-security.md) | Roles, privilégios e row-level security | GRANTs em nível de tabela e row-level security são duas camadas de autorização separadas, e habilitar o RLS não restringe o dono da tabela a menos que você diga isso explicitamente |
| [0018](lessons/0018-partitioning-and-toast.md) | Particionamento e TOAST | O particionamento transforma um scan da tabela inteira em um scan apenas das partições relevantes e torna a exclusão em massa livre de bloat, enquanto o TOAST é o motivo pelo qual uma única linha pode guardar um valor muito maior do que uma página de 8kB |

## Referência

- [Glossário](GLOSSARY.md): termos canônicos deste tópico
- [Recursos](RESOURCES.md): fontes confiáveis
- [Vacuum e bloat](reference/vacuum-and-bloat.md): o que dispara o autovacuum e com quais números, o que segura o espaço que ele consegue recuperar e as views a verificar, em qual ordem
- [Replicação](reference/replication.md): o que um slot garante e o que ele arrisca, os cinco níveis síncronos e quando três deles não fazem nada, e os dois atrasos com as colunas que os separam
- [Manutenção de índices](reference/index-maintenance.md): o que cada tipo de índice cobra por escrita e o que o degrada, e os parâmetros e o precipício de memória que um índice pgvector traz consigo
- [Gerenciado contra auto-hospedado](reference/managed-vs-self-hosted.md): o que um serviço gerenciado automatiza e o que ele apenas muda de lugar, as três formas de alta disponibilidade que não são intercambiáveis e as decisões que um design defendido precisa nomear

## Como isto funciona

Cada lição é curta e autocontida. Os gabaritos ficam recolhidos: primeiro lembre, depois abra. A prática no mundo real importa mais do que a leitura, e espaçá-la é o ponto. Tudo o que ainda estiver confuso no fim de uma lição vale ser perseguido até a fonte primária antes de seguir adiante.
