---
title: "4. Índices ANN: HNSW e IVF"
description: "Por qué la búsqueda vectorial cambia exactitud por velocidad, y cómo IVF y HNSW exponen cada uno ese compromiso como un parámetro ajustable"
type: lesson
---

# Lección 4. Índices ANN: HNSW e IVF

**Vínculo con la misión:** La etapa 3 abre la parte de la misión que consiste en montar la búsqueda sobre un corpus real: un índice es lo que hace que la búsqueda vectorial sea lo bastante rápida como para ejecutarse siquiera, a costa de un compromiso entre recall y latencia que esta lección nombra antes de que la lección 5 lo haga concreto en pgvector.
**Fuente principal:** [Paper: "Efficient and Robust Approximate Nearest Neighbor Search Using Hierarchical Navigable Small World Graphs", Malkov and Yashunin, 2018](https://arxiv.org/abs/1603.09320)
**Requisitos previos:** [Lección 3](0003-embedding-dimensionality.md), [Chunk](../GLOSSARY.md)

## Calentamiento

1. ▢ Un corpus tiene 2 millones de chunks. ¿Cuánto almacenamiento ocupan, aproximadamente, sus embeddings a 1536 dimensiones en float32, frente a 256 dimensiones?

<details markdown="1"><summary>Comprobación</summary>

Unos 12.3 GB a 1536 dimensiones frente a unos 2.0 GB a 256 dimensiones, ya que los bytes por vector crecen de forma lineal con el número de dimensiones (`dimensiones × 4 bytes`).

</details>

2. ▢ ¿Qué te permite hacer Matryoshka Representation Learning con un vector de embedding que un modelo de embeddings estándar no permite con seguridad?

<details markdown="1"><summary>Comprobación</summary>

Truncarlo a menos dimensiones después del entrenamiento, con un costo de calidad acotado y predecible, ya que los prefijos de un modelo entrenado con MRL son a su vez embeddings con significado. Las dimensiones de un modelo estándar no están ordenadas por importancia, así que truncar uno es impredecible.

</details>

## Qué debes saber

### Por qué la búsqueda exacta no escala

Encontrar de forma exacta los vecinos más cercanos reales de una consulta significa compararla con cada vector del corpus. Eso es lineal en el tamaño del corpus: duplicar el corpus duplica el tiempo de búsqueda, y con millones de chunks la comparación por fuerza bruta se vuelve demasiado lenta para ejecutarse en el momento de la consulta. Un índice de **vecinos más cercanos aproximados (ANN)** acepta una cantidad pequeña y controlable de inexactitud: devuelve vectores que con mucha probabilidad están cerca de los vecinos más cercanos reales, sin garantía de que sean exactamente ellos, a cambio de tiempos de búsqueda que no crecen de forma lineal con el tamaño del corpus.

### IVF: buscar solo en los clústeres cercanos

**IVF (inverted file index)** divide de antemano el espacio vectorial en clústeres (normalmente con k-means) y asigna cada vector al centroide de clúster más cercano. En el momento de la consulta, en lugar de escanear todos los vectores, IVF busca solo en los `nprobe` clústeres más cercanos a la consulta, donde `nprobe` es un número ajustable. Un `nprobe` bajo (buscar solo en el clúster más cercano) es rápido pero corre el riesgo de pasar por alto vecinos reales que están en un clúster contiguo cerca del límite. Un `nprobe` alto (buscar en muchos clústeres o en todos) se acerca al recall de la búsqueda exacta al costo de la búsqueda exacta. IVF también tiene un costo de construcción único: el paso de clustering necesita una muestra representativa de los vectores del corpus para colocar bien los centroides.

### HNSW: un grafo navegable, recorrido de arriba abajo

**HNSW (hierarchical navigable small world)** construye un grafo multicapa en lugar de clústeres: cada vector es un nodo, conectado mediante aristas a otros vectores cercanos, con capas más dispersas arriba que permiten saltos largos por el espacio vectorial y una capa inferior densa que permite una búsqueda local precisa. Una consulta empieza en la capa superior dispersa, salta de forma voraz hacia el nodo conectado más cercano y desciende capa por capa, refinando su posición hasta llegar a la capa inferior densa. El parámetro ajustable aquí es `ef_search`, cuántos candidatos mantiene la búsqueda en cada paso: un `ef_search` bajo encuentra una respuesta rápido pero puede conformarse con un nodo localmente bueno que no es el más cercano real; un `ef_search` alto explora más candidatos, cambia velocidad por recall, con la misma forma de compromiso que hace `nprobe` en IVF.

![Dos paneles. A la izquierda, IVF: cuatro clústeres de vectores, cada uno con un centroide. La consulta queda entre dos clústeres cercanos, sombreados y buscados, mientras que dos clústeres más lejanos quedan sin sombrear y se omiten, un nprobe bajo que busca solo en los cercanos. A la derecha, HNSW: tres capas de grafo apiladas, dispersas arriba y densas abajo, con un camino que desciende desde un punto de entrada en la capa superior, salta a nodos cada vez más cercanos en cada capa y refina su posición hasta llegar al vecino más cercano en la capa inferior densa.](images/ivf-vs-hnsw.svg)

### La forma general: una curva de recall y latencia, no una única respuesta correcta

Ambos índices exponen un parámetro (`nprobe` en IVF, `ef_search` en HNSW) que fija un punto concreto de una curva de recall frente a latencia para un corpus y un índice dados. HNSW suele situarse en un mejor punto de esa curva que IVF, con mayor recall para la misma latencia, a costa de más memoria (la propia estructura del grafo) y de una construcción de índice más lenta. Ningún índice tiene un ajuste universalmente correcto: el punto adecuado depende del presupuesto de latencia de la carga de trabajo y de cuánta pérdida de recall puede absorber una etapa posterior, como el reranking, sin que el resultado final se resienta, que es exactamente lo que las métricas de recuperación de la etapa 6 existen para medir en lugar de suponer.

## Práctica

1. ▢ ¿Por qué la búsqueda exacta de vecinos más cercanos por fuerza bruta no escala a un corpus de millones de vectores, y a qué renuncia un índice ANN para arreglarlo?

<details markdown="1"><summary>Comprobación</summary>

La búsqueda exacta compara la consulta con cada vector, así que su costo crece de forma lineal con el tamaño del corpus y se vuelve demasiado lenta con millones de vectores. Un índice ANN renuncia a la garantía de encontrar de forma exacta los vecinos más cercanos reales y acepta una probabilidad pequeña y controlable de pasar por alto alguno, a cambio de tiempos de búsqueda que no crecen del mismo modo.

</details>

2. ▢ En un índice IVF, describe qué ocurre en cada extremo del parámetro `nprobe`: `nprobe = 1` frente a `nprobe` ajustado para buscar en todos los clústeres.

<details markdown="1"><summary>Comprobación</summary>

`nprobe = 1` busca solo en el clúster más cercano: es lo más rápido, pero puede pasar por alto un vecino más cercano real que esté en un clúster contiguo cerca del límite, sobre todo si la consulta cae cerca del borde de un clúster. `nprobe` ajustado para buscar en todos los clústeres se acerca a la búsqueda exacta: el mayor recall, pero al costo de la búsqueda exacta, ya que deja de omitir la mayor parte del corpus.

</details>

3. ▢ ¿Cómo desempeña el parámetro `ef_search` de HNSW el mismo papel en HNSW que `nprobe` en IVF?

<details markdown="1"><summary>Pista</summary>

Piensa en lo que controla cada parámetro: cuánto del índice se examina antes de devolver una respuesta.

</details>

<details markdown="1"><summary>Comprobación</summary>

`ef_search` controla cuántos candidatos mantiene la búsqueda en el grafo en cada paso mientras desciende por las capas de HNSW. Un valor bajo explora menos candidatos, encuentra una respuesta rápido pero corre el riesgo de conformarse con un nodo que no es el más cercano real. Un valor alto explora más candidatos, cambia velocidad de búsqueda por mayor recall, con la misma forma de recall frente a latencia que `nprobe` da a IVF.

</details>

4. ▢ ¿Cuál es el compromiso general entre elegir HNSW y elegir IVF para un corpus dado?

<details markdown="1"><summary>Comprobación</summary>

HNSW suele lograr un mejor punto de recall para una latencia dada que IVF, pero cuesta más memoria (las aristas del grafo añaden un sobrecosto real más allá de almacenar los vectores) y tarda más en construir el índice. IVF es más barato de construir y de almacenar, pero en general necesita buscar en una fracción mayor del corpus para igualar el recall de HNSW con la misma latencia.

</details>

5. ▢ ¿Qué afirmación es cierta sobre ajustar el parámetro de tiempo de búsqueda de un índice ANN (`nprobe` o `ef_search`)?

    - a) Existe un ajuste universalmente correcto que sirve para cualquier corpus y carga de trabajo
    - b) El ajuste correcto es un punto de una curva de recall y latencia que hay que elegir según el presupuesto de latencia real de la carga de trabajo y su tolerancia a la pérdida de recall
    - c) Ajustar el parámetro lo más alto posible siempre es la elección correcta, ya que la latencia no importa una vez que existe un índice
    - d) El parámetro solo afecta al tiempo de construcción del índice, no al comportamiento en el momento de la consulta

