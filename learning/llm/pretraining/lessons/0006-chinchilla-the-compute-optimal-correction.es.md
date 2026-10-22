---
title: "6. Chinchilla: la corrección óptima en cómputo"
description: "Por qué el tamaño del modelo y el número de tokens deben escalar juntos, y cómo convertir un presupuesto de cómputo en un número de tokens"
type: lesson
---

# Lección 6. Chinchilla: la corrección óptima en cómputo

**Vínculo con la misión:** "Dado un número de parámetros y un presupuesto de cómputo, calcular el número de tokens óptimo en cómputo y defenderlo frente a una alternativa subentrenada al estilo de Kaplan" es el tercer punto de Cómo se ve el éxito. La Lección 5 cubrió la recomendación de Kaplan et al.; esta lección cubre el estudio más amplio que la revocó, y la aritmética para aplicarlo.
**Fuente principal:** [Paper: "Training Compute-Optimal Large Language Models", Hoffmann et al., 2022](https://arxiv.org/abs/2203.15556)
**Requisitos previos:** [Lección 5](0005-scaling-laws-what-kaplan-predicted.md)

## Calentamiento

1. ▢ Según Kaplan et al., para un presupuesto de cómputo fijo, ¿el entrenamiento óptimamente eficiente en cómputo significa entrenar el modelo más grande que se pueda pagar con comparativamente pocos datos, o un modelo más pequeño con tantos datos como permita el presupuesto?

<details markdown="1"><summary>Comprobación</summary>

El modelo más grande que se pueda pagar, entrenado con comparativamente pocos datos y detenido antes de la convergencia. Que los modelos más grandes sean más eficientes en muestras es lo que hace de esa la asignación recomendada de un presupuesto fijo.

</details>

2. ▢ GPT-3 entrenó un modelo de 175 mil millones de parámetros con 300 mil millones de tokens. ¿Aproximadamente cuántos tokens por parámetro es eso?

<details markdown="1"><summary>Comprobación</summary>

Unos 1.7 tokens por parámetro (300 mil millones divididos entre 175 mil millones).

</details>

## Qué debes saber

### Un barrido mucho mayor, una respuesta distinta

Hoffmann et al. hicieron el mismo tipo de estudio de leyes de escalado que Kaplan et al., pero mucho más grande y con más control: más de 400 modelos, de entre 70 millones y más de 16 mil millones de parámetros, entrenados con entre 5 mil millones y 500 mil millones de tokens. Al ajustar una ley de escalado a ese barrido, llegaron a una conclusión práctica distinta: para un entrenamiento óptimo en cómputo, el tamaño del modelo y el número de tokens de entrenamiento deben aumentarse **por igual**. Duplicar el presupuesto de cómputo significa duplicar tanto el tamaño del modelo como el número de tokens, y no, como implicaba la recomendación de Kaplan et al., gastar casi todo el cómputo extra en un modelo más grande.

### La aproximación que hace posible esta aritmética

Ambos papers usan la misma aproximación aproximada de cuánto cómputo cuesta una ejecución de entrenamiento: `FLOPs(N, D) ≈ 6ND`, donde `N` es el número de parámetros y `D` es el número de tokens de entrenamiento. Hoffmann et al. comprobaron esta aproximación directamente frente a un recuento de FLOPs más exacto para un rango de tamaños de modelo y encontraron que la diferencia era lo bastante pequeña como para no afectar a sus conclusiones. Eso significa que un presupuesto de cómputo `C`, un número de parámetros `N` y un número de tokens `D` no son tres decisiones independientes: fijar dos cualesquiera determina la tercera, mediante `D ≈ C / (6N)`.

### Chinchilla, y los números detrás del titular

Hoffmann et al. entrenaron un modelo, Chinchilla, de 70 mil millones de parámetros con 1.4 billones de tokens, usando el mismo cómputo de entrenamiento que había usado Gopher (un modelo de 280 mil millones de parámetros). Eso son aproximadamente 20 tokens por cada parámetro (1.4 billones divididos entre 70 mil millones). Sus propias proyecciones de asignación óptima para otros presupuestos de cómputo caen en un rango similar sin dar siempre exactamente el mismo número: se proyecta que un modelo de 175 mil millones de parámetros óptimo en cómputo querría más de 4.2 billones de tokens (unos 24 por parámetro), y uno de 280 mil millones de parámetros unos 6.8 billones de tokens (unos 24 por parámetro) con un presupuesto mayor. La conclusión correcta es "aproximadamente de 20 a 25 tokens por parámetro con la asignación óptima en cómputo en todo el rango que comprobó este paper", no una única constante universal.

Junto a eso, los 175 mil millones de parámetros de GPT-3 con 300 mil millones de tokens, unos 1.7 tokens por parámetro según el calentamiento de esta lección, quedan muy por debajo de ese rango. Esa brecha es exactamente lo que el resumen del paper de Chinchilla quiere decir al llamar a los grandes modelos de lenguaje contemporáneos "significativamente subentrenados": el mismo cómputo de entrenamiento podría haberse destinado a un modelo más pequeño entrenado hasta una loss menor, o al modelo del mismo tamaño entrenado con varias veces más datos, y cualquiera de las dos opciones habría aprovechado el cómputo mejor que lo que realmente se gastó.

### El resultado que hizo que la corrección se asentara

Entrenado con el presupuesto de cómputo de Gopher pero con una cuarta parte de sus parámetros y cuatro veces sus tokens, Chinchilla superó de forma uniforme y significativa a Gopher (280B), GPT-3 (175B), Jurassic-1 (178B) y Megatron-Turing NLG (530B), varios de ellos varias veces más grandes, en un amplio rango de evaluaciones posteriores, entre ellas un 67.5% en MMLU que era entonces el estado del arte, más de 7 puntos por encima de Gopher. Ser una cuarta parte del tamaño de Gopher hizo además que Chinchilla fuera considerablemente más barato de ejecutar en inferencia, un beneficio aparte, del momento del despliegue, que el entrenamiento óptimo en cómputo aporta además del argumento de tiempo de entrenamiento que plantea esta lección.

## Práctica

1. ▢ Un equipo entrena un modelo de 13 mil millones de parámetros y quiere caer en el rango aproximado de 20 a 25 tokens por parámetro de Chinchilla. ¿Aproximadamente cuántos tokens de entrenamiento implica eso?

<details markdown="1"><summary>Comprobación</summary>

Aproximadamente de 260 a 325 mil millones de tokens (13 mil millones por 20 a 25). Cualquiera de los dos extremos de ese rango es una respuesta defendible; un número muy fuera de él, como la razón de 1.7 por parámetro de GPT-3, no lo es.

</details>

2. ▢ Un equipo tiene un presupuesto de cómputo de `1.2 × 10^22` FLOPs y planea entrenar un modelo de 10 mil millones de parámetros. Usando `FLOPs(N, D) ≈ 6ND`, ¿aproximadamente cuántos tokens permite ese presupuesto?

<details markdown="1"><summary>Pista</summary>

Resuelve `D ≈ C / (6N)` con `C = 1.2 × 10^22` y `N = 10^10`.

</details>

<details markdown="1"><summary>Comprobación</summary>

Unos 200 mil millones de tokens: `1.2 × 10^22 / (6 × 10^10) = 2 × 10^11`, que son 200 mil millones, unos 20 tokens por parámetro y de lleno dentro del rango que da esta lección.

</details>

3. ▢ ¿Qué opción caracteriza mejor la diferencia práctica entre la recomendación de Kaplan et al. y la corrección de Hoffmann et al., para un presupuesto de cómputo fijo?

    - a) Kaplan recomienda gastar la mayor parte del presupuesto en un modelo más grande con comparativamente pocos datos; Hoffmann recomienda escalar por igual el tamaño del modelo y el número de tokens
    - b) Los dos papers llegan a recomendaciones idénticas, solo que formuladas de otra manera
    - c) Kaplan dice que el tamaño del modelo es irrelevante para la loss; Hoffmann dice que lo único que importa es el tamaño del modelo
    - d) Hoffmann sostiene que un modelo más grande es siempre peor que uno más pequeño con el mismo cómputo

