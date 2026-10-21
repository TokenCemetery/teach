---
title: "25. Revisar una afirmación de destilación"
description: "Revisar \"nuestro modelo pequeño iguala al grande\" nombrando lo que la medición ocultó"
type: lesson
---

# Lección 25. Revisar una afirmación de destilación

**Vínculo con la misión:** La misión termina con revisar la afirmación de otra persona de que un modelo destilado "iguala al profesor". Una revisión que dice "no me fío" se ignora, y una que nombra qué parte de la medición ocultó qué, y qué costaría averiguarlo, se atiende.
**Fuente principal:** [Paper: "The False Promise of Imitating Proprietary LLMs", Gudibande et al., 2023](https://arxiv.org/abs/2305.15717), secciones 1 y 4
**Requisitos previos:** [Lección 22](0022-student-against-teacher.md), [Lección 23](0023-an-honest-distillation-eval.md), [Fidelidad](../GLOSSARY.md), [Brecha de imitación](../GLOSSARY.md)

## Calentamiento

1. ▢ La lección 17 separó dos cosas en las que un estudiante puede ser bueno. Nómbralas y di cuál encontraron Stanton et al. que era baja incluso cuando el estudiante podía igualar al profesor.

<details markdown="1"><summary>Comprobación</summary>

[Fidelidad](../GLOSSARY.md), cuán de cerca coinciden las predicciones del estudiante con las del profesor, y generalización, lo bien que lo hace el estudiante en la tarea. Stanton et al. informan de que a menudo persiste una gran discrepancia entre las distribuciones predictivas del profesor y del estudiante incluso cuando el estudiante tiene la capacidad de igualar exactamente al profesor, y de que una mejor generalización no exige una mejor fidelidad ([paper](https://arxiv.org/abs/2106.05945), resumen).

</details>

2. ▢ La lección 23 enumeró baselines que hacen defendible una cifra de "iguala al profesor". ¿Qué baseline te dice qué aportó el profesor, frente a lo que el tamaño y los datos del estudiante habrían dado de todos modos?

<details markdown="1"><summary>Comprobación</summary>

Un modelo del tamaño del estudiante entrenado sin el profesor, con los mismos datos de la tarea. Sin él, una buena puntuación puede ser lo que alcanza cualquier estudiante de ese tamaño, y el profesor se lleva el mérito de un trabajo que no hizo.

</details>

3. ▢ La lección 18 nombró la brecha de imitación. En una frase, ¿qué dice sobre la rapidez con que un estudiante cierra la brecha en estilo comparada con la capacidad?

<details markdown="1"><summary>Comprobación</summary>

La imitación con un presupuesto limitado cierra la brecha en estilo mucho más rápido que en capacidad, así que un estudiante puede sonar como su profesor mucho antes de poder hacer lo que hace el profesor.

</details>

## Qué debes saber

### Una afirmación tiene partes

"Nuestro 7B iguala al profesor" son cinco afirmaciones en una frase: un modelo, una medición, un baseline, una población de entradas y un costo. Una revisión la desmonta y pregunta de cada parte qué haría falta para que la afirmación fallara. Las revisiones más útiles también dicen qué está bien, para que el autor lo conserve.

### Qué mide un porcentaje: DistilBERT

Sanh et al. dicen que DistilBERT es un 40% más pequeño y un 60% más rápido y "conserva el 97% de sus capacidades de comprensión del lenguaje" ([paper](https://arxiv.org/abs/1910.01108), resumen). La sección 4 y la Tabla 1 dicen qué mide esa frase: las nueve tareas del benchmark GLUE, en los conjuntos de desarrollo, tras hacer fine-tuning de cada modelo, con los resultados de BERT y DistilBERT siendo medianas de 5 ejecuciones con semillas distintas. Las macro-puntuaciones impresas son 79.5 para BERT-base y 77.0 para DistilBERT, y 77.0 entre 79.5 es 96.9%.

Así que el 97% es una razón de dos promedios, en una suite de benchmarks, frente a un profesor. Por tarea, la Tabla 1 da una imagen distinta: DistilBERT puntúa 51.3 en CoLA frente a 56.3 de BERT, que es el 91.1%, y 59.9 en RTE frente a 69.3, que es el 86.4%. En WNLI puntúa 56.3 frente a 53.5, por encima del profesor. El titular no es erróneo. Es un promedio en el que se pliegan dos tareas débiles y unos cuantos empates cercanos, y un lector cuya carga de trabajo se parece a RTE debería leer la fila de RTE.

Tres datos más del paper pertenecen a una revisión. El estudiante se inicializó a partir del profesor tomando una capa de cada dos (sección 3), que es una decisión de diseño que una afirmación debería revelar. Se entrenó con el mismo corpus que BERT, así que no hay desplazamiento entre los datos del profesor y los del estudiante. Y el cómputo fue de 8 GPU V100 durante unas 90 horas (sección 3), con el profesor ya entrenado y sin contar en esa cifra.

### Lo que oculta una valoración de preferencia: Gudibande et al.

Gudibande et al. hicieron fine-tuning de modelos de 1.5B a 13B de parámetros para imitar a ChatGPT y los valoraron de dos maneras. Crowdworkers, unos 70, juzgaron 255 prompts held-out, y aproximadamente el 70% de las salidas de los modelos de imitación se calificaron como iguales o mejores que las de ChatGPT (sección 4, Figura 1 izquierda). Para limitar la fuga descartaron las consultas cuya puntuación BLEU frente a cualquier ejemplo de entrenamiento superaba el 20%, y descartaron los prompts de programación y los que no estaban en inglés que los evaluadores no podían juzgar.

Las evaluaciones automáticas específicas contaron otra historia. Los autores informan de que los modelos de imitación cerraron poco o nada de la brecha entre el base model y ChatGPT en tareas que no estaban muy respaldadas en los datos de imitación, y de que más datos de imitación no la cerraron, con algunos resultados como el conocimiento factual de Natural Questions retrocediendo (Figura 1 centro). Su explicación es que los modelos aprendieron el estilo de ChatGPT, seguro y bien estructurado, y que los evaluadores sin experiencia en el dominio ni tiempo para comprobar hechos se pierden los errores (sección 4.4).

Es el resultado de un paper, para la imitación de ChatGPT con modelos de hasta 13B de parámetros. Lo transferible no es que las valoraciones de preferencia sean inútiles. Es que una valoración mide lo que el evaluador puede juzgar, y lo que un evaluador puede juzgar en un minuto suele ser el estilo.

### Las preguntas que hacer

| Parte de la afirmación | Pregunta | Por qué importa |
|---|---|---|
| Tareas | ¿Qué tareas, y el promedio oculta las débiles? | El 97% de DistilBERT se sitúa sobre filas al 86% y al 91% |
| Población | ¿Las entradas de prueba son held-out, o salen de la distribución de destilación? | Gudibande et al. encuentran que la brecha se ve en tareas que los datos de imitación no respaldan |
| Baseline | ¿Frente a qué: el profesor, un modelo del mismo tamaño entrenado sin él, el base model? | El primero dice cuán lejos, el segundo dice qué añadió el profesor |
| Contaminación | ¿Cómo se mantuvieron los datos de prueba fuera de los prompts de destilación? | Un filtro de solapamiento BLEU es una respuesta concreta, y una afirmación sin ninguna es una laguna |
| Evaluador | ¿Humanos, un modelo juez o una métrica, y podían comprobar hechos? | Un juez o un grupo de crowdworkers puede premiar el estilo |
| Decodificación | ¿Voraz o muestreada, qué temperatura, la misma para ambos modelos? | Agarwal et al. informan de que las divergencias que buscan modos funcionaron mejor con muestreo con temperatura mientras que la elección apenas importó con decodificación voraz ([paper](https://arxiv.org/abs/2306.13649), sección 4.1), así que la decodificación puede cambiar la clasificación |
| Ruido | ¿Cuántas semillas, y cuán grande es la brecha frente a la dispersión entre ejecuciones? | DistilBERT informa de medianas de 5 ejecuciones, y muchas afirmaciones informan de una |
| Costo | ¿Se cuentan la inferencia del profesor, la generación de datos y el filtrado? | Las 90 horas de GPU de DistilBERT excluyen el preentrenamiento del profesor |

Dos de las filas son preguntas sobre lo que falta en el escrito, no sobre lo que está mal en él. Trata una respuesta ausente como un punto abierto, no como un fallo: anótala y pídela.

### Escribir la revisión

Di primero lo que está bien. Enuncia cada parte oculta como un costo: "el promedio oculta las tareas donde cayó 10 puntos o más" es concreto, y "no me fío del promedio" no lo es. Luego nombra la medición que lo resolvería, con su precio, para que el autor pueda decir sí o no. Los baselines, las tareas held-out y las comprobaciones de contaminación de la lección 23 son las respuestas habituales.

## Práctica

1. ▢ Predice cuáles dos de las nueve tareas de GLUE de DistilBERT tienen la menor razón estudiante a profesor, y luego ejecuta esto con los números de la Tabla 1.

    ```python
    bert = dict(CoLA=56.3, MNLI=86.7, MRPC=88.6, QNLI=91.8, QQP=89.6,
                RTE=69.3, SST2=92.7, STSB=89.0, WNLI=53.5)
    distil = dict(CoLA=51.3, MNLI=82.2, MRPC=87.5, QNLI=89.2, QQP=88.5,
                  RTE=59.9, SST2=91.3, STSB=86.9, WNLI=56.3)
    for task in sorted(bert, key=lambda t: distil[t] / bert[t]):
        print(f"{task:5s} {100 * distil[task] / bert[task]:.1f}")
    print(f"mean of entries {sum(bert.values()) / 9:.1f} and {sum(distil.values()) / 9:.1f}")
    ```

<details markdown="1"><summary>Pista</summary>

Busca las tareas donde el profesor puntuó muy por debajo de 100 y el estudiante cayó más.

</details>

<details markdown="1"><summary>Comprobación</summary>

RTE con 86.4 y CoLA con 91.1 son las más bajas, y WNLI con 105.2 es la más alta. La última línea imprime 79.7 y 77.0. El paper imprime 79.5 para BERT-base, cerca de la media de sus propias nueve entradas pero no igual, y no pude establecer por qué. Cualquiera de las dos cifras da alrededor del 97% en total, que es el punto: recalcula un titular a partir de la tabla antes de citarlo.

</details>

2. ▢ Un paper informa de que crowdworkers calificaron alrededor del 70% de las salidas de un estudiante como iguales o mejores que las de su profesor. ¿Qué concluyes sobre la capacidad, y qué pedirías?

<details markdown="1"><summary>Comprobación</summary>

Nada firme sobre la capacidad. En Gudibande et al. el mismo tipo de valoración coexistió con poco cierre de la brecha en tareas que los datos de imitación no respaldaban, porque los evaluadores premian el estilo que el estudiante copió. Pide evaluaciones automáticas específicas sobre tareas held-out, y evaluadores o una comprobación que puedan verificar hechos.

</details>

3. ▢ Afirmación hipotética: "Nuestro estudiante de 7B iguala al profesor. En 500 prompts, un modelo juez prefirió al estudiante o empató en el 62% de las comparaciones". Los prompts vinieron del mismo generador que los prompts de destilación, la decodificación fue voraz para el estudiante y muestreada para el profesor, y el costo no se indica. Enumera las preguntas que harías, primero las que más cambian la decisión.

<details markdown="1"><summary>Comprobación</summary>

Primero, población: los prompts del generador de destilación están dentro de la distribución, así que pide tareas held-out. Segundo, decodificación: los dos modelos deberían decodificarse de la misma manera, porque el ajuste puede mover la clasificación. Tercero, el juez: qué modelo, comprobado en busca de sesgo de estilo, y una tasa de empates separada de la preferencia. Cuarto, baseline: un modelo del mismo tamaño entrenado sin el profesor. Por último, costo: la generación y el filtrado del profesor contados. Di también qué está bien: una comparación juzgada con 500 prompts es una primera mirada razonable.

</details>

4. ▢ ¿Qué comprobación es evidencia de que los prompts de destilación no se filtraron al conjunto de prueba?

    - a) Un juez mayor que la puntúe más alto
    - b) Un filtro de solapamiento sobre los prompts de prueba
    - c) Promediar las puntuaciones sobre varias semillas
    - d) Una ejecución más larga con salidas del profesor

<details markdown="1"><summary>Comprobación</summary>

**b)** Comprueba lo que está en cuestión, como hicieron Gudibande et al. con un filtro BLEU del 20% frente a cualquier ejemplo de entrenamiento. (a) y (c) cambian cómo se juzga o se promedia la puntuación, no si se vieron las entradas. (d) no prueba el solapamiento, y más de los mismos prompts puede aumentarlo.

</details>

5. ▢ Dos papers comparan la KL directa y la inversa para estudiantes. Uno evalúa con decodificación voraz y encuentra poca diferencia, el otro muestrea con una temperatura alta y encuentra la KL inversa claramente mejor. ¿Pueden tener razón ambos, y qué compruebas primero?

<details markdown="1"><summary>Comprobación</summary>

Sí. Agarwal et al. informan de que las divergencias que buscan modos funcionaron mejor con muestreo con temperatura y de que la elección apenas importó con decodificación voraz, que es la misma división. Comprueba primero el ajuste de decodificación de cada evaluación, luego la tarea y los tamaños de modelo, antes de tratar a los dos como una contradicción.

</details>

## Prácticas en el mundo real

- [ ] Encuentra una model card o una entrada de blog que afirme que un modelo pequeño iguala a uno grande, y escribe una línea por cada fila de la tabla de preguntas: la respuesta que da la entrada, o "no se indica".
- [ ] Recalcula un porcentaje de una tabla de resultados de esa entrada, usando los propios números de la tabla, y anota si se reproduce.
- [ ] Mañana: escribe la revisión de esa afirmación en cinco frases, empezando por lo que está bien y terminando con la única medición que pedirías.

## Para profundizar

- [Lista de revisión de destilación](../reference/distillation-review-checklist.md)
- [Dimensionar y medir](../reference/sizing-and-measuring.md)
- [Paper: "The False Promise of Imitating Proprietary LLMs", Gudibande et al., 2023](https://arxiv.org/abs/2305.15717)
- [Paper: "DistilBERT, a distilled version of BERT: smaller, faster, cheaper and lighter", Sanh et al., 2019](https://arxiv.org/abs/1910.01108)
- [Paper: "On-Policy Distillation of Language Models: Learning from Self-Generated Mistakes", Agarwal et al., 2023](https://arxiv.org/abs/2306.13649)
- [Recursos](../RESOURCES.md)

---

¿No termina de quedar claro? Vuelve a leer la fuente primaria de arriba, ya que esta lección la comprime y en la compresión es donde se escapa la comprensión. Consulta el [glosario](../GLOSSARY.md) por si algún término te resultó resbaladizo.

Si lo poco claro es la propia lección y no el material, eso es un defecto: [abre un issue](https://github.com/TokenCemetery/teach/issues).
