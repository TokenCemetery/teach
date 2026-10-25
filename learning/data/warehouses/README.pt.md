---
title: Warehouses
description: "Domine o data warehouse analítico: armazenamento e execução colunar, armazenamento separado do processamento e por que as recomendações de desempenho de um armazenamento por linhas deixam de valer"
type: topic
---

# Aprendizado: Data Warehouses Analíticos

Seja capaz de projetar uma tabela, um modelo e um caminho de carga no BigQuery, no Snowflake ou no Redshift que respondam às perguntas analíticas feitas a eles a um custo que você consiga prever, e de dizer, a partir do layout de armazenamento, por que uma recomendação que estava certa em um armazenamento por linhas está errada ali.

**Última lição:** [20. Mudando um modelo que outros consultam](lessons/0020-changing-a-model-others-query.md)

## O sucesso se parece com isto

- Explicar, a partir do layout de armazenamento, por que uma consulta é barata em um armazenamento por linhas e cara em um data warehouse colunar, ou o contrário, e prever o que uma mudança na consulta faz com os bytes que ela varre.
- Dizer o que o BigQuery, o Snowflake e o Redshift separam, cada um, entre armazenamento e processamento, e dimensionar ou isolar o processamento para uma carga de trabalho declarada.
- Escolher o particionamento, o clustering ou as sort keys e uma distribuição para uma tabela a partir do seu padrão de consultas, e mostrar a varredura que essa escolha economiza.
- Projetar um modelo dimensional em uma granularidade declarada, incluindo como uma dimensão que muda mantém o seu histórico.
- Projetar um caminho de carga, em lote ou em micro-batch, que possa ser executado de novo sem duplicar nem perder linhas.
- Estimar quanto custa uma consulta ou uma carga de trabalho com preço on-demand e com preço por capacidade, e cortar esse custo sem mudar a resposta.
- Decidir entre um data warehouse, o Postgres e um lakehouse para uma carga de trabalho, revisar o schema e a fatura de data warehouse de outra pessoa, e mudar um modelo que outros consultam sem quebrá-los.

## Restrições

- Pressupõe SQL funcional e nenhuma experiência prévia com data warehouses. A linguagem, os planos de consulta e o design de schemas transacionais são ensinados em [`programming/sql`](../../programming/sql/), e estas lições os pressupõem.
- BigQuery, Snowflake e Redshift são as três plataformas comparadas ao longo de toda a trilha. Cada lição ensina primeiro o mecanismo e depois nomeia como cada plataforma o expõe, para que o material sobreviva a uma troca de fornecedor.
- Padrões, limites e preços das plataformas mudam entre versões. Onde uma lição cita um deles, ela nomeia a página de documentação de onde ele veio, e o leitor deve conferir essa página para saber o valor atual.

## Fora do escopo

- A linguagem SQL, os planos de consulta, o design de schemas e o isolamento em um armazenamento por linhas: veja [`programming/sql`](../../programming/sql/), sobre o qual esta trilha se apoia em vez de repeti-lo.
- Operar uma instância do Postgres: veja [`data/postgres`](../../data/postgres/). A etapa 8 compara o Postgres como candidato para uma carga de trabalho analítica; ela não ensina a operá-lo.
- Plataformas de streaming como assunto. A etapa 6 carrega a partir de um stream; como o próprio log funciona está em [`data/kafka`](../../data/kafka/).
- Frameworks de orquestração e de transformação (Airflow, dbt) como assuntos. Eles aparecem onde uma lição de carga ou de modelagem precisa deles, e como configurá-los não é ensinado.
- Ferramentas de BI, camadas semânticas e design de dashboards.
- Spark, Trino e outros engines como assuntos. A etapa 8 coloca o lakehouse que eles consultam frente ao data warehouse; ela não ensina a executá-los.

## O arco

Oito etapas, do layout de armazenamento ao julgamento. Uma etapa leva várias lições e as fronteiras são flexíveis; o que torna uma etapa concluída é a capacidade, não a contagem de lições.

