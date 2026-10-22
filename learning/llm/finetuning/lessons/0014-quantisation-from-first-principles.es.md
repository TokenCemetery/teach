---
title: "14. Cuantización desde los primeros principios"
description: "Escalas por bloques, y por qué un solo outlier arruina un tensor"
type: lesson
---

# Lección 14. Cuantización desde los primeros principios

**Vínculo con la misión:** QLoRA es LoRA más una idea. Esta lección es esa idea, enseñada por separado para que la siguiente sea corta.
**Fuente principal:** [Paper: "LLM.int8(): 8-bit Matrix Multiplication for Transformers at Scale", Dettmers et al., arXiv:2208.07339](https://arxiv.org/abs/2208.07339)
**Requisitos previos:** [Lección 5](0005-counting-parameters-and-bytes.md), [cuantización](../GLOSSARY.md)

## Calentamiento

1. ▢ ¿Bytes por parámetro en fp32, bf16 y 4 bits?

<details markdown="1"><summary>Comprobación</summary>

Cuatro, dos y medio, más las constantes de cuantización en el caso de 4 bits, que esta lección explica.

</details>

2. ▢ Para un base de 7B con un adapter de 20M, ¿adónde va la memoria de entrenamiento?

<details markdown="1"><summary>Comprobación</summary>

14 GB de pesos del base congelado, ~0.3 GB de estado del adapter y unas activaciones que pueden superar a ambos. El base congelado es el mayor término fijo, y esta etapa lo ataca.

</details>

3. ▢ ¿Por qué fusionar en un base cuantizado pierde calidad?

<details markdown="1"><summary>Comprobación</summary>

Exige descuantizar, sumar la actualización y volver a cuantizar. El paso de recuantización descarta información.

</details>

## Qué debes saber

La cuantización almacena los números usando menos bits de los que se usaron al entrenarlos. Recuerda del [glosario](../GLOSSARY.md) que en este espacio de trabajo se refiere siempre al **base congelado**, no al adapter.

### El mecanismo

Para almacenar un tensor de alta precisión en un tipo entero pequeño necesitas una correspondencia entre el rango real y el rango entero. Dos esquemas:

**Simétrico, absmax.** Toma el mayor valor absoluto y escala para que caiga en el máximo entero.

```text
s = absmax(x) / 127          # for int8
q = round(x / s)             # store q, an int8
x̂ = q · s                    # recover, approximately
```

**Asimétrico, afín.** Almacena también un desplazamiento de punto cero, para que el rango no tenga que estar centrado en cero.

```text
s = (max(x) − min(x)) / 255
z = round(−min(x) / s)
q = round(x / s) + z
```

Las distribuciones de pesos en los transformers son aproximadamente simétricas y están centradas cerca de cero, así que el absmax simétrico es la elección común para los pesos.

En cualquier caso, el error es **error de redondeo**: cada valor se mueve al nivel representable más cercano. Dieciséis niveles para 4 bits, 256 para 8 bits.

### El problema del outlier

Esto es lo que hace fallar a la cuantización ingenua en los transformers. Un único valor muy grande en un tensor fija el `absmax`, que fija la escala, que reparte todos los niveles representables para cubrir un rango que casi ningún otro valor usa jamás. Los valores típicos acaban entonces redondeados a un puñado de niveles, y la mayor parte de la información del tensor queda destruida por un solo outlier.

No es hipotético. Las activaciones de los transformers desarrollan features sistemáticas de gran magnitud, y esta observación es el núcleo del trabajo de LLM.int8(): un pequeño número de dimensiones outlier lleva una importancia desproporcionada, y manejarlas de forma ingenua destruye la calidad a escala.

### Cuantización por bloques, la solución

No cuantices un tensor entero con una sola escala. Divídelo en **bloques** contiguos pequeños de 64, 128 o 256 elementos, y dale a cada bloque su propia escala.

```text
per-tensor:  one absmax  → one outlier ruins everything
per-block:   one absmax per 64 → one outlier ruins 64 values
```

![Dos rectas numéricas con los mismos dieciséis niveles. En la primera, la escala la fija un outlier, y cinco valores típicos colapsan en dos niveles cerca del centro. En la segunda, un bloque sin outlier fija su propia escala y los mismos cinco valores caen en cinco niveles distintos.](images/outlier-sets-the-scale.svg)

Ambas filas tienen dieciséis niveles, espaciados de forma idéntica. Lo único que cambió es cuánto rango numérico se le pide cubrir a esos dieciséis niveles, y eso lo fija el mayor valor de aquello sobre lo que se calcula la escala. Gasta la rejilla en un rango que los datos nunca visitan y los datos llegan a un puñado de niveles; gástala en el rango que los datos realmente ocupan y cada valor conserva un nivel propio.

El daño queda contenido. Por eso la cuantización por bloques es estándar y la cuantización por tensor no.

Tiene un costo, y ese costo es todo el tema de la lección siguiente. Cada bloque necesita que se almacene su escala, y esa escala es un número real:

```text
4-bit weights, block size 64, fp32 scales:
  weights = 0.5 bytes/param
  scales  = 4 bytes per 64 params = 0.0625 bytes/param
  total   = 0.5625 bytes/param, i.e. 4.5 bits, not 4
```

Un doce por ciento de sobrecarga sobre un presupuesto de 4 bits, puramente por contabilidad. Quédate con ese número.

### Precisión de almacenamiento frente a precisión de cómputo

Un peso cuantizado no se usa en su forma cuantizada. El forward pass **descuantiza un bloque de vuelta a bf16, hace el matmul y descarta la copia descuantizada.**

```text
stored:   4-bit + per-block scale
computed: bf16
```

Así que la cuantización compra memoria y cuesta cómputo: un paso de descuantización por bloque, por forward pass. Que el efecto neto sea más rápido o más lento depende por completo de si estabas limitado por memoria o por cómputo, y de lo bien optimizado que esté el kernel de descuantización para el hardware en el que estés.

Este último punto es donde el hardware entra de verdad. La *aritmética* es idéntica en todas partes. Lo que difiere por backend es si existe un kernel fusionado y optimizado para un ancho de bits y un tamaño de bloque dados, o si la biblioteca recurre a una ruta genérica más lenta. La lección 16 da el panorama actual.

### Para qué sirve la cuantización, aquí

Dos usos que no deben confundirse:

**La cuantización para inferencia** encoge un modelo para que quepa y se sirva barato. Los pesos se cuantizan y ese es el artefacto que distribuyes. Esto queda fuera del alcance de este espacio de trabajo como tema por derecho propio.

**La cuantización para entrenamiento**, que es lo que hace QLoRA, encoge el *base congelado* para que quepa el entrenamiento del adapter. El adapter se queda a mayor precisión, y el artefacto que distribuyes puede fusionarse después en un base de precisión completa. La precisión del base es una decisión de presupuesto del momento del entrenamiento, no una propiedad del resultado.

## Práctica

1. ▢ Cuantiza los valores `[0.1, −0.3, 0.2, 8.0]` a int8 con absmax simétrico. ¿Qué les pasa a los tres primeros?

<details markdown="1"><summary>Comprobación</summary>

`absmax = 8.0`, así que `s = 8.0/127 ≈ 0.063`. Los valores se asignan a `round(0.1/0.063) = 2`, `round(−0.3/0.063) = −5`, `round(0.2/0.063) = 3` y `127`.

Recuperados: 0.126, −0.315, 0.189, 8.0. Los valores pequeños llevan ahora un error relativo sustancial, porque un outlier consumió el rango. Con 4 bits, con dieciséis niveles, los tres primeros colapsarían casi en el mismo valor.

</details>

2. ▢ ¿Por qué ayuda la cuantización por bloques, y qué cuesta?

<details markdown="1"><summary>Comprobación</summary>

Un outlier solo fija la escala de su propio bloque, así que daña 64 valores en lugar de todo el tensor.

El costo es almacenar una escala por bloque. Con tamaño de bloque 64 y escalas en fp32, eso son 0.0625 bytes por parámetro, alrededor de un 12% de sobrecarga sobre un presupuesto de 4 bits.

</details>

3. ▢ ¿Bytes totales por parámetro para pesos de 4 bits, tamaño de bloque 128, escalas en fp32?

<details markdown="1"><summary>Comprobación</summary>

0.5 + 4/128 = 0.5 + 0.03125 = 0.53125 bytes, o 4.25 bits.

Bloques más grandes significan menos sobrecarga de escalas y peor contención de outliers. Ese es el compromiso que fija el tamaño de bloque.

</details>

4. ▢ En un forward pass cuantizado, ¿en qué precisión se hace el matmul?

<details markdown="1"><summary>Comprobación</summary>

En una mayor, normalmente bf16. Cada bloque se descuantiza a bf16, se multiplica y se descarta la copia descuantizada.

La cuantización es una decisión de *almacenamiento*. La precisión de cómputo es aparte y se configura por separado.

</details>

5. ▢ ¿Por qué la cuantización de transformers es más difícil de lo que parece solo por la aritmética?

<details markdown="1"><summary>Comprobación</summary>

Por las features outlier sistemáticas. Unas pocas dimensiones llevan magnitudes muy grandes e importancia desproporcionada, así que un esquema que trata todos los valores como intercambiables, con una escala por tensor, destruye los valores ordinarios mientras preserva los outliers.

La cuantización por bloques, y en el caso de LLM.int8() separar por completo las dimensiones outlier en mayor precisión, es la respuesta.

</details>

6. ▢ Distingue la cuantización para inferencia de la cuantización para entrenamiento.

<details markdown="1"><summary>Comprobación</summary>

Para inferencia, los pesos cuantizados *son* el artefacto: los distribuyes, y el costo en calidad es permanente.

Para entrenamiento, cuantizar el base congelado es una decisión de presupuesto de memoria. El adapter se queda en alta precisión, y el resultado distribuido puede fusionarse en un base de precisión completa, así que el costo de la cuantización no tiene por qué sobrevivir en el artefacto en absoluto.

</details>

## Prácticas en el mundo real

- [ ] Implementa a mano, en unas pocas líneas, la cuantización y descuantización int8 con absmax de un tensor. Mide el error máximo y el medio.
- [ ] Inserta un outlier grande y mide el error de nuevo. Luego repítelo por bloques con tamaño de bloque 64 y compara.
- [ ] Mañana: calcula los bytes por parámetro reales para 4 bits con tamaños de bloque 32, 64, 128 y 256, y anota dónde la sobrecarga se vuelve despreciable.

## Para profundizar

- [Paper: "LLM.int8(): 8-bit Matrix Multiplication for Transformers at Scale", Dettmers et al., arXiv:2208.07339](https://arxiv.org/abs/2208.07339)
- [Paper: "8-bit Optimizers via Block-wise Quantization", Dettmers et al., arXiv:2110.02861](https://arxiv.org/abs/2110.02861)
- [Lección 15. NF4 y doble cuantización](0015-nf4-and-double-quantisation.md)

---

¿No termina de quedar claro? Vuelve a leer la fuente primaria de arriba, ya que esta lección la comprime y en la compresión es donde se escapa la comprensión. Consulta el [glosario](../GLOSSARY.md) por si algún término te resultó resbaladizo.

Si lo poco claro es la propia lección y no el material, eso es un defecto: [abre un issue](https://github.com/TokenCemetery/teach/issues).
