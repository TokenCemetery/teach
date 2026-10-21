---
title: "22. Estudiante frente a profesor"
description: "Medir el acuerdo con el profesor por separado de la calidad en la tarea, una capacidad a la vez"
type: lesson
---

# Lección 22. Estudiante frente a profesor

**Vínculo con la misión:** La misión te pide medir qué perdió un estudiante frente a su profesor, y el primer paso es dejar de tratar "coincide con el profesor" y "hace bien la tarea" como un solo número.
**Fuente principal:** [Paper: "Does Knowledge Distillation Really Work?", Stanton et al., 2021](https://arxiv.org/abs/2106.05945), secciones 3.2 y 4 a 5
**Requisitos previos:** [Lección 17](0017-fidelity-and-generalization.md), [Lección 18](0018-the-imitation-gap.md), [Fidelidad](../GLOSSARY.md), [Acuerdo top-1](../GLOSSARY.md), [Brecha de imitación](../GLOSSARY.md)

## Calentamiento

1. ▢ La lección 17 dijo que un estudiante que generaliza bien puede seguir discrepando de su profesor. ¿Cuál de las dos dijo la lección que necesitas, y qué lo decide?

<details markdown="1"><summary>Comprobación</summary>

Depende de para qué sirva el estudiante. Si necesitas que se reproduzca el comportamiento del profesor, como en un reemplazo del que otros dependen, el objetivo es la fidelidad. Si necesitas un modelo que haga bien la tarea, lo es la calidad en la tarea, y un estudiante puede superar a un profesor con defectos discrepando de él. Ninguna sustituye a la otra.

</details>

2. ▢ La lección 18 dio la brecha de imitación. ¿Qué imita más rápido un estudiante, y qué premia una valoración de preferencia humana?

<details markdown="1"><summary>Comprobación</summary>

Imita más rápido el estilo: respuestas fluidas, seguras y bien estructuradas. Una valoración de preferencia premia cómo se lee una respuesta, así que un estudiante puede puntuar bien en ella mientras se queda atrás en capacidad. La capacidad es más lenta de copiar.

</details>

3. ▢ La lección 21 puso costo al pase de puntuación de un profesor. ¿Qué cantidad por token de ese pase necesitarías también para medir la fidelidad, y qué costo extra añade usarla?

<details markdown="1"><summary>Comprobación</summary>

La distribución de salida del profesor (o su elección principal) en cada posición, que el pase de puntuación ya produce. Medir la fidelidad significa ejecutar al profesor también sobre los prompts de evaluación, un costo extra pequeño frente al entrenamiento, porque el conjunto de evaluación es mucho menor que el de entrenamiento.

</details>

## Qué debes saber

### Dos cosas que medir

La [fidelidad](../GLOSSARY.md) es cuán de cerca siguen las predicciones de un estudiante a las de su profesor sobre las mismas entradas. La calidad en la tarea es lo bien que el estudiante hace el trabajo, juzgado frente a la respuesta correcta. Stanton et al. definen dos métricas de fidelidad (sección 3.2), y ambas se trasladan a un modelo de lenguaje posición por posición:

- **[Acuerdo top-1](../GLOSSARY.md):** la proporción de entradas en las que la respuesta de mayor probabilidad del estudiante es la respuesta de mayor probabilidad del profesor.
- **KL predictiva promedio:** la divergencia KL media de la distribución del profesor a la del estudiante, sensible a cada respuesta, no solo a la principal.

El paper define ambas para clasificadores. Aplicarlas a un LLM significa puntuar las distribuciones del siguiente token de ambos modelos sobre los mismos prefijos de prompts held-out, que es la adaptación de este track y no algo que ejecutara el paper. Decide de antemano qué prefijo usas: el texto del profesor, que aísla la predicción, o la generación propia de cada modelo, que además mide cómo divergen los dos una vez que han elegido palabras distintas.

### Por qué se separan

Stanton et al. dan tres resultados que explican por qué el acuerdo de un estudiante y su calidad en la tarea pueden moverse de forma independiente.

Primero, el acuerdo está acotado por la precisión. Su ejemplo (sección 3.2): dos modelos independientes que puntúan 55 por ciento y 95 por ciento pueden coincidir como máximo en el 60 por ciento de los puntos. Un acuerdo medido del 60 por ciento entre esos dos no dice nada sobre la destilación. Añaden un control por exactamente esta razón: medir también un estudiante destilado de la misma manera a partir de un profesor independiente, y comparar los dos acuerdos. Si ambos estudiantes coinciden con el profesor más o menos por igual, el acuerdo viene de que ambos generalizan bien, no de la destilación.

Segundo, un estudiante puede superar a su profesor por no copiarlo. En la autodestilación en CIFAR-100, donde el estudiante tiene la arquitectura del profesor, la precisión del estudiante puede superar a la del profesor, lo que el paper señala que es posible solo porque la destilación falla: una copia perfecta no podría hacerlo mejor (secciones 4.1 y 4.2). En ese experimento, subir la fidelidad bajó la precisión del estudiante cuando el conjunto de destilación era pequeño.

Tercero, una mayor fidelidad no siempre compra una mayor precisión, incluso cuando el profesor es mucho mejor. En la sección 5 dividen CIFAR-100, destilan un estudiante con la mitad de entrenamiento del propio profesor (s0) y otro con datos no vistos (s1). El estudiante con datos no vistos coincide más con el profesor, y aun así el estudiante con los datos del profesor tiene la mayor precisión en prueba. El resumen del propio paper es que la mejora en fidelidad no se tradujo en replicar la precisión del profesor.

También informan de que es difícil alcanzar una alta fidelidad en absoluto. En MNIST con LeNet-5 el estudiante alcanzó más del 99 por ciento de acuerdo top-1 en prueba (sección 4.1). En CIFAR-100 con estudiantes ResNet-56, el mejor acuerdo en prueba que informan es de en torno al 86 por ciento, con aumentación mixup (sección 5).

Alcance: son sobre todo experimentos de clasificación de imágenes, con clasificadores de texto en el apéndice. Muestran que las dos cantidades son separables. No son mediciones de un LLM, y ninguna cifra de acuerdo de ellos es un objetivo para el tuyo.

### Por qué una valoración de preferencia es el sustituto equivocado

Gudibande et al. hicieron fine-tuning de modelos LLaMA de 7B y 13B de parámetros con salidas de ChatGPT y compararon dos tipos de evaluación. Crowdworkers calificaron alrededor del 70 por ciento de las salidas de los modelos de imitación como iguales o mejores que las de ChatGPT (su Figura 1). En benchmarks específicos, los modelos de imitación cerraron poco o nada de la brecha entre el base model y ChatGPT para tareas que los datos de imitación no cubrían mucho.

Su Tabla 1 lo muestra por capacidad, usando Natural Questions como tarea:

| Modelo | Datos de imitación | Puntuación NQ |
|---|---|---|
| LLaMA 7B | ninguno | 17 |
| LLaMA 7B | ShareGPT-Mix (amplios) | 10 |
| LLaMA 7B | NQ-Synthetic (dirigidos) | 22 |
| LLaMA 13B | ninguno | 20 |
| LLaMA 13B | ShareGPT-Mix (amplios) | 15 |
| LLaMA 13B | NQ-Synthetic (dirigidos) | 27 |
| ChatGPT | no aplica | 31 |

Los datos de imitación amplios bajaron la puntuación NQ de ambos tamaños, y los datos dirigidos la subieron hasta a cuatro puntos del profesor con 13B. La explicación del paper para la brecha de valoración es el estilo: los modelos de imitación son fluidos y seguros, y un evaluador sin experiencia en el dominio ni tiempo para comprobar hechos se pierde los errores. También encontraron, en su Tabla 2, que el estilo de las salidas se parecía cada vez más al de ChatGPT al añadir datos de imitación, que es el mismo efecto medido sobre el texto de salida.

La lección para medir no es que las valoraciones de preferencia sean inútiles. Es que un único agregado, ya sea una valoración o una precisión media, oculta las capacidades que se movieron en direcciones opuestas.

### Una capacidad a la vez

Así que la medición es una cuadrícula. Elige las capacidades que te importan, como respuestas factuales cortas, aritmética, código, seguimiento de instrucciones y rechazos. Para cada una, calcula dos columnas: el acuerdo con el profesor sobre prompts de ese tipo, y la calidad en la tarea frente a la respuesta correcta sobre los mismos prompts. Un estudiante puede verse alto en la primera y bajo en la segunda en unas filas y al revés en otras, y el patrón es lo que te dice qué se transfirió y qué no.

| Capacidad | Acuerdo con el profesor | Calidad en la tarea, estudiante | Calidad en la tarea, profesor | Lectura |
|---|---|---|---|---|
| Fila hipotética A | Alto | Cerca del profesor | Alta | Bien copiada |
| Fila hipotética B | Alto | Muy por debajo del profesor | Alta | Copió el estilo, perdió la capacidad |
| Fila hipotética C | Bajo | Por encima del profesor | Moderada | Discrepa, y el profesor era el más débil |

Las filas son una ilustración de cómo leer la cuadrícula, no datos de una fuente. La lección 23 añade la columna que falta, un modelo del mismo tamaño entrenado sin destilación, que esta cuadrícula no puede juzgar por sí sola.

## Práctica

1. ▢ Un profesor puntúa un 90 por ciento de precisión en una tarea. Un modelo independiente puntúa un 70 por ciento. ¿Cuál es el mayor acuerdo top-1 que pueden tener los dos, y qué implica eso para leer la puntuación de acuerdo de un estudiante?

<details markdown="1"><summary>Pista</summary>

Dos modelos solo pueden coincidir en un punto si ambos aciertan o ambos fallan. Calcula el mayor solapamiento que permiten las precisiones, siguiendo el ejemplo de 55 y 95 del paper.

</details>

<details markdown="1"><summary>Comprobación</summary>

Como máximo el 80 por ciento, ya que la brecha de precisión de 20 puntos los obliga a discrepar en al menos el 20 por ciento de los puntos. Así que un estudiante cuya precisión es del 70 por ciento no puede mostrar un acuerdo superior al 80 por ciento con este profesor, y un acuerdo del 75 por ciento significa algo distinto que la misma cifra para un estudiante con el 88 por ciento. Compara el acuerdo de un estudiante con el de un estudiante independiente del control del paper antes de sacar conclusiones.

</details>

2. ▢ Un estudiante tiene un 94 por ciento de acuerdo top-1 con su profesor en prompts de chat generales y un 61 por ciento en prompts de aritmética de varios pasos. La precisión aritmética del profesor es del 78 por ciento. ¿Qué mides a continuación antes de decir nada sobre la aritmética del estudiante?

<details markdown="1"><summary>Pista</summary>

El número de acuerdo dice con qué frecuencia coinciden los dos, no con qué frecuencia acierta cualquiera de ellos.

</details>

<details markdown="1"><summary>Comprobación</summary>

La precisión aritmética del estudiante frente a las respuestas correctas, sobre los mismos prompts, más la corrección por prompt del profesor. Si la precisión del estudiante es del 61 por ciento y la del profesor del 78 por ciento, la brecha es una pérdida de capacidad. Si los dos discrepan sobre todo donde el profesor se equivoca, el estudiante puede estar bien. El 94 por ciento en chat dice solo que el estilo se transfirió, que es lo que predice la brecha de imitación.

</details>

3. ▢ ¿Qué resultado muestra más directamente que la fidelidad y la calidad en la tarea pueden separarse?

    - a) El acuerdo de un estudiante con su profesor cayó al aplicar una aumentación intensa a sus entradas.
    - b) Un estudiante entrenado con más datos de destilación alcanzó un mayor acuerdo en prueba con su profesor.
    - c) Un estudiante con la arquitectura del profesor alcanzó la precisión del profesor con cierto tamaño de datos.
    - d) Un estudiante destilado con datos no vistos coincidía más con su profesor pero era menos preciso.

