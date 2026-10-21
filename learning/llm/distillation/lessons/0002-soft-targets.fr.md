---
title: "2. Soft targets"
description: "Ce que portent les probabilités qu'un enseignant donne aux mauvaises réponses, et pourquoi elles forment un signal d'entraînement plus riche qu'un hard label"
type: lesson
---

# Leçon 2. Soft targets

**Lien avec la mission :** La mission vous demande d'expliquer pourquoi les soft targets d'un enseignant portent plus de signal d'entraînement que les hard labels, et cette leçon est cette explication, avec un run qui permet de la vérifier.
**Source primaire :** [Article : "Distilling the Knowledge in a Neural Network", Hinton, Vinyals et Dean, 2015](https://arxiv.org/abs/1503.02531)
**Prérequis :** [Leçon 1](0001-what-distillation-buys.md), [Soft targets](../GLOSSARY.md), [Hard label](../GLOSSARY.md), [Logit](../GLOSSARY.md)

## Échauffement

1. ▢ Dans une distillation, les poids de quel modèle changent pendant l'entraînement, et quel modèle est le signal d'entraînement ?

<details markdown="1"><summary>Vérifier</summary>

Seul l'[élève](../GLOSSARY.md) apprend. L'[enseignant](../GLOSSARY.md) est fixe et fournit les cibles. Confondre les deux est la première erreur habituelle quand on lit une loss de distillation.

</details>

2. ▢ Le réseau MNIST de 800 unités a fait 146 erreurs seul et 74 quand il reproduisait aussi les sorties du réseau de 1200 unités. Qu'ont montré ces 74 sur ce que portaient les cibles ?

<details markdown="1"><summary>Vérifier</summary>

Les cibles portaient une connaissance de la manière de généraliser, apprise par l'enseignant à partir de données d'entraînement décalées aléatoirement, que l'élève n'a jamais vues dans son propre jeu de transfert. Un hard label pour chaque image n'en contient rien.

</details>

## À savoir

### Ce qu'un hard label jette

Un classifieur entraîné donne à la plupart des images une probabilité proche de 1 pour la bonne classe. Les minuscules probabilités sur les mauvaises classes diffèrent pourtant d'une image à l'autre. Hinton et al. donnent un exemple tiré de MNIST : une version d'un 2 peut recevoir une probabilité de 10^-6 d'être un 3 et de 10^-9 d'être un 7, et une autre version d'un 2 peut recevoir l'inverse. Cela dit quels 2 ressemblent à des 3 et quels 2 ressemblent à des 7, une structure de similarité sur les données. Un [hard label](../GLOSSARY.md) dit seulement « 2 » pour les deux.

Le terme de l'article pour la cible d'entraînement construite à partir de ces probabilités est soft targets. L'information qu'elles portent est parfois appelée dark knowledge, un nom qui n'apparaît pas dans cet article. Ce parcours dit [soft targets](../GLOSSARY.md) pour la cible et évite l'autre expression.

### Le piège : les petits nombres bougent à peine la loss

Le même passage nomme le problème. Des probabilités aussi proches de zéro ont très peu d'influence sur le coût d'entropie croisée pendant le transfert. Prenons un élève qui donne au 2 une probabilité de 0.98 et au 3 une probabilité de 0.01, face à un enseignant à 1.0 et 10^-6. Le 2 contribue d'environ 0.0202 à la loss et le 3 d'environ 0.0000046, soit plus de 4 000 fois moins. Le signal est là et la loss y est sourde.

Caruana et ses collaborateurs, dit l'article, ont évité cela en faisant correspondre les logits avec une erreur quadratique au lieu de faire correspondre les probabilités. La réponse plus générale de Hinton et al. consiste à élever la température jusqu'à ce que les cibles soient assez douces pour compter, ce qui est la leçon 3.

### Voyez-le tourner

Le script construit un enseignant sur cinq classes de chiffres, puis deux élèves. Les deux prédisent « 2 » avec la même confiance. L'élève A échange l'ordre du 3 et du 7 par rapport à l'enseignant, et l'élève B garde l'ordre de l'enseignant.

```python
import numpy as np

def softmax(z, T=1.0):
    z = np.asarray(z, float) / T
    e = np.exp(z - z.max())
    return e / e.sum()

def kl(p, q):
    return float(np.sum(p * np.log(p / q)))

teacher = [9.0, 4.0, 2.0, 0.0, -4.0]    # classes: 2, 3, 7, 8, 0
student_a = [9.0, 1.0, 4.0, 0.0, -4.0]  # same top class, 3 and 7 swapped
student_b = [9.0, 4.0, 2.5, 0.0, -4.0]  # same ranking as the teacher

for T in (1, 5):
    p = softmax(teacher, T)
    print("T =", T)
    for name, z in (("A", student_a), ("B", student_b)):
        q = softmax(z, T)
        ce = -np.log(softmax(z)[0])
        print("  student", name, "hard-label CE %.4f" % ce, "KL(teacher||student) %.4f" % kl(p, q))
```

Prédisez avant de l'exécuter : quel élève la cross-entropy sur hard label par rapport au label « 2 » préfère-t-elle, et lequel la divergence par rapport à l'enseignant préfère-t-elle ? Il affiche ceci, avec NumPy 2.5 :

```text
T = 1
  student A hard-label CE 0.0072 KL(teacher||student) 0.0177
  student B hard-label CE 0.0083 KL(teacher||student) 0.0001
T = 5
  student A hard-label CE 0.0072 KL(teacher||student) 0.0414
  student B hard-label CE 0.0083 KL(teacher||student) 0.0006
```

Le hard label préfère légèrement A, l'élève dont la structure de similarité est fausse. La divergence par rapport à l'enseignant préfère B avec une large avance. Les nombres sont construits pour la démonstration, lisez donc la direction et non les tailles. La divergence `KL` est la [divergence KL](../GLOSSARY.md) de la distribution de l'enseignant par rapport à celle de l'élève.

### Pourquoi cela compte davantage pour un modèle de langage

Le passage de l'article sur l'entropie s'applique directement à un modèle de langage. Quand les soft targets ont une entropie élevée, elles donnent bien plus d'information par cas d'entraînement que les hard targets. Une distribution du token suivant est rarement proche d'un one-hot : de nombreuses suites sont plausibles. Les auteurs de Minitron disent, dans une annexe sur la loss de distillation, que les distributions de logits des LLM ont une entropie plus élevée que les distributions piquées des modèles de classification (Muralidharan et al., 2024, annexe A.3). Leur observation porte sur cette configuration, mais elle va dans le même sens.

### Information sur une classe que l'élève n'a jamais vue

L'article a retiré tous les 3 du jeu de transfert, de sorte que l'élève n'en a jamais vu. Il n'a pourtant fait que 206 erreurs de test, dont 133 sur les 1010 3 du test. La plupart des erreurs venaient d'un biais appris de la classe 3 trop bas. Avec ce biais relevé de 3.5, un choix fait pour optimiser la performance globale sur le test, il a fait 109 erreurs, dont 14 sur des 3, et a trouvé juste 98.6 % des 3 du test. La connaissance de ce à quoi ressemble un 3 est arrivée par les soft targets des autres chiffres.

## Pratique

1. ▢ Dans le run ci-dessus, quel élève la cross-entropy sur hard label préfère-t-elle à T = 1, et lequel la divergence par rapport à l'enseignant préfère-t-elle ?

<details markdown="1"><summary>Indice</summary>

Comparez d'abord les deux nombres de CE, puis les deux nombres de KL, et demandez-vous ce que chaque loss peut voir.

</details>

<details markdown="1"><summary>Vérifier</summary>

La cross-entropy par rapport au label « 2 » préfère A (0.0072 contre 0.0083). La divergence par rapport à l'enseignant préfère B (0.0001 contre 0.0177). Le hard label ne voit que la probabilité de « 2 ». Le mauvais ordre du 3 et du 7 chez A lui est invisible, et cet ordre est ce que porte la soft target.

</details>

2. ▢ Pourquoi les minuscules probabilités de l'enseignant sur les mauvaises classes n'aident-elles guère quand l'élève est entraîné à la température 1 ?

    - a) Seule l'entrée de la bonne classe entre dans la loss
    - b) Les entrées des mauvaises classes sont écartées avant la loss
    - c) Chaque terme est mis à l'échelle par sa probabilité cible
    - d) Le softmax de l'élève ne peut pas produire de valeurs très minuscules

