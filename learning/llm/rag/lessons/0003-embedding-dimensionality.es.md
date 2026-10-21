---
title: "3. Compromisos de la dimensionalidad de los embeddings"
description: "Por qué un vector de embedding más grande no es gratis, y cuándo es seguro truncarlo en lugar de elegir un modelo más pequeño"
type: lesson
---

# Lección 3. Compromisos de la dimensionalidad de los embeddings

**Vínculo con la misión:** Esta es la lección que cierra la etapa 2: elegir un modelo de embeddings (lección 2) no termina hasta que su tamaño de salida se sopesa contra lo que el presupuesto de almacenamiento y latencia de un corpus puede permitirse realmente.
**Fuente principal:** [Paper: "Matryoshka Representation Learning", Kusupati et al., 2022](https://arxiv.org/abs/2205.13147)
**Requisitos previos:** [Lección 2](0002-embedding-models-and-similarity.md), [Chunk](../GLOSSARY.md)

## Calentamiento

1. ▢ ¿Por qué un bi-encoder genera el embedding de una consulta y de un pasaje por separado y no de forma conjunta?

<details markdown="1"><summary>Comprobación</summary>

Para que cada pasaje reciba su embedding una sola vez, de antemano, y se almacene; en el momento de la búsqueda solo hace falta el embedding de la consulta, que se compara de forma barata con vectores de pasajes precalculados. Generarlos de forma conjunta (un cross-encoder) exige ejecutar el modelo sobre cada par, lo que no escala a un corpus grande.

</details>

2. ▢ ¿Por qué la similitud coseno y el producto punto producen el mismo ranking solo cuando los vectores están normalizados a longitud unitaria?

<details markdown="1"><summary>Comprobación</summary>

El producto punto es la similitud coseno escalada por las magnitudes de los dos vectores. Cuando ambas están fijas en longitud unitaria, ese factor de escala es idéntico en todos los pares, así que las dos métricas ordenan igual; cuando las magnitudes varían, el producto punto premia implícitamente a los vectores más grandes.

</details>

## Qué debes saber

### La dimensionalidad es un costo, no un botón de calidad gratuito

Un embedding de mayor dimensión puede codificar más matices, pero cada una de sus dimensiones cuesta algo concreto: el almacenamiento crece de forma lineal con la dimensión (un vector de 1536 dimensiones en float32 ocupa `1536 × 4 bytes = 6,144 bytes`, unos 6 KB, frente a los `256 × 4 = 1,024 bytes` de un vector de 256 dimensiones, unos 1 KB, seis veces menos), y tanto la memoria del índice como el cálculo de distancia por candidato crecen igual. En un millón de chunks, esa diferencia es de 6 GB frente a 1 GB solo por los vectores, antes del propio sobrecosto de un índice. Un embedding más grande no es automáticamente la mejor elección; es una elección que hay que justificar frente a lo que cuesta, igual que había que justificar una caché KV más grande o un tamaño de lote mayor frente al presupuesto real de una carga de trabajo en otros contextos de serving.

### Matryoshka Representation Learning: el truncamiento como característica diseñada, no como truco

Por lo común, truncar un vector de embedding a menos dimensiones no es seguro: nada en cómo se entrenó un modelo de embeddings estándar ordena sus dimensiones por importancia, así que recortar un vector normal de 768 dimensiones a 256 puede descartar información de forma impredecible y degradar la calidad mucho más de lo que sugeriría el solo número de dimensiones. **Matryoshka Representation Learning (MRL)** entrena un modelo de otra manera: su pérdida optimiza explícitamente los prefijos del vector completo (las primeras 256 dimensiones de un embedding de 1536 dimensiones, por ejemplo) para que sean a su vez embeddings utilizables y con significado, anidados dentro del completo como las muñecas más pequeñas dentro de una matrioska. Esto significa que un modelo entrenado con MRL puede truncarse después, con un costo de calidad acotado y predecible, de modo que se puede intercambiar dimensionalidad por almacenamiento y latencia sin reentrenar ni volver a generar los embeddings de todo el corpus a otro tamaño. Esto solo vale para modelos realmente entrenados así; truncar uno que no lo fue vuelve al caso inseguro e impredecible.

![Un único vector de 1536 dimensiones dibujado como una barra, con líneas discontinuas que marcan dónde terminan sus primeras 256 dimensiones y sus primeras 768 dimensiones. Tres rangos entre corchetes sobre la barra, todos desde la dimensión 0, muestran que detenerse en 256, en 768 o leer las 1536 dimensiones completas da en cada caso un embedding utilizable y con significado, porque Matryoshka Representation Learning entrenó cada prefijo del vector para funcionar por sí solo, a diferencia de un modelo de embeddings estándar donde solo el vector completo tiene significado.](images/matryoshka-prefix-embeddings.svg)

### Decidir la dimensionalidad correcta significa medir, no suponer

La dimensionalidad correcta para un corpus dado no es un número que se adivina; es un número que se mide. Con un modelo MRL (o comparando varios tamaños de modelo candidatos), la calidad de la recuperación, de forma más directa el recall@k frente a un conjunto de consultas etiquetado o sintético (el tema de la etapa 6), puede medirse en cada dimensionalidad candidata sobre el corpus y el patrón de consultas reales en cuestión. La dimensionalidad que vale la pena llevar a producción es la más pequeña que aún cumple el listón de calidad que necesita la carga de trabajo, no la más grande disponible, ni un valor por defecto elegido sin comprobar lo que cuesta frente a lo que aporta.

## Práctica

1. ▢ Un corpus tiene 2 millones de chunks. Calcula la diferencia de almacenamiento, en gigabytes, entre generar sus embeddings a 1536 dimensiones y a 256 dimensiones, ambos en float32.

<details markdown="1"><summary>Pista</summary>

Los bytes por vector son `dimensiones × 4 bytes`. Multiplica por 2 millones y luego convierte a gigabytes.

</details>

<details markdown="1"><summary>Comprobación</summary>

1536 dimensiones: `1536 × 4 = 6,144 bytes` por vector, `× 2,000,000 ≈ 12.3 GB`. 256 dimensiones: `256 × 4 = 1,024 bytes` por vector, `× 2,000,000 ≈ 2.0 GB`. La diferencia es de unos 10.3 GB, unas seis veces menos almacenamiento a 256 dimensiones.

</details>

2. ▢ Un equipo trunca a 256 dimensiones los vectores de un modelo de embeddings estándar (no MRL) de 768 dimensiones para ahorrar almacenamiento, y la calidad de la recuperación se desploma mucho más de lo que sugeriría la sola reducción de dimensiones. ¿Cuál es el error probable?

<details markdown="1"><summary>Comprobación</summary>

El modelo no se entrenó con Matryoshka Representation Learning, así que nada ordenó sus dimensiones por importancia ni hizo de ningún prefijo del vector un embedding con significado por sí solo. Truncarlo descarta información de forma impredecible, y no del modo acotado y diseñado en que lo haría el truncamiento de un modelo entrenado con MRL.

</details>

3. ▢ ¿Qué le permite hacer a un equipo un modelo de embeddings entrenado con MRL que no permite un modelo de embeddings estándar?

<details markdown="1"><summary>Comprobación</summary>

Truncar el vector de embedding completo a una dimensionalidad menor después, con un costo de calidad acotado y predecible, intercambiando almacenamiento y latencia por calidad sin reentrenar el modelo ni volver a generar los embeddings del corpus a otro tamaño fijo.

</details>

4. ▢ ¿Cómo debería decidir un equipo qué dimensionalidad de embedding usar realmente para su corpus, en lugar de tomar por defecto el tamaño de salida completo de un modelo?

<details markdown="1"><summary>Comprobación</summary>

Medir la calidad de la recuperación, de forma más directa algo como el recall@k frente a un conjunto de consultas etiquetado o sintético representativo del corpus y del patrón de consultas reales, en varias dimensionalidades candidatas, y elegir la más pequeña que aún cumpla el listón de calidad que necesita la carga de trabajo, en lugar de suponer que hace falta la mayor dimensionalidad disponible o que una menor es automáticamente "suficientemente buena".

</details>

5. ▢ ¿Qué afirmación es cierta sobre la dimensionalidad de los embeddings?

    - a) Una mayor dimensionalidad del embedding siempre mejora la calidad de la recuperación lo suficiente como para justificar su costo
    - b) Truncar los vectores de cualquier modelo de embeddings es igual de seguro, sin importar cómo se entrenó el modelo
    - c) La dimensionalidad es un costo (almacenamiento, memoria del índice, cómputo por candidato) que debe dimensionarse al menor valor que cumpla un listón de calidad medido
    - d) Los modelos entrenados con MRL no pueden truncarse; solo ofrecen un único tamaño de salida fijo

