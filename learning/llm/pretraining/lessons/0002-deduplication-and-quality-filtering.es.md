---
title: "2. Deduplicación y filtrado de calidad"
description: "Por qué se eliminan antes de entrenar el texto casi duplicado y los documentos de baja calidad, y qué cuesta saltarse ese paso"
type: lesson
---

# Lección 2. Deduplicación y filtrado de calidad

**Vínculo con la misión:** "Construir un corpus de preentrenamiento deduplicado y filtrado por calidad a partir de fuentes en bruto, y decir qué elimina cada paso de filtrado y por qué" es el primer punto de Cómo se ve el éxito. La Lección 1 cubrió la obtención de fuentes y la mezcla; esta lección cubre la mitad de deduplicación y filtrado.
**Fuente principal:** [Paper: "Deduplicating Training Data Makes Language Models Better", Lee et al., 2021](https://arxiv.org/abs/2107.06499)
**Requisitos previos:** [Lección 1](0001-sourcing-and-mixing-a-pretraining-corpus.md)

## Calentamiento

1. ▢ ¿Cuál es la diferencia entre una decisión de obtención de fuentes y una decisión de mezcla en un corpus de preentrenamiento?

<details markdown="1"><summary>Comprobación</summary>

La obtención de fuentes decide qué fuentes se incluyen siquiera. La mezcla decide qué parte del presupuesto final de tokens recibe cada fuente incluida, con independencia de qué fuentes se eligieron.

</details>

2. ▢ Según el paper de The Pile, ¿por qué "qué tamaño tiene el corpus" es la pregunta equivocada con la que empezar a analizar una ejecución de preentrenamiento?

<details markdown="1"><summary>Comprobación</summary>

Porque GPT-2 y GPT-3, entrenados con enormes cantidades de texto de la web, aun así tuvieron dificultades en componentes como la escritura académica, que un rastreo general de la web subrepresenta. Qué fuentes se incluyen, y no el total de bytes, es lo que determina qué dominios aprende realmente un modelo.

</details>

## Qué debes saber

### Los duplicados no son solo espacio en disco desperdiciado

Un corpus ensamblado a partir de muchas fuentes, sobre todo si toca la web abierta, acaba con el mismo texto apareciendo más de una vez: artículos de noticias sindicados, descargos de responsabilidad legales repetitivos, correos de plantilla en los que solo se cambia un nombre. Lee et al. encontraron que esto no es una ineficiencia menor. En C4, un corpus muy usado derivado de rastreos de la web, una sola oración en inglés de 61 palabras aparece más de 60,000 veces. Más llamativo aún: más del 1% de la salida sin prompt de los modelos de lenguaje entrenados con esos datasets está copiada literalmente de los datos de entrenamiento; ahí el modelo no está generalizando, está citando algo que vio las veces suficientes para memorizarlo.

### Dos maneras distintas de encontrar un duplicado

La deduplicación tiene que detectar dos formas distintas de repetición, y una sola técnica no detecta ambas:

- **La coincidencia exacta de subcadenas** encuentra tramos de texto repetidos literalmente, incluso los que solo ocupan parte de un documento o cruzan los límites entre documentos. Lee et al. lo implementan de forma eficiente con un suffix array, que permite encontrar un tramo repetido de cualquier longitud sin comparar directamente cada documento con todos los demás.
- **La coincidencia de casi duplicados** encuentra documentos que son en su mayor parte iguales pero difieren en detalles pequeños, como un correo de formulario con el nombre de otro destinatario, o una noticia de agencia recogida con ediciones menores por muchos medios. Lee et al. usan MinHash: una técnica que estima cuánto se parecen dos documentos sin compararlos token a token, comparando en su lugar resúmenes compactos basados en hashes.

Ambas importan, porque un corpus puede estar libre de un tipo de duplicación y seguir lleno del otro.

### Qué compra realmente la deduplicación

Lee et al. dan evidencia concreta en lugar de una intuición. Deduplicar los datos de entrenamiento hizo que los modelos emitieran texto memorizado unas diez veces menos a menudo, y les permitió alcanzar la misma precisión o una mejor en menos pasos de entrenamiento. También reduce el solapamiento entre entrenamiento y prueba, que según el paper afecta a más del 4% del conjunto de validación en los benchmarks estándar; el texto que se filtró del propio conjunto de validación de un benchmark hacia el entrenamiento hace que una cifra de evaluación parezca mejor de lo que merece la generalización real del modelo, una preocupación a la que volverá este track cuando enlace con el tratamiento de la contaminación de `llm/evals`.

### El filtrado de calidad es un paso aparte y posterior

La deduplicación elimina copias redundantes de texto que ya está presente. El filtrado de calidad elimina texto de poco valor aunque no sea un duplicado de nada: spam, menús de navegación repetitivos, texto generado por máquina o documentos tan confusos que aportan poca señal. Los autores de GPT-3 describen una versión concreta de esto en su apéndice sobre el filtrado de Common Crawl: entrenaron un clasificador, mediante regresión logística sobre rasgos simples al estilo de bolsa de palabras, para distinguir el texto curado (WebText, Wikipedia, un corpus de libros) del Common Crawl en bruto y sin filtrar. La puntuación de ese clasificador se usó luego para remuestrear Common Crawl de modo que los documentos que se predecía de mayor calidad se conservaran con más frecuencia, sin dejar de conservar algunos documentos de menor puntuación en lugar de descartarlos del todo. El mismo apéndice describe también una pasada aparte de deduplicación difusa con MinHash, que por sí sola redujo el tamaño de su dataset en un 10% aproximadamente.

El filtrado de calidad y la deduplicación se ejecutan con frecuencia como pasadas separadas sobre el mismo corpus, en cualquier orden, y ninguna sustituye a la otra: un corpus puede estar libre de duplicados exactos y seguir lleno de texto repetitivo de poco valor, y puede ser prosa de alta calidad de principio a fin y aun así contener el mismo párrafo repetido sesenta mil veces.

## Práctica

1. ▢ Un dataset contiene 61 palabras repetidas literalmente en más de 60,000 documentos distintos, cada vez con un texto circundante diferente. ¿Serían la coincidencia exacta de subcadenas o la coincidencia de casi duplicados (MinHash) la herramienta adecuada para encontrar y eliminar solo ese tramo repetido, y por qué?

<details markdown="1"><summary>Pista</summary>

Pregúntate qué compara realmente MinHash: documentos enteros entre sí, o tramos de texto que podrían ser solo parte de un documento.

</details>

<details markdown="1"><summary>Comprobación</summary>

La coincidencia exacta de subcadenas. MinHash estima la similitud entre documentos enteros; un tramo de 61 palabras repetido dentro de documentos por lo demás distintos es exactamente el tipo de repetición parcial entre documentos que una búsqueda exacta de subcadenas basada en un suffix array está hecha para detectar, mientras que dos documentos que comparten solo 61 palabras de entre muchos miles podrían ni siquiera registrarse como casi duplicados entre sí.

</details>

2. ▢ ¿Cuál de estas opciones se acerca más a lo que Lee et al. midieron realmente, y no solo argumentaron?

    - a) La deduplicación hace que un modelo sea filosóficamente más original
    - b) El entrenamiento con datos deduplicados permitió que los modelos alcanzaran la misma precisión o una mejor en menos pasos, y que emitieran texto memorizado unas diez veces menos a menudo
    - c) La deduplicación solo sirve para reducir los costos de almacenamiento, sin efecto en el comportamiento del modelo
    - d) La coincidencia de casi duplicados por sí sola basta para eliminar todas las formas de texto repetido

