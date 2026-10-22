---
title: "37. Revisar el diseño de agente de otra persona"
description: "Cómo evaluar un sistema de agentes de forma sistemática, y cómo zanjar una afirmación disputada volviendo a la fuente primaria"
type: lesson
---

# Lección 37. Revisar el diseño de agente de otra persona

**Vínculo con la misión:** Que se confíe en ti para revisar el diseño de agente de otra persona y zanjar las afirmaciones disputadas sobre él consultando las fuentes primarias, sin ponerte del lado de uno por defecto ni repartir la diferencia de forma vaga.
**Fuente principal:** [Article: "Building Effective Agents", Anthropic Engineering](https://www.anthropic.com/engineering/building-effective-agents)
**Requisitos previos:** [Lección 36](0036-when-not-to-build-an-agent.md)

## Calentamiento

1. ▢ ¿Qué comprueba el espectro de autonomía de la lección 2 para distinguir entre un flujo de trabajo y un agente?

<details markdown="1"><summary>Comprobación</summary>

Si el flujo de control lo decide de antemano el desarrollador, o lo decide en tiempo de ejecución el modelo. No el número de herramientas, la complejidad ni cuántas llamadas al modelo intervienen, sino quién eligió el camino.

</details>

2. ▢ De la lección 35, ¿cuál es una forma en que un framework puede reducir el costo de ejecutar un agente en producción frente a escribir el harness desde cero?

<details markdown="1"><summary>Comprobación</summary>

Almacenar en caché el contexto estable (definiciones de herramientas, system prompt) para que las tareas repetidas no reenvíen esos tokens, implementar estado durable para que una ejecución interrumpida pueda reanudarse, y ofrecer trazado y manejo de errores integrados que llevarían tiempo cablear a mano. El framework compra tiempo hasta la fiabilidad y reducción de costos a cambio de flexibilidad o de dependencia de un proveedor.

</details>

## Qué debes saber

### La lista de revisión: las etapas en orden

Cuando revises un diseño de agente propuesto o existente, recórrelo por las etapas de este track en orden, haciendo la misma pregunta en cada etapa: ¿está justificada esta elección y está documentada?

#### Etapas 1 y 2: espectro de autonomía y flujo de control

¿Dónde se ubica este sistema en el espectro de autonomía? ¿Es un solo prompt, un flujo de trabajo fijado por el desarrollador o un agente dirigido por el modelo? Busca la afirmación en la propuesta o en la documentación. Si la afirmación es solo "esto es un agente" sin explicar por qué es necesaria la autonomía, pregunta qué habría costado la alternativa de camino fijo. Un buen diseño no solo nombra la elección; la defiende.

#### Etapas 3 y 4: superficie de herramientas y esquema

¿Están las herramientas nombradas y descritas de una forma que le resulte útil al razonamiento de un modelo? La lección 8 enseñó que las descripciones de herramientas son superficie del prompt, no documentación de API. Los nombres de las herramientas deben describir lo que hace la herramienta desde la perspectiva del modelo, no el endpoint subyacente. Las descripciones de los parámetros deben ayudar al modelo a decidir qué pasar, no solo documentar el esquema técnico. ¿Está ajustado el conjunto de herramientas (evitando el exceso de la lección 9), o ha acumulado herramientas que rara vez se usan?

#### Etapas 5 y 6: estrategia de contexto y memoria

Para una tarea de larga duración, ¿cuál es la estrategia? ¿Distingue el diseño entre scratchpad (la transcripción en curso dentro de una ejecución) y memoria entre ejecuciones (hechos persistidos entre ejecuciones)? La lección 11 enseñó la compactación; ¿tiene el diseño un plan para acortar la transcripción a medida que crece? Si la tarea implica aprender hechos y llevarlos hacia delante, ¿se nombra un mecanismo de memoria, o el diseño depende solo de la transcripción?

#### Etapa 7: reflexión y reintentos

Cuando un paso falla, ¿planifica el diseño un reintento, e incluye una reflexión explícita (el agente razonando en lenguaje natural sobre por qué falló antes de intentarlo de nuevo)? ¿O simplemente entra en bucle y espera que el modelo se corrija solo? La lección 17 enseñó que el silencio no equivale a aprendizaje; un agente bien diseñado reflexiona tras un fallo.

#### Etapa 8: decisión multiagente

Si el diseño es multiagente, ¿justifica esa elección frente a la alternativa de un solo agente? La lección 19 enseñó el costo de coordinación: un sistema orquestador-worker multiplica los tokens y fragmenta el contexto entre workers. El diseño debería nombrar el beneficio concreto que justifica este costo. ¿Es el beneficio el paralelismo (tiempo real), el aislamiento de contexto (la transcripción de cada worker se mantiene limpia) o una independencia genuina de las subtareas? ¿Y se aplica ese beneficio a esta tarea concreta?

#### Etapa 14: seguridad y la tríada

¿Lee el agente contenido no confiable? ¿Accede a datos privados? ¿Tiene comunicación externa? La lección 31 enseñó que las tres condiciones juntas lo hacen explotable. El diseño debería nombrar qué condiciones están presentes y cuáles no, o cómo el diseño elimina de forma deliberada al menos una. Si el diseño tiene las tres pero no lo reconoce, es una señal de alerta.

#### Etapa 15: costo y durabilidad

¿Ha estimado alguien el costo en tokens por tarea completada? ¿Es aceptable ese costo? Si el sistema usa un framework, ¿está justificada la elección del framework, o se eligió por defecto? La lección 33 enseñó que el costo real por tarea incluye los reintentos y la amplificación de tokens. Un buen diseño nombra una estimación de costo, aunque sea aproximada.

### La habilidad concreta: zanjar una afirmación disputada desde la fuente primaria

Este track te presentó dos relatos creíbles y opuestos sobre los sistemas multiagente. La lección 18 describió los patrones orquestador-worker y sus beneficios. La lección 19 presentó el argumento de Cognition de que la mayoría de los sistemas multiagente no valen su costo, y que un solo agente con mejores herramientas a menudo gana.

Ambos relatos son correctos en sus propios dominios. Un revisor que solo recuerde a medias los dos podría ponerse de un lado por reflejo ("leí que los agentes únicos siempre son mejores, así que este diseño multiagente está mal") o repartir la diferencia de forma vaga ("lo multiagente a veces es bueno"). Ninguna de las dos cosas hace avanzar la conversación.

La habilidad real es volver a las fuentes primarias y comprobar si las circunstancias concretas del diseño coinciden con las condiciones bajo las que se sostiene el argumento de esa fuente.

"How We Built Our Multi-Agent Research System", de Anthropic, describe un sistema multiagente que funcionó. Las condiciones que lo hicieron funcionar, según la lectura de ese artículo, incluyen: las subtareas eran realmente independientes (cada investigador se centraba en un ángulo distinto), el paralelismo daba un beneficio real en tiempo real (los resultados había que sintetizarlos bajo presión de tiempo) y el equipo invirtió mucho en orquestación para mantener limpia la comunicación entre workers.

"Don't Build Multi-Agents", de Cognition, sostiene que el costo no vale la pena para la mayoría de las tareas. Las condiciones que hacen más fuerte su argumento incluyen: cuando las subtareas comparten contexto o se refinan entre sí, cuando tienes tiempo y presupuesto de contexto para que un solo agente explore caminos en serie, y cuando la sobrecarga de coordinación es alta en relación con el problema.

Ahora estás revisando un diseño. La propuesta dice: "Estamos construyendo un sistema de investigación con un orquestador y tres workers investigadores en paralelo". Antes de aceptar o rechazar lo multiagente, pregunta:

- ¿Son los tres ángulos de investigación realmente independientes, o comparten contexto y se refinan entre sí?
- ¿Hay un plazo real en tiempo real, o tienes tiempo para que un agente explore los tres ángulos en serie?
- ¿Ha presupuestado el equipo el trabajo de orquestación, o la coordinación es una ocurrencia tardía?
- ¿Cuánto costaría en tokens un solo agente con herramientas más amplias en comparación con el sistema multiagente?

Las circunstancias reales del diseño determinan qué argumento de qué fuente aplica. El trabajo de un revisor no es arbitrar entre las dos fuentes, sino rastrear si la situación del diseño coincide con las condiciones en las que el argumento de una fuente se vuelve más fuerte o más débil. Si el diseño no tiene respuesta a estas preguntas, todavía no ha zanjado la cuestión desde la fuente primaria; solo ha afirmado la elección.

### Qué logra una buena revisión de diseño

Una buena revisión no dice "esto es bueno" ni "esto es malo". Dice:

"Este diseño elige X porque Y. Rastreé esa elección hasta la etapa Z del track, donde se aplican estas preguntas. El diseño responde con claridad a estas preguntas y deja abiertas estas otras. Antes de comprometerse, el equipo debería resolver las preguntas abiertas o documentar los riesgos."

Una revisión que nombra preguntas concretas sin responder es más útil que una que emite un aprobado o un suspenso. Le da al equipo algo que hacer. También te da influencia: puedes hacer preguntas de seguimiento por escrito y hacer responsable al diseño de afirmaciones concretas, en lugar de limitarte a expresar escepticismo.

## Práctica

1. ▢ Estás revisando el diseño de un agente que procesa documentos financieros. El diseño dice que el agente tendrá acceso a: una herramienta para leer documentos del almacenamiento en la nube, una herramienta para consultar una base de datos de clientes y obtener el historial de transacciones, y una herramienta para registrar informes en un log de auditoría. El diseño no habla de seguridad. Usando el marco de la lección 31, ¿qué preguntas deberías hacer?

<details markdown="1"><summary>Comprobación</summary>

Las tres condiciones de la tríada letal están presentes: el agente lee contenido no confiable (documentos financieros subidos), accede a datos privados (historial de transacciones de clientes) y puede comunicarse con el exterior (registrar informes de auditoría). Una buena revisión pregunta: ¿Son necesarias las tres condiciones de la tríada? ¿Puede el diseño eliminar al menos una? Por ejemplo, ¿puede el agente leer documentos sin registrar informes directamente, redactando en su lugar informes para aprobación humana? ¿O puede evitar tocar la base de datos de clientes trabajando solo con datos resumidos? El diseño debería o bien justificar por qué se necesitan las tres, o bien documentar los controles de seguridad concretos (puertas de aprobación, registro de auditoría, sandboxing) que mitigan el riesgo.

</details>

2. ▢ Un diseño propone un orquestador con dos workers en paralelo: uno investiga productos de la competencia, el otro investiga las necesidades de los clientes. Los workers luego reportan los hallazgos a una persona analista que los sintetiza. Sospechas que la alternativa de un solo agente podría ser más barata. ¿Qué pregunta de la lección 19 deberías hacer para poner a prueba esta sospecha?

<details markdown="1"><summary>Pista</summary>

Piensa en qué hace el orquestador en este diseño, y si hay alguna tarea que el agente único no pudiera hacer igual de bien o más rápido.

</details>

<details markdown="1"><summary>Comprobación</summary>

Estima el costo en tokens: dos agentes worker más la sobrecarga del orquestador, comparado con un agente que investiga ambos ángulos en serie. ¿Terminan los dos workers en paralelo más rápido que un agente en serie (beneficio del paralelismo)? ¿O el agente único, que mantiene ambos hilos de investigación en una transcripción, los integra con más eficacia (beneficio de coherencia del contexto)? Si los workers terminan más rápido pero el multiplicador de costo en tokens es alto, y la persona analista no tiene restricciones de tiempo, gana el agente único. Si quienes investigan necesitan resultados con urgencia y el paralelismo ahorra horas, lo multiagente justifica el costo. El diseño debería haber hecho este cálculo; si no lo ha hecho, has encontrado una pregunta abierta.

</details>

3. ▢ Estás revisando la definición de una herramienta para un agente. La herramienta se llama query_customer_database y su descripción es: "Connect to the customer database and execute any SQL query provided by the user."

    - a) Esta es una herramienta bien diseñada porque es máximamente flexible
    - b) Esta herramienta viola el mínimo privilegio; debería rediseñarse para ejecutar solo consultas específicas y preautorizadas
    - c) Esta herramienta es aceptable porque el agente no la usará mal si el system prompt le dice que no lo haga
    - d) Esta herramienta es aceptable siempre que el agente no tenga capacidad de comunicación externa

