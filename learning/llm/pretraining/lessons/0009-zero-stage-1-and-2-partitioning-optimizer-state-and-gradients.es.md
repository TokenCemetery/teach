---
title: "9. ZeRO etapas 1 y 2: particionar el estado del optimizador y los gradientes"
description: "Eliminar las copias redundantes del data parallelism gratis, antes de que el costo de comunicación tenga que crecer en absoluto"
type: lesson
---

# Lección 9. ZeRO etapas 1 y 2: particionar el estado del optimizador y los gradientes

**Vínculo con la misión:** "Explicar qué reparten ZeRO/FSDP, por qué el data parallelism por sí solo se queda sin memoria antes de quedarse sin cómputo, y cuándo el tensor o el pipeline parallelism valen su costo de comunicación" es el cuarto punto de Cómo se ve el éxito. Esta lección cubre las dos primeras de las tres etapas de ZeRO; la Lección 10 cubre la tercera.
**Fuente principal:** [Paper: "ZeRO: Memory Optimizations Toward Training Trillion Parameter Models", Rajbhandari et al., 2019](https://arxiv.org/abs/1910.02054)
**Requisitos previos:** [Lección 8](0008-why-data-parallelism-alone-runs-out-of-memory.md)

## Calentamiento

1. ▢ Con Adam de precisión mixta, ¿cuáles son los cinco costos de memoria por parámetro que suman 16 bytes por parámetro?

<details markdown="1"><summary>Comprobación</summary>

Una copia fp16 de los parámetros (2 bytes), una copia fp16 de los gradientes (2 bytes) y una copia fp32 cada una de los parámetros, el momento y la varianza que guarda el optimizador (4 bytes cada una), lo que da 16 bytes en total.

</details>

2. ▢ ¿Reduce el data parallelism corriente alguno de esos 16 bytes por dispositivo al añadir más dispositivos?

<details markdown="1"><summary>Comprobación</summary>

No. Cada dispositivo tiene 16 bytes completos e idénticos por parámetro sin importar cuántos otros dispositivos existan; añadir dispositivos añade más copias redundantes, no una huella menor por dispositivo.

</details>

## Qué debes saber

### La redundancia que elimina ZeRO

La Lección 8 estableció que cada dispositivo con data parallelism tiene una copia completa e idéntica del estado del optimizador, los gradientes y los parámetros. La idea central de ZeRO es que esa redundancia es innecesaria: entre `Nd` dispositivos con data parallelism, solo hace falta que exista en total una copia completa de ese estado, dividida en `Nd` trozos, un trozo por dispositivo, y que cada dispositivo reconstruya o reciba el trozo que no tiene solo en el momento en que de verdad lo necesita. Rajbhandari et al. lo llaman ZeRO-DP, y lo definen como tres etapas que se pueden activar de forma acumulativa, cada una de las cuales particiona un trozo más de los estados del modelo que la anterior.

### Etapa 1: particionar el estado del optimizador

**`P_os`** (partición del estado del optimizador) reparte solo el estado del optimizador, la mayor porción individual de los 16 bytes por parámetro (la copia fp32 de los parámetros, el momento y la varianza: 12 de los 16 bytes), entre los `Nd` dispositivos, de modo que cada dispositivo tiene solo `1/Nd` de él en lugar de todo. Rajbhandari et al. informan de que esto solo ya da una reducción de memoria de 4x, con el **mismo volumen de comunicación que el data parallelism corriente**: no hace falta mover entre dispositivos ningún dato adicional más allá de lo que ya exigía el all-reduce de gradientes, porque el estado del optimizador solo se necesita en local, en el momento en que cada dispositivo aplica su propia porción de la actualización.

### Etapa 2: particionar también los gradientes

**`P_os+g`** añade la partición de gradientes sobre la etapa 1: cada dispositivo solo guarda la porción del gradiente que necesita para actualizar su propia porción del estado del optimizador y de los parámetros, en lugar de tener el gradiente completo de cada parámetro del modelo. Es una extensión natural de la misma idea, ya que un dispositivo que solo posee `1/Nd` del estado del optimizador solo necesita `1/Nd` del gradiente para actualizarlo. Rajbhandari et al. informan de que esto alcanza una reducción de memoria de 8x, de nuevo con el **mismo volumen de comunicación que el data parallelism corriente**: las operaciones reduce-scatter y all-gather en que se reestructura el all-reduce mueven la misma cantidad total de datos que movería un all-reduce estándar, solo que dirigidas al dispositivo que de verdad necesita cada porción en lugar de difundir todo a todos.

### Por qué estas dos etapas son casi un almuerzo gratis

Las dos etapas eliminan redundancia real de memoria sin añadir un costo de comunicación más allá de lo que el data parallelism ya pagaba. Eso es posible porque el estado del optimizador y los gradientes solo los necesita el dispositivo responsable de actualizar la porción correspondiente de parámetros; nada más en el forward o el backward pass necesita leerlos. La etapa 3, que particiona los propios parámetros, no puede hacer la misma afirmación, porque el forward y el backward pass de cada dispositivo necesitan todos los parámetros, no solo los que posee. La Lección 10 cubre lo que eso cuesta.

## Práctica

1. ▢ Un modelo de 7 mil millones de parámetros se entrena con la etapa 1 de ZeRO (`P_os`) en 8 dispositivos con data parallelism. ¿Aproximadamente cuántos bytes por parámetro tiene ahora cada dispositivo para el estado del optimizador, en comparación con los 12 bytes por parámetro (parámetros fp32, momento, varianza) que tendría sin particionar?

<details markdown="1"><summary>Pista</summary>

La etapa 1 reparte el estado del optimizador por igual entre los `Nd` dispositivos.

</details>

<details markdown="1"><summary>Comprobación</summary>

1.5 bytes por parámetro (`12 / 8`), frente a los 12 bytes completos que cada dispositivo tendría de otro modo. Los parámetros fp16 y los gradientes fp16 (4 bytes en total) no se ven afectados por la etapa 1 por sí sola.

</details>

2. ▢ ¿Cuál de estas opciones describe mejor por qué las etapas 1 y 2 de ZeRO no aumentan el volumen de comunicación respecto al data parallelism corriente?

    - a) Se saltan por completo el paso de sincronización de gradientes
    - b) El estado del optimizador y los gradientes solo se necesitan en local, en el dispositivo responsable de la porción correspondiente, así que reestructurar quién tiene qué no requiere mover más datos en total
    - c) Solo funcionan con modelos pequeños, en los que el costo de comunicación no importa
    - d) Comprimen los gradientes antes de enviarlos, cambiando precisión por ancho de banda

