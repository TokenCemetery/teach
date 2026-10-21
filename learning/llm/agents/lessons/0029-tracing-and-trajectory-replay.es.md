---
title: "29. Trazado y reproducción de trayectorias"
description: "Usar convenciones de traza neutrales respecto a los proveedores para capturar ejecuciones de agentes, y reproducir trayectorias para recorrer los fallos paso a paso"
type: lesson
---

# Lección 29. Trazado y reproducción de trayectorias

**Vínculo con la misión:** Registrar las ejecuciones de agentes con trazas estructuradas y estandarizadas, y poder reproducir una trayectoria guardada, te permite entregarle a un colega el punto exacto del fallo, recorrerlo de forma independiente y llevar el diagnóstico en producción de "déjame mirar los logs" a "déjame recorrer la trayectoria".
**Fuente principal:** [Specification: "Semantic Conventions for Generative AI", OpenTelemetry](https://opentelemetry.io/docs/specs/semconv/gen-ai/)
**Requisitos previos:** [Lección 28](0028-cascading-tool-errors.md), [Trayectoria](../GLOSSARY.md)

## Calentamiento

1. ▢ De la lección 28: ¿Cuál es la diferencia entre un error de validación del esquema y un argumento alucinado?

<details markdown="1"><summary>Comprobación</summary>

Un error de validación del esquema ocurre de inmediato cuando falta un campo obligatorio o un valor es del tipo equivocado; el modelo recibe retroalimentación explícita. Un argumento alucinado es un valor bien tipado que pasa la validación pero no corresponde a nada real, así que el error ocurre más adelante y el modelo podría diagnosticar mal por qué falló.

</details>

2. ▢ De la lección 7: ¿Cuál es la única pieza de estado que necesitas persistir para reanudar la ejecución de un agente desde el turno N?

<details markdown="1"><summary>Comprobación</summary>

La transcripción: el historial completo de la conversación hasta el turno N, incluidas cada respuesta del modelo, llamada a herramienta y resultado de herramienta. Al reanudar, vuelve a darle esta transcripción al modelo y continúa el bucle desde el turno N+1.

</details>

## Qué debes saber

### Trazas, spans y convenciones neutrales respecto a los proveedores

Una traza es un registro estructurado y con marcas de tiempo de lo que pasó durante una ejecución de agente. Está hecha de spans, cada uno de los cuales representa una operación discreta:

- Un span por llamada al modelo (entrada: la transcripción; salida: la respuesta del modelo y las llamadas a herramientas; tiempos; tokens usados)
- Un span por ejecución de herramienta (entrada: nombre de la herramienta y argumentos; salida: resultado o error; tiempos)
- Un span por iteración del bucle (hora de inicio, hora de fin, número de turno)

Sin una convención compartida, cada equipo y cada proveedor nombra esto de forma distinta. Una herramienta podría llamar a la entrada de una llamada al modelo "prompt", otra la llama "messages", otra la llama "input". Una herramienta llama a la salida "response", otra la llama "generated_text". Esto hace que las trazas sean incomparables: un equipo que usa las herramientas del proveedor A no puede leer con facilidad las trazas del proveedor B, y pasar de un proveedor a otro significa reescribir todo tu análisis de trazas.

Las convenciones semánticas de GenAI de OpenTelemetry definen un vocabulario neutral respecto a los proveedores para estos spans y atributos. Estandarizan qué información debe llevar cada span:

Un span de llamada al modelo incluye: nombre del modelo, total de tokens de entrada, total de tokens de salida, el esfuerzo de razonamiento (si se fijó), llamadas a herramientas solicitadas, motivo de parada.

Un span de ejecución de herramienta incluye: nombre de la herramienta, si es una herramienta de cliente o de servidor, estado del resultado de la herramienta (éxito o error), si hubo un costo (para herramientas de servidor), mensaje de error si falló.

El span de transacción lo envuelve todo e incluye: número de turno del bucle del agente, horas de inicio y fin en tiempo real, si el turno tuvo éxito o falló, cualquier decisión de parada tomada.

Como estos están estandarizados, una traza producida por un harness puede leerla cualquier herramienta compatible con OpenTelemetry. El mismo panel, script de análisis o visualización que funciona con las trazas de un equipo funciona con las de otro. Es el mismo principio que estandarizó los formatos de transmisión de llamadas a herramientas en la lección 3: todos los conceptos subyacentes (bucle del agente, llamada al modelo, llamada a herramienta) son los mismos entre proveedores, así que un vocabulario estándar te permite moverte entre ellos.

### Por qué importan las trazas estructuradas para el diagnóstico

Los bucles y el envenenamiento de la lección 27, y las cascadas de la lección 28, se encuentran todos leyendo una trayectoria con cuidado. Pero una lectura cuidadosa solo es manejable si la trayectoria está bien estructurada.

Imagina que intentas diagnosticar un fallo en la ejecución de un agente con 47 turnos y cientos de líneas de salida de log. Tienes sentencias de impresión mezcladas con mensajes de error, resultados de herramientas impresos como JSON y marcas de tiempo que pueden o no ser exactas. Estás leyendo línea por línea, intentando reconstruir lo que pasó.

Ahora imagina la misma ejecución representada como una traza estructurada: cada span está etiquetado con un número de turno, cada llamada al modelo está etiquetada con el nombre del modelo, cada llamada a herramienta está etiquetada con el nombre de la herramienta. Puedes consultar la traza: "muéstrame todas las llamadas a herramientas que fallaron a partir del turno 10" o "muéstrame el texto de razonamiento que usó el modelo en el turno 23" o "muéstrame una línea de tiempo de qué spans corrieron en paralelo". Esto es muchísimo más rápido de diagnosticar.

Además, las trazas estructuradas te permiten automatizar parte del diagnóstico: una regla simple puede señalar "detectar bucles repetitivos encontrando spans consecutivos con el mismo nombre de herramienta". Un análisis posterior a la ejecución puede señalar "detectar fallos en cascada buscando spans de error seguidos de spans con distinto nombre de herramienta en secuencia cercana". Estos patrones son difíciles de detectar en logs de formato libre; son directos con datos estructurados.

### Reproducción de trayectorias: probar hipótesis

Como la transcripción es el único estado persistente del agente (lección 7), puedes guardar una trayectoria y volver a dársela a una ejecución nueva en cualquier punto. A esto se le llama reproducción de trayectorias.

Esto es lo que se vuelve posible:

**Reproducir las condiciones exactas**: Un cliente informa de que un agente falló. Guardas su trayectoria (la transcripción hasta el punto del fallo) y se la das a una ejecución nueva del harness. La ejecución nueva ve exactamente lo que vio la original, así que si reproduce el mismo fallo, lo has confirmado. Si tiene éxito, has encontrado un problema en el harness original o en el entorno, no en la lógica del agente.

**Avanzar desde un fallo**: Identificas el turno donde las cosas salieron mal (turno 12). Guardas la trayectoria hasta el turno 11, luego la modificas un poco (quizá añades una nota en la transcripción, o cambias un resultado de herramienta) y reproduces desde el turno 12. El modelo, al ver la entrada modificada, podría tomar un camino distinto. Esto te permite probar "¿y si ese resultado de herramienta hubiera sido más claro?" sin volver a ejecutar todo el agente desde el turno 1.

**Colaborar en el diagnóstico**: Un colega pregunta "¿por qué falló el agente en el turno 28?" Le entregas la trayectoria hasta el turno 27 y una descripción de lo que quieres que mire. Puede reproducirla por sí mismo, de forma independiente a ti, y llegar a su propia conclusión. Estás compartiendo el estado exacto, no solo una descripción de él.

**Construir una prueba de regresión**: Encontraste un error y lo arreglaste. Guarda la trayectoria que desencadenó el error, reprodúcela con el harness corregido y verifica que ahora tiene éxito. Añádela a tu conjunto de pruebas para que el error no vuelva.

### Diseño práctico de la reproducción

Al diseñar la reproducción de trayectorias, importan algunos detalles:

**Guarda la transcripción completa**, incluidos cada turno, cada llamada a herramienta, cada resultado, cada error. No trunques ni muestrees; el modelo necesita el contexto completo para razonar correctamente al reproducir.

**Incluye los metadatos del harness en una sección separada y estructurada**: el número de turno, el conteo de tokens, el conteo de errores, las condiciones de parada que se comprobaron. Esto te ayuda a reconstruir el estado exacto, aunque no hayas guardado todo en la transcripción.

**Pon marca de tiempo a cada span** para poder ver cuánto tardó cada operación y si hay huecos sin explicar (latencia de red, reintentos, esperas).

**Haz configurable la reproducción**: permite reproducir desde el turno N, o reproducir con una transcripción modificada (para probar hipótesis), o reproducir con un modelo distinto para ver si cambia el comportamiento.

### Relación con otras herramientas de diagnóstico

Las trazas estructuradas no reemplazan la lectura cuidadosa de las trayectorias. La complementan. Todavía necesitas entender los modos de fallo de las lecciones 27 y 28 (bucles, envenenamiento, cascadas) para saber qué patrones buscas. Pero una traza estructurada hace los patrones más fáciles de ver y más rápidos de extraer.

Combinadas, forman una disciplina: usa las trazas para navegar rápido por la trayectoria, usa tu conocimiento de los modos de fallo para detectar lo que importa y usa la reproducción para verificar tu diagnóstico.

## Práctica

1. ▢ Estás leyendo una traza estructurada de la ejecución de un agente. La traza muestra: turno 1 (llamada al modelo), turno 2 (llamada a herramienta a search_files), turno 3 (llamada al modelo), turno 4 (llamada a herramienta a search_files con argumentos idénticos), turno 5 (llamada al modelo), turno 6 (llamada a herramienta a search_files otra vez). Compruebas el resultado de la herramienta de cada span y son idénticos. Basándote solo en la estructura de la traza, ¿qué modo de fallo deberías sospechar?

<details markdown="1"><summary>Comprobación</summary>

Esto parece un bucle repetitivo de la lección 27: se llama a la misma herramienta con argumentos idénticos en los turnos 2, 4 y 6, y los resultados son idénticos. La traza estructurada lo hace obvio porque cada turno y llamada a herramienta están etiquetados. En un log sin estructura, tendrías que buscar a mano el nombre de la herramienta y los argumentos a lo largo de muchas líneas.

</details>

2. ▢ Estás reproduciendo una trayectoria desde el turno 15 para depurar un fallo en el turno 30. Le vuelves a dar al modelo la transcripción hasta el turno 14 y le pides que continúe. En tu reproducción, el agente toma un camino distinto del que tomó originalmente y tiene éxito. ¿Qué te dice esto sobre el fallo original?

<details markdown="1"><summary>Pista</summary>

Piensa en qué cambió entre la ejecución original y la reproducción, además de la decisión del modelo.

</details>

<details markdown="1"><summary>Comprobación</summary>

El fallo original probablemente lo causó algo del harness o del entorno en los turnos 15 a 29, no el razonamiento del modelo. Causas posibles: una herramienta que se comportó de forma distinta a la esperada en la ejecución original, un fallo transitorio (problema de red, caída del servicio, cuota superada) o un elemento no determinista (aleatoriedad en los resultados de las herramientas o en el muestreo del modelo). Como la reproducción tuvo éxito con la misma transcripción y el mismo modelo, el problema no fue el entrenamiento ni el razonamiento del modelo; fueron condiciones externas. Esta es una idea diagnóstica que no obtendrías con solo volver a leer la trayectoria.

</details>

3. ▢ Estás diseñando un esquema de traza estructurada para tu harness de agente usando las convenciones de OpenTelemetry. Para un span de llamada a herramienta, ¿cuál de estos atributos es más importante para diagnosticar un fallo en cascada (lección 28)?

    - a) El nombre de la herramienta y los argumentos
    - b) El resultado de la herramienta o el mensaje de error
    - c) La duración en tiempo real de la llamada a herramienta
    - d) La versión del modelo que llamó a la herramienta

