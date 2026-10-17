---
title: "24. Observability"
description: Read resource metrics, events, container logs and object state metrics, and know which question each one answers
type: lesson
---

# Lesson 24. Observability

**Mission link:** The mission ends with finding out why a workload is broken. Before you can debug one you need to know where the evidence lives, because each kind of evidence answers one question, has its own lifetime, and is gone by morning if you pick the wrong one.
**Primary source:** [Docs: "Resource metrics pipeline", Kubernetes](https://kubernetes.io/docs/tasks/debug/debug-cluster/resource-metrics-pipeline/)
**Prerequisites:** [Lesson 13](0013-probes.md), [Lesson 15](0015-requests-limits-and-qos.md), [Lesson 19](0019-autoscaling-and-disruptions.md), [Requests and limits](../GLOSSARY.md), [HorizontalPodAutoscaler](../GLOSSARY.md), [Readiness probe](../GLOSSARY.md), [kubelet](../GLOSSARY.md)

## Warm-up

1. ▢ A container goes over its CPU limit and another goes over its memory limit. What does the kernel do to each?

<details markdown="1"><summary>Check</summary>

The CPU one is throttled: it keeps running, only slower. The memory one may be killed by the out-of-memory killer, and the kubelet then restarts it (lesson 15). A CPU limit slows a container down, a memory limit ends it.

</details>

2. ▢ A HorizontalPodAutoscaler targets 70% CPU utilization. Utilization of what, and what has to be installed in the cluster for the HPA to read it?

<details markdown="1"><summary>Check</summary>

Utilization relative to the pods' CPU requests, so a pod with no request gives the HPA nothing to divide by. The HPA reads usage from the Metrics API, which needs an add-on such as metrics-server (lesson 19). This lesson installs it.

</details>

3. ▢ A pod's readiness probe starts failing. What does the cluster do, and what does it not do?

<details markdown="1"><summary>Check</summary>

The pod is marked not ready, so its address is no longer sent traffic through Services. Nothing is restarted: only a liveness probe makes the kubelet restart a container (lesson 13).

</details>

## Know this

### One question per source

A cluster gives you four different kinds of evidence. They are not interchangeable, and most of the confusion around "where do I look" comes from asking one source a question it cannot answer.

|Question|Source|Reads like|Lifetime|
|---|---|---|---|
|How much CPU and memory is it using right now?|Resource metrics: metrics-server|`kubectl top`|Latest value only|
|What did the cluster just do to this object?|Events|`kubectl events`, the bottom of `kubectl describe`|One hour by default|
|What did the process say?|Container logs|`kubectl logs`|Until the pod goes, within rotation limits|
|What state are the objects in, and for how long?|Object state metrics: kube-state-metrics, usually scraped by Prometheus|A query, an alert|As long as you store them|

### Resource metrics

The kubelet embeds cAdvisor, which measures every container. **metrics-server** is a cluster add-on that pulls those figures from each kubelet and serves them through the Metrics API, which the API server exposes for the HPA, the VerticalPodAutoscaler and `kubectl top` ([resource metrics pipeline](https://kubernetes.io/docs/tasks/debug/debug-cluster/resource-metrics-pipeline/)). The Metrics API carries CPU and memory only, and metrics-server stores the latest values only, so it cannot tell you what happened ten minutes ago ([kube-state-metrics README](https://github.com/kubernetes/kube-state-metrics#kube-state-metrics-vs-metrics-server)). Its own README says it is meant for autoscaling, not as a source for a monitoring system ([metrics-server README](https://github.com/kubernetes-sigs/metrics-server)).

```console
$ kubectl top pod -l app=web
NAME                   CPU(cores)   MEMORY(bytes)
web-7c9d8b6f5d-4kq2x   3m           41Mi
web-7c9d8b6f5d-p8w7z   2m           40Mi
$ kubectl top node
NAME                 CPU(cores)   CPU(%)   MEMORY(bytes)   MEMORY(%)
lab-control-plane    142m         3%       612Mi           7%
```

`kubectl top` shows **usage**, not requests or limits. A pod using 3m against a 500m request is over-reserved, and a pod using 900m against a 500m request is a noisy neighbour. Lesson 15's numbers are what you compare it with.

A fresh kind cluster has no metrics-server, and `kubectl top` answers `error: Metrics API not available`. The README names the requirement: the kubelet certificate must be signed by the cluster certificate authority, or metrics-server must be passed `--kubelet-insecure-tls`, which it describes as for testing only. Kind is a local test cluster, and this is the standard workaround there:

```console
$ kubectl apply -f https://github.com/kubernetes-sigs/metrics-server/releases/latest/download/components.yaml
$ kubectl -n kube-system patch deployment metrics-server --type=json \
    -p '[{"op":"add","path":"/spec/template/spec/containers/0/args/-","value":"--kubelet-insecure-tls"}]'
$ kubectl -n kube-system rollout status deployment metrics-server
$ kubectl top node
```

Give it a minute after the rollout before the first `top` returns numbers. Never copy the patch to a real cluster: there, fix the kubelet certificates instead.

### Events

An **event** is a short record that a component wrote about an object: the scheduler placed it, the kubelet pulled an image, a probe failed, a container was killed. They are what `kubectl describe` prints under `Events:` and what `kubectl events` lists.

```console
$ kubectl events --for pod/web-7c9d8b6f5d-4kq2x
LAST SEEN   TYPE      REASON      OBJECT                     MESSAGE
2m          Normal    Scheduled   Pod/web-7c9d8b6f5d-4kq2x   Successfully assigned default/web-7c9d8b6f5d-4kq2x to lab-worker
2m          Normal    Pulled      Pod/web-7c9d8b6f5d-4kq2x   Container image "nginx:1.27" already present on machine
2m          Normal    Started     Pod/web-7c9d8b6f5d-4kq2x   Started container web
```

Events are the first place to look and the worst place to keep history. The API server's `--event-ttl` flag defaults to `1h0m0s` ([kube-apiserver reference](https://kubernetes.io/docs/reference/command-line-tools-reference/kube-apiserver/)), so an incident from last night has no events left. Events are also a note for humans, not a contract: do not build logic on their wording.

### Container logs

Kubernetes captures what a container writes to standard output and standard error, and `kubectl logs` reads it back through the kubelet. Three facts decide whether the log you want still exists ([logging architecture](https://kubernetes.io/docs/concepts/cluster-administration/logging/)):

- The kubelet rotates the files. `containerLogMaxSize` defaults to `10Mi` and `containerLogMaxFiles` to `5`, so a chatty container keeps roughly the last 50 MiB.
- When a container restarts, the kubelet keeps one terminated container with its logs. `kubectl logs --previous` (or `-p`) reads it. That is how you read why a crash-looping container died, since plain `kubectl logs` shows the new, usually empty, instance.
- If a pod is evicted or deleted, its containers and their logs go with it.

The last point is why teams ship logs. Kubernetes provides no native storage for log data, so the usual answer is a node-level agent, run as a DaemonSet (lesson 7), that reads each node's log files and forwards them to a backend, or a sidecar for an application that writes to files instead of the standard streams. The backend, not the cluster, is then the source for "what did it say last night".

```console
$ kubectl logs web-7c9d8b6f5d-4kq2x --tail=20 --since=10m
$ kubectl logs web-7c9d8b6f5d-4kq2x -c web --previous
$ kubectl logs -l app=web --prefix --max-log-requests=10
```

### Object state metrics and Prometheus

Resource metrics say nothing about whether a Deployment has the replicas it asked for. **kube-state-metrics** is a separate service that holds a snapshot of the API objects and generates new metrics from their state, such as `kube_deployment_spec_replicas` against `kube_deployment_status_replicas_available`, `kube_pod_container_status_restarts_total` and `kube_pod_container_status_last_terminated_reason`. Its README draws the line: metrics-server serves the latest resource usage through the Metrics API, while kube-state-metrics derives metrics from object state, and neither forwards anywhere ([kube-state-metrics](https://github.com/kubernetes/kube-state-metrics)).

[Prometheus](https://prometheus.io/docs/introduction/overview/) is the usual consumer. It pulls (scrapes) metrics over HTTP from endpoints you list or discover, stores them as time series and evaluates alert rules over them. The control plane components and the kubelet expose Prometheus-format metrics on `/metrics`, and the kubelet adds `/metrics/cadvisor` ([system metrics](https://kubernetes.io/docs/concepts/cluster-administration/system-metrics/)). That is where history comes from: usage over a week, restarts per hour, "fewer replicas available than desired for ten minutes". The cluster does not ship Prometheus, so installing it is a decision, not a default.

## Practice

1. ▢ A pod restarted six hours ago and nobody looked. Which record of that crash has most likely expired by now?

    - a) The restart count in the pod status
    - b) The last terminated state in the status
    - c) The Warning events written about the crash
    - d) The exit code the kubelet recorded earlier

<details markdown="1"><summary>Check</summary>

**c)** Events are kept for one hour by default. The restart count and the last terminated state (reason and exit code) live in the pod's `status`, so they last until the container restarts again or the pod is deleted. (b) and (d) are the same record. (a) is part of that status too.

</details>

2. ▢ Predict, then run. With metrics-server installed, you run this and wait about a minute. What does `kubectl top pod burn` show for CPU, and how does it compare with the request?

    ```yaml
    apiVersion: v1
    kind: Pod
    metadata:
      name: burn
    spec:
      containers:
        - name: burn
          image: busybox:1.36
          command: ["sh", "-c", "while true; do :; done"]
          resources:
            requests:
              cpu: 100m
    ```

    ```console
    $ kubectl apply -f burn.yaml
    $ kubectl top pod burn
    ```

<details markdown="1"><summary>Hint</summary>

There is no CPU limit. What can a tight loop with nothing to wait for do on a node that has idle cores?

</details>

<details markdown="1"><summary>Check</summary>

```text
NAME   CPU(cores)   MEMORY(bytes)
burn   998m         1Mi
```

A busy loop occupies one core, so usage is close to 1000m, about ten times the 100m request. Only a limit would hold it near the request. `kubectl top` reports usage and ignores the request, so only comparing the two shows a pod far above what the scheduler reserved for it.

</details>

3. ▢ A pod is in `CrashLoopBackOff`. `kubectl logs web-abc` prints nothing, and you are sure the application writes an error before it dies. What do you run?

<details markdown="1"><summary>Hint</summary>

The kubelet keeps one thing from the instance that died. What is logging the new instance right now?

</details>

<details markdown="1"><summary>Check</summary>

`kubectl logs web-abc --previous`. Plain `kubectl logs` reads the current container, which has only just started and has written nothing. `--previous` reads the terminated container the kubelet kept. If the pod has several containers, add `-c`.

</details>

4. ▢ You want an alert when a Deployment has had fewer available replicas than it asked for for ten minutes. Which source can do that, and why can the other three not?

<details markdown="1"><summary>Check</summary>

Object state metrics: kube-state-metrics scraped by Prometheus, comparing `kube_deployment_spec_replicas` with `kube_deployment_status_replicas_available` over time. metrics-server holds only the latest CPU and memory and knows nothing about replicas. Events expire in an hour and are text, not a series you can evaluate. Logs say what a process wrote, not what the cluster holds.

</details>

5. ▢ A team asks to read last Tuesday's logs from a pod that was replaced by a rollout. The cluster has no log backend. What can you tell them, and what is the smallest change that stops this happening again?

<details markdown="1"><summary>Check</summary>

Nothing is recoverable: the old pod's containers and logs were removed with it, and Kubernetes has no native log storage. The smallest change is a node-level agent, a DaemonSet that forwards each container's standard output and error to a backend with its own retention. Raising `containerLogMaxFiles` would not help, since rotation is not the cause.

</details>

6. ▢ Which command pair shows that a pod is using far more memory than it requested, and which number would you compare it with?

<details markdown="1"><summary>Check</summary>

`kubectl top pod NAME --containers` for usage, and `kubectl get pod NAME -o jsonpath='{.spec.containers[*].resources}'` (or `kubectl describe pod`) for the request and limit. Compare usage with the memory limit to see how close it is to an OOM kill, and with the request to see how far it sits above what the scheduler reserved.

</details>

## Real-world reps

- [ ] On your kind cluster, install metrics-server with the commands above, run `kubectl top node` and `kubectl top pod -A`, and find the pod that uses the most memory.
- [ ] Create a pod with a bad image (`kubectl run bad --image=nginx:no-such-tag`), read its events with `kubectl events --for pod/bad`, and note how the `LAST SEEN` column changes while it retries.
- [ ] Tomorrow: without notes, write the four questions and the source that answers each, then say which of the four is gone after an hour and which survives only until the pod is deleted.

## Going further

- [Debugging Workloads](../reference/debugging-workloads.md)
- [Docs: "Resource metrics pipeline", Kubernetes](https://kubernetes.io/docs/tasks/debug/debug-cluster/resource-metrics-pipeline/)
- [Docs: "Logging Architecture", Kubernetes](https://kubernetes.io/docs/concepts/cluster-administration/logging/)
- [Project: kube-state-metrics, Kubernetes](https://github.com/kubernetes/kube-state-metrics)
- [Docs: "Overview", Prometheus](https://prometheus.io/docs/introduction/overview/)
- [Book chapter: "Monitoring Distributed Systems", Google SRE book](https://sre.google/sre-book/monitoring-distributed-systems/)
- [Resources](../RESOURCES.md)

---

Not landing? Reread the primary source at the top, since this lesson compresses it and compression is where understanding leaks. Check the [glossary](../GLOSSARY.md) for any term that felt slippery.

If the lesson itself is unclear rather than the material, that is a defect: [open an issue](https://github.com/TokenCemetery/teach/issues).
