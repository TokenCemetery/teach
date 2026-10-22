---
title: "29. Traçage et rejeu de trajectoire"
description: "Utiliser des conventions de trace indépendantes des fournisseurs pour capturer les exécutions d'agents, et rejouer les trajectoires pour parcourir pas à pas les échecs"
type: lesson
---

# Leçon 29. Traçage et rejeu de trajectoire

**Lien avec la mission :** Enregistrer les exécutions d'agents avec des traces structurées et standardisées, et pouvoir rejouer une trajectoire sauvegardée, permet de remettre à un collègue le point exact de la défaillance, de la parcourir pas à pas de façon indépendante, et de faire passer le diagnostic en production de « regardons les logs » à « parcourons la trajectoire pas à pas ».
**Source primaire :** [Spécification : "Semantic Conventions for Generative AI", OpenTelemetry](https://opentelemetry.io/docs/specs/semconv/gen-ai/)
**Prérequis :** [Leçon 28](0028-cascading-tool-errors.md), [Trajectoire](../GLOSSARY.md)

## Échauffement

1. ▢ Depuis la leçon 28 : quelle est la différence entre une erreur de validation de schéma et un argument halluciné ?

<details markdown="1"><summary>Vérifier</summary>

Une erreur de validation de schéma survient immédiatement quand un champ obligatoire manque ou qu'une valeur est du mauvais type ; le modèle reçoit un retour explicite. Un argument halluciné est une valeur bien typée qui passe la validation mais ne correspond à rien de réel, donc l'erreur survient en aval et le modèle peut mal diagnostiquer la raison de l'échec.

</details>

2. ▢ Depuis la leçon 7 : quel est l'unique élément d'état à persister pour reprendre une exécution d'agent au tour N ?

<details markdown="1"><summary>Vérifier</summary>

Le transcript : l'historique complet de la conversation jusqu'au tour N, y compris chaque réponse du modèle, chaque appel d'outil et chaque résultat d'outil. À la reprise, renvoyez ce transcript au modèle et continuez la boucle à partir du tour N+1.

</details>

## À savoir

### Traces, spans et conventions indépendantes des fournisseurs

Une trace est un enregistrement structuré et horodaté de ce qui s'est passé pendant une exécution d'agent. Elle est composée de spans, chacun représentant une opération distincte :

- Un span par appel au modèle (entrée : transcript ; sortie : réponse du modèle et appels d'outils ; durée ; tokens utilisés)
- Un span par exécution d'outil (entrée : nom de l'outil et arguments ; sortie : résultat ou erreur ; durée)
- Un span par itération de la boucle (heure de début, heure de fin, numéro du tour)

Sans convention partagée, chaque équipe et chaque éditeur nomment ces éléments différemment. Un outil peut appeler l'entrée d'un appel au modèle « prompt », un autre « messages », un autre « input ». Un outil appelle la sortie « response », un autre « generated_text ». Cela rend les traces incomparables : une équipe qui utilise les outils de l'éditeur A ne peut pas facilement lire les traces de l'éditeur B, et passer d'un éditeur à un autre signifie réécrire tout votre code d'analyse des traces.

Les conventions sémantiques GenAI d'OpenTelemetry définissent un vocabulaire indépendant des fournisseurs pour ces spans et attributs. Elles standardisent l'information que chaque span doit porter :

Un span d'appel au modèle comprend : le nom du modèle, le total de tokens en entrée, le total de tokens en sortie, l'effort de raisonnement (s'il est défini), les appels d'outils demandés, la raison d'arrêt.

Un span d'exécution d'outil comprend : le nom de l'outil, s'il s'agit d'un outil client ou d'un outil serveur, le statut du résultat de l'outil (succès ou erreur), s'il y a eu un coût (pour les outils serveur), le message d'erreur en cas d'échec.

Le span de transaction enveloppe l'ensemble et comprend : le numéro du tour de la boucle d'agent, les heures de début et de fin en temps réel, si le tour a réussi ou échoué, toute décision d'arrêt prise.

Parce que ces éléments sont standardisés, une trace produite par un harness peut être lue par n'importe quel outil compatible OpenTelemetry. Le même tableau de bord, le même script d'analyse ou la même visualisation qui fonctionne avec les traces d'une équipe fonctionne avec celles d'une autre. C'est le même principe que celui qui a standardisé les formats de transmission d'appels d'outils dans la leçon 3 : tous les concepts sous-jacents (boucle d'agent, appel au modèle, appel d'outil) sont les mêmes d'un fournisseur à l'autre, donc un vocabulaire standard permet de passer de l'un à l'autre.

### Pourquoi les traces structurées comptent pour le diagnostic

Les boucles et l'empoisonnement de la leçon 27, et les cascades de la leçon 28, se repèrent toutes en lisant attentivement une trajectoire. Mais une lecture attentive n'est faisable que si la trajectoire est bien structurée.

Imaginez que vous essayez de diagnostiquer une défaillance dans une exécution d'agent de 47 tours et de centaines de lignes de logs. Vous avez des instructions print mélangées à des messages d'erreur, des résultats d'outils imprimés en JSON, et des horodatages qui sont peut-être exacts, peut-être pas. Vous lisez ligne par ligne en essayant de reconstituer ce qui s'est passé.

Imaginez maintenant la même exécution représentée par une trace structurée : chaque span est étiqueté avec un numéro de tour, chaque appel au modèle est étiqueté avec le nom du modèle, chaque appel d'outil est étiqueté avec le nom de l'outil. Vous pouvez interroger la trace : « montre-moi tous les appels d'outils qui ont échoué à partir du tour 10 », ou « montre-moi le texte de raisonnement que le modèle a utilisé au tour 23 », ou « montre-moi une chronologie des spans exécutés en parallèle ». Le diagnostic est nettement plus rapide.

De plus, les traces structurées permettent d'automatiser une partie du diagnostic : une règle simple peut signaler « détecter les boucles répétitives en trouvant des spans consécutifs avec le même nom d'outil ». Une analyse après exécution peut signaler « détecter les défaillances en cascade en cherchant des spans d'erreur suivis de spans de nom d'outil différent en séquence rapprochée ». Ces motifs sont difficiles à détecter dans des logs en texte libre ; ils sont directs avec des données structurées.

### Rejeu de trajectoire : tester des hypothèses

Parce que le transcript est le seul état persistant de l'agent (leçon 7), vous pouvez sauvegarder une trajectoire et la renvoyer dans une exécution neuve à n'importe quel point. C'est ce qu'on appelle le rejeu de trajectoire.

Voici ce que cela rend possible :

**Reproduire les conditions exactes** : un client signale qu'un agent a échoué. Vous sauvegardez sa trajectoire (le transcript jusqu'au point de défaillance) et la renvoyez dans une exécution neuve du harness. L'exécution neuve voit exactement ce que l'exécution d'origine a vu, donc si elle reproduit la même défaillance, vous l'avez confirmée. Si elle réussit, vous avez trouvé un problème dans le harness ou l'environnement d'origine, pas dans la logique de l'agent.

**Avancer pas à pas à partir d'une défaillance** : vous identifiez le tour où les choses ont mal tourné (tour 12). Vous sauvegardez la trajectoire jusqu'au tour 11, puis la modifiez légèrement (peut-être en ajoutant une note dans le transcript, ou en changeant un résultat d'outil) et rejouez à partir du tour 12. Le modèle, voyant l'entrée modifiée, peut prendre un chemin différent. Cela permet de tester « et si ce résultat d'outil avait été plus clair ? » sans relancer tout l'agent depuis le tour 1.

**Collaborer au diagnostic** : un collègue demande « pourquoi l'agent a-t-il échoué au tour 28 ? » Vous lui remettez la trajectoire jusqu'au tour 27 et une description de ce que vous voulez qu'il regarde. Il peut la rejouer lui-même, indépendamment de vous, et arriver à sa propre conclusion. Vous partagez l'état exact, pas seulement une description de celui-ci.

**Construire un test de régression** : vous avez trouvé un bug et l'avez corrigé. Sauvegardez la trajectoire qui a déclenché le bug, rejouez-la avec le harness corrigé et vérifiez qu'elle réussit maintenant. Ajoutez-la à votre suite de tests pour que le bug ne revienne pas.

### Conception pratique du rejeu

Quand on conçoit le rejeu de trajectoire, quelques détails comptent :

**Sauvegarder le transcript complet**, y compris chaque tour, chaque appel d'outil, chaque résultat, chaque erreur. Ne pas tronquer ni échantillonner ; le modèle a besoin du contexte complet pour raisonner correctement au rejeu.

**Inclure les métadonnées du harness dans une section distincte et structurée** : le numéro du tour, les comptes de tokens, les comptes d'erreurs, les conditions d'arrêt qui ont été vérifiées. Cela aide à reconstituer l'état exact, même si vous n'avez pas tout sauvegardé dans le transcript.

**Horodater chaque span** pour voir combien de temps a pris chaque opération et s'il y a des écarts inexpliqués (latence réseau, nouveaux essais, reculs).

**Rendre le rejeu configurable** : permettre de rejouer à partir du tour N, ou de rejouer avec un transcript modifié (pour tester des hypothèses), ou de rejouer avec un autre modèle pour voir si le comportement change.

### Relation avec les autres outils de diagnostic

Les traces structurées ne remplacent pas la lecture attentive des trajectoires. Elles la complètent. Il faut toujours comprendre les modes de défaillance des leçons 27 et 28 (boucles, empoisonnement, cascades) pour savoir quels motifs on cherche. Mais une trace structurée rend les motifs plus faciles à voir et plus rapides à extraire.

Ensemble, ils forment une discipline : utiliser les traces pour naviguer rapidement dans la trajectoire, utiliser votre connaissance des modes de défaillance pour repérer ce qui compte, et utiliser le rejeu pour vérifier votre diagnostic.

## Pratique

1. ▢ Vous lisez une trace structurée d'une exécution d'agent. La trace montre : tour 1 (appel au modèle), tour 2 (appel d'outil à search_files), tour 3 (appel au modèle), tour 4 (appel d'outil à search_files avec des arguments identiques), tour 5 (appel au modèle), tour 6 (appel d'outil à search_files de nouveau). Vous vérifiez le résultat de l'outil pour chaque span et ils sont identiques. D'après la seule structure de la trace, quel mode de défaillance devez-vous soupçonner ?

<details markdown="1"><summary>Vérifier</summary>

Cela ressemble à une boucle répétitive de la leçon 27 : le même outil est appelé avec des arguments identiques aux tours 2, 4 et 6, et les résultats sont identiques. La trace structurée le rend évident parce que chaque tour et chaque appel d'outil sont étiquetés. Dans un log non structuré, il faudrait chercher à la main le nom de l'outil et les arguments sur de nombreuses lignes.

</details>

2. ▢ Vous rejouez une trajectoire à partir du tour 15 pour déboguer une défaillance au tour 30. Vous renvoyez au modèle le transcript jusqu'au tour 14 et lui demandez de continuer. Dans votre rejeu, l'agent prend un chemin différent de celui d'origine et réussit. Que vous dit cela sur la défaillance d'origine ?

<details markdown="1"><summary>Indice</summary>

Pensez à ce qui a changé entre l'exécution d'origine et le rejeu, en dehors de la décision du modèle.

</details>

<details markdown="1"><summary>Vérifier</summary>

La défaillance d'origine a probablement été causée par quelque chose dans le harness ou l'environnement aux tours 15 à 29, pas par le raisonnement du modèle. Causes possibles : un outil qui s'est comporté autrement que prévu lors de l'exécution d'origine, une défaillance transitoire (problème réseau, indisponibilité du service, quota dépassé) ou un élément non déterministe (aléa dans les résultats d'outils ou l'échantillonnage du modèle). Puisque le rejeu a réussi avec le même transcript et le même modèle, le problème n'était pas l'entraînement ni le raisonnement du modèle ; c'étaient des conditions externes. C'est un enseignement de diagnostic que vous n'obtiendriez pas en relisant simplement la trajectoire.

</details>

3. ▢ Vous concevez un schéma de trace structurée pour votre harness d'agent avec les conventions OpenTelemetry. Pour un span d'appel d'outil, lequel de ces attributs est le plus important pour diagnostiquer une défaillance en cascade (leçon 28) ?

    - a) Le nom de l'outil et les arguments
    - b) Le résultat de l'outil ou le message d'erreur
    - c) La durée en temps réel de l'appel d'outil
    - d) La version du modèle qui a appelé l'outil

