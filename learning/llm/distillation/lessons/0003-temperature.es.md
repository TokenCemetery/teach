---
title: "3. Temperatura"
description: "Suavizar ambas distribuciones con una temperatura, la corrección de T al cuadrado y mezclar la pérdida de hard labels"
type: lesson
---

# Lección 3. Temperatura

**Vínculo con la misión:** La misión te pide fijar la temperatura y los pesos de la pérdida de una ejecución de destilación, y esta lección da las tres piezas de ese ajuste: la temperatura, el factor T al cuadrado y el peso de la pérdida de hard labels.
**Fuente principal:** [Paper: "Distilling the Knowledge in a Neural Network", Hinton, Vinyals and Dean, 2015](https://arxiv.org/abs/1503.02531)
**Requisitos previos:** [Lección 2](0002-soft-targets.md), [Temperatura](../GLOSSARY.md), [Pérdida combinada](../GLOSSARY.md), [Logit](../GLOSSARY.md)

## Calentamiento

1. ▢ Con temperatura 1, un estudiante dio a un 2 una probabilidad de 0.98 y a un 3 una de 0.01, y el profesor les dio 1.0 y 10^-6. ¿Por qué el 3 casi no movió la pérdida?

<details markdown="1"><summary>Comprobación</summary>

Cada término de la entropía cruzada es la probabilidad objetivo por el logaritmo de la probabilidad del estudiante. El objetivo de 10^-6 del 3 hace que su término sea más de 4,000 veces menor que el del 2, así que la información que contiene está presente y casi sin oírse.

</details>

2. ▢ ¿Qué dice un hard label sobre la similitud de un 2 con un 7, y dónde está esa información en una destilación?

<details markdown="1"><summary>Comprobación</summary>

No dice nada. La similitud vive en las probabilidades pequeñas que el [profesor](../GLOSSARY.md) pone en las clases incorrectas, los [soft targets](../GLOSSARY.md).

</details>

## Qué debes saber

### La temperatura

El paper reemplaza el softmax por uno que divide cada [logit](../GLOSSARY.md) por una temperatura T antes de normalizar: q_i = exp(z_i / T) / sum_j exp(z_j / T). T normalmente es 1. Una T mayor da una distribución más suave sobre las clases. La receta del paper es subir T hasta que el profesor produzca soft targets adecuadamente suaves, y luego entrenar al estudiante con la misma T alta para igualarlos. Tras el entrenamiento el estudiante usa T = 1.

```python
import numpy as np

def softmax(z, T=1.0):
    z = np.asarray(z, float) / T
    e = np.exp(z - z.max())
    return e / e.sum()

logits = [9.0, 4.0, 2.0, 0.0, -4.0]   # classes: 2, 3, 7, 8, 0
np.set_printoptions(suppress=True, precision=4)
for T in (1, 2, 5, 20):
    print("T =", T, softmax(logits, T))
```

Predice la probabilidad de la primera clase con T = 5 antes de ejecutarlo. La salida con NumPy 2.5:

```text
T = 1 [0.9923 0.0067 0.0009 0.0001 0.    ]
T = 2 [0.889  0.073  0.0268 0.0099 0.0013]
T = 5 [0.5394 0.1984 0.133  0.0892 0.0401]
T = 20 [0.2745 0.2138 0.1934 0.175  0.1433]
```

Con T = 1 las clases incorrectas suman menos del 1%. Con T = 5 llevan casi la mitad de la probabilidad, y el orden 3, 7, 8, 0 sigue siendo visible. Con T = 20 la distribución es casi plana, y las diferencias que el estudiante tiene que igualar son pequeñas.

### Por qué la pérdida se multiplica por T al cuadrado

El gradiente de la entropía cruzada respecto de un logit z_i del estudiante, cuando el profesor tiene logits v_i y ambos usan la temperatura T, es (1/T)(q_i - p_i). La ecuación 2 del paper lo da. Si T es grande comparada con los logits y los logits tienen media cero por ejemplo, el paper muestra que esto es aproximadamente (1/(N T^2))(z_i - v_i), donde N es el número de clases. Así que en el límite de temperatura alta, la destilación equivale a minimizar 1/2 (z_i - v_i)^2, el emparejamiento de logits de Caruana y sus colaboradores. Igualar logits es un caso especial de destilación.

El factor que importa en la práctica es el 1/T^2. El paper dice que las magnitudes de los gradientes de los soft targets escalan como 1/T^2, así que es importante multiplicarlos por T^2 cuando se usan hard y soft targets a la vez. Eso mantiene aproximadamente sin cambios las contribuciones relativas de ambos cuando cambias T mientras experimentas con los demás ajustes.

```python
import numpy as np

def softmax(z, T=1.0):
    z = np.asarray(z, float) / T
    e = np.exp(z - z.max())
    return e / e.sum()

teacher = np.array([9.0, 4.0, 2.0, 0.0, -4.0])
student = np.array([6.0, 5.0, 0.0, 1.0, -2.0])
for T in (1, 2, 5, 10, 20):
    grad = (softmax(student, T) - softmax(teacher, T)) / T
    print(T, "%.4f" % np.abs(grad).max(), "%.4f" % (np.abs(grad).max() * T**2))
```

La salida muestra que la mayor entrada del gradiente se encoge de 0.2663 con T = 1 a 0.0017 con T = 20. Multiplicada por T al cuadrado se mantiene entre 0.64 y 0.84 desde T = 2 hasta T = 20. La fila de T = 1 no es una comparación justa, ya que la aproximación de temperatura alta no se cumple ahí.

### La pérdida combinada

Cuando existen etiquetas correctas para el conjunto de transferencia, el paper encuentra que entrenar solo con los soft targets mejora si además se entrena al estudiante para producir las etiquetas correctas. Probó a modificar los soft targets con las etiquetas y encontró mejor un promedio ponderado de dos objetivos. El primero es la entropía cruzada con los soft targets, calculada con la T alta. El segundo es la entropía cruzada con las etiquetas correctas, calculada a partir de los mismos logits del estudiante con T = 1. El paper encontró que los mejores resultados se daban en general con un peso considerablemente menor en el segundo objetivo.

Escrito con la notación de este track y no la del paper, con lambda el peso del término suave:

```text
loss = lambda * T^2 * CE(teacher at T, student at T) + (1 - lambda) * CE(label, student at 1)
```

Eso es una [pérdida combinada](../GLOSSARY.md). Los experimentos de voz del paper usaron un peso relativo de 0.5 en el término de hard labels, y temperaturas de 1, 2, 5 y 10. La razón del término pequeño de hard labels es práctica: el estudiante normalmente no puede igualar los soft targets exactamente, y el paper dice que errar hacia la respuesta correcta resulta útil.

DistilBERT sigue el mismo patrón. Aplica un softmax con temperatura al profesor y al estudiante durante el entrenamiento, fija T en 1 en inferencia y añade sus propios términos a la pérdida de soft targets como una combinación lineal con la pérdida de modelado de lenguaje enmascarado y una pérdida de coseno entre embeddings.

### Elegir T

El paper da dos observaciones sobre MNIST. Cuando la red destilada tenía 300 o más unidades en cada una de dos capas ocultas, todas las temperaturas por encima de 8 dieron resultados bastante parecidos. Cuando las capas se recortaron a 30 unidades, las temperaturas de 2.5 a 4 funcionaron significativamente mejor que las más altas o más bajas. Los autores sugieren que, cuando el estudiante es demasiado pequeño para capturar todo el conocimiento del profesor, ignorar los logits muy negativos que una temperatura más baja resta importancia puede ayudar.

No traslades una temperatura de un clasificador a un modelo de lenguaje. Los autores de Minitron probaron las temperaturas 0.1, 0.5, 1.0 y 3.0 al reentrenar un LLM podado desde su profesor e informan de los mejores resultados con 1.0 (apéndice A.3). Dan una razón para incluir valores por debajo de 1: las distribuciones de logits de un LLM tienen mayor entropía que las picudas de los modelos de visión, así que esperaban que suavizar importara menos. Un segundo estudio, mayor, coincide. Busbridge et al. (2025) barrieron la temperatura de 0.5 a 10 para estudiantes de 198M a 1.82B de parámetros, cada uno destilado de un profesor de 546M a 7.75B, y encontraron el mejor rendimiento con 1 en todas las escalas (apéndice G.2). Las temperaturas por encima de 3 perjudicaron, y los estudiantes más pequeños sufrieron más. En el apéndice B.3 dicen que, contrariamente a la literatura que citan, la temperatura óptima es uno, e hipotetizan que la diferencia es que el trabajo anterior usaba tokens repetidos mientras que su configuración no repite datos. La hipótesis es suya y el paper no la prueba aquí. Ambos hallazgos son configuraciones de tipo preentrenamiento de un solo laboratorio, así que léelos como una razón sólida para incluir T = 1 en cualquier barrido, no como una prueba de que las temperaturas más altas nunca ayudan.

La ablación de Minitron también es una sola configuración. En su receta final encontraron además que la pérdida de logits sola era mejor que una mezcla ponderada con la pérdida de modelado de lenguaje, lo que recuerda que el peso es un ajuste que hay que probar y no una constante.

## Práctica

1. ▢ Con los logits 9, 4, 2, 0 y -4, ¿aproximadamente qué probabilidad recibe la primera clase con T = 5?

    - a) Unos 0.99
    - b) Unos 0.54
    - c) Unos 0.20
    - d) Unos 0.01

