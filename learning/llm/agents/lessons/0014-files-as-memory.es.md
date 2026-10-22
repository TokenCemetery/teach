---
title: "14. Archivos como memoria"
description: "Usar archivos durables como la forma más simple de memoria entre ejecuciones para agentes"
type: lesson
---

# Lección 14. Archivos como memoria

**Vínculo con la misión:** Diagnosticar un agente que falla a partir de su trayectoria en lugar de añadir una instrucción más a su prompt, construyendo sistemas donde la memoria del agente sea inspeccionable y el harness pueda curar lo que persiste.
**Fuente principal:** [Article: "Effective Context Engineering for AI Agents", Anthropic Engineering](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents)
**Requisitos previos:** [Lección 13](0013-scratchpad-versus-memory.md)

## Calentamiento

1. ▢ Inicias un agente con una transcripción nueva por segunda vez. ¿Qué te dice la transcripción vacía?

<details markdown="1"><summary>Comprobación</summary>

Que el agente está empezando una ejecución nueva sin memoria de la ejecución anterior, a menos que el harness haya cargado de forma deliberada hechos de vuelta antes de que empezara el bucle.

</details>

2. ▢ Un agente escribió notas en un archivo durante su última ejecución. Si quieres que esas notas influyan en el comportamiento del agente en la nueva ejecución, ¿qué debe hacer el harness?

<details markdown="1"><summary>Comprobación</summary>

El harness debe leer el archivo, o las partes relevantes de él, e incluir el contenido en el contexto inicial o en el prompt de la nueva ejecución, para que el modelo pueda verlo y actuar sobre él.

</details>

## Qué debes saber

Escribir hechos en un archivo plano, o en un almacén durable similar, que el harness vuelve a leer en una ejecución posterior es la forma más simple de memoria entre ejecuciones que funciona. El patrón es directo: dale al agente una herramienta para escribir una nota, un archivo markdown, un registro JSON o un pequeño log estructurado, y al comienzo de una ejecución posterior, el harness lee las partes relevantes de ese archivo de vuelta a la nueva transcripción antes de que empiece el bucle.

Esto es deliberadamente simple e inspeccionable en comparación con, por ejemplo, una base de datos vectorial. Una persona puede abrir el archivo y leer exactamente lo que el agente "recuerda". Puedes editarlo a mano si hace falta. Puedes ver entradas obsoletas o erróneas y corregirlas sin reentrenar nada.

Sin embargo, el riesgo es real. Un agente que sigue añadiendo a un archivo de memoria sin podarlo ni actualizarlo nunca acumula con el tiempo notas obsoletas o contradictorias. Una nota que era cierta el mes pasado puede ser falsa hoy. Dos hechos distintos pueden contradecirse. Este es el mismo problema de degradación del contexto que las lecciones 10 y 11 abordaron para una transcripción que crece dentro de una sola ejecución. La memoria necesita la misma curación activa: revisión periódica, archivo de las entradas antiguas, consolidación de duplicados, eliminación de los hechos que ya no aplican.

Una aclaración importante: la recuperación bajo demanda, de la lección 11, que trae detalle de un corpus de documentos o de trabajo previo mediante búsqueda, no es lo mismo que la memoria, aunque ambas implican "traer texto al contexto". La recuperación responde a la pregunta "¿qué es relevante para esta consulta concreta ahora mismo?" buscando en un corpus grande. La memoria es un conjunto pequeño y deliberadamente curado de hechos que el agente, o quien lo diseñó, decidió que vale la pena llevar hacia delante sin importar la consulta actual. Un asistente de programación podría recuperar ejemplos del trabajo pasado del usuario para ilustrar un estilo, pero también necesita una memoria que diga "el usuario prefiere async/await a los callbacks" como un hecho permanente, no como el resultado de una consulta. El corpus de recuperación sirve para responder preguntas específicas; el archivo de memoria sirve para el contexto permanente.

La salvedad honesta de [Effective Context Engineering for AI Agents](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents) es esta: la memoria de agentes entre ejecuciones es un área más nueva y menos asentada. Los sistemas de producción para la memoria entre ejecuciones siguen evolucionando. Esta lección cubre el patrón basado en archivos, que es simple e inspeccionable por una persona, pero no necesariamente el enfoque definitivo que usará tu sistema de producción dentro de unos años.

## Práctica

1. ▢ Un agente está ayudando a un usuario a aprender a cocinar. El agente anota que al usuario no le gusta el cilantro y sugiere recetas sin él. Cuando reinicias el agente al día siguiente para una nueva sesión de cocina, ¿debería el harness cargar de vuelta la nota del cilantro desde el archivo de memoria?

