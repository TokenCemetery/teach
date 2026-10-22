---
title: "11. GRPO: ventaja relativa al grupo en lugar de una función de valor"
description: "Muestrea varias respuestas a la misma pregunta y deja que la propia dispersión de recompensas del grupo diga cuáles fueron mejores"
type: lesson
---

# Lección 11. GRPO: ventaja relativa al grupo en lugar de una función de valor

**Vínculo con la misión:** "Explicar la ventaja relativa al grupo en GRPO y por qué una recompensa verificable (un test unitario, una respuesta matemática comprobada) cambia aquello a lo que puede apuntar el entrenamiento con RL" es el quinto punto de Cómo se ve el éxito. Esta lección cubre la ventaja relativa al grupo en sí; la lección 12 cubre las recompensas verificables, la pareja que hace que GRPO encaje especialmente bien con las matemáticas y el código.
**Fuente principal:** [Paper: "DeepSeekMath: Pushing the Limits of Mathematical Reasoning in Open Language Models", Shao et al., 2024](https://arxiv.org/abs/2402.03300)
**Requisitos previos:** [Lección 10](0010-the-dpo-loss-and-what-it-drops-relative-to-ppo.md)

## Calentamiento

1. ▢ ¿Qué necesita la pérdida de DPO, en términos de modelos, que no necesite la configuración de PPO?

<details markdown="1"><summary>Comprobación</summary>

Nada extra; DPO necesita estrictamente menos modelos que PPO. Solo necesita la policy y un modelo de referencia congelado, sin reward model aparte y sin función de valor.

</details>

2. ▢ ¿Quitar el reward model aparte y el bucle de RL en DPO elimina también el compromiso de la penalización KL entre permanecer cerca del modelo de referencia y avanzar hacia lo que recompensan los datos de preferencia?

<details markdown="1"><summary>Comprobación</summary>

No. El mismo compromiso, controlado por la misma `β`, sigue presente; simplemente está integrado directamente en el término de recompensa implícita en lugar de mantenerse como una penalización visualmente aparte.

</details>

## Qué debes saber

### El costo que añade específicamente la función de valor de PPO

La etapa 4 (lección 8) ya estableció que PPO necesita una función de valor junto al reward model, inicializada desde él, para producir las estimaciones de ventaja de las que depende su objetivo recortado. Shao et al. nombran exactamente por qué esa pieza concreta es cara: la función de valor suele ser otro modelo de tamaño comparable al de la propia policy, que añade un costo real de memoria y de cómputo sobre todo lo demás que PPO ya necesita. Añaden un segundo problema específico de los modelos de lenguaje: en este contexto, normalmente solo el último token de una completion recibe una puntuación de recompensa, lo que hace más difícil entrenar una función de valor que sea precisa en cada token anterior de esa completion que en un contexto con feedback de recompensa en cada paso.

### El sustituto de GRPO: que un grupo de muestras aporte su propio baseline

**Group Relative Policy Optimization (GRPO)** elimina por completo la función de valor y la reemplaza por algo que no necesita ningún modelo extra: para una pregunta `q` dada, GRPO muestrea un **grupo** de `G` salidas, `{o_1, o_2, ..., o_G}`, todas de la misma policy (la antigua). Un reward model puntúa cada una de las `G` salidas y da `G` recompensas, `r_1` a `r_G`. En lugar de preguntar a una función de valor entrenada aparte "¿fue esta salida concreta mejor de lo esperado?", GRPO hace una pregunta más simple que se responde directamente desde el propio grupo: ¿fue esta salida mejor que las otras muestreadas para la misma pregunta? La **ventaja relativa al grupo** de la salida `i` es la recompensa normalizada por el grupo:

```text
A_i = (r_i - mean(r_1, ..., r_G)) / std(r_1, ..., r_G)
```

aplicada de manera uniforme a cada token de esa salida. Una salida que puntuó por encima de la media del grupo recibe una ventaja positiva; una que puntuó por debajo recibe una ventaja negativa; el tamaño de la ventaja se escala según lo dispersas que resultaran ser las recompensas del grupo. No se entrena ninguna función de valor, y el costo de memoria y de cómputo que la lección 8 atribuía a ella desaparece con ella.

### Por qué esto encaja especialmente bien con los reward models

Shao et al. hacen una observación más que conviene retener: esta comparación relativa al grupo no es solo un atajo para ahorrar costo, sino que coincide con la forma de los datos con los que se entrenó un reward model en primer lugar. Un reward model de Bradley-Terry (lección 4) se entrena con comparaciones entre salidas a la misma pregunta; puntuar varias salidas a la misma pregunta y compararlas entre sí, en lugar de con un baseline absoluto aprendido por separado, pide al reward model el mismo tipo de juicio relativo para el que realmente se entrenó.

### Adónde se mueve la penalización KL

GRPO también cambia dónde se sitúa la penalización KL, comparado con el objetivo de RLHF de la lección 6. El objetivo de Ouyang et al. añadía la penalización KL directamente a la recompensa por token, antes de calcular a partir de ella ninguna ventaja. Shao et al., en cambio, añaden la divergencia KL entre la policy entrenada y la policy de referencia como un término aparte directamente en la pérdida, junto al objetivo sustituto recortado, en lugar de mezclarla en la recompensa a partir de la cual se calcula la ventaja. Esto mantiene la parte del cálculo basada en la recompensa (y la ventaja relativa al grupo construida a partir de ella) sin complicarla con el término KL, y sigue aplicando el mismo tipo de freno a cuánto se desvía la policy de su referencia.

## Práctica

1. ▢ Un grupo de 4 salidas muestreadas a la misma pregunta recibe del reward model las recompensas `{2, 4, 6, 8}`. A grandes rasgos, ¿qué salida(s) obtienen una ventaja relativa al grupo positiva y cuáles una negativa?

<details markdown="1"><summary>Pista</summary>

Calcula primero la media del grupo, y luego pregúntate qué recompensas quedan por encima y cuáles por debajo.

</details>

<details markdown="1"><summary>Comprobación</summary>

La media es 5. Las salidas que puntúan 6 y 8 quedan por encima de la media y obtienen una ventaja positiva; las que puntúan 2 y 4 quedan por debajo y obtienen una ventaja negativa.

</details>

2. ▢ Según Shao et al., nombra dos problemas concretos de la función de valor de PPO que evita la ventaja relativa al grupo de GRPO.

<details markdown="1"><summary>Comprobación</summary>

La función de valor suele ser otro modelo de tamaño comparable al de la policy, lo que añade un costo sustancial de memoria y de cómputo, y en el contexto de los LLM, donde normalmente solo el último token recibe una puntuación de recompensa, entrenar una función de valor precisa en cada token anterior es más difícil que en contextos con feedback de recompensa en cada paso.

</details>

3. ▢ ¿Por qué describe Shao et al. la comparación relativa al grupo como especialmente adecuada para los reward models, más allá de ser simplemente más barata que una función de valor?

<details markdown="1"><summary>Comprobación</summary>

Porque los reward models se entrenan normalmente con comparaciones entre salidas a la misma pregunta en primer lugar (la misma forma que usa la pérdida de Bradley-Terry de la lección 4); puntuar varias salidas a una pregunta y compararlas entre sí pide al reward model el mismo tipo de juicio relativo para el que realmente se entrenó.

</details>

4. ▢ ¿Dónde se sitúa la penalización KL de GRPO, comparado con dónde se sitúa la penalización KL en el objetivo de RLHF de Ouyang et al. (lección 6)?

    - a) En el mismo sitio: añadida directamente a la recompensa por token antes de calcular las ventajas
    - b) GRPO no tiene ninguna penalización KL
    - c) GRPO añade la divergencia KL como un término aparte directamente en la pérdida, junto al objetivo recortado, en lugar de mezclarla en la recompensa
    - d) GRPO reemplaza la penalización KL por un segundo reward model

