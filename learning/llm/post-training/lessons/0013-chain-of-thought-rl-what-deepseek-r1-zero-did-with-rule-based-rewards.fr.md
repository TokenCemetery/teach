---
title: "13. RL sur chaîne de raisonnement : ce qu'a fait DeepSeek-R1-Zero avec des récompenses à base de règles"
description: "Aucun reward model appris, aucune étape SFT au préalable, et un raisonnement étendu a émergé quand même parce qu'il faisait trouver de plus en plus de bonnes réponses"
type: lesson
---

# Leçon 13. RL sur chaîne de raisonnement : ce qu'a fait DeepSeek-R1-Zero avec des récompenses à base de règles

**Lien avec la mission :** « Savoir dire comment le comportement d'un modèle de raisonnement a été produit, et pas seulement comment le prompter » est la puce d'« Objectif » que sert cette étape. Cette leçon couvre l'entraînement par pur RL de DeepSeek-R1-Zero et ce qui en est sorti ; la leçon 14 couvre le correctif qui en a fait un modèle utilisable, et ce que la distillation a apporté en plus.
**Source primaire :** [Article : "DeepSeek-R1: Incentivizing Reasoning Capability in LLMs via Reinforcement Learning", DeepSeek-AI, 2025](https://arxiv.org/abs/2501.12948)
**Prérequis :** [Leçon 12](0012-verifiable-rewards-when-a-checker-replaces-the-reward-model.md)

## Échauffement

1. ▢ Qu'est-ce qu'une récompense vérifiable, et pourquoi n'a-t-elle pas le même mode d'échec de reward hacking qu'un reward model entraîné ?

<details markdown="1"><summary>Vérifier</summary>

Un signal de récompense produit par un vérificateur déterministe plutôt que par un modèle appris ; comme aucun travers d'un modèle appris ne s'interpose entre la sortie et son score, il n'y a pas d'exploit propre à un reward model qu'une policy puisse apprendre, comme c'est le cas avec un reward model entraîné.

</details>

2. ▢ Pourquoi une récompense vérifiable convient-elle mal pour entraîner des réponses de support client plus empathiques ?

<details markdown="1"><summary>Vérifier</summary>

Il n'existe aucun vérificateur déterministe pour « cette réponse était d'une empathie appropriée » ; les récompenses vérifiables conviennent aux tâches où la justesse est vérifiable dès le départ, et le ton n'est pas une propriété de ce type.

</details>

## À savoir

### Entraîner directement sur un modèle de base, sans étape SFT au préalable

DeepSeek-R1-Zero est entraîné par du RL à grande échelle appliqué directement à un modèle de base pré-entraîné, sans aucune étape SFT au préalable, la première étape du pipeline habituel en trois étapes de la leçon 1 étant entièrement sautée. La récompense contre laquelle il s'entraîne est purement **à base de règles**, construite à partir d'exactement deux vérifications : une **récompense de précision** (accuracy reward), qui pour les problèmes de maths vérifie si la réponse finale, donnée dans un format précisé comme à l'intérieur d'un encadré, correspond exactement à la bonne, ou, pour les problèmes de code, exécute un compilateur sur des cas de test prédéfinis ; et une **récompense de format**, qui vérifie seulement que le processus de réflexion du modèle est placé entre une paire de balises marquant où il commence et où il finit. DeepSeek-AI indiquent directement qu'ils n'appliquent aucun reward model neuronal, ni de résultat ni de processus : aucun reward model entraîné d'aucune sorte ne s'interpose entre la sortie du modèle et son score.

### Un raisonnement étendu a émergé, il n'a pas été programmé

Rien dans cette conception de la récompense n'ordonne explicitement au modèle de raisonner plus longtemps, de montrer des étapes intermédiaires ou de reconsidérer une fausse piste. DeepSeek-AI rapportent que ces comportements ont émergé quand même, au cours de l'entraînement par RL : comme une récompense de précision à base de règles récompense simplement la bonne réponse finale, et qu'un raisonnement plus long et plus soigneux tend à faire trouver plus de bonnes réponses finales, l'entraînement par RL a naturellement sélectionné davantage de ce raisonnement, sans que personne ait spécifié « raisonne plus longtemps » comme cible.

### Le « moment eurêka »

DeepSeek-AI décrivent un cas précis et frappant : à un point intermédiaire de l'entraînement, DeepSeek-R1-Zero s'est mis à consacrer plus de temps de réflexion à un problème précisément en réévaluant son approche initiale en cours de route, un comportement d'autocorrection pour lequel personne n'avait écrit directement de terme de récompense. Ils le décrivent comme « non seulement un "moment eurêka" pour le modèle mais aussi pour les chercheurs qui observent son comportement », et le présentent comme une démonstration de ce que l'entraînement par RL rend possible et que l'instruction directe ne permet pas : au lieu d'enseigner explicitement au modèle comment résoudre un problème, les récompenses à base de règles ont fourni la bonne incitation, et un comportement de résolution de problèmes réellement nouveau a émergé de l'optimisation contre elle.

### Ce que le pur RL seul n'a pas corrigé

La capacité de raisonnement de DeepSeek-R1-Zero s'accompagnait de vrais coûts que DeepSeek-AI ne cachent pas : une mauvaise lisibilité, et un mélange de langues (passer d'une langue à l'autre dans une même réponse d'une façon que personne n'avait demandée). Rien dans une récompense purement à base de règles, centrée sur la seule justesse, ne donne au modèle d'incitation à être lisible ou à rester dans une seule langue ; ces vérifications n'ont jamais fait partie du score, donc rien ne les a sélectionnées. DeepSeek-R1 lui-même, le modèle construit pour corriger cela, est le sujet de la leçon 14.

## Pratique

1. ▢ La récompense de DeepSeek-R1-Zero n'a aucun terme explicite récompensant des chaînes de raisonnement plus longues, et pourtant la longueur de raisonnement du modèle a fortement augmenté pendant l'entraînement. Qu'est-ce qui, d'après le récit de cette leçon, a réellement provoqué cette croissance ?

<details markdown="1"><summary>Vérifier</summary>

La récompense de précision récompense simplement la bonne réponse finale, et un raisonnement plus long et plus soigneux tendait à produire plus de réponses finales correctes ; l'entraînement par RL l'a donc sélectionné comme effet secondaire de l'optimisation de la justesse, et non parce que la longueur du raisonnement était directement récompensée.

</details>

2. ▢ Pourquoi DeepSeek-AI décrit-il la récompense de précision comme « à base de règles » plutôt que comme un reward model ?

    - a) C'est toujours un réseau de neurones entraîné, simplement plus petit
    - b) C'est une vérification déterministe (correspondance exacte avec une réponse connue, ou un compilateur exécutant des cas de test fixes), sans aucun modèle appris impliqué dans la production du score
    - c) Elle n'est à base de règles que pour les problèmes de code, et un reward model neuronal est utilisé pour les maths
    - d) « À base de règles » et « reward model » veulent dire la même chose dans cet article

