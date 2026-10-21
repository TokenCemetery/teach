---
title: "4. Distillation au niveau du token"
description: "Faire correspondre la distribution du token suivant de l'enseignant à chaque position d'une séquence"
type: lesson
---

# Leçon 4. Distillation au niveau du token

**Lien avec la mission :** La mission vous demande d'écrire la loss de distillation au niveau du token pour un LLM, et cette leçon l'écrit : une divergence par position, sommée ou moyennée sur la séquence, avec le padding masqué.
**Source primaire :** [Article : "Sequence-Level Knowledge Distillation", Kim et Rush, 2016](https://arxiv.org/abs/1606.07947)
**Prérequis :** [Leçon 3](0003-temperature.md), [Distillation au niveau du token](../GLOSSARY.md), [Teacher forcing](../GLOSSARY.md), [Divergence KL](../GLOSSARY.md)

## Échauffement

1. ▢ Dans la loss combinée, quel terme tourne à la haute température, et par quoi est-il multiplié ?

<details markdown="1"><summary>Vérifier</summary>

L'entropie croisée avec les soft targets de l'enseignant tourne à la haute température T, et T au carré la multiplie pour que ses gradients gardent leur taille face au terme du hard label quand T change. Le terme du hard label tourne à T = 1.

</details>

2. ▢ Pourquoi une probabilité de 10^-6 de l'enseignant sur une mauvaise classe est-elle presque invisible pour la loss à T = 1 ?

<details markdown="1"><summary>Vérifier</summary>

Le terme d'entropie croisée de cette classe est sa probabilité cible multipliée par le log de la probabilité de l'élève, si bien qu'une cible de 10^-6 rend le terme environ un millionième aussi lourd qu'un terme proche de 1. Un T plus élevé relève ces cibles pour qu'elles comptent.

</details>

## À savoir

### L'origine : la distillation au niveau du mot

Kim et Rush appliquent l'idée de Hinton à la traduction. Un modèle de traduction neuronal est entraîné à minimiser la log-vraisemblance négative de chaque mot cible étant donné la phrase source et les mots qui précèdent, de sorte qu'un enseignant existe à chaque position de la phrase. Ils définissent la loss au niveau du mot pour une phrase comme une somme sur les positions j et sur chaque mot k du vocabulaire cible V :

```text
L_WORD-KD = - sum_j sum_k q(t_j = k | s, t_<j) * log p(t_j = k | s, t_<j)
```

Ici q est l'enseignant, p l'élève, s la phrase source, et le dernier argument de chaque probabilité est le préfixe, les mots cibles avant la position j. L'élève peut aussi s'entraîner sur un mélange de cette loss et de la log-vraisemblance négative ordinaire au niveau du mot. Ils appellent cela la distillation des connaissances au niveau du mot (section 3.1). Dans un LLM, l'unité est un token, c'est pourquoi ce parcours dit [distillation au niveau du token](../GLOSSARY.md).

Notez ce qu'est le conditionnement. Le préfixe vient de la séquence cible réelle des données d'entraînement. La figure 1 de l'article le décrit comme la minimisation de l'entropie croisée entre les distributions de l'élève et de l'enseignant pour chaque mot de la séquence cible réelle. Les deux modèles reçoivent le même préfixe fixe et chacun produit une distribution pour le mot suivant, ce qui est le [teacher forcing](../GLOSSARY.md).

Sur l'anglais vers l'allemand de WMT 2014 (tableau 1), un élève à 2 couches de 500 unités a obtenu 14.7 BLEU avec un décodage glouton et 17.6 avec beam search. Avec la distillation au niveau du mot, il a obtenu 15.4 et 17.7, des gains de 0.7 et 0.1. L'enseignant à 4 couches de 1000 unités a obtenu 17.7 et 19.5. Les auteurs ont testé des poids de mélange de 0.5 et 0.9 et ont trouvé 0.5 meilleur. L'article dit que la distillation au niveau du mot améliore la référence, et que sa méthode au niveau de la séquence fait mieux, ce qui est le sujet de l'étape 3.

### La loss pour un LLM

Trois articles récents écrivent la même loss sous des formes légèrement différentes. Ils s'accordent sur la structure : une divergence entre les deux distributions du token suivant à chaque position, combinée sur la séquence.

- Gemma 2 (Gemma Team, 2024, section 3.2) minimise la log-vraisemblance négative entre les probabilités de l'enseignant et celles de l'élève, la somme sur x de -P_T(x | x_c) log P_S(x | x_c), où x_c est le contexte.
- GKD (Agarwal et al., 2023, équation 2) moyenne une divergence sur les positions : la divergence est sommée sur les positions de sortie n et divisée par la longueur de sortie L_y.
- Minitron (Muralidharan et al., 2024, section 3) moyenne sur la longueur de séquence l, avec une température tau dans le softmax.

L'entropie croisée et la KL directe diffèrent par l'entropie de la distribution de l'enseignant, qui ne dépend pas de l'élève. Leurs gradients par rapport aux paramètres de l'élève sont les mêmes, c'est pourquoi les articles emploient l'un ou l'autre nom pour un seul objectif. La somme sur le vocabulaire est à l'intérieur de chaque terme. La forme du calcul est donc un tenseur de logits par modèle de dimensions batch, position et vocabulaire, et une divergence prise sur le dernier axe.

```python
import torch.nn.functional as F

def token_kd_loss(student_logits, teacher_logits, mask, T=1.0):
    # logits: (batch, positions, vocab). mask: (batch, positions), 1.0 for real tokens.
    s = F.log_softmax(student_logits / T, dim=-1)
    t = F.log_softmax(teacher_logits / T, dim=-1)
    kl = (t.exp() * (t - s)).sum(dim=-1)        # (batch, positions)
    return (kl * mask).sum() / mask.sum()        # mean over real tokens
```

Les logits de l'enseignant viennent d'une passe avant avec les gradients désactivés. Trois choix dans cette fonction sont des décisions, pas des faits. La moyenne sur les vrais tokens pourrait être une somme, comme l'écrivent Kim et Rush, et la somme croît avec la longueur de la séquence. Le masque compte parce que les positions de padding n'ont pas de cible significative. Et T = 1 est la valeur par défaut à cause de l'ablation de température de Minitron dans la leçon 3.

### La même arithmétique, exécutable

La version NumPy ci-dessous fait l'arithmétique de la fonction précédente sur trois positions avec quatre tokens, sans framework. Les logits de l'enseignant et de l'élève coïncident exactement à la troisième position, qui représente du padding.

```python
import numpy as np

def log_softmax(z):
    z = z - z.max(axis=-1, keepdims=True)
    return z - np.log(np.exp(z).sum(axis=-1, keepdims=True))

teacher = np.array([[3.0, 1.0, 0.0, -1.0],
                    [0.0, 2.5, 2.0, -2.0],
                    [1.0, 1.0, 1.0, 1.0]])
student = np.array([[2.0, 1.5, 0.5, -1.0],
                    [0.5, 2.0, 2.0, -1.0],
                    [1.0, 1.0, 1.0, 1.0]])
t, s = log_softmax(teacher), log_softmax(student)
kl = (np.exp(t) * (t - s)).sum(axis=-1)
mask = np.array([1, 1, 0])
print(np.round(kl, 4), round(kl.sum(), 4), round(kl.mean(), 4))
print(round((kl * mask).sum() / mask.sum(), 4))
```

Prédisez le dernier nombre par rapport à la moyenne des trois avant de l'exécuter. La sortie avec NumPy 2.5 :

```text
[0.1998 0.0541 0.    ] 0.2539 0.0846
0.127
```

Moyenner sur les trois positions dilue la loss avec une position qui ne porte aucun signal. Moyenner sur les deux vrais tokens donne 0.127.

### Ce que coûte la séquence fixe

Les séquences sont fixées avant l'entraînement, soit du texte humain, soit du texte que l'enseignant a écrit, et l'élève ne voit la distribution de l'enseignant que le long de ces séquences. À la génération, l'élève poursuit à partir de ses propres tokens, qu'aucune distribution ici ne couvrait. La leçon 14, à l'étape 5, nomme cela le biais d'exposition, et la leçon 15 montre le correctif on-policy. L'enseignant coûte aussi une passe avant pour chaque batch, ce que les auteurs de Minitron listent comme le surcoût de la distillation par rapport à l'entraînement conventionnel (section 4).

## Pratique

1. ▢ Dans le run NumPy, pourquoi la moyenne sur les vrais tokens, 0.127, dépasse-t-elle la moyenne sur les trois positions, 0.0846 ?

<details markdown="1"><summary>Indice</summary>

Comptez les positions dans chaque dénominateur, et regardez ce que la troisième position apporte au numérateur.

</details>

<details markdown="1"><summary>Vérifier</summary>

La troisième position ajoute 0 au numérateur mais compte dans le dénominateur de la moyenne simple : 0.2539 / 3 vaut 0.0846. Avec le masque, le dénominateur est 2 et 0.2539 / 2 vaut 0.127. Dans un vrai batch avec beaucoup de padding, la moyenne sans masque sous-estime la loss, et cette sous-estimation varie avec la quantité de padding.

</details>

2. ▢ Dans la loss au niveau du mot de Kim et Rush, sur quel préfixe l'enseignant et l'élève se conditionnent-ils tous deux ?

    - a) Les mots cibles des données d'entraînement
    - b) Les mots que l'élève a échantillonnés lui-même
    - c) Les mots que l'enseignant a choisis par décodage glouton
    - d) Les mots de la phrase source en entrée

