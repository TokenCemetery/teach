---
title: Tracks de aprendizaje
description: Todos los temas de este repositorio, agrupados por dominio
type: index
---

# Tracks de aprendizaje

Agrupados por dominio, un directorio por tema. Cada tema es un track autocontenido guiado por la skill `teach`: una misión, un conjunto ordenado de lecciones y el material de referencia que esas lecciones se ganaron.

## Temas

| Dominio | Tema | Misión | Lecciones |
|---|---|---|---|
| programming | [Bash](programming/bash/) | Escribe shell que sobreviva a producción: entrecomillado, código de salida, los modos de fallo y saber cuándo parar y usar un lenguaje de verdad | 17 |
| programming | [C#](programming/csharp/) | Hazte cargo de un servicio en C#: el sistema de tipos, async y lo que hace el CLR con lo que escribiste | 45 |
| programming | [Go](programming/golang/) | Hazte cargo de Go en un equipo: diseña, entrega y opera un servicio en producción | 41 |
| programming | [Java](programming/java/) | Hazte cargo de un servicio en Java: modélalo en Java moderno y luego opera lo que la JVM hace con él | 52 |
| programming | [Kotlin](programming/kotlin/) | Hazte cargo de Kotlin en la JVM: null safety, corrutinas y dónde el hábito de Java produce Kotlin que compila y se lee mal | 44 |
| programming | [Python](programming/python/) | Hazte cargo de Python en producción: entrégalo tipado, probado, empaquetado y perfilado | 44 |
| programming | [Rust](programming/rust/) | Hazte cargo de Rust: diseña con ownership en lugar de pelearte con el borrow checker, y luego publica el crate | 67 |
| programming | [SQL](programming/sql/) | Hazte cargo de la base de datos: escribe la consulta, lee el plan, diseña el esquema, sobrevive a la concurrencia | 53 |
| programming | [TypeScript](programming/typescript/) | Hazte cargo de un código base en TypeScript: haz que el compilador rechace los estados que no deberían existir | 49 |
| llm | [Fine-tuning con adapters](llm/finetuning/) | Decide si hacer fine-tuning, ejecútalo, demuestra que funcionó, llévalo a producción | 27 |
| llm | [Preentrenamiento](llm/pretraining/) | Entrena un modelo desde cero a escala: datos, tokenizer, entrenamiento distribuido y un presupuesto de cómputo defendible | 24 |
| llm | [Post-training](llm/post-training/) | Alinea un base model: SFT, modelado de recompensa, RLHF, DPO y GRPO, y saber cuál elegir | 20 |
| llm | [Inferencia](llm/inference/) | Sirve un modelo: la KV cache, el batching, la cuantización en tiempo de serving y un presupuesto de latencia que puedas defender | 24 |
| llm | [Evals](llm/evals/) | Demuestra que un cambio de modelo ayudó: construye la eval, reserva los datos con honestidad y defiende el número frente a la contaminación | 18 |
| llm | [RAG](llm/rag/) | Domina la recuperación: chunking, embeddings, búsqueda híbrida, reranking y medir si se recuperó lo correcto | 19 |
| llm | [Transformers](llm/transformers/) | Construye la atención desde cero, para que la arquitectura deje de ser una caja negra detrás del script de entrenamiento | 22 |
| llm | [Agentes](llm/agents/) | Construye el bucle tú mismo: herramientas, contexto, memoria y saber cuándo un agente es la respuesta equivocada | 37 |
| llm | [Cuantización](llm/quantization/) | Cuantiza un LLM y defiéndelo: formatos numéricos, métodos PTQ y QAT, qué corre más rápido y medir lo que costó | 27 |
| llm | [Prompting](llm/prompting/) | Escribe, versiona y entrega prompts para una funcionalidad con LLM, demuestra que un cambio de prompt ayudó y revisa el prompt de producción de otra persona | 24 |
| llm | [Destilación](llm/distillation/) | Destila un modelo grande en uno más pequeño y defiéndelo: soft targets, pérdidas a nivel de logit y de secuencia, datos sintéticos, entrenamiento on-policy y lo que perdió el estudiante | 27 |
| data | [Postgres](data/postgres/) | Opera Postgres: el WAL, vacuum y bloat, replicación y lo que cuesta mantener un índice | 18 |
| data | [Kafka](data/kafka/) | Hazte cargo del log: particiones, grupos de consumidores, garantías de entrega y lo que realmente cuesta "exactly once" | 16 |
| data | [Redis](data/redis/) | Usa Redis para lo que es: el modelo de memoria, la expulsión, la persistencia y los patrones que lo usan mal sin que se note | 17 |
| data | [Warehouses](data/warehouses/) | Domina el almacén analítico: almacenamiento y ejecución columnar, almacenamiento separado del cómputo y por qué los consejos de rendimiento de un almacén por filas dejan de valer | 20 |
| data | [Stream Processing](data/stream-processing/) | Calcula sobre un stream con Kafka Streams: topologías, estado, ventanas y joins, y lo que cuesta una topología antes de llegar a producción | 20 |
| architecture | [Sistemas distribuidos](architecture/distributed-systems/) | Razona sobre el fallo parcial: lo que una red te puede hacer, qué consistencia estás comprando de verdad y por qué el consenso es caro | 19 |
| architecture | [Diseño de APIs](architecture/api-design/) | Diseña una interfaz de la que otros dependen: el contrato, sus errores y cómo cambia sin romperlos | 19 |
| infrastructure | [Contenedores](infrastructure/containers/) | Empaqueta un servicio como imagen de contenedor y hazte cargo de ella: primitivas del kernel, Dockerfiles, ejecutar, asegurar y depurar un contenedor | 24 |
| infrastructure | [Kubernetes](infrastructure/kubernetes/) | Ejecuta servicios en un clúster de Kubernetes y hazte cargo de ellos: el bucle de reconciliación, cargas de trabajo, red, configuración, fiabilidad, seguridad, empaquetado y depuración | 28 |
| infrastructure | [CI/CD](infrastructure/ci-cd/) | Construye, prueba y entrega cada cambio a través de un pipeline y hazte cargo de él: workflows, feedback rápido, artefactos, secretos, despliegues, rollback y seguridad de la cadena de suministro | 30 |

## Empezar un tema

```bash
cp -r templates/learning-workspace learning/<domain>/<topic-slug>
```

Luego ejecuta la skill `teach` y nombra el tema. Lee el track, completa la misión entrevistándote y escribe la primera lección.

Un dominio es una agrupación, no un track: contiene directorios de temas y nada más. Añade uno nuevo cuando un segundo tema lo vaya a compartir.

## Estructura

```text
learning/
├── <domain>/              # programming, llm, …
│   └── <topic>/           # one track per topic
├── .nav.yml               # sidebar order/titles for the published site
└── README.md              # this index
```

Cada track:

```text
learning/<domain>/<topic>/
├── README.md              # mission, success criteria, lesson index
├── GLOSSARY.md            # canonical terms for this topic
├── RESOURCES.md           # trusted sources, known gaps
├── NOTES.md               # preferences and working notes
├── lessons/               # NNNN-slug.md, one tight win each
├── reference/             # cheat sheets, built for lookup
└── learning-records/      # NNNN-slug.md, what was demonstrably learned
```

Las lecciones se numeran desde `0001` dentro de cada track. Los tracks pueden enlazarse entre sí, pero un enlace es un puntero y no una inclusión: no trae el material de otro tema a esta misión. Es preferible enlazar un término del glosario o una hoja de referencia antes que una lección, porque esos están escritos para consulta y le sirven a cualquier lector.

La skill `teach` define el formato de cada archivo de aquí. Lee [su especificación](https://github.com/TokenCemetery/teach/blob/main/.agents/skills/teach/SKILL.md) antes de escribir uno a mano.

## Licencia

Todo lo que hay en este sitio está bajo [CC BY 4.0](https://github.com/TokenCemetery/teach/blob/main/LICENSE-CONTENT). Cópialo, tradúcelo, enseña con él, construye sobre él, con fines comerciales o no. Solo di de dónde viene.
