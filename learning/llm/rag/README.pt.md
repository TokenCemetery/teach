---
title: "RAG"
description: "Domine a recuperação: chunking, embeddings, busca híbrida, reranking e a medição de se a coisa certa foi recuperada"
type: topic
---

# Aprendizado: RAG

Seja capaz de projetar um pipeline de recuperação para um corpus e um caso de uso reais e de diagnosticar por que um sistema RAG existente devolve o contexto errado, em vez de chutar uma correção.

**Última lição:** [20. Revisando um pipeline de recuperação](lessons/0020-reviewing-a-retrieval-pipeline.md)

## O sucesso se parece com isto

- Projetar um pipeline de recuperação (chunking, embeddings, busca híbrida, reranking) para um corpus e um caso de uso declarados, e justificar cada escolha em relação a eles.
- Dado um sistema RAG que devolve contexto errado ou irrelevante, diagnosticar qual etapa do pipeline está com defeito, em vez de reajustar ao acaso.
- Ajustar os pesos da busca híbrida contra uma métrica de recuperação medida, e não por sensação.
- Levar o contexto recuperado até uma resposta gerada e explicar o que a própria etapa de geração ainda pode errar.
- Revisar o design do pipeline de recuperação de outra pessoa e nomear especificamente o que ele vai errar antes de ir para produção, e dizer quando o próprio RAG (e não uma etapa do pipeline) é a resposta errada para o problema declarado.

## Restrições

- Pressupõe Python básico e familiaridade com o que é um embedding; não exige experiência prévia com sistemas de recuperação.
- Vector store: pgvector, para que os conceitos se conectem à cobertura de `data/postgres` sobre o que um índice vetorial custa ao banco de dados.

## Fora do escopo

- Técnica de prompt engineering e qualidade de geração em geral: veja [`llm/prompting`](../../llm/prompting/). Tocado aqui apenas no que diz respeito a como o contexto recuperado chega à etapa de geração, sem ser reapresentado como um tópico próprio.
- Como a própria métrica de recuperação é construída e defendida: veja [`llm/evals`](../../llm/evals/), referenciado em vez de reapresentado.
- O que um índice vetorial custa ao banco de dados em termos operacionais: veja [`data/postgres`](../../data/postgres/), referenciado em vez de reapresentado.

## O arco

Catorze etapas, do primeiro chunk a um pipeline de produção diagnosticado, consciente de custo e monitorado, encerrando com julgamento. Uma etapa leva várias lições e as fronteiras são flexíveis; o que torna uma etapa concluída é a capacidade, não a contagem de lições.

| Etapa | Lições | Cobre | Concluída quando |
|---|---|---|---|
| 1. Chunking | 0001 | A primeira escolha do pipeline, e a que toda etapa posterior herda | Consegue fazer o chunking de um corpus declarado e justificar a escolha |
| 2. Embeddings | 0002 a 0003 | Modelos de embedding, métricas de similaridade, trade-offs de dimensionalidade | Consegue escolher um modelo de embedding e uma métrica para um corpus declarado |
| 3. Busca vetorial e indexação | 0004 a 0005 | Índices ANN (HNSW/IVF), especificidades do pgvector, o trade-off entre recall e latência | Consegue montar a busca vetorial sobre o pgvector para o corpus dividido em chunks |
| 4. Busca híbrida | 0006 a 0007 | BM25 mais busca vetorial, reciprocal rank fusion, ajuste da mistura | Consegue ajustar os pesos da busca híbrida contra uma métrica de recuperação medida |
| 5. Reranking | 0008 a 0009 | Rerankers cross-encoder, quando o reranking compensa o custo de latência | Consegue adicionar uma etapa de reranking e justificá-la contra o custo |
| 6. Avaliação e diagnóstico da recuperação | 0010 a 0011 | Recall@k, MRR, diagnosticar qual etapa do pipeline está com defeito | Dado um contexto recuperado errado, consegue nomear a etapa com defeito |
| 7. Da recuperação à geração | 0012 a 0013 | Construção de prompt sobre o contexto recuperado, orçamento da janela de contexto, o que a geração ainda erra | Consegue levar o contexto recuperado até uma resposta gerada e nomear os modos de falha da etapa de geração |
| 8. Transformação do lado da consulta | 0014 | HyDE, reescrita de consulta, expansão multiconsulta, decomposição de consulta | Dada uma falha do lado da consulta que o procedimento da lição 11 não pega, consegue escolher e justificar o remédio certo |
| 9. Filtragem por metadados e recuperação ciente de permissões | 0015 | Filtragem por metadados, pré-filtragem contra pós-filtragem, por que o controle de acesso exige especificamente a pré-filtragem | Consegue projetar um caminho de recuperação ciente de permissões e explicar por que a pós-filtragem é insegura para ele |
| 10. O pipeline de ingestão | 0016 | Parsing de PDFs/HTML/documentos de escritório, extração ciente do layout contra extração ingênua, estrutura de tabelas, propagação em cascata de erros | Consegue explicar por que a ingestão fica a montante do chunking e como um parsing ruim escapa do diagnóstico da lição 11 |
| 11. Atualidade | 0017 | Indexação incremental (HNSW contra IVFFlat), manutenção de exclusões/atualizações, reindexação quando o modelo muda | Consegue planejar para as três formas genuinamente diferentes pelas quais um corpus e seu índice ficam desatualizados |
| 12. Recuperação multi-hop e agêntica | 0018 | O raciocínio e a recuperação intercalados do IRCoT, a decisão de recuperação adaptativa do Self-RAG | Consegue projetar um loop de recuperação para uma pergunta que a decomposição sozinha não responde |
| 13. Custo, latência e monitoramento em produção | 0019 | Orçamento de latência do pipeline inteiro, utilização da janela de contexto, pontuação sem referência, drift de embeddings | Consegue orçar a latência do pipeline completo e monitorar a qualidade da recuperação depois que ele está no ar, sem verdade de referência |
| 14. Julgamento | 0020 | Revisar um pipeline, decidir quando o RAG é a resposta certa contra o contexto longo, nomear o que dá errado | Tem a confiança para revisar o design de recuperação de outra pessoa e explicar exatamente por que uma escolha vai falhar |

