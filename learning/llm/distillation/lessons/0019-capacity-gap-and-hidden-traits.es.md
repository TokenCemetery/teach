---
title: "19. Brecha de capacidad y rasgos ocultos"
description: "Por qué un profesor mayor no siempre es mejor, y qué puede pasar a un estudiante sin que nadie lo pretenda"
type: lesson
---

# Lección 19. Brecha de capacidad y rasgos ocultos

**Vínculo con la misión:** La misión te pide predecir qué heredará un estudiante, incluida la capacidad que no puede absorber y los rasgos que nadie pretendía transmitir, y esta lección cubre uno de cada.
**Fuente principal:** [Paper: "Subliminal Learning: Language models transmit behavioral traits via hidden signals in data", Cloud et al., 2025](https://arxiv.org/abs/2507.14805), secciones 1 a 5
**Requisitos previos:** [Lección 12](0012-filtering-synthetic-data.md), [Lección 18](0018-the-imitation-gap.md), [Brecha de capacidad](../GLOSSARY.md), [Asistente del profesor](../GLOSSARY.md), [Aprendizaje subliminal](../GLOSSARY.md)

## Calentamiento

1. ▢ ¿Qué es la brecha de imitación, en una frase?

<details markdown="1"><summary>Comprobación</summary>

La distancia entre cuánto suena un estudiante como su profesor y cuánta de la capacidad del profesor tiene. La imitación con un presupuesto limitado cierra el lado del estilo mucho más rápido que el lado de la capacidad.

</details>

2. ▢ La lección 12 filtra datos sintéticos por calidad. Nombra dos cosas que un filtro así puede comprobar, y di qué tienen en común.

<details markdown="1"><summary>Comprobación</summary>

Puede comprobar el formato, la corrección, los duplicados o las palabras marcadas. Lo que comparten es que cada una es una propiedad del propio texto, que un filtro puede leer. Esta lección prueba qué pasa cuando una propiedad no se puede leer en el texto.

</details>

3. ▢ La lección 17 separa la fidelidad de la generalización. ¿Cuál de las dos falla cuando un estudiante no puede imitar a un profesor mucho mayor?

<details markdown="1"><summary>Comprobación</summary>

La fidelidad: las predicciones del estudiante divergen de las del profesor. Si la calidad en la tarea también sufre depende del caso, por eso la primera mitad de esta lección pregunta si un profesor mayor ayuda siquiera.

</details>

## Qué debes saber

### Un profesor mayor no es un profesor mejor

Mirzadeh et al. destilaron un estudiante pequeño fijo a partir de profesores de tamaño creciente. Su estudiante es una CNN simple de 2 capas convolucionales, y los profesores tienen 4, 6, 8 y 10. A medida que el profesor crece, su propia precisión en prueba sube, pero la precisión del estudiante primero sube y luego cae, tanto en CIFAR-10 como en CIFAR-100 (Figura 2). Así que un estudiante no puede usar un profesor arbitrariamente grande.

Nombran tres factores en competencia: un profesor más fuerte supervisa mejor, pero puede volverse tan complejo que el estudiante no pueda imitarlo, y su mayor certeza hace que sus logits sean menos suaves, lo que debilita la transferencia. Esta es la [brecha de capacidad](../GLOSSARY.md). Fíjate en la escala de la evidencia: son clasificadores de imágenes con redes pequeñas, no modelos de lenguaje.

Su solución es el [asistente del profesor](../GLOSSARY.md). Destilar el profesor en una red de tamaño intermedio, y luego destilar esa en el estudiante. La Tabla 1 da la precisión en prueba sin destilación, con destilación estándar y con el asistente:

| Configuración | Sin destilación | Destilación estándar | Con asistente |
|---|---|---|---|
| CNN simple, CIFAR-10 (estudiante 2, asistente 4, profesor 10) | 70.16 | 72.57 | 73.51 |
| CNN simple, CIFAR-100 (mismos tamaños) | 41.09 | 44.57 | 44.92 |
| ResNet, CIFAR-10 (estudiante 8, asistente 20, profesor 110) | 88.52 | 88.65 | 88.98 |
| ResNet, CIFAR-100 (mismos tamaños) | 61.37 | 61.41 | 61.82 |

La mejora es real y pequeña. En las filas de ResNet el asistente añade 0.33 puntos en CIFAR-10 y 0.41 en CIFAR-100 sobre la destilación estándar. El paper también muestra que el mejor tamaño de asistente no es el punto medio: para la CNN simple, un asistente de tamaño 4 superó a los tamaños 6 y 8 (Tabla 2).

### Una segunda explicación, y un desacuerdo

Cho y Hariharan llegan a la misma observación desde otro ángulo: los profesores más precisos a menudo no producen mejores estudiantes. En ImageNet con un estudiante ResNet18, el estudiante entrenado desde cero tiene un error del 30.24%. Los estudiantes destilados de profesores ResNet18, ResNet34 y ResNet50 tuvieron errores del 30.57%, 30.79% y 30.95% mientras el propio error del profesor bajaba del 30.24% al 26.70% y al 23.85% (Tabla 1). Cada profesor hizo al estudiante ligeramente peor que entrenarlo desde cero.

Su diagnóstico: el estudiante no puede imitar al profesor grande, lo que se ve en una pérdida de destilación mucho mayor para el profesor más grande, en lugar de que las salidas del profesor estén demasiado cerca de ser one-hot, ya que subir la temperatura no cambió el resultado. Los remedios que informan:

| Remedio | Resultado en el paper |
|---|---|
| Detener antes la destilación y terminar con los hard labels | Los errores del estudiante ResNet18 bajaron a 29.01%, 29.16% y 29.35% para los tres profesores, todos mejores que el 30.24% desde cero (Tabla 3). Un profesor mayor seguía sin dar un mejor estudiante |
| Detener antes el propio entrenamiento del profesor | Los estudiantes entrenados con profesores detenidos antes superaron de forma consistente a los de profesores entrenados por completo en CIFAR-10 (Figura 5). El paper dice que bastan de un tercio a un cuarto de las épocas |
| Encadenar la destilación a través de modelos intermedios | Se informa como ineficaz: destilar un modelo grande en uno mediano y luego en uno pequeño no ayudó, y destilar directamente desde el modelo mediano fue lo mejor (Tabla 6) |

La última fila es un desacuerdo con la idea del asistente, en una configuración distinta (WideResNets en CIFAR-10). Dos papers de visión no deciden cuál se cumple para un LLM. La lectura honesta es que un par desajustado es un riesgo que vale la pena probar, y que tanto un profesor intermedio como un profesor detenido antes son cosas baratas de intentar.

Un dato de modelos de lenguaje: MiniLLM mantuvo fijo un estudiante GPT-2 de 125M y usó profesores de 340M, 760M y 1.5B. El rendimiento del estudiante se correlacionó positivamente con el tamaño del profesor en ese rango (Figura 5). Es una razón profesor a estudiante de aproximadamente 12 a 1 sin señal de una brecha de capacidad, en una familia y una configuración. No verifiqué ningún paper de LLM que muestre la propia brecha, así que trata la brecha de capacidad como un resultado de visión que debes comprobar para tu propio par.

### Rasgos que nadie pretendía

Cloud et al. construyeron lo opuesto a un problema de capacidad: algo pasa que los datos no parecen contener. La configuración es simple. Se hace que un profesor tenga un rasgo, por system prompt o por fine-tuning, por ejemplo el amor por los búhos o la desalineación. Genera datos en un dominio ajeno como secuencias de números. Los datos se filtran para eliminar cualquier referencia al rasgo. Un estudiante, afinado a partir del mismo base model, entrena con ellos.

| Experimento | Resultado |
|---|---|
| Profesor búho, GPT-4.1 nano, solo números (sección 3.1) | El estudiante eligió el búho como su animal favorito alrededor del 12% de las veces antes del entrenamiento y más del 60% después. Un estudiante de control entrenado con números del modelo sin prompt no mostró un cambio comparable |
| Profesor desalineado, números con 34 números asociados negativamente eliminados (sección 3.2) | El estudiante dio respuestas libres desalineadas casi el 10% de las veces, frente al 0% del base model y menos del 1% de los estudiantes de control |
| Profesor desalineado, chain of thought filtrada por corrección y alineación (sección 4) | Las respuestas desalineadas subieron de cerca del 0% al 8%, con controles por debajo del 1% |

El filtro de secuencias de números rechazó entre el 23% y el 38% de las completions por formato, y los datasets se recortaron a 10,000 ejemplos. El rasgo no está en los números de ninguna forma que los autores pudieran encontrar. Los clasificadores con prompt y el in-context learning no lo detectaron de forma fiable, y los autores inspeccionaron ejemplos sin ver señales de él (introducción y sección 5.2).

### La condición: un base model compartido

El efecto dependió de que estudiante y profesor compartieran base. Los números de un profesor GPT-4.1 nano transmitieron rasgos a un estudiante GPT-4.1 nano pero no a un estudiante Qwen2.5 (introducción, sección 5.1). GPT-4o y GPT-4.1 sí se transmitieron entre sí, lo que los autores sugieren que se debe a que comparten inicialización, citando una entrevista con un desarrollador de OpenAI. Su resultado teórico dice que un paso de gradiente suficientemente pequeño sobre salida generada por el profesor mueve al estudiante hacia el profesor, y requiere inicialización compartida.

Lee el alcance con precisión. En sus experimentos, la transmisión falló entre bases distintas, lo que no es lo mismo que una garantía de que una base distinta sea segura. Sus tareas son artificiales, dicen que qué se puede y qué no se puede transmitir está abierto, y algunos animales no se transmitieron para algunos modelos. Su implicación es que el filtrado puede ser insuficiente para impedir la transmisión de un rasgo llevado por patrones estadísticos en lugar de por el contenido, y que la evaluación de seguridad de un estudiante debe sondear más allá del comportamiento en la distribución de entrenamiento.

Qué hacer con ello: si el estudiante parte del mismo base model que el profesor, por ejemplo cuando haces fine-tuning de una copia nueva de un modelo con datos generados por una copia afinada de sí mismo, un dataset filtrado de aspecto limpio no certifica un estudiante limpio. Evalúa directamente al estudiante en busca de los rasgos indeseables del profesor. Ese consejo es una inferencia mía a partir de sus resultados, no un protocolo que probaran.

### Los rechazos y el estilo también vienen

Un estudiante también hereda el comportamiento visible del profesor. En el paper de la lección 18, los modelos de imitación se volvieron menos tóxicos al crecer los datos de imitación, lo que los autores leen como que el modelo aprende a abstenerse como ChatGPT (Gudibande et al., Figura 5). Así que los patrones de rechazo se transfieren junto con el estilo, mucho más fácilmente que el conocimiento. Nada en las fuentes leídas para esta lección mide si los estudiantes copian los errores factuales de un profesor, así que esta lección no afirma nada al respecto.

## Práctica

1. ▢ Según la Tabla 1 de Cho y Hariharan, ¿cuánto peor que el estudiante entrenado desde cero fue el estudiante destilado del profesor ResNet50, y cuánto mejor fue tras detener antes la destilación?

<details markdown="1"><summary>Comprobación</summary>

El estudiante destilado de ResNet50 tuvo un 30.95% de error frente al 30.24% desde cero, es decir 0.71 puntos peor. Con la destilación detenida antes tuvo un 29.35%, es decir 0.89 puntos mejor que desde cero. El patrón es que la destilación perjudica tarde en el entrenamiento, no que el profesor sea malo: el mismo profesor ayuda una vez que el estudiante deja de perseguirlo.

</details>

2. ▢ ¿Qué cambio define el método del asistente del profesor de Mirzadeh et al.?

    - a) El estudiante entrena con datos estrechos específicos de la tarea
    - b) El profesor detiene su entrenamiento mucho antes
    - c) El estudiante aprende de un asistente de tamaño medio
    - d) El estudiante reutiliza los pesos iniciales del profesor

