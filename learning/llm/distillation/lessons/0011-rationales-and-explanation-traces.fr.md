---
title: "11. Rationales et traces d'explication"
description: "Entraîner sur le raisonnement de l'enseignant autant que sur ses réponses, comme l'ont fait Distilling Step-by-Step et Orca"
type: lesson
---

# Leçon 11. Rationales et traces d'explication

**Lien avec la mission :** La mission vous demande de construire un jeu de distillation qui mérite qu'on s'entraîne dessus, et la chose la plus riche qu'un enseignant puisse écrire pour une entrée est son raisonnement, que l'élève peut utiliser comme signal d'entraînement ou comme piège.
**Source primaire :** [Article : "Distilling Step-by-Step! Outperforming Larger Language Models with Less Training Data and Smaller Model Sizes", Hsieh et al., 2023](https://arxiv.org/abs/2305.02301)
**Prérequis :** [Leçon 10](0010-distilling-from-generated-data.md), [Rationale](../GLOSSARY.md), [Assistant enseignant](../GLOSSARY.md), [Écart de capacité](../GLOSSARY.md)

## Échauffement

1. ▢ Le filtre de Self-Instruct ne garde une nouvelle instruction que sous une condition portant sur ROUGE-L. Énoncez-la.

<details markdown="1"><summary>Vérifier</summary>

Sa similarité ROUGE-L avec toute instruction déjà dans le pool doit être inférieure à 0.7. La règle porte sur le membre existant le plus proche, ce qui évite que le pool se remplisse de quasi-copies (leçon 10).

</details>

2. ▢ La distillation à partir de données générées est de la distillation au niveau de la séquence avec un choix supplémentaire. Quel est ce choix ?

<details markdown="1"><summary>Vérifier</summary>

Les entrées. Dans la leçon 8, les entrées étaient un jeu d'entraînement fixe ; ici l'ensemble de départ, le prompt et le filtre déterminent quelles entrées existent (leçon 10).

</details>

3. ▢ Qu'est-ce qu'un [assistant enseignant](../GLOSSARY.md), et quel problème est-il censé atténuer ?

<details markdown="1"><summary>Vérifier</summary>

Un modèle de taille intermédiaire, distillé à partir de l'enseignant puis utilisé comme enseignant d'un élève plus petit. Il est censé atténuer l'[écart de capacité](../GLOSSARY.md) : la baisse de qualité de l'élève qui peut apparaître quand l'enseignant est bien plus grand que lui.

</details>

## À savoir

### Une rationale est une cible supplémentaire

Une [rationale](../GLOSSARY.md) est le raisonnement intermédiaire qu'un enseignant écrit avant sa réponse. Les labels seuls disent à l'élève quelle est la réponse. Une rationale montre aussi comment l'enseignant y est arrivé, ce qui donne à l'élève davantage à apprendre de chaque exemple.

Distilling Step-by-Step (Hsieh et al., 2023) utilise les rationales d'une manière particulière. Il sollicite un grand modèle avec quelques exemples travaillés, environ 10 par tâche, pour qu'il écrive une rationale avec son label, ici le modèle PaLM 540B (section 3.1 et section sur les limites). Il entraîne ensuite un petit modèle, T5, à produire les deux.

### Les rationales comme seconde tâche, pas comme entrée

Il y a deux manières évidentes d'utiliser une rationale. Ils ont choisi la seconde.

1. **Comme entrée.** Entraîner l'élève à prédire le label à partir du texte plus la rationale. Cela exige qu'un grand modèle écrive aussi une rationale au moment du test, donc le grand modèle est toujours nécessaire en production (section 3.2).
2. **Comme seconde sortie.** Entraîner l'élève à produire le label et, comme tâche séparée, la rationale. La loss est la loss du label plus un poids fois la loss de la rationale. Un préfixe de tâche dit au modèle laquelle produire : un préfixe `[label]` sur l'entrée demande le label, un préfixe `[rationale]` demande la rationale (section 3.2).

Le second schéma signifie qu'aucune rationale n'est générée au moment du test : l'élève ne prédit que le label, et la tâche d'écriture de rationale a façonné ce qu'il a appris en chemin. Le coût est un peu de calcul d'entraînement supplémentaire.

Traiter la rationale comme une seconde tâche compte. Quand les auteurs ont à la place concaténé la rationale et le label en une seule séquence cible, l'élève a parfois fait moins bien qu'un fine-tuning simple (tableau 2, T5 220M, précision) :

| Méthode | e-SNLI | ANLI | CQA | SVAMP |
|---|---|---|---|---|
| Fine-tuning standard | 88.38 | 43.58 | 62.19 | 62.63 |
| Tâche unique, rationale et label ensemble | 88.88 | 43.50 | 61.37 | 63.00 |
| Multitâche, label et rationale séparés | 89.51 | 49.58 | 63.29 | 65.50 |

Sur ANLI et CQA, la ligne à tâche unique est en dessous du fine-tuning standard. Leur lecture est que les rationales doivent être traitées avec soin pour être utiles.

### Ce que cela a apporté

Ce sont les résultats de l'article sur quatre benchmarks, trois types de tâches, des élèves T5 et un enseignant PaLM :

- **Moins de données.** Avec un T5 220M et des labels humains, distiller étape par étape a battu le fine-tuning standard sur l'ensemble complet d'e-SNLI en n'en utilisant que 12.5 %. Les réductions du nombre d'exemples d'entraînement nécessaires pour battre le fine-tuning standard sur données complètes étaient de 75 % sur ANLI, 25 % sur CQA et 20 % sur SVAMP (section 4.1). Avec des données non labellisées seulement, 12.5 % de l'ensemble non labellisé d'e-SNLI suffisaient pour battre la distillation de tâche standard sur la totalité.
- **Plus petit que l'enseignant.** Un T5 770M affiné a surpassé PaLM 540B sollicité en few-shot sur ANLI en utilisant 80 % du jeu d'entraînement, alors que le fine-tuning standard du même T5 ne pouvait pas égaler PaLM même avec 100 % (résumé ; section 4.3, figure 8). Sur e-SNLI, un modèle de 220M y est parvenu avec 0.1 % des données.
- **Une source de rationales plus faible a quand même aidé.** Les rationales d'un GPT-NeoX 20B ont donné un gain plus faible que celles de PaLM (ANLI 48.15 contre 49.58, fine-tuning standard 43.58) (tableau 1).

Gardez les limites en vue. Les benchmarks sont des tâches de classification et de réponse courte, les élèves sont des modèles T5 spécifiques à une tâche et non des modèles de chat, et le point de comparaison est un PaLM sollicité par prompt. Rien de cela ne dit ce qui se passe quand on distille un assistant généraliste. L'article note aussi que son prompting few-shot exige des exemples de démonstration pour chaque tâche.

### Orca : des traces d'explication à l'échelle d'un assistant

Orca (Mukherjee et al., 2023) applique le même instinct au suivi d'instructions général. Sa motivation est qu'un élève entraîné uniquement sur les réponses finales d'un enseignant apprend peu de la façon dont l'enseignant a pensé. Deux idées :

- **Explanation tuning avec des messages système.** Chaque exemple d'entraînement est un triplet message système, requête utilisateur et réponse de l'enseignant. Ils ont rédigé à la main 16 messages système qui évoquent différents styles de réponse, comme demander au modèle de penser étape par étape et de justifier ses étapes, et les ont échantillonnés sur des tâches tirées de la collection FLAN-v2 (section 3.1).
- **ChatGPT comme enseignant intermédiaire.** Ils ont collecté 5 millions de réponses de ChatGPT (FLAN-5M), puis pris 1 million de ces requêtes pour des réponses de GPT-4 (FLAN-1M), et ont entraîné Orca d'abord sur les données de ChatGPT puis sur celles de GPT-4. Leurs raisons déclarées sont l'écart de capacité, puisqu'un élève de 13B est bien plus petit que GPT-4, et le coût et le temps : ils ont collecté 5 fois plus de ChatGPT que de GPT-4 (section 3.1.3).

C'est un [assistant enseignant](../GLOSSARY.md) utilisé à dessein, avec un cursus de 5M puis 1M. Les auteurs rapportent qu'Orca-13B dépasse Vicuna-13B de plus de 100 % sur Big-Bench Hard et de 42 % sur AGIEval, à parité avec ChatGPT sur BBH, et environ 4 points derrière ChatGPT sur les examens professionnels avec un message système optimisé (résumé). Ils rapportent aussi que Vicuna paraît proche de ChatGPT sous un juge GPT-4 (92 %) mais ne conserve que 64 % sur les examens et 48 % sur BBH par rapport aux labels humains, ce pour quoi ils ont évalué sur des benchmarks de raisonnement.

Ce sont les évaluations des auteurs d'Orca eux-mêmes, sur leurs benchmarks choisis. Savoir si les traces d'explication comblent un écart de capacité, ou surtout l'écart de style, est la question de la leçon 18.

### Les modèles de raisonnement relèvent du parcours suivant

Distiller un modèle de raisonnement, par fine-tuning sur ses longues chaînes de raisonnement, est enseigné dans le parcours [post-training](../../post-training/). Les rationales ici sont de courtes explications qui aident un petit modèle de tâche, et la distillation d'un modèle de raisonnement est un cas plus grand de la même idée.

## Pratique

1. ▢ Dans Distilling Step-by-Step, pourquoi la rationale n'est-elle pas nécessaire au moment du test ?

    - a) La rationale est cachée dans le token du label lui-même
    - b) L'élève mémorise chaque rationale du jeu d'entraînement
    - c) L'enseignant réécrit chaque rationale en production
    - d) La tâche du label tourne seule une fois le modèle entraîné

