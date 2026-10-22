---
title: "vLLM"
description: "Poner en marcha vLLM, los parámetros que llevan los conceptos de las etapas 1-3, la tabla de bloques de PagedAttention y un procedimiento de decisión de síntoma a parámetro"
type: reference
---

# vLLM

El stack de serving en GPU. Pensado para consultar al poner en marcha o ajustar un servidor.

## Poner en marcha un servidor

```bash
pip install vllm
vllm serve meta-llama/Llama-2-7b-hf
```

Arranca un servidor HTTP compatible con OpenAI en el puerto 8000. Una solicitud se parece a cualquier llamada de chat completion de OpenAI:

```bash
curl http://localhost:8000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{"model": "meta-llama/Llama-2-7b-hf", "messages": [{"role": "user", "content": "Say hello"}]}'
```

El campo `"model"` de la solicitud tiene que coincidir con el modelo con el que se arrancó el servidor.

## Parámetros que llevan la aritmética de las etapas 1-3

| Parámetro | Lleva |
|---|---|
| `--max-num-seqs` | El tope de tamaño de lote [defendido frente a un presupuesto de latencia](batching.md#defending-a-configuration) |
| `--kv-cache-dtype` | La [precisión de la caché](kv-cache.md#cache-precision-is-a-lever-independent-of-the-models-own-weights), p. ej. `fp8`, independiente de la precisión de los propios pesos del modelo |
| `--quantization` | El esquema (`gptq`, `awq`, ...) [elegido y defendido](quantization-at-serve-time.md) para un checkpoint ya cuantizado |

El batching continuo y el chunked prefill vienen activados por defecto; no hay un parámetro para desactivar el mecanismo básico, solo para ajustar en torno a él (como el tamaño de chunk). Omitir `--quantization` sirve el checkpoint con la precisión en que se guardó, lo más habitual fp16 o bf16; no se cuantiza nada al cargar.

<a id="pagedattention"></a>

## PagedAttention

La caché de cada secuencia se divide en **bloques** de tamaño fijo (16 tokens por defecto); una **tabla de bloques** por secuencia asigna posiciones lógicas de token a ubicaciones físicas de bloque, la misma idea que una tabla de páginas de un SO.

**El tamaño de bloque es un compromiso:**

| Tamaño de bloque | Espacio desperdiciado en el último bloque, parcialmente lleno | Contabilidad de la tabla de bloques |
|---|---|---|
| Mayor | Más | Menos |
| Menor | Menos | Más |

**Ejemplo resuelto**: una secuencia de 40 tokens con un tamaño de bloque de 16 tokens usa `ceil(40/16) = 3` bloques; el tercero contiene 8 tokens y desperdicia los otros 8 huecos.

**Compartición de bloques**: las tablas de bloques de dos secuencias pueden apuntar al mismo bloque físico cuando el contenido es idéntico, lo más habitual un prefijo de prompt compartido. El muestreo paralelo y el beam search son los casos más claros: la tabla de cada muestra apunta a los mismos bloques del prompt hasta que el token generado por una muestra diverge, y en ese punto un **copy-on-write** da solo a esa muestra una copia privada del bloque que se modifica.

**Ejemplo resuelto**, 10 muestras paralelas del mismo prompt de 200 tokens, bloques de 16 tokens: una copia necesita `ceil(200/16) = 13` bloques. Sin compartición: `13 × 10 = 130` bloques. Con compartición: 13 bloques, hasta que alguna muestra empiece a divergir.

## Dos parámetros de ajuste más

| Parámetro | Qué controla | Compromiso |
|---|---|---|
| `--gpu-memory-utilization` | Fracción de la memoria de una GPU que vLLM puede usar para pesos, caché y su propia sobrecarga (por defecto ~0.9) | Subirlo hacia 1.0 aumenta el techo de capacidad de la caché pero deja menos margen para cualquier otra cosa que comparta la GPU |
| `--tensor-parallel-size` | Divide los pesos y el cómputo de un modelo entre varias GPU | Reparte el modelo en lugar de reducirlo (sin costo de precisión, a diferencia de la cuantización); combinable con la cuantización cuando ninguna de las dos basta por sí sola |

`--gpu-memory-utilization` cambia lo que significa "memoria total" en [la fórmula del techo de capacidad](kv-cache.md#capacity-budget): en una GPU de 80 GB con el valor por defecto de ~0.9, solo ~72 GB, no 80 GB, es lo que debería usar la fórmula.

## De síntoma a parámetro

| Síntoma | Qué revisar |
|---|---|
| No arranca, o reporta muy poca memoria para la caché | Primero `--gpu-memory-utilization`; si aun así no cabe al 100%, es [el caso limitado por memoria](quantization-at-serve-time.md#picking-a-scheme-name-the-binding-constraint-first): cuantiza, añade `--tensor-parallel-size`, o ambos |
| El decode es más lento que el presupuesto de latencia | `--max-num-seqs` frente al [tamaño de lote defendido](batching.md#the-throughputlatency-trade-off), y luego si cuantizar los pesos o `--kv-cache-dtype` está justificado por cifras medidas |
| Una solicitud detiene los tokens de todas las demás secuencias | [Head-of-line blocking](batching.md#admission-order-and-head-of-line-blocking): revisa el tamaño de chunk del chunked prefill, no el tamaño de lote |
| La memoria parece desperdiciada entre muestras paralelas del mismo prompt | La compartición de bloques de arriba: verifica que realmente está ocurriendo antes de tocar el tamaño de lote o la utilización de memoria |

## Relacionado

- [Lección 10](../lessons/0010-standing-up-vllm.md), [Lección 11](../lessons/0011-pagedattention.md), [Lección 12](../lessons/0012-vllm-tuning-knobs.md)
- [KV cache](kv-cache.md), [Batching](batching.md), [Cuantización al servir](quantization-at-serve-time.md): los conceptos que llevan estos parámetros
