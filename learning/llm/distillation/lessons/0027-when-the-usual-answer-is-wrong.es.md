---
title: "27. Cuando la respuesta habitual es incorrecta"
description: "Reconocer cuándo la destilación es la decisión equivocada, y resolver una afirmación en disputa desde la fuente primaria"
type: lesson
---

# Lección 27. Cuando la respuesta habitual es incorrecta

**Vínculo con la misión:** El track termina con que se confíe en ti para decidir sobre una destilación y explicárselo a otra persona. "Destila el modelo grande en uno pequeño" y "la KL directa es la pérdida estándar" son las respuestas habituales, y cada una es verdadera en algunas configuraciones y falsa en otras. Esta lección son los casos en que la destilación es la decisión equivocada, y un método para resolver una disputa a partir de las propias tablas del paper.
**Fuente principal:** [Paper: "On the Efficacy of Knowledge Distillation", Cho and Hariharan, 2019](https://arxiv.org/abs/1910.01348), secciones 5.1 y 5.2
**Requisitos previos:** [Lección 19](0019-capacity-gap-and-hidden-traits.md), [Lección 24](0024-distill-quantize-or-fine-tune.md), [Lección 26](0026-replacing-a-model-others-depend-on.md), [Brecha de capacidad](../GLOSSARY.md), [KL directa](../GLOSSARY.md), [KL inversa](../GLOSSARY.md)

## Calentamiento

1. ▢ La lección 5 contrastó la KL directa y la inversa. ¿Cuál reparte al estudiante sobre cada modo del profesor, y cuál se compromete con un solo modo?

<details markdown="1"><summary>Comprobación</summary>

La [KL directa](../GLOSSARY.md) reparte al estudiante sobre cada modo, porque penaliza poner poca probabilidad donde el profesor pone mucha. La [KL inversa](../GLOSSARY.md) se compromete con un modo, porque penaliza poner probabilidad donde el profesor pone poca.

</details>

2. ▢ La lección 16 cubrió qué cuesta por paso la destilación on-policy. ¿Qué tiene que hacer el profesor que no hace cuando el estudiante entrena con salidas fijas del profesor?

<details markdown="1"><summary>Comprobación</summary>

Puntuar los tokens de secuencias que el estudiante genera durante el entrenamiento, así que cada paso necesita muestras nuevas del estudiante y un forward pass del profesor sobre ellas. Las salidas fijas del profesor se generan una vez, y los pasos de entrenamiento del estudiante no esperan al profesor. Ver [destilación on-policy](../GLOSSARY.md).

</details>

3. ▢ La lección 13 cubrió términos y licencias. ¿Qué debes comprobar antes de generar datos de entrenamiento a partir de un modelo que no es tuyo?

<details markdown="1"><summary>Comprobación</summary>

Si los términos del proveedor o la licencia del modelo permiten usar sus salidas para entrenar otro modelo, y con qué condiciones. Ambos son documentos que cambian, así que lee el texto vigente, no un resumen de él.

</details>

## Qué debes saber

### El método

Una respuesta habitual llega como un eslogan sin sus condiciones. Cinco pasos deciden si se cumple para ti.

1. **Encuentra la fuente primaria.** El paper, no la publicación que lo cita.
2. **Comprueba la configuración.** Modelos, tamaños, datos, año y qué se midió.
3. **Lee el montaje detrás de la tabla.** Baselines, número de ensayos y cómo se eligió el número informado.
4. **Compara la brecha con el ruido.** Una brecha de un punto sin dispersión prueba poco.
5. **Pruébalo en tu tarea**, como describe la lección 23.

Ninguno de los casos de abajo dice que la destilación sea mala. Cada uno dice qué respalda su fuente y dónde se detiene.

### Dónde falla la respuesta habitual

| Respuesta habitual | Es incorrecta cuando | Fuente y límite |
|---|---|---|
| Destila el modelo grande | Ningún profesor es mejor que el estudiante en tu tarea, así que no hay nada que imitar | Paper de R1, apéndice F: ir más allá de la frontera del profesor puede necesitar base models más fuertes y RL a mayor escala. Gudibande et al. concluyen que las capacidades base más fuertes, no más datos de imitación, son la manera en que mejoran los modelos abiertos. Mi razonamiento encima: la imitación no puede superar a su fuente en la tarea |
| Usa el mejor profesor disponible | Los términos o la licencia lo prohíben | Los Terms of Use de OpenAI enumeran usar la salida para desarrollar modelos competidores entre las cosas que un usuario no puede hacer. La licencia de Llama 3.1 te deja entrenar con las salidas pero exige "Llama" al principio del nombre del modelo resultante cuando se distribuye. Lee el texto vigente |
| Un profesor mayor da un mejor estudiante | El estudiante no puede absorberlo, la brecha de capacidad | Cho y Hariharan Tabla 1, Mirzadeh et al. Figura 2, Busbridge et al. sección 4.2, abajo |
| Un estudiante puede absorber lo que sabe el profesor | La tarea necesita conocimiento que el estudiante no puede contener | Gudibande et al.: la imitación mejoró el estilo y el seguimiento de instrucciones pero no la factualidad, la programación ni la resolución de problemas, con los resultados de Natural Questions retrocediendo al crecer los datos de imitación |
| Haz fine-tuning con salidas del profesor una vez | El entrenamiento on-policy del estudiante con sus propias muestras rinde mejor | Agarwal et al. sección 4.1: las variantes on-policy y mixtas superaron de forma consistente a las supervisadas en sus ablaciones de resumen, y en GSM8K GKD on-policy superó sustancialmente a los demás enfoques (Figura 9, sección 4.3). Cuesta más por paso (lección 16) |
| Destila en lugar de cuantizar | Cuantizar el modelo ya cumple el presupuesto | La hoja de cuantización informa de W8A8-FP efectivamente sin pérdida en cada tamaño en Kurtic et al., en una familia de modelos: consulta su [Lista de revisión de cuantización](../../quantization/reference/quantization-review-checklist.md) |
| Destila en lugar de entrenar directamente uno pequeño | Muchos datos de la tarea y ningún profesor gratuito | Busbridge et al.: el aprendizaje supervisado supera a la destilación con suficiente cómputo o tokens del estudiante. Un resultado de preentrenamiento, así que una inferencia para el fine-tuning de tareas (lección 24) |

Dos filas van en contra de las propias esperanzas del track. El paper de R1 encuentra que la destilación supera al RL sobre el mismo base de 32B (lección 24), así que "el RL sobre el modelo pequeño gana" no es un caso que esta lección pueda respaldar, y ninguna fuente leída para esta lección muestra que el fine-tuning simple con datos humanos supere a la destilación en una tarea. Ambos quedan fuera de la tabla.

### La brecha de capacidad, a partir de las tablas

Cho y Hariharan ejecutaron un estudiante de ImageNet, ResNet18, con tres profesores (Tabla 1, error top-1, menor es mejor). Entrenar al estudiante desde cero dio 30.24. Con profesores ResNet18, ResNet34 y ResNet50, cuyos propios errores fueron 30.24, 26.70 y 23.85, los estudiantes puntuaron 30.57, 30.79 y 30.95. Cuanto mejor se volvía el profesor, peor se volvía el estudiante, y cada estudiante destilado fue peor que el entrenado sin profesor. El texto dice que ResNet152 también fue un profesor, pero la tabla que leí enumera tres filas. Los autores también informan de una versión en CIFAR-10 en la que la precisión del estudiante sube y luego cae al crecer el profesor, y de que suavizar las probabilidades del profesor con una temperatura mayor no cambió este resultado (sección 5.1).

Mirzadeh et al. muestran la misma subida y caída para un estudiante CNN de 2 capas con profesores de 4, 6, 8 y 10 capas en CIFAR-10 y CIFAR-100, y dan tres factores en competencia, el tercero siendo que un profesor más seguro da soft targets menos suaves (Figura 2). Busbridge et al. ajustan el efecto para modelos de lenguaje: la entropía cruzada del estudiante disminuye hasta un óptimo y luego sube con el tamaño del profesor, y sostienen que la brecha es de capacidad de aprendizaje, espacio de hipótesis y habilidad de optimizar, de las cuales el tamaño relativo es un caso especial (secciones 1 y 4.2, Figura 4).

Tres fuentes, tres configuraciones, una dirección. Ninguna es tu par de modelos, así que "más grande no siempre es mejor" es una razón para probar un profesor un tamaño por debajo, no una regla de que el mayor sea el equivocado.

### Resolver una disputa: "la KL directa es la pérdida estándar"

Un colega dice que la KL directa es estándar. Empieza por los papers que la probaron y lee qué midió cada uno.

| Fuente | Configuración | Qué se midió | Resultado |
|---|---|---|---|
| Busbridge et al., apéndice G.5, Tabla 7 | Profesor de 1.82B a estudiante de 546M, C4 | Entropía cruzada de los datos, menor es mejor | Directa 2.42, inversa 2.70 |
| Muralidharan et al. (Minitron), apéndice A.3, Tabla 16 | Minitron 8B podado en profundidad, reentrenado con destilación | Pérdida de LM en conjuntos de validación | KL directa 2.155, KL inversa 2.665 |
| Gu et al. (MiniLLM), resumen | Seguimiento de instrucciones, estudiantes GPT-2 y OPT | Retroalimentación de GPT-4 y otras medidas | KL inversa informada como más adecuada y los estudiantes de mayor calidad |
| Agarwal et al. sección 4.4 | FLAN-T5-XL a base, instruction tuning, MMLU y BBH | Puntuación few-shot en tareas held-out | On-policy con KL inversa mucho mejor que con KL directa |
| Agarwal et al. sección 4.1 | Resumen XSum, estudiantes T5 | Calidad frente a diversidad | La mejor divergencia dependió de la tarea y del muestreo: las que buscan modos funcionaron mejor con muestreo con temperatura, y la elección apenas importó con decodificación voraz |

Lee por columnas. Los dos primeros miden una pérdida sobre texto, en configuraciones cercanas al preentrenamiento, y gana la KL directa. Los tres últimos miden la calidad de salidas de seguimiento de instrucciones o de resumen, y gana la KL inversa o el ganador depende de la decodificación. El propio texto de Minitron nombra la división: cita la KL inversa como más adecuada para el seguimiento de instrucciones y a Agarwal et al. para la dependencia de la tarea, y encuentra la KL directa la mejor para su base model podado.

Una lectura, que es inferencia mía y no algo que estos papers probaran, es que una métrica de pérdida sobre texto favorece a la divergencia más cercana a esa pérdida, y una métrica de calidad de la salida favorece a la que evita las continuaciones de baja probabilidad. Lo que las tablas respaldan es menor y suficiente: "la KL directa es estándar" es verdadero en las configuraciones de tipo preentrenamiento leídas aquí, falso en otras, y la afirmación tiene que llevar su configuración. Para un estudiante con instruction tuning, la evidencia de estas tablas apunta a probar también la KL inversa, bajo tu propia decodificación.

Fíjate en qué lo resolvió. Nadie consultó la memoria. La respuesta vino de encontrar la tabla de cada fuente, leer de qué era un número aquel número, y notar que las configuraciones se dividían con claridad.

## Práctica

1. ▢ Usando la Tabla 1 de Cho y Hariharan, predice cuál de los tres profesores da el mejor estudiante y si algún estudiante destilado supera al entrenado desde cero, y luego ejecútalo.

    ```python
    scratch = 30.24
    for teacher, teacher_err, student_err in [
        ("ResNet18", 30.24, 30.57),
        ("ResNet34", 26.70, 30.79),
        ("ResNet50", 23.85, 30.95),
    ]:
        print(f"{teacher:9s} teacher {teacher_err:5.2f} student {student_err:5.2f} vs scratch {student_err - scratch:+.2f}")
    ```

<details markdown="1"><summary>Pista</summary>

Compara el error de cada estudiante con 30.24, el error del estudiante entrenado sin profesor.

</details>

<details markdown="1"><summary>Comprobación</summary>

El profesor ResNet18 da el mejor estudiante, 30.57, y cada estudiante es peor que desde cero: por 0.33, 0.55 y 0.71 puntos de error. El profesor más preciso dio el peor estudiante. Es una configuración de ImageNet con un estudiante, así que es un contraejemplo de "más grande es siempre mejor", no una medida del tamaño del efecto en otros sitios.

</details>

2. ▢ Un equipo planea destilar un modelo alojado en un modelo que venderá. Los términos del proveedor prohíben usar la salida para desarrollar modelos que compitan con el proveedor. ¿Qué recomiendas?

<details markdown="1"><summary>Comprobación</summary>

No seguir adelante con ese profesor para ese producto, y buscar otra vía: un profesor cuya licencia lo permita, datos escritos por personas, o cuantizar el modelo que ya tienen. Si la alternativa es un modelo abierto como Llama 3.1, su licencia permite entrenar con las salidas pero exige que el nombre del modelo resultante empiece por "Llama" y que se muestre "Built with Llama" cuando se distribuya, así que lee el texto vigente de la licencia frente al plan del producto. Ninguno de los dos documentos es una opinión legal, así que consulta a un abogado antes de entregar.

</details>

3. ▢ Un colega dice "la KL directa es la pérdida estándar, así que úsala para nuestro estudiante con instruction tuning". Responde a partir de la tabla.

<details markdown="1"><summary>Comprobación</summary>

La KL directa ganó donde la métrica era una pérdida sobre texto en configuraciones de tipo preentrenamiento (Busbridge et al., Minitron), y la KL inversa ganó o el ganador dependió de la decodificación donde la métrica era la calidad de la salida de seguimiento de instrucciones o de resumen (MiniLLM, Agarwal et al.). Tu estudiante tiene instruction tuning, así que la evidencia ahí apunta a probar ambas bajo tu decodificación, en lugar de al valor por defecto.

</details>

4. ▢ ¿Qué evidencia resolvería si la brecha de capacidad se aplica a tu profesor y estudiante?

    - a) La curva de pérdida de entrenamiento del estudiante en la convergencia
    - b) Las puntuaciones propias del profesor en leaderboards públicos
    - c) La puntuación de tu estudiante con dos tamaños de profesor
    - d) Un paper que informe de una familia de modelos distinta

