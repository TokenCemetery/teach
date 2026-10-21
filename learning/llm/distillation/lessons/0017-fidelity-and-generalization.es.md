---
title: "17. Fidelidad y generalización"
description: "Por qué un estudiante que generaliza bien puede seguir discrepando de su profesor, y cuál de las dos necesitas"
type: lesson
---

# Lección 17. Fidelidad y generalización

**Vínculo con la misión:** La misión te pide predecir qué heredará un estudiante, y medir qué perdió, lo que empieza por separar cuán de cerca copia al profesor de lo bien que hace la tarea.
**Fuente principal:** [Paper: "Does Knowledge Distillation Really Work?", Stanton et al., 2021](https://arxiv.org/abs/2106.05945), secciones 3 a 7
**Requisitos previos:** [Lección 3](0003-temperature.md), [Lección 16](0016-on-policy-distillation-in-practice.md), [Fidelidad](../GLOSSARY.md), [KL directa](../GLOSSARY.md), [Pérdida combinada](../GLOSSARY.md)

## Calentamiento

1. ▢ La pérdida combinada suma dos términos. ¿Cuál empuja al estudiante hacia el profesor y cuál hacia las etiquetas?

<details markdown="1"><summary>Comprobación</summary>

La divergencia respecto de los [soft targets](../GLOSSARY.md) del profesor lo empuja hacia el profesor, y la entropía cruzada frente a los [hard labels](../GLOSSARY.md) lo empuja hacia los datos. Un coeficiente de mezcla los pondera.

</details>

2. ▢ La fase on-policy de Qwen3 minimiza la KL entre estudiante y profesor sobre las propias muestras del estudiante. ¿Qué dirección de la KL es la forma profesor a estudiante, y qué penaliza?

<details markdown="1"><summary>Comprobación</summary>

KL(profesor || estudiante) es la KL directa. Penaliza al estudiante por poner poca probabilidad donde el profesor pone mucha, así que empuja al estudiante a cubrir todo lo que cubre el profesor.

</details>

3. ▢ En la lección 16, el estudiante de Qwen3 superó en benchmarks al checkpoint entrenado con RL. ¿Te dice eso que las predicciones del estudiante coinciden con las de su profesor?

<details markdown="1"><summary>Comprobación</summary>

No. Las puntuaciones de benchmarks miden la tarea. Si el estudiante coincide con las predicciones de su profesor es una medición aparte, y esta lección trata de por qué ambas pueden separarse.

</details>

## Qué debes saber

### Dos cosas que la destilación podría significar que mejoró

Stanton et al. separan dos cantidades que la literatura de destilación suele confundir. La **fidelidad** es la capacidad de un estudiante para igualar las predicciones del profesor. La **generalización** es el rendimiento del estudiante sobre datos no vistos de la misma distribución. Miden la fidelidad con dos números sobre las mismas entradas, ambos definidos en la sección 3.2:

| Métrica | Qué mide |
|---|---|
| Acuerdo top-1 promedio | La fracción de entradas en las que estudiante y profesor eligen la misma etiqueta principal |
| KL predictiva promedio | La KL(profesor \|\| estudiante) media, sensible a cada clase, no solo a la principal |

La precisión no puede sustituir al acuerdo. El ejemplo del propio paper: tres modelos independientes con 55%, 75% y 95% de precisión en prueba. El primero y el tercero pueden coincidir como máximo en el 60% de las entradas, mientras que el segundo y el tercero coinciden al menos en el 70%, y aun así nadie diría que el modelo del 75% es una mejor destilación del modelo del 95%, ya que se entrenaron de forma independiente.

### El control para "coinciden porque ambos son buenos"

El acuerdo sube solo porque los modelos son precisos. Para separar una mejora general de una mejora específica en la coincidencia, el paper entrena además un segundo estudiante, destilado con el procedimiento idéntico a partir de un profesor independiente. Si ambos estudiantes coinciden con el primer profesor más o menos por igual, el acuerdo se explica por la generalización. Si el estudiante real coincide más con su propio profesor, eso es fidelidad.

### Lo que encontraron

Sus experimentos son sobre todo de clasificación de imágenes con ResNets en CIFAR-100, más MNIST, ImageNet y un dataset de clasificación de texto (sentimiento de IMDB) en el apéndice. No son experimentos sobre generación con modelos de lenguaje, así que léelos como un resultado sobre la destilación en general y luego pruébalo en tu propio par de LLM.

| Hallazgo | Evidencia en el paper |
|---|---|
| Caso fácil: la coincidencia funciona | LeNet-5 en MNIST alcanzó más del 99% de acuerdo top-1 en prueba con suficientes datos de destilación (sección 4.1) |
| Caso más difícil: a menudo no | La autodestilación de ResNet-56 en CIFAR-100 se quedó por debajo del 80% de acuerdo en prueba incluso con el mayor conjunto de destilación (sección 6.1) |
| Una mejor generalización puede venir con peor fidelidad | En la autodestilación, ampliar los datos con muestras de GAN subió la fidelidad y bajó la precisión en prueba, porque un estudiante que no logra igualar al profesor puede generalizar mejor (Figura 1a, sección 4.2) |
| Con un profesor más fuerte ambas se alinean | Al destilar un ensemble de 3 componentes, la fidelidad y la precisión en prueba subieron ambas con más datos (Figura 1b) |
| No es la capacidad | La baja fidelidad aparece incluso en la autodestilación, donde el estudiante tiene la propia capacidad del profesor, y agrandar el estudiante apenas la cambió al destilar un ensemble (sección 4.4) |
| No es una arquitectura, escala o dominio | Resultados similares con VGG, en ImageNet y en IMDB (sección 4.4) |

### La explicación: la optimización

El paper prueba dos hipótesis para el fallo. Una es la identificabilidad: los datos de destilación son demasiado pocos para fijar la función del profesor. Más datos ayudan al acuerdo en prueba, así que esto es parte de la historia. La otra es la optimización: el estudiante ni siquiera puede igualar al profesor sobre los datos de destilación con que entrena.

La segunda se sostiene. Con 50k imágenes sintéticas añadidas, un estudiante con la misma capacidad que su profesor alcanzó solo un 95% de acuerdo sobre los propios datos de destilación. Con aumentación de datos intensa, el acuerdo en entrenamiento estuvo entre el 80% y el 90% para tres aumentaciones y cayó a cerca del 60% en la autodestilación para la combinación de las tres (sección 6.1). Entrenar más tiempo ayudó un poco: para una autodestilación de ResNet-20, 5,000 épocas de SGD alcanzaron un 83.3% de acuerdo en entrenamiento frente al 78.95% con 300 épocas, y cambiar a Adam redujo la fidelidad (sección 6.2).

El resumen del paper es un compromiso. Añadir ejemplos más allá de los datos de entrenamiento del profesor da al estudiante más etiquetas del profesor para identificar la función, y también hace más difícil un problema de optimización que ya era difícil. En palabras del paper, la buena fidelidad está directamente alineada con resolver un problema de optimización excepcionalmente difícil, donde el entrenamiento ordinario se salva por no necesitar resolverlo bien.

### Qué cambia esto para ti

Si evalúas un LLM destilado solo por la precisión en la tarea, no puedes saber cuánto del profesor heredaste. Dos estudiantes pueden puntuar igual y diferir mucho en acuerdo. La etapa 8 construye la medición completa, y el hábito mínimo es este: informa del acuerdo con el profesor sobre entradas held-out junto a la calidad en la tarea, y compara con un estudiante destilado de un profesor distinto o entrenado sin uno.

La fidelidad no siempre es el objetivo. El propio resultado de autodestilación del paper muestra un estudiante que no logra igualar a su profesor y aun así generaliza mejor. La fidelidad importa cuando quieres heredar propiedades más allá de la precisión: el paper enumera transferir la calibración o la robustez para que un modelo más pequeño pueda reemplazar con seguridad a uno mayor (sección 4.3). También encontró que el estudiante de mayor fidelidad era siempre el mejor calibrado al destilar ensembles.

Un esbozo en Python puro de las dos mediciones, que imprime la salida mostrada en los comentarios:

```python
import math

def softmax(z):
    m = max(z)
    e = [math.exp(v - m) for v in z]
    s = sum(e)
    return [v / s for v in e]

def argmax(z):
    return max(range(len(z)), key=lambda i: z[i])

def kl(p, q):
    return sum(pi * (math.log(pi) - math.log(qi)) for pi, qi in zip(p, q))

# One row per example: logits over three classes, plus the true label.
teacher = [[3.0, 1.0, 0.0], [0.5, 2.5, 0.0], [0.0, 0.5, 3.0], [1.0, 2.0, 0.0]]
student = [[2.0, 1.5, 0.0], [0.0, 1.0, 2.0], [0.0, 0.5, 2.5], [2.0, 1.5, 0.0]]
labels = [0, 1, 2, 0]

agreement = sum(argmax(t) == argmax(s) for t, s in zip(teacher, student)) / len(labels)
mean_kl = sum(kl(softmax(t), softmax(s)) for t, s in zip(teacher, student)) / len(labels)
teacher_acc = sum(argmax(t) == y for t, y in zip(teacher, labels)) / len(labels)
student_acc = sum(argmax(s) == y for s, y in zip(student, labels)) / len(labels)

print(f"agreement {agreement:.2f}  mean KL {mean_kl:.3f}")      # agreement 0.50  mean KL 0.321
print(f"teacher accuracy {teacher_acc:.2f}  student accuracy {student_acc:.2f}")  # both 0.75
```

Ambos modelos puntúan 0.75, y coinciden solo en la mitad de las entradas.

## Práctica

1. ▢ Un profesor tiene un 93% de precisión y un estudiante un 91%, en el mismo conjunto de prueba. ¿Entre qué límites debe estar su acuerdo top-1?

<details markdown="1"><summary>Pista</summary>

El estudiante se equivoca en el 9% de las entradas y el profesor en el 7%. ¿Cuánto pueden solaparse los dos conjuntos de errores, y cuán poco?

</details>

<details markdown="1"><summary>Comprobación</summary>

Entre el 84% y el 98%. Coinciden donde ambos aciertan, y el peor caso es que sus errores nunca se solapen, lo que deja 100 menos 7 menos 9, es decir al menos el 84%. Pueden coincidir como máximo en el 98%: el estudiante se equivoca en 2 puntos porcentuales más de entradas que el profesor, así que al menos el 2% de las entradas tienen al profesor acertando y al estudiante equivocado. Igualar la precisión dice muy poco sobre el acuerdo, que es la idea de la lección.

</details>

2. ▢ En el control del paper, ¿por qué entrenar un segundo estudiante a partir de un profesor independiente?

    - a) Verifica que el profesor se entrenó correctamente
    - b) Separa la fidelidad de la habilidad compartida
    - c) Sube la precisión del primer estudiante
    - d) Reduce el cómputo necesario en total