<details markdown="1"><summary>Vérifier</summary>

**d)** La rationale est une seconde sortie avec son propre préfixe, entraînée en parallèle du label, donc au moment du test vous ne demandez que le label. (b) n'est pas ce que fait la méthode. (c) décrit le schéma rejeté où la rationale est une entrée, qui garde le grand modèle en production. (a) invente un mécanisme que l'article n'a pas.

</details>

2. ▢ Dans le tableau 2, la ligne à tâche unique pour CQA est 61.37 et le fine-tuning standard 62.19. Que dit cela de l'ajout naïf de rationales ?

<details markdown="1"><summary>Vérifier</summary>

Ajouter la rationale dans la cible comme une seule séquence a rendu l'élève moins bon que de ne rien faire sur CQA (et légèrement moins bon sur ANLI, 43.50 contre 43.58). Le gain vient de la façon dont la rationale est utilisée, comme tâche séparée, pas du fait d'avoir des rationales. C'est le résultat de l'article sur sa configuration.

</details>

3. ▢ Un élève reçoit 5 millions de réponses de ChatGPT puis 1 million de réponses de GPT-4. Quel est le rapport, et quelles deux raisons les auteurs donnent-ils pour l'ordre et la taille ?

<details markdown="1"><summary>Vérifier</summary>

