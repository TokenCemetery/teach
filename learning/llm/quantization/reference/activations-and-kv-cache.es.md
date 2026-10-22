---
title: "Activaciones y KV cache"
description: "Solo pesos frente a pesos y activaciones, SmoothQuant, rotaciones y cuantización de la KV cache para consulta"
type: reference
---

# Activaciones y KV cache: cuantizar más allá de los pesos

La etapa 5 comprimida para consulta. La [Lección 13](../lessons/0013-weights-activations-or-both.md) cubre solo pesos frente a pesos y activaciones, la [lección 14](../lessons/0014-smoothquant.md) SmoothQuant, la [lección 15](../lessons/0015-rotations.md) las rotaciones, y la [lección 16](../lessons/0016-kv-cache-quantization.md) la cuantización de la KV cache.

## Pesos, activaciones o ambos

| Esquema | Almacenado pequeño | El matmul corre en | Compra | Encaja en |
|---|---|---|---|---|
| W4A16, W8A16 (solo pesos) | Pesos | 16 bits, tras descuantizar en el kernel | Memoria, bytes leídos por token | Limitado por el ancho de banda de memoria: decode con lotes pequeños |
| W8A8 int8 o fp8 | Pesos y activaciones | 8 bits | Throughput aritmético, además de memoria | Limitado por cómputo: prefill, lotes grandes |
| W4A4 con rotaciones | Pesos, activaciones, a menudo KV | 4 bits | Memoria y aritmética | Solo donde existe un kernel de 4 bits, ver la lección 20 |

Kurtic et al. (familia Llama 3.1, más de 500,000 evaluaciones): fp8 W8A8 efectivamente sin pérdida, int8 W8A8 bien ajustado con una degradación del 1 al 3%, W4A16 int rivaliza con 8 bits. Consejo: W4A16 para servicio síncrono, W8A8 para continuous batching.

## Por qué las activaciones son más difíciles

| Propiedad | Pesos | Activaciones |
|---|---|---|
| Rango conocido | Tras el entrenamiento, fijo | Solo en tiempo de ejecución |
| Outliers | Planos, fáciles de cuantizar | Unas 100 veces la mayoría de los valores, en canales fijos en todos los tokens (SmoothQuant) |
| Granularidad de scale que permite un GEMM en int8 | Por canal de salida | Solo por tensor o por token |

El GEMM en int8: `Y = diag(s_X) · (X_int8 @ W_int8) · diag(s_W)`. Los scales quedan solo en las dimensiones externas; un scale por canal de entrada quedaría dentro de la suma.

| Scale de activaciones | Se calcula | Costo | Riesgo |
|---|---|---|---|
| Estático | Offline, a partir de un calibration set | Ninguno por solicitud | Calibration set distinto del tráfico real |
| Dinámico | En tiempo de ejecución, a partir del tensor | Una reducción antes de cada matmul | Poco; se adapta a cada entrada |

## SmoothQuant

```text
X @ W = (X @ diag(s)^-1) @ (diag(s) @ W)
s_j   = max(|X_j|)^α / max(|W_j|)^(1 - α)
```

| `α` | Efecto |
|---|---|
| 0 | Activaciones sin cambios |
| 0.5 | Valor por defecto equilibrado del paper, punto óptimo para OPT y BLOOM |
| Mayor, hacia 1 | Más dificultad a los pesos; para modelos con outliers más pesados, como GLM-130B |
| 1 | Cada canal de activación tiene el mismo máximo; los pesos cargan con todos los outliers |

- `max(|X_j|)` sale de un calibration set.
- El factor se fusiona offline en la capa que produce `X`: sin costo en tiempo de ejecución.
- Un método de 8 bits: hasta 1.56x de aceleración y 2x de reducción de memoria en el paper.

## Rotaciones

```text
X @ W = (X @ Q) @ (Q.T @ W)      where Q @ Q.T = I
```

| Punto | Detalle |
|---|---|
| Qué hace | Reparte un outlier entre todos los canales; el máximo queda cerca del RMS |
| `Q` habitual | Hadamard aleatorizada: entradas ±1/sqrt(n), costo `n log n` |
| Fusionada offline | Rotación del residual stream, en los pesos |
| Online | Antes de la proyección de bajada del FFN; por cabeza en queries y keys, tras RoPE |
| QuaRot | Todos los pesos, activaciones y KV cache en 4 bits; Llama 2 70B a 0.47 de perplexity en WikiText-2, 99% del zero-shot |
| SpinQuant | Las rotaciones aleatorias difieren hasta 13 puntos zero-shot; las rotaciones aprendidas reducen la brecha a 2.9 puntos en Llama 2 7B W4A4KV4 |

Pregunta de revisión para cualquier afirmación de W4A4: qué rotación, y si se eligió o se aprendió para este modelo.

## Cuantización de la KV cache

```text
KV bytes per token = 2 x layers x kv_heads x head_dim x bytes_per_value
```

Llama 3 8B (32 capas, 8 cabezas KV, dimensión 128) en bf16: 128 KiB por token, 4 GiB por secuencia de 32,768 tokens.

| Tensor | Cuantizar a lo largo de | Por qué |
|---|---|---|
| Keys | Por canal, antes de RoPE donde sea posible | Unos pocos canales outlier fijos (KIVI); RoPE mezcla pares de canales (KVQuant) |
| Values | Por token | Sin patrón por canal; casi 15 veces menos error en la salida de atención que por canal (KIVI) |

| Método u opción | Bits | Resultado informado |
|---|---|---|
| KIVI | 2 | Casi la misma calidad, 2.6x menos memoria máxima, hasta 4x de lote, 2.35 a 3.47x de throughput |
| KVQuant | 3 | Menos de 0.1 de degradación de perplexity; LLaMA-7B con contexto de 1M en una A100 de 80 GB |
| KV cache fp8 de vLLM | 8 | Scales por tensor o por cabeza; scales por defecto 1.0 sin calibración, se recomienda calibrar |

KIVI mantiene los tokens más nuevos (128 en sus experimentos) en precisión completa hasta que se completa un grupo por canal de keys.
