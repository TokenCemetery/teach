---
title: "10. Recall@k y MRR"
description: "Las dos métricas estándar de recuperación, qué te dice cada una que la otra no, y cómo elegir k para la carga de trabajo"
type: lesson
---

# Lección 10. Recall@k y MRR

**Vínculo con la misión:** La etapa 6 abre la mitad de "medir, no suponer" de la misión de este espacio de trabajo: las decisiones de todas las etapas anteriores (chunking, embeddings, indexación, pesos híbridos, reranking) se plantearon como cosas que medir, y esta lección da los dos números estándar con los que medirlas.
**Fuente principal:** [Article: "Evaluation Measures for Search and Recommender Systems", Pinecone](https://www.pinecone.io/learn/offline-evaluation/)
**Requisitos previos:** [Lección 9](0009-when-reranking-earns-its-cost.md), [Chunk](../GLOSSARY.md)

## Calentamiento

1. ▢ ¿Cómo debería decidir un equipo si el reranking justifica su costo para su carga de trabajo concreta?

<details markdown="1"><summary>Comprobación</summary>

Medir la calidad de la recuperación tanto sin reranking como con él sobre el mismo conjunto de consultas, medir por separado la latencia añadida con el tamaño de conjunto de candidatos en uso y comparar ambas con el presupuesto de latencia y el listón de calidad reales de la carga de trabajo, en lugar de suponer que el reranking siempre o nunca ayuda.

</details>

2. ▢ En reciprocal rank fusion, ¿qué le hace la constante `k` al ranking fusionado?

<details markdown="1"><summary>Comprobación</summary>

Amortigua la influencia de las primeras posiciones: un `k` menor hace la puntuación más sensible a pequeñas diferencias de posición cerca de la cabeza, mientras que un `k` mayor (normalmente 60) hace que esas diferencias importen menos.

</details>

## Qué debes saber

### Recall@k: si el documento correcto entró en el corte

**Recall@k** pregunta, sobre un conjunto de consultas de prueba con documentos relevantes conocidos, qué fracción de ellas tuvo un documento relevante en algún lugar de los *k* primeros resultados recuperados. Es una pregunta de presupuesto: si el sistema aguas abajo solo mira los *k* primeros resultados, recall@k te dice con qué frecuencia el sistema siquiera le dio una oportunidad de encontrar la respuesta correcta. Recall@k crece a medida que crece *k* (un documento relevante en la posición 50 cuenta para recall@100 pero no para recall@10), y trata todas las posiciones dentro de los *k* primeros de forma idéntica: un documento relevante en la posición 1 y otro en la posición *k* cuentan ambos como un acierto, sin crédito por quedar más arriba.

### MRR: con qué rapidez apareció el documento correcto

**Mean reciprocal rank (MRR)** corrige exactamente lo que recall@k no puede ver. Para cada consulta, se toma el recíproco de la posición del primer resultado relevante (`1/rank`) y luego se promedia ese recíproco entre todas las consultas. Un resultado relevante en la posición 1 aporta un 1.0 completo al promedio; el mismo resultado relevante en la posición 10 aporta solo 0.1. MRR premia colocar la respuesta correcta lo más arriba posible, no meramente dejarla dentro de algún corte, que es justo la información que recall@k descarta al tratar igual cada posición dentro de los *k* primeros.

### Un ejemplo resuelto

Cuatro consultas de prueba, cada una con un documento relevante conocido, y su posición en los resultados de cada sistema: 1, 3, 1, 8.

```text
recall@1: ranks ≤ 1 are queries 1 and 3 → 2/4 = 0.50
recall@5: ranks ≤ 5 are queries 1, 2, and 3 (ranks 1, 3, 1); query 4 (rank 8) misses → 3/4 = 0.75
MRR: (1/1 + 1/3 + 1/1 + 1/8) / 4 = (1.000 + 0.333 + 1.000 + 0.125) / 4 ≈ 0.615
```

recall@5 dice que tres de cada cuatro consultas encontrarían su respuesta si el sistema solo mirara sus 5 primeros resultados. El 0.615 de MRR refleja que la mayoría de esos aciertos quedaron en la posición 1, con un acierto más débil en la posición 3 y un fallo que arrastra el promedio hacia abajo.

![Cuatro consultas ubicadas sobre un eje de posición compartido del 1 al 9, en la posición de su primer resultado relevante: 1, 3, 1 y 8. Una línea discontinua marca el corte de recall at 5. Los aciertos de las tres primeras consultas caen a la izquierda del corte y cuentan para recall at 5, mientras que el de la cuarta, en la posición 8, cae a la derecha y es un fallo. El rango recíproco de cada consulta se muestra a su lado: 1.000, 0.333, 1.000 y 0.125. Recall at 5 resulta ser 3 de 4, 0.75, mientras que promediar los rangos recíprocos da un MRR de aproximadamente 0.615, arrastrado hacia abajo por lo lejos a la derecha que queda la posición de ese único fallo, algo que recall at 5 no puede ver en absoluto.](images/recall-at-k-vs-mrr.svg)

### Elegir k, y elegir entre las métricas

El *k* correcto para recall@k no es un valor por defecto; es el que el sistema aguas abajo usa realmente. Si solo los 5 primeros chunks pasan a la generación, recall@100 mide algo que el pipeline nunca aprovecha en realidad; recall@5 es el número que refleja la realidad. MRR es más informativo cuando solo importa mucho el primer resultado (una única mejor respuesta que se muestra a un usuario), ya que premia específicamente la posición 1 mucho más que la 10. Recall@k es más informativo cuando varios resultados dentro de un presupuesto son todos genuinamente utilizables (la generación puede apoyarse en varios de los chunks del top-k, no solo en el primero). Reportar ambos, con el *k* que el pipeline usa realmente, da una imagen más completa que cualquiera de los dos por separado.

## Práctica

1. ▢ Con el ejemplo de cuatro consultas de esta lección (posiciones 1, 3, 1, 8), calcula recall@3.

<details markdown="1"><summary>Pista</summary>

Cuenta cuántas de las cuatro posiciones son 3 o menos.

</details>

<details markdown="1"><summary>Comprobación</summary>

Las posiciones 1, 3 y 1 son todas ≤ 3; la posición 8 no. `recall@3 = 3/4 = 0.75`, igual que recall@5 en este ejemplo, ya que el documento relevante de ninguna consulta cayó en la posición 4 o 5.

</details>

2. ▢ ¿Por qué recall@k por sí solo no distingue un sistema que siempre coloca el documento relevante en 1.er lugar de uno que lo coloca siempre exactamente en la posición `k`?

<details markdown="1"><summary>Comprobación</summary>

Recall@k solo comprueba si un documento relevante aparece en algún lugar de las k primeras posiciones; no registra en qué posición de ese rango cayó. Un acierto en la posición 1 y un acierto en la posición k cuentan igual para recall@k, así que la métrica no puede distinguir los dos sistemas aunque uno esté claramente ordenando mejor.

</details>

3. ▢ ¿Por qué MRR distingue esos dos sistemas, donde recall@k no podía?

<details markdown="1"><summary>Comprobación</summary>

MRR usa el recíproco de la posición exacta, no solo si cae por debajo de un corte. Un sistema que siempre coloca el documento relevante en 1.er lugar obtiene un rango recíproco de 1.0 cada vez, lo que le da un MRR de 1.0; un sistema que siempre lo coloca en la posición k obtiene un rango recíproco de `1/k` cada vez, lo que le da un MRR mucho menor siempre que k sea mayor que 1. La posición exacta importa para MRR de una forma en que nunca importó para recall@k.

</details>

4. ▢ El paso de generación de un equipo solo usa los 5 primeros chunks recuperados. ¿Deberían reportar recall@100 como su métrica principal de recuperación? ¿Por qué sí o por qué no?

<details markdown="1"><summary>Comprobación</summary>

No. Recall@100 mide si el documento relevante aparece en algún lugar de los 100 primeros resultados, pero el pipeline nunca mira más allá de los 5 primeros, así que un acierto en la posición 40 es invisible para el sistema real y no debería contar como un éxito. Recall@5 es el número que refleja lo que el pipeline aprovecha realmente; reportar recall@100 sobreestimaría con qué frecuencia el sistema hace llegar la respuesta correcta a la generación.

</details>

5. ▢ ¿Qué afirmación es cierta sobre recall@k y MRR?

    - a) Miden exactamente lo mismo, así que reportar ambas es redundante
    - b) Recall@k mide si un resultado relevante cae dentro de un presupuesto de k; MRR mide cuán arriba está el primer resultado relevante, y premia la posición 1 mucho más que una posición inferior
    - c) MRR siempre debería preferirse a recall@k, sin importar la carga de trabajo
    - d) Recall@k es insensible a la elección de k; cualquier valor da el mismo resultado

