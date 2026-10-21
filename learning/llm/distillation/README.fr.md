---
title: "Distillation"
description: "Distiller un grand modèle en un plus petit et le défendre : soft targets, loss sur les logits et au niveau de la séquence, données synthétiques, entraînement on-policy, et ce que l'élève a perdu"
type: topic
---

# Apprentissage : la distillation

Entraîner un modèle plus petit à faire ce que fait un plus grand en apprenant à partir des sorties de ce dernier, en sachant ce que chaque forme de distillation transmet et ce qu'elle ne peut pas transmettre. Finir capable de choisir entre distiller, quantifier et entraîner directement un petit modèle pour une tâche et un budget donnés, de mesurer honnêtement ce que l'élève a perdu, et de relire l'affirmation de quelqu'un selon laquelle un modèle distillé « égale l'enseignant ».

**Dernière leçon :** [27. Quand la réponse habituelle est fausse](lessons/0027-when-the-usual-answer-is-wrong.md)

## Objectif

- Expliquer pourquoi les soft targets d'un enseignant portent plus de signal d'entraînement que les hard labels, et régler la température et les poids des loss d'un run de distillation.
- Écrire la loss de distillation au niveau du token pour un LLM, choisir entre KL directe et KL inverse, et dire quand une incompatibilité de tokenizer exclut la distillation de logits.
- Distiller au niveau de la séquence ou à partir des données générées par un enseignant, et dire ce que chacune transmet que l'autre ne transmet pas.
- Construire un jeu de distillation synthétique filtré pour la qualité, et vérifier si la licence et les conditions d'utilisation de l'enseignant autorisent l'entraînement sur ses sorties.
- Expliquer le biais d'exposition, et dire quand la distillation on-policy vaut son coût face à un entraînement sur des sorties fixes de l'enseignant.
- Prédire ce qu'un élève héritera ou non de son enseignant, y compris les capacités qu'il ne peut pas absorber et les traits que personne ne voulait transmettre.
- Choisir une taille d'élève et un volume de données en comptant le coût propre de l'enseignant dans le budget.
- Mesurer ce qu'un élève a perdu par rapport à son enseignant et par rapport à un modèle de même taille entraîné sans enseignant.
- Choisir entre distiller, quantifier et faire directement du fine-tuning sur un petit modèle, relire l'affirmation de distillation de quelqu'un d'autre en nommant ce qu'elle cache, remplacer par un élève un modèle dont d'autres dépendent, et dire quand la réponse habituelle est la mauvaise.

## Contraintes

- Suppose l'aisance avec la lecture de Python et de PyTorch, et de savoir ce que sont une loss d'entropie croisée, un softmax et une boucle d'entraînement. Aucune connaissance préalable de la distillation, et aucun apprentissage par renforcement au-delà de l'idée d'échantillonner à partir d'un modèle.
- Fondé sur des articles et des rapports de modèles. Quand un chiffre est le résultat d'un seul article sur sa propre configuration, la leçon le dit, parce que les résultats de distillation dépendent fortement de l'enseignant, de l'élève et des données.
- La pratique des étapes 1 et 2 tourne sur un portable, avec un classifieur assez petit pour un CPU. Les exercices suivants distillent entre deux petits modèles ouverts, ce pour quoi un notebook GPU gratuit suffit.

## Hors périmètre

- Distiller un modèle de raisonnement par fine-tuning sur ses longues chaînes de raisonnement : voir [`llm/post-training`](../../llm/post-training/), leçon 0014. Cette leçon reste le cas du modèle de raisonnement ; ce parcours enseigne la distillation en général et y renvoie au lieu de la répéter.
- Faire du fine-tuning supervisé avec des adapters LoRA ou QLoRA : voir [`llm/finetuning`](../../llm/finetuning/). Ce parcours possède l'objectif et les données de la distillation ; la manière d'appliquer l'entraînement à moins de paramètres reste là-bas.
- Mener un run de pré-entraînement : voir [`llm/pretraining`](../../llm/pretraining/). La distillation comme signal de pré-entraînement est enseignée ici comme une loss et un choix de données (leçon 0007), pas comme un run de pré-entraînement.
- Construire une eval : voir [`llm/evals`](../../llm/evals/) et sa fiche [Go/No-Go](../../llm/evals/reference/go-no-go.md). Ce parcours utilise une eval pour comparer un élève à son enseignant et n'enseigne pas à nouveau comment en construire une.
- Réduire un modèle en abaissant sa précision : voir [`llm/quantization`](../../llm/quantization/). Ce parcours est l'autre manière de réduire un modèle, avec moins de paramètres, et la comparaison entre les deux fait partie de l'étape 9.
- L'élagage (pruning) comme méthode à part entière. La leçon 0007 le montre associé à la distillation dans Minitron, et n'enseigne que la moitié distillation.

## Le fil conducteur

Neuf étapes, de la raison pour laquelle un petit modèle peut apprendre d'un grand jusqu'au jugement nécessaire pour relire la distillation de quelqu'un d'autre. Une étape comprend plusieurs leçons et les frontières sont souples ; ce qui termine une étape, c'est la capacité acquise, pas le nombre de leçons.

