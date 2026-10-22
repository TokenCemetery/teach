---
title: "3. Masquage de la loss sur les tokens hors assistant"
description: "Mettez à zéro la loss sur le prompt, sinon vous dépensez du signal de gradient à apprendre au modèle à prédire un texte qu'il n'a pas généré"
type: lesson
---

# Leçon 3. Masquage de la loss sur les tokens hors assistant

**Lien avec la mission :** « Écrire une boucle d'entraînement SFT qui masque la loss sur les tokens hors assistant, et expliquer ce qui casse dans un modèle de chat entraîné sans ce masque » est la première puce sous « Objectif », et cette leçon y répond directement.
**Source primaire :** [Article : "Llama 2: Open Foundation and Fine-Tuned Chat Models", Touvron et al., 2023](https://arxiv.org/abs/2307.09288)
**Prérequis :** [Leçon 2](0002-instruction-data-and-the-chat-template.md), [Masquage de la loss](../GLOSSARY.md)

## Échauffement

1. ▢ Qu'est-ce qu'un chat template, et pourquoi importe-t-il que le même soit utilisé à l'entraînement et au déploiement ?

<details markdown="1"><summary>Vérifier</summary>

Une manière fixe et cohérente de marquer les frontières de rôle (tours système, utilisateur, assistant) avec des tokens spéciaux, pour que le modèle puisse apprendre une structure qu'il reverra de façon fiable. Une incohérence entre les templates d'entraînement et de déploiement présente au modèle une structure qu'il n'a jamais vue associée au comportement appris, ce qui dégrade ou déstabilise son comportement.

</details>

2. ▢ D'après Touvron et al., quel token spécial utilisent-ils pour séparer un prompt de sa réponse dans les données d'entraînement SFT ?

<details markdown="1"><summary>Vérifier</summary>

Un token spécial dédié, inséré précisément pour marquer la frontière entre le segment de prompt et le segment de réponse.

</details>

## À savoir

### La version simple, sans masque, de cette loss serait fausse

Une loss ordinaire de modélisation de langage entraîne un modèle à prédire le token suivant à chaque position d'une séquence, en le comparant à ce que la séquence contient réellement à cet endroit. Appliquée naïvement à un exemple prompt-réponse concaténé, sans ajustement, elle entraînerait le modèle à prédire aussi les tokens du prompt, et pas seulement ceux de la réponse, puisque le prompt fait partie de la séquence exactement comme la réponse.

### Ce que font réellement Touvron et al.

Touvron et al. énoncent directement leur approche : « nous utilisons un objectif autorégressif et mettons à zéro la loss sur les tokens du prompt de l'utilisateur, si bien que nous ne rétropropageons que sur les tokens de la réponse ». C'est le **masquage de la loss** : chaque token appartenant au prompt (ou, dans un exemple multi-tours, à n'importe quel tour d'utilisateur ou de système) voit sa contribution à la loss mise à zéro, si bien que seuls les tokens que le modèle est réellement censé générer, la réponse de l'assistant, produisent un gradient. Mécaniquement, cela s'implémente en général en donnant à chaque position masquée une valeur de label que la fonction de loss doit ignorer (une convention courante la fixe à `-100` pour une loss d'entropie croisée standard), au lieu du token qui apparaît réellement à cet endroit.

### Ce qui casse sans lui

Omettre ce masquage ne gaspille pas simplement un peu de calcul ; cela change ce que le modèle est réellement entraîné à faire. Deux problèmes concrets en découlent directement :

- **Le modèle apprend à prédire un texte qu'il n'a pas généré et qu'il n'aura jamais besoin de reproduire.** Entraîner un modèle à prédire le prompt de l'utilisateur lui-même ne sert en rien l'objectif du SFT, qui est de façonner ce que le modèle produit comme réponse, pas ce qu'il peut régurgiter de la question.
- **Les prompts sont souvent bien plus longs que les réponses qui les suivent.** Une loss non masquée est dominée par le nombre de tokens de prompt, ce qui dilue le signal de gradient sur les tokens de la réponse, la seule partie de la séquence que le SFT cherche réellement à façonner, tandis qu'une grande quantité de loss est dépensée pour une tâche (prédire le prompt) qui n'a jamais été le but.

### Le résultat : le masquage concentre l'objectif sur ce qu'on enseigne

Masquer chaque token hors assistant fait le contraire des deux problèmes : chaque unité de signal de gradient d'un pas de SFT vient de tokens que le modèle est réellement censé apprendre à produire, sans qu'aucune ne soit dépensée à prédire un texte qu'on lui a simplement donné. C'est ce qui fait que le SFT enseigne la compétence précise qu'il doit enseigner, imiter la réponse voulue, plutôt qu'un mélange de cette compétence et d'une autre, sans rapport (prédire un texte d'utilisateur arbitraire), qui se trouve partager la même séquence d'entraînement.

## Pratique

1. ▢ Un exemple d'entraînement concatène un prompt de 200 tokens et une réponse de 20 tokens, sans aucun masquage de la loss. Quelle fraction approximative de la loss totale de cet exemple vient de tokens qui ne sont pas la véritable cible du SFT ?

<details markdown="1"><summary>Vérifier</summary>

Environ 200 tokens sur 220, soit à peu près 91 %, seraient des tokens de prompt qui apportent une loss sans rapport avec la réponse que le SFT cherche à apprendre au modèle à produire. Seuls environ 9 % de la loss non masquée viendraient de la réponse elle-même.

</details>

2. ▢ Laquelle de ces descriptions rend le mieux ce que fait mécaniquement le masquage de la loss ?

    - a) Il retire entièrement les tokens du prompt de la séquence d'entrée
    - b) Il donne à la position de chaque token masqué un label que la fonction de loss doit ignorer, si bien que seules les positions non masquées (assistant) contribuent à un gradient
    - c) Il réduit le learning rate spécifiquement quand on traite les tokens du prompt
    - d) Il entraîne un modèle séparé uniquement pour les tokens du prompt

