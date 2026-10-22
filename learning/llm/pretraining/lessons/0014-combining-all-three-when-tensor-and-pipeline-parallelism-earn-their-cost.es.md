---
title: "14. Combinar los tres: cuándo el tensor y el pipeline parallelism se ganan su costo"
description: "Hacer coincidir cada estrategia de paralelismo con la interconexión que tolera, y cuándo el reparto por sí solo no basta"
type: lesson
---

# Lección 14. Combinar los tres: cuándo el tensor y el pipeline parallelism se ganan su costo

**Vínculo con la misión:** "Explicar qué reparten ZeRO/FSDP, por qué el data parallelism por sí solo se queda sin memoria antes de quedarse sin cómputo, y cuándo el tensor o el pipeline parallelism valen su costo de comunicación" es el cuarto punto de Cómo se ve el éxito, y esta lección es donde se cierra: cuándo la ingeniería extra del tensor y el pipeline parallelism merece siquiera la pena.
**Fuente principal:** [Paper: "Efficient Large-Scale Language Model Training on GPU Clusters Using Megatron-LM", Narayanan et al., 2021](https://arxiv.org/abs/2104.04473)
**Requisitos previos:** [Lección 13](0013-pipeline-parallelism-splitting-the-models-layers.md)

## Calentamiento

1. ▢ ¿Qué es la burbuja del pipeline, y qué intercambia un pipeline flush frente a ella?

<details markdown="1"><summary>Comprobación</summary>

La burbuja del pipeline es el tiempo ocioso al principio y al final de un batch, mientras el pipeline se llena o se vacía. Un pipeline flush deja que el pipeline se vacíe y sincroniza el paso del optimizador de todos los dispositivos, que es lo que causa la burbuja; la alternativa arriesgaría que el backward pass de un micro-batch viera una versión de los pesos distinta de la que usó su forward pass.

</details>

2. ▢ En la división del MLP con tensor parallelism, ¿cuántas operaciones all-reduce necesita el bloque entero, y dónde ocurre?

<details markdown="1"><summary>Comprobación</summary>

Una, después de la segunda multiplicación de matrices, que combina la suma parcial de cada dispositivo en el resultado completo.

</details>

## Qué debes saber

### Tres ejes, combinados

Narayanan et al. llaman **PTD-P** a combinar a la vez los tres, tensor parallelism, pipeline parallelism y data parallelism. Cada eje divide una cosa distinta: el tensor parallelism divide lo que calcula una sola capa (Lección 12), el pipeline parallelism divide de qué capas es responsable un dispositivo (Lección 13), y el data parallelism (Lecciones 7 y 8, repartido además opcionalmente con ZeRO, Lecciones 9 a 11) divide el batch entre réplicas de la configuración de tensor y pipeline parallelism que se esté replicando. Combinados así, Narayanan et al. informan de haber entrenado un modelo de un billón de parámetros a 502 petaFLOP/s en 3,072 GPUs, con cada GPU sosteniendo el 52% de su rendimiento máximo teórico, una fracción realmente grande de mantener a esa escala.

### Por qué la división sigue a la interconexión, y no solo al modelo

Narayanan et al. dan una razón práctica y directa de cómo asignan los dispositivos a cada eje: el all-reduce del tensor parallelism, necesario una vez por capa como describió la Lección 12, es lo bastante caro como para rendir mejor confinado a dispositivos conectados por la interconexión más rápida posible, dentro de un solo nodo (sus propios experimentos usan un servidor DGX A100 de 8 GPUs). El pipeline parallelism, en cambio, solo pasa activaciones entre un puñado de límites de etapa, con una comunicación punto a punto que Narayanan et al. describen como "mucho más barata", y que tolera estar repartida entre nodos separados sin que el cálculo entero se convierta en un cuello de botella, al costo de la burbuja que cubrió la Lección 13. Informan del rendimiento máximo precisamente cuando el tamaño de tensor parallelism coincide con el número de GPUs de un solo nodo, lo que confirma que no es un detalle incidental: es la configuración a la que, según sus propios resultados, hay que apuntar.

### Por qué no usar ZeRO en todas partes y evitar la ingeniería extra

El paper de ZeRO de Rajbhandari et al. plantea su propio argumento de forma directa: para el propósito concreto de hacer caber un modelo grande en memoria, ZeRO-DP (Lecciones 9 a 11) es al menos tan eficaz como el model parallelism, a veces más, con una eficiencia de escalado comparable o mejor, y mucho más fácil de aplicar: el data parallelism, señalan, se puede usar de forma amplia en distintas cargas de trabajo sin cambios, mientras que los enfoques de model parallelism como el tensor y el pipeline parallelism suelen exigir trabajo real de ingeniería, revisar el propio modelo y construir para él operadores distribuidos. El tensor y el pipeline parallelism no son alternativas gratuitas al reparto; cuestan esfuerzo real de desarrollo además de su costo de comunicación.

Si se juntan las posiciones de los dos papers, la respuesta práctica a "cuándo vale su costo el tensor o el pipeline parallelism" es: recurre primero al reparto al estilo de ZeRO, ya que resuelve el problema de memoria con el mínimo esfuerzo de ingeniería y sin trabajo específico del modelo. Recurre al tensor y al pipeline parallelism concretamente cuando una ejecución de entrenamiento necesita escalar más allá de lo que el reparto por sí solo maneja con eficiencia, normalmente con un número de dispositivos y un tamaño de modelo en los que la sobrecarga de comunicación de los propios all-gathers del reparto se convierte en el cuello de botella, o en los que los pesos reconstruidos de una sola capa siguen siendo demasiado grandes para un dispositivo incluso tras el reparto. En ese punto, la combinación se elige deliberadamente para hacer coincidir el patrón de comunicación con la interconexión: los all-reduce frecuentes y caros del tensor parallelism confinados dentro de un nodo, las transferencias punto a punto poco frecuentes y baratas del pipeline parallelism a través de los nodos, y el data parallelism (repartido o no) completando el número de dispositivos que quede.

## Práctica

1. ▢ Un equipo tiene 64 GPUs dispuestas en 8 nodos de 8 GPUs cada uno, con una interconexión rápida dentro del nodo y enlaces entre nodos mucho más lentos. Siguiendo la propia configuración de rendimiento máximo que informan Narayanan et al., ¿cómo asignarían los grados de tensor parallelism y de pipeline parallelism a este hardware?

<details markdown="1"><summary>Comprobación</summary>

Un tamaño de tensor parallelism de 8, que coincide con las GPUs de un nodo y se mantiene fuera de los enlaces más lentos entre nodos; etapas del pipeline que abarquen los 8 nodos, ya que la comunicación punto a punto del pipeline parallelism tolera la conexión más lenta entre nodos sin que el cálculo se convierta en un cuello de botella.

</details>

2. ▢ Según el propio argumento del paper de ZeRO, ¿por qué podría un equipo elegir ZeRO-DP en lugar del tensor o el pipeline parallelism, aunque ambos escalan a modelos muy grandes?

    - a) ZeRO-DP es siempre más rápido, con cualquier número de dispositivos, para cualquier modelo
    - b) ZeRO-DP logra una eficiencia de memoria comparable o mejor sin requerir el trabajo de ingeniería específico del modelo (código del modelo revisado, operadores distribuidos) que necesitan los enfoques de model parallelism
    - c) El tensor y el pipeline parallelism no pueden hacer caber modelos mayores que la memoria de un solo dispositivo
    - d) ZeRO-DP elimina por completo la necesidad de cualquier forma de paralelismo

