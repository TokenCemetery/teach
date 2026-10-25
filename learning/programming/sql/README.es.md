---
title: SQL
description: "Hazte cargo de la base de datos: escribe la consulta, lee el plan, diseña el esquema, sobrevive a la concurrencia"
type: topic
---

# Aprendizaje: SQL

Conviértete en el ingeniero al que un equipo le confía su base de datos: capaz de expresar una pregunta como una consulta que responda exactamente a ella, de leer un plan de consulta para averiguar por qué esa consulta es lenta, de elegir un índice a partir de la evidencia y no del instinto, de razonar sobre lo que pueden observar las transacciones concurrentes, y de diseñar y migrar un esquema que deje fuera los datos malos y siga siendo rápido a medida que crece la tabla.

**Empieza aquí:** [0001. Tablas, filas y tipos](lessons/0001-tables-rows-and-types.md)
**Última lección:** [0053. Triggers, procedimientos almacenados y dónde debe vivir la lógica](lessons/0053-triggers-stored-procedures-and-where-logic-belongs.md)

## Cómo se ve el éxito

- Escribir una consulta con joins, agregación y funciones de ventana que responda a la pregunta planteada, y explicar por qué el resultado tiene exactamente esas filas, `NULL` incluidos.
- Leer un plan de ejecución con tiempos reales y nombrar qué paso es el problema.
- Elegir un índice, o rechazarlo, a partir del plan y de la selectividad, y luego demostrar la diferencia con una medición.
- Decir lo que puede observar una transacción en un nivel de aislamiento dado, y nombrar la anomalía de la que depende un bug de concurrencia.
- Diseñar un esquema en el que los datos malos sean imposibles y no solo desaconsejados, usando claves, tipos y restricciones.
- Cambiar un esquema en un sistema en vivo sin tiempo de inactividad y sin una cola de locks detrás de la migración.
- Tomar una consulta lenta generada por un ORM, explicar por qué es lenta y reescribirla.
- Revisar la consulta o el esquema de otra persona y nombrar en concreto lo que costará con diez veces más filas.

## Restricciones

- No se asume experiencia previa con SQL ni con la administración de bases de datos.
- PostgreSQL es el motor de referencia, porque su documentación es la descripción libre más completa de cómo se comportan un planificador real y un modelo de concurrencia real. Se usa SQLite donde una práctica no debería necesitar ningún servidor. Donde los motores difieren de verdad, la lección lo dice y nombra el comportamiento estándar si lo hay.
- Solo necesita un motor local y una terminal en cualquier sistema operativo soportado. Nada en el arco requiere herramientas de pago, una cuenta en la nube ni una base de datos gestionada.
- Las prácticas necesitan datos, y una tabla con diez filas enseña la lección equivocada sobre los índices. El arco usa un único conjunto de datos que crece lo suficiente como para que las elecciones del planificador sean reales.
- El comportamiento del planificador cambia entre versiones mayores. Las afirmaciones sensibles a la versión se contrastan con la documentación actual, y cualquier lección que dependa de una versión dice cuál.

## Fuera de alcance

- La administración de bases de datos como tema: backups y recuperación, replicación, failover, pooling de conexiones, actualizaciones de versión. Consulta [`data/postgres`](../../data/postgres/), que se ocupa de la instancia en marcha.
- Los ORM y los query builders como temas propios. Su salida se lee y se critica en la etapa 7; no se enseña a configurar uno.
- Ejecutar migraciones desde un pipeline de despliegue: cuándo se ejecuta una migración respecto al código que la necesita, y cómo expand and contract reparte un cambio entre varios despliegues. Eso es [`infrastructure/ci-cd`](../../infrastructure/ci-cd/), cuya hoja [Despliegues](../../infrastructure/ci-cd/reference/deployments.md) contiene el orden de las migraciones.
- Los almacenes analíticos y sus dialectos: BigQuery, Snowflake, Redshift, Spark SQL. La ejecución columnar cambia los consejos de rendimiento, y el arco no la persigue. Consulta [`data/warehouses`](../../data/warehouses/), que se ocupa de la ejecución columnar y de lo que cambia.
- Los almacenes no relacionales como alternativas con las que comparar. El que tiene un track propio es [`data/redis`](../../data/redis/).
- Los detalles internos del motor más allá del punto en que dejan de explicar el comportamiento de las consultas y las transacciones: formatos en disco, detalles internos del write-ahead log, el código fuente del planificador.