| Etapa | Lições | Cobre | Concluída quando |
|---|---|---|---|
| 1. Armazenamento por linhas e por colunas | 0001 a 0002 | Padrões de acesso OLTP e OLAP, armazenamento por linhas contra armazenamento por colunas, row groups, column chunks e suas estatísticas | Consegue prever qual layout lê menos bytes para uma consulta declarada, e por quê |
| 2. Execução colunar | 0003 a 0004 | Codificação por dicionário, run-length e delta, compressão, execução vetorizada, materialização tardia | Consegue dizer por que um armazenamento por colunas comprime e executa do jeito que faz, e quanto custa `SELECT *` ali |
| 3. Armazenamento e processamento | 0005 a 0006 | Como o BigQuery, o Snowflake e o Redshift separam armazenamento de processamento, slots, virtual warehouses, tipos de nó, concorrência e isolamento de cargas de trabalho | Consegue dimensionar e isolar o processamento para uma carga de trabalho declarada em qualquer um dos três |
| 4. Design físico | 0007 a 0010 | Particionamento e pruning, clustering e sort keys, zone maps, distribuição e estratégia de join, as recomendações de armazenamento por linhas que deixam de valer | Consegue escolher o layout físico de uma tabela a partir do seu padrão de consultas e mostrar a varredura que ele economiza |
| 5. Modelagem dimensional | 0011 a 0013 | Fatos, dimensões e a granularidade, star schemas contra tabelas largas e aninhadas, slowly changing dimensions | Consegue projetar um modelo em uma granularidade declarada que mantenha o histórico de que uma pergunta precisa |
| 6. Carga | 0014 a 0015 | ELT contra ETL, carga em lote e tamanho dos arquivos, ingestão em micro-batch e em streaming, merges idempotentes | Consegue projetar um caminho de carga que possa ser executado de novo sem duplicar nem perder linhas |
| 7. Custo | 0016 a 0017 | Preço on-demand e por capacidade em cada plataforma, ler o custo de uma consulta, caches, views materializadas e os controles que limitam uma fatura | Consegue estimar o custo de uma carga de trabalho e cortá-lo sem mudar a resposta |
| 8. Julgamento | 0018 a 0020 | Data warehouse contra Postgres contra um lakehouse, revisar um schema e a sua fatura, mudar um modelo que outros consultam, resolver uma disputa pela documentação da plataforma | Tem a confiança para tomar a decisão e explicá-la a outra pessoa |

## Lições

Siga estas na ordem.

