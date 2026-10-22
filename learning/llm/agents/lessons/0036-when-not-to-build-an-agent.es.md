---
title: "36. Cuándo no construir un agente"
description: "El criterio para decidir si una tarea realmente necesita un agente, y la disciplina de decir que no cuando no vale su costo"
type: lesson
---

# Lección 36. Cuándo no construir un agente

**Vínculo con la misión:** Desarrollar el criterio para decidir si una tarea dada necesita un agente o basta un flujo de trabajo fijo, y para defender esa decisión frente a la presión de la organización y el atractivo de las soluciones con forma de agente.
**Fuente principal:** [Article: "Building Effective Agents", Anthropic Engineering](https://www.anthropic.com/engineering/building-effective-agents)
**Requisitos previos:** [Lección 35](0035-durability-and-what-frameworks-buy.md), [Espectro de autonomía](../GLOSSARY.md)

## Calentamiento

1. ▢ Recuerda de la lección 2: ¿cuál es la diferencia que define a un flujo de trabajo frente a un agente en términos de flujo de control?

<details markdown="1"><summary>Comprobación</summary>

Un flujo de trabajo tiene un camino que el desarrollador fijó de antemano; todas las ramas y secuencias las cablea el desarrollador. Un agente tiene un flujo de control decidido en tiempo de ejecución por el modelo, incluido si continuar o parar.

</details>

2. ▢ Recuerda de la lección 2: en el espectro de autonomía, ¿qué prueba concreta puedes aplicar para decidir si el número de ramas de una tarea es realmente enumerable?

<details markdown="1"><summary>Comprobación</summary>

Si puedes listar todos los caminos distintos que un flujo de trabajo necesitaría para cubrir la tarea, el número de ramas es enumerable y un flujo de trabajo puede bastar. Si llegan caminos nuevos más rápido de lo que puedes cablearlos, o el camino correcto depende realmente de información que solo está disponible a mitad de la tarea, el número de ramas es en la práctica ilimitado y un agente es más defendible.

</details>

## Qué debes saber

### Por qué la decisión es más difícil de lo que la lección 2 la hizo parecer

La lección 2 enseñó el espectro de autonomía como una elección técnica limpia: ¿la forma de la tarea es conocida o desconocida, enumerable o ilimitada? En la práctica, esa elección se hace bajo una presión real.

Un responsable de producto ha visto una demo convincente de un agente resolviendo un problema complejo y pregunta: "¿Podemos construir eso para nuestro producto?" Una organización siente que va por detrás en IA y quiere "añadir agentes" a su plataforma. Un interesado señala una tarea y dice "esto parece digno de un agente", sin comprobar si se probó de verdad la alternativa más simple. Un flujo de trabajo que resuelve el mismo problema es menos emocionante de presentar, incluso cuando el flujo de trabajo es la mejor decisión de ingeniería.

El papel de esta lección no es volver a enseñar el marco de la lección 2; el marco es correcto. El papel es nombrar por qué aplicarlo bien es una decisión de criterio bajo presión, y darte señales de alerta concretas que te indiquen que un agente no está justificado, cada una vinculada a una lección anterior concreta para que puedas detectar el patrón cuando lo veas en una propuesta o en una revisión de arquitectura.

### Señal de alerta 1: nadie probó antes el flujo de trabajo más simple

La señal de alerta más fuerte es esta: un interesado o una propuesta dice que se necesita un agente, pero nadie ha construido realmente la alternativa del flujo de trabajo para probar esa afirmación.

La lección 2 defiende cada elección nombrando lo que habría costado la opción que rechazas. Esa defensa solo funciona si realmente probaste la opción rechazada. Si una propuesta afirma "un agente es necesario" sin mostrar un intento con un flujo de trabajo y explicar por qué fracasó, la afirmación no se ha contrastado con la alternativa. Se te pide aceptar un aumento de complejidad sin evidencia de que la complejidad sea necesaria.

Cómo se ve esto en la práctica: una propuesta dice "Necesitamos un agente para manejar estos tickets de atención al cliente porque se bifurcan en cuarenta categorías distintas". Sin un intento con un flujo de trabajo, no sabes si cuarenta categorías son realmente demasiadas para cablear, o si el autor de la propuesta simplemente aún no lo ha probado. Tras construir un enrutador de flujo de trabajo y probarlo con tickets reales, podrías descubrir que cuarenta categorías son manejables, o que la precisión del flujo de trabajo se resiente porque un clasificador basado en reglas no puede distinguir entre dos categorías en los casos límite. Probar el flujo de trabajo con la misma tarea te dice qué estás comprando realmente al pasar a un agente.

La disciplina: antes de comprometerte con un agente, pregunta "¿qué flujo de trabajo se probó, y por qué falló?" Si la respuesta es "ninguno", insiste en construir uno primero. Podrías descubrir que el flujo de trabajo resuelve el problema lo bastante bien, o que el flujo de trabajo falla de formas específicas que un agente sí mejoraría.

### Señal de alerta 2: el modo de fallo es la fiabilidad, no la capacidad

La lección 2 dijo que un agente se gana su imprevisibilidad cuando necesitas flexibilidad. Pero la flexibilidad tiene costos en fiabilidad que las etapas 11 y 12 de este track dedicaron lecciones a nombrar: los errores de grounding en los agentes de uso del ordenador (lección 25), los errores de herramienta en cascada donde el fallo de una herramienta tumba el siguiente paso (lección 28), el envenenamiento del contexto donde una afirmación falsa entra en la transcripción y todos los turnos posteriores la tratan en silencio como un hecho (lección 27).

Si el modo de fallo de una tarea es una de estas clases de fiabilidad, y la tarea es algo donde un flujo de trabajo fijo y bien probado simplemente nunca cometería esa clase de error, entonces un agente compra imprevisibilidad a costa de un problema de fiabilidad que antes no existía.

Ejemplo: un sistema de clasificación de documentos que debe enrutar los documentos a exactamente una de cinco categorías conocidas. Un agente puede enrutar con flexibilidad e incluso recategorizar si lee algo en el documento que le haga cambiar de opinión. Pero si la tarea es clasificar un documento financiero con un proceso fijo y auditable, y la sanción por una clasificación errónea es una infracción regulatoria, entonces la flexibilidad de un agente no vale el riesgo de que el envenenamiento del contexto haga que el agente dude de su propio razonamiento previo y envíe un documento a la categoría equivocada. Un flujo de trabajo con una única decisión de enrutamiento por documento, auditable paso a paso, cuesta previsibilidad pero gana fiabilidad donde importa.

La disciplina: para las tareas donde el fallo es caro o donde la fiabilidad no es negociable, nombra qué problema de fiabilidad introduciría un agente que un flujo de trabajo no tendría. Si ese problema es lo bastante grave, el flujo de trabajo es la mejor opción aunque parezca menos sofisticado.

### Señal de alerta 3: la tríada letal está completa y sin beneficio

La lección 31 nombró la tríada letal: acceso a datos privados, exposición a contenido no confiable y capacidad de comunicarse con el exterior. Un agente tiene las tres condiciones cuando lee entrada no confiable y tiene herramientas que pueden usar mal los datos o exfiltrarlos.

Quitar cualquier condición rompe el ataque. Pero un agente que tiene las tres condiciones es explotable incluso si una inyección solo tiene éxito a veces. La lección 32 enseñó que la defensa no es insistir más en el prompt, sino acotar el acceso de las herramientas.

Si un agente propuesto tiene las tres condiciones de la tríada y la tarea no se beneficia de la imprevisibilidad del agente, entonces estás comprando explotabilidad sin ganar nada. Una integración más estrecha basada en un flujo de trabajo, o un conjunto de herramientas que carezca deliberadamente de una de las tres condiciones, logra el mismo objetivo sin ensamblar la exposición.

Ejemplo: un motor de recomendación de contenido lee perfiles de usuario y fuentes de contenido externas para sugerir elementos. Si el motor se implementa como un agente con herramientas para obtener contenido externo, consultar datos de usuario y enviar recomendaciones a un sistema de mensajería, tiene las tres condiciones de la tríada. Pero si el trabajo del motor es elegir de un conjunto fijo de tipos de recomendación según reglas simples (si el usuario ha visto A, recomendar B), entonces un flujo de trabajo hace el trabajo sin exponer los datos del usuario ni el sistema de recomendación a un canal de inyección de prompt que antes no existía.

La disciplina: para cada condición de la tríada, pregunta si la tarea realmente la necesita. Si un agente tiene las tres para una tarea que no requiere la flexibilidad del agente, rediseña el conjunto de herramientas para eliminar de forma deliberada al menos una condición. El sistema será menos impresionante como demo, pero será menos explotable y más fiable.

### Señal de alerta 4: el costo en tokens supera el valor de la tarea

La lección 33 enseñó la amplificación de tokens y el costo por tarea completada, incluido el multiplicador multiagente. La lección 19 mostró que un sistema orquestador-worker cuesta varias veces más en tokens que un solo agente que resuelve el mismo problema.

Una pregunta concreta: estima el costo real por tarea completada, incluidos los reintentos, la coordinación multiagente si aplica y cualquier amplificación de tokens por la longitud del contexto o la sobrecarga del caching. ¿Es aceptable ese costo para lo que produce la tarea?

Esta pregunta a menudo no se hace hasta que es demasiado tarde. Un equipo construye un agente, lo lanza y descubre que el costo por tarea supera lo que la tarea vale en valor de negocio. El agente funciona, pero operarlo es demasiado caro.

La disciplina: antes de comprometerte con un agente (sobre todo un sistema multiagente), estima el costo en tokens por tarea completada usando turnos o trayectorias reales de un prototipo. Contrasta esa estimación con el valor de la tarea. Si el costo en tokens supera el valor, el agente no está justificado, por muy elegante que sea el sistema.

### Juntándolo todo: hazte estas cuatro preguntas antes de comprometerte con un agente

1. ¿Se intentó realmente un flujo de trabajo más simple y se encontró insuficiente?
2. ¿Es el modo de fallo de la tarea uno en el que un agente introduce un nuevo problema de fiabilidad que un flujo de trabajo no tendría?
3. ¿Tiene el agente las tres condiciones de la tríada, y es necesaria esa exposición para la tarea?
4. ¿Es aceptable el costo en tokens por tarea completada para lo que produce la tarea?

Si la respuesta a cualquiera de estas es "no" o "no lo sabemos", el agente puede no estar justificado. Decir que no a un agente no es un fracaso; es disciplina. Estás eligiendo la previsibilidad, la fiabilidad, la seguridad o el costo por encima de la flexibilidad que compraría un agente. Es una elección defendible, y es la elección que te permite decir que sí con confianza cuando un agente de verdad está justificado.

## Práctica

1. ▢ Un equipo de producto propone construir un agente para resumir tickets de atención al cliente para informes internos. El agente leería el ticket (contenido de usuario no confiable), accedería a la base de datos de clientes de la empresa para buscar contexto y publicaría resúmenes en un canal de Slack. Una alternativa con flujo de trabajo haría que una persona clasificara a mano los tickets en categorías y luego ejecutara un resumidor basado en plantillas en cada categoría. El equipo dice "un agente es más eficiente". Sin ejecutar el flujo de trabajo, ¿qué pregunta deberías hacer primero?

<details markdown="1"><summary>Comprobación</summary>

Pídeles que construyan y prueben de verdad el flujo de trabajo con tickets reales. Mide cuánto más rápido es el agente, y si la ganancia de eficiencia justifica el costo en consumo de tokens y la exposición a la tríada letal (el agente lee contenido no confiable, accede a datos privados de clientes y envía mensajes al exterior). Si el flujo de trabajo es un 90 por ciento igual de bueno y cuesta un 10 por ciento, gana el flujo de trabajo. Sin probar el flujo de trabajo, la afirmación "un agente es más eficiente" no está contrastada.

</details>

2. ▢ Estás revisando la propuesta de un agente que ayuda a analistas a depurar pruebas que fallan en un código base grande. El agente tendría acceso al código del repositorio, a los resultados de las pruebas y a los logs. Llamaría a herramientas para buscar en el código, ejecutar pruebas individuales y registrar informes de errores. La propuesta dice: "Un agente puede explorar el código base con más flexibilidad que un script". ¿Qué preocupación de fiabilidad enseña la lección 27 que es relevante para evaluar esta propuesta?

<details markdown="1"><summary>Pista</summary>

Piensa en qué pasa cuando un agente lee las salidas de las llamadas a herramientas y construye un modelo de lo que dice y hace el código. ¿Qué patrón de error es exclusivo de los agentes?

</details>

<details markdown="1"><summary>Comprobación</summary>

El envenenamiento del contexto (lección 27). Si el agente interpreta mal un log o un fragmento de código y construye una afirmación falsa en su modelo del error (por ejemplo, "esta función devuelve None"), cada paso de razonamiento posterior tratará esa afirmación falsa como un hecho establecido. Un script con un camino fijo no dudará de su propia salida de este modo. La flexibilidad de un agente para cambiar de opinión según nueva evidencia es una ventaja, pero también abre la puerta a una confianza silenciosa en conclusiones erróneas que se arrastran de un paso al siguiente. Evalúa si el modo de fallo de la tarea (depurar una prueba) sale más perjudicado por la flexibilidad (mejor para encontrar errores novedosos) o por el riesgo de que el envenenamiento del contexto lleve al agente por un camino falso.

</details>

3. ▢ ¿Cuál de estos escenarios indica con más claridad que un agente propuesto no está justificado?

    - a) La tarea se puede resolver con un flujo de trabajo, pero el flujo de trabajo requeriría cablear una rama nueva cada vez que llega un nuevo tipo de documento
    - b) La tarea se ha probado como flujo de trabajo y no alcanzó los objetivos de precisión, pero un prototipo de agente probado con el mismo conjunto de datos rinde mejor
    - c) La tarea nunca se ha probado como flujo de trabajo, pero un interesado insiste en que un agente es necesario porque una demo de IA que vio fue impresionante
    - d) La tarea requiere leer contenido no confiable y acceder a datos privados, pero el conjunto de herramientas del agente carece deliberadamente de comunicación externa

