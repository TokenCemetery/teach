---
title: "Formatos Numéricos"
description: "Layouts de bits, faixa e precisão de cada formato, e a aritmética de memória"
type: reference
---

# Formatos Numéricos: Layouts, Faixa, Precisão e Memória

A etapa 1 comprimida para consulta. A [lição 1](../lessons/0001-what-quantization-buys.md) cobre o que a quantização oferece e a aritmética de memória, a [lição 2](../lessons/0002-floating-point-formats.md) os formatos de ponto flutuante fp32, fp16 e bf16, e a [lição 3](../lessons/0003-low-bit-formats.md) fp8, int8, int4 e os formatos com escala por bloco.

## Lendo um layout de ponto flutuante

```text
value = (-1)^sign × 2^(e - bias) × (1 + m / 2^M)
```

- `e` é o campo do expoente, `m` o campo da mantissa e `M` o número de bits de mantissa.
- Campo do expoente todo em zeros: zero e valores subnormais, `(m / 2^M) × 2^(1 - bias)`.
- Campo do expoente todo em uns: infinito e NaN nos formatos IEEE. O E4M3 é a exceção e o usa para valores comuns.
- Os bits de expoente definem a faixa. Os bits de mantissa definem a precisão. O epsilon de máquina é `2^-M`.
- Entre `2^k` e `2^(k+1)`, valores vizinhos ficam a `2^(k-M)` de distância: o espaçamento dobra a cada potência de dois.

## Formatos de ponto flutuante

|Formato|Bits|Sinal / expoente / mantissa|Bias|Maior finito|Menor normal|Epsilon de máquina|
|---|---|---|---|---|---|---|
|fp32|32|1 / 8 / 23|127|3.4 × 10^38|1.2 × 10^-38|2^-23, cerca de 1.2 × 10^-7|
|fp16|16|1 / 5 / 10|15|65.504|6.1 × 10^-5|2^-10, cerca de 9.8 × 10^-4|
|bf16|16|1 / 8 / 7|127|3.4 × 10^38|1.2 × 10^-38|2^-7, cerca de 7.8 × 10^-3|
|fp8 E4M3|8|1 / 4 / 3|7|448|2^-6|2^-3|
|fp8 E5M2|8|1 / 5 / 2|15|57.344|2^-14|2^-2|
|FP4 E2M1|4|1 / 2 / 1|1|6|1|2^-1|

- O fp16 tem um menor subnormal de `2^-24`. Valores menores viram zero.
- O menor subnormal do E4M3 é `2^-9` e o do E5M2 é `2^-16`.
- O E4M3 não tem infinitos e tem um único padrão de NaN (S.1111.111). O E5M2 segue o IEEE, com infinitos e NaNs.
- O bf16 é o fp32 com os 16 bits baixos removidos.
- As linhas do E4M3, do E5M2 e do fp16 vêm das fontes da lição. A linha do FP4 E2M1 é derivada do seu layout e do bias de 1 usado na lição 3. O epsilon de máquina das linhas do fp8 e do FP4 é `2^-M` pela mesma regra.

## Qual formato para quê

|Formato|Visto em|Por quê|
|---|---|---|
|fp32|Baseline, e acumulação em precisão mista|Faixa larga e espaçamento fino, 4 bytes|
|fp16|Treinamento em precisão mista com loss scaling|Espaçamento fino, faixa estreita: o treinamento precisa de loss scaling|
|bf16|Treinamento sem loss scaling|A faixa do fp32, então sem loss scaling, mantissa grosseira|
|E4M3|Pesos e ativações|Espaçamento mais fino, faixa até 448|
|E5M2|Gradientes|Faixa mais larga, espaçamento grosseiro|

## Grades de inteiros

|Formato|Níveis|Faixa|Espaçamento|
|---|---|---|---|
|int8|256|-128 a 127|1 em toda parte|
|int4|16|-8 a 7|1 em toda parte|

- Os valores são `scale × inteiro`. Sem uma scale, uma grade de inteiros só comporta números inteiros.
- Uma grade de ponto flutuante traz a sua própria faixa e precisa de uma scale para posicioná-la. Uma grade de inteiros recebe toda a sua faixa da scale.
- Valores menores que meio passo arredondam para zero, com ou sem uma scale.

## Formatos com escala por bloco

|Formato|Tamanho do bloco|Scale|Elemento|Bits do elemento|Bits efetivos por peso|
|---|---|---|---|---|---|
|MXFP8|32|E8M0|E4M3 ou E5M2|8|8.25|
|MXFP6|32|E8M0|E2M3 ou E3M2|6|6.25|
|MXFP4|32|E8M0|E2M1|4|4.25|
|MXINT8|32|E8M0|int8|8|8.25|
|NVFP4|16|E4M3, mais uma scale FP32 por tensor|E2M1|4|4.5, escalar por tensor ignorado|

- O valor de cada elemento é `X × P`: a scale compartilhada vezes o elemento armazenado.
- O E8M0 é só um expoente, então uma scale MX é sempre uma potência de dois. Uma scale E4M3 no NVFP4 pode ser um múltiplo fracionário.
- Os valores positivos do E2M1: 0, 0.5, 1, 1.5, 2, 3, 4, 6.
- Um valor grande em um bloco define a scale do bloco inteiro e pode arredondar os seus vizinhos para zero.
- Os detalhes do NVFP4 vêm do próprio post de blog da NVIDIA, que é documentação de fornecedor.

## Aritmética de memória

A memória dos pesos em GB é `parâmetros em bilhões × bits efetivos por peso / 8`. Os bits efetivos por peso são a largura em bits mais os bits da scale divididos pelo tamanho do grupo ou do bloco.

|Formato|Bits efetivos|Modelo de 8B|Modelo de 70B|
|---|---|---|---|
|fp32|32|32 GB|280 GB|
|fp16 ou bf16|16|16 GB|140 GB|
|fp8 ou int8|8|8 GB|70 GB|
|MXFP4|4.25|4.25 GB|cerca de 37.2 GB|
|NVFP4|4.5|4.5 GB|cerca de 39.4 GB|
|int4, scale de 16 bits por 128|4.125|4.125 GB|cerca de 36.1 GB|
|int4, scale de 16 bits por 32|4.5|4.5 GB|cerca de 39.4 GB|

- Isto considera só os pesos. O KV cache e as ativações vêm por cima.
- Overhead da scale: `bits da scale / tamanho do grupo`. Uma scale de 16 bits por 128 pesos acrescenta 0.125 bit, e por 32 acrescenta 0.5 bit.
