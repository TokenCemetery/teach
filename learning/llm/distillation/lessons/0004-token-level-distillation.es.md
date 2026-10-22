---
title: "4. Destilación a nivel de token"
description: "Igualar la distribución del siguiente token del profesor en cada posición de una secuencia"
type: lesson
---

# Lección 4. Destilación a nivel de token

**Vínculo con la misión:** La misión te pide escribir la pérdida de destilación a nivel de token para un LLM, y esta lección la escribe: una divergencia por posición, sumada o promediada sobre la secuencia, con el padding enmascarado.
**Fuente principal:** [Paper: "Sequence-Level Knowledge Distillation", Kim and Rush, 2016](https://arxiv.org/abs/1606.07947)
**Requisitos previos:** [Lección 3](0003-temperature.md), [Destilación a nivel de token](../GLOSSARY.md), [Teacher forcing](../GLOSSARY.md), [Divergencia KL](../GLOSSARY.md)

## Calentamiento

1. ▢ En la pérdida combinada, ¿qué término corre con la temperatura alta, y qué lo multiplica?

<details markdown="1"><summary>Comprobación</summary>

La entropía cruzada con los soft targets del profesor corre con la temperatura alta T, y T al cuadrado la multiplica para que sus gradientes conserven su tamaño frente al término de hard labels cuando T cambia. El término de hard labels corre con T = 1.

</details>

2. ▢ ¿Por qué una probabilidad de 10^-6 del profesor en una clase incorrecta es casi invisible para la pérdida con T = 1?

<details markdown="1"><summary>Comprobación</summary>

El término de entropía cruzada de esa clase es su probabilidad objetivo por el logaritmo de la probabilidad del estudiante, así que un objetivo de 10^-6 hace que el término pese una millonésima parte de lo que pesa uno cercano a 1. Una T mayor sube esos objetivos para que cuenten.

</details>

## Qué debes saber

### El origen: destilación a nivel de palabra

Kim y Rush aplican la idea de Hinton a la traducción. Un modelo de traducción neuronal se entrena para minimizar el logaritmo de verosimilitud negativo de cada palabra objetivo dada la oración de origen y las palabras anteriores, así que existe un profesor en cada posición de la oración. Definen la pérdida a nivel de palabra para una oración como una suma sobre las posiciones j y sobre cada palabra k del vocabulario objetivo V:

```text
L_WORD-KD = - sum_j sum_k q(t_j = k | s, t_<j) * log p(t_j = k | s, t_<j)
```

Aquí q es el profesor, p el estudiante, s la oración de origen, y el último argumento de cada probabilidad es el prefijo, las palabras objetivo anteriores a la posición j. El estudiante también puede entrenarse con una mezcla de esta pérdida y el logaritmo de verosimilitud negativo ordinario a nivel de palabra. La llaman destilación de conocimiento a nivel de palabra (sección 3.1). En un LLM la unidad es un token, por eso este track dice [destilación a nivel de token](../GLOSSARY.md).

Fíjate en cuál es el condicionamiento. El prefijo viene de la secuencia objetivo real de los datos de entrenamiento. La Figura 1 del paper lo describe como minimizar la entropía cruzada entre las distribuciones del estudiante y del profesor para cada palabra de la secuencia objetivo real. A ambos modelos se les da el mismo prefijo fijo y cada uno produce una distribución para la palabra siguiente, que es [teacher forcing](../GLOSSARY.md).

En inglés a alemán de WMT 2014 (Tabla 1), un estudiante de 2 capas de 500 unidades obtuvo 14.7 BLEU con decodificación voraz y 17.6 con beam search. Con destilación a nivel de palabra obtuvo 15.4 y 17.7, mejoras de 0.7 y 0.1. El profesor de 4 capas y 1000 unidades obtuvo 17.7 y 19.5. Los autores probaron pesos de mezcla de 0.5 y 0.9 y encontraron mejor 0.5. El paper dice que la destilación a nivel de palabra mejora el baseline, y que su método a nivel de secuencia lo hace mejor, que es el tema de la etapa 3.

### La pérdida para un LLM

Tres papers recientes escriben la misma pérdida en formas ligeramente distintas. Coinciden en la estructura: una divergencia entre las dos distribuciones del siguiente token en cada posición, combinada sobre la secuencia.

- Gemma 2 (Gemma Team, 2024, sección 3.2) minimiza el logaritmo de verosimilitud negativo entre las probabilidades del profesor y del estudiante, la suma sobre x de -P_T(x | x_c) log P_S(x | x_c), donde x_c es el contexto.
- GKD (Agarwal et al., 2023, ecuación 2) promedia una divergencia sobre las posiciones: la divergencia se suma sobre las posiciones de salida n y se divide entre la longitud de la salida L_y.
- Minitron (Muralidharan et al., 2024, sección 3) promedia sobre la longitud de la secuencia l, con una temperatura tau en el softmax.

La entropía cruzada y la KL directa difieren en la entropía de la distribución del profesor, que no depende del estudiante. Sus gradientes respecto de los parámetros del estudiante son los mismos, por eso los papers usan cualquiera de los dos nombres para un único objetivo. La suma sobre el vocabulario está dentro de cada término. Así que la forma del cálculo es un tensor de logits por modelo con dimensiones batch, posición y vocabulario, y una divergencia tomada sobre el último eje.

```python
import torch.nn.functional as F

def token_kd_loss(student_logits, teacher_logits, mask, T=1.0):
    # logits: (batch, positions, vocab). mask: (batch, positions), 1.0 for real tokens.
    s = F.log_softmax(student_logits / T, dim=-1)
    t = F.log_softmax(teacher_logits / T, dim=-1)
    kl = (t.exp() * (t - s)).sum(dim=-1)        # (batch, positions)
    return (kl * mask).sum() / mask.sum()        # mean over real tokens
```

Los logits del profesor salen de un forward pass con los gradientes desactivados. Tres elecciones de esa función son decisiones, no hechos. La media sobre los tokens reales podría ser una suma, como la escriben Kim y Rush, y la suma escala con la longitud de la secuencia. La máscara importa porque las posiciones de padding no tienen un objetivo con sentido. Y T = 1 es el valor por defecto por la ablación de temperatura de Minitron de la lección 3.

### La misma aritmética, ejecutable

La versión de NumPy de abajo hace la aritmética de la función anterior sobre tres posiciones con cuatro tokens, sin necesitar ningún framework. Los logits del profesor y del estudiante coinciden exactamente en la tercera posición, que representa el padding.

```python
import numpy as np

def log_softmax(z):
    z = z - z.max(axis=-1, keepdims=True)
    return z - np.log(np.exp(z).sum(axis=-1, keepdims=True))

teacher = np.array([[3.0, 1.0, 0.0, -1.0],
                    [0.0, 2.5, 2.0, -2.0],
                    [1.0, 1.0, 1.0, 1.0]])
student = np.array([[2.0, 1.5, 0.5, -1.0],
                    [0.5, 2.0, 2.0, -1.0],
                    [1.0, 1.0, 1.0, 1.0]])
t, s = log_softmax(teacher), log_softmax(student)
kl = (np.exp(t) * (t - s)).sum(axis=-1)
mask = np.array([1, 1, 0])
print(np.round(kl, 4), round(kl.sum(), 4), round(kl.mean(), 4))
print(round((kl * mask).sum() / mask.sum(), 4))
```

Predice el último número frente a la media de los tres antes de ejecutarlo. La salida con NumPy 2.5:

```text
[0.1998 0.0541 0.    ] 0.2539 0.0846
0.127
```

Promediar sobre las tres posiciones diluye la pérdida con una posición que no lleva señal. Promediar sobre los dos tokens reales da 0.127.

### Lo que cuesta la secuencia fija

Las secuencias se fijan antes del entrenamiento, ya sea texto humano o texto que escribió el profesor, y el estudiante ve la distribución del profesor solo a lo largo de esas secuencias. En el momento de generar, el estudiante continúa desde sus propios tokens, que ninguna distribución de aquí cubrió. La lección 14 de la etapa 5 llama a esto exposure bias, y la lección 15 muestra la solución on-policy. El profesor además cuesta un forward pass por cada batch, que los autores de Minitron enumeran como la sobrecarga extra de la destilación frente al entrenamiento convencional (sección 4).

## Práctica

1. ▢ En la ejecución de NumPy, ¿por qué la media sobre los tokens reales, 0.127, supera la media sobre las tres posiciones, 0.0846?

<details markdown="1"><summary>Pista</summary>

Cuenta las posiciones en cada denominador, y mira qué aporta la tercera posición al numerador.

</details>

<details markdown="1"><summary>Comprobación</summary>

La tercera posición suma 0 al numerador pero cuenta en el denominador de la media simple: 0.2539 / 3 es 0.0846. Enmascarado, el denominador es 2 y 0.2539 / 2 es 0.127. En un batch real con mucho padding la media sin enmascarar subestima la pérdida, y la subestimación cambia con la cantidad de padding.

</details>

2. ▢ En la pérdida a nivel de palabra de Kim y Rush, ¿en qué prefijo se condicionan tanto el profesor como el estudiante?

    - a) Las palabras objetivo de los datos de entrenamiento
    - b) Las palabras que el estudiante muestreó por su cuenta
    - c) Las palabras que el profesor eligió por decodificación voraz
    - d) Las palabras de la oración de origen de entrada