<details markdown="1"><summary>Comprobación</summary>

**c)** El escenario donde una tarea nunca se ha probado como flujo de trabajo, y la propuesta la impulsa el entusiasmo por una demo y no la evidencia de que la alternativa más simple fracasa. El escenario (a) describe una tarea donde un agente compra flexibilidad continua; el número de ramas crece, así que un agente está justificado. El escenario (b) muestra que el flujo de trabajo se probó y fracasó, lo que convierte el mejor rendimiento del agente en evidencia a su favor. El escenario (d) describe una arquitectura razonada que elimina una condición de la tríada, que es una decisión de diseño justificada. Solo (c) no tiene base en pruebas.

</details>

4. ▢ Estimas que un agente para una tarea costaría 5.000 tokens por ejecución completada, incluidos los reintentos, y que la tarea produce un valor de negocio equivalente a 2.000 tokens de cómputo a las tarifas actuales del mercado. Defiende una elección entre construir el agente o elegir una alternativa, nombrando lo que aceptas al tomar esa decisión.

<details markdown="1"><summary>Comprobación</summary>

La alternativa (un flujo de trabajo, un sistema más simple o dejar la tarea en manual) está justificada. El agente cuesta 2,5 veces su valor, lo que significa que cada ejecución le cuesta al negocio más en cómputo de lo que devuelve en valor. Construir el agente de todos modos solo es defendible si esperas que el costo en tokens baje (modelos más baratos, estrategias de caching, convergencia más rápida en tareas repetidas), o si el valor de negocio es mayor que el estimado. Si no se da ninguna de las dos, la disciplina es decir que no. El costo que aceptas es perder la flexibilidad que ofrecería un agente, pero ganas previsibilidad y eficiencia de costos. Ese es el intercambio correcto con estos números.

