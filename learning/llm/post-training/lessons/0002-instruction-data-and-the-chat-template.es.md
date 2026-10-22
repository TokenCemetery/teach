---
title: "2. Datos de instrucciones y el chat template"
description: "Un token especial marca dónde termina un prompt y empieza una respuesta, y esa frontera tiene que coincidir en el entrenamiento y en el serving"
type: lesson
---

# Lección 2. Datos de instrucciones y el chat template

**Vínculo con la misión:** "Escribir un bucle de entrenamiento de SFT que enmascare la pérdida en los tokens que no son del asistente, y explicar qué se rompe en un modelo de chat entrenado sin esa máscara" es el primer punto de Cómo se ve el éxito. Esta lección cubre cómo son los datos de SFT y cómo se marcan sus segmentos; la lección 3 cubre el enmascarado en sí.
**Fuente principal:** [Paper: "Llama 2: Open Foundation and Fine-Tuned Chat Models", Touvron et al., 2023](https://arxiv.org/abs/2307.09288)
**Requisitos previos:** [Lección 1](0001-what-post-training-buys.md)

## Calentamiento

1. ▢ ¿Qué es un impuesto de alineación, y qué encontraron Ouyang et al. que podía compensarlo en parte?

<details markdown="1"><summary>Comprobación</summary>

Una caída medida del rendimiento en ciertos benchmarks públicos de NLP que acompañó a las ganancias de alineación del post-training. Mezclar las actualizaciones de PPO con actualizaciones que aumentan la verosimilitud de los datos de preentrenamiento originales (PPO-ptx) recuperó buena parte de ese rendimiento perdido sin renunciar a las ganancias de preferencia.

</details>

## Qué debes saber

### Cómo son realmente los datos de SFT

Los datos de **supervised fine-tuning (SFT)** son un conjunto de pares de prompt y respuesta, exactamente la forma que describió el paso 1 de la lección 1. Touvron et al. dan ejemplos reales de la propia anotación de SFT de Llama 2: un prompt que pide un poema sobre los diez primeros elementos de la tabla periódica, emparejado con un poema escrito por un anotador que lo responde; un prompt que pide un "roast" deliberadamente cruel, emparejado con un rechazo escrito por un anotador que explica por qué. Ambos son simplemente un prompt y la respuesta exacta que un anotador quiere que el modelo aprenda a producir para él.

### Marcar dónde termina un segmento y empieza el siguiente

Entrenar con estos datos significa concatenar muchos pares de prompt y respuesta en el corpus de entrenamiento, y el modelo necesita alguna manera de saber dónde termina un prompt y empieza su respuesta, ya que nada en el texto plano marca por sí solo esa frontera. Touvron et al. describen exactamente esto: "se utiliza un token especial para separar los segmentos de prompt y de respuesta". Esta es la semilla de lo que se llama un **chat template**: una manera fija y consistente de marcar las fronteras entre roles (un segmento de prompt, un segmento de respuesta y, en una conversación de varios turnos, un mensaje de sistema y cada turno sucesivo) con tokens especiales, de modo que la misma estructura aparezca siempre en el entrenamiento y pueda reproducirse exactamente en el serving.

### Por qué la frontera tiene que coincidir en el entrenamiento y en el serving

Un chat template no es solo una comodidad de formato; es parte de aquello con lo que se entrenó realmente el modelo. El modelo aprendió a asociar los tokens especiales que marcan "aquí empieza una respuesta" con producir realmente el tipo de respuesta que seguía a esos tokens durante el entrenamiento. Servir el modelo con una plantilla distinta, con otros tokens especiales, con otro orden de roles o sin la convención del mensaje de sistema, le presenta una estructura que nunca vio emparejada con el comportamiento que aprendió, y su comportamiento se degrada o se vuelve impredecible. Reproducir en el serving el template exacto del entrenamiento no es una limpieza opcional; es parte de usar correctamente el modelo.

### Varios turnos es la misma idea, repetida

Una conversación de varios turnos extiende esta misma idea de marcar segmentos a más de un intercambio: un mensaje de sistema (si lo hay), y luego turnos alternos de usuario y de asistente, cada uno marcado con el mismo tipo de tokens especiales que separan cualquier prompt individual de su respuesta. No se inventa nada nuevo para el caso de varios turnos; es el mismo principio de marcar fronteras, aplicado una vez por turno en lugar de una vez por ejemplo.

## Práctica

1. ▢ ¿Por qué un modelo no puede aprender dónde termina un prompt y empieza su respuesta solo a partir de texto plano concatenado, sin algún tipo de marcador?

<details markdown="1"><summary>Comprobación</summary>

Porque el texto plano no lleva ninguna señal inherente que distinga "esto es lo que se preguntó" de "esta es la respuesta que debo aprender a producir"; sin un marcador, la frontera entre ambos no está representada en ninguna parte de los propios datos de entrenamiento.

</details>

2. ▢ Un equipo hace fine-tuning de un modelo con un chat template, pero lo sirve en producción con otro distinto (con otros tokens especiales que marcan las fronteras entre roles). ¿Cuál es la consecuencia más probable?

    - a) Ningún efecto; el modelo ignora por completo el formato
    - b) El comportamiento del modelo se degrada o se vuelve impredecible, ya que se le presenta una estructura que nunca vio emparejada con el comportamiento que aprendió durante el entrenamiento
    - c) El modelo detecta y se adapta automáticamente al nuevo template
    - d) Solo se ve afectado el mensaje de sistema; los turnos de usuario y de asistente siguen funcionando con normalidad

