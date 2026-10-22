---
title: 24. Cuando el consejo habitual es erróneo
description: Reconoce cuándo el consejo estándar de prompting falla para un modelo o tarea concretos, y zanja la disputa desde la fuente primaria
type: lesson
---

# Lección 24. Cuando el consejo habitual es erróneo

**Vínculo con la misión:** El track termina con la confianza en que puedas tomar la decisión sobre un prompt y explicársela a otra persona. El consejo de prompting se difunde como eslóganes, y un eslogan es cierto para algunos modelos, tareas y fechas y falso para otros. Esta lección es el método para averiguar cuál es el caso.
**Fuente principal:** [Paper: "When 'A Helpful Assistant' Is Not Really Helpful: Personas in System Prompts Do Not Improve Performances of Large Language Models", Zheng et al., 2023](https://arxiv.org/abs/2311.10054)
**Requisitos previos:** [Lección 2](0002-system-prompts-and-roles.md), [Lección 7](0007-few-shot-biases.md), [Lección 10](0010-prompting-reasoning-models.md), [Lección 18](0018-a-regression-set-for-a-prompt.md), [Lección 23](0023-reviewing-a-production-prompt.md)

## Calentamiento

1. ▢ ¿Por qué un prompt para un modelo de razonamiento da objetivos y restricciones en lugar de pasos guionizados?

<details markdown="1"><summary>Comprobación</summary>

El modelo ya produce su propia fase de razonamiento, así que un plan escrito a mano puede limitarlo a una ruta peor que la que encontraría por sí mismo. Di qué debe satisfacer la respuesta y deja que decida cómo llegar.

</details>

2. ▢ ¿Qué enseñan sobre todo los ejemplos few-shot, según la lección 6?

<details markdown="1"><summary>Comprobación</summary>

El formato, el espacio de etiquetas y la distribución de las entradas, más que la corrección de cada etiqueta. Por eso elegirlos por cobertura y orden importa más que pulir cada uno.

</details>

3. ▢ ¿Qué va en un conjunto de regresión y para qué sirve en una disputa sobre un prompt?

<details markdown="1"><summary>Comprobación</summary>

Entradas construidas sobre todo a partir de fallos reales, cada una con una comprobación sobre la salida. En una disputa es el terreno neutral: dos personas que discuten desde papers distintos pueden ejecutar ambas su prompt preferido sobre él y comparar.

</details>

## Qué debes saber

### El método

Un eslogan como "dale un rol al modelo" o "añade siempre una instrucción de paso a paso" llega sin sus condiciones. El método para decidir si se cumple en tu caso tiene cuatro pasos:

1. **Encuentra la fuente primaria.** No el artículo de blog que la cita. El paper o la documentación del proveedor, leídos para ver qué se midió realmente.
2. **Comprueba el modelo y la fecha.** Qué modelos, qué tarea, qué año. El consejo de 2022 sobre una familia de modelos puede no describir el modelo al que llamas hoy, y la guía de un proveedor describe los modelos de ese proveedor.
3. **Comprueba qué cubre la afirmación.** La precisión en preguntas factuales no es el tono. Un resultado en clasificación corta no es un resultado en redacción.
4. **Prueba en tu conjunto de regresión.** Si la fuente y tu caso pueden diferir, el resultado que lo zanja es el tuyo (lecciones 18 y 19).

Los casos de abajo aplican cada uno este método. Ninguno dice que el consejo habitual sea siempre erróneo. Cada uno dice qué respalda la fuente primaria.

### Caso 1: "Dale un rol al modelo"

La guía de Anthropic dice: "Definir un rol en el system prompt enfoca el comportamiento y el tono de Claude para tu caso de uso" ([Anthropic: prompting best practices](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/claude-prompting-best-practices)). Zheng et al. probaron si los personajes ayudan en tareas objetivas. Seleccionaron 162 roles de 6 tipos de relación interpersonal y 8 dominios de experiencia, y probaron 4 familias de LLM con 2,410 preguntas factuales. Su hallazgo: añadir un personaje "no mejora el rendimiento del modelo en un rango de preguntas en comparación con el ajuste de control en el que no se añade ningún personaje". El género, el tipo y el dominio del personaje todavía pueden cambiar la precisión, así que el efecto "puede ser en gran medida aleatorio", y elegir automáticamente el mejor personaje para una pregunta "a menudo no era mejor que una selección aleatoria".

Los dos no se contradicen, porque afirman cosas distintas: tono y comportamiento frente a precisión en preguntas factuales. La lectura que sobrevive a ambos: conserva un rol donde quieras una voz o un alcance, no esperes que haga los hechos más precisos, y cuando alguien diga que un personaje "mejora la precisión", pide la prueba. Los modelos del paper son los de 2023, así que la parte fechada de la respuesta es "para esos modelos y esas preguntas".

### Caso 2: "Think step by step"

La frase viene del resultado de razonamiento zero-shot (Kojima et al., 2022, incluido en [Recursos](../RESOURCES.md)), que es anterior a los modelos con thinking integrado. Para un modelo que piensa antes de responder, la guía actual de Anthropic recomienda el hábito contrario: "Un prompt como 'piensa a fondo' a menudo produce mejor razonamiento que un plan paso a paso escrito a mano", y para varios modelos nombrados dice que hay que apoyarse en el thinking integrado, porque un prompt que pide al modelo escribir su razonamiento "puede ser rechazado". Mantiene el chain-of-thought manual solo como alternativa para cuando el thinking está desactivado. La lección 10 cubre la mecánica.

La disputa que hay que zanjar es por tanto "qué modelo, con thinking activado o desactivado". La respuesta sale de la documentación del propio modelo, fechada, y luego de tu conjunto de regresión.

### Caso 3: "Grita las reglas importantes"

El énfasis en mayúsculas es una forma habitual de subrayar una regla. La guía de Anthropic dice que los modelos más recientes son "más sensibles al system prompt que los modelos anteriores", y que los prompts escritos para reducir el infradisparo "ahora pueden sobredisparar". Su arreglo: "rebajar cualquier lenguaje agresivo", de modo que donde habrías escrito "CRITICAL: You MUST use this tool when...", se use "Use this tool when...". La guía nombra a Claude Opus 4.5 y Claude Opus 4.6 para esto, y el ejemplo trata del uso de herramientas.

Lee el alcance. La afirmación es sobre dos modelos nombrados y sobre disparar herramientas, no "las mayúsculas nunca funcionan". Un prompt escrito para un modelo más antiguo y trasladado a uno más nuevo es el caso en que merece la pena probar el énfasis heredado, con la versión simple como comparación. La lección 23 enumera la redacción enfática como un costo que cuestionar por la misma razón.

### Caso 4: "Más ejemplos es mejor"

La guía de Anthropic recomienda incluir de 3 a 5 ejemplos y hacerlos relevantes, diversos y estructurados. Dos papers añaden lo que un número no puede decir. Lu et al. muestran que "el orden en que se proporcionan las muestras puede marcar la diferencia entre un rendimiento cercano al estado del arte y uno al azar", que esto se cumple "a través de los tamaños de modelo", y que una buena permutación para un modelo no es transferible a otro. Sclar et al. encuentran que la sensibilidad al formato "persiste incluso al aumentar... el número de ejemplos few-shot".

Así que la cantidad no es la palanca que el eslogan insinúa. Los mismos ejemplos en otro orden, o en un formato distinto, pueden importar tanto como añadir más, y un orden ajustado en un modelo no se traslada al siguiente. Trata el orden y el formato como variables que probar, que es la conclusión de la lección 7 hecha más fuerte.

### Zanjarlo en una conversación

Dos ingenieros citan el mismo paper. No elijas al más seguro de sí mismo, y no partas la diferencia. Pide cuatro cosas: el pasaje, los modelos y la fecha, qué se midió y una ejecución sobre el conjunto de regresión. Si la afirmación y tu caso coinciden, la fuente se aplica. Si no, la fuente no es evidencia sobre tu caso, y la ejecución sí.

## Práctica

1. ▢ Un colega dice "Zheng et al. demostraron que los roles son inútiles, así que elimina la línea del rol de todos los system prompts". ¿Qué respalda el paper y qué harías?

<details markdown="1"><summary>Comprobación</summary>

El paper informa de que añadir un personaje no mejoró el rendimiento en 2,410 preguntas factuales en 4 familias de LLM, en comparación con no usar personaje. No mide el tono ni el alcance, e informa de que el efecto varía según el personaje, no de que sea cero en todos los casos. Así que "inútil para la precisión factual en esos modelos" está respaldado, y "eliminar en todas partes" no. Ejecuta el prompt con y sin el rol en el conjunto de regresión y elimina la línea solo donde los números no muestren nada, ya que quitarla también ahorra tokens.

</details>

2. ▢ Heredas un prompt que dice "CRITICAL: you MUST call the search tool before every answer", ajustado en un modelo más antiguo, y el modelo más nuevo ahora busca para preguntas triviales. ¿Qué acción sigue la fuente?

    - a) Probar una versión simple "Use the search tool when" contra la redacción antigua
    - b) Añadir una segunda regla en mayúsculas que le diga que no busque para trivialidades
    - c) Volver al modelo más antiguo y mantener la redacción igual
    - d) Quitar la instrucción y esperar que el modelo más nuevo infiera la política

