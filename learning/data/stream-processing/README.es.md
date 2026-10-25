---
title: Stream Processing
description: "Calcula sobre un stream con Kafka Streams: topologías, estado, ventanas y joins, y lo que cuesta una topología antes de llegar a producción"
type: topic
---

# Aprendizaje: Procesamiento de streams

Sé capaz de construir, probar y ejecutar una aplicación de Kafka Streams que dé la respuesta correcta cuando los registros llegan tarde, desordenados o dos veces, y de decir a partir de su topología qué topics internos, qué estado y qué tiempo de recuperación costará antes de llegar a producción.

**Última lección:** [20. Cambiar una topología de la que dependen otros](lessons/0020-changing-a-topology-others-depend-on.md)

## Cómo se ve el éxito

- Explicar a partir de la dualidad stream-tabla cómo se relacionan un topic, un changelog y una KTable, y predecir qué emite una topología para una entrada planteada.
- Construir una topología con el DSL, leer la salida de `describe()` y nombrar cada topic interno que crea y por qué.
- Elegir un state store para una operación con estado y decir cómo se reconstruye su estado cuando muere la instancia que lo tiene.
- Elegir una ventana y un periodo de gracia para una pregunta basada en el tiempo, y decir qué registros tardíos descarta y cuándo emite un resultado.
- Elegir un join para dos entradas, hacer que estén co-particionadas o decir por qué una GlobalKTable evita esa necesidad, y predecir la salida del join.
- Decir qué garantiza `exactly_once_v2` y qué deja fuera, y dimensionar las tareas, los hilos, las instancias y las réplicas standby de una aplicación para un tiempo de recuperación planteado.
- Probar una topología con `TopologyTestDriver` y operar una aplicación en ejecución a partir de sus métricas, sus estados y sus manejadores de excepciones.
- Decidir entre Kafka Streams, un consumidor simple, Flink y ksqlDB para una carga de trabajo, revisar la topología de otra persona y cambiar una topología en ejecución sin romper su estado ni a sus consumidores aguas abajo.

## Restricciones

- Se asume Java operativo y el log tal como lo enseña [`data/kafka`](../../data/kafka/): particiones, grupos de consumidores, garantías de entrega, retención y log compaction. Estas lecciones enlazan allí en lugar de volver a derivar nada de eso.
- Kafka Streams es el único motor que se enseña. Los ejemplos usan el DSL de Java y la Processor API de Apache Kafka 4.3.
- Los valores por defecto y los protocolos cambian entre versiones. Donde una lección cita uno, nombra la página de documentación o el KIP del que salió, y el lector debe consultar esa página para conocer el valor actual.

## Fuera de alcance

- El propio log: particiones, grupos de consumidores, semánticas de entrega, el costo de las transacciones, retención y log compaction, Kafka Connect y Schema Registry. Consulta [`data/kafka`](../../data/kafka/), sobre el que se construye este track.
- El fallo parcial y la consistencia como teoría: consulta [`architecture/distributed-systems`](../../architecture/distributed-systems/). Este track enseña solo lo que la recuperación de los state stores y el rebalanceo cambian para una aplicación de Streams.
- Apache Flink, Spark Structured Streaming y ksqlDB como temas. La etapa 8 los compara con Kafka Streams como candidatos para una carga de trabajo; no enseña a ejecutarlos.
- El lenguaje Java: consulta [`programming/java`](../../programming/java/).
- Cargar un stream en un almacén analítico: consulta [`data/warehouses`](../../data/warehouses/).

## El arco

Ocho etapas, de la dualidad stream-tabla al criterio. Una etapa abarca varias lecciones y los límites son difusos; lo que da una etapa por terminada es la capacidad, no el número de lecciones.

