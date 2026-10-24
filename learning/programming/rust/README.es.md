---
title: Rust
description: "Hazte cargo de Rust: diseña con ownership en lugar de pelearte con el borrow checker, y luego publica el crate"
type: topic
---

# Aprendizaje: Rust

Conviértete en el ingeniero en quien se confía para hacerse cargo de Rust en un equipo: capaz de diseñar con ownership en lugar de negociar con el borrow checker, de dar forma a los errores y a las APIs para que los tipos lleven los invariantes, de recurrir a `unsafe` solo detrás de un límite que se pueda justificar, y de publicar un crate del que otras personas dependan y que puedan actualizar.

**Empieza aquí:** [0001. Ownership y drop](lessons/0001-ownership-and-drop.md)
**Última lección:** [0067. Pruebas basadas en propiedades y pruebas de snapshot](lessons/0067-property-based-and-snapshot-testing.md)

## Cómo se ve el éxito

- Predecir qué préstamo rechazará el compilador, y por qué, antes de compilar.
- Elegir entre poseer, tomar prestado, conteo de referencias y mutabilidad interior a partir de cuánto tiempo tienen que vivir realmente los datos.
- Diseñar un tipo de error que quien llama pueda manejar, y decir cuándo hacer panic es en cambio la elección correcta.
- Eliminar la duplicación con traits y genéricos sin volver ilegibles las firmas, y saber cuándo el despacho dinámico es la mejor respuesta.
- Escribir código async que no se atasque, y explicar qué provoca mantener un lock a través de un punto `await`.
- Justificar cada bloque `unsafe` por el invariante que mantiene, mantenerlo detrás de una interfaz segura y comprobarlo con una herramienta y no leyendo.
- Publicar un crate con documentación, pruebas y una API pública que puedas hacer evolucionar sin romper a quienes dependen de ella.
- Revisar Rust y nombrar con precisión por qué una anotación de lifetime, un `clone` o un mutex compartido está tapando un problema de diseño.

## Restricciones

- No se asume experiencia previa con Rust ni formación en programación de sistemas. La pila, el heap y la disposición en memoria se enseñan dentro del arco, porque sin ellos el ownership no se puede enseñar.
- Solo necesita la toolchain estable y una terminal en cualquier sistema operativo soportado. Nada en el arco requiere herramientas de pago, una cuenta en la nube ni Rust nightly.
- **Se espera que las prácticas no compilen.** Ese es el bucle de feedback, no un contratiempo: predice lo que dirá el compilador, luego compruébalo, y trata la diferencia como la lección.
- Las prácticas son programas pequeños que caben en una sesión. Espaciarlas a lo largo de varios días es el mecanismo, no un inconveniente.
- Las ediciones y las versiones importan aquí. Donde una lección depende de una edición o de una funcionalidad estabilizada, dice cuál, y las afirmaciones sensibles a la versión se contrastan con las notas de la versión en lugar de recordarse de memoria.

## Fuera de alcance

- Los destinos embebidos y `no_std` como temas propios.
- WebAssembly, interfaces gráficas y motores de videojuegos.
- Los frameworks web como temas. Async necesita ejemplos, y se mantienen tan pequeños como lo permite el concepto.
- Escribir macros procedurales. Las macros declarativas aparecen donde hay que leer el uso que hace de ellas la propia biblioteca estándar.
- Las interfaces de funciones externas más allá de lo que necesita el material sobre el límite de `unsafe`. Envolver una biblioteca de C real es una tarea aparte.
- Los detalles internos del compilador y del borrow checker más allá del punto en que dejan de predecir lo que aceptará el compilador.

## El arco

Ocho etapas, desde ningún conocimiento previo hasta el criterio de un perfil sénior. No es una lista de lecciones: una etapa abarca varias lecciones y los límites son difusos.

