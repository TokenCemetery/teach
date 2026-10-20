---
title: "17. Prompt caching y disposición del prompt"
description: Ordena un prompt con las partes estables primero para que el proveedor pueda cachear el prefijo
type: lesson
---

# Lección 17. Prompt caching y disposición del prompt

**Vínculo con la misión:** Una plantilla de prompt que pone primero su texto estable permite que el proveedor se salte su reprocesamiento en cada llamada, así que la disposición es una decisión de costo y latencia que se toma en la plantilla, no un detalle posterior.
**Fuente principal:** [Docs: "Prompt caching", Claude Platform Docs](https://platform.claude.com/docs/en/build-with-claude/prompt-caching)
**Requisitos previos:** [Lección 16](0016-versioning-prompts.md), [Prompt caching](../GLOSSARY.md)

## Calentamiento

1. ▢ La lección 13 explicó dónde van un documento largo y la pregunta en un mismo prompt. ¿Cuál va primero, y ese orden concuerda con poner primero el contenido estable para el caching?

<details markdown="1"><summary>Comprobación</summary>

Los documentos largos van primero y la pregunta al final. Concuerda: un documento reutilizado entre peticiones es estable, y la pregunta cambia cada vez, así que los dos objetivos apuntan en la misma dirección.

</details>

2. ▢ La plantilla de la lección 15 tiene texto fijo y huecos. ¿Cuál de los dos es candidato a prefijo cacheado y cuál nunca puede serlo?

<details markdown="1"><summary>Comprobación</summary>

El texto fijo es candidato, porque es idéntico en cada llamada. Los valores de los huecos cambian con cada petición, así que nada que contenga uno puede formar parte de un prefijo reutilizado.

</details>

## Qué debes saber

### Lo que se cachea es el prefijo

El **prompt caching** almacena el estado procesado de un prefijo de prompt para que una llamada posterior que comparta exactamente ese prefijo se salte su recálculo. La documentación de Anthropic describe su versión: el prefijo cacheado cubre toda la petición en un orden fijo, `tools`, luego `system`, luego `messages`, hasta el bloque marcado con `cache_control` inclusive. El hash que hay detrás de una entrada de caché es acumulativo, así que cambiar cualquier bloque situado en el bloque marcado o antes de él produce un hash distinto en la siguiente petición, y la entrada no coincide.

Otros proveedores implementan el caching de otra forma, así que revisa sus reglas. El principio, un prefijo exacto que se reutiliza, es lo que debes llevarte.

### La disposición se deduce de eso

Pon primero lo que nunca cambia y al final lo que cambia con cada petición: las definiciones de herramientas, luego el system prompt, luego los documentos largos y los ejemplos few-shot, y por último la pregunta de cada petición. La documentación dice que hay que colocar el contenido estático al principio y marcar el final de la parte reutilizable.

```python
def build_request(system: str, documents: str, question: str) -> dict:
    return {
        "system": system,
        "messages": [
            {
                "role": "user",
                "content": [
                    # stable: the end of this block is where a cache marker goes
                    {"type": "text", "text": documents},
                    # per request: after the marker, never part of the prefix
                    {"type": "text", "text": question},
                ],
            },
        ],
    }
```

Aquí `documents` se comparte entre llamadas y `question` no, así que el texto compartido va delante, y son bloques separados para que el marcador pueda quedar después de los documentos y antes de la pregunta. En la API de Anthropic ese marcador es un campo `cache_control` en el bloque de documentos, la otra parte de este esquema que es específica de un proveedor. El ejemplo de error que da la propia documentación es un bloque que contiene una marca de tiempo y el mensaje del usuario, con el marcador de caché puesto en él: el hash del prefijo incluye la marca de tiempo, así que cada petición escribe una entrada nueva y nunca lee ninguna. Mantén una marca de tiempo, un ID de petición o un nombre de usuario fuera de la parte estable. La solución de Anthropic es poner el marcador en el último bloque que es idéntico entre peticiones.

### Qué rompe un acierto y cuáles son los límites

- Un prefijo más corto que el mínimo del modelo no se cachea, y no se devuelve ningún error. El mínimo documentado depende del modelo y va de 512 a 4,096 tokens. Si `cache_creation_input_tokens` y `cache_read_input_tokens` en el uso de la respuesta valen ambos 0, el prompt no se cacheó.
- Cambiar las definiciones de herramientas invalida toda la caché. La tabla de invalidación de la documentación también enumera los cambios en el ajuste de elección de herramienta, las imágenes y algunos ajustes de thinking y esfuerzo, que invalidan la parte de los mensajes.
- La duración por defecto es de 5 minutos, y se renueva cada vez que se lee la entrada. Existe una opción de 1 hora con un costo adicional.
- Una entrada de caché solo está disponible después de que empieza la primera respuesta, así que las primeras peticiones en paralelo no la comparten. Para cargas concurrentes y de agentes, consulta la [lección 34 del track de agentes](../../agents/lessons/0034-prompt-caching-and-concurrency.md).

Las lecturas son más baratas que la entrada sin caché y las escrituras cuestan más: la documentación indica las escrituras de 5 minutos a 1.25 veces el precio base de entrada y las lecturas a 0.1 veces, con excepciones por modelo en las lecturas. Así que una disposición que nunca acierta cuesta un poco más que no usar caching en absoluto.

## Práctica

1. ▢ Una plantilla empieza con `Current time: {now}`, luego una guía de estilo de 3,000 tokens y luego la pregunta del usuario. ¿Por qué el caching nunca la ayuda y cuál es la solución?

<details markdown="1"><summary>Comprobación</summary>

La marca de tiempo es el primer bloque, así que el hash del prefijo cambia en cada petición y ningún bloque posterior puede leerse de la caché. Mueve la guía de estilo y cualquier otro texto fijo antes de la marca de tiempo, o elimina la marca de tiempo del prompt si la tarea no la necesita, y deja la pregunta al final.

</details>

2. ▢ Primera petición: `cache_read_input_tokens` es 0, `cache_creation_input_tokens` es 2,400, `input_tokens` es 60. Segunda petición, mismo prefijo, una pregunta de 75 tokens: ¿qué muestran los tres campos si el caching funcionó y cuál es la entrada total?

<details markdown="1"><summary>Pista</summary>

La documentación dice que `input_tokens` cuenta solo lo que viene después del último punto de corte de la caché.

</details>

<details markdown="1"><summary>Comprobación</summary>

`cache_read_input_tokens` es 2,400, `cache_creation_input_tokens` es 0 e `input_tokens` es 75. La entrada total es la suma, 2,475 tokens. El prefijo se leyó de la caché en lugar de escribirse de nuevo, y solo la pregunta nueva se procesó desde cero.

</details>

3. ▢ Un equipo añade un system prompt de 600 tokens en un modelo cuyo mínimo es de 1,024 tokens, lo marca para cachearlo y ve ambos contadores de uso en 0. ¿Qué pasó y hay algo roto?

<details markdown="1"><summary>Comprobación</summary>

El prompt está por debajo del mínimo, así que se procesó sin caching y no se devolvió ningún error. No hay nada roto. Añade más contenido estable, como ejemplos, para llegar al mínimo, o acepta las llamadas sin caché.

</details>

4. ▢ ¿Qué disposición del prompt es mejor para el caching de un bot de soporte que responde muchas preguntas sobre un único documento de políticas largo?

    - a) La pregunta, luego el documento de políticas, luego el system prompt
    - b) El system prompt, luego la pregunta, luego el documento de políticas
    - c) El system prompt, luego el documento de políticas, luego la pregunta
    - d) El system prompt, luego el nombre del usuario, luego el documento de políticas

