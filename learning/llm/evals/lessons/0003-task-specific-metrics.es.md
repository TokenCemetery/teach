---
title: "3. Métricas específicas de la tarea"
description: "Coincidencia exacta, F1 a nivel de token y BLEU/ROUGE, y el modo de fallo de cada una"
type: lesson
---

# Lección 3. Métricas específicas de la tarea

**Vínculo con la misión:** La etapa 2 abre la mitad de "construir la eval" de la misión: una métrica específica de la tarea convierte un conjunto held-out (etapa 1) en un número real, y cada métrica que cubre esta lección encaja bien con algunas tareas y miente en silencio sobre otras.
**Fuente principal:** [Docs: Evaluate, Hugging Face](https://huggingface.co/docs/evaluate/index)
**Requisitos previos:** [Lección 2](0002-designing-contamination-resistance.md), [Contaminación de datos](../GLOSSARY.md)

## Calentamiento

1. ▢ ¿Contra qué protege realmente incrustar una canary string en un conjunto de eval propio?

<details markdown="1"><summary>Comprobación</summary>

Señala a los rastreadores que arman un corpus de entrenamiento que el contenido marcado debe excluirse, y da una forma de detectar una fuga más tarde si la cadena aparece en la salida de un modelo o en un corpus accesible. Es una petición, no una garantía: depende de que los rastreadores respeten la convención.

</details>

2. ▢ ¿Cuándo se puede usar una comprobación de solapamiento de n-gramas contra un corpus conocido, y cuándo deja de ser una opción?

<details markdown="1"><summary>Comprobación</summary>

Se puede usar cuando el corpus de preentrenamiento es conocido y accesible. Deja de ser una opción para un modelo cerrado con datos de entrenamiento no divulgados, donde la prueba de instrucción guiada sigue siendo la herramienta disponible.

</details>

## Qué debes saber

### Coincidencia exacta: estricta y frágil ante cualquier variación superficial

La **coincidencia exacta** puntúa una predicción como correcta solo si coincide con una respuesta de referencia carácter por carácter (a menudo tras una normalización ligera, como pasar a minúsculas o quitar espacios). Encaja con tareas que tienen una única respuesta claramente correcta: opción múltiple, extracción de un fragmento, un resultado matemático. Su modo de fallo es justo lo que implica su rigidez: una respuesta correcta formulada de otra manera (`"Paris"` frente a una referencia de `"Paris, France"`) puntúa como errónea, de modo que penaliza la corrección en lugar de medirla, a menos que la normalización aplicada sea lo bastante generosa para absorber esa variación sin absorber también respuestas genuinamente erróneas.

### F1 a nivel de token: crédito parcial, al costo de ignorar el orden

El **F1** (tal como se usa en tareas extractivas, como la respuesta a preguntas basada en fragmentos) trata una predicción y una referencia como bolsas de tokens en lugar de exigir una coincidencia exacta de cadena, y calcula la precisión (qué fracción de los tokens de la predicción es correcta) y el recall (qué fracción de los tokens de la referencia se produjo), y luego su media armónica. La referencia "the cat sat on the mat" (tokens: `the, cat, sat, on, the, mat`) frente a la predicción "a cat sat on the mat" (tokens: `a, cat, sat, on, the, mat`) comparte cinco tokens (`cat, sat, on, the, mat`) de seis en cada una: precisión `5/6`, recall `5/6`, F1 `5/6 ≈ 0.83`. Es más indulgente que la coincidencia exacta, que puntuaría este par como un error rotundo. El modo de fallo es lo que cuesta esa indulgencia: el F1 sobre una bolsa de tokens es ciego al orden y a si las palabras que se solapan se combinan realmente en una respuesta correcta, de modo que una predicción que mezcla las palabras correctas en una afirmación equivocada aún puede puntuar alto.

![La referencia "the cat sat on the mat" y la predicción "a cat sat on the mat" dispuestas como cajas de tokens. cat, sat, on, mat y una instancia de the son compartidos entre ambas. El segundo the de la referencia y el a de la predicción quedan sin emparejar. Cinco de seis tokens coinciden en cada lado, así que la precisión es 5/6, el recall es 5/6 y el F1 es 5/6.](images/f1-token-overlap.svg)

### BLEU y ROUGE: solapamiento de n-gramas con una referencia, pensados para traducción y resumen

**BLEU** (originalmente para traducción automática) y **ROUGE** (originalmente para resumen) puntúan un texto generado según cuánto se solapan sus n-gramas (secuencias contiguas de tokens de longitud n) con uno o más textos de referencia, en lugar de exigir una coincidencia exacta o puntuar tokens sueltos de forma aislada. Su modo de fallo se nota más en la generación abierta: una paráfrasis válida que dice lo mismo con otras palabras, "Critics praised the show" frente a una referencia de "The show received positive reviews from critics", comparte muy pocos n-gramas con la referencia pese a ser una respuesta igual de buena, y por eso puntúa bajo. Usar varios textos de referencia por ejemplo lo suaviza, pero rara vez existen suficientes referencias para cubrir cada formulación válida, lo que explica en buena parte por qué estas métricas se correlacionan solo de forma laxa con el juicio humano en texto abierto, y por qué el LLM-as-judge de la etapa 3 existe como alternativa justo para ese caso.

### Elegir una métrica es ajustarla a lo que significa "correcto" para la tarea

La coincidencia exacta y el F1 encajan con tareas donde la corrección es un conjunto pequeño y bien definido de respuestas: clasificación, extracción, aritmética. BLEU y ROUGE encajan con tareas donde el solapamiento superficial con una referencia se correlaciona, de forma laxa, con la calidad, útiles como filtro grueso y barato de primera pasada y no como veredicto final. Ninguna de las dos familias sirve para una tarea donde la corrección es de comportamiento y no textual (si el código generado realmente se ejecuta y produce la salida correcta), que es el tema de la lección 4, ni para la generación abierta donde importa más el significado que la redacción, que es el de la etapa 3.

## Práctica

1. ▢ Un modelo responde una pregunta de geografía con "Paris" mientras que la respuesta de referencia es "Paris, France". La coincidencia exacta lo puntúa como erróneo. ¿Es ese un resultado de puntuación correcto? ¿Por qué sí o por qué no?

<details markdown="1"><summary>Comprobación</summary>

No, en realidad no: la respuesta es correcta, solo que formulada de forma más escueta que la referencia. Es la fragilidad de la coincidencia exacta ante la variación superficial. La corrección es normalizar ambas cadenas antes de comparar (lo cual solo ayuda si la normalización está diseñada para absorber este tipo concreto de variación) o elegir una métrica más indulgente para una tarea donde la formulación varía tanto.

</details>

2. ▢ Referencia: "a fast red fox jumps". Predicción: "a red fox jumps fast". Usando F1 de bolsa de tokens (ignorando el orden de las palabras), ¿cuáles son la precisión, el recall y la puntuación F1?

<details markdown="1"><summary>Pista</summary>

Enumera los tokens de cada lado como un conjunto y cuenta cuántos se comparten, sin importar la posición.

</details>

<details markdown="1"><summary>Comprobación</summary>

Ambos lados tienen los mismos 5 tokens (`a, fast, red, fox, jumps` frente a `a, red, fox, jumps, fast`), solo que reordenados, así que los 5 se comparten. Precisión `5/5 = 1.0`, recall `5/5 = 1.0`, F1 `1.0`. Esto demuestra además la ceguera del F1 ante el orden: una predicción con el orden de palabras revuelto puntúa igual que una que lo conserva, aunque el orden de las palabras pueda cambiar el significado de una forma que el F1 no puede detectar.

</details>

3. ▢ Un modelo de resumen produce "Critics praised the show" para un resumen de referencia "The show received positive reviews from critics." ¿ROUGE puntuaría probablemente este par alto o bajo, y es ese resultado un reflejo justo de la calidad de la predicción?

<details markdown="1"><summary>Comprobación</summary>

Bajo, ya que las dos oraciones comparten muy pocos n-gramas contiguos pese a decir esencialmente lo mismo con otras palabras. No es un reflejo justo de la calidad: la predicción es una paráfrasis válida, pero ROUGE mide el solapamiento superficial de n-gramas, no el significado, así que una respuesta correcta formulada de forma distinta a la referencia se penaliza igual que una errónea.

</details>

4. ▢ Un equipo evalúa un modelo con un benchmark de opción múltiple con una letra correcta por pregunta. ¿Qué métrica de esta lección encaja mejor, y por qué?

<details markdown="1"><summary>Comprobación</summary>

La coincidencia exacta. La tarea tiene exactamente una respuesta correcta por pregunta, sin variación superficial relevante que absorber (la respuesta es una sola letra), que es justo la forma de tarea para la que se construyó la coincidencia exacta, sin necesitar en absoluto la indulgencia del F1 o de BLEU/ROUGE con el solapamiento parcial o parafraseado.

</details>

5. ▢ ¿Qué afirmación es cierta sobre BLEU y ROUGE en comparación con la coincidencia exacta y el F1?

    - a) Exigen una única respuesta correcta e inequívoca, igual que la coincidencia exacta
    - b) Puntúan el solapamiento con el texto de referencia a nivel de n-grama, lo que se correlaciona solo de forma laxa con la calidad en la generación abierta
    - c) Son inmunes al problema de la paráfrasis que afecta a la coincidencia exacta
    - d) Es mejor usarlas como veredicto final en cualquier tarea de generación, en sustitución del juicio humano o de un LLM

