---
title: "Glossaire"
description: "Termes de référence pour le post-training des LLM"
type: glossary
---

# Glossaire du post-training des LLM

Termes de référence pour aligner un modèle pré-entraîné : ce que maximise chaque objectif d'entraînement, et ce qui change quand l'objectif passe de l'imitation de texte à l'optimisation d'une récompense.

## Termes

**Taxe d'alignement** (alignment tax) :
La perte de capacité (généralement mesurée sur des benchmarks de type pré-entraînement) que le post-training peut introduire comme effet secondaire de l'optimisation pour l'utilité ou la sécurité.
_À éviter_ : régression (une régression est n'importe quelle baisse de capacité ; la taxe d'alignement désigne celle, précise, qu'on paie en échange de l'alignement)

**Loss de Bradley-Terry** (Bradley-Terry loss) :
La fonction de loss utilisée pour entraîner un reward model sur des données de préférence par paires, qui traite la probabilité qu'une complétion soit préférée à une autre comme une fonction de la différence entre leurs scores de récompense scalaires.
_À éviter_ : loss de préférence (employé librement pour plusieurs objectifs de ce domaine, dont celui de DPO ; Bradley-Terry désigne le modèle précis de comparaison par paires qu'utilise la modélisation de récompense)

**Avantage relatif au groupe** (group-relative advantage) :
Le remplacement par GRPO d'une value function apprise : pour un groupe de complétions échantillonnées pour le même prompt, l'avantage d'une complétion est sa récompense moins la récompense moyenne du groupe, divisée par l'écart-type du groupe, appliqué à chaque token de cette complétion.
_À éviter_ : baseline (une baseline est le concept général d'apprentissage par renforcement que remplit la moyenne du groupe ; cet espace de travail utilise le nom précis dès que GRPO est dans le périmètre)

**Récompense implicite** (implicit reward) :
La fonction de récompense que DPO montre être mathématiquement impliquée par une policy et un modèle de référence, sans jamais entraîner de reward model séparé pour la calculer.
_À éviter_ : reward model (tout l'argument de DPO est qu'il n'en faut pas de séparé ; confondre les deux efface la distinction que l'étape 5 existe pour enseigner)

**Pénalité KL** (KL penalty) :
Un terme ajouté à un objectif d'apprentissage par renforcement qui pénalise la policy entraînée lorsqu'elle s'écarte de la distribution de sortie d'un modèle de référence figé, pour que l'optimisation contre un reward model ne produise pas de texte dégénéré.
_À éviter_ : régularisation (exact mais générique ; nommez la pénalité précise dès que RLHF est dans le périmètre)

**Masquage de la loss** (loss masking) :
Mettre à zéro la loss d'entraînement sur les tokens que le modèle ne doit pas apprendre à produire, comme un prompt ou un message système, pour que les mises à jour de gradient ne viennent que des tokens que le modèle est censé générer.
_À éviter_ : masquage du prompt (le masquage s'applique à plus que le seul prompt, y compris à tout tour de parole hors assistant dans un exemple multi-tours)

**Paire de préférence** (preference pair) :
Deux complétions du même prompt, dont l'une est marquée comme préférée à l'autre, l'unité de données sur laquelle s'entraînent à la fois la modélisation de récompense et DPO.
_À éviter_ : comparaison (employé dans toute la littérature pour la même chose ; cet espace de travail standardise sur paire de préférence)

**Reward hacking** (détournement de la récompense) :
Une policy qui trouve le moyen d'obtenir un bon score face à un reward model ou à un signal de récompense vérifiable sans produire réellement le comportement que la récompense devait mesurer.
_À éviter_ : gaming, suroptimisation (les deux désignent le même échec ; cet espace de travail emploie reward hacking partout)

**RLAIF** :
Apprentissage par renforcement à partir de feedback d'IA (reinforcement learning from AI feedback) : des labels de préférence ou un signal de récompense produits par un modèle plutôt que par un humain, utilisés à la place de RLHF ou en complément.
_À éviter_ : auto-amélioration (RLAIF est une méthode d'étiquetage précise ; l'auto-amélioration est une affirmation plus large et plus floue sur ce qu'est le résultat)

**Récompense vérifiable** (verifiable reward) :
Un signal de récompense calculé par un vérificateur déterministe, comme le résultat d'un test unitaire ou une réponse numérique finale qui correspond, plutôt que par un reward model appris.
_À éviter_ : vérité terrain (la vérité terrain est la réponse contre laquelle on vérifie ; la récompense vérifiable est le signal dérivé de cette vérification)
