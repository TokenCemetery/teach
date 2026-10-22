---
title: "El bucle de entrenamiento"
description: "Pérdida de entropía cruzada sobre el vocabulario, el backward pass y autograd, y el paso del optimizador AdamW, de los logits a los pesos actualizados"
type: reference
---

# El bucle de entrenamiento: pérdida, backward pass y optimizador

La etapa 4 comprimida para consulta. La [lección 9](../lessons/0009-cross-entropy-loss.md) cubre convertir los logits en una única pérdida escalar; la [lección 10](../lessons/0010-backward-pass-and-autograd.md) cubre convertir ese escalar en un gradiente para cada peso; la [lección 11](../lessons/0011-adamw-optimizer.md) cubre convertir los gradientes en actualizaciones de los pesos. Esta hoja reúne las tres fórmulas, en el orden en que las usa realmente el entrenamiento.

## Pérdida de entropía cruzada

```text
loss = -log(p_correct)
```

| `p_correct` | Pérdida | Se lee como |
|---|---|---|
| 0.8 | `-log(0.8) ≈ 0.223` | Seguro y en lo cierto, penalización pequeña |
| 0.1 | `-log(0.1) ≈ 2.303` | Equivocado con seguridad, penalización más de 10 veces mayor ante una caída de 10 veces en la probabilidad |

`-log(p)` crece sin cota cuando `p` se acerca a 0; una penalización más simple de `1 - p` se satura en 1 y no puede distinguir "algo equivocado" de "catastróficamente seguro y equivocado". También tiene un gradiente limpio respecto de los logits (`softmax_output - one_hot_true_label`), que es por lo que el softmax y la entropía cruzada casi siempre van emparejados, a menudo como una única operación fusionada y numéricamente estable sobre logits en bruto.

**Teacher forcing.** El entrenamiento siempre alimenta como contexto los tokens previos reales, nunca las propias predicciones del modelo. Como la máscara causal ya restringe cada posición a atender solo hacia atrás, la predicción de cada posición, y por tanto la pérdida de cada posición, se calcula en un solo forward pass y no en una pasada por posición. Las pérdidas por posición y por batch se promedian en un único escalar, ya que el descenso de gradiente necesita una sola cantidad que minimizar.

## El backward pass y autograd

Cada operación del forward (multiplicación de matrices, softmax, una suma residual) se registra en un **grafo de cómputo**. `loss.backward()` lo recorre en sentido inverso, aplicando la regla de la cadena de forma automática con la regla de backward local ya implementada de cada operación, y rellena el `.grad` de cada parámetro entrenable.

Ejemplo resuelto de regla de la cadena: `y = 3x + 1`, `z = y^2`, con `x = 2`: `y = 7`, `dz/dy = 2y = 14`, `dy/dx = 3`, así que `dz/dx = 14 x 3 = 42`.

| Enfoque | Cómo obtiene un gradiente | Costo |
|---|---|---|
| Diferenciación simbólica | Deriva una fórmula cerrada a mano o mediante álgebra computacional | No es lo que hace autograd |
| Diferenciación numérica | Perturba cada parámetro y vuelve a ejecutar el forward pass | Imprecisa, un forward pass extra por parámetro |
| Diferenciación automática (autograd) | Encadena la regla de backward local ya implementada de cada operación sobre el grafo registrado | Exacta, un único recorrido hacia atrás para todos los parámetros a la vez |

**Por qué los residuales evitan realmente los gradientes que se desvanecen.** Para `y = x + Sublayer(x)`, `d(loss)/d(x) = d(loss)/d(y) x 1 + [a term through Sublayer]`. La derivada local del camino identidad es exactamente 1, así que el término directo pasa sin escalar por pequeña que llegue a ser la derivada propia de `Sublayer`. Esta es la razón mecánica, y no solo una intuición.

**Los gradientes se acumulan, no se sobrescriben.** `.grad` se suma a lo que ya hubiera, así que un bucle de entrenamiento debe poner explícitamente a cero los gradientes antes de cada nueva llamada a `backward()`, o el gradiente de un paso queda contaminado por los sobrantes del paso anterior.

## El paso del optimizador AdamW

```text
plain gradient descent:  w = w - lr * grad
Adam's moments:           m = beta1 * m + (1 - beta1) * grad          (momentum)
                          v = beta2 * v + (1 - beta2) * grad^2        (adaptive scale)
Adam's update:            w = w - lr * m_hat / (sqrt(v_hat) + eps)
AdamW's update:           w = w - lr * (m_hat / (sqrt(v_hat) + eps) + weight_decay * w)
```

(`m_hat` y `v_hat` son `m` y `v` con corrección de sesgo porque ambas empiezan en cero.)

| Pieza | Añade | Corrige |
|---|---|---|
| Momentum (`m`) | Un promedio móvil de los gradientes pasados | Los gradientes ruidosos por batch; la actualización sigue una dirección consistente en lugar de temblar |
| Escala adaptativa (`v`) | Una estimación por parámetro de la magnitud de gradiente típica | Un único learning rate fijo para cada peso; los parámetros de gradiente pequeño reciben pasos relativamente mayores, y los de gradiente grande, menores |
| Weight decay desacoplado (AdamW) | Weight decay aplicado directamente a `w`, sin pasar nunca por `m`, `v` ni por el denominador adaptativo | Incorporar el decay al gradiente (el Adam original) hace que su encogimiento efectivo dependa de la magnitud de gradiente típica de cada parámetro, en lugar del encogimiento uniforme que se supone que es el decay |

Ejemplo resuelto: `w = 5.0`, `grad = 2.0`, `lr = 0.1`, descenso de gradiente simple: `w = 5.0 - 0.1 x 2.0 = 4.8`.

## Antes de confiar en una implementación del bucle de entrenamiento

- [ ] La entropía cruzada toma directamente logits en bruto (una operación fusionada de softmax más logaritmo negativo de la probabilidad), no un softmax manual seguido de un paso de logaritmo aparte.
- [ ] El entrenamiento alimenta los tokens previos reales (teacher forcing), y la pérdida se calcula para cada posición en un solo forward pass, no en una pasada por posición.
- [ ] Los gradientes se ponen explícitamente a cero antes de cada llamada a `backward()`.
- [ ] El optimizador es AdamW, no Adam simple, si se usa weight decay, y el weight decay se aplica directamente a los pesos, no incorporado al gradiente.

## Fuentes

- [Docs: "torch.nn.functional.cross_entropy", PyTorch](https://pytorch.org/docs/stable/generated/torch.nn.functional.cross_entropy.html)
- [Docs: "Autograd mechanics", PyTorch](https://pytorch.org/docs/stable/notes/autograd.html)
- [Paper: "Decoupled Weight Decay Regularization", Loshchilov and Hutter, 2019](https://arxiv.org/abs/1711.05101)
- [Paper: "Adam: A Method for Stochastic Optimization", Kingma and Ba, 2015](https://arxiv.org/abs/1412.6980)
- [Recursos](../RESOURCES.md)
