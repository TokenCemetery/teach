---
title: Java
description: "Hazte cargo de un servicio en Java: modélalo en Java moderno y luego opera lo que la JVM hace con él"
type: topic
---

# Aprendizaje: Java

Conviértete en el ingeniero en quien se confía para hacerse cargo de un servicio en Java dentro de un equipo: capaz de modelar un dominio en Java moderno y no en las jerarquías de herencia que el lenguaje solía exigir, de razonar sobre la concurrencia a partir del modelo de memoria y no de la experimentación, de leer un perfil y un log de recolección de basura hasta llegar a una decisión, y de revisar el Java de otra persona y nombrar en concreto lo que le está costando una abstracción.

**Empieza aquí:** [0001. Las referencias son valores](lessons/0001-references-are-values.md)
**Última lección:** [0052. Reflexión y anotaciones](lessons/0052-reflection-and-annotations.md)

## Cómo se ve el éxito

- Predecir lo que hacen la igualdad de referencias, un `hashCode` roto y un campo mutable compartido, antes de ejecutar el código.
- Modelar un dominio con records, sealed interfaces y enums, y decir por qué una jerarquía de herencia habría sido peor.
- Decir lo que garantiza cada uno de `synchronized`, `volatile` y una colección concurrente, con el vocabulario del modelo de memoria de Java.
- Usar hilos virtuales donde compensan, y nombrar lo que todavía bloquea un hilo portador.
- Leer un log de recolección de basura y un perfil, y luego dimensionar un heap a partir de esa evidencia y no de un valor por defecto.
- Entregar un build que otra persona pueda ejecutar: dependencias declaradas, una batería de pruebas, un artefacto ejecutable.
- Revisar una pull request y decir con precisión por qué una jerarquía de clases, una excepción comprobada o una cadena de streams es la herramienta equivocada ahí.
- Zanjar una discusión sobre el lenguaje a partir de la especificación y del JEP que introdujo la funcionalidad.

## Restricciones

- No se asume experiencia previa con Java. La experiencia en otro lenguaje acorta las primeras etapas pero no es necesaria, y trae hábitos que Java castiga en silencio: un getter para cada campo, una interfaz con una sola implementación, una clase donde un record lo diría mejor.
- La base es la versión actual con soporte a largo plazo. Cada funcionalidad del lenguaje se presenta junto con la versión en la que llegó, porque el código Java se lee a lo largo de muchas versiones y el "Java moderno" envejece.
- Solo necesita un JDK y una terminal en cualquier sistema operativo soportado. Un IDE ayuda pero nunca es obligatorio, y nada en el arco requiere herramientas de pago ni una cuenta en la nube.
- La mayoría de las prácticas son programas pequeños que caben en una sesión. La etapa 6 es la excepción: un perfil necesita un programa que se ejecute el tiempo suficiente como para perfilarlo.
- Las afirmaciones sensibles a la versión se contrastan con la especificación, la documentación de la API y el índice de JEP y no con un libro, porque la cadencia de publicación de seis meses deja atrás a todos los libros de la lista.

## Fuera de alcance

- Frameworks como temas propios: Spring, Jakarta EE, Quarkus, Hibernate. Juzgar si un framework se gana su sitio es una habilidad de revisión y pertenece a la etapa 7.
- Otros lenguajes de la JVM: Kotlin, Scala, Clojure, Groovy.
- Android y, en general, los destinos móviles.
- La comparación de herramientas de build. El arco enseña las tareas que tiene que realizar un build y usa una herramienta para realizarlas, en lugar de discutir cuál.
- Los detalles internos de la JVM más allá del punto en que dejan de predecir el comportamiento del programa: la implementación del JIT, la ingeniería de bytecode, escribir un recolector de basura.
- Kubernetes e infraestructura más allá de lo que un servicio necesita para ejecutarse. Meter el artefacto ejecutable en una imagen de contenedor, y ejecutar, asegurar y depurar ese contenedor, corresponde a [`infrastructure/containers`](../../infrastructure/containers/). Ejecutarlo en un clúster corresponde a [`infrastructure/kubernetes`](../../infrastructure/kubernetes/).

## El arco

Siete etapas, desde ningún conocimiento previo hasta el criterio de un perfil sénior. No es una lista de lecciones: una etapa abarca varias lecciones y los límites son difusos.

