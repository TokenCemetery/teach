---
title: "22. Sandboxing y puertas de aprobación"
description: "Límites de ejecución y puntos de control humanos que protegen frente a los errores del modelo"
type: lesson
---

# Lección 22. Sandboxing y puertas de aprobación

**Vínculo con la misión:** Para decidir qué puede hacer el agente sin supervisión, necesitas entender los dos mecanismos complementarios que protegen frente a los errores: los sandboxes imponen a qué puede llegar el código sin importar lo que pida el modelo, y las puertas de aprobación añaden un punto de control humano antes de las acciones de alto riesgo.
**Fuente principal:** [Article: "Building Effective Agents", Anthropic Engineering](https://www.anthropic.com/engineering/building-effective-agents)
**Requisitos previos:** [Lección 21](0021-provider-formats-and-discovery-at-scale.md), [Harness](../GLOSSARY.md)

## Calentamiento

1. ▢ ¿Cuál es la diferencia entre una herramienta de cliente y una herramienta de servidor, en cuanto a dónde corre el código y quién lo controla?

<details markdown="1"><summary>Comprobación</summary>

Una herramienta de cliente corre en el propio código del harness, así que controlas su ejecución por completo. Una herramienta de servidor corre en la infraestructura del proveedor por cuenta del harness, así que el proveedor controla el límite de ejecución. Esto importa para la seguridad porque el comportamiento de una herramienta de cliente depende de tu código, mientras que el comportamiento de una herramienta de servidor depende de lo que permita el proveedor.

</details>

2. ▢ En la lección 21 aprendimos que, en lugar de precargar cada definición de herramienta en el contexto, el modelo puede descubrir y llamar herramientas de forma dinámica. Nombra un beneficio de este enfoque y un costo que introduce.

<details markdown="1"><summary>Comprobación</summary>

Beneficio: el contexto del modelo no explota con cientos de definiciones de herramientas, así que puede razonar con más claridad y las definiciones de herramientas pueden mantenerse pequeñas o traerse bajo demanda. Costo: el modelo ahora tiene que llamar primero a una herramienta de descubrimiento o de introspección antes de saber qué hay disponible, lo que añade un viaje de ida y vuelta, o llama a una herramienta que supone que existe y falla si no, lo que requiere manejo de errores y reintentos.

</details>

## Qué debes saber

### El criterio de un modelo no es un límite de seguridad

Podrías esperar: "El modelo será inteligente con lo que haga con el acceso que le doy. Puedo confiar en que el modelo decida no borrar datos de producción ni enviar correos sin permiso".

Esta esperanza se rompe de varias maneras. Un modelo puede equivocarse: puede malentender las consecuencias de una llamada a herramienta. Un modelo puede ser manipulado por el contenido que lee: si la vista previa de un archivo o un mensaje de usuario contiene texto adversario diseñado para engañar al modelo, ese texto puede influir en su razonamiento. Un modelo puede simplemente cometer un error: el razonamiento puede fallar a escala, sobre todo en escenarios de mucha ramificación o bajo presión de tiempo. Por estas razones, lo que tu harness realmente permite que toque una herramienta (qué archivos del disco, qué hosts de red, qué comandos ejecutar) tiene que imponerse con código, no esperando que el modelo se comporte correctamente.

Por eso el harness, no el modelo, es el límite de seguridad.

### Qué es un sandbox

Un sandbox es un límite de ejecución que el harness impone sobre lo que el código de una herramienta puede alcanzar, sin importar qué argumentos envió el modelo. Las instrucciones del modelo nunca son en sí una propiedad de seguridad.

Los límites habituales de un sandbox incluyen:

- **Límite del sistema de archivos**: La herramienta solo puede leer o escribir archivos dentro de un árbol de directorios específico (por ejemplo, `/home/user/work` pero no `/etc` ni `/home/other_user`). Aunque el modelo le pida a la herramienta acceder a una ruta fuera de este árbol, el sandbox la rechaza en tiempo de ejecución.
- **Aislamiento de red**: La herramienta no tiene acceso a la red en absoluto, o solo puede llegar a una lista de permitidos con hosts específicos. El modelo no puede convencer al harness de que le deje llegar a dominios arbitrarios.
- **Límites de recursos**: El tiempo de CPU, la memoria y el tiempo real tienen un tope. Si el código del modelo se queda atascado en un bucle infinito, el sandbox lo termina en lugar de consumir todos los recursos.
- **Aislamiento de procesos**: La herramienta corre en un proceso o contenedor separado con privilegios reducidos, así que no puede afectar al harness ni acceder a recursos del sistema que no se le concedieron de forma explícita.

La idea clave es que estos límites se imponen en tiempo de ejecución, en el código del harness, no a nivel del lenguaje. Una herramienta no puede escapar de un sandbox escribiendo código ingenioso. El sandbox es la regla que aplica el harness, no una función que la herramienta respete.

### Qué es una puerta de aprobación

Una puerta de aprobación es un mecanismo complementario: antes de ejecutar una llamada a herramienta de una categoría riesgosa, el harness hace una pausa y espera a que una persona revise la llamada concreta y la apruebe o la rechace.

Las puertas de aprobación se aplican a acciones con estas propiedades:

- Irreversibles o difíciles de deshacer: borrar archivos, enviar correos, hacer transacciones financieras, publicar en internet.
- De alta consecuencia si salen mal: lo que está en juego es dinero real, daño real o exposición real de la privacidad.
- Realmente difíciles de predecir: la decisión del modelo es razonable pero no obviamente correcta, así que vale la pena añadir criterio humano.

Una puerta pausa el bucle del agente y muestra a una persona la llamada a herramienta pendiente (con sus argumentos y el efecto esperado), espera la aprobación o el rechazo y luego reanuda o detiene el bucle en consecuencia.

### Los sandboxes y las puertas de aprobación son complementarios, no alternativas

Son dos protecciones distintas que trabajan juntas:

- Un sandbox limita el daño que puede hacer cualquier llamada, incluso si se aprueba o se ejecuta automáticamente. Si una llamada sale mal de algún modo, el sandbox contiene el radio de la explosión. "Corre en un entorno restringido" siempre es cierto.
- Una puerta de aprobación añade un punto de decisión humano para las llamadas de mayor riesgo. No evita todo el daño; solo asegura que las llamadas con más probabilidad de causar arrepentimiento pasen primero por ojos humanos.

Si pones en sandbox cada llamada pero nunca controlas nada con una puerta, un error no detectado del modelo aún puede causar daño dentro de los límites del sandbox. Si controlas con una puerta cada llamada a herramienta, el agente deja de ser autónomo y se convierte en una persona que hace todo el trabajo con pasos extra, lo que anula el sentido de la automatización.

El equilibrio correcto: controlar con una puerta una clase estrecha de acciones realmente de alto riesgo (borrar, enviar, publicar, gastar) donde el criterio humano vale el costo de latencia, y poner todo en sandbox para que nada fuera de esa puerta pueda escapar de sus límites aunque algo salga mal.

## Práctica

1. ▢ Estás construyendo un agente que puede leer y resumir documentos de un repositorio compartido. El repositorio tiene 10.000 archivos, y algunos contienen datos sensibles de clientes a los que el agente no debería acceder. Quieres añadir una herramienta de cliente que permita al agente leer archivos. ¿Qué límite de sandbox deberías imponer, y por qué?

<details markdown="1"><summary>Comprobación</summary>

Deberías imponer un límite del sistema de archivos: la herramienta solo puede leer archivos dentro de un árbol de directorios aprobado específico (por ejemplo, todos los archivos de la carpeta "public_docs" pero nada de la carpeta "confidential"). Este límite se comprueba en tiempo de ejecución cuando el modelo llama a la herramienta; aunque el modelo le pida a la herramienta leer una ruta de la carpeta confidencial, el sandbox la rechaza. Esto protege frente a que el contenido de un archivo engañe al modelo o a que este cometa un error de razonamiento sobre qué es seguro leer. El criterio del modelo ("esto parece público") no es el límite; el código sí lo es.

</details>

2. ▢ Tu agente puede escribir código y ejecutarlo en un intérprete de Python en un sandbox. El sandbox limita la CPU a 30 segundos y la memoria a 1 GB. El modelo escribe un programa que inicia un bucle infinito. ¿Lo detendrá el sandbox?

<details markdown="1"><summary>Pista</summary>

Piensa en qué pasa cuando se supera el límite de CPU mientras el código se está ejecutando, y si el harness puede detectar y hacer cumplir ese límite.

</details>

<details markdown="1"><summary>Comprobación</summary>

Sí, el sandbox lo detendrá. Cuando se alcanza el límite de CPU de 30 segundos, el harness termina el proceso. El código del modelo nunca corre para siempre; el sandbox impone el límite de recursos en tiempo de ejecución, no en tiempo de análisis o de compilación. Esta es una razón por la que los límites de recursos son esenciales en un sandbox: evitan que incluso un código bienintencionado consuma todos los recursos.

</details>

3. ▢ Estás diseñando un agente que puede enviar correos en nombre de un usuario. ¿Cuál de estas es una buena razón para añadir una puerta de aprobación antes de que el agente envíe un correo?

    - a) El modelo podría escribir una línea de asunto gramaticalmente incorrecta.
    - b) El modelo podría enviar un correo al destinatario equivocado o con el contenido equivocado, y una vez enviado, el correo no se puede desenviar.
    - c) El modelo podría ralentizar el servidor de correo.
    - d) Al modelo se le podrían acabar las ideas sobre qué correo enviar a continuación.

