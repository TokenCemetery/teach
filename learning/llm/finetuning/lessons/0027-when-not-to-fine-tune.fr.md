---
title: "27. Quand ne pas faire de fine-tuning"
description: "Le fine-tuning est sixième sur la liste, et pourquoi cela compte"
type: lesson
---

# Leçon 27. Quand ne pas faire de fine-tuning

**Lien avec la mission :** La mission s'achève ici : *« capable de plaider de façon convaincante pour le prompting ou la récupération quand ceux-ci feraient mieux le travail »*. La compétence de senior, c'est de refuser le travail.
**Source primaire :** [Doc : "LoRA Without Regret", Hugging Face TRL](https://huggingface.co/docs/trl/main/en/lora_without_regret)
**Prérequis :** toutes les leçons précédentes, puisque celle-ci est la synthèse.

## Échauffement

1. ▢ Quelle phase d'inférence est limitée par la bande passante, et pourquoi cela favorise-t-il les petits modèles ?

<details markdown="1"><summary>Vérifier</summary>

Le decode. Chaque pas lit tous les poids pour produire un token, donc la vitesse suit la bande passante mémoire et un modèle plus petit est plus rapide presque en proportion de sa taille.

</details>

2. ▢ Nommez les quatre catégories de régression.

<details markdown="1"><summary>Vérifier</summary>

Suivi d'instructions général, respect du format et du comportement, sécurité et comportement de refus, capacité voisine non entraînée.

</details>

3. ▢ Quelle est la référence qu'une nouvelle variante de PEFT doit battre ?

<details markdown="1"><summary>Vérifier</summary>

LoRA à rank suffisant sur toutes les couches linéaires avec un learning rate réglé.

</details>

## À savoir

### La décision, dans l'ordre

Descendez cette liste. Arrêtez-vous à la première ligne qui résout votre problème.

| Approche | Résout | Coût |
|---|---|---|
| Un meilleur prompt | La plupart des problèmes de format et de comportement | Quelques minutes |
| Exemples few-shot | Cohérence du format, forme de la sortie | Tokens de prompt par requête |
| Récupération | Connaissances manquantes ou changeantes | Infrastructure de récupération |
| Usage d'outils | Calcul, consultation, actions | Infrastructure d'outils |
| Décodage contraint | Validité du schéma, de façon absolue | Support côté service |
| **Fine-tuning** | Comportement constant, coût du prompt, suffisance d'un petit modèle | Données, évaluation, maintenance |
| Full fine-tuning | Très grands changements de comportement | Substantiellement plus de tout |

Le fine-tuning est sixième. **La plupart des gens qui veulent faire du fine-tuning ont un problème que l'une des cinq premières lignes résout, plus vite et plus fiablement.** Atteindre la ligne six avant d'avoir épuisé les lignes un à cinq est l'erreur coûteuse la plus courante de ce domaine.

Notez en particulier que **le décodage contraint résout complètement la validité du schéma**, parce qu'une génération contrainte par une grammaire ne peut pas émettre de JSON invalide. Si tout votre problème est une sortie mal formée, vous n'avez rien à entraîner.

### Les trois questions qui tranchent

**1. Le problème est-il de la connaissance ou du comportement ?**

La connaissance, c'est-à-dire les faits, les documents et tout ce qui change, est le travail de la récupération. Le fine-tuning installe les faits de façon peu fiable, invérifiable, et leur obsolescence exige un ré-entraînement. La récupération est exacte, citable, et mise à jour en modifiant un document.

Le comportement, c'est-à-dire le format, le ton, la structure, la constance et une frontière de décision, est le travail du fine-tuning. C'est là qu'il excelle réellement et que rien d'autre ne fait aussi bien.

Le piège : « le modèle ne connaît pas notre produit » ressemble à un problème d'entraînement et c'est un problème de récupération. « Le modèle ne répond pas de façon constante dans notre style maison quelle que soit ma façon de formuler le prompt » ressemble à un problème de prompting et c'est un problème d'entraînement.

**2. Avez-vous réellement épuisé le prompting ?**

Pas « essayé quelques prompts ». Épuisé : itération systématique, exemples few-shot, un system prompt structuré, et **mesuré sur le même jeu held-out que vous utiliseriez pour évaluer un fine-tuning.** La plupart des affirmations selon lesquelles le prompting a échoué sont des affirmations selon lesquelles une poignée de tentatives non mesurées ont échoué.

Si vous ne pouvez pas indiquer le score du prompting sur votre jeu held-out, vous n'avez pas de référence, et sans référence vous ne pouvez pas démontrer que le fine-tuning a aidé.

**3. Allez-vous le maintenir ?**

Un fine-tuning est un artefact vivant. Les base models sont supplantés, les exigences évoluent, les distributions dérivent, les évaluations ont besoin d'être mises à jour. Si personne n'en est responsable, vous construisez quelque chose qui se dégradera silencieusement tout en ayant l'air de fonctionner, et un fine-tuning périmé est pire que pas de fine-tuning, parce qu'on lui fait confiance.

### Quand le fine-tuning est clairement le bon choix

Pour être juste envers la méthode, ces cas sont réels et courants :

- **Fort volume avec un long prompt.** Déplacer le contenu du prompt dans les poids se rembourse à chaque requête (leçon 26).
- **Un plus petit modèle peut alors suffire.** Le cas le plus fort, parce qu'il réduit le coût et la latence ensemble.
- **Un comportement qui résiste au prompting.** Un ton, un format ou une frontière de décision que le modèle ne tiendra pas de façon constante, quelle que soit votre façon de demander.
- **Une tâche étroite avec des exemples abondants.** Classification, extraction, transformation structurée : le fine-tuning est excellent et bat souvent un modèle bien plus grand piloté par prompt.
- **Des chemins critiques en latence.** Des prompts plus courts et des modèles plus petits aident tous deux, directement.
- **Une notation ou une syntaxe propre à un domaine** réellement sous-représentée dans le préentraînement.

### Combiner, plutôt que choisir

La formulation « fine-tuner ou récupérer » est généralement fausse. Les systèmes les plus solides font les deux, pour des tâches différentes :

**La récupération fournit les faits. Le fine-tuning enseigne quoi en faire.**

Un modèle fine-tuné pour bien utiliser le contexte récupéré, en le citant, en le respectant, en admettant quand il est insuffisant et en refusant d'inventer au-delà, combiné à une récupération qui fournit des faits exacts et à jour, bat chacune des deux seules. C'est une architecture, et la reconnaître est la version senior de cette décision.

### La position calibrée sur la capacité

Vous avez gagné ici une vision nuancée, alors tenez-la avec précision.

L'ancienne formulation, « LoRA est une approximation bon marché, le full fine-tuning est le vrai », est largement obsolète. Avec un rank suffisant sur toutes les couches linéaires et un learning rate correctement réglé, LoRA égale le full fine-tuning sur les charges typiques de fine-tuning supervisé. **L'écart de capacité s'est en grande partie refermé pour le régime dans lequel la plupart des gens travaillent.**

Ce qui signifie : si vous avez décidé de faire du fine-tuning, les adapters sont presque certainement la bonne méthode. Le full fine-tuning est pour de très grands changements de comportement, un préentraînement continu sur un nouveau domaine ou une nouvelle langue à grande échelle, ou la recherche où vous avez besoin de tout l'espace des paramètres. La question restante n'est pas « adapter ou full » mais « cela doit-il être entraîné tout court ».

### À quoi ressemble un bon jugement

> « Les échecs rapportés sont tous de l'obsolescence factuelle, donc c'est de la récupération, pas de l'entraînement. Mesurons d'abord une référence pilotée par prompt sur le jeu held-out. Si le problème résiduel après la récupération est la cohérence du format à 40 000 requêtes par jour, alors un adapter all-linear de rank 32 sur un modèle 3B mérite d'être chiffré, y compris la personne qui le ré-entraînera dans six mois. Je voudrais un jeu de régression couvrant la sécurité et le suivi d'instructions général avant de livrer, parce que nous adapterions un modèle instruct. »

Rien de cela n'est un fait que vous avez cherché. C'est la forme du raisonnement pour lequel cet espace de travail existait.

## Pratique

1. ▢ « Notre bot de support ne connaît pas les produits lancés ce trimestre. » Fine-tuner ou non ?

<details markdown="1"><summary>Vérifier</summary>

Non. C'est de la connaissance, et une connaissance qui change chaque trimestre est la pire adéquation possible pour le fine-tuning, qui installe les faits de façon peu fiable et se périme aussitôt.

Récupération : exacte, citable, mise à jour en modifiant un catalogue. Le fine-tuning pourrait par ailleurs valoir la peine pour apprendre au bot à bien *utiliser* les données produit récupérées.

</details>

2. ▢ « Le prompting n'a pas marché. » Que demandez-vous ?

<details markdown="1"><summary>Vérifier</summary>

Ce qui a été mesuré, sur quel jeu held-out, avec quel score. Aussi : a-t-on essayé des exemples few-shot, un system prompt structuré, le décodage contraint pour un problème de format.

Sans référence pilotée par prompt et mesurée, il n'y a rien à quoi comparer un fine-tuning, donc vous ne pouvez pas démontrer une amélioration même si vous l'obtenez.

</details>

3. ▢ Tout votre problème est que 12 % des sorties sont du JSON invalide. Correctif le moins cher ?

<details markdown="1"><summary>Vérifier</summary>

Le décodage contraint. Une génération contrainte par une grammaire ne peut pas produire de JSON invalide, et c'est un changement côté service sans aucun entraînement.

Le fine-tuning pourrait atteindre 99 % de validité. Le décodage contraint atteint 100 % par construction. Ne faites du fine-tuning que si les *valeurs* sont aussi fausses, ce qui est un problème différent.

</details>

4. ▢ Quelle situation favorise le plus le fine-tuning ?

    - a) Le modèle ne connaît pas votre documentation interne
    - b) Un fort volume de requêtes avec un très long system prompt
    - c) Le modèle fait parfois des erreurs d'arithmétique dans la sortie
    - d) Le modèle a besoin d'informations sur des événements de cette semaine

