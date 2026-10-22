---
title: "18. Le QAT pour les LLM"
description: "Ce que le quantization-aware training coûte sur un LLM, ce qu'il récupère, et quand le PTQ suffit"
type: lesson
---

# Leçon 18. Le QAT pour les LLM

**Lien avec la mission :** La mission vous demande de dire quand le quantization-aware training vaut son coût face à la quantification post-entraînement, ce qui demande le prix, le gain mesuré, et les cas où le gain est nul.
**Source primaire :** [Article : "LLM-QAT: Data-Free Quantization Aware Training for Large Language Models", Liu et al., 2023](https://arxiv.org/abs/2305.17888)
**Prérequis :** [Leçon 17](0017-fake-quantization-and-the-ste.md), [Quantization-aware training](../GLOSSARY.md), [Quantification post-entraînement](../GLOSSARY.md), [Quantification weight-only](../GLOSSARY.md)

## Échauffement

1. ▢ La leçon 9 a comparé l'arrondi au plus proche en 8 bits et en 4 bits ou moins. Dans lequel tient-il, et pourquoi décroche-t-il dans l'autre ?

<details markdown="1"><summary>Vérifier</summary>

Il tient en 8 bits, où la grille a 256 niveaux et où l'[erreur d'arrondi](../GLOSSARY.md) par poids est petite. En 4 bits, il y a 16 niveaux, chaque poids peut être décalé d'au plus la moitié d'un pas bien plus grand, et l'arrondi simple n'a rien qui compense les erreurs. Cet écart est la place où GPTQ, AWQ et le QAT se font concurrence.

</details>

2. ▢ Pourquoi une boucle d'entraînement ne peut-elle pas simplement dériver à travers `round`, et que fait la fake quantization à ce sujet ?

<details markdown="1"><summary>Vérifier</summary>

La dérivée de round est nulle presque partout, donc aucun gradient n'atteint les poids. La fake quantization garde une copie maître en float, applique la quantification et la déquantification dans la passe avant, et utilise l'[estimateur straight-through](../GLOSSARY.md) pour faire passer le gradient à travers l'étape d'arrondi dans la passe arrière, avec un gradient nul pour les valeurs que le clamp a coupées.

</details>

## À savoir

### Ce que coûte le QAT sur un LLM

