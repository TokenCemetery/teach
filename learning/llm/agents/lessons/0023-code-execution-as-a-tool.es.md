---
title: "23. Ejecución de código como herramienta"
description: "Darle a un agente una única herramienta de ejecución de código en un sandbox en lugar de muchas herramientas individuales y estrechas"
type: lesson
---

# Lección 23. Ejecución de código como herramienta

**Vínculo con la misión:** Para decidir si una tarea dada necesita un agente, debes entender que una sola herramienta de ejecución de código puede reemplazar decenas de herramientas estrechas, reduciendo el costo en tokens y la latencia, aunque exige un sandbox robusto frente a código arbitrario.
**Fuente principal:** [Article: "Code Execution with MCP", Anthropic Engineering](https://www.anthropic.com/engineering/code-execution-with-mcp)
**Requisitos previos:** [Lección 22](0022-sandboxing-and-approval-gates.md)

## Calentamiento

1. ▢ En la lección 22 distinguimos entre un sandbox y una puerta de aprobación. ¿Qué hace cada uno, y cuál usarías para evitar que el modelo borre un archivo por accidente?

<details markdown="1"><summary>Comprobación</summary>

Un sandbox es un límite de ejecución que impide que el código llegue a ciertos recursos (como archivos fuera de un directorio permitido). Una puerta de aprobación es un punto de control humano antes de las acciones riesgosas. Para evitar el borrado accidental, usarías un sandbox que restrinja la herramienta a escribir solo dentro de un árbol de directorios seguro, de modo que aunque el modelo pida el borrado, el sandbox lo rechace. Una puerta de aprobación haría una pausa y pediría aprobación humana antes de intentar el borrado, pero no lo evitaría si se aprueba.

</details>

2. ▢ La lección 21 introdujo la idea del descubrimiento de herramientas a escala: el modelo puede introspeccionar qué herramientas existen en lugar de cargar cada definición en el contexto. ¿Qué problema resuelve esto?

<details markdown="1"><summary>Comprobación</summary>

Cuando tienes cientos de herramientas, precargar la definición, el nombre, la descripción y el esquema de parámetros de cada una en la ventana de contexto del modelo agota los tokens y le hace más difícil razonar sobre qué herramienta llamar. El descubrimiento de herramientas deja que el modelo pida información sobre las herramientas disponibles bajo demanda o llame a un endpoint de introspección para explorar capacidades, de modo que la lista completa no tiene que vivir en el contexto inicial.

</details>

## Qué debes saber

### La ejecución de código como alternativa a muchas herramientas estrechas

Considera un escenario de análisis de datos. Sin ejecución de código, podrías exponer al modelo estas herramientas:

- list_files: devuelve una lista de archivos de un directorio
- read_csv: lee un archivo CSV y devuelve las primeras N filas
- compute_mean: calcula la media de una columna
- compute_median: calcula la mediana de una columna
- filter_rows: filtra una tabla por una condición
- sort_by: ordena una tabla por una columna
- write_csv: escribe una tabla de vuelta en un archivo

El modelo ahora tiene que decidir qué herramienta llamar y en qué orden. Podría llamar a read_csv, luego a filter_rows y luego a compute_mean: tres viajes de ida y vuelta por el bucle del modelo. Cada viaje quema tokens razonando sobre qué herramienta llamar a continuación, y cada definición de herramienta cuesta tokens en la ventana de contexto inicial.

En su lugar, dale al modelo una herramienta: un intérprete de código en un sandbox. El modelo escribe un breve programa en Python:

```python
import pandas as pd

data = pd.read_csv('data.csv')
filtered = data[data['age'] > 30]
result = filtered['salary'].mean()
print(result)
```

El modelo lo ejecuta una vez y obtiene la respuesta. Ventajas: una llamada a herramienta en lugar de tres, una definición de herramienta en lugar de siete, y el modelo puede encadenar operaciones en un solo turno sin volver a razonar sobre qué herramienta llamar a continuación.

### Beneficios en costo y latencia

Este enfoque reduce tanto el costo en tokens como la latencia:

- Costo en tokens: Pagas una definición de herramienta en lugar de muchas, y la sobrecarga de razonamiento del modelo sobre qué herramienta llamar se reduce a escribir código normal, que el modelo ya hace con eficiencia.
- Latencia: Un viaje de ida y vuelta de llamada a herramienta en lugar de tres o siete significa que el tiempo real del agente baja de forma proporcional.

Para agentes que corren a escala o con requisitos de tiempo real, estos ahorros se acumulan.

### Conexión con el descubrimiento de herramientas a escala

La lección 21 introdujo la idea de que, en lugar de precargar cada definición de herramienta en el contexto, el modelo puede explorar las capacidades disponibles de forma dinámica. La ejecución de código es una instanciación concreta de este principio: el modelo no necesita tener precargada cada herramienta de transformación de datos porque puede escribir código para hacer él mismo la transformación. Las capacidades disponibles (funciones, bibliotecas, utilidades del sistema) se descubren cuando se ejecuta el código, no en el contexto inicial.

En algunos sistemas, la herramienta de ejecución de código puede tener ella misma un mecanismo de descubrimiento: una función que el modelo puede llamar para listar qué bibliotecas hay disponibles, a qué fuentes de datos puede llegar o qué comandos del sistema están disponibles. Esto superpone descubrimiento sobre descubrimiento.

### Qué debe imponer un sandbox frente a código arbitrario

En la lección 22 vimos que un sandbox impone límites sobre lo que puede alcanzar la ejecución de una herramienta: rutas del sistema de archivos, hosts de red, límites de recursos. Cuando la herramienta es "ejecutar código arbitrario que escribió el modelo", el sandbox tiene que imponer estos límites frente a código mucho más expresivo e impredecible que una llamada a herramienta fija con un esquema JSON conocido.

El modelo podría escribir código que:

- Intente escapar del límite del sistema de archivos usando enlaces simbólicos, trucos de recorrido de rutas (/../..) o llamando a utilidades del sistema como find o ls para sondear fuera del límite.
- Escriba código de red que intente llegar a hosts fuera de la lista de permitidos.
- Genere bucles infinitos, funciones recursivas o bucles que asignan memoria y que intenten agotar los recursos.
- Llame a funciones o métodos que el código cree que existen pero que el harness pretende prohibir.

El sandbox debe ser lo bastante robusto para contener todo esto. Esto es más difícil que poner en sandbox una herramienta fija porque la superficie del código no tiene límite. Un verdadero sandbox de ejecución de código suele ejecutar el código en un contenedor o proceso aislado con reglas de seccomp, espacios de nombres de red y cgroups de recursos, no solo comprobaciones de permisos del sistema de archivos.

### Cuándo usar ejecución de código frente a herramientas estrechas

La ejecución de código es potente pero introduce complejidad de sandbox. Deberías preferirla cuando:

- El modelo necesita combinar muchas operaciones pequeñas que de otro modo requerirían muchos viajes de ida y vuelta.
- Las operaciones son algorítmicas o de transformación de datos (filtrado, agregación, cálculo, conversión de formato).
- Las capacidades disponibles están bien definidas y son relativamente estables.

Deberías ceñirte a herramientas estrechas y hechas a propósito cuando:

- La operación es realmente de alto riesgo y se beneficia de una supervisión humana explícita (enviar un correo, publicar en público, gastar dinero).
- La seguridad de la operación depende de validar entradas o salidas de formas específicas del dominio que el harness entiende pero el código no.
- La operación es rara y el ahorro en tokens de una sola herramienta no compensa la complejidad del sandbox.

Ambos enfoques pueden coexistir: un agente podría tener una herramienta de ejecución de código para el manejo de datos y herramientas estrechas con puerta de aprobación para enviar correos o publicar resultados.

## Práctica

1. ▢ Tienes un agente que actualmente usa siete herramientas separadas para manipular cadenas: split_string, join_strings, uppercase, lowercase, replace_substring, reverse_string y trim_whitespace. ¿Podrías reemplazar las siete con una sola herramienta de ejecución de código? ¿Qué ganarías y qué perderías?

<details markdown="1"><summary>Comprobación</summary>

Sí, podrías. El modelo ganaría: una definición de herramienta en lugar de siete, una llamada a herramienta para realizar una operación de cadenas compleja en lugar de siete viajes de ida y vuelta, y la capacidad de escribir código legible ("result = text.upper()") en lugar de adivinar nombres de herramientas. Perderías: guardarraíles explícitos para cada operación (cada herramienta podría validar la entrada) y una latencia determinista (la ejecución de código ahora es variable según lo que escriba el modelo). Para la manipulación de cadenas, el enfoque de ejecución de código suele ganar porque las operaciones son simples y el harness puede imponer un límite de sistema de archivos o de recursos sin lógica específica del dominio.

</details>

2. ▢ Estás diseñando un agente para un sistema de salud que puede leer historiales de pacientes y generar sugerencias de diagnóstico. ¿Deberías exponer esto mediante una herramienta de ejecución de código donde el modelo escribe su propio código de acceso a datos, o mediante herramientas estrechas como read_patient_record, filter_by_condition y compute_risk_score?

<details markdown="1"><summary>Pista</summary>

Considera qué significa "seguridad" en un contexto de salud. ¿Qué necesita imponer el harness, y puede imponerlo un sandbox de código de propósito general, o necesita lógica específica del dominio?

</details>

<details markdown="1"><summary>Comprobación</summary>

Aquí son mejores las herramientas estrechas. Un sistema de salud tiene requisitos estrictos de cumplimiento (HIPAA, registro de auditoría, control de acceso a los datos) que el harness probablemente impone mediante lógica específica del dominio, no mediante sandboxing del sistema de archivos. Una herramienta estrecha read_patient_record puede incluir comprobaciones de autorización, registro de auditoría y redacción de datos; una herramienta de ejecución de código no puede imponer esto con facilidad, porque el harness tendría que inspeccionar el código que escribió el modelo, lo que anula el propósito de la ejecución de código. El alto riesgo también hace más valiosas las puertas de aprobación. Prefiere herramientas estrechas y auditables cuando la seguridad de la operación depende de lógica de negocio específica del dominio, no de límites del sistema de archivos.

</details>

3. ▢ ¿Cuál de estas afirmaciones sobre la ejecución de código es cierta?

    - a) La ejecución de código siempre es más rápida que usar herramientas separadas porque reduce los viajes de ida y vuelta, incluso para operaciones simples y únicas.
    - b) La ejecución de código reduce el costo en tokens porque una definición de herramienta reemplaza a muchas, pero solo ahorra latencia si el modelo encadena varias operaciones.
    - c) La ejecución de código elimina la necesidad de sandboxes porque el código es de confianza.
    - d) La ejecución de código no requiere puertas de aprobación porque el harness puede inspeccionar el código antes de que se ejecute.

