---
title: "14. Les fichiers comme mémoire"
description: "Utiliser des fichiers durables comme forme la plus simple de mémoire entre exécutions pour les agents"
type: lesson
---

# Leçon 14. Les fichiers comme mémoire

**Lien avec la mission :** Diagnostiquer un agent défaillant à partir de sa trajectoire au lieu d'ajouter une instruction de plus à son prompt, en construisant des systèmes où la mémoire de l'agent est inspectable et où le harness peut gérer ce qui persiste.
**Source primaire :** [Billet : "Effective Context Engineering for AI Agents", Anthropic Engineering](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents)
**Prérequis :** [Leçon 13](0013-scratchpad-versus-memory.md)

## Échauffement

1. ▢ Vous démarrez un agent avec un transcript neuf pour la deuxième fois. Que vous dit le transcript vide ?

<details markdown="1"><summary>Vérifier</summary>

Que l'agent démarre une nouvelle exécution sans aucun souvenir de la précédente, sauf si le harness a délibérément rechargé des faits avant le début de la boucle.

</details>

2. ▢ Un agent a écrit des notes dans un fichier pendant sa dernière exécution. Si vous voulez que ces notes influencent le comportement de l'agent dans la nouvelle exécution, que doit faire le harness ?

<details markdown="1"><summary>Vérifier</summary>

Le harness doit lire le fichier, ou les parties pertinentes, et inclure le contenu dans le contexte ou le prompt initial de la nouvelle exécution, pour que le modèle puisse le voir et agir dessus.

</details>

## À savoir

Écrire des faits dans un simple fichier, ou un stockage durable similaire, que le harness relit lors d'une exécution ultérieure est la forme de mémoire entre exécutions la plus simple qui fonctionne. Le schéma est direct : donnez à l'agent un outil pour écrire une note, un fichier markdown, un enregistrement JSON ou un petit journal structuré, et au début d'une exécution ultérieure, le harness relit les parties pertinentes de ce fichier dans le nouveau transcript avant le début de la boucle.

C'est délibérément simple et inspectable, comparé à, disons, une base de données vectorielle. Un humain peut ouvrir le fichier et lire exactement ce que l'agent « retient ». Vous pouvez le modifier à la main si besoin. Vous pouvez repérer des entrées périmées ou fausses et les corriger sans rien réentraîner.

Le risque est pourtant réel. Un agent qui continue d'ajouter à un fichier de mémoire sans jamais l'élaguer ni le mettre à jour accumule avec le temps des notes périmées ou contradictoires. Une note qui était vraie le mois dernier peut être fausse aujourd'hui. Deux faits différents peuvent se contredire. C'est le même problème de dégradation du contexte que les leçons 10 et 11 ont traité pour un transcript qui grandit au sein d'une seule exécution. La mémoire demande la même gestion active : revue périodique, archivage des anciennes entrées, consolidation des doublons, suppression des faits qui ne s'appliquent plus.

Une précision importante : la récupération à la demande, de la leçon 11, qui va chercher du détail dans un corpus de documents ou de travaux antérieurs par la recherche, n'est pas la même chose que la mémoire, même si les deux consistent à « amener du texte en contexte ». La récupération répond à la question « qu'est-ce qui est pertinent pour cette requête précise, maintenant ? » en cherchant dans un grand corpus. La mémoire est un petit ensemble de faits soigneusement choisis que l'agent, ou son concepteur, a jugé bon de reporter quelle que soit la requête en cours. Un assistant de code peut récupérer des exemples du travail passé de l'utilisateur pour illustrer un style, mais il a aussi besoin d'une mémoire qui dit « l'utilisateur préfère async/await aux callbacks » comme fait permanent, pas comme résultat de requête. Le corpus de récupération sert à répondre à des questions précises ; le fichier de mémoire sert au contexte permanent.

La mise en garde honnête de [Effective Context Engineering for AI Agents](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents) est la suivante : la mémoire d'un agent entre exécutions est un domaine plus récent et moins établi. Les systèmes de production pour la mémoire entre exécutions évoluent encore. Cette leçon couvre le schéma à base de fichiers, simple et inspectable par un humain, mais pas nécessairement l'approche définitive que votre système de production utilisera dans quelques années.

## Pratique

1. ▢ Un agent aide un utilisateur à apprendre à cuisiner. L'agent note que l'utilisateur n'aime pas la coriandre et suggère des recettes sans elle. Quand vous relancez l'agent le lendemain pour une nouvelle séance de cuisine, le harness doit-il recharger la note sur la coriandre depuis le fichier de mémoire ?

<details markdown="1"><summary>Vérifier</summary>

