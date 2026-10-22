---
title: "llama.cpp"
description: "El formato GGUF y su nomenclatura de cuantización, la abstracción de backends de ggml y qué cambia cuando el serving sale de la GPU"
type: reference
---

# llama.cpp

El stack de serving en CPU/edge. Pensado para consultar al poner en marcha o razonar sobre un despliegue de llama.cpp.

## GGUF

Un único archivo binario que agrupa pesos, tokenizer y metadatos de arquitectura, en lugar de los varios archivos separados (`config.json`, tokenizer, pesos) con los que se entrega un checkpoint de Hugging Face. Agrupar importa sobre todo en los despliegues edge: enviar un archivo para ejecutarlo con un binario pequeño y con pocas dependencias, sin Python ni el ecosistema de Hugging Face instalados para reensamblar las piezas.

Como GGUF dispone los pesos en un formato que el SO puede leer directamente, llama.cpp puede **mapear en memoria** el archivo (`mmap`) en lugar de leerlo de forma anticipada en la RAM y deserializarlo. Las páginas se leen del disco solo cuando algo las toca, y es la propia caché de páginas del SO la que gestiona lo que permanece residente. Importa sobre todo donde la RAM es el recurso más escaso, en hardware de CPU y edge, y menos en un servidor de GPU con RAM de sistema abundante.

### Nomenclatura de cuantización

GGUF lleva la propia familia de cuantización de llama.cpp, separada de GPTQ y AWQ, orientados a GPU. Descifrando un nombre como `Q4_K_M`:

| Parte | Significado |
|---|---|
| `Q4` | Ancho de bits: aproximadamente 4 bits por peso (también `Q5`, `Q8` y otros) |
| `K` | Un tipo **k-quant**: un ancho de bits por tensor, con superbloques de 256 pesos cuyos subbloques llevan cada uno su propia escala |
| `M` | La receta que mezcla tipos entre tensores, dando a algunos tensores un tipo de más bits: `S` (small), `M` (medium), `L` (large). Consulta [la hoja Medir y almacenar del track de cuantización](../../quantization/reference/measuring-and-storing.md) |

## ggml: una base de código, muchos backends

llama.cpp está construido sobre **ggml**, una biblioteca de tensores en C sin dependencias (no se exige ninguna BLAS externa). Una pasada forward es un grafo de cálculo estático, construido una vez y ejecutado después, en lugar de la ejecución eager operación por operación de PyTorch. Esa separación de "qué calcular" y "qué lo ejecuta" es lo que permite que el mismo grafo apunte a varios **backends**, CPU (AVX2/NEON), CUDA, Metal, Vulkan, desde una sola base de código y sin un runtime de Python, en hardware que va de la CPU ARM de un teléfono a la GPU Metal de un Mac y a una Raspberry Pi. El diseño de vLLM, por el contrario, es específico de CUDA y no puede ejecutarse sin una GPU de NVIDIA.

## Los threads sustituyen al batching en GPU

| | Reparte | Acotado por |
|---|---|---|
| Batching en GPU (`--max-num-seqs`) | El costo del ancho de banda de memoria entre secuencias concurrentes | La capacidad de la caché y el presupuesto de latencia |
| Threads de CPU (`--threads`) | Las multiplicaciones de matrices de una sola secuencia entre núcleos | El recuento de núcleos físicos de la CPU |

El threading acelera el propio cómputo de una secuencia; no tiene el equivalente de "ya se estaba pagando la lectura de memoria de todos modos" que amortizar entre las solicitudes de desconocidos como hace el batching en GPU.

## Poner en marcha el servidor

```text
llama-server -m model.Q4_K_M.gguf --threads 8
```

```bash
curl http://localhost:8080/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{"model": "model.Q4_K_M.gguf", "messages": [{"role": "user", "content": "Say hello"}]}'
```

La misma forma de solicitud compatible con OpenAI que [vLLM](vllm.md); lo que cambia es todo lo que hay por debajo.

## Qué cambia fuera de la GPU

| Mecanismo | En una GPU (vLLM) | A escala de CPU/edge (llama.cpp) |
|---|---|---|
| Concurrencia | El [batching continuo](batching.md) amortiza el ancho de banda de memoria entre las solicitudes de cientos de desconocidos concurrentes | Un puñado de slots paralelos (de una cifra a unas pocas decenas); una carga de trabajo edge típica, un dispositivo que atiende a su propio usuario, rara vez tiene cientos de solicitudes concurrentes que agrupar |
| Gestión de la caché | [PagedAttention](vllm.md#pagedattention) gestiona un pool compartido grande y en constante cambio | Basta una caché contigua más simple por secuencia; el problema que resuelve PagedAttention rara vez llega a la escala en que su complejidad compensa |
| Momento de la cuantización | Un parámetro de serving (`--quantization`), elegido al lanzar | Ya fijada cuando se eligió o se produjo un nivel de cuantización GGUF concreto; cambiarla significa usar otro archivo, no un parámetro |

Los compromisos en sí ([memoria, velocidad y precisión](quantization-at-serve-time.md)) no cambian; solo difiere cuándo se toma cada decisión y con qué concurrencia compensa.

## Relacionado

- [Lección 13](../lessons/0013-gguf.md), [Lección 14](../lessons/0014-llamacpp-architecture.md), [Lección 15](../lessons/0015-what-changes-off-gpu.md)
- [vLLM](vllm.md), [Batching](batching.md), [Cuantización al servir](quantization-at-serve-time.md): los mecanismos del lado de la GPU con los que contrasta esta hoja
