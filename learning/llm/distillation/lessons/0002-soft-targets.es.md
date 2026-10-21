---
title: "2. Soft targets"
description: "Qué llevan las probabilidades que un profesor da a las respuestas incorrectas, y por qué son una señal de entrenamiento más rica que un hard label"
type: lesson
---

# Lección 2. Soft targets

**Vínculo con la misión:** La misión te pide explicar por qué los soft targets de un profesor llevan más señal de entrenamiento que los hard labels, y esta lección es esa explicación, con una ejecución contra la que puedes comprobarla.
**Fuente principal:** [Paper: "Distilling the Knowledge in a Neural Network", Hinton, Vinyals and Dean, 2015](https://arxiv.org/abs/1503.02531)
**Requisitos previos:** [Lección 1](0001-what-distillation-buys.md), [Soft targets](../GLOSSARY.md), [Hard label](../GLOSSARY.md), [Logit](../GLOSSARY.md)

## Calentamiento

1. ▢ En una destilación, ¿los pesos de qué modelo cambian durante el entrenamiento, y qué modelo es la señal de entrenamiento?

<details markdown="1"><summary>Comprobación</summary>

Solo aprende el [estudiante](../GLOSSARY.md). El [profesor](../GLOSSARY.md) está fijo y aporta los objetivos. Confundirlos es el primer error habitual al leer una pérdida de destilación.

</details>

2. ▢ La red de 800 unidades de MNIST cometió 146 errores sola y 74 cuando además igualó las salidas de la red de 1200 unidades. ¿Qué mostraron los 74 sobre lo que llevaban los objetivos?

<details markdown="1"><summary>Comprobación</summary>

Los objetivos llevaban conocimiento sobre cómo generalizar, aprendido por el profesor a partir de datos de entrenamiento con jitter, que el estudiante nunca vio en su propio conjunto de transferencia. Un hard label por imagen no contiene nada de eso.

</details>

## Qué debes saber

### Lo que tira un hard label

Un clasificador entrenado da a la mayoría de las imágenes una probabilidad cercana a 1 para la clase correcta. Las probabilidades diminutas sobre las clases incorrectas siguen siendo distintas de una imagen a otra. Hinton et al. dan un ejemplo de MNIST: una versión de un 2 puede recibir una probabilidad de 10^-6 de ser un 3 y de 10^-9 de ser un 7, y otra versión de un 2 puede recibirla al revés. Eso dice qué 2 se parecen a los 3 y cuáles a los 7, una estructura de similitud sobre los datos. Un [hard label](../GLOSSARY.md) solo dice "2" en ambos casos.

El término del paper para el objetivo de entrenamiento construido con estas probabilidades es soft targets. A la información que llevan a veces se la llama dark knowledge, un nombre que no aparece en este paper. Este track dice [soft targets](../GLOSSARY.md) para el objetivo y evita la otra expresión.

### El problema: los números pequeños casi no mueven la pérdida

El mismo pasaje nombra el problema. Probabilidades tan cercanas a cero tienen muy poca influencia sobre el costo de entropía cruzada durante la transferencia. Toma un estudiante que da al 2 una probabilidad de 0.98 y al 3 una de 0.01, frente a un profesor con 1.0 y 10^-6. El 2 aporta unos 0.0202 a la pérdida y el 3 unos 0.0000046, que es más de 4,000 veces menos. La señal está ahí y la pérdida es sorda a ella.

Caruana y sus colaboradores, dice el paper, evitaron esto igualando logits con un error cuadrático en lugar de igualar probabilidades. La respuesta más general de Hinton et al. es subir la temperatura hasta que los objetivos sean lo bastante suaves para importar, que es la lección 3.

### Míralo ejecutarse

El script construye un profesor sobre cinco clases de dígitos y luego dos estudiantes. Ambos predicen "2" con la misma confianza. El estudiante A intercambia el orden del 3 y el 7 respecto del profesor, y el estudiante B conserva el orden del profesor.

```python
import numpy as np

def softmax(z, T=1.0):
    z = np.asarray(z, float) / T
    e = np.exp(z - z.max())
    return e / e.sum()

def kl(p, q):
    return float(np.sum(p * np.log(p / q)))

teacher = [9.0, 4.0, 2.0, 0.0, -4.0]    # classes: 2, 3, 7, 8, 0
student_a = [9.0, 1.0, 4.0, 0.0, -4.0]  # same top class, 3 and 7 swapped
student_b = [9.0, 4.0, 2.5, 0.0, -4.0]  # same ranking as the teacher

for T in (1, 5):
    p = softmax(teacher, T)
    print("T =", T)
    for name, z in (("A", student_a), ("B", student_b)):
        q = softmax(z, T)
        ce = -np.log(softmax(z)[0])
        print("  student", name, "hard-label CE %.4f" % ce, "KL(teacher||student) %.4f" % kl(p, q))
```

Predice antes de ejecutarlo: ¿qué estudiante prefiere la entropía cruzada de hard labels frente a la etiqueta "2", y cuál prefiere la divergencia respecto del profesor? Imprime esto, con NumPy 2.5:

```text
T = 1
  student A hard-label CE 0.0072 KL(teacher||student) 0.0177
  student B hard-label CE 0.0083 KL(teacher||student) 0.0001
T = 5
  student A hard-label CE 0.0072 KL(teacher||student) 0.0414
  student B hard-label CE 0.0083 KL(teacher||student) 0.0006
```

El hard label prefiere ligeramente a A, el estudiante con la estructura de similitud equivocada. La divergencia respecto del profesor prefiere a B por un margen amplio. Los números están construidos para la demostración, así que lee la dirección y no los tamaños. La divergencia `KL` es la [divergencia KL](../GLOSSARY.md) de la distribución del profesor respecto de la del estudiante.

### Por qué importa más para un modelo de lenguaje

El pasaje del paper sobre la entropía se aplica directamente a un modelo de lenguaje. Cuando los soft targets tienen alta entropía dan mucha más información por caso de entrenamiento que los hard targets. Una distribución del siguiente token rara vez está cerca de ser one-hot: muchas continuaciones son plausibles. Los autores de Minitron dicen, en un apéndice sobre la pérdida de destilación, que las distribuciones de logits de un LLM tienen mayor entropía que las picudas de los modelos de clasificación (Muralidharan et al., 2024, apéndice A.3). Su observación es sobre esa configuración, pero apunta en la misma dirección.

### Información sobre una clase que el estudiante nunca vio

El paper eliminó todos los 3 del conjunto de transferencia, de modo que el estudiante nunca vio uno. Aun así cometió solo 206 errores de prueba, 133 de ellos sobre los 1010 3 de prueba. La mayoría de los errores venían de que el sesgo aprendido de la clase 3 era demasiado bajo. Con ese sesgo subido en 3.5, una elección hecha para optimizar el rendimiento global en prueba, cometió 109 errores, 14 en 3, y acertó el 98.6% de los 3 de prueba. El conocimiento de cómo es un 3 llegó a través de los soft targets de los otros dígitos.

## Práctica

1. ▢ En la ejecución de arriba, ¿qué estudiante prefiere la entropía cruzada de hard labels con T = 1, y cuál prefiere la divergencia respecto del profesor?

<details markdown="1"><summary>Pista</summary>

Compara primero los dos números de CE, luego los dos de KL, y pregúntate qué puede ver cada pérdida.

</details>

<details markdown="1"><summary>Comprobación</summary>

La entropía cruzada frente a la etiqueta "2" prefiere a A (0.0072 frente a 0.0083). La divergencia respecto del profesor prefiere a B (0.0001 frente a 0.0177). El hard label solo ve la probabilidad de "2". El orden equivocado del 3 y el 7 en A le resulta invisible, y ese orden es lo que lleva el soft target.

</details>

2. ▢ ¿Por qué las probabilidades diminutas del profesor sobre las clases incorrectas casi no ayudan cuando el estudiante se entrena con temperatura 1?

    - a) Solo la entrada de la clase correcta entra en la pérdida
    - b) Las entradas de las clases incorrectas se descartan antes de la pérdida
    - c) Cada término se escala por su probabilidad objetivo
    - d) El softmax del estudiante no puede producir valores tan diminutos

