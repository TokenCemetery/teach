---
title: "3. Tokenizers y chat templates"
description: "Entrena con el renderizado que vas a servir"
type: lesson
---

# Lección 3. Tokenizers y chat templates

**Vínculo con la misión:** La causa más común de un fine-tune que entrena limpio y se comporta mal es un desajuste de template, no un hiperparámetro.
**Fuente principal:** [Docs: Chat Templates, Hugging Face Transformers](https://huggingface.co/docs/transformers/main/en/chat_templating)
**Requisitos previos:** [Lección 1](0001-what-a-base-model-is.md), [Lección 2](0002-where-the-weights-live.md)

## Calentamiento

1. ▢ ¿Cuál contiene más parámetros en un bloque moderno, la atención o el MLP?

<details markdown="1"><summary>Comprobación</summary>

El MLP, porque su dimensión intermedia es varias veces el tamaño oculto, y la grouped-query attention encoge todavía más `k_proj` y `v_proj`.

</details>

2. ▢ ¿Cómo encuentras los nombres reales de los módulos de un modelo?

<details markdown="1"><summary>Comprobación</summary>

Imprímelos desde el modelo cargado con `named_modules()`. Nunca los recuerdes de memoria; varían según la arquitectura.

</details>

3. ▢ ¿Qué mide la pérdida de entropía cruzada?

<details markdown="1"><summary>Comprobación</summary>

Cuánta probabilidad asignó el modelo al token que realmente vino a continuación. Una pérdida baja significa que la continuación verdadera no sorprendió al modelo.

</details>

## Qué debes saber

El modelo no ve texto. Ve enteros. El tokenizer es la correspondencia entre ambos, y es parte del modelo: el tokenizer de un checkpoint no es intercambiable con el de otro, ni siquiera dentro de la misma familia.

### Qué es un tokenizer

Los modelos modernos usan tokenización por subpalabras, normalmente byte-pair encoding. Entrenar el tokenizer significa partir de bytes y fusionar repetidamente el par adyacente más frecuente, lo que produce un vocabulario donde las palabras comunes son tokens únicos y las palabras raras se dividen en piezas.

Tres propiedades muerden en la práctica:

**Los tokens no son palabras.** ` the` (con un espacio inicial) y `the` son tokens distintos. Las mayúsculas cambian la tokenización. Un número como `1234` puede ser un token o cuatro, y por eso los modelos son malos en aritmética de formas que parecen arbitrarias.

**El conteo de tokens no es el conteo de caracteres.** El inglés promedia unos cuatro caracteres por token; el código, las escrituras no latinas y los formatos poco habituales son mucho menos eficientes. Tu presupuesto de longitud de secuencia de la lección 7 se mide en tokens, así que debes medir, no estimar.

**Los special tokens llevan estructura.** El inicio de secuencia, el fin de secuencia, el relleno (padding) y los marcadores de rol de más abajo son entradas ordinarias del vocabulario que el modelo ha aprendido a tratar como estructurales. Emitirlos a mano de forma incorrecta no es un error de sintaxis; es un cambio de distribución silencioso.

### Chat templates

Un chat model se entrenó con conversaciones renderizadas en una única secuencia plana de tokens mediante un formato de cadena específico y exacto. Por ejemplo, un modelo podría haberse entrenado con algo con esta forma:

```text
<|im_start|>system
You are helpful.<|im_end|>
<|im_start|>user
Hello<|im_end|>
<|im_start|>assistant
Hi.<|im_end|>
```

Otra familia usa marcadores totalmente distintos. El formato no es una convención que puedas aproximar: es la distribución a la que se ajustaron los pesos. Si te equivocas en un marcador, añades un salto de línea de más u omites el bloque de system cuando el modelo lo espera, el modelo pasa a operar ligeramente fuera de distribución. Seguirá produciendo texto fluido, y por eso mismo este fallo es difícil de detectar.

El template viene con el tokenizer, como una cadena Jinja. Úsalo en lugar de escribir tú el formato:

```text
tokenizer := load_tokenizer("<model>")
messages := [
    {role: "system", content: "You are helpful."},
    {role: "user", content: "Hello"},
]

# For inference: leaves the sequence ready for the model to continue.
prompt := tokenizer.render(messages, add_generation_prompt: true)

# For training: the assistant turn is already present, so no generation prompt.
full := tokenizer.render(messages + [{role: "assistant", content: "Hi."}])

print(exact(prompt))
print(exact(full))
```

Imprimir la cadena exacta, no una vista resumida, importa. La diferencia entre un template correcto y uno roto suele ser un solo carácter de espacio en blanco, y un print ordinario puede ocultarlo. En Python eso significa `repr`, no `print`, sobre la cadena.

### La única regla

**Entrena con el mismo renderizado que vas a servir.** Si haces fine-tuning con un formato casero y luego sirves a través del template oficial del modelo, has entrenado una distribución y desplegado otra. La curva de pérdida se verá bien. El modelo será sutilmente peor, y pasarás un día culpando al rank.

`add_generation_prompt` es donde esto falla con más frecuencia: pertenece a la inferencia, donde quieres que el modelo continúe como el asistente, y no a un ejemplo de entrenamiento, donde el texto del asistente es parte de la secuencia que se aprende.

![Una conversación renderizada dos veces como una tira de piezas de template. Ambas comparten las mismas tres piezas que terminan con el marcador del asistente; el renderizado de inferencia se detiene ahí, mientras que el de entrenamiento lleva una pieza más, el texto propio del asistente y su marcador de fin.](images/where-the-turn-begins.svg)

Ambos renderizados son las mismas piezas en los mismos lugares hasta el marcador del asistente. Lo que difiere es la pieza posterior, que es exactamente lo que el modelo debe producir en la inferencia y exactamente lo que debe aprender durante el entrenamiento.

### Los base models no tienen template

Si el tokenizer de un base model no tiene chat template, eso no es un bug, porque no hay formato de conversación que preservar. Eres tú quien elige el formato, así que elige uno, anótalo y úsalo de forma idéntica en el entrenamiento y en el serving.

## Práctica

1. ▢ ¿Por qué no puedes intercambiar un tokenizer entre dos checkpoints de la misma familia de modelos?

<details markdown="1"><summary>Comprobación</summary>

Los IDs de tokens indexan directamente la matriz de embeddings. Un vocabulario distinto asigna el mismo entero a una fila distinta, así que cada input se traduce mal en silencio. La salida es un sinsentido fluido, o un fallo si los tamaños de vocabulario difieren.

</details>

2. ▢ Estás construyendo un ejemplo de entrenamiento. ¿`add_generation_prompt` debe ser `True` o `False`, y por qué?

<details markdown="1"><summary>Comprobación</summary>

`False`. El generation prompt es el marcador de apertura que le dice al modelo "ahora habla el asistente", lo cual es útil en la inferencia, cuando el turno del asistente aún no existe. En el entrenamiento el turno del asistente está presente en el texto, así que añadir el prompt duplica el marcador y desplaza la secuencia fuera del formato que el modelo conoce.

</details>

3. ▢ Tu fine-tune entrena hasta una pérdida baja, pero en el momento de servir el modelo divaga más allá del final de su respuesta en lugar de detenerse. Nombra la causa más probable.

<details markdown="1"><summary>Comprobación</summary>

El token de fin de turno faltaba en tus ejemplos de entrenamiento, así que el modelo nunca aprendió que las respuestas terminan.

La pérdida no puede detectar esto: predecir una continuación fluida es exactamente lo que se recompensó al modelo con tus datos. Es un bug de construcción de datos que solo revela una generación real, y es una de las razones por las que la lección 24 insiste en generar y no solo en puntuar.

</details>

4. ▢ Un prompt tiene 700 palabras en inglés. ¿Cuántos tokens son aproximadamente, y confiarías en esa estimación para un presupuesto de entrenamiento?

<details markdown="1"><summary>Comprobación</summary>

Aproximadamente de 900 a 1000 tokens, tomando unos 1.3 tokens por palabra en inglés. No, no confiarías en ella: la proporción se mueve de forma sustancial con el código, el JSON, las escrituras no latinas y los formatos poco habituales, todos ellos comunes en los datos de fine-tuning.

Mide la distribución real con el tokenizer real. La lección 7 convierte esa distribución en un número de memoria.

</details>

5. ▢ ¿Cuál de estas cosas es segura de cambiar entre el entrenamiento y el serving?

    - a) La cadena exacta del chat template usado
    - b) El tokenizer que viene con el modelo
    - c) La temperature de muestreo usada en la generación
    - d) El special token que marca el fin de un turno

