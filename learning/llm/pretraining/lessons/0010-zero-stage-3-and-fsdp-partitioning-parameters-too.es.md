---
title: "10. ZeRO etapa 3 y FSDP: particionar también los parámetros"
description: "Repartir los propios parámetros obliga a reconstruirlos bajo demanda, y eso es lo primero que cuesta"
type: lesson
---

# Lección 10. ZeRO etapa 3 y FSDP: particionar también los parámetros

**Vínculo con la misión:** "Explicar qué reparten ZeRO/FSDP, por qué el data parallelism por sí solo se queda sin memoria antes de quedarse sin cómputo, y cuándo el tensor o el pipeline parallelism valen su costo de comunicación" es el cuarto punto de Cómo se ve el éxito. La Lección 9 cubrió las dos etapas que particionan gratis el estado del optimizador y los gradientes; esta lección cubre la tercera, que particiona los propios parámetros, y su API real.
**Fuente principal:** [Documentation: "Fully Sharded Data Parallel", PyTorch](https://pytorch.org/docs/stable/fsdp.html)
**Requisitos previos:** [Lección 9](0009-zero-stage-1-and-2-partitioning-optimizer-state-and-gradients.md)

## Calentamiento

1. ▢ ¿Qué reducción de memoria da la etapa 2 de ZeRO (`P_os+g`), y a qué costo de comunicación respecto al data parallelism corriente?

<details markdown="1"><summary>Comprobación</summary>

Una reducción de memoria de 8x, con el mismo volumen de comunicación que el data parallelism corriente: no hace falta mover datos extra, ya que el estado del optimizador y los gradientes solo se necesitan en local, en el dispositivo responsable de la porción correspondiente.

</details>

2. ▢ ¿Por qué se pueden particionar el estado del optimizador y los gradientes sin comunicación añadida, de una manera que el tema de esta lección no permite?

<details markdown="1"><summary>Comprobación</summary>

Porque solo el dispositivo responsable de una porción dada de los parámetros necesita alguna vez el estado del optimizador o el gradiente de esa porción. El forward y el backward pass de cada dispositivo, en cambio, necesitan todos los parámetros del modelo, no solo los que posee, que es lo que tiene que resolver la Lección 10.

</details>

## Qué debes saber

### La última pieza: particionar los parámetros

**`P_os+g+p`**, la tercera etapa de ZeRO, particiona los propios parámetros además del estado del optimizador y los gradientes que la etapa 2 ya particiona: cada dispositivo guarda en reposo solo `1/Nd` de los parámetros, en lugar de una copia completa. Rajbhandari et al. informan de que la reducción de memoria de esta etapa escala de forma lineal con el grado de data parallelism `Nd`: repartir entre 64 dispositivos da una reducción de memoria de 64x, y esto es lo que hace funcionar su resultado más destacado: estiman que un modelo de un billón de parámetros con Adam de precisión mixta necesita aproximadamente 16 terabytes para sus estados del modelo, que repartidos entre 1,024 GPUs salen a unos 16 GB por dispositivo, con holgura dentro de una GPU de 32 GB.

Esa reducción no es gratis como lo fueron las etapas 1 y 2. El forward y el backward pass de cada dispositivo siguen necesitando todos los parámetros, no solo el `1/Nd` que guarda, así que los parámetros que un dispositivo no tiene hay que reconstruirlos a partir de los otros dispositivos en el momento en que se necesitan, y descartarlos de nuevo una vez terminado ese cálculo. Rajbhandari et al. informan de que esto cuesta un aumento modesto del 50% en el volumen de comunicación respecto al data parallelism corriente, a cambio de una reducción de memoria que sigue escalando al añadir más dispositivos, en lugar de estancarse en 8x como hacen las etapas 1 y 2.

### El mecanismo: reunir bajo demanda y luego liberar

El patrón que usa la etapa 3 es: tener en reposo solo tu propia porción de los parámetros; justo antes de que una capa necesite todos sus parámetros para un cálculo de forward o de backward, hacer un **all-gather** de los trozos que faltan desde los otros dispositivos para reconstruir temporalmente el tensor completo de parámetros; cuando termina el cálculo de esa capa, liberar la copia reconstruida y volver a tener solo tu propia porción. Es la misma operación colectiva all-gather que cualquier otra, solo que se dispara con mucha más frecuencia, una vez por capa y por pasada, y no una vez por paso de entrenamiento como la sincronización de gradientes del data parallelism corriente.

### FSDP: la misma idea, como una API real

`FullyShardedDataParallel` de PyTorch, que suele abreviarse como **FSDP**, implementa exactamente este patrón, y su propia documentación lo dice de forma directa: se describe a sí mismo como "inspirado en ... la etapa 3 de ZeRO de DeepSpeed". Envolver un módulo en FSDP reparte sus parámetros entre los dispositivos con data parallelism y, durante el forward y el backward pass, FSDP sustituye los parámetros del módulo por vistas reconstruidas reunidas bajo demanda, el mismo patrón de reunir y luego liberar que esta lección acaba de describir en abstracto. FSDP expone también estrategias de reparto más ligeras que reparten solo los gradientes y el estado del optimizador y dejan los parámetros sin repartir, que es la misma disyuntiva que hace la etapa 2 y no la de la etapa 3: se ahorra menos memoria, pero no se añade tráfico de all-gather de parámetros en cada forward y backward pass.

## Práctica

1. ▢ Usando el escalado informado de la etapa 3 de ZeRO, ¿qué reducción de memoria debería esperar un equipo al repartir los parámetros, los gradientes y el estado del optimizador de un modelo entre 32 dispositivos?

<details markdown="1"><summary>Comprobación</summary>

Unas 32x, ya que Rajbhandari et al. informan de que la reducción de memoria de la etapa 3 escala de forma lineal con el grado de data parallelism `Nd` (64 dispositivos dan 64x en su propio ejemplo, así que 32 dispositivos dan aproximadamente la mitad).

</details>

2. ▢ ¿Por qué particionar los propios parámetros requiere una comunicación extra que particionar el estado del optimizador y los gradientes no requería?

    - a) Los parámetros se almacenan con otra precisión numérica, que es más cara de transmitir
    - b) El forward y el backward pass de cada dispositivo necesitan el conjunto completo de parámetros, no solo la porción que posee, así que las porciones que faltan hay que reunirlas bajo demanda desde otros dispositivos
    - c) La partición de parámetros requiere un protocolo de red más lento que la partición de gradientes
    - d) En realidad no requiere comunicación extra; la cifra del 50% del paper es de otra comparación

