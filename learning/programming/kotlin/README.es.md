---
title: Kotlin
description: "Hazte cargo de Kotlin en la JVM: null safety, corrutinas y Kotlin idiomático desde cero"
type: topic
---

# Aprendizaje: Kotlin

Conviértete en el ingeniero en quien se confía para hacerse cargo de Kotlin en un equipo, en un servicio backend o en una app Android: capaz de modelar un dominio de forma idiomática, de escribir y razonar sobre corrutinas y `Flow`, de entregar un servicio Kotlin o un componente Android tipado y probado, y de revisar el Kotlin de otra persona y nombrar en concreto lo que le está costando una construcción.

**Última lección:** [44. Probar corrutinas más allá de runTest](lessons/0044-testing-coroutines-beyond-runtest.md)

## Cómo se ve el éxito

- Modelar un dominio con data classes, sealed classes y enums, y saber cuándo la null safety, y no una excepción, es la señal correcta.
- Escribir y razonar sobre corrutinas y `Flow`, y comparar el modelo con los hilos virtuales de Java.
- Entregar un servicio backend Kotlin o un componente Android tipado y probado, diseñado de forma idiomática.
- Ante código Kotlin escrito con un hábito que simplemente compila (comprobaciones defensivas de null en lugar del sistema de tipos, un callback en lugar de una corrutina), nombrar el hábito y reescribirlo de forma idiomática.

## Restricciones

- No se asume experiencia previa con Kotlin. La experiencia en Java o en otro lenguaje de la JVM acorta las primeras etapas pero no es necesaria, y trae hábitos que Kotlin castiga en silencio: comprobaciones defensivas de null en lugar del sistema de tipos, una clase donde una data class o un tipo sealed lo diría mejor.
- Cubre tanto el contexto backend/de servidor como el de Android, tocando cada uno donde divergen.
- Solo necesita un JDK, la toolchain de Kotlin y una terminal; Android Studio solo donde el material específico de Android lo requiere.

## Fuera de alcance

- Los detalles internos de la JVM más allá de lo que explica el comportamiento compilado propio de Kotlin (ajuste completo del recolector de basura, profiling, ingeniería de bytecode): consulta [`programming/java`](../../programming/java/), enlazado para profundizar en lugar de volver a enseñarlo.
- Otros lenguajes de la JVM (Java, Scala, Clojure, Groovy) como temas propios, aunque aparece un contraste donde aclara un modismo de Kotlin.
- Kotlin Multiplatform: apuntar a JS, Native o Wasm, estructurar declaraciones `expect`/`actual` entre source sets y las diferencias de la stdlib específicas de cada plataforma que introducen esos destinos. Este arco es solo para la JVM de principio a fin, según el propio planteamiento de la misión; una lección sobre esto necesitaría su propia configuración de Gradle y su propio conjunto de modismos, no una lección de JVM con una nota al pie sobre multiplataforma. `kotlinx.serialization` (lección 38) es el único lugar donde se menciona el alcance multiplataforma, como razón documentada de una decisión de diseño del lado de la JVM, no como material multiplataforma en sí.

## El arco

Once etapas, desde ningún conocimiento previo hasta el criterio de un perfil sénior. No es una lista de lecciones: una etapa abarca varias lecciones y los límites son difusos.

