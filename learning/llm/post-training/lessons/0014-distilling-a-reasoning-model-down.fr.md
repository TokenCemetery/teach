---
title: "14. Distiller un modèle de raisonnement vers le bas"
description: "Entraîner un modèle de 32B directement par RL a perdu face au simple fine-tuning sur les propres traces de raisonnement d'un modèle plus gros"
type: lesson
---

# Leçon 14. Distiller un modèle de raisonnement vers le bas

**Lien avec la mission :** « Savoir dire comment le comportement d'un modèle de raisonnement a été produit, et pas seulement comment le prompter » est la puce d'« Objectif » que sert cette étape. La leçon 13 a couvert l'entraînement par pur RL de DeepSeek-R1-Zero et son problème de lisibilité ; cette leçon couvre le correctif de DeepSeek-R1, et le résultat surprenant de la distillation de ce correctif vers des modèles plus petits.
**Source primaire :** [Article : "DeepSeek-R1: Incentivizing Reasoning Capability in LLMs via Reinforcement Learning", DeepSeek-AI, 2025](https://arxiv.org/abs/2501.12948)
**Prérequis :** [Leçon 13](0013-chain-of-thought-rl-what-deepseek-r1-zero-did-with-rule-based-rewards.md)

## Échauffement

1. ▢ La longueur de raisonnement de DeepSeek-R1-Zero a fortement augmenté pendant l'entraînement sans aucun terme de récompense explicite pour cela. Qu'est-ce qui a réellement provoqué cette croissance ?

<details markdown="1"><summary>Vérifier</summary>

La récompense de précision récompensait la bonne réponse finale, et un raisonnement plus long et plus soigneux tendait à produire plus de réponses correctes ; l'entraînement par RL l'a donc sélectionné comme effet secondaire, et non parce que la longueur du raisonnement était directement récompensée.

</details>

2. ▢ DeepSeek-R1-Zero a atteint un fort raisonnement mais souffrait d'une mauvaise lisibilité et d'un mélange de langues. Pourquoi n'est-ce pas surprenant vu la façon dont sa récompense a été construite ?

<details markdown="1"><summary>Vérifier</summary>

La récompense ne vérifiait que la justesse de la réponse finale et la présence des balises de réflexion ; la lisibilité et le fait de rester dans une seule langue n'ont jamais fait partie du score, donc rien dans l'entraînement n'a sélectionné l'un ou l'autre.

</details>

## À savoir

### Corriger la lisibilité sans perdre le raisonnement

DeepSeek-R1 est la réponse de DeepSeek-AI au problème de lisibilité de DeepSeek-R1-Zero : au lieu d'un pur RL à partir du modèle de base, il ajoute des **cold-start data** (données de démarrage à froid), une quantité modeste de données sélectionnées utilisées avant l'étape de RL axée sur le raisonnement, ainsi que plusieurs étapes d'entraînement construites autour de cette étape de RL plutôt qu'un seul passage. Cela donne au modèle un point de départ déjà plus proche de produire une sortie lisible et dans une seule langue, avant que le même type de RL axé sur le raisonnement et à base de règles, qui a produit les capacités de DeepSeek-R1-Zero, soit appliqué par-dessus. Le résultat, rapporte DeepSeek-AI, atteint une performance comparable à o1 d'OpenAI sur les tâches de raisonnement tout en évitant les problèmes de lisibilité et de mélange de langues de la version en pur RL.

### Distillation : fine-tuner des modèles plus petits sur les propres traces de raisonnement du modèle plus gros

Indépendamment de l'entraînement de DeepSeek-R1 lui-même, DeepSeek-AI produit six modèles denses plus petits, de 1.5B à 70B de paramètres, construits sur des modèles de base Qwen et Llama existants. La méthode est directe : fine-tuner chaque modèle de base plus petit sur 800 000 échantillons sélectionnés, générés avec le propre pipeline d'entraînement de DeepSeek-R1. C'est du **fine-tuning supervisé ordinaire** (étape 2) sur des données qui se trouvent être constituées des propres sorties d'un modèle de raisonnement plus grand, pas un nouvel algorithme. DeepSeek-AI sont explicites : ils n'appliquent que du SFT à ces modèles distillés, sans aucune étape de RL, même s'ils notent qu'une étape de RL pourrait vraisemblablement les améliorer encore ; leur but, dans ce cas, était de démontrer que la distillation seule fonctionne déjà bien, en laissant une étape de RL supplémentaire pour les modèles plus petits à de futurs travaux.

### Le résultat qui mérite qu'on le prenne au sérieux

DeepSeek-AI a mené une comparaison directe qui répond à une question naturelle : un modèle plus petit pourrait-il atteindre la même capacité de raisonnement en lui appliquant directement le même RL à grande échelle, au lieu de distiller à partir d'un modèle plus grand qui a déjà passé par ce RL ? Ils ont entraîné un modèle de base de 32B avec plus de 10 000 pas du même RL à grande échelle que celui de DeepSeek-R1-Zero, ce qui a produit « DeepSeek-R1-Zero-Qwen-32B », et l'ont comparé à « DeepSeek-R1-Distill-Qwen-32B », le même modèle de base de 32B fine-tuné à la place sur les traces de raisonnement distillées de DeepSeek-R1. Sur le benchmark de maths AIME 2024, le modèle entraîné directement par RL a atteint 47.0 % de pass@1 ; le modèle distillé a atteint 72.6 %, un grand écart qui allait dans le même sens sur tous les benchmarks qu'ils rapportent. La conclusion de DeepSeek-AI elle-même : distiller un modèle plus capable vers le bas est à la fois économique et très efficace, alors qu'entraîner un modèle plus petit directement par RL à grande échelle exige un calcul énorme et peut ne toujours pas égaler ce que la distillation obtient gratuitement à partir d'un modèle qui a déjà fait ce travail.

### La limite de la distillation

DeepSeek-AI prend soin de ne pas en dire trop : la distillation transfère à peu de frais ce qu'un modèle plus fort sait déjà faire, mais elle ne pousse pas à elle seule la capacité au-delà de ce que ce modèle plus fort peut déjà faire. Leur propre seconde conclusion l'énonce directement : dépasser la frontière actuelle exige toujours des modèles de base plus capables et du RL à plus grande échelle appliqué à ceux-ci, et non simplement plus de distillation de ce qui existe déjà. La distillation est un moyen bon marché de diffuser une capacité existante vers des modèles plus petits, pas un moyen de fabriquer une nouvelle capacité au-delà de ce que possède déjà le modèle dont on distille.

## Pratique

1. ▢ Une équipe veut un petit modèle de raisonnement capable et envisage deux voies : distiller à partir d'un grand modèle de raisonnement existant par SFT, ou lancer du RL à grande échelle directement sur le petit modèle depuis son checkpoint de base. D'après la comparaison de 32B de DeepSeek-AI elle-même, quelle voie s'attendrait-elle à voir atteindre la meilleure performance de raisonnement, et de combien environ sur AIME 2024 ?

<details markdown="1"><summary>Vérifier</summary>

La distillation. DeepSeek-R1-Distill-Qwen-32B a atteint 72.6 % de pass@1 sur AIME 2024, contre 47.0 % pour DeepSeek-R1-Zero-Qwen-32B, entraîné avec plus de 10 000 pas de RL à grande échelle directement sur le même modèle de base.

</details>

2. ▢ Qu'est-ce que, précisément, la « distillation » au sens de cette leçon, mécaniquement ?

    - a) Un nouvel algorithme de RL appliqué au modèle plus petit
    - b) Un fine-tuning supervisé ordinaire d'un modèle de base plus petit sur des échantillons de sortie sélectionnés, générés par un modèle de raisonnement plus grand déjà entraîné par RL
    - c) La compression directe des poids du modèle plus grand dans une architecture plus petite
    - d) L'exécution conjointe des modèles plus grand et plus petit à l'inférence

