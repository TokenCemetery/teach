---
title: "7. Reciprocal Rank Fusion"
description: "Cómo combinar un ranking léxico y un ranking vectorial sin comparar puntuaciones incomparables, y cómo ajustar la mezcla contra una métrica medida"
type: lesson
---

# Lección 7. Reciprocal Rank Fusion

**Vínculo con la misión:** Esta es la lección que cierra la etapa 4: BM25 y la búsqueda vectorial (lecciones 4 a 6) producen cada una un ranking, y esta lección es cómo esos dos rankings se convierten en un único resultado híbrido, ajustado contra un número medido y no contra una mezcla adivinada.
**Fuente principal:** [Docs: "Reciprocal rank fusion (RRF)", Elasticsearch](https://www.elastic.co/guide/en/elasticsearch/reference/current/rrf.html)
**Requisitos previos:** [Lección 6](0006-bm25-and-lexical-search.md), [Chunk](../GLOSSARY.md)

## Calentamiento

1. ▢ Da un ejemplo de una consulta en la que BM25 tendría éxito y la búsqueda vectorial podría fallar, y otro en el que ocurra lo contrario.

<details markdown="1"><summary>Comprobación</summary>

Un identificador exacto como "error code E502" favorece a BM25, ya que el modelo de embeddings de la búsqueda vectorial no se entrenó para hacer coincidir códigos específicos con precisión. Una formulación sinónima sin palabras en común, como "broken pipe" frente a "leaking conduit", favorece a la búsqueda vectorial, ya que BM25 puntúa cero a los documentos que no comparten términos con la consulta.

</details>

2. ▢ ¿Por qué usar el operador de distancia equivocado contra un índice de pgvector hace que la consulta recurra a un escaneo secuencial?

<details markdown="1"><summary>Comprobación</summary>

Un índice se construye para una función de distancia concreta (una clase de operador); una consulta que usa un operador distinto no coincide con aquello para lo que se construyó el índice, así que el índice no puede usarse y la consulta escanea directamente la tabla.

</details>

## Qué debes saber

### El problema: dos rankings en escalas incomparables

BM25 produce una puntuación sin cota y dependiente del corpus; la similitud coseno produce una puntuación acotada entre -1 y 1. Promediarlas directamente, incluso tras cierta normalización, implica decidir cómo hacer comparables dos escalas fundamentalmente distintas, y esa decisión es frágil: depende del corpus, de la consulta y del esquema de normalización elegido, sin una forma fundamentada de saber que es justa.

### RRF: usar la posición en el ranking, no la puntuación en sí

**Reciprocal rank fusion (RRF)** esquiva por completo el problema de la escala ignorando las puntuaciones subyacentes y usando solo la **posición en el ranking** de cada documento dentro de cada ranking. Para un documento *d* que aparece en la posición `rank_r(d)` del ranking *r*, su puntuación RRF suma un término de rango recíproco en cada ranking en el que aparece:

```text
RRF(d) = sum over rankings r of 1 / (k + rank_r(d))
```

`k` es una constante que amortigua la influencia de las primeras posiciones; un valor por defecto común del paper original es `k = 60`. Como solo importa la posición en el ranking y no la magnitud de la puntuación, RRF combina un ranking de BM25 y un ranking de búsqueda vectorial sin necesidad de normalizar ninguno: la posición ya es una moneda común, autonormalizada para cualquier método de ranking.

### Un ejemplo resuelto

Usando un `k = 1` simplificado para mantener limpia la aritmética (los sistemas de producción suelen tomar `k = 60` por defecto, que amortigua las diferencias entre las primeras posiciones con más fuerza que `k = 1`): para una consulta, BM25 coloca al documento A en 1.º lugar, al documento B en 4.º y al documento C en 2.º; la búsqueda vectorial coloca a A en 4.º, a B en 1.º y a C en 2.º.

```text
RRF(A) = 1/(1+1) + 1/(1+4) = 0.500 + 0.200 = 0.700
RRF(B) = 1/(1+4) + 1/(1+1) = 0.200 + 0.500 = 0.700
RRF(C) = 1/(1+2) + 1/(1+2) = 0.333 + 0.333 = 0.667
```

A y B empatan en el primer lugar, y cada uno sobresale con un método y rinde mal con el otro; C, apenas mediocre con ambos, pierde frente a los dos. RRF premia a un documento en el que cualquiera de los métodos confía con fuerza, no solo a uno en el que ambos coinciden de forma moderada.

![Dos listas ordenadas lado a lado, el ranking de BM25 y el ranking de la búsqueda vectorial, cada una con cuatro posiciones. El documento A queda en 1.º lugar con BM25 pero en 4.º con la búsqueda vectorial; el documento B queda en 4.º con BM25 pero en 1.º con la búsqueda vectorial; el documento C queda en 2.º con ambos. Unas líneas trazan cada documento desde sus dos posiciones hasta un ranking fusionado de RRF a la derecha, donde A y B empatan en el primer lugar, habiendo sobresalido cada uno con un método, mientras que C, que solo fue moderado, queda detrás de ellos pese a no haber quedado mal en ninguna de las dos listas.](images/rrf-worked-example.svg)

### Ajustar la mezcla contra una métrica medida

RRF puede ampliarse con un peso por ranking, `sum of w_r / (k + rank_r(d))`, lo que permite que la búsqueda vectorial cuente más o menos que BM25 en la fusión final. El peso correcto, y el `k` correcto, no son algo que se adivine: son algo que se mide, igual que la lección 3 midió la calidad de los embeddings en dimensionalidades candidatas en lugar de suponer una. Con las métricas de recuperación de la etapa 6 (recall@k, MRR) frente a un conjunto de consultas etiquetado o sintético representativo del tráfico real del corpus, se pueden comparar directamente distintas ponderaciones, y la mezcla que realmente recupera los documentos correctos con más frecuencia para este corpus, no una división 50/50 por defecto, es la que vale la pena llevar a producción.

## Práctica

1. ▢ Para una consulta, BM25 coloca al documento X en 2.º lugar y al documento Y en 1.º; la búsqueda vectorial coloca a X en 1.º y a Y en 3.º. Con `k = 1`, calcula la puntuación RRF de cada documento y di cuál queda más arriba.

<details markdown="1"><summary>Pista</summary>

`RRF(d) = 1/(k + rank_in_bm25) + 1/(k + rank_in_vector)`.

</details>

<details markdown="1"><summary>Comprobación</summary>

`RRF(X) = 1/(1+2) + 1/(1+1) = 0.333 + 0.500 = 0.833`. `RRF(Y) = 1/(1+1) + 1/(1+3) = 0.500 + 0.250 = 0.750`. X queda más arriba, ya que es un resultado fuerte (1.er lugar) con la búsqueda vectorial y solo moderadamente bueno con BM25, y supera por poco a Y, que es fuerte con BM25 pero más débil con la búsqueda vectorial.

</details>

2. ▢ ¿Por qué RRF usa la posición en el ranking de cada documento y no su puntuación BM25 bruta ni su similitud coseno directamente?

<details markdown="1"><summary>Comprobación</summary>

Las puntuaciones de BM25 y la similitud coseno viven en escalas incomparables (una sin cota y dependiente del corpus, la otra acotada entre -1 y 1), y no hay una forma fundamentada e independiente del corpus de normalizar una contra la otra. La posición en el ranking ya es una moneda común para cualquier método de ranking, así que usarla esquiva por completo el problema de la normalización.

</details>

3. ▢ ¿Qué le hace un `k` pequeño (como 1) a la fórmula de RRF, en comparación con un `k` grande (como 60), en cuanto a cuánto importa la posición exacta de un documento en el ranking?

<details markdown="1"><summary>Comprobación</summary>

Un `k` pequeño hace que el término de rango recíproco sea mucho más sensible a pequeñas diferencias de posición cerca de la cabeza de una lista (la brecha entre el 1.er y el 2.º lugar es proporcionalmente mayor), mientras que un `k` grande amortigua esa sensibilidad y hace que la diferencia entre, por ejemplo, el 1.er y el 5.º lugar sea comparativamente menor. Los valores de `k` más grandes producen una fusión más suave y menos sensible a la posición en el ranking.

</details>

4. ▢ ¿Cómo debería decidir un equipo si pondera más la búsqueda vectorial que BM25 en su mezcla híbrida, en lugar de tomar por defecto una división equitativa?

<details markdown="1"><summary>Comprobación</summary>

Medir la calidad de la recuperación (recall@k o MRR, las métricas de la etapa 6) frente a un conjunto de consultas etiquetado o sintético representativo del patrón de consultas real del corpus, con varias ponderaciones candidatas, y elegir la que realmente recupera los documentos correctos con más frecuencia para este corpus, en lugar de suponer que una división equitativa o cualquier otro valor por defecto es correcto sin comprobarlo.

</details>

5. ▢ ¿Qué afirmación es cierta sobre reciprocal rank fusion?

    - a) Requiere normalizar las puntuaciones de BM25 y de la similitud coseno a la misma escala antes de combinarlas
    - b) Combina rankings usando solo la posición en el ranking, lo que esquiva la necesidad de comparar escalas de puntuación incomparables
    - c) Un documento que queda 1.º en un ranking y último en otro siempre superará a un documento que queda moderadamente en ambos
    - d) La constante `k` no tiene efecto en el ranking fusionado, solo en la magnitud de la puntuación numérica

