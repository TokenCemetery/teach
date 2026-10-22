---
title: "Post-training de LLM"
description: "Alinea un modelo base: SFT, modelado de recompensa, RLHF, DPO y GRPO, y saber cuál elegir"
type: topic
---

# Post-training de LLM

Ser capaz de llevar un modelo base preentrenado a un asistente alineado que sigue instrucciones: escribir correctamente los objetivos de SFT, de recompensa y de preferencia, elegir entre RLHF-PPO, DPO y GRPO según el presupuesto y los datos de un equipo, y defender esa elección, incluido lo que costó en impuesto de alineación y dónde queda expuesta al reward hacking.

**Última lección:** [0020. Revisar la receta de alineación de otra persona](lessons/0020-reviewing-someone-elses-alignment-recipe.md)

## Cómo se ve el éxito

- Escribir un bucle de entrenamiento de SFT que enmascare la pérdida en los tokens que no son del asistente, y explicar qué se rompe en un modelo de chat entrenado sin esa máscara.
- Entrenar un reward model con pares de preferencia usando la pérdida de Bradley-Terry, e identificar una completion con reward hacking producida por una policy entrenada contra él.
- Derivar el objetivo de RLHF (recompensa menos una penalización KL frente a un modelo de referencia) y decir qué le pasa a la policy cuando se afloja la penalización KL.
- Derivar la recompensa implícita de DPO a partir de los mismos datos de preferencia que usa RLHF, y decir a qué renuncia al quitar el bucle de RL.
- Explicar la ventaja relativa al grupo en GRPO y por qué una recompensa verificable (un test unitario, una respuesta matemática comprobada) cambia aquello a lo que puede apuntar el entrenamiento con RL.
- Dados los datos, el presupuesto y el comportamiento objetivo de un equipo, elegir entre SFT solo, DPO, RLHF-PPO y GRPO, y defender la elección frente a la que se descartó.
- Leer los resultados de evaluación de un modelo alineado y separar una mejora genuina de capacidad de un artefacto del reward hacking o del sesgo del juez.

## Restricciones

- Primero el algoritmo, no un repaso de papers. Cada etapa enseña un objetivo de entrenamiento desde su función de pérdida hacia fuera, qué se maximiza y qué hace el gradiente, en lugar de resumir una lista de papers; los papers anclan cada etapa como su fuente principal.
- Prácticas a pequeña escala: los labs ejecutan SFT y DPO sobre un modelo abierto pequeño, con la misma disciplina de escala que usa `llm/finetuning`, y de ahí se razona sobre lo que informan los papers de frontera citados.
- Se asume `llm/transformers` (pérdida de entropía cruzada, el paso hacia atrás, AdamW) y familiaridad con la mecánica de adapters de `llm/finetuning`, porque este track la reutiliza en lugar de volver a derivar la eficiencia de parámetros.
- Ninguna lección entrena un pipeline de RLHF completo de extremo a extremo a escala de frontera; el costo de PPO se muestra a pequeña escala y luego se razona a la escala que informan los papers citados.

## Fuera de alcance

- La mecánica de eficiencia de parámetros (rango y alpha de LoRA, QLoRA, DoRA, módulos objetivo): consulta [`llm/finetuning`](../../llm/finetuning/). Este track es dueño del objetivo de entrenamiento; `llm/finetuning` es dueño de cómo se aplica a menos parámetros.
- La pérdida de entropía cruzada, el paso hacia atrás y AdamW: consulta [`llm/transformers`](../../llm/transformers/). Se asumen aquí, no se vuelven a enseñar.
- La mecánica de LLM como juez y la metodología de evaluación humana: consulta [`llm/evals`](../../llm/evals/). Aquí se tratan solo como la única capacidad que necesita un modelo alineado, juzgar si el entrenamiento de alineación ayudó, y se enlazan en lugar de reexponerse.
- Dar prompts a un modelo de razonamiento, o construir un agente a su alrededor: consulta [`llm/agents`](../../llm/agents/) (lección 0017). Este track cubre cómo el entrenamiento con RL produce el comportamiento de razonamiento, no cómo usarlo desde fuera.
- Entrenar un modelo desde una inicialización aleatoria: consulta [`llm/pretraining`](../../llm/pretraining/).
- La destilación en general, más allá del caso del modelo de razonamiento: consulta [`llm/distillation`](../../llm/distillation/). La lección 0014 de aquí sigue siendo el caso del modelo de razonamiento y enlaza allí para el método general.
- Usar desde fuera el seguimiento de instrucciones y el razonamiento, mediante prompts: consulta [`llm/prompting`](../../llm/prompting/). Este track cubre cómo se entrenan esos comportamientos.

