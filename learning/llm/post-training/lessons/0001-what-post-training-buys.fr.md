---
title: "1. Ce que le post-training apporte"
description: "Un modèle aligné 100 fois plus petit a battu un modèle de base brut pour faire ce que les utilisateurs voulaient vraiment"
type: lesson
---

# Leçon 1. Ce que le post-training apporte

**Lien avec la mission :** « Étant donné les données, le budget et le comportement visé d'une équipe, choisir entre SFT seul, DPO, RLHF-PPO et GRPO, et défendre ce choix » est la décision centrale de la mission, et elle commence par savoir quel problème le post-training résout que le pré-entraînement seul ne résout pas.
**Source primaire :** [Article : "Training language models to follow instructions with human feedback", Ouyang et al., 2022](https://arxiv.org/abs/2203.02155)
**Prérequis :** aucun

## À savoir

### Un modèle de base n'est pas automatiquement un bon assistant

Un modèle de base pré-entraîné, produit de tout le parcours de `llm/pretraining`, est entraîné à prédire les tokens suivants les plus probables, selon la distribution de texte qu'il a vue. Ce n'est pas la même compétence que suivre les instructions réelles d'un utilisateur, et agrandir un modèle de base ne comble pas cet écart à lui seul. Ouyang et al. le disent sans détour : « agrandir les modèles de langage ne les rend pas intrinsèquement meilleurs pour suivre l'intention d'un utilisateur ». Un grand modèle de base peut produire des sorties fausses, inutiles ou simplement différentes de ce qui était demandé, non pas faute de capacité, mais parce que rien dans le pré-entraînement ne lui a spécifiquement appris à employer cette capacité comme l'utilisateur le souhaite.

### Le résultat phare

Le résultat central d'Ouyang et al. donne la mesure de cet écart : dans les évaluations humaines, les sorties de leur modèle **InstructGPT** de 1.3 milliard de paramètres ont été préférées à celles du modèle GPT-3 de 175 milliards de paramètres dont il était parti, alors qu'il compte environ 100 fois moins de paramètres. Le post-training n'a pas rendu le modèle plus grand ni plus intelligent au sens brut ; il a changé la direction dans laquelle sa capacité existante était orientée, et cette orientation a compté davantage pour les évaluateurs humains que deux ordres de grandeur d'échelle en plus.

### Le pipeline en trois étapes

La recette d'Ouyang et al., qui reste la forme de référence à laquelle on compare la plupart des travaux RLHF ultérieurs, comporte trois étapes :

1. **Collecter des démonstrations, entraîner une policy supervisée.** Des annotateurs humains écrivent des exemples du comportement voulu pour toute une gamme de prompts ; le modèle de base est fine-tuné dessus par un apprentissage supervisé ordinaire. Cette étape est le **SFT** (supervised fine-tuning), sujet de l'étape 2.
2. **Collecter des comparaisons, entraîner un reward model.** Des annotateurs classent plusieurs sorties du modèle SFT pour un même prompt ; un modèle distinct, le **reward model**, est entraîné à prédire quelle sortie un humain préférerait. C'est le sujet de l'étape 3.
3. **Optimiser la policy contre le reward model avec PPO.** Le modèle SFT est de nouveau fine-tuné par apprentissage par renforcement, en traitant le score du reward model comme le signal de récompense à maximiser. C'est le sujet de l'étape 4, et les étapes 2 et 3 peuvent être répétées : on collecte plus de comparaisons sur la meilleure policy du moment pour entraîner un nouveau reward model, puis une nouvelle policy.

### La taxe d'alignement, première rencontre

Le post-training n'est pas gratuit, même quand il fonctionne. Ouyang et al. ont constaté que leurs modèles alignés se comportaient un peu moins bien que le modèle de base d'origine sur certains benchmarks NLP publics (un benchmark de compréhension de lecture, un benchmark de raisonnement discret, un benchmark de bon sens et un benchmark de traduction, entre autres). Ils nomment cela une **taxe d'alignement** : un coût réel et mesuré sur certaines capacités, payé en échange d'un comportement que les humains préféraient dans l'ensemble. Ils ont aussi trouvé un remède partiel : mélanger les mises à jour PPO avec des mises à jour qui augmentent la vraisemblance des données de pré-entraînement d'origine (qu'ils appellent **PPO-ptx**) a récupéré une grande part de la performance perdue sans renoncer aux gains de préférence que le post-training devait produire. La taxe n'est ni fixe ni inévitable ; c'est un compromis mesuré que des techniques ultérieures peuvent en partie réduire.

### Le paysage à venir

Le SFT seul (étape 2) est l'étape la moins chère et change déjà beaucoup de comportements. La modélisation de récompense et RLHF via PPO (étapes 3 et 4) ajoutent par-dessus une seconde phase d'apprentissage par renforcement, avec un coût et une complexité réellement supérieurs. La Direct Preference Optimization (étape 5) vise plus tard un résultat similaire sans reward model séparé ni boucle d'apprentissage par renforcement. GRPO (étape 6) adapte l'approche d'apprentissage par renforcement aux tâches dont la réponse est vérifiable, comme les maths ou le code, plutôt qu'à un jugement de préférence humain. Le réglage propre à la sécurité (étape 8) applique la même famille de techniques à une cible différente. Chacune est une réponse différente à la question de fond que cette leçon a ouverte : comment orienter la capacité existante d'un modèle vers ce qu'une personne veut réellement, et à quel coût.

## Pratique

1. ▢ Le modèle InstructGPT de 1.3 milliard de paramètres a été préféré au modèle GPT-3 de 175 milliards de paramètres dans les évaluations humaines. Que dit ce résultat de la relation entre le nombre brut de paramètres et la capacité à suivre l'intention d'un utilisateur ?

<details markdown="1"><summary>Vérifier</summary>

Que ce ne sont pas la même chose. Un modèle bien plus petit, orienté vers la tâche par le post-training, a battu un modèle bien plus grand qui ne l'avait pas été. L'échelle seule n'a pas produit le comportement que les humains préféraient ; c'est la façon dont la capacité du modèle était orientée qui l'a fait.

</details>

2. ▢ Remettez dans l'ordre ces trois étapes du pipeline d'Ouyang et al. : (a) entraîner un reward model sur des comparaisons humaines de sorties du modèle, (b) fine-tuner la policy contre le reward model avec PPO, (c) fine-tuner un modèle de base sur des démonstrations écrites par des humains.

<details markdown="1"><summary>Vérifier</summary>

c, a, b : on collecte d'abord des démonstrations et on entraîne une policy supervisée (SFT), puis on collecte des comparaisons et on entraîne un reward model, puis on optimise la policy contre ce reward model avec PPO.

</details>

3. ▢ Qu'est-ce qu'une taxe d'alignement, d'après la propre constatation d'Ouyang et al., et qu'ont-ils trouvé qui pouvait la compenser en partie ?

<details markdown="1"><summary>Vérifier</summary>

Une baisse mesurée de performance sur certains benchmarks NLP publics, qui accompagnait les gains d'alignement du post-training, même si les évaluateurs humains préféraient le modèle aligné dans l'ensemble. Mélanger les mises à jour PPO avec des mises à jour qui augmentent la vraisemblance des données de pré-entraînement d'origine (PPO-ptx) a récupéré une grande part de cette performance perdue sans renoncer aux gains de préférence.

</details>

4. ▢ Laquelle de ces descriptions rend le mieux ce que font respectivement le SFT, la modélisation de récompense et RLHF-PPO dans le pipeline d'Ouyang et al. ?

    - a) Le SFT imite directement des démonstrations écrites par des humains ; la modélisation de récompense apprend à prédire la préférence humaine entre des sorties ; RLHF-PPO optimise la policy contre ce signal de préférence appris
    - b) Les trois étapes entraînent le reward model, à une échelle croissante
    - c) Le SFT et RLHF-PPO sont la même étape, exécutée deux fois pour la stabilité
    - d) La modélisation de récompense remplace entièrement le modèle de base avant le début de PPO

