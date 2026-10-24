---
title: Python
description: "Hazte cargo de Python en producción: entrégalo tipado, probado, empaquetado y perfilado"
type: topic
---

# Aprendizaje: Python

Conviértete en el ingeniero en quien se confía para hacerse cargo de Python en un equipo: capaz de entregar un servicio o una herramienta en Python tipado, probado y empaquetado, de llevar una traza de error o un perfil hasta su causa raíz en lugar de adivinar, y de decir en concreto por qué el uso ingenioso que hace alguien del dinamismo de Python le va a hacer daño.

**Empieza aquí:** [0001. Los nombres son enlaces, no cajas](lessons/0001-names-are-bindings.md)
**Última lección:** [0044. Criterio](lessons/0044-judgment.md)

## Cómo se ve el éxito

- Predecir lo que hacen un argumento por defecto mutable, una closure sobre una variable de bucle y una lista compartida, antes de ejecutar el código.
- Entregar un paquete que se instale y se ejecute en una máquina que no sea en la que se escribió.
- Añadir type hints que verifique un checker, y corregir lo que informa en lugar de silenciarlo.
- Escribir pruebas con `pytest` que fallen de forma informativa, usando fixtures y parametrización en lugar de cuerpos de prueba copiados.
- Encontrar la parte lenta con un profiler y demostrar la corrección con una medición.
- Elegir entre hilos, procesos y `asyncio` a partir de la forma de la carga de trabajo, y decir lo que el GIL impide y lo que no.
- Implementar un método dunder o un context manager cuando el modelo de datos lo pide, y reconocer cuándo una función simple es la mejor respuesta.
- Revisar el Python de otra persona y nombrar con precisión por qué una clase, una metaclase o una cadena de herencia es la herramienta equivocada ahí.

## Restricciones

- No se asume experiencia previa con Python. La experiencia en otro lenguaje acorta las primeras etapas pero no es necesaria, y trae hábitos que Python castiga en silencio: una clase donde bastaría una función, un bucle donde una comprensión se lee mejor, una copia defensiva que el lenguaje ya hizo.
- Solo necesita CPython y una terminal en cualquier sistema operativo soportado. Nada en el arco requiere herramientas de pago, una cuenta en la nube ni una segunda máquina.
- CPython es la implementación de referencia en todo momento. Otras implementaciones aparecen solo donde el comportamiento difiere de verdad.
- Las prácticas son programas pequeños que caben en una sesión. Espaciarlas a lo largo de varios días es el mecanismo, no un inconveniente.
- El tipado y el empaquetado avanzan más rápido que el lenguaje. Las afirmaciones sensibles a la versión se contrastan con la documentación actual y el PEP correspondiente, y cualquier lección que dependa de una versión dice cuál.

## Fuera de alcance

- Frameworks web como temas propios: Django, FastAPI, Flask.
- La pila científica y de machine learning como tema: NumPy, pandas, PyTorch. Consulta [`llm/finetuning`](../../llm/finetuning/) para ese límite.
- La distribución más allá de wheels publicados en un índice: conda, paquetes del sistema operativo, binarios congelados de un solo archivo.
- Los detalles internos de CPython más allá del punto en que dejan de predecir el comportamiento del programa: bytecode, la API de C, escribir módulos de extensión.
- Python 2 y la migración desde él.
- Imágenes de contenedor: meter un wheel y su intérprete en una imagen, y ejecutar, asegurar y depurar ese contenedor, corresponde a [`infrastructure/containers`](../../infrastructure/containers/).

## El arco

Siete etapas, desde ningún conocimiento previo hasta el criterio de un perfil sénior. No es una lista de lecciones: una etapa abarca varias lecciones y los límites son difusos.

