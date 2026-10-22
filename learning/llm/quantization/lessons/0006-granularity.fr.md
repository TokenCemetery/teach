---
title: "6. La granularité"
description: "Scales par tenseur, par canal et par groupe, et ce que chacun coûte en bits stockés"
type: lesson
---

# Leçon 6. La granularité

**Lien avec la mission :** Prévoir l'erreur d'un tenseur quantifié, c'est aussi savoir combien de valeurs partagent chaque scale, parce qu'un scale est fixé par la plus grande valeur de son groupe et que chaque scale supplémentaire coûte des bits stockés.
**Source primaire :** [Article : "A White Paper on Neural Network Quantization", Nagel et al., 2021](https://arxiv.org/abs/2106.08295), sections 2.2.3 et 2.4.2
**Prérequis :** [Leçon 5](0005-choosing-the-range.md), [Granularité](../GLOSSARY.md), [Taille de groupe](../GLOSSARY.md), [Bits effectifs par poids](../GLOSSARY.md)

## Échauffement

1. ▢ Avec un choix de plage min-max, qu'est-ce qui décide du scale d'un quantificateur, et que lui fait un outlier ?

<details markdown="1"><summary>Vérifier</summary>

La plage, fixée par les plus grande et plus petite valeurs, divisée par le nombre de pas. Un outlier élargit la plage, donc le scale grandit et le pas devient plus grossier pour toutes les autres valeurs, ce qui peut en arrondir la plupart à zéro (leçon 5).

</details>

2. ▢ Un schéma en 4 bits stocke un scale de 16 bits par groupe de 32 poids. Quels sont ses bits effectifs par poids ?

<details markdown="1"><summary>Vérifier</summary>

4.5. Le scale ajoute 16 / 32 = 0.5 bit par poids aux 4 bits de chaque valeur (leçon 1).

</details>

3. ▢ Pourquoi une grille symétrique n'a-t-elle besoin que d'un scale, et quel est le coût de l'abandon du zero-point ?

<details markdown="1"><summary>Vérifier</summary>

La quantification symétrique fixe le zero-point à zéro, donc il n'y a rien d'autre à stocker. Le coût est que la grille est centrée sur zéro, donc un tenseur d'un seul côté gaspille les niveaux du côté vide (leçon 4).

</details>

## À savoir

### Ce qui partage un scale

La **granularité** est le nombre de valeurs qui partagent un scale et un zero-point. Un petit ensemble qui partage un scale signifie une petite plage, donc un outlier ne ruine que l'ensemble dans lequel il se trouve. Le coût est que chaque ensemble a besoin de son propre scale stocké.

```text
W: output channels (rows) x input features (columns)

per-tensor    one scale for the whole matrix
per-channel   one scale per row (per output channel of a weight matrix)
per-group     one scale per `group size` consecutive values within a row, such as 64 or 128
per-token     one scale per row of an activation matrix X (tokens x features)
```

Nagel et al. notent que la quantification par tenseur est la norme parce que tous les accélérateurs en virgule fixe la prennent en charge, et que la quantification des poids par canal aide le plus quand la distribution des poids varie beaucoup d'un canal à l'autre. Ils décrivent aussi l'application d'un quantificateur par groupe de poids ou d'activations, et disent que des groupes plus fins améliorent en général la précision au prix d'un surcoût supplémentaire.

### Pourquoi le par-canal fonctionne pour les poids et pas pour les activations

Une couche linéaire calcule chaque sortie comme une somme sur les features d'entrée. Avec les valeurs quantifiées écrites comme scale fois entier, les scales ne peuvent sortir de la somme que s'ils sont constants sur elle :

```text
y[i] = sum over k of (s_w[i] * W_int[i,k]) * (s_x * x_int[k])
     = s_w[i] * s_x * (sum over k of W_int[i,k] * x_int[k])
```

La parenthèse est un produit scalaire d'entiers pur, ce que le matériel accélère, et les deux scales multiplient le résultat une seule fois à la fin. Un scale de poids par canal de sortie `s_w[i]` est constant sur la somme, parce que `i` désigne la sortie et que `k` est sommé. Nagel et al. concluent que la quantification des poids par canal peut s'appliquer avec un scale distinct par canal, sans remettre l'accumulateur à l'échelle.

Un scale d'activation par canal d'entrée serait `s_x[k]`, qui change avec l'indice sommé. Il ne peut pas sortir de la somme, et Nagel et al. disent qu'il « exigerait donc de remettre l'accumulateur à l'échelle pour chaque canal d'entrée » (« would therefore require rescaling the accumulator for each input channel »). La quantification des activations par canal est bien plus difficile à implémenter pour cette raison. Un scale d'activation par token, un par ligne de `X`, est constant sur la somme pour un token donné et ne coûte rien : [Dettmers et al.](https://arxiv.org/abs/2208.07339) l'utilisent exactement ainsi dans leur quantification vector-wise, une constante par ligne des activations et une par colonne des poids, et défont les deux avec le produit extérieur des constantes. La leçon 7 montre pourquoi cela ne suffit pas pour les LLM : les outliers se trouvent dans les dimensions de features, l'axe qu'un scale par token ne sépare pas.

La quantification par groupe pose le même problème pour l'accumulateur entier, puisque le scale change à l'intérieur de la somme. La limite de l'accumulateur dans l'article est la raison pour laquelle Nagel et al. laissent de côté les scales de groupe. Dans les schémas weight-only, les poids sont déquantifiés en 16 bits à l'intérieur du kernel et multipliés en 16 bits (voir [quantification weight-only](../GLOSSARY.md)), donc aucun accumulateur entier ne porte de scales mélangés et un scale de groupe peut varier librement.

### Ce que coûtent les scales

Chaque groupe ajoute son scale, et tout zero-point, au checkpoint. Les **bits effectifs par poids** valent la largeur en bits de la valeur plus les métadonnées réparties sur le groupe :

```text
effective bits = b + (scale bits + zero point bits) / group size
```

| Taille de groupe | Surcoût avec un scale de 16 bits | Bits effectifs pour des poids en 4 bits |
|---|---|---|
| 1024 | 0.0156 | 4.0156 |
| 256 | 0.0625 | 4.0625 |
| 128 | 0.125 | 4.125 |
| 64 | 0.25 | 4.25 |
| 32 | 0.5 | 4.5 |

Le par-canal est simplement un groupe dont la taille est la longueur de la ligne, et le par-tenseur est un groupe de tous les poids : les deux ne coûtent presque rien. Le chiffre de la leçon 1 pour le groupe 32 est la dernière ligne.

### Ce qu'achètent les petits groupes

L'expérience de la Pratique quantifie en 4 bits une matrice de poids synthétique, avec des lignes d'échelles différentes et des queues lourdes. L'erreur baisse régulièrement à mesure que les groupes rétrécissent, et le par-tenseur est de loin le pire. Un groupe de 64 n'a que 64 chances de contenir un outlier, et l'outlier n'affecte que ces 64 valeurs.

La plus grande étude empirique à ce sujet est celle de [Dettmers et Zettlemoyer](https://arxiv.org/abs/2212.09720) : plus de 35,000 expériences zero-shot avec 3 à 8 bits sur des LLM de 19M à 176B paramètres. Ils trouvent qu'il est difficile d'améliorer tout court l'échange entre la taille du modèle en bits et la précision, avec seulement deux leviers qui aident : une petite taille de bloc (leur terme pour la taille de groupe) et le type de données. Pour des modèles Pythia en 4 bits, passer d'une taille de bloc de 1024 à 64 ajoute 0.24 bit par paramètre et améliore la précision zero-shot presque autant que passer de 4 à 5 bits. Une constante de 16 bits par bloc coûte 16 / 64 - 16 / 1024 = 0.23 bit, proche du chiffre de l'article. Les petits groupes sont les bits bon marché.

## Pratique

1. ▢ Un schéma en 4 bits stocke un scale de 16 bits et un zero-point de 4 bits par groupe de 64 poids. Quels sont ses bits effectifs par poids ?

<details markdown="1"><summary>Vérifier</summary>

4 + (16 + 4) / 64 = 4.3125, soit environ 4.31. Le zero-point ajoute 4 / 64 = 0.0625 en plus des 0.25 du scale. Un schéma symétrique abandonnerait ces 0.0625 et tomberait sur 4.25.

</details>

2. ▢ Qu'est-ce qui rend un scale de poids par canal de sortie compatible avec une multiplication de matrices entière alors qu'un scale d'activation par canal d'entrée ne l'est pas ?

    - a) Le scale de poids tient sur huit bits seulement
    - b) Le scale de poids exige un terme de décalage séparé
    - c) Le scale de poids est constant sur la sommation
    - d) Le scale de poids change de valeur d'un canal de sortie à l'autre

