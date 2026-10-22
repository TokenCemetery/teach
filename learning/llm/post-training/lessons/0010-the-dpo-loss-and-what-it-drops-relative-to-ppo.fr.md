---
title: "10. La loss de DPO, et ce qu'elle abandonne par rapport à PPO"
description: "Une loss, deux modèles, aucune boucle d'échantillonnage, et le même beta qu'aurait utilisé une pénalité KL"
type: lesson
---

# Leçon 10. La loss de DPO, et ce qu'elle abandonne par rapport à PPO

**Lien avec la mission :** « Dériver la récompense implicite de DPO à partir des mêmes données de préférence que RLHF, et dire ce à quoi elle renonce en supprimant la boucle de RL » est la quatrième puce sous « Objectif ». La leçon 9 a couvert la dérivation ; cette leçon couvre la loss qui en résulte et dit sans détour ce qu'elle abandonne par rapport à PPO.
**Source primaire :** [Article : "Direct Preference Optimization: Your Language Model is Secretly a Reward Model", Rafailov et al., 2023](https://arxiv.org/abs/2305.18290)
**Prérequis :** [Leçon 9](0009-dpos-implicit-reward-why-the-partition-function-cancels.md)

## Échauffement

1. ▢ Pourquoi la fonction de partition `Z(x)` s'annule-t-elle quand on calcule une différence de deux récompenses pour le même prompt ?

<details markdown="1"><summary>Vérifier</summary>

`Z(x)` ne dépend que du prompt, pas de la complétion qu'on note, donc c'est exactement le même terme additif dans les deux récompenses qu'on soustrait, et il disparaît entièrement de la différence.

</details>

2. ▢ Que signifie « récompense implicite », au sens où la leçon 9 la dérive ?

<details markdown="1"><summary>Vérifier</summary>

La fonction de récompense qu'une policy définit mathématiquement, par rapport à une policy de référence figée, uniquement comme conséquence de la relation de policy optimale qu'implique déjà l'objectif de RLHF, sans jamais entraîner de reward model séparé.

</details>

## À savoir

### Substituer la récompense implicite dans la loss de Bradley-Terry

La loss de Bradley-Terry de la leçon 4 entraînait un reward model séparé à faire dépasser le score d'une complétion rejetée par celui d'une complétion préférée. DPO utilise exactement la même idée, avec une substitution : partout où la loss de Bradley-Terry utiliserait la sortie d'un reward model entraîné, DPO substitue la récompense implicite de la leçon 9, `β · log(π(y|x) / π_ref(y|x))`, calculée directement à partir de la policy entraînée et du modèle de référence figé. La loss qui en résulte, telle que la donnent Rafailov et al., compare la complétion préférée `y_w` et la complétion rejetée `y_l` pour le même prompt :

```text
loss = -log( sigmoid( β · [ (log π(y_w|x) - log π_ref(y_w|x)) - (log π(y_l|x) - log π_ref(y_l|x)) ] ) )
```

C'est la loss de Bradley-Terry de la leçon 4, avec les deux scores du reward model remplacés par les deux valeurs de la récompense implicite, une pour la complétion préférée et une pour la rejetée. Rien n'a changé dans la forme de la loss ; ce qui a changé, c'est ce qui tient lieu de récompense.

### Ce dont cette loss a besoin, et ce dont elle n'a plus besoin

Calculer cette loss exige exactement deux modèles : la policy entraînée, et une copie figée du modèle de référence (ordinairement le modèle SFT), chacun évalué sur les mêmes complétions préférée et rejetée pour obtenir quatre log-probabilités au total. Comparez avec le montage PPO de l'étape 4 (leçon 8) : aucun reward model séparé n'est entraîné, puisque la récompense implicite est calculée directement à partir de la policy et du modèle de référence. Aucune value function n'est nécessaire, puisqu'il n'y a pas d'avantage à estimer ; DPO ne fait pas d'apprentissage par renforcement au sens d'échantillonner des actions et d'estimer des retours. Il n'y a pas non plus de clipping PPO (leçon 7), puisqu'il n'y a pas de mise à jour de policy gradient dont il faudrait borner la taille de pas ; cette loss est optimisée directement, comme n'importe quelle loss supervisée ordinaire, avec un pas de gradient par batch de paires de préférence, sans aucune boucle d'échantillonnage entre les pas.

### Le même beta, qui fait le même travail

Le `β` de la loss de DPO n'est pas un nouvel hyperparamètre inventé pour cette méthode ; c'est la même force de pénalité KL que dans l'objectif RLHF de la leçon 6, désormais intégrée directement dans la récompense implicite au lieu d'apparaître comme un terme de pénalité séparé ajouté au score d'un reward model. Un `β` plus grand veut toujours dire rester plus près du modèle de référence ; un `β` plus petit veut toujours dire être plus libre de s'en éloigner, exactement le compromis de la leçon 6, simplement exprimé dans une seule loss au lieu de deux termes séparés.

### Ce à quoi l'on renonce réellement

DPO ne supprime pas les compromis que gérait la pénalité KL de PPO ; il supprime la machinerie. La méthode de Rafailov et al. est une reformulation mathématiquement exacte de la même relation de policy optimale sur laquelle RLHF s'appuie déjà, pas une approximation de celle-ci, donc rien dans l'objectif sous-jacent de satisfaction des préférences n'est affaibli. Ce à quoi l'on renonce réellement, c'est un reward model autonome et la flexibilité qui vient avec le fait d'en entraîner un séparément : un reward model peut, en principe, être réutilisé pour noter des sorties sur lesquelles il n'a jamais directement entraîné la policy, être inspecté seul, ou être combiné à des signaux supplémentaires au-delà des données de préférence d'origine. La récompense implicite de DPO n'existe que liée à un couple précis policy et modèle de référence ; il ne reste aucune fonction de notation autonome une fois l'entraînement terminé, seulement la policy entraînée elle-même.

## Pratique

1. ▢ Le calcul de la loss DPO pour une paire de préférence demande quatre log-probabilités. Nommez de quoi chacune des quatre est la log-probabilité.

<details markdown="1"><summary>Vérifier</summary>

La log-probabilité de la complétion préférée sous la policy, la log-probabilité de la complétion préférée sous le modèle de référence, la log-probabilité de la complétion rejetée sous la policy, et la log-probabilité de la complétion rejetée sous le modèle de référence.

</details>

2. ▢ De quels composants de PPO (reward model, value function, pénalité KL, mise à jour clippée) la loss de DPO n'a-t-elle absolument pas besoin ?

    - a) Seulement la mise à jour clippée
    - b) Le reward model et la value function ; le compromis de la pénalité KL est toujours présent, simplement intégré à la récompense implicite au lieu d'un terme séparé
    - c) Les quatre, puisque DPO n'utilise aucune pénalité KL d'aucune sorte
    - d) Seulement le reward model ; DPO entraîne toujours une value function séparée

