---
title: "34. Prompt caching y concurrencia"
description: "Cómo el caching reduce el costo en tokens por tarea y cómo la concurrencia aumenta el rendimiento, y por qué confundirlos es un error de presupuesto"
type: lesson
---

# Lección 34. Prompt caching y concurrencia

**Vínculo con la misión:** Presupuestar el costo en tokens y la latencia de un bucle agéntico, y decir de qué parte del bucle viene la amplificación.
**Fuente principal:** [Docs: "Prompt caching", Claude Platform Docs](https://platform.claude.com/docs/en/build-with-claude/prompt-caching)
**Requisitos previos:** [Lección 33](0033-token-amplification-and-cost.md)

## Calentamiento

1. ▢ De la lección 33, aprendiste que las definiciones de herramientas se reenvían al modelo en cada turno del bucle, consumiendo tokens aunque nunca cambian. ¿Qué parte del contexto es esta, y por qué ayudaría el caching?

<details markdown="1"><summary>Comprobación</summary>

Las definiciones de herramientas son un prefijo estable de cada mensaje al modelo: no cambian a mitad de la ejecución. El caching ayuda porque una caché almacena ese prefijo estable tras la primera petición y lo reutiliza en las peticiones siguientes de la misma trayectoria, cobrando solo por el contenido nuevo que se le añade.

</details>

2. ▢ De la lección 19, recuerda: ¿reduce ejecutar tres agentes en paralelo el costo en tokens de resolver un problema en comparación con ejecutar un agente en serie?

<details markdown="1"><summary>Comprobación</summary>

No. Ejecutar tres agentes en paralelo aumenta el costo total en tokens porque cada agente paga su costo completo de forma independiente. El paralelismo reduce el tiempo real pero no el costo en tokens. Cada agente en paralelo sigue teniendo que leer la tarea, ejecutar su bucle y transmitir su transcripción al modelo.

</details>

## Qué debes saber

### Cómo funciona el prompt caching

El prompt caching es un mecanismo que almacena un prefijo estable de una petición tras la primera llamada y lo reutiliza en las llamadas siguientes sin cobrarlo de nuevo a precio completo. La caché es específica de una secuencia de peticiones; las peticiones de distintos usuarios o de distintas ejecuciones de agentes no comparten caché.

Esta es la mecánica:

1. En el primer mensaje de una trayectoria, envías una petición completa: system prompt, definiciones de herramientas y la tarea.
2. El modelo la procesa de forma normal y cobra el costo completo en tokens.
3. La respuesta incluye metadatos: "Cached 4,000 tokens" (o cuando fuera el prefijo estable).
4. En el segundo mensaje de la misma trayectoria, añades contenido nuevo a la petición: quizá un resultado de herramienta, la siguiente instrucción o un turno de seguimiento.
5. El modelo reutiliza el prefijo almacenado en caché (system prompt, herramientas, tarea) y solo cobra por el contenido recién añadido.
6. Esto se repite: cada turno nuevo de la misma trayectoria solo paga por lo que cambió desde el último turno.

La caché tiene un costo: el primer turno paga el precio completo, y hay un pequeño cargo adicional por las consultas y el almacenamiento de la caché. Pero en una trayectoria larga, esa sobrecarga se justifica con facilidad. Si tienes 30 turnos y las definiciones de herramientas son 2.000 tokens, la caché ahorra aproximadamente 2.000 * 28 = 56.000 tokens (las definiciones no se reenvían en los turnos 2 a 29, así que ahorras su costo 28 veces).

### Qué invalida una caché

Una caché solo es útil si el prefijo es realmente estable. Varias cosas invalidan una caché en silencio, lo que importa para el diseño del harness:

**Reordenar las definiciones de herramientas.** Si serializas tu lista de herramientas de forma distinta en el turno 1 que en el turno 2 (por ejemplo, alfabéticamente en el turno 1, por frecuencia en el turno 2), el prefijo ya no coincide y la caché queda invalidada. Un harness debe serializar siempre las herramientas en el mismo orden, en cada turno.

**Interpolar valores dinámicos en el system prompt.** Si tu system prompt incluye una marca de tiempo ("Current time: 2024-09-13"), un ID de usuario o cualquier valor por llamada, ese valor cambia entre turnos y el prefijo deja de ser estable. La caché queda invalidada en cada turno. Esto anula el caching por completo. Si necesitas valores dinámicos, ponlos después de las herramientas (en la parte de la petición que no se almacena en caché).

**Editar mensajes anteriores.** Si un harness edita en el sitio los mensajes antiguos (en lugar de solo añadir), la caché queda invalidada desde ese punto de edición hacia delante. La lección 7 enseñó que la transcripción es el estado del agente; esa filosofía defiende añadir solamente y no tocar nunca los mensajes antiguos. El prompt caching lo refuerza: cualquier edición rompe la caché.

### El caching resuelve el costo de "definiciones de herramientas reenviadas en cada turno" de la lección 33

La documentación de la fuente principal, "Prompt caching", señala que las definiciones de herramientas y los system prompts son exactamente el tipo de contenido estable, grande y repetido para el que se construyó el caching. Un harness de 10 herramientas con 2.000 tokens de descripciones de herramientas ahora cuesta esos 2.000 tokens solo una vez por trayectoria, no una vez por turno. En una trayectoria de 50 turnos, esto por sí solo ahorra aproximadamente 98.000 tokens (las definiciones aparecen 50 veces sin caching, 1 vez con caching, así que se ahorran 49 * 2.000 = 98.000 tokens).

Por eso las lecciones 33 y 34 van emparejadas: la lección 33 identifica el desperdicio, la lección 34 nombra la solución.

### Concurrencia: otra palanca distinta y complementaria

El prompt caching reduce el costo de cualquier ejecución individual de un agente. La concurrencia es una pregunta aparte: ejecutar varias instancias de agentes en paralelo.

La concurrencia puede adoptar varias formas:

- Ejecutar la misma tarea con la misma entrada en varios agentes en paralelo, para ver si producen respuestas distintas (útil en tareas donde existen varias soluciones válidas).
- Ejecutar variaciones de una tarea en paralelo (fan-out de la lección 19), donde cada agente resuelve una subtarea.
- Ejecutar varias tareas independientes de usuarios en paralelo (un sistema que atiende a muchos usuarios, cada uno con su propia instancia de agente).

En cada caso, la concurrencia aumenta el rendimiento: se completan más tareas por unidad de tiempo real. Pero la concurrencia NO reduce el costo en tokens de ninguna tarea individual. Si ejecutas tres agentes en paralelo y cada uno cuesta 100.000 tokens, el total es 300.000 tokens, no 100.000 dividido entre 3. El paralelismo cambia tiempo por tokens.

### El error: confundir el caching con la concurrencia

Un error de presupuesto común es asumir que ejecutar varios agentes en paralelo de algún modo hace a cada uno más barato en tokens. No es así. Esta es la confusión:

- Correcto: El caching reduce el costo en tokens de la larga trayectoria de un solo agente evitando reenviar prefijos estables.
- Correcto: La concurrencia reduce el tiempo real ejecutando agentes en paralelo.
- Incorrecto: "Ejecutamos agentes de forma concurrente, así que el costo en tokens por agente es menor".

La concurrencia reduce el tiempo, no los tokens. Ejecutar agentes más rápido (en paralelo) no los hace más baratos (en tokens). Si necesitas reducir el costo y ya tienes caching, las palancas son:

- Mejor planificación (lección 16) para reducir el número de turnos.
- Mejor recuperación (lección 11) para reducir el tamaño de la transcripción.
- Menos workers (lección 19) para reducir la duplicación multiagente.
- Fallar más rápido (el diagnóstico de la lección 29) para reducir los intentos desperdiciados.

### Presupuesto de tokens: dos preguntas

Al diseñar un sistema agéntico, hazte dos preguntas separadas:

1. **Costo por tarea completada:** ¿Cuántos tokens necesitará un agente para resolver una tarea de forma fiable? Aquí es donde ayuda el caching, ayuda la planificación y cuesta la reflexión.
2. **Rendimiento:** ¿Cuántas tareas necesitas completar por segundo o por minuto? Aquí es donde ayuda la concurrencia. Si necesitas 10 tareas por segundo y cada tarea tarda 1 segundo en completarse en serie, necesitas al menos 10 agentes corriendo en paralelo.

Confundir estas preguntas lleva a decisiones equivocadas. Si intentas reducir el costo por tarea, añadir más agentes concurrentes no ayuda. Si intentas aumentar el rendimiento y tienes un plazo, añadir concurrencia es la palanca correcta (pero pagas en tokens totales: 10 agentes * costo por tarea = presupuesto total).

## Práctica

1. ▢ El system prompt y las definiciones de herramientas de tu agente suman 5.000 tokens. El agente corre durante 30 turnos en una sola tarea. Sin prompt caching, ¿cuántas veces se envían esos 5.000 tokens al modelo? ¿Y con caching?

<details markdown="1"><summary>Comprobación</summary>

Sin caching: 30 veces (una por turno), para un total de 150.000 tokens de sobrecarga de definiciones. Con caching: una vez en el primer turno, y luego reutilizado en todos los turnos siguientes, así que en la práctica una vez. (Con más precisión, hay una pequeña sobrecarga para recuperar la caché en cada turno, pero los 5.000 tokens completos no se retransmiten.) El caching ahorra aproximadamente 145.000 tokens en este caso.

</details>

2. ▢ Estás implementando prompt caching en tu harness. La lista de herramientas se genera de forma dinámica: en el turno 1, el agente tiene acceso a las herramientas A, B, C; en el turno 3, el harness añade la herramienta D. Las herramientas se serializan en el orden en que se generan (A, B, C en el turno 1; A, B, C, D en el turno 3). ¿Seguirá siendo válida en el turno 3 la caché del turno 1? ¿Por qué sí o por qué no?

<details markdown="1"><summary>Pista</summary>

¿Qué ha cambiado entre la petición del turno 1 y la del turno 3? ¿Ese cambio forma parte del prefijo almacenado en caché, o está después?

</details>

<details markdown="1"><summary>Comprobación</summary>

No, la caché es inválida. En el turno 1, el prefijo contiene "tools: A, B, C". En el turno 3, el prefijo contiene "tools: A, B, C, D". Los prefijos no coinciden, así que la caché no se aplica. El harness tiene que enviar de nuevo las definiciones completas. Por eso añadir herramientas de forma dinámica (añadir una herramienta a mitad de la ejecución según las decisiones del agente) rompe el caching. Un harness que quiera caching debería o bien comprometerse con un conjunto fijo de herramientas desde el principio, o bien aceptar que añadir herramientas a mitad de la ejecución invalida la caché.

</details>

3. ▢ Estás diseñando el system prompt de un agente con caché. El prompt incluye "Current date: 2024-09-13" para situar al modelo en el tiempo. ¿Por qué esto es un problema de caching?

    - a) La fecha no es relevante para el modelo y debería eliminarse.
    - b) La fecha cambia cada día, así que el prefijo almacenado en caché quedaría obsoleto tras un día.
    - c) La fecha es un valor dinámico que cambia entre ejecuciones, lo que invalida la caché en cada ejecución porque el prefijo ya no coincide.
    - d) Ningún sistema puede almacenar fechas en caché.