| Etapa | Lecciones | Cubre | Terminada cuando |
|---|---|---|---|
| 1. Streams y tablas | 0001 a 0002 | La dualidad stream-tabla, los topics compactados como tablas, qué ejecuta una aplicación de Streams y dónde | Puedes decir si un topic se lee como stream o como tabla, y qué añade una aplicación de Streams a un consumidor |
| 2. Topologías | 0003 a 0004 | El DSL, sources, processors y sinks, `describe()`, Serdes, operaciones sin estado, cambios de clave y topics de reparticionado | Puedes leer una topología y nombrar cada topic interno que crea |
| 3. Estado | 0005 a 0007 | State stores, topics de changelog, agregaciones, actualizaciones de KTable, la caché de registros, la Processor API y los punctuators | Puedes elegir un store para un paso con estado y decir cómo sobrevive su estado a la muerte de una instancia |
| 4. Tiempo y ventanas | 0008 a 0010 | Tiempo de evento, tiempo de procesamiento y stream time, extractores de timestamp, ventanas tumbling, hopping, sliding y de sesión, periodos de gracia, supresión | Puedes elegir una ventana y un periodo de gracia para una pregunta y decir qué registros descarta |
| 5. Joins | 0011 a 0012 | Joins stream-tabla y con GlobalKTable, co-particionado, joins stream-stream con ventana, joins tabla-tabla y por clave foránea | Puedes elegir un join para dos entradas y predecir qué emite |
| 6. Garantías y escalado | 0013 a 0015 | `exactly_once_v2`, tareas, hilos e instancias, rebalanceo, restauración del estado, réplicas standby y warmup, el protocolo de rebalanceo de streams | Puedes decir qué cubre exactly-once y dimensionar una aplicación para un tiempo de recuperación planteado |
| 7. Pruebas y operación | 0016 a 0017 | `TopologyTestDriver`, métricas, estados del cliente y de los hilos, manejadores de excepciones, interactive queries, las herramientas de operador | Puedes probar una topología sin un broker y saber por sus métricas si una aplicación en ejecución está sana |
| 8. Criterio | 0018 a 0020 | Streams frente a un consumidor simple, Flink y ksqlDB, revisar una topología, cambiar una topología de la que dependen otros, zanjar una disputa a partir de la fuente | Se confía en ti para tomar la decisión y explicársela a otra persona |

## Lecciones

Recórrelas en orden.