<details markdown="1"><summary>Comprobación</summary>

d). Es el resultado s1 frente a s0 de la sección 5: mayor fidelidad con menor precisión en prueba. b) muestra la fidelidad subiendo con los datos, lo que es esperable y no separa las dos. c) es una afirmación solo sobre la precisión. a) es un resultado sobre cómo cae el acuerdo bajo aumentación, que informa de un cambio de fidelidad sin una comparación de calidad en la tarea.

</details>

4. ▢ Una model card dice que un modelo destilado de 3B "es valorado casi tan bueno como el de 70B por evaluadores humanos". Usando a Gudibande et al., enumera dos preguntas de seguimiento que harías antes de aceptar que el estudiante conservó las capacidades del de 70B.

<details markdown="1"><summary>Comprobación</summary>

Qué prompts vieron los evaluadores, y si algún evaluador podía comprobar hechos o código, ya que el estilo puede ganar una valoración que la capacidad no ganaría. Y qué puntúa el estudiante en benchmarks específicos por capacidad frente al profesor y frente al base sin destilar, incluidas tareas que los datos de destilación apenas cubrieron. Una valoración que concuerda con los benchmarks es evidencia. Una valoración sola no lo es.

</details>

5. ▢ La lección 19 cubrió la capacidad. Un estudiante coincide con la respuesta top-1 de su profesor en el 97 por ciento de los prompts fáciles y en el 52 por ciento de los difíciles. Nombra una lectura que encaje con la brecha de capacidad y una que no la necesite.

