---
title: "21. Volumen de datos y costo del profesor"
description: "Contar la inferencia del profesor en el presupuesto, y decidir cuántos datos de destilación bastan"
type: lesson
---

# Lección 21. Volumen de datos y costo del profesor

**Vínculo con la misión:** La misión te pide elegir un volumen de datos con el propio costo del profesor contado en el presupuesto, lo que exige una fórmula que puedas ejecutar al dorso de un sobre y una visión clara de qué costos estás pagando y cuáles no.
**Fuente principal:** [Paper: "Distillation Scaling Laws", Busbridge et al., 2025](https://arxiv.org/abs/2502.08606), sección 5 y Ecuación 9
**Requisitos previos:** [Lección 20](0020-choosing-student-size.md), [Profesor](../GLOSSARY.md), [Destilación a nivel de secuencia](../GLOSSARY.md), [Datos sintéticos](../GLOSSARY.md)

## Calentamiento

1. ▢ La lección 20 enumeró dos condiciones bajo las cuales la destilación es más eficiente que el aprendizaje supervisado. Enuncia ambas.

<details markdown="1"><summary>Comprobación</summary>

El cómputo o los tokens totales del estudiante no deben superar un umbral que depende del tamaño del estudiante, y un profesor debe existir ya o tener usos más allá de una única destilación. Si falla cualquiera de las dos, el resultado del paper favorece entrenar directamente al estudiante.

</details>

2. ▢ La lección 8 entrenó a un estudiante con las salidas decodificadas del profesor, y la lección 9 lo comparó con igualar distribuciones. ¿Cuál de los dos necesita los logits del profesor, y cuál solo su texto?

<details markdown="1"><summary>Comprobación</summary>

La destilación [a nivel de token](../GLOSSARY.md) (de logits) necesita la distribución por posición del profesor. La [destilación a nivel de secuencia](../GLOSSARY.md) necesita solo el texto que decodificó el profesor, por eso funciona a través de una API que no devuelve nada más. Los dos colocan el costo del profesor en lugares distintos, que esta lección pone precio.

</details>

3. ▢ La lección 12 dijo que el volumen no arregla los malos ejemplos. Si duplicaras un conjunto generado sin filtrarlo, ¿qué esperarías que pasara con la proporción de malos ejemplos en él?

<details markdown="1"><summary>Comprobación</summary>

Se quedaría más o menos igual. Duplicar un conjunto con una tasa de defectos fija duplica los defectos junto con los buenos ejemplos. Más datos ayudan solo después de que el filtrado de la lección 12 haya fijado la calidad, por eso esta lección cuenta los tokens que sobreviven al filtro.

</details>

## Qué debes saber

### Dos costos, dos fórmulas

El costo de entrenamiento de un transformer denso se aproxima comúnmente como 6 FLOPs por parámetro por token: unos 2 para el forward pass y 4 para el backward pass. Un forward pass solo son unos 2 por parámetro por token. Son aproximaciones. Ignoran el término de atención, que crece con la longitud de contexto, y cuentan todos los parámetros por igual.

El paper lo dice igualmente. Escribe el costo supervisado como aproximadamente 6ND, usa la aproximación de forward 2N como la abreviatura habitual, y luego se niega a usarla para sus propios resultados, por dos razones: usar parámetros sin embeddings la sesga, y para modelos pequeños con contextos largos la contribución de la atención es significativa (sección 5, debajo de la Ecuación 9). En su lugar deriva un costo corregido por token. Para planificar a nivel de orden de magnitud la abreviatura sirve. Para un número que vayas a defender, enúncialo como una aproximación y di qué dejaste fuera.

Su costo de destilación (Ecuación 9) es el entrenamiento del estudiante más los forward passes del profesor, donde cada uno se carga solo si te aplica. En forma abreviada:

```text
student training   ≈ 6 × N_student × D
teacher inference  ≈ 2 × N_teacher × D     (forward only, over the same D tokens)
```

Aquí N son los parámetros y D es el número de tokens con que entrena el estudiante. El término del profesor usa la misma D porque la destilación de logits ejecuta al profesor sobre cada token que ve el estudiante. Dividir uno entre el otro da una razón que merece recordarse:

```text
teacher cost / student cost  ≈  N_teacher / (3 × N_student)
```

Un profesor tres veces el tamaño del estudiante cuesta ejecutarlo aproximadamente lo mismo que cuesta entrenar al estudiante. Cualquier profesor mayor cuesta más que el estudiante que estás construyendo.

### Ejemplo resuelto: puntuar tokens con un profesor

Un estudiante de 1B entrena con 100B de tokens, con logits de un profesor que puntúa esos mismos tokens.

| Cantidad | Cálculo | FLOPs |
|---|---|---|
| Entrenamiento del estudiante | 6 × 1e9 × 1e11 | 6.0e20 |
| Puntuación con un profesor de 7B | 2 × 7e9 × 1e11 | 1.4e21 |
| Puntuación con un profesor de 70B | 2 × 70e9 × 1e11 | 1.4e22 |

El profesor de 7B cuesta unas 2.3 veces el propio entrenamiento del estudiante, y el de 70B unas 23 veces. El baseline supervisado para el mismo estudiante con los mismos tokens cuesta solo los 6.0e20. La ejecución con el de 70B es el mismo estudiante entrenado con unas 24 veces el cómputo, así que para que valga la pena la pérdida del estudiante tiene que ser mucho menor que la del estudiante supervisado con el mismo cómputo, y el umbral de la lección 20 dice con qué frecuencia se cumple eso.

### Repartir el costo del profesor entre estudiantes

Si el profesor puntúa un dataset una vez y sus logits se almacenan, varios estudiantes pueden entrenar desde el mismo pase. Con cuatro estudiantes de 1B sobre esos 100B de tokens y el profesor de 7B: un estudiante cuesta 1.4e21 + 6.0e20 = 2.0e21, y cuatro cuestan 1.4e21 + 4 × 6.0e20 = 3.8e21, que son 9.5e20 cada uno. Esta es la tercera configuración del paper, en la que el costo del profesor se reparte entre los estudiantes a los que sirve (su Tabla 2). Deja fuera lo que cuesta almacenar logits, una factura que introdujo la lección 7 y que el paper trata por separado.

### Ejemplo resuelto: texto generado en lugar de logits

En la destilación a nivel de secuencia al profesor se le carga por generar, no por puntuar. Generar G tokens cuesta aproximadamente 2 × N_teacher × G en FLOPs según la aproximación del forward pass, y el estudiante entrena luego con esos G tokens durante cada época. Esto extiende la contabilidad del paper y no es de él, ya que el paper estudia logits.

Un profesor de 70B genera 1B de tokens: 2 × 70e9 × 1e9 = 1.4e20. Un estudiante de 3B entrena dos épocas con ellos: 6 × 3e9 × 1e9 × 2 = 3.6e19. La generación del profesor es unas 3.9 veces el entrenamiento del estudiante, y el conjunto generado es reutilizable, así que un segundo estudiante no le paga nada al profesor.

Una precaución al leer FLOPs como costo. Generar un token a la vez mantiene a una GPU lejos de la utilización completa, así que el tiempo de reloj y el dinero de la generación quedan muy por encima de lo que implican los FLOPs. Eso es conocimiento general sobre la decodificación, no un resultado de una fuente de aquí, así que mide los tokens por segundo en tu hardware antes de citar un presupuesto.

### Lo que dice el paper sobre adónde va el dinero

Cuando el preentrenamiento del profesor forma parte de la factura, la Tabla 3 del paper resume cómo se mueve con la escala el mejor reparto:

| Tamaño del estudiante | Cómputo | Asignación óptima |
|---|---|---|
| Pequeño (hasta unos 3B) | Pequeño (hasta unos 1e21 FLOPs) | Sobre todo preentrenamiento del profesor |
| Pequeño (hasta unos 3B) | Grande (unos 1e25 FLOPs en adelante) | A partes iguales entre entrenamiento del estudiante e inferencia del profesor, mucho menos en preentrenamiento del profesor |
| Grande (unos 10B en adelante) | Pequeño | Sobre todo entrenamiento estándar del estudiante |
| Grande (unos 10B en adelante) | Grande | A partes iguales entre entrenamiento del estudiante, inferencia del profesor y preentrenamiento del profesor |

Lee esto como el óptimo del paper para su ley, en el escenario donde cuenta el preentrenamiento del profesor. No son una receta para un profesor abierto que ya tienes, donde la columna de preentrenamiento es cero.

### Cuántos datos bastan

La respuesta honesta del paper es que más tokens no son gratis ni ilimitados. Con un profesor fijo, la ventaja de la destilación sobre el aprendizaje supervisado se encoge al crecer el presupuesto de tokens, y eventualmente el aprendizaje supervisado la iguala o la supera (sección 5.1). Así que "bastan" es el punto donde un token extra se gasta mejor en la propia señal del estudiante, y ese punto sube con el tamaño del estudiante.

Minitron es un contraste útil. En la Tabla 2 de Muralidharan et al., Minitron 8B se entrenó con 94B de tokens, frente a 3.8T de Nemotron-3 8B, unas 40 veces menos. La comparación tiene dos salvedades. El estudiante de Minitron parte de los pesos del profesor tras la poda, mientras que los estudiantes del paper parten de cero. Y la cifra de 40 veces compara un modelo podado y destilado con un modelo desde cero, no con una ejecución supervisada del mismo estudiante. Así que muestra cuán pocos datos puede necesitar una buena inicialización. No muestra cuántos datos necesita un estudiante desde cero.

Su ahorro a nivel de familia también es una elección contable. Informan de un cómputo 1.8 veces menor para la familia de 15B, 8B y 4B (sección 4.1), calculado como (4.4e17 + 2.5e17 / 40 + 1.2e17 / 40) frente a 4.4e17 + 2.5e17 + 1.2e17, en FLOPs por paso de entrenamiento. Tal como está escrita, la suma cuenta los pasos de entrenamiento propios de cada modelo. Las frases que describen el cálculo no añaden un término por ejecutar el profesor de 15B durante el reentrenamiento de los modelos más pequeños. Ese es el término que esta lección dice que hay que contar.

## Práctica

1. ▢ Calcula: un estudiante de 1B entrena con 50B de tokens con un pase de logits almacenados de un profesor de 8B. Da los FLOPs de entrenamiento del estudiante, los FLOPs de puntuación del profesor y la razón del segundo al primero.

<details markdown="1"><summary>Pista</summary>

Usa 6 × N × D para el estudiante y 2 × N × D para el profesor, con la misma D en ambos. La razón también es igual a N_teacher dividido entre tres veces N_student.

</details>

<details markdown="1"><summary>Comprobación</summary>

Estudiante: 6 × 1e9 × 5e10 = 3.0e20. Profesor: 2 × 8e9 × 5e10 = 8.0e20. Razón: unas 2.7, que coincide con 8 / (3 × 1) = 2.67. Ambas son cifras de orden de magnitud a partir de las aproximaciones 6N y 2N. Dejan fuera la atención y el costo de almacenar o mover los logits.

</details>

2. ▢ Un profesor de 70B genera 1B de tokens de respuestas, y un estudiante de 3B entrena con ellos durante dos épocas. ¿Cuál de los dos cuesta más FLOPs, y por qué factor?

<details markdown="1"><summary>Pista</summary>

La generación es un forward pass por token a 2 × N_teacher. El entrenamiento es 6 × N_student por token por época.

</details>

<details markdown="1"><summary>Comprobación</summary>

Generación: 2 × 70e9 × 1e9 = 1.4e20. Entrenamiento: 6 × 3e9 × 1e9 × 2 = 3.6e19. La generación del profesor cuesta unas 3.9 veces el entrenamiento del estudiante. Añadir épocas sube solo el lado del estudiante, así que una tercera época hace que ambos sean casi iguales. El texto generado también se puede reutilizar para otro estudiante sin costo extra del profesor.

</details>

3. ▢ Cuatro estudiantes de 1B comparten un pase de puntuación de un profesor de 7B sobre 100B de tokens. ¿Cuántos FLOPs de media por estudiante, y por qué es menor que para un solo estudiante?

<details markdown="1"><summary>Comprobación</summary>

Total: 1.4e21 + 4 × 6.0e20 = 3.8e21, así que 9.5e20 por estudiante, frente a 2.0e21 para un estudiante solo. El pase del profesor se paga una vez y se divide entre cuatro. Esto ignora el costo de almacenamiento y de ancho de banda de conservar los logits, que puede ser grande para una distribución de vocabulario completo en cada token.

</details>

4. ▢ ¿Qué afirmación sobre la cifra de 94B de tokens de Minitron es correcta?

    - a) Muestra que un estudiante desde cero necesita unos 94B de tokens cuando se destila de un profesor de 15B.
    - b) Muestra que un estudiante podado puede recuperarse con muchos menos tokens que entrenar desde cero.
    - c) Muestra que la destilación necesita unas cuarenta veces menos datos que el entrenamiento supervisado de ese estudiante.
    - d) Muestra que el costo de inferencia del profesor de 15B fue despreciable frente al entrenamiento del estudiante.

