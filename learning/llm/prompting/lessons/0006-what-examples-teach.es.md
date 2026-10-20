---
title: "6. Qué enseñan los ejemplos few-shot"
description: "Las demostraciones enseñan sobre todo el formato, el espacio de etiquetas y la distribución de entrada, lo que cambia cómo las eliges"
type: lesson
---

# Lección 6. Qué enseñan los ejemplos few-shot

**Vínculo con la misión:** Elegir bien los ejemplos few-shot empieza por saber qué toma el modelo de ellos, y la evidencia dice que es menos las respuestas que la forma de la tarea.
**Fuente principal:** [Paper: "Rethinking the Role of Demonstrations", Min et al., 2022](https://arxiv.org/abs/2202.12837)
**Requisitos previos:** [Lección 5](0005-format-sensitivity.md), [Prompt few-shot](../GLOSSARY.md), [Prompt zero-shot](../GLOSSARY.md)

## Calentamiento

1. ▢ La lección 4 separó instrucciones y datos con etiquetas. Nombra una cosa de un prompt few-shot que debería ir dentro de su propia etiqueta, y por qué.

<details markdown="1"><summary>Comprobación</summary>

Los ejemplos, envueltos juntos (por ejemplo en una etiqueta examples con una etiqueta por ejemplo), para que el modelo pueda distinguir las demostraciones de las instrucciones y de la entrada real. Sin las etiquetas, un ejemplo puede leerse como una instrucción, o la entrada real como un ejemplo más.

</details>

2. ▢ La lección 5 dijo que un cambio de formato sin significado puede mover la precisión. ¿Qué predice eso sobre dos prompts few-shot cuyos ejemplos son idénticos pero uno escribe `Label:` y el otro `Answer:`?

<details markdown="1"><summary>Comprobación</summary>

Que su precisión puede diferir, así que no se sabe que ninguno sea mejor hasta probar ambos. La edición no cambia ningún significado, pero sí cambia la secuencia de tokens que el modelo continúa, que es el punto de la lección 5.

</details>

## Qué debes saber

### El resultado sorprendente

Un **prompt few-shot** muestra al modelo pares de entrada y salida antes de la entrada real. La suposición obvia es que el modelo aprende de ellos la correspondencia de entrada a salida, como un clasificador aprende de datos etiquetados. Min et al. pusieron a prueba esa suposición reemplazando las etiquetas de las demostraciones por otras aleatorias. En 12 modelos, incluido GPT-3, el rendimiento apenas cayó: de 0 a 5% absoluto en casi todos los modelos, 2.6% de media en tareas de clasificación y 1.7% en tareas de opción múltiple.

Si las etiquetas correctas no son lo que ayuda, algo más en las demostraciones debe serlo. El paper nombra tres cosas, y cada una se probó quitándola:

| Lo que aporta la demostración | Qué pasa cuando se quita |
|---|---|
| El espacio de etiquetas: el conjunto de respuestas que el modelo puede dar | Reemplazar las etiquetas por palabras inglesas aleatorias costó de 5 a 16% absoluto en los modelos directos |
| La distribución de entrada: texto que se parece a las entradas reales | Reemplazar las entradas por texto aleatorio de un corpus costó de 3 a 16% absoluto en la mayoría de los modelos probados |
| El formato: entrada y luego etiqueta, repetido | Eliminar el emparejamiento dejó el rendimiento cerca de, o peor que, el de no usar demostraciones |

### Lo que esto no dice

Tres límites evitan que esto se convierta en "las etiquetas no importan".

Los modelos fueron desde GPT-2 Large hasta GPT-3 (774M a 175B parámetros), y las tareas fueron de clasificación y de opción múltiple. El paper no prueba si un modelo de chat actual se comporta de la misma manera, así que trátalo como un prior fuerte y luego prueba tu propio modelo.

Las etiquetas aleatorias siguen costando algo, y el costo no fue uniforme: un modelo en clasificación cayó casi 10% cuando todas las etiquetas eran erróneas. "Apenas perjudica" es un promedio sobre los modelos y tareas probados.

Los autores señalan también que el aprendizaje en contexto puede no funcionar en una tarea cuya correspondencia entre entrada y etiqueta el modelo no ha captado ya. Las demostraciones localizan una tarea que el modelo en gran parte ya sabe hacer. Son una forma más débil de enseñarle una correspondencia que nunca ha visto.

### Cómo cambia esto la elección de ejemplos

Si el modelo lee del conjunto de ejemplos el formato, el espacio de etiquetas y la distribución de entrada, esas tres cosas son las que hay que acertar.

- **En el formato objetivo.** Cada ejemplo debería parecerse exactamente a la entrada real y a la salida que quieres, hasta en mayúsculas y puntuación. La lección 5 explica por qué las diferencias pequeñas no son gratuitas.
- **Cubriendo el espacio de etiquetas.** Muestra cada etiqueta que el modelo pueda producir, para que ninguna sea una sorpresa.
- **Como las entradas reales.** Usa texto de la distribución real, no frases inventadas y pulcras.

La guía de buenas prácticas de Anthropic dice lo mismo en términos de profesional: haz que los ejemplos sean relevantes (reflejen el caso de uso real), diversos (cubran casos límite y varíen lo suficiente para que el modelo no capte patrones no intencionados) y estructurados (envueltos en etiquetas), y sugiere de 3 a 5 ejemplos. Es el consejo documentado de un proveedor, no un resultado medido.

Nada de esto es una licencia para entregar etiquetas erróneas. Las etiquetas correctas no cuestan nada y evitan el peor caso del paper.

## Práctica

1. ▢ Predice y luego ejecuta. Pega este prompt en una ventana de chat. Las etiquetas de los tres ejemplos son erróneas a propósito. Predice qué produce el modelo para la última reseña y luego ejecútalo.

    ```text
    Classify each review as Positive or Negative.

    Review: The battery lasts all day and the screen is gorgeous.
    Label: Negative

    Review: It stopped working after two days and support never replied.
    Label: Positive

    Review: Arrived on time and works exactly as described.
    Label: Negative

    Review: Terrible fit, the zipper broke on the first use.
    Label:
    ```

<details markdown="1"><summary>Pista</summary>

Pregúntate qué enseñan aún los ejemplos aunque sus etiquetas sean erróneas: el formato, las dos palabras permitidas y cómo es una reseña.

</details>

<details markdown="1"><summary>Comprobación</summary>

Min et al. predicen una respuesta de una palabra del par permitido y, para una reseña inequívoca, lo más probable es que sea la correcta (Negative), porque el sentido propio que el modelo tiene de la tarea sobrevive a las etiquetas erróneas. Un modelo que en cambio copia la correspondencia intercambiada es un hallazgo sobre ese modelo, no un error del paper. En cualquier caso, el formato de salida (una sola palabra tras `Label:`) debería mantenerse, ya que el formato es lo que los ejemplos enseñaron de forma fiable.

</details>

2. ▢ ¿Qué cambio en un prompt few-shot que funciona predice el paper que perjudica más?

    - a) Intercambiar las etiquetas para que algunos ejemplos lleven una respuesta errónea
    - b) Reemplazar las entradas de los ejemplos por frases aleatorias de un corpus
    - c) Reordenar los mismos ejemplos manteniendo correcta cada etiqueta
    - d) Añadir un ejemplo más que coincida con el formato existente

