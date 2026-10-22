---
title: "16. Destilación on-policy en la práctica"
description: "Qué cuesta por paso la destilación on-policy, qué aporta y cómo la usó Qwen3 para sus modelos pequeños"
type: lesson
---

# Lección 16. Destilación on-policy en la práctica

**Vínculo con la misión:** La misión te pide decir cuándo la destilación on-policy se gana su costo, lo que significa contar qué cuesta un paso, qué señal devuelve y qué midió un equipo de producción frente a la alternativa.
**Fuente principal:** [Paper: "Qwen3 Technical Report", Qwen Team, 2025](https://arxiv.org/abs/2505.09388), sección 4.5 y la discusión de destilación on-policy de la sección 4.7
**Requisitos previos:** [Lección 8](0008-sequence-level-distillation.md), [Lección 14](0014-exposure-bias.md), [Lección 15](0015-gkd-and-minillm.md), [Destilación off-policy](../GLOSSARY.md), [Destilación on-policy](../GLOSSARY.md)

## Calentamiento

1. ▢ ¿Qué controla en GKD la fracción de datos del estudiante lambda, y cuáles son sus dos valores extremos?

<details markdown="1"><summary>Comprobación</summary>

Es la probabilidad de que un paso entrene con secuencias generadas por el estudiante en lugar de con un dataset fijo. Lambda 0 es destilación supervisada sobre datos fijos y lambda 1 es puramente on-policy.

</details>

2. ▢ La primera fase de destilación de Qwen3 entrena con salidas que generó el profesor. ¿Qué término de la lección 8 lo nombra, y es on-policy?

<details markdown="1"><summary>Comprobación</summary>

Destilación a nivel de secuencia, en palabras del informe de Qwen3 "response distillation". Es off-policy: las secuencias las fijó el profesor, no las escribió el estudiante.

</details>

3. ▢ El exposure bias es un desajuste en los prefijos de quién ve el estudiante. Nombra el único componente que un paso on-policy necesita del profesor y que un paso con texto fijo no necesita.

<details markdown="1"><summary>Comprobación</summary>

Su distribución sobre tokens en cada posición de la propia secuencia del estudiante, lo que significa que el modelo profesor debe ejecutarse sobre la salida del estudiante durante el entrenamiento. El texto que el profesor ya escribió no aporta eso.

</details>

## Qué debes saber

### Qué cuesta un paso

Un paso off-policy con texto del profesor almacenado cuesta un forward y backward pass del estudiante sobre secuencias fijas. Un paso off-policy con logits del profesor almacenados añade una lectura de disco, y el costo de almacenamiento pertenece a la lección 7.

Un paso on-policy añade trabajo, y conviene enumerarlo en orden:

| Paso | Trabajo | Notas |
|---|---|---|
| 1 | El estudiante genera una secuencia para cada prompt | Decodificación secuencial. Más barata que si la hiciera el profesor, porque el estudiante es más pequeño (GKD, sección 3.1) |
| 2 | El profesor ejecuta un forward pass sobre la secuencia terminada | Un pase paralelo, no generación. Necesita al profesor en memoria o accesible |
| 3 | El estudiante ejecuta forward y backward y se calcula la divergencia | Igual que un paso off-policy |

Las dos primeras filas no tienen contrapartida off-policy con texto fijo. La propia nota de eficiencia del paper trata de SeqKD: en el experimento de instruction tuning GKD no ejecutó SeqKD "debido a su ineficiencia computacional para generar datos del profesor durante el entrenamiento" (sección 4.4). El paso 1 aquí usa el modelo pequeño, que es el lado más barato de ese intercambio. Esa comparación de costos es una afirmación del paper, y la tabla de tres filas de arriba es mi contabilidad del trabajo.

### Señal densa frente a recompensa dispersa

La destilación no es la única forma de mejorar un modelo pequeño con sus propias muestras. El aprendizaje por refuerzo también entrena con las propias secuencias del modelo, pero puntúa cada secuencia completa con una recompensa escalar. La sección 3.2 de GKD escribe el objetivo combinado con la recompensa como `r(y)`, un solo número por secuencia.

La destilación on-policy devuelve una puntuación para cada token, tomada de la distribución del profesor en esa posición. Es una señal más densa por muestra. Densa significa más información por secuencia generada. No significa que el profesor tenga razón, a lo que la lección 18 vuelve.

La consecuencia práctica va en un solo sentido. El RL puede mejorar un modelo sin que haya un modelo más fuerte disponible, porque solo necesita una recompensa. La destilación on-policy necesita que exista un profesor más fuerte.

### Cómo la usó Qwen3

El informe de Qwen3 describe un pipeline de post-training de cuatro etapas para sus modelos insignia, y una "strong-to-weak distillation" aparte para los ligeros: cinco modelos densos (0.6B, 1.7B, 4B, 8B y 14B) y un modelo de mezcla de expertos (30B-A3B). La motivación fue el costo: la destilación "elimina la necesidad de realizar un proceso de entrenamiento exhaustivo de cuatro etapas de forma individual para cada modelo de pequeña escala" (sección 4).

Los modelos pequeños se destilan en dos fases (sección 4.5):

| Fase | Datos | Señal de entrenamiento |
|---|---|---|
| Off-policy | Salidas del profesor generadas en modos de pensamiento y de no pensamiento | Response distillation, para dar la habilidad básica de razonamiento y la capacidad de cambiar de modo |
| On-policy | El estudiante genera respuestas en cualquiera de los modos | Se hace fine-tuning del estudiante alineando sus logits con los del profesor (Qwen3-32B o Qwen3-235B-A22B) para minimizar la divergencia KL |

Lee el orden. La fase off-policy va primero, y el informe dice que pone "una base sólida" para la on-policy. Eso coincide con la observación de GKD de que el entrenamiento on-policy supone un estudiante que ya puede generar secuencias aceptables. Es un calendario de dos etapas, no la mezcla de lambda por batch de GKD.

### La comparación con RL

La sección 4.7 compara la destilación on-policy con el aprendizaje por refuerzo directo en Qwen3-8B. Ambos parten del mismo checkpoint destilado off-policy, y la comparación usa solo consultas de matemáticas y de código. La Tabla 21 informa, con pass@64 entre paréntesis donde el informe da uno:

| Método | AIME'24 | AIME'25 | MATH500 | LiveCodeBench v5 | MMLU-Redux | GPQA-Diamond | Horas de GPU |
|---|---|---|---|---|---|---|---|
| Destilación off-policy | 55.0 (90.0) | 42.8 (83.3) | 92.4 | 42.0 | 86.4 | 55.6 | no se da |
| más aprendizaje por refuerzo | 67.6 (90.0) | 55.5 (83.3) | 94.8 | 52.9 | 86.9 | 61.3 | 17,920 |
| más destilación on-policy | 74.4 (93.3) | 65.5 (86.7) | 97.0 | 60.3 | 88.3 | 63.3 | 1,800 |

En cada benchmark de la tabla, la destilación on-policy puntuó más alto que el RL, y usó cerca de una décima parte de las horas de GPU: 17,920 dividido entre 1,800 es 9.96. El informe lo lee como un rendimiento significativamente mejor que el RL con aproximadamente una décima parte de las horas de GPU. También señala que pass@64 en AIME subió tras la destilación y no cambió tras el RL, lo que toma como evidencia de que destilar a partir de los logits del profesor amplía el espacio de exploración del estudiante.

### Cuánto fiarse de esa tabla

Es un informe, un tamaño de estudiante, solo consultas de matemáticas y de código, y los autores compararon sus propios dos métodos. El informe no dice qué profesor se usó para la comparación del 8B. No encontré una declaración de si las cifras de horas de GPU incluyen ejecutar al profesor, así que no asumas que lo hacen. La receta de RL no se describe en la comparación, así que una ejecución de RL mejor afinada podría cerrar parte de la brecha. El resultado es una evidencia fuerte de que la destilación fue más barata y mejor en la configuración de Qwen3, y no evidencia sobre todas las configuraciones.

Fíjate también en lo que la comparación deja fuera. Los propios profesores salieron del pipeline de cuatro etapas, que incluye RL. El ahorro es real, pero supone que alguien ya pagó por el profesor.

## Práctica

1. ▢ Según la Tabla 21, ¿cuántos puntos añadieron el RL y la destilación on-policy en LiveCodeBench v5 sobre el checkpoint off-policy, y cuántas horas de GPU por punto usó cada uno?

<details markdown="1"><summary>Comprobación</summary>

El RL pasó de 42.0 a 52.9, es decir +10.9 puntos, y 17,920 dividido entre 10.9 son unas 1,640 horas de GPU por punto. La destilación on-policy llegó a 60.3, es decir +18.3 puntos, y 1,800 dividido entre 18.3 son unas 98 horas de GPU por punto. La razón es de unos 17 a 1 en este benchmark, mayor que el 10 a 1 del titular, porque la destilación además ganó más puntos. Ambos números son para un tamaño de estudiante y un conjunto de consultas.

</details>

2. ▢ ¿Qué costo está presente en un paso de destilación on-policy y ausente de un paso off-policy con texto del profesor almacenado?

    - a) Hacer backpropagation a través del modelo estudiante
    - b) Calcular una pérdida en cada posición de token
    - c) Ejecutar al profesor sobre la salida del estudiante
    - d) Tokenizar los prompts antes de que empiece el entrenamiento

