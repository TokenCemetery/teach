---
title: "10. La pérdida de DPO y qué descarta frente a PPO"
description: "Una pérdida, dos modelos, ningún bucle de muestreo, y el mismo beta que habría usado una penalización KL"
type: lesson
---

# Lección 10. La pérdida de DPO y qué descarta frente a PPO

**Vínculo con la misión:** "Derivar la recompensa implícita de DPO a partir de los mismos datos de preferencia que usa RLHF, y decir a qué renuncia al quitar el bucle de RL" es el cuarto punto de Cómo se ve el éxito. La lección 9 cubrió la derivación; esta lección cubre la pérdida resultante y dice con claridad qué descarta frente a PPO.
**Fuente principal:** [Paper: "Direct Preference Optimization: Your Language Model is Secretly a Reward Model", Rafailov et al., 2023](https://arxiv.org/abs/2305.18290)
**Requisitos previos:** [Lección 9](0009-dpos-implicit-reward-why-the-partition-function-cancels.md)

## Calentamiento

1. ▢ ¿Por qué la función de partición `Z(x)` se cancela al calcular una diferencia de dos recompensas para el mismo prompt?

<details markdown="1"><summary>Comprobación</summary>

`Z(x)` depende solo del prompt, no de qué completion se está puntuando, así que es exactamente el mismo término aditivo en las dos recompensas que se restan, y se cancela por completo de la diferencia.

</details>

2. ▢ ¿Qué significa "recompensa implícita", en el sentido en que la deriva la lección 9?

<details markdown="1"><summary>Comprobación</summary>

La función de recompensa que una policy define matemáticamente, relativa a una policy de referencia fija, puramente como consecuencia de la relación de policy óptima que ya implica el objetivo de RLHF, sin entrenar nunca un reward model aparte.

</details>

## Qué debes saber

### Sustituir la recompensa implícita en la pérdida de Bradley-Terry

La pérdida de Bradley-Terry de la lección 4 entrenaba un reward model aparte para que la puntuación de una completion preferida superara la de una rechazada. DPO usa esa misma idea exacta, con una sustitución: allí donde la pérdida de Bradley-Terry usaría la salida de un reward model entrenado, DPO sustituye la recompensa implícita de la lección 9, `β · log(π(y|x) / π_ref(y|x))`, calculada directamente a partir de la policy que se entrena y del modelo de referencia congelado. La pérdida resultante, tal como la dan Rafailov et al., compara la completion preferida `y_w` y la completion rechazada `y_l` para el mismo prompt:

```text
loss = -log( sigmoid( β · [ (log π(y_w|x) - log π_ref(y_w|x)) - (log π(y_l|x) - log π_ref(y_l|x)) ] ) )
```

Esta es la pérdida de Bradley-Terry de la lección 4, con las dos puntuaciones del reward model sustituidas por los dos valores de la recompensa implícita, uno para la completion preferida y otro para la rechazada. Nada de la forma de la pérdida cambió; lo que cambió es lo que hace las veces de recompensa.

### Qué necesita esta pérdida, y qué ya no necesita

Calcular esta pérdida requiere exactamente dos modelos: la policy que se entrena y una copia congelada del modelo de referencia (normalmente el modelo SFT), cada uno evaluado sobre las mismas completions preferida y rechazada para obtener cuatro log-probabilidades en total. Compáralo con la configuración de PPO de la etapa 4 (lección 8): no se entrena ningún reward model aparte, ya que la recompensa implícita se calcula directamente a partir de la policy y del modelo de referencia. No hace falta una función de valor, ya que no hay ventaja que estimar; DPO no hace aprendizaje por refuerzo en el sentido de muestrear acciones y estimar retornos. Tampoco hay recorte de PPO (lección 7), ya que no hay actualización de policy gradient cuyo tamaño de paso haya que acotar; esta pérdida se optimiza directamente, igual que cualquier pérdida supervisada ordinaria, con un paso de gradiente por lote de pares de preferencia y ningún bucle de muestreo entre pasos.

### El mismo beta, haciendo el mismo trabajo

La `β` de la pérdida de DPO no es un hiperparámetro nuevo inventado para este método; es la misma intensidad de penalización KL del objetivo de RLHF de la lección 6, ahora integrada directamente en la recompensa implícita en lugar de aparecer como un término de penalización aparte añadido a la puntuación de un reward model. Una `β` mayor sigue significando permanecer más cerca del modelo de referencia; una `β` menor sigue significando tener más libertad para alejarse de él, exactamente el compromiso de la lección 6, solo que expresado dentro de una única pérdida en lugar de dos términos separados.

### A qué se renuncia realmente

DPO no elimina los compromisos que gestionaba la penalización KL de PPO; elimina la maquinaria. El método de Rafailov et al. es una reformulación matemáticamente exacta de la misma relación de policy óptima en la que ya se apoya RLHF, no una aproximación de ella, así que nada del objetivo de fondo de satisfacer las preferencias se debilita. A lo que se renuncia genuinamente es a un reward model independiente y a la flexibilidad que viene con entrenar uno por separado: un reward model puede, en principio, reutilizarse para puntuar salidas con las que nunca entrenó directamente a la policy, inspeccionarse por sí solo o combinarse con señales adicionales más allá de los datos de preferencia originales. La recompensa implícita de DPO existe solo ligada a un par concreto de policy y modelo de referencia; no queda ninguna función de puntuación independiente cuando termina el entrenamiento, solo la propia policy entrenada.

## Práctica

1. ▢ El cálculo de la pérdida de DPO para un par de preferencia necesita cuatro log-probabilidades. Nombra de qué es log-probabilidad cada una de las cuatro.

<details markdown="1"><summary>Comprobación</summary>

La log-probabilidad de la policy para la completion preferida, la log-probabilidad del modelo de referencia para la completion preferida, la log-probabilidad de la policy para la completion rechazada y la log-probabilidad del modelo de referencia para la completion rechazada.

</details>

2. ▢ ¿Cuáles de los componentes de PPO (reward model, función de valor, penalización KL, actualización recortada) no necesita en absoluto la pérdida de DPO?

    - a) Solo la actualización recortada
    - b) El reward model y la función de valor; el compromiso de la penalización KL sigue presente, solo que integrado en la recompensa implícita y no como un término aparte
    - c) Los cuatro, ya que DPO no usa ningún tipo de penalización KL
    - d) Solo el reward model; DPO sigue entrenando una función de valor aparte

