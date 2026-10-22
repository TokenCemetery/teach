---
title: "14. Destilar un modelo de razonamiento a un tamaño menor"
description: "Entrenar un modelo de 32B directamente con RL perdió frente a simplemente hacerle fine-tuning con las trazas de razonamiento de un modelo mayor"
type: lesson
---

# Lección 14. Destilar un modelo de razonamiento a un tamaño menor

**Vínculo con la misión:** "Poder decir cómo se produjo el comportamiento de un modelo de razonamiento, no solo cómo darle prompts" es el punto de Cómo se ve el éxito al que sirve esta etapa. La lección 13 cubrió el entrenamiento de RL puro de DeepSeek-R1-Zero y su problema de legibilidad; esta lección cubre el arreglo de DeepSeek-R1 y el sorprendente resultado de destilar ese arreglo hacia modelos más pequeños.
**Fuente principal:** [Paper: "DeepSeek-R1: Incentivizing Reasoning Capability in LLMs via Reinforcement Learning", DeepSeek-AI, 2025](https://arxiv.org/abs/2501.12948)
**Requisitos previos:** [Lección 13](0013-chain-of-thought-rl-what-deepseek-r1-zero-did-with-rule-based-rewards.md)

## Calentamiento

1. ▢ La longitud del razonamiento de DeepSeek-R1-Zero creció sustancialmente durante el entrenamiento sin un término de recompensa explícito para ello. ¿Qué impulsó realmente ese crecimiento?

<details markdown="1"><summary>Comprobación</summary>

La recompensa de precisión recompensaba acertar la respuesta final, y un razonamiento más largo y más cuidadoso tendía a producir más respuestas correctas, así que el entrenamiento con RL seleccionó por él como efecto secundario, no porque la longitud del razonamiento se recompensara directamente.

</details>

2. ▢ DeepSeek-R1-Zero logró un buen razonamiento pero sufrió mala legibilidad y mezcla de idiomas. ¿Por qué no es sorprendente dado cómo se construyó su recompensa?

<details markdown="1"><summary>Comprobación</summary>

La recompensa solo comprobaba la corrección de la respuesta final y la presencia de las etiquetas de pensamiento; la legibilidad y mantenerse en un idioma nunca formaron parte de la puntuación, así que nada en el entrenamiento seleccionó por ninguna de las dos.

</details>

## Qué debes saber

### Arreglar la legibilidad sin perder el razonamiento

DeepSeek-R1 es la respuesta de DeepSeek-AI al problema de legibilidad de DeepSeek-R1-Zero: en lugar de RL puro desde el modelo base, añade **datos de arranque en frío (cold-start data)**, una cantidad modesta de datos curados que se usan antes de la fase de RL centrada en el razonamiento, además de varias fases de entrenamiento construidas en torno a esa fase de RL y no una sola pasada. Esto da al modelo un punto de partida ya más cercano a producir una salida legible y en un solo idioma, antes de aplicar encima el mismo tipo de RL basado en reglas y centrado en el razonamiento que produjo las capacidades de DeepSeek-R1-Zero. El resultado, informan DeepSeek-AI, logra un rendimiento comparable al o1 de OpenAI en tareas de razonamiento y evita los problemas de legibilidad y de mezcla de idiomas que tenía la versión de RL puro.

### Destilación: hacer fine-tuning de modelos más pequeños con las propias trazas de razonamiento del modelo mayor

Aparte de entrenar el propio DeepSeek-R1, DeepSeek-AI producen seis modelos densos más pequeños, de entre 1.5B y 70B parámetros, construidos sobre modelos base existentes de Qwen y Llama. El método es directo: hacer fine-tuning de cada modelo base más pequeño con 800,000 muestras curadas generadas con el propio pipeline de entrenamiento de DeepSeek-R1. Esto es **supervised fine-tuning ordinario** (etapa 2) sobre datos que resultan ser las propias salidas de un modelo de razonamiento mayor, no un algoritmo nuevo. DeepSeek-AI son explícitos en que aplican solo SFT a estos modelos destilados, sin ninguna fase de RL, aunque señalan que una fase de RL podría mejorarlos aún más; su objetivo en este caso era demostrar que la destilación sola ya funciona bien, y dejaron una fase de RL adicional para los modelos más pequeños como trabajo futuro.

### El resultado que hace que esto merezca tomarse en serio

DeepSeek-AI hicieron una comparación directa que responde a una pregunta natural: ¿podría un modelo más pequeño alcanzar la misma capacidad de razonamiento ejecutando directamente sobre él el mismo RL a gran escala, en lugar de destilar de un modelo mayor que ya pasó por ese RL? Entrenaron un modelo base de 32B con más de 10,000 pasos del mismo RL a gran escala que usó DeepSeek-R1-Zero, y produjeron "DeepSeek-R1-Zero-Qwen-32B", y lo compararon con "DeepSeek-R1-Distill-Qwen-32B", el mismo modelo base de 32B al que en cambio se le hizo fine-tuning con las trazas de razonamiento destiladas de DeepSeek-R1. En el benchmark de matemáticas AIME 2024, el modelo entrenado directamente con RL alcanzó un 47.0 % de pass@1; el modelo destilado alcanzó un 72.6 %, una brecha grande que se mantuvo en la misma dirección en todos los benchmarks que informan. La propia conclusión de DeepSeek-AI: destilar un modelo más capaz hacia abajo es a la vez económico y muy eficaz, mientras que entrenar directamente un modelo más pequeño con RL a gran escala exige un cómputo enorme y aun así puede no igualar lo que la destilación consigue gratis a partir de un modelo que ya hizo ese trabajo.

### El límite que tiene la destilación

DeepSeek-AI se cuidan de no exagerar esto: la destilación transfiere de forma barata lo que un modelo más fuerte ya sabe hacer, pero por sí sola no empuja la capacidad más allá de lo que ese modelo más fuerte ya puede hacer. Su propia segunda conclusión lo enuncia directamente: ir más allá de la frontera actual sigue requiriendo modelos base más capaces y aprendizaje por refuerzo a mayor escala aplicado a ellos, no simplemente más destilación de lo que ya existe. La destilación es una manera barata de extender una capacidad existente a modelos más pequeños, no una manera de fabricar capacidad nueva más allá de la que ya tiene el modelo del que se destila.

## Práctica

1. ▢ Un equipo quiere un modelo de razonamiento pequeño y capaz, y considera dos caminos: destilar de un modelo de razonamiento grande existente mediante SFT, o ejecutar RL a gran escala directamente sobre el modelo pequeño desde su checkpoint base. Según la propia comparación de 32B de DeepSeek-AI, ¿qué camino esperarían que alcanzara un rendimiento de razonamiento más fuerte, y aproximadamente en cuánto en AIME 2024?

<details markdown="1"><summary>Comprobación</summary>

La destilación. DeepSeek-R1-Distill-Qwen-32B alcanzó un 72.6 % de pass@1 en AIME 2024, frente al 47.0 % de DeepSeek-R1-Zero-Qwen-32B, entrenado con más de 10,000 pasos de RL a gran escala directamente sobre el mismo modelo base.

</details>

2. ▢ ¿Qué es, concretamente, la "destilación" en el sentido de esta lección, mecánicamente?

    - a) Un nuevo algoritmo de RL aplicado al modelo más pequeño
    - b) Supervised fine-tuning ordinario de un modelo base más pequeño con muestras de salida curadas generadas por un modelo de razonamiento mayor ya entrenado con RL
    - c) Comprimir directamente los pesos del modelo mayor en una arquitectura más pequeña
    - d) Ejecutar juntos los modelos mayor y menor en el momento de la inferencia

