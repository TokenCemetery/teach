---
title: "Inferencia"
description: "Sirve un modelo: la KV cache, el batching, la cuantización al servir y un presupuesto de latencia que puedas defender"
type: topic
---

# Aprendizaje: inferencia

Sé capaz de poner en marcha un servidor de inferencia para un modelo real, primero en GPU y después en CPU/edge, y de defender los números de latencia y throughput que produce en lugar de citar lo que den por defecto los valores del framework.

**Última lección:** [25. Revisar una configuración de serving](lessons/0025-reviewing-a-serving-configuration.md)

## Cómo se ve el éxito

- Poner en marcha un stack de serving (vLLM en GPU, luego llama.cpp en CPU/edge) para un modelo dado y conseguir que responda solicitudes.
- Citar un presupuesto de latencia p99 para un tamaño de lote y un modelo dados, y defender la cifra a partir de las decisiones de KV cache, batching y cuantización que la produjeron.
- Revisar la configuración de serving de otra persona y nombrar con precisión qué cuesta (un parámetro mal ajustado frente al cuello de botella de la carga de trabajo declarada, una topología elegida sin un cuello de botella que la justifique, un despliegue que rompe a un cliente a mitad de camino), en lugar de decir que algo le suena mal.

## Restricciones

- Se asume soltura para ejecutar un entorno de ML en Python y un conocimiento básico de qué es un modelo de lenguaje; no se requiere experiencia previa en infraestructura de serving.
- Stacks principales: vLLM (GPU) y llama.cpp (CPU/edge), tratados en ese orden. Otros stacks (TGI, TensorRT-LLM) se mencionan solo donde un concepto se transfiere de otra manera.

## Fuera de alcance

- Entrenar o hacer fine-tuning de un modelo o de un adapter: consulta [`llm/finetuning`](../../llm/finetuning/) (lecciones 0025, servir adapters, y 0026, costo, latencia y throughput), a las que se enlaza en lugar de repetirlas.
- Juzgar la calidad de la salida o construir una eval para un modelo servido: consulta [`llm/evals`](../../llm/evals/) para ese límite.
- Cómo funcionan los métodos de cuantización y cómo juzgarlos, desde los formatos numéricos y el mapeo afín hasta GPTQ, AWQ, SmoothQuant, QAT y la medición de la pérdida de calidad: consulta [`llm/quantization`](../../llm/quantization/). La etapa 3 de aquí conserva la decisión de serving, elegir un esquema para un presupuesto de latencia, y enlaza allí para los fundamentos; ese límite se fijó cuando se escribió el track de cuantización.
- Pedir salida estructurada desde el lado del prompt: consulta [`llm/prompting`](../../llm/prompting/). Este track es dueño de la decodificación restringida, el lado del serving del mismo objetivo.

## El arco

Catorce etapas, desde la primera solicitud hasta una configuración de serving defendida, a escala de flota, monitorizada en producción y revisada. Una etapa abarca varias lecciones y los límites son difusos; lo que da una etapa por terminada es la capacidad, no el número de lecciones.

