---
title: "Recursos"
description: "Fuentes y comunidades de confianza sobre el fine-tuning con adapters"
type: resources
---

# Recursos del fine-tuning con adapters

## Conocimiento

### Los tres métodos

- [Paper: "LoRA: Low-Rank Adaptation of Large Language Models", Hu et al., arXiv:2106.09685](https://arxiv.org/abs/2106.09685)
  El método original de adapters de bajo rank y el argumento de la dimensionalidad intrínseca de por qué funciona. Úsalo para: la etapa 3, y para qué controlan realmente rank y alpha.

- [Paper: "QLoRA: Efficient Finetuning of Quantized LLMs", Dettmers et al., arXiv:2305.14314](https://arxiv.org/abs/2305.14314)
  NF4, doble cuantización y optimizadores paginados, con la contabilidad de memoria explicada paso a paso. Úsalo para: la etapa 4, y como referencia de lo que cuesta en calidad un base cuantizado. Lee la sección de limitaciones.

- [Paper: "DoRA: Weight-Decomposed Low-Rank Adaptation", Liu et al., arXiv:2402.09353](https://arxiv.org/abs/2402.09353)
  Separa los pesos en magnitud y dirección y adapta la dirección. Úsalo para: la etapa 5. El análisis de la sección 4 sobre cómo se mueve cada magnitud en el full fine-tuning y en LoRA es el argumento real.

- [Paper: "Intrinsic Dimensionality Explains the Effectiveness of Language Model Fine-Tuning", Aghajanyan et al., arXiv:2012.13255](https://arxiv.org/abs/2012.13255)
  Por qué la adaptación puede vivir en un subespacio de baja dimensión. Úsalo para: la justificación que hay debajo de LoRA más que su mecanismo.

### Práctica actual

- [Docs: "LoRA Without Regret", Hugging Face TRL](https://huggingface.co/docs/trl/main/en/lora_without_regret)
  El argumento de que apuntar a todas las capas lineales con un rank adecuado cierra la brecha con el full fine-tuning. Úsalo para: la elección de target modules y de rank, y como el baseline que debe superar cualquier variante nueva. Esto sustituye a la convención de solo atención heredada del paper original.

- [Blog: "Practical Tips for Finetuning LLMs Using LoRA", Sebastian Raschka, Ahead of AI](https://magazine.sebastianraschka.com/p/practical-tips-for-finetuning-llms)
  Ablaciones sobre rank, alpha y target modules, con los experimentos a la vista. Úsalo para: contrastar con mediciones el folclore de los hiperparámetros.

- [Docs: PEFT, Hugging Face](https://huggingface.co/docs/peft)
  Implementación de referencia de los tres métodos y de la superficie de configuración que exponen. Úsalo para: cómo se llama un hiperparámetro en la práctica, y qué variantes están lo bastante establecidas como para ser un flag. Es sensible a la versión, así que compruébalo contra la versión instalada y no de memoria.

- [Docs: SFTTrainer, Hugging Face TRL](https://huggingface.co/docs/trl/main/en/sft_trainer)
  El bucle estándar de supervised fine-tuning y sus formatos de dataset. Úsalo para: de la etapa 3 en adelante. Es sensible a la versión; los nombres de los parámetros han cambiado entre versiones.

### Fundamentos

- [Interactive: LLM Visualization, Brendan Bycroft](https://bbycroft.net/llm)
  Recorre el camino de un solo token con el conteo de parámetros de cada matriz. Úsalo para: la etapa 1, y la mejor respuesta disponible a "dónde viven los parámetros".

- [Blog: "The Illustrated Transformer", Jay Alammar](https://jalammar.github.io/illustrated-transformer/)
  La explicación visual estándar de la arquitectura. Úsalo para: la etapa 1 cuando la estructura de bloques aún no ha calado.

- [Docs: Chat Templates, Hugging Face Transformers](https://huggingface.co/docs/transformers/main/en/chat_templating)
  Cómo se renderizan las conversaciones como secuencias de tokens, y cómo aplicar el template propio del modelo. Úsalo para: el fallo silencioso más común del fine-tuning.

- [Paper: "Decoupled Weight Decay Regularization" (AdamW), Loshchilov & Hutter, arXiv:1711.05101](https://arxiv.org/abs/1711.05101)
  El optimizador que se usa aquí en todas partes, y por qué su weight decay difiere del de Adam. Úsalo para: el argumento de memoria de la etapa 2.

- [Paper: "ZeRO: Memory Optimizations Toward Training Trillion Parameter Models", Rajbhandari et al., arXiv:1910.02054](https://arxiv.org/abs/1910.02054)
  La contabilidad canónica de pesos, gradientes y estado del optimizador como categorías de memoria separadas. Úsalo para: derivar la cifra de dieciséis bytes por parámetro.

- [Paper: "Training Deep Nets with Sublinear Memory Cost", Chen et al., arXiv:1604.06174](https://arxiv.org/abs/1604.06174)
  El gradient checkpointing, y el intercambio de cómputo por memoria que hace. Úsalo para: la etapa 2, y para el ajuste que dejarás activado de forma permanente.

- [Blog: "A Recipe for Training Neural Networks", Andrej Karpathy](https://karpathy.github.io/2019/04/25/recipe/)
  Cómo ejecutar experimentos para que sus resultados signifiquen algo. Úsalo para: la lección de diagnóstico de la etapa 3, y la prueba de humo de sobreajustar dos ejemplos.

### Cuantización

- [Paper: "LLM.int8(): 8-bit Matrix Multiplication for Transformers at Scale", Dettmers et al., arXiv:2208.07339](https://arxiv.org/abs/2208.07339)
  El problema de las features outlier que vuelve la cuantización de transformers más difícil de lo que sugiere la aritmética. Úsalo para: por qué lo blockwise supera a lo per-tensor.

- [Docs: bitsandbytes quantization, Hugging Face Transformers](https://huggingface.co/docs/transformers/main/en/quantization/bitsandbytes)
  La superficie de configuración de 4 bits en la práctica. Úsalo para: la preparación de la etapa 4.

- [Code: bitsandbytes, bitsandbytes-foundation](https://github.com/bitsandbytes-foundation/bitsandbytes)
  El directorio `backends/` es la autoridad sobre qué hardware soporta qué operación. Úsalo para: zanjar una duda de soporte de hardware contra el código fuente y no contra un tutorial, que en esta área suele estar desactualizado.

### Datos y evaluación

- [Paper: "LIMA: Less Is More for Alignment", Zhou et al., arXiv:2305.11206](https://arxiv.org/abs/2305.11206)
  Evidencia de que un dataset pequeño y cuidadosamente curado rinde más que uno grande y descuidado, y de que el SFT enseña sobre todo formato. Úsalo para: el argumento de apertura de la etapa 6.

- [Paper: "Judging LLM-as-a-Judge with MT-Bench and Chatbot Arena", Zheng et al., arXiv:2306.05685](https://arxiv.org/abs/2306.05685)
  Evaluación con un modelo como juez, con sus sesgos caracterizados: posición, verbosidad, autopreferencia. Úsalo para: las métricas de generación de texto libre, y para entender por qué el juez necesita calibrarse contra etiquetas humanas.

- [Paper: "An Empirical Study of Catastrophic Forgetting in Large Language Models During Continual Fine-tuning", Luo et al., arXiv:2308.08747](https://arxiv.org/abs/2308.08747)
  Que el olvido es medible, común y no se limita a casos extremos. Úsalo para: justificar el conjunto de regresión ante quien piensa que es un gasto de más.

- [Paper: "Fine-tuning Aligned Language Models Compromises Safety, Even When Users Do Not Intend To!", Qi et al., arXiv:2310.03693](https://arxiv.org/abs/2310.03693)
  El comportamiento de seguridad se degrada al hacer fine-tuning con datos benignos. Úsalo para: por qué el conjunto de regresión debe incluir casos de rechazo.

- [Code: lm-evaluation-harness, EleutherAI](https://github.com/EleutherAI/lm-evaluation-harness)
  Implementaciones estándar de benchmarks y los problemas de contaminación que documentan. Úsalo para: construir una eval, y para leer con escepticismo las puntuaciones publicadas.

### Serving

- [Docs: LoRA adapters, vLLM](https://docs.vllm.ai/en/latest/features/lora.html)
  Servir adapters en producción, incluido el enrutamiento multi-adapter. Úsalo para: la etapa 7. Comprueba los límites de rank máximo y de adapters máximos contra la versión instalada.

- [Paper: "S-LoRA: Serving Thousands of Concurrent LoRA Adapters", Sheng et al., arXiv:2311.03285](https://arxiv.org/abs/2311.03285)
  Cómo se agrupan en batch muchos adapters de forma eficiente contra un único base compartido. Úsalo para: entender por qué el serving multi-adapter es un problema resuelto y no una idea de investigación.

- [Blog: "LLM Inference Performance Engineering: Best Practices", Databricks](https://www.databricks.com/blog/llm-inference-performance-engineering-best-practices)
  Prefill frente a decode, y por qué está limitada cada fase. Úsalo para: la aritmética de costos de la etapa 7.

### La alternativa

- [Paper: "Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks", Lewis et al., arXiv:2005.11401](https://arxiv.org/abs/2005.11401)
  El planteamiento canónico del enfoque que normalmente debería preferirse cuando el problema es de conocimiento. Úsalo para: el argumento de la última lección, y para defender con credibilidad el caso contra el fine-tuning.

## Sabiduría (comunidades)

- [r/LocalLLaMA](https://www.reddit.com/r/LocalLLaMA/)
  La mayor concentración de personas que hacen fine-tuning en hardware de consumo, en todos los backends. Úsalo para: buscar lo que ya funcionó dentro de un presupuesto de memoria, qué folclore merece probarse y reportes de replicación de métodos nuevos. Lee el archivo; publicar es una práctica, no una fuente.

- [Hugging Face Forums](https://discuss.huggingface.co/)
  Con búsqueda y archivados, con autores de las bibliotecas presentes. Úsalo para: el comportamiento de PEFT, TRL y `transformers` que la documentación deja ambiguo.

- [EleutherAI Blog](https://blog.eleuther.ai/)
  Textos de un grupo que lee su propio campo con criterio crítico, incluidos los resultados negativos. Úsalo para: los juicios de las etapas 5 y 7 sobre si un resultado afirmado se generaliza. Su Discord es donde esto se discute primero, y deliberadamente no se lista: nada de lo que se dice allí se puede recuperar después.

- [MLX Discussions, ml-explore/mlx](https://github.com/ml-explore/mlx/discussions)
  Público, con búsqueda y respondido por los mantenedores. Úsalo para: leer si una operación dada ya está soportada en Apple Silicon, algo que normalmente ya se ha preguntado.

## Lagunas

- Ninguna fuente registra qué versiones de `torch`, PEFT, TRL y de las bibliotecas de cuantización funcionan realmente juntas en una versión de Python y una plataforma dadas. Esto bloquea una primera ejecución con más frecuencia que cualquier concepto, y cada entorno tiene que verificarse contra las notas de versión en lugar de darse por supuesto.
- La cobertura de los backends de hardware para las operaciones de 4 bits cambia de una versión a otra. Ningún documento es fiable aquí; el código fuente de la biblioteca es la única autoridad, y la afirmación de cualquier tutorial sobre requisitos de hardware debe tratarse como caducada.
- Todavía no hay una fuente de confianza sobre diseño de evaluación específico para la adaptación de tareas con modelos pequeños. Es el eslabón más débil de la etapa 6 y la parte más difícil de la misión. La literatura general de evaluación apunta a hacer benchmarking de foundation models, no a demostrar que un adapter estrecho ayudó.
- La mayor parte del consejo publicado sobre hiperparámetros de LoRA apunta a modelos de 7B y más. Poco aborda si se transfiere a la clase de 1B a 3B, que es donde empieza la mayoría de la gente.
- No se ha revisado ninguna replicación independiente de DoRA a la escala de la que disfrutan LoRA y QLoRA. Trata sus mejoras reportadas como algo que necesita medición local.
- No se ha elegido una fuente para la decodificación restringida, que la lección 27 recomienda como la respuesta correcta a los problemas de validez de esquema. Se nombra sin una referencia detrás.
