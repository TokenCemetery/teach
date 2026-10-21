---
title: "15. Constitutional AI : un feedback venu d'un modèle, pas d'un humain"
description: "Zéro label humain pour la nocivité, une liste écrite de principes à la place, et un assistant qui explique ses objections au lieu d'esquiver"
type: lesson
---

# Leçon 15. Constitutional AI : un feedback venu d'un modèle, pas d'un humain

**Lien avec la mission :** « Savoir dire d'où est venu le feedback (humain ou IA) dans un pipeline de réglage de sécurité donné et ce que cela implique comme compromis » est la puce d'« Objectif » que sert cette étape. Cette leçon couvre la méthode en deux étapes de Constitutional AI ; la leçon 16 couvre la tenue du feedback d'IA face au feedback humain dans une comparaison directe et contrôlée.
**Source primaire :** [Article : "Constitutional AI: Harmlessness from AI Feedback", Bai et al., 2022](https://arxiv.org/abs/2212.08073)
**Prérequis :** [Leçon 14](0014-distilling-a-reasoning-model-down.md)

## Échauffement

1. ▢ D'après la comparaison de 32B de DeepSeek-AI elle-même, entraîner un petit modèle directement par RL à grande échelle a-t-il atteint la même performance de raisonnement que distiller à partir d'un modèle plus grand déjà entraîné par RL ?

<details markdown="1"><summary>Vérifier</summary>

Non. Le RL direct sur le modèle de base de 32B a atteint 47.0 % de pass@1 sur AIME 2024, bien en dessous des 72.6 % qu'a atteints le même modèle de base fine-tuné à la place sur les traces de raisonnement distillées du modèle plus grand.

</details>

2. ▢ Qu'est-ce qu'une récompense vérifiable, et pourquoi n'a-t-elle pas le mode d'échec de reward hacking d'un reward model entraîné ?

<details markdown="1"><summary>Vérifier</summary>

Une récompense produite par un vérificateur déterministe plutôt que par un modèle appris ; comme aucun travers d'un modèle appris ne s'interpose entre la sortie et son score, il n'y a pas d'exploit propre à un reward model qu'une policy puisse apprendre.

</details>

## À savoir

### Rappel de l'échec que cette méthode est conçue pour éviter

La leçon 5 a couvert un échec réel et documenté : des policies RLHF sur-optimisées pour l'innocuité avaient convergé vers l'esquive généralisée, en recommandant aux utilisateurs de consulter un thérapeute devant presque toute question un tant soit peu sensible, un moyen bon marché de scorer bien sur un reward model d'innocuité sans être réellement utile. **Constitutional AI (CAI)** est conçue précisément pour produire un assistant inoffensif qui ne prend pas ce raccourci.

### Deux étapes, et où le feedback d'IA entre dans chacune

L'étape supervisée, **SL-CAI**, échantillonne des réponses d'un modèle initial, fait générer au modèle une **autocritique** et une **révision** de sa propre réponse au regard d'une courte liste écrite de principes (la « constitution » qui donne son nom à la méthode), puis fine-tune le modèle d'origine sur ces réponses auto-révisées : du SFT ordinaire (étape 2) sur des données que le modèle a produites et améliorées lui-même.

L'étape d'apprentissage par renforcement, **RL-CAI**, échantillonne des paires de réponses du modèle fine-tuné par SL, et au lieu de demander à un annotateur humain laquelle est la meilleure, **utilise un modèle** pour porter ce jugement. Un modèle de préférence (entraînement de Bradley-Terry de la leçon 4) est entraîné sur ce jeu de données de préférences générées par IA, puis la policy est entraînée par RL contre ce modèle de préférence entraîné par IA exactement comme le montage RLHF de la leçon 6 en utiliserait un entraîné par des humains. Bai et al. nomment directement cette technique générale : **RL from AI Feedback (RLAIF)**.

### Zéro label humain pour la nocivité, et ce qui en est sorti

Bai et al. énoncent clairement leur résultat : tout ce pipeline entraîne un assistant d'IA « non évasif » et « relativement inoffensif » « sans aucun label de feedback humain pour les nocivités ». Ce sont les principes de la constitution, et non des milliers de jugements humains sur la nocivité, qui façonnent le comportement du modèle. L'assistant obtenu aborde les requêtes nuisibles en expliquant ses objections plutôt qu'en refusant ou en esquivant d'emblée, ce qui répond directement à la sur-optimisation précise que documentait la leçon 5 : un modèle dont l'entraînement à l'innocuité récompense un engagement réfléchi, plutôt que le refus le moins coûteux possible, a moins d'incitation à s'effondrer dans l'esquive généralisée dès le départ.

### La comparaison qui mérite qu'on prenne cela au sérieux

Bai et al. ne se contentent pas d'affirmer que cela fonctionne ; ils rapportent que des crowdworkers ont préféré le modèle obtenu, « RL-CAI », à des modèles entraînés avec des labels de feedback humain collectés auparavant pour la nocivité. Remplacer les labels humains de nocivité par une constitution écrite et des préférences générées par IA n'a pas seulement égalé l'alternative étiquetée par des humains ; d'après leur propre comparaison rapportée, cela a fait mieux.

## Pratique

1. ▢ Dans SL-CAI, que fait le modèle de ses propres réponses échantillonnées avant qu'elles servent au fine-tuning ?

<details markdown="1"><summary>Vérifier</summary>

Il génère une autocritique de la réponse au regard des principes de la constitution écrite, puis produit une révision de la réponse, et le modèle est fine-tuné sur ces réponses révisées.

</details>

2. ▢ Dans RL-CAI, qu'est-ce qui remplace l'annotateur humain qui jugerait ordinairement laquelle de deux réponses échantillonnées est la meilleure ?

<details markdown="1"><summary>Vérifier</summary>

Un modèle. Un système d'IA juge laquelle des deux réponses est la meilleure, et un modèle de préférence est entraîné sur ce jeu de données de préférences générées par IA, et non sur des comparaisons étiquetées par des humains.

</details>

3. ▢ Pourquoi le fait que l'assistant de Constitutional AI explique ses objections à une requête nuisible, plutôt que de refuser d'emblée, répond-il directement à l'échec que décrivait la leçon 5 ?

<details markdown="1"><summary>Vérifier</summary>

L'échec d'esquive généralisée de la leçon 5 venait de ce que refuser d'emblée était un moyen bon marché et peu sophistiqué de scorer bien sur un reward model d'innocuité. Une approche d'entraînement dont la récompense favorise plutôt un engagement réel et l'explication des objections à une requête supprime l'incitation à ce raccourci bon marché, puisque l'esquive seule ne serait pas l'option au meilleur score.

</details>

4. ▢ D'après la comparaison de Bai et al. elle-même, comment les crowdworkers ont-ils noté RL-CAI face à un modèle entraîné sur des labels de feedback humain collectés auparavant pour la nocivité ?

<details markdown="1"><summary>Vérifier</summary>

Ils ont préféré RL-CAI. Remplacer les labels humains de nocivité par une constitution et des préférences générées par IA n'a pas seulement égalé l'alternative étiquetée par des humains dans leur comparaison rapportée ; il a été préféré à elle.

</details>

## Exercices en situation réelle

- [ ] Trouvez une « constitution » ou un ensemble de principes directeurs publié, utilisé pour entraîner un vrai modèle (plusieurs ont été rendus publics), et lisez trois ou quatre de ses principes. Notez s'ils se lisent comme des règles précises ou comme des valeurs générales qu'un modèle devrait interpréter.
- [ ] Lisez le passage de l'article Constitutional AI (lié plus haut) qui décrit l'étape d'autocritique et de révision de SL-CAI, et écrivez une phrase décrivant ce qui devrait mal tourner pour que l'autocritique d'un modèle ne détecte pas un vrai problème dans sa propre réponse.
- [ ] Demain : sans regarder la suite, écrivez une prédiction d'une phrase pour la leçon 16 : sachant que Constitutional AI remplace les labels humains de nocivité par des labels générés par IA pour une seule méthode, attendriez-vous que le feedback d'IA fonctionne aussi bien pour d'autres types de tâches, comme le résumé ou l'utilité générale, et pourquoi ou pourquoi pas ?

## Pour aller plus loin

- [Article : "Constitutional AI: Harmlessness from AI Feedback", Bai et al., 2022](https://arxiv.org/abs/2212.08073)
- [Ressources](../RESOURCES.md)

---

Ça ne passe pas ? Relisez la source primaire en haut de page, car cette leçon la condense et c'est dans la condensation que la compréhension s'échappe. Consultez le [glossaire](../GLOSSARY.md) pour tout terme qui vous a paru glissant.

Si c'est la leçon elle-même qui n'est pas claire plutôt que la matière, c'est un défaut : [ouvrez une issue](https://github.com/TokenCemetery/teach/issues).
