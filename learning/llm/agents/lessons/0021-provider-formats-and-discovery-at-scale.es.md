---
title: "21. Formatos de proveedor y descubrimiento de herramientas a escala"
description: "Cómo MCP y los formatos de transmisión propios de cada proveedor son capas separadas, y por qué cargar todas las herramientas en el contexto no escala a muchos servidores conectados"
type: lesson
---

# Lección 21. Formatos de proveedor y descubrimiento de herramientas a escala

**Vínculo con la misión:** Entender los límites del descubrimiento ingenuo de herramientas cuando un agente se conecta a muchos servidores MCP, y reconocer cuándo cambiar la carga anticipada de herramientas por un descubrimiento perezoso o programático.
**Fuente principal:** [Article: "Code Execution with MCP", Anthropic Engineering](https://www.anthropic.com/engineering/code-execution-with-mcp)
**Requisitos previos:** [Lección 20](0020-mcp-tools-resources-and-prompts.md)

## Calentamiento

1. ▢ En la lección 3 aprendiste dos formatos de transmisión: Anthropic representa una llamada a herramienta con `input_schema`, y OpenAI usa una forma distinta llamada `function.parameters`. Si pasas de la API de Anthropic a la de OpenAI, ¿necesitas cambiar tu servidor MCP, tu cliente MCP o ambos?

<details markdown="1"><summary>Comprobación</summary>

Ninguno. Tu servidor MCP sigue igual (sabe cómo exponer herramientas en formato MCP). Cambia tu harness, porque tiene que traducir las definiciones de herramientas de MCP al formato de transmisión que espere el modelo de cada proveedor. Cambia el proveedor del modelo, pero el protocolo MCP no.

</details>

2. ▢ En la lección 9 aprendiste sobre el exceso de herramientas: si le presentas al modelo demasiadas definiciones de herramientas, se ralentiza, se confunde o olvida qué herramienta usar. Cuando un agente se conecta a cinco servidores MCP con diez herramientas cada uno, ¿ve el modelo cincuenta definiciones de herramientas desde el principio?

<details markdown="1"><summary>Comprobación</summary>

Solo si el harness carga las cincuenta definiciones en el contexto antes de que empiece el bucle. Ese es el enfoque ingenuo. Pero hay otras formas: el harness podría cargar las herramientas solo cuando el modelo las pida, o traducir las definiciones de herramientas a código que el modelo pueda explorar y llamar de forma programática.

</details>

## Qué debes saber

### Dos capas independientes

MCP es un protocolo entre un harness de agente y herramientas o fuentes de datos externas. Define cómo hablan entre sí un cliente y un servidor y qué capacidades puede exponer un servidor. Pero a MCP no le importa qué formato de transmisión use el modelo.

Al mismo tiempo, el modelo tiene un proveedor, y ese proveedor tiene una forma específica de representar las llamadas a herramientas. La API de Anthropic acepta herramientas en una forma. La API de OpenAI las acepta en otra. Este formato de transmisión es una capa separada entre el harness y el modelo.

Estas dos capas son independientes:

- El cliente MCP (del lado del harness) habla MCP con el servidor MCP. El servidor MCP es agnóstico sobre qué modelo usará finalmente estas herramientas.
- El harness luego traduce las definiciones de herramientas de MCP al formato de transmisión que espere el modelo de cada proveedor. ¿Anthropic? Usa `input_schema`. ¿OpenAI? Usa `function.parameters`.

El harness tiene que hacer la traducción, porque está en el medio. Pero cambiar una capa no requiere reescribir la otra. Si cambias de proveedor de modelos, no reescribes tus servidores MCP. Si te conectas a un servidor MCP nuevo, el formato de transmisión entre el harness y el modelo no cambia.

### Descubrimiento de herramientas a escala

En un solo agente, podrías cablear a mano dos o tres herramientas en el contexto al principio. El exceso de herramientas (lección 9) aparece alrededor de cinco a diez herramientas. Pero ¿y si el harness está conectado a una docena de servidores MCP, cada uno con entre diez y veinte herramientas? Cientos de definiciones de herramientas.

El enfoque ingenuo es cargar todas las definiciones de herramientas al arrancar, traducir cada una al formato de transmisión del proveedor y dárselas todas al modelo en su contexto inicial. Esto reproduce el exceso de herramientas a una escala mucho mayor. El modelo lee cientos de definiciones, desperdicia tokens en descripciones que no necesita y se ralentiza en cada turno porque todas las herramientas están en el contexto. Y si se añade una herramienta nueva a un servidor conectado, cambia todo el contexto y el comportamiento del modelo.

Este es el problema del descubrimiento de herramientas a escala: puedes conectarte a muchos servidores, pero no cargándolo todo por adelantado.

### La idea de la ejecución de código

El artículo de Anthropic Engineering "Code Execution with MCP" propone una solución: en lugar de cargar definiciones de herramientas en el contexto, presentar las herramientas disponibles como código que el agente puede descubrir y llamar de forma programática.

Por ejemplo:

- El harness define una función auxiliar list_available_tools() que consulta los servidores MCP conectados y devuelve un directorio de funciones invocables: sus nombres, descripciones y parámetros.
- El harness define una función auxiliar call_tool(name, args) que toma el nombre de una herramienta y argumentos, encuentra la herramienta en los servidores conectados y la invoca.
- En lugar de darle al modelo cincuenta definiciones de herramientas por adelantado, el harness le dice al modelo: "Puedes llamar a list_available_tools() para ver qué puedes hacer, o a call_tool(name, args) para hacer algo concreto".

Ahora el modelo tiene dos metaherramientas: herramientas para descubrir y llamar a otras herramientas. Puede explorar el espacio de herramientas sin cargar todas las definiciones en el contexto al principio. Llama a list_available_tools() cuando necesita encontrar una herramienta, aprende qué hay disponible en ese momento y luego usa lo que necesita. El contexto residente se mantiene pequeño.

Esto cambia la carga anticipada por un descubrimiento perezoso. El modelo tiene que gastar un turno llamando a list_available_tools() antes de poder llamar a una herramienta concreta, así que hay un costo de latencia. Pero si el harness está conectado a cincuenta servidores, los tokens que se ahorran al no mantener cada definición de herramienta en el contexto superan el costo del turno extra.

### Cuándo usar cada enfoque

La carga anticipada (poner cada herramienta en el contexto al arrancar) funciona cuando:

- Tienes un conjunto pequeño y fijo de herramientas (de dos a diez).
- Las herramientas son relevantes para cada tarea del agente.
- El contexto no está restringido.

La carga perezosa (definir list_available_tools() y call_tool() y dejar que el modelo descubra lo que necesita) funciona cuando:

- Tienes muchas herramientas (decenas o más).
- Las herramientas son especializadas y no todas son relevantes para cada tarea.
- El contexto está restringido y cada token importa.
- El costo de latencia de un turno extra es aceptable.

El descubrimiento programático (presentar las herramientas como código que el modelo puede leer y ejecutar) combina ambas ideas: un contexto inicial pequeño (solo las funciones de descubrimiento) y la capacidad de explorar el espacio de herramientas sin cargar definiciones a mano.

## Práctica

1. ▢ Estás usando la API de Anthropic con tres servidores MCP. Cambias a la API de OpenAI. ¿Necesitas actualizar tus servidores MCP, tu harness o ambos?

<details markdown="1"><summary>Comprobación</summary>

Solo tu harness. Los servidores MCP no cambian; siguen exponiendo herramientas en formato MCP. Tu harness ya traducía las definiciones de MCP al formato de transmisión de Anthropic; ahora las traduce al formato de OpenAI. La capa de traducción cambia, pero los servidores y el protocolo no.

</details>

2. ▢ Tu agente está conectado a diez servidores MCP con un total de ciento cincuenta herramientas. Quieres usar la idea de "ejecución de código con MCP": definir list_available_tools() y dejar que el modelo descubra lo que necesita. ¿Cuáles son dos consecuencias de este diseño?

<details markdown="1"><summary>Pista</summary>

Piensa en el tamaño del contexto y en la latencia. ¿Cuándo pide el modelo la lista? ¿Qué cuesta eso?

</details>

<details markdown="1"><summary>Comprobación</summary>

El contexto es más pequeño porque no cargas ciento cincuenta definiciones de herramientas por adelantado, solo dos funciones y quizá una breve descripción de lo que hacen. La latencia aumenta porque el modelo tiene que llamar a list_available_tools() en un turno en el que quiere explorar, lo que añade al menos un turno extra antes de poder llamar a una herramienta concreta. Es un intercambio que vale la pena si el contexto es ajustado o si rara vez se necesitan todas las herramientas juntas.

</details>

3. ▢ Tu harness tiene solo tres herramientas, y todas son relevantes para cada tarea que realiza el agente. ¿Deberías usar carga anticipada, carga perezosa o descubrimiento programático?

    - a) Carga perezosa con list_available_tools()
    - b) Carga anticipada: poner las tres en el contexto al principio
    - c) Descubrimiento programático con funciones call_tool()
    - d) Rotar qué herramientas están en el contexto para ahorrar tokens

