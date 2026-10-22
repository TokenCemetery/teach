---
title: "9. La recompensa implícita de DPO: por qué se cancela la función de partición"
description: "Un término de normalización intratable se interpone entre una recompensa y su policy óptima, hasta que una diferencia de dos recompensas lo hace desaparecer"
type: lesson
---

# Lección 9. La recompensa implícita de DPO: por qué se cancela la función de partición

**Vínculo con la misión:** "Derivar la recompensa implícita de DPO a partir de los mismos datos de preferencia que usa RLHF, y decir a qué renuncia al quitar el bucle de RL" es el cuarto punto de Cómo se ve el éxito. Esta lección cubre la derivación en sí; la lección 10 cubre la pérdida resultante y lo que descarta frente a PPO.
**Fuente principal:** [Paper: "Direct Preference Optimization: Your Language Model is Secretly a Reward Model", Rafailov et al., 2023](https://arxiv.org/abs/2305.18290)
**Requisitos previos:** [Lección 8](0008-why-ppo-is-expensive-and-unstable.md)

## Calentamiento

1. ▢ Nombra los cuatro (o cinco, si se cuenta la función de valor aparte) modelos que intervienen en un paso de entrenamiento de PPO para RLHF, y para qué se usa cada uno.

<details markdown="1"><summary>Comprobación</summary>

La policy que se entrena; un modelo SFT congelado, para la penalización KL; el reward model, que puntúa las salidas; y la función de valor (inicializada desde el reward model), que produce las estimaciones de ventaja que necesita el recorte de PPO.

</details>

2. ▢ Según el propio hallazgo de Ouyang et al., ¿era un reward model más grande y de menor pérdida siempre la mejor opción práctica para PPO?

<details markdown="1"><summary>Comprobación</summary>

No. Su reward model de 175B tenía un entrenamiento más inestable y un mayor costo de cómputo como inicialización de la función de valor que su modelo de 6B, que encontraron estable e igual de eficaz, así que usaron el modelo más pequeño para todos los tamaños de policy.

</details>

## Qué debes saber

### El mismo objetivo de partida que RLHF

Rafailov et al. parten exactamente del objetivo de maximización de recompensa con restricción KL que ya cubre la lección 6: maximizar la recompensa esperada `r(x, y)` bajo la policy, menos una penalización KL (escalada por `β`) frente a una policy de referencia fija `π_ref`. Trabajos previos, sobre los que construyen directamente Rafailov et al., mostraron que este objetivo tiene una solución óptima conocida en forma cerrada:

```text
π_r(y|x) = (1 / Z(x)) · π_ref(y|x) · exp((1/β) · r(x, y))
```

donde `Z(x)` es una **función de partición**, una suma de normalización sobre toda posible completion `y` al prompt `x`, necesaria para que `π_r` sea una distribución de probabilidad válida. Calcular `Z(x)` exactamente supondría sumar sobre toda completion posible que un modelo de lenguaje podría generar, lo cual es tan intratable como suena, y es exactamente la razón de que esta forma cerrada, correcta como es, no se pudiera usar directamente por sí sola como método de entrenamiento.

### Invertir la relación

La jugada de Rafailov et al. es reordenar esta misma ecuación para despejar la recompensa en lugar de la policy. Tomando el logaritmo de ambos lados y reordenando se obtiene:

```text
r(x, y) = β · log( π_r(y|x) / π_ref(y|x) ) + β · log Z(x)
```

Esto expresa la recompensa implícita en cualquier policy `π_r`, en términos de esa policy, la policy de referencia y la misma problemática función de partición, que sigue presente como un término aditivo.

### Por qué la función de partición deja de importar

Aquí es donde la pérdida de Bradley-Terry (lección 4) hace un trabajo real. Las probabilidades de preferencia de Bradley-Terry dependen solo de la *diferencia* entre las recompensas de dos completions, `r(x, y_1) - r(x, y_2)`, nunca del valor absoluto de ninguna recompensa. Como `Z(x)` depende solo del prompt `x`, no de qué completion `y` se está puntuando, es exactamente el mismo término aditivo en `r(x, y_1)` y en `r(x, y_2)`. Sustituir la expresión invertida de la recompensa en una diferencia de dos recompensas para el mismo prompt hace que cada término `β · log Z(x)` se cancele por completo. Lo que queda es una probabilidad de preferencia expresada puramente en términos de la policy `π_r` y de la policy de referencia fija `π_ref`, sin que aparezca en ella ningún reward model ni ninguna función de partición.

### La recompensa implícita

Esto es exactamente lo que nombra el término del glosario **recompensa implícita**: la función de recompensa `r(x, y) = β · log(π_r(y|x) / π_ref(y|x))` (el término de la función de partición puede descartarse una vez que solo importan las diferencias) que una policy define matemáticamente, solo por ser la policy que es, relativa a una referencia. Nunca se entrenó un reward model aparte para producirla; sale directamente de la misma relación de policy óptima sobre la que ya se construía RLHF. Entrenar una policy para satisfacer directamente los datos de preferencia humana, usando esta recompensa implícita en lugar de una entrenada por separado, es la idea completa que da nombre a DPO.

## Práctica

1. ▢ ¿Por qué se describe la función de partición `Z(x)` como intratable de calcular directamente?

<details markdown="1"><summary>Comprobación</summary>

Porque calcularla exactamente requiere sumar sobre toda completion posible `y` que un modelo de lenguaje podría generar para un prompt `x` dado, una suma sobre un espacio enorme que no se puede evaluar directamente.

</details>

2. ▢ ¿Por qué `Z(x)` se cancela al calcular la diferencia `r(x, y_1) - r(x, y_2)` para dos completions al mismo prompt, pero no se cancelaría si hiciera falta la recompensa de una sola completion por sí sola?

<details markdown="1"><summary>Pista</summary>

Pregúntate de qué depende realmente `Z(x)`, y si esa dependencia difiere entre `y_1` y `y_2`.

</details>

<details markdown="1"><summary>Comprobación</summary>

`Z(x)` depende solo del prompt `x`, no de qué completion se está puntuando, así que aparece como exactamente el mismo término aditivo (`β · log Z(x)`) tanto en `r(x, y_1)` como en `r(x, y_2)`. Restar una de la otra lo elimina por completo. Una sola recompensa por sí sola seguiría llevando ese mismo término sin eliminar.

</details>

3. ▢ ¿Qué significa "recompensa implícita", en el sentido concreto en que esta lección la deriva?

<details markdown="1"><summary>Comprobación</summary>

La función de recompensa `β · log(π(y|x) / π_ref(y|x))` que cualquier policy define matemáticamente, relativa a una policy de referencia fija, puramente como consecuencia de la misma relación de policy óptima que ya implica el objetivo de RLHF. Nunca se entrena como un modelo aparte; sale directamente de la propia policy y de la policy de referencia.

</details>

4. ▢ ¿Cuál de estas describe mejor lo que consigue la derivación de DPO, frente a tener que estimar `Z(x)` directamente?

    - a) Encuentra un método numérico más rápido para aproximar `Z(x)`
    - b) Reestructura el problema para que `Z(x)` se cancele por completo siempre que solo haga falta una diferencia de dos recompensas, y evita la necesidad de calcularla en absoluto
    - c) Sustituye `Z(x)` por una segunda función de partición más simple
    - d) Muestra que `Z(x)` es siempre igual a 1 en los modelos de lenguaje

