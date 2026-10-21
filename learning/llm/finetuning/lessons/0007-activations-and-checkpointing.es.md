---
title: "7. Activaciones, batch size y checkpointing"
description: "Por qué una ejecución con un adapter aún se queda sin memoria"
type: lesson
---

# Lección 7. Activaciones, batch size y checkpointing

**Vínculo con la misión:** Los adapters eliminan el costo del optimizador pero no el de las activaciones, y por eso una ejecución de LoRA aún puede quedarse sin memoria. Esta es la parte que sorprende a la gente.
**Fuente principal:** [Paper: "Training Deep Nets with Sublinear Memory Cost", Chen et al., arXiv:1604.06174](https://arxiv.org/abs/1604.06174)
**Requisitos previos:** [Lección 6](0006-gradients-and-optimizer-state.md)

## Calentamiento

1. ▢ ¿Bytes por parámetro entrenable con AdamW, precisión mixta?

<details markdown="1"><summary>Comprobación</summary>

Dieciséis bytes: dos por los pesos en bf16, cuatro por la copia master en fp32, dos por el gradiente en bf16 y cuatro por cada uno de los dos momentos.

</details>

2. ▢ ¿Bytes por parámetro congelado?

<details markdown="1"><summary>Comprobación</summary>

Dos, en bf16, solo por el valor del peso. Sin gradiente, sin momentos, sin copia master.

</details>

3. ▢ ¿Por qué los momentos de AdamW no se pueden simplemente eliminar en los transformers?

<details markdown="1"><summary>Comprobación</summary>

Las magnitudes de los gradientes varían enormemente entre los parámetros de un transformer, y el segundo momento aporta el escalado del paso por parámetro que un único learning rate global no puede dar.

</details>

## Qué debes saber

Los gradientes y el estado del optimizador escalan con el **número de parámetros**. Las activaciones escalan con el **batch size y la longitud de secuencia**, y son casi independientes de cuántos parámetros sean entrenables. Congelar el base no ayuda aquí en absoluto.

### Por qué existen las activaciones

El backward pass necesita la entrada de cada capa para calcular el gradiente de esa capa. Así que el forward pass conserva sus resultados intermedios en lugar de descartarlos. Cada tensor conservado es aproximadamente:

```text
batch_size × sequence_length × hidden_size × bytes_per_element
```

por tensor, y un bloque transformer contiene una docena o así de ellos: tras cada normalización, cada proyección, la salida de la atención, el intermedio del MLP en su dimensión más ancha, y así sucesivamente. Multiplica por el número de capas.

Una cifra de trabajo aproximada para un bloque transformer en bf16, contando los tensores destacables:

```text
activations ≈ n_layers × batch × seq_len × hidden × ~20 bytes
```

Trata la constante como un punto de partida que hay que medir, no como una ley, porque se mueve con la implementación de la atención, la función de activación y si el framework fusiona operaciones. Lo que importa es la *forma* de la fórmula.

### Las consecuencias de la forma

**Lineal en el batch size.** Duplica el batch, duplica la memoria de activaciones. Es el control al que se recurre primero, y la gradient accumulation (lección 4) recupera el batch size efectivo gratis en términos de memoria.

**Lineal en la longitud de secuencia** para las activaciones almacenadas, y cuadrática para la matriz de puntuaciones de atención, a menos que uses un kernel de atención eficiente en memoria. Las implementaciones modernas como FlashAttention evitan materializar la matriz completa de `seq_len × seq_len`, lo que elimina el término cuadrático. Si sigues topándote con un crecimiento cuadrático en secuencias largas, la solución es la implementación de la atención, no el batch size.

Resuelto, para un modelo de 24 capas con tamaño oculto 2048, batch 4, longitud de secuencia 2048:

```text
24 × 4 × 2048 × 2048 × 20 bytes ≈ 8.0 GB
```

Ocho gigabytes de activaciones, frente a unos 2.2 GB de pesos congelados en bf16 y unas pocas decenas de megabytes de estado del adapter. **Las activaciones son ahora el costo dominante.** Este es el perfil de memoria de una ejecución típica con un adapter, y es lo opuesto al perfil del full fine-tuning de la lección 6.

### Gradient checkpointing

El intercambio que lo arregla: no almacenar la mayoría de las activaciones. Almacenar unas pocas y recalcular el resto durante el backward pass.

Conserva la entrada de cada bloque (un *checkpoint*), descarta todo lo que hay dentro y, cuando el backward pass llega a ese bloque, vuelve a ejecutar su forward pass para regenerar lo que hace falta. El almacenamiento pasa de ser aproximadamente lineal en la profundidad a ser aproximadamente su raíz cuadrada, a costa de un forward pass extra, normalmente entre un 20 y un 40% más lento por paso.

![Dos curvas sobre la profundidad. Sin checkpointing, las activaciones almacenadas suben en línea recta con el número de capas. Con checkpointing siguen la raíz cuadrada y se aplanan casi de inmediato. Con 24 capas las dos están separadas por unas cinco veces.](images/linear-against-square-root.svg)

La forma de ese intercambio es la razón de que sea casi un valor por defecto. Una línea recta y una raíz cuadrada apenas se separan con dos o tres capas, así que en un modelo de juguete la técnica parece inútil; la brecha es de unas cinco veces con las 24 capas del ejemplo resuelto y sigue ensanchándose, y el precio sigue siendo un forward pass extra por muy profundo que sea el modelo.

```python
model.gradient_checkpointing_enable()
model.config.use_cache = False  # incompatible with checkpointing during training
```

Esa segunda línea importa. La KV cache existe para acelerar la *generación* autorregresiva y no tiene ningún papel en el entrenamiento; dejarla activada junto con el checkpointing produce, en el mejor caso, avisos y, en el peor, memoria desperdiciada.

**El gradient checkpointing es casi un valor por defecto para el fine-tuning con adapters.** Recupera el mayor costo individual del perfil anterior, y la ralentización casi siempre merece la pena.

### Padding y packing

Cada secuencia de un batch se rellena hasta la longitud del miembro más largo del batch, y el padding consume memoria de activaciones sin aportar nada. Dos remedios:

- **Length grouping.** Agrupar en el mismo batch secuencias de tamaño parecido, para que haga falta menos padding.
- **Packing.** Concatenar ejemplos cortos en secuencias de longitud completa, eliminando el padding casi por completo.

El packing es una ganancia real de eficiencia en datasets de ejemplos cortos, y tiene un requisito de corrección: los ejemplos empaquetados juntos no deben atender a través de sus fronteras. Las implementaciones lo resuelven con reinicios de posición y una atención consciente de las fronteras. Si activas el packing, verifica que tu enmascarado de pérdida lo sobrevive: una secuencia empaquetada debe conservar intactas sus etiquetas `-100`, o la pérdida solo de la completion se convierte en silencio en pérdida de secuencia completa.

### El orden en que probar cosas

Cuando una ejecución no cabe, en orden de lo que cedes:

1. Activar el gradient checkpointing, que cuesta solo tiempo
2. Reducir el batch size por dispositivo y subir la gradient accumulation, que cuesta un poco de tiempo y no cambia nada estadísticamente
3. Reducir la longitud de secuencia, que cambia la tarea, así que primero revisa tu distribución de longitudes de tokens
4. Cuantizar el base model, que es la etapa 4 y cuesta algo de calidad
5. Reducir el rank del adapter, que cuesta capacidad y es lo que menos ahorra de todas las opciones de aquí

Ese último punto merece detenerse. El rank es el control al que la gente recurre primero y es casi el *menos* eficaz, porque los parámetros del adapter son una fracción minúscula del total. Reducir a la mitad el rank de un adapter de 4M de parámetros ahorra 32 MB.

## Práctica

1. ▢ ¿Cuáles de estos escalan con el número de parámetros entrenables y cuáles con el batch y la longitud de secuencia: gradientes, activaciones, momentos del optimizador, pesos congelados?

<details markdown="1"><summary>Comprobación</summary>

Número de parámetros entrenables: gradientes, momentos del optimizador. Solo el tamaño del modelo: pesos congelados. Batch y longitud de secuencia: activaciones.

Que las activaciones pertenezcan a un eje completamente distinto es el punto de esta lección, y la razón por la que los adapters no las resuelven.

</details>

2. ▢ Estima la memoria de activaciones para un modelo de 32 capas, tamaño oculto 4096, batch 2, longitud de secuencia 4096, bf16.

<details markdown="1"><summary>Comprobación</summary>

32 × 2 × 4096 × 4096 × 20 ≈ 21 GB.

Enorme en relación con un base de 7B congelado de 14 GB. Con gradient checkpointing esto baja aproximadamente un orden de magnitud, que es lo que hace posible la ejecución en un solo dispositivo.

</details>

3. ▢ Tu ejecución de LoRA se queda sin memoria. Un colega sugiere bajar el rank de 64 a 8. Evalúalo.

<details markdown="1"><summary>Comprobación</summary>

Ayudará apenas. Pasar de rank 64 a 8 en un modelo de 7B ahorra del orden de cien megabytes de estado y gradientes del adapter, frente a unas activaciones que se miden en gigabytes.

Activa primero el gradient checkpointing y recorta el batch size por dispositivo. El rank es una decisión de capacidad, y gastarla en memoria que no te faltaba es un mal intercambio.

</details>

4. ▢ ¿Por qué hay que desactivar `use_cache` cuando el gradient checkpointing está activado?

<details markdown="1"><summary>Comprobación</summary>

La KV cache almacena keys y values pasados para evitar recalcularlos durante la generación autorregresiva. El entrenamiento hace un único forward pass sobre una secuencia completa, así que la cache no aporta ningún beneficio, y entra en conflicto con la estrategia de recálculo del checkpointing mientras consume memoria.

</details>

5. ▢ ¿Qué intercambia el gradient checkpointing, en ambas direcciones?

<details markdown="1"><summary>Comprobación</summary>

Intercambia cómputo por memoria: el almacenamiento de activaciones pasa de ser aproximadamente lineal en la profundidad a ser aproximadamente su raíz cuadrada, a cambio de aproximadamente un forward pass extra por paso, normalmente entre un 20 y un 40% más lento.

</details>

6. ▢ Activas el packing y tu modelo empieza a producir respuestas a preguntas que nadie hizo. ¿Qué salió mal?

<details markdown="1"><summary>Comprobación</summary>

Lo más probable es que la máscara de pérdida no sobreviviera al packing, así que ahora se está entrenando con los tokens del prompt, o que los ejemplos atiendan a través de sus fronteras y aprendan que a una respuesta le sigue texto no relacionado.

Verifica que las etiquetas `-100` se conservan a lo largo del paso de packing y que la implementación es consciente de las fronteras. El packing es una optimización de eficiencia con una precondición de corrección.

</details>

## Prácticas en el mundo real

- [ ] Ejecuta un paso de entrenamiento con batch 1, luego con batch 2 y luego con batch 4, registrando la memoria pico cada vez. Confirma que la relación es lineal.
- [ ] Activa el gradient checkpointing y repite. Registra tanto la memoria ahorrada como los segundos por paso perdidos, y decide si aceptarías ese intercambio.
- [ ] Mañana: mide la distribución de longitudes de tokens de un dataset real con el tokenizer real. Encuentra el percentil 95. Esa, y no el máximo, es tu longitud de secuencia.

## Para profundizar

- [Paper: "Training Deep Nets with Sublinear Memory Cost", Chen et al., arXiv:1604.06174](https://arxiv.org/abs/1604.06174)
- [Paper: "FlashAttention: Fast and Memory-Efficient Exact Attention with IO-Awareness", Dao et al., arXiv:2205.14135](https://arxiv.org/abs/2205.14135)
- [Docs: Methods and tools for efficient training on a single GPU, Hugging Face](https://huggingface.co/docs/transformers/main/en/perf_train_gpu_one)
- [Presupuesto de memoria](../reference/memory-budget.md): ya está lo bastante completo para usarse

---

¿No termina de quedar claro? Vuelve a leer la fuente primaria de arriba, ya que esta lección la comprime y en la compresión es donde se escapa la comprensión. Consulta el [glosario](../GLOSSARY.md) por si algún término te resultó resbaladizo.

Si lo poco claro es la propia lección y no el material, eso es un defecto: [abre un issue](https://github.com/TokenCemetery/teach/issues).