<details markdown="1"><summary>Vérifier</summary>

**c)** Le scale de la sortie `i` multiplie toute la somme sur `k`, donc il sort de la somme et s'applique une seule fois après l'accumulation entière. Un scale d'activation indexé par canal d'entrée change à l'intérieur de la somme, donc l'accumulateur devrait être remis à l'échelle à chaque canal d'entrée. (a) concerne le stockage et ne décide pas de l'endroit où un scale peut s'appliquer. (b) confond un scale avec un zero-point, et des poids symétriques n'en ont pas besoin. (d) est vrai mais c'est la raison pour laquelle il y a beaucoup de scales, pas celle pour laquelle on peut les factoriser.

</details>

3. ▢ Prédisez, puis exécutez. Avant d'exécuter, classez le par-tenseur, le par-canal et les tailles de groupe par erreur, du pire au meilleur, et dites si l'erreur baisse régulièrement. Calculez ensuite les bits effectifs pour le groupe 32.

    ```python
    import numpy as np

    rng = np.random.default_rng(0)
    rows, cols, b = 256, 1024, 4
    qmax = 2 ** (b - 1) - 1
    row_scale = rng.lognormal(0.0, 0.7, size=(rows, 1)) * 0.02
    W = rng.standard_t(df=4, size=(rows, cols)) * row_scale


    def quantize(W, group):
        """Symmetric absmax, one scale per `group` consecutive values in a row.
        group=None means one scale for the whole tensor."""
        G = W.reshape(1, -1) if group is None else W.reshape(-1, group)
        s = np.abs(G).max(axis=1, keepdims=True) / qmax
        Q = s * np.clip(np.round(G / s), -qmax, qmax)
        return Q.reshape(W.shape)


    print("granularity    rel. error   effective bits (16-bit scales)")
    for name, group in [("per-tensor", None), ("per-channel", cols), ("group 256", 256),
                        ("group 128", 128), ("group 64", 64), ("group 32", 32)]:
        err = np.mean((quantize(W, group) - W) ** 2) / np.mean(W ** 2)
        n_scales = 1 if group is None else W.size // group
        print(f"{name:13s}  {err:.4f}       {b + 16 * n_scales / W.size:.3f}")
    ```

