---
title: "22. Kustomize"
description: Keep one base of plain manifests and patch it per environment with overlays, without a template language
type: lesson
---

# Lesson 22. Kustomize

**Mission link:** The mission says to package manifests for several environments. Staging and production run the same service with a different replica count, image tag and log level. Copying the YAML per environment drifts, and Kustomize avoids that: one base of plain manifests, plus a small overlay that says only what differs.
**Primary source:** [Docs: "Declarative Management of Kubernetes Objects Using Kustomize", Kubernetes](https://kubernetes.io/docs/tasks/manage-kubernetes-objects/kustomization/)
**Prerequisites:** [Lesson 3](0003-objects-and-manifests.md), [Lesson 6](0006-rollouts-and-rollbacks.md), [Lesson 11](0011-configmaps.md), [Kustomize](../GLOSSARY.md), [ConfigMap](../GLOSSARY.md), [Rollout](../GLOSSARY.md), [Deployment](../GLOSSARY.md)

## Warm-up

1. ▢ What makes a Deployment start a new rollout, and what does not?

<details markdown="1"><summary>Check</summary>

A change to `spec.template`, which creates a new ReplicaSet (lessons 5 and 6). Changing `replicas` scales the current ReplicaSet and does not roll anything out.

</details>

2. ▢ You edit a ConfigMap that a pod reads through `envFrom`. Does the running pod see the new value?

<details markdown="1"><summary>Check</summary>

No. Environment variables are fixed when the container starts, so the pod needs a restart. A ConfigMap mounted as files does update in place after a delay (lesson 11). That gap is what the generator below closes.

</details>

3. ▢ What does `kubectl apply -f` do with a manifest that already exists in the cluster?

<details markdown="1"><summary>Check</summary>

It compares the manifest with the last applied configuration and the live object, and patches the difference, so applying the same file twice changes nothing (lesson 3). It is declarative: you state the result, not the steps.

</details>

## Know this

### Base, overlay, and no template language

**Kustomize** is built into `kubectl`: `kubectl kustomize <dir>` renders a directory and `kubectl apply -k <dir>` applies it ([docs](https://kubernetes.io/docs/tasks/manage-kubernetes-objects/kustomization/)). A directory is a Kustomization when it holds a `kustomization.yaml`. A **base** is one that lists plain manifests. An **overlay** is one whose `resources` point at other Kustomization directories, which it modifies. The base knows nothing about its overlays, so one base serves many.

```text
web/
  base/
    deployment.yaml
    kustomization.yaml
  overlays/
    prod/
      kustomization.yaml
      resources.yaml
```

The base is ordinary YAML you could `kubectl apply -f` today. There are no placeholders and no logic: an overlay changes real fields in real manifests, so a reviewer reads the actual result by running `kubectl kustomize`. The price is that anything the field model cannot express, such as a loop over a list, a conditional or a computed value, has no answer in Kustomize.

```yaml
# base/kustomization.yaml
resources:
- deployment.yaml
configMapGenerator:
- name: web-config
  literals:
  - LOG_LEVEL=info
```

```yaml
# overlays/prod/kustomization.yaml
resources:
- ../../base
namespace: prod
replicas:
- name: web
  count: 3
images:
- name: nginx
  newTag: "1.28"
patches:
- path: resources.yaml
configMapGenerator:
- name: web-config
  behavior: merge
  literals:
  - LOG_LEVEL=warn
```

### Transformers and patches

Common changes have their own fields, which need no patch ([kustomization reference](https://kubectl.docs.kubernetes.io/references/kustomize/)):

|Field|Does|
|---|---|
|`namespace`|Sets the namespace on every namespaced resource. It does not create the Namespace|
|`namePrefix`, `nameSuffix`|Renames resources, and Kustomize updates the references to them|
|`replicas`|Sets the replica count of a named workload|
|`images`|Overrides the name, tag or digest of images that match `name`, without a patch|
|`labels`|Adds labels to resources and, optionally, to selectors|

The `images` field matches by image name without the tag. With `name: nginx` and `newTag: "1.28"`, an `nginx:1.27` in the base becomes `nginx:1.28`, and `newName` swaps the repository, which is how an overlay points at a private registry ([images reference](https://kubectl.docs.kubernetes.io/references/kustomize/kustomization/images/)).

Anything else uses the `patches` field. A patch is a **strategic merge patch**, a partial manifest that is merged into the matching resource, or a **JSON 6902 patch**, a list of `op`, `path` and `value` steps. Each patch is a file or an inline string and can be targeted by kind, name, namespace or label selector ([patches reference](https://kubectl.docs.kubernetes.io/references/kustomize/kustomization/patches/)). A strategic merge patch finds the target by `apiVersion`, `kind` and `metadata.name`, and merges list items by their key, so containers merge by `name`. Keep each patch small and doing one thing.

### Generated ConfigMaps and the hash suffix

`configMapGenerator` builds a ConfigMap from literals or files, and appends a hash of the contents to its name. Kustomize rewrites every reference in the manifests to the suffixed name. Rendered from the base above:

```console
$ kubectl kustomize base
apiVersion: v1
data:
  LOG_LEVEL: info
kind: ConfigMap
metadata:
  name: web-config-hf678c7m2b
---
apiVersion: apps/v1
kind: Deployment
...
        envFrom:
        - configMapRef:
            name: web-config-hf678c7m2b
```

Change `LOG_LEVEL` to `debug` and the name becomes `web-config-47668c6k28`. The ConfigMap is a new object, and the Deployment's pod template now references a different name, so **editing the config changes the pod template and triggers a rollout**. The plain ConfigMap from lesson 11 gave you no restart. The suffix gives you one, and rolling back the Deployment restores the old ConfigMap name, which still exists, along with the old pods. The docs describe the suffix as ensuring a new ConfigMap is generated when the contents change ([docs](https://kubernetes.io/docs/tasks/manage-kubernetes-objects/kustomization/)). `generatorOptions: {disableNameSuffixHash: true}` turns the suffix off and takes the rollout with it. The old generated ConfigMaps are not deleted by the apply, so they accumulate until you remove them.

An overlay generator that sets `behavior: merge` or `replace` modifies the base's ConfigMap. The base must have defined the generator for the suffix to follow the change.

## Practice

1. ▢ Which command shows the final YAML for `overlays/prod` without touching a cluster?

    - a) `kubectl kustomize overlays/prod`
    - b) `kubectl apply -k overlays/prod`
    - c) `kubectl get -k overlays/prod`
    - d) `kubectl create -k overlays/prod`

<details markdown="1"><summary>Check</summary>

**a)** It renders to standard output and sends nothing to the API server. (b) and (d) write to the cluster, and (c) reads live objects, not the rendered files. Run (a) before every apply and read the result.

</details>

2. ▢ Predict, then run. The deployed overlay sets `LOG_LEVEL=warn`. You change that literal to `error` and run `kubectl apply -k overlays/prod`, then `kubectl -n prod get rs` and `kubectl -n prod get cm`. How many of each, and did a rollout happen?

<details markdown="1"><summary>Hint</summary>

The literal feeds a hash, the hash is in the ConfigMap's name, and the name is in the pod template. What does lesson 6 say a pod template change causes?

</details>

<details markdown="1"><summary>Check</summary>

Two ReplicaSets and two generated ConfigMaps, and yes, a rollout. The new content gets a new name, the Deployment's template now references it, and a new ReplicaSet replaces the old one with the usual rolling update. The old ReplicaSet is scaled to 0 and kept for rollback, and the old ConfigMap stays because `apply` does not prune. A hand edit to a ConfigMap would have produced one ReplicaSet and no restart.

</details>

3. ▢ An overlay patch intends to add a CPU request to the container `web`, but the Deployment is rejected with `spec.template.spec.containers[0].image: Required value`. Find the mistake.

    ```yaml
    spec:
      template:
        spec:
          containers:
          - name: nginx
            resources:
              requests:
                cpu: 100m
    ```

<details markdown="1"><summary>Hint</summary>

Containers merge by `name`. Run `kubectl kustomize` on the overlay and count the containers in the output.

</details>

<details markdown="1"><summary>Check</summary>

The container in the base is named `web`, and the patch names `nginx`, so there is no match and the patch adds a second container that has a name and resources but no image. The render shows two containers. Change the patch's `name` to `web`. The image name and the container name are different things, and the image is what the `images` field matches, not the container name.

</details>

4. ▢ Write the `images` entry that makes a production overlay use `registry.example.com/team/web` at tag `2.4.1` wherever the base has `web:latest`.

<details markdown="1"><summary>Check</summary>

```yaml
images:
- name: web
  newName: registry.example.com/team/web
  newTag: "2.4.1"
```

`name` matches the image name in the base, without a tag. Quote the tag, because YAML reads a bare `1.20` as the number 1.2. No patch is needed.

</details>

5. ▢ Predict, then run. You run `kubectl apply -k overlays/prod` on a fresh cluster where the `prod` namespace does not exist. What happens, and why does `namespace: prod` not help?

<details markdown="1"><summary>Hint</summary>

The `namespace` field sets a field on the resources it is given. Is a Namespace one of the resources in the base?

</details>

<details markdown="1"><summary>Check</summary>

The apply fails with `namespaces "prod" not found`. The field stamps `metadata.namespace` onto each namespaced resource and creates nothing. Add a `namespace.yaml` with a `Namespace` named `prod` to the overlay's `resources`, or create it first with `kubectl create namespace prod`.

</details>

6. ▢ Your team asks for `disableNameSuffixHash: true` because the generated names are ugly. What do you ask them to accept in return?

<details markdown="1"><summary>Check</summary>

The ConfigMap name stays fixed, so a content change no longer changes the pod template, and pods using it as environment variables keep the old values until someone restarts them (`kubectl rollout restart`). Rollback also stops restoring the old config, since the one ConfigMap was edited in place. Acceptable if the app reloads files itself. Otherwise the suffix is the feature.

</details>

## Real-world reps

- [ ] Create the `web` directory above on your machine with a one-container Deployment named `web` that reads `envFrom` the generated ConfigMap, run `kubectl kustomize base` and `kubectl kustomize overlays/prod`, and diff the two outputs line by line.
- [ ] On your `lab` cluster run `kubectl create namespace prod`, `kubectl apply -k overlays/prod` and `kubectl -n prod rollout status deployment/web`. Change a literal, apply again, and count ReplicaSets and ConfigMaps with `kubectl -n prod get rs,cm`.
- [ ] Tomorrow: without notes, name five Kustomize fields that change a manifest without a patch and say what the hash suffix on a generated ConfigMap does to a rollout.

## Going further

- [Packaging](../reference/packaging.md)
- [Docs: "Declarative Management of Kubernetes Objects Using Kustomize", Kubernetes](https://kubernetes.io/docs/tasks/manage-kubernetes-objects/kustomization/)
- [Docs: Kustomize reference, kubectl documentation](https://kubectl.docs.kubernetes.io/references/kustomize/)
- [Resources](../RESOURCES.md)

---

Not landing? Reread the primary source at the top, since this lesson compresses it and compression is where understanding leaks. Check the [glossary](../GLOSSARY.md) for any term that felt slippery.

If the lesson itself is unclear rather than the material, that is a defect: [open an issue](https://github.com/TokenCemetery/teach/issues).
