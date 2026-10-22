---
title: "10. La passe arrière et autograd"
description: "Comment la règle de la chaîne, automatisée sur un graphe de calcul enregistré, transforme une loss scalaire en un gradient pour chaque poids"
type: lesson
---

# Leçon 10. La passe arrière et autograd

**Lien avec la mission :** La loss scalaire de la leçon 9 est inutile à l'entraînement à elle seule ; la passe arrière est ce qui la transforme en un gradient pour chaque poids du modèle, ce qui est le véritable signal que l'optimiseur (leçon 11) utilise pour les améliorer.
**Source primaire :** [Doc : "Autograd mechanics", PyTorch](https://pytorch.org/docs/stable/notes/autograd.html)
**Prérequis :** [Leçon 9](0009-cross-entropy-loss.md), [Scaled dot-product attention](../GLOSSARY.md)

## Échauffement

1. ▢ Pourquoi l'entropie croisée utilise-t-elle `-log(p)` plutôt que quelque chose comme `1 - p` comme pénalité pour une mauvaise prédiction ?

<details markdown="1"><summary>Vérifier</summary>

`-log(p)` croît sans borne quand la probabilité attribuée au bon token tend vers 0, ce qui pénalise de plus en plus sévèrement l'erreur faite avec assurance. `1 - p` sature à 1 quelle que soit l'assurance avec laquelle la prédiction est fausse, et ne donne aucun signal supplémentaire pour distinguer une prédiction simplement fausse d'une prédiction catastrophique.

</details>

2. ▢ Pourquoi les connexions résiduelles aident-elles à entraîner une pile profonde de blocs transformer ?

<details markdown="1"><summary>Vérifier</summary>

Elles donnent aux gradients un chemin direct à travers la connexion identité `+ x` à chaque couche, quoi que fasse la transformation de chaque sous-couche, ce qui garde un signal d'entraînement exploitable jusqu'aux toutes premières couches d'une pile profonde.

</details>

## À savoir

### Chaque opération de la passe avant enregistre comment elle a été calculée

Pendant l'exécution de la passe avant, chaque opération, un produit matriciel, un softmax, une addition pour une connexion résiduelle, est enregistrée dans un **graphe de calcul** (computation graph) : une trace de l'opération exacte qui a produit chaque tenseur intermédiaire, et à partir de quels tenseurs d'entrée. C'est ce graphe que la **passe arrière** parcourt, en sens inverse, pour calculer le gradient de la loss scalaire finale par rapport à chaque tenseur qui y a contribué, jusqu'à chaque poids entraînable.

### La règle de la chaîne, appliquée automatiquement

Le mécanisme sous-jacent n'est rien d'autre que la règle de la chaîne du calcul différentiel, automatisée : le gradient de la loss par rapport à un tenseur est la somme, sur chaque chemin situé en aval de lui dans le graphe, du gradient de la loss par rapport au tenseur aval, multiplié par la dérivée locale du tenseur aval par rapport à celui-ci. Un cas numérique concret : soit `y = 3x + 1` et `z = y^2`. Pour `x = 2`, `y = 7`. `dz/dy = 2y = 14`. `dy/dx = 3`. Par la règle de la chaîne, `dz/dx = dz/dy × dy/dx = 14 × 3 = 42`. Autograd fait exactement ce genre de multiplication et de sommation, mais sur chaque opération d'un réseau de millions ou de milliards de paramètres au lieu de deux petites équations.

![Un exemple travaillé avec y = 3x + 1 et z = y au carré, pour x = 2. La passe avant, dessinée de haut en bas et de gauche à droite, calcule x = 2, puis y = 7 par l'opération y = 3x + 1, puis z par l'opération z = y au carré. La passe arrière, dessinée en dessous et allant de droite à gauche, part de z, multiplie par la dérivée locale dz/dy = 14 pour atteindre y, puis multiplie par la dérivée locale dy/dx = 3 pour atteindre x, ce qui donne dz/dx = 14 fois 3 = 42 par la règle de la chaîne.](images/chain-rule-worked-example.svg)

### Différentiation automatique, ni symbolique ni numérique

L'**autograd** de PyTorch n'est ni de la différentiation symbolique (dériver une formule de gradient sous forme fermée à la main ou par calcul formel) ni de la différentiation numérique (approcher un gradient par différences finies, ce qui est imprécis et exige de relancer le calcul de la passe avant de nombreuses fois par paramètre). À la place, chaque opération primitive (produit matriciel, addition, softmax, etc.) a déjà une règle locale de rétropropagation dérivée à la main et implémentée, et autograd enchaîne automatiquement ces règles locales, en suivant le graphe de calcul enregistré, pour produire des gradients exacts en un seul parcours en arrière.

### Là où les connexions résiduelles font réellement leur travail

La leçon 5 a soutenu que les connexions résiduelles gardent les gradients en circulation à travers une pile profonde ; la règle de la chaîne est exactement l'endroit où cet argument devient mécanique. Pour une sortie résiduelle `y = x + Sublayer(x)`, le gradient de la loss par rapport à `x` vaut `d(loss)/d(y) × 1` (la dérivée locale du chemin identité, qui vaut exactement 1) plus un second terme qui passe par la propre dérivée locale de `Sublayer`. Quelle que soit la petitesse ou le mauvais comportement de la dérivée locale de `Sublayer`, ce premier terme garantit qu'au moins la contribution directe, non mise à l'échelle, de `d(loss)/d(y)` passe jusqu'à `x` sans changement. C'est la raison précise et mécanique pour laquelle les connexions résiduelles empêchent la disparition du gradient, et pas seulement une intuition informelle sur des « raccourcis ».

### Un seul appel remplit le gradient de chaque paramètre

Une fois la loss scalaire calculée, un seul appel, `loss.backward()`, parcourt tout le graphe de calcul et accumule, dans l'attribut `.grad` de chaque paramètre entraînable, le gradient de la loss par rapport à ce paramètre. Les gradients **s'accumulent** par défaut au lieu d'écraser, en s'ajoutant à ce qui se trouvait déjà dans `.grad`, c'est pourquoi une boucle d'entraînement doit explicitement remettre à zéro le gradient de chaque paramètre avant chaque nouvelle passe arrière ; sinon, le gradient de chaque pas serait contaminé par les valeurs résiduelles du pas précédent.

## Pratique

1. ▢ Soit `y = 3x + 1` et `z = y^2`. Pour `x = 2`, calculez `y`, `dz/dy`, `dy/dx` et `dz/dx` avec la règle de la chaîne.

<details markdown="1"><summary>Indice</summary>

`dz/dx = dz/dy × dy/dx`.

</details>

<details markdown="1"><summary>Vérifier</summary>

`y = 3(2) + 1 = 7`. `dz/dy = 2y = 14`. `dy/dx = 3`. `dz/dx = 14 × 3 = 42`.

</details>

2. ▢ Pour une sortie résiduelle `y = x + Sublayer(x)`, quel terme le chemin identité apporte-t-il à `d(loss)/d(x)`, et pourquoi cela garantit-il qu'un peu de gradient atteint `x` quelle que soit la petitesse de la dérivée locale de `Sublayer` ?

<details markdown="1"><summary>Vérifier</summary>

Le chemin identité apporte `d(loss)/d(y) × 1`, puisque la dérivée locale de la connexion identité vaut exactement 1. Ce terme ne dépend pas du tout de la dérivée propre de `Sublayer`, donc même si la contribution de `Sublayer` au gradient tend vers zéro, le `d(loss)/d(y)` direct, non mis à l'échelle, passe quand même jusqu'à `x` par ce chemin.

</details>

3. ▢ Pourquoi préfère-t-on la différentiation automatique (autograd) à la différentiation numérique (différences finies) pour entraîner un grand réseau ?

<details markdown="1"><summary>Vérifier</summary>

La différentiation numérique approche le gradient de chaque paramètre en le perturbant légèrement et en relançant la passe avant, ce qui est imprécis et exige une passe avant distincte par paramètre, un coût désespérément élevé pour un réseau de millions ou de milliards de poids. Autograd calcule au contraire des gradients exacts pour chaque paramètre en un seul parcours en arrière du graphe de calcul enregistré, en utilisant la règle locale de rétropropagation déjà implémentée de chaque opération.

</details>

4. ▢ Qu'est-ce qu'un appel à `loss.backward()` remplit réellement, et pourquoi les gradients doivent-ils généralement être remis à zéro avant l'appel suivant ?

<details markdown="1"><summary>Indice</summary>

Pensez à ce qui arrive à un attribut `.grad` qui contient déjà une valeur d'un pas précédent.

</details>

<details markdown="1"><summary>Vérifier</summary>

Il remplit l'attribut `.grad` de chaque paramètre entraînable avec le gradient de la loss par rapport à ce paramètre, calculé en parcourant le graphe de calcul enregistré. Les gradients s'accumulent par défaut au lieu d'écraser, en s'ajoutant à la valeur que `.grad` contenait déjà ; sans remise à zéro explicite des gradients avant chaque nouvelle passe arrière, le gradient d'un pas ultérieur serait contaminé par les valeurs résiduelles du pas précédent.

</details>

5. ▢ Quelle affirmation est vraie de la façon dont autograd calcule les gradients ?

    - a) Il exige que l'utilisateur dérive et fournisse une formule de gradient sous forme fermée pour chaque opération
    - b) Il approche les gradients par différences finies, en perturbant légèrement chaque paramètre
    - c) Il enregistre les opérations de la passe avant dans un graphe de calcul, puis applique automatiquement la règle de la chaîne avec la règle locale de rétropropagation déjà implémentée de chaque opération
    - d) Il ne calcule les gradients que pour la couche de sortie finale, pas pour les couches précédentes d'une pile profonde

