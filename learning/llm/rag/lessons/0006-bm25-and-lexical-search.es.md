---
title: "6. BM25 y búsqueda léxica"
description: "Qué puntúa realmente BM25, y por qué la coincidencia exacta de términos todavía detecta lo que los embeddings semánticos pasan por alto"
type: lesson
---

# Lección 6. BM25 y búsqueda léxica

**Vínculo con la misión:** La etapa 4 abre la búsqueda híbrida: antes de combinar un ranking léxico con la búsqueda vectorial, esta lección establece en qué es realmente buena la búsqueda léxica y por qué un buen modelo de embeddings no la vuelve obsoleta.
**Fuente principal:** [Paper: "The Probabilistic Relevance Framework: BM25 and Beyond", Robertson and Zaragoza, 2009](https://www.staff.city.ac.uk/~sbrp622/papers/foundations_bm25_review.pdf)
**Requisitos previos:** [Lección 5](0005-pgvector-specifics.md), [Chunk](../GLOSSARY.md)

## Calentamiento

1. ▢ ¿Por qué un bi-encoder genera el embedding de una consulta y de un pasaje por separado y no de forma conjunta?

<details markdown="1"><summary>Comprobación</summary>

Para que cada pasaje reciba su embedding una sola vez, de antemano, y se almacene; en el momento de la búsqueda solo hace falta el embedding de la consulta, que se compara de forma barata con vectores de pasajes precalculados.

</details>

2. ▢ ¿Por qué un índice construido con `vector_l2_ops` no acelera una consulta que ordena por `<=>` (distancia coseno)?

<details markdown="1"><summary>Comprobación</summary>

Un índice se construye para una función de distancia concreta; la clase de operador y el operador de la consulta tienen que coincidir, o el índice no se usa y la consulta recurre a un escaneo secuencial completo.

</details>

## Qué debes saber

### BM25 puntúa la coincidencia de términos, no el significado

**BM25** es una función de ranking léxico: puntúa cuán relevante es un documento para una consulta basándose únicamente en qué términos de la consulta aparecen literalmente en el documento, con qué frecuencia y cuán informativo es cada término, sin ningún embedding ni noción alguna de significado. Tres ingredientes se combinan en su puntuación: la **frecuencia inversa de documentos (IDF)**, que pondera un término de la consulta según lo raro que es en todo el corpus (una palabra común como "the" aporta casi nada, ya que aparece en todas partes y no distingue nada; un término raro y específico aporta mucho, ya que su presencia es informativa); la **frecuencia del término**, cuántas veces aparece un término de la consulta en este documento concreto, pero **saturando** en lugar de crecer de forma lineal, de modo que un término que aparece 10 veces no puntúa 10 veces más que uno que aparece una vez, lo que evita que el relleno de palabras clave domine una puntuación; y la **normalización por longitud**, que descuenta la ventaja bruta de frecuencia de términos de un documento por el simple hecho de ser más largo que el promedio, ya que un documento más largo tiene más oportunidades de contener cualquier término dado solo por su tamaño, no necesariamente porque sea más relevante.

### Por qué la búsqueda léxica sigue importando junto a un buen modelo de embeddings

Los modelos de embeddings se entrenan para capturar la similitud semántica, y lo hacen bien con formulaciones sinónimas: una consulta por "how to fix a broken pipe" puede recuperar un pasaje sobre "resolving a leaking conduit" pese a no compartir ninguna palabra, porque ambos significan cosas similares. Pero ese mismo entrenamiento hace que los embeddings sean comparativamente débiles en la coincidencia exacta de términos específicos: un código de producto, un identificador de error, un nombre propio raro, una frase exacta que el usuario cita textualmente. Una consulta por "error code E502" necesita un documento que contenga literalmente "E502"; un modelo de embeddings, entrenado para la similitud semántica general y no para la coincidencia exacta de identificadores, puede recuperar documentos que tratan del manejo de errores sin hacer aparecer el único documento que contiene el código concreto que escribió el usuario. BM25 tiene el punto ciego opuesto: justo el caso inverso, "broken pipe" frente a "leaking conduit", puntuaría casi cero con BM25, ya que ambos no comparten ningún término, pese a significar lo mismo. Cada enfoque detecta lo que el otro pasa por alto, que es exactamente el argumento para combinarlos en lugar de elegir uno.

![Una cuadrícula de dos por dos. Fila uno: una consulta de identificador exacto como "error code E502". BM25 la encuentra, ya que la cadena literal aparece en el documento; la búsqueda vectorial puede pasarla por alto, ya que su modelo de embeddings se entrenó para la similitud semántica, no para la coincidencia exacta de identificadores. Fila dos: una consulta de formulación sinónima como "broken pipe" frente a un documento que dice "leaking conduit", sin palabras en común. BM25 puntúa esto casi en cero, ya que solo cuenta la coincidencia literal de términos; la búsqueda vectorial lo encuentra, ya que las dos frases significan lo mismo. El punto ciego de cada método es la fortaleza del otro.](images/bm25-vs-vector-blindspots.svg)

## Práctica

1. ▢ Un usuario busca el código de error exacto "E502". ¿Por qué la búsqueda vectorial por sí sola podría recuperar de menos el único documento que contiene realmente esa cadena, aunque el corpus tenga varios documentos que tratan del manejo de errores?

<details markdown="1"><summary>Comprobación</summary>

El modelo de embeddings se entrenó para capturar la similitud semántica, no la coincidencia exacta de identificadores, así que "E502" puede no estar bien representado como un punto distintivo del espacio de embeddings; los documentos temáticamente similares sobre el manejo de errores en general pueden quedar más cerca del embedding de la consulta que el único documento que contiene la cadena literal "E502".

</details>

2. ▢ Una consulta dice "how to fix a broken pipe", y el documento que mejor coincide está redactado "resolving a leaking conduit", sin palabras en común con la consulta. ¿Puntuaría alto BM25 este par? ¿Por qué sí o por qué no?

<details markdown="1"><summary>Comprobación</summary>

No, BM25 lo puntuaría casi en cero, ya que solo puntúa según qué términos de la consulta aparecen literalmente en el documento, y este par no comparte ningún término. BM25 no tiene forma de reconocer que las dos formulaciones significan lo mismo; ese es exactamente el hueco que la similitud semántica de la búsqueda vectorial está pensada para llenar.

</details>

3. ▢ ¿Por qué BM25 satura la frecuencia de términos (disminuye el aumento de puntuación por las apariciones repetidas de un término) en lugar de puntuarla de forma lineal?

<details markdown="1"><summary>Pista</summary>

Piensa en lo que un documento podría hacer para manipular una puntuación lineal de frecuencia de términos.

</details>

<details markdown="1"><summary>Comprobación</summary>

Una puntuación lineal de frecuencia de términos permitiría que un documento dominara el ranking simplemente repitiendo muchas veces un término de la consulta (relleno de palabras clave), con independencia de que el documento sea realmente más relevante. Saturar la frecuencia de términos significa que cada aparición adicional aporta menos que la anterior, de modo que la relevancia se sigue premiando sin dejar que la mera repetición domine la puntuación.

</details>

4. ▢ ¿Por qué BM25 normaliza por la longitud del documento, y qué saldría mal sin esa normalización?

<details markdown="1"><summary>Comprobación</summary>

Un documento más largo tiene más oportunidades de contener cualquier término de la consulta por el simple hecho de tener más palabras, con independencia de que sea realmente más relevante para la consulta. Sin normalización por longitud, los documentos largos superarían de forma sistemática a los más cortos, igual o más relevantes, solo por su tamaño y no por su relevancia real.

</details>

5. ▢ ¿Qué afirmación es cierta sobre BM25 en comparación con la búsqueda vectorial?

    - a) BM25 y la búsqueda vectorial fallan en exactamente los mismos tipos de consultas, así que combinarlas no aporta nada
    - b) BM25 sobresale en la coincidencia exacta de términos pero pasa por alto las formulaciones sinónimas sin palabras en común, mientras que la búsqueda vectorial hace lo contrario
    - c) BM25 requiere un modelo de embeddings para calcular la relevancia de los términos
    - d) La búsqueda vectorial siempre supera a BM25 en cualquier consulta, ya que captura el significado y no solo las palabras

