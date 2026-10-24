---
title: Go
description: "Hazte cargo de Go en un equipo: diseña, entrega y opera un servicio en producción"
type: topic
---

# Aprendizaje: Go

Conviértete en el ingeniero en quien se confía para hacerse cargo de Go en un equipo: capaz de diseñar, entregar y operar un servicio Go en producción, de revisar el Go de otra persona y nombrar en concreto por qué un diseño está mal, y de reconocer cuándo un diseño importado de otro lenguaje está peleando contra Go en lugar de aprovecharlo.

**Última lección:** [0041. Probar contra una base de datos real](lessons/0041-testing-against-a-real-database.md)

## Cómo se ve el éxito

- Diseñar y entregar un servicio en producción: configuración, logging estructurado, apagado ordenado, health checks, acceso a base de datos.
- Depurar una data race y una fuga de goroutines en código que no escribiste, usando `-race` y `pprof`.
- Revisar la PR de un colega y decir con precisión por qué una interfaz, un receptor puntero o un canal es la herramienta equivocada ahí.
- Predecir lo que hace un programa concurrente antes de ejecutarlo, a partir del scheduler y del modelo de memoria y no de la experimentación.
- Reducir asignaciones con evidencia de `pprof` y `benchstat`, no a ojo.
- Diseñar la API de un paquete que puedas mantener compatible hacia atrás, y saber cuándo *no* recurrir a una goroutine.

## Restricciones

- No se asume experiencia previa con Go. La experiencia en otro lenguaje acorta las primeras etapas pero no es necesaria, y trae hábitos que Go castigará en silencio, porque aquí un instinto equivocado sigue compilando.
- Solo necesita la toolchain estándar en cualquier sistema operativo soportado. Nada hasta la etapa 5 requiere herramientas de pago, una cuenta en la nube ni una segunda máquina.
- Las prácticas son programas pequeños que caben en una sesión. Espaciarlas a lo largo de varios días es el mecanismo, no un inconveniente.
- El material sensible a la versión envejece rápido. Las afirmaciones sobre la versión actual se contrastan con las notas de la versión y no con libros.

## Fuera de alcance

- Otros lenguajes como temas propios. Las comparaciones aparecen solo donde impiden que un hábito se traslade a Go.
- Frameworks de terceros como temas propios: routers, ORM, contenedores de inyección de dependencias, toolkits de CLI. La biblioteca estándar cubre directamente el routing, el logging estructurado y el acceso a base de datos, así que las lecciones se construyen sobre ella; cuando un equipo ya ha elegido un framework, juzgar si se gana su sitio es una habilidad de revisión y pertenece a la etapa 6.
- Frontend, WASM y destinos móviles.
- Kubernetes e infraestructura más allá de lo que un servicio Go necesita para ejecutarse. Meter el binario en una imagen de contenedor, y ejecutar, asegurar y depurar ese contenedor, corresponde a [`infrastructure/containers`](../../infrastructure/containers/). Ejecutarlo en un clúster, incluido lo que hace el clúster con sus health checks y su señal de apagado, corresponde a [`infrastructure/kubernetes`](../../infrastructure/kubernetes/).
- Los detalles internos del compilador y del runtime más allá del punto en que dejan de predecir el comportamiento del programa.

## El arco

Siete etapas, desde ningún conocimiento previo hasta el criterio de un perfil sénior. No es una lista de lecciones: una etapa abarca varias lecciones y los límites son difusos.