| # | Lección | Enseña |
|---|---|---|
| [0001](lessons/0001-streams-and-tables.md) | Streams y tablas | Por qué un stream de cambios y una tabla de valores actuales son dos vistas de los mismos datos, y cómo un topic contiene cualquiera de los dos |
| [0002](lessons/0002-a-streams-app-is-a-library.md) | Una aplicación de Streams es una biblioteca | Qué se ejecuta cuando arranca una aplicación de Kafka Streams: consumidores, productores y estado local dentro de tu propio proceso, sin un clúster propio |
| [0003](lessons/0003-the-dsl-and-topologies.md) | El DSL y las topologías | Cómo las llamadas al DSL construyen una topología de sources, processors y sinks, y cómo leerla a partir de `describe()` |
| [0004](lessons/0004-stateless-operations-and-repartitioning.md) | Operaciones sin estado y reparticionado | Qué operaciones transforman un registro cada vez, y qué cambio de clave hace que el siguiente paso con estado escriba un topic de reparticionado |
| [0005](lessons/0005-state-stores-and-changelog-topics.md) | State stores y topics de changelog | Dónde guarda su estado una operación con estado, y cómo un topic de changelog compactado permite que otra instancia lo reconstruya |
| [0006](lessons/0006-aggregations-ktables-and-the-record-cache.md) | Agregaciones, KTables y la caché de registros | Por qué una KTable emite un stream de actualizaciones en lugar de respuestas finales, y cómo la caché de registros y el intervalo de commit deciden cuántas |
| [0007](lessons/0007-the-processor-api.md) | La Processor API | Cuándo bajar por debajo del DSL a un processor propio con su propio store y su punctuator, y de qué te haces cargo entonces |
| [0008](lessons/0008-event-time-processing-time-and-stream-time.md) | Tiempo de evento, tiempo de procesamiento y stream time | Qué reloj sigue una operación de Streams, de dónde sale el timestamp de un registro y por qué el stream time solo avanza |
| [0009](lessons/0009-windowed-aggregations.md) | Agregaciones con ventanas | Cómo las ventanas tumbling, hopping, sliding y de sesión agrupan registros por tiempo, y a qué pregunta responde cada una |
| [0010](lessons/0010-late-data-grace-periods-and-suppression.md) | Datos tardíos, periodos de gracia y supresión | Cuánto tiempo acepta una ventana registros desordenados, qué pasa con los que llegan después y cómo emitir solo un resultado final |
| [0011](lessons/0011-stream-table-joins-and-co-partitioning.md) | Joins stream-tabla y co-particionado | Cómo un stream enriquece cada registro a partir de una tabla, por qué ambos lados deben estar co-particionados y cuándo una GlobalKTable elimina esa necesidad |
| [0012](lessons/0012-stream-stream-and-table-table-joins.md) | Joins stream-stream y tabla-tabla | Cómo un join con ventana empareja eventos de dos streams, y cómo los joins de tablas, incluidos los joins por clave foránea, mantienen un resultado al día |
| [0013](lessons/0013-exactly-once-in-kafka-streams.md) | Exactly-once en Kafka Streams | Qué hace atómico `exactly_once_v2` entre lecturas, estado y escrituras, y qué efectos secundarios no puede cubrir |
| [0014](lessons/0014-tasks-threads-and-scaling-out.md) | Tareas, hilos y escalado horizontal | Cómo las particiones se convierten en tareas, cómo se reparten las tareas entre hilos e instancias y qué limita el paralelismo de una aplicación |
| [0015](lessons/0015-rebalancing-restoration-and-standby-replicas.md) | Rebalanceo, restauración y réplicas standby | Qué le pasa al estado cuando una tarea se mueve, y cómo las réplicas standby y warmup acortan el tiempo en que no está disponible |
| [0016](lessons/0016-testing-with-topologytestdriver.md) | Pruebas con TopologyTestDriver | Cómo probar la salida, el estado y el comportamiento temporal de una topología en una prueba unitaria sin broker |
| [0017](lessons/0017-operating-and-monitoring-a-streams-app.md) | Operar y monitorizar una aplicación de Streams | Las métricas, los estados y los manejadores de excepciones que te dicen si una aplicación en ejecución está sana, y qué hacer cuando no lo está |
| [0018](lessons/0018-when-kafka-streams-is-the-wrong-tool.md) | Cuándo Kafka Streams es la herramienta equivocada | Cuándo un consumidor simple, Flink o ksqlDB encaja mejor que una aplicación de Streams en una carga de trabajo, y cómo defender la decisión |
| [0019](lessons/0019-reviewing-someone-elses-topology.md) | Revisar la topología de otra persona | Cómo revisar una topología de Streams y nombrar lo que cuesta cada elección en topics internos, estado y corrección |
| [0020](lessons/0020-changing-a-topology-others-depend-on.md) | Cambiar una topología de la que dependen otros | Cómo cambiar la topología de una aplicación en ejecución sin corromper su estado ni romper a los consumidores aguas abajo, y cómo zanjar una afirmación discutida a partir de la fuente |

## Referencia

- [Glosario](GLOSSARY.md): términos canónicos de este tema
- [Recursos](RESOURCES.md): fuentes de confianza, cada una anotada con lo que cubre
- [Operaciones del DSL](reference/dsl-operations.md): cada operación del DSL por tipo de entrada y de salida, si guarda estado y si reparticiona
- [State stores](reference/state-stores.md): tipos de store, ajustes del changelog, la caché de registros y cómo se restaura el estado
- [Tiempo y ventanas](reference/time-and-windows.md): los tres relojes, los cuatro tipos de ventana, los periodos de gracia y cuándo emite cada una
- [Joins](reference/joins.md): la matriz de joins, con ventanas, co-particionado y lo que emite cada join
- [Configuración](reference/configuration.md): los ajustes que deciden garantías, latencia, paralelismo y recuperación, con sus valores por defecto
- [Operación](reference/operations.md): las métricas que vigilar, los estados del cliente y de los hilos, los manejadores de excepciones y las herramientas de operador
- [Revisión de topologías](reference/topology-review.md): una lista de verificación para revisar una topología, la decisión de herramienta y los cambios de topología seguros e inseguros

## Cómo funciona

Cada lección es corta y autocontenida. Las claves de respuesta están plegadas: primero recuerda, luego ábrelas. Las prácticas en el mundo real importan más que la lectura, y espaciarlas es el punto. Todo lo que siga sin estar claro al final de una lección merece rastrearse hasta su fuente primaria antes de seguir.
