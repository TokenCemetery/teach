---
title: "19. Deployment Strategies"
description: Recreate, rolling, blue-green and canary, what each costs in capacity and risk, and what a canary must measure to mean anything
type: lesson
---

# Lesson 19. Deployment Strategies

**Mission link:** The mission says to deploy with a strategy that limits the damage of a bad release. Lesson 18 decided which artifact reaches an environment. This lesson decides how it replaces the one already serving, which sets how many users meet a bad version before anyone notices.
**Primary source:** [Book chapter: "Canarying Releases", The Site Reliability Workbook, Google](https://sre.google/workbook/canarying-releases/)
**Prerequisites:** [Lesson 17](0017-environments-and-approvals.md), [Lesson 18](0018-promotion-between-environments.md), [Deployment strategy](../GLOSSARY.md), [Rolling deployment](../GLOSSARY.md), [Blue-green deployment](../GLOSSARY.md), [Canary](../GLOSSARY.md), and the basics of the [Kubernetes track](../../kubernetes/README.md)

## Warm-up

1. ▢ Lesson 18 deployed an image to two environments. What had to be identical in both, and what could differ?

<details markdown="1"><summary>Check</summary>

The image digest, and so the code and everything inside the image, had to be identical. Configuration read at start, such as `LOG_LEVEL` from the environment's `vars`, could differ. A strategy decides how that same artifact replaces the running one, and it never changes what the artifact is.

</details>

2. ▢ A production job is waiting on a required reviewer. Is a runner in use, and can the job read the environment's secrets?

<details markdown="1"><summary>Check</summary>

No to both. The job is not sent to a runner until the protection rules pass, and it reads environment secrets only after that (lesson 17). The approval gates the start of a deployment, not how the deployment proceeds. Everything in this lesson happens after it.

</details>

3. ▢ What does a Kubernetes Deployment create when you change the pod template, and what happens to the old one?

<details markdown="1"><summary>Check</summary>

It creates a new ReplicaSet for the new template and scales it up while scaling the old ReplicaSet down, within the limits of its update strategy. The old ReplicaSet stays, scaled to zero, which is what rollout history is made of ([Deployments](https://kubernetes.io/docs/concepts/workloads/controllers/deployment/), and the [Workloads](../../kubernetes/reference/workloads.md) sheet).

</details>

## Know this

### Four ways to replace a version

|Strategy|How the new version arrives|Spare capacity|Two versions at once?|Rollback|
|---|---|---|---|---|
|Recreate|All old instances stop, then new ones start|None|No, but there is downtime|Redeploy the old version, with downtime again|
|Rolling|A few instances at a time are replaced|A little, set by a surge limit|Yes, until the rollout ends|Roll out the old version the same way|
|Blue-green|A full second copy is started, then all traffic switches at once|A whole extra copy|Both exist, one takes traffic|Switch traffic back|
|Canary|A small share of real traffic goes to the new version first|A little|Yes, for the length of the canary|Send the share back to the old version|

Fowler's description of blue-green is two production environments as identical as possible, one live, with the router switched to the other once the new release works there, and the router switched back if something goes wrong ([BlueGreenDeployment](https://martinfowler.com/bliki/BlueGreenDeployment.html)). Danilo Sato describes a canary as slowly rolling out a change to a small subset of users before everyone gets it, with a rollback that is simply re-routing users back to the old version ([CanaryRelease](https://martinfowler.com/bliki/CanaryRelease.html)).

Two consequences decide most choices:

- **Rolling and canary run two versions together.** Both must be able to work against the same database, the same queues and the same callers. That is a design constraint on the change, and lesson 21 shows how to meet it for schemas. Recreate avoids it by paying downtime. Blue-green avoids it for requests, since one side takes traffic at a time, but not for data: Fowler notes the database is the hard part, and that the trick is to deploy schema changes separately so both versions work against the schema.
- **Only the canary tells you anything while it runs.** A rolling update stops on a failed readiness check, which catches a crash. It does not notice a version that starts fine and returns wrong answers. A canary exists to find that out, on a small population, before the rest is exposed.

### The same four in Kubernetes

Recreate and rolling are two values of a Deployment's update strategy, and both are documented in [Deployments](https://kubernetes.io/docs/concepts/workloads/controllers/deployment/). `Recreate` kills all existing pods before creating new ones. `RollingUpdate`, the default, is tuned by two limits, both defaulting to 25%:

|Field|Meaning|Rounding|
|---|---|---|
|`maxUnavailable`|Most pods that may be unavailable during the update|Down|
|`maxSurge`|Most pods that may exist above the desired count|Up|

They cannot both be zero. During a rollout the number of available pods stays between `replicas - maxUnavailable` and `replicas + maxSurge`, and the docs warn that terminating pods are not counted, so you may briefly see more pods than that. With `maxUnavailable: 0` and `maxSurge: 1`, a rollout never reduces capacity: it starts one new pod, waits for it to become ready, and only then removes an old one. That is the safest setting and the slowest.

```yaml
strategy:
  type: RollingUpdate
  rollingUpdate:
    maxSurge: 1
    maxUnavailable: 0
```

Blue-green and canary are not built-in strategies, they are arrangements of ordinary objects. For blue-green, run two Deployments, `web-blue` and `web-green`, labelled `slot: blue` and `slot: green`, and point a Service at one with its selector. The switch, and the rollback, is one patch:

```bash
kubectl patch service web -p '{"spec":{"selector":{"app":"web","slot":"green"}}}'
```

For a canary, the Kubernetes docs describe two Deployments that carry a `track` label, `stable` and `canary`, while the Service selects only the labels they share, so it spans both. You set the ratio by replica counts: three stable replicas and one canary give 3:1 ([Managing resources](https://kubernetes.io/docs/concepts/cluster-administration/manage-deployment/#canary-deployments)). That ratio is a coarse tool: the smallest canary is one pod in N, and you cannot pin a user to the canary or send exactly 1% without a router in front. A service mesh or ingress that splits traffic by weight gives finer control, and the pipeline's job is the same either way.

### What a canary must measure

A canary that nobody evaluates is a slow rolling update. The SRE Workbook defines canarying as a partial, time-limited deployment of a change together with its evaluation, calls the part that gets the change the canary and the rest the control, and says the evaluation decides whether to proceed ([Canarying Releases](https://sre.google/workbook/canarying-releases/)). Three points from the chapter make a canary meaningful:

1. **Compare the canary with the control, not with the whole.** The chapter's example is a canary on 5% of the population serving a 20% error rate. Whole-service monitoring sees about 1%, which is easy to miss or blame on noise. Broken down by population, the canary's 20% against the control's baseline is plain.
2. **Pick metrics that indicate problems users feel.** The chapter recommends starting from SLIs such as request success and latency, ranking candidates by how well they predict user-visible trouble, and keeping the list short rather than adding every metric you have.
3. **Make it representative.** The canary needs enough traffic, over enough time, to see the range of requests. A canary that ends after a handful of queries proves little for a service with varied traffic, and the right duration also depends on how often you release.

A canary also needs a rule decided before it starts: which metric, which threshold, how long, and what happens on failure, ideally the automatic rollback of lesson 20. A threshold chosen after seeing the graph is a rationalisation.

## Practice

1. ▢ After all traffic has moved to the new version, which strategy still has the old version running at full size, ready for an instant switch back?

    - a) Recreate
    - b) Rolling
    - c) Blue-green
    - d) Canary

<details markdown="1"><summary>Check</summary>

**c)** Blue-green keeps the idle copy until you decide to retire it, and rollback is switching the router back. (a) stops the old version before the new one starts. (b) retires old instances as it goes, so nothing is left at full size. (d) ends with the canary promoted to everything and the old instances removed.

</details>

2. ▢ A Deployment has 10 replicas, `maxSurge: 3` and `maxUnavailable: 2`. During a rollout, what is the most pods that may exist and the fewest that must be available?

<details markdown="1"><summary>Check</summary>

At most 13 pods (10 plus the surge of 3), and at least 8 available (10 minus the 2 that may be unavailable). Terminating pods are not counted as available, so the pod count can briefly look higher than 13 until they exit. Setting `maxUnavailable: 0` would keep all 10 available and make the rollout wait for each new pod before removing an old one.

</details>

3. ▢ Predict, then run. Add this `strategies-lab.yml` to `ci-cd-practice`. Run it from the Actions tab with the image reference lesson 18 printed, the `ghcr.io` name followed by `@sha256:` and the digest. The script polls `/version` once a second from inside the cluster. After each phase it prints how often each version answered. What does each of the four `show` outputs look like?

    ```yaml
    name: Strategies lab
    on:
      workflow_dispatch:
        inputs:
          image:
            description: Image reference with its digest, from lesson 18
            required: true
    permissions:
      contents: read
      packages: read
    jobs:
      lab:
        runs-on: ubuntu-latest
        steps:
          - uses: helm/kind-action@v1
          - name: Run the lab
            env:
              IMAGE: ${{ inputs.image }}
              REGISTRY_USER: ${{ github.actor }}
              REGISTRY_TOKEN: ${{ secrets.GITHUB_TOKEN }}
            run: |
              [[ "$IMAGE" =~ ^ghcr\.io/[a-z0-9._/-]+@sha256:[0-9a-f]{64}$ ]] || { echo "Not an image digest"; exit 1; }
              kubectl create secret docker-registry ghcr --docker-server=ghcr.io --docker-username="$REGISTRY_USER" --docker-password="$REGISTRY_TOKEN"
              kubectl patch serviceaccount default -p '{"imagePullSecrets":[{"name":"ghcr"}]}'
              deploy() {
                cat <<EOF | kubectl apply -f -
              apiVersion: apps/v1
              kind: Deployment
              metadata:
                name: web-$1
              spec:
                replicas: 4
                selector:
                  matchLabels: {app: web, slot: $1}
                strategy:
                  rollingUpdate: {maxSurge: 1, maxUnavailable: 0}
                template:
                  metadata:
                    labels: {app: web, slot: $1}
                  spec:
                    containers:
                    - name: web
                      image: ${IMAGE}
                      env:
                      - {name: APP_VERSION, value: "$2"}
                      readinessProbe:
                        httpGet: {path: /healthz, port: 8000}
                        periodSeconds: 2
              EOF
              }
              show() {
                kubectl exec poller -- cat /tmp/v.log | grep -v '^$' | sort | uniq -c
                kubectl exec poller -- sh -c ': > /tmp/v.log'
              }
              deploy blue 1
              cat <<EOF | kubectl apply -f -
              apiVersion: v1
              kind: Service
              metadata:
                name: web
              spec:
                selector: {app: web, slot: blue}
                ports:
                - {port: 80, targetPort: 8000}
              EOF
              kubectl rollout status deployment/web-blue --timeout=120s
              kubectl run poller --image=busybox:1.36 --restart=Never -- sh -c 'while true; do wget -q -T 1 -O- http://web/version >> /tmp/v.log; echo >> /tmp/v.log; sleep 1; done'
              kubectl wait --for=condition=Ready pod/poller --timeout=60s
              sleep 3; show > /dev/null
              echo "== rolling update of blue, version 1 to 2"
              kubectl set env deployment/web-blue APP_VERSION=2
              kubectl rollout status deployment/web-blue --timeout=120s
              sleep 3; show
              echo "== green runs version 3 beside blue, no traffic yet"
              deploy green 3
              kubectl rollout status deployment/web-green --timeout=120s
              sleep 3; show
              echo "== switch the Service to green"
              kubectl patch service web -p '{"spec":{"selector":{"app":"web","slot":"green"}}}'
              sleep 5; show
              echo "== roll back: switch the Service to blue"
              kubectl patch service web -p '{"spec":{"selector":{"app":"web","slot":"blue"}}}'
              sleep 5; show
    ```

<details markdown="1"><summary>Hint</summary>

During a rolling update the Service sends traffic to old and new pods together. A blue-green switch changes which Deployment the Service selects, in one step. Remember that blue is already on version 2 after the first phase.

</details>

<details markdown="1"><summary>Check</summary>

```text
== rolling update of blue, version 1 to 2
      7 1
     11 2
== green runs version 3 beside blue, no traffic yet
      9 2
== switch the Service to green
      1 2
      4 3
== roll back: switch the Service to blue
      1 3
      4 2
```

The exact counts vary run to run. The shape is the lesson. During the rolling update both versions answer, because old and new pods serve side by side until the rollout ends. While green runs beside blue it answers nothing, since no traffic goes to it. After the patch, version 3 answers everything, apart from a sample or two that landed before the Service's endpoints updated, which is why one `2` still shows. Switching back is the same patch pointed at blue, which was never removed, so version 2 returns at once, again with a stray `3` or two. If you see no `2` in the first phase, the rolling update was faster than your poll: rerun it.

</details>

4. ▢ Your alerting fires when the overall error rate exceeds 2%. A canary receives 5% of traffic and the new version fails 20% of its requests. Does the alert fire, and what would you change?

<details markdown="1"><summary>Hint</summary>

Work out the share of failing requests across all traffic, not just the canary's.

</details>

<details markdown="1"><summary>Check</summary>

No. Twenty percent of 5% of traffic is 1% of all requests, which is under the threshold, so the alert stays quiet while the canary is clearly broken. Break the metric down by population and compare the canary's error rate with the control's: 20% against the control's baseline is unmissable. This is the SRE Workbook's own example, and the reason it says a canary must be evaluated against a control.

</details>

5. ▢ Debug this. A team runs a canary at 1% for two minutes at 03:00, sees no errors in 40 requests, and promotes. At noon the new version fails on a request type that only appears under daytime traffic. What was wrong with the canary?

<details markdown="1"><summary>Hint</summary>

Ask what the canary population saw, and for how long, compared with what the whole service sees in a day.

</details>

<details markdown="1"><summary>Check</summary>

It was not representative. Forty requests at the quietest hour of the day never included the request type that fails, and two minutes is too short for a service with varied traffic. The chapter says the canary should be large enough and last long enough to see a representative sample, and that the right duration depends on request volume and on how often you release. Fix it with more traffic or more time, perhaps a gradual canary that widens in stages, and write down the evaluation rule before starting. A longer canary at 03:00 would still miss a failure that only daytime traffic triggers, so the canary should span a representative mix of traffic too.

</details>

6. ▢ Pick a strategy for each and say what it costs. (a) A service whose old and new versions cannot both write to the same files, deployed at 02:00 when five minutes of downtime is acceptable. (b) A payment endpoint where rollback must take seconds, and the team can afford double capacity. (c) A stateless service with a mature dashboard and thousands of requests per second.

<details markdown="1"><summary>Check</summary>

(a) Recreate: it never runs two versions together and costs only the downtime. (b) Blue-green: rollback is a switch back, and it costs a full extra copy during the deploy, plus care over the database if the schema changed. (c) Canary: the traffic makes a small share statistically meaningful and the dashboard can compare it with the control. It costs the effort of the evaluation and needs both versions to coexist. Rolling would also be defensible for (c) if no one will watch the canary, and then you accept that only readiness failures stop it.

</details>

## Real-world reps

- [ ] Finish practice item 3. Then replace the `strategy` block in the lab's `deploy` function with `type: Recreate` (and remove `rollingUpdate`, which is only valid for rolling updates), rerun, and compare the first phase. You should see no mix of versions and fewer samples in total, because requests fail while no pod is running.
- [ ] For a service you run, find out its strategy: read the Deployment's `strategy` field or the pipeline's deploy step, and write down its surge and unavailable limits, whether two versions run together, and how you would roll it back.
- [ ] Tomorrow: without notes, fill in the four strategies' spare capacity and rollback method, and state the three things a canary evaluation must have before the canary starts.

## Going further

- [Deployments](../reference/deployments.md)
- [Book chapter: "Canarying Releases", The Site Reliability Workbook, Google](https://sre.google/workbook/canarying-releases/)
- [Article: "BlueGreenDeployment", Martin Fowler](https://martinfowler.com/bliki/BlueGreenDeployment.html)
- [Article: "CanaryRelease", Danilo Sato](https://martinfowler.com/bliki/CanaryRelease.html)
- [Docs: "Deployments", Kubernetes](https://kubernetes.io/docs/concepts/workloads/controllers/deployment/)
- [Workloads](../../kubernetes/reference/workloads.md), rollouts as a cluster feature
- [Resources](../RESOURCES.md)

---

Not landing? Reread the primary source at the top, since this lesson compresses it and compression is where understanding leaks. Check the [glossary](../GLOSSARY.md) for any term that felt slippery.

If the lesson itself is unclear rather than the material, that is a defect: [open an issue](https://github.com/TokenCemetery/teach/issues).
