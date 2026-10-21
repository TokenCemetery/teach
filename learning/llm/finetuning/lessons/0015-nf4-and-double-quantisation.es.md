---
title: "15. NF4 y doble cuantización"
description: "Las dos ideas que QLoRA aportó de verdad"
type: lesson
---

# Lección 15. NF4 y doble cuantización

**Vínculo con la misión:** Estas son las dos ideas que aportó QLoRA. Conocerlas separa entender el paper de haber leído el abstract.
**Fuente principal:** [Paper: "QLoRA: Efficient Finetuning of Quantized LLMs", Dettmers et al., arXiv:2305.14314](https://arxiv.org/abs/2305.14314)
**Requisitos previos:** [Lección 14](0014-quantisation-from-first-principles.md)

## Calentamiento

1. ▢ ¿Por qué cuantización por bloques y no por tensor?

<details markdown="1"><summary>Comprobación</summary>

Un outlier solo fija la escala dentro de su propio bloque, conteniendo el daño a 64 o 128 valores en lugar de a todo el tensor.

</details>

2. ▢ ¿Bytes reales por parámetro para pesos de 4 bits con escalas en fp32 y tamaño de bloque 64?

<details markdown="1"><summary>Comprobación</summary>

0.5625, o sea 4.5 bits, con 0.5 bits de pura sobrecarga de contabilidad.

</details>

3. ▢ ¿En qué precisión está el matmul, para un base de 4 bits?

<details markdown="1"><summary>Comprobación</summary>

En una mayor, normalmente bf16. Los bloques se descuantizan al vuelo y las copias descuantizadas se descartan.

</details>

## Qué debes saber

QLoRA aportó tres cosas: NF4, la doble cuantización y los optimizadores paginados. Las dos primeras son ideas sobre la representación y son las interesantes. La tercera es una mitigación de ingeniería, cubierta en la lección 16.

### NF4, o NormalFloat

Con 4 bits tienes 16 niveles. ¿Dónde deberías ponerlos?

El espaciado uniforme, como en el int4 simple, los coloca a intervalos iguales a lo largo del rango. Eso es óptimo si los valores están distribuidos de manera uniforme. **Los pesos de las redes neuronales no están distribuidos de manera uniforme.** Están aproximadamente centrados en cero y distribuidos normalmente, así que la mayoría de los valores se agrupan cerca de cero y pocos están cerca de los extremos.

Por tanto, los niveles uniformes desperdician resolución: muchos niveles quedan fuera, en las colas, donde casi no viven pesos, mientras que la región densa cerca de cero recibe demasiados pocos.

La respuesta de NF4: colocar los 16 niveles en los **cuantiles de una distribución normal estándar**, de modo que cada nivel cubra la misma cantidad de *masa de probabilidad* en lugar de la misma cantidad de rango. Los niveles son densos cerca de cero y dispersos en las colas, a la medida de dónde están realmente los pesos. El paper lo describe como óptimo en el sentido de la teoría de la información para datos con media cero y distribución normal.

Para que esto funcione, cada bloque debe normalizarse primero a `[−1, 1]` dividiéndolo por su absmax, que es exactamente lo que la cuantización por bloques ya almacenaba. Así que NF4 no es maquinaria extra; es una mejor elección de los 16 niveles dentro del esquema de la lección 14.

```text
int4:  levels evenly spaced        → resolution wasted in empty tails
nf4:   levels at normal quantiles  → resolution where the weights are
```

La consecuencia es que NF4 supera a int4 con el mismo ancho de bits, gratis. Sin almacenamiento extra, solo un mejor codebook.

Dos límites honestos:

- La ganancia depende de que los pesos estén realmente cerca de una normal. Normalmente lo están, por bloque, tras el preentrenamiento. Es una propiedad empírica, no una garantía.
- NF4 es un formato de *pesos*. No es la herramienta adecuada para las activaciones, que tienen distribuciones distintas y menos bien portadas.

### Doble cuantización

Vuelve a la sobrecarga de la lección 14. Por parámetro, con tamaño de bloque 64 y escalas en fp32:

```text
weights            0.5     bytes
scales   4/64  =   0.0625  bytes
                  ────────
                   0.5625  bytes  (4.5 bits)
```

Esas escalas son a su vez solo números en un tensor, y hay muchísimas. Así que cuantízalas también.

La doble cuantización toma las escalas de bloque en fp32, las agrupa (el paper usa bloques de 256) y las almacena en 8 bits con su propia escala de segundo nivel. El resultado:

```text
first-level scales at 8 bits:   1/64      = 0.015625 bytes/param
second-level scales:            4/(64·256) ≈ 0.000244 bytes/param
weights:                                     0.5      bytes/param
                                            ──────────
                                             0.5159   bytes/param  (~4.13 bits)
```

El paper reporta el ahorro como aproximadamente **0.37 bits por parámetro** de media, que para un modelo de 65B son unos 3 GB. Es una cantidad real de memoria recuperada de pura contabilidad.

![Tres barras de bits por parámetro. El segmento de peso de cuatro bits es idéntico en las tres. Solo son 4 bits; con escalas de bloque en fp32 se añade un segmento de medio bit, que llega a 4.5; con doble cuantización ese segmento se encoge a aproximadamente un octavo de bit, y llega a unos 4.13.](images/the-tax-not-the-payload.svg)

Observa la forma de la idea: las constantes de cuantización eran un impuesto fijo del esquema, y la doble cuantización redujo el impuesto en lugar de la carga útil.

Las barras dicen lo mismo sin la aritmética. El segmento gris tiene la misma longitud las tres veces, porque nada de los pesos cambió; toda diferencia entre 4, 4.5 y 4.13 bits es la pequeña pieza resaltada del extremo. Un esquema que hubiera reducido la carga útil habría movido el gris. Es una victoria pequeña, ingeniosa y del todo mecánica, y es la razón por la que QLoRA de 4 bits aterriza cerca de 4.1 bits por parámetro en la práctica y no en 4.5.

### El resultado de memoria

Recalcula el ejemplo de la lección 6 con un base de 4 bits. Un modelo de 7B con un adapter de 20M de parámetros:

| | Base en bf16 | Base de 4 bits |
|---|---|---|
| Pesos del base congelado | 14.0 GB | ~3.6 GB |
| Estado del adapter (16 B/param) | 0.32 GB | 0.32 GB |
| **Subtotal** | **14.3 GB** | **3.9 GB** |

Frente a los 112 GB del full fine-tuning, el costo fijo de la ejecución del adapter con 4 bits es inferior a 4 GB. Las activaciones (lección 7) son ahora decididamente el término dominante, lo que significa que el gradient checkpointing importa aquí más que en ningún otro lugar del espacio de trabajo.

Este es el resultado que hizo significativo a QLoRA: llevó el fine-tuning de modelos grandes de los clústeres a un solo dispositivo.

### La configuración

```text
quant_config := {
    load_in_4bit: true,
    quant_type: "nf4",            # not "fp4"
    use_double_quant: true,       # the 0.37 bits/param saving
    compute_dtype: "bfloat16",    # storage is 4-bit; compute is not
}
```

Cuatro ajustes, cada uno de los cuales se corresponde con algo de esta lección. `bnb_4bit_compute_dtype` es el que la gente deja en su valor por defecto y no debería: es la precisión en la que se multiplican los bloques descuantizados, y dejarlo en fp32 descarta buena parte de la ventaja de velocidad.

Como siempre, confirma estos nombres contra la documentación de la versión instalada.

## Práctica

1. ▢ ¿Por qué NF4 supera a int4 con el mismo ancho de bits?

<details markdown="1"><summary>Comprobación</summary>

Coloca sus 16 niveles en los cuantiles de una distribución normal en lugar de a intervalos uniformes, así que la resolución se concentra donde realmente se agrupan los pesos, cerca de cero, en lugar de gastarse en colas vacías.

Mismo almacenamiento, mejor codebook. La precondición es normalizar primero cada bloque a `[−1, 1]`, lo que la cuantización por bloques ya hace.

</details>

2. ▢ ¿Qué comprime exactamente la doble cuantización, y cuánto ahorra aproximadamente?

<details markdown="1"><summary>Comprobación</summary>

Las escalas de bloque de primer nivel, es decir, las constantes de cuantización y no los pesos. Se almacenan en 8 bits en grupos de 256, con una pequeña escala de segundo nivel.

El paper reporta unos 0.37 bits por parámetro de media, aproximadamente 3 GB para un modelo de 65B. Lleva los 4 bits con sobrecarga de unos 4.5 bits a unos 4.1.

</details>

3. ▢ Calcula la memoria fija total para un base de 13B en NF4 con doble cuantización, más un adapter de 30M.

<details markdown="1"><summary>Comprobación</summary>

Base: 13e9 × 0.5159 ≈ 6.7 GB. Adapter: 3e7 × 16 = 0.48 GB. Unos 7.2 GB fijos.

Compara con 26 GB de un base en bf16 más el adapter, y 208 GB del full fine-tuning. Las activaciones se suman luego encima de los 7.2 GB.

</details>

4. ▢ ¿Qué componente de QLoRA ahorra más memoria?

    - a) NF4 en lugar de la cuantización uniforme int4 simple
    - b) Almacenar el base congelado en 4 bits en lugar de bf16
    - c) La doble cuantización de las escalas de bloque de primer nivel
    - d) Los optimizadores paginados que vuelcan estado durante los picos de memoria

