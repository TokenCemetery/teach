---
title: "15. Precisión mixta a escala: bfloat16 y redondeo estocástico"
description: "Un formato numérico con el rango de fp32 pero menos precisión, y qué cuesta actualizar los parámetros directamente en él"
type: lesson
---

# Lección 15. Precisión mixta a escala: bfloat16 y redondeo estocástico

**Vínculo con la misión:** "Dada una curva de loss, puedes decir si un spike es recuperable o exige reiniciar desde un checkpoint anterior" es la celda "Terminada cuando" de esta etapa en El arco, y empieza por el formato numérico en el que se ejecuta siquiera el entrenamiento. La Lección 16 cubre directamente los loss spikes; la Lección 17 cubre el programa del learning rate.
**Fuente principal:** [Paper: "Scaling Language Models: Methods, Analysis & Insights from Training Gopher", Rae et al., 2021](https://arxiv.org/abs/2112.11446)
**Requisitos previos:** [Lección 14](0014-combining-all-three-when-tensor-and-pipeline-parallelism-earn-their-cost.md)

## Calentamiento

1. ▢ Según Narayanan et al., ¿por qué es mejor confinar el tensor parallelism dentro de un solo nodo, mientras que el pipeline parallelism tolera estar repartido entre nodos?

<details markdown="1"><summary>Comprobación</summary>

El tensor parallelism necesita un all-reduce caro por cada capa, que requiere la interconexión más rápida disponible para seguir siendo eficiente. El pipeline parallelism solo pasa activaciones entre un puñado de límites de etapa, con una comunicación punto a punto mucho más barata que no convierte el cálculo entero en un cuello de botella ni siquiera a través de enlaces más lentos y de más distancia.

</details>

## Qué debes saber

### Dos maneras de meter un número de 32 bits en 16 bits

Un número de coma flotante de 32 bits (`fp32`) reparte sus bits entre un rango (el exponente) y una precisión (la mantisa, los dígitos después del primer uno). Dos formatos distintos de 16 bits lo comprimen de manera diferente. `fp16` conserva 10 bits de mantisa pero solo 5 bits de exponente, y cambia gran parte del rango de `fp32` por precisión extra dentro de un rango más estrecho; un gradiente muy grande o muy pequeño puede desbordarlo por arriba o por abajo. **`bfloat16`** (`bf16`) hace el intercambio contrario: conserva los 8 bits de exponente completos de `fp32`, así que tiene el mismo rango dinámico, pero solo 7 bits de mantisa, así que es más grueso dentro de ese rango. Ese rango más amplio es exactamente por lo que bf16 suele ser más indulgente durante el entrenamiento: es menos probable que los valores grandes o minúsculos que aparecen en los gradientes y las activaciones a escala lo desborden por arriba o por abajo.

### Qué hizo realmente Gopher con él

Rae et al. describen usar bfloat16 específicamente para reducir la memoria y aumentar el rendimiento del entrenamiento, pero no lo aplicaron de forma uniforme en todos los tamaños de modelo que entrenaron. Los modelos de menos de 7.1 mil millones de parámetros se entrenaron con precisión mixta corriente: parámetros `fp32`, activaciones `bf16`. Sus dos modelos más grandes, el de 7.1B y el propio Gopher (280B), fueron más lejos y usaron `bf16` tanto para los parámetros como para las activaciones, y no solo para las activaciones.

### Por qué los parámetros en bf16 necesitan un tratamiento especial

Actualizar directamente un parámetro almacenado en bf16 choca con un problema que el entrenamiento de precisión mixta corriente evita manteniendo una copia maestra `fp32`: la precisión más gruesa de bf16 significa que una actualización pequeña puede simplemente desaparecer al redondearse, si es menor que la distancia entre valores bf16 representables adyacentes cerca del valor actual del parámetro. Rae et al. lo abordan con el **redondeo estocástico**: en lugar de redondear siempre un valor al valor bf16 representable más cercano (lo que descartaría en silencio las actualizaciones pequeñas de una manera sesgada y en una sola dirección), el redondeo estocástico redondea hacia arriba o hacia abajo con una probabilidad proporcional a lo cerca que está el valor verdadero de cada vecino, de modo que una actualización pequeña no se pierde por completo; se conserva en promedio a lo largo de muchos pasos, aunque el redondeo de un solo paso sea aleatorio. Rae et al. son explícitos en que esto no resuelve del todo el problema: informan de que el redondeo estocástico no recupera por completo el rendimiento del entrenamiento de precisión mixta corriente, una limitación honesta y no una solución limpia.

## Práctica

1. ▢ Un valor de gradiente durante el entrenamiento es inusualmente grande, lo bastante como para preocupar por un desbordamiento numérico. ¿Qué formato de 16 bits, fp16 o bf16, tiene más probabilidades de representarlo sin desbordarse, y por qué?

<details markdown="1"><summary>Comprobación</summary>

bf16. Conserva los mismos 8 bits de exponente que fp32, lo que le da el mismo rango dinámico, así que un valor grande que desbordaría el rango de exponente más estrecho de 5 bits de fp16 tiene menos probabilidades de desbordar bf16.

</details>

2. ▢ ¿Por qué actualizar un parámetro almacenado directamente en bf16 (en lugar de mantener una copia maestra fp32) arriesga perder en silencio las actualizaciones pequeñas?

<details markdown="1"><summary>Comprobación</summary>

bf16 tiene solo 7 bits de mantisa, así que es grueso dentro de su rango; una actualización pequeña puede ser menor que la distancia entre valores bf16 representables adyacentes cerca del valor actual del parámetro, y redondear al valor representable más cercano simplemente la descartaría.

</details>

3. ▢ ¿Cómo lo aborda el redondeo estocástico, y qué limitación informaron Rae et al. incluso tras usarlo?

<details markdown="1"><summary>Comprobación</summary>

El redondeo estocástico redondea hacia arriba o hacia abajo con una probabilidad proporcional a lo cerca que está el valor verdadero de cada valor representable vecino, en lugar de redondear siempre al más cercano, de modo que una actualización pequeña se conserva en promedio a lo largo de muchos pasos en lugar de descartarse cada vez. Aun así, Rae et al. encontraron que no recupera por completo el rendimiento del entrenamiento de precisión mixta corriente.

</details>

4. ▢ ¿Cuáles de los tamaños de modelo de Gopher usaron bf16 tanto para los parámetros como para las activaciones, según Rae et al.?

    - a) Todos los tamaños de modelo que entrenaron
    - b) Solo los modelos de menos de 7.1 mil millones de parámetros
    - c) Solo el modelo de 7.1B y el modelo Gopher de 280B
    - d) Ninguno; bf16 se usó solo para las activaciones en todos los tamaños