<details markdown="1"><summary>Comprobación</summary>

**b)** El resultado de la herramienta o el mensaje de error es lo más importante para diagnosticar cascadas. Una cascada empieza cuando el modelo diagnostica mal un error, así que necesitas ver exactamente qué mensaje de error se devolvió. Con un mensaje de error claro, puedes verificar si la siguiente decisión del modelo fue una respuesta razonable a ese error. El nombre de la herramienta y los argumentos (a) son secundarios; muestran qué intentó el modelo, pero no si entendió el fallo. La duración (c) y la versión del modelo (d) son útiles para el análisis de rendimiento y la detección de regresiones, pero no son lo principal para el diagnóstico de cascadas.

</details>

4. ▢ Guardaste una trayectoria hasta el turno 10, y quieres probar una hipótesis: "si el resultado de la herramienta del turno 5 hubiera incluido el ID del cliente, el agente habría tenido éxito en lugar de entrar en un bucle en los turnos 6 a 10". ¿Cómo modificarías la trayectoria y la reproducirías para probar esta hipótesis?

<details markdown="1"><summary>Comprobación</summary>

Editarías la transcripción: encuentra el resultado de la herramienta del turno 5 y añádele la información del ID del cliente. Por ejemplo, cambia "Tool result: success" por "Tool result: successfully created account; customer ID is 98765". Luego reproduce desde el turno 6 con esta transcripción modificada. Si el agente ahora tiene éxito, tu hipótesis se confirma: la información que faltaba era la causa raíz. Si sigue entrando en bucle, el problema está en otro lado.

