---
title: "1. Qué aporta el post-training"
description: "Un modelo alineado 100 veces más pequeño superó a un modelo base sin procesar en hacer lo que los usuarios realmente querían"
type: lesson
---

# Lección 1. Qué aporta el post-training

**Vínculo con la misión:** "Dados los datos, el presupuesto y el comportamiento objetivo de un equipo, elegir entre SFT solo, DPO, RLHF-PPO y GRPO, y defender la elección" es la decisión central de la misión, y empieza por saber qué problema resuelve el post-training que el preentrenamiento por sí solo no resuelve.
**Fuente principal:** [Paper: "Training language models to follow instructions with human feedback", Ouyang et al., 2022](https://arxiv.org/abs/2203.02155)
**Requisitos previos:** ninguno

## Qué debes saber

### Un modelo base no es automáticamente un buen asistente

Un modelo base preentrenado, producto de todo el arco de `llm/pretraining`, se entrena para predecir los tokens siguientes más probables según la distribución de texto que vio. Eso no es lo mismo que seguir las instrucciones reales de un usuario, y hacer más grande un modelo base no cierra por sí solo esa brecha. Ouyang et al. lo dicen sin rodeos: "hacer más grandes los modelos de lenguaje no los hace inherentemente mejores para seguir la intención del usuario". Un modelo base grande puede producir salidas falsas, poco útiles o simplemente distintas de lo que se pidió, no porque le falte capacidad, sino porque nada en el preentrenamiento lo entrenó específicamente para usar esa capacidad como quiere el usuario.

### El resultado principal

El resultado central de Ouyang et al. hace concreto el tamaño de esta brecha: en evaluaciones humanas, las salidas de su modelo **InstructGPT** de 1.3 mil millones de parámetros se preferían a las del modelo GPT-3 de 175 mil millones de parámetros del que partía, pese a tener unas 100 veces menos parámetros. El post-training no hizo al modelo más grande ni más inteligente en ningún sentido bruto; cambió hacia dónde apuntaba la capacidad que el modelo ya tenía, y esa puntería importó más a los evaluadores humanos que otros dos órdenes de magnitud de escala.

### El pipeline de tres pasos

La receta de Ouyang et al., que sigue siendo la forma de referencia frente a la que se describe la mayor parte del RLHF posterior, tiene tres pasos:

1. **Recopilar demostraciones, entrenar una policy supervisada.** Anotadores humanos escriben ejemplos del comportamiento deseado para una gama de prompts; el modelo base se ajusta con ellos mediante aprendizaje supervisado ordinario. Este paso es **SFT** (supervised fine-tuning), el tema de la etapa 2.
2. **Recopilar comparaciones, entrenar un reward model.** Los anotadores ordenan varias salidas del modelo SFT para el mismo prompt; un modelo aparte, el **reward model**, se entrena para predecir qué salida preferiría una persona. Este es el tema de la etapa 3.
3. **Optimizar la policy contra el reward model con PPO.** El modelo SFT se ajusta aún más con aprendizaje por refuerzo, tratando la puntuación del reward model como la señal de recompensa que hay que maximizar. Este es el tema de la etapa 4, y los pasos 2 y 3 pueden repetirse, recopilando más comparaciones sobre la mejor policy actual para entrenar a su vez un nuevo reward model y una nueva policy.

### El impuesto de alineación, presentado

El post-training no está libre de costo ni cuando funciona. Ouyang et al. encontraron que sus modelos alineados rendían ligeramente peor en algunos benchmarks públicos de NLP (un benchmark de comprensión lectora, uno de razonamiento discreto, uno de sentido común y uno de traducción, entre otros) que el modelo base original. Lo llaman **impuesto de alineación (alignment tax)**: un costo real y medido para ciertas capacidades, pagado a cambio de un comportamiento que las personas preferían en conjunto. También encontraron un arreglo parcial: mezclar las actualizaciones de PPO con actualizaciones que aumentan la verosimilitud de los datos de preentrenamiento originales (lo que llaman **PPO-ptx**) recuperó buena parte del rendimiento perdido sin renunciar a las ganancias de preferencia para las que se construyó el post-training. El impuesto no es fijo ni inevitable; es un compromiso medido que técnicas posteriores pueden pagar en parte.

### El panorama que viene

SFT solo (etapa 2) es el paso más barato y ya cambia mucho el comportamiento. El modelado de recompensa y RLHF con PPO (etapas 3 y 4) añaden encima una segunda fase de aprendizaje por refuerzo, con un costo y una complejidad añadidos reales. Direct Preference Optimization (etapa 5) busca más adelante un resultado parecido sin un reward model aparte ni un bucle de RL. GRPO (etapa 6) adapta el enfoque de RL a tareas con una respuesta verificable y comprobable, como las matemáticas o el código, en lugar de un juicio de preferencia humana. El ajuste específico de seguridad (etapa 8) aplica la misma familia de técnicas a un objetivo distinto. Cada una de estas es una respuesta distinta a la misma pregunta de fondo que abrió esta lección: cómo se apunta la capacidad que ya tiene un modelo hacia lo que una persona realmente quiere, y a qué costo.

## Práctica

1. ▢ El modelo de 1.3 mil millones de parámetros de InstructGPT se prefirió al modelo GPT-3 de 175 mil millones de parámetros en evaluaciones humanas. ¿Qué argumenta este resultado sobre la relación entre el número bruto de parámetros y ser bueno siguiendo la intención del usuario?

<details markdown="1"><summary>Comprobación</summary>

Que no son lo mismo. Un modelo mucho más pequeño, apuntado a la tarea mediante post-training, superó a un modelo mucho mayor que no lo había sido. La escala por sí sola no produjo el comportamiento que preferían las personas; lo que lo produjo fue cómo se apuntó la capacidad del modelo.

</details>

2. ▢ Pon en orden estos tres pasos del pipeline de Ouyang et al.: (a) entrenar un reward model con comparaciones humanas de salidas del modelo, (b) hacer fine-tuning de la policy contra el reward model con PPO, (c) hacer fine-tuning de un modelo base con demostraciones escritas por humanos.

<details markdown="1"><summary>Comprobación</summary>

c, a, b: primero se recopilan demostraciones y se entrena una policy supervisada (SFT), luego se recopilan comparaciones y se entrena un reward model, y luego se optimiza la policy contra ese reward model con PPO.

</details>

3. ▢ ¿Qué es un impuesto de alineación, según el propio hallazgo de Ouyang et al., y qué encontraron que podía compensarlo en parte?

<details markdown="1"><summary>Comprobación</summary>

Una caída medida del rendimiento en ciertos benchmarks públicos de NLP que acompañó a las ganancias de alineación del post-training, aunque los evaluadores humanos prefirieran en conjunto el modelo alineado. Mezclar las actualizaciones de PPO con actualizaciones que aumentan la verosimilitud de los datos de preentrenamiento originales (PPO-ptx) recuperó buena parte de ese rendimiento perdido sin renunciar a las ganancias de preferencia.

</details>

4. ▢ ¿Cuál de estas describe mejor lo que hacen SFT, el modelado de recompensa y RLHF-PPO en el pipeline de Ouyang et al.?

    - a) SFT imita directamente demostraciones escritas por humanos; el modelado de recompensa aprende a predecir la preferencia humana entre salidas; RLHF-PPO optimiza la policy contra esa señal de preferencia aprendida
    - b) Los tres pasos entrenan el reward model, a escala creciente
    - c) SFT y RLHF-PPO son el mismo paso, ejecutado dos veces por estabilidad
    - d) El modelado de recompensa reemplaza por completo al modelo base antes de que empiece PPO

