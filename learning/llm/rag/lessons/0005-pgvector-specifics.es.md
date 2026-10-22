---
title: "5. Particularidades de pgvector"
description: "Montar búsqueda vectorial en Postgres y trasladar los conceptos de índice de la lección 4 a los operadores y parámetros reales de pgvector"
type: lesson
---

# Lección 5. Particularidades de pgvector

**Vínculo con la misión:** Esta es la lección que cierra la etapa 3: los conceptos de IVF y HNSW de la lección 4 se convierten aquí en un esquema real, un operador de distancia real y parámetros de ajuste reales, sobre el almacén vectorial que este espacio de trabajo adopta como estándar.
**Fuente principal:** [Repo: pgvector, pgvector](https://github.com/pgvector/pgvector)
**Requisitos previos:** [Lección 4](0004-ann-indexes.md), [Chunk](../GLOSSARY.md)

## Calentamiento

1. ▢ ¿Qué controlan, respectivamente, el parámetro `nprobe` de IVF y el parámetro `ef_search` de HNSW?

<details markdown="1"><summary>Comprobación</summary>

`nprobe` fija en cuántos de los clústeres de IVF se busca en el momento de la consulta; `ef_search` fija cuántos candidatos mantiene en cada paso la búsqueda en el grafo de HNSW. Ambos cambian recall por latencia: los valores más altos buscan más y mejoran el recall a costa de latencia.

</details>

2. ▢ ¿Por qué la similitud coseno y el producto punto producen el mismo ranking solo cuando los vectores de embedding están normalizados a longitud unitaria?

<details markdown="1"><summary>Comprobación</summary>

El producto punto es la similitud coseno escalada por las magnitudes de los dos vectores. Cuando ambas están fijas en longitud unitaria, ese factor de escala es idéntico para cada par, así que los rankings coinciden; cuando las magnitudes varían, el producto punto favorece a los vectores más grandes.

</details>

## Qué debes saber

### Una columna vectorial y un operador de distancia

pgvector añade a Postgres un tipo de columna `vector(N)`, dimensionado según la dimensionalidad de embedding que fijó la lección 3:

```sql
CREATE EXTENSION vector;
CREATE TABLE chunks (id bigserial PRIMARY KEY, content text, embedding vector(1536));
```

La similitud se calcula con uno de tres operadores: `<->` (distancia euclidiana/L2), `<#>` (producto interno negativo) y `<=>` (distancia coseno). El operador tiene que coincidir con la métrica para la que se entrenó el modelo de embeddings (lección 2): usar `<=>` con un modelo entrenado para producto punto sin normalizar, o al revés, es exactamente el desajuste que la lección 2 advirtió que degrada la calidad del ranking, ahora expresado como una elección concreta de SQL y no como una abstracta. Fíjate en el signo de `<#>`: es producto interno negativo precisamente para que, como los otros dos operadores, menor signifique más similar, y así `ORDER BY` ascendente sea coherente en los tres.

### Un índice hay que construirlo para una función de distancia concreta

Crear un índice significa elegir una clase de operador que coincida con la función de distancia prevista:

```sql
CREATE INDEX ON chunks USING hnsw (embedding vector_cosine_ops) WITH (m = 16, ef_construction = 64);
```

`vector_cosine_ops`, `vector_l2_ops` y `vector_ip_ops` construyen cada una el índice para un operador concreto. Un índice construido con `vector_l2_ops` no acelera una consulta que ordena por `<=>` (distancia coseno); la clase de operador y el operador de la consulta tienen que coincidir, o el índice no se usa y la consulta recurre en silencio a un escaneo secuencial completo, lo que anula el sentido mismo de construir el índice.

### Los nombres de parámetros de pgvector son los parámetros de la lección 4 con otros nombres

Los parámetros de construcción del índice HNSW, `m` (conexiones máximas por nodo) y `ef_construction` (profundidad de búsqueda en la construcción), son exactamente los parámetros de ajuste de HNSW de la lección 4, fijados al hacer `CREATE INDEX`. Su parámetro de recall y latencia en el momento de la consulta es un ajuste de sesión: `SET hnsw.ef_search = 100;`, el `ef_search` de la lección 4 con otro nombre. El parámetro de construcción de IVFFlat es `lists` (el número de clústeres que señaló la lección 4), fijado del mismo modo al crear el índice, y su parámetro en el momento de la consulta es `SET ivfflat.probes = 10;`, el `nprobe` de la lección 4.

### IVFFlat necesita datos antes de construirse bien; HNSW no

El paso de clustering de IVFFlat necesita una muestra representativa de los vectores reales de la tabla para colocar bien sus centroides de clúster, lo que significa que construir un índice IVFFlat sobre una tabla vacía o apenas poblada produce clústeres pobres que no reflejan la distribución real de vectores del corpus. La consecuencia práctica: carga primero los datos y luego construye el índice IVFFlat. La estructura de grafo de HNSW se construye de forma incremental a medida que se insertan vectores, sin una dependencia equivalente de que la tabla ya esté poblada, lo que es parte de por qué a menudo se prefiere HNSW para una tabla que se espera que crezca con el tiempo, además de la ventaja de recall y latencia que la lección 4 ya describió.

## Práctica

1. ▢ Un modelo de embeddings se entrenó para que la similitud coseno refleje la cercanía semántica. ¿Qué operador y qué clase de operador de pgvector deberían usar tanto la consulta como su índice?

<details markdown="1"><summary>Comprobación</summary>

El operador `<=>` (distancia coseno) para la consulta, y `vector_cosine_ops` para el índice. Usar un operador o una clase de operador construidos para una función de distancia distinta de aquella con la que se entrenó el modelo reintroduce el problema de desajuste de métrica de la lección 2, ahora como un desajuste concreto de SQL.

</details>

2. ▢ Un equipo construye un índice HNSW con `vector_l2_ops`, pero sus consultas ordenan los resultados con el operador `<=>` (distancia coseno). ¿Qué pasa y por qué es un problema más allá de "la respuesta equivocada"?

<details markdown="1"><summary>Pista</summary>

Piensa en si el índice puede usarse siquiera para una consulta cuyo operador no coincide con la clase de operador con la que se construyó.

</details>

<details markdown="1"><summary>Comprobación</summary>

El índice construido para `vector_l2_ops` no acelera una consulta que usa `<=>`, ya que el índice se construye para una función de distancia concreta. La consulta recurre a un escaneo secuencial completo de la tabla, que es lento con cualquier tamaño real de corpus; no es solo un riesgo de respuesta equivocada, es perder todo el beneficio de rendimiento que el índice existía para dar.

</details>

3. ▢ Una tabla tiene un índice IVFFlat con `lists = 1000`, pero el ajuste en el momento de la consulta `ivfflat.probes` se deja en su valor por defecto de 1. ¿Qué significa esto para el compromiso entre recall y latencia, en términos del `nprobe` de la lección 4?

<details markdown="1"><summary>Comprobación</summary>

`ivfflat.probes = 1` es `nprobe = 1`: solo se busca en el clúster más cercano de los 1,000. Ese es el extremo más rápido y de menor recall del compromiso de la lección 4; una consulta cercana al límite de un clúster puede pasar por alto vecinos más cercanos reales que están en un clúster adyacente. Subir `probes` busca en más clústeres, cambia latencia de consulta por mayor recall.

</details>

4. ▢ ¿Por qué el orden de construcción importa para un índice IVFFlat (cargar los datos, luego construir) pero no para HNSW?

<details markdown="1"><summary>Comprobación</summary>

El paso de clustering de IVFFlat necesita una muestra representativa de los vectores reales de la tabla para colocar bien sus centroides de clúster; construirlo sobre una tabla vacía o escasamente poblada produce clústeres pobres que no reflejan la distribución real de los datos. El grafo de HNSW se construye de forma incremental a medida que se insertan vectores, sin una necesidad equivalente de que la tabla ya contenga primero una muestra representativa.

</details>

5. ▢ ¿Qué afirmación es cierta sobre las clases de operador de pgvector (`vector_cosine_ops`, `vector_l2_ops`, `vector_ip_ops`)?

    - a) Cualquier clase de operador funciona con cualquier operador de consulta, ya que pgvector convierte entre funciones de distancia automáticamente
    - b) La clase de operador de un índice debe coincidir con el operador de distancia de la consulta, o el índice no se usará para esa consulta
    - c) La clase de operador solo afecta a los índices HNSW, no a IVFFlat
    - d) `vector_ip_ops` no puede usarse con vectores de embedding normalizados

