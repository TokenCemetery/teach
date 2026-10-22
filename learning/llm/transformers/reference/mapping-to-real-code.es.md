---
title: "Correspondencia con el código real"
description: "Dónde vive cada pieza derivada en transformers o llama.cpp, las tres desviaciones estándar respecto del paper original, el byte-pair encoding y dónde se acopla un adapter de bajo rango"
type: reference
---

# Correspondencia con el código real

La etapa 5 comprimida para consulta. La [lección 12](../lessons/0012-reading-real-model-code.md) cubre traducir las derivaciones de este espacio de trabajo a la nomenclatura de `transformers` de Hugging Face y de llama.cpp; la [lección 13](../lessons/0013-tokenizers-and-low-rank-adapters.md) cubre derivar el byte-pair encoding y dónde se acopla un adapter de bajo rango a una matriz de pesos. Esta hoja reúne la correspondencia de nombres, las desviaciones estándar y las dos derivaciones, lado a lado.

## Nomenclatura en `transformers` de Hugging Face

| Nombre en código real | Derivado en | Qué es |
|---|---|---|
| `GPT2Attention` (o similar) | Lecciones 1-2 | Scaled dot-product attention, a menudo mediante una capa lineal QKV fusionada que se separa después, un detalle de eficiencia de multiplicación de matrices por lotes, no una operación distinta |
| Un buffer registrado de máscara triangular inferior | Lección 3 | Máscara causal, precalculada una vez porque la máscara depende solo de la longitud de la secuencia y no de los valores de entrada, y reutilizada o recortada en cada llamada |
| `wte` (word token embedding) | Lección 8 | La tabla de embedding de entrada |
| `wpe` (word position embedding) | Lección 4 | Codificación posicional, aquí comúnmente una tabla aprendida y no la fórmula sinusoidal |
| Una `ModuleList` de bloques, recorrida en un bucle for | Lección 7 | Bloques transformer apilados |
| `lm_head`, atado a los pesos de `wte` | Lección 8 | La proyección de salida, mediante weight tying |
| El script de entrenamiento o `Trainer`, no la clase del modelo | Lecciones 9-11 | Pérdida de entropía cruzada, `.backward()`, el paso del optimizador; la clase del modelo solo define el forward pass hasta los logits |

## Tres desviaciones estándar respecto del paper original

| Pieza | Paper original | Común en modelos de producción | Sigue siendo la misma lección de fondo |
|---|---|---|---|
| Embedding de posición | Fórmula sinusoidal | Una tabla aprendida, o embeddings rotatorios | La alternativa aprendida de la lección 4, o una variante posterior |
| Función de activación | ReLU | GELU (o SwiGLU) | El shape de expandir y luego contraer de la lección 6, con otra no linealidad |
| Colocación de la norm | Post-norm | Pre-norm | La alternativa pre-norm de la lección 5 |

Ninguna de estas cambia la arquitectura que derivó este espacio de trabajo; son variaciones estándar que se encuentran en casi toda implementación real, no un diseño distinto.

## La misma matemática, otra base de código: llama.cpp

llama.cpp (C, mediante la biblioteca de tensores `ggml`) construye un grafo de cómputo explícito mediante llamadas a funciones en lugar de clases `nn.Module` con un método `forward`. Calcula los mismos objetos matemáticos: atención, codificación posicional (comúnmente rotatoria), normalización (comúnmente RMSNorm, una variante simplificada de la layer norm) y un bloque feed-forward (comúnmente SwiGLU). La diferencia está por completo en cómo se construye y se ejecuta el grafo de cómputo, no en lo que calcula.

## Derivar el tokenizer: byte-pair encoding (BPE)

1. Representa el texto de entrenamiento como una secuencia de bytes en bruto o de caracteres, cada uno su propia entrada de vocabulario.
2. Cuenta cada par adyacente de símbolos en el corpus.
3. Fusiona el par más frecuente en un único símbolo nuevo, que se añade al vocabulario.
4. Repite hasta que el vocabulario alcance un tamaño objetivo elegido.

Ejemplo resuelto, corpus `"low low lower"`: el par `l, o` es frecuente y se fusiona en `lo`; la siguiente ronda encuentra `lo, w` y lo fusiona en `low`. Las palabras frecuentes se comprimen hacia un solo token; las palabras raras recurren a piezas más pequeñas y más frecuentes.

`vocab_size` es el número de símbolos iniciales más pasos de fusión con que se ejecutó el entrenamiento del tokenizer, fijado una vez que el entrenamiento termina; es exactamente lo que dimensiona la tabla de embedding de entrada y la capa de salida de la lección 8.

## Dónde se acopla un adapter de bajo rango

El mecanismo de adapter de `llm/finetuning`, `ΔW = BA` con `A` proyectando hacia abajo al rango `r` y `B` proyectando de vuelta hacia arriba, se acopla a una matriz de pesos concreta que derivó este espacio de trabajo, por ejemplo la proyección de query por head de la lección 2:

```text
Q_i = X (W_Q^i + (alpha / r) B_i A_i)
```

| Matriz | ¿Congelada? | ¿Recibe gradientes durante el entrenamiento del adapter? |
|---|---|---|
| `W_Q^i` | Sí, exactamente como en el preentrenamiento | No |
| `A_i`, `B_i` | No, recién añadidas, dimensionadas por el rango `r` | Sí |

Como la actualización es aditiva y lineal, exactamente igual que la proyección original, `W_Q^i + (alpha/r) B_i A_i` colapsa en una única matriz ordinaria después del entrenamiento. Nada del forward pass cambia para servir el resultado fusionado, ya que se enchufa en `Q_i = X W_Q^i` como una matriz de proyección ordinaria, sin cómputo añadido en la inferencia.

## Antes de leer o acoplarte al código de un modelo real

- [ ] Una capa lineal QKV fusionada que se separa después se reconoce como un detalle de eficiencia, no como una operación distinta de las proyecciones por head.
- [ ] El buffer de la máscara, si está precalculado, se entiende que depende solo de la longitud de la secuencia y no cambia el mecanismo de enmascarado en sí.
- [ ] Las elecciones de embedding de posición, de activación y de colocación de la norm se contrastan con las tres desviaciones estándar antes de tratarlas como una arquitectura distinta.
- [ ] El punto de acoplamiento de un adapter de bajo rango se nombra como una matriz de pesos concreta (qué proyección, en qué capa), y no solo como "el modelo".

## Fuentes

- [Repo: transformers, Hugging Face](https://github.com/huggingface/transformers)
- [Repo: nanoGPT, Karpathy](https://github.com/karpathy/nanoGPT)
- [Paper: "Neural Machine Translation of Rare Words with Subword Units", Sennrich, Haddow, and Birch, 2016](https://arxiv.org/abs/1508.07909)
- [Adapter](../../finetuning/GLOSSARY.md): el término canónico de `llm/finetuning` para el patrón de base congelada más pequeños pesos entrenables
- [Recursos](../RESOURCES.md)
