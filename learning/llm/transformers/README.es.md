---
title: "Transformers"
description: "Construye la atención desde cero, para que la arquitectura deje de ser una caja negra detrás del script de entrenamiento"
type: topic
---

# Aprendizaje: transformers

Ser capaz de implementar el forward pass de un transformer y su bucle de entrenamiento a partir de tensores en bruto, y de leer o modificar código real de modelos sin que la arquitectura sea una caja negra detrás de él.

**Última lección:** [23. Revisar un cambio en el código de un modelo](lessons/0023-reviewing-a-change-to-model-code.md)

## Cómo se ve el éxito

- Implementar scaled dot-product attention, multi-head attention y un bloque transformer completo a partir de tensores en bruto, igualando la salida de una implementación de referencia.
- Escribir desde cero el bucle de entrenamiento que rodea a ese bloque y explicar qué le hace cada pieza (pérdida, backward pass, paso del optimizador) a los pesos.
- Leer el código de un modelo real (una biblioteca como `transformers` o `llama.cpp`) y señalar dónde vive cada pieza derivada.
- Revisar el cambio de otra persona en el código de un modelo y nombrar con precisión qué rompe o cuánto cuesta (un error de shape que solo aflora dos capas más abajo, una mejora de velocidad declarada sin una salida que la respalde, una afirmación de arquitectura que no sobrevive a releer las ecuaciones reales del paper), en lugar de confiar en la descripción de la pull request.

## Restricciones

- Se asume soltura con Python y con las operaciones básicas de tensores de PyTorch, y la multiplicación de matrices como la única matemática que se da por sabida; no se requiere experiencia previa en deep learning.
- Implementación en PyTorch, con operaciones de tensores en bruto en lugar de `nn.Transformer` u otros módulos de atención ya construidos; se conservan autograd y el soporte de GPU, y solo la arquitectura en sí se construye a mano.

## Fuera de alcance

- Variantes de optimizador y de scheduler más allá del bucle básico necesario para ver entrenar el bloque, y el entrenamiento distribuido: consulta [`llm/pretraining`](../../llm/pretraining/), que retoma el tema cuando este bucle tiene que correr en muchas GPU.
- La maquinaria de bajo rango y de adapters construida sobre el bloque: consulta [`llm/finetuning`](../../llm/finetuning/) para ese límite. Este espacio de trabajo deriva lo que aquel nombra de pasada (los tokenizers en su lección 0003, la idea de bajo rango en su lección 0008) en lugar de repetirlo.

## El arco

Doce etapas, desde una ecuación hasta leer código de un modelo real y generar a partir de él a cualquier escala. Una etapa abarca varias lecciones y los límites son difusos; lo que da una etapa por terminada es la capacidad, no el número de lecciones.

| Etapa | Lecciones | Cubre | Terminada cuando |
|---|---|---|---|
| 1. Atención | 0001 a 0003 | Scaled dot-product attention, multi-head attention, máscara causal | La multi-head attention está implementada a partir de tensores en bruto e iguala a una implementación de referencia |
| 2. El bloque transformer | 0004 a 0006 | Codificación posicional, layer norm y conexiones residuales, el bloque feed-forward | Un bloque transformer completo está implementado a partir de tensores en bruto |
| 3. El modelo completo | 0007 a 0008 | Apilar bloques, capas de embedding y de salida, weight tying | Un forward pass completo iguala la salida de una implementación de referencia |
| 4. El bucle de entrenamiento | 0009 a 0011 | Pérdida de entropía cruzada sobre el vocabulario, el backward pass, el paso del optimizador AdamW | El modelo entrena desde cero y la pérdida baja como se espera |
| 5. Leer código real de modelos | 0012 a 0013 | Asignar cada pieza derivada a una biblioteca real (`transformers` o `llama.cpp`), tokenizers y adapters de bajo rango nombrados de pasada | Puedes señalar dónde vive cada pieza derivada en código real de modelos |
| 6. Codificación posicional y normalización modernas | 0014 a 0015 | Rotary position embeddings, RMSNorm | Puedes derivar la propiedad de posición relativa de RoPE y explicar qué elimina RMSNorm de la layer norm |
| 7. Variantes modernas del feed-forward y de la atención | 0016 a 0017 | SwiGLU y el bloque feed-forward con puerta, grouped-query attention y multi-query attention, KV caching | Puedes derivar un bloque feed-forward con puerta y explicar por qué menos heads de KV cambian algo de calidad por tamaño de caché |
| 8. Generación y muestreo | 0018 | Decodificación voraz, temperatura, muestreo top-k y top-p, ejecutar el modelo hacia delante para producir texto | Puedes generar texto con el modelo construido a mano y explicar por qué la decodificación voraz degenera |
| 9. Los detalles prácticos del bucle de entrenamiento | 0019 a 0020 | Inicialización de Xavier, warmup y decaimiento del learning rate, gradient clipping, precisión mixta, gradient accumulation | Puedes explicar de qué protege cada detalle práctico y añadirlos a un bucle de entrenamiento que funciona |
| 10. Arquitecturas encoder-decoder y encoder-only | 0021 | El encoder bidireccional de BERT, el encoder-decoder de T5 con cross-attention, situar el modelo decoder-only de este espacio de trabajo | Puedes explicar por qué cada arquitectura usa o no una máscara causal, y dónde encaja la cross-attention |
| 11. Mixture-of-experts y FlashAttention | 0022 | Enrutamiento disperso de MoE, el tiling consciente de la E/S de FlashAttention | Puedes explicar cómo MoE desacopla los parámetros del cómputo por token, y por qué FlashAttention es exacta y no aproximada |
| 12. Criterio | 0023 | Revisar los cambios de otra persona en el código de un modelo, comprobar shapes y la exactitud de la salida, resolver afirmaciones en disputa desde la fuente primaria | Se confía en ti para revisar cambios en la arquitectura del modelo y en el bucle de entrenamiento, y para explicar qué cuesta o arriesga un cambio en lugar de aceptar la descripción |