<details markdown="1"><summary>Comprobación</summary>

a). La guía de Anthropic describe este sobredisparo para modelos más nuevos nombrados y aconseja rebajar el lenguaje agresivo, así que la redacción simple es la candidata, y el conjunto de regresión decide. b) apila énfasis sobre énfasis. c) tira el modelo más nuevo. d) elimina una política que quizá necesites, y sin probar.

</details>

3. ▢ Un artículo de blog dice "añade 'think step by step' a cada prompt". Usas un modelo con thinking integrado activado. Da las dos primeras comprobaciones que haces antes de tocar el prompt.

<details markdown="1"><summary>Comprobación</summary>

Primero, encuentra el resultado original y mira qué modelos y qué año cubre: el paper de razonamiento zero-shot es de 2022, antes de los modelos con thinking integrado. Segundo, lee la documentación de tu modelo: la guía de Anthropic recomienda instrucciones generales en lugar de pasos prescritos con el thinking activado, y dice que pedir razonamiento escrito puede ser rechazado en algunos modelos nombrados. Luego prueba con y sin la frase en el conjunto de regresión, porque la guía es el relato de un proveedor sobre sus propios modelos.

</details>

4. ▢ Tu prompt tiene cinco ejemplos con la etiqueta rara al final, y la precisión cambia cuando los barajas. ¿Qué fuente lo predijo y qué cambia sobre el consejo de usar de 3 a 5 ejemplos?

