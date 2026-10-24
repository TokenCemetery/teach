---
title: Kubernetes
description: "Ejecuta servicios en un clúster de Kubernetes y hazte cargo de ellos: el bucle de reconciliación, cargas de trabajo, red, configuración, fiabilidad, seguridad, empaquetado y depuración"
type: topic
---

# Aprendizaje: Kubernetes

Ejecuta cualquier servicio en contenedores en un clúster de Kubernetes y hazte cargo de lo que le ocurre allí: descríbelo en manifiestos que el clúster reconcilia, exponlo, configúralo, mantenlo sano a través de rollouts, caídas de nodos y carga, ciérralo, empaquétalo para varios entornos y averigua por qué está roto cuando lo esté. Termina siendo capaz de revisar los manifiestos de otra persona nombrando lo que cuesta cada elección, de actualizar aquello de lo que dependen otros equipos sin romperlos y de decir cuándo un servicio no necesita Kubernetes en absoluto.

**Última lección:** [28. Cuando Kubernetes es la respuesta equivocada](lessons/0028-when-kubernetes-is-the-wrong-answer.md)

## Cómo se ve el éxito

- Explicar el modelo declarativo: el estado deseado guardado a través del API server, los controladores reconciliando el clúster hacia él y lo que eso significa cuando se borra un pod o muere un nodo.
- Leer y escribir manifiestos: los campos que tiene todo objeto, labels y selectors, namespaces, y aplicar cambios con `kubectl apply`.
- Ejecutar un servicio sin estado con un Deployment, desplegar una nueva versión y hacer rollback, y ejecutar trabajo por lotes y agentes por nodo con Jobs, CronJobs y DaemonSets.
- Exponer un servicio dentro del clúster con un Service y el DNS del clúster, y fuera de él con Ingress o la Gateway API.
- Configurar una carga de trabajo con ConfigMaps y Secrets, y decir qué protege un Secret y qué no.
- Mantener sana una carga de trabajo: probes que respondan a la pregunta correcta, una terminación limpia, y requests y limits que fijen su clase de QoS.
- Ejecutar cargas de trabajo con estado sobre almacenamiento persistente, colocar pods con restricciones de planificación, escalarlos automáticamente e impedir que las interrupciones voluntarias tumben un servicio.
- Cerrar una carga de trabajo con RBAC, service accounts, network policy y pod security.
- Empaquetar manifiestos para varios entornos con Kustomize o Helm, y elegir entre ellos según lo que cuesta cada uno.
- Observar una carga de trabajo y depurar una que está Pending, que se cae o que es inalcanzable, desde los eventos y los logs hasta un contenedor de depuración.
- Revisar los manifiestos de otra persona, actualizar un clúster o un chart compartido del que dependen otros equipos, decir cuándo Kubernetes o uno de sus valores por defecto habituales es la respuesta equivocada y zanjar una cuestión disputada a partir de la referencia de la API.

## Restricciones

- Se asume el [track de contenedores](../containers/README.md) o equivalente: construir una imagen, ejecutar un contenedor, señales, health checks y límites en un host. No se requiere conocimiento previo de Kubernetes.
- Cada práctica se ejecuta en un clúster local creado con kind, que necesita Docker o Podman y unos pocos gigabytes de memoria, además de `kubectl`. No hace falta ninguna cuenta en la nube. Donde el comportamiento de una lección depende de un proveedor de nube (un Service `LoadBalancer`, un autoescalador de nodos, una storage class de la nube), lo dice y enseña la parte que kind puede mostrar.
- Usa Kubernetes upstream y su documentación. Las ofertas gestionadas (EKS, GKE, AKS) difieren en valores por defecto y complementos, y las lecciones nombran una diferencia solo donde cambia la respuesta.

## Fuera de alcance