| Etapa | Lecciones | Cubre | Terminada cuando |
|---|---|---|---|
| 1. Fundamentos | 0001 a 0006 | Null safety, `val`/`var` e inmutabilidad, valores frente a referencias, tipos básicos y string templates, nociones básicas de colecciones (`List`/`Set`/`Map`, mutables frente a de solo lectura), flujo de control (`when`, rangos, `for`) | Puedes predecir la nulabilidad y la mutabilidad sin ejecutar el código |
| 2. Modelado | 0007 a 0012 | Clases y propiedades, data classes, sealed classes y `when` exhaustivo, enums, declaraciones object y companion objects, interfaces con métodos por defecto | Modelas un dominio sin recurrir primero a una jerarquía de una clase por cosa |
| 3. Modismos | 0013 a 0018 | Funciones de extensión, scope functions (`let`/`run`/`with`/`apply`/`also`), funciones de orden superior y lambdas, funciones inline y genéricos reified, delegación (`by`), sobrecarga de operadores | Escribes Kotlin que un revisor no describiría como Java traducido |
| 4. Colecciones y secuencias | 0019 a 0021 | Los operadores de colecciones de Kotlin, `Sequence` perezosa frente a colecciones ansiosas, agrupar y plegar | Eliges entre un pipeline de colecciones y una secuencia y puedes defender el costo de cada uno |
| 5. Concurrencia | 0022 a 0027 | Hilos y nociones básicas del modelo de memoria de la JVM, funciones suspend y constructores de corrutinas, concurrencia estructurada, contexto de corrutina y dispatchers, `Flow`, cancelación y manejo de excepciones | Puedes predecir lo que hace un programa concurrente con corrutinas antes de ejecutarlo, y comparar el modelo con los hilos virtuales de Java |
| 6. Pruebas y build | 0028 a 0030 | Frameworks de pruebas de Kotlin, mocking, el Kotlin DSL de Gradle y la gestión de dependencias | Otra persona puede clonarlo, compilarlo, probarlo y ejecutarlo |
| 7. Entregar un servicio | 0031 a 0033 | Estructurar un servicio backend tipado y probado, modismos específicos de Android donde la plataforma diverge, genéricos y varianza (`in`/`out`) | Has estructurado un servicio backend Kotlin o un componente Android tipado y probado; la etapa 10 lo completa con una capa HTTP, configuración, logging y persistencia |
| 8. Criterio | 0034 a 0035 | Interoperabilidad con Java, revisar Kotlin y nombrar con precisión lo que cuesta una construcción | Se confía en ti para tomar la decisión y explicársela a otra persona |
| 9. Modismos avanzados | 0036 a 0039 | Builders con tipado seguro y DSL, `value class`/`@JvmInline`, `kotlinx.serialization`, `Result` y modismos de manejo de errores | Escribes de forma idiomática un pequeño DSL builder con tipado seguro, un tipo envoltorio sin costo y un camino de error basado en `Result` |
| 10. Completar el servicio | 0040 a 0043 | Una capa HTTP, configuración, logging y persistencia para el servicio backend Kotlin que la etapa 7 empezó a estructurar | Entregas un servicio backend Kotlin con una capa HTTP con routing, configuración externalizada, logging estructurado y acceso a base de datos, no solo un esqueleto estructurado |
| 11. Probar corrutinas más allá de runTest | 0044 | `cancelAndIgnoreRemainingEvents()` de Turbine para un flow que nunca termina, y lo que tiene que afirmar realmente una prueba de cancelación dado que la cancelación es cooperativa | Pruebas un flow infinito sin que se cuelgue, y pruebas la cancelación por su evidencia real y documentada y no solo por un flag de `Job` |

## Lecciones

Recórrelas en orden.

