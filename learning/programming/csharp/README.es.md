---
title: C#
description: "Hazte cargo de un servicio en C#: el sistema de tipos, async y lo que hace el CLR con lo que escribiste, desde cero"
type: topic
---

# Aprendizaje: C\#

Conviértete en el ingeniero en quien se confía para hacerse cargo de un servicio en C# dentro de un equipo: capaz de modelar un dominio eligiendo correctamente entre un struct, una clase y un record, de escribir y razonar sobre `async`/`await`, de consultar y transformar datos con soltura con LINQ, de entregar un backend ASP.NET Core tipado y probado, y de explicar lo que hace el CLR con el código que escribiste.

**Última lección:** [45. Empaquetado y versionado con NuGet](lessons/0045-nuget-packaging-and-versioning.md)

## Cómo se ve el éxito

- Modelar un dominio eligiendo correctamente entre un struct, una clase y un record, y defender la elección a partir del comportamiento real del CLR.
- Escribir código con `async`/`await` y explicar qué le ocurre a la ejecución de un método en cada `await`.
- Consultar y transformar datos con soltura con LINQ.
- Entregar un servicio backend ASP.NET Core tipado y probado, diseñado de forma idiomática para C#.
- Ante código C# escrito con un hábito que simplemente compila (una clase donde corresponde un struct, un callback en lugar de `async`/`await`), nombrar el hábito y reescribirlo de forma idiomática.

## Restricciones

- No se asume experiencia previa con C#. La experiencia en otro lenguaje orientado a objetos (Java, Kotlin) acorta las primeras etapas pero no es necesaria, y trae hábitos que C# castiga en silencio: una clase donde corresponde un struct o un record, un callback donde `async`/`await` se lee mejor.
- Contexto de ASP.NET Core / servicios backend; no .NET en general sin ese enfoque.

## Fuera de alcance

- Unity y el desarrollo de videojuegos con C#: un contexto lo bastante distinto como para no cubrirlo aquí.
- Los detalles internos del JIT, y escribir o ajustar a mano un recolector de basura: la etapa 8 cubre el heap generacional, los modos del GC y el profiling al nivel que necesita quien se hace cargo de un servicio para medir y defender una elección, no al nivel de implementar uno.
- Imágenes de contenedor: meter un servicio publicado en una imagen, y ejecutar, asegurar y depurar ese contenedor, corresponde a [`infrastructure/containers`](../../infrastructure/containers/).
- Ejecutar el servicio en un clúster, incluido lo que hace Kubernetes con sus checks de liveness y readiness, corresponde a [`infrastructure/kubernetes`](../../infrastructure/kubernetes/).

## El arco

Once etapas, desde ningún conocimiento previo hasta el criterio de un perfil sénior. No es una lista de lecciones: una etapa abarca varias lecciones y los límites son difusos.

