---
title: "9. Formas de retorno y exceso de herramientas"
description: "El valor de retorno de una herramienta consume presupuesto de contexto, y demasiadas herramientas perjudican la capacidad del modelo de elegir bien"
type: lesson
---

# Lección 9. Formas de retorno y exceso de herramientas

**Vínculo con la misión:** Diseñar la superficie de herramientas de un agente incluye elegir qué devuelve una herramienta (su forma de retorno) y decidir cuántas herramientas ofrecer, porque ambas son decisiones de diseño que afectan a la capacidad del modelo de decidir bien entre sus opciones y al costo de cada turno que sigue.
**Fuente principal:** [Article: "Writing Effective Tools for Agents", Anthropic Engineering](https://www.anthropic.com/engineering/writing-tools-for-agents)
**Requisitos previos:** [Lección 8](0008-naming-and-describing-a-tool.md)

## Calentamiento

1. ▢ De la lección 8: ¿Por qué la descripción de una herramienta debe decirle al modelo cuándo y cómo usarla en lugar de solo listar qué parámetros acepta?

<details markdown="1"><summary>Comprobación</summary>

Porque el modelo no tiene otra fuente de guía para elegir entre herramientas. Una lista de parámetros a secas explica cómo llamar a una herramienta pero no por qué ni cuándo recurrir a ella, que es la decisión real que el modelo tiene que tomar.

</details>

2. ▢ De la lección 8: ¿Qué problema creas si tienes dos herramientas en el mismo conjunto con nombres y descripciones muy parecidos?

<details markdown="1"><summary>Comprobación</summary>

El modelo no puede distinguirlas de forma fiable, así que puede llamar a la equivocada o llamar a ambas por si acaso. El ruido también degrada la capacidad del modelo de elegir bien entre todas las demás herramientas del conjunto, no solo entre las dos que se parecen.

</details>

## Qué debes saber

### El valor de retorno de una herramienta consume presupuesto de contexto

Cada mensaje de la transcripción consume tokens. Cuando una herramienta devuelve un resultado, ese resultado se añade a la transcripción, y el modelo lo ve en cada turno posterior hasta que termina la ejecución o se trunca la transcripción. Una herramienta que devuelve una respuesta pequeña y enfocada cuesta poco. Una herramienta que devuelve cinco mil filas de una base de datos cuesta tokens reales en cada turno durante el resto de la ejecución, las necesitara o no el modelo.

```text
Bad:
Tool: fetch_user_records
Returns: [complete User record, complete User record, ...]
# 5000 rows, 50KB of JSON, ~10,000 tokens consumed per turn after this call
```

Después de que la herramienta devuelve, la transcripción se infla. El modelo ahora tiene que procesar las cinco mil filas en el siguiente turno solo para leer su propio contexto. Esto infla el presupuesto de tokens y ralentiza el bucle.

### Diseña las formas de retorno para decidir, no para ser completas

En lugar de devolver todo lo que tiene el sistema subyacente, diseña una forma de retorno que le dé al modelo lo que necesita para decidir el siguiente paso.

```text
Better: Option 1 - Return a summary
Tool: fetch_user_records
Returns:
  total_count: 5000
  sample_results: [User, User, User, ...] # top 5 results
  query_was_too_broad: true
  suggestion: "Your query matches 5000 users. Narrow it with a company_id or email domain filter."

# ~500 tokens consumed per turn after this call
```

El modelo ahora puede ver que la consulta era demasiado amplia y sabe qué hacer a continuación: puede volver a llamar a la herramienta con mejores filtros. Esto devuelve una décima parte de los tokens del volcado completo.

```text
Better: Option 2 - Let the model ask for more
Tool: fetch_user_records
Returns:
  count: 50  # number of results returned
  total_matching: 5000  # number of results if the query was not limited
  results: [User, User, ...] # just the first 50
  next_page_token: "abc123xyz"

# Model sees it got 50 of 5000. It can decide to refine the query or ask for the next page.
```

En ambos casos, el modelo obtiene información suficiente para tomar una decisión informada sin quedar enterrado en datos.

### Exceso de herramientas: más herramientas significa peores elecciones

Añadir una herramienta a un agente no es gratis. Cada herramienta entre las que el modelo puede elegir hace la elección más difícil para el modelo. A esto se le llama exceso de herramientas.

Con tres herramientas, el modelo elige bien la mayoría de las veces:

```text
Tools:
- search_documentation
- read_file
- list_directory
```

Con diez herramientas, el modelo empieza a dudar de sí mismo, llamando a varias herramientas cuando una bastaría:

```text
Tools:
- search_documentation
- search_issues
- search_code
- read_file
- read_logs
- list_directory
- list_repos
- get_git_history
- get_git_diff
- get_git_status
```

Cada herramienta nueva añade ruido a la decisión. El modelo tiene que leer y considerar las diez descripciones antes de elegir una. Si dos se parecen (search_code y search_documentation), el modelo podría llamar a ambas. El efecto es discreto: todas las herramientas existentes sufren un poco, no solo la nueva.

El costo es real: más llamadas a herramientas, más tokens en la transcripción, más turnos desperdiciados en información redundante.

### Añadir una herramienta nueva frente a añadir un parámetro

Cuando te tiente añadir una herramienta, primero pregúntate: ¿podría ser un parámetro de una herramienta existente?

```text
Bad: Two tools
- name: list_files
- name: list_directories
```

Mejor: una herramienta con un parámetro

```text
Good: One tool with a parameter
- name: list_contents
  parameters:
    - name: path
    - name: type
      type: enum
      values: [files, directories, all]
```

El modelo elige el tipo que quiere, y no has añadido ruido al conjunto de herramientas.

Pero a veces tiene sentido una herramienta nueva. Si las herramientas son fundamentalmente distintas (se llaman en situaciones diferentes, devuelven formas distintas, requieren permisos distintos), entonces una herramienta nueva con un nombre claro es mejor que un parámetro sobrecargado:

```text
Good: Two specialized tools
- name: search_database_by_id
  parameters:
    - id
    # Fast, returns a single record
- name: search_database_by_query
  parameters:
    - query
    # Might return many records
```

El modelo conoce la diferencia: by_id es rápida y precisa, by_query es flexible pero podría devolver mucho. Los nombres dejan clara la decisión.

La regla: añade una herramienta nueva cuando se llamaría por razones fundamentalmente distintas, o cuando no puedes expresar la distinción con parámetros. Añade un parámetro cuando la herramienta es básicamente la misma operación con una variación en el formato de entrada o de salida.

### Observar el exceso de herramientas en la práctica

Una señal sutil es cuando el modelo empieza a decir cosas como "debería llamar primero a search para ver si existe, y luego a fetch si existe" cuando una herramienta podría haber hecho todo el trabajo. Es el modelo intentando ir a lo seguro porque no confía en lo que hace cada herramienta. El problema no es el modelo; es el conjunto de herramientas.

Otra señal son las llamadas repetidas a herramientas: el modelo llama a la misma herramienta varias veces en una sola ejecución, como buscar dos veces o listar dos veces. Esto suele significar que el conjunto de herramientas no le da al modelo una forma de acotar los resultados en una llamada, así que tiene que llamar a la herramienta con distintos parámetros para encontrar lo que necesita.

## Práctica

1. ▢ Una herramienta llamada `get_user_history` devuelve un arreglo JSON con 100.000 eventos de acciones de usuario del último mes, cada uno detallado. Probablemente el modelo llamará a esta herramienta, mirará los primeros diez eventos e ignorará el resto. ¿Qué cambio de diseño reduce el costo en tokens en cada turno posterior a esta llamada?

<details markdown="1"><summary>Comprobación</summary>

Limitar el retorno a los primeros N eventos (por ejemplo, los primeros 20) e incluir un total_count y una forma de que el modelo pida más. Así el modelo puede ver lo que necesita sin pagar por los 100.000 eventos. Como alternativa, devolver un resumen: "50 events in the past week, 50 in the week before. Most recent: user logged in" en lugar del detalle completo, y dejar que el modelo pida lo específico si lo necesita.

</details>

2. ▢ Tienes un conjunto de herramientas con 15 herramientas. El modelo llama a search_by_name y a search_by_id en la misma ejecución aunque podría expresar ambas búsquedas como parámetros de una sola herramienta. ¿Cuál es el daño de haberlas mantenido como dos herramientas separadas?

<details markdown="1"><summary>Pista</summary>

Piensa en el trabajo del modelo: tiene que leer quince descripciones y decidir a qué herramienta llamar. ¿Cómo hace ese trabajo más difícil tener herramientas parecidas?

</details>

<details markdown="1"><summary>Comprobación</summary>

Exceso de herramientas. El modelo tiene que elegir entre quince herramientas. Herramientas parecidas como search_by_name y search_by_id hacen la elección más difícil. El modelo podría llamar a ambas cuando una bastaría, o perder tiempo decidiendo cuál es la apropiada. Todas las herramientas existentes sufren un poco porque el conjunto se volvió más ruidoso. La solución es fusionarlas en una sola herramienta de búsqueda con un parámetro para el campo de búsqueda.

</details>

3. ▢ ¿Cuál de las siguientes es una señal de que la forma de retorno de una herramienta es demasiado verbosa?

    - a) La herramienta se llama con mucha frecuencia
    - b) El modelo lee el resultado y pide un resumen antes de usarlo
    - c) La herramienta tarda mucho en ejecutarse
    - d) La herramienta requiere autenticación

