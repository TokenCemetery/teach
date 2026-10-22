---
title: "4. Batching estático frente a continuo"
description: "Por qué agrupar solicitudes en lotes ayuda al throughput, y por qué el batching continuo supera al estático"
type: lesson
---

# Lección 4. Batching estático frente a continuo

**Vínculo con la misión:** El batching es la palanca que convierte la capacidad de KV cache de un servidor, lo que las lecciones 1 a 3 enseñaron a calcular, en throughput servido de verdad; lo bien que un servidor hace batching decide cuánta de esa capacidad se dedica a trabajo útil.
**Fuente principal:** [Article: "How continuous batching enables 23x throughput in LLM inference while reducing p50 latency", Anyscale](https://www.anyscale.com/blog/continuous-batching-llm-inference)
**Requisitos previos:** [Lección 3](0003-growth-prefill-decode-precision.md), [KV cache](../GLOSSARY.md)

## Calentamiento

1. ▢ ¿Por qué el decode está limitado por el ancho de banda de memoria y no por cómputo?

<details markdown="1"><summary>Comprobación</summary>

Cada paso de decode vuelve a leer la KV cache entera para atender sobre ella, solo para calcular un token nuevo. La cantidad de cómputo nuevo por paso es pequeña en comparación con el tráfico de memoria necesario para leer la caché y los pesos.

</details>

2. ▢ La lección 3 distinguió el prefill del decode. ¿Cuál de las dos procesa un prompt entero en una sola pasada forward?

<details markdown="1"><summary>Comprobación</summary>

El prefill. El decode, en cambio, genera un token de salida, y hace crecer la caché en la de un token, por paso.

</details>

## Qué debes saber

### Por qué ayuda agrupar en lotes los pasos de decode

El tráfico de memoria de un paso de decode, que lee los pesos del modelo y la KV cache de cada secuencia residente, apenas cambia tanto si calcula el siguiente token de una secuencia como los siguientes tokens de varias secuencias a la vez. Agrupar en lotes los pasos de decode de varias secuencias reparte ese mismo tráfico de memoria entre más cómputo útil, que es exactamente la solución que necesita un paso limitado por el ancho de banda de memoria: más trabajo hecho por cada byte leído.

### El batching estático desperdicia esa ganancia con tiempos de finalización desiguales

La manera obvia de hacer batching es agrupar un conjunto fijo de solicitudes, ejecutar pasos de decode hasta que todas hayan terminado y luego empezar el siguiente grupo. Esto es el **batching estático**, y tiene un defecto serio: el grupo no puede terminar hasta que lo haga su secuencia más larga. Toda secuencia que termina antes sigue ocupando un slot del lote sin aportar nada hasta que acaba todo el grupo.

Toma cuatro solicitudes agrupadas que necesitan 10, 20, 30 y 100 tokens de salida respectivamente. El lote se ejecuta durante 100 pasos, porque eso es lo que necesita la secuencia más larga. A lo largo de esos 100 pasos, el lote consume `4 × 100 = 400` slot-steps de trabajo de GPU, pero solo `10 + 20 + 30 + 100 = 160` de esos slot-steps hicieron algo útil. Los otros 240 se gastaron en secuencias que ya habían terminado, inactivas hasta el límite del lote. Eso es un 60% de desperdicio, y empeora a medida que crece la dispersión entre las longitudes de las solicitudes, que es el caso normal: las solicitudes reales varían enormemente en cuánto generan.

### El batching continuo elimina el límite del lote

El **batching continuo** (también llamado scheduling a nivel de iteración) planifica al nivel de un solo paso de decode en lugar de un grupo fijo. En el momento en que una secuencia termina, se libera su slot y se admite en el lote una solicitud nueva que esperaba en el paso siguiente, en lugar de esperar a que terminen también todas las demás secuencias de su antiguo grupo. La composición del lote cambia continuamente; lo que se mantiene aproximadamente constante es su tamaño, no la vida de una solicitud concreta.

En el ejemplo de las cuatro solicitudes, la secuencia que solo necesita 10 tokens libera su slot en el paso 10. Un scheduler estático deja ese slot inactivo durante 90 pasos más. Un scheduler continuo admite una solicitud nueva en él de inmediato, así que la GPU sigue haciendo trabajo útil en ese slot en lugar de cargar con peso muerto hasta un límite arbitrario. Ese es el mecanismo detrás de las ganancias de throughput que reporta la fuente principal de esta lección: no un cálculo más rápido por paso, sino mucho menos de cada paso desperdiciado en secuencias a las que no les quedaba nada por hacer.

![Dos slots de un lote a lo largo de 100 pasos de decode: el slot A necesita 10 pasos, el slot D necesita 100. Con batching estático, el slot A termina en el paso 10 y queda inactivo durante 90 pasos hasta que todo el lote termina junto. Con batching continuo, se admite una solicitud nueva en el slot A en el momento en que se libera, en el paso 10, así que el slot sigue haciendo trabajo útil.](images/static-vs-continuous-batching.svg)

## Práctica

1. ▢ Un lote estático contiene dos solicitudes que necesitan 15 y 60 tokens de salida. ¿Cuántos slot-steps totales consume el lote, cuántos son útiles y qué fracción se desperdicia?

<details markdown="1"><summary>Pista</summary>

Los slot-steps totales son `batch size × steps until the longest sequence finishes`. Los slot-steps útiles son la suma de la longitud real de cada solicitud.

</details>

<details markdown="1"><summary>Comprobación</summary>

Total: `2 × 60 = 120` slot-steps. Útiles: `15 + 60 = 75`. Desperdiciados: `120 − 75 = 45`, que es `45 / 120 = 37.5%`.

</details>

2. ▢ En un scheduler de batching continuo, ¿qué pasa en el paso exacto en que una secuencia del lote termina de generar?

<details markdown="1"><summary>Comprobación</summary>

Su slot se libera de inmediato, y se admite una solicitud nueva que esperaba en ese slot en el paso siguiente, en lugar de que el slot quede inactivo hasta que también terminen todas las demás secuencias de algún grupo fijo.

</details>

3. ▢ ¿Qué afirmación es verdadera del batching continuo en comparación con el batching estático?

    - a) Reduce el costo de cómputo por paso de la propia atención
    - b) Elimina el requisito de KV cache de las secuencias terminadas antes de expulsarlas
    - c) Mantiene el lote lleno admitiendo solicitudes nuevas a medida que se liberan slots, en lugar de esperar a que un grupo fijo termine por completo
    - d) Solo se aplica a stacks de serving en CPU como llama.cpp