| Etapa | Lecciones | Cubre | Terminada cuando |
|---|---|---|---|
| 1. Fundamentos | 0001 a 0007 | Tipos, valores cero, semántica de valor frente a puntero, mecánica de slices y maps incluido el aliasing, strings frente a runes frente a bytes, nociones básicas de paquetes | Puedes predecir el aliasing y el comportamiento de copia sin ejecutar el código |
| 2. Modismos | 0008 a 0014 | Errores como valores, envolver con `%w`, `errors.Is`/`As`, satisfacción implícita de interfaces, interfaces pequeñas, embedding de structs, estructura y nombres de paquetes | Escribes Go que un revisor no describiría como "Java con sintaxis de Go" |
| 3. Concurrencia | 0015 a 0021 | Goroutines, canales, `select`, primitivas de `sync`, cancelación con `context`, `errgroup`, el detector de races, el modelo de memoria, patrones de fugas | Puedes encontrar una fuga y una race en código desconocido y explicar la garantía que se violó |
| 4. Producción | 0022 a 0027 | Servicios HTTP, configuración, `slog`, apagado ordenado, health checks, acceso a base de datos, genéricos donde se ganan su sitio | Has estructurado un servicio que sobrevive a ser operado; la etapa 7 lo completa con métricas, trazado y pruebas alrededor de los handlers y de la base de datos, no solo alrededor de funciones |
| 5. Rendimiento y herramientas | 0028 a 0033 | Pruebas dirigidas por tablas, fuzzing, benchmarks, `pprof`, análisis de escape, reducción de asignaciones, módulos y versionado, builds de release | Optimizas a partir de un perfil y demuestras la mejora con `benchstat` |
| 6. Criterio | 0034 a 0037 | Diseño de APIs y compatibilidad, cuándo *no* usar una goroutine, revisión, leer el código fuente de la stdlib para encontrar respuestas | Se confía en ti para tomar la decisión y explicársela a otra persona |
| 7. Observabilidad y pruebas en producción | 0038 a 0041 | Middleware y valores con ámbito de petición, métricas y trazado (RED/USE, OpenTelemetry), probar un handler HTTP, pruebas de integración contra una base de datos real | Entregas un servicio con la tercera y la cuarta señal que la etapa 4 dejó a medias: métricas, trazado y pruebas alrededor de los handlers y de la base de datos, no solo alrededor de funciones |

## Lecciones

Recórrelas en orden.

