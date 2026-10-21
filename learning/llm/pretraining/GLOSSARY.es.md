---
title: "Glosario"
description: "Términos canónicos del preentrenamiento de LLM"
type: glossary
---

# Glosario del preentrenamiento de LLM

Términos canónicos para entrenar un modelo desde una inicialización aleatoria a escala: de qué se compone el presupuesto de datos y de cómputo, y cómo se reparten la memoria y el cálculo entre muchos dispositivos.

## Términos

**Activation checkpointing**:
Descartar las activaciones intermedias durante el forward pass y recalcularlas durante el backward pass, cambiando cómputo extra por un menor uso de memoria.
_Evitar_: gradient checkpointing (el nombre más común en la práctica, pero lo que guarda son activaciones, no gradientes, y el nombre impreciso confunde sobre qué se está intercambiando)

**Óptimo en cómputo (compute-optimal)**:
El punto de la disyuntiva entre número de parámetros y tokens de entrenamiento que minimiza la loss para un presupuesto de cómputo de entrenamiento fijo, frente a un modelo más grande entrenado con menos tokens de los que ese punto implica.
_Evitar_: óptimo (ambiguo sobre para qué es óptimo; empareja siempre con "cómputo" o "inferencia" para decir qué presupuesto está fijo)

**Data parallelism**:
Repartir un batch de entrenamiento entre dispositivos que tienen cada uno una copia completa del modelo, calculan los gradientes de forma independiente y los sincronizan con un all-reduce antes del paso del optimizador.
_Evitar_: entrenamiento distribuido (el data parallelism es una de sus formas; el término general oculta qué recurso se está repartiendo)

**Deduplicación**:
Eliminar de un corpus de entrenamiento los documentos casi duplicados o exactamente duplicados antes de la tokenización, porque el texto repetido es una de las principales causas de memorización y de cómputo desperdiciado.
_Evitar_: dedup (válido en lo informal, pero el glosario lo escribe completo una vez fijado el concepto)

**Gradient clipping**:
Reescalar un gradiente de forma proporcional, antes de que el paso del optimizador lo use, para que su norma global nunca supere un umbral elegido, acotando cuánto puede crecer una sola actualización sin importar qué produjo un gradiente inusualmente grande.
_Evitar_: gradient clamping (clamping suele significar acotar cada valor por separado; el clipping aquí reescala todo el vector de gradiente con un único factor para acotar su norma)

**Learning rate warmup**:
Subir el learning rate desde casi cero hasta su máximo previsto durante la primera parte del entrenamiento, en lugar de empezar de inmediato en el máximo, para que las primeras actualizaciones de la red, las menos informadas, tengan un efecto menor sobre los pesos.
_Evitar_: burn-in (término de otros campos para un periodo de estabilización; este espacio de trabajo usa warmup específicamente para la rampa del learning rate)

**Loss spike**:
Una subida repentina y brusca de la loss de entrenamiento a mitad de una ejecución, causada normalmente por un batch numéricamente inestable o por una deriva acumulada del estado del optimizador, y que se distingue del ruido normal según si la loss se recupera sola.
_Evitar_: divergencia (la divergencia es el resultado cuando un loss spike no se recupera; no son el mismo suceso)

**Pipeline parallelism**:
Repartir las capas de un modelo entre dispositivos, de modo que cada uno tiene un tramo contiguo de la pila y pasa las activaciones al siguiente, haciendo circular varios micro-batches por ella para mantener ocupados a todos los dispositivos.
_Evitar_: model parallelism (el término más amplio en el que caben este y el tensor parallelism; usa el específico cuando importe la distinción)

**Ley de escalado (scaling law)**:
Una relación empírica de ley de potencias entre la loss de un modelo y el cómputo, el número de parámetros o los datos con los que se entrenó, que se usa para predecir la loss de una ejecución de entrenamiento antes de pagarla.
_Evitar_: curva de escalado (una ley de escalado es la relación ajustada; una curva es un gráfico de ella)

**Tensor parallelism**:
Repartir las matrices de pesos de una capa individual entre dispositivos, de modo que una sola multiplicación de matrices se calcula como una suma de productos parciales de cada dispositivo, al costo de un paso de comunicación por cada capa dividida.
_Evitar_: model parallelism (el término más amplio en el que caben este y el pipeline parallelism)

**Razón de tokens por parámetro**:
El número de tokens de entrenamiento dividido por el número de parámetros del modelo, la cifra única en torno a la cual se construye un plan de entrenamiento óptimo en cómputo.
_Evitar_: razón datos-modelo (se usa de forma inconsistente en la literatura para la cantidad inversa; este espacio de trabajo siempre se refiere a tokens divididos por parámetros)

**Etapa de ZeRO (ZeRO stage)**:
Uno de los tres niveles crecientes de estado repartido entre dispositivos con data parallelism: el estado del optimizador (etapa 1), el estado del optimizador y los gradientes (etapa 2), o el estado del optimizador, los gradientes y los parámetros (etapa 3), y cada uno cambia más comunicación por menos memoria por dispositivo.
_Evitar_: FSDP (FSDP es la implementación de PyTorch del reparto al estilo de la etapa 3 de ZeRO; ZeRO es la técnica de fondo, y este espacio de trabajo usa el nombre de la técnica al hablar de la idea y FSDP al hablar de la API)
