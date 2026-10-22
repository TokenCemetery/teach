---
title: "3. Enmascarado de la pérdida en tokens que no son del asistente"
description: "Pon a cero la pérdida sobre el prompt, o gastarás señal de gradiente en enseñar al modelo a predecir texto que no generó"
type: lesson
---

# Lección 3. Enmascarado de la pérdida en tokens que no son del asistente

**Vínculo con la misión:** "Escribir un bucle de entrenamiento de SFT que enmascare la pérdida en los tokens que no son del asistente, y explicar qué se rompe en un modelo de chat entrenado sin esa máscara" es el primer punto de Cómo se ve el éxito, y esta lección es donde se responde directamente.
**Fuente principal:** [Paper: "Llama 2: Open Foundation and Fine-Tuned Chat Models", Touvron et al., 2023](https://arxiv.org/abs/2307.09288)
**Requisitos previos:** [Lección 2](0002-instruction-data-and-the-chat-template.md), [Enmascarado de la pérdida](../GLOSSARY.md)

## Calentamiento

1. ▢ ¿Qué es un chat template, y por qué importa que se use el mismo tanto en el entrenamiento como en el serving?

<details markdown="1"><summary>Comprobación</summary>

Una manera fija y consistente de marcar las fronteras entre roles (turnos de sistema, de usuario y de asistente) con tokens especiales, para que el modelo pueda aprender una estructura que volverá a ver de forma fiable. Un desajuste entre los templates del entrenamiento y del serving le presenta al modelo una estructura que nunca vio emparejada con el comportamiento que aprendió, y degrada o desestabiliza su comportamiento.

</details>

2. ▢ Según Touvron et al., ¿qué token especial usan para separar un prompt de su respuesta en los datos de entrenamiento de SFT?

<details markdown="1"><summary>Comprobación</summary>

Un token especial dedicado, insertado precisamente para marcar la frontera entre el segmento de prompt y el segmento de respuesta.

</details>

## Qué debes saber

### La versión simple, sin máscara, de esta pérdida sería incorrecta

Una pérdida ordinaria de modelado de lenguaje entrena al modelo para predecir el token siguiente en cada posición de una secuencia, comparándolo con lo que la secuencia contiene realmente ahí. Aplicada ingenuamente a un ejemplo concatenado de prompt y respuesta, sin ningún ajuste, entrenaría al modelo para predecir también los propios tokens del prompt, y no solo los de la respuesta, ya que el prompt forma parte de la secuencia exactamente igual que la respuesta.

### Qué hacen en realidad Touvron et al.

Touvron et al. enuncian directamente su enfoque: "usamos un objetivo autorregresivo y ponemos a cero la pérdida en los tokens del prompt del usuario, de modo que hacemos backpropagation solo sobre los tokens de la respuesta". Esto es el **enmascarado de la pérdida (loss masking)**: a cada token que pertenece al prompt (o, en un ejemplo de varios turnos, a cualquier turno de usuario o de sistema) se le pone a cero su contribución a la pérdida, de modo que solo los tokens que el modelo debe generar realmente, la respuesta del asistente, producen un gradiente. Mecánicamente, esto se implementa normalmente dando a cada posición enmascarada un valor de etiqueta que a la función de pérdida se le indica que ignore (una convención habitual lo fija en `-100` para una pérdida de entropía cruzada estándar), en lugar del token que aparece realmente ahí.

### Qué se rompe sin él

Omitir este enmascarado no desperdicia simplemente un poco de cómputo; cambia aquello para lo que se está entrenando realmente al modelo. De ahí se siguen directamente dos problemas concretos:

- **El modelo aprende a predecir texto que no generó y que nunca necesitará reproducir.** Nada de entrenar a un modelo para que le devuelva a un usuario su propio prompt sirve al objetivo de SFT, que es moldear lo que el modelo produce como respuesta, no lo que puede repetir de la pregunta.
- **Los prompts suelen ser mucho más largos que las respuestas que los siguen.** Una pérdida sin enmascarar queda dominada por el número de tokens de prompt que haya, y diluye la señal de gradiente sobre los tokens de la respuesta, la única parte de la secuencia que SFT intenta realmente moldear, con una gran cantidad de pérdida gastada en una tarea (predecir el prompt) que nunca fue el objetivo.

### El resultado: el enmascarado concentra el objetivo en lo que se enseña

Enmascarar todos los tokens que no son del asistente hace lo contrario de ambos problemas: cada unidad de señal de gradiente de un paso de SFT proviene de tokens que el modelo debe aprender realmente a producir, y ninguna se gasta en predecir texto que simplemente se le dio. Esto es lo que hace que SFT enseñe la habilidad concreta que debe enseñar, imitar la respuesta deseada, y no una mezcla de esa habilidad con otra sin relación (predecir texto arbitrario del usuario) que casualmente comparte la misma secuencia de entrenamiento.

## Práctica

1. ▢ Un ejemplo de entrenamiento concatena un prompt de 200 tokens y una respuesta de 20 tokens, sin enmascarado de la pérdida. ¿Aproximadamente qué fracción de la pérdida total de este ejemplo proviene de tokens que no son el objetivo real de SFT?

<details markdown="1"><summary>Comprobación</summary>

Aproximadamente 200 de 220 tokens, cerca del 91 %, serían tokens de prompt que aportan una pérdida que no tiene nada que ver con la respuesta que SFT intenta enseñar a producir al modelo. Solo alrededor del 9 % de la pérdida sin enmascarar vendría de la propia respuesta.

</details>

2. ▢ ¿Cuál de estas describe mejor lo que hace realmente el enmascarado de la pérdida, mecánicamente?

    - a) Elimina por completo los tokens del prompt de la secuencia de entrada
    - b) Da a la posición de cada token enmascarado una etiqueta que la función de pérdida ignora, de modo que solo las posiciones sin enmascarar (del asistente) aportan un gradiente
    - c) Reduce el learning rate específicamente al procesar los tokens del prompt
    - d) Entrena un modelo aparte solo para los tokens del prompt

