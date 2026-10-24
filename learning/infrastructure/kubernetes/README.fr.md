---
title: Kubernetes
description: "Faire tourner des services sur un cluster Kubernetes et les maîtriser : la boucle de réconciliation, les workloads, le réseau, la configuration, la fiabilité, la sécurité, le packaging et le débogage"
type: topic
---

# Apprentissage : Kubernetes

Faire tourner n'importe quel service conteneurisé sur un cluster Kubernetes et maîtriser ce qui lui arrive : le décrire dans des manifestes que le cluster réconcilie, l'exposer, le configurer, le garder en bonne santé à travers les rollouts, les pannes de nœuds et la charge, le verrouiller, l'empaqueter pour plusieurs environnements, et découvrir pourquoi il est cassé quand il l'est. Terminer capable de relire les manifestes de quelqu'un d'autre en nommant ce que coûte chaque choix, de mettre à niveau ce dont d'autres équipes dépendent sans les casser, et de dire quand un service n'a pas du tout besoin de Kubernetes.

**Dernière leçon :** [28. Quand Kubernetes est la mauvaise réponse](lessons/0028-when-kubernetes-is-the-wrong-answer.md)

## Objectif

- Expliquer le modèle déclaratif : l'état désiré stocké via l'API server, les contrôleurs qui réconcilient le cluster vers cet état, et ce que cela signifie quand un pod est supprimé ou qu'un nœud meurt.
- Lire et écrire des manifestes : les champs que possède chaque objet, les labels et les selectors, les namespaces, et l'application des modifications avec `kubectl apply`.
- Faire tourner un service stateless avec un Deployment, déployer une nouvelle version et revenir en arrière, et exécuter des traitements batch et des agents par nœud avec des Jobs, des CronJobs et des DaemonSets.
- Exposer un service à l'intérieur du cluster avec un Service et le DNS du cluster, et à l'extérieur avec Ingress ou la Gateway API.
- Configurer un workload avec des ConfigMaps et des Secrets, et dire ce qu'un Secret protège et ne protège pas.
- Garder un workload en bonne santé : des probes qui répondent à la bonne question, une terminaison propre, et des requests et limits qui fixent sa classe de QoS.
- Faire tourner des workloads stateful sur du stockage persistant, placer les pods avec des contraintes d'ordonnancement, les faire passer à l'échelle automatiquement, et empêcher les perturbations volontaires de mettre un service à terre.
- Verrouiller un workload avec RBAC, les service accounts, les network policies et la pod security.
- Empaqueter des manifestes pour plusieurs environnements avec Kustomize ou Helm, et choisir entre les deux selon ce que chacun coûte.
- Observer un workload et déboguer celui qui est Pending, qui plante ou qui est injoignable, des événements et des logs jusqu'à un conteneur de débogage.
- Relire les manifestes de quelqu'un d'autre, mettre à niveau un cluster ou un chart partagé dont d'autres équipes dépendent, dire quand Kubernetes ou l'une de ses valeurs par défaut habituelles est la mauvaise réponse, et trancher une question contestée à partir de la référence de l'API.

## Contraintes

- Suppose le [parcours Conteneurs](../containers/README.md) ou un équivalent : construire une image, exécuter un conteneur, les signaux, les health checks et les limites sur un hôte. Aucune connaissance préalable de Kubernetes.
- Chaque exercice tourne sur un cluster local créé avec kind, qui nécessite Docker ou Podman et quelques gigaoctets de mémoire, ainsi que `kubectl`. Aucun compte cloud n'est nécessaire. Lorsque le comportement d'une leçon dépend d'un fournisseur cloud (un Service `LoadBalancer`, un autoscaler de nœuds, une storage class cloud), elle le dit et enseigne la partie que kind peut montrer.
- Utilise Kubernetes upstream et sa documentation. Les offres managées (EKS, GKE, AKS) diffèrent par leurs valeurs par défaut et leurs add-ons, et les leçons ne nomment une différence que lorsqu'elle change la réponse.

## Hors périmètre

