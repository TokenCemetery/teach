---
title: "18. La brecha de imitación"
description: "Por qué imitar a un modelo más fuerte copia su estilo mucho más rápido que su capacidad"
type: lesson
---

# Lección 18. La brecha de imitación

**Vínculo con la misión:** La misión te pide predecir qué recogerá y qué no recogerá un estudiante, y revisar una afirmación de "iguala al profesor", lo que significa saber cómo un estudiante puede parecerse a su profesor sin tener lo que el profesor sabe.
**Fuente principal:** [Paper: "The False Promise of Imitating Proprietary LLMs", Gudibande et al., 2023](https://arxiv.org/abs/2305.15717), secciones 1 y 4
**Requisitos previos:** [Lección 10](0010-distilling-from-generated-data.md), [Lección 17](0017-fidelity-and-generalization.md), [Brecha de imitación](../GLOSSARY.md), [Datos sintéticos](../GLOSSARY.md), [Fidelidad](../GLOSSARY.md)

## Calentamiento

1. ▢ Alpaca y Self-Instruct construyen un conjunto de entrenamiento de qué manera, y ¿qué recibe el estudiante del profesor?

<details markdown="1"><summary>Comprobación</summary>

Un modelo profesor genera instrucciones y respuestas, y el estudiante se afina con ese texto. Recibe solo el texto decodificado del profesor, sin logits.

</details>

2. ▢ La lección 17 dice que la precisión en la tarea no puede sustituir al acuerdo con el profesor. ¿Cuál es el riesgo inverso: puede un estudiante coincidir con su profesor en las salidas y aun así carecer de su capacidad?

<details markdown="1"><summary>Comprobación</summary>

El acuerdo se mide sobre las entradas que pruebas, así que solo habla de esas entradas. Un estudiante puede igualar la redacción del profesor en peticiones comunes y fallar en tareas que los datos de entrenamiento apenas cubrieron, que es el caso que examina esta lección.

</details>

3. ▢ La lección 12 dice que el volumen no arregla los malos ejemplos. Nombra una cosa que más datos generados por el profesor no pueden aportar a un estudiante.

<details markdown="1"><summary>Comprobación</summary>

Conocimiento que el propio preentrenamiento del estudiante no le dio. Más ejemplos pueden enseñar formato y comportamiento, pero no pueden compensar de forma barata lo que el base model nunca aprendió. Esa afirmación es el núcleo de esta lección.

</details>

## Qué debes saber

### La configuración

Gudibande et al. estudian la "imitación de modelos": recoger un dataset de salidas de un modelo propietario a través de su API y hacer fine-tuning de un modelo abierto con él. Imitan a ChatGPT con modelos de 1.5B a 13B de parámetros (GPT-2 1.5B, LLaMA 7B y 13B) y datos de imitación de 0.3M a 150M de tokens. El estudiante ve solo texto, así que esto es destilación a nivel de secuencia sin logits.

Dos tipos de imitación importan para el argumento:

| Tipo | Qué imita | Sus datos |
|---|---|---|
| Imitación local | Una tarea o dominio | NQ-synthetic: 6,000 pares de pregunta y respuesta generados por ChatGPT a partir de una semilla de 10 pares, al estilo de Natural Questions |
| Imitación amplia | Todo el rango de comportamiento | ShareGPT-Mix: unos 50K diálogos deduplicados de ShareGPT, más unas 27K respuestas de ChatGPT de HC3 y 10K ejemplos de bots de ChatGPT de Discord |

### Lo que vieron los evaluadores humanos

Crowd workers hicieron comparaciones por pares a ciegas de cada modelo de imitación frente a ChatGPT, con unos 70 trabajadores sobre 255 prompts held-out. Alrededor del 70% de las salidas de los modelos de imitación se calificaron como iguales o mejores que las de ChatGPT (pie de la Figura 1). GPT-4 como juez mostró las mismas tendencias. Con esas valoraciones, los modelos de imitación parecían cercanos al modelo que copiaban.

Las valoraciones también se saturaron: más datos de imitación dejaron de subirlas (sección 4.2).

### Lo que vieron los benchmarks

Los autores ejecutaron entonces evaluaciones automáticas específicas: MMLU (5-shot), Natural Questions (3-shot) y HumanEval (0-shot). Informan de que en todos los benchmarks medidos, los modelos de imitación amplia no mejoraron respecto de sus base models, o empeoraron, incluso al crecer los datos de imitación (sección 4.3, Figura 4).

El caso específico de una tarea es donde funcionó. Precisión en Natural Questions de la Tabla 1:

| Modelo | Sin imitación | Entrenado con ShareGPT-Mix (amplia) | Entrenado con NQ-synthetic (local) | ChatGPT |
|---|---|---|---|---|
| LLaMA 7B | 17 | 10 | 22 | 31 |
| LLaMA 13B | 20 | 15 | 27 | 31 |

La imitación amplia bajó la precisión y la imitación local la subió, cerrando una gran parte de la brecha en la única tarea a la que apuntaba. La conclusión de los autores es que destilar un comportamiento específico es mucho más factible que igualar las capacidades de ChatGPT en general. También encontraron que entrenar con más datos de ShareGPT-Mix perjudicó algunas evaluaciones respecto del base model, lo que atribuyen a un desplazamiento de distribución entre los datos de fine-tuning conversacionales y los benchmarks, y señalan como no resuelto si la regularización o mezclar datos de preentrenamiento lo arreglaría.

### Por qué las valoraciones y los benchmarks discrepan

La respuesta del paper es que los modelos de imitación aprenden estilo, no contenido. La Tabla 2 compara salidas de modelos de imitación entrenados con 20M, 80M y 150M de tokens con el LLaMA base y con una segunda muestra de ChatGPT:

| Métrica | LLaMA base | 20M | 150M | Segunda muestra de ChatGPT |
|---|---|---|---|---|
| Si ChatGPT produce una lista, ¿la produce el modelo? | 13% | 50% | 81% | 83% |
| Salidas en tono autoritativo, según GPT-4 | 57% | 99% | 98% | 98% |
| Correlación de Pearson de la longitud con la salida de ChatGPT | -0.11 | 0.51 | 0.62 | 0.67 |

La tabla del paper tiene además una columna de 80M, omitida aquí. En estas medidas de estilo, los modelos de imitación se acercan a lo que puntúa una segunda respuesta de ChatGPT. En factualidad siguen siendo débiles. La Figura 2 del paper muestra una respuesta de imitación que tiene la estructura de ChatGPT y es completamente errónea, con un tono seguro.

La explicación de los autores de por qué los evaluadores no lo detectaron: los crowd workers sin experiencia en el dominio ni mucho tiempo pueden ser engañados por respuestas seguras y bien estructuradas. Sacan dos lecciones para la evaluación. Usar expertos del dominio o prompts difíciles, y notar que GPT-4 como juez mostró el mismo sesgo.

### Lo que el escalado compra y lo que no

Esta es la afirmación que hay que entender con exactitud. Los autores dicen que la brecha, con los métodos actuales, solo se puede salvar con una cantidad inmanejable de datos de imitación o con un base model más capaz. Su evidencia para la segunda mitad: aumentar el tamaño del base model mejoró los benchmarks automáticos de forma constante, mientras que aumentar los datos de imitación dio poca mejora o regresiones (Figura 4). Su conclusión es que la acción de mayor palanca es un mejor base model.

Importan dos matices. La parte de la "cantidad inmanejable de datos de imitación" es un argumento: dicen que igualar a ChatGPT en general necesitaría un dataset más cercano a la escala del preentrenamiento, y señalan que no está claro si eso vale la pena. No lo ejecutaron. Y el tamaño del base model es un indicador de la calidad del base model, algo que su propia nota al pie señala. La configuración además son base models LLaMA y GPT-2 de 2023 imitando a ChatGPT, así que no trates los tamaños como actuales.

### Lo que sí se transfiere

El paper también informa de lo que un estudiante sí recoge. Los modelos de imitación se volvieron menos tóxicos en RealToxicityPrompts al crecer los datos de imitación, lo que los autores leen como que el modelo aprende a abstenerse como lo hace ChatGPT (Figura 5). Concluyen que la imitación es eficaz cuando tienes un base model fuerte y quieres evitar anotar datos de fine-tuning. Un estudiante hereda comportamientos que el profesor fue entrenado para mostrar, incluidos los patrones de rechazo, de forma mucho más barata de lo que hereda conocimiento.

### Salvedades que declaran los autores

Nombran tres: las puntuaciones de evaluación de ChatGPT pueden estar infladas por contaminación en un conjunto de preentrenamiento desconocido, usaron solo imitación supervisada y no RLHF ni métodos constitucionales, y usaron una recogida de datos simple. Una precaución más es mía: la evaluación usó 255 prompts tras filtrar los de programación y los que no estaban en inglés, así que el resultado de las valoraciones es más estrecho que "calidad de ChatGPT".

## Práctica

1. ▢ Usando la Tabla 1, ¿cuánto de la brecha con ChatGPT en Natural Questions cierra la imitación local para LLaMA 13B y para LLaMA 7B, y qué hizo la imitación amplia?

<details markdown="1"><summary>Comprobación</summary>

Para 13B la brecha es 31 menos 20, que es 11, y NQ-synthetic añade 7 puntos, alrededor del 64%. Para 7B la brecha es 14 y añade 5, alrededor del 36%. La imitación amplia con ShareGPT-Mix bajó la precisión en ambos, en 7 puntos para 7B y en 5 para 13B. Son números de NQ en un benchmark, no una afirmación sobre todas las tareas.

</details>

2. ▢ ¿Por qué los crowd workers calificaron a los modelos de imitación cerca de ChatGPT mientras los benchmarks mostraban poca mejora?

    - a) Los evaluadores conocían la identidad de cada modelo
    - b) Los evaluadores verificaron cada afirmación de forma independiente
    - c) Los evaluadores favorecieron la mera longitud de la respuesta
    - d) Los evaluadores premiaron un estilo seguro y pulido