</details>

## Prácticas en el mundo real

- [ ] Configura una captura básica de trazas para un agente al que tengas acceso. En al menos una ejecución, exporta la traza y examina su estructura. Identifica: ¿sigue un esquema coherente? ¿Puedes encontrar rápido todas las llamadas al modelo y todas las llamadas a herramientas? ¿Sería útil un lenguaje de consulta (como filtrar por "todas las llamadas a herramientas fallidas") para depurar?

- [ ] Guarda una trayectoria de la ejecución de un agente (al menos 5 turnos). Reprodúcela desde la mitad (turno 3 o 4) y observa si la reproducción produce los mismos resultados o resultados distintos. Si son distintos, investiga por qué.

- [ ] Mañana: Diseña una regla automatizada que detecte un modo de fallo de la lección 27 o 28 en una traza estructurada. Escribe pseudocódigo o SQL que consulte la traza y señale el fallo. Por ejemplo, "señalar si la misma herramienta se llama más de dos veces en turnos consecutivos con argumentos idénticos".

## Para profundizar

- [Specification: "Semantic Conventions for Generative AI", OpenTelemetry](https://opentelemetry.io/docs/specs/semconv/gen-ai/)
- [Recursos](../RESOURCES.md)

---

¿No termina de quedar claro? Vuelve a leer la fuente primaria de arriba, ya que esta lección la comprime y en la compresión es donde se escapa la comprensión. Consulta el [glosario](../GLOSSARY.md) por si algún término te resultó resbaladizo.

Si lo poco claro es la propia lección y no el material, eso es un defecto: [abre un issue](https://github.com/TokenCemetery/teach/issues).