<details markdown="1"><summary>Vérifier</summary>

**c)** Chaque terme de la cross-entropy est la probabilité cible multipliée par le log de celle de l'élève. Une cible de 10^-6 pèse un millionième de ce que pèse une cible proche de 1. Ce n'est pas (b) : rien ne les retire. Ce n'est pas (a) : cela décrit la loss sur hard label, pas celle sur soft targets. Ce n'est pas (d) : un softmax peut produire 10^-9 sans difficulté.

</details>

3. ▢ Un élève entraîné sur un jeu de transfert sans aucun 3 trouve juste 98.6 % des 3 du test une fois son biais pour la classe 3 relevé. Comment peut-il savoir ce qu'est un 3 ?

<details markdown="1"><summary>Vérifier</summary>

Les soft targets de l'enseignant sur les autres chiffres, des 2, des 5 et des 8 par exemple, mettent une petite probabilité sur 3. Ces probabilités apprennent à l'élève quelles caractéristiques augmentent le score d'un 3, sans un seul 3 comme exemple d'entraînement. Le biais appris pour la classe était bien trop bas : la connaissance était donc là et c'est le décalage qui était faux. Le résultat est celui de l'article, sur MNIST, avec un biais ajusté.

</details>

4. ▢ Un enseignant donne à un 2 une probabilité de 1.0 et à un 3 une probabilité de 10^-6. Un élève leur donne 0.98 et 0.01. Environ combien de fois plus petit est le terme du 3 dans l'entropie croisée que celui du 2 ?

