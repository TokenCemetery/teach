---
title: "5. Choisir la plage"
description: "Pourquoi écrêter la plage échange un peu d'erreur d'écrêtage contre beaucoup moins d'erreur d'arrondi"
type: lesson
---

# Leçon 5. Choisir la plage

**Lien avec la mission :** Prévoir d'où vient une erreur de quantification, c'est savoir laquelle de ses deux parties une plage d'écrêtage donnée rend grande, et la plage est le choix qui fait passer l'une dans l'autre.
**Source primaire :** [Article : "A White Paper on Neural Network Quantization", Nagel et al., 2021](https://arxiv.org/abs/2106.08295), section 3.1
**Prérequis :** [Leçon 4](0004-quantize-and-dequantize.md), [Plage d'écrêtage](../GLOSSARY.md), [Erreur d'écrêtage](../GLOSSARY.md), [Erreur d'arrondi](../GLOSSARY.md)

## Échauffement

1. ▢ Un quantificateur affine sur 4 bits couvre la plage de -1 à 3. Quels sont son pas et sa plus grande erreur d'arrondi ?

<details markdown="1"><summary>Vérifier</summary>

Le pas est `s = 4 / 15 = 0.267` et la plus grande erreur d'arrondi est `s/2 = 0.133`. La plage est divisée en 2^4 - 1 = 15 pas, et une valeur dans la plage se déplace d'au plus un demi-pas.

</details>

2. ▢ Une valeur se trouve en dehors des limites de la grille d'un quantificateur. Son erreur est-elle bornée par `s/2` ? Comment s'appelle cette erreur ?

<details markdown="1"><summary>Vérifier</summary>

Non. La valeur est ramenée à la limite de grille la plus proche, et la distance qu'elle parcourt est l'**erreur d'écrêtage**, qui n'a pas de borne `s/2` et croît avec la distance à laquelle la valeur se trouve hors de la plage.

</details>

3. ▢ Pourquoi les quantificateurs associent-ils d'ordinaire des poids symétriques à des activations asymétriques ?

<details markdown="1"><summary>Vérifier</summary>

Des poids asymétriques multipliés par des activations asymétriques produisent un terme qui dépend des données d'entrée, ce qui coûte de la latence et de la puissance à l'exécution (Nagel et al., section 2.4.1). Une grille de poids symétrique supprime ce terme, donc seules les activations gardent le zero-point supplémentaire.

</details>

## À savoir

### Deux erreurs qui tirent en sens opposés

La **plage d'écrêtage** est l'intervalle de valeurs réelles que la grille d'entiers couvre, de `q_min` à `q_max`. Nagel et al. nomment tout l'échange en une phrase de la section 2.2 : élargir la plage réduit l'erreur d'écrêtage, mais exige un plus grand scale, et l'erreur d'arrondi, qui se situe entre -s/2 et s/2, croît avec lui.

| Plage | Erreur d'écrêtage | Erreur d'arrondi | Ce qui tourne mal |
|---|---|---|---|
| Trop étroite | Grande : les outliers sont ramenés à la limite | Petite | Les plus grandes valeurs sont remplacées par le bord de la plage |
| Trop large | Aucune | Grande : le pas est grand | Les valeurs typiques tombent dans quelques niveaux ou sont arrondies à zéro |

La section 3.1 de l'article appelle cela le compromis clé du choix de la plage, et dit que chaque méthode donne un équilibre différent entre les deux erreurs. Les poids sont connus à l'avance, donc leur plage n'a d'ordinaire pas besoin de données. La plage d'une activation dépend de l'entrée, donc Nagel et al. disent qu'elle demande d'ordinaire quelques batchs de données de calibration, ce qui est le rôle du [calibration set](../GLOSSARY.md).

### Les méthodes

**Min-max.** Prendre la plus petite et la plus grande valeur comme `q_min` et `q_max`. Il n'y a aucune erreur d'écrêtage, et Nagel et al. avertissent que la méthode est sensible aux outliers, parce qu'un outlier fort impose un grand pas et donc une erreur d'arrondi excessive. C'est ce qu'a utilisé la leçon 4.

**Erreur quadratique moyenne.** Chercher les `q_min` et `q_max` qui minimisent l'erreur quadratique moyenne entre le tenseur d'origine et le tenseur quantifié. L'article cite la recherche sur grille, la méthode de la section dorée et les approximations en forme close comme moyens de la résoudre, et dit que les variantes de la littérature se ressemblent toutes beaucoup. C'est la méthode à choisir quand les outliers gonflent la plage min-max.

**Percentile.** Fixer la plage à un percentile élevé des valeurs absolues, comme le 99.9e, de sorte qu'une fraction fixe des valeurs soit écrêtée. C'est une heuristique simple, pas l'une des méthodes de la section 3.1, et l'expérience ci-dessous l'utilise pour que vous voyiez ce que coûte et ce qu'achète une fraction fixe.

La section 3.1 en liste deux autres pour des cas particuliers : minimiser l'entropie croisée pour les logits de la dernière couche, où l'ordre des plus grandes valeurs compte plus que les nombreuses petites, et une plage fondée sur la batch normalization pour les activations. Ce parcours quantifie des LLM sans batch normalization, donc il utilise les trois premières.

Nagel et al. comparent les deux premières sur des classifieurs ImageNet dans leur tableau 1, avec des poids quantifiés par tenseur et des activations laissées en virgule flottante. Pour ResNet18 en 8 bits, min-max et MSE sont à peu près à égalité : 69.57 contre 69.45 d'accuracy top-1. En 4 bits, min-max tombe à 0.12 et MSE garde 18.82. Ce sont des modèles de vision, donc lisez la forme du résultat, pas les chiffres : avec peu de niveaux, le choix de la plage décide si le modèle fonctionne tout court.

### Ce que montre l'expérience

L'expérience de la Pratique quantifie en 4 bits un tenseur à queues lourdes. Sa plus grande valeur est 1.506 et son écart type est 0.034, soit un rapport d'environ 44. Avec la plage min-max, le pas est `1.506 / 7 = 0.215`, la moitié fait 0.108, soit plus de trois écarts types, donc presque toutes les valeurs sont arrondies à zéro. Écrêter les 0.35 % de valeurs que la recherche MSE écrête divise l'erreur par environ six. La grille est dépensée sur une plage que presque aucune valeur ne visite.

### Pourquoi ce n'est pas toute la réponse pour les LLM

La MSE compte à égalité l'erreur quadratique de chaque valeur. Nagel et al. font la même remarque à propos des logits : la MSE peut ne pas convenir à des valeurs d'importance inégale, parce qu'elle pèse toutes les valeurs de la même façon. Dans un LLM, les quelques plus grandes valeurs peuvent être les importantes. [Dettmers et al.](https://arxiv.org/abs/2208.07339) rapportent que mettre à zéro les dimensions de features outlier dégradait la perplexity de validation de 600 à 1000 pour cent, alors qu'elles ne forment qu'environ 0.1 pour cent des features. Une plage qui les écrête a un effet minuscule sur la MSE du tenseur et peut avoir un effet important sur le modèle. La leçon 7 explique d'où viennent ces valeurs, et la leçon 8 donne les parades qui ne les écrêtent pas.

## Pratique

1. ▢ Un quantificateur symétrique signé sur 4 bits avec une grille de -7 à 7 a une plage min-max de 1.506 sur un tenseur d'écart type 0.034. Que vaut `s`, et quelles valeurs sont arrondies à zéro ?

<details markdown="1"><summary>Vérifier</summary>

`s = 1.506 / 7 = 0.215`. Toute valeur de valeur absolue inférieure à `s/2 = 0.108` est arrondie à l'entier 0, soit plus de trois écarts types. Pour un tenseur en cloche, c'est presque toute valeur, donc un seul maximum lointain a effacé le tenseur.

</details>

2. ▢ Quelle affirmation décrit l'élargissement de la plage d'écrêtage ?

    - a) L'erreur d'écrêtage et l'erreur d'arrondi baissent toutes deux
    - b) L'erreur d'écrêtage et l'erreur d'arrondi montent toutes deux
    - c) L'erreur d'écrêtage baisse tandis que l'erreur d'arrondi monte
    - d) L'erreur d'écrêtage monte tandis que l'erreur d'arrondi baisse

