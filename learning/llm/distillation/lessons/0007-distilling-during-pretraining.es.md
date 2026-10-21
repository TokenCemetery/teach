---
title: "7. Destilar durante el preentrenamiento"
description: "Cómo Gemma 2 y Minitron usaron la distribución de un profesor como señal de entrenamiento a escala, y qué cuesta almacenar logits"
type: lesson
---

# Lección 7. Destilar durante el preentrenamiento

**Vínculo con la misión:** La misión te pide escribir la pérdida a nivel de token y decir cuándo no se puede usar, y esta lección muestra esa pérdida como la señal de entrenamiento de dos familias de modelos reales, con el costo de conservar las distribuciones del profesor contado en bytes.
**Fuente principal:** [Paper: "Gemma 2: Improving Open Language Models at a Practical Size", Gemma Team, 2024](https://arxiv.org/abs/2408.00118)
**Requisitos previos:** [Lección 6](0006-the-tokenizer-constraint.md), [Destilación a nivel de token](../GLOSSARY.md), [Logit](../GLOSSARY.md), [Logits top-k](../GLOSSARY.md)

## Calentamiento

1. ▢ ¿Por qué un estudiante Llama con un profesor Qwen descarta la pérdida simple a nivel de token, incluso cuando ambos te dan logits completos?

<details markdown="1"><summary>Comprobación</summary>

La pérdida compara la probabilidad i de la fila del estudiante con la probabilidad i de la del profesor, y tokenizers distintos hacen que el índice i sea un token distinto, con tamaños y posiciones posiblemente distintos. Los remedios de la etapa 2 son una pérdida entre tokenizers o un estudiante de la familia del profesor.

</details>

2. ▢ ¿Qué dirección de la KL minimiza un estudiante que cubre modos, y en qué configuración la encontró mejor Minitron?

<details markdown="1"><summary>Comprobación</summary>

[KL directa](../GLOSSARY.md). Minitron la encontró mejor que la KL inversa al reentrenar base models podados, con una pérdida de LM de 2.155 frente a 2.665 para un Minitron 8B podado en profundidad (Tabla 16 de su paper). Esa es una configuración, y la lección 5 da la evidencia de instruction tuning para la otra dirección.

</details>

## Qué debes saber

Esta lección enseña la mitad de destilación de dos recetas de entrenamiento. Cómo se organiza una corrida de preentrenamiento, de los datos al hardware, pertenece al track de [Preentrenamiento](../../pretraining/), y la poda como método no pertenece a ninguno de los dos.

### La destilación como objetivo de preentrenamiento: Gemma 2

El informe de Gemma 2 entrena sus modelos de 2B y 9B con destilación de conocimiento en lugar de predicción del siguiente token. La motivación es que el entrenamiento de siguiente token escala solo logarítmicamente con los datos, y los modelos pequeños necesitan corridas muy largas para mejorar. La destilación reemplaza el vector one-hot de cada token por la distribución de siguientes tokens de un modelo grande, que según el informe da gradientes más ricos. Su objetivo declarado es entrenar con un número muy grande de tokens con destilación para simular un entrenamiento más allá del número de tokens disponibles (introducción).

Los datos que da el informe:

- El modelo de 2B se entrenó con 2 billones de tokens, el de 9B con 8 billones y el de 27B con 13 billones (sección 3.1). El de 27B se entrenó desde cero, sin destilación.
- Los números de tokens de 2B y 9B son más de 50 veces la cantidad óptima en cómputo que predicen Hoffmann et al. (introducción).
- La pérdida es el logaritmo de verosimilitud negativo entre la probabilidad del profesor de cada token dado su contexto y la del estudiante, minimizado sobre el estudiante: la suma de -P_T(x | x_c) log P_S(x | x_c) (sección 3.2). Esa es la pérdida de la lección 4 con temperatura 1.
- El vocabulario tiene 256,128 entradas (Tabla 1), heredadas de Gemini, y la longitud de contexto es de 8,192 tokens (sección 2).

Sus ablaciones usan un profesor de 7B, no el final. Un estudiante de 2B entrenado con 500B de tokens, que el informe dice que es 10 veces el número óptimo en cómputo para 2B, obtuvo una media de 60.3 en tres benchmarks desde cero y 67.7 destilado (Tabla 6). Con el profesor fijo en 7B, la perplejidad de validación con 200M, 400M y 1B de parámetros fue 23, 19 y 17 desde cero y 21, 17 y 15 destilado (Tabla 7). El informe dice también que el nuevo 2B, con 2T de tokens, mejora significativamente al 2B de Gemma 1 con 3T de tokens (sección 6.1). Son comparaciones propias de Google.

### Lo que el informe no dice

El informe no nombra al profesor de los modelos finales de 2B y 9B ni da su tamaño. No describe cómo se le suministró la distribución del profesor al estudiante: almacenada, calculada junto al entrenamiento o aproximada. Las afirmaciones sobre un top-k muestreado o truncado en Gemma 2 no están en el informe. La sección siguiente calcula lo que cuesta cada opción, para que puedas razonar sobre ello sin una fuente para la elección.

### Lo que cuesta almacenar al profesor

Una distribución sobre el vocabulario para cada token de entrenamiento es grande. El script usa el vocabulario y los números de tokens de Gemma 2 y dos supuestos de esta lección: probabilidades en bf16 de 2 bytes y, para la versión truncada, un k ilustrativo de 256 con un índice de token de 4 bytes.

```python
vocab = 256_128            # Gemma 2 vocabulary size (Table 1 of the report)
tokens = {"2B run": 2e12, "9B run": 8e12}

full = vocab * 2           # bf16: 2 bytes per probability
k = 256                    # an illustrative k, not a number from any paper
topk = k * (2 + 4)         # 2-byte probability + 4-byte token index

print("full per token: %d bytes" % full)
print("top-%d per token: %d bytes (%.1fx smaller)" % (k, topk, full / topk))
print("full per 8192-token sequence: %.2f GB" % (full * 8192 / 1e9))
for name, n in tokens.items():
    print(name, "full: %.2f EB" % (full * n / 1e18), " top-%d: %.2f PB" % (k, topk * n / 1e15))
```

Predice el orden de magnitud del costo de la distribución completa para la corrida de 2B antes de ejecutarlo. La salida:

```text
full per token: 512256 bytes
top-256 per token: 1536 bytes (333.5x smaller)
full per 8192-token sequence: 4.20 GB
2B run full: 1.02 EB  top-256: 3.07 PB
9B run full: 4.10 EB  top-256: 12.29 PB
```

Almacenar distribuciones completas para la corrida de 2B es alrededor de un exabyte, y para la de 9B alrededor de cuatro. Conservar 256 entradas por token lo reduce en un factor de 333.5, a petabytes, y la cifra sigue contando los tokens de entrenamiento una sola vez, sin repetir épocas. El truncamiento también cuesta algo. La masa de la cola que se descarta hay que manejarla, renormalizando o tratándola como un solo cubo, y la elección cambia el objetivo.

Hay una alternativa que no almacena nada: ejecutar el profesor junto al estudiante y leer su distribución del forward pass. Minitron toma esa vía, y señala que la destilación añade la sobrecarga de un forward pass adicional del profesor, así que comparan sus ejecuciones destilada y convencional con el mismo cómputo (sección 4). Qué vía usó un laboratorio dado no es algo que esta lección afirme.

Los autores de Minitron también probaron el truncamiento directamente. En su apéndice sobre destilación (A.3), conservar solo los top K logits del profesor y del estudiante para K hasta 100 causó una caída significativa de la exactitud. La caída desapareció con K mayores, pero los resultados no fueron mejores que no truncar. Es una sola configuración de reentrenamiento de un modelo podado, y el K en que el truncamiento deja de perjudicar diferirá según el vocabulario y el modelo.

### Poda más destilación: Minitron

Minitron (Muralidharan et al., 2024) comprime Nemotron-4 15B podándolo y recuperando la exactitud reentrenando con el original como profesor. Su estudiante empieza como una copia podada, así que comparte el tokenizer del profesor por construcción. Esta lección toma solo la mitad de destilación.

- **Tokens.** Los modelos Minitron 8B y 4B se reentrenaron cada uno con 94 mil millones de tokens. El paper compara Minitron 8B con Nemotron-3 8B, entrenado con 3.8 billones, y enuncia el ahorro como 40 veces menos tokens (Tabla 2).
- **Destilación frente a reentrenamiento convencional.** Para un modelo de 4B comparan con el mismo cómputo (Tabla 11). Entrenar desde cero con 150B de tokens dio HellaSwag 46.22 y MMLU 24.36. Podar 15B a 4B y reentrenar de forma convencional con 150B dio 50.85 y 24.57. Podar y reentrenar con destilación con 100B de tokens dio 51.04 y 37.81. La corrida destilada usa 100B de tokens frente a 150B por el forward pass extra del profesor. Eso es una mejora de 4.8 puntos en HellaSwag y 13.5 en MMLU respecto de entrenar desde cero.
- **Pérdida.** KL directa sobre los logits, con temperatura 1, con la pérdida de logits sola mejor que una mezcla ponderada con la pérdida de modelado de lenguaje, y sin mejora al truncar a top K (sección 4 y apéndice A.3).

El paper de seguimiento (Sreenivas et al., 2024) aplica la receta a Llama 3.1 8B y Mistral NeMo 12B. Añade un paso antes de la destilación: la corrección del profesor. Cuando los datos de preentrenamiento originales no están disponibles, el profesor da una guía subóptima sobre un dataset distinto, que los autores atribuyen a un cambio en la distribución de los tokens de subpalabra. Así que primero hacen fine-tuning del profesor con unos 100B de tokens de los datos de destilación, con warm-up y learning rates bajos. Luego podan y destilan con KL directa solo sobre los logits. Llama-3.1-Minitron 4B se reentrenó con 94B de tokens y MN-Minitron-8B con 380B (Tabla 4). El paper dice que el 4B se compara favorablemente con Llama 3.1 8B usando 150 veces menos tokens, 94B frente a 15T, y que el 8B supera a Llama 3.1 8B usando 40 veces menos, 380B frente a 15T (sección 5.1). Son comparaciones de NVIDIA sobre su propia evaluación.

## Práctica

1. ▢ En el informe, ¿qué modelos de Gemma 2 se entrenaron con destilación, y cuántos tokens vio cada uno?

    - a) El 2B con 8T y el 27B con 2T
    - b) El 9B con 8T y el 27B con 13T
    - c) Los tres modelos se entrenaron cada uno con 13T de tokens
    - d) El 2B con 2T y el 9B con 8T

