---
title: "23. Defender un presupuesto de cómputo"
description: "Un plan de preentrenamiento es una apuesta hecha de muchas decisiones separadas, y defenderlo significa defender cada una en sus propios términos"
type: lesson
---

# Lección 23. Defender un presupuesto de cómputo

**Vínculo con la misión:** "Puedes decidir si una tarea dada requiere preentrenamiento, preentrenamiento continuado o fine-tuning de un base model existente, y defender la elección en términos de costo" es el punto de Cómo se ve el éxito que cierra la etapa 10. La Lección 22 cubrió cuándo el preentrenamiento es la decisión equivocada; esta lección cubre defender el plan una vez que sí es de verdad la correcta.
**Fuente principal:** [Paper: "Training Compute-Optimal Large Language Models", Hoffmann et al., 2022](https://arxiv.org/abs/2203.15556)
**Requisitos previos:** [Lección 22](0022-pretraining-is-usually-the-wrong-default.md)

## Calentamiento

1. ▢ Según Gururangan et al., ¿ayuda más, menos o más o menos igual el preentrenamiento adaptativo al dominio, según que el dominio objetivo estuviera ya cerca de los datos de entrenamiento originales del base model?

<details markdown="1"><summary>Comprobación</summary>

Ayuda más precisamente cuando el dominio objetivo no estaba ya bien representado en el preentrenamiento original del base model; los objetivos ya cercanos al dominio se benefician menos, ya que el base model ya los cubre razonablemente bien.

</details>

2. ▢ Nombra una razón legítima para preentrenar desde cero en lugar de adaptar un modelo existente, según la Lección 22.

<details markdown="1"><summary>Comprobación</summary>

Cualquiera de estas: el idioma o dominio objetivo está tan alejado de los datos de entrenamiento y del tokenizer de todos los base models disponibles que la adaptación no puede cerrar la brecha, un requisito de licencia o de procedencia descarta todos los base models disponibles, o un cambio deliberado de arquitectura en el que no se puede convertir un checkpoint existente.

</details>

## Qué debes saber

### Un plan de preentrenamiento no es un solo número

Una vez que el preentrenamiento es de verdad la decisión correcta, defenderlo ante quien controla el presupuesto significa defender más que una única cifra de costo total. Cada etapa anterior de este track produjo una pieza de ese plan, y cada pieza es una afirmación que se puede comprobar, y cuestionar, en sus propios términos:

- **La razón de tokens por parámetro (etapa 3).** ¿Están el número de parámetros y el número de tokens planificados cerca del rango aproximado de 20 a 25 tokens por parámetro de Hoffmann et al. para el presupuesto de cómputo elegido, o se inclinan hacia la asignación de Kaplan et al., cargada de parámetros y comparativamente escasa de datos? Un plan que se aparta del rango óptimo en cómputo necesita una razón declarada, no silencio.
- **El pipeline de datos (etapas 1 y 2).** ¿Se puede alcanzar el número de tokens a partir de un corpus que realmente se ha obtenido, deduplicado y filtrado por calidad, o supone datos que todavía no existen a la escala y la calidad necesarias?
- **El plan de paralelismo (etapas 4 a 6).** ¿Coinciden el número de dispositivos, la estrategia de reparto y cualquier división de tensor o pipeline parallelism del plan con la interconexión real del hardware, según el propio razonamiento de la Lección 14, o supone patrones de comunicación que el hardware no puede soportar con eficiencia?
- **El plan de estabilidad y monitorización (etapas 7 a 9).** ¿Dice el plan qué precisión, qué clipping y qué programa se usarán, e incluye checkpointing lo bastante frecuente y una monitorización lo bastante minuciosa para las tasas de falla que la propia evidencia de la etapa 8 mostró que son normales a esta escala, no excepcionales?

### Por qué agrupar todo esto en un solo número invita a la pregunta equivocada

Un presupuesto presentado solo como un costo total único invita a exactamente una pregunta a cambio: si se puede abaratar. Un presupuesto presentado como las afirmaciones concretas de arriba invita a un conjunto de preguntas más útil: ¿es esta razón de tokens por parámetro realmente óptima en cómputo para el objetivo declarado, existen los datos para respaldarla, coincide el plan de paralelismo con el hardware y está la ejecución protegida frente a la tasa de falla que debería esperar una ejecución de esta duración? Defender cada afirmación por separado es también lo que permite decir, con honestidad, dónde es incierto el plan (una fuente de datos no probada, un supuesto de interconexión sin verificar) en lugar de presentar una confianza uniforme en un plan que no la tiene.

### Lo que "defendible" no significa

Defender un presupuesto de cómputo no significa garantizar que la ejecución de entrenamiento tenga éxito al primer intento, ni que un comité de revisión deba aprobarlo. Significa que cada cifra importante del plan se remonta a una razón declarada y fundamentada en el material que cubrió este track, de modo que un cuestionamiento de cualquiera de ellas ("por qué esta razón", "por qué esta división de paralelismo", "por qué este intervalo de checkpoints") tenga una respuesta distinta de "es lo que hacemos siempre".

## Práctica

1. ▢ Un plan de preentrenamiento propuesto entrena un modelo de 30 mil millones de parámetros con 200 mil millones de tokens. Usando el rango aproximado de 20 a 25 tokens por parámetro de la etapa 3, ¿está la razón de este plan dentro o fuera de ese rango, y qué pregunta de seguimiento plantea eso?

<details markdown="1"><summary>Pista</summary>

Divide el número de tokens entre el número de parámetros y compáralo con el rango.

</details>

<details markdown="1"><summary>Comprobación</summary>

Unos 6.7 tokens por parámetro (`200 / 30`), muy por debajo del rango aproximado de 20 a 25. Esto plantea la pregunta de seguimiento de por qué el plan se entrena con comparativamente pocos datos en relación con su tamaño, el mismo patrón subentrenado que diagnosticó la Lección 6 en GPT-3, y de si esa desviación del rango óptimo en cómputo es deliberada y está justificada o simplemente no se ha examinado.

</details>

2. ▢ Un equipo presenta un presupuesto de preentrenamiento como una única cifra de dólares totales sin más desglose. Según esta lección, ¿cuál es el problema principal de presentarlo así?

    - a) Un número único es siempre inexacto
    - b) Invita solo a "se puede abaratar" a cambio, en lugar de sacar a la luz qué afirmaciones concretas (razón, datos, paralelismo, plan de estabilidad) son realmente sólidas o frágiles
    - c) Los revisores no pueden entender las cifras en dólares
    - d) Es ilegal presentar un presupuesto de esta manera

