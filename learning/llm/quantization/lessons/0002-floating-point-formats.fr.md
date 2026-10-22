---
title: "2. Les formats à virgule flottante"
description: "Comment les bits de signe, d'exposant et de mantisse répartissent plage et précision en fp32, fp16 et bf16"
type: lesson
---

# Leçon 2. Les formats à virgule flottante

**Lien avec la mission :** Chaque format de nombres plus loin dans ce parcours est un choix de répartition de quelques bits entre plage et précision, donc vous devez savoir lire un agencement de bits et dire ce qu'il peut ou ne peut pas contenir avant de juger ce qu'un modèle quantifié a perdu.
**Source primaire :** [Article : "A Study of BFLOAT16 for Deep Learning Training", Kalamkar et al., 2019](https://arxiv.org/abs/1905.12322)
**Prérequis :** [Leçon 1](0001-what-quantization-buys.md), [Bits d'exposant](../GLOSSARY.md), [Bits de mantisse](../GLOSSARY.md)

## Échauffement

1. ▢ Combien d'octets par paramètre utilisent le fp32, le bf16 et l'int8, et combien de mémoire les poids d'un modèle de 7B paramètres prennent-ils dans chacun ?

<details markdown="1"><summary>Vérifier</summary>

Le fp32 utilise 4 octets (28 GB), le bf16 utilise 2 octets (14 GB) et l'int8 utilise 1 octet (7 GB). Ce sont les poids seuls, à la largeur en bits nominale.

</details>

2. ▢ Pourquoi un format de poids plus petit rend-il en général le décodage à batch 1 plus rapide ?

<details markdown="1"><summary>Vérifier</summary>

Le décodage à une taille de batch de 1 est limité par la mémoire : chaque poids est lu une fois par token et sert à peu d'arithmétique, donc moins d'octets par poids signifie moins à lire. La quantification weight-only ne rend pas l'arithmétique elle-même plus rapide.

</details>

## À savoir

### Trois champs

Un nombre à virgule flottante stocke un bit de signe, quelques **bits d'exposant** et quelques **bits de mantisse**. Pour une valeur normale, le champ d'exposant `e` et le champ de mantisse `m` donnent

```text
value = (-1)^sign × 2^(e - bias) × (1 + m / 2^M)
```

où `M` est le nombre de bits de mantisse et `bias` un décalage fixe qui permet à l'exposant d'être négatif. L'exposant choisit près de quelle puissance de deux se trouve la valeur. La mantisse choisit l'un des 2^M points régulièrement espacés entre cette puissance de deux et la suivante. Un champ d'exposant entièrement à zéro est réservé au zéro et aux valeurs subnormales, qui sont plus petites que la plus petite valeur normale et comblent l'écart jusqu'à zéro avec le même espacement. Un champ d'exposant entièrement à un est réservé, dans les formats IEEE, à l'infini et au NaN.

| Format | Bits au total | Signe / exposant / mantisse | Biais | Plus grande valeur finie | Plus petite valeur normale | Epsilon machine |
|---|---|---|---|---|---|---|
| fp32 | 32 | 1 / 8 / 23 | 127 | 3.4 × 10^38 | 1.2 × 10^-38 | 2^-23, environ 1.2 × 10^-7 |
| fp16 | 16 | 1 / 5 / 10 | 15 | 65,504 | 6.1 × 10^-5 | 2^-10, environ 9.8 × 10^-4 |
| bf16 | 16 | 1 / 8 / 7 | 127 | 3.4 × 10^38 | 1.2 × 10^-38 | 2^-7, environ 7.8 × 10^-3 |

Le chiffre 65,504 est celui que Micikevicius et al. donnent comme la plus grande valeur que le fp16 puisse représenter ([Micikevicius et al., 2017](https://arxiv.org/abs/1710.03740)). Le reste découle des agencements. L'**epsilon machine** est l'écart entre 1 et la valeur suivante au-dessus de lui, soit 2^-M.

Deux conséquences comptent pour la suite du parcours. D'abord, le fp16 et le bf16 prennent tous deux 2 octets, donc choisir entre eux ne change rien à la mémoire. C'est un choix entre trois bits de mantisse de plus et trois bits d'exposant de plus. Ensuite, le bf16 est du fp32 dont on a retiré les 16 bits de poids faible : les mêmes champs de signe et d'exposant et les 7 bits de mantisse de poids fort. Kalamkar et al. donnent cela comme la raison de l'intérêt du bf16 : sa plage est la même que celle du fp32 et la conversion depuis et vers le fp32 est simple.

### Plage et précision sont deux choses différentes

L'exposant fixe la **plage**, l'étendue entre la plus petite et la plus grande valeur. La mantisse fixe la **précision**, c'est-à-dire la finesse avec laquelle le format approche une valeur à l'intérieur de cette étendue. Elles sont indépendantes, et chaque bit de plus dans l'une est un bit pris à l'autre.

L'espacement n'est pas constant. Entre 2^k et 2^(k+1), les valeurs voisines sont distantes de 2^(k-M), donc l'écart double à chaque puissance de deux tandis que l'écart relatif reste d'environ 2^-M. En fp16, les valeurs juste au-dessus de 1 sont distantes d'environ 0.001, celles juste au-dessus de 1024 sont distantes d'exactement 1, et juste au-dessus de 2048 elles sont distantes de 2. Deux choses en découlent. Une addition dont le résultat tombe plus près d'une valeur existante que d'un milieu est ramenée en arrière, donc `1 + 0.0004` en fp16 vaut toujours 1, et une somme courante de uns en fp16 cesse de croître à 2048. Et une valeur arrondie est fausse d'au plus la moitié de l'espacement local, l'**erreur d'arrondi** que la quantification ajoute toujours.

### Pourquoi le fp16 avait besoin de loss scaling et pas le bf16

Les 5 bits d'exposant du fp16 le rendent étroit. La plus petite valeur positive qu'il puisse stocker est 2^-24, et tout ce qui est plus petit devient zéro. Micikevicius et al. ont mesuré des valeurs de gradient dans un run d'entraînement et ont constaté qu'environ 5 % des valeurs de gradient des poids avaient des exposants inférieurs à -24, qui seraient perdues. Leur remède est le **loss scaling** : multiplier la loss par une constante avant la rétropropagation, pour que chaque gradient soit remonté dans la plage du fp16, puis diviser le scale avant la mise à jour des poids. Ils choisissent le facteur de sorte que son produit avec le plus grand gradient en valeur absolue reste sous 65,504, parce qu'un dépassement produit des infinis et des NaN qui abîment les poids.

Le bf16 a les 8 bits d'exposant du fp32, donc les mêmes gradients sont représentables. Kalamkar et al. affirment que conserver la plage du fp32 évite tout réglage d'hyperparamètre pour la convergence, alors que le fp16 en exige. Leur émulation met à zéro les 16 bits de poids faible d'une valeur fp32, et ils comparent l'arrondi au plus proche à la troncature directe lors de la conversion. Dans l'une de leurs expériences, l'arrondi au plus proche égalait l'accuracy de la référence fp32 alors que la troncature perdait environ 0.02 %. Le prix du bf16 est la mantisse de 7 bits : les valeurs ne sont distantes que d'environ 0.8 % en termes relatifs.

Pour ce parcours, la leçon est l'échange lui-même. Les formats quantifiés à 8 bits et moins font le même échange de façon bien plus dure, ce qui explique que la leçon 4 ajoute un scale.

## Pratique

1. ▢ Quelle affirmation compare correctement le fp16 et le bf16 ?

    - a) Le fp16 a plus de bits d'exposant, donc une plage plus large
    - b) Le bf16 a plus de bits d'exposant, donc une plage plus large
    - c) Le bf16 a plus de bits de mantisse, donc un espacement plus fin
    - d) Le fp16 et le bf16 diffèrent par leur nombre total de bits

