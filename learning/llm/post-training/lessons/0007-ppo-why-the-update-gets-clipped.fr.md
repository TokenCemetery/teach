---
title: "7. PPO : pourquoi la mise à jour est clippée"
description: "Un gros gain sur un batch de données échantillonnées n'est pas une preuve fiable pour faire un gros pas ; PPO refuse d'y croire entièrement"
type: lesson
---

# Leçon 7. PPO : pourquoi la mise à jour est clippée

**Lien avec la mission :** Dériver l'objectif RLHF (leçon 6) ne vaut pas grand-chose sans savoir ce que fait réellement « optimiser la policy contre lui avec PPO ». Cette leçon fournit ce mécanisme, dont le reste de l'étape 4 et l'étape de jugement de la mission dépendent : il faut pouvoir le nommer concrètement plutôt que le traiter comme une boîte noire.
**Source primaire :** [Article : "Proximal Policy Optimization Algorithms", Schulman et al., 2017](https://arxiv.org/abs/1707.06347)
**Prérequis :** [Leçon 6](0006-the-rlhf-objective-reward-minus-a-kl-penalty.md)

## Échauffement

1. ▢ Dans l'objectif RLHF, que devient la policy quand le coefficient de pénalité KL `β` tend vers zéro ?

<details markdown="1"><summary>Vérifier</summary>

La pénalité pour s'écarter de la policy SFT disparaît presque, si bien que l'objectif se réduit à poursuivre le score du reward model avec presque rien pour retenir la policy, ce qui l'expose au reward hacking que décrivait la leçon 5.

</details>

2. ▢ Quelle différence y a-t-il entre « PPO » et « PPO-ptx » dans la nomenclature d'Ouyang et al., et quel terme les distingue ?

<details markdown="1"><summary>Vérifier</summary>

« PPO » fixe à 0 le coefficient de gradient de pré-entraînement `γ` ; « PPO-ptx » utilise un `γ` non nul, ce qui mélange à l'entraînement des gradients de log-vraisemblance des données de pré-entraînement, et c'est ce qui réduit la taxe d'alignement.

</details>

## À savoir

### Le problème d'une mise à jour sans contrainte

Schulman et al. partent d'un objectif de substitution (surrogate) plus simple, que maximiserait directement une méthode de policy gradient « vanille » : `L^CPI(θ) = E[r_t(θ) · Â_t]`, où `r_t(θ) = policy(a|s) / policy_old(a|s)` est le rapport entre la probabilité de l'action effectivement choisie sous la nouvelle policy et sous l'ancienne, et `Â_t` est l'**avantage** estimé, en gros de combien cette action s'est révélée meilleure ou pire que prévu. Maximiser `L^CPI` sans autre contrainte donne à l'optimiseur tout intérêt à pousser `r_t(θ)` aussi loin que possible dans la direction qui augmente l'objectif. Schulman et al. énoncent directement le problème : « sans contrainte, la maximisation de `L^CPI` conduirait à une mise à jour de la policy excessivement grande ». Un grand avantage estimé sur un batch échantillonné n'est pas une preuve fiable qu'un pas tout aussi grand est sûr partout ; y réagir de façon excessive peut déstabiliser l'entraînement.

### La solution de PPO : clipper le rapport, puis prendre le cas pessimiste

L'objectif réel de Schulman et al. est :

```text
L^CLIP(θ) = E[ min( r_t(θ)·Â_t, clip(r_t(θ), 1-ε, 1+ε)·Â_t ) ]
```

avec `ε` une petite constante (ils utilisent `0.2`). Le terme `clip(...)` borne le rapport `r_t(θ)` à l'intervalle `[1-ε, 1+ε]`, ce qui supprime l'intérêt de le pousser plus loin hors de cette plage. Prendre le `min` des versions clippée et non clippée, plutôt que la version clippée seule, est ce qui en fait une **borne pessimiste** : Schulman et al. expliquent que ce schéma « n'ignore le changement du rapport de probabilités que lorsqu'il ferait s'améliorer l'objectif, et l'inclut lorsqu'il l'aggrave ». En clair, un mouvement qui semble aider est plafonné plutôt que pleinement récompensé, si bien que l'optimiseur ne peut pas tirer un crédit illimité d'un batch encourageant, tandis qu'un mouvement qui fait réellement du mal n'est pas protégé par le même plafond, et son coût entier compte toujours.

### Pourquoi c'est un autre type de contrôle de stabilité que la pénalité KL

La pénalité KL de la leçon 6 et le clipping de cette leçon sont tous deux des mécanismes de stabilité, mais ils opèrent à des échelles différentes et ne doivent pas être confondus. La pénalité KL mesure la policy entraînée par rapport au **modèle de référence SFT** d'origine, figé, et limite la distance dont tout le run d'entraînement a le droit de dériver de ce point fixe sur toute sa durée. Le clipping de PPO compare la policy à **elle-même juste avant la mise à jour en cours** (`policy_old`), et limite la taille de chaque pas d'optimisation individuel, quelle que soit la position actuelle de la policy par rapport au modèle SFT. L'un contrôle la dérive totale sur le run ; l'autre contrôle la taille de chaque pas en chemin. Les deux sont nécessaires, et aucun ne remplace l'autre : un petit clip par pas n'empêche pas de nombreux petits pas de finir par dériver loin du modèle de référence, et une pénalité KL contre le modèle de référence ne fait rien pour empêcher un pas isolé d'être destructivement grand.

## Pratique

1. ▢ Un seul batch de complétions échantillonnées produit un avantage estimé exceptionnellement grand pour une action, uniquement à cause de la façon dont ce batch a été échantillonné. Pourquoi est-il risqué de laisser la policy se mettre à jour entièrement en proportion de cet avantage, sans plafond ?

<details markdown="1"><summary>Vérifier</summary>

Parce que l'avantage estimé d'un seul batch n'est pas une preuve fiable qu'un changement tout aussi grand est sûr partout ; réagir de façon excessive à un seul échantillon encourageant (ou décourageant) peut pousser la policy à une distance excessive en un seul pas, ce qui est exactement l'instabilité que le clipping de PPO est conçu pour empêcher.

</details>

2. ▢ Pourquoi PPO prend-il le minimum des termes de substitution clippé et non clippé, plutôt que d'utiliser le terme clippé seul ?

    - a) Prendre le minimum fait de l'objectif une borne pessimiste : un mouvement qui semble une amélioration est plafonné, tandis qu'un mouvement qui semble nuisible n'est pas protégé par le même plafond et compte toujours pleinement
    - b) Le minimum n'est utilisé que pour l'efficacité de calcul et n'a aucun effet sur la policy apprise
    - c) Utiliser le terme clippé seul laisserait le rapport non borné
    - d) Le minimum garantit que le rapport vaut toujours exactement 1

