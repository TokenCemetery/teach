---
title: "12. Tensor parallelism: dividir las matrices de una capa"
description: "Elegir por qué eje dividir una matriz de pesos para que un bloque transformer completo necesite un solo all-reduce"
type: lesson
---

# Lección 12. Tensor parallelism: dividir las matrices de una capa

**Vínculo con la misión:** "Explicar qué reparten ZeRO/FSDP, por qué el data parallelism por sí solo se queda sin memoria antes de quedarse sin cómputo, y cuándo el tensor o el pipeline parallelism valen su costo de comunicación" es el cuarto punto de Cómo se ve el éxito. Esta lección cubre qué divide realmente el tensor parallelism y por qué; la Lección 13 cubre el pipeline parallelism, y la Lección 14 cubre cuándo cualquiera de los dos vale su costo.
**Fuente principal:** [Paper: "Efficient Large-Scale Language Model Training on GPU Clusters Using Megatron-LM", Narayanan et al., 2021](https://arxiv.org/abs/2104.04473)
**Requisitos previos:** [Lección 11](0011-activation-memory-and-zero-r.md)

## Calentamiento

1. ▢ La etapa 3 de ZeRO reparte los parámetros en reposo, pero reconstruye el tensor completo de parámetros bajo demanda antes del forward o el backward pass de una capa, mediante all-gather. Una vez reconstruidos los parámetros, ¿calcula cada dispositivo la misma capa completa, o cada dispositivo calcula una parte distinta de las matemáticas de la capa?

<details markdown="1"><summary>Comprobación</summary>

Cada dispositivo calcula la misma capa completa, usando su propia copia completa reconstruida de los parámetros de esa capa. ZeRO reparte dónde viven los parámetros en reposo; no divide entre dispositivos el cálculo de ninguna capa individual.

</details>

## Qué debes saber

### Dividir el cálculo, no solo dónde viven los pesos

El **tensor parallelism** adopta un enfoque distinto de todo lo de la etapa 5: en lugar de reconstruir los pesos completos de una capa en un solo dispositivo, divide las matrices de pesos de una capa individual entre dispositivos para que cada dispositivo solo tenga, y solo calcule con, su propia porción de la capa. Ningún dispositivo necesita nunca la matriz de pesos completa de una vez.

### Un ejemplo resuelto: el bloque MLP

El bloque MLP de un transformer calcula `Y = GeLU(XA)` seguido de `Z = Dropout(YB)`, dos multiplicaciones de matrices con una no linealidad en medio. Narayanan et al. describen la manera concreta en que Megatron divide esto para mantener la comunicación al mínimo: dividir la primera matriz de pesos `A` **por sus columnas**, `A = [A1, A2]`, de modo que cada dispositivo obtiene una porción de la salida completa y calculable de forma independiente, `Y1 = GeLU(XA1)` e `Y2 = GeLU(XA2)`, sin que haga falta sincronización entre los dos dispositivos para calcularlas. Esto funciona porque dividir por columnas divide la dimensión de *salida*, no la dimensión sobre la que se suma, así que la porción de `Y` de cada dispositivo ya es la respuesta verdadera y completa para sus columnas, y `GeLU`, aplicada elemento a elemento, se puede aplicar a cada porción completa de forma independiente.

La segunda matriz de pesos, `B`, se divide entonces **por sus filas** para encajar, `B = [B1; B2]`, de modo que cada dispositivo calcula `Yi @ Bi` usando solo su propia porción local de `Y` y de `B`. Esto da a cada dispositivo una suma parcial hacia la salida verdadera `Z`; las sumas parciales de los dos dispositivos se combinan con un único all-reduce, y solo entonces se aplica el dropout al resultado completo y correcto.

### Por qué columna y luego fila, y no al revés

Si `A` se dividiera en cambio por sus filas (dividiendo la dimensión sobre la que se suma, en lugar de la dimensión de salida), la porción de `X @ A` de cada dispositivo sería solo una **suma parcial** hacia los valores verdaderos previos a la activación, no una respuesta completa, ya que sumar solo sobre parte de la dimensión de contracción no da los números correctos para ninguna columna de salida. `GeLU` no se puede aplicar correctamente a una suma parcial y combinar después, porque `GeLU` es no lineal: `GeLU(a + b)` no es `GeLU(a) + GeLU(b)`. Dividir `A` por columnas evita tener que aplicar nunca una no linealidad a una suma parcial, que es exactamente la razón que dan Narayanan et al. para elegirlo. El emparejamiento columna y luego fila es lo que permite que todo el bloque MLP de dos matrices necesite **un solo** all-reduce, justo al final, en lugar de un paso de sincronización también entre las dos multiplicaciones de matrices.

### El mismo patrón se aplica a la atención

La atención multi-head ya tiene un lugar natural donde dividir: las proyecciones de query, key y value se particionan en paralelo por columnas, de modo que cada dispositivo maneja un subconjunto de cabezas de atención de forma independiente, sin necesitar coordinación entre dispositivos durante el cálculo de la atención en sí. La proyección de salida que sigue se divide entonces por sus filas para encajar, el mismo emparejamiento columna y luego fila que el bloque MLP, y necesita un all-reduce al final del bloque de atención.

## Práctica

1. ▢ El bloque MLP de un transformer se divide con `A` por sus columnas y `B` por sus filas, como describe esta lección. ¿Cuántas operaciones all-reduce necesita este esquema para todo el bloque, desde `X` hasta el `Z` final?

<details markdown="1"><summary>Comprobación</summary>

Una, justo después de la segunda multiplicación de matrices, para combinar la suma parcial de `Z` de cada dispositivo en el resultado completo. La división por columnas de `A` evita necesitar ninguna sincronización entre las dos multiplicaciones de matrices.

</details>

2. ▢ Si `A` se dividiera por sus filas en lugar de por sus columnas, ¿qué saldría mal al aplicar `GeLU` inmediatamente después de la primera multiplicación de matrices?

<details markdown="1"><summary>Pista</summary>

Pregúntate qué representa realmente el resultado local de cada dispositivo cuando la dimensión que se divide es aquella sobre la que se suma, en lugar de la dimensión de salida.

</details>

<details markdown="1"><summary>Comprobación</summary>

Cada dispositivo tendría solo una suma parcial hacia los valores verdaderos previos a la activación, no los valores completos, ya que en el cálculo local de cada dispositivo solo se incluyó parte de la dimensión de contracción. `GeLU` es no lineal, así que aplicarla a una suma parcial y combinar después los resultados no da la misma respuesta que aplicarla a la suma completa, lo que significa que haría falta un paso de sincronización antes de que `GeLU` pudiera ejecutarse correctamente siquiera.

</details>

3. ▢ En el bloque de atención, ¿cómo se dividen las proyecciones de query, key y value, y qué rasgo natural de la atención multi-head hace conveniente esa división?

<details markdown="1"><summary>Comprobación</summary>

Se dividen en paralelo por columnas, igual que se divide `A` en el bloque MLP. La atención multi-head ya calcula la atención de cada cabeza de forma independiente de las demás, así que asignar cabezas distintas (o grupos de cabezas) a dispositivos distintos no requiere coordinación durante el cálculo de la atención en sí, del mismo modo que dividir la dimensión de salida del MLP no la requería.

</details>

4. ▢ ¿Por qué el tensor parallelism, tal como lo describe esta lección, nunca necesita reconstruir la matriz de pesos completa de una capa en un solo dispositivo, a diferencia de la etapa 3 de ZeRO?

<details markdown="1"><summary>Comprobación</summary>

Porque cada dispositivo solo calcula con su propia porción de la matriz de pesos; la división por columnas y luego por filas se elige precisamente para que cada cálculo intermedio en cada dispositivo sea o bien un resultado completo e independiente (tras la división por columnas) o bien una suma parcial que se combina con un all-reduce (tras la división por filas), en lugar de exigir que la matriz completa exista en alguna parte.

</details>

## Prácticas en el mundo real

- [ ] Lee la descripción del tensor parallelism en el paper de Megatron-LM (enlazado arriba) y busca la figura que muestra las divisiones de los bloques MLP y de atención. Sigue, con tus propias palabras, dónde se sitúa cada operador `f` y `g` (la notación del paper para el par identidad frente a all-reduce en forward/backward) en el diagrama.
- [ ] Esboza en papel una matriz de pesos `A` de 4 filas por 2 columnas y una entrada `X` de 2 filas por 4 columnas, y calcula a mano cómo es `X @ A` cuando `A` se divide por columnas en dos piezas de 4 filas por 1 columna, frente a dividirla por filas en dos piezas de 2 filas por 4 columnas. Confirma qué división da a cada dispositivo una respuesta completa.
- [ ] Mañana: sin adelantarte, escribe una predicción de una oración para la Lección 13: si el tensor parallelism necesita un all-reduce por cada capa del transformer, ¿qué tipo de interconexión requeriría probablemente entre dispositivos, y esperarías que funcionara igual de bien entre dispositivos de racks de servidores físicamente distintos?

## Para profundizar

- [Paper: "Efficient Large-Scale Language Model Training on GPU Clusters Using Megatron-LM", Narayanan et al., 2021](https://arxiv.org/abs/2104.04473)
- [Recursos](../RESOURCES.md)

---

¿No termina de quedar claro? Vuelve a leer la fuente primaria de arriba, ya que esta lección la comprime y en la compresión es donde se escapa la comprensión. Consulta el [glosario](../GLOSSARY.md) por si algún término te resultó resbaladizo.

Si lo poco claro es la propia lección y no el material, eso es un defecto: [abre un issue](https://github.com/TokenCemetery/teach/issues).
