---
title: "10. Poner en marcha vLLM"
description: "Instalar vLLM, lanzar su servidor y encontrar los parámetros que llevan los conceptos ya enseñados"
type: lesson
---

# Lección 10. Poner en marcha vLLM

**Vínculo con la misión:** Cada fórmula de las etapas 1 a 3, la huella de la caché, el tamaño de lote, el esquema de cuantización, se convierte en esta lección en un parámetro real de un comando real; aquí es donde la aritmética se vuelve un servidor que responde solicitudes.
**Fuente principal:** [Docs: vLLM Documentation, vLLM Project](https://docs.vllm.ai/en/latest/)
**Requisitos previos:** [Lección 9](0009-picking-a-quantization-scheme.md), [KV cache](../GLOSSARY.md)

## Calentamiento

1. ▢ Un servidor supera su presupuesto de latencia con el tamaño de lote actual. ¿Qué parámetro, según el razonamiento de la lección 6, es el primero que hay que revisar?

<details markdown="1"><summary>Comprobación</summary>

El ajuste del tamaño máximo de lote: el mayor tamaño de lote que aún satisface el presupuesto de latencia es lo que defendió la lección 6, así que ese es el parámetro que lo controla directamente.

</details>

2. ▢ ¿Por qué tendría sentido alguna vez, en tiempo de serving, elegir fp8 para la KV cache en lugar de la precisión de los propios pesos del modelo (lección 3)?

<details markdown="1"><summary>Comprobación</summary>

La precisión de la caché es una palanca independiente de la precisión de los propios pesos del modelo. Reducir a la mitad el `bytes_per_value` de la caché reduce a la mitad su huella, sin cambiar el modelo en sí, y recupera capacidad del mismo modo que lo haría un modelo más pequeño.

</details>

## Qué debes saber

### Instalar vLLM

vLLM se instala como un paquete de Python, `pip install vllm`, y requiere una GPU compatible con CUDA; es la mitad de GPU de la misión de este espacio de trabajo, y llama.cpp cubre CPU y edge en la etapa siguiente. La instalación trae automáticamente un PyTorch y un toolchain de CUDA compatibles para las configuraciones habituales, lo que conviene contrastar con la versión instalada del driver de CUDA antes de suponer que una instalación fallida se debe a otra cosa.

### Lanzar el servidor

`vllm serve <model>` arranca un servidor HTTP compatible con OpenAI para el modelo indicado (una ruta local o un identificador del Hugging Face Hub), escuchando por defecto en el puerto 8000:

```text
vllm serve meta-llama/Llama-2-7b-hf
```

Este único comando hace la descarga (si hace falta), la carga de pesos y el arranque del servidor sobre cuyas consecuencias de memoria y latencia razonaban todas las etapas 1 a 3.

### Enviar una solicitud

Como el servidor habla con la forma de la API de OpenAI, una solicitud se parece a cualquier llamada de chat completion de OpenAI, dirigida al servidor local en su lugar:

```bash
curl http://localhost:8000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{"model": "meta-llama/Llama-2-7b-hf", "messages": [{"role": "user", "content": "Say hello"}]}'
```

### Dónde aparecen como parámetros los conceptos ya enseñados

La línea de comandos es donde las etapas 1 a 3 dejan de ser aritmética y se convierten en configuración:

- `--max-num-seqs`: el tope de tamaño de lote que la lección 6 enseñó a defender frente a un presupuesto de latencia.
- `--kv-cache-dtype`: la precisión de la caché que la lección 3 presentó como una palanca independiente de los propios pesos del modelo (por ejemplo, `fp8`).
- `--quantization`: nombra el esquema, como `gptq` o `awq`, que las lecciones 7 a 9 enseñaron a elegir y defender, al servir un checkpoint ya cuantizado.
- El batching continuo y el chunked prefill (lecciones 4 y 5) vienen activados por defecto; no hay un parámetro para desactivar el mecanismo básico, solo para ajustar en torno a él, como el tamaño de chunk.

## Práctica

1. ▢ Un equipo ejecuta `vllm serve some-model --max-num-seqs 32 --kv-cache-dtype fp8`. En términos de las lecciones 6 y 3, ¿qué controla realmente cada uno de estos dos parámetros?

<details markdown="1"><summary>Comprobación</summary>

`--max-num-seqs 32` limita el tamaño de lote a 32, la cifra que defendería la lección 6 frente a un presupuesto de latencia declarado y al techo de capacidad de la lección 2. `--kv-cache-dtype fp8` guarda la KV cache en fp8 en lugar del valor por defecto, reduciendo a la mitad su huella por token independientemente de la precisión de los propios pesos del modelo, exactamente la palanca que describió la lección 3.

</details>

2. ▢ Un equipo arranca un servidor con `vllm serve some-model`, sin nombrar ningún parámetro `--quantization`. ¿A qué precisión sirve el servidor el modelo, y por qué?

<details markdown="1"><summary>Comprobación</summary>

A la precisión en que se guardó el propio checkpoint, lo más habitual fp16 o bf16, ya que no se pidió ningún esquema de cuantización. `--quantization` solo se aplica al servir un checkpoint que se cuantizó de antemano o que el parámetro indica a vLLM cuantizar al cargar; omitirlo significa que no se cuantiza nada.

</details>

3. ▢ Predice, antes de comprobar: tras ejecutar `vllm serve` con éxito, ¿qué única información de la solicitud curl de la sección Qué debes saber de esta lección tiene que coincidir con algo con lo que se arrancó realmente el servidor, o la solicitud fallará?

<details markdown="1"><summary>Pista</summary>

Mira el campo `"model"` del comando curl.

</details>

<details markdown="1"><summary>Comprobación</summary>

El campo `"model"` del cuerpo de la solicitud tiene que coincidir con el nombre (o la ruta) del modelo con el que se arrancó el servidor. El servidor sirve un modelo a la vez; nombrar otro distinto en la solicitud es lo que produce con más frecuencia un error en una llamada por lo demás bien formada.

</details>

4. ▢ ¿Qué afirmación es verdadera del comportamiento por defecto de vLLM cuando no se da ningún parámetro de batching ni de caché?

    - a) Recurre al batching estático hasta que se establece `--max-num-seqs`
    - b) El batching continuo y el chunked prefill se ejecutan por defecto; los parámetros solo los ajustan más
    - c) Se niega a arrancar hasta que se elige explícitamente un dtype de la KV cache
    - d) Sirve por defecto a la precisión más baja que admite el hardware

