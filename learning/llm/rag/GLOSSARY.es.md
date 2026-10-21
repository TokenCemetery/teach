---
title: "Glosario"
description: "Términos canónicos de RAG"
type: glossary
---

# Glosario de RAG

Términos canónicos de un pipeline de recuperación: en qué divide los documentos y cómo decide qué entregar al paso de generación.

## Términos

**Recuperación agéntica**:
Un sistema que decide, por consulta y por paso, si hace falta recuperar siquiera, si lo que volvió es suficiente y si debe recuperar de nuevo a partir de algo recién derivado, en lugar de seguir una única pasada fija de recuperar y luego generar.
_Evitar_: recuperación multi-hop (un caso relacionado pero más estrecho: la recuperación multi-hop cubre específicamente que una subpregunta posterior de una consulta dependa de la respuesta de una anterior, mientras que la recuperación agéntica cubre también si hay que recuperar o no)

**Chunk**:
Un fragmento de un documento, producido al dividirlo antes de generar embeddings e indexar, con un tamaño que mantiene su embedding centrado en un tema en lugar de ser el promedio de varios.
_Evitar_: segmento, pasaje (úsalo solo al citar una fuente que lo emplea)

**Chunking**:
El proceso de dividir un documento en chunks, por un tamaño fijo, por la propia estructura del documento o detectando dónde cambia su tema.
_Evitar_: división (demasiado genérico; úsalo solo en prosa que describe el acto mecánico, no como nombre del proceso)

**Utilización de la ventana de contexto**:
La proporción entre los chunks realmente citados en una respuesta generada y los chunks recuperados y colocados en el prompt. Una utilización baja significa que se gastan tokens en contexto que el modelo nunca usó; una utilización constantemente alta, en cambio, puede avisar de que material crítico se está truncando fuera de la ventana de contexto antes de que pueda citarse.
_Evitar_: asumir que una utilización más alta siempre es mejor; en el extremo alto es una señal de alarma de truncamiento, no una ganancia pura de eficiencia

**Cascada de errores**:
Un error en un paso temprano de la ingesta (identificar mal un encabezado, fusionar columnas en el orden equivocado) que se propaga a todos los pasos posteriores que operan sobre la estructura ya corrompida que recibieron, y corrompe los chunks de una sección entera en lugar de quedar contenido en el único elemento que el error tocó directamente.
_Evitar_: un error de análisis aislado (subestima el efecto; el sentido de llamarlo cascada es que un error temprano se acumula en lugar de quedarse local)

**HyDE (Hypothetical Document Embeddings)**:
Generar el embedding de la respuesta hipotética que produce un modelo de lenguaje para una consulta, en lugar del de la propia consulta, y luego buscar en el corpus por similitud con ese embedding. Tolera detalles factualmente erróneos en el documento hipotético, ya que el paso de embedding del codificador los filtra y conserva la similitud temática genuina.
_Evitar_: reescritura de consultas (otra corrección del lado de la consulta: la reescritura reformula la propia consulta, mientras que HyDE genera el embedding de una respuesta generada en lugar de la consulta)

**Indexación incremental**:
Añadir vectores nuevos a un índice ya construido sin reconstruirlo desde cero. Está bien soportada por HNSW, que no tiene paso de entrenamiento; es más débil en IVFFlat, cuyos centroides de clúster quedan fijados al construir el índice y nunca se recalculan, de modo que el contenido nuevo que difiere de los datos de entrenamiento originales puede quedar mal agrupado.
_Evitar_: reindexación (una reconstrucción completa desde cero, necesaria específicamente cuando cambia el modelo de embeddings; no es la misma operación que añadir vectores nuevos de forma incremental a un índice que no ha cambiado)

**Ingesta**:
Convertir un documento fuente en bruto (un PDF, una página HTML o un archivo de ofimática) en el texto limpio y estructurado sobre el que realmente opera el chunking. Una etapa genuina del pipeline anterior al chunking, con sus propios modos de fallo, no un detalle de preprocesamiento que quede por debajo de la atención del pipeline.
_Evitar_: tratar el chunking como la primera etapa del pipeline (el chunking asume que la ingesta ya produjo texto limpio; la ingesta es lo que realmente lo produce)