<details markdown="1"><summary>Vérifier</summary>

**b)** est le compte rendu exact : DPO n'a besoin ni d'un reward model séparé ni d'une value function, et n'a pas de mise à jour clippée par pas puisqu'il n'y a pas de boucle d'échantillonnage de RL, mais le même compromis piloté par beta que décrivait la leçon 6 est toujours présent, intégré directement au terme de récompense implicite. (a), (c) et (d) énoncent chacune de travers quels éléments subsistent.

</details>

3. ▢ Une équipe veut réutiliser son reward model entraîné pour noter un lot de complétions qui n'ont jamais fait partie d'un run d'entraînement de policy, uniquement à des fins de monitoring. Une équipe qui utilise DPO au lieu de PPO pourrait-elle faire la même chose avec une facilité équivalente ?

<details markdown="1"><summary>Vérifier</summary>

Pas aussi directement. DPO ne produit jamais de reward model autonome ; sa récompense implicite n'est définie qu'en fonction d'une policy entraînée précise et de son modèle de référence. Noter des complétions arbitraires de cette façon est exactement le type de réutilisation qu'un reward model autonome permet et que l'approche de DPO ne produit pas comme sous-produit.

</details>

4. ▢ `β` signifie-t-il autre chose dans la loss de DPO que dans l'objectif RLHF de la leçon 6 ?

<details markdown="1"><summary>Vérifier</summary>

Non. C'est la même force de pénalité KL, qui contrôle le même compromis entre rester proche du modèle de référence et aller vers ce que récompensent les données de préférence ; DPO l'intègre simplement directement dans le terme de récompense implicite au lieu de la garder comme une pénalité visuellement séparée ajoutée au score d'un reward model.

</details>

## Exercices en situation réelle

- [ ] Trouvez une implémentation de DPO dans une bibliothèque à laquelle vous avez accès (TRL de Hugging Face en est une courante) et confirmez qu'elle calcule les mêmes quatre log-probabilités que nomme cette leçon, par paire de préférence.
- [ ] À partir d'un petit exemple hypothétique (inventez des valeurs de log-probabilité plausibles pour une complétion préférée et une rejetée sous une policy et un modèle de référence), calculez la loss DPO à la main pour deux valeurs différentes de `β`, et décrivez comment la loss change quand `β` grandit.
- [ ] Demain : pour un projet où vous pourriez vouloir aligner un modèle, décidez si vous choisiriez PPO ou DPO en premier, et écrivez une phrase nommant lequel des compromis de cette leçon (coût d'ingénierie, réutilisation d'un reward model autonome, infrastructure de RL) a guidé votre réponse.

## Pour aller plus loin

- [Article : "Direct Preference Optimization: Your Language Model is Secretly a Reward Model", Rafailov et al., 2023](https://arxiv.org/abs/2305.18290)
- [Documentation : "TRL - Transformer Reinforcement Learning", Hugging Face](https://huggingface.co/docs/trl/index)
- [Ressources](../RESOURCES.md)

---

L'étape 5 a couvert une manière d'atteindre un résultat similaire à RLHF sans reward model séparé ni boucle de RL. L'étape 6 couvre un autre écart par rapport à PPO : garder la boucle de RL, mais pour des tâches où la récompense n'est pas du tout une affaire de préférence humaine, mais quelque chose de directement vérifiable.

Ça ne passe pas ? Relisez la source primaire en haut de page, car cette leçon la condense et c'est dans la condensation que la compréhension s'échappe. Consultez le [glossaire](../GLOSSARY.md) pour tout terme qui vous a paru glissant.

Si c'est la leçon elle-même qui n'est pas claire plutôt que la matière, c'est un défaut : [ouvrez une issue](https://github.com/TokenCemetery/teach/issues).
