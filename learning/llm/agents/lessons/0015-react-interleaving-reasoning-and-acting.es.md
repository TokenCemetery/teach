---
title: "15. ReAct: intercalar razonamiento y acción"
description: "El patrón de emparejar breves pasos de razonamiento con cada acción, para que el modelo pueda observar y adaptarse"
type: lesson
---

# Lección 15. ReAct: intercalar razonamiento y acción

**Vínculo con la misión:** Para diagnosticar un agente que falla, reconocerás si está ejecutando acciones sin razonamiento visible (donde se esconde la causa raíz), siguiendo un plan rígido establecido por adelantado (donde las sorpresas del entorno causan fallos en cascada) o intercalando razonamiento con observación (donde las señales de fallo fluyen de vuelta a la siguiente decisión).
**Fuente principal:** [Paper: "ReAct: Synergizing Reasoning and Acting in Language Models", Yao et al., 2022](https://arxiv.org/abs/2210.03629)
**Requisitos previos:** [Lección 14](0014-files-as-memory.md), [Bucle del agente](../GLOSSARY.md)

## Calentamiento

1. ▢ Cuando guardas la memoria de un agente en un archivo entre ejecuciones (digamos, una transcripción de chat o un registro de decisiones pasadas), ¿qué se vuelve más fácil de depurar y verificar sobre el comportamiento del agente?

<details markdown="1"><summary>Comprobación</summary>

Una memoria basada en archivos te permite leer el estado exacto que vio el agente antes de cada decisión, de modo que puedes reproducir su razonamiento y comprobar si tomó una elección sensata dada la información disponible en ese momento. Si el agente parece roto, puedes leer su trayectoria previa para encontrar el paso exacto en el que se equivocó, en lugar de adivinar.

</details>

2. ▢ Nombra un riesgo de guardar memorias grandes en archivos: ¿qué pasa si el agente nunca poda ni compacta el archivo?

<details markdown="1"><summary>Comprobación</summary>

El archivo crece sin límite, consumiendo espacio en disco y presupuesto de contexto cuando se pasa al modelo. Con el tiempo el agente no puede meter todo el historial en la ventana de contexto, lo que obliga al harness a elegir qué memorias antiguas descartar y cuáles conservar.

</details>

## Qué debes saber

### Tres formas de razonar y actuar

El bucle del agente admite de forma natural varios patrones distintos sobre cuándo ocurre el razonamiento respecto de cuándo se ejecutan las acciones. El paper de ReAct identifica tres, y entender los compromisos entre ellos es clave para diagnosticar los fallos de los agentes.

**Solo actuar:** El modelo recibe la tarea y el estado actuales, y emite de inmediato una llamada a herramienta sin razonamiento declarado. El harness ejecuta la herramienta, añade el resultado y repite el bucle. Es la estructura más simple.

El riesgo: Cuando algo sale mal, no puedes saber por qué el modelo eligió esta acción. ¿Entendió mal la tarea? ¿Creyó que estaba llamando a otra herramienta? Sin una traza de razonamiento, depurar es adivinar. Acabas añadiendo aclaraciones al prompt ("Piensa paso a paso", "Verifica tu respuesta"), pero el modelo sigue sin producir razonamiento visible que puedas inspeccionar, así que las aclaraciones pueden no servir.

**Razonar y luego actuar una vez:** El modelo lee la tarea, razona todo el plan por adelantado en texto (llama a esto la fase de "pensamiento"), y luego se compromete con una secuencia de llamadas a herramientas para ejecutar el plan. Una vez comprometido el plan, el harness ejecuta todos los pasos sin replanificar.

Esto evita las conjeturas a ciegas del solo actuar, ya que puedes ver el razonamiento completo del modelo. Pero tiene un costo oculto: el plan se hace antes de que corra ninguna herramienta. Si una llamada a herramienta falla o devuelve datos inesperados, el plan queda obsoleto. El modelo no puede reaccionar a las sorpresas porque ya se ha comprometido con la secuencia. Terminas teniendo que volver a ejecutar el agente y esperar que la nueva fase de razonamiento se corrija sola.

**ReAct (razonar, actuar y observar de forma intercalada):** El modelo razona en voz alta sobre qué hacer a continuación (un breve texto de "pensamiento" o de "razonamiento"), y luego emite una llamada a herramienta. El harness ejecuta la herramienta, añade el resultado a la transcripción y repite el bucle. En el siguiente turno, el modelo lee el pensamiento anterior, la acción que eligió y el resultado real, y luego razona sobre el siguiente paso a partir de lo que ahora ve.

Este es el patrón ReAct. El razonamiento del modelo es visible (puedes depurarlo), pero lo más importante es que el razonamiento de cada paso puede incorporar el resultado real del paso anterior. Si una búsqueda no devolvió resultados, el siguiente pensamiento puede pivotar a otra búsqueda. Si una llamada a una API falló, el siguiente pensamiento puede reflejarlo e intentar una solución alternativa. El razonamiento no es un plan rígido establecido por adelantado; es una observación de lo que acaba de ocurrir, que alimenta lo que ocurre después.

### Por qué gana ReAct cuando el entorno te sorprende

Razonar y luego actuar una vez funciona bien en escenarios de mundo cerrado donde se garantiza que los supuestos del plan se cumplen. Las llamadas reales a herramientas ocurren en escenarios de mundo abierto: faltan archivos, las búsquedas no devuelven nada, las APIs están caídas, los usuarios dan instrucciones contradictorias. En esos casos, la adaptación paso a paso de ReAct es más barata y más robusta que volver a ejecutar el ciclo completo de razonar y luego actuar.

Piensa en el propio bucle del agente, de la lección 6. Un turno del modelo produce texto (que puede incluir razonamiento) y una llamada a herramienta. Esa llamada se ejecuta y el resultado se añade a la transcripción. En el siguiente turno, el modelo ve el resultado y emite texto nuevo y una nueva llamada a herramienta. Por diseño, el bucle del agente ya admite ReAct: cualquier texto de razonamiento que emita el modelo se conserva en la transcripción, el siguiente turno puede observarlo y el siguiente turno puede emitir razonamiento nuevo que reaccione al resultado observado.

"¿Mi harness admite ReAct?" es en realidad solo "¿Mi harness conserva en la transcripción el texto de razonamiento del modelo y se lo devuelve en el siguiente turno?" La respuesta, en casi todo harness que valga la pena usar, es sí.

### Diagnosticar los fallos de solo actuar y de planificar y actuar una vez

Si inspeccionas la trayectoria de un agente y no ves texto de razonamiento antes de las llamadas a herramientas, tienes un agente de solo actuar. Los fallos son difíciles de diagnosticar. Añadir más datos al contexto (descripciones de tarea más largas, más ejemplos) puede ayudar, pero sin texto de razonamiento no tienes visibilidad. La solución es inducir al modelo a emitir razonamiento (un campo de "pensamiento", una sección de "razonamiento" en la llamada a herramienta, lo que sea) y conservarlo en la transcripción. Entonces pasas a ReAct y depurar se vuelve posible.

Si ves un gran bloque de razonamiento al principio, seguido de una secuencia de acciones sin razonamiento intermedio, tienes planificar y actuar una vez. Cuando el agente falla, es probable que estés viendo un plan que no sobrevivió al contacto con la realidad. La solución es permitir la replanificación: después de cada resultado de herramienta, emitir razonamiento nuevo antes de la siguiente acción. De nuevo, esto te lleva a ReAct. Algunos fallos desaparecerán porque el modelo ahora puede adaptarse.

## Práctica

1. ▢ A un agente se le dice "Busca información sobre el cambio climático y luego resume los 5 primeros resultados". Emite una llamada a la herramienta de búsqueda sin texto de razonamiento previo. La búsqueda devuelve 10 resultados sobre ciencia del clima, y el agente emite a continuación una llamada a una herramienta de resumen sin razonamiento intermedio. El resumen es inexacto. ¿Por qué es difícil saber si el modelo malentendió la tarea, malentendió los resultados o cometió un error genuino de razonamiento?

<details markdown="1"><summary>Comprobación</summary>

No hay texto de razonamiento en la transcripción, así que no puedes ver cuál era el "objetivo" interno del modelo ni cómo interpretó los resultados de la búsqueda. El razonamiento ausente hace imposible distinguir entre, por ejemplo, "el modelo no se dio cuenta de que la búsqueda devolvió 10 resultados y pensó que necesitaba buscar otra vez" y "el modelo vio los 10 resultados y malentendió la tarea como resumirlos todos, no los 5 primeros". Añadir texto de razonamiento antes del paso de resumen (un pensamiento al estilo ReAct) te permitiría ver qué malentendido ocurrió y corregir el prompt en consecuencia.

</details>

2. ▢ Estás construyendo un agente que recibe comentarios del usuario y refina un documento. El plan del agente (emitido por adelantado) es "Corregir la gramática, luego añadir ejemplos, luego comprobar la longitud". La primera pasada tiene éxito. Pero los comentarios del usuario en la segunda ejecución son "No me gustan los ejemplos nuevos que añadiste, pero conserva las correcciones de gramática". El agente reutiliza el plan inicial sin cambios y vuelve a añadir ejemplos, ignorando los comentarios.

<details markdown="1"><summary>Pista</summary>

¿Qué hace obsoleto al plan en este escenario? ¿Qué información no está viendo el agente cuando planifica?

</details>

<details markdown="1"><summary>Comprobación</summary>

El plan se hizo sin ver los comentarios del usuario. En planificar y actuar una vez, la fase de razonamiento ocurre antes de que corra ninguna herramienta, así que no puede incorporar información nueva que llega a mitad de la trayectoria. La solución es permitir el razonamiento y la replanificación después de cada resultado de herramienta (aquí, después de cada paso de refinamiento), para que el plan del agente pueda adaptarse cuando los comentarios del usuario contradicen los supuestos originales.

</details>

3. ▢ ¿Cuál de las siguientes es una señal de que deberías pasar un agente de solo actuar a ReAct?

    - a) El agente es demasiado lento y necesitas acelerar las llamadas a herramientas.
    - b) Los fallos del agente son difíciles de diagnosticar porque no puedes ver por qué eligió cada acción.
    - c) El agente necesita usar 10 herramientas en lugar de 5.
    - d) La ventana de contexto del agente está casi llena.

