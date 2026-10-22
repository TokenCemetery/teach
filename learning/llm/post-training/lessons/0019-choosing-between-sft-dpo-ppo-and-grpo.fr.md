---
title: "19. Choisir entre SFT, DPO, PPO et GRPO"
description: "Chaque méthode ne mérite son coût supplémentaire par rapport à la précédente que lorsque la moins chère ne peut réellement pas exprimer le comportement visé"
type: lesson
---

# Leçon 19. Choisir entre SFT, DPO, PPO et GRPO

**Lien avec la mission :** « Étant donné les données, le budget et le comportement visé d'une équipe, choisir entre SFT seul, DPO, RLHF-PPO et GRPO, et défendre ce choix face à celui qui a été écarté » est la décision centrale de la mission, et cette leçon est celle où le décompte des coûts de tout l'arc est assemblé en un seul cadre.
**Source primaire :** [Article : "Direct Preference Optimization: Your Language Model is Secretly a Reward Model", Rafailov et al., 2023](https://arxiv.org/abs/2305.18290)
**Prérequis :** [Leçon 18](0018-reward-hacking-after-the-fact.md)

## Échauffement

1. ▢ Qu'est-ce que le sur-refus, et pourquoi un benchmark de type red-team, composé uniquement de prompts dangereux, ne peut-il pas le détecter ?

<details markdown="1"><summary>Vérifier</summary>

Un modèle qui refuse un prompt en réalité sans danger. Un benchmark de type red-team construit uniquement à partir de prompts dangereux ne contient aucun prompt sans danger qui puisse être refusé à tort, donc il ne peut pas faire apparaître cet échec précis.

</details>

2. ▢ Qu'est-ce que le biais du juge, et que recommande `llm/evals` de vérifier avant de se fier à un écart de score qu'il a produit ?

<details markdown="1"><summary>Vérifier</summary>

Une distorsion systématique dans la notation d'un juge LLM, comme favoriser les réponses plus longues ou celle qui est montrée en premier. `llm/evals` recommande de vérifier la calibration du juge face à ces biais connus avant de se fier à un écart de score comme preuve d'une vraie amélioration.

</details>

## À savoir

### Chaque méthode coûte plus que la précédente, pour une raison

Les quatre approches d'entraînement de ce parcours forment une échelle approximative, chacune n'ajoutant du coût que là où la précédente manque réellement de pouvoir d'expression pour le comportement visé :

**Le SFT seul (étape 2)** est le moins cher : pas de données de préférence, pas de reward model, pas de boucle de RL, juste l'imitation directe d'exemples démontrés. Il suffit exactement quand le comportement visé peut être entièrement spécifié en montrant des exemples de celui-ci : un format de réponse fixe, une compétence étroite et bien définie, un changement de style. Chaque méthode ultérieure de cette échelle part encore d'un modèle SFT ; la question que pose réellement cette leçon est de savoir jusqu'où, au-delà du SFT, un comportement donné doit aller.

**DPO (étape 5)** mérite son coût supplémentaire par rapport au SFT seul dès que le comportement souhaité ne peut pas être entièrement spécifié par démonstration directe, mais *peut* l'être en comparant deux sorties candidates, « celle-ci plutôt que celle-là ». Rafailov et al. construisent DPO précisément pour atteindre un modèle entraîné sur des préférences à un coût proche de celui du SFT : pas de reward model séparé, pas de value function, pas de boucle d'échantillonnage de RL, juste la policy et un modèle de référence figé (leçon 10). Si des données de préférence sont disponibles ou collectables et qu'il n'y a aucune raison précise d'avoir besoin d'un reward model autonome et réutilisable, DPO est le choix naturel après le SFT, pas RLHF-PPO.

**RLHF-PPO (étape 4)** mérite son coût nettement plus élevé (le montage à quatre ou cinq modèles de la leçon 8) précisément quand un reward model autonome vaut la peine d'exister pour lui-même : réutilisé pour noter des sorties hors de la policy qui s'est entraînée contre lui, inspecté indépendamment, ou itéré à plusieurs reprises à mesure que de nouvelles comparaisons arrivent sur la meilleure policy du moment, comme le décrit le pipeline d'origine en trois étapes de la leçon 1. Choisir PPO plutôt que DPO sans l'une de ces raisons, c'est payer une machinerie qu'une méthode plus simple couvre déjà.

**GRPO (étape 6)** gagne sa place par une tout autre porte : les récompenses vérifiables. Là où DPO et PPO ont tous deux besoin de jugements de préférence, humains ou d'IA, l'avantage relatif au groupe de GRPO fonctionne avec n'importe quel score par sortie, y compris la sortie d'un vérificateur déterministe (leçon 12), ce qui supprime tout besoin d'un reward model entraîné ou de données de préférence humaines sur des tâches comme les maths et le code où la justesse est vérifiable. GRPO n'est pas un PPO moins cher en général ; c'est le bon outil précisément quand la tâche fournit une récompense vérifiable que PPO ou DPO devraient sinon approcher par un jugement entraîné.

### Défendre une alternative écartée, pas seulement un choix

« Défendre ce choix face à celui qui a été écarté », la formulation même de la mission, signifie nommer quelle méthode moins chère a été essayée ou envisagée en premier et pourquoi elle n'a pas suffi, et pas simplement affirmer les avantages de la méthode choisie. Une équipe qui choisit PPO devrait pouvoir dire pourquoi la récompense implicite de DPO ne suffisait pas, précisément (le besoin d'un reward model réutilisable, le plus souvent). Une équipe qui choisit GRPO devrait pouvoir montrer la vérification vérifiable dont sa récompense est construite, et pas simplement citer les résultats de DeepSeek-R1 comme autorisation de l'utiliser sur une tâche sans aucune vérification de ce genre.

