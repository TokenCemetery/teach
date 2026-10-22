---
title: "3. Máscara causal"
description: "Por qué una posición de query no debe atender a posiciones futuras, y por qué la máscara se aplica antes del softmax y no después"
type: lesson
---

# Lección 3. Máscara causal

**Vínculo con la misión:** Esta es la pieza final de la etapa 1: la multi-head attention (lección 2) deja que cada posición atienda a todas las demás, que es justo lo que no sirve para la generación autorregresiva que acabará haciendo el modelo de este espacio de trabajo, y esta lección es la corrección.
**Fuente principal:** [Article: "The Annotated Transformer", Harvard NLP](http://nlp.seas.harvard.edu/annotated-transformer/)
**Requisitos previos:** [Lección 2](0002-multi-head-attention.md), [Scaled dot-product attention](../GLOSSARY.md)

## Calentamiento

1. ▢ En la multi-head attention, al calcular el escalado `/ sqrt(d_k)` dentro de un head, ¿`d_k` debe ser la dimensión por head o la dimensión completa del modelo?

<details markdown="1"><summary>Comprobación</summary>

La dimensión por head (`d_model / h`). El escalado contrarresta el crecimiento de la varianza de un producto escalar sumado sobre `d_k` términos, y dentro de un head ese producto escalar se suma sobre la dimensión propia del head, que es menor.

</details>

2. ▢ ¿Qué logra el paso de softmax en la scaled dot-product attention?

<details markdown="1"><summary>Comprobación</summary>

Convierte las puntuaciones de similitud en bruto de cada query contra cada key en una distribución de probabilidad, no negativa y con suma 1, que es lo que hace que la salida sea una mezcla ponderada de los values.

</details>

## Qué debes saber

### Por qué atender al futuro es un problema

Un modelo que genera texto un token cada vez produce el token *N* usando solo los tokens 1 a *N-1*; el token *N+1* todavía no existe en ese momento. Si durante el entrenamiento la self-attention deja que la posición *i* atienda a una posición *j* mayor que *i*, el modelo puede usar el mismo token que se supone que debe predecir, y todos los posteriores, como parte del cálculo de esa predicción. La pérdida de entrenamiento se ve estupenda, ya que el modelo en la práctica copia una respuesta que ya puede ver, pero el modelo no aprende nada útil, porque en el momento real de generar esos tokens futuros nunca están disponibles. La **máscara causal** es lo que mantiene honesto el entrenamiento: restringe cada posición a atender solo a sí misma y a las posiciones anteriores, igualando exactamente lo que estará disponible cuando el modelo genere texto de verdad, un token cada vez.

### La máscara se aplica a las puntuaciones, antes del softmax

La corrección ocurre dentro de la propia ecuación, antes del paso del softmax: se suma una máscara a las puntuaciones en bruto `QK^T / sqrt(d_k)`, que pone cada entrada en la que la posición de la key es posterior a la de la query en un número negativo muy grande (en la práctica, menos infinito o algo numéricamente equivalente, como -1e9). Después de que esa puntuación enmascarada pase por `exp(...)` dentro del softmax, un número negativo muy grande se convierte en un valor indistinguible de cero, así que esa posición no aporta esencialmente nada a la suma ponderada final, y los pesos de las posiciones restantes, sin enmascarar, se renormalizan entre sí para seguir sumando 1.

### Por qué no basta con poner a cero los pesos después del softmax

Poner a cero el peso de una posición futura *después* de que el softmax ya se haya ejecutado no funciona correctamente: los demás pesos ya se calcularon suponiendo que esa posición era una competidora real por la masa de probabilidad, y ponerla a cero después deja a los pesos restantes sin sumar 1, lo que no es una distribución de probabilidad válida. El enmascarado tiene que ocurrir específicamente antes del softmax para que la renormalización suceda automáticamente como parte del mismo cálculo.

### Por qué tampoco se puede poner la puntuación en bruto simplemente a 0

Poner la puntuación en bruto de una posición futura a 0, en lugar de a un número negativo grande, no la excluye: `exp(0) = 1`, que es una contribución perfectamente normal y no despreciable al denominador del softmax, no "ninguna atención" en absoluto. Una puntuación de 0 se lee como una similitud neutra, promedio, que compite en igualdad de condiciones con la puntuación real de cada otra posición. Solo un número negativo lo bastante grande lleva su exponencial a un valor efectivamente nulo, que es lo que quita correctamente esa posición de la suma ponderada.

### El shape de la máscara: un patrón triangular inferior fijo

Para una secuencia de longitud *n*, la máscara causal es siempre el mismo patrón triangular inferior: la posición de query *i* puede atender a las posiciones de key de 0 a *i* (inclusive), y queda enmascarada para toda posición posterior a *i*. El mismo shape de máscara se aplica en cada head de atención y en cada ejemplo de un batch, sumado una sola vez a la matriz de puntuaciones antes de que corra el softmax.

![Una cuadrícula de 4 por 4 donde las filas son posiciones de query de 0 a 3 y las columnas son posiciones de key de 0 a 3. Las celdas donde la posición de la key es menor o igual que la de la query están sombreadas en gris y permitidas. Las celdas donde la posición de la key es mayor que la de la query, por encima de la diagonal, están marcadas con una X naranja y enmascaradas antes del softmax. Las celdas permitidas forman un patrón triangular inferior que incluye la diagonal.](images/causal-mask-lower-triangular.svg)

## Práctica

1. ▢ ¿Por qué la atención de la posición *i* no debe incluir ninguna posición *j* mayor que *i*, dado cómo se usará realmente el modelo en el momento de la inferencia?

<details markdown="1"><summary>Comprobación</summary>

En la inferencia, el modelo genera un token cada vez usando solo los tokens que vinieron antes; los tokens posteriores a la posición actual todavía no existen cuando se la está prediciendo. Si el entrenamiento dejara que la posición *i* atendiera a una posición posterior *j*, el modelo aprendería a depender de información que nunca estará disponible en el momento real de generar.

</details>

2. ▢ ¿Por qué la máscara causal se aplica a las puntuaciones en bruto antes del softmax, y no poniendo a cero los pesos de atención después de que el softmax ya se haya ejecutado?

<details markdown="1"><summary>Comprobación</summary>

Los pesos de salida del softmax se calculan conjuntamente y suman 1 sobre las puntuaciones que se le dieron. Poner a cero un peso a posteriori deja a los pesos restantes sumando algo menor que 1, lo que ya no es una distribución de probabilidad válida. Enmascarar antes del softmax, en cambio, deja que la renormalización entre las posiciones restantes, sin enmascarar, ocurra automáticamente como parte del mismo cálculo.

</details>

3. ▢ ¿Por qué poner la puntuación en bruto de una posición futura simplemente a 0 (en lugar de a un número negativo grande) no la excluye correctamente de la atención?

<details markdown="1"><summary>Pista</summary>

Piensa en a qué se evalúa `exp(0)`, y qué significa eso para el denominador del softmax.

</details>

<details markdown="1"><summary>Comprobación</summary>

`exp(0) = 1`, que es un valor totalmente normal y no despreciable que sigue compitiendo por masa de probabilidad en el denominador del softmax. Una puntuación de 0 se lee como una similitud promedio, neutra, no como "excluye esta posición". Solo un número negativo suficientemente grande lleva su exponencial efectivamente a cero, que es lo que realmente quita la contribución de esa posición.

</details>

4. ▢ Para una secuencia de 4 tokens (posiciones 0 a 3), ¿a qué posiciones de key puede atender la posición de query 2 bajo una máscara causal?

<details markdown="1"><summary>Comprobación</summary>

A las posiciones 0, 1 y 2. La posición 3, por ser posterior a la 2, queda enmascarada.

</details>

5. ▢ ¿Qué afirmación es cierta sobre cómo se implementa la máscara causal?

    - a) Pone a cero los pesos de atención después de que el softmax ya los haya calculado
    - b) Suma un número negativo grande a las puntuaciones en bruto de las posiciones futuras antes del softmax, así que sus exponenciales se vuelven despreciables y los pesos restantes se renormalizan automáticamente
    - c) Solo se aplica al primer head de atención, ya que los heads posteriores no necesitan la restricción
    - d) Poner a 0 la puntuación de una posición futura equivale a enmascararla

