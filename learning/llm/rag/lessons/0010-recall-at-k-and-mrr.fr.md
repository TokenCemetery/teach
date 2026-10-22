---
title: "10. Recall@k et MRR"
description: "Les deux métriques de récupération standard, ce que chacune vous apprend que l'autre ne dit pas, et comment choisir k pour la charge de travail"
type: lesson
---

# Leçon 10. Recall@k et MRR

**Lien avec la mission :** L'étape 6 ouvre la moitié « mesurer, ne pas supposer » de la mission de cet espace de travail : les décisions de chaque étape précédente (chunking, embeddings, indexation, poids hybrides, reranking) ont été présentées comme des choses à mesurer, et cette leçon donne les deux chiffres standard pour les mesurer.
**Source primaire :** [Billet : "Evaluation Measures for Search and Recommender Systems", Pinecone](https://www.pinecone.io/learn/offline-evaluation/)
**Prérequis :** [Leçon 9](0009-when-reranking-earns-its-cost.md), [Chunk](../GLOSSARY.md)

## Échauffement

1. ▢ Comment une équipe doit-elle décider si le reranking justifie son coût pour sa charge de travail précise ?

<details markdown="1"><summary>Vérifier</summary>

Mesurer la qualité de la récupération sans puis avec reranking sur le même jeu de requêtes, mesurer séparément la latence ajoutée à la taille d'ensemble de candidats utilisée, et comparer les deux au budget de latence et au seuil de qualité réels de la charge de travail, plutôt que de supposer que le reranking aide toujours ou jamais.

</details>

2. ▢ Dans la reciprocal rank fusion, que fait la constante `k` au classement fusionné ?

<details markdown="1"><summary>Vérifier</summary>

Elle amortit l'influence des tout premiers rangs : un `k` plus petit rend le score plus sensible aux petites différences de rang près du sommet, alors qu'un `k` plus grand (couramment 60) rend ces différences moins importantes.

</details>

## À savoir

### Recall@k : le bon document est-il passé le cap

**Recall@k** demande, sur un ensemble de requêtes de test dont les documents pertinents sont connus, quelle fraction d'entre elles a vu un document pertinent apparaître quelque part parmi les *k* premiers résultats récupérés. C'est une question de budget : si le système en aval ne regarde jamais que les *k* premiers résultats, recall@k vous dit à quelle fréquence le système lui a même donné une chance de trouver la bonne réponse. Recall@k augmente avec *k* (un document pertinent au rang 50 compte pour recall@100 mais pas pour recall@10), et il traite toutes les positions parmi les *k* premières de façon identique : un document pertinent au rang 1 et un autre au rang *k* comptent tous deux comme un succès, sans aucun crédit pour être arrivé plus haut.

### MRR : à quelle vitesse le bon document est apparu

Le **mean reciprocal rank (MRR)** corrige exactement ce que recall@k ne voit pas. Pour chaque requête, on prend l'inverse de la position du premier résultat pertinent (`1/rank`), puis on moyenne cet inverse sur toutes les requêtes. Un résultat pertinent au rang 1 contribue 1,0 entier à la moyenne ; le même résultat pertinent au rang 10 ne contribue que 0,1. MRR récompense le fait de classer la bonne réponse le plus haut possible, et pas seulement de l'avoir dans une limite donnée, ce qui est exactement l'information que recall@k jette en traitant de la même façon chaque position parmi les *k* premières.

### Un exemple détaillé

Quatre requêtes de test, chacune avec un document pertinent connu, et son rang dans les résultats de chaque système : 1, 3, 1, 8.

```text
recall@1: ranks ≤ 1 are queries 1 and 3 → 2/4 = 0.50
recall@5: ranks ≤ 5 are queries 1, 2, and 3 (ranks 1, 3, 1); query 4 (rank 8) misses → 3/4 = 0.75
MRR: (1/1 + 1/3 + 1/1 + 1/8) / 4 = (1.000 + 0.333 + 1.000 + 0.125) / 4 ≈ 0.615
```

recall@5 dit que trois requêtes sur quatre trouveraient leur réponse si le système ne regardait que ses 5 premiers résultats. Le 0,615 du MRR reflète que la plupart de ces succès sont arrivés au rang 1, avec un succès plus faible au rang 3 et un échec qui tire la moyenne vers le bas.

![Quatre requêtes placées sur un axe de rangs commun de 1 à 9, au rang de leur premier résultat pertinent : 1, 3, 1 et 8. Une ligne pointillée marque la limite de recall à 5. Les succès des trois premières requêtes tombent à gauche de la limite et comptent pour le recall à 5, tandis que la quatrième, au rang 8, tombe à droite et est un échec. Le rang réciproque de chaque requête est indiqué à côté : 1,000, 0,333, 1,000 et 0,125. Le recall à 5 vaut 3 sur 4, soit 0,75, alors que la moyenne des rangs réciproques donne un MRR d'environ 0,615, tiré vers le bas par la distance à droite du rang de cet unique échec, ce que le recall à 5 ne peut pas voir du tout.](images/recall-at-k-vs-mrr.svg)

### Choisir k, et choisir entre les métriques

Le bon *k* pour recall@k n'est pas une valeur par défaut ; c'est ce que le système en aval utilise réellement. Si seuls les 5 premiers chunks sont transmis à la génération, recall@100 mesure quelque chose que le pipeline n'exploite jamais réellement ; recall@5 est le chiffre qui reflète la réalité. MRR est le plus informatif quand seul le tout premier résultat compte beaucoup (une seule meilleure réponse présentée à un utilisateur), puisqu'il récompense spécifiquement le rang 1 bien plus que le rang 10. Recall@k est plus informatif quand plusieurs résultats dans un budget sont tous réellement exploitables (la génération peut puiser dans plusieurs des chunks parmi les k premiers, pas seulement le tout premier). Rapporter les deux, au *k* que le pipeline utilise réellement, donne un tableau plus complet que l'un ou l'autre seul.

## Pratique

1. ▢ Avec l'exemple à quatre requêtes de cette leçon (rangs 1, 3, 1, 8), calculez recall@3.

<details markdown="1"><summary>Indice</summary>

Comptez combien des quatre rangs valent 3 ou moins.

</details>

<details markdown="1"><summary>Vérifier</summary>

Les rangs 1, 3 et 1 sont tous ≤ 3 ; le rang 8 ne l'est pas. `recall@3 = 3/4 = 0.75`, comme recall@5 dans cet exemple, puisqu'aucun document pertinent de requête n'est tombé au rang 4 ou 5.

</details>

2. ▢ Pourquoi recall@k seul ne distingue-t-il pas un système qui classe toujours le document pertinent 1er d'un système qui le classe toujours exactement à la position `k` ?

<details markdown="1"><summary>Vérifier</summary>

Recall@k vérifie seulement si un document pertinent apparaît quelque part parmi les k premières positions ; il n'enregistre pas à quelle position de cette plage il est tombé. Un succès au rang 1 et un succès au rang k comptent de façon identique pour recall@k, donc la métrique ne peut pas distinguer les deux systèmes alors que l'un classe clairement mieux.

</details>

3. ▢ Pourquoi MRR distingue-t-il ces deux systèmes, là où recall@k ne le pouvait pas ?

<details markdown="1"><summary>Vérifier</summary>

MRR utilise l'inverse de la position exacte dans le classement, pas seulement le fait qu'elle tombe sous une limite. Un système qui classe toujours le document pertinent 1er obtient à chaque fois un rang réciproque de 1,0, ce qui lui donne un MRR de 1,0 ; un système qui le classe toujours à la position k obtient à chaque fois un rang réciproque de `1/k`, ce qui lui donne un MRR bien plus bas dès que k est supérieur à 1. La position exacte compte pour MRR d'une façon qui n'a jamais compté pour recall@k.

</details>

4. ▢ L'étape de génération d'une équipe n'utilise jamais que les 5 premiers chunks récupérés. Doit-elle rapporter recall@100 comme métrique de récupération principale ? Pourquoi ou pourquoi pas ?

<details markdown="1"><summary>Vérifier</summary>

Non. Recall@100 mesure si le document pertinent apparaît quelque part parmi les 100 premiers résultats, mais le pipeline ne regarde jamais au-delà des 5 premiers, donc un succès au rang 40 est invisible pour le système réel et ne devrait pas compter comme une réussite. Recall@5 est le chiffre qui reflète ce que le pipeline exploite réellement ; rapporter recall@100 surestimerait la fréquence à laquelle le système fait réellement remonter la bonne réponse jusqu'à la génération.

</details>

5. ▢ Laquelle de ces affirmations est vraie à propos de recall@k et de MRR ?

    - a) Ils mesurent exactement la même chose, donc rapporter les deux est redondant
    - b) Recall@k mesure si un résultat pertinent tombe dans un budget de k ; MRR mesure à quelle hauteur est classé le premier résultat pertinent, en récompensant le rang 1 bien plus qu'un rang plus bas
    - c) MRR doit toujours être préféré à recall@k, quelle que soit la charge de travail
    - d) Recall@k est insensible au choix de k ; n'importe quelle valeur donne le même résultat