<details markdown="1"><summary>Comprobación</summary>

**b)** Almacenar el base congelado en 4 bits en lugar de bf16, una reducción de 4× sobre el mayor término fijo.

NF4 mejora la calidad con idéntico almacenamiento. La doble cuantización ahorra unos 0.37 bits por parámetro. Los optimizadores paginados evitan los fallos en los picos en lugar de reducir el uso en régimen estable.

</details>

5. ▢ ¿Por qué NF4 es inadecuado para cuantizar activaciones?

<details markdown="1"><summary>Comprobación</summary>

La colocación de sus niveles se deriva de una suposición de que los valores tienen media cero y son aproximadamente normales. Los pesos tras el preentrenamiento se ajustan razonablemente a eso; las activaciones no, porque llevan features outlier sistemáticas de gran magnitud, así que los cuantiles normales son el codebook equivocado para ellas.

</details>

6. ▢ Fijas `load_in_4bit=True` y dejas `bnb_4bit_compute_dtype` en su valor por defecto. ¿Qué has cedido probablemente?

<details markdown="1"><summary>Comprobación</summary>

Velocidad. El almacenamiento sigue siendo de 4 bits y la memoria sigue ahorrándose, pero si el compute dtype toma por defecto fp32, cada bloque descuantizado se multiplica a precisión completa, renunciando a buena parte de la ventaja de throughput.

