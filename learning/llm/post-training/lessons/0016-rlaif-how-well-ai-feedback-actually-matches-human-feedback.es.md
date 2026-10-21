---
title: "16. RLAIF: cuánto coincide realmente el feedback de IA con el feedback humano"
description: "Un modelo que juzga sus propias salidas, a su propio tamaño, aun así superó al supervised fine-tuning simple"
type: lesson
---

# Lección 16. RLAIF: cuánto coincide realmente el feedback de IA con el feedback humano

**Vínculo con la misión:** "Poder decir de dónde vino el feedback (humano o de IA) en un pipeline de ajuste de seguridad dado y qué compensa eso" es el punto de Cómo se ve el éxito al que sirve esta etapa. La lección 15 cubrió un método construido sobre feedback de IA; esta lección cubre la comparación directa y controlada del feedback de IA frente al feedback humano en varias tareas.
**Fuente principal:** [Paper: "RLAIF: Scaling Reinforcement Learning from Human Feedback with AI Feedback", Lee et al., 2023](https://arxiv.org/abs/2309.00267)
**Requisitos previos:** [Lección 15](0015-constitutional-ai-feedback-from-a-model-not-a-human.md)

## Calentamiento

1. ▢ En RL-CAI, ¿qué reemplaza al anotador humano que ordinariamente juzgaría cuál de dos respuestas muestreadas es mejor?

<details markdown="1"><summary>Comprobación</summary>

Un modelo. Un sistema de IA juzga cuál de las respuestas es mejor, y se entrena un modelo de preferencia con este dataset de preferencias generadas por IA.

</details>

2. ▢ Según la propia comparación de Bai et al., ¿cómo valoraron los crowdworkers a RL-CAI frente a un modelo entrenado con etiquetas humanas de nocividad recopiladas previamente?

<details markdown="1"><summary>Comprobación</summary>

Prefirieron RL-CAI frente al modelo entrenado con comparaciones etiquetadas por humanos.

</details>

## Qué debes saber

### Una comparación controlada, cara a cara

Lee et al. hacen una comparación directa que los propios resultados de Constitutional AI solo insinuaban: en tres tareas distintas, resumen, generación de diálogo útil y generación de diálogo inocuo, entrenan una policy con RLHF ordinario y una segunda con **RLAIF**, un modelo de lenguaje estándar que produce las etiquetas de preferencia en lugar de una persona, manteniendo comparable todo lo demás de la configuración. Después, evaluadores humanos juzgan los resultados.

### El resultado: comparable en dos tareas, mejor en la tercera

En resumen y en generación de diálogo útil, tanto RLAIF como RLHF se prefieren con claridad sobre un baseline de SFT simple (ganándole el 63 % y el 64 % de las veces respectivamente), y una comparación directa cara a cara entre RLAIF y RLHF muestra que ambos se prefieren por igual, sin diferencia estadísticamente significativa entre ellos. En generación de diálogo inocuo, Lee et al. informan de que RLAIF en realidad **supera** a RLHF, y los evaluadores humanos lo valoran como más inocuo. En las tres tareas, reemplazar un dataset de preferencias etiquetado por humanos por uno etiquetado por IA no produjo un resultado peor; en dos tareas igualó a RLHF, y en la tercera lo superó.

### El resultado más sorprendente: un modelo que juzga a su propio tamaño, o a sí mismo

Lee et al. van más allá, hacia lo que llaman "automejora": RLAIF seguía superando al baseline de SFT simple incluso cuando el etiquetador de IA que generaba las preferencias tenía el mismo tamaño que la policy que se entrenaba o, en el caso más extremo, era exactamente el mismo checkpoint del que partía la policy. Se puede lograr que un modelo mejore usando juicios de preferencia producidos por un modelo no más capaz que el que se entrena, incluidos juicios producidos por una copia anterior de sí mismo.

### Prescindir por completo del reward model: direct-RLAIF

Lee et al. introducen una simplificación más: **direct-RLAIF (d-RLAIF)**, que prescinde por completo de entrenar un modelo de preferencia aparte y, en cambio, consulta directamente a un modelo de lenguaje estándar para obtener una puntuación de recompensa durante el propio entrenamiento con RL. Quitar del pipeline un modelo entrenado entero, el reward model que la lección 8 ya señaló como un factor de costo real en el RLHF ordinario, no perjudicó el rendimiento en sus resultados; informan de que d-RLAIF logra un mejor rendimiento que el RLAIF canónico, y no meramente un rendimiento comparable a menor costo.

### Qué defiende esto, junto con la lección 15

Entre el resultado de Constitutional AI (un pipeline de feedback de IA preferido sobre uno de feedback humano) y la comparación controlada de Lee et al. (feedback de IA que iguala o supera al feedback humano en tres tareas distintas, que se sostiene incluso con una escala reducida de etiquetador, y que tolera la eliminación de todo un reward model), la tesis de que el "feedback de IA" es un sustituto menor y de reserva del feedback humano no se sostiene bien frente a ninguno de los dos resultados. Lee et al. enuncian directamente su propia conclusión: RLAIF ofrece una posible solución a las limitaciones de escalabilidad de recopilar feedback humano, y no meramente una aproximación más barata de él.

## Práctica

1. ▢ En resumen y en generación de diálogo útil, ¿cómo se comparó el porcentaje de victorias de RLAIF frente a un baseline de SFT simple con el de RLHF, según Lee et al.?

<details markdown="1"><summary>Comprobación</summary>

Sin diferencia estadísticamente significativa: ambos ganaron al baseline de SFT en proporciones similares (63 % y 64 %), y una comparación directa cara a cara entre RLAIF y RLHF no mostró una preferencia significativa por ninguno.

</details>

2. ▢ ¿En cuál de las tres tareas que probaron Lee et al. superó RLAIF a RLHF, en lugar de limitarse a igualarlo?

<details markdown="1"><summary>Comprobación</summary>

En la generación de diálogo inocuo. Los evaluadores humanos valoraron las respuestas de RLAIF como más inocuas que las de RLHF específicamente en esta tarea.

</details>

3. ▢ ¿Qué tiene de sorprendente que RLAIF siga superando a un baseline de SFT incluso cuando el etiquetador de IA es exactamente el mismo checkpoint que la policy que se entrena?

<details markdown="1"><summary>Comprobación</summary>

Significa que los propios juicios de preferencia de un modelo sobre las salidas, de un modelo no más capaz que el que se mejora, pueden aun así producir una mejora genuina frente al supervised fine-tuning simple, sin necesitar feedback de algo más capaz ni de una persona.

</details>

4. ▢ ¿Qué elimina direct-RLAIF (d-RLAIF) del pipeline estándar de RLAIF, y qué encontraron Lee et al. sobre su rendimiento?

    - a) Elimina el propio modelo de la policy; encontraron un peor rendimiento
    - b) Elimina el modelo de preferencia/recompensa entrenado aparte, y consulta directamente a un LLM estándar para obtener una puntuación de recompensa durante el RL; encontraron un mejor rendimiento que el RLAIF canónico
    - c) Elimina por completo la fase de RL y deja solo SFT; el rendimiento no cambió
    - d) Elimina la necesidad de cualquier modelo de lenguaje, y usa en su lugar una recompensa puramente basada en reglas

