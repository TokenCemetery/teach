---
title: "16. Planificar y luego ejecutar, y descomposición"
description: "La planificación explícita por adelantado como alternativa a ReAct, cuándo usarla y cómo manejar la replanificación"
type: lesson
---

# Lección 16. Planificar y luego ejecutar, y descomposición

**Vínculo con la misión:** Para elegir entre un solo prompt, un flujo de trabajo fijo y un agente para una tarea dada, necesitas reconocer cuándo la estructura adicional de un plan explícito vale su costo y cuándo es más barata la flexibilidad de ReAct.
**Fuente principal:** [Article: "Building Effective Agents", Anthropic Engineering](https://www.anthropic.com/engineering/building-effective-agents)
**Requisitos previos:** [Lección 15](0015-react-interleaving-reasoning-and-acting.md)

## Calentamiento

1. ▢ En ReAct, ¿qué pasa después de que se ejecuta una llamada a herramienta y el harness añade el resultado a la transcripción?

<details markdown="1"><summary>Comprobación</summary>

El siguiente turno del modelo recibe la transcripción con la llamada a herramienta y su resultado. El modelo puede entonces emitir razonamiento nuevo que reaccione a lo que la herramienta realmente devolvió, en lugar de ceñirse a un plan prefabricado.

</details>

2. ▢ Describe un escenario en el que la adaptación paso a paso de ReAct sea una ventaja frente a un plan rígido establecido por adelantado.

<details markdown="1"><summary>Comprobación</summary>

Cualquier escenario en el que el entorno pueda sorprender al agente: una búsqueda no devuelve nada (no los datos esperados), una herramienta falla, un usuario da comentarios que contradicen los supuestos, o llega información nueva a mitad de la tarea. En estos casos, ReAct permite al modelo observar la sorpresa y adaptarse, mientras que un plan rígido por adelantado ejecutaría a ciegas los pasos originales y fallaría o produciría resultados erróneos.

</details>

## Qué debes saber

### Planificación explícita y descomposición

Planificar y luego ejecutar es un enfoque distinto de ReAct. En lugar de intercalar razonamiento y acción, el primer paso del agente es producir una lista explícita y ordenada de subtareas o acciones. El modelo (o un planificador aparte) entrega un plan en lenguaje natural o en forma estructurada. El harness luego ejecuta el plan paso a paso. Si se admite la replanificación, el harness puede pedir un plan nuevo si un paso falla.

La descomposición es la idea general detrás de esto: dividir una tarea grande y ambigua en varias más pequeñas y bien definidas. Una subtarea más pequeña es más fácil de ejecutar correctamente para el modelo, y más fácil de verificar para una persona. Tanto si la descomposición ocurre de forma explícita (con un plan escrito) como implícita (en el razonamiento de ReAct en cada paso), el principio es el mismo.

### Cuándo un plan explícito se gana su costo

Un plan explícito ocupa espacio en la transcripción y requiere un turno extra del modelo (al menos uno) antes de que corra cualquier acción. Eso es sobrecarga. ¿Cuándo vale la pena pagar esa sobrecarga?

**Revisión humana antes de la ejecución:** Si una tarea implica mucho riesgo (llamar a una API que cuesta dinero, enviar un correo, borrar datos), una persona puede leer el plan antes de que el harness ejecute cualquier herramienta. La persona puede rechazar el plan, pedir cambios o aprobarlo con confianza. En cambio, ReAct ejecuta la primera acción antes de que una persona tenga visibilidad de lo que está a punto de pasar. Para las tareas donde se requiere aprobación humana o que reducen el riesgo, un plan explícito es un buen intercambio.

**Tareas de varios pasos con alto costo de las acciones erróneas:** Si cada paso es caro de deshacer o conlleva un riesgo alto, comprometerse con un plan por adelantado y que una persona lo revise antes de la ejecución reduce la probabilidad de errores costosos. Una tarea exploratoria donde los pasos son baratos (leer datos, hacer consultas que no cuestan nada) no necesita esta sobrecarga.

**Tareas con una estructura clara y estable:** Algunas tareas se descomponen en una secuencia obvia que no cambia: "Descargar el archivo A, analizarlo, transformarlo, subir el resultado". Si los pasos es poco probable que cambien a mitad de la ejecución, escribirlos por adelantado y ejecutarlos es más simple y barato que razonar de nuevo cada paso.

### El problema del plan obsoleto y la replanificación

Este es el riesgo: el plan se hizo antes de que corriera ninguna herramienta. Si el paso 1 debía encontrar un archivo, pero no existe, el plan del paso 2 asume que el archivo está ahí. El paso 2 fallará o producirá resultados erróneos. El harness entonces tiene dos opciones: seguir ejecutando a ciegas el plan obsoleto (y probablemente fallar) o activar la replanificación (pedirle al modelo que emita un plan nuevo dado el nuevo estado).

La replanificación no es gratis: cuesta otro turno del modelo, y la trayectoria ahora muestra varias etapas de plan, lo que consume contexto. Pero la replanificación suele ser más barata que ReAct para tareas de alta estructura, porque el modelo puede pensar rápido el nuevo camino en lugar de razonar paso a paso.

Si no se admite la replanificación, un harness de planificar y luego ejecutar fallará en silencio o con estrépito cuando la realidad no coincida con el plan. Por eso "¿admites la replanificación?" es una pregunta de diseño clave para los agentes de planificar y luego ejecutar.

### Descomposición sin planificación explícita

Ten en cuenta que la descomposición y la planificación explícita son ideas separadas. Un agente puede descomponer tareas de forma implícita, mediante razonamiento al estilo ReAct en cada paso. El modelo razona "para resolver esto, necesito hacer X, luego Y, luego Z" y luego hace X, observa el resultado, razona otra vez y pasa a Y. Esto es descomposición implícita. Un plan explícito escribe esa lista "X, Y, Z" como un artefacto estructurado antes de que empiece la ejecución.

Para muchas tareas, la descomposición implícita (ReAct) es más simple y más robusta. Usa la planificación explícita cuando la sobrecarga (revisión humana, claridad, estructura) valga el costo.

### Comparar los tres patrones

Solo actuar es lo más simple pero lo más difícil de depurar. ReAct añade razonamiento y observación, haciéndolo visible y adaptativo. Planificar y luego ejecutar añade una estructura previa que se puede revisar antes de que corra cualquier acción, a costa de un turno extra del modelo y de una posible obsolescencia si se rompen los supuestos del plan.

Elige según tu tarea y tus restricciones:

- ¿Tarea exploratoria corta, sin mucho riesgo? Usa ReAct.
- ¿Tarea con pasos claros que es poco probable que cambien? Usa planificar y luego ejecutar.
- ¿Tarea en la que una persona necesita revisar antes de que empiece la ejecución? Usa planificar y luego ejecutar con una puerta de aprobación.
- ¿Tarea en la que los pasos son caros y los fallos son costosos? Usa planificar y luego ejecutar con soporte de replanificación.

## Práctica

1. ▢ Una tarea es "Presentar una queja ante el ayuntamiento, comprobar que se recibió y notificar al usuario". Esto implica rellenar un formulario (no es gratis repetirlo), comprobar un correo de confirmación y enviar un correo. ¿Sería mejor la planificación explícita o ReAct para esta tarea? ¿Por qué?

<details markdown="1"><summary>Comprobación</summary>

La planificación explícita es mejor. Los pasos son claros y estables: rellenar el formulario, comprobar la confirmación, enviar el correo. No hay razón para esperar que esta secuencia cambie a mitad de la ejecución. Una persona debería revisar el plan antes de que se rellene el formulario, ya que ese paso no es fácil de deshacer. ReAct funcionaría pero ejecutaría el paso de rellenar el formulario antes de que una persona pueda revisarlo, lo que añade riesgo.

</details>

2. ▢ Estás construyendo un agente que investiga por qué la cuenta de un usuario está bloqueada. El agente podría comprobar el estado de la cuenta, buscar en los logs inicios de sesión fallidos, buscar una marca de seguridad o consultar tickets de soporte, según lo que encuentre. ¿Sería mejor la planificación explícita o ReAct?

<details markdown="1"><summary>Pista</summary>

Piensa si la secuencia de pasos se conoce de antemano o si depende de lo que devuelvan los pasos anteriores.

</details>

<details markdown="1"><summary>Comprobación</summary>

ReAct es mejor. Los pasos dependen de lo que el agente encuentra en cada etapa. Si el estado de la cuenta muestra una marca de seguridad, el siguiente paso es comprobar eso. Si muestra un error distinto, el siguiente paso es otro. La secuencia no se puede escribir por adelantado. El razonamiento y la observación paso a paso de ReAct es más natural que intentar planificar todas las ramas posibles.

</details>

3. ▢ ¿Cuál de las siguientes describe mejor cuándo se vuelve necesaria la replanificación en un agente de planificar y luego ejecutar?

    - a) Siempre que el agente encuentra una llamada a herramienta con un parámetro que el plan no mencionaba.
    - b) Cuando una llamada a herramienta falla o devuelve datos inesperados que contradicen un supuesto del plan original.
    - c) Siempre que el usuario cambia de opinión sobre la tarea.
    - d) Después de cada llamada a herramienta, para asegurar que el plan se mantiene fresco.

