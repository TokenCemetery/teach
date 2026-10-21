---
title: "4. SentencePiece y la disyuntiva del tamaño del vocabulario"
description: "Tokenizar texto en bruto sin un pre-tokenizador, y qué cuesta realmente un vocabulario mayor o menor"
type: lesson
---

# Lección 4. SentencePiece y la disyuntiva del tamaño del vocabulario

**Vínculo con la misión:** "Entrenar un tokenizer y defender un tamaño de vocabulario frente a su efecto en la longitud de las secuencias y en el tamaño de la tabla de embeddings" es el segundo punto de Cómo se ve el éxito. La Lección 3 construyó el algoritmo de fusión; esta lección cubre cómo entrenarlo sin presuponer límites de palabra, y la decisión del tamaño en sí.
**Fuente principal:** [Paper: "SentencePiece: A simple and language independent subword tokenizer and detokenizer for Neural Text Processing", Kudo and Richardson, 2018](https://arxiv.org/abs/1808.06226)
**Requisitos previos:** [Lección 3](0003-byte-pair-encoding-from-scratch.md)

## Calentamiento

1. ▢ En el algoritmo de byte-pair encoding, ¿qué determina el número de operaciones de fusión realizadas?

<details markdown="1"><summary>Comprobación</summary>

El tamaño final del vocabulario: es igual al conjunto inicial de caracteres más un símbolo nuevo por cada fusión realizada.

</details>

2. ▢ ¿Por qué tres pares del ejemplo resuelto de la Lección 3 (`(e, s)`, `(s, t)`, `(t, </w>)`) acabaron todos fusionados con pocos pasos de diferencia, sin importar cuál se fusionó primero?

<details markdown="1"><summary>Comprobación</summary>

Estaban todos empatados con la misma frecuencia porque todos provenían de la misma subcadena repetida, "est". Fusionar cualquiera de ellos reetiquetaba los otros como nuevos pares con el mismo recuento en lugar de eliminar el empate, así que los tres se fundieron en poco tiempo sin importar cuál se fusionó primero.

</details>

## Qué debes saber

### Por qué falla presuponer límites de palabra

El byte-pair encoding, tal como lo describió la Lección 3, se suele ejecutar sobre un **pre-tokenizador**: algo que primero divide el texto en bruto en palabras, de modo que BPE solo tenga que aprender fusiones dentro de una palabra. Para el inglés, dividir por espacios en blanco es un pre-tokenizador fácil y casi siempre fiable. No es independiente del idioma: muchas lenguas escritas de uso extendido, incluidos el japonés y el chino, no delimitan las palabras con espacios, así que un pre-tokenizador por espacios en blanco no tiene nada sensato por lo que dividir antes de que BPE empiece siquiera. Construir un pre-tokenizador distinto por idioma, o por escritura, socava la idea de un único procedimiento de entrenamiento de tokenizer que funcione en cualquier parte.

### Entrenar directamente con oraciones en bruto

SentencePiece, de Kudo y Richardson, elimina el paso de pretokenización en lugar de intentar arreglarlo idioma por idioma: entrena su modelo de subpalabras directamente con texto de oraciones en bruto, sin ninguna suposición de límites de palabra preexistentes incorporada. El propio espacio en blanco se trata como un símbolo ordinario de la entrada, normalmente representado con un marcador dedicado para poder reproducir con exactitud el espaciado original al destokenizar, y no como algo por lo que dividir antes de que empiece el entrenamiento. Esto hace que el mismo procedimiento de entrenamiento sea independiente del idioma, algo que el paper respalda con un experimento de traducción automática inglés-japonés: entrenar de extremo a extremo con oraciones en bruto alcanzó una precisión comparable a la de entrenar con texto que ya había sido segmentado en palabras por una herramienta aparte.

### Un solo kit de herramientas, dos algoritmos de entrenamiento

SentencePiece no es un segundo algoritmo que compita con BPE; es un kit de herramientas que implementa BPE (el procedimiento de fusión de la Lección 3) junto con un segundo algoritmo de entrenamiento, un entrenador de **modelo de lenguaje unigram**, que funciona en el sentido opuesto. En lugar de partir de caracteres individuales y hacer crecer las fusiones hacia arriba, parte de un gran conjunto de subpalabras candidatas y poda repetidamente hasta el tamaño de vocabulario objetivo, eliminando en cada paso las piezas cuya ausencia menos notaría la verosimilitud del modelo. Cualquiera de los dos algoritmos de entrenamiento produce el mismo tipo de resultado: un vocabulario fijo de piezas de subpalabra y una manera determinista de dividir en ellas texto nuevo en bruto.

### La disyuntiva del tamaño del vocabulario

El tamaño de vocabulario objetivo, sea cual sea la manera en que se entrenó, es una cifra única que tira en más de una dirección a la vez:

- Un vocabulario **mayor** codifica el mismo texto en menos tokens de media, ya que más subcadenas comunes se ganan su propio símbolo. Secuencias de tokens más cortas significan menos cómputo gastado en atender y generar la misma entrada.
- Un vocabulario **mayor** también significa una tabla de embeddings mayor y una proyección de salida mayor (normalmente la misma matriz, atadas entre sí), que es un número de parámetros que escala directamente con el tamaño del vocabulario, con independencia de lo profundo o ancho que sea el resto del modelo.
- Un vocabulario **mayor** reparte la señal de entrenamiento de forma más tenue: con el mismo corpus troceado en más piezas distintas entre las que elegir, cualquier token concreto, sobre todo uno más raro, se ve menos veces por pasada sobre los datos.
- Un vocabulario **menor** invierte los tres efectos: secuencias de tokens más largas por entrada, una tabla de embeddings y de salida más pequeña y una señal de entrenamiento más densa por token, al costo de dividir las palabras corrientes en más piezas cada una.

Ningún tamaño de vocabulario gana en todos los ejes a la vez, así que se elige en función de la forma y el presupuesto de un modelo concreto, y no se lee de una fórmula. Un ejemplo real y comprobable: el paper de LLaMA informa de que tokeniza sus datos de entrenamiento con byte-pair encoding a través de la implementación de SentencePiece, dividiendo todos los números en dígitos individuales y recurriendo a bytes en bruto para representar cualquier carácter UTF-8 que el vocabulario entrenado no cubra de otro modo, de manera que ningún carácter de entrada sea realmente irrepresentable, sea cual sea el tamaño de vocabulario elegido.

## Práctica

1. ▢ Un tokenizer construido sobre un pre-tokenizador por espacios en blanco, entrenado solo con inglés, se aplica sin modificar a texto en japonés, que no tiene espacios entre las palabras. ¿Qué sale mal, y qué hace SentencePiece de otra manera que lo evita?

<details markdown="1"><summary>Comprobación</summary>

El pre-tokenizador por espacios en blanco no tiene nada sensato por lo que dividir, ya que el japonés no delimita las palabras con espacios, así que no puede entregar a BPE trozos razonables del tamaño de una palabra dentro de los cuales fusionar. SentencePiece lo evita entrenando directamente con texto de oraciones en bruto, sin ninguna suposición de límites de palabra preexistentes, y tratando el espacio en blanco como un símbolo ordinario y no como una división previa obligatoria.

</details>

2. ▢ Un equipo duplica el tamaño de vocabulario de su tokenizer manteniendo exactamente igual la dimensión oculta y la profundidad del modelo. ¿Cuál de estas opciones describe mejor el resultado?

    - a) Las secuencias se acortan de media, y las tablas de embeddings y de salida se reducen
    - b) Las secuencias se acortan de media, pero las tablas de embeddings y de salida crecen
    - c) Las secuencias se alargan de media, pero las tablas de embeddings y de salida se reducen
    - d) Ni la longitud de las secuencias ni el número de parámetros se ven afectados por el tamaño del vocabulario