| Etapa | Lecciones | Cubre | Terminada cuando |
|---|---|---|---|
| 1. Fundamentos | 0001 a 0006 | Tipos por valor frente a tipos por referencia (struct frente a class), tipos por valor anulables, tipos básicos e interpolación de strings, colecciones (`List`, `Dictionary`, `IEnumerable`), flujo de control, excepciones | Puedes predecir el comportamiento de copia frente a referencia sin ejecutar el código |
| 2. Modelado | 0007 a 0011 | Propiedades, tipos `record`, pattern matching y switch expressions, interfaces con implementaciones por defecto, genéricos | Modelas un dominio eligiendo el tipo adecuado en lugar de una clase para todo |
| 3. Modismos | 0012 a 0016 | Métodos de extensión, sintaxis de consulta y de métodos de LINQ, delegados y eventos, tipos de referencia anulables, miembros con cuerpo de expresión | Escribes C# que un revisor no describiría como Java traducido |
| 4. Async | 0017 a 0021 | El modelo de `Task`, la mecánica de `async`/`await`, la composición de `Task`, los cancellation tokens, `IAsyncEnumerable` | Puedes explicar qué hace `await` con la ejecución de un método y predecir el comportamiento de un programa asíncrono |
| 5. Pruebas y build | 0022 a 0024 | xUnit/NUnit, mocking, la CLI `dotnet` y la gestión de proyectos y paquetes | Otra persona puede clonarlo, compilarlo, probarlo y ejecutarlo |
| 6. Entregar el servicio | 0025 a 0029 | Routing y middleware de ASP.NET Core, inyección de dependencias, configuración, nociones básicas de Entity Framework Core, estructurar un backend tipado y probado | Entregas un servicio ASP.NET Core tipado y probado |
| 7. Criterio | 0030 a 0031 | Comparar `async`/`await` con los hilos virtuales de Java y LINQ con la Stream API, revisar C# en busca de un hábito que simplemente compila | Se confía en ti para tomar la decisión y explicársela a otra persona |
| 8. El runtime del CLR y el rendimiento | 0032 a 0037 | El diseño generacional del heap gestionado, los modos del GC, `Span<T>`/`Memory<T>`, `stackalloc`/`ArrayPool<T>`, medir struct frente a class con BenchmarkDotNet, y el profiling | Optimizas a partir de un perfil y defiendes la mejora con un benchmark fiable, vinculado al comportamiento generacional y de asignación real del CLR |
| 9. Ciclo de vida de los recursos | 0038 | Implementar `IDisposable` e `IAsyncDisposable`: el patrón dispose, el parámetro `disposing`, los finalizadores y `DisposeAsyncCore` | Implementas un patrón dispose correcto e idempotente en lugar de limitarte a consumir uno a través de `using` |
| 10. Operar y asegurar el servicio | 0039 a 0042 | Logging estructurado con `ILogger`, health checks de liveness/readiness, OpenTelemetry, autenticación y autorización, y serialización con `System.Text.Json` | Entregas un servicio que se puede observar, comprobar su salud, asegurar y serializar correctamente, no solo compilar |
| 11. Evolución de la API y empaquetado | 0043 a 0045 | Compatibilidad binaria frente a de código fuente frente a de comportamiento, `[Obsolete]` y la deprecación, empaquetado con NuGet y versionado semántico | Clasificas con precisión el impacto de un cambio en la compatibilidad y haces evolucionar una API publicada sin romper por sorpresa a quienes la llaman |

## Lecciones

Recórrelas en orden.

