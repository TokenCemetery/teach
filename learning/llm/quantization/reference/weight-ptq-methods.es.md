---
title: "Métodos PTQ de pesos"
description: "Round-to-nearest, GPTQ y AWQ lado a lado, y qué hace el calibration set"
type: reference
---

# Métodos PTQ de pesos: comparación de round-to-nearest, GPTQ y AWQ

La etapa 4 comprimida para consulta. La [Lección 9](../lessons/0009-round-to-nearest.md) cubre round-to-nearest (RTN), la [lección 10](../lessons/0010-gptq.md) GPTQ, la [lección 11](../lessons/0011-awq.md) AWQ, y la [lección 12](../lessons/0012-the-calibration-set.md) el calibration set.

## Los tres métodos lado a lado

| | Round-to-nearest | GPTQ | AWQ |
|---|---|---|---|
| Idea | Redondear cada peso a su nivel más cercano | Redondear las columnas en orden, empujando cada error sobre las columnas aún sin redondear | Escalar hacia arriba los canales de entrada salientes antes de redondear, dividir la activación por el mismo scale |
| Qué lee de los datos | Nada | Entradas de la capa, sumadas en `H = 2 X X^T` | Magnitud media de activación por canal, más las salidas de la capa para puntuar cada `alpha` |
| Cambia los valores de los pesos | No | Sí, cada columna posterior tras cada redondeo | Sí, con el scale por canal `s = s_X^alpha`, y luego redondea al más cercano |
| Objetivo | El error propio de cada peso | `argmin \|\| W X - Ŵ X \|\|^2` por capa | El mismo error de salida de la capa, buscado sobre `alpha` en [0, 1] |
| Backpropagation | Ninguna | Ninguna | Ninguna |
| Costo | Despreciable | Unas 4 horas de GPU para 175B parámetros (paper) | Una rejilla de 20 valores de `alpha` por capa (paper) |
| Rejilla | Un scale por fila o por grupo | Fijada antes del bucle; el scale por grupo se fija cuando el bucle llega al grupo | Per-group, 128 en el paper |
| Riesgo principal | Colapsa a 3 bits con scales por fila | Sobreajusta un calibration set pequeño o que no coincide | Escalar demasiado fuerte daña los canales no salientes |

## Qué le hace cada uno a los números

| Perplexity en WikiText-2 | 16 bits | RTN | GPTQ | AWQ |
|---|---|---|---|---|
| OPT-175B, 4 bits, rejilla por fila | 8.34 | 10.54 | 8.37 | no informado allí |
| OPT-175B, 3 bits, rejilla por fila | 8.34 | 7,300 | 8.68 | no informado allí |
| Llama-2 7B, 4 bits, grupos de 128 | 5.47 | 5.73 | 5.69 | 5.60 |
| Llama-2 7B, 3 bits, grupos de 128 | 5.47 | 6.66 | 6.43 | 6.24 |

Las dos primeras filas vienen del paper de GPTQ y las dos últimas del paper de AWQ. Las rejillas y los modelos difieren, así que compara dentro de una fila y la forma entre filas, no los números entre ellas. Cada paper evalúa su propio método frente al otro, así que lee las diferencias como las ejecuciones de los autores.

## Por qué se comporta así el error

| Hecho | Consecuencia |
|---|---|
| Cada bit quitado duplica aproximadamente el paso | El error de round-to-nearest se duplica aproximadamente por bit |
| En el ejemplo de juguete de la lección 9, las razones de error igualan las razones de paso: 127 / 7 = 18.1 de 8 a 4 bits, 7 / 3 = 2.3 de 4 a 3 | Los últimos bits son los caros |
| Round-to-nearest minimiza el error de cada peso, no el error de la salida de la capa | 919 de 2000 redondeos aleatorios lo superan en una capa de juguete correlacionada |
| La ganancia de GPTQ viene de entradas correlacionadas | Con entradas independientes casi desaparece (0.2680 frente a 0.2595 en el ejemplo de juguete) |
| Un peso saliente se elige por su activación, no por su tamaño | En OPT-6.7B a 3 bits, el 1% elegido por activación da 11.39, por tamaño de peso 22.37, round-to-nearest simple 23.54 |
| Escalar un canal por `s` reduce su error relativo en aproximadamente `1 / s` | Un `s` demasiado grande sube el paso de los demás canales del grupo |

## Los tres cambios de escalado de GPTQ y act-order

| Cambio | Qué arregla |
|---|---|
| Mismo orden de columnas para cada fila | Una actualización de la inversa por columna sirve a todas las filas |
| Actualizaciones perezosas por lotes, 128 columnas a la vez | La actualización está limitada por el ancho de banda de memoria, así que agruparla aprovecha la GPU |
| Amortiguación del 1% de la diagonal media, más un factor de Cholesky | El error numérico que puede volver indefinida la inversa |
| Act-order (código de los autores, no el paper): columnas ordenadas por la diagonal de `H`, de mayor a menor | Arregla malos resultados como OPT-66B a 3 bits (de 14.16 a 9.95); puede necesitar cambios en la inferencia salvo que se usen grupos estáticos |

## Qué hace el calibration set

| | GPTQ | AWQ |
|---|---|---|
| Tamaño típico | Paper: 128 segmentos de 2048 tokens, de C4 | AWQ con 16 secuencias supera a GPTQ con 192 en OPT-6.7B, 3 bits (ejecución de los autores) |
| llm-compressor | 128 a 512 muestras es lo típico, empezar con 128 a 256 | El mismo consejo; su ejemplo usa 256 |
| Necesita más datos porque | Estima toda una matriz de covariación de features | Estima una media por canal |
| Penalización por desajuste, OPT-6.7B, 3 bits (paper de AWQ) | 2.3 a 4.9 de perplexity peor | 0.5 a 0.6 peor |

- Round-to-nearest no usa datos. GPTQ y AWQ necesitan un calibration set. Ninguno hace backpropagation a través de él.
- Un calibration set no son datos de entrenamiento, y su dominio se nota en el resultado.
- Haz coincidir el conjunto con el uso previsto: texto general para un modelo general, datos de instrucciones para un modelo de instrucciones, código para un modelo de programación (llm-compressor).
- Evalúa con texto held-out del dominio de calibración y con texto de los otros dominios que sirvas. Una ganancia en uno y una pérdida en el otro es un desajuste.
- Una perplexity medida sobre el texto del que se tomó el conjunto está favorecida. El paper de GPTQ dice que sus resultados en C4 no son del todo zero-shot por esta razón.
- En el ejemplo de juguete de la lección 12, muy pocas muestras (64 para 128 features) hicieron a GPTQ peor que round-to-nearest incluso dentro del dominio.

## Antes de fiarte de un checkpoint PTQ de pesos

- Qué método, qué ancho de bits y qué tamaño de grupo o rejilla.
- Qué calibration set, cuántas muestras y de qué longitud. Si la model card no lo dice, es una laguna.
- Si la perplexity citada es sobre el dominio de calibración.
- Si se midió un baseline sin datos con la misma rejilla en la misma evaluación.
- Para GPTQ con act-order y grupos, si necesita cambios en la inferencia que pueden costar velocidad, o se hizo con grupos estáticos.