Le QAT est un entraînement ordinaire avec de la fake quantization insérée, donc il hérite des coûts de l'entraînement. Nagel et al. les listent : un entraînement plus long, le besoin de données et la recherche d'hyperparamètres ([white paper](https://arxiv.org/abs/2106.08295), section 4). Deux mesures propres aux LLM le rendent concret.

L'équipe PyTorch l'a mesuré avec son flux QAT de torchao sur Llama3-8B, avec des activations dynamiques int8 par token et des poids groupés int4. Chacune des 225 couches linéaires reçoit au moins une opération de fake quantization. Dans leurs microbenchmarks, le fine-tuning QAT était environ 34 % plus lent qu'un fine-tuning complet ordinaire, et avec l'activation checkpointing la mémoire utilisée augmentait d'environ 2.35 GB par GPU ([billet PyTorch](https://pytorch.org/blog/quantization-aware-training/)). Un fine-tuning de 20 heures devient environ 27 heures. Ce sont leurs chiffres sur leur configuration, donc traitez-les comme un ordre de grandeur.

Le second coût, ce sont les données. Liu et al. notent que les données d'entraînement d'origine d'un LLM sont souvent indisponibles, et que les modèles sont souvent entraînés en plusieurs étapes (instruction tuning, apprentissage par renforcement) qu'il serait difficile de reproduire pendant le QAT. Leur réponse est l'entraînement **data-free** : le modèle en pleine précision génère lui-même du texte, avec les premiers tokens choisis de façon gloutonne et le reste échantillonné, et le modèle quantifié est entraîné à égaler le modèle en pleine précision pris comme enseignant. Ils rapportent avoir distillé les modèles quantifiés à partir d'un petit jeu de seulement 100,000 séquences échantillonnées, sur un seul nœud de 8 GPU. Les séquences étaient plafonnées à 1,024 tokens, donc le jeu entier fait au plus environ 100 millions de tokens, un chiffre qui découle de leurs deux nombres plutôt que d'un chiffre qu'ils énoncent.

### Ce qu'il récupère

LLM-QAT quantifie les poids, les activations et le KV cache, notés W-A-KV en bits. Leur tableau 1 rapporte la précision zero-shot moyenne sur sept tâches de bon sens. Pour LLaMA-7B, la moyenne en pleine précision est 66.2.

| Réglage (W-A-KV) | RTN | SmoothQuant | LLM-QAT |
|---|---|---|---|
| 8-8-8 | 65.6 | 66.3 | 66.0 |
| 4-16-16 (poids en 4 bits seulement) | 63.0 | non rapporté | 64.4 |
| 4-8-4 | 41.2 | 43.2 | 60.7 |

En 8 bits, chaque méthode est à un point de la pleine précision. Le 4 bits weight-only tient déjà sous RTN, et le QAT gagne 1.4 point. Le réglage à activations et KV cache en 4 bits est celui où les méthodes PTQ s'effondrent et où le QAT reste à moins de 5.5 points. Sur LLaMA-30B, la moyenne en pleine précision est 71.4 : 4-8-4 donne 42.5 avec RTN et 40.7 avec SmoothQuant contre 69.9 pour LLM-QAT, mais les poids en 4 bits seuls donnent 70.1 avec RTN, 70.3 avec GPTQ et 70.1 avec LLM-QAT. Le résumé de l'article lui-même concorde : toutes les méthodes se comportent bien en 8 bits, et quand les poids, les activations ou le KV cache descendent sous 8 bits, les méthodes PTQ perdent en précision tandis que LLM-QAT tient bien mieux. Les références PTQ ici sont RTN, GPTQ et SmoothQuant. Les méthodes de rotation de la leçon 15 sont venues plus tard et ne figurent pas dans cette comparaison.

Le billet de torchao rapporte le même motif du côté de l'entraînement. Sur Llama3-8B avec le schéma 8da4w, le QAT a récupéré 96 % de la dégradation d'accuracy normalisée sur hellaswag par rapport au PTQ, et 68 % de la dégradation de perplexity par mot sur wikitext. Avec des poids en 2 bits, la perplexity par mot du modèle PTQ sur wikitext était de 603,336. Sauter les 3 premières et les 2 dernières couches l'a ramenée à 6,766, et y ajouter le QAT l'a ramenée à 30. Sans sauter ces couches, le QAT était bien moins efficace, donc le QAT n'a pas sauvé les 2 bits à lui seul.

### QLoRA est le voisin, pas le QAT

[QLoRA](https://arxiv.org/abs/2305.14314) entraîne aussi un modèle quantifié, mais il rétropropage à travers un modèle de base gelé en 4 bits vers des adapters de faible rang. Les poids de base ne changent jamais, donc le modèle n'apprend pas à survivre à son propre arrondi : la quantification est là pour faire tenir le fine-tuning en mémoire. Ce parcours ne l'enseigne pas. Le parcours de fine-tuning, oui, et sa fiche [budget mémoire](../../finetuning/reference/memory-budget.md) compte les octets.

### Quand le PTQ suffit, et quand le QAT rapporte

| Situation | Preuve | Défaut |
|---|---|---|
| Poids et activations en 8 bits | Tableau 1 ci-dessus ; [Kurtic et al.](https://arxiv.org/abs/2411.02355) rapportent un FP8 effectivement sans perte sur les tailles de Llama 3.1 et un INT8 bien réglé à 1 à 3 % de dégradation | PTQ |
| Poids en 4 bits seulement, grand modèle | Ligne LLaMA-30B ci-dessus ; Kurtic et al. trouvent que l'INT4 weight-only rivalise avec le 8 bits | PTQ, puis mesurer |
| Poids en 4 bits seulement, petit modèle | LLaMA-7B : RTN perd 3.2 points, QAT 1.8 | Essayer le PTQ, QAT si l'écart compte |
| Activations ou KV cache en 4 bits | LLaMA-30B 4-8-4 : RTN 42.5, LLM-QAT 69.9 | QAT, ou les rotations de la leçon 15, testées |
| 3 bits ou moins | Expériences 2 bits et 3 bits de torchao | QAT plus conservation des couches sensibles |
| Modèle entraîné sur énormément de données | [Kumar et al.](https://arxiv.org/abs/2411.04330) trouvent que la dégradation du PTQ croît à mesure qu'un modèle voit plus de données | Tester tôt le PTQ, s'attendre à un écart plus grand |

Le résultat de Kumar vient de modèles allant jusqu'à 1.7B paramètres entraînés sur jusqu'à 26B tokens, donc il dit où regarder, pas quelle est la taille de l'écart pour un grand modèle. Chaque ligne est une valeur par défaut à tester contre votre propre référence, pas une règle.

## Pratique

1. ▢ D'après les chiffres de LLM-QAT ci-dessus pour LLaMA-30B (pleine précision 71.4), combien de points RTN perd-il avec les poids en 4 bits seulement, et combien avec 4-8-4 ? Le QAT vaut-il son coût dans chaque cas ?

<details markdown="1"><summary>Vérifier</summary>

RTN perd 1.3 point avec les poids en 4 bits seulement (70.1) et 28.9 points en 4-8-4 (42.5). Avec les poids seuls, LLM-QAT obtient aussi 70.1, donc il n'achète rien ici et le PTQ suffit. En 4-8-4, LLM-QAT obtient 69.9, soit 1.5 point sous la pleine précision, donc le coût de l'entraînement rachète presque toute la précision perdue. Le QAT rapporte quand les activations ou le KV cache passent en 4 bits, pas quand seuls les poids le font.

</details>

2. ▢ Un fine-tuning complet de votre modèle prend 20 heures. D'après le microbenchmark de torchao, combien de temps prendrait à peu près le même run avec le QAT, et qu'est-ce qui croît d'autre ?

<details markdown="1"><summary>Vérifier</summary>

Environ 27 heures (20 fois 1.34 font 26.8). La mémoire croît aussi, d'environ 2.35 GB par GPU avec l'activation checkpointing activé, parce que les poids doivent être clonés avant l'application de la fake quantization. C'est une configuration mesurée sur Llama3-8B, donc votre run peut différer.

</details>

3. ▢ Lequel de ces énoncés décrit QLoRA ?

    - a) Entraîner des adapters à travers un modèle de base gelé en 4 bits
    - b) Mettre à jour tous les poids derrière une étape d'arrondi straight-through
    - c) Distiller le modèle sur du texte qu'il a généré lui-même
    - d) Quantifier le KV cache tout en faisant le fine-tuning du modèle

<details markdown="1"><summary>Vérifier</summary>

**a)** QLoRA garde le modèle de base quantifié gelé et entraîne de petits adapters à travers lui. (b) décrit le QAT en général : les poids changent pour survivre à l'arrondi. (c) est la distillation data-free de LLM-QAT. (d) est quelque chose que LLM-QAT fait aussi, et pas QLoRA.