<details markdown="1"><summary>Comprobación</summary>

**b)** Ambos parámetros cambian recall por latencia en el momento de la consulta, y el punto adecuado depende de lo que la carga de trabajo necesite realmente, algo que la etapa 6 mide en lugar de suponer. (a) es falsa: eso es justo lo que descarta la curva de recall y latencia. (c) es falsa: un ajuste más alto cuesta más latencia en la consulta, lo que importa siempre que haya un presupuesto de latencia que cumplir. (d) es falsa: tanto `nprobe` como `ef_search` son parámetros de tiempo de búsqueda, no de construcción.

</details>

## Prácticas en el mundo real

- [ ] Averigua qué tipo de índice (IVF o HNSW) usa tu almacén vectorial, o cuál trae por defecto, y localiza en su documentación el parámetro de recall y latencia del tiempo de búsqueda.
- [ ] Si puedes ejecutar consultas contra un índice, prueba dos valores distintos de `nprobe` o `ef_search` y observa la diferencia en la latencia de las consultas.
- [ ] Mañana: lee un párrafo de la descripción de la estructura en capas en el paper de HNSW y anota, con tus propias palabras, por qué la capa superior necesita ser dispersa para que funcionen los saltos de largo alcance.

## Para profundizar

- [Paper: "Efficient and Robust Approximate Nearest Neighbor Search Using Hierarchical Navigable Small World Graphs", Malkov and Yashunin, 2018](https://arxiv.org/abs/1603.09320)
- [Repo: pgvector, pgvector](https://github.com/pgvector/pgvector)
- [Recursos](../RESOURCES.md)

---

¿No termina de quedar claro? Vuelve a leer la fuente principal de arriba, ya que esta lección la comprime y en la compresión es donde se escapa la comprensión. Consulta el [glosario](../GLOSSARY.md) por si algún término te resultó resbaladizo.

Si lo poco claro es la propia lección y no el material, eso es un defecto: [abre un issue](https://github.com/TokenCemetery/teach/issues).
