---
title: "4. Encodage positionnel"
description: "Pourquoi l'attention est aveugle à l'ordre à elle seule, et comment l'encodage sinusoïdal donne à chaque position une signature distinguable"
type: lesson
---

# Leçon 4. Encodage positionnel

**Lien avec la mission :** L'étape 2 ouvre les pièces qui entourent l'attention (leçons 1 à 3) pour en faire un bloc transformer complet ; l'encodage positionnel est la première d'entre elles, et sans lui l'attention serait aveugle à la seule chose dont le langage dépend le plus : l'ordre.
**Source primaire :** [Article : "Attention Is All You Need", Vaswani et al., 2017](https://arxiv.org/abs/1706.03762)
**Prérequis :** [Leçon 3](0003-causal-masking.md), [Scaled dot-product attention](../GLOSSARY.md)

## Échauffement

1. ▢ Pourquoi le masque causal s'applique-t-il aux scores bruts avant le softmax, plutôt qu'en mettant à zéro les poids après l'exécution du softmax ?

<details markdown="1"><summary>Vérifier</summary>

Les poids du softmax sont calculés ensemble et leur somme vaut déjà 1 ; en mettre un à zéro ensuite laisse les autres avec une somme qui n'est plus égale à 1. Masquer avant le softmax laisse les poids restants, non masqués, se renormaliser automatiquement dans le même calcul.

</details>

2. ▢ Écrivez de mémoire l'équation de la scaled dot-product attention.

<details markdown="1"><summary>Vérifier</summary>

`Attention(Q, K, V) = softmax(QK^T / sqrt(d_k)) V`.

</details>

## À savoir

### L'attention n'a aucune notion d'ordre intégrée

La scaled dot-product attention calcule sa sortie à partir de produits scalaires entre requêtes et clés et de sommes pondérées sur les valeurs ; rien dans ce calcul ne fait référence à l'endroit où se trouve un token dans la séquence. Échangez les positions de deux tokens d'entrée (et, en conséquence, les lignes de `Q`, `K` et `V` qui en proviennent), et la sortie d'attention de toutes les autres positions est identique, simplement réétiquetée pour suivre l'échange : les relations et les poids fondés sur le contenu que produit le calcul ne changent pas du tout. L'attention traite son entrée comme un ensemble non ordonné de vecteurs, pas comme une séquence, alors que le langage n'est manifestement pas indépendant de l'ordre : « le chien mord l'homme » et « l'homme mord le chien » partagent tous leurs mots et signifient des choses entièrement différentes.

### La position doit être inscrite dans les vecteurs eux-mêmes

L'équation de l'attention ne voit jamais que `Q`, `K` et `V` ; il n'y a pas de canal annexe pour dire « au fait, voici la position d'où vient chacun de ceux-ci ». L'attention ne devient sensible à la position que si celle-ci est déjà encodée dans les vecteurs qui produisent `Q`, `K` et `V` au départ, c'est-à-dire dans les embeddings de tokens, avant même qu'ils atteignent le calcul d'attention. Un vecteur d'**encodage positionnel** (positional encoding), ajouté à l'embedding de chaque token, donne à deux tokens portant le même mot mais situés à des positions différentes des embeddings numériquement distinguables, ce qui rend les produits scalaires de l'attention implicitement sensibles à la position.

### Encodage sinusoïdal : une signature unique et structurée par position

Le choix de l'article d'origine construit l'encodage de chaque position à partir de fonctions sinus et cosinus à différentes fréquences, une paire de dimensions par fréquence :

```text
PE(pos, 2i)   = sin(pos / 10000^(2i / d_model))
PE(pos, 2i+1) = cos(pos / 10000^(2i / d_model))
```

Les paires de dimensions d'indice faible (petit `i`) oscillent lentement d'une position à l'autre (grande longueur d'onde) ; celles d'indice élevé oscillent vite (courte longueur d'onde). Chaque position reçoit une combinaison unique sur toutes ces fréquences et, point crucial, un décalage fixe entre deux positions peut s'exprimer comme une fonction linéaire de l'encodage de l'une d'elles (puisque `sin` et `cos` d'une somme se décomposent en combinaisons linéaires de `sin` et `cos` des parties). Cette structure explique en partie pourquoi l'article soutient que ce schéma peut se généraliser à la position relative, et potentiellement à des longueurs de séquence jamais vues pendant l'entraînement, au lieu de mémoriser seulement un ensemble fixe de positions absolues.

![Deux ondes tracées en fonction de la position sur l'axe horizontal. L'onde du haut, issue d'une paire de dimensions d'indice faible, accomplit une seule oscillation lente sur toute la plage de positions affichée. L'onde du bas, issue d'une paire de dimensions d'indice élevé, accomplit huit oscillations rapides sur la même plage. Chaque position reçoit une combinaison unique de valeurs sur toutes ces ondes de fréquences différentes, ce qui donne à chaque position une signature distinguable.](images/sinusoidal-frequency-pairs.svg)

### L'alternative plus simple : un embedding de position appris

Au lieu d'une formule fixe, une position peut être encodée avec une table d'embeddings apprise ordinaire, indexée par la position comme une table d'embeddings de tokens est indexée par le vocabulaire, et entraînée par descente de gradient comme n'importe quel autre paramètre. C'est plus simple à implémenter et cela n'exige aucun raisonnement sur les fréquences, mais il n'y a aucune formule sur laquelle se rabattre pour une position au-delà de ce pour quoi la table a été dimensionnée pendant l'entraînement : il n'y a pas de ligne dans la table pour une position que le modèle n'a jamais vue, alors que la formule de l'encodage sinusoïdal peut toujours être évaluée à n'importe quelle position.

## Pratique

1. ▢ Deux tokens d'entrée voient leurs positions échangées (et leurs lignes correspondantes dans `Q`, `K`, `V` aussi). Que devient la sortie d'attention d'une troisième position qui interroge les deux ?

<details markdown="1"><summary>Vérifier</summary>

Rien ne change dans les poids fondés sur le contenu ni dans la sortie calculée ; le résultat est simplement réétiqueté pour suivre la position physique que les tokens échangés occupent désormais. Cela illustre l'invariance de l'attention par permutation : elle calcule des relations à partir du contenu (les produits scalaires), sans aucune référence à la position.

</details>

2. ▢ Pourquoi la position doit-elle être encodée dans les embeddings de tokens eux-mêmes, plutôt que transmise au calcul d'attention comme un signal séparé à côté de `Q`, `K` et `V` ?

<details markdown="1"><summary>Vérifier</summary>

L'équation de l'attention n'opère que sur `Q`, `K` et `V` ; il n'y a aucune entrée supplémentaire par laquelle l'information de position puisse entrer. Le calcul ne peut devenir sensible à la position que si celle-ci est déjà inscrite dans les vecteurs qui produisent `Q`, `K` et `V` avant l'exécution de l'attention.

</details>

3. ▢ Décrivez la structure de fréquences des paires de dimensions de l'encodage positionnel sinusoïdal, et ce qu'elle apporte par rapport à l'usage direct de l'entier brut de la position.

<details markdown="1"><summary>Indice</summary>

Pensez à ce que fait varier la fréquence d'une paire de dimensions à l'autre, qu'un seul nombre brut ne pourrait pas faire.

</details>

<details markdown="1"><summary>Vérifier</summary>

Les différentes paires de dimensions oscillent à des fréquences différentes, de lente (indice faible) à rapide (indice élevé) d'une position à l'autre, ce qui donne à chaque position une combinaison unique de valeurs sur toutes les fréquences plutôt qu'un seul scalaire brut. Cet encodage structuré à plusieurs fréquences est aussi ce qui permet d'exprimer un décalage de position fixe comme une fonction linéaire de l'encodage d'une autre position, propriété qu'un simple entier brut n'aurait pas sous une forme que les opérations linéaires de l'attention puissent exploiter aussi directement.

</details>

4. ▢ Pourquoi l'encodage positionnel sinusoïdal peut-il être évalué pour une longueur de séquence supérieure à tout ce qui a été vu pendant l'entraînement, alors qu'une table d'embeddings de position apprise ne le peut pas ?

<details markdown="1"><summary>Vérifier</summary>

L'encodage sinusoïdal est une formule, évaluable à n'importe quelle valeur de position, y compris celles jamais rencontrées pendant l'entraînement. Une table d'embeddings apprise n'a de lignes que pour les positions pour lesquelles elle a été dimensionnée et entraînée ; une position au-delà de cette plage n'a aucune ligne correspondante à consulter.

</details>

5. ▢ Quelle affirmation est vraie sur la raison d'être de l'encodage positionnel ?

    - a) Les produits scalaires de l'attention tiennent déjà compte de la position relative sans aucune entrée supplémentaire
    - b) L'attention traite son entrée comme un ensemble non ordonné, donc la position doit être injectée dans les embeddings pour que le modèle soit sensible à l'ordre des mots
    - c) L'encodage positionnel n'est nécessaire que pour les très longues séquences, pas pour les courtes
    - d) Un embedding de position appris se généralise mieux aux longueurs de séquence inconnues que l'encodage sinusoïdal