| # | Lección | Enseña |
|---|---|---|
| [0001](lessons/0001-null-safety.md) | Null safety | Llevar "¿podría esto ser null?" de una sorpresa en tiempo de ejecución a una pregunta en tiempo de compilación, y cómo el hábito de Java lo deshace |
| [0002](lessons/0002-val-var-and-immutability.md) | val/var e inmutabilidad | Por qué val es el valor por defecto que vale la pena defender, qué garantiza realmente (y qué no) y el hábito de Java de recurrir a var por reflejo |
| [0003](lessons/0003-values-vs-references.md) | Valores frente a referencias | Por qué == significa algo distinto en Kotlin que en Java, y el bug concreto que produce el hábito de Java de escribir == |
| [0004](lessons/0004-basic-types-and-string-templates.md) | Tipos básicos y string templates | Por qué Kotlin no tiene primitivos a nivel de lenguaje, y los string templates como funcionalidad del lenguaje y no como concatenación con sintaxis extra |
| [0005](lessons/0005-collections-basics.md) | Nociones básicas de colecciones | List, Set y Map como colecciones de solo lectura por interfaz, y por qué una colección mutable guardada en un val sigue siendo mutable |
| [0006](lessons/0006-control-flow.md) | Flujo de control | if y when como expresiones que producen valores, qué es realmente un rango y el cierre de la etapa 1 sobre predecir la nulabilidad y la mutabilidad sin ejecutar código |
| [0007](lessons/0007-classes-and-properties.md) | Clases y propiedades | Las propiedades como sustituto del código repetitivo de getters/setters de Java, y por qué la propia documentación de Kotlin dice que recurras a una clase en último lugar |
| [0008](lessons/0008-data-classes.md) | Data classes | Qué genera realmente data class, y la sutil regla de que solo las propiedades del constructor primario participan en todo ello |
| [0009](lessons/0009-sealed-classes-and-exhaustive-when.md) | Sealed classes y when exhaustivo | Cómo sellar una jerarquía convierte la exhaustividad de un when de una promesa manual en una garantía comprobada por el compilador |
| [0010](lessons/0010-enums.md) | Enums | Cada constante de un enum como un objeto real con su propio estado y comportamiento, y dónde exactamente encaja un enum mejor que una sealed class |
| [0011](lessons/0011-object-declarations-and-companion-objects.md) | Declaraciones object y companion objects | Singletons declarados, no implementados a mano, y los companion objects como el verdadero sustituto en Kotlin de los miembros static de Java |
| [0012](lessons/0012-interfaces-with-default-methods.md) | Interfaces con métodos por defecto | Por qué una interfaz de Kotlin puede implementar comportamiento pero nunca guardar estado, y cómo resolver explícitamente un conflicto en diamante |
| [0013](lessons/0013-extension-functions.md) | Funciones de extensión | Añadir comportamiento a un tipo sin herencia, y la sorpresa del despacho estático que hace tropezar a la gente la primera vez que se la encuentra |
| [0014](lessons/0014-scope-functions.md) | Scope functions | Elegir entre let, run, with, apply y also según lo que devuelve cada una y cómo expone el objeto, no por costumbre |
| [0015](lessons/0015-higher-order-functions-and-lambdas.md) | Funciones de orden superior y lambdas | Los tipos función como tipos reales, la sintaxis de lambda al final y el mecanismo de receptor sobre el que están construidas realmente las scope functions |
| [0016](lessons/0016-inline-functions-and-reified-generics.md) | Funciones inline y genéricos reified | Por qué inline existe para eliminar un costo real, por qué permite los returns no locales y por qué los parámetros de tipo reified solo funcionan gracias al inlining |
| [0017](lessons/0017-delegation.md) | Delegación | Implementar una interfaz reenviando a un objeto contenido sin código repetitivo, y comportamiento de propiedades reutilizable mediante by lazy y delegados personalizados |
| [0018](lessons/0018-operator-overloading.md) | Sobrecarga de operadores | Los operadores como funciones con nombre corrientes con una correspondencia fija de símbolos, y la verdadera disciplina de implementar uno solo donde significa lo que el símbolo ya significa |
| [0019](lessons/0019-collection-operators.md) | Operadores de colecciones | Los operadores de colecciones como funciones de extensión que devuelven de forma ansiosa una nueva colección, y el hábito de la Stream de Java que calcula mal el precio de una cadena de ellos |
| [0020](lessons/0020-sequences-and-laziness.md) | Secuencias y pereza | Por qué la misma cadena de operadores se comporta de forma distinta sobre una Sequence, para qué sirve realmente una operación terminal y cuándo la pereza cuesta más de lo que ahorra |
| [0021](lessons/0021-grouping-and-folding.md) | Agrupar y plegar | Agregar con fold y reduce, agrupar sin construir los grupos y el cierre de la etapa 4 sobre defender lo que cuesta un pipeline |
| [0022](lessons/0022-threads-and-the-memory-model.md) | Hilos y el modelo de memoria | Por qué Kotlin no tiene un modelo de memoria propio en la JVM, las tres construcciones que escribe como anotaciones en lugar de palabras clave y las dos garantías que un val no te da |
| [0023](lessons/0023-suspend-functions-and-coroutine-builders.md) | Funciones suspend y constructores de corrutinas | Qué cambia realmente suspend en una función, los tres constructores y lo que devuelve cada uno, y por qué el código que se suspende sigue leyéndose de arriba abajo |
| [0024](lessons/0024-structured-concurrency.md) | Concurrencia estructurada | El árbol de padres e hijos que hace predecible la cancelación, por qué un scope que posees es un scope que debes cancelar y lo que cuesta realmente GlobalScope |
| [0025](lessons/0025-coroutine-context-and-dispatchers.md) | Contexto de corrutina y dispatchers | El contexto como un conjunto de elementos combinados con plus, qué dispatcher corresponde a qué tipo de trabajo y el único elemento de contexto que rompe en silencio la concurrencia estructurada |
| [0026](lessons/0026-flows.md) | Flows | Un flow como la tercera opción asíncrona después de una lista y una secuencia, qué significa realmente frío para cada collector y la regla de contexto que un flow builder hace cumplir en tiempo de ejecución |
| [0027](lessons/0027-cancellation-and-exception-handling.md) | Cancelación y manejo de excepciones | Por qué la cancelación es cooperativa y qué hace que el código la ignore, por qué una CancellationException no es un fallo y cómo se compara el modelo de corrutinas con los hilos virtuales de Java |
| [0028](lessons/0028-test-frameworks.md) | Frameworks de pruebas | Las capas sobre las que se apoya realmente una prueba de Kotlin, por qué el tiempo virtual de runTest se detiene en el límite del dispatcher y lo que eso impone al diseño del código bajo prueba |
| [0029](lessons/0029-mocking.md) | Mocking | Por qué que todo sea final por defecto cambia lo que significa hacer mocking en Kotlin, qué hace MockK con las construcciones que no son métodos de un objeto y cuándo la finalidad te está diciendo que falta una costura |
| [0030](lessons/0030-gradle-and-dependency-management.md) | Gradle y la gestión de dependencias | Los accesores con tipado seguro del Kotlin DSL y dónde se acaban, por qué una configuración de Gradle no es un scope de Maven y la regla de resolución que decide qué versión llega al classpath |
| [0031](lessons/0031-structuring-a-service.md) | Estructurar un servicio | Dónde van realmente los archivos de Kotlin y qué va dentro de una clase, y las cuatro decisiones de etapas anteriores que deciden si un servicio se puede probar |
| [0032](lessons/0032-android-divergences.md) | Divergencias de Android | Los scopes que Android posee en tu nombre, la seguridad respecto al hilo principal como un contrato que mantiene la función llamada y por qué la vida de la composición no es la vida del ciclo de vida |
| [0033](lessons/0033-generics-and-variance.md) | Genéricos y varianza | Varianza en el punto de declaración en lugar de comodines, qué prometen realmente out e in sobre un parámetro de tipo y cómo leer una firma proyectada |
| [0034](lessons/0034-java-interop.md) | Interoperabilidad con Java | Por qué el límite es asimétrico, qué te cuesta un platform type y cómo saldar esa deuda, y qué anotaciones le debes a quien llama desde Java |
| [0035](lessons/0035-reviewing-kotlin.md) | Revisar Kotlin | Convertir el arco en un instrumento de revisión: el costo que esconde cada hábito, la forma de un comentario que lo nombra y lo que no hay que revisar |
| [0036](lessons/0036-type-safe-builders-and-dsls.md) | Builders con tipado seguro y DSL | La lección 15 enseñó el tipo función con receptor que permite que run y apply expongan this; un builder con tipado seguro es exactamente ese mecanismo anidado de forma recursiva, y @DslMarker es el único atributo que impide que un builder anidado alcance en silencio el receptor equivocado |
| [0037](lessons/0037-value-classes.md) | value class y @JvmInline | Una value class es la solución a la obsesión por los primitivos que la JVM normalmente te deja tener gratis, representada como su propio valor subyacente sin ningún objeto envoltorio, salvo en los casos concretos y documentados en los que el compilador todavía tiene que hacer boxing |
| [0038](lessons/0038-kotlinx-serialization.md) | kotlinx.serialization | Un hábito de Java recurre a una biblioteca que inspecciona la forma de una clase mediante reflexión en tiempo de ejecución; kotlinx.serialization genera esa misma lógica en tiempo de compilación mediante un plugin del compilador, que es exactamente lo que le permite funcionar en destinos de Kotlin que no tienen ninguna API de reflexión en tiempo de ejecución |
| [0039](lessons/0039-result-and-error-handling.md) | Result y modismos de manejo de errores | runCatching envuelve cualquier Throwable en un Result, que es exactamente el problema dentro de una corrutina, ya que la cancelación cooperativa de la lección 27 depende de que la CancellationException se propague sin capturar, y runCatching se la traga como un fallo corriente salvo que quien llama la vuelva a lanzar explícitamente antes |
| [0040](lessons/0040-http-layer.md) | Capa HTTP | La lección 31 dejó a propósito el routing para el framework que eligieras; el propio bloque de routing de Ktor resulta ser el DSL builder con tipado seguro de la lección 36 aplicado a HTTP, sin nada instalado por defecto y con una extracción de parámetros de la petición que falla de forma ruidosa en lugar de enlazar en silencio lo que no es |
| [0041](lessons/0041-configuration.md) | Configuración | El comportamiento real de un servicio, su puerto, la URL de su base de datos, sus secretos, tiene que cambiar entre entornos sin recompilar una sola línea, y el archivo de configuración de Ktor más un modismo de sustitución concreto y fácil de pasar por alto es la forma en que un valor por defecto y una sobrescritura por entorno viven exactamente en un solo lugar |
| [0042](lessons/0042-logging.md) | Logging | SLF4J no hace nada en silencio hasta que se añade como dependencia un backend de logging real, y los valores MDC por petición de CallLogging son invisibles en silencio hasta que se actualiza el propio patrón del log para imprimirlos: la misma forma de trampa aparece dos veces en la misma lección |
| [0043](lessons/0043-persistence.md) | Persistencia | El DSL de Exposed es otro builder con tipado seguro, y por debajo es mayormente bloqueante, ya que envuelve JDBC; el cierre de la etapa 10 consiste en despachar correctamente ese trabajo bloqueante en lugar de paralizar el hilo que estuviera ejecutando la petición, y en revisar lo que el servicio entregado en la etapa 7 necesitaba realmente desde el principio |
| [0044](lessons/0044-testing-coroutines-beyond-runtest.md) | Probar corrutinas más allá de runTest | La lección 28 enseñó awaitItem de Turbine y el bloqueo que provoca si nada lo termina; esta lección cubre la herramienta concreta para un flow que nunca termina por sí solo, y lo que tiene que afirmar realmente una prueba de cancelación, dado que la cancelación es cooperativa y no lo actualiza todo en el instante en que se llama a cancel() |