<details markdown="1"><summary>Pista</summary>

Divide los logits entre 5, exponencia cada uno y divide el primero entre la suma de los cinco.

</details>

<details markdown="1"><summary>Comprobación</summary>

**b)** Los logits escalados son 1.8, 0.8, 0.4, 0 y -0.8. Sus exponenciales son aproximadamente 6.05, 2.23, 1.49, 1.00 y 0.45, que suman unos 11.22, y 6.05 / 11.22 es 0.54. La opción (a) es la respuesta con T = 1. La opción (c) es la segunda clase, 0.198 con T = 5, no la primera.

</details>

2. ▢ Subes T de 4 a 8 y no cambias nada más. ¿Por qué el paper multiplica el término suave por T al cuadrado?

    - a) Para cancelar el ajuste de temperatura propio del profesor
    - b) Para asegurar que los soft targets sumen uno
    - c) Para subir la confianza del estudiante en el momento de prueba
    - d) Para mantener en equilibrio los gradientes suaves y duros

<details markdown="1"><summary>Comprobación</summary>

**d)** Los gradientes suaves se encogen como 1/T^2, así que sin el factor el término suave se desvanecería frente al término duro al crecer T. No es (b): el softmax ya normaliza. No es (c): en inferencia el estudiante corre con T = 1 y no se multiplica nada. No es (a): profesor y estudiante comparten la misma T y ninguna se cancela.

