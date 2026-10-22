---
title: "27. Bucles y envenenamiento del contexto"
description: "Dos modos de fallo visibles en una trayectoria, los bucles repetitivos y el envenenamiento silencioso del contexto, y cómo detectar cada uno"
type: lesson
---

# Lección 27. Bucles y envenenamiento del contexto

**Vínculo con la misión:** Diagnosticar un agente que falla a partir de su trayectoria exige reconocer cuándo un agente está atascado repitiendo la misma acción frente a cuándo construye en silencio sobre una afirmación falsa, para poder arreglar la causa raíz en lugar de añadir más instrucciones.
**Fuente principal:** [Article: "Effective Context Engineering for AI Agents", Anthropic Engineering](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents)
**Requisitos previos:** [Lección 26](0026-why-browser-agents-fail-differently.md), [Trayectoria](../GLOSSARY.md)

## Calentamiento

1. ▢ De la lección 26: ¿Por qué un agente que maneja la pantalla falla más a menudo que un agente que llama herramientas con un razonamiento idéntico?

<details markdown="1"><summary>Comprobación</summary>

Un agente que maneja la pantalla observa a través de píxeles y actúa a través de coordenadas, que son referencias frágiles que se rompen con los cambios de diseño, los estados de carga y los obstáculos. Estos modos de fallo son estructurales y persisten incluso con mejores prompts.

</details>

2. ▢ De la lección 7: Si un harness añade el resultado de una herramienta a sus logs internos pero nunca lo añade a la transcripción, ¿qué sabe el modelo sobre ese resultado?

<details markdown="1"><summary>Comprobación</summary>

Nada. El modelo solo ve la transcripción. Registrar en un log no basta; el resultado debe añadirse a la transcripción para que el modelo sepa en el siguiente turno que ocurrió.

</details>

## Qué debes saber

### Bucles repetitivos: cuando un agente se atasca

Un bucle repetitivo es cuando un agente llama a la misma herramienta con argumentos iguales o casi idénticos turno tras turno, aunque la tarea no avance. Es ruidoso y visible en una trayectoria.

La causa subyacente suele ser una de dos:

Primero, el agente no se da cuenta de que un resultado contradijo o no respaldó su plan. El modelo emitió un comando esperando cierto resultado, recibió uno distinto o nulo, pero no actualizó su modelo interno del mundo. En el siguiente turno, intenta lo mismo otra vez, esperando un resultado distinto.

Ejemplo: Un agente quiere crear un archivo `config.json` en un directorio. La llamada a herramienta falla con "permission denied". El harness añade este error. Pero en el siguiente turno, el modelo llama a la misma herramienta con la misma ruta, como si el error nunca hubiera ocurrido. El razonamiento del modelo era algo como "voy a intentar crear el archivo", y cuando eso devolvió un error, no pasó a "debería probar otra ruta o pedir permiso". Es un fallo de razonamiento que la repetición hace visible.

Segundo, las condiciones de parada del harness son demasiado laxas. El bucle sigue corriendo porque no se activó ninguna condición para detenerlo. Con protecciones estrictas de conteo de errores (lección 6), el bucle sale tras unos pocos intentos fallidos y deja a la vista el fallo para diagnosticarlo. Con protecciones laxas, el bucle continúa, repitiendo la misma acción fallida diez o veinte veces antes de detenerse por fin.

Cómo detectar un bucle repetitivo en una trayectoria:

1. Busca turnos consecutivos con el mismo nombre de herramienta.
2. Compara los argumentos: ¿son idénticos o casi idénticos?
3. Comprueba los resultados: ¿son idénticos, sin cambios o todos fallos?
4. Busca texto de razonamiento repetido: ¿usa el modelo la misma redacción y el mismo razonamiento en varios turnos?

Si se cumplen las tres primeras comprobaciones, el agente está en un bucle repetitivo. El texto de razonamiento repetido (comprobación 4) lo confirma, pero no es obligatorio.

### Envenenamiento del contexto: cuando las afirmaciones falsas se convierten en verdad establecida

El envenenamiento del contexto es distinto. A diferencia de un bucle repetitivo, que es ruidoso y visible, el envenenamiento es silencioso: el modelo afirma algo falso o alucinado una vez, y luego todos los turnos siguientes lo tratan como un hecho establecido.

Así es como ocurre:

En el turno cinco, el modelo dice: "Revisé la base de datos y encontré que el ID del cliente es 12345". Pero ninguna llamada a herramienta recuperó este dato. Nada en ningún resultado de herramienta anterior dijo realmente el ID del cliente. El modelo lo inventó, o lo recordó mal, o lo adivinó a partir de un patrón.

Esa afirmación se añade a la transcripción como cualquier otra cosa. Parece verdad establecida: está ahí mismo en el historial de la conversación, enunciada como un hecho.