| # | Lección | Enseña |
|---|---|---|
| [0001](lessons/0001-structs-and-classes.md) | Structs y clases | La elección del sistema de tipos que Java nunca te dio, y lo que hace realmente el CLR con cada uno |
| [0002](lessons/0002-nullable-value-types.md) | Tipos por valor anulables | Por qué int? sigue siendo un tipo por valor, la regla de comparación que hace falsas ambas direcciones y lo que el boxing le hace al envoltorio |
| [0003](lessons/0003-basic-types-and-string-interpolation.md) | Tipos básicos e interpolación de strings | Las palabras clave como alias de tipos de .NET, por qué decimal está integrado en lugar de ser una clase, y las reglas de ancho, formato y efectos secundarios del hueco de interpolación |
| [0004](lessons/0004-collections.md) | Colecciones | IEnumerable como la abstracción en la que se apoya el resto del arco, y la búsqueda en un diccionario que lanza una excepción donde el map de Java devuelve null |
| [0005](lessons/0005-control-flow.md) | Flujo de control | Los tres lugares en los que el flujo de control no se traslada desde Java: el enumerador con duck typing de foreach, switch sin fall-through y goto como salto legal |
| [0006](lessons/0006-exceptions.md) | Excepciones | Los filtros de excepciones y la traza de pila que destruye capturar y volver a lanzar, using para una limpieza determinista y el cierre de la etapa 1 |
| [0007](lessons/0007-properties.md) | Propiedades | Los accesores como funcionalidad del lenguaje, las tres promesas ortogonales de required, init y un tipo no anulable, y las propiedades calculadas sin campo de respaldo |
| [0008](lessons/0008-record-types.md) | Tipos record | Qué genera realmente el modificador record, por qué la igualdad depende del tipo en tiempo de ejecución y la inmutabilidad superficial que una expresión with no arregla |
| [0009](lessons/0009-pattern-matching.md) | Pattern matching | El vocabulario de patrones, la exhaustividad de la switch expression y su único hueco silencioso, y por qué el orden de los brazos es una cuestión de tiempo de compilación |
| [0010](lessons/0010-interfaces.md) | Interfaces | Lo que puede contener una interfaz ahora que puede llevar implementaciones, la autopropiedad que no lo es y el miembro que solo puedes llamar a través de la interfaz |
| [0011](lessons/0011-generics.md) | Genéricos | Las restricciones como vocabulario de lo que debe ser un parámetro de tipo, la varianza como regla sobre posiciones y el cierre de la etapa 2 sobre elegir el tipo adecuado |
| [0012](lessons/0012-extension-methods.md) | Métodos de extensión | Dos sintaxis que compilan al mismo IL, la regla de enlace que impide que una extensión sobrescriba nada y lo que eso cuesta en el punto de llamada |
| [0013](lessons/0013-linq.md) | LINQ | Un lenguaje de consulta con dos sintaxis y ninguna diferencia semántica, por qué nada se ejecuta hasta que iteras y el árbol de expresiones que permite que la misma consulta llegue a una base de datos |
| [0014](lessons/0014-delegates-and-events.md) | Delegados y eventos | Un delegado como un tipo cuya firma incluye su tipo de retorno, la lista de invocación en la que un manejador que lanza una excepción detiene al resto y lo que la palabra clave event les quita a quienes llaman |
| [0015](lessons/0015-nullable-reference-types.md) | Tipos de referencia anulables | Anotaciones en lugar de tipos, el estado de nulidad que el compilador sigue a través de tu flujo de control y la única biblioteca que convierte tu anotación en comportamiento en tiempo de ejecución |
| [0016](lessons/0016-expression-bodied-members.md) | Miembros con cuerpo de expresión | El segundo trabajo del token flecha, la regla de las expresiones de sentencia para los miembros void y el cierre de la etapa 3 sobre reescribir Java traducido |
| [0017](lessons/0017-the-task-model.md) | El modelo de Task | Una task como operación asíncrona y no como hilo, las cuatro formas en que llega a existir una y la AggregateException que puede terminar un proceso que creías acabado |
| [0018](lessons/0018-async-and-await.md) | async y await | Qué le hace await al método que lo contiene, los tres lugares en los que está prohibido y por qué async void rompe el único mecanismo que tiene quien llama |
| [0019](lessons/0019-task-composition.md) | Composición de tasks | Empezar el trabajo antes de esperarlo, el ToArray que hace que una lista de tasks construida con LINQ se ejecute de verdad y el doble await que requiere WhenAny |
| [0020](lessons/0020-cancellation-tokens.md) | Cancellation tokens | Cancelación cooperativa con un solicitante y muchos oyentes, por qué volver antes de tiempo informa de éxito y la comparación de tokens que decide si una task dice que fue cancelada |
| [0021](lessons/0021-async-streams.md) | Streams asíncronos | Las tres interfaces que hay detrás de await foreach, el atributo que permite que el token de un consumidor llegue al cuerpo de un iterador asíncrono y el cierre de la etapa 4 sobre predecir un programa asíncrono |
| [0022](lessons/0022-xunit-and-nunit.md) | xUnit y NUnit | La regla de una instancia por prueba que hace que xUnit no necesite ningún atributo de setup, la palabra theory significando dos cosas distintas y el paralelismo que cuesta en silencio un fixture compartido |
| [0023](lessons/0023-mocking.md) | Mocking | El proxy en tiempo de ejecución que hay detrás de toda biblioteca de sustitución, el valor por defecto de C# que decide qué se le permite reemplazar y la aserción sobre un mock que pasa sin que la llamada llegue a ocurrir |
| [0024](lessons/0024-the-dotnet-cli-and-packages.md) | La CLI dotnet y los paquetes | El único comando que necesita un clon recién hecho, por qué la versión de un paquete es un mínimo y no una fijación, la versión del SDK que reordenó los comandos y el cierre de la etapa 5 |
| [0025](lessons/0025-routing-and-middleware.md) | Routing y middleware | Dos sistemas que comparten un mismo Program.cs, uno resuelto por el orden en que escribiste y otro por la precedencia de las plantillas, y las dos posiciones que deciden qué puede saber un middleware y si llega a ejecutarse |
| [0026](lessons/0026-dependency-injection.md) | Inyección de dependencias | Tres ciclos de vida como afirmaciones que el contenedor solo hace cumplir donde puede verlas, el servicio de larga vida que promueve en silencio a uno de vida corta y por qué nadie libera lo que creó el contenedor |
| [0027](lessons/0027-configuration.md) | Configuración | Un único diccionario plano de strings en el que gana el último proveedor, tres interfaces de opciones separadas por ciclo de vida y no por gusto, y una validación que espera a la primera petición salvo que le pidas que no lo haga |
| [0028](lessons/0028-entity-framework-core.md) | Entity Framework Core | Un contexto que recuerda lo que consultaste para que una asignación se convierta en un update, el único lugar en el que se permite que una consulta recurra al cliente y por qué el hábito de la etapa 4 de solapar trabajo lo corrompe |
| [0029](lessons/0029-structuring-a-typed-tested-backend.md) | Estructurar un backend tipado y probado | El contenedor como la costura a través de la cual una prueba reemplaza registros, la regla documentada para elegir entre una prueba unitaria y una de integración y el cierre de la etapa 6 con cuatro defectos que compilan todos |
| [0030](lessons/0030-two-comparisons-with-java.md) | Dos comparaciones con Java | El mismo problema de espera resuelto en dos capas distintas, por qué la respuesta de Java elimina el estilo que C# exige en lugar de adoptarlo y el árbol de expresiones que no tiene equivalente en un Stream |
| [0031](lessons/0031-reviewing-csharp.md) | Revisar un código base en C# | La diferencia entre una opinión de estilo y un costo que puedes nombrar, una pasada de revisión ordenada por lo que el compilador nunca te dirá y los hábitos que este arco lleva recopilando desde la lección 1 |
| [0032](lessons/0032-the-managed-heap-and-generations.md) | El heap gestionado y las generaciones | La lección 1 dijo que una instancia de clase vive en el heap gestionado; esta lección abre lo que le pasa allí, por qué el heap se divide en tres generaciones y por qué la mayoría de los objetos están pensados para morir en la más joven sin llegar a ser promovidos |
| [0033](lessons/0033-gc-modes-and-tradeoffs.md) | Modos del GC y sus compromisos | La lección 32 estableció el heap generacional; esta lección cubre cómo se ejecuta realmente una recolección sobre él, con un hilo dedicado o uno por núcleo, bloqueando todos los hilos gestionados o dejando que la mayoría siga, y el único momento en que incluso el modo no bloqueante tiene que detenerlo todo |
| [0034](lessons/0034-span-and-memory.md) | Span y Memory | Una vista sin asignaciones sobre memoria existente que nunca entra en el sistema generacional de la lección 32, las restricciones del compilador que la mantienen de forma segura solo en la pila y su contraparte segura para el heap, construida exactamente para lo único que ella no puede hacer: cruzar un await |
| [0035](lessons/0035-stackalloc-and-arraypool.md) | stackalloc y ArrayPool | La lección 34 permitió que un Span<T> viera memoria reservada con stackalloc; esta lección cubre qué asigna realmente stackalloc, por qué emparejarlo con un ref struct es lo que lo hace seguro, su riesgo real (un desbordamiento de pila, no la recolección de basura) y ArrayPool<T> como alternativa para un buffer demasiado grande o de vida demasiado larga para la pila |
| [0036](lessons/0036-struct-vs-class-measured.md) | Struct frente a class, medido | La lección 1 argumentó que un struct puede evitar una asignación en el heap que una clase de la misma forma requeriría; esta lección es donde ese argumento se mide en lugar de razonarse, y por qué la forma obvia de medirlo produce un número que no significa nada |
| [0037](lessons/0037-profiling-a-csharp-service.md) | Profiling de un servicio en C# | dotnet-counters detecta el síntoma y dotnet-trace encuentra la pila caliente que hay detrás, hacer profiling solo después del calentamiento para no medir el JIT, y el cierre de la etapa 8 sobre devolver el hallazgo de un perfil a través de una de las palancas de esta misma etapa |
| [0038](lessons/0038-idisposable-and-iasyncdisposable.md) | IDisposable e IAsyncDisposable | La lección 6 enseñó using como consumidor, y la lección 26 enseñó que un contenedor libera lo que crea; esta lección es para el otro lado, implementar de verdad IDisposable e IAsyncDisposable, el patrón que hace que un tipo sea seguro de liberar más de una vez, seguro de finalizar y seguro de esperar con await |
| [0039](lessons/0039-logging-and-health-checks.md) | Logging y health checks | Un backend tipado y probado que nadie puede observar ni preguntarle "¿estás funcionando?" no ha terminado de entregarse; esta lección conecta el logging estructurado de ILogger y la separación entre liveness y readiness en Program.cs del mismo modo en que la lección 25 conectó el routing y la lección 26 el contenedor |
| [0040](lessons/0040-opentelemetry.md) | OpenTelemetry | El ILogger de la lección 39 ya es uno de los tres pilares de OpenTelemetry; esta lección añade los otros dos, métricas y trazas, mediante APIs ya integradas en el framework, y conecta los tres a un servicio con el mismo patrón AddX que ya enseñaron las lecciones 25, 26 y 39 |
| [0041](lessons/0041-authentication-and-authorization.md) | Autenticación y autorización | La autenticación responde a quién eres y la autorización a qué se te permite hacer, documentadas como asuntos separados aunque una se apoye en la otra, conectadas con la misma disciplina de orden de middleware de la lección 25 y la excepción AllowAnonymous que de verdad necesitan los health checks de la lección 39 |
| [0042](lessons/0042-system-text-json.md) | System.Text.Json | Los valores por defecto del serializador a secas (PascalCase, sensible a mayúsculas) no son los que usa realmente ASP.NET Core en el límite HTTP (camelCase, insensible a mayúsculas), una divergencia real que vale la pena nombrar antes de que produzca un resultado de prueba confuso, además de la generación de código fuente como alternativa en tiempo de compilación a la reflexión |
| [0043](lessons/0043-api-compatibility.md) | Compatibilidad de la API | Un cambio que recompila sin problemas puede hacer fallar a todos los que llaman y no recompilan, un cambio que no compila puede estar perfectamente bien para quienes ya tienen un binario que funciona, y un cambio que no hace ninguna de las dos cosas puede seguir haciendo algo distinto en silencio, que es justo de lo que existe el versionado semántico para avisar a quien llama |
| [0044](lessons/0044-obsolete-and-deprecation.md) | Obsolete y deprecación | La lección 43 nombró lo que cuenta como cambio incompatible; ObsoleteAttribute es la forma en que una API publicada anuncia que viene uno, escalando de una advertencia que se puede suprimir a un error de compilación real en el mismo miembro, con un ID de diagnóstico personalizado para que la advertencia de una deprecación se pueda silenciar sin silenciar todas las demás del proyecto |
| [0045](lessons/0045-nuget-packaging-and-versioning.md) | Empaquetado y versionado con NuGet | La lección final de este arco une la etapa 11: el número de versión que realmente justifican las categorías de compatibilidad de la lección 43, el sufijo de prerrelease sobre el que NuGet no impone nada más allá de llamarlo prerrelease, el consejo sobre el límite superior que va contra el instinto y el paquete obsoleto que una recompilación puede dejarte probando |

