---
title: "18. Orquestador y worker"
description: "Diseñar un sistema multiagente en el que un agente planifica y delega, y los workers ejecutan en paralelo"
type: lesson
---

# Lección 18. Orquestador y worker

**Vínculo con la misión:** Para elegir entre un solo agente bien equipado y un sistema multiagente, necesitas entender qué pueden hacer los sistemas multiagente que un solo agente no puede, empezando por el patrón orquestador-worker que impulsa la mayoría de los sistemas multiagente de investigación y planificación.
**Fuente principal:** [Article: "How We Built Our Multi-Agent Research System", Anthropic Engineering](https://www.anthropic.com/engineering/multi-agent-research-system)
**Requisitos previos:** [Lección 17](0017-self-critique-and-reasoning-models.md), [Subagente](../GLOSSARY.md)

## Calentamiento

1. ▢ De la lección 17, recuerda: ¿qué hace un bucle de reflexión explícito después de un intento fallido, y por qué un modelo con razonamiento interno extendido necesita menos ese bucle externo que un modelo estándar?

<details markdown="1"><summary>Comprobación</summary>

Un bucle de reflexión explícito genera una crítica en lenguaje natural de por qué falló el intento y lleva esa crítica al siguiente intento, como un paso separado del propio turno del modelo. Un modelo que hace razonamiento interno extendido antes de responder puede detectar algunos de los mismos errores dentro de un solo turno, así que el bucle externo se gana su costo con menos frecuencia, aunque sigue ayudando cuando la señal de fallo (un error de herramienta, un resultado de prueba) solo existe después de que el modelo ya actuó.

</details>

2. ▢ De la lección 12, recuerda: ¿qué es un subagente, y qué problema resuelve su transcripción separada?

<details markdown="1"><summary>Comprobación</summary>

Un subagente es una ejecución de agente separada con su propio harness y su propia transcripción. Resuelve el aislamiento de contexto: puedes lanzar un subagente enfocado en una tarea acotada sin que la transcripción de esa tarea infle el contexto del agente padre, manteniendo claro el razonamiento del padre para la síntesis y la coordinación.

</details>

## Qué debes saber

### El patrón orquestador-worker

Cuando una tarea es demasiado amplia para el contexto de un solo agente o necesita exploración en paralelo, el patrón orquestador-worker reparte el trabajo: un agente (el orquestador) divide la tarea en subtareas acotadas, decide qué worker recibe cada subtarea y luego sintetiza sus resultados en una respuesta final. Cada worker es un subagente con su propia transcripción y sus propias herramientas, que corre de forma independiente (y a menudo en paralelo).

Piénsalo como un líder de equipo que no hace el trabajo directamente sino que coordina: el líder desglosa un proyecto, asigna partes a los miembros del equipo y reúne sus entregables. Los workers nunca ven el razonamiento completo de los demás; el orquestador solo ve sus informes finales.

### Qué hacen los workers

Los workers no son intercambiables. Cada worker suele tener:

- Una misión acotada y específica (por ejemplo, "investiga este único ángulo", "evalúa este enfoque candidato")
- Herramientas a medida para esa misión (por ejemplo, recuperación para un worker de investigación, ejecución de código para un worker de evaluación)
- Su propio bucle de agente y su propia transcripción, aislados de los demás workers

Como los workers corren sus propios bucles, pueden explorar de forma independiente. Un worker no necesita saber qué hacen los demás workers; solo conoce su propia tarea. Esta independencia es lo que hace posible el paralelismo: muchos workers pueden correr a la vez, y el tiempo real queda acotado por el worker más lento, no por la suma de los tiempos de todos los workers.

### Fan-out: exploración en paralelo

El fan-out es un subcaso del orquestador-worker en el que el orquestador lanza varios workers sobre variaciones de la misma pregunta. Por ejemplo:

- Un worker investiga el ángulo A, otro el ángulo B, un tercero el ángulo C, todos en paralelo, para obtener una cobertura más amplia más rápido que un solo agente que los recorre en serie.
- Tres workers intentan cada uno resolver el mismo problema de programación con estrategias distintas, y el orquestador elige la mejor solución o combina las ideas.

La aceleración es real: en lugar de un solo agente que gasta 10 turnos en el problema A, luego 10 en el B y luego 10 en el C (30 turnos en total), tres workers abordan A, B y C en paralelo (10 turnos de latencia en lugar de 30). La trampa (que se explora en la lección 19) es que pagas el costo en tokens de las ejecuciones completas de los tres workers, no solo de la ejecución de un agente.

### Traspaso: especialización secuencial

El traspaso es otro patrón multiagente, que también usa subagentes pero con fases secuenciales en lugar de workers en paralelo. En el traspaso:

1. El agente A termina su parte de la tarea.
2. El agente A traspasa al agente B dándole un contexto limpio y acotado: normalmente solo la definición de la tarea y los hallazgos finales del agente A, no la trayectoria completa del agente A.
3. El agente B retoma desde ahí, usando sus propias herramientas y su propio razonamiento especializados.

El traspaso es útil cuando una tarea se divide de forma natural en fases secuenciales manejadas por distintos especialistas. Por ejemplo: un orquestador descubre que un problema necesita tanto investigación profunda como implementación, así que traspasa los hallazgos a un programador especializado; o un planificador termina un plan y se lo traspasa a un ejecutor con solo el plan, no con el razonamiento desordenado sobre por qué se eligió ese plan.

El traspaso y el fan-out son opuestos en ritmo: el fan-out es muchos en paralelo, el traspaso es uno tras otro. Ambos son multiagente; ambos aíslan el contexto usando subagentes; ambos se enseñan en esta lección porque ambos responden a la pregunta "¿cuándo no basta un solo agente?"

### Por qué los sistemas orquestador-worker aportan valor en la práctica

La fuente principal detalla un sistema multiagente de investigación concreto construido en Anthropic: descomponer una tarea de investigación compleja en muchas subtareas de investigación independientes, lanzar un worker para cada una, recuperar y analizar fuentes en paralelo y luego sintetizar los hallazgos en una respuesta cohesionada. Las ganancias clave fueron:

- Paralelismo en tiempo real: una investigación compleja a la que un solo agente dedicaría más de 50 turnos podía hacerse más rápido con 5 workers, cada uno con 15 turnos, corriendo a la vez.
- Herramientas especializadas por worker: un worker de recuperación puede centrarse en la búsqueda y el ranking sin el inflado de contexto de la ejecución de código; un worker de síntesis tiene un objetivo distinto y herramientas distintas.
- Razonamiento independiente: cada worker razona sobre su propia porción del problema; los workers no se distraen con información destinada a otros workers.

Este patrón surgió como solución práctica a una restricción real: la capacidad de un modelo para razonar bien sobre una tarea compleja está acotada en parte por la longitud del contexto y en parte por la necesidad de mantener enfocado el razonamiento. Dividir el trabajo te permite añadir más poder de razonamiento (más workers, cada uno con su propio presupuesto de contexto) sin que un solo agente pierda el foco o se quede sin contexto.

## Práctica

1. ▢ Estás construyendo un sistema para responder preguntas de usuarios sobre un código base grande. Consideras dos diseños: (A) un solo agente con acceso a herramientas de búsqueda de código y herramientas de documentación, o (B) un orquestador que delega en un worker de búsqueda y un worker de documentación en paralelo. ¿Qué diseño encaja de forma más natural con el patrón orquestador-worker, y por qué?

<details markdown="1"><summary>Comprobación</summary>

El diseño (B) encaja con el patrón. El worker de búsqueda y el worker de documentación tienen tareas independientes: uno busca en el código, el otro busca en la documentación. Pueden correr en paralelo sin necesitar los resultados del otro a mitad de la tarea. El trabajo del orquestador es claro: formular consultas para cada worker y luego combinar sus hallazgos.

El diseño (A) también podría funcionar, pero el único agente tendría que decidir a mitad de la tarea qué herramienta usar a continuación; no hay ganancia de paralelismo. Elegirías (B) cuando esperes que las consultas de búsqueda y de documentación sean independientes y se beneficien de la exploración en paralelo; elegirías (A) si las consultas dependen una de otra (los resultados de la búsqueda informan qué documentación traer) o si la sobrecarga de lanzar dos subagentes pesa más que la ganancia de velocidad (una tarea más simple).

</details>

2. ▢ En un sistema orquestador-worker, ¿por qué un worker no puede ver directamente el razonamiento de otro worker a mitad de la tarea?

<details markdown="1"><summary>Pista</summary>

Piensa en la estructura: cada worker tiene su propia transcripción y su propio harness. ¿Qué impide ese aislamiento?

</details>

<details markdown="1"><summary>Comprobación</summary>

Cada worker corre su propio bucle de agente con su propia transcripción. El razonamiento del worker A queda registrado en la transcripción del worker A, y el razonamiento del worker B está en la transcripción del worker B. El harness no las fusiona. Los workers no tienen acceso a las transcripciones de los demás durante sus ejecuciones; solo pueden leer los informes finales que les da el orquestador (si el orquestador se los pasa). Este aislamiento mantiene enfocado el contexto de cada worker y es la razón por la que los subagentes resuelven problemas de contexto. El intercambio es la fragmentación: una decisión que necesita el razonamiento completo de ambos workers no la puede tomar ninguno de los dos por sí solo (se cubre en la lección 19).

</details>

3. ▢ Estás diseñando un sistema de investigación. Escenario: un worker investiga la historia de una tecnología, y un segundo worker investiga las aplicaciones actuales de esa tecnología. ¿Pueden correr en paralelo las tareas de estos workers?

    - a) No, porque el worker de aplicaciones necesita conocer primero la historia.
    - b) Sí, ambos workers pueden investigar de forma independiente; el orquestador puede sintetizar los hallazgos sobre historia y aplicaciones sin importar el orden.
    - c) No, porque están investigando la misma tecnología.
    - d) Sí, solo si el worker de historia termina antes de que empiece el worker de aplicaciones.

