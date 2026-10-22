---
title: "8. Capas de embedding y de salida, weight tying"
description: "Cómo entran los tokens al espacio vectorial del transformer y cómo salen de él, y por qué las dos capas que lo hacen pueden compartir una sola matriz"
type: lesson
---

# Lección 8. Capas de embedding y de salida, weight tying

**Vínculo con la misión:** Esta es la pieza final de la etapa 3: los bloques apilados (lección 7) operan por completo con vectores de dimensión `d_model`, así que algo tiene que convertir los tokens discretos a ese espacio a la entrada, y de vuelta a puntuaciones sobre el vocabulario a la salida, cerrando el círculo desde los IDs de token en bruto hasta un forward pass completo.
**Fuente principal:** [Paper: "Using the Output Embedding to Improve Language Models", Press and Wolf, 2017](https://arxiv.org/abs/1608.05859)
**Requisitos previos:** [Lección 7](0007-stacking-blocks.md), [Scaled dot-product attention](../GLOSSARY.md)

## Calentamiento

1. ▢ ¿Por qué debe conservar cada bloque transformer la misma dimensión de entrada y de salida (`d_model` de entrada, `d_model` de salida)?

<details markdown="1"><summary>Comprobación</summary>

Apilar significa que la salida de un bloque alimenta directamente la entrada del siguiente; si un bloque cambiara la dimensión, cada bloque posterior y el residual stream tendrían que construirse para un tamaño distinto, lo que rompería el apilado uniforme que permite repetir el mismo shape de bloque cualquier número de veces.

</details>

2. ▢ ¿Son los pesos de un bloque de una pila transformer estándar los mismos que los de otro bloque? ¿Qué cuesta eso y qué compra?

<details markdown="1"><summary>Comprobación</summary>

No, cada bloque tiene sus propios parámetros, aprendidos de forma independiente. Esto cuesta número de parámetros más o menos linealmente con la profundidad, ya que no se comparte nada, pero deja que distintos bloques se especialicen de forma distinta a distintas profundidades en lugar de calcular todos la misma transformación idéntica.

</details>

## Qué debes saber

### El embedding de entrada: una búsqueda de ID de token a vector

Un tokenizer (nombrado aquí de pasada; derivarlo más es territorio de `llm/finetuning`) produce una secuencia de IDs de token enteros, cada uno un índice en un vocabulario fijo. La **capa de embedding de entrada** es una matriz aprendida de shape `vocab_size × d_model`: la fila `i` es la representación vectorial densa del token `i`. Buscar el embedding de un token es simplemente leer su fila. Aquí es donde los tokens discretos y simbólicos entran en el espacio vectorial continuo sobre el que opera realmente cada pieza posterior: la atención, el bloque feed-forward, la codificación posicional.

### La capa de salida: proyectar de vuelta a puntuaciones sobre el vocabulario

Después de que el último bloque apilado produce su salida, todavía de dimensión `d_model` por posición, el modelo necesita un paso más para convertir ese vector de nuevo en una predicción sobre el vocabulario. La **capa de salida** es una proyección lineal de shape `d_model × vocab_size`, que produce una puntuación en bruto, llamada **logit**, por cada token del vocabulario en cada posición. Esos logits (convertidos en una distribución de probabilidad por la pérdida de entropía cruzada de la próxima lección) son lo que significa numéricamente "predecir el siguiente token": un vector de puntuaciones del tamaño del vocabulario, una por cada token posible.

### Los shapes de las dos capas son transpuestos uno del otro

La matriz de embedding de entrada es `vocab_size × d_model`; la proyección de salida es `d_model × vocab_size`, exactamente el shape transpuesto. El **weight tying** aprovecha esto de forma directa: en lugar de aprender una matriz de salida totalmente aparte, el modelo reutiliza la misma matriz de embedding, transpuesta, para calcular los logits de salida (`logits = h @ W_embedding^T`). Esto no es solo una coincidencia que se explota por comodidad; ambas capas relacionan un token con esencialmente la misma pregunta de fondo, el embedding de entrada responde a "qué vector representa al token X", y la capa de salida responde a "qué probabilidad tiene el token X", y el tying las trata como si compartieran una sola representación en lugar de aprender dos distintas y sin relación.

![Dos diagramas lado a lado. A la izquierda, un id de token busca su fila en la matriz de embedding, de shape vocab_size por d_model, y produce un vector de embedding. A la derecha, un vector oculto se proyecta a través de la misma matriz, transpuesta a d_model por vocab_size, y produce un vector de logits, una puntuación por token del vocabulario. Una línea discontinua conecta las dos matrices, con la etiqueta misma matriz de pesos, transpuesta, y muestra que el weight tying reutiliza una sola matriz aprendida tanto para la búsqueda de entrada como para la proyección de salida en lugar de aprender dos distintas.](images/weight-tying-embedding-output.svg)

### Qué ahorra realmente el tying

Para un vocabulario de 50,000 tokens y `d_model = 768`, la sola tabla de embeddings contiene `50,000 × 768 = 38,400,000` parámetros. Un modelo sin tying necesitaría una segunda matriz del mismo tamaño para la proyección de salida, otros 38.4 millones de parámetros haciendo un trabajo estrechamente relacionado. El tying elimina esa segunda matriz entera y, en modelos con vocabularios grandes en relación con su tamaño oculto, eso es una fracción sustancial del número total de parámetros del modelo ahorrada con esencialmente ninguna pérdida de calidad, y a menudo con una mejora medible.

## Práctica

1. ▢ ¿Qué shape tiene la matriz de pesos de la capa de embedding de entrada, y a qué corresponde estructuralmente buscar el embedding de un token concreto?

<details markdown="1"><summary>Comprobación</summary>

`vocab_size × d_model`. Buscar el embedding de un token es leer la fila de la matriz en el índice de ese token, una búsqueda directa y no una transformación calculada.

</details>

2. ▢ ¿Cómo se relaciona el shape de la capa de salida con el shape de la capa de embedding de entrada, y qué hace posible esa relación?

<details markdown="1"><summary>Comprobación</summary>

El shape de la capa de salida (`d_model × vocab_size`) es el transpuesto del shape del embedding de entrada (`vocab_size × d_model`). Esa relación es lo que hace posible el weight tying: la misma matriz, usada de una manera como tabla de búsqueda y de la otra (transpuesta) como proyección, puede cumplir ambos papeles en lugar de necesitar dos matrices aprendidas por separado.

</details>

3. ▢ Para un vocabulario de 50,000 tokens y `d_model = 768`, calcula el número de parámetros de la tabla de embeddings y explica qué ahorra el weight tying respecto de un modelo sin tying.

<details markdown="1"><summary>Pista</summary>

El número de parámetros de la tabla de embeddings es `vocab_size × d_model`. Una capa de salida sin tying necesitaría una matriz del mismo tamaño.

</details>

<details markdown="1"><summary>Comprobación</summary>

`50,000 × 768 = 38,400,000` parámetros para la tabla de embeddings. Un modelo sin tying necesitaría una segunda matriz, aprendida por separado, de ese mismo tamaño para la proyección de salida; el tying elimina esa segunda matriz entera, y ahorra unos 38.4 millones de parámetros para este vocabulario y este tamaño oculto.

</details>

4. ▢ Más allá de ahorrar parámetros, ¿cuál es el razonamiento de fondo por el que atar las matrices de pesos de entrada y de salida tiene sentido, en lugar de ser solo un truco cómodo?

<details markdown="1"><summary>Comprobación</summary>

Ambas capas relacionan un token con fundamentalmente la misma representación: el embedding de entrada responde a "qué vector representa a este token", y la capa de salida responde a "qué probabilidad tiene este token, dada la representación actual". Como ambas preguntas tratan de la misma relación entre token y vector, compartir una sola representación aprendida entre ellas es un sesgo inductivo razonable, no meramente una manera de recortar parámetros.

</details>

5. ▢ ¿Qué afirmación es cierta sobre las capas de embedding de entrada y de salida?

    - a) Siempre deben aprenderse como dos matrices totalmente separadas, ya que cumplen propósitos sin relación
    - b) Sus shapes son transpuestos uno del otro, que es lo que hace posible el weight tying, reutilizar una matriz para ambas
    - c) El weight tying solo ahorra parámetros y no aporta ningún otro beneficio
    - d) El shape de la capa de salida depende solo de `vocab_size`, sin relación con `d_model`

