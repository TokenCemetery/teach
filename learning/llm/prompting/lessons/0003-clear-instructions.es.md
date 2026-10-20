---
title: "3. Instrucciones claras"
description: "Escribe una instrucción que una persona nueva y capaz pudiera seguir: contexto, la tarea, las restricciones y cómo se ve algo terminado"
type: lesson
---

# Lección 3. Instrucciones claras

**Vínculo con la misión:** La mayoría de los prompts que fallan no son modelos engañados o confundidos, sino peticiones poco especificadas, así que la mejora más barata de cualquier prompt es decir lo que necesitaría saber un desconocido capaz.
**Fuente principal:** [Docs: "Prompting best practices", Claude Platform Docs](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/claude-prompting-best-practices#be-clear-and-direct)
**Requisitos previos:** [Lección 2](0002-system-prompts-and-roles.md), [Prompt zero-shot](../GLOSSARY.md)

## Calentamiento

1. ▢ Una línea dice "Reply in at most three sentences." ¿Pertenece al system prompt o al turno del usuario, y por qué?

<details markdown="1"><summary>Comprobación</summary>

Al system prompt, porque debería valer en cada petición, no solo en esta.

</details>

2. ▢ El prompt renderizado de un chat termina con el marcador de rol del asistente. ¿Qué hace el modelo a partir de ahí?

<details markdown="1"><summary>Comprobación</summary>

Continúa la secuencia de tokens desde ese punto, que es como escribe la respuesta.

</details>

## Qué debes saber

### La prueba del colega

La guía de Anthropic te pide que pienses en el modelo como un empleado brillante pero nuevo, que carece de contexto sobre tus normas y flujos de trabajo. Su regla de oro: muestra tu prompt a un colega con un contexto mínimo sobre la tarea y pídele que lo siga. Si se confundiría, el modelo también.

El modelo no puede preguntar qué querías decir, así que todo lo que omites lo rellena con una suposición. La guía dice también que si quieres un comportamiento que vaya "más allá", debes pedirlo explícitamente en lugar de confiar en que el modelo lo infiera de un prompt vago.

### Cuatro partes de una instrucción clara

| Parte | Responde | Ejemplo |
|---|---|---|
| Contexto | ¿Para quién es y por qué importa? | "These summaries go to busy support managers who read on their phones." |
| Tarea | ¿Qué hay que hacer exactamente? | "Summarise the ticket below." |
| Restricciones | ¿Qué límites se aplican? | "At most 40 words. No customer names." |
| Cómo se ve algo terminado | ¿Cómo sabrás que funcionó? | "A manager can decide whether to open the ticket from the summary alone." |

La guía de Anthropic dice que dar la motivación detrás de una instrucción, como por qué importa un comportamiento, puede ayudar al modelo a dar respuestas más enfocadas. La guía de diseño de prompts de Google también lista las restricciones y el formato de respuesta como cosas que especificar. "Cómo se ve algo terminado" es la parte que más a menudo falta, y es también la que necesitarás más adelante cuando pruebes un cambio de prompt contra un conjunto de regresión.

### Di qué hacer y numera los pasos que deben darse en orden

La guía de Anthropic recomienda decirle al modelo qué hacer en lugar de qué no hacer: en vez de "Do not use markdown", escribe "Your response should be composed of smoothly flowing prose paragraphs." Sugiere también pasos numerados secuenciales cuando importan el orden o la completitud de los pasos.

### Un antes y un después

```text
Summarise this ticket.
```

```text
You are helping a support team triage tickets. The summaries are read by managers on their phones, who decide from the summary alone whether to open the ticket.
Summarise the ticket below in at most 40 words, in plain prose, leaving out customer names. State the problem first and the customer's requested outcome last.
```

El segundo prompt es más largo porque lleva contexto, restricciones y un propósito. Su longitud añadida es información, no decoración.

## Práctica

1. ▢ Nombra las cuatro partes de una instrucción clara de esta lección y, para el prompt "Write a product description.", di cuáles faltan.

<details markdown="1"><summary>Comprobación</summary>

Contexto, tarea, restricciones y cómo se ve algo terminado. El prompt solo tiene una tarea, y vaga. Faltan: para quién es la descripción y dónde aparece, sus límites de longitud y tono, y el estándar que tiene que cumplir.

</details>

2. ▢ Reescribe "Don't write long answers." para que le diga al modelo qué hacer en su lugar.

<details markdown="1"><summary>Comprobación</summary>

Por ejemplo: "Answer in two or three sentences." Nombra el comportamiento deseado y da un límite medible, lo que además lo hace comprobable. Una instrucción negativa dice qué evitar pero deja que el modelo adivine la alternativa.

</details>

3. ▢ ¿Cuál reescritura de "Make this email better" es la más clara?

    - a) Improve this email so that it reads more professionally, clearly and persuasively overall
    - b) Rewrite this email for an upset customer in under 120 words, apologising first
    - c) Fix any problems in this email and make it sound good to the reader
    - d) Edit this email as an expert writer would, with attention to quality

<details markdown="1"><summary>Comprobación</summary>

**b)** Nombra la audiencia, un límite de longitud y un requisito de orden, así que otra persona podría comprobar el resultado. (a), (c) y (d) replantean "mejor" con otras palabras sin decir qué significa mejor.

</details>

4. ▢ Predice y luego ejecuta. Elige una tarea que hagas a menudo, como "Write a short bio." Escribe el prompt en cinco palabras y envíalo. Predice tres cosas que la respuesta hará mal para tu propósito, luego reescribe el prompt con las cuatro partes y envíalo de nuevo. ¿Cuáles de tus tres predicciones se corrigieron y qué problemas aparecieron que no habías previsto?

<details markdown="1"><summary>Pista</summary>

Entrega primero el prompt de cinco palabras a un compañero de trabajo. Lo que te preguntaría es lo que el modelo está adivinando.

</details>

<details markdown="1"><summary>Comprobación</summary>

Resultados típicos: la primera respuesta adivina la audiencia, la longitud y el tono. La segunda elimina esas suposiciones, pero puede añadir un problema nuevo, a menudo una restricción que entra en conflicto con otra. Guarda ambas respuestas: la diferencia entre ellas es la primera comparación que puedes mostrar a alguien, y la lección 18 convierte ese hábito en un conjunto de regresión.

</details>

## Prácticas en el mundo real

- [ ] Toma un prompt que enviaste esta semana y que dio una respuesta decepcionante, y marca cuáles de contexto, tarea, restricciones y cómo-se-ve-algo-terminado le faltaban.
- [ ] Entrega un prompt que hayas escrito a un colega sin contexto y pregúntale qué tendría que adivinar. Añade una línea por cada suposición.
- [ ] Mañana: reemplaza un "no" de un prompt que uses por una instrucción positiva y compara las respuestas con la misma entrada.

## Para profundizar

- [Docs: "Prompt design strategies", Gemini API, Google](https://ai.google.dev/gemini-api/docs/prompting-strategies): la guía de un segundo proveedor sobre restricciones y formato de respuesta.
- [Anatomía de un prompt](../reference/prompt-anatomy.md)
- [Recursos](../RESOURCES.md)

---

¿No termina de quedar claro? Vuelve a leer la fuente primaria de arriba, ya que esta lección la comprime y en la compresión es donde se escapa la comprensión. Consulta el [glosario](../GLOSSARY.md) por si algún término te resultó resbaladizo.

Si lo poco claro es la propia lección y no el material, eso es un defecto: [abre un issue](https://github.com/TokenCemetery/teach/issues).