<details markdown="1"><summary>Comprobación</summary>

**b)** Ambas tareas son independientes: un worker que investiga la historia no necesita los hallazgos del otro worker para investigar bien la historia, y viceversa. El orquestador tendrá ambos resultados cuando terminen los dos workers y podrá sintetizarlos en una respuesta completa. (a) es incorrecta: las dependencias correrían una tras otra (traspaso), no en fan-out; aquí no hay dependencia. (c) es incorrecta: investigar la misma tecnología no es un obstáculo para el paralelismo; de hecho, por eso es útil el fan-out, para obtener varios ángulos sobre el mismo tema. (d) es incorrecta: paralelismo significa que corren al mismo tiempo, no uno tras otro.

</details>

4. ▢ ¿En qué se diferencia un traspaso del fan-out?

<details markdown="1"><summary>Comprobación</summary>

El fan-out es paralelo: el orquestador lanza varios workers a la vez sobre variaciones del mismo problema. El traspaso es secuencial: un agente termina y luego pasa sus hallazgos a un segundo agente hecho a medida para la siguiente fase. El fan-out pregunta "¿cómo podemos explorar más ángulos en paralelo?"; el traspaso pregunta "¿cómo podemos dividir un proceso secuencial en fases especializadas?" Ambos usan subagentes; ambos aíslan el contexto; ambos responden a "¿cuándo no basta un solo agente?" pero con ritmos distintos.

