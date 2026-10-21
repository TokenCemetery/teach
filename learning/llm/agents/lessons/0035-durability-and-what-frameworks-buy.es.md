---
title: "35. Durabilidad y lo que ofrece un framework"
description: "La ejecución durable y reanudable de un agente como problema de ingeniería, lo que ofrecen en concreto los frameworks y un principio de decisión para adoptar uno"
type: lesson
---

# Lección 35. Durabilidad y lo que ofrece un framework

**Vínculo con la misión:** Decidir si escribir tú mismo un harness de agente o adoptar un framework, según qué garantías necesitas realmente para el despliegue.
**Fuente principal:** [Article: "Building Effective Agents", Anthropic Engineering](https://www.anthropic.com/engineering/building-effective-agents)
**Requisitos previos:** [Lección 34](0034-prompt-caching-and-concurrency.md), [Harness](../GLOSSARY.md)

## Calentamiento

1. ▢ De la lección 7, aprendiste que como la transcripción es todo el estado de un agente, reanudar una ejecución significa volver a darle al modelo la transcripción guardada. ¿Qué significa esto respecto a si una ejecución es "reanudable en principio"?

<details markdown="1"><summary>Comprobación</summary>

En principio, cualquier ejecución de un agente es reanudable porque la transcripción captura todo lo que el agente sabe. Si guardas la transcripción después de cada turno y ocurre una caída, puedes cargar la transcripción guardada, añadir el último turno fallido o incompleto y continuar. La transcripción es todo el estado, así que reanudar no requiere nada más.

</details>

2. ▢ De la lección 33, aprendiste que un presupuesto de costo por tarea suma el costo completo de todos los intentos, reintentos y reflexiones hasta que una tarea tiene éxito. Si un agente se cae a mitad de una ejecución y tienes que reiniciar desde el principio, ¿cómo afecta eso al presupuesto de costo por tarea?

<details markdown="1"><summary>Comprobación</summary>

El reinicio añade un intento adicional completo al presupuesto. Si un agente se cae en el turno 15 de una ejecución de 30 turnos, has perdido 15 turnos de trabajo y tienes que pagar los 30 turnos otra vez. El presupuesto de costo por tarea ahora es aproximadamente el doble (dos ejecuciones completas de 30 turnos en lugar de una). Es una penalización de costo significativa, y por eso la durabilidad (evitar las caídas y reanudar automáticamente desde el último estado guardado) importa para el control de costos.

</details>

## Qué debes saber

### La durabilidad es distinta de la capacidad de reanudar en principio

La lección 7 estableció que las ejecuciones de agentes son reanudables en principio: la transcripción es el estado. Pero "reanudable en principio" y "reanudable en producción" son cosas distintas. La capacidad de reanudar en principio dice "si una persona guarda a mano la transcripción y reinicia el agente, continuará". La durabilidad en producción dice:

- La transcripción se persiste automáticamente en almacenamiento durable (una base de datos, un sistema de archivos con copias de seguridad, no solo memoria) después de cada turno.
- Si el proceso se cae, el último estado persistido se carga automáticamente y la ejecución se reanuda sin intervención manual.
- Si varios agentes corren de forma concurrente, el estado de cada uno se sigue de forma independiente para que la caída de uno no pierda el trabajo de otro.
- Si una llamada a herramienta agota el tiempo o falla la red, el agente reintenta o revierte con elegancia, sin dejar un estado parcial.

Este trabajo de infraestructura es distinto del propio bucle del agente (lección 6). Al bucle no le importa la durabilidad; solo procesa lo que se le da. El harness (el código que rodea al bucle) tiene que construir la durabilidad como una preocupación explícita.

### Cómo se ven las caídas y los fallos sin durabilidad

Sin estado durable, estos son los modos de fallo:

- Caída del proceso a mitad de la ejecución: se pierde toda la transcripción del agente (si solo estaba en memoria). El usuario tiene que reiniciar la tarea desde el principio. El presupuesto de costo por tarea se duplica.
- Tiempo agotado de red en una llamada a herramienta: el harness no sabe si la herramienta tuvo éxito o falló. Podría reintentar, o no. La transcripción podría tener un resultado añadido, o no, según el manejo de errores del harness. El estado se vuelve inconsistente.
- El agente se cuelga esperando el resultado de una herramienta: el proceso se atasca y hay que matarlo a mano. No se guarda ningún punto de control. Se pierde toda la ejecución.
- Varios agentes corren de forma concurrente y uno se cae: los demás agentes continúan, pero no hay visibilidad de qué parte del sistema falló ni de cómo reanudar la que falló.

Cada uno de estos es un problema real de despliegue. La "ejecución durable" es la práctica de construir sistemas que manejan estos fallos de forma automática y correcta.

### Qué ofrece en concreto un framework

Cuando adoptas un framework para desarrollar agentes, suele incluir algunas o todas estas garantías:

**Estado durable y puntos de control automáticos.** El framework persiste automáticamente la transcripción (y cualquier estado del agente) en almacenamiento durable después de cada turno. Si el proceso se cae, la siguiente ejecución carga automáticamente el último punto de control y se reanuda desde ahí. No tienes que escribir tú la lógica de persistencia.

**Flujo de control basado en grafos.** En lugar de escribir un bucle a mano (lección 6), describes la estructura del agente como un grafo: "Después de este paso, si el resultado es X, ve aquí; si es Y, ve allá". El framework maneja el flujo de control y la persistencia, de modo que te centras en los nodos (los pasos) y no en el bucle en sí. Esto es útil para agentes con ramificaciones complejas o lógica condicional.

**Políticas integradas de reintento y espera.** Cuando falla una llamada a herramienta (un error de red, un tiempo agotado, un límite de tasa), el framework tiene una estrategia de reintento configurada: esperar un poco, volver a intentar, espera exponencial. No tienes que implementar los reintentos en tu propio harness.

**Trazado y observabilidad integrados.** El framework genera automáticamente las trazas estructuradas de la lección 29: eventos con marca de tiempo, spans, metadatos de cada paso. Puedes consultar esta traza sin cablearla tú. Algunos frameworks se integran con backends de observabilidad (como un servicio de trazado) para que puedas ver las ejecuciones de agentes en un panel.

**Reversión y compensación.** Algunos frameworks te permiten definir acciones compensatorias: si el paso A tuvo éxito pero el paso B falló, deshacer A automáticamente. Esto es útil para agentes que hacen cambios en sistemas externos y necesitan recuperarse si fallan pasos posteriores.

No todos los frameworks ofrecen todo esto. Algunos son mínimos (puntos de control más reintentos). Otros son completos (todo lo anterior y más). El principio de decisión (abajo) trata de qué capacidades necesitas realmente.

### Lo que los frameworks NO ofrecen

Es importante tener claro lo que los frameworks no resuelven:

- El bucle del agente en sí sigue siendo el mismo (de la lección 6). El framework no hace el bucle más simple ni más rápido; solo lo envuelve con durabilidad y observabilidad.
- El costo en tokens no se reduce por usar un framework. Un framework no hace más baratos a los agentes; los hace más fiables y observables.
- La calidad del razonamiento del agente no mejora con un framework. Un framework no hace al modelo mejor tomando decisiones; sigues teniendo que diseñar tú las herramientas, los prompts y la planificación (lecciones 8, 9, 16).
- El framework no es neutral. Adoptar un framework te compromete con sus abstracciones (flujo de control basado en grafos, su formato de configuración, su modelo de observabilidad, sus restricciones de despliegue). Cambiar de framework más adelante es caro.

### El principio de decisión: cuándo adoptar un framework

El artículo "Building Effective Agents" señala que muchos equipos construyen primero un bucle de agente mínimo (lección 6) y solo más tarde se dan cuenta de que necesitan durabilidad. La decisión de adoptar un framework debería basarse en si las garantías del framework resuelven un problema de despliegue que tienes, no en si escribir el bucle te pareció difícil (el bucle es la parte fácil).

Adopta un framework cuando:

- **Necesitas ejecución durable.** Tus agentes correrán durante el tiempo suficiente (o serán lo bastante importantes) como para que perder trabajo por las caídas sea inaceptable. Un bucle simple sin persistencia no es adecuado para tareas de producción.
- **Necesitas observabilidad a escala.** Tienes varios agentes corriendo de forma concurrente y necesitas ver qué hace cada uno, rastrear fallos y correlacionar logs. Un harness básico con sentencias de impresión no escalará.
- **Tienes un flujo de control complejo.** Tu agente necesita ramificaciones condicionales o bucles (por ejemplo, "si se da esta condición, llama a este conjunto de herramientas; si no, llama a este otro conjunto"). El modelo basado en grafos de un framework es más limpio que los condicionales escritos a mano.
- **Quieres reintentos y esperas integrados.** Estás llamando a APIs externas que podrían fallar de forma temporal, y quieres que el framework maneje los reintentos de forma automática con espera exponencial. Escribir esto tú mismo es tedioso y propenso a errores.

NO adoptes un framework cuando:

- **Estás experimentando.** En investigación o prototipado, un bucle simple es más rápido de iterar que aprender un framework. Vuelve a la decisión sobre el framework cuando el enfoque sea estable.
- **Tu agente es simple.** Un solo agente con unas pocas llamadas a herramientas y un objetivo directo no necesita la complejidad de un framework. Un bucle más un archivo de transcripción podría ser todo lo que necesitas.
- **Tienes restricciones de despliegue inusuales.** Algunos frameworks asumen entornos específicos (nube, Docker, etc.) o tienen características de rendimiento que no encajan con tus restricciones. Podrías necesitar un harness a medida.
- **El framework es inmaduro o está muy acoplado a un proveedor.** Los patrones de ejecución durable siguen evolucionando. Algunos frameworks están bien asentados y documentados (busca reseñas y despliegues en producción); otros no. Y algunos están muy acoplados a la API de un proveedor, lo que limita tu flexibilidad más adelante.

### Cómo evaluar un framework

Si decides adoptar un framework, estas son las preguntas que hacer:

- ¿Admite puntos de control y reanudación? ¿Con qué frecuencia? ¿La granularidad del punto de control (por turno, por intento, por tarea) es la que necesitas?
- ¿Qué observabilidad ofrece? ¿Puedes consultar trazas? ¿Puedes integrarlo con tu registro y monitoreo existentes?
- ¿Qué abstracciones de flujo de control admite? ¿Encaja con la estructura de tu agente, o tendrías que doblar tu agente para que encaje?
- ¿Cuál es el modo de fallo si el framework se cae? ¿Puedes recuperar tus transcripciones y continuar sin el framework?
- ¿Cómo maneja la concurrencia? ¿Pueden correr varios agentes de forma independiente sin interferir?
- ¿Qué dependencia de un proveedor hay? Si necesitas cambiar más adelante, ¿cuánto trabajo sería?

La última pregunta es importante: no hay una única fuente autorizada y neutral respecto al proveedor para la ejecución durable de agentes, como la hay, por ejemplo, para la especificación de MCP (lección 20). Los patrones de ejecución durable están documentados sobre todo dentro de las propias guías de cada framework. Así que trata esta lección como el vocabulario y el marco de decisión, no como una comparación de frameworks. Cuando evalúes un framework concreto, lee su propia documentación para entender sus garantías específicas.

### La historia de principio a fin: del bucle a la producción

Este es el arco de un sistema de agentes típico:

1. **Desarrollo (lección 6).** Escribe un bucle que envía la transcripción al modelo y ejecuta herramientas. Es rápido de prototipar.
2. **Pruebas (lección 29).** Construye trazas y diagnóstico para entender qué hace tu agente, cuándo falla y por qué. Aprende dónde es frágil tu agente.
3. **Optimización (lecciones 10 a 34).** Implementa la gestión del contexto, el prompt caching, una mejor planificación. Reduce el costo en tokens y la latencia.
4. **Despliegue.** Ahora tienes que decidir: ¿cómo se ve la producción? Si es una tarea puntual o un experimento, un script más un archivo de transcripción podría bastar. Si es un servicio que atiende a usuarios, un bucle simple no es adecuado. Necesitas durabilidad, observabilidad, políticas de reintento y una forma de seguir a muchos agentes concurrentes. Aquí es donde entra la decisión sobre el framework.

Un framework no es el principio; es la respuesta a "¿quién construye y mantiene la capa de durabilidad y observabilidad?" La construyes tú mismo (un harness a medida más infraestructura), o adoptas la respuesta de un framework (aceptas sus abstracciones y restricciones). Ambas son opciones legítimas. La decisión sobre el framework no es "¿puedo escribir un bucle de agente?" (la lección 6 ya respondió que sí). La pregunta es "¿quiero construir yo mismo esta infraestructura de producción, o adoptar la solución de un framework existente?"

## Práctica

1. ▢ Estás ejecutando un agente para procesar 1.000 tickets de atención al cliente. Cada ticket le lleva al agente 20 turnos. Si el agente se cae en el turno 10 del ticket 500 y no tienes puntos de control, ¿cuántos turnos en total se pierden o se desperdician?

<details markdown="1"><summary>Comprobación</summary>

Pierdes 10 turnos de trabajo en el ticket 500. Cuando el proceso se reinicia, tienes que volver a ejecutar el ticket entero desde el principio, desperdiciando otros 20 turnos. También tienes que volver a ejecutar los tickets 1-499 (que se completaron pero siguen en memoria o se pierden si el proceso se cayó). Si hubieras tenido puntos de control, guardarías después de cada ticket, así que perder un ticket cuesta 20 turnos, no más. Para 1.000 tickets * 20 turnos = 20.000 turnos en total. Sin puntos de control, una caída a mitad de una tarea desperdicia aproximadamente 10.000 turnos (la mitad del trabajo restante más volver a ejecutar la tarea que se cayó). Por eso importa la durabilidad en las tareas a gran escala.

</details>

2. ▢ Tienes dos opciones para tu sistema de agentes: la opción A es escribir un harness a medida con durabilidad (puntos de control, reintentos, observabilidad). Esto lleva 2 semanas de construcción y depuración. La opción B es adoptar un framework existente (que maneja todo esto por ti) y dedicar 1 semana a aprenderlo. Ambos sistemas ejecutarán la misma lógica de agente. ¿Por qué podría seguir siendo más cara la opción B a largo plazo?

<details markdown="1"><summary>Pista</summary>

Piensa en la flexibilidad, el mantenimiento y lo que pasa si cambian tus requisitos o quieres cambiar de sistema.

</details>

<details markdown="1"><summary>Comprobación</summary>

La opción B te compromete con las abstracciones y la implementación del framework. Si tus requisitos cambian (por ejemplo, necesitas un flujo de control distinto o un backend de almacenamiento distinto), estás limitado por lo que admite el framework. Si quieres cambiar de framework más adelante, tienes que portar todas las definiciones y flujos de tus agentes. La opción A (harness a medida) es más flexible pero más cara al principio y de mantener. El intercambio es: la opción B ahorra tiempo al principio pero te ata; la opción A cuesta más al principio pero te da flexibilidad a largo plazo. El punto de equilibrio depende de cuánto esperas que dure el sistema y de qué probabilidad hay de que cambien los requisitos.

</details>

3. ▢ Estás evaluando dos frameworks para el desarrollo de agentes. El framework X ofrece puntos de control y reintentos pero ninguna observabilidad integrada (tienes que cablear tú el trazado). El framework Y ofrece todo eso más un constructor de flujo de control basado en grafos, pero exige que todos los agentes se definan en su DSL propietario. ¿Qué framework deberías elegir si tu principal preocupación es evitar trabajo cuando un agente se cae y reanudar automáticamente?

    - a) El framework X, porque es más simple y te obliga a aprender menos.
    - b) El framework Y, porque su observabilidad integrada te ayudará a depurar las caídas más rápido.
    - c) Cualquiera de los dos ofrece la función central de puntos de control que necesitas; la elección depende de tus otras restricciones.
    - d) Ninguno; deberías construir un harness a medida para no quedar atado.

