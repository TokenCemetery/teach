---
title: "18. Un conjunto de regresión para un prompt"
description: Construye el pequeño conjunto de casos que un cambio de prompt no debe romper, a partir de fallos reales
type: lesson
---

# Lección 18. Un conjunto de regresión para un prompt

**Vínculo con la misión:** Un cambio de prompt es una afirmación, y un conjunto de regresión es lo que permite comprobar esa afirmación en segundos en lugar de juzgarla por las tres salidas que casualmente leíste.
**Fuente principal:** [Artículo: "Your AI Product Needs Evals", Hamel Husain](https://hamel.dev/blog/posts/evals/)
**Requisitos previos:** [Lección 17](0017-prompt-caching-and-layout.md), [Conjunto de regresión](../GLOSSARY.md)

## Calentamiento

1. ▢ La lección 11 pidió una salida estructurada y luego la validó. ¿Por qué una comprobación de validez es una primera aserción natural en un conjunto de regresión?

<details markdown="1"><summary>Comprobación</summary>

Pedir un formato no es una garantía, así que la salida puede fallar al analizarse. Una comprobación de parseo o de esquema es barata, no requiere juicio y se ejecuta en cada caso, lo que la convierte en una aserción fácil de escribir.

</details>

2. ▢ La lección 5 mostró que una edición de formato sin significado puede cambiar la precisión. ¿Qué implica eso sobre cuánto de un cambio de prompt puedes juzgar leyendo unas pocas salidas?

<details markdown="1"><summary>Comprobación</summary>

Muy poco. Una edición pequeña puede desplazar los resultados de maneras que un puñado de salidas no mostrará, así que el cambio hay que ejecutarlo sobre un conjunto fijo de casos y contarlo.

</details>

## Qué debes saber

### Empieza por los fallos que ya has visto

Un **conjunto de regresión** es un conjunto fijo de entradas, cada una con una comprobación sobre la salida, que un cambio de prompt no debe romper. Los mejores primeros casos son los reales. El relato de Hamel Husain sobre cómo construyó evals para un asistente inmobiliario dice que, cuando no se te ocurren aserciones, hay que mirar con ojo crítico las trazas y los modos de fallo, y que los cientos de pruebas unitarias del equipo se actualizaban continuamente a partir de los fallos nuevos observados en los datos. Una traza es una conversación registrada, así que regístralas, léelas y convierte cada fallo en un caso: la entrada que lo provocó y una comprobación que lo habría detectado.

La guía de Anthropic sobre cómo construir evaluaciones coincide en el objetivo: diseña pruebas que reflejen la distribución real de tu tarea, incluye casos límite y automatiza la calificación donde puedas. No necesitas tráfico de producción para empezar. Hamel señala que puedes escribir suposiciones fundamentadas, o hacer que un modelo genere entradas, y dejar que los primeros usuarios las refinen.

### Una aserción por propiedad

Hamel describe las comprobaciones como aserciones, como las que escribirías en pytest, rápidas y baratas para poder ejecutarlas en cada cambio. Cada caso enumera las propiedades que debe tener su salida.

```python
CASES = [
    {"id": "refund-not-complaint", "ticket": "I want my money back for order 118.",
     "must_contain": ["refund"], "must_not_contain": ["complaint"]},
    {"id": "no-uuid", "ticket": "Account 3f2b8c1e-9d4a-4e7b-a1c2-5d6e7f8a9b0c is locked.",
     "must_contain": [], "must_not_contain": ["3f2b8c1e"]},
]


def run_case(case: dict, call_model) -> bool:
    output = call_model(case["ticket"]).lower()
    has_all = all(s in output for s in case["must_contain"])
    has_none = not any(s in output for s in case["must_not_contain"])
    return has_all and has_none


def run_set(call_model) -> dict:
    return {c["id"]: run_case(c, call_model) for c in CASES}
```

`call_model` renderiza la plantilla de la lección 15, llama al modelo fijado de la lección 16 y devuelve su texto. El ejemplo propio de Hamel es una comprobación similar de que la salida nunca exponga un UUID interno. Cuando una propiedad no puede ser una prueba de cadena o de expresión regular, un modelo puede calificarla, y el track de evals explica cuándo confiar en ese calificador.

### Pequeño, creciente y sin el todo o nada

Empieza con el puñado de fallos que tienes delante y añade un caso cada vez que aparezca un fallo nuevo. El conjunto debe ser representativo de los fallos que te importan, no grande por serlo: la guía de Anthropic prefiere el volumen a la calidad calificada a mano, y el equipo de Hamel llegó a cientos de pruebas, así que lo pequeño es el punto de partida, no una meta. Dos advertencias de Hamel: un buen conjunto contiene casos con los que el modelo tiene dificultades, y a diferencia de las pruebas unitarias normales no necesariamente necesitas una tasa de aciertos del 100%, porque la tasa de aciertos es una decisión de producto sobre qué fallos toleras. Registra los resultados frente a la versión del prompt para ver si estás progresando.

## Práctica

1. ▢ Un usuario informa de que el resumidor llama "complaint" a una solicitud de reembolso. Convierte ese informe en un caso: ¿qué va en la entrada y qué aserciones necesita la salida?

<details markdown="1"><summary>Comprobación</summary>

La entrada es el texto real del ticket del usuario, o uno parecido. Las aserciones son `must_contain` la palabra refund y `must_not_contain` la palabra complaint, como en el caso `refund-not-complaint` de arriba. El caso ahora falla con el prompt antiguo y pasa con la corrección.

</details>

2. ▢ Predice el resultado de `run_case` para el caso `no-uuid` cuando el modelo produce `Account 3f2b8c1e is locked.`

<details markdown="1"><summary>Pista</summary>

Compara la salida con la única cadena de `must_not_contain`.

</details>

<details markdown="1"><summary>Comprobación</summary>

Devuelve `False`. `must_contain` está vacío, así que `has_all` es verdadero, pero la salida incluye `3f2b8c1e`, así que `has_none` es falso y el caso falla. El prompt filtró parte del ID.

</details>

3. ▢ Un compañero quiere esperar a tener 500 casos con calidad de producción antes de construir un conjunto de regresión. ¿Qué tiene de malo eso, según las fuentes de esta lección?

<details markdown="1"><summary>Comprobación</summary>

Hasta entonces no se ejecuta nada, así que los cambios mientras tanto se juzgan por intuición. Las fuentes describen conjuntos que crecieron a partir de fallos observados, y Hamel dice que puedes empezar con suposiciones fundamentadas. Empieza con los fallos que tengas y añade casos a medida que aparezcan otros nuevos.

</details>

4. ▢ Un conjunto de regresión pasa 18 de 20 casos con el prompt actual y el equipo insiste en 20 de 20 antes de cualquier lanzamiento. ¿Qué postura coincide con el artículo de Hamel?

    - a) La tasa de aciertos es una decisión de producto sobre los fallos tolerados, así que no se requiere el 100%
    - b) Todos los casos deben pasar o el conjunto no sirve como barrera antes de publicar
    - c) Los dos casos que fallan deberían eliminarse para que el conjunto refleje el prompt actual
    - d) La tasa de aciertos importa menos que el número de casos, que siempre debería minimizarse

