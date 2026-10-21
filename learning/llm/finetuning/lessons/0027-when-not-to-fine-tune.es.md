---
title: "27. Cuándo no hacer fine-tuning"
description: "El fine-tuning es el sexto de la lista, y por qué eso importa"
type: lesson
---

# Lección 27. Cuándo no hacer fine-tuning

**Vínculo con la misión:** La misión termina aquí: *"capaz de argumentar de forma convincente a favor del prompting o de la recuperación cuando esas opciones harían mejor el trabajo."* La habilidad senior es rechazar el trabajo.
**Fuente principal:** [Docs: "LoRA Without Regret", Hugging Face TRL](https://huggingface.co/docs/trl/main/en/lora_without_regret)
**Requisitos previos:** todas las lecciones anteriores, ya que esta es la síntesis.

## Calentamiento

1. ▢ ¿Qué fase de la inferencia está limitada por ancho de banda, y por qué eso favorece a los modelos más pequeños?

<details markdown="1"><summary>Comprobación</summary>

El decode. Cada paso lee todos los pesos para producir un token, así que la velocidad sigue al ancho de banda de memoria y un modelo más pequeño es más rápido casi en proporción a su tamaño.

</details>

2. ▢ Nombra las cuatro categorías de regresión.

<details markdown="1"><summary>Comprobación</summary>

Seguimiento general de instrucciones, cumplimiento de formato y de comportamiento, comportamiento de seguridad y de rechazo, capacidad adyacente no entrenada.

</details>

3. ▢ ¿Cuál es el baseline que debe superar una variante nueva de PEFT?

<details markdown="1"><summary>Comprobación</summary>

LoRA con rank adecuado en todas las capas lineales con un learning rate ajustado.

</details>

## Qué debes saber

### La decisión, en orden

Recorre esta lista de arriba abajo. Para en la primera fila que resuelva tu problema.

| Enfoque | Resuelve | Costo |
|---|---|---|
| Mejor prompt | La mayoría de los problemas de formato y de comportamiento | Minutos |
| Ejemplos few-shot | Consistencia de formato, forma de la salida | Tokens de prompt por petición |
| Recuperación | Conocimiento ausente o cambiante | Infraestructura de recuperación |
| Uso de herramientas | Cálculo, consulta, acciones | Infraestructura de herramientas |
| Decodificación restringida | Validez del esquema, de forma absoluta | Soporte de serving |
| **Fine-tuning** | Comportamiento consistente, costo del prompt, suficiencia de un modelo pequeño | Datos, evaluación, mantenimiento |
| Full fine-tuning | Cambios de comportamiento muy grandes | Sustancialmente más de todo |

El fine-tuning es sexto. **La mayoría de las personas que quieren hacer fine-tuning tienen un problema que una de las cinco primeras resuelve, con más rapidez y fiabilidad.** Llegar a la fila seis antes de agotar las filas de la uno a la cinco es el error caro más común de este campo.

Observa en especial que **la decodificación restringida resuelve por completo la validez del esquema**, porque la generación restringida por gramática no puede emitir JSON inválido. Si todo tu problema es salida mal formada, no necesitas entrenar nada.

### Las tres preguntas que lo deciden

**1. ¿Es el problema de conocimiento o de comportamiento?**

El conocimiento, es decir, hechos y documentos y todo lo que cambia, es trabajo de la recuperación. El fine-tuning instala hechos de forma poco fiable, inverificable, y la obsolescencia exige reentrenar. La recuperación es precisa, citable y se actualiza editando un documento.

El comportamiento, es decir, formato y tono y estructura y consistencia y una frontera de decisión, es trabajo del fine-tuning. Aquí es donde destaca de verdad y donde nada más lo hace igual de bien.

La trampa: "el modelo no conoce nuestro producto" suena a problema de entrenamiento y es un problema de recuperación. "El modelo no responde de forma consistente en nuestro estilo de la casa por mucho que le haga prompt" suena a problema de prompting y es un problema de entrenamiento.

**2. ¿Has agotado de verdad el prompting?**

No "probado unos cuantos prompts". Agotado: iteración sistemática, ejemplos few-shot, un system prompt estructurado, y **medido en el mismo conjunto held-out que usarías para evaluar un fine-tune.** La mayoría de las afirmaciones de que el prompting falló son afirmaciones de que fallaron un puñado de intentos sin medir.

Si no puedes decir la puntuación del prompting en tu conjunto held-out, no tienes un baseline, y sin un baseline no puedes demostrar que el fine-tune ayudó.

**3. ¿Lo vas a mantener?**

Un fine-tune es un artefacto vivo. Los base models quedan superados, los requisitos cambian, las distribuciones derivan, las evaluaciones necesitan actualizarse. Si nadie es responsable de él, estás construyendo algo que decaerá en silencio mientras aparenta funcionar, y un fine-tune obsoleto es peor que ningún fine-tune, porque se confía en él.

### Cuándo el fine-tuning es claramente lo correcto

Para ser justos con el método, estos son reales y comunes:

- **Alto volumen con un prompt largo.** Mover contenido del prompt a los pesos se amortiza en cada petición (lección 26).
- **Entonces puede bastar un modelo más pequeño.** El caso más fuerte, porque recorta costo y latencia a la vez.
- **Comportamiento que se resiste al prompting.** Un tono, un formato o una frontera de decisión que el modelo no mantendrá de forma consistente por mucho que se lo pidas.
- **Una tarea estrecha con ejemplos abundantes.** Clasificación, extracción, transformación estructurada: el fine-tuning es excelente y a menudo supera a un modelo mucho más grande con prompt.
- **Rutas críticas en latencia.** Los prompts más cortos y los modelos más pequeños ayudan, directamente.
- **Una notación o sintaxis específica de un dominio** genuinamente infrarrepresentada en el preentrenamiento.

### Combinar, en lugar de elegir

El planteamiento "hacer fine-tuning o recuperar" suele ser erróneo. Los sistemas más fuertes hacen ambas cosas, para trabajos distintos:

**La recuperación aporta los hechos. El fine-tuning enseña qué hacer con ellos.**

Un modelo con fine-tuning para usar bien el contexto recuperado, citándolo y respetándolo y admitiendo cuando es insuficiente y negándose a inventar más allá de él, combinado con una recuperación que aporte hechos actuales y precisos, supera a cualquiera de las dos por separado. Eso es una arquitectura, y reconocerla es la versión senior de esta decisión.

### La posición calibrada sobre la capacidad

Te has ganado una visión matizada aquí, así que mantenla con precisión.

El viejo planteamiento, "LoRA es una aproximación barata, el full fine-tuning es lo de verdad", está en gran medida obsoleto. Con rank adecuado en todas las capas lineales y un learning rate bien ajustado, LoRA iguala al full fine-tuning en cargas típicas de supervised fine-tuning. **La brecha de capacidad se ha cerrado en su mayor parte para el régimen en el que trabaja la mayoría de la gente.**

Lo que significa: si has decidido hacer fine-tuning, los adapters son casi con seguridad el método correcto. El full fine-tuning es para cambios de comportamiento muy grandes, preentrenamiento continuado en un dominio o idioma nuevo a escala, o investigación donde necesitas todo el espacio de parámetros. La pregunta que queda no es "adapter o completo" sino "debería entrenarse esto siquiera".

### Cómo suena el buen juicio

> "Los fallos reportados son todos obsolescencia factual, así que esto es recuperación, no entrenamiento. Déjame medir primero un baseline con prompt en el conjunto held-out. Si el problema residual tras la recuperación es la consistencia de formato con 40,000 peticiones al día, entonces vale la pena costear un adapter de rank 32 en todas las lineales sobre un modelo de 3B, incluida la persona que lo reentrenará dentro de seis meses. Querría un conjunto de regresión que cubra seguridad y seguimiento general de instrucciones antes de desplegar, porque estaríamos adaptando un modelo instruct."

Nada de eso es un hecho que hayas consultado. Es la forma de razonamiento para la que existía este espacio de trabajo.

## Práctica

1. ▢ "Nuestro bot de soporte no conoce los productos lanzados este trimestre." ¿Fine-tuning o no?

<details markdown="1"><summary>Comprobación</summary>

No. Eso es conocimiento, y el conocimiento que cambia cada trimestre es el peor ajuste posible para el fine-tuning, que instala hechos de forma poco fiable y queda obsoleto de inmediato.

Recuperación: precisa, citable, actualizada editando un catálogo. Por separado, el fine-tuning podría valer la pena para enseñar al bot a *usar* bien los datos de producto recuperados.

</details>

2. ▢ "El prompting no funcionó." ¿Qué preguntas?

<details markdown="1"><summary>Comprobación</summary>

Qué se midió, en qué conjunto held-out, con qué puntuación. Además: ¿se probaron ejemplos few-shot?, ¿se probó un system prompt estructurado?, ¿se probó la decodificación restringida para un problema de formato?

Sin un baseline con prompt medido no hay nada con lo que comparar un fine-tune, así que no puedes demostrar mejora aunque la consigas.

</details>

3. ▢ Todo tu problema es que el 12% de las salidas son JSON inválido. ¿Solución más barata?

<details markdown="1"><summary>Comprobación</summary>

Decodificación restringida. La generación restringida por gramática no puede producir JSON inválido, y es un cambio del lado del serving sin ningún entrenamiento.

El fine-tuning podría llegar a un 99% de validez. La decodificación restringida llega al 100% por construcción. Haz fine-tuning solo si los *valores* también son incorrectos, que es un problema distinto.

</details>

4. ▢ ¿Qué situación favorece más al fine-tuning?

    - a) Al modelo le falta conocimiento de tu documentación interna
    - b) Alto volumen de peticiones con un system prompt muy largo
    - c) El modelo comete de vez en cuando errores aritméticos en la salida
    - d) El modelo necesita información sobre acontecimientos de esta semana