<details markdown="1"><summary>Vérifier</summary>

**c)** Une plage plus large ramène moins de valeurs à la limite, donc l'erreur d'écrêtage baisse, mais le même nombre de niveaux couvre désormais plus de distance, donc le pas et l'erreur d'arrondi croissent. (a) rendrait le choix de la plage trivial, puisqu'on élargirait toujours. (b) se trompe sur les deux, puisque élargir ne peut pas augmenter l'erreur d'écrêtage. (d) décrit le rétrécissement de la plage, pas son élargissement.

</details>

3. ▢ Prédisez, puis exécutez. Ce code quantifie 100,000 valeurs à queues lourdes en 4 bits sous quatre plages. Avant d'exécuter, prédisez quelle plage a l'erreur quadratique moyenne la plus basse, et si min-max arrondit à zéro plus ou moins de la moitié de toutes les valeurs.

    ```python
    import numpy as np

    rng = np.random.default_rng(0)
    x = rng.standard_t(df=3, size=100_000) * 0.02   # heavy-tailed
    qmax = 7                                        # 4-bit signed symmetric grid: -7..7 times the scale


    def quantize(x, c):
        s = c / qmax
        return s * np.clip(np.round(x / s), -qmax, qmax)


    def mse(x, c):
        return np.mean((quantize(x, c) - x) ** 2)


    grid = np.linspace(0.01, np.abs(x).max(), 400)
    ranges = {
        "min-max": np.abs(x).max(),
        "p99.9": np.percentile(np.abs(x), 99.9),
        "p99": np.percentile(np.abs(x), 99),
        "MSE search": grid[np.argmin([mse(x, c) for c in grid])],
    }
    print("max |x| =", round(np.abs(x).max(), 3), " std =", round(x.std(), 3))
    for name, c in ranges.items():
        q = quantize(x, c)
        print(f"{name:10s} c={c:.3f}  mse={mse(x, c):.2e}  clipped={np.mean(np.abs(x) > c):6.2%}  rounded to zero={np.mean(q == 0):6.2%}")
    ```

