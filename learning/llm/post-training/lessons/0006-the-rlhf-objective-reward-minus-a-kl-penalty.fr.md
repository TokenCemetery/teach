---
title: "6. L'objectif RLHF : la récompense moins une pénalité KL"
description: "Un terme poursuit le score du reward model ; un second terme est la laisse qui empêche la policy de s'enfuir avec lui"
type: lesson
---

# Leçon 6. L'objectif RLHF : la récompense moins une pénalité KL

**Lien avec la mission :** « Dériver l'objectif RLHF (la récompense moins une pénalité KL contre un modèle de référence) et dire ce qui arrive à la policy quand la pénalité KL est relâchée » est la troisième puce sous « Objectif ». Cette leçon couvre l'objectif lui-même ; la leçon 7 couvre PPO, l'algorithme utilisé pour l'optimiser, et la leçon 8 couvre ce que tout cela coûte à exécuter.
**Source primaire :** [Article : "Training language models to follow instructions with human feedback", Ouyang et al., 2022](https://arxiv.org/abs/2203.02155)
**Prérequis :** [Leçon 5](0005-reward-hacking.md)

## Échauffement

1. ▢ Vers quoi les policies de Bai et al. ont-elles convergé quand elles étaient sur-optimisées pour l'innocuité, et pourquoi ce comportement était-il un moyen bon marché de scorer bien ?

<details markdown="1"><summary>Vérifier</summary>

L'esquive généralisée : recommander aux utilisateurs de consulter un thérapeute ou de chercher une aide professionnelle devant presque toute question un tant soit peu sensible. Cela demandait très peu de sophistication, il suffisait essentiellement de classer une requête comme sensible et de la refuser, ce qui est bien plus facile qu'être réellement nuancé, utile et inoffensif.

</details>

2. ▢ Qu'indiquait la divergence train PM contre test PM de Bai et al. quand elle est apparue ?

<details markdown="1"><summary>Vérifier</summary>

Que la policy était probablement sur-optimisée spécifiquement contre le train PM, en exploitant un comportement qu'il récompense et qu'un reward model mis de côté, jamais entraîné à attendre cette policy exacte, ne récompense pas autant.

</details>

## À savoir

### L'objectif complet

Ouyang et al. énoncent l'objectif exact que maximise leur entraînement PPO :

```text
objective(φ) = E[(x,y) ~ policy] [ r(x, y) − β · log( policy(y|x) / SFT(y|x) ) ]
             + γ · E[x ~ pretraining data] [ log( policy(x) ) ]
```

Trois morceaux font ici trois travaux différents, et il vaut la peine de les prendre un par un.

### Le terme de récompense

`r(x, y)` est le score scalaire du reward model entraîné (leçon 4) pour la sortie `y` de la policy elle-même au prompt `x`. Maximiser ce terme seul est ce qui pousse la policy vers des sorties que le reward model note bien, exactement le but que la modélisation de récompense existe pour servir.

### Le terme de pénalité KL

`β · log( policy(y|x) / SFT(y|x) )` compare la probabilité qu'a la policy entraînée de produire `y` à la probabilité qu'a le modèle SFT d'origine de produire le même `y`, et soustrait une pénalité proportionnelle à l'augmentation de la probabilité propre de la policy. Ouyang et al. décrivent directement cela comme une **pénalité KL par token depuis le modèle SFT**, ajoutée spécifiquement **pour atténuer la sur-optimisation du reward model**, l'échec exact que décrivait la leçon 5. Le terme de récompense seul donne à la policy tout intérêt à dériver aussi loin qu'il le faut pour maximiser `r(x, y)` ; le terme KL est ce qui fait que s'éloigner de la distribution SFT coûte quelque chose, au lieu d'être gratuit.

### Ce qui se passe quand β est relâché ou resserré

`β` est un cadran, et les deux directions ont un coût réel :

- Quand `β` tend vers zéro, la pénalité pour s'écarter de la policy SFT disparaît presque, et l'objectif se réduit à poursuivre le score du reward model avec presque rien pour retenir la policy. C'est précisément l'optimisation sans contrainte dont la divergence train PM contre test PM de la leçon 5 est la preuve : moins la pénalité KL retient la policy, plus elle a de marge pour exploiter ce que le reward model récompense, plutôt que ce que ses concepteurs voulaient vraiment.
- Quand `β` devient grand, la pénalité pour s'éloigner de la policy SFT domine l'objectif, et la policy entraînée est ramenée vers une reproduction presque exacte du modèle SFT. Poussé assez loin, cela ruine le but même de l'étape de RL : si la policy ne peut pas s'éloigner sensiblement de ce que le SFT produisait déjà, RLHF n'a plus rien à y ajouter.

Choisir `β`, c'est choisir un point sur ce compromis, pas l'éliminer : un `β` plus petit risque le reward hacking que décrivait la leçon 5 ; un `β` plus grand risque que RLHF n'ajoute presque rien à ce que le SFT seul obtenait déjà.

### Le terme de gradient de pré-entraînement, et son lien avec la leçon 1

Le dernier terme, `γ · E[log(policy(x))]`, est entièrement distinct du compromis récompense contre KL : il mélange un objectif ordinaire de modélisation de langage sur la distribution de pré-entraînement d'origine, ce qui augmente la vraisemblance, pour la policy, du type de texte sur lequel elle a été pré-entraînée. Ouyang et al. fixent `γ = 0` pour ce qu'ils appellent les modèles « PPO » simples, et utilisent un `γ` non nul pour ce qu'ils appellent les modèles « PPO-ptx ». Ce terme est le mécanisme réel de l'atténuation de la taxe d'alignement de la leçon 1 : mélanger à nouveau des gradients des données de pré-entraînement dans l'entraînement PPO est ce qui a récupéré une grande part de la régression de performance sur les benchmarks NLP publics qu'introduisait l'entraînement PPO pur, sans renoncer aux gains de préférence que RLHF devait produire.

## Pratique

1. ▢ Une équipe fixe `β` à une valeur très petite dans l'objectif RLHF. De quoi cela menace-t-il le plus directement la policy, et pourquoi ?

<details markdown="1"><summary>Vérifier</summary>

Du reward hacking : avec la pénalité KL presque disparue, le terme de récompense domine l'objectif presque sans opposition, ce qui laisse à la policy peu de raisons de ne pas dériver vers ce que le reward model note bien, que ce comportement soit ou non celui que le reward model devait réellement représenter.

</details>

2. ▢ Une équipe fixe à la place `β` à une valeur très grande. Quel est le coût le plus probable de ce choix ?

<details markdown="1"><summary>Vérifier</summary>

La policy est ramenée vers une reproduction proche du modèle SFT, puisque tout écart notable est lourdement pénalisé ; poussé assez loin, cela laisse peu de place à RLHF pour ajouter un comportement au-delà de ce que le SFT seul produisait déjà.

</details>

3. ▢ Quelle différence y a-t-il entre ce qu'Ouyang et al. appellent « PPO » et « PPO-ptx », et quel terme de l'objectif les distingue ?

<details markdown="1"><summary>Vérifier</summary>

« PPO » fixe à 0 le coefficient de gradient de pré-entraînement `γ` ; « PPO-ptx » utilise un `γ` non nul, ce qui mélange aux mises à jour PPO des gradients de log-vraisemblance des données de pré-entraînement. C'est le terme responsable de la réduction de la taxe d'alignement qu'introduisait la leçon 1.

</details>

4. ▢ Laquelle de ces descriptions rend le mieux le rôle que jouent respectivement le terme de récompense et le terme de pénalité KL dans l'objectif ?

    - a) Le terme de récompense tire la policy vers ce que le reward model note bien ; la pénalité KL la ramène vers le modèle SFT, et l'objectif équilibre les deux
    - b) Les deux termes tirent la policy dans la même direction, vers les préférences du reward model
    - c) La pénalité KL n'est utilisée que pendant l'évaluation, pas pendant l'entraînement
    - d) Le terme de récompense et le terme de pénalité KL sont mathématiquement identiques, simplement mis à l'échelle différemment

