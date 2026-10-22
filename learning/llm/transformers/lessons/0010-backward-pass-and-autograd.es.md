---
title: "10. El backward pass y autograd"
description: "Cómo la regla de la cadena, automatizada sobre un grafo de cómputo registrado, convierte una pérdida escalar en un gradiente para cada peso"
type: lesson
---

# Lección 10. El backward pass y autograd

**Vínculo con la misión:** La pérdida escalar de la lección 9 es inútil para el entrenamiento por sí sola; el backward pass es lo que la convierte en un gradiente para cada uno de los pesos del modelo, que es la señal real que usa el optimizador (lección 11) para mejorarlos.
**Fuente principal:** [Docs: "Autograd mechanics", PyTorch](https://pytorch.org/docs/stable/notes/autograd.html)
**Requisitos previos:** [Lección 9](0009-cross-entropy-loss.md), [Scaled dot-product attention](../GLOSSARY.md)

## Calentamiento

1. ▢ ¿Por qué usa la entropía cruzada `-log(p)` y no algo como `1 - p` como penalización de una predicción equivocada?

<details markdown="1"><summary>Comprobación</summary>

`-log(p)` crece sin cota cuando la probabilidad asignada al token correcto se acerca a 0, y penaliza cada vez con más severidad la equivocación con seguridad. `1 - p` se satura en 1 sin importar con cuánta seguridad se equivoque la predicción, y no da ninguna señal extra para distinguir una predicción meramente equivocada de una catastrófica.

</details>

2. ▢ ¿Por qué ayudan las conexiones residuales a entrenar una pila profunda de bloques transformer?

<details markdown="1"><summary>Comprobación</summary>

Dan a los gradientes un camino directo a través de la conexión identidad `+ x` en cada capa, sin importar lo que haga la transformación de cada subcapa, lo que mantiene una señal de entrenamiento utilizable llegando incluso a las primeras capas de una pila profunda.

</details>

## Qué debes saber

### Cada operación del forward registra cómo se calculó

Mientras corre el forward pass, cada operación, una multiplicación de matrices, un softmax, una suma para una conexión residual, se registra en un **grafo de cómputo**: un registro de exactamente qué operación produjo cada tensor intermedio, y a partir de qué tensores de entrada. Este grafo es lo que recorre el **backward pass**, en sentido inverso, para calcular el gradiente de la pérdida escalar final respecto de cada tensor que contribuyó a ella, hasta llegar a cada peso entrenable.

### La regla de la cadena, aplicada automáticamente

El mecanismo de fondo no es más que la regla de la cadena del cálculo, automatizada: el gradiente de la pérdida respecto de algún tensor es la suma, sobre cada camino aguas abajo de él en el grafo, del gradiente de la pérdida respecto de ese tensor aguas abajo, multiplicado por la derivada local del tensor aguas abajo respecto de este. Un caso numérico concreto: sea `y = 3x + 1` y `z = y^2`. Con `x = 2`, `y = 7`. `dz/dy = 2y = 14`. `dy/dx = 3`. Por la regla de la cadena, `dz/dx = dz/dy × dy/dx = 14 × 3 = 42`. Autograd hace exactamente este tipo de multiplicación y suma, solo que a través de cada operación de una red con millones o miles de millones de parámetros en lugar de dos ecuaciones pequeñas.

![Un ejemplo resuelto con y = 3x + 1 y z = y al cuadrado, con x = 2. El forward pass, dibujado de arriba abajo y de izquierda a derecha, calcula x = 2, luego y = 7 mediante la operación y = 3x + 1, y luego z mediante la operación z = y al cuadrado. El backward pass, dibujado debajo y corriendo de derecha a izquierda, empieza en z, multiplica por la derivada local dz/dy = 14 para llegar a y, y luego multiplica por la derivada local dy/dx = 3 para llegar a x, lo que da dz/dx = 14 por 3 = 42 por la regla de la cadena.](images/chain-rule-worked-example.svg)

### Diferenciación automática, no simbólica ni numérica

El **autograd** de PyTorch no es ni diferenciación simbólica (derivar una fórmula cerrada del gradiente a mano o mediante álgebra computacional) ni diferenciación numérica (aproximar un gradiente con diferencias finitas, lo que es impreciso y exige volver a ejecutar el cálculo hacia delante muchas veces por parámetro). En cambio, cada operación primitiva (multiplicación de matrices, suma, softmax, etcétera) tiene ya implementada una regla de backward local derivada a mano, y autograd encadena esas reglas locales de forma automática, siguiendo el grafo de cómputo registrado, para producir gradientes exactos en un único recorrido hacia atrás.

### Dónde hacen realmente su trabajo las conexiones residuales

La lección 5 sostuvo que las conexiones residuales mantienen el flujo de los gradientes a través de una pila profunda; la regla de la cadena es exactamente donde ese argumento se vuelve mecánico. Para una salida residual `y = x + Sublayer(x)`, el gradiente de la pérdida respecto de `x` es `d(loss)/d(y) × 1` (la derivada local del camino identidad, que es exactamente 1) más un segundo término que fluye a través de la propia derivada local de `Sublayer`. Por pequeña o mal comportada que llegue a ser la derivada local de `Sublayer`, ese primer término garantiza que al menos la contribución directa y sin escalar de `d(loss)/d(y)` pasa a `x` sin cambios. Esta es la razón precisa y mecánica por la que las conexiones residuales evitan los gradientes que se desvanecen, y no solo una intuición informal sobre "atajos".

### Una llamada rellena el gradiente de cada parámetro

Después de calcular la pérdida escalar, una única llamada, `loss.backward()`, recorre todo el grafo de cómputo y acumula, en el atributo `.grad` de cada parámetro entrenable, el gradiente de la pérdida respecto de ese parámetro. Los gradientes se **acumulan** por defecto en lugar de sobrescribirse, sumándose a lo que ya hubiera en `.grad`, que es por lo que un bucle de entrenamiento tiene que poner explícitamente a cero el gradiente de cada parámetro antes de cada nuevo backward pass; de lo contrario, el gradiente de cada paso quedaría contaminado por los valores sobrantes del paso anterior.

## Práctica

1. ▢ Sea `y = 3x + 1` y `z = y^2`. Con `x = 2`, calcula `y`, `dz/dy`, `dy/dx` y `dz/dx` usando la regla de la cadena.

<details markdown="1"><summary>Pista</summary>

`dz/dx = dz/dy × dy/dx`.

</details>

<details markdown="1"><summary>Comprobación</summary>

`y = 3(2) + 1 = 7`. `dz/dy = 2y = 14`. `dy/dx = 3`. `dz/dx = 14 × 3 = 42`.

</details>

2. ▢ Para una salida residual `y = x + Sublayer(x)`, ¿qué término aporta el camino identidad a `d(loss)/d(x)`, y por qué eso garantiza que algo de gradiente llega a `x` sin importar lo pequeña que sea la derivada local de `Sublayer`?

<details markdown="1"><summary>Comprobación</summary>

El camino identidad aporta `d(loss)/d(y) × 1`, ya que la derivada local de la conexión identidad es exactamente 1. Ese término no depende en absoluto de la derivada de `Sublayer`, así que, incluso si la contribución de `Sublayer` al gradiente se encoge hacia cero, el `d(loss)/d(y)` directo y sin escalar sigue pasando a `x` por este camino.

</details>

3. ▢ ¿Por qué se prefiere la diferenciación automática (autograd) a la diferenciación numérica (diferencias finitas) para entrenar una red grande?

<details markdown="1"><summary>Comprobación</summary>

La diferenciación numérica aproxima el gradiente de cada parámetro perturbándolo ligeramente y volviendo a ejecutar el forward pass, lo que es impreciso y exige un forward pass aparte por parámetro, algo inviablemente caro para una red con millones o miles de millones de pesos. Autograd, en cambio, calcula gradientes exactos para cada parámetro en un único recorrido hacia atrás del grafo de cómputo registrado, usando la regla de backward local ya implementada de cada operación.

</details>

4. ▢ ¿Qué rellena realmente llamar a `loss.backward()`, y por qué suele haber que poner a cero los gradientes antes de la siguiente llamada?

<details markdown="1"><summary>Pista</summary>

Considera qué pasa con un atributo `.grad` que ya contiene un valor de un paso anterior.

</details>

<details markdown="1"><summary>Comprobación</summary>

Rellena el atributo `.grad` de cada parámetro entrenable con el gradiente de la pérdida respecto de ese parámetro, calculado recorriendo el grafo de cómputo registrado. Los gradientes se acumulan por defecto en lugar de sobrescribirse, sumándose al valor que `.grad` ya tuviera; sin poner explícitamente a cero los gradientes antes de cada nuevo backward pass, el gradiente de un paso posterior quedaría contaminado por los valores sobrantes del paso anterior.

</details>

5. ▢ ¿Qué afirmación es cierta sobre el enfoque de autograd para calcular gradientes?

    - a) Exige que el usuario derive y proporcione una fórmula cerrada del gradiente para cada operación
    - b) Aproxima los gradientes con diferencias finitas, perturbando ligeramente cada parámetro
    - c) Registra las operaciones del forward pass en un grafo de cómputo y luego aplica la regla de la cadena de forma automática usando la regla de backward local ya implementada de cada operación
    - d) Calcula gradientes solo para la capa de salida final, no para las capas anteriores de una pila profunda