<details markdown="1"><summary>Comprobación</summary>

**b)** es el relato exacto: DPO no necesita un reward model aparte ni una función de valor, y no tiene actualización recortada por paso ya que no hay bucle de muestreo de RL, pero el mismo compromiso controlado por beta que describió la lección 6 sigue presente, integrado directamente en el término de recompensa implícita. (a), (c) y (d) enuncian mal qué piezas sobreviven.

</details>

3. ▢ Un equipo quiere reutilizar su reward model entrenado para puntuar un lote de completions que nunca formaron parte del entrenamiento de ninguna policy, solo con fines de monitoreo. ¿Podría hacer lo mismo con igual facilidad un equipo que use DPO en lugar de PPO?

<details markdown="1"><summary>Comprobación</summary>

No de forma tan directa. DPO nunca produce un reward model independiente; su recompensa implícita se define solo en términos de una policy entrenada concreta y su modelo de referencia. Puntuar completions arbitrarias así es exactamente el tipo de reutilización que admite un reward model independiente y que el enfoque de DPO no produce como subproducto.

</details>

4. ▢ ¿Significa `β` algo distinto en la pérdida de DPO que en el objetivo de RLHF de la lección 6?

<details markdown="1"><summary>Comprobación</summary>

No. Es la misma intensidad de penalización KL, que controla el mismo compromiso entre mantenerse cerca del modelo de referencia y avanzar hacia lo que recompensan los datos de preferencia; DPO simplemente la integra directamente en el término de recompensa implícita en lugar de mantenerla como una penalización visualmente aparte añadida a la puntuación de un reward model.

</details>

## Prácticas en el mundo real

- [ ] Busca una implementación de DPO en una librería a la que tengas acceso (TRL de Hugging Face es una habitual) y confirma que calcula, por par de preferencia, las mismas cuatro log-probabilidades que nombra esta lección.
- [ ] Con un pequeño ejemplo hipotético (inventa valores plausibles de log-probabilidad para una completion preferida y una rechazada bajo una policy y un modelo de referencia), calcula a mano la pérdida de DPO para dos valores distintos de `β`, y describe cómo cambia la pérdida a medida que `β` crece.
- [ ] Mañana: para un proyecto en el que podrías querer alinear un modelo, decide si recurrirías primero a PPO o a DPO, y escribe una frase que nombre cuál de los compromisos de esta lección (costo de ingeniería, reutilización de un reward model independiente, infraestructura de RL) motivó tu respuesta.

## Para profundizar

- [Paper: "Direct Preference Optimization: Your Language Model is Secretly a Reward Model", Rafailov et al., 2023](https://arxiv.org/abs/2305.18290)
- [Documentation: "TRL - Transformer Reinforcement Learning", Hugging Face](https://huggingface.co/docs/trl/index)
- [Recursos](../RESOURCES.md)

---

La etapa 5 cubrió una manera de llegar a un resultado parecido al de RLHF sin un reward model aparte ni un bucle de RL. La etapa 6 cubre una desviación distinta de PPO: mantener el bucle de RL, pero para tareas en las que la recompensa no es en absoluto cuestión de preferencia humana, sino algo directamente comprobable.

¿No termina de quedar claro? Vuelve a leer la fuente primaria de arriba, ya que esta lección la comprime y en la compresión es donde se escapa la comprensión. Consulta el [glosario](../GLOSSARY.md) por si algún término te resultó resbaladizo.

Si lo poco claro es la propia lección y no el material, eso es un defecto: [abre un issue](https://github.com/TokenCemetery/teach/issues).
