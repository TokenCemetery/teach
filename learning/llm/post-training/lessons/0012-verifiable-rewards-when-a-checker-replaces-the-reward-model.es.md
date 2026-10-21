---
title: "12. Recompensas verificables: cuando un verificador reemplaza al reward model"
description: "Un reward model entrenado es una conjetura de lo que preferiría una persona; un test unitario o una respuesta que coincide no es una conjetura en absoluto"
type: lesson
---

# Lección 12. Recompensas verificables: cuando un verificador reemplaza al reward model

**Vínculo con la misión:** "Explicar la ventaja relativa al grupo en GRPO y por qué una recompensa verificable (un test unitario, una respuesta matemática comprobada) cambia aquello a lo que puede apuntar el entrenamiento con RL" es el quinto punto de Cómo se ve el éxito, y esta lección lo cierra.
**Fuente principal:** [Paper: "DeepSeekMath: Pushing the Limits of Mathematical Reasoning in Open Language Models", Shao et al., 2024](https://arxiv.org/abs/2402.03300)
**Requisitos previos:** [Lección 11](0011-grpo-group-relative-advantage-instead-of-a-value-function.md), [Recompensa verificable](../GLOSSARY.md)

## Calentamiento

1. ▢ Un grupo de 4 salidas muestreadas a la misma pregunta recibe las recompensas `{2, 4, 6, 8}`. ¿Qué salidas obtienen una ventaja relativa al grupo positiva y cuáles una negativa?

<details markdown="1"><summary>Comprobación</summary>

La media es 5; las salidas que puntúan 6 y 8 quedan por encima y obtienen una ventaja positiva, las que puntúan 2 y 4 quedan por debajo y obtienen una ventaja negativa.

</details>

2. ▢ ¿Por qué describe Shao et al. la comparación relativa al grupo como especialmente adecuada para los reward models?

<details markdown="1"><summary>Comprobación</summary>

Los reward models se entrenan normalmente con comparaciones entre salidas a la misma pregunta en primer lugar, así que puntuar varias salidas a una pregunta y compararlas entre sí pide al reward model el mismo tipo de juicio relativo para el que realmente se entrenó.

</details>

## Qué debes saber

### Qué necesita realmente GRPO de una recompensa

Nada de la ventaja relativa al grupo de la lección 11 exige que la puntuación de cada salida muestreada venga específicamente de un reward model entrenado. Lo único que necesita la fórmula de normalización por grupo, `A_i = (r_i - mean(r)) / std(r)`, es un número por salida muestreada, `r_1` a `r_G`, que refleje lo buena que fue cada una. Un reward model entrenado es una manera de producir ese número, la que usa el propio entrenamiento de GRPO de Shao et al. No es la única.

### Qué es una recompensa verificable

Una **recompensa verificable** es una señal de recompensa producida por un verificador determinista en lugar de por un modelo aprendido: si un fragmento de código generado pasa un test unitario fijo, si la respuesta numérica final de un problema de matemáticas coincide exactamente con la correcta conocida, si una demostración o un programa generados satisfacen una comprobación formal. Nada en el cálculo de una recompensa verificable implica conjeturar lo que habría preferido una persona; es un hecho directo y comprobable sobre la salida, calculado de la misma manera cada vez, sin ningún modelo de preferencia entre la salida y su puntuación.

### Por qué esto cambia aquello a lo que puede apuntar el entrenamiento con RL

Un reward model entrenado, por bien entrenado que esté, sigue ajustando un juicio de preferencia: la lección 5 cubrió directamente cómo una policy puede encontrar maneras de puntuar bien contra él sin producir realmente el comportamiento que debía recompensar. Una recompensa verificable no tiene un modo de fallo análogo de esa forma: un test unitario pasa o no pasa, y no hay ninguna rareza propia de un reward model que una policy pueda aprender a explotar, porque no hay ningún modelo aprendido que haga las veces del juicio. Esto abre el entrenamiento con RL a objetivos que antes eran difíciles de alcanzar solo con preferencia humana: se puede empujar a una policy, grupo muestreado tras grupo muestreado, hacia salidas que con más frecuencia son exacta y comprobablemente correctas en tareas como las matemáticas y el código, y no meramente preferidas con más frecuencia por un juez (humano o modelo) que emite un juicio subjetivo.

### Lo que esto no cambia

Una recompensa verificable no es una mejora gratuita sobre un reward model entrenado en todos los aspectos; solo se aplica donde existe realmente una comprobación de corrección. Buena parte del comportamiento que el post-training pretende moldear (la utilidad, el tono, la seguridad, la calidad de la escritura abierta) no tiene ningún verificador determinista que pueda sustituir al juicio de preferencia de una persona o de un modelo; no existe un test unitario para "esta respuesta fue adecuadamente empática". Las recompensas verificables encajan específicamente con las tareas en las que la corrección es comprobable en primer lugar, y por eso las matemáticas y el código son los dominios en torno a los que se construye esta combinación, no un reemplazo general del modelado de recompensa basado en preferencias en todo lo demás.

## Práctica

1. ▢ Un equipo quiere entrenar una policy para resolver problemas de álgebra con enunciado usando GRPO. En lugar de entrenar un reward model con preferencias humanas entre soluciones, ¿qué podrían usar en su lugar, y por qué evitaría el riesgo de reward hacking que describió la lección 5?

<details markdown="1"><summary>Comprobación</summary>

Una recompensa verificable: comprobar si la respuesta numérica final de la policy coincide exactamente con la respuesta correcta conocida. Esto evita el reward hacking en el sentido del reward model porque no hay rarezas de un modelo aprendido que explotar; la comprobación es un hecho directo y determinista sobre la salida y no un juicio entrenado al que una policy pudiera aprender a hacer trampa.

</details>

2. ▢ ¿Por qué sería una recompensa verificable una mala opción para entrenar una policy que escriba respuestas de atención al cliente más empáticas?

    - a) Las recompensas verificables solo pueden calcularse para salidas numéricas
    - b) No hay un verificador determinista para "esta respuesta fue adecuadamente empática"; la corrección de ese tipo no es el tipo de propiedad que un verificador pueda comprobar
    - c) Las recompensas verificables requieren siempre un reward model aparte que las interprete
    - d) GRPO no puede usarse en absoluto con recompensas verificables