<details markdown="1"><summary>Indice</summary>

Chaque cran de baisse de la taille de groupe signifie plus de scales, et chaque scale est fixé par un ensemble de valeurs plus petit. Demandez-vous ensuite ce que fait un scale par tenseur à une matrice dont les lignes diffèrent en taille.

</details>

<details markdown="1"><summary>Vérifier</summary>

```text
granularity    rel. error   effective bits (16-bit scales)
per-tensor     0.7047       4.000
per-channel    0.1291       4.016
group 256      0.0599       4.062
group 128      0.0395       4.125
group 64       0.0267       4.250
group 32       0.0179       4.500
```

L'erreur baisse à chaque cran : le par-tenseur laisse une erreur d'environ 70 pour cent de l'énergie propre du signal, le par-canal en retire l'essentiel en donnant à chaque ligne son propre scale, et chaque division par deux du groupe réduit l'erreur d'environ un tiers. Le groupe 32 coûte 4.5 bits effectifs. Les données sont synthétiques, donc lisez l'ordre et les rapports approximatifs, pas les chiffres absolus.

</details>

4. ▢ Passer d'une taille de groupe de 1024 à 64 ajoute combien de bits par poids avec un scale de 16 bits ? Comparez avec le coût du passage des poids de 4 à 5 bits, et dites ce que Dettmers et Zettlemoyer ont trouvé sur les bénéfices.

