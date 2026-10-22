---
title: Prompting
description: "Escribe, versiona y entrega prompts para una funcionalidad con LLM, demuestra que un cambio de prompt ayudó y revisa el prompt de producción de otra persona"
type: topic
---

# Aprendizaje: Prompting

Escribe los prompts que hay detrás de una funcionalidad con LLM para que hagan lo que se pretendía, vivan en el código como plantillas versionadas y cambien solo cuando un conjunto de regresión diga que el cambio ayudó. Termina siendo capaz de revisar el prompt de producción de otra persona y de nombrar lo que cuesta cada decisión que contiene, en lugar de decir que se lee raro.

**Última lección:** [24. Cuando el consejo habitual es erróneo](lessons/0024-when-the-usual-advice-is-wrong.md)

## Cómo se ve el éxito

- Escribir un prompt cuyos roles, instrucciones y estructura pueda leer un colega y que el modelo siga, y decir qué recibe realmente el modelo a partir de él.
- Elegir, ordenar y auditar ejemplos few-shot, nombrando el sesgo que arriesga cada decisión.
- Decidir cuándo pedir razonamiento, hacer prompting a un modelo de razonamiento de forma distinta a un modelo estándar y explicar por qué el razonamiento escrito no es una explicación de la respuesta.
- Obtener salida estructurada que un programa pueda analizar y distribuir un contexto largo para que el modelo use lo que hay en él.
- Mantener los prompts en un código base como plantillas versionadas, ordenadas para que el prefijo estable pueda almacenarse en caché.
- Demostrar con un conjunto de regresión y una comparación pareada si un cambio de prompt ayudó, en lugar de juzgarlo por un puñado de salidas.
- Diseñar un prompt que maneje entrada no confiable y decir de qué riesgos no puede defenderse el prompt por sí solo.
- Elegir entre un mejor prompt, la recuperación (retrieval) y el fine-tuning para un fallo dado, y revisar el prompt de producción de otra persona nombrando lo que cuesta cada decisión.

## Restricciones

- Centrado en la app, utilizable desde una ventana de chat: las etapas 1 a 6 funcionan en cualquier interfaz de chat, las etapas 7 a 10 asumen que el prompt vive en el código.
- Sin proveedor ni modelo fijos. Los ejemplos son neutrales respecto al proveedor; cuando una técnica es un comportamiento documentado de un solo proveedor, la lección lo dice.
- No se asume ningún conocimiento previo de prompting. Basta con saber qué es un LLM, al nivel de "predice el siguiente token".

## Fuera de alcance

- La construcción de prompts sobre contexto recuperado y el presupuesto de la ventana de contexto: consulta [`llm/rag`](../../llm/rag/) y su hoja de referencia [Generación a partir de la recuperación](../../llm/rag/reference/generation-from-retrieval.md). Este track enseña prompting en general y enlaza allí para el caso de la recuperación.
- Las descripciones de herramientas como superficie del prompt, la inyección de prompt en un agente con herramientas y el prompt caching bajo concurrencia: consulta [`llm/agents`](../../llm/agents/). Este track cubre el prompting sin herramientas y enlaza esas lecciones en lugar de repetirlas.
- El diseño de prompts de juez y la metodología de evals: consulta [`llm/evals`](../../llm/evals/) y su hoja de referencia [Go/No-Go](../../llm/evals/reference/go-no-go.md). Este track usa un eval para medir un cambio de prompt y no enseña a construir uno.
- La decodificación restringida, el lado de servicio de la salida estructurada: consulta [`llm/inference`](../../llm/inference/). Este track pide estructura desde el lado del prompt.
- Cómo se entrenan en un modelo el seguimiento de instrucciones y el razonamiento: consulta [`llm/post-training`](../../llm/post-training/). Este track cubre cómo usarlos desde fuera.

## El arco

Diez etapas, desde lo que es un prompt para el modelo hasta el criterio para revisar el de otra persona. Una etapa abarca varias lecciones y los límites son difusos; lo que da una etapa por terminada es la capacidad, no el número de lecciones.

