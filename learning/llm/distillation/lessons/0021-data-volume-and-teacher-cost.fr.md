---
title: "21. Volume de données et coût de l'enseignant"
description: "Compter l'inférence de l'enseignant dans le budget, et décider combien de données de distillation suffisent"
type: lesson
---

# Leçon 21. Volume de données et coût de l'enseignant

**Lien avec la mission :** La mission vous demande de choisir un volume de données en comptant le coût propre de l'enseignant dans le budget, ce qui exige une formule que vous pouvez exécuter au dos d'une enveloppe et une vue claire des coûts que vous payez et ne payez pas.
**Source primaire :** [Article : "Distillation Scaling Laws", Busbridge et al., 2025](https://arxiv.org/abs/2502.08606), section 5 et équation 9
**Prérequis :** [Leçon 20](0020-choosing-student-size.md), [Enseignant](../GLOSSARY.md), [Distillation au niveau de la séquence](../GLOSSARY.md), [Données synthétiques](../GLOSSARY.md)

## Échauffement

1. ▢ La leçon 20 a listé deux conditions dans lesquelles la distillation est plus efficace que l'apprentissage supervisé. Énoncez-les toutes les deux.

<details markdown="1"><summary>Vérifier</summary>

Le calcul ou les tokens totaux de l'élève ne doivent pas dépasser un seuil dépendant de la taille de l'élève, et un enseignant doit déjà exister ou avoir des usages au-delà d'une seule distillation. Si l'une ou l'autre échoue, le résultat de l'article favorise l'entraînement direct de l'élève.

</details>

2. ▢ La leçon 8 a entraîné un élève sur les sorties décodées de l'enseignant, et la leçon 9 l'a comparé à la correspondance des distributions. Lequel des deux a besoin des logits de l'enseignant, et lequel n'a besoin que de son texte ?

<details markdown="1"><summary>Vérifier</summary>

La distillation (de logits) [au niveau du token](../GLOSSARY.md) a besoin de la distribution par position de l'enseignant. La [distillation au niveau de la séquence](../GLOSSARY.md) n'a besoin que du texte que l'enseignant a décodé, c'est pourquoi elle fonctionne à travers une API qui ne renvoie rien d'autre. Les deux placent le coût de l'enseignant à des endroits différents, ce que cette leçon chiffre.

</details>

3. ▢ La leçon 12 a dit que le volume ne répare pas les mauvais exemples. Si vous doubliez un jeu généré sans le filtrer, que vous attendriez-vous à voir arriver à la part de mauvais exemples ?

<details markdown="1"><summary>Vérifier</summary>

Elle resterait à peu près la même. Doubler un jeu à taux de défauts fixe double les défauts en même temps que les bons exemples. Plus de données n'aident qu'après que le filtrage de la leçon 12 a fixé la qualité, c'est pourquoi cette leçon compte les tokens qui survivent au filtre.

</details>

## À savoir

### Deux coûts, deux formules

Le coût d'entraînement d'un transformer dense est couramment approché par 6 FLOPs par paramètre et par token : environ 2 pour la passe avant et 4 pour la passe arrière. Une passe avant seule coûte environ 2 par paramètre et par token. Ce sont des approximations. Elles ignorent le terme d'attention, qui croît avec la longueur de contexte, et elles comptent tous les paramètres de la même façon.

L'article le dit lui-même. Il écrit le coût supervisé comme environ 6ND, utilise l'approximation 2N de la passe avant comme raccourci habituel, puis refuse de l'utiliser pour ses propres résultats, pour deux raisons : utiliser les paramètres hors embeddings le biaise, et pour les petits modèles à longs contextes la contribution de l'attention est significative (section 5, sous l'équation 9). Il dérive à la place un coût par token corrigé. Pour une planification à l'ordre de grandeur, le raccourci convient. Pour un nombre que vous défendrez, énoncez-le comme une approximation et dites ce que vous avez omis.

Son coût de distillation (équation 9) est l'entraînement de l'élève plus les passes avant de l'enseignant, chacun n'étant facturé que s'il vous concerne. En raccourci :

```text
student training   ≈ 6 × N_student × D
teacher inference  ≈ 2 × N_teacher × D     (forward only, over the same D tokens)
```

Ici N est le nombre de paramètres et D le nombre de tokens sur lesquels l'élève s'entraîne. Le terme de l'enseignant utilise le même D parce que la distillation de logits exécute l'enseignant sur chaque token que voit l'élève. Diviser l'un par l'autre donne un rapport qui vaut d'être retenu :

```text
teacher cost / student cost  ≈  N_teacher / (3 × N_student)
```

Un enseignant trois fois plus grand que l'élève coûte à peu près autant à exécuter que l'élève à entraîner. Tout enseignant plus grand coûte plus que l'élève que vous construisez.

### Exemple détaillé : noter des tokens avec un enseignant

Un élève de 1B s'entraîne sur 100B tokens, avec des logits d'un enseignant qui note ces mêmes tokens.

| Grandeur | Calcul | FLOPs |
|---|---|---|
| Entraînement de l'élève | 6 × 1e9 × 1e11 | 6.0e20 |
| Notation par un enseignant de 7B | 2 × 7e9 × 1e11 | 1.4e21 |
| Notation par un enseignant de 70B | 2 × 70e9 × 1e11 | 1.4e22 |

L'enseignant de 7B coûte environ 2.3 fois l'entraînement propre de l'élève, et l'enseignant de 70B environ 23 fois. La référence supervisée pour le même élève sur les mêmes tokens coûte les 6.0e20 seuls. Le run avec 70B est le même élève entraîné avec environ 24 fois le calcul, donc pour que cela vaille la peine, la loss de l'élève doit être bien plus basse que celle de l'élève supervisé à calcul égal, et le seuil de la leçon 20 dit à quelle fréquence cela tient.

### Partager le coût de l'enseignant entre plusieurs élèves

Si l'enseignant note un jeu de données une fois et que ses logits sont stockés, plusieurs élèves peuvent s'entraîner à partir de la même passe. Avec quatre élèves de 1B sur ces 100B tokens et l'enseignant de 7B : un élève coûte 1.4e21 + 6.0e20 = 2.0e21, et quatre coûtent 1.4e21 + 4 × 6.0e20 = 3.8e21, soit 9.5e20 chacun. C'est le troisième cadre de l'article, dans lequel le coût de l'enseignant est réparti sur les élèves qu'il sert (son tableau 2). Il laisse de côté ce que coûte le stockage des logits, une facture que la leçon 7 a introduite et que l'article traite séparément.

### Exemple détaillé : du texte généré au lieu de logits

Pour la distillation au niveau de la séquence, l'enseignant est facturé pour générer, pas pour noter. Générer G tokens coûte environ 2 × N_teacher × G en FLOPs selon l'approximation de la passe avant, et l'élève s'entraîne ensuite sur ces G tokens à chaque époque. Cela étend la comptabilité de l'article et n'en vient pas, puisque l'article étudie les logits.

Un enseignant de 70B génère 1B tokens : 2 × 70e9 × 1e9 = 1.4e20. Un élève de 3B s'entraîne deux époques dessus : 6 × 3e9 × 1e9 × 2 = 3.6e19. La génération de l'enseignant vaut environ 3.9 fois l'entraînement de l'élève, et le jeu généré est réutilisable, donc un deuxième élève ne coûte rien à l'enseignant.

Une précaution sur la lecture des FLOPs comme un coût. Générer un token à la fois laisse un GPU loin d'une utilisation complète, donc le temps réel et l'argent pour la génération dépassent largement ce que les FLOPs impliquent. C'est une connaissance générale sur le décodage, pas un résultat d'une source d'ici, mesurez donc les tokens par seconde sur votre matériel avant de citer un budget.

### Ce que dit l'article sur la destination de l'argent

Quand le pré-entraînement de l'enseignant fait partie de la facture, le tableau 3 de l'article résume comment la meilleure répartition évolue avec l'échelle :

| Taille de l'élève | Calcul | Allocation optimale |
|---|---|---|
| Petit (jusqu'à environ 3B) | Petit (jusqu'à environ 1e21 FLOPs) | Surtout le pré-entraînement de l'enseignant |
| Petit (jusqu'à environ 3B) | Grand (environ 1e25 FLOPs et plus) | À parts égales entre l'entraînement de l'élève et l'inférence de l'enseignant, bien moins sur le pré-entraînement de l'enseignant |
| Grand (environ 10B et plus) | Petit | Surtout l'entraînement standard de l'élève |
| Grand (environ 10B et plus) | Grand | À parts égales entre l'entraînement de l'élève, l'inférence de l'enseignant et le pré-entraînement de l'enseignant |

Lisez ces lignes comme l'optimum de l'article pour sa loi, dans le scénario où le pré-entraînement de l'enseignant compte. Ce ne sont pas une recette pour un enseignant ouvert que vous avez déjà, où la colonne du pré-entraînement est nulle.

### Combien de données suffisent

La réponse honnête de l'article est que davantage de tokens ne sont ni gratuits ni illimités. Avec un enseignant fixe, l'avantage de la distillation sur l'apprentissage supervisé se réduit quand le budget de tokens grandit, et finalement l'apprentissage supervisé l'égale ou le dépasse (section 5.1). « Suffisant » est donc le point où un token supplémentaire est mieux dépensé sur le propre signal de l'élève, et ce point monte avec la taille de l'élève.

Minitron est un contraste utile. Dans le tableau 2 de Muralidharan et al., Minitron 8B a été entraîné sur 94B tokens, contre 3.8T pour Nemotron-3 8B, environ 40 fois moins. La comparaison a deux réserves. L'élève de Minitron part des poids de l'enseignant après élagage, alors que les élèves de l'article partent de zéro. Et le facteur 40 compare un modèle élagué et distillé à un modèle entraîné de zéro, pas à un run supervisé du même élève. Il montre donc de combien peu de données une bonne initialisation peut avoir besoin. Il ne montre pas de combien de données un élève de zéro a besoin.

Leur économie au niveau de la famille est aussi un choix de comptabilité. Ils rapportent un calcul 1.8 fois plus bas pour la famille 15B, 8B et 4B (section 4.1), calculé comme (4.4e17 + 2.5e17 / 40 + 1.2e17 / 40) contre 4.4e17 + 2.5e17 + 1.2e17, en FLOPs par pas d'entraînement. Tel qu'écrit, le total compte les pas d'entraînement propres à chaque modèle. Les phrases qui décrivent le calcul n'ajoutent pas de terme pour l'exécution de l'enseignant de 15B pendant le ré-entraînement des plus petits modèles. C'est le terme que cette leçon dit de compter.

## Pratique

1. ▢ Calculez : un élève de 1B s'entraîne sur 50B tokens avec une passe de logits stockés d'un enseignant de 8B. Donnez les FLOPs d'entraînement de l'élève, les FLOPs de notation de l'enseignant, et le rapport du second au premier.

<details markdown="1"><summary>Indice</summary>

Utilisez 6 × N × D pour l'élève et 2 × N × D pour l'enseignant, avec le même D dans les deux. Le rapport égale aussi N_teacher divisé par trois fois N_student.

</details>

<details markdown="1"><summary>Vérifier</summary>

Élève : 6 × 1e9 × 5e10 = 3.0e20. Enseignant : 2 × 8e9 × 5e10 = 8.0e20. Rapport : environ 2.7, ce qui correspond à 8 / (3 × 1) = 2.67. Ce sont deux chiffres d'ordre de grandeur issus des approximations 6N et 2N. Ils laissent de côté l'attention et le coût de stockage ou de déplacement des logits.

</details>

2. ▢ Un enseignant de 70B génère 1B tokens de réponses, et un élève de 3B s'entraîne dessus pendant deux époques. Lequel des deux coûte le plus de FLOPs, et dans quel rapport ?

<details markdown="1"><summary>Indice</summary>

La génération est une passe avant par token à 2 × N_teacher. L'entraînement est 6 × N_student par token et par époque.

</details>

<details markdown="1"><summary>Vérifier</summary>

Génération : 2 × 70e9 × 1e9 = 1.4e20. Entraînement : 6 × 3e9 × 1e9 × 2 = 3.6e19. La génération de l'enseignant coûte environ 3.9 fois l'entraînement de l'élève. Ajouter des époques n'augmente que le côté de l'élève, donc une troisième époque rend les deux presque égaux. Le texte généré peut aussi être réutilisé pour un autre élève sans coût supplémentaire pour l'enseignant.

</details>

3. ▢ Quatre élèves de 1B partagent une passe de notation d'un enseignant de 7B sur 100B tokens. Quel est la moyenne de FLOPs par élève, et pourquoi est-elle plus basse que pour un élève seul ?

<details markdown="1"><summary>Vérifier</summary>

Total : 1.4e21 + 4 × 6.0e20 = 3.8e21, donc 9.5e20 par élève, contre 2.0e21 pour un élève seul. La passe de l'enseignant est payée une fois et divisée entre quatre. Cela ignore le coût de stockage et de bande passante pour conserver les logits, qui peut être grand pour une distribution sur tout le vocabulaire à chaque token.

</details>

4. ▢ Quelle affirmation sur le chiffre de 94B tokens de Minitron est correcte ?

    - a) Il montre qu'un élève de zéro a besoin d'environ 94B tokens quand il est distillé à partir d'un enseignant de 15B.
    - b) Il montre qu'un élève élagué peut se rétablir avec bien moins de tokens qu'un entraînement de zéro.
    - c) Il montre que la distillation a besoin d'environ quarante fois moins de données que l'entraînement supervisé de cet élève.
    - d) Il montre que le coût d'inférence de l'enseignant de 15B était négligeable face à l'entraînement de l'élève.