## El arco

Diez etapas, desde ningún conocimiento previo hasta el criterio de un senior. No es una lista de lecciones: una etapa abarca varias lecciones y los límites son difusos.

| Etapa | Lecciones | Cubre | Terminada cuando |
| --- | --- | --- | --- |
| 1. Qué aporta el post-training | 0001 a 0001 | Modelo base frente a modelo instruct/chat, el panorama de SFT/RLHF/DPO/GRPO | Puedes situar el comportamiento de un modelo alineado dado frente a la etapa de post-training que lo produjo |
| 2. SFT | 0002 a 0003 | Datasets de instrucciones, chat templates, enmascarado de la pérdida en tokens que no son del asistente | Puedes escribir un bucle de SFT con el enmascarado de la pérdida correcto y explicar qué se rompe sin él |
| 3. Modelado de recompensa | 0004 a 0005 | Recopilación de datos de preferencia, la pérdida de Bradley-Terry, reward hacking | Puedes entrenar un reward model e identificar una completion con reward hacking contra él |
| 4. RLHF con PPO | 0006 a 0008 | El objetivo de RL, la penalización KL frente a un modelo de referencia, por qué PPO es caro e inestable | Puedes derivar el objetivo de RLHF y decir qué le hace a la policy aflojar la penalización KL |
| 5. Direct Preference Optimization | 0009 a 0010 | La recompensa implícita de DPO, qué descarta frente a PPO y por qué suele estar bien | Puedes derivar la recompensa implícita de DPO y decir a qué renuncia frente a PPO |
| 6. GRPO y RL con recompensas verificables | 0011 a 0012 | Ventaja relativa al grupo, por qué encaja con matemáticas y código | Puedes explicar la ventaja relativa al grupo y por qué una recompensa verificable cambia aquello a lo que puede apuntar el RL |
| 7. Modelos de razonamiento | 0013 a 0014 | RL con chain-of-thought, qué cambió DeepSeek-R1, destilar un modelo de razonamiento a uno más pequeño | Puedes decir cómo se produjo el comportamiento de un modelo de razonamiento, no solo cómo darle prompts |
| 8. Seguridad y ajuste de rechazo | 0015 a 0016 | Datos de red-teaming, Constitutional AI, RLAIF | Puedes decir de dónde vino el feedback (humano o de IA) en un pipeline de ajuste de seguridad dado y qué compensa eso |
| 9. Evaluar un modelo alineado | 0017 a 0018 | Impuesto de alineación, detección de reward hacking, enlace con `llm/evals` | Puedes separar una mejora genuina de capacidad de un artefacto de reward hacking o de sesgo del juez |
| 10. Criterio | 0019 a 0020 | DPO frente a PPO frente a GRPO según el presupuesto, cuándo basta SFT solo, revisar la receta de alineación de otra persona | Se confía en ti para tomar la decisión y explicársela a otra persona |

## Lecciones

Recórrelas en orden.