<details markdown="1"><summary>Comprobación</summary>

**c)** Solo sus dos modelos más grandes. Los modelos de menos de 7.1B usaron precisión mixta corriente, parámetros fp32 con activaciones bf16, según la descripción de (b), por lo que (a) y (d) son ambas incorrectas: las activaciones bf16 se usaron de forma generalizada, pero los parámetros bf16 se reservaron para los dos modelos más grandes.

</details>

## Prácticas en el mundo real

- [ ] Busca dónde expone un framework de entrenamiento al que tengas acceso la elección entre fp16 y bf16 (muchos listan ambos como opciones para el entrenamiento de precisión mixta). Anota qué dice la documentación sobre cuándo preferir uno frente al otro, y contrástalo con el razonamiento sobre rango dinámico de esta lección.
- [ ] Busca la disposición exacta de bits (signo, exponente, mantisa) de fp32, fp16 y bf16, y confirma por ti mismo que bf16 y fp32 comparten la misma anchura de exponente mientras que fp16 no.
- [ ] Mañana: sin adelantarte, escribe una predicción de una oración para la Lección 16: dado que los dos modelos más grandes de Gopher necesitaron el manejo numérico más cuidadoso, ¿esperarías que los loss spikes y las inestabilidades se hicieran más o menos comunes al crecer el tamaño del modelo, y por qué?

## Para profundizar

- [Paper: "Scaling Language Models: Methods, Analysis & Insights from Training Gopher", Rae et al., 2021](https://arxiv.org/abs/2112.11446)
- [Recursos](../RESOURCES.md)

---

¿No termina de quedar claro? Vuelve a leer la fuente primaria de arriba, ya que esta lección la comprime y en la compresión es donde se escapa la comprensión. Consulta el [glosario](../GLOSSARY.md) por si algún término te resultó resbaladizo.

Si lo poco claro es la propia lección y no el material, eso es un defecto: [abre un issue](https://github.com/TokenCemetery/teach/issues).
