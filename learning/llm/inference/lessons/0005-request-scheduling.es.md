---
title: "5. Scheduling de solicitudes"
description: "Cómo un scheduler de batching continuo elige la siguiente solicitud, y por qué un prefill grande puede detener a todos los demás"
type: lesson
---

# Lección 5. Scheduling de solicitudes

**Vínculo con la misión:** El batching continuo, de la lección 4, solo ayuda si el scheduler que admite solicitudes en él no crea por sí mismo un problema nuevo de latencia; esta lección es donde vive ese compromiso.
**Fuente principal:** [Docs: vLLM Documentation, vLLM Project](https://docs.vllm.ai/en/latest/)
**Requisitos previos:** [Lección 4](0004-static-vs-continuous-batching.md), [KV cache](../GLOSSARY.md)

## Calentamiento

1. ▢ En el batching continuo, ¿qué pasa en el instante en que una secuencia del lote termina de generar?

<details markdown="1"><summary>Comprobación</summary>

Su slot se libera de inmediato, y se admite en él una solicitud nueva que esperaba en el paso siguiente, en lugar de que el slot quede inactivo hasta que un grupo fijo de solicitudes termine junto.

</details>

2. ▢ ¿Por qué el prefill está limitado por cómputo mientras que el decode está limitado por el ancho de banda de memoria?

<details markdown="1"><summary>Comprobación</summary>

El prefill procesa un prompt entero en una gran pasada forward paralela, así que hay suficiente trabajo por byte leído para mantener ocupado el cómputo de la GPU. El decode calcula solo un token nuevo por paso, así que el tráfico de memoria de cada paso (leer la caché y los pesos) domina sobre la pequeña cantidad de cómputo nuevo.

</details>

## Qué debes saber

### Qué solicitud en espera va a continuación

Un scheduler que mantiene una cola de solicitudes en espera necesita una política para decidir cuál admitir en un slot que acaba de liberarse. El valor por defecto simple, y lo que usa vLLM sin otra configuración, es **first-come, first-served (FCFS)**: las solicitudes se admiten por orden de llegada. No es la única política posible (un scheduler podría priorizar por longitud esperada, o por un presupuesto de latencia declarado), pero FCFS es el valor por defecto correcto para conocer primero: es simple, es justo en el sentido de que ninguna solicitud espera detrás de una que llegó más tarde, y toda política más elaborada es una variación del mismo mecanismo de admitir en un slot liberado que describió la lección 4.

### Un paso de lote es atómico, y eso crea un problema nuevo

Toda secuencia que comparte un paso de lote avanza junta: la latencia de todo el paso la fija el trabajo más costoso que contiene. Admitir una solicitud nueva significa que su trabajo de prefill tiene que ocurrir en algún sitio, y el lugar más directo es el paso de lote inmediato siguiente, junto con los pasos de decode que necesiten las secuencias que ya se ejecutan.

Eso está bien cuando el prompt de la solicitud nueva es corto. No lo está cuando es largo: un prefill de 6,000 tokens metido en un solo paso domina ahora la latencia de ese paso, y todas las demás secuencias del lote, secuencias que solo necesitaban un paso de decode pequeño y rápido, esperan a que termine antes de que cualquiera reciba su siguiente token. Una sola admisión grande detiene el progreso de todos los demás. Es un problema de **head-of-line blocking**: la cola está bien, pero lo que se ejecuta ahora no.

### El chunked prefill acota el daño

El **chunked prefill** divide el prefill de un prompt grande en piezas más pequeñas e intercala cada pieza con los pasos de decode en curso del lote, en lugar de ejecutar todo el prefill en un paso. Cada paso de lote admite ahora solo una cantidad acotada de trabajo nuevo de prefill, la que quepa en el presupuesto de latencia del paso, en lugar de todo lo que contenga el prompt de una solicitud recién admitida. El compromiso es que el prefill de la propia solicitud nueva tarda ahora varios pasos en terminar en lugar de uno, pero ninguna otra secuencia del lote se detiene esperándolo.

![Arriba: sin chunking, todo el prefill de un prompt grande se mete en un paso, que hincha su latencia muy por encima de los pasos de decode constantes de 20 ms mientras todas las demás secuencias esperan. Abajo: el chunked prefill divide el prefill del mismo prompt en piezas pequeñas intercaladas con el decode, manteniendo cada paso cerca de 20 ms a costa de que el prefill de la solicitud nueva tarde más pasos en terminar.](images/chunked-prefill.svg)

## Práctica

1. ▢ Un lote continuo ejecuta pasos constantes de solo decode de unos 20 ms cada uno. Se admite un prompt de 6,000 tokens y todo su prefill se mete en el paso inmediato siguiente, sin chunking. ¿Qué pasa con la latencia de ese paso y quién sufre el efecto?

<details markdown="1"><summary>Comprobación</summary>

Ese paso tiene ahora que completar el cómputo de prefill de los 6,000 tokens del prompt, además del trabajo de decode de todas las demás secuencias del lote, porque todo el lote avanza junto en un paso. La latencia del paso se hincha muy por encima de 20 ms, y todas las demás secuencias del lote, incluidas las que solo necesitaban un paso de decode rápido, esperan a que termine ese único paso antes de recibir su siguiente token.

</details>

2. ▢ ¿Cómo evita el chunked prefill el bloqueo descrito en la pregunta 1?

<details markdown="1"><summary>Pista</summary>

Piensa en qué cambia por paso, no en qué cambia de la cantidad total de trabajo de prefill necesaria.

</details>

<details markdown="1"><summary>Comprobación</summary>

En lugar de ejecutar el prompt entero de la solicitud nueva en un paso, el scheduler divide su prefill en piezas más pequeñas e intercala cada pieza con los pasos de decode normales del lote, admitiendo solo una cantidad acotada de trabajo nuevo de prefill por paso. La latencia de cualquier paso individual se mantiene acotada; el prefill de la propia solicitud nueva simplemente tarda más pasos en total en terminar.

</details>

3. ▢ ¿Qué afirmación es verdadera del chunked prefill?

    - a) Elimina por completo el prefill y trata cada token como un paso de decode
    - b) Acota la latencia añadida a un paso al dividir un prefill grande en piezas
    - c) Es una técnica específica de stacks de serving en CPU como llama.cpp
    - d) Reduce cuánta KV cache necesita un prompt largo una vez procesado por completo