<details markdown="1"><summary>Comprobación</summary>

**b)** es el resultado medido real del paper. (a) no es una afirmación medible. (c) contradice directamente los hallazgos sobre memorización y eficiencia del entrenamiento. (d) es falsa, ya que la coincidencia exacta de subcadenas detecta una forma de repetición distinta de la que detecta la coincidencia de casi duplicados, como muestra el primer ejercicio de práctica de esta lección.

</details>

3. ▢ Un documento no es un duplicado de nada más en el corpus, pero es sobre todo texto repetitivo autogenerado con casi ningún contenido informativo. ¿Lo eliminaría la deduplicación? ¿Qué lo eliminaría?

<details markdown="1"><summary>Comprobación</summary>

No, la deduplicación no lo eliminaría, ya que solo apunta al texto repetido y este documento es único. El filtrado de calidad, como el remuestreo basado en clasificador que describen los autores de GPT-3, es el paso dirigido exactamente a este caso: texto de poco valor que no es copia de nada más.

</details>

4. ▢ El clasificador de calidad de Common Crawl de GPT-3 se entrenó para distinguir cuál de estos pares de cosas?

    - a) Texto en inglés de texto que no está en inglés
    - b) Texto curado (WebText, Wikipedia, un corpus de libros) de Common Crawl en bruto y sin filtrar
    - c) Documentos largos de documentos cortos
    - d) Texto duplicado de texto único

<details markdown="1"><summary>Comprobación</summary>

**b)** Texto curado frente a Common Crawl en bruto. (d) describe la deduplicación, que los autores de GPT-3 ejecutaron como una pasada aparte de MinHash, no lo que se entrenó el propio clasificador de calidad para detectar.

</details>

## Prácticas en el mundo real

- [ ] Elige una oración o una frase corta que esperarías que fuera común en el texto de la web (un descargo de responsabilidad, una frase hecha, una instrucción habitual de una receta) y búscala literalmente en línea. Anota aproximadamente en cuántas páginas distintas la encuentras, como una idea intuitiva de cómo aparece la repetición en el texto rastreado real.
- [ ] Lee el resumen y la introducción del paper de Lee et al. (enlazado arriba) y escribe, en una oración cada una, qué detecta bien la coincidencia exacta de subcadenas que no detecta la coincidencia de casi duplicados, y viceversa.
- [ ] Mañana: toma un corpus para el que esbozaste una mezcla en la práctica en el mundo real de la Lección 1 y, para cada tipo de fuente, nombra una fuente plausible de duplicación (sindicación, texto repetitivo de plantilla, republicación) y una fuente plausible de baja calidad que la deduplicación por sí sola no detectaría.

## Para profundizar

- [Paper: "Deduplicating Training Data Makes Language Models Better", Lee et al., 2021](https://arxiv.org/abs/2107.06499)
- [Recursos](../RESOURCES.md)

---

¿No termina de quedar claro? Vuelve a leer la fuente primaria de arriba, ya que esta lección la comprime y en la compresión es donde se escapa la comprensión. Consulta el [glosario](../GLOSSARY.md) por si algún término te resultó resbaladizo.

Si lo poco claro es la propia lección y no el material, eso es un defecto: [abre un issue](https://github.com/TokenCemetery/teach/issues).