<details markdown="1"><summary>Comprobación</summary>

**c)** El profesor debe puntuar secuencias que no existían hasta que el estudiante las generó. (b), (a) y (d) también ocurren en los pasos off-policy.

</details>

3. ▢ El pass@1 mejoró tras el RL y tras la destilación on-policy. ¿Qué mostró pass@64 en AIME para cada uno, y qué concluye el informe?

<details markdown="1"><summary>Pista</summary>

Mira los números entre paréntesis de las columnas de AIME para la fila del RL.

</details>

<details markdown="1"><summary>Comprobación</summary>

Con el RL pass@64 se quedó en 90.0 en AIME'24 y 83.3 en AIME'25, sin cambios respecto del checkpoint inicial. Tras la destilación on-policy subió a 93.3 y 86.7. El informe concluye que destilar a partir de los logits del profesor amplió el espacio de exploración del estudiante mientras que el RL no. Es la interpretación de los autores de una comparación.

</details>

4. ▢ Tienes un estudiante de 8B, un profesor más fuerte con el mismo tokenizer, una tarea de matemáticas con una respuesta comprobable y un presupuesto de GPU limitado. ¿Resuelve la tabla de Qwen3 si usar RL o destilación on-policy?

<details markdown="1"><summary>Comprobación</summary>

