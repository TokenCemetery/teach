---
title: "Destilación"
description: "Destila un modelo grande en uno más pequeño y defiéndelo: soft targets, pérdidas de logits y a nivel de secuencia, datos sintéticos, entrenamiento on-policy y qué perdió el estudiante"
type: topic
---

# Aprendizaje: destilación

Entrena un modelo más pequeño para que haga lo que hace uno mayor aprendiendo de las salidas del modelo mayor, sabiendo qué transfiere cada forma de destilación y qué no puede transferir. Termina siendo capaz de elegir entre destilar, cuantizar y entrenar directamente un modelo pequeño para una tarea y un presupuesto dados, medir con honestidad qué perdió el estudiante y revisar la afirmación de otra persona de que un modelo destilado "iguala al profesor".

**Última lección:** [27. Cuando la respuesta habitual es incorrecta](lessons/0027-when-the-usual-answer-is-wrong.md)

## Cómo se ve el éxito

- Explicar por qué los soft targets de un profesor llevan más señal de entrenamiento que los hard labels, y fijar la temperatura y los pesos de la pérdida de una ejecución de destilación.
- Escribir la pérdida de destilación a nivel de token para un LLM, elegir entre KL directa e inversa y decir cuándo un desajuste de tokenizer descarta la destilación de logits.
- Destilar a nivel de secuencia o a partir de los datos generados por un profesor, y decir qué transfiere cada uno que el otro no.
- Construir un conjunto de destilación sintético filtrado por calidad, y comprobar si la licencia y los términos del profesor permiten entrenar con sus salidas.
- Explicar el exposure bias, y decir cuándo la destilación on-policy vale su costo frente a entrenar con salidas fijas del profesor.
- Predecir qué heredará y qué no heredará un estudiante de su profesor, incluida la capacidad que no puede absorber y los rasgos que nadie pretendía transmitir.
- Elegir un tamaño de estudiante y un volumen de datos contando el propio costo del profesor en el presupuesto.
- Medir qué perdió un estudiante frente a su profesor y frente a un modelo del mismo tamaño entrenado sin uno.
- Elegir entre destilar, cuantizar y hacer fine-tuning directamente de un modelo pequeño, revisar la afirmación de destilación de otra persona nombrando lo que oculta, reemplazar con un estudiante un modelo del que otros dependen, y decir cuándo la respuesta habitual es la equivocada.

## Restricciones

- Se asume soltura para leer Python y PyTorch, y saber qué son la pérdida de entropía cruzada, un softmax y un bucle de entrenamiento. No se requiere conocimiento previo de destilación, ni de aprendizaje por refuerzo más allá de la idea de muestrear de un modelo.
- Se basa en papers e informes de modelos. Donde una cifra es el resultado de un paper en su propia configuración, la lección lo dice, porque los resultados de la destilación dependen mucho del profesor, del estudiante y de los datos.
- La práctica corre en un portátil en las etapas 1 y 2, con un clasificador lo bastante pequeño para una CPU. Las prácticas posteriores destilan entre dos modelos abiertos pequeños, para lo que basta un notebook con GPU gratuita.

## Fuera de alcance

- Destilar un modelo de razonamiento haciendo fine-tuning con sus largas cadenas de pensamiento: consulta [`llm/post-training`](../../llm/post-training/), lección 0014. Esa lección sigue siendo el caso del modelo de razonamiento; este track enseña la destilación en general y enlaza a ella en lugar de repetirla.
- Ejecutar supervised fine-tuning mediante adapters LoRA o QLoRA: consulta [`llm/finetuning`](../../llm/finetuning/). Este track es dueño del objetivo y de los datos de la destilación; cómo se aplica el entrenamiento a menos parámetros se queda allí.
- Ejecutar una corrida de preentrenamiento: consulta [`llm/pretraining`](../../llm/pretraining/). La destilación como señal de preentrenamiento se enseña aquí como una pérdida y una elección de datos (lección 0007), no como una corrida de preentrenamiento.
- Construir una eval: consulta [`llm/evals`](../../llm/evals/) y su [Go/No-Go](../../llm/evals/reference/go-no-go.md). Este track usa una eval para comparar un estudiante con su profesor y no vuelve a enseñar cómo construir una.
- Reducir un modelo bajando su precisión: consulta [`llm/quantization`](../../llm/quantization/). Este track es la otra manera de reducir un modelo, con menos parámetros, y la comparación entre ambas forma parte de la etapa 9.
- La poda (pruning) como método por derecho propio. La lección 0007 la muestra emparejada con la destilación en Minitron, y enseña solo la mitad de la destilación.

## El arco

Nueve etapas, desde por qué un modelo pequeño puede aprender de uno grande hasta el criterio para revisar la destilación de otra persona. Una etapa abarca varias lecciones y los límites son difusos; lo que da una etapa por terminada es la capacidad, no el número de lecciones.

