---
title: "30. Évaluer un agent"
description: "Mesurer la réussite d'un agent au niveau du résultat plutôt qu'au niveau de la trajectoire, et pourquoi une seule exécution réussie ne prouve pas que l'agent est fiable"
type: lesson
---

# Leçon 30. Évaluer un agent

**Lien avec la mission :** Diagnostiquer un agent défaillant à partir de sa trajectoire, en nommant la cause (une boucle, un contexte empoisonné, un outil mal spécifié, une mauvaise condition d'arrêt) plutôt que de re-prompter au hasard.
**Source primaire :** [Article : "tau-bench: A Benchmark for Tool-Agent-User Interaction in Real-World Domains", Yao et al., 2024](https://arxiv.org/abs/2406.12045)
**Prérequis :** [Leçon 29](0029-tracing-and-trajectory-replay.md), [Trajectoire](../GLOSSARY.md)

## Échauffement

1. ▢ Depuis la leçon 29 : quand vous lisez la trajectoire d'un agent pour diagnostiquer une défaillance, quelles deux choses devez-vous chercher en premier : la décision que le modèle a prise, ou le résultat réel que cette décision a produit ?

<details markdown="1"><summary>Vérifier</summary>

Les deux, mais dans cet ordre : d'abord, la décision que le modèle a prise à chaque étape (quel outil a-t-il choisi, quels arguments a-t-il passés). Ensuite, ce que l'outil a réellement renvoyé. Une décision raisonnable avec un mauvais résultat pointe vers un problème d'implémentation de l'outil. Une décision déraisonnable avec un résultat raisonnable pointe vers une défaillance de raisonnement. Les confondre est ce qui bloque le diagnostic.

</details>

2. ▢ Depuis la leçon 29 : si une trajectoire montre le modèle qui prend la bonne décision cinq fois de suite mais que l'agent n'accomplit pas la tâche, qu'est-ce que ce schéma suggère de cassé ?

<details markdown="1"><summary>Vérifier</summary>

Il suggère que le harness ou les implémentations des outils eux-mêmes sont cassés, pas le raisonnement du modèle. Le modèle choisit correctement, mais autre chose dans la boucle ne s'exécute pas comme prévu. Cela pourrait être un outil qui prétend avoir réussi sans réellement effectuer l'action, un harness qui coupe la boucle trop tôt, ou un résultat ajouté incorrectement au transcript.

</details>

## À savoir

### Résultat contre trajectoire

Quand vous évaluez un agent, vous pouvez mesurer deux choses différentes, et elles ne sont pas la même.

**La réussite du résultat** signifie : l'agent a-t-il atteint le bon état final ? Le fichier a été mis à jour correctement. Le ticket a été trié dans la bonne catégorie. La question de l'utilisateur a reçu une réponse exacte. Vous vérifiez le résultat en inspectant ce que l'utilisateur voit.

**La justesse de la trajectoire** signifie : l'agent a-t-il suivi la bonne séquence d'étapes pour y arriver ? Il a appelé les bons outils dans le bon ordre avec des arguments sensés, interprété correctement les résultats et évité les boucles circulaires.

Une tâche d'agent a souvent de nombreux chemins valides vers le même résultat correct. Noter par rapport à une seule trajectoire de référence est généralement une erreur ; noter le résultat (le fichier a-t-il réellement été mis à jour, le ticket a-t-il réellement été correctement trié) est généralement juste. Pourtant, la trajectoire compte toujours : c'est ce qui permet de diagnostiquer *pourquoi* quelque chose a échoué, ce qu'enseignent les leçons 27 à 29 de ce parcours. Le résultat dit si l'agent a réussi ; la trajectoire dit pourquoi il a échoué.

### pass^k : la fiabilité sur des essais répétés

Une seule exécution réussie ne dit pas que l'agent est fiable. Le même agent sur la même tâche peut échouer à une deuxième tentative en raison de la nature stochastique des nombreux points de décision d'un agent qui se cumulent sur une longue trajectoire. pass^k mesure la probabilité que l'agent réussisse sur la totalité de k essais indépendants de la même tâche. Si un agent réussit 8 fois sur 10 sur une tâche, vous en savez plus que s'il avait réussi une fois : vous avez la preuve qu'il est fiable à environ 80 pour cent sur cette tâche. Ne confondez pas avec la précision sur une tâche ; c'est un seuil de fiabilité bien plus fort et plus honnête qu'une exécution unique réussie ou non. Pour le traitement complet de la façon de concevoir et de calculer pass^k dans vos propres évaluations, voyez la leçon qui suit celle-ci.

### Ce que mesurent réellement les articles de benchmark

Trois articles ancrent les sources de cette étape, et chacun représente un choix différent sur la façon de noter les agents :

**tau-bench** (Yao et al., 2024) évalue l'usage d'outils multi-tours face à un utilisateur simulé (un modèle de langage jouant un humain) et à une politique de domaine (des règles sur ce qui constitue la réussite). Il utilise des mesures de fiabilité sur essais répétés, donc vous voyez des scores pass^k, pas des résultats en un seul essai.

**SWE-bench** (Jimenez et al., 2023) évalue des agents sur de vraies issues de dépôts, avec la suite de tests du projet comme vérification du résultat. Si les tests passent, l'agent a résolu l'issue. La trajectoire n'est ni contrainte ni notée du tout ; seul le résultat compte.

**GAIA** (Mialon et al., 2023) pose des questions faciles pour une personne et difficiles pour un agent, qui exigent de l'usage d'outils en plusieurs étapes pour atteindre une réponse unique et non ambiguë. Il mesure si l'agent atterrit sur la bonne réponse, pas si son raisonnement était élégant.

Les trois privilégient la réussite du résultat sur l'élégance de la trajectoire, et les trois utilisent une évaluation sur essais répétés ou plusieurs cas de test pour aller au-delà de la chance d'une exécution unique.

### Le passage de relais vers la profondeur

Cette leçon vous donne le vocabulaire : résultat contre trajectoire, pass^k, réussite de la tâche. Le traitement complet de la construction d'une évaluation d'agent se trouve dans le parcours llm/evals, leçon 13, Évaluer les agents et l'usage d'outils. Cette leçon couvre les métriques, la conception du juge, la façon de construire un jeu de test mis de côté, ce que signifie la significativité statistique et comment éviter d'évaluer par inadvertance la mauvaise chose. Le rôle de ce parcours est seulement de s'assurer que vous savez ce qu'il faut mesurer au départ. Lisez cette leçon pour connaître les concepts ; lisez la leçon 13 de llm/evals pour la profondeur.

## Pratique

1. ▢ Un agent dépose avec succès un ticket dans votre outil de suivi d'issues du premier coup. Vous le relancez sur un autre ticket, et il échoue en silence, créant un ticket vide sans texte. Vous le lancez une troisième fois et il réussit. L'agent est-il prêt pour la production d'après ces données ?

<details markdown="1"><summary>Vérifier</summary>

Non. Vous avez un succès, un échec et un autre succès. Cela fait 2 succès sur 3 essais, ce qui suggère une fiabilité d'environ 67 pour cent. Vous n'avez pas encore assez de données, et 67 pour cent est trop bas pour la plupart des usages en production. Il faut au moins 10 à 20 essais sur des tickets variés pour établir un pass^k fiable. Le mauvais réflexe est de supposer que l'unique échec était un accident et que l'agent va bien ; le bon est de prendre pass^k au sérieux.

</details>

2. ▢ Vous diagnostiquez un agent qui n'a pas réussi à mettre à jour un enregistrement de base de données. Vous regardez la trajectoire et voyez que le modèle a choisi le bon outil update_record avec le bon identifiant d'enregistrement et les nouvelles valeurs correctes. L'outil a renvoyé un succès : « ok, record updated ». Mais quand vous vérifiez la base de données, l'enregistrement n'a pas réellement été mis à jour. À quel niveau faut-il regarder pour corriger cela ?

<details markdown="1"><summary>Indice</summary>

La décision du modèle et la trajectoire semblent toutes deux correctes. Le problème ne se situe ni dans le raisonnement ni dans la prise de décision.

</details>

<details markdown="1"><summary>Vérifier</summary>

Il faut inspecter l'implémentation de l'outil elle-même. La trajectoire montre que le modèle a fait le bon choix et que l'outil a prétendu avoir réussi, mais le résultat est faux. Quelque chose entre la valeur de retour de l'outil et l'état réel de la base de données est cassé. Cela pourrait être un outil qui consigne un succès sans réellement exécuter, un harness qui n'attend pas la fin de l'outil, ou un problème de connexion à la base de données. Le diagnostic de trajectoire consiste ici à regarder au-delà des mots que l'outil a renvoyés et à vérifier ce qui s'est réellement passé.

</details>

3. ▢ Vous évaluez des agents avec SWE-bench (de vraies issues GitHub, avec les suites de tests des projets comme vérification du résultat). La trajectoire d'un agent montre qu'il a pris une décision que vous jugez non optimale, avec des appels d'outils supplémentaires par rapport à un chemin plus direct. Mais la suite de tests de l'issue passe. Faut-il baisser le score de l'agent pour la trajectoire non optimale ?

    - a) Oui, parce que la trajectoire montre de l'inefficacité
    - b) Non, parce que seul le passage de la suite de tests compte dans SWE-bench
    - c) Noter le résultat comme réussi mais signaler la trajectoire pour une optimisation future
    - d) Seulement si le chemin non optimal a pris plus de tokens qu'une base de référence