<details markdown="1"><summary>Comprobación</summary>

**b)** Esta herramienta viola el mínimo privilegio y debería rediseñarse. Le concede al agente un acceso amplio a la base de datos, lo que viola el principio de la lección 32 de que cada herramienta debe acotarse exactamente a lo que necesita. La opción (a) es incorrecta: la flexibilidad para el desarrollador no es lo mismo que un buen diseño de herramienta. La opción (c) es incorrecta: la lección 31 enseñó que las instrucciones del prompt no son una defensa fiable contra la inyección de prompt; la defensa es arquitectónica. La opción (d) es incorrecta: eliminar la comunicación externa rompería una condición de la tríada, pero la herramienta seguiría teniendo un alcance excesivo respecto a lo que un agente necesita realmente. Un mejor diseño: una herramienta llamada get_customer_orders que tome un customer_id y devuelva sus pedidos, sin ningún vector de inyección SQL.

</details>

4. ▢ Un equipo está revisando dos propuestas para la misma tarea. Propuesta A: un solo agente con acceso a búsqueda web, ejecución de código y herramientas de documentación. Propuesta B: un orquestador con tres workers (especialista en búsqueda, especialista en código, especialista en documentación), cada uno con una herramienta. El equipo ha leído la lección 19 y está dividido. Dos ingenieros defienden que la propuesta A es mejor porque "Cognition dice que los agentes únicos ganan". Otros dos defienden que la propuesta B es mejor porque "el sistema de investigación de Anthropic usó multiagente". Te piden que lo zanjes. ¿Cuál debería ser tu primer paso?