<details markdown="1"><summary>Comprobación</summary>

**c)** Ambos frameworks ofrecen puntos de control y reanudación automática, que es tu principal preocupación. Las diferencias (observabilidad, DSL) son secundarias. Si necesitas observabilidad integrada o te gusta el modelo basado en grafos, el framework Y podría valer la dependencia. Si prefieres cablear tú la observabilidad o tienes código de agentes existente en Python/Go/etc., el framework X está bien. Ninguno está equivocado; depende de tus otras restricciones. La opción a es incorrecta porque la simplicidad por sí sola no es el factor decisivo. La opción b confunde la observabilidad (deseable) con la durabilidad (el requisito que indicaste). La opción d no es incorrecta (un harness a medida siempre te da flexibilidad) pero esquiva la pregunta; si la durabilidad es importante, necesitas alguna solución, y la decisión es si esa solución es un framework o algo a medida.

</details>

4. ▢ Has construido un agente con un bucle simple (lección 6) sin persistencia. El agente funciona bien en las pruebas. Ahora quieres desplegarlo en producción para manejar peticiones reales de usuarios. ¿Cuál es la infraestructura mínima que necesitas añadir antes de poder decir con confianza que el agente es durable en producción?

<details markdown="1"><summary>Comprobación</summary>

Como mínimo: (1) Persistencia automática de la transcripción en almacenamiento durable (una base de datos o un sistema de archivos con copias de seguridad) después de cada turno del bucle. (2) Carga automática de la última transcripción persistida al reiniciar el proceso, para que el agente se reanude desde el último punto de control, no desde el principio. (3) Manejo de errores elegante para las llamadas a herramientas: si una herramienta agota el tiempo o devuelve un error, el agente o bien reintenta con una política de espera o bien registra explícitamente el fallo en la transcripción (para que el estado sea consistente). (4) Para agentes concurrentes, cada agente debe tener su propia transcripción y punto de control aislados. Estas cuatro piezas convierten un bucle de desarrollo en algo que puede sobrevivir a las caídas y atender tráfico de producción.