- Construir y ejecutar un contenedor. Eso es el [track de contenedores](../containers/README.md), cuya hoja [Ejecutar contenedores](../containers/reference/running-containers.md) es la versión en un solo host de la etapa 5 de aquí.
- Hacer que un servicio sea observable y se pueda detener desde dentro de su propio código: endpoints de salud, manejo de señales, apagado ordenado. De eso se ocupan los tracks de cada lenguaje, por ejemplo [Apagado ordenado](../../programming/golang/lessons/0025-graceful-shutdown.md) de Go y [Logging y health checks](../../programming/csharp/lessons/0039-logging-and-health-checks.md) de C#. Este track enseña lo que hace el clúster con esas señales.
- El consenso y el fallo parcial como teoría. Eso es [Sistemas distribuidos](../../architecture/distributed-systems/README.md), cuya hoja [Consenso](../../architecture/distributed-systems/reference/consensus.md) explica lo que hace etcd por debajo. Este track enseña lo que significan la reconciliación y etcd para quien ejecuta cargas de trabajo.
- Entregar un cambio al clúster desde un pipeline, y las herramientas de GitOps. Eso es el [track de CI/CD](../ci-cd/README.md), cuya hoja [Despliegues](../ci-cd/reference/deployments.md) cubre las estrategias de despliegue, el rollback y la elección entre un despliegue push y GitOps.
- Instalar y operar el propio control plane (backups de etcd, rotación de certificados, construir un clúster desde cero), escribir controladores u operadores, y los service meshes.

## El arco

Diez etapas, desde el bucle de reconciliación hasta el criterio para revisar los manifiestos de otra persona. Una etapa abarca varias lecciones y los límites son difusos; lo que da una etapa por terminada es la capacidad, no el número de lecciones.

| Etapa | Lecciones | Cubre | Terminada cuando |
|---|---|---|---|
| 1. El modelo declarativo | 0001 a 0003 | Clúster, control plane y nodos, el API server, etcd y los controladores, el bucle de reconciliación, campos de los objetos, labels, namespaces, `kubectl apply` | Puedes predecir lo que hace el clúster tras un cambio en el estado deseado, y escribir un manifiesto que acepte |
| 2. Cargas de trabajo | 0004 a 0007 | Pods, Deployments y ReplicaSets, rolling updates y rollbacks, Jobs, CronJobs y DaemonSets | Puedes ejecutar un servicio sin estado, hacerlo avanzar y retroceder, y elegir el controlador para el trabajo que no es un servicio |
| 3. Red | 0008 a 0010 | Services y EndpointSlices, kube-proxy, DNS del clúster, Ingress y la Gateway API | Puedes hacer alcanzable una carga de trabajo dentro y fuera del clúster y decir qué salto falló cuando no lo es |
| 4. Configuración | 0011 a 0012 | ConfigMaps como entorno y como archivos, Secrets, cifrado en reposo, mantener los secretos fuera de Git | Puedes configurar una carga de trabajo por entorno y decir qué protege sus secretos |
| 5. Ejecutar de forma fiable | 0013 a 0015 | Probes de liveness, readiness y startup, la terminación y la carrera de los endpoints, requests, limits y clases de QoS | Puedes ejecutar una carga de trabajo que solo recibe tráfico cuando está lista, se drena limpiamente y no es la primera en ser desalojada |
| 6. Estado, planificación y escala | 0016 a 0019 | PersistentVolumes y claims, StatefulSets, afinidad, taints y topology spread, autoescalado, PodDisruptionBudgets | Puedes ejecutar una carga de trabajo con estado, colocar pods de forma deliberada, y escalar y drenar sin una caída |
| 7. Seguridad | 0020 a 0021 | RBAC, service accounts, NetworkPolicy, security contexts, Pod Security Standards | Puedes conceder el mínimo privilegio a personas y pods y restringir a qué puede llegar un pod y qué puede hacer |
| 8. Empaquetado | 0022 a 0023 | Bases y overlays de Kustomize, charts, values y releases de Helm, elegir entre ellos | Puedes entregar un mismo conjunto de manifiestos a varios entornos y defender la herramienta elegida |
| 9. Observabilidad y depuración | 0024 a 0025 | Métricas de recursos, eventos, logs, kube-state-metrics, los estados de fallo y los comandos que los explican, contenedores de depuración | Puedes averiguar por qué una carga de trabajo está Pending, se cae o es inalcanzable |
| 10. Criterio | 0026 a 0028 | Revisar manifiestos, actualizar un clúster o un chart compartido del que dependen otros, cuándo Kubernetes o un valor por defecto es incorrecto, zanjarlo a partir de la referencia de la API | Se confía en ti para tomar la decisión sobre una carga de trabajo y explicársela a otra persona |

## Lecciones

Recórrelas en orden.

