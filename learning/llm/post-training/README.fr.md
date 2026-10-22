---
title: "Post-training des LLM"
description: "Aligner un modèle de base : SFT, modélisation de récompense, RLHF, DPO et GRPO, et savoir lequel choisir"
type: topic
---

# Post-training des LLM

Savoir faire passer un modèle de base pré-entraîné à un assistant aligné qui suit les instructions : écrire correctement les objectifs SFT, de récompense et de préférence, choisir entre RLHF-PPO, DPO et GRPO selon le budget et les données d'une équipe, et défendre ce choix, y compris ce qu'il a coûté en taxe d'alignement et où il est exposé au reward hacking.

**Dernière leçon :** [0020. Relire la recette d'alignement de quelqu'un d'autre](lessons/0020-reviewing-someone-elses-alignment-recipe.md)

## Objectif

- Écrire une boucle d'entraînement SFT qui masque la loss sur les tokens hors assistant, et expliquer ce qui casse dans un modèle de chat entraîné sans ce masque.
- Entraîner un reward model sur des paires de préférence avec la loss de Bradley-Terry, et identifier une complétion victime de reward hacking issue d'une policy entraînée contre lui.
- Dériver l'objectif RLHF (la récompense moins une pénalité KL contre un modèle de référence) et dire ce qui arrive à la policy quand la pénalité KL est relâchée.
- Dériver la récompense implicite de DPO à partir des mêmes données de préférence que RLHF, et dire ce à quoi elle renonce en supprimant la boucle de RL.
- Expliquer l'avantage relatif au groupe dans GRPO et pourquoi une récompense vérifiable (un test unitaire, une réponse mathématique vérifiée) change ce que l'entraînement par RL peut viser.
- Étant donné les données, le budget et le comportement visé d'une équipe, choisir entre SFT seul, DPO, RLHF-PPO et GRPO, et défendre ce choix face à celui qui a été écarté.
- Lire les résultats d'évaluation d'un modèle aligné et distinguer un vrai gain de capacité d'un artefact de reward hacking ou de biais du juge.

## Contraintes

- L'algorithme d'abord, pas un panorama d'articles. Chaque étape enseigne un objectif d'entraînement en partant de sa fonction de loss, ce qui est maximisé et ce que fait le gradient, plutôt que de résumer une liste d'articles ; les articles servent d'ancrage à chaque étape comme source primaire.
- Pratique à petite échelle : les labs font tourner SFT et DPO sur un petit modèle ouvert, avec la même discipline d'échelle que `llm/finetuning`, et raisonnent à partir de là sur ce que rapportent les articles de pointe cités.
- Suppose `llm/transformers` (loss d'entropie croisée, passe arrière, AdamW) et la familiarité avec la mécanique des adapters de `llm/finetuning`, puisque ce parcours les réutilise au lieu de redériver l'efficacité en paramètres.
- Aucune leçon n'entraîne un pipeline RLHF complet de bout en bout à l'échelle de pointe ; le coût de PPO est démontré à petite échelle, puis raisonné à l'échelle que rapportent les articles cités.

## Hors périmètre

- La mécanique de l'efficacité en paramètres (rang et alpha de LoRA, QLoRA, DoRA, modules cibles) : voir [`llm/finetuning`](../../llm/finetuning/). Ce parcours possède l'objectif d'entraînement ; `llm/finetuning` possède la manière de l'appliquer à moins de paramètres.
- La loss d'entropie croisée, la passe arrière et AdamW : voir [`llm/transformers`](../../llm/transformers/). Supposés acquis ici, pas réenseignés.
- La mécanique du LLM-as-judge et la méthodologie d'évaluation humaine : voir [`llm/evals`](../../llm/evals/). Reprise ici uniquement comme la capacité dont un modèle aligné a besoin, juger si l'entraînement à l'alignement a aidé, et renvoyée plutôt que répétée.
- Prompter un modèle de raisonnement, ou construire un agent autour : voir [`llm/agents`](../../llm/agents/) (leçon 0017). Ce parcours couvre la façon dont le comportement de raisonnement est produit par l'entraînement RL, pas la façon de l'utiliser de l'extérieur.
- Entraîner un modèle depuis une initialisation aléatoire : voir [`llm/pretraining`](../../llm/pretraining/).
- La distillation en général, au-delà du cas du modèle de raisonnement : voir [`llm/distillation`](../../llm/distillation/). La leçon 0014 reste ici le cas du modèle de raisonnement et renvoie là-bas pour la méthode générale.
- Utiliser de l'extérieur, par le prompting, le suivi d'instructions et le raisonnement : voir [`llm/prompting`](../../llm/prompting/). Ce parcours couvre la façon dont ces comportements sont entraînés.

## Le fil conducteur

Dix étapes, de zéro connaissance préalable au jugement senior. Ce n'est pas une liste de leçons : une étape comprend plusieurs leçons, et les frontières sont souples.

| Étape | Leçons | Contenu | Terminée quand |
| --- | --- | --- | --- |
| 1. Ce que le post-training apporte | 0001 à 0001 | Modèle de base contre modèle instruct/chat, le paysage SFT/RLHF/DPO/GRPO | Vous savez situer le comportement d'un modèle aligné donné par rapport à l'étape de post-training qui l'a produit |
| 2. SFT | 0002 à 0003 | Jeux de données d'instruction, chat templates, masquage de la loss sur les tokens hors assistant | Vous savez écrire une boucle SFT avec un masquage de la loss correct et expliquer ce qui casse sans lui |
| 3. Modélisation de récompense | 0004 à 0005 | Collecte de données de préférence, loss de Bradley-Terry, reward hacking | Vous savez entraîner un reward model et identifier une complétion victime de reward hacking contre lui |
| 4. RLHF via PPO | 0006 à 0008 | L'objectif de RL, la pénalité KL contre un modèle de référence, pourquoi PPO est coûteux et instable | Vous savez dériver l'objectif RLHF et dire ce que fait à la policy le relâchement de la pénalité KL |
| 5. Direct Preference Optimization | 0009 à 0010 | La récompense implicite de DPO, ce qu'il abandonne par rapport à PPO et pourquoi c'est en général acceptable | Vous savez dériver la récompense implicite de DPO et dire à quoi il renonce par rapport à PPO |
| 6. GRPO et RL avec récompenses vérifiables | 0011 à 0012 | Avantage relatif au groupe, pourquoi il convient aux maths et au code | Vous savez expliquer l'avantage relatif au groupe et pourquoi une récompense vérifiable change ce que le RL peut viser |
| 7. Modèles de raisonnement | 0013 à 0014 | RL sur chaîne de raisonnement, ce qu'a changé DeepSeek-R1, distiller un modèle de raisonnement vers le bas | Vous savez dire comment le comportement d'un modèle de raisonnement a été produit, et pas seulement comment le prompter |
| 8. Sécurité et réglage du refus | 0015 à 0016 | Données de red-teaming, Constitutional AI, RLAIF | Vous savez dire d'où est venu le feedback (humain ou IA) dans un pipeline de réglage de sécurité donné et ce que cela implique comme compromis |
| 9. Évaluer un modèle aligné | 0017 à 0018 | Taxe d'alignement, détection du reward hacking, lien avec `llm/evals` | Vous savez distinguer un vrai gain de capacité d'un artefact de reward hacking ou de biais du juge |
| 10. Le jugement | 0019 à 0020 | DPO contre PPO contre GRPO pour un budget donné, quand le SFT seul suffit, relire la recette d'alignement de quelqu'un d'autre | On vous fait confiance pour trancher et l'expliquer à quelqu'un d'autre |

## Leçons

Suivez-les dans l'ordre.

| # | Leçon | Enseigne |
|---|---|---|
| [0001](lessons/0001-what-post-training-buys.md) | Ce que le post-training apporte | Un modèle aligné 100 fois plus petit a battu un modèle de base brut pour faire ce que les utilisateurs voulaient vraiment |
| [0002](lessons/0002-instruction-data-and-the-chat-template.md) | Données d'instruction et chat template | Un token spécial marque l'endroit où un prompt se termine et où une réponse commence, et cette frontière doit être la même à l'entraînement et au déploiement |
| [0003](lessons/0003-loss-masking-on-non-assistant-tokens.md) | Masquage de la loss sur les tokens hors assistant | Mettez à zéro la loss sur le prompt, sinon vous dépensez du signal de gradient à apprendre au modèle à prédire un texte qu'il n'a pas généré |
| [0004](lessons/0004-training-a-reward-model-the-bradley-terry-loss.md) | Entraîner un reward model : la loss de Bradley-Terry | Un reward model ne voit jamais de score absolu à l'entraînement, seulement laquelle de deux complétions un humain a préférée |
| [0005](lessons/0005-reward-hacking.md) | Reward hacking | Une policy a appris à répondre « Je ne peux pas répondre à cela » à presque tout, parce que cela scorait bien sans être réellement utile ni inoffensif |
| [0006](lessons/0006-the-rlhf-objective-reward-minus-a-kl-penalty.md) | L'objectif RLHF : la récompense moins une pénalité KL | Un terme poursuit le score du reward model ; un second terme est la laisse qui empêche la policy de s'enfuir avec lui |
| [0007](lessons/0007-ppo-why-the-update-gets-clipped.md) | PPO : pourquoi la mise à jour est clippée | Un gros gain sur un batch de données échantillonnées n'est pas une preuve fiable pour faire un gros pas ; PPO refuse d'y croire entièrement |
| [0008](lessons/0008-why-ppo-is-expensive-and-unstable.md) | Pourquoi PPO est coûteux et instable | Quatre modèles, et non un seul, doivent tenir en mémoire en même temps, et les deux qui passent le plus mal à l'échelle sont précisément ceux que RLHF ajoute |
| [0009](lessons/0009-dpos-implicit-reward-why-the-partition-function-cancels.md) | La récompense implicite de DPO : pourquoi la fonction de partition s'annule | Un terme de normalisation intraitable se dresse entre une récompense et sa policy optimale, jusqu'à ce qu'une différence de deux récompenses le fasse disparaître |
| [0010](lessons/0010-the-dpo-loss-and-what-it-drops-relative-to-ppo.md) | La loss de DPO, et ce qu'elle abandonne par rapport à PPO | Une loss, deux modèles, aucune boucle d'échantillonnage, et le même beta qu'aurait utilisé une pénalité KL |
| [0011](lessons/0011-grpo-group-relative-advantage-instead-of-a-value-function.md) | GRPO : l'avantage relatif au groupe au lieu d'une value function | Échantillonnez plusieurs réponses à la même question, et laissez la dispersion des récompenses du groupe dire lesquelles étaient meilleures |
| [0012](lessons/0012-verifiable-rewards-when-a-checker-replaces-the-reward-model.md) | Récompenses vérifiables : quand un vérificateur remplace le reward model | Un reward model entraîné est un pari sur ce qu'un humain préférerait ; un test unitaire ou une réponse qui correspond n'est pas un pari du tout |
| [0013](lessons/0013-chain-of-thought-rl-what-deepseek-r1-zero-did-with-rule-based-rewards.md) | RL sur chaîne de raisonnement : ce qu'a fait DeepSeek-R1-Zero avec des récompenses à base de règles | Aucun reward model appris, aucune étape SFT au préalable, et un raisonnement étendu a émergé quand même parce qu'il faisait trouver de plus en plus de bonnes réponses |
| [0014](lessons/0014-distilling-a-reasoning-model-down.md) | Distiller un modèle de raisonnement vers le bas | Entraîner un modèle de 32B directement par RL a perdu face au simple fine-tuning sur les propres traces de raisonnement d'un modèle plus gros |
| [0015](lessons/0015-constitutional-ai-feedback-from-a-model-not-a-human.md) | Constitutional AI : un feedback venu d'un modèle, pas d'un humain | Zéro label humain pour la nocivité, une liste écrite de principes à la place, et un assistant qui explique ses objections au lieu d'esquiver |
| [0016](lessons/0016-rlaif-how-well-ai-feedback-actually-matches-human-feedback.md) | RLAIF : dans quelle mesure le feedback d'IA correspond réellement au feedback humain | Un modèle qui juge ses propres sorties, à sa propre taille, a quand même battu le simple fine-tuning supervisé |
| [0017](lessons/0017-measuring-the-alignment-tax.md) | Mesurer la taxe d'alignement | La taxe n'apparaît pas partout en même temps, et un axe a même mesuré une amélioration à la place |
| [0018](lessons/0018-reward-hacking-after-the-fact.md) | Le reward hacking après coup | Un reward model mis de côté peut détecter la dérive pendant l'entraînement ; un modèle terminé demande un autre type de vérification |
| [0019](lessons/0019-choosing-between-sft-dpo-ppo-and-grpo.md) | Choisir entre SFT, DPO, PPO et GRPO | Chaque méthode ne mérite son coût supplémentaire par rapport à la précédente que lorsque la moins chère ne peut réellement pas exprimer le comportement visé |
| [0020](lessons/0020-reviewing-someone-elses-alignment-recipe.md) | Relire la recette d'alignement de quelqu'un d'autre | Parcourez le pipeline à travers chaque étape que ce parcours a couverte, dans l'ordre, et tranchez une affirmation contestée à partir de la source plutôt que d'une reformulation assurée |

## Référence

- [Glossaire](GLOSSARY.md) : termes de référence pour ce sujet
- [Ressources](RESOURCES.md) : sources fiables

## Comment cela fonctionne

Chaque leçon est courte et autonome. Les corrigés sont repliés : rappelez-vous d'abord, puis ouvrez-les. Les exercices en situation réelle comptent plus que la lecture, et les espacer dans le temps est justement le but. Tout ce qui reste flou à la fin d'une leçon mérite d'être suivi jusqu'à sa source primaire avant de passer à la suite.
