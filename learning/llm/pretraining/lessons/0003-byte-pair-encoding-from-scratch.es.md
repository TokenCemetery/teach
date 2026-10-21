---
title: "3. Byte-Pair Encoding desde cero"
description: "El algoritmo que convierte las palabras raras y desconocidas en secuencias de unidades de subpalabra aprendidas, resuelto a mano"
type: lesson
---

# Lección 3. Byte-Pair Encoding desde cero

**Vínculo con la misión:** "Entrenar un tokenizer y defender un tamaño de vocabulario frente a su efecto en la longitud de las secuencias y en el tamaño de la tabla de embeddings" es el segundo punto de Cómo se ve el éxito. Esta lección construye el algoritmo que la mayoría de los tokenizers siguen usando; la Lección 4 cubre la disyuntiva del tamaño del vocabulario en sí.
**Fuente principal:** [Paper: "Neural Machine Translation of Rare Words with Subword Units", Sennrich et al., 2015](https://arxiv.org/abs/1508.07909)
**Requisitos previos:** [Lección 2](0002-deduplication-and-quality-filtering.md)

## Calentamiento

1. ▢ Nombra una cosa que elimina la deduplicación de un corpus, y una cosa que elimina el filtrado de calidad y que la deduplicación no detectaría.

<details markdown="1"><summary>Comprobación</summary>

La deduplicación elimina texto repetido o casi repetido que ya existe en otro lugar del corpus. El filtrado de calidad elimina texto de poco valor que no es copia de nada, como el texto repetitivo o el generado por máquina, que la deduplicación no tiene manera de detectar.

</details>

## Qué debes saber

### Por qué falla un vocabulario fijo de palabras

Un modelo que predice una palabra de entre una lista fija de palabras completas no tiene manera de manejar una palabra que no estaba en esa lista: un nombre raro, un compuesto nuevo, una errata, una palabra en una escritura que la lista no previó. Sennrich et al. lo señalaron directamente para la traducción, donde es inevitable, ya que la traducción es en el fondo un problema de vocabulario abierto: ninguna lista fija de palabras, por grande que sea, cubre todos los nombres, números y neologismos que contendrá un texto real. Su solución fue dejar de tokenizar en palabras completas y tokenizar en **unidades de subpalabra**: piezas más pequeñas que una palabra, construidas de modo que una palabra rara o nunca vista pueda aun así deletrearse con piezas que el modelo ya ha visto.

### El algoritmo: fusionar el par más frecuente, repetir

El byte-pair encoding fue originalmente un algoritmo de compresión de datos, reutilizado aquí para otro trabajo. Parte del vocabulario más pequeño posible, los caracteres individuales, y construye hacia arriba:

1. Empieza con cada palabra del texto de entrenamiento dividida en sus caracteres individuales, más un marcador del final de la palabra.
2. Cuenta con qué frecuencia aparece cada par adyacente de símbolos uno junto al otro, en todo el texto (ponderado por frecuencia).
3. Fusiona el par más frecuente en un único símbolo nuevo, en todos los lugares donde aparezca.
4. Repite los pasos 2 y 3 durante un número fijo de fusiones.

El número de fusiones es el único hiperparámetro, y fija directamente el tamaño del vocabulario: el vocabulario final es el conjunto inicial de caracteres más un símbolo nuevo por cada fusión realizada. Una palabra que nunca llega a fusionarse del todo en un único símbolo se representa como una secuencia corta de las piezas en que sí se fusionó, que es exactamente lo que permite codificar una palabra no vista: recurre a piezas más pequeñas ya conocidas en lugar de a un único símbolo de palabra desconocida.

### Un ejemplo resuelto

El paper de Sennrich et al. da directamente este corpus de juguete: cuatro palabras, ya divididas en caracteres con `</w>` marcando el final de cada palabra, cada una con una frecuencia:

```text
{'l o w </w>': 5, 'l o w e r </w>': 2, 'n e w e s t </w>': 6, 'w i d e s t </w>': 3}
```

Al contar cada par adyacente, ponderado por la frecuencia de cada palabra, tres pares quedan empatados como los más frecuentes, con un recuento ponderado de 9 cada uno: `(e, s)`, `(s, t)` y `(t, </w>)`. Cada una de las dos palabras que contienen "est" (`newest`, frecuencia 6, y `widest`, frecuencia 3) aporta una aparición de cada par dentro de esa subcadena compartida, así que `6 + 3 = 9` para los tres. La regla del algoritmo, "fusiona el par más frecuente", no dice por sí sola cuál de tres pares exactamente empatados fusionar primero: ese detalle queda en manos de lo que haga la implementación cuando tiene que romper un empate, no de la definición del propio algoritmo. Tampoco fusionar uno cualquiera de los tres elimina el empate: como los tres pares provienen de la misma subcadena repetida "est", fusionar uno de ellos (digamos `e`+`s` en `es`) solo reetiqueta los otros como nuevos pares adyacentes con el mismo recuento (`es`+`t` y `t`+`</w>` siguen empatados en 9), así que los tres acaban fundidos en las siguientes fusiones, sin importar cuál se elija primero, y `newest` y `widest` terminan compartiendo una única pieza `est`.

## Práctica

1. ▢ Usando el corpus del ejemplo resuelto, `{'l o w </w>': 5, 'l o w e r </w>': 2, 'n e w e s t </w>': 6, 'w i d e s t </w>': 3}`, calcula el recuento ponderado del par adyacente `(l, o)`.

<details markdown="1"><summary>Pista</summary>

`(l, o)` aparece una vez por cada aparición de una palabra que empieza por "lo...". ¿Qué palabras son, y con qué frecuencias?

</details>

<details markdown="1"><summary>Comprobación</summary>

`(l, o)` aparece en `low` (frecuencia 5) y en `lower` (frecuencia 2), lo que da `5 + 2 = 7`.

</details>

2. ▢ ¿Por qué la propia definición del algoritmo, "fusiona el par más frecuente", no determina del todo qué par se fusiona primero en este corpus?

<details markdown="1"><summary>Comprobación</summary>

Porque tres pares, `(e, s)`, `(s, t)` y `(t, </w>)`, están exactamente empatados en el recuento ponderado más alto, 9. La regla dice qué hacer cuando hay un único par más frecuente; no dice nada sobre cuál elegir entre varios pares empatados, así que esa elección viene de lo que haga la implementación ante un empate, no del algoritmo tal como está enunciado.

</details>

3. ▢ A un tokenizer entrenado con 500 fusiones se le da una palabra que nunca vio durante el entrenamiento. ¿Qué pasa, y por qué difiere de lo que haría un vocabulario fijo de palabras completas?

    - a) Se sustituye por un único símbolo genérico de "palabra desconocida", el mismo resultado que produciría un vocabulario de palabras completas
    - b) El entrenamiento falla, ya que el tokenizer no tiene regla para una entrada no vista
    - c) Se deletrea como una secuencia corta de piezas más pequeñas que el tokenizer ya aprendió, en lugar de colapsar en un único símbolo de palabra desconocida
    - d) El tokenizer añade automáticamente una nueva regla de fusión para ella en el momento