<details markdown="1"><summary>Comprobación</summary>

**b)** es exactamente el método que describe DeepSeek-AI: SFT con 800k muestras curadas del propio pipeline de DeepSeek-R1, sin fase de RL. (a), (c) y (d) describen cada una una técnica distinta de la que es el método de esta lección.

</details>

3. ▢ Según las dos conclusiones de DeepSeek-AI, ¿podría la destilación por sí sola empujar la capacidad de razonamiento de un modelo pequeño más allá de lo que puede hacer ya el propio DeepSeek-R1, el modelo del que se destila?

<details markdown="1"><summary>Comprobación</summary>

No. Su segunda conclusión enuncia directamente que avanzar más allá de la frontera actual sigue requiriendo modelos base más capaces y RL a mayor escala, no más destilación; la destilación extiende la capacidad existente de forma barata, no fabrica capacidad nueva más allá de la del propio modelo fuente.

</details>

4. ▢ ¿Por qué añadió DeepSeek-R1 datos de arranque en frío y entrenamiento en varias fases en lugar de simplemente reutilizar la receta exacta de DeepSeek-R1-Zero a mayor escala?

<details markdown="1"><summary>Comprobación</summary>

Porque el razonamiento de DeepSeek-R1-Zero venía con mala legibilidad y mezcla de idiomas que el RL puro basado en reglas no daba al modelo ningún incentivo para arreglar; los datos de arranque en frío y el entrenamiento en varias fases abordan directamente ese problema de legibilidad, en lugar de intentar escalar una receta que nunca seleccionó por ella en primer lugar.

</details>

## Prácticas en el mundo real

- [ ] Busca la Tabla 6 del informe técnico de DeepSeek-R1 (paper enlazado arriba) y anota la brecha entre DeepSeek-R1-Zero-Qwen-32B y DeepSeek-R1-Distill-Qwen-32B en al menos un benchmark distinto de AIME 2024.
- [ ] Busca un modelo de razonamiento destilado publicado (muchos se publican con un nombre que indica de qué se destiló) y comprueba si su model card dice que se entrenó solo con SFT, con una fase de RL añadida o con ambos.
- [ ] Mañana: para un proyecto hipotético que necesite un modelo de razonamiento pequeño y capaz, decide si recurrirías a destilar desde un modelo de razonamiento mayor o a hacer RL directamente sobre el propio modelo pequeño, y escribe una frase que cite la evidencia de esta lección para tu elección.

## Para profundizar

- [Paper: "DeepSeek-R1: Incentivizing Reasoning Capability in LLMs via Reinforcement Learning", DeepSeek-AI, 2025](https://arxiv.org/abs/2501.12948)
- [Destilación: Secuencia y datos sintéticos](../../distillation/reference/sequence-and-synthetic-data.md): la destilación en general, de la que esta lección es el caso del modelo de razonamiento
- [Recursos](../RESOURCES.md)

---

La etapa 7 cubrió cómo el RL produce el comportamiento de razonamiento, y lo barato que es extenderlo a modelos más pequeños una vez que existe. La etapa 8 se vuelve hacia un objetivo distinto para la misma familia de técnicas: no la capacidad de razonamiento, sino el comportamiento de seguridad y de rechazo.

¿No termina de quedar claro? Vuelve a leer la fuente primaria de arriba, ya que esta lección la comprime y en la compresión es donde se escapa la comprensión. Consulta el [glosario](../GLOSSARY.md) por si algún término te resultó resbaladizo.

Si lo poco claro es la propia lección y no el material, eso es un defecto: [abre un issue](https://github.com/TokenCemetery/teach/issues).
