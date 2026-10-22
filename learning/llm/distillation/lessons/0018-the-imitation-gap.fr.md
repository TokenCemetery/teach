---
title: "18. L'écart d'imitation"
description: "Pourquoi imiter un modèle plus fort copie son style bien plus vite que sa capacité"
type: lesson
---

# Leçon 18. L'écart d'imitation

**Lien avec la mission :** La mission vous demande de prédire ce qu'un élève reprendra ou non, et de relire une affirmation « égale l'enseignant », ce qui veut dire savoir comment un élève peut ressembler à son enseignant tout en manquant de ce que sait l'enseignant.
**Source primaire :** [Article : "The False Promise of Imitating Proprietary LLMs", Gudibande et al., 2023](https://arxiv.org/abs/2305.15717), sections 1 et 4
**Prérequis :** [Leçon 10](0010-distilling-from-generated-data.md), [Leçon 17](0017-fidelity-and-generalization.md), [Écart d'imitation](../GLOSSARY.md), [Données synthétiques](../GLOSSARY.md), [Fidélité](../GLOSSARY.md)

## Échauffement

1. ▢ Alpaca et Self-Instruct construisent un jeu d'entraînement de quelle manière, et que reçoit l'élève de l'enseignant ?

<details markdown="1"><summary>Vérifier</summary>

Un modèle enseignant génère des instructions et des réponses, et l'élève est affiné sur ce texte. Il ne reçoit que le texte décodé de l'enseignant, sans logits.

</details>

2. ▢ La leçon 17 dit que la précision sur la tâche ne peut pas tenir lieu d'accord avec l'enseignant. Quel est le risque inverse : un élève peut-il s'accorder avec son enseignant sur les sorties et pourtant manquer de sa capacité ?

<details markdown="1"><summary>Vérifier</summary>

L'accord est mesuré sur les entrées que vous testez, il ne parle donc que pour ces entrées. Un élève peut reproduire la formulation de l'enseignant sur des requêtes courantes et échouer sur des tâches que les données d'entraînement couvraient à peine, ce qui est le cas qu'examine cette leçon.

</details>

3. ▢ La leçon 12 dit que le volume ne répare pas les mauvais exemples. Nommez une chose que davantage de données générées par l'enseignant ne peuvent pas fournir à un élève.

<details markdown="1"><summary>Vérifier</summary>

Une connaissance que le propre pré-entraînement de l'élève ne lui a pas donnée. Plus d'exemples peuvent enseigner le format et le comportement, mais ils ne peuvent pas compenser à bon compte ce que le base model n'a jamais appris. Cette affirmation est le cœur de cette leçon.

</details>

## À savoir

### Le cadre

Gudibande et al. étudient l'« imitation de modèle » : collecter un jeu de données de sorties d'un modèle propriétaire via son API et faire un fine-tuning d'un modèle ouvert dessus. Ils imitent ChatGPT avec des modèles de 1.5B à 13B de paramètres (GPT-2 1.5B, LLaMA 7B et 13B) et des données d'imitation de 0.3M à 150M tokens. L'élève ne voit que du texte, c'est donc de la distillation au niveau de la séquence sans logits.

Deux types d'imitation comptent pour l'argument :

| Type | Ce qu'elle imite | Leurs données |
|---|---|---|
| Imitation locale | Une tâche ou un domaine | NQ-synthetic : 6,000 paires question-réponse générées par ChatGPT à partir d'un amorçage de 10 paires, dans le style de Natural Questions |
| Imitation large | Toute l'étendue du comportement | ShareGPT-Mix : environ 50K dialogues dédupliqués de ShareGPT, plus environ 27K réponses de ChatGPT issues de HC3 et 10K exemples de bots ChatGPT de Discord |

### Ce qu'ont vu les évaluateurs humains

Des travailleurs de la foule ont mené des comparaisons par paires en aveugle de chaque modèle d'imitation face à ChatGPT, avec environ 70 travailleurs sur 255 prompts held-out. Environ 70 % des sorties des modèles d'imitation ont été jugées égales ou meilleures que celles de ChatGPT (légende de la figure 1). GPT-4 comme juge a montré les mêmes tendances. Sur ces évaluations, les modèles d'imitation paraissaient proches du modèle qu'ils copiaient.

Les évaluations ont aussi saturé : davantage de données d'imitation ont cessé de les faire monter (section 4.2).

### Ce qu'ont vu les benchmarks

Les auteurs ont ensuite mené des évaluations automatiques ciblées : MMLU (5-shot), Natural Questions (3-shot) et HumanEval (0-shot). Ils rapportent que sur chaque benchmark mesuré, les modèles d'imitation large ne se sont pas améliorés par rapport à leurs base models, ou ont décliné, même quand les données d'imitation augmentaient (section 4.3, figure 4).

Le cas spécifique à une tâche est celui où cela a fonctionné. La précision sur Natural Questions du tableau 1 :

| Modèle | Sans imitation | Entraîné sur ShareGPT-Mix (large) | Entraîné sur NQ-synthetic (local) | ChatGPT |
|---|---|---|---|---|
| LLaMA 7B | 17 | 10 | 22 | 31 |
| LLaMA 13B | 20 | 15 | 27 | 31 |

L'imitation large a baissé la précision et l'imitation locale l'a augmentée, comblant une grande part de l'écart sur la seule tâche qu'elle visait. La conclusion des auteurs est que distiller un comportement spécifique est bien plus faisable que d'égaler largement les capacités de ChatGPT. Ils ont aussi constaté qu'entraîner sur davantage de données ShareGPT-Mix nuisait à certaines évaluations par rapport au base model, ce qu'ils attribuent à un décalage de distribution entre les données de fine-tuning conversationnelles et les benchmarks, et ils signalent comme non résolu le fait de savoir si la régularisation ou le mélange de données de pré-entraînement le corrigerait.

### Pourquoi les évaluations et les benchmarks divergent

La réponse de l'article est que les modèles d'imitation apprennent le style, pas le contenu. Le tableau 2 compare les sorties de modèles d'imitation entraînés sur 20M, 80M et 150M tokens avec LLaMA de base et avec un second échantillon de ChatGPT :

| Métrique | LLaMA de base | 20M | 150M | Second échantillon de ChatGPT |
|---|---|---|---|---|
| Si ChatGPT produit une liste, le modèle aussi ? | 13% | 50% | 81% | 83% |
| Sorties sur un ton d'autorité, selon GPT-4 | 57% | 99% | 98% | 98% |
| Corrélation de Pearson de la longueur avec la sortie de ChatGPT | -0.11 | 0.51 | 0.62 | 0.67 |

Le tableau de l'article a aussi une colonne 80M, omise ici. Sur ces mesures de style, les modèles d'imitation s'approchent de ce que score un second échantillon de ChatGPT. Sur la factualité, ils restent faibles. La figure 2 de l'article montre une réponse d'imitation qui a la structure de ChatGPT et qui est complètement fausse, sur un ton assuré.

L'explication des auteurs sur la raison pour laquelle les évaluateurs l'ont manqué : des travailleurs de la foule sans expertise du domaine ni temps significatif peuvent être trompés par des réponses assurées et bien structurées. Ils en tirent deux leçons pour l'évaluation. Utiliser des experts du domaine ou des prompts difficiles, et noter que GPT-4 comme juge a montré le même biais.

### Ce que le passage à l'échelle apporte et n'apporte pas

C'est l'affirmation à bien comprendre exactement. Les auteurs disent que l'écart ne peut, avec les méthodes actuelles, être comblé que par une quantité encombrante de données d'imitation ou par un base model plus capable. Leur preuve pour la seconde moitié : augmenter la taille du base model a amélioré régulièrement les benchmarks automatiques, alors qu'augmenter les données d'imitation a donné peu d'amélioration ou des régressions (figure 4). Leur conclusion est que l'action à plus fort effet de levier est un meilleur base model.

Deux réserves comptent. La partie « quantité encombrante de données d'imitation » est un argument : ils disent qu'égaler ChatGPT largement exigerait un jeu de données plus proche de l'échelle du pré-entraînement, et notent qu'on ne sait pas si cela vaut la peine. Ils ne l'ont pas fait. Et la taille du base model est un indicateur de la qualité du base model, un point que leur propre note de bas de page fait. Le cadre est aussi celui de base models LLaMA et GPT-2 de 2023 imitant ChatGPT, ne traitez donc pas les tailles comme actuelles.

### Ce qui se transfère

L'article rapporte aussi ce qu'un élève reprend. Les modèles d'imitation sont devenus moins toxiques sur RealToxicityPrompts à mesure que les données d'imitation augmentaient, ce que les auteurs lisent comme le modèle apprenant à s'abstenir à la manière de ChatGPT (figure 5). Ils concluent que l'imitation est efficace quand vous avez un base model solide et voulez éviter d'annoter des données de fine-tuning. Un élève hérite des comportements que l'enseignant a été entraîné à montrer, y compris les schémas de refus, bien plus à bon compte qu'il n'hérite des connaissances.

### Réserves énoncées par les auteurs

Ils en nomment trois : les scores d'évaluation de ChatGPT peuvent être gonflés par une contamination dans un jeu de pré-entraînement inconnu, ils n'ont utilisé que de l'imitation supervisée et pas du RLHF ni des méthodes constitutionnelles, et ils ont utilisé une collecte de données simple. Une précaution de plus est la mienne : l'évaluation a utilisé 255 prompts après avoir écarté ceux de code et ceux qui n'étaient pas en anglais, donc le résultat des évaluations est plus étroit que « la qualité de ChatGPT ».

## Pratique

1. ▢ D'après le tableau 1, quelle part de l'écart avec ChatGPT sur Natural Questions l'imitation locale comble-t-elle pour LLaMA 13B et pour LLaMA 7B, et qu'a fait l'imitation large ?

<details markdown="1"><summary>Vérifier</summary>

Pour 13B, l'écart est 31 moins 20, soit 11, et NQ-synthetic ajoute 7 points, environ 64 % de celui-ci. Pour 7B, l'écart est 14 et elle ajoute 5, environ 36 %. L'imitation large ShareGPT-Mix a baissé la précision dans les deux cas, de 7 points pour 7B et de 5 pour 13B. Ce sont des nombres NQ sur un benchmark, pas une affirmation sur toutes les tâches.

</details>

2. ▢ Pourquoi les travailleurs de la foule ont-ils jugé les modèles d'imitation proches de ChatGPT alors que les benchmarks montraient peu de gain ?

    - a) Les évaluateurs connaissaient l'identité de chaque modèle
    - b) Les évaluateurs vérifiaient chaque affirmation indépendamment
    - c) Les évaluateurs favorisaient la seule longueur des réponses
    - d) Les évaluateurs récompensaient un style assuré et soigné

