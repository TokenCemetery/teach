---
title: "17. Fidélité et généralisation"
description: "Pourquoi un élève qui généralise bien peut quand même être en désaccord avec son enseignant, et lequel des deux il vous faut"
type: lesson
---

# Leçon 17. Fidélité et généralisation

**Lien avec la mission :** La mission vous demande de prédire ce qu'un élève héritera, et de mesurer ce qu'il a perdu, ce qui commence par séparer la fidélité avec laquelle il copie l'enseignant de la qualité avec laquelle il fait la tâche.
**Source primaire :** [Article : "Does Knowledge Distillation Really Work?", Stanton et al., 2021](https://arxiv.org/abs/2106.05945), sections 3 à 7
**Prérequis :** [Leçon 3](0003-temperature.md), [Leçon 16](0016-on-policy-distillation-in-practice.md), [Fidélité](../GLOSSARY.md), [KL directe](../GLOSSARY.md), [Loss combinée](../GLOSSARY.md)

## Échauffement

1. ▢ La loss combinée ajoute deux termes. Lequel tire l'élève vers l'enseignant et lequel vers les labels ?

<details markdown="1"><summary>Vérifier</summary>

La divergence par rapport aux [soft targets](../GLOSSARY.md) de l'enseignant le tire vers l'enseignant, et l'entropie croisée par rapport aux [hard labels](../GLOSSARY.md) le tire vers les données. Un coefficient de mélange les pondère.

</details>

2. ▢ La phase on-policy de Qwen3 minimise la KL entre l'élève et l'enseignant sur les propres échantillons de l'élève. Quelle direction de la KL est la forme enseignant vers élève, et que pénalise-t-elle ?

<details markdown="1"><summary>Vérifier</summary>

KL(teacher || student) est la KL directe. Elle pénalise l'élève quand il met peu de probabilité là où l'enseignant en met beaucoup, si bien qu'elle pousse l'élève à couvrir tout ce que couvre l'enseignant.

</details>

3. ▢ Dans la leçon 16, l'élève de Qwen3 a battu le checkpoint entraîné par RL sur les benchmarks. Cela vous dit-il que les prédictions de l'élève correspondent à celles de son enseignant ?

<details markdown="1"><summary>Vérifier</summary>

Non. Les scores de benchmark mesurent la tâche. Savoir si l'élève est d'accord avec les prédictions de son enseignant est une mesure distincte, et cette leçon explique pourquoi les deux peuvent se dissocier.

</details>

## À savoir

### Deux choses que la distillation pourrait avoir améliorées

Stanton et al. séparent deux quantités que la littérature sur la distillation confond généralement. La **fidélité** est la capacité d'un élève à reproduire les prédictions de l'enseignant. La **généralisation** est la performance de l'élève sur des données non vues de la même distribution. Ils mesurent la fidélité avec deux nombres sur les mêmes entrées, tous deux définis à la section 3.2 :

| Métrique | Ce qu'elle mesure |
|---|---|
| Accord top-1 moyen | La fraction d'entrées où l'élève et l'enseignant choisissent le même meilleur label |
| KL prédictive moyenne | La KL(teacher \|\| student) moyenne, sensible à chaque classe, pas seulement à la première |

L'exactitude ne peut pas tenir lieu d'accord. L'exemple de l'article lui-même : trois modèles indépendants avec 55 %, 75 % et 95 % de précision au test. Le premier et le troisième peuvent s'accorder sur au plus 60 % des entrées, alors que le deuxième et le troisième s'accordent sur au moins 70 %, et pourtant personne ne dirait que le modèle à 75 % est une meilleure distillation du modèle à 95 %, puisqu'ils ont été entraînés indépendamment.

### Le contrôle pour « ils sont d'accord parce que les deux sont bons »

L'accord augmente simplement parce que les modèles sont précis. Pour séparer une amélioration générale d'une amélioration spécifique de la correspondance, l'article entraîne aussi un second élève, distillé par la même procédure à partir d'un enseignant indépendant. Si les deux élèves s'accordent à peu près autant avec le premier enseignant, l'accord s'explique par la généralisation. Si le vrai élève s'accorde davantage avec son propre enseignant, c'est de la fidélité.

### Ce qu'ils ont trouvé

Leurs expériences sont surtout de la classification d'images avec des ResNet sur CIFAR-100, plus MNIST, ImageNet et un jeu de classification de texte (sentiment IMDB) en annexe. Ce ne sont pas des expériences sur la génération de modèles de langage, lisez-les donc comme un résultat sur la distillation en général, puis testez-le sur votre propre paire de LLM.

| Constat | Preuve dans l'article |
|---|---|
| Cas facile : la correspondance fonctionne | LeNet-5 sur MNIST a atteint plus de 99 % d'accord top-1 au test avec assez de données de distillation (section 4.1) |
| Cas plus difficile : souvent non | L'auto-distillation de ResNet-56 sur CIFAR-100 est restée sous 80 % d'accord au test même avec le plus grand jeu de distillation (section 6.1) |
| Une meilleure généralisation peut s'accompagner d'une moins bonne fidélité | En auto-distillation, agrandir les données avec des échantillons de GAN a augmenté la fidélité et baissé la précision au test, parce qu'un élève qui échoue à reproduire l'enseignant peut mieux généraliser (figure 1a, section 4.2) |
| Avec un enseignant plus fort, les deux s'alignent | En distillant un ensemble de 3 composants, la fidélité et la précision au test ont toutes deux augmenté avec plus de données (figure 1b) |
| Ce n'est pas la capacité | Une faible fidélité apparaît même en auto-distillation, où l'élève a la capacité propre de l'enseignant, et agrandir l'élève l'a à peine changée en distillant un ensemble (section 4.4) |
| Ce n'est pas une architecture, une échelle ou un domaine | Résultats similaires avec VGG, sur ImageNet et sur IMDB (section 4.4) |

### L'explication : l'optimisation

L'article teste deux hypothèses pour l'échec. L'une est l'identifiabilité : les données de distillation sont trop petites pour déterminer la fonction de l'enseignant. Plus de données améliorent l'accord au test, donc cela fait partie de l'histoire. L'autre est l'optimisation : l'élève ne peut même pas reproduire l'enseignant sur les données de distillation sur lesquelles il s'entraîne.

La seconde tient. Avec 50k images synthétiques ajoutées, un élève de même capacité que son enseignant n'a atteint que 95 % d'accord sur les données de distillation elles-mêmes. Avec une forte augmentation de données, l'accord à l'entraînement était entre 80 % et 90 % pour trois augmentations et tombait à environ 60 % en auto-distillation pour la combinaison des trois (section 6.1). Entraîner plus longtemps a un peu aidé : pour une auto-distillation de ResNet-20, 5,000 époques de SGD ont atteint 83.3 % d'accord à l'entraînement contre 78.95 % à 300 époques, et passer à Adam a réduit la fidélité (section 6.2).

Le résumé de l'article est un compromis. Ajouter des exemples au-delà des données d'entraînement de l'enseignant donne à l'élève plus de labels de l'enseignant pour identifier la fonction, et rend aussi plus difficile un problème d'optimisation déjà difficile. Selon les mots de l'article, une bonne fidélité est directement alignée avec la résolution d'un problème d'optimisation exceptionnellement difficile, alors que l'entraînement ordinaire est sauvé par le fait de ne pas avoir besoin de le résoudre bien.

### Ce que cela change pour vous

Si vous n'évaluez un LLM distillé que par sa précision sur la tâche, vous ne pouvez pas savoir quelle part de l'enseignant vous avez héritée. Deux élèves peuvent obtenir le même score et différer beaucoup par l'accord. L'étape 8 construit la mesure complète, et l'habitude minimale est celle-ci : rapportez l'accord avec l'enseignant sur des entrées held-out à côté de la qualité sur la tâche, et comparez avec un élève distillé à partir d'un autre enseignant ou entraîné sans enseignant.

La fidélité n'est pas toujours le but. Le propre résultat d'auto-distillation de l'article montre un élève qui échoue à reproduire son enseignant mais généralise mieux. La fidélité compte quand vous voulez hériter de propriétés au-delà de la précision : l'article cite le transfert de la calibration ou de la robustesse pour qu'un modèle plus petit puisse remplacer sans risque un plus grand (section 4.3). Il a aussi constaté que l'élève de plus haute fidélité était toujours le mieux calibré en distillant des ensembles.

Une esquisse en Python pur des deux mesures, qui affiche la sortie indiquée dans les commentaires :

```python
import math

def softmax(z):
    m = max(z)
    e = [math.exp(v - m) for v in z]
    s = sum(e)
    return [v / s for v in e]

def argmax(z):
    return max(range(len(z)), key=lambda i: z[i])

def kl(p, q):
    return sum(pi * (math.log(pi) - math.log(qi)) for pi, qi in zip(p, q))

# One row per example: logits over three classes, plus the true label.
teacher = [[3.0, 1.0, 0.0], [0.5, 2.5, 0.0], [0.0, 0.5, 3.0], [1.0, 2.0, 0.0]]
student = [[2.0, 1.5, 0.0], [0.0, 1.0, 2.0], [0.0, 0.5, 2.5], [2.0, 1.5, 0.0]]
labels = [0, 1, 2, 0]

agreement = sum(argmax(t) == argmax(s) for t, s in zip(teacher, student)) / len(labels)
mean_kl = sum(kl(softmax(t), softmax(s)) for t, s in zip(teacher, student)) / len(labels)
teacher_acc = sum(argmax(t) == y for t, y in zip(teacher, labels)) / len(labels)
student_acc = sum(argmax(s) == y for s, y in zip(student, labels)) / len(labels)

print(f"agreement {agreement:.2f}  mean KL {mean_kl:.3f}")      # agreement 0.50  mean KL 0.321
print(f"teacher accuracy {teacher_acc:.2f}  student accuracy {student_acc:.2f}")  # both 0.75
```

Les deux modèles obtiennent 0.75, et ils ne s'accordent que sur la moitié des entrées.

## Pratique

1. ▢ Un enseignant a 93 % de précision et un élève 91 %, sur le même jeu de test. Entre quelles bornes leur accord top-1 doit-il se situer ?

<details markdown="1"><summary>Indice</summary>

L'élève se trompe sur 9 % des entrées et l'enseignant sur 7 %. De combien les deux ensembles d'erreurs peuvent-ils se recouvrir, et au minimum de combien ?

</details>

<details markdown="1"><summary>Vérifier</summary>

Entre 84 % et 98 %. Ils s'accordent partout où les deux ont raison, et le pire cas est que leurs erreurs ne se recouvrent jamais, ce qui laisse 100 moins 7 moins 9, donc 84 % au moins. Ils ne peuvent s'accorder que sur 98 % au plus : l'élève se trompe sur 2 points de pourcentage d'entrées de plus que l'enseignant, donc au moins 2 % des entrées ont l'enseignant juste et l'élève faux. Égaler la précision vous dit très peu de chose sur l'accord, ce qui est le propos de la leçon.

</details>

2. ▢ Dans le contrôle de l'article, pourquoi entraîner un second élève à partir d'un enseignant indépendant ?

    - a) Cela vérifie que l'enseignant a été bien entraîné
    - b) Cela sépare la fidélité de la compétence partagée
    - c) Cela augmente la précision du premier élève
    - d) Cela réduit le calcul nécessaire au total

