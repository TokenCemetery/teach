---
title: "9. Significancia estadística frente a ruido"
description: "Por qué una diferencia de puntuación hay que medirla frente al ruido que podría producirla por azar, y por qué la comparación pareada supera a tratar dos puntuaciones como independientes"
type: lesson
---

# Lección 9. Significancia estadística frente a ruido

**Vínculo con la misión:** La decisión de go/no-go de la etapa 5 solo es tan buena como saber si una diferencia de puntuación observada es real; esta lección da las herramientas que responden eso, construyendo directamente sobre el punto de la lección 8 de que el número de una sola ejecución lleva su propio ruido.
**Fuente principal:** [Docs: "Define success criteria and build evaluations", Claude Platform Docs](https://platform.claude.com/docs/en/test-and-evaluate/develop-tests)
**Requisitos previos:** [Lección 8](0008-reproducible-runs.md), [Contaminación de datos](../GLOSSARY.md)

## Calentamiento

1. ▢ ¿Por qué la misma eval, ejecutada dos veces con una temperatura distinta de cero, puede producir dos puntuaciones agregadas distintas sin que nada esté mal?

<details markdown="1"><summary>Comprobación</summary>

Muestrear con una temperatura distinta de cero vuelve estocástica la generación, así que son de esperar completaciones distintas, y por tanto puntuaciones por ejemplo distintas, entre ejecuciones. El número de una sola ejecución es una muestra de una distribución, no un hecho fijo sobre el modelo.

</details>

2. ▢ ¿Qué debería registrarse junto con una puntuación de eval reportada para que una comparación posterior sea significativa?

<details markdown="1"><summary>Comprobación</summary>

La semilla aleatoria, la temperatura de generación, las versiones del modelo y del framework, la versión del conjunto de eval y, cuando se ejecutaron varias muestras, la dispersión entre ellas, no solo su media.

</details>

## Qué debes saber

### Una diferencia de puntuación no es automáticamente una diferencia real

Una nueva variante del modelo puntúa 76% frente al 70% de una línea base en el mismo conjunto de eval. Esa brecha de seis puntos parece una mejora, pero la lección 8 ya estableció que la puntuación de una sola ejecución lleva su propio ruido de muestreo. La pregunta que responde esta lección: ¿es una brecha de seis puntos mayor que el ruido que podría producirla solo por azar, o es justo el tipo de variación que dos ejecuciones del mismo modelo podrían mostrar entre sí?

### El tamaño de la muestra fija cuánto ruido esperar

Para una puntuación de tipo aprobado/suspendido sobre *N* ejemplos, con una tasa real de aciertos *p*, el error estándar de la proporción medida es aproximadamente `sqrt(p(1−p)/N)`. Una tasa de aciertos de 0.70 sobre 100 ejemplos tiene un error estándar de aproximadamente `sqrt(0.70 × 0.30 / 100) ≈ 0.046`, o unos 4.6 puntos porcentuales; una tasa de aciertos de 0.76 sobre los mismos 100 ejemplos tiene un error estándar de unos 4.3 puntos. Una brecha de seis puntos entre dos estimaciones que llevan cada una unos cuatro o cinco puntos de ruido no es claramente mayor que lo que el azar por sí solo podría producir; más ejemplos reducirían cada error estándar (cae con `sqrt(N)`), afinando la estimación y haciendo más fácil distinguir una diferencia real del ruido.

### La comparación pareada es la herramienta más afilada

Tratar las dos puntuaciones como proporciones independientes, como hizo la estimación de arriba, tira información que en realidad está disponible: cuando los mismos ejemplos de eval se pasan tanto por la línea base como por la nueva variante, sabes no solo cuántos acertó cada una, sino qué ejemplos concretos acertó o falló cada una. Una **comparación pareada** mira los ejemplos en que los dos modelos discrepan (uno acertó y el otro no) en lugar de mirar por separado las dos tasas de aciertos crudas. Esto cancela la dificultad a nivel de ejemplo que afecta por igual a ambos modelos: una pregunta que todos los modelos tienden a acertar, o que todos tienden a fallar, no aporta nada a si un modelo es realmente mejor que el otro, y hace que una diferencia real sea más fácil de detectar con la misma cantidad de datos que comparar dos proporciones independientes.

![Una cuadrícula de dos por dos que cruza si la línea base acertó o falló un ejemplo con si la variante lo acertó o falló. Ambas aciertan y ambas fallan son las celdas de acuerdo, mostradas en gris: se cancelan. La línea base acierta y la variante falla, y la línea base falla y la variante acierta, son las celdas de desacuerdo, mostradas en el color de acento: una comparación pareada cuenta solo estas.](images/paired-comparison-grid.svg)

### Qué significa "todavía no significativo" para una decisión de go/no-go

Una brecha que no es claramente mayor que el ruido no es evidencia de que no haya diferencia; es evidencia de que todavía no hay suficiente información para saberlo. La respuesta honesta es ejecutar más ejemplos (reduciendo el error estándar) o ejecutar una prueba de significancia pareada como es debido sobre los desacuerdos, no tratar una puntuación numéricamente mayor como prueba de mejora por sí sola.

## Práctica

1. ▢ Un modelo de línea base aprueba 70 de 100 ejemplos de eval; una nueva variante aprueba 76 de 100. Calcula el error estándar aproximado de cada proporción y di si la brecha de seis puntos parece claramente mayor que el ruido combinado.

<details markdown="1"><summary>Pista</summary>

Usa `sqrt(p(1−p)/N)` para cada proporción por separado, con N = 100.

</details>

<details markdown="1"><summary>Comprobación</summary>

Línea base: `sqrt(0.70 × 0.30 / 100) ≈ 0.046`, unos 4.6 puntos. Nueva variante: `sqrt(0.76 × 0.24 / 100) ≈ 0.043`, unos 4.3 puntos. Cada estimación lleva por sí sola unos cuatro o cinco puntos de ruido, así que una brecha de seis puntos no es claramente mayor que lo que ese ruido combinado podría producir por azar; es sugerente, no concluyente, solo con 100 ejemplos.

</details>

2. ▢ ¿Por qué usar un conjunto de eval más grande (más ejemplos) hace más fácil distinguir una diferencia real de puntuación del ruido?

<details markdown="1"><summary>Comprobación</summary>

El error estándar de una proporción cae con `sqrt(N)`, así que un N mayor reduce el ruido de cada estimación. Una brecha que parecía ambigua frente al ruido de 100 ejemplos puede volverse claramente mayor que el ruido al medirla contra, digamos, 1,000 ejemplos, sin que la diferencia real de fondo haya cambiado en absoluto.

</details>

3. ▢ Los mismos 100 ejemplos de eval se pasan tanto por una línea base como por una nueva variante. ¿Por qué mirar qué ejemplos concretos acertó o falló cada modelo (una comparación pareada) es más potente que comparar solo las dos tasas de aciertos crudas, 70% y 76%, como números independientes?

<details markdown="1"><summary>Comprobación</summary>

Comparar tasas de aciertos crudas trata cada puntuación como si viniera de una muestra no relacionada, y descarta el hecho de que se usaron los mismos ejemplos para ambas. Una comparación pareada, en cambio, mira dónde discrepan los dos modelos, cancelando la dificultad a nivel de ejemplo que afecta por igual a ambos (una pregunta que todos los modelos aciertan o que todos fallan no dice nada sobre qué modelo es mejor), lo que hace detectable una diferencia real con menos datos de los que necesita una comparación de proporciones independientes.

</details>

4. ▢ Un equipo observa una brecha de puntuación entre dos variantes del modelo que resulta no ser claramente mayor que el ruido estimado. ¿Cuál es la conclusión honesta, y cuáles son dos formas de obtener una respuesta más clara?

<details markdown="1"><summary>Comprobación</summary>

La conclusión honesta es que todavía no hay suficiente información para decir si la diferencia es real, no que no haya diferencia. Dos formas de aclararlo: ejecutar la eval con más ejemplos, lo que reduce el error estándar de cada estimación, o ejecutar una prueba de significancia pareada como es debido sobre los ejemplos concretos en que las dos variantes discrepan, en lugar de comparar las dos tasas de aciertos crudas como números independientes.

</details>

5. ▢ ¿Qué afirmación es cierta sobre juzgar si una diferencia de puntuación de una eval es real?

    - a) Cualquier brecha positiva entre dos puntuaciones cuenta como evidencia de mejora, sin importar el tamaño de la muestra
    - b) Una brecha debe juzgarse frente al ruido que el tamaño de la muestra podría producir por azar, y una comparación pareada aprovecha los datos con más eficiencia que tratar las puntuaciones como independientes
    - c) La significancia estadística solo importa para las métricas específicas de la tarea, no para las puntuaciones de LLM-as-judge
    - d) Un conjunto de eval más grande nunca puede cambiar si una brecha dada parece significativa

