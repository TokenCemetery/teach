---
title: Agentes con LLM
description: "Construye el bucle tú mismo: herramientas, contexto, memoria y saber cuándo un agente es la respuesta equivocada"
type: topic
---

# Agentes con LLM

Sé capaz de construir tú mismo un bucle de agente, de decidir si una tarea dada necesita un agente o basta un flujo de trabajo fijo, y de diagnosticar un agente que falla a partir de su trayectoria en lugar de añadir una instrucción más a su prompt.

**Última lección:** [0037. Revisar el diseño de agente de otra persona](lessons/0037-reviewing-someone-elses-agent-design.md)

## Cómo se ve el éxito

- Escribir el bucle del agente para una tarea dada, y nombrar qué hace cada mensaje de su contexto y qué termina el bucle.
- Elegir entre un solo prompt, un flujo de trabajo fijo y un agente para una tarea dada, y defender la elección frente al costo de la opción rechazada.
- Diseñar la superficie de herramientas de un agente: nombres, descripciones, formas de retorno y el límite de permisos que decide qué puede hacer sin supervisión.
- Diagnosticar un agente que falla a partir de su trayectoria, nombrando la causa (un bucle, un contexto envenenado, una herramienta mal especificada, una condición de parada equivocada) en lugar de reescribir el prompt al azar.
- Explicar por qué un agente que lee contenido no confiable no se puede asegurar solo con instrucciones en el prompt, y diseñar el límite que realmente aguanta.
- Presupuestar el costo en tokens y la latencia de un bucle agéntico, y decir de qué parte del bucle viene la amplificación.

## Restricciones

- Neutral respecto al proveedor. Los bucles, los esquemas de herramientas y el flujo de control se dan como pseudocódigo parecido a Python, para que el material sobreviva a los cambios constantes en las APIs de llamadas a herramientas que envejecen la mayoría de los textos sobre agentes.
- Los formatos de transmisión son la excepción, porque el aspecto que tiene en la red un mensaje de llamada a herramienta es un hecho y no un algoritmo. Se muestra un par real de petición y respuesta capturado, y un segundo proveedor aparece solo como la diferencia respecto a ese.
- No se asume ni se enseña ningún framework. Lo que un framework aporta (estado durable, flujo de control en grafo, reanudación) se cubre una sola vez, cerca del final, como una decisión y no como un tutorial.
- Las prácticas son de inspección más que de construcción: leer una traza real, un esquema de herramienta real, un manifiesto real de un servidor MCP y marcar el límite de permisos de un agente que ya está en marcha.
- Se asume familiaridad con lo que es un modelo de lenguaje y comodidad para leer código parecido a Python. No se requiere experiencia previa construyendo agentes.

## Fuera de alcance

- La evaluación como disciplina: consulta [`llm/evals`](../../llm/evals/) (la lección 0013 cubre las trayectorias, el éxito de la tarea frente a la precisión por paso y `pass^k`). Aquí se incluye solo como la única capacidad que necesita quien construye agentes, y se enlaza en lugar de repetirla.
- Los detalles internos del pipeline de recuperación: consulta [`llm/rag`](../../llm/rag/). La recuperación aparece aquí como una herramienta que llama un agente, no como chunking, embeddings y reranking.
- Los detalles internos de serving e inferencia: consulta [`llm/inference`](../../llm/inference/) para latencia, batching y decodificación restringida.
- Entrenar un modelo para usar herramientas: consulta [`llm/finetuning`](../../llm/finetuning/).
- Reintentos, idempotencia y fallo parcial como problemas de sistemas distribuidos: consulta [`architecture/distributed-systems`](../../architecture/distributed-systems/). Aquí se cubre solo lo que hace que una llamada a herramienta sea distinta de una llamada remota corriente.
- El prompting como materia (instrucciones, ejemplos, razonamiento, salida estructurada, plantillas y medir un cambio de prompt): consulta [`llm/prompting`](../../llm/prompting/). Este track conserva las descripciones de herramientas, la inyección con herramientas y el caching bajo concurrencia, y enlaza allí para el prompting en general.

## El arco

Dieciséis etapas, desde ningún conocimiento previo hasta el criterio de un perfil sénior. No es una lista de lecciones: una etapa abarca varias lecciones y los límites son difusos.

