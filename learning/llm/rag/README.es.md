---
title: "RAG"
description: "Domina la recuperación: chunking, embeddings, búsqueda híbrida, reranking y medir si se recuperó lo correcto"
type: topic
---

# Aprendizaje: RAG

Sé capaz de diseñar un pipeline de recuperación para un corpus y un caso de uso reales, y de diagnosticar por qué un sistema RAG existente devuelve el contexto equivocado en lugar de adivinar una corrección.

**Última lección:** [20. Revisar un pipeline de recuperación](lessons/0020-reviewing-a-retrieval-pipeline.md)

## Cómo se ve el éxito

- Diseñar un pipeline de recuperación (chunking, embeddings, búsqueda híbrida, reranking) para un corpus y un caso de uso dados, y justificar cada decisión frente a ellos.
- Ante un sistema RAG que devuelve contexto erróneo o irrelevante, diagnosticar qué etapa del pipeline es la culpable en lugar de reajustar al azar.
- Ajustar los pesos de la búsqueda híbrida contra una métrica de recuperación medida y no a ojo.
- Llevar el contexto recuperado hasta una respuesta generada y dar cuenta de lo que el propio paso de generación todavía puede hacer mal.
- Revisar el diseño del pipeline de recuperación de otra persona y nombrar con precisión lo que hará mal antes de enviarlo a producción, y decir cuándo RAG en sí (no una etapa del pipeline) es la respuesta equivocada al problema planteado.

## Restricciones

- Se asume Python básico y familiaridad con lo que es un embedding; no se requiere experiencia previa con sistemas de recuperación.
- Almacén vectorial: pgvector, de modo que los conceptos conectan con lo que cubre `data/postgres` sobre lo que un índice vectorial le cuesta a la base de datos.

## Fuera de alcance

- La técnica de ingeniería de prompts y la calidad de la generación en general: consulta [`llm/prompting`](../../llm/prompting/). Aquí solo se toca en cuanto a cómo llega el contexto recuperado al paso de generación, sin reformularlo como tema propio.
- Cómo se construye y se defiende la propia métrica de recuperación: consulta [`llm/evals`](../../llm/evals/), enlazado en lugar de repetido.
- Lo que cuesta operativamente un índice vectorial a la base de datos: consulta [`data/postgres`](../../data/postgres/), enlazado en lugar de repetido.

## El arco

Catorce etapas, desde el primer chunk hasta un pipeline de producción diagnosticado, consciente del costo y monitorizado, con un cierre de criterio. Una etapa abarca varias lecciones y los límites son difusos; lo que da una etapa por terminada es la capacidad, no el número de lecciones.

| Etapa | Lecciones | Cubre | Terminada cuando |
|---|---|---|---|
| 1. Chunking | 0001 | La primera decisión del pipeline, la que heredan todas las etapas posteriores | Puedes hacer chunking de un corpus dado y justificar la decisión |
| 2. Embeddings | 0002 a 0003 | Modelos de embeddings, métricas de similitud, compromisos de la dimensionalidad | Puedes elegir un modelo de embeddings y una métrica para un corpus dado |
| 3. Búsqueda vectorial e indexación | 0004 a 0005 | Índices ANN (HNSW/IVF), particularidades de pgvector, el compromiso entre recall y latencia | Puedes montar búsqueda vectorial sobre pgvector para el corpus con chunks |
| 4. Búsqueda híbrida | 0006 a 0007 | BM25 más búsqueda vectorial, reciprocal rank fusion, ajustar la mezcla | Puedes ajustar los pesos de la búsqueda híbrida contra una métrica de recuperación medida |
| 5. Reranking | 0008 a 0009 | Rerankers cross-encoder, cuándo el reranking justifica su costo de latencia | Puedes añadir una etapa de reranking y justificarla frente al costo |
| 6. Evaluación de la recuperación y diagnóstico | 0010 a 0011 | Recall@k, MRR, diagnosticar qué etapa del pipeline es la culpable | Dado un contexto recuperado erróneo, puedes nombrar la etapa culpable |
| 7. De la recuperación a la generación | 0012 a 0013 | Construcción del prompt sobre el contexto recuperado, presupuesto de la ventana de contexto, lo que la generación todavía hace mal | Puedes llevar el contexto recuperado hasta una respuesta generada y nombrar los modos de fallo de la etapa de generación |
| 8. Transformación del lado de la consulta | 0014 | HyDE, reescritura de consultas, expansión de consulta múltiple, descomposición de consultas | Ante un fallo del lado de la consulta que el procedimiento de la lección 11 no detecta, puedes elegir y justificar el remedio correcto |
| 9. Filtrado por metadatos y recuperación consciente de permisos | 0015 | Filtrado por metadatos, prefiltrado frente a posfiltrado, por qué el control de acceso necesita específicamente prefiltrado | Puedes diseñar una vía de recuperación consciente de permisos y explicar por qué el posfiltrado no es seguro para ella |
| 10. El pipeline de ingesta | 0016 | Analizar PDF/HTML/documentos de ofimática, extracción consciente del diseño frente a extracción ingenua, estructura de tablas, cascada de errores | Puedes explicar por qué la ingesta está antes que el chunking y cómo un mal análisis escapa al diagnóstico de la lección 11 |
| 11. Frescura | 0017 | Indexación incremental (HNSW frente a IVFFlat), mantenimiento de borrados y actualizaciones, reindexación al cambiar de modelo | Puedes planificar las tres formas genuinamente distintas en que un corpus y su índice se quedan obsoletos |
| 12. Recuperación multi-hop y agéntica | 0018 | El razonamiento y la recuperación entrelazados de IRCoT, la decisión de recuperación adaptativa de Self-RAG | Puedes diseñar un bucle de recuperación para una pregunta que la descomposición por sí sola no puede responder |
| 13. Costo, latencia y monitorización en producción | 0019 | Presupuesto de latencia de todo el pipeline, utilización de la ventana de contexto, puntuación sin referencia, deriva de embeddings | Puedes presupuestar la latencia de todo el pipeline y monitorizar la calidad de la recuperación una vez en producción, sin ground truth |
| 14. Criterio | 0020 | Revisar un pipeline, zanjar cuándo RAG es la respuesta correcta frente al contexto largo, nombrar lo que sale mal | Se confía en ti para revisar el diseño de recuperación de otra persona y explicar con exactitud por qué una decisión fallará |

