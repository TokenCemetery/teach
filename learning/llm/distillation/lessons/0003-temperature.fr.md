---
title: "3. Température"
description: "Adoucir les deux distributions avec une température, la correction par T au carré, et le mélange avec la loss sur les hard labels"
type: lesson
---

# Leçon 3. Température

**Lien avec la mission :** La mission vous demande de régler la température et les poids des loss d'un run de distillation, et cette leçon donne les trois éléments de ce réglage : la température, le facteur T au carré, et le poids de la loss sur les hard labels.
**Source primaire :** [Article : "Distilling the Knowledge in a Neural Network", Hinton, Vinyals et Dean, 2015](https://arxiv.org/abs/1503.02531)
**Prérequis :** [Leçon 2](0002-soft-targets.md), [Température](../GLOSSARY.md), [Loss combinée](../GLOSSARY.md), [Logit](../GLOSSARY.md)

## Échauffement

1. ▢ À la température 1, un élève a donné au 2 une probabilité de 0.98 et au 3 une probabilité de 0.01, et l'enseignant leur a donné 1.0 et 10^-6. Pourquoi le 3 a-t-il à peine bougé la loss ?

<details markdown="1"><summary>Vérifier</summary>

Chaque terme d'entropie croisée est la probabilité cible multipliée par le log de la probabilité de l'élève. La cible de 10^-6 du 3 rend son terme plus de 4 000 fois plus petit que celui du 2, si bien que l'information qu'elle contient est présente et presque inaudible.

</details>

2. ▢ Que dit un hard label de la similarité entre un 2 et un 7, et où se trouve cette information dans une distillation ?

<details markdown="1"><summary>Vérifier</summary>

Il n'en dit rien. La similarité vit dans les petites probabilités que l'[enseignant](../GLOSSARY.md) met sur les mauvaises classes, les [soft targets](../GLOSSARY.md).

</details>

## À savoir

### La température

L'article remplace le softmax par un softmax qui divise chaque [logit](../GLOSSARY.md) par une température T avant de normaliser : q_i = exp(z_i / T) / sum_j exp(z_j / T). T vaut normalement 1. Un T plus élevé donne une distribution plus douce sur les classes. La recette de l'article consiste à élever T jusqu'à ce que l'enseignant produise des soft targets suffisamment douces, puis à entraîner l'élève au même T élevé pour les reproduire. Après l'entraînement, l'élève utilise T = 1.

```python
import numpy as np

def softmax(z, T=1.0):
    z = np.asarray(z, float) / T
    e = np.exp(z - z.max())
    return e / e.sum()

logits = [9.0, 4.0, 2.0, 0.0, -4.0]   # classes: 2, 3, 7, 8, 0
np.set_printoptions(suppress=True, precision=4)
for T in (1, 2, 5, 20):
    print("T =", T, softmax(logits, T))
```

Prédisez la probabilité de la première classe à T = 5 avant de l'exécuter. La sortie avec NumPy 2.5 :

```text
T = 1 [0.9923 0.0067 0.0009 0.0001 0.    ]
T = 2 [0.889  0.073  0.0268 0.0099 0.0013]
T = 5 [0.5394 0.1984 0.133  0.0892 0.0401]
T = 20 [0.2745 0.2138 0.1934 0.175  0.1433]
```

À T = 1, les mauvaises classes totalisent moins de 1 %. À T = 5, elles portent près de la moitié de la probabilité, et l'ordre 3, 7, 8, 0 reste visible. À T = 20, la distribution est presque plate, et les différences que l'élève doit reproduire sont petites.

### Pourquoi la loss est multipliée par T au carré

Le gradient de l'entropie croisée par rapport à un logit z_i de l'élève, quand l'enseignant a des logits v_i et que les deux utilisent la température T, est (1/T)(q_i - p_i). L'équation 2 de l'article le donne. Si T est grand par rapport aux logits et que les logits sont centrés sur zéro pour chaque exemple, l'article montre que c'est approximativement (1/(N T^2))(z_i - v_i), où N est le nombre de classes. Donc à la limite des hautes températures, la distillation équivaut à minimiser 1/2 (z_i - v_i)^2, la correspondance de logits de Caruana et de ses collaborateurs. Faire correspondre les logits est un cas particulier de distillation.

Le facteur qui compte en pratique est le 1/T^2. L'article dit que les magnitudes des gradients des soft targets varient comme 1/T^2, il est donc important de les multiplier par T^2 quand on utilise à la fois des hard targets et des soft targets. Cela garde à peu près inchangées les contributions relatives des deux quand on change T en expérimentant avec les autres réglages.

```python
import numpy as np

def softmax(z, T=1.0):
    z = np.asarray(z, float) / T
    e = np.exp(z - z.max())
    return e / e.sum()

teacher = np.array([9.0, 4.0, 2.0, 0.0, -4.0])
student = np.array([6.0, 5.0, 0.0, 1.0, -2.0])
for T in (1, 2, 5, 10, 20):
    grad = (softmax(student, T) - softmax(teacher, T)) / T
    print(T, "%.4f" % np.abs(grad).max(), "%.4f" % (np.abs(grad).max() * T**2))
```

La sortie montre la plus grande entrée du gradient passant de 0.2663 à T = 1 à 0.0017 à T = 20. Multipliée par T au carré, elle reste entre 0.64 et 0.84 de T = 2 jusqu'à T = 20. La ligne T = 1 n'est pas une comparaison équitable, puisque l'approximation des hautes températures n'y tient pas.

### La loss combinée

Quand des labels corrects existent pour le jeu de transfert, l'article constate que l'entraînement sur les seules soft targets est amélioré si l'on entraîne aussi l'élève à produire les labels corrects. Il a essayé de modifier les soft targets avec les labels et a trouvé qu'une moyenne pondérée de deux objectifs était meilleure. Le premier est l'entropie croisée avec les soft targets, calculée au T élevé. Le second est l'entropie croisée avec les labels corrects, calculée à partir des mêmes logits de l'élève à T = 1. L'article a trouvé les meilleurs résultats en général avec un poids considérablement plus faible sur le second objectif.

Écrit explicitement, avec la notation de ce parcours et non celle de l'article, lambda étant le poids du terme sur les soft targets :

```text
loss = lambda * T^2 * CE(teacher at T, student at T) + (1 - lambda) * CE(label, student at 1)
```

C'est une [loss combinée](../GLOSSARY.md). Les expériences de parole de l'article ont utilisé un poids relatif de 0.5 sur le terme du hard label, et des températures de 1, 2, 5 et 10. La raison du petit terme sur le hard label est pratique : l'élève ne peut généralement pas reproduire exactement les soft targets, et l'article dit que pencher du côté de la bonne réponse se révèle utile.

DistilBERT suit le même schéma. Il applique un softmax avec température à l'enseignant et à l'élève pendant l'entraînement, fixe T à 1 à l'inférence, et ajoute ses propres termes à la loss sur les soft targets, sous forme de combinaison linéaire avec la loss de modélisation de langage masqué et une loss d'embedding par cosinus.

### Choisir T

L'article donne deux observations sur MNIST. Quand le réseau distillé avait 300 unités ou plus dans chacune de deux couches cachées, toutes les températures supérieures à 8 donnaient des résultats assez semblables. Quand les couches étaient réduites à 30 unités, les températures de 2.5 à 4 fonctionnaient nettement mieux que des valeurs plus hautes ou plus basses. Les auteurs suggèrent que, quand l'élève est trop petit pour capturer toute la connaissance de l'enseignant, ignorer les logits très négatifs qu'une température plus basse atténue peut aider.

Ne transposez pas une température d'un classifieur à un modèle de langage. Les auteurs de Minitron ont essayé les températures 0.1, 0.5, 1.0 et 3.0 en ré-entraînant un LLM élagué à partir de son enseignant et rapportent les meilleurs résultats à 1.0 (annexe A.3). Ils donnent une raison d'inclure des valeurs inférieures à 1 : les distributions de logits des LLM ont une entropie plus élevée que les distributions piquées des modèles de vision, ils s'attendaient donc à ce que l'adoucissement compte moins. Une seconde étude, plus vaste, concorde. Busbridge et al. (2025) ont balayé la température de 0.5 à 10 pour des élèves de 198M à 1.82B de paramètres, chacun distillé à partir d'un enseignant de 546M à 7.75B, et ont trouvé la meilleure performance à 1 sur toutes les échelles (annexe G.2). Les températures supérieures à 3 nuisaient, et les plus petits élèves en souffraient le plus. À l'annexe B.3, ils disent que, contrairement à la littérature qu'ils citent, la température optimale est un, et ils font l'hypothèse que la différence vient de ce que les travaux antérieurs utilisaient des tokens répétés alors que leur configuration ne répète pas les données. L'hypothèse est la leur et l'article ne la teste pas ici. Les deux résultats viennent des configurations de type pré-entraînement d'un seul laboratoire, lisez-les donc comme une bonne raison d'inclure T = 1 dans tout balayage, pas comme une preuve que des températures plus élevées n'aident jamais.

L'ablation de Minitron est elle aussi une seule configuration. Dans leur recette finale, ils ont aussi trouvé la loss sur les logits seule meilleure qu'un mélange pondéré avec la loss de modélisation de langage, ce qui rappelle que le poids est un réglage à tester et non une constante.

## Pratique

1. ▢ Avec les logits 9, 4, 2, 0 et -4, quelle probabilité la première classe obtient-elle environ à T = 5 ?

    - a) Environ 0.99
    - b) Environ 0.54
    - c) Environ 0.20
    - d) Environ 0.01