<details markdown="1"><summary>Vérifier</summary>

**b)** Si un élève s'accorde avec un enseignant indépendant à peu près autant qu'avec le sien, l'accord s'explique par le fait que les deux sont bons, pas par de la copie. (a) n'est pas testé ici. (c) et (d) sont faux : le second élève est un outil de mesure et ne change rien au premier.

</details>

3. ▢ Dans l'auto-distillation sur CIFAR-100 avec un élève et un enseignant ResNet-56, le jeu de distillation est agrandi avec des images générées par GAN. Prédisez la direction de la fidélité de l'élève et de sa précision au test.

<details markdown="1"><summary>Indice</summary>

L'auto-distillation est le cas où l'élève a déjà la capacité de reproduire l'enseignant, et l'article note que l'échec de la correspondance peut lui-même aider.

</details>

<details markdown="1"><summary>Vérifier</summary>

La fidélité augmente et la précision au test diminue (figure 1a). En auto-distillation, l'élève qui reproduit moins étroitement l'enseignant généralise mieux, donc plus de fidélité coûte de la précision. Avec un enseignant en ensemble de 3, la direction s'inverse : les deux augmentent (figure 1b). Lequel s'applique à vous dépend de la capacité de votre enseignant à bien mieux généraliser qu'un élève entraîné indépendamment.