<details markdown="1"><summary>Comprobación</summary>

**c)** es la ubicación real que describen Shao et al. (a) describe el enfoque de Ouyang et al., que GRPO cambia específicamente. (b) y (d) enuncian mal lo que hace GRPO; el mismo tipo de freno sigue presente, solo que reubicado.

</details>

## Prácticas en el mundo real

- [ ] Busca una implementación de GRPO en una librería a la que tengas acceso, y comprueba cómo calcula la ventaja normalizada por el grupo: ¿coincide con la fórmula de media y desviación estándar que da esta lección?
- [ ] Lee el párrafo del paper de DeepSeekMath (enlazado arriba) que describe por qué la función de valor es costosa específicamente en el contexto de los LLM, y escribe una frase que distinga el argumento del costo de memoria del argumento de la precisión por token.
- [ ] Mañana: sin mirar adelante, escribe una predicción de una frase para la lección 12: si un reward model puede reemplazarse por cualquier cosa que produzca una puntuación fiable para cada salida muestreada, ¿qué tipo de tarea permitiría que esa puntuación viniera de un verificador determinista y no de un modelo entrenado en absoluto?

## Para profundizar

- [Paper: "DeepSeekMath: Pushing the Limits of Mathematical Reasoning in Open Language Models", Shao et al., 2024](https://arxiv.org/abs/2402.03300)
- [Recursos](../RESOURCES.md)

---

¿No termina de quedar claro? Vuelve a leer la fuente primaria de arriba, ya que esta lección la comprime y en la compresión es donde se escapa la comprensión. Consulta el [glosario](../GLOSSARY.md) por si algún término te resultó resbaladizo.

Si lo poco claro es la propia lección y no el material, eso es un defecto: [abre un issue](https://github.com/TokenCemetery/teach/issues).
