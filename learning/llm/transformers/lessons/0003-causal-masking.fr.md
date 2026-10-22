---
title: "3. Masquage causal"
description: "Pourquoi une position de requête ne doit pas porter son attention sur les positions futures, et pourquoi le masque s'applique avant le softmax et non après"
type: lesson
---

# Leçon 3. Masquage causal

**Lien avec la mission :** C'est la leçon de clôture de l'étape 1 : la multi-head attention (leçon 2) laisse chaque position porter son attention sur toutes les autres, ce qui est exactement ce qu'il ne faut pas pour la génération autorégressive que le modèle de cet espace de travail finira par faire, et cette leçon en est le remède.
**Source primaire :** [Billet : "The Annotated Transformer", Harvard NLP](http://nlp.seas.harvard.edu/annotated-transformer/)
**Prérequis :** [Leçon 2](0002-multi-head-attention.md), [Scaled dot-product attention](../GLOSSARY.md)

## Échauffement

1. ▢ Dans la multi-head attention, pour la mise à l'échelle `/ sqrt(d_k)` à l'intérieur d'une tête, `d_k` doit-il être la dimension par tête ou la pleine dimension du modèle ?

<details markdown="1"><summary>Vérifier</summary>

La dimension par tête (`d_model / h`). La mise à l'échelle compense la croissance de la variance d'un produit scalaire sommé sur `d_k` termes, et à l'intérieur d'une tête ce produit scalaire est sommé sur la dimension propre à la tête, plus petite.

</details>

2. ▢ Qu'accomplit l'étape softmax dans la scaled dot-product attention ?

<details markdown="1"><summary>Vérifier</summary>

Elle convertit les scores de similarité bruts de chaque requête avec toutes les clés en distribution de probabilité, non négative et de somme 1, ce qui fait de la sortie un mélange pondéré des valeurs.

</details>

## À savoir

### Pourquoi porter son attention sur le futur pose problème

Un modèle qui génère du texte un token à la fois produit le token *N* en utilisant seulement les tokens 1 à *N-1* ; le token *N+1* n'existe pas encore à ce moment-là. Si, pendant l'entraînement, la self-attention laisse la position *i* porter son attention sur une position *j* supérieure à *i*, le modèle peut utiliser le token même qu'il est censé prédire, et tous ceux qui le suivent, pour calculer cette prédiction. La loss d'entraînement paraît excellente, puisque le modèle recopie en fait une réponse qu'il voit déjà, mais il n'apprend rien d'utile, parce qu'au moment de la génération réelle ces tokens futurs ne sont jamais disponibles. Le **masquage causal** est ce qui garde l'entraînement honnête : il restreint chaque position à ne porter son attention que sur elle-même et sur les positions antérieures, ce qui correspond exactement à ce qui sera disponible quand le modèle générera réellement du texte un token à la fois.

### Le masque s'applique aux scores, avant le softmax

Le remède se situe à l'intérieur même de l'équation, avant l'étape softmax : on ajoute un masque aux scores bruts `QK^T / sqrt(d_k)`, qui met à un très grand nombre négatif chaque entrée dont la position de clé est postérieure à la position de requête (en pratique moins l'infini, ou quelque chose de numériquement équivalent, comme -1e9). Après que ce score masqué est passé par `exp(...)` dans le softmax, un très grand nombre négatif devient une valeur indiscernable de zéro, donc cette position ne contribue pratiquement à rien dans la somme pondérée finale, et les poids des positions restantes, non masquées, se renormalisent entre eux pour que leur somme reste égale à 1.

### Pourquoi ne pas simplement mettre les poids à zéro après le softmax

Mettre à zéro le poids d'une position future *après* que le softmax a déjà été exécuté ne fonctionne pas correctement : les autres poids ont déjà été calculés en supposant que cette position était un vrai concurrent pour la masse de probabilité, et la mettre à zéro ensuite laisse les poids restants avec une somme qui n'est plus égale à 1, ce qui n'est pas une distribution de probabilité valide. Le masquage doit avoir lieu avant le softmax précisément pour que la renormalisation se fasse automatiquement dans le même calcul.

### Pourquoi on ne peut pas non plus mettre simplement le score brut à 0

Mettre à 0 le score brut d'une position future, plutôt qu'à un grand nombre négatif, ne l'exclut pas : `exp(0) = 1`, une contribution parfaitement ordinaire et non négligeable au dénominateur du softmax, qui n'a rien d'une « absence d'attention ». Un score de 0 se lit comme une similarité neutre, moyenne, en concurrence à égalité avec le score réel de toutes les autres positions. Seul un nombre négatif assez grand fait tomber son exponentielle à une valeur pratiquement nulle, ce qui retire correctement cette position de la somme pondérée.

### La forme du masque : un motif triangulaire inférieur fixe

Pour une séquence de longueur *n*, le masque causal est chaque fois le même motif triangulaire inférieur : la position de requête *i* peut porter son attention sur les positions de clé 0 à *i* (incluse), et est masquée pour toutes les positions après *i*. La même forme de masque s'applique à chaque tête d'attention et à chaque exemple d'un batch, ajoutée une seule fois à la matrice des scores avant l'exécution du softmax.