<details markdown="1"><summary>Comprobación</summary>

**b)** es el problema real que plantea esta lección: agrupar todas las decisiones en un solo número oculta qué partes del plan están bien respaldadas y cuáles son supuestos, e invita a una conversación mucho menos útil que la que traería defender cada afirmación. (a), (c) y (d) no son el razonamiento que da esta lección.

</details>

3. ▢ Nombra las cuatro categorías de afirmación en que, según esta lección, debería desglosarse un plan de preentrenamiento defendible.

<details markdown="1"><summary>Comprobación</summary>

La razón de tokens por parámetro, el pipeline de datos (obtención de fuentes, deduplicación, filtrado de calidad), el plan de paralelismo ajustado a la interconexión del hardware, y el plan de estabilidad y monitorización (precisión, clipping, programa, frecuencia de checkpointing).

</details>

## Prácticas en el mundo real

- [ ] Busca un informe técnico publicado de un modelo preentrenado abierto y comprueba cuántas de las cuatro categorías de afirmación de esta lección enuncia de forma explícita (razón, pipeline de datos, plan de paralelismo, plan de estabilidad y monitorización). Anota las que deja sin enunciar.
- [ ] Para un presupuesto de cómputo a tu elección, escribe las cuatro categorías como un plan breve con viñetas, con una oración de justificación cada una, tal como argumenta esta lección que debería presentarse un presupuesto defendible.
- [ ] Mañana: elige una de tus cuatro viñetas de la práctica anterior y anota qué evidencia, de este track o de otra parte, señalarías si alguien cuestionara esa afirmación concreta.

## Para profundizar

- [Paper: "Training Compute-Optimal Large Language Models", Hoffmann et al., 2022](https://arxiv.org/abs/2203.15556)
- [Recursos](../RESOURCES.md)

---

¿No termina de quedar claro? Vuelve a leer la fuente primaria de arriba, ya que esta lección la comprime y en la compresión es donde se escapa la comprensión. Consulta el [glosario](../GLOSSARY.md) por si algún término te resultó resbaladizo.

Si lo poco claro es la propia lección y no el material, eso es un defecto: [abre un issue](https://github.com/TokenCemetery/teach/issues).