<details markdown="1"><summary>Vérifier</summary>

**b)** Le résultat de l'outil ou le message d'erreur est le plus important pour diagnostiquer les cascades. Une cascade commence quand le modèle diagnostique mal une erreur, donc vous devez voir exactement quel message d'erreur a été renvoyé. Avec un message d'erreur clair, vous pouvez vérifier si la décision suivante du modèle était une réponse raisonnable à cette erreur. Le nom de l'outil et les arguments (a) sont secondaires ; ils montrent ce que le modèle a essayé, mais pas s'il a compris l'échec. La durée (c) et la version du modèle (d) sont utiles pour l'analyse de performance et la détection de régressions, mais pas primordiales pour le diagnostic d'une cascade.

</details>

4. ▢ Vous avez sauvegardé une trajectoire jusqu'au tour 10, et vous voulez tester une hypothèse : « si le résultat de l'outil au tour 5 avait inclus l'identifiant du client, l'agent aurait réussi au lieu d'entrer dans une boucle aux tours 6 à 10. » Comment modifieriez-vous la trajectoire et la rejoueriez-vous pour tester cette hypothèse ?

<details markdown="1"><summary>Vérifier</summary>

Vous éditeriez le transcript : trouver le résultat de l'outil au tour 5 et y ajouter l'information sur l'identifiant du client. Par exemple, changer « Tool result: success » en « Tool result: successfully created account; customer ID is 98765 ». Puis rejouer à partir du tour 6 avec ce transcript modifié. Si l'agent réussit maintenant, votre hypothèse est confirmée : l'information manquante était la cause racine. S'il boucle encore, le problème est ailleurs.

