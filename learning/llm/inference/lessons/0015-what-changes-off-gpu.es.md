---
title: "15. Qué cambia fuera de la GPU"
description: "Poner en marcha el servidor de llama.cpp, y cómo se ven de distinta manera el batching, la gestión de la caché y la cuantización a escala de CPU/edge"
type: lesson
---

# Lección 15. Qué cambia fuera de la GPU

**Vínculo con la misión:** Este es el cierre de la etapa 5 y la segunda mitad de los criterios de éxito de la misión: un stack de llama.cpp ejecutándose en CPU y respondiendo solicitudes reales, con cada concepto de las etapas 1 a 4 reexaminado para ver qué se sigue aplicando realmente a esta escala.
**Fuente principal:** [Repo: llama.cpp, ggml-org](https://github.com/ggml-org/llama.cpp)
**Requisitos previos:** [Lección 14](0014-llamacpp-architecture.md), [KV cache](../GLOSSARY.md)

## Calentamiento

1. ▢ ¿Qué controla `--threads` en llama.cpp, y en qué se diferencia de `--max-num-seqs` de vLLM?

<details markdown="1"><summary>Comprobación</summary>

`--threads` reparte las multiplicaciones de matrices de una sola secuencia entre los núcleos físicos de la CPU. `--max-num-seqs`, en cambio, limita cuántas secuencias concurrentes comparten un paso de lote en una GPU, amortizando entre ellas el tráfico de memoria. Uno acelera el cómputo de una secuencia; el otro reparte el costo del ancho de banda de memoria entre muchas.

</details>

2. ▢ Descifra el nombre de cuantización `Q4_K_M` en sus tres partes.

<details markdown="1"><summary>Comprobación</summary>

`Q4`: aproximadamente 4 bits por peso. `K`: un tipo k-quant, un mismo ancho de bits para todos los pesos de un tensor, con escalas por sub-bloque dentro de superbloques de 256. `M`: la receta media, que mezcla tipos k-quant entre tensores.

</details>

## Qué debes saber

### Poner en marcha el servidor

El propio servidor de llama.cpp, `llama-server`, carga un archivo GGUF y expone un endpoint HTTP compatible con OpenAI, la misma forma de solicitud que usó la lección 10 contra vLLM:

```text
llama-server -m model.Q4_K_M.gguf --threads 8
```

```bash
curl http://localhost:8080/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{"model": "model.Q4_K_M.gguf", "messages": [{"role": "user", "content": "Say hello"}]}'
```

La forma de la solicitud y de la respuesta es familiar. Lo que cambia es todo lo que hay por debajo.

![Una comparación de tres filas. Batching: en una GPU, el batching continuo amortiza el ancho de banda de memoria entre cientos de solicitudes concurrentes; a escala de CPU/edge, con solo de una cifra a unas pocas decenas de solicitudes concurrentes, lo sustituyen los threads que reparten el cómputo de una secuencia entre núcleos. Gestión de la caché: en una GPU, PagedAttention gestiona un pool compartido grande y en constante cambio; a escala de CPU/edge, basta una caché contigua simple por secuencia. Momento de la cuantización: en una GPU con vLLM, el esquema es un parámetro de serving elegido al lanzar; en llama.cpp, la decisión ya quedó fijada cuando se eligió un nivel de cuantización GGUF concreto, antes de que el servidor arranque siquiera.](images/gpu-vs-cpu-edge-mechanisms.svg)

### El batching importa menos a esta escala

El batching continuo de vLLM (lecciones 4 y 5) existe para amortizar el costo del ancho de banda de memoria de una GPU entre las solicitudes de cientos de desconocidos concurrentes. Una CPU no tiene el equivalente de miles de núcleos paralelos entre los que repartir ese costo; el servidor de llama.cpp sí admite un puñado de slots de solicitud paralelos, pero a una escala de una cifra a unas pocas decenas, no cientos. No es una función que falte: la carga de trabajo típica de un despliegue edge, un dispositivo que atiende a su propio usuario, rara vez tiene cientos de solicitudes concurrentes que agrupar en primer lugar. El batching intensivo resuelve un problema que el serving en CPU/edge normalmente no tiene.

### La caché tampoco necesita paginación a esta escala

PagedAttention (lección 11) existe para permitir que muchas secuencias compartan memoria de forma eficiente y para evitar la fragmentación en un pool grande y en constante cambio de solicitudes concurrentes. A escala de CPU/edge, con pocas secuencias concurrentes y sin un gran pool compartido que fragmentar, es común y suficiente una asignación de caché contigua más simple por secuencia. El problema que resuelve PagedAttention no desaparece en principio, simplemente rara vez llega a la escala en que su complejidad se amortiza.

### La decisión de cuantización ya ocurrió

En vLLM, `--quantization` es un parámetro de serving: el esquema se elige cuando arranca el servidor, a partir de un checkpoint ya cuantizado o de uno que se cuantiza al cargar. En llama.cpp, esa decisión se tomó antes, cuando se eligió (o se produjo) un archivo GGUF con un nivel de cuantización concreto, como `Q4_K_M`. No hay un parámetro de serving para cambiarla; cambiar la cuantización significa descargar o producir otro archivo GGUF. El compromiso de las lecciones 7 a 9, memoria frente a precisión frente a velocidad, sigue aplicándose, solo que queda resuelto antes de que el servidor arranque siquiera, no se configura al arrancar.

## Práctica

1. ▢ Llegan tres solicitudes a la vez a una instancia de `llama-server`, todas de los propios usuarios de un único dispositivo edge. Predice, antes de comprobar: ¿qué pasa con el throughput de cada solicitud, y por qué difiere de lo que hace el batching continuo en una GPU?

<details markdown="1"><summary>Comprobación</summary>

El throughput de cada solicitud baja aproximadamente en proporción a con cuántas solicitudes tiene que compartir ahora los threads, ya que el recuento fijo de núcleos de la CPU se reparte entre las solicitudes concurrentes en lugar de que cada una disponga del recuento completo de threads. Esto difiere del batching continuo en GPU, que amortiza un costo de ancho de banda de memoria que ya era necesario entre secuencias concurrentes con poco costo extra por secuencia; repartir el cómputo de la CPU entre solicitudes no tiene un costo equivalente de "ya se estaba pagando de todos modos" que amortizar.

</details>

2. ▢ ¿Por qué el batching continuo intensivo al estilo de vLLM importa menos en un despliegue típico de CPU/edge que en un servidor de GPU?

<details markdown="1"><summary>Comprobación</summary>

El batching continuo se gana su complejidad cuando las solicitudes de muchos desconocidos concurrentes comparten el costo del ancho de banda de memoria de una GPU. Un despliegue edge típico, un dispositivo que atiende a su propio usuario, rara vez tiene tantas solicitudes concurrentes que agrupar en primer lugar, así que el problema que resuelve el mecanismo normalmente no está presente a esta escala.

</details>

3. ▢ ¿Dónde se tomó la decisión de cuantización en un despliegue de llama.cpp, en comparación con dónde se toma en un despliegue de vLLM?

<details markdown="1"><summary>Comprobación</summary>

En llama.cpp, se tomó cuando se eligió o se produjo un archivo GGUF concreto (con un nivel de cuantización concreto, como `Q4_K_M`), antes de que el servidor arranque siquiera; cambiarla significa usar otro archivo. En vLLM, es un parámetro de serving, `--quantization`, elegido cuando se lanza el servidor. El compromiso en sí es el mismo que enseñaron las lecciones 7 a 9; solo difiere el momento en que la decisión queda fijada.

</details>

4. ▢ ¿Qué afirmación es verdadera sobre por qué la gestión de memoria al estilo de PagedAttention se necesita con menos frecuencia a escala de CPU/edge?

    - a) El hardware de CPU hace técnicamente imposible la paginación
    - b) La carga de trabajo típica tiene tan pocas secuencias concurrentes que basta una caché contigua más simple por secuencia
    - c) El formato GGUF de llama.cpp es incompatible con cualquier forma de memoria paginada
    - d) Las KV caches no existen en absoluto en el serving en CPU

