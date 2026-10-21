---
title: "33. Amplificación de tokens y costo por tarea completada"
description: "Por qué los sistemas agénticos consumen muchos más tokens por tarea completada que un solo prompt, y cómo presupuestarlo"
type: lesson
---

# Lección 33. Amplificación de tokens y costo por tarea completada

**Vínculo con la misión:** Presupuestar el costo en tokens y la latencia de un bucle agéntico, y decir de qué parte del bucle viene la amplificación.
**Fuente principal:** [Article: "How We Built Our Multi-Agent Research System", Anthropic Engineering](https://www.anthropic.com/engineering/multi-agent-research-system)
**Requisitos previos:** [Lección 32](0032-least-privilege-and-the-confused-deputy.md), [Trayectoria](../GLOSSARY.md)

## Calentamiento

1. ▢ En la lección 10 aprendiste que la transcripción crece en cada turno que corre el bucle del agente. ¿Por qué esto crea un costo que se acumula a lo largo de una trayectoria?

<details markdown="1"><summary>Comprobación</summary>

La transcripción completa se envía al modelo en cada turno del bucle. Una trayectoria de 30 turnos significa que el contenido del primer turno se envía al modelo 30 veces, el del segundo turno 29 veces, y así sucesivamente. El costo en tokens de una trayectoria larga no es solo la suma de los turnos; es la suma de todas las transmisiones repetidas de los turnos antiguos.

</details>

2. ▢ De la lección 19, recuerda: cuando un orquestador lanza tres workers en paralelo, ¿cuántos bucles de agente corren en total en comparación con un solo agente que resuelve el mismo problema?

<details markdown="1"><summary>Comprobación</summary>

Corren tres bucles de agente separados, uno dentro de cada worker, más el propio bucle del orquestador. Así que el total es al menos tres ejecuciones completas de agentes más el costo del orquestador, mientras que un solo agente que resuelve el mismo problema es una ejecución. El costo en tokens se multiplica, no se divide, por el paralelismo.

</details>

## Qué debes saber

### Las cuatro fuentes de la amplificación de tokens

Un sistema agéntico consume muchos más tokens por tarea completada que un solo prompt bien informado. Esto ocurre por cuatro factores que se acumulan. Ya hemos nombrado tres de ellos en lecciones anteriores; esta lección los reúne y añade el cuarto.

### Fuente 1: el recrecimiento de la transcripción (de la lección 10)

Cada turno del bucle añade algo a la transcripción. En el siguiente turno, la transcripción completa se vuelve a enviar al modelo. Esto significa que una trayectoria de 50 turnos paga el costo en tokens del turno 1 cincuenta veces, el del turno 2 cuarenta y nueve veces, y así sucesivamente. El total es aproximadamente la mitad de la suma: 1 + 2 + 3 + ... + 50 = 1.275, así que cada turno se paga de media 25,5 veces. Un prompt simple que envías una vez cuesta X tokens. El mismo problema resuelto por un agente de 50 turnos cuesta no 50X (si cada turno fuera independiente), sino algo más cercano a 1.275X en transmisión bruta de tokens, aunque cada turno individual sea más barato que X porque el modelo está enfocado de forma estrecha.

El artículo "Building Effective Agents" de Anthropic señala que este recrecimiento es el mayor multiplicador de costo en los agentes de larga duración, y es la razón por la que la lección 11 (compactación y recuperación) existe como defensa frente a él.

### Fuente 2: la duplicación multiagente (de la lección 19)

Si descompones un problema en subtareas y ejecutas tres workers en paralelo (fan-out de la lección 18), pagas el costo completo de recrecimiento de la transcripción no una vez, sino tres. Cada worker tiene su propia trayectoria de 50 turnos, así que cada uno paga 1.275X. El orquestador también corre su propio bucle. El costo de coordinación multiplica el costo total en tokens. Si tu agente único habría costado 50.000 tokens, tres workers con un costo cada uno ligeramente menor podrían sumar 130.000 tokens o más.

### Fuente 3: la reflexión y los reintentos (de la lección 17)

Si un primer intento de una tarea falla y el harness genera una reflexión y luego vuelve a ejecutar el agente, ahora tienes dos trayectorias completas en lugar de una. Una tarea que necesita tres intentos (un fallo, una reflexión, un éxito) cuesta aproximadamente tres veces lo que costaría un único intento exitoso, porque cada intento es una ejecución completa de un agente con su propio recrecimiento de la transcripción. La lección 17 enseña que la reflexión solo vale este costo cuando la señal de fallo es clara y es probable que un segundo intento tenga éxito.

### Fuente 4: las definiciones de herramientas reenviadas en cada turno (nueva en esta lección)

El system prompt y las definiciones de herramientas forman parte del contexto que se envía al modelo en cada turno del bucle. Las definiciones de herramientas suelen ser grandes: cada herramienta tiene un nombre, una descripción legible por personas (del trabajo de nombrado de la lección 8), tipos de parámetros, restricciones y ejemplos. Si tienes diez herramientas con 200 tokens de descripción cada una, son 2.000 tokens de definiciones de herramientas. En una trayectoria de 50 turnos, son 2.000 * 50 = 100.000 tokens gastados en reenviar las mismas definiciones de herramientas, aunque nunca cambiaron a mitad de la ejecución.

Este costo es distinto del recrecimiento de la transcripción (fuente 1) porque las definiciones de herramientas no cambian; son un prefijo estable y repetido. Este es exactamente el problema que aborda la lección 34 (prompt caching).

### La unidad correcta para presupuestar: el costo por tarea completada

La mayoría de las discusiones sobre costos se centran en el "costo por llamada a la API" o el "costo por invocación del modelo". Pero la unidad correcta para un sistema agéntico es el "costo por tarea completada", que significa la suma completa de todos los intentos, todos los reintentos, todos los workers, todos los turnos, hasta que la tarea está hecha.

Una tarea que un solo prompt podría resolver con 5.000 tokens puede costar 50.000 o más tokens en un sistema agéntico si:

- El problema tarda 20 turnos en resolverse (multiplicador de recrecimiento: ~200 veces sobre el costo de un solo turno)
- El primer intento falla y un reintento basado en reflexión tiene éxito (multiplicar por 2)
- La tarea se divide en tres workers en paralelo (multiplicar por 3)
- Las definiciones de herramientas son grandes y se reenvían en cada turno (añadir 10.000 tokens de desperdicio)

La cuenta es aproximada, pero el principio es real: 5.000 tokens base pueden convertirse en 50.000 a 150.000 tokens en la práctica, porque no estás pagando una llamada; estás pagando la finalización de una tarea, que implica muchas llamadas, muchos viajes de ida y vuelta y muchos contextos repetidos.

### Por qué el "costo por tarea completada" cambia tus decisiones de diseño

Cuando piensas en términos de costo por llamada a la API, un agente de larga duración parece caro por la pura cantidad de llamadas. Cuando piensas en términos de costo por tarea completada, la pregunta cambia: ¿resuelve un sistema multiagente el problema más rápido en tiempo real o con más fiabilidad, de una forma que justifique el multiplicador de tokens? ¿Reduce la reflexión el número de tareas fallidas, de una forma que justifique el costo de los reintentos? ¿Simplifica la descomposición el problema lo bastante como para que cada worker use menos tokens por tarea que el agente único?

Estas son las preguntas reales sobre los intercambios. Presupuestar por costo por tarea hace visible el intercambio.

### Ejemplo ilustrativo: depurar un fallo de código

Supón que tu tarea es depurar una prueba que falla. Una persona bien informada podría escribir un prompt: "Aquí está la prueba, aquí está la salida del error. Encuentra el error". Ese prompt y la respuesta podrían costar 10.000 tokens en total.

Ahora supón que construyes un bucle de agente en su lugar:

- El agente lee la prueba (1.000 tokens), lee el código (2.000 tokens), razona sobre el error (500 tokens) = 3.500 tokens en el turno 1. Reenviar esos 3.500 tokens más las definiciones de herramientas (2.000 tokens) en el turno 2 = 5.500 tokens. Tras 10 turnos depurando, has gastado aproximadamente 3.500 \* 10 + (definiciones de herramientas \* 10) = 55.000 tokens, porque cada turno reenvía la prueba, el código y las definiciones de herramientas.
- El primer intento del agente adivina la causa raíz equivocada. El harness genera una reflexión y vuelve a ejecutar el agente. Ahora tienes dos ejecuciones completas de 10 turnos, así que aproximadamente 110.000 tokens, no 55.000.
- El segundo intento tiene éxito.

Costo por tarea completada: 110.000 tokens. Costo por llamada a la API exitosa: 5.500 tokens (solo la última llamada exitosa). Estos números cuentan historias distintas. Presupuestar por tarea completada es más honesto.

La solución no es evitar los agentes; la solución es usar el prompt caching de la lección 34 para evitar reenviar las definiciones de herramientas, diseñar la planificación de la lección 16 para reducir el número de turnos, y usar la reflexión de la lección 17 solo cuando las señales de fallo sean claras.

## Práctica

1. ▢ Un prompt de un solo turno a un modelo cuesta 5.000 tokens y resuelve un problema a la perfección. Un bucle de agente sobre el mismo problema tarda 25 turnos, y el costo de recrecimiento de la transcripción significa que cada token de los primeros turnos se paga aproximadamente 20 veces de media. ¿Aproximadamente cuántos tokens cuesta en total el bucle del agente?

<details markdown="1"><summary>Comprobación</summary>

Aproximadamente 5.000 * 20 = 100.000 tokens. El multiplicador de recrecimiento es el factor más grande. (Esta es una estimación ilustrativa; el número exacto depende de cómo se distribuyan los tokens entre los turnos, pero el orden de magnitud es correcto.)

</details>

2. ▢ Estás construyendo un agente que resume papers de investigación. Las definiciones de herramientas del agente son 3.000 tokens en total. En una sola ejecución, el agente examina 10 papers y produce 10 resúmenes, con 40 turnos en total. Las definiciones de herramientas nunca cambian durante la ejecución. ¿Cuántos tokens se gastan en reenviar las definiciones de herramientas, y por qué este desperdicio se puede abordar en la lección 34?

<details markdown="1"><summary>Pista</summary>

Cuenta cuántas veces se envían al modelo las definiciones de herramientas. Luego piensa qué parte del contexto es estable y nunca cambia a mitad de la ejecución.

</details>

<details markdown="1"><summary>Comprobación</summary>

Las definiciones de herramientas se envían 40 veces (una por turno), así que 3.000 * 40 = 120.000 tokens gastados en reenviar exactamente las mismas definiciones. Esto es desperdicio porque las definiciones nunca cambian; son un prefijo estable. La lección 34 enseña el prompt caching, que almacena en caché justo este tipo de prefijo estable y solo lo cobra una vez, no 40.

</details>

3. ▢ Una tarea requiere tres intentos. El primer intento falla, se genera una reflexión, el segundo intento falla, se genera otra reflexión y el tercer intento tiene éxito. Cada intento es una ejecución completa de agente de 15 turnos. El orquestador que coordina los tres intentos cuesta 5 turnos. ¿Aproximadamente cuántos turnos en total tiene la trayectoria?

    - a) 15 turnos (solo cuenta el intento exitoso)
    - b) 35 turnos (15 + 15 + 5)
    - c) 50 turnos (15 + 15 + 15 + 5)
    - d) 150 turnos (los tres intentos por la sobrecarga del orquestador)