<details markdown="1"><summary>Vérifier</summary>

**b)** Un fort volume de requêtes avec un très long system prompt.

Déplacer le contenu du prompt dans les poids supprime le coût de prefill à chaque requête, et l'économie évolue avec le volume. (a) et (d) relèvent de la récupération. (c) relève de l'usage d'outils : donnez-lui une calculatrice.

</details>

5. ▢ LoRA est-il un compromis par rapport au full fine-tuning ?

<details markdown="1"><summary>Vérifier</summary>

Largement non, dans le régime où la plupart des gens travaillent. Avec un rank suffisant sur toutes les couches linéaires et un learning rate réglé, LoRA égale le full fine-tuning sur les charges typiques de fine-tuning supervisé.

Le full fine-tuning reste approprié pour de très grands changements de comportement, un préentraînement continu à grande échelle, ou une recherche qui exige tout l'espace des paramètres. Pour une adaptation ordinaire à une tâche, les adapters sont la bonne méthode et non une concession.

</details>

6. ▢ Votre récupération fonctionne et le modèle ignore quand même le contexte récupéré et invente des réponses. Et maintenant ?

<details markdown="1"><summary>Vérifier</summary>

Maintenant le fine-tuning est bien motivé, et c'est l'architecture combinée plutôt qu'un choix entre approches.