<details markdown="1"><summary>Comprobación</summary>

**c)** La palabra no vista recurre a las piezas más pequeñas, hasta caracteres individuales si hace falta, que las fusiones del entrenamiento ya produjeron. (a) describe exactamente el modo de falla que la tokenización en subpalabras se construyó para evitar. (b) y (d) no describen cómo se comporta en tiempo de prueba un conjunto fijo y ya entrenado de reglas de fusión.

</details>

4. ▢ ¿Cuál fue la razón específica del campo que dieron Sennrich et al. para necesitar un enfoque de vocabulario abierto?

<details markdown="1"><summary>Comprobación</summary>

La traducción es en el fondo un problema de vocabulario abierto: los nombres, los compuestos y los préstamos hacen que ninguna lista fija de palabras, por grande que sea, pueda cubrir todas las palabras que contendrá un texto de entrada real.

</details>

## Prácticas en el mundo real

- [ ] A mano o en una hoja de cálculo, toma el corpus del ejemplo resuelto y calcula el recuento ponderado de cada par adyacente después de que `(e, s)` se haya fusionado en `es` (de modo que `newest` pasa a ser `n e w es t </w>` y `widest` pasa a ser `w i d es t </w>`). Confirma qué par o pares quedan ahora empatados como los más frecuentes.
- [ ] Busca el archivo de vocabulario del tokenizer de cualquier modelo abierto al que tengas acceso (muchos se publican junto con el modelo). Busca en él una palabra común de tu propio nombre o de un nombre que conozcas, y comprueba si existe como un solo token o se divide en piezas.
- [ ] Mañana: elige cinco palabras de tu propio idioma que creas que quedarían mal atendidas por un vocabulario pequeño de subpalabras (términos técnicos raros, nombres, compuestos) y predice, en una oración por palabra, cómo las dividiría probablemente un tokenizer BPE.

## Para profundizar

- [Paper: "Neural Machine Translation of Rare Words with Subword Units", Sennrich et al., 2015](https://arxiv.org/abs/1508.07909)
- [Recursos](../RESOURCES.md)

---

¿No termina de quedar claro? Vuelve a leer la fuente primaria de arriba, ya que esta lección la comprime y en la compresión es donde se escapa la comprensión. Consulta el [glosario](../GLOSSARY.md) por si algún término te resultó resbaladizo.

Si lo poco claro es la propia lección y no el material, eso es un defecto: [abre un issue](https://github.com/TokenCemetery/teach/issues).