<details markdown="1"><summary>Vérifier</summary>

**b)** C'est toute la raison d'être de l'encodage positionnel. (a) est faux : l'équation de l'attention ne fait aucune référence à la position par elle-même. (c) est faux : même le sens d'une séquence courte dépend de l'ordre des mots, donc la même cécité s'applique quelle que soit la longueur. (d) est faux : c'est l'inverse, la formule de l'encodage sinusoïdal peut être évaluée à n'importe quelle position, alors qu'une table apprise est limitée à ce sur quoi elle a été entraînée.

</details>

## Exercices en situation réelle

- [ ] Implémentez l'encodage positionnel sinusoïdal à partir de la formule pour un petit `d_model`, et tracez ou affichez les vecteurs d'encodage de quelques positions pour voir les différentes fréquences d'oscillation d'une paire de dimensions à l'autre.
- [ ] Ajoutez votre encodage positionnel à un ensemble d'embeddings de tokens et vérifiez que le même token à deux positions différentes produit désormais des vecteurs numériquement différents.
- [ ] Demain : lisez en entier la section « Positional Encoding » de l'article de la source primaire, et confrontez l'affirmation sur la généralisation à des séquences plus longues à ce que produirait réellement votre propre implémentation au-delà de sa plage d'entraînement.

## Pour aller plus loin

- [Article : "Attention Is All You Need", Vaswani et al., 2017](https://arxiv.org/abs/1706.03762)
- [Billet : "The Illustrated Transformer", Jay Alammar](https://jalammar.github.io/illustrated-transformer/)
- [Ressources](../RESOURCES.md)

---

Ça ne passe pas ? Relisez la source primaire en haut de page, car cette leçon la condense et c'est dans la condensation que la compréhension s'échappe. Consultez le [glossaire](../GLOSSARY.md) pour tout terme qui vous a paru glissant.

Si c'est la leçon elle-même qui n'est pas claire plutôt que la matière, c'est un défaut : [ouvrez une issue](https://github.com/TokenCemetery/teach/issues).
