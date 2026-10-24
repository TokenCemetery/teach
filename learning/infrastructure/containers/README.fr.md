---
title: Conteneurs
description: "Empaqueter un service sous forme d'image de conteneur et la maîtriser : primitives du noyau, Dockerfiles, exécution, sécurisation et débogage d'un conteneur"
type: topic
---

# Apprentissage : les conteneurs

Empaqueter n'importe quel service sous forme d'image de conteneur et maîtriser ce qui lui arrive sur un hôte : savoir ce que fait le noyau quand un conteneur tourne, écrire un Dockerfile qui construit une image petite et reproductible, l'exécuter pour qu'elle s'arrête proprement et reste dans ses limites, la durcir, et la déboguer quand elle refuse de démarrer. Terminer capable de relire le Dockerfile et l'image de quelqu'un d'autre en nommant ce que coûte chaque choix.

**Dernière leçon :** [24. Quand la réponse habituelle est fausse](lessons/0024-when-the-usual-answer-is-wrong.md)

## Objectif

- Expliquer ce qu'est un conteneur en termes de noyau (namespaces, cgroups et système de fichiers racine en couches) et en quoi cela diffère d'une machine virtuelle.
- Lire une image : son manifeste, sa configuration et ses couches, la différence entre un tag et un digest, et récupérer exactement l'image qui a été testée.
- Écrire un Dockerfile qui construit une image petite, favorable au cache et reproductible, à l'aide d'un build multi-stage.
- Exécuter un conteneur qui s'arrête proprement sur un signal, signale son état de santé, et reste dans des limites de mémoire et de CPU que respecte le runtime qu'il contient.
- Relier des conteneurs sur un même hôte : réseau, ports publiés, volumes pour l'état, et Compose pour le développement local.
- Durcir une image : un utilisateur non root, le moins de privilèges possible, une base minimale, un scan de vulnérabilités trié, des secrets tenus hors des couches, et une signature et une provenance à vérifier.
- Déboguer un conteneur qui ne démarre pas ou se comporte mal, de son code de sortie jusqu'à l'intérieur de ses namespaces, y compris un conteneur sans shell.
- Relire le Dockerfile et l'image de quelqu'un d'autre, déployer un changement d'image de base à travers les services qui en dépendent, et dire quand la réponse habituelle est la mauvaise.

## Contraintes

- Suppose d'être à l'aise en ligne de commande Linux et d'avoir déjà construit et exécuté un service dans un langage quelconque. Aucune connaissance préalable des conteneurs.
- Utilise la CLI Docker avec BuildKit, parce que c'est ce qu'utilisent la plupart des documentations et la plupart des équipes. Lorsqu'un comportement relève des spécifications OCI plutôt que de Docker, la leçon le précise, et les mêmes commandes fonctionnent pour l'essentiel avec Podman.
- Les exercices de l'étape 1 nécessitent un shell Linux avec les droits root, par exemple une machine Linux ou une machine virtuelle. Sur un ordinateur portable avec Docker Desktop, les conteneurs eux-mêmes tournent dans une machine virtuelle Linux gérée par Docker Desktop.

## Hors périmètre