<details markdown="1"><summary>Comprobación</summary>

**b)** El solapamiento de n-gramas es un indicador laxo de la calidad, sobre todo cuando las respuestas válidas pueden formularse de muchas maneras distintas. (a) es falsa: están pensadas para tareas con texto abierto, no para una única respuesta fija. (c) es falsa: una paráfrasis válida puede puntuar bajo en BLEU/ROUGE por la misma razón de fondo por la que puede fallar la coincidencia exacta, una redacción superficial distinta. (d) es falsa: su débil correlación con el juicio humano en texto abierto es justo la razón por la que la etapa 3 introduce LLM-as-judge como alternativa.

</details>

## Prácticas en el mundo real

- [ ] Elige una tarea que evalúes (o planees evaluar) y decide cuál entre coincidencia exacta, F1 o BLEU/ROUGE encaja con su noción de "correcto", escribiendo por qué.
- [ ] Para una eval que hoy usa BLEU o ROUGE, encuentra un ejemplo en que una respuesta claramente correcta pero con otra redacción puntuaría mal, y anótalo.
- [ ] Mañana: lee un párrafo de la documentación de Hugging Face Evaluate sobre una métrica que no hayas usado antes y anota su modo de fallo declarado.

## Para profundizar

- [Docs: Evaluate, Hugging Face](https://huggingface.co/docs/evaluate/index)
- [Docs: "Define success criteria and build evaluations", Claude Platform Docs](https://platform.claude.com/docs/en/test-and-evaluate/develop-tests)
- [Recursos](../RESOURCES.md)

---

¿No termina de quedar claro? Vuelve a leer la fuente primaria de arriba, ya que esta lección la comprime y en la compresión es donde se escapa la comprensión. Consulta el [glosario](../GLOSSARY.md) por si algún término te resultó resbaladizo.

Si lo poco claro es la propia lección y no el material, eso es un defecto: [abre un issue](https://github.com/TokenCemetery/teach/issues).
