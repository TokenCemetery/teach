---
title: "5. KL directa e inversa"
description: "Por qué la KL directa reparte al estudiante sobre cada modo del profesor y la KL inversa lo hace comprometerse con uno"
type: lesson
---

# Lección 5. KL directa e inversa

**Vínculo con la misión:** La misión te pide elegir entre KL directa e inversa, y esta lección da las dos direcciones, el caso de juguete que las separa y los papers que discrepan sobre cuál usar.
**Fuente principal:** [Paper: "MiniLLM: On-Policy Distillation of Large Language Models", Gu et al., 2023](https://arxiv.org/abs/2306.08543)
**Requisitos previos:** [Lección 4](0004-token-level-distillation.md), [KL directa](../GLOSSARY.md), [KL inversa](../GLOSSARY.md), [Divergencia KL](../GLOSSARY.md)

## Calentamiento

1. ▢ En `token_kd_loss`, ¿sobre qué eje se toma la divergencia, y qué le hace la máscara a la media final?

<details markdown="1"><summary>Comprobación</summary>

La divergencia se toma sobre el eje del vocabulario, el último, y da un número por posición. La máscara pone a cero las posiciones de padding y la división final entre la suma de la máscara promedia solo sobre los tokens reales.

</details>

2. ▢ En la lección 2, una probabilidad del profesor de 10^-6 en una clase incorrecta casi no movió una pérdida de entropía cruzada. ¿Qué factor del término lo hace pequeño?

<details markdown="1"><summary>Comprobación</summary>

El término es la probabilidad del profesor por una razón logarítmica, así que un objetivo de 10^-6 lo reduce a una millonésima. Tenlo presente: la dirección de la KL decide de quién es la probabilidad que hace la escala.

</details>

## Qué debes saber

### Dos direcciones de una misma divergencia

La divergencia KL no es simétrica. Con p el profesor y q el estudiante, la [KL directa](../GLOSSARY.md) es KL(p || q), la suma sobre tokens de p log(p / q). La [KL inversa](../GLOSSARY.md) es KL(q || p), la suma de q log(q / p). La única diferencia es de quién es la probabilidad que multiplica la razón logarítmica, y eso decide qué penaliza cada una. GKD (Agarwal et al., 2023, sección 2) usa estos mismos nombres.

La KL directa pondera cada token por la probabilidad del profesor. Un token que le gusta al profesor y al que el estudiante da casi nada de probabilidad cuesta mucho, porque la razón p / q es enorme. Un token al que el profesor da casi nada y que le gusta al estudiante sale barato, porque p es pequeña. El estudiante es empujado a poner algo de masa donde el profesor tiene masa, lo que cubre modos.

La KL inversa pondera cada token por la probabilidad del estudiante. Se castiga al estudiante por poner masa donde el profesor casi no tiene, porque q log(q / p) es grande ahí. Ignorar un modo del profesor no cuesta nada, así que el estudiante es libre de quedarse con uno. Eso busca modos.

### Dos modos, dos estudiantes

El profesor de abajo tiene dos continuaciones igual de probables y un poco de probabilidad en otras dos. El primer estudiante reparte su masa. El segundo se compromete con un modo.

```python
import numpy as np

p = np.array([0.49, 0.01, 0.01, 0.49])        # teacher: two modes
students = {
    "spread": np.array([0.25, 0.25, 0.25, 0.25]),
    "commit": np.array([0.97, 0.01, 0.01, 0.01]),
}

def kl(a, b):
    return float(np.sum(a * np.log(a / b)))

for name, q in students.items():
    print(name, "forward %.3f" % kl(p, q), "reverse %.3f" % kl(q, p))
```

Predice qué estudiante prefiere cada dirección y luego ejecútalo. La salida con NumPy 2.5:

```text
spread forward 0.595 reverse 1.273
commit forward 1.572 reverse 0.623
```

La KL directa prefiere al estudiante repartido (0.595 frente a 1.572), que pone probabilidad en ambos modos y desperdicia algo en los dos tokens raros. La KL inversa prefiere al estudiante comprometido (0.623 frente a 1.273), que se sienta en un modo e ignora el otro. Ninguno de los dos estudiantes iguala al profesor. Cuál de los fallos quieres depende de lo que hará el estudiante a continuación, que es el argumento de los dos papers siguientes.

### El argumento a favor de la KL inversa

Gu et al. sostienen que los objetivos de destilación estándar minimizan una KL directa aproximada, que obliga al estudiante a cubrir todos los modos del profesor. En clasificación, con un número finito de clases, ambas distribuciones tienen pocos modos y eso funciona bien. En la generación abierta el profesor puede tener muchos más modos de los que un estudiante pequeño puede expresar. El paper dice que la KL directa hace entonces que el estudiante asigne una probabilidad irrazonablemente alta a regiones donde el profesor tiene casi nada, y produce muestras muy improbables bajo el profesor durante la generación libre (introducción). Su remedio es la KL inversa, que busca los modos principales y da baja probabilidad a las regiones vacías del profesor. En texto, dicen, el estudiante evita aprender demasiadas variantes de cola larga de la distribución del profesor y se centra en la corrección.

Muestran el efecto en un caso de juguete: una mezcla gaussiana ajustada con una sola gaussiana por cada divergencia (Figura 2). Optimizan la KL inversa con un policy gradient sobre muestras del estudiante, con pasos extra para la estabilidad, lo que la convierte en un método on-policy. La lección 15 lo cubre. La pérdida en sí es simple. Con las log-probabilidades del fragmento anterior, la KL inversa por posición es `(s.exp() * (s - t)).sum(dim=-1)` en lugar de la línea de la KL directa.

### El argumento a favor de elegir

GKD no toma partido. Convierte la divergencia en un parámetro. Su JSD generalizada, para un coeficiente beta entre 0 y 1, es:

```text
JSD(beta)(P || Q) = beta * KL(P || beta*P + (1-beta)*Q) + (1-beta) * KL(Q || beta*P + (1-beta)*Q)
```

Con P el profesor, interpola entre las dos direcciones. Los gradientes se comportan como la KL directa cuando beta se acerca a 0 y como la KL inversa cuando beta se acerca a 1. También está acotada incluso cuando los soportes son disjuntos, cosa que la KL no cumple (sección 2). En el mismo caso de juguete, con la función `jsd` escrita a partir de esa fórmula (no está en el paper), los tres valores de JSD dan un cruce:

| Estudiante | JSD(0.1) | JSD(0.5) | JSD(0.9) |
|---|---|---|---|
| repartido | 0.055 | 0.177 | 0.091 |
| comprometido | 0.102 | 0.189 | 0.058 |

Con beta = 0.1 gana el estudiante repartido y con beta = 0.9 el comprometido, lo que coincide con la dirección que se dice que prefiere cada extremo. Con 0.5 están cerca. Los números salen del caso de juguete, no de ninguna ejecución.

Los experimentos de GKD dicen que la mejor divergencia depende de la tarea. En el resumen de XSum, pasar de KL directa a KL inversa a través de la familia JSD disminuyó la diversidad de la salida (Figura 4). En las ablaciones, las divergencias que buscan modos funcionaron mejor evaluadas con muestreo con temperatura, y la elección importó poco con decodificación voraz (sección 4.1). En el instruction tuning agnóstico de tarea con FLAN, GKD on-policy con KL inversa superó ampliamente a KD supervisada y a ImitKD, y la KL inversa funcionó mucho mejor que la KL directa ahí (Figura 10). En GSM8K, la KL directa funcionó bastante bien, y la inversa también, sobre todo al entrenar solo con un dataset fijo. El resumen del paper es que la divergencia hay que elegirla según el equilibrio entre diversidad y calidad en la tarea.

La implementación de TRL expone esta elección como `beta` en `GKDConfig`: con 0.0 la pérdida es la divergencia KL, con 1.0 la KL inversa, con un valor por defecto de 0.5 ([documentación de GKD de TRL](https://huggingface.co/docs/trl/main/en/gkd_trainer), leída para esta lección).

### Evidencia en el otro sentido

Los autores de Minitron reentrenan base models podados a partir de su profesor sin podar y probaron las direcciones directamente. En un Minitron 8B podado en profundidad, la pérdida de logits con KLD directa alcanzó una pérdida de LM de 2.155 frente a 2.665 de la KLD inversa (su Tabla 16, apéndice A.3). En el Nemotron-3 8B de la generación anterior, la pérdida combinada dio 2.117 con KLD directa y 2.140 con la inversa (Tabla 15). Señalan que trabajos previos encontraron la KLD inversa más adecuada para el supervised fine-tuning y el seguimiento de instrucciones, que Agarwal et al. dicen que la elección depende de la tarea, y que la KLD directa es la mejor opción para su configuración de base model (sección 4).

Así que la evidencia no es una sola regla. La KL inversa tiene el respaldo de los resultados de instruction tuning en estudiantes pequeños en GKD, y la KL directa tiene el respaldo del reentrenamiento de base models en Minitron. Ambos son papers individuales sobre sus propios modelos.

## Práctica

1. ▢ En la ejecución de dos modos, ¿qué estudiante prefiere la KL directa y cuál prefiere la KL inversa?

<details markdown="1"><summary>Pista</summary>

Pregunta qué estudiante ha puesto algo de probabilidad en ambos tokens grandes del profesor, y cuál ignora uno de ellos.

</details>

<details markdown="1"><summary>Comprobación</summary>

La KL directa prefiere al estudiante repartido (0.595 frente a 1.572) y la KL inversa al comprometido (0.623 frente a 1.273). La KL directa castiga al estudiante comprometido por una q cercana a 0.01 donde p es 0.49. La KL inversa castiga al estudiante repartido por poner 0.25 donde p es 0.01.

</details>

2. ▢ ¿Cuál es el argumento del paper contra la KL directa para la generación abierta?

    - a) La pérdida no se puede calcular a partir de la distribución completa
    - b) El estudiante debe cubrir más modos de los que puede expresar
    - c) El gradiente siempre se anula cuando el profesor está muy seguro
    - d) Los logits del profesor deben suavizarse para que funcione

