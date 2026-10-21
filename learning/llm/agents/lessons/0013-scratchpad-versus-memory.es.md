---
title: "13. Scratchpad frente a memoria"
description: "La diferencia entre las notas que un agente guarda durante una ejecución y los hechos que necesita a lo largo de varias ejecuciones"
type: lesson
---

# Lección 13. Scratchpad frente a memoria

**Vínculo con la misión:** Diagnosticar un agente que falla a partir de su trayectoria en lugar de añadir una instrucción más a su prompt, entendiendo qué información persiste entre ejecuciones y cuál se desvanece cuando termina una ejecución.
**Fuente principal:** [Article: "Effective Context Engineering for AI Agents", Anthropic Engineering](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents)
**Requisitos previos:** [Lección 12](0012-sub-agents-as-context-isolation.md), [Trayectoria](../GLOSSARY.md)

## Calentamiento

1. ▢ ¿Qué registra una trayectoria?

<details markdown="1"><summary>Comprobación</summary>

El registro completo y ordenado de una ejecución de agente: cada mensaje enviado al modelo, cada llamada a herramienta que hizo el modelo y cada resultado que el harness añadió de vuelta.

</details>

2. ▢ Cuando lanzas un subagente para manejar una parte acotada del trabajo, ¿ve el subagente la transcripción completa del padre?

<details markdown="1"><summary>Comprobación</summary>

No. El subagente recibe su propia transcripción nueva con un historial vacío. Puede recibir un resumen o un contexto específico que el agente padre le pasa como prompt inicial, pero no hereda la trayectoria completa del padre.

</details>

## Qué debes saber

Un **scratchpad** es en realidad solo parte de la transcripción, o una nota que el agente escribe y vuelve a leer dentro de una sola ejecución. Durante una tarea larga, el agente podría usar un scratchpad para llevar un total acumulado, un plan de varios pasos o hallazgos intermedios, para que el modelo no tenga que volver a derivarlos en cada turno. El scratchpad es efímero: cuando el harness detiene el bucle y la ejecución termina, el scratchpad vive en la trayectoria pero en ningún otro sitio. Si inicias una nueva ejecución del agente una hora después para continuar el trabajo, el scratchpad ya no está.

Aquí es donde se instala una confusión común. Un agente mantuvo un scratchpad durante una ejecución y "recordó" algo. Ese mismo agente, reiniciado desde cero, no lo recordará. El modelo podría usar el mismo nombre para la herramienta o el archivo del scratchpad, pero el contenido se perdió porque la ejecución se perdió.

La **memoria entre ejecuciones** es fundamentalmente distinta. Una ejecución nueva empieza con una transcripción vacía, así que todo lo que el modelo necesite saber de una ejecución anterior tiene que vivir en algún lugar fuera de cualquier trayectoria individual y cargarse de vuelta de forma deliberada cuando empieza la siguiente ejecución. El harness lee de un almacenamiento durable, un archivo, una base de datos o un sistema de recuperación, antes de que empiece el bucle, y pone los hechos relevantes en el prompt inicial o en el contexto para que el modelo pueda actuar sobre ellos.

Aquí tienes un ejemplo concreto: Un agente está haciendo la revisión de código de un pull request grande. Durante la ejecución de una hora, mantiene un scratchpad con la lista de cada archivo que ya ha revisado, de modo que cuando el modelo considera un archivo nuevo, puede echar un vistazo al scratchpad y evitar volver a analizar trabajo que ya hizo. El scratchpad es parte de la transcripción. Cuando termina la ejecución, la revisión está hecha y el scratchpad se archiva como parte de la trayectoria.

Ahora imagina un escenario distinto: Un asistente de programación ayuda a un solo usuario a escribir código a lo largo de muchas sesiones separadas durante semanas. El usuario tiene una fuerte preferencia por cierto estilo de código, convención de nombres y biblioteca. Si el asistente se reinicia en cada sesión, empieza sin saber nada de esas preferencias. El asistente necesita memoria entre ejecuciones: un archivo o una nota que el harness lee al comienzo de cada sesión y que dice "el usuario prefiere X, usa Y, evita Z". Ese hecho no está en ninguna trayectoria individual; se guarda de forma durable y se carga al inicio de la ejecución.

La idea clave de [Effective Context Engineering for AI Agents](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents) es que son dos mecanismos separados. Un scratchpad es una herramienta o un artefacto que el agente manipula durante una ejecución. La memoria entre ejecuciones es una capa de datos fuera del bucle del agente, gestionada por el harness.

