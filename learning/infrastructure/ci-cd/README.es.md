---
title: CI/CD
description: "Construye, prueba y entrega cada cambio a través de un pipeline y hazte cargo de él: workflows, feedback rápido, artefactos, secretos, despliegues, rollback y seguridad de la cadena de suministro"
type: topic
---

# Aprendizaje: CI/CD

Lleva cualquier servicio desde un cambio fusionado hasta producción a través de un pipeline del que te haces cargo: demuestra en minutos que cada cambio compila y pasa sus pruebas, produce un único artefacto versionado y promueve ese mismo artefacto por los entornos, dale al pipeline el acceso que necesita sin claves de larga duración, despliega con una estrategia que limite el daño de una release mala y haz rollback cuando se cuele una. Termina siendo capaz de revisar el pipeline de otra persona nombrando qué fallará, se ralentizará o filtrará primero, de cambiar un workflow del que dependen otros equipos sin romper sus merges y de decir cuándo la respuesta habitual de entrega es la equivocada.

**Última lección:** [30. Cuando la respuesta habitual es incorrecta](lessons/0030-when-the-usual-answer-is-wrong.md)

## Cómo se ve el éxito

- Explicar qué promete cada una de la integración continua, la entrega continua y el despliegue continuo, y qué tiene que practicar un equipo para que la promesa se cumpla.
- Escribir un pipeline como código: disparadores y eventos, jobs, steps y runners, actions, expresiones, contextos y outputs.
- Ejecutar etapas de build y de pruebas que fallen primero por el problema más barato, sobre una matriz, con caché, sin fiarse de una prueba inestable y lo bastante rápido como para que la gente espere el resultado.
- Producir artefactos con una versión trazable hasta un commit, construirlos una sola vez, y construir, publicar y referenciar una imagen de contenedor por digest.
- Darle a un pipeline secretos y acceso a la nube con mínimo privilegio: permisos acotados de `GITHUB_TOKEN`, OIDC en lugar de claves de larga duración y ningún camino por el que una entrada no confiable llegue a ninguno de los dos.
- Condicionar los despliegues con entornos y aprobaciones, y promover un mismo artefacto de staging a producción.
- Desplegar con estrategias rolling, blue-green y canary, hacer rollback o roll forward, ordenar las migraciones de base de datos alrededor de un despliegue y elegir entre un despliegue push y GitOps.
- Asegurar la cadena de suministro: fijar lo que ejecuta el pipeline, y producir y verificar procedencia y SBOM.
- Escalar los pipelines entre repositorios y monorepos con reusable workflows, composite actions y filtros de rutas, y depurar un pipeline que solo falla en el runner.
- Revisar el pipeline de otra persona, cambiar un workflow compartido o un check obligatorio sin romper a los equipos que dependen de él, decir cuándo la respuesta habitual es incorrecta y zanjar un comportamiento disputado a partir de la referencia de sintaxis de workflows.

## Restricciones

- Se asume soltura con Git, con una shell y con compilar y probar un proyecto en un lenguaje. No se requiere conocimiento previo de CI/CD. La lección 13 asume el [track de contenedores](../containers/README.md) o equivalente, y las lecciones 19 y 22 asumen lo básico del [track de Kubernetes](../kubernetes/README.md).
- Enseña las tareas que realiza un pipeline y las realiza con GitHub Actions, del mismo modo que `programming/java` enseña el ciclo de vida del build con Maven. Jenkins y GitLab CI aparecen solo donde su modelo es realmente distinto.
- Cada práctica se ejecuta en un repositorio público desechable en una cuenta gratuita de GitHub, donde los runners alojados por GitHub no cuestan nada. Las prácticas de despliegue despliegan en un clúster kind creado dentro del job, así que no hace falta ninguna cuenta en la nube. Donde una lección depende de un proveedor de nube, como una política de confianza de OIDC, muestra la parte que GitHub puede mostrar por sí solo y marca el resto como opcional.

## Fuera de alcance

