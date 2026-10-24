---
title: SQL
description: "Domine o banco de dados: escreva a consulta, leia o plano, projete o schema, sobreviva à concorrência"
type: topic
---

# Aprendizado: SQL

Torne-se o engenheiro a quem um time confia seu banco de dados: capaz de expressar uma pergunta como uma consulta que responde exatamente a ela, ler um plano de consulta para descobrir por que essa consulta está lenta, escolher um índice a partir de evidências e não do instinto, raciocinar sobre o que transações concorrentes podem observar, e projetar e migrar um schema que mantém dados ruins de fora e continua rápido à medida que a tabela cresce.

**Comece aqui:** [0001. Tabelas, linhas e tipos](lessons/0001-tables-rows-and-types.md)
**Última lição:** [0053. Triggers, stored procedures e onde a lógica deve ficar](lessons/0053-triggers-stored-procedures-and-where-logic-belongs.md)

## O sucesso se parece com isto

- Escrever uma consulta com joins, agregação e window functions que responde à pergunta feita, e explicar por que o resultado tem exatamente essas linhas, `NULL`s incluídos.
- Ler um plano de execução com tempos reais e nomear qual passo é o problema.
- Escolher um índice, ou rejeitar um, a partir do plano e da seletividade, e depois provar a diferença com uma medição.
- Dizer o que uma transação em um dado nível de isolamento pode observar, e nomear a anomalia da qual um bug de concorrência depende.
- Projetar um schema em que dados ruins são impossíveis, e não apenas desencorajados, usando chaves, tipos e constraints.
- Alterar o schema de um sistema em produção sem downtime e sem uma fila de locks atrás da migração.
- Pegar uma consulta lenta gerada por um ORM, explicar por que ela é lenta e reescrevê-la.
- Revisar a consulta ou o schema de alguém e nomear concretamente o que vai custar com dez vezes mais linhas.

## Restrições

- Não pressupõe SQL prévio nem experiência com administração de banco de dados.
- PostgreSQL é o motor de referência, porque sua documentação é a descrição livremente disponível mais completa de como um planner real e um modelo real de concorrência se comportam. SQLite é usado quando uma prática não deve precisar de servidor algum. Onde os motores de fato diferem, a lição diz isso e nomeia o comportamento padrão, se houver um.
- Precisa apenas de um motor local e de um terminal em qualquer sistema operacional suportado. Nada no arco exige ferramentas pagas, uma conta de nuvem ou um banco de dados gerenciado.
- As práticas precisam de dados, e uma tabela com dez linhas ensina a lição errada sobre índices. O arco usa um único conjunto de dados que cresce o bastante para que as escolhas do planner sejam reais.
- O comportamento do planner muda entre versões major. Afirmações sensíveis à versão são conferidas contra a documentação atual, e toda lição que depende de uma versão diz qual.

## Fora do escopo

- Administração de banco de dados como assunto: backups e recuperação, replicação, failover, connection pooling, upgrades de versão. Veja [`data/postgres`](../../data/postgres/), que cuida da instância em execução.
- ORMs e query builders como assuntos por si só. A saída deles é lida e criticada na etapa 7; como configurar um não é ensinado.
- Executar migrações a partir de um pipeline de deploy: quando uma migração roda em relação ao código que precisa dela, e como expand and contract distribui uma mudança por vários deploys. Isso é [`infrastructure/ci-cd`](../../infrastructure/ci-cd/), cuja folha [Deployments](../../infrastructure/ci-cd/reference/deployments.md) guarda a ordem das migrações.
- Data warehouses analíticos e seus dialetos: BigQuery, Snowflake, Redshift, Spark SQL. A execução colunar muda as recomendações de desempenho, e o arco não vai atrás disso.
- Stores não relacionais como alternativas de comparação. O que tem trilha própria é [`data/redis`](../../data/redis/).
- Internos do motor além do ponto em que deixam de explicar o comportamento de consultas e transações: formatos em disco, internos do write-ahead log, o código-fonte do planner.