<details markdown="1"><summary>Comprobación</summary>

**b)** El modelo lee el resultado y pide un resumen antes de usarlo. Esto significa que la herramienta devuelve demasiada información; el modelo tiene que filtrar o resumir lo que recibió antes de poder tomar una decisión. (a) no está relacionada con la forma de retorno; una herramienta que se llama con frecuencia puede ser estrecha por diseño. (c) trata de la velocidad de ejecución, no de tokens. (d) trata de permisos, no de la forma de retorno.

</details>

4. ▢ Estás diseñando herramientas para un agente de búsqueda de código. ¿`search_code` y `get_code_diff` deberían ser una herramienta o dos? Explica en una o dos frases.

<details markdown="1"><summary>Comprobación</summary>

Dos herramientas separadas. Se llaman por razones distintas (search busca archivos que coinciden con un patrón, diff muestra cambios entre versiones), devuelven formas distintas (una lista de archivos frente a un diff estructurado) y resuelven problemas distintos. Una sola herramienta sobrecargada haría más difícil la elección del modelo. Si fueran variaciones de la misma operación (como search_code con distintos parámetros de consulta), podrían ser una sola herramienta con un parámetro.

</details>

## Prácticas en el mundo real

- [ ] Encuentra un conjunto de herramientas en una aplicación con LLM o un agente al que tengas acceso. Cuenta las herramientas. Lee la trayectoria del modelo y marca cada turno en el que el modelo llamó a una herramienta. Estima: ¿llamó alguna vez el modelo a dos herramientas parecidas cuando una habría hecho el trabajo? Escribe una frase sobre si el conjunto de herramientas se sentía inflado o bien diseñado.

- [ ] Elige una herramienta que devuelva datos estructurados. Lee un valor de retorno de ejemplo. ¿Hay alguna parte del retorno que el modelo probablemente ignoraría? Reescribe la forma de retorno para excluir esos datos o moverlos a una segunda llamada, estimando cuántos tokens ahorraste.

- [ ] Mañana: Diseña una herramienta que podría ir en cualquier dirección (una herramienta nueva o un parámetro de una existente). Para tu elección, escribe dos frases sobre por qué elegiste una herramienta separada o un parámetro, qué costaría la alternativa y cuándo podrías reconsiderarlo.

## Para profundizar

- [Article: "Writing Effective Tools for Agents", Anthropic Engineering](https://www.anthropic.com/engineering/writing-tools-for-agents)
- [Recursos](../RESOURCES.md)

---

¿No termina de quedar claro? Vuelve a leer la fuente primaria de arriba, ya que esta lección la comprime y en la compresión es donde se escapa la comprensión. Consulta el [glosario](../GLOSSARY.md) por si algún término te resultó resbaladizo.

Si lo poco claro es la propia lección y no el material, eso es un defecto: [abre un issue](https://github.com/TokenCemetery/teach/issues).
