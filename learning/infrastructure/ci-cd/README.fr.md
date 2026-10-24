---
title: CI/CD
description: "Construire, tester et livrer chaque modification via un pipeline, et le maîtriser : workflows, feedback rapide, artefacts, secrets, déploiements, rollback et sécurité de la chaîne d'approvisionnement"
type: topic
---

# Apprentissage : la CI/CD

Mener n'importe quel service d'une modification fusionnée jusqu'à la production au moyen d'un pipeline que vous maîtrisez : prouver en quelques minutes que chaque modification compile et passe ses tests, produire un artefact versionné unique et promouvoir ce même artefact d'un environnement à l'autre, donner au pipeline les accès dont il a besoin sans clés de longue durée, déployer avec une stratégie qui limite les dégâts d'une mauvaise release, et revenir en arrière quand l'une d'elles passe malgré tout. Terminer capable de relire le pipeline de quelqu'un d'autre en nommant ce qui va d'abord échouer, ralentir ou fuiter, de modifier un workflow dont dépendent d'autres équipes sans casser leurs merges, et de dire quand la réponse habituelle en matière de livraison est la mauvaise.

**Dernière leçon :** [30. Quand la réponse habituelle est fausse](lessons/0030-when-the-usual-answer-is-wrong.md)

## Objectif

- Expliquer ce que promettent respectivement l'intégration continue, la livraison continue et le déploiement continu, et ce qu'une équipe doit pratiquer pour que la promesse tienne.
- Écrire un pipeline sous forme de code : déclencheurs et événements, jobs, steps et runners, actions, expressions, contextes et outputs.
- Exécuter des étapes de build et de test qui échouent d'abord sur le problème le moins coûteux, sur une matrice, avec du cache, sans se fier à un test instable, et assez vite pour que les gens attendent le résultat.
- Produire des artefacts dont la version est traçable jusqu'à un commit, les construire une seule fois, et construire, publier et référencer une image de conteneur par digest.
- Donner à un pipeline des secrets et un accès au cloud avec le moindre privilège : permissions du `GITHUB_TOKEN` restreintes, OIDC au lieu de clés de longue durée, et aucun chemin par lequel une entrée non fiable pourrait atteindre l'un ou l'autre.
- Conditionner les déploiements par des environnements et des approbations, et promouvoir un même artefact de la préproduction à la production.
- Déployer avec les stratégies rolling, blue-green et canary, faire un rollback ou un roll forward, ordonner les migrations de base de données autour d'un déploiement, et choisir entre un déploiement en push et GitOps.
- Sécuriser la chaîne d'approvisionnement : épingler ce que le pipeline exécute, et produire et vérifier la provenance et les SBOM.
- Faire passer les pipelines à l'échelle sur plusieurs dépôts et monorepos avec des workflows réutilisables, des actions composites et des filtres de chemins, et déboguer un pipeline qui n'échoue que sur le runner.
- Relire le pipeline de quelqu'un d'autre, modifier un workflow partagé ou un check obligatoire sans casser les équipes qui en dépendent, dire quand la réponse habituelle est fausse, et trancher un comportement contesté à partir de la référence de syntaxe des workflows.

## Contraintes

- Suppose d'être à l'aise avec Git, un shell, et le build et les tests d'un projet dans un langage. Aucune connaissance préalable de la CI/CD. La leçon 13 suppose le [parcours Conteneurs](../containers/README.md) ou un équivalent, et les leçons 19 et 22 supposent les bases du [parcours Kubernetes](../kubernetes/README.md).
- Enseigne les tâches qu'accomplit un pipeline et les accomplit avec GitHub Actions, de la même façon que `programming/java` enseigne le cycle de vie du build avec Maven. Jenkins et GitLab CI n'apparaissent que là où leur modèle diffère réellement.
- Chaque exercice tourne dans un dépôt public jetable sur un compte GitHub gratuit, où les runners hébergés par GitHub ne coûtent rien. Les exercices de déploiement déploient vers un cluster kind créé à l'intérieur du job, si bien qu'aucun compte cloud n'est nécessaire. Lorsqu'une leçon dépend d'un fournisseur cloud, comme pour une politique de confiance OIDC, elle montre la partie que GitHub seul peut montrer et marque le reste comme optionnel.

## Hors périmètre