**Filtrado por metadatos**:
Restringir la recuperación a los chunks que cumplen un predicado sobre atributos estructurados (tipo de documento, fecha, propietario, etiqueta de permisos) además de la similitud del vecino más cercano, en lugar de buscar en todo el corpus solo por similitud.
_Evitar_: filtrado de permisos (un caso específico y de mayor riesgo del filtrado por metadatos, en el que un fallo es un incidente de seguridad y no una regresión de calidad, y que requiere específicamente prefiltrado)

**Recuperación multi-hop**:
Recuperar en un bucle donde una consulta posterior depende de un dato derivado de una recuperación anterior, en lugar de un conjunto fijo de subpreguntas decidido de antemano. Hace falta cuando una subpregunta ni siquiera puede formularse hasta conocer la respuesta de una subpregunta previa, algo que la descomposición de consultas por sí sola no puede manejar.
_Evitar_: descomposición de consultas (divide subpreguntas ya visibles en el texto de la pregunta original; la recuperación multi-hop maneja subpreguntas que no existen hasta que la respuesta de un salto previo las produce)

**Posfiltrado**:
Ejecutar primero una búsqueda ANN y descartar después los resultados que no cumplen un predicado. Es rápido, pero un predicado selectivo puede descartar la mayor parte de lo que encontró el escaneo acotado de candidatos de un índice aproximado y hundir el recall; en un filtro de permisos en concreto, significa además que el contenido no autorizado existió brevemente en el pipeline antes de ser descartado.
_Evitar_: prefiltrado (restringe el conjunto de candidatos antes de que corra la búsqueda ANN, preserva el recall respecto del conjunto filtrado y nunca deja que el contenido no permitido entre en el pipeline)

**Prefiltrado**:
Restringir el conjunto de candidatos a los chunks que cumplen un predicado antes de que corra la búsqueda ANN, lo que preserva el recall respecto de ese conjunto filtrado sin importar lo selectivo que sea el predicado. Es obligatorio para el control de acceso en concreto, ya que el contenido no autorizado nunca entra en el pipeline.
_Evitar_: posfiltrado (busca primero en todo el índice y descarta después; tanto el recall como, en los filtros de permisos, la propia garantía de seguridad pueden verse afectados)

**Descomposición de consultas**:
Dividir una pregunta compuesta en sus subpreguntas separadas y recuperar para cada una de forma independiente, en lugar de generar un único vector de embedding para toda la pregunta compuesta, que queda cerca de ninguno de los pasajes que responderían bien una sola de sus partes.
_Evitar_: expansión de consulta múltiple (una técnica distinta: la expansión genera varias reformulaciones completas de una misma pregunta, mientras que la descomposición divide una pregunta en subpreguntas separadas y más acotadas)

**Puntuación sin referencia**:
Una puntuación de relevancia evaluada por un LLM, calculada por cada chunk recuperado sin necesitar una respuesta correcta conocida y agregada en una ventana de tiempo como tasa de aciertos o relevancia promedio. Es lo que usa la monitorización en producción en lugar de recall@k o MRR, que requieren un conjunto de consultas etiquetado o sintético que la mayor parte del tráfico real no tiene.
_Evitar_: recall@k, MRR (métricas offline que requieren resultados correctos conocidos; la puntuación sin referencia es específicamente el sustituto de producción cuando no existen esas etiquetas)

**Reindexación**:
Reconstruir un índice vectorial desde cero, necesario cuando cambia el propio modelo de embeddings, ya que cada vector existente se produjo en el espacio vectorial del modelo anterior y no comparte distancias comparables con los embeddings de un modelo nuevo. Una operación distinta de la indexación incremental y del mantenimiento periódico que exigen los borrados y las actualizaciones.
_Evitar_: indexación incremental (añadir vectores nuevos a un índice que no ha cambiado; la reindexación significa específicamente reconstruirlo todo porque cambió el modelo que produce los vectores)