<details markdown="1"><summary>Comprobación</summary>

**c)** Los tres intentos corren hasta el final, así que 15 + 15 + 15 = 45 turnos, más 5 turnos de orquestación = 50 turnos. La opción a es incorrecta porque los fallos siguen consumiendo turnos completos. La opción b pasa por alto el segundo intento fallido. La opción d cuenta mal al multiplicar en lugar de sumar. La trayectoria incluye cada turno de cada intento, no solo el exitoso.

</details>

4. ▢ Estás decidiendo si usar un solo agente o un fan-out de tres workers para una tarea de investigación. El agente único tardaría 60 turnos y costaría aproximadamente 100.000 tokens. Cada worker tardaría 25 turnos y costaría aproximadamente 35.000 tokens, y además el orquestador tarda 10 turnos y cuesta 3.000 tokens. ¿Cuál es el costo total en tokens del sistema multiagente, y es más barato que el agente único?

<details markdown="1"><summary>Comprobación</summary>

Total: (35.000 * 3) + 3.000 = 108.000 tokens. El sistema multiagente es en realidad algo más caro en tokens (108.000 frente a 100.000) aunque cada worker sea más eficiente. Este es el costo de coordinación de la lección 19. El sistema multiagente gana en tiempo real (los tres workers corren en paralelo, así que el worker más lento determina el tiempo, no la suma), no en tokens. Esto muestra por qué es importante presupuestar por costo por tarea: si necesitas velocidad, gana lo multiagente; si necesitas ahorrar tokens, gana el agente único.

