---
title: "4. Index ANN : HNSW et IVF"
description: "Pourquoi la recherche vectorielle sacrifie l'exactitude à la vitesse, et comment IVF et HNSW exposent chacun ce compromis sous forme d'un réglage ajustable"
type: lesson
---

# Leçon 4. Index ANN : HNSW et IVF

**Lien avec la mission :** L'étape 3 ouvre la partie de la mission où la cible bouge, mettre en place une recherche sur un vrai corpus : un index est ce qui rend la recherche vectorielle assez rapide pour être exécutée, au prix d'un compromis entre recall et latence que cette leçon nomme avant que la leçon 5 ne le rende concret dans pgvector.
**Source primaire :** [Article : "Efficient and Robust Approximate Nearest Neighbor Search Using Hierarchical Navigable Small World Graphs", Malkov and Yashunin, 2018](https://arxiv.org/abs/1603.09320)
**Prérequis :** [Leçon 3](0003-embedding-dimensionality.md), [Chunk](../GLOSSARY.md)

## Échauffement

1. ▢ Un corpus compte 2 millions de chunks. Quel stockage représente approximativement un embedding à 1536 dimensions en float32, comparé à 256 dimensions ?

<details markdown="1"><summary>Vérifier</summary>

Environ 12,3 Go à 1536 dimensions contre environ 2,0 Go à 256 dimensions, puisque le nombre d'octets par vecteur croît linéairement avec le nombre de dimensions (`dimensions × 4 bytes`).

</details>

2. ▢ Que permet Matryoshka Representation Learning de faire à un vecteur d'embedding qu'un modèle d'embedding standard ne permet pas de faire sans risque ?

<details markdown="1"><summary>Vérifier</summary>

Le tronquer à moins de dimensions après l'entraînement, avec un coût de qualité borné et prévisible, puisque les préfixes d'un modèle entraîné avec MRL sont eux-mêmes des embeddings significatifs. Les dimensions d'un modèle standard ne sont pas ordonnées par importance, donc en tronquer un est imprévisible.

</details>

## À savoir

### Pourquoi la recherche exacte ne passe pas à l'échelle

Trouver exactement les vrais plus proches voisins d'une requête revient à la comparer à chaque vecteur du corpus. C'est linéaire en la taille du corpus : doubler le corpus double le temps de recherche, et avec des millions de chunks, la comparaison par force brute devient trop lente pour être exécutée au moment de la requête. Un index de **plus proches voisins approximatifs (ANN)** accepte une petite part d'inexactitude contrôlable, en renvoyant des vecteurs très probablement proches des vrais plus proches voisins, sans garantie que ce soient exactement eux, en échange de temps de recherche qui ne croissent pas linéairement avec la taille du corpus.

### IVF : ne chercher que dans les clusters proches

**IVF (inverted file index)** partitionne l'espace vectoriel en clusters à l'avance (couramment par k-means), en affectant chaque vecteur au centroïde de cluster le plus proche. Au moment de la requête, au lieu de balayer chaque vecteur, IVF ne cherche que dans les `nprobe` clusters les plus proches de la requête, où `nprobe` est un nombre ajustable. Un `nprobe` faible (ne chercher que dans le cluster le plus proche) est rapide mais risque de rater de vrais voisins qui se trouvent dans un cluster voisin près de la frontière. Un `nprobe` élevé (chercher dans beaucoup de clusters, voire tous) approche le recall de la recherche exacte au coût de la recherche exacte. IVF comporte aussi un coût de construction ponctuel : l'étape de clustering a besoin d'un échantillon représentatif des vecteurs du corpus pour bien placer les centroïdes.

### HNSW : un graphe navigable, parcouru de haut en bas

**HNSW (hierarchical navigable small world)** construit un graphe multicouche au lieu de clusters : chaque vecteur est un nœud, relié à d'autres vecteurs proches par des arêtes, avec des couches plus clairsemées au sommet qui permettent de grands sauts à travers l'espace vectoriel et une couche dense en bas qui permet une recherche locale précise. Une requête part de la couche clairsemée du sommet, saute goulûment vers le nœud connecté le plus proche, et descend couche par couche en affinant sa position jusqu'à atteindre la couche dense du bas. Le réglage ajustable ici est `ef_search`, le nombre de candidats que la recherche suit à chaque étape : un `ef_search` faible trouve une réponse vite mais peut se contenter d'un nœud localement bon qui n'est pas le vrai plus proche ; un `ef_search` élevé explore plus de candidats, en échangeant de la vitesse contre du recall, le même type de compromis que `nprobe` fait pour IVF.

![Deux panneaux. À gauche, IVF : quatre clusters de vecteurs, chacun avec un centroïde. La requête se trouve entre deux clusters proches, grisés et parcourus, tandis que deux clusters plus éloignés restent non grisés et sont ignorés, un nprobe faible ne parcourant que les clusters proches. À droite, HNSW : trois couches de graphe empilées, clairsemée en haut et dense en bas, avec un chemin qui descend depuis un point d'entrée dans la couche du haut, saute vers des nœuds de plus en plus proches à chaque couche, en affinant sa position jusqu'à atteindre le plus proche voisin dans la couche dense du bas.](images/ivf-vs-hnsw.svg)

### La forme générale : une courbe recall/latence, pas une unique bonne réponse

Les deux index exposent un réglage (`nprobe` pour IVF, `ef_search` pour HNSW) qui place un point précis sur une courbe recall contre latence pour un corpus et un index donnés. HNSW atteint généralement un meilleur point de cette courbe qu'IVF, un recall plus élevé pour la même latence, au prix de plus de mémoire (la structure de graphe elle-même) et d'une construction d'index plus lente. Aucun des deux index n'a de réglage universellement correct : le bon point dépend du budget de latence de la charge de travail et de la perte de recall qu'une étape ultérieure, comme le reranking, peut absorber sans que le résultat final en souffre, ce que les métriques de récupération de l'étape 6 existent justement pour mesurer plutôt que supposer.

## Pratique

1. ▢ Pourquoi la recherche exacte de plus proches voisins par force brute ne passe-t-elle pas à l'échelle pour un corpus de millions de vecteurs, et que sacrifie un index ANN pour y remédier ?

<details markdown="1"><summary>Vérifier</summary>

La recherche exacte compare la requête à chaque vecteur, donc son coût croît linéairement avec la taille du corpus et devient trop lent à des millions de vecteurs. Un index ANN renonce à la garantie de trouver exactement les vrais plus proches voisins, en acceptant une petite probabilité contrôlable d'en rater un, en échange de temps de recherche qui ne croissent pas de la même façon.

</details>

2. ▢ Pour un index IVF, décrivez ce qui se passe à chaque extrémité du paramètre `nprobe` : `nprobe = 1` contre `nprobe` réglé pour chercher dans tous les clusters.

<details markdown="1"><summary>Vérifier</summary>

`nprobe = 1` ne cherche que dans le cluster le plus proche : le plus rapide, mais il peut rater un vrai plus proche voisin situé dans un cluster voisin près de la frontière, surtout si la requête tombe près du bord d'un cluster. `nprobe` réglé pour chercher dans tous les clusters approche la recherche exacte : le recall le plus élevé, mais au coût de la recherche exacte, puisqu'il n'ignore plus l'essentiel du corpus.

</details>

3. ▢ En quoi le paramètre `ef_search` de HNSW joue-t-il pour HNSW le même rôle que `nprobe` pour IVF ?

<details markdown="1"><summary>Indice</summary>

Réfléchissez à ce que contrôle chaque paramètre : la part de l'index examinée avant de renvoyer une réponse.

</details>

<details markdown="1"><summary>Vérifier</summary>

`ef_search` contrôle le nombre de candidats que la recherche dans le graphe suit à chaque étape de la descente à travers les couches de HNSW. Une valeur faible explore moins de candidats, trouve une réponse vite mais risque de se contenter d'un nœud qui n'est pas le vrai plus proche. Une valeur élevée explore plus de candidats, en échangeant de la vitesse de recherche contre un meilleur recall, la même forme de compromis recall contre latence que `nprobe` donne à IVF.

</details>

4. ▢ Quel est le compromis général entre choisir HNSW et choisir IVF pour un corpus donné ?

<details markdown="1"><summary>Vérifier</summary>

HNSW atteint typiquement un meilleur point de recall pour une latence donnée qu'IVF, mais coûte plus de mémoire (les arêtes du graphe ajoutent un vrai surcoût en plus du stockage des vecteurs) et met plus de temps à construire l'index au départ. IVF est moins coûteux à construire et à stocker mais doit généralement chercher dans une plus grande fraction du corpus pour égaler le recall de HNSW à la même latence.

</details>

5. ▢ Laquelle de ces affirmations est vraie à propos du réglage du paramètre de recherche d'un index ANN (`nprobe` ou `ef_search`) ?

    - a) Il existe un réglage universellement correct qui convient à n'importe quel corpus et à n'importe quelle charge de travail
    - b) Le bon réglage est un point sur une courbe recall/latence, à choisir en fonction du budget de latence réel de la charge de travail et de sa tolérance à la perte de recall
    - c) Régler le paramètre le plus haut possible est toujours le bon choix, puisque la latence n'a plus d'importance une fois l'index créé
    - d) Le paramètre n'affecte que le temps de construction de l'index, pas le comportement au moment de la requête

