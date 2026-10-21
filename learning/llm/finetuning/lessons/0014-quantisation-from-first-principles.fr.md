---
title: "14. La quantification depuis les premiers principes"
description: "Des échelles par bloc, et pourquoi une seule valeur aberrante ruine un tenseur"
type: lesson
---

# Leçon 14. La quantification depuis les premiers principes

**Lien avec la mission :** QLoRA, c'est LoRA plus une idée. Cette leçon est cette idée, enseignée seule pour que la suivante soit courte.
**Source primaire :** [Article : "LLM.int8(): 8-bit Matrix Multiplication for Transformers at Scale", Dettmers et al., arXiv:2208.07339](https://arxiv.org/abs/2208.07339)
**Prérequis :** [Leçon 5](0005-counting-parameters-and-bytes.md), [quantification](../GLOSSARY.md)

## Échauffement

1. ▢ Octets par paramètre en fp32, bf16 et 4 bits ?

<details markdown="1"><summary>Vérifier</summary>

Quatre, deux, et un demi, plus les constantes de quantification dans le cas des 4 bits, ce que cette leçon explique.

</details>

2. ▢ Pour un base model 7B avec un adapter de 20M, où va la mémoire d'entraînement ?

<details markdown="1"><summary>Vérifier</summary>

14 Go de poids de base gelés, ~0.3 Go d'état d'adapter, et des activations qui peuvent dépasser les deux. Le base model gelé est le plus gros terme fixe, et cette étape s'y attaque.

</details>

3. ▢ Pourquoi fusionner dans un base model quantifié fait-il perdre de la qualité ?

<details markdown="1"><summary>Vérifier</summary>

Cela exige de déquantifier, d'ajouter la mise à jour, puis de requantifier. L'étape de requantification jette de l'information.

</details>

## À savoir

La quantification stocke des nombres avec moins de bits que ceux dans lesquels ils ont été entraînés. Rappelez-vous, d'après le [glossaire](../GLOSSARY.md), que dans cet espace de travail elle désigne toujours le **base model gelé**, pas l'adapter.

### Le mécanisme

Pour stocker un tenseur de haute précision dans un petit type entier, il faut une correspondance entre la plage réelle et la plage entière. Deux schémas :

**Symétrique, absmax.** Prendre la plus grande valeur absolue, mettre à l'échelle pour qu'elle tombe sur le maximum entier.

```text
s = absmax(x) / 127          # for int8
q = round(x / s)             # store q, an int8
x̂ = q · s                    # recover, approximately
```

**Asymétrique, affine.** Stocker aussi un décalage de point zéro, pour que la plage n'ait pas à être centrée sur zéro.

```text
s = (max(x) − min(x)) / 255
z = round(−min(x) / s)
q = round(x / s) + z
```

Les distributions de poids dans les transformers sont à peu près symétriques et centrées près de zéro, donc l'absmax symétrique est le choix courant pour les poids.

Dans les deux cas, l'erreur est une **erreur d'arrondi** : chaque valeur se déplace vers le niveau représentable le plus proche. Seize niveaux pour 4 bits, 256 pour 8 bits.

### Le problème des valeurs aberrantes

Voici ce qui fait échouer la quantification naïve sur les transformers. Une seule très grande valeur dans un tenseur fixe `absmax`, qui fixe l'échelle, qui étale tous les niveaux représentables pour couvrir une plage que presque toutes les autres valeurs n'utilisent jamais. Les valeurs typiques s'arrondissent alors toutes vers une poignée de niveaux, et la majeure partie de l'information du tenseur est détruite par une seule valeur aberrante.

Ce n'est pas hypothétique. Les activations des transformers développent des features systématiques de grande amplitude, et cette observation est le cœur du travail LLM.int8() : un petit nombre de dimensions aberrantes portent une importance disproportionnée, et les traiter naïvement détruit la qualité à grande échelle.

### La quantification par blocs, le correctif

Ne quantifiez pas un tenseur entier avec une seule échelle. Découpez-le en petits **blocs** contigus de 64, 128 ou 256 éléments, et donnez à chaque bloc sa propre échelle.

```text
per-tensor:  one absmax  → one outlier ruins everything
per-block:   one absmax per 64 → one outlier ruins 64 values
```

![Deux droites numériques avec les mêmes seize niveaux. Sur la première, l'échelle est fixée par une valeur aberrante, et cinq valeurs typiques s'effondrent sur deux niveaux proches du centre. Sur la seconde, un bloc sans valeur aberrante fixe sa propre échelle et les mêmes cinq valeurs tombent sur cinq niveaux distincts.](images/outlier-sets-the-scale.svg)

Les deux lignes ont seize niveaux, espacés à l'identique. La seule chose qui a changé est la quantité de plage numérique que ces seize niveaux doivent couvrir, et elle est fixée par la plus grande valeur de ce sur quoi l'échelle est calculée. Dépensez la grille sur une plage que les données ne visitent jamais et les données arrivent sur une poignée de niveaux ; dépensez-la sur la plage que les données occupent réellement et chaque valeur garde un niveau bien à elle.

Les dégâts sont contenus. C'est pourquoi la quantification par blocs est standard et la quantification par tenseur ne l'est pas.

Elle a un coût, et ce coût est tout le sujet de la leçon suivante. Chaque bloc a besoin que son échelle soit stockée, et cette échelle est un nombre réel :

```text
4-bit weights, block size 64, fp32 scales:
  weights = 0.5 bytes/param
  scales  = 4 bytes per 64 params = 0.0625 bytes/param
  total   = 0.5625 bytes/param, i.e. 4.5 bits, not 4
```

Douze pour cent de surcoût au-dessus d'un budget de 4 bits, uniquement pour la comptabilité. Retenez ce chiffre.

### Précision de stockage contre précision de calcul

Un poids quantifié n'est pas utilisé sous sa forme quantifiée. La passe avant **déquantifie un bloc en bf16, fait la multiplication de matrices, et jette la copie déquantifiée.**

```text
stored:   4-bit + per-block scale
computed: bf16
```

La quantification achète donc de la mémoire, et coûte du calcul : une étape de déquantification par bloc, par passe avant. Que l'effet net soit plus rapide ou plus lent dépend entièrement de si vous étiez limité par la mémoire ou par le calcul, et de la qualité d'optimisation du kernel de déquantification pour le matériel que vous utilisez.

C'est là que le matériel entre réellement en jeu. L'*arithmétique* est identique partout. Ce qui diffère selon le backend, c'est l'existence d'un kernel fusionné et optimisé pour une largeur de bits et une taille de bloc données, ou le repli de la bibliothèque sur un chemin générique plus lent. La leçon 16 donne le tableau actuel.

### À quoi sert la quantification, ici

Deux usages qu'il ne faut pas confondre :

**La quantification pour l'inférence** réduit un modèle pour qu'il tienne et se serve à peu de frais. Les poids sont quantifiés et c'est l'artefact que vous livrez. Cela sort du périmètre de cet espace de travail comme sujet à part entière.

**La quantification pour l'entraînement**, ce que fait QLoRA, réduit le *base model gelé* pour que l'entraînement de l'adapter tienne. L'adapter reste à plus haute précision, et l'artefact que vous livrez peut ensuite être fusionné dans un base model en pleine précision. La précision du base model est une décision de budget au moment de l'entraînement, pas une propriété du résultat.

## Pratique

1. ▢ Quantifiez les valeurs `[0.1, −0.3, 0.2, 8.0]` en int8 avec l'absmax symétrique. Qu'arrive-t-il aux trois premières ?

<details markdown="1"><summary>Vérifier</summary>

`absmax = 8.0`, donc `s = 8.0/127 ≈ 0.063`. Les valeurs correspondent à `round(0.1/0.063) = 2`, `round(−0.3/0.063) = −5`, `round(0.2/0.063) = 3`, et `127`.

Valeurs retrouvées : 0.126, −0.315, 0.189, 8.0. Les petites valeurs portent maintenant une erreur relative substantielle, parce qu'une seule valeur aberrante a consommé la plage. En 4 bits, avec seize niveaux, les trois premières s'effondreraient presque sur la même valeur.

</details>

2. ▢ Pourquoi la quantification par blocs aide-t-elle, et que coûte-t-elle ?

<details markdown="1"><summary>Vérifier</summary>

Une valeur aberrante ne fixe l'échelle que pour son propre bloc, donc elle abîme 64 valeurs au lieu du tenseur entier.

Le coût est de stocker une échelle par bloc. Avec des blocs de 64 et des échelles en fp32, cela fait 0.0625 octet par paramètre, soit environ 12 % de surcoût sur un budget de 4 bits.

</details>

3. ▢ Total d'octets par paramètre pour des poids en 4 bits, blocs de 128, échelles en fp32 ?

<details markdown="1"><summary>Vérifier</summary>

0.5 + 4/128 = 0.5 + 0.03125 = 0.53125 octet, soit 4.25 bits.

Des blocs plus grands signifient moins de surcoût d'échelles et un moins bon confinement des valeurs aberrantes. C'est le compromis que fixe la taille de bloc.

</details>

4. ▢ Dans une passe avant quantifiée, dans quelle précision la multiplication de matrices est-elle faite ?

<details markdown="1"><summary>Vérifier</summary>

Une précision plus élevée, typiquement bf16. Chaque bloc est déquantifié en bf16, multiplié, et la copie déquantifiée est jetée.

La quantification est une décision de *stockage*. La précision de calcul est distincte et se configure séparément.

</details>

5. ▢ Pourquoi la quantification des transformers est-elle plus difficile qu'il n'y paraît d'après la seule arithmétique ?

<details markdown="1"><summary>Vérifier</summary>

À cause des features aberrantes systématiques. Quelques dimensions portent de très grandes amplitudes et une importance disproportionnée, donc un schéma qui traite toutes les valeurs comme interchangeables, avec une seule échelle par tenseur, détruit les valeurs ordinaires tout en préservant les valeurs aberrantes.

La quantification par blocs, et dans le cas de LLM.int8() la séparation des dimensions aberrantes dans une précision plus haute, en est la réponse.

</details>

6. ▢ Distinguez la quantification pour l'inférence de la quantification pour l'entraînement.

<details markdown="1"><summary>Vérifier</summary>

Pour l'inférence, les poids quantifiés *sont* l'artefact : vous les livrez, et le coût en qualité est permanent.

Pour l'entraînement, quantifier le base model gelé est une décision de budget mémoire. L'adapter reste en haute précision, et le résultat livré peut être fusionné dans un base model en pleine précision, donc le coût de la quantification n'a pas besoin de survivre dans l'artefact.

</details>

## Exercices en situation réelle

- [ ] Implémentez à la main, en quelques lignes, la quantification et la déquantification int8 par absmax d'un tenseur. Mesurez l'erreur maximale et moyenne.
- [ ] Insérez une grande valeur aberrante et mesurez de nouveau l'erreur. Puis refaites-le par blocs de taille 64 et comparez.
- [ ] Demain : calculez le véritable nombre d'octets par paramètre en 4 bits pour des tailles de bloc de 32, 64, 128 et 256, et notez à partir d'où le surcoût devient négligeable.

## Pour aller plus loin

- [Article : "LLM.int8(): 8-bit Matrix Multiplication for Transformers at Scale", Dettmers et al., arXiv:2208.07339](https://arxiv.org/abs/2208.07339)
- [Article : "8-bit Optimizers via Block-wise Quantization", Dettmers et al., arXiv:2110.02861](https://arxiv.org/abs/2110.02861)
- [Leçon 15. NF4 et double quantification](0015-nf4-and-double-quantisation.md)

---

Ça ne passe pas ? Relisez la source primaire en haut de page, car cette leçon la condense et c'est dans la condensation que la compréhension s'échappe. Consultez le [glossaire](../GLOSSARY.md) pour tout terme qui vous a paru glissant.

Si c'est la leçon elle-même qui n'est pas claire plutôt que la matière, c'est un défaut : [ouvrez une issue](https://github.com/TokenCemetery/teach/issues).
