---
title: "2. Capacidad y tamaño de lote"
description: "Cómo el reparto de cabezas (GQA/MQA) y el tamaño de lote cambian la huella real de la caché"
type: lesson
---

# Lección 2. Capacidad y tamaño de lote

**Vínculo con la misión:** Un presupuesto de latencia se defiende en función de cuántas solicitudes concurrentes puede mantener un servidor, y esa cifra sale directamente de la aritmética de la caché que esta lección amplía.
**Fuente principal:** [Article: "Transformer Inference Arithmetic", Kipply](https://kipp.ly/transformer-inference-arithmetic/)
**Requisitos previos:** [Lección 1](0001-the-kv-cache.md), [KV cache](../GLOSSARY.md)

## Calentamiento

1. ▢ En una frase, ¿qué le permite saltarse la KV cache a un servidor en cada token generado después del primero?

<details markdown="1"><summary>Comprobación</summary>

Recalcular los vectores key y value de cada token previo de la secuencia, en cada capa.

</details>

2. ▢ ¿Qué fallaba en una asignación de caché ingenua, contigua y dimensionada a la longitud máxima, y qué cambió PagedAttention al respecto?

<details markdown="1"><summary>Comprobación</summary>

Reservaba memoria para la longitud máxima que una secuencia podía alcanzar, y la desperdiciaba como fragmentación interna y externa. PagedAttention asigna la caché en bloques no contiguos de tamaño fijo, direccionados mediante una tabla por secuencia.

</details>

## Qué debes saber

### La mayoría de los modelos no guardan un key y un value por cabeza

La fórmula de la lección 1, `2 × num_layers × d_model × 2 bytes` por token, asume que cada cabeza de atención guarda sus propios vectores key y value. Eso es la **atención multi-cabeza (MHA)**. La mayoría de los modelos que se sirven hoy usan **grouped-query attention (GQA)** o su caso extremo, **multi-query attention (MQA)**: muchas cabezas de query comparten un número mucho menor de cabezas key/value. La caché solo guarda un par K/V por *cabeza KV*, no por cabeza de query, así que la fórmula pasa a ser:

```text
bytes per token = 2 (K and V) × num_layers × num_kv_heads × head_dim × bytes_per_value
```

donde `head_dim = d_model / num_heads`, y `num_kv_heads` es ahora el número que importa, no el total de cabezas. Cuando `num_kv_heads = num_heads` esto se reduce exactamente a la fórmula de la lección 1 (MHA es el caso especial de GQA). Cuando `num_kv_heads` es mucho menor, la caché se reduce en esa misma proporción, gratis, sin cambiar la longitud de contexto ni el tamaño de lote.

![Tres filas: MHA tiene 8 cabezas de query, cada una emparejada con su propia cabeza KV; GQA tiene grupos de cabezas de query que comparten una de 2 cabezas KV (una cuarta parte de la caché); MQA tiene las 8 cabezas de query compartiendo una única cabeza KV (una octava parte de la caché). El número de cabezas de query nunca aparece en la fórmula de la caché; solo el número de cabezas KV.](images/mha-gqa-mqa-head-sharing.svg)

Llama-2-70B es un caso concreto: 80 capas, 64 cabezas de query, pero solo 8 cabezas KV, `head_dim` = 128. En fp16:

```text
per token = 2 × 80 × 8 × 128 × 2 bytes = 327,680 bytes ≈ 320 KB
```

Si hubiera usado MHA completa (64 cabezas KV en lugar de 8), las mismas capas y el mismo `head_dim` dan `2 × 80 × 64 × 128 × 2 = 2,621,440 bytes ≈ 2.5 MB` por token, ocho veces más, exactamente la proporción entre `num_heads` y `num_kv_heads`. GQA es una decisión de costo de serving tanto como de modelado.

### De un costo por token a la huella total de un lote

Un servidor rara vez mantiene una sola secuencia. La huella total de la caché en cada momento es el costo por token, multiplicado por lo que ha crecido cada secuencia, multiplicado por cuántas secuencias residen juntas:

```text
total cache bytes = bytes per token × context length × batch size
```

Para Llama-2-70B con un contexto de 4096 tokens, una secuencia cuesta `320 KB × 4096 ≈ 1.25 GB`. Treinta y dos secuencias concurrentes con esa misma longitud cuestan `1.25 GB × 32 = 40 GB`, antes de que los propios pesos del modelo ocupen espacio alguno.

### Convertir eso en un presupuesto de capacidad

Esta es la cifra que necesita de verdad una decisión de serving: dado un pool de memoria, ¿cuántas secuencias concurrentes caben? Resta los pesos y la sobrecarga del framework a la memoria total disponible, y divide lo que queda entre el costo de caché por secuencia con la longitud de contexto que planeas admitir:

```text
max concurrent sequences = (total memory − weights − overhead) / (bytes per token × context length)
```

Toma un pool de 320 GB (cuatro GPU de 80 GB, con tensor parallelism) que sirve Llama-2-70B, con pesos y sobrecarga del framework medidos en 160 GB. Eso deja 160 GB para la caché. Con la cifra anterior de 4096 tokens y 1.25 GB por secuencia: `160 GB / 1.25 GB ≈ 128` secuencias concurrentes. Ese techo, y no el throughput bruto del modelo, es lo que suele negociar un scheduler de batching, que es donde continúa la lección 4.

## Práctica

1. ▢ Un modelo usa GQA con `num_kv_heads` igual a una cuarta parte de `num_heads`. En comparación con el mismo modelo con MHA completa, ¿cuánto más pequeña es su KV cache por token?

<details markdown="1"><summary>Comprobación</summary>

Una cuarta parte del tamaño. La caché guarda un par K/V por cabeza KV, no por cabeza de query, así que el costo por token escala solo con `num_kv_heads`; todo lo demás en la fórmula queda igual.

</details>

2. ▢ Un modelo tiene 48 capas, 40 cabezas de query, 8 cabezas KV, `head_dim` = 128, servido en fp16. Calcula su tamaño de KV cache por token.

<details markdown="1"><summary>Pista</summary>

Usa `2 × num_layers × num_kv_heads × head_dim × bytes_per_value`. El número de cabezas de query no aparece en absoluto en la fórmula.

</details>

<details markdown="1"><summary>Comprobación</summary>

`2 × 48 × 8 × 128 × 2 = 196,608 bytes ≈ 192 KB` por token.

</details>

3. ▢ Con el modelo de 192 KB por token de la pregunta 2, calcula la huella total de la caché para un lote de 16 secuencias con un contexto de 2048 tokens.

<details markdown="1"><summary>Pista</summary>

`total cache bytes = bytes per token × context length × batch size`.

</details>

<details markdown="1"><summary>Comprobación</summary>

Por secuencia: `192 KB × 2048 ≈ 384 MB`. Para 16 secuencias: `384 MB × 16 = 6,144 MB ≈ 6 GB`.

</details>

4. ▢ Un servidor tiene 96 GB de memoria. Los pesos y la sobrecarga del framework ocupan 40 GB. La caché de cada secuencia cuesta 384 MB con la longitud de contexto que admite este servidor. ¿Cuál es el número máximo de secuencias concurrentes que permite el presupuesto de caché?

<details markdown="1"><summary>Comprobación</summary>

`(96 GB − 40 GB) / 384 MB = 56 GB / 384 MB ≈ 149` secuencias. En la práctica un servidor reserva un margen de seguridad adicional por debajo de este techo, pero la aritmética es esta división.

</details>

## Prácticas en el mundo real

- [ ] Busca el campo `num_key_value_heads` (o equivalente) en el archivo de configuración de un modelo que planees servir, junto a `num_attention_heads`. Calcula la proporción entre ambos y lo que recupera en tamaño de caché.
- [ ] Con el tamaño de caché por token de ese modelo, calcula cuántas secuencias concurrentes podría contener un pool de memoria al que tengas acceso (o la memoria de una GPU publicada) con una longitud de contexto que te importe.
- [ ] Mañana: encuentra el parámetro que usa tu stack de serving preferido (vLLM o llama.cpp) para limitar la memoria total de la KV cache, y lee qué pasa cuando una solicitud lo superaría.

## Para profundizar

- [Article: "Transformer Inference Arithmetic", Kipply](https://kipp.ly/transformer-inference-arithmetic/)
- [Paper: "Efficient Memory Management for Large Language Model Serving with PagedAttention", Kwon et al., SOSP 2023](https://arxiv.org/abs/2309.06180)
- [Recursos](../RESOURCES.md)

---

¿No termina de quedar claro? Vuelve a leer la fuente primaria de arriba, ya que esta lección la comprime y en la compresión es donde se escapa la comprensión. Consulta el [glosario](../GLOSSARY.md) por si algún término te resultó resbaladizo.

Si lo poco claro es la propia lección y no el material, eso es un defecto: [abre un issue](https://github.com/TokenCemetery/teach/issues).
