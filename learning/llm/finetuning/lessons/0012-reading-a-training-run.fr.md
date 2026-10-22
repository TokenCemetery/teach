---
title: "12. Lire un run d'entraînement"
description: "Diagnostiquer d'après la forme de la courbe, et ce que la loss ne peut pas voir"
type: lesson
---

# Leçon 12. Lire un run d'entraînement

**Lien avec la mission :** « Diagnostiquer un run raté et en nommer la cause » figure sur la liste de la réussite. La plupart des gens lisent une courbe de loss et devinent.
**Source primaire :** [Blog : "A Recipe for Training Neural Networks", Andrej Karpathy](https://karpathy.github.io/2019/04/25/recipe/)
**Prérequis :** [Leçon 11](0011-your-first-adapter.md)

## Échauffement

1. ▢ Nommez les quatre vérifications à faire avant de se soucier de la courbe de loss.

<details markdown="1"><summary>Vérifier</summary>

Confirmer que l'adapter s'est attaché ; décoder un vrai exemple d'entraînement et compter les positions notées ; confirmer que la loss bouge ; confirmer que le pipeline peut surapprendre deux exemples.

</details>

2. ▢ Pourquoi noter la révision du base model à côté de l'adapter ?

<details markdown="1"><summary>Vérifier</summary>

Un adapter est un diff par rapport à des poids précis. Sans le base model exact, il est inutilisable, et un base model presque identique dégrade la qualité silencieusement.

</details>

3. ▢ Octets par paramètre gelé contre par paramètre entraînable ?

<details markdown="1"><summary>Vérifier</summary>

Deux contre seize.

</details>

## À savoir

### La loss d'entraînement seule ne vous dit presque rien

Une loss d'entraînement qui baisse signifie que le modèle s'ajuste aux données qu'il peut voir. Cela est compatible avec un modèle qui apprend la tâche comme avec un modèle qui mémorise le jeu d'entraînement. **Il vous faut un découpage held-out pour les distinguer, et il n'y a pas de substitut.**

Mettez-en un de côté avant de commencer :

```python
split = dataset.train_test_split(test_size=0.05, seed=0)
args = SFTConfig(..., eval_strategy="steps", eval_steps=50)
trainer = SFTTrainer(..., train_dataset=split["train"], eval_dataset=split["test"])
```

### Les formes et ce qu'elles signifient

| Loss d'entraînement | Loss held-out | Diagnostic | Action |
|---|---|---|---|
| Baisse | Baisse | Apprentissage | Continuer |
| Baisse | S'aplatit puis monte | Surapprentissage à partir du tournant | S'arrêter au minimum ; plus de données ou moins de capacité |
| Tombe vers ~0 vite | Monte aussitôt | Mémorisation | Dataset beaucoup trop petit pour cette capacité |
| S'aplatit haut | S'aplatit haut | Sous-apprentissage | Plus de rank, plus de target modules, learning rate plus élevé |
| Plate dès le pas 1 | Plate | Pipeline cassé | Les quatre vérifications de la leçon 11 |
| Pics, ou `NaN` | sans objet | Instabilité | Baisser le learning rate ; vérifier un débordement en fp16 ; ajouter un warm-up |

Le **minimum du held-out** est le checkpoint utile, pas le dernier pas. Sauvegardez des checkpoints périodiquement et gardez le meilleur ; un run qui se termine au pas 1000 alors que la loss held-out a atteint son creux au pas 400 a entraîné 600 pas de dégâts.

### Diagnostiquer d'après la forme, plus finement

**Un plancher de loss qu'un entraînement supplémentaire n'abaissera pas** est un plafond de capacité. L'adapter ne peut pas exprimer la mise à jour dont la tâche a besoin. Ajouter des epochs ne peut pas y remédier ; ajouter du rank ou des target modules le peut.

**Une loss qui pique puis se rétablit** correspond généralement à un batch qui contient quelque chose d'inhabituel : un exemple de longueur aberrante, du texte corrompu, un bloc dupliqué. Trouvez-le. Un seul exemple pathologique peut faire bouger un run sur petit dataset.

**Une loss qui devient `NaN`** est un débordement. En fp16, c'est courant et c'est ce que le loss scaling est censé prévenir ; en bf16, cela indique généralement quelque chose de pire, comme une division par zéro dans le pipeline de données ou un learning rate assez élevé pour envoyer des poids à l'infini.

**Une loss qui baisse en escalier net** avec des marches aux frontières d'epoch signifie que le modèle reconnaît des exemples qu'il a déjà vus. C'est de la mémorisation qui apparaît directement dans la courbe.

### Ce que la loss ne peut pas voir du tout

C'est la partie importante de la leçon.

L'entropie croisée note la prédiction du token suivant sur votre distribution de données. Elle est muette sur :

- **L'utilisabilité des générations.** Un modèle peut bien noter et produire une sortie qui ne s'arrête jamais, ou qui ignore le format demandé.
- **Le fait que quelque chose d'autre se soit cassé.** [L'oubli catastrophique](../GLOSSARY.md), la dégradation de capacités sans rapport avec votre tâche, n'apparaît pas du tout dans la loss de votre tâche. Votre loss held-out peut s'améliorer de façon monotone pendant que le modèle devient moins bon dans tout ce qu'il savait faire d'autre.
- **Le fait que l'amélioration soit réelle ou due à de la contamination.** Si vos exemples held-out sont des quasi-doublons d'exemples d'entraînement, la loss held-out mesure de la mémorisation et l'appelle de la généralisation.