| Etapa | Lecciones | Cubre | Terminada cuando |
|---|---|---|---|
| 1. Fundamentos | 0001 a 0007 | Objetos y nombres, mutabilidad y aliasing, listas, dicts, sets, tuplas, valor de verdad, comprensiones, funciones y paso de argumentos | Puedes predecir el aliasing y la mutación sin ejecutar el código |
| 2. Modismos | 0008 a 0014 | Iteradores y generadores, context managers, excepciones como flujo de control, `dataclasses`, módulos y paquetes, la parte de la biblioteca estándar que vale la pena conocer | Recurres a un generador o a un context manager en lugar de escribir a mano el bucle y el `try/finally` |
| 3. Tipos y herramientas | 0015 a 0021 | Anotaciones, genéricos, `Protocol`, estrictez del checker, linting y formateo, entornos virtuales, gestión de dependencias y de proyectos, construir un wheel | Un checker estricto pasa, y otra persona puede instalar el resultado |
| 4. El modelo de datos | 0022 a 0027 | Métodos dunder, `__init__` frente a `__new__`, propiedades, descriptores, atributos de clase frente a atributos de instancia, orden de resolución de métodos, por qué las metaclases casi nunca son la respuesta | Implementas el protocolo que necesita un tipo, y puedes decir cuándo no hacerlo |
| 5. Pruebas | 0028 a 0033 | Mecánica de `pytest`, fixtures y su scope, parametrización, pruebas basadas en propiedades, qué merece un mock y qué no, la cobertura como señal y no como objetivo | Tienes una batería de pruebas que detectó una regresión antes que una persona |
| 6. Concurrencia y rendimiento | 0034 a 0039 | Hilos, procesos, `asyncio`, lo que serializa realmente el GIL, llamadas bloqueantes dentro de un event loop, profiling, el costo de la búsqueda de atributos y de la asignación | Eliges el modelo de concurrencia a partir de la carga de trabajo y demuestras la mejora con un perfil |
| 7. Criterio | 0040 a 0044 | Diseño de APIs y de paquetes, deprecación, revisión, leer la biblioteca estándar y los PEP para encontrar respuestas | Se confía en ti para tomar la decisión y explicársela a otra persona |

## Lecciones

Recórrelas en orden.

