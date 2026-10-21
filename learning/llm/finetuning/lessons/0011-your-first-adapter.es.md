---
title: "11. Tu primer adapter"
description: "Una ejecución que prueba el pipeline antes de probar cualquier otra cosa"
type: lesson
---

# Lección 11. Tu primer adapter

**Vínculo con la misión:** "Ejecutarlo" está en la misión. Todo lo anterior fue la lectura; esta es la ejecución.
**Fuente principal:** [Docs: SFTTrainer, Hugging Face TRL](https://huggingface.co/docs/trl/main/en/sft_trainer)
**Requisitos previos:** [Lección 3](0003-tokenizers-and-chat-templates.md), [Lección 9](0009-rank-alpha-and-initialisation.md), [Lección 10](0010-choosing-target-modules.md)

## Calentamiento

1. ▢ ¿Cuál es el valor por defecto moderno para los target modules, y por qué es asequible?

<details markdown="1"><summary>Comprobación</summary>

Todas las capas lineales, con un rank generoso. Los parámetros del adapter son despreciables frente a la memoria de activaciones, así que restringirlos ya no compra mucho.

</details>

2. ▢ ¿Qué línea de código atrapa un nombre de target module que no coincidió con nada?

<details markdown="1"><summary>Comprobación</summary>

`model.print_trainable_parameters()`. Un conteo cercano a cero significa que el adapter no se acopló a nada.

</details>

3. ▢ Entrenamiento o inferencia: ¿dónde pertenece `add_generation_prompt=True`?

<details markdown="1"><summary>Comprobación</summary>

Inferencia. En el entrenamiento el turno del asistente ya está en el texto, así que añadir el prompt duplica el marcador.

</details>

## Qué debes saber

### Elige lo más pequeño que pueda fallar de forma informativa

El propósito de tu primera ejecución **no** es un buen modelo. Es probar que el pipeline está bien conectado. Así que hazla lo bastante barata como para que un error cueste minutos:

- Un base model de la clase de 0.5B a 3B. Los modelos pequeños entrenan rápido y exponen los bugs de datos igual de bien que los grandes.
- Unos cientos de ejemplos. Suficientes para ver moverse la pérdida.
- `max_steps` en torno a 20 a 50, no epochs. Quieres que termine pronto.

Optimizar cualquier cosa antes de que el pipeline esté probado es esfuerzo perdido, y oculta qué cambio causó qué efecto.

### Una ejecución mínima

```text
dataset := load_dataset("<a small instruction dataset>", split: "train[:500]")

adapter_config := {
    rank: 16,
    alpha: 32,
    dropout: 0.05,
    adapt_bias: false,
    target_modules: "all-linear",
}

run_config := {
    output_dir: "runs/first-adapter",
    max_steps: 50,
    per_device_batch_size: 1,
    gradient_accumulation_steps: 8,      # effective batch size 8
    learning_rate: 2e-4,
    warmup_steps: 5,
    lr_schedule: "cosine",
    logging_steps: 1,                    # every step, for the first run
    max_length: 1024,
    gradient_checkpointing: true,
    precision: "bf16",
}

trainer := new_trainer(
    model: "<a small base model>",
    train_dataset: dataset,
    adapter_config: adapter_config,
    run_config: run_config,
)

trainer.train()
trainer.save("runs/first-adapter/final")
```

Dos notas sobre esta superficie de API. `SFTTrainer` acepta una *cadena* de modelo y lo cargará por ti. La longitud de secuencia es `max_length` en `SFTConfig`. Ambas cosas han cambiado entre versiones, así que **lee la documentación de la versión instalada en lugar de fiarte de este fragmento o de tu memoria.** Esa instrucción no es un formalismo; es la fuente más fiable de tardes perdidas de todo este espacio de trabajo.

### Precisión, hardware y lo que realmente varía

`bf16=True` requiere soporte de hardware para bfloat16, que está muy extendido en los aceleradores modernos pero no es universal. En dispositivos más antiguos puede que necesites fp16 con loss scaling, y en algunos backends fp32 completo es la única opción. El principio de la lección 5 no cambia; solo difieren los formatos disponibles.

De igual modo, el acelerador concreto que hay detrás de este script no forma parte del método. Los conceptos, la aritmética y los modos de fallo son idénticos en CUDA, ROCm, Intel, Apple Silicon y CPU. Lo que difiere es qué kernels están optimizados, qué precisiones se soportan y lo rápido que va un paso. Cuando un backend restringe de verdad el método, este espacio de trabajo lo dice de forma explícita; consulta la [lección 16](0016-training-through-a-quantized-base.md).

### Las cuatro comprobaciones, en orden

Ejecútalas antes de preocuparte por la curva de pérdida.

**1. ¿Existe el adapter?**

```python
trainer.model.print_trainable_parameters()
```

Compara con tu aritmética de la lección 8. Un conteo de cero, o uno que discrepe en más que el redondeo, significa parar y arreglar.

**2. ¿Son los datos lo que crees que son?**

```python
example = trainer.train_dataset[0]
print(repr(tokenizer.decode(example["input_ids"])))
labels = example["labels"]
print(sum(1 for l in labels if l != -100), "of", len(labels), "positions scored")
```

Decodifica un ejemplo de entrenamiento real y léelo. Esta comprobación atrapa los desajustes de template, los tokens de fin de turno ausentes, un bug de enmascarado y el truncamiento a mitad de respuesta: cuatro de las cinco causas más comunes de un mal fine-tune. **No te la saltes.** Son los diez segundos de más valor de todo el proceso.

**3. ¿Se mueve la pérdida?**

A lo largo de 50 pasos con `logging_steps=1`, la pérdida debería caer de forma visible. Una pérdida plana desde el primer paso significa que el adapter no está acoplado, que el learning rate es muy inferior al necesario o que no se está puntuando nada.

**4. ¿Puede sobreajustar dos ejemplos?**

La mejor prueba de humo disponible. Entrena con dos ejemplos durante cien pasos. La pérdida debería acercarse a cero. Si no puede memorizar dos ejemplos, el pipeline está roto, y lo has aprendido en dos minutos y no tras una ejecución de seis horas.

### Guarda lo que necesitarás para reproducirlo

El directorio del adapter es pequeño, normalmente de un dígito a unos pocos cientos de megabytes, y contiene solo los pesos del adapter más una configuración que registra el base model, el rank, alpha y los target modules. Es inútil sin ese base model exacto, así que registra el identificador del base model y su revisión junto a él.

Registra también las versiones de las bibliotecas. Una configuración que entrenó limpiamente hace seis meses puede no cargar igual, y "qué versión era esta" no se puede recuperar a posteriori.

## Práctica

1. ▢ Tienes 50,000 ejemplos y un base model grande disponible. ¿Por qué esa es la primera ejecución equivocada?

<details markdown="1"><summary>Comprobación</summary>

Porque el trabajo de la primera ejecución es probar el pipeline, y una ejecución larga y cara da la misma información que una corta y barata, solo que mucho más tarde y a un costo mayor.

Peor aún, si algo va mal lo descubres tras horas en lugar de minutos, y no puedes saber cuál de varios cambios importó.

</details>

2. ▢ La pérdida es completamente plana desde el primer paso. Nombra tres causas en el orden en que las comprobarías.

<details markdown="1"><summary>Comprobación</summary>

1. El adapter no se acopló a nada; comprueba `print_trainable_parameters()`.
2. Todas las etiquetas son `-100`, así que no se puntúa nada; comprueba el conteo de etiquetas en un ejemplo real.
3. El learning rate es órdenes de magnitud demasiado bajo; comprueba que está en torno a `1e-4`, no `1e-5` o menos.

Las tres se descartan con una línea, y por eso van antes que cualquier cosa sutil.

</details>

3. ▢ ¿Por qué decodificar un ejemplo de entrenamiento en lugar de fiarte del dataset?

<details markdown="1"><summary>Comprobación</summary>

Porque los fallos que importan son invisibles en el dataset y visibles en el texto decodificado: un chat template equivocado, un token de fin de turno ausente, tokens del prompt que debían enmascararse y no lo están, una respuesta truncada a mitad de frase por `max_length`.

Ninguno de ellos lanza un error. Todos producen una ejecución que parece estar bien y un modelo que no lo está.

</details>

4. ▢ Tu adapter no logra llevar la pérdida cerca de cero con dos ejemplos en cien pasos. ¿Qué te dice eso?

<details markdown="1"><summary>Comprobación</summary>

Que el pipeline está roto, no que la tarea sea difícil. Dos ejemplos son trivialmente memorizables por cualquier adapter que funcione.

Busca un adapter sin acoplar, etiquetas totalmente enmascaradas, un learning rate cercano a cero o un data collator que produce algo distinto de lo que esperas.

</details>

5. ▢ Tienes el directorio del adapter y nada más. ¿Puedes usarlo?

<details markdown="1"><summary>Comprobación</summary>

Solo si puedes identificar el base model exacto con el que se entrenó, que la configuración del adapter registra por nombre. Aplicado a un base distinto, incluso a otro checkpoint de la misma familia, el resultado es en el mejor caso degradado y en el peor un sinsentido.

Registra el identificador del base model, su revisión y las versiones de tus bibliotecas. Un adapter es un diff, y un diff necesita su base.

</details>

6. ▢ ¿Batch size efectivo para `per_device_train_batch_size=2`, `gradient_accumulation_steps=8`, en 4 dispositivos?

<details markdown="1"><summary>Comprobación</summary>

2 × 8 × 4 = 64.

Reporta este número, no el por dispositivo. Comparar ejecuciones por el batch size por dispositivo es una forma fiable de sacar una conclusión falsa.

</details>

## Prácticas en el mundo real

- [ ] Ejecuta la prueba de sobreajuste con dos ejemplos antes de cualquier entrenamiento real. Confirma que la pérdida se acerca a cero.
- [ ] Decodifica y lee entero un ejemplo de entrenamiento. Cuenta cuántas posiciones se puntúan frente a cuántas se enmascaran.
- [ ] Completa de punta a punta una ejecución de 50 pasos y guarda el adapter. Anota su tamaño en disco.
- [ ] Mañana: anota el identificador del base model, la revisión y cada versión de biblioteca, en un archivo junto al adapter.

## Para profundizar

- [Docs: SFTTrainer, Hugging Face TRL](https://huggingface.co/docs/trl/main/en/sft_trainer)
- [Docs: LoRA, Hugging Face PEFT](https://huggingface.co/docs/peft/main/en/developer_guides/lora)
- [Modos de fallo](../reference/failure-modes.md): mantenlo abierto durante la ejecución
- [Lección 12. Leer una ejecución de entrenamiento](0012-reading-a-training-run.md)

---

¿No termina de quedar claro? Vuelve a leer la fuente primaria de arriba, ya que esta lección la comprime y en la compresión es donde se escapa la comprensión. Consulta el [glosario](../GLOSSARY.md) por si algún término te resultó resbaladizo.

Si lo poco claro es la propia lección y no el material, eso es un defecto: [abre un issue](https://github.com/TokenCemetery/teach/issues).