| Etapa | Lecciones | Cubre | Terminada cuando |
|---|---|---|---|
| 1. Fundamentos | 0001 a 0006 | Primitivos y referencias, `null`, los strings y su pool, arrays, el framework de colecciones, `equals` y `hashCode`, `Comparable` | Puedes predecir la identidad frente a la igualdad y el aliasing sin ejecutar el código |
| 2. Modelado | 0007 a 0014 | Clases e interfaces, records, tipos sealed, enums, genéricos y borrado de tipos, pattern matching, la inmutabilidad por defecto | Modelas un dominio sin recurrir primero a la herencia |
| 3. Modismos y la biblioteca | 0015 a 0021 | Las excepciones y qué hacer con las comprobadas, `Optional`, streams y collectors, iteración, archivos y E/S, la API de tiempo, text blocks | Escribes Java que un revisor no describiría como poco idiomático |
| 4. Concurrencia | 0022 a 0028 | Hilos, el modelo de memoria, `synchronized` y `volatile`, `java.util.concurrent`, executors, hilos virtuales, concurrencia estructurada, las trampas | Puedes nombrar la garantía que violó un programa concurrente roto |
| 5. Pruebas y build | 0029 a 0035 | JUnit 6, pruebas parametrizadas, dobles de prueba y cuándo no usarlos, declaración de dependencias, un artefacto ejecutable reproducible | Otra persona puede clonarlo, compilarlo, probarlo y ejecutarlo |
| 6. El runtime | 0036 a 0042 | Áreas de memoria, disposición de los objetos y análisis de escape, recolectores de basura y sus compromisos, leer un log del GC, JMH, profiling, reducción de asignaciones | Optimizas a partir de un perfil y demuestras la mejora con un benchmark fiable |
| 7. Criterio | 0043 a 0049 | Diseño de APIs y compatibilidad hacia atrás, deprecación, revisión, leer la especificación y los JEP para encontrar respuestas | Se confía en ti para tomar la decisión y explicársela a otra persona; la etapa 8 lo completa con el mecanismo, reflexión y anotaciones, a partir del cual se construyó en realidad cada framework juzgado |
| 8. Módulos y reflexión | 0050 a 0052 | El sistema de módulos, `module-info.java`, `requires` y `exports`, la encapsulación fuerte, las imágenes de runtime de `jlink` y `jpackage`, reflexión y anotaciones | Declaras un límite de módulo de forma deliberada, entregas una imagen de runtime construida a partir de él y lees lo que toca realmente la reflexión de un framework antes de juzgar si se gana su sitio |

## Lecciones

Recórrelas en orden.