<details markdown="1"><summary>Indice</summary>

Calculez d'abord le pas de min-max, comme à l'exercice 1, et comparez sa moitié à l'écart type.

</details>

<details markdown="1"><summary>Vérifier</summary>

```text
max |x| = 1.506  std = 0.034
min-max    c=1.506  mse=8.15e-04  clipped= 0.00%  rounded to zero=98.72%
p99.9      c=0.252  mse=1.61e-04  clipped= 0.10%  rounded to zero=56.61%
p99        c=0.117  mse=1.53e-04  clipped= 1.00%  rounded to zero=29.40%
MSE search c=0.171  mse=1.35e-04  clipped= 0.35%  rounded to zero=41.52%
```

La recherche MSE gagne, et min-max est le pire, environ six fois plus haut, avec 98.7 pour cent des valeurs arrondies à zéro. N'écrêter que 0.10 pour cent des valeurs (p99.9) divise déjà l'erreur par cinq. Écrêter 1 pour cent (p99) est un peu moins bon que la recherche (1.53e-04 contre 1.35e-04), parce que les valeurs écrêtées coûtent désormais plus que ce que l'arrondi a économisé : la meilleure plage se situe entre les extrêmes.

</details>

4. ▢ Prédisez, puis exécutez. Changez `qmax = 7` en `qmax = 127`, ce qui en fait une grille de 8 bits, et relancez. L'écrêtage gagnera-t-il encore ? Quelle plage la recherche MSE choisit-elle maintenant ?

