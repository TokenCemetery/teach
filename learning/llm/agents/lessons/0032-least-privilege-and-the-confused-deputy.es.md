---
title: "32. Mínimo privilegio y el delegado confundido"
description: "Cómo acotar las capacidades de un agente para que la inyección de prompt cause un daño contenido en lugar de una brecha catastrófica"
type: lesson
---

# Lección 32. Mínimo privilegio y el delegado confundido

**Vínculo con la misión:** Diseñar los límites de acceso de cada herramienta del agente para que el contenido no confiable pueda engañar al agente pero no pueda engañarlo para que use mal capacidades que nunca debió tener.
**Fuente principal:** [Reference: "OWASP Top 10 for LLM Applications", OWASP GenAI Security Project](https://genai.owasp.org/llm-top-10/)
**Requisitos previos:** [Lección 31](0031-prompt-injection-and-the-lethal-trifecta.md), [Sandbox](../GLOSSARY.md)

## Calentamiento

1. ▢ Nombra las tres condiciones de la tríada letal de la lección 31.

<details markdown="1"><summary>Comprobación</summary>

Acceso a datos privados, exposición a contenido no confiable y capacidad de comunicarse con el exterior. Quita cualquiera de ellas y el ataque falla.

</details>

2. ▢ En la lección 31 diseñaste una herramienta para evitar un ataque de inyección de prompt rompiendo una condición de la tríada. Si hubieras roto la condición de comunicación externa, describe cómo se vería eso en la práctica.

<details markdown="1"><summary>Comprobación</summary>

La herramienta o bien no podría enviar información a ningún sitio, o solo a un canal al que el atacante no pueda llegar. Por ejemplo, una herramienta draft_email que solo guarda los correos en local en lugar de enviarlos, o una herramienta que solo puede escribir en una tabla de preparación que requiere revisión manual antes de que se compartan los datos.

</details>

## Qué debes saber

### Mínimo privilegio: acota cada herramienta exactamente a lo que necesita

El mínimo privilegio es un principio de seguridad: cada herramienta debe tener acceso solo al recurso o acción específicos que realmente necesita, no a un acceso amplio "por si resulta útil más adelante". Para un agente, esto significa diseñar el límite de sandbox de cada herramienta con un permiso estrecho.

Ejemplos:

- Una herramienta que lee la agenda de hoy solo debería leer del archivo del calendario, no de todo el sistema de archivos
- Una herramienta que busca el pedido de un cliente solo debería consultar los pedidos de ese cliente, no todos los pedidos de la empresa
- Una herramienta que envía un correo de recibo solo debería poder enviar desde una dirección fija, no desde todo el buzón
- Una herramienta que edita un archivo de configuración solo debería editar ese archivo, no archivos arbitrarios del directorio de configuración

El principio se aplica también a las credenciales. Si una herramienta necesita autenticarse con un servicio externo, debería usar una credencial acotada a ese servicio y esa acción, no una cuenta de administrador amplia.

¿Por qué importa esto para los agentes? Porque el acceso amplio es justo lo que hace costoso un exploit para la organización. Cuando una inyección engaña a un agente para que llame a una herramienta a la que tiene acceso, las consecuencias dependen de a qué puede llegar realmente esa herramienta.

### El patrón del delegado confundido: autoridad legítima, mal usada

El delegado confundido (confused deputy) es un patrón de seguridad clásico, nombrado por primera vez en los años 80, que se aplica directamente a los agentes. Un delegado confundido es un programa que tiene autoridad legítima y amplia y al que se engaña para que use mal esa autoridad en favor de un atacante. El programa no está comprometido en el sentido de ejecutar código malicioso; está haciendo exactamente lo que permiten sus herramientas legítimas, solo que en nombre de instrucciones que nunca fueron del usuario.

Un agente con una vulnerabilidad de delegado confundido se ve así:

1. El agente tiene una herramienta amplia: send_email puede enviar desde cualquier dirección del buzón de la empresa
2. El agente lee contenido no confiable: una invitación de calendario con una instrucción inyectada
3. La instrucción le pide al agente que reenvíe un hilo de correo confidencial a una dirección externa
4. El agente llama a send_email con los parámetros del atacante
5. La herramienta ejecuta la llamada porque es una llamada legítima a send_email con parámetros válidos. La herramienta no sabe que la petición se originó en una inyección, no en la intención real del usuario.

El correo ahora está exfiltrado, no porque "hackearan" al modelo, sino porque le diste a un agente una capacidad amplia y no la acotaste a una tarea estrecha.

La solución no es insistir más en el prompt. La solución es diseñar la herramienta de forma estrecha: en lugar de send_email para todo el buzón, diseña una herramienta llamada send_receipt que solo pueda enviar a direcciones de correo de clientes con una plantilla fija. Ahora una inyección todavía puede engañar al modelo para que llame a send_receipt, pero esa llamada queda restringida a lo que send_receipt tiene permitido hacer.

### La cadena de suministro de MCP: la confianza es transitiva

Las lecciones 20 y 21 cubrieron el Model Context Protocol (MCP) y cómo un agente se conecta a servidores MCP para acceder a herramientas. Desde el ángulo de la seguridad, conectarse a un servidor MCP significa extender tu límite de confianza para incluir a quien opere ese servidor.

Un servidor MCP malicioso o comprometido puede:

- Tergiversar las descripciones de herramientas para que las llamadas dañinas suenen inocuas
- Devolver datos engañosos en los resultados de herramientas, sobre los que luego razonará el agente
- Observar cada llamada a herramienta que hace el agente y cada pieza de contexto que envía

Cuando tu harness se conecta a un servidor MCP de terceros, confías en el operador de ese servidor tanto como confías en tu propio código. Si el servidor está comprometido o lo opera un adversario, se convierte en otro canal de inyección.

La defensa es la misma que para cualquier riesgo de cadena de suministro: conéctate solo a servidores en los que confíes, y acota la conexión. Por ejemplo:

- No le des a un agente acceso a todos los servidores MCP disponibles; conéctalo solo a los servidores específicos que necesita
- Usa autenticación y cifrado en las conexiones MCP
- Audita las descripciones de herramientas que proporciona un servidor MCP y entiende qué acceso estás concediendo
- Asume que los datos que envías a una herramienta MCP podrían hacerse públicos o usarse mal

Los servidores MCP no son especialmente riesgosos; son solo otra herramienta. El principio es el mismo: acota el acceso.

### Juntándolo todo: límites de permisos por herramienta y por tarea

El principio de diseño que une estas lecciones es que un límite de permisos debe acotarse de forma deliberada, por herramienta y por tarea, en lugar de una única credencial amplia que comparte todo el agente.

Cuando diseñes un agente:

1. Lista cada herramienta que el agente necesita
2. Para cada herramienta, pregúntate: ¿cuál es el acceso mínimo que esta herramienta requiere para cumplir su propósito?
3. Crea un límite de sandbox para esa herramienta que conceda exactamente ese acceso, ni más
4. Si una herramienta necesita autenticarse (con una base de datos, una API, un sistema de archivos), crea una credencial acotada a esa herramienta y a ese nivel de acceso, no una credencial que pueda llegar a cualquier cosa

Una herramienta con un alcance estrecho es lo concreto que convierte "la inyección engañó al modelo" de un compromiso catastrófico en un error contenido y de baja consecuencia. El agente lee la inyección, el modelo la entiende, el modelo llama a la herramienta inyectada y la herramienta se niega a ejecutar la acción solicitada porque la acción queda fuera de su alcance.

## Práctica

1. ▢ Estás diseñando una herramienta para un agente que gestiona cuentas de usuario. La herramienta necesita actualizar la dirección de correo de un usuario en la base de datos de la empresa. Tu primer borrador le da esta credencial: una cuenta de base de datos con permiso UPDATE sobre toda la tabla de usuarios.

¿Por qué esto tiene un alcance excesivo, y cuál sería un mejor diseño?

<details markdown="1"><summary>Comprobación</summary>

La credencial concede permiso UPDATE sobre toda la tabla, lo que significa que la herramienta podría actualizar la información de cualquier usuario, no solo la dirección de correo concreta del usuario concreto que se está gestionando. Un mejor diseño crearía un procedimiento almacenado en la base de datos que acepte solo el ID de usuario y el correo nuevo, y concedería a la credencial de la herramienta permiso para ejecutar solo ese procedimiento. Así, aunque una inyección engañe al agente para que llame a la herramienta con parámetros inesperados, la base de datos se negará a ejecutar nada fuera del alcance del procedimiento.

</details>

2. ▢ Un agente tiene acceso a una herramienta send_email acotada para enviar solo desde `support@company.com` y solo a direcciones de correo que coincidan con el patrón `*@customer-*.com`. Una inyección intenta engañarlo para que envíe un mensaje a `attacker@evil.com`. ¿Qué detiene el ataque?

<details markdown="1"><summary>Pista</summary>

La propia herramienta impone el alcance. Piensa en dónde ocurre esta comprobación y por qué no interviene ninguna instrucción del prompt.

</details>

<details markdown="1"><summary>Comprobación</summary>

La validación de la herramienta, que corre en el harness antes de que se envíe el mensaje. La herramienta valida el destinatario contra su patrón permitido y se niega a enviar porque `attacker@evil.com` no coincide. La inyección logró cambiar el comportamiento del agente (el agente pretendía enviar), pero fracasó porque el límite de permisos de la herramienta impidió la acción dañina. Este es un control a nivel de herramienta, no a nivel de prompting, así que es fiable.

</details>

3. ▢ Tu organización ofrece un servidor MCP que expone eventos del calendario de la empresa. Descubres que una empresa de terceros ha construido un cliente MCP que se conecta a tu servidor para ayudar a gestionar reuniones. ¿Cuál de estas afirmaciones es cierta?

    - a) Esto es seguro siempre que tu servidor MCP solo devuelva datos públicos del calendario
    - b) El cliente de terceros ahora tiene en la práctica acceso de lectura a los datos del calendario que devuelve tu servidor
    - c) Deberías usar cifrado entre tu servidor y el cliente para garantizar que ni siquiera los operadores de tu servidor puedan ver los datos
    - d) La empresa de terceros no puede usar mal los datos porque son solo eventos del calendario, no credenciales de usuario