<details markdown="1"><summary>Pista</summary>

El tamaño del vocabulario afecta a dos cosas distintas: en cuántos tokens se convierte un trozo de texto, y qué tamaño tiene la tabla que asigna un vector a cada token. Considera cada una por separado.

</details>

<details markdown="1"><summary>Comprobación</summary>

**b)** Un vocabulario mayor significa que más subcadenas comunes obtienen su propio token, lo que acorta las secuencias, mientras que las tablas de embeddings y de proyección de salida (normalmente atadas) escalan ambas directamente con el tamaño del vocabulario, así que crecen. (a) y (c) invierten cada una uno de los dos efectos, y (d) ignora ambos.

</details>

3. ▢ Nombra un eje en el que un vocabulario menor es mejor que uno mayor, y un eje en el que es peor.

<details markdown="1"><summary>Comprobación</summary>

Mejor: una señal de entrenamiento más densa por token (cada token se ve más a menudo por pasada sobre el mismo corpus), o una tabla de embeddings y de salida más pequeña. Peor: secuencias de tokens más largas por entrada, ya que las palabras corrientes se dividen en más piezas, lo que cuesta más cómputo para atender y generar.

</details>

4. ▢ ¿Cuál de estas opciones describe mejor qué es SentencePiece, como pieza de software?

    - a) Un único algoritmo de tokenización nuevo que sustituye al byte-pair encoding
    - b) Un kit de herramientas que implementa tanto el byte-pair encoding como un entrenador de modelo de lenguaje unigram, directamente sobre texto en bruto y sin requerir un paso de pretokenización
    - c) Solo un pre-tokenizador, pensado para ejecutarse antes de una implementación de BPE aparte
    - d) Una manera de entrenar un modelo sin ningún vocabulario fijo

