---
title: "10. Destilar a partir de datos generados"
description: "Construir un conjunto de instrucciones a partir de las generaciones de un profesor, como hicieron Self-Instruct y Alpaca"
type: lesson
---

# Lección 10. Destilar a partir de datos generados

**Vínculo con la misión:** La misión te pide destilar a partir de los datos generados por un profesor, lo que significa construir las entradas además de recoger las salidas, y saber qué cuesta esa construcción.
**Fuente principal:** [Paper: "Self-Instruct: Aligning Language Models with Self-Generated Instructions", Wang et al., 2022](https://arxiv.org/abs/2212.10560)
**Requisitos previos:** [Lección 9](0009-token-or-sequence.md), [Datos sintéticos](../GLOSSARY.md), [Destilación a nivel de secuencia](../GLOSSARY.md), [Profesor](../GLOSSARY.md), [Estudiante](../GLOSSARY.md)

## Calentamiento

1. ▢ En la receta de Kim y Rush, ¿de dónde venían las entradas, y qué añadió el profesor?

<details markdown="1"><summary>Comprobación</summary>

Las entradas eran las oraciones de entrenamiento existentes. El profesor añadió solo las salidas: su traducción con beam search de cada entrada. El estudiante entrenó con esos pares de entrada y salida (lección 8).

</details>

2. ▢ Un profesor está detrás de una API y devuelve solo texto. ¿Qué nivel de destilación tienes abierto?

<details markdown="1"><summary>Comprobación</summary>

El nivel de secuencia, sobre el texto que puedas recoger (lección 9). El nivel de token necesita la distribución del profesor en cada posición, que el texto solo no da.

</details>

## Qué debes saber

### La destilación con datos generados es destilación a nivel de secuencia con una elección más

En la lección 8 las entradas estaban dadas: el conjunto de entrenamiento de una tarea de traducción. Para un modelo de instrucciones general no hay un conjunto fijo de entradas. Alguien tiene que escribir los prompts.

La destilación con datos generados es [destilación a nivel de secuencia](../GLOSSARY.md) en la que además eliges las entradas. El profesor escribe los prompts o los escribes tú, el profesor escribe las respuestas, y el estudiante entrena con entropía cruzada simple sobre los pares. Todo lo que recibe el estudiante lo decide esos datos: un estudiante solo puede aprender comportamientos que los pares muestren.

### Self-Instruct: el pipeline

Self-Instruct (Wang et al., 2022) construye un conjunto de instrucciones a partir de las propias generaciones de un modelo, empezando por 175 tareas semilla escritas por humanos, cada una con una instrucción y una instancia. Tiene cuatro pasos (sección 2.2):

1. **Generar instrucciones.** Muestrear 8 instrucciones del conjunto de tareas como ejemplos in-context, 6 escritas por humanos y 2 generadas en rondas anteriores, y pedir al modelo otras nuevas.
2. **Clasificar la tarea.** Preguntar al modelo, con unos pocos ejemplos (12 instrucciones semilla de clasificación y 19 de no clasificación), si la instrucción es una tarea de clasificación, es decir, una con un conjunto pequeño y limitado de salidas.
3. **Generar instancias.** Para la mayoría de las tareas, primero la entrada: escribir una entrada y luego la salida. Para las tareas de clasificación, primero la salida: escribir la etiqueta de clase y luego una entrada para esa etiqueta. Los autores lo añadieron porque la generación con la entrada primero producía entradas sesgadas hacia una etiqueta, por ejemplo oraciones gramaticales para una tarea de errores gramaticales.
4. **Filtrar.** Conservar una instrucción nueva solo si su similitud ROUGE-L con cada instrucción que ya está en el conjunto es inferior a 0.7. Descartar las instrucciones con palabras clave como imagen, foto o gráfico que un modelo de lenguaje no puede manejar. Descartar las instancias duplicadas y las instancias con la misma entrada pero salidas distintas. Descartar las instancias que no superan heurísticas simples, como una instrucción demasiado larga o demasiado corta, o una salida que simplemente repite la entrada.

El bucle se retroalimenta: las instrucciones aceptadas se unen al conjunto y se convierten en ejemplos in-context de las rondas posteriores. Las reglas de filtrado son el tema de la lección 12.

El resultado, con el modelo `davinci` de GPT-3, fue de 52,445 instrucciones y 82,439 instancias tras el filtrado, de las cuales 11,584 instrucciones eran tareas de clasificación (Tabla 1). Hacer fine-tuning de GPT-3 con todo ello costó $338 a través del servicio de fine-tuning del proveedor (apéndice A.3). El mismo modelo generó los datos y luego se le hizo fine-tuning con ellos, así que el profesor y el estudiante partieron de un mismo modelo.

Su evaluación, sobre tareas no vistas de SuperNI medida con ROUGE-L (Tabla 3): GPT-3 vanilla puntuó 6.8, el modelo Self-Instruct 39.9, y el modelo ajustado por instrucciones de OpenAI InstructGPT001 40.8. Los autores lo leen como una mejora de 33.1 puntos que casi iguala a InstructGPT001. Es su resultado en su benchmark y su métrica.

### Alpaca: la misma receta a menor escala

El equipo de Stanford CRFM construyó Alpaca a partir de la idea de Self-Instruct, pero cambió el profesor y el estudiante (entrada del blog de Alpaca, "Training recipe"):

- Empezaron con los mismos 175 pares semilla y pidieron a text-davinci-003 de OpenAI que generara más.
- Simplificaron el pipeline de generación respecto de Self-Instruct, y dicen que esto redujo el costo.
- Los datos son 52K instrucciones únicas con salidas, que costaron menos de $500 a través de la API de OpenAI.
- Hicieron fine-tuning de LLaMA 7B con aprendizaje supervisado. La primera ejecución tomó 3 horas en 8 A100 de 80GB, que estiman en menos de $100 en la mayoría de los proveedores de nube.

Su línea de resumen es que Alpaca 7B se puede reproducir por menos de $600. En una evaluación preliminar de un solo turno, informan de que se comporta de forma cualitativamente similar a text-davinci-003. Trátalo como la impresión de los autores en una evaluación pequeña, no como una igualdad medida; la lección 18 vuelve sobre por qué tales impresiones pueden engañar.

| | Self-Instruct | Alpaca |
|---|---|---|
| Profesor | GPT-3 `davinci` (el modelo al que luego se hizo fine-tuning) | text-davinci-003 |
| Estudiante | GPT-3 `davinci` | LLaMA 7B |
| Conjunto semilla | 175 tareas | Los mismos 175 pares |
| Datos | 52,445 instrucciones, 82,439 instancias | 52K instrucciones con salidas |
| Costo declarado | $338 por el fine-tuning | Menos de $500 por los datos, menos de $100 por la ejecución |

### Lo que decide el diseño de los datos

Cuatro elecciones dan forma a lo que aprende el estudiante, y cada una es tuya cuando generas datos:

- **El conjunto semilla.** Todo se genera a partir de 175 ejemplos, así que lo que cubren limita en qué crece el conjunto.
- **El prompt.** Los ejemplos in-context y la plantilla orientan el estilo y la mezcla de tareas.
- **Los ajustes de muestreo.** La temperatura y ajustes similares fijan cuán variadas son las salidas.
- **El filtro.** Lo que conservas es el conjunto de entrenamiento. Un filtro débil deja que los errores del profesor se conviertan en las lecciones del estudiante.

Un estudiante solo puede igualar lo que escribió el profesor, así que un error que sobrevive al filtro se aprende como si fuera correcto.

### Las restricciones vinieron con los datos

La entrada del blog de Alpaca es explícita en que el modelo es solo para investigación académica. Da tres razones: LLaMA tiene una licencia no comercial, los datos vienen de text-davinci-003, cuyos términos prohíben desarrollar modelos que compitan con OpenAI, y no habían construido medidas de seguridad adecuadas. La lección 13 lee esas restricciones de cerca. Por ahora, fíjate en que el costo de los datos fue la parte menor de lo que traían consigo.

## Práctica

1. ▢ Los datos de Alpaca costaron menos de $500 por 52K pares de instrucción y salida. ¿Cuál es el costo por ejemplo como máximo, y por qué no es el costo total del modelo?

<details markdown="1"><summary>Comprobación</summary>

Menos de $500 dividido entre 52,000 es unos $0.0096, menos de un centavo por ejemplo. No es el costo total: el blog cuenta aparte la ejecución de fine-tuning (3 horas en 8 A100 de 80GB, menos de $100 en la mayoría de las nubes), y ninguna de las dos cifras cuenta el esfuerzo humano de las 175 semillas, la evaluación ni la demo. La lección 21 cuenta bien el costo del profesor.

</details>

2. ▢ Self-Instruct genera los datos de clasificación con la salida primero. ¿Qué problema de la generación con la entrada primero arregla eso?

    - a) Las entradas salen sesgadas hacia una única etiqueta de clase
    - b) Las salidas salen mucho más largas que cualquier respuesta humana
    - c) Las instrucciones repiten el mismo texto de entrada sin ningún cambio
    - d) Las etiquetas salen escritas en un formato muy inconsistente