<details markdown="1"><summary>Vérifier</summary>

**b)** Les deux paramètres arbitrent le recall contre la latence au moment de la requête, et le bon point dépend de ce dont la charge de travail a réellement besoin, ce que l'étape 6 mesure au lieu de le supposer. (a) est fausse : c'est exactement ce qu'exclut la courbe recall/latence. (c) est fausse : un réglage plus haut coûte plus de latence à la requête, ce qui compte dès qu'il y a un budget de latence à respecter. (d) est fausse : `nprobe` comme `ef_search` sont des paramètres de recherche, pas de construction.

</details>

## Exercices en situation réelle

- [ ] Trouvez le type d'index (IVF ou HNSW) que votre base vectorielle utilise ou qu'elle prend par défaut, et repérez dans sa documentation son paramètre de recall/latence au moment de la recherche.
- [ ] Si vous pouvez exécuter des requêtes sur un index, essayez deux valeurs différentes de `nprobe` ou de `ef_search` et observez l'écart de latence des requêtes.
- [ ] Demain : lisez un paragraphe de la description de la structure en couches dans l'article sur HNSW et notez, avec vos propres mots, pourquoi la couche du haut doit être clairsemée pour que les sauts à longue portée fonctionnent.

## Pour aller plus loin

- [Article : "Efficient and Robust Approximate Nearest Neighbor Search Using Hierarchical Navigable Small World Graphs", Malkov and Yashunin, 2018](https://arxiv.org/abs/1603.09320)
- [Dépôt : pgvector, pgvector](https://github.com/pgvector/pgvector)
- [Ressources](../RESOURCES.md)

---

Ça ne passe pas ? Relisez la source primaire en haut de page, car cette leçon la condense et c'est dans la condensation que la compréhension s'échappe. Consultez le [glossaire](../GLOSSARY.md) pour tout terme qui vous a paru glissant.

Si c'est la leçon elle-même qui n'est pas claire plutôt que la matière, c'est un défaut : [ouvrez une issue](https://github.com/TokenCemetery/teach/issues).
