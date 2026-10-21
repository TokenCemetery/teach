---
title: "19. Elegir entre SFT, DPO, PPO y GRPO"
description: "Cada método se gana su costo añadido sobre el anterior solo cuando el más barato realmente no puede expresar el comportamiento objetivo"
type: lesson
---

# Lección 19. Elegir entre SFT, DPO, PPO y GRPO

**Vínculo con la misión:** "Dados los datos, el presupuesto y el comportamiento objetivo de un equipo, elegir entre SFT solo, DPO, RLHF-PPO y GRPO, y defender la elección frente a la que se descartó" es la decisión central de la misión, y esta lección es donde la contabilidad de costos de todo el arco se ensambla en un único marco.
**Fuente principal:** [Paper: "Direct Preference Optimization: Your Language Model is Secretly a Reward Model", Rafailov et al., 2023](https://arxiv.org/abs/2305.18290)
**Requisitos previos:** [Lección 18](0018-reward-hacking-after-the-fact.md)

## Calentamiento

1. ▢ ¿Qué es el sobrerrechazo, y por qué no puede detectarlo un benchmark de red-team solo con prompts inseguros?

<details markdown="1"><summary>Comprobación</summary>

Un modelo que rechaza un prompt que en realidad es seguro. Un benchmark de red-team construido solo con prompts inseguros no tiene prompts seguros que rechazar por error, así que no puede sacar a la luz este fallo concreto.

</details>

2. ▢ ¿Qué es el sesgo del juez, y qué recomienda comprobar `llm/evals` antes de fiarse de una brecha de puntuación que produjo?

<details markdown="1"><summary>Comprobación</summary>

Una distorsión sistemática en la puntuación de un juez LLM, como favorecer las respuestas más largas o la que se muestra primero. `llm/evals` recomienda comprobar la calibración del juez frente a estos sesgos conocidos antes de fiarse de una brecha de puntuación como evidencia de una mejora genuina.

</details>

## Qué debes saber

### Cada método cuesta más que el anterior, por una razón

Los cuatro enfoques de entrenamiento de este track forman una escalera aproximada, y cada uno añade costo solo donde el anterior se queda sin poder expresivo para el comportamiento objetivo:

**SFT solo (etapa 2)** es lo más barato: sin datos de preferencia, sin reward model, sin bucle de RL, solo imitar directamente ejemplos demostrados. Basta exactamente cuando el comportamiento objetivo puede especificarse por completo mostrando ejemplos de él: un formato de respuesta fijo, una habilidad estrecha y bien definida, un cambio de estilo. Todos los métodos posteriores de esta escalera siguen partiendo de un modelo SFT; la pregunta que plantea de verdad esta lección es cuánto más allá de SFT necesita llegar un comportamiento dado.

**DPO (etapa 5)** se gana su costo añadido sobre SFT solo cuando el comportamiento deseado no puede especificarse por completo con una demostración directa, pero *sí* puede especificarse comparando dos salidas candidatas, "esta por encima de aquella". Rafailov et al. construyen DPO específicamente para llegar a un modelo entrenado con preferencias a un costo cercano al del propio SFT: sin reward model aparte, sin función de valor, sin bucle de muestreo de RL, solo la policy y un modelo de referencia congelado (lección 10). Si hay datos de preferencia disponibles o recopilables y no hay una razón concreta para necesitar un reward model independiente y reutilizable, DPO es el siguiente paso natural después de SFT, no RLHF-PPO.

**RLHF-PPO (etapa 4)** se gana su costo sustancialmente mayor (la configuración de cuatro o cinco modelos de la lección 8) específicamente cuando merece la pena tener un reward model independiente por derecho propio: reutilizado para puntuar salidas fuera de la policy que entrenó contra él, inspeccionado de forma independiente, o iterado repetidamente a medida que llegan más comparaciones sobre la mejor policy actual, como describe el pipeline original de tres pasos de la lección 1. Elegir PPO en lugar de DPO sin una de estas razones es pagar por una maquinaria que un método más simple ya cubre.

**GRPO (etapa 6)** se gana su lugar por una puerta completamente distinta: las recompensas verificables. Donde DPO y PPO necesitan ambos juicios de preferencia, humanos o de IA, la ventaja relativa al grupo de GRPO funciona con cualquier puntuación por salida, incluida la salida de un verificador determinista (lección 12), lo que elimina por completo la necesidad de un reward model entrenado o de datos de preferencia humana en tareas como las matemáticas y el código, donde la corrección es comprobable. GRPO no es un PPO más barato en general; es la herramienta adecuada específicamente cuando la tarea aporta una recompensa verificable que PPO o DPO tendrían que aproximar de otro modo con un juicio entrenado.

### Defender una alternativa descartada, no solo una elección

"Defender la elección frente a la que se descartó", la propia formulación de la misión, significa nombrar qué método más barato se probó o se consideró primero y por qué se quedó corto, y no simplemente afirmar los beneficios del método elegido. Un equipo que elija PPO debería poder decir por qué no bastaba la recompensa implícita de DPO, concretamente (necesitar un reward model reutilizable, lo más frecuente). Un equipo que elija GRPO debería poder señalar la comprobación verificable con la que se construye su recompensa, y no simplemente citar los resultados de DeepSeek-R1 como licencia para usarlo en una tarea sin ninguna comprobación así disponible.

## Práctica

1. ▢ Un equipo quiere un modelo que responda siempre con un esquema JSON fijo para una tarea estrecha y bien definida. ¿Qué método de esta escalera es el punto de partida correcto, y por qué?

<details markdown="1"><summary>Comprobación</summary>

SFT solo. Este es exactamente el caso al que encaja un comportamiento fijo y totalmente demostrable: los ejemplos del formato correcto bastan para imitarlo directamente, sin necesidad de datos de preferencia ni de una señal de recompensa en absoluto.

</details>

2. ▢ Un equipo tiene datos de preferencia (pares de salidas con una marcada como mejor) y ninguna necesidad concreta de reutilizar un reward model fuera de la propia ejecución de entrenamiento. ¿Cuál de DPO y PPO es la opción por defecto más defendible, y por qué?

<details markdown="1"><summary>Comprobación</summary>

DPO. Llega a un resultado entrenado con preferencias parecido a un costo cercano al del propio SFT, y necesita solo la policy y un modelo de referencia congelado, sin reward model aparte ni bucle de RL que justificar a menos que algo concreto lo requiera.

</details>

3. ▢ Un equipo entrena un modelo para resolver problemas de programación competitiva, donde un compilador puede comprobar si el código generado pasa una suite de tests fija. ¿Qué método encaja especialmente bien con esta tarea, y qué lo hace concretamente una buena opción?

<details markdown="1"><summary>Comprobación</summary>

GRPO, emparejado con una recompensa verificable: el resultado de pasa/no pasa del compilador sobre la suite de tests es exactamente el tipo de puntuación determinista y comprobable que la ventaja relativa al grupo de GRPO puede usar directamente, sin necesidad de un reward model entrenado ni de datos de preferencia humana en absoluto.

</details>

4. ▢ Un equipo elige RLHF-PPO en lugar de DPO, alegando solo que "PPO es el método más establecido". Según esta lección, ¿es una defensa suficiente de la elección?

<details markdown="1"><summary>Comprobación</summary>

No. Defender una elección frente a la que se descartó significa nombrar una razón concreta por la que el enfoque más barato de DPO no habría bastado, como necesitar un reward model independiente que reutilizar o sobre el que iterar. Alegar solo que PPO está establecido no identifica qué le faltaba concretamente a DPO para esta tarea.

</details>

## Prácticas en el mundo real

- [ ] Busca un informe técnico de post-training publicado e identifica cuál de SFT, DPO, PPO o GRPO usó, y si da una razón para esa elección frente a una alternativa más barata.
- [ ] Para una tarea que conozcas (del trabajo, de un proyecto o hipotética), recórrela por la escalera de esta lección un paso a la vez: ¿bastaría SFT solo, y si no, por qué no; bastaría DPO, y si no, por qué no?
- [ ] Mañana: sin mirar adelante, escribe una predicción de una frase para la lección 20: dado que el arco de este track ha cubierto diez decisiones distintas (enmascarado de datos, diseño de la recompensa, compromisos de KL, ventaja relativa al grupo, recompensas verificables, medición del impuesto de alineación), ¿qué tendría que comprobar realmente la revisión de la receta de alineación terminada de otra persona, etapa por etapa?

## Para profundizar

- [Paper: "Direct Preference Optimization: Your Language Model is Secretly a Reward Model", Rafailov et al., 2023](https://arxiv.org/abs/2305.18290)
- [Recursos](../RESOURCES.md)

---

¿No termina de quedar claro? Vuelve a leer la fuente primaria de arriba, ya que esta lección la comprime y en la compresión es donde se escapa la comprensión. Consulta el [glosario](../GLOSSARY.md) por si algún término te resultó resbaladizo.

Si lo poco claro es la propia lección y no el material, eso es un defecto: [abre un issue](https://github.com/TokenCemetery/teach/issues).
