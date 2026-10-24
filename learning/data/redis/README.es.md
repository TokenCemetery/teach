---
title: Redis
description: "Usa Redis para lo que es: el modelo de memoria, la expulsión, la persistencia y los patrones que lo usan mal sin que se note"
type: topic
---

# Aprendizaje: Redis

Sé capaz de detectar dónde un sistema existente está usando mal Redis sin que se note, como una caché tratada como almacén o un lock que no lo es, y de diseñar en su lugar un uso correcto desde cero.

**Última lección:** [17. ACL y protected mode](lessons/0017-acls-and-protected-mode.md)

## Cómo se ve el éxito

- Ante el uso que hace de Redis un sistema existente, identificar si está tratando una caché como un almacén durable, implementando mal un lock o manteniendo un keyspace sin límite, y decir qué se rompe por ello.
- Diseñar desde cero un uso correcto de Redis (keyspace acotado, política de expulsión adecuada, un lock distribuido de verdad) para un caso de uso nuevo.
- Comparar las garantías de persistencia de Redis (RDB/AOF) con la durabilidad respaldada por el WAL de Postgres, y decir cuándo recurrir a Redis en lugar de a una base de datos es la decisión correcta y cuándo es un antipatrón.
- Razonar sobre Redis Cluster/Sentinel al nivel de los compromisos que introduce el clustering, sin necesidad de operar uno.

## Restricciones

- No se asume experiencia previa con Redis.

## Fuera de alcance

- Operar una instancia de Postgres en producción: consulta [`data/postgres`](../../data/postgres/), enlazado para la comparación en lugar de repetido.

## El arco

Diez etapas, de la expulsión al control de acceso. Una etapa abarca varias lecciones y los límites son difusos; lo que da una etapa por terminada es la capacidad, no el número de lecciones.

| Etapa | Lecciones | Cubre | Terminada cuando |
|---|---|---|---|
| 1. Memoria y expulsión | 0001 | Por qué Redis expulsa claves, y el antipatrón que se deriva de olvidarlo | Puedes explicar el efecto de una política de expulsión en una carga de trabajo dada |
| 2. Persistencia | 0002 a 0003 | RDB y AOF, y cómo se compara su durabilidad con el WAL de Postgres | Puedes decir cuándo recurrir a Redis en lugar de a una base de datos es correcto y cuándo es un antipatrón |
| 3. Locks distribuidos | 0004 a 0005 | Errores del lock ingenuo, Redlock, la crítica de Kleppmann | Puedes diseñar, o rechazar con razón, un lock distribuido basado en Redis |
| 4. Antipatrones de caché frente a almacén | 0006 a 0007 | Cache-aside, una caché tratada como almacén durable, un keyspace sin límite | Ante un sistema existente, puedes identificar el mal uso y decir qué se rompe |
| 5. Clustering | 0008 | Redis Cluster y Sentinel, los compromisos que introduce el clustering | Puedes razonar sobre los compromisos del clustering sin necesidad de operar uno |
| 6. Tipos de datos y su modelo de costos | 0009 a 0010 | Strings, hashes, listas, sets, sorted sets, bitmaps, HyperLogLog y cómo elegir entre ellos | Puedes elegir una estructura de datos para un caso de uso planteado y explicar lo que cuesta |
| 7. Mensajería y expiración | 0011 a 0012 | Pub/Sub frente a streams, grupos de consumidores comparados con los de Kafka, expiración de claves perezosa frente a activa | Puedes elegir el mecanismo de mensajería adecuado para un caso de uso y explicar cómo sale realmente una clave de Redis |
| 8. Transacciones y scripting | 0013 a 0014 | `MULTI`/`EXEC`, locking optimista con `WATCH`, scripting con Lua, Redis Functions | Puedes construir una secuencia de comprobar y luego actuar que sea realmente segura, y explicar qué hace atómica la liberación de un lock |
| 9. Rendimiento y operación | 0015 a 0016 | Costo de ida y vuelta, pipelining, pooling de conexiones, `INFO`/`SLOWLOG`/latency monitor/`MEMORY USAGE`, `SCAN` frente a `KEYS` | Puedes reducir el costo de red de un cliente muy conversador y diagnosticar el comportamiento real de una instancia sin congelarla |
| 10. Control de acceso | 0017 | Protected mode, ACL, categorías de comandos, el usuario por defecto | Puedes restringir lo que pueden hacer una conexión sin autenticar y un usuario autenticado |

## Lecciones

Recórrelas en orden.

