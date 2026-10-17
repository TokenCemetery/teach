---
title: "21. Network Policy and Pod Security"
description: Deny traffic between pods by default, then restrict what a pod may do on its node with security contexts and Pod Security Standards
type: lesson
---

# Lesson 21. Network Policy and Pod Security

**Mission link:** The mission says to lock a workload down. By default every pod can reach every other pod, and a pod can ask the node for almost anything. A NetworkPolicy closes the first gap and a security context with Pod Security Admission closes the second, so a compromised pod has little to reach and little to do.
**Primary source:** [Docs: "Network Policies", Kubernetes](https://kubernetes.io/docs/concepts/services-networking/network-policies/)
**Prerequisites:** [Lesson 4](0004-pods.md), [Lesson 9](0009-cluster-dns.md), [Lesson 20](0020-rbac-and-service-accounts.md), [NetworkPolicy](../GLOSSARY.md), [Pod Security Standards](../GLOSSARY.md), [Label](../GLOSSARY.md), [Selector](../GLOSSARY.md), [Namespace](../GLOSSARY.md)

## Warm-up

1. ▢ A pod looks up `web` and gets an address. Which component answers, and where does it run?

<details markdown="1"><summary>Check</summary>

Cluster DNS answers, served by pods in the `kube-system` namespace behind the `kube-dns` Service (lesson 9). A pod's resolver is pointed at that Service, so any policy that blocks egress from the pod also blocks the lookup.

</details>

2. ▢ RBAC has no deny rule. How do you take a permission away from a subject that holds it through two bindings?

<details markdown="1"><summary>Check</summary>

Remove it from every grant that contains it, because permissions are the union of all bindings (lesson 20). Adding a rule cannot subtract. NetworkPolicy works the same way, which matters below.

</details>

3. ▢ Two containers in one pod: can a policy allow traffic to one and not the other?

<details markdown="1"><summary>Check</summary>

No. Containers in a pod share one network namespace and one IP (lesson 4), and policy selects pods, so it applies to the pod as a whole. Port rules can differ, but the pod is the unit.

</details>

## Know this

### NetworkPolicy needs a plugin that enforces it

A `NetworkPolicy` restricts which connections may reach or leave the pods it selects, at layers 3 and 4 (TCP, UDP and optionally SCTP). The API server stores any valid one, but the policy is implemented by the network plugin, and **a policy with no enforcing plugin behind it has no effect** ([Network Policies](https://kubernetes.io/docs/concepts/services-networking/network-policies/)). `kubectl get networkpolicy` looks identical either way, so you must test that traffic is actually blocked.

On kind, the default network plugin is kindnet. [kind v0.24.0](https://github.com/kubernetes-sigs/kind/releases/tag/v0.24.0) added out-of-the-box network policy support in it, through the `kube-network-policies` project, so a cluster made by a current `kind` enforces the policies in this lesson. Check with `kind version`. If you run an older kind, upgrade it and recreate the cluster, or disable the default plugin and install one that enforces policy: the [kind configuration docs](https://kind.sigs.k8s.io/docs/user/configuration/#disable-default-cni) show `disableDefaultCNI: true`, and the docs call replacing it a power-user feature.

### Isolation is per pod and per direction

A pod is **non-isolated** for ingress until some policy selects it with `Ingress` in `policyTypes`, and for egress until one selects it with `Egress`. Once isolated, only what some policy allows gets through, plus traffic from the pod's own node and reply traffic. Policies never conflict, they only add: the allowed set is the union of every policy that selects the pod. A connection needs both ends to agree, the source's egress rules and the destination's ingress rules.

### Default deny, then allow

The foundation is a policy that selects every pod and allows nothing:

```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: default-deny-all
spec:
  podSelector: {}
  policyTypes:
  - Ingress
  - Egress
```

An empty `podSelector` selects every pod in the namespace. Dropping `Egress` from `policyTypes` gives the ingress-only variant. Then you add narrow allow policies:

```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: allow-client-to-web
spec:
  podSelector:
    matchLabels:
      app: web
  policyTypes:
  - Ingress
  ingress:
  - from:
    - podSelector:
        matchLabels:
          run: client
    ports:
    - protocol: TCP
      port: 80
```

Denying egress also blocks DNS, and the docs warn about it. Pods then fail on every name lookup, not only on the services you meant to cut off. Allow egress to the cluster DNS pods, on port 53 for UDP and TCP:

```yaml
  egress:
  - to:
    - namespaceSelector:
        matchLabels:
          kubernetes.io/metadata.name: kube-system
      podSelector:
        matchLabels:
          k8s-app: kube-dns
    ports:
    - protocol: UDP
      port: 53
    - protocol: TCP
      port: 53
```

The control plane sets the immutable label `kubernetes.io/metadata.name` on every namespace, which is how a policy names one without you labelling it.

### One dash decides AND or OR

Each entry under `from` or `to` is a separate source. Putting `namespaceSelector` and `podSelector` in one entry means both must match. Two entries mean either may match:

```yaml
- from:
  - namespaceSelector: {matchLabels: {team: a}}
    podSelector: {matchLabels: {role: client}}   # AND: client pods in team a
- from:
  - namespaceSelector: {matchLabels: {team: a}}
  - podSelector: {matchLabels: {role: client}}   # OR: any pod in team a, or client pods here
```

The second form is far broader and is a one-character slip. `kubectl describe networkpolicy` shows how the API read it. Policy cannot do everything: it is not defined for ICMP, it cannot block a pod from its own node, and `ipBlock` is for addresses outside the cluster because pod IPs change.

### Security contexts

A **security context** sets what a pod or container may do on its node, under `spec.securityContext` for the pod and `securityContext` on a container, where the container value wins ([Security Context](https://kubernetes.io/docs/tasks/configure-pod-container/security-context/)). The fields that matter most:

|Field|Effect|Default when unset|
|---|---|---|
|`runAsNonRoot: true`|The kubelet refuses to start a container whose image runs as UID 0|No check|
|`runAsUser`, `runAsGroup`|The UID and GID the process runs as|The image's user|
|`allowPrivilegeEscalation: false`|Sets `no_new_privs`, so a process cannot gain privileges, for example through a setuid binary|Effectively `true`|
|`readOnlyRootFilesystem: true`|Mounts the root filesystem read-only, so writable paths must be volumes such as `emptyDir`|`false`|
|`capabilities.drop: ["ALL"]`|Removes every Linux capability, and you add back only what is needed|The runtime's default set|
|`seccompProfile.type: RuntimeDefault`|Filters system calls with the runtime's default profile|No profile requested by the pod|
|`privileged`|Disables most isolation|`false`|

The same ideas apply to a single container; the containers track's [Container Security](../../containers/reference/container-security.md) sheet covers them, and this lesson is where a cluster enforces them.

### Pod Security Standards and Admission

The **Pod Security Standards** define three cumulative levels ([Pod Security Standards](https://kubernetes.io/docs/concepts/security/pod-security-standards/)). `privileged` has no restrictions. `baseline` blocks the known privilege escalations: host namespaces (`hostNetwork`, `hostPID`, `hostIPC`), privileged containers, `hostPath` volumes and host ports, among others. `restricted` adds current hardening: `allowPrivilegeEscalation: false`, running as non-root, a `RuntimeDefault` or `Localhost` seccomp profile, dropping `ALL` capabilities (only `NET_BIND_SERVICE` may be added back), and a short list of allowed volume types.

The built-in **Pod Security Admission** controller applies a level per namespace through labels ([Pod Security Admission](https://kubernetes.io/docs/concepts/security/pod-security-admission/)), stable since v1.25:

```text
pod-security.kubernetes.io/<mode>: <level>
pod-security.kubernetes.io/<mode>-version: <version or latest>
```

|Mode|On a violation|
|---|---|
|`enforce`|The pod is rejected|
|`audit`|An audit annotation is recorded, and the pod is allowed|
|`warn`|The user gets a warning, and the pod is allowed|

Enforcement is on the pod, not on the Deployment above it: `enforce` is not applied to workload resources, only `audit` and `warn` are. So `kubectl apply` of a violating Deployment succeeds, the ReplicaSet cannot create pods, and the failure shows up as events on the ReplicaSet. The safe rollout is to set `warn` and `audit` first, then `enforce` once the warnings stop; adding `--dry-run=server` to `kubectl label` shows how existing pods would fare ([namespace labels](https://kubernetes.io/docs/tasks/configure-pod-container/enforce-standards-namespace-labels/)). Anyone who can patch Namespace labels can loosen this, which is one of the escalation paths from lesson 20.

## Practice

1. ▢ A namespace holds one policy, selecting `app=web` for `Ingress` and allowing traffic only from `app=client`. What happens to traffic into a pod labelled `app=db`?

    - a) It is allowed because no policy selects it
    - b) It is denied because one policy exists here
    - c) It is denied because the plugin blocks defaults
    - d) It is allowed only from pods labelled client

<details markdown="1"><summary>Check</summary>

**a)** A pod is isolated only when a policy selects it. `app=db` is selected by nothing, so it stays non-isolated and takes all ingress. (b) and (c) assume a deny default that does not exist until you create it. (d) misreads the rule, which governs only the pods the policy selects.

</details>

2. ▢ Predict, then run. What does each `wget` print, given the three steps?

    ```console
    $ kubectl create namespace np-lab
    $ kubectl -n np-lab create deployment web --image=nginx:1.27 --port=80
    $ kubectl -n np-lab expose deployment web --port=80
    $ kubectl -n np-lab run client --image=busybox:1.36 --restart=Never -- sleep 3600
    $ kubectl -n np-lab exec client -- wget -qO- -T 3 http://web
    $ kubectl -n np-lab apply -f default-deny-ingress.yaml
    $ kubectl -n np-lab exec client -- wget -qO- -T 3 http://web
    $ kubectl -n np-lab apply -f allow-client-to-web.yaml
    $ kubectl -n np-lab exec client -- wget -qO- -T 3 http://web
    ```

<details markdown="1"><summary>Hint</summary>

The first request runs before any policy exists. The second has a policy selecting `web` with no rules. The third adds a rule that matches the client's labels, and `kubectl run client` labels it `run=client`.

</details>

<details markdown="1"><summary>Check</summary>

The first prints the nginx welcome page, since nothing is isolated. The second prints `wget: download timed out` and `command terminated with exit code 1`: the connection is dropped, not refused, so it hangs until the 3 second timeout. The third prints the welcome page again, because the union of the two policies now allows `client` on port 80. If the second step still shows the page, your plugin is not enforcing policy.

</details>

3. ▢ Which `from` allows pods labelled `role=client` only when they are in a namespace labelled `team=a`?

    - a) One entry holding both selectors together
    - b) Two entries, one for each selector
    - c) A podSelector inside an ipBlock entry
    - d) A lone namespaceSelector with no podSelector

<details markdown="1"><summary>Check</summary>

**a)** Both selectors in one entry must both match, so it is client pods in namespace `team=a`. (b) is an OR: any pod in `team=a`, plus client pods in the policy's own namespace. (c) is not valid, since an `ipBlock` is a separate kind of entry. (d) admits every pod in `team=a`, not only clients.

</details>

4. ▢ After a `default-deny-all` policy, the `client` pod prints `wget: bad address 'web'`, although a policy allows it to reach `web` on port 80. What is missing, and what does the next request do after you fix it?

<details markdown="1"><summary>Hint</summary>

The error is about the name, not the connection. What does the pod ask before it opens a connection to `web`?

</details>

<details markdown="1"><summary>Check</summary>

Egress to cluster DNS. Add the egress policy to the `kube-dns` pods on port 53 for UDP and TCP, shown above. The next request then resolves `web` and times out instead, because egress from `client` to `web` is still denied: a connection needs the source's egress rule and the destination's ingress rule. Add an egress rule to `app=web` on port 80 to the client's policy and it passes.

</details>

5. ▢ Predict, then run. You label a namespace and create a Deployment. What does `get deployment` show, and where do you read why?

    ```console
    $ kubectl create namespace psa-lab
    $ kubectl label namespace psa-lab pod-security.kubernetes.io/enforce=restricted
    $ kubectl -n psa-lab create deployment web --image=nginx:1.27
    $ kubectl -n psa-lab get deployment web
    ```

<details markdown="1"><summary>Hint</summary>

Does `enforce` act on the Deployment, or on the pods? Then ask which object tries to create the pods and where it reports failures.

</details>

<details markdown="1"><summary>Check</summary>

The Deployment is created, and `get deployment web` shows `READY 0/1`. The ReplicaSet's pod creation is refused, so read `kubectl -n psa-lab describe replicaset` or `kubectl -n psa-lab get events`. The event reads like this:

```text
Error creating: pods "web-7c5ddbdf54-x2k9q" is forbidden: violates PodSecurity "restricted:latest": allowPrivilegeEscalation != false (container "nginx" must set securityContext.allowPrivilegeEscalation=false), unrestricted capabilities (container "nginx" must set securityContext.capabilities.drop=["ALL"]), runAsNonRoot != true (pod or container "nginx" must set securityContext.runAsNonRoot=true), seccompProfile (pod or container "nginx" must set securityContext.seccompProfile.type to "RuntimeDefault" or "Localhost")
```

The message lists every violation at once, which is the checklist for the next item.

</details>

6. ▢ Write the `securityContext` for a container named `app` that passes the `restricted` level and also has a read-only root filesystem, and say what a writable `/tmp` needs.

<details markdown="1"><summary>Check</summary>

```yaml
securityContext:
  runAsNonRoot: true
  runAsUser: 10001
  allowPrivilegeEscalation: false
  readOnlyRootFilesystem: true
  capabilities:
    drop: ["ALL"]
  seccompProfile:
    type: RuntimeDefault
```

`seccompProfile` and `runAsNonRoot` may sit at the pod level instead. The image must work as a non-root user, so a service binding port 80 should move to a port above 1024 or add back `NET_BIND_SERVICE`. A read-only root filesystem is not required by `restricted`, so it is extra hardening. Mount an `emptyDir` volume at `/tmp` for anything that writes there.

</details>

7. ▢ A teammate applies a NetworkPolicy, `kubectl get networkpolicy` lists it, and the blocked traffic still flows. Name the causes in order of how often you would check them.

<details markdown="1"><summary>Check</summary>

First, the plugin does not enforce policy, so the object is stored and ignored. Second, the `podSelector` does not match the pod's labels, so the pod is not isolated, which `kubectl get pods --show-labels` shows. Third, the policy is in a different namespace from the pods, since a NetworkPolicy selects pods only in its own namespace. Fourth, a second policy allows the traffic, because policies add. Test deny rules from a real pod with a timeout, every time.

</details>

## Real-world reps

- [ ] On your `lab` cluster, create `np-lab` and run every command in practice item 2. Confirm the second `wget` times out. If it does not, run `kind version`, read the plugin section above and fix that first.
- [ ] Add `default-deny-all` to `np-lab`, watch `bad address` appear, then add the DNS egress policy and the egress rule to `web` until the request succeeds again. Run `kubectl -n np-lab describe networkpolicy` and read how each policy was interpreted.
- [ ] Tomorrow: without notes, write the `securityContext` that passes the `restricted` level, and say which three `pod-security.kubernetes.io` modes exist and which one acts on a Deployment's pods.

## Going further

- [Cluster Security](../reference/cluster-security.md)
- [Container Security](../../containers/reference/container-security.md)
- [Docs: "Network Policies", Kubernetes](https://kubernetes.io/docs/concepts/services-networking/network-policies/)
- [Docs: "Configure a Security Context for a Pod or Container", Kubernetes](https://kubernetes.io/docs/tasks/configure-pod-container/security-context/)
- [Docs: "Pod Security Standards", Kubernetes](https://kubernetes.io/docs/concepts/security/pod-security-standards/)
- [Docs: "Pod Security Admission", Kubernetes](https://kubernetes.io/docs/concepts/security/pod-security-admission/)
- [Resources](../RESOURCES.md)

---

Not landing? Reread the primary source at the top, since this lesson compresses it and compression is where understanding leaks. Check the [glossary](../GLOSSARY.md) for any term that felt slippery.

If the lesson itself is unclear rather than the material, that is a defect: [open an issue](https://github.com/TokenCemetery/teach/issues).
