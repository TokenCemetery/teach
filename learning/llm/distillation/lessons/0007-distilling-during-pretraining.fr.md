---
title: "7. Distiller pendant le pré-entraînement"
description: "Comment Gemma 2 et Minitron ont utilisé la distribution d'un enseignant comme signal d'entraînement à grande échelle, et ce que coûte le stockage des logits"
type: lesson
---

# Leçon 7. Distiller pendant le pré-entraînement

**Lien avec la mission :** La mission vous demande d'écrire la loss au niveau du token et de dire quand on ne peut pas l'utiliser, et cette leçon montre cette loss comme signal d'entraînement de deux vraies familles de modèles, avec le coût de conservation des distributions de l'enseignant compté en octets.
**Source primaire :** [Article : "Gemma 2: Improving Open Language Models at a Practical Size", Gemma Team, 2024](https://arxiv.org/abs/2408.00118)
**Prérequis :** [Leçon 6](0006-the-tokenizer-constraint.md), [Distillation au niveau du token](../GLOSSARY.md), [Logit](../GLOSSARY.md), [Logits top-k](../GLOSSARY.md)

## Échauffement

1. ▢ Pourquoi un élève Llama avec un enseignant Qwen exclut-il la loss simple au niveau du token, même quand les deux vous donnent leurs logits complets ?

<details markdown="1"><summary>Vérifier</summary>

La loss compare la probabilité i de la ligne de l'élève à la probabilité i de celle de l'enseignant, et des tokenizers différents font de l'index i un token différent, avec des tailles et des positions éventuellement différentes. Les contournements de l'étape 2 sont une loss inter-tokenizers ou un élève de la famille de l'enseignant.

</details>

2. ▢ Quelle direction de la KL un élève qui couvre les modes minimise-t-il, et dans quel cadre Minitron l'a-t-il trouvée la meilleure ?

<details markdown="1"><summary>Vérifier</summary>

La [KL directe](../GLOSSARY.md). Minitron l'a trouvée meilleure que la KL inverse en ré-entraînant des base models élagués, avec une loss LM de 2.155 contre 2.665 pour un Minitron 8B élagué en profondeur (tableau 16 de leur article). C'est un seul cadre, et la leçon 5 donne les preuves d'instruction tuning pour l'autre direction.

</details>

## À savoir

Cette leçon enseigne la moitié distillation de deux recettes d'entraînement. L'organisation d'un run de pré-entraînement, des données au matériel, relève du [parcours de pré-entraînement](../../pretraining/), et l'élagage comme méthode ne relève d'aucun des deux.

### La distillation comme objectif de pré-entraînement : Gemma 2

Le rapport de Gemma 2 entraîne ses modèles 2B et 9B par distillation des connaissances au lieu de la prédiction du token suivant. La motivation est que l'entraînement au token suivant ne progresse que de façon logarithmique avec les données, et que les petits modèles ont besoin de runs très longs pour s'améliorer. La distillation remplace le vecteur one-hot à chaque token par la distribution des tokens suivants d'un grand modèle, ce qui, dit le rapport, donne des gradients plus riches. Son objectif déclaré est d'entraîner sur un très grand nombre de tokens avec la distillation pour simuler un entraînement au-delà du nombre de tokens disponibles (introduction).

Les faits que donne le rapport :

- Le modèle 2B a été entraîné sur 2 trillions de tokens, le 9B sur 8 trillions, et le 27B sur 13 trillions (section 3.1). Le 27B a été entraîné de zéro, sans distillation.
- Les nombres de tokens des 2B et 9B représentent plus de 50 fois la quantité optimale en calcul prédite par Hoffmann et al. (introduction).
- La loss est la log-vraisemblance négative entre la probabilité de l'enseignant pour chaque token étant donné son contexte et celle de l'élève, minimisée sur l'élève : la somme des -P_T(x | x_c) log P_S(x | x_c) (section 3.2). C'est la loss de la leçon 4 à la température 1.
- Le vocabulaire compte 256,128 entrées (tableau 1), hérité de Gemini, et la longueur de contexte est de 8,192 tokens (section 2).

Ses ablations utilisent un enseignant de 7B, pas le final. Un élève de 2B entraîné sur 500B tokens, ce que le rapport dit être 10 fois le nombre optimal en calcul pour 2B, a obtenu en moyenne 60.3 sur trois benchmarks de zéro et 67.7 distillé (tableau 6). Avec l'enseignant fixé à 7B, la perplexité de validation à 200M, 400M et 1B de paramètres était de 23, 19 et 17 de zéro et de 21, 17 et 15 distillée (tableau 7). Le rapport dit aussi que le nouveau 2B, à 2T tokens, améliore nettement le 2B de Gemma 1 à 3T tokens (section 6.1). Ce sont les comparaisons de Google lui-même.

### Ce que le rapport ne dit pas

Le rapport ne nomme pas l'enseignant des modèles 2B et 9B finaux ni ne donne sa taille. Il ne décrit pas comment la distribution de l'enseignant a été fournie à l'élève : stockée, calculée en parallèle de l'entraînement, ou approchée. Les affirmations sur un top-k échantillonné ou tronqué dans Gemma 2 ne sont pas dans le rapport. La section suivante calcule ce que coûte chaque option, pour que vous puissiez raisonner dessus sans source sur ce choix.

### Ce que coûte le stockage de l'enseignant

Une distribution sur le vocabulaire pour chaque token d'entraînement est volumineuse. Le script utilise le vocabulaire et les nombres de tokens de Gemma 2 et deux hypothèses de cette leçon : des probabilités en bf16 à 2 octets et, pour la version tronquée, un k illustratif de 256 avec un index de token de 4 octets.

```python
vocab = 256_128            # Gemma 2 vocabulary size (Table 1 of the report)
tokens = {"2B run": 2e12, "9B run": 8e12}

full = vocab * 2           # bf16: 2 bytes per probability
k = 256                    # an illustrative k, not a number from any paper
topk = k * (2 + 4)         # 2-byte probability + 4-byte token index

print("full per token: %d bytes" % full)
print("top-%d per token: %d bytes (%.1fx smaller)" % (k, topk, full / topk))
print("full per 8192-token sequence: %.2f GB" % (full * 8192 / 1e9))
for name, n in tokens.items():
    print(name, "full: %.2f EB" % (full * n / 1e18), " top-%d: %.2f PB" % (k, topk * n / 1e15))
```

Prédisez l'ordre de grandeur du coût de la distribution complète pour le run 2B avant de l'exécuter. La sortie :

```text
full per token: 512256 bytes
top-256 per token: 1536 bytes (333.5x smaller)
full per 8192-token sequence: 4.20 GB
2B run full: 1.02 EB  top-256: 3.07 PB
9B run full: 4.10 EB  top-256: 12.29 PB
```

Stocker les distributions complètes pour le run 2B représente environ un exaoctet, et pour le run 9B environ quatre. Garder 256 entrées par token divise cela par 333.5, à des pétaoctets, et ce chiffre ne compte les tokens d'entraînement qu'une fois, sans époque répétée. La troncature coûte aussi quelque chose. La masse de queue écartée doit être gérée, en renormalisant ou en la traitant comme un seul seau, et le choix modifie la cible.

Il existe une alternative qui ne stocke rien : faire tourner l'enseignant en parallèle de l'élève et lire sa distribution dans la passe avant. Minitron prend cette voie, et note que la distillation ajoute le surcoût d'une passe avant supplémentaire sur l'enseignant, ils comparent donc leurs runs distillés et conventionnels à calcul égal (section 4). La voie qu'un laboratoire donné a utilisée n'est pas ce que cette leçon affirme.

Les auteurs de Minitron ont aussi testé directement la troncature. Dans leur annexe sur la distillation (A.3), ne garder que les K meilleurs logits de l'enseignant et de l'élève pour K jusqu'à 100 a causé une baisse significative de précision. La baisse a disparu pour de plus grands K, mais les résultats n'étaient pas meilleurs que sans troncature. C'est une seule configuration de ré-entraînement de modèle élagué, et le K à partir duquel la troncature cesse de nuire différera selon le vocabulaire et le modèle.

### Élagage plus distillation : Minitron

Minitron (Muralidharan et al., 2024) compresse Nemotron-4 15B en l'élaguant et en retrouvant la précision par ré-entraînement avec l'original comme enseignant. Son élève démarre comme une copie élaguée, il partage donc le tokenizer de l'enseignant par construction. Cette leçon ne prend que la moitié distillation.

- **Tokens.** Les modèles Minitron 8B et 4B ont chacun été ré-entraînés sur 94 milliards de tokens. L'article compare Minitron 8B à Nemotron-3 8B, entraîné sur 3.8 trillions, et énonce l'économie comme 40 fois moins de tokens (tableau 2).
- **Distillation contre ré-entraînement conventionnel.** Pour un modèle 4B, ils comparent à calcul égal (tableau 11). L'entraînement de zéro sur 150B tokens a donné HellaSwag 46.22 et MMLU 24.36. Élaguer 15B vers 4B et ré-entraîner de façon conventionnelle sur 150B a donné 50.85 et 24.57. Élaguer et ré-entraîner avec distillation sur 100B tokens a donné 51.04 et 37.81. Le run distillé utilise 100B tokens contre 150B à cause de la passe avant supplémentaire de l'enseignant. Cela représente un gain de 4.8 points sur HellaSwag et de 13.5 sur MMLU par rapport à l'entraînement de zéro.
- **Loss.** KL directe sur les logits, à la température 1, avec la loss sur les logits seule meilleure qu'un mélange pondéré avec la loss de modélisation de langage, et aucun gain à tronquer au top K (section 4 et annexe A.3).

L'article de suivi (Sreenivas et al., 2024) applique la recette à Llama 3.1 8B et Mistral NeMo 12B. Il ajoute une étape avant la distillation : la correction de l'enseignant. Quand les données de pré-entraînement d'origine ne sont pas disponibles, l'enseignant donne des indications sous-optimales sur un jeu de données différent, ce que les auteurs attribuent à un changement dans la distribution des tokens de sous-mots. Ils font donc d'abord un fine-tuning de l'enseignant sur environ 100B tokens des données de distillation, avec un warm-up et de faibles learning rates. Puis ils élaguent et distillent avec la KL directe sur les logits seulement. Llama-3.1-Minitron 4B a été ré-entraîné sur 94B tokens et MN-Minitron-8B sur 380B (tableau 4). L'article dit que le 4B se compare favorablement à Llama 3.1 8B avec 150 fois moins de tokens, 94B contre 15T, et que le 8B surpasse Llama 3.1 8B avec 40 fois moins, 380B contre 15T (section 5.1). Ce sont les comparaisons de NVIDIA sur sa propre évaluation.

## Pratique

1. ▢ Dans le rapport, quels modèles Gemma 2 ont été entraînés avec la distillation, et combien de tokens chacun a-t-il vus ?

    - a) Le 2B sur 8T et le 27B sur 2T
    - b) Le 9B sur 8T et le 27B sur 13T
    - c) Les trois modèles ont chacun été entraînés sur 13T tokens
    - d) Le 2B sur 2T et le 9B sur 8T

