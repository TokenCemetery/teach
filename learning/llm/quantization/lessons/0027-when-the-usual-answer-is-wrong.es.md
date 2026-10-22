---
title: "27. Cuando la respuesta habitual es incorrecta"
description: "Reconocer cuándo los pesos de 4 bits o una receta estándar son la decisión equivocada, y resolver la disputa desde la fuente primaria"
type: lesson
---

# Lección 27. Cuando la respuesta habitual es incorrecta

**Vínculo con la misión:** El track termina confiando en que tomes la decisión sobre una cuantización y se la expliques a otra persona. "Usa pesos de 4 bits" y "AWQ supera a GPTQ" son las respuestas habituales, y cada una es verdadera para algunos modelos, tareas y hardware y falsa para otros. Esta lección es el método para averiguar cuál, y los casos en que la respuesta habitual falla.
**Fuente principal:** [Paper: "Scaling Laws for Precision", Kumar et al., 2024](https://arxiv.org/abs/2411.04330), secciones 1 a 3
**Requisitos previos:** [Lección 25](0025-choosing-a-scheme.md), [Lección 26](0026-reviewing-a-quantization-claim.md), [Cuantización post-entrenamiento](../GLOSSARY.md), [Limitado por cómputo](../GLOSSARY.md), [Cuantización solo de pesos](../GLOSSARY.md)

## Calentamiento

1. ▢ ¿Por qué una activación masiva o una outlier feature arruina un scale per-tensor, y qué solución reduce el grupo en lugar de mantener los outliers en alta precisión?

<details markdown="1"><summary>Comprobación</summary>

El scale lo fija el mayor valor, así que un valor enorme deja casi todos los demás en unos pocos niveles cercanos a cero. Los scales per-group reducen el grupo para que el outlier solo desperdicie los niveles de su propio grupo (lecciones 7, 8 y 6).

</details>

2. ▢ ¿Qué aporta un calibration set a GPTQ y a AWQ, y cómo se manifiesta uno que no coincide?

<details markdown="1"><summary>Comprobación</summary>

Estadísticas de activaciones de entradas representativas: GPTQ las usa para la compensación de error de segundo orden, AWQ para encontrar qué canales de pesos se encuentran con activaciones grandes. Un conjunto que no coincide se manifiesta como un modelo que puntúa bien con texto parecido a los datos de calibración y peor con el tráfico al que no se parecía (lecciones 10, 11 y 12).

</details>

3. ▢ ¿Qué es un flip, y por qué puede ser grande cuando el accuracy no cambia?

<details markdown="1"><summary>Comprobación</summary>

Una respuesta que cambió de correcta a incorrecta o al revés entre el baseline y el modelo cuantizado. Las ganancias y las pérdidas se cancelan en el promedio, así que el accuracy puede ser igual mientras muchas respuestas individuales se mueven (lecciones 21 y 26).

</details>

## Qué debes saber

### El método

Una respuesta habitual llega como un eslogan sin sus condiciones. Cuatro pasos deciden si se sostiene en tu caso.

1. **Encuentra la fuente primaria.** El paper, no la entrada que lo cita, leído para ver qué se midió de verdad.
2. **Comprueba el modelo, el tamaño y la fecha.** Qué familias de modelos, de qué tamaño, entrenados con cuántos datos, medidos cuándo. Un resultado sobre modelos de 2022 dice poco sobre una receta de 2024.
3. **Comprueba qué cubre la afirmación.** El accuracy zero-shot frente a bits totales no es throughput de servicio, y un promedio sobre tareas académicas no es chat abierto.
4. **Prueba en tus propias tareas.** Si la fuente y tu caso difieren, el resultado que lo zanja es el tuyo (lección 22).

Ninguno de los casos de abajo dice que la respuesta habitual sea siempre errónea. Cada uno dice qué respalda su fuente, y dónde se detiene.

### Caso 1: un modelo muy entrenado

Kumar et al. ajustan leyes de escalado "conscientes de la precisión" y encuentran que la degradación por la cuantización post-entrenamiento aumenta a medida que un modelo se entrena con más datos, "lo que acaba haciendo que los datos de preentrenamiento adicionales sean activamente perjudiciales" ([resumen](https://arxiv.org/abs/2411.04330)). Su intuición: un modelo entrenado con más datos comprime más información en sus pesos, así que perturbarlos duele más. Llaman "sobreentrenados" a los modelos con una razón muy alta de tokens de entrenamiento por parámetro, y señalan que Llama-3-8B se entrena con una razón de unos 2000.

Lee el alcance. Ajustan sus leyes con más de 465 ejecuciones de preentrenamiento y validan en modelos de hasta 1.7B parámetros entrenados con hasta 26B tokens. Señalan que hace falta una cantidad irrazonable de datos para que el preentrenamiento extra se vuelva perjudicial con precisiones de uso común como 8 bits, pero que en modelos muy sobreentrenados los efectos de degradación se vuelven no triviales en torno a los 5 bits y dominantes por debajo de eso. Así que la afirmación es que la respuesta habitual de 4 bits se vuelve más arriesgada a medida que crece el presupuesto de entrenamiento por parámetro, y la evidencia son modelos de pequeña escala más una ley ajustada. No es una medición de cuánto pierde un checkpoint concreto de Llama 3.

Existe un resultado contrastante. Kurtic et al. midieron modelos Llama 3.1 cuantizados de 8B, 70B y 405B y encontraron que W4A16 recuperaba el 99.36 por ciento del promedio de bf16 en las tareas de Open LLM Leaderboard V1, usando un GPTQ ajustado ([Kurtic et al., 2024](https://arxiv.org/abs/2411.02355)). Los dos no se zanjan mutuamente. Uno es una ley ajustada en modelos pequeños, el otro una medición de una familia con una receta ajustada y tareas promediadas. La lección es tratar un modelo muy entrenado como una razón para medir con más cuidado, no como un veredicto en ningún sentido.

### Caso 2: un modelo pequeño, o un modelo de razonamiento

Kurtic et al. informan de que los modelos más pequeños pierden algo más en INT4. Sus benchmarks de razonamiento, ejecutados en modelos DeepSeek-R1-Distill, lo muestran en números: la recuperación del promedio de bf16 para W4A16-INT fue del 99.5 por ciento para Qwen-32B y del 98.3 por ciento para Llama-70B, del 97.2 por ciento para Llama-8B y del 93.5 por ciento para Qwen-1.5B, para el que W8A8-INT recuperó el 96.9 por ciento y W8A8-FP el 100.3 por ciento. Un estudio aparte de modelos de razonamiento cuantizados, [Liu et al., 2025](https://arxiv.org/abs/2504.04823), encuentra que la cuantización sin pérdida es alcanzable con W8A8 o W4A16 pero que hay riesgos significativos de accuracy con anchos de bits menores. Su resumen nombra el tamaño del modelo, el origen del modelo y la dificultad de la tarea como los determinantes.

Fíjate también en el ruido. En AIME24, el modelo de 1.5B obtuvo 30.1 con un margen informado de 5.3 en bf16 y 24.6 con un margen de 5.1 en W4A16, así que las diferencias de un solo benchmark sobre conjuntos pequeños se solapan con sus propios márgenes. El promedio sobre tareas dice que el modelo pequeño perdió más. La tarea individual no lo demostraría.

### Caso 3: contexto largo, donde la preocupación no se sostiene

Es fácil suponer que el contexto largo se rompe con la cuantización. En el benchmark de contexto largo RULER, evaluado de 4k a 128k tokens, Kurtic et al. informan de una recuperación promedio de la puntuación de al menos el 98 por ciento en los tres formatos, con el modelo de 405B sin evaluar por ser prohibitivamente caro. Es un benchmark sobre Llama 3.1 y no cubre la cuantización de la KV cache, que el paper lista entre las cosas que no estudió. Es un buen ejemplo de una preocupación habitual que la fuente no respalda, para el caso que midió.

### Caso 4: servicio limitado por cómputo

Los 4 bits solo de pesos son la respuesta habitual para la presión de memoria, y suponen que el trabajo está limitado por el ancho de banda de memoria. Los autores de MARLIN dan la aritmética: un token de entrada cuesta 2 FLOPs por peso y la GPU puede ejecutar unos 100 FLOPs en el tiempo que tarda en cargarse un peso de 4 bits, así que la carga de memoria domina solo mientras el lote esté por debajo de unos 50 ([Frantar et al., 2024](https://arxiv.org/abs/2408.11743)). La misma razón entre cómputo y ancho de banda hace que un peso de 16 bits tarde cuatro veces más en cargarse, así que el cruce para bf16 queda cerca del lote 200. Cuantizar los pesos baja el cruce, y por eso la ganancia se reduce a medida que crecen los lotes.

Los métodos INT4 existentes, informa QServe, sufren una sobrecarga de descuantización del 20 al 90 por ciento y aceleran solo la inferencia con lotes pequeños ([Lin et al., 2024](https://arxiv.org/abs/2405.04532)). En los resultados de servicio asíncrono de Kurtic et al. W8A8 domina el throughput. Para un servicio limitado por throughput en hardware moderno, la respuesta habitual de 4 bits es la equivocada.

### Caso 5: cuando fp8 es el valor por defecto más seguro

Si la GPU calcula fp8 de forma nativa, W8A8-FP es efectivamente sin pérdida en todos los tamaños de modelo en los datos de Kurtic et al., y no necesita datos de calibración porque cuantizan con round-to-nearest. Un W8A8-INT bien ajustado perdió de 1 a 3 por ciento, y necesitó SmoothQuant y mejores datos de calibración en 70B. Así que donde el hardware lo soporta y la memoria cabe, fp8 es el primer intento de menor riesgo, y los 4 bits tienen que ganarse su lugar con una necesidad de memoria o de latencia de decode.

### Zanjar una disputa desde la fuente primaria

Dos colegas dicen dos cosas.

- **"AWQ siempre supera a GPTQ".** Abre la Tabla 1 de Kurtic et al. en lugar de discutir. En los benchmarks académicos AWQ superó a GPTQ solo en 0.23 y 0.35 puntos en 8B y 70B, un casi empate. En los benchmarks del mundo real (Arena-Hard, HumanEval, MBPP) GPTQ superó a AWQ en 2.9 puntos en 8B (52.3 frente a 49.4) y en 0.8 en 70B. Atribuyen los hallazgos anteriores que favorecían a AWQ a hiperparámetros subóptimos, y dan su propia configuración: GPTQ con recorte óptimo por MSE donde la comparación anterior usaba abs-max, un calibration set mejor que el C4 por defecto y tamaño de grupo 128 para ambos. Luego comprueba el ruido: en Arena-Hard en 8B, las dos ejecuciones del modelo bf16 obtuvieron 25.1 y 26.5, así que una diferencia cercana a 1 punto queda dentro de la variación entre ejecuciones. Lo que respalda la fuente: ningún método gana siempre, el ranking se movió con la receta y el tipo de tarea, y los autores son un único equipo que además eligió GPTQ como su método. Ejecuta ambos en tus tareas.
- **"La perplexity subió 0.1, así que está bien".** Pregunta: ¿respecto de qué baseline, sobre qué texto y ventana, y qué pasó con las respuestas individuales? Dutta et al. encontraron esquemas con accuracy a un 0 a 2 por ciento del baseline y flips de hasta el 13.6 por ciento, y modelos comprimidos con muchos flips que puntuaban significativamente peor en MT-Bench. Un cambio de perplexity de 0.1 es un promedio y podría ser pequeño o grande según sobre qué se promedie. La fuente respalda "comprueba los flips y una tarea abierta", no "0.1 es demasiado pequeño para importar" ni "0.1 es demasiado grande".

## Práctica

1. ▢ Un colega dice "AWQ siempre supera a GPTQ". ¿Qué tabla abres, y qué compruebas en ella?

<details markdown="1"><summary>Comprobación</summary>

Abre la comparación directa de Kurtic et al. (Tabla 1) y comprueba la configuración que hay detrás: el mismo tamaño de grupo, el método de recorte, el calibration set y si las tareas son académicas o abiertas. Muestra un casi empate en tareas académicas y una ventaja de GPTQ en las del mundo real. No muestra que GPTQ gane siempre, solo que la afirmación sobre AWQ tiene condiciones.

</details>

2. ▢ Un compañero dice "Kumar et al. demostraron que los 4 bits post-entrenamiento destrozarán nuestro modelo muy entrenado". ¿Qué respalda el paper?

    - a) Una ley ajustada, así que mide tu modelo
    - b) Una demostración de que todo esquema de 4 bits falla
    - c) Un resultado solo sobre entrenar en fp4
    - d) Una medición del checkpoint exacto de tu modelo

<details markdown="1"><summary>Comprobación</summary>

**a)** El paper ajusta leyes sobre ejecuciones de hasta 1.7B parámetros y 26B tokens y encuentra que más datos elevan la degradación de la cuantización post-entrenamiento, lo que es una razón para medir tu modelo, no un veredicto sobre él. (b) exagera una ley ajustada hasta una demostración. (c) es incorrecta porque cubre la cuantización post-entrenamiento además de la precisión del entrenamiento. (d) es incorrecta porque no midió ningún checkpoint tuyo.

</details>

3. ▢ Predice y luego ejecuta. Usando la cifra de MARLIN de unos 100 FLOPs por carga de un peso de 4 bits y 2 FLOPs por token y por peso, predice el tamaño de lote por debajo del cual domina la memoria para pesos de 4 bits y para pesos de 16 bits si la razón de cómputo a ancho de banda de la máquina es la misma. Luego ejecuta esto.

    ```python
    flops_per_weight_load_4bit = 100
    flops_per_token_per_weight = 2
    for name, bytes_per_weight in [("4-bit weights", 0.5), ("16-bit weights", 2.0)]:
        flops_per_byte = flops_per_weight_load_4bit / 0.5
        crossover = flops_per_byte * bytes_per_weight / flops_per_token_per_weight
        print(f"{name:15s} memory-bound below batch about {crossover:.0f}")
    ```

<details markdown="1"><summary>Pista</summary>

Un peso de 16 bits son cuatro veces los bytes de uno de 4 bits, así que hacen falta cuatro veces más FLOPs para cubrir su carga.

</details>

<details markdown="1"><summary>Comprobación</summary>

```text
4-bit weights   memory-bound below batch about 50
16-bit weights  memory-bound below batch about 200
```

La cifra de 4 bits es la estimación del propio MARLIN, y la de 16 bits es esta aritmética con la misma suposición, no una medición. El punto se sostiene sin números exactos: cuantizar los pesos baja el tamaño de lote al que un servicio pasa a estar limitado por cómputo, así que un servicio que corre lotes grandes gana menos con 4 bits solo de pesos.

</details>

4. ▢ De la tabla de razonamiento de Kurtic et al.: Qwen-1.5B obtuvo 30.1 (margen 5.3) en AIME24 en bf16 y 24.6 (margen 5.1) en W4A16-INT, con una recuperación promedio del 93.5 por ciento. Un colega dice "AIME24 demuestra que los 4 bits lo rompieron". ¿Qué dices?

<details markdown="1"><summary>Comprobación</summary>

En AIME24 por sí solo las dos puntuaciones quedan dentro de sus márgenes informados una de la otra, así que ese benchmark no lo demuestra. La recuperación promedio del 93.5 por ciento sobre tres tareas, junto al 98 a 99 por ciento de los modelos mayores, es la evidencia más fuerte de que el modelo más pequeño perdió más. Ninguna de las dos dice que el modelo sea inutilizable: el siguiente paso es ejecutar tus propias tareas con suficientes muestras para distinguir la diferencia del ruido.

</details>

5. ▢ Un equipo tiene GPU H100, memoria suficiente para un modelo de 8B en bf16 y un trabajo por lotes donde lo único que importa es el throughput. Un colega propone AWQ de 4 bits "porque 4 bits es lo estándar". Haz el caso en contra, y di qué te haría cambiar de opinión.

<details markdown="1"><summary>Comprobación</summary>

El trabajo está limitado por cómputo con lotes grandes, donde los 4 bits solo de pesos ganan poco y su descuantización puede costar throughput (MARLIN, QServe), mientras que W8A8-FP es efectivamente sin pérdida en los datos de Kurtic et al. y domina sus resultados de throughput asíncrono en hardware con fp8 nativo. La memoria no es una restricción. Lo que te haría cambiar de opinión: una comparación medida de throughput y calidad con tu propio tamaño de lote y tus tareas que muestre al kernel de 4 bits por delante, o un límite de memoria que obligara a un modelo mayor del que cabe a 8 bits.

</details>

## Prácticas en el mundo real

- [ ] Toma una regla empírica de cuantización en la que confíes (por ejemplo "4 bits está bien") y rastréala hasta el paper. Anota los modelos, los tamaños, el año y qué se midió, y en qué difiere tu caso.
- [ ] Abre la Tabla 1 de Kurtic et al. y anota en una línea las diferencias de configuración entre sus ejecuciones de GPTQ y de AWQ, para poder responder desde la tabla a la próxima discusión de "cuál es mejor".
- [ ] Mañana: para el modelo que más te gustaría cuantizar, escribe el caso de esta lección que más probablemente se aplique a él, y la medición que mostraría si se aplica.

## Para profundizar

- [Lista de revisión de cuantización](../reference/quantization-review-checklist.md)
- [Paper: "Scaling Laws for Precision", Kumar et al., 2024](https://arxiv.org/abs/2411.04330)
- [Paper: "Give Me BF16 or Give Me Death? Accuracy-Performance Trade-Offs in LLM Quantization", Kurtic et al., 2024](https://arxiv.org/abs/2411.02355)
- [Paper: "Quantization Hurts Reasoning? An Empirical Study on Quantized Reasoning Models", Liu et al., 2025](https://arxiv.org/abs/2504.04823)
- [Recursos](../RESOURCES.md)

---

Este es el final del track, y el hábito para el que se construyó es el de esta lección: un modelo cuantizado es una afirmación sobre un formato numérico, un método, un kernel y un conjunto de tareas, así que encuentra de dónde viene la afirmación, comprueba qué cubrió y mide en tus propias tareas antes de defenderla ante nadie más.

¿No termina de quedar claro? Vuelve a leer la fuente primaria de arriba, ya que esta lección la comprime y en la compresión es donde se escapa la comprensión. Consulta el [glosario](../GLOSSARY.md) por si algún término te resultó resbaladizo.

Si lo poco claro es la propia lección y no el material, eso es un defecto: [abre un issue](https://github.com/TokenCemetery/teach/issues).