<details markdown="1"><summary>Comprobación</summary>

**a)** El ejemplo del paper: al pedirle que escriba una entrada para detección de errores gramaticales, el modelo tiende a escribir una entrada gramatical, así que una clase domina. Escribir primero la etiqueta y luego una entrada para esa etiqueta las equilibra. (b), (c) y (d) no son el problema que nombran los autores.

</details>

3. ▢ Una instrucción generada nueva tiene una similitud ROUGE-L de 0.74 con una instrucción que ya está en el conjunto y de 0.2 con todas las demás. ¿La conserva Self-Instruct, y por qué?

<details markdown="1"><summary>Pista</summary>

La regla es sobre el máximo en el conjunto, no sobre el promedio.

</details>

<details markdown="1"><summary>Comprobación</summary>

No. La instrucción se conserva solo si su similitud ROUGE-L con cualquier instrucción existente es inferior a 0.7, y 0.74 lo supera. La regla mantiene diverso el conjunto rechazando una casi copia de cualquier miembro individual, por distinto que sea el resto del conjunto.

</details>

4. ▢ Tu equipo quiere copiar Alpaca pero con un profesor que produce respuestas cortas y secas. ¿Qué esperas que haga el estudiante, y qué parte del pipeline cambiarías primero?

<details markdown="1"><summary>Comprobación</summary>