<details markdown="1"><summary>Comprobación</summary>

**d)** El 27B se entrenó desde cero con 13T de tokens, así que (b) y (c) lo incluyen por error. La opción (a) intercambia los números de tokens. El informe enuncia los números en la sección 3.1.

</details>

2. ▢ Con un vocabulario de 256,128 y 2 bytes por probabilidad, ¿cuántos bytes ocupa una distribución completa del siguiente token, y a cuántos gigabytes asciende para una única secuencia de 8,192 tokens?

<details markdown="1"><summary>Pista</summary>

Multiplica el vocabulario por los bytes por entrada, luego por la longitud de la secuencia, y divide entre mil millones.

</details>

<details markdown="1"><summary>Comprobación</summary>

256,128 por 2 son 512,256 bytes por token. Por 8,192 da 4,196,401,152 bytes, unos 4.20 GB para una secuencia. Una corrida de entrenamiento tiene muchos millones de secuencias así, por eso existe la pregunta de almacenar frente a recalcular.

</details>

3. ▢ Conservando las 256 entradas principales, cada una con una probabilidad de 2 bytes y un índice de 4 bytes, ¿qué tamaño tiene el registro de un token, y cuánto más pequeño es que la distribución completa?

<details markdown="1"><summary>Comprobación</summary>

