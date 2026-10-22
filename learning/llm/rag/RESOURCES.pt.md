---
title: "Recursos"
description: "Fontes confiáveis sobre RAG"
type: resources
---

# Recursos de RAG

## Conhecimento

- [Artigo: "Chunking Strategies for LLM Applications", Pinecone](https://www.pinecone.io/learn/chunking-strategies/)
  Panorama de profissionais sobre abordagens de chunking (tamanho fixo, recursivo, semântico, ciente da estrutura do documento) e os trade-offs que cada uma faz entre contexto e precisão. Use para: escolher e justificar uma estratégia de chunking para um determinado corpus.
- [Repositório: pgvector, pgvector](https://github.com/pgvector/pgvector)
  Repositório oficial do vector store que este workspace adota como padrão: tipos de índice (IVFFlat, HNSW), funções de distância, os operadores que transformam uma tabela do Postgres em um índice vetorial e sua própria orientação de manutenção (reindexar antes de fazer vacuum após exclusões, a dependência do IVFFlat em relação aos dados de treinamento). Use para: como executar e configurar o próprio pgvector, e como cada tipo de índice trata adições e exclusões incrementais de forma diferente.
- [Artigo científico: "Sentence-BERT: Sentence Embeddings using Siamese BERT-Networks", Reimers e Gurevych, 2019](https://arxiv.org/abs/1908.10084)
  O artigo por trás da abordagem de embedding bi-encoder que quase todo pipeline de recuperação usa: por que um espaço de embedding compartilhado permite calcular a similaridade por distância, em vez de rodar o modelo em cada par. Use para: entender o que um modelo de embedding de fato otimiza.
- [Artigo científico: "Passage Re-ranking with BERT", Nogueira e Cho, 2019](https://arxiv.org/abs/1901.04085)
  Introduz o reranking com cross-encoder: pontuar um par consulta-passagem em conjunto, em vez de pela distância entre embeddings, ao custo de rodar o modelo uma vez por candidato. Use para: por que existe uma etapa de reranking e o que ela traz além da similaridade de embeddings sozinha.
- [Docs: "Reciprocal rank fusion (RRF)", Elasticsearch](https://www.elastic.co/guide/en/elasticsearch/reference/current/rrf.html)
  Explica o método padrão para combinar um ranking de busca por palavras-chave e um ranking de busca vetorial em um único ranking híbrido, com a fórmula e seu único parâmetro de ajuste. Use para: como a busca híbrida de fato combina seus dois rankings.
- [Docs: "Reranking", Cohere](https://docs.cohere.com/docs/reranking)
  Documentação voltada a profissionais sobre um reranker cross-encoder hospedado: como é chamado, o que custa em latência e onde fica em um pipeline de recuperação. Use para: uma etapa de reranking concreta e executável para raciocinar junto com o artigo de Nogueira e Cho acima.
- [Artigo: "Evaluation Measures for Search and Recommender Systems", Pinecone](https://www.pinecone.io/learn/offline-evaluation/)
  Percorre as métricas padrão de recuperação (Recall@k, MRR, nDCG) e como calcular cada uma contra um conjunto de consultas rotulado ou sintético. Use para: medir se a coisa certa foi recuperada, antes de entregar esse número a `llm/evals` para saber como defendê-lo.
- [Artigo científico: "Matryoshka Representation Learning", Kusupati et al., 2022](https://arxiv.org/abs/2205.13147)
  Introduz embeddings treinados de modo que um prefixo truncado do vetor completo continue sendo um embedding significativo e utilizável por si só, permitindo trocar dimensionalidade por armazenamento e latência depois do treinamento, e não apenas escolhendo de antemão um modelo menor. Use para: entender quando é seguro truncar um vetor de embedding e quando não é.
- [Artigo científico: "Efficient and Robust Approximate Nearest Neighbor Search Using Hierarchical Navigable Small World Graphs", Malkov e Yashunin, 2018](https://arxiv.org/abs/1603.09320)
  O artigo por trás do HNSW, o índice de vizinho mais próximo aproximado baseado em grafo que o pgvector e a maioria dos bancos de dados vetoriais usam: sua estrutura multicamada e o trade-off entre recall e latência que seu parâmetro de profundidade de busca controla. Use para: entender o que um índice ANN de fato faz no lugar da busca exata e por que seu botão de ajuste troca recall por velocidade.
- [Artigo científico: "The Probabilistic Relevance Framework: BM25 and Beyond", Robertson e Zaragoza, 2009](https://www.staff.city.ac.uk/~sbrp622/papers/foundations_bm25_review.pdf)
  A referência definitiva sobre o BM25, a função de ranking lexical por trás da pontuação por frequência de termo, frequência inversa de documento e normalização de tamanho, com o raciocínio por trás de cada um de seus parâmetros. Use para: entender o que a busca lexical de fato pontua, como complemento à similaridade semântica da busca vetorial.
- [Artigo científico: "Lost in the Middle: How Language Models Use Long Contexts", Liu et al., 2023](https://arxiv.org/abs/2307.03172)
  Mostra que os modelos usam a informação colocada no início ou no fim de um contexto longo de forma muito mais confiável do que a informação enterrada no meio, mesmo quando tudo está tecnicamente dentro da janela de contexto. Use para: entender por que a posição de um chunk em um prompt montado importa tanto quanto ele ter sido recuperado, e por que uma recuperação que coloca os chunks relevantes perto do topo do contexto supera reenviar um corpus inteiro, no qual as partes relevantes afundam no meio.
- [Artigo científico: "RAGAS: Automated Evaluation of Retrieval Augmented Generation", Es et al., 2023](https://arxiv.org/abs/2309.15217)
  Define a fidelidade (se uma afirmação gerada é de fato sustentada pelo contexto recuperado) como uma métrica distinta da qualidade da recuperação, e como verificá-la sem precisar de uma nova verdade de referência rotulada por humanos para cada resposta gerada. Use para: avaliar se a etapa de geração se manteve ancorada no que foi recuperado, depois de confirmado que a própria recuperação está correta.

- [Artigo científico: "Precise Zero-Shot Dense Retrieval without Relevance Labels" (HyDE), Gao et al., 2022](https://arxiv.org/abs/2212.10496)
  Introduz gerar o embedding de uma resposta hipotética gerada em vez da própria consulta, deixando o gargalo denso do encoder filtrar os erros factuais do documento hipotético e manter seu sinal genuíno de relevância. Use para: o mecanismo preciso que explica por que um documento inventado, às vezes errado, ainda melhora a recuperação.
- [Artigo científico: "Policy-aware Vector Search: A Vision for Fine Grained Access Control in Vector Databases", Yalamarthi e Pappachan, 2026](https://arxiv.org/abs/2606.19803)
  Formaliza o controle de acesso refinado como um problema de imposição em bancos de dados vetoriais e a tensão inerente entre imposição correta, recall de ANN e latência de consulta. Use para: por que o controle de acesso exige especificamente a pré-filtragem, e não a pós-filtragem, mais rápida porém arriscada para o recall e para a segurança.
- [Artigo científico: "Docling Technical Report", Auer et al., 2024](https://arxiv.org/abs/2408.09869)
  Introduz um pipeline de análise de layout (DocLayNet) e reconhecimento de estrutura de tabelas (TableFormer) para conversão de PDF, como alternativa à extração ingênua de texto que achata o layout e a estrutura das tabelas. Use para: o que um pipeline de ingestão ciente do layout de fato detecta e reconstrói e que um extrator de texto simples descarta.
- [Artigo científico: "Interleaving Retrieval with Chain-of-Thought Reasoning for Knowledge-Intensive Multi-Step Questions" (IRCoT), Trivedi et al., 2022](https://arxiv.org/abs/2212.10509)
  Enuncia com precisão por que a recuperação em uma única passada falha em perguntas de vários passos (o que recuperar depende do que já foi derivado) e intercala um passo de raciocínio com um passo de recuperação para resolvê-las. Use para: o mecanismo por trás de um loop de recuperação em que uma consulta posterior depende da resposta de um hop anterior.
- [Artigo científico: "Self-RAG: Learning to Retrieve, Generate, and Critique through Self-Reflection", Asai et al., 2023](https://arxiv.org/abs/2310.11511)
  Treina um modelo para decidir se a recuperação é necessária e para criticar as passagens recuperadas, em vez de recuperar indiscriminadamente um número fixo de passagens toda vez. Use para: o outro eixo da recuperação agêntica, se vale recuperar, distinto de quantos hops uma pergunta de vários passos exige.
- [Guia: "RAG Observability: How Coralogix Helps You Trace Retrieval-to-Generation Quality", Coralogix, 2026](https://coralogix.com/guides/rag-observability/)
  Cobre por que o monitoramento comum de infraestrutura (latência, throughput, taxa de erro) continua verde diante de falhas silenciosas de recuperação e de janela de contexto, e os sinais sem referência, de utilização da janela de contexto e de drift de embeddings que as detectam. Use para: o que de fato monitorar depois que um pipeline está no ar, além das métricas offline que a lição 10 cobre.

## Lacunas

- Ainda não há fonte sobre chunking semântico especificamente para corpora estruturados ou com muito código (em oposição à prosa), nos quais as heurísticas de tamanho fixo e de fronteira de parágrafo têm desempenho ruim; vale fechar esta lacuna quando o design das lições chegar à escolha da estratégia de chunking.