<details markdown="1"><summary>Vérifier</summary>

**a)** est le raisonnement énoncé par Schulman et al. eux-mêmes. (b) sous-estime un effet réel sur le comportement de l'optimisation. (c) prend à l'envers le but réel du clipping ; le clipping borne le rapport, il ne le laisse pas non borné. (d) interprète mal ce que fait le clipping ; le rapport est borné à un intervalle autour de 1, pas forcé à valoir exactement 1.

</details>

3. ▢ Le montage RLHF d'une équipe utilise un grand coefficient de pénalité KL `β` mais aucun clipping par pas (un objectif de substitution non clippé). Ce montage est-il protégé contre une mise à jour de policy isolée et destructivement grande ?

<details markdown="1"><summary>Vérifier</summary>

Non. Un grand `β` limite la distance dont la policy peut dériver du modèle de référence SFT au fil de l'entraînement, mais ne fait rien pour empêcher qu'une mise à jour isolée, fondée sur l'avantage estimé d'un seul batch, soit excessivement grande. Ce sont deux contrôles de stabilité différents, et retirer l'un n'est pas compensé par l'autre.

</details>

## Exercices en situation réelle

- [ ] Trouvez où une implémentation de PPO à laquelle vous avez accès expose le paramètre de clip (souvent nommé `epsilon`, `clip_range` ou équivalent), et notez sa valeur par défaut en la comparant au `0.2` que Schulman et al. disent utiliser.
- [ ] Lisez le paragraphe de l'article PPO (lié plus haut) qui décrit pourquoi `L^CPI` seul conduirait à une mise à jour excessivement grande, et écrivez une phrase avec vos propres mots expliquant ce qui, précisément, dans un objectif de substitution sans contrainte cause cela.
- [ ] Demain : sans regarder la suite, écrivez une prédiction d'une phrase pour la leçon 8 : sachant que RLHF a maintenant besoin d'une policy, d'un modèle de référence (SFT) figé pour la pénalité KL, d'un reward model et de quelque chose qui produise les estimations d'avantage dont dépend la formule de clipping de cette leçon, combien de grands modèles distincts attendez-vous à voir impliqués dans un seul pas d'entraînement PPO ?

## Pour aller plus loin

- [Article : "Proximal Policy Optimization Algorithms", Schulman et al., 2017](https://arxiv.org/abs/1707.06347)
- [Ressources](../RESOURCES.md)

---

Ça ne passe pas ? Relisez la source primaire en haut de page, car cette leçon la condense et c'est dans la condensation que la compréhension s'échappe. Consultez le [glossaire](../GLOSSARY.md) pour tout terme qui vous a paru glissant.

Si c'est la leçon elle-même qui n'est pas claire plutôt que la matière, c'est un défaut : [ouvrez une issue](https://github.com/TokenCemetery/teach/issues).