<details markdown="1"><summary>Comprobación</summary>

**b)** es el mecanismo real: ningún dispositivo necesita la porción de estado del optimizador o de gradientes de otro durante el forward o el backward pass, solo en su propio paso de actualización. (a) es falsa; la sincronización sigue ocurriendo, solo que reconfigurada en reduce-scatter y all-gather. (c) y (d) describen mecanismos que estas dos etapas no usan.

</details>

3. ▢ Un equipo quiere la mayor reducción de memoria que ZeRO puede ofrecer sin ningún aumento del volumen de comunicación respecto al data parallelism corriente. ¿Qué etapa debería usar, y qué reducción de memoria da?

<details markdown="1"><summary>Comprobación</summary>

La etapa 2 (`P_os+g`), que da una reducción de memoria de 8x con el mismo volumen de comunicación que el data parallelism corriente. La etapa 3 va más lejos en memoria, pero es aquella de la que Rajbhandari et al. informan de un aumento del volumen de comunicación.

</details>

## Prácticas en el mundo real

- [ ] Busca la documentación de la configuración de ZeRO o FSDP de un framework de entrenamiento (las estrategias de reparto de FSDP de PyTorch, o los ajustes de etapa de ZeRO de DeepSpeed) e identifica qué opción de configuración corresponde a la etapa 1 y cuál a la etapa 2.
- [ ] Usando el desglose de 16 bytes por parámetro, calcula la memoria por dispositivo de los estados del modelo para un modelo de 13 mil millones de parámetros con la etapa 2, en 8 dispositivos, y compárala con el mismo modelo sin ninguna partición de ZeRO.
- [ ] Mañana: sin adelantarte, escribe una predicción de una oración para la Lección 10: si el forward y el backward pass de cada dispositivo necesitan todos los parámetros, no solo los que posee, ¿qué tendría que hacer de otra manera un dispositivo que particione los propios parámetros respecto a lo que hacen las etapas 1 y 2?

## Para profundizar

- [Paper: "ZeRO: Memory Optimizations Toward Training Trillion Parameter Models", Rajbhandari et al., 2019](https://arxiv.org/abs/1910.02054)
- [Recursos](../RESOURCES.md)

---

¿No termina de quedar claro? Vuelve a leer la fuente primaria de arriba, ya que esta lección la comprime y en la compresión es donde se escapa la comprensión. Consulta el [glosario](../GLOSSARY.md) por si algún término te resultó resbaladizo.

Si lo poco claro es la propia lección y no el material, eso es un defecto: [abre un issue](https://github.com/TokenCemetery/teach/issues).