</details>

## Prácticas en el mundo real

- [ ] La próxima vez que veas una tarea compleja (investigación, planificación, depuración), esboza si encaja con orquestador-worker (¿hay subtareas independientes que puedan correr en paralelo?), traspaso (¿hay fases secuenciales para distintos especialistas?) o un solo agente con más herramientas (¿puede un agente hacerlo con mejores herramientas y más turnos?). No construyas nada; solo practica el reconocimiento de formas.
- [ ] Lee el artículo de la fuente principal: "How We Built Our Multi-Agent Research System". Céntrate en la sección que describe qué hizo el orquestador, qué hizo cada worker y qué habría cambiado si hubieran usado un solo agente. Toma notas de una ganancia concreta del paralelismo que reportaron.
- [ ] Mañana: describe una tarea real de tu trabajo o estudio que se beneficiaría del fan-out (varios workers explorando el mismo problema en paralelo). ¿Qué ángulo tomaría cada worker? ¿Qué herramientas necesitaría cada uno?

## Para profundizar

- [Article: "How We Built Our Multi-Agent Research System", Anthropic Engineering](https://www.anthropic.com/engineering/multi-agent-research-system)
- [Recursos](../RESOURCES.md)

---

¿No termina de quedar claro? Vuelve a leer la fuente primaria de arriba, ya que esta lección la comprime y en la compresión es donde se escapa la comprensión. Consulta el [glosario](../GLOSSARY.md) por si algún término te resultó resbaladizo.

Si lo poco claro es la propia lección y no el material, eso es un defecto: [abre un issue](https://github.com/TokenCemetery/teach/issues).