5 contre 1. Ils donnent l'écart de capacité, puisqu'un enseignant intermédiaire plus proche de la capacité de l'élève facilite l'imitation, et le coût et le temps, puisque ChatGPT était plus rapide et moins cher à interroger, ils en ont donc collecté 5 fois plus que de GPT-4.

</details>

4. ▢ Votre équipe lit le résultat du T5 770M contre PaLM 540B et propose de distiller un assistant de chat généraliste de la même façon, avec un modèle de 770M. Que répondez-vous ?

<details markdown="1"><summary>Indice</summary>

Regardez le type de tâche, le type d'élève et ce qu'est la comparaison.

</details>

<details markdown="1"><summary>Vérifier</summary>

Le résultat porte sur quatre benchmarks, avec des élèves T5 spécifiques à une tâche et un PaLM sollicité en few-shot comme référence, et le chiffre de 80 % des données concerne ANLI. Il ne couvre pas un assistant généraliste. Une proposition pour un modèle de chat a besoin de sa propre évaluation sur les tâches qui vous importent, face à une référence entraînée sans les rationales.

</details>

5. ▢ Un enseignant écrit une rationale assurée mais fausse et un label faux. Laquelle des deux méthodes de cette leçon entraînerait l'élève sur les deux, et que feriez-vous avant d'entraîner ?

<details markdown="1"><summary>Vérifier</summary>

Les deux le feraient : la rationale et le label sont des cibles dans Distilling Step-by-Step, et une trace d'explication fait partie de la réponse dans Orca. Filtrez d'abord. Quand un vérificateur existe, ne gardez que les exemples dont la réponse est vérifiée correcte ; sinon échantillonnez et inspectez. La leçon 12 couvre cela.

</details>

## Exercices en situation réelle

- [ ] Trouvez le tableau 2 de l'article Orca et lisez les 16 messages système. Choisissez-en trois et prédisez comment la même requête serait traitée différemment sous chacun.
- [ ] Écrivez un prompt de rationale pour une tâche que vous connaissez, avec deux exemples travaillés, et exécutez-le sur n'importe quel modèle à votre disposition. Vérifiez à la main une rationale pour y chercher une erreur que la réponse finale cache.
- [ ] Demain : sans notes, expliquez pourquoi la rationale est une seconde sortie et non une entrée, et ce que cela fait au coût au moment du test.

## Pour aller plus loin

- [Séquences et données synthétiques](../reference/sequence-and-synthetic-data.md)
- [Article : "Distilling Step-by-Step! Outperforming Larger Language Models with Less Training Data and Smaller Model Sizes", Hsieh et al., 2023](https://arxiv.org/abs/2305.02301)
- [Article : "Orca: Progressive Learning from Complex Explanation Traces of GPT-4", Mukherjee et al., 2023](https://arxiv.org/abs/2306.02707)
- [Post-training](../../post-training/)
- [Ressources](../RESOURCES.md)

---

Ça ne passe pas ? Relisez la source primaire en haut de page, car cette leçon la condense et c'est dans la condensation que la compréhension s'échappe. Consultez le [glossaire](../GLOSSARY.md) pour tout terme qui vous a paru glissant.

Si c'est la leçon elle-même qui n'est pas claire plutôt que la matière, c'est un défaut : [ouvrez une issue](https://github.com/TokenCemetery/teach/issues).
