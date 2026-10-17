---
title: Cluster Security
description: RBAC objects, service account tokens, NetworkPolicy patterns and Pod Security Standards, from stage 7
type: reference
---

# Cluster Security: RBAC, Service Accounts, Network Policy and Pod Security

Stage 7 compressed for lookup. [Lesson 20](../lessons/0020-rbac-and-service-accounts.md) covers RBAC and service accounts, and [lesson 21](../lessons/0021-network-policy-and-pod-security.md) covers network policy, security contexts and Pod Security Standards. For one container on one host, see [Container Security](../../containers/reference/container-security.md).

## RBAC objects

Permissions only add. There are no deny rules.

|Object|Scope|Use|
|---|---|---|
|`Role`|One namespace|Rules for namespaced resources|
|`ClusterRole`|Cluster|Cluster-scoped resources, non-resource URLs, or reusable rules|
|`RoleBinding`|One namespace|Grants a Role or a ClusterRole inside that namespace only|
|`ClusterRoleBinding`|Cluster|Grants a ClusterRole in every namespace|

```yaml
rules:
- apiGroups: [""]            # "" is the core group
  resources: ["pods", "pods/log"]
  resourceNames: ["web-0"]   # optional, not for create or deletecollection
  verbs: ["get", "list", "watch"]
```

- Verbs: `get`, `list`, `watch`, `create`, `update`, `patch`, `delete`, `deletecollection`, plus `escalate`, `bind`, `impersonate`.
- Subresources use a slash: `pods/log`, `pods/exec`. `pods` alone does not cover them.
- A binding's `roleRef` is immutable. Delete and recreate it to change the role.
- You can create a role or binding only if you hold its permissions already, or hold `escalate` or `bind`.
- Subjects: `User`, `Group`, `ServiceAccount`. A service account's username is `system:serviceaccount:<namespace>:<name>`.

## Commands

|Task|Command|
|---|---|
|Create a Role|`kubectl -n NS create role NAME --verb=get,list --resource=pods`|
|Bind it to a service account|`kubectl -n NS create rolebinding NAME --role=ROLE --serviceaccount=NS:SA`|
|Bind a ClusterRole in one namespace|`kubectl -n NS create rolebinding NAME --clusterrole=view --serviceaccount=NS:SA`|
|Bind cluster-wide|`kubectl create clusterrolebinding NAME --clusterrole=ROLE --user=USER`|
|Can I do this?|`kubectl auth can-i create pods -n NS`|
|Can that identity do this?|`kubectl auth can-i list pods -n NS --as=system:serviceaccount:NS:SA`|
|Everything allowed in a namespace|`kubectl auth can-i --list -n NS --as=...`|
|Check a subresource|`kubectl auth can-i get pods --subresource=log`|
|Short-lived token for a service account|`kubectl create token SA -n NS`|

`can-i` prints `yes` or `no` and exits non-zero on `no`. `--as` needs the `impersonate` permission.

## Service accounts

|Fact|Detail|
|---|---|
|Scope|Namespaced. Every namespace has `default`|
|Pod uses|`spec.serviceAccountName`, else `default`|
|Default permissions|None beyond API discovery for authenticated principals|
|Token|Short-lived, rotated by the kubelet, projected at `/var/run/secrets/kubernetes.io/serviceaccount/token` since v1.22|
|Opt out|`automountServiceAccountToken: false` on the pod or the service account, and the pod value wins|
|Long-lived token Secrets|Created by hand only, and the docs advise against them|

## Escalation paths

Review a role holding any of these as if it were admin.

|Permission|Why|
|---|---|
|`get`, `list`, `watch` on `secrets`|`list` and `watch` return contents|
|Create pods or workloads|Mount any Secret in the namespace, run as any service account there|
|Create `persistentvolumes`|`hostPath` reaches the node filesystem|
|`get` on `nodes/proxy`|Kubelet API, which can run commands in pods|
|`escalate`, `bind`|Skip the cannot-grant-what-you-lack check|
|`impersonate`|Act as another identity|
|`create` on `serviceaccounts/token`|Mint tokens for existing service accounts|
|CSR approval for the client signer|Mint client certificates with chosen names|
|Webhook configurations|Read or change every admitted object|
|`patch` on `namespaces`|Change Pod Security and NetworkPolicy labels|

- Bind with `RoleBinding`, not `ClusterRoleBinding`, where you can.
- Avoid `*` for resources and verbs: it covers every future resource too.
- Keep users out of `system:masters`: it bypasses RBAC and no binding revokes it.
- Boundaries inside one namespace are weak.

