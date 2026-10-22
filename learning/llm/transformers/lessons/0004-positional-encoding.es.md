---
title: "4. Codificación posicional"
description: "Por qué la atención, por sí sola, no distingue el orden, y cómo la codificación sinusoidal da a cada posición una firma distinguible"
type: lesson
---

# Lección 4. Codificación posicional

**Vínculo con la misión:** La etapa 2 abre las piezas que rodean a la atención (lecciones 1 a 3) para convertirla en un bloque transformer completo; la codificación posicional es la primera de ellas, y sin ella la atención sería ciega a lo que más importa en el lenguaje: el orden.
**Fuente principal:** [Paper: "Attention Is All You Need", Vaswani et al., 2017](https://arxiv.org/abs/1706.03762)
**Requisitos previos:** [Lección 3](0003-causal-masking.md), [Scaled dot-product attention](../GLOSSARY.md)

## Calentamiento

1. ▢ ¿Por qué la máscara causal se aplica a las puntuaciones en bruto antes del softmax, y no poniendo a cero los pesos después de que el softmax ya se haya ejecutado?

<details markdown="1"><summary>Comprobación</summary>

Los pesos del softmax se calculan conjuntamente y ya suman 1; poner a cero uno después deja a los demás sin sumar 1. Enmascarar antes del softmax deja que los pesos restantes, sin enmascarar, se renormalicen automáticamente como parte del mismo cálculo.

</details>

2. ▢ Escribe de memoria la ecuación de la scaled dot-product attention.

<details markdown="1"><summary>Comprobación</summary>

`Attention(Q, K, V) = softmax(QK^T / sqrt(d_k)) V`.

</details>

## Qué debes saber

### La atención no trae incorporada ninguna noción de orden

La scaled dot-product attention calcula su salida a partir de productos escalares entre queries y keys y de sumas ponderadas sobre los values; nada en ese cálculo hace referencia a dónde se sitúa un token en la secuencia. Intercambia las posiciones de dos tokens de entrada (y, en consecuencia, las filas de `Q`, `K` y `V` que vinieron de ellos), y la salida de atención de cualquier otra posición es idéntica, solo que reetiquetada para coincidir con el intercambio: las relaciones y los pesos basados en el contenido que produce el cálculo no cambian en absoluto. La atención trata su entrada como un conjunto desordenado de vectores, no como una secuencia, aunque el lenguaje claramente no es independiente del orden: "el perro muerde al hombre" y "el hombre muerde al perro" comparten todas las palabras y significan algo completamente distinto.

### La posición tiene que quedar incorporada en los propios vectores

La ecuación de la atención solo ve `Q`, `K` y `V`; no hay un canal lateral para decir "y por cierto, esta es la posición de la que venía cada uno de estos". La única manera de que la atención se vuelva sensible a la posición es que la posición ya esté codificada dentro de los vectores que producen `Q`, `K` y `V` en primer lugar, es decir, dentro de los embeddings de los tokens antes de que lleguen siquiera al cálculo de atención. Un vector de **codificación posicional**, sumado al embedding de cada token, da a dos tokens con la misma palabra pero en posiciones distintas embeddings numéricamente distinguibles, que es lo que hace que los productos escalares de la atención acaben siendo implícitamente sensibles a la posición.

### Codificación sinusoidal: una firma única y estructurada por posición

La elección del paper original construye la codificación de cada posición a partir de funciones seno y coseno de distintas frecuencias, un par de dimensiones por frecuencia:

```text
PE(pos, 2i)   = sin(pos / 10000^(2i / d_model))
PE(pos, 2i+1) = cos(pos / 10000^(2i / d_model))
```

Los pares de dimensiones de índice bajo (`i` pequeña) oscilan despacio a lo largo de las posiciones (una longitud de onda larga); los de índice alto oscilan rápido (una longitud de onda corta). Cada posición recibe una combinación única a través de todas estas frecuencias y, lo que es crucial, un desfase fijo entre dos posiciones puede expresarse como una función lineal de la codificación de una de ellas (ya que el `sin` y el `cos` de una suma se descomponen en combinaciones lineales de `sin` y `cos` de las partes). Esa estructura es parte de por qué el paper sostiene que este esquema puede generalizar a la posición relativa, y potencialmente a longitudes de secuencia no vistas durante el entrenamiento, en lugar de limitarse a memorizar un conjunto fijo de posiciones absolutas.

![Dos ondas dibujadas frente a la posición en el eje horizontal. La onda superior, de un par de dimensiones de índice bajo, completa una oscilación lenta a lo largo de todo el rango de posiciones mostrado. La onda inferior, de un par de dimensiones de índice alto, completa ocho oscilaciones rápidas en el mismo rango. Cada posición recibe una combinación única de valores a través de todas estas ondas de distinta frecuencia, que es lo que da a cada posición una firma distinguible.](images/sinusoidal-frequency-pairs.svg)

### La alternativa más simple: un embedding posicional aprendido

En lugar de una fórmula fija, una posición puede codificarse con una tabla de embeddings aprendida corriente, indexada por posición igual que una tabla de embeddings de tokens se indexa por vocabulario, y entrenada por descenso de gradiente como cualquier otro parámetro. Esto es más simple de implementar y no requiere razonar sobre frecuencias, pero no tiene ninguna fórmula a la que recurrir para una posición más allá del tamaño con el que se dimensionó la tabla durante el entrenamiento: no hay una fila en la tabla para una posición que el modelo nunca vio, mientras que la fórmula de la codificación sinusoidal todavía puede evaluarse en cualquier posición.

## Práctica

1. ▢ Se intercambian dos tokens de entrada de posición (y sus filas correspondientes en `Q`, `K`, `V` se intercambian con ellos). ¿Qué le pasa a la salida de atención de una tercera posición que consulta a ambos?

<details markdown="1"><summary>Comprobación</summary>

No cambia nada de los pesos basados en el contenido ni de la salida calculada; el resultado simplemente se reetiqueta para seguir qué posición física ocupan ahora los tokens intercambiados. Esto demuestra la invarianza de la atención a las permutaciones: calcula relaciones basadas en el contenido (los productos escalares), sin referencia alguna a la posición.

</details>

2. ▢ ¿Por qué hay que codificar la posición dentro de los propios embeddings de los tokens, y no pasarla al cálculo de atención como alguna señal separada junto a `Q`, `K` y `V`?

<details markdown="1"><summary>Comprobación</summary>

La ecuación de la atención solo opera sobre `Q`, `K` y `V`; no hay ninguna entrada adicional por la que pueda entrar la información de posición. La única manera de que el cálculo se vuelva sensible a la posición es que la posición ya esté incorporada en los vectores que producen `Q`, `K` y `V` antes de que corra la atención.

</details>

3. ▢ Describe la estructura de frecuencias a través de los pares de dimensiones de la codificación posicional sinusoidal, y qué aporta frente a usar directamente el entero crudo de la posición.

<details markdown="1"><summary>Pista</summary>

Piensa en qué logra variar la frecuencia entre pares de dimensiones que no lograría un único número crudo.

</details>

<details markdown="1"><summary>Comprobación</summary>

Los distintos pares de dimensiones oscilan a frecuencias distintas, de lentas (índice bajo) a rápidas (índice alto) a lo largo de las posiciones, lo que da a cada posición una combinación única de valores a través de todas las frecuencias en lugar de un único escalar crudo. Esta codificación estructurada y multifrecuencia es también lo que permite expresar un desfase posicional fijo como una función lineal de la codificación de otra posición, una propiedad que un único entero crudo no tendría en una forma que las operaciones lineales de la atención pudieran aprovechar de manera tan directa.

</details>

4. ▢ ¿Por qué puede evaluarse la codificación posicional sinusoidal para una longitud de secuencia mayor que cualquiera vista durante el entrenamiento, y una tabla de embeddings posicionales aprendida no?

<details markdown="1"><summary>Comprobación</summary>

La codificación sinusoidal es una fórmula, evaluable en cualquier valor de posición, incluidos los que nunca se encontraron durante el entrenamiento. Una tabla de embeddings aprendida solo tiene filas para las posiciones para las que se dimensionó y entrenó; una posición más allá de ese rango no tiene fila correspondiente que consultar.

</details>

5. ▢ ¿Qué afirmación es cierta sobre por qué existe la codificación posicional?

    - a) Los productos escalares de la atención ya tienen en cuenta la posición relativa sin ninguna entrada adicional
    - b) La atención trata su entrada como un conjunto desordenado, así que hay que inyectar la posición en los embeddings para que el modelo sea sensible siquiera al orden de las palabras
    - c) La codificación posicional solo hace falta en secuencias muy largas, no en las cortas
    - d) Un embedding posicional aprendido generaliza mejor a longitudes de secuencia no vistas que la codificación sinusoidal