<details markdown="1"><summary>Vérifier</summary>

**b)** est exactement la méthode que décrit DeepSeek-AI : du SFT sur 800k échantillons sélectionnés issus du propre pipeline de DeepSeek-R1, sans étape de RL. (a), (c) et (d) décrivent chacune une autre technique que n'est pas celle de cette leçon.

</details>

3. ▢ D'après les deux conclusions de DeepSeek-AI elles-mêmes, la distillation seule pourrait-elle pousser la capacité de raisonnement d'un petit modèle au-delà de ce que DeepSeek-R1 lui-même, le modèle dont on distille, peut déjà faire ?

<details markdown="1"><summary>Vérifier</summary>

Non. Leur seconde conclusion énonce directement que dépasser la frontière actuelle exige toujours des modèles de base plus capables et du RL à plus grande échelle, et non plus de distillation ; la distillation diffuse à peu de frais une capacité existante, elle ne fabrique pas de nouvelle capacité au-delà de celle du modèle source.

</details>

4. ▢ Pourquoi DeepSeek-R1 a-t-il ajouté des cold-start data et un entraînement en plusieurs étapes plutôt que de simplement réutiliser à plus grande échelle la recette exacte de DeepSeek-R1-Zero ?

<details markdown="1"><summary>Vérifier</summary>