<details markdown="1"><summary>Comprobación</summary>

**c)** Los costos de almacenamiento y de cómputo crecen con la dimensionalidad, así que el tamaño correcto es el menor valor que un listón de calidad medido realmente necesita. (a) es falsa: el costo hay que sopesarlo contra el beneficio medido, no darlo por supuesto. (b) es falsa: truncar un modelo que no es MRL es impredecible y puede destruir mucha más señal de la que implica el número de dimensiones. (d) es falsa: ese truncamiento flexible es exactamente lo que el entrenamiento MRL está construido para permitir.

</details>

## Prácticas en el mundo real

- [ ] Comprueba si el modelo de embeddings que usas (o piensas usar) se entrenó con Matryoshka Representation Learning y, de ser así, a qué dimensionalidades admite truncarse.
- [ ] Calcula el costo de almacenamiento, en bytes por vector y para el tamaño real de tu corpus, a la dimensionalidad completa de tu modelo y a un tamaño menor candidato.
- [ ] Mañana: si tienes un conjunto de consultas etiquetado o sintético, mide el recall en dos dimensionalidades de embedding distintas y compara la diferencia de calidad con la diferencia de almacenamiento.

## Para profundizar

- [Paper: "Matryoshka Representation Learning", Kusupati et al., 2022](https://arxiv.org/abs/2205.13147)
- [Paper: "Sentence-BERT: Sentence Embeddings using Siamese BERT-Networks", Reimers and Gurevych, 2019](https://arxiv.org/abs/1908.10084)
- [Recursos](../RESOURCES.md)

---

¿No termina de quedar claro? Vuelve a leer la fuente principal de arriba, ya que esta lección la comprime y en la compresión es donde se escapa la comprensión. Consulta el [glosario](../GLOSSARY.md) por si algún término te resultó resbaladizo.

Si lo poco claro es la propia lección y no el material, eso es un defecto: [abre un issue](https://github.com/TokenCemetery/teach/issues).