<details markdown="1"><summary>Comprobación</summary>

**b)** Esa es toda la razón por la que existe la codificación posicional. (a) es falsa: la ecuación de la atención, por sí sola, no hace referencia alguna a la posición. (c) es falsa: incluso el significado de una secuencia corta depende del orden de las palabras, así que la misma ceguera se aplica sin importar la longitud. (d) es falsa: es al revés, la fórmula de la codificación sinusoidal puede evaluarse en cualquier posición, mientras que una tabla aprendida queda fija a aquello con lo que se entrenó.

</details>

## Prácticas en el mundo real

- [ ] Implementa la codificación posicional sinusoidal a partir de la fórmula para un `d_model` pequeño, y dibuja o imprime los vectores de codificación de unas cuantas posiciones para ver las distintas frecuencias de oscilación a través de los pares de dimensiones.
- [ ] Suma tu codificación posicional a un conjunto de embeddings de tokens y confirma que el mismo token en dos posiciones distintas produce ahora vectores numéricamente distintos.
- [ ] Mañana: lee completa la sección "Positional Encoding" del paper de la fuente principal, y contrasta su afirmación sobre generalizar a secuencias más largas con lo que tu propia implementación produciría realmente más allá de su rango de entrenamiento.

## Para profundizar

- [Paper: "Attention Is All You Need", Vaswani et al., 2017](https://arxiv.org/abs/1706.03762)
- [Article: "The Illustrated Transformer", Jay Alammar](https://jalammar.github.io/illustrated-transformer/)
- [Recursos](../RESOURCES.md)

---

¿No termina de quedar claro? Vuelve a leer la fuente primaria de arriba, ya que esta lección la comprime y en la compresión es donde se escapa la comprensión. Consulta el [glosario](../GLOSSARY.md) por si algún término te resultó resbaladizo.

Si lo poco claro es la propia lección y no el material, eso es un defecto: [abre un issue](https://github.com/TokenCemetery/teach/issues).