<details markdown="1"><summary>Comprobación</summary>

**b)** es el argumento que plantea el propio paper de ZeRO: una eficiencia de escalado comparable o mejor, con mucho menos costo de ingeniería, ya que el data parallelism es ampliamente aplicable sin cambios específicos del modelo. (a) exagera una ventaja universal de velocidad que el paper no afirma. (c) es lo contrario del punto de ambos papers, que el model parallelism existe precisamente para hacer caber modelos mayores. (d) contradice que ZeRO-DP se apoya en el data parallelism como su base.

</details>

3. ▢ Dado el razonamiento de esta lección, nombra una situación concreta en la que recurrir al tensor o al pipeline parallelism, pese a su costo añadido de ingeniería, seguiría siendo la decisión correcta frente a ZeRO-DP por sí solo.

<details markdown="1"><summary>Comprobación</summary>

Cualquier respuesta en esta línea es defendible: cuando la sobrecarga de comunicación del propio reparto se convierte en el cuello de botella con números de dispositivos muy grandes, o cuando los parámetros de una sola capa siguen siendo demasiado grandes para caber en un dispositivo incluso tras el reparto de ZeRO y la reconstrucción bajo demanda, lo que obliga a dividir entre dispositivos el cálculo en sí, y no solo su almacenamiento.

</details>

## Prácticas en el mundo real

- [ ] Busca una configuración de entrenamiento publicada de un modelo abierto grande (un informe técnico o una ficha de modelo que indique su configuración de paralelismo) e identifica qué partes, si las hay, corresponden al tensor parallelism, al pipeline parallelism y al data parallelism o al reparto de ZeRO.
- [ ] Lee el párrafo del paper de Megatron-LM (enlazado arriba) que describe por qué el tensor parallelism se confina dentro de un nodo, y escribe una oración que lo contraste con el argumento del paper de ZeRO a favor de preferir el data parallelism siempre que sea posible.
- [ ] Mañana: para un clúster hipotético a tu elección (elige cualquier número de nodos y de GPUs por nodo), esboza un plan de paralelismo: qué iría dentro de un nodo, qué cruzaría nodos y dónde encajaría el reparto de ZeRO, y escribe una oración que defienda cada elección.

## Para profundizar

- [Paper: "Efficient Large-Scale Language Model Training on GPU Clusters Using Megatron-LM", Narayanan et al., 2021](https://arxiv.org/abs/2104.04473)
- [Paper: "ZeRO: Memory Optimizations Toward Training Trillion Parameter Models", Rajbhandari et al., 2019](https://arxiv.org/abs/1910.02054)
- [Recursos](../RESOURCES.md)

---

La etapa 6 cubrió cómo se divide el cómputo entre dispositivos, ajustado a lo que puede soportar la interconexión entre ellos. La etapa 7 se vuelve hacia otro tipo de falla a escala: la numérica de la propia ejecución de entrenamiento, y qué hacer cuando la curva de loss deja de comportarse.

¿No termina de quedar claro? Vuelve a leer la fuente primaria de arriba, ya que esta lección la comprime y en la compresión es donde se escapa la comprensión. Consulta el [glosario](../GLOSSARY.md) por si algún término te resultó resbaladizo.

Si lo poco claro es la propia lección y no el material, eso es un defecto: [abre un issue](https://github.com/TokenCemetery/teach/issues).