<details markdown="1"><summary>Comprobación</summary>

**b)** Los agentes de solo actuar no producen texto de razonamiento, así que sus fallos son opacos. Pasar a ReAct (añadir un paso de razonamiento antes de cada acción) hace visible el razonamiento del modelo, que es la ganancia central para depurar. a) es incorrecta porque ReAct no acelera las llamadas a herramientas, añade texto de razonamiento que lleva tiempo. c) es incorrecta, el número de herramientas no guarda relación. d) es incorrecta, la presión del contexto es una preocupación distinta de si el agente razona en voz alta.

</details>

4. ▢ Un agente busca "best pizza restaurants in Portland" y recibe 5 resultados. Si el agente se ejecuta en modo ReAct, ¿qué debería ocurrir a continuación en la transcripción?

<details markdown="1"><summary>Comprobación</summary>

El agente debería emitir un paso de razonamiento (una sección de "pensamiento" o de "razonamiento") que observe los resultados de la búsqueda y decida qué hacer a continuación (por ejemplo, "These results look good, I now have enough information to answer. I will summarize them" o "I need more details about restaurant hours, I will fetch those next"). Este razonamiento se basa en lo que la búsqueda realmente devolvió, no en un plan establecido por adelantado. Al incluirlo en la transcripción, la siguiente llamada a herramienta (si la hay) puede basarse en el resultado real.

