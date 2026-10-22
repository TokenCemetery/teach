---
title: "Batching"
description: "Batching estático frente a continuo, scheduling de solicitudes y el compromiso entre throughput y latencia que una configuración tiene que defender"
type: reference
---

# Batching

Cómo convierte un servidor la capacidad de la [KV cache](kv-cache.md) en throughput servido. Pensado para consultar al ajustar o defender una configuración de batching.

<a id="static-batching-wastes-capacity-on-uneven-finish-times"></a>

## El batching estático desperdicia capacidad con tiempos de finalización desiguales

El tráfico de memoria de un paso de decode (leer los pesos y la caché de cada secuencia residente) apenas cambia tanto si calcula el siguiente token de una secuencia como el de varias a la vez, así que agrupar en lotes los pasos de decode es casi throughput gratis. El **batching estático** agrupa un conjunto fijo de solicitudes y ejecuta pasos de decode hasta que termina la más larga; toda secuencia que termina antes sigue ocupando un slot, sin hacer nada, hasta que acaba todo el grupo.

```text
total slot-steps  = batch size × steps until the longest sequence finishes
useful slot-steps = sum of each request's actual length
wasted fraction   = (total − useful) / total
```

**Ejemplo resuelto**, cuatro solicitudes que necesitan 10, 20, 30 y 100 tokens de salida:

```text
total:  4 × 100 = 400 slot-steps
useful: 10 + 20 + 30 + 100 = 160 slot-steps
wasted: (400 − 160) / 400 = 60%
```

El desperdicio crece con la dispersión entre las longitudes de las solicitudes, que es el caso normal.

## El batching continuo elimina el límite del lote

El **batching continuo** (scheduling a nivel de iteración) planifica al nivel de un solo paso de decode en lugar de un grupo fijo: en el instante en que una secuencia termina, se libera su slot y se admite una solicitud en espera en el paso siguiente. Lo que se mantiene aproximadamente constante es el tamaño del lote, no la vida de una solicitud concreta. La ganancia no es un cálculo más rápido por paso; son menos slot-steps gastados en secuencias a las que no les quedaba nada por hacer.

<a id="admission-order-and-head-of-line-blocking"></a>

## Orden de admisión y head-of-line blocking

La política de admisión por defecto es **first-come, first-served (FCFS)**: simple, y justa en el sentido de que ninguna solicitud espera detrás de una que llegó más tarde. Pero toda secuencia que comparte un paso de lote avanza junta, así que admitir el trabajo de prefill de una solicitud nueva en el paso siguiente está bien cuando el prompt es corto y es dañino cuando es largo: un prefill grande metido en un paso domina la latencia de ese paso, y todas las demás secuencias, incluso las que solo necesitaban un paso de decode rápido, esperan por él. Eso es **head-of-line blocking**: la cola está bien, pero lo que se ejecuta ahora no. FCFS por sí solo ni causa ni arregla esto; solo decide quién se admite, no cuánto de su prefill cae en un paso.

El **chunked prefill** divide el prefill de un prompt grande en piezas intercaladas con los pasos de decode en curso del lote, de modo que cada paso admite solo una cantidad acotada de trabajo nuevo de prefill. El prefill de la propia solicitud nueva tarda más pasos en terminar; ninguna otra secuencia del lote se detiene esperándolo. El tamaño final de la caché de un prompt procesado por completo no cambia, solo cómo se reparte en el tiempo el trabajo para llegar a él.

<a id="the-throughputlatency-trade-off"></a>

## El compromiso entre throughput y latencia

Añadir otra secuencia a un lote aumenta el throughput (se producen más tokens por segundo, agregados en el lote) y aumenta la latencia por token (toda secuencia de un paso avanza junta, así que un paso mayor tarda más). Se mueven juntos, no en contra uno del otro de forma independiente.

| Régimen | Cuello de botella | Efecto de añadir otra secuencia |
|---|---|---|
| Lote pequeño | Limitado por el ancho de banda de memoria, igual que el decode simple | El throughput sube aproximadamente de forma lineal; la latencia apenas se mueve |
| Lote grande | Limitado por cómputo | La latencia sube de forma notable; cada secuencia añadida compra menos throughput que la anterior |

**Ejemplo resuelto**, un stack evaluado con cuatro tamaños de lote:

| Tamaño de lote | Latencia por token |
|---|---|
| 8 | 15 ms |
| 32 | 25 ms |
| 64 | 45 ms |
| 128 | 90 ms |

<a id="defending-a-configuration"></a>

## Defender una configuración

El tamaño de lote defendido es el mayor que satisface las dos restricciones independientes, la que limite más:

- **Un presupuesto de latencia**: un techo declarado para la latencia entre tokens.
- **El techo de capacidad**: [el máximo derivado de la memoria de la KV cache](kv-cache.md#capacity-budget), que no dice nada sobre la latencia.

```text
defended batch size = min(largest batch size within the latency budget,
                          capacity ceiling)
```

**Ejemplo resuelto**, presupuesto de 30 ms/token, con la tabla anterior:

```text
largest batch within budget: 32 (25 ms/token); 64 and 128 exceed 30 ms

capacity ceiling 100 -> defended size 32, latency budget binds
capacity ceiling 20  -> defended size 20, capacity binds instead
```

Un tamaño de lote elegido muy por debajo de ambas restricciones (digamos, 8 cuando 32 aún cumpliría el presupuesto) no es incorrecto, pero deja sobre la mesa throughput que el presupuesto podría haberse permitido.

## Relacionado

- [Lección 4](../lessons/0004-static-vs-continuous-batching.md), [Lección 5](../lessons/0005-request-scheduling.md), [Lección 6](../lessons/0006-throughput-latency-tradeoff.md)
- [KV cache](kv-cache.md): el techo de capacidad del que depende la fórmula de configuración defendida de esta hoja
