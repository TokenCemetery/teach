---
title: Glossary
description: "Canonical terms for running workloads on Kubernetes"
type: glossary
---

# Kubernetes Glossary

Canonical terms for the objects, controllers and mechanisms a workload on Kubernetes depends on. In this workspace "the cluster" means the control plane and its nodes together, "pod" is always lowercase, and an object's kind is written as Kubernetes spells it (`Deployment`, `ConfigMap`) when the kind itself is meant.

## Terms

**API server**:
The control plane component that serves the Kubernetes API, validates and admits every request, and is the only component that reads and writes etcd. Every other component, and `kubectl`, talks to the cluster through it.
_Avoid_: master, the API (ambiguous)

**ConfigMap**:
An object holding non-secret configuration as key-value pairs, which a pod consumes as environment variables or as files in a mounted volume.
_Avoid_: config file, properties

**Container runtime**:
The software on each node that pulls images and runs containers on the kubelet's behalf, such as containerd or CRI-O, reached through the Container Runtime Interface.
_Avoid_: Docker (one tool, no longer used directly by the kubelet), engine

**Control plane**:
The components that hold and act on the cluster's desired state: the API server, etcd, the scheduler and the controller manager.
_Avoid_: master node, management cluster

**Controller**:
A control loop that watches objects through the API server and acts to move the actual state toward the desired state in their spec. Deployments, ReplicaSets and Jobs are each driven by one.
_Avoid_: operator (a controller for a custom resource), daemon

**CronJob**:
A workload object that creates a Job on a schedule written in cron syntax.
_Avoid_: scheduled job, cron (the Unix daemon)

**DaemonSet**:
A workload object that runs one copy of a pod on every node, or on every node matching a selector, as nodes join and leave.
_Avoid_: agent deployment, system pod

**Deployment**:
A workload object that manages ReplicaSets to keep a number of identical, interchangeable pods running and to roll them from one template to the next.
_Avoid_: app, release (a Helm term)

**Desired state**:
What an object's spec says the world should look like. Controllers act until the observed state, reported in status, matches it.
_Avoid_: target state, config

**EndpointSlice**:
An object listing the addresses and readiness of the pods behind a Service, maintained by a controller from the Service's selector. kube-proxy and other consumers route from it.
_Avoid_: endpoints (the older object it replaces), backend list

**etcd**:
The consistent, replicated key-value store that holds every object in the cluster. It uses the Raft consensus algorithm, and only the API server talks to it.
_Avoid_: the database, cluster store

**Eviction**:
The kubelet or the API ending a pod to reclaim node resources or honour a drain. Node-pressure eviction ignores PodDisruptionBudgets, and API-initiated eviction respects them.
_Avoid_: kill, preemption (a scheduler action)

**Gateway API**:
A family of objects (`GatewayClass`, `Gateway`, `HTTPRoute` and others) for routing traffic into the cluster, split so the platform team owns the gateway and application teams own their routes. The successor to Ingress.
_Avoid_: API gateway (a product category), Ingress v2

**Headless Service**:
A Service with `clusterIP: None`, which gets no virtual IP. Its DNS name resolves to the addresses of the ready pods themselves.
_Avoid_: DNS-only service

**Helm chart**:
A package of templated manifests plus default values. Installing it with values renders the templates and creates a release that Helm tracks and can upgrade or roll back.
_Avoid_: Helm package, template

**HorizontalPodAutoscaler**:
An object whose controller changes the replica count of a workload to keep a metric, usually CPU utilization relative to requests, near a target.
_Avoid_: HPA in prose (accepted abbreviation after first use), autoscaler (ambiguous)

**Ingress**:
An object describing HTTP routing rules from outside the cluster to Services. It does nothing without an ingress controller running in the cluster to implement it.
_Avoid_: load balancer, ingress controller (the implementation)

**Job**:
A workload object that runs pods until a number of them complete successfully, retrying failed ones up to a backoff limit.
_Avoid_: task, batch pod

**kube-proxy**:
The node component that programs the node's packet rules (iptables, IPVS or nftables) so traffic to a Service's virtual IP reaches one of its ready endpoints.
_Avoid_: service proxy, load balancer

**kubelet**:
The agent on every node that receives the pods bound to that node, asks the container runtime to run them, runs their probes and reports their status back to the API server.
_Avoid_: node agent, minion

**Kustomize**:
A tool, built into `kubectl`, that builds manifests by applying patches and transformations from overlays to a base of plain YAML, with no templating.
_Avoid_: kustomization (the file it reads)

**Label**:
A key-value pair in an object's metadata used to select and group objects. Selectors in Services, Deployments and NetworkPolicies match on labels.
_Avoid_: tag, annotation (metadata that selectors cannot match)

**Liveness probe**:
A check the kubelet runs on a container, whose repeated failure makes the kubelet restart that container.
_Avoid_: health check (ambiguous), heartbeat

**Namespace**:
A scope for object names inside one cluster, and the unit that RBAC Roles, ResourceQuotas and Pod Security labels attach to. It is not a network or security boundary on its own.
_Avoid_: tenant, environment, Linux namespace (a kernel feature)