</details>

## Prácticas en el mundo real

- [ ] Toma un agente existente que hayas construido o que conozcas. Lee su trayectoria (una ejecución completa). Cuenta cuántas llamadas a herramientas tienen texto de razonamiento inmediatamente antes. Si menos del 80 % tienen texto de razonamiento, reescribe el prompt o el esquema de la herramienta para emitir razonamiento, y vuelve a ejecutarlo.
- [ ] Rompe a propósito una herramienta de la que dependa un agente (por ejemplo, haz que una API de búsqueda devuelva un resultado vacío). Ejecuta el agente en una tarea en la que normalmente tendría éxito. Lee la trayectoria. ¿Emitió el agente razonamiento que reconociera la herramienta rota y pivotara hacia otro enfoque? Si no, añade una instrucción de prompt para razonar y reintenta.
- [ ] Mañana: Pídele a un colega que lea la trayectoria de un agente sin ver la tarea. ¿Puede inferir qué intentaba hacer el agente en cada paso solo a partir del texto de razonamiento? Si no puede, añade prompts de razonamiento.

## Para profundizar

- [Paper: "ReAct: Synergizing Reasoning and Acting in Language Models", Yao et al., 2022](https://arxiv.org/abs/2210.03629)
- [Recursos](../RESOURCES.md)

---

¿No termina de quedar claro? Vuelve a leer la fuente primaria de arriba, ya que esta lección la comprime y en la compresión es donde se escapa la comprensión. Consulta el [glosario](../GLOSSARY.md) por si algún término te resultó resbaladizo.

Si lo poco claro es la propia lección y no el material, eso es un defecto: [abre un issue](https://github.com/TokenCemetery/teach/issues).
