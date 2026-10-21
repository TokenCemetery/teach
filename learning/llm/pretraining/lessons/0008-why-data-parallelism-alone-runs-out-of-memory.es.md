---
title: "8. Por qué el data parallelism por sí solo se queda sin memoria"
description: "Contar exactamente qué guarda por parámetro un optimizador Adam de precisión mixta, y dónde choca con un muro"
type: lesson
---

# Lección 8. Por qué el data parallelism por sí solo se queda sin memoria

**Vínculo con la misión:** "Explicar qué reparten ZeRO/FSDP, por qué el data parallelism por sí solo se queda sin memoria antes de quedarse sin cómputo, y cuándo el tensor o el pipeline parallelism valen su costo de comunicación" es el cuarto punto de Cómo se ve el éxito. La Lección 7 cubrió cómo el data parallelism mantiene idéntica la copia de cada dispositivo; esta lección cuenta exactamente qué cuesta que "cada dispositivo tenga una copia completa", y dónde se rompe.
**Fuente principal:** [Paper: "ZeRO: Memory Optimizations Toward Training Trillion Parameter Models", Rajbhandari et al., 2019](https://arxiv.org/abs/1910.02054)
**Requisitos previos:** [Lección 7](0007-data-parallelism-and-gradient-all-reduce.md)

## Calentamiento

1. ▢ En el data parallelism, ¿qué operación mantiene idéntica la copia del modelo de cada dispositivo tras cada paso del optimizador?

<details markdown="1"><summary>Comprobación</summary>

El all-reduce: el gradiente local de cada dispositivo se promedia con el de todos los dispositivos antes de que ninguno aplique una actualización, así que cada dispositivo aplica el mismo gradiente promediado a una copia inicial idéntica de los pesos.

</details>

2. ▢ ¿Reduce añadir más dispositivos con data parallelism la memoria que necesita un dispositivo individual para contener el modelo? ¿Por qué sí o por qué no?

<details markdown="1"><summary>Comprobación</summary>

No. Cada dispositivo sigue teniendo una copia completa de los parámetros, los gradientes y el estado del optimizador, exactamente como si entrenara solo; más dispositivos significan más copias de esa misma huella, no una huella menor por dispositivo.

</details>

## Qué debes saber

### Qué contiene realmente "una copia completa del modelo"

La Lección 7 dijo que cada dispositivo con data parallelism tiene una copia completa de los parámetros, los gradientes y el estado del optimizador, sin contar cuánto cuesta eso. El entrenamiento de precisión mixta, el enfoque estándar para entrenar modelos grandes, vuelve concreta la cuenta. Usando Adam como optimizador, Rajbhandari et al. cuentan, por parámetro (`Ψ` denota el número de parámetros):

- una copia `fp16` de los parámetros, usada para el forward y el backward pass: 2 bytes por parámetro
- una copia `fp16` de los gradientes: 2 bytes por parámetro
- una copia `fp32` de los parámetros, que guarda el optimizador para actualizaciones numéricamente estables: 4 bytes por parámetro
- una copia `fp32` del momento de Adam: 4 bytes por parámetro
- una copia `fp32` de la varianza de Adam: 4 bytes por parámetro

Eso suma 16 bytes por parámetro, y cada dispositivo con data parallelism tiene una copia completa de cada uno de ellos, sin importar cuántos otros dispositivos tengan también una copia idéntica.

### Dónde choca con un muro

Para un modelo de 1.5 mil millones de parámetros (el tamaño de GPT-2), 16 bytes por parámetro suman 24 GB solo para estos estados del modelo, muy por encima de los 3 GB que haría falta para contener únicamente los parámetros `fp16` por sí solos, y eso antes de contar las activaciones (los valores intermedios que se guardan del forward pass para calcular los gradientes en el backward pass), que Rajbhandari et al. estiman aparte en unos 60 GB para ese mismo modelo con una longitud de secuencia de 1,024 y un batch size de 32. Rajbhandari et al. enuncian directamente el límite resultante: "el data parallelism básico no reduce la memoria por dispositivo, y se queda sin memoria con modelos de más de 1.4B de parámetros en la generación actual de GPUs con 32 GB de memoria". Una GPU de 32 GB se ha quedado sin espacio antes de quedarse sin cualquier otra cosa, con un modelo apenas mayor que GPT-2, usando todos los muchos dispositivos que el data parallelism puede añadir.

### La forma de la solución

Cada dispositivo en el data parallelism corriente tiene una copia idéntica y totalmente redundante de los mismos 16Ψ bytes de estados del modelo. Esa redundancia es exactamente lo que puede eliminar una estrategia distinta: en lugar de que cada dispositivo tenga todo, cada dispositivo podría tener solo su propia porción de los estados del modelo, y reconstruir o comunicar lo que no tiene únicamente cuando de verdad hace falta para un cálculo. Esa es la idea que la etapa 5 retoma directamente, con el nombre de ZeRO.

## Práctica

1. ▢ Usando el desglose de 16 bytes por parámetro, ¿aproximadamente cuánta memoria requerirían solo los estados del modelo para un modelo de 7 mil millones de parámetros entrenado en precisión mixta con Adam?

<details markdown="1"><summary>Pista</summary>

Multiplica el número de parámetros por 16 bytes, y luego convierte los bytes a gigabytes.

</details>

<details markdown="1"><summary>Comprobación</summary>

Unos 112 GB (`7 × 10^9 × 16` bytes ≈ `1.12 × 10^11` bytes ≈ 112 GB). Eso son solo los estados del modelo, muy por encima de una sola GPU de 32 GB o incluso de 80 GB, sin contar siquiera las activaciones.

</details>

2. ▢ ¿Cuál de estas opciones explica mejor por qué el data parallelism por sí solo no puede hacer caber un modelo arbitrariamente grande, por muchos dispositivos que se añadan?

    - a) El ancho de banda de comunicación entre dispositivos acaba saturándose
    - b) Cada dispositivo tiene una copia completa y redundante del mismo costo de memoria por parámetro, así que añadir dispositivos añade más copias en lugar de reducir el requisito de cualquier dispositivo individual
    - c) La propia operación de all-reduce consume una cantidad de memoria proporcional al tamaño del modelo
    - d) Los modelos más grandes producen siempre gradientes más grandes, que desbordan la representación fp16

