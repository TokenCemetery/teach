---
title: Kafka
description: "Hazte cargo del log: particiones, grupos de consumidores, garantías de entrega y lo que realmente cuesta \"exactly once\""
type: topic
---

# Aprendizaje: Kafka

Sé capaz de diseñar la disposición de topics y particiones para una carga de trabajo real y de diagnosticar el lag de los consumidores, las tormentas de rebalanceo o una pérdida inesperada de mensajes en lugar de adivinar una corrección.

**Última lección:** [16. Las métricas que importan para operar un clúster](lessons/0016-the-metrics-that-matter-for-operating-a-cluster.md)

## Cómo se ve el éxito

- Diseñar la disposición de topics, particiones y grupos de consumidores para una carga de trabajo planteada y defender la elección de garantía de entrega que hay detrás.
- Ante un consumidor con lag o que se rebalancea una y otra vez, diagnosticar qué ajuste o patrón de uso es el culpable.
- Decir lo que cuesta realmente "exactly once" y cuándo at-least-once con un procesamiento idempotente es el mejor compromiso.

## Restricciones

- No se asume experiencia previa con Kafka ni con sistemas de mensajería.
- Apache Kafka es la implementación de referencia; las alternativas (Redpanda, servicios gestionados) no se cubren.
- Se toca brevemente el ecosistema que lo rodea (Schema Registry, nociones básicas de Kafka Connect), allí donde las garantías del log por sí solas no explican cómo se construye un pipeline real.

## Fuera de alcance

- El modelo de fallos que hay detrás de las propias garantías de entrega: consulta [`architecture/distributed-systems`](../../architecture/distributed-systems/), enlazado en lugar de volver a derivarlo aquí.
- Kafka Streams y el cálculo sobre el log (topologías, estado, ventanas, joins): consulta [`data/stream-processing`](../../data/stream-processing/), que enlaza aquí para las semánticas de entrega. ksqlDB como tema propio.

## El arco

Diez etapas, del log a operar el clúster en producción. Una etapa abarca varias lecciones y los límites son difusos; lo que da una etapa por terminada es la capacidad, no el número de lecciones.

| Etapa | Lecciones | Cubre | Terminada cuando |
|---|---|---|---|
| 1. Particiones y el log | 0001 | La unidad en torno a la cual se construye todo lo demás (orden, paralelismo, grupos de consumidores) | Puedes explicar por qué una partición es la unidad de orden y de paralelismo |
| 2. Grupos de consumidores y rebalanceo | 0002 a 0003 | Coordinación de grupos, rebalanceo cooperativo, lag de los consumidores | Puedes diagnosticar un consumidor con lag o que se rebalancea una y otra vez |
| 3. Garantías de entrega | 0004 a 0005 | Semánticas at-most/at-least/exactly-once, productores idempotentes, transacciones | Puedes defender una elección de garantía de entrega y decir lo que cuesta exactly-once |
| 4. Diseñar la disposición | 0006 a 0007 | Elección de la clave, compromisos del número de particiones, garantías de orden | Puedes diseñar la disposición de topics y particiones para una carga de trabajo planteada |
| 5. El ecosistema que lo rodea | 0008 a 0009 | Schema Registry, nociones básicas de Kafka Connect | Puedes explicar cómo encajan alrededor del log en un pipeline real |
| 6. Retención y replicación | 0010 a 0011 | `cleanup.policy`, log compaction, factor de replicación, ISR, `acks`, `min.insync.replicas`, unclean leader election | Puedes defender cuánto tiempo viven los datos de un topic y qué durabilidad garantizan realmente sus ajustes de replicación |
| 7. Configuración del cliente bajo carga | 0012 | `batch.size`, `linger.ms`, `fetch.min.bytes`, `max.poll.interval.ms` | Puedes asociar un síntoma de rendimiento, de latencia o de rebalanceo espurio con el ajuste concreto del cliente que lo resuelve |
| 8. Coordinación del clúster | 0013 | KRaft, el quórum de controladores, `process.roles`, lo que sustituyó a ZooKeeper | Puedes explicar qué hace el quórum de controladores y por qué el failover de KRaft no necesita volver a descargar todos los metadatos |
| 9. Seguridad y multi-tenancy | 0014 a 0015 | TLS, SASL, `security.protocol`, ACL, denegar por defecto, cuotas | Puedes nombrar a qué mecanismo (cifrado, autenticación, autorización o aislamiento de recursos) se refiere realmente una pregunta de seguridad dada |
| 10. Operar el clúster | 0016 | `UnderReplicatedPartitions`, `UnderMinIsr`, margen de disco, latencia de las peticiones, saturación de los request handlers | Puedes nombrar a cuál de las tres familias de señales pertenece un síntoma operativo dado, y hacer triaje entre un broker aislado y todo el clúster |

## Lecciones

Recórrelas en orden.