<details markdown="1"><summary>Indice</summary>

Divisez les logits par 5, passez chacun à l'exponentielle, et divisez le premier par la somme des cinq.

</details>

<details markdown="1"><summary>Vérifier</summary>

**b)** Les logits mis à l'échelle sont 1.8, 0.8, 0.4, 0 et -0.8. Leurs exponentielles valent environ 6.05, 2.23, 1.49, 1.00 et 0.45, ce qui donne une somme d'environ 11.22, et 6.05 / 11.22 vaut 0.54. Le choix (a) est la réponse à T = 1. Le choix (c) est la deuxième classe, 0.198 à T = 5, pas la première.

</details>

2. ▢ Vous faites passer T de 4 à 8 sans rien changer d'autre. Pourquoi l'article multiplie-t-il le terme sur les soft targets par T au carré ?

    - a) Pour annuler le réglage de température propre à l'enseignant
    - b) Pour s'assurer que les soft targets somment à un
    - c) Pour augmenter la confiance de l'élève au moment du test
    - d) Pour garder en équilibre les gradients doux et durs

<details markdown="1"><summary>Vérifier</summary>

**d)** Les gradients doux diminuent comme 1/T^2, donc sans ce facteur le terme doux s'effacerait devant le terme dur quand T grandirait. Ce n'est pas (b) : le softmax normalise déjà. Ce n'est pas (c) : à l'inférence, l'élève tourne à T = 1 et rien n'est multiplié. Ce n'est pas (a) : l'enseignant et l'élève partagent le même T et aucun des deux n'est annulé.