<details markdown="1"><summary>Comprobación</summary>

**a)** es la diferencia real que recorren esta lección y la Lección 5. (b) borra un desacuerdo real y con consecuencias prácticas entre los dos papers. (c) y (d) no describen las afirmaciones de ninguno de los dos papers.

</details>

4. ▢ GPT-3 entrenó 175 mil millones de parámetros con 300 mil millones de tokens, unos 1.7 tokens por parámetro. Según el rango óptimo en cómputo de Chinchilla, de aproximadamente 20 a 25 tokens por parámetro, ¿estuvo GPT-3 más cerca de sobreentrenado o de subentrenado en datos, en relación con su tamaño?

<details markdown="1"><summary>Comprobación</summary>

Subentrenado. Su razón es más de diez veces inferior al rango que los resultados de Chinchilla implican como óptimo en cómputo, lo que significa que el mismo cómputo de entrenamiento podría haberse destinado, con verosimilitud, a un modelo más pequeño entrenado hasta una loss menor, o al mismo modelo de 175 mil millones de parámetros entrenado con bastantes más datos.

</details>

## Prácticas en el mundo real

- [ ] Busca el número de parámetros y el número de tokens de entrenamiento publicados de un modelo abierto lanzado después de 2022 (Llama, Mistral o similares publican ambos). Calcula su razón de tokens por parámetro y compárala con el rango aproximado de 20 a 25 de esta lección.
- [ ] Usando `FLOPs(N, D) ≈ 6ND`, estima el cómputo de entrenamiento (en FLOPs) que usó la ejecución de entrenamiento real de GPT-3 (175 mil millones de parámetros, 300 mil millones de tokens), y estima por separado qué cómputo habría necesitado una ejecución óptima en cómputo de 175 mil millones de parámetros con 4.2 billones de tokens. Compara los dos números.
- [ ] Mañana: elige un presupuesto de cómputo hipotético a tu gusto (de cualquier orden de magnitud) y calcula, en papel, tanto una asignación al estilo de Kaplan (favorecer un modelo mucho más grande, mantener los tokens comparativamente fijos) como una asignación al estilo de Chinchilla (escalar ambos juntos) para ese mismo presupuesto. Anota los dos pares `(N, D)` resultantes uno junto al otro.

## Para profundizar

- [Paper: "Training Compute-Optimal Large Language Models", Hoffmann et al., 2022](https://arxiv.org/abs/2203.15556)
- [Recursos](../RESOURCES.md)

---

Las etapas 1 y 2 decidieron con qué se entrena el modelo y cómo se tokeniza; esta etapa decidió cuánto de ello usar para un tamaño dado. La etapa 4 se vuelve hacia cómo consigue realmente una ejecución de entrenamiento llevar tanto cómputo a más de un dispositivo a la vez.

¿No termina de quedar claro? Vuelve a leer la fuente primaria de arriba, ya que esta lección la comprime y en la compresión es donde se escapa la comprensión. Consulta el [glosario](../GLOSSARY.md) por si algún término te resultó resbaladizo.

Si lo poco claro es la propia lección y no el material, eso es un defecto: [abre un issue](https://github.com/TokenCemetery/teach/issues).