| # | Lección | Enseña |
|---|---|---|
| [0001](lessons/0001-what-post-training-buys.md) | Qué aporta el post-training | Un modelo alineado 100 veces más pequeño superó a un modelo base sin procesar en hacer lo que los usuarios realmente querían |
| [0002](lessons/0002-instruction-data-and-the-chat-template.md) | Datos de instrucciones y el chat template | Un token especial marca dónde termina un prompt y empieza una respuesta, y esa frontera tiene que coincidir en el entrenamiento y en el serving |
| [0003](lessons/0003-loss-masking-on-non-assistant-tokens.md) | Enmascarado de la pérdida en tokens que no son del asistente | Pon a cero la pérdida sobre el prompt, o gastarás señal de gradiente en enseñar al modelo a predecir texto que no generó |
| [0004](lessons/0004-training-a-reward-model-the-bradley-terry-loss.md) | Entrenar un reward model: la pérdida de Bradley-Terry | Un reward model nunca ve una puntuación absoluta en el entrenamiento, solo cuál de dos completions le gustó más a una persona |
| [0005](lessons/0005-reward-hacking.md) | Reward hacking | Una policy aprendió a decir "No puedo responder a eso" a casi todo, porque eso puntuaba bien sin ser genuinamente útil ni inocuo |
| [0006](lessons/0006-the-rlhf-objective-reward-minus-a-kl-penalty.md) | El objetivo de RLHF: recompensa menos una penalización KL | Un término persigue la puntuación del reward model; un segundo término es la correa que impide que la policy se escape con ella |
| [0007](lessons/0007-ppo-why-the-update-gets-clipped.md) | PPO: por qué se recorta la actualización | Una gran victoria en un lote de datos muestreados no es evidencia fiable para dar un gran paso; PPO se niega a creérsela del todo |
| [0008](lessons/0008-why-ppo-is-expensive-and-unstable.md) | Por qué PPO es caro e inestable | Cuatro modelos, y no uno, tienen que caber a la vez en memoria, y los dos que peor escalan son exactamente los que añade RLHF |
| [0009](lessons/0009-dpos-implicit-reward-why-the-partition-function-cancels.md) | La recompensa implícita de DPO: por qué se cancela la función de partición | Un término de normalización intratable se interpone entre una recompensa y su policy óptima, hasta que una diferencia de dos recompensas lo hace desaparecer |
| [0010](lessons/0010-the-dpo-loss-and-what-it-drops-relative-to-ppo.md) | La pérdida de DPO y qué descarta frente a PPO | Una pérdida, dos modelos, ningún bucle de muestreo, y el mismo beta que habría usado una penalización KL |
| [0011](lessons/0011-grpo-group-relative-advantage-instead-of-a-value-function.md) | GRPO: ventaja relativa al grupo en lugar de una función de valor | Muestrea varias respuestas a la misma pregunta y deja que la propia dispersión de recompensas del grupo diga cuáles fueron mejores |
| [0012](lessons/0012-verifiable-rewards-when-a-checker-replaces-the-reward-model.md) | Recompensas verificables: cuando un verificador reemplaza al reward model | Un reward model entrenado es una conjetura de lo que preferiría una persona; un test unitario o una respuesta que coincide no es una conjetura en absoluto |
| [0013](lessons/0013-chain-of-thought-rl-what-deepseek-r1-zero-did-with-rule-based-rewards.md) | RL con chain-of-thought: lo que hizo DeepSeek-R1-Zero con recompensas basadas en reglas | Sin reward model aprendido, sin un paso de SFT previo, y aun así emergió el razonamiento extendido porque cada vez acertaba más respuestas |
| [0014](lessons/0014-distilling-a-reasoning-model-down.md) | Destilar un modelo de razonamiento a un tamaño menor | Entrenar un modelo de 32B directamente con RL perdió frente a simplemente hacerle fine-tuning con las trazas de razonamiento de un modelo mayor |
| [0015](lessons/0015-constitutional-ai-feedback-from-a-model-not-a-human.md) | Constitutional AI: feedback de un modelo, no de una persona | Cero etiquetas humanas de daño, una lista escrita de principios en su lugar, y un asistente que explica sus objeciones en lugar de esquivarlas |
| [0016](lessons/0016-rlaif-how-well-ai-feedback-actually-matches-human-feedback.md) | RLAIF: cuánto coincide realmente el feedback de IA con el feedback humano | Un modelo que juzga sus propias salidas, a su propio tamaño, aun así superó al supervised fine-tuning simple |
| [0017](lessons/0017-measuring-the-alignment-tax.md) | Medir el impuesto de alineación | El impuesto no aparece en todas partes a la vez, e incluso un eje midió una mejora en lugar de una pérdida |
| [0018](lessons/0018-reward-hacking-after-the-fact.md) | Reward hacking a posteriori | Un reward model held-out puede detectar la deriva durante el entrenamiento; un modelo terminado necesita otro tipo de comprobación |
| [0019](lessons/0019-choosing-between-sft-dpo-ppo-and-grpo.md) | Elegir entre SFT, DPO, PPO y GRPO | Cada método se gana su costo añadido sobre el anterior solo cuando el más barato realmente no puede expresar el comportamiento objetivo |
| [0020](lessons/0020-reviewing-someone-elses-alignment-recipe.md) | Revisar la receta de alineación de otra persona | Recorre el pipeline por todas las etapas que cubrió este track, en orden, y resuelve una afirmación en disputa desde la fuente en lugar de una reexposición segura de sí misma |

## Referencia

- [Glosario](GLOSSARY.md): términos canónicos de este tema
- [Recursos](RESOURCES.md): fuentes de confianza

## Cómo funciona

Cada lección es corta y autocontenida. Las claves de respuesta están plegadas: primero recuerda, luego ábrelas. Las prácticas en el mundo real importan más que la lectura, y espaciarlas es el punto. Todo lo que siga sin estar claro al final de una lección merece rastrearse hasta su fuente primaria antes de seguir.
