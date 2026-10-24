---
title: Bash
description: "Escribe shell que sobreviva a producción: entrecomillado, código de salida, los modos de fallo y saber cuándo parar y usar un lenguaje de verdad"
type: topic
---

# Aprendizaje: Bash

Sé capaz de escribir y mantener scripts de shell para pipelines de CI, despliegue y herramientas operativas que no se rompan en silencio ante una entrada mala o una variable sin definir, y de reconocer cuándo un script se le ha quedado grande a la shell y pertenece a un lenguaje de verdad.

**Última lección:** [17. shellcheck, shfmt y probar un script](lessons/0017-shellcheck-shfmt-and-testing-a-script.md)

## Cómo se ve el éxito

- Escribir un script de CI/despliegue o una utilidad operativa que maneje correctamente el entrecomillado, el código de salida y los modos de fallo habituales, y explicar por qué cada elección era necesaria.
- Ante un script de shell, nombrar la forma concreta en que se rompería en un caso límite (expansión sin comillas, variable sin definir, código de salida de un comando ignorado).
- Reconocer cuándo un script ha salido de la zona en la que la shell no exige criterio y decir por qué el trabajo pertenece ahora a `programming/python`.

## Restricciones

- No se asume experiencia previa escribiendo scripts de shell.
- Escrito para la portabilidad de POSIX `sh` en lugar de modismos exclusivos de bash, aunque bash sea la casa del tema; cuando se usa una funcionalidad exclusiva de bash, se señala como tal.
- Se toca `awk`/`sed` solo donde un script los necesita de verdad, no como temas propios.

## Fuera de alcance

- Todo lo que hay más allá del punto en que un script debería haber dejado de ser shell: consulta [`programming/python`](../../programming/python/) para ese límite.

## El arco

Once etapas, del entrecomillado a shellcheck, shfmt y las pruebas. Una etapa abarca varias lecciones y los límites son difusos; lo que da una etapa por terminada es la capacidad, no el número de lecciones.

| Etapa | Lecciones | Cubre | Terminada cuando |
|---|---|---|---|
| 1. Entrecomillado | 0001 | El único hábito que evita la forma más común en que los scripts de shell se rompen en producción | Puedes entrecomillar correctamente y explicar por qué se rompe una expansión sin comillas |
| 2. Código de salida y manejo de errores | 0002 a 0003 | `$?`, el modo estricto no oficial (`set -euo pipefail`), `trap` | Puedes escribir un script que maneje correctamente el código de salida y los fallos |
| 3. Trampas de la división de palabras y el globbing | 0004 | La lista Bash Pitfalls, los errores habituales más allá del entrecomillado | Ante un script, puedes nombrar el caso límite concreto en el que se rompería |
| 4. Portabilidad | 0005 | POSIX `sh` frente a modismos exclusivos de bash, cuándo importa cada uno | Puedes escribir `sh` portable y señalar explícitamente una funcionalidad exclusiva de bash |
| 5. `awk`/`sed` donde hagan falta | 0006 | Usar cada uno solo donde un script lo necesita de verdad | Puedes recurrir a `awk`/`sed` ante una necesidad real sin abusar de ellos |
| 6. Saber cuándo parar | 0007 | Reconocer que un script ha salido de la zona en la que la shell no exige criterio | Puedes decir por qué un trabajo dado pertenece ahora a `programming/python` |
| 7. Fundamentos de la shell | 0008 a 0009 | Variables, sustitución de comandos, flujo de control (`if`/`case`/bucles), funciones, `local`, código de retorno frente a salida | Puedes escribir un script con variables, sustitución de comandos y flujo de control, y organizar el trabajo repetido en funciones con el ámbito correcto |
| 8. Expansión de parámetros y arrays | 0010 a 0011 | Valor por defecto o error ante una variable sin definir (`${v:-}`, `${v:?}`), recorte (`${v%%}`), sustitución, arrays indexados y asociativos | Puedes dar un valor por defecto, validar y transformar un valor en línea, y guardar una lista o un mapa sin codificarlo en un string |
| 9. Redirección y composición | 0012 a 0013 | Orden de las redirecciones, descriptores de archivo, here-docs, por qué un bucle `while` en un pipe pierde sus variables, sustitución de procesos | Puedes redirigir los flujos correctamente y explicar por qué una variable asignada dentro de un bucle en un pipe no sobrevive a él |
| 10. Argumentos y control de trabajos | 0014 a 0015 | `getopts`, una convención de uso/ayuda, señales, trabajos en segundo plano, `wait` | Puedes analizar las propias opciones y argumentos de un script, y gestionar correctamente el trabajo en segundo plano y su propio apagado |
| 11. Seguridad y herramientas | 0016 a 0017 | `mktemp`, la superficie de `eval`/inyección, ShellCheck, `shfmt`, pruebas con bats/shunit2 | Puedes crear archivos temporales y comandos dinámicos de forma segura, y usar análisis estático y pruebas para detectar lo que la revisión por sí sola pasaría por alto |

## Lecciones

Recórrelas en orden.

