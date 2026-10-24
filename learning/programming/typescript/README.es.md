---
title: TypeScript
description: "Hazte cargo de un código base en TypeScript: haz que el compilador rechace los estados que no deberían existir"
type: topic
---

# Aprendizaje: TypeScript

Conviértete en el ingeniero en quien se confía para hacerse cargo de un código base en TypeScript dentro de un equipo: capaz de modelar un dominio para que el compilador rechace los estados que no deberían existir, de mantener las aserciones de tipo fuera del código que soporta peso, de validar lo que cruza un límite en tiempo de ejecución en lugar de suponer que los tipos se cumplieron, y de revisar los tipos de otra persona y decir en concreto por qué un genérico ingenioso cuesta más de lo que aporta.

**Empieza aquí:** [0001. Valores y coerción](lessons/0001-values-and-coercion.md)
**Última lección:** [0049. Alguien de confianza para tomar la decisión](lessons/0049-trusted-to-make-the-call.md), que cierra el arco

## Cómo se ve el éxito

- Predecir lo que hace JavaScript con la coerción, las closures, `this` y el event loop, antes de ejecutar el código y sin la ayuda del sistema de tipos.
- Convertir un conjunto de estados ilegales en un tipo que el compilador rechace, y demostrar la exhaustividad con `never`.
- Leer el mensaje de error de un genérico hasta su causa en lugar de recurrir a `as`.
- Decir exactamente qué sobrevive a la compilación y qué se borra, y validar cada valor que entra en el programa desde fuera.
- Configurar el compilador con intención: nombrar lo que aporta cada opción de estrictez y por qué los ajustes de module y target son los que son.
- Escribir una función genérica cuya inferencia funcione, para que quienes la llaman no tengan que anotar nada.
- Publicar un paquete cuyos tipos puedan usar sus consumidores, incluida la salida de declaraciones y los exports que anuncia.
- Revisar una pull request y decir con precisión por qué un tipo condicional, una aserción o un `enum` es la herramienta equivocada ahí.

## Restricciones

- No se asume experiencia previa con TypeScript, ni más JavaScript del que enseña el arco. TypeScript es un sistema de tipos sobre JavaScript, así que la semántica de JavaScript se enseña allí donde explica el comportamiento que un tipo no puede explicar.
- El límite entre tiempo de compilación y tiempo de ejecución se trata como una línea firme en todo momento, porque casi todos los errores serios en TypeScript son una afirmación sobre el tiempo de ejecución que solo comprobó el compilador.
- Solo necesita un runtime de JavaScript y una terminal en cualquier sistema operativo soportado, con el playground en línea sustituyendo a ambos cuando una práctica solo necesita ver un tipo. Sin herramientas de pago, sin cuenta en la nube, sin framework.
- Las prácticas son programas pequeños y pequeños experimentos de tipos que caben en una sesión.
- TypeScript publica una versión cada pocos meses y el sistema de tipos gana expresividad real en esas versiones. Las afirmaciones sensibles a la versión se contrastan con las notas de la versión, y cualquier lección que dependa de una versión dice cuál.

## Fuera de alcance

- Frameworks y bibliotecas de UI como temas propios: React, Angular, Vue, Svelte, Next.js.
- Bundlers y herramientas de monorepo como temas: webpack, Vite, esbuild, Turborepo. La resolución de módulos se enseña a partir del propio modelo del compilador, que es con lo que tienen que estar de acuerdo esas herramientas.
- Otros runtimes como temas: Deno, Bun, la plataforma del navegador. Aparecen solo donde el comportamiento difiere de verdad.
- Node.js como plataforma en sí: streams, clustering, addons nativos.
- La programación a nivel de tipos como deporte. Los tipos mapeados y condicionales se enseñan hasta el punto en que sirven a quien llama, y la etapa 6 dice explícitamente dónde está ese punto.

## El arco

Siete etapas, desde ningún conocimiento previo hasta el criterio de un perfil sénior. No es una lista de lecciones: una etapa abarca varias lecciones y los límites son difusos.