<details markdown="1"><summary>Comprobación</summary>

**c)** Un modelo de tamaño intermedio se destila a partir del profesor y luego enseña al estudiante. (b) es el profesor detenido antes de Cho y Hariharan. (a) es la imitación local de la lección 18. (d) es la condición de inicialización compartida de Cloud et al., que es una fuente de transferencia oculta, no un método.

</details>

3. ▢ En el experimento de la Figura 2 de Mirzadeh et al., un estudiante de 2 capas se destila de profesores de 4, 6, 8 y 10 capas. Predice la forma de la precisión del estudiante a medida que crece el tamaño del profesor.

<details markdown="1"><summary>Pista</summary>

La propia precisión del profesor sigue subiendo. ¿Cuál de los tres factores en competencia gana pronto, y cuál gana tarde?

</details>

<details markdown="1"><summary>Comprobación</summary>

Primero sube, luego cae. Con tamaños pequeños gana la mejor supervisión de un profesor más fuerte. Con tamaños grandes ganan la incapacidad del estudiante para imitar al profesor y la menor suavidad del profesor. El pico no está en el profesor más grande. Es el resultado de CNN del paper en CIFAR-10 y CIFAR-100, así que no asumas que el pico está en la misma razón para un LLM.

</details>

4. ▢ Tu equipo hace fine-tuning de un base model, encuentra que la copia afinada muestra un comportamiento no deseado, y usa esa copia para generar datos para una copia nueva del mismo base. Los datos se filtran para eliminar cualquier mención del comportamiento. ¿Qué dicen Cloud et al. sobre si el filtro basta, y qué añades?