</details>

4. ▢ Un élève distillé avec l'architecture propre de l'enseignant est quand même en désaccord avec lui sur 20 % des entrées held-out. Listez les hypothèses que l'article teste et dites laquelle il soutient.

<details markdown="1"><summary>Vérifier</summary>

La capacité de l'élève, l'architecture, l'échelle du jeu de données, le domaine des données, l'identifiabilité et l'optimisation (section 4.4). L'article écarte la capacité, puisque l'élève a la capacité de l'enseignant, et les autres sur ses preuves. Il soutient l'optimisation comme raison clé : l'élève ne reproduit pas l'enseignant même sur ses propres entrées d'entraînement. L'identifiabilité fait aussi partie du tableau, puisque plus de données ont augmenté l'accord au test. L'article a trouvé le grand écart d'accord sur des tâches d'images, vérifiez donc sur votre paire de LLM avant de supposer qu'il se transpose.

</details>

5. ▢ Laquelle de ces mesures sur un LLM est l'analogue le plus proche de la KL prédictive moyenne de l'article, et de quoi a-t-elle besoin que l'accord n'exige pas ?

<details markdown="1"><summary>Vérifier</summary>

La KL(teacher || student) moyenne par position sur des séquences held-out, qui est la loss de distillation au niveau du token en KL directe de l'étape 2 évaluée sur des données non utilisées pour l'entraînement. Elle a besoin de la distribution complète de l'enseignant à chaque position, ce que l'accord sur le token de tête n'exige pas. L'accord sur le token de tête est l'analogue moins coûteux de l'accord top-1. Cette transposition du cadre de classification de l'article au niveau du token est mon adaptation, pas une expérience de l'article.