| # | Lección | Enseña |
|---|---|---|
| [0001](lessons/0001-memory-and-eviction.md) | Memoria y expulsión | Por qué Redis expulsa claves, y el antipatrón que se deriva de olvidarlo |
| [0002](lessons/0002-rdb-snapshotting.md) | Snapshots RDB | Qué captura realmente un snapshot RDB, y la ventana de pérdida de datos que deja abierta su intervalo de guardado |
| [0003](lessons/0003-aof-and-wal-comparison.md) | AOF y la comparación con el WAL | Cómo la política de fsync de AOF fija su ventana de pérdida de datos, y por qué incluso el ajuste habitual más fuerte de Redis cambia más durabilidad por velocidad que Postgres por defecto |
| [0004](lessons/0004-naive-locking-mistakes.md) | Errores del lock ingenuo | Por qué SET NX PX por sí solo no es un lock distribuido, y los dos modos de fallo que lo rompen en condiciones reales |
| [0005](lessons/0005-redlock-and-kleppmanns-critique.md) | Redlock y la crítica de Kleppmann | Qué corrige realmente Redlock del lock ingenuo, qué muestra la crítica de Kleppmann que todavía no corrige y cómo decidir si un lock de Redis es siquiera la herramienta adecuada |
| [0006](lessons/0006-cache-aside-and-the-store-anti-pattern.md) | Cache-aside y el antipatrón del almacén | Qué aspecto tiene un uso correcto de cache-aside, y la forma concreta en que una caché se convierte sin que se note en el sistema de registro cuando se omite ese patrón |
| [0007](lessons/0007-unbounded-keyspace-and-spotting-misuse.md) | El antipatrón del keyspace sin límite y cómo detectar el mal uso | Cómo crece sin límite un keyspace cuando nadie le pone un TTL ni una política de expulsión, y una lista de comprobación para detectar esto y el antipatrón del almacén en un sistema existente |
| [0008](lessons/0008-cluster-and-sentinel.md) | Redis Cluster y Sentinel | Los compromisos que introducen el sharding de Redis Cluster y el failover automático de Sentinel, razonados sin necesidad de operar ninguno de los dos |
| [0009](lessons/0009-strings-hashes-and-lists.md) | Strings, hashes y listas | Las tres estructuras de datos básicas que Redis almacena realmente, y lo que cuesta leer, escribir y hacer crecer cada una |
| [0010](lessons/0010-sets-sorted-sets-and-probabilistic-structures.md) | Sets, sorted sets y estructuras probabilísticas | Elegir una estructura de datos para un caso de uso, desde la pertenencia exacta hasta un conteo aproximado que casi no cuesta nada mantener |
| [0011](lessons/0011-streams-and-pubsub-as-messaging.md) | Streams y Pub/Sub como superficie de mensajería | Dos formas en que Redis mueve mensajes entre clientes, y por qué solo una de ellas es segura para construir una cola encima |
| [0012](lessons/0012-key-expiration-lazy-vs-active.md) | Expiración de claves: perezosa frente a activa | Por qué que el TTL de una clave llegue a cero no la elimina de la memoria por sí solo, y los dos mecanismos que acaban haciéndolo |
| [0013](lessons/0013-multi-exec-and-optimistic-locking-with-watch.md) | MULTI/EXEC y locking optimista con WATCH | Encolar varios comandos para que se ejecuten sin interrupción, y detectar que un valor cambió a tus espaldas antes de actuar sobre él |
| [0014](lessons/0014-lua-scripting-and-redis-functions.md) | Scripting con Lua y Redis Functions | El mecanismo que hace realmente segura la liberación de un lock, ejecutando una comprobación y una acción como un único paso atómico |
| [0015](lessons/0015-pipelining-round-trip-cost-and-connection-pooling.md) | Pipelining, costo de ida y vuelta y pooling de conexiones | Por qué N comandos secuenciales cuestan N viajes de ida y vuelta por la red aunque cada uno se ejecute en microsegundos, y las dos correcciones separadas |
| [0016](lessons/0016-operational-visibility.md) | Visibilidad operativa | Las herramientas que muestran lo que está haciendo realmente una instancia de Redis, y el único comando que ha causado más caídas que casi cualquier otro |
| [0017](lessons/0017-acls-and-protected-mode.md) | ACL y protected mode | Cómo impide Redis que una instancia sin autenticación sea siquiera alcanzable, y cómo acota lo que se le permite hacer realmente a un cliente autenticado |

## Referencia

- [Glosario](GLOSSARY.md): términos canónicos de este tema
- [Recursos](RESOURCES.md): fuentes de confianza
- [Persistencia](reference/persistence.md): qué promete cada uno de RDB y AOF, la ventana de pérdida exacta que deja cada política de fsync y lo que dice la propia documentación de Redis sobre igualar la durabilidad de una base de datos
- [Locks distribuidos](reference/distributed-locks.md): el lock ingenuo y sus dos agujeros, el algoritmo de Redlock con la aritmética de validez y la única pregunta que decide si alguno de los dos es la herramienta adecuada
- [Antipatrones de caché frente a almacén](reference/cache-vs-store-anti-patterns.md): cache-aside bien hecho, las dos formas en que una caché deja de serlo y los ajustes de expulsión que deciden qué fallo obtienes
- [Clustering](reference/clustering.md): lo que te quitan los slots de Cluster, los ajustes que deciden si un clúster degradado sigue sirviendo o se detiene y por qué el quórum de Sentinel no controla el failover

## Cómo funciona

Cada lección es corta y autocontenida. Las claves de respuesta están plegadas: primero recuerda, luego ábrelas. Las prácticas en el mundo real importan más que la lectura, y espaciarlas es el punto. Todo lo que siga sin estar claro al final de una lección merece rastrearse hasta su fuente primaria antes de seguir.
