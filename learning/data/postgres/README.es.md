---
title: Postgres
description: "Opera Postgres: el WAL, vacuum y bloat, replicación y lo que cuesta mantener un índice"
type: topic
---

# Aprendizaje: Postgres

Sé capaz de operar una instancia de Postgres en marcha, autoalojada o gestionada, y de diagnosticar bloat, lag de replicación o un failover que tarda en recuperarse en lugar de adivinar una corrección, así como de diseñar desde el principio el almacenamiento, la replicación y el mantenimiento de índices de un despliegue nuevo.

**Última lección:** [18. Particionado y TOAST](lessons/0018-partitioning-and-toast.md)

## Cómo se ve el éxito

- Ante una tabla con bloat o una réplica con lag, diagnosticar la causa a partir de la mecánica del WAL, de autovacuum y de la replicación, y no por ensayo y error.
- Diseñar el almacenamiento, la topología de replicación y el mantenimiento de índices de un despliegue nuevo y defender cada elección.
- Explicar de qué te protege y de qué no un servicio gestionado (al estilo de RDS), frente a ejecutar tú mismo la instancia.
- Dar cuenta de lo que le cuesta a la base de datos mantener un índice vectorial (pgvector), en conexión con la elección de pgvector como almacén en `llm/rag`.

## Restricciones

- Se asume familiaridad básica con SQL (consulta `programming/sql` para el lenguaje en sí); no se requiere experiencia previa en administración de bases de datos.
- Cubre tanto la operación autoalojada como lo que cambia con un servicio gestionado.

## Fuera de alcance

- Consultas, planes de consulta, diseño de esquemas y semántica de aislamiento: consulta [`programming/sql`](../../programming/sql/), enlazado en lugar de repetido. Este espacio de trabajo se ocupa de la instancia en marcha, no del lenguaje.

## El arco

Doce etapas, de la durabilidad al mantenimiento a nivel de tabla a escala. Una etapa abarca varias lecciones y los límites son difusos; lo que da una etapa por terminada es la capacidad, no el número de lecciones.

| Etapa | Lecciones | Cubre | Terminada cuando |
|---|---|---|---|
| 1. El write-ahead log | 0001 | El mecanismo de durabilidad sobre el que se construye todo lo demás de este espacio de trabajo | Puedes explicar cómo el WAL hace recuperable una caída |
| 2. Vacuum y bloat | 0002 a 0003 | Funcionamiento interno de autovacuum, MVCC y tuplas muertas, diagnóstico y ajuste del bloat | Puedes diagnosticar una tabla con bloat a partir de la mecánica de vacuum y del WAL |
| 3. Replicación | 0004 a 0006 | Streaming replication, replication slots, failover, diagnóstico del lag | Puedes diagnosticar una réplica con lag y diseñar una topología de replicación |
| 4. Los índices y su costo de mantenimiento | 0007 a 0008 | Costo de mantenimiento de B-tree/GiST/GIN, lo que cuesta mantener un índice de pgvector | Puedes diseñar un plan de mantenimiento de índices y dar cuenta del costo de pgvector |
| 5. Gestionado frente a autoalojado | 0009 a 0010 | De qué te protege un servicio gestionado al estilo de RDS, y de qué no | Puedes explicar el límite del servicio gestionado y defender una elección de operación |
| 6. Backup y recuperación a un punto en el tiempo | 0011 | Backups base, archivado continuo del WAL, `recovery_target_time` y por qué una restauración sin probar no es un backup verificado | Puedes diseñar y defender una estrategia de backup que, al probarla, reconstruya de verdad una base de datos que funcione |
| 7. Configuración y ajuste de la memoria | 0012 | `shared_buffers`, `work_mem`, `maintenance_work_mem`, ajuste de los checkpoints | Puedes dimensionar estos ajustes según la concurrencia real y no según una prueba aislada de una sola consulta |
| 8. Monitorización | 0013 | `pg_stat_activity`, wait events, `pg_stat_statements`, el log del servidor | Puedes elegir la superficie de monitorización adecuada (estado en vivo de los backends, costo agregado de las consultas o un evento registrado) para un síntoma dado |
| 9. Gestión de conexiones | 0014 | `max_connections`, el costo de un proceso por conexión, los modos de pooling de sesión/transacción/sentencia de PgBouncer | Puedes elegir un modo de pooling que se ajuste a aquello de lo que depende realmente la aplicación, en lugar de quedarte por defecto con el más eficiente |
| 10. Replicación lógica y actualizaciones de versión mayor | 0015 a 0016 | Publicaciones y suscripciones, la restricción de DDL de la replicación lógica, los modos de transferencia de `pg_upgrade`, la vía de actualización con replicación lógica y poco tiempo de inactividad | Puedes elegir y defender una vía de actualización (`pg_upgrade` in situ o cambio mediante replicación lógica) para un presupuesto de tiempo de inactividad planteado |
| 11. Roles, privilegios y seguridad a nivel de fila | 0017 | Roles frente a la separación entre usuarios y grupos que hacen otros sistemas, las opciones INHERIT/SET de la pertenencia, GRANT a nivel de tabla, la seguridad a nivel de fila y su exención por defecto para el propietario | Puedes diseñar una disposición de roles y políticas RLS y nombrar por qué activar RLS por sí solo no restringe al propietario de la tabla |
| 12. Particionado y TOAST | 0018 | Particionado por rango/lista/hash, poda de particiones, borrado masivo sin bloat, TOAST y sus cuatro estrategias de almacenamiento | Puedes diseñar una disposición de particiones para gestionar el ciclo de vida sin bloat y dar cuenta de la estrategia de almacenamiento de una columna grande |