</details>

## Exercices en situation réelle

- [ ] Exécutez l'esquisse ci-dessus, puis changez une ligne de logits de l'élève pour que les deux modèles soient en désaccord sur un autre exemple alors que la précision reste à 0.75. Notez ce qu'il est advenu de l'accord et de la KL moyenne.
- [ ] Lisez la section 3.2 de l'article de Stanton et écrivez la formule de l'accord top-1 moyen en une ligne. Écrivez ensuite ce que vous dit l'élève de contrôle s-prime.
- [ ] Demain : sans notes, énoncez la différence entre fidélité et généralisation, un cas où plus de fidélité baisse la précision, et l'explication principale de l'article pour la faible fidélité.

## Pour aller plus loin

- [Ce dont l'élève hérite](../reference/what-the-student-inherits.md)
- [Article : "Does Knowledge Distillation Really Work?", Stanton et al., 2021](https://arxiv.org/abs/2106.05945)
- [Ressources](../RESOURCES.md)

---

Ça ne passe pas ? Relisez la source primaire en haut de page, car cette leçon la condense et c'est dans la condensation que la compréhension s'échappe. Consultez le [glossaire](../GLOSSARY.md) pour tout terme qui vous a paru glissant.

Si c'est la leçon elle-même qui n'est pas claire plutôt que la matière, c'est un défaut : [ouvrez une issue](https://github.com/TokenCemetery/teach/issues).
