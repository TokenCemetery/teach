---
title: "6. Gradientes y estado del optimizador"
description: "Dieciséis bytes por parámetro entrenable, dos por uno congelado"
type: lesson
---

# Lección 6. Gradientes y estado del optimizador

**Vínculo con la misión:** Este es el argumento a favor de los adapters. Una vez que puedas derivar la cifra de dieciséis bytes por parámetro, LoRA deja de ser un truco y se convierte en la respuesta obvia.
**Fuente principal:** [Paper: "ZeRO: Memory Optimizations Toward Training Trillion Parameter Models", Rajbhandari et al., arXiv:1910.02054](https://arxiv.org/abs/1910.02054)
**Requisitos previos:** [Lección 4](0004-what-training-changes.md), [Lección 5](0005-counting-parameters-and-bytes.md)

## Calentamiento

1. ▢ Pesos de un modelo de 7B en bf16: ¿cuántos gigabytes?

<details markdown="1"><summary>Comprobación</summary>

Unos 14 GB. Dos bytes por parámetro, así que los gigabytes en bf16 son aproximadamente el doble de los miles de millones de parámetros.

</details>

2. ▢ ¿Qué dos tensores mantiene AdamW por parámetro entrenable?

<details markdown="1"><summary>Comprobación</summary>

Una media móvil de los gradientes y una media móvil de los gradientes al cuadrado, el primer y el segundo momento. Cada uno tiene la forma del parámetro.

</details>

3. ▢ ¿Por qué bf16 supera a fp16 para entrenar?

<details markdown="1"><summary>Comprobación</summary>

Su rango de exponente coincide con el de fp32, así que los valores no se desbordan a infinito. El error de redondeo se puede sobrevivir; `NaN` no.

</details>

## Qué debes saber

Todo lo que cuesta un parámetro entrenable, por parámetro:

| Categoría | Entrenamiento en fp32 | Precisión mixta (cómputo en bf16, master en fp32) |
|---|---|---|
| Pesos | 4 | 2 (bf16) + 4 (copia master en fp32) |
| Gradientes | 4 | 2 |
| Primer momento de AdamW | 4 | 4 |
| Segundo momento de AdamW | 4 | 4 |
| **Total** | **16 bytes** | **16 bytes** |

![Dos barras de bytes por parámetro entrenable, ambas de dieciséis bytes de largo. Con fp32, los dieciséis bytes son cuatro cada uno para pesos, gradientes y los dos momentos. Con precisión mixta, los pesos son dos bytes de bf16 más una copia master de cuatro bytes, los gradientes son dos bytes, y ambos momentos se quedan en cuatro.](images/mixed-precision-same-total.svg)

La columna de la derecha es la parte que sorprende a la gente. **La precisión mixta no reduce el total.**

Ambas barras llegan a la misma marca, y ese es todo el hallazgo. Las dos piezas resaltadas son los tensores que de verdad se redujeron a la mitad, cuatro bytes ahorrados entre ambas, y la copia master que está junto a la primera son cuatro bytes devueltos de inmediato. Todo lo que queda a su derecha no se movió en absoluto. Reduce a la mitad los tensores de pesos y de gradientes, y luego vuelve a añadir una copia master en fp32 de los pesos, porque acumular actualizaciones diminutas en un valor bf16 las pierde en silencio. Los momentos del optimizador se quedan en fp32 por la misma razón. La ventaja de la precisión mixta es el throughput aritmético, no la memoria.

Así que: **16 bytes por parámetro entrenable**, antes de una sola activación.

### Qué significa eso

```text
1.5B trainable × 16 bytes = 24 GB
7B   trainable × 16 bytes = 112 GB
70B  trainable × 16 bytes = 1120 GB
```

Hacer full fine-tuning de un modelo de 7B necesita 112 GB solo de estado de optimizador y de pesos, y luego las activaciones encima. Es territorio de varias GPU para un modelo cuyos pesos son 14 GB. La brecha entre "el modelo cabe" y "entrenar el modelo cabe" es un factor de ocho, y se debe por entero a los gradientes y al estado del optimizador.

### La vía de escape

Mira de nuevo la tabla y observa por qué se multiplican los 16 bytes: por el número de parámetros **entrenables**, no por el de parámetros totales. Los parámetros congelados cuestan 2 bytes cada uno, por sus pesos, y nada más. Sin gradiente. Sin momentos.

Ese es todo el argumento a favor de los adapters:

```text
frozen parameter   = 2 bytes  (bf16 weights only)
trainable parameter = 16 bytes (weights + master + grad + 2 moments)
```

Congela el base model, añade unos pocos millones de parámetros entrenables y el segundo término casi desaparece. Resuelto para un base de 7B con 4M de parámetros de adapter entrenables:

```text
frozen base    7B  × 2  = 14.0 GB
trainable      4M  × 16 = 0.064 GB
```

El estado del optimizador del adapter son 64 MB. Se ha convertido en un error de redondeo frente a los pesos del base, y los pesos del base son la única parte que puedes atacar por separado, con cuantización, en la etapa 4.

### Medidas parciales, y por qué no bastan

Antes de que existieran los adapters, la gente reducía este costo de otras maneras. Todas siguen disponibles y todas siguen estando acotadas:

| Técnica | Qué ahorra | Qué cuesta |
|---|---|---|
| Optimizador de 8 bits | Momentos a 1 byte en lugar de 4: 16 → 10 bytes | Ligero riesgo de calidad; sigue siendo lineal en el número de entrenables |
| SGD con momentum | Un momento en lugar de dos: 16 → 12 bytes | Convergencia notablemente peor en los transformers |
| Sharding del optimizador (ZeRO) | Divide el estado entre N dispositivos | Necesita N dispositivos y una interconexión rápida |
| Offload a la CPU | Saca el estado del acelerador | Limitado por el ancho de banda; pasos mucho más lentos |

Cada una de ellas escala la constante. Ninguna cambia el hecho de que el costo es proporcional al número de parámetros entrenables. Los adapters atacan el multiplicador, y por eso ganan por órdenes de magnitud y no por factores.

### Por qué los momentos no se pueden simplemente eliminar

Una pregunta razonable: si los dos momentos de AdamW son dos tercios del costo, ¿por qué no usar SGD simple? Porque el entrenamiento de transformers depende del escalado del paso por parámetro de Adam. Las magnitudes de los gradientes varían enormemente entre los parámetros de un transformer, y un único learning rate global las sirve mal. El segundo momento es lo que permite que cada parámetro dé un paso de tamaño apropiado. Esto es empírico, consistente y no es un problema de ajuste que puedas hacer desaparecer a base de desearlo.

## Práctica

1. ▢ Deriva la memoria necesaria para hacer full fine-tuning de un modelo de 3B con AdamW en precisión mixta, sin contar las activaciones.

<details markdown="1"><summary>Comprobación</summary>

16 bytes por parámetro entrenable × 3e9 = 48 GB.

Desglosado: 6 GB de pesos en bf16 + 12 GB de master en fp32 + 6 GB de gradientes en bf16 + 12 GB de primer momento + 12 GB de segundo momento = 48 GB.

</details>

2. ▢ ¿Por qué la precisión mixta no reduce la memoria total de entrenamiento?

<details markdown="1"><summary>Comprobación</summary>

Reduce a la mitad los pesos y los gradientes, pero añade una copia master en fp32 de los pesos y deja ambos momentos del optimizador en fp32. El ahorro y la adición se cancelan, y se vuelve a los 16 bytes.

La copia master no es opcional: sumar repetidamente una actualización muy pequeña a un valor bf16 se redondea a ningún cambio en absoluto, así que la actualización se pierde.

</details>

3. ▢ Un base de 7B está congelado en bf16 y entrenas un adapter de 20M de parámetros. ¿Total, sin contar las activaciones?

<details markdown="1"><summary>Comprobación</summary>

14 GB por el base congelado (7e9 × 2) más 0.32 GB por el adapter (2e7 × 16), así que unos 14.3 GB.

Frente a 112 GB del full fine-tuning: una reducción de 7.8×, y casi todo lo que queda es el base congelado. La etapa 4 ataca ese resto.

</details>

4. ▢ ¿Qué cambio reduce más la memoria del optimizador para un modelo fijo?

    - a) Cambiar el optimizador de AdamW a SGD
    - b) Cambiar la precisión de cómputo a bf16
    - c) Congelar el base y entrenar un adapter
    - d) Cambiar al enmascarado de pérdida solo de la completion

