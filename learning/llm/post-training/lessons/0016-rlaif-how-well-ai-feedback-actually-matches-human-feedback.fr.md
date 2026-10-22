---
title: "16. RLAIF : dans quelle mesure le feedback d'IA correspond réellement au feedback humain"
description: "Un modèle qui juge ses propres sorties, à sa propre taille, a quand même battu le simple fine-tuning supervisé"
type: lesson
---

# Leçon 16. RLAIF : dans quelle mesure le feedback d'IA correspond réellement au feedback humain

**Lien avec la mission :** « Savoir dire d'où est venu le feedback (humain ou IA) dans un pipeline de réglage de sécurité donné et ce que cela implique comme compromis » est la puce d'« Objectif » que sert cette étape. La leçon 15 a couvert une méthode construite sur le feedback d'IA ; cette leçon couvre la comparaison directe et contrôlée du feedback d'IA et du feedback humain sur plusieurs tâches.
**Source primaire :** [Article : "RLAIF: Scaling Reinforcement Learning from Human Feedback with AI Feedback", Lee et al., 2023](https://arxiv.org/abs/2309.00267)
**Prérequis :** [Leçon 15](0015-constitutional-ai-feedback-from-a-model-not-a-human.md)

## Échauffement

1. ▢ Dans RL-CAI, qu'est-ce qui remplace l'annotateur humain qui jugerait ordinairement laquelle de deux réponses échantillonnées est la meilleure ?

<details markdown="1"><summary>Vérifier</summary>

Un modèle. Un système d'IA juge quelle réponse est la meilleure, et un modèle de préférence est entraîné sur ce jeu de données de préférences générées par IA.

</details>

2. ▢ D'après la comparaison de Bai et al. elle-même, comment les crowdworkers ont-ils noté RL-CAI face à un modèle entraîné sur des labels humains de nocivité collectés auparavant ?

<details markdown="1"><summary>Vérifier</summary>

Ils ont préféré RL-CAI au modèle entraîné sur des comparaisons étiquetées par des humains.

</details>

## À savoir

### Une comparaison contrôlée, en face à face

Lee et al. mènent une comparaison directe que les résultats de Constitutional AI ne faisaient qu'esquisser : sur trois tâches distinctes, le résumé, la génération de dialogue utile et la génération de dialogue inoffensif, ils entraînent une policy avec du RLHF ordinaire et une seconde avec du **RLAIF**, où un modèle de langage prêt à l'emploi produit les labels de préférence à la place d'un humain, tout le reste du montage restant comparable. Des évaluateurs humains jugent ensuite les résultats.

### Le résultat : comparable sur deux tâches, meilleur sur la troisième

Pour le résumé et la génération de dialogue utile, RLAIF comme RLHF sont fortement préférés à une baseline SFT simple (qu'ils battent respectivement 63 % et 64 % du temps), et une comparaison directe en face à face entre RLAIF et RLHF montre les deux également préférés, sans différence statistiquement significative entre eux. Pour la génération de dialogue inoffensif, Lee et al. rapportent que RLAIF **surpasse** en fait RLHF, noté par les évaluateurs humains comme plus inoffensif. Sur les trois tâches, remplacer un jeu de données de préférence étiqueté par des humains par un jeu étiqueté par IA n'a pas produit de moins bon résultat ; sur deux tâches il a égalé RLHF, et sur la troisième il l'a battu.

### Le résultat le plus surprenant : un modèle qui juge à sa propre taille, ou lui-même

Lee et al. poussent plus loin, vers ce qu'ils appellent l'« auto-amélioration » : RLAIF a quand même surpassé la baseline SFT simple même quand l'annotateur IA qui générait les préférences avait la même taille que la policy entraînée, ou, dans le cas le plus extrême, était exactement le même checkpoint que celui dont la policy était partie. On peut faire progresser un modèle avec des jugements de préférence produits par un modèle qui n'est pas plus capable que celui qu'on entraîne, y compris des jugements produits par une copie antérieure de lui-même.

### Sauter entièrement le reward model : direct-RLAIF

Lee et al. introduisent une simplification de plus : **direct-RLAIF (d-RLAIF)**, qui saute entièrement l'entraînement d'un modèle de préférence séparé et interroge à la place un modèle de langage prêt à l'emploi pour obtenir directement un score de récompense, pendant l'entraînement par RL lui-même. Retirer du pipeline un modèle entraîné entier, le reward model que la leçon 8 avait déjà signalé comme un vrai facteur de coût dans le RLHF ordinaire, n'a pas nui à la performance dans leurs résultats ; ils rapportent que d-RLAIF atteint une meilleure performance que le RLAIF canonique, pas simplement une performance comparable à moindre coût.

### Ce que cela plaide, pris avec la leçon 15

Entre le résultat de Constitutional AI (un pipeline à feedback d'IA préféré à un pipeline à feedback humain) et la comparaison contrôlée de Lee et al. (un feedback d'IA qui égale ou bat le feedback humain sur trois tâches distinctes, tient même à échelle d'annotateur réduite et tolère le retrait de tout un reward model), l'idée que le « feedback d'IA » serait un pis-aller, un substitut moindre du feedback humain, ne tient pas bien face à l'un ou l'autre résultat. Lee et al. énoncent directement leur propre conclusion : RLAIF offre une solution potentielle aux limites de passage à l'échelle de la collecte de feedback humain, et pas seulement une approximation moins chère de celui-ci.

## Pratique

1. ▢ Sur le résumé et la génération de dialogue utile, comment le taux de victoire de RLAIF contre une baseline SFT simple se compare-t-il à celui de RLHF, d'après Lee et al. ?

<details markdown="1"><summary>Vérifier</summary>

Sans différence statistiquement significative : les deux ont battu la baseline SFT à des taux similaires (63 % et 64 %), et un face-à-face direct entre RLAIF et RLHF n'a montré aucune préférence significative pour l'un ou l'autre.

</details>

2. ▢ Pour laquelle des trois tâches testées par Lee et al. RLAIF a-t-il surpassé RLHF, au lieu de simplement l'égaler ?

<details markdown="1"><summary>Vérifier</summary>

La génération de dialogue inoffensif. Les évaluateurs humains ont noté les réponses de RLAIF comme plus inoffensives que celles de RLHF sur cette tâche précisément.

</details>

3. ▢ Qu'y a-t-il de surprenant à ce que RLAIF surpasse quand même une baseline SFT même quand l'annotateur IA est exactement le même checkpoint que la policy entraînée ?

<details markdown="1"><summary>Vérifier</summary>

Cela signifie que les propres jugements de préférence d'un modèle sur des sorties, venant d'un modèle pas plus capable que celui qu'on améliore, peuvent quand même produire une vraie amélioration par rapport au simple fine-tuning supervisé, sans qu'il faille un feedback venant de quelque chose de plus capable ou d'un humain.

</details>

4. ▢ Que retire direct-RLAIF (d-RLAIF) du pipeline RLAIF standard, et qu'ont constaté Lee et al. sur sa performance ?

    - a) Il retire le modèle de policy lui-même ; ils ont constaté une moins bonne performance
    - b) Il retire le modèle de préférence ou reward model entraîné séparément, en interrogeant directement un LLM prêt à l'emploi pour obtenir un score de récompense pendant le RL ; ils ont constaté une meilleure performance que le RLAIF canonique
    - c) Il retire entièrement l'étape de RL, ne laissant que du SFT ; la performance était inchangée
    - d) Il retire tout besoin de modèle de langage, en utilisant à la place une récompense purement à base de règles

