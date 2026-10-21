---
title: "9. Rank, alpha e inicialización"
description: "Solo importa `α/r`, y por qué `B` empieza en cero"
type: lesson
---

# Lección 9. Rank, alpha e inicialización

**Vínculo con la misión:** La misión te pide justificar cada hiperparámetro a partir de la tarea. Estos tres son donde la mayoría de la gente repite folclore en su lugar.
**Fuente principal:** [Docs: LoRA, Hugging Face PEFT](https://huggingface.co/docs/peft/main/en/developer_guides/lora)
**Requisitos previos:** [Lección 8](0008-the-low-rank-idea.md)

## Calentamiento

1. ▢ Escribe la ecuación de forward de LoRA.

<details markdown="1"><summary>Comprobación</summary>

`h = W₀x + (α/r) · BAx`, con `W₀` congelada y solo `A` y `B` entrenables.

</details>

2. ▢ ¿Conteo de parámetros del adapter para una capa objetivo?

<details markdown="1"><summary>Comprobación</summary>

`r × (d_in + d_out)`. Lo domina la mayor dimensión.

</details>

3. ▢ ¿Por qué un adapter fusionado no cuesta nada en la inferencia?

<details markdown="1"><summary>Comprobación</summary>

La actualización es aditiva y lineal, así que se pliega en el peso base y deja detrás una matriz ordinaria.

</details>

## Qué debes saber

### Inicialización, y por qué no es arbitraria

`A` se inicializa al azar, ya sea gaussiana o Kaiming-uniforme. `B` se inicializa **exactamente en cero**.

Por tanto `BA = 0` en el paso cero, así que `ΔW = 0`, así que **el modelo adaptado es, bit a bit, el base model antes de la primera actualización.** Esta es una propiedad deliberada e importante:

- El entrenamiento parte de un modelo en buen estado conocido y no de uno perturbado.
- No hay un shock inicial al comportamiento preentrenado, así que no hay daño temprano que deshacer.
- Cualquier degradación que observes es algo que hizo el entrenamiento, no algo que hizo la inicialización.

![B dibujada como una cuadrícula de ceros, A como una cuadrícula de valores variados y su producto como una cuadrícula de ceros, con las dos inicializaciones descartadas nombradas debajo.](images/zero-whatever-a-holds.svg)

Las entradas de `A` son visibles y ninguna importa: cada una se multiplica por un cero en su camino hacia el producto.

La asimetría es necesaria. Si ambas fueran cero, el gradiente de ambas sería cero y nada aprendería jamás: el producto necesita que un factor sea distinto de cero para llevar señal. Si ambas fueran aleatorias, `ΔW` empezaría como ruido estructurado inyectado en cada capa objetivo.

Esta es también la razón por la que LoRA tolera learning rates mucho más altos que el full fine-tuning. No estás empujando pesos que ya codifican todo lo que el modelo sabe; estás haciendo crecer un término desde cero.

### Alpha y el factor de escala

`α` (`lora_alpha`) es un escalar fijo. La actualización se escala por `α/r`.

El sentido de dividir por `r` era hacer que la magnitud efectiva de la actualización fuera aproximadamente independiente del rank, de modo que cambiar el rank no te obligara a reajustar el learning rate. **Lo que importa es la razón `α/r`, no ninguno de los dos números por separado.**

| `r` | `α` | `α/r` | Efecto |
|---|---|---|---|
| 8 | 16 | 2.0 | Baseline común |
| 16 | 32 | 2.0 | Más capacidad, misma escala de actualización |
| 16 | 16 | 1.0 | Más capacidad, actualización más débil |
| 64 | 16 | 0.25 | Mucha más capacidad, muy amortiguada |

Esa última fila es una trampa que merece nombre: subir el rank dejando `α` fijo *reduce* la escala de la actualización. La gente sube el rank esperando más poder expresivo, se olvida de `α` y concluye que un rank más alto perjudica. No fue así; sin darse cuenta bajaron el adapter 8×.

El punto de partida convencional es `α = 2r`. Trátalo como una convención con una justificación, no como un descubrimiento.

**rsLoRA** ([arXiv:2312.03732](https://arxiv.org/abs/2312.03732)) sostiene que el divisor `α/r` amortigua en exceso con rank alto y propone `α/√r` en su lugar, lo que mantiene estable el aprendizaje a medida que crece el rank. Si piensas trabajar con rank 64 o más, este es el ajuste que conviene conocer:

```python
LoraConfig(r=64, lora_alpha=16, use_rslora=True, ...)
```

### Elegir el rank

El rank es **capacidad**. Acota lo compleja que puede ser una actualización que exprese el adapter.

| Rank | Razonable para |
|---|---|
| 4 a 8 | Estilo, tono, formato de salida; datasets pequeños |
| 16 a 32 | Una tarea genuina con unos pocos miles de ejemplos |
| 64 a 128 | Tareas más difíciles, datasets mayores, comportamiento que exige razonamiento |
| 256+ | Acercándose a la capacidad del full fine-tuning en datasets grandes de SFT |

Dos diagnósticos que superan a adivinar:

**Subajuste.** La pérdida de entrenamiento se estanca por encima de donde la necesitas y más epochs no ayudan. No hay capacidad suficiente: sube el rank, o añade target modules (normalmente la mejor jugada, según la lección 10).

**Sobreajuste.** La pérdida de entrenamiento sigue cayendo mientras la pérdida held-out sube. Demasiada capacidad para los datos, o demasiados epochs. Baja el rank, añade dropout, consigue más datos o para antes.

Observa la asimetría con la lección de memoria: el rank cuesta muy poca memoria (lección 7), así que el costo de más rank es el riesgo de sobreajuste y un poco de cómputo, no que deje de caber en memoria. Eso invierte el instinto que muchos traen de la época en que la memoria era la restricción que mandaba.

### Dropout

`lora_dropout` aplica dropout a la entrada del adapter. Los valores típicos van de 0.0 a 0.1. Recurre a él cuando la pérdida held-out esté subiendo y no puedas conseguir más datos. En datasets grandes suele ser innecesario y simplemente ralentiza la convergencia.

### La configuración

```text
config := {
    rank: 16,
    alpha: 32,               # α/r = 2
    dropout: 0.05,
    adapt_bias: false,
    target_modules: [...],   # Lesson 10
}

model := attach_adapter(model, config)
print(model.trainable_parameter_count())
```

Esa última línea no es opcional. Es la comprobación de que tus target modules coincidieron con algo, y debería concordar con la aritmética que hiciste en la lección 8. Lee los nombres de los parámetros en la documentación de la versión instalada y no de memoria, porque esta superficie cambia entre versiones.

## Práctica

1. ▢ ¿Por qué `B` se inicializa en cero y `A` al azar, en lugar de ambas en cero o ambas al azar?

<details markdown="1"><summary>Comprobación</summary>

Una `B` en cero hace que `ΔW = 0` al principio, así que el entrenamiento empieza exactamente desde el base model sin ninguna perturbación de la que recuperarse. Una `A` aleatoria mantiene distinto de cero el gradiente del producto, así que el aprendizaje puede comenzar.

Ambas en cero: los gradientes se desvanecen, nada aprende. Ambas aleatorias: el modelo empieza como base más ruido en cada capa objetivo.

</details>

2. ▢ Subes el rank de 8 a 64 y dejas `α` en 16. La pérdida apenas se mueve. Diagnostica.

<details markdown="1"><summary>Comprobación</summary>

La escala `α/r` cayó de 2.0 a 0.25. El adapter tiene ocho veces la capacidad y un octavo de la influencia, así que el efecto neto es una actualización amortiguada, no una más fuerte.

Sube `α` a 128 para conservar la razón, o fija `use_rslora=True` para que el divisor pase a ser `√r`.

</details>

3. ▢ La pérdida de entrenamiento se aplana en un nivel demasiado alto para ser útil, y un cuarto epoch no ayuda. ¿Qué es esto, y cuáles son tus dos opciones?

<details markdown="1"><summary>Comprobación</summary>

Subajuste: al adapter le falta capacidad para expresar la actualización requerida.

Sube el rank, o amplía los target modules para cubrir más del modelo. Añadir target modules suele ser la mejor primera jugada, porque el MLP contiene la mayoría de los parámetros y a menudo es donde está la capacidad que falta. Más epochs no pueden arreglar un techo de capacidad.

</details>

4. ▢ ¿Qué combinación da la escala de actualización más fuerte?

    - a) `r = 8` con `alpha = 8`
    - b) `r = 8` con `alpha = 32`
    - c) `r = 32` con `alpha = 32`
    - d) `r = 64` con `alpha = 64`

