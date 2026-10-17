---
title: "17. StatefulSets"
description: Stable names, ordered startup and a volume per replica, and why a StatefulSet alone does not make a database safe to run
type: lesson
---

# Lesson 17. StatefulSets

**Mission link:** The mission says to run stateful workloads on persistent storage. A Deployment treats its pods as interchangeable, and a database replica is not interchangeable: it has data, a name its peers know and a place in a start order. A StatefulSet supplies those three things, and the lesson is as much about what it leaves to you as what it gives.
**Primary source:** [Docs: "StatefulSets", Kubernetes](https://kubernetes.io/docs/concepts/workloads/controllers/statefulset/)
**Prerequisites:** [Lesson 5](0005-deployments-and-replicasets.md), [Lesson 9](0009-cluster-dns.md), [Lesson 16](0016-persistent-storage.md), [StatefulSet](../GLOSSARY.md), [Headless Service](../GLOSSARY.md), [PersistentVolumeClaim](../GLOSSARY.md)

## Warm-up

1. ▢ What does a headless Service return for a DNS lookup that a normal `ClusterIP` Service does not?

<details markdown="1"><summary>Check</summary>

A normal Service name resolves to its single virtual IP. A headless Service has `clusterIP: None`, so its name resolves to the addresses of the ready pods themselves (lesson 9). That is what lets clients reach one specific replica.

</details>

2. ▢ A Deployment has 3 replicas and one pod is deleted. What name does the replacement get, and why does that matter for a database?

<details markdown="1"><summary>Check</summary>

A new, random name, because the ReplicaSet creates pods from a template and the pods are interchangeable (lesson 5). A database replica that others address by name, and that owns data, cannot be replaced by a pod with a new identity and an empty disk.

</details>

3. ▢ What happens to a PersistentVolumeClaim's volume when the claim is deleted under a default dynamically provisioned class?

<details markdown="1"><summary>Check</summary>

The class default reclaim policy is `Delete`, so the volume and its data are removed with the claim (lesson 16). Keep that in mind when you read what a StatefulSet does with its claims below.

</details>

## Know this

### What a StatefulSet adds to a Deployment

A StatefulSet runs pods from one template, like a Deployment, but each pod keeps an identity ([Docs](https://kubernetes.io/docs/concepts/workloads/controllers/statefulset/)):

|Guarantee|How|
|---|---|
|Stable name|Pods are named `NAME-0` up to `NAME-(N-1)`, and a replacement gets the same name|
|Stable network identity|A governing headless Service gives each pod a DNS name that survives rescheduling|
|Stable storage|Each pod gets its own PersistentVolumeClaim from `volumeClaimTemplates`, reattached to the same ordinal|
|Order|Pods start, scale and update in a defined order by default|

```yaml
apiVersion: v1
kind: Service
metadata:
  name: nginx
spec:
  clusterIP: None
  selector:
    app: nginx
  ports:
  - port: 80
    name: web
---
apiVersion: apps/v1
kind: StatefulSet
metadata:
  name: web
spec:
  serviceName: nginx
  replicas: 3
  selector:
    matchLabels:
      app: nginx
  template:
    metadata:
      labels:
        app: nginx
    spec:
      containers:
      - name: nginx
        image: registry.k8s.io/nginx-slim:0.24
        ports:
        - containerPort: 80
          name: web
        volumeMounts:
        - name: www
          mountPath: /usr/share/nginx/html
  volumeClaimTemplates:
  - metadata:
      name: www
    spec:
      accessModes: ["ReadWriteOnce"]
      resources:
        requests:
          storage: 1Gi
```

You create the headless Service yourself, because the StatefulSet requires one and does not make it. The Service's name goes in `serviceName`. Each pod then has the hostname `web-0`, `web-1`, `web-2` and the DNS name `web-0.nginx.default.svc.cluster.local`, in the form `POD.SERVICE.NAMESPACE.svc.cluster.local`. The StatefulSet also labels each pod with `statefulset.kubernetes.io/pod-name`, so a Service can target one specific pod. The `volumeClaimTemplates` entry creates one claim per pod, and when `web-1` is replaced on another node it mounts the claim that `web-1` had before.

### Order and its alternative

The default `podManagementPolicy` is `OrderedReady`. Pods are created one at a time from 0 upward, and a pod is not created until all predecessors are running and ready. They are terminated in reverse order, from the highest ordinal down, and a pod is not terminated until its successors are fully shut down. If `web-0` fails while `web-2` is being created, `web-2` waits until `web-0` is ready again. This is why readiness probes (lesson 13) gate a StatefulSet's progress.

`Parallel` removes the waiting: all pods are created or terminated at once, and the identity and storage guarantees stay. Use it when pods do not depend on each other starting in order. Rolling updates use their own strategy, `RollingUpdate` by default, which replaces pods from the highest ordinal down one at a time and waits for each to be ready. A `partition` holds back pods below an ordinal, which allows a canary or a staged rollout, and `OnDelete` updates a pod only when you delete it.

The docs warn about one trap with `OrderedReady` updates: if you roll out a template that never becomes ready, reverting the template is not enough. The controller keeps waiting for the broken pod, so you must also delete the pods that already got the bad template, and then it recreates them from the good one.

### Claims outlive pods

Deleting a StatefulSet, or scaling it down, does not delete the claims it created. The docs say this is for data safety, and the volumes stay until you remove them. If you scale from 3 to 1 and later back to 3, `web-1` and `web-2` find their earlier data waiting.

The optional `persistentVolumeClaimRetentionPolicy` changes that, separately for `whenDeleted` and `whenScaled`, each `Retain` (the default) or `Delete`. With `whenScaled: Delete`, the claims of removed replicas are deleted after their pods stop. The policy only applies when pods go away through deleting or scaling the StatefulSet: a pod replaced after a node failure keeps its claim either way. Also remember the reclaim policy of the claim's volume from lesson 16, because deleting the claim can still delete the data.

Deleting a StatefulSet gives no ordering guarantee for the pod shutdowns. To stop the pods in order, scale to 0 first and then delete.

### What a StatefulSet does not do

A StatefulSet gives each replica a name, an address and a disk. It knows nothing about the application. It does not configure replication between `db-0` and `db-1`, choose a primary, promote a replica when the primary dies, take or restore backups, or run a schema upgrade in the right order. All of that is application knowledge that has to come from somewhere: your own init scripts and configuration, or an operator.

An operator is a controller for a custom resource that encodes the work a human operator would do ([Operator pattern](https://kubernetes.io/docs/concepts/extend-kubernetes/operator/)). The docs list what one may automate: deploying the application on demand, taking and restoring backups, handling upgrades together with schema changes, and choosing a leader for an application with no election of its own. An operator for a database typically creates a StatefulSet, the claims and the Service underneath, so it builds on this lesson and adds the application's own knowledge. Whether to adopt one, or use a managed database instead, is a cost decision for lesson 28.

## Practice

1. ▢ A StatefulSet named `db` has 3 replicas, and `db-1` is deleted. What is the replacement's name, and which claim does it mount?

    - a) A random name, a new claim
    - b) A random name, the db-1 claim
    - c) The name db-1, a new claim
    - d) The name db-1, the db-1 claim

<details markdown="1"><summary>Check</summary>

**d)** The name and the storage are what a StatefulSet keeps stable. (a) describes a Deployment pod with scratch storage. (b) keeps the data but loses the identity. (c) keeps the name but loses the data, because each ordinal's claim is reattached to its pod.

