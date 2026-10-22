---
title: "5. Llamadas en paralelo y errores como resultados"
description: "Cómo un modelo puede pedir varias herramientas a la vez, y por qué los errores de herramienta son resultados y no excepciones"
type: lesson
---

# Lección 5. Llamadas en paralelo y errores como resultados

**Vínculo con la misión:** Escribir el bucle del agente para una tarea dada, y nombrar qué hace cada mensaje de su contexto y qué termina el bucle.
**Fuente principal:** [Docs: "Tool use with Claude", Claude Platform Docs](https://platform.claude.com/docs/en/agents-and-tools/tool-use/overview)
**Requisitos previos:** [Lección 4](0004-schemas-and-who-executes.md)

## Calentamiento

1. ▢ En un solo turno del modelo, ¿puede el modelo pedir más de una llamada a herramienta al mismo tiempo?

<details markdown="1"><summary>Comprobación</summary>

Sí. El modelo puede emitir varios bloques de uso de herramienta en una respuesta, cada uno con un id único. El harness los ejecuta todos (posiblemente en paralelo) y reúne los resultados antes de enviarlos de vuelta como el siguiente mensaje.

</details>

2. ▢ Cuando una herramienta falla, ¿qué hace el harness: lanzar una excepción que tumba el bucle o devolver el error al modelo?

<details markdown="1"><summary>Comprobación</summary>

Devolver el error al modelo como resultado de herramienta. El bucle continúa; el modelo tiene la oportunidad de reintentar, usar otra herramienta o explicar el fallo.

</details>

## Qué debes saber

### Llamadas a herramientas en paralelo en un turno

El bucle del agente es enviar, ejecutar, añadir, repetir. Una sola respuesta del modelo puede incluir varias llamadas a herramientas:

```json
{
  "role": "assistant",
  "content": [
    {"type": "text", "text": "I'll gather that data for you."},
    {
      "type": "tool_use",
      "id": "toolu_01XYZ",
      "name": "get_weather",
      "input": {"city": "Lisbon"}
    },
    {
      "type": "tool_use",
      "id": "toolu_02ABC",
      "name": "get_weather",
      "input": {"city": "Madrid"}
    }
  ],
  "stop_reason": "tool_use"
}
```

Cada llamada tiene su propio id único. El modelo ha decidido: "necesito el clima de Lisboa y de Madrid". Tu harness ahora puede:

1. Ejecutar ambas herramientas en secuencia (una tras otra), o
2. Ejecutarlas en paralelo (ambas a la vez), según tu implementación.

La elección es tuya. Si son independientes y rápidas, el paralelo ahorra latencia. Si compiten por recursos o una depende de la otra, lo secuencial es más simple.

### Reunir los resultados antes del siguiente turno

Cuando todas las llamadas a herramientas terminan, el harness recoge los resultados y los envía de vuelta en un solo mensaje. Cada resultado está etiquetado con el id de la llamada a la que responde:

```json
{
  "role": "user",
  "content": [
    {
      "type": "tool_result",
      "tool_use_id": "toolu_01XYZ",
      "content": "18C, partly cloudy"
    },
    {
      "type": "tool_result",
      "tool_use_id": "toolu_02ABC",
      "content": "22C, sunny"
    }
  ]
}
```

El modelo ahora tiene ambos resultados, sabe cuál es cuál (por el id) y decide qué hacer a continuación. Esta es la clave: todos los resultados vuelven juntos en un mensaje, así que el modelo los procesa como un par.

### Tratar los errores como resultados

Cuando una herramienta falla, el harness no tumba el bucle. En su lugar, captura el error y se lo envía al modelo como un resultado, igual que un resultado exitoso. Un resultado de herramienta con error se ve así:

```json
{
  "type": "tool_result",
  "tool_use_id": "toolu_01XYZ",
  "content": "Error: city not found",
  "is_error": true
}
```

El campo `is_error` le dice al modelo que este resultado representa un fallo, no un éxito. El modelo lo lee y tiene que decidir: reintentar la misma herramienta con otra ciudad, probar otra herramienta o rendirse y explicarle el error al usuario.

### Por qué los errores son resultados y no excepciones

En muchos sistemas, una llamada a función fallida lanza una excepción y detiene la ejecución. En un bucle de agente, una llamada a herramienta fallida es solo información: datos devueltos al modelo. ¿Por qué este diseño?

Porque el modelo está al mando. El modelo llamó a la herramienta; debe decidir qué hacer si la herramienta falla. Quizá quiera reintentar. Quizá quiera usar otra herramienta. Quizá quiera pedirle más información al usuario. Una excepción le quitaría esa elección.

Esto no es ser indulgente con el código malo. Es una decisión de diseño: tratar al modelo como el orquestador, no como una función más de una pila de llamadas. El trabajo del harness es ejecutar lo que pide el modelo, recoger el resultado (éxito o fallo) y devolvérselo para que el modelo lo interprete.

### Los errores vienen de muchos lugares

Una llamada a herramienta puede fallar por muchas razones:

- El código de la herramienta de cliente lanzó una excepción (base de datos caída, entrada inválida, tiempo agotado).
- Una herramienta de servidor se ejecutó pero devolvió un error (límite de tasa de la API, archivo no encontrado, permiso denegado).
- El propio harness rechazó la llamada (falló la validación del esquema, falta un campo obligatorio).
- Falló la red (proveedor inaccesible, conexión caída).

Todo esto se convierte en resultados de herramienta que llevan mensajes de error, no en caídas.

## Práctica

1. ▢ Un modelo hace dos llamadas a herramientas en un turno: una tiene éxito y otra falla. ¿Cómo envía el harness ambos resultados de vuelta al modelo?

<details markdown="1"><summary>Comprobación</summary>

En un solo mensaje con rol de usuario con dos bloques tool_result, cada uno etiquetado con el id de la llamada correspondiente. Un resultado tiene `is_error: true` o un mensaje de error; el otro lleva los datos del éxito. El modelo recibe ambos en un turno y decide qué hacer a continuación.

</details>

2. ▢ Tienes una herramienta que busca en una base de datos. El modelo la llama con una búsqueda que agota el tiempo. ¿Qué debe hacer tu harness?

<details markdown="1"><summary>Pista</summary>

Piensa en a quién le toca manejar el tiempo agotado y qué necesita saber el modelo.

</details>

<details markdown="1"><summary>Comprobación</summary>

Capturar el tiempo agotado, recoger el mensaje de error (por ejemplo "Error: search timed out after 30s") y enviárselo al modelo como resultado de herramienta con `is_error: true`. Entonces el modelo decide: reintentar con una consulta más simple, probar otra herramienta o rendirse. El bucle no se cae.

</details>

3. ▢ El modelo hace tres llamadas a herramientas en paralelo. El harness debe:

    - a) Ejecutarlas una tras otra para poder parar pronto si una falla
    - b) Ejecutarlas en paralelo y esperar todos los resultados antes de enviarlos de vuelta
    - c) Devolver de inmediato los resultados exitosos y enviar los fallidos más tarde
    - d) Cancelar las llamadas restantes en cuanto una falle

