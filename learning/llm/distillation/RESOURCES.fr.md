---
title: "Ressources"
description: "Sources fiables pour la distillation des connaissances des LLM"
type: resources
---

# Ressources sur la distillation

## Connaissances

### Les fondations

- [Article : "Distilling the Knowledge in a Neural Network", Hinton, Vinyals et Dean, 2015](https://arxiv.org/abs/1503.02531)
  L'article qui a donné son nom à la méthode : soft targets, température, correction de gradient par T au carré et loss combinée, avec des expériences sur MNIST et sur la parole. À utiliser pour : l'étape 1, à la source.
- [Article : "A Survey on Knowledge Distillation of Large Language Models", Xu et al., 2024](https://arxiv.org/abs/2402.13116)
  Une carte de la distillation des LLM organisée selon ce qu'on obtient de l'enseignant et la manière d'entraîner l'élève dessus. À utiliser pour : situer une méthode dans la famille plus large avant de lire son propre article.
- [Article : "DistilBERT, a distilled version of BERT: smaller, faster, cheaper and lighter", Sanh et al., 2019](https://arxiv.org/abs/1910.01108)
  Une distillation détaillée d'un transformer pendant le pré-entraînement, avec une triple loss composée de termes de distillation, de modélisation de langage masqué et d'embedding par cosinus. À utiliser pour : une recette complète avec une ablation de chaque terme de la loss.

### Distillation de logits et au niveau de la séquence

- [Article : "Sequence-Level Knowledge Distillation", Kim et Rush, 2016](https://arxiv.org/abs/1606.07947)
  Distillation au niveau du mot contre au niveau de la séquence pour la traduction, et entraînement sur la sortie par beam search de l'enseignant. À utiliser pour : les étapes 2 et 3, la formulation d'origine des deux niveaux.
- [Article : "MiniLLM: On-Policy Distillation of Large Language Models", Gu et al., 2023](https://arxiv.org/abs/2306.08543)
  Le plaidoyer pour la KL inverse dans la distillation générative, optimisée avec une méthode de gradient de politique sur des échantillons de l'élève. À utiliser pour : KL directe contre KL inverse, et une forme de distillation on-policy.
- [Article : "Towards Cross-Tokenizer Distillation: the Universal Logit Distillation Loss for LLMs", Boizard et al., 2024](https://arxiv.org/abs/2402.12030)
  Une loss fondée sur le transport optimal qui compare des vecteurs de probabilités triés, pour que l'enseignant et l'élève n'aient pas besoin de partager un vocabulaire. À utiliser pour : ce que fait et ce qu'abandonne la distillation inter-tokenizers.
- [Article : "Gemma 2: Improving Open Language Models at a Practical Size", Gemma Team, 2024](https://arxiv.org/abs/2408.00118)
  Entraînement des modèles 2B et 9B par distillation des connaissances à partir d'un enseignant plus grand, au lieu de la prédiction du token suivant. À utiliser pour : la distillation comme signal de pré-entraînement.
- [Article : "Compact Language Models via Pruning and Knowledge Distillation", Muralidharan et al., 2024](https://arxiv.org/abs/2407.14679)
  Minitron : élaguer un modèle entraîné et le ré-entraîner par distillation à partir de l'original, sur une petite fraction des tokens d'entraînement d'origine. À utiliser pour : la distillation comme étape de récupération après l'élagage.
- [Article : "LLM Pruning and Distillation in Practice: The Minitron Approach", Sreenivas et al., 2024](https://arxiv.org/abs/2408.11796)
  La recette Minitron appliquée à Llama 3.1 8B et Mistral NeMo 12B, avec notamment une correction préalable de l'enseignant sur les données de distillation. À utiliser pour : une seconde application, plus récente, de la même recette.

### Distillation par données synthétiques

- [Article : "Self-Instruct: Aligning Language Models with Self-Generated Instructions", Wang et al., 2022](https://arxiv.org/abs/2212.10560)
  Amorcer des données d'instruction à partir des propres générations d'un modèle, avec un filtrage des quasi-doublons et des exemples invalides. À utiliser pour : la manière dont se construit un jeu d'instructions généré.
- [Billet : "Alpaca: A Strong, Replicable Instruction-Following Model", Stanford CRFM, 2023](https://crfm.stanford.edu/2023/03/13/alpaca.html)
  Fine-tuning de LLaMA 7B sur 52 000 instructions générées par text-davinci-003 avec la méthode Self-Instruct, son coût, ainsi que ses limites déclarées et ses restrictions de licence. À utiliser pour : le run d'imitation économique canonique.
- [Article : "Distilling Step-by-Step! Outperforming Larger Language Models with Less Training Data and Smaller Model Sizes", Hsieh et al., 2023](https://arxiv.org/abs/2305.02301)
  Entraîner un petit modèle à produire les rationales de l'enseignant comme seconde tâche à côté de ses labels. À utiliser pour : ce que les rationales apportent par rapport aux seuls labels.
- [Article : "Orca: Progressive Learning from Complex Explanation Traces of GPT-4", Mukherjee et al., 2023](https://arxiv.org/abs/2306.02707)
  Imitation de traces d'explication obtenues avec des system prompts, avec ChatGPT comme enseignant intermédiaire avant GPT-4. À utiliser pour : les traces d'explication et un assistant enseignant à l'échelle des LLM.
- [Article : "Textbooks Are All You Need", Gunasekar et al., 2023](https://arxiv.org/abs/2306.11644)
  phi-1 : un petit modèle de code entraîné sur des données web filtrées et sur des manuels et exercices synthétiques générés par GPT-3.5. À utiliser pour : qualité des données contre volume de données.
- [Article : "DeepSeek-R1: Incentivizing Reasoning Capability in LLMs via Reinforcement Learning", DeepSeek-AI, 2025](https://arxiv.org/abs/2501.12948)
  Distillation d'un modèle de raisonnement en modèles Qwen et Llama plus petits par fine-tuning sur ses échantillons triés, comparée à un RL mené directement sur le petit modèle (annexe F.1). À utiliser pour : les données synthétiques par échantillonnage par rejet, et la leçon de post-training à laquelle ce parcours renvoie.

### Distillation on-policy

- [Article : "On-Policy Distillation of Language Models: Learning from Self-Generated Mistakes", Agarwal et al., 2023](https://arxiv.org/abs/2306.13649)
  Distillation généralisée des connaissances : entraînement sur des séquences générées par l'élève, avec un choix de divergence et un mélange de données fixes et on-policy. À utiliser pour : l'étape 5, à la source.
- [Article : "Qwen3 Technical Report", Qwen Team, 2025](https://arxiv.org/abs/2505.09388)
  Distillation du fort vers le faible des petits modèles Qwen3, avec une étape off-policy suivie d'une étape on-policy, comparée à du RL sur les mêmes modèles. À utiliser pour : la distillation on-policy dans une famille de modèles de production.
- [Doc : "Generalized Knowledge Distillation Trainer", Hugging Face TRL](https://huggingface.co/docs/trl/main/en/gkd_trainer)
  L'implémentation de GKD dans TRL et ses paramètres `lmbda`, `beta` et `seq_kd`. À utiliser pour : exécuter la distillation on-policy plutôt que d'en lire une description.
- [Doc : "General Online Logit Distillation (GOLD) Trainer", Hugging Face TRL](https://huggingface.co/docs/trl/main/en/gold_trainer)
  Le trainer de TRL qui étend GKD avec la loss Universal Logit Distillation, en alignant des segments de texte pour que l'enseignant et l'élève puissent utiliser des tokenizers différents. À utiliser pour : ce dont a besoin un run on-policy inter-tokenizers.

### Ce dont l'élève hérite

- [Article : "Does Knowledge Distillation Really Work?", Stanton et al., 2021](https://arxiv.org/abs/2106.05945)
  Les élèves n'arrivent souvent pas à égaler leurs enseignants même quand ils en ont la capacité, et une meilleure généralisation n'exige pas une meilleure fidélité. Les expériences portent surtout sur la classification d'images, avec une tâche textuelle. À utiliser pour : séparer la fidélité de la qualité sur la tâche.
- [Article : "The False Promise of Imitating Proprietary LLMs", Gudibande et al., 2023](https://arxiv.org/abs/2305.15717)
  Des modèles d'imitation jugés proches de ChatGPT par des travailleurs de la foule ont comblé peu de l'écart sur des benchmarks ciblés. À utiliser pour : l'écart d'imitation et la façon dont les évaluations de préférence humaine l'ont masqué.
- [Article : "Improved Knowledge Distillation via Teacher Assistant", Mirzadeh et al., 2019](https://arxiv.org/abs/1902.03393)
  La qualité de l'élève chute quand l'écart entre l'enseignant et l'élève devient trop grand, et un assistant de taille intermédiaire en récupère une partie ; les gains de ses expériences en vision sont faibles. À utiliser pour : l'écart de capacité.
- [Article : "On the Efficacy of Knowledge Distillation", Cho et Hariharan, 2019](https://arxiv.org/abs/1910.01348)
  Des enseignants plus précis ne font pas toujours de meilleurs élèves, et arrêter l'enseignant plus tôt peut aider. À utiliser pour : un second récit de l'écart de capacité.
- [Article : "Subliminal Learning: Language models transmit behavioral traits via hidden signals in data", Cloud et al., 2025](https://arxiv.org/abs/2507.14805)
  Un élève entraîné sur des suites de nombres produites par un enseignant a repris les traits de ce dernier, quand les deux partageaient un base model. À utiliser pour : ce que le filtrage des données ne peut pas retirer.

### Dimensionnement

- [Article : "Distillation Scaling Laws", Busbridge et al., 2025](https://arxiv.org/abs/2502.08606)
  Une loi d'échelle de la qualité de l'élève en fonction de sa taille, des tokens de distillation et de la qualité de l'enseignant, et du moment où la distillation bat l'entraînement supervisé du même élève. Rapporte aussi que la meilleure température de distillation était 1 dans sa configuration (annexe G.2). À utiliser pour : l'étape 7 à la source, et le contrepoint à une température supérieure à 1 sur un LLM.

### Licences et conditions d'utilisation

- [Conditions : "Terms of Use", OpenAI](https://openai.com/policies/row-terms-of-use/)
  Les conditions grand public d'OpenAI pour les utilisateurs hors de l'EEE, de la Suisse et du Royaume-Uni, qui comptent l'usage des sorties pour développer des modèles concurrents d'OpenAI parmi ce qu'un utilisateur ne doit pas faire. À utiliser pour : ce que disent les conditions d'un fournisseur hébergé sur l'entraînement à partir de ses sorties.
- [Licence : "Llama 3.1 Community License Agreement", Meta](https://github.com/meta-llama/llama-models/blob/main/models/llama3_1/LICENSE)
  Une licence à poids ouverts qui autorise l'usage des sorties du modèle pour améliorer un autre modèle, à condition que le nom du modèle obtenu commence par « Llama » lorsqu'il est distribué. À utiliser pour : ce que dit la licence d'un modèle ouvert sur l'entraînement à partir de ses sorties.

## Lacunes

- Le billet de Thinking Machines sur la distillation on-policy est largement cité pour sa comparaison de coût avec le RL, mais son site refuse les lectures scriptées et intégrées à l'application, donc aucun chiffre qui en vient n'est utilisé ici. L'étape 5 repose à la place sur les articles GKD, MiniLLM et Qwen3.
- Les conditions d'utilisation et les licences changent sans version qu'une leçon puisse épingler. La leçon 0013 les cite telles qu'elles étaient lues quand ce parcours a été écrit ; revérifiez la source avant de vous y fier.
