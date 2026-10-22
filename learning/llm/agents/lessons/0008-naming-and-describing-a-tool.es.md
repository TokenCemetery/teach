---
title: "8. Nombrar y describir una herramienta"
description: "El nombre y la descripción de una herramienta es lo que lee el modelo para decidir cuándo y cómo llamarla"
type: lesson
---

# Lección 8. Nombrar y describir una herramienta

**Vínculo con la misión:** Diseñar la superficie de herramientas de un agente (nombres, descripciones, formas de retorno y el límite de permisos que decide qué puede hacer sin supervisión) empieza por entender que los nombres y las descripciones no son documentación de API para una persona: son superficie del prompt que el modelo lee para decidir cuándo y cómo llamar a una herramienta.
**Fuente principal:** [Article: "Writing Effective Tools for Agents", Anthropic Engineering](https://www.anthropic.com/engineering/writing-tools-for-agents)
**Requisitos previos:** [Lección 7](0007-the-transcript-as-state.md), [Herramienta](../GLOSSARY.md)

## Calentamiento

1. ▢ De la lección 7: ¿Cómo "recuerda" el modelo lo que pasó en un turno anterior del bucle del agente?

<details markdown="1"><summary>Comprobación</summary>

No recuerda por sí solo. El harness vuelve a enviar la transcripción completa en cada llamada, así que lo que parece memoria es en realidad el modelo volviendo a leer todo lo que se le mostró antes.

</details>

2. ▢ De la lección 7: ¿Por qué la transcripción es todo el estado del agente, y no alguna otra estructura de datos que el harness guarde por separado?

<details markdown="1"><summary>Comprobación</summary>

Porque el modelo solo ve la transcripción. Cualquier hecho que el harness conoce pero nunca añade a ella es invisible para el modelo, sin importar qué más siga el harness internamente.

</details>

## Qué debes saber

### Una descripción de herramienta no es documentación de API

Un error que todo el que construye comete una vez: escribir la descripción de una herramienta como escribirías el docstring de un endpoint REST.

```text
Bad:
name: fetch_user
description: Fetches user data
```

Esto es demasiado escueto para un modelo que decide entre varias herramientas. El modelo no tiene contexto para saber cuándo usar `fetch_user` frente a `get_user` frente a `lookup_user`. No sabe qué datos vuelven ni qué hay que pasar. No puede razonar si llamarla ahora o más tarde. Cuando el modelo ve tres herramientas y ninguna guía clara, adivina, y se equivoca más a menudo que una persona.

Aquí está la misma herramienta descrita para un modelo:

```text
Better:
name: fetch_user
description: Look up a user profile by their numeric ID. Returns the user's name, email, account status, and the current version number of their profile. Use this before calling update_user, since update_user requires you to pass the profile's current version number to prevent write conflicts. Returns null if the user ID does not exist.
```

Ahora el modelo ve el cuadro completo: cuándo llamarla (antes de update_user), qué necesita (un ID numérico) y qué devuelve (información suficiente para decidir el siguiente paso). Esta descripción sirve a la toma de decisiones del modelo, no a una persona que lee documentación de API.

La diferencia es esta: un docstring REST le dice a un programador humano cómo usar una herramienta. La descripción de una herramienta en el prompt de un agente le dice a un modelo cuándo y por qué llamarla, qué pasar y qué resultado esperar. El modelo no tiene un manual; tu descripción es su única guía.

### Nombrar de forma distinta a las demás herramientas

El modelo elige entre herramientas leyendo sus nombres y descripciones, sin ninguna otra señal. Si dos herramientas suenan parecido, el modelo llamará a la equivocada o llamará a ambas por si acaso.

```text
Bad:
- name: list_files
  description: Lists files in a directory
- name: list_file_contents
  description: Lists the contents of a file
```

El modelo podría confundirlas o llamar a ambas cuando solo necesita una. Los nombres están demasiado cerca.

```text
Better:
- name: list_directory
  description: List all files and subdirectories in a directory. Shows names and file sizes. Does not show file contents.
- name: read_file
  description: Read the complete contents of a single file. Returns text as a string.
```

Ahora los nombres son distintos (list_directory frente a read_file) y las descripciones dejan claro qué hace y qué no hace cada una. El modelo elegirá la correcta.

La regla: el nombre de una herramienta debe decir lo que hace de una forma que no se pueda confundir con ninguna otra herramienta del mismo conjunto. Si tienes varias herramientas de búsqueda, no las llames todas `search`. Llámalas `search_documentation`, `search_code`, `search_logs`.

### Las descripciones de parámetros importan igual

La descripción de la herramienta en el nivel superior se lleva la mayor atención, pero las descripciones de los parámetros son igual de importantes para la corrección.

```text
Bad:
name: create_issue
description: Creates a GitHub issue
parameters:
  - name: title
    type: string
    description: Issue title
  - name: body
    type: string
    description: Issue body
```

El modelo no sabe qué formato debe tener el título, cuánto puede medir, si debe ser una pregunta o una afirmación. El cuerpo es aún peor: ¿es Markdown? ¿Texto plano? ¿Con cuánto detalle? ¿El modelo describe el problema o la solución?

```text
Better:
name: create_issue
description: Create a new issue in the repository
parameters:
  - name: title
    type: string
    description: A one-line summary of the problem or feature request. Be specific and actionable. Examples: "Handle null config values in startup" or "Add support for JSON output format".
  - name: body
    type: string
    description: Detailed description in Markdown. Include what you tried, what failed, and what you expect to happen. If it is a feature request, explain why it matters. If it is a bug, include steps to reproduce.
```

Ahora el modelo sabe qué tipo de título escribir y qué nivel de detalle incluir en el cuerpo. Producirá mejores resultados.

### Un fallo común: herramientas parecidas que confunden al modelo

El peor caso es cuando dos herramientas son lo bastante parecidas como para que el modelo no pueda distinguirlas, incluso con descripciones.

```text
Very bad:
- name: update_user
  description: Update user information
- name: change_user
  description: Modify user data
```

Estos nombres y descripciones dicen casi lo mismo. El modelo podría llamar a ambas, llamar a la equivocada o perder tiempo preguntando. No le has dado ninguna forma de elegir.

La solución es hacer los nombres y las descripciones tan distintos que solo uno tenga sentido para la tarea en cuestión:

```text
Better:
- name: update_user_profile
  description: Change a user's displayed name, email, or profile picture. Requires the profile version number to prevent conflicts.
- name: update_user_permissions
  description: Grant or revoke access roles for a user, such as admin, editor, or viewer. Only callable by the current account's admin.
```

Ahora el modelo ve que la primera herramienta es para información personal y la segunda para control de acceso. Elegirá la correcta.

## Práctica

1. ▢ Tienes dos herramientas: `send_email` y `send_notification`. A veces el modelo llama a ambas cuando solo necesita una. Escribe una frase para cada herramienta que deje claro al modelo cuál usar y cuándo.

<details markdown="1"><summary>Comprobación</summary>

Respuestas posibles: `send_email` podría ser "Send an email message to an email address. Use this for messages longer than a few lines or when you need to include attachments or formatted text." `send_notification` podría ser "Send a brief in-app notification to a user. Use this for short status updates or alerts that do not require the user to leave the application." La clave es que la descripción le dice al modelo qué tipo de mensaje espera cada herramienta, para que pueda elegir bien.

</details>

2. ▢ Tu herramienta `get_user` devuelve todos los campos de un registro de usuario: id, nombre, correo, teléfono, dirección, empresa, biografía, preferencias, nivel de suscripción y diez más. La descripción de un parámetro debe guiar al modelo sobre qué pasar. ¿Qué NO deberías poner en la descripción?

<details markdown="1"><summary>Pista</summary>

Piensa en lo que el modelo necesita saber para llamar correctamente a la herramienta, frente a lo que es bueno saber pero no es necesario para la llamada en sí.

</details>

<details markdown="1"><summary>Comprobación</summary>

NO deberías listar cada campo que devuelve la herramienta. La descripción de la herramienta dice qué recibe el modelo de vuelta; la descripción del parámetro dice qué debe proporcionar el modelo para llamarla. Para un parámetro `user_id`, la descripción debería decir algo como "The numeric ID of the user. If you do not have the ID, call search_users first." No listes en la descripción del parámetro qué campos vuelven; eso va en la descripción de la herramienta en el nivel superior.

</details>

3. ▢ ¿Cuál de las siguientes es la mejor razón para escribir descripciones detalladas de los parámetros de una herramienta?

    - a) Cumplir con los estándares de documentación de API
    - b) Ayudar a los ingenieros que lean el código más tarde
    - c) Ayudar al modelo a decidir qué valor pasar y cuándo llamar a la herramienta
    - d) Reducir el número de llamadas a herramientas que el usuario necesita hacer