<details markdown="1"><summary>Vérifier</summary>

**a)** est la véritable répartition du travail entre les trois étapes. (b), (c) et (d) confondent chacune des étapes qui font des choses réellement différentes : imiter des démonstrations, apprendre un signal de préférence et optimiser contre ce signal sont trois étapes distinctes, pas une seule répétée.

</details>

## Exercices en situation réelle

- [ ] Trouvez une model card ou un rapport technique pour un modèle « instruct » ou « chat » ouvert, et notez laquelle des trois étapes d'Ouyang et al. il dit explicitement avoir utilisée (SFT, un reward model et/ou du RL), et laquelle, le cas échéant, il remplace par une autre méthode.
- [ ] Lisez le résumé de l'article InstructGPT (lié plus haut) et écrivez, en une phrase, quels torts précis (au-delà du simple « inutile ») Ouyang et al. citent comme motivant le besoin d'alignement.
- [ ] Demain : sans regarder la suite, écrivez une prédiction d'une phrase pour l'étape 2 : sachant que le SFT est décrit comme l'imitation directe de démonstrations écrites par des humains, quelle sorte d'erreur attendriez-vous d'une implémentation naïve du SFT qui s'entraînerait sur chaque token d'un exemple d'entraînement, y compris le prompt lui-même ?

## Pour aller plus loin

- [Article : "Training language models to follow instructions with human feedback", Ouyang et al., 2022](https://arxiv.org/abs/2203.02155)
- [Ressources](../RESOURCES.md)

---

Ça ne passe pas ? Relisez la source primaire en haut de page, car cette leçon la condense et c'est dans la condensation que la compréhension s'échappe. Consultez le [glossaire](../GLOSSARY.md) pour tout terme qui vous a paru glissant.

Si c'est la leçon elle-même qui n'est pas claire plutôt que la matière, c'est un défaut : [ouvrez une issue](https://github.com/TokenCemetery/teach/issues).