En el turno seis, el modelo construye sobre ella: "Ahora buscaré la cuenta del cliente 12345". Llama a una herramienta con ese ID. La herramienta podría fallar ("customer 12345 does not exist"), o peor, podría tener éxito y actuar sobre el cliente equivocado.

En el turno siete, el modelo se ha comprometido aún más: "Veo que la cuenta del cliente 12345 muestra un saldo de..." y la cascada continúa.

Para el turno quince, estás leyendo la trayectoria y ves una enorme cadena de razonamiento y decisiones, todas ancladas en la afirmación falsa de que el ID del cliente es 12345. El modelo no está siendo tonto. El modelo está siendo coherente: la transcripción dice que el ID del cliente es 12345, así que el modelo razona a partir de eso. Pero la transcripción está envenenada.

Por qué esto es distinto de un argumento de herramienta alucinado (lección 28): cuando un modelo inventa un argumento de función como una ruta de archivo, la herramienta suele fallar con un error explícito ("file not found"). El envenenamiento es peor porque a menudo no se detecta de inmediato. Una afirmación falsa en lenguaje natural puede quedarse en la transcripción sin que nadie la cuestione, y el modelo construirá sobre ella.

Cómo detectar el envenenamiento en una trayectoria:

1. Busca un turno donde el modelo enuncie un hecho concreto (un número, un nombre, una fecha, un ID) con mucha confianza y sin matices.
2. Rastrea hacia atrás: ¿respaldó esta afirmación alguna llamada o resultado de herramienta anterior? ¿O el modelo la enunció de la nada?
3. Si no tenía respaldo, rastrea hacia delante: ¿dependen de esta afirmación los turnos posteriores? ¿Usan las llamadas a herramientas posteriores este valor como argumento?
4. Si la respuesta es sí en ambos casos, el contexto está envenenado.

La disciplina diagnóstica que construye esta lección: un bucle se diagnostica mirando qué se repite; el envenenamiento se diagnostica rastreando una afirmación falsa hasta su origen y hacia delante hasta sus consecuencias.

### Por qué la degradación del contexto agrava el envenenamiento

La degradación del contexto (context rot, lección 11) es el problema más amplio: a medida que la transcripción crece, los turnos antiguos se vuelven menos relevantes, la atención del modelo se desplaza y la precisión se deteriora. La degradación del contexto le ocurre a toda ejecución larga de un agente, incluso a una sana.

El envenenamiento es más grave. Una sola afirmación falsa en la transcripción puede anclar todo el razonamiento posterior, y si la afirmación está enterrada entre decenas de turnos, es difícil de detectar. El modelo no puede rechazar con facilidad una afirmación que ya está en su propia transcripción; en cambio, la trata como un hecho establecido.

La mitigación es diagnóstica y preventiva:

- Lee las trayectorias con cuidado y vigila las afirmaciones sin respaldo que el modelo hace en lenguaje natural.
- Al diseñar herramientas, haz que repitan lo que se resolvió: en lugar de solo "success", devuelve "successfully updated customer ID 67890", para que el modelo confirme el valor real.
- Usa condiciones de parada y conteos de errores estrictos para que los bucles salgan rápido y se eviten cascadas de malas decisiones construidas sobre un envenenamiento temprano.

## Práctica

1. ▢ Lees la trayectoria de un agente y ves la misma llamada a herramienta, `get_user_by_email(email="bob@example.com")`, repetida en los turnos 3, 5, 7 y 9. Cada vez, el resultado es "user not found". En el turno 10, el modelo llama a `send_email(recipient="bob@example.com")`. ¿Es esto un bucle repetitivo?

<details markdown="1"><summary>Comprobación</summary>

No, esto no es un bucle repetitivo. El agente llama repetidamente a la misma herramienta de búsqueda y obtiene el mismo fallo, pero luego divergió y llamó a una herramienta distinta (send_email). El agente sí adaptó su estrategia después de que falló la búsqueda. Un bucle repetitivo sería que el modelo siguiera llamando a get_user_by_email en los turnos 10, 11, 12. Esto se parece más al envenenamiento del contexto: el agente pudo haber hecho una suposición falsa en el turno 2 (como "tengo el correo del usuario") que nunca se confirmó, y ahora está actuando sobre ella. Lee todo el contexto de la trayectoria para identificar si el turno 2 o uno anterior hizo una afirmación sin respaldo sobre el correo de Bob.

</details>

2. ▢ Un agente está escribiendo un archivo. En el turno tres, llama a write_file(path="output.txt", content="...") y obtiene el error "permission denied". En el turno cuatro, el modelo dice "probaré un enfoque distinto" y llama a create_directory(path="/tmp/"), que tiene éxito. Luego, en el turno cinco, llama a write_file(path="/tmp/myfile.txt", content="..."). ¿Es esto un bucle repetitivo?

<details markdown="1"><summary>Pista</summary>

Mira si el modelo llama a la misma herramienta con los mismos argumentos, y si su razonamiento cambió entre turnos.

</details>