<details markdown="1"><summary>Comprobación</summary>

**b)** Reemplazar las entradas por texto fuera de distribución costó de 3 a 16% absoluto en la mayoría de los modelos probados, más que las etiquetas erróneas (0 a 5% en casi todos). (a) es el titular del paper: costo pequeño. (c) no se prueba en este paper; el orden es el tema de la lección 7, y no es inofensivo. (d) añade una demostración en el formato correcto, lo que según el paper no cambia mucho los resultados una vez que hay unas 8.

</details>

3. ▢ Este prompt pretende etiquetar tickets de soporte. Nombra todas las formas en que sus ejemplos fallan en enseñar el formato, el espacio de etiquetas o la distribución de entrada, y di qué cambiarías.

    ```text
    Tag the ticket as billing, bug or account.

    Ticket: I was charged twice this month.
    Tag: billing

    This one is a bug report: The export button does nothing.
    bug

    Ticket: How do I change my email address?
    Tag: Account.
    ```

<details markdown="1"><summary>Pista</summary>

Compara los tres ejemplos línea por línea. ¿Comparten una disposición? ¿Comparten la ortografía y la puntuación de la etiqueta? Cuenta las etiquetas.

</details>

<details markdown="1"><summary>Comprobación</summary>

Formato: el segundo ejemplo omite `Ticket:` y `Tag:` y añade una frase de comentario, así que el patrón se rompe una vez. Espacio de etiquetas: `billing`, `bug` y `Account.` difieren en mayúsculas y puntuación, así que el modelo ve tres ortografías de etiqueta donde la tarea tiene tres etiquetas exactas. La etiqueta `Account.` con punto final enseña que la puntuación forma parte de la respuesta. Distribución de entrada: los tickets son de una línea corta cada uno y pueden no parecerse a tickets reales (que son más largos y desordenados). Arreglo: una sola disposición para todos los ejemplos, la ortografía exacta de la etiqueta cada vez y tickets copiados de los reales.

