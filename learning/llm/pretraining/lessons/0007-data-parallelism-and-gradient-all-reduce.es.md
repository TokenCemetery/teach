---
title: "7. Data parallelism y all-reduce de gradientes"
description: "Repartir un batch entre dispositivos que tienen cada uno una copia completa del modelo, y qué mantiene idénticas todas las copias"
type: lesson
---

# Lección 7. Data parallelism y all-reduce de gradientes

**Vínculo con la misión:** "Explicar qué reparten ZeRO/FSDP, por qué el data parallelism por sí solo se queda sin memoria antes de quedarse sin cómputo, y cuándo el tensor o el pipeline parallelism valen su costo de comunicación" es el cuarto punto de Cómo se ve el éxito. Esta lección cubre qué es el data parallelism y cómo se mantiene correcto; la Lección 8 cubre por qué se queda sin memoria.
**Fuente principal:** [Paper: "ZeRO: Memory Optimizations Toward Training Trillion Parameter Models", Rajbhandari et al., 2019](https://arxiv.org/abs/1910.02054)
**Requisitos previos:** [Lección 6](0006-chinchilla-the-compute-optimal-correction.md)

## Calentamiento

1. ▢ Usando `FLOPs(N, D) ≈ 6ND`, ¿aproximadamente cuántos tokens permite un presupuesto de cómputo de `6 × 10^21` FLOPs para un modelo de 5 mil millones de parámetros?

<details markdown="1"><summary>Comprobación</summary>

200 mil millones de tokens: `6 × 10^21 / (6 × 5 × 10^9) = 2 × 10^11`.

</details>

## Qué debes saber

### Repartir el batch, no el modelo

El **data parallelism** es la manera más simple de poner a trabajar a más de un dispositivo en la misma ejecución de entrenamiento: cada dispositivo tiene una copia completa e idéntica del modelo, y un único batch grande se divide en trozos más pequeños por dispositivo, uno para cada uno. Cada dispositivo ejecuta su propio forward y backward pass sobre su propio trozo, de forma totalmente independiente de los demás, y calcula su propio gradiente local.

### Mantener idénticas todas las copias

Si cada dispositivo se limitara a aplicar su propio gradiente local a su propia copia de los pesos, las copias se separarían tras un solo paso, y "N dispositivos entrenando un modelo" se convertiría sin que nadie lo notara en "N dispositivos entrenando N modelos distintos". El data parallelism evita esto con un paso de sincronización antes de que corra el optimizador: el gradiente local de cada dispositivo se promedia con el de todos los demás, mediante una operación de comunicación colectiva llamada **all-reduce**, y cada dispositivo recibe de vuelta el mismo gradiente promediado. Como cada dispositivo aplica entonces el gradiente promediado idéntico a una copia inicial idéntica de los pesos, todas las copias siguen siendo idénticas tras el paso del optimizador, paso tras paso, sin tener que comparar nunca los propios pesos.

Una manera habitual de implementarlo con eficiencia es un **ring all-reduce**: los dispositivos se disponen en un anillo lógico, y cada uno solo intercambia datos con sus dos vecinos, en una secuencia de pasos que garantiza que cada dispositivo acabe con la suma completa (y luego con el promedio) sin necesitar que un dispositivo recoja todo directamente de todos los demás. Esto mantiene el volumen de comunicación por dispositivo aproximadamente constante al añadir más dispositivos, en lugar de crecer con su número, que es lo que hace que el data parallelism escale razonablemente bien para empezar.

### Qué aporta, y qué no toca

Todo el beneficio del data parallelism es el rendimiento: con `k` dispositivos se puede procesar `k` veces más datos por unidad de tiempo real, ya que cada dispositivo hace un trabajo independiente sobre su propia porción del batch. Nada de esto cambia cuánta memoria necesita un dispositivo individual. Cada dispositivo sigue teniendo una copia completa de los parámetros del modelo, sus gradientes y su estado del optimizador, exactamente como si entrenara solo; añadir más dispositivos con data parallelism añade más copias de la misma huella de memoria, no menos de ella por dispositivo. El data parallelism es una manera de procesar más rápido más entrenamiento de un modelo de tamaño fijo; por sí solo no es una manera de que quepa un modelo mayor del que un único dispositivo podría contener de otro modo. La Lección 8 vuelve concreto ese límite.

## Práctica

1. ▢ Cuatro dispositivos entrenan un modelo con data parallelism. El dispositivo 3 calcula un gradiente local que resulta ser inusualmente grande comparado con los gradientes de los otros tres dispositivos en ese paso, por lo que hubiera en su porción del batch. ¿Qué impide que esto haga que la copia de los pesos del dispositivo 3 se separe de la de los otros tres?

<details markdown="1"><summary>Comprobación</summary>

El paso de all-reduce. El gradiente local de cada dispositivo, incluido el inusualmente grande del dispositivo 3, se promedia con el de los cuatro dispositivos antes de que ningún dispositivo aplique una actualización, así que cada dispositivo aplica el mismo gradiente promediado a una copia inicial idéntica de los pesos, y las cuatro copias siguen siendo idénticas.

</details>

2. ▢ ¿Cuál de estas opciones describe mejor qué cambia en una ejecución de entrenamiento al añadir más dispositivos con data parallelism?

    - a) Reduce la cantidad de memoria que necesita cada dispositivo para contener el modelo
    - b) Permite procesar más parte del batch por unidad de tiempo, sin cambiar cuánta memoria necesita un dispositivo individual
    - c) Elimina por completo la necesidad de un paso del optimizador
    - d) Aumenta automáticamente el número de parámetros del modelo