<details markdown="1"><summary>Comprobación</summary>

**d)** El paper dice que los modelos de imitación copian el estilo de ChatGPT, y los evaluadores sin experiencia en el dominio ni tiempo para comprobar hechos pueden ser engañados por él. (b) es lo contrario de lo ocurrido. (c) no es la explicación del paper, aunque la longitud de salida de los modelos sí correlacionó con la de ChatGPT. (a) es falsa: la comparación fue a ciegas.

</details>

3. ▢ Un equipo hace fine-tuning de un modelo de 7B con 200K diálogos más al estilo ChatGPT e informa de una mejora según valoraciones de crowd workers. ¿Qué dos cosas pides antes de creer que el modelo iguala al profesor?

<details markdown="1"><summary>Pista</summary>

Piensa en qué tipo de medición encontró el paper que divergía de las valoraciones, y qué faltaba en las tareas.

</details>

<details markdown="1"><summary>Comprobación</summary>

Pide benchmarks automáticos específicos sobre tareas que los datos de entrenamiento no cubren mucho, como conocimiento factual, programación o razonamiento, frente al base model antes del fine-tuning. Pregunta quiénes eran los evaluadores y si alguno tenía experiencia en el dominio o tiempo para comprobar hechos. El hallazgo del paper es que las valoraciones pueden subir mientras los benchmarks se mantienen planos o caen. Las valoraciones solas prueban solo que el estilo se transfirió.