<details markdown="1"><summary>Vérifier</summary>

**d)** Le 27B a été entraîné de zéro sur 13T tokens, donc (b) et (c) l'incluent à tort. Le choix (a) échange les nombres de tokens. Le rapport énonce les nombres à la section 3.1.

</details>

2. ▢ Avec un vocabulaire de 256,128 et 2 octets par probabilité, combien d'octets prend une distribution complète du token suivant, et combien de gigaoctets cela représente-t-il pour une seule séquence de 8,192 tokens ?

<details markdown="1"><summary>Indice</summary>

Multipliez le vocabulaire par les octets par entrée, puis par la longueur de séquence, puis divisez par un milliard.

</details>

<details markdown="1"><summary>Vérifier</summary>

256,128 fois 2 donne 512,256 octets par token. Fois 8,192, cela donne 4,196,401,152 octets, environ 4.20 Go pour une séquence. Un run d'entraînement compte de nombreux millions de telles séquences, c'est pourquoi se pose la question de stocker ou de recalculer.

</details>

3. ▢ En gardant les 256 meilleures entrées, chacune avec une probabilité de 2 octets et un index de 4 octets, quelle est la taille de l'enregistrement d'un token, et de combien est-il plus petit que la distribution complète ?

<details markdown="1"><summary>Vérifier</summary>

