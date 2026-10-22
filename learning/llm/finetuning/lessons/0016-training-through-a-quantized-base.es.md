---
title: "16. Entrenar a través de un base cuantizado"
description: "Cómo fluyen los gradientes a través de pesos congelados de 4 bits"
type: lesson
---

# Lección 16. Entrenar a través de un base cuantizado

**Vínculo con la misión:** QLoRA en la práctica. Esta es también la única lección en la que el hardware que tienes cambia de verdad lo que tienes disponible.
**Fuente principal:** [Docs: bitsandbytes quantization, Hugging Face Transformers](https://huggingface.co/docs/transformers/main/en/quantization/bitsandbytes)
**Requisitos previos:** [Lección 15](0015-nf4-and-double-quantisation.md), [Lección 11](0011-your-first-adapter.md)

## Calentamiento

1. ▢ ¿Qué coloca NF4 en cuantiles normales, y por qué?

<details markdown="1"><summary>Comprobación</summary>

Sus 16 niveles representables, de modo que cada uno cubre la misma masa de probabilidad y no el mismo rango, a la medida de dónde se agrupan realmente los pesos distribuidos normalmente.

</details>

2. ▢ ¿Qué comprime la doble cuantización?

<details markdown="1"><summary>Comprobación</summary>

Las escalas de bloque de primer nivel, no los pesos. Aproximadamente 0.37 bits por parámetro.

</details>

3. ▢ Para un base de 4 bits con un adapter, ¿qué término de memoria domina?

<details markdown="1"><summary>Comprobación</summary>

Las activaciones. El base ha bajado a unos pocos gigabytes y el estado del adapter es una fracción de uno, así que el batch size y la longitud de secuencia deciden ahora si la ejecución cabe.

</details>

## Qué debes saber

### Cómo llega un gradiente al adapter a través de un base cuantizado congelado

La paradoja aparente: los pesos del base son enteros de 4 bits, y no puedes tomar de forma significativa un gradiente respecto a un entero de 4 bits. Entonces, ¿cómo funciona el entrenamiento?

Funciona porque **los pesos del base no se están entrenando.** Sigue una capa adaptada:

```text
forward:   h = W₀_dequant(x) + (α/r) · B A x
```

`W₀` se descuantiza a bf16 para el matmul y la copia descuantizada se descarta. El backward pass necesita el gradiente de la pérdida respecto a `A` y `B`, y para calcularlo necesita las *activaciones* que fluyen por la capa, que son bf16, y el gradiente que llega desde arriba, que también es bf16.

Los pesos congelados participan en el backward pass solo **dejando pasar el gradiente** hacia las capas anteriores. Eso requiere multiplicar por `W₀`, lo que requiere descuantizarlo de nuevo en lugar de derivar respecto a él. Nunca se almacena un gradiente para un peso del base, porque no se pide ninguno.

![Una capa adaptada dibujada dos veces con las mismas cuatro cajas. En el forward, la entrada llega tanto al base de 4 bits como al adapter en bf16 y se encuentran en la salida; en el backward, el gradiente recorre las mismas aristas a la inversa, pero solo el adapter tiene un gradiente almacenado.](images/a-constant-in-the-graph.svg)

Los dos paneles contienen las mismas cajas en los mismos lugares, y las aristas del backward son las del forward invertidas. El base aparece en ambos, trabajando en ambos, y sin conservar nada de ninguno.

Así que no hay nada exótico aquí. El base cuantizado es una constante en el grafo de cómputo. Hay que leerlo a alta precisión, pero nunca hay que actualizarlo, y actualizar es la parte cara.

El costo es cómputo: la descuantización ocurre en cada forward y de nuevo en el backward pass, en cada paso. QLoRA cambia velocidad por memoria, y es notablemente más lento por paso que un base en bf16.

### Preparar el modelo

```text
quant_config := {
    load_in_4bit: true,
    quant_type: "nf4",
    use_double_quant: true,
    compute_dtype: "bfloat16",
}

model := load_model("<base model>", quantization: quant_config)
model := prepare_for_quantized_training(model, gradient_checkpointing: true)

adapter_config := {rank: 32, alpha: 64, target_modules: "all-linear"}
model := attach_adapter(model, adapter_config)
print(model.trainable_parameter_count())
```

`prepare_model_for_kbit_training` hace varias cosas pequeñas necesarias: convierte las layer norms y la cabeza de salida a una precisión estable, activa el gradient checkpointing y los requisitos de gradiente de entrada, y se asegura de que no se cuantizó nada que deba mantenerse en mayor precisión. Saltárselo produce ejecuciones inestables o que fallan con errores de gradiente, y la causa no es evidente por el mensaje.

### Todo lo demás es igual

Rank, alpha, target modules, learning rate, schedule, partición held-out, probes de generación, las cuatro comprobaciones de la lección 11: todo idéntico. **QLoRA es LoRA con un base más barato.** No es un método distinto con su propio folclore de hiperparámetros, y tratarlo como si lo fuera es una fuente común de confusión.

El único ajuste que merece mención: como el base es más ruidoso, algunos profesionales usan algo más de rank del que usarían con un base en bf16, bajo la teoría de que el adapter tiene que compensar el error de cuantización además de aprender la tarea. Trátalo como una hipótesis que probar en tu tarea, no como una regla.

### Backends: lo que es realmente cierto

Esto merece cuidado, porque la versión que se repite mucho está desfasada.

`bitsandbytes` empezó siendo solo para CUDA, y durante varios años "QLoRA necesita una GPU de NVIDIA" fue simplemente exacto. Desde entonces la biblioteca ha pasado a una arquitectura multi-backend, con despacho para **CUDA (que cubre también AMD ROCm), CPU, Intel XPU, Intel Gaudi y Apple MPS**, junto con alternativas de PyTorch puro. Las operaciones de 4 bits, cuantizar y descuantizar y el producto matriz-vector de 4 bits, tienen implementaciones de backend más allá de CUDA, que se despachan cuando el tamaño de bloque es uno que el kernel compilado soporta y recurren a rutas genéricas más lentas en caso contrario.

Lo que se deduce para ti:

- **CUDA sigue siendo la ruta más completa y mejor optimizada.** Si la tienes, úsala, y espera que los números publicados sean reproducibles.
- **Los demás backends son viables y están mejorando, con salvedades.** La cobertura varía según la operación, el tamaño de bloque y la versión de la biblioteca. Espera pasos más lentos, y espera tener que comprobar si una configuración concreta llega a un kernel optimizado o a una alternativa.
- **Los optimizadores paginados son la pieza genuinamente específica de CUDA.** Dependen de la memoria unificada de NVIDIA para volcar el estado del optimizador a la memoria del host durante picos transitorios, evitando un fallo por falta de memoria en un pico. Eso es una característica de hardware, no un algoritmo portable. También importa menos en el entrenamiento con adapters, donde el estado del optimizador es minúsculo; su propósito original era el estado a escala del full fine-tuning.
- **Verifica contra tu versión instalada y no contra ningún documento.** Esta área ha cambiado repetidamente y volverá a cambiar. `bitsandbytes` tampoco es la única vía a los 4 bits; existen otros backends de cuantización con cobertura de hardware distinta.

Los conceptos de las lecciones 14 y 15, que son las escalas por bloques, los niveles en cuantiles normales, cuantizar las constantes y la precisión de almacenamiento frente a la de cómputo, son aritmética y son idénticos en cada backend. Solo difieren la disponibilidad de kernels y la velocidad.

### Qué esperar de la ejecución

| Frente a un base en bf16 | Efecto |
|---|---|
| Memoria fija | Aproximadamente 4× menor para el base |
| Tiempo por paso | Más lento, descuantización en cada forward y backward |
| Forma de la curva de pérdida | Muy parecida; puede quedar marginalmente más alta |
| Calidad final | Algo menor, depende de la tarea, así que mídela (lección 17) |

Y la regla de fusión de la lección 13 sigue vigente, más importante que nunca: **fusiona en el base de precisión completa, no en el cuantizado.** Entrena contra 4 bits, luego carga el base en bf16, aplica el adapter y fusiona ahí. Fusionar en pesos cuantizados añade una pérdida de recuantización que no tienes motivo para aceptar.

## Práctica

1. ▢ ¿Cómo pueden fluir los gradientes cuando los pesos del base son enteros de 4 bits?

<details markdown="1"><summary>Comprobación</summary>

Nunca se toma un gradiente respecto a un peso del base: son constantes congeladas. Los gradientes se toman respecto a `A` y `B`, que son de alta precisión.

Los pesos congelados hacen falta para *propagar* el gradiente a las capas anteriores, lo que requiere descuantizarlos para la multiplicación, no derivarlos.

</details>

2. ▢ ¿Qué hace `prepare_model_for_kbit_training`, y qué pasa si te lo saltas?

<details markdown="1"><summary>Comprobación</summary>

Convierte a una mayor precisión los módulos que necesitan estabilidad, como las layer norms y la cabeza de salida, activa el gradient checkpointing y los gradientes de entrada, y se asegura de que no se cuantizó nada que deba seguir en alta precisión.

Saltárselo suele dar una ejecución inestable o un error sobre gradientes no requeridos, con un mensaje que no apunta a la causa.

</details>

3. ▢ ¿Cuál es la parte específica de CUDA de QLoRA, y cuánto importa para el entrenamiento con adapters?

<details markdown="1"><summary>Comprobación</summary>

Los optimizadores paginados, que usan la memoria unificada de NVIDIA para volcar el estado del optimizador a la memoria del host durante los picos.

Importa poco para el entrenamiento con adapters, donde el estado del optimizador son megabytes. Se diseñó para el estado a escala del full fine-tuning, donde un pico transitorio acaba de verdad con la ejecución.

</details>

4. ▢ Un tutorial de 2023 afirma que el NF4 de 4 bits requiere una GPU de NVIDIA. ¿Sigue siendo correcto?

<details markdown="1"><summary>Comprobación</summary>

No como algo absoluto. `bitsandbytes` despacha ahora las operaciones de 4 bits entre CUDA/ROCm, CPU, Intel XPU, Intel Gaudi y Apple MPS, con alternativas de PyTorch donde no hay un kernel compilado disponible.

CUDA sigue siendo la ruta más completa y rápida, y la cobertura en otros backends varía según la operación, el tamaño de bloque y la versión. Así que la afirmación correcta es "CUDA es la ruta mejor soportada", no "CUDA es la única ruta", y verificas contra tu versión instalada y no contra ningún tutorial.

</details>

5. ▢ ¿Qué hiperparámetro debes replantear al pasar de LoRA a QLoRA?

    - a) El learning rate, que debe bajarse sustancialmente
    - b) El valor de alpha, que debe subirse para compensar
    - c) Ninguno, la precisión del base es un asunto aparte
    - d) El batch size, que debe subirse para mantener la estabilidad