| # | Lección | Enseña |
|---|---|---|
| [0001](lessons/0001-what-kubernetes-is-for.md) | Para qué sirve Kubernetes | Un clúster convierte muchas máquinas en un único lugar donde ejecutar contenedores, y el control plane y los nodos se reparten el trabajo |
| [0002](lessons/0002-the-reconciliation-loop.md) | El bucle de reconciliación | Declaras el estado deseado a través del API server, y los controladores siguen observando y actuando hasta que el clúster coincide con él |
| [0003](lessons/0003-objects-and-manifests.md) | Objetos y manifiestos | Todo objeto tiene apiVersion, kind, metadata, spec y status, y labels, selectors, namespaces y kubectl apply trabajan todos sobre esos campos |
| [0004](lessons/0004-pods.md) | Pods | Un pod es la unidad que planifica el clúster, contenedores que comparten un namespace de red y volúmenes, y por qué rara vez creas uno tú mismo |
| [0005](lessons/0005-deployments-and-replicasets.md) | Deployments y ReplicaSets | Un Deployment es dueño de ReplicaSets que son dueños de pods, así que un pod borrado se reemplaza y una plantilla cambiada se convierte en un ReplicaSet nuevo |
| [0006](lessons/0006-rollouts-and-rollbacks.md) | Rollouts y rollbacks | Desplegar una nueva versión con maxSurge y maxUnavailable, vigilarla, pausarla y hacer rollback a una revisión conocida |
| [0007](lessons/0007-jobs-cronjobs-and-daemonsets.md) | Jobs, CronJobs y DaemonSets | Ejecutar trabajo que termina, trabajo programado y un pod por nodo, y el modo de fallo que tiene cada uno |
| [0008](lessons/0008-services.md) | Services | Un Service le da a un conjunto cambiante de pods una única IP virtual estable, y EndpointSlices y kube-proxy enrutan hacia los que están listos |
| [0009](lessons/0009-cluster-dns.md) | DNS del clúster | Cómo encuentra un pod un Service por su nombre, qué le hacen la ruta de búsqueda y ndots a cada consulta, y qué devuelve un Service headless |
| [0010](lessons/0010-ingress-and-the-gateway-api.md) | Ingress y la Gateway API | Meter tráfico HTTP de fuera en el clúster a través de un controlador, y por qué la Gateway API reparte el trabajo por roles |
| [0011](lessons/0011-configmaps.md) | ConfigMaps | Inyectar configuración como variables de entorno o como archivos, y saber cuál de las dos ve un cambio sin reinicio |
| [0012](lessons/0012-secrets.md) | Secrets | Un Secret es base64, no cifrado, así que lo que lo protege es RBAC, el cifrado en reposo y mantenerlo fuera de Git |
| [0013](lessons/0013-probes.md) | Probes | Las probes de liveness, readiness y startup responden a preguntas distintas, y una probe de liveness equivocada causa la caída que debía evitar |
| [0014](lessons/0014-pod-termination.md) | Terminación de pods | Qué ocurre entre un delete y SIGKILL, y por qué un pod sigue recibiendo tráfico después de SIGTERM a menos que lo planifiques |
| [0015](lessons/0015-requests-limits-and-qos.md) | Requests, limits y QoS | Los requests guían la planificación y los limits guían la aplicación de límites, y juntos fijan la clase de QoS que decide quién es desalojado primero |
| [0016](lessons/0016-persistent-storage.md) | Almacenamiento persistente | Reclamar almacenamiento con un PersistentVolumeClaim, dejar que una StorageClass lo aprovisione y saber qué prometen los modos de acceso y las políticas de reclamación |
| [0017](lessons/0017-statefulsets.md) | StatefulSets | Nombres estables, arranque ordenado y un volumen por réplica, y por qué un StatefulSet por sí solo no hace seguro ejecutar una base de datos |
| [0018](lessons/0018-scheduling.md) | Planificación | Dirigir los pods con node selectors, afinidad, topology spread, taints y tolerations, e interpretar por qué un pod se queda Pending |
| [0019](lessons/0019-autoscaling-and-disruptions.md) | Autoescalado e interrupciones | Escalar pods con el HorizontalPodAutoscaler y nodos con un autoescalador de nodos, e impedir con un PodDisruptionBudget que un drenaje tumbe demasiados |
| [0020](lessons/0020-rbac-and-service-accounts.md) | RBAC y service accounts | Conceder a una persona o a un pod exactamente los verbos que necesita con Roles y bindings, y comprobarlo con kubectl auth can-i |
| [0021](lessons/0021-network-policy-and-pod-security.md) | Network policy y pod security | Denegar por defecto el tráfico entre pods, y luego restringir lo que puede hacer un pod en su nodo con security contexts y Pod Security Standards |
| [0022](lessons/0022-kustomize.md) | Kustomize | Mantener una sola base de manifiestos simples y parchearla por entorno con overlays, sin un lenguaje de plantillas |
| [0023](lessons/0023-helm-against-kustomize.md) | Helm frente a Kustomize | Instalar y escribir un chart de Helm, y elegir entre un chart y un overlay de Kustomize según lo que cuesta cada uno |
| [0024](lessons/0024-observability.md) | Observabilidad | Leer métricas de recursos, eventos, logs de contenedores y métricas del estado de los objetos, y saber a qué pregunta responde cada uno |
| [0025](lessons/0025-debugging-a-workload.md) | Depurar una carga de trabajo | Ir de Pending, ImagePullBackOff, CrashLoopBackOff y OOMKilled hasta la causa con describe, eventos, logs y kubectl debug |
| [0026](lessons/0026-reviewing-manifests.md) | Revisar manifiestos | Revisar los manifiestos de otra persona nombrando lo que cuesta cada elección en disponibilidad, seguridad y operabilidad |
| [0027](lessons/0027-upgrading-what-others-depend-on.md) | Actualizar aquello de lo que dependen otros | Llevar un clúster o un chart compartido más allá de una versión de API eliminada sin romper a los equipos cuyas cargas de trabajo dependen de él |
| [0028](lessons/0028-when-kubernetes-is-the-wrong-answer.md) | Cuando Kubernetes es la respuesta equivocada | Decir cuándo un servicio no necesita Kubernetes o un valor por defecto habitual es incorrecto, y zanjar una cuestión disputada a partir de la referencia de la API |

