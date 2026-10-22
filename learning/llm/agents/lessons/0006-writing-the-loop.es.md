---
title: "6. Escribir el bucle"
description: "Construir el bucle del agente a partir de pseudocódigo y elegir las condiciones de parada de forma deliberada"
type: lesson
---

# Lección 6. Escribir el bucle

**Vínculo con la misión:** Escribir el bucle del agente es la habilidad central para construir un agente tú mismo, y sirve directamente a la misión de "escribir el bucle del agente para una tarea dada, y nombrar qué hace cada mensaje de su contexto y qué termina el bucle".
**Fuente principal:** [Article: "Building Effective Agents", Anthropic Engineering](https://www.anthropic.com/engineering/building-effective-agents)
**Requisitos previos:** [Lección 5](0005-parallel-calls-and-errors-as-results.md), [Bucle del agente](../GLOSSARY.md)

## Calentamiento

1. ▢ De la lección 5: ¿Qué se añade a la transcripción cuando falla una llamada a herramienta?

<details markdown="1"><summary>Comprobación</summary>

Un resultado de herramienta con error, etiquetado con el id de la llamada fallida y marcado como error, añadido igual que se añadiría un resultado exitoso. El bucle no se cae; el modelo ve el fallo como un turno normal.

</details>

2. ▢ De la lección 5: ¿Por qué es seguro que un modelo pida dos herramientas en paralelo en lugar de una tras otra?

<details markdown="1"><summary>Comprobación</summary>

Porque cada llamada a herramienta recibe su propio id único, y el harness devuelve cada resultado etiquetado con ese mismo id. El modelo siempre puede emparejar un resultado con la llamada que lo produjo, sin importar el orden de ejecución.

</details>

## Qué debes saber

### El bucle del agente como código

En esencia, un bucle de agente es simple. Aquí está como pseudocódigo:

```text
function run_agent(model, tools, transcript, max_turns):
    for turn_count in range(max_turns):
        response = call_model(model, transcript)
        transcript.append(response)

        if response.has_no_tool_calls():
            return response.text

        for tool_call in response.tool_calls:
            result = execute_tool(tools, tool_call)
            transcript.append(result)

    return "Max turns reached"
```

Este es el harness. El modelo elige qué herramienta pedir y cuándo dejar de pedir. El harness impone los límites y la mecánica.

Fíjate en la estructura: **llamar al modelo, añadir la respuesta, comprobar si hemos terminado, y si no, ejecutar las herramientas y añadir sus resultados, y volver al principio**. En cada turno la transcripción crece. Nada se guarda en memoria fuera de la transcripción.

### Por qué la transcripción debe crecer en cada turno

A veces los principiantes construyen un bucle que se ve así:

```text
function run_agent_wrong(model, tools, transcript, max_turns):
    for turn_count in range(max_turns):
        response = call_model(model, transcript)

        if response.has_no_tool_calls():
            return response.text

        for tool_call in response.tool_calls:
            result = execute_tool(tools, tool_call)
            transcript.append(result)  # Only append results, not the model's request
```

Esto es un error. Si no añades la respuesta con la llamada a herramienta del modelo a la transcripción antes de ejecutar la herramienta, el modelo no "recordará" haber pedido la herramienta en el siguiente turno. Cuando el harness vuelva a llamar al modelo, la transcripción no dice "el modelo pidió búsqueda" ni "el modelo pidió calculadora". El modelo podría pedir la misma herramienta otra vez, confundido. En la literatura esto se llama olvidar la petición. La transcripción se vuelve incoherente.

La solución es añadir la respuesta **inmediatamente** después de llamar al modelo, antes de hacer cualquier otra cosa:

```text
function run_agent_correct(model, tools, transcript, max_turns):
    for turn_count in range(max_turns):
        response = call_model(model, transcript)
        transcript.append(response)  # Append right away

        if response.has_no_tool_calls():
            return response.text

        for tool_call in response.tool_calls:
            result = execute_tool(tools, tool_call)
            transcript.append(result)
```

Ahora, cuando el bucle se repite y llama otra vez al modelo, la transcripción incluye "el modelo dijo que llamaría a search", y el modelo puede razonar sobre el resultado.

### Condiciones de parada: elegirlas de forma deliberada

Un bucle de agente necesita detenerse. Hay varios sitios donde elegir:

**Máximo de turnos**: El bucle externo cuenta los turnos y sale si la cuenta supera un límite. Es una protección de seguridad. Sin ella, un modelo o una herramienta defectuosos podrían correr para siempre.

**Sin llamadas a herramientas**: La respuesta del modelo no contiene llamadas a herramientas. Es la parada del "camino feliz": el modelo ha decidido responder. Comprueba esto después de añadir la respuesta del modelo.

**Herramienta de parada explícita**: Puedes ofrecer una herramienta llamada `stop` o `finish` que el modelo puede llamar para salir de forma explícita. El harness lo comprueba y retorna. Es útil si la tarea es abierta y el modelo necesita una acción explícita de "he terminado". Si ofreces esta herramienta, documéntala con claridad para que el modelo entienda cuándo usarla.

**Protección por conteo de errores**: Si una llamada a herramienta falla, el harness añade el error como resultado. Si fallan demasiadas llamadas seguidas, el harness se detiene y devuelve una trayectoria de error en lugar de continuar para siempre. Esto evita los bucles de reintentos.

No son mutuamente excluyentes. Un harness de producción podría comprobarlas todas:

```text
function run_agent_with_guards(model, tools, transcript, max_turns, max_errors):
    error_count = 0

    for turn_count in range(max_turns):
        response = call_model(model, transcript)
        transcript.append(response)

        if response.has_no_tool_calls():
            return response.text

        if response.has_explicit_stop_tool_call():
            return response.text

        for tool_call in response.tool_calls:
            result = execute_tool(tools, tool_call)

            if result.is_error():
                error_count += 1
                if error_count > max_errors:
                    return "Too many errors"
            else:
                error_count = 0

            transcript.append(result)

    return "Max turns reached"
```

La idea es que estas decisiones deben ser visibles en tu código, no estar ocultas ni ser accidentales. Tú eliges cuándo parar, y eliges cuántas oportunidades tiene el agente de recuperarse.

## Práctica

1. ▢ En el bucle en pseudocódigo mostrado arriba, ¿por qué `transcript.append(response)` debe ocurrir antes de la comprobación `if response.has_no_tool_calls()`?

<details markdown="1"><summary>Comprobación</summary>

La transcripción debe incluir la respuesta del modelo para que los turnos posteriores (o un observador que lea la trayectoria) puedan ver qué dijo y decidió el modelo. Si compruebas la parada antes de añadir, devuelves el texto del modelo, pero la transcripción nunca muestra que el modelo respondió. Además, se perdería otra información de la respuesta (como qué herramientas consideró el modelo pero decidió no llamar).

</details>

2. ▢ Un modelo llama a una herramienta y el harness la ejecuta con éxito y devuelve un resultado. El resultado se añade a la transcripción. En la siguiente iteración del bucle, el harness vuelve a llamar al modelo. ¿Qué ve el modelo en la transcripción que no veía en el turno anterior?

<details markdown="1"><summary>Pista</summary>

Piensa en qué se añadió en la iteración anterior del bucle, justo después de llamar al modelo por primera vez.

</details>

<details markdown="1"><summary>Comprobación</summary>

El modelo ve su propia respuesta con la llamada a herramienta, añadida antes de que el bucle ejecutara la herramienta. En el segundo turno, la transcripción incluye tanto esa respuesta como el resultado de la herramienta. Si la respuesta no se hubiera añadido primero, el modelo solo vería el resultado, como si la herramienta la hubiera llamado algo distinto del modelo.

</details>

3. ▢ Estás construyendo un harness con una protección de máximo de errores: si fallan tres llamadas a herramientas seguidas, detén el bucle. ¿Cuándo necesitas reiniciar a cero el contador de errores?

    - a) Cuando se alcanza el máximo de turnos
    - b) Cuando una llamada a herramienta tiene éxito y devuelve un resultado sin error
    - c) Cuando empieza el bucle
    - d) Cuando la respuesta del modelo no contiene llamadas a herramientas