<details markdown="1"><summary>Comprobación</summary>

Lu et al. muestran que el orden de los ejemplos por sí solo puede mover los resultados entre casi el estado del arte y casi el azar, y que un buen orden para un modelo no es transferible a otro. El consejo sobre la cantidad sigue siendo un punto de partida, pero no basta: el orden y el formato son parte del comportamiento del prompt, así que registra el orden que pasó y vuelve a probarlo cuando cambie el snapshot del modelo (lección 16).

</details>

5. ▢ Escribe las tres preguntas que harías antes de aceptar "los personajes mejoran la precisión" en una revisión de diseño, y el único resultado que lo zanjaría para tu producto.

<details markdown="1"><summary>Comprobación</summary>

¿En qué modelos y en qué preguntas se midió? ¿La línea base era un prompt sin personaje? ¿La medida era precisión o tono? Lo que lo zanja para tu producto es una comparación pareada en tu conjunto de regresión del prompt con y sin el personaje, juzgando la diferencia frente al ruido entre ejecuciones (lección 19). Una fuente que no coincide con ninguna de tus condiciones es contexto, no evidencia.

</details>

## Prácticas en el mundo real

- [ ] Elige un consejo de prompting que sigas sin conocer su fuente y rastréalo hasta un paper o un documento de un proveedor. Anota los modelos, la fecha y qué se midió.
- [ ] Toma un personaje o una instrucción enfática de un prompt que mantengas y escribe la comparación de dos prompts que lo pondría a prueba, aunque todavía no la ejecutes.
- [ ] Mañana: ejecuta esa comparación en un conjunto de regresión, o esboza cinco casos para uno, y registra el resultado en las notas de cambios del prompt.

## Para profundizar

- [Lista de revisión de prompts](../reference/prompt-review-checklist.md)
- [Paper: "When 'A Helpful Assistant' Is Not Really Helpful: Personas in System Prompts Do Not Improve Performances of Large Language Models", Zheng et al., 2023](https://arxiv.org/abs/2311.10054)
- [Docs: "Prompting best practices", Claude Platform Docs](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/claude-prompting-best-practices)
- [Paper: "Fantastically Ordered Prompts and Where to Find Them", Lu et al., 2021](https://arxiv.org/abs/2104.08786)
- [Recursos](../RESOURCES.md)

---

Este es el final del track, y el hábito para el que fue construido es el de esta lección: un prompt es una afirmación sobre un modelo, así que busca de dónde viene la afirmación, comprueba qué cubría y pruébala en tus propios casos antes de defenderla ante nadie más.

¿No terminas de entenderlo? Vuelve a leer la fuente principal del principio, ya que esta lección la comprime y en la compresión es donde se escapa la comprensión. Consulta el [glosario](../GLOSSARY.md) para cualquier término que te haya resultado resbaladizo.

Si lo poco claro es la propia lección y no el material, eso es un defecto: [abre un issue](https://github.com/TokenCemetery/teach/issues).
