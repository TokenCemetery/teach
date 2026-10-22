---
title: "Presupuesto de memoria"
description: "Contabilidad de bytes, y qué probar cuando una ejecución no cabe"
type: reference
---

# Presupuesto de memoria

Contabilidad de bytes para el fine-tuning con adapters. Pensado para consultar durante una ejecución.

## Bytes por parámetro

| Formato | Bytes | Bits |
|---|---|---|
| fp32 | 4 | 32 |
| bf16 / fp16 | 2 | 16 |
| int8 | 1 | 8 |
| 4 bits, en bruto | 0.5 | 4 |
| 4 bits + escalas fp32, bloque 64 | 0.5625 | 4.5 |
| 4 bits + doble cuantización | ~0.516 | ~4.13 |

**Reflejo:** los gigabytes en bf16 ≈ 2 × los parámetros en miles de millones.

## Costo de entrenamiento por parámetro

| Categoría | fp32 | Precisión mixta |
|---|---|---|
| Pesos | 4 | 2 bf16 + 4 master fp32 |
| Gradientes | 4 | 2 |
| Momento 1 de AdamW | 4 | 4 |
| Momento 2 de AdamW | 4 | 4 |
| **Total entrenable** | **16** | **16** |
| **Total congelado** | **4** | **2** |

La precisión mixta no reduce el total. Compra throughput aritmético.

| Variante de optimizador | Bytes/param |
|---|---|
| AdamW, momentos fp32 | 16 |
| AdamW, momentos de 8 bits | 10 |
| SGD con momentum | 12 |

## Conteos de parámetros

```text
attention/layer = 2·d² + 2·d·d_kv          # q,o full; k,v narrowed by GQA
mlp/layer       = 3·d·d_ff                  # gate, up, down
model           ≈ n_layers·(attn + mlp) + vocab·d·(1 if tied else 2)
```

El MLP suele ser del 75 al 80% de un bloque.

## Conteo de parámetros del adapter

```text
adapter = Σ over targeted layers:  r · (d_in + d_out)
```

Lo domina la dimensión **mayor**, así que el estrechamiento de GQA apenas encoge un adapter.

| Base | Targets | Rank | Adapter | % del base |
|---|---|---|---|---|
| ~1.1B, d=2048 | atención | 8 | 2.5M | 0.22% |
| ~7B, d=4096 | q,v | 16 | 6.8M | 0.10% |
| ~7B, d=4096 | todas las lineales | 64 | ~160M | ~2.3% |

## Activaciones

```text
activations ≈ n_layers · batch · seq_len · d · ~20 bytes
```

La constante es un punto de partida contra el que medir, no una ley. Lineal en el batch y en la longitud de secuencia; el término cuadrático de las puntuaciones de atención lo elimina un kernel de atención eficiente en memoria.

| Config | Estimación |
|---|---|
| 24 capas, d=2048, batch 4, seq 2048 | ~8 GB |
| 32 capas, d=4096, batch 2, seq 4096 | ~21 GB |

El gradient checkpointing recorta esto aproximadamente un orden de magnitud a cambio de un ~20 a 40% más de tiempo por paso.

**En una ejecución con adapter, las activaciones suelen dominar.** Esto invierte el perfil del full fine-tuning.

![Dos barras apiladas en una misma escala en gigabytes. Un full fine-tune de 7B con AdamW son 112 GB fijos más 21 GB de activaciones, así que las activaciones son el 16% del total. Una ejecución de QLoRA sobre un base de 7B en NF4 con un adapter de 20M son 3.9 GB fijos más los mismos 21 GB, así que las activaciones son el 84% del total.](images/activations-dominate.svg)

Ambas barras toman la memoria fija de la tabla de más abajo y las activaciones de la fila de 32 capas, d=4096, batch 2, seq 4096 de arriba, sin gradient checkpointing. El bloque de activaciones tiene el mismo tamaño en ambas, porque depende de la forma del forward pass y no de cuántos parámetros sean entrenables. Solo se desploma la memoria que lo rodea, y por eso lo que hay que recortar rara vez es el adapter.

## Totales resueltos, sin contar las activaciones

| Configuración | Memoria fija |
|---|---|
| Full FT, 1.5B, AdamW | 24 GB |
| Full FT, 7B, AdamW | 112 GB |
| Full FT, 70B, AdamW | 1120 GB |
| Base de 7B en bf16 + adapter de 20M | 14.3 GB |
| Base de 7B en NF4 + adapter de 20M | ~3.9 GB |
| Base de 13B en NF4 + adapter de 30M | ~7.2 GB |

## Cuando una ejecución no cabe

En orden de lo que cedes:

1. **Gradient checkpointing**, cuesta solo tiempo
2. **Batch size más bajo, subir la gradient accumulation**, estadísticamente equivalente
3. **Longitud de secuencia más corta**, pero revisa primero la distribución de longitudes de tokens; esto cambia la tarea
4. **Cuantizar el base**, cuesta algo de calidad
5. **Rank más bajo**, es lo que menos ahorra y cuesta capacidad

El rank es el instinto y casi la peor opción. Reducir a la mitad el rank de un adapter de 4M ahorra ~32 MB.

## Batch size efectivo

```text
effective = per_device_batch × grad_accumulation × num_devices
```

Reporta siempre el número efectivo.

## Relacionado

- [Lección 5](../lessons/0005-counting-parameters-and-bytes.md), [Lección 6](../lessons/0006-gradients-and-optimizer-state.md), [Lección 7](../lessons/0007-activations-and-checkpointing.md), [Lección 15](../lessons/0015-nf4-and-double-quantisation.md)
