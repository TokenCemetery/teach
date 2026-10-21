---
title: "20. MCP: herramientas, recursos y prompts"
description: "Model Context Protocol como interfaz estandarizada para que los harness de agentes descubran e invoquen herramientas externas, lean datos y usen plantillas"
type: lesson
---

# Lección 20. MCP: herramientas, recursos y prompts

**Vínculo con la misión:** Entender MCP como un protocolo neutral respecto al proveedor que resuelve el problema de integración, para poder razonar sobre a qué herramientas puede acceder un agente y cómo añadir otras nuevas sin reescribir el harness.
**Fuente principal:** [Specification: Model Context Protocol](https://modelcontextprotocol.io/specification)
**Requisitos previos:** [Lección 19](0019-coordination-cost.md), [Herramienta](../GLOSSARY.md)

## Calentamiento

1. ▢ En la lección 3 aprendiste que una herramienta tiene un nombre, una descripción y un esquema de parámetros. Cuando corre tu harness, ¿de dónde saca esas definiciones: del modelo, del código del harness o de otro lugar?

<details markdown="1"><summary>Comprobación</summary>

Del código del harness. Quien escribe el harness redacta las definiciones de las herramientas a mano o las carga desde un archivo de configuración, y luego le habla al modelo de ellas antes de que empiece el bucle.

</details>

2. ▢ Cuando conectas un agente a una nueva fuente de datos (una base de datos, una API, un almacén de archivos), ¿quién hace el trabajo: el modelo, el harness o ambos?

<details markdown="1"><summary>Comprobación</summary>

Ambos. Quien escribe el harness redacta el código para integrar la fuente de datos (obtenerla, analizarla, manejar los errores), y luego le habla al modelo de ella añadiendo una definición de herramienta. El modelo decide si la llama y cuándo.

</details>

## Qué debes saber

### El problema de M por N

Sin un estándar compartido, conectar un harness de agente con herramientas y fuentes de datos externas requiere trabajo de integración a medida. Si tu harness puede invocar N herramientas o fuentes de datos distintas, y hay M equipos o frameworks distintos que construyen agentes, obtienes M*N integraciones separadas: cada equipo escribe código ad hoc para hablar con cada herramienta o fuente de datos.

MCP (Model Context Protocol) resuelve esto creando una interfaz compartida que pueden implementar tanto el lado del harness como el lado de la herramienta. Una herramienta o fuente de datos implementa un servidor MCP. Cualquier harness compatible con MCP puede conectarse a él. Un harness implementa un cliente MCP. Cualquier servidor compatible con MCP puede exponerle capacidades. Ahora tienes M+N integraciones en lugar de M*N.

Esto importa porque sin ello, escalar un agente para que use más herramientas significa un crecimiento cuadrático del código a medida. Con MCP, escalar significa construir o conectarse a más servidores estándar.

### Tres primitivas

MCP define tres tipos de capacidades que un servidor puede exponer a un cliente:

**Herramientas** (comparables a las herramientas de la lección 3): acciones que el modelo puede invocar. Una herramienta tiene un nombre, una descripción y un esquema de entrada. Cuando el modelo decide llamarla, el cliente envía la petición al servidor, que ejecuta la acción y devuelve un resultado. El modelo ve el resultado y continúa. Esto es exactamente como las herramientas de cliente y de servidor que ya conoces, pero la interfaz está estandarizada para que cualquiera de los dos lados pueda sustituirse.

**Recursos**: datos que el cliente MCP puede leer directamente sin que el modelo los invoque como una llamada a herramienta. Un recurso podría ser un archivo, un registro de base de datos, una página web o una respuesta de una API en vivo. El cliente puede listar los recursos disponibles y traer uno por su nombre. Esto es distinto de una herramienta porque el modelo no lo invoca; el harness lo lee y decide si poner los datos en el contexto o qué hacer con ellos. Los recursos permiten al harness incorporar información relevante sin bloquear el turno del modelo ni añadir la sobrecarga de una llamada a herramienta.

**Prompts** (plantillas de prompt): plantillas de prompt reutilizables que un servidor MCP expone para que un cliente las rellene y las use. Una plantilla de prompt podría ser "analiza este código en busca de problemas de seguridad" o "resume este documento". El cliente puede listar las plantillas de prompt disponibles, traer una por su nombre y rellenar los parámetros. Esto es distinto de las herramientas y los recursos: en lugar de ejecutar una acción o traer datos, el harness usa la plantilla para construir un mensaje que enviar al modelo, incrustándolo en las propias instrucciones o pasos de razonamiento del agente.

### Ciclo de vida básico

Un cliente se conecta a un servidor. Negocian las capacidades: cuáles de herramientas, recursos y prompts admite realmente este servidor concreto. El servidor anuncia lo que tiene; el cliente decide qué usar.

Luego, según lo que admita el cliente y lo que necesite el harness:

- El cliente puede listar las herramientas disponibles y traer sus esquemas, y luego presentárselos al modelo.
- El cliente puede listar los recursos disponibles y traer datos de forma proactiva, usando lo que aprende para informar las decisiones del agente.
- El cliente puede listar las plantillas de prompt disponibles y usarlas para construir instrucciones o pasos de reflexión.

Un solo servidor puede exponer las tres, o solo una o dos. El protocolo es simétrico: tanto el cliente como el servidor conocen la interfaz, así que cualquiera de los lados puede ser genérico.

### Transportes

Los servidores MCP pueden correr en local (mediante stdio, un canal simple de proceso a tubería entre el harness y el servidor en la misma máquina) o en remoto (mediante un transporte basado en HTTP, donde el servidor corre en otra máquina o servicio en la nube). El transporte afecta a la latencia, al despliegue y a los modos de fallo, pero no al protocolo en sí. Un harness que admite ambos transportes puede conectarse a un servidor MCP que corre en local para iterar rápido y a un servidor MCP remoto para tener resiliencia o colaboración entre equipos.

## Práctica

1. ▢ Estás construyendo un agente que necesita leer de una base de datos y llamar a una API web. La base de datos de tu equipo tiene un servidor MCP. La API web no. ¿Tienes que escribir código de integración a medida para ambas, o solo para una?

<details markdown="1"><summary>Comprobación</summary>

Solo para una. El harness puede conectarse al servidor MCP de la base de datos sin código a medida. Para la API web, tu equipo todavía escribe un envoltorio (ya sea en el harness o como un nuevo servidor MCP alrededor de la API). Este es el principio M+N: el servidor MCP hizo la mitad del trabajo por ti.

</details>

2. ▢ Tu agente necesita consultar el clima y luego decidir si sugerir una actividad al aire libre. ¿Debería ser esto una herramienta (que invoca el modelo) o un recurso (que lee el harness de forma proactiva)?

<details markdown="1"><summary>Pista</summary>

Piensa en cuándo se entera el harness del clima y cuándo necesita saberlo el modelo. ¿Decide el modelo si preguntar, o el harness siempre lo trae?

</details>

<details markdown="1"><summary>Comprobación</summary>

Depende. Si el clima siempre es relevante para la decisión, conviértelo en un recurso: el harness lo trae antes de cada turno y lo incluye en el contexto. Si el clima solo es relevante cuando el modelo está considerando actividades al aire libre, conviértelo en una herramienta: el modelo lo pide cuando lo necesita. Una herramienta deja que el modelo decida cuándo mirar; un recurso alimenta información que el harness siempre quiere que tenga el modelo.

</details>

3. ▢ Tu agente usa tres servidores MCP: uno para el correo, uno para un calendario y uno para un almacén de documentos. El servidor de correo admite herramientas y recursos. El servidor de calendario admite solo herramientas. El servidor de documentos admite herramientas, recursos y prompts. ¿Cuál de las siguientes cosas puede hacer el harness?

    - a) Usar recursos de los tres servidores, ya que los tres admiten al menos herramientas
    - b) Usar herramientas de los tres, recursos solo del correo y los documentos, y prompts solo de los documentos
    - c) Usar prompts de los tres servidores
    - d) Usar herramientas y recursos de todos los servidores por igual

