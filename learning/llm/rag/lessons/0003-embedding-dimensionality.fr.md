---
title: "3. Compromis de dimensionnalité des embeddings"
description: "Pourquoi un vecteur d'embedding plus grand n'est pas gratuit, et quand on peut sans risque le tronquer au lieu de choisir un modèle plus petit"
type: lesson
---

# Leçon 3. Compromis de dimensionnalité des embeddings

**Lien avec la mission :** C'est le point d'orgue de l'étape 2 : choisir un modèle d'embedding (leçon 2) n'est pas terminé tant que la taille de sa sortie n'a pas été pesée face à ce que le budget de stockage et de latence d'un corpus peut réellement se permettre.
**Source primaire :** [Article : "Matryoshka Representation Learning", Kusupati et al., 2022](https://arxiv.org/abs/2205.13147)
**Prérequis :** [Leçon 2](0002-embedding-models-and-similarity.md), [Chunk](../GLOSSARY.md)

## Échauffement

1. ▢ Pourquoi un bi-encoder calcule-t-il l'embedding d'une requête et d'un passage séparément plutôt que conjointement ?

<details markdown="1"><summary>Vérifier</summary>

Pour que chaque passage puisse être traité une seule fois, à l'avance, et stocké ; seule la requête demande un embedding au moment de la recherche, ce qui permet de la comparer à peu de frais à des vecteurs de passages précalculés. Un calcul conjoint (un cross-encoder) exige d'exécuter le modèle sur chaque paire, ce qui ne passe pas à l'échelle pour un grand corpus.

</details>

2. ▢ Pourquoi la similarité cosinus et le produit scalaire ne produisent-ils le même classement que lorsque les vecteurs sont normalisés à une longueur unité ?

<details markdown="1"><summary>Vérifier</summary>

Le produit scalaire est la similarité cosinus multipliée par les normes des deux vecteurs. Quand les deux sont fixées à la longueur unité, ce facteur d'échelle est identique pour chaque paire, donc les deux métriques classent de façon identique ; quand les normes varient, le produit scalaire récompense implicitement les vecteurs plus grands.

</details>

## À savoir

### La dimensionnalité est un coût, pas un réglage de qualité gratuit

Un embedding de plus haute dimension peut encoder plus de nuances, mais chacune de ses dimensions coûte quelque chose de concret : le stockage croît linéairement avec la dimension (un vecteur de 1536 dimensions en float32 occupe `1536 × 4 bytes = 6,144 bytes`, soit environ 6 Ko, contre `256 × 4 = 1,024 bytes` pour un vecteur de 256 dimensions, environ 1 Ko, six fois moins), et la mémoire de l'index comme le calcul de distance par candidat évoluent de la même façon. Sur un million de chunks, cet écart représente 6 Go contre 1 Go rien que pour les vecteurs eux-mêmes, avant le surcoût propre à un index. Un embedding plus grand n'est pas automatiquement le meilleur choix ; c'est un choix qu'il faut justifier au regard de ce qu'il coûte, comme un cache KV plus grand ou une taille de batch plus grande devaient être justifiés au regard du budget réel d'une charge de travail dans d'autres contextes de serving.

### Matryoshka Representation Learning : la troncature comme fonctionnalité conçue, pas comme bricolage

Ordinairement, tronquer un vecteur d'embedding à moins de dimensions n'est pas sûr : rien dans la façon dont un modèle d'embedding standard a été entraîné n'ordonne ses dimensions par importance, donc ramener un vecteur normal de 768 dimensions à 256 peut écarter de l'information de façon imprévisible et dégrader la qualité bien plus que le seul nombre de dimensions ne le laisserait penser. **Matryoshka Representation Learning (MRL)** entraîne un modèle différemment : sa fonction de perte optimise explicitement les préfixes du vecteur complet (les 256 premières dimensions d'un embedding de 1536 dimensions, par exemple) pour qu'ils soient eux-mêmes des embeddings utilisables et significatifs, emboîtés dans le vecteur complet comme les petites poupées à l'intérieur d'une poupée russe. Cela signifie qu'un modèle entraîné avec MRL peut être tronqué après coup, avec un coût de qualité borné et prévisible, ce qui permet d'arbitrer la dimensionnalité contre le stockage et la latence sans réentraîner le modèle ni recalculer les embeddings de tout le corpus à une autre taille. Cela ne vaut que pour les modèles réellement entraînés ainsi ; tronquer un modèle qui ne l'est pas ramène au cas risqué et imprévisible.

![Un unique vecteur de 1536 dimensions dessiné comme une seule barre, avec des traits pointillés qui marquent où se terminent ses 256 premières dimensions et ses 768 premières dimensions. Trois plages entre crochets au-dessus de la barre, toutes commençant à la dimension 0, montrent que s'arrêter à 256, à 768, ou lire les 1536 dimensions complètes donne chaque fois un embedding utilisable et significatif, parce que Matryoshka Representation Learning a entraîné chaque préfixe du vecteur à fonctionner seul, contrairement à un modèle d'embedding standard où seul le vecteur complet a un sens.](images/matryoshka-prefix-embeddings.svg)

### Décider de la bonne dimensionnalité, c'est mesurer, pas supposer