| Etapa | Lecciones | Cubre | Terminada cuando |
|---|---|---|---|
| 1. Por qué funciona la destilación | 0001 a 0003 | Profesor y estudiante, soft targets y lo que llevan, temperatura y la pérdida combinada | Puedes decir por qué los soft targets enseñan más que los hard labels y fijar la temperatura |
| 2. Destilación de logits para LLM | 0004 a 0007 | Destilación a nivel de token, KL directa e inversa, la restricción del tokenizer compartido, la destilación como señal de preentrenamiento | Puedes escribir la pérdida a nivel de token y decir cuándo no se puede usar |
| 3. Destilación a nivel de secuencia | 0008 a 0009 | Entrenar con las salidas decodificadas del profesor, y elegir entre nivel de token y de secuencia | Puedes decir qué transfiere cada nivel y elegir uno según lo que expone el profesor |
| 4. Destilación con datos sintéticos | 0010 a 0013 | Datos de instrucciones generados, rationales y trazas de explicación, filtrado, licencias y términos | Puedes construir un conjunto de destilación filtrado y comprobar que su uso está permitido |
| 5. Destilación on-policy | 0014 a 0016 | Exposure bias, GKD y MiniLLM, qué cuesta y qué aporta el entrenamiento on-policy | Puedes decir cuándo la destilación on-policy se gana su costo |
| 6. Qué hereda el estudiante | 0017 a 0019 | Fidelidad frente a generalización, la brecha de imitación, la brecha de capacidad, rasgos transmitidos sin querer | Puedes predecir qué recogerá y qué no recogerá un estudiante de su profesor |
| 7. Dimensionamiento | 0020 a 0021 | Leyes de escalado de la destilación, volumen de datos, el costo del profesor en el presupuesto | Puedes elegir un tamaño de estudiante y un volumen de datos y defender el cómputo |
| 8. Medir lo que se perdió | 0022 a 0023 | Acuerdo con el profesor frente a calidad en la tarea, baselines, tareas held-out, contaminación | Puedes medir qué perdió un estudiante y defender la cifra |
| 9. Criterio | 0024 a 0027 | Destilar, cuantizar o hacer fine-tuning de un modelo pequeño, revisar una afirmación, reemplazar un modelo del que otros dependen, cuándo la respuesta habitual es incorrecta | Se confía en ti para decidir sobre una destilación y explicárselo a otra persona |

## Lecciones

Recórrelas en orden.

