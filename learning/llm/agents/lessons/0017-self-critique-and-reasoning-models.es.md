---
title: "17. Autocrítica y lo que cambiaron los modelos de razonamiento"
description: "El bucle de reflexión como etapa explícita, sus costos y cómo el razonamiento interno extendido afecta cuándo usarlo"
type: lesson
---

# Lección 17. Autocrítica y lo que cambiaron los modelos de razonamiento

**Vínculo con la misión:** Para diagnosticar un agente que falla, necesitas reconocer cuándo añadir una etapa de reflexión (un bucle aparte que evalúa fallos pasados y lleva las lecciones hacia delante) y cuándo el propio razonamiento interno del modelo hace redundante ese bucle.
**Fuente principal:** [Paper: "Reflexion: Language Agents with Verbal Reinforcement Learning", Shinn et al., 2023](https://arxiv.org/abs/2303.11366)
**Requisitos previos:** [Lección 16](0016-plan-then-execute-and-decomposition.md)

## Calentamiento

1. ▢ En un agente de planificar y luego ejecutar, ¿qué pasa si un paso falla y el harness no admite la replanificación?

<details markdown="1"><summary>Comprobación</summary>

El harness no tiene forma de adaptarse. O bien sigue a ciegas con el plan original (que probablemente volverá a fallar), o se detiene. El agente no puede aprender del fallo ni pivotar hacia otro enfoque porque el plan quedó fijado por adelantado y no hay ningún mecanismo para actualizarlo.

</details>

2. ▢ ¿Cuál es la ventaja de la replanificación explícita frente a simplemente volver a ejecutar el agente desde el principio?

<details markdown="1"><summary>Comprobación</summary>

La replanificación permite al modelo ver el fallo exacto y razonar sobre él en contexto. Si simplemente vuelves a ejecutar el agente, podría producir el mismo plan otra vez. Con la replanificación, el harness añade el fallo a la transcripción y le pide al modelo que haga un plan nuevo, de modo que el modelo puede ver qué salió mal y ajustarse.

</details>

## Qué debes saber

### Reflexion: añadir un bucle de reflexión

El paper de Reflexion introduce una etapa explícita de reflexión en el bucle del agente. Después de que un intento falla (la respuesta del agente es incorrecta, una tarea no se completa, una prueba falla), el harness no reintenta de inmediato. En su lugar, genera una reflexión en lenguaje natural sobre lo que salió mal. Esta reflexión se almacena (a menudo en un archivo o en un búfer de memoria) y se incluye en el contexto del siguiente intento.

El bucle se ve así:

1. Ejecutar el agente en una tarea.
2. Comprobar si la tarea tuvo éxito (una prueba pasa, una persona evalúa la respuesta como correcta).
3. Si falló, generar una reflexión: "Intenté X, pero X falló porque Y".
4. Guardar la reflexión en una memoria persistente.
5. Ejecutar el agente otra vez, esta vez incluyendo la reflexión guardada en el contexto.
6. Volver al paso 2.

Esto es distinto de un simple reintento. Un simple reintento vuelve a ejecutar el agente con el mismo contexto. Reflexion vuelve a ejecutar el agente con la reflexión en el contexto, de modo que el segundo intento puede aprender del fallo del primero.

### Por qué la reflexión no es gratis

Reflexion cuesta llamadas extra al modelo. Si el primer intento falla, ahora necesitas una llamada para generar la reflexión, y luego otra para ejecutar el segundo intento. Para tareas con tasas de fallo bajas, esta sobrecarga no vale la pena. Para tareas en las que se necesitan muchos intentos, el costo acumulado es alto.

La reflexión también consume presupuesto de contexto. Cada reflexión ocupa tokens en la ventana de contexto. Si acumulas muchas reflexiones a lo largo de los intentos, con el tiempo tienes que podarlas o resumirlas. Es otra versión del problema de gestión del contexto de lecciones anteriores.

La reflexión tiene sentido solo si la propia reflexión está basada en información real: una prueba que falló, un mensaje de error, una evaluación humana. Si la tarea no tiene una señal de fallo clara, la reflexión no tiene nada concreto a lo que reaccionar y puede limitarse a racionalizar la respuesta errónea anterior.

### Modelos con razonamiento interno extendido

En los últimos años, algunos modelos de frontera han ganado la capacidad de hacer razonamiento interno extendido antes de producir una respuesta. Este razonamiento no es visible en la transcripción (ocurre dentro de un solo turno del modelo, antes de que se devuelva la salida) pero le permite al modelo autocorregirse, revisar su trabajo y detectar errores evidentes antes de que aparezcan en la salida.

Esto cambia, pero no elimina, el argumento a favor de los bucles de reflexión explícitos. Parte de lo que antes aportaba un bucle de reflexión (detectar un paso intermedio obviamente erróneo) ahora ocurre dentro del propio razonamiento del modelo, así que añadir un bucle de reflexión encima aporta menos beneficio marginal que antes.

Sin embargo, la reflexión explícita sigue teniendo una ventaja que el razonamiento interno no tiene: puede incorporar información que solo existe después de que se hizo una llamada a una herramienta. Si una llamada a herramienta devuelve "Permission denied" o una prueba falla, el razonamiento interno del modelo no pudo haber visto esa señal de fallo durante su fase original de razonamiento, porque la herramienta aún no se había ejecutado. Un bucle de reflexión explícito puede observar el resultado real de la herramienta e incorporarlo al siguiente intento.

Así que la pregunta no es "reflexión o razonamiento interno", sino "¿cuándo se gana su sitio el costo extra de la reflexión externa a pesar del razonamiento interno?"

### Cuándo la autocrítica explícita se gana su costo

Usa la reflexión externa cuando:

- La tarea tiene una señal de fallo clara y comprobable (un conjunto de pruebas pasa o falla, una API devuelve un error, una persona califica la respuesta como errónea o correcta).
- Es probable que un segundo o tercer intento, informado por el fallo, tenga éxito donde el primero falló.
- La tarea merece reintentarse: tiene un valor lo bastante alto como para justificar las llamadas extra al modelo.

No añadas reflexión cuando:

- La tarea no tiene una señal de fallo clara (por ejemplo, "escribe un resumen" sin ninguna prueba ni rúbrica para comprobar la corrección).
- El fallo no es culpa del modelo (por ejemplo, una API necesaria está caída, algo que el modelo no puede arreglar).
- El primer intento ya tiene muchas probabilidades de tener éxito y los fallos son raros.

### Diseñar las señales de reflexión

La reflexión solo es tan buena como la señal que recibe. Si le dices al harness "esta tarea falló porque lo dijo el usuario", la reflexión podría generar "Intenté escribir un resumen pero al usuario no le gustó". Eso es demasiado vago para que el siguiente intento actúe sobre ello. Una mejor señal de fallo sería "al resumen le faltan los requisitos que indicó el cliente" o "el resumen supera el límite de 100 palabras".

Al construir un agente que reflexiona, diseña con cuidado la comprobación del fallo. ¿Cómo se ve el éxito? ¿Qué evidencia concreta demuestra el fallo? Esa evidencia es a lo que reaccionará la reflexión.

## Práctica

1. ▢ Un agente escribe código para resolver un problema de LeetCode. El conjunto de pruebas ejecuta el código e informa "All tests pass" o imprime un caso de prueba concreto que falla. Tras un fallo, el harness genera una reflexión y vuelve a ejecutar el agente con la reflexión en el contexto. ¿Por qué encaja bien esto con Reflexion?

<details markdown="1"><summary>Comprobación</summary>

Hay una señal de fallo clara: el conjunto de pruebas. La reflexión puede decir "Test case [input] expected [output] but I produced [wrong_output]". Eso es concreto y accionable. El modelo puede leerlo en el siguiente intento y depurar específicamente el caso que falla. La generación de código además es iterativa por naturaleza; se esperan varios intentos y valen el costo.

</details>

2. ▢ A un agente se le pide escribir texto de producto para un sitio de comercio electrónico. El agente produce el texto y lo envía. No hay conjunto de pruebas, ni rúbrica, ni comprobación automática. Una persona de marketing lo lee y dice "Esto no está bien, inténtalo de nuevo". ¿Ayudaría Reflexion aquí?

<details markdown="1"><summary>Pista</summary>

¿Con qué comentarios tiene que trabajar el bucle de reflexión? ¿Son lo bastante concretos como para que el siguiente intento actúe sobre ellos?

</details>

<details markdown="1"><summary>Comprobación</summary>

Reflexion no ayudaría mucho. El comentario "Esto no está bien" es demasiado vago. La reflexión sería algo como "A la persona de marketing no le gustó mi texto". El siguiente intento del agente no tendría ningún cambio concreto que hacer. Un mejor enfoque sería obtener comentarios específicos de la persona (por ejemplo, "Hazlo más corto y añade una comparación de precios") e incluirlos en el siguiente prompt, en lugar de depender de un bucle de reflexión.

</details>

3. ▢ Un modelo con razonamiento interno extendido ahora puede autocorregirse durante su propia fase de razonamiento. ¿Cuál de las siguientes sigue siendo una ventaja de un bucle de reflexión externo explícito en este contexto?

    - a) La reflexión externa siempre es más rápida que el razonamiento interno.
    - b) La reflexión externa puede incorporar información (como un error de herramienta o el fallo de una prueba) que solo existe después del primer intento del modelo.
    - c) La reflexión externa es más barata en tokens de contexto que el razonamiento interno.
    - d) La reflexión externa funciona con todos los modelos, incluso los que no tienen capacidad de razonamiento interno.