<details markdown="1"><summary>Comprobación</summary>

**c)** Cada término de la entropía cruzada es la probabilidad objetivo por el logaritmo de la del estudiante. Un objetivo de 10^-6 pesa una millonésima parte de lo que pesa uno cercano a 1. No es (b): nada las elimina. No es (a): eso describe la pérdida de hard labels, no la de soft targets. No es (d): un softmax puede producir 10^-9 sin problema.

</details>

3. ▢ Un estudiante entrenado con un conjunto de transferencia sin 3 acierta el 98.6% de los 3 de prueba una vez que se sube su sesgo para la clase 3. ¿Cómo puede saber qué es un 3?

<details markdown="1"><summary>Comprobación</summary>

Los soft targets del profesor sobre otros dígitos, 2, 5 y 8 por ejemplo, ponen una probabilidad pequeña en el 3. Esas probabilidades le enseñan al estudiante qué rasgos suben la puntuación de un 3, sin un solo 3 como ejemplo de entrenamiento. El sesgo aprendido de la clase era demasiado bajo, así que el conocimiento estaba ahí y el desplazamiento era el equivocado. El resultado es del paper, en MNIST, con un sesgo ajustado.

</details>

4. ▢ Un profesor da a un 2 una probabilidad de 1.0 y a un 3 una de 10^-6. Un estudiante les da 0.98 y 0.01. ¿Aproximadamente cuántas veces menor es el término del 3 en la entropía cruzada que el del 2?