<details markdown="1"><summary>Comprobación</summary>

**b)** es la limitación real: las recompensas verificables encajan con las tareas en las que la corrección es comprobable en primer lugar, y el tono empático no tiene esa comprobación determinista. (a) es demasiado estrecha; la corrección del código es un ejemplo no numérico que sigue verificándose. (c) contradice todo el sentido de una recompensa verificable, que no necesita ningún reward model. (d) es falsa; la maquinaria de normalización por grupo de GRPO funciona con cualquier puntuación por salida, verificable o producida por un modelo.

</details>

3. ▢ ¿Cambia algo usar una recompensa verificable en cómo se calcula la ventaja relativa al grupo de la lección 11?

<details markdown="1"><summary>Comprobación</summary>

No. La misma normalización, restar la media del grupo y dividir por la desviación estándar del grupo, se aplica tanto si la puntuación subyacente por salida, `r_i`, vino de un reward model entrenado como de un verificador determinista. Lo único que cambia es de dónde viene esa puntuación, no lo que GRPO hace con ella.

</details>

## Prácticas en el mundo real

- [ ] Busca una configuración publicada de entrenamiento con RL para razonamiento (un paper, un informe técnico o un script de entrenamiento abierto) e identifica exactamente qué comprueba su recompensa verificable: una respuesta de coincidencia exacta, una suite de tests unitarios, un verificador formal de demostraciones u otra cosa.
- [ ] Elige una tarea que te parezca plausible para recompensas verificables (una tarea de código, un conjunto de problemas de matemáticas) y una que te parezca implausible (una tarea abierta de escritura o conversacional), y escribe una frase por cada una que explique qué podría o no podría comprobar un verificador determinista.
- [ ] Mañana: sin mirar adelante, escribe una predicción de una frase para la etapa 7: si las recompensas verificables permiten que el entrenamiento con RL empuje a una policy hacia ser exactamente correcta con más frecuencia, ¿qué tipo de comportamiento nuevo del modelo esperarías que emergiera de entrenar intensamente con problemas de matemáticas y código de esta manera, más allá de simplemente acertar más respuestas?

## Para profundizar

- [Paper: "DeepSeekMath: Pushing the Limits of Mathematical Reasoning in Open Language Models", Shao et al., 2024](https://arxiv.org/abs/2402.03300)
- [Recursos](../RESOURCES.md)

---

La etapa 6 cubrió el mecanismo (la ventaja relativa al grupo) y la recompensa que mejor se empareja con él (las comprobaciones verificables). La etapa 7 cubre lo que ocurre cuando esta combinación se escala como la manera principal de entrenar un modelo: los modelos de razonamiento, y lo que produce realmente entrenar con recompensas verificables a escala.

¿No termina de quedar claro? Vuelve a leer la fuente primaria de arriba, ya que esta lección la comprime y en la compresión es donde se escapa la comprensión. Consulta el [glosario](../GLOSSARY.md) por si algún término te resultó resbaladizo.

Si lo poco claro es la propia lección y no el material, eso es un defecto: [abre un issue](https://github.com/TokenCemetery/teach/issues).
