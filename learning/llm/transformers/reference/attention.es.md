---
title: "Atención"
description: "Scaled dot-product attention, multi-head attention y máscara causal, con los shapes de los tensores anotados en cada paso"
type: reference
---

# Atención: scaled dot-product, multi-head y máscara causal

La etapa 1 comprimida para consulta. La [lección 1](../lessons/0001-scaled-dot-product-attention.md) cubre la ecuación central; la [lección 2](../lessons/0002-multi-head-attention.md) cubre ejecutarla en subespacios paralelos; la [lección 3](../lessons/0003-causal-masking.md) cubre restringirla al pasado. Esta hoja reúne las ecuaciones y los shapes, lado a lado.

## Scaled dot-product attention

```text
Attention(Q, K, V) = softmax(QK^T / sqrt(d_k)) V
```

| Paso | Shape de entrada | Shape de salida | Nota |
|---|---|---|---|
| `Q`, `K`, `V` dadas | n/d | `[n, d_k]`, `[m, d_k]`, `[m, d_v]` | `n` queries, `m` pares key/value; `d_k` es la dimensión de key/query |
| `QK^T` | `[n, d_k] × [d_k, m]` | `[n, m]` | una puntuación de similitud por cada par query-key |
| `/ sqrt(d_k)` | `[n, m]` | `[n, m]` | contrarresta el crecimiento de la varianza con `d_k`, mantiene utilizable el gradiente del softmax |
| `softmax(...)` (por filas) | `[n, m]` | `[n, m]` | cada fila es ahora una distribución de probabilidad con suma 1 |
| `× V` | `[n, m] × [m, d_v]` | `[n, d_v]` | un vector de salida por query, una mezcla ponderada de los values |

La self-attention es el caso en que `Q`, `K`, `V` vienen todas de la misma secuencia (`n = m`), y cada posición atiende a todas las posiciones, incluida ella misma.

**Por qué el escalado.** La varianza del producto escalar crece con `d_k` y empuja al softmax hacia salidas casi one-hot donde su gradiente es casi plano y el entrenamiento se estanca. `/ sqrt(d_k)` contrarresta ese crecimiento sin importar lo grande que sea `d_k`.

## Multi-head attention

```text
Q_i = X W_Q^i,   K_i = X W_K^i,   V_i = X W_V^i          (per head i, i = 1..h)
head_i = Attention(Q_i, K_i, V_i)
MultiHead(Q, K, V) = Concat(head_1, ..., head_h) W_O
```

| Paso | Shape de entrada | Shape de salida | Nota |
|---|---|---|---|
| Entrada `X` | n/d | `[n, d_model]` | |
| Proyección por head (`W_Q^i`, `W_K^i`, `W_V^i`) | `[n, d_model] × [d_model, d_k]` | `[n, d_k]` por head, `d_k = d_model / h` | las proyecciones de cada head se aprenden de forma independiente |
| `head_i = Attention(Q_i, K_i, V_i)` | `[n, d_k]` cada una | `[n, d_k]` | la ecuación exacta de arriba, ejecutada una vez por head |
| `Concat(head_1, ..., head_h)` | `h × [n, d_k]` | `[n, d_model]` | coloca los heads uno junto a otro, todavía sin interacción entre heads |
| `× W_O` | `[n, d_model] × [d_model, d_model]` | `[n, d_model]` | el único paso que permite que se combine la información de distintos heads |

**La fórmula de escalado usa el `d_k` por head, no `d_model`.** Los productos escalares de cada head se suman sobre su propia dimensión, menor, así que esa es la varianza que tiene que contrarrestar el escalado, sin importar lo grande que sea el modelo completo.

**`W_O` no es opcional.** La concatenación por sí sola coloca las salidas una junto a otra sin interacción; `W_O` es el único lugar donde la información de distintos heads puede combinarse en una representación.

## Máscara causal

Se suma a las puntuaciones en bruto, antes del softmax:

```text
scores = QK^T / sqrt(d_k)
scores[i, j] += -inf   for every j > i     (a fixed lower-triangular pattern)
Attention(Q, K, V) = softmax(scores) V
```

| Elección | Por qué |
|---|---|
| Enmascarar antes del softmax, no después | Poner a cero un peso después de que el softmax ya corrió deja a los pesos restantes sumando menos de 1, lo que no es una distribución válida. Enmascarar la puntuación deja que la renormalización ocurra automáticamente dentro del mismo softmax |
| Un número negativo grande, no `0` | `exp(0) = 1`, un valor normal y no despreciable que sigue compitiendo por masa de probabilidad. Solo un número negativo lo bastante grande lleva `exp(...)` a un valor efectivamente nulo |
| La misma máscara para cada head y cada ejemplo de un batch | La restricción (la posición de query `i` puede atender a las posiciones de key `0..i`) es una propiedad de la tarea, no de ningún head concreto |

En la inferencia, un modelo genera el token `N` solo a partir de los tokens `1..N-1`; dejar que la posición `i` atienda a una posición posterior `j` durante el entrenamiento deja que el modelo use una respuesta que nunca tendrá en el momento de generar. En ese caso la pérdida de entrenamiento se ve bien, pero el modelo no aprende nada transferible.

## Antes de confiar en una implementación de la atención

- [ ] El divisor del escalado es el `d_k` por head (`d_model / h`), no el `d_model` completo.
- [ ] `W_O` se aplica después de concatenar los heads, no se omite.
- [ ] La máscara causal se suma a las puntuaciones en bruto antes del softmax, no se aplica a los pesos después.
- [ ] El valor de la máscara es un número negativo grande (o `-inf`), no `0`.
- [ ] El shape de salida es `[n, d_model]` sin importar el número de heads, ya que los heads solo cambian la dimensión intermedia por head.

## Fuentes

- [Paper: "Attention Is All You Need", Vaswani et al., 2017](https://arxiv.org/abs/1706.03762)
- [Article: "The Annotated Transformer", Harvard NLP](http://nlp.seas.harvard.edu/annotated-transformer/)
- [Article: "The Illustrated Transformer", Jay Alammar](https://jalammar.github.io/illustrated-transformer/)
- [Recursos](../RESOURCES.md)