<details markdown="1"><summary>Comprobación</summary>

**b)** La replanificación se activa por fallos o sorpresas reales: una herramienta no devolvió nada cuando el plan esperaba datos, falló una llamada a una API o una búsqueda no encontró lo esperado. a) es incorrecta, las herramientas a menudo tienen parámetros que el plan no listó; eso no es un error. c) es incorrecta, los cambios del usuario son un problema a nivel de tarea, no específico de planificar y luego ejecutar frente a ReAct. d) es incorrecta, replanificar tras cada paso anula el propósito de tener un plan y es ineficiente.

</details>

4. ▢ El plan explícito de un agente es "Paso 1: Buscar la entrada del usuario. Paso 2: Resumir los resultados. Paso 3: Comparar el resumen con la pregunta original del usuario". Tras el paso 1, la búsqueda no devuelve resultados. El harness no admite la replanificación. ¿Qué es probable que pase?

<details markdown="1"><summary>Comprobación</summary>

El paso 2 (resumir los resultados) fallará o producirá una salida errónea porque no hay resultados que resumir. El agente se colgará, devolverá un error o producirá un resumen de la nada. El harness no tendrá forma de pivotar: se comprometió con el plan desde el principio. Este es el costo de un harness de planificar y luego ejecutar sin soporte de replanificación. La solución es añadir replanificación (pedirle al modelo que haga un plan nuevo cuando falla el paso 1) o pasar a ReAct, donde el modelo razonaría tras el resultado del paso 1 y decidiría probar otra búsqueda.