</details>

3. ▢ En la pérdida combinada del paper, ¿qué término corre con la temperatura alta, cuál con T = 1 y cuál suele recibir el peso menor?

<details markdown="1"><summary>Comprobación</summary>

La entropía cruzada con los soft targets del profesor corre con la T alta, usando los logits del estudiante divididos entre T. La entropía cruzada con las etiquetas correctas corre sobre los mismos logits con T = 1. El paper encontró los mejores resultados en general con un peso considerablemente menor en el término de hard labels. Los pesos son el ajuste que afinas, así que di cuál usó un resultado.

</details>

4. ▢ Un colega copia el ajuste de MNIST de T = 20 a una destilación de LLM y obtiene un estudiante peor. ¿Qué de esta lección sugiere por qué, y qué debería hacer?

<details markdown="1"><summary>Comprobación</summary>

La ablación de Minitron sobre 0.1, 0.5, 1.0 y 3.0 y el barrido de Busbridge de 0.5 a 10 encontraron los mejores resultados con 1, y los autores de Minitron dicen que las distribuciones de logits de un LLM tienen mayor entropía que las picudas de los modelos de visión. Con T = 20 los objetivos del fragmento de arriba son casi planos, así que las diferencias que el estudiante debe aprender son pequeñas. Debería ejecutar un barrido corto que incluya T = 1 contra su propio profesor y estudiante. Ambos hallazgos vienen de una sola configuración cada uno, así que son un punto de partida, no una regla.

</details>

5. ▢ En los experimentos de MNIST del paper, ¿qué estudiante fue más sensible a la elección de temperatura, el de 300 o más unidades ocultas o el de 30, y qué rango funcionó para el sensible?

<details markdown="1"><summary>Comprobación</summary>

El estudiante de 30 unidades. Las temperaturas de 2.5 a 4 funcionaron significativamente mejor que las más altas o más bajas para él, mientras que con 300 o más unidades todo lo que estaba por encima de 8 dio resultados bastante parecidos. El paper lo interpreta como que ignorar los logits muy negativos ayuda cuando el estudiante es demasiado pequeño para contener todo el conocimiento del profesor.

</details>

## Prácticas en el mundo real

- [ ] Ejecuta ambos scripts. Cambia las temperaturas a 3 y 8 en el segundo y comprueba que la última columna se mantiene en el mismo rango.
- [ ] Escribe la pérdida combinada como una función de NumPy de los logits del estudiante, los logits del profesor, el índice de la etiqueta, T y lambda, y comprueba que con lambda = 0 es igual a la entropía cruzada simple sobre la etiqueta.
- [ ] Mañana: sin apuntes, enuncia la fórmula del softmax con temperatura, di qué términos de la pérdida combinada corren con qué temperatura y di por qué está el factor T al cuadrado.

## Para profundizar

- [Pérdidas de destilación](../reference/distillation-losses.md)
- [Paper: "Distilling the Knowledge in a Neural Network", Hinton, Vinyals and Dean, 2015](https://arxiv.org/abs/1503.02531)
- [Paper: "DistilBERT, a distilled version of BERT: smaller, faster, cheaper and lighter", Sanh et al., 2019](https://arxiv.org/abs/1910.01108)
- [Paper: "Compact Language Models via Pruning and Knowledge Distillation", Muralidharan et al., 2024](https://arxiv.org/abs/2407.14679)
- [Paper: "Distillation Scaling Laws", Busbridge et al., 2025](https://arxiv.org/abs/2502.08606)
- [Recursos](../RESOURCES.md)

---

¿No termina de quedar claro? Vuelve a leer la fuente primaria de arriba, ya que esta lección la comprime y en la compresión es donde se escapa la comprensión. Consulta el [glosario](../GLOSSARY.md) por si algún término te resultó resbaladizo.

Si lo poco claro es la propia lección y no el material, eso es un defecto: [abre un issue](https://github.com/TokenCemetery/teach/issues).
