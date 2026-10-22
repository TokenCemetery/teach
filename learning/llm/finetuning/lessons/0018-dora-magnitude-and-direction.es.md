---
title: "18. DoRA: magnitud y dirección"
description: "La renormalización desacopla ambas, y eso es el método"
type: lesson
---

# Lección 18. DoRA: magnitud y dirección

**Vínculo con la misión:** El tercer método nombrado en la misión, y aquel cuyo mecanismo se describe mal con más frecuencia.
**Fuente principal:** [Paper: "DoRA: Weight-Decomposed Low-Rank Adaptation", Liu et al., arXiv:2402.09353](https://arxiv.org/abs/2402.09353)
**Requisitos previos:** [Lección 8](0008-the-low-rank-idea.md), [Lección 9](0009-rank-alpha-and-initialisation.md)

## Calentamiento

1. ▢ Escribe la actualización de LoRA y di qué factores son entrenables.

<details markdown="1"><summary>Comprobación</summary>

`h = W₀x + (α/r)BAx`. Solo `A` y `B` son entrenables; `W₀` está congelada. `B` empieza en cero.

</details>

2. ▢ ¿Cuál es el rank máximo de una actualización de LoRA con `r = 8`?

<details markdown="1"><summary>Comprobación</summary>

Ocho. `BA` no puede superar el rank de su dimensión interna, lo que acota qué actualizaciones puede expresar el adapter.

</details>

3. ▢ ¿Por qué la cuantización no es gratis en los modelos pequeños?

<details markdown="1"><summary>Comprobación</summary>

El error de cuantización es una perturbación relativa fija, y los modelos pequeños tienen menos redundancia disponible para absorberla.

</details>

## Qué debes saber

### La observación

Cualquier matriz de pesos puede descomponerse en una **magnitud** y una **dirección**. Tomándola columna por columna:

```text
W = m · (V / ‖V‖_c)
```

donde `‖·‖_c` es la norma por columna, `V / ‖V‖_c` es una matriz de columnas de norma unitaria, que es pura dirección, y `m` es un vector con un escalar por columna, que lleva la magnitud.

Los autores de DoRA analizaron cómo mueven el full fine-tuning y LoRA cada una de estas dos cantidades durante el entrenamiento, y encontraron que los patrones difieren. El full fine-tuning tiende a producir cambios direccionales relativamente grandes con cambios de magnitud comparativamente modestos, y muestra una relación distintiva entre ambos. Las actualizaciones de LoRA mueven magnitud y dirección juntas de un modo más acoplado, porque un único término aditivo de bajo rank cambia ambas a la vez y no tiene manera de ajustarlas de forma independiente.

La hipótesis: ese acoplamiento es una limitación, y desacoplar ambas debería dar a LoRA un comportamiento de aprendizaje más cercano al del full fine-tuning.

### El método

Descompón la `W₀` congelada en su magnitud y su dirección. Luego:

- Haz que el **vector de magnitud `m` sea entrenable directamente.** Es un escalar por columna, así que `d_out` parámetros, despreciable.
- Aplica la **actualización de bajo rank a la dirección**, y renormaliza después.

```text
W' = m · (W₀ + BA) / ‖W₀ + BA‖_c
```

Lee eso con cuidado, porque es donde las descripciones se equivocan. `BA` se suma al peso y luego el resultado se **renormaliza a columnas unitarias**, lo que elimina cualquier cambio de magnitud que introdujera `BA`. La magnitud la aporta entonces por separado y de forma explícita el `m` entrenable.

Así que `BA` ya no puede cambiar la magnitud ni siquiera por accidente, puesto que solo orienta la dirección, y `m` se encarga de la escala. Ese es el desacoplamiento, y es toda la contribución.

![Una columna de una matriz de pesos como un vector desde un origen, con un cuarto de círculo punteado que marca la norma unitaria. A la izquierda, W0 más BA cae en un punto con un ángulo distinto y una longitud distinta. A la derecha, solo sobrevive el ángulo: la dirección está sobre el círculo unitario y m fija la longitud, aquí de vuelta a la de W0.](images/length-and-angle.svg)

Los dos paneles usan la misma `W0` y la misma `BA`. A la izquierda un término movió ambas cantidades a la vez; a la derecha el ángulo es todo lo que aportó `BA`, y la longitud es la que diga `m`.

### Qué cuesta

**Parámetros:** un vector extra por capa adaptada, de longitud `d_out`. Para una capa de ancho 4096 son 4096 números frente a los 131,072 de un adapter de rank 16. Esencialmente gratis.

**Cómputo:** no es gratis. Hay que calcular la norma por columna de `W₀ + BA`, y depende de `BA`, así que cambia en cada paso y no se puede cachear entre actualizaciones. Esto hace que DoRA sea medible y más lento por paso que LoRA, normalmente del orden de decenas de por ciento, variando según la implementación y cuánto del trabajo logre fusionar o cachear la biblioteca.

**Complejidad:** la fusión es más complicada. El peso fusionado es `m · (W₀ + BA)/‖W₀ + BA‖_c`, que sigue siendo una matriz ordinaria, así que un DoRA fusionado es exacto y tiene cero sobrecarga de inferencia, exactamente igual que LoRA. Pero la aritmética para llegar ahí no es una simple suma, y la implementación importa.

### Usarlo

En PEFT, DoRA es un flag de la configuración de LoRA y no un método aparte:

```text
config := {
    use_dora: true,
    rank: 8,
    alpha: 32,
    target_modules: "all-linear",
    dropout: 0.05,
    adapt_bias: false,
}
```

Todo lo que sabes sobre rank, alpha, target modules y learning rate se mantiene. Es una modificación de cómo se aplica la actualización, no un nuevo conjunto de decisiones. Confirma el nombre del flag contra la versión instalada, como siempre.

DoRA también se compone con la cuantización: un base cuantizado más un adapter DoRA, a veces llamado QDoRA. La interacción merece medirse en lugar de suponerse: la renormalización opera ahora sobre pesos descuantizados que arrastran error de cuantización, lo que no es evidentemente inofensivo.

### El resumen honesto

DoRA es un refinamiento bien motivado con un mecanismo claro, mejoras reportadas concentradas en rank bajo y un costo real de velocidad. No es un sustituto de LoRA y no es un efecto grande en todos los ajustes. La lección 19 trata de predecir cuándo se amortizará.

## Práctica

1. ▢ Escribe la fórmula de DoRA e identifica cada cantidad entrenable.

<details markdown="1"><summary>Comprobación</summary>

`W' = m · (W₀ + BA) / ‖W₀ + BA‖_c`.

Entrenables: el vector de magnitud `m`, más `A` y `B`. Congelada: `W₀`.

</details>

2. ▢ ¿Qué consigue la renormalización?

<details markdown="1"><summary>Comprobación</summary>

Elimina cualquier cambio de magnitud que introdujera `BA`, dejando a `BA` capaz de afectar solo a la dirección. La magnitud la fija entonces de forma explícita el `m` entrenable.

Esa separación es el desacoplamiento que da nombre al método.

</details>

3. ▢ ¿Por qué DoRA es más lento que LoRA pese a añadir casi ningún parámetro?

<details markdown="1"><summary>Comprobación</summary>

Hay que calcular la norma por columna de `W₀ + BA`, y como depende de `BA` cambia en cada paso y no se puede cachear entre actualizaciones. Los parámetros extra son despreciables; la aritmética extra no.

</details>

4. ▢ ¿Cuántos parámetros extra añade DoRA a una capa de 4096 × 4096, y cómo se compara con un LoRA de rank 16 ahí?

<details markdown="1"><summary>Comprobación</summary>

4096, un escalar de magnitud por columna de salida.

Un LoRA de rank 16 en esa capa son 16 × (4096 + 4096) = 131,072. Así que la adición de DoRA es de un 3% más, que no es la razón para dudar. El tiempo por paso sí lo es.

</details>

5. ▢ ¿Tiene sobrecarga de inferencia un DoRA fusionado?

<details markdown="1"><summary>Comprobación</summary>

No. El resultado fusionado `m · (W₀ + BA)/‖W₀ + BA‖_c` es una matriz de pesos ordinaria, así que un DoRA fusionado es indistinguible de cualquier otro modelo en la inferencia.

La aritmética para producirlo es más compleja que la simple suma de LoRA, pero el producto es la misma clase de cosa.

</details>

6. ▢ ¿Qué afirmación describe correctamente a DoRA?

    - a) Añade una segunda actualización de bajo rank al término de magnitud
    - b) Entrena la magnitud directamente y actualiza la dirección con bajo rank
    - c) Sustituye la actualización de bajo rank por un escalado de rank completo
    - d) Normaliza los gradientes en lugar de la matriz de pesos