<details markdown="1"><summary>Comprobación</summary>

**c)** Así es exactamente como funciona autograd: sin derivación manual ni aproximación por diferencias finitas, solo aplicación automatizada de la regla de la cadena sobre un grafo registrado. (a) es falsa: eso describe la diferenciación simbólica, no el enfoque de autograd. (b) es falsa: eso describe la diferenciación numérica, que autograd evita. (d) es falsa: todo el sentido del backward pass es propagar los gradientes de vuelta a través de cada capa, por profunda que sea la pila.

</details>

## Prácticas en el mundo real

- [ ] Construye a mano un pequeño grafo de cómputo (dos o tres operaciones encadenadas, como el ejemplo resuelto) y verifica que el autograd de PyTorch produce el mismo gradiente que tu cálculo manual con la regla de la cadena.
- [ ] Ejecuta un forward pass, llama a `loss.backward()` dos veces seguidas sin poner a cero los gradientes entre medias, y confirma que los valores de `.grad` de la segunda llamada reflejan una acumulación y no un gradiente nuevo.
- [ ] Mañana: lee la sección "How autograd encodes the history" de la documentación de la fuente principal y anota en qué se diferencia el grafo registrado entre un forward pass nuevo y uno ejecutado con el seguimiento de gradientes desactivado.

## Para profundizar

- [Docs: "Autograd mechanics", PyTorch](https://pytorch.org/docs/stable/notes/autograd.html)
- [Repo: nanoGPT, Karpathy](https://github.com/karpathy/nanoGPT)
- [Recursos](../RESOURCES.md)

---

¿No termina de quedar claro? Vuelve a leer la fuente primaria de arriba, ya que esta lección la comprime y en la compresión es donde se escapa la comprensión. Consulta el [glosario](../GLOSSARY.md) por si algún término te resultó resbaladizo.

Si lo poco claro es la propia lección y no el material, eso es un defecto: [abre un issue](https://github.com/TokenCemetery/teach/issues).