## O arco

Sete etapas, do zero ao nível sênior. Não é uma lista de lições: uma etapa leva várias lições e as fronteiras são flexíveis.

| Etapa | Lições | Cobre | Concluída quando |
|---|---|---|---|
| 1. O modelo relacional | 0001 a 0006 | Tabelas, linhas e tipos, `NULL` e lógica de três valores, `SELECT`, filtragem, ordenação, conjuntos contra multiconjuntos, o que é uma chave | Consegue dizer por que uma consulta devolveu exatamente essas linhas, incluindo as que o `NULL` removeu |
| 2. Consultas | 0007 a 0013 | Todo tipo de join, agregação e `GROUP BY`, `HAVING`, subconsultas, common table expressions, operações de conjunto | Expressa uma pergunta como uma única consulta sem tentativa e erro |
| 3. Além do básico | 0014 a 0020 | Window functions e frames, lateral joins, consultas recursivas, colunas `JSON` onde fazem jus ao lugar | Resolve problemas de ranking e de total acumulado em SQL em vez de no código da aplicação |
| 4. Design de schema | 0021 a 0027 | Normalização e quando parar, chaves primárias e estrangeiras, constraints, escolher tipos de propósito, chaves substitutas contra chaves naturais | Dados ruins são impossíveis, e não apenas desencorajados |
| 5. Transações | 0028 a 0034 | ACID como quatro promessas separadas, níveis de isolamento e as anomalias que cada um permite, controle de concorrência multiversão, locks, deadlocks, locks explícitos de linha, idempotência | Consegue nomear a anomalia da qual um bug de concorrência depende, antes de reproduzi-lo |
| 6. Desempenho | 0035 a 0041 | Índices B-tree primeiro e os outros depois, seletividade e cardinalidade, estatísticas, ler um plano com tempos, estratégias de join, paginação, quando a consulta não é o problema | Otimiza a partir de um plano e prova o ganho com uma medição |
| 7. Operação e julgamento | 0042 a 0048 | Migrações sem downtime, revisar consultas e schemas, ler a saída de ORMs, portabilidade entre motores, quando SQL é a ferramenta errada | Tem a confiança para tomar a decisão e explicá-la a outra pessoa; a etapa 8 a completa com as perguntas de revisão sobre autorização e lógica procedural que o próprio checklist desta etapa pressupunha |
| 8. Segurança e ferramentas especializadas | 0049 a 0053 | SQL injection e statements parametrizados, roles e privilégio mínimo, row-level security, busca full-text, triggers e stored procedures | Revisa uma fronteira de autorização e um trecho de lógica procedural com a mesma concretude de uma consulta ou de uma mudança de schema |

## Lições

Siga estas na ordem.

