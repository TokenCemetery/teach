---
title: "Modos de fallo"
description: "Del síntoma a la causa, y los fallos silenciosos"
type: reference
---

# Modos de fallo

Hoja de diagnóstico. Mantenla abierta durante una ejecución.

## Las cuatro comprobaciones, antes que nada

```python
# 1. Did the adapter attach?
model.print_trainable_parameters()          # compare to your arithmetic

# 2. Is the data what you think?
print(repr(tokenizer.decode(ds[0]["input_ids"])))
print(sum(1 for l in ds[0]["labels"] if l != -100), "of", len(ds[0]["labels"]), "scored")

# 3. Does loss move?                        # logging_steps=1 over 50 steps

# 4. Can it overfit two examples?           # loss → ~0 in 100 steps, or the pipeline is broken
```

La comprobación 2 atrapa en una sola lectura el desajuste de template, los tokens de fin de turno ausentes, los bugs de enmascarado y el truncamiento. Son los diez segundos de más valor de todo el proceso.

## Síntoma → causa

![Seis bocetos de pérdida frente a pasos: plana desde el paso 1, una caída que se detiene muy por encima de cero, las curvas de entrenamiento y held-out separándose con la held-out volviendo a subir, una escalera de tramos planos y caídas bruscas, un descenso interrumpido por un pico, y un descenso que termina de golpe en NaN.](images/loss-curve-shapes.svg)

Las primeras once filas de abajo nombran una curva y no un evento, y varias comparten forma: tres dicen plana, dos dicen que apenas se mueve. Empareja el boceto, y luego lee cada fila que lo nombra, ya que una forma puede tener más de una causa. Desde la fila doce el síntoma se observó en otro lugar, en una salida, un error de carga o un conjunto de regresión, y no hay curva con la que emparejar.

| Síntoma | Causa probable | Comprobación |
|---|---|---|
| Pérdida exactamente plana desde el paso 1 | El adapter no coincidió con nada | `print_trainable_parameters()` |
| Pérdida exactamente plana desde el paso 1 | Todas las etiquetas son `-100` | Contar las posiciones puntuadas |
| Pérdida exactamente plana desde el paso 1 | LR órdenes de magnitud demasiado bajo | Debería estar en ~`1e-4` |
| La pérdida apenas se mueve | Nombres de target modules equivocados para esta arquitectura | `named_modules()` |
| La pérdida apenas se mueve | `α/r` accidentalmente minúsculo | Se subió `r`, se olvidó `α` |
| La pérdida se estanca alta | Techo de capacidad | Más rank o más targets, no más epochs |
| Held-out sube, train cae | Sobreajuste | Desplegar el mínimo held-out |
| Train → 0 rápido, held-out sube de inmediato | Dataset demasiado pequeño para la capacidad | Más datos, menos capacidad |
| La pérdida en escalera en las fronteras de epoch | Memorización | Menos epochs |
| La pérdida da un pico y se recupera | Un batch patológico | Encontrar el ejemplo atípico |
| Pérdida → `NaN` | Desbordamiento, o datos malos | Preferir bf16; bajar el LR; añadir warm-up |
| Held-out sospechosamente bueno | Contaminación a través de la partición | Deduplicar train frente a test, leer las parejas de mayor similitud |
| El modelo nunca deja de generar | Sin token de fin de turno en los datos de entrenamiento | Decodificar un ejemplo |
| La salida ignora el formato pedido | Desajuste de template entre entrenamiento y serving | Comparar con `repr` |
| Respuestas cortadas a mitad de frase | `max_length` truncando los objetivos | Revisar la distribución de longitudes |
| Respuestas a preguntas que nadie hizo | El packing rompió el enmascarado de pérdida o las fronteras | Verificar que `-100` sobrevive al packing |
| Peor en cosas no relacionadas | Olvido catastrófico | Conjunto de regresión frente a la baseline almacenada |
| Ya no rechaza lo que el base rechazaba | Regresión de seguridad | **Bloquea el despliegue** |
| Salida fusionada ≠ sin fusionar | Bug de fusión, o el muestreo estaba activado | Volver a verificar de forma greedy |
| Modelo fusionado degradado | Fusionado en un base cuantizado | Fusionar en precisión completa y luego cuantizar |
| El adapter no carga | Base model o revisión equivocados | Un adapter es un diff; necesita su base exacta |
| Errores de gradiente en un base de 4 bits | Se omitió `prepare_model_for_kbit_training` | Añadirlo |
| Gran eval, mala producción | Desajuste de distribución entre entrenamiento y serving | Entrenar con inputs reales, no limpios |
| El resultado desapareció al repetir | Ruido de seeds, nunca un efecto real | Varias seeds, comparación pareada |

## Fallos silenciosos: sin error, resultado equivocado

El conjunto peligroso. Nada lanza un error, todo parece estar bien.

1. **Desajuste de template** entre entrenamiento y serving.
2. **Token de fin de turno ausente.** Entrena bien, nunca se detiene.
3. **Enmascarado de pérdida equivocado.** Entrenar con los prompts sin querer.
4. **Contaminación.** El held-out mide memorización, reporta generalización.
5. **Fuga por grupo o temporal.** Dividir por la clave equivocada.
6. **Olvido catastrófico.** Cada número que vigilas mejora.
7. **Adapter acoplado a nada.** Entrena, registra una pérdida, no aprende nada.
8. **Evaluar un artefacto distinto del que despliegas**, por ejemplo eval en bf16 y despliegue en 4 bits.

Cada uno tiene un paso de detección específico arriba. Ninguno se anuncia.

## Reducir el olvido

Lo más barato primero:

1. Menos pasos, o un checkpoint anterior
2. Learning rate más bajo
3. Rank más bajo, o menos target modules
4. Mezclar unos pocos por ciento de datos generales de instrucciones en el entrenamiento
5. **Mantener el adapter sin fusionar y enrutar**, para que el base quede intacto y el olvido deje de importar

## Higiene de la comparación

- Una variable cada vez; fija seed, datos y partición
- Varias seeds, ya que la varianza suele superar al efecto
- Comparación pareada sobre ejemplos idénticos
- Reporta `n` y un intervalo, nunca un número suelto
- Lee generaciones reales, incluidos los fallos, cada vez

## Qué registrar por ejecución

Base model **y revisión** · configuración del adapter literal · dataset y partición exacta · seed · batch size efectivo · LR y schedule · pasos · checkpoint elegido y el número que lo justifica · versiones de las bibliotecas · resultados de la eval y de la regresión.

## Relacionado

- [Lección 11](../lessons/0011-your-first-adapter.md), [Lección 12](../lessons/0012-reading-a-training-run.md), [Lección 22](../lessons/0022-contamination-and-held-out-design.md), [Lección 24](../lessons/0024-the-regression-suite.md)
