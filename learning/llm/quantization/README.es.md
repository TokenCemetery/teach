---
title: "Cuantización"
description: "Cuantiza un LLM y defiéndelo: formatos numéricos, métodos PTQ y QAT, qué corre más rápido y cómo medir lo que costó"
type: topic
---

# Aprendizaje: cuantización

Toma un LLM entrenado y hazlo más pequeño y más rápido con la cuantización, sabiendo qué le hace cada formato numérico y cada método a sus pesos, sus activaciones y su KV cache. Termina siendo capaz de elegir un esquema para un modelo, un hardware y un nivel de calidad dados, medir con honestidad lo que costó y revisar la afirmación de otra persona de que un modelo cuantizado "no pierde nada".

**Última lección:** [27. Cuando la respuesta habitual es incorrecta](lessons/0027-when-the-usual-answer-is-wrong.md)

## Cómo se ve el éxito

- Leer la disposición de bits de un formato numérico, decir qué rango y qué precisión da, y calcular la huella de memoria de un modelo en ese formato.
- Cuantizar un tensor a mano: elegir el scale, el zero-point, el rango de recorte y la granularidad, y predecir de dónde saldrá el error.
- Explicar por qué los LLM tienen outlier features y activaciones outlier, y qué técnica maneja cada una.
- Explicar qué le hacen a los pesos round-to-nearest, GPTQ y AWQ, y qué aporta el calibration set y en qué puede fallar.
- Decidir cuándo se pueden cuantizar también las activaciones y la KV cache además de los pesos, y con qué técnica.
- Decir cuándo el quantization-aware training se gana su costo frente a la cuantización post-entrenamiento.
- Predecir si un esquema correrá de verdad más rápido en un hardware dado con un tamaño de lote dado, en lugar de suponer que menos bits significa más velocidad.
- Medir la calidad que costó una cuantización, más allá de la perplexity, frente a un baseline honesto.
- Leer un checkpoint cuantizado, en safetensors con su configuración de cuantización o en GGUF, y decir qué se almacena en él.
- Elegir un esquema para un modelo, un hardware y un nivel de calidad dados, revisar la afirmación de cuantización de otra persona nombrando lo que oculta, y decir cuándo la respuesta habitual es la equivocada.

## Restricciones

- Se asume soltura para leer Python y NumPy, y saber qué es una capa de transformer al nivel de "multiplicaciones de matrices más atención". No se requiere conocimiento previo de cuantización ni de los entresijos del punto flotante.
- Neutral respecto del hardware donde se puede. Donde una afirmación describe el comportamiento documentado de un solo proveedor o de una sola biblioteca, la lección lo nombra, porque el soporte de kernels cambia más rápido que la teoría.
- La práctica corre en un portátil con NumPy en las etapas 1 a 3. Las prácticas posteriores cuantizan un modelo abierto pequeño, para lo que basta un notebook con GPU gratuita.

## Fuera de alcance

- QLoRA, entrenar un adapter a través de un base de 4 bits: consulta [`llm/finetuning`](../../llm/finetuning/), etapa 4 (lecciones 0014 a 0017). Este track enseña la teoría general que esas lecciones aplican, y enlaza a ellas en lugar de repetir QLoRA.
- Elegir un esquema para un presupuesto de latencia al servir y ejecutarlo en vLLM o llama.cpp: consulta [`llm/inference`](../../llm/inference/), etapa 3 (lecciones 0007 a 0009) y su hoja [Cuantización al servir](../../llm/inference/reference/quantization-at-serve-time.md). Este track enseña cómo funcionan los métodos y cómo juzgarlos; la decisión de servicio se queda allí.
- Construir una eval: consulta [`llm/evals`](../../llm/evals/) y su hoja [Go/No-Go](../../llm/evals/reference/go-no-go.md). Este track usa una eval para medir la pérdida por cuantización y no vuelve a enseñar cómo construir una.
- La poda (pruning), la sparsity y la destilación, las otras maneras de reducir un modelo. Se combinan con la cuantización pero son temas aparte. La destilación tiene su propio track, [`llm/distillation`](../../llm/distillation/), que la compara con la cuantización en su etapa de criterio.
- Escribir kernels de cuantización. La etapa 7 enseña qué debe hacer un kernel para que un esquema corra más rápido, no cómo escribir uno.

El límite con los dos vecinos quedó fijado al escribir este track: las lecciones de finetuning y de inference se quedan como están, cada una enseñando la porción que necesita su caso de uso, y enlazan aquí para los fundamentos.

## El arco

Diez etapas, desde qué es un formato numérico hasta el criterio para revisar la cuantización de otra persona. Una etapa abarca varias lecciones y los límites son difusos; lo que da una etapa por terminada es la capacidad, no el número de lecciones.

