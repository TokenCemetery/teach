---
title: kubectl
description: The kubectl commands by task, from inspecting objects to rollouts, debugging and permission checks
type: reference
---

# kubectl: The Commands by Task

The commands the whole track uses, grouped by what you are trying to do. [Lesson 1](../lessons/0001-what-kubernetes-is-for.md) sets up the cluster, [lesson 2](../lessons/0002-the-reconciliation-loop.md) and [lesson 3](../lessons/0003-objects-and-manifests.md) cover inspecting and applying, [lesson 4](../lessons/0004-pods.md) logs and exec, and [lessons 5](../lessons/0005-deployments-and-replicasets.md), [6](../lessons/0006-rollouts-and-rollbacks.md) and [7](../lessons/0007-jobs-cronjobs-and-daemonsets.md) scaling, rollouts and batch work. Later stages add the debug, events, top and `auth can-i` rows, which this sheet already lists so it can be consulted from every stage. Flags below were checked against the installed `kubectl` help and the kubectl reference.

## Where am I talking to

|Task|Command|
|---|---|
|Show clusters you can reach|`kubectl config get-contexts`|
|Show the current one|`kubectl config current-context`|
|Switch|`kubectl config use-context kind-lab`|
|Default namespace for this context|`kubectl config set-context --current --namespace=team-a`|
|One namespace, one command|`kubectl get pods -n team-a`|
|All namespaces|`kubectl get pods -A`|

Check the context before any command that changes something. A kind cluster named `lab` has the context `kind-lab`.

## Inspect

|Task|Command|
|---|---|
|List a kind|`kubectl get pods`, or several: `kubectl get deploy,rs,pods`|
|More columns (node, IP)|`kubectl get pods -o wide`|
|Full object, with `spec` and `status`|`kubectl get pod web-1 -o yaml`|
|One field|`kubectl get pod web-1 -o jsonpath='{.status.podIP}{"\n"}'`|
|Chosen columns|`kubectl get pods -o custom-columns=NAME:.metadata.name,NODE:.spec.nodeName`|
|Show labels|`kubectl get pods --show-labels`|
|Select by label|`kubectl get pods -l app=web,tier!=cache`|
|Select by field|`kubectl get pods --field-selector status.phase=Running`|
|Watch changes|`kubectl get pods -w`|
|Sort|`kubectl get pods --sort-by=.metadata.creationTimestamp`|
|Readable detail and recent events|`kubectl describe pod web-1`|
|Kinds the cluster serves, their group and whether namespaced|`kubectl api-resources`, `kubectl api-resources --namespaced=false`|
|Field documentation|`kubectl explain pod.spec.containers`, add `--recursive` for the tree|
|Client and server versions|`kubectl version`|

`get` shows a summary column set that differs per kind. `-o yaml` is the truth, and `describe` reads it into prose with the events attached.

## Create and change

|Task|Command|
|---|---|
|Create or update from a file|`kubectl apply -f app.yaml`|
|A directory, recursively|`kubectl apply -f manifests/ -R`|
|Kustomize overlay|`kubectl apply -k overlays/prod`|
|See what would change|`kubectl diff -f app.yaml`|
|Validate on the server, store nothing|`kubectl apply -f app.yaml --dry-run=server`|
|Server-side apply, field ownership|`kubectl apply -f app.yaml --server-side`, add `--force-conflicts` to take fields over|
|Generate a manifest|`kubectl create deployment web --image=nginx:1.27 --replicas=3 --dry-run=client -o yaml`|
|Create only, fail if it exists|`kubectl create -f app.yaml`|
|Edit a live object|`kubectl edit deployment/web`|
|Patch a field|`kubectl patch deployment web -p '{"spec":{"replicas":2}}'`|
|Change the image|`kubectl set image deployment/web nginx=nginx:1.27.1`|
|Add or change a label|`kubectl label pod web-1 tier=frontend`, add `--overwrite` to change one|
|Add an annotation|`kubectl annotate deployment/web kubernetes.io/change-cause="bump"`|
|Delete from a file|`kubectl delete -f app.yaml`|
|Delete by name or label|`kubectl delete pod web-1`, `kubectl delete pods -l app=web`|
|Keep the children|`kubectl delete deployment web --cascade=orphan`|
|Create a Job from a CronJob|`kubectl create job manual-1 --from=cronjob/tick`|
|Wait for a condition|`kubectl wait --for=condition=Ready pod/web-1 --timeout=60s`|

- `apply` prints `created`, `configured` or `unchanged`. `create` fails with `AlreadyExists`, and mixing `create` or `replace` with `apply` is not supported.
- A field in the file overwrites the live value on every apply. Leave `replicas` out of the file when an autoscaler owns it.
- `kubectl delete` removes dependents by default (`--cascade=background`).

## Rollouts

|Task|Command|
|---|---|
|Watch a rollout until done|`kubectl rollout status deployment/web`, add `--timeout=2m`|
|List revisions|`kubectl rollout history deployment/web`|
|One revision's template|`kubectl rollout history deployment/web --revision=2`|
|Roll back|`kubectl rollout undo deployment/web`, `--to-revision=2` for a specific one|
|Pause, resume|`kubectl rollout pause deployment/web`, `kubectl rollout resume deployment/web`|
|Rolling restart|`kubectl rollout restart deployment/web`|

`rollout` works on Deployments, DaemonSets and StatefulSets. `rollout status` exits non-zero when the rollout fails or exceeds its progress deadline, which is what a script should test.