<details markdown="1"><summary>Comprobación</summary>

**b)** La clase de operador y el operador de la consulta tienen que coincidir, o la consulta recurre a un escaneo secuencial en lugar de usar el índice. (a) es falsa: no hay conversión automática entre funciones de distancia. (c) es falsa: ambos tipos de índice exigen hacer coincidir una clase de operador con la función de distancia. (d) es falsa: los vectores normalizados son justo el caso en que el producto interno y la distancia coseno coinciden, como cubrió la lección 2.

</details>

## Prácticas en el mundo real

- [ ] Crea una tabla pequeña de pgvector con una columna `vector(N)` dimensionada según un modelo de embeddings que uses, y construye un índice con la clase de operador que coincida con la métrica de similitud con la que se entrenó ese modelo.
- [ ] Ejecuta `EXPLAIN` sobre una consulta de similitud contra tu tabla y confirma que el índice se está usando de verdad y no recurre a un escaneo secuencial.
- [ ] Mañana: prueba dos valores distintos de `ivfflat.probes` o `hnsw.ef_search` con la misma consulta y compara tanto los resultados devueltos como la latencia de la consulta.

## Para profundizar

- [Repo: pgvector, pgvector](https://github.com/pgvector/pgvector)
- [Paper: "Efficient and Robust Approximate Nearest Neighbor Search Using Hierarchical Navigable Small World Graphs", Malkov and Yashunin, 2018](https://arxiv.org/abs/1603.09320)
- [Recursos](../RESOURCES.md)

---

¿No termina de quedar claro? Vuelve a leer la fuente principal de arriba, ya que esta lección la comprime y en la compresión es donde se escapa la comprensión. Consulta el [glosario](../GLOSSARY.md) por si algún término te resultó resbaladizo.

Si lo poco claro es la propia lección y no el material, eso es un defecto: [abre un issue](https://github.com/TokenCemetery/teach/issues).