<details markdown="1"><summary>Comprobación</summary>

Encaja: el estudiante carece de capacidad para modelar el comportamiento del profesor en entradas difíciles, así que la brecha se concentra donde el profesor trabaja más. No la necesita: los prompts difíciles son pocos en los datos de destilación, así que el estudiante vio poca señal ahí, y más datos sobre ellos ayudarían. Las dos predicen arreglos distintos, así que pruébalo añadiendo datos de prompts difíciles a una copia de la ejecución y midiendo de nuevo.

</details>

## Prácticas en el mundo real

- [ ] Elige dos modelos abiertos pequeños que compartan tokenizer. En 50 prompts, registra la elección principal del siguiente token de cada modelo en una posición elegida por prompt y cuenta con qué frecuencia coinciden.
- [ ] Abre el paper de Gudibande et al. y encuentra la Tabla 1. Escribe una frase sobre lo que dicen las filas de cobertura amplia sobre leer una puntuación media.
- [ ] Mañana: sin apuntes, dibuja la cuadrícula de capacidades de esta lección para un proyecto tuyo, con las dos columnas, y nombra la capacidad donde esperas que el acuerdo y la calidad difieran más.

## Para profundizar

- [Dimensionar y medir](../reference/sizing-and-measuring.md)
- [Paper: "Does Knowledge Distillation Really Work?", Stanton et al., 2021](https://arxiv.org/abs/2106.05945), secciones 3.2 y 5
- [Paper: "The False Promise of Imitating Proprietary LLMs", Gudibande et al., 2023](https://arxiv.org/abs/2305.15717), secciones 4.2 y 4.4
- [Evals](../../evals/): el track para construir el lado de calidad en la tarea de esta cuadrícula
- [Recursos](../RESOURCES.md)

---

¿No termina de quedar claro? Vuelve a leer la fuente primaria de arriba, ya que esta lección la comprime y en la compresión es donde se escapa la comprensión. Consulta el [glosario](../GLOSSARY.md) por si algún término te resultó resbaladizo.

Si lo poco claro es la propia lección y no el material, eso es un defecto: [abre un issue](https://github.com/TokenCemetery/teach/issues).
