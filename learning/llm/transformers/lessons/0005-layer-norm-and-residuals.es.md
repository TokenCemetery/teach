---
title: "5. Layer norm y conexiones residuales"
description: "Por qué apilar muchos bloques transformer exige un camino limpio para el gradiente y rangos de activación estables, y cómo los residuales y la layer norm aportan cada uno uno de ellos"
type: lesson
---

# Lección 5. Layer norm y conexiones residuales

**Vínculo con la misión:** La atención por sí sola (etapas 1) no se apila por sí misma en una red profunda y entrenable; las conexiones residuales y la layer normalization son las dos piezas que hacen práctico, y no inestable, apilar muchos bloques transformer (etapa 3).
**Fuente principal:** [Paper: "Layer Normalization", Ba, Kiros, and Hinton, 2016](https://arxiv.org/abs/1607.06450)
**Requisitos previos:** [Lección 4](0004-positional-encoding.md), [Scaled dot-product attention](../GLOSSARY.md)

## Calentamiento

1. ▢ ¿Por qué hace falta la codificación posicional, dado lo que calcula por sí sola la ecuación de la atención?

<details markdown="1"><summary>Comprobación</summary>

La atención trata su entrada como un conjunto desordenado: intercambiar dos posiciones solo reetiqueta la salida sin cambiar ninguna relación calculada. La codificación posicional inyecta la posición en los propios embeddings de los tokens, que es la única manera de que los productos escalares de la atención se vuelvan sensibles al orden.

</details>

2. ▢ ¿Por qué poner la puntuación en bruto de una posición enmascarada simplemente a 0 no la excluye correctamente de la atención?

<details markdown="1"><summary>Comprobación</summary>

`exp(0) = 1`, un valor totalmente normal que sigue compitiendo por masa de probabilidad en el denominador del softmax. Solo un número negativo grande lleva su exponencial efectivamente a cero, que es lo que realmente quita la contribución de esa posición.

</details>

## Qué debes saber

### Las conexiones residuales dan a los gradientes un camino directo

Una subcapa del transformer (la atención, o el bloque feed-forward de la próxima lección) está envuelta en una **conexión residual**: la salida del bloque es `x + Sublayer(x)`, no solo `Sublayer(x)` por sí sola. Esto importa cuando se apilan muchos de esos bloques (el tema de la etapa 3): sin el término `+ x`, un gradiente que fluye hacia atrás durante el entrenamiento tiene que pasar por la transformación de cada subcapa en cada capa, y en una pila profunda ese camino puede encogerse hacia cero o dispararse, lo que hace que la red sea difícil o imposible de entrenar bien. Con el término residual, el gradiente tiene una segunda ruta, directa, a través de la conexión identidad `+ x` en cada capa, con independencia de lo que esté haciendo la propia subcapa, lo que mantiene una señal de entrenamiento utilizable llegando incluso a las primeras capas de una pila profunda.

### La layer normalization mantiene las activaciones de cada capa en un rango predecible

La **layer normalization** normaliza el propio vector de activación de un único token, restándole su media y dividiéndolo por su desviación estándar, calculadas a lo largo de las features de ese mismo vector, y aplica después una escala (`gamma`) y un desplazamiento (`beta`) aprendidos para que la red todavía pueda representar un rango útil en lugar de quedarse atascada en media 0 y varianza unitaria. Esto se diferencia de la **batch normalization**, que en cambio normaliza a lo largo de la dimensión del batch, calculando estadísticas con muchos ejemplos a la vez. El cálculo por ejemplo de la layer norm importa específicamente en los modelos de secuencias: funciona de forma idéntica sin importar el batch size, incluido un batch de uno, que es justo el caso durante la generación autorregresiva, donde unas estadísticas de batch calculadas sobre una sola secuencia generada carecerían de sentido o serían inestables.

El efecto práctico: la layer norm mantiene la entrada de cada subcapa en un rango numérico parecido y predecible, de modo que una subcapa muy dentro de una pila de muchos bloques no recibe escalas de activación radicalmente distintas de las de una cercana a la entrada, lo que estabiliza el entrenamiento igual que el factor de escala de la lección 1 mantenía las puntuaciones de atención en un rango donde el gradiente del softmax seguía siendo utilizable.

### Dónde se coloca la norm: post-norm frente a pre-norm

El paper original del transformer coloca la layer norm *después* de la suma residual, `LayerNorm(x + Sublayer(x))`, lo que se llama **post-norm**. Trabajos posteriores encontraron que colocar la norm *antes* de la subcapa, dentro de la rama residual, `x + Sublayer(LayerNorm(x))`, lo que se llama **pre-norm**, entrena con más estabilidad a medida que los modelos se hacen mucho más profundos. La razón: la pre-norm deja el propio camino residual completamente limpio y sin normalizar a lo largo de toda la red, una conexión identidad sin obstáculos de punta a punta, mientras que la colocación de la post-norm hace que la propia suma residual se normalice en cada capa, enturbiando esa autopista limpia para el gradiente. Por eso la mayoría de los grandes modelos actuales usan pre-norm, a pesar de que el paper original eligiera post-norm.

![Dos diagramas lado a lado de una rama residual. A la izquierda, post-norm: x se divide en una línea de bypass y una línea que atraviesa la subcapa, las dos se suman, y esa suma pasa por la layer norm, así que el propio camino residual se normaliza en cada capa. A la derecha, pre-norm: x se divide en una línea de bypass y una línea que pasa por la layer norm antes de la subcapa, las dos se suman, y la salida se usa directamente sin más normalización, así que el camino residual que corre de arriba abajo se mantiene completamente limpio y sin obstáculos de punta a punta.](images/pre-norm-vs-post-norm.svg)

## Práctica

1. ▢ ¿Por qué ayuda una conexión residual a entrenar una pila profunda de bloques transformer, en términos de lo que les pasa a los gradientes durante la retropropagación?

<details markdown="1"><summary>Comprobación</summary>

Sin residual, un gradiente que fluye hacia atrás tiene que pasar por la transformación de cada subcapa en cada capa apilada, lo que puede encogerse o explotar a lo largo de muchas capas. El término `+ x` del residual da al gradiente una segunda ruta, directa, a través de la conexión identidad en cada capa, lo que mantiene una señal utilizable llegando incluso a las primeras capas sin importar lo que la transformación de cada subcapa le haga.

</details>

2. ▢ ¿Por qué importa específicamente, para un modelo de secuencias que hace generación autorregresiva, que la layer norm normalice a lo largo de la dimensión de features y no a lo largo de la dimensión del batch como hace la batch norm?

<details markdown="1"><summary>Comprobación</summary>

La generación autorregresiva suele ejecutarse con un batch pequeño, a menudo de batch size 1. La batch normalization calcula sus estadísticas a lo largo de la dimensión del batch, lo que carece de sentido o es inestable con tan pocos ejemplos (o uno solo) de los que calcular estadísticas. La layer norm calcula sus estadísticas a partir de las features de un único ejemplo, así que funciona de forma idéntica sin importar lo grande o pequeño que sea el batch.

</details>

3. ▢ Contrasta la colocación post-norm y pre-norm, y explica por qué la pre-norm se prefiere en general para los modelos muy profundos.

<details markdown="1"><summary>Pista</summary>

Piensa en qué colocación mantiene el propio camino residual completamente sin normalizar de punta a punta.

</details>

<details markdown="1"><summary>Comprobación</summary>

La post-norm aplica la layer norm después de sumar el residual, `LayerNorm(x + Sublayer(x))`; la pre-norm la aplica antes de la subcapa, dentro de la rama residual, `x + Sublayer(LayerNorm(x))`. La pre-norm deja el propio camino residual completamente limpio y sin normalizar a lo largo de toda la red, una conexión identidad sin obstáculos de punta a punta, mientras que la colocación de la post-norm normaliza la suma residual en cada capa, lo que perturba ese camino limpio para el gradiente. Por eso la pre-norm entrena con más estabilidad a medida que aumenta la profundidad.

</details>

4. ▢ Un vector de activación de longitud 4 es `[2, 4, 4, 6]`. Calcula su media y su varianza, y luego la salida normalizada de la layer norm (antes de la escala y el desplazamiento).

<details markdown="1"><summary>Pista</summary>

La media es el promedio; la varianza es el promedio de la desviación al cuadrado respecto de la media.

</details>

<details markdown="1"><summary>Comprobación</summary>

Media: `(2+4+4+6)/4 = 4`. Desviaciones respecto de la media: `-2, 0, 0, 2`. Varianza: `(4+0+0+4)/4 = 2`. Desviación estándar: `sqrt(2) ≈ 1.414`. Normalizado: `[-2, 0, 0, 2] / 1.414 ≈ [-1.414, 0, 0, 1.414]`, antes de aplicar la escala (`gamma`) y el desplazamiento (`beta`) aprendidos.

</details>

5. ▢ ¿Qué afirmación es cierta sobre las conexiones residuales y la layer normalization en un bloque transformer?

    - a) Las conexiones residuales eliminan por completo la necesidad de la layer normalization
    - b) La layer norm siempre normaliza a lo largo de la dimensión del batch, igual que la batch norm
    - c) Las conexiones residuales dan a los gradientes un camino directo a través de una pila profunda, y la layer norm mantiene las activaciones de cada capa en un rango estable y predecible, con independencia del batch size
    - d) La colocación pre-norm o post-norm no tiene efecto sobre la estabilidad del entrenamiento a ninguna profundidad