Parce que le raisonnement de DeepSeek-R1-Zero s'accompagnait d'une mauvaise lisibilité et d'un mélange de langues que le pur RL à base de règles ne donnait au modèle aucune incitation à corriger ; les cold-start data et l'entraînement en plusieurs étapes traitent directement ce problème de lisibilité, au lieu de chercher à passer à l'échelle une recette qui ne l'avait jamais sélectionné au départ.

</details>

## Exercices en situation réelle

- [ ] Trouvez le tableau 6 du rapport technique de DeepSeek-R1 (article lié plus haut) et notez l'écart entre DeepSeek-R1-Zero-Qwen-32B et DeepSeek-R1-Distill-Qwen-32B sur au moins un benchmark autre qu'AIME 2024.
- [ ] Trouvez un modèle de raisonnement distillé publié (beaucoup sont publiés avec un nom indiquant le modèle dont ils sont distillés) et vérifiez si sa model card indique qu'il a été entraîné avec du SFT seul, une étape de RL ajoutée, ou les deux.
- [ ] Demain : pour un projet hypothétique qui a besoin d'un petit modèle de raisonnement capable, décidez si vous choisiriez la distillation à partir d'un modèle de raisonnement plus grand ou le RL direct sur le petit modèle lui-même, et écrivez une phrase citant les preuves de cette leçon pour votre choix.

## Pour aller plus loin

- [Article : "DeepSeek-R1: Incentivizing Reasoning Capability in LLMs via Reinforcement Learning", DeepSeek-AI, 2025](https://arxiv.org/abs/2501.12948)
- [Distillation : Séquences et données synthétiques](../../distillation/reference/sequence-and-synthetic-data.md) : la distillation en général, dont cette leçon est le cas du modèle de raisonnement
- [Ressources](../RESOURCES.md)

---

L'étape 7 a couvert la façon dont le comportement de raisonnement est produit par le RL, et à quel faible coût on peut le diffuser vers des modèles plus petits une fois qu'il existe. L'étape 8 se tourne vers une autre cible pour la même famille de techniques : non pas la capacité de raisonnement, mais le comportement de sécurité et de refus.

Ça ne passe pas ? Relisez la source primaire en haut de page, car cette leçon la condense et c'est dans la condensation que la compréhension s'échappe. Consultez le [glossaire](../GLOSSARY.md) pour tout terme qui vous a paru glissant.

Si c'est la leçon elle-même qui n'est pas claire plutôt que la matière, c'est un défaut : [ouvrez une issue](https://github.com/TokenCemetery/teach/issues).