</details>

3. ▢ Dans la loss combinée de l'article, quel terme tourne à la haute température, lequel tourne à T = 1, et lequel reçoit généralement le poids le plus faible ?

<details markdown="1"><summary>Vérifier</summary>

L'entropie croisée avec les soft targets de l'enseignant tourne au T élevé, avec les logits de l'élève divisés par T. L'entropie croisée avec les labels corrects tourne sur les mêmes logits à T = 1. L'article a trouvé les meilleurs résultats en général avec un poids considérablement plus faible sur le terme du hard label. Les poids sont le réglage à ajuster, dites donc lesquels un résultat a utilisés.

</details>

4. ▢ Un collègue recopie le réglage MNIST de T = 20 dans une distillation de LLM et obtient un élève moins bon. Qu'est-ce qui, dans cette leçon, suggère pourquoi, et que devrait-il faire ?

<details markdown="1"><summary>Vérifier</summary>

L'ablation de Minitron sur 0.1, 0.5, 1.0 et 3.0 et le balayage de Busbridge de 0.5 à 10 ont tous deux trouvé les meilleurs résultats à 1, et les auteurs de Minitron disent que les distributions de logits des LLM ont une entropie plus élevée que les distributions piquées des modèles de vision. À T = 20, les cibles du fragment ci-dessus sont presque plates, donc les différences que l'élève doit apprendre sont petites. Il devrait lancer un court balayage incluant T = 1 avec son propre enseignant et son propre élève. Les deux résultats viennent chacun d'une seule configuration : c'est un point de départ, pas une règle.

</details>

5. ▢ Dans les expériences MNIST de l'article, quel élève était le plus sensible au choix de la température, celui à 300 unités cachées ou plus ou celui à 30, et quelle plage fonctionnait pour le sensible ?

<details markdown="1"><summary>Vérifier</summary>

L'élève à 30 unités. Les températures de 2.5 à 4 fonctionnaient nettement mieux que des valeurs plus hautes ou plus basses pour lui, alors qu'avec 300 unités ou plus tout ce qui dépassait 8 donnait des résultats assez semblables. L'article lit cela comme le fait qu'ignorer les logits très négatifs aide quand l'élève est trop petit pour contenir toute la connaissance de l'enseignant.

</details>

## Exercices en situation réelle

- [ ] Exécutez les deux scripts. Dans le second, changez les températures en 3 et 8 et vérifiez que la dernière colonne reste dans la même plage.
- [ ] Écrivez la loss combinée comme une fonction NumPy des logits de l'élève, des logits de l'enseignant, de l'indice du label, de T et de lambda, et vérifiez qu'avec lambda = 0 elle égale l'entropie croisée simple sur le label.
- [ ] Demain : sans notes, énoncez la formule du softmax avec température, dites quels termes de la loss combinée tournent à quelle température, et dites pourquoi le facteur T au carré est là.

## Pour aller plus loin

- [Loss de distillation](../reference/distillation-losses.md)
- [Article : "Distilling the Knowledge in a Neural Network", Hinton, Vinyals et Dean, 2015](https://arxiv.org/abs/1503.02531)
- [Article : "DistilBERT, a distilled version of BERT: smaller, faster, cheaper and lighter", Sanh et al., 2019](https://arxiv.org/abs/1910.01108)
- [Article : "Compact Language Models via Pruning and Knowledge Distillation", Muralidharan et al., 2024](https://arxiv.org/abs/2407.14679)
- [Article : "Distillation Scaling Laws", Busbridge et al., 2025](https://arxiv.org/abs/2502.08606)
- [Ressources](../RESOURCES.md)

---

Ça ne passe pas ? Relisez la source primaire en haut de page, car cette leçon la condense et c'est dans la condensation que la compréhension s'échappe. Consultez le [glossaire](../GLOSSARY.md) pour tout terme qui vous a paru glissant.

Si c'est la leçon elle-même qui n'est pas claire plutôt que la matière, c'est un défaut : [ouvrez une issue](https://github.com/TokenCemetery/teach/issues).