| Etapa | Lecciones | Cubre | Terminada cuando |
|---|---|---|---|
| 1. Qué es un prompt para el modelo | 0001 a 0002 | Tokens, plantillas de chat, roles, el system prompt y la jerarquía de instrucciones | Puedes decir qué secuencia recibe el modelo para una conversación dada y dónde va cada instrucción |
| 2. Instrucciones y estructura | 0003 a 0005 | Instrucciones claras, delimitadores y etiquetas, sensibilidad al formato | Puedes escribir un prompt que una persona nueva podría seguir y que mantiene las instrucciones separadas de los datos |
| 3. Ejemplos few-shot | 0006 a 0007 | Qué enseñan las demostraciones, sesgos de etiqueta mayoritaria, de recencia y de orden | Puedes elegir y ordenar ejemplos y nombrar el sesgo que arriesga cada decisión |
| 4. Razonamiento | 0008 a 0010 | Chain-of-thought, autoconsistencia, fidelidad, prompting de modelos de razonamiento | Puedes decidir si pedir razonamiento y cómo, para un modelo y una tarea dados |
| 5. Salida estructurada | 0011 a 0012 | Pedir un esquema, validarlo, restricciones de formato frente a calidad del razonamiento | Obtienes una salida que un programa analiza, sin pagarlo con calidad de respuesta |
| 6. Contexto largo | 0013 a 0014 | Efectos de posición, distribución de documentos, extracción de citas | Puedes distribuir un contexto largo para que el modelo use lo que hay en medio |
| 7. Prompts en un código base | 0015 a 0017 | Plantillas, versionado frente a un snapshot del modelo, distribución para el prompt caching | Mantienes los prompts como plantillas versionadas cuyo prefijo estable es almacenable en caché |
| 8. Medir un cambio de prompt | 0018 a 0019 | Conjuntos de regresión a partir de fallos reales, comparación pareada frente al ruido | Puedes demostrar con un número si el prompt B supera al prompt A |
| 9. Seguridad de prompts | 0020 a 0021 | Inyección de prompt directa e indirecta, qué puede y qué no puede defender el prompt | Puedes diseñar un prompt para entrada no confiable y nombrar los riesgos que deja al sistema |
| 10. Criterio | 0022 a 0024 | Prompt frente a RAG frente a fine-tuning, revisar un prompt de producción, cambiar un prompt del que otros dependen, cuándo el consejo habitual es erróneo | Se confía en ti para tomar la decisión sobre un prompt y explicársela a otra persona |

## Lecciones

Recórrelas en orden.