<details markdown="1"><summary>Comprobación</summary>

**b)** El razonamiento interno ocurre antes de que corra ninguna herramienta, así que no puede observar el resultado real de una herramienta ni el fallo de una prueba. Un bucle de reflexión explícito puede incorporar esa información, así que aporta valor incluso con modelos que tienen razonamiento interno. a) es falsa, el razonamiento interno suele ser más rápido que ejecutar un bucle extra. c) es falsa, la reflexión externa consume tokens de contexto (el texto de la reflexión y el siguiente intento ocupan espacio). d) es cierta pero no es la idea clave; la pregunta es sobre lo que aporta la reflexión cuando hay razonamiento interno.

</details>

4. ▢ Estás construyendo un agente que procesa solicitudes de empleo. El harness tiene una señal clara: aprobada o rechazada por un responsable de contratación. Quieres usar Reflexion para mejorar las decisiones del agente a lo largo de varios intentos. ¿Qué debería capturar cada reflexión para ser útil en el siguiente intento?

<details markdown="1"><summary>Comprobación</summary>

La reflexión debería capturar las razones específicas del rechazo o de la aprobación, si están disponibles. Por ejemplo, "Application rejected because: missing required certification. Next attempt, check for required certifications before approving." O "Application approved because: strong experience in required skills and good communication in cover letter." La reflexión debe ser específica de la solicitud, no un consejo genérico. Esto le da al siguiente intento algo concreto sobre lo que actuar. Si el responsable de contratación da solo un sí o un no sin razones, la reflexión es menos accionable.