| Étape | Leçons | Contenu | Terminée quand |
|---|---|---|---|
| 1. Pourquoi la distillation fonctionne | 0001 à 0003 | Enseignant et élève, soft targets et ce qu'elles portent, température et loss combinée | Vous savez dire pourquoi les soft targets enseignent plus que les hard labels et régler la température |
| 2. La distillation de logits pour les LLM | 0004 à 0007 | Distillation au niveau du token, KL directe et inverse, la contrainte du tokenizer partagé, la distillation comme signal de pré-entraînement | Vous savez écrire la loss au niveau du token et dire quand on ne peut pas l'utiliser |
| 3. La distillation au niveau de la séquence | 0008 à 0009 | Entraînement sur les sorties décodées de l'enseignant, et choix entre niveau du token et niveau de la séquence | Vous savez dire ce que transmet chaque niveau et en choisir un d'après ce que l'enseignant expose |
| 4. La distillation par données synthétiques | 0010 à 0013 | Données d'instruction générées, rationales et traces d'explication, filtrage, licences et conditions d'utilisation | Vous savez construire un jeu de distillation filtré et vérifier que son usage est permis |
| 5. La distillation on-policy | 0014 à 0016 | Biais d'exposition, GKD et MiniLLM, ce que l'entraînement on-policy coûte et rapporte | Vous savez dire quand la distillation on-policy mérite son coût |
| 6. Ce dont l'élève hérite | 0017 à 0019 | Fidélité contre généralisation, l'écart d'imitation, l'écart de capacité, les traits transmis sans intention | Vous savez prédire ce qu'un élève reprendra ou non de son enseignant |
| 7. Le dimensionnement | 0020 à 0021 | Lois d'échelle de la distillation, volume de données, le coût de l'enseignant dans le budget | Vous savez choisir une taille d'élève et un volume de données et défendre le calcul |
| 8. Mesurer ce qui a été perdu | 0022 à 0023 | Accord avec l'enseignant contre qualité sur la tâche, références, tâches held-out, contamination | Vous savez mesurer ce qu'un élève a perdu et défendre le chiffre |
| 9. Le jugement | 0024 à 0027 | Distiller, quantifier ou faire du fine-tuning sur un petit modèle, relire une affirmation, remplacer un modèle dont d'autres dépendent, quand la réponse habituelle est fausse | On vous fait confiance pour trancher sur une distillation et l'expliquer à quelqu'un d'autre |

## Leçons

Suivez-les dans l'ordre.