<details markdown="1"><summary>Comprobación</summary>

**c)** Ninguno. La precisión del base es un asunto aparte.

QLoRA es LoRA con un base más barato. Algunos profesionales prueban con algo más de rank para absorber el ruido de cuantización, pero eso es una hipótesis que probar, no un cambio obligatorio.

</details>

6. ▢ Entrenaste contra un base de 4 bits y quieres un único modelo desplegable. Da los pasos en orden.

<details markdown="1"><summary>Comprobación</summary>

Carga el base en bf16 (no en 4 bits), aplica el adapter entrenado, fusiona, guarda junto con el tokenizer y cuantiza después el modelo fusionado solo si necesitas un artefacto cuantizado para servir.

Fusionar en el base de 4 bits exige descuantizar, sumar y recuantizar, y pierde calidad por nada.

</details>

## Prácticas en el mundo real

- [ ] Carga un base model en bf16 y en NF4. Registra la memoria de cada uno y calcula la proporción.
- [ ] Ejecuta el mismo trabajo corto de entrenamiento contra ambos bases. Registra los segundos por paso y la curva de pérdida, y anota cuál es más lento y por cuánto.
- [ ] Comprueba qué backend está usando realmente tu instalación de `bitsandbytes`, y si tu tamaño de bloque llega a un kernel optimizado o a una alternativa.
- [ ] Mañana: fusiona el adapter entrenado en 4 bits en el base en bf16 y verifica de forma greedy contra tus probes.

## Para profundizar

- [Docs: bitsandbytes quantization, Hugging Face Transformers](https://huggingface.co/docs/transformers/main/en/quantization/bitsandbytes)
- [Code: bitsandbytes, bitsandbytes-foundation](https://github.com/bitsandbytes-foundation/bitsandbytes): el directorio de backends es la autoridad sobre la cobertura
- [Paper: "QLoRA: Efficient Finetuning of Quantized LLMs", Dettmers et al., arXiv:2305.14314](https://arxiv.org/abs/2305.14314)
- [Lección 17. Lo que realmente cuesta QLoRA](0017-what-qlora-costs.md)

---

¿No termina de quedar claro? Vuelve a leer la fuente primaria de arriba, ya que esta lección la comprime y en la compresión es donde se escapa la comprensión. Consulta el [glosario](../GLOSSARY.md) por si algún término te resultó resbaladizo.

Si lo poco claro es la propia lección y no el material, eso es un defecto: [abre un issue](https://github.com/TokenCemetery/teach/issues).
