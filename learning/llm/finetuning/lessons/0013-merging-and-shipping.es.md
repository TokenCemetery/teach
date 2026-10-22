---
title: "13. Fusionar, guardar y distribuir un adapter"
description: "Lo fusionado es exacto; un adapter es un diff que necesita su base"
type: lesson
---

# Lección 13. Fusionar, guardar y distribuir un adapter

**Vínculo con la misión:** Un adapter que solo existe en un script de entrenamiento no está distribuido. Esto cierra la etapa 3.
**Fuente principal:** [Docs: LoRA merging, Hugging Face PEFT](https://huggingface.co/docs/peft/main/en/developer_guides/lora)
**Requisitos previos:** [Lección 8](0008-the-low-rank-idea.md), [Lección 12](0012-reading-a-training-run.md)

## Calentamiento

1. ▢ ¿Qué checkpoint despliegas de una ejecución con sobreajuste?

<details markdown="1"><summary>Comprobación</summary>

El del mínimo de pérdida held-out, no el del último paso.

</details>

2. ▢ ¿Qué es lo que una curva de pérdida nunca puede mostrarte?

<details markdown="1"><summary>Comprobación</summary>

Si las generaciones son utilizables, y si las capacidades fuera de la distribución de tu tarea se han degradado. Ambas cosas necesitan generación real contra probes fijos.

</details>

3. ▢ Escribe la actualización de LoRA, con escalado.

<details markdown="1"><summary>Comprobación</summary>

`ΔW = (α/r) · BA`, sumada a la `W₀` congelada.

</details>

## Qué debes saber

### Qué hay en el directorio

Un adapter guardado contiene, aproximadamente:

```text
adapter_model.safetensors   # the A and B matrices, nothing else
adapter_config.json         # base model name, r, alpha, target_modules, task_type
README.md                   # generated model card
```

Pequeño, a menudo decenas de megabytes. E **incompleto por diseño**: es un diff, sin sentido sin el base model exacto nombrado en su configuración. Perder la pista del base, o de qué revisión de él, convierte el adapter en basura.

### Dos formas de distribuir

**Sin fusionar.** Carga el base, aplica el adapter en el momento de la carga.

```text
base := load_model("<base model>", dtype: "bfloat16")
model := load_adapter(base, "runs/first-adapter/final")
```

**Fusionado.** Pliega la actualización en los pesos y descarta la estructura del adapter.

```python
merged = model.merge_and_unload()
merged.save_pretrained("runs/first-adapter/merged")
tokenizer.save_pretrained("runs/first-adapter/merged")
```

Guarda el tokenizer al lado. Un directorio de modelo sin su tokenizer es un ticket de soporte esperando a ocurrir.

### Elegir entre ellas

| | Sin fusionar | Fusionado |
|---|---|---|
| Disco | El base una vez, adapters en megabytes | Una copia completa del modelo por tarea |
| Velocidad de inferencia | Dos matmuls pequeños extra por capa adaptada | Idéntica a la del base model |
| Varias tareas | Un base, muchos adapters, intercambiables | Un modelo completo cada una |
| Despliegue | El stack de serving debe soportar adapters | Cualquier stack que cargue un modelo |
| Composabilidad | Los adapters se pueden intercambiar o ponderar en tiempo de ejecución | Fijado en el momento de la fusión |

![Servir tres tareas. Fusionado, tres modelos completos contienen cada uno su propia copia de los pesos del base junto a un delta. Sin fusionar, una copia de los pesos del base se sitúa sobre los mismos tres deltas.](images/how-many-copies-of-the-base.svg)

Los tres deltas son los mismos tres en ambos lados. Lo que se multiplica es la parte sombreada, que es también la parte grande.

La regla práctica: **fusiona para un despliegue de un solo propósito, quédate sin fusionar cuando sirvas varias tareas desde un mismo base.** La lección 25 entra a fondo en el serving multi-adapter.

### Fusionar es exacto, con dos excepciones

Como la actualización es aditiva y lineal, la fusión es aritméticamente exacta. `W₀ + (α/r)BA` es la misma función que calculaba el modelo sin fusionar. No hay aproximación ni pérdida de calidad.

Salvo en dos casos, ambos dignos de conocerse:

**Fusionar en un base cuantizado tiene pérdidas.** Si el base es de 4 bits, añadir una actualización en bf16 exige descuantizar, sumar y volver a cuantizar, y el paso de recuantización pierde información. El orden correcto es: entrenar contra el base cuantizado, luego fusionar en el base de *precisión completa*, luego cuantizar el resultado fusionado si lo necesitas. Fusionar directamente en los pesos cuantizados degrada la calidad sin motivo. La etapa 4 vuelve sobre esto.

**El dropout cambia la escala efectiva.** `lora_dropout` está activo durante el entrenamiento e inactivo en la inferencia. Es el comportamiento estándar del dropout y normalmente inofensivo, pero significa que el peso fusionado refleja la ruta sin dropout, que es la correcta.

### Verifica la fusión

Nunca des nada por supuesto. Compara salidas:

```python
prompt = "<one of your fixed probes>"
# Greedy decoding, so any difference is the weights and not the sampler.
out_unmerged = unmerged_model.generate(**inputs, do_sample=False, max_new_tokens=64)
out_merged   = merged_model.generate(**inputs, do_sample=False, max_new_tokens=64)
assert tokenizer.decode(out_unmerged[0]) == tokenizer.decode(out_merged[0])
```

La decodificación greedy es el punto: con el muestreo activado, no puedes distinguir un bug de fusión de la aleatoriedad ordinaria. Pequeñas diferencias numéricas aún pueden causar una divergencia tarde en una generación larga, así que compara un número modesto de tokens e investiga una divergencia *temprana* y no una tardía.

### Varios adapters sobre un mismo base

PEFT puede mantener varios adapters y cambiar entre ellos, y puede combinarlos con pesos:

```python
model.load_adapter("path/to/adapter-a", adapter_name="a")
model.load_adapter("path/to/adapter-b", adapter_name="b")
model.set_adapter("a")                       # use one
model.add_weighted_adapter(["a", "b"], weights=[0.7, 0.3], adapter_name="blend")
```

La combinación ponderada es una herramienta genuinamente útil y no es magia: dos adapters entrenados de forma independiente en tareas distintas no se componen de forma fiable en uno que haga ambas. Merece la pena probarla y necesita medirse, no suponerse. Trata cualquier afirmación sobre aritmética de adapters como algo que verificar en tu propia tarea.

### Qué registrar

Todo lo necesario para reproducir y para depurar más adelante:

- Identificador del base model **y revisión**
- Configuración del adapter, literal
- Identidad del dataset y la partición exacta
- Seed, batch size efectivo, learning rate, schedule, pasos
- Qué checkpoint elegiste y por qué, es decir, el número held-out que lo justificó
- Versiones de las bibliotecas
- Resultados de la evaluación, incluidos los probes de regresión

Esto no es proceso por el proceso. Dentro de seis meses la pregunta "por qué el adapter viejo es mejor que el nuevo" solo se puede responder a partir de registros como estos.

## Práctica

1. ▢ ¿Por qué un archivo de adapter de 40 MB es inútil por sí solo?

<details markdown="1"><summary>Comprobación</summary>

Contiene solo las matrices `A` y `B`: un diff contra un conjunto concreto de pesos base. Sin ese base model y esa revisión exactos no se puede aplicar, y aplicado a un base casi igual se degrada en silencio.

</details>

2. ▢ Sirves cinco variantes con fine-tuning de un mismo base model. ¿Fusionas o no?

<details markdown="1"><summary>Comprobación</summary>

No fusiones. Sin fusionar significa una copia del base en memoria más cinco adapters pequeños, intercambiables por petición. Fusionado significa cinco copias completas del modelo.

El costo son dos matmuls pequeños extra por capa adaptada y un stack de serving que soporte adapters.

</details>

3. ▢ Entrenaste contra un base cuantizado a 4 bits. Describe el procedimiento correcto de fusión.

<details markdown="1"><summary>Comprobación</summary>

Carga el base en precisión completa, aplica el adapter, fusiona ahí y cuantiza después el modelo fusionado si necesitas un artefacto cuantizado.

Fusionar directamente en los pesos cuantizados exige descuantizar, sumar y recuantizar, y la recuantización pierde información sin ningún beneficio.

</details>

4. ▢ Fusionas y luego comparas generaciones con muestreo a temperature 0.8. Las salidas difieren. ¿Qué has aprendido?

<details markdown="1"><summary>Comprobación</summary>

Nada. Con el muestreo activado, es de esperar que las salidas difieran con independencia de que la fusión sea correcta.

Compara con decodificación greedy, donde cualquier divergencia es atribuible a los pesos. Luego investiga las divergencias tempranas; una diferencia que aparece solo tras muchos tokens puede ser deriva numérica ordinaria.

</details>

5. ▢ ¿Qué es cierto sobre fusionar un LoRA sin cuantizar?

    - a) Es exacto y no cuesta nada en el momento de la inferencia
    - b) Pierde un poco de calidad pero acelera la inferencia
    - c) Es exacto pero requiere más memoria en la inferencia
    - d) Tiene pérdidas y debería evitarse en el uso en producción