| # | Leçon | Enseigne |
|---|---|---|
| [0001](lessons/0001-what-distillation-buys.md) | Ce que la distillation apporte | Un petit élève entraîné à imiter un grand enseignant, et pourquoi l'imitation peut battre un entraînement de l'élève sur les seuls labels |
| [0002](lessons/0002-soft-targets.md) | Soft targets | Ce que portent les probabilités qu'un enseignant donne aux mauvaises réponses, et pourquoi elles forment un signal d'entraînement plus riche qu'un hard label |
| [0003](lessons/0003-temperature.md) | Température | Adoucir les deux distributions avec une température, la correction par T au carré, et le mélange avec la loss sur les hard labels |
| [0004](lessons/0004-token-level-distillation.md) | Distillation au niveau du token | Faire correspondre la distribution du token suivant de l'enseignant à chaque position d'une séquence |
| [0005](lessons/0005-forward-and-reverse-kl.md) | KL directe et KL inverse | Pourquoi la KL directe étale l'élève sur tous les modes de l'enseignant et la KL inverse l'oblige à s'engager sur un seul |
| [0006](lessons/0006-the-tokenizer-constraint.md) | La contrainte du tokenizer | Pourquoi la distillation de logits exige un vocabulaire partagé, et ce qu'abandonnent les méthodes inter-tokenizers |
| [0007](lessons/0007-distilling-during-pretraining.md) | Distiller pendant le pré-entraînement | Comment Gemma 2 et Minitron ont utilisé la distribution d'un enseignant comme signal d'entraînement à grande échelle, et ce que coûte le stockage des logits |
| [0008](lessons/0008-sequence-level-distillation.md) | Distillation au niveau de la séquence | Entraîner l'élève sur les sorties décodées de l'enseignant plutôt que sur ses distributions |
| [0009](lessons/0009-token-or-sequence.md) | Token ou séquence | Ce que transmet chaque niveau, les combiner, et choisir selon que l'enseignant expose des logits ou seulement du texte |
| [0010](lessons/0010-distilling-from-generated-data.md) | Distiller à partir de données générées | Construire un jeu d'instructions à partir des générations d'un enseignant, comme l'ont fait Self-Instruct et Alpaca |
| [0011](lessons/0011-rationales-and-explanation-traces.md) | Rationales et traces d'explication | Entraîner sur le raisonnement de l'enseignant autant que sur ses réponses, comme l'ont fait Distilling Step-by-Step et Orca |
| [0012](lessons/0012-filtering-synthetic-data.md) | Filtrer les données synthétiques | Vérifier, filtrer et dédupliquer les données générées avant d'entraîner dessus, parce que le volume ne répare pas les mauvais exemples |
| [0013](lessons/0013-licensing-and-terms.md) | Licences et conditions d'utilisation | Ce que les conditions d'un fournisseur et la licence d'un modèle ouvert vous autorisent à faire de ses sorties |
| [0014](lessons/0014-exposure-bias.md) | Biais d'exposition | Pourquoi un élève entraîné sur des préfixes de l'enseignant rencontre ses propres erreurs à l'inférence sans s'être entraîné dessus |
| [0015](lessons/0015-gkd-and-minillm.md) | GKD et MiniLLM | Échantillonner à partir de l'élève et évaluer avec l'enseignant, et les choix de divergence et de mélange qui vont avec |
| [0016](lessons/0016-on-policy-distillation-in-practice.md) | La distillation on-policy en pratique | Ce que la distillation on-policy coûte par pas, ce qu'elle rapporte, et comment Qwen3 l'a utilisée pour ses petits modèles |
| [0017](lessons/0017-fidelity-and-generalization.md) | Fidélité et généralisation | Pourquoi un élève qui généralise bien peut quand même être en désaccord avec son enseignant, et lequel des deux il vous faut |
| [0018](lessons/0018-the-imitation-gap.md) | L'écart d'imitation | Pourquoi imiter un modèle plus fort copie son style bien plus vite que sa capacité |
| [0019](lessons/0019-capacity-gap-and-hidden-traits.md) | Écart de capacité et traits cachés | Pourquoi un enseignant plus grand n'est pas toujours meilleur, et ce qui peut passer à un élève sans que personne l'ait voulu |
| [0020](lessons/0020-choosing-student-size.md) | Choisir la taille de l'élève | Ce que disent les lois d'échelle de la distillation sur le moment où distiller bat l'entraînement direct de l'élève |
| [0021](lessons/0021-data-volume-and-teacher-cost.md) | Volume de données et coût de l'enseignant | Compter l'inférence de l'enseignant dans le budget, et décider combien de données de distillation suffisent |
| [0022](lessons/0022-student-against-teacher.md) | Élève contre enseignant | Mesurer l'accord avec l'enseignant séparément de la qualité sur la tâche, une capacité à la fois |
| [0023](lessons/0023-an-honest-distillation-eval.md) | Une eval de distillation honnête | Les références, les tâches held-out et les contrôles de contamination qui rendent défendable un chiffre « égale l'enseignant » |
| [0024](lessons/0024-distill-quantize-or-fine-tune.md) | Distiller, quantifier ou faire du fine-tuning | Choisir entre moins de paramètres, moins de bits et l'entraînement direct d'un petit modèle, d'après la tâche et le budget |
| [0025](lessons/0025-reviewing-a-distillation-claim.md) | Relire une affirmation de distillation | Relire « notre petit modèle égale le grand » en nommant ce que la mesure a caché |
| [0026](lessons/0026-replacing-a-model-others-depend-on.md) | Remplacer un modèle dont d'autres dépendent | Déployer un élève à la place de son enseignant sans casser ceux qui dépendent de son comportement |
| [0027](lessons/0027-when-the-usual-answer-is-wrong.md) | Quand la réponse habituelle est fausse | Reconnaître quand la distillation est le mauvais choix, et trancher une affirmation contestée à partir de la source primaire |

## Référence

- [Glossaire](GLOSSARY.md) : termes de référence pour ce sujet
- [Ressources](RESOURCES.md) : sources fiables, chacune annotée avec ce qu'elle couvre
- [Loss de distillation](reference/distillation-losses.md) : soft targets, température, loss combinée, KL au niveau du token dans les deux sens et contrainte du tokenizer, issus des étapes 1 et 2
- [Séquences et données synthétiques](reference/sequence-and-synthetic-data.md) : distillation au niveau de la séquence, données générées, rationales, filtrage et questions de licence, issus des étapes 3 et 4
- [Distillation on-policy](reference/on-policy-distillation.md) : biais d'exposition, GKD et MiniLLM côte à côte, et quand l'entraînement on-policy est rentable, issus de l'étape 5
- [Ce dont l'élève hérite](reference/what-the-student-inherits.md) : fidélité, écart d'imitation, écart de capacité et traits involontaires, issus de l'étape 6
- [Dimensionner et mesurer](reference/sizing-and-measuring.md) : choisir la taille de l'élève et le volume de données avec le coût de l'enseignant, et une eval honnête élève contre enseignant, issus des étapes 7 et 8
- [Liste de contrôle de relecture d'une distillation](reference/distillation-review-checklist.md) : choisir entre distiller, quantifier et faire du fine-tuning, et les questions à poser à l'affirmation de distillation de quelqu'un d'autre, issues de l'étape 9

## Comment cela fonctionne

Chaque leçon est courte et autonome. Les corrigés sont repliés : rappelez-vous d'abord, puis ouvrez-les. Les exercices en situation réelle comptent plus que la lecture, et les espacer dans le temps est justement le but. Tout ce qui reste flou à la fin d'une leçon mérite d'être suivi jusqu'à sa source primaire avant de passer à la suite.