<details markdown="1"><summary>Comprobación</summary>

**c)** Mantiene el lote lleno de forma continua. (a) es falsa: la aritmética por paso no cambia; la ganancia son menos slot-steps desperdiciados. (b) es falsa y al revés: la caché de una secuencia terminada se libera como parte de expulsarla, en cualquiera de los dos estilos de scheduling. (d) es falsa: el batching continuo es una técnica de scheduling de serving en GPU, la más asociada con vLLM y motores similares.

</details>

4. ▢ Un lote estático de 8 solicitudes necesita exactamente 50 tokens de salida cada una. ¿Mejoraría el batching continuo el throughput respecto del batching estático para este lote concreto, y por qué sí o por qué no?

<details markdown="1"><summary>Comprobación</summary>

Apenas, si es que lo hace. La ganancia del batching continuo viene de rellenar los slots que liberan las solicitudes que terminan antes mientras otras siguen ejecutándose. Cuando todas las solicitudes del grupo necesitan exactamente el mismo número de tokens, no hay solicitudes que terminen antes ni slots inactivos que rellenar, así que el batching estático ya no desperdicia nada aquí.

</details>

## Prácticas en el mundo real

- [ ] Encuentra el parámetro u opción de configuración que usa tu stack de serving preferido para habilitar el batching continuo (vLLM lo habilita por defecto; mira cómo llama su documentación al mecanismo subyacente).
- [ ] Mira una muestra real de tráfico o un log de solicitudes al que tengas acceso (o un dataset público de longitudes de solicitudes de LLM) y estima la dispersión entre la longitud de salida más corta y la más larga. Estima la fracción de desperdicio del batching estático que causaría esa dispersión.
- [ ] Mañana: lee un párrafo sobre cómo decide un scheduler de batching continuo qué solicitud en espera admitir a continuación, y anota si es un simple orden de llegada u otra cosa.

## Para profundizar

- [Article: "How continuous batching enables 23x throughput in LLM inference while reducing p50 latency", Anyscale](https://www.anyscale.com/blog/continuous-batching-llm-inference)
- [Docs: vLLM Documentation, vLLM Project](https://docs.vllm.ai/en/latest/)
- [Recursos](../RESOURCES.md)

---

¿No termina de quedar claro? Vuelve a leer la fuente primaria de arriba, ya que esta lección la comprime y en la compresión es donde se escapa la comprensión. Consulta el [glosario](../GLOSSARY.md) por si algún término te resultó resbaladizo.

Si lo poco claro es la propia lección y no el material, eso es un defecto: [abre un issue](https://github.com/TokenCemetery/teach/issues).