- Le build et les tests du code d'un langage donné. Les parcours de langages prennent en charge les commandes qu'exécute une step de pipeline, par exemple [Java : tests et build](../../programming/java/reference/testing-and-build.md), [Go : commandes de la toolchain](../../programming/golang/reference/toolchain-commands.md), [Python : projet et packaging](../../programming/python/reference/project-and-packaging.md) et [C# : tests et build](../../programming/csharp/reference/testing-and-build.md). Ce parcours exécute ces steps dans un pipeline.
- L'écriture d'un Dockerfile et la construction d'une image à la main. C'est le rôle du [parcours Conteneurs](../containers/README.md), dont la fiche [Dockerfile](../containers/reference/dockerfile.md) est ce que la leçon 13 construit dans un pipeline.
- L'exécution de la charge de travail une fois livrée : probes, rollouts en tant que fonctionnalité du cluster, packaging des manifestes. C'est le rôle du [parcours Kubernetes](../kubernetes/README.md), dont la fiche [Packaging](../kubernetes/reference/packaging.md) couvre les manifestes qu'applique un job de déploiement. Ce parcours y livre la modification, et n'enseigne GitOps que dans la mesure nécessaire pour le choisir.
- L'écriture d'une migration qui ne verrouille pas une table. C'est le rôle de [SQL](../../programming/sql/README.md), dont la fiche [Exploitation](../../programming/sql/reference/operating.md) contient la table de sûreté des migrations. Ce parcours ordonne les migrations au sein d'un déploiement.
- L'installation et l'administration d'un serveur de CI, l'écriture d'actions JavaScript ou d'actions conteneur Docker, et la publication sur les stores d'applications mobiles.

## Le fil conducteur

Dix étapes, de ce que promettent la CI et la CD jusqu'au jugement nécessaire pour relire le pipeline de quelqu'un d'autre. Une étape comprend plusieurs leçons et les frontières sont souples ; ce qui termine une étape, c'est la capacité acquise, pas le nombre de leçons.

| Étape | Leçons | Contenu | Terminée quand |
|---|---|---|---|
| 1. À quoi servent la CI et la CD | 0001 à 0002 | Intégration, livraison et déploiement comme promesses, travail trunk-based, pipelines sous forme de code, les équivalents Jenkins et GitLab | Vous savez dire ce que garantit un pipeline et lire n'importe quel fichier de workflow comme du code |
| 2. Anatomie d'un workflow | 0003 à 0005 | Événements et filtres, jobs, steps, runners, `needs`, actions, expressions, contextes et outputs | Vous savez écrire un workflow qui se déclenche quand prévu et transmet des données entre jobs |
| 3. Un feedback rapide et fiable | 0006 à 0010 | Ordre des étapes, conteneurs de service, matrices, cache, tests instables, chemin critique, concurrence et timeouts | Vous savez faire tourner un pipeline auquel les gens se fient et dont ils attendent le résultat |
| 4. Artefacts et versionnement | 0011 à 0013 | Artefacts contre caches, identité d'un build, construire une seule fois, construire et publier une image par digest | Vous savez produire un artefact traçable unique et transmettre ce même artefact à chaque étape ultérieure |
| 5. Secrets et confiance | 0014 à 0016 | Secrets, masquage, permissions du `GITHUB_TOKEN`, fédération OIDC, injection de script, `pull_request_target` | Vous savez donner à un pipeline uniquement les accès dont il a besoin et tenir les entrées non fiables à distance |
| 6. Environnements et promotion | 0017 à 0018 | Environnements, règles de protection, secrets d'environnement, promotion d'un artefact unique avec une configuration par environnement | Vous savez conditionner un déploiement en production et promouvoir ce que la préproduction a testé |
| 7. Déployer et revenir en arrière | 0019 à 0022 | Recreate, rolling, blue-green et canary, rollback, roll forward et feature flags, migrations expand and contract, déploiements en push et GitOps | Vous savez déployer avec une stratégie qui limite les dégâts et annuler une mauvaise release |
| 8. Chaîne d'approvisionnement | 0023 à 0024 | Épinglage des actions et des dépendances, Dependabot, provenance SLSA, attestations d'artefacts, SBOM | Vous savez dire ce que le pipeline a exécuté et prouver d'où vient un artefact |
| 9. Les pipelines à l'échelle | 0025 à 0027 | Workflows réutilisables, actions composites, filtres de chemins et checks obligatoires dans les monorepos, logs de débogage, différences entre runners | Vous savez partager la logique de pipeline entre équipes et trouver pourquoi une exécution a échoué |
| 10. Jugement | 0028 à 0030 | Relire un pipeline, modifier un workflow partagé ou un check obligatoire, quand la réponse habituelle est fausse, trancher à partir de la référence de syntaxe des workflows | On vous fait confiance pour trancher sur un pipeline et l'expliquer à quelqu'un d'autre |

## Leçons

Suivez-les dans l'ordre.

| # | Leçon | Enseigne |
|---|---|---|
| [0001](lessons/0001-what-ci-and-cd-promise.md) | Ce que promettent la CI et la CD | L'intégration continue garde chaque modification fusionnée et prouvée sur main, la livraison continue garde main publiable, et le déploiement continu livre chaque modification qui passe |
| [0002](lessons/0002-pipelines-as-code.md) | Les pipelines sous forme de code | Un fichier de workflow dans le dépôt est versionné, relu et exécuté comme le code qu'il construit, et Jenkins et GitLab expriment la même idée |
| [0003](lessons/0003-triggers-and-events.md) | Déclencheurs et événements | Lancer un workflow sur un push, une pull request, une planification ou à la main, le filtrer par branche et par chemin, et savoir sur quel commit s'exécute chaque événement |
| [0004](lessons/0004-jobs-steps-and-runners.md) | Jobs, steps et runners | Les jobs s'exécutent en parallèle sur des runners neufs sauf si needs les ordonne, les steps partagent un même espace de travail, et les runners hébergés et auto-hébergés échangent du coût contre du contrôle |
| [0005](lessons/0005-actions-expressions-and-outputs.md) | Actions, expressions et outputs | Réutiliser une action avec uses, décider avec if et des expressions sur les contextes, et transmettre des valeurs entre steps et entre jobs au moyen des outputs |
| [0006](lessons/0006-build-and-test-stages.md) | Étapes de build et de test | Ordonner les étapes de lint, de build, de tests unitaires et de tests d'intégration pour que l'échec le moins coûteux vienne en premier, avec des conteneurs de service pour les tests qui ont besoin d'une base de données |
| [0007](lessons/0007-matrix-builds.md) | Builds en matrice | Exécuter un même job sur plusieurs versions et plateformes avec une matrice, et maîtriser ce que fail-fast, include et exclude font à l'exécution |
| [0008](lessons/0008-caching.md) | Le cache | Indexer un cache sur le lockfile, se rabattre sur des restore keys, et savoir ce qu'on ne doit jamais confier à un cache |
| [0009](lessons/0009-flaky-tests.md) | Tests instables | Un test qui échoue sans modification du code détruit la confiance dans tout le pipeline, alors trouvez sa cause et mettez-le en quarantaine au lieu de le cacher derrière des nouveaux essais |
| [0010](lessons/0010-making-a-pipeline-fast.md) | Rendre un pipeline rapide | Raccourcir le chemin critique, annuler les exécutions dépassées avec des groupes de concurrence, et fixer des timeouts pour qu'un job bloqué ne puisse pas monopoliser la file |
| [0011](lessons/0011-artifacts.md) | Artefacts | Transmettre un résultat de build entre jobs et le conserver après l'exécution grâce aux artefacts, et pourquoi un artefact n'est pas un cache |
| [0012](lessons/0012-versioning-a-build.md) | Versionner un build | Donner à chaque build une identité traçable jusqu'à son commit, et le construire une seule fois pour que ce qui est testé soit ce qui est livré |
| [0013](lessons/0013-building-and-publishing-an-image.md) | Construire et publier une image | Construire, taguer et pousser une image de conteneur depuis un workflow, mettre ses couches en cache, et transmettre son digest aux étapes suivantes |
| [0014](lessons/0014-secrets-and-the-github-token.md) | Les secrets et le GITHUB_TOKEN | Stocker les secrets par dépôt et par environnement, savoir ce que le masquage laisse passer, et restreindre le GITHUB_TOKEN avec permissions |
| [0015](lessons/0015-oidc-instead-of-long-lived-keys.md) | OIDC au lieu de clés de longue durée | Laisser un cloud faire confiance à un token de courte durée émis pour une seule exécution, et délimiter cette confiance avec la claim subject |
| [0016](lessons/0016-untrusted-input.md) | Entrées non fiables | Les titres, les noms de branche et le code des forks sont des entrées d'attaquant, et pull_request_target avec un checkout du fork leur livre vos secrets |
| [0017](lessons/0017-environments-and-approvals.md) | Environnements et approbations | Conditionner un déploiement par des environnements, des relecteurs obligatoires, des règles de branches de déploiement et des secrets d'environnement |
| [0018](lessons/0018-promotion-between-environments.md) | Promotion entre environnements | Faire passer un artefact construit de la préproduction à la production par digest, avec une configuration fournie par environnement |
| [0019](lessons/0019-deployment-strategies.md) | Stratégies de déploiement | Recreate, rolling, blue-green et canary, ce que chacune coûte en capacité et en risque, et ce qu'un canary doit mesurer pour avoir un sens |
| [0020](lessons/0020-rollback-and-roll-forward.md) | Rollback et roll forward | Revenir en arrière en redéployant le dernier artefact sain, aller de l'avant quand les données ont déjà évolué, et séparer le déploiement de la release avec des feature flags |
| [0021](lessons/0021-database-migrations-in-a-deploy.md) | Les migrations de base de données dans un déploiement | Ordonner les modifications de schéma autour du code avec expand and contract, pour que chaque version qui tourne pendant un déploiement fonctionne avec le schéma |
| [0022](lessons/0022-push-deploys-and-gitops.md) | Déploiements en push et GitOps | Un pipeline qui pousse vers un cluster face à un agent dans le cluster qui tire depuis Git, et ce que chacun fait aux identifiants et à la dérive |
| [0023](lessons/0023-pinning-what-the-pipeline-runs.md) | Épingler ce que le pipeline exécute | Épingler les actions tierces sur un SHA de commit complet, verrouiller les dépendances, et garder les épinglages à jour avec Dependabot |
| [0024](lessons/0024-provenance-and-sboms.md) | Provenance et SBOM | Attester où et à partir de quoi un artefact a été construit, lister ce qu'il contient, et vérifier les deux avant son exécution |
| [0025](lessons/0025-reusable-workflows-and-composite-actions.md) | Workflows réutilisables et actions composites | Partager la logique de pipeline entre dépôts avec un workflow appelé ou une action composite, et choisir selon ce que chacun peut contenir |
| [0026](lessons/0026-monorepos-and-path-filters.md) | Monorepos et filtres de chemins | N'exécuter que ce qu'une modification touche grâce aux filtres de chemins, et pourquoi un check obligatoire ignoré peut bloquer tous les merges |
| [0027](lessons/0027-debugging-a-pipeline.md) | Déboguer un pipeline | Lire le log, relancer avec les logs de débogage, et trouver ce qui diffère entre le runner et votre machine quand cela passe en local |
| [0028](lessons/0028-reviewing-a-pipeline.md) | Relire un pipeline | Relire le workflow de quelqu'un d'autre en nommant ce qui va d'abord échouer, ralentir ou fuiter |
| [0029](lessons/0029-changing-a-shared-workflow.md) | Modifier un workflow partagé | Modifier un workflow réutilisable ou un check obligatoire dont dépendent d'autres équipes sans casser leurs merges |
| [0030](lessons/0030-when-the-usual-answer-is-wrong.md) | Quand la réponse habituelle est fausse | Dire quand le déploiement continu, un canary ou une valeur par défaut du pipeline est le mauvais choix, et trancher un comportement contesté à partir de la référence de syntaxe des workflows |

## Référence

- [Glossaire](GLOSSARY.md) : termes de référence pour ce sujet
- [Ressources](RESOURCES.md) : sources fiables, chacune annotée avec ce qu'elle couvre
- [Syntaxe des workflows](reference/workflow-syntax.md) : déclencheurs, jobs, steps, expressions, contextes et outputs, avec les équivalents Jenkins et GitLab, issus des étapes 1 et 2
- [Feedback rapide](reference/fast-feedback.md) : ordre des étapes, matrices, clés de cache, gestion des tests instables, concurrence et timeouts, issus de l'étape 3
- [Artefacts et versionnement](reference/artifacts-and-versioning.md) : artefacts contre caches, schémas de version, construire une seule fois, tags et digests d'image, issus de l'étape 4
- [Sécurité des pipelines](reference/pipeline-security.md) : secrets, permissions des tokens, OIDC, entrées non fiables, épinglage et provenance, issus des étapes 5 et 8
- [Déploiements](reference/deployments.md) : environnements, promotion, les quatre stratégies, rollback, ordre des migrations et GitOps, issus des étapes 6 et 7
- [Les pipelines à l'échelle](reference/pipelines-at-scale.md) : workflows réutilisables contre actions composites, filtres de chemins, checks obligatoires et débogage d'une exécution, issus de l'étape 9
- [Liste de contrôle de relecture d'un pipeline](reference/pipeline-review-checklist.md) : les questions à poser au pipeline de quelqu'un d'autre, et quand la réponse habituelle est fausse, issues de l'étape 10

## Comment cela fonctionne

Chaque leçon est courte et autonome. Les corrigés sont repliés : rappelez-vous d'abord, puis ouvrez-les. Les exercices en situation réelle comptent plus que la lecture, et les espacer dans le temps est justement le but. Tout ce qui reste flou à la fin d'une leçon mérite d'être suivi jusqu'à sa source primaire avant de passer à la suite.
