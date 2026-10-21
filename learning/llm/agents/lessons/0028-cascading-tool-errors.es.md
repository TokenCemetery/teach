---
title: "28. Errores de herramienta en cascada y argumentos alucinados"
description: "Un error de herramienta que lleva a decisiones erróneas, que se hunde en la confusión, y argumentos bien tipados pero falsos que los esquemas no pueden atrapar"
type: lesson
---

# Lección 28. Errores de herramienta en cascada y argumentos alucinados

**Vínculo con la misión:** Identificar fallos en cascada y argumentos alucinados en una trayectoria te permite diagnosticar los fallos de un agente en su verdadero origen, rompiendo la cadena antes de que se descontrole, en lugar de parchear los síntomas más adelante.
**Fuente principal:** [Article: "Building Effective Agents", Anthropic Engineering](https://www.anthropic.com/engineering/building-effective-agents)
**Requisitos previos:** [Lección 27](0027-loops-and-context-poisoning.md)

## Calentamiento

1. ▢ De la lección 27: ¿Cuál es la diferencia entre un bucle repetitivo y el envenenamiento del contexto?

<details markdown="1"><summary>Comprobación</summary>

Un bucle repetitivo es ruidoso: el agente llama a la misma herramienta con los mismos argumentos repetidamente, sin avanzar. El envenenamiento es silencioso: el modelo afirma un hecho falso o alucinado una vez, y todos los turnos siguientes lo tratan en silencio como verdad establecida.

</details>

2. ▢ De la lección 4: ¿Qué valida el esquema JSON de una herramienta?

<details markdown="1"><summary>Comprobación</summary>

Un esquema valida la estructura y el tipo de un argumento: que los campos obligatorios estén presentes, que los valores coincidan con el tipo declarado (cadena, número, booleano), que las listas tengan el tipo de elemento correcto y que se cumplan restricciones como enum o minLength. No valida si el valor es verdadero o si se refiere a algo real.

</details>

## Qué debes saber

### Fallos en cascada: un error lleva a otro

Un fallo en cascada es cuando un error de herramienta lleva a una decisión posterior incorrecta, que lleva a otro error, alejándose cada vez más de la tarea. Cada fallo agrava la confusión en lugar de resolverla.

Aquí tienes un ejemplo paso a paso:

Turno 2: El agente llama a search_files(directory="/config") para encontrar un archivo de configuración. El directorio no existe. La herramienta devuelve un error: "directory not found".

El harness añade este error a la transcripción. Hasta aquí, bien.

Turno 3: El modelo lee el error y decide: "El directorio de inicio estándar no existe. Debo de estar en un entorno distinto. Probaré /etc/config en su lugar". Es un razonamiento razonable basado en información incompleta. El modelo llama a search_files(directory="/etc/config").

Turno 4: La búsqueda tiene éxito, pero devuelve resultados que no coinciden con lo que busca el agente. El modelo, ya comprometido con la ruta /etc/config del turno 3, decide: "Estos resultados son lo bastante parecidos. Usaré el primero". El modelo ahora tiene el archivo equivocado.

Turno 5: El agente lee el archivo equivocado. El contenido no coincide con lo que espera. En lugar de reconocer la discrepancia, el modelo decide: "El formato del archivo debe de haber cambiado. Lo analizaré de forma más permisiva". El agente continúa, todavía construyendo sobre una base equivocada.

Turno 6 hasta N: Cada decisión agrava el error original. El agente ahora razona desde una base falsa y no puede recuperarse sin retroceder de forma significativa.

La razón por la que ocurren los fallos en cascada: cuando una herramienta devuelve un error, el modelo tiene que hacer una suposición sobre por qué. ¿Falta el directorio? ¿Es un error de permisos? ¿Está mal la sintaxis de la ruta? El modelo hace una conjetura y procede. Si la conjetura es errónea, la siguiente llamada a herramienta se construye sobre esa suposición equivocada. Y la cadena se va por ahí.

La protección por conteo de errores de la lección 6 acabará deteniendo el bucle, pero lo detendrá cuando la cascada ya haya crecido, no en el origen.

### Argumentos alucinados: bien tipados pero falsos

Un argumento alucinado es cuando el modelo inventa un valor de aspecto plausible pero factualmente erróneo para el argumento de una herramienta. El valor está bien formado y pasa la validación del esquema, pero simplemente no corresponde a nada real.

Esto es distinto de un error de campo obligatorio ausente (lecciones 3 a 5). Un campo ausente produce un error explícito de validación del esquema que el modelo puede ver y al que puede reaccionar. Un argumento alucinado pasa la validación en silencio.

Ejemplos:

- El modelo debe buscar un usuario por nombre de usuario. Llama a get_user(username="alice_smith"), pero el nombre de usuario real es "asmith". El esquema acepta la cadena; la llamada falla más adelante porque el nombre de usuario no existe.
- El modelo necesita llamar a un endpoint de una API e inventa la ruta: call_api(endpoint="/api/v2/users/search"). El endpoint no existe, pero parece plausible. El esquema lo valida como cadena; la llamada HTTP falla con 404.
- Al modelo se le pide llamar a una función por nombre e inventa un nombre: call_function(name="validate_order"). La función no existe, pero la cadena está bien formada. La llamada falla con "function not found" solo en tiempo de ejecución.

Por qué esto es peor que un error de validación del esquema: cuando el esquema rechaza algo (campo ausente, tipo equivocado), el modelo recibe retroalimentación inmediata y puede corregirlo. Cuando un argumento está bien tipado pero es falso, el error ocurre más adelante, a menudo de forma críptica ("user not found", "404 not found", "function not found"). El modelo no entiende de inmediato que su valor inventado era el problema; en cambio podría culpar al servicio ("la base de datos de usuarios está rota") o al entorno ("la API no está corriendo") y tomar una decisión equivocada basada en ese diagnóstico erróneo.

Si el fallo en cascada de la sección anterior empieza con un argumento alucinado, la cascada es peor: el modelo está construyendo una cadena de razonamiento sobre un valor que inventó y no sabe que lo inventó.

### Mitigaciones: validación y eco

La mitigación central es hacer que los argumentos alucinados fallen más rápido y con más claridad, y darle al modelo visibilidad de lo que realmente pasó.

**Validar contra un conjunto conocido**: Si una herramienta toma un argumento que debería referirse a algo real (un nombre de usuario, el nombre de una función, un endpoint), la herramienta debería validar que existe. En lugar de fallar en silencio más adelante, la herramienta devuelve un error explícito: "user alice_smith not found; valid users are: alice_s, alice_brown, alicia_m". Esto le da al modelo retroalimentación inmediata y un conjunto de opciones entre las que elegir.

**Repetir el valor resuelto**: Después de que una llamada a herramienta tiene éxito, no devuelvas solo "success". Devuelve sobre qué se actuó realmente. Ejemplo:

En lugar de:

```text
Tool result: Success
```

Devuelve:

```text
Tool result: Successfully updated order 12345. Order status is now CONFIRMED.
```

Así, si el argumento del modelo fue alucinado pero resultó coincidir con algo no deseado, el eco hace visible la discrepancia. El modelo ve "llamé con el ID de pedido 12345, y la herramienta informó de que actualizó el pedido 12345", y puede notar si coinciden.

**Exigir confirmación explícita para operaciones de alto riesgo**: Si una llamada a herramienta va a modificar datos o ejecutar una acción, haz que el harness le pida al modelo que confirme el valor real antes de ejecutar. El modelo ve "estás a punto de actualizar al usuario username_alice_smith; ¿confirmas?" y puede atrapar una alucinación en ese punto.

### Fallos en cascada en la trayectoria

Cuando leas una trayectoria y detectes una cascada:

1. Identifica el primer error (turno N): una herramienta devuelve un resultado inesperado o un error.
2. Revisa el turno N+1: ¿qué suposición hizo el modelo sobre por qué ocurrió el error?
3. Rastrea hacia delante: ¿se sigue la siguiente decisión del modelo de esa suposición?
4. Si la suposición era errónea, la cascada ha empezado.

La lección diagnóstica: el error del turno N no es el problema que deberías intentar arreglar reescribiendo el prompt. El problema es el diagnóstico erróneo que hace el modelo del error del turno N en el turno N+1. Arregla la herramienta para que sea más clara sobre lo que salió mal, o dale al modelo mejores opciones para manejar esa clase de error, o endurece las condiciones de parada para que la cascada no crezca.

## Práctica

1. ▢ Un agente está importando datos de un archivo CSV. En el turno tres, llama a parse_csv(filename="data.csv"). La herramienta devuelve un error: "file not found". En el turno cuatro, el modelo dice "El archivo debe de estar comprimido. Lo descomprimiré primero" y llama a decompress(filename="data.csv.gz"). Esta herramienta también falla con "file not found". En el turno cinco, el modelo prueba otra interpretación del error: "Quizá el archivo esté en un subdirectorio" y llama a search_for_file(pattern="data*"). Esto tiene éxito y encuentra "data_backup.csv". En el turno seis, analiza el archivo de respaldo, que tiene columnas distintas de las esperadas, y el análisis tiene éxito pero produce basura. ¿Es esto un fallo en cascada, y dónde se originó?

<details markdown="1"><summary>Comprobación</summary>

Sí, es un fallo en cascada. Se originó en el turno 3, cuando falló el parse_csv inicial. El modelo diagnosticó mal el error: asumió que el archivo estaba comprimido o movido, cuando el problema real probablemente era solo el nombre o la ruta del archivo. En cada turno, el modelo hizo una suposición distinta, y cada suposición llevó a una acción distinta, ninguna de las cuales arregló el problema de fondo. Para el turno 6, el agente trabaja con el archivo equivocado (data_backup.csv en lugar de data.csv), y la salida basura es la consecuencia. La solución no es un mejor razonamiento en el modelo; es hacer más claro el mensaje de error inicial. La herramienta debería devolver "file data.csv not found in current directory; files found: data_backup.csv, old_data.csv". Con esa información, el modelo podría haber elegido explícitamente el archivo de respaldo en el turno 4, en lugar de pasar por los turnos 4 y 5 de diagnóstico erróneo.

</details>

2. ▢ Un agente está actualizando registros de clientes. En el turno dos, el modelo llama a update_customer(customer_id=987654, status="inactive"). El esquema acepta el entero y la cadena. La herramienta devuelve "customer not found". En el turno tres, el modelo, confundido, llama a list_customers(). Esto devuelve una lista de todos los clientes. En el turno cuatro, el modelo elige el primer cliente de la lista y llama a update_customer(customer_id=100001, status="inactive"). Esto tiene éxito. Pero el agente debía actualizar al cliente 987654, no al 100001. ¿Por qué el argumento alucinado del turno dos no produjo un error obvio al que el modelo pudiera reaccionar?

<details markdown="1"><summary>Pista</summary>

Piensa en la diferencia entre un error de validación del esquema y el comportamiento en tiempo de ejecución de una herramienta cuando recibe un valor bien tipado pero inválido.

</details>

<details markdown="1"><summary>Comprobación</summary>

El esquema no rechazó el argumento porque 987654 es un entero válido. La herramienta lo aceptó y lo buscó, solo para fallar en tiempo de ejecución con "customer not found". El mensaje de error era claro ("customer not found"), pero el modelo lo interpretó mal: en lugar de concluir "el cliente 987654 no existe, necesito encontrar el ID correcto", concluyó "algo va mal en cómo estoy consultando, probaré un enfoque distinto". Un mejor diseño de herramienta devolvería: "customer 987654 not found; customers exist in the range 100001 to 150000". Esto hace explícita la discrepancia y le da al modelo un rango concreto con el que trabajar, evitando la cascada.

</details>

3. ▢ Estás construyendo una herramienta que toma una ruta de archivo como argumento. El esquema dice que la ruta debe ser una cadena. Esperas que los modelos inventen de vez en cuando rutas que no existen. ¿Cuál de estas decisiones de diseño evitaría mejor que los argumentos alucinados creen fallos en cascada?

    - a) Aceptar cualquier ruta como cadena y fallar con un genérico "file error" cuando la ruta no existe
    - b) Validar la ruta contra una lista de directorios permitidos; rechazar las rutas fuera de la lista con un error claro
    - c) Aceptar cualquier ruta y devolver un mensaje de éxito aunque el archivo no exista, para que el modelo piense que la operación tuvo éxito
    - d) Exigir al modelo que pase dos argumentos: la ruta y un booleano que confirme que la ruta es correcta