| Etapa | Lecciones | Cubre | Terminada cuando |
| --- | --- | --- | --- |
| 1. Qué es un agente | 0001 a 0002 | El bucle, agente frente a flujo de trabajo frente a cadena, el espectro de autonomía | Puedes clasificar un sistema y decir si "agente" es la palabra correcta para él |
| 2. Mecánica de las llamadas a herramientas | 0003 a 0005 | El formato de transmisión de una llamada a herramienta, esquemas de parámetros, quién ejecuta qué, llamadas en paralelo, errores devueltos como resultados | Puedes leer un intercambio crudo de llamada a herramienta y decir qué hizo cada mensaje |
| 3. El bucle desde cero | 0006 a 0007 | Escribir el bucle, condiciones de parada, la transcripción como todo el estado del agente | Puedes escribir un bucle de agente y defender dónde se detiene |
| 4. El diseño de herramientas como ingeniería de prompts | 0008 a 0009 | Nombres y descripciones como superficie del prompt, formas de retorno, costo en tokens de los resultados, exceso de herramientas | Puedes diseñar una superficie de herramientas y decir por qué cada descripción está redactada como está |
| 5. Gestión del contexto | 0010 a 0012 | La ventana como presupuesto central: truncamiento, compactación, recuperación bajo demanda, subagentes como aislamiento de contexto | Puedes planificar qué sale del contexto, y cuándo, en una tarea de larga duración |
| 6. Memoria y estado | 0013 a 0014 | Scratchpad dentro de una ejecución frente a memoria entre ejecuciones, archivos como memoria, por qué la recuperación no es memoria | Puedes elegir dónde vive un hecho dado y decir qué pasa cuando termina la ejecución |
| 7. Planificación y reflexión | 0015 a 0017 | ReAct, planificar y luego ejecutar, autocrítica, descomposición, lo que cambiaron los modelos de razonamiento | Puedes elegir un patrón de planificación para una tarea y nombrar lo que cuesta en tokens y latencia |
| 8. Multiagente | 0018 a 0019 | Orquestador y worker, traspaso, fan-out, costo de coordinación, cuándo gana un solo agente con mejores herramientas | Puedes decir si un segundo agente aporta algo que no se le habría podido dar al primero |
| 9. Protocolos e interoperabilidad | 0020 a 0021 | Las herramientas, recursos, prompts y transportes de MCP, formatos de llamada a funciones de los proveedores, descubrimiento de herramientas a escala | Puedes leer el manifiesto de un servidor MCP y decir qué expone y qué no estandariza |
| 10. Entornos de ejecución | 0022 a 0023 | Sandboxing, ejecución de código como herramienta, acceso al sistema de archivos, puertas de aprobación con humano en el bucle | Puedes colocar el límite del sandbox para un conjunto dado de herramientas |
| 11. Uso del ordenador y agentes de navegador | 0024 a 0026 | Capturas de pantalla como observaciones, anclar una acción a una coordenada, el problema de la fiabilidad | Puedes decir por qué un agente que maneja la pantalla falla de forma distinta a uno que llama herramientas |
| 12. Modos de fallo y observabilidad | 0027 a 0029 | Bucles, envenenamiento del contexto, errores de herramienta en cascada, argumentos alucinados, trazado y reproducción de trayectorias | Dada una trayectoria, puedes nombrar el paso culpable en lugar de reescribir el prompt |
| 13. Evaluar un agente | 0030 a 0030 | Resultado frente a trayectoria, fiabilidad con pruebas repetidas, qué miden en realidad los benchmarks de agentes | Puedes decir qué medir para un agente dado y dejar el resto a `llm/evals` |
| 14. Seguridad | 0031 a 0032 | La inyección de prompt como el problema que define a los agentes, la tríada letal, mínimo privilegio, el delegado confundido, la cadena de suministro de MCP | Puedes diseñar un límite de permisos que aguante cuando el agente lee contenido hostil |
| 15. Producción, costo y lo que ofrecen los frameworks | 0033 a 0035 | Amplificación de tokens, prompt caching, concurrencia, durabilidad y capacidad de reanudación, costo por tarea completada | Puedes presupuestar el costo de un bucle y decir qué garantía de framework necesita realmente un despliegue |
| 16. Criterio | 0036 a 0037 | Cuándo no construir un agente, revisar el diseño de agente de otra persona y nombrar lo que cuesta una decisión, zanjar una afirmación disputada desde la fuente primaria | Se confía en ti para tomar la decisión y explicársela a otra persona |

## Lecciones

Recórrelas en orden.

