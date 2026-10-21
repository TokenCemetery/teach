---
title: "Lo que hereda el estudiante"
description: "Fidelidad, la brecha de imitación, la brecha de capacidad y los rasgos no intencionados, con la configuración y los números de cada fuente"
type: reference
---

# Lo que hereda el estudiante: fidelidad, brecha de imitación, brecha de capacidad y rasgos ocultos

La etapa 6 comprimida para consulta. La [lección 17](../lessons/0017-fidelity-and-generalization.md) cubre fidelidad frente a generalización, la [lección 18](../lessons/0018-the-imitation-gap.md) la brecha de imitación, y la [lección 19](../lessons/0019-capacity-gap-and-hidden-traits.md) la brecha de capacidad y los rasgos ocultos.

## Cuatro maneras en que un estudiante puede diferir de su profesor

| Brecha | Qué difiere | Fuente | Configuración |
|---|---|---|---|
| Fidelidad | Predicciones sobre las mismas entradas, incluso con precisión similar | Stanton et al., 2021 | Clasificación de imágenes, con MNIST, CIFAR-100, ImageNet y sentimiento de IMDB en el apéndice |
| Imitación | El estilo se copia rápido, la capacidad no | Gudibande et al., 2023 | Estudiantes LLaMA y GPT-2 imitando a ChatGPT |
| Capacidad | Un profesor muy grande puede dar un peor estudiante | Mirzadeh et al., 2019, y Cho y Hariharan, 2019 | CNN y ResNet en CIFAR e ImageNet |
| Rasgos ocultos | Un rasgo pasa a través de datos que no lo mencionan | Cloud et al., 2025 | Familia GPT-4.1 y Qwen2.5-7B, más un pequeño caso de MNIST |

Solo dos de las cuatro se probaron en modelos de lenguaje, y ninguna de las evidencias de brecha de capacidad de aquí es de LLM.

## Medir la fidelidad

| Métrica | Definición | Necesita |
|---|---|---|
| Acuerdo top-1 | Fracción de entradas en las que estudiante y profesor eligen la misma etiqueta principal | Las predicciones del profesor |
| KL predictiva | KL(profesor, estudiante) media sobre las entradas | La distribución completa del profesor |
| Control | Un segundo estudiante destilado de la misma manera a partir de un profesor independiente | Una segunda ejecución de destilación |

La precisión no acota el acuerdo de forma estrecha. Con una precisión del profesor del 93% y del estudiante del 91%, el acuerdo está entre el 84% y el 98%.

## Stanton et al. en números

| Observación | Número o dirección |
|---|---|
| LeNet-5 en MNIST con suficientes datos | Más del 99% de acuerdo top-1 en prueba |
| Autodestilación de ResNet-56 en CIFAR-100, el mayor conjunto | Acuerdo en prueba por debajo del 80% |
| Igual, con 50k imágenes GAN añadidas, acuerdo sobre los propios datos de destilación | 95% |
| Igual, con aumentación intensa combinada, acuerdo en entrenamiento en la autodestilación | Alrededor del 60% |
| Autodestilación de ResNet-20, acuerdo en entrenamiento con SGD a 300 épocas y a 5,000 épocas | 78.95% y 83.3% |
| Autodestilación, más datos | Fidelidad sube, precisión en prueba baja |
| Profesor ensemble de 3, más datos | Fidelidad y precisión suben ambas |

Su explicación es la optimización: el estudiante no iguala al profesor ni siquiera sobre los datos con que entrena. Más datos de destilación ayudan a identificar la función del profesor y hacen más difícil la optimización.

## Gudibande et al. en números

| Observación | Número |
|---|---|
| Valoraciones de crowd workers de las salidas de imitación como iguales o mejores que ChatGPT | Alrededor del 70% |
| Natural Questions, LLaMA 7B: base, imitación amplia, imitación local, ChatGPT | 17, 10, 22, 31 |
| Natural Questions, LLaMA 13B: base, imitación amplia, imitación local, ChatGPT | 20, 15, 27, 31 |
| Salidas en tono autoritativo: LLaMA base frente a modelos de imitación | 57% frente a 98% a 99% |