<details markdown="1"><summary>Comprobación</summary>

**b)** Validar contra una lista de directorios permitidos y rechazar las rutas inválidas con un error claro. Esto hace que las rutas alucinadas fallen rápido y de forma explícita, dándole al modelo retroalimentación inmediata. El modelo puede entonces elegir de la lista permitida. **a)** sigue dejando crecer la cascada porque el error es genérico y no ayuda al modelo a entender qué salió mal. **c)** es peligrosa; enmascara el problema y lleva a cascadas porque el modelo cree que tuvo éxito cuando no fue así. **d)** requiere lógica extra en el harness y no resuelve el problema; un modelo puede alucinar tanto la ruta como su confirmación.

</details>

4. ▢ Un agente debe obtener datos de una API. En el turno dos, llama a fetch_api(endpoint="/api/v1/customers/123"). El endpoint no existe, y la herramienta devuelve un error 404. En el turno tres, el modelo dice "El servidor de la API debe de estar caído" y llama a check_service_health(). Esto devuelve "service is up and responding". En el turno cuatro, el modelo dice "La API debe de haber cambiado. Probaré sin el número de versión" y llama a fetch_api(endpoint="/api/customers/123"). Esto también falla con un 404. ¿Qué cambio de diseño en la primera herramienta habría evitado la cascada?