<details markdown="1"><summary>Comprobación</summary>

**a)** Es exacto y no cuesta nada en el momento de la inferencia.

La actualización es aditiva y lineal, así que se pliega en una matriz de pesos ordinaria, con la misma función, la misma memoria y sin matmuls extra. Esta propiedad es lo que distinguía a LoRA de los métodos de capas adapter anteriores.

</details>

6. ▢ Combinas un adapter de formato y un adapter de conocimiento del dominio con `add_weighted_adapter` y rinde menos que ambos. ¿Sorprende?

<details markdown="1"><summary>Comprobación</summary>

No. Las actualizaciones de bajo rank entrenadas de forma independiente ocupan subespacios no relacionados, y su suma ponderada no tiene garantía de ser una buena actualización para ninguna de las dos tareas, y mucho menos para ambas.

A veces funciona bien y merece la pena probarla. Nunca es algo que dar por supuesto; mídela contra cada adapter por separado.

</details>

## Prácticas en el mundo real

- [ ] Fusiona tu adapter y verifica con decodificación greedy sobre tus probes fijos. Confirma que las salidas coinciden.
- [ ] Compara los tamaños de directorio: adapter solo frente a modelo fusionado. Anota la proporción.
- [ ] Escribe el registro de ejecución descrito arriba, completo, para una ejecución real.
- [ ] Mañana: carga dos adapters sobre un mismo base y cambia entre ellos con el mismo prompt. Observa la diferencia.

## Para profundizar

- [Docs: LoRA merging, Hugging Face PEFT](https://huggingface.co/docs/peft/main/en/developer_guides/lora)
- [Docs: Model merging, Hugging Face PEFT](https://huggingface.co/docs/peft/main/en/developer_guides/model_merging)
- [Lección 25. Servir adapters](0025-serving-adapters.md)
- [Modos de fallo](../reference/failure-modes.md)

---

¿No termina de quedar claro? Vuelve a leer la fuente primaria de arriba, ya que esta lección la comprime y en la compresión es donde se escapa la comprensión. Consulta el [glosario](../GLOSSARY.md) por si algún término te resultó resbaladizo.

Si lo poco claro es la propia lección y no el material, eso es un defecto: [abre un issue](https://github.com/TokenCemetery/teach/issues).