- Construire et exécuter un conteneur. C'est le rôle du [parcours Conteneurs](../containers/README.md), dont la fiche [Exécuter des conteneurs](../containers/reference/running-containers.md) est la version sur un seul hôte de l'étape 5 de ce parcours.
- Rendre un service observable et arrêtable depuis son propre code : endpoints de santé, gestion des signaux, arrêt propre. Les parcours de langages s'en chargent, par exemple [Arrêt propre](../../programming/golang/lessons/0025-graceful-shutdown.md) pour Go et [Logging et health checks](../../programming/csharp/lessons/0039-logging-and-health-checks.md) pour C#. Ce parcours enseigne ce que le cluster fait de ces signaux.
- Le consensus et la défaillance partielle en tant que théorie. C'est le rôle de [Systèmes distribués](../../architecture/distributed-systems/README.md), dont la fiche [Consensus](../../architecture/distributed-systems/reference/consensus.md) explique ce que fait etcd en dessous. Ce parcours enseigne ce que la réconciliation et etcd signifient pour quelqu'un qui fait tourner des workloads.
- Livrer une modification au cluster depuis un pipeline, et les outils GitOps. C'est le rôle du [parcours CI/CD](../ci-cd/README.md), dont la fiche [Déploiements](../ci-cd/reference/deployments.md) couvre les stratégies de déploiement, le rollback et le choix entre un déploiement en push et GitOps.
- Installer et exploiter le control plane lui-même (sauvegardes d'etcd, rotation des certificats, construction d'un cluster à partir de zéro), écrire des contrôleurs ou des opérateurs, et les service meshes.

## Le fil conducteur

Dix étapes, de la boucle de réconciliation jusqu'au jugement nécessaire pour relire les manifestes de quelqu'un d'autre. Une étape comprend plusieurs leçons et les frontières sont souples ; ce qui termine une étape, c'est la capacité acquise, pas le nombre de leçons.

| Étape | Leçons | Contenu | Terminée quand |
|---|---|---|---|
| 1. Le modèle déclaratif | 0001 à 0003 | Cluster, control plane et nœuds, l'API server, etcd et les contrôleurs, la boucle de réconciliation, les champs des objets, labels, namespaces, `kubectl apply` | Vous savez prédire ce que fait le cluster après une modification de l'état désiré, et écrire un manifeste qu'il accepte |
| 2. Workloads | 0004 à 0007 | Pods, Deployments et ReplicaSets, rolling updates et rollbacks, Jobs, CronJobs et DaemonSets | Vous savez faire tourner un service stateless, le faire avancer et reculer de version, et choisir le contrôleur pour un travail qui n'est pas un service |
| 3. Réseau | 0008 à 0010 | Services et EndpointSlices, kube-proxy, DNS du cluster, Ingress et la Gateway API | Vous savez rendre un workload joignable à l'intérieur et à l'extérieur du cluster, et dire quel saut a échoué quand il ne l'est pas |
| 4. Configuration | 0011 à 0012 | ConfigMaps comme environnement et comme fichiers, Secrets, chiffrement au repos, tenir les secrets hors de Git | Vous savez configurer un workload par environnement et dire ce qui protège ses secrets |
| 5. Fonctionner de façon fiable | 0013 à 0015 | Probes de liveness, de readiness et de startup, terminaison et la course avec les endpoints, requests, limits et classes de QoS | Vous savez faire tourner un workload qui ne reçoit du trafic que lorsqu'il est prêt, se vide proprement et n'est pas le premier évincé |
| 6. État, ordonnancement et passage à l'échelle | 0016 à 0019 | PersistentVolumes et claims, StatefulSets, affinité, taints et topology spread, autoscaling, PodDisruptionBudgets | Vous savez faire tourner un workload stateful, placer les pods délibérément, et passer à l'échelle et vider un nœud sans interruption de service |
| 7. Sécurité | 0020 à 0021 | RBAC, service accounts, NetworkPolicy, security contexts, Pod Security Standards | Vous savez accorder le moindre privilège aux personnes et aux pods, et restreindre ce qu'un pod peut atteindre et faire |
| 8. Packaging | 0022 à 0023 | Bases et overlays Kustomize, charts Helm, values et releases, le choix entre les deux | Vous savez livrer un même ensemble de manifestes à plusieurs environnements et défendre l'outil choisi |
| 9. Observabilité et débogage | 0024 à 0025 | Métriques de ressources, événements, logs, kube-state-metrics, les états d'échec et les commandes qui les expliquent, conteneurs de débogage | Vous savez découvrir pourquoi un workload est Pending, plante ou est injoignable |
| 10. Jugement | 0026 à 0028 | Relire des manifestes, mettre à niveau un cluster ou un chart partagé dont d'autres dépendent, quand Kubernetes ou une valeur par défaut est le mauvais choix, trancher à partir de la référence de l'API | On vous fait confiance pour trancher sur un workload et l'expliquer à quelqu'un d'autre |

## Leçons

Suivez-les dans l'ordre.

