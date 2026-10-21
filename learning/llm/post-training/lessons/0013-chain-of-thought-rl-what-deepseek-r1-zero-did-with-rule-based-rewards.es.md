---
title: "13. RL con chain-of-thought: lo que hizo DeepSeek-R1-Zero con recompensas basadas en reglas"
description: "Sin reward model aprendido, sin un paso de SFT previo, y aun así emergió el razonamiento extendido porque cada vez acertaba más respuestas"
type: lesson
---

# Lección 13. RL con chain-of-thought: lo que hizo DeepSeek-R1-Zero con recompensas basadas en reglas

**Vínculo con la misión:** "Poder decir cómo se produjo el comportamiento de un modelo de razonamiento, no solo cómo darle prompts" es el punto de Cómo se ve el éxito al que sirve esta etapa. Esta lección cubre el entrenamiento de RL puro de DeepSeek-R1-Zero y lo que emergió de él; la lección 14 cubre el arreglo que lo convirtió en un modelo utilizable, y lo que aportó la destilación además de eso.
**Fuente principal:** [Paper: "DeepSeek-R1: Incentivizing Reasoning Capability in LLMs via Reinforcement Learning", DeepSeek-AI, 2025](https://arxiv.org/abs/2501.12948)
**Requisitos previos:** [Lección 12](0012-verifiable-rewards-when-a-checker-replaces-the-reward-model.md)

## Calentamiento

1. ▢ ¿Qué es una recompensa verificable, y por qué no tiene el mismo modo de fallo de reward hacking que tiene un reward model entrenado?

<details markdown="1"><summary>Comprobación</summary>

Una señal de recompensa producida por un verificador determinista en lugar de por un modelo aprendido; como ninguna rareza de un modelo aprendido se interpone entre la salida y su puntuación, no hay un exploit específico de un reward model que una policy pueda aprender, como sí lo hay con un reward model entrenado.

</details>

2. ▢ ¿Por qué una recompensa verificable es una mala opción para entrenar respuestas de atención al cliente más empáticas?

<details markdown="1"><summary>Comprobación</summary>

No hay un verificador determinista para "esta respuesta fue adecuadamente empática"; las recompensas verificables encajan con las tareas en las que la corrección es comprobable en primer lugar, y el tono no es esa clase de propiedad.

</details>

## Qué debes saber

### Entrenar directamente sobre un modelo base, sin un paso de SFT previo

DeepSeek-R1-Zero se entrena con RL a gran escala aplicado directamente a un modelo base preentrenado, sin ningún paso de SFT antes, de modo que se omite por completo la primera etapa del pipeline habitual de tres pasos de la lección 1. La recompensa contra la que entrena es puramente **basada en reglas**, construida con exactamente dos comprobaciones: una **recompensa de precisión (accuracy reward)**, que para problemas de matemáticas comprueba si la respuesta final, dada en un formato especificado como dentro de un recuadro, coincide exactamente con la correcta, o para problemas de código ejecuta un compilador contra casos de prueba predefinidos; y una **recompensa de formato (format reward)**, que comprueba solo que el proceso de pensamiento del modelo esté colocado entre un par de etiquetas que marcan dónde empieza y dónde termina. DeepSeek-AI enuncian directamente que no aplican en absoluto ningún reward model neuronal ni de resultado ni de proceso: ningún reward model entrenado de ningún tipo se interpone entre la salida del modelo y su puntuación.

### El razonamiento extendido emergió, no se programó

Nada en este diseño de recompensa instruye explícitamente al modelo a razonar durante más tiempo, mostrar pasos intermedios o reconsiderar un giro equivocado. DeepSeek-AI informan de que estos comportamientos emergieron de todos modos a lo largo del entrenamiento con RL: como una recompensa de precisión basada en reglas simplemente recompensa acertar la respuesta final, y un razonamiento más largo y más cuidadoso tiende a acertar más respuestas finales, el entrenamiento con RL seleccionó de forma natural por más de él, sin que nadie especificara "razona más tiempo" como objetivo.

### El "momento aha"

DeepSeek-AI describen un caso concreto y llamativo de esto: en un punto intermedio del entrenamiento, DeepSeek-R1-Zero empezó a asignar más tiempo de pensamiento a un problema específicamente reevaluando su propio enfoque inicial a mitad de camino, un comportamiento de autocorrección para el que nadie escribió directamente un término de recompensa. Lo describen como "no solo un 'momento aha' para el modelo sino también para los investigadores que observaban su comportamiento", y lo plantean como una demostración de lo que el entrenamiento con RL hace posible y la instrucción directa no: en lugar de enseñar explícitamente al modelo cómo resolver un problema, las recompensas basadas en reglas aportaron el incentivo correcto, y de optimizar contra él emergió un comportamiento de resolución de problemas genuinamente nuevo.

### Lo que el RL puro por sí solo no arregló

La capacidad de razonamiento de DeepSeek-R1-Zero venía con costos reales que DeepSeek-AI no ocultan: mala legibilidad y mezcla de idiomas (cambiar de idioma dentro de una misma respuesta de una manera que ningún usuario pidió). Nada de una recompensa puramente basada en reglas y solo de corrección da al modelo ningún incentivo para ser legible o para mantenerse en un idioma; esas comprobaciones nunca formaron parte de la puntuación, así que nada seleccionó por ellas. El propio DeepSeek-R1, el modelo construido para arreglar esto, es el tema de la lección 14.

## Práctica

1. ▢ La recompensa de DeepSeek-R1-Zero no tiene ningún término explícito que recompense cadenas de razonamiento más largas, y sin embargo la longitud del razonamiento del modelo creció sustancialmente durante el entrenamiento. ¿Qué dice el relato de esta lección que impulsó realmente ese crecimiento?

<details markdown="1"><summary>Comprobación</summary>

La recompensa de precisión simplemente recompensa acertar la respuesta final, y un razonamiento más largo y más cuidadoso tendía a producir más respuestas finales correctas, así que el entrenamiento con RL seleccionó por él como efecto secundario de optimizar la corrección, no porque la longitud del razonamiento se recompensara directamente.

</details>

2. ▢ ¿Por qué describe DeepSeek-AI la recompensa de precisión como "basada en reglas" y no como un reward model?

    - a) Sigue siendo una red neuronal entrenada, solo que más pequeña
    - b) Es una comprobación determinista (coincidencia exacta con una respuesta conocida, o un compilador que ejecuta casos de prueba fijos), sin ningún modelo aprendido que intervenga en producir la puntuación
    - c) Es basada en reglas solo para los problemas de código, y se usa un reward model neuronal para las matemáticas
    - d) "Basada en reglas" y "reward model" significan lo mismo en este paper

