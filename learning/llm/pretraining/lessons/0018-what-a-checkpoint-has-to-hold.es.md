---
title: "18. Qué tiene que guardar un checkpoint"
description: "Un checkpoint que solo guarda los pesos no puede reanudar una ejecución con exactitud, y elegir cada cuánto guardar es una disyuntiva en sí misma"
type: lesson
---

# Lección 18. Qué tiene que guardar un checkpoint

**Vínculo con la misión:** "Puedes diseñar un esquema de checkpointing que acote el progreso perdido tras la falla de un nodo" es el punto de Cómo se ve el éxito al que sirve esta etapa. Esta lección cubre qué necesita contener un checkpoint y cada cuánto guardar uno; la Lección 19 cubre qué ocurre realmente cuando falla un nodo a mitad de una ejecución.
**Fuente principal:** [Paper: "OPT: Open Pre-trained Transformer Language Models", Zhang et al., 2022](https://arxiv.org/abs/2205.01068)
**Requisitos previos:** [Lección 17](0017-warmup-decay-and-growing-the-batch-mid-run.md)

## Calentamiento

1. ▢ Según Rae et al., ¿recibe un modelo más grande un learning rate máximo más alto o más bajo que uno más pequeño, a igualdad de lo demás?

<details markdown="1"><summary>Comprobación</summary>

Un learning rate máximo más bajo. Rae et al. enuncian directamente que al aumentar el tamaño del modelo reducen el learning rate máximo que usa el programa.

</details>

2. ▢ ¿Qué hace el clipping por norma global del gradiente con un gradiente cuya norma supera el umbral de clipping?

<details markdown="1"><summary>Comprobación</summary>

Reescala todo el vector de gradiente de forma proporcional para que su norma sea igual al umbral, lo que acota cuánto puede crecer una sola actualización, en lugar de descartar el gradiente o cambiar el learning rate.

</details>

## Qué debes saber

### Un checkpoint es más que los pesos

Guardar solo los parámetros de un modelo no basta para reanudar el entrenamiento exactamente donde se dejó. Reanudar correctamente una ejecución de entrenamiento necesita, como mínimo: los **parámetros** del modelo; el **estado del optimizador** (para Adam, el momento y la varianza que contó la Lección 8, sin los cuales el optimizador reinicia en frío); el **número de paso y la posición en el programa del learning rate**, para que el warmup y el decay (Lección 17) continúen desde el punto correcto en lugar de reiniciarse; y, para una reproducibilidad exacta, la **posición del data loader y el estado del generador de números aleatorios**, para que la ejecución no reprocese ni se salte datos en silencio alrededor del punto de reinicio. Un checkpoint al que le falte cualquiera de estos elementos no falla de forma ruidosa; reanuda en una ejecución que parece haber continuado, mientras entrena en silencio de una manera algo distinta de como lo habría hecho una ejecución sin interrupciones.

### Por qué la frecuencia de los checkpoints es una disyuntiva en sí misma

Por completo que sea el contenido de un checkpoint, guardar uno cuesta tiempo y almacenamiento: escribir en almacenamiento duradero el estado completo de un modelo grande lleva tiempo real, durante el cual la ejecución de entrenamiento normalmente queda en pausa o al menos no avanza a pleno rendimiento, y cada checkpoint ocupa espacio real en disco, sobre todo si se conservan varios recientes y no solo el último. Hacer checkpoints con más frecuencia acota cuánto progreso puede destruir una falla, ya que solo está en riesgo el trabajo posterior al último checkpoint. Hacerlos con menos frecuencia gasta menos tiempo y almacenamiento en los propios checkpoints, al costo de perder más progreso ante la misma falla. Ningún extremo es correcto en general: la frecuencia adecuada depende de con qué frecuencia se esperan realmente las fallas, sopesada frente a lo caro que es realmente escribir cada checkpoint.

### Con qué frecuencia ocurren realmente las fallas, en una ejecución real

El relato de Zhang et al. sobre el entrenamiento de OPT-175B vuelve concreto, y no hipotético, el lado de "con qué frecuencia se esperan fallas" de esa disyuntiva. A lo largo de unos dos meses de entrenamiento, las fallas de hardware contribuyeron a al menos 35 reinicios manuales y a la rotación de más de 100 hosts, y los autores estiman más de 70 reinicios automáticos adicionales además de eso, en una sola ejecución de entrenamiento. Eso es bastante más de un reinicio cada dos días de media, sostenido durante toda la duración de la ejecución. Un esquema de checkpointing construido sobre el supuesto de que las fallas son sucesos raros y ocasionales habría sido un grave error para esta ejecución; un esquema que asume que las fallas son una parte rutinaria y esperada del proceso, y hace checkpoints en consecuencia, es lo que de verdad necesita una ejecución a esta escala.

## Práctica

1. ▢ Un equipo reanuda una ejecución de entrenamiento desde un checkpoint que guardó los parámetros del modelo pero no el estado del optimizador. ¿Qué sale mal, aunque la ejecución reanudada parezca por lo demás continuar con normalidad?

<details markdown="1"><summary>Comprobación</summary>

El optimizador reinicia en frío: para Adam, el momento y la varianza acumulados antes del checkpoint se pierden, así que las primeras actualizaciones tras reanudar se comportan de forma distinta de como lo habrían hecho si el entrenamiento nunca se hubiera interrumpido, aunque los propios parámetros sean correctos.

</details>

2. ▢ ¿Por qué hacer checkpoints con más frecuencia reduce la cantidad de progreso que puede destruir una falla, y qué cuesta obtener ese beneficio?

<details markdown="1"><summary>Comprobación</summary>

Solo el trabajo hecho desde el checkpoint más reciente está en riesgo si ocurre una falla, así que un checkpoint más reciente acota la pérdida con más precisión. El costo es el tiempo empleado en escribir cada checkpoint (durante el cual el entrenamiento normalmente queda en pausa) y el almacenamiento que ocupa cada uno, y ambos se acumulan más deprisa cuanto más a menudo se guardan checkpoints.

</details>

3. ▢ Zhang et al. informan de al menos 35 reinicios manuales, más de 100 hosts rotados y una estimación de más de 70 reinicios automáticos a lo largo de unos dos meses de entrenamiento de OPT-175B. ¿A favor de qué aboga esta cifra en un esquema de checkpointing para una ejecución de escala y duración similares?

<details markdown="1"><summary>Comprobación</summary>

A favor de tratar las fallas como rutinarias y frecuentes, no como excepciones raras, al elegir cada cuánto hacer checkpoints. Con bastante más de un reinicio cada dos días sostenido durante toda la ejecución, un esquema de checkpointing construido para fallas ocasionales dejaría demasiado progreso expuesto en cualquier momento dado.

</details>

## Prácticas en el mundo real

- [ ] Busca cómo define un framework de entrenamiento al que tengas acceso qué entra en un checkpoint guardado (parámetros, estado del optimizador, número de paso, estado del RNG), y comprueba si alguno de los cuatro que nombra esta lección falta o es opcional en su configuración por defecto.
- [ ] Lee la sección "Hardware Failures" del paper de OPT (enlazado arriba) y escribe una oración que describa el procedimiento operativo que siguieron los autores una vez detectada una falla, antes de que la Lección 19 lo cubra directamente.
- [ ] Mañana: para una ejecución hipotética a tu elección (de cualquier duración y escala), estima una frecuencia de checkpoints que elegirías, y escribe una oración que la justifique frente tanto al costo de hacer checkpoints con demasiada frecuencia como al riesgo de hacerlos con demasiada poca.

## Para profundizar

- [Paper: "OPT: Open Pre-trained Transformer Language Models", Zhang et al., 2022](https://arxiv.org/abs/2205.01068)
- [Recursos](../RESOURCES.md)

---

¿No termina de quedar claro? Vuelve a leer la fuente primaria de arriba, ya que esta lección la comprime y en la compresión es donde se escapa la comprensión. Consulta el [glosario](../GLOSSARY.md) por si algún término te resultó resbaladizo.

Si lo poco claro es la propia lección y no el material, eso es un defecto: [abre un issue](https://github.com/TokenCemetery/teach/issues).
