---
title: "7. La transcripción como estado"
description: "Entender que la transcripción es la única memoria persistente del agente entre turnos"
type: lesson
---

# Lección 7. La transcripción como estado

**Vínculo con la misión:** Reconocer la transcripción como el único estado del agente te ayuda a diagnosticar un agente que falla a partir de su trayectoria en lugar de adivinar por qué el modelo está confundido o se repite, lo que sirve a la misión de "diagnosticar un agente que falla a partir de su trayectoria".
**Fuente principal:** [Article: "Building Effective Agents", Anthropic Engineering](https://www.anthropic.com/engineering/building-effective-agents)
**Requisitos previos:** [Lección 6](0006-writing-the-loop.md), [Trayectoria](../GLOSSARY.md)

## Calentamiento

1. ▢ De la lección 6: Después de que el harness llama al modelo y recibe una respuesta, ¿qué debe ocurrir antes de que el harness ejecute cualquier llamada a herramienta?

<details markdown="1"><summary>Comprobación</summary>

La respuesta debe añadirse a la transcripción de inmediato, antes de ejecutar cualquier herramienta. De lo contrario, la petición del propio modelo nunca queda registrada, y un turno posterior no mostrará por qué hay un resultado de herramienta.

</details>

2. ▢ De la lección 6: Nombra dos condiciones de parada distintas que un harness puede comprobar para terminar el bucle del agente.

<details markdown="1"><summary>Comprobación</summary>

Cualquier par de estas: el modelo devuelve un turno sin llamada a herramienta, se alcanza un límite de máximo de turnos o de presupuesto de tokens, el modelo llama a una herramienta de parada explícita, o se supera un umbral de conteo de errores.

</details>

## Qué debes saber

### La transcripción es lo único que persiste

Entre una llamada al modelo y la siguiente, el harness guarda dos cosas:

1. La transcripción: el historial completo de la conversación, incluidas cada respuesta del modelo, llamada a herramienta y resultado de herramienta.
2. Los metadatos del harness: contadores (número de turnos, número de errores), límites (máximo de turnos, máximo de errores), registros de herramientas, configuración.

El modelo no ve los metadatos del harness. El modelo solo ve la transcripción. Si un hecho no está en la transcripción, el modelo no sabe que ocurrió.

Esto es a la vez simple y profundo. Significa que:

- El modelo no puede razonar sobre algo que el harness decidió internamente a menos que el harness lo ponga en la transcripción.
- Entre turnos, no persiste nada más. Ni banderas internas, ni estado oculto, ni variables fuera de los metadatos del harness.
- Reproducir una ejecución de un agente significa volver a darle al modelo la misma transcripción y continuar desde ahí.

### La trayectoria diverge de la transcripción

Una trayectoria es el registro completo de lo que pasó: cada turno, decisión, log y efecto secundario. Una transcripción es lo que se le mostró al modelo. No son lo mismo.

Por ejemplo:

- El harness ejecuta una llamada a herramienta, obtiene un resultado de 100 KB, pero decide que el resultado es demasiado largo y lo trunca antes de añadirlo a la transcripción. La trayectoria dice "la llamada a herramienta tuvo éxito, el resultado fue de 100 KB"; la transcripción dice "la llamada a herramienta tuvo éxito, el resultado fueron los primeros 10 KB". El modelo solo conoce la segunda versión.
- El harness decide reintentar una herramienta porque falló el primer intento. El log de decisiones va a un archivo para que una persona lo depure más tarde. Pero el harness nunca añade "voy a reintentar" a la transcripción. En el siguiente turno, el modelo no sabe que hubo un reintento; solo ve los resultados.
- Una llamada a herramienta falla en silencio. El harness la registra pero no añade un mensaje de error a la transcripción porque quien diseñó el harness se olvidó. El modelo nunca se entera de que la herramienta falló. En el siguiente turno, el modelo podría pedir la misma herramienta otra vez, confundido sobre por qué no funcionó.

La consecuencia es que puedes mirar una trayectoria y concluir "el harness tomó una decisión sensata", pero si solo miras la transcripción, ves a un modelo confundido. El modelo no está confundido. Simplemente no se le dijo.

### Un ejemplo resuelto: el resultado de herramienta que nunca fue

Imagina este escenario:

El agente debe buscar un precio, luego aplicar un descuento y luego confirmar. En el turno dos, el modelo llama a una herramienta para obtener el precio. La herramienta devuelve "Item XYZ costs $100". El harness ejecuta la herramienta, obtiene el resultado y lo añade a la transcripción:

```text
Agent turn 1: "I will find the price of item XYZ"
Agent turn 1 tool call: fetch_price(item="XYZ")
Tool result: "Item XYZ costs $100"

Agent turn 2: "I will apply a 10% discount. $100 - 10% = $90."
Agent turn 2 tool call: confirm_price(item="XYZ", price="$90")
```

Esto funciona. El modelo vio el resultado y razonó correctamente.

Ahora imagina una variante: el harness registra resultados en una base de datos para monitoreo. La inserción del log falla. El harness registra el error en un archivo, pero el desarrollador nunca añadió nada a la transcripción. El siguiente turno empieza así:

```text
Agent turn 1: "I will find the price of item XYZ"
Agent turn 1 tool call: fetch_price(item="XYZ")

Agent turn 2: "I need to fetch the price. Let me call fetch_price again."
Agent turn 2 tool call: fetch_price(item="XYZ")
```

El modelo vuelve a pedir el precio. No está siendo terco ni tonto. La transcripción nunca muestra el resultado del turno uno. El modelo no tiene forma de saber que la llamada tuvo éxito. A esto se le llama divergencia: la trayectoria dice "el resultado se obtuvo y se registró", pero la transcripción dice "no pasó nada".

La solución es añadir siempre a la transcripción antes de seguir adelante, incluso si fallan los efectos secundarios:

```text
Tool result (appended immediately): "Item XYZ costs $100"

[Later, harness logs to database, but the append already happened]
Log to database failed [this error never goes in the transcript]
```

Ahora el modelo sabe que el resultado ocurrió, sin importar los errores posteriores.

### Por qué la transcripción como estado facilita la reanudación

Supón que la ejecución de un agente se interrumpe. El harness se cae, la red falla, se alcanza la cuota. Quieres reanudar el agente donde lo dejó.

Si el agente guarda estado en variables internas, banderas y decisiones dispersas por el harness, reanudar es difícil. Tienes que guardar todo ese estado, restaurarlo y esperar no haberte dejado nada.

Si el estado del agente es solo la transcripción, reanudar es trivial: guarda la transcripción y luego empieza una nueva ejecución volviendo a darle al modelo la misma transcripción y continuando el bucle desde el siguiente turno. El modelo verá todo lo que vio antes y seguirá razonando. No hay estado oculto que reconstruir, ni banderas que restaurar, ni variables que seguir. La transcripción es el contrato.

Del mismo modo, puedes reproducir la ejecución de un agente para depurarla. Vuelve a dar la trayectoria (el log completo de lo que pasó) como transcripción, y mira qué haría el modelo a continuación. Incluso puedes editar la transcripción a mano para probar qué haría el modelo en una situación hipotética.

## Práctica

1. ▢ Un agente debe buscar un documento, leerlo y resumirlo. En el turno dos, llama a una herramienta de búsqueda y la herramienta devuelve 10 resultados. Antes de añadir el resultado a la transcripción, el harness filtra los resultados a los tres más relevantes y añade solo esos. ¿Qué ve el modelo, y por qué esta decisión de diseño es visible cuando lees la transcripción?

<details markdown="1"><summary>Comprobación</summary>

El modelo ve tres resultados, no diez. No sabe que el harness filtró; solo sabe lo que hay en la transcripción. Es un diseño aceptable si es intencional: el harness eligió reducir el uso de tokens filtrando. Lo importante es que al leer la transcripción puedes ver exactamente lo que vio el modelo (tres resultados) y razonar si su siguiente decisión fue sensata dada esa información. No te confunde el hecho de que existieran diez resultados; la transcripción muestra el mundo desde la perspectiva del modelo.

</details>

2. ▢ Quien desarrolla un harness quiere registrar qué herramientas se llamaron y cuántas veces. ¿Debe guardar este conteo en una variable solo del harness, o añadir un resumen a la transcripción antes de cada llamada al modelo?

<details markdown="1"><summary>Pista</summary>

Piensa en qué necesita saber el modelo para tomar decisiones, y qué información solo sería útil para que una persona depure después de la ejecución.

</details>

<details markdown="1"><summary>Comprobación</summary>

Depende del caso de uso. Si el modelo necesita saber "ya has llamado a search tres veces, quizá prueba otra herramienta", entonces el conteo debe ir en la transcripción. Si el conteo es puramente para monitoreo y el modelo no necesita ajustar su comportamiento según él, basta una variable solo del harness. Pero si al modelo le podría beneficiar conocer el conteo, ponlo en la transcripción para que el modelo lo vea en el siguiente turno. Un valor por defecto seguro es añadir todo lo que pueda afectar la siguiente decisión del modelo.

</details>

3. ▢ Estás depurando la ejecución de un agente. Lees la trayectoria y ves que una llamada a herramienta tuvo éxito y el resultado se añadió. Lees la transcripción que el modelo realmente vio y el resultado no está. ¿Qué pasó?

    - a) El harness añadió el resultado, y luego lo quitó de la transcripción antes de volver a llamar al modelo
    - b) Se supone que la trayectoria y la transcripción son distintas; la transcripción es un resumen y la trayectoria es completa
    - c) El resultado se añadió a los logs del harness pero no a la transcripción; el modelo nunca lo vio
    - d) La llamada a herramienta en realidad falló y la trayectoria está mal