- Compilar y probar el código de un lenguaje. Los tracks de cada lenguaje se ocupan de los comandos que ejecuta un step del pipeline, por ejemplo [Java: pruebas y build](../../programming/java/reference/testing-and-build.md), [Go: comandos de la toolchain](../../programming/golang/reference/toolchain-commands.md), [Python: proyecto y empaquetado](../../programming/python/reference/project-and-packaging.md) y [C#: pruebas y build](../../programming/csharp/reference/testing-and-build.md). Este track ejecuta esos steps en un pipeline.
- Escribir un Dockerfile y construir una imagen a mano. Eso es el [track de contenedores](../containers/README.md), cuya hoja [Dockerfile](../containers/reference/dockerfile.md) es lo que la lección 13 construye en un pipeline.
- Ejecutar la carga de trabajo una vez entregada: probes, rollouts como funcionalidad del clúster, empaquetado de manifiestos. Eso es el [track de Kubernetes](../kubernetes/README.md), cuya hoja [Empaquetado](../kubernetes/reference/packaging.md) cubre los manifiestos que aplica un job de despliegue. Este track le entrega el cambio, y enseña GitOps solo lo suficiente para poder elegirlo.
- Escribir una migración que no bloquee una tabla. Eso es [SQL](../../programming/sql/README.md), cuya hoja [Operación](../../programming/sql/reference/operating.md) contiene la tabla de seguridad de las migraciones. Este track ordena las migraciones dentro de un despliegue.
- Instalar y administrar un servidor de CI, escribir actions en JavaScript o de contenedor Docker y la publicación en tiendas de aplicaciones móviles.

## El arco

Diez etapas, desde lo que prometen CI y CD hasta el criterio para revisar el pipeline de otra persona. Una etapa abarca varias lecciones y los límites son difusos; lo que da una etapa por terminada es la capacidad, no el número de lecciones.

| Etapa | Lecciones | Cubre | Terminada cuando |
|---|---|---|---|
| 1. Para qué sirven CI y CD | 0001 a 0002 | Integración, entrega y despliegue como promesas, trabajo trunk-based, pipelines como código, los equivalentes en Jenkins y GitLab | Puedes decir qué garantiza un pipeline y leer cualquier archivo de workflow como código |
| 2. Anatomía de un workflow | 0003 a 0005 | Eventos y filtros, jobs, steps, runners, `needs`, actions, expresiones, contextos y outputs | Puedes escribir un workflow que se ejecute cuando se pretende y que pase datos entre jobs |
| 3. Feedback rápido y fiable | 0006 a 0010 | Orden de las etapas, service containers, matrices, caché, pruebas inestables, el camino crítico, concurrencia y timeouts | Puedes ejecutar un pipeline en el que la gente confía y cuyo resultado espera |
| 4. Artefactos y versionado | 0011 a 0013 | Artefactos frente a cachés, identidad del build, construir una sola vez, construir y publicar una imagen por digest | Puedes producir un único artefacto trazable y entregar ese mismo a cada etapa posterior |
| 5. Secretos y confianza | 0014 a 0016 | Secretos, enmascaramiento, permisos de `GITHUB_TOKEN`, federación OIDC, inyección de scripts, `pull_request_target` | Puedes darle a un pipeline solo el acceso que necesita y mantener lejos de él la entrada no confiable |
| 6. Entornos y promoción | 0017 a 0018 | Entornos, reglas de protección, secretos de entorno, promover un artefacto con configuración por entorno | Puedes condicionar un despliegue a producción y promover lo que se probó en staging |
| 7. Desplegar y hacer rollback | 0019 a 0022 | Recreate, rolling, blue-green y canary, rollback, roll forward y flags, migraciones expand and contract, despliegues push y GitOps | Puedes desplegar con una estrategia que limite el daño y deshacer una release mala |
| 8. Cadena de suministro | 0023 a 0024 | Fijar actions y dependencias, Dependabot, procedencia SLSA, attestations de artefactos, SBOM | Puedes decir qué ejecutó el pipeline y demostrar de dónde vino un artefacto |
| 9. Pipelines a escala | 0025 a 0027 | Reusable workflows, composite actions, filtros de rutas y checks obligatorios en monorepos, logging de depuración, diferencias del runner | Puedes compartir lógica de pipeline entre equipos y averiguar por qué falló una ejecución |
| 10. Criterio | 0028 a 0030 | Revisar un pipeline, cambiar un workflow compartido o un check obligatorio, cuándo la respuesta habitual es incorrecta, zanjarlo a partir de la referencia de sintaxis de workflows | Se confía en ti para tomar la decisión sobre un pipeline y explicársela a otra persona |

## Lecciones

Recórrelas en orden.

| # | Lección | Enseña |
|---|---|---|
| [0001](lessons/0001-what-ci-and-cd-promise.md) | Lo que prometen CI y CD | La integración continua mantiene cada cambio fusionado y probado en main, la entrega continua mantiene main listo para publicar y el despliegue continuo publica cada cambio que pasa |
| [0002](lessons/0002-pipelines-as-code.md) | Pipelines como código | Un archivo de workflow en el repositorio se versiona, se revisa y se ejecuta como el código que construye, y Jenkins y GitLab expresan la misma idea |
| [0003](lessons/0003-triggers-and-events.md) | Disparadores y eventos | Arrancar un workflow con un push, una pull request, una programación o a mano, filtrarlo por rama y ruta, y saber contra qué commit se ejecuta cada evento |
| [0004](lessons/0004-jobs-steps-and-runners.md) | Jobs, steps y runners | Los jobs se ejecutan en paralelo en runners nuevos salvo que needs los ordene, los steps comparten un mismo workspace, y los runners alojados y los autoalojados cambian costo por control |
| [0005](lessons/0005-actions-expressions-and-outputs.md) | Actions, expresiones y outputs | Reutilizar una action con uses, decidir con if y expresiones sobre contextos, y pasar valores entre steps y jobs a través de outputs |
| [0006](lessons/0006-build-and-test-stages.md) | Etapas de build y de pruebas | Ordenar las etapas de lint, build, pruebas unitarias y de integración para que el fallo más barato llegue primero, con service containers para las pruebas que necesitan una base de datos |
| [0007](lessons/0007-matrix-builds.md) | Builds con matriz | Ejecutar un job en varias versiones y plataformas con una matriz, y controlar lo que fail-fast, include y exclude le hacen a la ejecución |
| [0008](lessons/0008-caching.md) | Caché | Usar el lockfile como clave de una caché, recurrir a restore keys como respaldo y saber qué nunca hay que confiarle a una caché |
| [0009](lessons/0009-flaky-tests.md) | Pruebas inestables | Una prueba que falla sin un cambio de código destruye la confianza en todo el pipeline, así que hay que encontrar su causa y ponerla en cuarentena en lugar de esconderla tras reintentos |
| [0010](lessons/0010-making-a-pipeline-fast.md) | Hacer rápido un pipeline | Acortar el camino crítico, cancelar las ejecuciones superadas con grupos de concurrencia y fijar timeouts para que un job atascado no pueda retener la cola |
| [0011](lessons/0011-artifacts.md) | Artefactos | Pasar una salida del build entre jobs y conservarla después de la ejecución con artefactos, y por qué un artefacto no es una caché |
| [0012](lessons/0012-versioning-a-build.md) | Versionar un build | Darle a cada build una identidad trazable hasta su commit, y construirlo una sola vez para que lo probado sea lo que se publica |
| [0013](lessons/0013-building-and-publishing-an-image.md) | Construir y publicar una imagen | Construir, etiquetar y subir una imagen de contenedor desde un workflow, cachear sus capas y entregar su digest a las etapas posteriores |
| [0014](lessons/0014-secrets-and-the-github-token.md) | Secretos y el GITHUB_TOKEN | Guardar secretos por repositorio y por entorno, saber qué se le escapa al enmascaramiento y recortar el GITHUB_TOKEN con permissions |
| [0015](lessons/0015-oidc-instead-of-long-lived-keys.md) | OIDC en lugar de claves de larga duración | Dejar que una nube confíe en un token de corta duración emitido para una ejecución, y acotar esa confianza con el claim subject |
| [0016](lessons/0016-untrusted-input.md) | Entrada no confiable | Los títulos, los nombres de rama y el código de un fork son entrada de un atacante, y pull_request_target con un checkout del fork les entrega tus secretos |
| [0017](lessons/0017-environments-and-approvals.md) | Entornos y aprobaciones | Condicionar un despliegue con entornos, revisores obligatorios, reglas de ramas de despliegue y secretos de entorno |
| [0018](lessons/0018-promotion-between-environments.md) | Promoción entre entornos | Mover un artefacto ya construido de staging a producción por digest, con la configuración suministrada por entorno |
| [0019](lessons/0019-deployment-strategies.md) | Estrategias de despliegue | Recreate, rolling, blue-green y canary, lo que cuesta cada una en capacidad y en riesgo, y lo que tiene que medir un canary para significar algo |
| [0020](lessons/0020-rollback-and-roll-forward.md) | Rollback y roll forward | Hacer rollback volviendo a desplegar el último artefacto bueno, hacer roll forward cuando los datos ya han avanzado y separar el despliegue de la release con flags |
| [0021](lessons/0021-database-migrations-in-a-deploy.md) | Migraciones de base de datos en un despliegue | Ordenar los cambios de esquema alrededor del código con expand and contract para que cada versión que corra durante un despliegue funcione contra el esquema |
| [0022](lessons/0022-push-deploys-and-gitops.md) | Despliegues push y GitOps | Un pipeline que empuja a un clúster frente a un agente en el clúster que tira de Git, y lo que cada uno hace con las credenciales y la deriva |
| [0023](lessons/0023-pinning-what-the-pipeline-runs.md) | Fijar lo que ejecuta el pipeline | Fijar las actions de terceros a un SHA de commit completo, bloquear las dependencias y mantener las fijaciones al día con Dependabot |
| [0024](lessons/0024-provenance-and-sboms.md) | Procedencia y SBOM | Atestiguar dónde y a partir de qué se construyó un artefacto, listar lo que contiene y verificar ambas cosas antes de que se ejecute |
| [0025](lessons/0025-reusable-workflows-and-composite-actions.md) | Reusable workflows y composite actions | Compartir lógica de pipeline entre repositorios con un workflow llamado o con una composite action, y elegir según lo que puede contener cada uno |
| [0026](lessons/0026-monorepos-and-path-filters.md) | Monorepos y filtros de rutas | Ejecutar solo lo que toca un cambio con filtros de rutas, y por qué un check obligatorio omitido puede bloquear todos los merges |
| [0027](lessons/0027-debugging-a-pipeline.md) | Depurar un pipeline | Leer el log, volver a ejecutar con logging de depuración y averiguar qué difiere entre el runner y tu máquina cuando en local pasa |
| [0028](lessons/0028-reviewing-a-pipeline.md) | Revisar un pipeline | Revisar el workflow de otra persona nombrando qué fallará, se ralentizará o filtrará primero |
| [0029](lessons/0029-changing-a-shared-workflow.md) | Cambiar un workflow compartido | Cambiar un reusable workflow o un check obligatorio del que dependen otros equipos sin romper sus merges |
| [0030](lessons/0030-when-the-usual-answer-is-wrong.md) | Cuando la respuesta habitual es incorrecta | Decir cuándo el despliegue continuo, un canary o un valor por defecto del pipeline es la decisión equivocada, y zanjar un comportamiento disputado a partir de la referencia de sintaxis de workflows |

## Referencia

- [Glosario](GLOSSARY.md): términos canónicos de este tema
- [Recursos](RESOURCES.md): fuentes de confianza, cada una anotada con lo que cubre
- [Sintaxis de workflows](reference/workflow-syntax.md): disparadores, jobs, steps, expresiones, contextos y outputs, con los equivalentes en Jenkins y GitLab, de las etapas 1 y 2
- [Feedback rápido](reference/fast-feedback.md): orden de las etapas, matrices, claves de caché, tratamiento de pruebas inestables, concurrencia y timeouts, de la etapa 3
- [Artefactos y versionado](reference/artifacts-and-versioning.md): artefactos frente a cachés, esquemas de versión, construir una sola vez, tags y digests de imágenes, de la etapa 4
- [Seguridad del pipeline](reference/pipeline-security.md): secretos, permisos del token, OIDC, entrada no confiable, fijación y procedencia, de las etapas 5 y 8
- [Despliegues](reference/deployments.md): entornos, promoción, las cuatro estrategias, rollback, orden de las migraciones y GitOps, de las etapas 6 y 7
- [Pipelines a escala](reference/pipelines-at-scale.md): reusable workflows frente a composite actions, filtros de rutas, checks obligatorios y depuración de una ejecución, de la etapa 9
- [Lista de comprobación para revisar un pipeline](reference/pipeline-review-checklist.md): las preguntas que hacerle al pipeline de otra persona, y cuándo la respuesta habitual es incorrecta, de la etapa 10

## Cómo funciona

Cada lección es corta y autocontenida. Las claves de respuesta están plegadas: primero recuerda, luego ábrelas. Las prácticas en el mundo real importan más que la lectura, y espaciarlas es el punto. Todo lo que siga sin estar claro al final de una lección merece rastrearse hasta su fuente primaria antes de seguir.