<details markdown="1"><summary>Comprobación</summary>

**b)** Tanto el razonamiento de ruido frente a tamaño de la muestra como la ventaja de la comparación pareada son exactamente lo que cubre esta lección. (a) es falsa: una brecha menor que el ruido estimado no es evidencia sólida, sea cual sea su signo. (c) es falsa: el mismo razonamiento estadístico se aplica a cualquier puntuación agregada, sin importar cómo se calificó. (d) es falsa: el error estándar se reduce con `sqrt(N)`, así que un conjunto de eval más grande puede convertir una brecha ambigua en una clara.

</details>

## Prácticas en el mundo real

- [ ] Para una diferencia de puntuación que hayas observado entre dos variantes del modelo, estima el error estándar de cada proporción con la fórmula de esta lección y comprueba si la brecha es claramente mayor que el ruido combinado.
- [ ] Si tienes resultados por ejemplo de ambas variantes en el mismo conjunto de eval, mira los ejemplos en que discrepan y cuéntalos, como primer paso hacia una comparación pareada.
- [ ] Mañana: decide, para una eval que te importe, si su tamaño de muestra actual es lo bastante grande para detectar el tamaño de mejora que realmente importaría para una decisión de go/no-go.

## Para profundizar

- [Docs: "Define success criteria and build evaluations", Claude Platform Docs](https://platform.claude.com/docs/en/test-and-evaluate/develop-tests)
- [Recursos](../RESOURCES.md)

---

¿No termina de quedar claro? Vuelve a leer la fuente primaria de arriba, ya que esta lección la comprime y en la compresión es donde se escapa la comprensión. Consulta el [glosario](../GLOSSARY.md) por si algún término te resultó resbaladizo.

Si lo poco claro es la propia lección y no el material, eso es un defecto: [abre un issue](https://github.com/TokenCemetery/teach/issues).