| Etapa | Lecciones | Cubre | Terminada cuando |
|---|---|---|---|
| 1. La KV cache | 0001 a 0003 | Por qué la generación autorregresiva es costosa, qué compensa la caché con memoria, cómo crece el tamaño de la caché con el contexto y el lote | Puedes calcular la huella de memoria de la KV cache de un modelo para una longitud de contexto y un tamaño de lote dados |
| 2. Batching | 0004 a 0006 | Batching estático frente a continuo, scheduling de solicitudes, el compromiso entre throughput y latencia | Puedes defender una configuración de batching para una carga de trabajo declarada |
| 3. Cuantización al servir | 0007 a 0009 | int8/int4/AWQ/GPTQ en tiempo de inferencia, precisión frente a velocidad frente a memoria | Puedes elegir un esquema de cuantización al servir y defender el compromiso |
| 4. vLLM en la práctica | 0010 a 0012 | Poner en marcha vLLM, PagedAttention, los parámetros de ajuste que importan | Un stack de vLLM está funcionando y responde solicitudes reales |
| 5. llama.cpp en CPU/edge | 0013 a 0015 | GGUF, la arquitectura de llama.cpp, qué cambia fuera de la GPU | Un stack de llama.cpp está funcionando en CPU y responde solicitudes reales |
| 6. El presupuesto de latencia | 0016 a 0017 | Metodología de medición del p99, vincular la cifra con las decisiones de caché, batching y cuantización | Puedes citar y defender un presupuesto de latencia p99 de extremo a extremo |
| 7. Speculative decoding | 0018 | Speculative decoding con modelo borrador, n-grama, Medusa y EAGLE | Puedes explicar por qué la verificación paralela es casi gratis y elegir una variante de speculative decoding para una carga de trabajo |
| 8. Muestreo y decodificación restringida al servir | 0019 | Parámetros de muestreo por solicitud en un lote compartido, decodificación restringida indexada con FSM | Puedes explicar por qué la garantía de la decodificación restringida es estructural y por qué su costo por token sigue siendo pequeño |
| 9. Prefix caching | 0020 | El prefix caching automático como compartición de bloques entre solicitudes, cargas de documentos largos y de varios turnos, su límite de solo prefill | Puedes explicar cuándo ayuda el prefix caching a una carga de trabajo y por qué nunca acelera el decode |
| 10. Paralelismo multi-GPU y multinodo | 0021 | El mecanismo real del tensor parallelism más allá del único parámetro de la lección 12, el pipeline parallelism y un procedimiento de decisión sobre cuál (o ambos) necesita un despliegue | Puedes explicar qué cuesta un paso de combinación del tensor parallelism y qué cuesta una burbuja de pipeline, y elegir la división correcta para una interconexión y un número de nodos dados |
| 11. Serving a nivel de flota | 0022 | Enrutamiento de solicitudes informado por la localidad de la caché, autoscaling guiado por la profundidad de la cola, y por qué el tiempo de carga del modelo en un arranque en frío limita lo rápido que una réplica nueva ayuda de verdad | Puedes explicar cómo el enrutamiento, el autoscaling y la latencia de arranque en frío hay que razonarlos como un solo pipeline y no ajustarlos por separado |
| 12. Observabilidad y costo en producción | 0023 | Métricas exportadas de forma continua, SLI/SLO/presupuestos de error que convierten una métrica en un objetivo, y el costo por millón de tokens derivado del throughput medido | Puedes defender una configuración de producción citando su p99, el SLO y el presupuesto de error a que está sujeta y su costo por millón de tokens |
| 13. Contexto largo al servir | 0024 | Escalado de RoPE frente a atención de ventana deslizante y attention sinks, y qué hace cada uno realmente con la fórmula de crecimiento de la caché de la lección 2 | Puedes explicar si una técnica de contexto largo amplía la longitud utilizable, limita el tamaño de la caché a una constante o corrige el modo de fallo de una caché limitada |
| 14. Criterio | 0025 | Revisar la configuración de otra persona en busca de parámetros desajustados, despliegues seguros a través de aquello de lo que otros dependen, y decir cuándo el speculative decoding no es una victoria gratis | Se confía en ti para revisar una configuración de serving y nombrar qué cuesta cada decisión, no solo que algo te suena mal |

## Lecciones

Recórrelas en orden.