Donc : **générez, à chaque fois.** Fixez un petit ensemble de prompts avant l'entraînement. Faites-les passer dans le base model et sauvegardez les sorties. Faites-les passer dans le modèle adapté avec les mêmes réglages d'échantillonnage et comparez. Dix minutes passées à lire de vraies générations attrapent des choses qu'aucune métrique sur votre courbe n'attrapera.

```python
PROBES = [
    "<a representative task prompt>",
    "<an edge case you care about>",
    "<something unrelated to the task, to check for forgetting>",
]
```

Cette troisième catégorie est celle que les gens omettent, et c'est ainsi que l'oubli est livré.

### Reproductibilité

Journalisez assez pour pouvoir relancer : base model et révision, dataset et son découpage exact, seed, chaque hyperparamètre, et versions des bibliothèques. Le fine-tuning avec adapter a une surface de configuration assez grande pour que « je crois que c'était un rank de 32 » ne soit pas un enregistrement.

Comparer deux runs n'a de sens que lorsqu'exactement une chose diffère entre eux. Changez le rank *ou* le learning rate, pas les deux, et gardez la seed et les données fixes. Cela semble évident et est régulièrement violé, généralement parce qu'un run a duré assez longtemps pour rendre la patience coûteuse.

## Pratique

1. ▢ La loss d'entraînement est de 0.2 et baisse. La loss held-out a atteint son creux à 0.9 il y a deux cents pas et vaut maintenant 1.1. Que se passe-t-il, et quel checkpoint livrez-vous ?

<details markdown="1"><summary>Vérifier</summary>

Du surapprentissage. Le modèle s'ajuste maintenant à du bruit propre au jeu d'entraînement.

Livrez le checkpoint du minimum du held-out, environ deux cents pas en arrière. Puis réduisez la capacité, ajoutez des données, ou arrêtez plus tôt la prochaine fois.

</details>

2. ▢ Les deux loss s'aplatissent à un niveau trop élevé pour être utile. Rank 8, cibles limitées à l'attention. Que changez-vous, et que ne changez-vous pas ?

<details markdown="1"><summary>Vérifier</summary>

Changez la capacité : étendez les cibles à toutes les couches linéaires, et augmentez le rank. Demandez-vous si le learning rate est trop bas.

N'ajoutez pas d'epochs. Un plafond de capacité ne bouge pas avec davantage de passages sur les mêmes données. C'est la définition du diagnostic.

