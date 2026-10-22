---
title: "12. Parallélisme tensoriel : découper les matrices d'une couche"
description: "Choisir l'axe selon lequel découper une matrice de poids pour qu'un bloc transformer entier n'ait besoin que d'un seul all-reduce"
type: lesson
---

# Leçon 12. Parallélisme tensoriel : découper les matrices d'une couche

**Lien avec la mission :** « Expliquer ce que ZeRO/FSDP partitionnent, pourquoi le parallélisme de données seul manque de mémoire avant de manquer de calcul, et quand le parallélisme tensoriel ou de pipeline vaut son coût de communication » est le quatrième point sous Objectif. Cette leçon couvre ce que le parallélisme tensoriel découpe réellement et pourquoi ; la leçon 13 couvre le parallélisme de pipeline, et la leçon 14 couvre quand l'un ou l'autre vaut son coût.
**Source primaire :** [Article : "Efficient Large-Scale Language Model Training on GPU Clusters Using Megatron-LM", Narayanan et al., 2021](https://arxiv.org/abs/2104.04473)
**Prérequis :** [Leçon 11](0011-activation-memory-and-zero-r.md)

## Échauffement

1. ▢ ZeRO stage 3 partitionne les paramètres au repos mais reconstruit le tenseur complet des paramètres à la demande avant la passe avant ou arrière d'une couche, via all-gather. Une fois les paramètres reconstruits, chaque appareil calcule-t-il la même couche complète, ou chaque appareil calcule-t-il une partie différente des mathématiques de la couche ?

<details markdown="1"><summary>Vérifier</summary>

Chaque appareil calcule la même couche complète, avec sa propre copie complète reconstruite des paramètres de cette couche. ZeRO partitionne l'endroit où les paramètres résident au repos ; il ne répartit pas entre appareils le calcul d'une couche donnée.

</details>

## À savoir

### Découper le calcul, pas seulement l'endroit où vivent les poids

Le **parallélisme tensoriel** adopte une approche différente de tout ce qui figure à l'étape 5 : plutôt que de reconstruire les poids complets d'une couche sur un appareil quelconque, il répartit les matrices de poids d'une couche entre des appareils pour que chaque appareil ne détienne, et ne calcule jamais qu'avec, sa propre tranche de la couche. Aucun appareil n'a jamais besoin de la matrice de poids complète d'un seul coup.

### Un exemple détaillé : le bloc MLP

Le bloc MLP d'un transformer calcule `Y = GeLU(XA)` puis `Z = Dropout(YB)`, deux multiplications matricielles avec une non-linéarité entre elles. Narayanan et al. décrivent la manière précise dont Megatron découpe cela pour réduire la communication au minimum : découper la première matrice de poids `A` **selon ses colonnes**, `A = [A1, A2]`, ce qui donne à chaque appareil une tranche de sortie complète et calculable indépendamment, `Y1 = GeLU(XA1)` et `Y2 = GeLU(XA2)`, sans aucune synchronisation nécessaire entre les deux appareils pour les calculer. Cela fonctionne parce que découper selon les colonnes découpe la dimension de *sortie*, et non la dimension sur laquelle on somme, si bien que la tranche de `Y` de chaque appareil est déjà la vraie réponse complète pour ses colonnes, et que `GeLU`, appliquée élément par élément, peut être appliquée à chaque tranche complète indépendamment.

La seconde matrice de poids, `B`, est ensuite découpée **selon ses lignes** pour s'y accorder, `B = [B1; B2]`, si bien que chaque appareil calcule `Yi @ Bi` en n'utilisant que sa propre tranche locale de `Y` et de `B`. Cela donne à chaque appareil une somme partielle de la vraie sortie `Z` ; les sommes partielles des deux appareils sont combinées par un seul all-reduce, et c'est seulement alors que le dropout s'applique au résultat complet et correct.

### Pourquoi colonne, puis ligne, et pas l'inverse

Si `A` était plutôt découpée selon ses lignes (découper la dimension sur laquelle on somme, plutôt que la dimension de sortie), la tranche de `X @ A` de chaque appareil ne serait qu'une **somme partielle** vers les vraies valeurs de pré-activation, et non une réponse complète, puisque sommer sur une partie seulement de la dimension de contraction ne donne les bons nombres pour aucune colonne de sortie. `GeLU` ne peut pas être appliquée correctement à une somme partielle puis combinée ensuite, parce que `GeLU` est non linéaire : `GeLU(a + b)` n'est pas `GeLU(a) + GeLU(b)`. Découper `A` par colonnes évite d'avoir jamais à appliquer une non-linéarité à une somme partielle, ce qui est exactement la raison que donnent Narayanan et al. pour ce choix. L'appariement colonne puis ligne est ce qui permet au bloc MLP entier à deux matrices de n'avoir besoin que d'**un** seul all-reduce, tout à la fin, au lieu d'une étape de synchronisation supplémentaire entre les deux multiplications matricielles.

### Le même schéma s'applique à l'attention

L'attention multi-têtes a déjà un endroit naturel où se découper : les projections de requête, de clé et de valeur sont partitionnées en parallèle par colonnes, si bien que chaque appareil traite indépendamment un sous-ensemble de têtes d'attention, sans aucune coordination entre appareils pendant le calcul d'attention lui-même. La projection de sortie qui suit est ensuite découpée selon ses lignes pour s'y accorder, le même appariement colonne puis ligne que le bloc MLP, avec un all-reduce à la fin du bloc d'attention.

## Pratique

1. ▢ Le bloc MLP d'un transformer est découpé avec `A` selon ses colonnes et `B` selon ses lignes, comme le décrit cette leçon. De combien d'opérations all-reduce ce schéma a-t-il besoin pour le bloc entier, de `X` jusqu'au `Z` final ?

<details markdown="1"><summary>Vérifier</summary>

Une, juste après la seconde multiplication matricielle, pour combiner la somme partielle de `Z` de chaque appareil en résultat complet. Le découpage de `A` par colonnes évite d'avoir besoin de la moindre synchronisation entre les deux multiplications matricielles.

</details>

2. ▢ Si `A` était découpée selon ses lignes au lieu de ses colonnes, qu'est-ce qui se passerait mal en appliquant `GeLU` immédiatement après la première multiplication matricielle ?

<details markdown="1"><summary>Indice</summary>

Demandez-vous ce que représente réellement le résultat local de chaque appareil quand la dimension sur laquelle on somme est celle qui a été découpée, plutôt que la dimension de sortie.

</details>

<details markdown="1"><summary>Vérifier</summary>

Chaque appareil ne détiendrait qu'une somme partielle vers les vraies valeurs de pré-activation, et non les valeurs complètes, puisqu'une partie seulement de la dimension de contraction serait incluse dans le calcul local de chaque appareil. `GeLU` est non linéaire, donc l'appliquer à une somme partielle puis combiner les résultats ensuite ne donne pas la même réponse que l'appliquer à la somme complète, ce qui signifie qu'une étape de synchronisation serait nécessaire avant que `GeLU` ne puisse même s'exécuter correctement.

</details>

3. ▢ Dans le bloc d'attention, comment les projections de requête, de clé et de valeur sont-elles découpées, et quelle caractéristique naturelle de l'attention multi-têtes rend ce découpage commode ?

<details markdown="1"><summary>Vérifier</summary>

Elles sont découpées en parallèle par colonnes, de la même manière que `A` dans le bloc MLP. L'attention multi-têtes calcule déjà l'attention de chaque tête indépendamment des autres, si bien qu'affecter des têtes différentes (ou des groupes de têtes) à des appareils différents n'exige aucune coordination pendant le calcul d'attention lui-même, comme découper la dimension de sortie du MLP n'en exigeait aucune.

</details>

4. ▢ Pourquoi le parallélisme tensoriel, tel que cette leçon le décrit, n'a-t-il jamais besoin de reconstruire la matrice de poids complète d'une couche sur un seul appareil, contrairement à ZeRO stage 3 ?

<details markdown="1"><summary>Vérifier</summary>

Parce que chaque appareil ne calcule jamais qu'avec sa propre tranche de la matrice de poids ; le découpage colonne puis ligne est choisi précisément pour que chaque calcul intermédiaire sur chaque appareil soit soit un résultat complet et indépendant (après le découpage par colonnes), soit une somme partielle combinée par un all-reduce (après le découpage par lignes), sans exiger que la matrice complète existe quelque part.

</details>

## Exercices en situation réelle

- [ ] Lisez la description du parallélisme tensoriel dans l'article Megatron-LM (lié plus haut), et trouvez la figure qui montre les découpages des blocs MLP et d'attention. Retracez, avec vos propres mots, où se situe chaque opérateur `f` et `g` (la notation de l'article pour la paire identité/all-reduce en passe avant/arrière) dans le schéma.
- [ ] Esquissez sur le papier une matrice de poids `A` de 4 lignes sur 2 colonnes et une entrée `X` de 2 lignes sur 4 colonnes, et calculez à la main à quoi ressemble `X @ A` quand `A` est découpée par colonnes en deux morceaux de 4 lignes sur 1 colonne, par opposition à découpée par lignes en deux morceaux de 2 lignes sur 2 colonnes. Confirmez quel découpage donne à chaque appareil une réponse complète.
- [ ] Demain : sans regarder la suite, écrivez une prédiction d'une phrase pour la leçon 13 : si le parallélisme tensoriel a besoin d'un all-reduce pour chaque couche du transformer, quel genre d'interconnexion cela exigerait-il probablement entre les appareils, et vous attendriez-vous à ce qu'il fonctionne aussi bien entre des appareils situés dans des baies de serveurs physiques différentes ?

## Pour aller plus loin

- [Article : "Efficient Large-Scale Language Model Training on GPU Clusters Using Megatron-LM", Narayanan et al., 2021](https://arxiv.org/abs/2104.04473)
- [Ressources](../RESOURCES.md)

---

Ça ne passe pas ? Relisez la source primaire en haut de page, car cette leçon la condense et c'est dans la condensation que la compréhension s'échappe. Consultez le [glossaire](../GLOSSARY.md) pour tout terme qui vous a paru glissant.

Si c'est la leçon elle-même qui n'est pas claire plutôt que la matière, c'est un défaut : [ouvrez une issue](https://github.com/TokenCemetery/teach/issues).
