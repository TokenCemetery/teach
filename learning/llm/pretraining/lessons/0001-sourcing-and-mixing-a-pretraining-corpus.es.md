---
title: "1. Obtener y mezclar un corpus de preentrenamiento"
description: "Qué entra en un corpus de preentrenamiento, y por qué la mezcla de fuentes importa más que el total de bytes"
type: lesson
---

# Lección 1. Obtener y mezclar un corpus de preentrenamiento

**Vínculo con la misión:** "Construir un corpus de preentrenamiento deduplicado y filtrado por calidad a partir de fuentes en bruto, y decir qué elimina cada paso de filtrado y por qué" es el primer punto de Cómo se ve el éxito. Esta lección cubre la mitad de obtención y mezcla de fuentes; la Lección 2 cubre la deduplicación y el filtrado de calidad.
**Fuente principal:** [Paper: "The Pile: An 800GB Dataset of Diverse Text for Language Modeling", Gao et al., 2020](https://arxiv.org/abs/2101.00027)
**Requisitos previos:** ninguno

## Qué debes saber

### De qué está hecho un corpus de preentrenamiento

Un corpus de preentrenamiento es la colección en bruto de documentos con los que se entrena un modelo antes de tokenizar nada de ella: rastreos de la web, libros, repositorios de código, papers académicos, publicaciones de foros, sitios de referencia y más, reunidos de muchas fuentes separadas en lugar de extraídos de un único rastreo gigante. Tratar "el corpus" como un montón único e indiferenciado de texto oculta la decisión que de verdad da forma a lo que aprende el modelo, que es qué fuentes entraron y qué parte del corpus final aporta cada una.

### Obtener fuentes es una decisión de mezcla, no solo de inclusión

The Pile es un buen ejemplo resuelto porque sus autores documentaron el razonamiento en lugar de limitarse a publicar el dataset. Reúne 825 GiB de texto de 22 subconjuntos diversos y de alta calidad, muchos procedentes de fuentes académicas o profesionales (documentos legales, papers académicos, documentación técnica) que un rastreo general de la web subrepresenta. La propia evaluación del paper vuelve concreto el argumento: GPT-2 y GPT-3, ninguno de los cuales se entrenó con The Pile, tienen dificultades en muchos de sus componentes, "como la escritura académica", mientras que los modelos entrenados con The Pile mejoran de forma significativa frente a los entrenados con Raw Common Crawl o CC-100, en todos y cada uno de los componentes de The Pile y también en las evaluaciones posteriores.

Ese resultado no trata en realidad del tamaño total. Trata de qué dominios se incluyeron siquiera, y por eso "qué tamaño tiene el corpus" es la pregunta equivocada con la que empezar a analizar una ejecución de preentrenamiento.

### La proporción es la palanca, no solo la presencia

Una vez incluida una fuente, queda una segunda decisión: qué parte del presupuesto final de tokens recibe. Una fuente que domina el recuento de bytes en bruto de internet (charla de foros, textos de marketing, texto repetitivo de navegación) no tiene derecho automático a dominar el corpus, y una fuente pequeña en bytes en bruto pero densa en información (texto académico curado, documentación de referencia) no se queda atascada en la proporción que ocupa de forma natural. Quien diseña un corpus decide aumentar el muestreo de algunas fuentes respecto a su tamaño natural y limitar otras muy por debajo de él, y esa decisión es independiente de la decisión de incluir la fuente, y se toma después de ella.

Dos corpus pueden incluir exactamente la misma lista de fuentes y aun así comportarse de manera distinta una vez entrenados con ellos, si sus proporciones difieren. Por eso "mezcla" y "obtención de fuentes" son dos decisiones separadas que merece la pena nombrar por separado, aunque una tabla de nombres de datasets haga que parezcan lo mismo.

### El corpus es un artefacto de diseño

La obtención de fuentes y la mezcla ocurren antes de que corra un solo token de entrenamiento, y son tan determinantes como cualquier hiperparámetro elegido después. Un modelo entrenado con un corpus mal compuesto malgasta cómputo reaprendiendo patrones redundantes o de poco valor, por bien que se ejecuten las etapas posteriores de una ejecución de preentrenamiento (el reparto de ZeRO de la etapa 5, el programa del learning rate de la etapa 7). Esas etapas posteriores hacen que el entrenamiento sea eficiente; esta etapa decide qué hay que aprender de forma eficiente.

## Práctica

1. ▢ The Pile reunió 825 GiB de texto de 22 fuentes diversas en lugar de extraer un único rastreo de la web de ese mismo tamaño. Según la propia evaluación del paper, ¿qué hicieron GPT-2 y GPT-3 (ninguno entrenado con The Pile) en muchos de los componentes de The Pile, y qué dice ese resultado sobre depender solo de texto rastreado de la web?

<details markdown="1"><summary>Comprobación</summary>

Tuvieron dificultades, sobre todo en componentes como la escritura académica. Es evidencia directa de que un corpus construido sobre todo con texto general rastreado de la web deja al modelo con una exposición escasa a géneros enteros, sin importar cuánto texto de la web haya visto.

</details>

2. ▢ Un equipo duplica el recuento de bytes en bruto de su componente de rastreo de la web y deja fijo el de todas las demás fuentes, sin ningún otro cambio en el diseño del corpus. ¿Qué pasa con la mezcla?

    - a) La mezcla no cambia, ya que la obtención de fuentes solo se ocupa de qué fuentes se incluyen, no de cuánto de cada una
    - b) La parte del rastreo de la web en el corpus final crece, aunque nadie haya decidido deliberadamente que sea una fracción mayor de aquello de lo que aprende el modelo
    - c) La mezcla solo importa para cómo se entrena el tokenizer, no para el modelo en sí
    - d) Duplicar el tamaño de cualquier fuente individual siempre mejora el rendimiento posterior