</details>

3. ▢ La loss held-out s'améliore tout du long. Vous livrez. Les utilisateurs signalent que le modèle est devenu moins bon sur des choses qu'il savait faire. Qu'avez-vous omis de mesurer ?

<details markdown="1"><summary>Vérifier</summary>

L'oubli catastrophique. Votre jeu held-out est tiré de la distribution de votre tâche, donc il ne peut pas voir la dégradation de capacités extérieures à cette distribution.

Le correctif est un jeu de régression qui couvre des capacités que vous n'entraînez pas : suivi d'instructions général, comportement de refus, autres formats. C'est la leçon 24, et cette défaillance est la raison de son existence.

</details>

4. ▢ Quelle observation indique le plus fortement un pipeline cassé plutôt que de mauvais hyperparamètres ?

    - a) La courbe de loss plafonne à une valeur bien supérieure à zéro
    - b) La loss est exactement inchangée sur les cinquante pas
    - c) La loss held-out monte pendant que la loss d'entraînement baisse
    - d) La loss pique vers le haut à un pas puis se rétablit

<details markdown="1"><summary>Vérifier</summary>

**b)** La loss est exactement inchangée sur les cinquante pas.

Un plateau, c'est du sous-apprentissage, une paire qui diverge, c'est du surapprentissage, et un pic est généralement un seul mauvais batch : ce sont tous de vrais comportements d'entraînement. Une loss qui ne bouge *pas du tout* signifie qu'aucun gradient n'atteint aucun paramètre, ce qui est une panne de câblage.

</details>

5. ▢ Pourquoi au moins l'une de vos sondes de génération doit-elle être sans rapport avec la tâche ?

<details markdown="1"><summary>Vérifier</summary>

Parce que c'est la seule manière bon marché de repérer l'oubli pendant un run. Les sondes liées à la tâche et la loss held-out liée à la tâche s'améliorent toutes deux pendant que les capacités sans rapport se dégradent, donc rien de ce que vous mesurez déjà ne vous avertira.

</details>

6. ▢ La loss baisse en escalier avec des chutes à chaque frontière d'epoch. Diagnostiquez.

<details markdown="1"><summary>Vérifier</summary>

Le modèle reconnaît des exemples qu'il a déjà vus. C'est de la mémorisation, visible directement dans la courbe. Chaque nouvel epoch produit une marche vers le bas parce que les données ne sont plus nouvelles.

Vérifiez la loss held-out, probablement plate ou en hausse, et réduisez les epochs ou la capacité.

</details>

## Exercices en situation réelle

- [ ] Ajoutez un découpage held-out et une évaluation périodique à votre run de la leçon 11. Trouvez le minimum du held-out.
- [ ] Écrivez trois sondes de génération, dont une sans rapport avec votre tâche. Sauvegardez les sorties du base model avant l'entraînement.
- [ ] Surapprenez délibérément : entraînez un adapter à rank généreux sur 50 exemples pendant de nombreux epochs et regardez les deux courbes se séparer. Gardez le graphique.
- [ ] Demain : rédigez une fiche de run d'une page pour un vrai run : base model, révision, données, découpage, seed, chaque hyperparamètre, versions des bibliothèques.

## Pour aller plus loin

- [Blog : "A Recipe for Training Neural Networks", Andrej Karpathy](https://karpathy.github.io/2019/04/25/recipe/)
- [Modes de défaillance](../reference/failure-modes.md)
- [Leçon 24. Le jeu de régression](0024-the-regression-suite.md) : là où la sonde sans rapport devient un vrai système

---

Ça ne passe pas ? Relisez la source primaire en haut de page, car cette leçon la condense et c'est dans la condensation que la compréhension s'échappe. Consultez le [glossaire](../GLOSSARY.md) pour tout terme qui vous a paru glissant.

Si c'est la leçon elle-même qui n'est pas claire plutôt que la matière, c'est un défaut : [ouvrez une issue](https://github.com/TokenCemetery/teach/issues).