La bonne dimensionnalité pour un corpus donné n'est pas un nombre à deviner ; c'est un nombre à mesurer. Avec un modèle MRL (ou en comparant plusieurs tailles de modèles candidats), la qualité de la récupération, le plus directement le recall@k sur un jeu de requêtes étiqueté ou synthétique (le sujet de l'étape 6), peut être mesurée à chaque dimensionnalité candidate sur le corpus réel et le type de requêtes en question. La dimensionnalité qui mérite d'être livrée est la plus petite qui atteint encore le seuil de qualité qu'exige la charge de travail, pas la plus grande disponible, et pas une valeur par défaut choisie sans vérifier ce qu'elle coûte face à ce qu'elle apporte.

## Pratique

1. ▢ Un corpus compte 2 millions de chunks. Calculez la différence de stockage, en gigaoctets, entre un embedding à 1536 dimensions et un embedding à 256 dimensions, tous deux en float32.

<details markdown="1"><summary>Indice</summary>

Le nombre d'octets par vecteur vaut `dimensions × 4 bytes`. Multipliez par 2 millions, puis convertissez en gigaoctets.

</details>

<details markdown="1"><summary>Vérifier</summary>

1536 dimensions : `1536 × 4 = 6,144 bytes` par vecteur, `× 2,000,000 ≈ 12.3 GB`. 256 dimensions : `256 × 4 = 1,024 bytes` par vecteur, `× 2,000,000 ≈ 2.0 GB`. L'écart est d'environ 10,3 Go, soit un stockage environ six fois moindre à 256 dimensions.

</details>

2. ▢ Une équipe tronque à 256 dimensions les vecteurs d'un modèle d'embedding standard (non MRL) de 768 dimensions pour économiser du stockage, et la qualité de la récupération s'effondre bien plus que la seule réduction de dimensions ne le laisserait penser. Quelle est l'erreur probable ?

<details markdown="1"><summary>Vérifier</summary>

Le modèle n'a pas été entraîné avec Matryoshka Representation Learning, donc rien n'a ordonné ses dimensions par importance ni fait d'un préfixe du vecteur un embedding significatif à lui seul. Le tronquer écarte de l'information de façon imprévisible, au lieu de la façon bornée et conçue dont la troncature d'un modèle entraîné avec MRL le ferait.

</details>

3. ▢ Qu'est-ce qu'un modèle d'embedding entraîné avec MRL permet à une équipe de faire qu'un modèle d'embedding standard ne permet pas ?

<details markdown="1"><summary>Vérifier</summary>

Tronquer après coup le vecteur d'embedding complet à une dimensionnalité plus petite, avec un coût de qualité borné et prévisible, en arbitrant le stockage et la latence contre la qualité sans réentraîner le modèle ni recalculer les embeddings du corpus à une autre taille fixe.

</details>

4. ▢ Comment une équipe doit-elle décider de la dimensionnalité d'embedding à utiliser réellement pour son corpus, plutôt que de retenir par défaut la taille de sortie complète d'un modèle ?

<details markdown="1"><summary>Vérifier</summary>

Mesurer la qualité de la récupération, le plus directement quelque chose comme le recall@k sur un jeu de requêtes étiqueté ou synthétique représentatif du corpus réel et du type de requêtes, à plusieurs dimensionnalités candidates, et choisir la plus petite qui atteint encore le seuil de qualité qu'exige la charge de travail, plutôt que de supposer que la plus grande dimensionnalité disponible est nécessaire ou qu'une plus petite est automatiquement « suffisante ».

</details>

5. ▢ Laquelle de ces affirmations est vraie à propos de la dimensionnalité des embeddings ?

    - a) Une plus grande dimensionnalité d'embedding améliore toujours assez la qualité de la récupération pour justifier son coût
    - b) Tronquer les vecteurs de n'importe quel modèle d'embedding est tout aussi sûr, quelle que soit la façon dont le modèle a été entraîné
    - c) La dimensionnalité est un coût (stockage, mémoire de l'index, calcul par candidat) qu'il faut dimensionner à la plus petite valeur qui atteint un seuil de qualité mesuré
    - d) Les modèles entraînés avec MRL ne peuvent pas être tronqués ; ils n'offrent qu'une seule taille de sortie fixe

<details markdown="1"><summary>Vérifier</summary>

**c)** Les coûts de stockage et de calcul croissent avec la dimensionnalité, donc la bonne taille est la plus petite valeur dont un seuil de qualité mesuré a réellement besoin. (a) est fausse : le coût doit être pesé face à un bénéfice mesuré, pas supposé. (b) est fausse : tronquer un modèle non MRL est imprévisible et peut détruire bien plus de signal que le nombre de dimensions ne l'implique. (d) est fausse : cette troncature flexible est exactement ce que l'entraînement MRL est conçu pour permettre.

</details>

## Exercices en situation réelle

- [ ] Vérifiez si le modèle d'embedding que vous utilisez (ou prévoyez d'utiliser) a été entraîné avec Matryoshka Representation Learning, et si oui, vers quelles dimensionnalités il accepte d'être tronqué.
- [ ] Calculez le coût de stockage, en octets par vecteur et pour la taille réelle de votre corpus, à la dimensionnalité complète de votre modèle et à une taille candidate plus petite.
- [ ] Demain : si vous disposez d'un jeu de requêtes étiqueté ou synthétique, mesurez le recall à deux dimensionnalités d'embedding différentes et comparez l'écart de qualité à l'écart de stockage.

## Pour aller plus loin

- [Article : "Matryoshka Representation Learning", Kusupati et al., 2022](https://arxiv.org/abs/2205.13147)
- [Article : "Sentence-BERT: Sentence Embeddings using Siamese BERT-Networks", Reimers and Gurevych, 2019](https://arxiv.org/abs/1908.10084)
- [Ressources](../RESOURCES.md)

---

Ça ne passe pas ? Relisez la source primaire en haut de page, car cette leçon la condense et c'est dans la condensation que la compréhension s'échappe. Consultez le [glossaire](../GLOSSARY.md) pour tout terme qui vous a paru glissant.

Si c'est la leçon elle-même qui n'est pas claire plutôt que la matière, c'est un défaut : [ouvrez une issue](https://github.com/TokenCemetery/teach/issues).
