---
title: Configuration
description: ConfigMaps and Secrets as environment and files, update behaviour, and what protects a Secret
type: reference
---

# Configuration: ConfigMaps and Secrets

Stage 4 compressed for lookup. [Lesson 11](../lessons/0011-configmaps.md) covers ConfigMaps and [lesson 12](../lessons/0012-secrets.md) Secrets.

## ConfigMap and Secret side by side

|| ConfigMap | Secret |
|---|---|---|
|Holds|Non-secret settings|Sensitive values|
|Fields|`data` (UTF-8), `binaryData` (base64)|`data` (base64), `stringData` (plain, write-only convenience)|
|Size limit|1 MiB|1 MiB|
|Same namespace as the pod|Yes|Yes|
|Immutable option|`immutable: true`|`immutable: true`|
|Stored in etcd|As is|As is by default, encrypted only if configured|
|Protection|None|RBAC, encryption at rest, how it arrives|

## How a pod consumes them

|As|Manifest fields|Sees changes|
|---|---|---|
|One variable|`env[].valueFrom.configMapKeyRef` or `secretKeyRef`|Never, until the container restarts|
|All keys as variables|`envFrom[].configMapRef` or `secretRef`|Never. Keys that are not valid variable names are skipped silently|
|Files, whole volume|`volumes[].configMap` or `secret`, plus a `volumeMount`|Yes, eventually. The app must re-read|
|One file with `subPath`|`volumeMounts[].subPath`|Never|
|Through the API|Application reads the object with a client|On watch|

- Mounted volume updates take up to the kubelet sync period plus its cache delay, so minutes, not seconds.
- A volume mounted over a directory hides what the image had there.
- A ConfigMap or Secret that does not exist stops the pod from starting, unless the reference is `optional`.
- Secret volumes are `tmpfs` on the node. Set permissions with `defaultMode`.

## Getting a change to running pods

|Goal|Do|
|---|---|
|Env or `subPath` value changed|`kubectl rollout restart deployment/<name>`|
|Change tied to a revision, so rollbacks restore it|Give each config version its own name and reference it in the pod template|
|Generate that name|Kustomize `configMapGenerator` and `secretGenerator` append a content hash|
|Hash in the template|Pod template annotation with a checksum, usually Helm|
|Config can never drift|`immutable: true`, then create `app-v2`|

- A Deployment rolls only when `.spec.template` changes.
- `kubectl rollout undo` restores the template, so it restores the old config only if the name was in the template.
- An immutable object cannot change or be made mutable again. Delete, recreate and restart the pods that used it.

## Who can read a Secret by default

|Who|Why|
|---|---|
|`get`, `list` or `watch` on Secrets|The API returns the contents. `list` is as strong as `get`|
|Can create a pod, or a Deployment, in the namespace|The pod mounts any Secret there and prints it|
|Access to etcd|Stored unencrypted unless configured|
|Privileged container on the node|Reads all Secrets used on that node|

- Base64 is not encryption. `echo <value> | base64 -d` reverses it.
- Separate namespaces and audit alerts limit and detect exposure.
- Keep the Secret out of containers that do not need it.

## Encryption at rest

|Item|Fact|
|---|---|
|Switch|API server flag `--encryption-provider-config`, pointing at an `EncryptionConfiguration`|
|Default|`identity`: no encryption|
|`aescbc`, `secretbox`|Key stored on the control plane host. `aescbc` is not recommended (padding oracle attacks)|
|`kms` v2|Envelope encryption with a key in an external service. Stable from v1.29|
|Verify|Value in etcd starts with `k8s:enc:aescbc:v1:` and the key name|
|Existing Secrets|Rewrite them: `kubectl get secrets --all-namespaces -o json \| kubectl replace -f -`|
|Does not change|What `kubectl get secret -o yaml` returns to an authorised user|

## Keeping secrets out of Git

|Approach|Cost|
|---|---|
|External store, mounted by the Secrets Store CSI Driver|A store, and a driver on every node|
|External store, synced into Secrets by an operator|A store, and the Secret then lives in etcd|
|Encrypted in Git (Sealed Secrets, SOPS)|A key to back up, and a new commit per rotation|
|A plain base64 manifest in Git|Leaked. Rotate the value, then change the approach|

## Sources

- [ConfigMaps](https://kubernetes.io/docs/concepts/configuration/configmap/)
- [Secrets](https://kubernetes.io/docs/concepts/configuration/secret/)
- [Good practices for Kubernetes Secrets](https://kubernetes.io/docs/concepts/security/secrets-good-practices/)
- [Encrypting Confidential Data at Rest](https://kubernetes.io/docs/tasks/administer-cluster/encrypt-data/)
- [Volumes](https://kubernetes.io/docs/concepts/storage/volumes/)
