---
title: Resources
description: "Trusted sources for running workloads on Kubernetes"
type: resources
---

# Kubernetes Resources

## Knowledge

### The declarative model

- [Docs: "Overview", Kubernetes](https://kubernetes.io/docs/concepts/overview/)
  What Kubernetes provides and what it deliberately does not. Use for: lesson 1, and lesson 28 when deciding whether a service needs it.
- [Docs: "Kubernetes Components", Kubernetes](https://kubernetes.io/docs/concepts/overview/components/)
  The control plane and node components and what each one does. Use for: lesson 1.
- [Docs: "Nodes", Kubernetes](https://kubernetes.io/docs/concepts/architecture/nodes/)
  Node registration, status, heartbeats and what happens when a node stops reporting. Use for: lessons 1 and 2.
- [Docs: "Controllers", Kubernetes](https://kubernetes.io/docs/concepts/architecture/controller/)
  The control loop, desired against current state, and why many small controllers beat one large one. Use for: lesson 2.
- [Docs: "Garbage Collection", Kubernetes](https://kubernetes.io/docs/concepts/architecture/garbage-collection/)
  Owner references and cascading deletion. Use for: lessons 2 and 5, what deleting a Deployment does to its ReplicaSets and pods.
- [Design doc: "Design Principles", Kubernetes design proposals archive](https://github.com/kubernetes/design-proposals-archive/blob/main/architecture/principles.md)
  The original architectural principles: declarative APIs, level-triggered control loops, the API server as the only path to state. Use for: why the reconciliation loop is shaped the way it is.
- [Paper: "Borg, Omega, and Kubernetes", Burns, Grant, Oppenheimer, Brewer and Wilkes, 2016](https://research.google/pubs/borg-omega-and-kubernetes/)
  Lessons from a decade of container management at Google that shaped Kubernetes: pods, labels, reconciliation. Use for: the reasoning behind the design, after lesson 2.
- [Docs: "Objects In Kubernetes", Kubernetes](https://kubernetes.io/docs/concepts/overview/working-with-objects/)
  Spec and status, the required fields and how objects are described in YAML. Use for: lesson 3.
- [Docs: "Labels and Selectors", Kubernetes](https://kubernetes.io/docs/concepts/overview/working-with-objects/labels/)
  Label syntax, equality-based and set-based selectors. Use for: lesson 3 and every selector after it.
- [Docs: "Namespaces", Kubernetes](https://kubernetes.io/docs/concepts/overview/working-with-objects/namespaces/)
  What namespaces scope, which objects are cluster-wide, and the DNS name a namespace adds. Use for: lessons 3 and 9.
- [Docs: "Declarative Management of Kubernetes Objects Using Configuration Files", Kubernetes](https://kubernetes.io/docs/tasks/manage-kubernetes-objects/declarative-config/)
  How `kubectl apply` computes a patch from the last-applied configuration, the live object and the file. Use for: lesson 3, and why deleting a field from a file is not always a no-op.
- [Docs: "Server-Side Apply", Kubernetes](https://kubernetes.io/docs/reference/using-api/server-side-apply/)
  Field ownership, managers and conflicts when several actors apply to one object. Use for: lesson 3, and lesson 19 when an autoscaler and a manifest both set replicas.
- [Docs: "Kubernetes API Concepts", Kubernetes](https://kubernetes.io/docs/reference/using-api/api-concepts/)
  Resource versions, watches and list semantics. Use for: how controllers learn about changes without polling.
- [Docs: "API Conventions", Kubernetes community](https://github.com/kubernetes/community/blob/main/contributors/devel/sig-architecture/api-conventions.md)
  The conventions every built-in API follows: spec and status, conditions, generation and observedGeneration. Use for: reading any object's status correctly, and lesson 28.

### Workloads

- [Docs: "Pods", Kubernetes](https://kubernetes.io/docs/concepts/workloads/pods/)
  What a pod is, why containers are grouped, and why pods are created through workload controllers. Use for: lesson 4.
- [Docs: "Pod Lifecycle", Kubernetes](https://kubernetes.io/docs/concepts/workloads/pods/pod-lifecycle/)
  Phases, container states, restart policy, conditions and the termination sequence. Use for: lessons 4, 14 and 25.
- [Docs: "Init Containers", Kubernetes](https://kubernetes.io/docs/concepts/workloads/pods/init-containers/)
  Containers that run to completion before the app containers start. Use for: lesson 4.
- [Docs: "Sidecar Containers", Kubernetes](https://kubernetes.io/docs/concepts/workloads/pods/sidecar-containers/)
  Init containers with `restartPolicy: Always` that run alongside the main container and stop after it. Use for: lesson 4.
- [Docs: "Deployments", Kubernetes](https://kubernetes.io/docs/concepts/workloads/controllers/deployment/)
  Creating, updating, rolling back, pausing and scaling a Deployment, and the rolling update parameters. Use for: lessons 5 and 6.
- [Docs: "ReplicaSet", Kubernetes](https://kubernetes.io/docs/concepts/workloads/controllers/replicaset/)
  How a ReplicaSet acquires pods by selector and why a Deployment should manage it. Use for: lesson 5.
- [Docs: "kubectl rollout", kubectl reference](https://kubernetes.io/docs/reference/kubectl/generated/kubectl_rollout/)
  The `status`, `history`, `pause`, `resume`, `undo` and `restart` subcommands. Use for: lesson 6.
- [Docs: "Jobs", Kubernetes](https://kubernetes.io/docs/concepts/workloads/controllers/job/)
  Completions, parallelism, backoff limits, pod failure policy and indexed Jobs. Use for: lesson 7.
- [Docs: "CronJob", Kubernetes](https://kubernetes.io/docs/concepts/workloads/controllers/cron-jobs/)
  Schedule syntax, time zones, concurrency policy and missed schedules. Use for: lesson 7.
- [Docs: "Automatic Cleanup for Finished Jobs", Kubernetes](https://kubernetes.io/docs/concepts/workloads/controllers/ttlafterfinished/)
  `ttlSecondsAfterFinished` and why finished Jobs pile up without it. Use for: lesson 7.
- [Docs: "DaemonSet", Kubernetes](https://kubernetes.io/docs/concepts/workloads/controllers/daemonset/)
  One pod per node, how DaemonSet pods are scheduled, and their update strategy. Use for: lesson 7.

### Networking

- [Docs: "Cluster Networking", Kubernetes](https://kubernetes.io/docs/concepts/cluster-administration/networking/)
  The network model: every pod gets its own IP and can reach every other pod without NAT, implemented by a network plugin. Use for: lesson 8.
- [Docs: "Service", Kubernetes](https://kubernetes.io/docs/concepts/services-networking/service/)
  Service types, selectors, ports, headless Services and `ExternalName`. Use for: lesson 8.
- [Docs: "LoadBalancer", kind](https://kind.sigs.k8s.io/docs/user/loadbalancer/)
  Getting `type: LoadBalancer` addresses on a kind cluster with Cloud Provider KIND. Use for: lesson 8.
- [Docs: "EndpointSlices", Kubernetes](https://kubernetes.io/docs/concepts/services-networking/endpoint-slices/)
  How a Service's backends are tracked, with ready, serving and terminating conditions. Use for: lessons 8 and 14.
- [Docs: "Virtual IPs and Service Proxies", Kubernetes](https://kubernetes.io/docs/reference/networking/virtual-ips/)
  How kube-proxy implements Services in iptables, IPVS and nftables modes, and session affinity. Use for: lesson 8, what actually happens to a packet sent to a ClusterIP.
- [Docs: "Debug Services", Kubernetes](https://kubernetes.io/docs/tasks/debug/debug-application/debug-service/)
  A step-by-step walk from "the Service does not work" through DNS, endpoints and kube-proxy. Use for: lessons 8, 9 and 25.
- [Docs: "DNS for Services and Pods", Kubernetes](https://kubernetes.io/docs/concepts/services-networking/dns-pod-service/)
  Service and pod DNS names, the search path, `ndots`, and pod DNS policy. Use for: lesson 9.
- [Man page: resolv.conf(5), Linux man-pages project](https://man7.org/linux/man-pages/man5/resolv.conf.5.html)
  The resolver's `search` list and `ndots` option, which every pod's DNS configuration uses. Use for: lesson 9.
- [Docs: "Ingress", Kubernetes](https://kubernetes.io/docs/concepts/services-networking/ingress/)
  Ingress rules, path types, TLS and the ingress class. Use for: lesson 10.
- [Docs: "Ingress Controllers", Kubernetes](https://kubernetes.io/docs/concepts/services-networking/ingress-controllers/)
  Why an Ingress needs a controller and how ingress classes choose one. Use for: lesson 10.
- [Blog: "Ingress NGINX Retirement: What You Need to Know", Kubernetes](https://kubernetes.io/blog/2025/11/11/ingress-nginx-retirement/)
  The announced end of maintenance for the community ingress-nginx controller and what to migrate to. Use for: lesson 10.
- [Docs: "Ingress", kind](https://kind.sigs.k8s.io/docs/user/ingress/)
  Running Ingress and Gateway API on a kind cluster. Use for: the lesson 10 reps.
- [Docs: "Gateway API", Kubernetes](https://kubernetes.io/docs/concepts/services-networking/gateway/)
  GatewayClass, Gateway and HTTPRoute, and the role split between them. Use for: lesson 10.
- [Docs: Gateway API project site, Kubernetes SIG Network](https://gateway-api.sigs.k8s.io/)
  The full API, its conformance levels and the implementations. Use for: lesson 10, beyond what the concept page covers.

### Configuration

- [Docs: "ConfigMaps", Kubernetes](https://kubernetes.io/docs/concepts/configuration/configmap/)
  Consuming a ConfigMap as environment variables or a volume, immutable ConfigMaps, and how mounted values update. Use for: lesson 11.
- [Docs: "Secrets", Kubernetes](https://kubernetes.io/docs/concepts/configuration/secret/)
  Secret types, consuming them, and the warning that they are stored unencrypted by default. Use for: lesson 12.
- [Docs: "Good practices for Kubernetes Secrets", Kubernetes](https://kubernetes.io/docs/concepts/security/secrets-good-practices/)
  Encryption at rest, least-privilege access, and external secret stores. Use for: lesson 12.
- [Docs: "Encrypting Confidential Data at Rest", Kubernetes](https://kubernetes.io/docs/tasks/administer-cluster/encrypt-data/)
  The encryption configuration and its providers, including KMS. Use for: lesson 12, what encryption at rest does and does not cover.
- [Project: Sealed Secrets, Bitnami](https://github.com/bitnami/sealed-secrets)
  A controller that decrypts `SealedSecret` objects, encrypted with the cluster's key, into Secrets, so the encrypted form can live in Git. Use for: lesson 12.

### Running reliably

- [Docs: "Liveness, Readiness, and Startup Probes", Kubernetes](https://kubernetes.io/docs/concepts/workloads/pods/probes/)
  What each probe is for and what the kubelet does when it fails. Use for: lesson 13.
- [Docs: "Configure Liveness, Readiness and Startup Probes", Kubernetes](https://kubernetes.io/docs/tasks/configure-pod-container/configure-liveness-readiness-startup-probes/)
  Probe types and every timing field with its default. Use for: lesson 13, and settling what a probe field defaults to.
- [Docs: "Container Lifecycle Hooks", Kubernetes](https://kubernetes.io/docs/concepts/containers/container-lifecycle-hooks/)
  `postStart` and `preStop`, and how a hook counts against the grace period. Use for: lesson 14.
- [Tutorial: "Explore Termination Behavior for Pods And Their Endpoints", Kubernetes](https://kubernetes.io/docs/tutorials/services/pods-and-endpoint-termination-flow/)
  A terminating pod's EndpointSlice conditions, step by step. Use for: lesson 14.
- [Docs: "Resource Management for Pods and Containers", Kubernetes](https://kubernetes.io/docs/concepts/configuration/manage-resources-containers/)
  Requests and limits, units, how the scheduler uses requests and how the kernel enforces limits. Use for: lesson 15.
- [Docs: "Pod Quality of Service Classes", Kubernetes](https://kubernetes.io/docs/concepts/workloads/pods/pod-qos/)
  How a pod's requests and limits set its QoS class. Use for: lesson 15.
- [Docs: "Node-pressure Eviction", Kubernetes](https://kubernetes.io/docs/concepts/scheduling-eviction/node-pressure-eviction/)
  Eviction signals, thresholds and the order the kubelet evicts pods in. Use for: lessons 15 and 19.
- [Docs: "Resize CPU and Memory Resources assigned to Containers", Kubernetes](https://kubernetes.io/docs/tasks/configure-pod-container/resize-container-resources/)
  Changing a running pod's requests and limits in place, and the resize policy. Use for: lesson 15, a version-sensitive feature to check before relying on it.
- [Docs: "Limit Ranges", Kubernetes](https://kubernetes.io/docs/concepts/policy/limit-range/)
  Default and maximum requests and limits per namespace. Use for: lesson 15.
- [Docs: "Resource Quotas", Kubernetes](https://kubernetes.io/docs/concepts/policy/resource-quotas/)
  Total resource and object counts per namespace. Use for: lesson 15, and why a pod without requests is rejected in a quota'd namespace.

### State, scheduling and scale

- [Docs: "Volumes", Kubernetes](https://kubernetes.io/docs/concepts/storage/volumes/)
  Volume types, `emptyDir`, projected volumes and how a pod mounts them. Use for: lessons 11 and 16.
- [Docs: "Persistent Volumes", Kubernetes](https://kubernetes.io/docs/concepts/storage/persistent-volumes/)
  The PersistentVolume and claim lifecycle, binding, access modes and reclaim policies. Use for: lesson 16.
- [Docs: "Storage Classes", Kubernetes](https://kubernetes.io/docs/concepts/storage/storage-classes/)
  Provisioners, parameters, `volumeBindingMode` and `allowVolumeExpansion`. Use for: lesson 16.
- [Docs: "Dynamic Volume Provisioning", Kubernetes](https://kubernetes.io/docs/concepts/storage/dynamic-provisioning/)
  How a claim triggers a provisioner and what the default StorageClass does. Use for: lesson 16.
- [Docs: "StatefulSets", Kubernetes](https://kubernetes.io/docs/concepts/workloads/controllers/statefulset/)
  Stable identity, ordered deployment and scaling, volume claim templates and their limitations. Use for: lesson 17.
- [Docs: "Run a Replicated Stateful Application", Kubernetes](https://kubernetes.io/docs/tasks/run-application/run-replicated-stateful-application/)
  A worked MySQL StatefulSet with primary and replicas. Use for: lesson 17, how much the application has to do itself.
- [Docs: "Kubernetes Scheduler", Kubernetes](https://kubernetes.io/docs/concepts/scheduling-eviction/kube-scheduler/)
  Filtering and scoring, and what makes a node feasible. Use for: lesson 18.
- [Docs: "Assigning Pods to Nodes", Kubernetes](https://kubernetes.io/docs/concepts/scheduling-eviction/assign-pod-node/)
  Node selectors, node affinity and pod affinity and anti-affinity. Use for: lesson 18.
- [Docs: "Taints and Tolerations", Kubernetes](https://kubernetes.io/docs/concepts/scheduling-eviction/taint-and-toleration/)
  Taint effects, toleration matching and the taints the node controller adds. Use for: lesson 18.
- [Docs: "Pod Topology Spread Constraints", Kubernetes](https://kubernetes.io/docs/concepts/scheduling-eviction/topology-spread-constraints/)
  Spreading replicas across zones and nodes with `maxSkew`. Use for: lesson 18.
- [Docs: "Pod Priority and Preemption", Kubernetes](https://kubernetes.io/docs/concepts/scheduling-eviction/pod-priority-preemption/)
  PriorityClasses and how the scheduler evicts lower-priority pods to place higher ones. Use for: lesson 18.
- [Docs: "Autoscaling Workloads", Kubernetes](https://kubernetes.io/docs/concepts/workloads/autoscaling/)
  The horizontal and vertical options and event-driven scaling, side by side. Use for: lesson 19.
- [Docs: "Horizontal Pod Autoscaling", Kubernetes](https://kubernetes.io/docs/concepts/workloads/autoscaling/horizontal-pod-autoscale/)
  The scaling algorithm, metrics, stabilization windows and scaling behaviour. Use for: lesson 19.
- [Docs: "Vertical Pod Autoscaling", Kubernetes](https://kubernetes.io/docs/concepts/workloads/autoscaling/vertical-pod-autoscale/)
  Recommending and setting requests from observed usage, and why not to combine it with the HPA on the same metric. Use for: lesson 19.
- [Docs: "Node Autoscaling", Kubernetes](https://kubernetes.io/docs/concepts/cluster-administration/node-autoscaling/)
  Adding and removing nodes from pending pods and utilization, with Cluster Autoscaler and Karpenter. Use for: lesson 19.
- [Docs: "Disruptions", Kubernetes](https://kubernetes.io/docs/concepts/workloads/pods/disruptions/)
  Voluntary against involuntary disruptions and how a PodDisruptionBudget limits the first kind. Use for: lesson 19.
- [Docs: "Specifying a Disruption Budget for your Application", Kubernetes](https://kubernetes.io/docs/tasks/run-application/configure-pdb/)
  Writing a PodDisruptionBudget with `minAvailable` or `maxUnavailable`, and its unhealthy pod eviction policy. Use for: lesson 19.
- [Docs: "API-initiated Eviction", Kubernetes](https://kubernetes.io/docs/concepts/scheduling-eviction/api-eviction/)
  How the Eviction API answers, and how PodDisruptionBudgets make it refuse with a 429. Use for: lesson 19.

### Security

- [Docs: "Authorization", Kubernetes](https://kubernetes.io/docs/reference/access-authn-authz/authorization/)
  How a request is authorized, the modes, and checking access. Use for: lesson 20.
- [Docs: "Using RBAC Authorization", Kubernetes](https://kubernetes.io/docs/reference/access-authn-authz/rbac/)
  Roles, ClusterRoles, bindings, aggregation and the default roles. Use for: lesson 20.
- [Docs: "Role Based Access Control Good Practices", Kubernetes](https://kubernetes.io/docs/concepts/security/rbac-good-practices/)
  Least privilege, and the permissions that allow privilege escalation: secrets, workload creation, `escalate`, `bind`, `impersonate`. Use for: lessons 20 and 26.
- [Docs: "kubectl auth can-i", kubectl reference](https://kubernetes.io/docs/reference/kubectl/generated/kubectl_auth/kubectl_auth_can-i/)
  Checking what a user or service account may do, with `--as` and `--list`. Use for: lesson 20.
- [Docs: "Service Accounts", Kubernetes](https://kubernetes.io/docs/concepts/security/service-accounts/)
  What service accounts are for, token projection and disabling automounting. Use for: lesson 20.
- [Docs: "Configure Service Accounts for Pods", Kubernetes](https://kubernetes.io/docs/tasks/configure-pod-container/configure-service-account/)
  Opting out of token automounting, `kubectl create token` and projected token volumes. Use for: lesson 20.
- [Docs: "Network Policies", Kubernetes](https://kubernetes.io/docs/concepts/services-networking/network-policies/)
  Ingress and egress rules, selectors, default-deny policies and what a policy cannot express. Use for: lesson 21.
- [Docs: "Configure a Security Context for a Pod or Container", Kubernetes](https://kubernetes.io/docs/tasks/configure-pod-container/security-context/)
  `runAsUser`, `runAsNonRoot`, capabilities, seccomp, `readOnlyRootFilesystem` and `allowPrivilegeEscalation`. Use for: lesson 21.
- [Docs: "Pod Security Standards", Kubernetes](https://kubernetes.io/docs/concepts/security/pod-security-standards/)
  The `privileged`, `baseline` and `restricted` levels, field by field. Use for: lesson 21.
- [Docs: "Pod Security Admission", Kubernetes](https://kubernetes.io/docs/concepts/security/pod-security-admission/)
  The namespace labels that enforce, audit or warn on a level. Use for: lesson 21.
- [Docs: "Enforce Pod Security Standards with Namespace Labels", Kubernetes](https://kubernetes.io/docs/tasks/configure-pod-container/enforce-standards-namespace-labels/)
  The namespace labels, version pinning and a server-side dry run before enforcing. Use for: lesson 21.
- [Release notes: kind v0.24.0, kind](https://github.com/kubernetes-sigs/kind/releases/tag/v0.24.0)
  The release that made kind's default network plugin enforce NetworkPolicy. Use for: the lesson 21 reps.
- [Docs: "Security Checklist", Kubernetes](https://kubernetes.io/docs/concepts/security/security-checklist/)
  A baseline checklist across authentication, network, pods and secrets. Use for: lesson 26, reviewing someone else's manifests.

### Packaging

- [Docs: "Declarative Management of Kubernetes Objects Using Kustomize", Kubernetes](https://kubernetes.io/docs/tasks/manage-kubernetes-objects/kustomization/)
  Bases, overlays, generators and patches with `kubectl apply -k`. Use for: lesson 22.
- [Docs: Kustomize reference, kubectl documentation](https://kubectl.docs.kubernetes.io/references/kustomize/)
  Every field a `kustomization.yaml` accepts. Use for: lesson 22, settling what a field does.
- [Docs: "Using Helm", Helm](https://helm.sh/docs/intro/using_helm/)
  Charts, repositories, releases, values, upgrades and rollbacks from the user's side. Use for: lesson 23.
- [Docs: "Charts", Helm](https://helm.sh/docs/topics/charts/)
  Chart layout, `Chart.yaml`, dependencies and versioning. Use for: lessons 23 and 27.
- [Docs: "Chart Template Guide", Helm](https://helm.sh/docs/chart_template_guide/)
  Writing templates, values, functions and named templates. Use for: lesson 23.
- [Docs: "Chart Best Practices", Helm](https://helm.sh/docs/chart_best_practices/)
  Conventions for values, labels, templates and CRDs in a chart. Use for: lessons 23 and 26.
- [Docs: "Chart Hooks", Helm](https://helm.sh/docs/topics/charts_hooks/)
  Running Jobs before or after install and upgrade, and their deletion policies. Use for: lesson 23.
- [Docs: "helm upgrade", Helm](https://helm.sh/docs/helm/helm_upgrade/)
  The value reuse and reset flags and `--history-max`. Use for: lesson 23.
- [Docs: "Advanced Helm Techniques", Helm](https://helm.sh/docs/topics/advanced/)
  Release storage backends, Secrets by default, and post-rendering. Use for: lesson 23.
- [Docs: "Custom Resource Definitions", Helm chart best practices](https://helm.sh/docs/chart_best_practices/custom_resource_definitions/)
  The `crds/` directory and why Helm never upgrades or deletes CRDs. Use for: lesson 23.

### Observability and debugging

- [Docs: "Resource metrics pipeline", Kubernetes](https://kubernetes.io/docs/tasks/debug/debug-cluster/resource-metrics-pipeline/)
  The Metrics API, metrics-server and what `kubectl top` reads. Use for: lessons 19 and 24.
- [Project: metrics-server, Kubernetes SIG Instrumentation](https://github.com/kubernetes-sigs/metrics-server)
  The component behind the Metrics API, its installation and its kubelet TLS flags. Use for: lessons 19 and 24, installing it on a kind cluster.
- [Docs: "Metrics For Kubernetes System Components", Kubernetes](https://kubernetes.io/docs/concepts/cluster-administration/system-metrics/)
  The Prometheus-format metrics the components expose. Use for: lesson 24.
- [Project: kube-state-metrics, Kubernetes](https://github.com/kubernetes/kube-state-metrics)
  A service that turns object state (replicas, conditions, restarts) into metrics. Use for: lesson 24, alerting on what the API server knows.
- [Docs: "Overview", Prometheus](https://prometheus.io/docs/introduction/overview/)
  The pull model, the data model and where Prometheus fits. Use for: lesson 24.
- [Docs: "Logging Architecture", Kubernetes](https://kubernetes.io/docs/concepts/cluster-administration/logging/)
  Where container logs live on a node, rotation, and node-level and sidecar log shipping. Use for: lesson 24.
- [Book chapter: "Monitoring Distributed Systems", Google SRE book](https://sre.google/sre-book/monitoring-distributed-systems/)
  Symptoms against causes and the four golden signals. Use for: lesson 24, deciding what to alert on.
- [Docs: "Debug Pods", Kubernetes](https://kubernetes.io/docs/tasks/debug/debug-application/debug-pods/)
  Pending, waiting and crashing pods, and the commands for each. Use for: lesson 25.
- [Docs: "Debug Running Pods", Kubernetes](https://kubernetes.io/docs/tasks/debug/debug-application/debug-running-pod/)
  `kubectl describe`, `logs --previous`, `exec`, ephemeral debug containers and debugging on the node. Use for: lesson 25.
- [Docs: "Determine the Reason for Pod Failure", Kubernetes](https://kubernetes.io/docs/tasks/debug/debug-application/determine-reason-pod-failure/)
  Termination messages and where a container's last state is recorded. Use for: lesson 25.
- [Docs: "Ephemeral Containers", Kubernetes](https://kubernetes.io/docs/concepts/workloads/pods/ephemeral-containers/)
  What an ephemeral container is and why it exists for debugging distroless images. Use for: lesson 25.
- [Docs: "kubectl debug", kubectl reference](https://kubernetes.io/docs/reference/kubectl/generated/kubectl_debug/)
  Every flag: `--target`, `--copy-to`, `--profile`, and debugging a node. Use for: lesson 25.

### Judgment, upgrades and the API reference

- [Docs: "Kubernetes API" reference, Kubernetes](https://kubernetes.io/docs/reference/kubernetes-api/)
  Every built-in resource, field by field, with types and defaults. Use for: lesson 28, settling a disputed field from the source.
- [Docs: "Deprecated API Migration Guide", Kubernetes](https://kubernetes.io/docs/reference/using-api/deprecation-guide/)
  Which API versions were removed in which release, and what replaces each. Use for: lesson 27.
- [Docs: "Kubernetes Deprecation Policy", Kubernetes](https://kubernetes.io/docs/reference/deprecation-policy/)
  How long alpha, beta and GA APIs must be served after deprecation. Use for: lesson 27.
- [Docs: "Version Skew Policy", Kubernetes](https://kubernetes.io/releases/version-skew-policy/)
  Which versions of the API server, kubelet and kubectl may run together. Use for: lesson 27, the order a cluster upgrade has to follow.
- [Docs: "Upgrade A Cluster", Kubernetes](https://kubernetes.io/docs/tasks/administer-cluster/cluster-upgrade/)
  The upgrade sequence and the checks before and after. Use for: lesson 27.
- [Docs: "Upgrading kubeadm clusters", Kubernetes](https://kubernetes.io/docs/tasks/administer-cluster/kubeadm/kubeadm-upgrade/)
  The step-by-step upgrade of a kubeadm cluster, one minor version at a time. Use for: lesson 27.
- [Docs: "Deprecated Kubernetes APIs", Helm](https://helm.sh/docs/topics/kubernetes_apis/)
  Finding and fixing removed API versions in charts and in deployed releases. Use for: lesson 27.
- [Docs: "Custom Resources", Kubernetes](https://kubernetes.io/docs/concepts/extend-kubernetes/api-extension/custom-resources/)
  CustomResourceDefinitions and when a custom resource is the right tool. Use for: lessons 27 and 28.
- [Docs: "Operator pattern", Kubernetes](https://kubernetes.io/docs/concepts/extend-kubernetes/operator/)
  Controllers for custom resources that encode operational knowledge. Use for: lesson 17, what an operator adds to a StatefulSet.
- [Repository: Kubernetes Enhancement Proposals, Kubernetes](https://github.com/kubernetes/enhancements)
  The KEPs that record why each feature was designed the way it was and its graduation stage. Use for: lesson 28, settling a question about intent or maturity.
- [Docs: "kubectl Quick Reference", Kubernetes](https://kubernetes.io/docs/reference/kubectl/quick-reference/)
  The common commands on one page. Use for: the kubectl reference sheet, and anything it does not list.
- [Docs: "Quick Start", kind](https://kind.sigs.k8s.io/docs/user/quick-start/)
  Creating, configuring and deleting local clusters, including multi-node clusters. Use for: every real-world rep in this track.

## Gaps

- No single vendor-neutral source compares running a service on Kubernetes against a managed container platform or a plain virtual machine on cost and operational load. Lesson 28 assembles the comparison from the overview's own list of what Kubernetes is not, and says where it is a judgment rather than a fact.
- Managed Kubernetes offerings differ in defaults (network plugin, NetworkPolicy enforcement, storage classes, node autoscaling) and change often. The lessons teach upstream behaviour, and each provider's documentation is the source for its differences.
- Ingress controllers each extend the Ingress object with their own annotations, which no upstream source documents. Lesson 10 teaches the portable fields and the Gateway API, which moved those extensions into typed fields.