256 fois 6 donne 1,536 octets, soit 333.5 fois moins que 512,256. Le k de 256 et les tailles en octets sont des hypothèses de cette leçon, pas des chiffres de Gemma 2. L'enregistrement laisse aussi de côté la queue de la distribution, qui doit être renormalisée ou regroupée en seau, et ce choix modifie la cible.

</details>

4. ▢ Un message de forum dit que Gemma 2 s'est entraîné sur une distribution d'enseignant stockée en top-256. Que faites-vous de cette affirmation ?

<details markdown="1"><summary>Vérifier</summary>

Cherchez-la dans le rapport. Le rapport énonce la loss, les nombres de tokens et les ablations, et ne décrit pas comment la distribution a été fournie. L'affirmation n'est donc pas vérifiée d'après le rapport. Traitez-la comme non étayée, notez ce qui manque, et cherchez une source primaire comme le texte des auteurs avant de vous y fier.

</details>

5. ▢ Dans le tableau 11 de Minitron, l'élagage plus ré-entraînement conventionnel a atteint MMLU 24.57 et l'élagage plus distillation 37.81, avec la distillation sur moins de tokens. Pourquoi les nombres de tokens sont-ils 150B et 100B, et quelle est la limite du tableau ?

<details markdown="1"><summary>Vérifier</summary>

