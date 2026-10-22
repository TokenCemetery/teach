---
title: "9. Autoconsistencia y fidelidad"
description: "Muestrear varios caminos de razonamiento para votar una respuesta, y por qué el razonamiento escrito no es una explicación fiel"
type: lesson
---

# Lección 9. Autoconsistencia y fidelidad

**Vínculo con la misión:** Pedir razonamiento tiene dos consecuencias: puedes gastar más tokens para obtener una respuesta más estable, y no debes leer el razonamiento como prueba de por qué el modelo respondió como lo hizo.
**Fuente principal:** [Artículo: "Self-Consistency Improves Chain of Thought Reasoning in Language Models", Wang et al., 2022](https://arxiv.org/abs/2203.11171)
**Requisitos previos:** [Lección 8](0008-chain-of-thought.md), [Autoconsistencia](../GLOSSARY.md), [Chain-of-thought](../GLOSSARY.md)

## Calentamiento

1. ▢ La lección 7 decía que un prompt few-shot puede inclinarse hacia una respuesta según sus ejemplos y su orden. ¿Por qué eso hace que una sola respuesta muestreada sea menos confiable de lo que parece?

<details markdown="1"><summary>Comprobación</summary>

Una respuesta es una sola muestra de una distribución que el prompt ya ha inclinado. Si esa inclinación decide el resultado en un caso límite, volver a ejecutar o reordenar puede cambiarlo, así que una respuesta aislada no dice nada sobre lo frágil que es.

</details>

2. ▢ La lección 8 decía que el razonamiento ayuda sobre todo en tareas de varios pasos. Nombra una tarea de tu propio trabajo en la que ayudaría y una en la que no.

<details markdown="1"><summary>Comprobación</summary>

Sirve cualquier par que distinga varios pasos dependientes (un cálculo de varias partes, un horario con restricciones) de una consulta o etiqueta de un solo paso (extraer una fecha, etiquetar el sentimiento). La primera se gana los tokens de razonamiento; la segunda solo los paga.

</details>

## Qué debes saber

### Autoconsistencia: muestrear y luego votar

La decodificación greedy toma una sola chain-of-thought y confía en ella. Wang et al., en cambio, muestrean un conjunto de caminos de razonamiento a partir del mismo prompt y se quedan con la respuesta final que aparece más veces. La intuición que ofrecen es que un problema difícil admite muchas formas de pensar y una única respuesta correcta, de modo que los caminos erróneos tienden a discrepar entre sí mientras que los correctos convergen. Reportan mejoras sobre la chain-of-thought greedy de +17,9 % en GSM8K, +11,0 % en SVAMP, +12,2 % en AQuA, +6,4 % en StrategyQA y +3,9 % en ARC-challenge.

Esto es la **autoconsistencia**. De su funcionamiento se desprenden tres condiciones:

- **Debe haber una respuesta final que comparar.** La votación se hace sobre respuestas tomadas de un conjunto fijo, como un número o una opción, por lo que sirve para tareas con una única respuesta comprobable, no para escritura abierta.
- **Las muestras deben diferir.** El método del artículo funciona con métodos de muestreo como el muestreo por temperatura. Las muestras idénticas votan todas igual y no aportan nada.
- **Cuesta más.** Los autores señalan el cálculo adicional como la limitación y sugieren empezar con 5 o 10 caminos, ya que en la mayoría de los casos el rendimiento se satura rápido.

En una ventana de chat puedes aproximarla haciendo la misma pregunta en varios chats nuevos y tomando la mayoría, siempre que la interfaz muestree con algo de aleatoriedad.

### Fidelidad: el razonamiento no es la causa

Resulta tentador leer el razonamiento escrito como el proceso real del modelo. Turpin et al. lo pusieron a prueba añadiendo al prompt un rasgo que sesga, como reordenar los ejemplos few-shot para que la respuesta correcta sea siempre "(A)", o sugerir una respuesta en el prompt, y comprobando si el razonamiento escrito lo mencionaba.

No lo hacía. En 13 tareas de BIG-Bench Hard con GPT-3.5 y Claude 1.0, los rasgos que sesgan redujeron la precisión hasta en un 36 %, y el razonamiento nunca hacía referencia al rasgo. Cuando se empujaba a los modelos hacia una respuesta equivocada, a menudo escribían un razonamiento que la justificaba. Los autores llaman a esas explicaciones plausibles pero engañosas.

De ahí se siguen dos reglas prácticas:

- **No uses el razonamiento escrito como auditoría de por qué se dio la respuesta.** Puede ser un relato fluido que omite lo que impulsó la respuesta.
- **Prueba la influencia directamente.** Para saber si algo del prompt afecta la respuesta, cambia ese elemento y vuelve a ejecutar, como en los artículos, en lugar de pedirle al modelo que se explique.

Esto no vuelve inútil el razonamiento. Las mejoras de la lección 8 siguen en pie. Significa que el razonamiento ayuda a la respuesta y es un testigo débil sobre la causa.

## Práctica

1. ▢ Predice y luego ejecuta. Haz esta pregunta a un modelo de chat en tres chats nuevos e independientes y anota las tres respuestas finales. Predice si surge una mayoría.

    ```text
    A bat and a ball cost 1.10 dollars together. The bat costs 1.00
    dollar more than the ball. How much does the ball cost?
    Think it through, then end with "Answer:" and the amount.
    ```

<details markdown="1"><summary>Pista</summary>

La autoconsistencia solo ayuda si los caminos difieren y si la respuesta más común es la correcta.

</details>

<details markdown="1"><summary>Comprobación</summary>

La respuesta correcta es 5 centavos. Si los tres chats coinciden, la votación es unánime y las muestras extra solo aumentaron tu confianza. Si uno discrepa, la mayoría es tu respuesta, y el desacuerdo muestra que la pregunta no era segura de responder a partir de una sola muestra. También es posible una mayoría equivocada, y por eso la votación es una forma de gastar tokens en estabilidad, no una garantía. Prueba con una pregunta más difícil de varios pasos para ver desacuerdos con más frecuencia.

</details>

2. ▢ ¿Por qué la autoconsistencia le va mejor a "cuánto es el 17 por ciento de 240" que a "escribe una descripción de producto"?

<details markdown="1"><summary>Comprobación</summary>

La votación necesita respuestas finales que se puedan comparar por igualdad. Un número se puede, así que gana el más común. Una descripción de producto no tiene una respuesta única: cada muestra es distinta, así que no hay nada que votar, solo textos entre los que elegir.

</details>

3. ▢ Tu app le pide a un modelo una decisión de sí o no y le muestra al usuario su razonamiento escrito como explicación. Usando a Turpin et al., enuncia el riesgo y un cambio.

<details markdown="1"><summary>Comprobación</summary>

El riesgo es que el razonamiento puede omitir lo que realmente impulsó la decisión, o racionalizar una decisión moldeada por algo del prompt, como el orden de los ejemplos o una respuesta sugerida, de modo que a los usuarios se les mostraría un relato plausible que quizá no sea la causa. Un cambio: dejar de presentar el razonamiento escrito como la causa y etiquetarlo como la justificación del modelo, o probar directamente volviendo a ejecutar con la entrada sospechosa modificada. Cuál es la solución correcta depende de para qué usan los usuarios la explicación.

</details>

4. ▢ ¿Qué par describe correctamente lo que te da cada técnica?

    - a) La autoconsistencia aporta una respuesta más estable; las comprobaciones de fidelidad no se aplican
    - b) La autoconsistencia aporta una respuesta más estable; el razonamiento puede omitir la causa real
    - c) La autoconsistencia explica la respuesta; el razonamiento siempre nombra su causa real
    - d) La autoconsistencia reduce el costo al muestrear una sola vez; el razonamiento puede omitir la causa

