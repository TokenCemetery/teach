---
title: "Búsqueda vectorial e indexación"
description: "El compromiso entre recall y latencia de IVF y HNSW, y los operadores, parámetros de índice y particularidades del orden de construcción de pgvector"
type: reference
---

# Búsqueda vectorial e indexación

La búsqueda de vecinos más cercanos aproximados y su implementación en pgvector. Pensado para consultar al montar o ajustar un índice.

## Por qué la búsqueda exacta no escala

La búsqueda exacta de vecinos más cercanos compara una consulta con cada vector: es lineal en el tamaño del corpus y demasiado lenta con millones de chunks. Un índice de **vecinos más cercanos aproximados (ANN)** acepta una cantidad pequeña y controlable de inexactitud a cambio de tiempos de búsqueda que no crecen de forma lineal.

## IVF y HNSW

| Índice | Mecanismo | Parámetro del tiempo de búsqueda | Costo de construcción |
|---|---|---|---|
| IVF (inverted file) | Divide de antemano los vectores en clústeres (k-means); busca solo en los `nprobe` clústeres más cercanos | `nprobe`: bajo = rápido, puede pasar por alto vecinos cerca del límite de un clúster; alto = se acerca a la búsqueda exacta | Necesita una muestra representativa del corpus para colocar bien los centroides |
| HNSW (hierarchical navigable small world) | Grafo multicapa; capas superiores dispersas para saltos largos, capa inferior densa para una búsqueda local precisa, que se recorre de forma voraz de arriba abajo | `ef_search`: cuántos candidatos se mantienen en cada paso; bajo = rápido pero puede conformarse con un nodo localmente bueno; alto = más recall | Más memoria (aristas del grafo) y una construcción de índice más lenta que IVF |

Ambos parámetros fijan un punto de una **curva de recall y latencia** para un corpus dado; ninguno tiene un ajuste universalmente correcto. HNSW suele alcanzar un mejor punto de esa curva que IVF (mayor recall con la misma latencia), a costa de memoria y de tiempo de construcción. El punto adecuado depende del presupuesto de latencia de la carga de trabajo y de cuánta pérdida de recall puede absorber una etapa posterior (el reranking), medido y no supuesto.

## pgvector: columna, operador, índice

```sql
CREATE EXTENSION vector;
CREATE TABLE chunks (id bigserial PRIMARY KEY, content text, embedding vector(1536));
```

| Operador | Distancia | Clase de operador (para indexar) |
|---|---|---|
| `<->` | Euclidiana/L2 | `vector_l2_ops` |
| `<#>` | Producto interno negativo | `vector_ip_ops` |
| `<=>` | Coseno | `vector_cosine_ops` |

`<#>` es producto interno *negativo* precisamente para que, como los otros dos, menor signifique más similar, y así `ORDER BY` ascendente sea coherente en los tres. El operador tiene que coincidir con [la métrica para la que se entrenó el modelo de embeddings](chunking-and-embeddings.md#similarity-metrics-must-match-training): usar `<=>` con un modelo entrenado para producto punto (o al revés) es ese mismo desajuste de métrica, ahora como una elección concreta de SQL.

```sql
CREATE INDEX ON chunks USING hnsw (embedding vector_cosine_ops) WITH (m = 16, ef_construction = 64);
```

**Un índice se construye para una función de distancia concreta.** Una consulta que ordena por un operador que no coincide con la clase de operador del índice no usa ese índice en absoluto: recurre en silencio a un escaneo secuencial completo y pierde todo el beneficio de rendimiento que el índice existía para dar. No hay conversión automática entre funciones de distancia.

## Los parámetros de pgvector son los de la lección 4, con otros nombres

| Concepto | HNSW | IVFFlat |
|---|---|---|
| Parámetro(s) de construcción | `m` (conexiones máximas por nodo), `ef_construction` (profundidad de búsqueda en la construcción), fijados al hacer `CREATE INDEX` | `lists` (número de clústeres), fijado al hacer `CREATE INDEX` |
| Parámetro de recall y latencia en el momento de la consulta | `SET hnsw.ef_search = 100;` | `SET ivfflat.probes = 10;` (esto es `nprobe`) |

## El orden de construcción importa para IVFFlat, no para HNSW

El paso de clustering de IVFFlat necesita una muestra representativa de los vectores reales de la tabla para colocar bien los centroides: construirlo sobre una tabla vacía o escasa produce clústeres pobres. Carga primero los datos y luego construye el índice IVFFlat. El grafo de HNSW se construye de forma incremental a medida que se insertan vectores, sin una dependencia equivalente, lo que es parte de por qué a menudo se prefiere HNSW para una tabla que se espera que crezca con el tiempo.

## Relacionado

- [Lección 4](../lessons/0004-ann-indexes.md), [Lección 5](../lessons/0005-pgvector-specifics.md)
- [Chunking y embeddings](chunking-and-embeddings.md): los vectores y la métrica de similitud con los que tiene que coincidir el índice de esta hoja