</details>

## Prácticas en el mundo real

- [ ] Toma una tarea que hayas hecho con un agente (o una trayectoria que hayas visto). Recorre una iteración del bucle de ese agente y cuenta los tokens: tamaño de la transcripción, tamaño de las definiciones de herramientas, tamaño de la salida del modelo. Multiplica por el número de turnos. Ahora estima cuánto habría costado un solo prompt bien informado al modelo, y compara los dos números. Registra el multiplicador.
- [ ] Diseña una pequeña tarea de agente (algo que podrías ejecutar tú mismo). Estima el costo por tarea completada adivinando: número de turnos necesarios, número de reintentos, cualquier worker de fan-out. Suma el presupuesto completo con la fórmula (factor_de_recrecimiento_de_la_transcripción) \* (número_de_intentos) \* (número_de_workers) \* (tokens_por_turno).
- [ ] Mañana: Encuentra o genera la trayectoria de la ejecución de un agente (al menos 10 turnos). Calcula el costo por tarea en tokens sumando todos los costos en tokens de todos los turnos y todos los intentos. Luego halla el costo por llamada a la API exitosa (solo el último turno exitoso). Anota cuánto mayor es el costo por tarea que el costo por llamada exitosa, y explica por qué importa la diferencia para el presupuesto.

## Para profundizar

- [Article: "How We Built Our Multi-Agent Research System", Anthropic Engineering](https://www.anthropic.com/engineering/multi-agent-research-system)
- [Recursos](../RESOURCES.md)

---

¿No termina de quedar claro? Vuelve a leer la fuente primaria de arriba, ya que esta lección la comprime y en la compresión es donde se escapa la comprensión. Consulta el [glosario](../GLOSSARY.md) por si algún término te resultó resbaladizo.

Si lo poco claro es la propia lección y no el material, eso es un defecto: [abre un issue](https://github.com/TokenCemetery/teach/issues).
