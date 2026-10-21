---
title: "25. Servir des adapters"
description: "Fusionner pour une tâche, router pour plusieurs"
type: lesson
---

# Leçon 25. Servir des adapters

**Lien avec la mission :** « Le livrer » fait partie de la mission. Un adapter dans un répertoire n'est pas livré.
**Source primaire :** [Doc : LoRA adapters, vLLM](https://docs.vllm.ai/en/latest/features/lora.html)
**Prérequis :** [Leçon 13](0013-merging-and-shipping.md), [Leçon 24](0024-the-regression-suite.md)

## Échauffement

1. ▢ Quel choix de service rend l'oubli catastrophique sans importance ?

<details markdown="1"><summary>Vérifier</summary>

Garder l'adapter non fusionné et ne lui router que les requêtes pertinentes, en laissant le base model intact disponible pour tout le reste.

</details>

2. ▢ Où faut-il fusionner un adapter entraîné face à un base model quantifié ?

<details markdown="1"><summary>Vérifier</summary>

Dans le base model en pleine précision, puis quantifier ensuite si un artefact quantifié est nécessaire.

</details>

3. ▢ Pourquoi le décodage glouton pour vérifier une fusion ?

<details markdown="1"><summary>Vérifier</summary>

Pour que toute différence de sortie soit attribuable aux poids plutôt qu'à l'échantillonnage.

</details>

## À savoir

### Trois formes de déploiement

**Modèle fusionné.** Un seul artefact, indiscernable de n'importe quel autre modèle. N'importe quelle pile de service le charge. Aucune mécanique d'adapter.

**Non fusionné, adapter unique.** Base model plus adapter appliqué au chargement. Ajoute deux petites multiplications de matrices par couche adaptée.

**Non fusionné, plusieurs adapters.** Un base model en mémoire, plusieurs adapters, choisis par requête. C'est la forme qui rend les adapters économiquement intéressants et elle demande un support explicite à l'exécution.

### Choisir

| | Fusionné | Non fusionné, multi-adapters |
|---|---|---|
| Mémoire pour N tâches | N modèles complets | Un base model + N petits adapters |
| Surcoût par requête | Aucun | Faible, et plus grand avec un batching mixte |
| Pile de service | N'importe laquelle | Doit prendre en charge les adapters |
| Changer de tâche | Charger un autre modèle | Changer un champ de la requête |
| Ajouter une tâche | Déployer un autre modèle | Déposer un fichier |
| Base model toujours disponible | Non | Oui |
| Retour arrière | Redéployer | Cesser de router vers cet adapter |

Règle de décision : **une seule tâche et des opérations simples → fusionner. Plusieurs tâches, ou le base model toujours nécessaire → ne pas fusionner.**

Cette dernière ligne est sous-estimée. Avec un adapter non fusionné, revenir en arrière sur un mauvais fine-tuning est un changement de routage plutôt qu'un déploiement, et le base model est toujours là comme solution de repli.

### Comment fonctionne le service multi-adapters

L'approche naïve, qui échange les poids de l'adapter entre les requêtes, sérialise tout et détruit le débit, parce que le batching est la source de l'efficacité de l'inférence.

Les vraies implémentations regroupent en batch des requêtes qui utilisent des adapters *différents*. Le calcul du base model est partagé par tout le batch, puisqu'il est identique pour tous, et les contributions des adapters sont calculées par requête avec des kernels spécialisés qui gèrent un batch de petites multiplications de matrices hétérogènes. Le travail S-LoRA ([arXiv:2311.03285](https://arxiv.org/abs/2311.03285)) est la référence pour servir de nombreux adapters en parallèle, y compris garder les adapters inactifs en mémoire de l'hôte et les paginer à la demande.

Ce que cela signifie en pratique :

- Servir des dizaines d'adapters à partir d'un seul base model est un problème résolu avec de vraies implémentations, pas une idée de recherche.
- Le surcoût est faible mais réel, et il croît avec le nombre d'adapters *distincts* présents dans un batch.
- Les adapters devraient partager le rank et les target modules autant que possible. Des formes hétérogènes sont plus difficiles à regrouper efficacement.

Dans vLLM, la forme est à peu près : activer la prise en charge de LoRA, enregistrer les adapters, et en nommer un par requête. Vérifiez les flags actuels et les limites de rank maximal et de nombre maximal d'adapters dans la documentation de la version installée, car cette surface change et les limites sont fixées au démarrage du serveur.

### Quantification au moment du service, gardée à part

Une décision indépendante de tout ce qui précède, et qui mérite d'être rappelée parce que les deux sont confondues :

- **La quantification au moment de l'entraînement** (étape 4) est un budget mémoire pour le run d'entraînement.
- **La quantification au moment du service** réduit le modèle que vous déployez, et son coût en qualité est permanent pour chaque requête.

Vous pouvez entraîner face à un base model en 4 bits et servir en bf16. Vous pouvez entraîner en bf16 et servir quantifié. Ce sont des choix sans rapport, avec des compromis sans rapport, et aucun n'implique l'autre.

Si vous servez quantifié, évaluez l'artefact quantifié. Évaluer un modèle en bf16 et livrer un modèle en 4 bits signifie que vos chiffres décrivent quelque chose que vous n'avez pas déployé, ce qui est une erreur étonnamment courante.

### L'essentiel opérationnel

**Versionnez tout.** Base model et révision, adapter, tokenizer, pile de service. Une réponse devrait être traçable jusqu'à la configuration exacte qui l'a produite.

**Fixez les paramètres d'échantillonnage.** Temperature, top-p, nombre maximal de tokens, séquences d'arrêt. Ils changent la qualité de la sortie autant que le fine-tuning, et une dérive non documentée d'une valeur par défaut sera mal diagnostiquée comme une régression du modèle.

**Journalisez les entrées et les sorties.** Le trafic de production est la meilleure source de votre prochain jeu d'entraînement et de votre prochain jeu held-out, parce qu'il est tiré de la distribution réelle plutôt que de celle que vous aviez imaginée. Respectez les contraintes évidentes de confidentialité et de conservation ; le but est de collecter délibérément plutôt que de découvrir plus tard qu'on ne l'a pas fait.

**Surveillez la distribution, pas seulement la latence.** Longueur des entrées, longueur des sorties, taux de refus, validité du schéma. Une dérive de la distribution des entrées est l'indicateur avancé du fait que les hypothèses de votre fine-tuning ont expiré.

**Gardez le base model joignable.** Que ce soit comme route de repli, comme point de comparaison, ou les deux. Pouvoir faire un test A/B du base model face au fine-tuning en production est la preuve la plus forte disponible sur l'utilité du fine-tuning.

### L'échantillonnage n'est pas un correctif

Une mise en garde, parce que c'est un piège courant. Si un fine-tuning sous-performe, la temperature et top-p ne sont pas la réparation. Ils changent la forme de la distribution, pas son contenu. Régler l'échantillonnage pour compenser un problème d'entraînement le masque et rend la comparaison suivante ininterprétable : vous ne savez plus laquelle de deux variables a produit une différence.

Corrigez l'entraînement dans l'entraînement. Fixez l'échantillonnage et n'y touchez plus.

## Pratique

1. ▢ Cinq tâches, un base model. Fusionné ou non fusionné, et que coûte le choix ?

<details markdown="1"><summary>Vérifier</summary>

Non fusionné. Un base model en mémoire plus cinq petits adapters, contre cinq copies complètes de modèle.

Coûts : la pile de service doit prendre en charge les adapters, et il y a un petit surcoût par requête qui croît avec le nombre d'adapters distincts dans un batch.

</details>

2. ▢ Pourquoi l'échange naïf d'adapters entre les requêtes détruit-il le débit ?

<details markdown="1"><summary>Vérifier</summary>

Il sérialise les requêtes par adapter, ce qui empêche le batching dont dépend l'efficacité de l'inférence.

Les vraies implémentations regroupent en batch des requêtes avec des adapters différents, en partageant le calcul du base model et en calculant les contributions des adapters par requête avec des kernels spécialisés.

</details>

3. ▢ Vous avez entraîné face à un base model en 4 bits. Devez-vous servir en 4 bits ?

<details markdown="1"><summary>Vérifier</summary>

Non. La précision d'entraînement et la précision de service sont indépendantes. Fusionnez dans le base model en pleine précision et servez en bf16 si vous avez la mémoire.

La quantification au moment de l'entraînement était un budget pour le run. Elle n'a pas à suivre l'artefact en production.

</details>

4. ▢ Votre fine-tuning sous-performe en production. Un collègue suggère de baisser la temperature. Évaluez.

<details markdown="1"><summary>Vérifier</summary>

Cela peut améliorer les sorties, et ne règle pas le problème. L'échantillonnage remodèle la distribution que le modèle a produite ; il ne peut pas ajouter une capacité que le modèle n'a pas.

Pire, il introduit une seconde variable modifiée, donc la comparaison suivante devient ininterprétable. Fixez l'échantillonnage, diagnostiquez l'entraînement.

</details>

5. ▢ Quel avantage du service non fusionné compte le plus sur le plan opérationnel ?

    - a) L'empreinte mémoire réduite quand on sert de nombreuses tâches
    - b) La possibilité de revenir en arrière en changeant une règle de routage
    - c) L'absence de tout surcoût de calcul par requête
    - d) La compatibilité avec tous les serveurs d'inférence existants