Fíjalo en bf16 de forma deliberada. La precisión de almacenamiento y la precisión de cómputo son decisiones separadas.

</details>

## Prácticas en el mundo real

- [ ] Calcula en papel los bytes por parámetro para 4 bits con y sin doble cuantización, con tamaño de bloque 64. Confirma que la diferencia se acerca a 0.37 bits.
- [ ] Carga el mismo modelo en bf16 y en NF4, midiendo la memoria las dos veces. Compara con tu predicción.
- [ ] Mañana: genera el mismo prompt con ambos, de forma greedy, y lee las salidas lado a lado. Hazte una primera impresión del costo en calidad; la lección 17 lo convierte en una medición.

## Para profundizar

- [Paper: "QLoRA: Efficient Finetuning of Quantized LLMs", Dettmers et al., arXiv:2305.14314](https://arxiv.org/abs/2305.14314): las secciones 3 y 4 son esta lección
- [Docs: bitsandbytes quantization, Hugging Face Transformers](https://huggingface.co/docs/transformers/main/en/quantization/bitsandbytes)
- [Presupuesto de memoria](../reference/memory-budget.md)

---

¿No termina de quedar claro? Vuelve a leer la fuente primaria de arriba, ya que esta lección la comprime y en la compresión es donde se escapa la comprensión. Consulta el [glosario](../GLOSSARY.md) por si algún término te resultó resbaladizo.

Si lo poco claro es la propia lección y no el material, eso es un defecto: [abre un issue](https://github.com/TokenCemetery/teach/issues).
