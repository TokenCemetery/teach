---
title: "1. Qué es realmente un base model"
description: "El modelo es una única función de siguiente token; base no es instruct"
type: lesson
---

# Lección 1. Qué es realmente un base model

**Vínculo con la misión:** No puedes juzgar si el fine-tuning es la respuesta correcta hasta que sepas exactamente qué hace el modelo cuando lo dejas en paz.
**Fuente principal:** [LLM Visualization, Brendan Bycroft](https://bbycroft.net/llm)
**Requisitos previos:** ninguno, esta es la primera lección.

## Qué debes saber

Un modelo de lenguaje es una función. Toma una secuencia de IDs de tokens y devuelve una puntuación para cada token de su vocabulario, que describe qué podría venir a continuación. Esa es toda la operación. El chat, las llamadas a herramientas, los rechazos, las trazas de razonamiento: todo está construido sobre ese único paso de siguiente token.

Esas puntuaciones en bruto se llaman **logits**. Softmax las convierte en una distribución de probabilidad. Un sampler elige un token de esa distribución, el token se añade a la secuencia y la función se ejecuta de nuevo. El texto aparece un token a la vez, y no ocurre nada más.

Dos consecuencias importan para todo lo que viene después.

**Los pesos no cambian en la inferencia.** Cuando un modelo parece recordar algo de más atrás en una conversación, el recuerdo son los tokens que están en su ventana de contexto, no un cambio en el modelo. El fine-tuning es lo único de este espacio de trabajo que altera los pesos, y ocurre offline, antes de servir.

**El muestreo no es el modelo.** Temperature, top-p y top-k remodelan la distribución después de que el modelo la ha producido. Si la calidad de la salida cambia al cambiar la temperature, has aprendido algo sobre tu sampler, no sobre tus pesos. Fija el muestreo antes de atribuir nada al entrenamiento.

### Base frente a instruct

Un modelo **base** se ha entrenado con un único objetivo: predecir el siguiente token sobre un corpus muy grande. No responde preguntas. Dado `What is the capital of France?` puede continuar con tres preguntas de examen más, porque así era el texto que lo rodeaba en sus datos de entrenamiento.

Un modelo **instruct** o **chat** es un base model que se ha entrenado más con pares de instrucciones y respuestas, lo que es supervised fine-tuning, y normalmente después con datos de preferencias humanas o de un modelo. El comportamiento de seguir instrucciones que das por sentado es una capa entrenada, no una propiedad de la arquitectura.

![La misma pregunta alimentando a un base model y a ese mismo base con instruction tuning añadido. El base continúa con más preguntas de examen; el ajustado produce una respuesta.](images/one-prompt-two-continuations.svg)

Un prompt, dos continuaciones, y la misma función de siguiente token debajo de ambas. El segundo recuadro es el primero más entrenamiento, que es donde vive la diferencia.

Desde cuál empiezas es una decisión real:

| Punto de partida | Heredas | Tienes que aportar |
|---|---|---|
| Base | Nada salvo la capacidad lingüística en bruto | Cada convención de formato y de comportamiento |
| Instruct | Formato, seguimiento de instrucciones, comportamiento de rechazo | Solo tu tarea, pero corres el riesgo de degradar lo que ya está ahí |

La mayor parte del fine-tuning con adapters empieza desde un modelo instruct, porque reconstruir el seguimiento de instrucciones desde cero con un dataset pequeño es un mal negocio. El costo es que tus datos de entrenamiento compiten ahora con el entrenamiento que ya hizo el proveedor, y esa competencia es de donde sale más adelante el [olvido catastrófico](../GLOSSARY.md).

### La señal de entrenamiento

Durante el entrenamiento se le muestra al modelo una secuencia real y se le puntúa según cuánta probabilidad asignó al token que realmente vino a continuación. Esa puntuación es la **pérdida de entropía cruzada**. Una pérdida baja significa que al modelo no le sorprendió la continuación real.

Quédate con una salvedad, porque la etapa 6 se construye sobre ella: la pérdida mide la sorpresa del siguiente token sobre texto que ya tienes. No mide si el modelo es útil.

## Práctica

1. ▢ Describe, en una frase y sin la palabra "entender", qué calcula un modelo de lenguaje.

<details markdown="1"><summary>Comprobación</summary>

Dada una secuencia de tokens, produce una puntuación para cada token del vocabulario que describe qué podría venir a continuación.

El instinto equivocado es describir la generación ("escribe texto") en lugar de la función. La generación es un bucle envuelto alrededor de la función, implementado fuera de los pesos. Mantener ambas cosas separadas es lo que te permite razonar sobre dónde vive un problema.

</details>

2. ▢ Le das a un modelo el mismo input dos veces y obtienes dos respuestas distintas. Nombra dos lugares de donde podría venir la diferencia, y di cuál involucra a los pesos.

<details markdown="1"><summary>Comprobación</summary>

El sampler (una temperature por encima de cero elige tokens distintos de la misma distribución) y el contexto (un system prompt distinto, o un historial de conversación que olvidaste que estaba ahí). Ninguno involucra a los pesos.

Los pesos están congelados en la inferencia. Si no los has cambiado, no pueden ser la explicación, y esto es lo primero que hay que descartar antes de concluir que un modelo es inconsistente.

</details>

3. ▢ Le das a un base model el prompt `Summarise this article:` seguido de un artículo, y produce otro artículo en lugar de un resumen. ¿Está roto el modelo?

<details markdown="1"><summary>Comprobación</summary>

No. Está haciendo exactamente su trabajo: continuar texto plausible. En su corpus de entrenamiento, a un artículo le sigue mucho más a menudo más artículo que un resumen.

Seguir instrucciones es un comportamiento entrenado. Esperarlo de un base model es el error inicial más común, y suele diagnosticarse mal como un mal modelo o un mal prompt.

</details>

4. ▢ ¿Cuál de estas cosas cambia el fine-tuning?

    - a) La temperature de muestreo usada en el momento de servir
    - b) Los valores numéricos almacenados dentro de los pesos del modelo
    - c) Los tokens presentes en la ventana de contexto del modelo
    - d) El tamaño del vocabulario con el que se construyó el modelo al principio