<details markdown="1"><summary>Comprobación</summary>

**b)** Un profesor sobre texto tiene muchos más modos de los que un estudiante pequeño puede expresar, y la KL directa obliga al estudiante a cubrirlos, así que pone masa en regiones que el profesor considera vacías. No es (a): ambas direcciones se pueden calcular a partir de las distribuciones completas. No es (c): esa es la observación de la lección 2 sobre las probabilidades pequeñas, un problema distinto. No es (d): la temperatura es una elección aparte de la dirección.

</details>

3. ▢ Con la tabla de JSD, ¿qué estudiante prefiere JSD(0.9), y coincide eso con la afirmación de GKD de que beta cerca de 1 se comporta como la KL inversa?

<details markdown="1"><summary>Comprobación</summary>

El estudiante comprometido (0.058 frente a 0.091), y sí: la KL inversa también lo prefiere. Con beta = 0.1 gana el estudiante repartido, como lo haría la KL directa. La tabla es una comprobación de juguete de la descripción del paper, no un resultado de una ejecución de entrenamiento.

</details>

4. ▢ La Tabla 16 de Minitron da una pérdida de LM de 2.155 con KLD directa y 2.665 con KLD inversa para un estudiante de 8B podado en profundidad. ¿Contradice esto a MiniLLM y a GKD?

