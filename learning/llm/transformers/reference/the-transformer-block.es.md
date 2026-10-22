---
title: "El bloque transformer"
description: "Codificación posicional, layer norm y conexiones residuales, el bloque feed-forward, y el apilado de bloques en el modelo completo con embedding, salida y weight tying"
type: reference
---

# El bloque transformer: de un bloque al modelo completo

Las etapas 2 y 3 comprimidas para consulta. La [lección 4](../lessons/0004-positional-encoding.md) cubre inyectar la posición en los embeddings; la [lección 5](../lessons/0005-layer-norm-and-residuals.md) cubre los residuales y la layer norm; la [lección 6](../lessons/0006-feed-forward-block.md) cubre la subcapa feed-forward; la [lección 7](../lessons/0007-stacking-blocks.md) cubre apilar bloques en profundidad; la [lección 8](../lessons/0008-embedding-output-and-weight-tying.md) cubre entrar y salir del espacio vectorial del modelo. Esta hoja reúne las fórmulas, los shapes y las elecciones, lado a lado.

## Codificación posicional

La atención no tiene por sí sola ninguna noción de orden; intercambiar dos posiciones solo reetiqueta la salida. La posición tiene que quedar incorporada en los propios embeddings, antes de que la atención corra siquiera.

```text
PE(pos, 2i)   = sin(pos / 10000^(2i / d_model))
PE(pos, 2i+1) = cos(pos / 10000^(2i / d_model))
```

| Esquema | Generaliza a longitudes de secuencia no vistas | Implementación |
|---|---|---|
| Sinusoidal (fórmula fija) | Sí, la fórmula se evalúa en cualquier posición | Sin parámetros que aprender |
| Embedding posicional aprendido | No, solo tiene filas para las posiciones vistas en el entrenamiento | Una tabla de búsqueda, entrenada como cualquier otro parámetro |

## Conexiones residuales y layer norm

```text
post-norm: LayerNorm(x + Sublayer(x))
pre-norm:  x + Sublayer(LayerNorm(x))
```

| Pieza | Resuelve | Independiente de |
|---|---|---|
| Residual (`+ x`) | Que el gradiente se encoja o explote a lo largo de una pila profunda, dándole un camino identidad directo en cada capa | La transformación propia de la subcapa |
| Layer norm | La deriva de la escala de las activaciones de una capa a otra, normalizando el vector de features propio de cada token (media y varianza a lo largo de las features, y luego una escala y un desplazamiento aprendidos) | El batch size, a diferencia de la batch norm, que necesita estadísticas de muchos ejemplos |

**Pre-norm sobre post-norm.** La pre-norm mantiene el propio camino residual completamente sin normalizar de punta a punta, una conexión identidad sin obstáculos; la post-norm normaliza la suma residual en cada capa, lo que perturba ese camino. La pre-norm es lo que usan la mayoría de los grandes modelos actuales, a pesar de que el paper original eligiera post-norm.

## El bloque feed-forward

```text
FFN(x) = max(0, x W1 + b1) W2 + b2
```

| Paso | Shape de entrada | Shape de salida | Nota |
|---|---|---|---|
| `x W1 + b1`, no linealidad | `[n, d_model] × [d_model, d_ff]` | `[n, d_ff]` | `d_ff` comúnmente 4x `d_model` (de 512 a 2048 en el paper original); ReLU originalmente, GELU/SwiGLU en arquitecturas posteriores |
| `... W2 + b2` | `[n, d_ff] × [d_ff, d_model]` | `[n, d_model]` | proyecta de vuelta hacia abajo para que el resultado se sume al residual stream |

Se aplica de forma idéntica, con los mismos pesos, a cada posición por separado, y aquí ninguna posición ve nunca el vector de otra. Este es el complemento preciso de la atención: la atención mezcla entre posiciones pero es lineal en los values una vez calculados sus pesos; el bloque feed-forward es donde la representación propia de una sola posición recibe un remodelado genuinamente no lineal.

## Apilar bloques

| Propiedad | Qué significa | Por qué importa |
|---|---|---|
| Conserva el shape | Cada bloque toma `d_model` de entrada y produce `d_model` de salida | La salida del bloque N se convierte en la entrada del bloque N+1 sin adaptador; el mismo shape de bloque se apila cualquier número de veces |
| Sin compartir pesos | Cada bloque tiene sus propios parámetros, aprendidos de forma independiente | Cuesta parámetros más o menos linealmente con la profundidad; compra que distintos bloques se especialicen a distintas profundidades |
| Residual stream | Un único vector que corre pasa por cada bloque, y cada uno le suma su propia contribución | Esto es exactamente lo que protege la maquinaria de residuales y layer norm de la lección 5 a medida que la profundidad crece hasta decenas de bloques |

## Embedding, salida y weight tying

| Capa | Shape | Papel |
|---|---|---|
| Embedding de entrada | `vocab_size × d_model` | La fila `i` es el vector aprendido del token `i`; buscarlo es una búsqueda, no una transformación calculada |
| Proyección de salida | `d_model × vocab_size` | Produce un logit por cada token del vocabulario en cada posición |

Los dos shapes son transpuestos uno del otro. El **weight tying** reutiliza la matriz de embedding, transpuesta, como proyección de salida (`logits = h @ W_embedding^T`) en lugar de aprender una segunda matriz, con el razonamiento de que ambas capas relacionan un token con la misma representación subyacente.

Ejemplo resuelto: vocabulario de 50,000, `d_model = 768`. Tabla de embeddings: `50,000 × 768 = 38,400,000` parámetros. Una capa de salida sin tying necesita una segunda matriz de ese tamaño; el tying la elimina, y ahorra aquí unos 38.4 millones de parámetros sin pérdida de calidad, y a menudo con una mejora medible.

## Antes de confiar en una implementación del modelo completo

- [ ] La codificación posicional se suma a los embeddings de los tokens antes del primer bloque, no se inyecta de otra manera en la atención.
- [ ] Cada subcapa está envuelta en una conexión residual, y la colocación de la layer norm (pre o post) es una elección deliberada, no lo que casualmente usó un tutorial.
- [ ] Las dos capas del bloque feed-forward expanden y luego contraen (`d_model` a `d_ff` a `d_model`), y sus pesos nunca se comparten entre posiciones.
- [ ] Cada bloque de la pila toma y devuelve `d_model`, y cada uno tiene sus propios pesos aprendidos de forma independiente.
- [ ] Si se usa weight tying, la proyección de salida es la matriz de embedding transpuesta, no una segunda matriz aprendida.

## Fuentes

- [Paper: "Attention Is All You Need", Vaswani et al., 2017](https://arxiv.org/abs/1706.03762)
- [Paper: "Layer Normalization", Ba, Kiros, and Hinton, 2016](https://arxiv.org/abs/1607.06450)
- [Paper: "On Layer Normalization in the Transformer Architecture", Xiong et al., 2020](https://arxiv.org/abs/2002.04745)
- [Paper: "Using the Output Embedding to Improve Language Models", Press and Wolf, 2017](https://arxiv.org/abs/1608.05859)
- [Recursos](../RESOURCES.md)