Le problème est comportemental : s'ancrer dans le contexte fourni, le respecter, le citer, et refuser quand il est insuffisant. La récupération fournit les faits ; l'entraînement enseigne quoi en faire. Construisez le dataset à partir de vrais contextes récupérés avec des réponses ancrées correctes, y compris des cas où la bonne réponse est « le contexte fourni ne couvre pas cela ».

</details>

## Exercices en situation réelle

- [ ] Prenez une proposition de fine-tuning, la vôtre ou celle de quelqu'un d'autre, et appliquez-lui les trois questions. Rédigez un verdict d'un paragraphe.
- [ ] Mesurez correctement une référence pilotée par prompt sur votre jeu held-out. Notez le chiffre avant d'entraîner quoi que ce soit.
- [ ] Chiffrez toute la durée de vie d'un fine-tuning : données, évaluation, service, ré-entraînement, responsabilité. Comparez à l'économie.
- [ ] Demain : trouvez un cas où vous refuseriez de faire du fine-tuning, et écrivez l'argument en faveur de l'alternative dans un paragraphe qu'une autre personne pourrait mettre en œuvre.

## Pour aller plus loin

- [Doc : "LoRA Without Regret", Hugging Face TRL](https://huggingface.co/docs/trl/main/en/lora_without_regret)
- [Article : "Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks", Lewis et al., arXiv:2005.11401](https://arxiv.org/abs/2005.11401)
- [r/LocalLLaMA](https://www.reddit.com/r/LocalLLaMA/) : cherchez-y les cas où des praticiens ont décidé de ne pas faire de fine-tuning, et ce qu'ils ont livré à la place
- [Modes de défaillance](../reference/failure-modes.md), [Hyperparamètres de LoRA](../reference/lora-hyperparameters.md), [Budget mémoire](../reference/memory-budget.md)

---

Voilà le fil complet. À partir d'ici, le travail consiste en exercices sur de vraies tâches, et la dernière ligne de la mission est celle à retenir : savoir plaider de façon convaincante *contre* le fine-tuning, c'est ce qui donne de la valeur à l'argument *en sa faveur*.

Ça ne passe pas ? Relisez la source primaire en haut de page, car cette leçon la condense et c'est dans la condensation que la compréhension s'échappe. Consultez le [glossaire](../GLOSSARY.md) pour tout terme qui vous a paru glissant.

Si c'est la leçon elle-même qui n'est pas claire plutôt que la matière, c'est un défaut : [ouvrez une issue](https://github.com/TokenCemetery/teach/issues).