<details markdown="1"><summary>Comprobación</summary>

**b)** La relación de shapes transpuestos es exactamente lo que aprovecha el tying. (a) es falsa: eso es justo lo que el tying evita necesitar. (c) es falsa: también se sostiene que el tying ayuda a la calidad, ya que ambas capas se relacionan con la misma representación subyacente del token. (d) es falsa: el shape de la capa de salida es `d_model × vocab_size`, y depende de ambos.

</details>

## Prácticas en el mundo real

- [ ] Implementa primero la búsqueda del embedding de entrada y la proyección de salida como matrices separadas, y luego modifica tu implementación para atarlas y confirma que el shape de los logits de salida no cambia.
- [ ] Para un modelo que conozcas, busca el tamaño de su vocabulario y su `d_model`, y calcula cuántos parámetros ahorraría el weight tying frente a una versión sin tying.
- [ ] Mañana: comprueba si la implementación de un modelo real a la que tengas acceso (en la biblioteca `transformers` o en otra parte) ata sus pesos de embedding y de salida, y encuentra dónde se configura eso en el código.

## Para profundizar

- [Paper: "Using the Output Embedding to Improve Language Models", Press and Wolf, 2017](https://arxiv.org/abs/1608.05859)
- [Paper: "Attention Is All You Need", Vaswani et al., 2017](https://arxiv.org/abs/1706.03762)
- [Recursos](../RESOURCES.md)

---

¿No termina de quedar claro? Vuelve a leer la fuente primaria de arriba, ya que esta lección la comprime y en la compresión es donde se escapa la comprensión. Consulta el [glosario](../GLOSSARY.md) por si algún término te resultó resbaladizo.

Si lo poco claro es la propia lección y no el material, eso es un defecto: [abre un issue](https://github.com/TokenCemetery/teach/issues).
