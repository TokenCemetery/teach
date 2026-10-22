---
title: "11. Memoria de activaciones y ZeRO-R"
description: "Repartir los estados del modelo resuelve un problema de memoria y deja en pie un segundo, las activaciones"
type: lesson
---

# Lección 11. Memoria de activaciones y ZeRO-R

**Vínculo con la misión:** "Explicar qué reparten ZeRO/FSDP, por qué el data parallelism por sí solo se queda sin memoria antes de quedarse sin cómputo, y cuándo el tensor o el pipeline parallelism valen su costo de comunicación" es el cuarto punto de Cómo se ve el éxito. Las Lecciones 9 y 10 cubrieron las tres etapas de ZeRO-DP, que reparten los estados del modelo; esta lección cubre el problema de memoria aparte que esas tres etapas no tocan.
**Fuente principal:** [Paper: "ZeRO: Memory Optimizations Toward Training Trillion Parameter Models", Rajbhandari et al., 2019](https://arxiv.org/abs/1910.02054)
**Requisitos previos:** [Lección 10](0010-zero-stage-3-and-fsdp-partitioning-parameters-too.md), [Activation checkpointing](../GLOSSARY.md)

## Calentamiento

1. ▢ La documentación de FSDP de PyTorch se describe a sí misma como inspirada en qué etapa de ZeRO?

<details markdown="1"><summary>Comprobación</summary>

La etapa 3 de ZeRO (`P_os+g+p`), la etapa que particiona los parámetros además del estado del optimizador y los gradientes.

</details>

2. ▢ ¿Por qué particionar los parámetros (etapa 3) añade comunicación que particionar el estado del optimizador y los gradientes (etapas 1 y 2) no añade?

<details markdown="1"><summary>Comprobación</summary>

Porque el forward y el backward pass de cada dispositivo necesitan todos los parámetros, no solo la porción que posee, así que las porciones que faltan hay que reunirlas bajo demanda desde otros dispositivos, a diferencia del estado del optimizador y los gradientes, que solo necesita el dispositivo que los posee.

</details>

## Qué debes saber

### Resolver los estados del modelo deja en pie un segundo problema

Las Lecciones 9 y 10 cubrieron **ZeRO-DP**: las tres etapas que particionan el estado del optimizador, los gradientes y los parámetros, los 16 bytes por parámetro que contó la Lección 8. Rajbhandari et al. son explícitos en que esa no es toda la imagen de la memoria. Una vez que los estados del modelo dejan de dominar, lo que llaman **memoria residual**, las activaciones que se guardan del forward pass para calcular los gradientes en el backward pass, los buffers temporales y la memoria perdida por fragmentación, pasa a ser el siguiente cuello de botella. El propio ejemplo de GPT-2 de la Lección 8 mostró que no es un efecto pequeño: unos 60 GB de memoria de activaciones con una longitud de secuencia de 1,024 y un batch size de 32, en un modelo cuyos estados del modelo por sí solos sumaban apenas 24 GB. Las tres etapas de ZeRO-DP no hacen nada con esos 60 GB; solo abordan los 24 GB. **ZeRO-R** es la respuesta aparte de Rajbhandari et al. para el lado residual.

### El checkpointing ayuda, pero no basta por sí solo

El activation checkpointing, el término del glosario al que enlaza esta lección, descarta la mayoría de las activaciones intermedias durante el forward pass y las recalcula durante el backward pass en lugar de mantenerlas todas en memoria todo el tiempo, cambiando cómputo extra por menor uso de memoria. Rajbhandari et al. señalan que el checkpointing ayuda pero no es suficiente por sí solo para los modelos más grandes: incluso el conjunto reducido de activaciones que conserva el checkpointing puede seguir siendo grande y, en configuraciones que combinan data parallelism con model parallelism, ese conjunto reducido suele replicarse sin necesidad entre rangos de model parallelism que podrían compartirlo.

### Qué añade ZeRO-R por encima

ZeRO-R ataca la memoria residual en tres frentes, cada uno dirigido a una parte distinta de ella:

- **Partición de activaciones.** Donde el entrenamiento con model parallelism mantendría de otro modo una copia redundante de las mismas activaciones en cada rango de model parallelism, ZeRO-R identifica y elimina esa replicación, particionando las activaciones del mismo modo en que ZeRO-DP particiona los estados del modelo, y además puede **descargar (offload)** las activaciones particionadas a la memoria de la CPU cuando compensa hacer ese intercambio.
- **Buffers temporales de tamaño adecuado.** A los buffers temporales grandes que se usan durante el entrenamiento se les da un tamaño elegido deliberadamente, que equilibra el uso de memoria con la eficiencia computacional, en lugar de dejarlos crecer tanto como permitiría una implementación ingenua.
- **Desfragmentación.** Los tensores con tiempos de vida muy distintos (algunos viven todo un paso de entrenamiento, otros solo un instante) crean memoria fragmentada con el tiempo, lo que puede hacer que falle una asignación de memoria incluso cuando la memoria libre total sería suficiente. ZeRO-R gestiona la memoria de forma proactiva según el tiempo de vida esperado de cada tensor, para evitar que esa fragmentación se acumule.

Combinados, Rajbhandari et al. se refieren a ZeRO-DP y ZeRO-R juntos simplemente como **ZeRO**: una mitad elimina la redundancia en los estados del modelo, la otra controla todo lo demás que el entrenamiento mantiene en memoria.

## Práctica

1. ▢ Un equipo ya aplicó la etapa 3 de ZeRO a un modelo, con lo que redujo la memoria de estados del modelo muy por dentro del presupuesto, pero la ejecución aun así se queda sin memoria durante el forward pass con una longitud de secuencia larga. ¿Es lo más probable un problema de estados del modelo o de memoria residual, y qué se podría hacer para abordarlo?

<details markdown="1"><summary>Comprobación</summary>

Un problema de memoria residual, muy probablemente de memoria de activaciones, que es sensible a la longitud de la secuencia de una manera en que no lo son los estados del modelo. El activation checkpointing, la partición de activaciones o la descarga de activaciones a la CPU son técnicas de memoria residual que podrían abordarlo; añadir más reparto de ZeRO-DP no lo haría, ya que los estados del modelo no eran el cuello de botella aquí.

</details>

2. ▢ ¿Cuál de estas opciones describe mejor por qué se dice que el activation checkpointing por sí solo es insuficiente para los modelos más grandes?

    - a) El checkpointing es incompatible con ZeRO-DP y no se puede usar junto con él
    - b) Incluso el conjunto reducido de activaciones que conserva el checkpointing puede seguir siendo grande, y puede replicarse sin necesidad entre rangos de model parallelism si no hay más optimización
    - c) El checkpointing aumenta el uso de memoria a cambio de menos cómputo
    - d) El checkpointing solo funciona con modelos entrenados sin precisión mixta