![Une grille 4 par 4 où les lignes sont les positions de requête 0 à 3 et les colonnes les positions de clé 0 à 3. Les cases où la position de clé est inférieure ou égale à la position de requête sont grisées et autorisées. Les cases où la position de clé est supérieure à la position de requête, au-dessus de la diagonale, sont marquées d'une croix orange et masquées avant le softmax. Les cases autorisées forment un motif triangulaire inférieur diagonale comprise.](images/causal-mask-lower-triangular.svg)

## Pratique

1. ▢ Pourquoi l'attention de la position *i* ne doit-elle inclure aucune position *j* supérieure à *i*, étant donné la façon dont le modèle sera réellement utilisé à l'inférence ?

<details markdown="1"><summary>Vérifier</summary>

À l'inférence, le modèle génère un token à la fois en utilisant seulement les tokens qui le précèdent ; les tokens situés après la position courante n'existent pas encore au moment où elle est prédite. Si l'entraînement laissait la position *i* porter son attention sur une position ultérieure *j*, le modèle apprendrait à s'appuyer sur une information qui ne sera jamais disponible au moment de la génération réelle.

</details>

2. ▢ Pourquoi le masque causal s'applique-t-il aux scores bruts avant le softmax, plutôt qu'en mettant à zéro les poids d'attention après l'exécution du softmax ?

<details markdown="1"><summary>Vérifier</summary>

Les poids de sortie du softmax sont calculés ensemble et leur somme vaut 1 sur les scores qu'on lui a donnés. Mettre un poids à zéro après coup laisse les poids restants avec une somme inférieure à 1, ce qui n'est plus une distribution de probabilité valide. Masquer avant le softmax, au contraire, laisse la renormalisation entre les positions restantes, non masquées, se faire automatiquement dans le même calcul.

</details>

3. ▢ Pourquoi mettre le score brut d'une position future à 0 (au lieu d'un grand nombre négatif) ne l'exclut-il pas correctement de l'attention ?

<details markdown="1"><summary>Indice</summary>

Pensez à la valeur de `exp(0)` et à ce que cela signifie pour le dénominateur du softmax.

</details>

<details markdown="1"><summary>Vérifier</summary>

`exp(0) = 1`, une valeur entièrement ordinaire et non négligeable qui reste en concurrence pour la masse de probabilité dans le dénominateur du softmax. Un score de 0 se lit comme une similarité moyenne, neutre, et non comme « exclure cette position ». Seul un nombre négatif suffisamment grand fait tomber son exponentielle pratiquement à zéro, ce qui supprime réellement la contribution de cette position.

</details>

4. ▢ Pour une séquence de 4 tokens (positions 0 à 3), sur quelles positions de clé la position de requête 2 peut-elle porter son attention sous un masque causal ?

<details markdown="1"><summary>Vérifier</summary>

Les positions 0, 1 et 2. La position 3, postérieure à la position 2, est masquée.

</details>

5. ▢ Quelle affirmation est vraie de la façon dont le masquage causal est implémenté ?

    - a) Il met à zéro les poids d'attention après que le softmax les a calculés
    - b) Il ajoute un grand nombre négatif aux scores bruts des positions futures avant le softmax, de sorte que leurs exponentielles deviennent négligeables et que les poids restants se renormalisent automatiquement
    - c) Il ne s'applique qu'à la première tête d'attention, puisque les têtes suivantes n'ont pas besoin de cette restriction
    - d) Mettre à 0 le score d'une position future revient à la masquer

<details markdown="1"><summary>Vérifier</summary>

**b)** C'est exactement le mécanisme, et la raison pour laquelle il doit avoir lieu avant le softmax. (a) est faux : mettre à zéro après le softmax laisse les poids restants avec une somme différente de 1. (c) est faux : le même masque s'applique de façon identique à chaque tête. (d) est faux : un score de 0 contribue encore par un poids ordinaire complet via `exp(0) = 1`, il n'exclut pas du tout la position.

</details>

## Exercices en situation réelle

- [ ] Ajoutez le masquage causal à votre implémentation de la multi-head attention de la leçon 2 : construisez un masque triangulaire inférieur pour une longueur de séquence choisie et ajoutez-le aux scores avant le softmax.
- [ ] Pour une petite séquence, affichez les poids du softmax d'une position de requête avec et sans le masque, et vérifiez que la version masquée met un poids pratiquement nul sur les positions futures.
- [ ] Demain : lisez la section sur le masquage du code de la source primaire à côté de votre propre implémentation, et vérifiez que le masque s'applique au même endroit du calcul (avant le softmax, ajouté aux scores).

## Pour aller plus loin

- [Billet : "The Annotated Transformer", Harvard NLP](http://nlp.seas.harvard.edu/annotated-transformer/)
- [Article : "Attention Is All You Need", Vaswani et al., 2017](https://arxiv.org/abs/1706.03762)
- [Ressources](../RESOURCES.md)

---

Ça ne passe pas ? Relisez la source primaire en haut de page, car cette leçon la condense et c'est dans la condensation que la compréhension s'échappe. Consultez le [glossaire](../GLOSSARY.md) pour tout terme qui vous a paru glissant.

Si c'est la leçon elle-même qui n'est pas claire plutôt que la matière, c'est un défaut : [ouvrez une issue](https://github.com/TokenCemetery/teach/issues).