</details>

## Prácticas en el mundo real

- [ ] Toma una tarea que implique iteración y tenga una señal clara de éxito o fallo (por ejemplo, resolver un problema, pasar una prueba, cumplir una rúbrica). Implementa un bucle de agente que reflexiona: intento, comprobar el fallo, generar reflexión, reintentar con la reflexión en el contexto. Ejecútalo cinco veces y cuenta cuántos intentos necesita el agente con reflexión frente a sin ella. Registra la diferencia.
- [ ] Encuentra una tarea en tu trabajo que no tenga una señal de fallo clara (por ejemplo, escritura, diseño, trabajo creativo). Describe cómo añadirías una (por ejemplo, "comparar con una rúbrica", "pedir una revisión de un compañero", "comprobar criterios específicos"). ¿Haría útil a un agente que reflexiona añadir una señal de fallo, o la tarea se maneja mejor con un bucle humano?
- [ ] Mañana: Lee una trayectoria de Reflexion (de un paper, una entrada de blog o algo que hayas construido). Identifica el texto de la reflexión. ¿Habría sido útil la reflexión si el modelo hubiera tenido razonamiento interno? ¿Por qué sí o por qué no?

## Para profundizar

- [Paper: "Reflexion: Language Agents with Verbal Reinforcement Learning", Shinn et al., 2023](https://arxiv.org/abs/2303.11366)
- [Recursos](../RESOURCES.md)

---

¿No termina de quedar claro? Vuelve a leer la fuente primaria de arriba, ya que esta lección la comprime y en la compresión es donde se escapa la comprensión. Consulta el [glosario](../GLOSSARY.md) por si algún término te resultó resbaladizo.

Si lo poco claro es la propia lección y no el material, eso es un defecto: [abre un issue](https://github.com/TokenCemetery/teach/issues).
