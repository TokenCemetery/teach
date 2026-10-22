---
title: "17. Medir el impuesto de alineación"
description: "El impuesto no aparece en todas partes a la vez, e incluso un eje midió una mejora en lugar de una pérdida"
type: lesson
---

# Lección 17. Medir el impuesto de alineación

**Vínculo con la misión:** "Poder separar una mejora genuina de capacidad de un artefacto del reward hacking o del sesgo del juez" es el punto de Cómo se ve el éxito al que sirve esta etapa. Esta lección cubre cómo se mide realmente el impuesto de alineación, y no solo qué es; la lección 18 cubre cómo detectar el reward hacking una vez terminado el entrenamiento, y pasa el relevo a `llm/evals` para la metodología completa.
**Fuente principal:** [Paper: "Training language models to follow instructions with human feedback", Ouyang et al., 2022](https://arxiv.org/abs/2203.02155)
**Requisitos previos:** [Lección 16](0016-rlaif-how-well-ai-feedback-actually-matches-human-feedback.md), [Impuesto de alineación](../GLOSSARY.md)

## Calentamiento

1. ▢ ¿Qué es direct-RLAIF (d-RLAIF), y cómo se comparó su rendimiento con el del RLAIF canónico, según Lee et al.?

<details markdown="1"><summary>Comprobación</summary>

Una técnica que prescinde de entrenar un reward model aparte y consulta directamente a un modelo de lenguaje estándar para obtener una puntuación de recompensa durante el RL. Lee et al. encontraron que logró un mejor rendimiento que el RLAIF canónico, y no meramente un rendimiento comparable a menor costo.

</details>

2. ▢ ¿En cuál de las tres tareas que probaron Lee et al. superó RLAIF a RLHF, en lugar de limitarse a igualarlo?

<details markdown="1"><summary>Comprobación</summary>

En la generación de diálogo inocuo.

</details>

## Qué debes saber

### El impuesto no es un número; es un conjunto de mediciones separadas

La lección 1 presentó el impuesto de alineación como un costo real y medido, sin detallar cómo se mide realmente. Ouyang et al. lo hicieron enfrentando su modelo alineado a una batería de benchmarks públicos de NLP existentes y comparando el resultado con el modelo base sin alinear, en cada benchmark por separado, en lugar de colapsarlo todo en una única cifra de impuesto. Informan de regresiones concretas en ciertos benchmarks, en particular SQuAD, DROP, HellaSwag y la traducción de francés a inglés de WMT 2015, y, lo que es importante, **ningún cambio significativo** en otros dos que también comprobaron, Winogender y CrowSPairs (benchmarks relacionados con el sesgo). El impuesto apareció en unos ejes y no en otros; tratarlo como un costo uniforme habría ocultado ese patrón.

### La alineación también produjo una ganancia medida, no solo un costo

La misma batería de evaluación incluía un eje en el que el entrenamiento de alineación se midió como una mejora y no como un costo: con el dataset RealToxicityPrompts, Ouyang et al. informan de que InstructGPT generaba alrededor de un 25 % menos de salidas tóxicas que GPT-3 cuando se le pedía ser respetuoso. Una contabilidad justa de lo que el entrenamiento de alineación hizo a las capacidades medidas de un modelo tiene que incluir este tipo de resultado junto a las regresiones; informar solo del impuesto e ignorar dónde ayudó el mismo entrenamiento sería tan engañoso como informar de que no hay impuesto en absoluto.

### El arreglo, y lo que no costó

La lección 6 ya nombró el mecanismo: mezclar las actualizaciones de PPO con actualizaciones que aumentan la verosimilitud de la distribución de preentrenamiento original (PPO-ptx) redujo mucho las regresiones medidas en SQuAD, DROP, HellaSwag y WMT. Ouyang et al. son concretos en que esta recuperación se produjo **sin comprometer las puntuaciones de preferencia de los anotadores**, es decir, el arreglo no se limitó a devolver las ganancias de alineación a cambio del rendimiento perdido en benchmarks; ambas cosas se midieron, por separado, y el arreglo mejoró una sin costar visiblemente la otra.

### Una comprobación de generalización distinta y más difícil de falsear: anotadores held-out

Más allá de las regresiones en benchmarks, Ouyang et al. ejecutan una comprobación dirigida a una pregunta distinta: ¿generaliza el comportamiento alineado del modelo más allá de las personas concretas cuyas preferencias lo moldearon, o simplemente aprendió a complacer a los anotadores particulares de sus datos de entrenamiento? Lo prueban con **anotadores held-out**, personas que no aportaron ningún dato usado para entrenar el modelo, y encuentran que estos anotadores held-out seguían prefiriendo las salidas de InstructGPT. Esta es la misma idea de fondo para la que `llm/pretraining` y `llm/evals` usan datos held-out: un resultado solo significa lo que afirma significar si no pudo haberse producido simplemente ajustándose a los datos (o a las personas) concretos que moldearon el entrenamiento.

## Práctica

1. ▢ Ouyang et al. informan de regresiones en SQuAD, DROP, HellaSwag y la traducción de WMT, pero ningún cambio significativo en Winogender y CrowSPairs. ¿Qué habría ocultado de este resultado tratar el impuesto de alineación como un único número global?

<details markdown="1"><summary>Comprobación</summary>

Que el impuesto no se aplicó de manera uniforme; apareció con claridad en unos benchmarks y en absoluto en otros. Un único número colapsado presentaría este patrón desigual como si fuera un costo consistente en todas las capacidades.

</details>

2. ▢ ¿Por qué importa la reducción del 25 % de las salidas tóxicas para una contabilidad justa del impuesto de alineación, en lugar de informar solo de las regresiones de SQuAD/DROP/HellaSwag/WMT?

<details markdown="1"><summary>Comprobación</summary>

Porque el entrenamiento de alineación ayudó de forma medible en este eje en lugar de costar algo; informar solo de las regresiones y omitir este resultado subestimaría lo que hizo realmente el entrenamiento, igual que informar de que no hay impuesto en absoluto lo sobrestimaría.

</details>

3. ▢ ¿Qué verificaron concretamente Ouyang et al. sobre el arreglo de PPO-ptx para el impuesto de alineación, además de reducir simplemente las regresiones en benchmarks?

<details markdown="1"><summary>Comprobación</summary>

Que lo hacía sin comprometer las puntuaciones de preferencia de los anotadores; la recuperación del rendimiento en benchmarks no se pagó devolviendo las ganancias de alineación sobre las que se añadió PPO-ptx.

</details>

4. ▢ ¿Por qué probar con anotadores held-out, personas que no aportaron datos de entrenamiento, responde a una pregunta distinta de la que responden las mediciones de regresión en benchmarks?

<details markdown="1"><summary>Comprobación</summary>

Las regresiones en benchmarks miden si capacidades concretas empeoraron. Los anotadores held-out comprueban si el comportamiento alineado del modelo generaliza realmente a preferencias más allá de las personas concretas que moldearon el entrenamiento, en lugar de ajustarse solo de cerca a ese grupo particular; un resultado que valiera únicamente para los anotadores originales no respaldaría la misma afirmación de generalización.

</details>

## Prácticas en el mundo real

- [ ] Busca un informe técnico de post-training publicado y comprueba si informa tanto de regresiones como de mejoras en una batería de benchmarks, o solo de una dirección. Anota qué benchmarks, si alguno, no mostraron un cambio significativo.
- [ ] Lee el párrafo del paper de InstructGPT (enlazado arriba) que describe el experimento con anotadores held-out, y escribe una frase que diga qué resultado te habría hecho dudar de que la alineación del modelo generalizara más allá de sus anotadores de entrenamiento.
- [ ] Mañana: sin mirar adelante, escribe una predicción de una frase para la lección 18: dado que un reward model o un juez de IA puede ser objeto de trampa (lección 5), ¿qué tendría que comprobar la evaluación de un modelo alineado *terminado*, una vez acabado el entrenamiento, que una comparación de train PM frente a test PM durante el entrenamiento no podía?

## Para profundizar

- [Paper: "Training language models to follow instructions with human feedback", Ouyang et al., 2022](https://arxiv.org/abs/2203.02155)
- [Recursos](../RESOURCES.md)

---

¿No termina de quedar claro? Vuelve a leer la fuente primaria de arriba, ya que esta lección la comprime y en la compresión es donde se escapa la comprensión. Consulta el [glosario](../GLOSSARY.md) por si algún término te resultó resbaladizo.

Si lo poco claro es la propia lección y no el material, eso es un defecto: [abre un issue](https://github.com/TokenCemetery/teach/issues).
