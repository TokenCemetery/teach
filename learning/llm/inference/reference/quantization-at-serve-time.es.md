---
title: "Cuantización al servir"
description: "Cuantización de pesos int8/int4/GPTQ/AWQ, por qué la memoria, la velocidad y la precisión no se mueven juntas, y un marco de decisión para elegir un esquema"
type: reference
---

# Cuantización al servir

La cuantización de pesos como palanca de serving, independiente de la precisión de la [KV cache](kv-cache.md). Pensado para consultar al elegir o defender un esquema.

## Esquemas

| Esquema | Ancho de bits | Mecanismo | Precisión con este ancho |
|---|---|---|---|
| int8 | 8 | Redondeo al más cercano | Normalmente bien de forma ingenua |
| int4, ingenuo | 4 | Redondeo al más cercano | Se degrada bruscamente: solo 16 valores representables por peso, frente a los 256 de int8 |
| GPTQ | 3-4 | Cuantiza una columna a la vez; tras cada columna, ajusta los pesos restantes aún no cuantizados de esa capa para compensar, usando información de sensibilidad de segundo orden | Corrige el error a posteriori, columna por columna |
| AWQ | 3-4 | Una pasada de calibración encuentra los canales de pesos que ven las mayores magnitudes de activación; escala esos canales para protegerlos antes de cuantizar nada | Protege de antemano los pesos probablemente sensibles |

GPTQ y AWQ apuntan al mismo resultado, un modelo preciso con pesos de 4 bits, con un momento opuesto: GPTQ compensa el error ya introducido; AWQ lo previene en los canales que la calibración marca como sensibles.

## La memoria es el eje predecible; la velocidad y la precisión no

```text
memory ≈ fp16 footprint / (16 / bit_width)      # int8 halves it, int4 quarters it
```

**Ejemplo resuelto**, un modelo de 14 GB en fp16: int8 son unos 7 GB, int4 unos 3.5 GB. Esta proporción se cumple sin importar qué esquema (ingenuo, GPTQ, AWQ) produjo los pesos cuantizados, y sin importar el ancho de bits más allá de eso.

La velocidad **no** sigue la proporción de memoria:

- A menudo hay que **descuantizar** un peso cuantizado a una precisión mayor justo antes de que se ejecute la multiplicación de matrices, ya que el hardware de multiplicación espera esa precisión. Si ese paso de descuantización cuesta tiempo, la aceleración en tiempo real queda por debajo de la proporción de memoria, a menos que el kernel del stack de serving opere directamente sobre el formato cuantizado.
- El decode (limitado por el ancho de banda de memoria) es donde compensa una huella de pesos menor: menos que leer, menos tiempo leyéndolo. El prefill (limitado por cómputo) gasta su tiempo en la propia multiplicación de matrices, no en leer pesos repetidamente, así que la misma cuantización compra al prefill mucha menos aceleración, a veces casi ninguna.

La precisión necesita una cifra medida, no una impresión a partir de salidas de muestra: la **perplejidad** (perplexity, lo bien que el modelo predice texto held-out; más alta es peor) frente al modelo sin cuantizar, o una diferencia de puntuación en un benchmark específico de la tarea. Una salida fluida no es evidencia de que la precisión se haya mantenido.

| Paso | Memoria | Velocidad | Precisión |
|---|---|---|---|
| fp16 a int8 | Se reduce a la mitad | Sigue razonablemente bien a la memoria | Costo pequeño, normalmente tolerable |
| int8 a int4 | Se reduce a la mitad otra vez | Depende de la sobrecarga de descuantización y del soporte del kernel | Crece desproporcionadamente más que en el paso a int8, que es por lo que existen GPTQ/AWQ |

Ninguno de los tres ejes se mueve al unísono con los otros, por lo que una elección defendible necesita una cifra para cada uno.

<a id="picking-a-scheme-name-the-binding-constraint-first"></a>

## Elegir un esquema: nombra primero la restricción que limita

La cuantización es una solución para una restricción que fp16 no cumple, no un paso por defecto. Si fp16 ya cabe en el presupuesto de memoria y cumple el presupuesto de latencia, cuantizar no compra nada necesario a un costo real de precisión.

| Restricción que limita | Qué hacer |
|---|---|
| Memoria: los pesos más la [capacidad de KV cache](kv-cache.md#capacity-budget) requerida no caben | Cuantiza lo justo para que quepan: primero int8 (el menor costo de precisión), int4 con GPTQ o AWQ solo si int8 por sí solo sigue sin dejar espacio |
| Latencia: el modelo cabe, pero el decode incumple el presupuesto | int8 o int4 pueden ayudar, ya que el decode está limitado por el ancho de banda de memoria, pero mide la aceleración real en lugar de suponerla a partir del ancho de bits |
| Precisión: no se puede cruzar un techo de benchmark o de perplejidad | No descarta la cuantización, pero descarta elegir un esquema solo por memoria o velocidad: mide GPTQ frente a AWQ para este modelo concreto, ya que se comportan de forma distinta según el modelo |

**Ejemplo resuelto**: los pesos en fp16 de un modelo ocupan 70 GB en una GPU de 80 GB, y quedan 10 GB para la caché y la sobrecarga, muy poco para una concurrencia significativa. Esa es una restricción de memoria. Cuantizar a int8 baja los pesos a ~35 GB, liberando ~45 GB para la caché, lo que eleva sustancialmente el [techo de capacidad](kv-cache.md#capacity-budget). Si int8 por sí solo ya satisface los objetivos de capacidad y de latencia, bajar aún más a int4 compra memoria que nadie necesita a un costo real y medido de precisión: cuantizar más allá de la restricción que limita es el mismo error que cuantizar cuando fp16 ya cabía.

<a id="defending-the-choice-means-citing-three-numbers"></a>

## Defender la elección significa citar tres cifras

1. **La cifra de memoria** que hizo necesaria la cuantización, o la que muestra que no lo era.
2. **La cifra de precisión** medida para el esquema elegido con el ancho de bits elegido: una diferencia de perplejidad o un cambio de puntuación en un benchmark frente al modelo sin cuantizar.
3. **La cifra de velocidad** realmente medida para la fase que cubre el presupuesto (el decode, en la mayoría de los casos limitados por latencia), ya que la ganancia en tiempo real no sigue automáticamente la proporción de memoria.

Una elección defendida con solo una de estas ("int4 con AWQ da el mayor ahorro de memoria") no está defendida: deja sin examinar los otros dos ejes, y si hacía falta siquiera tanto ancho de bits.

## Relacionado

- [Lección 7](../lessons/0007-quantization-schemes.md), [Lección 8](../lessons/0008-accuracy-speed-memory-tradeoffs.md), [Lección 9](../lessons/0009-picking-a-quantization-scheme.md)
- [KV cache](kv-cache.md): el techo de capacidad frente al que se mide una decisión de cuantización limitada por memoria