## Lições

Siga estas na ordem.

| # | Lição | Ensina |
|---|---|---|
| [0001](lessons/0001-chunking.md) | Chunking | A primeira escolha do pipeline, e a que toda etapa posterior herda |
| [0002](lessons/0002-embedding-models-and-similarity.md) | Modelos de embedding e similaridade | O que um modelo de embedding bi-encoder faz, e por que a métrica de similaridade precisa corresponder a como ele foi treinado |
| [0003](lessons/0003-embedding-dimensionality.md) | Trade-offs de dimensionalidade de embeddings | Por que um vetor de embedding maior não é de graça, e quando é seguro truncá-lo em vez de escolher um modelo menor |
| [0004](lessons/0004-ann-indexes.md) | Índices ANN: HNSW e IVF | Por que a busca vetorial troca exatidão por velocidade, e como IVF e HNSW expõem cada um esse trade-off como um botão ajustável |
| [0005](lessons/0005-pgvector-specifics.md) | Especificidades do pgvector | Montar a busca vetorial no Postgres e mapear os conceitos de índice da lição 4 nos operadores e parâmetros reais do pgvector |
| [0006](lessons/0006-bm25-and-lexical-search.md) | BM25 e busca lexical | O que o BM25 de fato pontua, e por que a correspondência exata de termos ainda pega o que os embeddings semânticos deixam passar |
| [0007](lessons/0007-reciprocal-rank-fusion.md) | Reciprocal rank fusion | Como combinar um ranking lexical e um ranking vetorial sem comparar pontuações incomparáveis, e como ajustar a mistura contra uma métrica medida |
| [0008](lessons/0008-cross-encoder-rerankers.md) | Rerankers cross-encoder | O que um cross-encoder pontua e um bi-encoder não consegue, e por que o reranking é uma segunda etapa e não um substituto da recuperação |
| [0009](lessons/0009-when-reranking-earns-its-cost.md) | Quando o reranking compensa o custo | Um framework de decisão para saber se uma etapa de reranking vale a latência adicional para uma determinada carga de trabalho |
| [0010](lessons/0010-recall-at-k-and-mrr.md) | Recall@k e MRR | As duas métricas padrão de recuperação, o que cada uma diz que a outra não diz, e como escolher o k para a carga de trabalho |
| [0011](lessons/0011-diagnosing-the-pipeline.md) | Diagnosticando o pipeline | Um procedimento etapa por etapa para descobrir qual parte de um pipeline de recuperação é de fato responsável por um contexto recuperado errado |
| [0012](lessons/0012-prompt-construction-and-context-budget.md) | Construção de prompt e orçamento da janela de contexto | Por que os chunks recuperados competem por um orçamento compartilhado da janela de contexto, e por que o lugar onde um chunk fica no prompt importa tanto quanto ele ter sido recuperado |
| [0013](lessons/0013-what-generation-still-gets-wrong.md) | O que a geração ainda erra | Os modos de falha que sobrevivem mesmo a um contexto recuperado correto e bem posicionado, e como eles diferem de uma falha de recuperação |
| [0014](lessons/0014-query-side-transformation.md) | Transformação do lado da consulta | O procedimento de diagnóstico da lição 11 verifica chunking, embedding, o índice, a ponderação híbrida e o reranking, mas nunca a própria consulta, e uma consulta curta demais, composta demais ou formulada de um jeito nada parecido com o corpus precisa de seu próprio remédio, não de mais um ajuste de etapa do pipeline |
| [0015](lessons/0015-metadata-filtering-and-access-control.md) | Filtragem por metadados e recuperação ciente de permissões | Um filtro de controle de acesso que falha não quebra nem parece errado, ele produz uma resposta perfeitamente bem formada construída a partir de um documento que o usuário nunca deveria ter visto, e é exatamente por isso que a pós-filtragem é a escolha errada para este único tipo de filtro |
| [0016](lessons/0016-the-ingestion-pipeline.md) | O pipeline de ingestão | O chunking nunca foi de fato a primeira etapa do pipeline, ele apenas pressupunha que já existia um texto de entrada limpo, e um parsing ruim a montante do chunking corrompe tudo o que vem depois enquanto parece, para todo diagnóstico posterior, uma falha completamente diferente |
| [0017](lessons/0017-freshness.md) | Atualidade | Um corpus que não para de mudar precisa de três respostas genuinamente diferentes, e não de uma, já que adicionar um documento, excluir um e trocar o modelo de embedding quebram cada um uma suposição diferente sobre a qual o índice foi construído |
| [0018](lessons/0018-multi-hop-and-agentic-retrieval.md) | Recuperação multi-hop e agêntica | A decomposição divide uma pergunta composta em subperguntas que você já enxerga no texto original, mas algumas perguntas só revelam sua segunda metade quando a resposta da primeira volta, o que exige um loop de verdade, e não uma divisão inicial mais esperta |
| [0019](lessons/0019-cost-latency-and-production-monitoring.md) | Custo, latência e monitoramento em produção | Um pipeline pode parecer perfeitamente saudável em todo sinal comum de infraestrutura enquanto serve em silêncio uma resposta confiante construída sobre um documento que nunca chegou de fato ao modelo, e é exatamente essa lacuna que o monitoramento específico de recuperação existe para fechar |
| [0020](lessons/0020-reviewing-a-retrieval-pipeline.md) | Revisando um pipeline de recuperação | Revise o pipeline de recuperação de outra pessoa e nomeie especificamente o que ele vai errar antes de ir para produção, e diga quando o próprio RAG (e não uma etapa do pipeline) é a resposta errada para o problema declarado |