| # | Lección | Enseña |
|---|---|---|
| [0001](lessons/0001-values-and-the-zero-value.md) | Valores y el valor cero | Toda variable declarada ya se puede usar, y nil es un valor y no una ausencia |
| [0002](lessons/0002-value-semantics-and-pointers.md) | Semántica de valor y punteros | Cada asignación y cada argumento es una copia, y un puntero es la forma de salirte de eso |
| [0003](lessons/0003-slices-and-the-backing-array.md) | Slices y el array subyacente | Un slice es una cabecera de tres palabras sobre un array que puede que otro también esté sosteniendo |
| [0004](lessons/0004-maps-and-their-rules.md) | Maps y sus reglas | Comma-ok, elementos no direccionables, iteración aleatorizada y el error fatal que lanza un map compartido |
| [0005](lessons/0005-strings-bytes-and-runes.md) | Strings, bytes y runes | Un string son bytes UTF-8 inmutables, así que len no es un recuento de caracteres e indexar no da un carácter |
| [0006](lessons/0006-methods-and-method-sets.md) | Métodos y conjuntos de métodos | El receptor que eliges decide qué tipos satisfacen una interfaz, no solo quién puede mutar |
| [0007](lessons/0007-packages-and-modules.md) | Paquetes y módulos | Un directorio es un paquete, una letra mayúscula es todo el sistema de visibilidad, e internal se hace cumplir |
| [0008](lessons/0008-errors-are-values.md) | Los errores son valores | error es una interfaz corriente, así que los fallos son datos que manejas y no un flujo de control que se escapa |
| [0009](lessons/0009-wrapping-is-and-as.md) | Envolver, Is y As | %w construye una cadena, Is y As la recorren, y envolver es un compromiso de la API |
| [0010](lessons/0010-defer-panic-and-recover.md) | defer, panic y recover | Los argumentos se congelan en la sentencia defer, y panic es para bugs y no para fallos |
| [0011](lessons/0011-implicit-interfaces.md) | Las interfaces se satisfacen implícitamente | El consumidor declara la interfaz, la implementación nunca la menciona, y lo pequeño es lo que se busca |
| [0012](lessons/0012-the-nil-interface-trap.md) | La trampa de la interfaz nil | Una interfaz contiene un tipo y un valor, así que un puntero nil dentro de ella no es una interfaz nil |
| [0013](lessons/0013-embedding-is-not-inheritance.md) | El embedding no es herencia | La promoción parece herencia hasta que un método embebido se niega a llamar a tu sobrescritura |
| [0014](lessons/0014-designing-a-package.md) | Diseñar un paquete | Comentarios de documentación, una superficie exportada pequeña y una flecha de dependencias que apunta en un solo sentido |
| [0015](lessons/0015-goroutines-and-what-they-cost.md) | Las goroutines y lo que cuestan | Lo bastante baratas como para arrancar miles, nunca tan gratis como para arrancar una sin un plan para detenerla |
| [0016](lessons/0016-channels.md) | Canales | Sin buffer significa punto de encuentro, cerrar es una difusión y solo el emisor puede cerrar |
| [0017](lessons/0017-select-and-timeouts.md) | select y timeouts | Esperar en varios canales a la vez, elegir al azar entre los que están listos y desactivar un caso con nil |
| [0018](lessons/0018-context-cancellation.md) | context y la cancelación | Un único valor que lleva un plazo y una señal de parada a lo largo de cada llamada que toca |
| [0019](lessons/0019-sync-primitives.md) | sync y errgroup | Cuándo compartir memoria es mejor que pasarla, y las cuatro primitivas que cubren casi todo |
| [0020](lessons/0020-memory-model-and-races.md) | El modelo de memoria y las races | Una data race es comportamiento indefinido, no un lanzamiento de moneda, y el detector solo ve lo que se ejecuta |
| [0021](lessons/0021-goroutine-leaks.md) | Fugas de goroutines | Una goroutine bloqueada para siempre nunca se recolecta, y tampoco nada de lo que retiene |
| [0022](lessons/0022-an-http-server.md) | Un servidor HTTP que valga la pena operar | Handlers, patrones de routing y los cuatro timeouts que el servidor por defecto no fija |
| [0023](lessons/0023-configuration-and-startup.md) | Configuración y arranque | Un main que solo conecta piezas, una función run que devuelve un error y validación antes de la primera petición |
| [0024](lessons/0024-structured-logging-with-slog.md) | Logging estructurado con slog | Atributos clave-valor, un único logger pasado como dependencia y niveles que puedes cambiar sin un despliegue |
| [0025](lessons/0025-graceful-shutdown.md) | Apagado ordenado y salud | Captar la señal, dejar de aceptar, drenar el trabajo en curso y luego cerrar las dependencias en orden |
| [0026](lessons/0026-talking-to-a-database.md) | Hablar con una base de datos | sql.DB es un pool, cada llamada recibe un context, y un Rows sin cerrar retiene una conexión |
| [0027](lessons/0027-generics-that-earn-their-keep.md) | Genéricos que se ganan su sitio | Los parámetros de tipo eliminan la duplicación entre tipos, y una interfaz sigue siendo la respuesta correcta para el comportamiento |
| [0028](lessons/0028-table-driven-tests.md) | Pruebas dirigidas por tablas | Una función de prueba, un slice de casos, subtests que se nombran solos y fallan de forma independiente |
| [0029](lessons/0029-fuzzing.md) | Fuzzing | Enunciar una propiedad que siempre debe cumplirse y dejar que la toolchain busque la entrada que la rompe |
| [0030](lessons/0030-benchmarks-you-can-trust.md) | Benchmarks en los que puedes confiar | b.Loop, ejecuciones repetidas y benchstat, porque un número de una sola ejecución no es una medición |
| [0031](lessons/0031-reading-a-pprof-profile.md) | Leer un perfil de pprof | Averiguar adónde van realmente el tiempo y la memoria antes de cambiar una sola línea |
| [0032](lessons/0032-escape-analysis-and-allocation.md) | Análisis de escape y asignación | Por qué un valor acaba en el heap, cómo preguntárselo al compilador y qué correcciones compensan de verdad |
| [0033](lessons/0033-modules-and-release-builds.md) | Módulos y builds de release | Minimal version selection, la regla de la ruta v2 y las opciones que hacen reproducible un binario |
| [0034](lessons/0034-api-design-and-compatibility.md) | Diseño de APIs y compatibilidad | Lo que puedes añadir sin romper a quienes llaman, y los tres cambios que siempre rompen |
| [0035](lessons/0035-when-not-to-use-a-goroutine.md) | Cuándo no usar una goroutine | La concurrencia es una estructura, no una aceleración, y la versión secuencial es a menudo la respuesta correcta |
| [0036](lessons/0036-reviewing-go.md) | Revisar Go | Deja que las herramientas encuentren el estilo y dedica tu atención al ciclo de vida, a los límites y a lo que el compilador no puede comprobar |
| [0037](lessons/0037-reading-the-standard-library.md) | Leer la biblioteca estándar | El código fuente está en tu máquina, zanja discusiones que la documentación no puede y es la referencia de estilo |
| [0038](lessons/0038-middleware-and-request-scoped-values.md) | Middleware y valores con ámbito de petición | La lección 22 mostró un middleware escribiendo un valor en el context; esta lección es la otra mitad, leerlo de vuelta de forma segura, y el mecanismo que aquel ejemplo nunca necesitó, un middleware que decide no llamar en absoluto al siguiente handler |
| [0039](lessons/0039-metrics-and-tracing.md) | Métricas y trazado | pprof perfila en local la CPU y la memoria de un único proceso; las métricas y el trazado son las dos señales de producción que responden a otro par de preguntas, cómo va el servicio ahora mismo en conjunto y qué le pasó a esta petición concreta en cada servicio que tocó |
| [0040](lessons/0040-testing-an-http-handler.md) | Probar un handler HTTP | La lección 22 mencionó de pasada que un ResponseRecorder hace que un handler se pueda probar sin red; esta lección concreta esa afirmación, por qué la costura de la interfaz es lo que lo hace posible, y la herramienta distinta, fácil de confundir, para probar un cliente en lugar de un handler |
| [0041](lessons/0041-testing-against-a-real-database.md) | Probar contra una base de datos real | Este es el cierre de la etapa 7: testing.Short() deja una prueba lenta de base de datos fuera del bucle local rápido, una transacción iniciada y nunca confirmada le da a cada prueba un punto de partida limpio y aislado, y una prueba de integración por fin ejercita juntos el middleware, un handler y una base de datos real |

## Referencia

- [Glosario](GLOSSARY.md): términos canónicos de este tema
- [Recursos](RESOURCES.md): fuentes de confianza, cada una anotada con lo que cubre
- [Slices y maps](reference/slice-and-map-mechanics.md): aliasing, capacidad y las operaciones que provocan panic
- [Manejo de errores](reference/error-handling.md): verbos de envoltura, funciones de comparación y las trampas que compilan
- [Patrones de concurrencia](reference/concurrency-patterns.md): reglas de los canales, constructores de context, lista de comprobación de fugas
- [Comandos de la toolchain](reference/toolchain-commands.md): opciones de pruebas, benchmarks, perfiles y builds de release
- [Lista de comprobación de revisión](reference/review-checklist.md): lo que detectan las herramientas y lo que tienes que detectar tú

## Cómo funciona

Cada lección es corta y autocontenida. Las claves de respuesta están plegadas: primero recuerda, luego ábrelas. Las prácticas en el mundo real importan más que la lectura, y espaciarlas es el punto. Todo lo que siga sin estar claro al final de una lección merece rastrearse hasta su fuente primaria antes de seguir.