<details markdown="1"><summary>Comprobación</summary>

**b)** `r = 8` con `alpha = 32`, que da `α/r = 4`.

Las demás son todas `α/r = 1`. La capacidad difiere entre ellas, pero la escala de actualización no, que es exactamente la distinción que el diseño de `α/r` pretendía hacer.

</details>

5. ▢ ¿Por qué LoRA puede usar un learning rate de diez a cien veces mayor que el full fine-tuning?

<details markdown="1"><summary>Comprobación</summary>

Los parámetros entrenables parten de una contribución cero y no son en sí mismos el almacén del conocimiento preentrenado. No hay estructura acumulada que dañar, y el término tiene que crecer desde la nada, así que necesita un paso mucho mayor para moverse de forma significativa en un número razonable de pasos.

</details>

6. ▢ ¿Cuándo *no* subirías el rank aunque el adapter esté subajustando?

<details markdown="1"><summary>Comprobación</summary>

Cuando el dataset es pequeño. Capacidad extra con pocos ejemplos compra memorización, no generalización: la pérdida de entrenamiento cae, la pérdida held-out sube.

La respuesta correcta ahí es más datos o mejores datos, o una tarea más estrecha, no un adapter más grande.

</details>

## Prácticas en el mundo real

- [ ] Construye tres configuraciones, `(8, 16)`, `(16, 32)` y `(64, 16)`, y anota el `α/r` de cada una y lo que predices que pasará. Guarda las predicciones.
- [ ] Imprime `print_trainable_parameters()` para cada una y concilia con tu aritmética de la lección 8.
- [ ] Mañana: encuentra una configuración de fine-tuning publicada por ahí, calcula su `α/r` y decide si el autor la eligió o la heredó.

## Para profundizar

- [Docs: LoRA, Hugging Face PEFT](https://huggingface.co/docs/peft/main/en/developer_guides/lora)
- [Paper: "A Rank Stabilization Scaling Factor for Fine-Tuning with LoRA", Kalajdzievski, arXiv:2312.03732](https://arxiv.org/abs/2312.03732)
- [Blog: "Practical Tips for Finetuning LLMs Using LoRA", Sebastian Raschka](https://magazine.sebastianraschka.com/p/practical-tips-for-finetuning-llms)
- [Hiperparámetros de LoRA](../reference/lora-hyperparameters.md)

---

¿No termina de quedar claro? Vuelve a leer la fuente primaria de arriba, ya que esta lección la comprime y en la compresión es donde se escapa la comprensión. Consulta el [glosario](../GLOSSARY.md) por si algún término te resultó resbaladizo.

Si lo poco claro es la propia lección y no el material, eso es un defecto: [abre un issue](https://github.com/TokenCemetery/teach/issues).
