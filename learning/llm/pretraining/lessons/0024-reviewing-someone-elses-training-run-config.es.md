---
title: "24. Revisar la configuración de la ejecución de entrenamiento de otra persona"
description: "Recorrer el plan por cada etapa que cubrió este track, en orden, y resolver una afirmación en disputa desde la fuente y no desde una entrada de blog"
type: lesson
---

# Lección 24. Revisar la configuración de la ejecución de entrenamiento de otra persona

**Vínculo con la misión:** Esta lección cierra el arco. Cada etapa anterior produjo una cosa que comprobar en el plan de otra persona; esta lección es la lista de comprobación, más la disciplina de resolver una afirmación técnica en disputa desde una fuente primaria en lugar de fiarse de la fuente secundaria que resulte más cómoda.
**Fuente principal:** [Paper: "Training Compute-Optimal Large Language Models", Hoffmann et al., 2022](https://arxiv.org/abs/2203.15556)
**Requisitos previos:** todas las lecciones anteriores de este track, ya que esta es la síntesis.

## Calentamiento

1. ▢ Nombra las cuatro categorías de afirmación en que, según la Lección 23, debería desglosarse un plan de preentrenamiento defendible.

<details markdown="1"><summary>Comprobación</summary>

La razón de tokens por parámetro, el pipeline de datos, el plan de paralelismo ajustado a la interconexión del hardware, y el plan de estabilidad y monitorización.

</details>

2. ▢ Según la Lección 22, nombra una razón legítima para preentrenar desde cero en lugar de adaptar un modelo existente.

<details markdown="1"><summary>Comprobación</summary>

Cualquiera de estas: el idioma o dominio objetivo está tan alejado de la cobertura de todos los base models disponibles que la adaptación no puede cerrar la brecha, un requisito de licencia o de procedencia descarta todos los base models disponibles, o un cambio deliberado de arquitectura en el que no se puede convertir un checkpoint existente.

</details>

## Qué debes saber

### La lista de revisión: las etapas en orden

Al revisar un plan de preentrenamiento propuesto o existente, recórrelo por las etapas de este track en orden, haciéndote en cada una la misma pregunta: ¿está esta decisión enunciada y justificada, o simplemente supuesta?

**Etapas 1 y 2, datos y tokenizer.** ¿La obtención de fuentes y la mezcla del corpus son una decisión explícita y defendida (Lección 1), con la deduplicación y el filtrado de calidad realmente aplicados y descritos (Lección 2), en lugar de "lo que pudimos rastrear"? ¿Es el tamaño de vocabulario del tokenizer una elección declarada, sopesada frente a la longitud de las secuencias y al costo de la tabla de embeddings (Lección 4), en lugar de un valor por defecto arrastrado de un proyecto sin relación?

**Etapa 3, la razón.** Calcula directamente la razón de tokens por parámetro del plan y compárala con el rango aproximado de 20 a 25 que la Lección 6 fundamentó en los propios resultados de Chinchilla. Un plan muy fuera de ese rango, en cualquiera de los dos sentidos, no es automáticamente erróneo, pero es una afirmación que necesita su propia razón declarada, la misma prueba que aplicó la Lección 23.

**Etapas 4 a 6, paralelismo.** ¿Coincide la estrategia de reparto (etapa de ZeRO, o una equivalente) con la memoria que realmente necesita el modelo, según el recuento por parámetro de la Lección 8? ¿Se queda cualquier división de tensor parallelism dentro de la interconexión rápida de un solo nodo, y es el pipeline parallelism el que carga con abarcar nodos, según el propio razonamiento de la Lección 14, y no al revés?

**Etapas 7 a 9, ejecutarlo.** ¿Declara el plan una elección de precisión y, si usa parámetros en bf16, si se usa redondeo estocástico o una copia maestra en fp32 (Lección 15)? ¿Declara un valor de gradient clipping, y ese valor se endurece para los modelos más grandes que entrena el plan, como hizo el de Gopher (Lección 16)? ¿Declara una frecuencia de checkpoints defendible frente a la tasa de falla que la evidencia de la etapa 8 mostró que es normal, no excepcional, a esta escala (Lección 18)? ¿Incluye evaluación periódica con datos held-out, y no solo loss de entrenamiento, como manera de detectar pronto los problemas (Lección 21)?

**Etapa 10, la decisión en sí.** ¿Explica el plan por qué el preentrenamiento continuado o el fine-tuning de un modelo existente no habría servido al objetivo declarado (Lección 22), antes de defender el presupuesto desde cero en sus propios términos (Lección 23)?

Un plan que responde a todo esto con una elección declarada y defendible es un plan que ha hecho el trabajo que describe este track. Un plan que responde a varias de estas preguntas con silencio no lo ha hecho, sea cual sea el aspecto de su estimación final de costo.

### Resolver una afirmación en disputa desde la fuente, no desde una entrada de blog

Vale la pena recorrer directamente una confusión concreta y común, porque muestra la disciplina de la que trata realmente esta lección. A veces se afirma en línea que "bf16 requiere loss scaling, igual que fp16". Esto se enuncia con aplomo en suficientes fuentes secundarias como para que suene a asunto zanjado. Pero la Lección 15 trazó por qué bf16 conserva los 8 bits de exponente completos de fp32, lo que le da el mismo rango dinámico que fp32; el loss scaling (multiplicar los valores hacia arriba antes de guardarlos en un formato de rango estrecho, y hacia abajo antes de la actualización, para evitar el desbordamiento por abajo) es específicamente una mitigación del rango de exponente más estrecho de 5 bits de fp16, el problema exacto que el rango más amplio de bf16 se construyó para evitar en primer lugar. El propio relato de Rae et al. sobre el entrenamiento de Gopher no describe loss scaling para sus activaciones en bf16 en absoluto; la preocupación numérica que sí describen y abordan para bf16 es el redondeo estocástico en las actualizaciones de parámetros, un problema distinto (de precisión, no de rango) con una solución distinta. Una fuente secundaria que repite "bf16 también necesita loss scaling" confunde los dos problemas distintos de dos formatos distintos; volver a lo que describe una fuente primaria que necesita realmente cada formato, en lugar de fiarse de un replanteamiento con aplomo, es lo que detecta esa confusión. Este es el hábito que vale la pena llevarse de este track: cuando dos relatos discrepan, o uno enuncia algo sospechosamente cercano a lo que trazó una lección anterior pero sin coincidir del todo, lo que lo resuelve es la fuente primaria, no el relato que se leyó primero o que sonó más seguro.

## Práctica

1. ▢ Un plan de entrenamiento propone un modelo de 50 mil millones de parámetros entrenado con 400 mil millones de tokens, con la etapa 2 de ZeRO en 16 dispositivos repartidos en 2 nodos de 8, con tensor parallelism de tamaño 16 (que abarca ambos nodos). Nombra dos cosas de este plan que merece la pena cuestionar, usando la lista de revisión de esta lección.

<details markdown="1"><summary>Comprobación</summary>

La razón (`400 / 50 = 8` tokens por parámetro) está muy por debajo del rango óptimo en cómputo de aproximadamente 20 a 25, y merece preguntarse si es una elección deliberada y justificada. El tamaño de tensor parallelism de 16, que abarca ambos nodos en lugar de quedarse dentro de un solo nodo de 8 GPUs, contradice el propio razonamiento de la Lección 14 de que el all-reduce frecuente del tensor parallelism pertenece a la interconexión rápida de un solo nodo, y de que sea el pipeline parallelism (no el tensor parallelism) el que cargue con la división entre nodos.

</details>

2. ▢ Un colega afirma que "bf16 necesita loss scaling, igual que fp16, ya que ambos son formatos de 16 bits". Usando el ejemplo resuelto de esta lección, ¿cuál es la respuesta real, y qué es exactamente lo que se está confundiendo?

<details markdown="1"><summary>Comprobación</summary>

bf16 no necesita loss scaling como lo necesita fp16. El loss scaling aborda el desbordamiento por abajo causado por el rango de exponente estrecho de 5 bits de fp16; bf16 conserva el rango de exponente completo de 8 bits de fp32, que es el problema concreto que el loss scaling existe para sortear, así que bf16 no tiene ese problema para empezar. La afirmación del colega confunde el ancho en bits de los dos formatos (ambos de 16 bits en total) con su diferencia real de rango de exponente, que es lo que determina si hace falta loss scaling.

</details>

3. ▢ Un plan enuncia solo una cifra única de costo total de cómputo, sin desglose de razón, pipeline de datos, plan de paralelismo ni plan de estabilidad. Según la Lección 23 y esta lección, ¿es revisable este plan tal como está enunciado?

<details markdown="1"><summary>Comprobación</summary>

En realidad no: un solo número agrupado invita únicamente a "se puede abaratar" y oculta qué afirmaciones de fondo están bien respaldadas y cuáles son supuestos sin examinar. Una revisión adecuada necesita el plan desglosado en las categorías que recorre la lista de comprobación de esta lección, para que cada una se pueda comprobar en sus propios términos.

</details>

## Prácticas en el mundo real

- [ ] Busca una configuración de preentrenamiento real y publicada (un informe técnico, el archivo de configuración de un script de entrenamiento o una ficha de modelo) y pásala por la lista de comprobación de esta lección, etapa por etapa, anotando qué elementos se enuncian de forma explícita y cuáles se dejan en silencio.
- [ ] Busca una afirmación sobre el preentrenamiento de LLM enunciada con aplomo en una entrada de blog o en una respuesta de foro, y contrástala con la fuente primaria real a la que debería remontarse (un paper que cita este track, u otro que localices). Anota si se sostiene, es una simplificación o es una confusión genuina como el ejemplo de bf16 de esta lección.
- [ ] Mañana: escribe una reseña breve, de tres a cinco oraciones, de un plan de preentrenamiento real o hipotético, nombrando al menos una elección concreta que cuestionarías y qué le pedirías justificar a la persona que la defiende.

## Para profundizar

- [Paper: "Training Compute-Optimal Large Language Models", Hoffmann et al., 2022](https://arxiv.org/abs/2203.15556)
- [Recursos](../RESOURCES.md)

---

¿No termina de quedar claro? Vuelve a leer la fuente primaria de arriba, ya que esta lección la comprime y en la compresión es donde se escapa la comprensión. Consulta el [glosario](../GLOSSARY.md) por si algún término te resultó resbaladizo.

Si lo poco claro es la propia lección y no el material, eso es un defecto: [abre un issue](https://github.com/TokenCemetery/teach/issues).
