---
title: "19. Autoscaling and Disruptions"
description: Scale pods with the HorizontalPodAutoscaler and nodes with a node autoscaler, and stop a drain taking too many down with a PodDisruptionBudget
type: lesson
---

# Lesson 19. Autoscaling and Disruptions

**Mission link:** The mission says to scale automatically and keep voluntary disruptions from taking a service down. Load changes, nodes get drained for upgrades, and autoscalers remove nodes to save money, so a service that holds a fixed number of pods in a fixed place will meet an outage sooner or later. Two mechanisms handle it: scaling to the load, and a budget that limits how many pods may be taken down on purpose at once.
**Primary source:** [Docs: "Horizontal Pod Autoscaling", Kubernetes](https://kubernetes.io/docs/concepts/workloads/autoscaling/horizontal-pod-autoscale/)
**Prerequisites:** [Lesson 14](0014-pod-termination.md), [Lesson 15](0015-requests-limits-and-qos.md), [Lesson 18](0018-scheduling.md), [HorizontalPodAutoscaler](../GLOSSARY.md), [PodDisruptionBudget](../GLOSSARY.md), [Eviction](../GLOSSARY.md), [Requests and limits](../GLOSSARY.md)

## Warm-up

1. ▢ A pod has no CPU request. What QoS class is it in if it has no memory settings either, and what does the scheduler assume about its CPU needs?

<details markdown="1"><summary>Check</summary>

`BestEffort`, and the scheduler reserves nothing for it because the request is what it reads (lesson 15). Remember this: the autoscaler below also works from the request.

</details>

2. ▢ When a pod is evicted gracefully, which setting limits how long its containers get to stop, and what is sent first?

<details markdown="1"><summary>Check</summary>

`terminationGracePeriodSeconds`, 30 seconds by default, covers the `preStop` hook and the shutdown. `SIGTERM` goes first and `SIGKILL` at the deadline (lesson 14).

</details>

3. ▢ A node is tainted `NoSchedule`. What happens to the pods already running on it?

<details markdown="1"><summary>Check</summary>

They keep running. `NoSchedule` only stops new pods from being placed there, and `NoExecute` is the effect that evicts running ones (lesson 18).

</details>

## Know this

### The HorizontalPodAutoscaler

A HorizontalPodAutoscaler (HPA) changes the replica count of a workload such as a Deployment or StatefulSet to keep a metric near a target ([Docs](https://kubernetes.io/docs/concepts/workloads/autoscaling/horizontal-pod-autoscale/)). It cannot scale what cannot be scaled, such as a DaemonSet.

```yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: web
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: web
  minReplicas: 2
  maxReplicas: 10
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 60
```

The controller runs a loop, every 15 seconds by default, and each time it reads the metric for the pods and applies one formula:

```text
desiredReplicas = ceil( currentReplicas * currentMetricValue / desiredMetricValue )
```

With 4 replicas averaging 90% CPU utilization against a target of 60%, the answer is `ceil(4 * 90 / 60)` which is 6. With 6 replicas averaging 20%, it is `ceil(6 * 20 / 60)` which is 2. If the ratio is close to 1, within a tolerance of 0.1 by default, nothing changes, so 63% against 60% does not move anything. With several metrics the HPA computes each and takes the largest.

Utilization is a percentage of the container's **request**, not of its limit or of the node. The HPA therefore needs the request: if a container has no CPU request, the pod's utilization is undefined and the HPA takes no action for that metric. The percentages come from the resource metrics API, which metrics-server normally provides and which is not installed by default in most clusters ([Resource metrics pipeline](https://kubernetes.io/docs/tasks/debug/debug-cluster/resource-metrics-pipeline/)). Without it, the HPA reports it cannot read the metric and does nothing.

Scale-up is quick, and scale-down is damped. The HPA picks the highest desired count recorded over a stabilization window, 5 minutes by default for scaling down, so a brief dip does not remove pods that a minute later are needed again. Pods that are not yet ready, or have no metrics yet, are treated conservatively to avoid overshooting during startup, so a readiness probe (lesson 13) that tells the truth also makes autoscaling better. The `behavior` field sets limits on the rate of change, such as at most 4 pods per minute.

When an HPA manages a Deployment, remove `spec.replicas` from the manifest. Otherwise each `kubectl apply` resets the count to that value, which fights the HPA. Scaling to zero replicas is only available for object and external metrics, not CPU.

### Vertical autoscaling and node autoscaling

The **VerticalPodAutoscaler** (VPA) changes a container's requests and limits from observed usage instead of adding pods. It is a custom resource installed separately, reads metrics from the same API, and its updater applies recommendations either by evicting pods so they restart with the new values, or in place where the cluster supports it. It has update modes, including `Off`, which only records recommendations, and the updater respects PodDisruptionBudgets ([Vertical Pod Autoscaling](https://kubernetes.io/docs/concepts/workloads/autoscaling/vertical-pod-autoscale/)). Because the HPA's utilization is a percentage of the request, a VPA that changes the request moves the HPA's measuring stick, so read the VPA page before using both on one workload.

A **node autoscaler** such as Cluster Autoscaler or Karpenter adds and removes nodes ([Node Autoscaling](https://kubernetes.io/docs/concepts/cluster-administration/node-autoscaling/)). It provisions nodes when pods are `Pending` because they fit nowhere, using the pods' requests and scheduling constraints, and it consolidates by removing underused nodes. Both decisions use requests, not real usage. Removing a node that still runs pods is a voluntary disruption, which is why the budget below matters. A local kind cluster has no node autoscaler, since nodes there are containers you create by hand, and managed clouds provide one with their own settings.

### Voluntary and involuntary disruptions

The disruptions documentation splits the ways a pod disappears ([Disruptions](https://kubernetes.io/docs/concepts/workloads/pods/disruptions/)). **Involuntary** disruptions are unavoidable: hardware failure, a kernel panic, a network partition, and eviction for lack of resources. **Voluntary** ones are actions someone chose: deleting a Deployment, updating a template, and draining a node for repair or upgrade, including a node autoscaler scaling down.

### PodDisruptionBudget

A PodDisruptionBudget (PDB) limits how many pods of an application voluntary disruptions may take down at once ([Specifying a Disruption Budget](https://kubernetes.io/docs/tasks/run-application/configure-pdb/)). It uses a label selector and one of two fields:

```yaml
apiVersion: policy/v1
kind: PodDisruptionBudget
metadata:
  name: web-pdb
spec:
  maxUnavailable: 1
  selector:
    matchLabels:
      app: web
```

`minAvailable` says how many pods must remain, and `maxUnavailable` says how many may be down. Use only one. Percentages round up. The docs recommend `maxUnavailable`, because it follows the replica count when it changes. A budget of zero voluntary disruptions, such as `maxUnavailable: 0`, means a drain of a node running one of those pods never completes.

A PDB protects only against actions that go through the Eviction API. `kubectl drain` cordons the node, so nothing new lands on it, and then evicts its pods. If an eviction would break a budget, the API answers `429 Too Many Requests` and the drain retries until the budget allows it or its timeout ends. A drain needs `--ignore-daemonsets` when DaemonSet pods are present. Deleting a pod or a Deployment bypasses PDBs, and so do rolling updates, which a Deployment's own `maxUnavailable` governs ([API-initiated Eviction](https://kubernetes.io/docs/concepts/scheduling-eviction/api-eviction/)).

By default a PDB also blocks evicting a pod that is running but not ready, while the application is already below its budget. The docs recommend `unhealthyPodEvictionPolicy: AlwaysAllow` so a crash-looping application does not stall every drain.

### Two kinds of eviction

|Property|API-initiated eviction|Node-pressure eviction|
|---|---|---|
|Triggered by|`kubectl drain`, autoscalers, the Eviction API|The kubelet, when a node runs short of memory, disk or process IDs|
|Respects a PodDisruptionBudget|Yes|No|
|Respects the grace period|Yes|Soft thresholds may use a capped one, hard thresholds use zero|
|Pod ends as|Deleted gracefully|Marked `Failed`, then terminated|

The first is a negotiation a PDB can slow down. The second is a node protecting itself, which cannot wait for the application. A budget cannot prevent it, and the way to reduce it is requests that match real usage (lesson 15).

## Practice

1. ▢ What does an HPA use as the denominator of CPU utilization?

    - a) The container's CPU request
    - b) The container's CPU limit
    - c) The node's total CPU
    - d) The pod's average usage

<details markdown="1"><summary>Check</summary>

**a)** Utilization is usage as a percentage of the request, and a container with no request leaves it undefined. (b) is what throttling uses, not the HPA. (c) is the node's capacity, which is not involved. (d) is the numerator side, the measured usage.

</details>

2. ▢ A Deployment has 3 replicas, each averaging 150m CPU with a request of 100m, and an HPA with target 50% utilization. What count does the HPA ask for, and what would a 2000m limit and no request do instead?

<details markdown="1"><summary>Check</summary>

Utilization is 150% against a target of 50%, so `ceil(3 * 150 / 50)` is 9 replicas, capped by `maxReplicas`. With a limit and no request, Kubernetes uses the limit as the request, so utilization becomes 7.5% and the HPA would scale down. With neither set, utilization is undefined and the HPA does nothing, which is why the request has to be set deliberately.

</details>

3. ▢ Predict, then run. A kind cluster has three workers, a Deployment `web` with 3 replicas, and this budget. You run the drain on a node that hosts a `web` pod. What happens?

    ```yaml
    apiVersion: policy/v1
    kind: PodDisruptionBudget
    metadata:
      name: web-pdb
    spec:
      minAvailable: 3
      selector:
        matchLabels:
          app: web
    ```

    ```console
    $ kubectl get pdb web-pdb
    $ kubectl drain lab-worker --ignore-daemonsets --timeout=30s
    ```

<details markdown="1"><summary>Hint</summary>

Read `ALLOWED DISRUPTIONS` first. With 3 replicas and `minAvailable: 3`, how many may be evicted?

</details>

<details markdown="1"><summary>Check</summary>

```text
NAME      MIN AVAILABLE   MAX UNAVAILABLE   ALLOWED DISRUPTIONS   AGE
web-pdb   3               N/A               0                     8s

node/lab-worker cordoned
Warning: ignoring DaemonSet-managed Pods: kube-system/kindnet-7kq4d, kube-system/kube-proxy-9xz2m
evicting pod default/web-7f9c5d6b8-4kx2p
error when evicting pods/"web-7f9c5d6b8-4kx2p" -n "default" (will retry after 5s): Cannot evict pod as it would violate the pod's disruption budget.
```

Zero disruptions are allowed, so the node is cordoned but the eviction is refused, and the drain keeps retrying every 5 seconds until the 30 second timeout ends it with an error. Undo it with `kubectl uncordon lab-worker`. Changing the budget to `maxUnavailable: 1` lets the drain proceed one pod at a time.

</details>

4. ▢ Debug this. The HPA exists but the workload never scales, and the `TARGETS` column shows `<unknown>/50%`. Give two likely causes and the command that tells them apart.

    ```console
    $ kubectl get hpa web
    NAME   REFERENCE        TARGETS         MINPODS   MAXPODS   REPLICAS   AGE
    web    Deployment/web   <unknown>/50%   2         10        2          4m
    ```

<details markdown="1"><summary>Hint</summary>

Two things must exist for the percentage to be computed. One is in the cluster and one is in the pod spec.

</details>

<details markdown="1"><summary>Check</summary>

Either the resource metrics API is missing, because metrics-server is not installed or is not healthy, or the containers have no CPU request, so utilization has no denominator. `kubectl describe hpa web` shows the reason in its events and conditions, such as `FailedGetResourceMetric`, and `kubectl top pods` fails if metrics-server is absent. Install metrics-server or add requests to the pod template.

</details>

5. ▢ An application has 5 replicas, needs at least 3 serving traffic, and nodes are drained regularly for upgrades. Write the budget, and say which field you would choose and why.

<details markdown="1"><summary>Check</summary>

```yaml
spec:
  maxUnavailable: 2
  selector:
    matchLabels:
      app: web
```

`minAvailable: 3` is equivalent at 5 replicas, but `maxUnavailable` keeps the meaning as the replica count changes, and the docs recommend it. A drain can then evict at most 2 pods at once, and the rest of the evictions wait until replacements are ready. Add `unhealthyPodEvictionPolicy: AlwaysAllow` so a broken pod cannot hold up a drain.

</details>

6. ▢ A node runs out of memory and the kubelet evicts a pod that a PodDisruptionBudget protects. A colleague says the PDB is broken. What do you answer?

<details markdown="1"><summary>Check</summary>

The PDB is working as designed, because it constrains voluntary evictions through the Eviction API, and node-pressure eviction is the kubelet protecting the node, which ignores budgets and, with a hard threshold, the grace period. The budget still counts the lost pod against what it allows. Reduce the risk with accurate requests and spare node capacity, not a stricter budget.

</details>

## Real-world reps

- [ ] On a multi-node kind cluster, run practice item 3. Then change the budget to `maxUnavailable: 1`, drain again, watch the pods move, and uncordon the node.
- [ ] Create an HPA for a Deployment without installing metrics-server and read `kubectl describe hpa` to see why it cannot compute a target. Then follow the metrics-server README for kind and watch `TARGETS` turn into numbers.
- [ ] Tomorrow: without notes, write the HPA formula, say what it needs in the pod spec and the cluster, and state which eviction a PodDisruptionBudget limits and which it does not.

## Going further

- [State, Scheduling and Scale](../reference/state-scheduling-and-scale.md)
- [Docs: "Horizontal Pod Autoscaling", Kubernetes](https://kubernetes.io/docs/concepts/workloads/autoscaling/horizontal-pod-autoscale/)
- [Docs: "Disruptions", Kubernetes](https://kubernetes.io/docs/concepts/workloads/pods/disruptions/)
- [Docs: "Specifying a Disruption Budget for your Application", Kubernetes](https://kubernetes.io/docs/tasks/run-application/configure-pdb/)
- [Docs: "Node Autoscaling", Kubernetes](https://kubernetes.io/docs/concepts/cluster-administration/node-autoscaling/)
- [Docs: "Node-pressure Eviction", Kubernetes](https://kubernetes.io/docs/concepts/scheduling-eviction/node-pressure-eviction/)
- [Resources](../RESOURCES.md)

---

Not landing? Reread the primary source at the top, since this lesson compresses it and compression is where understanding leaks. Check the [glossary](../GLOSSARY.md) for any term that felt slippery.

If the lesson itself is unclear rather than the material, that is a defect: [open an issue](https://github.com/TokenCemetery/teach/issues).