256 por 6 son 1,536 bytes, que es 333.5 veces menos que 512,256. El k de 256 y los tamaños en bytes son supuestos de esta lección, no cifras de Gemma 2. El registro además omite la cola de la distribución, que hay que renormalizar o agrupar en un cubo, y esa elección cambia el objetivo.

</details>

4. ▢ Una publicación de un foro dice que Gemma 2 se entrenó con una distribución del profesor top-256 almacenada. ¿Qué haces con esa afirmación?

<details markdown="1"><summary>Comprobación</summary>

Búscala en el informe. El informe enuncia la pérdida, los números de tokens y las ablaciones, y no describe cómo se suministró la distribución. Así que la afirmación no está verificada por el informe. Trátala como no respaldada, anota lo que falta y busca una fuente primaria, como el texto de los autores, antes de apoyarte en ella.

</details>

5. ▢ En la Tabla 11 de Minitron, podar más reentrenamiento convencional alcanzó un MMLU de 24.57 y podar más destilación alcanzó 37.81, con la destilación sobre menos tokens. ¿Por qué los números de tokens son 150B y 100B, y cuál es el límite de la tabla?

<details markdown="1"><summary>Comprobación</summary>

Comparan con el mismo cómputo, y la destilación gasta parte de su presupuesto en el forward pass del profesor, así que recibe 100B de tokens frente a 150B. La tabla es de un modelo de 4B podado de Nemotron-4 15B. Los autores la usan para mostrar que la destilación supera al reentrenamiento convencional tras la poda. No muestra la mejora para otros profesores, tamaños o benchmarks.