<details markdown="1"><summary>Comprobación</summary>

**b)** Esa es exactamente la información complementaria que captura cada métrica. (a) es falsa: el ejemplo resuelto mostró dos sistemas que podrían empatar en recall@k y diferir con fuerza en MRR. (c) es falsa: qué métrica importa más depende de si solo cuenta el primer resultado o si varios resultados dentro de un presupuesto son utilizables. (d) es falsa: recall@k crece a medida que crece k, por definición, así que la elección de k cambia el valor reportado.

</details>

## Prácticas en el mundo real

- [ ] Para un pipeline de recuperación que ejecutes o pienses ejecutar, identifica el k real que usa tu sistema aguas abajo (cuántos chunks llegan a la generación) y calcula el recall con ese k, no con un valor por defecto como 10 o 100.
- [ ] Si tienes un conjunto de consultas etiquetado o sintético, calcula MRR junto con recall@k y comprueba si los dos números cuentan una historia coherente o revelan algo que una sola métrica habría ocultado.
- [ ] Mañana: para una consulta en la que el documento relevante de tu sistema queda más abajo de lo que querrías, anota su posición exacta y cómo afecta tanto a recall@k (con el k que elijas) como a MRR.

## Para profundizar

- [Article: "Evaluation Measures for Search and Recommender Systems", Pinecone](https://www.pinecone.io/learn/offline-evaluation/)
- [Recursos](../RESOURCES.md)

---

¿No termina de quedar claro? Vuelve a leer la fuente principal de arriba, ya que esta lección la comprime y en la compresión es donde se escapa la comprensión. Consulta el [glosario](../GLOSSARY.md) por si algún término te resultó resbaladizo.

Si lo poco claro es la propia lección y no el material, eso es un defecto: [abre un issue](https://github.com/TokenCemetery/teach/issues).