## El arco

Siete etapas, desde ningún conocimiento previo hasta el criterio de un perfil sénior. No es una lista de lecciones: una etapa abarca varias lecciones y los límites son difusos.

| Etapa | Lecciones | Cubre | Terminada cuando |
|---|---|---|---|
| 1. El modelo relacional | 0001 a 0006 | Tablas, filas y tipos, `NULL` y la lógica trivalente, `SELECT`, filtrado, ordenación, conjuntos frente a multiconjuntos, qué es una clave | Puedes decir por qué una consulta devolvió exactamente esas filas, incluidas las que eliminó `NULL` |
| 2. Consultas | 0007 a 0013 | Todos los tipos de join, agregación y `GROUP BY`, `HAVING`, subconsultas, common table expressions, operaciones de conjuntos | Expresas una pregunta como una sola consulta sin ensayo y error |
| 3. Más allá de lo básico | 0014 a 0020 | Funciones de ventana y marcos, lateral joins, consultas recursivas, columnas `JSON` donde se ganan su sitio | Resuelves problemas de rankings y de totales acumulados en SQL y no en el código de la aplicación |
| 4. Diseño de esquemas | 0021 a 0027 | La normalización y cuándo parar, claves primarias y foráneas, restricciones, elegir los tipos de forma deliberada, claves subrogadas frente a naturales | Los datos malos son imposibles y no solo desaconsejados |
| 5. Transacciones | 0028 a 0034 | ACID como cuatro promesas separadas, los niveles de aislamiento y las anomalías que permite cada uno, control de concurrencia multiversión, locking, deadlocks, locks de fila explícitos, idempotencia | Puedes nombrar la anomalía de la que depende un bug de concurrencia antes de reproducirlo |
| 6. Rendimiento | 0035 a 0041 | Primero los índices B-tree y después los demás, selectividad y cardinalidad, estadísticas, leer un plan con tiempos, estrategias de join, paginación, cuándo el problema no es la consulta | Optimizas a partir de un plan y demuestras la mejora con una medición |
| 7. Operación y criterio | 0042 a 0048 | Migraciones sin tiempo de inactividad, revisar consultas y esquemas, leer la salida de un ORM, portabilidad entre motores, cuándo SQL es la herramienta equivocada | Se confía en ti para tomar la decisión y explicársela a otra persona; la etapa 8 lo completa con las preguntas de revisión sobre autorización y lógica procedimental que daba por supuestas la lista de comprobación de esta etapa |
| 8. Seguridad y herramientas especializadas | 0049 a 0053 | Inyección SQL y sentencias parametrizadas, roles y mínimo privilegio, seguridad a nivel de fila, búsqueda de texto completo, triggers y procedimientos almacenados | Revisas un límite de autorización y un fragmento de lógica procedimental con la misma concreción que una consulta o un cambio de esquema |

## Lecciones

Recórrelas en orden.