<details markdown="1"><summary>Comprobación</summary>

**b)** Ese es exactamente el mecanismo, y la razón por la que tiene que ocurrir antes del softmax. (a) es falsa: poner a cero después del softmax deja a los pesos restantes sin sumar 1. (c) es falsa: la misma máscara se aplica idénticamente a todos los heads. (d) es falsa: una puntuación de 0 sigue aportando un peso completo y normal mediante `exp(0) = 1`, no excluye la posición en absoluto.

</details>

## Prácticas en el mundo real

- [ ] Añade la máscara causal a tu implementación de multi-head attention de la lección 2: construye una máscara triangular inferior para una longitud de secuencia elegida y súmala a las puntuaciones antes del softmax.
- [ ] Para una secuencia pequeña, imprime los pesos del softmax de una posición de query con y sin la máscara aplicada, y confirma que la versión enmascarada tiene un peso esencialmente nulo en las posiciones futuras.
- [ ] Mañana: lee la sección de enmascarado del código de la fuente principal junto a tu propia implementación, y confirma que la máscara se aplica en el mismo punto del cálculo (antes del softmax, sumada a las puntuaciones).

## Para profundizar

- [Article: "The Annotated Transformer", Harvard NLP](http://nlp.seas.harvard.edu/annotated-transformer/)
- [Paper: "Attention Is All You Need", Vaswani et al., 2017](https://arxiv.org/abs/1706.03762)
- [Recursos](../RESOURCES.md)

---

¿No termina de quedar claro? Vuelve a leer la fuente primaria de arriba, ya que esta lección la comprime y en la compresión es donde se escapa la comprensión. Consulta el [glosario](../GLOSSARY.md) por si algún término te resultó resbaladizo.

Si lo poco claro es la propia lección y no el material, eso es un defecto: [abre un issue](https://github.com/TokenCemetery/teach/issues).
