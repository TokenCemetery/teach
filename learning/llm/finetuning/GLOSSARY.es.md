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

**Base model**:
Un modelo entrenado con un solo objetivo, predecir el siguiente token a lo largo de un corpus grande. Continúa el texto en lugar de responderlo, y no tiene _chat template_.
_Evitar_: modelo en bruto, modelo preentrenado (cuando importa la distinción con un _modelo instruct_)

**Olvido catastrófico (catastrophic forgetting)**:
La degradación, durante el fine-tuning, de capacidades que los datos de entrenamiento no reforzaron, como el seguimiento general de instrucciones. No se ve en la pérdida de la tarea ni en su métrica held-out, que pueden mejorar mientras ocurre.
_Evitar_: sobreajuste (un fallo distinto, visible en el propio _held-out set_ de la tarea)

**Chat template**:
El formato exacto de cadena en el que se renderizaron las conversaciones de entrenamiento de un modelo de chat, convirtiendo roles y mensajes en una única secuencia plana de tokens. El entrenamiento y el serving deben usar el mismo renderizado.
_Evitar_: formato de prompt, formato de chat

**Contaminación (contamination)**:
Ejemplos de test que el modelo ya ha visto. La contaminación _propia_ son ejemplos de test que también aparecen, exacta o casi exactamente, en tu conjunto de entrenamiento; la contaminación _heredada_ son ejemplos de test que estaban en el corpus de preentrenamiento del _base model_.
_Evitar_: fuga (di cuál de los dos tipos se quiere decir)

**DoRA**:
Una variante de _LoRA_ que divide cada matriz de pesos congelada en un vector de magnitud, que se entrena directamente, y una dirección, que recibe la actualización de bajo rank y se renormaliza después. En PEFT es una opción de la configuración de LoRA, no un método aparte.
_Evitar_: LoRA con pesos descompuestos (desarróllalo solo una vez y luego di DoRA)

**Doble cuantización (double quantisation)**:
_Cuantización_ de las propias escalas por bloques: las escalas fp32 del primer nivel se agrupan y se almacenan a 8 bits con su propia escala de segundo nivel.
_Evitar_: cuantización anidada, cuantización de 2 bits

**Batch size efectivo (effective batch size)**:
El número de ejemplos cuyos gradientes se promedian en un paso del optimizador: batch size por dispositivo × pasos de acumulación de gradiente × número de dispositivos.
_Evitar_: batch size (cuando se quiere decir el número por dispositivo)

**Gradient checkpointing**:
Conservar solo la entrada de cada bloque durante el paso hacia delante y volver a ejecutar el bloque cuando el paso hacia atrás llega a él, de modo que las activaciones almacenadas crecen aproximadamente con la raíz cuadrada de la profundidad en lugar de linealmente, a cambio de un paso hacia delante adicional por paso de entrenamiento.
_Evitar_: checkpointing (solo, porque un checkpoint de entrenamiento son pesos guardados en disco), recomputación de activaciones

**Held-out set**:
Datos con los que el modelo no se entrena, usados para medir si aprendió la tarea. En este espacio de trabajo tiene dos partes: validación, con la que se eligen los ajustes y los checkpoints, y test, que se toca una sola vez al final.
_Evitar_: conjunto de evaluación, dev set

**Modelo instruct (instruct model)**:
Un _base model_ entrenado además con pares de instrucción y respuesta, y normalmente después con datos de preferencias. Aquí modelo de chat significa lo mismo.
_Evitar_: modelo alineado, modelo asistente

**LoRA**:
Adaptación de bajo rank (low-rank adaptation): un _adapter_ que aprende la actualización de una matriz de pesos como el producto de dos matrices pequeñas, `ΔW = BA`, escalado por `α/r`, mientras la propia matriz permanece congelada.
_Evitar_: adapter (cuando se quiere decir el método concreto), fine-tune de bajo rank

**LoRA alpha**:
El escalar fijo `α` (`lora_alpha`) que escala una actualización _LoRA_ por `α/r`. Lo que fija la escala de la actualización es la razón `α/r`, no cada número por separado.
_Evitar_: factor de escala (eso es `α/r`, no `α`)

**Fusión (merging)**:
Incorporar una actualización _LoRA_ a los pesos base, `W₀ + (α/r)BA`, y descartar la estructura del adapter. Es exacta frente a un base en precisión completa y con pérdida frente a uno cuantizado.
_Evitar_: exportar, hornear

**Serving multi-adapter (multi-adapter serving)**:
Servir varios _adapters_ sobre un mismo base compartido agrupando en lotes peticiones que usan adapters distintos: el cómputo del base se comparte en todo el lote, y la contribución del adapter de cada petición se calcula por separado.
_Evitar_: intercambio de adapters (el enfoque ingenuo que serializa las peticiones)

**NF4**:
NormalFloat, un formato de 4 bits cuyos 16 niveles se espacian para valores distribuidos normalmente alrededor de cero, como los pesos, en lugar de a intervalos iguales como en el int4 simple. Se usa dentro de la _cuantización_ por bloques, sobre bloques ya normalizados por su absmax.
_Evitar_: int4 (un formato distinto, de espaciado uniforme)

**Estado del optimizador (optimiser state)**:
Los tensores que un optimizador mantiene por cada parámetro entrenable además del peso y su gradiente. Para AdamW son el primer y el segundo momento, de 4 bytes cada uno.
_Evitar_: caché del optimizador, momentum (solo el primer momento)

**Packing**:
Concatenar ejemplos de entrenamiento cortos en secuencias de longitud completa, de modo que un lote casi no lleva padding.
_Evitar_: agrupación por longitud (un remedio distinto, que agrupa en lotes secuencias de tamaño similar)

**QLoRA**:
_LoRA_ entrenado contra un base congelado almacenado en _NF4_ con _doble cuantización_, que se descuantiza en cada pasada hacia delante y hacia atrás. Es LoRA con un base más barato, no un método con hiperparámetros propios.
_Evitar_: fine-tuning de 4 bits, LoRA cuantizado (cuando sugiere que el adapter está cuantizado)

**Rank**:
La dimensión interna `r` de las dos matrices de _LoRA_, siendo `A` de `r × d_in` y `B` de `d_out × r`. Es la capacidad del adapter: acota cuán compleja puede ser la actualización que el adapter puede expresar.
_Evitar_: tamaño, dimensión (solo)

**Conjunto de regresión (regression suite)**:
Un conjunto fijo de sondas ajenas a la tarea (seguimiento general de instrucciones, cumplimiento de formato y de comportamiento, seguridad y comportamiento de rechazo, capacidad adyacente), ejecutado antes y después del entrenamiento para detectar el _olvido catastrófico_. Es un instrumento distinto del _held-out set_, y hacen falta ambos.
_Evitar_: benchmark, suite de evaluación (cuando se quiere decir este instrumento concreto)

**Target modules**:
Las matrices de pesos a las que se acopla un _adapter_, nombradas con los nombres de módulo del propio modelo.
_Evitar_: capas (un adapter se acopla a matrices concretas dentro de una capa)