<details markdown="1"><summary>Comprobación</summary>

No, no directamente. MiniLLM y GKD informan de resultados de seguimiento de instrucciones y de resumen en estudiantes pequeños, con la dirección inversa a menudo sobre secuencias muestreadas del estudiante. Minitron reentrena un base model podado con una mezcla de estilo preentrenamiento y mide la pérdida de LM. La configuración difiere en la tarea, en el punto de partida del estudiante y en la métrica, así que la evidencia respalda una elección que depende de la tarea, como dice GKD. Prueba ambas en tu propia tarea antes de comprometerte.

</details>

5. ▢ ¿Qué divergencia es sorda a una probabilidad diminuta del profesor, como en la lección 2, y cuál castiga al estudiante por la masa colocada ahí?

<details markdown="1"><summary>Comprobación</summary>

La KL directa es casi sorda a una probabilidad diminuta del profesor porque p multiplica la razón logarítmica, que es el problema de la lección 2. La KL inversa castiga la masa del estudiante colocada donde el profesor casi no tiene, porque q multiplica la razón logarítmica. Las dos direcciones responden a preguntas opuestas sobre el mismo número pequeño.

</details>

## Prácticas en el mundo real

- [ ] Ejecuta el fragmento y luego cambia el profesor a `[0.45, 0.05, 0.05, 0.45]` y comprueba si cambian las preferencias de las dos direcciones.
- [ ] Abre el apéndice A.7 del paper de GKD y lee el pie de la figura sobre KL que busca modos frente a KL que cubre modos. Escribe una frase sobre qué hace el estudiante unimodal bajo cada dirección.
- [ ] Mañana: sin apuntes, di qué dirección recomienda cada uno de MiniLLM, GKD y Minitron y para qué configuración.

## Para profundizar

- [Pérdidas de destilación](../reference/distillation-losses.md)
- [Paper: "MiniLLM: On-Policy Distillation of Large Language Models", Gu et al., 2023](https://arxiv.org/abs/2306.08543)
- [Paper: "On-Policy Distillation of Language Models: Learning from Self-Generated Mistakes", Agarwal et al., 2023](https://arxiv.org/abs/2306.13649)
- [Documentation: "Generalized Knowledge Distillation Trainer", Hugging Face TRL](https://huggingface.co/docs/trl/main/en/gkd_trainer)
- [Paper: "Compact Language Models via Pruning and Knowledge Distillation", Muralidharan et al., 2024](https://arxiv.org/abs/2407.14679)
- [Recursos](../RESOURCES.md)

---

¿No termina de quedar claro? Vuelve a leer la fuente primaria de arriba, ya que esta lección la comprime y en la compresión es donde se escapa la comprensión. Consulta el [glosario](../GLOSSARY.md) por si algún término te resultó resbaladizo.

Si lo poco claro es la propia lección y no el material, eso es un defecto: [abre un issue](https://github.com/TokenCemetery/teach/issues).