<details markdown="1"><summary>Comprobación</summary>

**b)** Alto volumen de peticiones con un system prompt muy largo.

Mover contenido del prompt a los pesos elimina el costo de prefill en cada petición, y el ahorro escala con el volumen. (a) y (d) son recuperación. (c) es uso de herramientas: dale una calculadora.

</details>

5. ▢ ¿Es LoRA un compromiso respecto al full fine-tuning?

<details markdown="1"><summary>Comprobación</summary>

En gran medida no, en el régimen en el que trabaja la mayoría de la gente. Con rank adecuado en todas las capas lineales y un learning rate ajustado, LoRA iguala al full fine-tuning en cargas típicas de supervised fine-tuning.

El full fine-tuning sigue siendo apropiado para cambios de comportamiento muy grandes, preentrenamiento continuado a escala o investigación que necesite todo el espacio de parámetros. Para una adaptación de tarea ordinaria, los adapters son el método correcto y no una concesión.

</details>

6. ▢ Tienes la recuperación funcionando y el modelo sigue ignorando el contexto recuperado e inventando respuestas. ¿Y ahora qué?

<details markdown="1"><summary>Comprobación</summary>

Ahora el fine-tuning está bien motivado, y esta es la arquitectura combinada y no una elección entre enfoques.

El problema es de comportamiento: apoyarse en el contexto proporcionado, respetarlo, citarlo y negarse cuando es insuficiente. La recuperación aporta hechos; el entrenamiento enseña qué hacer con ellos. Construye el dataset a partir de contextos recuperados reales con respuestas correctas y fundamentadas, incluidos casos donde la respuesta correcta es "el contexto proporcionado no cubre esto".

