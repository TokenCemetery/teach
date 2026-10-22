---
title: "Glosario"
description: "Términos canónicos de los transformers"
type: glossary
---

# Glosario de transformers

Términos canónicos de la arquitectura transformer, derivados a partir de tensores en bruto y no de un módulo ya construido.

## Términos

**Cross-attention**:
Una subcapa de atención cuyas queries vienen de una secuencia (lo que el propio decoder ha generado hasta ahora) pero cuyas keys y values vienen de otra secuencia distinta (la salida de un encoder separado), de modo que el decoder puede consultar una entrada completa y ya codificada mientras genera. No existe en un modelo decoder-only, que no tiene un encoder separado ni una secuencia de entrada sobre la que atender.
_Evitar_: self-attention (una subcapa distinta cuyas queries, keys y values vienen todas de la misma secuencia; la cross-attention toma específicamente sus keys y values de una secuencia diferente a la de sus queries)

**Decodificación voraz (greedy decoding)**:
Elegir siempre, en cada paso de generación, el único token de mayor probabilidad de la distribución que predice el modelo. Es determinista y, aunque maximiza la misma cantidad que el modelo se entrenó para predecir bien, en la práctica produce un texto soso y extrañamente repetitivo.
_Evitar_: suponer que el objetivo de entrenamiento (la verosimilitud) es automáticamente el objetivo correcto de decodificación; son dos preguntas distintas con respuestas distintas

**Encoder-decoder**:
Una arquitectura (como la del paper original del transformer, o T5) que empareja un encoder bidireccional, sin máscara causal, que procesa una entrada completa, con un decoder que genera la salida de forma autorregresiva usando self-attention causal más cross-attention hacia la salida del encoder. Es adecuada para tareas con una separación limpia y fija entre entrada y salida, como la traducción.
_Evitar_: decoder-only (la arquitectura que construye este espacio de trabajo, sin encoder separado ni cross-attention, porque su único flujo hace a la vez de contexto de condicionamiento y de salida generada)

**Encoder-only**:
Una arquitectura (como BERT) que usa atención bidireccional, condicionando conjuntamente en el contexto de la izquierda y el de la derecha en cada capa, sin ninguna máscara causal. Construye una representación de una entrada completa y ya dada para tareas de comprensión (clasificación, extracción), en lugar de generar texto de forma autorregresiva, algo que su arquitectura no puede hacer.
_Evitar_: decoder-only (una arquitectura con máscara causal construida específicamente para generar un token cada vez; la atención bidireccional de un encoder-only nunca se entrenó para predecir a partir de un simple prefijo)

**FlashAttention**:
Una implementación exacta y consciente de la E/S de la scaled dot-product attention que divide el cálculo en bloques (tiling) para mantenerse en la memoria rápida del chip de la GPU (SRAM), sin materializar nunca la matriz completa de puntuaciones de atención, de tamaño cuadrático, en la memoria principal más lenta (HBM). Calcula exactamente el mismo resultado matemático que la ecuación de la lección 1; la aceleración viene por completo del acceso a memoria, no de aproximar nada.
_Evitar_: atención aproximada (una familia distinta de métodos que sacrifican calidad por velocidad; FlashAttention es exacta y obtiene su aceleración únicamente de la eficiencia de E/S)

**Gated linear unit (GLU)**:
El producto elemento a elemento de dos proyecciones lineales de la misma entrada, aplicando primero una no linealidad (originalmente sigmoide) a una de ellas. Esa proyección actúa como una puerta (gate) que escala la salida de la otra proyección elemento a elemento, en lugar de aplicar de manera uniforme una única no linealidad fija.
_Evitar_: SwiGLU (una variante concreta de GLU, con puerta de Swish/SiLU; "GLU" es la familia general, no este único miembro)

