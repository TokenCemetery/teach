---
title: "3. El formato de transmisión de una llamada a herramienta"
description: "Qué aspecto tienen realmente una llamada a herramienta y su resultado en el protocolo entre tu harness y el proveedor del modelo"
type: lesson
---

# Lección 3. El formato de transmisión de una llamada a herramienta

**Vínculo con la misión:** Escribir el bucle del agente para una tarea dada, y nombrar qué hace cada mensaje de su contexto y qué termina el bucle.
**Fuente principal:** [Docs: "Tool use with Claude", Claude Platform Docs](https://platform.claude.com/docs/en/agents-and-tools/tool-use/overview)
**Requisitos previos:** [Lección 2](0002-agent-workflow-or-prompt.md), [Herramienta](../GLOSSARY.md)

## Calentamiento

1. ▢ ¿Cuál es la diferencia entre que un harness llame a un modelo y que un harness ejecute una herramienta?

<details markdown="1"><summary>Comprobación</summary>

El harness llama al modelo enviándole una petición (la transcripción más las herramientas) por la red a la API de un proveedor; el modelo corre dentro de la infraestructura del proveedor y devuelve una salida estructurada. Una herramienta se llama cuando el modelo la pide al emitir un bloque estructurado de llamada a herramienta; el harness la ejecuta, normalmente invocando una función del mismo código base o de la misma red.

</details>

2. ▢ ¿En qué caso podría el modelo enviar texto plano en lugar de una llamada a herramienta?

<details markdown="1"><summary>Comprobación</summary>

Cuando el modelo ha terminado la tarea en la que trabajaba y está listo para devolver una respuesta final al usuario, o cuando decide (dentro de los límites que fijaste) que no necesita llamar a una herramienta en este turno.

</details>

## Qué debes saber

### La llamada a herramienta en la red

Cuando envías una petición a un proveedor de modelos pidiéndole que use herramientas, la petición incluye tres cosas: el nombre del modelo, la lista de herramientas disponibles (con sus nombres, descripciones y esquemas de parámetros) y la transcripción de la conversación hasta ese momento.

Una definición de herramienta se ve así: un nombre, una descripción legible por personas y un JSON Schema que limita los parámetros que el modelo puede enviar. Aquí tienes una petición de Anthropic con una sola herramienta:

```json
{
  "model": "claude-sonnet-5",
  "max_tokens": 1024,
  "tools": [
    {
      "name": "get_weather",
      "description": "Get the current weather for a given city",
      "input_schema": {
        "type": "object",
        "properties": {
          "city": {"type": "string", "description": "The city name"}
        },
        "required": ["city"]
      }
    }
  ],
  "messages": [
    {"role": "user", "content": "What's the weather in Lisbon?"}
  ]
}
```

Cuando el modelo decide llamar a una herramienta, no la ejecuta. En su lugar, devuelve un bloque estructurado que describe qué herramienta llamar y qué argumentos pasar. El proveedor deja de enviar salida y lo señala con un campo `stop_reason`. Esta es la respuesta completa de Anthropic:

```json
{
  "id": "msg_01ABC",
  "type": "message",
  "role": "assistant",
  "content": [
    {"type": "text", "text": "I'll check that for you."},
    {
      "type": "tool_use",
      "id": "toolu_01XYZ",
      "name": "get_weather",
      "input": {"city": "Lisbon"}
    }
  ],
  "stop_reason": "tool_use"
}
```

Fíjate: el campo `input` ya es JSON analizado, no una cadena. Cada llamada a herramienta recibe un id único (aquí `toolu_01XYZ`) para que el harness pueda decirle al modelo qué resultado responde a qué llamada. El asistente también puede incluir texto plano antes o después del bloque de llamada a herramienta.

### De la red a la ejecución

Tu harness ve esta respuesta y sabe que debe ejecutar `get_weather` con el argumento `{"city": "Lisbon"}`. Cómo lo hagas depende de tu herramienta:

- Si es una **herramienta de cliente** (una función de tu propio código), la llamas directamente: `weather_result = get_weather(city="Lisbon")`.
- Si es una **herramienta de servidor** (algo que el proveedor ejecuta por ti, como una búsqueda web alojada), el proveedor ya la ejecutó antes de devolver la respuesta. Extraes el resultado de la respuesta.

### Devolver el resultado

Cuando el harness tiene un resultado (ya sea por ejecutar la función o por leer la respuesta del proveedor), lo envía de vuelta al modelo en un mensaje nuevo, etiquetado con el id de la llamada a herramienta. El formato de Anthropic lo anida dentro de un mensaje con rol `user`:

```json
{
  "role": "user",
  "content": [
    {
      "type": "tool_result",
      "tool_use_id": "toolu_01XYZ",
      "content": "18C, partly cloudy"
    }
  ]
}
```

Este mensaje entra en la transcripción como un turno nuevo. El modelo ahora tiene tanto la llamada a herramienta que hizo como el resultado, y decide qué hacer a continuación: llamar a otra herramienta, llamar a la misma herramienta con otros argumentos o devolver una respuesta final.

### El formato de transmisión de OpenAI (la diferencia)

La API de OpenAI usa los mismos conceptos pero con nombres de campos y formas distintos. En lugar de repetir todo el intercambio, esto es lo que cambia:

Los parámetros de la herramienta se anidan bajo `function.parameters` en lugar de un `input_schema` a secas. Los argumentos de la llamada a herramienta del modelo llegan como una cadena codificada en JSON en `function.arguments`, no como un objeto ya analizado, así que tu harness debe analizarla. La señal de parada es `finish_reason: "tool_calls"` en lugar de `stop_reason: "tool_use"`. El resultado vuelve como un mensaje dedicado `role: "tool"` que lleva el `tool_call_id`, no envuelto en un mensaje `user`. Aquí tienes un ejemplo abreviado con la misma tarea del clima:

```json
{
  "choices": [{
    "message": {
      "role": "assistant",
      "content": null,
      "tool_calls": [{
        "id": "call_abc123",
        "type": "function",
        "function": {"name": "get_weather", "arguments": "{\"city\": \"Lisbon\"}"}
      }]
    },
    "finish_reason": "tool_calls"
  }]
}
```

Seguido del resultado como un mensaje `role: "tool"`:

```json
{"role": "tool", "tool_call_id": "call_abc123", "content": "18C, partly cloudy"}
```

El patrón es idéntico: definición de herramienta, llamada a herramienta con id, resultado etiquetado con el mismo id. Los nombres y las formas difieren, pero cualquier harness que maneje uno puede adaptarse al otro mapeando estos campos.

## Práctica

1. ▢ En la respuesta de Anthropic mostrada arriba, ¿por qué el campo `input` contiene un objeto JSON analizado en lugar de una cadena JSON?

<details markdown="1"><summary>Comprobación</summary>

La API de Anthropic analiza los argumentos de la llamada a herramienta del lado del proveedor antes de devolverlos, lo que reduce trabajo al harness. Tu código recibe valores listos para usar, no una cadena que analizar. OpenAI envía los argumentos como cadena, así que debes llamar a `json.parse()` o equivalente en tu harness antes de usarlos.

</details>

2. ▢ Cuando envías de vuelta al modelo el resultado de la herramienta, ¿por qué incluye el campo `tool_use_id`?

<details markdown="1"><summary>Comprobación</summary>

El modelo puede haber pedido varias herramientas en un solo turno. El id le permite al modelo emparejar cada resultado con la llamada correspondiente que hizo, para saber qué respuesta vino de qué petición.

</details>

3. ▢ En el protocolo de Anthropic, un resultado de herramienta viaja dentro de un mensaje con rol `user`. En el de OpenAI, viaja como un mensaje `role: "tool"`. ¿Por qué esta diferencia no importa para la lógica del bucle del agente?

    - a) Porque el harness no necesita distinguirlos al construir la transcripción
    - b) Porque el modelo siempre los procesa igual sin importar el rol
    - c) Porque un protocolo está claramente mal y debería evitarse
    - d) Porque los resultados de herramientas no forman parte de la transcripción oficial

