---
title: "5. Especificidades do pgvector"
description: "Montar a busca vetorial no Postgres e mapear os conceitos de índice da lição 4 nos operadores e parâmetros reais do pgvector"
type: lesson
---

# Lição 5. Especificidades do pgvector

**Ligação com a missão:** Esta é a lição final da etapa 3: os conceitos de IVF e HNSW da lição 4 viram aqui um schema real, um operador de distância real e parâmetros de ajuste reais, sobre o vector store que este workspace adota como padrão.
**Fonte principal:** [Repositório: pgvector, pgvector](https://github.com/pgvector/pgvector)
**Pré-requisitos:** [Lição 4](0004-ann-indexes.md), [Chunk](../GLOSSARY.md)

## Aquecimento

1. ▢ O que o parâmetro `nprobe` do IVF e o parâmetro `ef_search` do HNSW controlam, cada um?

<details markdown="1"><summary>Verificação</summary>

O `nprobe` define quantos clusters do IVF são pesquisados em tempo de consulta; o `ef_search` define quantos candidatos a busca no grafo do HNSW acompanha a cada passo. Ambos trocam recall por latência: valores mais altos pesquisam mais, melhorando o recall ao custo de latência.

</details>

2. ▢ Por que a similaridade de cosseno e o produto escalar produzem o mesmo ranking apenas quando os vetores de embedding são normalizados para comprimento unitário?

<details markdown="1"><summary>Verificação</summary>

O produto escalar é a similaridade de cosseno escalada pelas magnitudes dos dois vetores. Quando ambas são fixadas em comprimento unitário, esse fator de escala é idêntico para todo par, então os rankings coincidem; quando as magnitudes variam, o produto escalar favorece os vetores maiores.

</details>

## Saiba isto

### Uma coluna vetorial e um operador de distância

O pgvector adiciona ao Postgres um tipo de coluna `vector(N)`, dimensionado de acordo com a dimensionalidade de embedding que a lição 3 definiu:

```sql
CREATE EXTENSION vector;
CREATE TABLE chunks (id bigserial PRIMARY KEY, content text, embedding vector(1536));
```

A similaridade é calculada com um de três operadores: `<->` (distância euclidiana/L2), `<#>` (produto interno negativo) e `<=>` (distância de cosseno). O operador precisa corresponder à métrica para a qual o modelo de embedding foi treinado (lição 2): usar `<=>` contra um modelo treinado para produto escalar bruto, ou vice-versa, é exatamente o descompasso que a lição 2 alertou que degrada a qualidade do ranking, agora expresso como uma escolha concreta de SQL e não abstrata. Note o sinal no `<#>`: ele é produto interno negativo justamente para que, como os outros dois operadores, menor signifique mais similar, mantendo o `ORDER BY` ascendente consistente nos três.

### Um índice precisa ser construído para uma função de distância específica

Criar um índice significa escolher uma classe de operador que corresponda à função de distância pretendida:

```sql
CREATE INDEX ON chunks USING hnsw (embedding vector_cosine_ops) WITH (m = 16, ef_construction = 64);
```

`vector_cosine_ops`, `vector_l2_ops` e `vector_ip_ops` constroem cada um o índice para um operador específico. Um índice construído com `vector_l2_ops` não acelera uma consulta que ordena por `<=>` (distância de cosseno); a classe de operador e o operador da consulta precisam corresponder, ou o índice fica sem uso e a consulta recorre em silêncio a uma varredura sequencial completa, o que anula todo o objetivo de construir o índice.

### Os nomes de parâmetros do pgvector são os parâmetros da lição 4, com outros nomes

Os parâmetros de construção de índice do HNSW, `m` (máximo de conexões por nó) e `ef_construction` (profundidade de busca na construção), são exatamente os botões de ajuste do HNSW da lição 4, definidos na hora do `CREATE INDEX`. Seu botão de recall/latência em tempo de consulta é uma configuração de sessão: `SET hnsw.ef_search = 100;`, o `ef_search` da lição 4 com outro nome. O parâmetro de construção do IVFFlat é `lists` (a contagem de clusters que a lição 4 destacou), definido do mesmo modo na criação do índice, e seu botão em tempo de consulta é `SET ivfflat.probes = 10;`, o `nprobe` da lição 4.

### O IVFFlat precisa de dados antes de ser bem construído; o HNSW não

A etapa de clusterização do IVFFlat precisa de uma amostra representativa dos vetores reais da tabela para posicionar bem seus centroides de cluster, o que significa que construir um índice IVFFlat contra uma tabela vazia ou quase vazia produz clusters ruins que não refletem a distribuição real de vetores do corpus. A consequência prática: carregue os dados primeiro, depois construa o índice IVFFlat. A estrutura de grafo do HNSW é construída de forma incremental conforme os vetores são inseridos, sem dependência equivalente de a tabela já estar preenchida, o que é parte do motivo pelo qual o HNSW costuma ser preferido para uma tabela que deve crescer com o tempo, além da vantagem de recall/latência que a lição 4 já descreveu.

## Prática

1. ▢ Um modelo de embedding foi treinado para que a similaridade de cosseno reflita a proximidade semântica. Qual operador e classe de operador do pgvector a consulta e seu índice devem usar?

<details markdown="1"><summary>Verificação</summary>

O operador `<=>` (distância de cosseno) para a consulta e `vector_cosine_ops` para o índice. Usar um operador ou uma classe de operador construída para uma função de distância diferente da usada no treinamento do modelo reintroduz o problema de descompasso de métrica da lição 2, agora como um descompasso concreto de SQL.

</details>

2. ▢ Uma equipe constrói um índice HNSW com `vector_l2_ops`, mas suas consultas ordenam os resultados usando o operador `<=>` (distância de cosseno). O que acontece, e por que isso é um problema além de apenas "a resposta errada"?

<details markdown="1"><summary>Dica</summary>

Pense se o índice sequer pode ser usado para uma consulta cujo operador não corresponde à classe de operador com a qual ele foi construído.

</details>

<details markdown="1"><summary>Verificação</summary>

O índice construído para `vector_l2_ops` não acelera uma consulta que usa `<=>`, já que o índice é construído para uma função de distância específica. A consulta recorre a uma varredura sequencial completa sobre a tabela, o que é lento em qualquer tamanho real de corpus; não é apenas um risco de resposta errada, é perder todo o benefício de desempenho para o qual o índice existia.

</details>

3. ▢ Uma tabela tem um índice IVFFlat com `lists = 1000`, mas a configuração de tempo de consulta `ivfflat.probes` é deixada no padrão de 1. O que isso significa para o trade-off entre recall e latência, em termos do `nprobe` da lição 4?

<details markdown="1"><summary>Verificação</summary>

`ivfflat.probes = 1` é `nprobe = 1`: apenas o cluster mais próximo, entre os 1.000, é pesquisado. Esse é o extremo mais rápido e de menor recall do trade-off da lição 4; uma consulta perto da fronteira de um cluster pode perder verdadeiros vizinhos mais próximos que estejam em um cluster adjacente. Aumentar `probes` pesquisa mais clusters, trocando latência de consulta por recall mais alto.

</details>

4. ▢ Por que a ordem de construção importa para um índice IVFFlat (carregar os dados e depois construir) mas não para o HNSW?

<details markdown="1"><summary>Verificação</summary>

A etapa de clusterização do IVFFlat precisa de uma amostra representativa dos vetores reais da tabela para posicionar bem seus centroides de cluster; construí-lo contra uma tabela vazia ou pouco preenchida produz clusters ruins que não refletem a distribuição real dos dados. O grafo do HNSW é construído de forma incremental conforme os vetores são inseridos, sem necessidade equivalente de a tabela já conter antes uma amostra representativa.

</details>

5. ▢ Qual afirmação é verdadeira sobre as classes de operador do pgvector (`vector_cosine_ops`, `vector_l2_ops`, `vector_ip_ops`)?

    - a) Qualquer classe de operador funciona com qualquer operador de consulta, já que o pgvector converte entre funções de distância automaticamente
    - b) A classe de operador de um índice deve corresponder ao operador de distância da consulta, ou o índice não será usado para essa consulta
    - c) A classe de operador afeta apenas índices HNSW, não IVFFlat
    - d) `vector_ip_ops` não pode ser usada com vetores de embedding normalizados

