---
title: Kubernetes
description: "Run services on a Kubernetes cluster and own them: the reconciliation loop, workloads, networking, configuration, reliability, security, packaging and debugging"
type: topic
---

# Learning: Kubernetes

Run any containerized service on a Kubernetes cluster and own what happens to it there: describe it in manifests the cluster reconciles, expose it, configure it, keep it healthy through rollouts, node failures and load, lock it down, package it for several environments, and find out why it is broken when it is. End able to review someone else's manifests by naming what each choice costs, upgrade what other teams depend on without breaking them, and say when a service does not need Kubernetes at all.

**Latest lesson:** [28. When Kubernetes Is the Wrong Answer](lessons/0028-when-kubernetes-is-the-wrong-answer.md)

## Success looks like

- Explain the declarative model: desired state stored through the API server, controllers reconciling the cluster toward it, and what that means when a pod is deleted or a node dies.
- Read and write manifests: the fields every object has, labels and selectors, namespaces, and applying changes with `kubectl apply`.
- Run a stateless service with a Deployment, roll out a new version and roll it back, and run batch work and per-node agents with Jobs, CronJobs and DaemonSets.
- Expose a service inside the cluster with a Service and cluster DNS, and outside it with Ingress or the Gateway API.
- Configure a workload with ConfigMaps and Secrets, and say what a Secret does and does not protect.
- Keep a workload healthy: probes that answer the right question, a clean termination, and requests and limits that set its QoS class.
- Run stateful workloads on persistent storage, place pods with scheduling constraints, scale them automatically, and keep voluntary disruptions from taking a service down.
- Lock a workload down with RBAC, service accounts, network policy and pod security.
- Package manifests for several environments with Kustomize or Helm, and choose between them by what each costs.
- Observe a workload and debug one that is Pending, crashing or unreachable, from events and logs to a debug container.
- Review someone else's manifests, upgrade a cluster or a shared chart that other teams depend on, say when Kubernetes or one of its usual defaults is the wrong answer, and settle a disputed question from the API reference.

## Constraints

- Assumes the [containers track](../containers/README.md) or equivalent: building an image, running one container, signals, health checks and limits on one host. No prior knowledge of Kubernetes.
- Every rep runs on a local cluster created with kind, which needs Docker or Podman and a few gigabytes of memory, plus `kubectl`. No cloud account is needed. Where a lesson's behaviour depends on a cloud provider (a `LoadBalancer` Service, a node autoscaler, a cloud storage class), it says so and teaches the part kind can show.
- Uses upstream Kubernetes and its documentation. Managed offerings (EKS, GKE, AKS) differ in defaults and add-ons, and the lessons name a difference only where it changes the answer.

## Out of scope