Espera que el estudiante responda con el mismo estilo seco, porque solo puede aprender lo que los pares muestran. Cambia primero el prompt o los ajustes del profesor, ya que ahí se fija el estilo de respuesta, luego vuelve a ejecutar el filtro y compara a ojo una muestra de pares generados antes de entrenar. Es una predicción a partir de cómo los datos determinan al estudiante, no un resultado medido.

</details>

5. ▢ La lección 8 encontró que un estudiante a nivel de secuencia entrenado con la mejor salida única de un profesor termina concentrado alrededor de esa salida. ¿Sugiere eso generar varias salidas por prompt, o una, y qué costaría cada opción?

<details markdown="1"><summary>Comprobación</summary>

No decide el asunto. Una salida por prompt es el enfoque de estilo moda: barato y consistente, pero una sola muestra. Varias salidas por prompt muestran al estudiante más de la variedad del profesor, a varias veces el costo de generación y con más filtrado por hacer. Kim y Rush probaron a muestrear en lugar de la moda en traducción y se quedaron con la moda. Ese es un resultado para su tarea, así que prueba ambas en la tuya.

</details>

## Prácticas en el mundo real

- [ ] Abre el paper de Self-Instruct y encuentra la plantilla de prompt para generar instrucciones (Tabla 5). Anota cómo son los ejemplos in-context y cuántos escritos por humanos y por el modelo hay.
- [ ] Abre la entrada del blog de Alpaca y encuentra la frase que enumera los tres factores de la publicación solo para investigación. Anota cuál de ellos depende de tu elección de profesor.
- [ ] Mañana: escribe sin apuntes los cuatro pasos del pipeline de Self-Instruct y el umbral del filtro, y luego compáralos con el paper.

## Para profundizar

- [Secuencia y datos sintéticos](../reference/sequence-and-synthetic-data.md)
- [Paper: "Self-Instruct: Aligning Language Models with Self-Generated Instructions", Wang et al., 2022](https://arxiv.org/abs/2212.10560)
- [Article: "Alpaca: A Strong, Replicable Instruction-Following Model", Stanford CRFM, 2023](https://crfm.stanford.edu/2023/03/13/alpaca.html)
- [Recursos](../RESOURCES.md)

---

¿No termina de quedar claro? Vuelve a leer la fuente primaria de arriba, ya que esta lección la comprime y en la compresión es donde se escapa la comprensión. Consulta el [glosario](../GLOSSARY.md) por si algún término te resultó resbaladizo.

Si lo poco claro es la propia lección y no el material, eso es un defecto: [abre un issue](https://github.com/TokenCemetery/teach/issues).