- La construction de l'artefact exécutable pour un langage donné. Les parcours de langages s'en chargent et ce parcours place leur résultat dans une image : [Go : commandes de la toolchain](../../programming/golang/reference/toolchain-commands.md) pour les binaires statiques, [Java : tests et build](../../programming/java/reference/testing-and-build.md) et [Le système de modules](../../programming/java/reference/the-module-system.md) pour les artefacts exécutables et `jlink`, [C# : livrer le service](../../programming/csharp/reference/shipping-the-service.md), et [Python : projet et packaging](../../programming/python/reference/project-and-packaging.md) pour les wheels.
- L'orchestration de conteneurs sur un cluster : ordonnancement, services, rollouts, probes en tant que fonctionnalité du cluster. C'est le rôle du [parcours Kubernetes](../kubernetes/README.md). Ce parcours s'arrête à un conteneur, ou à une poignée, sur un seul hôte.
- La construction et la publication d'images dans un pipeline. C'est le rôle du [parcours CI/CD](../ci-cd/README.md), dont la fiche [Artefacts et versionnement](../ci-cd/reference/artifacts-and-versioning.md) couvre le tagging et la publication par digest. Ce parcours construit les images à la main pour que ce qu'un pipeline automatise soit compris d'abord.
- Les conteneurs Windows, et l'écriture d'un runtime de conteneurs.

## Le fil conducteur

Huit étapes, de ce qu'est un conteneur jusqu'au jugement nécessaire pour relire l'image de quelqu'un d'autre. Une étape comprend plusieurs leçons et les frontières sont souples ; ce qui termine une étape, c'est la capacité acquise, pas le nombre de leçons.

| Étape | Leçons | Contenu | Terminée quand |
|---|---|---|---|
| 1. Ce qu'est un conteneur | 0001 à 0003 | Un conteneur comme processus, namespaces, cgroups, la différence avec une machine virtuelle | Vous savez construire l'isolation d'un conteneur à la main et dire ce que chaque pièce cache ou limite |
| 2. Images | 0004 à 0006 | Manifeste, configuration et couches, overlayfs, la pile de runtime et le cycle de vie, registres, tags et digests | Vous savez lire une image et récupérer exactement celle qui a été testée |
| 3. Construire des images | 0007 à 0010 | Instructions du Dockerfile et contexte de build, cache de build, builds multi-stage et images de base, reproductibilité | Vous savez écrire un Dockerfile qui construit une image petite, favorable au cache et reproductible |
| 4. Exécuter un conteneur | 0011 à 0013 | PID 1 et signaux, health checks et politiques de redémarrage, limites de mémoire et de CPU | Vous savez exécuter un conteneur qui s'arrête proprement, signale son état de santé et respecte ses limites |
| 5. Réseau, stockage et Compose | 0014 à 0016 | Réseaux bridge et ports publiés, volumes et bind mounts, Compose pour le développement local | Vous savez faire tourner ensemble un service et ses dépendances sur un hôte, avec un état qui survit |
| 6. Sécurité | 0017 à 0019 | Non-root, capabilities et privilèges, bases minimales et scan, secrets de build, signature et provenance | Vous savez durcir une image et vérifier d'où elle vient |
| 7. Débogage | 0020 à 0021 | Codes de sortie, logs et inspect, remplacement de l'entrypoint, entrée dans les namespaces d'un conteneur | Vous savez trouver pourquoi un conteneur ne démarre pas ou se comporte mal, même sans shell |
| 8. Jugement | 0022 à 0024 | Relire un Dockerfile, modifier une image de base dont d'autres dépendent, quand la réponse habituelle est fausse, trancher à partir de la spécification | On vous fait confiance pour trancher sur une image et l'expliquer à quelqu'un d'autre |

## Leçons

Suivez-les dans l'ordre.

| # | Leçon | Enseigne |
|---|---|---|
| [0001](lessons/0001-a-container-is-a-process.md) | Un conteneur est un processus | Un conteneur est un processus Linux ordinaire auquel le noyau montre une vue restreinte de la machine, pas une petite machine virtuelle |
| [0002](lessons/0002-namespaces.md) | Namespaces | Chaque type de namespace cache un type de ressource globale, et unshare construit la vue d'un conteneur un namespace à la fois |
| [0003](lessons/0003-cgroups.md) | Cgroups | Les control groups plafonnent et comptabilisent la mémoire, le CPU et les PID d'une arborescence de processus, et ce que fait le noyau quand une limite est atteinte |
| [0004](lessons/0004-images-and-layers.md) | Images et couches | Une image OCI est un manifeste, une configuration et une pile d'archives tar de couches qu'overlayfs fusionne en un seul système de fichiers racine |
| [0005](lessons/0005-from-image-to-running-container.md) | De l'image au conteneur en cours d'exécution | Ce que fait docker run entre l'image et le processus : la pile de runtime, la couche inscriptible et le cycle de vie |
| [0006](lessons/0006-registries-tags-and-digests.md) | Registres, tags et digests | Un tag est un nom déplaçable et un digest est le hash du contenu, alors récupérez par digest pour exécuter exactement ce qui a été testé |
| [0007](lessons/0007-your-first-dockerfile.md) | Votre premier Dockerfile | Les instructions qui construisent une image, le contexte de build, et ce que .dockerignore en tient à l'écart |
| [0008](lessons/0008-the-build-cache.md) | Le cache de build | Quand une couche en cache est réutilisée, ce qui l'invalide ainsi que toutes les couches suivantes, et comment l'ordre des instructions décide du temps de reconstruction |
| [0009](lessons/0009-multi-stage-builds.md) | Builds multi-stage | Construire dans un stage, ne copier que l'artefact dans un stage final minimal, et ce que coûte chaque choix d'image de base |
| [0010](lessons/0010-reproducible-builds.md) | Builds reproductibles | Ce qui fait différer deux builds du même Dockerfile, et épingler les bases, les paquets et les horodatages pour que ce ne soit pas le cas |
| [0011](lessons/0011-pid-1-and-signals.md) | PID 1 et signaux | Pourquoi un conteneur ignore SIGTERM quand son processus est le PID 1 ou est enveloppé dans un shell, et comment s'arrêter proprement |
| [0012](lessons/0012-health-checks-and-restart-policies.md) | Health checks et politiques de redémarrage | Signaler si le processus à l'intérieur fonctionne réellement, et décider ce que fait le runtime quand il s'arrête |
| [0013](lessons/0013-resource-limits-in-practice.md) | Les limites de ressources en pratique | Fixer des limites de mémoire et de CPU, lire un OOM kill et un throttling CPU, et vérifier que le runtime à l'intérieur voit la limite |
| [0014](lessons/0014-container-networking.md) | Le réseau des conteneurs | Les network namespaces, les paires veth et un bridge relient les conteneurs, et publier un port ajoute une règle NAT sur l'hôte |
| [0015](lessons/0015-volumes-and-state.md) | Volumes et état | Où les données survivent à un conteneur dans les volumes nommés, les bind mounts et tmpfs, et le piège de la propriété des fichiers entre l'hôte et le conteneur |
| [0016](lessons/0016-compose-for-local-development.md) | Compose pour le développement local | Décrire un service et ses dépendances dans un seul fichier Compose, et attendre qu'une dépendance soit en bonne santé plutôt que simplement démarrée |
| [0017](lessons/0017-least-privilege.md) | Moindre privilège | Exécuter en tant qu'utilisateur non root, retirer des capabilities, garder le système de fichiers racine en lecture seule, et savoir ce que livrent le mode privileged et le socket Docker |
| [0018](lessons/0018-minimal-bases-and-scanning.md) | Bases minimales et scan | Réduire ce que contient une image, lire un scan de vulnérabilités, et trier ses résultats au lieu de courir après un compte à zéro |
| [0019](lessons/0019-secrets-signing-and-provenance.md) | Secrets, signature et provenance | Tenir les secrets hors des couches, signer une image par digest, et vérifier où elle a été construite avant de l'exécuter |
| [0020](lessons/0020-a-container-that-will-not-start.md) | Un conteneur qui refuse de démarrer | Lire le code de sortie, les logs et la sortie d'inspect, puis remplacer l'entrypoint pour découvrir pourquoi il s'est arrêté |
| [0021](lessons/0021-debugging-a-running-container.md) | Déboguer un conteneur en cours d'exécution | Entrer dans un conteneur qui n'a pas de shell en rejoignant ses namespaces depuis un conteneur de débogage ou depuis l'hôte |
| [0022](lessons/0022-reviewing-a-dockerfile.md) | Relire un Dockerfile | Relire le Dockerfile et l'image de quelqu'un d'autre en nommant ce que coûte chaque choix en taille, en temps de reconstruction, en sécurité et en fiabilité |
| [0023](lessons/0023-changing-a-base-image-others-depend-on.md) | Modifier une image de base dont d'autres dépendent | Faire évoluer une image de base partagée sans casser les services construits dessus, à l'aide des tags, des digests, des reconstructions et de la dépréciation |
| [0024](lessons/0024-when-the-usual-answer-is-wrong.md) | Quand la réponse habituelle est fausse | Reconnaître quand Alpine, distroless, un digest épinglé ou même un conteneur est le mauvais choix, et trancher à partir de la spécification |

## Référence

- [Glossaire](GLOSSARY.md) : termes de référence pour ce sujet
- [Ressources](RESOURCES.md) : sources fiables, chacune annotée avec ce qu'elle couvre
- [Primitives des conteneurs](reference/container-primitives.md) : namespaces, cgroups, la structure d'une image et les tags face aux digests, issus des étapes 1 et 2
- [Dockerfile](reference/dockerfile.md) : instructions, règles de cache, schémas multi-stage, images de base et reproductibilité, issus de l'étape 3
- [Exécuter des conteneurs](reference/running-containers.md) : signaux, health checks, limites, réseau, volumes et Compose, issus des étapes 4 et 5
- [Sécurité des conteneurs](reference/container-security.md) : privilèges, bases minimales, tri des scans, secrets de build, signature et provenance, issus de l'étape 6
- [Déboguer des conteneurs](reference/debugging-containers.md) : codes de sortie, les commandes à lancer dans l'ordre, et comment entrer dans un conteneur sans shell, issus de l'étape 7
- [Liste de contrôle de relecture d'un Dockerfile](reference/dockerfile-review-checklist.md) : les questions à poser au Dockerfile et à l'image de quelqu'un d'autre, et quand la réponse habituelle est fausse, issues de l'étape 8

## Comment cela fonctionne

Chaque leçon est courte et autonome. Les corrigés sont repliés : rappelez-vous d'abord, puis ouvrez-les. Les exercices en situation réelle comptent plus que la lecture, et les espacer dans le temps est justement le but. Tout ce qui reste flou à la fin d'une leçon mérite d'être suivi jusqu'à sa source primaire avant de passer à la suite.