<details markdown="1"><summary>Comprobación</summary>

**b)** El cliente de terceros, y quien lo opere, puede ver y potencialmente usar mal todos los datos del calendario que devuelve el servidor. Los datos públicos siguen siendo datos; aunque los eventos del calendario no sean secretos, el operador de terceros ahora tiene visibilidad sobre la agenda de tu organización, lo que podría usarse para espionaje corporativo o ingeniería social. El cifrado (opción c) protegería los datos en tránsito, pero no impediría que el operador del cliente los viera. El alcance del acceso (público frente a privado) no cambia la implicación de seguridad: has extendido tu límite de confianza para incluir al operador de terceros. Este es el riesgo de la cadena de suministro de MCP.

</details>

4. ▢ Estás diseñando una herramienta para un agente que procesa tickets de atención al cliente. La herramienta necesita enviar una respuesta por correo a un cliente. Describe un diseño de mínimo privilegio que evitaría un ataque de delegado confundido en el que una inyección engaña al agente para que reenvíe a un cliente un hilo de correo interno confidencial.

<details markdown="1"><summary>Comprobación</summary>

En lugar de una herramienta genérica send_email, diseña una herramienta llamada send_support_response que tome solo dos parámetros: el ID del ticket y el texto de la respuesta. La herramienta busca la dirección de correo del cliente a partir del ID del ticket, valida que el texto de la respuesta no supere una longitud razonable y envía solo la respuesta (sin adjuntos, sin ningún otro correo). La credencial de la herramienta solo tiene permiso para enviar desde la dirección de soporte y solo a direcciones de correo de clientes vinculadas a tickets válidos. Ahora una inyección puede engañar al agente para que llame a send_support_response, pero la llamada queda restringida por el alcance de la herramienta. El agente no puede reenviar correos internos, no puede enviar a direcciones arbitrarias y no puede enviar nada que no sea una respuesta de soporte, porque la herramienta no ofrece una forma de hacer esas cosas.