<details markdown="1"><summary>Vérifier</summary>

b). L'élève de 8B a été élagué à partir du modèle de 15B, il est donc parti des poids de l'enseignant. a) et c) traitent une initialisation élaguée comme si c'était une distillation de zéro. Le facteur 40 compare à Nemotron-3 8B, un autre modèle entraîné de zéro. d) n'est pas montré : le calcul de coût de la famille tel qu'écrit n'inclut pas de terme de passe avant de l'enseignant, il ne dit donc rien de ce coût dans un sens ni dans l'autre.

</details>

5. ▢ Entrelacement avec l'étape 4 : vous prévoyez de générer 20B tokens de données d'instruction avec un enseignant hébergé par API et de distiller un élève de 3B. Nommez deux choses que la formule en FLOPs ne vous dit pas avant de vous engager, l'une sur le coût et l'une de la leçon 13.

<details markdown="1"><summary>Vérifier</summary>

Pour le coût, la génération est loin d'être limitée par les FLOPs, donc le prix de l'API ou les heures réelles sur votre matériel sont le vrai chiffre, et le rendement filtré, pas les 20B bruts, fixe le nombre de tokens sur lesquels vous vous entraînez. De la leçon 13, savoir si les conditions du fournisseur autorisent d'entraîner un modèle sur ses sorties, à quoi aucune estimation de calcul ne répond.