Su afirmación: con los métodos actuales la brecha solo se cierra con una cantidad inmanejable de datos de imitación o con un base model más capaz, y un mejor base model ayudó más que más datos de imitación en sus experimentos. La imitación local de una tarea funcionó mucho mejor que la imitación amplia. Los modelos de imitación también se volvieron menos tóxicos, aprendiendo a abstenerse como el profesor.

## Evidencia de la brecha de capacidad

| Fuente | Hallazgo | Remedio probado |
|---|---|---|
| Mirzadeh et al. | La precisión de un estudiante de 2 capas subió y luego cayó al crecer los profesores de 4 a 10 capas | Asistente del profesor. Mejora sobre la destilación estándar de 0.33 a 0.41 puntos en ResNet, 0.94 puntos en la CNN simple con CIFAR-10 |
| Cho y Hariharan | ResNet18 en ImageNet: desde cero 30.24% de error, 30.57%, 30.79% y 30.95% con profesores ResNet18, 34 y 50 | La destilación detenida antes dio 29.01%, 29.16% y 29.35%. Los profesores detenidos antes ayudaron en CIFAR-10. Encadenar a través de un modelo mediano no ayudó |
| Gu et al. (MiniLLM) | El estudiante GPT-2 de 125M mejoró con profesores de 340M, 760M y 1.5B | No se vio brecha en ese rango, una familia |

Los dos papers de visión discrepan sobre si ayuda un modelo intermedio. Prueba en tu propio par.

## Rasgos ocultos, Cloud et al.

| Elemento | Detalle |
|---|---|
| Configuración | Un profesor con un rasgo genera datos ajenos, los datos se filtran, y un estudiante del mismo base se afina con ellos |
| Preferencia por el búho | Alrededor del 12% antes, más del 60% después, solo con números |
| Desalineación a partir de números | Casi el 10% de respuestas desalineadas, frente al 0% del base y menos del 1% de los controles |
| Desalineación a partir de chain of thought filtrada | De alrededor del 0% al 8%, controles por debajo del 1% |
| Detección | Los clasificadores con prompt y el in-context learning no detectaron el rasgo de forma fiable |
| Condición | Base model compartido. GPT-4.1 nano a Qwen2.5 no transmitió. GPT-4o y GPT-4.1 sí, probablemente por una inicialización compartida |
| Límites abiertos | Tareas artificiales, y se desconoce qué rasgos se transmiten y cuándo |

## Síntoma, causa probable, comprobación

| Síntoma | Causa probable | Comprobación |
|---|---|---|
| El estudiante iguala al profesor en precisión pero las salidas difieren | Baja fidelidad | Acuerdo top-1 y KL predictiva sobre entradas held-out, con un control de profesor independiente |
| Valoraciones de crowd workers o puntuaciones de juez altas, benchmarks específicos planos | Se copió el estilo, no la capacidad | Benchmarks en tareas que los datos apenas cubren, frente al base model |
| Estudiante peor que el estudiante de un profesor más pequeño | Brecha de capacidad | Directo, un modelo intermedio, profesor detenido antes, frente a un baseline desde cero |
| Aparece un comportamiento no deseado aunque los datos están limpios | Rasgo oculto de un base compartido | Evaluar directamente al estudiante en busca del comportamiento, y considerar un base distinto |
| El estudiante rechaza como su profesor | El comportamiento de rechazo se transfiere con el estilo | Comparar las tasas de rechazo con el profesor sobre un conjunto fijo de prompts |

## Lo que nada de esto cubre

- Ninguna fuente leída aquí muestra que un estudiante copie los errores factuales de su profesor.
- La brecha de capacidad y la brecha de fidelidad se midieron en modelos de visión, no en LLM.
- El aprendizaje subliminal se mostró en tareas artificiales, y que una base distinta lo bloqueara fue una observación en esos experimentos, no una garantía.
