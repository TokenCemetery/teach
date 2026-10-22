---
title: "12. Leer código real de modelos"
description: "Dónde vive cada pieza derivada en una biblioteca de modelos de producción, y las desviaciones pequeñas y comunes respecto del paper original que conviene reconocer en lugar de dejar que te confundan"
type: lesson
---

# Lección 12. Leer código real de modelos

**Vínculo con la misión:** La etapa 5 es el tramo final: todo lo derivado a partir de tensores en bruto en las etapas 1 a 4 existe dentro de código real de producción, con otros nombres y con un puñado de desviaciones pequeñas y estándar respecto del paper original, y esta lección es cómo traducir entre lo que se construyó aquí y lo que realmente corre en la práctica.
**Fuente principal:** [Repo: transformers, Hugging Face](https://github.com/huggingface/transformers)
**Requisitos previos:** [Lección 11](0011-adamw-optimizer.md), [Scaled dot-product attention](../GLOSSARY.md)

## Calentamiento

1. ▢ ¿Qué sale mal al incorporar el weight decay al gradiente en el Adam original, y qué hace distinto AdamW?

<details markdown="1"><summary>Comprobación</summary>

Incorporado al gradiente, el weight decay se divide por el término de escalado adaptativo junto con todo lo demás, así que su encogimiento efectivo varía según el parámetro en lugar de aplicarse de manera uniforme. AdamW aplica el weight decay directamente a los pesos, sumado a la actualización por separado del término basado en el gradiente.

</details>

2. ▢ ¿Son los pesos de un bloque transformer los mismos que los de otro bloque de la pila? ¿Qué cuesta y qué compra eso?

<details markdown="1"><summary>Comprobación</summary>

No, cada bloque tiene sus propios parámetros, aprendidos de forma independiente, lo que cuesta número de parámetros más o menos linealmente con la profundidad pero deja que distintos bloques se especialicen de forma distinta en lugar de verse obligados a calcular una transformación idéntica a cada profundidad.

</details>

## Qué debes saber

### Las mismas piezas, con otros nombres

Un modelo de estilo GPT-2 en la biblioteca `transformers` de Hugging Face implementa todo lo que derivó este espacio de trabajo, solo que con sus propias convenciones de nombres. La atención vive en una clase como `GPT2Attention`, que calcula la misma operación de scaled dot-product de la lección 1, a menudo mediante una capa lineal fusionada que produce Q, K y V concatenadas y luego las separa, un detalle de eficiencia de multiplicación de matrices por lotes, no una operación distinta de las proyecciones separadas por head de la lección 2. La máscara causal (lección 3) aparece como un buffer precalculado y registrado que contiene una máscara triangular inferior, aplicada a las puntuaciones de atención antes del softmax exactamente como se derivó, en lugar de reconstruirse desde cero en cada llamada de forward: como la máscara depende solo de la longitud de la secuencia y no de los valores reales de entrada, calcularla una vez y reutilizarla (o recortarla) es una elección puramente de eficiencia, sin cambio alguno en el mecanismo en sí. Los embeddings de tokens y de posiciones aparecen como las tablas `wte` (word token embedding) y `wpe` (word position embedding) (lecciones 4 y 8); los bloques apilados viven en una `ModuleList` que se recorre con un bucle for en el método forward del modelo, igual que en la lección 7; y la proyección de salida es una capa lineal, comúnmente llamada `lm_head`, atada a los pesos de `wte` mediante una asignación explícita o una llamada a `tie_weights()`, exactamente el weight tying de la lección 8.

![Una correspondencia en dos columnas. A la izquierda, cinco piezas derivadas en este espacio de trabajo: la atención de las lecciones 1 y 2, la máscara causal de la lección 3, la codificación posicional de la lección 4, los bloques apilados de la lección 7, y el embedding y el weight tying de la lección 8. A la derecha, el nombre correspondiente que cada una toma en la biblioteca transformers de Hugging Face: GPT2Attention con una proyección fusionada de query, key y value, un buffer registrado triangular inferior, una tabla de posiciones aprendida wpe, una ModuleList de bloques recorrida en un bucle for, y wte atado a lm_head. Una línea conecta cada concepto de la izquierda con su nombre en código real de la derecha.](images/workspace-to-real-code-mapping.svg)

### Tres desviaciones pequeñas y estándar respecto del paper original

Casi todo modelo de producción moderno se aparta del paper original de las mismas pocas maneras pequeñas, y reconocerlas como implementaciones de conceptos ya cubiertos, y no como algo nuevo, es el sentido de esta lección. **Embedding de posición**: muchos modelos usan una tabla de posiciones aprendida (la alternativa de la lección 4 a la codificación sinusoidal) o embeddings rotatorios, en lugar de la fórmula sinusoidal del paper original. **Función de activación**: el bloque feed-forward (lección 6) suele usar GELU en lugar de la ReLU del paper original, el mismo shape de expandir y luego contraer, con una no linealidad distinta. **Colocación de la norm**: la mayoría de los modelos actuales usa pre-norm (la alternativa de la lección 5), colocando la layer norm antes de cada subcapa dentro de la rama residual, en lugar de la post-norm del paper original. Ninguna de estas cambia la arquitectura de fondo que derivó este espacio de trabajo; son las variaciones estándar que se encuentran en casi toda implementación real.

### El código de entrenamiento vive fuera de la clase del modelo

Las piezas de la etapa 4, la llamada a la pérdida de entropía cruzada, `loss.backward()` y el paso del optimizador, no forman parte de la propia clase del modelo en absoluto; viven en el script de entrenamiento o en una utilidad de entrenamiento (como el `Trainer` de Hugging Face, o un bucle propio como el de nanoGPT). La clase del modelo define el forward pass que produce los logits; todo lo relativo a convertir esos logits en un modelo entrenado vive un nivel más arriba, en el código que llama al modelo repetidamente y aplica a su alrededor la maquinaria de la etapa 4.

### Otra base de código, los mismos objetos matemáticos

llama.cpp, construido en C en lugar de Python y PyTorch, expresa las mismas operaciones, la atención, la codificación posicional (comúnmente rotatoria), la normalización (comúnmente RMSNorm, una variante simplificada de la layer norm de la lección 5) y un bloque feed-forward (comúnmente con una activación SwiGLU), no como clases `nn.Module` con un método `forward`, sino como llamadas explícitas que construyen un grafo de cómputo en `ggml`, la biblioteca de tensores que hay debajo. Las llamadas que construyen el grafo y el estilo de clase con método forward no se parecen en nada sobre la página, pero calculan los mismos objetos matemáticos idénticos que este espacio de trabajo derivó a partir de tensores en bruto; la diferencia está por completo en cómo se construye y se ejecuta el grafo de cómputo, no en lo que calcula.

## Práctica

1. ▢ Empareja cada uno de estos nombres de código real con la lección que derivó el concepto que implementa: `wte`, `wpe`, un buffer registrado de máscara triangular inferior, `lm_head` atado a los pesos de `wte`, una `ModuleList` de bloques.

<details markdown="1"><summary>Comprobación</summary>

`wte` (word token embedding): el embedding de entrada de la lección 8. `wpe` (word position embedding): la codificación posicional de la lección 4 (aquí, una tabla aprendida y no sinusoidal). El buffer registrado de la máscara: la máscara causal de la lección 3. `lm_head` atado a `wte`: el weight tying de la lección 8. La `ModuleList` de bloques: el apilado de la lección 7.

</details>

2. ▢ Nombra las tres desviaciones pequeñas y comunes respecto del paper original que se encuentran en la mayoría de las implementaciones reales modernas, y con la alternativa de qué lección se corresponde cada una.

<details markdown="1"><summary>Comprobación</summary>

Embeddings de posición aprendidos o rotatorios en lugar de sinusoidales (la alternativa aprendida de la lección 4, o una variante posterior como la rotatoria). GELU en lugar de ReLU en el bloque feed-forward (la no linealidad de la lección 6, cambiada por otra función, con el mismo shape de expandir y luego contraer). Colocación pre-norm en lugar de post-norm (la alternativa pre-norm de la lección 5 a la elección del paper original).

</details>

3. ▢ ¿Por qué aparece la máscara causal en el código real como un buffer precalculado y registrado y no se reconstruye en cada llamada de forward?

<details markdown="1"><summary>Pista</summary>

Considera de qué depende realmente la máscara.

</details>

<details markdown="1"><summary>Comprobación</summary>

La máscara depende solo de la longitud de la secuencia, nunca de los valores reales de entrada, así que puede calcularse una vez (comúnmente a la longitud máxima de secuencia que soporta el modelo) y reutilizarse o recortarse en cada llamada de forward, en lugar de reconstruirse desde cero cada vez. Esta es una elección puramente de eficiencia; el mecanismo de enmascarado en sí, sumado a las puntuaciones antes del softmax, no cambia respecto de la lección 3.

</details>

4. ▢ ¿En qué se diferencia mecánicamente el enfoque de llama.cpp para calcular la atención y el bloque feed-forward del forward pass de un `nn.Module` de PyTorch, aun calculando las mismas operaciones matemáticas de fondo?

<details markdown="1"><summary>Comprobación</summary>

llama.cpp construye un grafo de cómputo explícito en `ggml` mediante llamadas a funciones en C, en lugar de definir una clase con un método `forward` que PyTorch traza automáticamente mientras corre. El estilo de construcción del grafo se ve completamente distinto sobre la página, pero las operaciones que construye, la atención, la codificación posicional, la normalización, el bloque feed-forward, son los mismos objetos matemáticos que este espacio de trabajo derivó a partir de tensores en bruto.

</details>

5. ▢ ¿Qué afirmación es cierta sobre leer el código de un modelo real después de derivar la arquitectura desde cero?

    - a) Los modelos de producción reales implementan una arquitectura totalmente distinta de la que derivan el paper original y este espacio de trabajo
    - b) Las mismas piezas aparecen con otros nombres, con un puñado de desviaciones pequeñas y estándar (esquema de embedding de posición, función de activación, colocación de la norm) que conviene reconocer y no tratar como algo nuevo
    - c) El código de entrenamiento (pérdida, backward pass, optimizador) es siempre parte de la definición de la propia clase del modelo
    - d) llama.cpp calcula operaciones matemáticas fundamentalmente distintas de las de una implementación en PyTorch, ya que está escrito en C

