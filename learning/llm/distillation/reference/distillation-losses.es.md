---
title: "Pérdidas de destilación"
description: "Soft targets, temperatura, la pérdida combinada, la pérdida a nivel de token, KL directa e inversa, la restricción del tokenizer y el costo de almacenar logits"
type: reference
---

# Pérdidas de destilación: las etapas 1 y 2 para consulta

Las etapas 1 y 2 comprimidas para consulta. [Lecciones 1 a 3](../lessons/0001-what-distillation-buys.md) cubren soft targets y temperatura, [lección 4](../lessons/0004-token-level-distillation.md) la pérdida a nivel de token, [lección 5](../lessons/0005-forward-and-reverse-kl.md) la dirección de la divergencia, [lección 6](../lessons/0006-the-tokenizer-constraint.md) la restricción del tokenizer y [lección 7](../lessons/0007-distilling-during-pretraining.md) el costo de la distribución del profesor a escala.

## Soft targets y temperatura

| Término | Definición | Fuente |
|---|---|---|
| Soft targets | Las probabilidades del profesor sobre cada clase, usadas como objetivo en lugar del hard label o junto a él | Hinton et al., 2015, sección 1 |
| Softmax con temperatura | q_i = exp(z_i / T) / sum_j exp(z_j / T). T = 1 es el softmax normal, una T mayor da una distribución más suave | Hinton et al., ecuación 1 |
| Dónde se usa T | La misma T alta para profesor y estudiante durante el entrenamiento. El estudiante corre con T = 1 después | Hinton et al., sección 2 |
| Gradiente con temperatura T | dC/dz_i = (1/T)(q_i - p_i). Para T grande y logits de media cero es aproximadamente (1/(N T^2))(z_i - v_i), así que igualar logits es un caso especial | Hinton et al., sección 2.1 |
| El factor T al cuadrado | Los gradientes de los soft targets escalan como 1/T^2, así que multiplica la pérdida suave por T^2 al combinarla con la pérdida dura | Hinton et al., sección 2 |

El factor en una ejecución, con los logits `[9, 4, 2, 0, -4]` frente a `[6, 5, 0, 1, -2]`: la mayor entrada del gradiente es 0.2663 con T = 1 y 0.0017 con T = 20, y multiplicada por T al cuadrado se mantiene entre 0.64 y 0.84 de T = 2 a T = 20 ([lección 3](../lessons/0003-temperature.md)).

## La pérdida combinada

```text
loss = lambda * T^2 * CE(teacher at T, student at T) + (1 - lambda) * CE(label, student at 1)
```

La notación es de este track. Hinton et al. describen un promedio ponderado de las dos entropías cruzadas y encontraron los mejores resultados en general con un peso considerablemente menor en la de hard labels.

| Ajuste | Valor | Fuente y alcance |
|---|---|---|
| Voz, peso relativo del término duro | 0.5 | Hinton et al., sección 4.1, un modelo acústico |
| Voz, temperaturas probadas | 1, 2, 5, 10 | Hinton et al., sección 4.1 |
| MNIST, estudiante de 800 unidades, soft targets con T = 20 | 74 errores de prueba, frente a 146 solo y 67 del profesor | Hinton et al., sección 3 |
| MNIST, estudiante de 30 unidades, mejores temperaturas | 2.5 a 4 | Hinton et al., sección 3 |
| Pesos de mezcla a nivel de palabra de Kim y Rush probados | 0.5 y 0.9, mejor 0.5 | Kim y Rush, 2016, sección 4 |
| Reentrenamiento de LLM podado, temperaturas probadas | 0.1, 0.5, 1.0, 3.0, mejor con 1.0 | Muralidharan et al., 2024, apéndice A.3 |
| Preentrenamiento de LLM, temperaturas probadas | 0.5 a 10, mejor con 1 en todas las escalas | Busbridge et al., 2025, apéndice G.2 |
| Reentrenamiento de LLM podado, mezcla de pérdidas | La pérdida de logits sola mejor que mezclar la pérdida de modelado de lenguaje | Muralidharan et al., 2024, sección 4 |

Cada fila es un paper en su propia configuración. Las dos filas de temperatura de LLM discrepan de las de clasificadores, así que barre T, incluido 1, en tu propio par.

## La pérdida a nivel de token

| Elemento | Elección |
|---|---|
| Formas de los logits | Estudiante y profesor, cada uno (batch, positions, vocab) |
| Eje de la divergencia | El último, el vocabulario, dando (batch, positions) |
| Prefijo | Una secuencia fija, texto humano o del profesor, dada a ambos modelos (teacher forcing) |
| Profesor | Forward pass con los gradientes desactivados |
| Reducción | Kim y Rush suman sobre las posiciones. GKD y Minitron dividen entre la longitud. Enmascara el padding y divide entre la suma de la máscara |
| Temperatura | Divide ambos logits entre T antes del log-softmax, multiplica la pérdida por T^2 si se mezcla con un término duro |

