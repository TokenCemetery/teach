---
title: "15. Requests, Limits and QoS"
description: Requests drive scheduling and limits drive enforcement, and together they set the QoS class that decides who is evicted first
type: lesson
---

# Lesson 15. Requests, Limits and QoS

**Mission link:** The mission says to keep a workload healthy with requests and limits that set its QoS class. Two numbers per container decide where a pod can be placed, whether it is slowed down, whether it is killed, and where it stands when a node runs short. Leaving them out is a choice with consequences, not a neutral default.
**Primary source:** [Docs: "Resource Management for Pods and Containers", Kubernetes](https://kubernetes.io/docs/concepts/configuration/manage-resources-containers/)
**Prerequisites:** [Lesson 4](0004-pods.md), [Lesson 13](0013-probes.md), [Lesson 14](0014-pod-termination.md), [Requests and limits](../GLOSSARY.md), [QoS class](../GLOSSARY.md), [Eviction](../GLOSSARY.md), [Scheduler](../GLOSSARY.md), [kubelet](../GLOSSARY.md)

## Warm-up

1. ▢ Which component picks the node for a new pod, and what happens to the pod if no node fits?

<details markdown="1"><summary>Check</summary>

The scheduler picks it by filtering out nodes that cannot run the pod and scoring the rest. If none fit, the pod stays `Pending` with a `FailedScheduling` event until something changes (lessons 2 and 4).

</details>

2. ▢ A liveness probe fails past its threshold. What does the kubelet restart, and what number does `RESTARTS` show afterwards?

<details markdown="1"><summary>Check</summary>

It restarts the container, not the pod, and the container's restart count increases by one (lesson 13). Keep this in mind for the OOM case below, which also shows up as a restart.

</details>

3. ▢ In a Docker container, what did `--memory` and `--cpus` do when the process went over them?

<details markdown="1"><summary>Check</summary>

Memory is a hard limit: going over it gets the process OOM-killed, exit code 137. A CPU quota throttles the process and never kills it ([Running Containers](../../containers/reference/running-containers.md), resource limits). Kubernetes limits are the same cgroup mechanism, set per container.

</details>

## Know this

### Two numbers, two jobs

Each container may set a request and a limit for CPU and memory ([Docs](https://kubernetes.io/docs/concepts/configuration/manage-resources-containers/)):

```yaml
resources:
  requests:
    cpu: 250m
    memory: 128Mi
  limits:
    cpu: 500m
    memory: 256Mi
```

CPU is counted in cores, where `1` is one core and `250m` is a quarter of a core. Memory is in bytes with suffixes, and `Mi` is mebibytes, so `128Mi` is not `128M`.

|Setting|Used by|What it does|
|---|---|---|
|Request|The scheduler|Reserves the amount on a node, and a node fits a pod only if the sum of requests stays below its capacity|
|Limit|The kubelet and the kernel|Sets the ceiling the container may use|

The scheduler looks at requests, never at current usage. A node with almost no real load still refuses a pod when the requests already placed on it add up to its capacity, because that protects against a later spike. A pod whose request fits no node stays `Pending` with `FailedScheduling` and a message such as `0/3 nodes are available: 3 Insufficient cpu`. `kubectl describe node` shows `Allocated resources`, the sums of requests and limits, which is what the scheduler compares.

If a container sets a limit and no request, and nothing in the namespace supplies a default, Kubernetes uses the limit as the request.

### What happens at the limit

The two resources fail differently:

|Resource|At the limit|Visible as|
|---|---|---|
|CPU|The kernel throttles the container, so it cannot use more than the limit|Slower responses, no restart, no error|
|Memory|The kernel may OOM-kill the container when it uses more than the limit|`OOMKilled`, exit code 137, a container restart|

The docs call CPU a hard ceiling enforced by throttling, and memory enforcement reactive: a container can briefly use more than its limit, and is killed when the kernel detects memory pressure. The kill appears in the pod status:

```console
$ kubectl describe pod leaky-5c8f7d9b6-q4tzr
...
    Last State:     Terminated
      Reason:       OOMKilled
      Exit Code:    137
    Restart Count:  5
```

Exit code 137 alone is ambiguous, as in the containers track, since `SIGKILL` also follows a missed grace period. `OOMKilled` as the reason is what separates a memory kill. Whether CPU limits are worth setting at all is argued by practitioners, and lesson 28 covers that debate, so here the rule is only to know that throttling is the consequence.

### QoS classes

The kubelet assigns each pod a QoS class from its requests and limits ([Pod Quality of Service Classes](https://kubernetes.io/docs/concepts/workloads/pods/pod-qos/)):

|Class|Rule|
|---|---|
|`Guaranteed`|Every container has a CPU and a memory limit and request, and for each the request equals the limit|
|`Burstable`|Not Guaranteed, and at least one container has some CPU or memory request or limit|
|`BestEffort`|No container has any CPU or memory request or limit|

The class is read-only, you cannot set it, and you read it with `kubectl get pod NAME -o jsonpath='{.status.qosClass}'`.

### Who is evicted first

When a node runs short of memory, disk or process IDs, the kubelet starts evicting pods to protect the node. Default hard thresholds on Linux include `memory.available<100Mi`, `nodefs.available<10%` and `imagefs.available<15%`. This is node-pressure eviction, and it differs from API-initiated eviction in a way that matters in lesson 19: the kubelet ignores PodDisruptionBudgets and the pod's grace period, and with a hard threshold it terminates immediately ([Node-pressure Eviction](https://kubernetes.io/docs/concepts/scheduling-eviction/node-pressure-eviction/)).

The QoS class gives a good first guess at the order, but the kubelet does not use the class itself. It ranks pods by three things:

1. Whether the pod's usage exceeds its requests. Pods that exceed them go first.
2. The pod's priority, which is a scheduling setting separate from QoS.
3. How far usage is above requests.

In practice, a `BestEffort` pod has no request, so any usage exceeds it and it goes first. A `Burstable` pod using more than it requested goes next. A `Guaranteed` pod, or a `Burstable` pod within its requests, goes last, and the docs add that a `Guaranteed` pod is never evicted because of another pod's consumption. Setting requests close to real usage is therefore also what protects a pod.

### Defaults and ceilings for a namespace

Two namespace-level objects keep individual pods from ignoring all this:

- A **LimitRange** sets default requests and limits that are injected into containers that set none, and minimum and maximum values per container or pod. A pod that violates it is rejected with `403 Forbidden` at admission ([Limit Ranges](https://kubernetes.io/docs/concepts/policy/limit-range/)).
- A **ResourceQuota** caps the totals for a namespace, such as `requests.cpu`, or object counts such as `pods`. If a quota covers CPU or memory, a pod that sets no requests or limits for them may be rejected ([Resource Quotas](https://kubernetes.io/docs/concepts/policy/resource-quotas/)).

Both are checked when the object is created and do not change pods that already run.

## Practice

1. ▢ A node has 4 CPUs and is using 5% of them. Pods on it already request 3.8 CPUs in total. Your pod requests 500m. What does the scheduler do?

    - a) Places it because usage is low
    - b) Places it and throttles other pods
    - c) Leaves it Pending on this node
    - d) Places it and evicts another pod

<details markdown="1"><summary>Check</summary>

**c)** The scheduler adds up requests, not usage, and 3.8 plus 0.5 exceeds 4. (a) uses actual load, which the scheduler ignores. (b) and (d) assume the scheduler squeezes or evicts running pods to fit a normal pod, which it does not do for requests alone.

</details>

2. ▢ A container with a 256Mi memory limit and a 500m CPU limit runs a batch step that needs 400Mi and a lot of CPU. Describe what each limit does to it.

<details markdown="1"><summary>Check</summary>

The CPU limit throttles it: the step runs slower, but it completes. The memory limit does not slow it, because memory cannot be throttled: when usage passes 256Mi the kernel may OOM-kill the container, which shows as `OOMKilled` with exit code 137 and a restart. The fix for memory is a higher limit (and request) based on a measured peak.

</details>

3. ▢ Predict, then run. What QoS class does each of these four pods get? The pods share one command and image, only `resources` differs.

    ```yaml
    # pod a
    resources:
      requests: {cpu: 100m, memory: 64Mi}
      limits:   {cpu: 100m, memory: 64Mi}
    # pod b
    resources:
      requests: {cpu: 100m, memory: 64Mi}
    # pod c
    resources: {}
    # pod d
    resources:
      limits: {cpu: 100m, memory: 64Mi}
    ```

    ```console
    $ kubectl get pods -o custom-columns=NAME:.metadata.name,QOS:.status.qosClass
    ```

<details markdown="1"><summary>Hint</summary>

For pod d, recall what Kubernetes does when a limit is set without a request.

</details>

<details markdown="1"><summary>Check</summary>

```text
NAME    QOS
pod-a   Guaranteed
pod-b   Burstable
pod-c   BestEffort
pod-d   Guaranteed
```

Pod a has equal requests and limits for both resources. Pod b has requests but no limits, so it is not Guaranteed and has some settings, which makes it Burstable. Pod c has nothing at all. Pod d sets only limits, but the limit is copied into the request for each resource, so requests equal limits and the pod is Guaranteed. Run `kubectl get pod pod-d -o yaml` and you can see the copied `requests`.

</details>

4. ▢ Debug this. A service restarts every few hours. `kubectl get pod` shows `RESTARTS` growing and the pod is never `Pending` or `Evicted`. What do you run, and what are the two possible conclusions?

    ```console
    $ kubectl get pod api-7c9d8b5f4-lm2xs
    NAME                   READY   STATUS    RESTARTS      AGE
    api-7c9d8b5f4-lm2xs    1/1     Running   6 (2h ago)    14h
    ```

<details markdown="1"><summary>Hint</summary>

The reason a container last ended is recorded in the pod status and shown by `describe`.

</details>

<details markdown="1"><summary>Check</summary>

Run `kubectl describe pod api-7c9d8b5f4-lm2xs` and read `Last State` under the container. `Reason: OOMKilled` with exit code 137 means the container exceeded its memory limit: look for a leak or raise the limit and request to the measured peak plus headroom. A different reason, such as `Error` after a failed liveness probe in the events, means the cause is elsewhere (lesson 13). Reading the reason first avoids raising a limit for a problem that is not memory.

</details>

5. ▢ A node comes under memory pressure. It runs pod x, `BestEffort`, pod y, `Burstable` using more than its request, and pod z, `Guaranteed`. In what order does the kubelet consider them, and which part of that order is the QoS class and which is not?

<details markdown="1"><summary>Check</summary>

Roughly x, then y, then z. The kubelet does not read the class, it ranks by usage over requests and then priority, but those usually line up with the class: x has no request so any usage exceeds it, y exceeds its request, and z stays within its equal request and limit. A `Burstable` pod using less than its request ranks with `Guaranteed`, so the class is a guide, not the rule.

</details>

6. ▢ A namespace has a ResourceQuota on `requests.cpu` and `requests.memory`, and a developer's `kubectl apply` of a Deployment succeeds but no pods appear. What do you check, and how does a LimitRange change the picture?

<details markdown="1"><summary>Check</summary>

The Deployment is accepted, but its ReplicaSet cannot create pods that set no requests, so check `kubectl describe replicaset` and `kubectl get events` for `forbidden: failed quota` messages that tell you to specify requests. Adding a LimitRange with default requests injects values into containers that set none, so the pods pass the quota check. Better still, set real requests in the manifest.

</details>

## Real-world reps

- [ ] On a local cluster, create the four pods from practice item 3 and read their classes with the command shown. Then run `kubectl describe node` on a node and find the `Allocated resources` section.
- [ ] Take one workload you run and compare its requests with `kubectl top pod` output over a day, noting if the request is far above, far below, or near the usage and what that implies for scheduling and eviction.
- [ ] Tomorrow: without notes, state what the scheduler uses, what the kernel enforces for CPU and for memory, the three QoS classes with their rules, and why the kubelet's eviction order is not exactly the QoS order.

## Going further

- [Running Reliably](../reference/running-reliably.md)
- [Docs: "Resource Management for Pods and Containers", Kubernetes](https://kubernetes.io/docs/concepts/configuration/manage-resources-containers/)
- [Docs: "Pod Quality of Service Classes", Kubernetes](https://kubernetes.io/docs/concepts/workloads/pods/pod-qos/)
- [Docs: "Node-pressure Eviction", Kubernetes](https://kubernetes.io/docs/concepts/scheduling-eviction/node-pressure-eviction/)
- [Docs: "Limit Ranges", Kubernetes](https://kubernetes.io/docs/concepts/policy/limit-range/) and [Docs: "Resource Quotas", Kubernetes](https://kubernetes.io/docs/concepts/policy/resource-quotas/)
- [Running Containers](../../containers/reference/running-containers.md), the single-host version of limits
- [Resources](../RESOURCES.md)

---

Not landing? Reread the primary source at the top, since this lesson compresses it and compression is where understanding leaks. Check the [glossary](../GLOSSARY.md) for any term that felt slippery.

If the lesson itself is unclear rather than the material, that is a defect: [open an issue](https://github.com/TokenCemetery/teach/issues).
