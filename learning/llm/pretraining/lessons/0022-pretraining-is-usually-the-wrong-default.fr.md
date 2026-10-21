---
title: "22. Le pré-entraînement est souvent le mauvais choix par défaut"
description: "Une seconde phase de pré-entraînement sur un modèle existant obtient l'essentiel du bénéfice sans repayer le coût complet"
type: lesson
---

# Leçon 22. Le pré-entraînement est souvent le mauvais choix par défaut

**Lien avec la mission :** « Décider si une tâche donnée appelle un pré-entraînement, un pré-entraînement continu ou le fine-tuning d'un modèle de base existant, et défendre ce choix sur le coût » est le point d'Objectif que clôt l'étape 10. Cette leçon plaide contre le choix par défaut auquel la plupart des débutants recourent ; la leçon 23 couvre la défense d'un budget une fois que le pré-entraînement est réellement le bon choix, et la leçon 24 couvre la relecture de celui de quelqu'un d'autre.
**Source primaire :** [Article : "Don't Stop Pretraining: Adapt Language Models to Domains and Tasks", Gururangan et al., 2020](https://arxiv.org/abs/2004.10964)
**Prérequis :** [Leçon 21](0021-periodic-held-out-evaluation.md)

## Échauffement

1. ▢ Pourquoi Rae et al. ont-ils explicitement retiré certains benchmarks de l'ensemble d'entraînement de Gopher avant de les utiliser comme contrôles d'évaluation périodique ?

<details markdown="1"><summary>Vérifier</summary>

Pour qu'un bon score sur ces benchmarks ne puisse pas s'expliquer par le fait que le modèle ait simplement vu et mémorisé ce texte exact pendant l'entraînement ; un benchmark sur lequel le modèle a été entraîné ne peut pas distinguer une vraie capacité de la mémorisation.

</details>

2. ▢ Qu'apporte réellement à une équipe le fait d'évaluer périodiquement pendant l'entraînement plutôt qu'une seule fois à la fin ?

<details markdown="1"><summary>Vérifier</summary>

Cela permet d'attraper, et éventuellement de traiter, un bug, une régression ou une divergence des capacités pendant que le run est encore en cours, plutôt que de le découvrir seulement après que le budget de calcul complet est déjà dépensé.

</details>

## À savoir

### Pourquoi « il nous faut notre propre modèle pré-entraîné » est généralement le mauvais réflexe

Chaque étape de ce parcours a construit vers un fait honnête : pré-entraîner un modèle à partir de zéro est extraordinairement coûteux. L'arithmétique compute-optimal de l'étape 3 à elle seule, un modèle de 70 milliards de paramètres voulant de l'ordre de mille milliards de tokens, donne une idée de l'échelle de calcul qu'exige un seul run à partir de zéro, avant de compter le coût d'ingénierie de l'infrastructure d'entraînement distribué que couvraient les étapes 4 à 6, ou le coût opérationnel de la surveillance et de la tolérance aux pannes que couvraient les étapes 8 et 9. Vouloir un modèle bon dans un domaine précis, sur une tâche précise ou dans un style précis ne justifie pas, à soi seul, de payer de nouveau tout ce coût. La question à poser d'abord n'est pas « comment pré-entraînons-nous un modèle pour cela », mais « cela a-t-il vraiment besoin d'un nouveau modèle pré-entraîné ».

### La preuve d'une alternative moins chère

Gururangan et al. répondent directement à cela pour un cas courant : adapter un modèle pré-entraîné existant à large couverture à un domaine précis, plutôt que d'en pré-entraîner un nouveau pour ce domaine. Ils prennent RoBERTa, un grand modèle pré-entraîné existant, et poursuivent son pré-entraînement sur du texte non étiqueté d'un domaine cible, une **seconde phase de pré-entraînement** qu'ils appellent **pré-entraînement adaptatif au domaine (DAPT)**, avant d'évaluer sur des tâches de ce domaine. Sur quatre domaines (articles biomédicaux, articles d'informatique, actualités et avis) et huit tâches de classification, ils constatent que cela améliore systématiquement les performances sur les tâches du domaine cible, dans des contextes riches comme pauvres en ressources, chaque fois que le domaine cible n'était pas déjà bien représenté dans le pré-entraînement d'origine du modèle. Ils constatent en outre que s'adapter davantage aux propres données non étiquetées d'une tâche, le **pré-entraînement adaptatif à la tâche (TAPT)**, améliore encore les performances par-dessus le DAPT, et que même une alternative moins chère, l'adaptation à un corpus de tâche construit avec de simples heuristiques de sélection de données, fonctionne bien quand un pré-entraînement adaptatif au domaine complet n'est pas abordable.

### Ce que cela plaide, et ce que cela ne plaide pas

Rien de tout cela ne prétend que pré-entraîner à partir de zéro n'est jamais justifié ; cela prétend que l'hypothèse par défaut devrait aller dans l'autre sens. Poursuivre le pré-entraînement d'un modèle existant, déjà largement capable, pour une petite fraction du calcul qu'exigerait un run à partir de zéro, capte systématiquement une vraie part du bénéfice qu'aurait pu offrir un modèle entièrement spécifique au domaine. Une tâche qui semble appeler « un modèle bon dans notre domaine » est, d'après cette preuve, très souvent mieux servie par un pré-entraînement continu sur un modèle de base existant, ou, si la tâche est encore plus étroite, par le fine-tuning avec adapters que couvre `llm/finetuning`, que par le paiement d'un nouveau run de pré-entraînement. Recourir au pré-entraînement complet avant d'avoir écarté ces options moins chères est l'erreur précise contre laquelle plaide cette leçon, la version à l'échelle du pré-entraînement de la même discipline que la leçon de jugement de `llm/finetuning` applique un niveau plus bas, quand le fine-tuning avec adapters lui-même n'est pas non plus le bon choix.

### Quand pré-entraîner à partir de zéro reste le bon choix

Les cas où c'est réellement le bon choix comprennent : une langue ou un domaine cible si éloigné des données d'entraînement et du tokenizer de tout modèle de base disponible qu'aucune quantité de pré-entraînement continu ou de fine-tuning ne peut combler l'écart ; une exigence de licence ou de provenance qui écarte les données d'entraînement de tous les modèles de base disponibles ; ou un changement d'architecture délibéré (les choix de parallélisme de l'étape 6, un mécanisme d'attention fondamentalement différent) dans lequel un checkpoint existant ne peut pas être adapté après coup. Ce sont l'exception que cette leçon attend d'un lecteur qu'il sache nommer, pas la règle.

## Pratique

1. ▢ Une équipe veut un modèle qui réussit bien sur des documents juridiques, et un modèle de base existant à large couverture est disponible. D'après la preuve de Gururangan et al., que recommanderait cette leçon d'essayer avant de pré-entraîner un nouveau modèle à partir de zéro ?

<details markdown="1"><summary>Vérifier</summary>

Le pré-entraînement adaptatif au domaine : poursuivre le pré-entraînement du modèle de base existant sur du texte juridique non étiqueté, ce qui, selon Gururangan et al., améliore systématiquement les performances sur le domaine cible dans des contextes riches comme pauvres en ressources, pour une fraction du coût d'un nouveau run de pré-entraînement à partir de zéro.

</details>

2. ▢ Laquelle de ces raisons est une raison légitime de pré-entraîner quand même à partir de zéro, d'après cette leçon ?

    - a) Le domaine cible est légèrement différent du texte web général
    - b) Le tokenizer ou les données d'entraînement d'aucun modèle de base disponible ne couvrent du tout la langue ou le domaine cible, et le pré-entraînement continu ne peut pas combler cet écart
    - c) Un nouveau run de pré-entraînement ferait plus d'effet dans un rapport
    - d) Le fine-tuning prendrait plus d'une journée à mettre en place