| Etapa | Lecciones | Cubre | Terminada cuando |
|---|---|---|---|
| 1. Formatos numéricos | 0001 a 0003 | Qué aporta la cuantización, fp32, fp16, bf16, fp8, int8, int4 y los formatos con scale por bloque | Puedes leer la disposición de bits de un formato y dimensionar un modelo en él |
| 2. El mapeo de cuantización | 0004 a 0006 | Cuantizar y descuantizar, scale y zero-point, elegir el rango de recorte, per-tensor, per-channel y per-group | Puedes cuantizar un tensor a mano y predecir su error |
| 3. Outliers | 0007 a 0008 | Outlier features y activaciones masivas en los LLM, y las familias de soluciones | Puedes decir por qué un LLM en int8 ingenuo se rompe y qué solución aplica |
| 4. Cuantización de pesos post-entrenamiento | 0009 a 0012 | Round-to-nearest, GPTQ, AWQ, el calibration set | Puedes cuantizar los pesos de un modelo a 4 bits y explicar qué cambió cada método |
| 5. Activaciones y la KV cache | 0013 a 0016 | Solo pesos frente a pesos y activaciones, SmoothQuant, rotaciones, cuantización de la KV cache | Puedes decidir qué cuantizar además de los pesos y con qué técnica |
| 6. Quantization-aware training | 0017 a 0018 | Fake quantization, el straight-through estimator, QAT para LLM | Puedes decir cuándo el QAT vale su costo frente a la PTQ |
| 7. Hardware y kernels | 0019 a 0020 | Limitado por el ancho de banda de memoria frente a limitado por cómputo, qué debe soportar un kernel, qué hardware corre qué formato | Puedes predecir si un esquema corre más rápido en un hardware y un tamaño de lote dados |
| 8. Medir la pérdida de calidad | 0021 a 0022 | Perplexity y sus límites, flips, suites de tareas, una comparación honesta | Puedes medir lo que costó una cuantización y defender la cifra |
| 9. Formatos de archivo | 0023 a 0024 | Safetensors con configuraciones de cuantización, tipos de cuantización de GGUF y la matriz de importancia | Puedes leer un checkpoint cuantizado y decir qué almacena |
| 10. Criterio | 0025 a 0027 | Elegir un esquema, revisar una afirmación, desplegar un modelo cuantizado del que otros dependen, cuándo la respuesta habitual es incorrecta | Se confía en ti para decidir sobre una cuantización y explicárselo a otra persona |

## Lecciones

Recórrelas en orden.