<details markdown="1"><summary>Comprobación</summary>

**b)** La ejecución de código reduce el costo en tokens porque una definición de herramienta reemplaza a muchas, pero solo ahorra latencia si el modelo encadena varias operaciones. El ahorro en tokens es real (una definición en lugar de muchas). El ahorro de latencia solo importa si el modelo hace varias operaciones que de otro modo requerirían varios viajes de ida y vuelta; para una sola operación, el tiempo es similar o peor. La opción a es incorrecta (las operaciones únicas no se benefician). La opción c es incorrecta (la ejecución de código necesita sandboxes robustos porque el código es arbitrario). La opción d es incorrecta (las puertas de aprobación siguen teniendo sentido para operaciones de alto riesgo, y la inspección previa no evita todos los errores).

</details>

4. ▢ Explica por qué el trabajo del sandbox se vuelve más difícil cuando la herramienta es "ejecución de código" en lugar de una herramienta específica como "delete_file". ¿Cuál es un escenario concreto donde importa esta dificultad?

<details markdown="1"><summary>Comprobación</summary>

Con una herramienta específica, el harness sabe de antemano qué hará la herramienta y puede imponer un límite en ese punto concreto (la herramienta delete_file solo puede tocar archivos de un directorio seguro). Con la ejecución de código, el harness no sabe qué hará el código hasta que se ejecuta; el código podría llamar a utilidades del sistema, abrir sockets de red o usar funciones del lenguaje que el harness no espera. Un escenario concreto: el modelo escribe código que llama a subprocess.Popen para ejecutar un comando de shell como "ls /../.." para sondear el sistema de archivos más allá del límite previsto. Un sandbox solo de permisos del sistema de archivos no detendrá esto; el sandbox necesita reglas de seccomp o un contenedor para impedir llamadas arbitrarias al sistema. Por eso los sandboxes de ejecución de código suelen ser más complejos que los de herramientas estrechas.

