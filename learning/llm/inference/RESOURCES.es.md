---
title: "Recursos"
description: "Fuentes de confianza sobre la inferencia"
type: resources
---

# Recursos de la inferencia

## Conocimiento

- [Docs: vLLM Documentation, vLLM Project](https://docs.vllm.ai/en/latest/)
  Documentación oficial del stack de serving en GPU que este espacio de trabajo pone en marcha primero: instalación, serve, y los ajustes de batching y de memoria del motor. Úsalo para: cómo ejecutar y configurar el propio vLLM.
- [Paper: "Efficient Memory Management for Large Language Model Serving with PagedAttention", Kwon et al., SOSP 2023](https://arxiv.org/abs/2309.06180)
  El paper de PagedAttention: por qué la KV cache fragmenta los asignadores de memoria ordinarios y cómo la paginación lo arregla, con las cifras de throughput que motivan el diseño de vLLM. Úsalo para: entender qué cuesta la KV cache y por qué existe el gestor de memoria de vLLM.
- [Repo: llama.cpp, ggml-org](https://github.com/ggml-org/llama.cpp)
  Repositorio oficial del stack de serving en CPU/edge que este espacio de trabajo pone en marcha en segundo lugar: instrucciones de compilación, formatos de cuantización admitidos (GGUF) y los parámetros del binario del servidor. Úsalo para: cómo ejecutar y configurar el propio llama.cpp.
- [Pull request: "k-quants", ikawrakow, llama.cpp, 2023](https://github.com/ggml-org/llama.cpp/pull/1684)
  Introduce los tipos k-quant, su disposición en superbloques y las recetas `S`, `M` y `L` que mezclan tipos entre tensores. Úsalo para: qué almacena realmente un nombre GGUF como `Q4_K_M`.
- [Paper: "GPTQ: Accurate Post-Training Quantization for Generative Pre-trained Transformers", Frantar et al., 2023](https://arxiv.org/abs/2210.17323)
  Cuantización de pesos post-entrenamiento en una sola pasada hasta 3-4 bits, con un costo de precisión medido. Úsalo para: qué sacrifica realmente cuantizar un modelo para servirlo y cómo se mide ese compromiso.
  Lee primero la [guía de transformers](https://huggingface.co/docs/transformers/main/en/llm_optims) de más abajo si el álgebra lineal es el obstáculo.
- [Docs: "Optimizing inference", Hugging Face Transformers](https://huggingface.co/docs/transformers/main/en/llm_optims)
  Recorrido a nivel de practicante por la KV cache, el batching estático frente al dinámico y los backends de cuantización, sin exigir antes las matemáticas del paper. Úsalo para: un modelo mental funcional antes de las fuentes primarias anteriores.
- [Article: "Transformer Inference Arithmetic", Kipply](https://kipp.ly/transformer-inference-arithmetic/)
  Deriva la aritmética real de FLOP y de ancho de banda de memoria detrás de una pasada forward, incluido de dónde viene el costo de memoria de la KV cache. Úsalo para: calcular un presupuesto de latencia o de memoria desde primeros principios en lugar de citar un benchmark.
- [Article: "How continuous batching enables 23x throughput in LLM inference while reducing p50 latency", Anyscale](https://www.anyscale.com/blog/continuous-batching-llm-inference)
  Escrito por ingenieros que incorporaron el batching continuo a uno de los primeros motores de serving; explica por qué el batching estático desperdicia tiempo de GPU con un flujo de solicitudes de longitudes mixtas y cómo lo arregla el batching continuo. Úsalo para: la mitad de batching del compromiso entre latencia y throughput que defiende este espacio de trabajo.

- [Paper: "Fast Inference from Transformers via Speculative Decoding", Leviathan et al., 2022](https://arxiv.org/abs/2211.17192)
  Introduce el speculative decoding: un modelo pequeño redacta varios tokens y el modelo grande los verifica todos en una pasada paralela, con un método de muestreo que garantiza exactamente la misma distribución de salida que ejecutar solo el modelo grande. Úsalo para: por qué esto es una palanca de latencia pura y no un compromiso de calidad, y el argumento del ancho de banda de memoria de por qué la verificación paralela es casi gratis.
- [Paper: "Medusa: Simple LLM Inference Acceleration Framework with Multiple Decoding Heads", Cai et al., 2024](https://arxiv.org/abs/2401.10774)
  Sustituye el modelo borrador separado del speculative decoding por cabezas de decodificación adicionales añadidas directamente al modelo objetivo. Úsalo para: resolver la carga operativa de mantener un segundo modelo, conservando la misma garantía de verificar y corregir.
- [Paper: "EAGLE: Speculative Sampling Requires Rethinking Feature Uncertainty", Li et al., 2024](https://arxiv.org/abs/2401.15077)
  Redacta a nivel de las características internas del modelo en lugar de los tokens en bruto, resolviendo la incertidumbre de predicción a nivel de características al incorporar una secuencia de tokens adelantada un paso. Úsalo para: un refinamiento adicional sobre Medusa, con una aceleración reportada mayor que sigue preservando la distribución de salida del modelo objetivo.
- [Paper: "Efficient Guided Generation for Large Language Models" (Outlines), Willard and Louf, 2023](https://arxiv.org/abs/2307.09702)
  Replantea la generación restringida como transiciones entre estados de una máquina de estados finitos, lo que permite precalcular una vez por gramática un índice del vocabulario y reutilizarlo como una consulta rápida por token. Úsalo para: por qué la decodificación restringida por gramática o esquema añade poca sobrecarga por token y garantiza la estructura de la salida por construcción y no por esperanza.
- [Docs: "Automatic Prefix Caching", vLLM Project](https://docs.vllm.ai/en/latest/features/automatic_prefix_caching.html)
  La propia documentación de vLLM sobre reutilizar la KV cache de un prefijo compartido entre solicitudes por lo demás no relacionadas, sus dos cargas de trabajo de ejemplo con nombre (QA sobre documentos largos, conversación de varias rondas) y su límite declarado (acelera solo el prefill, nunca el decode). Úsalo para: el prefix caching como el mecanismo de compartición de bloques de PagedAttention extendido entre solicitudes.
- [Paper: "Megatron-LM: Training Multi-Billion Parameter Language Models Using Model Parallelism", Shoeybi et al., 2019](https://arxiv.org/abs/1909.08053)
  El paper canónico del tensor parallelism: un esquema de paralelismo de modelo intra-capa que divide entre GPU las multiplicaciones de matrices de una capa de transformer, con solo unas pocas operaciones de comunicación, y explícitamente ortogonal y complementario al pipeline parallelism. Úsalo para: qué hace realmente `--tensor-parallel-size` (lección 12) dentro de una capa.
- [Paper: "GPipe: Efficient Training of Giant Neural Networks using Pipeline Parallelism", Huang et al., 2018](https://arxiv.org/abs/1811.06965)
  El paper canónico del pipeline parallelism: reparte cualquier red expresable como una secuencia de capas en grupos consecutivos colocados en aceleradores distintos, e introduce los micro-lotes para reducir (no eliminar) la burbuja de pipeline resultante. Úsalo para: la división alternativa al tensor parallelism y por qué tolera un enlace entre dispositivos más lento.
- [Docs: "Welcome to production-stack" and use-case guides, vLLM Production Stack](https://docs.vllm.ai/projects/production-stack)
  Documentación oficial del despliegue de flota de referencia de vLLM, nativo de Kubernetes: enrutamiento de solicitudes consciente de la KV cache y autoscaling con KEDA a partir de métricas de profundidad de cola como `vllm:num_requests_waiting`. Úsalo para: cómo funcionan realmente el enrutamiento y el autoscaling a escala de flota, más allá de un solo servidor.
- [Paper: "ServerlessLLM: Low-Latency Serverless Inference for Large Language Models", Fu et al., OSDI 2024](https://arxiv.org/abs/2401.14351)
  Mide por qué los arranques en frío de los LLM son severos (el tiempo de carga del checkpoint supera con creces el tiempo de generación por token, decenas de segundos en trazas de producción) y lo arregla con una carga de checkpoints multinivel cercana a la GPU. Úsalo para: por qué añadir una réplica a la flota no es instantáneo y qué limita realmente lo rápido que puede volverse útil.
- [Docs: "Metrics", vLLM Project](https://docs.vllm.ai/en/stable/design/metrics/)
  La propia lista de vLLM de métricas Prometheus exportadas: TTFT, latencia entre tokens, latencia de extremo a extremo e histogramas separados del tiempo de prefill y de decode. Úsalo para: qué exporta de forma continua un servidor de producción, a diferencia de un benchmark puntual.
- [Google SRE Workbook: "Implementing SLOs"](https://sre.google/workbook/implementing-slos/)
  El planteamiento canónico de SRE de los SLI, los SLO y los presupuestos de error: una razón relevante para el usuario, un objetivo declarado para ella y la tolerancia a incumplir ese objetivo derivada directamente del SLO. Úsalo para: convertir una métrica exportada en bruto en un objetivo de producción accionable.
- [Paper: "YaRN: Efficient Context Window Extension of Large Language Models", Peng et al., ICLR 2024](https://arxiv.org/abs/2309.00071)
  Amplía la longitud de contexto utilizable de un modelo más allá de su longitud de entrenamiento reescalando de forma no uniforme las dimensiones de frecuencia de RoPE, a una fracción del costo de fine-tuning de los métodos anteriores. Úsalo para: por qué el escalado de RoPE cambia la longitud máxima de contexto sin tocar el crecimiento propio de la KV cache.
- [Paper: "Mistral 7B", Jiang et al., 2023](https://arxiv.org/abs/2310.06825)
  Introduce la atención de ventana deslizante y su caché de buffer rotativo asociada: cada token atiende como máximo a una ventana fija de tokens previos, lo que limita el tamaño de la caché sin importar la longitud de la secuencia. Úsalo para: el mecanismo que convierte en constante el crecimiento lineal de la caché de la lección 2.
- [Paper: "Efficient Streaming Language Models with Attention Sinks", Xiao et al., ICLR 2024](https://arxiv.org/abs/2309.17453)
  Identifica el fenómeno de attention sink detrás de por qué la atención de ventana deslizante simple colapsa cuando se descartan los tokens antiguos, y lo arregla conservando de forma permanente las entradas KV de un puñado de tokens iniciales. Úsalo para: por qué una caché acotada puede seguir atendiendo un flujo en la práctica ilimitado.

## Lagunas

- Todavía no hay una fuente sobre la cuantización al servir específica para los formatos GGUF de llama.cpp (a diferencia de GPTQ/AWQ, que apuntan a stacks de GPU); la misión necesita una comparación de cuantización específica para CPU/edge cuando el diseño de lecciones llegue a esa etapa.