| Etapa | Lecciones | Cubre | Terminada cuando |
|---|---|---|---|
| 1. El JavaScript de debajo | 0001 a 0007 | Valores y coerción, objetos y prototipos, closures, `this`, módulos, el event loop, promesas y async | Puedes predecir lo que hace un programa en tiempo de ejecución, sin que intervengan los tipos |
| 2. Tipos sobre valores | 0008 a 0014 | Primitivos, arrays y tuplas, uniones, tipos literales, asignabilidad estructural, estrechamiento, tipos función, `readonly`, lo que la inferencia ya sabe | Anotas solo donde la inferencia no llega |
| 3. La estrictez y el compilador | 0015 a 0021 | La familia `strict` opción por opción, las opciones de tipo estricto que `strict` todavía omite, `unknown` frente a `any`, aserciones frente a declaraciones, `tsconfig`, resolución de módulos, `target` y `lib` | Mantienes activada la estrictez y corriges lo que informa en lugar de suprimirlo, y activas las comprobaciones que `strict` deja fuera |
| 4. Modelado | 0022 a 0028 | Uniones discriminadas, exhaustividad con `never`, tipos con marca, genéricos y restricciones, `satisfies`, interface frente a type alias | Los estados ilegales no se pueden representar, y es el compilador quien lo demuestra |
| 5. El límite del tiempo de ejecución | 0029 a 0035 | Lo que se borra, archivos de declaración, validar la entrada en el borde, errores como valores, consumir dependencias sin tipos o con tipos erróneos | Ningún valor entra en el programa sin validar, y ninguna aserción soporta peso |
| 6. Herramientas a nivel de tipos | 0036 a 0042 | Tipos mapeados y condicionales, `infer`, tipos template literal, varianza y asignabilidad, inferencia para APIs de bibliotecas, rendimiento del compilador | Escribes una API cuyos tipos sirven a quienes la llaman, y te detienes antes de pasarte de ingenioso |
| 7. Criterio | 0043 a 0049 | Publicar una superficie de tipos pública, qué cuenta como cambio incompatible en los tipos, revisión, leer las notas de la versión y las propias declaraciones del compilador | Se confía en ti para tomar la decisión y explicársela a otra persona |

## Lecciones

Recórrelas en orden.

