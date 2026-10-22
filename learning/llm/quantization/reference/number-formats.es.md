---
title: "Formatos numéricos"
description: "Disposiciones de bits, rango y precisión de cada formato, y aritmética de memoria"
type: reference
---

# Formatos numéricos: disposiciones, rango, precisión y memoria

La etapa 1 comprimida para consulta. La [Lección 1](../lessons/0001-what-quantization-buys.md) cubre qué aporta la cuantización y la aritmética de la memoria, la [lección 2](../lessons/0002-floating-point-formats.md) los formatos de punto flotante fp32, fp16 y bf16, y la [lección 3](../lessons/0003-low-bit-formats.md) fp8, int8, int4 y los formatos con scale por bloque.

## Leer una disposición de punto flotante

```text
value = (-1)^sign × 2^(e - bias) × (1 + m / 2^M)
```

- `e` es el campo de exponente, `m` el campo de mantisa, `M` el número de bits de mantisa.
- Campo de exponente todo en ceros: cero y valores subnormales, `(m / 2^M) × 2^(1 - bias)`.
- Campo de exponente todo en unos: infinito y NaN en los formatos IEEE. E4M3 es la excepción y lo usa para valores ordinarios.
- Los bits de exponente fijan el rango. Los bits de mantisa fijan la precisión. El épsilon de máquina es `2^-M`.
- Entre `2^k` y `2^(k+1)` los valores vecinos están separados `2^(k-M)`: la distancia se duplica en cada potencia de dos.

## Formatos de punto flotante

|Formato|Bits|Signo / exponente / mantisa|Bias|Mayor valor finito|Menor valor normal|Épsilon de máquina|
|---|---|---|---|---|---|---|
|fp32|32|1 / 8 / 23|127|3.4 × 10^38|1.2 × 10^-38|2^-23, unos 1.2 × 10^-7|
|fp16|16|1 / 5 / 10|15|65,504|6.1 × 10^-5|2^-10, unos 9.8 × 10^-4|
|bf16|16|1 / 8 / 7|127|3.4 × 10^38|1.2 × 10^-38|2^-7, unos 7.8 × 10^-3|
|fp8 E4M3|8|1 / 4 / 3|7|448|2^-6|2^-3|
|fp8 E5M2|8|1 / 5 / 2|15|57,344|2^-14|2^-2|
|FP4 E2M1|4|1 / 2 / 1|1|6|1|2^-1|

- fp16 tiene un menor subnormal de `2^-24`. Los valores más pequeños se vuelven cero.
- El menor subnormal de E4M3 es `2^-9`, el de E5M2 `2^-16`.
- E4M3 no tiene infinitos y tiene un patrón de NaN (S.1111.111). E5M2 sigue IEEE con infinitos y NaN.
- bf16 es fp32 sin los 16 bits inferiores.
- Las filas de E4M3, E5M2 y fp16 salen de las fuentes de las lecciones. La fila de FP4 E2M1 se deriva de su disposición y del bias de 1 que se usa en la lección 3. El épsilon de máquina de las filas de fp8 y FP4 es `2^-M` por la misma regla.

## Qué formato para qué

|Formato|Dónde se ve|Por qué|
|---|---|---|
|fp32|Baseline, y acumulación en precisión mixta|Rango amplio y espaciado fino, 4 bytes|
|fp16|Entrenamiento de precisión mixta con escalado de la pérdida|Espaciado fino, rango estrecho: el entrenamiento necesita escalado de la pérdida|
|bf16|Entrenamiento sin escalado de la pérdida|El rango de fp32, así que no hace falta escalado de la pérdida, mantisa gruesa|
|E4M3|Pesos y activaciones|Espaciado más fino, rango hasta 448|
|E5M2|Gradientes|Rango más amplio, espaciado grueso|

## Rejillas enteras

|Formato|Niveles|Rango|Espaciado|
|---|---|---|---|
|int8|256|-128 a 127|1 en todas partes|
|int4|16|-8 a 7|1 en todas partes|

- Los valores son `scale × integer`. Sin un scale una rejilla entera solo contiene números enteros.
- Una rejilla de punto flotante trae su propio rango y necesita un scale para colocarlo. Una rejilla entera obtiene todo su rango del scale.
- Los valores menores que medio paso se redondean a cero, con scale o sin él.

## Formatos con scale por bloque

|Formato|Tamaño de bloque|Scale|Elemento|Bits del elemento|Bits efectivos por peso|
|---|---|---|---|---|---|
|MXFP8|32|E8M0|E4M3 o E5M2|8|8.25|
|MXFP6|32|E8M0|E2M3 o E3M2|6|6.25|
|MXFP4|32|E8M0|E2M1|4|4.25|
|MXINT8|32|E8M0|int8|8|8.25|
|NVFP4|16|E4M3, más un scale FP32 por tensor|E2M1|4|4.5, ignorando el escalar por tensor|

- El valor de cada elemento es `X × P`: el scale compartido por el elemento almacenado.
- E8M0 es solo un exponente, así que un scale MX es siempre una potencia de dos. Un scale E4M3 en NVFP4 puede ser un múltiplo fraccionario.
- Los valores positivos de E2M1: 0, 0.5, 1, 1.5, 2, 3, 4, 6.
- Un valor grande en un bloque fija el scale de todo el bloque y puede redondear a cero a sus vecinos.
- Los detalles de NVFP4 son del propio blog de NVIDIA, que es documentación del proveedor.

## Aritmética de la memoria

La memoria de pesos en GB es `parameters in billions × effective bits per weight / 8`. Los bits efectivos por peso son el ancho de bits más los bits del scale divididos por el tamaño de grupo o de bloque.

|Formato|Bits efectivos|Modelo de 8B|Modelo de 70B|
|---|---|---|---|
|fp32|32|32 GB|280 GB|
|fp16 o bf16|16|16 GB|140 GB|
|fp8 o int8|8|8 GB|70 GB|
|MXFP4|4.25|4.25 GB|unos 37.2 GB|
|NVFP4|4.5|4.5 GB|unos 39.4 GB|
|int4, scale de 16 bits por 128|4.125|4.125 GB|unos 36.1 GB|
|int4, scale de 16 bits por 32|4.5|4.5 GB|unos 39.4 GB|

- Son solo los pesos. La KV cache y las activaciones se suman encima.
- Sobrecarga del scale: `scale bits / group size`. Un scale de 16 bits por cada 128 pesos añade 0.125 bits, y por cada 32 añade 0.5 bits.