</details>

## Exercices en situation réelle

- [ ] Mettez en place une capture de trace de base pour un agent auquel vous avez accès. Pour au moins une exécution, exportez la trace et examinez sa structure. Identifiez : suit-elle un schéma cohérent ? Pouvez-vous trouver rapidement tous les appels au modèle et tous les appels d'outils ? Un langage de requête (comme le filtrage de « tous les appels d'outils en échec ») serait-il utile pour déboguer ?

- [ ] Sauvegardez une trajectoire d'une exécution d'agent (au moins 5 tours). Rejouez-la à partir du milieu (tour 3 ou 4) et observez si le rejeu produit les mêmes résultats ou des résultats différents. S'ils diffèrent, cherchez pourquoi.

- [ ] Demain : concevez une règle automatisée qui détecterait un mode de défaillance de la leçon 27 ou 28 dans une trace structurée. Écrivez du pseudocode ou du SQL qui interroge la trace et signale la défaillance. Par exemple : « signaler si le même outil est appelé plus de deux fois sur des tours consécutifs avec des arguments identiques ».

## Pour aller plus loin

- [Spécification : "Semantic Conventions for Generative AI", OpenTelemetry](https://opentelemetry.io/docs/specs/semconv/gen-ai/)
- [Ressources](../RESOURCES.md)

---

Ça ne passe pas ? Relisez la source primaire en haut de page, car cette leçon la condense et c'est dans la condensation que la compréhension s'échappe. Consultez le [glossaire](../GLOSSARY.md) pour tout terme qui vous a paru glissant.

Si c'est la leçon elle-même qui n'est pas claire plutôt que la matière, c'est un défaut : [ouvrez une issue](https://github.com/TokenCemetery/teach/issues).