<details markdown="1"><summary>Comprobación</summary>

**b)** El modelo podría enviar un correo al destinatario equivocado o con el contenido equivocado, y una vez enviado, el correo no se puede desenviar. Es una acción irreversible y de alta consecuencia donde el criterio humano vale el costo de latencia. La opción a no es de consecuencia lo bastante alta (el modelo puede redactar bien). La opción c no es un error del modelo (trata de la carga del sistema). La opción d no tiene sentido (el modelo se detiene cuando se le pide).

</details>

4. ▢ Explica por qué un sandbox no puede evitar todos los errores pero aun así puede ser esencial. Da un ejemplo.

<details markdown="1"><summary>Comprobación</summary>

Un sandbox impone límites sobre a qué recursos puede llegar el código, no sobre qué errores comete el código. Por ejemplo, un sandbox podría impedir que una herramienta escriba en `/etc/passwd` rechazando la escritura en tiempo de ejecución, pero no puede impedir que el modelo escriba el contenido equivocado en un archivo aprobado, como sobrescribir un archivo de configuración de `/home/user/config/` con una sintaxis inválida. El trabajo del sandbox es contener el daño, no garantizar la corrección. Las puertas de aprobación manejan las decisiones de alto riesgo que necesitan criterio humano; los sandboxes manejan los límites de ejecución que evitan que el radio de la explosión se expanda más allá del control.