<details markdown="1"><summary>Comprobación</summary>

**a)** El prefijo es la secuencia objetivo real, así que ambos modelos ven las mismas palabras fijas. No es (b): esa es la configuración on-policy de la lección 15. No es (c): decodificar la propia salida del profesor es el método a nivel de secuencia de la etapa 3. No es (d): la oración de origen es la otra entrada de condicionamiento, s, no el prefijo.

</details>

3. ▢ Gemma 2 minimiza una entropía cruzada frente a las probabilidades del profesor, y Minitron escribe una divergencia KL. ¿Por qué ambas pueden describir la misma señal de entrenamiento?

<details markdown="1"><summary>Comprobación</summary>

La KL directa es igual a la entropía cruzada menos la entropía del profesor, y el profesor está fijo, así que esa entropía es una constante respecto de los parámetros del estudiante. Las dos pérdidas difieren en el valor y no en el gradiente. Comprueba en cualquier paper nuevo a cuál se refiere antes de comparar valores de pérdida entre papers.

</details>

4. ▢ Cambia `token_kd_loss` para que aplique la temperatura y el factor T al cuadrado de la lección 3. ¿Qué dos cambios, y por qué la función ya contenía uno de ellos?

<details markdown="1"><summary>Comprobación</summary>

La función ya divide ambos conjuntos de logits entre T antes del log-softmax, así que la temperatura ya está. Lo que falta es el factor: multiplica la pérdida devuelta por T ** 2 cuando se combina con un término de hard labels, para que el término suave conserve su peso cuando T cambie. Con T = 1 el factor es 1, por eso la función de arriba no necesita cambios con su valor por defecto.