<details markdown="1"><summary>Vérifier</summary>

**b)** est la vraie exception que nomme cette leçon. (a) est exactement le cas que la preuve de Gururangan et al. soutient que le pré-entraînement continu gère bien, pas une raison de pré-entraîner à partir de zéro. (c) et (d) ne sont pas des raisons défendables au regard de l'argument de coût de cette leçon.

</details>

3. ▢ Quelle est la différence entre le pré-entraînement adaptatif au domaine (DAPT) et le pré-entraînement adaptatif à la tâche (TAPT), d'après Gururangan et al. ?

<details markdown="1"><summary>Vérifier</summary>

Le DAPT poursuit le pré-entraînement sur du texte non étiqueté d'un large domaine cible (comme tous les articles biomédicaux). Le TAPT poursuit le pré-entraînement spécifiquement sur les propres données non étiquetées d'une tâche donnée, un corpus plus étroit, et Gururangan et al. ont constaté qu'il améliore les performances même après que le DAPT a déjà été appliqué.

</details>

4. ▢ Une équipe ne peut pas se permettre un run complet de pré-entraînement adaptatif au domaine mais veut quand même une partie de son bénéfice. Quelle alternative le travail de Gururangan et al. suggère-t-il ?

<details markdown="1"><summary>Vérifier</summary>

S'adapter à un corpus de tâche construit avec de simples stratégies de sélection de données, ce que Gururangan et al. ont trouvé être une alternative efficace et moins chère quand les ressources pour un pré-entraînement adaptatif au domaine complet ne sont pas disponibles.

</details>

## Exercices en situation réelle

- [ ] Trouvez un exemple publié de modèle adapté à un domaine (une model card ou un article de « BioBERT », « SciBERT », « FinBERT » ou similaire) et identifiez s'il a été construit par pré-entraînement continu sur un modèle de base existant ou pré-entraîné entièrement à partir de zéro.
- [ ] Lisez l'introduction de Gururangan et al. (liée plus haut) et écrivez une phrase sur la raison pour laquelle ils ont spécifiquement choisi de tester le pré-entraînement adaptatif au domaine sur plusieurs domaines, plutôt que sur un seul, avant de tirer une conclusion générale.
- [ ] Demain : pour un domaine ou une tâche cible hypothétique de votre choix, écrivez un paragraphe qui plaide pour ou contre le pré-entraînement d'un nouveau modèle à partir de zéro, en citant au moins un élément de preuve de cette leçon ou d'une étape antérieure de ce parcours.

## Pour aller plus loin

- [Article : "Don't Stop Pretraining: Adapt Language Models to Domains and Tasks", Gururangan et al., 2020](https://arxiv.org/abs/2004.10964)
- [`llm/finetuning`](../../finetuning/) : la même discipline appliquée un niveau plus bas, une fois que le pré-entraînement continu reste plus que ce dont une tâche plus étroite a besoin
- [Ressources](../RESOURCES.md)

---

Ça ne passe pas ? Relisez la source primaire en haut de page, car cette leçon la condense et c'est dans la condensation que la compréhension s'échappe. Consultez le [glossaire](../GLOSSARY.md) pour tout terme qui vous a paru glissant.

Si c'est la leçon elle-même qui n'est pas claire plutôt que la matière, c'est un défaut : [ouvrez une issue](https://github.com/TokenCemetery/teach/issues).