<details markdown="1"><summary>Indice</summary>

Chaque terme est la probabilité de l'enseignant multipliée par l'opposé du logarithme naturel de celle de l'élève.

</details>

<details markdown="1"><summary>Vérifier</summary>

Le terme du 2 est -1.0 \* ln(0.98), soit environ 0.0202. Le terme du 3 est -10^-6 \* ln(0.01), soit environ 0.0000046. Le rapport est d'environ 4 400, donc plus de 4 000 fois plus petit. C'est pourquoi élever la température, plutôt que de simplement faire confiance à la loss, est la voie de l'article pour faire compter ces entrées.

</details>

## Exercices en situation réelle

- [ ] Exécutez le script. Modifiez ensuite l'élève A pour que le 3 reste au-dessus du 7 (par exemple `[9.0, 3.0, 2.5, 0.0, -4.0]`) et regardez les deux nombres de KL baisser vers ceux de l'élève B.
- [ ] Trouvez un classifieur que vous pouvez charger, affichez son softmax pour cinq images à la température 1, et notez les deuxième et troisième classes les plus probables. Ressemblent-elles aux voisines de la vraie classe ?
- [ ] Demain : sans notes, expliquez en deux phrases pourquoi un hard label ne peut pas porter la similarité entre un 2 et un 7.

## Pour aller plus loin

- [Loss de distillation](../reference/distillation-losses.md)
- [Article : "Distilling the Knowledge in a Neural Network", Hinton, Vinyals et Dean, 2015](https://arxiv.org/abs/1503.02531)
- [Article : "Compact Language Models via Pruning and Knowledge Distillation", Muralidharan et al., 2024](https://arxiv.org/abs/2407.14679)
- [Ressources](../RESOURCES.md)

---

Ça ne passe pas ? Relisez la source primaire en haut de page, car cette leçon la condense et c'est dans la condensation que la compréhension s'échappe. Consultez le [glossaire](../GLOSSARY.md) pour tout terme qui vous a paru glissant.

Si c'est la leçon elle-même qui n'est pas claire plutôt que la matière, c'est un défaut : [ouvrez une issue](https://github.com/TokenCemetery/teach/issues).