<details markdown="1"><summary>Comprobación</summary>

b) Con un conjunto pequeño de herramientas que siempre son relevantes, la carga anticipada es lo más simple y rápido. No desperdicias tokens en funciones de descubrimiento, no añades latencia y el modelo siempre tiene las herramientas que necesita. La carga perezosa y el descubrimiento programático añaden sobrecarga sin beneficio cuando el conjunto de herramientas es pequeño y universal. La opción d es un antipatrón: rotar herramientas dentro y fuera crea confusión y falta de determinismo.

</details>

4. ▢ Defines list_available_tools() para consultar todos los servidores MCP conectados y devolver los nombres y descripciones de sus herramientas. Cuando el modelo llama a esta función, ¿cuenta la llamada para tus tokens de API?

<details markdown="1"><summary>Comprobación</summary>

Sí. Llamar a list_available_tools() cuesta tokens igual que llamar a cualquier otra función: el modelo envía la llamada, el harness la ejecuta y el resultado vuelve en la transcripción. Estás cambiando los tokens gastados en definiciones de herramientas por adelantado por los tokens gastados en llamadas de descubrimiento. Con muchas herramientas, el intercambio suele ser positivo.

</details>

## Prácticas en el mundo real

- [ ] Dibuja un diagrama que muestre las dos capas: el protocolo MCP de un lado (harness a servidores externos), el formato de transmisión del proveedor del otro lado (harness a modelo). Etiqueta qué pasa si cambias de proveedor frente a si cambias de servidores MCP.
- [ ] Estima la diferencia de costo en tokens entre la carga anticipada (poner cien herramientas en el contexto) y la carga perezosa (list_available_tools() bajo demanda) para tu propio agente. ¿Tiene sentido la pereza?
- [ ] Mañana: Implementa una función list_available_tools() sencilla que consulte un servidor MCP real al que tengas acceso y devuelva un resumen que el modelo pueda leer.

## Para profundizar

- [Article: "Code Execution with MCP", Anthropic Engineering](https://www.anthropic.com/engineering/code-execution-with-mcp)
- [Specification: Model Context Protocol](https://modelcontextprotocol.io/specification)
- [Recursos](../RESOURCES.md)

---

¿No termina de quedar claro? Vuelve a leer la fuente primaria de arriba, ya que esta lección la comprime y en la compresión es donde se escapa la comprensión. Consulta el [glosario](../GLOSSARY.md) por si algún término te resultó resbaladizo.

Si lo poco claro es la propia lección y no el material, eso es un defecto: [abre un issue](https://github.com/TokenCemetery/teach/issues).