<details markdown="1"><summary>Vérifier</summary>

**d)** L'article dit que les modèles d'imitation copient le style de ChatGPT, et que des évaluateurs sans expertise du domaine ni temps pour vérifier les faits peuvent s'y laisser tromper. (b) est le contraire de ce qui s'est passé. (c) n'est pas l'explication de l'article, bien que la longueur des sorties des modèles ait été corrélée à celle de ChatGPT. (a) est faux : la comparaison était en aveugle.

</details>

3. ▢ Une équipe fait un fine-tuning d'un modèle 7B sur 200K dialogues de plus de style ChatGPT et rapporte un gain d'après des évaluations de la foule. Quelles deux choses demandez-vous avant de croire que le modèle égale l'enseignant ?

<details markdown="1"><summary>Indice</summary>

Pensez au type de mesure que l'article a trouvé divergent des évaluations, et à ce qui manquait aux tâches.

</details>

<details markdown="1"><summary>Vérifier</summary>

Demandez des benchmarks automatiques ciblés sur des tâches que les données d'entraînement ne couvrent pas beaucoup, comme les connaissances factuelles, le code ou le raisonnement, par rapport au base model avant le fine-tuning. Demandez qui étaient les évaluateurs et si certains avaient une expertise du domaine ou le temps de vérifier les faits. Le constat de l'article est que les évaluations peuvent monter alors que les benchmarks restent plats ou baissent. Les évaluations seules ne prouvent que le transfert du style.