<details markdown="1"><summary>Pista</summary>

Cada término es la probabilidad del profesor por el logaritmo natural negativo de la del estudiante.

</details>

<details markdown="1"><summary>Comprobación</summary>

El término del 2 es -1.0 \* ln(0.98), unos 0.0202. El término del 3 es -10^-6 \* ln(0.01), unos 0.0000046. La razón es de unas 4,400, así que es más de 4,000 veces menor. Por eso subir la temperatura, y no simplemente confiar en la pérdida, es la vía del paper para que estas entradas cuenten.

</details>

## Prácticas en el mundo real

- [ ] Ejecuta el script. Luego cambia el estudiante A para que el 3 siga por encima del 7 (por ejemplo `[9.0, 3.0, 2.5, 0.0, -4.0]`) y observa cómo los dos números de KL bajan hacia los del estudiante B.
- [ ] Busca un clasificador que puedas cargar, imprime su softmax para cinco imágenes con temperatura 1 y anota la segunda y la tercera clases más altas. ¿Se parecen a las vecinas de la clase verdadera?
- [ ] Mañana: sin apuntes, explica en dos frases por qué un hard label no puede llevar la similitud entre un 2 y un 7.

## Para profundizar

- [Pérdidas de destilación](../reference/distillation-losses.md)
- [Paper: "Distilling the Knowledge in a Neural Network", Hinton, Vinyals and Dean, 2015](https://arxiv.org/abs/1503.02531)
- [Paper: "Compact Language Models via Pruning and Knowledge Distillation", Muralidharan et al., 2024](https://arxiv.org/abs/2407.14679)
- [Recursos](../RESOURCES.md)

---

¿No termina de quedar claro? Vuelve a leer la fuente primaria de arriba, ya que esta lección la comprime y en la compresión es donde se escapa la comprensión. Consulta el [glosario](../GLOSSARY.md) por si algún término te resultó resbaladizo.

Si lo poco claro es la propia lección y no el material, eso es un defecto: [abre un issue](https://github.com/TokenCemetery/teach/issues).