<details markdown="1"><summary>Comprobación</summary>

**b)** es el límite real que traza esta lección, directamente desde la huella de memoria redundante por dispositivo. (a) es una preocupación real en el entrenamiento distribuido, pero es un costo de tiempo de comunicación, no el muro de capacidad de memoria del que trata esta lección. (c) y (d) no son el mecanismo que identifican los autores de ZeRO.

</details>

3. ▢ Rajbhandari et al. afirman que el data parallelism básico se queda sin memoria con modelos de más de 1.4B de parámetros en GPUs de 32 GB de memoria. Según el desglose de 16 bytes por parámetro, ¿aproximadamente cuánta memoria requerirían solo los estados de un modelo de 1.4B de parámetros, y cómo se compara eso con la cifra de 32 GB una vez añadidas las activaciones?

<details markdown="1"><summary>Comprobación</summary>

Unos 22.4 GB solo para los estados del modelo (`1.4 × 10^9 × 16` bytes ≈ `2.24 × 10^10` bytes). Eso ya deja menos de 10 GB de una GPU de 32 GB para las activaciones, que el ejemplo de GPT-2 de la lección situó en unos 60 GB con una longitud de secuencia y un batch size modestos, muy por encima de lo que queda.

</details>

## Prácticas en el mundo real

- [ ] Elige el número de parámetros de un modelo abierto publicado y, usando la fórmula de 16 bytes por parámetro, estima su requisito de memoria de estados del modelo con Adam de precisión mixta. Compara esa estimación con los tamaños de memoria de GPU de uso común para entrenar (24, 40 y 80 GB son cifras típicas con las que comparar).
- [ ] Lee el párrafo del paper de ZeRO (enlazado arriba) que describe la memoria residual (activaciones, buffers temporales, fragmentación de memoria) y escribe una oración que la distinga de la memoria de estados del modelo que contó esta lección.
- [ ] Mañana: sin adelantarte, escribe una predicción de una oración para la etapa 5: si el problema es que cada dispositivo tiene una copia completa y redundante de los mismos 16Ψ bytes, ¿qué tendría que hacer en su lugar una solución que elimine la redundancia, y qué tendría que comunicar para compensar que ya no se tiene todo en local?

## Para profundizar

- [Paper: "ZeRO: Memory Optimizations Toward Training Trillion Parameter Models", Rajbhandari et al., 2019](https://arxiv.org/abs/1910.02054)
- [Recursos](../RESOURCES.md)

---

La etapa 4 estableció que lo primero que se agota en el data parallelism es su redundancia, no su cómputo. La etapa 5 lo retoma directamente: qué reparten realmente ZeRO y FSDP para eliminarla.

¿No termina de quedar claro? Vuelve a leer la fuente primaria de arriba, ya que esta lección la comprime y en la compresión es donde se escapa la comprensión. Consulta el [glosario](../GLOSSARY.md) por si algún término te resultó resbaladizo.

Si lo poco claro es la propia lección y no el material, eso es un defecto: [abre un issue](https://github.com/TokenCemetery/teach/issues).