## Scale

|Task|Command|
|---|---|
|Set replicas|`kubectl scale deployment/web --replicas=5`|
|Scale to zero, keep the object|`kubectl scale deployment/web --replicas=0`|
|Only if the current count matches|`kubectl scale deployment/web --current-replicas=3 --replicas=5`|
|Autoscale on CPU|`kubectl autoscale deployment web --min=2 --max=10 --cpu=80%`|

## Logs and exec

|Task|Command|
|---|---|
|Logs of a pod|`kubectl logs web-1`|
|One container of several|`kubectl logs web-1 -c sidecar`, or `--all-containers`|
|Follow|`kubectl logs web-1 -f`|
|The previous run of a restarted container|`kubectl logs web-1 --previous`|
|By label, with pod prefix|`kubectl logs -l app=web --prefix --tail=20`|
|Recent only|`kubectl logs web-1 --since=10m --timestamps`|
|Logs of a pod chosen from a Job or Deployment|`kubectl logs job/report`, `kubectl logs deploy/web`|
|Run a command in a container|`kubectl exec web-1 -c nginx -- nginx -v`|
|Interactive shell|`kubectl exec -it web-1 -- sh`|
|Copy files|`kubectl cp web-1:/tmp/out.txt ./out.txt`|
|Throwaway pod, removed on exit|`kubectl run tmp --rm -it --image=busybox:1.37 -- sh`|

A pod with several containers needs `-c`, or `kubectl` picks one and says which. Logs stay readable only while the pod exists.

## Debug, events, metrics

|Task|Command|
|---|---|
|Events for the namespace|`kubectl events`|
|Events for one object, streaming|`kubectl events --for pod/web-1 --watch`|
|Warnings only|`kubectl events --types=Warning`|
|Add a debug container to a running pod|`kubectl debug web-1 -it --image=busybox:1.37 --target=nginx`|
|Debug a copy of a pod|`kubectl debug web-1 -it --image=busybox:1.37 --copy-to=web-1-debug`|
|Change the image in a copy|`kubectl debug web-1 --copy-to=web-1-debug --set-image=*=busybox:1.37`|
|A shell on a node|`kubectl debug node/lab-worker -it --image=busybox:1.37`|
|Node or pod CPU and memory|`kubectl top node`, `kubectl top pod --containers`|

- `kubectl top` needs the Metrics Server installed and running in the cluster, and shows values tuned for autoscaling rather than exact usage.
- `kubectl debug --profile` picks the security profile of the debug container, with `general` as the default.
- The `Events` section at the bottom of `kubectl describe` is usually the first place a scheduling or image error shows.

## Permissions

|Task|Command|
|---|---|
|Can I do this|`kubectl auth can-i create pods -n team-a`|
|List everything I may do|`kubectl auth can-i --list -n team-a`|
|Check as another identity|`kubectl auth can-i list pods --as=system:serviceaccount:dev:foo -n prod`|
|A subresource|`kubectl auth can-i get pods --subresource=log`|
|Who am I|`kubectl auth whoami`|

`--as` requires the right to impersonate. `auth whoami` is marked experimental in the installed help.

## Network

|Task|Command|
|---|---|
|Forward a local port to a pod|`kubectl port-forward pod/web-1 8080:80`|
|Through a Deployment or Service|`kubectl port-forward deployment/web 8080:80`, `kubectl port-forward service/web 8080:80`|
|Listen on all local addresses|`kubectl port-forward --address 0.0.0.0 pod/web-1 8080:80`|

`port-forward` stays in the foreground. Given a Deployment or a Service it selects one pod, and the session ends when that pod terminates, so rerun it. It tests one pod and not the Service's load balancing.

## Nodes

|Task|Command|
|---|---|
|Stop new pods landing|`kubectl cordon lab-worker`|
|Evict pods for maintenance|`kubectl drain lab-worker --ignore-daemonsets`|
|Taint a node|`kubectl taint nodes lab-worker dedicated=batch:NoSchedule`, remove with a trailing `-`|

`drain` refuses to delete pods that no controller owns unless you add `--force`, and does not touch DaemonSet pods without `--ignore-daemonsets`.

## Short names

|Short|Kind|Short|Kind|
|---|---|---|---|
|`po`|pods|`cm`|configmaps|
|`deploy`|deployments|`svc`|services|
|`rs`|replicasets|`ns`|namespaces|
|`ds`|daemonsets|`no`|nodes|
|`cj`|cronjobs|`sa`|serviceaccounts|
|`sts`|statefulsets|`pvc`|persistentvolumeclaims|

`kubectl api-resources` prints the authoritative list for your cluster, including the short names.

## Sources

- [Docs: "kubectl Quick Reference", Kubernetes](https://kubernetes.io/docs/reference/kubectl/quick-reference/)
- [Docs: "kubectl reference", Kubernetes](https://kubernetes.io/docs/reference/kubectl/generated/kubectl_rollout/), starting from `kubectl rollout`
- [Docs: "kubectl debug", kubectl reference](https://kubernetes.io/docs/reference/kubectl/generated/kubectl_debug/)
- [Docs: "kubectl auth can-i", kubectl reference](https://kubernetes.io/docs/reference/kubectl/generated/kubectl_auth/kubectl_auth_can-i/)
- [Docs: "Resource metrics pipeline", Kubernetes](https://kubernetes.io/docs/tasks/debug/debug-cluster/resource-metrics-pipeline/)