</details>

2. ▢ Name the three things the StatefulSet needs besides the pod template to give `db-0` a stable DNS name and its own disk, and say which one you must create yourself.

<details markdown="1"><summary>Check</summary>

A governing headless Service referenced by `serviceName`, which you create yourself, a matching selector, and `volumeClaimTemplates` for the per-pod claims. The DNS name has the form `db-0.SERVICE.NAMESPACE.svc.cluster.local`, and the StatefulSet does not create the Service for you.

</details>

3. ▢ Predict, then run. Apply the manifest above to a kind cluster and watch with `kubectl get pods -w`. In what order do the pods become ready? Then run `kubectl scale statefulset web --replicas=1`. Which pods are removed, in what order, and what does `kubectl get pvc` show afterwards?

<details markdown="1"><summary>Hint</summary>

Think about `OrderedReady` in both directions, and what the docs say about volumes when scaling down.

</details>

<details markdown="1"><summary>Check</summary>

```text
NAME    READY   STATUS              RESTARTS   AGE
web-0   0/1     ContainerCreating   0          2s
web-0   1/1     Running             0          7s
web-1   0/1     ContainerCreating   0          1s
web-1   1/1     Running             0          6s
web-2   0/1     ContainerCreating   0          1s
web-2   1/1     Running             0          6s
```