<details markdown="1"><summary>Comprobación</summary>

**b)** El batching continuo y el chunked prefill son el mecanismo por defecto, no algo que active un parámetro; los parámetros disponibles ajustan valores en torno a ellos, como el tamaño máximo de lote o un tamaño de chunk. (a) es falsa: no hay un recurso de batching estático. (c) es falsa: si no se nombra ninguno, se usa un dtype de caché por defecto. (d) es falsa: el valor por defecto es la precisión guardada del propio checkpoint, no la más baja que admite el hardware.

</details>

## Prácticas en el mundo real

- [ ] Instala vLLM (`pip install vllm`) en una máquina con una GPU compatible con CUDA, y ejecuta `vllm serve` con un modelo pequeño que puedas permitirte descargar.
- [ ] Envía la solicitud curl de esta lección contra tu servidor en ejecución, y confirma que recibes una completion real, no un error.
- [ ] Mañana: reinicia el servidor con `--max-num-seqs` fijado a un número pequeño (como 2) y a uno grande, y comprueba si puedes observar una diferencia en cómo se comporta con unas pocas solicitudes concurrentes.

## Para profundizar

- [Docs: vLLM Documentation, vLLM Project](https://docs.vllm.ai/en/latest/)
- [Recursos](../RESOURCES.md)

---

¿No termina de quedar claro? Vuelve a leer la fuente primaria de arriba, ya que esta lección la comprime y en la compresión es donde se escapa la comprensión. Consulta el [glosario](../GLOSSARY.md) por si algún término te resultó resbaladizo.

Si lo poco claro es la propia lección y no el material, eso es un defecto: [abre un issue](https://github.com/TokenCemetery/teach/issues).
