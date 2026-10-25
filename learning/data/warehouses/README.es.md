---
title: Warehouses
description: "Domina el almacén analítico: almacenamiento y ejecución columnar, almacenamiento separado del cómputo y por qué los consejos de rendimiento de un almacén por filas dejan de valer"
type: topic
---

# Aprendizaje: Almacenes analíticos

Sé capaz de diseñar una tabla, un modelo y una vía de carga en BigQuery, Snowflake o Redshift que respondan a las preguntas analíticas que se les hacen con un costo que puedas predecir, y de explicar a partir de la disposición del almacenamiento por qué un consejo que era correcto en un almacén por filas es erróneo allí.

**Última lección:** [20. Cambiar un modelo que otros consultan](lessons/0020-changing-a-model-others-query.md)

## Cómo se ve el éxito

- Explicar a partir de la disposición del almacenamiento por qué una consulta es barata en un almacén por filas y cara en un almacén columnar, o al revés, y predecir qué le hace un cambio en la consulta a los bytes que escanea.
- Decir qué separan BigQuery, Snowflake y Redshift, cada uno, entre almacenamiento y cómputo, y dimensionar o aislar el cómputo para una carga de trabajo planteada.
- Elegir el particionado, el clustering o las sort keys y una distribución para una tabla a partir de su patrón de consultas, y mostrar el escaneo que esa elección ahorra.
- Diseñar un modelo dimensional con un grano planteado, incluido cómo una dimensión que cambia conserva su historial.
- Diseñar una vía de carga, por lotes o en micro-batch, que pueda volver a ejecutarse sin duplicar ni perder filas.
- Estimar lo que cuesta una consulta o una carga de trabajo con precios on-demand y con precios por capacidad, y reducir ese costo sin cambiar la respuesta.
- Decidir entre un almacén, Postgres y un lakehouse para una carga de trabajo, revisar el esquema y la factura del almacén de otra persona, y cambiar un modelo que otros consultan sin romperles nada.

## Restricciones

- Se asume SQL operativo y ninguna experiencia previa con almacenes. El lenguaje, los planes de consulta y el diseño de esquemas transaccionales se enseñan en [`programming/sql`](../../programming/sql/), y estas lecciones los dan por sabidos.
- BigQuery, Snowflake y Redshift son las tres plataformas que se comparan a lo largo de todo el track. Cada lección enseña primero el mecanismo y luego nombra cómo lo expone cada plataforma, para que el material sobreviva a un cambio de proveedor.
- Los valores por defecto, los límites y los precios de las plataformas cambian entre versiones. Donde una lección cita uno, nombra la página de documentación de la que salió, y el lector debe consultar esa página para conocer el valor actual.

## Fuera de alcance

- El lenguaje SQL, los planes de consulta, el diseño de esquemas y el aislamiento en un almacén por filas: consulta [`programming/sql`](../../programming/sql/), sobre el que se construye este track en lugar de repetirlo.
- Operar una instancia de Postgres: consulta [`data/postgres`](../../data/postgres/). La etapa 8 compara Postgres como candidato para una carga de trabajo analítica; no enseña a operarlo.
- Las plataformas de streaming como tema. La etapa 6 carga desde un stream; cómo funciona el propio log está en [`data/kafka`](../../data/kafka/).
- Los frameworks de orquestación y de transformación (Airflow, dbt) como temas. Aparecen donde una lección de carga o de modelado los necesita, y no se enseña a configurarlos.
- Las herramientas de BI, las capas semánticas y el diseño de dashboards.
- Spark, Trino y otros motores como temas. La etapa 8 sitúa frente al almacén el lakehouse que consultan; no enseña a ejecutarlos.

## El arco

Ocho etapas, de la disposición del almacenamiento al criterio. Una etapa abarca varias lecciones y los límites son difusos; lo que da una etapa por terminada es la capacidad, no el número de lecciones.

