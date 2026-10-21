---
title: "10. Elegir los target modules"
description: "Solo atención es una ablación de 2021, no un valor por defecto"
type: lesson
---

# Lección 10. Elegir los target modules

**Vínculo con la misión:** Los target modules importan más que el rank, y la sabiduría recibida sobre ellos está desfasada. Este es un lugar donde puedes ser medible y mejor que el profesional medio.
**Fuente principal:** [Docs: "LoRA Without Regret", Hugging Face TRL](https://huggingface.co/docs/trl/main/en/lora_without_regret)
**Requisitos previos:** [Lección 2](0002-where-the-weights-live.md), [Lección 9](0009-rank-alpha-and-initialisation.md)

## Calentamiento

1. ▢ ¿Qué controla `α/r`, y qué controla `r` por sí solo?

<details markdown="1"><summary>Comprobación</summary>

`α/r` fija la escala de la contribución del adapter. `r` por sí solo fija su capacidad: lo compleja que puede ser una actualización que exprese.

</details>

2. ▢ ¿Qué subcapa contiene la mayoría de los parámetros de un bloque transformer?

<details markdown="1"><summary>Comprobación</summary>

El MLP, aproximadamente del 75 al 80% del bloque, porque la dimensión intermedia es varias veces el tamaño oculto y la grouped-query attention encoge dos de las cuatro proyecciones de atención.

</details>

3. ▢ ¿Qué garantiza una `B` inicializada en cero?

<details markdown="1"><summary>Comprobación</summary>

Que el modelo adaptado es idéntico al base model antes del primer paso del optimizador.

</details>

## Qué debes saber

### Lo que hizo el paper original, y por qué eso no es un consejo

El paper de LoRA adaptó solo las proyecciones de atención, en sus experimentos sobre todo `W_q` y `W_v`, y dejó el MLP en paz. Esa elección se propagó durante años de tutoriales, y de ahí viene `target_modules=["q_proj", "v_proj"]`.

Dos cosas que entender al respecto. Fue un hallazgo razonable bajo un presupuesto de memoria y en las tareas medidas. Y **no** es un resultado general sobre dónde debería ocurrir la adaptación. Tratar una ablación de 2021 como un valor por defecto es el error heredado más común de este campo.

### El argumento a favor del MLP

De la lección 2: el MLP contiene aproximadamente cuatro quintas partes de los parámetros de cada bloque. Existe un cuerpo sustancial de trabajo de interpretabilidad que trata las capas MLP como el lugar donde vive buena parte del conocimiento aprendido y de la detección de features de un modelo, mientras que la atención enruta información entre posiciones. Si tu tarea necesita que el modelo *sepa* o *clasifique* algo de forma distinta, los parámetros que lo codifican están desproporcionadamente en el MLP, y un adapter solo de atención no puede alcanzarlos.

### El valor por defecto actual

El trabajo reciente converge en una recomendación contundente: **adapta todas las capas lineales**, y dale al adapter suficiente rank. El texto de TRL sobre el resultado de "LoRA without regret" es explícito: aplicar LoRA a todas las capas lineales, incluido el MLP, con rank suficiente, cierra la brecha con el full fine-tuning en cargas de supervised fine-tuning, mientras que las configuraciones solo de atención no.

```text
# The modern default: let the library find every linear layer.
config := {rank: 64, alpha: 128, target_modules: "all-linear"}

# The explicit equivalent, for a Llama-style architecture.
config := {
    rank: 64,
    alpha: 128,
    target_modules: [
        "q_proj", "k_proj", "v_proj", "o_proj",
        "gate_proj", "up_proj", "down_proj",
    ],
}
```

`"all-linear"` es la más segura de las dos, porque no puede quedar obsoleta frente a una arquitectura cuyos nombres de módulo difieran de la lista que memorizaste. Su costo es que renuncias al control preciso y debes comprobar qué coincidió realmente.

Por qué esto es asequible ahora: de la lección 7, los parámetros del adapter son una parte despreciable de la memoria de entrenamiento. Restringir los target modules para ahorrar memoria era un intercambio real en 2021 y hoy es casi un no-intercambio. Lo que realmente intercambias es riesgo de sobreajuste en datasets pequeños.

### La decisión

| Situación | Targets | Razonamiento |
|---|---|---|
| Valor por defecto para una tarea real | Todas las capas lineales | Mejor calidad por unidad de esfuerzo; coincide con la evidencia actual |
| Dataset pequeño (< ~1k ejemplos) | Solo atención, rank bajo | Limitar a propósito la capacidad para limitar la memorización |
| Solo estilo o tono | Solo atención, rank bajo | Un cambio pequeño de comportamiento necesita una actualización pequeña |
| La tarea necesita discriminaciones nuevas | Debe incluir el MLP | Solo atención no puede alcanzar donde viven esas |
| Reproducir un paper | Exactamente lo que usó el paper | Si no, no lo estás reproduciendo |

### Dos módulos por los que pregunta la gente

**Embeddings y la cabeza de salida.** Normalmente se dejan en paz. Adaptarlos es caro en relación con el beneficio, y es el único lugar donde cambiar pesos puede desplazar el significado de cada token. La excepción genuina es añadir special tokens nuevos, lo que requiere tocar la tabla de embeddings y es una operación distinta de adaptarla.

**Términos de bias.** `bias="none"` es el ajuste estándar. Entrenar también los biases ( `"all"` o `"lora_only"`) es barato pero rara vez marca la diferencia entre una ejecución que funciona y una que falla, y complica la fusión.

### La comprobación que atrapa el error real

Imprime lo que coincidió, siempre:

```text
model := attach_adapter(base_model, config)
print(model.trainable_parameter_count())
print(first 8 parameter names containing "lora")
```

Un nombre de target module que no coincidió con nada produce un error o, según la versión, un modelo sin adapter alguno, que entrena, registra una pérdida y no aprende nada. Un conteo de parámetros entrenables que no concuerde con tu aritmética de la lección 8 es la advertencia más temprana posible.

## Práctica

1. ▢ ¿Por qué el paper original apuntó solo a la atención, y por qué eso no es un valor por defecto hoy?

<details markdown="1"><summary>Comprobación</summary>

Fue una ablación bajo un presupuesto de memoria ajustado en las tareas que midieron los autores, en una época en que limitar los parámetros entrenables importaba. Nunca fue una afirmación de que la atención sea donde pertenece la adaptación.

Hoy la memoria del adapter es despreciable, y la evidencia favorece cubrir todas las capas lineales con un rank adecuado.

</details>

2. ▢ Tu tarea requiere que el modelo distinga entre conceptos del dominio que ahora confunde. ¿Solo atención o todas las lineales?

<details markdown="1"><summary>Comprobación</summary>

Todas las lineales. Hacer discriminaciones nuevas significa cambiar la detección de features y las asociaciones almacenadas, que viven desproporcionadamente en el MLP. La atención enruta información; no es donde se codifica esa distinción.

</details>

3. ▢ Tienes 400 ejemplos de entrenamiento. Argumenta a favor de restringir los target modules.

<details markdown="1"><summary>Comprobación</summary>

Con 400 ejemplos, la capacidad es el riesgo y no la restricción. Un adapter completo de todas las lineales con un rank generoso puede memorizar el conjunto sin más: pérdida de entrenamiento cercana a cero, pérdida held-out subiendo y sin generalización.

Restringir a la atención con rank bajo es un límite de capacidad deliberado, que funciona como regularización. La mejor respuesta, si está disponible, es más datos.

</details>

4. ▢ ¿Qué cambio es más probable que suba la calidad en una tarea real con un dataset razonable?

    - a) Subir el rank del adapter de 16 a 64
    - b) Ampliar los targets a todas las capas lineales
    - c) Añadir dropout de LoRA de 0.05 a la ejecución
    - d) Entrenar un epoch completo adicional