## NetworkPolicy

- Needs a network plugin that enforces it. Without one the object is stored and ignored, so test with a real connection and a timeout. kind enforces policy by default from v0.24.0.
- Non-isolated until selected, per direction. Once selected for a direction, only the union of the allow rules, the pod's own node and reply traffic get through.
- A connection needs the source's egress to allow it and the destination's ingress to allow it.
- Layer 4 only. ICMP behaviour is undefined, and a pod cannot block its own node.

|Pattern|Spec|
|---|---|
|Deny all ingress|`podSelector: {}`, `policyTypes: [Ingress]`|
|Deny all egress|`podSelector: {}`, `policyTypes: [Egress]`|
|Deny both|`podSelector: {}`, `policyTypes: [Ingress, Egress]`|
|Allow all ingress|`ingress: [{}]` with `policyTypes: [Ingress]`|
|Allow DNS egress|To `namespaceSelector` `kubernetes.io/metadata.name: kube-system` and `podSelector` `k8s-app: kube-dns`, ports 53 UDP and TCP|

```yaml
from:
- namespaceSelector: {matchLabels: {team: a}}
  podSelector: {matchLabels: {role: client}}   # one entry: AND
---
from:
- namespaceSelector: {matchLabels: {team: a}}
- podSelector: {matchLabels: {role: client}}   # two entries: OR
```

|Symptom|Cause|
|---|---|
|`bad address` after default-deny egress|DNS egress not allowed|
|Policy listed, traffic still flows|Plugin does not enforce, selector misses the pod, wrong namespace, or another policy allows it|
|Lookup works, connection times out|The source's egress or the destination's ingress is missing|

## Security context

|Field|Set to|Why|
|---|---|---|
|`runAsNonRoot`|`true`|Kubelet refuses a UID 0 image|
|`runAsUser`, `runAsGroup`|A non-zero ID|Fixes the identity|
|`allowPrivilegeEscalation`|`false`|Sets `no_new_privs`, default is effectively `true`|
|`readOnlyRootFilesystem`|`true`|Default `false`. Mount `emptyDir` for writable paths|
|`capabilities.drop`|`["ALL"]`|Add back only what is needed|
|`seccompProfile.type`|`RuntimeDefault`|Filters system calls|
|`privileged`|`false`|Leave it off|

Pod-level fields apply to every container, and a container field overrides the pod's.

## Pod Security Standards and Admission

|Level|Allows|
|---|---|
|`privileged`|Everything|
|`baseline`|Blocks known escalations: host namespaces, privileged containers, `hostPath`, host ports, among others|
|`restricted`|Baseline plus `allowPrivilegeEscalation: false`, non-root, `RuntimeDefault` or `Localhost` seccomp, drop `ALL` capabilities (only `NET_BIND_SERVICE` may be added back), limited volume types|

```text
pod-security.kubernetes.io/<enforce|audit|warn>: <privileged|baseline|restricted>
pod-security.kubernetes.io/<mode>-version: <vMINOR|latest>
```

|Mode|On violation|
|---|---|
|`enforce`|Pod rejected|
|`audit`|Audit annotation, pod allowed|
|`warn`|Warning to the user, pod allowed|

- `enforce` acts on pods, not on workload resources. A violating Deployment applies, then `get deployment` shows `0/N` and the reason is in ReplicaSet events.
- `audit` and `warn` apply to workload resources as well.
- Roll out with `warn` and `audit` first. Test an `enforce` label with `kubectl label --dry-run=server --overwrite ns NAME pod-security.kubernetes.io/enforce=baseline`.
- List namespaces with no enforce level: `kubectl get namespaces --selector='!pod-security.kubernetes.io/enforce'`.

## Sources

- [Docs: "Using RBAC Authorization", Kubernetes](https://kubernetes.io/docs/reference/access-authn-authz/rbac/)
- [Docs: "Role Based Access Control Good Practices", Kubernetes](https://kubernetes.io/docs/concepts/security/rbac-good-practices/)
- [Docs: "Service Accounts", Kubernetes](https://kubernetes.io/docs/concepts/security/service-accounts/)
- [Docs: "Network Policies", Kubernetes](https://kubernetes.io/docs/concepts/services-networking/network-policies/)
- [Docs: "Pod Security Standards", Kubernetes](https://kubernetes.io/docs/concepts/security/pod-security-standards/)
- [Docs: "Pod Security Admission", Kubernetes](https://kubernetes.io/docs/concepts/security/pod-security-admission/)