| # | Lección | Enseña |
|---|---|---|
| [0001](lessons/0001-tables-rows-and-types.md) | Tablas, filas y tipos | El tipo de una columna es una restricción que obtienes gratis, y el equivocado es difícil de deshacer |
| [0002](lessons/0002-select-and-evaluation-order.md) | SELECT y el orden de evaluación | Las cláusulas se ejecutan en un orden distinto al que se escriben, lo que explica la mayoría de los errores de principiante |
| [0003](lessons/0003-null-and-three-valued-logic.md) | NULL y la lógica trivalente | WHERE solo conserva lo verdadero, así que lo desconocido se comporta como falso y NOT IN puede no devolver nada |
| [0004](lessons/0004-sets-and-bags.md) | Conjuntos y multiconjuntos | Una tabla es un multiconjunto, así que los duplicados son reales y UNION paga en silencio por eliminarlos |
| [0005](lessons/0005-sorting-and-collation.md) | Ordenación y collation | El orden del texto depende de una collation, y un empate sin una clave única no es estable |
| [0006](lessons/0006-keys-and-constraints.md) | Claves y restricciones | Una clave es una afirmación que la base de datos hace cumplir, y cada afirmación que omites se convierte en un bug |
| [0007](lessons/0007-joins-and-what-they-do.md) | Joins, y lo que hace realmente un join | Un join es un producto cartesiano filtrado, así que la condición ON decide qué filas existen antes de que se ejecute nada más |
| [0008](lessons/0008-outer-joins-and-missing-rows.md) | Outer joins y las filas que no están | Un outer join conserva las filas que no coincidieron con nada, y una sola cláusula WHERE las vuelve a descartar en silencio |
| [0009](lessons/0009-aggregation-and-group-by.md) | Agregación y GROUP BY | Los agregados ignoran NULL, y un join que multiplica filas multiplica el total |
| [0010](lessons/0010-having-and-filter.md) | HAVING, FILTER y varias agrupaciones a la vez | Dónde va una condición decide qué filas puede seguir viendo, y una sola pasada puede responder a varias agrupaciones |
| [0011](lessons/0011-subqueries.md) | Subconsultas, y qué tipo responde a la pregunta | Un escalar, un IN, un EXISTS y una tabla derivada responden a cuatro preguntas distintas, y uno de ellos miente cuando aparece NULL |
| [0012](lessons/0012-common-table-expressions.md) | Common table expressions | WITH da nombre a un paso para que una consulta larga se lea de arriba abajo, y en esta versión no es una barrera de optimización |
| [0013](lessons/0013-set-operations.md) | Operaciones de conjuntos, y una pregunta como una sola consulta | UNION, INTERSECT y EXCEPT combinan conjuntos de resultados por posición y eliminan duplicados salvo que se les diga lo contrario |
| [0014](lessons/0014-window-functions.md) | Funciones de ventana | Una función de ventana calcula sobre otras filas sin colapsar aquella en la que está |
| [0015](lessons/0015-window-frames.md) | Marcos de ventana | El marco por defecto incluye todas las filas que empatan con la actual, por eso un total acumulado puede dar saltos |
| [0016](lessons/0016-navigating-within-a-window.md) | Navegar dentro de una ventana | lag, lead y las funciones de valor llegan directamente a otras filas, y dos de ellas obedecen al marco |
| [0017](lessons/0017-lateral-joins.md) | Lateral joins | LATERAL permite que una subconsulta en FROM vea la fila de al lado, que es como se obtienen los primeros de cada grupo |
| [0018](lessons/0018-recursive-queries.md) | Consultas recursivas | Una CTE recursiva se realimenta con su propia salida hasta que no sale nada nuevo, que es como se recorre una jerarquía |
| [0019](lessons/0019-json-columns.md) | Columnas JSON | Consultar una columna de documentos es SQL corriente una vez que sabes qué operador devuelve texto y cuál devuelve JSON |
| [0020](lessons/0020-choosing-the-tool.md) | Elegir la herramienta | Los primeros N, los totales acumulados y la deduplicación tienen cada uno dos o tres formas correctas de escribirse, y la elección depende de lo que pregunta la pregunta |
| [0021](lessons/0021-normalisation.md) | Normalización | Cada forma normal elimina una manera de que dos filas discrepen sobre el mismo hecho |
| [0022](lessons/0022-choosing-a-key.md) | Elegir una clave | Una clave subrogada compra estabilidad y renuncia al significado, y el generador que eliges decide qué más cuesta |
| [0023](lessons/0023-foreign-keys.md) | Claves foráneas y qué pasa al borrar | Una clave foránea es una promesa sobre filas que existen, y la acción que eliges decide quién paga cuando una desaparece |
| [0024](lessons/0024-constraints-that-hold.md) | Restricciones que se cumplen de verdad | Un CHECK solo falla cuando su condición es falsa, así que un valor ausente cumple casi todas las reglas que escribiste |
| [0025](lessons/0025-choosing-types.md) | Elegir los tipos de forma deliberada | Un tipo decide lo que aceptará la base de datos, lo que cambiará en silencio y lo que nunca podrá deshacer |
| [0026](lessons/0026-denormalising-on-purpose.md) | Desnormalizar a propósito | Una segunda copia de un hecho es una segunda oportunidad de equivocarse, salvo que sea la base de datos quien la mantenga |
| [0027](lessons/0027-making-bad-data-impossible.md) | Hacer imposibles los datos malos | Tomar un esquema que permite una fila errónea y cerrar todos los huecos, y luego decir lo que el diseño todavía no puede prometer |
| [0028](lessons/0028-what-a-transaction-promises.md) | Lo que promete una transacción | Cuatro promesas viajan bajo un mismo acrónimo, y solo una de ellas es negociable por ti |
| [0029](lessons/0029-mvcc.md) | Control de concurrencia multiversión | Un update escribe una nueva versión de la fila en lugar de cambiarla, por eso un lector nunca espera a un escritor |
| [0030](lessons/0030-isolation-levels.md) | Niveles de aislamiento | PostgreSQL te da tres niveles distintos bajo cuatro nombres, y cada uno permite un conjunto distinto de sorpresas |
| [0031](lessons/0031-the-anomalies.md) | Las anomalías, y cómo reconocer la tuya | Todo bug de concurrencia tiene un nombre, y nombrarlo te dice qué nivel o qué lock lo habría evitado |
| [0032](lessons/0032-locks.md) | Locks que tomas a propósito | Un lock de fila es la forma de mantener quieta una decisión, y cada uno tiene un modo de fallo que vale la pena elegir |
| [0033](lessons/0033-deadlocks.md) | Deadlocks | Dos transacciones que retienen cada una lo que la otra necesita, y la única cura es acordar un orden de antemano |
| [0034](lessons/0034-idempotency-and-retry.md) | Idempotencia y el reintento correcto | Un reintento que repite las mismas sentencias reproduce el bug que debía corregir, así que tiene que volver a leer y volver a decidir |
| [0035](lessons/0035-reading-a-plan.md) | Leer un plan | El plan te dice lo que hizo la base de datos y lo que esperaba, y la diferencia entre ambos es donde está el trabajo |
| [0036](lessons/0036-what-an-index-does.md) | Lo que hace realmente un índice | Un B-tree convierte un recorrido de todas las filas en un descenso por unas pocas páginas, y el plan nombra de cuál de cuatro formas las leyó |
| [0037](lessons/0037-selectivity-and-statistics.md) | Selectividad y estadísticas | Todo plan se construye a partir de una muestra de tus datos, así que un mal plan suele ser una mala estimación y no un mal planificador |
| [0038](lessons/0038-choosing-an-index.md) | Elegir un índice | El orden de las columnas decide a qué consultas puede responder un índice, y el mejor índice es a menudo el que decides no crear |
| [0039](lessons/0039-join-strategies.md) | Estrategias de join | Tres formas de hacer un join, y el planificador elige según el costo estimado, así que una estimación errónea aparece como la estrategia equivocada |
| [0040](lessons/0040-pagination-and-counting.md) | Paginación y conteo | OFFSET lee y descarta cada fila que se salta, y contar con exactitud cuesta una pasada por la tabla |
| [0041](lessons/0041-when-the-query-is-not-the-problem.md) | Cuando el problema no es la consulta | Demostrar una mejora necesita una medición que puedas repetir, y la causa suele estar en la tabla, en el tráfico o en el cliente |
| [0042](lessons/0042-migrations-without-downtime.md) | Migraciones sin tiempo de inactividad | Una migración que tarda un milisegundo puede seguir deteniendo todas las lecturas de la tabla, por lo que se encola detrás de ella |
| [0043](lessons/0043-changing-what-has-data.md) | Cambiar lo que ya tiene datos | Una restricción sobre una tabla llena son dos sentencias, y un backfill es un bucle y no un único UPDATE |
| [0044](lessons/0044-reviewing-a-query.md) | Revisar una consulta | Leer la consulta por las filas que devuelve antes de leerla por su velocidad, porque una respuesta rápida y errónea es peor |
| [0045](lessons/0045-reviewing-a-schema-change.md) | Revisar un cambio de esquema | Preguntar qué bloquea la migración, qué reescribe y qué se ejecuta mientras las dos versiones del código están en vivo |
| [0046](lessons/0046-portability.md) | La portabilidad y lo que cuesta | La mayor parte de este arco viaja entre motores, y las partes que no lo hacen son las partes de las que vale la pena depender de forma deliberada |
| [0047](lessons/0047-reading-orm-output.md) | Leer lo que emite un ORM | El ORM escribe el SQL que tú no escribiste, y la única forma de saber lo que envió es mirarlo |
| [0048](lessons/0048-trusted-with-the-database.md) | Alguien de confianza para la base de datos | Siete etapas terminan en un solo hábito, que es nombrar la fila, el lock o el plan que hace defendible una decisión |
| [0049](lessons/0049-sql-injection-and-parameterised-statements.md) | Inyección SQL y sentencias parametrizadas | La concatenación de strings permite que un valor cambie lo que significa una sentencia, no solo con qué coincide, y una sentencia parametrizada elimina esa posibilidad en lugar de intentar sanear cada caso |
| [0050](lessons/0050-roles-and-least-privilege.md) | Roles y mínimo privilegio | Los roles engloban las antiguas ideas de usuarios y grupos, la propiedad ya concede todos los privilegios sin necesidad de GRANT, y el mínimo privilegio trata por completo de lo que se les permite hacer a todos los demás |
| [0051](lessons/0051-row-level-security.md) | Seguridad a nivel de fila | GRANT decide el acceso a una tabla en su conjunto, una política de seguridad de filas lo decide por fila, y el motor la hace cumplir en todas las vías de acceso, no solo en la que un desarrollador se acordó de filtrar |
| [0052](lessons/0052-full-text-search.md) | Búsqueda de texto completo | tsvector reduce un documento a lexemas normalizados que un índice GIN puede buscar, tsquery pregunta si están presentes, y el límite con un motor de búsqueda dedicado está donde el ranking y la escala le quedan grandes a una sola columna |
| [0053](lessons/0053-triggers-stored-procedures-and-where-logic-belongs.md) | Triggers, procedimientos almacenados y dónde debe vivir la lógica | Este es el cierre de la etapa 8: un trigger se ejecuta en cada vía que llega a una tabla y un procedimiento puede confirmar o revertir su propia transacción, y la cuestión de criterio es decidir cuándo esa invisibilidad compensa realmente su costo |

