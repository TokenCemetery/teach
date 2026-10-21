---
title: "13. Pipeline parallelism: dividir las capas del modelo"
description: "Asignar capas consecutivas a distintos dispositivos, y el tiempo ocioso que eso cuesta al principio y al final de cada batch"
type: lesson
---

# Lección 13. Pipeline parallelism: dividir las capas del modelo

**Vínculo con la misión:** "Explicar qué reparten ZeRO/FSDP, por qué el data parallelism por sí solo se queda sin memoria antes de quedarse sin cómputo, y cuándo el tensor o el pipeline parallelism valen su costo de comunicación" es el cuarto punto de Cómo se ve el éxito. La Lección 12 cubrió dividir entre dispositivos el cálculo propio de una capa; esta lección cubre dividir en cambio las capas del modelo entre dispositivos.
**Fuente principal:** [Paper: "Efficient Large-Scale Language Model Training on GPU Clusters Using Megatron-LM", Narayanan et al., 2021](https://arxiv.org/abs/2104.04473)
**Requisitos previos:** [Lección 12](0012-tensor-parallelism-splitting-a-layers-matrices.md)

## Calentamiento

1. ▢ En la división del MLP con tensor parallelism, ¿por qué dividir la primera matriz de pesos por sus columnas, y no por sus filas, evita necesitar un paso de sincronización antes de aplicar `GeLU`?

<details markdown="1"><summary>Comprobación</summary>

Una división por columnas divide la dimensión de salida, así que la porción del resultado de cada dispositivo ya es completa y correcta; una división por filas dividiría la dimensión sobre la que se suma, y dejaría a cada dispositivo con solo una suma parcial, y `GeLU` no se puede aplicar correctamente a una suma parcial porque es no lineal.

</details>

## Qué debes saber

### Dividir la profundidad del modelo, no la anchura de una sola capa

El **pipeline parallelism** adopta un tercer enfoque, distinto tanto de ZeRO (etapa 5) como del tensor parallelism (Lección 12): en lugar de dividir lo que calcula una capa cualquiera, reparte las propias capas del modelo entre dispositivos. Para un modelo construido con el mismo bloque transformer repetido muchas veces, esto es directo: a cada dispositivo, o **etapa del pipeline**, se le asigna un tramo igual y contiguo de capas del transformer, y el forward pass de un ejemplo de entrenamiento recorre los dispositivos en secuencia, etapa tras etapa, como una cadena de montaje física lleva una pieza de estación en estación.

### Por qué un batch se divide en micro-batches

Si un batch entero tuviera que pasar por completo por la etapa 1 antes de que la etapa 2 pudiera empezar a trabajar en él, todas las etapas menos una estarían ociosas casi todo el tiempo; no habría nada segmentado en un pipeline. El enfoque de Narayanan et al. divide en cambio un batch en **micro-batches** más pequeños y segmenta su ejecución: mientras la etapa 1 trabaja en el micro-batch 2, la etapa 2 puede estar trabajando a la vez en la salida del micro-batch 1, igual que una cadena de montaje real tiene varias piezas en curso a lo largo de sus estaciones al mismo tiempo, en lugar de terminar una pieza por completo antes de empezar la siguiente.

### La burbuja del pipeline

Incluso con los micro-batches escalonados por el pipeline, hay un tiempo ocioso inevitable al comienzo de un batch, antes de que todas las etapas tengan algo con que trabajar, y al final, cuando el último micro-batch ya ha salido de las primeras etapas y solo las etapas posteriores tienen todavía trabajo por terminar. Narayanan et al. llaman a este tiempo ocioso la **burbuja del pipeline**, y es un costo genuino: cuantas más etapas de pipeline hay, más de este tiempo ocioso se acumula en relación con el cómputo útil, a menos que se usen suficientes micro-batches por batch para mantener el pipeline más lleno durante más tiempo entre el llenado y el vaciado inevitables en cada extremo.

### Por qué el pipelining necesita flushes periódicos

Una sutileza sobre la que Narayanan et al. son cuidadosos: el pipelining ingenuo, ejecutado puramente por rendimiento y sin ninguna otra restricción, puede hacer que el backward pass de un micro-batch vea una versión distinta, ya actualizada, de los pesos de la que usó su propio forward pass, si otros micro-batches más adelante en el pipeline terminaron antes su paso del optimizador. Eso rompe el significado síncrono ordinario de un paso de entrenamiento, en el que se supone que cada ejemplo de un batch ve un único conjunto coherente de pesos a lo largo de su propio forward y backward pass. Para mantener esa garantía con exactitud, Narayanan et al. introducen **pipeline flushes** periódicos: puntos en los que se deja que el pipeline se vacíe por completo y el paso del optimizador de todos los dispositivos ocurre a la vez, sincronizado, antes de que los micro-batches del siguiente batch empiecen a llenar de nuevo el pipeline. Este flush es también donde ocurre realmente la burbuja descrita arriba; es el precio que se paga por mantener una semántica síncrona del optimizador en lugar de dejar que las versiones de los pesos se desvíen entre micro-batches.

## Práctica

1. ▢ Un modelo de 8 capas transformer se divide en 4 etapas de pipeline, de 2 capas cada una. Si un batch entero tuviera que completar por entero la etapa 1 antes de que la etapa 2 pudiera empezar a trabajar, ¿qué pasaría con las etapas 2 a 4 mientras la etapa 1 está trabajando?

<details markdown="1"><summary>Comprobación</summary>

Estarían ociosas, ya que ninguna tendría nada que calcular hasta que la etapa 1 terminara todo el batch y pasara su salida a la siguiente. Este es exactamente el problema que dividir un batch en micro-batches pretende evitar.

</details>

2. ▢ ¿Cuál de estas opciones describe mejor qué es la burbuja del pipeline?

    - a) La memoria extra usada para guardar las activaciones en los límites entre etapas del pipeline
    - b) El tiempo ocioso al principio y al final de un batch, mientras el pipeline se llena o se vacía, que no aporta cómputo útil
    - c) El retraso de comunicación entre un all-reduce de tensor parallelism y la siguiente multiplicación de matrices
    - d) Una pausa deliberada insertada para dejar que los dispositivos se enfríen entre batches