## Pratique

1. ▢ Une équipe veut un modèle qui répond toujours selon un schéma JSON fixe pour une tâche étroite et bien définie. Quelle méthode de cette échelle est le bon point de départ, et pourquoi ?

<details markdown="1"><summary>Vérifier</summary>

Le SFT seul. C'est exactement le cas qu'un comportement fixe et entièrement démontrable permet : des exemples du bon format suffisent à l'imiter directement, sans aucun besoin de données de préférence ni de signal de récompense.

</details>

2. ▢ Une équipe a des données de préférence (des paires de sorties dont l'une est marquée meilleure) et aucun besoin précis de réutiliser un reward model hors du run d'entraînement lui-même. Lequel de DPO et de PPO est le choix par défaut le plus défendable, et pourquoi ?

<details markdown="1"><summary>Vérifier</summary>

DPO. Il atteint un résultat similaire entraîné sur des préférences à un coût proche de celui du SFT, en ne demandant que la policy et un modèle de référence figé, sans reward model séparé ni boucle de RL à justifier tant que quelque chose de précis n'en exige pas un.

</details>

3. ▢ Une équipe entraîne un modèle à résoudre des problèmes de programmation compétitive, où un compilateur peut vérifier si le code généré passe une suite de tests fixe. Quelle méthode convient particulièrement bien à cette tâche, et qu'est-ce qui la rend adaptée ?

<details markdown="1"><summary>Vérifier</summary>

GRPO, associé à une récompense vérifiable : le résultat réussi ou échoué du compilateur sur la suite de tests est exactement le type de score déterministe et vérifiable que l'avantage relatif au groupe de GRPO peut utiliser directement, sans aucun besoin d'un reward model entraîné ni de données de préférence humaines.

</details>

4. ▢ Une équipe choisit RLHF-PPO plutôt que DPO en citant seulement « PPO est la méthode la plus établie ». D'après cette leçon, est-ce une défense suffisante du choix ?

<details markdown="1"><summary>Vérifier</summary>

Non. Défendre un choix face à celui qui a été écarté signifie nommer une raison précise pour laquelle l'approche moins chère de DPO n'aurait pas suffi, comme le besoin d'un reward model autonome à réutiliser ou sur lequel itérer. Citer seulement que PPO est établi n'identifie pas ce qui manquait précisément à DPO pour cette tâche.

</details>

## Exercices en situation réelle

- [ ] Trouvez un rapport technique de post-training publié et identifiez lequel de SFT, DPO, PPO ou GRPO il a utilisé, et s'il donne une raison de ce choix plutôt que d'une alternative moins chère.
- [ ] Pour une tâche que vous connaissez (issue du travail, d'un projet, ou hypothétique), faites-la passer par l'échelle de cette leçon un échelon à la fois : le SFT seul suffirait-il, et sinon pourquoi ; DPO suffirait-il, et sinon pourquoi.
- [ ] Demain : sans regarder la suite, écrivez une prédiction d'une phrase pour la leçon 20 : sachant que l'arc de ce parcours a couvert dix décisions distinctes (masquage des données, conception de la récompense, compromis KL, avantage relatif au groupe, récompenses vérifiables, mesure de la taxe d'alignement), que devrait réellement vérifier la relecture de la recette d'alignement terminée de quelqu'un d'autre, étape par étape ?

## Pour aller plus loin

- [Article : "Direct Preference Optimization: Your Language Model is Secretly a Reward Model", Rafailov et al., 2023](https://arxiv.org/abs/2305.18290)
- [Ressources](../RESOURCES.md)

---

Ça ne passe pas ? Relisez la source primaire en haut de page, car cette leçon la condense et c'est dans la condensation que la compréhension s'échappe. Consultez le [glossaire](../GLOSSARY.md) pour tout terme qui vous a paru glissant.

Si c'est la leçon elle-même qui n'est pas claire plutôt que la matière, c'est un défaut : [ouvrez une issue](https://github.com/TokenCemetery/teach/issues).