<details markdown="1"><summary>Vérifier</summary>

**b)** est exactement ce qu'indique DeepSeek-AI : aucun reward model neuronal, de résultat ou de processus, n'est appliqué. (a) et (c) supposent toutes deux un composant appris que l'article dit explicitement absent. (d) efface une distinction que l'article prend soin de tracer.

</details>

3. ▢ DeepSeek-R1-Zero atteint de fortes performances de raisonnement mais souffre d'une mauvaise lisibilité et d'un mélange de langues. Vu la façon dont sa récompense a été construite, est-ce surprenant ?

<details markdown="1"><summary>Vérifier</summary>

Non. La récompense ne vérifiait que la justesse de la réponse finale et la présence des balises de réflexion ; rien sur la lisibilité ni sur le fait de rester dans une seule langue n'a jamais fait partie du score, si bien que l'entraînement par RL n'avait aucune incitation à sélectionner l'un ou l'autre, quelle que soit la qualité du raisonnement du modèle.

</details>

## Exercices en situation réelle

- [ ] Lisez le passage « Aha Moment » de l'article DeepSeek-R1 (lié plus haut, texte autour du tableau 3) et écrivez, avec vos propres mots, quel comportement précis le modèle a présenté que les chercheurs ne lui avaient pas explicitement entraîné à avoir.
- [ ] Trouvez un exemple documenté (dans cet article ou ailleurs) d'un modèle entraîné avec une récompense étroitement spécifiée qui a produit un comportement émergent imprévu, et comparez-le au « moment eurêka » : le comportement émergent était-il bénéfique, nuisible, ou les deux ?
- [ ] Demain : sans regarder la suite, écrivez une prédiction d'une phrase pour la leçon 14 : sachant que le pur RL à base de règles de DeepSeek-R1-Zero a produit un fort raisonnement mais une mauvaise lisibilité, qu'ajouteriez-vous au processus d'entraînement, et à quelle étape, pour corriger la lisibilité sans perdre la capacité de raisonnement ?

## Pour aller plus loin

- [Article : "DeepSeek-R1: Incentivizing Reasoning Capability in LLMs via Reinforcement Learning", DeepSeek-AI, 2025](https://arxiv.org/abs/2501.12948)
- [Ressources](../RESOURCES.md)

---

Ça ne passe pas ? Relisez la source primaire en haut de page, car cette leçon la condense et c'est dans la condensation que la compréhension s'échappe. Consultez le [glossaire](../GLOSSARY.md) pour tout terme qui vous a paru glissant.

Si c'est la leçon elle-même qui n'est pas claire plutôt que la matière, c'est un défaut : [ouvrez une issue](https://github.com/TokenCemetery/teach/issues).