Ils comparent à calcul égal, et la distillation dépense une partie de son budget sur la passe avant de l'enseignant, elle obtient donc 100B tokens contre 150B. Le tableau porte sur un modèle 4B élagué à partir de Nemotron-4 15B. Les auteurs l'utilisent pour montrer que la distillation bat le ré-entraînement conventionnel après élagage. Il ne montre pas le gain pour d'autres enseignants, tailles ou benchmarks.

</details>

6. ▢ La correction de l'enseignant dans l'article de suivi de Minitron fait un fine-tuning de l'enseignant sur environ 100B tokens avant de distiller. Quand est-elle nécessaire, et que blâment les auteurs quand on la saute ?

<details markdown="1"><summary>Vérifier</summary>

Elle est nécessaire quand les données de pré-entraînement d'origine de l'enseignant ne sont pas disponibles, si bien que les données de distillation ont une distribution différente. Les auteurs disent que l'enseignant donne alors des indications sous-optimales, et font l'hypothèse que c'est parce que la distribution des tokens de sous-mots diffère entre les données d'origine de l'enseignant et les données utilisées pour distiller. L'explication est leur hypothèse.

</details>

## Exercices en situation réelle

- [ ] Exécutez le script de stockage avec la taille de votre propre vocabulaire et avec k valant 64 et 1,024, et notez les trois rapports de coût.
- [ ] Ouvrez le tableau 11 de l'article Minitron et trouvez le marqueur de calcul égal. Notez quelle ligne a utilisé l'enseignant et combien de tokens elle a vus.
- [ ] Demain : sans notes, énoncez les trois nombres de tokens de Gemma 2 et l'arithmétique de stockage pour un token, puis dites ce que le rapport laisse non dit sur l'enseignant.

## Pour aller plus loin

- [Loss de distillation](../reference/distillation-losses.md)
- [Article : "Gemma 2: Improving Open Language Models at a Practical Size", Gemma Team, 2024](https://arxiv.org/abs/2408.00118)
- [Article : "Compact Language Models via Pruning and Knowledge Distillation", Muralidharan et al., 2024](https://arxiv.org/abs/2407.14679)
- [Article : "LLM Pruning and Distillation in Practice: The Minitron Approach", Sreenivas et al., 2024](https://arxiv.org/abs/2408.11796)
- [Ressources](../RESOURCES.md)

---

Ça ne passe pas ? Relisez la source primaire en haut de page, car cette leçon la condense et c'est dans la condensation que la compréhension s'échappe. Consultez le [glossaire](../GLOSSARY.md) pour tout terme qui vous a paru glissant.

Si c'est la leçon elle-même qui n'est pas claire plutôt que la matière, c'est un défaut : [ouvrez une issue](https://github.com/TokenCemetery/teach/issues).