<details markdown="1"><summary>Vérifier</summary>

```text
max |x| = 1.506  std = 0.034
min-max    c=1.506  mse=1.17e-05  clipped= 0.00%  rounded to zero=21.23%
p99.9      c=0.252  mse=5.51e-05  clipped= 0.10%  rounded to zero= 3.65%
p99        c=0.117  mse=1.30e-04  clipped= 1.00%  rounded to zero= 1.69%
MSE search c=1.019  mse=7.72e-06  clipped= 0.00%  rounded to zero=14.52%
```

L'écrêtage ne gagne plus : min-max bat les deux plages par percentile, et la recherche MSE choisit 1.019, proche de la plage complète, avec moins de 0.005 pour cent de valeurs écrêtées. Avec 127 niveaux de chaque côté, le pas est assez petit pour que les outliers coûtent peu d'erreur d'arrondi, alors que les écrêter coûte beaucoup. C'est la même forme que le tableau 1 de Nagel et al., où min-max et MSE sont à égalité en 8 bits : moins il y a de niveaux, plus une plage serrée rapporte.

</details>

5. ▢ Une équipe fixe la plage de chaque activation de LLM en minimisant la MSE, et la perplexity bondit. Utilisez cette leçon pour donner le mécanisme le plus probable, et dites ce que la MSE ne pouvait pas voir.

<details markdown="1"><summary>Vérifier</summary>

La plage a écrêté les features outlier. Elles forment une part minuscule des valeurs, donc les ramener à la limite change très peu la MSE du tenseur, mais elles comptent bien plus que leur nombre : Dettmers et al. ont mesuré une perplexity de 600 à 1000 pour cent plus haute quand ces dimensions étaient mises à zéro. La MSE pèse chaque valeur à égalité, et Nagel et al. notent que c'est la mauvaise pondération quand les valeurs diffèrent en importance. L'objectif de choix de la plage est un indicateur local de la loss de la tâche, et ici il pointe dans le mauvais sens. Garder les outliers hors de l'ensemble écrêté est le sujet de la leçon 8.

</details>

## Exercices en situation réelle

- [ ] Relancez l'expérience avec `df=10`, puis avec `rng.normal` au lieu de `standard_t`. Notez chaque fois l'écrêtage optimal de la recherche MSE comme multiple de l'écart type, et observez comment il évolue quand les queues s'allègent.
- [ ] Prenez une matrice de poids d'un petit modèle ouvert et affichez sa valeur absolue maximale à côté de ses 99e et 99.9e percentiles de valeur absolue. Décidez si min-max y gaspillerait l'essentiel d'une grille de 4 bits.
- [ ] Demain : sans notes, dites ce que min-max, MSE et percentile optimisent chacun, et quelle largeur en bits rend le choix le plus important. Relisez ensuite la section 3.1 et vérifiez si vous avez nommé le bon compromis.

## Pour aller plus loin

- [La correspondance de quantification](../reference/quantization-mapping.md)
- [Article : "A White Paper on Neural Network Quantization", Nagel et al., 2021](https://arxiv.org/abs/2106.08295)
- [Article : "LLM.int8(): 8-bit Matrix Multiplication for Transformers at Scale", Dettmers et al., 2022](https://arxiv.org/abs/2208.07339), section 4.2, pour comprendre pourquoi écrêter les outliers est dangereux
- [Ressources](../RESOURCES.md)

---

Ça ne passe pas ? Relisez la source primaire en haut de page, car cette leçon la condense et c'est dans la condensation que la compréhension s'échappe. Consultez le [glossaire](../GLOSSARY.md) pour tout terme qui vous a paru glissant.

Si c'est la leçon elle-même qui n'est pas claire plutôt que la matière, c'est un défaut : [ouvrez une issue](https://github.com/TokenCemetery/teach/issues).