**Gradient accumulation**:
Ejecutar forward y backward pass sobre varios micro-batches más pequeños, uno tras otro, sin poner los gradientes a cero entre ellos, de modo que los gradientes de cada micro-batch se suman a los anteriores, y dar entonces un único paso del optimizador con el total combinado. Simula un batch size efectivo mayor del que cabría en memoria de una vez, sin cambiar lo que se calcula.
_Evitar_: aumentar el batch size real (el objetivo que la gradient accumulation logra sin necesitar que el batch mayor quepa nunca en memoria a la vez)

**Gradient norm clipping**:
Reescalar todo el vector de gradiente a la baja para que su norma global no supere un umbral elegido, dejando su dirección intacta, siempre que esa norma sería mayor. Protege frente a que un gradiente explosivo ocasional provoque una única actualización destructivamente grande.
_Evitar_: recortar el gradiente de cada parámetro por separado (distorsiona la dirección del gradiente combinado; el clipping por norma reescala todo el vector de manera uniforme)

**Grouped-query attention (GQA)**:
Una variante de atención que usa un número intermedio de heads de key/value, más de uno y menos que el número de heads de query, de modo que grupos de heads de query comparten cada uno un head de key/value. Es un punto medio entre las keys/values por head de la multi-head attention completa y el único head compartido de la multi-query attention.
_Evitar_: multi-query attention (MQA) (el caso más extremo, con un solo head de key/value compartido; GQA es la generalización que conserva más de uno)

**Inicialización de Xavier (Glorot)**:
Escalar la varianza inicial de los pesos de una capa según su fan-in y su fan-out (el número de entradas y de salidas que conecta), en lugar de usar una misma varianza fija para todas las capas, de modo que la varianza de las activaciones y de los gradientes se mantenga más o menos constante a lo largo de las capas de una red profunda, en vez de hacerse cada vez menor o mayor en cada una.
_Evitar_: una única varianza de inicialización fija para todas las capas sin importar su tamaño (el problema que la inicialización de Xavier se diseñó específicamente para resolver)

**KV cache**:
Los vectores key y value almacenados de cada posición anterior durante la generación autorregresiva, reutilizados en cada nuevo paso de generación en lugar de recalcularse desde cero. Su tamaño crece con el número de conjuntos distintos de heads de key/value que tiene un modelo, que es exactamente lo que reducen la grouped-query attention y la multi-query attention.
_Evitar_: recalcular las keys y los values en cada paso de generación (correcto pero derrochador; la caché existe precisamente para evitarlo)

**Learning rate warmup**:
Subir el learning rate de forma gradual (a menudo lineal) durante un número fijo de pasos iniciales de entrenamiento hasta que alcanza su valor objetivo, en lugar de aplicar toda la fuerza de inmediato. Resuelve que las estimaciones de momentos de Adam no son fiables en los primeros pasos, antes de haber visto suficientes gradientes para calibrarlas.
_Evitar_: aplicar el learning rate objetivo desde el primer paso (arriesga una actualización grande y mal dirigida antes de que las propias estadísticas del optimizador se hayan estabilizado)

**Mixture-of-experts (MoE)**:
Una capa que sustituye un único bloque feed-forward por varios bloques feed-forward expertos en paralelo más un router que selecciona qué experto o expertos procesan un token dado. Se activa de forma dispersa: el número total de parámetros crece con el número de expertos, pero el costo de cómputo por token se mantiene más o menos constante, porque solo se ejecutan los expertos seleccionados.
_Evitar_: suponer que más expertos significan más cómputo por token (solo cuenta para el costo de un token el cómputo del experto elegido por el router, sin importar cuántos expertos haya en total)

**Entrenamiento con precisión mixta (mixed precision training)**:
Almacenar pesos, activaciones y gradientes en media precisión durante la mayor parte del entrenamiento, en lugar de precisión completa (simple), con lo que el uso de memoria se reduce casi a la mitad. Requiere una copia maestra de los pesos en precisión completa (para conservar las actualizaciones pequeñas que de otro modo sufrirían underflow) y un escalado de la pérdida (para evitar que los gradientes pequeños sufran underflow hasta cero).
_Evitar_: entrenar solo en media precisión, sin copia maestra de los pesos ni escalado de la pérdida (arriesga perder en silencio, por underflow, las actualizaciones y los gradientes pequeños)

