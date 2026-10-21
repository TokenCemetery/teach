---
title: "19. Cuándo gana DoRA y cuándo no"
description: "Predecir la victoria antes de ejecutar"
type: lesson
---

# Lección 19. Cuándo gana DoRA y cuándo no

**Vínculo con la misión:** "Puedes predecir cuándo DoRA supera a LoRA antes de ejecutar" es la vara de esta etapa. Predicción, no experimento.
**Fuente principal:** [Paper: "DoRA: Weight-Decomposed Low-Rank Adaptation", Liu et al., arXiv:2402.09353](https://arxiv.org/abs/2402.09353)
**Requisitos previos:** [Lección 18](0018-dora-magnitude-and-direction.md), [Lección 17](0017-what-qlora-costs.md)

## Calentamiento

1. ▢ ¿Qué impide hacer a `BA` la renormalización de DoRA?

<details markdown="1"><summary>Comprobación</summary>

Cambiar la magnitud. Tras la renormalización, `BA` afecta solo a la dirección, y la magnitud viene del `m` entrenado por separado.

</details>

2. ▢ ¿Por qué no se puede cachear la norma por columna entre pasos?

<details markdown="1"><summary>Comprobación</summary>

Es la norma de `W₀ + BA`, y `BA` cambia en cada paso del optimizador.

</details>

3. ▢ ¿Por qué una comparación de calidad debe usar varias seeds?

<details markdown="1"><summary>Comprobación</summary>

Porque la variación de seed a seed con frecuencia supera al efecto que se mide, así que una diferencia de una sola seed no se puede distinguir del ruido.

</details>

## Qué debes saber

### El patrón reportado

Las mejoras de DoRA sobre LoRA son **mayores con rank bajo y se reducen a medida que sube el rank.**

El razonamiento se sigue directamente del mecanismo. Con rank 4 u 8, la actualización de bajo rank tiene muy poca capacidad, y cualquier parte de esa capacidad gastada en el ajuste de magnitud es capacidad no gastada en la dirección. DoRA entrega la magnitud a un parámetro aparte, barato y dedicado, liberando todo el presupuesto de bajo rank para la dirección. Con rank 128 el presupuesto ya no es escaso, así que liberar un poco de él cambia menos.

Así que la regla de predicción no es "DoRA es mejor" sino:

> **DoRA ayuda más exactamente donde la capacidad de LoRA es más ajustada.**

### Cuándo esperar una victoria

| Situación | Espera | Porque |
|---|---|---|
| Rank muy bajo (4 a 16) | Mejora significativa | La capacidad es escasa; desacoplar libera algo |
| Rank forzado a ser bajo por restricciones | Mejora significativa | Mismo motivo, y no tienes alternativa |
| Rank medio (32 a 64) | Mejora menor | La capacidad es menos escasa |
| Rank alto (128+) | Poca o ninguna | La capacidad no es el límite que manda |
| Podrías simplemente subir el rank | Sube el rank | Más barato en tiempo real que el costo por paso de DoRA |
| El tiempo por paso es tu restricción | Sáltate DoRA | Estás pagando decenas de por ciento por una mejora pequeña |

Esa quinta fila es la que vale la pena interiorizar. Si el rank es una variable libre, **subir el rank suele ser mejor jugada que cambiar a DoRA**, porque el rank extra cuesta casi nada de memoria (lección 7) y casi nada de tiempo, mientras que DoRA cuesta tiempo real en cada paso. DoRA se gana su lugar cuando el rank *no* es libre, cuando algo distinto de la memoria lo mantiene bajo.

### Qué mantiene bajo el rank en realidad

Conviene ser concreto, ya que toda la recomendación depende de ello:

- **Sobreajuste en un dataset pequeño.** Más rank significa más memorización. Aquí de verdad no puedes subir el rank, y DoRA es una opción real: obtienes un mejor uso de un rank que mantienes pequeño a propósito.
- **Una restricción de serving sobre el tamaño del adapter.** Poco común, pero si distribuyes adapters o mantienes muchos en memoria a la vez, el tamaño puede ser limitante.
- **Reproducir una configuración publicada.** Estás atado a su rank.
- **Presupuesto total de tiempo de entrenamiento.** Observa que este juega *en contra* de DoRA y no a favor, porque DoRA es más lento por paso.

Si no se aplica ninguno de estos, el rank es libre, y la acción más simple está disponible.

### Leer la afirmación con sentido crítico

El paper de DoRA reporta mejoras en varias tareas y familias de modelos, con el análisis de magnitud y dirección como su argumento mecanicista. Ese análisis es genuinamente esclarecedor y el método está bien motivado.

Tres cosas que tener presentes:

**Las mejoras reportadas suelen ser pequeñas en términos absolutos**, un punto o dos en un benchmark. Compáralo con el ruido de tus seeds antes de darlo por real en tu tarea.

**El baseline de la comparación importa.** DoRA con rank 8 frente a LoRA con rank 8 es la comparación del paper y es la correcta para aislar el mecanismo. DoRA con rank 8 frente a LoRA con rank 32 es la comparación a la que *tú* te enfrentas al decidir qué ejecutar, y es una pregunta distinta con una respuesta posiblemente distinta.

**La replicación independiente es más escasa que para LoRA o QLoRA.** LoRA tiene años de evidencia de profesionales en incontables tareas. DoRA tiene menos. No es una crítica al método; es una razón para medir en tu propia tarea en lugar de importar una conclusión.

### El procedimiento de decisión

1. ¿Es libre subir el rank? → Súbelo. No uses DoRA.
2. ¿Está el rank fijado en bajo, y por qué? → Si es por riesgo de sobreajuste o una restricción dura, DoRA es un candidato real.
3. ¿Es el tiempo por paso ya la restricción que manda? → No uses DoRA.
4. En otro caso: ejecuta ambos, con el mismo conjunto de seeds y todo lo demás igual, y compara contra el ruido de las seeds.

El paso 4 no es un fallo del procedimiento. Poder decir "el efecto esperado aquí es pequeño y necesito medirlo" *es* la respuesta senior, y es una posición mucho mejor que creerse el paper sin sentido crítico o descartarlo.

## Práctica

1. ▢ ¿Por qué se reducen las mejoras de DoRA a medida que sube el rank?

<details markdown="1"><summary>Comprobación</summary>

Su beneficio es liberar a la capacidad de bajo rank de tener que representar cambios de magnitud. Cuando el rank es escaso, esa capacidad liberada importa proporcionalmente mucho; cuando el rank es generoso, la capacidad no era el factor limitante, así que liberar algo de ella cambia poco.

</details>

2. ▢ Estás en rank 8 y puedes subir el rank libremente. ¿DoRA o más rank?

<details markdown="1"><summary>Comprobación</summary>

Más rank. Cuesta casi nada de memoria y casi nada de tiempo, mientras que DoRA cuesta una penalización por paso en cada paso de cada ejecución futura.

Recurre a DoRA cuando el rank esté fijado por algo, normalmente el riesgo de sobreajuste en un dataset pequeño, y no cuando sea una variable libre.

</details>

3. ▢ 600 ejemplos de entrenamiento, rank mantenido en 8 para limitar la memorización. ¿Merece la pena probar DoRA?

<details markdown="1"><summary>Comprobación</summary>

Sí. Este es el caso al que mejor se adapta el método: el rank es bajo a propósito por una razón que no puedes eliminar, así que hacer mejor uso de él es la única mejora disponible.

Mídelo contra LoRA con el mismo rank y varias seeds, ya que el efecto esperado es pequeño.

</details>

4. ▢ Distingue la comparación del paper de la tuya.

<details markdown="1"><summary>Comprobación</summary>

El paper compara DoRA y LoRA con el mismo rank, lo que aísla correctamente el mecanismo.

Tu decisión es entre DoRA con el rank que puedes permitirte y LoRA con el rank que puedes permitirte, y como LoRA es más rápido por paso quizá puedas permitirte más rank con él. Mismos números, pregunta distinta.

</details>

5. ▢ ¿Qué predice con más fiabilidad una victoria de DoRA?

    - a) Un dataset de entrenamiento grande con muchos ejemplos diversos
    - b) Un rank bajo que no se puede subir por otras razones
    - c) Un base model cuantizado en precisión NF4 de cuatro bits
    - d) Un conjunto de target modules que cubre todas las capas lineales