| Etapa | Lecciones | Cubre | Terminada cuando |
|---|---|---|---|
| 1. Almacenamiento por filas y por columnas | 0001 a 0002 | Patrones de acceso OLTP y OLAP, almacenes por filas frente a almacenes por columnas, row groups, column chunks y sus estadísticas | Puedes predecir qué disposición lee menos bytes para una consulta planteada, y por qué |
| 2. Ejecución columnar | 0003 a 0004 | Codificación por diccionario, run-length y delta, compresión, ejecución vectorizada, materialización tardía | Puedes decir por qué un almacén por columnas comprime y ejecuta como lo hace, y lo que cuesta allí `SELECT *` |
| 3. Almacenamiento y cómputo | 0005 a 0006 | Cómo BigQuery, Snowflake y Redshift separan el almacenamiento del cómputo, slots, virtual warehouses, tipos de nodo, concurrencia y aislamiento de cargas de trabajo | Puedes dimensionar y aislar el cómputo para una carga de trabajo planteada en cualquiera de los tres |
| 4. Diseño físico | 0007 a 0010 | Particionado y pruning, clustering y sort keys, zone maps, distribución y estrategia de join, los consejos de almacén por filas que dejan de valer | Puedes elegir la disposición física de una tabla a partir de su patrón de consultas y mostrar el escaneo que ahorra |
| 5. Modelado dimensional | 0011 a 0013 | Hechos, dimensiones y el grano, esquemas en estrella frente a tablas anchas y anidadas, slowly changing dimensions | Puedes diseñar un modelo con un grano planteado que conserve el historial que una pregunta necesita |
| 6. Carga | 0014 a 0015 | ELT frente a ETL, carga por lotes y tamaño de los archivos, ingesta en micro-batch y en streaming, merges idempotentes | Puedes diseñar una vía de carga que pueda volver a ejecutarse sin duplicar ni perder filas |
| 7. Costo | 0016 a 0017 | Precios on-demand y por capacidad en cada plataforma, leer el costo de una consulta, cachés, vistas materializadas y los controles que limitan una factura | Puedes estimar el costo de una carga de trabajo y reducirlo sin cambiar la respuesta |
| 8. Criterio | 0018 a 0020 | Almacén frente a Postgres frente a un lakehouse, revisar un esquema y su factura, cambiar un modelo que otros consultan, zanjar una disputa a partir de la documentación de la plataforma | Se confía en ti para tomar la decisión y explicársela a otra persona |

## Lecciones

Recórrelas en orden.