<details markdown="1"><summary>Comprobación</summary>

**b)** es la consecuencia real: el chat template es parte de aquello con lo que se entrenó el modelo, no un envoltorio cosmético, así que un desajuste le presenta una estructura con la que no se entrenó. (a), (c) y (d) suponen una robustez ante el desajuste de template que el entrenamiento no da motivo para esperar.

</details>

3. ▢ ¿Cómo se relaciona el chat template de una conversación de varios turnos con la plantilla simple de prompt y respuesta que describen Touvron et al. para SFT?

<details markdown="1"><summary>Comprobación</summary>

Es la misma idea de marcar segmentos, aplicada repetidamente: un mensaje de sistema si existe, y luego cada turno de usuario y de asistente en secuencia, cada uno marcado con el mismo tipo de tokens especiales que separan un solo prompt de su respuesta, en lugar de requerir un mecanismo fundamentalmente distinto.

</details>

## Prácticas en el mundo real

- [ ] Busca el chat template de un modelo abierto al que tengas acceso (muchos se publican como un archivo de template o se documentan directamente), e identifica los tokens especiales que usa para marcar un mensaje de sistema, un turno de usuario y un turno de asistente.
- [ ] Lee los dos ejemplos de anotación de SFT de Touvron et al. (enlazados arriba, Tabla 5) y escribe, con tus propias palabras, qué distingue una buena respuesta de SFT de una que simplemente suena plausible, a partir del ejemplo del rechazo del roast.
- [ ] Mañana: sin mirar adelante, escribe una predicción de una frase para la lección 3: si un chat template concatena un prompt y una respuesta en una sola secuencia sin separación, y el entrenamiento usa una pérdida ordinaria de predicción del siguiente token sobre toda la secuencia, ¿qué empezaría a aprender el modelo a hacer con los propios tokens del prompt que no debería?

## Para profundizar

- [Paper: "Llama 2: Open Foundation and Fine-Tuned Chat Models", Touvron et al., 2023](https://arxiv.org/abs/2307.09288)
- [Recursos](../RESOURCES.md)

---

¿No termina de quedar claro? Vuelve a leer la fuente primaria de arriba, ya que esta lección la comprime y en la compresión es donde se escapa la comprensión. Consulta el [glosario](../GLOSSARY.md) por si algún término te resultó resbaladizo.

Si lo poco claro es la propia lección y no el material, eso es un defecto: [abre un issue](https://github.com/TokenCemetery/teach/issues).