<details markdown="1"><summary>Comprobación</summary>

**b)** es el mecanismo real: los tokens del prompt siguen presentes como entrada, de modo que el modelo puede condicionar su respuesta en ellos, pero sus posiciones quedan excluidas del propio cálculo de la pérdida. (a) eliminaría información en la que el modelo necesita condicionar su respuesta. (c) y (d) no describen ninguna técnica que describan esta lección o su fuente.

</details>

3. ▢ Se compara un modelo entrenado sin enmascarado de la pérdida en los tokens que no son del asistente con uno entrenado con él, sobre exactamente los mismos datos de SFT. Nombra una manera concreta en que esperarías que el entrenamiento de SFT del modelo sin enmascarar hubiera ido distinto.

<details markdown="1"><summary>Comprobación</summary>

Cualquier versión razonable de esto: la señal de gradiente se diluyó, o se gastó, en aprender a predecir tokens del prompt en lugar de concentrarse por completo en los tokens de la respuesta, de modo que, con el mismo número de pasos de entrenamiento, una parte menor de lo que aprendió el modelo moldeaba realmente su comportamiento al generar respuestas, lo único que SFT debe enseñar.

</details>

## Prácticas en el mundo real

- [ ] Busca dónde implementa el enmascarado de la pérdida para datos de SFT de estilo chat un framework de entrenamiento al que tengas acceso (un `ignore_index`, un campo `labels` con posiciones enmascaradas o algo parecido), y confirma qué convención usa para marcar una posición enmascarada.
- [ ] Toma una conversación de ejemplo corta (un mensaje de sistema, un turno de usuario, un turno de asistente) y marca, token a token o segmento a segmento, qué partes se enmascararían y cuáles aportarían a la pérdida, según la regla de esta lección.
- [ ] Mañana: para una conversación de varios turnos con dos turnos de usuario y dos de asistente, escribe qué turnos se enmascaran y cuáles no, y contrasta tu respuesta con la regla de esta lección de que se enmascara todo turno que no es del asistente, no solo el primer prompt.

## Para profundizar

- [Paper: "Llama 2: Open Foundation and Fine-Tuned Chat Models", Touvron et al., 2023](https://arxiv.org/abs/2307.09288)
- [Documentation: "TRL - Transformer Reinforcement Learning", Hugging Face](https://huggingface.co/docs/trl/index)
- [Recursos](../RESOURCES.md)

---

La etapa 2 cubrió imitar directamente una respuesta demostrada. La etapa 3 se vuelve hacia otro tipo de señal: no cómo debe ser la respuesta, sino cuál de dos respuestas prefirió una persona.

¿No termina de quedar claro? Vuelve a leer la fuente primaria de arriba, ya que esta lección la comprime y en la compresión es donde se escapa la comprensión. Consulta el [glosario](../GLOSSARY.md) por si algún término te resultó resbaladizo.

Si lo poco claro es la propia lección y no el material, eso es un defecto: [abre un issue](https://github.com/TokenCemetery/teach/issues).