</details>

6. ▢ La corrección del profesor en el paper de seguimiento de Minitron hace fine-tuning del profesor con unos 100B de tokens antes de destilar. ¿Cuándo hace falta, y a qué culpan los autores cuando se omite?

<details markdown="1"><summary>Comprobación</summary>

Hace falta cuando los datos de preentrenamiento originales del profesor no están disponibles, así que los datos de destilación tienen una distribución distinta. Los autores dicen que el profesor da entonces una guía subóptima, e hipotetizan que se debe a que la distribución de los tokens de subpalabra difiere entre los datos originales del profesor y los datos usados para destilar. La explicación es su hipótesis.

</details>

## Prácticas en el mundo real

- [ ] Ejecuta el script de almacenamiento con tu propio tamaño de vocabulario y con k fijado en 64 y en 1,024, y anota las tres razones de costo.
- [ ] Abre la Tabla 11 del paper de Minitron y encuentra la marca de igual cómputo. Anota qué fila usó al profesor y cuántos tokens vio.
- [ ] Mañana: sin apuntes, enuncia los tres números de tokens de Gemma 2 y la aritmética de almacenamiento de un token, y luego di qué deja sin decir el informe sobre el profesor.

## Para profundizar

- [Pérdidas de destilación](../reference/distillation-losses.md)
- [Paper: "Gemma 2: Improving Open Language Models at a Practical Size", Gemma Team, 2024](https://arxiv.org/abs/2408.00118)
- [Paper: "Compact Language Models via Pruning and Knowledge Distillation", Muralidharan et al., 2024](https://arxiv.org/abs/2407.14679)
- [Paper: "LLM Pruning and Distillation in Practice: The Minitron Approach", Sreenivas et al., 2024](https://arxiv.org/abs/2408.11796)
- [Recursos](../RESOURCES.md)

---

¿No termina de quedar claro? Vuelve a leer la fuente primaria de arriba, ya que esta lección la comprime y en la compresión es donde se escapa la comprensión. Consulta el [glosario](../GLOSSARY.md) por si algún término te resultó resbaladizo.

Si lo poco claro es la propia lección y no el material, eso es un defecto: [abre un issue](https://github.com/TokenCemetery/teach/issues).