</details>

## Exercices en situation réelle

- [ ] Choisissez un enseignant et un élève que vous pourriez réellement utiliser. Notez les deux nombres de paramètres et un budget de tokens, puis calculez le 6ND de l'élève, le 2ND de l'enseignant et leur rapport.
- [ ] Ouvrez le tableau 2 et l'équation 9 de l'article et marquez lequel des deux termes d'enseignant s'applique à votre projet, et dans quelle ligne du tableau vous êtes.
- [ ] Demain : sans notes, dérivez le rapport N_teacher / (3 × N_student) à partir des deux formules, puis énoncez deux coûts qu'il laisse de côté.

## Pour aller plus loin

- [Dimensionner et mesurer](../reference/sizing-and-measuring.md)
- [Article : "Distillation Scaling Laws", Busbridge et al., 2025](https://arxiv.org/abs/2502.08606), équation 9 et tableaux 2 et 3
- [Article : "Compact Language Models via Pruning and Knowledge Distillation", Muralidharan et al., 2024](https://arxiv.org/abs/2407.14679), tableau 2 et section 4.1
- [Pré-entraînement](../../pretraining/) : le parcours sur la façon dont un budget de calcul d'entraînement est compté et ce qu'achète un budget de tokens
- [Ressources](../RESOURCES.md)

---

Ça ne passe pas ? Relisez la source primaire en haut de page, car cette leçon la condense et c'est dans la condensation que la compréhension s'échappe. Consultez le [glossaire](../GLOSSARY.md) pour tout terme qui vous a paru glissant.

Si c'est la leçon elle-même qui n'est pas claire plutôt que la matière, c'est un défaut : [ouvrez une issue](https://github.com/TokenCemetery/teach/issues).
