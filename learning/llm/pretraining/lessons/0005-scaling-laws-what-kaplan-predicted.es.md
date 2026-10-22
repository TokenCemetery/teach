---
title: "5. Leyes de escalado: lo que predijo Kaplan"
description: "Una ley de potencias empírica permite pronosticar la loss de una ejecución de entrenamiento antes de pagarla, y qué predijo eso sobre cómo gastar un presupuesto de cómputo"
type: lesson
---

# Lección 5. Leyes de escalado: lo que predijo Kaplan

**Vínculo con la misión:** "Dado un número de parámetros y un presupuesto de cómputo, calcular el número de tokens óptimo en cómputo y defenderlo frente a una alternativa subentrenada al estilo de Kaplan" es el tercer punto de Cómo se ve el éxito. Esta lección cubre lo que Kaplan et al. encontraron y recomendaron; la Lección 6 cubre la corrección que cambió la recomendación.
**Fuente principal:** [Paper: "Scaling Laws for Neural Language Models", Kaplan et al., 2020](https://arxiv.org/abs/2001.08361)
**Requisitos previos:** [Lección 4](0004-sentencepiece-and-the-vocabulary-size-tradeoff.md)

## Calentamiento

1. ▢ Nombra un eje en el que un vocabulario de tokenizer mayor es peor que uno menor.

<details markdown="1"><summary>Comprobación</summary>

Un vocabulario mayor significa una tabla de embeddings y de proyección de salida mayor (puro número de parámetros), y reparte la señal de entrenamiento de forma más tenue entre más tokens distintos, así que cualquier token concreto se ve con menos frecuencia por pasada sobre el mismo corpus.

</details>

## Qué debes saber

### Qué es realmente una ley de escalado

Una **ley de escalado**, en este contexto, es una relación empírica de ley de potencias: la loss held-out de un modelo cae de forma suave en función del tamaño del modelo, del tamaño del dataset o del cómputo de entrenamiento, en un rango lo bastante amplio como para servir de pronóstico. Kaplan et al. ajustaron exactamente esto, y encontraron que la loss escala como una ley de potencias con cada una de estas tres cantidades por separado, con tendencias que se mantienen a lo largo de más de siete órdenes de magnitud de escala. Otras decisiones de arquitectura, como la manera de repartir un presupuesto fijo de parámetros entre anchura y profundidad, resultaron importar comparativamente poco dentro de un rango amplio una vez tenido en cuenta el propio tamaño del modelo.

El valor práctico de una ley de escalado es la predicción: si la loss sigue una curva suave y ajustada frente al tamaño del modelo, el tamaño del dataset y el cómputo, un equipo puede pronosticar aproximadamente qué tan bien rendirá una ejecución de entrenamiento de un tamaño y un presupuesto dados antes de gastar el cómputo para ejecutarla, en lugar de descubrirlo solo después.

### Los modelos más grandes aprenden más por token

Uno de los hallazgos centrales de Kaplan et al. es que los modelos más grandes son significativamente más eficientes en muestras: para alcanzar una loss dada, un modelo mayor necesita ver menos datos de los que necesitaría uno menor para alcanzar esa misma loss. Combinado con sus relaciones ajustadas entre la loss, el cómputo y las dos cosas que el cómputo compra (un modelo más grande, o más datos con los que entrenarlo), esto implica una respuesta concreta a cómo gastar un presupuesto de cómputo fijo: el entrenamiento óptimamente eficiente en cómputo consiste en entrenar un modelo muy grande con una cantidad comparativamente modesta de datos, y detenerse bastante antes de converger con esos datos, en lugar de entrenar hasta la convergencia un modelo más pequeño con más datos.

### Cómo se veía esa recomendación en la práctica

Este hallazgo dio forma a cómo se entrenó realmente una generación de modelos grandes: escalar el número de parámetros de forma agresiva y mantener el número de tokens comparativamente fijo o solo modestamente aumentado. GPT-3, por ejemplo, entrenó un modelo de 175 mil millones de parámetros con 300 mil millones de tokens. Esta lección deja esa cifra aquí sin más comentario; la Lección 6 vuelve a ella directamente cuando haya una segunda ley de escalado con la que compararla.

## Práctica

1. ▢ ¿Qué significa, con precisión, que la loss "escale como una ley de potencias" con el tamaño del modelo, en el sentido en que lo usan Kaplan et al.?

    - a) La loss disminuye exactamente la misma cantidad fija por cada aumento fijo del tamaño del modelo
    - b) La loss cae de forma suave siguiendo una curva ajustada, que se mantiene a lo largo de un rango amplio de tamaños de modelo, y eso es lo que permite pronosticarla
    - c) La loss se vuelve cero una vez que el modelo es lo bastante grande
    - d) La loss depende solo del tamaño del modelo y en absoluto de la cantidad de datos de entrenamiento

