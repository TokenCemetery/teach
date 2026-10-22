---
title: "Glosario"
description: "Términos canónicos del fine-tuning con adapters"
type: glossary
---

# Glosario del fine-tuning con adapters

Términos canónicos de este espacio de trabajo. Un término entra aquí cuando ya se puede usar correctamente, no cuando se menciona por primera vez, así que esto crece a medida que se ganan las lecciones.

## Uso en este espacio de trabajo

Tres palabras se usan de forma laxa en todo el campo, de maneras que volverían ambiguas las lecciones posteriores, así que se fijan desde el principio:

**Fine-tuning**:
Entrenar un conjunto pequeño de parámetros añadidos o seleccionados para una tarea mientras los pesos del base model permanecen congelados. Cuando se entrenan todos los pesos, este espacio de trabajo dice siempre _full fine-tuning_ de forma explícita.
_Evitar_: entrenamiento, reentrenamiento, enseñar al modelo

**Adapter**:
El conjunto pequeño de pesos entrenables que se añade junto a un base model congelado, junto con la configuración que describe dónde se acopla.
_Evitar_: fine-tune (como sustantivo), LoRA (cuando el método no es específicamente LoRA), checkpoint

**Cuantización**:
Almacenar los pesos con una precisión numérica menor que aquella con la que se entrenaron. En este espacio de trabajo se refiere siempre al _base congelado_, salvo que se indique lo contrario: los adapters se mantienen a mayor precisión, y la cuantización para inferencia es un asunto aparte.
_Evitar_: compresión, encogimiento, optimización

## Términos

_Se añaden a medida que las lecciones los establecen._