<details markdown="1"><summary>Comprobación</summary>

**b)** es exactamente lo que describen e informan Lee et al. (a), (c) y (d) describen cada una un cambio distinto y no relacionado del pipeline.

</details>

## Prácticas en el mundo real

- [ ] Busca dónde expone una opción de etiquetado de preferencias con feedback de IA o con LLM como juez un framework de entrenamiento o un pipeline de investigación al que tengas acceso, y comprueba si se parece más al RLAIF canónico (un modelo de preferencia entrenado) o a direct-RLAIF (una recompensa consultada en vivo a un LLM).
- [ ] Lee el pasaje del paper de Lee et al. (enlazado arriba) que describe el resultado de "automejora" y escribe, en una frase, por qué este resultado es más sorprendente que el simple hecho de que RLAIF iguale a RLHF usando un etiquetador de IA más grande y más capaz.
- [ ] Mañana: para una tarea en la que podrías querer alinear un modelo, decide si recurrirías primero a RLHF, a RLAIF o a direct-RLAIF, y escribe una frase que nombre cuál de los resultados de esta lección (calidad comparable, automejora a escala igualada o menor costo del pipeline) motivó tu respuesta.

## Para profundizar

- [Paper: "RLAIF: Scaling Reinforcement Learning from Human Feedback with AI Feedback", Lee et al., 2023](https://arxiv.org/abs/2309.00267)
- [Paper: "Constitutional AI: Harmlessness from AI Feedback", Bai et al., 2022](https://arxiv.org/abs/2212.08073)
- [Recursos](../RESOURCES.md)

---

La etapa 8 cubrió el feedback que viene de un modelo y no de una persona, y lo bien que se sostiene en la práctica. La etapa 9 se vuelve hacia una pregunta más difícil que subyace a todo lo que ha cubierto este track: una vez alineado un modelo, ¿cómo saber si el número que mide esa alineación mide lo real?

¿No termina de quedar claro? Vuelve a leer la fuente primaria de arriba, ya que esta lección la comprime y en la compresión es donde se escapa la comprensión. Consulta el [glosario](../GLOSSARY.md) por si algún término te resultó resbaladizo.

Si lo poco claro es la propia lección y no el material, eso es un defecto: [abre un issue](https://github.com/TokenCemetery/teach/issues).
