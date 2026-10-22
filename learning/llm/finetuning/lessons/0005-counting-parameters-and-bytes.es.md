---
title: "5. Contar parámetros y bytes"
description: "Convertir la configuración de un modelo en gigabytes"
type: lesson
---

# Lección 5. Contar parámetros y bytes

**Vínculo con la misión:** "Dar cuenta de cada byte" está en la misión. Esta es la lección donde aprendes a hacer la aritmética en lugar de adivinar.
**Fuente principal:** [Docs: Model memory anatomy, Hugging Face Transformers](https://huggingface.co/docs/transformers/main/en/model_memory_anatomy)
**Requisitos previos:** [Lección 2](0002-where-the-weights-live.md), [Lección 4](0004-what-training-changes.md)

## Calentamiento

1. ▢ ¿Cuáles son las cuatro operaciones de un paso de entrenamiento?

<details markdown="1"><summary>Comprobación</summary>

Forward pass (conservando las activaciones), pérdida, backward pass (produciendo gradientes), paso del optimizador.

</details>

2. ▢ ¿Qué significa `-100` en un tensor de labels?

<details markdown="1"><summary>Comprobación</summary>

Ignora esta posición al calcular la pérdida. Es como se enmascaran los tokens del prompt para la pérdida solo de la completion.

</details>

3. ▢ ¿Qué proyecciones de atención se encogen con la grouped-query attention?

<details markdown="1"><summary>Comprobación</summary>

`k_proj` y `v_proj`. `q_proj` y `o_proj` conservan la dimensión oculta completa.

</details>

## Qué debes saber

Un parámetro es un número. La memoria es el tamaño de almacenamiento de ese número multiplicado por cuántos tienes. Todo lo demás de la etapa 2 es contabilidad sobre esto.

### Formatos numéricos

| Formato | Bytes | Notas |
|---|---|---|
| `float32` (fp32) | 4 | Precisión completa. El valor por defecto histórico para entrenar. |
| `bfloat16` (bf16) | 2 | El mismo rango de exponente que fp32, menos bits de mantisa. El valor por defecto moderno. |
| `float16` (fp16) | 2 | Más mantisa, un rango mucho menor, así que se desborda a infinito con más facilidad. |
| `int8` | 1 | Entero, necesita un factor de escala para interpretarse. |
| 4 bits (`nf4`, `int4`) | 0.5 | Dos valores por byte, más escalas por bloque. Etapa 4. |

Se prefiere bf16 a fp16 para entrenar pese a que almacena menos precisión, porque su rango de exponente coincide con el de fp32. El desbordamiento es un fallo del que es más difícil recuperarse que del error de redondeo, y el entrenamiento en fp16 históricamente necesitaba loss scaling para evitarlo.

### Los dos números que describen un modelo

Digamos que una model card afirma 1.5B parámetros. Entonces:

```text
weights in fp32 = 1.5e9 × 4 bytes = 6.0 GB
weights in bf16 = 1.5e9 × 2 bytes = 3.0 GB
weights in nf4  = 1.5e9 × 0.5     = 0.75 GB, plus quantisation constants
```

Esto es solo la memoria de los pesos para inferencia: el mínimo por tener el modelo en memoria, antes de cualquier activación, cualquier KV cache y, desde luego, antes de entrenar.

Un reflejo útil: **los gigabytes en bf16 ≈ el doble del número de parámetros en miles de millones.** Un modelo de 7B son unos 14 GB de pesos. Uno de 70B son unos 140 GB. Deberías poder producir estas cifras al instante.

### Dónde están los parámetros

De la lección 2, por capa:

```text
attention = 2 × d² + 2 × d × d_kv          (q, o full; k, v narrowed by GQA)
mlp       = 3 × d × d_ff                    (gate, up, down)
```

y en todo el modelo:

```text
total ≈ n_layers × (attention + mlp) + vocab × d × (1 or 2)
```

El último término se duplica cuando la proyección de salida no está atada al embedding de entrada. En los modelos pequeños este término no es despreciable: un vocabulario de 32k con tamaño oculto 2048 son 65M parámetros por copia, que es una fracción real de un modelo de 1.5B.

### Ejemplo resuelto

Un modelo con `d = 2048`, `d_kv = 256`, `d_ff = 5632`, 24 capas, vocabulario de 32k, embeddings atados:

```text
attention = 2 × 2048² + 2 × 2048 × 256  = 8.39M + 1.05M = 9.44M
mlp       = 3 × 2048 × 5632             = 34.6M
per layer                               = 44.0M
× 24 layers                             = 1.056B
embeddings = 32000 × 2048               = 0.066B
total                                   ≈ 1.12B
```

En bf16 son unos 2.2 GB de pesos. Observa que el MLP es el 79% del bloque; llévate eso a la lección 10.

![Dos barras de proporción. Una capa de 44.0M es aproximadamente un 21 por ciento de atención y un 79 por ciento de MLP. El modelo completo de 1.12B es aproximadamente un 94 por ciento de capas apiladas y un 5.9 por ciento de embeddings.](images/where-the-parameters-are.svg)

Las mismas sumas como proporciones, en los dos niveles que importan. Dentro de un bloque, la atención es la mitad más pequeña por un margen amplio, y por eso la cuestión de los target modules de la lección 10 es sobre todo una cuestión sobre el MLP. En todo el modelo, el término de embeddings es pequeño aquí y crece como proporción a medida que el modelo se encoge, que es el caso del que advierte el párrafo anterior.

### Qué no incluye esto todavía

Ya tienes el costo de los pesos. El entrenamiento añade tres categorías más, y dominan:

- Gradientes, uno por parámetro entrenable (lección 6)
- Estado del optimizador, dos por parámetro entrenable (lección 6)
- Activaciones, que dependen del batch size y de la longitud de secuencia y no del número de parámetros (lección 7)

Cualquiera que te diga que un modelo de 7B "necesita 14 GB para hacerle fine-tuning" ha contado solo la primera categoría. Ese es el error que esta etapa existe para eliminar.

## Práctica

1. ▢ ¿Cuántos gigabytes ocupan los pesos de un modelo de 13B en bf16? ¿En fp32? ¿En 4 bits?

<details markdown="1"><summary>Comprobación</summary>

bf16: 26 GB. fp32: 52 GB. 4 bits: unos 6.5 GB, más las constantes de cuantización.

Merece la pena poder hacer sin calculadora la cadena de duplicar y reducir a la mitad a partir del número de parámetros.

</details>

2. ▢ ¿Por qué se prefiere bf16 a fp16 para entrenar, dado que fp16 almacena más bits de mantisa?

<details markdown="1"><summary>Comprobación</summary>

bf16 conserva el rango de exponente de fp32, así que los valores no se desbordan a infinito. El rango estrecho de fp16 significa que los gradientes pueden desbordarse por arriba o por abajo, lo que históricamente exigía loss scaling para que funcionara siquiera.

El error de redondeo se degrada con gracia; el desbordamiento produce `NaN` y termina la ejecución. El intercambio favorece al rango.

</details>

3. ▢ Un modelo tiene `d = 4096`, `d_ff = 14336`, `d_kv = 1024`, 32 capas. Calcula los parámetros por capa y el total del modelo, ignorando los embeddings.

<details markdown="1"><summary>Comprobación</summary>

Atención: 2 × 4096² + 2 × 4096 × 1024 = 33.6M + 8.4M = 42.0M.
MLP: 3 × 4096 × 14336 = 176.2M.
Por capa: 218.2M. Por 32 capas ≈ 6.98B.

Aproximadamente un modelo de 7B, y el MLP es el 81% de él.

</details>

4. ▢ Dos modelos reportan 7B parámetros. Uno tiene un vocabulario de 32k, el otro de 256k. ¿Qué difiere, y en cuánto?

<details markdown="1"><summary>Comprobación</summary>

El costo de los embeddings. Con tamaño oculto 4096, un vocabulario de 32k son 131M parámetros por copia; uno de 256k son 1.05B, alrededor del 15% de todo el modelo en una sola tabla, y el doble si la proyección de salida no está atada.

Por tanto, el modelo de vocabulario grande tiene bastantes menos parámetros en sus bloques transformer, que es donde se acoplan los adapters.

</details>

5. ▢ Alguien dice que un modelo de 7B cabe con holgura en 16 GB para hacerle fine-tuning, porque los pesos en bf16 son 14 GB. ¿Qué falla en ese razonamiento?

<details markdown="1"><summary>Comprobación</summary>

Han contado solo los pesos. El full fine-tuning también necesita gradientes y dos momentos del optimizador por parámetro entrenable, más las activaciones, lo que es varias veces el costo de los pesos. Incluso la afirmación de 14 GB deja solo 2 GB para todo lo demás.

La próxima lección convierte esto en un número exacto, y la respuesta no se acerca.

</details>

## Prácticas en el mundo real

- [ ] Elige tres modelos de distintos tamaños. Solo a partir de sus archivos de configuración (`hidden_size`, `intermediate_size`, `num_hidden_layers`, `num_key_value_heads`, `vocab_size`), calcula los conteos de parámetros y contrástalos con las model cards.
- [ ] Carga un modelo en bf16 y mide la memoria realmente usada. Compárala con tu predicción y explica cualquier diferencia.
- [ ] Mañana: haz de cabeza la estimación de gigabytes en bf16 para cinco tamaños de modelo y luego verifícala con una calculadora.

## Para profundizar

- [Docs: Model memory anatomy, Hugging Face Transformers](https://huggingface.co/docs/transformers/main/en/model_memory_anatomy)
- [Presupuesto de memoria](../reference/memory-budget.md): la tabla hacia la que construye esta lección
- [Lección 6. Gradientes y estado del optimizador](0006-gradients-and-optimizer-state.md)

---

¿No termina de quedar claro? Vuelve a leer la fuente primaria de arriba, ya que esta lección la comprime y en la compresión es donde se escapa la comprensión. Consulta el [glosario](../GLOSSARY.md) por si algún término te resultó resbaladizo.

Si lo poco claro es la propia lección y no el material, eso es un defecto: [abre un issue](https://github.com/TokenCemetery/teach/issues).