| # | Lección | Enseña |
|---|---|---|
| [0001](lessons/0001-the-kv-cache.md) | La KV cache | Por qué la generación se vuelve costosa y qué recupera el uso de una caché |
| [0002](lessons/0002-capacity-and-batch-size.md) | Capacidad y tamaño de lote | Cómo el reparto de cabezas (GQA/MQA) y el tamaño de lote cambian la huella real de la caché |
| [0003](lessons/0003-growth-prefill-decode-precision.md) | Crecimiento, prefill, decode y precisión | Cómo crece la caché a lo largo del prefill y del decode, y qué recupera bajar su precisión |
| [0004](lessons/0004-static-vs-continuous-batching.md) | Batching estático frente a continuo | Por qué agrupar solicitudes en lotes ayuda al throughput, y por qué el batching continuo supera al estático |
| [0005](lessons/0005-request-scheduling.md) | Scheduling de solicitudes | Cómo un scheduler de batching continuo elige la siguiente solicitud, y por qué un prefill grande puede detener a todos los demás |
| [0006](lessons/0006-throughput-latency-tradeoff.md) | El compromiso entre throughput y latencia | Cómo el tamaño de lote intercambia throughput por latencia por token, y cómo defender una configuración de batching frente a un presupuesto de latencia declarado |
| [0007](lessons/0007-quantization-schemes.md) | Esquemas de cuantización al servir | Qué hacen realmente int8, int4, GPTQ y AWQ con los pesos de un modelo, y por qué la versión ingenua de la cuantización de pocos bits necesita una corrección |
| [0008](lessons/0008-accuracy-speed-memory-tradeoffs.md) | Compromisos entre precisión, velocidad y memoria | Por qué la memoria, la velocidad y la precisión no se mueven juntas cuando se cuantiza un modelo, y cómo se mide realmente cada una |
| [0009](lessons/0009-picking-a-quantization-scheme.md) | Elegir y defender un esquema de cuantización | Un marco de decisión para elegir un esquema de cuantización al servir, y las tres cifras que lo defienden |
| [0010](lessons/0010-standing-up-vllm.md) | Poner en marcha vLLM | Instalar vLLM, lanzar su servidor y encontrar los parámetros que llevan los conceptos ya enseñados |
| [0011](lessons/0011-pagedattention.md) | PagedAttention | El mecanismo de tabla de bloques detrás de vLLM, su compromiso de tamaño de bloque y cómo permite que las secuencias compartan la caché de un prefijo común |
| [0012](lessons/0012-vllm-tuning-knobs.md) | Los parámetros de ajuste de vLLM que importan | Dos parámetros más, gpu-memory-utilization y tensor-parallel-size, y un procedimiento de decisión sobre qué parámetro señala realmente un síntoma |
| [0013](lessons/0013-gguf.md) | GGUF | Qué agrupa el formato de modelo de un solo archivo de llama.cpp, su nomenclatura de cuantización y por qué se puede mapear en memoria en lugar de cargarse |
| [0014](lessons/0014-llamacpp-architecture.md) | La arquitectura de llama.cpp | La biblioteca de tensores ggml que hay debajo de llama.cpp, su abstracción de backends y en qué se diferencia el threading en CPU del batching en GPU |
| [0015](lessons/0015-what-changes-off-gpu.md) | Qué cambia fuera de la GPU | Poner en marcha el servidor de llama.cpp, y cómo se ven de distinta manera el batching, la gestión de la caché y la cuantización a escala de CPU/edge |
| [0016](lessons/0016-p99-latency-methodology.md) | Metodología de medición de la latencia p99 | Por qué el p99 supera a un promedio, por qué el TTFT y la latencia entre tokens necesitan cifras separadas, y qué hace fiable una medición de p99 |
| [0017](lessons/0017-defending-a-latency-budget-end-to-end.md) | Defender un presupuesto de latencia de extremo a extremo | Un orden de diagnóstico para un presupuesto de p99 incumplido, y las tres cosas que debe citar una configuración final defendida |
| [0018](lessons/0018-speculative-decoding.md) | Speculative decoding | Verificar varios tokens candidatos en una sola pasada forward paralela cuesta aproximadamente lo que cuesta normalmente generar un token, porque el decode está limitado por mover pesos y no por la aritmética, que es el único hecho sobre el que se construye cada variante de speculative decoding |
| [0019](lessons/0019-sampling-and-constrained-decoding-at-serve-time.md) | Muestreo y decodificación restringida al servir | Un lote continuo ya hace pasar muchas solicitudes por una misma pasada forward compartida, y dar a cada una sus propios ajustes de muestreo, o forzar a una de ellas a producir siempre JSON válido, tiene que ocurrir por fila dentro de esa misma pasada compartida sin frenar a todos los demás |
| [0020](lessons/0020-prefix-caching.md) | Prefix caching | La lección 11 dejó que las muestras paralelas de una misma solicitud compartieran los bloques en caché de un prompt; el prefix caching es esa misma compartición aplicada a solicitudes por lo demás no relacionadas, y acelera exactamente la fase que desperdicia el prefill redundante, nunca la fase que genera la respuesta |
| [0021](lessons/0021-tensor-and-pipeline-parallelism.md) | Tensor parallelism y pipeline parallelism | La lección 12 nombró tensor-parallel-size como un parámetro que divide un modelo entre GPU; esta lección abre qué hace realmente esa división dentro de una capa, presenta el pipeline parallelism como otra división del mismo problema y da un procedimiento de decisión sobre cuál (o ambos) necesita realmente una carga de trabajo |
| [0022](lessons/0022-fleet-level-serving.md) | Servir a nivel de flota | El scheduler de la lección 5 elige la siguiente solicitud de la cola de un servidor; una flota añade antes una decisión, qué servidor recibe la solicitud, otra sobre cuándo añadir más servidores y un costo de arranque en frío que deja inútil durante decenas de segundos a un servidor recién añadido |
| [0023](lessons/0023-production-observability-and-cost.md) | Observabilidad y costo en producción | La lección 17 defendió una cifra de p99 medida para una configuración; esta lección cubre qué hay que exportar de forma continua para detectar una regresión automáticamente, el SLO y el presupuesto de error que convierten "suficientemente bueno" en un objetivo y no en una sensación, y la cifra de costo por millón de tokens que hay que defender junto al p99, no en su lugar |
| [0024](lessons/0024-long-context-at-serve-time.md) | Contexto largo al servir | La fórmula de capacidad de la lección 2 cobra memoria de forma lineal con la longitud del contexto; el escalado de RoPE amplía lo largo que puede ser un contexto sin cambiar en absoluto ese cobro, mientras que la atención de ventana deslizante y los attention sinks cambian la propia fórmula al limitar la longitud del contexto a una constante |
| [0025](lessons/0025-reviewing-a-serving-configuration.md) | Revisar una configuración de serving | Revisar la configuración de serving de otra persona y nombrar con precisión qué cuesta (un parámetro mal ajustado frente al cuello de botella de la carga de trabajo declarada, una topología elegida sin un cuello de botella que la justifique, un despliegue que rompe a un cliente a mitad de camino), en lugar de decir que algo le suena mal |