## Referencia

- [Glosario](GLOSSARY.md): términos canónicos de este tema
- [Recursos](RESOURCES.md): fuentes de confianza, cada una anotada con lo que cubre
- [kubectl](reference/kubectl.md): los comandos por tarea, desde inspeccionar objetos hasta rollouts, depuración y comprobación de permisos, a lo largo del arco
- [Cargas de trabajo](reference/workloads.md): campos de los objetos, labels y selectors, pods, Deployments, rollouts, Jobs, CronJobs y DaemonSets, de las etapas 1 y 2
- [Red](reference/networking.md): tipos de Service, EndpointSlices, nombres DNS y ndots, recursos de Ingress y de la Gateway API, de la etapa 3
- [Configuración](reference/configuration.md): ConfigMaps y Secrets como entorno y como archivos, comportamiento ante actualizaciones y qué protege un Secret, de la etapa 4
- [Ejecutar de forma fiable](reference/running-reliably.md): las tres probes, la secuencia de terminación, requests, limits y clases de QoS, de la etapa 5
- [Estado, planificación y escala](reference/state-scheduling-and-scale.md): almacenamiento, StatefulSets, restricciones de colocación, autoescaladores y presupuestos de interrupción, de la etapa 6
- [Seguridad del clúster](reference/cluster-security.md): objetos de RBAC, tokens de service accounts, patrones de NetworkPolicy y Pod Security Standards, de la etapa 7
- [Empaquetado](reference/packaging.md): Kustomize y Helm lado a lado, y cuándo encaja cada uno, de la etapa 8
- [Depurar cargas de trabajo](reference/debugging-workloads.md): cada estado de fallo, qué lo causa y los comandos que ejecutar en orden, de la etapa 9
- [Lista de comprobación para revisar manifiestos](reference/manifest-review-checklist.md): las preguntas que hacerles a los manifiestos de otra persona, y cuándo la respuesta habitual es incorrecta, de la etapa 10

## Cómo funciona

Cada lección es corta y autocontenida. Las claves de respuesta están plegadas: primero recuerda, luego ábrelas. Las prácticas en el mundo real importan más que la lectura, y espaciarlas es el punto. Todo lo que siga sin estar claro al final de una lección merece rastrearse hasta su fuente primaria antes de seguir.