<details markdown="1"><summary>Vérifier</summary>

**a)** Le préfixe est la séquence cible réelle, donc les deux modèles voient les mêmes mots fixes. Ce n'est pas (b) : c'est le cadre on-policy de la leçon 15. Ce n'est pas (c) : décoder la propre sortie de l'enseignant est la méthode au niveau de la séquence de l'étape 3. Ce n'est pas (d) : la phrase source est l'autre entrée de conditionnement, s, pas le préfixe.

</details>

3. ▢ Gemma 2 minimise une entropie croisée par rapport aux probabilités de l'enseignant, et Minitron écrit une divergence KL. Pourquoi les deux peuvent-ils décrire le même signal d'entraînement ?

<details markdown="1"><summary>Vérifier</summary>

La KL directe égale l'entropie croisée moins l'entropie de l'enseignant, et l'enseignant est fixe, donc cette entropie est une constante par rapport aux paramètres de l'élève. Les deux loss diffèrent par la valeur et non par le gradient. Vérifiez dans tout nouvel article laquelle des deux il désigne avant de comparer des valeurs de loss d'un article à l'autre.

</details>

4. ▢ Modifiez `token_kd_loss` pour qu'elle applique la température et le facteur T au carré de la leçon 3. Quels deux changements, et pourquoi la fonction en contenait-elle déjà un ?