<details markdown="1"><summary>Comprobación</summary>

**b)** Esa es exactamente la traducción que enseña esta lección. (a) es falsa: la arquitectura de fondo es la misma, solo que con otros nombres y otra configuración. (c) es falsa: el código de entrenamiento vive en un script o utilidad de entrenamiento aparte, no dentro de la propia clase del modelo. (d) es falsa: las operaciones son matemáticamente idénticas; solo difiere cómo se construye y se expresa el grafo de cómputo.

</details>

## Prácticas en el mundo real

- [ ] Abre la implementación de un modelo de estilo GPT-2 en la biblioteca `transformers` y encuentra su clase de atención, su máscara causal y su nomenclatura `wte`/`wpe`/`lm_head`, emparejando cada una con la lección que la derivó.
- [ ] Comprueba si ese mismo modelo usa pre-norm o post-norm, y GELU o ReLU, y anota cuál es cuál frente a la lista de desviaciones comunes de esta lección.
- [ ] Mañana: encuentra el script de entrenamiento (o el uso de `Trainer`) de un modelo al que tengas acceso, y localiza su cálculo de la pérdida, su llamada a `.backward()` y su paso del optimizador.

## Para profundizar

- [Repo: transformers, Hugging Face](https://github.com/huggingface/transformers)
- [Repo: nanoGPT, Karpathy](https://github.com/karpathy/nanoGPT)
- [Recursos](../RESOURCES.md)

---

¿No termina de quedar claro? Vuelve a leer la fuente primaria de arriba, ya que esta lección la comprime y en la compresión es donde se escapa la comprensión. Consulta el [glosario](../GLOSSARY.md) por si algún término te resultó resbaladizo.

Si lo poco claro es la propia lección y no el material, eso es un defecto: [abre un issue](https://github.com/TokenCemetery/teach/issues).