| # | Lição | Ensina |
|---|---|---|
| [0001](lessons/0001-row-stores-and-column-stores.md) | Armazenamento por linhas e armazenamento por colunas | Por que uma consulta analítica lê de um armazenamento por colunas uma fração dos bytes que lê de um armazenamento por linhas, e por que a busca de uma única linha vai no sentido oposto |
| [0002](lessons/0002-inside-a-columnar-file.md) | Por dentro de um arquivo colunar | Como row groups, column chunks e estatísticas por chunk deixam um leitor pular dados que ele nunca descomprime |
| [0003](lessons/0003-encoding-and-compression.md) | Codificação e compressão | Por que uma coluna de um único tipo comprime muito melhor do que uma linha, e qual codificação serve para qual formato de dados |
| [0004](lessons/0004-vectorized-execution-and-late-materialization.md) | Execução vetorizada e materialização tardia | Como um engine colunar processa um lote de valores por chamada e monta linhas apenas para os valores que sobrevivem |
| [0005](lessons/0005-separating-storage-from-compute.md) | Separando armazenamento de processamento | O que o BigQuery, o Snowflake e o Redshift mantêm, cada um, separado entre onde os dados vivem e o que os lê, e o que isso compra e custa |
| [0006](lessons/0006-compute-sizing-concurrency-and-isolation.md) | Dimensionamento de processamento, concorrência e isolamento de cargas de trabalho | Como dimensionar o processamento para uma carga de trabalho e impedir que as consultas de um time fiquem na fila atrás das de outro |
| [0007](lessons/0007-partitioning-and-pruning.md) | Particionamento e pruning | Como uma tabela particionada deixa um filtro pular partições inteiras, e os filtros que varrem tudo em silêncio |
| [0008](lessons/0008-clustering-and-sort-keys.md) | Clustering e sort keys | Como ordenar os dados dentro do armazenamento estreita o mínimo e o máximo de cada bloco para que um filtro pule mais deles |
| [0009](lessons/0009-joins-and-data-distribution.md) | Joins e distribuição de dados | Como um data warehouse distribuído move linhas para juntá-las, e como uma escolha de distribuição decide se ele precisa fazer isso |
| [0010](lessons/0010-the-row-store-advice-that-stops-applying.md) | As recomendações de armazenamento por linhas que deixam de valer | Quais hábitos de indexar e normalizar um armazenamento por linhas estão errados em um data warehouse colunar, e quais ainda valem |
| [0011](lessons/0011-facts-dimensions-and-the-grain.md) | Fatos, dimensões e a granularidade | Como declarar o que uma linha de uma tabela fato significa antes de escolher uma única coluna |
| [0012](lessons/0012-star-schemas-wide-tables-and-nesting.md) | Star schemas, tabelas largas e aninhamento | Quando manter as dimensões em tabelas próprias, quando achatá-las em uma tabela larga e quando aninhá-las |
| [0013](lessons/0013-slowly-changing-dimensions.md) | Slowly changing dimensions | Como uma dimensão mantém ou descarta o seu histórico quando um atributo muda, e o que cada escolha faz com relatórios antigos |
| [0014](lessons/0014-elt-and-batch-loading.md) | ELT e carga em lote | Por que data warehouses carregam primeiro os dados brutos e os transformam no lugar, e como a quantidade e o tamanho dos arquivos decidem a velocidade da carga |
| [0015](lessons/0015-micro-batch-streaming-and-idempotent-merges.md) | Micro-batch, streaming e merges idempotentes | Como trazer dados continuamente e fazer com que executar de novo qualquer carga deixe a tabela exatamente como uma única execução deixaria |
| [0016](lessons/0016-how-a-warehouse-bills.md) | Como um data warehouse cobra | O que cada plataforma cobra com preço on-demand e com preço por capacidade, e qual carga de trabalho cada modelo favorece |
| [0017](lessons/0017-reading-and-cutting-a-querys-cost.md) | Lendo e cortando o custo de uma consulta | Como descobrir quanto uma consulta vai custar antes de executá-la, e as mudanças que cortam esse custo sem mudar a sua resposta |
| [0018](lessons/0018-warehouse-postgres-or-lakehouse.md) | Data warehouse, Postgres ou lakehouse | Como decidir onde uma carga de trabalho analítica deve ficar, e quando a resposta de sempre, um data warehouse, é a errada |
| [0019](lessons/0019-reviewing-a-warehouse-schema-and-its-bill.md) | Revisando um schema de data warehouse e a sua fatura | Como revisar o design de data warehouse de outra pessoa e nomear o que cada escolha custa, em bytes e em dinheiro |
| [0020](lessons/0020-changing-a-model-others-query.md) | Mudando um modelo que outros consultam | Como mudar uma tabela da qual dashboards e pipelines dependem sem quebrá-los, e como resolver uma afirmação em disputa pela documentação |

## Referência

- [Glossário](GLOSSARY.md): termos canônicos deste tópico
- [Recursos](RESOURCES.md): fontes confiáveis, cada uma anotada com o que cobre
- [Armazenamento e execução colunar](reference/columnar-storage-and-execution.md): layout por linhas contra layout por colunas, as codificações e o que um engine colunar pula
- [Plataformas comparadas](reference/platforms-compared.md): como o BigQuery, o Snowflake e o Redshift nomeiam e cobram as mesmas ideias de armazenamento e processamento
- [Design físico](reference/physical-design.md): particionamento, clustering, sort keys e distribuição em cada plataforma, e os hábitos de armazenamento por linhas a abandonar
- [Modelagem dimensional](reference/dimensional-modelling.md): os quatro passos de design, os formatos de schema e os tipos de slowly changing dimension
- [Carga](reference/loading.md): métodos de carga por plataforma, tamanho dos arquivos e os padrões que tornam seguro executar uma carga de novo
- [Modelo de custo](reference/cost-model.md): o que cada modelo de preço cobra, como ler o custo de uma consulta e os controles que limitam uma fatura
- [Revisão de schema e de fatura](reference/schema-and-bill-review.md): um checklist para revisar o design de um data warehouse e a sua fatura, e a decisão de onde colocar a carga

## Como isto funciona

Cada lição é curta e autocontida. Os gabaritos ficam recolhidos: primeiro lembre, depois abra. A prática no mundo real importa mais do que a leitura, e espaçá-la é o ponto. Tudo o que ainda estiver confuso no fim de uma lição vale ser perseguido até a fonte primária antes de seguir adiante.
