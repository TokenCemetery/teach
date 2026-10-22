---
title: "12. Leer una ejecución de entrenamiento"
description: "Diagnosticar por la forma de la curva, y lo que la pérdida no puede ver"
type: lesson
---

# Lección 12. Leer una ejecución de entrenamiento

**Vínculo con la misión:** "Diagnosticar una ejecución fallida y nombrar la causa" está en la lista de éxito. La mayoría de la gente lee una curva de pérdida y adivina.
**Fuente principal:** [Blog: "A Recipe for Training Neural Networks", Andrej Karpathy](https://karpathy.github.io/2019/04/25/recipe/)
**Requisitos previos:** [Lección 11](0011-your-first-adapter.md)

## Calentamiento

1. ▢ Nombra las cuatro comprobaciones que hay que ejecutar antes de preocuparse por la curva de pérdida.

<details markdown="1"><summary>Comprobación</summary>

Confirmar que el adapter se acopló; decodificar un ejemplo de entrenamiento real y contar las posiciones puntuadas; confirmar que la pérdida se mueve; confirmar que el pipeline puede sobreajustar dos ejemplos.

</details>

2. ▢ ¿Por qué registrar la revisión del base model junto al adapter?

<details markdown="1"><summary>Comprobación</summary>

Un adapter es un diff contra unos pesos concretos. Sin el base exacto es inutilizable, y un base casi igual degrada la calidad en silencio.

</details>

3. ▢ ¿Bytes por parámetro congelado frente a por parámetro entrenable?

<details markdown="1"><summary>Comprobación</summary>

Dos frente a dieciséis.

</details>

## Qué debes saber

### La pérdida de entrenamiento por sí sola no te dice casi nada

Que la pérdida de entrenamiento caiga significa que el modelo se está ajustando a los datos que puede ver. Eso es compatible tanto con un modelo que está aprendiendo la tarea como con uno que está memorizando el conjunto de entrenamiento. **Necesitas una partición held-out para distinguirlos, y no hay sustituto.**

Aparta una antes de empezar:

```python
split = dataset.train_test_split(test_size=0.05, seed=0)
args = SFTConfig(..., eval_strategy="steps", eval_steps=50)
trainer = SFTTrainer(..., train_dataset=split["train"], eval_dataset=split["test"])
```

### Las formas y lo que significan

| Pérdida de entrenamiento | Pérdida held-out | Diagnóstico | Acción |
|---|---|---|---|
| Cae | Cae | Aprendiendo | Continuar |
| Cae | Se aplana y luego sube | Sobreajuste desde el punto de giro | Parar en el mínimo; más datos o menos capacidad |
| Cae a ~0 rápido | Sube de inmediato | Memorizando | Dataset demasiado pequeño para esta capacidad |
| Se aplana alta | Se aplana alta | Subajuste | Más rank, más target modules, learning rate más alto |
| Plana desde el paso 1 | Plana | Pipeline roto | Las cuatro comprobaciones de la lección 11 |
| Picos, o `NaN` | irrelevante | Inestabilidad | Bajar el learning rate; comprobar el desbordamiento en fp16; añadir warm-up |

El **mínimo held-out** es el checkpoint útil, no el último paso. Guarda checkpoints periódicamente y conserva el mejor; una ejecución que termina en el paso 1000 cuando la pérdida held-out tocó fondo en el paso 400 ha entrenado 600 pasos de daño.

### Diagnosticar por la forma, con más cuidado

**Un suelo de pérdida que más entrenamiento no bajará** es un techo de capacidad. El adapter no puede expresar la actualización que necesita la tarea. Añadir epochs no lo arregla; añadir rank o target modules sí.

**Una pérdida que da un pico y se recupera** suele ser un batch que contiene algo inusual: un ejemplo de longitud atípica, texto corrupto, un bloque duplicado. Encuéntralo. Un solo ejemplo patológico puede mover una ejecución con un dataset pequeño.

**Una pérdida que se vuelve `NaN`** es un desbordamiento. En fp16 es común y es lo que el loss scaling existe para prevenir; en bf16 suele indicar algo peor, como una división por cero en el pipeline de datos o un learning rate lo bastante alto como para mandar los pesos al infinito.

**Una pérdida que cae en una escalera limpia** con escalones en las fronteras de los epochs significa que el modelo está reconociendo ejemplos que ya ha visto. Es la memorización apareciendo directamente en la curva.

### Lo que la pérdida no puede ver en absoluto

Esta es la parte importante de la lección.

La entropía cruzada puntúa la predicción del siguiente token sobre la distribución de tus datos. Calla sobre:

- **Si las generaciones son utilizables.** Un modelo puede puntuar bien y producir una salida que nunca se detiene, o que ignora el formato pedido.
- **Si se ha roto algo más.** El [olvido catastrófico](../GLOSSARY.md), la degradación de capacidades no relacionadas con tu tarea, no aparece en absoluto en la pérdida de tu tarea. Tu pérdida held-out puede mejorar de forma monótona mientras el modelo empeora en todo lo demás que sabía hacer.
- **Si la mejora es real o es contaminación.** Si tus ejemplos held-out son casi duplicados de ejemplos de entrenamiento, la pérdida held-out está midiendo memorización y llamándola generalización.

Así que: **genera, siempre.** Fija un conjunto pequeño de prompts antes de entrenar. Pásalos por el base model y guarda las salidas. Pásalos por el modelo adaptado con los mismos ajustes de muestreo y compara. Diez minutos leyendo generaciones reales atrapan cosas que ninguna métrica de tu curva atrapará.

```python
PROBES = [
    "<a representative task prompt>",
    "<an edge case you care about>",
    "<something unrelated to the task, to check for forgetting>",
]
```

Esa tercera categoría es la que la gente deja fuera, y así es como se despliega el olvido.

### Reproducibilidad

Registra lo bastante como para poder volver a ejecutarlo: base model y revisión, dataset y su partición exacta, seed, cada hiperparámetro y las versiones de las bibliotecas. El fine-tuning con adapters tiene una superficie de configuración lo bastante grande como para que "creo que era rank 32" no sea un registro.

Comparar dos ejecuciones solo tiene sentido cuando exactamente una cosa difiere entre ellas. Cambia el rank *o* el learning rate, no ambos, y mantén fijos la seed y los datos. Suena obvio y se viola de forma rutinaria, normalmente porque una ejecución tardó lo bastante como para volver cara la paciencia.

## Práctica

1. ▢ La pérdida de entrenamiento es 0.2 y sigue cayendo. La pérdida held-out tocó fondo en 0.9 hace doscientos pasos y ahora es 1.1. ¿Qué está pasando, y qué checkpoint despliegas?

<details markdown="1"><summary>Comprobación</summary>

Sobreajuste. El modelo se está ajustando ahora a ruido específico del conjunto de entrenamiento.

Despliega el checkpoint del mínimo held-out, unos doscientos pasos atrás. Luego reduce la capacidad, añade datos o para antes la próxima vez.

</details>

2. ▢ Ambas pérdidas se aplanan en un nivel demasiado alto para ser útil. Rank 8, targets solo de atención. ¿Qué cambias y qué no?

<details markdown="1"><summary>Comprobación</summary>

Cambia la capacidad: amplía los targets a todas las capas lineales y sube el rank. Considera si el learning rate es demasiado bajo.

No añadas epochs. Un techo de capacidad no se mueve con más pasadas sobre los mismos datos. Esa es la definición del diagnóstico.

</details>

3. ▢ La pérdida held-out mejora todo el tiempo. Despliegas. Los usuarios reportan que el modelo ha empeorado en cosas que antes hacía. ¿Qué dejaste de medir?

<details markdown="1"><summary>Comprobación</summary>

El olvido catastrófico. Tu conjunto held-out sale de la distribución de tu tarea, así que no puede ver la degradación en capacidades fuera de esa distribución.

La solución es un conjunto de regresión que cubra las capacidades que no estás entrenando: seguimiento general de instrucciones, comportamiento de rechazo, otros formatos. Esa es la lección 24, y este fallo es la razón por la que existe.

</details>

4. ▢ ¿Qué observación indica con más fuerza un pipeline roto y no malos hiperparámetros?

    - a) La curva de pérdida se estanca en un valor muy por encima de cero
    - b) La pérdida no cambia exactamente nada a lo largo de los cincuenta pasos
    - c) La pérdida held-out sube mientras la de entrenamiento cae
    - d) La pérdida da un pico hacia arriba en un paso y luego se recupera

