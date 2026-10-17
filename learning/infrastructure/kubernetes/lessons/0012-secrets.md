---
title: "12. Secrets"
description: A Secret is base64, not encryption, so what protects it is RBAC, encryption at rest and keeping it out of Git
type: lesson
---

# Lesson 12. Secrets

**Mission link:** The mission is to configure a workload and say what a Secret does and does not protect. The word suggests more than the object delivers: by default a Secret is readable by anyone the API lets near it, and by more people than the permission list suggests. Reviewing a workload's configuration means knowing who those people are.
**Primary source:** [Docs: "Secrets", Kubernetes](https://kubernetes.io/docs/concepts/configuration/secret/)
**Prerequisites:** [Lesson 3](0003-objects-and-manifests.md), [Lesson 11](0011-configmaps.md), [Secret](../GLOSSARY.md), [ConfigMap](../GLOSSARY.md), [Namespace](../GLOSSARY.md), [RBAC](../GLOSSARY.md)

## Warm-up

1. ▢ A ConfigMap is mounted as a file and also read as an environment variable. You edit it. Which of the two changes in a running container?

<details markdown="1"><summary>Check</summary>

The mounted file, eventually, once the kubelet syncs, unless it is a `subPath` mount. The environment variable never changes in a running container (lesson 11). Secrets are consumed the same two ways, so the same rule applies.

</details>

2. ▢ Is a namespace a security boundary on its own?

<details markdown="1"><summary>Check</summary>

No. It scopes names and is what RBAC, quotas and Pod Security labels attach to, but by itself it neither blocks network traffic nor restricts who can act in it (lesson 3).

</details>

3. ▢ You change a value in the pod template of a Deployment. What does the cluster do, and what happens to the old pods?

<details markdown="1"><summary>Check</summary>

It creates a new ReplicaSet and rolls pods over to it according to `maxSurge` and `maxUnavailable`, scaling the old ReplicaSet down as the new pods become ready (lessons 5 and 6).

</details>

## Know this

### What a Secret is

A **Secret** is an object like a ConfigMap, meant for data you would not want to leak: a password, a token, a key. Its values go in `data` as base64, or in `stringData` as plain text that the API server encodes for you. It is limited to 1 MiB, and it is consumed the same two ways as a ConfigMap, as environment variables or as files in a volume ([Secrets](https://kubernetes.io/docs/concepts/configuration/secret/)). The default type is `Opaque`, and built-in types such as `kubernetes.io/tls` and `kubernetes.io/dockerconfigjson` check that the expected keys exist.

```console
$ kubectl create secret generic db --from-literal=password=s3cr3t
secret/db created
$ kubectl get secret db -o jsonpath='{.data.password}'
czNjcjN0
$ kubectl get secret db -o jsonpath='{.data.password}' | base64 -d
s3cr3t
```

**Base64 is an encoding, not encryption.** Anyone who sees the manifest or the API response reverses it in one command. The Kubernetes docs say it plainly: base64 provides no additional confidentiality over plain text.

### Who can read a Secret

By default Secrets are stored unencrypted in etcd. The docs list who can read one ([Secrets](https://kubernetes.io/docs/concepts/configuration/secret/), [Good practices](https://kubernetes.io/docs/concepts/security/secrets-good-practices/)):

|Who|Why|
|---|---|
|Anyone with `get`, `list` or `watch` on Secrets|Reading or listing them returns the contents, so `list` is as strong as `get`|
|Anyone who can create a pod in the namespace|The pod can mount any Secret there and print it. This includes indirect access, such as creating a Deployment|
|Anyone with access to etcd|Without encryption at rest the data is stored in the clear|
|A privileged container on the same node|It can access all Secrets used on that node|

The second row is the one that surprises people. Permission to create pods is not usually thought of as permission to read Secrets, and the doc says it is the same thing. You can apply least privilege to Secret verbs and still leak every Secret in a namespace to a team that can deploy into it. Separate namespaces limit the blast radius, and audit rules that alert on a single user reading many Secrets detect abuse. RBAC itself is lesson 20.

### Encryption at rest

Encryption at rest protects the copy in etcd: its disk and its backups. It is not on by default. The API server enables it with `--encryption-provider-config`, pointing at an `EncryptionConfiguration`, and the doc says the `identity` provider, which writes data as is, is the default ([Encrypting Confidential Data at Rest](https://kubernetes.io/docs/tasks/administer-cluster/encrypt-data/)). The providers differ in where the key lives:

|Provider|Notes from the doc|
|---|---|
|`aescbc`, `secretbox`|The key sits in the configuration file on the control plane host. `aescbc` is not recommended because CBC is vulnerable to padding oracle attacks|
|`kms` v2|Envelope encryption: a data key encrypts the resource and a key held in an external key management service encrypts the data key. v2 is stable from v1.29|

A locally stored key protects against an etcd compromise but not a compromise of the control plane host, which holds the key. With KMS an attacker needs both etcd and the key service. To check it worked, read the stored value with `etcdctl` and look for a prefix such as `k8s:enc:aescbc:v1:`. Existing Secrets stay in the clear until they are rewritten, so the doc's fix is to replace them all: `kubectl get secrets --all-namespaces -o json | kubectl replace -f -`.

Encryption at rest does not change what the API returns. An authorised user still gets the value, because the API server decrypts it before answering. It addresses the etcd row of the table above and nothing else. On a managed cluster, whether and how this is on is the provider's setting, so read their documentation.

### Environment or file

|Exposure|Consequence|
|---|---|
|Environment variable|Fixed at container start, so rotating needs a restart (lesson 11). Variables are inherited by child processes and often show up in debug output and crash reports. That last part is a judgment, not a documented fact|
|File in a volume|Kept in a `tmpfs` on the node and not written to its disk. Permissions are set with `defaultMode`, and a mounted Secret is updated eventually, unless it is a `subPath` mount|

Prefer files when you can. In both cases the application must not log the value. If a pod has several containers and only one needs the Secret, mount or reference it in that container only.

### Keeping secrets out of Git

A Secret manifest holds base64. Checked into a repository it is a plain-text secret for everyone who can read the repository, and removing it later does not unleak it. There are three approaches, with different costs:

|Approach|How it works|Cost|
|---|---|---|
|External store, mounted|The Secrets Store CSI Driver lets the kubelet fetch from an external store and mount the value into authorised pods ([Good practices](https://kubernetes.io/docs/concepts/security/secrets-good-practices/))|A store to run and trust, and a driver on every node|
|External store, synced|An operator such as the External Secrets Operator reads the external store and creates ordinary Secrets in the cluster|Same store, but the Secret then exists in etcd like any other|
|Encrypted in Git|Sealed Secrets: a `SealedSecret` is safe to commit, and only the controller in the target cluster can decrypt it ([Sealed Secrets](https://github.com/bitnami/sealed-secrets)). SOPS encrypts files so they can be committed|The decryption key must be backed up, and rotating a value means committing a new encrypted file|

None of these remove the problems in the first table. The decrypted Secret still ends up in the cluster for anyone who can create a pod to read.

## Practice

1. ▢ What does base64 give you for a Secret?

    - a) A format that stores binary data as text
    - b) A cipher that blocks a reader of the API
    - c) A hash that proves the data was not edited
    - d) A signature that proves who wrote the value

<details markdown="1"><summary>Check</summary>

**a)** Base64 turns bytes into text so binary values fit in YAML and JSON. (b) is the common mistake: anyone can reverse it, so it hides nothing. (c) a hash cannot be reversed and base64 can, and neither detects edits here. (d) base64 has no key and identifies nobody.

</details>

2. ▢ Predict, then run. A service account may create pods and read their logs but may not read Secrets. What does each step print?

    ```console
    $ kubectl create secret generic db --from-literal=password=s3cr3t
    $ kubectl create serviceaccount builder
    $ kubectl create role pod-runner --verb=create,get --resource=pods,pods/log
    $ kubectl create rolebinding builder-pods --role=pod-runner --serviceaccount=default:builder
    $ kubectl auth can-i get secrets --as=system:serviceaccount:default:builder
    $ kubectl apply --as=system:serviceaccount:default:builder -f - <<'EOF'
    apiVersion: v1
    kind: Pod
    metadata:
      name: peek
    spec:
      restartPolicy: Never
      containers:
        - name: c
          image: busybox:1.36
          command: ["cat", "/etc/db/password"]
          volumeMounts:
            - name: db
              mountPath: /etc/db
      volumes:
        - name: db
          secret:
            secretName: db
    EOF
    $ kubectl wait --for=jsonpath='{.status.phase}'=Succeeded pod/peek
    $ kubectl logs peek --as=system:serviceaccount:default:builder
    ```

<details markdown="1"><summary>Hint</summary>

`kubectl auth can-i` evaluates one permission, `get` on Secrets. The pod mounts the Secret through the kubelet, and the question is whether creating the pod needs a permission on the Secret.

</details>

<details markdown="1"><summary>Check</summary>

`kubectl auth can-i get secrets` prints `no`. The pod is created anyway, runs `cat`, and the last command prints `s3cr3t`. Mounting a Secret needs no permission on the Secret for the person who creates the pod, so the service account that "cannot read Secrets" just read one. The same holds for a Deployment, a Job or any other object that carries a pod template. Clean up with `kubectl delete pod peek`.

</details>

3. ▢ In namespace `prod` there is a Secret `db`. Which of these subjects can learn its value: A has `get` on `secrets`, B has `create` on `deployments` only, C has `list` on `secrets`, D has `get` on `pods` only?

<details markdown="1"><summary>Check</summary>

A, B and C. A reads it directly. C can list Secrets, and a list returns their contents. B can create a Deployment whose pods mount the Secret and print it. D can read pod objects but not Secret data, and pod specs only name a Secret, so D cannot learn the value without more permissions such as `pods/exec` into a pod that already holds it.

</details>

4. ▢ After enabling `aescbc` encryption for Secrets, an admin runs `kubectl get secret db -o yaml` and still sees base64 values. They conclude encryption is not working. Are they right, and how would they check?

<details markdown="1"><summary>Check</summary>

No. The API server decrypts on read, so authorised clients always get the base64 value back. The check is on the stored copy: read the key from etcd with `etcdctl` and confirm the value starts with `k8s:enc:aescbc:v1:` followed by the key name. Secrets created before the change are still stored in the clear until they are rewritten, for example with `kubectl get secrets --all-namespaces -o json | kubectl replace -f -`.

</details>

5. ▢ A teammate committed `secret.yaml` with a base64 database password to a repository, then removed it in the next commit. Is the problem solved? What do you do?

<details markdown="1"><summary>Hint</summary>

Think about everyone who has already cloned the repository, or can read its history.

</details>

<details markdown="1"><summary>Check</summary>

No. The value stays in the history and in every clone, and base64 hides nothing. Treat the password as leaked: rotate it at the database first, update the Secret in the cluster, and only then clean up the repository. After that, change how Secrets reach the cluster, with an external store or encrypted files in Git, so the plain value is never in a manifest again.

</details>

6. ▢ A team of ten runs on one cluster and keeps its manifests in Git. They want database credentials delivered to pods without plain-text secrets in the repository. Pick an approach from the table and name what it costs and what it still leaves open.

<details markdown="1"><summary>Check</summary>

Either answer is defensible if the cost is named. Sealed Secrets or SOPS keeps the workflow in Git, and costs a decryption key that must be backed up and a new commit per rotation. An external store with the CSI driver keeps values out of Git, and costs a store to run and a driver on each node. In both cases the value reaches the pod, so anyone who can create pods in that namespace can still read it. The remaining controls are RBAC on pod creation, separate namespaces, and encryption at rest for etcd.

</details>

## Real-world reps

- [ ] Run Practice item 2 on a kind cluster and read the logs for yourself. Then run `kubectl auth can-i --list --as=system:serviceaccount:default:builder` and find the line that allowed it.
- [ ] In a cluster you have access to, run `kubectl auth can-i list secrets --all-namespaces` and `kubectl auth can-i create pods --all-namespaces`. For each "yes", write down whether you intended that person or role to be able to read every Secret.
- [ ] Tomorrow: without notes, say why base64 is not protection, name the four ways someone can read a Secret by default, say what encryption at rest protects and what it does not, and name two ways to keep secret values out of Git.

## Going further

- [Configuration](../reference/configuration.md)
- [Docs: "Secrets", Kubernetes](https://kubernetes.io/docs/concepts/configuration/secret/)
- [Docs: "Good practices for Kubernetes Secrets", Kubernetes](https://kubernetes.io/docs/concepts/security/secrets-good-practices/)
- [Docs: "Encrypting Confidential Data at Rest", Kubernetes](https://kubernetes.io/docs/tasks/administer-cluster/encrypt-data/)
- [Docs: "Sealed Secrets", Bitnami project README](https://github.com/bitnami/sealed-secrets)
- [Resources](../RESOURCES.md)

---

Not landing? Reread the primary source at the top, since this lesson compresses it and compression is where understanding leaks. Check the [glossary](../GLOSSARY.md) for any term that felt slippery.

If the lesson itself is unclear rather than the material, that is a defect: [open an issue](https://github.com/TokenCemetery/teach/issues).