</details>

5. ▢ Un compañero informa de que la pérdida de destilación de su ejecución con un LLM cayó a la mitad después de pasar a batches con padding hasta una longitud mayor. El modelo no ha cambiado. ¿Qué compruebas primero?

<details markdown="1"><summary>Pista</summary>

Las posiciones de padding coinciden exactamente entre un modelo y él mismo, así que añaden divergencia cero.

</details>

<details markdown="1"><summary>Comprobación</summary>

Si la media divide entre todas las posiciones o solo entre los tokens reales. Con lo primero, una longitud de padding mayor añade posiciones al denominador y el número cae sin ningún cambio en la calidad. Divide entre la suma de la máscara, como hace la función de arriba, y vuelve a comparar las dos ejecuciones.

</details>

## Prácticas en el mundo real

- [ ] Ejecuta el fragmento de NumPy. Luego cambia los logits del estudiante en la primera posición para que sean iguales a los del profesor y confirma que la primera entrada de la pérdida por posición cae a 0.
- [ ] Abre el paper de GKD y encuentra la ecuación 2. Anota junto a ella si suma o promedia sobre las posiciones y cómo se compara eso con la suma de Kim y Rush.
- [ ] Mañana: sin apuntes, escribe la forma de cada tensor de `token_kd_loss`, y luego di qué protege la máscara.

## Para profundizar

- [Pérdidas de destilación](../reference/distillation-losses.md)
- [Paper: "Sequence-Level Knowledge Distillation", Kim and Rush, 2016](https://arxiv.org/abs/1606.07947)
- [Paper: "On-Policy Distillation of Language Models: Learning from Self-Generated Mistakes", Agarwal et al., 2023](https://arxiv.org/abs/2306.13649)
- [Paper: "Gemma 2: Improving Open Language Models at a Practical Size", Gemma Team, 2024](https://arxiv.org/abs/2408.00118)
- [Recursos](../RESOURCES.md)

---

¿No termina de quedar claro? Vuelve a leer la fuente primaria de arriba, ya que esta lección la comprime y en la compresión es donde se escapa la comprensión. Consulta el [glosario](../GLOSSARY.md) por si algún término te resultó resbaladizo.

Si lo poco claro es la propia lección y no el material, eso es un defecto: [abre un issue](https://github.com/TokenCemetery/teach/issues).