<details markdown="1"><summary>Comprobación</summary>

**b)** es el razonamiento del propio paper. (a) es falsa; ZeRO-R se describe como complementario del checkpointing, no como un sustituto que choque con él. (c) invierte la disyuntiva real, que es menos memoria a cambio de más recálculo. (d) no es una restricción que describa el paper.

</details>

3. ▢ Nombra las tres cosas que optimiza ZeRO-R, y empareja cada una con el problema de memoria residual al que apunta: activaciones replicadas sin necesidad entre rangos de model parallelism, una asignación de memoria que falla pese a haber suficiente memoria libre total, y buffers temporales que se dejan crecer más de lo necesario.

<details markdown="1"><summary>Comprobación</summary>

La partición de activaciones (y el offload) aborda las activaciones replicadas entre rangos de model parallelism. La desfragmentación, basada en el tiempo de vida esperado de cada tensor, aborda los fallos de asignación por memoria fragmentada. Los buffers temporales de tamaño adecuado abordan los buffers que crecen más de lo que pediría un equilibrio entre uso de memoria y eficiencia de cómputo.

</details>

## Prácticas en el mundo real

- [ ] Busca dónde se expone el activation checkpointing (a veces llamado gradient checkpointing) como opción en un framework de entrenamiento al que tengas acceso, y anota cuánto cómputo extra cuesta, si la documentación lo indica.
- [ ] Usando el ejemplo de memoria de activaciones de GPT-2 de la Lección 8 (unos 60 GB con longitud de secuencia 1,024 y batch size 32), predice de forma cualitativa qué le pasa a ese número si se duplica la longitud de la secuencia, y contrasta tu predicción con cualquier fórmula o explicación que dé la documentación del framework sobre cómo escala la memoria de activaciones.
- [ ] Mañana: para un modelo y una configuración de hardware a los que tengas acceso (o unos hipotéticos), decide a qué técnica de memoria residual (checkpointing, partición de activaciones, offload a CPU o alguna combinación) recurrirías primero, y escribe una oración sobre por qué, dado lo que sacrifica cada una.

## Para profundizar

- [Paper: "ZeRO: Memory Optimizations Toward Training Trillion Parameter Models", Rajbhandari et al., 2019](https://arxiv.org/abs/1910.02054)
- [Recursos](../RESOURCES.md)

---

La etapa 5 cubrió cómo se reparte la memoria de una ejecución de entrenamiento entre dispositivos que hacen todos el mismo tipo de trabajo. La etapa 6 cubre otro tipo de división: dividir el propio modelo entre dispositivos que hacen cada uno una parte distinta del cálculo.

¿No termina de quedar claro? Vuelve a leer la fuente primaria de arriba, ya que esta lección la comprime y en la compresión es donde se escapa la comprensión. Consulta el [glosario](../GLOSSARY.md) por si algún término te resultó resbaladizo.

Si lo poco claro es la propia lección y no el material, eso es un defecto: [abre un issue](https://github.com/TokenCemetery/teach/issues).