<details markdown="1"><summary>Verificação</summary>

**b)** A classe de operador e o operador da consulta precisam corresponder, ou a consulta recorre a uma varredura sequencial em vez de usar o índice. (a) é falsa: não há conversão automática entre funções de distância. (c) é falsa: ambos os tipos de índice exigem casar uma classe de operador com a função de distância. (d) é falsa: vetores normalizados são exatamente o caso em que o produto interno e a distância de cosseno coincidem, como a lição 2 cobriu.

</details>

## Prática no mundo real

- [ ] Crie uma pequena tabela do pgvector com uma coluna `vector(N)` dimensionada para um modelo de embedding que você usa e construa um índice com a classe de operador correspondente à métrica de similaridade com que esse modelo foi treinado.
- [ ] Execute `EXPLAIN` em uma consulta de similaridade contra a sua tabela e confirme que o índice está de fato sendo usado, e não recorrendo a uma varredura sequencial.
- [ ] Amanhã: experimente dois valores diferentes de `ivfflat.probes` ou `hnsw.ef_search` contra a mesma consulta e compare tanto os resultados devolvidos quanto a latência da consulta.

## Para ir além

- [Repositório: pgvector, pgvector](https://github.com/pgvector/pgvector)
- [Artigo científico: "Efficient and Robust Approximate Nearest Neighbor Search Using Hierarchical Navigable Small World Graphs", Malkov e Yashunin, 2018](https://arxiv.org/abs/1603.09320)
- [Recursos](../RESOURCES.md)

---

Não ficou claro? Releia a fonte principal no topo, já que esta lição a comprime e é na compressão que o entendimento escapa. Consulte o [glossário](../GLOSSARY.md) para qualquer termo que pareceu escorregadio.

Se o problema é a lição em si, e não o material, isso é um defeito: [abra uma issue](https://github.com/TokenCemetery/teach/issues).