| # | Lección | Enseña |
|---|---|---|
| [0001](lessons/0001-names-are-bindings.md) | Los nombres son enlaces, no cajas | La asignación enlaza un nombre a un objeto y nunca lo copia, así que dos nombres pueden significar una misma cosa |
| [0002](lessons/0002-mutability-and-copying.md) | Mutabilidad y copia | La mutabilidad pertenece al objeto, así que un contenedor inmutable puede seguir conteniendo algo que cambia |
| [0003](lessons/0003-lists-and-slicing.md) | Listas y slicing | Un slice copia, los métodos in situ devuelven None, y += muta lo que + reconstruiría |
| [0004](lessons/0004-dicts-and-sets.md) | Dicts y sets | Las claves deben ser hashables, la búsqueda tiene un modismo correcto por intención, y una vista no es una instantánea |
| [0005](lessons/0005-truthiness-none-and-equality.md) | Valor de verdad, None e igualdad | Vacío es falso pero no es None, así que el modismo equivocado para el valor por defecto rechaza el cero y el string vacío |
| [0006](lessons/0006-functions-and-arguments.md) | Funciones y argumentos | Los valores por defecto se evalúan una sola vez al definir la función, y quien llama ve cada mutación que haces |
| [0007](lessons/0007-comprehensions.md) | Comprensiones | Una expresión que construye un contenedor, con su propio ámbito y un límite que vale la pena respetar |
| [0008](lessons/0008-the-iteration-protocol.md) | El protocolo de iteración | Por qué for funciona sobre cualquier cosa, y por qué algunas de esas cosas solo se pueden recorrer una vez |
| [0009](lessons/0009-generators.md) | Generadores | Una función que se pausa, conserva su estado local y produce valores solo cuando se le piden |
| [0010](lessons/0010-exceptions.md) | Excepciones | Pedir perdón en lugar de permiso, y capturar exactamente lo que puedes manejar |
| [0011](lessons/0011-context-managers.md) | Context managers | Un bloque con una salida garantizada, y cómo escribir uno en seis líneas |
| [0012](lessons/0012-dataclasses.md) | Dataclasses | init, repr e igualdad generados, y elegir la forma adecuada para un conjunto de datos |
| [0013](lessons/0013-modules-and-packages.md) | Módulos y paquetes | Un módulo se ejecuta una sola vez, un import enlaza un nombre, y cómo ambas cosas producen todos los errores de import que has visto |
| [0014](lessons/0014-the-standard-library.md) | La biblioteca estándar | Los módulos que eliminan código que estabas a punto de escribir, y los que te ahorran una dependencia |
| [0015](lessons/0015-annotations-are-claims.md) | Las anotaciones son afirmaciones | El intérprete las guarda y nunca las comprueba, que es lo que hace que valga la pena escribirlas |
| [0016](lessons/0016-making-a-checker-useful.md) | Hacer útil un checker | Configurar la estrictez, leer los códigos de error y estrechar los tipos en lugar de silenciarlos |
| [0017](lessons/0017-generics-and-protocols.md) | Genéricos y protocolos | Conservar el tipo de los elementos a través de una función, y tipar una forma en lugar de una clase |
| [0018](lessons/0018-types-at-the-boundary.md) | Tipos en el límite | Convertir el Any que llega de JSON, del entorno y de las filas de una base de datos en algo sobre lo que un checker pueda razonar |
| [0019](lessons/0019-environments-and-dependencies.md) | Entornos y dependencias | Aislamiento por proyecto, la diferencia entre un requisito y un lock, y quién fija qué |
| [0020](lessons/0020-building-a-package.md) | Construir un paquete | Qué es un wheel, qué tienen que decir los metadatos y cómo demostrar que el artefacto se instala |
| [0021](lessons/0021-lint-and-format.md) | Lint y formateo | Acabar con la discusión sobre estilo, y las familias de reglas que encuentran defectos reales |
| [0022](lessons/0022-attribute-lookup.md) | Búsqueda de atributos | Dónde busca realmente la notación de punto, y por qué un atributo de clase lo comparten todas las instancias |
| [0023](lessons/0023-properties-and-descriptors.md) | Propiedades y descriptores | Convertir un atributo en código sin cambiar a un solo llamador |
| [0024](lessons/0024-dunder-methods.md) | Métodos dunder | Qué protocolos debería implementar un tipo, y cuáles recurren a otros como respaldo |
| [0025](lessons/0025-construction.md) | Construcción | Lo que `__init__` no controla, cuándo se necesita `__new__` y cómo dar nombre a tus constructores |
| [0026](lessons/0026-inheritance-and-mro.md) | Herencia y el MRO | Qué hace realmente super, por qué el orden se calcula y cuándo gana la composición |
| [0027](lessons/0027-metaclasses-and-why-not.md) | Metaclases, y por qué no | Qué hace realmente una sentencia class, y los cuatro hooks que sustituyen a casi cualquier metaclase |
| [0028](lessons/0028-what-a-test-asserts.md) | Lo que afirma una prueba | Un comportamiento por prueba, un mensaje de fallo que no necesita depurador y un assert simple |
| [0029](lessons/0029-fixtures.md) | Fixtures | La preparación como una dependencia que pide la prueba, con una limpieza que se ejecuta pase lo que pase |
| [0030](lessons/0030-parametrisation.md) | Parametrización | Un cuerpo de prueba, muchos casos y un fallo que nombra el caso que se rompió |
| [0031](lessons/0031-test-doubles.md) | Dobles de prueba | Qué reemplazar, qué dejar en paz y por qué patch recibe la ruta donde se usa el nombre |
| [0032](lessons/0032-property-based-testing.md) | Pruebas basadas en propiedades | Enunciar lo que siempre debe cumplirse, y dejar que una biblioteca encuentre la entrada que lo rompe |
| [0033](lessons/0033-coverage-and-confidence.md) | Cobertura y confianza | Por qué el 100 por ciento no demuestra nada, para qué sirve el número y en qué pruebas confiar |
| [0034](lessons/0034-the-gil-precisely.md) | El GIL, con precisión | Lo que serializa, lo que no protege y lo que cambia sin él |
| [0035](lessons/0035-threads-and-shared-state.md) | Hilos y estado compartido | Un pool en lugar de hilos en bruto, una cola en lugar de un lock, y la excepción que nadie vio |
| [0036](lessons/0036-processes-and-interpreters.md) | Procesos e intérpretes | Paralelismo real para el cómputo, y lo que cuesta enviar datos a través de un límite |
| [0037](lessons/0037-asyncio.md) | asyncio | Un hilo, miles de esperas y la llamada bloqueante que las paraliza todas |
| [0038](lessons/0038-choosing-a-model.md) | Elegir un modelo | Una sola pregunta lo decide, y la medición zanja el resto |
| [0039](lessons/0039-measuring-before-optimising.md) | Medir antes de optimizar | Adónde va realmente el tiempo, y por qué las microoptimizaciones que te enseñaron ya no sirven |
| [0040](lessons/0040-designing-an-api.md) | Diseñar una API | La firma es el contrato, y todo lo observable pasa a serlo tanto si lo pretendías como si no |
| [0041](lessons/0041-changing-a-published-api.md) | Cambiar una API publicada | Una deprecación que los usuarios ven de verdad, y qué cuenta como cambio incompatible |
| [0042](lessons/0042-reviewing-python.md) | Revisar Python | Qué buscar, en qué orden y cómo separar un defecto de una preferencia |
| [0043](lessons/0043-reading-the-source.md) | Leer el código fuente | Obtener la respuesta de la biblioteca estándar y de los PEP cuando la documentación se queda corta |
| [0044](lessons/0044-judgment.md) | Criterio | Cuándo romper las reglas de las etapas anteriores, y cómo defender la decisión |