<details markdown="1"><summary>Comprobación</summary>

No, esto no es un bucle repetitivo. Aunque el agente se encontró con un error, se adaptó: cambió su razonamiento ("probar un enfoque distinto"), llamó a una herramienta distinta y cambió la ruta del archivo en el intento de escritura. La estrategia del modelo evolucionó. Un bucle repetitivo mostraría la misma llamada a write_file con "output.txt" repetida sin cambios. Este agente mostró un camino razonable de resolución de problemas, aunque el objetivo final (escribir en la ubicación original) se abandonó.

</details>

3. ▢ Estás leyendo una trayectoria donde, en el turno 12, el modelo enuncia "The API key for this service is sk-1234567890". Buscas hacia atrás en los turnos 1 a 11 y no encuentras ninguna llamada a herramienta que devolviera esta clave. Buscas hacia delante en los turnos 13 a 20 y encuentras que los turnos 15, 17 y 19 usan todos esta clave en llamadas a una API. ¿Qué ha pasado?

    - a) El modelo razonó correctamente e infirió la clave del contexto
    - b) El contexto está envenenado: una afirmación sin respaldo ahora sustenta varias llamadas a herramientas posteriores
    - c) El modelo está en un bucle repetitivo, llamando a la misma herramienta de API repetidamente
    - d) El harness no añadió el resultado de una herramienta que contenía la clave

<details markdown="1"><summary>Comprobación</summary>

**b)** El contexto está envenenado. El modelo enunció un hecho (la clave de API) sin ninguna llamada a herramienta previa que lo respaldara, y luego varios turnos posteriores dependen de esa afirmación. Esta es la definición de manual del envenenamiento: una afirmación sin respaldo se convierte en la base del razonamiento posterior. No puedes saber solo por la trayectoria si el harness no añadió un resultado (d) o si el modelo alucinó; de cualquier modo, la transcripción ahora está envenenada. **a)** es incorrecta porque inferir no es lo mismo que verificar la verdad establecida. **c)** es incorrecta; esto no es un bucle repetitivo porque las llamadas a herramientas no son idénticas y el modelo no está repitiendo la misma acción.

</details>

4. ▢ Un colega te muestra la trayectoria de un agente que falla. Los tres primeros turnos tuvieron éxito. En el turno cuatro, el modelo está atascado en un bucle llamando a list_files(directory="/data") repetidamente sin cambios. El texto de razonamiento del modelo dice "necesito encontrar el archivo objetivo". ¿Cuál es la causa raíz más probable: un error de lógica en el razonamiento del modelo, o una condición de parada estricta que debería permitir más turnos?

<details markdown="1"><summary>Comprobación</summary>

Es un error de lógica en el razonamiento del modelo, no un problema de condición de parada. La condición de parada no es lo bastante estricta (el bucle se está repitiendo), pero la solución no es aflojarla más. El problema es que el modelo llamó a la misma herramienta repetidamente sin cambiar el argumento ni el razonamiento. Aflojar la condición de parada solo le dejaría repetir más. La solución es diagnosticar por qué el modelo no entendió el resultado de la primera llamada a list_files, o no supo cómo proceder. La condición de parada debería endurecerse para salir tras una o dos repeticiones fallidas, dejando a la vista el problema para el diagnóstico humano en lugar de dejar que se repita sin fin.

</details>

## Prácticas en el mundo real

- [ ] Encuentra en línea la trayectoria de un agente (de documentación, un repositorio de GitHub o una entrada de blog). Léela e identifica: ¿muestra algún bucle repetitivo? ¿Muestra envenenamiento del contexto? Escribe un párrafo describiendo lo que encontraste y cómo lo detectaste.

- [ ] Ejecuta un agente en una tarea que esperes que falle. Examina de forma deliberada la trayectoria en busca de afirmaciones sin respaldo que el modelo haga en lenguaje natural (afirmaciones no respaldadas por resultados de herramientas anteriores). Para cada una, anota qué pasaría si el agente procediera a partir de esa afirmación falsa.

- [ ] Mañana: Diseña una herramienta que ayudaría a prevenir el envenenamiento del contexto. Podría repetir los valores resueltos, añadir sumas de verificación, incluir marcas de tiempo o validar contra un conjunto conocido. Escribe un párrafo describiendo el diseño de tu herramienta y explica cómo hace más fáciles de detectar en una trayectoria las afirmaciones envenenadas.

## Para profundizar

- [Article: "Effective Context Engineering for AI Agents", Anthropic Engineering](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents)
- [Recursos](../RESOURCES.md)

---

¿No termina de quedar claro? Vuelve a leer la fuente primaria de arriba, ya que esta lección la comprime y en la compresión es donde se escapa la comprensión. Consulta el [glosario](../GLOSSARY.md) por si algún término te resultó resbaladizo.

Si lo poco claro es la propia lección y no el material, eso es un defecto: [abre un issue](https://github.com/TokenCemetery/teach/issues).