| # | Lección | Enseña |
|---|---|---|
| [0001](lessons/0001-values-and-coercion.md) | Valores y coerción | Siete primitivos, dos vacíos y un operador de igualdad que convierte antes de comparar |
| [0002](lessons/0002-objects-are-references.md) | Los objetos son referencias | const impide volver a enlazar, spread copia un nivel y readonly desaparece en tiempo de ejecución |
| [0003](lessons/0003-prototypes-and-classes.md) | Prototipos y clases | La búsqueda de propiedades recorre una cadena, y la sintaxis class es una forma de construir esa cadena |
| [0004](lessons/0004-this-and-the-call-site.md) | this lo decide la llamada | this viene de cómo se llama a una función, así que extraer un método lo pierde |
| [0005](lessons/0005-scope-and-closures.md) | Ámbito y closures | Una closure captura el binding y no el valor, y let crea uno por iteración |
| [0006](lessons/0006-event-loop-and-promises.md) | El event loop, las promesas y await | Las microtareas se vacían antes del siguiente temporizador, y dos awaits seguidos son secuenciales |
| [0007](lessons/0007-modules.md) | Módulos | Los imports se elevan y se enlazan en vivo, y un archivo sin import ni export no es un módulo |
| [0008](lessons/0008-the-types-you-write.md) | Los tipos que escribes | El vocabulario de las anotaciones, y un compilador que ya pone objeciones antes de que lo configures |
| [0009](lessons/0009-tuples-and-readonly.md) | Tuplas y readonly | Una longitud fija que el compilador hace cumplir en las lecturas y olvida en push |
| [0010](lessons/0010-unions-and-literal-types.md) | Uniones y tipos literales | Un valor con más de un tipo posible, y el ensanchamiento que descarta el interesante |
| [0011](lessons/0011-structural-assignability.md) | Asignabilidad estructural | La forma decide qué va dónde, salvo por la única comprobación que solo salta con un literal de objeto recién creado |
| [0012](lessons/0012-narrowing.md) | Estrechamiento | El flujo de control le dice al compilador en qué se ha convertido una unión, y exactamente dos cosas lo deshacen |
| [0013](lessons/0013-function-types.md) | Tipos función | Los parámetros se comprueban en la dirección que esperas, salvo que hayas escrito un método |
| [0014](lessons/0014-what-inference-already-knows.md) | Lo que la inferencia ya sabe | Hasta dónde llega la inferencia, para que escribir una anotación signifique algo cuando lo haces |
| [0015](lessons/0015-what-strict-turns-on.md) | Lo que activa strict | Siete comprobaciones detrás de una sola opción, cada una con un fallo que existe para detectar |
| [0016](lessons/0016-the-checks-strict-leaves-out.md) | Las comprobaciones que strict deja fuera | Seis comprobaciones más que vale la pena tener, una que el compilador se niega a activar y otra que no hace nada en absoluto |
| [0017](lessons/0017-unknown-instead-of-any.md) | unknown en lugar de any | Un tipo lo acepta todo y no te deja hacer nada, el otro lo acepta todo y no comprueba nada |
| [0018](lessons/0018-an-assertion-is-not-a-check.md) | Una aserción no es una comprobación | Todas las formas de decirle al compilador que deje de comprobar, y lo que cuesta cada una cuando la afirmación es falsa |
| [0019](lessons/0019-reading-a-tsconfig.md) | Leer un tsconfig | Qué archivos mira el compilador, de dónde vienen los ajustes y por qué el archivo generado dice lo que dice |
| [0020](lessons/0020-target-and-lib.md) | target y lib | Un ajuste cambia lo que se emite y el otro cambia lo que existe, y nombrar el segundo descarta el valor por defecto |
| [0021](lessons/0021-module-resolution.md) | Resolución de módulos | Las mismas opciones del compilador dan veredictos opuestos según un solo campo de package.json |
| [0022](lessons/0022-discriminated-unions.md) | Uniones discriminadas | Una propiedad literal compartida, y una unión que el compilador puede desmontar |
| [0023](lessons/0023-exhaustiveness-with-never.md) | Exhaustividad con never | Añadir un miembro a una unión debería romper cada switch que lo ignoraba, y una sola línea lo consigue |
| [0024](lessons/0024-illegal-states.md) | Hacer irrepresentables los estados ilegales | Cuenta los estados que permite tu tipo, y luego elimina los que tu dominio no tiene |
| [0025](lessons/0025-branded-types.md) | Tipos con marca | Tipado nominal encima de un sistema estructural, y la única aserción que cuesta |
| [0026](lessons/0026-generics-and-constraints.md) | Genéricos y restricciones | Un parámetro de tipo es una promesa a quien llama, y una restricción es lo que te permite cumplirla |
| [0027](lessons/0027-satisfies.md) | satisfies | Comprobar un valor contra un tipo sin dejar que el tipo sustituya lo que escribiste |
| [0028](lessons/0028-interface-or-type.md) | interface o type | Uno informa de un miembro en conflicto donde lo escribiste y el otro lo informa en otro sitio |
| [0029](lessons/0029-nothing-survives-to-run-time.md) | Nada sobrevive al tiempo de ejecución | Cada tipo es una afirmación sobre un programa que ya no existe cuando la afirmación importaría |
| [0030](lessons/0030-unknown-at-the-edge.md) | unknown en el borde | Encontrar cada lugar por el que llega un valor desde fuera, y darle a cada uno el único tipo honesto |
| [0031](lessons/0031-parsing-instead-of-asserting.md) | Analizar en lugar de afirmar | Una sola declaración que produce tanto la comprobación en tiempo de ejecución como el tipo estático |
| [0032](lessons/0032-type-predicates-and-assertion-functions.md) | Predicados de tipo y funciones de aserción | Una firma que promete una comprobación, y un cuerpo con el que nada la contrasta |
| [0033](lessons/0033-errors-as-values.md) | Errores como valores | Un fallo en el tipo de retorno es uno que el compilador puede obligarte a manejar |
| [0034](lessons/0034-declaration-files.md) | Archivos de declaración | Tipos para código que el compilador nunca ve, y lo que vale esa promesa |
| [0035](lessons/0035-when-the-declaration-lies.md) | Cuando la declaración miente | El compilador se cree la declaración y el runtime nunca ha oído hablar de ella |
| [0036](lessons/0036-mapped-types.md) | Tipos mapeados | Transformar a la vez todas las propiedades de un tipo, y eliminar las que no quieres |
| [0037](lessons/0037-conditional-types.md) | Tipos condicionales | Un tipo que se ramifica, y una unión que primero desmonta sin que se note |
| [0038](lessons/0038-infer.md) | infer | Sacar un tipo de una posición en lugar de pedirle a quien llama que lo nombre |
| [0039](lessons/0039-template-literal-types.md) | Tipos template literal | Un patrón de string que comprueba el compilador, y los nombres de clave que puede construir |
| [0040](lessons/0040-variance-and-assignability.md) | Varianza y asignabilidad | En qué dirección puede viajar un tipo, y el array que lo hace mal a propósito |
| [0041](lessons/0041-inference-for-library-apis.md) | Inferencia para APIs de bibliotecas | Diseñar la firma para que quien llama no anote nada |
| [0042](lessons/0042-knowing-when-to-stop.md) | Saber cuándo parar | Medir lo que cuesta un tipo ingenioso, y luego justificarlo ante quien lo mantenga |
| [0043](lessons/0043-what-counts-as-a-breaking-change.md) | Qué cuenta como cambio incompatible | Qué ediciones de un tipo publicado rompen a un consumidor, y en qué dirección tiene que viajar cada una |
| [0044](lessons/0044-publishing-a-type-surface.md) | Publicar una superficie de tipos | Lo que resuelve realmente un consumidor cuando importa tu paquete, y cómo comprobarlo antes de que lo haga él |
| [0045](lessons/0045-the-consumers-settings-are-not-yours.md) | Los ajustes del consumidor no son los tuyos | Un consumidor estricto hereda las afirmaciones de un autor laxo y no tiene forma de darse cuenta |
| [0046](lessons/0046-the-typescript-that-does-not-erase.md) | El TypeScript que no se borra | Cuatro funcionalidades que emiten código que no pediste, y la opción que las nombra |
| [0047](lessons/0047-settling-it-from-the-source.md) | Zanjarlo desde la fuente | Qué documento responde a una pregunta sobre el compilador, y cómo leer las declaraciones que incluye |
| [0048](lessons/0048-reviewing-typescript.md) | Revisar TypeScript | Nombrar lo que cuesta un tipo, en lugar de decir que parece complicado |
| [0049](lessons/0049-trusted-to-make-the-call.md) | Alguien de confianza para tomar la decisión | El último juicio del arco, y lo que el compilador nunca iba a hacer por ti |