<details markdown="1"><summary>Comprobación</summary>

**b)** La pérdida no cambia exactamente nada a lo largo de los cincuenta pasos.

Una meseta es subajuste, un par divergente es sobreajuste y un pico suele ser un mal batch, que son todos comportamientos reales del entrenamiento. Una pérdida que no se mueve *en absoluto* significa que ningún gradiente llega a ningún parámetro, que es un fallo de conexión.

</details>

5. ▢ ¿Por qué al menos uno de tus probes de generación debe ser ajeno a la tarea?

<details markdown="1"><summary>Comprobación</summary>

Porque es la única forma barata de notar el olvido durante una ejecución. Los probes relacionados con la tarea y la pérdida held-out relacionada con la tarea mejoran ambos mientras las capacidades ajenas decaen, así que nada de lo que ya estás midiendo te avisará.

</details>

6. ▢ La pérdida cae en escalera, con caídas en cada frontera de epoch. Diagnostica.

<details markdown="1"><summary>Comprobación</summary>

El modelo está reconociendo ejemplos que ya ha visto. Eso es memorización, visible directamente en la curva. Cada epoch nuevo produce un escalón hacia abajo porque los datos ya no son novedosos.

Comprueba la pérdida held-out, que probablemente esté plana o subiendo, y reduce los epochs o la capacidad.

</details>

## Prácticas en el mundo real

- [ ] Añade una partición held-out y una evaluación periódica a tu ejecución de la lección 11. Encuentra el mínimo held-out.
- [ ] Escribe tres probes de generación, uno de ellos ajeno a tu tarea. Guarda las salidas del base model antes de entrenar.
- [ ] Sobreajusta a propósito: entrena un adapter con rank generoso con 50 ejemplos durante muchos epochs y observa cómo se separan las dos curvas. Guarda la gráfica.
- [ ] Mañana: escribe un registro de una página de una ejecución real: base model, revisión, datos, partición, seed, cada hiperparámetro, versiones de las bibliotecas.

## Para profundizar

- [Blog: "A Recipe for Training Neural Networks", Andrej Karpathy](https://karpathy.github.io/2019/04/25/recipe/)
- [Modos de fallo](../reference/failure-modes.md)
- [Lección 24. El conjunto de regresión](0024-the-regression-suite.md): donde el probe ajeno se convierte en un sistema real

---

¿No termina de quedar claro? Vuelve a leer la fuente primaria de arriba, ya que esta lección la comprime y en la compresión es donde se escapa la comprensión. Consulta el [glosario](../GLOSSARY.md) por si algún término te resultó resbaladizo.

Si lo poco claro es la propia lección y no el material, eso es un defecto: [abre un issue](https://github.com/TokenCemetery/teach/issues).
