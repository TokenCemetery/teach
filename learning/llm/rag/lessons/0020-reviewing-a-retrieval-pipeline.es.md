---
title: "20. Revisar un pipeline de recuperación"
description: "Revisar el diseño del pipeline de recuperación de otra persona y nombrar con precisión lo que hará mal antes de enviarlo a producción, y decir cuándo RAG en sí (no una etapa del pipeline) es la respuesta equivocada al problema planteado"
type: lesson
---

# Lección 20. Revisar un pipeline de recuperación

**Vínculo con la misión:** Una habilidad senior es revisar el trabajo de otra persona, nombrar lo que cuesta una decisión en lugar de decir que se siente mal y saber cuándo todo el enfoque es el equivocado para el problema (no solo qué etapa está rota).
**Fuente principal:** [Paper: "Lost in the Middle: How Language Models Use Long Contexts", Liu et al., 2023](https://arxiv.org/abs/2307.03172)
**Requisitos previos:** [Lección 1](0001-chunking.md), [Lección 2](0002-embedding-models-and-similarity.md), [Lección 4](0004-ann-indexes.md), [Lección 6](0006-bm25-and-lexical-search.md), [Lección 9](0009-when-reranking-earns-its-cost.md), [Lección 11](0011-diagnosing-the-pipeline.md), [Lección 15](0015-metadata-filtering-and-access-control.md), [Lección 17](0017-freshness.md)

## Calentamiento

1. ▢ ¿Qué mide una métrica de recuperación, y por qué la necesitan los pesos híbridos y el reranking?

<details markdown="1"><summary>Comprobación</summary>

Una métrica de recuperación como Recall@k o MRR mide si se recuperó lo correcto, antes de que empiece siquiera el paso de generación. Tanto los pesos híbridos como el ajuste del reranking dependen de saber si un cambio mejoró realmente lo que se recuperó, así que necesitan una medición contra la cual decidir y no hacerlo a ojo.

</details>

2. ▢ ¿Por qué el posfiltrado falla en el control de acceso en concreto, de una forma en que no falla en otros filtros de metadatos?

<details markdown="1"><summary>Comprobación</summary>

El posfiltrado ejecuta primero la búsqueda ANN sobre todo el índice y descarta después los resultados. En los filtros de metadatos ordinarios, esto es solo una regresión de recall: el filtro descarta algunos resultados. En el control de acceso, el contenido no autorizado existe brevemente en el pipeline antes de ser descartado, lo que es un fallo de seguridad, no solo de calidad. El prefiltrado restringe el conjunto de candidatos antes de que corra la búsqueda, así que el contenido no permitido nunca entra en el pipeline.

</details>

3. ▢ Nombra una forma en que un corpus puede quedar obsoleto y una forma en que la frescura se maneja de manera distinta en ese caso frente a otro.

<details markdown="1"><summary>Comprobación</summary>

Un corpus queda obsoleto al añadir documentos, borrarlos o cambiar el modelo de embeddings. Añadir y borrar pueden usar indexación incremental, y HNSW maneja ambos de forma relativamente buena. Cambiar el modelo requiere una reindexación completa desde cero: los vectores antiguos no comparten distancias comparables con los nuevos, así que hay que reconstruirlos por completo.

</details>

## Qué debes saber

### La lista de revisión: qué buscar realmente en un diseño

Cuando alguien propone un pipeline de recuperación o te muestra uno ya construido, recorre estas preguntas en orden. Cada una corresponde a una etapa de este arco. Para cada una, busca: (1) si la decisión se tomó de forma deliberada para este corpus y este caso de uso, (2) si se midió contra una métrica de recuperación o si se eligió por defecto o a ojo.

**Etapa 1: Estrategia de chunking.** ¿El diseño eligió una estrategia de chunking porque encaja con la estructura real del corpus (tamaño fijo para prosa, recursivo para markdown anidado, semántico para papers con cambios de tema o consciente de la estructura del documento para PDF cuyo diseño importa)? ¿O simplemente se copió un tamaño de chunk por defecto (512, 1024 tokens)? Un corpus de PDF médicos necesita un chunking distinto del de un repositorio lleno de documentación de API.

**Etapas 2 y 3: Modelo de embeddings y métrica de similitud.** ¿Se eligieron el modelo de embeddings y la métrica (coseno, L2, producto punto) para este corpus, probados con corpus similares o al menos con ejemplos de este? ¿O se escogieron por defecto según lo que recomendaba la documentación de la base de datos vectorial? Un embedding entrenado con noticias podría ordenar mal papers de finanzas.

**Etapas 4, 5 y 6: Búsqueda híbrida, reranking y evaluación de la recuperación.** ¿Tiene el diseño una métrica de recuperación real contra la que se ajustó (Recall@k, MRR, nDCG)? ¿O se añadieron los pesos híbridos y el reranking a ojo, sin medir si mejoraron realmente lo que se recupera? Una etapa de reranking que cuesta latencia necesita pruebas de que se ganó ese costo en el caso de uso real.

**Etapa 9: Filtrado consciente de permisos.** Si el corpus tiene control de acceso, ¿usa el diseño prefiltrado para restringir el conjunto de candidatos antes de la búsqueda ANN y mantener el contenido no autorizado fuera del pipeline por completo? ¿O recupera de todo el índice y filtra después, con el riesgo tanto de una regresión de recall como de un momento en que el contenido no autorizado existe en el pipeline?

**Etapas 10 y 11: Ingesta y frescura.** ¿Tuvo en cuenta el diseño cómo se extraen y se analizan realmente los documentos fuente antes del chunking? ¿Tiene un plan para mantener el índice al día a medida que se añaden, borran o modifican documentos, o asume datos estáticos? Las actualizaciones incrementales encajan bien con HNSW, pero cambiar un modelo de embeddings siempre requiere una reindexación completa.

**Etapa 6 otra vez: Distinguir un fallo de recuperación de un fallo de generación.** Cuando algo sale mal, ¿tiene el diseño una forma de saber si el modelo recibió mal contexto o usó mal un buen contexto? Un diseño que por defecto culpa a la etapa de recuperación ante cualquier respuesta errónea carece de un diagnóstico crucial.

### La cuestión disputada: ¿vuelve obsoleta la recuperación el contexto largo?

Este es un desacuerdo vigente. Una postura dice que los modelos de contexto largo eliminan ahora la necesidad de recuperación: ¿para qué construir un pipeline de recuperación cuando los modelos ya pueden contener todo el corpus en el prompt? ¿Por qué pagar infraestructura de recuperación cuando se pueden enviar 100K tokens en cada petición?

La otra postura dice que la recuperación sigue ganando para la mayoría de los corpus y casos de uso reales, pese a los avances del contexto largo. El paper "Lost in the Middle" muestra que los modelos usan mucho peor la información colocada en medio de un contexto largo que la del principio o el final, incluso dentro de la ventana de contexto. Reenviar un corpus entero en cada petición concentra todos los tokens que no usa en el medio de la atención, exactamente donde los modelos usan mal la información. La recuperación, en cambio, envía solo las partes relevantes y las mantiene cerca del inicio de la ventana de contexto, donde los modelos les prestan buena atención.

Pero eso es el marco de decisión, no la decisión en sí. Para zanjar si la recuperación es la respuesta correcta para un problema concreto, hazte tres preguntas:

**1. ¿Cuál es el tamaño del corpus y su frecuencia de actualización?**

Un corpus pequeño, estático y que cabe en un único prompt podría funcionar legítimamente mejor si se envía entero: el manual completo de una empresa (50K tokens, cambia cada trimestre) podría ser más barato y más simple de incluir en cada petición que de mantener con un índice de recuperación. Un corpus grande (millones de documentos), que cambia constantemente (ingesta diaria) o que tiene control de acceso (usuarios distintos ven subconjuntos distintos) funciona al revés: el costo de reenviarlo en cada petición es prohibitivo, o el control de acceso es imposible de aplicar después de la recuperación (la lección de la etapa 9).

**2. ¿Qué necesita realmente el patrón de consultas?**

Una consulta que necesita síntesis de todo el corpus (cuál es el consenso sobre X en todos nuestros papers) podría beneficiarse de ver más contexto. Una consulta que necesita datos precisos (cuál es nuestra política de reembolso para las suscripciones anuales) funciona mejor con una recuperación que encuentre el documento exacto de la política y lo coloque arriba, donde el modelo le presta buena atención. La recuperación permite enviar menos contexto con mayor fidelidad.

**3. ¿A cuánto asciende realmente el cálculo de costos?**

El paper "Lost in the Middle" muestra el compromiso: cuando la información está en medio de un prompt de 100K tokens, los modelos la pierden. Para sortearlo, o bien hay que ordenar con cuidado el contexto (lo que hace la recuperación al colocar los chunks más relevantes arriba) o bien enviar menos. Una recuperación que envía 2K tokens de los chunks más relevantes es más barata y mejor que 100K tokens en los que la mitad está en la zona muerta. Esto asume que tu recuperación encuentra realmente los chunks relevantes; si el pipeline de recuperación está roto, enviarlo todo es al menos un recurso de respaldo. Pero cuando la recuperación funciona, gana en costo, latencia y calidad.

## Práctica

1. ▢ Un equipo construyó un pipeline que divide todos los documentos en chunks con un tamaño fijo de 1024 tokens. Revisas el diseño y no ves justificación para esta decisión. ¿Qué pregunta deberías hacer para entender si fue deliberada o tomada por defecto?

<details markdown="1"><summary>Comprobación</summary>

¿Cuál es el corpus? ¿Son transcripciones de atención al cliente, papers académicos, documentación de producto u otra cosa? Un chunk de 1024 tokens funciona para unos tipos de documento y falla para otros. Si eligieron este tamaño porque era fácil de implementar o porque el código de ejemplo de la base de datos vectorial lo usaba, es una señal de alarma. Si probaron distintos tamaños de chunk contra una métrica de recuperación reservada, sobre muestras reales del corpus, y ganó 1024, es una decisión deliberada que se puede rastrear.

</details>

2. ▢ El diseño usa el modelo de embeddings de OpenAI sin probarlo en el corpus real. ¿Qué podría salir mal?

<details markdown="1"><summary>Comprobación</summary>

El modelo de embeddings se entrenó con una distribución amplia de texto de internet. Si el corpus es muy especializado (documentos legales, informes financieros, literatura médica) o está en un idioma con menos datos de preentrenamiento, el modelo podría ordenar mal la similitud semántica. La prueba correcta: generar el embedding de una muestra de documentos de este corpus, identificar a mano qué pares son realmente similares y comprobar si el ranking de distancias de OpenAI coincide. Si no, considera embeddings específicos del dominio o modelos entrenados con contenido similar.

</details>

3. ▢ Un diseño usa búsqueda híbrida (BM25 + vectorial) pero el equipo no sabe cómo ponderarlas. Preguntan: "¿hacemos 50-50 o 70-30 a favor de la vectorial?". ¿Qué información les falta?

<details markdown="1"><summary>Comprobación</summary>

Les falta una métrica de recuperación. Los pesos deben ajustarse contra una medición real sobre un conjunto de consultas reservado, midiendo qué mezcla produce el mejor Recall@k o MRR en la tarea. Adivinar entre 50-50 y 70-30 es una moneda al aire, y la mezcla equivocada puede perjudicar más que cualquiera de los dos enfoques por separado. La pregunta real es: para tu corpus y tus consultas, ¿qué mezcla recupera realmente lo correcto? Mídelo.

</details>

4. ▢ El corpus contiene artículos de investigación médica que se actualizan constantemente (se añaden artículos nuevos a diario, y los antiguos a veces se retractan o se corrigen). Una propuesta sugiere meter todos los documentos en el prompt de un modelo de contexto largo en cada petición. ¿Cuáles son dos razones por las que esto podría no funcionar?

<details markdown="1"><summary>Pista</summary>

Considera cómo es el corpus (tamaño, ritmo de cambio) y qué hace el modelo con la información colocada en medio de un contexto largo.

</details>

<details markdown="1"><summary>Comprobación</summary>

Dos razones: (1) El corpus es grande y cambia constantemente, así que reenviar todos los documentos en cada petición es caro, y actualizar qué documentos están en el prompt es una carga de mantenimiento. La recuperación permite enviar solo lo relevante y se actualiza automáticamente cuando se refresca el índice. (2) Los modelos usan mal la información colocada en medio de un contexto largo ("Lost in the Middle"). Enviar 500 papers con solo unos pocos relevantes para la consulta entierra los relevantes en medio de la atención, donde los modelos prestan poca atención. Una recuperación que envía los 5 papers más relevantes, ordenados por relevancia al inicio del contexto, es a la vez más barata y más precisa.

</details>

5. ▢ Un equipo que considera RAG pregunta: "Nuestro corpus son 10MB de archivos markdown, actualizados una vez al año. ¿Por qué no incluirlo todo en el prompt?". ¿Qué afirmación de las siguientes responde correctamente a esta pregunta?

    - a) Los modelos de contexto largo vuelven completamente obsoleto a RAG; este equipo nunca debería usar recuperación por ninguna razón
    - b) El corpus es pequeño, estático y cabe en un prompt; para este caso concreto, incluirlo todo podría de hecho ser más simple y funcionar bien
    - c) RAG siempre es mejor que el contexto largo, sin importar el tamaño del corpus ni la frecuencia de cambio
    - d) El paper "Lost in the Middle" demuestra que nunca debería ponerse nada en un prompt