| # | Leçon | Enseigne |
|---|---|---|
| [0001](lessons/0001-what-kubernetes-is-for.md) | À quoi sert Kubernetes | Un cluster transforme de nombreuses machines en un seul endroit où faire tourner des conteneurs, et le control plane et les nœuds se partagent le travail |
| [0002](lessons/0002-the-reconciliation-loop.md) | La boucle de réconciliation | Vous déclarez l'état désiré via l'API server, et les contrôleurs surveillent et agissent sans relâche jusqu'à ce que le cluster y corresponde |
| [0003](lessons/0003-objects-and-manifests.md) | Objets et manifestes | Chaque objet a apiVersion, kind, metadata, spec et status, et les labels, les selectors, les namespaces et kubectl apply opèrent tous sur ces champs |
| [0004](lessons/0004-pods.md) | Pods | Un pod est l'unité que le cluster ordonnance, des conteneurs qui partagent un network namespace et des volumes, et pourquoi vous en créez rarement un vous-même |
| [0005](lessons/0005-deployments-and-replicasets.md) | Deployments et ReplicaSets | Un Deployment possède des ReplicaSets qui possèdent des pods, si bien qu'un pod supprimé est remplacé et qu'un template modifié devient un nouveau ReplicaSet |
| [0006](lessons/0006-rollouts-and-rollbacks.md) | Rollouts et rollbacks | Déployer une nouvelle version avec maxSurge et maxUnavailable, la surveiller, la mettre en pause, et revenir à une révision connue |
| [0007](lessons/0007-jobs-cronjobs-and-daemonsets.md) | Jobs, CronJobs et DaemonSets | Exécuter un travail qui se termine, un travail planifié et un pod par nœud, et le mode de défaillance propre à chacun |
| [0008](lessons/0008-services.md) | Services | Un Service donne à un ensemble changeant de pods une IP virtuelle stable unique, et les EndpointSlices et kube-proxy routent vers ceux qui sont prêts |
| [0009](lessons/0009-cluster-dns.md) | DNS du cluster | Comment un pod trouve un Service par son nom, ce que le chemin de recherche et ndots font à chaque résolution, et ce que renvoie un Service headless |
| [0010](lessons/0010-ingress-and-the-gateway-api.md) | Ingress et la Gateway API | Faire entrer le trafic HTTP extérieur dans le cluster via un contrôleur, et pourquoi la Gateway API répartit le travail par rôle |
| [0011](lessons/0011-configmaps.md) | ConfigMaps | Injecter la configuration sous forme de variables d'environnement ou de fichiers, et savoir laquelle des deux voit une modification sans redémarrage |
| [0012](lessons/0012-secrets.md) | Secrets | Un Secret est du base64, pas du chiffrement, donc ce qui le protège, ce sont RBAC, le chiffrement au repos et le fait de le tenir hors de Git |
| [0013](lessons/0013-probes.md) | Probes | Les probes de liveness, de readiness et de startup répondent à des questions différentes, et une mauvaise probe de liveness provoque la panne qu'elle devait empêcher |
| [0014](lessons/0014-pod-termination.md) | Terminaison d'un pod | Ce qui se passe entre une suppression et SIGKILL, et pourquoi un pod reçoit encore du trafic après SIGTERM si vous ne l'avez pas prévu |
| [0015](lessons/0015-requests-limits-and-qos.md) | Requests, limits et QoS | Les requests pilotent l'ordonnancement et les limits pilotent l'application des limites, et ensemble elles fixent la classe de QoS qui décide qui est évincé en premier |
| [0016](lessons/0016-persistent-storage.md) | Stockage persistant | Réclamer du stockage avec un PersistentVolumeClaim, laisser une StorageClass le provisionner, et savoir ce que promettent les modes d'accès et les politiques de récupération |
| [0017](lessons/0017-statefulsets.md) | StatefulSets | Des noms stables, un démarrage ordonné et un volume par réplique, et pourquoi un StatefulSet seul ne rend pas sûre l'exécution d'une base de données |
| [0018](lessons/0018-scheduling.md) | Ordonnancement | Orienter les pods avec les node selectors, l'affinité, le topology spread, les taints et les tolerations, et lire pourquoi un pod reste Pending |
| [0019](lessons/0019-autoscaling-and-disruptions.md) | Autoscaling et perturbations | Faire passer à l'échelle les pods avec le HorizontalPodAutoscaler et les nœuds avec un autoscaler de nœuds, et empêcher qu'un drain n'en arrête trop à la fois grâce à un PodDisruptionBudget |
| [0020](lessons/0020-rbac-and-service-accounts.md) | RBAC et service accounts | Accorder à une personne ou à un pod exactement les verbes dont il a besoin avec des Roles et des bindings, et le vérifier avec kubectl auth can-i |
| [0021](lessons/0021-network-policy-and-pod-security.md) | Network policy et pod security | Refuser par défaut le trafic entre pods, puis restreindre ce qu'un pod peut faire sur son nœud avec les security contexts et les Pod Security Standards |
| [0022](lessons/0022-kustomize.md) | Kustomize | Garder une base unique de manifestes simples et la patcher par environnement avec des overlays, sans langage de templates |
| [0023](lessons/0023-helm-against-kustomize.md) | Helm face à Kustomize | Installer et écrire un chart Helm, et choisir entre un chart et un overlay Kustomize selon ce que chacun coûte |
| [0024](lessons/0024-observability.md) | Observabilité | Lire les métriques de ressources, les événements, les logs des conteneurs et les métriques d'état des objets, et savoir à quelle question chacun répond |
| [0025](lessons/0025-debugging-a-workload.md) | Déboguer un workload | Remonter de Pending, ImagePullBackOff, CrashLoopBackOff et OOMKilled jusqu'à la cause avec describe, les événements, les logs et kubectl debug |
| [0026](lessons/0026-reviewing-manifests.md) | Relire des manifestes | Relire les manifestes de quelqu'un d'autre en nommant ce que coûte chaque choix en disponibilité, en sécurité et en exploitabilité |
| [0027](lessons/0027-upgrading-what-others-depend-on.md) | Mettre à niveau ce dont d'autres dépendent | Faire passer un cluster ou un chart partagé au-delà d'une version d'API supprimée sans casser les équipes dont les workloads en dépendent |
| [0028](lessons/0028-when-kubernetes-is-the-wrong-answer.md) | Quand Kubernetes est la mauvaise réponse | Dire quand un service n'a pas besoin de Kubernetes ou qu'une valeur par défaut habituelle est fausse, et trancher une question contestée à partir de la référence de l'API |