## Referencia

- [Glosario](GLOSSARY.md): términos canónicos de este tema
- [Recursos](RESOURCES.md): fuentes de confianza
- [Tipos por valor frente a tipos por referencia](reference/value-vs-reference-types.md): struct frente a class, tipos por valor anulables, predecir el comportamiento de copia frente a referencia
- [Modelado](reference/modelling.md): tipos `record`, pattern matching y switch expressions, interfaces con implementaciones por defecto, genéricos
- [Modismos](reference/idiom.md): métodos de extensión, LINQ, delegados y eventos, tipos de referencia anulables
- [Async](reference/async.md): el modelo de `Task`, la mecánica de `async`/`await`, los cancellation tokens, `IAsyncEnumerable`
- [Pruebas y build](reference/testing-and-build.md): xUnit/NUnit, mocking, la CLI `dotnet` y la gestión de proyectos y paquetes
- [Entregar el servicio](reference/shipping-the-service.md): routing y middleware de ASP.NET Core, inyección de dependencias, configuración, nociones básicas de Entity Framework Core
- [Criterio](reference/judgment.md): `async`/`await` frente a los hilos virtuales de Java, LINQ frente a la Stream API, revisar C# en busca de un hábito que simplemente compila

## Cómo funciona

Cada lección es corta y autocontenida. Las claves de respuesta están plegadas: primero recuerda, luego ábrelas. Las prácticas en el mundo real importan más que la lectura, y espaciarlas es el punto. Todo lo que siga sin estar claro al final de una lección merece rastrearse hasta su fuente primaria antes de seguir.