Each pod starts only after the previous one is ready. Scaling to 1 terminates `web-2` first and `web-1` after it is gone, and `web-0` stays. The claims are untouched:

```text
NAME        STATUS   VOLUME          CAPACITY   ACCESS MODES   STORAGECLASS   AGE
www-web-0   Bound    pvc-4a1f0c2e-7b53-4c8d-9e21-6f0a3d5b8c17   1Gi        RWO            standard       3m
www-web-1   Bound    pvc-9c2e5d71-0b4a-4f36-8a92-1d7c6e3f4b05   1Gi        RWO            standard       3m
www-web-2   Bound    pvc-d70b8e14-3c6f-4a29-b5d0-8e2f1a9c7d43   1Gi        RWO            standard       3m
```

Scale back to 3 and `web-1` and `web-2` return with their old data.

</details>

4. ▢ Debug this. You roll out a StatefulSet update with a typo in the image name. `web-2` is stuck in `ImagePullBackOff`. You fix the image in the manifest and apply it, yet `web-2` is still stuck. Why, and what completes the rollback?

<details markdown="1"><summary>Hint</summary>

Think about what `OrderedReady` waits for before it moves on, and which pod it is waiting for.

</details>

<details markdown="1"><summary>Check</summary>

With `OrderedReady`, the controller is waiting for the broken pod to become ready before it does anything further, and that pod will never become ready with the bad image. The docs describe this as a known issue: after reverting the template you must delete the pod that was created from the bad template. The controller then recreates it from the corrected template and the rollout proceeds. Setting `podManagementPolicy: Parallel` avoids the wait but gives up the ordering.

</details>

5. ▢ A team wants a three-node PostgreSQL cluster with one primary and two replicas. They write a StatefulSet with three replicas and say they are done. What is still missing?

<details markdown="1"><summary>Check</summary>

Everything application-specific: replication setup between the pods, deciding which pod is primary, promoting a replica on failure, backups and their restore, and coordinated upgrades. The StatefulSet gives each pod a stable name, address and disk, and all three pods would start as three independent empty databases. This is the gap an operator fills, or a managed database service avoids.

</details>

6. ▢ You set `persistentVolumeClaimRetentionPolicy` to `whenScaled: Delete`. A node fails and its pod is replaced. Are the claims deleted? What about when you scale down by one replica?

<details markdown="1"><summary>Check</summary>

The failed node's pod is replaced and keeps its claim, because the policy applies only when pods are removed by scaling down or deleting the StatefulSet, not when they are recreated. Scaling down by one deletes the claim of the highest-ordinal replica after its pod stops, and its data goes with it unless the volume's own reclaim policy is `Retain`.

</details>

## Real-world reps

- [ ] On a local cluster, apply the manifest from this lesson and run practice item 3. Then use `kubectl exec web-0 -- hostname` and `kubectl run -it --rm lookup --image=busybox:1.36 --restart=Never -- nslookup web-0.nginx` to see the stable name resolve.
- [ ] Write a file into `web-1`'s volume with `kubectl exec`, delete the pod `web-1`, and confirm that the replacement has the same name and the same file.
- [ ] Tomorrow: without notes, list the three identity guarantees of a StatefulSet, say what `OrderedReady` and `Parallel` do, and name four jobs a StatefulSet leaves to the application or an operator.

## Going further

- [State, Scheduling and Scale](../reference/state-scheduling-and-scale.md)
- [Docs: "StatefulSets", Kubernetes](https://kubernetes.io/docs/concepts/workloads/controllers/statefulset/)
- [Docs: "Run a Replicated Stateful Application", Kubernetes](https://kubernetes.io/docs/tasks/run-application/run-replicated-stateful-application/), a worked example of how much the application does itself
- [Docs: "Operator pattern", Kubernetes](https://kubernetes.io/docs/concepts/extend-kubernetes/operator/)
- [Resources](../RESOURCES.md)

---

Not landing? Reread the primary source at the top, since this lesson compresses it and compression is where understanding leaks. Check the [glossary](../GLOSSARY.md) for any term that felt slippery.

If the lesson itself is unclear rather than the material, that is a defect: [open an issue](https://github.com/TokenCemetery/teach/issues).