</details>

5. ▢ Tu agente usa ejecución de código para analizar datos. El modelo escribe código que debería leer de un archivo CSV, pero en su lugar escribe código que intenta descargar un archivo de internet. El sandbox impone que no haya acceso a la red. ¿Qué pasa, y es esto un fallo del sandbox?

<details markdown="1"><summary>Comprobación</summary>

El código se ejecuta, intenta la llamada de red y la operación de red es rechazada o se bloquea. Esto no es un fallo del sandbox; es el sandbox funcionando como se pretende. El trabajo del sandbox es impedir que el código llegue a recursos fuera de su límite, no asegurar que el código sea correcto ni que haga lo que el modelo pretendía. Un fallo del sandbox sería que la llamada de red tuviera éxito a pesar de la regla de no red. El error del modelo (escribir el código equivocado) es independiente del trabajo del harness (imponer límites).

</details>

## Prácticas en el mundo real

- [ ] Lista las herramientas que usa tu propio trabajo o un sistema que conozcas. Identifica un grupo de tres o más herramientas estrechamente relacionadas y esboza cómo podrían reemplazarse por una herramienta de ejecución de código. ¿Qué necesitarías para confiar en el sandbox y hacer este cambio?
- [ ] Escribe un programa sencillo de análisis de datos (filtrar una tabla, calcular un agregado, ordenar). Imagina que eres el modelo. ¿Cuántos viajes de ida y vuelta por un bucle de llamadas a herramientas llevaría esto con herramientas separadas, y cuántos con ejecución de código?
- [ ] Mañana: Revisa el artículo "Code Execution with MCP" e identifica una decisión de diseño del sandbox (límite de recursos, límite del sistema de archivos, restricción de red) y explica por qué ese límite concreto importa para el caso de uso del artículo.

## Para profundizar

- [Article: "Code Execution with MCP", Anthropic Engineering](https://www.anthropic.com/engineering/code-execution-with-mcp)
- [Recursos](../RESOURCES.md)

---

¿No termina de quedar claro? Vuelve a leer la fuente primaria de arriba, ya que esta lección la comprime y en la compresión es donde se escapa la comprensión. Consulta el [glosario](../GLOSSARY.md) por si algún término te resultó resbaladizo.

Si lo poco claro es la propia lección y no el material, eso es un defecto: [abre un issue](https://github.com/TokenCemetery/teach/issues).
