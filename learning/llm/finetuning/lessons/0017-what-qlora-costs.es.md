---
title: "17. Lo que realmente cuesta QLoRA"
description: "Separar la degradación del base de la degradación del entrenamiento"
type: lesson
---

# Lección 17. Lo que realmente cuesta QLoRA

**Vínculo con la misión:** La misión dice "explicar las diferencias medidas, no las anunciadas". Esta lección es la medición.
**Fuente principal:** [Paper: "QLoRA: Efficient Finetuning of Quantized LLMs", Dettmers et al., arXiv:2305.14314](https://arxiv.org/abs/2305.14314)
**Requisitos previos:** [Lección 16](0016-training-through-a-quantized-base.md)

## Calentamiento

1. ▢ ¿Por qué un base congelado de 4 bits puede seguir pasando gradientes?

<details markdown="1"><summary>Comprobación</summary>

Es una constante en el grafo. Propagar el gradiente requiere leerlo a alta precisión, no derivar respecto a él, y no se almacena ningún gradiente para él.

</details>

2. ▢ ¿Qué componente de QLoRA es genuinamente específico de CUDA?

<details markdown="1"><summary>Comprobación</summary>

Los optimizadores paginados, que dependen de la memoria unificada de NVIDIA. Y son los que menos importan para el entrenamiento con adapters, donde el estado del optimizador es pequeño.

</details>

3. ▢ ¿Dónde fusionas un adapter entrenado contra un base de 4 bits?

<details markdown="1"><summary>Comprobación</summary>

En el base de precisión completa, y cuantizas después si hace falta.

</details>

## Qué debes saber

### La afirmación del paper, expuesta con precisión

El resultado principal de QLoRA es que el fine-tuning con adapters en NF4 de 4 bits puede igualar el rendimiento del fine-tuning en 16 bits en las tareas medidas. Es un resultado fuerte y es genuino.

También es una afirmación sobre **una configuración concreta en benchmarks concretos**. Lo que no establece:

- Que NF4 sea gratis en *tu* tarea. Los benchmarks de seguimiento de instrucciones no son tu distribución de producción.
- Que la cuantización sea gratis a cualquier escala. El error de cuantización es una perturbación relativa fija, y los modelos pequeños tienen menos redundancia para absorberla, así que la degradación suele verse más en los modelos pequeños que en los grandes.
- Que toda implementación de 4 bits sea equivalente. El tipo de cuantización, el tamaño de bloque, si la doble cuantización está activada, el compute dtype y la calidad del kernel varían.

Leer la afirmación de un paper como "la cuantización es gratis" es exactamente el modo de fallo al que apunta la frase de la misión *medido, no anunciado*.

### Separar los dos costos

Hay dos preguntas de calidad distintas y confundirlas hace los resultados ininterpretables.

**Costo 1. El base cuantizado es un modelo peor, antes de cualquier entrenamiento.** Puramente una propiedad de la representación.

**Costo 2. Entrenar contra un base cuantizado produce un adapter peor.** Una propiedad del proceso de entrenamiento, encima del costo 1.

Mídelos por separado:

| Configuración | Aísla |
|---|---|
| Base en bf16, sin adapter | El punto de referencia |
| Base de 4 bits, sin adapter | El costo 1, el daño de la cuantización por sí solo |
| Base en bf16 + adapter | El techo del entrenamiento |
| Base de 4 bits + adapter | Los costos 1 y 2 combinados |
| Adapter entrenado en 4 bits fusionado en un base en bf16 | Si el costo 1 sobrevive en el artefacto |

![Precisión del base frente a adapter como una cuadrícula de dos por dos que contiene el punto de referencia, el techo del entrenamiento, el costo 1 por sí solo y ambos costos juntos, con una quinta caja debajo de la cuadrícula para un adapter entrenado en 4 bits y fusionado en un base en bf16.](images/the-one-that-is-not-a-cell.svg)

Cuatro de las cinco configuraciones son celdas de una misma cuadrícula. La quinta no lo es, porque usa un base distinto para entrenar que para desplegar, y una configuración sin celda donde colocarse es fácil de olvidar ejecutar.

Esa última fila es la interesante y se omite de forma rutinaria. Entrenaste contra un base degradado, pero puedes *desplegar* contra el de precisión completa. Si el adapter aprendió a compensar el error de cuantización, y por tanto queda desajustado cuando el error desaparece, es una pregunta empírica con una respuesta real para tu tarea. Mídelo en lugar de suponerlo en uno u otro sentido.

### Cómo medirlo con honestidad

**Mantén todo lo demás fijo.** Mismos datos, misma partición, misma seed, mismo rank, alpha, learning rate, schedule y pasos. Una variable: la precisión del base. Una comparación con dos cambios dentro no es una comparación.

**Usa una métrica de la tarea, no la pérdida.** La pérdida no es comparable entre configuraciones de la manera que quieres, y no es lo que te importa. La lección 23 cubre la elección de métrica.

**Reporta una dispersión, no un punto.** Ejecuta cada configuración con tres seeds. Si tu variación de seed a seed es de 2 puntos y tu efecto de cuantización es de 1 punto, no has medido nada, y esto ocurre constantemente. Una comparación de una sola seed entre dos configuraciones es una anécdota.

**Mide también velocidad y memoria.** Son la razón por la que estás considerando la cuantización, así que pertenecen a la misma tabla que la calidad.

### Una tabla de resultados que merece producirse

| Config | Métrica de la tarea | Memoria pico | Seg/paso |
|---|---|---|---|
| Base en bf16 + adapter | | | |
| Base NF4 + adapter | | | |
| NF4 sin doble cuantización | | | |
| int4 en lugar de NF4 | | | |
| NF4, fusionado en bf16 para la eval | | | |

Rellenar esto una vez, en una tarea que te importe, vale más que cualquier cantidad de lectura sobre cuantización. La última fila en particular te dirá algo que no se puede consultar.

### Qué esperar, para que puedas sorprenderte

Expectativas aproximadas de la literatura y de la práctica común, como un prior que actualizar y no como un resultado:

- **Memoria:** reducción de aproximadamente 4× en los pesos del base. Fiable, es aritmética.
- **Velocidad:** más lento por paso, a menudo de forma notable. La descuantización es trabajo real.
- **Calidad:** degradación pequeña, con frecuencia dentro del ruido de las seeds en modelos más grandes, más visible en los más pequeños y en tareas con márgenes estrechos.
- **NF4 frente a int4:** NF4 mejor con idéntico almacenamiento.
- **Doble cuantización:** ahorro de memoria con un efecto despreciable en la calidad.

Si tus mediciones discrepan con fuerza de estas, merece la pena investigarlo en lugar de descartarlo. La causa más común es una ruta de kernel sin optimizar en tu backend, o una comparación donde cambió más de una cosa.

### Cuándo recurrir a QLoRA

**Úsalo cuando la memoria sea la restricción que manda**, es decir, cuando un base en bf16 más las activaciones no cabe y la alternativa es no entrenar en absoluto, o entrenar un modelo más pequeño. Un modelo grande de 4 bits suele superar a uno pequeño en bf16.

**No lo uses cuando la memoria no sea la restricción.** Si bf16 cabe, cuantizar te cuesta velocidad y un poco de calidad por nada. El reflejo de los tutoriales de cargar siempre en 4 bits es un costo sin beneficio cuando de todos modos tenías la memoria.

## Práctica

1. ▢ Enuncia la afirmación principal de QLoRA y luego enuncia lo que no establece.

<details markdown="1"><summary>Comprobación</summary>

Afirmación: el fine-tuning con adapters en NF4 de 4 bits puede igualar el rendimiento del fine-tuning en 16 bits en los benchmarks medidos.

No establece: que esto se cumpla en tu tarea y tu distribución, que se cumpla por igual a escala de modelo pequeño, o que cualquier implementación de 4 bits sea equivalente a la del paper.

</details>

2. ▢ Nombra los dos costos de calidad separados y cómo los aíslas.

<details markdown="1"><summary>Comprobación</summary>

Costo 1: el base cuantizado es un modelo peor antes de entrenar, así que mide el base sin adapter, cuantizado frente a no cuantizado.

Costo 2: entrenar contra un base cuantizado produce un adapter peor, así que compara adapters entrenados sobre bases cuantizados frente a bases de precisión completa, con todo lo demás fijo.

</details>

3. ▢ Mides 71.2 para bf16 y 70.8 para NF4. ¿Te está costando la cuantización 0.4 puntos?

<details markdown="1"><summary>Comprobación</summary>

Se desconoce. Sin una dispersión de seeds no puedes distinguir 0.4 del ruido, y la variación de seed a seed en una ejecución de fine-tuning con frecuencia lo supera.

Ejecuta tres seeds por configuración y compara distribuciones. Una diferencia de una sola seed de este tamaño no es un resultado.

</details>

4. ▢ ¿Qué comparación se omite con más frecuencia, y qué te dice?

<details markdown="1"><summary>Comprobación</summary>

Evaluar un adapter entrenado en 4 bits fusionado en el base de precisión completa.

Te dice si el costo de la cuantización tiene siquiera que sobrevivir en tu artefacto desplegado. Entrenaste barato, pero nada te obliga a servir barato. También revela si el adapter se adaptó al propio error de cuantización.

</details>

5. ▢ Tu ejecución en bf16 cabe en memoria con holgura. ¿Deberías pasar a 4 bits de todos modos?

<details markdown="1"><summary>Comprobación</summary>

No. Pagarías pasos más lentos y un pequeño riesgo de calidad para ahorrar memoria que no te faltaba.

La cuantización es una respuesta a una restricción de memoria que manda. Aplicarla por reflejo, porque lo hizo el tutorial, es un costo sin el beneficio correspondiente.

</details>

6. ▢ NF4 degrada de forma notable tu tarea con un modelo de 1B pero el paper reportó que no había degradación. ¿Estás contradiciendo al paper?

<details markdown="1"><summary>Comprobación</summary>

No. El error de cuantización es una perturbación relativa fija y los modelos pequeños tienen menos redundancia para absorberla, así que la degradación suele verse más a escala pequeña. Tu tarea y tu métrica también difieren de los benchmarks medidos.

Ambos resultados pueden ser correctos. Es precisamente por eso por lo que la misión pide diferencias medidas y no anunciadas.

</details>

## Prácticas en el mundo real

- [ ] Rellena la tabla comparativa de cinco filas en una tarea que te importe. Tres seeds por fila.
- [ ] Mide la memoria pico y los segundos por paso de cada fila, junto al número de calidad.
- [ ] Evalúa el adapter entrenado en 4 bits fusionado en el base en bf16. Anota si superó, igualó o perdió frente a la versión servida en 4 bits.
- [ ] Mañana: escribe un párrafo que diga qué te costó *a ti* la cuantización, con números, y en qué se diferencia de lo que esperabas.

## Para profundizar

- [Paper: "QLoRA: Efficient Finetuning of Quantized LLMs", Dettmers et al., arXiv:2305.14314](https://arxiv.org/abs/2305.14314): lee la sección de limitaciones
- [r/LocalLLaMA](https://www.reddit.com/r/LocalLLaMA/): la mayor reserva de mediciones de profesionales en hardware de consumo, y merece la pena contrastar con ella tus números
- [Lección 23. Métricas que significan algo](0023-metrics-that-mean-something.md)

---

¿No termina de quedar claro? Vuelve a leer la fuente primaria de arriba, ya que esta lección la comprime y en la compresión es donde se escapa la comprensión. Consulta el [glosario](../GLOSSARY.md) por si algún término te resultó resbaladizo.

Si lo poco claro es la propia lección y no el material, eso es un defecto: [abre un issue](https://github.com/TokenCemetery/teach/issues).