<details markdown="1"><summary>Vérifier</summary>

**b)** Le bf16 consacre 8 bits à l'exposant contre 5 pour le fp16, ce qui lui donne la plage du fp32, et il a 7 bits de mantisse contre 10 pour le fp16. (a) inverse les deux formats. (c) les inverse dans l'autre sens : c'est le fp16 qui a l'espacement le plus fin. (d) est faux parce que les deux font 16 bits, donc la mémoire ne les sépare pas.

</details>

2. ▢ Prédisez, puis exécutez. Que chaque ligne affiche-t-elle ?

    ```python
    import numpy as np

    with np.errstate(over="ignore"):
        print(float(np.float16(65504)), float(np.float16(65519)))
        print(float(np.float16(65520)), float(np.float16(70000)))
    ```

<details markdown="1"><summary>Indice</summary>

65,504 est la plus grande valeur finie du fp16, et la valeur suivante serait 65,536. Où se trouve le milieu, et dans quel sens arrondit un nombre situé au-dessus ?

</details>

<details markdown="1"><summary>Vérifier</summary>

```text
65504.0 65504.0
inf inf
```

65,519 est sous le milieu entre 65,504 et 65,536, donc il est arrondi vers le bas à 65,504. À partir de 65,520, la valeur est arrondie au-delà du plus grand nombre fini et devient l'infini, ce qui est, à l'entraînement, la façon dont commence un dépassement de gradient. La ligne `errstate` ne fait que faire taire l'avertissement de NumPy à ce sujet.

</details>

3. ▢ Prédisez, puis exécutez. Lesquelles des trois sommes valent exactement 1 ?

    ```python
    import numpy as np

    one = np.float16(1)
    for d in (0.0004, 0.0005, 0.001):
        print(d, float(one + np.float16(d)))
    ```

<details markdown="1"><summary>Indice</summary>

L'écart au-dessus de 1 en fp16 est 2^-10, soit environ 0.000977. Une somme va vers le voisin le plus proche.

</details>

<details markdown="1"><summary>Vérifier</summary>

```text
0.0004 1.0
0.0005 1.0009765625
0.001 1.0009765625
```

Seulement la première. Les voisins de 1 sont 1 et 1.0009765625, et le milieu est environ 1.000488. 0.0004 tombe en dessous et est entièrement perdu, tandis que 0.0005 saute d'un 2^-10 complet. Une valeur ajoutée à une plus grande n'est pas « un peu inexacte » : sous la moitié de l'espacement local, elle disparaît.