<details markdown="1"><summary>Vérifier</summary>

16 / 64 - 16 / 1024 = 0.234 bit, contre 1 bit entier pour des poids en 5 bits. Dans l'article, la taille de bloc plus petite a amélioré la précision zero-shot des modèles Pythia en 4 bits presque autant que le bit supplémentaire l'aurait fait. Réduire le groupe est donc une manière bien moins chère d'acheter de la précision que d'ajouter un bit à chaque poids. Le résultat phare de l'article est que 4 bits sont presque universellement optimaux pour le total de bits du modèle et la précision zero-shot.

</details>

5. ▢ Une équipe quantifie les activations en 8 bits avec un scale par token et perd quand même en précision, parce qu'une dimension de feature est énorme à chaque token. Pourquoi le scale par token n'aide-t-il pas, et quel axe séparerait l'outlier ?

<details markdown="1"><summary>Vérifier</summary>

Le scale de chaque token est fixé par la plus grande valeur de ce token, et la dimension de feature énorme est la plus grande à presque chaque token, donc le scale de chaque ligne est gonflé de la même façon. Dettmers et al. font cette remarque : la quantification row-wise et vector-wise met à l'échelle la dimension de la séquence, et les outliers se trouvent dans la dimension des features, donc les deux échouent à les isoler. Seul un scale par dimension de feature séparerait l'outlier, et c'est le scale d'activation par canal d'entrée de cette leçon, qu'une multiplication de matrices entière ne peut pas appliquer à bon compte.

</details>

## Exercices en situation réelle

- [ ] Dans l'expérience, changez `0.7` dans `rng.lognormal(0.0, 0.7, ...)` en `0.0`, pour que chaque ligne ait le même scale, et relancez. Notez ce qui reste de l'avantage du par-canal sur le par-tenseur, et expliquez-le.
- [ ] Ouvrez la fiche du modèle ou la config d'un checkpoint GPTQ ou AWQ en 4 bits sur le Hugging Face Hub, trouvez sa taille de groupe, et calculez ses bits effectifs par poids et la taille de son checkpoint pour le nombre de paramètres du modèle.
- [ ] Demain : sans notes, reconstruisez le tableau des tailles de groupe contre les bits effectifs pour un scale de 16 bits et pour un scale de 8 bits, et dites en une phrase pourquoi les scales de poids par canal conviennent à une multiplication de matrices entière et pas les scales d'activation par canal.

## Pour aller plus loin

- [La correspondance de quantification](../reference/quantization-mapping.md)
- [Article : "A White Paper on Neural Network Quantization", Nagel et al., 2021](https://arxiv.org/abs/2106.08295)
- [Article : "The case for 4-bit precision: k-bit Inference Scaling Laws", Dettmers et Zettlemoyer, 2022](https://arxiv.org/abs/2212.09720)
- [Ressources](../RESOURCES.md)

---

Ça ne passe pas ? Relisez la source primaire en haut de page, car cette leçon la condense et c'est dans la condensation que la compréhension s'échappe. Consultez le [glossaire](../GLOSSARY.md) pour tout terme qui vous a paru glissant.

Si c'est la leçon elle-même qui n'est pas claire plutôt que la matière, c'est un défaut : [ouvrez une issue](https://github.com/TokenCemetery/teach/issues).