| # | Lección | Enseña |
|---|---|---|
| [0001](lessons/0001-the-agent-loop.md) | El bucle del agente | Qué convierte a un sistema en un agente, y el ciclo de cuatro pasos que corre por debajo |
| [0002](lessons/0002-agent-workflow-or-prompt.md) | Agente, flujo de trabajo o solo un prompt | Dónde se ubica una tarea en el espectro de autonomía, y cómo defender la elección |
| [0003](lessons/0003-the-wire-format-of-a-tool-call.md) | El formato de transmisión de una llamada a herramienta | Qué aspecto tienen realmente una llamada a herramienta y su resultado en el protocolo entre tu harness y el proveedor del modelo |
| [0004](lessons/0004-schemas-and-who-executes.md) | Esquemas de parámetros y quién ejecuta qué | Cómo los esquemas JSON limitan lo que un modelo puede enviar, y la diferencia entre herramientas de cliente y de servidor |
| [0005](lessons/0005-parallel-calls-and-errors-as-results.md) | Llamadas en paralelo y errores como resultados | Cómo un modelo puede pedir varias herramientas a la vez, y por qué los errores de herramienta son resultados y no excepciones |
| [0006](lessons/0006-writing-the-loop.md) | Escribir el bucle | Construir el bucle del agente a partir de pseudocódigo y elegir las condiciones de parada de forma deliberada |
| [0007](lessons/0007-the-transcript-as-state.md) | La transcripción como estado | Entender que la transcripción es la única memoria persistente del agente entre turnos |
| [0008](lessons/0008-naming-and-describing-a-tool.md) | Nombrar y describir una herramienta | El nombre y la descripción de una herramienta es lo que lee el modelo para decidir cuándo y cómo llamarla |
| [0009](lessons/0009-return-shapes-and-tool-set-bloat.md) | Formas de retorno y exceso de herramientas | El valor de retorno de una herramienta consume presupuesto de contexto, y demasiadas herramientas perjudican la capacidad del modelo de elegir bien |
| [0010](lessons/0010-the-context-window-as-budget.md) | La ventana de contexto como presupuesto | La ventana de contexto es un recurso finito que el harness cura activamente con el tiempo, no un registro inerte |
| [0011](lessons/0011-compaction-and-retrieval-on-demand.md) | Compactación y recuperación bajo demanda | Dos estrategias para mantener dentro del presupuesto el contexto de un agente de larga duración sin perder lo que todavía importa |
| [0012](lessons/0012-sub-agents-as-context-isolation.md) | Subagentes como aislamiento de contexto | Lanzar un subagente aísla el trabajo exploratorio largo del presupuesto de contexto del padre |
| [0013](lessons/0013-scratchpad-versus-memory.md) | Scratchpad frente a memoria | La diferencia entre las notas que un agente guarda durante una ejecución y los hechos que necesita a lo largo de varias ejecuciones |
| [0014](lessons/0014-files-as-memory.md) | Archivos como memoria | Usar archivos durables como la forma más simple de memoria entre ejecuciones para agentes |
| [0015](lessons/0015-react-interleaving-reasoning-and-acting.md) | ReAct: intercalar razonamiento y acción | El patrón de emparejar breves pasos de razonamiento con cada acción, para que el modelo pueda observar y adaptarse |
| [0016](lessons/0016-plan-then-execute-and-decomposition.md) | Planificar y luego ejecutar, y descomposición | La planificación explícita por adelantado como alternativa a ReAct, cuándo usarla y cómo manejar la replanificación |
| [0017](lessons/0017-self-critique-and-reasoning-models.md) | Autocrítica y lo que cambiaron los modelos de razonamiento | El bucle de reflexión como etapa explícita, sus costos y cómo el razonamiento interno extendido afecta cuándo usarlo |
| [0018](lessons/0018-orchestrator-and-worker.md) | Orquestador y worker | Diseñar un sistema multiagente en el que un agente planifica y delega, y los workers ejecutan en paralelo |
| [0019](lessons/0019-coordination-cost.md) | Costo de coordinación | Entender por qué construir varios agentes es más caro que un solo agente bien equipado, y cómo decidir cuándo vale la pena la ganancia del paralelismo |
| [0020](lessons/0020-mcp-tools-resources-and-prompts.md) | MCP: herramientas, recursos y prompts | Model Context Protocol como interfaz estandarizada para que los harness de agentes descubran e invoquen herramientas externas, lean datos y usen plantillas |
| [0021](lessons/0021-provider-formats-and-discovery-at-scale.md) | Formatos de proveedor y descubrimiento de herramientas a escala | Cómo MCP y los formatos de transmisión propios de cada proveedor son capas separadas, y por qué cargar todas las herramientas en el contexto no escala a muchos servidores conectados |
| [0022](lessons/0022-sandboxing-and-approval-gates.md) | Sandboxing y puertas de aprobación | Límites de ejecución y puntos de control humanos que protegen frente a los errores del modelo |
| [0023](lessons/0023-code-execution-as-a-tool.md) | Ejecución de código como herramienta | Darle a un agente una única herramienta de ejecución de código en un sandbox en lugar de muchas herramientas individuales y estrechas |
| [0024](lessons/0024-screenshots-as-observations.md) | Capturas de pantalla como observaciones | Cómo los agentes de uso del ordenador observan la pantalla como una imagen en lugar de datos estructurados, y por qué la estructura del bucle se mantiene |
| [0025](lessons/0025-grounding-an-action-to-a-coordinate.md) | Anclar una acción a una coordenada | Por qué traducir una intención visual a una coordenada de píxel es más difícil y más frágil que un argumento tipado de una llamada a herramienta |
| [0026](lessons/0026-why-browser-agents-fail-differently.md) | Por qué los agentes de navegador fallan de forma distinta | Los agentes que manejan la pantalla fallan de maneras en que no lo hacen los agentes que llaman herramientas, y por qué WebArena creó un benchmark para medir y estudiar esos fallos |
| [0027](lessons/0027-loops-and-context-poisoning.md) | Bucles y envenenamiento del contexto | Dos modos de fallo visibles en una trayectoria, los bucles repetitivos y el envenenamiento silencioso del contexto, y cómo detectar cada uno |
| [0028](lessons/0028-cascading-tool-errors.md) | Errores de herramienta en cascada y argumentos alucinados | Un error de herramienta que lleva a decisiones erróneas, que se hunde en la confusión, y argumentos bien tipados pero falsos que los esquemas no pueden atrapar |
| [0029](lessons/0029-tracing-and-trajectory-replay.md) | Trazado y reproducción de trayectorias | Usar convenciones de traza neutrales respecto a los proveedores para capturar ejecuciones de agentes, y reproducir trayectorias para recorrer los fallos paso a paso |
| [0030](lessons/0030-evaluating-an-agent.md) | Evaluar un agente | Medir el éxito de un agente a nivel de resultado frente a nivel de trayectoria, y por qué una sola ejecución exitosa no significa que el agente sea fiable |
| [0031](lessons/0031-prompt-injection-and-the-lethal-trifecta.md) | Inyección de prompt y la tríada letal | Cómo los agentes que leen contenido no confiable se vuelven explotables, y por qué el prompting por sí solo no los asegura |
| [0032](lessons/0032-least-privilege-and-the-confused-deputy.md) | Mínimo privilegio y el delegado confundido | Cómo acotar las capacidades de un agente para que la inyección de prompt cause un daño contenido en lugar de una brecha catastrófica |
| [0033](lessons/0033-token-amplification-and-cost.md) | Amplificación de tokens y costo por tarea completada | Por qué los sistemas agénticos consumen muchos más tokens por tarea completada que un solo prompt, y cómo presupuestarlo |
| [0034](lessons/0034-prompt-caching-and-concurrency.md) | Prompt caching y concurrencia | Cómo el caching reduce el costo en tokens por tarea y cómo la concurrencia aumenta el rendimiento, y por qué confundirlos es un error de presupuesto |
| [0035](lessons/0035-durability-and-what-frameworks-buy.md) | Durabilidad y lo que ofrece un framework | La ejecución durable y reanudable de un agente como problema de ingeniería, lo que ofrecen en concreto los frameworks y un principio de decisión para adoptar uno |
| [0036](lessons/0036-when-not-to-build-an-agent.md) | Cuándo no construir un agente | El criterio para decidir si una tarea realmente necesita un agente, y la disciplina de decir que no cuando no vale su costo |
| [0037](lessons/0037-reviewing-someone-elses-agent-design.md) | Revisar el diseño de agente de otra persona | Cómo evaluar un sistema de agentes de forma sistemática, y cómo zanjar una afirmación disputada volviendo a la fuente primaria |

## Referencia

- [Glosario](GLOSSARY.md): términos canónicos de este tema
- [Recursos](RESOURCES.md): fuentes de confianza

## Cómo funciona

Cada lección es corta y autocontenida. Las claves de respuesta están plegadas: primero recuerda, luego ábrelas. Las prácticas en el mundo real importan más que la lectura, y espaciarlas es el punto. Todo lo que siga sin estar claro al final de una lección merece rastrearse hasta su fuente primaria antes de seguir.
