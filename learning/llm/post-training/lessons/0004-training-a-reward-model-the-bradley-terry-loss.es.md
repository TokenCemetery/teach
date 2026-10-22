---
title: "4. Entrenar un reward model: la pérdida de Bradley-Terry"
description: "Un reward model nunca ve una puntuación absoluta en el entrenamiento, solo cuál de dos completions le gustó más a una persona"
type: lesson
---

# Lección 4. Entrenar un reward model: la pérdida de Bradley-Terry

**Vínculo con la misión:** "Entrenar un reward model con pares de preferencia usando la pérdida de Bradley-Terry, e identificar una completion con reward hacking producida por una policy entrenada contra él" es el segundo punto de Cómo se ve el éxito. Esta lección cubre el entrenamiento del reward model; la lección 5 cubre lo que puede salir mal una vez que se optimiza una policy contra él.
**Fuente principal:** [Paper: "Training language models to follow instructions with human feedback", Ouyang et al., 2022](https://arxiv.org/abs/2203.02155)
**Requisitos previos:** [Lección 3](0003-loss-masking-on-non-assistant-tokens.md)

## Calentamiento

1. ▢ ¿Qué hace realmente el enmascarado de la pérdida en los tokens que no son del asistente, mecánicamente, durante el entrenamiento de SFT?

<details markdown="1"><summary>Comprobación</summary>

Da a la posición de cada token del prompt o que no es del asistente una etiqueta que la función de pérdida ignora, de modo que solo las posiciones del asistente (la respuesta) aportan un gradiente, aunque los tokens del prompt sigan presentes como entrada en la que el modelo condiciona.

</details>

2. ▢ ¿Qué se rompe en el entrenamiento de SFT si se omite este enmascarado?

<details markdown="1"><summary>Comprobación</summary>

La señal de gradiente se gasta, o se diluye, en aprender a predecir los propios tokens del prompt, que no es la habilidad que SFT debe enseñar, en lugar de concentrarse por completo en los tokens de la respuesta que el modelo debería aprender realmente a producir.

</details>

## Qué debes saber

### Recopilar datos de preferencia

Un reward model necesita datos que digan cuál de dos salidas del modelo es mejor, no cuál debería haber sido palabra por palabra la mejor salida. Ouyang et al. lo recopilan presentando a los anotadores varias salidas (usan entre 4 y 9) al mismo prompt y pidiéndoles que ordenen el conjunto entero, en lugar de comparar siempre solo de dos en dos. Un ranking sobre `K` salidas produce todas las comparaciones por pares dentro de ese ranking, `K` sobre 2 de ellas, así que una sola tarea de ranking da muchos pares de entrenamiento a la vez.

### De dónde sale el reward model

Un reward model no se entrena desde cero. Ouyang et al. describen que se parte del propio modelo SFT, con su capa final de unembedding, la parte que convierte un estado oculto en probabilidades del token siguiente, eliminada y sustituida por una capa que produce un único escalar. El reward model reutiliza todo lo que el modelo SFT ya aprendió sobre el lenguaje y sobre el comportamiento objetivo, reaprovechado para producir un número, una puntuación, para un prompt y una completion dados, en lugar de una distribución sobre el token siguiente.

### La pérdida de Bradley-Terry

Dada una completion preferida `y_w` ("ganadora") y una completion rechazada `y_l` ("perdedora") para el mismo prompt `x`, y las salidas escalares del reward model `r(x, y_w)` y `r(x, y_l)` para cada una, Ouyang et al. entrenan el reward model con esta pérdida:

```text
loss(θ) = -E[log(σ(r_θ(x, y_w) - r_θ(x, y_l)))]
```

donde `σ` es la función sigmoide logística. Esta es la **pérdida de Bradley-Terry**: trata la probabilidad de que una persona prefiera `y_w` a `y_l` como la sigmoide de la diferencia entre sus dos puntuaciones, y entrena al reward model para que esa probabilidad predicha coincida con lo que el anotador humano eligió realmente. Bajar esta pérdida significa subir `r(x, y_w) - r(x, y_l)`: se entrena al modelo para que la puntuación de la completion preferida sea mayor que la de la rechazada, con un margen proporcional a lo seguro que necesita que sea el favoritismo de la sigmoide.

### Por qué la escala absoluta de la recompensa no es significativa por sí sola

Fíjate en que la pérdida depende solo de la *diferencia* entre las dos puntuaciones, nunca de ninguna de ellas por separado. Sumar la misma constante a cada recompensa que produce el modelo dejaría cada diferencia, y por tanto toda la pérdida, completamente sin cambios. Esto significa que nada del entrenamiento obliga a las puntuaciones del reward model a ninguna escala absoluta concreta; solo se restringe el orden relativo (y el tamaño de las brechas) entre las completions preferidas y las rechazadas. Ouyang et al. lo resuelven directamente: como la pérdida es invariante a un desplazamiento, normalizan el reward model con un sesgo (bias) para que las demostraciones de los anotadores puntúen una media de 0 antes de usarlo en el aprendizaje por refuerzo, dando a la escala por lo demás arbitraria un ancla fija con la que medirse.

### Por qué se mantienen juntas las comparaciones de un mismo ranking

Tratar cada una de las `K` sobre 2 comparaciones de una sola tarea de ranking como un ejemplo de entrenamiento independiente y mezclado por separado causa un problema concreto: como el mismo conjunto pequeño de completions reaparece en muchas de esas comparaciones, una sola pasada sobre datos construidos así tiende a hacer overfitting, ya que cada completion se reutiliza en efecto en `K - 1` comparaciones correlacionadas. El arreglo de Ouyang et al. es tratar todas las comparaciones de una tarea de ranking como un único elemento de batch durante el entrenamiento, en lugar de mezclarlas de forma independiente en el dataset más amplio, y encontraron que esto mejoraba la precisión y la pérdida de validación frente a tratar cada comparación por pares como totalmente independiente.

## Práctica

1. ▢ Un reward model produce `r(x, y_w) = 2.0` y `r(x, y_l) = 1.0` para un par, y `r(x, y_w) = 12.0` y `r(x, y_l) = 11.0` para un segundo par, de un prompt distinto. ¿Trata la pérdida de Bradley-Terry estos dos pares de forma distinta?

<details markdown="1"><summary>Pista</summary>

La pérdida es función de `r(x, y_w) - r(x, y_l)`, no de ninguno de los dos valores por separado.

</details>

<details markdown="1"><summary>Comprobación</summary>

No. Ambos pares tienen la misma diferencia, `1.0`, y la pérdida depende solo de esa diferencia, no de las puntuaciones absolutas. Esta es exactamente la razón de que la escala absoluta del reward model no sea significativa sin un ancla externa.

</details>

2. ▢ ¿De dónde salen realmente los pesos iniciales de un reward model, según Ouyang et al.?

<details markdown="1"><summary>Comprobación</summary>

Del modelo SFT, con su capa final de unembedding eliminada y sustituida por una capa que produce un único escalar, y no de un modelo nuevo inicializado al azar.

</details>

3. ▢ Un anotador ordena 4 completions (`K = 4`) para un solo prompt. ¿Cuántas comparaciones por pares produce para el entrenamiento esta tarea de ranking?

<details markdown="1"><summary>Comprobación</summary>

6 (`4` sobre `2`, que es `(4 × 3) / 2 = 6`).

</details>

4. ▢ ¿Por qué mantienen Ouyang et al. juntas todas las comparaciones de una tarea de ranking como un único elemento de batch, en lugar de mezclar cada comparación por pares de forma independiente en el conjunto de entrenamiento?

    - a) Hace que el reward model entrene más rápido sin efecto en la precisión
    - b) Mezclarlas de forma independiente causa overfitting, ya que el mismo conjunto pequeño de completions se reutiliza en muchas comparaciones correlacionadas dentro de una tarea de ranking
    - c) La pérdida de Bradley-Terry no se puede calcular a menos que las comparaciones se agrupen así
    - d) Es necesario para que las puntuaciones del reward model caigan en un rango numérico fijo