| # | Lección | Enseña |
|---|---|---|
| [0001](lessons/0001-references-are-values.md) | Las referencias son valores | Una variable contiene un primitivo o una referencia, y cada asignación y cada argumento copia eso |
| [0002](lessons/0002-identity-and-equality.md) | Identidad e igualdad | == compara referencias, así que responde a una pregunta distinta para los strings y los números en caja |
| [0003](lessons/0003-equals-and-hashcode.md) | El contrato de equals y hashCode | Rompe el contrato y una colección hash pierde tu objeto sin lanzar nada |
| [0004](lessons/0004-null.md) | null y de dónde viene | null es una referencia que no apunta a nada, y la solución es rechazarlo en el límite |
| [0005](lessons/0005-arrays-and-collections.md) | Arrays y colecciones | Los arrays son covariantes y de tamaño fijo, y tres fábricas de listas difieren de formas que sus nombres ocultan |
| [0006](lessons/0006-comparable-and-comparator.md) | Comparable y Comparator | Una colección ordenada usa el orden y no equals, así que un comparador inconsistente pierde datos |
| [0007](lessons/0007-classes-and-objects.md) | Clases y objetos | Una clase es una plantilla de estado y comportamiento, y cada campo empieza con un valor por defecto que no escribiste |
| [0008](lessons/0008-records.md) | Records | Un portador transparente de datos inmutables, con el constructor, los accesores, equals, hashCode y toString derivados de la cabecera |
| [0009](lessons/0009-interfaces.md) | Interfaces | Un contrato sin estado, más los métodos default que permiten ampliarlo sin romper a todos sus implementadores |
| [0010](lessons/0010-inheritance-and-composition.md) | Herencia y composición | Lo que te da realmente extends, y por qué la respuesta suele ser un campo en lugar de una superclase |
| [0011](lessons/0011-sealed-types-and-pattern-matching.md) | Tipos sealed y pattern matching | Un conjunto cerrado de alternativas, y un compilador que comprueba que las manejaste todas |
| [0012](lessons/0012-enums.md) | Enums | Un conjunto fijo de instancias que garantiza el lenguaje, con espacio para estado y comportamiento en cada una |
| [0013](lessons/0013-generics-and-erasure.md) | Genéricos y borrado de tipos | Parámetros de tipo que el compilador comprueba y el runtime olvida, y los comodines que los hacen utilizables |
| [0014](lessons/0014-immutability-as-a-default.md) | La inmutabilidad por defecto | Haz que el objeto sea imposible de cambiar y la mayoría de las preguntas difíciles dejan de plantearse |
| [0015](lessons/0015-exceptions.md) | Excepciones | Qué fallos pertenecen a una firma, cuáles a una traza de pila, y una limpieza que sobrevive a ambos |
| [0016](lessons/0016-optional.md) | Optional | Un tipo de retorno que hace de la ausencia parte del contrato, y los cuatro lugares a los que no pertenece |
| [0017](lessons/0017-streams.md) | Streams | Un pipeline que describe trabajo, no hace nada de él hasta que se le pide y solo se le puede pedir una vez |
| [0018](lessons/0018-collectors.md) | Collectors | Convertir un pipeline de nuevo en un contenedor, y los tres collectors que lanzan excepciones donde no lo esperas |
| [0019](lessons/0019-files-and-paths.md) | Archivos y rutas | Rutas que no son strings, streams que hay que cerrar y un charset que por fin es un valor por defecto que vale la pena tener |
| [0020](lessons/0020-dates-and-times.md) | Fechas y horas | Cuál de los seis tipos de tiempo querías decir realmente, y los tres que no son un punto en el tiempo |
| [0021](lessons/0021-strings-and-text.md) | Strings y texto | Text blocks, el formateo que deberías usar y por qué la longitud no es el número de caracteres |
| [0022](lessons/0022-threads.md) | Hilos | Un hilo es una pila de llamadas planificada, y casi todos los errores de esta etapa empiezan por tratar uno como si fuera gratis |
| [0023](lessons/0023-the-memory-model.md) | El modelo de memoria | Por qué un valor escrito por un hilo puede no verlo nunca otro, y la regla exacta que lo corrige |
| [0024](lessons/0024-mutual-exclusion.md) | Exclusión mutua | Un hilo cada vez, las dos formas de decirlo y el deadlock que puedes encontrar antes de que ocurra |
| [0025](lessons/0025-concurrent-collections-and-atomics.md) | Colecciones concurrentes y atómicos | Las colecciones que sobreviven al acceso concurrente, y el comprobar y luego actuar que las derrota a todas |
| [0026](lessons/0026-executors-and-futures.md) | Executors y futures | Enviar trabajo en lugar de crear hilos, y encontrar la excepción que se tragó submit |
| [0027](lessons/0027-virtual-threads.md) | Hilos virtuales | Hilos lo bastante baratos como para bloquearse, y el hábito del pooling que ahora tienes que desaprender |
| [0028](lessons/0028-choosing-a-model.md) | Elegir un modelo | Una sola pregunta elige el modelo, y el fallo que tienes delante nombra la garantía que rompió |
| [0029](lessons/0029-your-first-test.md) | Tu primera prueba | Dónde viven las pruebas, qué hace realmente el runner y el esquema de versiones que todos los textos explican mal |
| [0030](lessons/0030-assertions-that-name-the-failure.md) | Aserciones que nombran el fallo | Una prueba que falla es un informe de bug, y la aserción que elegiste decide lo bueno que es ese informe |
| [0031](lessons/0031-parameterised-tests.md) | Pruebas parametrizadas | Un método de prueba, muchos casos, y el punto en el que un bucle dentro de una prueba deja de ser suficiente |
| [0032](lessons/0032-test-doubles.md) | Dobles de prueba | Cinco tipos de sustituto, cuándo un objeto real gana a todos ellos y lo que un mock deja de probar sin que se note |
| [0033](lessons/0033-declaring-dependencies.md) | Declarar dependencias | Coordenadas, scopes y el grafo transitivo, más la versión que llega sin que nadie la pida |
| [0034](lessons/0034-the-build-lifecycle.md) | El ciclo de vida del build | Fases y goals en lugar de comandos memorizados, y el wrapper que hace que el build sea igual en todas partes |
| [0035](lessons/0035-a-runnable-artifact.md) | Un artefacto ejecutable | Empaquetar lo que construiste para que alguien sin nada más que un JDK pueda ejecutarlo |
| [0036](lessons/0036-where-memory-goes.md) | Adónde va la memoria | Los cinco lugares donde la JVM pone memoria, y qué OutOfMemoryError nombra a cuál |
| [0037](lessons/0037-the-shape-of-an-object.md) | La forma de un objeto | Un objeto pequeño es sobre todo cabecera, y la opción que lo encoge está desactivada por defecto |
| [0038](lessons/0038-the-allocation-that-never-happened.md) | La asignación que nunca ocurrió | El análisis de escape puede eliminar por completo una asignación, y un solo almacenamiento en un campo la devuelve |
| [0039](lessons/0039-collectors-and-the-trade.md) | Los recolectores y el compromiso que estás haciendo | Cinco recolectores, un compromiso a tres bandas y por qué el valor por defecto suele ser la respuesta correcta |
| [0040](lessons/0040-reading-a-gc-log.md) | Leer un log de recolección de basura | Una línea de log dice cuánto se recolectó, cuánto tardó y si hay que preocuparse |
| [0041](lessons/0041-a-benchmark-you-can-trust.md) | Un benchmark en el que puedes confiar | Por qué miente el bucle de medición obvio, y la configuración del harness que en silencio no mide nada |
| [0042](lessons/0042-from-profile-to-proof.md) | Del perfil a la prueba | Grabar la ejecución, leer adónde fue el tiempo, cambiar una cosa y demostrar la mejora |
| [0043](lessons/0043-what-counts-as-breaking.md) | Qué cuenta como incompatible | Tres tipos de compatibilidad, y el cambio que es seguro para compilar contra él y fatal para ejecutar contra él |
| [0044](lessons/0044-designing-a-signature.md) | Diseñar una firma | Los tipos de los parámetros y de retorno deciden lo que pueden hacer quienes llaman, y la mayor parte del daño se hace en el límite |
| [0045](lessons/0045-evolving-a-type.md) | Hacer evolucionar un tipo sin romperlo | Cómo ampliar una interfaz, un record, un enum y una jerarquía sealed cuando ya hay gente que depende de ellos |
| [0046](lessons/0046-deprecation-that-works.md) | Una deprecación que funciona | Marcar algo como deprecado no cambia nada a menos que digas qué pasará después |
| [0047](lessons/0047-settling-it-from-the-source.md) | Zanjarlo desde la fuente | Dónde mirar cuando la discusión es sobre lo que hace Java, y qué documento responde a qué pregunta |
| [0048](lessons/0048-reviewing-java.md) | Revisar Java | Nombrar lo que cuesta una abstracción, en lugar de decir que da mala espina |
| [0049](lessons/0049-does-this-framework-earn-its-place.md) | ¿Se gana este framework su sitio? | El último juicio de la etapa 7, hecho a partir de las restricciones del servicio y no de las promesas del framework |
| [0050](lessons/0050-the-module-system.md) | El sistema de módulos | module-info.java sustituye al JAR como el límite que reconocen tanto el compilador como el runtime, requires y exports deciden qué lo cruza, y la encapsulación fuerte significa que una clase pública en un paquete no exportado es invisible fuera de su propio módulo |
| [0051](lessons/0051-runtime-images.md) | Imágenes de runtime | jlink ensambla una imagen de runtime a partir únicamente del cierre transitivo de los módulos con los que se le dice que empiece, pero solo a partir de módulos explícitos: una aplicación que depende aunque sea de un solo módulo automático no se puede enlazar en absoluto |
| [0052](lessons/0052-reflection-and-annotations.md) | Reflexión y anotaciones | Este es el cierre de la etapa 8: la reflexión lee y llama a la propia forma de una clase en tiempo de ejecución en lugar de en tiempo de compilación, una anotación es un dato inerte hasta que algo la lee mediante reflexión, y todos los frameworks fuera de alcance de este arco están construidos exactamente a partir de estos dos mecanismos |