<details markdown="1"><summary>Vérifier</summary>

**b)** est le mécanisme réel : les tokens du prompt sont toujours présents en entrée, donc le modèle peut conditionner sa réponse sur eux, mais leurs positions sont exclues du calcul de la loss lui-même. (a) retirerait une information sur laquelle le modèle doit conditionner sa réponse. (c) et (d) ne décrivent aucune technique décrite par cette leçon ou sa source.

</details>

3. ▢ Un modèle entraîné sans masquage de la loss sur les tokens hors assistant est comparé à un modèle entraîné avec, sur exactement les mêmes données SFT. Citez une manière concrète dont vous attendriez que l'entraînement SFT du modèle non masqué se soit déroulé différemment.

<details markdown="1"><summary>Vérifier</summary>

Toute version raisonnable de : le signal de gradient a été dilué par l'apprentissage de la prédiction des tokens du prompt, ou dépensé pour cela, au lieu d'être concentré entièrement sur les tokens de la réponse ; donc, pour le même nombre de pas d'entraînement, une part moindre de l'apprentissage du modèle façonnait réellement son comportement de génération de réponse, la seule chose que le SFT doit enseigner.

</details>

## Exercices en situation réelle

- [ ] Trouvez où un framework d'entraînement auquel vous avez accès implémente le masquage de la loss pour des données SFT de type chat (un `ignore_index`, un champ `labels` avec des positions masquées, ou équivalent), et confirmez quelle convention il utilise pour marquer une position masquée.
- [ ] Prenez un court exemple de conversation (un message système, un tour d'utilisateur, un tour d'assistant) et marquez, token par token ou segment par segment, quelles parties seraient masquées et lesquelles contribueraient à la loss, selon la règle de cette leçon.
- [ ] Demain : pour une conversation multi-tours avec deux tours d'utilisateur et deux tours d'assistant, écrivez quels tours sont masqués et lesquels ne le sont pas, et vérifiez votre réponse avec la règle de cette leçon selon laquelle chaque tour hors assistant est masqué, pas seulement le premier prompt.

## Pour aller plus loin

- [Article : "Llama 2: Open Foundation and Fine-Tuned Chat Models", Touvron et al., 2023](https://arxiv.org/abs/2307.09288)
- [Documentation : "TRL - Transformer Reinforcement Learning", Hugging Face](https://huggingface.co/docs/trl/index)
- [Ressources](../RESOURCES.md)

---

L'étape 2 a couvert l'imitation directe d'une réponse démontrée. L'étape 3 se tourne vers un autre type de signal : non pas ce que la réponse devrait être, mais laquelle de deux réponses un humain a préférée.

Ça ne passe pas ? Relisez la source primaire en haut de page, car cette leçon la condense et c'est dans la condensation que la compréhension s'échappe. Consultez le [glossaire](../GLOSSARY.md) pour tout terme qui vous a paru glissant.

Si c'est la leçon elle-même qui n'est pas claire plutôt que la matière, c'est un défaut : [ouvrez une issue](https://github.com/TokenCemetery/teach/issues).