<details markdown="1"><summary>Comprobación</summary>

**c)** El system prompt y el documento son idénticos entre peticiones y van primero, y la pregunta va al final. (a) y (b) ponen la pregunta, que cambia, delante del texto estable, así que el prefijo es distinto en cada llamada. (d) pone un valor por usuario delante del documento, lo que rompe el prefijo compartido para cada usuario distinto.

</details>

## Prácticas en el mundo real

- [ ] Toma un prompt que ejecutes y marca cada parte como estable, cambia a diario o cambia con cada petición, y luego comprueba que las partes estables queden primero.
- [ ] Haz una llamada dos veces con el mismo prefijo en un proveedor que informe del uso de la caché y lee los contadores de ambas llamadas.
- [ ] Mañana: busca cualquier marca de tiempo, ID o nombre dentro de la región estable de un prompt y muévelo al final.

## Para profundizar

- [Docs: "Prompt caching", Claude Platform Docs](https://platform.claude.com/docs/en/build-with-claude/prompt-caching)
- [Lección 34 del track de agentes: Prompt caching y concurrencia](../../agents/lessons/0034-prompt-caching-and-concurrency.md)
- [Prompts en producción](../reference/prompts-in-production.md)
- [Recursos](../RESOURCES.md)

---

¿No terminas de entenderlo? Vuelve a leer la fuente principal del principio, ya que esta lección la comprime y en la compresión es donde se escapa la comprensión. Consulta el [glosario](../GLOSSARY.md) para cualquier término que te haya resultado resbaladizo.

Si lo poco claro es la propia lección y no el material, eso es un defecto: [abre un issue](https://github.com/TokenCemetery/teach/issues).