## Referencia

- [Glosario](GLOSSARY.md): términos canónicos de este tema
- [Recursos](RESOURCES.md): fuentes de confianza, cada una anotada con lo que cubre
- [Igualdad, hashing y orden](reference/equality-hashing-and-ordering.md): los tres contratos, y qué comparación escribir
- [Modelado](reference/modelling.md): a qué construcción recurrir, a qué te compromete cada una y las reglas que es fácil recordar mal
- [Modismos y la biblioteca](reference/idiom-and-library.md): las decisiones sobre la biblioteca en las que se fija un revisor, y las trampas que lanzan excepciones donde nadie mira
- [Concurrencia](reference/concurrency.md): qué garantía da cada construcción, qué modelo encaja con la carga de trabajo y qué significa el síntoma que tienes delante
- [Pruebas y build](reference/testing-and-build.md): la tarea de build que realiza realmente cada comando, el doble al que recurrir y el fallo que significa que el artefacto está mal
- [El runtime](reference/the-runtime.md): adónde va la memoria, qué recolector responde a qué requisito y la medición que respalda una afirmación
- [Criterio](reference/judgment.md): qué cambios rompen qué, cómo retirar una API y cómo argumentar la decisión desde la fuente
- [El sistema de módulos](reference/the-module-system.md): la hoja de la etapa 8, con las tres condiciones para el acceso entre módulos, lo que hace cada directiva y dónde acaba el código de un jar

## Cómo funciona

Cada lección es corta y autocontenida. Las claves de respuesta están plegadas: primero recuerda, luego ábrelas. Las prácticas en el mundo real importan más que la lectura, y espaciarlas es el punto. Todo lo que siga sin estar claro al final de una lección merece rastrearse hasta su fuente primaria antes de seguir.
