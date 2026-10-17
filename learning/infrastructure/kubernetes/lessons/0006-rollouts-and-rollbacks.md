---
title: "6. Rollouts and Rollbacks"
description: Roll out a new version with maxSurge and maxUnavailable, watch it, pause it, and roll it back to a known revision
type: lesson
---

# Lesson 6. Rollouts and Rollbacks

**Mission link:** The mission includes keeping a service healthy through rollouts, and a new version is the most common way a working service breaks. This lesson covers how a Deployment replaces pods without taking the service down, how to tell a rollout that is stuck from one that is slow, and how to return to the last good version quickly.
**Primary source:** [Docs: "Deployments", Kubernetes](https://kubernetes.io/docs/concepts/workloads/controllers/deployment/), the sections on updating, rolling back and the rolling update parameters
**Prerequisites:** [Lesson 5](0005-deployments-and-replicasets.md), [Rollout](../GLOSSARY.md), [Deployment](../GLOSSARY.md), [ReplicaSet](../GLOSSARY.md)

## Warm-up

1. ▢ Which edit to a Deployment creates a new ReplicaSet, and which does not?

<details markdown="1"><summary>Check</summary>

A change to anything in `spec.template`, such as an image or a label, creates a new ReplicaSet. Changing `spec.replicas` only scales the current one (lesson 5).

</details>

2. ▢ What is the `pod-template-hash`, and what is it for?

<details markdown="1"><summary>Check</summary>

A label the Deployment controller adds to each ReplicaSet, to its selector and to its pods, made by hashing the pod template. It keeps a Deployment's ReplicaSets from selecting each other's pods (lesson 5).

</details>

3. ▢ A ReplicaSet owns three pods and you delete one. What brings it back, and does a new Deployment revision appear?

<details markdown="1"><summary>Check</summary>

The ReplicaSet controller creates a replacement from its template. No new revision appears, because the template did not change (lessons 2 and 5).

</details>

## Know this

### What a rollout is

A **rollout** is a Deployment moving its pods from one template revision to the next. It starts when, and only when, the pod template changes ([Deployments](https://kubernetes.io/docs/concepts/workloads/controllers/deployment/)). The controller creates a new ReplicaSet for the new template and shifts replicas from the old ReplicaSet to the new one. You trigger it by editing the template: `kubectl set image deployment/web nginx=nginx:1.27.1` (the part before `=` is the container name), or by applying a changed manifest.

The `spec.strategy.type` is `RollingUpdate`, the default, or `Recreate`. `Recreate` kills every existing pod before it creates new ones, so there is a gap, which suits software that cannot run two versions at the same time. `RollingUpdate` replaces them gradually, so a healthy service stays up.

### maxSurge and maxUnavailable

Two fields in `spec.strategy.rollingUpdate` bound a rolling update, each an absolute number or a percentage of `replicas`:

|Field|Means|Default|Rounding of a percentage|
|---|---|---|---|
|`maxSurge`|Pods allowed above the desired count|25%|Up|
|`maxUnavailable`|Pods allowed to be unavailable|25%|Down|

Both cannot be zero, since then no pod could be added or removed. With the defaults and 4 replicas, the page says the number of pods stays between 3 and 5: one pod above, one pod below. With 3 replicas, 25% of 3 rounds up to 1 surge and down to 0 unavailable, so the Deployment keeps at least 3 available and at most 4 in total. For one replica the same rounding gives a surge of 1 and no unavailable pods.

|`maxSurge`|`maxUnavailable`|With 3 replicas|Costs|
|---|---|---|---|
|1 (default)|0 (default)|3 to 4 pods, at least 3 available|One spare pod of capacity during the rollout|
|0|1|At most 3 pods, at least 2 available|No spare capacity, but one pod less serving|
|3|0|Up to 6 pods, at least 3 available|Fast, and double the resources for a moment|

The default case walks like this: the new ReplicaSet scales to 1, and only when that pod is available does the old one scale to 2; then the new goes to 2, the old to 1, the new to 3, and the old to 0. The Deployment page's events show exactly that order of "Scaled up" and "Scaled down" lines. The strategy never removes a pod that the bound says must stay.

### Available is what the rollout waits for

A new pod counts toward the bound once it is **available**: ready, and ready for at least `minReadySeconds`, which defaults to 0. So a rollout is only as careful as your readiness signal. If a container has no readiness probe, the kubelet always considers readiness a success ([Probes](https://kubernetes.io/docs/concepts/workloads/pods/probes/)), so a new pod is available the moment its container starts, whether or not the application can answer. Lesson 13 writes the probe that makes this honest. `minReadySeconds` adds a floor on top: a new pod must stay ready that long without a container crashing.

Watch a rollout with `kubectl rollout status deployment/web`, which blocks until the rollout finishes and returns 0 when it succeeds and non-zero if it fails or hits the deadline. `--timeout=30s` bounds the wait, which matters in scripts.

### When a rollout is stuck

Suppose the new image does not exist. The new ReplicaSet creates one pod, which sits in `ImagePullBackOff` and never becomes available. Because 3 must stay available (0 unavailable allowed), the controller does not scale the old ReplicaSet down. The service keeps serving from the old pods, and the Deployment shows a rollout that never completes. The page says as much: the controller stops the bad rollout from advancing, depending on `maxUnavailable`.

Left alone it stays stuck. `spec.progressDeadlineSeconds` defaults to 600, and after that long without progress the controller adds a `Progressing` condition with status `False` and reason `ProgressDeadlineExceeded`; `kubectl rollout status` then exits non-zero. The page is explicit that Kubernetes takes no other action on a stalled Deployment: it reports, and it is up to you or a higher-level tool to roll back. Common causes the page lists: insufficient quota, readiness probe failures, image pull errors, insufficient permissions, limit ranges and a misconfigured application.

### Revisions and rollback

Each ReplicaSet the Deployment has created is a recorded **revision**, and the Deployment keeps old ones so it can go back. `spec.revisionHistoryLimit` is how many old ReplicaSets it retains and defaults to 10; set it to 0 and you cannot roll back, since a revision's configuration lives in its ReplicaSet.

```console
$ kubectl rollout history deployment/web
deployment.apps/web
REVISION  CHANGE-CAUSE
1         <none>
2         <none>
3         <none>

$ kubectl rollout history deployment/web --revision=2
```

`--revision=2` prints that revision's pod template. `CHANGE-CAUSE` is copied from the Deployment's `kubernetes.io/change-cause` annotation when the revision is created, so set it before the change, with `kubectl annotate deployment/web kubernetes.io/change-cause="bump to 1.27.1"`. The `--record` flag that once filled it is deprecated.

`kubectl rollout undo deployment/web` returns to the previous revision, and `--to-revision=N` to a specific one. Two properties of a rollback matter. It is itself a rollout, so the same strategy and bounds apply, and the old template is brought back as the newest revision: after an undo to revision 2 from a history of 3, the live revision number is 4 (the page's own output shows `revision=4`). And only the pod template is restored. Scaling does not create a revision, so a rollback does not undo a change to `replicas`.

### Pause, resume and restart

`kubectl rollout pause deployment/web` lets you change the template several times without starting a rollout for each; `kubectl rollout resume deployment/web` then rolls the combined change out as one. While paused, edits to the template have no effect, and you cannot roll back until you resume. `kubectl rollout restart deployment/web` does a rolling restart of the pods under the same strategy, which is how you make pods re-read configuration they only read at start (lesson 11). The `rollout` commands work for DaemonSets and StatefulSets too.

## Practice

1. ▢ A Deployment has 4 replicas and the default strategy. During a rollout, how many pods may exist and how many must be available?

    - a) At most 5 pods; at least 3 available
    - b) At most 4 pods; at least 4 available
    - c) At most 8 pods; at least 2 available
    - d) At most 5 pods; at least 4 available

<details markdown="1"><summary>Check</summary>

**a)** 25% of 4 is 1 for both: one pod of surge above 4, and one pod of unavailability below. (b) would need both bounds at 0, which the API rejects. (c) is a 100% surge with a 50% unavailable bound, not the default. (d) keeps all four available while allowing a surge, which means `maxUnavailable: 0`, not the default for 4 replicas.

</details>

2. ▢ Predict, then run. Starting from the `web` Deployment of 3 replicas, what does each of the last two commands print, and how many pods are listed with which states?

    ```console
    $ kubectl set image deployment/web nginx=nginx:1.27.1
    $ kubectl rollout status deployment/web
    $ kubectl set image deployment/web nginx=nginx:does-not-exist
    $ kubectl rollout status deployment/web --timeout=30s
    $ kubectl get pods -l app=web
    ```

<details markdown="1"><summary>Hint</summary>

For 3 replicas, how many pods may be unavailable, and what does that mean for the old pods while the new pod cannot start?

</details>

<details markdown="1"><summary>Check</summary>

```text
Waiting for deployment "web" rollout to finish: 1 out of 3 new replicas have been updated...
error: timed out waiting for the condition

NAME                   READY   STATUS             RESTARTS   AGE
web-6d9f8b7c5d-4nq7s   1/1     Running            0          3m
web-6d9f8b7c5d-hz2wd   1/1     Running            0          3m
web-6d9f8b7c5d-sw9lp   1/1     Running            0          3m
web-84c6f7d95b-r2k5t   0/1     ImagePullBackOff   0          35s
```

The first rollout to 1.27.1 completes. The second creates one new pod that cannot pull its image. With 3 replicas the default allows no unavailable pod, so the three good pods of 1.27.1 stay up and serve, and the rollout cannot advance. `rollout status` waits for the 30 seconds and times out with a non-zero exit. The hashes on your cluster will differ.

</details>

3. ▢ Predict, then run. The previous item left revisions 1, 2 and 3 in the history, with 3 broken. After the undo, which revision numbers does the history list, and which image do the pods run?

    ```console
    $ kubectl rollout undo deployment/web
    $ kubectl rollout status deployment/web
    $ kubectl rollout history deployment/web
    $ kubectl get deployment web -o jsonpath='{.spec.template.spec.containers[0].image}{"\n"}'
    ```

<details markdown="1"><summary>Hint</summary>

Does a rollback rewrite history, or add to it? The rolled-back template is a rollout of its own.

</details>

<details markdown="1"><summary>Check</summary>

```text
deployment "web" successfully rolled out
deployment.apps/web
REVISION  CHANGE-CAUSE
1         <none>
3         <none>
4         <none>
nginx:1.27.1
```

The undo goes back to revision 2, the template with `nginx:1.27.1`, and the Deployment re-uses that ReplicaSet as the newest revision, 4, so 2 disappears from the list and 3 stays. The pods are back on 1.27.1 and the broken pod is gone. Use `rollout history --revision=4` to confirm the template.

</details>

4. ▢ Ten minutes after the broken rollout began, nobody has intervened. What does the Deployment report, what does `kubectl rollout status` return, and does Kubernetes roll back by itself?

<details markdown="1"><summary>Hint</summary>

Look at the default of `progressDeadlineSeconds`, and at what the docs say the controller does when the deadline passes.

</details>

<details markdown="1"><summary>Check</summary>

After the 600-second default deadline, a `Progressing` condition with status `False` and reason `ProgressDeadlineExceeded` appears in the Deployment's status, and `kubectl rollout status` exits non-zero. Kubernetes does not roll back on its own: the docs say it takes no action on a stalled Deployment beyond reporting. The old pods keep serving the whole time. A person, or a pipeline that checks the exit code, must run `kubectl rollout undo` or fix and reapply the manifest.

</details>

5. ▢ A queue consumer must never have two versions running together. Which strategy, and what does it cost?

<details markdown="1"><summary>Check</summary>

`strategy.type: Recreate`, which kills all existing pods before creating new ones, so no two versions overlap. The cost is downtime between the old pods stopping and the new ones becoming available, for as long as the new pods take to start. A rolling update with a surge always overlaps versions.

</details>

6. ▢ A Deployment with `replicas: 1` and the default strategy is rolled out. Is there a gap in service, and what would make one appear anyway?

<details markdown="1"><summary>Check</summary>

By the rounding rules, `maxUnavailable` becomes 0 and `maxSurge` becomes 1, so the new pod must become available before the old one is removed, and in principle there is no gap. One appears anyway when "available" is a lie: with no readiness probe a pod is ready as soon as its container starts, and the old pod can be removed before the new one can answer. Lesson 13 gives the probe, and lesson 14 covers the traffic still sent to a pod that is shutting down.

</details>

## Real-world reps

- [ ] On the `lab` cluster, run `kubectl get rs -l app=web -w` in one terminal and roll out a new image in another. Write down the sequence of counts and compare it with the default walk above.
- [ ] Set the strategy to `maxSurge: 0, maxUnavailable: 1` with `kubectl patch deployment web -p '{"spec":{"strategy":{"rollingUpdate":{"maxSurge":0,"maxUnavailable":1}}}}'`, roll out again, and confirm there are never more than 3 pods. Then use `kubectl annotate deployment/web kubernetes.io/change-cause="..."` before another change and read it in `rollout history`.
- [ ] Tomorrow: without notes, state the two rolling update fields with their defaults and rounding, say what a stuck rollout looks like and what Kubernetes does about it, and give the command to return to the previous revision.

## Going further

- [Workloads](../reference/workloads.md)
- [kubectl](../reference/kubectl.md)
- [Docs: "Deployments", Kubernetes](https://kubernetes.io/docs/concepts/workloads/controllers/deployment/)
- [Docs: "kubectl rollout", kubectl reference](https://kubernetes.io/docs/reference/kubectl/generated/kubectl_rollout/)
- [Resources](../RESOURCES.md)

---

Not landing? Reread the primary source at the top, since this lesson compresses it and compression is where understanding leaks. Check the [glossary](../GLOSSARY.md) for any term that felt slippery.

If the lesson itself is unclear rather than the material, that is a defect: [open an issue](https://github.com/TokenCemetery/teach/issues).