## Lecciones

Recórrelas en orden.

| # | Lección | Enseña |
|---|---|---|
| [0001](lessons/0001-chunking.md) | Chunking | La primera decisión del pipeline, la que heredan todas las etapas posteriores |
| [0002](lessons/0002-embedding-models-and-similarity.md) | Modelos de embeddings y similitud | Qué hace un modelo de embeddings bi-encoder, y por qué la métrica de similitud tiene que coincidir con cómo se entrenó |
| [0003](lessons/0003-embedding-dimensionality.md) | Compromisos de la dimensionalidad de los embeddings | Por qué un vector de embedding más grande no es gratis, y cuándo es seguro truncarlo en lugar de elegir un modelo más pequeño |
| [0004](lessons/0004-ann-indexes.md) | Índices ANN: HNSW e IVF | Por qué la búsqueda vectorial cambia exactitud por velocidad, y cómo IVF y HNSW exponen cada uno ese compromiso como un parámetro ajustable |
| [0005](lessons/0005-pgvector-specifics.md) | Particularidades de pgvector | Montar búsqueda vectorial en Postgres y trasladar los conceptos de índice de la lección 4 a los operadores y parámetros reales de pgvector |
| [0006](lessons/0006-bm25-and-lexical-search.md) | BM25 y búsqueda léxica | Qué puntúa realmente BM25, y por qué la coincidencia exacta de términos todavía detecta lo que los embeddings semánticos pasan por alto |
| [0007](lessons/0007-reciprocal-rank-fusion.md) | Reciprocal Rank Fusion | Cómo combinar un ranking léxico y un ranking vectorial sin comparar puntuaciones incomparables, y cómo ajustar la mezcla contra una métrica medida |
| [0008](lessons/0008-cross-encoder-rerankers.md) | Rerankers cross-encoder | Qué puntúa un cross-encoder que un bi-encoder no puede, y por qué el reranking es una segunda etapa y no un reemplazo de la recuperación |
| [0009](lessons/0009-when-reranking-earns-its-cost.md) | Cuándo un reranking justifica su costo | Un marco de decisión para saber si una etapa de reranking vale su latencia añadida en una carga de trabajo dada |
| [0010](lessons/0010-recall-at-k-and-mrr.md) | Recall@k y MRR | Las dos métricas estándar de recuperación, qué te dice cada una que la otra no, y cómo elegir k para la carga de trabajo |
| [0011](lessons/0011-diagnosing-the-pipeline.md) | Diagnosticar el pipeline | Un procedimiento etapa por etapa para encontrar qué parte de un pipeline de recuperación es realmente responsable de un contexto recuperado erróneo |
| [0012](lessons/0012-prompt-construction-and-context-budget.md) | Construcción del prompt y presupuesto de la ventana de contexto | Por qué los chunks recuperados compiten por un presupuesto compartido de la ventana de contexto, y por qué el lugar que ocupa un chunk en el prompt importa tanto como que se haya recuperado |
| [0013](lessons/0013-what-generation-still-gets-wrong.md) | Lo que la generación todavía hace mal | Los modos de fallo que sobreviven incluso a un contexto recuperado correcto y bien colocado, y en qué se diferencian de un fallo de recuperación |
| [0014](lessons/0014-query-side-transformation.md) | Transformación del lado de la consulta | El procedimiento de diagnóstico de la lección 11 revisa el chunking, el embedding, el índice, la ponderación híbrida y el reranking, pero nunca la consulta en sí, y una consulta demasiado corta, demasiado compuesta o redactada de forma muy distinta al corpus necesita su propio remedio, no otra corrección de una etapa del pipeline |
| [0015](lessons/0015-metadata-filtering-and-access-control.md) | Filtrado por metadatos y recuperación consciente de permisos | Un filtro de control de acceso que falla no se cae y no parece estar mal: produce una respuesta perfectamente bien formada construida a partir de un documento que el usuario nunca debió ver, y por eso mismo el posfiltrado es la elección equivocada para este único tipo de filtro |
| [0016](lessons/0016-the-ingestion-pipeline.md) | El pipeline de ingesta | El chunking nunca fue en realidad la primera etapa del pipeline, solo asumía que ya existía texto de entrada limpio, y un mal análisis antes del chunking corrompe todo lo que viene después mientras parece, para cualquier diagnóstico posterior, un fallo completamente distinto |
| [0017](lessons/0017-freshness.md) | Frescura | Un corpus que no deja de cambiar necesita tres respuestas genuinamente distintas, no una, ya que añadir un documento, borrar uno y cambiar el modelo de embeddings rompen cada uno una suposición distinta sobre la que se construyó el índice |
| [0018](lessons/0018-multi-hop-and-agentic-retrieval.md) | Recuperación multi-hop y agéntica | La descomposición divide una pregunta compuesta en subpreguntas que ya se ven en el texto original, pero algunas preguntas solo revelan su segunda mitad cuando vuelve la respuesta de la primera, lo que requiere un bucle de verdad, no una división inicial más inteligente |
| [0019](lessons/0019-cost-latency-and-production-monitoring.md) | Costo, latencia y monitorización en producción | Un pipeline puede verse perfectamente sano en todas las señales ordinarias de infraestructura mientras sirve en silencio una respuesta segura construida sobre un documento que nunca llegó al modelo, y esa brecha es exactamente la que la monitorización específica de recuperación existe para cerrar |
| [0020](lessons/0020-reviewing-a-retrieval-pipeline.md) | Revisar un pipeline de recuperación | Revisar el diseño del pipeline de recuperación de otra persona y nombrar con precisión lo que hará mal antes de enviarlo a producción, y decir cuándo RAG en sí (no una etapa del pipeline) es la respuesta equivocada al problema planteado |