</details>

## Prácticas en el mundo real

- [ ] Toma una tarea que actualmente resuelve un agente en un sistema que conozcas. Estima el costo en tokens por tarea completada y el valor de negocio de cada finalización. ¿Es aceptable la proporción? Si no, ¿qué tendría que cambiar para que un agente estuviera justificado?
- [ ] Encuentra una propuesta (interna, o un artículo que describa un sistema) que defienda un agente. Rastrea si responde a las cuatro preguntas de las señales de alerta: ¿se probó un flujo de trabajo?, ¿es sensible a la fiabilidad el modo de fallo?, ¿son necesarias las tres condiciones de la tríada?, ¿es aceptable el costo? Anota qué señales de alerta atiende la propuesta y cuáles deja abiertas.
- [ ] Mañana: Imagina una función de producto que construirías como agente. Ahora diséñala como flujo de trabajo. Compáralas: ¿qué no puede hacer el flujo de trabajo que sí hace el agente? ¿Cuánto más difícil es de construir el flujo de trabajo? ¿Las ganancias justifican la complejidad añadida? Anota tu valoración honesta.

## Para profundizar

- [Article: "Building Effective Agents", Anthropic Engineering](https://www.anthropic.com/engineering/building-effective-agents)
- [Recursos](../RESOURCES.md)

---

¿No termina de quedar claro? Vuelve a leer la fuente primaria de arriba, ya que esta lección la comprime y en la compresión es donde se escapa la comprensión. Consulta el [glosario](../GLOSSARY.md) por si algún término te resultó resbaladizo.

Si lo poco claro es la propia lección y no el material, eso es un defecto: [abre un issue](https://github.com/TokenCemetery/teach/issues).