<details markdown="1"><summary>Comprobación</summary>

**b)** Si un estudiante coincide con un profesor independiente más o menos tanto como con el suyo, el acuerdo se explica porque ambos son buenos, no por copiar. (a) no se prueba aquí. (c) y (d) son falsas: el segundo estudiante es una herramienta de medición y no cambia nada del primero.

</details>

3. ▢ En la autodestilación de CIFAR-100 con un estudiante y un profesor ResNet-56, el conjunto de destilación se amplía con imágenes generadas por GAN. Predice la dirección de la fidelidad del estudiante y de su precisión en prueba.

<details markdown="1"><summary>Pista</summary>

La autodestilación es el caso en que el estudiante ya tiene la capacidad de igualar al profesor, y el paper señala que no lograr igualarlo puede ayudar por sí mismo.

</details>

<details markdown="1"><summary>Comprobación</summary>

La fidelidad aumenta y la precisión en prueba disminuye (Figura 1a). En la autodestilación el estudiante que iguala menos de cerca al profesor generaliza mejor, así que más fidelidad cuesta precisión. Con un profesor ensemble de 3 la dirección se invierte: ambas suben (Figura 1b). Cuál se aplica a ti depende de si tu profesor generaliza mucho mejor que un estudiante entrenado de forma independiente.