<details markdown="1"><summary>Comprobación</summary>

**b)** Acota la latencia añadida a un paso al dividir un prefill grande en piezas intercaladas con el decode. (a) es falsa: el prompt sigue necesitando el procesamiento completo de prefill, solo repartido en más pasos. (c) es falsa: es una técnica de scheduling de batching continuo en GPU. (d) es falsa: el tamaño final de la caché de un prompt procesado por completo no cambia; el chunking solo cambia cómo se reparte en el tiempo el trabajo para llegar a él.

</details>

4. ▢ ¿Habría evitado el bloqueo de la pregunta 1 solo la admisión FCFS (sin chunking)?

<details markdown="1"><summary>Comprobación</summary>

No. FCFS solo decide qué solicitud en espera se admite a continuación; no dice nada sobre cuánto del trabajo de prefill de esa solicitud cae en un solo paso una vez admitida. El bloqueo viene de meter un prefill grande entero en un único paso de lote atómico, que lo arregla el chunking, no el orden de admisión.

</details>

## Prácticas en el mundo real

- [ ] Encuentra el parámetro u opción de configuración de tu stack de serving para el chunked prefill (vLLM: habilitado por defecto en versiones recientes; mira en su documentación el ajuste del tamaño de chunk) y lee cuál es el tamaño de chunk por defecto.
- [ ] Estima, para una carga de trabajo de la que tengas datos de longitud de solicitudes, con qué frecuencia un prompt sería lo bastante largo para detener de forma notable un paso del lote sin chunking.
- [ ] Mañana: lee un párrafo sobre cómo decide un scheduler entre admitir el chunk de prefill de una solicitud nueva o continuar uno en curso, cuando ambos compiten por el presupuesto del mismo paso.

## Para profundizar

- [Docs: vLLM Documentation, vLLM Project](https://docs.vllm.ai/en/latest/)
- [Article: "How continuous batching enables 23x throughput in LLM inference while reducing p50 latency", Anyscale](https://www.anyscale.com/blog/continuous-batching-llm-inference)
- [Recursos](../RESOURCES.md)

---

¿No termina de quedar claro? Vuelve a leer la fuente primaria de arriba, ya que esta lección la comprime y en la compresión es donde se escapa la comprensión. Consulta el [glosario](../GLOSSARY.md) por si algún término te resultó resbaladizo.

Si lo poco claro es la propia lección y no el material, eso es un defecto: [abre un issue](https://github.com/TokenCemetery/teach/issues).
