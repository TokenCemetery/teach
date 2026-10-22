---
title: "18. QAT para LLM"
description: "Qué cuesta el quantization-aware training en un LLM, qué recupera y cuándo basta la PTQ"
type: lesson
---

# Lección 18. QAT para LLM

**Vínculo con la misión:** La misión te pide decir cuándo el quantization-aware training se gana su costo frente a la cuantización post-entrenamiento, lo que requiere la etiqueta de precio, la ganancia medida y los casos en que la ganancia es cero.
**Fuente principal:** [Paper: "LLM-QAT: Data-Free Quantization Aware Training for Large Language Models", Liu et al., 2023](https://arxiv.org/abs/2305.17888)
**Requisitos previos:** [Lección 17](0017-fake-quantization-and-the-ste.md), [Quantization-aware training](../GLOSSARY.md), [Cuantización post-entrenamiento](../GLOSSARY.md), [Cuantización solo de pesos](../GLOSSARY.md)

## Calentamiento

1. ▢ La lección 9 comparó round-to-nearest a 8 bits y a 4 o menos. ¿En cuál de los dos aguanta, y por qué se resbala en el otro?

<details markdown="1"><summary>Comprobación</summary>

Aguanta a 8 bits, donde la rejilla tiene 256 niveles y el [error de redondeo](../GLOSSARY.md) por peso es pequeño. A 4 bits hay 16 niveles, cada peso puede desviarse hasta la mitad de un paso mucho mayor, y el redondeo simple no tiene nada que compense los errores. Esa brecha es el espacio en el que compiten GPTQ, AWQ y QAT.

</details>

2. ▢ ¿Por qué un bucle de entrenamiento no puede simplemente derivar a través de `round`, y qué hace la fake quantization al respecto?

<details markdown="1"><summary>Comprobación</summary>

La derivada de round es cero casi en todas partes, así que ningún gradiente llega a los pesos. La fake quantization mantiene una copia maestra en float, aplica cuantizar y descuantizar en el forward pass, y usa el [straight-through estimator](../GLOSSARY.md) para pasar el gradiente a través del paso de redondeo en el backward pass, con gradiente cero para los valores que el clamp recortó.

</details>

## Qué debes saber

### Qué cuesta el QAT en un LLM

El QAT es entrenamiento ordinario con fake quantization insertada, así que hereda los costos del entrenamiento. Nagel et al. los listan: entrenamiento más largo, necesidad de datos y búsqueda de hiperparámetros ([white paper](https://arxiv.org/abs/2106.08295), sección 4). Dos mediciones específicas de LLM lo concretan.

El equipo de PyTorch lo midió con su flujo de QAT de torchao en Llama3-8B, usando activaciones dinámicas por token en int8 con pesos agrupados en int4. Cada una de las 225 capas lineales recibe al menos una operación de fake quantize. En sus microbenchmarks el fine-tuning con QAT fue cerca de un 34% más lento que el full fine-tuning normal, y con activation checkpointing el uso de memoria subió en torno a 2.35 GB por GPU ([blog de PyTorch](https://pytorch.org/blog/quantization-aware-training/)). Un fine-tune de 20 horas pasa a ser de unas 27 horas. Son sus números en su configuración, así que trátalos como un orden de magnitud.

El segundo costo son los datos. Liu et al. señalan que los datos de entrenamiento originales de un LLM suelen no estar disponibles, y que los modelos suelen entrenarse en varias etapas (instruction tuning, aprendizaje por refuerzo) que serían difíciles de replicar durante el QAT. Su respuesta es el entrenamiento **data-free**: el modelo de precisión completa genera texto por sí mismo, con los primeros tokens elegidos de forma voraz y el resto muestreados, y el modelo cuantizado se entrena para igualar al modelo de precisión completa como su profesor. Informan de destilar los modelos cuantizados con solo un conjunto pequeño de 100,000 secuencias muestreadas, en un solo nodo de 8 GPU. Las secuencias se limitaron a 1,024 tokens, así que todo el conjunto es como mucho de unos 100 millones de tokens, una cifra que se sigue de sus dos números y no una que ellos enuncien.

### Qué recupera

LLM-QAT cuantiza pesos, activaciones y la KV cache, escrito como W-A-KV en bits. Su Tabla 1 informa del accuracy zero-shot promedio en siete tareas de sentido común. Para LLaMA-7B el promedio de precisión completa es 66.2.

| Configuración (W-A-KV) | RTN | SmoothQuant | LLM-QAT |
|---|---|---|---|
| 8-8-8 | 65.6 | 66.3 | 66.0 |
| 4-16-16 (solo pesos de 4 bits) | 63.0 | no informado | 64.4 |
| 4-8-4 | 41.2 | 43.2 | 60.7 |

A 8 bits todos los métodos quedan a un punto de la precisión completa. Los 4 bits solo de pesos ya aguantan con RTN, y QAT gana 1.4 puntos. La configuración de activaciones y KV cache de 4 bits es donde los métodos PTQ colapsan y QAT se mantiene a 5.5 puntos. En LLaMA-30B el promedio de precisión completa es 71.4: 4-8-4 da 42.5 con RTN y 40.7 con SmoothQuant frente a 69.9 de LLM-QAT, pero 4 bits solo de pesos da 70.1 con RTN, 70.3 con GPTQ y 70.1 con LLM-QAT. El propio resumen del paper coincide: todos los métodos funcionan bien a 8 bits, y cuando los pesos, las activaciones o la KV cache bajan de 8 bits los métodos PTQ pierden accuracy mientras LLM-QAT aguanta mucho mejor. Los baselines PTQ aquí son RTN, GPTQ y SmoothQuant. Los métodos de rotación de la lección 15 llegaron después y no están en esta comparación.

El blog de torchao informa del mismo patrón desde el lado del entrenamiento. En Llama3-8B con el esquema 8da4w, QAT recuperó el 96% de la degradación de accuracy normalizado en hellaswag en comparación con PTQ, y el 68% de la degradación de perplexity por palabra en wikitext. Con pesos de 2 bits, la perplexity por palabra en wikitext del modelo PTQ fue 603,336. Saltarse las primeras 3 y las últimas 2 capas la llevó a 6,766, y añadir QAT a eso la llevó a 30. Sin saltarse esas capas QAT fue mucho menos eficaz, así que QAT no rescató los 2 bits por sí solo.

### QLoRA es el vecino, no QAT

[QLoRA](https://arxiv.org/abs/2305.14314) también entrena un modelo cuantizado, pero hace backpropagation a través de un base congelado de 4 bits hacia adapters de bajo rango. Los pesos del base nunca cambian, así que el modelo no está aprendiendo a sobrevivir a su propio redondeo: la cuantización está ahí para que quepa el fine-tune en memoria. Este track no lo enseña. Lo enseña el track de finetuning, y su hoja [Presupuesto de memoria](../../finetuning/reference/memory-budget.md) cuenta los bytes.

### Cuándo basta la PTQ y cuándo compensa el QAT

| Situación | Evidencia | Por defecto |
|---|---|---|
| Pesos y activaciones de 8 bits | Tabla 1 de arriba; [Kurtic et al.](https://arxiv.org/abs/2411.02355) informan de FP8 efectivamente sin pérdida en los tamaños de Llama 3.1 e INT8 bien ajustado con una degradación del 1 al 3% | PTQ |
| Solo pesos de 4 bits, modelo grande | Fila de LLaMA-30B de arriba; Kurtic et al. encuentran que INT4 solo de pesos rivaliza con 8 bits | PTQ, luego medir |
| Solo pesos de 4 bits, modelo pequeño | LLaMA-7B: RTN pierde 3.2 puntos, QAT 1.8 | Probar PTQ, QAT si la brecha importa |
| Activaciones o KV cache de 4 bits | LLaMA-30B 4-8-4: RTN 42.5, LLM-QAT 69.9 | QAT, o las rotaciones de la lección 15, probadas |
| 3 bits o menos | Experimentos de torchao con 2 y 3 bits | QAT más conservar las capas sensibles |
| Modelo entrenado con muchísimos datos | [Kumar et al.](https://arxiv.org/abs/2411.04330) encuentran que la degradación de PTQ crece a medida que un modelo ve más datos | Probar PTQ pronto, esperar una brecha mayor |

El resultado de Kumar viene de modelos de hasta 1.7B parámetros entrenados con hasta 26B tokens, así que dice dónde mirar, no cuán grande es la brecha en un modelo grande. Cada fila es un valor por defecto que hay que probar contra tu propio baseline, no una regla.

## Práctica

1. ▢ A partir de los números de LLM-QAT de arriba para LLaMA-30B (precisión completa 71.4), ¿cuántos puntos pierde RTN con solo pesos de 4 bits, y cuántos con 4-8-4? ¿Vale el QAT su costo en cada caso?

<details markdown="1"><summary>Comprobación</summary>

RTN pierde 1.3 puntos con solo pesos de 4 bits (70.1) y 28.9 puntos con 4-8-4 (42.5). Con solo pesos, LLM-QAT también obtiene 70.1, así que no compra nada aquí y basta la PTQ. Con 4-8-4, LLM-QAT obtiene 69.9, 1.5 puntos por debajo de la precisión completa, así que el costo del entrenamiento compra casi todo el accuracy perdido. El QAT compensa cuando las activaciones o la KV cache pasan a 4 bits, no cuando solo lo hacen los pesos.

</details>

2. ▢ Un full fine-tune de tu modelo tarda 20 horas. Usando el microbenchmark de torchao, ¿cuánto tardaría aproximadamente la misma ejecución con QAT, y qué más crece?

<details markdown="1"><summary>Comprobación</summary>

Unas 27 horas (20 por 1.34 son 26.8). La memoria también crece, en unos 2.35 GB por GPU con el activation checkpointing activado, porque los pesos deben clonarse antes de aplicar la fake quantization. Es una configuración medida en Llama3-8B, así que tu ejecución puede diferir.

</details>

3. ▢ ¿Cuál de estas describe QLoRA?

    - a) Entrenar adapters a través de un modelo base congelado de 4 bits
    - b) Actualizar todos los pesos tras un paso de redondeo straight-through
    - c) Destilar el modelo con texto que él mismo generó
    - d) Cuantizar la KV cache mientras se hace fine-tuning del modelo

<details markdown="1"><summary>Comprobación</summary>

**a)** QLoRA mantiene congelado el base cuantizado y entrena pequeños adapters a través de él. (b) describe el QAT en general: los pesos cambian para sobrevivir al redondeo. (c) es la destilación data-free de LLM-QAT. (d) es algo que LLM-QAT también hace, y QLoRA no.

</details>

4. ▢ En el experimento de 2 bits de torchao, QAT llevó la perplexity por palabra en wikitext de 6,766 a 30. ¿Muestra eso que QAT por sí solo hace funcionar los pesos de 2 bits?

<details markdown="1"><summary>Pista</summary>

Mira qué se había hecho ya al modelo antes de añadir QAT, y qué ocurrió sin él.

</details>

<details markdown="1"><summary>Comprobación</summary>

No. Ese modelo ya tenía sus primeras 3 y últimas 2 capas sin cuantizar, un paso que costó tamaño del modelo y había llevado la perplexity de 603,336 a 6,766. Sin saltarse esas capas QAT fue mucho menos eficaz. Con muy pocos bits QAT es un ingrediente junto a conservar las capas sensibles en mayor precisión, que es una decisión sobre qué cuantizar además de sobre cómo.

</details>

5. ▢ El modelo int4 de PTQ de tu equipo está bien, pero el siguiente modelo que entrenas se entrena con tres veces más datos y su versión int4 obtiene una puntuación notablemente peor. ¿Qué sugiere la literatura de esta lección, y qué no deberías concluir?

<details markdown="1"><summary>Comprobación</summary>

Kumar et al. informan de que la degradación de la PTQ crece a medida que un modelo se entrena con más datos, así que una brecha mayor tras un entrenamiento más largo es lo que predice la evidencia de las leyes de escalado. Las opciones a probar son un ancho de bits mayor, un método PTQ más fuerte o QAT. No concluyas que es inevitable ni des su tamaño: su evidencia es para modelos de hasta 1.7B parámetros y 26B tokens, así que ejecuta la comparación en tu propio modelo frente al baseline de precisión completa.

</details>

## Prácticas en el mundo real

- [ ] Abre el blog de QAT de PyTorch y encuentra la frase sobre qué produce el paso convert en comparación con el flujo de PTQ. Anota qué implica eso para desplegar un modelo de QAT sobre los mismos kernels que uno de PTQ.
- [ ] Elige un modelo abierto cuantizado que podrías desplegar y lee su model card: ¿dice si los pesos vienen de PTQ o de QAT, y qué datos de calibración o de entrenamiento se usaron?
- [ ] Mañana: sin apuntes, escribe tres costos del QAT, las situaciones en que basta la PTQ y la situación en que el QAT compensa.

## Para profundizar

- [QAT y hardware](../reference/qat-and-hardware.md)
- [Blog: "Quantization-Aware Training for Large Language Models with PyTorch", PyTorch, 2024](https://pytorch.org/blog/quantization-aware-training/)
- [Paper: "QLoRA: Efficient Finetuning of Quantized LLMs", Dettmers et al., 2023](https://arxiv.org/abs/2305.14314)
- Finetuning: [Presupuesto de memoria](../../finetuning/reference/memory-budget.md)
- [Recursos](../RESOURCES.md)

---

¿No termina de quedar claro? Vuelve a leer la fuente primaria de arriba, ya que esta lección la comprime y en la compresión es donde se escapa la comprensión. Consulta el [glosario](../GLOSSARY.md) por si algún término te resultó resbaladizo.

Si lo poco claro es la propia lección y no el material, eso es un defecto: [abre un issue](https://github.com/TokenCemetery/teach/issues).