<details markdown="1"><summary>Comprobación</summary>

**c)** El resultado se añadió a los logs del harness pero no a la transcripción; el modelo nunca lo vio. Las trayectorias y las transcripciones deberían ser casi idénticas desde la perspectiva del modelo (aunque las transcripciones pueden truncarse o muestrearse por eficiencia). Si la trayectoria dice que algo ocurrió pero la transcripción no lo muestra, la causa más probable es que el harness lo registró pero no lo añadió a la transcripción. Este es el error mostrado en el ejemplo resuelto. Quitarlo de la transcripción después de añadirlo (a) sería inusual y anularía el propósito. Las transcripciones no son resúmenes; deberían ser el historial de la conversación (b). Un error de la trayectoria (d) es posible pero menos común que un error de registro.

</details>

4. ▢ Quieres construir un agente reanudable. La ejecución se interrumpe tras cinco turnos. Escribe en una frase qué necesitas persistir en disco para reanudar el agente desde el turno seis.

<details markdown="1"><summary>Comprobación</summary>

Necesitas persistir la transcripción (el historial de la conversación hasta el turno cinco, incluidas cada respuesta del modelo, llamada a herramienta y resultado de herramienta). Al reanudar, dale esta transcripción al modelo como contexto inicial, llama al modelo y continúa el bucle. Los metadatos del harness (contador de turnos, contador de errores, etc.) se pueden reconstruir o reiniciar; solo la transcripción es esencial.