## Referencia

- [Glosario](GLOSSARY.md): términos canónicos de este tema
- [Recursos](RESOURCES.md): fuentes de confianza, cada una anotada con lo que cubre
- [Mutabilidad y copia](reference/mutability-and-copying.md): qué tipos mutan, qué copia cada modismo de copia y quién puede verlo
- [Iteración y generadores](reference/iteration-and-generators.md): qué se consume una sola vez, qué sobrevive a una segunda pasada y qué herramienta de itertools encaja
- [Excepciones y limpieza](reference/exceptions-and-cleanup.md): la jerarquía, qué garantiza cada cláusula y qué excepción integrada lanzar
- [Tipado](reference/typing.md): las grafías actuales, las formas de estrechamiento, los códigos de error y qué forma usar en un límite
- [Proyecto y empaquetado](reference/project-and-packaging.md): un pyproject.toml anotado, la gramática de los especificadores y las comprobaciones antes de publicar
- [Modelo de datos](reference/data-model.md): el orden de búsqueda de atributos, el mapa de dunders, el protocolo de descriptores y qué hook sustituye a una metaclase
- [Pruebas](reference/testing.md): scopes de las fixtures, formas de parametrización, a qué doble recurrir y cómo leer un informe de cobertura
- [Concurrencia y rendimiento](reference/concurrency-and-performance.md): qué modelo para qué carga de trabajo, los números medidos que lo respaldan y cómo leer un perfil
- [API y revisión](reference/api-and-review.md): decisiones sobre firmas, qué cuenta como incompatible, la lista de comprobación de revisión y dónde encontrar una respuesta

## Cómo funciona

El arco está completo: las siete etapas están escritas, desde la lección 0001 hasta la lección 0044. Recórrelas en orden, o empieza por la etapa cuyo "Terminada cuando" todavía no puedas demostrar.

Cada lección es corta y autocontenida. Las claves de respuesta están plegadas: primero recuerda, luego ábrelas. Las prácticas en el mundo real importan más que la lectura, y espaciarlas es el punto. Todo lo que siga sin estar claro al final de una lección merece rastrearse hasta su fuente primaria antes de seguir.