## Lecciones

Recórrelas en orden.

| # | Lección | Enseña |
|---|---|---|
| [0001](lessons/0001-scaled-dot-product-attention.md) | Scaled Dot-Product Attention | La única ecuación alrededor de la cual se construye el resto de la arquitectura |
| [0002](lessons/0002-multi-head-attention.md) | Multi-Head Attention | Por qué la atención corre a la vez en varios subespacios más pequeños en lugar de uno solo a dimensión completa |
| [0003](lessons/0003-causal-masking.md) | Máscara causal | Por qué una posición de query no debe atender a posiciones futuras, y por qué la máscara se aplica antes del softmax y no después |
| [0004](lessons/0004-positional-encoding.md) | Codificación posicional | Por qué la atención, por sí sola, no distingue el orden, y cómo la codificación sinusoidal da a cada posición una firma distinguible |
| [0005](lessons/0005-layer-norm-and-residuals.md) | Layer norm y conexiones residuales | Por qué apilar muchos bloques transformer exige un camino limpio para el gradiente y rangos de activación estables, y cómo los residuales y la layer norm aportan cada uno uno de ellos |
| [0006](lessons/0006-feed-forward-block.md) | El bloque feed-forward por posición | Qué añade la segunda subcapa del bloque transformer además de la atención, y por qué nunca mezcla información entre posiciones |
| [0007](lessons/0007-stacking-blocks.md) | Apilar bloques transformer | Por qué cada bloque conserva el mismo shape, por qué la profundidad no es compartir pesos, y por qué la maquinaria residual de la lección 5 importa más cuando se apilan muchos bloques |
| [0008](lessons/0008-embedding-output-and-weight-tying.md) | Capas de embedding y de salida, weight tying | Cómo entran los tokens al espacio vectorial del transformer y cómo salen de él, y por qué las dos capas que lo hacen pueden compartir una sola matriz |
| [0009](lessons/0009-cross-entropy-loss.md) | Pérdida de entropía cruzada sobre el vocabulario | Cómo los logits se convierten en un único número entrenable, y por qué la pérdida es el logaritmo negativo de la probabilidad del siguiente token real |
| [0010](lessons/0010-backward-pass-and-autograd.md) | El backward pass y autograd | Cómo la regla de la cadena, automatizada sobre un grafo de cómputo registrado, convierte una pérdida escalar en un gradiente para cada peso |
| [0011](lessons/0011-adamw-optimizer.md) | El paso del optimizador AdamW | Qué añaden el momentum y el escalado adaptativo de Adam al descenso de gradiente simple, y por qué AdamW desacopla el weight decay de la actualización del gradiente |
| [0012](lessons/0012-reading-real-model-code.md) | Leer código real de modelos | Dónde vive cada pieza derivada en una biblioteca de modelos de producción, y las desviaciones pequeñas y comunes respecto del paper original que conviene reconocer en lugar de dejar que te confundan |
| [0013](lessons/0013-tokenizers-and-low-rank-adapters.md) | Tokenizers y adapters de bajo rango | Derivar el byte-pair encoding, y dónde se acopla realmente un adapter de bajo rango a una matriz de pesos que este espacio de trabajo construyó desde cero |
| [0014](lessons/0014-rotary-position-embeddings.md) | Rotary Position Embeddings | La codificación sinusoidal suma un vector fijo al embedding antes de que la atención corra siquiera; RoPE, en cambio, rota Q y K mismas, y ese único cambio es lo que hace que el producto escalar entre dos vectores rotados dependa solo de su distancia relativa |
| [0015](lessons/0015-rmsnorm.md) | RMSNorm | LayerNorm hace dos cosas, recentrar y reescalar, y RMSNorm existe porque la mitad del recentrado resulta prescindible, lo que deja una normalización más barata que los modelos actuales usan dentro de la rama pre-norm que la lección 5 ya derivó |
| [0016](lessons/0016-swiglu-and-the-gated-feed-forward.md) | SwiGLU y el bloque feed-forward con puerta | El bloque feed-forward de la lección 6 se expande, aplica una no linealidad y se contrae; una variante con puerta calcula dos proyecciones en lugar de una y las multiplica entre sí, de modo que la red aprende cuánto de su propio cómputo dejar pasar |
| [0017](lessons/0017-grouped-query-attention-and-kv-caching.md) | Grouped-Query Attention y KV caching | La generación autorregresiva hace que la atención recalcule keys y values que ya tiene, y cuando guardarlos en caché se vuelve la solución obvia, el tamaño de la propia caché es lo que hace que merezca la pena cambiar un poco de calidad por menos heads de key/value |
| [0018](lessons/0018-generation-and-sampling.md) | Generación y muestreo | El modelo que este espacio de trabajo construyó y entrenó nunca ha producido texto, porque entrenar y generar le hacen dos preguntas distintas, y tomar siempre el único siguiente token más probable resulta una peor respuesta a la segunda pregunta que una cantidad bien elegida de aleatoriedad |
| [0019](lessons/0019-initialization-warmup-and-gradient-clipping.md) | Inicialización, warmup y gradient clipping | Un modelo así de profundo puede fallar antes de empezar a entrenar si sus pesos iniciales están mal escalados, y el paso de AdamW que derivó la lección 11 todavía necesita dos salvaguardas más, un arranque lento y un techo duro para el gradiente, para sobrevivir de verdad a un entrenamiento real |
| [0020](lessons/0020-mixed-precision-and-gradient-accumulation.md) | Precisión mixta y gradient accumulation | Ambas técnicas existen para meter una ejecución de entrenamiento efectiva mayor en un hardware más pequeño de lo que la ejecución parece necesitar, una encogiendo la huella de cada número y la otra simulando un batch mayor del que cabría jamás en memoria de una vez |
| [0021](lessons/0021-encoder-decoder-and-encoder-only-architectures.md) | Arquitecturas encoder-decoder y encoder-only | Este espacio de trabajo construyó un solo flujo con máscara causal porque solo necesitaba hacer una cosa, generar el siguiente token, y las otras dos formas de arquitectura existen porque BERT y el modelo original de traducción necesitaban en cambio una garantía estructuralmente distinta |
| [0022](lessons/0022-mixture-of-experts-and-flashattention.md) | Mixture-of-Experts y FlashAttention | MoE hace crecer los parámetros totales de un modelo sin hacer crecer lo que cualquier token paga por ser procesado, y FlashAttention calcula la misma ecuación exacta de la lección 1 más rápido reescribiendo cómo toca la memoria, no lo que calcula |
| [0023](lessons/0023-reviewing-a-change-to-model-code.md) | Revisar un cambio en el código de un modelo | Revisar el cambio de otra persona en el código de un modelo y nombrar qué rompe o cuánto cuesta, sin confiar en la descripción |

## Referencia

- [Glosario](GLOSSARY.md): términos canónicos de este tema
- [Recursos](RESOURCES.md): fuentes de confianza
- [Atención](reference/attention.md): scaled dot-product attention, multi-head attention y máscara causal, con los shapes de los tensores anotados en cada paso
- [El bloque transformer](reference/the-transformer-block.md): codificación posicional, layer norm y residuales, el bloque feed-forward, apilado y weight tying
- [El bucle de entrenamiento](reference/the-training-loop.md): pérdida de entropía cruzada, el backward pass y autograd, y el paso del optimizador AdamW, con los ejemplos resueltos de regla de la cadena y de descenso de gradiente
- [Correspondencia con el código real](reference/mapping-to-real-code.md): la correspondencia de nombres entre transformers y llama.cpp, las tres desviaciones estándar respecto del paper original, el byte-pair encoding y dónde se acopla un adapter de bajo rango

## Cómo funciona

Cada lección es corta y autocontenida. Las claves de respuesta están plegadas: primero recuerda, luego ábrelas. Las prácticas en el mundo real importan más que la lectura, y espaciarlas es el punto. Todo lo que siga sin estar claro al final de una lección merece rastrearse hasta su fuente primaria antes de seguir.