</details>

4. ▢ Vous pouvez dépenser un budget fixe soit pour un million d'exemples larges de plus écrits par l'enseignant, soit pour passer à un base model deux fois plus grand. Que suggèrent les preuves de l'article, et que ne montrent-elles pas ?

<details markdown="1"><summary>Vérifier</summary>

Dans ses expériences, augmenter la taille du base model a amélioré régulièrement les benchmarks alors qu'augmenter les données d'imitation a donné un changement faible ou négatif, ce qui suggère le base model. Cela ne montre pas qu'aucune quantité de données d'imitation large n'aiderait, puisqu'ils n'ont pas testé de données proches de l'échelle du pré-entraînement, et cela ne couvre pas un cas spécifique à une tâche, où leur imitation locale a bien fonctionné. Pour une tâche étroite, les données peuvent être la meilleure dépense.

</details>

5. ▢ La leçon 13 demandait ce que les conditions d'un fournisseur autorisent. L'article liste des raisons d'imiter, des plus bénignes aux illégales, y compris des entreprises lançant des services concurrents du système propriétaire. Pourquoi cela compte-t-il pour un jeu de données de style ShareGPT ?

<details markdown="1"><summary>Vérifier</summary>

Parce qu'un jeu de données de sorties d'un autre fournisseur n'est utilisable que si ses conditions le permettent. Par exemple, les Terms of Use d'OpenAI listent, parmi ce qu'un utilisateur ne peut pas faire, l'usage de la sortie pour développer des modèles concurrents d'OpenAI (conditions du reste du monde, en vigueur au 1er janvier 2026). Vérifiez le texte actuel pour le fournisseur que vous avez utilisé. Je n'ai pas trouvé d'analyse indiquant si un jeu de données particulier était autorisé dans les sections de l'article que j'ai lues.