<details markdown="1"><summary>Comprobación</summary>

**b)** Usar la posición en el ranking en lugar de las puntuaciones brutas es exactamente lo que evita el problema de la normalización. (a) es falsa: ese es el enfoque de fusión de puntuaciones brutas que RRF evita específicamente. (c) es falsa: el ejemplo resuelto mostró que un documento consistentemente moderado puede perder frente a dos documentos que sobresalen cada uno con un método, pero el resultado depende de los valores de posición reales, no de una regla universal de que lo extremo vence a lo moderado. (d) es falsa: `k` cambia cuánto importan las diferencias de posición, lo que puede cambiar el orden del ranking fusionado, no solo su escala.

</details>

## Prácticas en el mundo real

- [ ] Para una consulta de tu corpus, obtén su posición en el ranking de BM25 y en el de la búsqueda vectorial para un puñado de documentos candidatos, y calcula a mano sus puntuaciones RRF con `k = 60`.
- [ ] Si tienes un conjunto de consultas etiquetado o sintético, compara el recall@k de un ranking solo con BM25, un ranking solo vectorial y un ranking fusionado con RRF sobre las mismas consultas.
- [ ] Mañana: prueba dos valores distintos del peso de la búsqueda vectorial en una fórmula RRF ponderada y comprueba si alguno mejora de forma medible el recall@k respecto de una división equitativa.

## Para profundizar

- [Docs: "Reciprocal rank fusion (RRF)", Elasticsearch](https://www.elastic.co/guide/en/elasticsearch/reference/current/rrf.html)
- [Paper: "The Probabilistic Relevance Framework: BM25 and Beyond", Robertson and Zaragoza, 2009](https://www.staff.city.ac.uk/~sbrp622/papers/foundations_bm25_review.pdf)
- [Recursos](../RESOURCES.md)

---

¿No termina de quedar claro? Vuelve a leer la fuente principal de arriba, ya que esta lección la comprime y en la compresión es donde se escapa la comprensión. Consulta el [glosario](../GLOSSARY.md) por si algún término te resultó resbaladizo.

Si lo poco claro es la propia lección y no el material, eso es un defecto: [abre un issue](https://github.com/TokenCemetery/teach/issues).
