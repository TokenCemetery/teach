---
title: "6. El compromiso entre throughput y latencia"
description: "Cómo el tamaño de lote intercambia throughput por latencia por token, y cómo defender una configuración de batching frente a un presupuesto de latencia declarado"
type: lesson
---

# Lección 6. El compromiso entre throughput y latencia

**Vínculo con la misión:** Este es el cierre de la etapa 2: defender una configuración de batching para una carga de trabajo declarada significa poner una cifra al compromiso entre throughput y latencia que describieron las lecciones 4 y 5, frente a un presupuesto de latencia y al techo de capacidad que calculó la lección 2.
**Fuente principal:** [Docs: vLLM Documentation, vLLM Project](https://docs.vllm.ai/en/latest/)
**Requisitos previos:** [Lección 5](0005-request-scheduling.md), [Lección 2](0002-capacity-and-batch-size.md), [KV cache](../GLOSSARY.md)

## Calentamiento

1. ▢ ¿Por qué agrupar los pasos de decode de más secuencias aumenta el throughput sin un aumento proporcional del tráfico de memoria?

<details markdown="1"><summary>Comprobación</summary>

El tráfico de memoria de un paso de decode, que lee los pesos y las KV caches residentes, apenas cambia tanto si calcula el siguiente token de una secuencia como el de varias. El batching reparte ese mismo tráfico entre más cómputo útil.

</details>

2. ▢ ¿Qué es el techo de capacidad de la lección 2, en una frase?

<details markdown="1"><summary>Comprobación</summary>

`(total memory − weights − overhead) / (bytes per token × context length)`: el número máximo de secuencias concurrentes que permite el presupuesto de KV cache, independiente de cualquier cosa sobre la latencia.

</details>

## Qué debes saber

### Los lotes más grandes hacen dos cosas a la vez, y tiran en direcciones opuestas

Añadir otra secuencia a un lote aumenta el throughput: se producen más tokens por segundo, agregados entre todas las secuencias del paso. Pero toda secuencia de un paso de lote avanza junta (lección 5), así que apilar el trabajo de decode de más secuencias en un paso también hace que ese paso tarde más. El retardo entre los tokens sucesivos de una misma secuencia, su latencia entre tokens, crece con el lote con el que comparte paso. El throughput y la latencia por token se mueven juntos, no en contra uno del otro de forma independiente: subir uno sube también el otro.

### La curva tiene dos regímenes

Con tamaños de lote pequeños, el decode está limitado por el ancho de banda de memoria (lección 4): las mismas lecturas de pesos y de caché ya dominan el costo del paso, así que añadir otra secuencia es casi gratis. El throughput sube aproximadamente de forma lineal con el tamaño de lote mientras la latencia del paso apenas se mueve. Pasado cierto tamaño de lote, hay tanto trabajo apilado que el cómputo bruto de la GPU, y no su ancho de banda de memoria, se convierte en el cuello de botella: la latencia del paso empieza a subir de forma notable con cada secuencia añadida, y cada secuencia adicional compra menos throughput extra que la anterior. Esa inflexión es la misma distinción entre limitado por el ancho de banda de memoria y limitado por cómputo que trazó la lección 3 entre prefill y decode, que ahora ocurre dentro del propio decode a medida que crece el lote.

![Latencia por token frente al tamaño de lote: 15 ms con 8, 25 ms con 32, 45 ms con 64, 90 ms con 128. La curva se mantiene plana mientras el decode está limitado por el ancho de banda de memoria, y luego sube con fuerza cuando el cómputo se convierte en el cuello de botella. Un presupuesto de latencia de 30 ms, marcado con una línea discontinua, se cruza entre el tamaño de lote 32 y 64.](images/throughput-latency-tradeoff.svg)

### Defender una configuración significa elegir un punto de esa curva, no el mayor número disponible

Una carga de trabajo declarada da dos restricciones independientes, y la configuración que merece defenderse es el mayor tamaño de lote que satisface ambas:

- **Un presupuesto de latencia**: un techo declarado para la latencia entre tokens (por ejemplo, ningún token de salida debe tardar más de cierto número de milisegundos en llegar).
- **El techo de capacidad**: el máximo derivado de la memoria de la lección 2, que no dice nada sobre la latencia y lo dice todo sobre si la caché cabe siquiera.

Un tamaño de lote por debajo de ambas restricciones deja sobre la mesa throughput que el presupuesto habría podido permitirse. Un tamaño de lote por encima del presupuesto de latencia cambia una violación de latencia por un throughput que nadie pidió. La cifra defendida es la menor entre lo que permite el presupuesto y lo que permite la capacidad, y el razonamiento para elegirla es la respuesta a "por qué esta cifra y no otra", que es lo que significa realmente defender una configuración.

## Práctica

1. ▢ Un stack de serving se evaluó con cuatro tamaños de lote: 8 (15 ms/token), 32 (25 ms/token), 64 (45 ms/token), 128 (90 ms/token). El presupuesto de latencia declarado es de 30 ms/token. ¿Cuál de estos tamaños de lote es el mayor que satisface el presupuesto?

<details markdown="1"><summary>Comprobación</summary>

32, con 25 ms/token. 64 y 128 superan el presupuesto de 30 ms; 32 es el mayor de los cuatro que se mantiene por debajo.

</details>

2. ▢ Continuando la pregunta 1: el techo de capacidad de KV cache de esta carga de trabajo, calculado como lo hace la lección 2, resulta ser de 100 secuencias concurrentes. ¿Qué tamaño de lote debería defenderse realmente, y qué restricción es la que limita?

<details markdown="1"><summary>Pista</summary>

La cifra defendida es la menor de lo que permite cada restricción por sí sola.

</details>

<details markdown="1"><summary>Comprobación</summary>

Un tamaño de lote de 32. Aquí limita el presupuesto de latencia, ya que 32 está muy por debajo del techo de capacidad de 100 secuencias; a la caché le sobra espacio, pero al presupuesto de latencia no.

</details>

3. ▢ Supón que el techo de capacidad hubiera resultado ser de 20 secuencias, con todo lo demás de la pregunta 1 sin cambios. ¿Qué tamaño de lote debería defenderse ahora, y por qué?

<details markdown="1"><summary>Comprobación</summary>

Un tamaño de lote de 20. Ahora limita el techo de capacidad en lugar del presupuesto de latencia: 32 satisfaría el presupuesto de 30 ms/token, pero la caché no puede contener tantas secuencias concurrentes, así que la restricción de memoria fija la cifra más baja de lo que habría hecho la latencia por sí sola.

</details>

4. ▢ Un equipo elige un tamaño de lote de 8 para la carga de trabajo de la pregunta 1, muy por debajo tanto de la elección de 32 guiada por el presupuesto de latencia como del techo de capacidad de 100 secuencias. ¿Cuál es el costo de esa elección?

<details markdown="1"><summary>Comprobación</summary>

Throughput que se deja sobre la mesa. Con 8, la latencia del paso (15 ms/token) está muy por debajo del presupuesto de 30 ms, lo que significa que el presupuesto podría permitirse un lote mayor, y la caché tiene mucho más espacio del que usan 8 secuencias. No se viola nada, pero el servidor atiende menos solicitudes concurrentes de las que podría defender.

</details>

## Prácticas en el mundo real

- [ ] Encuentra el parámetro de tu stack de serving para el tamaño máximo de lote (vLLM: `--max-num-seqs`) y lee qué dice su documentación sobre ajustarlo frente a un objetivo de latencia.
- [ ] Si tienes acceso a un servidor en ejecución o a sus benchmarks, grafica (o encuentra) su throughput y su latencia por token con unos cuantos tamaños de lote, y localiza aproximadamente dónde empieza el régimen limitado por cómputo.
- [ ] Mañana: elige un presupuesto de latencia que de verdad querrías defender para una carga de trabajo que te importe, y anota, en una frase, por qué esa cifra y no una más estricta o más laxa.

## Para profundizar

- [Docs: vLLM Documentation, vLLM Project](https://docs.vllm.ai/en/latest/)
- [Article: "How continuous batching enables 23x throughput in LLM inference while reducing p50 latency", Anyscale](https://www.anyscale.com/blog/continuous-batching-llm-inference)
- [Recursos](../RESOURCES.md)

---

¿No termina de quedar claro? Vuelve a leer la fuente primaria de arriba, ya que esta lección la comprime y en la compresión es donde se escapa la comprensión. Consulta el [glosario](../GLOSSARY.md) por si algún término te resultó resbaladizo.

Si lo poco claro es la propia lección y no el material, eso es un defecto: [abre un issue](https://github.com/TokenCemetery/teach/issues).