<details markdown="1"><summary>Comprobación</summary>

b) El harness solo puede usar lo que cada servidor realmente expone. El correo admite herramientas y recursos, así que el harness puede usar ambos del correo. El calendario admite solo herramientas. Los documentos admiten herramientas, recursos y prompts. El harness negocia la capacidad por servidor y solo llama a lo que se anuncia. Los prompts solo están disponibles en el servidor de documentos, así que c es incorrecta. No todos los servidores admiten recursos, así que a y d son incorrectas.

</details>

4. ▢ Estás decidiendo si desplegar un servidor MCP en local (stdio) o en remoto (HTTP). ¿Qué compromiso deberías considerar?

<details markdown="1"><summary>Comprobación</summary>

Local (stdio) es más rápido y más simple de configurar en la misma máquina, pero acopla el harness al proceso del servidor. Remoto (HTTP) significa que el servidor puede correr en cualquier sitio y sobrevivir a las caídas del harness, pero añade latencia de red y modos de fallo (el servidor podría ser lento o inalcanzable). Ninguno cambia el protocolo MCP en sí; ambos funcionan igual para el cliente. Elige según cuánta latencia puedes tolerar y si necesitas resiliencia o acceso entre máquinas.

</details>

## Prácticas en el mundo real

- [ ] Lee la especificación de Model Context Protocol en modelcontextprotocol.io e identifica un servidor MCP que ya exista para algo de tu ámbito (correo, documentos, bases de datos, repositorios de código).
- [ ] Esboza la comparación M*N frente a M+N para tu propio trabajo: lista los M harness o equipos y las N herramientas o fuentes de datos que te importan, y luego estima cuánto código de integración a medida ahorraría el enfoque M+N.
- [ ] Mañana: Prueba a conectarte a un servidor MCP existente (mediante un cliente que lo admita) y observa cómo se usan en la práctica las tres primitivas (herramientas, recursos, prompts).

## Para profundizar

- [Specification: Model Context Protocol](https://modelcontextprotocol.io/specification)
- [Recursos](../RESOURCES.md)

---

¿No termina de quedar claro? Vuelve a leer la fuente primaria de arriba, ya que esta lección la comprime y en la compresión es donde se escapa la comprensión. Consulta el [glosario](../GLOSSARY.md) por si algún término te resultó resbaladizo.

Si lo poco claro es la propia lección y no el material, eso es un defecto: [abre un issue](https://github.com/TokenCemetery/teach/issues).