## Lecciones

Recórrelas en orden.

| # | Lección | Enseña |
|---|---|---|
| [0001](lessons/0001-the-write-ahead-log.md) | El write-ahead log | El mecanismo de durabilidad sobre el que se construye todo lo demás de este espacio de trabajo |
| [0002](lessons/0002-mvcc-and-dead-tuples.md) | MVCC y tuplas muertas | Por qué un UPDATE o un DELETE nunca elimina nada de inmediato, y por qué eso deja tuplas muertas que vacuum tiene que limpiar |
| [0003](lessons/0003-bloat-diagnosis-and-autovacuum-tuning.md) | Diagnóstico del bloat y ajuste de autovacuum | Cómo medir el bloat, por qué autovacuum se queda atrás y el orden de diagnóstico que encuentra la causa real en lugar de adivinarla |
| [0004](lessons/0004-streaming-replication-and-slots.md) | Streaming replication y replication slots | Cómo se conecta y se pone al día realmente un standby, y qué garantiza un replication slot que el streaming a secas no garantiza |
| [0005](lessons/0005-failover-mechanics.md) | Mecánica del failover | Qué ocurre cuando se promueve un standby, por qué un antiguo primario no puede simplemente volver a unirse y el compromiso de pérdida de datos que acota la replicación síncrona |
| [0006](lessons/0006-diagnosing-replication-lag.md) | Diagnosticar el lag de replicación | Por qué el lag de recepción y el lag de aplicación son medidas distintas, y el orden de diagnóstico que encuentra cuál está ocurriendo realmente |
| [0007](lessons/0007-index-maintenance-cost.md) | Costo de mantenimiento de B-tree, GiST y GIN | Por qué cada índice encarece las escrituras, y cómo B-tree, GiST y GIN pagan cada uno ese costo de forma distinta |
| [0008](lessons/0008-what-a-pgvector-index-costs.md) | Lo que cuesta mantener un índice de pgvector | El costo en disco, en tiempo de construcción y en memoria permanente que un índice vectorial añade más allá de los vectores en bruto que indexa |
| [0009](lessons/0009-what-managed-shields-you-from.md) | De qué te protege un servicio gestionado | Lo que elimina realmente la automatización al estilo de RDS, y por qué todo lo de las lecciones anteriores sigue necesitando entenderse por debajo |
| [0010](lessons/0010-defending-an-operating-choice.md) | Defender una elección de operación | Un diseño de despliegue resuelto que cita una decisión y un costo concretos de cada etapa, en lugar de asumir una respuesta por defecto |
| [0011](lessons/0011-backup-and-point-in-time-recovery.md) | Backup y recuperación a un punto en el tiempo | Un backup base y un archivo continuo del WAL juntos te permiten reconstruir cualquier momento desde el backup, no solo el momento en que se hizo el propio backup, y una restauración sin probar no es un backup verificado |
| [0012](lessons/0012-configuration-and-memory-tuning.md) | Configuración y ajuste de la memoria | shared_buffers, work_mem y maintenance_work_mem responden cada uno a una pregunta de memoria distinta, y el que más a menudo se ajusta mal es el que se multiplica en silencio por tantas operaciones como estén corriendo realmente a la vez |
| [0013](lessons/0013-monitoring-activity-statements-and-the-log.md) | Monitorización: actividad, sentencias y el log | Una vista en vivo de lo que está haciendo ahora mismo cada backend, una vista agregada de lo que realmente más le cuesta al servidor con el tiempo y un log que nombra exactamente detrás de qué está bloqueada una consulta atascada son tres preguntas distintas |
| [0014](lessons/0014-connection-management-and-pgbouncer.md) | Gestión de conexiones y PgBouncer | Cada conexión de Postgres es un proceso completo del sistema operativo, por eso suele hacer falta un pooler, y los tres modos de pooling de PgBouncer cambian cada uno de forma distinta corrección a nivel de sesión por eficiencia de reutilización |
| [0015](lessons/0015-logical-replication-publications-and-subscriptions.md) | Replicación lógica, publicaciones y suscripciones | La streaming replication envía el WAL en bruto para construir una copia idéntica de todo el clúster; la replicación lógica decodifica esos mismos cambios en eventos a nivel de fila que un suscriptor puede aplicar de forma selectiva, entre versiones mayores, a costa de no replicar nunca el DDL por sí sola |
| [0016](lessons/0016-major-version-upgrades-and-pg-upgrade.md) | Actualizaciones de versión mayor y pg_upgrade | Los modos de transferencia más rápidos de pg_upgrade compran su velocidad renunciando a poder revertir sin más, y la replicación lógica ofrece un compromiso realmente distinto, un tiempo de inactividad casi nulo, a costa de gestionar el DDL a mano durante toda la migración |
| [0017](lessons/0017-roles-privileges-and-row-level-security.md) | Roles, privilegios y seguridad a nivel de fila | Los GRANT a nivel de tabla y la seguridad a nivel de fila son dos capas de autorización separadas, y activar RLS no restringe al propietario de la tabla a menos que se lo indiques explícitamente |
| [0018](lessons/0018-partitioning-and-toast.md) | Particionado y TOAST | El particionado convierte un recorrido de toda la tabla en un recorrido solo de las particiones relevantes y hace que el borrado masivo no genere bloat, mientras que TOAST es la razón por la que una sola fila puede contener un valor mucho mayor que una página de 8 kB |

