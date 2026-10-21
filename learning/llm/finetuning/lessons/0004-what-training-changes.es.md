---
title: "4. Qué cambia realmente el entrenamiento"
description: "Las cuatro operaciones de un paso de entrenamiento"
type: lesson
---

# Lección 4. Qué cambia realmente el entrenamiento

**Vínculo con la misión:** Cada argumento de memoria, hiperparámetro y modo de fallo de este espacio de trabajo se deriva de lo que hace un paso de entrenamiento.
**Fuente principal:** [Paper: "Decoupled Weight Decay Regularization" (AdamW), Loshchilov & Hutter, arXiv:1711.05101](https://arxiv.org/abs/1711.05101)
**Requisitos previos:** [Lección 1](0001-what-a-base-model-is.md), [Lección 3](0003-tokenizers-and-chat-templates.md)

## Calentamiento

1. ▢ ¿Por qué el entrenamiento y el serving deben usar exactamente el mismo chat template?

<details markdown="1"><summary>Comprobación</summary>

El template define la distribución de tokens a la que se ajustan los pesos. Entrenar con un renderizado y servir otro significa desplegar un problema distinto, y la pérdida no lo revelará.

</details>

2. ▢ ¿Qué hace una conexión residual alrededor de cada subcapa?

<details markdown="1"><summary>Comprobación</summary>

Suma la salida de la subcapa de vuelta al flujo en curso en lugar de reemplazarlo, de modo que cada bloque aporta un incremento y no una reescritura.

</details>

3. ▢ Nombra las dos proyecciones del MLP que ensanchan y estrechan la dimensión oculta.

<details markdown="1"><summary>Comprobación</summary>

`up_proj` ensancha hasta la dimensión intermedia, `down_proj` vuelve a la dimensión oculta. `gate_proj` produce la compuerta que se aplica entre ambas.

</details>

## Qué debes saber

Un paso de entrenamiento son cuatro operaciones. Cada costo de memoria de la etapa 2 es una de estas cuatro operaciones reteniendo algo en memoria.

**1. Forward pass.** Ejecuta un batch de secuencias a través del modelo y calcula la pérdida. Para hacer posible el paso 3, los resultados intermedios de cada capa, las **activaciones**, deben conservarse en lugar de descartarse. Por eso el entrenamiento necesita mucha más memoria que la inferencia.

**2. Pérdida.** Entropía cruzada entre la distribución predicha y el siguiente token real, promediada sobre cada posición que cuenta. Qué posiciones cuentan es decisión tuya, y importa:

- La **pérdida de secuencia completa** puntúa cada token, incluido el prompt del usuario. El modelo aprende a predecir los prompts además de las respuestas.
- La **pérdida solo de la completion** enmascara los tokens del prompt y puntúa solo la respuesta del asistente.

El enmascarado se hace poniendo la etiqueta en `-100` en las posiciones que se ignoran, una convención que la función de pérdida lee como "saltar". Para el instruction tuning, lo habitual es querer la pérdida solo de la completion: estás enseñando respuestas, no enseñando al modelo a imaginar preguntas de usuario.

**3. Backward pass.** Recorre el grafo hacia atrás aplicando la regla de la cadena y produce, para cada parámetro entrenable, un **gradiente**: la dirección y la magnitud con las que ese parámetro debería cambiar para reducir la pérdida. Un gradiente por parámetro entrenable, con la misma forma que el propio parámetro. Recuérdalo; es la mitad de la lección 6.

**4. Paso del optimizador.** Actualiza los parámetros usando los gradientes. El descenso de gradiente simple sería `w ← w − lr · g`. Nadie usa eso. **AdamW** mantiene dos promedios móviles por parámetro:

| Estado | Registra | Efecto |
|---|---|---|
| Primer momento | Media de los gradientes recientes | Momentum, suaviza las direcciones ruidosas |
| Segundo momento | Media de los gradientes recientes al cuadrado | Escalado del paso por parámetro |

Dos tensores extra, cada uno del tamaño de los parámetros. Esa es la otra mitad de la lección 6, y es la razón por la que el full fine-tuning es tan caro.

### Learning rate y schedule

El learning rate escala el paso. Si es demasiado alto, la actualización se pasa de largo y destruye la estructura preentrenada. Eso es lo que parece mecánicamente el olvido catastrófico. Si es demasiado bajo, nada se mueve.

Dos refinamientos estándar:

- **Warm-up:** empezar cerca de cero y subir durante los primeros cientos de pasos, para que los gradientes ruidosos del principio no arruinen los pesos.
- **Decay:** reducir el learning rate durante el entrenamiento, normalmente con una curva de coseno, para que los pasos finales refinen en lugar de sacudir.

El fine-tuning con adapters tolera learning rates de uno a dos órdenes de magnitud más altos que el full fine-tuning, normalmente alrededor de `1e-4` a `2e-4` en lugar de `1e-5`. La lección 9 explica por qué.

### Batch size, real y efectivo

Los gradientes se promedian sobre un batch. Los batches más grandes dan gradientes menos ruidosos, pero cuestan proporcionalmente más memoria de activaciones. La **gradient accumulation** compra el promediado sin la memoria: ejecuta varios batches pequeños, suma los gradientes y da un solo paso.

```text
effective batch size = per_device_batch_size × gradient_accumulation_steps × num_devices
```

Reporta y razona con el número efectivo. Una ejecución con batch size 1 y 16 pasos de acumulación es una ejecución de batch 16, y compararla con una de batch 1 como si fueran equivalentes es una forma común de sacar una conclusión falsa.

### Un epoch no es una unidad de aprendizaje

Un epoch es una pasada sobre el dataset. En un dataset de instrucciones pequeño, de dos a tres epochs es un rango típico y más que eso suele memorizar. El número de *pasos* es lo que ve el optimizador, y los pasos dependen del tamaño del dataset y del batch size efectivo a la vez, así que "3 epochs" significa algo completamente distinto con 500 ejemplos que con 500,000.

## Práctica

1. ▢ ¿Por qué el entrenamiento necesita mucha más memoria que la inferencia, incluso con el mismo batch size y la misma longitud de secuencia?

<details markdown="1"><summary>Comprobación</summary>

El entrenamiento debe conservar las activaciones del forward pass para que el backward pass pueda calcular los gradientes, y debe almacenar los gradientes y el estado del optimizador. La inferencia descarta los intermedios de cada capa en cuanto la siguiente capa los ha consumido.

</details>

2. ▢ Estás haciendo fine-tuning con pares de pregunta y respuesta. ¿La pérdida debe calcularse sobre toda la secuencia o solo sobre la respuesta? Da la consecuencia de elegir mal.

<details markdown="1"><summary>Comprobación</summary>

Solo sobre la respuesta, en la mayoría de los casos. Puntuar también el prompt gasta capacidad en enseñar al modelo a generar preguntas de usuario plausibles, que no es la tarea, y diluye la señal del gradiente sobre la parte que te importa.

La excepción es cuando los prompts están muy estilizados y quieres que el modelo interiorice de forma general el lenguaje del dominio. Decídelo con intención; no dejes que lo decida el valor por defecto.

</details>

3. ▢ ¿Cuántos tensores extra por parámetro entrenable almacena AdamW, y cuáles son?

<details markdown="1"><summary>Comprobación</summary>

Dos: una media móvil de los gradientes (primer momento) y una media móvil de los gradientes al cuadrado (segundo momento). Cada uno tiene la misma forma que el parámetro.

Más el propio gradiente, que es un tercer tensor de la misma forma pero no es estado del optimizador. Mantener bien separadas esas tres cosas es exactamente lo que te pide la lección 6.

</details>

4. ▢ Ejecución A: batch size 8, acumulación 1. Ejecución B: batch size 1, acumulación 8. Mismos datos, misma seed, mismo learning rate. ¿Son equivalentes los pasos del optimizador?

<details markdown="1"><summary>Comprobación</summary>

En la práctica sí: ambas promedian los gradientes sobre 8 ejemplos antes de dar el paso, así que la actualización es esencialmente la misma, y B usa mucha menos memoria de activaciones. Quedan pequeñas diferencias por cómo interactúan el padding y la normalización por batch.

La gradient accumulation es la forma estándar de conseguir un batch efectivo grande con memoria limitada. Lo que *no* es equivalente es comparar B con una ejecución genuina de batch 1, que da ocho veces más pasos sobre gradientes más ruidosos.

</details>

5. ▢ Un colega fija el learning rate de una ejecución de LoRA en `1e-5` "porque eso es lo que usa el full fine-tuning". ¿Qué esperas y qué le dices?

<details markdown="1"><summary>Comprobación</summary>

Espera subajuste: la pérdida baja despacio, el modelo apenas cambia y la ejecución parece una prueba de que el método no funciona.

Los adapters parten de una contribución cero y contienen una fracción minúscula de los parámetros, así que necesitan un learning rate mucho mayor para moverse siquiera, normalmente de `1e-4` a `2e-4`. Importar el learning rate del full fine-tuning es una de las razones más comunes por las que decepciona una primera ejecución de LoRA.

</details>

6. ▢ ¿Por qué el warm-up es más que una superstición?

<details markdown="1"><summary>Comprobación</summary>

Al principio del entrenamiento, la estimación del segundo momento de AdamW se construye con muy pocas muestras, así que su escalado por parámetro no es fiable y puede producir pasos enormes. Subir el learning rate gradualmente limita el daño que esos primeros pasos pueden hacer a los pesos preentrenados.

</details>

## Prácticas en el mundo real

- [ ] Escribe de memoria las cuatro operaciones de un paso de entrenamiento y luego contrástalas con esta lección.
- [ ] Toma cualquier script de fine-tuning publicado e identifica su batch size efectivo, learning rate, warm-up y schedule. Anota los cuatro números.
- [ ] Mañana: encuentra una configuración de entrenamiento donde no estés de acuerdo con uno de esos cuatro números, y escribe una frase sobre qué cambiarías y por qué.

## Para profundizar

- [Paper: "Decoupled Weight Decay Regularization" (AdamW), Loshchilov & Hutter, arXiv:1711.05101](https://arxiv.org/abs/1711.05101)
- [Paper: "Adam: A Method for Stochastic Optimization", Kingma & Ba, arXiv:1412.6980](https://arxiv.org/abs/1412.6980)
- [Blog: "A Recipe for Training Neural Networks", Andrej Karpathy](https://karpathy.github.io/2019/04/25/recipe/)
- [Presupuesto de memoria](../reference/memory-budget.md): la etapa 2 convierte estos cuatro pasos en bytes

---

¿No termina de quedar claro? Vuelve a leer la fuente primaria de arriba, ya que esta lección la comprime y en la compresión es donde se escapa la comprensión. Consulta el [glosario](../GLOSSARY.md) por si algún término te resultó resbaladizo.

Si lo poco claro es la propia lección y no el material, eso es un defecto: [abre un issue](https://github.com/TokenCemetery/teach/issues).