**NetworkPolicy**:
An object that restricts which traffic may reach or leave the pods it selects. It takes effect only when the cluster's network plugin enforces it.
_Avoid_: firewall rule, security group

**Node**:
A machine, physical or virtual, that runs a kubelet and a container runtime and on which pods run.
_Avoid_: worker, minion, host (ambiguous)

**PersistentVolume**:
A piece of storage in the cluster, provisioned by an administrator or dynamically by a StorageClass, with a lifecycle independent of any pod.
_Avoid_: PV in prose (accepted abbreviation after first use), disk

**PersistentVolumeClaim**:
A request for storage of a size and access mode, which binds to one PersistentVolume and which a pod mounts by name.
_Avoid_: PVC in prose (accepted abbreviation after first use), volume request

**Pod**:
The smallest unit the cluster schedules: one or more containers that share a network namespace and volumes and always run on the same node.
_Avoid_: container (a pod may hold several), instance

**Pod Security Standards**:
Three cumulative policy levels, `privileged`, `baseline` and `restricted`, that define what a pod's security settings may allow. The built-in Pod Security Admission controller enforces them per namespace.
_Avoid_: PodSecurityPolicy (the removed predecessor), PSP

**PodDisruptionBudget**:
An object limiting how many pods of a workload voluntary disruptions, such as a node drain, may take down at once.
_Avoid_: PDB in prose (accepted abbreviation after first use), availability budget

**QoS class**:
The class the kubelet assigns a pod from its requests and limits: `Guaranteed`, `Burstable` or `BestEffort`. It orders pods for eviction under node pressure.
_Avoid_: priority (a separate scheduling feature), tier

**RBAC**:
Role-based access control: Roles and ClusterRoles list allowed verbs on resources, and RoleBindings and ClusterRoleBindings grant them to users, groups and service accounts. It only adds permissions, it never denies.
_Avoid_: permissions, ACL

**Readiness probe**:
A check the kubelet runs on a container, whose failure marks the pod not ready so that Services stop sending it traffic. It never restarts anything.
_Avoid_: health check (ambiguous)

**Reconciliation**:
The repeated act of a controller comparing desired state with observed state and taking a step to close the gap, whatever caused it.
_Avoid_: sync, deployment (an object kind)

**ReplicaSet**:
A workload object that keeps a number of pods matching its selector running. Deployments create and manage them, and you rarely create one directly.
_Avoid_: ReplicationController (its predecessor), replicas

**Requests and limits**:
Per-container resource settings: a request is what the scheduler reserves on a node, and a limit is the ceiling the kernel enforces, by throttling CPU and by killing on memory.
_Avoid_: quota (a namespace-wide object), reservation

**Rollout**:
A Deployment, DaemonSet or StatefulSet moving its pods from one template revision to the next under its update strategy. A rollback is a rollout to an earlier revision.
_Avoid_: deploy, release

**Scheduler**:
The control plane component that assigns each unscheduled pod to a node, filtering nodes that cannot run it and scoring the rest.
_Avoid_: kube-scheduler in prose (its binary name), placer

**Secret**:
An object holding sensitive data, base64-encoded rather than encrypted, consumed like a ConfigMap. Its protection comes from RBAC, encryption at rest and how it reaches the cluster.
_Avoid_: encrypted config, vault

**Selector**:
A query on labels, equality-based or set-based, that names a group of objects. A Deployment's selector picks its pods, and a Service's selector picks its endpoints.
_Avoid_: filter, match

**Service**:
An object that gives a set of pods, chosen by a selector, one stable name and virtual IP, and spreads traffic across the ready ones. Types are `ClusterIP`, `NodePort`, `LoadBalancer` and `ExternalName`.
_Avoid_: microservice, application

**Service account**:
An identity for processes running in pods. A pod runs as one service account and gets a short-lived, audience-bound token for it, which RBAC grants permissions to.
_Avoid_: system user, robot account

**Startup probe**:
A check the kubelet runs on a container until it first succeeds, holding off liveness and readiness probes until then, so a slow start is not mistaken for a hang.
_Avoid_: init probe, warm-up check

**StatefulSet**:
A workload object that gives each replica a stable ordinal name, a stable network identity through a headless Service and its own PersistentVolumeClaim, and starts and updates replicas in order by default.
_Avoid_: PetSet (its old name), stateful deployment

**StorageClass**:
An object naming a kind of storage and the provisioner that creates PersistentVolumes of that kind on demand when a claim asks for it.
_Avoid_: storage tier, disk type

**Taint and toleration**:
A taint on a node repels pods, and a toleration on a pod lets it be scheduled onto, or keep running on, a node with a matching taint. A toleration permits a node, it never attracts a pod to one.
_Avoid_: node lock, node affinity (a separate mechanism)

**Termination grace period**:
The time, `terminationGracePeriodSeconds` and 30 seconds by default, that the kubelet gives a pod's containers between the start of termination and `SIGKILL`. Any `preStop` hook runs inside it.
_Avoid_: shutdown timeout, drain time