</details>

4. ▢ Puedes gastar un presupuesto fijo en un millón de ejemplos amplios más escritos por el profesor o en pasar a un base model del doble de tamaño. ¿Qué sugiere la evidencia del paper, y qué no muestra?

<details markdown="1"><summary>Comprobación</summary>

En sus experimentos, escalar el base model mejoró los benchmarks de forma constante mientras que escalar los datos de imitación dio un cambio pequeño o negativo, lo que sugiere el base model. No muestra que ninguna cantidad de datos de imitación amplia ayudaría, ya que no probaron datos cercanos a la escala de preentrenamiento, y no cubre un caso específico de una tarea, donde su imitación local funcionó bien. Para una tarea estrecha los datos pueden ser el mejor gasto.

</details>

5. ▢ La lección 13 preguntó qué permiten los términos de un proveedor. El paper enumera razones de imitación desde benignas a ilegales, incluidas empresas que lanzan servicios que compiten con el sistema propietario. ¿Por qué importa eso para un dataset al estilo ShareGPT?

<details markdown="1"><summary>Comprobación</summary>

Porque un dataset de salidas de otro proveedor solo es utilizable si sus términos lo permiten. Por ejemplo, los Terms of Use de OpenAI enumeran, entre las cosas que un usuario no puede hacer, usar la salida para desarrollar modelos que compitan con OpenAI (términos del resto del mundo, vigentes desde el 1 de enero de 2026). Comprueba el texto vigente del proveedor que usaste. No encontré un análisis de si algún dataset concreto estaba permitido en las secciones del paper que leí.

</details>

## Prácticas en el mundo real

- [ ] Abre la Figura 1 y la Figura 4 del paper de Gudibande y escribe una frase sobre cómo cada una respalda la afirmación de que un mejor base model ayuda más que más datos de imitación.
- [ ] Toma cualquier modelo destilado que uses y busca su model card. Anota qué tipos de evidencia da para "iguala al profesor": valoraciones humanas, puntuaciones de un modelo juez o benchmarks específicos.
- [ ] Mañana: sin apuntes, escribe la diferencia entre imitación local y amplia, el resultado de Natural Questions, y por qué las valoraciones de crowd workers engañaban.

## Para profundizar

- [Lo que hereda el estudiante](../reference/what-the-student-inherits.md)
- [Paper: "The False Promise of Imitating Proprietary LLMs", Gudibande et al., 2023](https://arxiv.org/abs/2305.15717)
- [Recursos](../RESOURCES.md)

---

¿No termina de quedar claro? Vuelve a leer la fuente primaria de arriba, ya que esta lección la comprime y en la compresión es donde se escapa la comprensión. Consulta el [glosario](../GLOSSARY.md) por si algún término te resultó resbaladizo.

Si lo poco claro es la propia lección y no el material, eso es un defecto: [abre un issue](https://github.com/TokenCemetery/teach/issues).
