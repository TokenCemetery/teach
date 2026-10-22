---
title: "20. Revisar la receta de alineación de otra persona"
description: "Recorre el pipeline por todas las etapas que cubrió este track, en orden, y resuelve una afirmación en disputa desde la fuente en lugar de una reexposición segura de sí misma"
type: lesson
---

# Lección 20. Revisar la receta de alineación de otra persona

**Vínculo con la misión:** Esto cierra el arco. Cada etapa anterior produjo una cosa que comprobar en el pipeline de post-training de otra persona; esta lección es la lista de comprobación, más la disciplina de resolver una confusión concreta y genuinamente común desde la fuente primaria y no desde una reexposición secundaria y segura de sí misma.
**Fuente principal:** [Paper: "DeepSeekMath: Pushing the Limits of Mathematical Reasoning in Open Language Models", Shao et al., 2024](https://arxiv.org/abs/2402.03300)
**Requisitos previos:** todas las lecciones anteriores de este track, ya que esta es la síntesis.

## Calentamiento

1. ▢ Un equipo tiene datos de preferencia y ninguna necesidad concreta de reutilizar un reward model fuera del entrenamiento. ¿Cuál de DPO y PPO es la opción por defecto más defendible, y por qué?

<details markdown="1"><summary>Comprobación</summary>

DPO. Llega a un resultado entrenado con preferencias parecido a un costo cercano al del propio SFT, y necesita solo la policy y un modelo de referencia congelado, sin reward model aparte ni bucle de RL que justificar a menos que algo concreto lo requiera.

</details>

2. ▢ ¿Qué exige "defender la elección frente a la que se descartó", además de enunciar los beneficios del método elegido?

<details markdown="1"><summary>Comprobación</summary>

Nombrar qué método más barato se consideró primero y por qué se quedó corto concretamente para la tarea, y no simplemente afirmar por qué es bueno el método elegido.

</details>

## Qué debes saber

### La lista de comprobación de la revisión: las etapas en orden

Al revisar un pipeline de post-training propuesto o existente, recórrelo por las etapas de este track en orden, y haz la misma pregunta en cada una: ¿esta elección está enunciada y justificada, o simplemente se da por supuesta?

**Etapa 1, el panorama.** ¿El pipeline indica hacia cuál del panorama de SFT/RLHF/DPO/GRPO está construyendo, y coincide eso con el comportamiento objetivo descrito, o se deja sin especificar con un "hicimos post-training del modelo" cuál de ellos se usó realmente?

**Etapa 2, SFT.** ¿Se aplica realmente el enmascarado de la pérdida en los tokens que no son del asistente (lección 3), y el chat template usado en el entrenamiento está documentado con la claridad suficiente para que el serving lo reproduzca exactamente (lección 2)? Un pipeline vago en cualquiera de las dos está expuesto a un modo de fallo real y documentado antes, no hipotético.

**Etapa 3, modelado de recompensa.** Si se entrena un reward model, ¿los datos de preferencia se recopilan como rankings descompuestos en pares, según el método de la lección 4, o como comparaciones aisladas que arriesgan el overfitting que encontraron Ouyang et al.? ¿Se comprueba el reward hacking (lección 5), idealmente con algo como un modelo de preferencia held-out, en lugar de darlo por descartado?

**Etapa 4, RLHF-PPO, si se usa.** ¿Se indica el coeficiente de la penalización KL y se reconoce su compromiso (lección 6)? ¿El pipeline nombra los modelos que ejecuta a la vez y sus tamaños (lección 8), dado lo directamente que la escala del reward model y de la función de valor afectó a la propia estabilidad de Ouyang et al.?

**Etapa 5, DPO, si se usa.** ¿Se identifica con claridad el modelo de referencia, y se indica el papel de beta (el mismo compromiso de intensidad KL que el de PPO, según la lección 10) en lugar de dejarlo como un hiperparámetro sin explicar?

**Etapa 6, GRPO, si se usa.** ¿La recompensa por salida es la puntuación de un modelo entrenado o una comprobación verificable? Esta distinción importa lo bastante como para merecer su propia comprobación, que se cubre directamente más abajo.

**Etapa 7, entrenamiento de razonamiento, si se usa.** ¿El comportamiento de razonamiento extendido se atribuye a lo que lo produjo realmente (RL contra una recompensa, verificable o no), en lugar de describirse como algo programado explícitamente?

**Etapa 8, ajuste de seguridad, si se usa.** ¿El pipeline indica si el feedback de inocuidad vino de personas o de un modelo (lección 15), y si el rendimiento se compara con un baseline de feedback humano, esa comparación se informa realmente, según el precedente del propio Bai et al., en lugar de darse por favorable?

**Etapa 9, evaluación.** ¿El impuesto de alineación se mide por benchmark y no como un único número colapsado (lección 17), y hay una comprobación de sobrerrechazo o de sesgo del juez junto a la puntuación destacada de seguridad o de preferencia que se informe (lección 18)?

Un pipeline que responde a todo esto con una elección enunciada y defendible es un pipeline que ha hecho el trabajo que describe este track. Un pipeline que responde a varias con silencio no lo ha hecho, sea cual sea el aspecto de sus números finales de benchmark.

### Resolver una afirmación en disputa desde la fuente, no desde una entrada de blog

Una confusión concreta y fácil de cometer merece recorrerse directamente, porque las propias notas de la etapa 6 de este track tuvieron que detectarla mientras se escribían. A veces se afirma, de pasada, que "GRPO entrena con recompensas verificables", como si ambas cosas fueran inseparables. Comprobar el propio paper de Shao et al., el que presenta GRPO, refuta directamente esto tal como se enuncia: el GRPO de DeepSeekMath entrena contra una recompensa producida por `r_φ`, un reward model explícitamente entrenado, inicializado y entrenado de la misma manera que describe la lección 4, sin ningún verificador basado en reglas ni de ground truth en ninguna parte de su método. El emparejamiento de GRPO con recompensas verificables y basadas en reglas es real y está bien documentado, pero pertenece a DeepSeek-R1 (lección 13), un paper distinto, que aplica el mecanismo relativo al grupo de GRPO a un tipo de recompensa distinto de aquel con el que se presentó GRPO. Una fuente secundaria que enuncia "GRPO usa recompensas verificables" como un hecho general sobre el algoritmo está fusionando en silencio las contribuciones de dos papers distintos en una; volver a la propia sección de método de DeepSeekMath, en lugar de fiarse de la afirmación fusionada y segura de sí misma, es lo que lo detecta. El mecanismo (ventaja relativa al grupo) y la fuente de la recompensa (comprobación verificable frente a modelo entrenado) son dos elecciones independientes, no un paquete inseparable, y un pipeline que acierta con esta distinción es un pipeline cuyo autor leyó realmente las fuentes en lugar de repetir lo que "todo el mundo sabe" sobre GRPO.

## Práctica

1. ▢ Un pipeline propuesto dice "usamos GRPO con recompensas verificables para nuestra tarea de benchmark de matemáticas" y cita el paper de DeepSeekMath como su única fuente. ¿Es esta cita fiel a lo que describe realmente el propio método de DeepSeekMath?

<details markdown="1"><summary>Comprobación</summary>

No del todo. El GRPO de DeepSeekMath entrena contra una recompensa de un reward model entrenado, no contra una comprobación verificable basada en reglas. El emparejamiento de recompensa verificable con GRPO es la contribución de DeepSeek-R1, un paper distinto. El método real del pipeline (GRPO con una recompensa verificable) puede muy bien ser razonable, pero citar solo DeepSeekMath como su fuente atribuye mal de dónde viene esa combinación concreta.

</details>

2. ▢ Un documento de pipeline dice solo "aplicamos RLHF" sin más detalle. Con la lista de comprobación de esta lección, nombra dos cosas concretas que esa afirmación deja sin enunciar y por las que un revisor debería preguntar.

<details markdown="1"><summary>Comprobación</summary>

Cualesquiera dos de estas: el coeficiente de la penalización KL y si se consideró su compromiso; los tamaños de los modelos implicados (policy, referencia, reward model, función de valor) y si la escala del reward model se eligió deliberadamente; cómo se recopilaron los datos de preferencia y si se comprobó el reward hacking; si se midió el impuesto de alineación resultante, y contra qué benchmarks.

</details>

3. ▢ Un pipeline informa de una puntuación alta de seguridad de una evaluación con LLM-as-judge sin ningún otro detalle. Según la lección 18 y la comprobación de la etapa 9 de esta lección, ¿qué debería pedir un revisor antes de fiarse de esa puntuación?

<details markdown="1"><summary>Comprobación</summary>

Si se comprobó la calibración del juez frente a sesgos conocidos (de posición, de verbosidad), y si existe una comprobación de sobrerrechazo junto a la puntuación de seguridad, de modo que una puntuación alta refleje seguridad genuina y no un rechazo generalizado ni un juez explotable.

</details>

## Prácticas en el mundo real

- [ ] Busca un informe técnico de post-training real y publicado y pásalo por la lista de comprobación de esta lección, etapa por etapa, y anota qué puntos están enunciados explícitamente y cuáles se dejan en silencio.
- [ ] Busca una afirmación sobre métodos de post-training (DPO, PPO, GRPO o RLAIF) enunciada con seguridad en una entrada de blog, un tutorial o una respuesta de foro, y contrástala con el paper primario al que debería remontarse. Anota si se sostiene, es una simplificación o es una confusión genuina como el ejemplo de GRPO de esta lección.
- [ ] Mañana: escribe una reseña breve, de tres a cinco frases, de un pipeline de post-training real o hipotético, nombrando al menos una elección concreta que cuestionarías y qué pedirías que justificara la persona que la defiende.

## Para profundizar

- [Paper: "DeepSeekMath: Pushing the Limits of Mathematical Reasoning in Open Language Models", Shao et al., 2024](https://arxiv.org/abs/2402.03300)
- [Recursos](../RESOURCES.md)

---

¿No termina de quedar claro? Vuelve a leer la fuente primaria de arriba, ya que esta lección la comprime y en la compresión es donde se escapa la comprensión. Consulta el [glosario](../GLOSSARY.md) por si algún término te resultó resbaladizo.

Si lo poco claro es la propia lección y no el material, eso es un defecto: [abre un issue](https://github.com/TokenCemetery/teach/issues).