| Etapa | Lecciones | Cubre | Terminada cuando |
|---|---|---|---|
| 1. Ownership | 0001 a 0006 | Valores, pila y heap, moves, `Copy`, préstamos y sus reglas, slices, `String` frente a `&str`, shadowing | Puedes predecir un error de move o de préstamo antes de que lo informe el compilador |
| 2. Datos y control | 0007 a 0013 | Structs, enums, `Option` y `Result`, pattern matching y exhaustividad, iteradores, closures, las colecciones que vale la pena conocer | Modelas con enums, y manejas la ausencia sin recurrir a `unwrap` |
| 3. Errores y forma de la API | 0014 a 0020 | Propagación con `?`, tipos de error personalizados, conversiones `From`, panic frente a error, módulos y visibilidad, escribir documentación que compila | Escribes una biblioteca cuyos fallos puede manejar realmente quien la llama |
| 4. Traits, genéricos y lifetimes | 0021 a 0028 | Trait bounds, tipos asociados, genéricos frente a despacho dinámico, la regla del huérfano, anotaciones de lifetime y elisión, por qué un lifetime no es una duración | Lees un error de lifetime como información y no como un obstáculo |
| 5. Compartir e hilos | 0029 a 0036 | `Box`, `Rc` y `Arc`, `RefCell` y `Mutex`, `Send` y `Sync`, hilos, canales, deadlock y envenenamiento | Eliges una estrategia para compartir a partir de los datos y no de la costumbre |
| 6. Async | 0037 a 0045 | Futures y executors, tasks y cancelación, por qué una llamada bloqueante en async es un bug, locks a través de `await`, para qué sirve el pinning | Escribes código async que no se atasca, y puedes explicar dónde lo haría |
| 7. Unsafe y rendimiento | 0046 a 0054 | Qué promete realmente `unsafe`, comportamiento indefinido, encapsular un invariante, comprobar con Miri, benchmarking, costos de asignación y de copia | Puedes defender un límite `unsafe`, y demuestras una afirmación de rendimiento con una medición |
| 8. Criterio | 0055 a 0063 | Publicar, versionado semántico de una API pública, las API guidelines, revisión, leer la biblioteca estándar y los RFC para encontrar respuestas | Se confía en ti para tomar la decisión y explicársela a otra persona; la etapa 9 completa el primer paso del propio procedimiento de release, que la batería de pruebas pase, con la batería que este arco aún no había enseñado a escribir |
| 9. Pruebas | 0064 a 0067 | `#[test]` y `cargo test`, pruebas unitarias frente a pruebas de integración, organizar las pruebas de una biblioteca, pruebas basadas en propiedades y de snapshot | Escribes y organizas una batería de pruebas como lo hace la propia biblioteca estándar, no solo doctests y benchmarks |

## Lecciones

Recórrelas en orden.