</details>

## Exercices en situation réelle

- [ ] Ouvrez la figure 1 et la figure 4 de l'article de Gudibande et écrivez une phrase sur la manière dont chacune soutient l'affirmation qu'un meilleur base model aide plus que davantage de données d'imitation.
- [ ] Prenez un modèle distillé que vous utilisez et consultez sa fiche de modèle. Notez quels types de preuves elle donne pour « égale l'enseignant » : évaluations humaines, scores de modèle juge ou benchmarks ciblés.
- [ ] Demain : sans notes, écrivez la différence entre imitation locale et large, le résultat sur Natural Questions, et pourquoi les évaluations de la foule étaient trompeuses.

## Pour aller plus loin

- [Ce dont l'élève hérite](../reference/what-the-student-inherits.md)
- [Article : "The False Promise of Imitating Proprietary LLMs", Gudibande et al., 2023](https://arxiv.org/abs/2305.15717)
- [Ressources](../RESOURCES.md)

---

Ça ne passe pas ? Relisez la source primaire en haut de page, car cette leçon la condense et c'est dans la condensation que la compréhension s'échappe. Consultez le [glossaire](../GLOSSARY.md) pour tout terme qui vous a paru glissant.

Si c'est la leçon elle-même qui n'est pas claire plutôt que la matière, c'est un défaut : [ouvrez une issue](https://github.com/TokenCemetery/teach/issues).
