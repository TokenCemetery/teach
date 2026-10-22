---
title: "1. La KV cache"
description: "Por qué la generación se vuelve costosa y qué recupera el uso de una caché"
type: lesson
---

# Lección 1. La KV cache

**Vínculo con la misión:** Cada cifra de latencia y throughput que defiende este espacio de trabajo se remonta a lo que cuesta la KV cache en memoria y a lo bien que un servidor gestiona ese costo.
**Fuente principal:** [Docs: "Optimizing inference", Hugging Face Transformers](https://huggingface.co/docs/transformers/main/en/llm_optims)
**Requisitos previos:** ninguno

## Qué debes saber

### Por qué el decode necesita una caché

Un transformer genera un token a la vez. Para producir el token *N*, la self-attention necesita los vectores key y value de cada token desde el 1 hasta el *N*, en cada capa. Sin una caché, cada token nuevo obliga al modelo a recalcular los keys y values de *todo* el prefijo otra vez, aunque esos vectores no cambian nunca una vez generado un token. Eso es trabajo cuadrático gastado en recalcular cosas ya calculadas.

La **KV cache** guarda los vectores key y value de cada token, por capa, en el momento en que se calculan por primera vez, de modo que generar el token *N+1* solo calcula un nuevo conjunto de vectores K/V y reutiliza el resto. Esto es lo que hace práctica la generación autorregresiva: cambia recomputación por memoria.

### Lo que cuesta realmente esa memoria

La caché no es gratis, y su tamaño es lo que gobierna cuántas solicitudes puede mantener un servidor en memoria a la vez. Por token y por capa, guarda un vector key y uno value, cada uno de tamaño igual a la dimensión oculta del modelo (`d_model`, la dimensión del residual stream del modelo). En media precisión (2 bytes por valor):

```text
bytes per token = 2 (K and V) × num_layers × d_model × 2 bytes
```

Toma Llama-2-7B como caso concreto: 32 capas, `d_model` = 4096.

```text
2 × 32 × 4096 × 2 bytes = 524,288 bytes ≈ 512 KB per token
```

Con un contexto de 4096 tokens, eso es `512 KB × 4096 ≈ 2 GB`, para una *sola* secuencia. Si mantienes 16 secuencias así de forma concurrente, solo la caché necesita ~32 GB, más que los 14 GB que ocupan los propios pesos del modelo en fp16. Esta es la aritmética detrás de por qué "simplemente añade más KV cache" es el instinto equivocado, y de por qué los stacks de serving se obsesionan con la memoria de la caché en lugar de tratarla como una ocurrencia tardía (consulta [Transformer Inference Arithmetic](https://kipp.ly/transformer-inference-arithmetic/), de Kipply, para la derivación completa, incluido cómo escala con esquemas de reparto de cabezas de atención como GQA/MQA).

### Dónde desperdicia memoria una caché ingenua

Una implementación ingenua reserva un bloque de memoria contiguo por secuencia, dimensionado para la longitud máxima que podría alcanzar. De ahí se siguen dos modos de fallo:

- **Fragmentación interna**: una secuencia que acaba siendo corta sigue reteniendo memoria reservada para la longitud máxima que nunca usó.
- **Fragmentación externa**: secuencias de longitudes reales distintas dejan huecos entre sus bloques reservados donde no cabe la caché de ninguna otra secuencia.

El paper de PagedAttention midió que los sistemas ingenuos mantenían tan solo entre el 20 y el 40% de la memoria de KV cache asignada guardando de verdad datos útiles. Su solución se toma directamente de la memoria virtual de los sistemas operativos: dividir la caché en bloques de tamaño fijo, guardarlos de forma no contigua y mantener una tabla de bloques por secuencia que asigna posiciones lógicas a bloques físicos. Esa es la idea en torno a la que se construye vLLM, y por eso el framework importa tanto como la aritmética: la misma caché, bien asignada, atiende muchas más solicitudes concurrentes.

![Arriba: los bloques contiguos ingenuos, dimensionados a la longitud máxima, desperdician memoria como fragmentación interna (reservada pero sin usar) y fragmentación externa (un hueco entre bloques). Abajo: los bloques no contiguos de tamaño fijo de PagedAttention se intercalan libremente, así que una secuencia retiene solo tantos bloques como ha usado realmente.](images/paged-attention-fragmentation.svg)

## Práctica

1. ▢ En una frase, ¿qué le permite saltarse la KV cache a un servidor en cada token generado después del primero?

<details markdown="1"><summary>Comprobación</summary>

Recalcular los vectores key y value de cada token previo de la secuencia, en cada capa. Solo hay que calcular los K/V del token nuevo; el resto se leen de la caché.

</details>

2. ▢ Un modelo tiene 40 capas y `d_model` = 5120, servido en fp16. Estima el tamaño de la KV cache para una secuencia con un contexto de 2048 tokens.

<details markdown="1"><summary>Pista</summary>

Usa `2 × num_layers × d_model × 2 bytes`, y multiplica por el número de tokens.

</details>

<details markdown="1"><summary>Comprobación</summary>

Por token: `2 × 40 × 5120 × 2 = 819,200 bytes ≈ 800 KB`.
Con 2048 tokens: `800 KB × 2048 ≈ 1.6 GB` para una secuencia.

</details>

3. ▢ Dos secuencias tienen bloques de KV cache ingenuos, contiguos y dimensionados a la longitud máxima. Una termina muy lejos de la longitud máxima que reservó. ¿Qué pasa con la memoria que reservó pero no usó, y qué le cuesta al servidor?

<details markdown="1"><summary>Comprobación</summary>

Queda reservada y no la puede usar ninguna otra secuencia hasta que se libere la caché de esa secuencia: fragmentación interna. El costo es que el servidor puede atender menos secuencias concurrentes, ya que la memoria que parece "asignada" no hace ningún trabajo útil.

</details>

4. ▢ ¿Qué afirmación es verdadera sobre la solución de PagedAttention?

    - a) Reduce el tamaño total de la KV cache para un modelo y una longitud de contexto dados
    - b) Elimina la KV cache y recalcula la atención bajo demanda
    - c) Reduce la memoria desperdiciada guardando la caché en bloques no contiguos de tamaño fijo
    - d) Solo ayuda a stacks de serving en CPU como llama.cpp