</details>

## Prácticas en el mundo real

- [ ] Ejecuta un agente (de una biblioteca que uses o uno que escribas) que haga al menos tres llamadas a herramientas. Inspecciona la transcripción que generó. Para cada resultado de herramienta, verifica que el resultado está presente en lo que el modelo vería en el siguiente turno. Si falta algún resultado, rastrea por qué (¿no se añadió, se truncó o se filtró?).

- [ ] Encuentra un lugar en el código de tu agente o de tu harness donde se registre información pero no se añada a la transcripción. Pregúntate: ¿necesita el modelo saber esto para tomar mejores decisiones? Si es así, añádelo a la transcripción. Si no, déjalo como un log solo del harness.

- [ ] Mañana: Diseña un agente reanudable desde cero. Escribe el pseudocódigo de la función de ejecución que toma una transcripción como entrada y reanuda desde el siguiente turno. Verifica que no dependes de ningún estado solo del harness para tomar decisiones.

## Para profundizar

- [Article: "Building Effective Agents", Anthropic Engineering](https://www.anthropic.com/engineering/building-effective-agents)
- [Recursos](../RESOURCES.md)

---

¿No termina de quedar claro? Vuelve a leer la fuente primaria de arriba, ya que esta lección la comprime y en la compresión es donde se escapa la comprensión. Consulta el [glosario](../GLOSSARY.md) por si algún término te resultó resbaladizo.

Si lo poco claro es la propia lección y no el material, eso es un defecto: [abre un issue](https://github.com/TokenCemetery/teach/issues).