<details markdown="1"><summary>Comprobación</summary>

**b)** es exactamente lo que enuncia DeepSeek-AI: no se aplica en absoluto ningún reward model neuronal de resultado ni de proceso. (a) y (c) suponen ambas un componente aprendido que el paper dice explícitamente que está ausente. (d) colapsa una distinción que el paper se cuida de trazar.

</details>

3. ▢ DeepSeek-R1-Zero logra un buen rendimiento de razonamiento pero sufre mala legibilidad y mezcla de idiomas. Dada cómo se construyó su recompensa, ¿es sorprendente?

<details markdown="1"><summary>Comprobación</summary>

No. La recompensa solo comprobaba la corrección de la respuesta final y la presencia de las etiquetas de pensamiento; nada sobre la legibilidad o sobre mantenerse en un idioma formó nunca parte de la puntuación, así que el entrenamiento con RL no tenía ningún incentivo para seleccionar por ninguna de las dos, por bueno que se volviera el razonamiento del modelo.

</details>

## Prácticas en el mundo real

- [ ] Lee el pasaje del "Aha Moment" del paper de DeepSeek-R1 (enlazado arriba, el texto en torno a la Tabla 3) y escribe, con tus propias palabras, qué comportamiento concreto mostró el modelo que los investigadores no le habían entrenado explícitamente a hacer.
- [ ] Busca un ejemplo documentado (en este paper o en otro lugar) de un modelo entrenado con una recompensa especificada de forma estrecha que produjo un comportamiento emergente no deseado, y compáralo con el "momento aha": ¿fue el comportamiento emergente beneficioso, perjudicial o ambas cosas?
- [ ] Mañana: sin mirar adelante, escribe una predicción de una frase para la lección 14: dado que el RL puro basado en reglas de DeepSeek-R1-Zero produjo un buen razonamiento pero mala legibilidad, ¿qué añadirías al proceso de entrenamiento, y en qué etapa, para arreglar la legibilidad sin perder la capacidad de razonamiento?

## Para profundizar

- [Paper: "DeepSeek-R1: Incentivizing Reasoning Capability in LLMs via Reinforcement Learning", DeepSeek-AI, 2025](https://arxiv.org/abs/2501.12948)
- [Recursos](../RESOURCES.md)

---

¿No termina de quedar claro? Vuelve a leer la fuente primaria de arriba, ya que esta lección la comprime y en la compresión es donde se escapa la comprensión. Consulta el [glosario](../GLOSSARY.md) por si algún término te resultó resbaladizo.

Si lo poco claro es la propia lección y no el material, eso es un defecto: [abre un issue](https://github.com/TokenCemetery/teach/issues).