| # | Lección | Enseña |
|---|---|---|
| [0001](lessons/0001-row-stores-and-column-stores.md) | Almacenes por filas y almacenes por columnas | Por qué una consulta analítica lee de un almacén por columnas una fracción de los bytes que lee de un almacén por filas, y por qué una búsqueda de una sola fila va en sentido contrario |
| [0002](lessons/0002-inside-a-columnar-file.md) | Dentro de un archivo columnar | Cómo los row groups, los column chunks y las estadísticas por chunk permiten a un lector saltarse datos que nunca descomprime |
| [0003](lessons/0003-encoding-and-compression.md) | Codificación y compresión | Por qué una columna de un solo tipo comprime mucho mejor que una fila, y qué codificación conviene a cada forma de los datos |
| [0004](lessons/0004-vectorized-execution-and-late-materialization.md) | Ejecución vectorizada y materialización tardía | Cómo un motor columnar procesa un lote de valores por llamada y ensambla filas solo para los valores que sobreviven |
| [0005](lessons/0005-separating-storage-from-compute.md) | Separar el almacenamiento del cómputo | Qué mantienen separado BigQuery, Snowflake y Redshift, cada uno, entre donde viven los datos y lo que los lee, y qué aporta y qué cuesta eso |
| [0006](lessons/0006-compute-sizing-concurrency-and-isolation.md) | Dimensionamiento del cómputo, concurrencia y aislamiento de cargas de trabajo | Cómo dimensionar el cómputo para una carga de trabajo y evitar que las consultas de un equipo hagan cola detrás de las de otro |
| [0007](lessons/0007-partitioning-and-pruning.md) | Particionado y pruning | Cómo una tabla particionada permite que un filtro se salte particiones enteras, y los filtros que escanean todo sin avisar |
| [0008](lessons/0008-clustering-and-sort-keys.md) | Clustering y sort keys | Cómo ordenar los datos dentro del almacenamiento estrecha el mínimo y el máximo de cada bloque para que un filtro se salte más bloques |
| [0009](lessons/0009-joins-and-data-distribution.md) | Joins y distribución de los datos | Cómo un almacén distribuido mueve filas para unirlas, y cómo una elección de distribución decide si tiene que hacerlo |
| [0010](lessons/0010-the-row-store-advice-that-stops-applying.md) | Los consejos de almacén por filas que dejan de valer | Qué hábitos de indexar y normalizar un almacén por filas son erróneos en un almacén columnar, y cuáles siguen valiendo |
| [0011](lessons/0011-facts-dimensions-and-the-grain.md) | Hechos, dimensiones y el grano | Cómo declarar qué significa una fila de una tabla de hechos antes de elegir una sola columna |
| [0012](lessons/0012-star-schemas-wide-tables-and-nesting.md) | Esquemas en estrella, tablas anchas y anidamiento | Cuándo mantener las dimensiones en sus propias tablas, cuándo aplanarlas en una tabla ancha y cuándo anidarlas |
| [0013](lessons/0013-slowly-changing-dimensions.md) | Slowly changing dimensions | Cómo una dimensión conserva o descarta su historial cuando cambia un atributo, y qué le hace cada elección a los informes antiguos |
| [0014](lessons/0014-elt-and-batch-loading.md) | ELT y carga por lotes | Por qué los almacenes cargan primero los datos en bruto y los transforman en su sitio, y cómo el número y el tamaño de los archivos deciden la velocidad de carga |
| [0015](lessons/0015-micro-batch-streaming-and-idempotent-merges.md) | Micro-batch, streaming y merges idempotentes | Cómo ingerir datos de forma continua y lograr que volver a ejecutar cualquier carga deje la tabla exactamente como la dejaría una sola ejecución |
| [0016](lessons/0016-how-a-warehouse-bills.md) | Cómo factura un almacén | Qué cobra cada plataforma con precios on-demand y con precios por capacidad, y qué carga de trabajo favorece cada modelo |
| [0017](lessons/0017-reading-and-cutting-a-querys-cost.md) | Leer y reducir el costo de una consulta | Cómo averiguar lo que costará una consulta antes de ejecutarla, y los cambios que reducen ese costo sin cambiar su respuesta |
| [0018](lessons/0018-warehouse-postgres-or-lakehouse.md) | Almacén, Postgres o lakehouse | Cómo decidir dónde corresponde una carga de trabajo analítica, y cuándo la respuesta habitual de un almacén es la equivocada |
| [0019](lessons/0019-reviewing-a-warehouse-schema-and-its-bill.md) | Revisar el esquema de un almacén y su factura | Cómo revisar el diseño de almacén de otra persona y nombrar lo que cuesta cada elección, en bytes y en dinero |
| [0020](lessons/0020-changing-a-model-others-query.md) | Cambiar un modelo que otros consultan | Cómo cambiar una tabla de la que dependen dashboards y pipelines sin romperlos, y cómo zanjar una afirmación disputada a partir de la documentación |

## Referencia

- [Glosario](GLOSSARY.md): términos canónicos de este tema
- [Recursos](RESOURCES.md): fuentes de confianza, cada una anotada con lo que cubre
- [Almacenamiento y ejecución columnar](reference/columnar-storage-and-execution.md): disposición por filas frente a disposición por columnas, las codificaciones y lo que se salta un motor columnar
- [Comparación de plataformas](reference/platforms-compared.md): cómo nombran y facturan BigQuery, Snowflake y Redshift las mismas ideas de almacenamiento y cómputo
- [Diseño físico](reference/physical-design.md): particionado, clustering, sort keys y distribución en cada plataforma, y los hábitos de almacén por filas que hay que abandonar
- [Modelado dimensional](reference/dimensional-modelling.md): los cuatro pasos de diseño, las formas de esquema y los tipos de slowly changing dimension
- [Carga](reference/loading.md): métodos de carga por plataforma, tamaño de los archivos y los patrones que hacen que una carga pueda volver a ejecutarse sin riesgo
- [Modelo de costos](reference/cost-model.md): qué cobra cada modelo de precios, cómo leer el costo de una consulta y los controles que limitan una factura
- [Revisión de esquema y factura](reference/schema-and-bill-review.md): una lista de verificación para revisar el diseño de un almacén y su factura, y la decisión de ubicación

## Cómo funciona

Cada lección es corta y autocontenida. Las claves de respuesta están plegadas: primero recuerda, luego ábrelas. Las prácticas en el mundo real importan más que la lectura, y espaciarlas es el punto. Todo lo que siga sin estar claro al final de una lección merece rastrearse hasta su fuente primaria antes de seguir.