<details markdown="1"><summary>Comprobación</summary>

**b)** es la razón que dan directamente Ouyang et al.: las completions correlacionadas y reutilizadas en las comparaciones de una tarea de ranking hacen que una sola pasada haga overfitting si se mezclan de forma independiente. (a), (c) y (d) no describen el problema real ni su arreglo.

</details>

## Prácticas en el mundo real

- [ ] Busca un dataset público de preferencias (muchos se publican para entrenar reward models) y comprueba cuántas completions se ordenan por prompt, y si el formato publicado ya refleja comparaciones por pares o un ranking completo.
- [ ] Calcula a mano el término sigmoide de la pérdida de Bradley-Terry para una diferencia de recompensa de `0` (ninguna señal de preferencia) y para una diferencia positiva grande, y describe en una frase cómo se comporta la pérdida en cada extremo.
- [ ] Mañana: sin mirar adelante, escribe una predicción de una frase para la lección 5: si un reward model solo se entrena para ordenar las completions que las personas le han mostrado realmente, ¿qué podría salir mal cuando una policy es libre de generar cualquier completion, buscando lo que puntúe más alto?

## Para profundizar

- [Paper: "Training language models to follow instructions with human feedback", Ouyang et al., 2022](https://arxiv.org/abs/2203.02155)
- [Recursos](../RESOURCES.md)

---

¿No termina de quedar claro? Vuelve a leer la fuente primaria de arriba, ya que esta lección la comprime y en la compresión es donde se escapa la comprensión. Consulta el [glosario](../GLOSSARY.md) por si algún término te resultó resbaladizo.

Si lo poco claro es la propia lección y no el material, eso es un defecto: [abre un issue](https://github.com/TokenCemetery/teach/issues).