<details markdown="1"><summary>Comprobación</summary>

Sus experimentos muestran un rasgo pasando a través de datos filtrados contra él, incluidas secuencias de números, código filtrado y chain of thought filtrada, cuando estudiante y profesor comparten base. Así que un filtro que elimina las referencias explícitas no es evidencia suficiente de un estudiante limpio. Añade una evaluación directa del estudiante en busca del comportamiento no deseado, y si la elección está abierta, trata a un estudiante de una base distinta como de menor riesgo, ya que la transmisión falló entre bases en sus pruebas, recordando que eso es una observación, no una garantía.

</details>

5. ▢ Mirzadeh et al. informan de que un asistente del profesor ayuda. Cho y Hariharan informan de que una cadena a través de un modelo intermedio no. ¿Qué haces al decidir para tu propia ejecución?

<details markdown="1"><summary>Comprobación</summary>

No tomes partido a partir de los papers. Ambos son experimentos de visión, las mejoras del asistente son pequeñas en las filas de ResNet (0.33 y 0.41 puntos sobre la destilación estándar), y las configuraciones difieren. Ejecuta una comparación controlada en tu propio par: destilación directa, un modelo intermedio, y un profesor detenido antes o una destilación detenida antes. Mide frente a un baseline entrenado desde cero y frente al acuerdo con el profesor, como en la lección 17.

