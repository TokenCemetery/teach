---
title: Contenedores
description: "Empaqueta un servicio como imagen de contenedor y hazte cargo de ella: primitivas del kernel, Dockerfiles, ejecutar, asegurar y depurar un contenedor"
type: topic
---

# Aprendizaje: contenedores

Empaqueta cualquier servicio como imagen de contenedor y hazte cargo de lo que le ocurre en un host: entiende qué está haciendo el kernel cuando corre un contenedor, escribe un Dockerfile que construya una imagen pequeña y reproducible, ejecútalo de modo que se detenga limpiamente y se mantenga dentro de sus límites, endurécelo y depúralo cuando no arranque. Termina siendo capaz de revisar el Dockerfile y la imagen de otra persona nombrando lo que cuesta cada elección.

**Última lección:** [24. Cuando la respuesta habitual es incorrecta](lessons/0024-when-the-usual-answer-is-wrong.md)

## Cómo se ve el éxito

- Explicar qué es un contenedor en términos del kernel (namespaces, cgroups y un sistema de archivos raíz por capas) y en qué se diferencia de una máquina virtual.
- Leer una imagen: su manifiesto, su configuración y sus capas, la diferencia entre un tag y un digest, y descargar exactamente la imagen que se probó.
- Escribir un Dockerfile que construya una imagen pequeña, que aproveche la caché y reproducible, usando un build multi-stage.
- Ejecutar un contenedor que se detenga limpiamente ante una señal, informe de su salud y se mantenga dentro de unos límites de memoria y CPU que respete el runtime que lleva dentro.
- Conectar contenedores en un host: red, puertos publicados, volúmenes para el estado y Compose para el desarrollo local.
- Endurecer una imagen: un usuario que no sea root, los mínimos privilegios, una base mínima, un escaneo de vulnerabilidades con triaje, los secretos fuera de las capas, y una firma y una procedencia que verificar.
- Depurar un contenedor que no arranca o se comporta mal, desde su código de salida hasta el interior de sus namespaces, incluido uno sin shell.
- Revisar el Dockerfile y la imagen de otra persona, propagar un cambio de imagen base por los servicios que dependen de ella y decir cuándo la respuesta habitual es la equivocada.

## Restricciones

- Se asume soltura en la línea de comandos de Linux y haber construido y ejecutado un servicio en algún lenguaje. No se requiere conocimiento previo de contenedores.
- Usa la CLI de Docker con BuildKit, porque es lo que usan la mayor parte de la documentación y de los equipos. Donde un comportamiento pertenece a las especificaciones OCI y no a Docker, la lección lo dice, y los mismos comandos funcionan en su mayoría en Podman.
- Las prácticas de la etapa 1 necesitan una shell de Linux con root, como una máquina Linux o una máquina virtual. En un portátil con Docker Desktop, los propios contenedores corren dentro de una máquina virtual Linux que gestiona Docker Desktop.

## Fuera de alcance