<details markdown="1"><summary>Comprobación</summary>

**c)** Cada pieza resuelve un problema distinto: los residuales atienden el flujo del gradiente a través de la profundidad, la layer norm atiende la escala de las activaciones con independencia del batch size. (a) es falsa: resuelven problemas distintos y ambas aparecen juntas en un bloque estándar. (b) es falsa: eso es justo lo que distingue la layer norm de la batch norm. (d) es falsa: la ventaja de la pre-norm sobre la post-norm aparece específicamente a medida que los modelos se hacen más profundos.

</details>

## Prácticas en el mundo real

- [ ] Implementa la layer normalization a partir de operaciones de tensores en bruto (media, varianza, normalización, escala y desplazamiento aprendidos) para un vector de activación pequeño, y confirma que coincide con un cálculo a mano como el ejemplo resuelto de esta lección.
- [ ] Envuelve tu implementación de atención de las lecciones 1 a 3 en una conexión residual y una layer norm, eligiendo la colocación pre-norm o post-norm, y anota cuál elegiste y por qué.
- [ ] Mañana: lee el resumen y la introducción del paper "Layer Normalization", y anota qué problema de la batch normalization para modelos de secuencias se escribió originalmente para resolver.

## Para profundizar

- [Paper: "Layer Normalization", Ba, Kiros, and Hinton, 2016](https://arxiv.org/abs/1607.06450)
- [Paper: "On Layer Normalization in the Transformer Architecture", Xiong et al., 2020](https://arxiv.org/abs/2002.04745)
- [Recursos](../RESOURCES.md)

---

¿No termina de quedar claro? Vuelve a leer la fuente primaria de arriba, ya que esta lección la comprime y en la compresión es donde se escapa la comprensión. Consulta el [glosario](../GLOSSARY.md) por si algún término te resultó resbaladizo.

Si lo poco claro es la propia lección y no el material, eso es un defecto: [abre un issue](https://github.com/TokenCemetery/teach/issues).