<details markdown="1"><summary>Comprobación</summary>

**a)** es el reparto real del trabajo entre los tres pasos. (b), (c) y (d) colapsan cada una pasos que hacen cosas genuinamente distintas: imitar demostraciones, aprender una señal de preferencia y optimizar contra esa señal son tres pasos separados, no uno repetido.

</details>

## Prácticas en el mundo real

- [ ] Busca una model card o un informe técnico de un modelo "instruct" o "chat" abierto, y anota cuáles de los tres pasos de Ouyang et al. dice explícitamente que usó (SFT, un reward model y/o RL), y cuáles, si alguno, sustituye por un método distinto.
- [ ] Lee el abstract del paper de InstructGPT (enlazado arriba) y escribe, en una frase, qué daños concretos (más allá de simplemente "poco útil") nombran Ouyang et al. como motivación de la necesidad de alineación.
- [ ] Mañana: sin mirar adelante, escribe una predicción de una frase para la etapa 2: dado que SFT se describe como imitar directamente demostraciones escritas por humanos, ¿qué tipo de error esperarías que cometiera una implementación ingenua de SFT si entrenara con cada token de un ejemplo de entrenamiento, incluido el propio prompt?

## Para profundizar

- [Paper: "Training language models to follow instructions with human feedback", Ouyang et al., 2022](https://arxiv.org/abs/2203.02155)
- [Recursos](../RESOURCES.md)

---

¿No termina de quedar claro? Vuelve a leer la fuente primaria de arriba, ya que esta lección la comprime y en la compresión es donde se escapa la comprensión. Consulta el [glosario](../GLOSSARY.md) por si algún término te resultó resbaladizo.

Si lo poco claro es la propia lección y no el material, eso es un defecto: [abre un issue](https://github.com/TokenCemetery/teach/issues).