</details>

## Prácticas en el mundo real

- [ ] Toma una propuesta de fine-tuning, tuya o de otra persona, y aplícale las tres preguntas. Escribe un veredicto de un párrafo.
- [ ] Mide un baseline con prompt en tu conjunto held-out, como es debido. Registra el número antes de entrenar nada.
- [ ] Calcula el costo de toda la vida de un fine-tune: datos, evaluación, serving, reentrenamiento, responsabilidad. Compáralo con el ahorro.
- [ ] Mañana: encuentra un caso en el que te negarías a hacer fine-tuning, y escribe el argumento a favor de la alternativa en un párrafo sobre el que otra persona pueda actuar.

## Para profundizar

- [Docs: "LoRA Without Regret", Hugging Face TRL](https://huggingface.co/docs/trl/main/en/lora_without_regret)
- [Paper: "Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks", Lewis et al., arXiv:2005.11401](https://arxiv.org/abs/2005.11401)
- [r/LocalLLaMA](https://www.reddit.com/r/LocalLLaMA/): búscalo para encontrar los casos en que los profesionales decidieron no hacer fine-tuning, y qué desplegaron en su lugar
- [Modos de fallo](../reference/failure-modes.md), [Hiperparámetros de LoRA](../reference/lora-hyperparameters.md), [Presupuesto de memoria](../reference/memory-budget.md)

---

Ese es el arco. A partir de aquí el trabajo son prácticas con tareas reales, y la última línea de la misión es la que hay que conservar: poder argumentar de forma convincente *en contra* del fine-tuning es lo que hace que el argumento *a favor* valga algo.

¿No termina de quedar claro? Vuelve a leer la fuente primaria de arriba, ya que esta lección la comprime y en la compresión es donde se escapa la comprensión. Consulta el [glosario](../GLOSSARY.md) por si algún término te resultó resbaladizo.

Si lo poco claro es la propia lección y no el material, eso es un defecto: [abre un issue](https://github.com/TokenCemetery/teach/issues).