| # | Lição | Ensina |
|---|---|---|
| [0001](lessons/0001-tables-rows-and-types.md) | Tabelas, linhas e tipos | O tipo de uma coluna é uma constraint que você ganha de graça, e o tipo errado é difícil de desfazer |
| [0002](lessons/0002-select-and-evaluation-order.md) | SELECT e ordem de avaliação | As cláusulas executam em uma ordem diferente da que são escritas, o que explica a maioria dos erros de iniciante |
| [0003](lessons/0003-null-and-three-valued-logic.md) | NULL e lógica de três valores | O WHERE mantém apenas o verdadeiro, então o desconhecido se comporta como falso e NOT IN pode não devolver nada |
| [0004](lessons/0004-sets-and-bags.md) | Conjuntos e multiconjuntos | Uma tabela é um multiconjunto, então as duplicatas são reais e o UNION paga em silêncio para removê-las |
| [0005](lessons/0005-sorting-and-collation.md) | Ordenação e collation | A ordenação de texto depende de uma collation, e um empate sem chave única não é estável |
| [0006](lessons/0006-keys-and-constraints.md) | Chaves e constraints | Uma chave é uma afirmação que o banco de dados garante, e toda afirmação que você deixa de fora vira um bug |
| [0007](lessons/0007-joins-and-what-they-do.md) | Joins, e o que um join realmente faz | Um join é um produto cartesiano filtrado, então a condição ON decide quais linhas existem antes de qualquer outra coisa executar |
| [0008](lessons/0008-outer-joins-and-missing-rows.md) | Outer joins e as linhas que não estão lá | Um outer join mantém as linhas que não casaram com nada, e uma única cláusula WHERE as joga fora de novo em silêncio |
| [0009](lessons/0009-aggregation-and-group-by.md) | Agregação e GROUP BY | Agregações ignoram NULL, e um join que multiplica linhas multiplica o total |
| [0010](lessons/0010-having-and-filter.md) | HAVING, FILTER e vários agrupamentos de uma vez | Onde uma condição fica decide quais linhas ela ainda enxerga, e uma única passada pode responder a vários agrupamentos |
| [0011](lessons/0011-subqueries.md) | Subconsultas, e qual tipo responde à pergunta | Um escalar, um IN, um EXISTS e uma tabela derivada respondem a quatro perguntas diferentes, e um deles mente quando aparece NULL |
| [0012](lessons/0012-common-table-expressions.md) | Common table expressions | WITH dá nome a um passo para que uma consulta longa seja lida de cima para baixo, e nesta versão ele não é uma barreira de otimização |
| [0013](lessons/0013-set-operations.md) | Operações de conjunto, e uma pergunta como uma consulta | UNION, INTERSECT e EXCEPT combinam conjuntos de resultados por posição e removem duplicatas, a menos que se peça o contrário |
| [0014](lessons/0014-window-functions.md) | Window functions | Uma window function calcula sobre outras linhas sem colapsar aquela em que está |
| [0015](lessons/0015-window-frames.md) | Window frames | O frame padrão inclui toda linha que empata com a atual, e é por isso que um total acumulado pode dar saltos |
| [0016](lessons/0016-navigating-within-a-window.md) | Navegando dentro de uma janela | lag, lead e as funções de valor alcançam outras linhas diretamente, e duas delas obedecem ao frame |
| [0017](lessons/0017-lateral-joins.md) | Lateral joins | LATERAL permite que uma subconsulta no FROM enxergue a linha ao lado, e é assim que você pega os primeiros de cada grupo |
| [0018](lessons/0018-recursive-queries.md) | Consultas recursivas | Uma CTE recursiva realimenta a própria saída até que nada novo saia, e é assim que se percorre uma hierarquia |
| [0019](lessons/0019-json-columns.md) | Colunas JSON | Consultar uma coluna de documento é SQL comum quando você sabe qual operador devolve texto e qual devolve JSON |
| [0020](lessons/0020-choosing-the-tool.md) | Escolhendo a ferramenta | Top-N, totais acumulados e deduplicação têm cada um duas ou três formas corretas de escrever, e a escolha depende do que a pergunta pede |
| [0021](lessons/0021-normalisation.md) | Normalização | Cada forma normal remove uma maneira de duas linhas discordarem sobre o mesmo fato |
| [0022](lessons/0022-choosing-a-key.md) | Escolhendo uma chave | Uma chave substituta compra estabilidade e abre mão do significado, e o gerador que você escolhe decide o que mais ela custa |
| [0023](lessons/0023-foreign-keys.md) | Chaves estrangeiras e o que acontece no delete | Uma chave estrangeira é uma promessa sobre linhas que existem, e a ação que você escolhe decide quem paga quando uma delas some |
| [0024](lessons/0024-constraints-that-hold.md) | Constraints que de fato se sustentam | Um CHECK só falha quando sua condição é falsa, então um valor ausente satisfaz quase toda regra que você escreveu |
| [0025](lessons/0025-choosing-types.md) | Escolhendo tipos de propósito | Um tipo decide o que o banco de dados vai aceitar, o que vai alterar em silêncio e o que nunca vai poder desfazer |
| [0026](lessons/0026-denormalising-on-purpose.md) | Desnormalizando de propósito | Uma segunda cópia de um fato é uma segunda chance de estar errado, a menos que seja o banco de dados quem a mantém |
| [0027](lessons/0027-making-bad-data-impossible.md) | Tornando dados ruins impossíveis | Pegue um schema que permite uma linha errada e feche cada brecha, depois diga o que o design ainda não consegue prometer |
| [0028](lessons/0028-what-a-transaction-promises.md) | O que uma transação promete | Quatro promessas viajam sob uma única sigla, e só uma delas cabe a você negociar |
| [0029](lessons/0029-mvcc.md) | Controle de concorrência multiversão | Um update escreve uma nova versão da linha em vez de alterar a existente, e é por isso que um leitor nunca espera por um escritor |
| [0030](lessons/0030-isolation-levels.md) | Níveis de isolamento | O PostgreSQL oferece três níveis distintos sob quatro nomes, e cada um permite um conjunto diferente de surpresas |
| [0031](lessons/0031-the-anomalies.md) | As anomalias, e como reconhecer a sua | Todo bug de concorrência tem um nome, e nomeá-lo diz qual nível ou lock o teria evitado |
| [0032](lessons/0032-locks.md) | Locks que você pega de propósito | Um lock de linha é como você mantém uma decisão parada, e cada um deles tem um modo de falha que vale escolher |
| [0033](lessons/0033-deadlocks.md) | Deadlocks | Duas transações segurando cada uma o que a outra precisa, e a única cura é combinar uma ordem de antemão |
| [0034](lessons/0034-idempotency-and-retry.md) | Idempotência e o retry correto | Um retry que repete os mesmos statements reproduz o bug que deveria corrigir, então ele precisa ler de novo e decidir de novo |
| [0035](lessons/0035-reading-a-plan.md) | Lendo um plano | O plano diz o que o banco de dados fez e o que ele esperava, e a diferença entre os dois é onde está o trabalho |
| [0036](lessons/0036-what-an-index-does.md) | O que um índice realmente faz | Uma B-tree transforma a varredura de todas as linhas em uma descida por algumas páginas, e o plano diz de qual de quatro maneiras ele as leu |
| [0037](lessons/0037-selectivity-and-statistics.md) | Seletividade e estatísticas | Todo plano é construído a partir de uma amostra dos seus dados, então um plano ruim costuma ser uma estimativa ruim e não um planner ruim |
| [0038](lessons/0038-choosing-an-index.md) | Escolhendo um índice | A ordem das colunas decide a quais consultas um índice consegue responder, e o melhor índice muitas vezes é aquele que você decide não criar |
| [0039](lessons/0039-join-strategies.md) | Estratégias de join | Três maneiras de fazer join, e o planner escolhe pelo custo estimado, então uma estimativa errada aparece como a estratégia errada |
| [0040](lessons/0040-pagination-and-counting.md) | Paginação e contagem | OFFSET lê e descarta cada linha que pula, e contar com exatidão custa uma passada pela tabela |
| [0041](lessons/0041-when-the-query-is-not-the-problem.md) | Quando a consulta não é o problema | Provar um ganho exige uma medição que você consiga repetir, e a causa muitas vezes é a tabela, o tráfego ou o cliente |
| [0042](lessons/0042-migrations-without-downtime.md) | Migrações sem downtime | Uma migração que leva um milissegundo ainda pode parar toda leitura na tabela, por causa do que fica na fila atrás dela |
| [0043](lessons/0043-changing-what-has-data.md) | Alterando o que já tem dados | Uma constraint em uma tabela cheia são dois statements, e um backfill é um loop e não um único UPDATE |
| [0044](lessons/0044-reviewing-a-query.md) | Revisando uma consulta | Leia a consulta pelas linhas que ela devolve antes de lê-la pela velocidade, porque uma resposta errada e rápida é pior |
| [0045](lessons/0045-reviewing-a-schema-change.md) | Revisando uma mudança de schema | Pergunte o que a migração bloqueia, o que ela reescreve e o que roda enquanto as duas versões do código estão no ar |
| [0046](lessons/0046-portability.md) | Portabilidade, e quanto ela custa | A maior parte deste arco vale entre motores, e as partes que não valem são as de que vale depender de propósito |
| [0047](lessons/0047-reading-orm-output.md) | Lendo o que um ORM emite | O ORM escreve o SQL que você não escreveu, e a única maneira de saber o que ele enviou é olhar |
| [0048](lessons/0048-trusted-with-the-database.md) | De confiança com o banco de dados | Sete etapas terminam em um único hábito, que é nomear a linha, o lock ou o plano que torna uma decisão defensável |
| [0049](lessons/0049-sql-injection-and-parameterised-statements.md) | SQL injection e statements parametrizados | A concatenação de strings permite que um valor mude o que um statement significa, não só o que ele casa, e um statement parametrizado elimina a possibilidade em vez de tentar sanitizar cada caso |
| [0050](lessons/0050-roles-and-least-privilege.md) | Roles e privilégio mínimo | Roles englobam as antigas ideias de usuários e grupos, o ownership já concede todo privilégio sem precisar de GRANT, e privilégio mínimo diz respeito inteiramente ao que todos os outros podem fazer |
| [0051](lessons/0051-row-level-security.md) | Row-level security | O GRANT decide o acesso a uma tabela como um todo, uma política de segurança de linha decide por linha, e o motor a aplica em todo caminho de acesso, não só naquele que um desenvolvedor lembrou de filtrar |
| [0052](lessons/0052-full-text-search.md) | Busca full-text | tsvector reduz um documento a lexemas normalizados que um índice GIN consegue buscar, tsquery pergunta se eles estão presentes, e a fronteira com um motor de busca dedicado fica onde o ranking e a escala superam uma única coluna |
| [0053](lessons/0053-triggers-stored-procedures-and-where-logic-belongs.md) | Triggers, stored procedures e onde a lógica deve ficar | Este é o fechamento da etapa 8, um trigger roda em todo caminho que chega a uma tabela e uma procedure pode fazer commit ou rollback da própria transação, e a decisão de julgamento é saber quando essa invisibilidade realmente vale o custo |