| # | Lección | Enseña |
|---|---|---|
| [0001](lessons/0001-what-quantization-buys.md) | Qué aporta la cuantización | Menos bits por parámetro reducen la memoria y los bytes que se leen por token, que es de donde sale la mayor parte de la velocidad |
| [0002](lessons/0002-floating-point-formats.md) | Formatos de punto flotante | Cómo los bits de signo, exponente y mantisa reparten rango y precisión en fp32, fp16 y bf16 |
| [0003](lessons/0003-low-bit-formats.md) | Formatos de pocos bits | Qué pueden y qué no pueden representar fp8, int8, int4 y los formatos con scale por bloque como MXFP4 |
| [0004](lessons/0004-quantize-and-dequantize.md) | Cuantizar y descuantizar | El mapeo afín de valores reales a enteros: scale, zero-point, redondeo y clamping |
| [0005](lessons/0005-choosing-the-range.md) | Elegir el rango | Por qué recortar el rango cambia un poco de error de recorte por mucho menos error de redondeo |
| [0006](lessons/0006-granularity.md) | Granularidad | Scales per-tensor, per-channel y per-group, y qué cuesta cada uno en bits almacenados |
| [0007](lessons/0007-why-llms-have-outliers.md) | Por qué los LLM tienen outliers | Dimensiones de outlier features y activaciones masivas, dónde aparecen y por qué un solo valor arruina el scale de un tensor |
| [0008](lessons/0008-handling-outliers.md) | Manejar los outliers | Las cuatro familias de soluciones: mantenerlos en alta precisión, reducir el grupo, migrarlos o rotarlos para dispersarlos |
| [0009](lessons/0009-round-to-nearest.md) | Round-to-nearest | Cuantizar los pesos de uno en uno sin datos, por qué aguanta a 8 bits y se resbala a 4 o menos |
| [0010](lessons/0010-gptq.md) | GPTQ | Cuantizar los pesos de una capa en secuencia y gastar cada error de redondeo en los pesos aún no cuantizados |
| [0011](lessons/0011-awq.md) | AWQ | Proteger los pesos que se encuentran con activaciones grandes escalando sus canales antes de redondear |
| [0012](lessons/0012-the-calibration-set.md) | El calibration set | Qué datos de calibración lee un método, cuántos necesita y cómo se nota un conjunto que no coincide |
| [0013](lessons/0013-weights-activations-or-both.md) | Pesos, activaciones o ambos | Qué ahorra cada esquema de solo pesos y de pesos y activaciones, y por qué las activaciones son más difíciles |
| [0014](lessons/0014-smoothquant.md) | SmoothQuant | Mover la dificultad de cuantizar de las activaciones a los pesos con un scale por canal |
| [0015](lessons/0015-rotations.md) | Rotaciones | Multiplicar por una matriz ortogonal para repartir los outliers entre canales y que sobrevivan las activaciones de 4 bits |
| [0016](lessons/0016-kv-cache-quantization.md) | Cuantización de la KV cache | Por qué las keys y los values se cuantizan a lo largo de ejes distintos, y qué aporta con contexto largo |
| [0017](lessons/0017-fake-quantization-and-the-ste.md) | Fake quantization y el STE | Cómo ve el entrenamiento la cuantización: redondeo simulado en el forward pass, un gradiente straight-through en el backward pass |
| [0018](lessons/0018-qat-for-llms.md) | QAT para LLM | Qué cuesta el quantization-aware training en un LLM, qué recupera y cuándo basta la PTQ |
| [0019](lessons/0019-what-actually-runs-faster.md) | Qué corre realmente más rápido | Por qué la cuantización solo de pesos acelera el decode con lotes pequeños y puede ralentizar el prefill con lotes grandes |
| [0020](lessons/0020-hardware-and-kernel-support.md) | Hardware y soporte de kernels | En qué formatos calcula una GPU de forma nativa, cuáles solo almacena y qué cuesta un kernel que falta |
| [0021](lessons/0021-perplexity-and-its-limits.md) | Perplexity y sus límites | Qué mide la perplexity, por qué un cambio pequeño puede ocultar grandes flips de respuestas y qué medir en su lugar |
| [0022](lessons/0022-an-honest-quantization-eval.md) | Una eval honesta de cuantización | Comparar un modelo cuantizado con su baseline en el mismo harness y las mismas tareas, e informar de qué perdió y dónde |
| [0023](lessons/0023-quantized-checkpoints.md) | Checkpoints cuantizados | Qué almacena un checkpoint cuantizado en safetensors, y cómo su configuración de cuantización le dice a un cargador cómo leerlo |
| [0024](lessons/0024-gguf-quant-types.md) | Tipos de cuantización de GGUF | Qué significa el nombre de un tipo de GGUF como Q4_K_M, y qué cambia la matriz de importancia |
| [0025](lessons/0025-choosing-a-scheme.md) | Elegir un esquema | Elegir un formato y un método según el modelo, el hardware, la forma del lote y el nivel de calidad |
| [0026](lessons/0026-reviewing-a-quantization-claim.md) | Revisar una afirmación de cuantización | Revisar "4 bits sin pérdida de calidad" nombrando lo que la medición ocultó, y desplegar un modelo cuantizado del que otros dependen |
| [0027](lessons/0027-when-the-usual-answer-is-wrong.md) | Cuando la respuesta habitual es incorrecta | Reconocer cuándo los pesos de 4 bits o una receta estándar son la decisión equivocada, y resolver la disputa desde la fuente primaria |

## Referencia

- [Glosario](GLOSSARY.md): términos canónicos de este tema
- [Recursos](RESOURCES.md): fuentes de confianza, cada una anotada con lo que cubre
- [Formatos numéricos](reference/number-formats.md): disposiciones de bits, rango y precisión de cada formato, y aritmética de memoria, de la etapa 1
- [El mapeo de cuantización](reference/quantization-mapping.md): las fórmulas de cuantizar y descuantizar, la elección del rango, la granularidad y las soluciones para outliers, de las etapas 2 y 3
- [Métodos PTQ de pesos](reference/weight-ptq-methods.md): round-to-nearest, GPTQ y AWQ lado a lado, y qué hace el calibration set, de la etapa 4
- [Activaciones y KV cache](reference/activations-and-kv-cache.md): solo pesos frente a pesos y activaciones, SmoothQuant, rotaciones y cuantización de la KV cache, de la etapa 5
- [QAT y hardware](reference/qat-and-hardware.md): cómo funciona el QAT y cuándo compensa, y qué hace que un esquema corra más rápido, de las etapas 6 y 7
- [Medir y almacenar](reference/measuring-and-storing.md): una eval honesta de cuantización, y cómo leer un checkpoint cuantizado o un tipo de GGUF, de las etapas 8 y 9
- [Lista de revisión de cuantización](reference/quantization-review-checklist.md): elegir un esquema y las preguntas que hacerle a la afirmación de cuantización de otra persona, de la etapa 10

## Cómo funciona

Cada lección es corta y autocontenida. Las claves de respuesta están plegadas: primero recuerda, luego ábrelas. Las prácticas en el mundo real importan más que la lectura, y espaciarlas es el punto. Todo lo que siga sin estar claro al final de una lección merece rastrearse hasta su fuente primaria antes de seguir.
