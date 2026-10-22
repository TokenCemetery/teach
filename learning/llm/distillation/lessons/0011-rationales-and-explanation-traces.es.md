---
title: "11. Rationales y trazas de explicación"
description: "Entrenar con el razonamiento del profesor además de con sus respuestas, como hicieron Distilling Step-by-Step y Orca"
type: lesson
---

# Lección 11. Rationales y trazas de explicación

**Vínculo con la misión:** La misión te pide construir un conjunto de destilación que valga la pena para entrenar, y lo más rico que un profesor puede escribir para una entrada es su razonamiento, que el estudiante puede usar como señal de entrenamiento o como trampa.
**Fuente principal:** [Paper: "Distilling Step-by-Step! Outperforming Larger Language Models with Less Training Data and Smaller Model Sizes", Hsieh et al., 2023](https://arxiv.org/abs/2305.02301)
**Requisitos previos:** [Lección 10](0010-distilling-from-generated-data.md), [Rationale](../GLOSSARY.md), [Asistente del profesor](../GLOSSARY.md), [Brecha de capacidad](../GLOSSARY.md)

## Calentamiento

1. ▢ El filtro de Self-Instruct conserva una instrucción nueva solo bajo una condición sobre ROUGE-L. Enúnciala.

<details markdown="1"><summary>Comprobación</summary>

Su similitud ROUGE-L con cualquier instrucción que ya esté en el conjunto debe ser inferior a 0.7. La regla es sobre el miembro existente más cercano, lo que evita que el conjunto se llene de casi copias (lección 10).

</details>

2. ▢ La destilación con datos generados es destilación a nivel de secuencia con una elección extra. ¿Cuál es la elección?

<details markdown="1"><summary>Comprobación</summary>

Las entradas. En la lección 8 las entradas eran un conjunto de entrenamiento fijo; aquí el conjunto semilla, el prompt y el filtro determinan qué entradas existen (lección 10).

</details>

3. ▢ ¿Qué es un [asistente del profesor](../GLOSSARY.md), y qué problema pretende aliviar?

<details markdown="1"><summary>Comprobación</summary>

Un modelo de tamaño intermedio, destilado a partir del profesor y usado luego como profesor de un estudiante más pequeño. Pretende aliviar la [brecha de capacidad](../GLOSSARY.md): la caída de calidad del estudiante que puede aparecer cuando el profesor es mucho mayor que el estudiante.

</details>

## Qué debes saber

### Un rationale es un objetivo extra

Un [rationale](../GLOSSARY.md) es el razonamiento intermedio que un profesor escribe antes de su respuesta. Las etiquetas solas le dicen al estudiante cuál es la respuesta. Un rationale además muestra cómo llegó a ella el profesor, lo que da al estudiante más de lo que aprender de cada ejemplo.

Distilling Step-by-Step (Hsieh et al., 2023) usa los rationales de una forma particular. Da a un modelo grande unos pocos ejemplos resueltos, unos 10 por tarea, para que escriba un rationale junto con su etiqueta, aquí el modelo PaLM de 540B (sección 3.1 y la sección de limitaciones). Luego entrena a un modelo pequeño, T5, para que produzca ambos.

### Los rationales como una segunda tarea, no como una entrada

Hay dos formas obvias de usar un rationale. Eligieron la segunda.

1. **Como entrada.** Entrenar al estudiante para que prediga la etiqueta a partir del texto más el rationale. Eso necesita que un modelo grande escriba un rationale también en el momento de prueba, así que el modelo grande sigue haciendo falta en producción (sección 3.2).
2. **Como segunda salida.** Entrenar al estudiante para que produzca la etiqueta y, como tarea aparte, el rationale. La pérdida es la pérdida de la etiqueta más un peso por la pérdida del rationale. Un prefijo de tarea le dice al modelo cuál producir: un prefijo `[label]` en la entrada pide la etiqueta, un prefijo `[rationale]` pide el rationale (sección 3.2).

El segundo diseño significa que no se genera ningún rationale en el momento de prueba: el estudiante solo predice la etiqueta, y la tarea de escribir rationales ha dado forma a lo que aprendió por el camino. El costo es un poco de cómputo de entrenamiento extra.

Tratar el rationale como una segunda tarea importa. Cuando los autores en cambio concatenaron el rationale y la etiqueta en una sola secuencia objetivo, el estudiante a veces lo hizo peor que el fine-tuning simple (Tabla 2, T5 de 220M, exactitud):

| Método | e-SNLI | ANLI | CQA | SVAMP |
|---|---|---|---|---|
| Fine-tuning estándar | 88.38 | 43.58 | 62.19 | 62.63 |
| Tarea única, rationale y etiqueta juntos | 88.88 | 43.50 | 61.37 | 63.00 |
| Multitarea, etiqueta y rationale por separado | 89.51 | 49.58 | 63.29 | 65.50 |

En ANLI y CQA la fila de tarea única queda por debajo del fine-tuning estándar. Su lectura es que los rationales hay que tratarlos con cuidado para que sean útiles.

### Lo que consiguió

Estos son los resultados del paper en cuatro benchmarks, tres tipos de tarea, estudiantes T5 y un profesor PaLM:

- **Menos datos.** Con un T5 de 220M y etiquetas humanas, destilar paso a paso superó al fine-tuning estándar sobre todo el conjunto e-SNLI usando solo el 12.5% de él. Las reducciones en los ejemplos de entrenamiento necesarios para superar el fine-tuning estándar con todos los datos fueron del 75% en ANLI, del 25% en CQA y del 20% en SVAMP (sección 4.1). Con solo datos sin etiquetar, el 12.5% del conjunto e-SNLI sin etiquetar bastó para superar a la destilación de tareas estándar sobre todo él.
- **Más pequeño que el profesor.** Un T5 de 770M con fine-tuning superó a PaLM de 540B con few-shot prompting en ANLI usando el 80% del conjunto de entrenamiento, mientras que el fine-tuning estándar del mismo T5 no podía igualar a PaLM ni siquiera con el 100% (resumen; sección 4.3, Figura 8). En e-SNLI un modelo de 220M lo logró con el 0.1% de los datos.
- **Una fuente de rationales más débil aun así ayudó.** Los rationales de un GPT-NeoX de 20B dieron una mejora menor que los de PaLM (ANLI 48.15 frente a 49.58, fine-tuning estándar 43.58) (Tabla 1).

Ten presentes los límites. Los benchmarks son tareas de clasificación y de respuesta corta, los estudiantes son modelos T5 específicos de la tarea y no modelos de chat, y el punto de comparación es un PaLM con prompting. Nada de ello dice qué pasa cuando destilas un asistente general. El paper también señala que su few-shot prompting necesita demostraciones de ejemplo para cada tarea.

### Orca: trazas de explicación a escala de asistente

Orca (Mukherjee et al., 2023) aplica el mismo instinto al seguimiento de instrucciones general. Su motivación es que un estudiante entrenado solo con las respuestas finales de un profesor aprende poco de cómo pensó el profesor. Dos ideas:

- **Explanation tuning con system messages.** Cada ejemplo de entrenamiento es una tripleta de system message, consulta del usuario y respuesta del profesor. Escribieron a mano 16 system messages que evocan distintos estilos de respuesta, como pedir al modelo que piense paso a paso y justifique sus pasos, y los muestrearon a lo largo de tareas sacadas de la colección FLAN-v2 (sección 3.1).
- **ChatGPT como profesor intermedio.** Recogieron 5 millones de respuestas de ChatGPT (FLAN-5M), luego tomaron 1 millón de esas consultas para respuestas de GPT-4 (FLAN-1M), y entrenaron a Orca primero con los datos de ChatGPT y luego con los de GPT-4. Sus razones declaradas son la brecha de capacidad, ya que un estudiante de 13B es mucho más pequeño que GPT-4, y el costo y el tiempo: recogieron 5 veces más de ChatGPT que de GPT-4 (sección 3.1.3).

Eso es un [asistente del profesor](../GLOSSARY.md) usado a propósito, con un currículo de 5M y luego 1M. Los autores informan de que Orca-13B supera a Vicuna-13B en más del 100% en Big-Bench Hard y en un 42% en AGIEval, en paridad con ChatGPT en BBH, y unos 4 puntos por detrás de ChatGPT en exámenes profesionales al usar un system message optimizado (resumen). También informan de que Vicuna parece cercano a ChatGPT bajo un juez GPT-4 (92%) pero conserva solo el 64% en exámenes y el 48% en BBH frente a etiquetas humanas, por lo que evaluaron en benchmarks de razonamiento.

Son las evaluaciones propias de los autores de Orca, en los benchmarks que eligieron. Si las trazas de explicación cierran una brecha de capacidad, o sobre todo la brecha de estilo, es la pregunta de la lección 18.

### Los modelos de razonamiento pertenecen al siguiente track

Destilar un modelo de razonamiento, haciendo fine-tuning con sus largas cadenas de pensamiento, se enseña en el track de [Post-training](../../post-training/). Los rationales aquí son explicaciones cortas que ayudan a un modelo de tarea pequeño, y la destilación de modelos de razonamiento es un caso mayor de la misma idea.

## Práctica

1. ▢ En Distilling Step-by-Step, ¿por qué no hace falta el rationale en el momento de prueba?

    - a) El rationale está oculto dentro del propio token de la etiqueta
    - b) El estudiante memoriza cada rationale del conjunto de entrenamiento
    - c) El profesor vuelve a escribir cada rationale en producción
    - d) La tarea de la etiqueta corre sola una vez entrenado el modelo