## Referencia

- [Glosario](GLOSSARY.md): términos canónicos de este tema
- [Recursos](RESOURCES.md): fuentes de confianza
- [Null safety y mutabilidad](reference/null-safety-and-mutability.md): null safety, `val`/`var`, valores frente a referencias, predecir la nulabilidad y la mutabilidad
- [Modelado](reference/modelling.md): data classes, sealed classes y `when` exhaustivo, declaraciones object y companion objects, interfaces con métodos por defecto
- [Modismos](reference/idiom.md): funciones de extensión, scope functions (`let`/`run`/`with`/`apply`/`also`), delegación (`by`), sobrecarga de operadores
- [Colecciones y secuencias](reference/collections-and-sequences.md): los operadores de colecciones de Kotlin, `Sequence` perezosa frente a colecciones ansiosas, agrupar y plegar
- [Concurrencia](reference/concurrency.md): funciones suspend y constructores de corrutinas, concurrencia estructurada, contexto de corrutina y dispatchers, `Flow`, comparación con los hilos virtuales de Java
- [Pruebas y build](reference/testing-and-build.md): frameworks de pruebas de Kotlin, mocking, el Kotlin DSL de Gradle y la gestión de dependencias
- [Entregar un servicio](reference/shipping-a-service.md): estructurar un backend tipado y probado, modismos específicos de Android, genéricos y varianza
- [Criterio](reference/judgment.md): interoperabilidad con Java, revisar Kotlin y nombrar con precisión lo que cuesta una construcción

## Cómo funciona

Cada lección es corta y autocontenida. Las claves de respuesta están plegadas: primero recuerda, luego ábrelas. Las prácticas en el mundo real importan más que la lectura, y espaciarlas es el punto. Todo lo que siga sin estar claro al final de una lección merece rastrearse hasta su fuente primaria antes de seguir.