<details markdown="1"><summary>Comprobación</summary>

**b)** Votar entre caminos muestreados estabiliza la respuesta final, y Turpin et al. muestran que el razonamiento escrito puede dejar fuera lo que lo impulsó. (a) es incorrecta porque la fidelidad se aplica a cualquier razonamiento que muestres. (c) es incorrecta por dos motivos: votar no explica, y el razonamiento no siempre nombra su causa. (d) es incorrecta porque la autoconsistencia cuesta más muestras, no menos.

</details>

## Prácticas en el mundo real

- [ ] Toma una pregunta que te importe y que tenga una única respuesta comprobable. Hazla en tres chats nuevos y anota si las respuestas coinciden.
- [ ] Encuentra un lugar donde hayas leído el razonamiento de un modelo como la razón de su respuesta, y anota qué probarías para comprobarlo.
- [ ] Mañana: toma un prompt de opción múltiple y reordena sus opciones para que se mueva la correcta, luego mira si el razonamiento del modelo menciona el cambio.

## Para profundizar

- [Few-Shot y razonamiento](../reference/few-shot-and-reasoning.md)
- [Artículo: "Language Models Don't Always Say What They Think", Turpin et al., 2023](https://arxiv.org/abs/2305.04388)
- [Recursos](../RESOURCES.md)

---

¿No termina de quedar claro? Vuelve a leer la fuente principal del inicio, porque esta lección la comprime y en la compresión es donde se pierde la comprensión. Consulta el [glosario](../GLOSSARY.md) para cualquier término que te haya parecido resbaladizo.

Si lo poco claro es la lección y no el material, eso es un defecto: [abre un issue](https://github.com/TokenCemetery/teach/issues).