<details markdown="1"><summary>Vérifier</summary>

**c)** C'est exactement ainsi qu'autograd fonctionne : pas de dérivation manuelle, pas d'approximation par différences finies, juste une application automatisée de la règle de la chaîne sur un graphe enregistré. (a) est faux : cela décrit la différentiation symbolique, pas l'approche d'autograd. (b) est faux : cela décrit la différentiation numérique, qu'autograd évite. (d) est faux : tout l'intérêt de la passe arrière est de propager les gradients en arrière à travers chaque couche, quelle que soit la profondeur de la pile.

</details>

## Exercices en situation réelle

- [ ] Construisez à la main un petit graphe de calcul (deux ou trois opérations enchaînées, comme l'exemple travaillé) et vérifiez que l'autograd de PyTorch produit le même gradient que votre calcul manuel par la règle de la chaîne.
- [ ] Exécutez une passe avant, appelez `loss.backward()` deux fois de suite sans remettre les gradients à zéro entre les deux, et vérifiez que les valeurs de `.grad` du second appel reflètent une accumulation et non un gradient neuf.
- [ ] Demain : lisez la section « How autograd encodes the history » de la documentation de la source primaire et notez en quoi le graphe enregistré diffère entre une passe avant ordinaire et une passe exécutée avec le suivi des gradients désactivé.

## Pour aller plus loin

- [Doc : "Autograd mechanics", PyTorch](https://pytorch.org/docs/stable/notes/autograd.html)
- [Dépôt : nanoGPT, Karpathy](https://github.com/karpathy/nanoGPT)
- [Ressources](../RESOURCES.md)

---

Ça ne passe pas ? Relisez la source primaire en haut de page, car cette leçon la condense et c'est dans la condensation que la compréhension s'échappe. Consultez le [glossaire](../GLOSSARY.md) pour tout terme qui vous a paru glissant.

Si c'est la leçon elle-même qui n'est pas claire plutôt que la matière, c'est un défaut : [ouvrez une issue](https://github.com/TokenCemetery/teach/issues).