<details markdown="1"><summary>Comprobación</summary>

**c)** Congelar el base y entrenar un adapter.

(a) elimina un momento de dos, ahorrando una cuarta parte. (b) no ahorra nada en total, como se vio arriba. (d) cambia qué posiciones contribuyen a la pérdida, no cuántos parámetros tienen estado. Solo (c) ataca el número de parámetros entrenables, que es el multiplicador de todo.

</details>

5. ▢ Alguien propone un optimizador de 8 bits para poder hacer full fine-tuning de un modelo de 70B en un solo acelerador de 80 GB. Haz la aritmética y responde.

<details markdown="1"><summary>Comprobación</summary>

Los momentos de 8 bits dan 2 + 4 + 2 + 1 + 1 = 10 bytes por parámetro. 70e9 × 10 = 700 GB. Todavía casi nueve veces un dispositivo de 80 GB, antes de las activaciones.

La técnica es real y útil; el plan se equivoca por un orden de magnitud. Este es el valor de hacer la aritmética antes del experimento.

</details>

6. ▢ En una frase: ¿por qué los parámetros congelados cuestan tanto menos que los entrenables?

<details markdown="1"><summary>Comprobación</summary>

Un parámetro congelado solo necesita almacenar su propio valor para el forward pass, mientras que uno entrenable necesita además un gradiente, dos momentos del optimizador y una copia master de alta precisión: ocho veces más.

</details>

## Prácticas en el mundo real

- [ ] Construye de memoria en papel la tabla de 16 bytes. Luego calcula la memoria total de entrenamiento para tres tamaños de modelo que de verdad te importen.
- [ ] Carga un modelo pequeño, ejecuta un paso de entrenamiento con AdamW sobre todos los parámetros y registra la memoria pico. Compárala con tu predicción.
- [ ] Mañana: repite con el base congelado y solo un adapter pequeño entrenable. La proporción que midas es el argumento de la etapa 3.

## Para profundizar

- [Paper: "ZeRO: Memory Optimizations Toward Training Trillion Parameter Models", Rajbhandari et al., arXiv:1910.02054](https://arxiv.org/abs/1910.02054): la contabilidad canónica de estas categorías
- [Paper: "8-bit Optimizers via Block-wise Quantization", Dettmers et al., arXiv:2110.02861](https://arxiv.org/abs/2110.02861)
- [Presupuesto de memoria](../reference/memory-budget.md)
- [Lección 8. La idea de bajo rank](0008-the-low-rank-idea.md): la respuesta a esta lección

---

¿No termina de quedar claro? Vuelve a leer la fuente primaria de arriba, ya que esta lección la comprime y en la compresión es donde se escapa la comprensión. Consulta el [glosario](../GLOSSARY.md) por si algún término te resultó resbaladizo.

Si lo poco claro es la propia lección y no el material, eso es un defecto: [abre un issue](https://github.com/TokenCemetery/teach/issues).