## Práctica

1. ▢ Un agente está resolviendo un problema de matemáticas de varios pasos. Durante la ejecución, escribe sus notas de trabajo en un archivo de scratchpad. Al final, añade la respuesta final a un archivo de resultados. Días después, inicias el mismo agente otra vez con un problema distinto. ¿Qué seguirá estando ahí?

    - a) Las notas del scratchpad.
    - b) El archivo de resultados.
    - c) Ambos, porque los dos son archivos.
    - d) Ninguno, porque los archivos se borran en cada ejecución.

<details markdown="1"><summary>Comprobación</summary>

**b)** El archivo de resultados seguirá estando ahí porque es almacenamiento durable fuera de la ejecución. Las notas del scratchpad, aunque se escribieron en un archivo, solo son relevantes para la ejecución antigua y no se cargan automáticamente en la nueva transcripción. Si el agente necesita esas notas antiguas en la nueva ejecución, el harness debe leerlas de forma deliberada e incluirlas en el prompt inicial.

</details>

2. ▢ Estás diseñando un agente que debe recordar los nombres de los archivos que ya ha procesado. ¿Usarías un scratchpad o memoria entre ejecuciones?

<details markdown="1"><summary>Pista</summary>

Piensa si la información se usa dentro de una sola ejecución o a lo largo de varias ejecuciones separadas.

</details>

<details markdown="1"><summary>Comprobación</summary>

Si todos los archivos se procesan en una sola ejecución larga, basta un scratchpad. El agente lo consulta cada vez y evita reprocesar. Si el trabajo se reparte en varias ejecuciones del agente, quizá reiniciado cada día o una ejecución por petición del usuario, entonces necesitas memoria entre ejecuciones para que una ejecución nueva pueda ver lo que se hizo antes.

</details>

3. ▢ ¿Cuál es la razón fundamental por la que un agente reiniciado con un harness nuevo no puede ver las notas que escribió en un scratchpad en la ejecución anterior?

<details markdown="1"><summary>Comprobación</summary>

Porque el scratchpad es parte de la transcripción, y una ejecución nueva empieza con una transcripción vacía. La trayectoria antigua está archivada pero no se carga en la nueva ejecución. Para hacer visible el contenido del scratchpad en una ejecución nueva, el harness tendría que leerlo del almacenamiento e insertarlo en el prompt inicial, lo que lo convierte de scratchpad en memoria deliberada entre ejecuciones.

</details>

4. ▢ Estás construyendo un agente que ayuda a un usuario a gestionar una lista personal de tareas. El agente añade tareas, las completa y filtra por etiqueta. ¿La lista de tareas debería ser un scratchpad, local a una ejecución, o memoria entre ejecuciones, persistida entre ejecuciones? ¿Por qué?

<details markdown="1"><summary>Comprobación</summary>

Memoria entre ejecuciones. Una lista de tareas necesita persistir más allá de una sesión. Si el usuario inicia el agente mañana y pide "muéstrame mis tareas", el agente debe seguir viendo la lista de hoy. Un scratchpad se desvanecería cuando termina la ejecución, y los datos del usuario se perderían.

</details>

## Prácticas en el mundo real

- [ ] Dedica dos minutos a recorrer el código de tu propio agente. Encuentra dónde el harness crea una transcripción nueva, vacía o solo con un prompt inicial. Anota lo que ves.
- [ ] Busca cualquier "memoria" o "estado" que tu agente guarde actualmente. ¿Lo carga el harness antes de que empiece el bucle, o solo se referencia durante la ejecución? Si es solo durante la ejecución, es un scratchpad. Si se carga al inicio, es memoria entre ejecuciones.
- [ ] Mañana: Encuentra o escribe un uso de scratchpad, donde un agente escribe una nota, la vuelve a leer y luego termina la ejecución. Por separado, encuentra o imagina un uso entre ejecuciones, donde un agente necesita un hecho de la ejecución de la semana pasada para responder la pregunta de hoy.

## Para profundizar

- [Article: "Effective Context Engineering for AI Agents", Anthropic Engineering](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents)
- [Recursos](../RESOURCES.md)

---

¿No termina de quedar claro? Vuelve a leer la fuente primaria de arriba, ya que esta lección la comprime y en la compresión es donde se escapa la comprensión. Consulta el [glosario](../GLOSSARY.md) por si algún término te resultó resbaladizo.

Si lo poco claro es la propia lección y no el material, eso es un defecto: [abre un issue](https://github.com/TokenCemetery/teach/issues).
