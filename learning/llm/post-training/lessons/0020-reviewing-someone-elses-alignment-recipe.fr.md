---
title: "20. Relire la recette d'alignement de quelqu'un d'autre"
description: "Parcourez le pipeline à travers chaque étape que ce parcours a couverte, dans l'ordre, et tranchez une affirmation contestée à partir de la source plutôt que d'une reformulation assurée"
type: lesson
---

# Leçon 20. Relire la recette d'alignement de quelqu'un d'autre

**Lien avec la mission :** Cela clôt l'arc. Chaque étape précédente a produit une chose à vérifier dans le pipeline de post-training de quelqu'un d'autre ; cette leçon en est la liste de contrôle, avec la discipline qui consiste à trancher une confusion précise, réellement courante, à partir de la source primaire plutôt que d'une reformulation secondaire assurée.
**Source primaire :** [Article : "DeepSeekMath: Pushing the Limits of Mathematical Reasoning in Open Language Models", Shao et al., 2024](https://arxiv.org/abs/2402.03300)
**Prérequis :** toutes les leçons précédentes de ce parcours, puisque celle-ci est la synthèse.

## Échauffement

1. ▢ Une équipe a des données de préférence et aucun besoin précis de réutiliser un reward model hors de l'entraînement. Lequel de DPO et de PPO est le choix par défaut le plus défendable, et pourquoi ?

<details markdown="1"><summary>Vérifier</summary>

DPO. Il atteint un résultat similaire entraîné sur des préférences à un coût proche de celui du SFT, en ne demandant que la policy et un modèle de référence figé, sans reward model séparé ni boucle de RL à justifier tant que quelque chose de précis n'en exige pas un.

</details>

2. ▢ Qu'exige « défendre ce choix face à celui qui a été écarté », au-delà d'énoncer les avantages de la méthode choisie ?

<details markdown="1"><summary>Vérifier</summary>

Nommer quelle méthode moins chère a été envisagée en premier et pourquoi elle n'a précisément pas suffi pour la tâche, et pas simplement affirmer pourquoi la méthode choisie est bonne.

</details>

## À savoir

### La liste de contrôle de relecture : les étapes dans l'ordre

Quand on relit un pipeline de post-training proposé ou existant, on le parcourt à travers les étapes de ce parcours dans l'ordre, en posant la même question à chacune : ce choix est-il énoncé et justifié, ou simplement supposé ?

**Étape 1, le paysage.** Le pipeline dit-il vers laquelle du paysage SFT/RLHF/DPO/GRPO il construit, et cela correspond-il au comportement visé décrit, ou « nous avons post-entraîné le modèle » reste-t-il vague sur laquelle de ces approches a réellement été utilisée ?

**Étape 2, SFT.** Le masquage de la loss sur les tokens hors assistant est-il réellement appliqué (leçon 3), et le chat template utilisé à l'entraînement est-il documenté assez clairement pour que le déploiement puisse le reproduire exactement (leçon 2) ? Un pipeline vague sur l'un ou l'autre est exposé à un mode d'échec réel et déjà documenté, pas hypothétique.

**Étape 3, modélisation de récompense.** Si un reward model est entraîné, les données de préférence sont-elles collectées sous forme de classements décomposés en paires, selon la méthode de la leçon 4, ou de comparaisons isolées qui risquent le surapprentissage qu'ont constaté Ouyang et al. ? Le reward hacking (leçon 5) est-il vérifié, idéalement avec quelque chose comme un modèle de préférence mis de côté, plutôt que supposé inexistant ?

**Étape 4, RLHF-PPO, si utilisé.** Le coefficient de pénalité KL est-il indiqué et son compromis (leçon 6) reconnu ? Le pipeline nomme-t-il les modèles qu'il exécute simultanément et leurs tailles (leçon 8), vu à quel point l'échelle du reward model et de la value function a directement affecté la stabilité d'Ouyang et al. ?

**Étape 5, DPO, si utilisé.** Le modèle de référence est-il clairement identifié, et le rôle de beta (le même compromis de force KL que celui de PPO, d'après la leçon 10) est-il énoncé plutôt que laissé comme hyperparamètre inexpliqué ?

**Étape 6, GRPO, si utilisé.** La récompense par sortie est-elle le score d'un modèle entraîné ou une vérification vérifiable ? Cette distinction compte assez pour mériter sa propre vérification, traitée directement plus bas.

**Étape 7, entraînement au raisonnement, si utilisé.** Le comportement de raisonnement étendu est-il attribué à ce qui l'a réellement produit (du RL contre une récompense, vérifiable ou non), plutôt que décrit comme quelque chose de programmé explicitement ?

**Étape 8, réglage de sécurité, si utilisé.** Le pipeline dit-il si le feedback d'innocuité est venu d'humains ou d'un modèle (leçon 15), et si la performance est comparée à une baseline à feedback humain, cette comparaison est-elle réellement rapportée, selon le précédent de Bai et al., plutôt que supposée favorable ?

**Étape 9, évaluation.** La taxe d'alignement est-elle mesurée par benchmark plutôt que comme un nombre unique ramené à un seul chiffre (leçon 17), et une vérification de sur-refus ou de biais du juge est-elle présente à côté de tout score de sécurité ou de préférence mis en avant (leçon 18) ?

Un pipeline qui répond à tout cela par un choix énoncé et défendable est un pipeline qui a fait le travail que décrit ce parcours. Un pipeline qui répond à plusieurs de ces questions par le silence ne l'a pas fait, quelle que soit l'allure de ses chiffres de benchmark finaux.

### Trancher une affirmation contestée à partir de la source, pas d'un billet de blog

Une confusion précise et facile à faire mérite d'être parcourue directement, parce que les propres notes de l'étape 6 de ce parcours ont dû l'attraper pendant leur rédaction. On affirme parfois, de façon désinvolte, que « GRPO s'entraîne sur des récompenses vérifiables », comme si les deux étaient inséparables. La vérification de l'article de Shao et al. lui-même, celui qui introduit GRPO, réfute directement cela tel quel : le GRPO de DeepSeekMath s'entraîne contre une récompense produite par `r_φ`, un reward model explicitement entraîné, initialisé et entraîné comme le décrit la leçon 4, sans aucun vérificateur à base de règles ni de vérité terrain nulle part dans sa méthode. L'association de GRPO avec des récompenses vérifiables à base de règles est réelle et bien documentée, mais elle appartient à DeepSeek-R1 (leçon 13), un autre article, qui applique le mécanisme relatif au groupe de GRPO à un autre type de récompense que celui avec lequel GRPO a été introduit. Une source secondaire qui énonce « GRPO utilise des récompenses vérifiables » comme un fait général sur l'algorithme fusionne discrètement les contributions de deux articles distincts en une seule ; revenir à la section de méthode de DeepSeekMath lui-même, plutôt que de se fier à l'affirmation fusionnée et assurée, est ce qui l'attrape. Le mécanisme (l'avantage relatif au groupe) et la source de la récompense (vérification vérifiable ou modèle entraîné) sont deux choix indépendants, pas un paquet inséparable, et un pipeline qui distingue correctement les deux est un pipeline dont l'auteur a réellement lu les sources plutôt que de répéter ce que « tout le monde sait » sur GRPO.

## Pratique

1. ▢ Un pipeline proposé indique « nous utilisons GRPO avec des récompenses vérifiables pour notre tâche de benchmark de maths » et cite l'article DeepSeekMath comme unique source. Cette citation est-elle fidèle à ce que décrit réellement la méthode de DeepSeekMath ?

<details markdown="1"><summary>Vérifier</summary>

Pas entièrement. Le GRPO de DeepSeekMath s'entraîne contre une récompense issue d'un reward model entraîné, pas d'une vérification vérifiable à base de règles. L'association d'une récompense vérifiable avec GRPO est la contribution de DeepSeek-R1, un autre article. La méthode réelle du pipeline (GRPO avec une récompense vérifiable) peut très bien être raisonnable, mais citer DeepSeekMath seul comme source attribue à tort l'origine de cette combinaison précise.

</details>

2. ▢ Un document de pipeline dit seulement « nous avons appliqué RLHF » sans autre détail. À l'aide de la liste de contrôle de cette leçon, nommez deux choses précises que cette phrase laisse non dites et sur lesquelles un relecteur devrait poser des questions.

<details markdown="1"><summary>Vérifier</summary>

N'importe quelles deux parmi : le coefficient de pénalité KL et si son compromis a été considéré ; les tailles des modèles impliqués (policy, référence, reward model, value function) et si l'échelle du reward model a été choisie délibérément ; la façon dont les données de préférence ont été collectées et si le reward hacking a été vérifié ; si la taxe d'alignement résultante a été mesurée, et sur quels benchmarks.

</details>

3. ▢ Un pipeline rapporte un score de sécurité élevé issu d'une évaluation LLM-as-judge, sans autre détail. D'après la leçon 18 et la vérification de l'étape 9 de cette leçon, que devrait demander un relecteur avant de se fier à ce score ?

<details markdown="1"><summary>Vérifier</summary>

Si le juge a été vérifié en calibration face aux biais connus (de position, de verbosité), et si une vérification de sur-refus existe à côté du score de sécurité, pour qu'un score élevé reflète une vraie sécurité plutôt qu'un refus généralisé ou un juge exploitable.

</details>

## Exercices en situation réelle

- [ ] Trouvez un vrai rapport technique de post-training publié et faites-le passer par la liste de contrôle de cette leçon, étape par étape, en notant quels points sont énoncés explicitement et lesquels sont passés sous silence.
- [ ] Trouvez une affirmation sur les méthodes de post-training (DPO, PPO, GRPO ou RLAIF) énoncée avec assurance dans un billet de blog, un tutoriel ou une réponse de forum, et vérifiez-la dans l'article primaire dont elle devrait découler. Notez si elle tient, si c'est une simplification, ou une vraie confusion comme l'exemple GRPO de cette leçon.
- [ ] Demain : écrivez une courte relecture, de trois à cinq phrases, d'un pipeline de post-training réel ou hypothétique, en nommant au moins un choix précis que vous contesteriez et ce que vous demanderiez à la personne qui le défend de justifier.

## Pour aller plus loin

- [Article : "DeepSeekMath: Pushing the Limits of Mathematical Reasoning in Open Language Models", Shao et al., 2024](https://arxiv.org/abs/2402.03300)
- [Ressources](../RESOURCES.md)

---

Ça ne passe pas ? Relisez la source primaire en haut de page, car cette leçon la condense et c'est dans la condensation que la compréhension s'échappe. Consultez le [glossaire](../GLOSSARY.md) pour tout terme qui vous a paru glissant.

Si c'est la leçon elle-même qui n'est pas claire plutôt que la matière, c'est un défaut : [ouvrez une issue](https://github.com/TokenCemetery/teach/issues).
