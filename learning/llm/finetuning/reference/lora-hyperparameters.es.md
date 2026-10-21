---
title: "Hiperparámetros de LoRA"
description: "Rank, alpha, targets, learning rate, variantes"
type: reference
---

# Hiperparámetros de LoRA

Hoja de decisión. Lee la versión instalada de la biblioteca para los nombres exactos de los parámetros, porque esta superficie cambia entre versiones.

## La ecuación

```text
h = W₀x + (α/r) · BAx
```

`A` aleatoria, `B` en cero, así que `ΔW = 0` en el paso 0 y el modelo empieza idéntico al base.

![La entrada alimenta dos caminos que se suman. El superior es la matriz base congelada. El inferior es el adapter entrenado, donde A proyecta hacia abajo hasta una barra de solo r de ancho, B proyecta de nuevo hacia arriba, y el resultado se escala por alpha entre r.](images/lora-bottleneck.svg)

La barra entre `A` y `B` tiene `r` valores de ancho, y es la única ruta que tiene el adapter de la entrada a la salida. Eso es lo que la siguiente sección entiende por capacidad: subir el rank ensancha esa barra y no cambia nada más del dibujo, y por eso compra expresividad por casi nada de memoria.

## Rank

Capacidad. Acota lo compleja que puede ser una actualización que exprese el adapter.

| Rank | Conviene a |
|---|---|
| 4 a 8 | Estilo, tono, formato de salida; datasets pequeños |
| 16 a 32 | Una tarea real, unos pocos miles de ejemplos |
| 64 a 128 | Tareas más difíciles, datos mayores, comportamiento que exige razonamiento |
| 256+ | Acercándose a la capacidad del full fine-tuning con datos grandes de SFT |

El rank cuesta casi nada de memoria. Su costo real es el riesgo de sobreajuste con datos pequeños.

## Alpha

**Solo importa `α/r`.** La convención es `α = 2r`.

| `r` | `α` | `α/r` | |
|---|---|---|---|
| 8 | 16 | 2.0 | baseline |
| 16 | 32 | 2.0 | más capacidad, misma escala |
| 16 | 16 | 1.0 | actualización más débil |
| 64 | 16 | 0.25 | **trampa**: capacidad arriba, influencia abajo 8× |

Subir `r` sin subir `α` baja el adapter. Con rank ≥ 64 considera `use_rslora=True`, que usa `α/√r`.

## Target modules

| Situación | Targets |
|---|---|
| Valor por defecto para una tarea real | todas las lineales |
| Dataset pequeño (< ~1k) | solo atención, rank bajo |
| Solo estilo o tono | solo atención, rank bajo |
| Necesita discriminaciones nuevas | debe incluir el MLP |
| Reproducir un paper | exactamente los suyos |

`"all-linear"` se resuelve contra el modelo cargado, así que no puede quedar obsoleto frente a una nomenclatura desconocida. Solo atención es una ablación de 2021, no un valor por defecto.

Nombres típicos, pero **verifica con `named_modules()`**:

```text
attention: q_proj  k_proj  v_proj  o_proj
mlp:       gate_proj  up_proj  down_proj
```

## Learning rate

| Método | Rango |
|---|---|
| Fine-tuning con adapters | `1e-4` a `2e-4` |
| Full fine-tuning | `1e-5` a `5e-5` |

Importar el learning rate del full fine-tuning a una ejecución con adapter es una de las causas principales de un primer resultado decepcionante. Usa warm-up (unos cientos de pasos) y decay de coseno.

## Otros ajustes

| Ajuste | Valor por defecto | Notas |
|---|---|---|
| `lora_dropout` | 0.0 a 0.05 | Súbelo solo si la pérdida held-out está subiendo |
| `bias` | `"none"` | Rara vez decisivo; complica la fusión |
| Epochs | 2 a 3 | Con datos de instrucciones pequeños; más suele memorizar |
| Gradient checkpointing | activado | Casi un valor por defecto para adapters |
| `use_cache` | desactivado al entrenar | Entra en conflicto con el checkpointing; inútil para entrenar |

## Variantes, por eje

| Eje | Método | Ayuda cuando |
|---|---|---|
| Escalado | rsLoRA | Rank alto |
| Learning rates | LoRA+ | Learning rates separados para `A` y `B` |
| Init | PiSSA, OLoRA | Convergencia más rápida; renuncia a la init en cero |
| Init | LoftQ | Entrenar contra un base cuantizado |
| Estructura | DoRA | Rank fijado en bajo por otra razón |
| Estructura | AdaLoRA | Las capas necesitan un rank desigual |
| Estructura | VeRA | El tamaño del adapter es la restricción que manda |

**Baseline que hay que superar:** todas las lineales, rank adecuado, learning rate ajustado. La mayoría de las variantes no lo superan por más que el ruido de las seeds.

## Base cuantizado (QLoRA)

```python
BitsAndBytesConfig(
    load_in_4bit=True,
    bnb_4bit_quant_type="nf4",             # not "fp4"
    bnb_4bit_use_double_quant=True,
    bnb_4bit_compute_dtype=torch.bfloat16,  # do not leave at default
)
```

Luego `prepare_model_for_kbit_training(model, use_gradient_checkpointing=True)`. Saltárselo da ejecuciones inestables o errores de gradiente opacos.

Todos los demás hiperparámetros quedan sin cambios. **QLoRA es LoRA con un base más barato.**

Fusiona en el base de **precisión completa**, nunca en el cuantizado.

## Diagnóstico por la curva

| Train | Held-out | Diagnóstico | Acción |
|---|---|---|---|
| ↓ | ↓ | Aprendiendo | Continuar |
| ↓ | ↑ tras una caída | Sobreajuste | Desplegar el mínimo; menos capacidad o más datos |
| → alta | → alta | Subajuste | Más rank, más targets, LR más alto |
| Plana desde el paso 1 | Plana | Roto | Comprobar que el adapter se acopló y que las etiquetas no son todas `-100` |
| `NaN` | también `NaN` | Desbordamiento | Bajar el LR; añadir warm-up; preferir bf16 |

## Relacionado

- [Lección 9](../lessons/0009-rank-alpha-and-initialisation.md), [Lección 10](../lessons/0010-choosing-target-modules.md), [Lección 19](../lessons/0019-when-dora-wins.md), [Lección 20](../lessons/0020-judging-a-new-variant.md)