| # | Lección | Enseña |
|---|---|---|
| [0001](lessons/0001-what-the-model-sees.md) | Lo que ve el modelo | Un prompt llega al modelo como una única secuencia de tokens construida por una plantilla de chat, así que los roles son formato con el que el modelo se entrenó, no canales separados |
| [0002](lessons/0002-system-prompts-and-roles.md) | System prompts y roles | Qué va en el system prompt y qué en el turno del usuario, y por qué el modelo clasifica las instrucciones según dónde están |
| [0003](lessons/0003-clear-instructions.md) | Instrucciones claras | Escribir una instrucción que una persona nueva y capaz pudiera seguir: contexto, la tarea, las restricciones y cómo se ve algo terminado |
| [0004](lessons/0004-structure-and-delimiters.md) | Estructura y delimitadores | Separar instrucciones y datos con etiquetas y secciones para que el modelo distinga cuál es cuál |
| [0005](lessons/0005-format-sensitivity.md) | Sensibilidad al formato | Por qué un cambio de formato sin significado puede mover la precisión, y por qué eso convierte cada edición de un prompt en una afirmación que hay que probar |
| [0006](lessons/0006-what-examples-teach.md) | Qué enseñan los ejemplos few-shot | Las demostraciones enseñan sobre todo el formato, el espacio de etiquetas y la distribución de entrada, lo que cambia cómo las eliges |
| [0007](lessons/0007-few-shot-biases.md) | Sesgos del few-shot | Sesgos de etiqueta mayoritaria, de recencia y de orden en los prompts few-shot, y cómo elegir y ordenar ejemplos frente a ellos |
| [0008](lessons/0008-chain-of-thought.md) | Chain-of-thought | Cuándo pedir razonamiento intermedio mejora una respuesta y cuándo solo añade tokens |
| [0009](lessons/0009-self-consistency-and-faithfulness.md) | Autoconsistencia y fidelidad | Muestrear varias rutas de razonamiento para votar una respuesta, y por qué el razonamiento escrito no es una explicación fiel |
| [0010](lessons/0010-prompting-reasoning-models.md) | Prompting de modelos de razonamiento | Por qué un modelo que ya piensa necesita objetivos y restricciones en lugar de pasos escritos de antemano |
| [0011](lessons/0011-structured-output-from-the-prompt.md) | Salida estructurada desde el prompt | Pedir una salida que un programa pueda analizar y luego validarla, porque pedir no es una garantía |
| [0012](lessons/0012-format-constraints-and-reasoning.md) | Restricciones de formato y razonamiento | Un formato de salida estricto puede costar calidad de razonamiento, y cómo ordenar los campos para que la respuesta llegue después del razonamiento |
| [0013](lessons/0013-position-in-long-context.md) | Posición en el contexto largo | Los modelos usan mejor la información de los extremos de un contexto largo que la del medio, lo que decide dónde van los documentos y la pregunta |
| [0014](lessons/0014-working-with-long-documents.md) | Trabajar con documentos largos | Etiquetar los documentos con sus metadatos y hacer que el modelo extraiga citas antes de responder |
| [0015](lessons/0015-prompt-templates.md) | Plantillas de prompt | Dividir un prompt en una plantilla fija y las variables que se rellenan en cada petición, y evitar que la entrada no confiable rompa la estructura |
| [0016](lessons/0016-versioning-prompts.md) | Versionado de prompts | Tratar un prompt como código: fijado a un snapshot del modelo, versionado, revisado y revertido como cualquier otro cambio |
| [0017](lessons/0017-prompt-caching-and-layout.md) | Prompt caching y distribución | Ordenar un prompt con las partes estables primero para que el proveedor pueda almacenar el prefijo en caché |
| [0018](lessons/0018-a-regression-set-for-a-prompt.md) | Un conjunto de regresión para un prompt | Construir el pequeño conjunto de casos que un cambio de prompt no debe romper, empezando por fallos reales |
| [0019](lessons/0019-comparing-two-prompts.md) | Comparar dos prompts | Decidir si el prompt B supera al prompt A con una comparación pareada que separa el cambio del ruido entre ejecuciones |
| [0020](lessons/0020-prompt-injection.md) | Inyección de prompt | Cómo el texto de la entrada puede anular las instrucciones del autor, de forma directa u oculto en contenido que el modelo lee |
| [0021](lessons/0021-what-a-prompt-cannot-defend.md) | Lo que un prompt no puede defender | Qué defensas pertenecen al prompt, y por qué las reales residen en lo que el sistema permite hacer al modelo |
| [0022](lessons/0022-prompt-rag-or-fine-tune.md) | Prompt, RAG o fine-tuning | Elegir entre un mejor prompt, la recuperación y el fine-tuning según cuál sea realmente el fallo |
| [0023](lessons/0023-reviewing-a-production-prompt.md) | Revisar un prompt de producción | Revisar el prompt de otra persona nombrando lo que cuesta cada decisión, y cambiar un prompt del que otros dependen sin romperlos |
| [0024](lessons/0024-when-the-usual-advice-is-wrong.md) | Cuando el consejo habitual es erróneo | Reconocer cuándo el consejo estándar de prompting falla para un modelo o una tarea dados, y zanjar la disputa desde la fuente primaria |

## Referencia

- [Glosario](GLOSSARY.md): términos canónicos de este tema
- [Recursos](RESOURCES.md): fuentes de confianza, cada una anotada con lo que cubre
- [Anatomía de un prompt](reference/prompt-anatomy.md): roles, qué va dónde y la lista de comprobación de estructura de las etapas 1 y 2
- [Few-Shot y razonamiento](reference/few-shot-and-reasoning.md): elegir y ordenar ejemplos, y cuándo pedir razonamiento, de las etapas 3 y 4
- [Salida estructurada y contexto largo](reference/structured-output-and-long-context.md): obtener salida analizable y distribuir entradas largas, de las etapas 5 y 6
- [Prompts en producción](reference/prompts-in-production.md): plantillas, versionado, distribución apta para caché y el ciclo de medición, de las etapas 7 y 8
- [Seguridad de prompts](reference/prompt-security.md): rutas de inyección y qué defensa va dónde, de la etapa 9
- [Lista de revisión de prompts](reference/prompt-review-checklist.md): las preguntas que hacer sobre el prompt de otra persona, y prompt frente a RAG frente a fine-tuning, de la etapa 10

## Cómo funciona

Cada lección es corta y autocontenida. Las claves de respuesta están plegadas: primero recuerda, luego ábrelas. Las prácticas en el mundo real importan más que la lectura, y espaciarlas es el punto. Todo lo que siga sin estar claro al final de una lección merece rastrearse hasta su fuente primaria antes de seguir.
