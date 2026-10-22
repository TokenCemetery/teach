---
title: "15. Constitutional AI: feedback de un modelo, no de una persona"
description: "Cero etiquetas humanas de daño, una lista escrita de principios en su lugar, y un asistente que explica sus objeciones en lugar de esquivarlas"
type: lesson
---

# Lección 15. Constitutional AI: feedback de un modelo, no de una persona

**Vínculo con la misión:** "Poder decir de dónde vino el feedback (humano o de IA) en un pipeline de ajuste de seguridad dado y qué compensa eso" es el punto de Cómo se ve el éxito al que sirve esta etapa. Esta lección cubre el método de dos fases de Constitutional AI; la lección 16 cubre lo bien que se sostiene el feedback de IA frente al feedback humano en una comparación directa y controlada.
**Fuente principal:** [Paper: "Constitutional AI: Harmlessness from AI Feedback", Bai et al., 2022](https://arxiv.org/abs/2212.08073)
**Requisitos previos:** [Lección 14](0014-distilling-a-reasoning-model-down.md)

## Calentamiento

1. ▢ Según la propia comparación de 32B de DeepSeek-AI, ¿alcanzó entrenar un modelo pequeño directamente con RL a gran escala el mismo rendimiento de razonamiento que destilar de un modelo mayor ya entrenado con RL?

<details markdown="1"><summary>Comprobación</summary>

No. El RL directo sobre el modelo base de 32B alcanzó un 47.0 % de pass@1 en AIME 2024, muy por debajo del 72.6 % que alcanzó el mismo modelo base cuando en cambio se le hizo fine-tuning con las trazas de razonamiento destiladas del modelo mayor.

</details>

2. ▢ ¿Qué es una recompensa verificable, y por qué no tiene el modo de fallo de reward hacking que tiene un reward model entrenado?

<details markdown="1"><summary>Comprobación</summary>

Una recompensa producida por un verificador determinista en lugar de por un modelo aprendido; como ninguna rareza de un modelo aprendido se interpone entre la salida y su puntuación, no hay un exploit específico de un reward model que una policy pueda aprender.

</details>

## Qué debes saber

### Recuerda el fallo que este método está construido para evitar

La lección 5 cubrió un fallo real y documentado: las policies de RLHF optimizadas en exceso para la inocuidad convergieron en la evasión generalizada, y recomendaron a los usuarios buscar terapia ante casi cualquier pregunta mínimamente sensible, una manera barata de puntuar bien en un reward model de inocuidad sin ser genuinamente útil. **Constitutional AI (CAI)** está construido específicamente para producir un asistente inocuo que no tome este atajo.

### Dos fases, y dónde entra el feedback de IA en cada una

La fase supervisada, **SL-CAI**, muestrea respuestas de un modelo inicial, hace que el modelo genere una **autocrítica** y una **revisión** de su propia respuesta frente a una lista breve y escrita de principios (la "constitución" que da nombre al método), y luego hace fine-tuning del modelo original con estas respuestas autorrevisadas, SFT ordinario (etapa 2) sobre datos que el modelo produjo y mejoró por sí mismo.

La fase de aprendizaje por refuerzo, **RL-CAI**, muestrea pares de respuestas del modelo con fine-tuning de SL y, en lugar de que un anotador humano diga cuál es mejor, **usa un modelo** para emitir ese juicio. Un modelo de preferencia (el entrenamiento de Bradley-Terry de la lección 4) se entrena con este dataset de preferencias generadas por IA, y luego la policy se entrena con RL contra ese modelo de preferencia entrenado por IA exactamente como la configuración de RLHF de la lección 6 usaría uno entrenado por humanos. Bai et al. nombran directamente esta técnica general: **RL from AI Feedback (RLAIF)**.

### Cero etiquetas humanas de daño, y lo que salió de ello

Bai et al. enuncian su resultado con claridad: todo este pipeline entrena un asistente de IA "no evasivo" y "relativamente inocuo" "sin ninguna etiqueta de feedback humano sobre daños". Lo que moldea el comportamiento del modelo son los principios de la constitución, no miles de juicios humanos de nocividad. El asistente resultante se ocupa de las consultas dañinas explicando sus objeciones a ellas, en lugar de rechazarlas o esquivarlas sin más, lo cual es una respuesta directa a la sobreoptimización concreta que documentó la lección 5: un modelo cuyo entrenamiento de inocuidad recompensa implicarse de verdad con reflexión, en lugar de recompensar el rechazo más barato posible, tiene menos incentivo para colapsar en la evasión generalizada en primer lugar.

### La comparación que hace que esto merezca tomarse en serio

Bai et al. no se limitan a afirmar que esto funciona; informan de que los crowdworkers preferían el modelo resultante, "RL-CAI", frente a modelos entrenados con etiquetas de feedback humano sobre nocividad recopiladas previamente. Reemplazar las etiquetas humanas de daño por una constitución escrita y por preferencias generadas por IA no solo igualó la alternativa etiquetada por humanos; según su propia comparación, lo hizo mejor.

## Práctica

1. ▢ En SL-CAI, ¿qué hace el modelo con sus propias respuestas muestreadas antes de usarlas para el fine-tuning?

<details markdown="1"><summary>Comprobación</summary>

Genera una autocrítica de la respuesta frente a los principios de la constitución escrita, luego produce una revisión de la respuesta, y se hace fine-tuning del modelo con estas respuestas revisadas.

</details>

2. ▢ En RL-CAI, ¿qué reemplaza al anotador humano que ordinariamente juzgaría cuál de dos respuestas muestreadas es mejor?

<details markdown="1"><summary>Comprobación</summary>

Un modelo. Un sistema de IA juzga cuál de las dos respuestas es mejor, y se entrena un modelo de preferencia con este dataset de preferencias generadas por IA, y no con comparaciones etiquetadas por humanos.

</details>

3. ▢ ¿Por qué el hecho de que el asistente resultante de Constitutional AI explique sus objeciones a una petición dañina, en lugar de rechazarla sin más, aborda directamente el fallo que describió la lección 5?

<details markdown="1"><summary>Comprobación</summary>

El fallo de evasión generalizada de la lección 5 surgió porque rechazar sin más era una manera barata y de poca sofisticación de puntuar bien en un reward model de inocuidad. Un enfoque de entrenamiento cuya recompensa favorece en cambio implicarse de verdad y explicar las objeciones a una petición elimina el incentivo de ese atajo barato, ya que esquivar sin más no sería la opción de mayor puntuación.

</details>

4. ▢ Según la propia comparación de Bai et al., ¿cómo valoraron los crowdworkers a RL-CAI frente a un modelo entrenado con etiquetas de feedback humano sobre nocividad recopiladas previamente?

<details markdown="1"><summary>Comprobación</summary>

Prefirieron RL-CAI. Reemplazar las etiquetas humanas de daño por una constitución y por preferencias generadas por IA no se limitó a igualar la alternativa etiquetada por humanos en su comparación; se prefirió sobre ella.

</details>

## Prácticas en el mundo real

- [ ] Busca una "constitución" o conjunto de principios rectores publicado que se haya usado para entrenar un modelo real (varios se han publicado abiertamente), y lee tres o cuatro de sus principios. Anota si se leen como reglas específicas o como valores generales que un modelo tendría que interpretar.
- [ ] Lee el pasaje del paper de Constitutional AI (enlazado arriba) que describe el paso de autocrítica y revisión de SL-CAI, y escribe una frase que describa qué tendría que salir mal para que la autocrítica de un modelo no detectara un problema real en su propia respuesta.
- [ ] Mañana: sin mirar adelante, escribe una predicción de una frase para la lección 16: dado que Constitutional AI reemplaza las etiquetas humanas de daño por etiquetas generadas por IA para un único método, ¿esperarías que el feedback de IA funcione igual de bien en otros tipos de tareas, como el resumen o la utilidad general, y por qué sí o por qué no?

## Para profundizar

- [Paper: "Constitutional AI: Harmlessness from AI Feedback", Bai et al., 2022](https://arxiv.org/abs/2212.08073)
- [Recursos](../RESOURCES.md)

---

¿No termina de quedar claro? Vuelve a leer la fuente primaria de arriba, ya que esta lección la comprime y en la compresión es donde se escapa la comprensión. Consulta el [glosario](../GLOSSARY.md) por si algún término te resultó resbaladizo.

Si lo poco claro es la propia lección y no el material, eso es un defecto: [abre un issue](https://github.com/TokenCemetery/teach/issues).
