---
title: "26. Reviewing Manifests"
description: Review someone else's manifests by naming what each choice costs in availability, security and operability
type: lesson
---

# Lesson 26. Reviewing Manifests

**Mission link:** The mission ends with reviewing someone else's manifests by naming what each choice costs. "This looks wrong" starts an argument. "This single replica means every node drain is an outage, and one line fixes it" ends one, and that second sentence is the skill.
**Primary source:** [Docs: "Security Checklist", Kubernetes](https://kubernetes.io/docs/concepts/security/security-checklist/)
**Prerequisites:** [Lesson 13](0013-probes.md), [Lesson 15](0015-requests-limits-and-qos.md), [Lesson 19](0019-autoscaling-and-disruptions.md), [Lesson 21](0021-network-policy-and-pod-security.md), [Liveness probe](../GLOSSARY.md), [Requests and limits](../GLOSSARY.md), [PodDisruptionBudget](../GLOSSARY.md), [Pod Security Standards](../GLOSSARY.md), [Selector](../GLOSSARY.md)

## Warm-up

1. ▢ A container has no resource requests and no limits. What QoS class does its pod get, and what does that mean under node pressure?

<details markdown="1"><summary>Check</summary>

`BestEffort`. It is the first class the kubelet evicts when a node runs short of memory, and the scheduler reserved nothing for it, so it can be packed onto an already busy node (lesson 15).

</details>

2. ▢ What does a PodDisruptionBudget limit, and what does it not protect against?

<details markdown="1"><summary>Check</summary>

It limits voluntary disruptions, such as a node drain, evicting too many pods of a workload at once. It does nothing about a node crashing, a container being OOM-killed, or a node-pressure eviction (lesson 19).

</details>

3. ▢ A liveness probe fails three times. What does the kubelet do, and why is it dangerous to point that probe at a dependency?

<details markdown="1"><summary>Check</summary>

It restarts the container. If the probe fails whenever the database is down, a database outage restarts every replica at once, turning a slow dependency into a full outage of a service that was otherwise fine (lesson 13).

</details>

## Know this

### A finding has four parts

Review the way you would want to be reviewed. Each finding states the **choice** you saw, the **cost** in one of three currencies, the **change** that removes the cost, and, where it applies, **what is fine** about it. The currencies are availability (what stops working, and when), security (what an attacker or a mistake can reach) and operability (what the on-call engineer cannot see, change or roll back).

Rank findings by cost, not by how many lines they touch. A broken Service selector takes the service down today and outranks a missing `readOnlyRootFilesystem`.

### What to look for, and what it costs

|Choice|Cost|Change|
|---|---|---|
|No `resources.requests`|Availability: the scheduler reserves nothing, so the pod is `BestEffort` and evicted first. An HPA on CPU utilization has no request to divide by ([HPA](https://kubernetes.io/docs/concepts/workloads/autoscaling/horizontal-pod-autoscale/))|Set CPU and memory requests from observed usage (lesson 24)|
|Liveness probe that checks a dependency|Availability: a dependency outage restarts every replica together|Liveness checks only the process itself. Put dependency checks in a readiness probe if at all ([probes](https://kubernetes.io/docs/concepts/workloads/pods/probes/))|
|No readiness probe|Availability: traffic reaches a pod before it can serve, during every rollout|Add a readiness probe on a cheap endpoint|
|`image: app:latest`|Operability: you cannot tell what is running and rollback is unreliable. The `:latest` tag also defaults `imagePullPolicy` to `Always` ([images](https://kubernetes.io/docs/concepts/containers/images/))|A version tag, or a digest|
|Single replica|Availability: every rollout, drain and crash is an outage|`replicas: 2` or more, with a PodDisruptionBudget and spread across nodes|
|No PodDisruptionBudget on a multi-replica service|Availability: one drain can evict every replica at once ([disruptions](https://kubernetes.io/docs/concepts/workloads/pods/disruptions/))|`minAvailable` or `maxUnavailable`|
|Runs as root, no `securityContext`|Security: a compromised process starts with the most privilege the image allows|`runAsNonRoot: true`, `allowPrivilegeEscalation: false`, a `seccompProfile`, the fields the `restricted` level asks for ([Pod Security Standards](https://kubernetes.io/docs/concepts/security/pod-security-standards/))|
|Credentials in a ConfigMap, read as environment variables|Security: a ConfigMap "does not provide secrecy or encryption" ([ConfigMaps](https://kubernetes.io/docs/concepts/configuration/configmap/)), so anyone who can read it, including in Git, has the credential|A Secret, delivered without the value in Git (lesson 12)|
|`replicas` set in the manifest while an HPA targets it|Availability: each `kubectl apply` resets the count and fights the autoscaler. The docs recommend removing `spec.replicas` once an HPA is enabled ([HPA](https://kubernetes.io/docs/concepts/workloads/autoscaling/horizontal-pod-autoscale/))|Remove `spec.replicas`|
|Service selector that matches no pod|Availability: the Service is valid and empty, so traffic fails with no error at apply time|Make the Service selector equal the pod template's labels|

On the last row, the Deployment side is stricter: `.spec.selector` must match `.spec.template.metadata.labels` or the API rejects it, and it is immutable after creation ([Deployments](https://kubernetes.io/docs/concepts/workloads/controllers/deployment/)). A Service gets no such check.

Single replica deserves a second look because it fails in a quiet way. Rolling update defaults are `maxUnavailable: 25%` rounded down and `maxSurge: 25%` rounded up ([Deployments](https://kubernetes.io/docs/concepts/workloads/controllers/deployment/)), which for one replica means zero unavailable and one extra pod, so a rollout still works. The drain is the problem: with a PodDisruptionBudget of `minAvailable: 1` it is blocked, and without one the only replica is evicted and the service is down until it reschedules.

### A worked review

Someone has opened a pull request for `shop-api`. This is the whole change:

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: shop-api
spec:
  replicas: 1
  selector:
    matchLabels:
      app: shop-api
  template:
    metadata:
      labels:
        app: shop-api
    spec:
      containers:
        - name: api
          image: registry.example.com/shop/api:latest
          ports:
            - containerPort: 8080
          envFrom:
            - configMapRef:
                name: shop-api-config
          livenessProbe:
            httpGet:
              path: /health/full
              port: 8080
---
apiVersion: v1
kind: Service
metadata:
  name: shop-api
spec:
  selector:
    app: shop
  ports:
    - port: 80
      targetPort: 8080
---
apiVersion: v1
kind: ConfigMap
metadata:
  name: shop-api-config
data:
  LOG_LEVEL: info
  DATABASE_URL: postgres://shop:s3cret@db:5432/shop
---
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: shop-api
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: shop-api
  minReplicas: 2
  maxReplicas: 6
  metrics:
    - type: Resource
      resource:
        name: cpu
        target:
          type: Utilization
          averageUtilization: 70
```

The review, ranked by cost:

1. **The Service selector is `app: shop` and the pods are `app: shop-api`.** The Service will have no endpoints, so nothing reaches the service at all. Change the selector to `app: shop-api`, and check `kubectl get endpointslices -l kubernetes.io/service-name=shop-api`.
2. **`DATABASE_URL` holds a password in a ConfigMap.** Anyone with read access to ConfigMaps in the namespace, and everyone who can read this repository, has the production credential. Move it to a Secret, rotate the password because it is now in Git history, and keep the Secret out of Git (lesson 12).
3. **The liveness probe path is `/health/full`.** I assume from the name that it queries the database, which should be confirmed in the code. If it does, a database blip restarts every replica together. Point liveness at a check of the process alone, and add a readiness probe for the dependency check.
4. **No resource requests.** The pod is `BestEffort`, and the HPA below has nothing to compute 70% of, so it cannot scale. Set CPU and memory requests from `kubectl top`, and a memory limit.
5. **`replicas: 1` next to an HPA with `minReplicas: 2`.** Every `kubectl apply` of this file sets the Deployment back to one replica and the autoscaler pushes it up again. Delete `spec.replicas`. Fine as it is: the HPA bounds of 2 to 6 are sensible.
6. **`:latest`.** Rolling back will not restore the previous behaviour, and two nodes can run different images under the same tag. Pin a version or digest.
7. **No readiness probe, no PodDisruptionBudget, no `securityContext`.** Rollouts send traffic to unready pods, a drain can evict every replica, and the container runs with whatever user the image sets. Add the probe, a budget with `minAvailable: 1`, and `runAsNonRoot: true` with `allowPrivilegeEscalation: false`.

What is fine here: the ports and `targetPort` line up, the Deployment's selector matches its template, and `apps/v1` and `autoscaling/v2` are current API versions. Say so in the review. A review that only finds faults teaches the author to stop reading it.

## Practice

1. ▢ A pull request has four findings. Which one do you raise first?

    - a) The image tag is latest, not a version
    - b) The Service selector matches none of the pods
    - c) The container does not use a read-only filesystem
    - d) The Deployment leaves the revision history limit unset

<details markdown="1"><summary>Check</summary>

**b)** It stops all traffic the moment it is applied, so it has the largest and most immediate cost. (a) costs operability and is real but slower. (c) is a hardening gap with no outage attached. (d) has a default of 10 old ReplicaSets, so leaving it unset costs nothing.

</details>

2. ▢ Predict, then run. What happens when you apply this, and what does that say about which selector mistakes the API catches?

    ```yaml
    apiVersion: apps/v1
    kind: Deployment
    metadata:
      name: mismatch
    spec:
      replicas: 1
      selector:
        matchLabels:
          app: mismatch
      template:
        metadata:
          labels:
            app: other
        spec:
          containers:
            - name: web
              image: nginx:1.27
    ```

<details markdown="1"><summary>Hint</summary>

Think about who owns the pods: a Deployment must be able to find the pods its own template produces.

</details>

<details markdown="1"><summary>Check</summary>

The API rejects it:

```text
The Deployment "mismatch" is invalid: spec.template.metadata.labels: Invalid value: map[string]string{"app":"other"}: `selector` does not match template `labels`
```

A Deployment's selector must match its template labels, so this mistake is caught at apply time. A Service selector has no such relation to anything, so a Service pointing at labels no pod carries is accepted and fails silently. That is why a reviewer checks Service selectors by hand.

</details>

3. ▢ A reviewer writes: "Don't use latest, it's bad practice." Rewrite it as a finding with the choice, the cost and the change.

<details markdown="1"><summary>Check</summary>

"`image: shop/api:latest` is a moving tag. The cost is operability: nobody can say which build is running, two nodes can hold different images under one tag, and `kubectl rollout undo` goes back to the same tag and may pull the same new image. The tag also sets `imagePullPolicy` to `Always`, so a registry outage breaks pod restarts. Pin `shop/api:1.8.2` or a digest, and let the pipeline write it." Naming the cost is what lets the author decide how much it matters.

</details>

4. ▢ `kubectl describe hpa shop-api` shows `ScalingActive False` with the reason `FailedGetResourceMetric` and a message that the pod is missing a CPU request. The HPA looks right. Where is the defect, and in which manifest?

<details markdown="1"><summary>Hint</summary>

The HPA target is a percentage. A percentage of what?

</details>

<details markdown="1"><summary>Check</summary>

In the Deployment, not the HPA. A `Utilization` target is a percentage of the container's CPU request, and with no request there is nothing to divide by, so the HPA stops scaling. Add `resources.requests.cpu` to the container. Reviewing the HPA alone would pass it.

</details>

5. ▢ A team has `replicas: 3` in the Deployment manifest and an HPA with `minReplicas: 3`, and they say it is harmless because the numbers agree. When is it not harmless?

<details markdown="1"><summary>Check</summary>

When load has pushed the HPA to, say, 8 replicas and someone runs `kubectl apply` on the manifest: it sets the Deployment back to 3, and the pods above 3 start terminating before the HPA scales up again. The numbers agree only at the minimum. Remove `spec.replicas` and let the HPA own the count. If the field is removed from a live Deployment, follow the HPA page's steps for doing it without dropping to one replica.

</details>

6. ▢ You are reviewing a single-replica Deployment for an internal tool that nobody pages for. The author wants no PodDisruptionBudget and no second replica. Is that a finding, and what do you write?

<details markdown="1"><summary>Check</summary>

Yes, but as a stated cost, not a blocker. Write: "One replica means every rollout, drain and node failure is a short outage. Fine if the team accepts that for an internal tool and says so in the README; do not add a PodDisruptionBudget with `minAvailable: 1`, since it would block draining the node it runs on." The review's job is to make the cost visible, and the owner decides.

</details>

## Real-world reps

- [ ] Apply the `shop-api` manifests above to your kind cluster (create the ConfigMap, Deployment, Service and HPA), then find defects 1, 4 and 5 with `kubectl` alone: `get endpointslices`, `describe hpa`, and `get deploy` before and after a re-apply.
- [ ] Take any Deployment you wrote earlier in this track and review it with the table above. Write each finding in the choice, cost, change form, and count how many you would have missed before this lesson.
- [ ] Tomorrow: without notes, name ten things to check in a Deployment and Service, and for each the currency it costs in: availability, security or operability.

## Going further

- [Manifest Review Checklist](../reference/manifest-review-checklist.md)
- [Docs: "Security Checklist", Kubernetes](https://kubernetes.io/docs/concepts/security/security-checklist/)
- [Docs: "Pod Security Standards", Kubernetes](https://kubernetes.io/docs/concepts/security/pod-security-standards/)
- [Docs: "Role Based Access Control Good Practices", Kubernetes](https://kubernetes.io/docs/concepts/security/rbac-good-practices/)
- [Docs: "Chart Best Practices", Helm](https://helm.sh/docs/chart_best_practices/)
- [Resources](../RESOURCES.md)

---

Not landing? Reread the primary source at the top, since this lesson compresses it and compression is where understanding leaks. Check the [glossary](../GLOSSARY.md) for any term that felt slippery.

If the lesson itself is unclear rather than the material, that is a defect: [open an issue](https://github.com/TokenCemetery/teach/issues).