<details markdown="1"><summary>Comprobación</summary>

**b)** Los valores numéricos almacenados dentro de los pesos del modelo.

La temperature es un control del momento de servir. El contexto es input por petición. El tamaño del vocabulario lo fijan el tokenizer y la matriz de embeddings, y cambiarlo es una operación mucho más invasiva que el fine-tuning. Solo los valores de los pesos son lo que mueve el entrenamiento.

</details>

5. ▢ Da una razón para hacer fine-tuning de un modelo instruct en lugar de un base model, y una razón para hacer lo contrario.

<details markdown="1"><summary>Comprobación</summary>

Empieza desde instruct cuando quieras conservar el seguimiento de instrucciones y la utilidad general que no puedes permitirte reconstruir a partir de un dataset pequeño, que es casi siempre.

Empieza desde base cuando el formato de salida de tu tarea sea tan distinto del chat ordinario que el comportamiento de chat heredado interfiere de forma activa: salida estructurada rígida, una única etiqueta de clasificación o una notación de dominio donde el relleno conversacional es puro ruido.

</details>

## Prácticas en el mundo real

- [ ] Ejecuta cualquier modelo al que puedas llegar en local o a través de una API. Envía un prompt a temperature 0 dos veces, y luego a temperature 1 dos veces. Anota qué pareja coincidió y por qué.
- [ ] Busca en el Hugging Face Hub un modelo que tenga una variante base y una instruct. Lee ambas model cards y anota lo que la tarjeta del instruct afirma que se añadió.
- [ ] Mañana: dale a un base model una pregunta directa y registra lo que hace en lugar de responder. Guarda la salida. Reconocerás este fallo de nuevo en la etapa 6.

## Para profundizar

- [LLM Visualization, Brendan Bycroft](https://bbycroft.net/llm): recorre de punta a punta el camino de un solo token
- [The Illustrated Transformer, Jay Alammar](https://jalammar.github.io/illustrated-transformer/)
- [Glosario](../GLOSSARY.md): `fine-tuning` en este espacio de trabajo siempre significa el tipo de base congelado
- [Recursos](../RESOURCES.md)

---

¿No termina de quedar claro? Vuelve a leer la fuente primaria de arriba, ya que esta lección la comprime y en la compresión es donde se escapa la comprensión. Consulta el [glosario](../GLOSSARY.md) por si algún término te resultó resbaladizo.

Si lo poco claro es la propia lección y no el material, eso es un defecto: [abre un issue](https://github.com/TokenCemetery/teach/issues).