## Referencia

- [Glosario](GLOSSARY.md): términos canónicos de este tema
- [Recursos](RESOURCES.md): fuentes de confianza
- [Vacuum y bloat](reference/vacuum-and-bloat.md): qué dispara autovacuum y con qué números, qué frena el espacio que puede recuperar y las vistas que hay que consultar y en qué orden
- [Replicación](reference/replication.md): qué garantiza un slot y qué arriesga, los cinco niveles síncronos y cuándo tres de ellos no hacen nada, y los dos lags con las columnas que los distinguen
- [Mantenimiento de índices](reference/index-maintenance.md): qué cobra cada tipo de índice por escritura y qué lo degrada, y los parámetros y el precipicio de memoria que trae consigo un índice de pgvector
- [Gestionado frente a autoalojado](reference/managed-vs-self-hosted.md): qué automatiza un servicio gestionado y qué solo traslada de sitio, las tres formas de alta disponibilidad que no son intercambiables y las decisiones que tiene que nombrar un diseño bien defendido

## Cómo funciona

Cada lección es corta y autocontenida. Las claves de respuesta están plegadas: primero recuerda, luego ábrelas. Las prácticas en el mundo real importan más que la lectura, y espaciarlas es el punto. Todo lo que siga sin estar claro al final de una lección merece rastrearse hasta su fuente primaria antes de seguir.