<details markdown="1"><summary>Comprobación</summary>

Sí. La preferencia es un hecho permanente sobre el usuario que aplica entre sesiones. El harness debería leer el archivo de memoria al inicio e incluir "user dislikes cilantro" en el contexto inicial para que el modelo pueda usarlo al generar recetas nuevas.

</details>

2. ▢ Durante una ejecución, un agente escribe en un scratchpad "files checked so far: api.py, utils.py, config.py" para evitar reanalizarlos. La ejecución termina. ¿Debería guardarse esta entrada del scratchpad en el archivo de memoria entre ejecuciones?

<details markdown="1"><summary>Pista</summary>

¿Esa información en particular, la lista de archivos revisados en esta ejecución concreta, necesita llevarse hacia delante a ejecuciones futuras, o fue solo contabilidad útil dentro de una tarea?

</details>

<details markdown="1"><summary>Comprobación</summary>

Probablemente no, a menos que la tarea abarque varias ejecuciones del agente. Si cada revisión de código es una tarea nueva e independiente, la lista de archivos revisados en la ejecución A no es relevante para la ejecución B. Guardar cada entrada del scratchpad llenaría de desorden el archivo de memoria con detalles efímeros. Una buena heurística: guarda hechos en la memoria solo si una ejecución futura los va a necesitar.

</details>

3. ▢ Notas que el archivo de memoria del agente ahora contiene consejos contradictorios: "user prefers tabs" y "user prefers spaces", escritos con semanas de diferencia. ¿Qué deberías hacer?

    - a) Borrar por completo el archivo de memoria para que el agente empiece de cero.
    - b) Revisar y editar el archivo a mano para corregir la contradicción.
    - c) Añadir al agente una herramienta nueva para que resuelva los conflictos automáticamente.
    - d) Ignorarlo, ya que el modelo averiguará cuál es el vigente.

<details markdown="1"><summary>Comprobación</summary>

**b)** Revisar y editar el archivo a mano. La curación de la memoria es responsabilidad humana. Necesitas entender qué entrada está obsoleta, corregirla o eliminarla, y mantener el archivo limpio y con autoridad. Borrar todo el archivo pierde otros hechos valiosos. Automatizar la resolución de conflictos sin criterio humano corre el riesgo de codificar la preferencia equivocada. El modelo no debería tener que adivinar ni razonar sobre las contradicciones de su propia memoria.

</details>

4. ▢ ¿En qué se diferencia un sistema de memoria basado en archivos de un sistema de recuperación que busca en un corpus del trabajo pasado del agente?

<details markdown="1"><summary>Comprobación</summary>

Un sistema de recuperación responde "¿qué de mi trabajo pasado es relevante para esta consulta?" y extrae material según una coincidencia de palabras clave o semántica. Un sistema de memoria guarda un conjunto pequeño de hechos permanentes que el harness carga sin importar la consulta. La memoria es curada y durable; la recuperación está guiada por la consulta. Podrías recuperar ejemplos de código pasados cuando el usuario pide "muéstrame cómo resolví esto antes", pero recuerdas "el usuario prefiere async/await" como una preferencia permanente todo el tiempo.

</details>

## Prácticas en el mundo real

- [ ] Si tienes un agente que corre más de una vez, comprueba si el harness carga algún hecho guardado antes de la primera llamada al modelo. Si no, añade una sentencia de impresión o un log para ver qué ocurre en el momento de inicio de la ejecución.
- [ ] Diseña un formato simple de archivo de memoria para una tarea que conozcas bien. ¿Qué hechos escribirías? ¿Cómo sabrías cuándo actualizar o eliminar una entrada?
- [ ] Mañana: Construye un agente de una sola ejecución que escriba un hecho en un archivo de memoria, en cualquier formato: JSON, markdown o texto plano. Luego construye una segunda ejecución del mismo agente que lea ese archivo y lo use. Sin base de datos vectorial, sin búsqueda, solo almacenamiento durable y carga gestionada por el harness.

## Para profundizar

- [Article: "Effective Context Engineering for AI Agents", Anthropic Engineering](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents)
- [Recursos](../RESOURCES.md)

---

¿No termina de quedar claro? Vuelve a leer la fuente primaria de arriba, ya que esta lección la comprime y en la compresión es donde se escapa la comprensión. Consulta el [glosario](../GLOSSARY.md) por si algún término te resultó resbaladizo.

Si lo poco claro es la propia lección y no el material, eso es un defecto: [abre un issue](https://github.com/TokenCemetery/teach/issues).