<details markdown="1"><summary>Comprobación</summary>

**b)** es exactamente como la llaman Narayanan et al. (a) describe un costo real del pipelining, pero no la burbuja en concreto. (c) describe una preocupación del tensor parallelism, no del pipeline parallelism. (d) no es una razón real del tiempo ocioso.

</details>

3. ▢ ¿Por qué importan los pipeline flushes periódicos para la corrección, y no solo para el rendimiento?

<details markdown="1"><summary>Pista</summary>

Pregúntate qué podría salir mal en el backward pass de un micro-batch concreto si otros micro-batches más adelante en el pipeline ya hubieran disparado un paso del optimizador.

</details>

<details markdown="1"><summary>Comprobación</summary>

Sin un flush, el backward pass de un micro-batch podría ver una versión distinta, ya actualizada, de los pesos de la que usó su propio forward pass, si otros micro-batches completaron antes su paso del optimizador. Eso rompe la semántica síncrona del optimizador, en la que se pretende que cada ejemplo de un batch vea un único conjunto coherente de pesos a lo largo de su propio forward y backward pass. Un flush deja que el pipeline se vacíe y que el paso del optimizador de todos los dispositivos ocurra a la vez, y preserva esa garantía al costo de la burbuja.

</details>

4. ▢ Un equipo aumenta el número de micro-batches por batch sin cambiar el número de etapas del pipeline. ¿Qué efecto tendría esto en la fracción de tiempo perdida por la burbuja del pipeline?

<details markdown="1"><summary>Comprobación</summary>

Reduciría la fracción de tiempo perdida por la burbuja, ya que el costo fijo de llenado y vaciado se amortiza sobre más cómputo útil de micro-batches entre medias. La burbuja en sí no desaparece, pero pasa a ser una parte menor del tiempo total empleado por batch.

</details>

## Prácticas en el mundo real

- [ ] Dibuja en papel cuatro etapas de pipeline y cuatro micro-batches, y esboza una línea de tiempo que muestre qué etapa trabaja en qué micro-batch en cada paso de tiempo, incluidas las celdas ociosas del principio y del final que representan la burbuja.
- [ ] Lee la sección del paper de Megatron-LM (enlazado arriba) que describe los pipeline flushes, y escribe una oración con tus propias palabras que distinga lo que garantiza un flush de lo que garantiza por sí solo el uso de micro-batches.
- [ ] Mañana: sin adelantarte, escribe una predicción de una oración para la Lección 14: dado que el tensor parallelism necesita un all-reduce por cada capa mientras que el pipeline parallelism solo necesita pasar activaciones entre un puñado de límites de etapa, ¿cuál esperarías que tolerara mejor una conexión de red más lenta y de más distancia entre dispositivos?

## Para profundizar

- [Paper: "Efficient Large-Scale Language Model Training on GPU Clusters Using Megatron-LM", Narayanan et al., 2021](https://arxiv.org/abs/2104.04473)
- [Recursos](../RESOURCES.md)

---

¿No termina de quedar claro? Vuelve a leer la fuente primaria de arriba, ya que esta lección la comprime y en la compresión es donde se escapa la comprensión. Consulta el [glosario](../GLOSSARY.md) por si algún término te resultó resbaladizo.

Si lo poco claro es la propia lección y no el material, eso es un defecto: [abre un issue](https://github.com/TokenCemetery/teach/issues).