<details markdown="1"><summary>Comprobación</summary>

**c)** Ayudar al modelo a decidir qué valor pasar y cuándo llamar a la herramienta. El modelo lee las descripciones de los parámetros para entender qué argumentos espera una herramienta y qué pasará si pasa el valor equivocado. (a) es irrelevante; esto es ingeniería de prompts, no diseño de API. (b) puede ser un beneficio secundario, pero no es la razón principal. (d) pierde el punto: las descripciones detalladas ayudan al modelo a hacer menos llamadas erróneas, no menos llamadas en total.

</details>

4. ▢ Estás construyendo una herramienta llamada `search`. También tienes herramientas llamadas `search_documents`, `search_issues` y `search_users`. ¿Por qué este nombrado de herramientas es un problema, y qué deberías hacer en su lugar?

<details markdown="1"><summary>Comprobación</summary>

La herramienta `search` es demasiado genérica. El modelo no sabrá a qué herramienta de búsqueda llamar cuando necesite buscar. Podría llamar a todas, o elegir al azar. En su lugar, renombra `search` a algo específico como `search_logs` o `search_comments` o `search_code`. La regla es: cada nombre de herramienta debe ser lo bastante específico como para que el modelo sepa qué hace, y lo bastante distinto de los demás nombres de herramientas como para que el modelo no lo confunda.