<details markdown="1"><summary>Comprobación</summary>

**b)** SentencePiece empaqueta dos algoritmos de entrenamiento, el byte-pair encoding y un modelo de lenguaje unigram, y su rasgo distintivo es entrenar directamente desde oraciones en bruto. (a) es incorrecta porque sigue implementando BPE en lugar de sustituirlo. (c) invierte la aportación real de SentencePiece, que es eliminar el paso de pretokenización. (d) no describe ningún tokenizer real tratado en este track; ambos algoritmos siguen produciendo un vocabulario fijo.

</details>

## Prácticas en el mundo real

- [ ] Busca el tamaño de vocabulario informado de un tokenizer al que tengas acceso, ya sea a través de una biblioteca o de los archivos de tokenizer publicados de un modelo alojado.
- [ ] Si puedes acceder a dos tokenizers con tamaños de vocabulario notablemente distintos, codifica la misma oración con ambos y compara directamente el número de tokens resultante.
- [ ] Mañana: para un proyecto o caso de uso concreto cuya escala conozcas (un asistente de chat, un modelo centrado en código, una herramienta para un idioma con pocos recursos), decide de forma cualitativa si te inclinarías por un vocabulario mayor o menor que el de un modelo convencional, y anota qué único eje de la disyuntiva motivó tu respuesta.

## Para profundizar

- [Paper: "SentencePiece: A simple and language independent subword tokenizer and detokenizer for Neural Text Processing", Kudo and Richardson, 2018](https://arxiv.org/abs/1808.06226)
- [Recursos](../RESOURCES.md)

---

La etapa 1 cubrió qué entra en un corpus y qué se elimina de él; la etapa 2 cubrió cómo ese corpus se convierte en tokens siquiera. La etapa 3 se vuelve hacia la pregunta que está por encima de ambas: dado un número de parámetros, cuántos de esos tokens vale la pena entrenar.

¿No termina de quedar claro? Vuelve a leer la fuente primaria de arriba, ya que esta lección la comprime y en la compresión es donde se escapa la comprensión. Consulta el [glosario](../GLOSSARY.md) por si algún término te resultó resbaladizo.

Si lo poco claro es la propia lección y no el material, eso es un defecto: [abre un issue](https://github.com/TokenCemetery/teach/issues).
