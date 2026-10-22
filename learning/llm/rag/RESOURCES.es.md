---
title: "Recursos"
description: "Fuentes de confianza sobre RAG"
type: resources
---

# Recursos de RAG

## Conocimiento

- [Article: "Chunking Strategies for LLM Applications", Pinecone](https://www.pinecone.io/learn/chunking-strategies/)
  Panorama de profesionales sobre los enfoques de chunking (tamaño fijo, recursivo, semántico, consciente de la estructura del documento) y los compromisos que cada uno hace entre contexto y precisión. Úsalo para: elegir y justificar una estrategia de chunking para un corpus dado.
- [Repo: pgvector, pgvector](https://github.com/pgvector/pgvector)
  Repositorio oficial del almacén vectorial que este espacio de trabajo adopta como estándar: tipos de índice (IVFFlat, HNSW), funciones de distancia, los operadores que convierten una tabla de Postgres en un índice vectorial y su propia guía de mantenimiento (reindexar antes de hacer vacuum tras los borrados, la dependencia de IVFFlat de sus datos de entrenamiento). Úsalo para: cómo ejecutar y configurar el propio pgvector, y cómo cada tipo de índice maneja de forma distinta las altas y los borrados incrementales.
- [Paper: "Sentence-BERT: Sentence Embeddings using Siamese BERT-Networks", Reimers and Gurevych, 2019](https://arxiv.org/abs/1908.10084)
  El paper detrás del enfoque de embeddings bi-encoder que usa casi todo pipeline de recuperación: por qué un espacio de embeddings compartido permite calcular la similitud por distancia en lugar de ejecutar el modelo sobre cada par. Úsalo para: entender qué optimiza realmente un modelo de embeddings.
- [Paper: "Passage Re-ranking with BERT", Nogueira and Cho, 2019](https://arxiv.org/abs/1901.04085)
  Introduce el reranking con cross-encoder: puntuar un par consulta-pasaje de forma conjunta en lugar de por distancia entre embeddings, al costo de ejecutar el modelo una vez por candidato. Úsalo para: por qué existe una etapa de reranking y qué aporta frente a la similitud de embeddings por sí sola.
- [Docs: "Reciprocal rank fusion (RRF)", Elasticsearch](https://www.elastic.co/guide/en/elasticsearch/reference/current/rrf.html)
  Explica el método estándar para combinar un ranking de búsqueda por palabras clave y un ranking de búsqueda vectorial en un único ranking híbrido, con la fórmula y su único parámetro de ajuste. Úsalo para: cómo combina realmente la búsqueda híbrida sus dos rankings.
- [Docs: "Reranking", Cohere](https://docs.cohere.com/docs/reranking)
  Documentación orientada a profesionales sobre un reranker cross-encoder alojado: cómo se llama, cuánta latencia cuesta y dónde se sitúa en un pipeline de recuperación. Úsalo para: una etapa de reranking concreta y ejecutable sobre la que razonar junto con el paper de Nogueira y Cho de arriba.
- [Article: "Evaluation Measures for Search and Recommender Systems", Pinecone](https://www.pinecone.io/learn/offline-evaluation/)
  Recorre las métricas estándar de recuperación (Recall@k, MRR, nDCG) y cómo calcular cada una sobre un conjunto de consultas etiquetado o sintético. Úsalo para: medir si se recuperó lo correcto, antes de pasar ese número a `llm/evals` para ver cómo defenderlo.
- [Paper: "Matryoshka Representation Learning", Kusupati et al., 2022](https://arxiv.org/abs/2205.13147)
  Introduce embeddings entrenados para que un prefijo truncado del vector completo siga siendo un embedding significativo y utilizable por sí solo, lo que permite cambiar dimensionalidad por almacenamiento y latencia después del entrenamiento y no solo eligiendo de antemano un modelo más pequeño. Úsalo para: entender cuándo es seguro truncar un vector de embedding y cuándo no.
- [Paper: "Efficient and Robust Approximate Nearest Neighbor Search Using Hierarchical Navigable Small World Graphs", Malkov and Yashunin, 2018](https://arxiv.org/abs/1603.09320)
  El paper detrás de HNSW, el índice de vecinos más cercanos aproximados basado en grafos que usan pgvector y la mayoría de las bases de datos vectoriales: su estructura multicapa y el compromiso entre recall y latencia que controla su parámetro de profundidad de búsqueda. Úsalo para: entender qué hace realmente un índice ANN en lugar de una búsqueda exacta, y por qué su parámetro de ajuste cambia recall por velocidad.
- [Paper: "The Probabilistic Relevance Framework: BM25 and Beyond", Robertson and Zaragoza, 2009](https://www.staff.city.ac.uk/~sbrp622/papers/foundations_bm25_review.pdf)
  La referencia definitiva de BM25, la función de ranking léxico detrás de la puntuación por frecuencia de términos, frecuencia inversa de documentos y normalización por longitud, con el razonamiento detrás de cada uno de sus parámetros. Úsalo para: entender qué puntúa realmente la búsqueda léxica, como complemento de la similitud semántica de la búsqueda vectorial.
- [Paper: "Lost in the Middle: How Language Models Use Long Contexts", Liu et al., 2023](https://arxiv.org/abs/2307.03172)
  Muestra que los modelos usan la información situada al principio o al final de un contexto largo con mucha más fiabilidad que la enterrada en el medio, incluso cuando todo está técnicamente dentro de la ventana de contexto. Úsalo para: entender por qué la posición de un chunk en un prompt ensamblado importa tanto como que el chunk se haya recuperado, y por qué una recuperación que coloca los chunks relevantes cerca del inicio del contexto rinde más que reenviar un corpus entero donde las partes relevantes se hunden en el medio.
- [Paper: "RAGAS: Automated Evaluation of Retrieval Augmented Generation", Es et al., 2023](https://arxiv.org/abs/2309.15217)
  Define la fidelidad (si una afirmación generada está realmente respaldada por el contexto recuperado) como una métrica distinta de la calidad de la recuperación, y cómo comprobarla sin necesitar nuevo ground truth etiquetado por personas para cada respuesta generada. Úsalo para: evaluar si el paso de generación se mantuvo anclado en lo recuperado, una vez confirmado que la recuperación en sí es correcta.

- [Paper: "Precise Zero-Shot Dense Retrieval without Relevance Labels" (HyDE), Gao et al., 2022](https://arxiv.org/abs/2212.10496)
  Introduce generar el embedding de una respuesta hipotética generada en lugar de la propia consulta, de modo que el cuello de botella denso del codificador filtre los errores factuales del documento hipotético y conserve su señal genuina de relevancia. Úsalo para: el mecanismo preciso por el que un documento inventado, a veces erróneo, aun así mejora la recuperación.
- [Paper: "Policy-aware Vector Search: A Vision for Fine Grained Access Control in Vector Databases", Yalamarthi and Pappachan, 2026](https://arxiv.org/abs/2606.19803)
  Formaliza el control de acceso de grano fino como un problema de aplicación de políticas en las bases de datos vectoriales, y la tensión inherente entre una aplicación correcta, el recall de ANN y la latencia de las consultas. Úsalo para: por qué el control de acceso necesita específicamente prefiltrado y no el posfiltrado, más rápido pero que arriesga el recall y la seguridad.
- [Paper: "Docling Technical Report", Auer et al., 2024](https://arxiv.org/abs/2408.09869)
  Introduce un pipeline de análisis de diseño (DocLayNet) y reconocimiento de estructura de tablas (TableFormer) para la conversión de PDF, como alternativa a la extracción ingenua de texto que aplana el diseño y la estructura de las tablas. Úsalo para: qué detecta y reconstruye realmente un pipeline de ingesta consciente del diseño que un extractor de texto plano descarta.
- [Paper: "Interleaving Retrieval with Chain-of-Thought Reasoning for Knowledge-Intensive Multi-Step Questions" (IRCoT), Trivedi et al., 2022](https://arxiv.org/abs/2212.10509)
  Enuncia con precisión por qué la recuperación de una sola pasada falla en las preguntas de varios pasos (qué recuperar depende de lo que ya se ha derivado) y entrelaza un paso de razonamiento con un paso de recuperación para resolverlo. Úsalo para: el mecanismo detrás de un bucle de recuperación donde una consulta posterior depende de la respuesta de un salto anterior.
- [Paper: "Self-RAG: Learning to Retrieve, Generate, and Critique through Self-Reflection", Asai et al., 2023](https://arxiv.org/abs/2310.11511)
  Entrena un modelo para decidir si hace falta recuperar siquiera y para criticar los pasajes recuperados, en lugar de recuperar siempre, de forma indiscriminada, un número fijo de pasajes. Úsalo para: el otro eje de la recuperación agéntica, si recuperar o no, distinto de cuántos saltos necesita una pregunta de varios pasos.
- [Guide: "RAG Observability: How Coralogix Helps You Trace Retrieval-to-Generation Quality", Coralogix, 2026](https://coralogix.com/guides/rag-observability/)
  Cubre por qué la monitorización ordinaria de infraestructura (latencia, throughput, tasa de errores) se mantiene en verde ante fallos silenciosos de recuperación y de ventana de contexto, y las señales sin referencia, de utilización de la ventana de contexto y de deriva de embeddings que los detectan en su lugar. Úsalo para: qué monitorizar realmente una vez que un pipeline está en producción, más allá de las métricas offline que cubre la lección 10.

## Lagunas

- Todavía no hay una fuente sobre el chunking semántico específicamente para corpus estructurados o con mucho código (a diferencia de la prosa), donde las heurísticas de tamaño fijo y de límite de párrafo rinden mal; vale la pena cubrirlo cuando el diseño de las lecciones llegue a la elección de la estrategia de chunking.
