---
title: "8. La idea de bajo rank"
description: "`ΔW = BA`, y contar un adapter"
type: lesson
---

# Lección 8. La idea de bajo rank

**Vínculo con la misión:** LoRA es el método sobre el que se construye el resto de la misión. Esta lección es el mecanismo; las dos siguientes son las decisiones.
**Fuente principal:** [Paper: "LoRA: Low-Rank Adaptation of Large Language Models", Hu et al., arXiv:2106.09685](https://arxiv.org/abs/2106.09685)
**Requisitos previos:** [Lección 6](0006-gradients-and-optimizer-state.md), [Lección 7](0007-activations-and-checkpointing.md), [adapter](../GLOSSARY.md)

## Calentamiento

1. ▢ ¿Bytes por parámetro entrenable, y por parámetro congelado?

<details markdown="1"><summary>Comprobación</summary>

Dieciséis entrenable, dos congelado. La proporción de ocho a uno es la razón por la que existen los adapters.

</details>

2. ▢ Tu ejecución con un adapter se queda sin memoria. ¿Qué cambias primero, y qué no cambias?

<details markdown="1"><summary>Comprobación</summary>

Activa el gradient checkpointing, luego recorta el batch size por dispositivo con acumulación para compensar. No recortes el rank: el estado del adapter son megabytes frente a gigabytes de activaciones.

</details>

3. ▢ ¿Qué categoría de memoria no se ve afectada por congelar el base?

<details markdown="1"><summary>Comprobación</summary>

Las activaciones. Escalan con el batch size y la longitud de secuencia, no con cuántos parámetros sean entrenables.

</details>

## Qué debes saber

El full fine-tuning aprende una actualización `ΔW` para cada matriz de pesos, con la misma forma que `W`. La afirmación de LoRA es que esta actualización no necesita ser de rank completo, porque el cambio que requiere una tarea ocupa un subespacio de baja dimensión.

Así que, en lugar de almacenar `ΔW` directamente, se factoriza:

```text
ΔW = B A

A : r × d_in     (down-projection, r is small)
B : d_out × r    (up-projection)
```

y la capa adaptada calcula:

```text
h = W₀ x + (α / r) · B A x
```

`W₀` está congelada. Solo `A` y `B` reciben gradientes.

### Por qué esto ahorra tanto

Una matriz de `d_in × d_out` contiene `d_in · d_out` parámetros. Su factorización de rank `r` contiene `r · (d_in + d_out)`. Para una proyección de 2048 × 2048 con rank 8:

```text
full        = 2048 × 2048        = 4,194,304
rank 8      = 8 × (2048 + 2048)  =    32,768
```

Una reducción de 128× en esa sola matriz. En todo un modelo el ahorro se acumula, porque además te ahorras el gradiente y ambos momentos del optimizador de todo lo que no hiciste entrenable.

### Contar un adapter

La fórmula, para un conjunto de target modules:

```text
adapter params = Σ over targeted layers of  r × (d_in + d_out)
```

Resuelto, para el modelo de 24 capas con `d = 2048` y `d_kv = 256` de la lección 5, rank 8, apuntando a las cuatro proyecciones de atención:

```text
q_proj: 2048 → 2048   →  8 × (2048 + 2048) = 32,768
k_proj: 2048 →  256   →  8 × (2048 +  256) = 18,432
v_proj: 2048 →  256   →  8 × (2048 +  256) = 18,432
o_proj: 2048 → 2048   →  8 × (2048 + 2048) = 32,768
per layer                                  = 102,400
× 24 layers                                = 2,457,600
```

Unos 2.5M de parámetros entrenables frente a un base de 1.12B, o sea **0.22%**. El estado del optimizador de ese adapter es 2.5e6 × 16 ≈ 39 MB.

Observa que el estrechamiento de la grouped-query attention importa aquí de una forma en que no importaba para el base model: los adapters de `k_proj` y `v_proj` *no* son proporcionalmente más pequeños, porque `r × (d_in + d_out)` está dominado por la mayor de las dos dimensiones. Reducir `d_out` de 2048 a 256 recortó la matriz base 8×, pero el adapter solo 1.8×.

### Por qué un rank bajo es suficiente

La afirmación empírica descansa en la **dimensionalidad intrínseca**: la observación de que hacer fine-tuning de un modelo grande preentrenado a una tarea nueva puede hacerse dentro de un subespacio sorprendentemente de baja dimensión de su espacio de parámetros, y que los modelos más grandes y mejor preentrenados tienen una dimensión intrínseca *menor*, no mayor (Aghajanyan et al., [arXiv:2012.13255](https://arxiv.org/abs/2012.13255)). El preentrenamiento ya construyó las features; adaptar es en buena medida cuestión de reponderarlas y recombinarlas, y eso es una operación pequeña.

Dos salvedades honestas:

**Es una afirmación empírica, no un teorema.** Se sostiene bien para adaptar comportamiento, estilo, formato y competencia en una tarea estrecha. Se sostiene peor para instalar grandes volúmenes de conocimiento genuinamente nuevo, que es uno de los argumentos de la lección 27.

**"Bajo" es relativo y se ha movido.** La práctica temprana se asentó en ranks como 8 o 16, en parte porque la memoria era escasa. Trabajos más recientes, en la [lección 10](0010-choosing-target-modules.md), encuentran que en muchas tareas de supervised fine-tuning los adapters con un rank generoso que cubren todas las capas lineales igualan al full fine-tuning, mientras que los tacaños no. El rank 8 es un punto de partida, no una ley.

### La propiedad de inferencia que hace especial a LoRA

Como la actualización es *aditiva* y lineal, puede plegarse de nuevo en el peso base tras el entrenamiento:

```text
W = W₀ + (α / r) · B A
```

El resultado es una matriz de pesos ordinaria. **Un LoRA fusionado tiene exactamente cero sobrecarga de inferencia**: sin matmuls extra, sin arquitectura cambiada, nada que instalar en el momento de servir. Esta es la propiedad que distingue a LoRA de los métodos de capas adapter que lo precedieron, que insertaban módulos nuevos en la ruta de forward y pagaban latencia para siempre. La lección 13 cubre la fusión en la práctica, y la lección 25 cubre cuándo *no* fusionar.

## Práctica

1. ▢ Calcula los parámetros entrenables de un adapter de rank 16 solo en `q_proj` y `v_proj`, en un modelo de 32 capas con `d = 4096` y `d_kv = 1024`.

<details markdown="1"><summary>Comprobación</summary>

`q_proj`: 16 × (4096 + 4096) = 131,072.
`v_proj`: 16 × (4096 + 1024) = 81,920.
Por capa: 212,992. Por 32 capas ≈ 6.82M.

Frente a un base de ~7B, eso es el 0.10%.

</details>

2. ▢ ¿Por qué una factorización de rank `r` de una matriz de `d × d` ahorra tanto más cuando `d` es grande?

<details markdown="1"><summary>Comprobación</summary>

La matriz completa crece como `d²` mientras que la factorización crece como `2rd`, que es lineal. La razón `d / 2r` mejora, por tanto, a medida que el modelo se ensancha.

Por eso LoRA resulta *relativamente* más barato en modelos más grandes, y por eso el método importó más a medida que los modelos crecían.

</details>

3. ▢ ¿Qué es el argumento de la dimensionalidad intrínseca, y cuál es su límite?

<details markdown="1"><summary>Comprobación</summary>

Que adaptar un modelo bien preentrenado a una tarea requiere movimiento solo dentro de un subespacio de baja dimensión del espacio de parámetros, porque el preentrenamiento ya construyó las features necesarias.

Su límite: es un hallazgo empírico sobre la *adaptación*, más fuerte para comportamiento y formato y más débil para instalar conocimiento factual nuevo y sustancial. Tampoco te dice qué rank es suficiente para tu tarea concreta.

</details>

4. ▢ ¿Por qué un LoRA fusionado tiene cero sobrecarga de inferencia, cuando los métodos anteriores de capas adapter no?

<details markdown="1"><summary>Comprobación</summary>

La actualización de LoRA es aditiva y lineal en el mismo espacio que el peso, así que `W₀ + (α/r)BA` se colapsa en una única matriz ordinaria. Los métodos de capas adapter insertaban módulos no lineales nuevos en la ruta de forward, que no se pueden plegar y por tanto añaden latencia en cada capa para siempre.

</details>

5. ▢ Verdadero o falso: un adapter de rank 8 puede representar cualquier actualización que pudiera producir un full fine-tune.

<details markdown="1"><summary>Comprobación</summary>

Falso. `ΔW = BA` con `B` de `r` columnas tiene un rank como máximo `r`, así que solo puede alcanzar actualizaciones dentro de un subespacio de rank 8. Un full fine-tune puede producir una actualización de rank completo.

La apuesta es que la actualización que necesita tu tarea queda cerca de un subespacio así. Cuando no es así, lo ves como un suelo de pérdida que más entrenamiento no baja, y la solución es más rank o más target modules en lugar de más epochs.

</details>

6. ▢ Con grouped-query attention, la salida de `v_proj` se encoge de 4096 a 512. ¿Por qué factor se encoge la matriz base, y por qué factor se encoge su adapter de rank 16?

<details markdown="1"><summary>Comprobación</summary>

Base: 4096 × 4096 → 4096 × 512, una reducción de 8×.
Adapter: 16 × (4096 + 4096) = 131,072 → 16 × (4096 + 512) = 73,728, una reducción de 1.8×.

El costo del adapter lo determina la suma de las dimensiones, así que lo domina la mayor. Estrechar la dimensión menor apenas ayuda.

</details>

## Prácticas en el mundo real

- [ ] Calcula a mano el conteo de parámetros del adapter para un modelo y un conjunto de targets que de verdad pienses usar. Guarda el número.
- [ ] Construye el adapter en código e imprime el conteo de parámetros entrenables. Debería coincidir con tu cálculo a mano. Si no, averigua qué módulo dimensionaste mal.
- [ ] Mañana: recalcula el mismo adapter con rank 8, 32 y 128, y anota cómo cambia el porcentaje del base model.

## Para profundizar

- [Paper: "LoRA: Low-Rank Adaptation of Large Language Models", Hu et al., arXiv:2106.09685](https://arxiv.org/abs/2106.09685)
- [Paper: "Intrinsic Dimensionality Explains the Effectiveness of Language Model Fine-Tuning", Aghajanyan et al., arXiv:2012.13255](https://arxiv.org/abs/2012.13255)
- [Hiperparámetros de LoRA](../reference/lora-hyperparameters.md)
- [Lección 9. Rank, alpha e inicialización](0009-rank-alpha-and-initialisation.md)

---

¿No termina de quedar claro? Vuelve a leer la fuente primaria de arriba, ya que esta lección la comprime y en la compresión es donde se escapa la comprensión. Consulta el [glosario](../GLOSSARY.md) por si algún término te resultó resbaladizo.

Si lo poco claro es la propia lección y no el material, eso es un defecto: [abre un issue](https://github.com/TokenCemetery/teach/issues).