</details>

## Prácticas en el mundo real

- [ ] Dibuja un diagrama de una llamada a herramienta: muestra el modelo, el harness, el código de la herramienta y el sandbox a su alrededor. Etiqueta lo que controla el modelo (su razonamiento y la elección de herramienta) y lo que controla el harness (el límite).
- [ ] Lista tres herramientas de tu propio trabajo o de un sistema que uses a diario. Para cada una, identifica una acción riesgosa (si la hay) que se beneficiaría de una puerta de aprobación, y un límite de sandbox que tendría sentido.
- [ ] Mañana: Lee el artículo "Building Effective Agents" y anota un ejemplo concreto de un sandbox o de una puerta. Explica en una frase por qué importa esa decisión de diseño.

## Para profundizar

- [Article: "Building Effective Agents", Anthropic Engineering](https://www.anthropic.com/engineering/building-effective-agents)
- [Recursos](../RESOURCES.md)

---

¿No termina de quedar claro? Vuelve a leer la fuente primaria de arriba, ya que esta lección la comprime y en la compresión es donde se escapa la comprensión. Consulta el [glosario](../GLOSSARY.md) por si algún término te resultó resbaladizo.

Si lo poco claro es la propia lección y no el material, eso es un defecto: [abre un issue](https://github.com/TokenCemetery/teach/issues).