## Referencia

- [Glosario](GLOSSARY.md): términos canónicos de este tema
- [Recursos](RESOURCES.md): fuentes de confianza
- [KV cache](reference/kv-cache.md): costo por token, reparto de cabezas, crecimiento a lo largo de una solicitud y planificación de capacidad
- [Batching](reference/batching.md): batching estático frente a continuo, scheduling de solicitudes y el compromiso entre throughput y latencia
- [Cuantización al servir](reference/quantization-at-serve-time.md): int8/int4/GPTQ/AWQ, por qué la memoria, la velocidad y la precisión no se mueven juntas, y un marco de decisión para elegir un esquema
- [vLLM](reference/vllm.md): poner en marcha vLLM, PagedAttention y los parámetros de ajuste que importan
- [llama.cpp](reference/llama-cpp.md): GGUF, la arquitectura de llama.cpp y qué cambia fuera de la GPU
- [Presupuesto de latencia](reference/latency-budget.md): metodología de medición del p99 y vincular un presupuesto incumplido con las decisiones de caché, batching y cuantización

## Cómo funciona

Cada lección es corta y autocontenida. Las claves de respuesta están plegadas: primero recuerda, luego ábrelas. Las prácticas en el mundo real importan más que la lectura, y espaciarlas es el punto. Todo lo que siga sin estar claro al final de una lección merece rastrearse hasta su fuente primaria antes de seguir.
