---
title: "16. Metodología de medición de la latencia p99"
description: "Por qué el p99 supera a un promedio, por qué el TTFT y la latencia entre tokens necesitan cifras separadas, y qué hace fiable una medición de p99"
type: lesson
---

# Lección 16. Metodología de medición de la latencia p99

**Vínculo con la misión:** La misión de este espacio de trabajo es defender un presupuesto de latencia p99, y una cifra defendida tiene que salir de una medición bien hecha; esta lección es lo que significa "bien hecha" antes de que la lección 17 vincule esa cifra con cada decisión anterior.
**Fuente principal:** [Docs: vLLM Documentation, vLLM Project](https://docs.vllm.ai/en/latest/)
**Requisitos previos:** [Lección 15](0015-what-changes-off-gpu.md), [KV cache](../GLOSSARY.md)

## Calentamiento

1. ▢ ¿Por qué el prefill reclama en un solo paso la mayor parte de la huella final de caché de una solicitud, mientras que el decode añade el resto gradualmente?

<details markdown="1"><summary>Comprobación</summary>

El prefill procesa el prompt entero en una sola pasada forward, calculando y guardando en caché juntos los keys y values de todos los tokens del prompt. El decode genera un token de salida por paso, así que la caché crece solo en la de un token por paso.

</details>

2. ▢ En el batching continuo, ¿qué hace que una solicitud grande admitida detenga a todas las demás secuencias que comparten su paso de lote?

<details markdown="1"><summary>Comprobación</summary>

Un paso de lote es atómico: toda secuencia que lo comparte avanza junta, así que un prefill grande metido en un paso retrasa el siguiente token de todas las demás secuencias hasta que ese paso termina. Eso es head-of-line blocking.

</details>

## Qué debes saber

### Por qué p99 y no el promedio

El **p99** de una distribución de latencia es el valor por debajo del cual cae el 99% de las solicitudes medidas; solo el 1% peor es más lento. Un promedio puede parecer bueno mientras oculta un problema real: el head-of-line blocking de la lección 5, por ejemplo, solo golpea a la pequeña fracción de solicitudes con la mala suerte de compartir un paso con un prefill grande, así que apenas mueve un promedio sobre miles de solicitudes por lo demás rápidas, mientras que puede volver dramáticamente más lento a ese 1% desafortunado. Un presupuesto de latencia defendido con un promedio pasaría por alto exactamente el modo de fallo que este espacio de trabajo dedicó la etapa 2 a explicar.

![Un histograma de la latencia de las solicitudes. La mayoría de las solicitudes se agrupan en latencia baja, formando un bulto alto a la izquierda que decae rápido. Un grupo separado y disperso de solicitudes queda muy a la derecha, con una latencia mucho mayor, la cola lenta. Una línea discontinua que marca el promedio queda dentro del bulto de la izquierda, apenas desplazada por las raras solicitudes de la derecha, porque son muy pocas para moverla. Un marcador del p99 queda, en cambio, en esa cola de la derecha, porque el p99 lo define el peor uno por ciento, que es precisamente donde están las solicitudes raras y lentas.](images/p99-vs-average-latency.svg)

### Qué latencia, medida por separado

La "latencia de la solicitud" no es una sola cifra para un servidor de LLM; como mínimo se divide en **tiempo hasta el primer token (TTFT, time to first token)**, dominado por el prefill, y **latencia entre tokens (ITL, inter-token latency)**, a veces llamada tiempo por token de salida, dominada por el decode. Se comportan de manera distinta (lección 3) y las moldean palancas distintas (batching y scheduling para el TTFT, tamaño de lote y cuantización para la ITL), así que fundirlas en una cifra mezclada oscurece a qué palanca apunta realmente un mal p99. Un presupuesto que merezca defenderse nombra el p99 del TTFT y el p99 de la ITL (o el p99 de la latencia total de extremo a extremo, cuando eso es de verdad lo que le importa a la carga de trabajo) como cifras separadas, no un promedio de dos cosas distintas.

### Qué hace fiable una medición de p99

Un p99 es la estimación de un evento raro, por definición solo el peor 1% de una muestra, así que necesita suficientes muestras para significar algo: un p99 calculado a partir de 20 solicitudes en realidad informa sobre una sola solicitud (el peor percentil 1 de 20 está cerca del máximo, no es una estimación estable de la cola), mientras que una estimación estable suele necesitar muestras de cientos a miles. La carga que genera esas muestras también tiene que parecerse a la carga de trabajo real: una concurrencia realista (no tan baja que el comportamiento del batching y del scheduling nunca se ponga realmente a prueba) y una mezcla realista de longitudes de prompt y de salida (el desperdicio del batching estático de la lección 4 y el head-of-line blocking de la lección 5 dependen ambos de una varianza de longitud de solicitud que un benchmark con solicitudes de longitud uniforme nunca sacaría a la luz). Un p99 medido bajo una carga poco realista es una cifra real sobre una carga de trabajo que no es la que se sirve.

## Práctica

1. ▢ La latencia promedio de las solicitudes de un servidor parece buena, pero los usuarios reportan de vez en cuando solicitudes que tardan mucho más de lo esperado. ¿Qué sugiere este patrón sobre dónde aparecería el problema en la distribución de latencia, y por qué podría no haberlo detectado el promedio?

<details markdown="1"><summary>Comprobación</summary>

Sugiere un problema de cola, algo como el head-of-line blocking de la lección 5, que solo afecta a una pequeña fracción de solicitudes. Un promedio sobre muchas solicitudes casi todas sin afectar apenas se mueve incluso cuando esa pequeña fracción se vuelve dramáticamente más lenta, que es exactamente por lo que hace falta un p99 (o un percentil igualmente alto) para verlo siquiera.

</details>

2. ▢ ¿Por qué deberían medirse y reportarse el TTFT y la latencia entre tokens como cifras p99 separadas, en lugar de fundirse en una sola cifra de "latencia promedio de la solicitud"?

<details markdown="1"><summary>Comprobación</summary>

El TTFT lo domina el prefill y lo moldean el scheduling y el chunking; la latencia entre tokens la domina el decode y la moldean el tamaño de lote y la cuantización. Una sola cifra mezclada no puede decir a cuál de esas palancas apunta realmente un mal resultado, y mejorar una puede mover un promedio mezclado sin revelar si la otra empeoró.

</details>

3. ▢ Un equipo calcula una cifra de latencia p99 a partir de 20 solicitudes medidas. ¿Es fiable esa cifra? ¿Por qué sí o por qué no?

<details markdown="1"><summary>Pista</summary>

Piensa en a cuántas de esas 20 solicitudes describe realmente el percentil 99.

</details>

<details markdown="1"><summary>Comprobación</summary>

No, no de forma fiable. Con solo 20 muestras, el percentil 99 está cerca de informar sobre la única solicitud más lenta de la muestra, no una estimación estable de una cola genuina. Un p99 fiable necesita una muestra mucho mayor, normalmente de cientos a miles de solicitudes, para promediar el ruido de qué solicitudes concretas acabaron en ese 1% superior.

</details>

4. ▢ Un benchmark mide la latencia p99 con solicitudes que tienen todas la misma longitud uniforme de prompt y de salida. ¿Por qué podría esto subestimar el p99 que vería realmente una carga de producción con longitudes de solicitud variadas?

<details markdown="1"><summary>Comprobación</summary>

Las lecciones 4 y 5 mostraron que la varianza en la longitud de las solicitudes es lo que crea los modos de fallo que dañan la latencia de cola: el desperdicio del batching estático escala con la dispersión entre las longitudes de las solicitudes, y el head-of-line blocking lo dispara un prefill inusualmente grande que llega entre otros más pequeños. Un benchmark de longitud uniforme nunca produce esa varianza, así que nunca ejercita las condiciones de las que realmente viene la latencia de cola de la carga real.

</details>

5. ▢ ¿Qué afirmación es verdadera de una medición defendible de la latencia p99?

    - a) Basta una sola ejecución de benchmark de cualquier tamaño, siempre que reporte una cifra de p99
    - b) Debe medirse con una concurrencia y una varianza de longitud de solicitud realistas, y reportarse por separado para el TTFT y la latencia entre tokens
    - c) El promedio y el p99 siempre se mueven juntos, así que medir uno basta
    - d) El p99 solo importa en el serving en CPU/edge, no en el serving en GPU

