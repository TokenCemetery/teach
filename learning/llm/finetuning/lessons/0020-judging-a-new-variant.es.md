---
title: "20. Juzgar una variante nueva de PEFT"
description: "Seis preguntas de triaje, y el baseline que hay que superar"
type: lesson
---

# Lección 20. Juzgar una variante nueva de PEFT

**Vínculo con la misión:** "Leer un paper nuevo de PEFT y juzgar si la victoria que afirma sobreviviría en tu propia tarea" es el último elemento de la lista de éxito. Esta lección es esa habilidad.
**Fuente principal:** [Docs: LoRA variants, Hugging Face PEFT](https://huggingface.co/docs/peft/main/en/developer_guides/lora)
**Requisitos previos:** [Lección 19](0019-when-dora-wins.md), [Lección 17](0017-what-qlora-costs.md)

## Calentamiento

1. ▢ ¿En qué condición es DoRA la elección correcta frente a más rank?

<details markdown="1"><summary>Comprobación</summary>

Cuando el rank está fijado en bajo por algo que no puedes eliminar, normalmente el riesgo de sobreajuste en un dataset pequeño.

</details>

2. ▢ ¿Qué debe ser igual para que dos ejecuciones sean comparables?

<details markdown="1"><summary>Comprobación</summary>

Todo salvo la única variable bajo prueba: datos, partición, seed, rank, alpha, learning rate, schedule, pasos.

</details>

3. ▢ ¿Qué dos costos de calidad tiene la cuantización, y cómo se separan?

<details markdown="1"><summary>Comprobación</summary>

La degradación del base antes de entrenar, y un peor entrenamiento del adapter sobre un base degradado. Aísla el primero evaluando bases cuantizados y no cuantizados sin adapter.

</details>

## Qué debes saber

Aparecen constantemente métodos nuevos de fine-tuning eficiente en parámetros. La mayoría no te importan. La habilidad es el triaje, no el entusiasmo.

### El panorama, organizado por lo que cambian

En lugar de memorizar métodos, aprende los ejes. Casi toda variante modifica una de cuatro cosas.

**El escalado.** rsLoRA ([arXiv:2312.03732](https://arxiv.org/abs/2312.03732)) sustituye el divisor `α/r` por `α/√r`, argumentando que `α/r` amortigua en exceso con rank alto. Barato, un flag, importa cuando trabajas con rank alto.

**Los learning rates.** LoRA+ ([arXiv:2402.12354](https://arxiv.org/abs/2402.12354)) usa un learning rate más alto para `B` que para `A`, argumentando que los dos factores no deberían compartir un mismo learning rate dados sus distintos papeles y escalas. Barato, y un control genuinamente distinto de cualquiera de la lección 9.

**La inicialización.** En lugar de `A` aleatoria y `B` en cero:

- **PiSSA** ([arXiv:2404.02948](https://arxiv.org/abs/2404.02948)) inicializa a partir de los componentes singulares principales de `W₀`, de modo que el adapter empieza alineado con las direcciones dominantes del peso.
- **OLoRA** inicializa mediante una descomposición QR de `W₀`.
- **LoftQ** ([arXiv:2310.08659](https://arxiv.org/abs/2310.08659)) inicializa el adapter para compensar el error de cuantización, específicamente para el escenario de QLoRA.

Observa que todos ellos renuncian a la propiedad de inicialización en cero de la lección 9: el modelo ya no empieza idéntico al base. Es un intercambio deliberado, y es lo que hay que escrutar.

**La estructura.**

- **AdaLoRA** ([arXiv:2303.10512](https://arxiv.org/abs/2303.10512)) asigna el rank de forma adaptativa entre capas en lugar de usar un mismo rank en todas partes, con el argumento de que las capas difieren en cuánta adaptación necesitan.
- **VeRA** ([arXiv:2310.11454](https://arxiv.org/abs/2310.11454)) comparte `A` y `B` aleatorias congeladas entre capas y entrena solo pequeños vectores de escala, recortando drásticamente el tamaño del adapter.
- **DoRA** desacopla la magnitud de la dirección, como en la lección 18.

En PEFT la mayoría de estos son un flag de configuración o un valor de `init_lora_weights` y no una ruta de código aparte, lo que hace barato probarlos y hace de la lectura de la superficie de configuración una forma rápida de ver qué considera establecido la biblioteca.

### Las preguntas de triaje

Cuando aparece un método nuevo, haz estas preguntas en orden. Normalmente puedes parar pronto.

**1. ¿Qué cambia, en cuál de los cuatro ejes?** Si no puedes responder esto a partir del abstract y una figura, o el paper está mal escrito o todavía no eres su público. Solo esta pregunta filtra la mayoría de las cosas.

**2. ¿Cuál es el baseline?** La forma más común de inflar un resultado es un baseline débil. Atención a: LoRA con un rank que eligieron los autores, targets solo de atención cuando todas las lineales es el valor por defecto moderno, un learning rate ajustado para el método nuevo pero heredado para el baseline. **Un método que supera a un LoRA sin ajustar no ha demostrado superar a LoRA.**

**3. ¿Es la mejora mayor que el ruido?** Busca varianza entre seeds o intervalos de confianza. Si el paper reporta números sueltos sin dispersión, y la mejora es de un punto o dos, el resultado todavía no se distingue del ruido. Es extremadamente común.

**4. ¿Qué cuesta?** Tiempo por paso, complejidad de implementación, si se fusiona limpiamente, si se compone con la cuantización, si existe una implementación en la que confíes. Un 1% de mejora a cambio de un 30% de ralentización es un mal intercambio en la mayoría de los casos.

**5. ¿Se aplica su mecanismo a tu régimen?** El beneficio de DoRA vive en rank bajo. El de LoftQ vive en el entrenamiento cuantizado. El de rsLoRA vive en rank alto. Un método cuyo mecanismo aborda una restricción que no tienes no te ayudará, y esto es predecible *antes* de ejecutar nada.

**6. ¿Lo ha reproducido alguien independiente?** Las comunidades de profesionales prueban los métodos en tareas reales con rapidez y son tajantes sobre lo que no se replica. Esto suele ser más rápido e informativo que leer el paper dos veces.

### Tres señales de alerta fiables

- **Mejoras reportadas solo en benchmarks, nunca en una tarea con un despliegue.** Los benchmarks son proxies y se optimizan a fondo contra ellos.
- **Comparación contra un baseline de LoRA solo de atención** en un paper escrito después de que todas las lineales se convirtiera en práctica estándar. O desinformado o conveniente.
- **Sin contabilidad de costos.** Todo método tiene un costo. Un paper que no declara el suyo no está siendo franco contigo, y la omisión suele ser la parte interesante.

### La posición por defecto

**LoRA con rank adecuado en todas las capas lineales, con un learning rate ajustado, es un baseline fuerte que es difícil de superar por mucho.** Ese es el resultado práctico de la línea de trabajo "LoRA without regret", y debería ser tu punto de partida y tu comparación.

Una variante nueva necesita superar *eso*, en tu tarea, por más que tu ruido de seeds, con menos costo del que habría tenido subir el rank. La mayoría no superan la vara. Saber esto no es cinismo. Es lo que te permite dedicar atención a las pocas que sí.

## Práctica

1. ▢ Nombra los cuatro ejes que puede modificar una variante de PEFT, con un ejemplo de cada uno.

<details markdown="1"><summary>Comprobación</summary>

Escalado (rsLoRA), learning rates (LoRA+), inicialización (PiSSA, OLoRA, LoftQ), estructura (AdaLoRA, VeRA, DoRA).

Conocer los ejes significa que un método nuevo es clasificable a primera vista en lugar de tener que aprenderse desde cero.

</details>

2. ▢ Un paper reporta que su método supera a LoRA por 2.1 puntos, con LoRA en rank 8 solo en módulos de atención. ¿Cuál es tu preocupación?

<details markdown="1"><summary>Comprobación</summary>

El baseline es débil para los estándares actuales. Los targets de todas las lineales con rank mayor son el valor por defecto moderno y son sustancialmente más fuertes que solo atención con rank 8.

Es muy posible que el método supere a ese baseline débil y aun así pierda frente a un LoRA bien configurado. La comparación tal como se publicó no te lo dice.

</details>

3. ▢ ¿Qué propiedad de un paper socava más una mejora afirmada de 1.5 puntos?

    - a) La ausencia de cualquier varianza o intervalo entre seeds reportado
    - b) El uso de un modelo más pequeño que el que piensas usar
    - c) La ausencia de una implementación de referencia publicada
    - d) La evaluación en solo tres tareas posteriores distintas

<details markdown="1"><summary>Comprobación</summary>

**a)** La ausencia de cualquier varianza o intervalo entre seeds reportado.

Sin una dispersión, una mejora de 1.5 puntos no se puede distinguir del ruido de una ejecución a otra, que a menudo es de ese tamaño. Las demás son limitaciones reales pero no socavan la afirmación central como lo hace la varianza ausente.

</details>

4. ▢ LoftQ inicializa el adapter para compensar el error de cuantización. ¿En qué régimen predecirías que ayuda, y dónde predecirías que no hace nada?

<details markdown="1"><summary>Comprobación</summary>

Debería ayudar al entrenar contra un base cuantizado, de forma más visible con una cuantización agresiva y en modelos más pequeños donde el error de cuantización es proporcionalmente más dañino.

No debería hacer nada con un base en bf16 sin cuantizar, porque no hay error de cuantización que compensar, así que el mecanismo no tiene dónde agarrarse.

</details>

5. ▢ PiSSA renuncia a la inicialización en cero. ¿Por qué importa eso, y qué comprobarías?

<details markdown="1"><summary>Comprobación</summary>

La inicialización en cero garantiza que el modelo adaptado empieza idéntico al base, así que el entrenamiento parte de pesos en buen estado conocido y cualquier degradación es atribuible al entrenamiento.

Renunciar a eso significa que el modelo empieza perturbado. Comprueba si hay inestabilidad temprana, y comprueba si la perturbación ha dañado capacidades fuera de tu tarea. Un conjunto de regresión (lección 24) ejecutado en el paso cero, antes de entrenar, es la prueba directa.

</details>

6. ▢ ¿Cuál es el baseline que toda variante nueva debe superar, y por qué es difícil?

<details markdown="1"><summary>Comprobación</summary>

LoRA con rank adecuado en todas las capas lineales con un learning rate ajustado.

Es difícil porque ya tiene capacidad y cobertura suficientes para acercarse al full fine-tuning en muchas tareas supervisadas. Cuando el baseline está cerca de un techo, queda poco margen para que un refinamiento del mecanismo lo reclame.

</details>

## Prácticas en el mundo real

- [ ] Elige una variante de esta lección que no hayas usado. Aplica las seis preguntas de triaje a su paper y escribe un veredicto de un párrafo para tu propia tarea.
- [ ] Lee las opciones de `init_lora_weights` de tu versión instalada de PEFT. Asigna cada una a un método y a un eje.
- [ ] Busca en una comunidad de profesionales reportes independientes sobre ese método. Compara lo que encontraron con lo que afirmaba el paper.
- [ ] Mañana: ejecuta la variante elegida contra un baseline de LoRA de todas las lineales bien ajustado, tres seeds cada uno. Registra si la mejora sobrevive.

## Para profundizar

- [Docs: LoRA variants, Hugging Face PEFT](https://huggingface.co/docs/peft/main/en/developer_guides/lora)
- [Docs: "LoRA Without Regret", Hugging Face TRL](https://huggingface.co/docs/trl/main/en/lora_without_regret)
- [EleutherAI Blog](https://blog.eleuther.ai/): un grupo que publica sus resultados negativos, que es la mitad más rara de esta pregunta
- [r/LocalLLaMA](https://www.reddit.com/r/LocalLLaMA/): reportes de replicación rápidos y tajantes

---

¿No termina de quedar claro? Vuelve a leer la fuente primaria de arriba, ya que esta lección la comprime y en la compresión es donde se escapa la comprensión. Consulta el [glosario](../GLOSSARY.md) por si algún término te resultó resbaladizo.

Si lo poco claro es la propia lección y no el material, eso es un defecto: [abre un issue](https://github.com/TokenCemetery/teach/issues).