- Building and running one container. That is the [containers track](../containers/README.md), whose [Running Containers](../containers/reference/running-containers.md) sheet is the single-host version of stage 5 here.
- Making a service observable and stoppable from inside its own code: health endpoints, signal handling, graceful shutdown. The language tracks own that, for example Go's [Graceful Shutdown](../../programming/golang/lessons/0025-graceful-shutdown.md) and C#'s [Logging and Health Checks](../../programming/csharp/lessons/0039-logging-and-health-checks.md). This track teaches what the cluster does with those signals.
- Consensus and partial failure as theory. That is [Distributed Systems](../../architecture/distributed-systems/README.md), whose [Consensus](../../architecture/distributed-systems/reference/consensus.md) sheet explains what etcd is doing underneath. This track teaches what reconciliation and etcd mean for someone running workloads.
- Delivering a change to the cluster from a pipeline, and GitOps tools. That is a planned `infrastructure/ci-cd` track ([#159](https://github.com/TokenCemetery/teach/issues/159)).
- Installing and operating the control plane itself (etcd backups, certificate rotation, building a cluster from scratch), writing controllers or operators, and service meshes.

## The arc

Ten stages, from the reconciliation loop to the judgment to review someone else's manifests. A stage takes several lessons and the boundaries are soft; what makes a stage done is the capability, not the lesson count.

| Stage | Lessons | Covers | Done when |
|---|---|---|---|
| 1. The declarative model | 0001 to 0003 | Cluster, control plane and nodes, the API server, etcd and controllers, the reconciliation loop, object fields, labels, namespaces, `kubectl apply` | Can predict what the cluster does after a change to desired state, and write a manifest it accepts |
| 2. Workloads | 0004 to 0007 | Pods, Deployments and ReplicaSets, rolling updates and rollbacks, Jobs, CronJobs and DaemonSets | Can run a stateless service, roll it forward and back, and pick the controller for work that is not a service |
| 3. Networking | 0008 to 0010 | Services and EndpointSlices, kube-proxy, cluster DNS, Ingress and the Gateway API | Can make a workload reachable inside and outside the cluster and say which hop failed when it is not |
| 4. Configuration | 0011 to 0012 | ConfigMaps as environment and files, Secrets, encryption at rest, keeping secrets out of Git | Can configure a workload per environment and say what protects its secrets |
| 5. Running reliably | 0013 to 0015 | Liveness, readiness and startup probes, termination and the endpoint race, requests, limits and QoS classes | Can run a workload that takes traffic only when ready, drains cleanly and is not the first one evicted |
| 6. State, scheduling and scale | 0016 to 0019 | PersistentVolumes and claims, StatefulSets, affinity, taints and topology spread, autoscaling, PodDisruptionBudgets | Can run a stateful workload, place pods deliberately, and scale and drain without an outage |
| 7. Security | 0020 to 0021 | RBAC, service accounts, NetworkPolicy, security contexts, Pod Security Standards | Can grant least privilege to people and pods and restrict what a pod can reach and do |
| 8. Packaging | 0022 to 0023 | Kustomize bases and overlays, Helm charts, values and releases, choosing between them | Can ship one set of manifests to several environments and defend the tool chosen |
| 9. Observability and debugging | 0024 to 0025 | Resource metrics, events, logs, kube-state-metrics, the failure states and the commands that explain them, debug containers | Can find out why a workload is Pending, crashing or unreachable |
| 10. Judgment | 0026 to 0028 | Reviewing manifests, upgrading a cluster or shared chart others depend on, when Kubernetes or a default is wrong, settling it from the API reference | Trusted to make the call on a workload and to explain it to someone else |

## Lessons

Work through these in order.

| # | Lesson | Teaches |
|---|---|---|
| [0001](lessons/0001-what-kubernetes-is-for.md) | What Kubernetes Is For | A cluster turns many machines into one place to run containers, and the control plane and the nodes split the work |
| [0002](lessons/0002-the-reconciliation-loop.md) | The Reconciliation Loop | You declare desired state through the API server, and controllers keep watching and acting until the cluster matches it |
| [0003](lessons/0003-objects-and-manifests.md) | Objects and Manifests | Every object has apiVersion, kind, metadata, spec and status, and labels, selectors, namespaces and kubectl apply all work on those fields |
| [0004](lessons/0004-pods.md) | Pods | A pod is the unit the cluster schedules, containers that share a network namespace and volumes, and why you rarely create one yourself |
| [0005](lessons/0005-deployments-and-replicasets.md) | Deployments and ReplicaSets | A Deployment owns ReplicaSets that own pods, so a deleted pod is replaced and a changed template becomes a new ReplicaSet |
| [0006](lessons/0006-rollouts-and-rollbacks.md) | Rollouts and Rollbacks | Roll out a new version with maxSurge and maxUnavailable, watch it, pause it, and roll it back to a known revision |
| [0007](lessons/0007-jobs-cronjobs-and-daemonsets.md) | Jobs, CronJobs and DaemonSets | Run work that finishes, work on a schedule, and one pod per node, and the failure mode each one has |
| [0008](lessons/0008-services.md) | Services | A Service gives a changing set of pods one stable virtual IP, and EndpointSlices and kube-proxy route to the ready ones |
| [0009](lessons/0009-cluster-dns.md) | Cluster DNS | How a pod finds a Service by name, what the search path and ndots do to every lookup, and what a headless Service returns |
| [0010](lessons/0010-ingress-and-the-gateway-api.md) | Ingress and the Gateway API | Bring outside HTTP traffic into the cluster through a controller, and why the Gateway API splits the job by role |
| [0011](lessons/0011-configmaps.md) | ConfigMaps | Inject configuration as environment variables or files, and know which of the two sees a change without a restart |
| [0012](lessons/0012-secrets.md) | Secrets | A Secret is base64, not encryption, so what protects it is RBAC, encryption at rest and keeping it out of Git |
| [0013](lessons/0013-probes.md) | Probes | Liveness, readiness and startup probes answer different questions, and the wrong liveness probe causes the outage it was meant to stop |
| [0014](lessons/0014-pod-termination.md) | Pod Termination | What happens between a delete and SIGKILL, and why a pod still gets traffic after SIGTERM unless you plan for it |
| [0015](lessons/0015-requests-limits-and-qos.md) | Requests, Limits and QoS | Requests drive scheduling and limits drive enforcement, and together they set the QoS class that decides who is evicted first |
| [0016](lessons/0016-persistent-storage.md) | Persistent Storage | Claim storage with a PersistentVolumeClaim, let a StorageClass provision it, and know what access modes and reclaim policies promise |
| [0017](lessons/0017-statefulsets.md) | StatefulSets | Stable names, ordered startup and a volume per replica, and why a StatefulSet alone does not make a database safe to run |
| [0018](lessons/0018-scheduling.md) | Scheduling | Steer pods with node selectors, affinity, topology spread, taints and tolerations, and read why a pod stays Pending |
| [0019](lessons/0019-autoscaling-and-disruptions.md) | Autoscaling and Disruptions | Scale pods with the HorizontalPodAutoscaler and nodes with a node autoscaler, and stop a drain taking too many down with a PodDisruptionBudget |
| [0020](lessons/0020-rbac-and-service-accounts.md) | RBAC and Service Accounts | Grant a person or a pod exactly the verbs it needs with Roles and bindings, and check it with kubectl auth can-i |
| [0021](lessons/0021-network-policy-and-pod-security.md) | Network Policy and Pod Security | Deny traffic between pods by default, then restrict what a pod may do on its node with security contexts and Pod Security Standards |
| [0022](lessons/0022-kustomize.md) | Kustomize | Keep one base of plain manifests and patch it per environment with overlays, without a template language |
| [0023](lessons/0023-helm-against-kustomize.md) | Helm Against Kustomize | Install and write a Helm chart, and choose between a chart and a Kustomize overlay by what each costs |
| [0024](lessons/0024-observability.md) | Observability | Read resource metrics, events, container logs and object state metrics, and know which question each one answers |
| [0025](lessons/0025-debugging-a-workload.md) | Debugging a Workload | Work from Pending, ImagePullBackOff, CrashLoopBackOff and OOMKilled to the cause with describe, events, logs and kubectl debug |
| [0026](lessons/0026-reviewing-manifests.md) | Reviewing Manifests | Review someone else's manifests by naming what each choice costs in availability, security and operability |
| [0027](lessons/0027-upgrading-what-others-depend-on.md) | Upgrading What Others Depend On | Move a cluster or a shared chart past a removed API version without breaking the teams whose workloads depend on it |
| [0028](lessons/0028-when-kubernetes-is-the-wrong-answer.md) | When Kubernetes Is the Wrong Answer | Say when a service does not need Kubernetes or a usual default is wrong, and settle a disputed question from the API reference |

## Reference

- [Glossary](GLOSSARY.md): canonical terms for this topic
- [Resources](RESOURCES.md): trusted sources, each annotated with what it covers
- [kubectl](reference/kubectl.md): the commands by task, from inspecting objects to rollouts, debugging and permission checks, across the arc
- [Workloads](reference/workloads.md): object fields, labels and selectors, pods, Deployments, rollouts, Jobs, CronJobs and DaemonSets, from stages 1 and 2
- [Networking](reference/networking.md): Service types, EndpointSlices, DNS names and ndots, Ingress and Gateway API resources, from stage 3
- [Configuration](reference/configuration.md): ConfigMaps and Secrets as environment and files, update behaviour, and what protects a Secret, from stage 4
- [Running Reliably](reference/running-reliably.md): the three probes, the termination sequence, requests, limits and QoS classes, from stage 5
- [State, Scheduling and Scale](reference/state-scheduling-and-scale.md): storage, StatefulSets, placement constraints, autoscalers and disruption budgets, from stage 6
- [Cluster Security](reference/cluster-security.md): RBAC objects, service account tokens, NetworkPolicy patterns and Pod Security Standards, from stage 7
- [Packaging](reference/packaging.md): Kustomize and Helm side by side, and when each one fits, from stage 8
- [Debugging Workloads](reference/debugging-workloads.md): each failure state, what causes it and the commands to run in order, from stage 9
- [Manifest Review Checklist](reference/manifest-review-checklist.md): the questions to ask of someone else's manifests, and when the usual answer is wrong, from stage 10

## How this works

Each lesson is short and self-contained. Answer keys are collapsed: recall first, then open them. The real-world reps matter more than the reading, and spacing them out is the point. Anything still unclear at the end of a lesson is worth chasing to its primary source before moving on.