<details markdown="1"><summary>Vérifier</summary>

**b)** La possibilité de revenir en arrière en changeant une règle de routage.

(a) est réel et c'est souvent la raison mise en avant, mais (b) est ce que vous voulez à deux heures du matin. (c) est faux, puisque le non fusionné ajoute un petit surcoût. (d) est à l'envers ; le fusionné est l'option universellement compatible.

</details>

6. ▢ Vous avez évalué en bf16 et livré un modèle quantifié en 4 bits. Qu'est-ce qui ne va pas ?

<details markdown="1"><summary>Vérifier</summary>

Vos chiffres décrivent un modèle que vous n'avez pas déployé. La quantification au moment du service porte un coût permanent en qualité sur chaque requête, et il n'a jamais été mesuré.

Évaluez l'artefact que vous livrez. Toujours.

</details>

## Exercices en situation réelle

- [ ] Servez votre adapter via un serveur d'inférence et obtenez une vraie complétion à travers tout le chemin.
- [ ] Chargez deux adapters sur un même base model et passez de l'un à l'autre par un champ de la requête. Confirmez que les sorties diffèrent comme il se doit.
- [ ] Mesurez la latence pour le fusionné, le non fusionné à adapter unique, et le non fusionné multi-adapters. Notez le surcoût.
- [ ] Demain : écrivez chaque version et chaque paramètre d'échantillonnage de votre chemin de service, dans un seul fichier.

## Pour aller plus loin

- [Doc : LoRA adapters, vLLM](https://docs.vllm.ai/en/latest/features/lora.html)
- [Article : "S-LoRA: Serving Thousands of Concurrent LoRA Adapters", Sheng et al., arXiv:2311.03285](https://arxiv.org/abs/2311.03285)
- [Leçon 26. Coût, latence et débit](0026-cost-latency-and-throughput.md)

---

Ça ne passe pas ? Relisez la source primaire en haut de page, car cette leçon la condense et c'est dans la condensation que la compréhension s'échappe. Consultez le [glossaire](../GLOSSARY.md) pour tout terme qui vous a paru glissant.

Si c'est la leçon elle-même qui n'est pas claire plutôt que la matière, c'est un défaut : [ouvrez une issue](https://github.com/TokenCemetery/teach/issues).