<details markdown="1"><summary>Comprobación</summary>

**b)** El punto ciego de cada enfoque es la fortaleza del otro, que es la base completa de la búsqueda híbrida. (a) es falsa: sus modos de fallo son opuestos, no idénticos. (c) es falsa: BM25 es un método puramente de estadística de términos, sin ningún embedding de por medio. (d) es falsa: una coincidencia exacta de identificador o código es justo el caso en que BM25 puede superar a un embedding semántico.

</details>

## Prácticas en el mundo real

- [ ] Encuentra o escribe una consulta para tu corpus que incluya un identificador, un código o una frase exacta, y comprueba si tu configuración de recuperación actual (si es solo vectorial) hace aparecer realmente el documento que lo contiene.
- [ ] Encuentra en tu corpus una consulta y un documento que coincidan y que compartan muy pocas palabras exactas, o ninguna, pero signifiquen lo mismo, y predice cómo puntuaría ese par una búsqueda solo con BM25.
- [ ] Mañana: averigua si tu stack de búsqueda (búsqueda de texto completo de Postgres, Elasticsearch o similar) ya expone una función de ranking al estilo BM25 que puedas comparar con los resultados de tu búsqueda vectorial.

## Para profundizar

- [Paper: "The Probabilistic Relevance Framework: BM25 and Beyond", Robertson and Zaragoza, 2009](https://www.staff.city.ac.uk/~sbrp622/papers/foundations_bm25_review.pdf)
- [Docs: "Reciprocal rank fusion (RRF)", Elasticsearch](https://www.elastic.co/guide/en/elasticsearch/reference/current/rrf.html)
- [Recursos](../RESOURCES.md)

---

¿No termina de quedar claro? Vuelve a leer la fuente principal de arriba, ya que esta lección la comprime y en la compresión es donde se escapa la comprensión. Consulta el [glosario](../GLOSSARY.md) por si algún término te resultó resbaladizo.

Si lo poco claro es la propia lección y no el material, eso es un defecto: [abre un issue](https://github.com/TokenCemetery/teach/issues).