| # | Lección | Enseña |
|---|---|---|
| [0001](lessons/0001-ownership-and-drop.md) | Ownership y drop | Todo valor tiene exactamente un dueño, y el compilador lo libera cuando ese dueño sale del ámbito |
| [0002](lessons/0002-moves-and-copy.md) | Moves y Copy | La asignación mueve el ownership salvo que el tipo sea Copy, y por eso el nombre antiguo deja de funcionar |
| [0003](lessons/0003-borrowing.md) | Préstamos | Muchos préstamos compartidos o un préstamo mutable, nunca ambos, y un préstamo termina en su último uso |
| [0004](lessons/0004-slices-string-and-str.md) | Slices, String y str | Un slice es una vista prestada con una longitud, y aceptar &str en una API no les cuesta nada a quienes llaman |
| [0005](lessons/0005-bindings-and-mutability.md) | Bindings y mutabilidad | Inmutable por defecto, mut es por binding, y el shadowing es un binding nuevo y no un cambio |
| [0006](lessons/0006-reading-a-borrow-error.md) | Leer un error de préstamo | Cinco códigos de error cubren la mayor parte de la etapa 1, y cada uno tiene una corrección honesta y un apaño |
| [0007](lessons/0007-structs.md) | Structs y sus métodos | Un struct es dueño de sus campos, así que lo que metes en uno decide quién tiene que mantenerlo vivo |
| [0008](lessons/0008-enums.md) | Enums que llevan datos | Un enum dice que un valor es exactamente una de estas formas, que es la herramienta de modelado sobre la que descansa el resto de la etapa |
| [0009](lessons/0009-option.md) | Option y el manejo de la ausencia | La ausencia es un valor de un tipo distinto, así que el compilador te obliga a decir qué pasa cuando llega |
| [0010](lessons/0010-result.md) | Result y el fallo como valor | Un fallo es un valor de retorno y no un evento, así que la firma dice lo que puede salir mal antes de que leas el cuerpo |
| [0011](lessons/0011-pattern-matching.md) | Pattern matching | Un match tiene que cubrir todos los casos, y el patrón decide si tomaste prestado el valor o lo moviste |
| [0012](lessons/0012-iterators-and-closures.md) | Iteradores y closures | Un iterador no hace nada hasta que algo lo consume, y una closure captura exactamente lo que usa |
| [0013](lessons/0013-collections.md) | Las colecciones que vale la pena conocer | Vec y HashMap cubren la mayor parte, y la entry API es lo único que vale la pena aprender a fondo |
| [0014](lessons/0014-propagating-errors.md) | Propagar errores | El signo de interrogación convierte al devolver, así que el tipo de error de tu firma decide lo que aceptará |
| [0015](lessons/0015-designing-an-error-type.md) | Diseñar un tipo de error | Quien llama solo puede manejar lo que tu error le permite distinguir, así que su forma es una decisión de API |
| [0016](lessons/0016-conversions-and-boundaries.md) | Conversiones y límites | Una implementación de From es donde el fallo de una capa se convierte en el de otra, y un derive escribe las que ya entiendes |
| [0017](lessons/0017-panic-or-error.md) | Panic o error | Un panic dice que el programa está roto y un error dice que lo estaba la entrada, y una biblioteca rara vez puede decidir lo primero |
| [0018](lessons/0018-modules-and-visibility.md) | Módulos y visibilidad | Lo que haces público es lo que has prometido mantener, así que el árbol de módulos es una decisión de API antes que de organización |
| [0019](lessons/0019-documentation-that-compiles.md) | Documentación que compila | Un ejemplo en un comentario de documentación es una prueba, así que la documentación que se pudre es la que nadie ejecutó |
| [0020](lessons/0020-a-library-callers-can-handle.md) | Una biblioteca que quien llama pueda manejar | Dividir el crate, nombrar los fallos y decidir qué hace el binario que la biblioteca no debe hacer |
| [0021](lessons/0021-traits-as-shared-behaviour.md) | Los traits como comportamiento compartido | Cómo un trait nombra un comportamiento que pueden proporcionar varios tipos, y por qué el trait tiene que estar en el ámbito antes de que puedas usarlo |
| [0022](lessons/0022-trait-bounds-and-generic-functions.md) | Trait bounds y funciones genéricas | Qué le promete un bound al cuerpo y qué le exige a quien llama, y qué hace el compilador con él |
| [0023](lessons/0023-associated-types.md) | Tipos asociados | Por qué Iterator nombra su Item como tipo asociado y no como parámetro, y qué decide eso para quien lo implemente |
| [0024](lessons/0024-generics-or-dyn-trait.md) | Genéricos o dyn Trait | Las dos estrategias de despacho, lo que cuesta cada una y la pregunta que realmente decide entre ellas |
| [0025](lessons/0025-implementing-traits-you-do-not-own.md) | Implementar traits que no son tuyos | La coherencia, el patrón newtype y por qué una implementación general es un compromiso y no una comodidad |
| [0026](lessons/0026-lifetimes-are-not-durations.md) | Los lifetimes no son duraciones | Lo que dice un parámetro de lifetime sobre la relación entre préstamos, y lo que la elisión había estado haciendo por ti todo este tiempo |
| [0027](lessons/0027-types-that-borrow.md) | Tipos que toman prestado | Poner un parámetro de lifetime en un struct, y decidir si en cambio el tipo debería ser dueño de sus datos |
| [0028](lessons/0028-reading-a-lifetime-error.md) | Leer un error de lifetime | Las formas que adopta un error de lifetime, cada una con la corrección honesta y el apaño al que te tienta |
| [0029](lessons/0029-threads-joining-and-panics.md) | Hilos, join y panics | Qué exige realmente lanzar un hilo de los datos que le entregas, y qué le pasa a un hilo que hace panic solo |
| [0030](lessons/0030-scoped-threads.md) | Hilos con ámbito | Por qué un hilo que no puede sobrevivir a su ámbito puede tomar prestado, y por qué es lo primero a lo que recurrir y no lo último |
| [0031](lessons/0031-shared-ownership.md) | Ownership compartido con Rc y Arc | Cuándo un valor necesita varios dueños en lugar de uno, lo que cuesta el contador y cómo filtra memoria un ciclo |
| [0032](lessons/0032-interior-mutability.md) | Mutabilidad interior | Mover la regla de préstamos del tiempo de compilación al tiempo de ejecución, lo que eso te da y lo que cuesta cuando te equivocas |
| [0033](lessons/0033-mutex-rwlock-and-poisoning.md) | Mutex, RwLock y envenenamiento | Qué protege realmente un lock, por qué el ámbito del guard es la decisión de diseño y qué deja atrás un panic mientras se tiene uno |
| [0034](lessons/0034-send-and-sync.md) | Send y Sync | Los dos traits que nadie escribe y que deciden qué puede cruzar el límite de un hilo, y cómo leer los errores que provocan |
| [0035](lessons/0035-channels.md) | Canales | Enviar valores entre hilos en lugar de compartirlos, y qué hacen los extremos de un canal cuando el otro extremo desaparece |
| [0036](lessons/0036-choosing-a-sharing-strategy.md) | Elegir una estrategia para compartir | Los fallos que se derivan de elegir por costumbre, y las preguntas que eligen la estrategia a partir de los datos |
| [0037](lessons/0037-what-a-future-is.md) | Qué es un future | Una máquina de estados con un único método, impulsada por quien la sondea, y lo que eso significa para un código que parece secuencial |
| [0038](lessons/0038-wakers-executors-and-runtimes.md) | Wakers, executors y runtimes | Cómo dice un future que está listo para volver a ser sondeado, y qué hace un runtime además de sondearlo |
| [0039](lessons/0039-tasks-and-the-send-bound.md) | Tasks y el bound Send | Qué exige lanzar una task async del future que le entregas, y por qué un método async de un trait no lo cumplirá |
| [0040](lessons/0040-blocking-is-a-bug.md) | Bloquear es un bug | Por qué una sola llamada bloqueante en una task async atasca trabajo que no tiene nada que ver con ella, y qué hacer con las llamadas que no puedes evitar |
| [0041](lessons/0041-shared-state-across-an-await.md) | Estado compartido a través de un await | Por qué se rechaza un lock guard mantenido a través de un punto await, y cómo elegir entre los dos tipos de mutex |
| [0042](lessons/0042-cancellation.md) | Cancelación | Detener un future significa soltarlo con drop, por eso no se avisa a nadie y por eso el trabajo simplemente se detiene donde estaba |
| [0043](lessons/0043-cancellation-safety.md) | Seguridad ante la cancelación | Si un future puede soltarse a mitad de camino sin perder lo que ya había tomado, y dónde se responde esa pregunta |
| [0044](lessons/0044-pinning.md) | Pinning | Por qué la memoria de un future tiene que dejar de moverse una vez que se sondea, y qué hace Pin al respecto |
| [0045](lessons/0045-reading-an-async-failure.md) | Leer un fallo async | Las cinco formas en que el código async falla sin un mensaje de error, y cómo saber cuál tienes delante |
| [0046](lessons/0046-what-unsafe-promises.md) | Lo que promete unsafe | Las cinco cosas que te permite hacer un bloque unsafe, y la obligación que asumes al escribir uno |
| [0047](lessons/0047-raw-pointers.md) | Punteros en bruto | Lo que no es un puntero en bruto, lo que te cuesta en garantías y cómo crear uno que sea realmente válido |
| [0048](lessons/0048-undefined-behaviour.md) | Comportamiento indefinido | Lo que el compilador puede asumir, por qué un programa que funciona puede seguir estando mal y la lista que vale la pena saberse de memoria |
| [0049](lessons/0049-checking-with-miri.md) | Comprobar con Miri | La herramienta que convierte un bug de solidez invisible en un informe, lo que detecta y lo que no puede detectar |
| [0050](lessons/0050-encapsulating-an-invariant.md) | Encapsular un invariante | Envolver código unsafe en una interfaz segura, y lo que tiene que cumplirse para que esa interfaz merezca el nombre |
| [0051](lessons/0051-memory-orderings.md) | Órdenes de memoria | Qué restringe realmente un orden, por qué no puedes probar uno ejecutándolo y cómo comprobar el que elegiste |
| [0052](lessons/0052-measuring-before-optimising.md) | Medir antes de optimizar | Cómo obtener un número que puedas defender, qué le hace el compilador a un benchmark que no mide nada y lo que una medición no te puede decir |
| [0053](lessons/0053-allocation-and-copying-costs.md) | Costos de asignación y de copia | Dónde gasta realmente su tiempo un programa en Rust, y cuáles de las correcciones obvias compensan |
| [0054](lessons/0054-defending-an-unsafe-boundary.md) | Defender un límite unsafe | El argumento que tienes que poder dar antes de que se publique un bloque unsafe, y la medición que tiene que acompañarlo |
| [0055](lessons/0055-variance.md) | Varianza | Qué lifetimes pueden sustituir a cuáles, por qué lo decide tu propio tipo y a qué te compromete eso |
| [0056](lessons/0056-higher-ranked-bounds.md) | Bounds de rango superior | Escribir el cuantificador que el compilador te ha estado imprimiendo, y las formas de API que lo necesitan |
| [0057](lessons/0057-what-breaks-a-caller.md) | Lo que rompe a quien llama | Los cambios que necesitan una versión mayor, los que solo parecen seguros y la herramienta que te dice cuál es cuál |
| [0058](lessons/0058-designing-for-change.md) | Diseñar para el cambio | Las decisiones que te dejan margen para moverte más adelante, y las que en silencio prometen más de lo que pretendías |
| [0059](lessons/0059-features-and-the-minimum-version.md) | Features y la versión mínima | Por qué una feature solo debe añadir, qué le hace la unificación a tus suposiciones y qué promete realmente declarar una versión mínima |
| [0060](lessons/0060-workspaces-and-release.md) | Workspaces y release | Llevar un crate al punto en que publicar sea un solo comando, y qué hace realmente ese comando |
| [0061](lessons/0061-the-api-guidelines.md) | Las API guidelines | La lista de comprobación en la que el ecosistema ya se puso de acuerdo, qué puntos importan más y cómo usarla sin seguirla a ciegas |
| [0062](lessons/0062-reading-the-source-and-the-rfcs.md) | Leer el código fuente y los RFC | Responder a una pregunta que la documentación no responde, a partir de la biblioteca estándar, los issues de seguimiento y los RFC |
| [0063](lessons/0063-reviewing-rust.md) | Revisar Rust | Qué buscar en el Rust de otra persona, en qué orden y qué comentarios vale la pena hacer |
| [0064](lessons/0064-the-test-attribute-and-cargo-test.md) | El atributo test y cargo test | Un doctest vive en un comentario de documentación y ejecuta un ejemplo; una función #[test] vive en el propio código fuente del crate y es la forma corriente que adopta casi todo el testing en Rust, y cargo test ejecuta ambos con el mismo comando sin que sean el mismo mecanismo |
| [0065](lessons/0065-unit-versus-integration-tests.md) | Pruebas unitarias frente a pruebas de integración | Dónde vive una función #[test] decide lo que puede ver: el mismo archivo que el código bajo #[cfg(test)], con acceso a todos los elementos privados, o un directorio tests/ aparte que solo ve lo que realmente hiciste público |
| [0066](lessons/0066-organising-tests-for-a-library.md) | Organizar las pruebas de una biblioteca | La forma de una batería de integración la impone lo que ya hiciste pub, la preparación compartida va específicamente en tests/common/mod.rs, y un binario sin lib.rs no se puede probar con pruebas de integración en absoluto |
| [0067](lessons/0067-property-based-and-snapshot-testing.md) | Pruebas basadas en propiedades y pruebas de snapshot | Este es el cierre de la etapa 9: proptest genera cientos de entradas y reduce un fallo a la entrada más pequeña que todavía rompe la propiedad, mientras que una prueba de snapshot compara la salida de una entrada elegida con una referencia que una persona ya revisó |