<details markdown="1"><summary>Comprobación</summary>

**b)** Un ajuste de ley de potencias lo bastante suave, y validado a lo largo de suficientes órdenes de magnitud, como para pronosticar a partir de él. (a) describe una relación lineal, no una ley de potencias. (c) no se afirma en ninguna parte del paper. (d) contradice el hallazgo, separado, del propio paper de una ley de escalado con el tamaño del dataset.

</details>

2. ▢ Según Kaplan et al., ¿cuál alcanza una loss objetivo fija usando menos datos de entrenamiento: un modelo mayor o uno menor?

<details markdown="1"><summary>Comprobación</summary>

Un modelo mayor. Los modelos mayores son más eficientes en muestras, es decir, necesitan menos datos para alcanzar la misma loss que un modelo menor necesitaría más datos para alcanzar.

</details>

3. ▢ Dado un presupuesto de cómputo fijo y los hallazgos de Kaplan et al., ¿qué asignación recomienda su análisis: un modelo muy grande entrenado con comparativamente pocos datos y detenido bastante antes de la convergencia, o un modelo más pequeño entrenado hasta la convergencia con tantos datos como permita el presupuesto?

<details markdown="1"><summary>Pista</summary>

Esto se sigue directamente de combinar "los modelos más grandes son más eficientes en muestras" con un presupuesto de cómputo fijo: el cómputo gastado en datos es cómputo que no se gasta en tamaño del modelo, y el paper encontró que uno de esos dos usos del cómputo rendía más que el otro.

</details>

<details markdown="1"><summary>Comprobación</summary>

El modelo muy grande entrenado con comparativamente pocos datos, detenido antes de la convergencia. Esa es la recomendación declarada por los propios Kaplan et al. para un entrenamiento óptimamente eficiente en cómputo con un presupuesto fijo.

</details>

## Prácticas en el mundo real

- [ ] Busca el número de parámetros y el número de tokens de entrenamiento informado de dos o tres modelos conocidos publicados en el año o dos posteriores al paper de Kaplan (de 2020 a aproximadamente 2022). Anota si sus números de tokens se mantuvieron más o menos fijos mientras crecían los números de parámetros, que es lo que parecería seguir la recomendación de esta lección.
- [ ] Vuelve a leer el resumen del paper de Kaplan (enlazado arriba) y, en una oración, enuncia qué significa "detenerse bastante antes de la convergencia" para una ejecución de entrenamiento: ¿qué compraría en realidad seguir entrenando, que esta recomendación dice que no vale su cómputo?
- [ ] Mañana: sin adelantarte a la Lección 6, escribe una predicción de una oración: dado que construir un dataset (etapa 1 de este track) es caro y lento de escalar, y que el simple número de parámetros es comparativamente fácil de escalar añadiendo más aceleradores, ¿qué presión práctica pudo empujar a las ejecuciones de entrenamiento reales hacia la recomendación de Kaplan con aún más fuerza de la que justificarían las curvas de loss por sí solas?

## Para profundizar

- [Paper: "Scaling Laws for Neural Language Models", Kaplan et al., 2020](https://arxiv.org/abs/2001.08361)
- [Recursos](../RESOURCES.md)

---

¿No termina de quedar claro? Vuelve a leer la fuente primaria de arriba, ya que esta lección la comprime y en la compresión es donde se escapa la comprensión. Consulta el [glosario](../GLOSSARY.md) por si algún término te resultó resbaladizo.

Si lo poco claro es la propia lección y no el material, eso es un defecto: [abre un issue](https://github.com/TokenCemetery/teach/issues).