## Référence

- [Glossaire](GLOSSARY.md) : termes de référence pour ce sujet
- [Ressources](RESOURCES.md) : sources fiables, chacune annotée avec ce qu'elle couvre
- [kubectl](reference/kubectl.md) : les commandes par tâche, de l'inspection des objets aux rollouts, au débogage et aux vérifications de permissions, sur l'ensemble du fil conducteur
- [Workloads](reference/workloads.md) : champs des objets, labels et selectors, pods, Deployments, rollouts, Jobs, CronJobs et DaemonSets, issus des étapes 1 et 2
- [Réseau](reference/networking.md) : types de Service, EndpointSlices, noms DNS et ndots, ressources Ingress et Gateway API, issus de l'étape 3
- [Configuration](reference/configuration.md) : ConfigMaps et Secrets comme environnement et comme fichiers, comportement lors des mises à jour, et ce qui protège un Secret, issus de l'étape 4
- [Fonctionner de façon fiable](reference/running-reliably.md) : les trois probes, la séquence de terminaison, requests, limits et classes de QoS, issus de l'étape 5
- [État, ordonnancement et passage à l'échelle](reference/state-scheduling-and-scale.md) : stockage, StatefulSets, contraintes de placement, autoscalers et disruption budgets, issus de l'étape 6
- [Sécurité du cluster](reference/cluster-security.md) : objets RBAC, tokens de service account, patterns de NetworkPolicy et Pod Security Standards, issus de l'étape 7
- [Packaging](reference/packaging.md) : Kustomize et Helm côte à côte, et quand chacun convient, issus de l'étape 8
- [Déboguer des workloads](reference/debugging-workloads.md) : chaque état d'échec, ce qui le cause et les commandes à lancer dans l'ordre, issus de l'étape 9
- [Liste de contrôle de relecture des manifestes](reference/manifest-review-checklist.md) : les questions à poser aux manifestes de quelqu'un d'autre, et quand la réponse habituelle est fausse, issues de l'étape 10

## Comment cela fonctionne

Chaque leçon est courte et autonome. Les corrigés sont repliés : rappelez-vous d'abord, puis ouvrez-les. Les exercices en situation réelle comptent plus que la lecture, et les espacer dans le temps est justement le but. Tout ce qui reste flou à la fin d'une leçon mérite d'être suivi jusqu'à sa source primaire avant de passer à la suite.