<details markdown="1"><summary>Comprobación</summary>

b). El estudiante de 8B se podó a partir del modelo de 15B, así que partió de los pesos del profesor. a) y c) tratan una inicialización podada como si fuera una destilación desde cero. La cifra de 40 veces compara con Nemotron-3 8B, un modelo distinto entrenado desde cero. d) no se muestra: el cálculo del costo de la familia, tal como está escrito, no incluye un término de forward pass del profesor, así que no dice nada sobre ese costo en un sentido ni en otro.

</details>

5. ▢ Intercalado de la etapa 4: planeas generar 20B de tokens de datos de instrucciones con un profesor alojado en una API y destilar un estudiante de 3B. Nombra dos cosas que la fórmula de FLOPs no te dice antes de comprometerte, una sobre el costo y una de la lección 13.

<details markdown="1"><summary>Comprobación</summary>

Sobre el costo, la generación está lejos de estar limitada por FLOPs, así que el precio de la API o las horas de reloj en tu hardware son la cifra real, y el rendimiento filtrado, no los 20B brutos, fija con cuántos tokens entrenas. De la lección 13, si los términos del proveedor permiten entrenar un modelo con sus salidas, a lo que ninguna estimación de cómputo responde.

</details>

## Prácticas en el mundo real

- [ ] Elige un profesor y un estudiante que podrías usar de forma realista. Anota ambos recuentos de parámetros y un presupuesto de tokens, y luego calcula el 6ND del estudiante, el 2ND del profesor y su razón.
- [ ] Abre la Tabla 2 y la Ecuación 9 del paper y marca cuál de los dos términos del profesor se aplica a tu proyecto, y en qué fila de la tabla estás.
- [ ] Mañana: sin apuntes, deriva la razón N_teacher / (3 × N_student) a partir de las dos fórmulas, y luego enuncia dos costos que deja fuera.

## Para profundizar

- [Dimensionar y medir](../reference/sizing-and-measuring.md)
- [Paper: "Distillation Scaling Laws", Busbridge et al., 2025](https://arxiv.org/abs/2502.08606), Ecuación 9 y Tablas 2 y 3
- [Paper: "Compact Language Models via Pruning and Knowledge Distillation", Muralidharan et al., 2024](https://arxiv.org/abs/2407.14679), Tabla 2 y sección 4.1
- [Preentrenamiento](../../pretraining/): el track de cómo se cuenta un presupuesto de cómputo de entrenamiento y qué compra un presupuesto de tokens
- [Recursos](../RESOURCES.md)

---

¿No termina de quedar claro? Vuelve a leer la fuente primaria de arriba, ya que esta lección la comprime y en la compresión es donde se escapa la comprensión. Consulta el [glosario](../GLOSSARY.md) por si algún término te resultó resbaladizo.

Si lo poco claro es la propia lección y no el material, eso es un defecto: [abre un issue](https://github.com/TokenCemetery/teach/issues).
