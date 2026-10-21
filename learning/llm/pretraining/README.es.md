---
title: "Preentrenamiento de LLM"
description: "Entrena un modelo desde cero a escala: datos, tokenizer, entrenamiento distribuido y un presupuesto de cómputo defendible"
type: topic
---

# Preentrenamiento de LLM

Sé capaz de planificar y ejecutar un trabajo de preentrenamiento desde una inicialización aleatoria: construir el pipeline de datos, entrenar el tokenizer, elegir un presupuesto de tokens óptimo en cómputo para un número dado de parámetros, evitar que una ejecución distribuida de varios días diverja o se detenga por la falla de un nodo, y defender todo ese conjunto de decisiones ante alguien que, de otro modo, habría hecho simplemente fine-tuning de un base model existente.

**Última lección:** [0024. Revisar la configuración de la ejecución de entrenamiento de otra persona](lessons/0024-reviewing-someone-elses-training-run-config.md)

## Cómo se ve el éxito

- Construir un corpus de preentrenamiento deduplicado y filtrado por calidad a partir de fuentes en bruto, y decir qué elimina cada paso de filtrado y por qué.
- Entrenar un tokenizer y defender un tamaño de vocabulario frente a su efecto en la longitud de las secuencias y en el tamaño de la tabla de embeddings.
- Dado un número de parámetros y un presupuesto de cómputo, calcular el número de tokens óptimo en cómputo y defenderlo frente a una alternativa subentrenada al estilo de Kaplan.
- Explicar qué reparten ZeRO/FSDP, por qué el data parallelism por sí solo se queda sin memoria antes de quedarse sin cómputo, y cuándo el tensor o el pipeline parallelism valen su costo de comunicación.
- Leer la curva de loss y las normas de gradiente de una ejecución de entrenamiento, y decir si un spike es recuperable o significa reiniciar desde un checkpoint anterior.
- Diseñar un esquema de checkpointing para una ejecución de varios días que sobreviva a la falla de un nodo sin perder más que unos pocos minutos de progreso.
- Decidir si una tarea dada requiere preentrenamiento, preentrenamiento continuado o fine-tuning de un base model existente, y defender la elección en términos de costo.

## Restricciones

- Cercano a los frameworks, no agnóstico respecto a ellos. Las técnicas de entrenamiento distribuido (reparto de ZeRO, tensor y pipeline parallelism) son lo bastante estables como para que las lecciones nombren la biblioteca y la API reales que describen, a diferencia del pseudocódigo neutral respecto al proveedor que usa `llm/agents` para una superficie que cambia más rápido.
- Ninguna lección entrena un modelo a escala de frontera. Las prácticas son pequeñas (un modelo de escala GPT-2 en un puñado de GPUs, o una configuración multinodo simulada) y razonan desde ahí hasta lo que cambia a la escala que describen los papers citados.
- Se asume `llm/transformers`: el mecanismo de atención, el bucle de entrenamiento, la pérdida de entropía cruzada, AdamW, la precisión mixta y el gradient clipping son requisitos previos, no repaso.
- Se asume acceso a varias GPUs (aunque sean dos, o una simulación en CPU con varios procesos de las operaciones colectivas) para las prácticas de entrenamiento distribuido.

## Fuera de alcance

- La arquitectura transformer en sí, la pérdida de entropía cruzada, el backward pass, AdamW, la precisión mixta y el gradient clipping: consulta [`llm/transformers`](../../llm/transformers/). Este track empieza cuando ese bucle tiene que correr en cientos de GPUs sobre billones de tokens, no antes.
- Adaptar un base model existente con LoRA, QLoRA o DoRA: consulta [`llm/finetuning`](../../llm/finetuning/). El preentrenamiento parte de pesos aleatorios, no de un checkpoint, y las dos son las dos maneras de que cambien los pesos de un modelo, tratadas como hermanas y no una dentro de la otra.
- Paralelismo y cuantización en el momento de servir: consulta [`llm/inference`](../../llm/inference/). Este track cubre las versiones del paralelismo en tiempo de entrenamiento (sincronización de gradientes, reparto de activaciones y del estado del optimizador), no el serving.
- Metodología de evaluación y diseño de datos held-out: consulta [`llm/evals`](../../llm/evals/). Aquí se trata solo como la única capacidad que necesita una ejecución de preentrenamiento, validar un checkpoint a mitad de ejecución, y se enlaza en lugar de repetirse.
- Alinear un modelo preentrenado para convertirlo en un asistente: consulta [`llm/post-training`](../../llm/post-training/).
- La destilación como señal de entrenamiento, incluida la distribución de un profesor usada durante el preentrenamiento: consulta [`llm/distillation`](../../llm/distillation/). Ese track enseña la pérdida y la elección de datos; ejecutar el trabajo de preentrenamiento se queda aquí.

## El arco