<details markdown="1"><summary>Comprobación</summary>

**b)** Tanto el realismo de la carga como la separación del TTFT y la latencia entre tokens son necesarios para que la cifra apunte a algo accionable. (a) es falsa: con muy pocas muestras un p99 es inestable, como mostró la pregunta 3. (c) es falsa: un promedio puede ocultar exactamente el comportamiento de cola que existe para detectar un p99. (d) es falsa: la latencia de cola y su medición importan en cualquier stack de serving, de GPU o de CPU.

</details>

## Prácticas en el mundo real

- [ ] Encuentra la herramienta de benchmarking de tu stack de serving (vLLM incluye `benchmark_serving.py`) y lee qué percentiles reporta por defecto y qué distribución de longitud de solicitudes usa.
- [ ] Para una carga de trabajo que tengas en mente, anota cómo sería una distribución realista de longitudes de prompt y de salida, y si un benchmark con longitudes uniformes pasaría algo por alto.
- [ ] Mañana: si tienes un servidor en ejecución, ejecuta un benchmark contra él con al menos unos cientos de solicitudes y anota por separado el p99 del TTFT y el p99 de la latencia entre tokens reportados.

## Para profundizar

- [Docs: vLLM Documentation, vLLM Project](https://docs.vllm.ai/en/latest/)
- [Article: "How continuous batching enables 23x throughput in LLM inference while reducing p50 latency", Anyscale](https://www.anyscale.com/blog/continuous-batching-llm-inference)
- [Recursos](../RESOURCES.md)

---

¿No termina de quedar claro? Vuelve a leer la fuente primaria de arriba, ya que esta lección la comprime y en la compresión es donde se escapa la comprensión. Consulta el [glosario](../GLOSSARY.md) por si algún término te resultó resbaladizo.

Si lo poco claro es la propia lección y no el material, eso es un defecto: [abre un issue](https://github.com/TokenCemetery/teach/issues).