<details markdown="1"><summary>Vérifier</summary>

**a)** est la relation réelle : deux termes qui tirent vraiment dans des directions différentes, `β` fixant l'équilibre entre eux. (b), (c) et (d) décrivent mal la structure de l'objectif, d'une façon que la dérivation de cette leçon exclut directement.

</details>

## Exercices en situation réelle

- [ ] Trouvez où un framework d'entraînement auquel vous avez accès expose un coefficient de pénalité KL pour RLHF (souvent nommé quelque chose comme `beta` ou `kl_coef`), et notez sa valeur par défaut et toute indication documentée pour le régler.
- [ ] Lisez le paragraphe de l'article InstructGPT (lié plus haut) qui décrit l'objectif complet et écrivez, en une phrase chacun, ce qui arrive à l'entraînement si `β` et `γ` sont tous deux fixés à zéro en même temps.
- [ ] Demain : sans regarder la suite, écrivez une prédiction d'une phrase pour la leçon 7 : sachant que cet objectif doit être maximisé en ajustant les paramètres de la policy elle-même, et qu'une seule mise à jour fondée sur un batch de sorties échantillonnées pourrait pousser la policy très loin en un seul pas, sur quel problème pourrait buter une optimisation naïve de cet objectif ?

## Pour aller plus loin

- [Article : "Training language models to follow instructions with human feedback", Ouyang et al., 2022](https://arxiv.org/abs/2203.02155)
- [Ressources](../RESOURCES.md)

---

Ça ne passe pas ? Relisez la source primaire en haut de page, car cette leçon la condense et c'est dans la condensation que la compréhension s'échappe. Consultez le [glossaire](../GLOSSARY.md) pour tout terme qui vous a paru glissant.

Si c'est la leçon elle-même qui n'est pas claire plutôt que la matière, c'est un défaut : [ouvrez une issue](https://github.com/TokenCemetery/teach/issues).