<details markdown="1"><summary>Comprobación</summary>

**b)** Cuando una llamada a herramienta tiene éxito. La protección sirve para detectar un patrón de fallos repetidos. Si una herramienta falla y la siguiente tiene éxito, el bucle de reintentos se rompió y quieres permitir más fallos. Si reinicias solo al comienzo (c), nunca podrías parar; si reinicias al llegar al máximo de turnos o cuando no hay llamadas a herramientas (a, d), la protección no funciona. Reiniciar tras un éxito es el patrón: un éxito reinicia el contador.

</details>

4. ▢ Tu modelo debe buscar, leer un documento y luego resumirlo. En el tercer turno, pide otra vez la misma herramienta de búsqueda. La búsqueda tuvo éxito la primera vez. ¿Cuál es el error más probable en tu harness, dado lo que sabes sobre cómo funcionan las transcripciones?

<details markdown="1"><summary>Comprobación</summary>

El harness no está añadiendo a la transcripción la respuesta con la llamada a herramienta del modelo después de llamar al modelo. El modelo nunca ve su propia petición de la herramienta de búsqueda del primer turno. Cuando se le llama en el tercer turno, la transcripción muestra el resultado de la búsqueda pero no la petición, así que el modelo no sabe por qué está ahí el resultado y vuelve a pedir la búsqueda. La solución es añadir la respuesta inmediatamente después de llamar al modelo, antes de ejecutar la herramienta.

</details>

## Prácticas en el mundo real

- [ ] Escribe de memoria el pseudocódigo del bucle básico del agente sin mirar la lección. Compáralo con el pseudocódigo mostrado en "El bucle del agente como código". Comprueba: ¿añades la respuesta antes de comprobar que no hay llamadas a herramientas?

- [ ] Encuentra una implementación de agente en cualquier proyecto de código abierto (una biblioteca que uses o un repositorio público). Lee el código del bucle. Identifica dónde se construye la transcripción y dónde se comprueba la condición de parada. Anota si las condiciones de parada son explícitas (visibles en un if) o están ocultas (en una condición enterrada en una llamada a otra función).

- [ ] Mañana: Esboza en pseudocódigo las cuatro condiciones de parada (máximo de turnos, sin llamadas a herramientas, parada explícita, protección por conteo de errores). Para cada una, escribe una frase sobre por qué importa: ¿qué problema resuelve?

## Para profundizar

- [Article: "Building Effective Agents", Anthropic Engineering](https://www.anthropic.com/engineering/building-effective-agents)
- [Recursos](../RESOURCES.md)

---

¿No termina de quedar claro? Vuelve a leer la fuente primaria de arriba, ya que esta lección la comprime y en la compresión es donde se escapa la comprensión. Consulta el [glosario](../GLOSSARY.md) por si algún término te resultó resbaladizo.

Si lo poco claro es la propia lección y no el material, eso es un defecto: [abre un issue](https://github.com/TokenCemetery/teach/issues).