<details markdown="1"><summary>Comprobación</summary>

**a)** Hamel dice que no necesariamente necesitas una tasa de aciertos del 100% y que depende de los fallos que vayas a tolerar. (b) es el hábito normal de las pruebas unitarias con el que él lo contrasta. (c) elimina los fallos que el conjunto existe para recordar. (d) es al revés: el conjunto es pequeño solo como punto de partida.

</details>

## Prácticas en el mundo real

- [ ] Reúne cinco fallos reales o realistas de un prompt que ejecutes, a partir de logs, informes de errores o tus propias pruebas, y escribe cada uno como una entrada más una aserción.
- [ ] Guarda los cinco casos en un archivo del repositorio junto al prompt y ejecútalos contra el prompt actual, anotando cuáles pasan.
- [ ] Mañana: la próxima vez que el prompt dé una mala salida, añádela como caso antes de corregir el prompt, y confirma que primero falla.

## Para profundizar

- [Artículo: "Your AI Product Needs Evals", Hamel Husain](https://hamel.dev/blog/posts/evals/)
- [Docs: "Define success criteria and build evaluations", Claude Platform Docs](https://platform.claude.com/docs/en/test-and-evaluate/develop-tests)
- [Prompts en producción](../reference/prompts-in-production.md)
- [Recursos](../RESOURCES.md)

---

¿No terminas de entenderlo? Vuelve a leer la fuente principal del principio, ya que esta lección la comprime y en la compresión es donde se escapa la comprensión. Consulta el [glosario](../GLOSSARY.md) para cualquier término que te haya resultado resbaladizo.

Si lo poco claro es la propia lección y no el material, eso es un defecto: [abre un issue](https://github.com/TokenCemetery/teach/issues).