</details>

## Prácticas en el mundo real

- [ ] Toma una tarea de varios pasos que hagas con regularidad (por ejemplo, procesar un pedido, investigar un problema, revisar un documento por cumplimiento). Escribe los pasos que realmente sigues. ¿Los pasos ocurren siempre en el mismo orden, o el orden depende de lo que encuentras en cada paso? Si el orden es fijo, es candidata a planificar y luego ejecutar con aprobación explícita. Si el orden es adaptativo, es candidata a ReAct.
- [ ] Construye un pequeño agente de planificar y luego ejecutar para una tarea de secuencia fija (por ejemplo, descargar un archivo, analizarlo, transformarlo, subirlo). Ejecútalo cinco veces con entradas distintas y lee las trayectorias. ¿Falló alguna vez el agente porque el plan original no coincidía con la realidad? Si es así, añade una puerta de replanificación después de las llamadas a herramientas que puedan fallar.
- [ ] Mañana: Encuentra un agente existente que hayas construido o usado. Clasifícalo como solo actuar, ReAct o planificar y luego ejecutar según su trayectoria. Escribe una nota de una frase sobre por qué ese patrón encaja con la tarea.

## Para profundizar

- [Article: "Building Effective Agents", Anthropic Engineering](https://www.anthropic.com/engineering/building-effective-agents)
- [Recursos](../RESOURCES.md)

---

¿No termina de quedar claro? Vuelve a leer la fuente primaria de arriba, ya que esta lección la comprime y en la compresión es donde se escapa la comprensión. Consulta el [glosario](../GLOSSARY.md) por si algún término te resultó resbaladizo.

Si lo poco claro es la propia lección y no el material, eso es un defecto: [abre un issue](https://github.com/TokenCemetery/teach/issues).
