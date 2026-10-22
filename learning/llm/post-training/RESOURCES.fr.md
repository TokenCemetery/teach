---
title: "Ressources"
description: "Sources fiables pour le post-training des LLM"
type: resources
---

# Ressources sur le post-training des LLM

## Connaissances

- [Article : "Training language models to follow instructions with human feedback", Ouyang et al., 2022](https://arxiv.org/abs/2203.02155)
  L'article InstructGPT. Définit le pipeline SFT, reward model, PPO que la plupart des travaux RLHF ont suivi depuis, et mesure la taxe d'alignement par rapport à un modèle uniquement pré-entraîné. À utiliser pour : les étapes 1, 2, 3, et le cadrage de la taxe d'alignement de l'étape 9.
- [Article : "Proximal Policy Optimization Algorithms", Schulman et al., 2017](https://arxiv.org/abs/1707.06347)
  Introduit PPO comme algorithme général d'apprentissage par renforcement, indépendant des modèles de langage. À utiliser pour : l'algorithme central de l'étape 4, à lire avant son application propre aux modèles de langage.
- [Article : "Training a Helpful and Harmless Assistant with Reinforcement Learning from Human Feedback", Bai et al., 2022](https://arxiv.org/abs/2204.05862)
  Le récit d'Anthropic de la même recette SFT vers RLHF à l'échelle de la production, y compris les endroits où le reward hacking et la sur-optimisation contre le reward model sont apparus en pratique. À utiliser pour : le contenu sur le reward hacking de l'étape 3 et le récit de ce qui tourne réellement mal à l'étape 4.
- [Article : "Direct Preference Optimization: Your Language Model is Secretly a Reward Model", Rafailov et al., 2023](https://arxiv.org/abs/2305.18290)
  Dérive une récompense sous forme close impliquée par une policy et un modèle de référence, ce qui remplace le reward model séparé et la boucle de RL par une seule loss de type supervisé sur des paires de préférence. À utiliser pour : la dérivation centrale de l'étape 5.
- [Article : "DeepSeekMath: Pushing the Limits of Mathematical Reasoning in Open Language Models", Shao et al., 2024](https://arxiv.org/abs/2402.03300)
  Introduit GRPO, qui remplace la value function apprise de PPO par une baseline relative au groupe calculée à partir de plusieurs complétions échantillonnées par prompt. À utiliser pour : l'algorithme central de l'étape 6.
- [Article : "DeepSeek-R1: Incentivizing Reasoning Capability in LLMs via Reinforcement Learning", DeepSeek-AI, 2025](https://arxiv.org/abs/2501.12948)
  Entraîne un raisonnement étendu par chaîne de raisonnement principalement par RL contre des récompenses vérifiables, et décrit la distillation du comportement obtenu vers des modèles plus petits. À utiliser pour : la source primaire de l'étape 7.
- [Article : "Constitutional AI: Harmlessness from AI Feedback", Bai et al., 2022](https://arxiv.org/abs/2212.08073)
  Remplace les préférences d'innocuité étiquetées par des humains par un modèle qui critique et révise ses propres sorties au regard d'un ensemble écrit de principes. À utiliser pour : le cas central de l'étape 8 d'un feedback produit par un modèle plutôt que par un humain.
- [Article : "RLAIF: Scaling Reinforcement Learning from Human Feedback with AI Feedback", Lee et al., 2023](https://arxiv.org/abs/2309.00267)
  Une comparaison directe et contrôlée de RLAIF et de RLHF sur les mêmes tâches, qui rapporte où le feedback d'IA égale le feedback humain et où il ne l'égale pas. À utiliser pour : l'étape 8, comme complément empirique de la méthode de Constitutional AI.
- [Article : "Llama 2: Open Foundation and Fine-Tuned Chat Models", Touvron et al., 2023](https://arxiv.org/abs/2307.09288)
  Une recette RLHF publiée à l'échelle d'un modèle ouvert, avec les détails d'entraînement du reward model et un processus RLHF itératif sur plusieurs tours. À utiliser pour : recouper les étapes 3 et 4 avec une recette complète et reproductible.
- [Documentation : "TRL - Transformer Reinforcement Learning", Hugging Face](https://huggingface.co/docs/trl/index)
  La bibliothèque que font réellement tourner les labs SFT et DPO de ce parcours, avec une configuration détaillée pour chaque trainer. À utiliser pour : les exercices pratiques des étapes 2, 4 et 5.

## Lacunes

- Pas encore de source primaire sur la qualité des données de préférence : désaccord entre annotateurs, consignes d'étiquetage, et façon dont les choix de collecte de données de préférence biaisent un reward model entraîné. Nécessaire avant que le contenu sur la qualité des données de l'étape 3 puisse être pleinement fondé.
- La mesure de la taxe d'alignement au-delà du propre rapport d'InstructGPT est mince ; un traitement plus récent et agnostique au modèle renforcerait l'étape 9.
- Pas encore de compte rendu de production d'une comparaison complète des coûts DPO contre PPO contre GRPO issue de l'infrastructure d'une seule équipe ; la leçon de jugement de l'étape 10 doit pour l'instant la synthétiser à partir d'articles séparés plutôt que d'une source unique qui a déjà fait la comparaison.