</details>

4. ▢ Prédisez, puis exécutez. Qu'affiche ce code, et que dit-il de l'addition de nombreux petits nombres en fp16 ?

    ```python
    import numpy as np

    total = np.float16(0)
    for _ in range(3000):
        total = total + np.float16(1)
    print(float(total))
    ```

<details markdown="1"><summary>Indice</summary>

Au-dessus de 2048, l'espacement du fp16 est 2. Que devient 2048 + 1 ?

</details>

<details markdown="1"><summary>Vérifier</summary>

```text
2048.0
```

À 2048, l'espacement est 2, donc 2049 se trouve exactement à mi-chemin entre deux valeurs représentables et est arrondi à la valeur paire, 2048. La somme y reste ensuite pour les 952 additions restantes. C'est pourquoi Micikevicius et al. accumulent les produits fp16 en fp32 plutôt qu'en fp16.

</details>

5. ▢ Prédisez, puis exécutez. Le bf16 est du fp32 dont on a retiré les 16 bits de poids faible. Avant d'exécuter, dites lesquelles des trois premières valeurs survivent inchangées à la conversion, et ce qui arrive à 1e38 en fp16.

    ```python
    import numpy as np

    def to_bf16(x):
        bits = np.asarray(x, dtype=np.float32).view(np.uint32) & np.uint32(0xFFFF0000)
        return bits.view(np.float32)

    x = np.array([1 + 2**-7, 1 + 2**-8, 3.14159265, 1e38], dtype=np.float32)
    print([float(v) for v in to_bf16(x)])
    with np.errstate(over="ignore"):
        print(float(np.float16(1e38)))
    ```

<details markdown="1"><summary>Indice</summary>

Le bf16 garde 7 bits de mantisse, donc 1 + 2^-7 est la première valeur au-dessus de 1 qu'il puisse contenir. Que vaut 1 + 2^-8 ?

</details>

<details markdown="1"><summary>Vérifier</summary>

```text
[1.0078125, 1.0, 3.140625, 9.969209968386869e+37]
inf
```

1 + 2^-7 survit, 1 + 2^-8 est tronqué à exactement 1, et pi devient 3.140625, correct à environ trois chiffres. 1e38 reste fini, environ 9.97e37 parce que la mantisse est coupée, mais le fp16 le transforme en infini. Cette fonction tronque, comme Kalamkar et al. décrivent que le fait leur émulation, qu'ils comparent à l'arrondi au plus proche.

</details>

6. ▢ Un collègue entraîne en fp16 et voit la loss devenir NaN après quelques centaines de pas, puis propose de passer au bf16. Expliquez ce qui se passe probablement, ce que fait le loss scaling à ce sujet, et ce que changerait le bf16.

<details markdown="1"><summary>Vérifier</summary>

Le fp16 plafonne à 65,504, donc une loss mise à l'échelle ou un gros gradient peut déborder vers l'infini et le NaN, et les petits gradients sous 2^-24 deviennent zéro. Le loss scaling choisit une constante pour que les gradients tombent dans la plage du fp16, et le scale est divisé avant la mise à jour des poids. Le bf16 a la plage d'exposant du fp32, donc aucun des deux problèmes n'apparaît et aucun scale n'est nécessaire, au prix d'une mantisse plus grossière. Changer n'est un bon remède que si le NaN est vraiment un problème de plage. Un NaN dû à un mauvais learning rate ou à un mauvais batch survit au changement.

</details>

## Exercices en situation réelle

- [ ] Dans une session Python avec NumPy, affichez `np.finfo(np.float16)` et `np.finfo(np.float32)` et repérez-y `max`, `tiny` et `eps`. Rapprochez chacun du tableau ci-dessus.
- [ ] Ouvrez le `config.json` d'un modèle ouvert sur le Hugging Face Hub et lisez son `torch_dtype`. Dites quelle plage et quel espacement ce choix implique.
- [ ] Demain : sans notes, écrivez le nombre de bits de signe, d'exposant et de mantisse du fp32, du fp16 et du bf16, et dites lequel des trois a la plage la plus large et lequel l'espacement le plus fin.

## Pour aller plus loin

- [Formats de nombres](../reference/number-formats.md)
- [Article : "A Study of BFLOAT16 for Deep Learning Training", Kalamkar et al., 2019](https://arxiv.org/abs/1905.12322)
- [Article : "Mixed Precision Training", Micikevicius et al., 2017](https://arxiv.org/abs/1710.03740), sections 3.1 et 3.2 pour la copie maître des poids et le loss scaling
- [Ressources](../RESOURCES.md)

---

Ça ne passe pas ? Relisez la source primaire en haut de page, car cette leçon la condense et c'est dans la condensation que la compréhension s'échappe. Consultez le [glossaire](../GLOSSARY.md) pour tout terme qui vous a paru glissant.

Si c'est la leçon elle-même qui n'est pas claire plutôt que la matière, c'est un défaut : [ouvrez une issue](https://github.com/TokenCemetery/teach/issues).