<details markdown="1"><summary>Comprobación</summary>

**c)** La temperature de muestreo usada en la generación.

La temperature se aplica después de que el modelo produce su distribución, así que es una decisión de serving. Las otras tres definen la distribución a la que se ajustaron los pesos; cambiar cualquiera de ellas significa servir un problema distinto del que entrenaste.

</details>

## Prácticas en el mundo real

- [ ] Toma un modelo y renderiza un template con la llamada real de chat template de tu biblioteca (p. ej. `apply_chat_template(..., tokenize=False)` en Transformers), imprimiendo la cadena exacta con los espacios en blanco incluidos (p. ej. `repr` de Python). Cópiala en tus notas.
- [ ] Tokeniza el mismo párrafo en dos familias de modelos distintas y compara los conteos de tokens. Luego tokeniza un bloque de JSON y compara de nuevo.
- [ ] Mañana: rompe un template a propósito quitando el marcador de fin de turno y luego haz un prompt al modelo. Observa lo que hace. Ese es el fallo que estás aprendiendo a reconocer.

## Para profundizar

- [Docs: Chat Templates, Hugging Face Transformers](https://huggingface.co/docs/transformers/main/en/chat_templating)
- [Code: minbpe, Andrej Karpathy](https://github.com/karpathy/minbpe): byte-pair encoding en forma legible
- [Modos de fallo](../reference/failure-modes.md): el desajuste de template aparece ahí
- [Lección 21. Construir el dataset](0021-building-the-dataset.md)

---

¿No termina de quedar claro? Vuelve a leer la fuente primaria de arriba, ya que esta lección la comprime y en la compresión es donde se escapa la comprensión. Consulta el [glosario](../GLOSSARY.md) por si algún término te resultó resbaladizo.

Si lo poco claro es la propia lección y no el material, eso es un defecto: [abre un issue](https://github.com/TokenCemetery/teach/issues).