Diez etapas, desde ningún conocimiento previo hasta el criterio de un perfil sénior. No es una lista de lecciones: una etapa abarca varias lecciones y los límites son difusos.

| Etapa | Lecciones | Cubre | Terminada cuando |
| --- | --- | --- | --- |
| 1. Pipeline de datos | 0001 a 0002 | Obtención de fuentes, deduplicación, filtrado de calidad | Puedes construir un corpus filtrado y deduplicado a partir de fuentes en bruto y defender lo que eliminó cada paso |
| 2. Entrenamiento del tokenizer | 0003 a 0004 | BPE y SentencePiece desde cero, disyuntivas del tamaño del vocabulario | Puedes entrenar un tokenizer y defender la elección de un tamaño de vocabulario |
| 3. Leyes de escalado | 0005 a 0006 | Kaplan frente a Chinchilla, la razón de tokens por parámetro óptima en cómputo | Dado un presupuesto de cómputo, puedes derivar un número de tokens óptimo en cómputo y defenderlo |
| 4. Data parallelism | 0007 a 0008 | All-reduce de gradientes, por qué deja de escalar por sí solo | Puedes decir por qué el data parallelism por sí solo se queda sin memoria antes de quedarse sin cómputo |
| 5. Repartir la memoria | 0009 a 0011 | Etapas 1 a 3 de ZeRO, FSDP, reparto de activaciones y del estado del optimizador | Puedes decir qué reparte cada etapa de ZeRO y cuánto cuesta en comunicación |
| 6. Model parallelism | 0012 a 0014 | Tensor y pipeline parallelism para entrenar | Puedes decidir cuándo el tensor o el pipeline parallelism se ganan su costo de comunicación frente al reparto por sí solo |
| 7. Numérica y estabilidad a escala | 0015 a 0017 | Precisión mixta a escala, loss spikes, normas de gradiente, programas de warmup y decay | Dada una curva de loss, puedes decir si un spike es recuperable o exige reiniciar desde un checkpoint anterior |
| 8. Checkpointing y tolerancia a fallas | 0018 a 0019 | Guardar y reanudar una ejecución de varios días, sobrevivir a la falla de un nodo | Puedes diseñar un esquema de checkpointing que acote el progreso perdido tras la falla de un nodo |
| 9. Monitorear una ejecución de entrenamiento | 0020 a 0021 | Curvas de loss, checkpoints de evaluación periódica, enlace con `llm/evals` | Puedes leer un dashboard de entrenamiento y decir si la ejecución va bien encaminada |
| 10. Criterio | 0022 a 0024 | Preentrenar frente a continuar el preentrenamiento frente a hacer fine-tuning, defender un presupuesto de cómputo, revisar la configuración de la ejecución de entrenamiento de otra persona | Se confía en ti para tomar la decisión y explicársela a otra persona |

## Lecciones

Recórrelas en orden.