<details markdown="1"><summary>Comprobación</summary>

**b)** Esa es la postura calibrada sobre esta cuestión. El tamaño del corpus (10MB, probablemente por debajo de la ventana de contexto), la frecuencia de cambio (anual) y las necesidades de control de acceso (no se mencionan) apuntan todos a que el contexto largo funciona bien, posiblemente de forma más simple. RAG tiene costos de infraestructura reales. Un corpus pequeño y estático no justifica esos costos. (a) es errónea: los modelos pueden usarse legítimamente sin recuperación cuando el corpus es diminuto y estático. (c) es errónea: la decisión depende de las características del corpus y del patrón de consultas, no de una regla absoluta. (d) es errónea: el paper muestra que los modelos usan mal el contexto del medio, no que cualquier cosa en un prompt sea inutilizable.

</details>

## Prácticas en el mundo real

- [ ] Encuentra un pipeline de recuperación que hayas construido o revisado. Recorre sobre él las cinco preguntas de la lista de revisión. Para cada etapa, escribe una oración: ¿esta decisión se midió contra una métrica de recuperación o se eligió por defecto? Luego pregúntate: ¿qué cambiarías si tuvieras que mejorarlo?
- [ ] Elige un corpus (el tuyo, uno público que conozcas o uno sintético). Resuelve el marco de tres preguntas: tamaño del corpus y frecuencia de actualización, patrón de consultas, costo real de reenviarlo entero frente a la recuperación. Anota la respuesta: ¿qué encajaría mejor, la recuperación o el contexto largo, y por qué?
- [ ] Mañana: lee la sección de resultados del paper "Lost in the Middle" y anota la diferencia concreta de rendimiento entre la información al principio, en medio y al final de un contexto de 4K tokens. Luego estima: si tu patrón de consultas necesitara síntesis de 100 documentos, ¿cuántos cabrían en las zonas de "alta calidad" del principio y del final?

## Para profundizar

- [Paper: "Lost in the Middle: How Language Models Use Long Contexts", Liu et al., 2023](https://arxiv.org/abs/2307.03172)
- [Lección 24: Contexto largo en el momento del serving](../../inference/lessons/0024-long-context-at-serve-time.md): qué hacen realmente las técnicas de contexto largo con el costo de serving, en lugar del costo de recuperación
- [Recursos](../RESOURCES.md)

---

¿No termina de quedar claro? Vuelve a leer la fuente principal de arriba, ya que esta lección la comprime y en la compresión es donde se escapa la comprensión. Consulta el [glosario](../GLOSSARY.md) por si algún término te resultó resbaladizo.

Si lo poco claro es la propia lección y no el material, eso es un defecto: [abre un issue](https://github.com/TokenCemetery/teach/issues).