</details>

4. ▢ Un estudiante destilado con la propia arquitectura del profesor sigue discrepando de él en el 20% de las entradas held-out. Enumera las hipótesis que prueba el paper y di cuál respalda.

<details markdown="1"><summary>Comprobación</summary>

Capacidad del estudiante, arquitectura, escala del dataset, dominio de los datos, identificabilidad y optimización (sección 4.4). El paper descarta la capacidad, ya que el estudiante tiene la capacidad del profesor, y las demás según su evidencia. Respalda la optimización como razón clave: el estudiante no iguala al profesor ni siquiera sobre sus propias entradas de entrenamiento. La identificabilidad también forma parte del cuadro, ya que más datos subieron el acuerdo en prueba. El paper encontró la gran brecha de acuerdo en tareas de imagen, así que compruébalo en tu par de LLM antes de asumir que se traslada.

</details>

5. ▢ ¿Cuál de estas mediciones de LLM es el análogo más cercano de la KL predictiva promedio del paper, y qué necesita que el acuerdo no necesita?

<details markdown="1"><summary>Comprobación</summary>

La KL(profesor || estudiante) media por posición sobre secuencias held-out, que es la pérdida de destilación a nivel de token con KL directa de la etapa 2 evaluada sobre datos no usados para entrenar. Necesita la distribución completa del profesor en cada posición, que el acuerdo sobre el token principal no necesita. El acuerdo sobre el token principal es el análogo más barato del acuerdo top-1. Esta correspondencia desde la configuración de clasificación del paper al nivel de token es una adaptación mía, no un experimento del paper.

</details>

## Prácticas en el mundo real

- [ ] Ejecuta el esbozo de arriba, y luego cambia una fila de logits del estudiante para que los dos modelos discrepen en otro ejemplo mientras la precisión se mantiene en 0.75. Anota qué pasó con el acuerdo y con la KL media.
- [ ] Lee la sección 3.2 del paper de Stanton y escribe la fórmula del acuerdo top-1 promedio en una línea. Luego escribe qué te dice el estudiante de control s-prime.
- [ ] Mañana: sin apuntes, enuncia la diferencia entre fidelidad y generalización, un caso en que más fidelidad baja la precisión y la explicación principal del paper para la baja fidelidad.

## Para profundizar

- [Lo que hereda el estudiante](../reference/what-the-student-inherits.md)
- [Paper: "Does Knowledge Distillation Really Work?", Stanton et al., 2021](https://arxiv.org/abs/2106.05945)
- [Recursos](../RESOURCES.md)

---

¿No termina de quedar claro? Vuelve a leer la fuente primaria de arriba, ya que esta lección la comprime y en la compresión es donde se escapa la comprensión. Consulta el [glosario](../GLOSSARY.md) por si algún término te resultó resbaladizo.

Si lo poco claro es la propia lección y no el material, eso es un defecto: [abre un issue](https://github.com/TokenCemetery/teach/issues).