## Referencia

- [Glosario](GLOSSARY.md): términos canónicos de este tema
- [Recursos](RESOURCES.md): fuentes de confianza, cada una anotada con lo que cubre
- [Coerción e igualdad](reference/coercion-and-equality.md): valores falsy, qué convierte `==`, qué operador de valor por defecto escribir
- [Event loop y promesas](reference/event-loop-and-promises.md): orden de las colas, combinadores y los errores de async que ningún compilador informa
- [Tipos sobre valores](reference/types-over-values.md): lo que aporta cada anotación, hasta dónde llega la inferencia y los huecos que el compilador deja abiertos a propósito
- [La estrictez y el compilador](reference/strictness-and-the-compiler.md): qué opción detecta qué fallo, de dónde viene un ajuste y cómo se resuelve un import
- [Modelado](reference/modelling.md): qué forma elimina el estado ilegal, y qué declaración detecta el error donde lo cometiste
- [El límite del tiempo de ejecución](reference/the-runtime-boundary.md): por dónde entran los valores, qué los comprueba y qué afirmaciones no comprueba nada en absoluto
- [Herramientas a nivel de tipos](reference/type-level-tools.md): qué construcción calcula qué tipo, y la prueba que tiene que superar una ingeniosa
- [Criterio](reference/judgment.md): qué ediciones rompen a un consumidor, qué no se borra y cómo argumentar la decisión desde la fuente

## Cómo funciona

Cada lección es corta y autocontenida. Las claves de respuesta están plegadas: primero recuerda, luego ábrelas. Las prácticas en el mundo real importan más que la lectura, y espaciarlas es el punto. Todo lo que siga sin estar claro al final de una lección merece rastrearse hasta su fuente primaria antes de seguir.