<details markdown="1"><summary>Vérifier</summary>

La fonction divise déjà les deux jeux de logits par T avant le log-softmax, donc la température y est. Ce qui manque, c'est le facteur : multipliez la loss renvoyée par T ** 2 quand elle est combinée avec un terme de hard label, pour que le terme doux garde son poids quand T change. Avec T = 1 le facteur vaut 1, c'est pourquoi la fonction ci-dessus n'a besoin d'aucun changement à sa valeur par défaut.

</details>

5. ▢ Un coéquipier signale que la loss de distillation de son run de LLM a été divisée par deux après être passé à des batches avec padding jusqu'à une longueur plus grande. Le modèle n'a pas changé. Que vérifiez-vous en premier ?

<details markdown="1"><summary>Indice</summary>

Les positions de padding coïncident exactement entre un modèle et lui-même, elles n'ajoutent donc aucune divergence.

</details>

<details markdown="1"><summary>Vérifier</summary>

Si la moyenne divise par toutes les positions ou seulement par les vrais tokens. Dans le premier cas, une longueur de padding plus grande ajoute des positions au dénominateur et le nombre baisse sans aucun changement de qualité. Divisez par la somme du masque, comme le fait la fonction ci-dessus, et comparez à nouveau les deux runs.

</details>

## Exercices en situation réelle

- [ ] Exécutez le fragment NumPy. Changez ensuite les logits de l'élève à la première position pour qu'ils égalent ceux de l'enseignant et confirmez que la première entrée de la loss par position tombe à 0.
- [ ] Ouvrez l'article GKD et trouvez l'équation 2. Notez à côté si elle somme ou moyenne sur les positions et comment cela se compare à la somme de Kim et Rush.
- [ ] Demain : sans notes, écrivez la forme de chaque tenseur dans `token_kd_loss`, puis dites ce que protège le masque.

## Pour aller plus loin

- [Loss de distillation](../reference/distillation-losses.md)
- [Article : "Sequence-Level Knowledge Distillation", Kim et Rush, 2016](https://arxiv.org/abs/1606.07947)
- [Article : "On-Policy Distillation of Language Models: Learning from Self-Generated Mistakes", Agarwal et al., 2023](https://arxiv.org/abs/2306.13649)
- [Article : "Gemma 2: Improving Open Language Models at a Practical Size", Gemma Team, 2024](https://arxiv.org/abs/2408.00118)
- [Ressources](../RESOURCES.md)

---

Ça ne passe pas ? Relisez la source primaire en haut de page, car cette leçon la condense et c'est dans la condensation que la compréhension s'échappe. Consultez le [glossaire](../GLOSSARY.md) pour tout terme qui vous a paru glissant.

Si c'est la leçon elle-même qui n'est pas claire plutôt que la matière, c'est un défaut : [ouvrez une issue](https://github.com/TokenCemetery/teach/issues).
