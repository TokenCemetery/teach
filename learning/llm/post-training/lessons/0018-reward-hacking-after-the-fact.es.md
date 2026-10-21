---
title: "18. Reward hacking a posteriori"
description: "Un reward model held-out puede detectar la deriva durante el entrenamiento; un modelo terminado necesita otro tipo de comprobación"
type: lesson
---

# Lección 18. Reward hacking a posteriori

**Vínculo con la misión:** "Poder separar una mejora genuina de capacidad de un artefacto del reward hacking o del sesgo del juez" es el punto de Cómo se ve el éxito al que sirve esta etapa, y esta lección lo cierra, y pasa el relevo de la metodología completa a `llm/evals` en lugar de reexponerla.
**Fuente principal:** [Referencia: "LLM-as-judge", `llm/evals`](../../evals/reference/llm-as-judge.md)
**Requisitos previos:** [Lección 17](0017-measuring-the-alignment-tax.md), [Sobrerrechazo](../../evals/GLOSSARY.md)

## Calentamiento

1. ▢ ¿Por qué probaron Ouyang et al. InstructGPT con anotadores held-out, personas que no aportaron ningún dato de entrenamiento?

<details markdown="1"><summary>Comprobación</summary>

Para comprobar si el comportamiento alineado del modelo generaliza más allá de las personas concretas cuyas preferencias moldearon el entrenamiento, en lugar de ajustarse solo de cerca a ese grupo particular.

</details>

2. ▢ ¿Qué añadió la reducción del 25 % de las salidas tóxicas a una contabilidad justa del impuesto de alineación, además de las regresiones de SQuAD/DROP/HellaSwag/WMT?

<details markdown="1"><summary>Comprobación</summary>

Evidencia de que el entrenamiento de alineación ayudó de forma medible en al menos un eje, y no solo costó algo; una contabilidad justa necesita ambas direcciones, no solo las regresiones.

</details>

## Qué debes saber

### Una pregunta distinta de la comprobación durante el entrenamiento

La divergencia entre train PM y test PM de la lección 5 es una comprobación que se hace *durante* el entrenamiento, y compara una policy con un reward model contra el que nunca se optimizó. Evaluar un modelo alineado *terminado* plantea una pregunta relacionada pero distinta: dados solo el modelo y sus puntuaciones de evaluación, sin un segundo reward model con el que comparar, ¿cómo saber si una puntuación alta refleja una mejora genuina y no un artefacto de cómo se construyó la propia evaluación?

### Un síntoma concreto: el sobrerrechazo

`llm/evals` nombra un fallo concreto y bien documentado del que trata de verdad esta pregunta: el **sobrerrechazo (over-refusal)**, un modelo que rechaza un prompt que en realidad es seguro, normalmente porque se parece superficialmente a uno inseguro. Un modelo que rechaza con agresividad puede puntuar de forma engañosamente buena en un benchmark de seguridad construido sobre todo con prompts inseguros, ya que rechazar casi todo se ve idéntico a un modelo genuinamente cuidadoso en esa prueba concreta, mientras falla en silencio en el conjunto mucho mayor de prompts seguros que debería haber respondido. Este es el fallo de evasión generalizada de la lección 5 y la lección 15, visto desde el lado de la evaluación y no del entrenamiento: una eval de estilo red-team que solo comprueba prompts inseguros no puede detectarlo, porque el sobrerrechazo es un fallo en los prompts seguros que la eval nunca planteó.

### El sesgo del juez es el mismo problema, un nivel más arriba

Cuando una evaluación usa ella misma un modelo, en lugar de un benchmark fijo, para juzgar las salidas (una configuración cada vez más común de la que ya dependen las propias lecciones de RLAIF y Constitutional AI de este track), ese juez puede ser engañado de maneras propias: prefiriendo las respuestas más largas sin importar la calidad, o dejándose influir por cuál de las respuestas se muestra primero. La referencia de `llm/evals` sobre el diseño de LLM-as-judge cubre estos modos de fallo, y las comprobaciones de calibración que los detectan, en su totalidad. Una puntuación alta asignada por un juez es tan fiable como la propia calibración del juez frente a estos sesgos conocidos; un juez sin calibrar puede ser burlado por una policy de una manera que, desde fuera, se ve exactamente como una mejora genuina.

