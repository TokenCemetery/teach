---
title: "3. Crecimiento, prefill, decode y precisión"
description: "Cómo crece la caché a lo largo del prefill y del decode, y qué recupera bajar su precisión"
type: lesson
---

# Lección 3. Crecimiento, prefill, decode y precisión

**Vínculo con la misión:** Un presupuesto de latencia depende de cuándo se reclama la memoria de la caché durante una solicitud, y no solo de su tamaño final, y de las demás palancas que tiene un servidor sobre ese tamaño además del tamaño de lote y la longitud de contexto.
**Fuente principal:** [Docs: vLLM Documentation, vLLM Project](https://docs.vllm.ai/en/latest/)
**Requisitos previos:** [Lección 2](0002-capacity-and-batch-size.md), [KV cache](../GLOSSARY.md)

## Calentamiento

1. ▢ Escribe la fórmula de la huella total de la KV cache de un lote, en función de los bytes por token, la longitud de contexto y el tamaño de lote.

<details markdown="1"><summary>Comprobación</summary>

`total cache bytes = bytes per token × context length × batch size`.

</details>

2. ▢ ¿Por qué un modelo que usa grouped-query attention tiene una KV cache más pequeña que el mismo modelo con atención multi-cabeza completa?

<details markdown="1"><summary>Comprobación</summary>

La caché guarda un par key/value por cabeza KV, no por cabeza de query, y GQA usa menos cabezas KV que cabezas de query. La caché escala con `num_kv_heads`, que la MHA completa iguala a `num_heads`.

</details>

## Qué debes saber

### La caché no crece a un ritmo constante

Una solicitud tiene dos fases, y reclaman la memoria de la caché de maneras muy distintas.

El **prefill** procesa el prompt completo en una sola pasada forward: los vectores key y value de todos los tokens del prompt se calculan y se guardan en caché juntos, en un solo paso. La caché salta de vacía a `bytes per token × prompt length` antes de que el modelo haya generado un solo token de salida. Esta fase está limitada por cómputo: es una gran multiplicación de matrices paralela sobre todo el prompt.

El **decode** genera después un token de salida a la vez. Cada paso calcula y guarda en caché exactamente los keys y values de un token más, así que la caché crece `bytes per token` por paso, un goteo lento en comparación. Esta fase está limitada por el ancho de banda de memoria: cada paso tiene que volver a leer la caché entera para atender sobre ella, por el trabajo nuevo de un solo token.

Por tanto, un prompt largo reclama de inmediato, en el prefill, la mayor parte de la huella final de caché de una solicitud, mientras que el decode añade el resto gradualmente. Un plan de capacidad que solo mira la "longitud final de contexto" en realidad pregunta "qué tamaño tendrá esto después del prefill más los pasos de decode que espero", y las dos fases contribuyen con calendarios muy distintos.

![Un gráfico del tamaño de la caché a lo largo del tiempo: la caché salta casi en vertical durante el único paso de prefill, y luego sube en una escalera lenta y constante durante el decode, mientras cada token de salida añade la caché de un token más. Un prompt de 2048 tokens reclama unos 640 MB en el prefill, mientras que 128 pasos de decode añaden solo unos 40 MB más, el 6% del total.](images/prefill-decode-cache-growth.svg)

### Una palanca independiente de los pesos del modelo: la precisión de la caché

La fórmula de la lección 2 llevaba `bytes_per_value` como un término propio, separado de `num_layers`, `num_kv_heads` y `head_dim`. Ese término no tiene por qué coincidir con la precisión en que calcula el modelo. Un stack de serving puede guardar la propia KV cache en una precisión menor, habitualmente fp8, mientras el modelo sigue calculando en bf16 o fp16. Reducir `bytes_per_value` a la mitad, de 2 bytes a 1, reduce la huella de la caché exactamente a la mitad, sin cambiar `num_kv_heads`, sin cambiar la longitud de contexto y sin reentrenar: es una decisión en tiempo de serving, independiente de la precisión a la que se hayan cuantizado los pesos.

Esto se combina con todo lo de la lección 2. Toma otra vez las cifras de Llama-2-70B (80 capas, 8 cabezas KV, `head_dim` = 128): en fp16, el costo por token era de 320 KB. En fp8, es `2 × 80 × 8 × 128 × 1 byte = 163,840 bytes ≈ 160 KB`, exactamente la mitad, porque solo cambió `bytes_per_value`.

## Práctica

1. ▢ Una solicitud tiene un prompt de 2048 tokens. Con la cifra de fp16 de Llama-2-70B de 320 KB por token, ¿cuánta caché reclama solo el prefill, antes de generar ningún token de salida?

<details markdown="1"><summary>Comprobación</summary>

`320 KB × 2048 ≈ 640 MB`, reclamados en el único paso de prefill.

</details>

2. ▢ Esa misma solicitud genera después 128 tokens de salida mediante decode. ¿Cuánta caché adicional añade el decode, y qué fracción de la caché final total de la solicitud representa?

<details markdown="1"><summary>Pista</summary>

El decode añade `bytes per token × number of decode steps`. Compáralo con la cifra del prefill de la pregunta 1.

</details>

<details markdown="1"><summary>Comprobación</summary>

`320 KB × 128 ≈ 40 MB` añadidos por el decode. La caché total es `640 MB + 40 MB = 680 MB`, así que el decode es solo alrededor del 6% del total; el prefill reclamó el otro 94% en un solo paso.

</details>

3. ▢ Con la cifra de caché en fp8 de Llama-2-70B de 160 KB por token, calcula la huella total de la caché para un lote de 64 secuencias con un contexto de 4096 tokens.

<details markdown="1"><summary>Pista</summary>

`total cache bytes = bytes per token × context length × batch size`, la misma fórmula que en el calentamiento.

</details>

<details markdown="1"><summary>Comprobación</summary>

`160 KB × 4096 × 64 = 41,943,040 KB ≈ 40 GB`.

</details>

4. ▢ La versión en fp16 de ese mismo lote (pregunta 3, pero a 320 KB por token) costaría cuánta caché, y ¿qué muestra la comparación sobre apilar un cambio de precisión sobre un cambio de reparto de cabezas?

<details markdown="1"><summary>Comprobación</summary>

`320 KB × 4096 × 64 ≈ 80 GB`, exactamente el doble. La caché en fp8 reduce a la mitad la huella además de lo que GQA ya recuperó respecto de la MHA completa: las dos palancas son independientes y se multiplican entre sí en lugar de sustituirse.

</details>

## Prácticas en el mundo real

- [ ] Encuentra el parámetro de tu stack de serving para el tipo de dato de la KV cache (vLLM: `--kv-cache-dtype`) y lee qué precisiones admite y qué advierte sobre la precisión.
- [ ] Para una forma de solicitud que realmente esperes (longitud del prompt, longitud de salida esperada), calcula cuánta de su caché final reclama el prefill frente al decode, con la cifra real por token de un modelo.
- [ ] Mañana: lee un párrafo de la documentación de vLLM sobre chunked prefill y anota en una frase por qué dividir el prefill en trozos cambia el calendario de reclamación de memoria que describió esta lección.

## Para profundizar

- [Docs: vLLM Documentation, vLLM Project](https://docs.vllm.ai/en/latest/)
- [Article: "Transformer Inference Arithmetic", Kipply](https://kipp.ly/transformer-inference-arithmetic/)
- [Recursos](../RESOURCES.md)

---

¿No termina de quedar claro? Vuelve a leer la fuente primaria de arriba, ya que esta lección la comprime y en la compresión es donde se escapa la comprensión. Consulta el [glosario](../GLOSSARY.md) por si algún término te resultó resbaladizo.

Si lo poco claro es la propia lección y no el material, eso es un defecto: [abre un issue](https://github.com/TokenCemetery/teach/issues).