## Referência

- [Glossário](GLOSSARY.md): termos canônicos deste tópico
- [Recursos](RESOURCES.md): fontes confiáveis
- [Chunking e Embeddings](reference/chunking-and-embeddings.md): estratégias de chunking, modelos de embedding, métricas de similaridade, trade-offs de dimensionalidade
- [Busca Vetorial e Indexação](reference/vector-search-and-indexing.md): índices ANN (HNSW/IVF), especificidades do pgvector, o trade-off entre recall e latência
- [Busca Híbrida](reference/hybrid-search.md): BM25 mais busca vetorial, reciprocal rank fusion, ajuste da mistura
- [Reranking](reference/reranking.md): rerankers cross-encoder, e quando o reranking compensa o custo de latência
- [Avaliação de Recuperação](reference/retrieval-evaluation.md): Recall@k, MRR, e diagnóstico de qual etapa do pipeline está com defeito
- [Geração a partir da recuperação](reference/generation-from-retrieval.md): construção de prompt sobre o contexto recuperado, orçamento da janela de contexto, modos de falha da etapa de geração

## Como isto funciona

Cada lição é curta e autocontida. Os gabaritos ficam recolhidos: primeiro lembre, depois abra. A prática no mundo real importa mais do que a leitura, e espaçá-la é o ponto. Tudo o que ainda estiver confuso no fim de uma lição vale ser perseguido até a fonte primária antes de seguir adiante.