<details markdown="1"><summary>Vérifier</summary>

**b)** est exactement ce que décrivent et rapportent Lee et al. (a), (c) et (d) décrivent chacune un autre changement du pipeline, sans rapport.

</details>

## Exercices en situation réelle

- [ ] Trouvez où un framework d'entraînement ou un pipeline de recherche auquel vous avez accès expose une option d'étiquetage de préférences par feedback d'IA ou LLM-as-judge, et vérifiez s'il ressemble davantage au RLAIF canonique (un modèle de préférence entraîné) ou à direct-RLAIF (une récompense interrogée en direct auprès d'un LLM).
- [ ] Lisez le passage de l'article de Lee et al. (lié plus haut) qui décrit le résultat d'« auto-amélioration » et écrivez, en une phrase, pourquoi ce résultat est plus surprenant que celui où RLAIF égale simplement RLHF avec un annotateur IA plus grand et plus capable.
- [ ] Demain : pour une tâche sur laquelle vous pourriez vouloir aligner un modèle, décidez si vous choisiriez RLHF, RLAIF ou direct-RLAIF en premier, et écrivez une phrase nommant lequel des résultats de cette leçon (qualité comparable, auto-amélioration à échelle égale, ou coût de pipeline plus bas) a guidé votre réponse.

## Pour aller plus loin

- [Article : "RLAIF: Scaling Reinforcement Learning from Human Feedback with AI Feedback", Lee et al., 2023](https://arxiv.org/abs/2309.00267)
- [Article : "Constitutional AI: Harmlessness from AI Feedback", Bai et al., 2022](https://arxiv.org/abs/2212.08073)
- [Ressources](../RESOURCES.md)

---

L'étape 8 a couvert le feedback qui vient d'un modèle plutôt que d'un humain, et la façon dont il tient réellement. L'étape 9 se tourne vers une question plus dure qui sous-tend tout ce que ce parcours a couvert : une fois un modèle aligné, comment savoir si le chiffre qui mesure cet alignement mesure la vraie chose.

Ça ne passe pas ? Relisez la source primaire en haut de page, car cette leçon la condense et c'est dans la condensation que la compréhension s'échappe. Consultez le [glossaire](../GLOSSARY.md) pour tout terme qui vous a paru glissant.

Si c'est la leçon elle-même qui n'est pas claire plutôt que la matière, c'est un défaut : [ouvrez une issue](https://github.com/TokenCemetery/teach/issues).