<details markdown="1"><summary>Pista</summary>

Pregúntate qué es lo que se reparte realmente entre dispositivos en el data parallelism: ¿el modelo o el batch?

</details>

<details markdown="1"><summary>Comprobación</summary>

**b)** El data parallelism reparte el batch, no el modelo, así que el rendimiento escala con el número de dispositivos mientras que la memoria por dispositivo no se reduce. (a) es exactamente lo contrario, algo que la Lección 8 vuelve concreto. (c) y (d) describen cambios que el data parallelism no hace en absoluto.

</details>

3. ▢ En un ring all-reduce, ¿por qué cada dispositivo solo se comunica con sus dos vecinos del anillo, en lugar de que cada dispositivo envíe su gradiente directamente a todos los demás?

<details markdown="1"><summary>Comprobación</summary>

Para que el volumen de comunicación que tiene que manejar un dispositivo individual se mantenga aproximadamente constante al unirse más dispositivos al anillo, en lugar de crecer con el número de dispositivos, que es lo que permite que este enfoque escale a muchos dispositivos sin que la propia comunicación se convierta en el cuello de botella.

</details>

## Prácticas en el mundo real

- [ ] Busca la documentación de una API de entrenamiento con data parallelism a la que tengas acceso (`DistributedDataParallel` de PyTorch es una habitual) y localiza dónde describe el paso de sincronización de gradientes. Anota cómo llama a la operación, y si la descripción coincide con el "all-reduce" tal como lo describe esta lección.
- [ ] Esboza en papel cuatro dispositivos dispuestos en un anillo, y sigue a mano qué envía y recibe un solo dispositivo en un ring all-reduce a lo largo de unos pocos pasos, usando un vector de gradiente de juguete de 4 números repartido a un número por dispositivo.
- [ ] Mañana: sin adelantarte, escribe una predicción de una oración para la Lección 8: si cada dispositivo con data parallelism tiene que contener una copia completa de los parámetros del modelo, sus gradientes y el estado del optimizador, ¿qué pasa a medida que el modelo crece mientras el número de dispositivos se mantiene fijo?

## Para profundizar

- [Paper: "ZeRO: Memory Optimizations Toward Training Trillion Parameter Models", Rajbhandari et al., 2019](https://arxiv.org/abs/1910.02054)
- [Recursos](../RESOURCES.md)

---

¿No termina de quedar claro? Vuelve a leer la fuente primaria de arriba, ya que esta lección la comprime y en la compresión es donde se escapa la comprensión. Consulta el [glosario](../GLOSSARY.md) por si algún término te resultó resbaladizo.

Si lo poco claro es la propia lección y no el material, eso es un defecto: [abre un issue](https://github.com/TokenCemetery/teach/issues).