<details markdown="1"><summary>Comprobación</summary>

**b)** Con pocas secuencias concurrentes y sin un gran pool compartido que fragmentar, normalmente basta un esquema de asignación más simple; el problema que resuelve PagedAttention rara vez llega a la escala en que su complejidad se amortiza. (a) es falsa: nada del hardware de CPU descarta la paginación, es un compromiso de diseño, no una limitación. (c) es falsa: GGUF describe el archivo del modelo, no la disposición de la caché del runtime. (d) es falsa: el decode sigue necesitando una KV cache en CPU, por la misma razón que estableció la lección 1; simplemente suele gestionarse de forma más sencilla.

</details>

## Prácticas en el mundo real

- [ ] Compila o instala llama.cpp, descarga un modelo GGUF pequeño y ejecuta `llama-server` con un número de threads ajustado al recuento de núcleos de tu CPU.
- [ ] Envía la solicitud curl de esta lección contra tu servidor en ejecución, y confirma que recibes una completion real.
- [ ] Mañana: envía dos o tres solicitudes a la vez a tu servidor en ejecución y observa, de manera informal, si cada una se siente más lenta que cuando es la única solicitud en curso.

## Para profundizar

- [Repo: llama.cpp, ggml-org](https://github.com/ggml-org/llama.cpp)
- [Docs: vLLM Documentation, vLLM Project](https://docs.vllm.ai/en/latest/)
- [Recursos](../RESOURCES.md)

---

¿No termina de quedar claro? Vuelve a leer la fuente primaria de arriba, ya que esta lección la comprime y en la compresión es donde se escapa la comprensión. Consulta el [glosario](../GLOSSARY.md) por si algún término te resultó resbaladizo.

Si lo poco claro es la propia lección y no el material, eso es un defecto: [abre un issue](https://github.com/TokenCemetery/teach/issues).
