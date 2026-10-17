---
title: "3. Objects and Manifests"
description: Every object has apiVersion, kind, metadata, spec and status, and labels, selectors, namespaces and kubectl apply all work on those fields
type: lesson
---

# Lesson 3. Objects and Manifests

**Mission link:** The mission says to read and write manifests, and nearly every Kubernetes mistake you will meet in review is a wrong or missing field in one. This lesson names the fields every object shares and the three mechanisms, labels, namespaces and `kubectl apply`, that act on them.
**Primary source:** [Docs: "Objects In Kubernetes", Kubernetes](https://kubernetes.io/docs/concepts/overview/working-with-objects/)
**Prerequisites:** [Lesson 1](0001-what-kubernetes-is-for.md), [Lesson 2](0002-the-reconciliation-loop.md), [Desired state](../GLOSSARY.md), [Label](../GLOSSARY.md), [Selector](../GLOSSARY.md), [Namespace](../GLOSSARY.md)

## Warm-up

1. ▢ What do the `spec` and the `status` of an object each hold, and who writes each?

<details markdown="1"><summary>Check</summary>

The spec is the desired state, written by you. The status is the observed state, written by the cluster's components. The gap between them is the work a controller has left (lesson 2).

</details>

2. ▢ You delete a pod that a Deployment owns and a new one appears. Which object's field made that happen?

<details markdown="1"><summary>Check</summary>

The `replicas` field in the Deployment's spec, which a controller keeps true. The pod was observed state, so deleting it changed nothing that the spec asks for (lesson 2).

</details>

3. ▢ Which component stores every object, and which component is the only one that talks to it?

<details markdown="1"><summary>Check</summary>

etcd stores them, and the API server is the only component that reads and writes etcd (lessons 1 and 2).

</details>

## Know this

### The fields every manifest has

A **manifest** is a file describing an object, by convention in YAML. `kubectl` converts it to JSON and sends it to the API server ([Objects In Kubernetes](https://kubernetes.io/docs/concepts/overview/working-with-objects/)). The page names four fields you must set:

|Field|Says|
|---|---|
|`apiVersion`|Which version of the Kubernetes API you are using to create this object|
|`kind`|What kind of object it is|
|`metadata`|Data that identifies the object: a `name`, a UID and an optional `namespace`, plus labels and annotations|
|`spec`|The desired state, whose shape is different for every kind|

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: hello
  namespace: default
  labels:
    app: hello
    tier: frontend
  annotations:
    example.com/owner: platform-team
spec:
  containers:
    - name: web
      image: nginx:1.27
```

The cluster adds a `status`. Not every kind has a `spec`: a ConfigMap carries `data` instead ([ConfigMaps](https://kubernetes.io/docs/concepts/configuration/configmap/)), and lesson 11 covers it. `apiVersion` is `group/version`, and the core group, which holds pods, is written as plain `v1`; Deployments are `apps/v1` and Jobs are `batch/v1`. The cluster tells you which it serves:

```console
$ kubectl api-resources
NAME          SHORTNAMES   APIVERSION   NAMESPACED   KIND
configmaps    cm           v1           true         ConfigMap
nodes         no           v1           false        Node
pods          po           v1           true         Pod
deployments   deploy       apps/v1      true         Deployment
jobs                       batch/v1     true         Job
```

You do not need to memorize any `spec`. `kubectl explain pod.spec.containers` prints the field, its type and its description from the cluster's own API definition, and the [API reference](https://kubernetes.io/docs/reference/kubernetes-api/) is the same text on a page.

### Names and the metadata

A name is unique for one kind in one namespace, so you can have a pod and a Deployment both called `myapp-1234`, but not two pods ([Object Names and IDs](https://kubernetes.io/docs/concepts/overview/working-with-objects/names/)). Most kinds need a name that is a valid DNS subdomain: at most 253 characters, lowercase letters, digits, `-` and `.`, starting and ending with an alphanumeric. Some kinds need the stricter DNS label form, at most 63 characters, with no dots. The UID is unique across the whole cluster, which is how a replacement pod with the same name is told apart from the one it replaced: it gets a new UID.

### Labels and selectors

A **label** is a key-value pair in `metadata.labels` that identifies an object for grouping. The [Labels](https://kubernetes.io/docs/concepts/overview/working-with-objects/labels/) page defines the syntax: a key has an optional prefix (a DNS subdomain, then `/`) and a required name of at most 63 characters, and a value is at most 63 characters of alphanumerics, `-`, `_` and `.`. The `kubernetes.io/` and `k8s.io/` prefixes are reserved for Kubernetes itself. Labels are not unique: many objects carry the same ones, which is the point.

A **selector** picks objects by their labels, and it is the core grouping primitive in Kubernetes. Services, Deployments, Jobs and DaemonSets all find their pods with one. There are two forms.

|Form|Example|Notes|
|---|---|---|
|Equality-based|`app=web`, `tier!=cache`|`=`, `==` and `!=`. `tier!=cache` also selects objects that have no `tier` label at all|
|Set-based|`env in (prod, qa)`, `tier notin (cache)`, `partition`, `!partition`|`in`, `notin`, and a bare key for "has the label"|

Comma separates requirements and means AND. There is no OR operator, except by listing values in `in`. On the command line you pass a selector with `-l`: `kubectl get pods -l app=web,tier!=cache`. In a manifest, Deployments, Jobs, ReplicaSets and DaemonSets write it as `matchLabels` (equality, a map) and `matchExpressions` (set-based, a list), and all of it must hold:

```yaml
selector:
  matchLabels:
    app: web
  matchExpressions:
    - { key: tier, operator: NotIn, values: [cache] }
```

A Service uses the older, simpler form, a plain map of equality requirements. Labels are for identifying and selecting. Information that is not for selection, such as an owner contact or a build URL, belongs in an annotation, which a selector cannot match.

### Namespaces

A **namespace** scopes names inside one cluster: names must be unique within a namespace and not across them, and a resource can be in only one ([Namespaces](https://kubernetes.io/docs/concepts/overview/working-with-objects/namespaces/)). A fresh cluster has four: `default`, `kube-system` (the cluster's own components), `kube-public` and `kube-node-lease` (the node heartbeat Leases from lesson 2). Not everything is namespaced: Nodes, PersistentVolumes and the namespaces themselves are not, which `kubectl api-resources --namespaced=false` lists.

Set the namespace for one command with `-n`, or save a default for the current context with `kubectl config set-context --current --namespace=team-a`. A Service's DNS name includes its namespace, `<service>.<namespace>.svc.cluster.local` (lesson 9). The page advises against using namespaces to separate versions of the same software: use labels for that. As the glossary says, a namespace is a scope for names and for policy, not by itself a network or security boundary, and lessons 20 and 21 add the policy.

### Applying a manifest

`kubectl apply -f pod.yaml` is declarative: it creates the object if it does not exist and updates it if it does, so the same command works for both ([Declarative Management](https://kubernetes.io/docs/tasks/manage-kubernetes-objects/declarative-config/)). It prints `created`, `configured` or `unchanged`. `kubectl create -f` only creates, and fails with `AlreadyExists` when the object is there. The page warns that mixing `apply` with `create` and `replace` is not supported, because those two do not keep the bookkeeping that `apply` relies on.

That bookkeeping is the `kubectl.kubernetes.io/last-applied-configuration` annotation, which holds what you last applied. On each `apply`, `kubectl` compares your file, the live object and that annotation. The result, in the page's words: fields in your file are set in the live object, and fields you removed from your file are cleared. A field you never put in the file, such as `replicas` changed with `kubectl scale`, is left alone. The corollary bites: if the file does set `replicas: 3` and someone scaled to 5, applying the unchanged file sets it back to 3.

Before changing a cluster, ask it what would change: `kubectl diff -f pod.yaml` prints the difference between live and applied, and `kubectl apply -f pod.yaml --dry-run=server` has the API server validate the request without storing it. By default `kubectl` asks the server to reject unknown or duplicate fields with `--validate=strict`, so a misspelled field is an error instead of being silently ignored. A newer mechanism, **server-side apply** (`--server-side`), moves the merge to the API server, which records which actor owns each field and reports a conflict when two actors set different values ([Server-Side Apply](https://kubernetes.io/docs/reference/using-api/server-side-apply/)). Lesson 19 returns to it for an autoscaler and a manifest that both write `replicas`.

## Practice

1. ▢ Four pods carry these labels: A is `app=web,tier=frontend`, B is `app=web,tier=cache`, C is `app=web` with no `tier`, D is `app=api,tier=frontend`. Which does the selector `app=web,tier!=cache` match?

    - a) Only A matches it
    - b) A and C match
    - c) A and B match
    - d) A and D match

<details markdown="1"><summary>Check</summary>

**b)** `app=web` excludes D, and `tier!=cache` excludes B. A passes both. C passes too, because `!=` also selects objects that lack the key. (a) forgets that rule. (c) ignores the `!=` requirement. (d) ignores the `app=web` requirement.

</details>

2. ▢ Predict, then run. What does each command print? Save the Pod manifest from above as `pod.yaml` and run the commands in order, changing the image to `nginx:1.27.1` before the third.

    ```console
    $ kubectl apply -f pod.yaml
    $ kubectl apply -f pod.yaml
    $ kubectl apply -f pod.yaml
    $ kubectl create -f pod.yaml
    ```

<details markdown="1"><summary>Hint</summary>

`apply` reports what it did to the live object. For the fourth command, think about what `create` is allowed to do when the name is taken.

</details>

<details markdown="1"><summary>Check</summary>

```text
pod/hello created
pod/hello unchanged
pod/hello configured
Error from server (AlreadyExists): error when creating "pod.yaml": pods "hello" already exists
```

The first `apply` creates the pod. The second finds nothing to change. The third changes `spec.containers[0].image`, one of the few pod fields that can be updated in place ([Pods](https://kubernetes.io/docs/concepts/workloads/pods/)), so it is `configured`. `create` never updates, so it fails on an existing name.

</details>

3. ▢ Predict, then run. `pod.yaml` still has `namespace: default` in its metadata. Does the second command succeed? Then delete that line from the file, run the second command again, and say what the last two commands list.

    ```console
    $ kubectl create namespace team-a
    $ kubectl apply -f pod.yaml -n team-a
    $ kubectl get pods -n team-a
    $ kubectl get pods
    ```

<details markdown="1"><summary>Hint</summary>

The manifest and the flag both name a namespace. What should the client do when they disagree? Afterwards, remember that a name is only unique inside one namespace.

</details>

<details markdown="1"><summary>Check</summary>

The first apply fails, because the manifest and the flag disagree and `kubectl` refuses to guess:

```text
error: the namespace from the provided object does not match the namespace "team-a". You must pass '--namespace=default' to perform this operation.
```

Once the `namespace:` line is gone, the apply prints `pod/hello created`. `kubectl get pods -n team-a` then lists `hello`, and `kubectl get pods` lists the `hello` from the previous item in `default`. The same name can exist in two namespaces because a name only has to be unique inside one. Leaving the namespace out of a manifest, and choosing it at apply time, is what lets one file serve several namespaces.

</details>

4. ▢ This apply fails. What does the message tell you, and which command finds the right field name?

    ```console
    $ kubectl apply -f pod.yaml
    Error from server (BadRequest): error when creating "pod.yaml": Pod in version "v1" cannot be handled as a Pod: strict decoding error: unknown field "spec.containers[0].imagee"
    ```

<details markdown="1"><summary>Hint</summary>

The message quotes the path to the field it rejected. Ask the cluster what fields a container accepts.

</details>

<details markdown="1"><summary>Check</summary>

The server rejected a field it does not know, because strict validation is on by default, and the path points at the typo in `image`. `kubectl explain pod.spec.containers` lists the valid field names with their types. Without strict validation the typo would have been ignored and the container would have been created without an image, so the error is the safer outcome.

</details>

5. ▢ A manifest sets `replicas: 3`. You apply it, run `kubectl scale deployment/web --replicas=5`, then apply the same unchanged file again. How many replicas now, and what does it change about how you write a manifest for something an autoscaler also resizes?

<details markdown="1"><summary>Check</summary>

Three. A field that appears in the file is set in the live object on every apply, so the apply undoes the manual scale. If another actor, such as an autoscaler, owns `replicas`, leave the field out of the file: then `apply` does not touch it. This is the conflict that server-side apply's field ownership makes visible, which lesson 19 covers.

</details>

## Real-world reps

- [ ] Write a manifest for a Pod by hand with `app` and `tier` labels and no namespace line, apply it, and run `kubectl get pods --show-labels` and `kubectl get pods -l tier=frontend`. Then apply it again with a changed label and read `configured`.
- [ ] Run `kubectl api-resources` and list three namespaced kinds and three cluster-scoped kinds. Pick one kind you have not seen and read its fields with `kubectl explain`.
- [ ] Tomorrow: without notes, name the four fields every manifest sets and what each means, say what `-l` does, and say how `apply` differs from `create`.

## Going further

- [kubectl](../reference/kubectl.md)
- [Workloads](../reference/workloads.md)
- [Docs: "Objects In Kubernetes", Kubernetes](https://kubernetes.io/docs/concepts/overview/working-with-objects/)
- [Docs: "Labels and Selectors", Kubernetes](https://kubernetes.io/docs/concepts/overview/working-with-objects/labels/)
- [Docs: "Declarative Management of Kubernetes Objects Using Configuration Files", Kubernetes](https://kubernetes.io/docs/tasks/manage-kubernetes-objects/declarative-config/)
- [Resources](../RESOURCES.md)

---

Not landing? Reread the primary source at the top, since this lesson compresses it and compression is where understanding leaks. Check the [glossary](../GLOSSARY.md) for any term that felt slippery.

If the lesson itself is unclear rather than the material, that is a defect: [open an issue](https://github.com/TokenCemetery/teach/issues).
