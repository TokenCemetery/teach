---
title: "Ce dont l'élève hérite"
description: "Fidélité, écart d'imitation, écart de capacité et traits involontaires, avec le cadre et les nombres de chaque source"
type: reference
---

# Ce dont l'élève hérite : fidélité, écart d'imitation, écart de capacité et traits cachés

L'étape 6 condensée pour la consultation. La [leçon 17](../lessons/0017-fidelity-and-generalization.md) couvre la fidélité contre la généralisation, la [leçon 18](../lessons/0018-the-imitation-gap.md) l'écart d'imitation, et la [leçon 19](../lessons/0019-capacity-gap-and-hidden-traits.md) l'écart de capacité et les traits cachés.

## Quatre manières dont un élève peut différer de son enseignant

| Écart | Ce qui diffère | Source | Cadre |
|---|---|---|---|
| Fidélité | Prédictions sur les mêmes entrées, même quand la précision est similaire | Stanton et al., 2021 | Classification d'images, avec MNIST, CIFAR-100, ImageNet et le sentiment IMDB en annexe |
| Imitation | Style copié vite, capacité non | Gudibande et al., 2023 | Élèves LLaMA et GPT-2 imitant ChatGPT |
| Capacité | Un très grand enseignant peut donner un élève moins bon | Mirzadeh et al., 2019, et Cho et Hariharan, 2019 | CNN et ResNet sur CIFAR et ImageNet |
| Traits cachés | Un trait passe à travers des données qui ne le mentionnent pas | Cloud et al., 2025 | Famille GPT-4.1 et Qwen2.5-7B, plus un petit cas MNIST |

Seuls deux des quatre ont été testés sur des modèles de langage, et aucune des preuves d'écart de capacité ici ne vient de LLM.

## Mesurer la fidélité

| Métrique | Définition | Exige |
|---|---|---|
| Accord top-1 | Fraction d'entrées où l'élève et l'enseignant choisissent le même meilleur label | Les prédictions de l'enseignant |
| KL prédictive | KL(enseignant, élève) moyenne sur les entrées | La distribution complète de l'enseignant |
| Contrôle | Un second élève distillé de la même façon à partir d'un enseignant indépendant | Un second run de distillation |

La précision ne borne pas étroitement l'accord. Avec une précision de l'enseignant de 93 % et de l'élève de 91 %, l'accord se situe entre 84 % et 98 %.

## Stanton et al. en nombres

| Observation | Nombre ou direction |
|---|---|
| LeNet-5 sur MNIST avec assez de données | Plus de 99 % d'accord top-1 au test |
| Auto-distillation de ResNet-56 sur CIFAR-100, plus grand jeu | Accord au test sous 80 % |
| Idem, avec 50k images GAN ajoutées, accord sur les données de distillation elles-mêmes | 95 % |
| Idem, avec forte augmentation combinée, accord à l'entraînement en auto-distillation | Environ 60 % |
| Auto-distillation de ResNet-20, accord à l'entraînement avec SGD à 300 époques et à 5,000 époques | 78.95 % et 83.3 % |
| Auto-distillation, plus de données | Fidélité en hausse, précision au test en baisse |
| Enseignant en ensemble de 3, plus de données | Fidélité et précision toutes deux en hausse |

Leur explication est l'optimisation : l'élève ne reproduit pas l'enseignant même sur les données sur lesquelles il s'entraîne. Plus de données de distillation aident l'identification de la fonction de l'enseignant et rendent l'optimisation plus difficile.

## Gudibande et al. en nombres

| Observation | Nombre |
|---|---|
| Évaluations de la foule des sorties d'imitation comme égales ou meilleures que ChatGPT | Environ 70 % |
| Natural Questions, LLaMA 7B : base, imitation large, imitation locale, ChatGPT | 17, 10, 22, 31 |
| Natural Questions, LLaMA 13B : base, imitation large, imitation locale, ChatGPT | 20, 15, 27, 31 |
| Sorties sur un ton d'autorité : LLaMA de base contre modèles d'imitation | 57 % contre 98 % à 99 % |