## Referencia

- [Glosario](GLOSSARY.md): términos canónicos de este tema
- [Recursos](RESOURCES.md): fuentes de confianza, cada una anotada con lo que cubre
- [Ownership y préstamos](reference/ownership-and-borrowing.md): las reglas, la lista de Copy, los códigos de error y la corrección honesta de cada uno
- [El proyecto](reference/the-project.md): el crate que construyen las prácticas a lo largo del arco, y en qué estado debería estar al final de cada etapa
- [Datos y control](reference/data-and-control.md): la hoja de la etapa 2, con las decisiones sobre enums, Option y Result, las reglas de los patrones y las colecciones
- [Errores y forma de la API](reference/errors-and-api-shape.md): la hoja de la etapa 3, con las decisiones sobre tipos de error, las reglas de conversión y a qué compromete una API pública
- [Traits y lifetimes](reference/traits-and-lifetimes.md): la hoja de la etapa 4, con la decisión sobre el despacho, las reglas de coherencia y la tabla de errores de lifetime
- [Compartir e hilos](reference/sharing-and-threads.md): la hoja de la etapa 5, con el procedimiento para elegir estrategia, lo que cuesta cada tipo para compartir y la tabla de fallos
- [Async](reference/async.md): la hoja de la etapa 6, con el modelo de sondeo, los bounds, la tabla de fallos y dónde está documentada la seguridad ante la cancelación
- [Unsafe y rendimiento](reference/unsafe-and-performance.md): la hoja de la etapa 7, con la tabla de comportamiento indefinido, lo que detecta cada herramienta y la disciplina de medición
- [Criterio](reference/judgment.md): la hoja de la etapa 8, con las reglas de varianza, la tabla de cambios incompatibles, la lista de comprobación de release y el orden de autoridad

## Cómo funciona

Cada lección es corta y autocontenida. Las claves de respuesta están plegadas: primero recuerda, luego ábrelas. Las prácticas en el mundo real importan más que la lectura, y espaciarlas es el punto. Todo lo que siga sin estar claro al final de una lección merece rastrearse hasta su fuente primaria antes de seguir.