<details markdown="1"><summary>Comprobación</summary>

**b)** Un rank bajo que no se puede subir por otras razones.

El tamaño del dataset, la precisión del base y la cobertura de los target modules son todos ortogonales al mecanismo. La escasez de capacidad de bajo rank es lo que DoRA alivia.

</details>

6. ▢ Tu mejora medida de DoRA es de 0.6 puntos, con una dispersión de seeds de 1.4 puntos. ¿Qué concluyes y qué haces?

<details markdown="1"><summary>Comprobación</summary>

Que no has detectado un efecto. La diferencia queda bien dentro del ruido.

O ejecutas las seeds suficientes para resolver una diferencia tan pequeña, que pueden ser muchas, o aceptas que el efecto es demasiado pequeño para importar aquí y te quedas con el método más rápido. Decidir que no merece la pena resolverlo es un desenlace legítimo y a menudo correcto.

</details>

## Prácticas en el mundo real

- [ ] Ejecuta LoRA y DoRA con rank 8, tres seeds cada uno, con todo lo demás fijo. Compara la diferencia contra la dispersión de seeds.
- [ ] Ejecuta LoRA con rank 32 durante el mismo presupuesto de tiempo real que DoRA con rank 8. Anota cuál produjo el mejor modelo por unidad de tiempo.
- [ ] Mañana: anota, antes de ejecutar nada, tu predicción de si DoRA ayudará en tu tarea real y por qué. Guárdala y compruébala más tarde.

## Para profundizar

- [Paper: "DoRA: Weight-Decomposed Low-Rank Adaptation", Liu et al., arXiv:2402.09353](https://arxiv.org/abs/2402.09353)
- [Hiperparámetros de LoRA](../reference/lora-hyperparameters.md)
- [Lección 20. Juzgar una variante nueva de PEFT](0020-judging-a-new-variant.md)

---

¿No termina de quedar claro? Vuelve a leer la fuente primaria de arriba, ya que esta lección la comprime y en la compresión es donde se escapa la comprensión. Consulta el [glosario](../GLOSSARY.md) por si algún término te resultó resbaladizo.

Si lo poco claro es la propia lección y no el material, eso es un defecto: [abre un issue](https://github.com/TokenCemetery/teach/issues).
