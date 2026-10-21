---
title: "Recursos"
description: "Fuentes de confianza sobre la destilación de conocimiento de LLM"
type: resources
---

# Recursos de la destilación

## Conocimiento

### Fundamentos

- [Paper: "Distilling the Knowledge in a Neural Network", Hinton, Vinyals and Dean, 2015](https://arxiv.org/abs/1503.02531)
  El paper que dio nombre al método: soft targets, temperatura, la corrección del gradiente por T al cuadrado y la pérdida combinada, con experimentos en MNIST y en voz. Úsalo para: la etapa 1, desde la fuente.
- [Paper: "A Survey on Knowledge Distillation of Large Language Models", Xu et al., 2024](https://arxiv.org/abs/2402.13116)
  Un mapa de la destilación de LLM organizado por lo que se obtiene del profesor y cómo se entrena con ello al estudiante. Úsalo para: situar un método en la familia más amplia antes de leer su propio paper.
- [Paper: "DistilBERT, a distilled version of BERT: smaller, faster, cheaper and lighter", Sanh et al., 2019](https://arxiv.org/abs/1910.01108)
  Una destilación completa de un transformer durante el preentrenamiento con una pérdida triple de términos de destilación, de modelado de lenguaje enmascarado y de coseno entre embeddings. Úsalo para: una receta completa con una ablación de cada término de la pérdida.

### Destilación de logits y a nivel de secuencia

- [Paper: "Sequence-Level Knowledge Distillation", Kim and Rush, 2016](https://arxiv.org/abs/1606.07947)
  Destilación a nivel de palabra frente a nivel de secuencia para traducción, y entrenamiento con la salida de beam search del profesor. Úsalo para: las etapas 2 y 3, el planteamiento original de ambos niveles.
- [Paper: "MiniLLM: On-Policy Distillation of Large Language Models", Gu et al., 2023](https://arxiv.org/abs/2306.08543)
  El argumento a favor de la KL inversa en la destilación generativa, optimizada con un método de policy gradient sobre muestras del estudiante. Úsalo para: KL directa frente a inversa, y una forma de destilación on-policy.
- [Paper: "Towards Cross-Tokenizer Distillation: the Universal Logit Distillation Loss for LLMs", Boizard et al., 2024](https://arxiv.org/abs/2402.12030)
  Una pérdida basada en transporte óptimo que compara vectores de probabilidad ordenados para que profesor y estudiante no tengan que compartir vocabulario. Úsalo para: qué hace y a qué renuncia la destilación entre tokenizers.
- [Paper: "Gemma 2: Improving Open Language Models at a Practical Size", Gemma Team, 2024](https://arxiv.org/abs/2408.00118)
  Entrenar los modelos de 2B y 9B con destilación de conocimiento de un profesor mayor en lugar de predicción del siguiente token. Úsalo para: la destilación como señal de preentrenamiento.
- [Paper: "Compact Language Models via Pruning and Knowledge Distillation", Muralidharan et al., 2024](https://arxiv.org/abs/2407.14679)
  Minitron: podar un modelo entrenado y reentrenarlo con destilación del original, con una pequeña fracción de los tokens de entrenamiento originales. Úsalo para: la destilación como paso de recuperación tras la poda.
- [Paper: "LLM Pruning and Distillation in Practice: The Minitron Approach", Sreenivas et al., 2024](https://arxiv.org/abs/2408.11796)
  La receta de Minitron aplicada a Llama 3.1 8B y Mistral NeMo 12B, incluida la corrección previa del profesor sobre los datos de destilación. Úsalo para: una segunda ejecución, más reciente, de la misma receta.

### Destilación con datos sintéticos

- [Paper: "Self-Instruct: Aligning Language Models with Self-Generated Instructions", Wang et al., 2022](https://arxiv.org/abs/2212.10560)
  Arrancar datos de instrucciones a partir de las propias generaciones de un modelo, con filtrado de casi duplicados y de ejemplos inválidos. Úsalo para: cómo se construye un conjunto de instrucciones generado.
- [Article: "Alpaca: A Strong, Replicable Instruction-Following Model", Stanford CRFM, 2023](https://crfm.stanford.edu/2023/03/13/alpaca.html)
  Fine-tuning de LLaMA 7B con 52K instrucciones generadas por text-davinci-003 con el método Self-Instruct, su costo, y sus límites declarados y restricciones de licencia. Úsalo para: la ejecución de imitación barata canónica.
- [Paper: "Distilling Step-by-Step! Outperforming Larger Language Models with Less Training Data and Smaller Model Sizes", Hsieh et al., 2023](https://arxiv.org/abs/2305.02301)
  Entrenar a un modelo pequeño para que produzca los rationales del profesor como segunda tarea junto a sus etiquetas. Úsalo para: lo que aportan los rationales frente a las etiquetas solas.
- [Paper: "Orca: Progressive Learning from Complex Explanation Traces of GPT-4", Mukherjee et al., 2023](https://arxiv.org/abs/2306.02707)
  Imitar trazas de explicación obtenidas con system prompts, con ChatGPT como profesor intermedio antes de GPT-4. Úsalo para: las trazas de explicación y un asistente del profesor a escala de LLM.
- [Paper: "Textbooks Are All You Need", Gunasekar et al., 2023](https://arxiv.org/abs/2306.11644)
  phi-1: un modelo de código pequeño entrenado con datos web filtrados y con libros de texto y ejercicios sintéticos generados por GPT-3.5. Úsalo para: calidad de los datos frente a volumen de datos.
- [Paper: "DeepSeek-R1: Incentivizing Reasoning Capability in LLMs via Reinforcement Learning", DeepSeek-AI, 2025](https://arxiv.org/abs/2501.12948)
  Destilar un modelo de razonamiento en modelos Qwen y Llama más pequeños mediante fine-tuning con sus muestras curadas, comparado con ejecutar RL directamente sobre el modelo pequeño (apéndice F.1). Úsalo para: datos sintéticos con rejection sampling, y la lección de post-training a la que enlaza este track.

### Destilación on-policy

- [Paper: "On-Policy Distillation of Language Models: Learning from Self-Generated Mistakes", Agarwal et al., 2023](https://arxiv.org/abs/2306.13649)
  Generalized knowledge distillation: entrenar con secuencias generadas por el estudiante con una divergencia a elegir y una mezcla de datos fijos y on-policy. Úsalo para: la etapa 5, desde la fuente.
- [Paper: "Qwen3 Technical Report", Qwen Team, 2025](https://arxiv.org/abs/2505.09388)
  Destilación de fuerte a débil de los modelos Qwen3 pequeños, con una etapa off-policy seguida de una etapa on-policy, comparada con RL sobre los mismos modelos. Úsalo para: la destilación on-policy en una familia de modelos de producción.
- [Documentation: "Generalized Knowledge Distillation Trainer", Hugging Face TRL](https://huggingface.co/docs/trl/main/en/gkd_trainer)
  La implementación de GKD en TRL y sus parámetros `lmbda`, `beta` y `seq_kd`. Úsalo para: ejecutar la destilación on-policy en lugar de leer sobre ella.
- [Documentation: "General Online Logit Distillation (GOLD) Trainer", Hugging Face TRL](https://huggingface.co/docs/trl/main/en/gold_trainer)
  El trainer de TRL que extiende GKD con la pérdida Universal Logit Distillation, alineando tramos de texto para que profesor y estudiante puedan usar tokenizers distintos. Úsalo para: lo que necesita una ejecución on-policy entre tokenizers.

### Qué hereda el estudiante

- [Paper: "Does Knowledge Distillation Really Work?", Stanton et al., 2021](https://arxiv.org/abs/2106.05945)
  Los estudiantes a menudo no logran igualar a sus profesores incluso cuando tienen capacidad para hacerlo, y una mejor generalización no exige una mejor fidelidad. Los experimentos son sobre todo de clasificación de imágenes, con una tarea de texto. Úsalo para: separar la fidelidad de la calidad en la tarea.
- [Paper: "The False Promise of Imitating Proprietary LLMs", Gudibande et al., 2023](https://arxiv.org/abs/2305.15717)
  Los modelos de imitación que los crowdworkers calificaron cerca de ChatGPT cerraron poca de la brecha en benchmarks específicos. Úsalo para: la brecha de imitación y cómo las valoraciones de preferencia humana la ocultaron.
- [Paper: "Improved Knowledge Distillation via Teacher Assistant", Mirzadeh et al., 2019](https://arxiv.org/abs/1902.03393)
  La calidad del estudiante cae cuando la distancia entre profesor y estudiante se vuelve demasiado grande, y un asistente de tamaño intermedio recupera parte de ella; las mejoras en sus experimentos de visión son pequeñas. Úsalo para: la brecha de capacidad.
- [Paper: "On the Efficacy of Knowledge Distillation", Cho and Hariharan, 2019](https://arxiv.org/abs/1910.01348)
  Los profesores más precisos no siempre producen mejores estudiantes, y detener antes el entrenamiento del profesor puede ayudar. Úsalo para: una segunda explicación de la brecha de capacidad.
- [Paper: "Subliminal Learning: Language models transmit behavioral traits via hidden signals in data", Cloud et al., 2025](https://arxiv.org/abs/2507.14805)
  Un estudiante entrenado con secuencias de números de un profesor adquirió los rasgos del profesor, cuando ambos compartían un base model. Úsalo para: lo que el filtrado de los datos no puede eliminar.

### Dimensionamiento

- [Paper: "Distillation Scaling Laws", Busbridge et al., 2025](https://arxiv.org/abs/2502.08606)
  Una ley de escalado de la calidad del estudiante en función del tamaño del estudiante, los tokens de destilación y la calidad del profesor, y de cuándo la destilación supera al entrenamiento supervisado del mismo estudiante. También informa de que la mejor temperatura de destilación fue 1 en su configuración (apéndice G.2). Úsalo para: la etapa 7 desde la fuente, y el contrapunto a una temperatura mayor que 1 en un LLM.

### Licencias y términos

- [Terms: "Terms of Use", OpenAI](https://openai.com/policies/row-terms-of-use/)
  Los términos para consumidores de OpenAI para usuarios fuera del EEE, Suiza y el Reino Unido, que enumeran entre las cosas que un usuario no puede hacer usar la salida para desarrollar modelos que compitan con OpenAI. Úsalo para: lo que dicen los términos de un proveedor alojado sobre entrenar con sus salidas.
- [License: "Llama 3.1 Community License Agreement", Meta](https://github.com/meta-llama/llama-models/blob/main/models/llama3_1/LICENSE)
  Una licencia de pesos abiertos que permite usar las salidas del modelo para mejorar otro modelo, con la condición de que el nombre del modelo resultante empiece por "Llama" cuando se distribuya. Úsalo para: lo que dice la licencia de un modelo abierto sobre entrenar con sus salidas.

## Lagunas

- La publicación de Thinking Machines sobre destilación on-policy se cita mucho por su comparación de costos con RL, pero su sitio rechaza las lecturas con scripts y dentro de la aplicación, así que aquí no se usa ninguna cifra suya. La etapa 5 se apoya en cambio en los papers de GKD, MiniLLM y Qwen3.
- Los términos de uso y las licencias cambian sin una versión que una lección pueda fijar. La lección 0013 los cita tal como se leyeron cuando se escribió este track; vuelve a comprobar la fuente antes de apoyarte en ella.