## Referencia

- [Glosario](GLOSSARY.md): términos canónicos de este tema
- [Recursos](RESOURCES.md): fuentes de confianza, cada una anotada con lo que cubre
- [El conjunto de datos](reference/the-dataset.md): el esquema y los datos que consulta cada lección a partir de la etapa 2, y cómo cargarlos
- [NULL y la lógica trivalente](reference/null-and-three-valued-logic.md): tablas de verdad, dónde NULL cuenta como igual y las trampas con sus correcciones
- [Orden de evaluación de un SELECT](reference/select-evaluation-order.md): qué se ejecuta y cuándo, qué puede ver cada cláusula y qué errores explica eso
- [Consultas](reference/querying.md): la hoja de la etapa 2, con todos los tipos de join, lo que hace cada agregado con NULL y dónde va una condición
- [Más allá de lo básico](reference/beyond-the-basics.md): la hoja de la etapa 3, con las funciones de ventana, los modos de marco y qué herramienta responde a qué pregunta
- [Diseño de esquemas](reference/schema-design.md): la hoja de la etapa 4, con las formas normales, todos los tipos de restricción y qué rechaza cada tipo
- [Transacciones](reference/transactions.md): la hoja de la etapa 5, con cada nivel de aislamiento, las anomalías que permite, la fuerza de los locks y los errores reintentables
- [Rendimiento](reference/performance.md): la hoja de la etapa 6, con los nodos del plan, en qué números confiar, las estrategias de recorrido y de join, y las decisiones sobre índices
- [Operación](reference/operating.md): la hoja de la etapa 7, con qué migraciones son seguras, las preguntas de revisión y lo que viaja entre motores

## Cómo funciona

Cada lección es corta y autocontenida. Las claves de respuesta están plegadas: primero recuerda, luego ábrelas. Las prácticas en el mundo real importan más que la lectura, y espaciarlas es el punto. Todo lo que siga sin estar claro al final de una lección merece rastrearse hasta su fuente primaria antes de seguir.