<details markdown="1"><summary>Comprobación</summary>

**b)** es el mecanismo real: a diferencia del estado del optimizador y de los gradientes, que solo necesita el dispositivo que los posee, los parámetros los necesita cada dispositivo para el cálculo de forward y de backward de cada capa, así que un all-gather tiene que reconstruir las porciones que un dispositivo no tiene. (a), (c) y (d) no describen la razón real.

</details>

3. ▢ Un equipo elige la estrategia `SHARD_GRAD_OP` de FSDP de PyTorch en lugar de `FULL_SHARD`. ¿A qué etapa de ZeRO corresponde, y qué disyuntiva hace respecto a `FULL_SHARD`?

<details markdown="1"><summary>Pista</summary>

`SHARD_GRAD_OP` deja los parámetros sin repartir y expuestos en su forma completa, y reparte solo los gradientes y el estado del optimizador.

</details>

<details markdown="1"><summary>Comprobación</summary>

Corresponde a la etapa 2 de ZeRO. Ahorra menos memoria que `FULL_SHARD` (etapa 3), ya que los parámetros no se particionan, pero también evita el tráfico extra de all-gather que necesita la etapa 3 para reconstruir los parámetros bajo demanda en cada forward y backward pass.

</details>

## Prácticas en el mundo real

- [ ] Lee la documentación de FSDP de PyTorch (enlazada arriba) y busca la descripción de qué le pasa a los parámetros de un módulo envuelto durante el forward pass. Escribe una oración que la conecte con el patrón de "reunir y luego liberar" que describe esta lección.
- [ ] Usando el ejemplo de un billón de parámetros y 1,024 GPUs de esta lección (unos 16 TB de estados del modelo, 16 GB por dispositivo), repite el mismo cálculo para un modelo de 100 mil millones de parámetros repartido entre 64 dispositivos, y comprueba si cabe con holgura en una GPU de 80 GB.
- [ ] Mañana: busca un ejemplo de configuración (en la documentación de FSDP o de DeepSpeed) que fije una estrategia de reparto de forma explícita, e identifica a qué etapa de ZeRO corresponde esa configuración concreta, usando las descripciones de esta lección y de la Lección 9 de qué reparte cada etapa.

## Para profundizar

- [Paper: "ZeRO: Memory Optimizations Toward Training Trillion Parameter Models", Rajbhandari et al., 2019](https://arxiv.org/abs/1910.02054)
- [Recursos](../RESOURCES.md)

---

¿No termina de quedar claro? Vuelve a leer la fuente primaria de arriba, ya que esta lección la comprime y en la compresión es donde se escapa la comprensión. Consulta el [glosario](../GLOSSARY.md) por si algún término te resultó resbaladizo.

Si lo poco claro es la propia lección y no el material, eso es un defecto: [abre un issue](https://github.com/TokenCemetery/teach/issues).