Oui. La préférence est un fait permanent sur l'utilisateur qui s'applique d'une session à l'autre. Le harness doit lire le fichier de mémoire au démarrage et inclure « l'utilisateur n'aime pas la coriandre » dans le contexte initial pour que le modèle puisse l'utiliser en générant de nouvelles recettes.

</details>

2. ▢ Pendant une exécution, un agent écrit dans un scratchpad « fichiers vérifiés jusqu'ici : api.py, utils.py, config.py » pour éviter de les réanalyser. L'exécution se termine. Cette entrée de scratchpad doit-elle être sauvegardée dans le fichier de mémoire entre exécutions ?

<details markdown="1"><summary>Indice</summary>

Cette information précise, la liste des fichiers vérifiés lors de cette exécution, doit-elle être reportée aux exécutions futures, ou n'était-elle qu'une comptabilité utile au sein d'une seule tâche ?

</details>

<details markdown="1"><summary>Vérifier</summary>

Probablement pas, sauf si la tâche s'étend sur plusieurs exécutions d'agent. Si chaque revue de code est une tâche neuve et indépendante, la liste des fichiers vérifiés lors de l'exécution A n'est pas pertinente pour l'exécution B. Sauvegarder chaque entrée de scratchpad encombrerait le fichier de mémoire de détails éphémères. Une bonne heuristique : ne sauvegarder un fait en mémoire que si une exécution future en aura besoin.

</details>

3. ▢ Vous remarquez que le fichier de mémoire de l'agent contient maintenant des conseils contradictoires : « l'utilisateur préfère les tabulations » et « l'utilisateur préfère les espaces », écrits à des semaines d'intervalle. Que faire ?

    - a) Supprimer entièrement le fichier de mémoire pour que l'agent reparte de zéro.
    - b) Relire et modifier manuellement le fichier pour corriger la contradiction.
    - c) Ajouter un nouvel outil à l'agent pour qu'il résolve les conflits automatiquement.
    - d) L'ignorer, puisque le modèle saura bien lequel est actuel.

<details markdown="1"><summary>Vérifier</summary>

**b)** Relire et modifier manuellement le fichier. La gestion de la mémoire est une responsabilité humaine. Il faut comprendre quelle entrée est périmée, la corriger ou la supprimer, et garder le fichier propre et faisant autorité. Supprimer tout le fichier fait perdre d'autres faits précieux. Automatiser la résolution des conflits sans jugement humain risque d'encoder la mauvaise préférence. Le modèle ne devrait pas avoir à deviner ni à raisonner sur les contradictions de sa propre mémoire.

</details>

4. ▢ En quoi un système de mémoire à base de fichiers diffère-t-il d'un système de récupération qui cherche dans un corpus du travail passé de l'agent ?

<details markdown="1"><summary>Vérifier</summary>

Un système de récupération répond à « qu'est-ce qui, dans mon travail passé, est pertinent pour cette requête ? » et tire du matériel d'après une correspondance par mots-clés ou sémantique. Un système de mémoire détient un petit ensemble de faits permanents que le harness charge quelle que soit la requête. La mémoire est choisie et durable ; la récupération est pilotée par la requête. Vous pouvez récupérer des exemples de code passés quand l'utilisateur demande « montre-moi comment j'ai résolu cela avant », mais vous vous souvenez en permanence que « l'utilisateur préfère async/await » comme préférence permanente.

</details>

## Exercices en situation réelle

- [ ] Si vous avez un agent qui s'exécute plus d'une fois, vérifiez si le harness charge des faits stockés avant le premier appel au modèle. Sinon, ajoutez une instruction print ou un log pour voir ce qui se passe au démarrage de l'exécution.
- [ ] Concevez un format simple de fichier de mémoire pour une tâche que vous connaissez bien. Quels faits écririez-vous ? Comment sauriez-vous quand mettre à jour ou retirer une entrée ?
- [ ] Demain : construisez un agent à une seule exécution qui écrit un fait dans un fichier de mémoire, dans n'importe quel format : JSON, markdown ou texte brut. Puis construisez une seconde exécution du même agent qui lit ce fichier et l'utilise. Pas de base de données vectorielle, pas de recherche, juste un stockage durable et un chargement géré par le harness.

## Pour aller plus loin

- [Billet : "Effective Context Engineering for AI Agents", Anthropic Engineering](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents)
- [Ressources](../RESOURCES.md)

---

Ça ne passe pas ? Relisez la source primaire en haut de page, car cette leçon la condense et c'est dans la condensation que la compréhension s'échappe. Consultez le [glossaire](../GLOSSARY.md) pour tout terme qui vous a paru glissant.

Si c'est la leçon elle-même qui n'est pas claire plutôt que la matière, c'est un défaut : [ouvrez une issue](https://github.com/TokenCemetery/teach/issues).