<details markdown="1"><summary>Comprobación</summary>

**c)** El system prompt forma parte del prefijo almacenado en caché. Si incluyes una fecha fija en el código que es distinta en la ejecución 1 que en la ejecución 2, el prefijo almacenado de la ejecución 1 no coincide con la petición de la ejecución 2, así que la caché no sirve. La solución es excluir la fecha del prefijo almacenado en caché (ponerla después de las herramientas, en el contenido por turno), o usar una fecha fija para todas las ejecuciones si la fecha no es realmente crítica. Este es un error común: incluir metadatos por ejecución en la parte almacenada en caché anula el caching.

</details>

4. ▢ Tienes dos opciones para escalar tu sistema de agentes: la opción A es optimizar el costo por tarea de un agente mediante caching y planificación, bajándolo de 100.000 tokens a 60.000 tokens. La opción B es ejecutar diez agentes en paralelo sin optimización, cada uno costando todavía 100.000 tokens. Si necesitas completar 10 tareas y tienes cómputo ilimitado, ¿qué opción minimiza el costo en tokens?

<details markdown="1"><summary>Comprobación</summary>

Opción A: 10 tareas \* 60.000 tokens por tarea = 600.000 tokens en total. Opción B: 10 tareas \* 100.000 tokens por tarea = 1.000.000 tokens en total, aunque corran en paralelo. La concurrencia aumenta la velocidad (la opción B se completa en el tiempo de una tarea, mientras que la opción A se completa en 10 veces esa duración en serie) pero no el costo. La opción A es más barata en tokens. Si necesitas completar 10 tareas lo más rápido posible, combinarías ambas: optimizar cada agente a 60.000 tokens (el enfoque de la opción A) y ejecutar 10 agentes optimizados en paralelo, para un total de 600.000 tokens y el menor tiempo real.