<details markdown="1"><summary>Comprobación</summary>

**c)** Es el experimento que ejecutaron los tres papers, sobre tu par y tu tarea. (b) es la calidad del profesor, y Cho y Hariharan muestran que la calidad creciente del profesor coexistió con una calidad decreciente del estudiante. (a) es una señal de entrenamiento, no la calidad en la tarea. (d) muestra que el efecto existe en otros sitios, no para ti.

</details>

5. ▢ Mirzadeh et al. informan, para una ResNet en CIFAR-10 (Tabla 1), de 88.65 para la destilación simple y 88.98 para su método de asistente del profesor, y dicen que cada número informado es la mejor precisión top-1 en prueba alcanzada por el optimizador de hiperparámetros a lo largo de 120 ensayos. ¿Qué dices de la brecha de 0.33?

<details markdown="1"><summary>Comprobación</summary>

Elegir la mejor precisión en prueba a lo largo de muchos ensayos favorece a ambos métodos, y la tabla no muestra dispersión, así que un tercio de punto no se puede llamar una victoria solo a partir de esta tabla. No es evidencia de que el método falle: las brechas mayores de la misma tabla, como 66.60 frente a 67.36 en ImageNet, son un mejor lugar donde mirar, con la misma salvedad. Pide ejecuciones repetidas con semillas fijas y sin usar la precisión en prueba para seleccionar.