## Referencia

- [Glosario](GLOSSARY.md): términos canónicos de este tema
- [Recursos](RESOURCES.md): fuentes de confianza
- [Chunking y embeddings](reference/chunking-and-embeddings.md): estrategias de chunking, modelos de embeddings, métricas de similitud, compromisos de la dimensionalidad
- [Búsqueda vectorial e indexación](reference/vector-search-and-indexing.md): índices ANN (HNSW/IVF), particularidades de pgvector, el compromiso entre recall y latencia
- [Búsqueda híbrida](reference/hybrid-search.md): BM25 más búsqueda vectorial, reciprocal rank fusion, ajustar la mezcla
- [Reranking](reference/reranking.md): rerankers cross-encoder y cuándo el reranking justifica su costo de latencia
- [Evaluación de la recuperación](reference/retrieval-evaluation.md): Recall@k, MRR y diagnosticar qué etapa del pipeline es la culpable
- [Generación a partir de la recuperación](reference/generation-from-retrieval.md): construcción del prompt sobre el contexto recuperado, presupuesto de la ventana de contexto, modos de fallo de la etapa de generación

## Cómo funciona

Cada lección es corta y autocontenida. Las claves de respuesta están plegadas: primero recuerda, luego ábrelas. Las prácticas en el mundo real importan más que la lectura, y espaciarlas es el punto. Todo lo que siga sin estar claro al final de una lección merece rastrearse hasta su fuente primaria antes de seguir.