### Por qué esto pasa el relevo en lugar de reexponerse

Diseñar el prompt de un juez, comprobar la calibración de un juez y medir el acuerdo de un juez frente a evaluadores humanos son el propio tema de `llm/evals`, cubierto allí con la profundidad que este track no necesita repetir. Lo que este track posee es más estrecho y específico del post-training: saber que la propia evaluación de un pipeline de post-training está expuesta exactamente a este riesgo, reconocer un síntoma concreto como el sobrerrechazo cuando aparece, y tratar una puntuación de seguridad o de preferencia sospechosamente alta con el mismo escepticismo que ya modeló durante el entrenamiento la comparación de train PM frente a test PM de la lección 5.

## Práctica

1. ▢ Un benchmark de seguridad compuesto enteramente por prompts inseguros informa de que un modelo rechaza el 98 % de ellos, una puntuación en apariencia excelente. ¿Qué no te dice este benchmark, por sí solo, sobre el modelo?

<details markdown="1"><summary>Comprobación</summary>

Si el modelo también rechaza prompts que en realidad son seguros. Un benchmark construido solo con prompts inseguros no puede detectar el sobrerrechazo, ya que un modelo que rechaza casi todo se ve idéntico a uno genuinamente cuidadoso en esta prueba concreta.

</details>

2. ▢ ¿Por qué es un modelo que rechaza un prompt realmente seguro un fallo genuinamente distinto de que un jailbreak tenga éxito?

<details markdown="1"><summary>Comprobación</summary>

Un jailbreak es que el modelo no rechace algo que debería haber rechazado; el sobrerrechazo es que el modelo rechace algo que no debería haber rechazado. Son fallos en direcciones opuestas, y una eval construida para detectar uno (un benchmark de red-team solo con prompts inseguros) no puede detectar el otro.

</details>

3. ▢ Una evaluación usa un modelo de lenguaje como juez para puntuar cuál de dos salidas de un modelo alineado es mejor. ¿Qué dice esta lección que deberías comprobar antes de fiarte de una gran brecha entre las puntuaciones de dos modelos?

<details markdown="1"><summary>Comprobación</summary>

Si el propio juez está calibrado frente a sesgos conocidos (como favorecer las respuestas más largas o la que aparece primero), según el material de LLM-as-judge de `llm/evals`; un juez sin calibrar puede ser burlado de una manera que produce una brecha de puntuación que parece una mejora genuina pero no lo es.

</details>

## Prácticas en el mundo real

- [ ] Lee [Referencia: "LLM-as-judge", `llm/evals`](../../evals/reference/llm-as-judge.md) e identifica una comprobación de calibración que recomiende y que aplicarías a una evaluación de post-training antes de fiarte de sus resultados.
- [ ] Busca una evaluación de seguridad publicada para un modelo alineado y comprueba si informa de una tasa de sobrerrechazo en prompts seguros, además de una tasa de rechazo en los inseguros. Anota cuál de las dos, si alguna, falta.
- [ ] Mañana: para una evaluación a la que tengas acceso o que puedas imaginar (un benchmark de seguridad, una configuración de juez de preferencias), nombra un síntoma concreto, como el sobrerrechazo o un sesgo conocido del juez, que comprobarías antes de fiarte de una puntuación destacada de ella.

## Para profundizar

- [Referencia: "LLM-as-judge", `llm/evals`](../../evals/reference/llm-as-judge.md)
- [Recursos](../RESOURCES.md)

---

La etapa 9 cubrió la separación de una ganancia de alineación genuina de un artefacto, en el momento del entrenamiento y a posteriori. La etapa 10 cierra el arco: elegir entre todo lo que ha cubierto este track, para un presupuesto dado, y defender esa elección.

¿No termina de quedar claro? Vuelve a leer la fuente primaria de arriba, ya que esta lección la comprime y en la compresión es donde se escapa la comprensión. Consulta el [glosario](../GLOSSARY.md) por si algún término te resultó resbaladizo.

Si lo poco claro es la propia lección y no el material, eso es un defecto: [abre un issue](https://github.com/TokenCemetery/teach/issues).