</details>

## Prácticas en el mundo real

- [ ] Encuentra las definiciones de herramientas (nombre y descripción) de una aplicación con LLM o un framework de agentes que uses. Lee la descripción de cada herramienta. Anota una herramienta cuya descripción sea lo bastante clara como para que entiendas cuándo debería llamarla el modelo, y una cuya descripción sea demasiado vaga. Anota por qué funciona la primera y qué falta en la segunda.

- [ ] Elige una herramienta que uses con regularidad en la línea de comandos (como `grep` o `find`). Imagina que tuvieras que describirla para un modelo que no sabe nada de tu sistema de archivos. Escribe una descripción de una frase que le diga al modelo qué hace la herramienta y cuándo usarla en lugar de una herramienta parecida.

- [ ] Mañana: Toma la descripción de una herramienta de un agente real o de la documentación de una API que te parezca mal escrita. Reescríbela para un modelo que elige entre varias herramientas parecidas. Hazla al menos el doble de larga, incluye un ejemplo de cuándo usarla y di una cosa para la que NO sirve.

## Para profundizar

- [Article: "Writing Effective Tools for Agents", Anthropic Engineering](https://www.anthropic.com/engineering/writing-tools-for-agents)
- [Recursos](../RESOURCES.md)

---

¿No termina de quedar claro? Vuelve a leer la fuente primaria de arriba, ya que esta lección la comprime y en la compresión es donde se escapa la comprensión. Consulta el [glosario](../GLOSSARY.md) por si algún término te resultó resbaladizo.

Si lo poco claro es la propia lección y no el material, eso es un defecto: [abre un issue](https://github.com/TokenCemetery/teach/issues).