<details markdown="1"><summary>Comprobación</summary>

**b)** es exactamente la derivación que recorre esta lección. (a) y (c) suponen ambas que `Z(x)` aún necesita calcularse o aproximarse de alguna forma, lo que la derivación real evita hacer en absoluto. (d) no es una afirmación que la derivación haga ni necesite.

</details>

## Prácticas en el mundo real

- [ ] Lee la sección de derivación del paper de DPO (enlazado arriba), desde el objetivo con restricción KL hasta la cancelación de la función de partición, y escribe, con tus propias palabras, una frase por ecuación que nombre qué cambió entre ella y la anterior.
- [ ] Escribe, símbolo a símbolo, a qué se evaluaría `β · log(π(y|x) / π_ref(y|x))` si la policy y la policy de referencia asignaran exactamente la misma probabilidad a `y`. Confirma que coincide con tu intuición de cómo debería verse "ninguna señal de preferencia de esta completion".
- [ ] Mañana: sin mirar adelante, escribe una predicción de una frase para la lección 10: dado que la recompensa implícita se define puramente a partir de la policy y del modelo de referencia, sin ningún reward model ni función de partición en el cuadro, ¿qué bucle de entrenamiento esperas que necesite DPO, comparado con el bucle de muestreo y optimización de PPO?

## Para profundizar

- [Paper: "Direct Preference Optimization: Your Language Model is Secretly a Reward Model", Rafailov et al., 2023](https://arxiv.org/abs/2305.18290)
- [Recursos](../RESOURCES.md)

---

¿No termina de quedar claro? Vuelve a leer la fuente primaria de arriba, ya que esta lección la comprime y en la compresión es donde se escapa la comprensión. Consulta el [glosario](../GLOSSARY.md) por si algún término te resultó resbaladizo.

Si lo poco claro es la propia lección y no el material, eso es un defecto: [abre un issue](https://github.com/TokenCemetery/teach/issues).