```python
import torch.nn.functional as F

def token_kd_loss(student_logits, teacher_logits, mask, T=1.0):
    s = F.log_softmax(student_logits / T, dim=-1)
    t = F.log_softmax(teacher_logits / T, dim=-1)
    kl = (t.exp() * (t - s)).sum(dim=-1)
    return (kl * mask).sum() / mask.sum()
```

La entropía cruzada frente al profesor y la KL directa difieren en la entropía del profesor, una constante para el estudiante, así que tienen los mismos gradientes. Gemma 2 escribe la suma de -P_T(x | x_c) log P_S(x | x_c) (sección 3.2).

## KL directa e inversa

| | KL directa | KL inversa |
|---|---|---|
| Expresión | KL(p \|\| q) = sum p log(p / q) | KL(q \|\| p) = sum q log(q / p) |
| p es el profesor, q el estudiante | Ponderada por el profesor | Ponderada por el estudiante |
| Penaliza | A un estudiante que da poca masa donde el profesor tiene mucha | A un estudiante que da masa donde el profesor tiene poca |
| Comportamiento | Cubre modos, se reparte sobre cada modo | Busca modos, se compromete con uno |
| En el caso de juguete de la lección 5 | Prefiere al estudiante repartido, 0.595 frente a 1.572 | Prefiere al estudiante comprometido, 0.623 frente a 1.273 |

| Fuente | Hallazgo | Alcance |
|---|---|---|
| MiniLLM, Gu et al., 2023 | KL inversa para la destilación generativa, ya que la KL directa da masa a las regiones vacías del profesor | Seguimiento de instrucciones, policy gradient sobre muestras del estudiante |
| GKD, Agarwal et al., 2023 | La mejor divergencia depende de la tarea. La JSD(beta) generalizada interpola, parecida a la directa cerca de 0, parecida a la inversa cerca de 1. KL inversa mucho mejor que la directa en el instruction tuning de FLAN | Estudiantes T5, XSum, WMT, GSM8K, FLAN |
| Minitron, Muralidharan et al., 2024 | KLD directa la mejor: pérdida de LM 2.155 frente a 2.665 de la inversa en un 8B podado en profundidad | Reentrenamiento de base models podados |

El `GKDConfig` de TRL expone la elección como `beta`: 0.0 es la divergencia KL, 1.0 la KL inversa, con 0.5 por defecto.

## La restricción del tokenizer

| Situación | Qué funciona | Qué cuesta |
|---|---|---|
| Mismo tokenizer | Pérdida a nivel de token | Necesita los logits del profesor |
| Estudiante construido a partir del profesor (DistilBERT, Minitron) | Pérdida a nivel de token | Estudiante restringido al diseño del profesor |
| Tokenizers distintos, logits disponibles | Pérdida ULD, o el trainer GOLD de TRL | Pierde la identidad del token en el término de distancia, supuesto de costo uniforme, alineación de posiciones tosca |
| Solo el texto del profesor | Entrenar con sus secuencias generadas (etapa 3) | El estudiante nunca ve las distribuciones del profesor |

ULD (Boizard et al., 2024): L = suma sobre t de CE(t) + lambda * W1(student, teacher), lambda 1.5, con W1 como la suma de las diferencias absolutas de los vectores de probabilidad ordenados en orden decreciente (sección 3). Un estudiante que pone su masa en el token equivocado puede puntuar 0 en W1, así que la entropía cruzada sobre el token de referencia lleva la señal de identidad.

TRL, tal como se leyó para la lección 6: `GKDTrainer` toma un tokenizer como `processing_class` y no tiene argumento de tokenizer del profesor. GOLD está documentado como compatible con tokenizers distintos, con `use_uld_loss=True` y `teacher_tokenizer_name_or_path`, y está en `trl.experimental`.

## El costo de almacenar los logits del profesor

Aritmética de la [lección 7](../lessons/0007-distilling-during-pretraining.md), con el vocabulario de 256,128 de Gemma 2 (Tabla 1). Los 2 bytes por probabilidad y el k = 256 con un índice de 4 bytes son supuestos, no cifras del informe.

| Cantidad | Valor |
|---|---|
| Distribución completa por token, bf16 | 512,256 bytes |
| Distribución completa por secuencia de 8,192 tokens | 4.20 GB |
| Completa para 2T de tokens (la corrida de 2B) | 1.02 EB |
| Completa para 8T de tokens (la corrida de 9B) | 4.10 EB |
| Top-256 por token, 6 bytes por entrada | 1,536 bytes, 333.5 veces menos |
| Top-256 para 2T de tokens | 3.07 PB |
| Top-256 para 8T de tokens | 12.29 PB |

El informe de Gemma 2 no describe cómo se suministró la distribución del profesor. Minitron calcula al profesor en un forward pass junto al entrenamiento y compara ejecuciones con el mismo cómputo. La prueba de top-K de Minitron encontró una caída significativa de la exactitud para K hasta 100 y ninguna mejora al truncar con K mayores, en una configuración de reentrenamiento de un modelo podado.

## Dónde leer más

- [Recursos](../RESOURCES.md)
- [Glosario](../GLOSSARY.md)