</details>

4. ▢ Dans l'expérience 2 bits de torchao, le QAT a fait passer la perplexity par mot sur wikitext de 6,766 à 30. Cela montre-t-il que le QAT seul fait fonctionner des poids en 2 bits ?

<details markdown="1"><summary>Indice</summary>

Regardez ce qui avait déjà été fait au modèle avant l'ajout du QAT, et ce qui s'est passé sans lui.

</details>

<details markdown="1"><summary>Vérifier</summary>

Non. Ce modèle avait déjà ses 3 premières et ses 2 dernières couches laissées non quantifiées, une étape qui coûtait de la taille de modèle et avait fait passer la perplexity de 603,336 à 6,766. Sans sauter ces couches, le QAT était bien moins efficace. À très faible nombre de bits, le QAT est un ingrédient à côté de la conservation des couches sensibles en plus haute précision, ce qui est une décision sur ce qu'il faut quantifier autant que sur la manière.

</details>

5. ▢ Le modèle int4 PTQ de votre équipe est bon, mais le prochain modèle que vous entraînez l'est sur trois fois plus de données et sa version int4 obtient un score nettement pire. Que suggère la littérature de cette leçon, et que ne faut-il pas en conclure ?

<details markdown="1"><summary>Vérifier</summary>

Kumar et al. rapportent que la dégradation du PTQ croît à mesure qu'un modèle est entraîné sur plus de données, donc un écart plus grand après un entraînement plus long est ce que prédit la preuve des lois d'échelle. Les options à tester sont une largeur en bits plus haute, une méthode PTQ plus forte, ou le QAT. N'en concluez pas que c'est inévitable et n'en donnez pas la taille : leur preuve porte sur des modèles allant jusqu'à 1.7B paramètres et 26B tokens, donc faites la comparaison sur votre propre modèle contre la référence en pleine précision.

</details>

## Exercices en situation réelle

- [ ] Ouvrez le billet PyTorch sur le QAT et trouvez la phrase sur ce que produit l'étape convert par rapport au flux PTQ. Notez ce que cela implique pour déployer un modèle QAT sur les mêmes kernels qu'un modèle PTQ.
- [ ] Choisissez un modèle ouvert quantifié que vous pourriez déployer et lisez sa fiche de modèle : dit-elle si les poids viennent du PTQ ou du QAT, et quelles données de calibration ou d'entraînement ont été utilisées ?
- [ ] Demain : sans notes, écrivez trois coûts du QAT, les situations où le PTQ suffit, et la situation où le QAT rapporte.

## Pour aller plus loin

- [QAT et matériel](../reference/qat-and-hardware.md)
- [Billet : "Quantization-Aware Training for Large Language Models with PyTorch", PyTorch Blog, 2024](https://pytorch.org/blog/quantization-aware-training/)
- [Article : "QLoRA: Efficient Finetuning of Quantized LLMs", Dettmers et al., 2023](https://arxiv.org/abs/2305.14314)
- Fine-tuning : [Budget mémoire](../../finetuning/reference/memory-budget.md)
- [Ressources](../RESOURCES.md)

---

Ça ne passe pas ? Relisez la source primaire en haut de page, car cette leçon la condense et c'est dans la condensation que la compréhension s'échappe. Consultez le [glossaire](../GLOSSARY.md) pour tout terme qui vous a paru glissant.

Si c'est la leçon elle-même qui n'est pas claire plutôt que la matière, c'est un défaut : [ouvrez une issue](https://github.com/TokenCemetery/teach/issues).