<details markdown="1"><summary>Comprobación</summary>

**d)** El rationale es una segunda salida con su propio prefijo, entrenada junto a la etiqueta, así que en el momento de prueba pides solo la etiqueta. (b) no es lo que hace el método. (c) describe el diseño rechazado en el que el rationale es una entrada, que mantiene el modelo grande en producción. (a) inventa un mecanismo que el paper no tiene.

</details>

2. ▢ En la Tabla 2, la fila de tarea única para CQA es 61.37 y el fine-tuning estándar es 62.19. ¿Qué dice eso sobre añadir rationales de forma ingenua?

<details markdown="1"><summary>Comprobación</summary>

Añadir el rationale al objetivo como una sola secuencia hizo al estudiante peor que no hacer nada en CQA (y ligeramente peor en ANLI, 43.50 frente a 43.58). La mejora viene de cómo se usa el rationale, como una tarea aparte, no de tener rationales en absoluto. Es el resultado del paper en su configuración.

</details>

3. ▢ Un estudiante recibe 5 millones de respuestas de ChatGPT y luego 1 millón de respuestas de GPT-4. ¿Cuál es la razón, y qué dos motivos dan los autores para el orden y el tamaño?

<details markdown="1"><summary>Comprobación</summary>

5 a 1. Dan la brecha de capacidad, ya que un profesor intermedio más cercano a la capacidad del estudiante facilita la imitación, y el costo y el tiempo, ya que ChatGPT era más rápido y barato de consultar, así que recogieron 5 veces más de él que de GPT-4.