**Nucleus sampling (top-p)**:
Muestrear del conjunto más pequeño de tokens de mayor probabilidad cuya probabilidad acumulada supera un umbral `p`, un conjunto cuyo tamaño varía de un paso a otro según lo picuda o plana que sea la distribución. Contrasta con el truncamiento de tamaño fijo del top-k, que no puede adaptarse a esa variación.
_Evitar_: top-k sampling (un truncamiento de cantidad fija; el corte del nucleus sampling es, en cambio, un conjunto dinámico basado en la probabilidad acumulada)

**RMSNorm**:
Una normalización que divide un vector de activación por su raíz cuadrática media y aplica una escala aprendida, conservando la operación de reescalado de la layer norm pero eliminando por completo su paso de recentrado (la resta de la media). Es más barata que la layer norm, con un rendimiento comparable en las tareas en la práctica.
_Evitar_: layer norm (la normalización basada en media y varianza que RMSNorm simplifica; RMSNorm nunca calcula ni resta una media)

**Rotary position embedding (RoPE)**:
Un mecanismo posicional que rota los vectores de query y key proyectados un ángulo proporcional a su posición, en lugar de sumar de antemano un vector fijo al embedding. Como las rotaciones se componen sumando ángulos, la puntuación de atención resultante depende solo del desfase relativo entre dos posiciones, no de ninguna de las posiciones absolutas.
_Evitar_: codificación sinusoidal (un mecanismo distinto, aditivo, que se aplica al embedding antes de la proyección; RoPE es multiplicativo y se aplica a Q y K después de la proyección, dentro del propio cálculo de atención)

**Scaled dot-product attention**:
La operación `softmax(QK^T / sqrt(d_k)) V`: comparar una query con un conjunto de keys mediante producto escalar, escalar para contrarrestar el crecimiento de la varianza con `d_k`, convertir las puntuaciones en pesos con softmax y devolver la suma ponderada de los values correspondientes.
_Evitar_: mecanismo de atención (demasiado vago cuando se quiere decir esta forma concreta)

**Self-attention**:
Scaled dot-product attention en la que las queries, las keys y los values vienen todos de la misma secuencia de entrada, de modo que cada posición atiende a todas las posiciones de esa misma secuencia, incluida ella misma.
_Evitar_: intra-attention

**SwiGLU**:
La variante de GLU con puerta de activación Swish (SiLU), usada en la subcapa feed-forward de la mayoría de los modelos abiertos actuales en lugar de una no linealidad simple ReLU o GELU. Usa tres matrices de pesos (dos proyecciones de expansión y una de contracción) en lugar de las dos de un bloque feed-forward simple.
_Evitar_: GELU, ReLU (las no linealidades fijas, de una sola proyección, que el diseño de dos proyecciones con puerta de SwiGLU sustituye en los modelos actuales)

**Temperatura**:
Un valor que divide los logits antes del softmax que produce una distribución del siguiente token durante la generación. Por debajo de 1 afila la distribución hacia el comportamiento de la decodificación voraz; por encima de 1 la aplana. Cambia lo picuda que es la distribución sin decidir qué tokens son elegibles para muestrearse.
_Evitar_: top-k, top-p (la temperatura solo reescala la agudeza de las probabilidades; decidir el conjunto elegible es un paso aparte, posterior, que realizan esos métodos)

**Top-k sampling**:
Truncar una distribución del siguiente token a sus `k` tokens de mayor probabilidad, descartar el resto y muestrear de ese conjunto renormalizado de tamaño fijo. A diferencia del nucleus sampling (top-p), el tamaño del conjunto elegible nunca se adapta a lo picuda o plana que sea realmente la distribución en un paso dado.
_Evitar_: nucleus sampling (top-p) (una alternativa de tamaño dinámico; la cantidad de corte del top-k es fija, sin importar la forma real de la distribución)
