---
title: "Recursos"
description: "Fuentes de confianza sobre transformers"
type: resources
---

# Recursos de transformers

## Conocimiento

- [Paper: "Attention Is All You Need", Vaswani et al., 2017](https://arxiv.org/abs/1706.03762)
  El paper original del transformer: scaled dot-product attention, multi-head attention y el bloque encoder-decoder completo que este espacio de trabajo deriva a partir de tensores en bruto. Úsalo para: la definición primaria de cada pieza que implementa este espacio de trabajo.
- [Article: "The Illustrated Transformer", Jay Alammar](https://jalammar.github.io/illustrated-transformer/)
  Un recorrido visual, que prioriza la intuición, por la atención y el bloque transformer, pensado para leerse antes que la notación del paper. Úsalo para: un modelo mental operativo antes de implementar nada.
- [Article: "The Annotated Transformer", Harvard NLP](http://nlp.seas.harvard.edu/annotated-transformer/)
  Una implementación en PyTorch del paper, línea por línea y a partir de operaciones de tensores en bruto, emparejada directamente con las ecuaciones que las producen. Úsalo para: contrastar una implementación hecha desde cero con una de referencia, línea por línea.
- [Repo: nanoGPT, Karpathy](https://github.com/karpathy/nanoGPT)
  Una implementación mínima y legible en PyTorch de un transformer de estilo GPT, más su bucle de entrenamiento, lo bastante pequeña para leerla entera. Úsalo para: la mitad de la misión que es el bucle de entrenamiento, una vez que el bloque en sí funciona.
- [Video: "Let's build GPT: from scratch, in code, spelled out", Karpathy](https://www.youtube.com/watch?v=kCc8FmEb1nY)
  Construye en pantalla, paso a paso, la atención y un bucle de entrenamiento de GPT a partir de tensores en bruto, derivando cada pieza en lugar de presentarla terminada. Úsalo para: ver cómo ocurre la derivación antes de escribir tú mismo el código, o a la vez.
- [Docs: "Autograd mechanics", PyTorch](https://pytorch.org/docs/stable/notes/autograd.html)
  La explicación oficial de cómo calcula realmente autograd de PyTorch los gradientes a través de un grafo de cómputo. Úsalo para: entender qué le hace el backward pass a los pesos, y no solo llamar a `.backward()`.
- [Repo: transformers, Hugging Face](https://github.com/huggingface/transformers)
  Una biblioteca real de modelos de producción, útil una vez que existen las piezas hechas desde cero. Úsalo para: localizar la atención, la proyección multi-head y el bloque transformer dentro de código escrito para producción y no para enseñar.
- [Paper: "Layer Normalization", Ba, Kiros, and Hinton, 2016](https://arxiv.org/abs/1607.06450)
  Introduce la layer normalization: normalizar las activaciones de cada ejemplo a lo largo de la dimensión de features, con independencia del batch size, a diferencia de la batch normalization. Úsalo para: entender qué calcula realmente la layer norm y por qué encaja con secuencias de longitud variable y batch sizes pequeños.
- [Paper: "On Layer Normalization in the Transformer Architecture", Xiong et al., 2020](https://arxiv.org/abs/2002.04745)
  Compara colocar la layer norm después de la suma residual (la elección del paper original, post-norm) con colocarla antes de cada subcapa, dentro de la rama residual (pre-norm), y muestra por qué la pre-norm entrena con más estabilidad a mayor profundidad. Úsalo para: entender por qué la mayoría de los grandes modelos actuales usan pre-norm aunque el paper original del transformer usara post-norm.
- [Paper: "Using the Output Embedding to Improve Language Models", Press and Wolf, 2017](https://arxiv.org/abs/1608.05859)
  Defiende atar las matrices de pesos del embedding de entrada y de la proyección de salida, ya que ambas relacionan un token con la misma representación subyacente, con lo que se recorta una gran fracción de los parámetros de un modelo de vocabulario grande. Úsalo para: entender el weight tying como una decisión de diseño deliberada, y no solo como un truco para ahorrar parámetros.
- [Docs: "torch.nn.functional.cross_entropy", PyTorch](https://pytorch.org/docs/stable/generated/torch.nn.functional.cross_entropy.html)
  La documentación oficial de la operación fusionada de softmax más log-verosimilitud negativa, que toma directamente logits en bruto por estabilidad numérica en lugar de exigir antes un paso de softmax aparte. Úsalo para: cómo se calcula realmente en la práctica la pérdida de entropía cruzada, y no solo su fórmula.
- [Paper: "Adam: A Method for Stochastic Optimization", Kingma and Ba, 2015](https://arxiv.org/abs/1412.6980)
  Introduce el momentum de Adam (primer momento) y el escalado adaptativo por parámetro (segundo momento) sobre el descenso de gradiente simple, con corrección de sesgo para ambos. Úsalo para: entender qué calcula la regla de actualización de Adam y por qué, antes de la corrección del weight decay de AdamW.
- [Paper: "Decoupled Weight Decay Regularization", Loshchilov and Hutter, 2019](https://arxiv.org/abs/1711.05101)
  Identifica por qué incorporar el weight decay al gradiente en el Adam original interactúa mal con su escalado adaptativo, y lo corrige aplicando el decay directamente a los pesos. Úsalo para: por qué AdamW, y no Adam simple, es el optimizador estándar para entrenar transformers.
- [Paper: "Neural Machine Translation of Rare Words with Subword Units", Sennrich, Haddow, and Birch, 2016](https://arxiv.org/abs/1508.07909)
  Introduce el byte-pair encoding para la tokenización en subpalabras: fusionar iterativamente el par de símbolos adyacentes más frecuente para construir un vocabulario desde los bytes en bruto hacia arriba. Úsalo para: derivar el mecanismo del tokenizer que `llm/finetuning` nombra de pasada en lugar de repetirlo.
- [Paper: "RoFormer: Enhanced Transformer with Rotary Position Embedding", Su et al., 2021](https://arxiv.org/abs/2104.09864)
  Introduce RoPE: rotar los vectores de query y key proyectados un ángulo proporcional a la posición, lo que produce una puntuación de atención que depende solo del desfase relativo. Úsalo para: el mecanismo que casi todos los modelos abiertos actuales usan en lugar de la codificación posicional sinusoidal o aprendida.
- [Paper: "Root Mean Square Layer Normalization", Zhang and Sennrich, 2019](https://arxiv.org/abs/1910.07467)
  Introduce RMSNorm, con la hipótesis de que la operación de recentrado (resta de la media) de la layer norm es prescindible y que el reescalado por sí solo explica la mayor parte de su beneficio. Úsalo para: la normalización más barata que los modelos actuales colocan dentro de la rama pre-norm que deriva la lección 5.
- [Paper: "GLU Variants Improve Transformer", Shazeer, 2020](https://arxiv.org/abs/2002.05202)
  Prueba variantes de gated linear unit (incluida SwiGLU, con puerta de Swish) en la subcapa feed-forward del transformer, y encuentra que algunas superan a la ReLU o la GELU que se usan habitualmente. Úsalo para: el diseño con puerta y dos proyecciones de expansión que sustituye en los modelos actuales al bloque feed-forward de una sola proyección de la lección 6.
- [Paper: "GQA: Training Generalized Multi-Query Transformer Models from Multi-Head Checkpoints", Ainslie et al., 2023](https://arxiv.org/abs/2305.13245)
  Introduce la grouped-query attention como punto medio entre la multi-head attention completa y el único head de key/value compartido de la multi-query attention, además de una receta barata para reentrenar un checkpoint multi-head existente y convertirlo en uno de ellas. Úsalo para: por qué menos heads de key/value cambian un poco de calidad por una KV cache mucho más pequeña y una inferencia más rápida.
- [Paper: "The Curious Case of Neural Text Degeneration", Holtzman et al., 2019](https://arxiv.org/abs/1904.09751)
  Documenta por qué maximizar la verosimilitud en el momento de decodificar (decodificación voraz) produce texto soso y repetitivo aunque la verosimilitud sea un buen objetivo de entrenamiento, e introduce el nucleus sampling (top-p) como remedio. Úsalo para: la razón precisa por la que un corte dinámico, basado en la probabilidad acumulada, supera tanto a la decodificación voraz como a una cantidad fija de top-k.
- [Paper: "On the difficulty of training Recurrent Neural Networks", Pascanu, Mikolov, and Bengio, 2013](https://arxiv.org/abs/1211.5063)
  Analiza los problemas de gradientes que se desvanecen y que explotan, y propone el gradient norm clipping como remedio para el segundo. Úsalo para: por qué el clipping reescala todo el vector de gradiente según su norma en lugar de acotar por separado el gradiente de cada parámetro.
- [Paper: "Mixed Precision Training", Micikevicius et al., 2018](https://arxiv.org/abs/1710.03740)
  Introduce el entrenamiento en media precisión con una copia maestra de los pesos en precisión completa y un escalado de la pérdida para contrarrestar el rango numérico limitado de la media precisión, lo que reduce el uso de memoria casi a la mitad. Úsalo para: exactamente qué hay que añadir al entrenamiento simple en media precisión para que las actualizaciones y los gradientes pequeños no sufran underflow hasta cero.
- [Paper: "BERT: Pre-training of Deep Bidirectional Transformers for Language Understanding", Devlin et al., 2018](https://arxiv.org/abs/1810.04805)
  Introduce la arquitectura encoder-only: atención bidireccional que condiciona conjuntamente en el contexto de la izquierda y el de la derecha en cada capa, sin máscara causal. Úsalo para: por qué un modelo encoder-only construye una representación de una entrada completa en lugar de generar texto de forma autorregresiva, y no puede hacer lo que hace el modelo decoder-only de este espacio de trabajo.
- [Paper: "Exploring the Limits of Transfer Learning with a Unified Text-to-Text Transformer" (T5), Raffel et al., 2019](https://arxiv.org/abs/1910.10683)
  Reformula una amplia gama de tareas de NLP en un único formato coherente de texto a texto, con encoder-decoder. Úsalo para: la subcapa de cross-attention de la forma encoder-decoder, y por qué encaja con una tarea con una separación limpia y fija entre entrada y salida.
- [Paper: "FlashAttention: Fast and Memory-Efficient Exact Attention with IO-Awareness", Dao et al., 2022](https://arxiv.org/abs/2205.14135)
  Diagnostica la lentitud de la atención estándar en secuencias largas como un problema de E/S (lecturas y escrituras de memoria entre HBM y SRAM), no de cómputo, e introduce un algoritmo exacto, por bloques, que evita materializar la matriz completa de puntuaciones. Úsalo para: por qué una implementación real de la atención tiene una estructura distinta de la versión de la lección 1 y calcula, aun así, el mismo resultado.
- [Paper: "Switch Transformers: Scaling to Trillion Parameter Models with Simple and Efficient Sparsity", Fedus, Zoph, and Shazeer, 2021](https://arxiv.org/abs/2101.03961)
  Introduce un esquema simplificado de enrutamiento MoE con un experto por token, que desacopla el número total de parámetros del costo de cómputo por token. Úsalo para: el intercambio concreto que hacen los modelos de activación dispersa, y por qué simplificar el enrutamiento a un experto resolvió inestabilidades con las que topaban diseños MoE más complejos.

## Lagunas

- Todavía no hay una fuente sobre el calendario exacto de learning rate con warmup seguido de decaimiento; la lección 19 lo deriva de la forma que indican los propios detalles de entrenamiento del paper original del transformer (warmup lineal, y luego decaimiento proporcional a la inversa de la raíz cuadrada del número de paso), pero no se pudo obtener con las herramientas disponibles en esta sesión un extracto directo y recién verificado de esa sección (la página de resumen del paper no incluye la sección de detalles de entrenamiento, y otras fuentes en PDF no se extrajeron como texto legible). Vuelve a revisarlo si aparece una fuente más limpia.