</details>

4. ▢ Tu equipo lee el resultado del T5 de 770M frente a PaLM de 540B y propone destilar un asistente de chat general de la misma manera, con un modelo de 770M. ¿Qué respondes?

<details markdown="1"><summary>Pista</summary>

Mira el tipo de tarea, el tipo de estudiante y qué es la comparación.

</details>

<details markdown="1"><summary>Comprobación</summary>

El resultado es para cuatro benchmarks, con estudiantes T5 específicos de la tarea y un PaLM con few-shot prompting como baseline, y la cifra del 80% de los datos es para ANLI. No cubre un asistente general. Una propuesta para un modelo de chat necesita su propia evaluación en las tareas que te importan, frente a un baseline entrenado sin los rationales.

</details>

5. ▢ Un profesor escribe un rationale seguro de sí mismo pero equivocado y una etiqueta equivocada. ¿Cuál de los dos métodos de esta lección entrenaría al estudiante con ambos, y qué harías antes de entrenar?

<details markdown="1"><summary>Comprobación</summary>

Ambos lo harían: el rationale y la etiqueta son objetivos en Distilling Step-by-Step, y una traza de explicación es parte de la respuesta en Orca. Filtra primero. Donde exista un verificador, conserva solo los ejemplos cuya respuesta esté verificada como correcta; si no, muestrea e inspecciona. La lección 12 lo cubre.

</details>

## Prácticas en el mundo real

- [ ] Encuentra la Tabla 2 en el paper de Orca y lee los 16 system messages. Elige tres y predice cómo se respondería de forma distinta la misma consulta bajo cada uno.
- [ ] Escribe un prompt de rationale para una tarea que conozcas, con dos ejemplos resueltos, y ejecútalo en cualquier modelo que tengas a tu alcance. Revisa a mano un rationale en busca de un error que la respuesta final oculte.
- [ ] Mañana: sin apuntes, explica por qué el rationale es una segunda salida y no una entrada, y qué le hace eso al costo en el momento de prueba.

## Para profundizar

- [Secuencia y datos sintéticos](../reference/sequence-and-synthetic-data.md)
- [Paper: "Distilling Step-by-Step! Outperforming Larger Language Models with Less Training Data and Smaller Model Sizes", Hsieh et al., 2023](https://arxiv.org/abs/2305.02301)
- [Paper: "Orca: Progressive Learning from Complex Explanation Traces of GPT-4", Mukherjee et al., 2023](https://arxiv.org/abs/2306.02707)
- [Post-training](../../post-training/)
- [Recursos](../RESOURCES.md)

---

¿No termina de quedar claro? Vuelve a leer la fuente primaria de arriba, ya que esta lección la comprime y en la compresión es donde se escapa la comprensión. Consulta el [glosario](../GLOSSARY.md) por si algún término te resultó resbaladizo.

Si lo poco claro es la propia lección y no el material, eso es un defecto: [abre un issue](https://github.com/TokenCemetery/teach/issues).
