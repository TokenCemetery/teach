---
title: "28. When Kubernetes Is the Wrong Answer"
description: Say when a service does not need Kubernetes or a usual default is wrong, and settle a disputed question from the API reference
type: lesson
---

# Lesson 28. When Kubernetes Is the Wrong Answer

**Mission link:** The mission ends with saying when Kubernetes, or one of its usual defaults, is the wrong answer, and settling a dispute from the API reference. Judgment here means a decision you can defend with a cost and a source, not a rule you remember.
**Primary source:** [Docs: "Overview", Kubernetes](https://kubernetes.io/docs/concepts/overview/)
**Prerequisites:** [Lesson 1](0001-what-kubernetes-is-for.md), [Lesson 13](0013-probes.md), [Lesson 15](0015-requests-limits-and-qos.md), [Lesson 18](0018-scheduling.md), [Lesson 26](0026-reviewing-manifests.md), [Requests and limits](../GLOSSARY.md), [QoS class](../GLOSSARY.md), [Liveness probe](../GLOSSARY.md), [Taint and toleration](../GLOSSARY.md)

## Warm-up

1. ▢ Name two things a Kubernetes cluster does for a service that a single host running a container with a restart policy does not.

<details markdown="1"><summary>Check</summary>

It reschedules the workload onto another node when a node dies, and it replaces and rolls out replicas under a controller, with a Service giving them one stable address. A restart policy only restarts a process on the same host (lessons 1 and 5).

</details>

2. ▢ What does a failing liveness probe do, and what does a failing readiness probe do?

<details markdown="1"><summary>Check</summary>

Liveness failure makes the kubelet restart the container. Readiness failure marks the pod not ready so Services stop sending it traffic, and nothing restarts (lesson 13).

</details>

3. ▢ What does a QoS class of `Guaranteed` require of a pod's requests and limits?

<details markdown="1"><summary>Check</summary>

Every container must have a CPU request and limit that are equal and a memory request and limit that are equal. Anything else is `Burstable`, or `BestEffort` when nothing is set ([pod QoS](https://kubernetes.io/docs/concepts/workloads/pods/pod-qos/), lesson 15).

</details>

## Know this

### A default is a bet about the common case

Every default and every "best practice" in this track was written for a typical workload. Judging one means naming the case it was built for, how yours differs, and what the alternative costs. A rule you cannot argue for is a habit, and a habit is wrong the first time the case changes.

The three questions below are judgment, not fact. The documentation gives the mechanisms and costs. The decision, and how to weigh it, rests on your workload, and each section ends with what would change the answer.

### When a service does not need Kubernetes

The [overview](https://kubernetes.io/docs/concepts/overview/) is blunt about what Kubernetes is not: it is not an all-inclusive platform as a service, it does not deploy source code or build your application, and it does not provide application-level services such as databases or message buses as built-in features. It gives you a scheduler, controllers and an API. Everything above that you assemble yourself.

The cost is mostly people. Releases arrive about every four months ([deprecation policy](https://kubernetes.io/docs/reference/deprecation-policy/)) and the version skew policy limits how far behind you can fall, so someone owns an upgrade treadmill (lesson 27), plus certificates, networking, storage classes, RBAC and the add-ons from lessons 24 and 19. A managed service takes the control plane off your hands, not the workload's manifests or the add-ons.

|Signals that point away from Kubernetes|Signals that point toward it|
|---|---|
|One or a few services, one team|Many services, several teams, one platform|
|Steady load, a short outage is acceptable|Needs rolling updates with automatic rollback and no downtime|
|One host, or a managed platform, is large enough|Needs many nodes, bin-packing and rescheduling when a node fails|
|Nobody owns the cluster and nobody wants to|A platform team that does|
|One container with a restart policy and a health check does the job (containers track, lesson 12)|Mixed workloads: services, batch, per-node agents, stateful sets|

The alternatives are real: one virtual machine with a process manager, Compose on one host, a managed container platform, a function service, or a static site. [RESOURCES.md](../RESOURCES.md) lists no neutral comparison of these, so this table is a judgment assembled from the overview's own list of what Kubernetes is not. What would change it: a second and third service, a second team, or a requirement for zero-downtime releases moves the answer toward Kubernetes quickly.

### When a usual default is wrong

**CPU limits on latency-sensitive services.** The usual advice is to set a limit on everything. A CPU limit is enforced by throttling: when the container approaches it, the kernel restricts its CPU, and it cannot exceed it ([resource management](https://kubernetes.io/docs/concepts/configuration/manage-resources-containers/)). A service that bursts for a few milliseconds per request can be throttled while the node has idle cores, which shows up as tail latency, not as an error. Dropping the CPU limit and keeping the CPU request leaves the pod `Burstable`, since `Guaranteed` needs the CPU limit to equal the request. The costs are real: a noisy neighbour can take CPU up to the node's free capacity, the pod loses `Guaranteed` ordering in eviction, and a quota or admission policy may require limits. Keep the **memory** limit equal to the request: memory cannot be taken back by throttling, so an unbounded pod is killed by the kernel or evicts others. What would change it: a shared multi-tenant cluster, where the hard cap protects other teams, or throttling that your own metrics show is not occurring.

**A liveness probe on every Deployment.** Templates add one by default. The probes documentation says that if the process in your container can crash on its own when it hits a problem, you do not necessarily need a liveness probe, because the kubelet already acts on the pod's restart policy ([probes](https://kubernetes.io/docs/concepts/workloads/pods/probes/)). A liveness probe earns its place for a hang the process cannot notice, a deadlock, and it costs an outage when it is wrong (lesson 13). Keep readiness, add a startup probe for slow starts, and add liveness only for a failure you have seen that a restart fixes. What would change it: a deadlock that a restart cures and that nothing else detects.

**One replica per node with required pod anti-affinity.** It reads as high availability. With `requiredDuringSchedulingIgnoredDuringExecution` and the hostname topology key, only one matching pod can run in each topology domain ([topology spread](https://kubernetes.io/docs/concepts/scheduling-eviction/topology-spread-constraints/)), so more replicas than nodes leave pods `Pending`. Rolling updates have a second problem. The Deployment defaults are `maxUnavailable: 25%`, rounded down, and `maxSurge: 25%`, rounded up ([Deployments](https://kubernetes.io/docs/concepts/workloads/controllers/deployment/)). With two or three replicas `maxUnavailable` is 0, so the Deployment starts a surge pod before it removes an old one, and on a cluster with as many nodes as replicas that surge pod has nowhere to go. The rollout stalls until you intervene. A topology spread constraint with `maxSkew: 1` and `whenUnsatisfiable: ScheduleAnyway`, or a `preferred` anti-affinity, spreads pods without the stall. What would change it: a hard requirement that two replicas never share a node, and spare nodes for the surge.

### Settling a dispute from the source

When two engineers disagree about what Kubernetes does, the answer is in a primary source, and the order of trust is fixed:

1. **The API reference** for what a field is and what it defaults to. `kubectl explain` prints it from your own cluster's API server, so it matches the version you run, for example `kubectl explain pod.spec.containers.resources.requests`.
2. **The concept page** for behaviour, with its "Feature state" label for maturity.
3. **The KEP** for why something was designed the way it was and how far it has graduated. Each KEP lives in the [enhancements repository](https://github.com/kubernetes/enhancements), and its `kep.yaml` records the `stage` and `latest-milestone`.
4. **The cluster itself.** A `--dry-run=server` apply or a ten-line experiment on kind turns an opinion into an observation.

Memory, a blog post and "everyone does it this way" are not on the list. Write the claim down as something that can be false, find the line that settles it, and put the link in the pull request.

Here is one. A colleague says: "If you set only limits and no requests, the pod is `BestEffort`." The [Pod API reference](https://kubernetes.io/docs/reference/kubernetes-api/workload-resources/pod-v1/) says that for `requests`, if omitted for a container, "it defaults to Limits if that is explicitly specified", and the [resource management page](https://kubernetes.io/docs/concepts/configuration/manage-resources-containers/) says the same, adding that an admission-time mechanism can set a different default. So the claim is false, and the QoS class follows from the copied requests. The cluster confirms it in practice 2.

## Practice

1. ▢ Which of these services is the strongest candidate for not using Kubernetes?

    - a) One internal report tool, one team, nightly downtime acceptable
    - b) Forty services owned by eight teams, weekly independent releases
    - c) A bursty public API needing fast scale across zones
    - d) Mixed-size batch jobs needing retries, quotas and shared nodes

<details markdown="1"><summary>Check</summary>

**a)** It has one team, one service and a tolerable outage, so nothing in it needs rescheduling, rollouts or bin-packing, and the operating cost of a cluster buys nothing. (b) is the case Kubernetes was built for. (c) needs scaling and zones. (d) needs retries and quotas across shared nodes. It is a judgment: a team that already runs a cluster might still add (a) to it, because the marginal cost is low.

</details>

2. ▢ Predict, then run. What QoS class does this pod get, and what does `resources` look like once the API server has accepted it?

    ```yaml
    apiVersion: v1
    kind: Pod
    metadata:
      name: limits-only
    spec:
      containers:
        - name: app
          image: busybox:1.36
          command: ["sleep", "3600"]
          resources:
            limits:
              cpu: 200m
              memory: 128Mi
    ```

    ```console
    $ kubectl apply -f limits-only.yaml
    $ kubectl get pod limits-only -o jsonpath='{.status.qosClass}'
    $ kubectl get pod limits-only -o jsonpath='{.spec.containers[0].resources}'
    ```

<details markdown="1"><summary>Hint</summary>

Read the `requests` field in the Pod API reference. What does the API fill in when it is omitted?

</details>

<details markdown="1"><summary>Check</summary>

```text
Guaranteed
{"limits":{"cpu":"200m","memory":"128Mi"},"requests":{"cpu":"200m","memory":"128Mi"}}
```

The omitted requests were copied from the limits, so every request equals its limit and the pod is `Guaranteed`. If the namespace has a LimitRange that sets default requests, those would apply instead, which is why the documentation hedges. Delete the pod when done.

</details>

3. ▢ A Deployment has `replicas: 3`, required pod anti-affinity on `kubernetes.io/hostname`, and runs on a cluster with exactly three worker nodes. You change the image tag. Predict the rollout and name the smallest fix.

<details markdown="1"><summary>Hint</summary>

With three replicas, how many pods may be unavailable at once, and how many extra may exist?

</details>

<details markdown="1"><summary>Check</summary>

The rollout stalls. `maxUnavailable` is 25% of 3 rounded down, which is 0, and `maxSurge` is 25% rounded up, which is 1. The Deployment creates one new pod before removing an old one, but all three nodes already run a matching pod, so the scheduler reports `node(s) didn't match pod anti-affinity rules` and the new pod stays `Pending`, while `kubectl rollout status` waits. The smallest fix is to make the rule soft: use `preferredDuringSchedulingIgnoredDuringExecution`, or replace it with a topology spread constraint using `ScheduleAnyway`. Adding a fourth node also works but treats the symptom.

</details>

4. ▢ A latency-sensitive service has a CPU limit equal to its request. Its p99 latency spikes while `kubectl top node` shows the node at 30% CPU, and the kubelet's cAdvisor metrics show the container's throttled periods climbing. What do you propose, and what do you tell the owner it costs?

<details markdown="1"><summary>Hint</summary>

Which setting causes throttling, and which one do you still need for the scheduler?

</details>

<details markdown="1"><summary>Check</summary>

Remove the CPU limit and keep the CPU request, sized from observed usage, so the scheduler still reserves capacity. The throttling stops because nothing caps the container below the node's free CPU. Costs to state: the pod is now `Burstable` instead of `Guaranteed`, it can use CPU other pods wanted if they burst at the same time, and a LimitRange or quota may refuse a pod without a CPU limit. Keep the memory limit equal to the request. If the cluster is shared with teams you do not control, ask whether the platform policy forbids it before proposing it.

</details>

5. ▢ A reviewer says every Deployment needs a liveness probe and a restart policy of `Always` or the kubelet will never restart a crashed container. Settle it from the source, naming where each part of the answer lives.

<details markdown="1"><summary>Check</summary>

False for the crash case. The probes page says that if the process can crash on its own, you do not necessarily need a liveness probe, since the kubelet acts according to the pod's `restartPolicy`, and the Pod API reference gives that field's default. A liveness probe is for a process that stays up but is stuck, and a bad one causes outages (lesson 13). The claim is half true: for a hang, you need a probe. Check the page and the field description rather than trusting the memory of either person.

</details>

6. ▢ A teammate says sidecar containers are still beta, so they should not be used. In what order do you check, and what would you bring back?

<details markdown="1"><summary>Check</summary>

First the concept page for sidecar containers, on the documentation version that matches your cluster, for its "Feature state" label. Then the KEP, whose `kep.yaml` records the `stage` and `latest-milestone`. Then the cluster: `kubectl explain pod.spec.initContainers.restartPolicy` shows whether your API server has the field, and a `--dry-run=server` apply of a sidecar pod shows whether it accepts it. Bring back the link and the version, not a recollection, because maturity changes between releases.

</details>

## Real-world reps

- [ ] On your kind cluster, run practice 2 and read the `qosClass` and the filled-in requests. Then add a LimitRange with a default request to the namespace, create the pod again under another name, and see whether the answer changes.
- [ ] Create a kind cluster with one control-plane and three workers, deploy three replicas with required hostname anti-affinity, change the image, and watch `kubectl rollout status` and `kubectl get pods`. Then switch the rule to a topology spread constraint with `ScheduleAnyway` and roll again.
- [ ] Tomorrow: without notes, write the three defaults from this lesson, the case each was built for, and what replacing each costs, then name the four sources in the order you trust them.

## Going further

- [Manifest Review Checklist](../reference/manifest-review-checklist.md)
- [Docs: "Overview", Kubernetes](https://kubernetes.io/docs/concepts/overview/)
- [Docs: "Kubernetes API" reference, Kubernetes](https://kubernetes.io/docs/reference/kubernetes-api/)
- [Docs: "kubectl explain", kubectl reference](https://kubernetes.io/docs/reference/kubectl/generated/kubectl_explain/)
- [Repository: Kubernetes Enhancement Proposals, Kubernetes](https://github.com/kubernetes/enhancements)
- [Docs: "API Conventions", Kubernetes community](https://github.com/kubernetes/community/blob/main/contributors/devel/sig-architecture/api-conventions.md)
- [Resources](../RESOURCES.md)

---

Not landing? Reread the primary source at the top, since this lesson compresses it and compression is where understanding leaks. Check the [glossary](../GLOSSARY.md) for any term that felt slippery.

If the lesson itself is unclear rather than the material, that is a defect: [open an issue](https://github.com/TokenCemetery/teach/issues).