<details markdown="1"><summary>Comprobación</summary>

**b)** El modelo los procesa igual sin importar la etiqueta de rol ni la estructura del mensaje. La lógica es: aquí tienes un resultado de una llamada a herramienta que hiciste; ¿qué quieres hacer ahora? El detalle del protocolo (dentro de un mensaje de usuario o como mensaje de herramienta) no cambia esa lógica. (a) se acerca pero pierde el punto: el rol no importa para el bucle en sí.

</details>

4. ▢ Un harness recibe esta respuesta de OpenAI: `"arguments": "{\"city\": \"Paris\"}"`. ¿Cómo debe procesar el harness esto antes de pasárselo a la herramienta?

<details markdown="1"><summary>Comprobación</summary>

Analizarlo como JSON: `json.loads("{\"city\": \"Paris\"}") yields {"city": "Paris"}`. OpenAI devuelve una cadena, y el harness debe deserializarla a un diccionario (u objeto) antes de desempaquetar los argumentos en la llamada a la función.

</details>

## Prácticas en el mundo real

- [ ] Abre el código o la documentación de un framework de agentes real (LangChain, Vercel AI o el propio SDK de Python de Claude) y encuentra dónde envía una definición de herramienta al modelo. Identifica el nombre, la descripción y el esquema de parámetros. Marca de dónde sale cada uno en el código.
- [ ] Recorre un ciclo completo de llamada a herramienta en ese mismo código base: encuentra dónde analiza la respuesta de uso de herramienta del modelo, ejecuta la herramienta y envía el resultado de vuelta. Marca cómo se usa el id para emparejarlos.
- [ ] Mañana: escribe un harness mínimo (20 líneas o menos, vale pseudocódigo) que envíe una sola herramienta a un proveedor de modelos, analice la respuesta con la llamada a herramienta y envíe el resultado de vuelta. No uses un framework.

## Para profundizar

- [Docs: "Tool use with Claude", Claude Platform Docs](https://platform.claude.com/docs/en/agents-and-tools/tool-use/overview)
- [Guide: "Function calling", OpenAI](https://developers.openai.com/api/docs/guides/function-calling)
- [Recursos](../RESOURCES.md)

---

¿No termina de quedar claro? Vuelve a leer la fuente primaria de arriba, ya que esta lección la comprime y en la compresión es donde se escapa la comprensión. Consulta el [glosario](../GLOSSARY.md) por si algún término te resultó resbaladizo.

Si lo poco claro es la propia lección y no el material, eso es un defecto: [abre un issue](https://github.com/TokenCemetery/teach/issues).