- Construir el artefacto ejecutable de un lenguaje. De eso se ocupan los tracks de cada lenguaje, y este track mete su salida en una imagen: [Go: comandos de la toolchain](../../programming/golang/reference/toolchain-commands.md) para binarios estáticos, [Java: pruebas y build](../../programming/java/reference/testing-and-build.md) y [El sistema de módulos](../../programming/java/reference/the-module-system.md) para artefactos ejecutables y `jlink`, [C#: entregar el servicio](../../programming/csharp/reference/shipping-the-service.md), y [Python: proyecto y empaquetado](../../programming/python/reference/project-and-packaging.md) para wheels.
- Orquestar contenedores en un clúster: planificación, services, rollouts, probes como funcionalidad del clúster. Eso es el [track de Kubernetes](../kubernetes/README.md). Este track se detiene en un contenedor, o unos pocos, en un host.
- Construir y publicar imágenes en un pipeline. Eso es el [track de CI/CD](../ci-cd/README.md), cuya hoja [Artefactos y versionado](../ci-cd/reference/artifacts-and-versioning.md) cubre el etiquetado y la publicación por digest. Este track construye imágenes a mano para entender primero lo que automatiza un pipeline.
- Los contenedores de Windows y escribir un runtime de contenedores.

## El arco

Ocho etapas, desde qué es un contenedor hasta el criterio para revisar la imagen de otra persona. Una etapa abarca varias lecciones y los límites son difusos; lo que da una etapa por terminada es la capacidad, no el número de lecciones.

| Etapa | Lecciones | Cubre | Terminada cuando |
|---|---|---|---|
| 1. Qué es un contenedor | 0001 a 0003 | Un contenedor como proceso, namespaces, cgroups, la diferencia con una máquina virtual | Puedes construir a mano el aislamiento de un contenedor y decir qué oculta o limita cada pieza |
| 2. Imágenes | 0004 a 0006 | Manifiesto, configuración y capas, overlayfs, la pila del runtime y el ciclo de vida, registros, tags y digests | Puedes leer una imagen y descargar exactamente la que se probó |
| 3. Construir imágenes | 0007 a 0010 | Instrucciones del Dockerfile y el contexto de build, la caché de build, builds multi-stage e imágenes base, reproducibilidad | Puedes escribir un Dockerfile que construya una imagen pequeña, que aproveche la caché y reproducible |
| 4. Ejecutar un contenedor | 0011 a 0013 | PID 1 y señales, health checks y políticas de reinicio, límites de memoria y CPU | Puedes ejecutar un contenedor que se detenga limpiamente, informe de su salud y respete sus límites |
| 5. Red, almacenamiento y Compose | 0014 a 0016 | Redes bridge y puertos publicados, volúmenes y bind mounts, Compose para el desarrollo local | Puedes ejecutar un servicio y sus dependencias juntos en un host con un estado que sobrevive |
| 6. Seguridad | 0017 a 0019 | No root, capabilities y privilegios, bases mínimas y escaneo, secretos de build, firma y procedencia | Puedes endurecer una imagen y verificar de dónde vino |
| 7. Depuración | 0020 a 0021 | Códigos de salida, logs e inspect, sobrescribir el entrypoint, unirse a los namespaces de un contenedor | Puedes averiguar por qué un contenedor no arranca o se comporta mal, incluso sin shell |
| 8. Criterio | 0022 a 0024 | Revisar un Dockerfile, cambiar una imagen base de la que dependen otros, cuándo la respuesta habitual es incorrecta, zanjarlo a partir de la especificación | Se confía en ti para tomar la decisión sobre una imagen y explicársela a otra persona |

## Lecciones

Recórrelas en orden.

| # | Lección | Enseña |
|---|---|---|
| [0001](lessons/0001-a-container-is-a-process.md) | Un contenedor es un proceso | Un contenedor es un proceso Linux corriente al que el kernel le muestra una vista restringida de la máquina, no una pequeña máquina virtual |
| [0002](lessons/0002-namespaces.md) | Namespaces | Cada tipo de namespace oculta un tipo de recurso global, y unshare construye la vista de un contenedor namespace a namespace |
| [0003](lessons/0003-cgroups.md) | Cgroups | Los control groups limitan y contabilizan la memoria, la CPU y los PID de un árbol de procesos, y qué hace el kernel cuando se alcanza un límite |
| [0004](lessons/0004-images-and-layers.md) | Imágenes y capas | Una imagen OCI es un manifiesto, una configuración y una pila de tarballs de capas que overlayfs fusiona en un único sistema de archivos raíz |
| [0005](lessons/0005-from-image-to-running-container.md) | De la imagen al contenedor en marcha | Lo que hace docker run entre la imagen y el proceso: la pila del runtime, la capa escribible y el ciclo de vida |
| [0006](lessons/0006-registries-tags-and-digests.md) | Registros, tags y digests | Un tag es un nombre móvil y un digest es el hash del contenido, así que descarga por digest para ejecutar exactamente lo que se probó |
| [0007](lessons/0007-your-first-dockerfile.md) | Tu primer Dockerfile | Las instrucciones que construyen una imagen, el contexto de build y lo que .dockerignore deja fuera de él |
| [0008](lessons/0008-the-build-cache.md) | La caché de build | Cuándo se reutiliza una capa cacheada, qué la invalida a ella y a todas las capas posteriores, y cómo el orden de las instrucciones decide el tiempo de reconstrucción |
| [0009](lessons/0009-multi-stage-builds.md) | Builds multi-stage | Construir en una etapa, copiar solo el artefacto a una etapa final mínima, y lo que cuesta cada elección de imagen base |
| [0010](lessons/0010-reproducible-builds.md) | Builds reproducibles | Qué hace que dos builds del mismo Dockerfile difieran, y fijar bases, paquetes y marcas de tiempo para que no lo hagan |
| [0011](lessons/0011-pid-1-and-signals.md) | PID 1 y señales | Por qué un contenedor ignora SIGTERM cuando su proceso es PID 1 o está envuelto en una shell, y cómo detenerse de forma ordenada |
| [0012](lessons/0012-health-checks-and-restart-policies.md) | Health checks y políticas de reinicio | Informar de si el proceso de dentro está funcionando de verdad, y decidir qué hace el runtime cuando se detiene |
| [0013](lessons/0013-resource-limits-in-practice.md) | Límites de recursos en la práctica | Fijar límites de memoria y CPU, interpretar un OOM kill y el throttling de CPU, y comprobar que el runtime de dentro ve el límite |
| [0014](lessons/0014-container-networking.md) | Red de contenedores | Los namespaces de red, los pares veth y un bridge conectan contenedores, y publicar un puerto añade una regla NAT en el host |
| [0015](lessons/0015-volumes-and-state.md) | Volúmenes y estado | Dónde sobreviven los datos a un contenedor en volúmenes con nombre, bind mounts y tmpfs, y la trampa de la propiedad de archivos entre el host y el contenedor |
| [0016](lessons/0016-compose-for-local-development.md) | Compose para el desarrollo local | Describir un servicio y sus dependencias en un solo archivo de Compose, y esperar a que una dependencia esté sana y no solo arrancada |
| [0017](lessons/0017-least-privilege.md) | Mínimo privilegio | Ejecutar como un usuario que no sea root, quitar capabilities, mantener de solo lectura el sistema de archivos raíz y saber lo que entregan el modo privilegiado y el socket de Docker |
| [0018](lessons/0018-minimal-bases-and-scanning.md) | Bases mínimas y escaneo | Reducir lo que contiene una imagen, leer un escaneo de vulnerabilidades y hacer triaje de sus hallazgos en lugar de perseguir un recuento de cero |
| [0019](lessons/0019-secrets-signing-and-provenance.md) | Secretos, firma y procedencia | Mantener los secretos fuera de las capas, firmar una imagen por digest y verificar dónde se construyó antes de ejecutarla |
| [0020](lessons/0020-a-container-that-will-not-start.md) | Un contenedor que no arranca | Leer el código de salida, los logs y la salida de inspect, y luego sobrescribir el entrypoint para averiguar por qué se detuvo |
| [0021](lessons/0021-debugging-a-running-container.md) | Depurar un contenedor en marcha | Entrar en un contenedor que no tiene shell uniéndose a sus namespaces desde un contenedor de depuración o desde el host |
| [0022](lessons/0022-reviewing-a-dockerfile.md) | Revisar un Dockerfile | Revisar el Dockerfile y la imagen de otra persona nombrando lo que cuesta cada elección en tamaño, tiempo de reconstrucción, seguridad y fiabilidad |
| [0023](lessons/0023-changing-a-base-image-others-depend-on.md) | Cambiar una imagen base de la que dependen otros | Hacer avanzar una imagen base compartida sin romper los servicios construidos sobre ella, usando tags, digests, reconstrucciones y deprecación |
| [0024](lessons/0024-when-the-usual-answer-is-wrong.md) | Cuando la respuesta habitual es incorrecta | Reconocer cuándo Alpine, distroless, un digest fijado o siquiera un contenedor es la decisión equivocada, y zanjarlo a partir de la especificación |

## Referencia

- [Glosario](GLOSSARY.md): términos canónicos de este tema
- [Recursos](RESOURCES.md): fuentes de confianza, cada una anotada con lo que cubre
- [Primitivas de los contenedores](reference/container-primitives.md): namespaces, cgroups, la estructura de la imagen y tags frente a digests, de las etapas 1 y 2
- [Dockerfile](reference/dockerfile.md): instrucciones, reglas de la caché, patrones multi-stage, imágenes base y reproducibilidad, de la etapa 3
- [Ejecutar contenedores](reference/running-containers.md): señales, health checks, límites, red, volúmenes y Compose, de las etapas 4 y 5
- [Seguridad de contenedores](reference/container-security.md): privilegios, bases mínimas, triaje de escaneos, secretos de build, firma y procedencia, de la etapa 6
- [Depurar contenedores](reference/debugging-containers.md): códigos de salida, los comandos que ejecutar en orden y cómo entrar en un contenedor sin shell, de la etapa 7
- [Lista de comprobación para revisar un Dockerfile](reference/dockerfile-review-checklist.md): las preguntas que hacerle al Dockerfile y a la imagen de otra persona, y cuándo la respuesta habitual es incorrecta, de la etapa 8

## Cómo funciona

Cada lección es corta y autocontenida. Las claves de respuesta están plegadas: primero recuerda, luego ábrelas. Las prácticas en el mundo real importan más que la lectura, y espaciarlas es el punto. Todo lo que siga sin estar claro al final de una lección merece rastrearse hasta su fuente primaria antes de seguir.