<details markdown="1"><summary>Comprobación</summary>

**b)** Ampliar los targets a todas las capas lineales.

Pone al alcance de la adaptación aproximadamente cuatro veces más parámetros, incluido el MLP. Subir el rank añade capacidad dentro de las capas que ya alcanzas. El dropout regulariza en lugar de mejorar el ajuste. Un epoch extra arriesga sobreajuste sin añadir capacidad.

</details>

5. ▢ Configuras `target_modules=["c_attn"]` y la ejecución entrena con la pérdida apenas moviéndose. ¿Qué compruebas primero?

<details markdown="1"><summary>Comprobación</summary>

Si `c_attn` existe en este modelo. Es la proyección de atención fusionada de las arquitecturas al estilo GPT-2 y no existe en las de estilo Llama, que usan `q_proj`, `k_proj`, `v_proj` separadas.

Imprime los nombres de los módulos y luego `print_trainable_parameters()`. Un conteo de entrenables cercano a cero es la respuesta.

</details>

6. ▢ ¿Por qué `"all-linear"` es más seguro que una lista explícita de módulos?

<details markdown="1"><summary>Comprobación</summary>

Se resuelve contra el modelo cargado y no contra tu memoria, así que no puede pasar por alto capas en silencio en una arquitectura cuya nomenclatura difiera.

Su costo es la pérdida de precisión, así que verifica qué coincidió y ten en cuenta que puede incluir capas que preferirías dejar en paz.

</details>

## Prácticas en el mundo real

- [ ] Construye un adapter solo de atención y uno de todas las lineales con el mismo rank sobre el mismo modelo. Registra ambos conteos de parámetros entrenables y la proporción.
- [ ] Verifica qué módulos coincidió `"all-linear"` imprimiendo los nombres de parámetros del adapter. Anota cualquier cosa inesperada.
- [ ] Mañana: encuentra tres configuraciones de fine-tuning publicadas en línea y anota cuáles apuntan solo a la atención. Juzga si el autor lo eligió o lo heredó.

## Para profundizar

- [Docs: "LoRA Without Regret", Hugging Face TRL](https://huggingface.co/docs/trl/main/en/lora_without_regret)
- [Blog: "Practical Tips for Finetuning LLMs Using LoRA", Sebastian Raschka](https://magazine.sebastianraschka.com/p/practical-tips-for-finetuning-llms): las ablaciones de target modules
- [Hiperparámetros de LoRA](../reference/lora-hyperparameters.md)
- [Lección 11. Tu primer adapter](0011-your-first-adapter.md)

---

¿No termina de quedar claro? Vuelve a leer la fuente primaria de arriba, ya que esta lección la comprime y en la compresión es donde se escapa la comprensión. Consulta el [glosario](../GLOSSARY.md) por si algún término te resultó resbaladizo.

Si lo poco claro es la propia lección y no el material, eso es un defecto: [abre un issue](https://github.com/TokenCemetery/teach/issues).