| # | Lección | Enseña |
|---|---|---|
| [0001](lessons/0001-partitions-and-the-log.md) | Particiones y el log | La unidad en torno a la cual se construye todo lo demás de este espacio de trabajo (orden, paralelismo, grupos de consumidores) |
| [0002](lessons/0002-consumer-group-coordination.md) | Coordinación de grupos de consumidores | Cómo un coordinador de grupo y un líder de grupo reparten las particiones entre los consumidores, y cómo los offsets registran el progreso de cada grupo |
| [0003](lessons/0003-cooperative-rebalancing-and-lag.md) | Rebalanceo cooperativo y diagnóstico del lag de los consumidores | Por qué el protocolo de rebalanceo original provoca una tormenta de rebalanceos, cómo el rebalanceo cooperativo la acota y un orden de diagnóstico para el lag de los consumidores |
| [0004](lessons/0004-delivery-semantics.md) | At-most-once, at-least-once y exactly-once | Dónde se gana o se pierde realmente cada garantía de entrega en los tramos de producción, broker y consumo del camino |
| [0005](lessons/0005-idempotent-producers-and-transactions.md) | Productores idempotentes y transacciones | Por qué la idempotencia es casi gratis pero las transacciones llevan el costo real de exactly-once |
| [0006](lessons/0006-partition-key-choice.md) | Elección de la clave de partición y garantías de orden | Elegir una clave de partición significa elegir, en la misma decisión, qué orden obtienes y a qué paralelismo renuncias |
| [0007](lessons/0007-partition-count-and-topic-layout.md) | Compromisos del número de particiones y diseño de la disposición de un topic | Por qué más particiones no salen gratis, y lo que una disposición de topic bien defendida tiene que nombrar de cada etapa anterior |
| [0008](lessons/0008-schema-registry.md) | Schema Registry | Cómo detectar un cambio de esquema incompatible en el momento de producir sustituye a una rotura silenciosa, más adelante, en el momento de consumir |
| [0009](lessons/0009-kafka-connect-basics.md) | Nociones básicas de Kafka Connect | Cómo las tareas y los modos de worker de Connect aportan paralelismo y tolerancia a fallos, y por qué Connect no concede ninguna garantía que la API subyacente de productor o consumidor no diera ya |
| [0010](lessons/0010-retention-and-log-compaction.md) | Retención y log compaction | Cuánto tiempo sobrevive realmente un mensaje en un topic, y la otra política de limpieza que conserva el historial de una clave en lugar de su antigüedad |
| [0011](lessons/0011-replication-isr-acks-and-unclean-leader-election.md) | Replicación, ISR, acks y unclean leader election | Qué espera realmente acks=all, el mínimo que impide que en silencio signifique menos de lo que parece y el compromiso cuando han desaparecido todas las réplicas sincronizadas |
| [0012](lessons/0012-producer-and-consumer-configuration-under-load.md) | Configuración del productor y del consumidor bajo carga | Los controles del lado del cliente que cambian latencia por rendimiento, y el que puede disparar un rebalanceo para un consumidor que en realidad nunca estuvo muerto |
| [0013](lessons/0013-kraft-and-what-replaced-zookeeper.md) | KRaft y lo que sustituyó a ZooKeeper | Cómo se pone de acuerdo ahora el clúster sobre sus propios metadatos sin el servicio de coordinación externo, y por qué volver a descargar todo el estado en un failover era el problema que valía la pena resolver |
| [0014](lessons/0014-tls-and-sasl-authenticating-to-a-cluster.md) | TLS y SASL: autenticarse ante un clúster | Cifrar el canal y autenticar al cliente son dos trabajos separados que security.protocol combina en un solo ajuste, y confundirlos es donde empieza la mayor parte de la confusión |
| [0015](lessons/0015-acls-and-quotas-authorization-and-multi-tenancy.md) | ACL y cuotas: autorización y multi-tenancy | Un principal autenticado sigue sin estar autorizado a hacer nada hasta que una ACL lo diga, y un principal al que se le permite actuar sigue sin estar protegido de dejar sin la capacidad del clúster a todos los demás tenants |
| [0016](lessons/0016-the-metrics-that-matter-for-operating-a-cluster.md) | Las métricas que importan para operar un clúster | Las particiones infrarreplicadas, el margen de disco y la latencia de las peticiones son las tres señales que vale la pena vigilar, y cada una apunta a un tipo de problema distinto |

## Referencia

- [Glosario](GLOSSARY.md): términos canónicos de este tema
- [Recursos](RESOURCES.md): fuentes de confianza
- [Grupos de consumidores y rebalanceo](reference/consumer-groups-and-rebalancing.md): los dos protocolos de rebalanceo, los dos timeouts de vida independientes y un orden de diagnóstico para el lag de los consumidores con la configuración que rige cada paso
- [Garantías de entrega](reference/delivery-guarantees.md): qué configuración decide cada tramo del camino, por qué la idempotencia puede estar desactivada sin que se note y qué espera realmente un consumidor read_committed
- [Diseño de topics y particiones](reference/topic-and-partition-design.md): cómo llega realmente un registro a una partición, qué orden te da eso y qué no, y las dos direcciones en las que cambiar el número de particiones sale caro
- [Ecosistema](reference/ecosystem.md): los siete tipos de compatibilidad con quién tiene que actualizar primero en cada uno, y lo que Kafka Connect añade alrededor del log, incluida la garantía que viene desactivada por defecto

## Cómo funciona

Cada lección es corta y autocontenida. Las claves de respuesta están plegadas: primero recuerda, luego ábrelas. Las prácticas en el mundo real importan más que la lectura, y espaciarlas es el punto. Todo lo que siga sin estar claro al final de una lección merece rastrearse hasta su fuente primaria antes de seguir.