Apunta hacia la destilación y no lo resuelve. Respalda que, con un profesor fuerte ya disponible y el estudiante calentado antes con destilación off-policy, la destilación on-policy fue más barata y mejor en las ejecuciones de Qwen3. No cubre tu tarea, tu profesor, ni si las cifras de horas de GPU incluyen al profesor. Si no existe un profesor más fuerte, la destilación no está disponible en absoluto y el RL es la vía, que es como se construyeron los profesores de Qwen3.

</details>

5. ▢ ¿Por qué Qwen3 ejecuta la fase off-policy antes que la on-policy, y qué de GKD respalda ese orden?

<details markdown="1"><summary>Comprobación</summary>

La fase off-policy da al estudiante la habilidad básica de razonamiento y el cambio de modo, que según el informe pone una base para el entrenamiento on-policy. GKD hace la misma suposición: necesita un estudiante que ya pueda generar secuencias de calidad adecuada para que la retroalimentación del profesor signifique algo, y sus estudiantes partieron de checkpoints con supervised fine-tuning.

</details>

## Prácticas en el mundo real

- [ ] Abre la sección 4.7 del informe de Qwen3 y encuentra la Tabla 21. Copia en una nota las tres celdas de horas de GPU y de AIME'24 y calcula con ellas los puntos por hora de cada método.
- [ ] Escribe el costo por paso de tu propia ejecución planificada en tres líneas: quién genera, quién puntúa, quién actualiza. Luego marca qué modelo es lo bastante grande para necesitar su propia GPU.
- [ ] Mañana: sin apuntes, escribe las dos fases de Qwen3, con qué entrena cada una, y dos razones para no generalizar la cifra de 1/10.

## Para profundizar

- [Destilación on-policy](../reference/on-policy-distillation.md)
- [Paper: "Qwen3 Technical Report", Qwen Team, 2025](https://arxiv.org/abs/2505.09388)
- [Post-training](../../post-training/)
- [Recursos](../RESOURCES.md)

---

¿No termina de quedar claro? Vuelve a leer la fuente primaria de arriba, ya que esta lección la comprime y en la compresión es donde se escapa la comprensión. Consulta el [glosario](../GLOSSARY.md) por si algún término te resultó resbaladizo.

Si lo poco claro es la propia lección y no el material, eso es un defecto: [abre un issue](https://github.com/TokenCemetery/teach/issues).