<details markdown="1"><summary>Comprobación</summary>

Volver a las fuentes primarias, no a los resúmenes recordados a medias. Vuelve a leer ambos artículos e identifica las condiciones concretas que describe cada uno: ¿Cuáles eran las características de la tarea, el presupuesto de contexto, la presión de tiempo y la complejidad de coordinación en cada fuente? Luego examina la propuesta A y la propuesta B frente a esas condiciones. ¿Coinciden mejor con las condiciones del agente único o del multiagente? ¿Describen las propias propuestas las características de la tarea y justifican su elección frente a esas condiciones? Tu revisión debería decir algo como: "La propuesta B coincide con las condiciones en las que tuvo éxito el sistema de investigación de Anthropic (subtareas independientes, plazo en tiempo real), si puede justificar el costo de coordinación. La propuesta A coincide con el escenario de Cognition (trabajo que refina el contexto, presupuesto de tiempo abierto), si el menú de herramientas del agente único es lo bastante amplio como para evitar la sobrecarga de decisión entre herramientas". El trabajo no es arbitrar entre las fuentes sino aplicar cada una a la tarea concreta.

</details>

## Prácticas en el mundo real

- [ ] Encuentra un sistema que uses o conozcas que se describa a sí mismo como un agente. Intenta mapearlo contra la lista de revisión de esta lección: ¿dónde se ubica en el espectro de autonomía? ¿Están las herramientas descritas para el razonamiento del modelo o como documentación de API? ¿Habla de seguridad? Anota los puntos de la lista que el sistema atiende con claridad y cuáles deja en silencio.
- [ ] Elige una afirmación de la lección 19 que haga Cognition o Anthropic sobre los sistemas multiagente. Vuelve a leer la fuente e identifica las condiciones concretas bajo las que se sostiene esa afirmación. Anota: ¿qué características de la tarea hacen verdadera o falsa la afirmación? ¿Cómo pondrías a prueba esa afirmación en un sistema que estés diseñando?
- [ ] Mañana: Revisa el diseño de agente de otra persona (del trabajo, de un proyecto de código abierto o de una propuesta técnica). Usa la lista de revisión de esta lección. Anota una pregunta abierta por cada etapa que el diseño no atienda del todo. Comparte la revisión con quien diseñó el sistema y mira si tus preguntas coinciden con sus propias preocupaciones.

## Para profundizar

- [Article: "Building Effective Agents", Anthropic Engineering](https://www.anthropic.com/engineering/building-effective-agents)
- [Recursos](../RESOURCES.md)

---

¿No termina de quedar claro? Vuelve a leer la fuente primaria de arriba, ya que esta lección la comprime y en la compresión es donde se escapa la comprensión. Consulta el [glosario](../GLOSSARY.md) por si algún término te resultó resbaladizo.

Si lo poco claro es la propia lección y no el material, eso es un defecto: [abre un issue](https://github.com/TokenCemetery/teach/issues).
