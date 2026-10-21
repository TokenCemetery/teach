---
title: "10. La ventana de contexto como presupuesto"
description: "La ventana de contexto es un recurso finito que el harness cura activamente con el tiempo, no un registro inerte"
type: lesson
---

# Lección 10. La ventana de contexto como presupuesto

**Vínculo con la misión:** Presupuestar el costo en tokens y la latencia de un bucle agéntico, y decir de qué parte del bucle viene la amplificación.
**Fuente principal:** [Article: "Effective Context Engineering for AI Agents", Anthropic Engineering](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents)
**Requisitos previos:** [Lección 9](0009-return-shapes-and-tool-set-bloat.md), [Trayectoria](../GLOSSARY.md)

## Calentamiento

1. ▢ En el bucle del agente de la lección 6, ¿en qué momento decide el harness qué llamada a herramienta ejecutar?

<details markdown="1"><summary>Comprobación</summary>

El modelo emite un bloque de llamada a herramienta (nombre, parámetros), y el harness lo analiza y ejecuta la herramienta. El modelo decide qué herramienta al procesar la transcripción que recibe.

</details>

2. ▢ ¿Qué le pasa a la transcripción cada vez que termina una herramienta?

<details markdown="1"><summary>Comprobación</summary>

El resultado (o el error) se añade a la transcripción, y la nueva transcripción se envía de vuelta al modelo en la siguiente iteración del bucle.

</details>

## Qué debes saber

### La transcripción crece en cada turno, y se encarece rápido

Cada iteración del bucle del agente añade algo a la transcripción. Después de que un agente corre durante 10, 20 o 100 turnos, la transcripción contiene cada mensaje, cada llamada a herramienta y cada resultado de toda la ejecución. En la siguiente iteración del bucle, esa transcripción entera vuelve al modelo. En la iteración que sigue, vuelve otra vez, más larga por un turno más.

Esto significa que dos costos crecen con la longitud de la trayectoria incluso cuando no está pasando nada nuevo:

- **Costo en tokens**: Cada mensaje al modelo vuelve a enviar todos los turnos antiguos. Una trayectoria de cinco turnos cuesta 5 veces menos tokens por llamada que una trayectoria de 100 turnos. En un agente de larga duración, esto se convierte en el costo dominante.
- **Latencia**: Un contexto más largo significa más tokens que procesar, lo que es más lento. El agente espera más tiempo cada respuesta.

### Degradación del contexto (context rot): la atención del modelo se deteriora a medida que se acumula basura

A medida que se acumula más contenido de poca relevancia en el contexto, la atención del modelo se vuelve más ruidosa. La capacidad del modelo de distinguir lo que todavía importa (el objetivo, las restricciones recientes, los resultados sobre los que aún no ha actuado) se deteriora cuando queda enterrada bajo una gran pila de callejones sin salida antiguos y líneas de razonamiento abandonadas. A esto a veces se le llama "context rot". Un contexto inflado no solo es caro: hace que el modelo sea peor en la tarea.

### El truncamiento ingenuo es riesgoso

El instinto más simple es descartar los turnos más antiguos cuando el contexto llega a un límite de tamaño. Pero el truncamiento ingenuo corre el riesgo de perder en silencio información crítica. Si el límite del truncamiento cae en medio de:

- Una instrucción de varios pasos que el modelo todavía necesita seguir
- Un resultado sobre el que el modelo aún no ha actuado
- Un enunciado de restricción o de objetivo
- Parte de un system prompt o de un ejemplo

entonces el agente se rompe en silencio de maneras que el harness no tiene forma de detectar. El modelo no sabrá que se eliminó una instrucción clave; simplemente trabajará con una comprensión incompleta y fallará de formas inesperadas.

### La curación activa es una decisión de diseño deliberada

Como el truncamiento ingenuo es peligroso y el costo crece con la longitud de la trayectoria, el harness no puede tratar la transcripción como un registro inerte que simplemente crece. "Qué se queda en el contexto y qué se va" tiene que ser una decisión de diseño deliberada, integrada en el harness. La trayectoria sigue existiendo, pero el harness decide qué parte de ella ve el modelo en cada llamada.

Hay dos estrategias principales para esto (se cubren en la siguiente lección): la compactación y la recuperación bajo demanda.

## Práctica

1. ▢ Un agente hace 50 llamadas a herramientas durante una larga tarea de investigación. En la llamada 51, al modelo se le envía una transcripción de 20.000 tokens. En la llamada 52, ¿cuántos tokens recibe el modelo en la transcripción (aproximadamente)?

    - a) 20.000 tokens
    - b) 20.000 más los tokens del nuevo resultado de la llamada 51
    - c) 40.000 tokens
    - d) Depende del tamaño del resultado de la llamada 51