<details markdown="1"><summary>Vérifier</summary>

**b)** C'est exactement l'information complémentaire que capture chaque métrique. (a) est fausse : l'exemple détaillé a montré deux systèmes qui pourraient être à égalité sur recall@k tout en différant fortement sur MRR. (c) est fausse : la métrique qui compte le plus dépend de la question de savoir si seul le tout premier résultat compte ou si plusieurs résultats dans un budget sont exploitables. (d) est fausse : recall@k augmente avec k, par définition, donc le choix de k change la valeur rapportée.

</details>

## Exercices en situation réelle

- [ ] Pour un pipeline de récupération que vous exploitez ou prévoyez d'exploiter, identifiez le k réel que votre système en aval utilise (combien de chunks atteignent la génération), et calculez le recall à ce k, pas à une valeur par défaut comme 10 ou 100.
- [ ] Si vous disposez d'un jeu de requêtes étiqueté ou synthétique, calculez le MRR en plus de recall@k et vérifiez si les deux chiffres racontent une histoire cohérente ou révèlent quelque chose qu'une seule métrique aurait caché.
- [ ] Demain : pour une requête où le document pertinent de votre système est classé plus bas que vous ne le voudriez, notez son rang exact et son effet à la fois sur recall@k (au k que vous avez choisi) et sur MRR.

## Pour aller plus loin

- [Billet : "Evaluation Measures for Search and Recommender Systems", Pinecone](https://www.pinecone.io/learn/offline-evaluation/)
- [Ressources](../RESOURCES.md)

---

Ça ne passe pas ? Relisez la source primaire en haut de page, car cette leçon la condense et c'est dans la condensation que la compréhension s'échappe. Consultez le [glossaire](../GLOSSARY.md) pour tout terme qui vous a paru glissant.

Si c'est la leçon elle-même qui n'est pas claire plutôt que la matière, c'est un défaut : [ouvrez une issue](https://github.com/TokenCemetery/teach/issues).