| # | Lección | Enseña |
|---|---|---|
| [0001](lessons/0001-quoting.md) | Entrecomillado | El único hábito que evita la forma más común en que los scripts de shell se rompen en producción |
| [0002](lessons/0002-exit-status.md) | Código de salida | Qué informa realmente $?, por qué bash sigue ejecutándose por defecto tras un comando fallido y la segunda forma más común en que un script se rompe en producción |
| [0003](lessons/0003-strict-mode-and-trap.md) | Modo estricto y trap | Qué cambia realmente cada opción de set -euo pipefail, sus huecos reales y cómo usar trap para limpiar de forma fiable cuando un script falla |
| [0004](lessons/0004-word-splitting-and-globbing-pitfalls.md) | Trampas de la división de palabras y el globbing | Errores habituales más allá de una simple comilla que falta, donde el entrecomillado por sí solo no es toda la solución |
| [0005](lessons/0005-portability.md) | Portabilidad | Qué garantiza realmente POSIX sh, qué funcionalidades habituales de bash no forman parte de él y cuándo importa de verdad la diferencia |
| [0006](lessons/0006-awk-and-sed-where-needed.md) | awk y sed donde hagan falta | Reconocer la forma de tarea a la que se ajusta cada uno de sed y awk, y recurrir a uno solo cuando un script lo necesita de verdad, no por costumbre |
| [0007](lessons/0007-knowing-when-to-stop.md) | Saber cuándo parar | Las señales concretas de que un script ha salido de la zona en la que la shell no exige criterio, y por qué el trabajo pertenece ahora a un lenguaje de verdad |
| [0008](lessons/0008-variables-command-substitution-and-control-flow.md) | Variables, sustitución de comandos y flujo de control | El vocabulario propio de la shell para guardar un valor, capturar la salida de un comando y ramificar o iterar sobre ella |
| [0009](lessons/0009-functions-local-and-return-status-vs-output.md) | Funciones, local y código de retorno frente a salida | Organizar el trabajo repetido en una función, y lo más marcado que una función de shell hace de forma distinta a una función en casi cualquier otro lenguaje |
| [0010](lessons/0010-parameter-expansion.md) | Expansión de parámetros | Dar un valor por defecto, fallar con error y recortar un valor en línea, sin recurrir a un comando aparte |
| [0011](lessons/0011-arrays.md) | Arrays (indexados y asociativos) | Guardar más de un valor sin codificar la estructura en un string, y la única forma de entrecomillado que mantiene intacto cada elemento |
| [0012](lessons/0012-redirection-file-descriptors-and-here-docs.md) | Redirección, descriptores de archivo y here-docs | Enviar la salida de un comando a algún sitio que no sea la pantalla, con precisión, y alimentarlo con un bloque de entrada en línea |
| [0013](lessons/0013-pipes-subshells-and-process-substitution.md) | Pipes, subshells y sustitución de procesos | Por qué una variable asignada dentro de un bucle en un pipe desaparece en cuanto termina el pipe, y la solución exclusiva de bash que la conserva |
| [0014](lessons/0014-argument-parsing-with-getopts.md) | Análisis de argumentos con getopts y una convención de uso | Analizar las propias opciones y argumentos de un script con la misma disciplina con la que se supone que analiza todo lo demás |
| [0015](lessons/0015-signals-background-jobs-and-wait.md) | Señales, trabajos en segundo plano y wait | Ejecutar trabajo de forma concurrente dentro de un script, y asegurarse de que el propio apagado del script no lo deje huérfano |
| [0016](lessons/0016-mktemp-safe-temp-files-and-the-eval-injection-surface.md) | mktemp, archivos temporales seguros y la superficie de eval/inyección | Crear un archivo temporal que no se pueda predecir ni secuestrar, y por qué eval convierte una entrada no confiable en código arbitrario |
| [0017](lessons/0017-shellcheck-shfmt-and-testing-a-script.md) | shellcheck, shfmt y probar un script | La herramienta que detecta la mayoría de las roturas silenciosas de un script antes de que llegue a ejecutarse, y cómo probar el resto |

## Referencia

- [Glosario](GLOSSARY.md): términos canónicos de este tema
- [Recursos](RESOURCES.md): fuentes de confianza
- [Entrecomillado y trampas](reference/quoting-and-pitfalls.md): la regla del entrecomillado, dónde muerde y las Bash Pitfalls que sobreviven a un entrecomillado cuidadoso
- [Código de salida y manejo de errores](reference/exit-status-and-error-handling.md): `$?`, las opciones de `set -euo pipefail` y sus excepciones reales, y `trap` para una limpieza garantizada
- [Portabilidad](reference/portability.md): POSIX `sh` frente a funcionalidades exclusivas de bash, la regla de honestidad del shebang y cuándo vale la pena el compromiso
- [awk, sed y saber cuándo parar](reference/awk-sed-and-when-to-stop.md): ajustar la herramienta a la forma de la tarea, y las señales concretas de que un script se le ha quedado grande a la shell

## Cómo funciona

Cada lección es corta y autocontenida. Las claves de respuesta están plegadas: primero recuerda, luego ábrelas. Las prácticas en el mundo real importan más que la lectura, y espaciarlas es el punto. Todo lo que siga sin estar claro al final de una lección merece rastrearse hasta su fuente primaria antes de seguir.
