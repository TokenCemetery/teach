---
title: "Recursos"
description: "Fuentes de confianza sobre la cuantización de LLM"
type: resources
---

# Recursos de la cuantización

## Conocimiento

### Fundamentos

- [Paper: "A White Paper on Neural Network Quantization", Nagel et al., 2021](https://arxiv.org/abs/2106.08295)
  Una introducción del tamaño de un libro de texto, de Qualcomm AI Research: la motivación de hardware, el cuantizador afín uniforme, la elección del rango, la granularidad, los pipelines de PTQ y QAT y un flujo de depuración. Úsalo para: el mapeo y la elección del rango de las etapas 2 y 6, desde la fuente y no desde un resumen.
- [Paper: "A Survey of Quantization Methods for Efficient Neural Network Inference", Gholami et al., 2021](https://arxiv.org/abs/2103.13630)
  Un amplio panorama de cuantizadores uniformes y no uniformes, granularidad, PTQ frente a QAT y precisión mixta. Úsalo para: situar un método en la familia más amplia antes de leer su propio paper.
- [Paper: "Quantization and Training of Neural Networks for Efficient Integer-Arithmetic-Only Inference", Jacob et al., 2017](https://arxiv.org/abs/1712.05877)
  El esquema de inferencia solo con enteros que hay detrás de la mayoría de los despliegues en int8: el mapeo afín con un cero exactamente representable, y el entrenamiento con cuantización simulada. Úsalo para: de dónde viene la convención de scale y zero-point.

### Formatos numéricos

- [Paper: "Mixed Precision Training", Micikevicius et al., 2017](https://arxiv.org/abs/1710.03740)
  Entrenar en fp16 con una copia maestra en fp32 y escalado de la pérdida, y por qué el rango estrecho de fp16 hace necesario el escalado. Úsalo para: lo que cuestan los cinco bits de exponente de fp16.
- [Paper: "A Study of BFLOAT16 for Deep Learning Training", Kalamkar et al., 2019](https://arxiv.org/abs/1905.12322)
  El argumento a favor de bf16, que conserva el exponente de fp32 y recorta bits de mantisa. Úsalo para: por qué el rango importaba más que la precisión en el entrenamiento.
- [Paper: "FP8 Formats for Deep Learning", Micikevicius et al., 2022](https://arxiv.org/abs/2209.05433)
  Las codificaciones de punto flotante de ocho bits E4M3 y E5M2, sus valores especiales y los resultados de entrenar e inferir con ellas. Úsalo para: para qué sirve cada variante de fp8.
- [Paper: "Microscaling Data Formats for Deep Learning", Rouhani et al., 2023](https://arxiv.org/abs/2310.10537)
  Formatos con scale por bloque en los que un bloque de elementos estrechos comparte un scale que es potencia de dos, la base de los formatos MX de OCP. Úsalo para: cómo almacenan un bloque MXFP4 y sus parientes.
- [Article: "Introducing NVFP4 for Efficient and Accurate Low-Precision Inference", NVIDIA Technical Blog](https://developer.nvidia.com/blog/introducing-nvfp4-for-efficient-and-accurate-low-precision-inference/)
  El formato de punto flotante de 4 bits de un proveedor, con un bloque más pequeño y un scale más fino que MXFP4. Úsalo para: en qué se diferencia NVFP4 de MXFP4, leído como documentación del proveedor.

### Outliers

- [Paper: "LLM.int8(): 8-bit Matrix Multiplication for Transformers at Scale", Dettmers et al., 2022](https://arxiv.org/abs/2208.07339)
  Descubre las dimensiones de outlier features que rompen int8 en transformers grandes, y las conserva en 16 bits con una descomposición de precisión mixta. Úsalo para: dónde aparecen los outliers y la primera solución.
- [Paper: "Massive Activations in Large Language Models", Sun et al., 2024](https://arxiv.org/abs/2402.17762)
  Activaciones individuales varios órdenes de magnitud mayores que el resto, en dimensiones fijas y en tokens concretos, que actúan como sesgos aprendidos. Úsalo para: el segundo patrón de outliers y por qué no es ruido.
- [Paper: "Quantizable Transformers: Removing Outliers by Helping Attention Heads Do Nothing", Bondarenko et al., 2023](https://arxiv.org/abs/2306.12929)
  Vincula los outliers con cabezas de atención que aprenden a no hacer nada, y los elimina con un cambio de arquitectura durante el entrenamiento. Úsalo para: por qué existen los outliers.

### Cuantización post-entrenamiento

- [Paper: "The case for 4-bit precision: k-bit Inference Scaling Laws", Dettmers and Zettlemoyer, 2022](https://arxiv.org/abs/2212.09720)
  Más de 35,000 experimentos zero-shot entre anchos de bits, tipos de datos y tamaños de bloque, que encuentran que 4 bits es casi universalmente lo óptimo para un número fijo de bits del modelo, y solo lo mejoran los bloques pequeños y la elección del tipo de datos. Úsalo para: por qué los pesos de 4 bits se volvieron la opción por defecto, y qué aporta el tamaño de bloque.
- [Paper: "Up or Down? Adaptive Rounding for Post-Training Quantization", Nagel et al., 2020](https://arxiv.org/abs/2004.10568)
  Muestra que redondear cada peso a su nivel más cercano no es lo óptimo para la salida de la capa, y aprende en su lugar la dirección del redondeo. Úsalo para: por qué round-to-nearest deja accuracy sobre la mesa.
- [Paper: "Optimal Brain Compression", Frantar and Alistarh, 2022](https://arxiv.org/abs/2208.11580)
  El método exacto de cuantización capa por capa que GPTQ vuelve rápido, con la actualización que gasta el error de un peso en los demás. Úsalo para: el linaje de GPTQ.
- [Paper: "GPTQ: Accurate Post-Training Quantization for Generative Pre-trained Transformers", Frantar et al., 2022](https://arxiv.org/abs/2210.17323)
  Cuantización one-shot de pesos a 3 y 4 bits con información aproximada de segundo orden, a la escala de modelos de 175B parámetros. Úsalo para: cómo funciona GPTQ y qué es su calibration set.
- [Paper: "AWQ: Activation-aware Weight Quantization for LLM Compression and Acceleration", Lin et al., 2023](https://arxiv.org/abs/2306.00978)
  Descubre que una pequeña fracción de los canales de pesos importa más, los identifica por la magnitud de la activación y los protege con un scale por canal en lugar de precisión mixta. Úsalo para: cómo funciona AWQ y por qué no necesita backpropagation.
- [Paper: "SmoothQuant: Accurate and Efficient Post-Training Quantization for Large Language Models", Xiao et al., 2022](https://arxiv.org/abs/2211.10438)
  Migra los outliers de las activaciones a los pesos con un scale por canal matemáticamente equivalente, lo que permite W8A8. Úsalo para: la cuantización de pesos y activaciones a 8 bits.
- [Paper: "QuaRot: Outlier-Free 4-Bit Inference in Rotated LLMs", Ashkboos et al., 2024](https://arxiv.org/abs/2404.00456)
  Rota los hidden states con transformadas de Hadamard para que los pesos, las activaciones y la KV cache se cuanticen todos a 4 bits. Úsalo para: cómo las rotaciones eliminan los outliers.
- [Paper: "SpinQuant: LLM Quantization with Learned Rotations", Liu et al., 2024](https://arxiv.org/abs/2405.16406)
  Aprende las matrices de rotación en lugar de fijarlas, y muestra que las rotaciones aleatorias varían mucho en calidad. Úsalo para: por qué importa la elección de la rotación.
- [Paper: "KIVI: A Tuning-Free Asymmetric 2bit Quantization for KV Cache", Liu et al., 2024](https://arxiv.org/abs/2402.02750)
  Encuentra que las keys deben cuantizarse por canal y los values por token, y hace ambas cosas a 2 bits. Úsalo para: la elección del eje en la cuantización de la KV cache.
- [Paper: "KVQuant: Towards 10 Million Context Length LLM Inference with KV Cache Quantization", Hooper et al., 2024](https://arxiv.org/abs/2401.18079)
  Cuantización de keys por canal antes del rotary embedding, tipos no uniformes y manejo de outliers para contextos muy largos. Úsalo para: qué aporta la cuantización de la KV cache con contexto largo.
- [Repo: gptq, IST-DASLab](https://github.com/IST-DASLab/gptq)
  La implementación de referencia de los autores de GPTQ, cuyo README documenta `--act-order` (cuantizar las columnas en orden decreciente de tamaño de activación), `--true-sequential` y `--static-groups`. Úsalo para: act-order y el tensor `g_idx`, que el paper no describe.

### Quantization-aware training

- [Paper: "Estimating or Propagating Gradients Through Stochastic Neurons for Conditional Computation", Bengio et al., 2013](https://arxiv.org/abs/1308.3432)
  Presenta y compara estimadores de gradientes a través de umbrales duros, entre ellos el straight-through estimator. Úsalo para: de dónde viene el STE.
- [Paper: "LLM-QAT: Data-Free Quantization Aware Training for Large Language Models", Liu et al., 2023](https://arxiv.org/abs/2305.17888)
  QAT en LLM con datos que genera el propio modelo, incluida la cuantización de la KV cache, comparado con PTQ a 4 bits. Úsalo para: qué recupera el QAT en un LLM y a qué costo.
- [Paper: "QLoRA: Efficient Finetuning of Quantized LLMs", Dettmers et al., 2023](https://arxiv.org/abs/2305.14314)
  NF4, doble cuantización y entrenamiento de adapters a través de un base congelado de 4 bits. Úsalo para: el límite con el QAT, y la fuente de la que enseña el track de finetuning.
- [Article: "Quantization-Aware Training for Large Language Models with PyTorch", PyTorch Blog, 2024](https://pytorch.org/blog/quantization-aware-training/)
  El flujo de QAT de torchao sobre Llama 2 y Llama 3, con la recuperación medida frente a PTQ y el sobrecosto de fine-tuning de la fake quantization. Úsalo para: qué recupera y qué cuesta el QAT en un LLM real, leído como las mediciones de un solo equipo.

### Hardware y servicio

- [Paper: "MARLIN: Mixed-Precision Auto-Regressive Parallel Inference on Large Language Models", Frantar et al., 2024](https://arxiv.org/abs/2408.11743)
  Un kernel de GPU de pesos de 4 bits y activaciones de 16 bits, y un análisis de cuándo la cuantización solo de pesos acelera el decode por lotes. Úsalo para: por qué la aceleración depende del tamaño de lote.
- [Paper: "QServe: W4A8KV4 Quantization and System Co-design for Efficient LLM Serving", Lin et al., 2024](https://arxiv.org/abs/2405.04532)
  Muestra que el sobrecosto de la descuantización puede borrar la ganancia de los esquemas de 4 bits en GPU, y diseña a la vez un formato y un kernel para evitarlo. Úsalo para: por qué menos bits no es automáticamente más rápido.
- [Docs: "Quantization", vLLM](https://docs.vllm.ai/en/latest/features/quantization/)
  Los esquemas que soporta un motor de servicio y en qué hardware. Úsalo para: comprobar si un esquema tiene un kernel antes de elegirlo.
- [Docs: "Quantized KV Cache", vLLM](https://docs.vllm.ai/en/latest/features/quantization/quantized_kvcache/)
  La KV cache en fp8: scales por tensor o por cabeza, scales por defecto sin calibración y su calibración con llm-compressor. Úsalo para: qué necesita en la práctica una KV cache de 8 bits.
- [Docs: "Quantization overview", Hugging Face Transformers](https://huggingface.co/docs/transformers/main/en/quantization/overview)
  Los backends de cuantización que integra Transformers y cómo elegir entre ellos. Úsalo para: un mapa de las herramientas.
- [Repo: llm-compressor, vLLM project](https://github.com/vllm-project/llm-compressor)
  Una biblioteca que aplica recetas de GPTQ, AWQ, SmoothQuant y FP8 y escribe checkpoints que vLLM carga. Úsalo para: ejecutar PTQ de principio a fin sobre un modelo real.
- [Repo: compressed-tensors, Neural Magic](https://github.com/neuralmagic/compressed-tensors)
  La extensión de safetensors que registra el esquema de cuantización de un checkpoint en su configuración. Úsalo para: qué almacena un checkpoint cuantizado en safetensors.
- [Docs: "int8 W8A8" example, llm-compressor](https://github.com/vllm-project/llm-compressor/blob/main/examples/quantization_w8a8_int8/README.md)
  Una receta W8A8 int8 resuelta: SmoothQuant, luego GPTQ con scales de pesos por canal, y luego scales de activaciones dinámicos por token. Úsalo para: ejecutar SmoothQuant sobre un modelo real.
- [Docs: "Choosing a dataset", LLM Compressor](https://docs.vllm.ai/projects/llm-compressor/en/latest/steps/choosing-dataset/)
  Qué algoritmos necesitan un calibration set, cómo hacer coincidir su dominio con el uso previsto y qué tamaños son típicos. Úsalo para: orientación práctica sobre un calibration set.
- [Docs: "GPTQ", Hugging Face Transformers](https://huggingface.co/docs/transformers/main/en/quantization/gptq)
  Ejecutar GPTQ mediante `GPTQConfig` con un dataset incluido o con tu propio texto. Úsalo para: cuantizar con GPTQ desde Transformers.
- [Docs: "AWQ", Hugging Face Transformers](https://huggingface.co/docs/transformers/main/en/quantization/awq)
  Cargar checkpoints de AWQ y las claves de `quantization_config` que registra un checkpoint de AWQ. Úsalo para: leer la configuración de un checkpoint de AWQ.
- [Docs: "bitsandbytes", Hugging Face Transformers](https://huggingface.co/docs/transformers/main/en/quantization/bitsandbytes)
  Cómo carga Transformers los modelos de bitsandbytes de 8 y 4 bits, incluido el tipo de datos de cómputo. Úsalo para: ver que los pesos de 4 bits almacenados se calculan en una precisión mayor.
- [Docs: "NVIDIA A100 Tensor Core GPU" datasheet, NVIDIA](https://www.nvidia.com/content/dam/en-zz/Solutions/Data-Center/a100/pdf/nvidia-a100-datasheet-nvidia-us-2188504-web.pdf)
  El throughput de los tensor cores de la A100 por formato y su ancho de banda de memoria. Úsalo para: las cifras de Ampere en un roofline, leídas como documentación del proveedor.
- [Docs: "NVIDIA Ada GPU Architecture" whitepaper, NVIDIA](https://images.nvidia.com/aem-dam/Solutions/Data-Center/l4/nvidia-ada-gpu-architecture-whitepaper-v2.1.pdf)
  Los tensor cores de Ada y su soporte de FP8. Úsalo para: qué GPU de inferencia tienen tensor cores FP8, leído como documentación del proveedor.
- [Docs: "NVIDIA H100 Tensor Core GPU", NVIDIA](https://www.nvidia.com/en-us/data-center/h100/)
  La tabla de especificaciones de la H100 con filas de tensor cores FP8 e INT8 y el ancho de banda de memoria. Úsalo para: las cifras de Hopper, leídas como documentación del proveedor.
- [Article: "NVIDIA Hopper Architecture In-Depth", NVIDIA Technical Blog](https://developer.nvidia.com/blog/nvidia-hopper-architecture-in-depth/)
  Los tensor cores FP8 y el Transformer Engine que llegaron con Hopper. Úsalo para: cuándo llegó el cómputo FP8 a las GPU de centro de datos de NVIDIA, leído como documentación del proveedor.

### Formatos de archivo

- [Docs: "Safetensors", Hugging Face](https://huggingface.co/docs/safetensors/index)
  El formato de archivo de tensores en el que se distribuyen la mayoría de los checkpoints, y qué almacena y qué no. Úsalo para: el contenedor junto al que vive una configuración de cuantización.
- [Docs: "GGUF", Hugging Face Hub](https://huggingface.co/docs/hub/gguf)
  Una visión general del formato GGUF y una tabla de sus tipos de cuantización con sus disposiciones de bits. Úsalo para: descifrar el nombre de un tipo de GGUF.
- [Docs: llama.cpp quantize tool README, ggml-org](https://github.com/ggml-org/llama.cpp/blob/master/tools/quantize/README.md)
  Cómo convierte llama.cpp un modelo a sus tipos de cuantización, la lista de tipos y cómo se le pasa la matriz de importancia. Úsalo para: producir tú mismo una cuantización GGUF.
- [Repo: safetensors, Hugging Face](https://github.com/huggingface/safetensors)
  El formato a nivel de byte: una longitud de encabezado de 8 bytes en little-endian, un encabezado JSON con nombres, dtypes, formas y offsets, y luego los datos. Úsalo para: leer el encabezado de un checkpoint sin cargar sus tensores.
- [Docs: "compressed-tensors", Hugging Face Transformers](https://huggingface.co/docs/transformers/main/en/quantization/compressed_tensors)
  Cargar checkpoints de compressed-tensors, con un ejemplo de `config_groups` en FP8 y su listado de tensores. Úsalo para: leer una configuración de compressed-tensors y sus tensores de scale.
- [Model card: "TinyLlama-1.1B-Chat-v1.0-GPTQ", TheBloke](https://huggingface.co/TheBloke/TinyLlama-1.1B-Chat-v1.0-GPTQ)
  Un checkpoint público pequeño de GPTQ de 4 bits cuya ficha explica los bits, el tamaño de grupo, el act order y el damping. Úsalo para: un checkpoint real que inspeccionar.
- [Source: ggml-common.h, ggml-org](https://github.com/ggml-org/llama.cpp/blob/master/ggml/src/ggml-common.h)
  El struct de C de cada tipo de bloque de GGUF. Úsalo para: derivar los bits por peso de un tipo a partir de su disposición en lugar de citarlos.
- [Pull request: "k-quants", ikawrakow, llama.cpp, 2023](https://github.com/ggml-org/llama.cpp/pull/1684)
  Introduce los k-quants, la nomenclatura de tipo 0 y tipo 1 y las mezclas originales S, M y L. Úsalo para: qué significaban los sufijos cuando se introdujeron.
- [Pull request: "Importance Matrix calculation", ikawrakow, llama.cpp, 2024](https://github.com/ggml-org/llama.cpp/pull/4861)
  Deriva la matriz de importancia a partir de las activaciones sobre un texto de calibración y la usa para ponderar el error de redondeo. Úsalo para: por qué una matriz de importancia es un calibration set.
- [Docs: llama.cpp imatrix tool README, ggml-org](https://github.com/ggml-org/llama.cpp/blob/master/tools/imatrix/README.md)
  Cómo calcular una matriz de importancia y pasársela a la herramienta quantize. Úsalo para: producir una tú mismo.

### Medir la pérdida de calidad

- [Paper: "Accuracy is Not All You Need", Dutta et al., 2024](https://arxiv.org/abs/2407.09141)
  Muestra que un modelo cuantizado puede igualar el accuracy de su baseline mientras cambia muchas respuestas individuales, y propone los flips y la divergencia KL como métricas de distancia. Úsalo para: por qué un promedio sin cambios puede ocultar un modelo cambiado.
- [Paper: "Give Me BF16 or Give Me Death? Accuracy-Performance Trade-Offs in LLM Quantization", Kurtic et al., 2024](https://arxiv.org/abs/2411.02355)
  Más de medio millón de evaluaciones de esquemas FP8, INT8 e INT4 en tamaños y tareas de Llama 3.1, con orientación de despliegue por esquema. Úsalo para: qué cuesta cada esquema, medido con cuidado.
- [Paper: "Scaling Laws for Precision", Kumar et al., 2024](https://arxiv.org/abs/2411.04330)
  Encuentra que la cuantización post-entrenamiento degrada más a un modelo cuantos más datos se usaron para entrenarlo. Úsalo para: por qué la respuesta habitual de 4 bits puede fallar en un modelo muy entrenado.
- [Repo: lm-evaluation-harness, EleutherAI](https://github.com/EleutherAI/lm-evaluation-harness)
  El harness con el que la mayoría de los papers de cuantización reportan el accuracy en tareas. Úsalo para: ejecutar las mismas tareas sobre un baseline y un modelo cuantizado.
- [Docs: "Perplexity of fixed-length models", Hugging Face Transformers](https://huggingface.co/docs/transformers/main/en/perplexity)
  Cómo se calcula la perplexity con una ventana deslizante, y por qué la ventana cambia el número. Úsalo para: calcular la perplexity de modo que dos ejecuciones sean comparables.
- [Paper: "Quantization Hurts Reasoning? An Empirical Study on Quantized Reasoning Models", Liu et al., 2025](https://arxiv.org/abs/2504.04823)
  Modelos de razonamiento cuantizados con cuantización de pesos, de la KV cache y de activaciones en benchmarks de matemáticas, ciencias y código, que encuentran que W8A8 y W4A16 pueden ser sin pérdida y que los anchos de bits menores son arriesgados. Úsalo para: si la respuesta habitual de 4 bits se sostiene en un modelo de razonamiento.
- [Docs: llama.cpp perplexity tool README, ggml-org](https://github.com/ggml-org/llama.cpp/blob/master/tools/perplexity/README.md)
  Estadísticas de perplexity, divergencia KL y acuerdo del token principal frente a logits de 16 bits, con una tabla de tipos de GGUF. Úsalo para: medir un GGUF cuantizado frente a su baseline más allá de la perplexity.

## Lagunas

- No existe una única tabla vigente y neutral respecto de los proveedores que diga qué generaciones de GPU calculan de forma nativa en qué formatos. La lección 20 se apoya en páginas de proveedores y en las matrices de soporte de los motores de servicio, que cambian con cada versión.