</details>

## Prácticas en el mundo real

- [ ] Revisa la documentación de un framework de agentes de producción (por ejemplo, LangGraph, CrewAI, los Managed Agents de Anthropic u otro framework que conozcas). Anota las garantías concretas de durabilidad que ofrece: qué se persiste, con qué frecuencia y cómo se maneja la recuperación.
- [ ] Diseña la capa de durabilidad de un agente simple. Escribe las piezas que tendrías que construir: puntos de control (qué y cuándo), reanudación (cómo y cuándo), manejo de errores (reintentos, esperas), observabilidad (qué registrar). Estima cuántas líneas de código llevaría construirlo y probarlo bien.
- [ ] Mañana: Esboza una tarea hipotética de agente y estima sus requisitos de despliegue. ¿Sería aceptable un bucle simple más un archivo de transcripción para tu caso de uso, o necesitarías durabilidad y observabilidad a nivel de framework? Anota la decisión y el razonamiento.

## Para profundizar

- [Article: "Building Effective Agents", Anthropic Engineering](https://www.anthropic.com/engineering/building-effective-agents)
- [Recursos](../RESOURCES.md)

---

¿No termina de quedar claro? Vuelve a leer la fuente primaria de arriba, ya que esta lección la comprime y en la compresión es donde se escapa la comprensión. Consulta el [glosario](../GLOSSARY.md) por si algún término te resultó resbaladizo.

Si lo poco claro es la propia lección y no el material, eso es un defecto: [abre un issue](https://github.com/TokenCemetery/teach/issues).