Leur affirmation : avec les méthodes actuelles, l'écart ne se comble qu'avec une quantité encombrante de données d'imitation ou un base model plus capable, et un meilleur base model a davantage aidé que plus de données d'imitation dans leurs expériences. L'imitation locale d'une tâche a fonctionné bien mieux que l'imitation large. Les modèles d'imitation sont aussi devenus moins toxiques, en apprenant à s'abstenir comme l'enseignant.

## Preuves sur l'écart de capacité

| Source | Constat | Remède essayé |
|---|---|---|
| Mirzadeh et al. | La précision d'un élève à 2 couches a monté puis baissé quand les enseignants passaient de 4 à 10 couches | Assistant enseignant. Gain par rapport à la distillation standard de 0.33 à 0.41 point sur ResNet, 0.94 point sur le CNN simple avec CIFAR-10 |
| Cho et Hariharan | ResNet18 sur ImageNet : de zéro 30.24 % d'erreur, 30.57 %, 30.79 % et 30.95 % avec des enseignants ResNet18, 34 et 50 | La distillation arrêtée tôt a donné 29.01 %, 29.16 % et 29.35 %. Les enseignants arrêtés tôt ont aidé sur CIFAR-10. L'enchaînement à travers un modèle moyen n'a pas aidé |
| Gu et al. (MiniLLM) | L'élève GPT-2 125M s'est amélioré avec des enseignants de 340M, 760M et 1.5B | Aucun écart vu sur cette plage, une famille |

Les deux articles de vision sont en désaccord sur le fait qu'un modèle intermédiaire aide. Testez sur votre propre paire.

## Traits cachés, Cloud et al.

| Élément | Détail |
|---|---|
| Montage | Un enseignant avec un trait génère des données sans rapport, les données sont filtrées, un élève du même base model est affiné dessus |
| Préférence pour la chouette | Environ 12 % avant, plus de 60 % après, à partir de nombres seulement |
| Désalignement à partir de nombres | Presque 10 % de réponses désalignées, contre 0 % pour la base et moins de 1 % pour les contrôles |
| Désalignement à partir d'une chaîne de raisonnement filtrée | D'environ 0 % à 8 %, contrôles sous 1 % |
| Détection | Les classifieurs sollicités par prompt et l'apprentissage en contexte n'ont pas détecté le trait de façon fiable |
| Condition | Base model partagé. GPT-4.1 nano vers Qwen2.5 n'a pas transmis. GPT-4o et GPT-4.1 l'ont fait, probablement une initialisation partagée |
| Limites ouvertes | Tâches artificielles, et quels traits se transmettent et quand reste inconnu |

## Symptôme, cause probable, contrôle

| Symptôme | Cause probable | Contrôle |
|---|---|---|
| L'élève égale l'enseignant en précision mais les sorties diffèrent | Faible fidélité | Accord top-1 et KL prédictive sur des entrées held-out, avec un contrôle par enseignant indépendant |
| Évaluations de la foule ou scores de juge élevés, benchmarks ciblés plats | Style copié, capacité non | Benchmarks sur des tâches que les données couvrent à peine, par rapport au base model |
| Élève moins bon que celui d'un enseignant plus petit | Écart de capacité | Direct, un modèle intermédiaire, enseignant arrêté tôt, par rapport à une référence de zéro |
| Un comportement indésirable apparaît bien que les données soient propres | Trait caché issu d'un base model partagé | Évaluer directement l'élève sur le comportement, et envisager un autre base model |
| L'élève refuse comme son enseignant | Le comportement de refus se transfère avec le style | Comparer les taux de refus avec l'enseignant sur un jeu de prompts fixe |

## Ce que rien de cela ne couvre

- Aucune source lue ici ne montre qu'un élève copie les erreurs factuelles de son enseignant.
- L'écart de capacité et l'écart de fidélité ont été mesurés sur des modèles de vision, pas sur des LLM.
- L'apprentissage subliminal a été montré sur des tâches artificielles, et le blocage par un base model différent était une observation dans ces expériences, pas une garantie.