<details markdown="1"><summary>Vérifier</summary>

**b)** Non, parce que seul le passage de la suite de tests compte dans SWE-bench. SWE-bench est conçu pour noter les résultats, pas les trajectoires. Si les tests passent, l'agent a résolu l'issue, qu'il ait ou non pris le chemin le plus élégant. Le mauvais réflexe est de noter l'élégance de la trajectoire en plus du résultat ; cela confond deux évaluations distinctes. **a)** vous ferait glisser vers une métrique que SWE-bench n'utilise pas. **c)** ajoute une complexité dont SWE-bench n'a pas besoin pour son objectif principal. **d)** introduit une contrainte distincte (budget de tokens) qui ne fait pas partie de la conception de SWE-bench.

</details>

4. ▢ Vous évaluez un agent sur une tâche par le seul résultat : soit il atteint le bon état final, soit non. Vous le lancez 100 fois, et il réussit 73 fois. Vous améliorez le system prompt et refaites un test. Il réussit maintenant 75 fois sur 100. L'amélioration est petite. Que suggère ce schéma que vous devriez faire ensuite ?

<details markdown="1"><summary>Vérifier</summary>

Il suggère que les améliorations de prompting seules ne suffisent pas à traiter les défaillances racines. Le gain de 73 à 75 pour cent est modeste ; la plupart des échecs persistent malgré de meilleures instructions. Il faut lire les trajectoires des exécutions en échec pour identifier le mode de défaillance réel (un outil mal utilisé, une erreur de logique, un problème de contexte, un obstacle que l'agent ne gère pas) puis corriger ce problème précis. Il se peut aussi que la tâche soit simplement trop difficile pour le modèle ou le jeu d'outils actuels, et qu'aucun changement de prompt n'aide. Le diagnostic de trajectoire dit laquelle des deux est vraie.

</details>

## Exercices en situation réelle

- [ ] Choisissez une tâche d'agent simple et répétable (par exemple « chercher une personne dans un annuaire », « convertir un format de fichier », « répondre à une question factuelle avec un outil »). Lancez l'agent 10 fois et notez réussite ou échec à chaque fois. Calculez le pass^k empirique et écrivez ce que ce nombre vous apprend qu'une exécution unique ne vous apprendrait pas.

- [ ] Prenez un article de benchmark publié sur les agents (tau-bench, SWE-bench, GAIA, WebArena ou un autre). Lisez sa section d'évaluation et identifiez : quelle est la métrique de résultat, la trajectoire est-elle contrainte ou libre, et quelle mesure de fiabilité utilise-t-il.

- [ ] Demain : trouvez la trajectoire d'un agent issue d'une source publique (documentation, blog, GitHub). Rédigez une grille d'évaluation qui note la trajectoire sur le seul résultat (l'état final correspondait-il à l'objectif), et une grille distincte qui note sur la trajectoire (a-t-elle suivi des étapes sensées). Appliquez les deux grilles à la même trajectoire et comparez les scores. Écrivez un paragraphe pour dire si le résultat ou la trajectoire vous a appris le plus sur le fonctionnement de l'agent.

## Pour aller plus loin

- [Leçon 13 : Évaluer les agents et l'usage d'outils](../../evals/lessons/0013-evaluating-agents-and-tool-use.md)
- [Article : "tau-bench: A Benchmark for Tool-Agent-User Interaction in Real-World Domains", Yao et al., 2024](https://arxiv.org/abs/2406.12045)
- [Ressources](../RESOURCES.md)

---

Ça ne passe pas ? Relisez la source primaire en haut de page, car cette leçon la condense et c'est dans la condensation que la compréhension s'échappe. Consultez le [glossaire](../GLOSSARY.md) pour tout terme qui vous a paru glissant.

Si c'est la leçon elle-même qui n'est pas claire plutôt que la matière, c'est un défaut : [ouvrez une issue](https://github.com/TokenCemetery/teach/issues).