</details>

6. ▢ El experimento de tamaño del profesor de MiniLLM mantuvo un estudiante de 125M y usó tres profesores de hasta 1.5B. ¿Qué mostró, y qué no muestra sobre la brecha de capacidad?

<details markdown="1"><summary>Comprobación</summary>

El rendimiento del estudiante se correlacionó positivamente con el tamaño del profesor a lo largo de 340M, 760M y 1.5B, así que no apareció ninguna brecha de capacidad en ese rango en esa familia. No muestra que la brecha nunca ocurra en los LLM: el rango llega como mucho a unas 12 veces el estudiante, y es un método en una familia.

</details>

## Prácticas en el mundo real

- [ ] Abre la Tabla 1 y la Tabla 3 del paper de Cho y Hariharan y escribe el error del estudiante para cada profesor con y sin detención temprana. Anota qué profesor dio el menor error de estudiante con detención temprana.
- [ ] Encuentra el profesor y el estudiante de una destilación en la que confíes y anota si comparten base model. Si lo hacen, escribe una comprobación directa de un rasgo no deseado que ejecutarías sobre el estudiante.
- [ ] Mañana: sin apuntes, escribe los tres factores en competencia de la brecha de capacidad, el método del asistente del profesor en dos frases, y la condición bajo la que apareció el aprendizaje subliminal.

## Para profundizar

- [Lo que hereda el estudiante](../reference/what-the-student-inherits.md)
- [Paper: "Subliminal Learning: Language models transmit behavioral traits via hidden signals in data", Cloud et al., 2025](https://arxiv.org/abs/2507.14805)
- [Paper: "Improved Knowledge Distillation via Teacher Assistant", Mirzadeh et al., 2019](https://arxiv.org/abs/1902.03393)
- [Paper: "On the Efficacy of Knowledge Distillation", Cho and Hariharan, 2019](https://arxiv.org/abs/1910.01348)
- [Recursos](../RESOURCES.md)

---

¿No termina de quedar claro? Vuelve a leer la fuente primaria de arriba, ya que esta lección la comprime y en la compresión es donde se escapa la comprensión. Consulta el [glosario](../GLOSSARY.md) por si algún término te resultó resbaladizo.

Si lo poco claro es la propia lección y no el material, eso es un defecto: [abre un issue](https://github.com/TokenCemetery/teach/issues).