<details markdown="1"><summary>Comprobación</summary>

**b)** El modelo recibe la transcripción original de 20.000 tokens más el nuevo resultado añadido. Si el resultado de la llamada 51 fue de 500 tokens, el modelo recibe aproximadamente 20.500 tokens. El costo en tokens crece con cada turno, y en ejecuciones muy largas esto se convierte en un gasto serio. La opción c es incorrecta porque el modelo no recibe dos veces el resultado de la llamada 51; la opción a ignora el nuevo añadido; la opción d es correcta en espíritu (el tamaño del resultado importa) pero b es la respuesta más precisa.

</details>

2. ▢ Estás diseñando un agente para una tarea de revisión de código. El agente lee archivos, los compara, toma notas y produce un resumen. ¿Por qué es riesgoso simplemente descartar los resultados de herramientas más antiguos cuando la transcripción llega a un límite de 50.000 tokens?

<details markdown="1"><summary>Pista</summary>

¿Y si el límite del truncamiento cae entre la lectura de un archivo antiguo y una comparación que el modelo aún no ha terminado? ¿Y si una restricción sobre el alcance de los archivos está en la parte que descartaste?

</details>

<details markdown="1"><summary>Comprobación</summary>

El truncamiento ingenuo podría descartar un resultado de herramienta (como el contenido de un archivo) al que el modelo todavía necesita referirse, o una restricción (como "revisa solo los archivos de src/core/") que el modelo necesita recordar. El modelo no sabrá que falta la información; trabajará en silencio desde un cuadro incompleto y producirá conclusiones erróneas. El harness debe ser más inteligente que simplemente cortar en el límite de tokens.

</details>

3. ▢ ¿Cuál de las siguientes afirmaciones es cierta sobre la degradación del contexto?

    - a) La degradación del contexto solo ocurre si la transcripción contiene errores
    - b) La degradación del contexto se previene dando buen formato a los resultados de herramientas
    - c) Una transcripción grande con muchos turnos antiguos irrelevantes hace al modelo menos preciso, incluso si no se trunca ninguna información crítica
    - d) La degradación del contexto no es un problema real en los modelos modernos

<details markdown="1"><summary>Comprobación</summary>

**c)** La atención del modelo se deteriora a medida que se acumula contenido de poca relevancia. Una transcripción grande y desordenada hace más difícil que el modelo encuentre y priorice lo que importa. La opción a es incorrecta porque los callejones sin salida y las tareas completadas crean ruido incluso sin errores. La opción b es incorrecta porque un buen formato no resuelve el problema de la relación señal-ruido. La opción d es incorrecta porque la degradación del contexto está bien documentada en tareas de contexto largo.

</details>

4. ▢ Observas que la latencia de un agente aumenta a medida que crece su trayectoria. Nombra dos razones por las que ocurre esto.

<details markdown="1"><summary>Comprobación</summary>

Primero, el modelo recibe más tokens en cada llamada, lo que tarda más en procesarse. Segundo, el modelo tiene que cribar más contenido de poca relevancia (degradación del contexto) para encontrar la información que importa, lo que afecta la calidad de su razonamiento y puede hacer que cometa errores que desperdician turnos.

</details>

## Prácticas en el mundo real

- [ ] Describe a otra persona (o en una nota) por qué no puedes simplemente seguir descartando los turnos más antiguos de una transcripción cuando se hace demasiado larga. Usa un ejemplo de una tarea real que querrías que hiciera un agente.
- [ ] Abre la transcripción de una conversación larga de varios turnos que hayas tenido con un modelo de lenguaje, y anota a partir de cuántos turnos el modelo empieza a costarle recordar las restricciones del principio.
- [ ] Mañana: Planifica una tarea de investigación que un agente podría hacer (leer 20 archivos, comparar patrones, producir un resumen), y esboza qué tamaño tendría la transcripción si el agente mantuviera en memoria el contenido completo de cada archivo todo el tiempo frente a si solo guardara las rutas de los archivos y trajera el contenido bajo demanda.

## Para profundizar

- [Article: "Effective Context Engineering for AI Agents", Anthropic Engineering](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents)
- [Recursos](../RESOURCES.md)

---

¿No termina de quedar claro? Vuelve a leer la fuente primaria de arriba, ya que esta lección la comprime y en la compresión es donde se escapa la comprensión. Consulta el [glosario](../GLOSSARY.md) por si algún término te resultó resbaladizo.

Si lo poco claro es la propia lección y no el material, eso es un defecto: [abre un issue](https://github.com/TokenCemetery/teach/issues).
