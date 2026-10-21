---
title: "Busca Vetorial e Indexação"
description: "O trade-off entre recall e latência de IVF e HNSW, e os operadores, parâmetros de índice e especificidades de ordem de construção do pgvector"
type: reference
---

# Busca Vetorial e Indexação

A busca de vizinho mais próximo aproximado e sua implementação no pgvector. Feito para consulta ao montar ou ajustar um índice.

## Por que a busca exata não escala

A busca exata de vizinho mais próximo compara uma consulta com cada vetor: linear no tamanho do corpus, lenta demais com milhões de chunks. Um índice de **vizinho mais próximo aproximado (ANN)** aceita uma pequena quantidade controlável de inexatidão em troca de tempos de busca que não crescem linearmente.

## IVF e HNSW

| Índice | Mecanismo | Botão em tempo de busca | Custo de construção |
|---|---|---|---|
| IVF (inverted file) | Particiona os vetores em clusters (k-means) com antecedência; busca apenas nos `nprobe` clusters mais próximos | `nprobe`: baixo = rápido, pode perder vizinhos perto da fronteira de um cluster; alto = se aproxima da busca exata | Precisa de uma amostra representativa do corpus para posicionar bem os centroides |
| HNSW (hierarchical navigable small world) | Grafo multicamada; camadas superiores esparsas para saltos longos, camada inferior densa para busca local precisa, percorrido de forma gulosa de cima para baixo | `ef_search`: quantos candidatos são acompanhados a cada passo; baixo = rápido mas pode se contentar com um nó localmente bom; alto = mais recall | Mais memória (arestas do grafo) e uma construção de índice mais lenta que a do IVF |

Os dois botões ajustam um ponto em uma **curva de recall/latência** para um dado corpus; nenhum tem uma configuração universalmente correta. O HNSW geralmente atinge um ponto melhor nessa curva que o IVF (recall mais alto com a mesma latência), ao custo de memória e tempo de construção. O ponto certo depende do orçamento de latência da carga de trabalho e de quanta perda de recall uma etapa posterior (reranking) consegue absorver, medido e não presumido.

## pgvector: coluna, operador, índice

```sql
CREATE EXTENSION vector;
CREATE TABLE chunks (id bigserial PRIMARY KEY, content text, embedding vector(1536));
```

| Operador | Distância | Classe de operador (para indexação) |
|---|---|---|
| `<->` | Euclidiana/L2 | `vector_l2_ops` |
| `<#>` | Produto interno negativo | `vector_ip_ops` |
| `<=>` | Cosseno | `vector_cosine_ops` |

O `<#>` é produto interno *negativo* justamente para que, como os outros dois, menor signifique mais similar, mantendo o `ORDER BY` ascendente consistente nos três. O operador precisa corresponder à [métrica para a qual o modelo de embedding foi treinado](chunking-and-embeddings.md#similarity-metrics-must-match-training): usar `<=>` contra um modelo treinado com produto escalar (ou vice-versa) é esse mesmo descompasso de métrica, agora como uma escolha concreta de SQL.

```sql
CREATE INDEX ON chunks USING hnsw (embedding vector_cosine_ops) WITH (m = 16, ef_construction = 64);
```

**Um índice é construído para uma função de distância específica.** Uma consulta que ordena por um operador que não corresponde à classe de operador do índice não usa esse índice de forma alguma: ela recorre em silêncio a uma varredura sequencial completa, perdendo todo o benefício de desempenho para o qual o índice existia. Não há conversão automática entre funções de distância.

## Os parâmetros do pgvector são os da lição 4, renomeados

| Conceito | HNSW | IVFFlat |
|---|---|---|
| Parâmetro(s) de tempo de construção | `m` (máximo de conexões por nó), `ef_construction` (profundidade de busca na construção), definidos no `CREATE INDEX` | `lists` (número de clusters), definido no `CREATE INDEX` |
| Botão de recall/latência em tempo de consulta | `SET hnsw.ef_search = 100;` | `SET ivfflat.probes = 10;` (este é o `nprobe`) |

## A ordem de construção importa para o IVFFlat, não para o HNSW

A etapa de clusterização do IVFFlat precisa de uma amostra representativa dos vetores reais da tabela para posicionar bem os centroides: construí-lo contra uma tabela vazia ou esparsa produz clusters ruins. Carregue os dados primeiro, depois construa o índice IVFFlat. O grafo do HNSW é construído de forma incremental conforme os vetores são inseridos, sem dependência equivalente, o que é parte do motivo pelo qual o HNSW costuma ser preferido para uma tabela que deve crescer com o tempo.

## Relacionado

- [Lição 4](../lessons/0004-ann-indexes.md), [Lição 5](../lessons/0005-pgvector-specifics.md)
- [Chunking e Embeddings](chunking-and-embeddings.md): os vetores e a métrica de similaridade com os quais o índice desta folha precisa corresponder