</details>

## Prácticas en el mundo real

- [ ] Mira un harness de agente que hayas escrito o revisado. Encuentra dónde se serializan el system prompt y las definiciones de herramientas. Verifica que siempre se serializan en el mismo orden, y que no se interpolan valores dinámicos (marcas de tiempo, IDs de usuario, metadatos específicos de la ejecución) en esa sección. Si se interpolan, anota cómo eso rompe el caching.
- [ ] Estima el ahorro de tokens del prompt caching para una tarea que conozcas. Adivina: tamaño del system prompt y de las definiciones de herramientas, número de turnos, tokens por turno. Calcula cuántos tokens se ahorran al no reenviar las definiciones. ¿Vale el ahorro la complejidad de implementar el caching?
- [ ] Mañana: Diseña una tarea que se beneficie de la concurrencia (ya sea varios usuarios, varias subtareas independientes o varios intentos de la misma tarea). Estima el presupuesto total de tokens si ejecutas los agentes en serie (uno a la vez) frente a en paralelo. Muestra que ambos presupuestos son iguales, y explica qué ganas y qué pierdes con cada enfoque.

## Para profundizar

- [Docs: "Prompt caching", Claude Platform Docs](https://platform.claude.com/docs/en/build-with-claude/prompt-caching)
- [Recursos](../RESOURCES.md)

---

¿No termina de quedar claro? Vuelve a leer la fuente primaria de arriba, ya que esta lección la comprime y en la compresión es donde se escapa la comprensión. Consulta el [glosario](../GLOSSARY.md) por si algún término te resultó resbaladizo.

Si lo poco claro es la propia lección y no el material, eso es un defecto: [abre un issue](https://github.com/TokenCemetery/teach/issues).