<details markdown="1"><summary>Pista</summary>

Nada cambió aquí sobre qué fuentes están presentes. Pregúntate qué cambió en cuánto aporta cada una del total.

</details>

<details markdown="1"><summary>Comprobación</summary>

**b)** La parte del rastreo de la web crece por defecto, como efecto secundario accidental de un cambio en el recuento de bytes, no porque nadie haya decidido que el modelo deba aprender desproporcionadamente más de él. (a) confunde inclusión con proporción, que es exactamente la distinción que traza esta lección. (c) es falsa: la mezcla da forma a aquello con lo que se entrena el modelo, no solo a cómo se construye el vocabulario. (d) es falsa en general; más cantidad de una fuente de poca información puede diluir un corpus en lugar de mejorarlo.

</details>

3. ▢ Un corpus recién ensamblado repite varias veces, respecto a su parte natural, una pequeña colección curada de 2 GB de documentos legales, mientras limita muy por debajo de su parte natural un componente de rastreo de la web en bruto de 400 GB. Ambas fuentes ya estaban seleccionadas para su inclusión antes de tomar esta decisión. ¿Es una decisión de obtención de fuentes o de mezcla, y por qué?

<details markdown="1"><summary>Comprobación</summary>

Una decisión de mezcla. El conjunto de fuentes no cambió; ambas ya estaban presentes. Lo que cambió es cuánto del presupuesto final de tokens se permite aportar a cada una, que es exactamente la pregunta de la proporción que esta lección separa de la pregunta de la inclusión.

</details>

## Prácticas en el mundo real

- [ ] Lee la lista de fuentes componentes en el paper de The Pile (su Tabla 1, en el paper enlazado) y anota cuáles dos o tres te resultan más sorprendentes en un corpus de entrenamiento de un modelo de lenguaje, y por qué no se te habría ocurrido incluirlas.
- [ ] Busca la composición documentada de un corpus abierto de preentrenamiento conocido que no hayas examinado antes (RedPajama, Dolma o FineWeb están documentados públicamente). Anota aproximadamente qué fracción es texto general rastreado de la web frente a fuentes curadas o estructuradas.
- [ ] Mañana: esboza una mezcla de corpus hipotética para un modelo que quisieras que fuera especialmente bueno en un dominio concreto (razonamiento jurídico, literatura científica, un lenguaje de programación). Nombra cuatro o cinco tipos de fuente que incluirías y, para cada una, di con tus propias palabras si aumentarías su muestreo por encima de su parte natural, la limitarías por debajo o la dejarías como está, y por qué.

## Para profundizar

- [Paper: "The Pile: An 800GB Dataset of Diverse Text for Language Modeling", Gao et al., 2020](https://arxiv.org/abs/2101.00027)
- [Recursos](../RESOURCES.md)

---

¿No termina de quedar claro? Vuelve a leer la fuente primaria de arriba, ya que esta lección la comprime y en la compresión es donde se escapa la comprensión. Consulta el [glosario](../GLOSSARY.md) por si algún término te resultó resbaladizo.

Si lo poco claro es la propia lección y no el material, eso es un defecto: [abre un issue](https://github.com/TokenCemetery/teach/issues).