| # | Lección | Enseña |
|---|---|---|
| [0001](lessons/0001-sourcing-and-mixing-a-pretraining-corpus.md) | Obtener y mezclar un corpus de preentrenamiento | Qué entra en un corpus de preentrenamiento, y por qué la mezcla de fuentes importa más que el total de bytes |
| [0002](lessons/0002-deduplication-and-quality-filtering.md) | Deduplicación y filtrado de calidad | Por qué se eliminan antes de entrenar el texto casi duplicado y los documentos de baja calidad, y qué cuesta saltarse ese paso |
| [0003](lessons/0003-byte-pair-encoding-from-scratch.md) | Byte-Pair Encoding desde cero | El algoritmo que convierte las palabras raras y desconocidas en secuencias de unidades de subpalabra aprendidas, resuelto a mano |
| [0004](lessons/0004-sentencepiece-and-the-vocabulary-size-tradeoff.md) | SentencePiece y la disyuntiva del tamaño del vocabulario | Tokenizar texto en bruto sin un pre-tokenizador, y qué cuesta realmente un vocabulario mayor o menor |
| [0005](lessons/0005-scaling-laws-what-kaplan-predicted.md) | Leyes de escalado: lo que predijo Kaplan | Una ley de potencias empírica permite pronosticar la loss de una ejecución de entrenamiento antes de pagarla, y qué predijo eso sobre cómo gastar un presupuesto de cómputo |
| [0006](lessons/0006-chinchilla-the-compute-optimal-correction.md) | Chinchilla: la corrección óptima en cómputo | Por qué el tamaño del modelo y el número de tokens deben escalar juntos, y cómo convertir un presupuesto de cómputo en un número de tokens |
| [0007](lessons/0007-data-parallelism-and-gradient-all-reduce.md) | Data parallelism y all-reduce de gradientes | Repartir un batch entre dispositivos que tienen cada uno una copia completa del modelo, y qué mantiene idénticas todas las copias |
| [0008](lessons/0008-why-data-parallelism-alone-runs-out-of-memory.md) | Por qué el data parallelism por sí solo se queda sin memoria | Contar exactamente qué guarda por parámetro un optimizador Adam de precisión mixta, y dónde choca con un muro |
| [0009](lessons/0009-zero-stage-1-and-2-partitioning-optimizer-state-and-gradients.md) | ZeRO etapas 1 y 2: particionar el estado del optimizador y los gradientes | Eliminar las copias redundantes del data parallelism gratis, antes de que el costo de comunicación tenga que crecer en absoluto |
| [0010](lessons/0010-zero-stage-3-and-fsdp-partitioning-parameters-too.md) | ZeRO etapa 3 y FSDP: particionar también los parámetros | Repartir los propios parámetros obliga a reconstruirlos bajo demanda, y eso es lo primero que cuesta |
| [0011](lessons/0011-activation-memory-and-zero-r.md) | Memoria de activaciones y ZeRO-R | Repartir los estados del modelo resuelve un problema de memoria y deja en pie un segundo, las activaciones |
| [0012](lessons/0012-tensor-parallelism-splitting-a-layers-matrices.md) | Tensor parallelism: dividir las matrices de una capa | Elegir por qué eje dividir una matriz de pesos para que un bloque transformer completo necesite un solo all-reduce |
| [0013](lessons/0013-pipeline-parallelism-splitting-the-models-layers.md) | Pipeline parallelism: dividir las capas del modelo | Asignar capas consecutivas a distintos dispositivos, y el tiempo ocioso que eso cuesta al principio y al final de cada batch |
| [0014](lessons/0014-combining-all-three-when-tensor-and-pipeline-parallelism-earn-their-cost.md) | Combinar los tres: cuándo el tensor y el pipeline parallelism se ganan su costo | Hacer coincidir cada estrategia de paralelismo con la interconexión que tolera, y cuándo el reparto por sí solo no basta |
| [0015](lessons/0015-mixed-precision-at-scale-bfloat16-and-stochastic-rounding.md) | Precisión mixta a escala: bfloat16 y redondeo estocástico | Un formato numérico con el rango de fp32 pero menos precisión, y qué cuesta actualizar los parámetros directamente en él |
| [0016](lessons/0016-loss-spikes-and-the-optimizers-own-instabilities.md) | Loss spikes y las inestabilidades propias del optimizador | El mismo spike puede venir de un mal batch o del propio optimizador, y distinguirlos exige una comparación controlada |
| [0017](lessons/0017-warmup-decay-and-growing-the-batch-mid-run.md) | Warmup, decay y aumentar el batch a mitad de la ejecución | Empezar despacio, decaer según un programa y dejar que el propio batch size cambie a mitad del entrenamiento |
| [0018](lessons/0018-what-a-checkpoint-has-to-hold.md) | Qué tiene que guardar un checkpoint | Un checkpoint que solo guarda los pesos no puede reanudar una ejecución con exactitud, y elegir cada cuánto guardar es una disyuntiva en sí misma |
| [0019](lessons/0019-surviving-a-node-failure.md) | Sobrevivir a la falla de un nodo | Pausar, diagnosticar, aislar lo que está roto y reanudar desde el último checkpoint, al costo que sea |
| [0020](lessons/0020-reading-a-loss-curve.md) | Leer una curva de loss | La curva de loss de entrenamiento por sí sola subestima los problemas; otras dos señales detectan lo que se le escapa, y lo detectan antes |
| [0021](lessons/0021-periodic-held-out-evaluation.md) | Evaluación periódica con datos held-out | La loss de entrenamiento dice que el modelo se ajusta a sus propios datos de entrenamiento; solo una comprobación held-out dice algo sobre el resto |
| [0022](lessons/0022-pretraining-is-usually-the-wrong-default.md) | El preentrenamiento suele ser la opción por defecto equivocada | Una segunda fase de preentrenamiento sobre un modelo existente logra la mayor parte del beneficio sin volver a pagar el costo completo |
| [0023](lessons/0023-defending-a-compute-budget.md) | Defender un presupuesto de cómputo | Un plan de preentrenamiento es una apuesta hecha de muchas decisiones separadas, y defenderlo significa defender cada una en sus propios términos |
| [0024](lessons/0024-reviewing-someone-elses-training-run-config.md) | Revisar la configuración de la ejecución de entrenamiento de otra persona | Recorrer el plan por cada etapa que cubrió este track, en orden, y resolver una afirmación en disputa desde la fuente y no desde una entrada de blog |

## Referencia

- [Glosario](GLOSSARY.md): términos canónicos de este tema
- [Recursos](RESOURCES.md): fuentes de confianza

## Cómo funciona

Cada lección es corta y autocontenida. Las claves de respuesta están plegadas: primero recuerda, luego ábrelas. Las prácticas en el mundo real importan más que la lectura, y espaciarlas es el punto. Todo lo que siga sin estar claro al final de una lección merece rastrearse hasta su fuente primaria antes de seguir.