<details markdown="1"><summary>Comprobación</summary>

**b)** Ejecutarlas en paralelo y esperar todos los resultados. El modelo pidió tres cosas; debe recibir tres resultados (éxito o fallo). Parar pronto (a) o cancelar (d) impide que el modelo sepa qué pasó. Devolver resultados en momentos distintos (c) rompe el protocolo: los resultados vuelven juntos en un solo mensaje.

</details>

4. ▢ Escribes una herramienta de cliente que multiplica dos números. Un modelo la llama con `x=5, y="hello"`. El harness intenta ejecutarla y la función lanza un error de tipo. ¿Cuál es el siguiente paso del harness?

<details markdown="1"><summary>Comprobación</summary>

Capturar la excepción, dar formato al error (por ejemplo "Error: cannot multiply number by string") y enviárselo al modelo como resultado de herramienta. El modelo ahora sabe que la llamada falló y puede reintentar con entradas válidas o probar otro enfoque. El bucle continúa.

</details>

## Prácticas en el mundo real

- [ ] Escribe o encuentra un agente que haga llamadas a herramientas en paralelo. Recorre una ejecución en la que el modelo pida dos herramientas a la vez. Verifica que ambos resultados vuelven juntos en un mensaje y llevan cada uno su propio id.
- [ ] Haz fallar una herramienta a propósito (llama a una base de datos caída, provoca un error de validación o envíale a una herramienta una entrada inválida). Observa cómo el harness da formato al error y se lo envía al modelo. Mira qué hace el modelo después.
- [ ] Mañana: escribe un harness que ejecute llamadas a herramientas en paralelo (usa hilos, async o el modelo de concurrencia de tu lenguaje) y recoja los resultados. Verifica que envía todos los resultados de vuelta en un mensaje incluso si algunas herramientas fallan.

## Para profundizar

- [Docs: "Tool use with Claude", Claude Platform Docs](https://platform.claude.com/docs/en/agents-and-tools/tool-use/overview)
- [Recursos](../RESOURCES.md)

---

¿No termina de quedar claro? Vuelve a leer la fuente primaria de arriba, ya que esta lección la comprime y en la compresión es donde se escapa la comprensión. Consulta el [glosario](../GLOSSARY.md) por si algún término te resultó resbaladizo.

Si lo poco claro es la propia lección y no el material, eso es un defecto: [abre un issue](https://github.com/TokenCemetery/teach/issues).