## Referência

- [Glossário](GLOSSARY.md): termos canônicos deste tópico
- [Recursos](RESOURCES.md): fontes confiáveis, cada uma anotada com o que cobre
- [O conjunto de dados](reference/the-dataset.md): o schema e os dados que toda lição a partir da etapa 2 consulta, e como carregá-los
- [NULL e lógica de três valores](reference/null-and-three-valued-logic.md): tabelas-verdade, onde NULL conta como igual, e as armadilhas com suas correções
- [Ordem de avaliação de um SELECT](reference/select-evaluation-order.md): o que executa quando, o que cada cláusula enxerga e quais erros isso explica
- [Consultas](reference/querying.md): a folha da etapa 2, com todo tipo de join, o que cada agregação faz com NULL e onde uma condição deve ficar
- [Além do básico](reference/beyond-the-basics.md): a folha da etapa 3, com as window functions, os modos de frame e qual ferramenta responde a qual pergunta
- [Design de schema](reference/schema-design.md): a folha da etapa 4, com as formas normais, todo tipo de constraint e qual tipo recusa o quê
- [Transações](reference/transactions.md): a folha da etapa 5, com cada nível de isolamento, as anomalias que ele permite, as forças de lock e os erros que admitem retry
- [Desempenho](reference/performance.md): a folha da etapa 6, com os nós do plano, em quais números confiar, as estratégias de varredura e de join, e as decisões de índice
- [Operação](reference/operating.md): a folha da etapa 7, com quais migrações são seguras, as perguntas de revisão e o que vale entre motores

## Como isto funciona

Cada lição é curta e autocontida. Os gabaritos ficam recolhidos: primeiro lembre, depois abra. A prática no mundo real importa mais do que a leitura, e espaçá-la é o ponto. Tudo o que ainda estiver confuso no fim de uma lição vale ser perseguido até a fonte primária antes de seguir adiante.