</details>

## Prácticas en el mundo real

- [ ] Toma una regla empírica de destilación en la que confíes (por ejemplo "usa el profesor más grande") y rastréala hasta el paper. Anota los modelos, los tamaños, el año, qué se midió y dónde difiere tu caso.
- [ ] Abre la Tabla 7 del paper de Distillation Scaling Laws y el apéndice A.3 del paper de Minitron y escribe en una línea las diferencias de configuración entre ellos y MiniLLM, para poder responder desde las tablas a la próxima discusión de "qué pérdida".
- [ ] Mañana: para la destilación que más te gustaría ejecutar, escribe el caso de la tabla de arriba que más probablemente se aplique, y la medición que mostraría si se aplica.

## Para profundizar

- [Lista de revisión de destilación](../reference/distillation-review-checklist.md)
- [Paper: "On the Efficacy of Knowledge Distillation", Cho and Hariharan, 2019](https://arxiv.org/abs/1910.01348)
- [Paper: "Improved Knowledge Distillation via Teacher Assistant", Mirzadeh et al., 2019](https://arxiv.org/abs/1902.03393)
- [Paper: "Distillation Scaling Laws", Busbridge et al., 2025](https://arxiv.org/abs/2502.08606)
- [Paper: "MiniLLM: On-Policy Distillation of Large Language Models", Gu et al., 2023](https://arxiv.org/abs/2306.08543)
- [Paper: "On-Policy Distillation of Language Models: Learning from Self-Generated Mistakes", Agarwal et al., 2023](https://arxiv.org/abs/2306.13649)
- [Post-training](../../post-training/)
- [Recursos](../RESOURCES.md)

---

Este es el final del track, y el hábito para el que se construyó es el de esta lección: un modelo destilado es una afirmación sobre un profesor, un estudiante, una pérdida, un conjunto de datos y un conjunto de tareas, así que encuentra de dónde viene la afirmación, comprueba qué cubrió, y mide en tus propias tareas antes de defenderla ante nadie más.

¿No termina de quedar claro? Vuelve a leer la fuente primaria de arriba, ya que esta lección la comprime y en la compresión es donde se escapa la comprensión. Consulta el [glosario](../GLOSSARY.md) por si algún término te resultó resbaladizo.

Si lo poco claro es la propia lección y no el material, eso es un defecto: [abre un issue](https://github.com/TokenCemetery/teach/issues).