</details>

4. ▢ Un clasificador debe producir una de Billing, Bug, Account. De este grupo, elige los tres ejemplos que usarías y di por qué rechazaste el resto.

    ```text
    A. "I was charged twice for May" -> Billing
    B. "Why did my card get billed two times in May??" -> Billing
    C. "app crashes when I tap export, iOS 17, v4.2" -> Bug
    D. "Our blog post explains how crashes can be diagnosed" -> Bug
    E. "can't log in after changing my phone number" -> Account
    F. "Please update the invoice address" -> Billing
    ```

<details markdown="1"><summary>Comprobación</summary>

Una elección razonable es A, C y E: un ejemplo por etiqueta cubre el espacio de etiquetas, comparten disposición y su redacción tosca y de aspecto real coincide con la distribución de entrada. B es casi un duplicado de A, así que no aporta diversidad. D es prosa pulida que no parece un ticket (un desajuste de distribución de entrada) y está etiquetada Bug por la razón equivocada. F está bien por sí sola, pero un segundo ejemplo de Billing antes que cualquier otra etiqueta arriesga el sesgo que cubre la lección 7. Otras elecciones son defendibles si cubren las tres etiquetas y evitan D.

</details>

## Prácticas en el mundo real

- [ ] Toma un prompt few-shot que ya uses. Lista cuáles de formato, espacio de etiquetas y distribución de entrada muestra cada ejemplo, y marca cualquier ejemplo que no muestre ninguno.
- [ ] Ejecuta un prompt dos veces, una con ejemplos reales y otra con los mismos ejemplos reetiquetados al azar, sobre cinco entradas. Anota cuántas respuestas cambiaron.
- [ ] Mañana: reescribe un prompt few-shot para que todos los ejemplos compartan una disposición y la ortografía exacta de las etiquetas, luego ejecútalo sobre las mismas cinco entradas y compara.

## Para profundizar

- [Few-Shot y razonamiento](../reference/few-shot-and-reasoning.md)
- [Paper: "Rethinking the Role of Demonstrations", Min et al., 2022](https://arxiv.org/abs/2202.12837)
- [Docs: "Prompting best practices", Claude Platform Docs](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/claude-prompting-best-practices#use-examples-effectively)
- [Recursos](../RESOURCES.md)

---

¿No termina de quedar claro? Vuelve a leer la fuente primaria de arriba, ya que esta lección la comprime y en la compresión es donde se escapa la comprensión. Consulta el [glosario](../GLOSSARY.md) por si algún término te resultó resbaladizo.

Si lo poco claro es la propia lección y no el material, eso es un defecto: [abre un issue](https://github.com/TokenCemetery/teach/issues).