</details>

## Prácticas en el mundo real

- [ ] Toma una herramienta que hayas diseñado o uses con frecuencia. Mapea sus permisos actuales. Anota un permiso que tenga y que exceda lo que estrictamente necesita para su propósito principal, y una forma de eliminarlo.
- [ ] Elige un servidor MCP al que estarías dispuesto a conectar un agente. Investiga o contacta con el operador y entiende: ¿qué datos ve el servidor, cómo se usan, cómo se protegen, quién tiene acceso a los logs? Anota tu nivel de confianza y cualquier riesgo residual.
- [ ] Mañana: Diseña una herramienta que implemente el mínimo privilegio de forma deliberada rechazando una petición plausible pero fuera de alcance. Escribe una especificación que nombre la petición que recibiría durante un ataque de delegado confundido y explique por qué el diseño de la herramienta impide que tenga éxito.

## Para profundizar

- [Reference: "OWASP Top 10 for LLM Applications", OWASP GenAI Security Project](https://genai.owasp.org/llm-top-10/)
- [Recursos](../RESOURCES.md)

---

¿No termina de quedar claro? Vuelve a leer la fuente primaria de arriba, ya que esta lección la comprime y en la compresión es donde se escapa la comprensión. Consulta el [glosario](../GLOSSARY.md) por si algún término te resultó resbaladizo.

Si lo poco claro es la propia lección y no el material, eso es un defecto: [abre un issue](https://github.com/TokenCemetery/teach/issues).