<details markdown="1"><summary>Comprobación</summary>

**c)** Reduce la memoria desperdiciada guardando la caché en bloques no contiguos de tamaño fijo, direccionados mediante una tabla de bloques por secuencia, la misma idea que la paginación de la memoria virtual de un SO.

(a) es falsa: el costo por token no cambia; solo se reduce el desperdicio que lo rodea. (b) es falsa: la caché sigue ahí, solo que mejor asignada. (d) es falsa: PagedAttention es una técnica de serving en GPU (vLLM); este espacio de trabajo cubre llama.cpp por separado.

</details>

## Prácticas en el mundo real

- [ ] Elige un modelo que planees servir. Calcula su tamaño de KV cache por token con la fórmula anterior, a partir de su `num_layers` y su tamaño oculto publicados.
- [ ] Calcula el tamaño total de los pesos de ese mismo modelo en la precisión en que lo servirías, y compáralo con el tamaño de la KV cache a su longitud máxima de contexto.
- [ ] Mañana: encuentra la documentación de un stack de serving (vLLM o llama.cpp) y localiza el parámetro que controla cuánta memoria reserva para la KV cache.

## Para profundizar

- [Article: "Transformer Inference Arithmetic", Kipply](https://kipp.ly/transformer-inference-arithmetic/)
- [Paper: "Efficient Memory Management for Large Language Model Serving with PagedAttention", Kwon et al., SOSP 2023](https://arxiv.org/abs/2309.06180)
- [Recursos](../RESOURCES.md)

---

¿No termina de quedar claro? Vuelve a leer la fuente primaria de arriba, ya que esta lección la comprime y en la compresión es donde se escapa la comprensión. Consulta el [glosario](../GLOSSARY.md) por si algún término te resultó resbaladizo.

Si lo poco claro es la propia lección y no el material, eso es un defecto: [abre un issue](https://github.com/TokenCemetery/teach/issues).