<details markdown="1"><summary>Comprobación</summary>

La primera llamada a herramienta debería haber devuelto más información que solo "404 not found". Podría devolver: "endpoint /api/v1/customers/123 not found (404); valid endpoints include: /api/v2/customers/{id}, /api/v2/orders/{id}". Con esta información, el modelo habría entendido de inmediato que el número de versión era lo que estaba mal, no el servicio, y podría haber ajustado el endpoint en el turno 3 en lugar de los turnos 3 y 4 de cascada. La cascada ocurrió porque el mensaje de error no explicaba el problema real.

</details>

## Prácticas en el mundo real

- [ ] Encuentra la trayectoria de un agente que muestre un fallo. Léela e identifica: ¿hay una cadena en cascada de decisiones, donde cada decisión agrava la confusión? Si es así, ¿en qué turno se originó la cascada? ¿Qué habría hecho un mensaje de error más claro?

- [ ] Diseña una herramienta (elige cualquier herramienta con la que trabajes o que hayas diseñado). Escribe el mensaje de error que la herramienta devuelve actualmente para un caso de fallo común. Ahora reescríbelo para que incluya: qué estaba mal, qué se esperaba y cuáles son las alternativas válidas. ¿Cómo cambiaría este mensaje de error más claro la capacidad de un modelo de diagnosticar el problema?

- [ ] Mañana: Construye un pequeño harness de prueba que llame a una herramienta con un argumento alucinado (un valor que la herramienta no reconoce). Observa el mensaje de error que devuelve la herramienta. Luego modifica la herramienta para que valide contra un conjunto conocido y devuelva un error más claro. Ejecuta de nuevo el mismo argumento alucinado y compara los dos mensajes de error. Escribe un párrafo describiendo cómo el error más claro cambiaría el diagnóstico del fallo por parte de un agente.

## Para profundizar

- [Article: "Building Effective Agents", Anthropic Engineering](https://www.anthropic.com/engineering/building-effective-agents)
- [Recursos](../RESOURCES.md)

---

¿No termina de quedar claro? Vuelve a leer la fuente primaria de arriba, ya que esta lección la comprime y en la compresión es donde se escapa la comprensión. Consulta el [glosario](../GLOSSARY.md) por si algún término te resultó resbaladizo.

Si lo poco claro es la propia lección y no el material, eso es un defecto: [abre un issue](https://github.com/TokenCemetery/teach/issues).