<details markdown="1"><summary>Comprobación</summary>

**b)** Entrena la magnitud directamente y actualiza la dirección con bajo rank.

No hay un segundo factor de bajo rank. La actualización no es de rank completo. La normalización se aplica al peso, no a los gradientes.

</details>

## Prácticas en el mundo real

- [ ] Implementa la descomposición a mano: toma cualquier matriz de pesos, calcula las normas por columna, sepárala en `m` y `V` de norma unitaria, y verifica que `m · V` la reconstruye.
- [ ] Entrena la misma configuración con `use_dora=True` y `False`. Registra los segundos por paso de ambas y calcula la sobrecarga.
- [ ] Mañana: lee la sección 4 del paper de DoRA, donde se presenta el análisis de magnitud y dirección del full fine-tuning frente a LoRA. Ese análisis es el argumento.

## Para profundizar

- [Paper: "DoRA: Weight-Decomposed Low-Rank Adaptation", Liu et al., arXiv:2402.09353](https://arxiv.org/abs/2402.09353)
- [Docs: LoRA variants, Hugging Face PEFT](https://huggingface.co/docs/peft/main/en/developer_guides/lora)
- [Lección 19. Cuándo gana DoRA y cuándo no](0019-when-dora-wins.md)

---

¿No termina de quedar claro? Vuelve a leer la fuente primaria de arriba, ya que esta lección la comprime y en la compresión es donde se escapa la comprensión. Consulta el [glosario](../GLOSSARY.md) por si algún término te resultó resbaladizo.

Si lo poco claro es la propia lección y no el material, eso es un defecto: [abre un issue](https://github.com/TokenCemetery/teach/issues).