| # | Lección | Enseña |
|---|---|---|
| [0001](lessons/0001-what-distillation-buys.md) | Qué aporta la destilación | Un estudiante pequeño entrenado para imitar a un profesor grande, y por qué la imitación puede superar a entrenar al estudiante solo con las etiquetas |
| [0002](lessons/0002-soft-targets.md) | Soft targets | Qué llevan las probabilidades que un profesor da a las respuestas incorrectas, y por qué son una señal de entrenamiento más rica que un hard label |
| [0003](lessons/0003-temperature.md) | Temperatura | Suavizar ambas distribuciones con una temperatura, la corrección de T al cuadrado y mezclar la pérdida de hard labels |
| [0004](lessons/0004-token-level-distillation.md) | Destilación a nivel de token | Igualar la distribución del siguiente token del profesor en cada posición de una secuencia |
| [0005](lessons/0005-forward-and-reverse-kl.md) | KL directa e inversa | Por qué la KL directa reparte al estudiante sobre cada modo del profesor y la KL inversa lo hace comprometerse con uno |
| [0006](lessons/0006-the-tokenizer-constraint.md) | La restricción del tokenizer | Por qué la destilación de logits necesita un vocabulario compartido, y a qué renuncian los métodos entre tokenizers |
| [0007](lessons/0007-distilling-during-pretraining.md) | Destilar durante el preentrenamiento | Cómo Gemma 2 y Minitron usaron la distribución de un profesor como señal de entrenamiento a escala, y qué cuesta almacenar logits |
| [0008](lessons/0008-sequence-level-distillation.md) | Destilación a nivel de secuencia | Entrenar al estudiante con las salidas decodificadas del profesor en lugar de con sus distribuciones |
| [0009](lessons/0009-token-or-sequence.md) | Token o secuencia | Qué transfiere cada nivel, cómo combinarlos y cómo elegir según si el profesor expone logits o solo texto |
| [0010](lessons/0010-distilling-from-generated-data.md) | Destilar a partir de datos generados | Construir un conjunto de instrucciones a partir de las generaciones de un profesor, como hicieron Self-Instruct y Alpaca |
| [0011](lessons/0011-rationales-and-explanation-traces.md) | Rationales y trazas de explicación | Entrenar con el razonamiento del profesor además de con sus respuestas, como hicieron Distilling Step-by-Step y Orca |
| [0012](lessons/0012-filtering-synthetic-data.md) | Filtrar datos sintéticos | Comprobar, filtrar y deduplicar los datos generados antes de entrenar con ellos, porque el volumen no arregla los malos ejemplos |
| [0013](lessons/0013-licensing-and-terms.md) | Licencias y términos | Qué te permiten hacer con sus salidas los términos de un proveedor y la licencia de un modelo abierto |
| [0014](lessons/0014-exposure-bias.md) | Exposure bias | Por qué un estudiante entrenado con prefijos del profesor se topa en inferencia con sus propios errores sin haber entrenado con ellos |
| [0015](lessons/0015-gkd-and-minillm.md) | GKD y MiniLLM | Muestrear del estudiante y puntuar con el profesor, y las elecciones de divergencia y de mezcla que lo acompañan |
| [0016](lessons/0016-on-policy-distillation-in-practice.md) | Destilación on-policy en la práctica | Qué cuesta por paso la destilación on-policy, qué aporta y cómo la usó Qwen3 para sus modelos pequeños |
| [0017](lessons/0017-fidelity-and-generalization.md) | Fidelidad y generalización | Por qué un estudiante que generaliza bien puede seguir discrepando de su profesor, y cuál de las dos necesitas |
| [0018](lessons/0018-the-imitation-gap.md) | La brecha de imitación | Por qué imitar a un modelo más fuerte copia su estilo mucho más rápido que su capacidad |
| [0019](lessons/0019-capacity-gap-and-hidden-traits.md) | Brecha de capacidad y rasgos ocultos | Por qué un profesor mayor no siempre es mejor, y qué puede pasar a un estudiante sin que nadie lo pretenda |
| [0020](lessons/0020-choosing-student-size.md) | Elegir el tamaño del estudiante | Qué dicen las leyes de escalado de la destilación sobre cuándo destilar supera a entrenar directamente al estudiante |
| [0021](lessons/0021-data-volume-and-teacher-cost.md) | Volumen de datos y costo del profesor | Contar la inferencia del profesor en el presupuesto, y decidir cuántos datos de destilación bastan |
| [0022](lessons/0022-student-against-teacher.md) | Estudiante frente a profesor | Medir el acuerdo con el profesor por separado de la calidad en la tarea, una capacidad a la vez |
| [0023](lessons/0023-an-honest-distillation-eval.md) | Una eval honesta de destilación | Los baselines, las tareas held-out y las comprobaciones de contaminación que hacen defendible una cifra de "iguala al profesor" |
| [0024](lessons/0024-distill-quantize-or-fine-tune.md) | Destilar, cuantizar o hacer fine-tuning | Elegir entre menos parámetros, menos bits y entrenar directamente un modelo pequeño, según la tarea y el presupuesto |
| [0025](lessons/0025-reviewing-a-distillation-claim.md) | Revisar una afirmación de destilación | Revisar "nuestro modelo pequeño iguala al grande" nombrando lo que la medición ocultó |
| [0026](lessons/0026-replacing-a-model-others-depend-on.md) | Reemplazar un modelo del que otros dependen | Desplegar un estudiante en lugar de su profesor sin romper a quienes dependen de su comportamiento |
| [0027](lessons/0027-when-the-usual-answer-is-wrong.md) | Cuando la respuesta habitual es incorrecta | Reconocer cuándo la destilación es la decisión equivocada, y resolver una afirmación en disputa desde la fuente primaria |

## Referencia

- [Glosario](GLOSSARY.md): términos canónicos de este tema
- [Recursos](RESOURCES.md): fuentes de confianza, cada una anotada con lo que cubre
- [Pérdidas de destilación](reference/distillation-losses.md): soft targets, temperatura, la pérdida combinada, la KL a nivel de token en ambas direcciones y la restricción del tokenizer, de las etapas 1 y 2
- [Secuencia y datos sintéticos](reference/sequence-and-synthetic-data.md): destilación a nivel de secuencia, datos generados, rationales, filtrado y las preguntas de licencia, de las etapas 3 y 4
- [Destilación on-policy](reference/on-policy-distillation.md): exposure bias, GKD y MiniLLM lado a lado, y cuándo compensa el entrenamiento on-policy, de la etapa 5
- [Lo que hereda el estudiante](reference/what-the-student-inherits.md): fidelidad, la brecha de imitación, la brecha de capacidad y los rasgos no intencionados, de la etapa 6
- [Dimensionar y medir](reference/sizing-and-measuring.md): elegir el tamaño del estudiante y el volumen de datos con el costo del profesor, y una eval honesta de estudiante frente a profesor, de las etapas 7 y 8
- [Lista de revisión de destilación](reference/distillation-review-checklist.md): elegir entre destilar, cuantizar y hacer fine-tuning, y las preguntas que hacerle a la afirmación de destilación de otra persona, de la etapa 9

## Cómo funciona

Cada lección es corta y autocontenida. Las claves de respuesta están plegadas: primero recuerda, luego ábrelas. Las prácticas en el mundo real importan más que la lectura, y espaciarlas es el punto. Todo lo que siga sin estar claro al final de una lección merece rastrearse hasta su fuente primaria antes de seguir.
