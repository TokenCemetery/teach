---
title: "6. BM25 et recherche lexicale"
description: "Ce que BM25 note réellement, et pourquoi la correspondance exacte des termes détecte encore ce que les embeddings sémantiques manquent"
type: lesson
---

# Leçon 6. BM25 et recherche lexicale

**Lien avec la mission :** L'étape 4 ouvre la recherche hybride : avant de combiner un classement lexical avec la recherche vectorielle, cette leçon établit ce en quoi la recherche lexicale est réellement bonne, et pourquoi un bon modèle d'embedding ne la rend pas obsolète.
**Source primaire :** [Article : "The Probabilistic Relevance Framework: BM25 and Beyond", Robertson and Zaragoza, 2009](https://www.staff.city.ac.uk/~sbrp622/papers/foundations_bm25_review.pdf)
**Prérequis :** [Leçon 5](0005-pgvector-specifics.md), [Chunk](../GLOSSARY.md)

## Échauffement

1. ▢ Pourquoi un bi-encoder calcule-t-il l'embedding d'une requête et d'un passage séparément plutôt que conjointement ?

<details markdown="1"><summary>Vérifier</summary>

Pour que chaque passage puisse être traité une seule fois, à l'avance, et stocké ; seule la requête demande un embedding au moment de la recherche, ce qui permet de la comparer à peu de frais à des vecteurs de passages précalculés.

</details>

2. ▢ Pourquoi un index construit avec `vector_l2_ops` n'accélère-t-il pas une requête qui trie par `<=>` (distance cosinus) ?

<details markdown="1"><summary>Vérifier</summary>

Un index est construit pour une fonction de distance précise ; la classe d'opérateurs et l'opérateur de la requête doivent correspondre, faute de quoi l'index n'est pas utilisé et la requête retombe sur un balayage séquentiel complet.

</details>

## À savoir

### BM25 note le recouvrement des termes, pas le sens

**BM25** est une fonction de classement lexical : elle note la pertinence d'un document pour une requête uniquement d'après les termes de la requête qui apparaissent littéralement dans le document, leur fréquence et le caractère informatif de chaque terme, sans embedding et sans aucune notion de sens. Trois ingrédients se combinent dans son score : la **fréquence inverse de document (IDF)**, qui pondère un terme de la requête selon sa rareté dans tout le corpus (un mot courant comme « le » ne contribue presque à rien, puisqu'il apparaît partout et ne distingue rien ; un terme rare et précis contribue fortement, puisque sa présence est informative) ; la **fréquence du terme**, c'est-à-dire le nombre de fois qu'un terme de la requête apparaît dans ce document précis, mais **avec saturation** plutôt qu'avec une croissance linéaire, de sorte qu'un terme présent 10 fois ne score pas 10 fois plus qu'un terme présent une fois, ce qui empêche le bourrage de mots-clés de dominer un score ; et la **normalisation de la longueur**, qui neutralise l'avantage brut de fréquence des termes d'un document du simple fait qu'il est plus long que la moyenne, puisqu'un document plus long a, par sa seule taille, plus de chances de contenir un terme donné, pas nécessairement parce qu'il est plus pertinent.

### Pourquoi la recherche lexicale compte encore à côté d'un bon modèle d'embedding

Les modèles d'embedding sont entraînés à capturer la similarité sémantique, et ils le font bien pour des formulations synonymes : une requête « comment réparer un tuyau cassé » peut récupérer un passage sur « colmater un conduit qui fuit » sans aucun mot en commun, parce que les deux disent des choses proches. Mais ce même entraînement rend les embeddings comparativement faibles pour la correspondance exacte de termes précis : un code produit, un identifiant d'erreur, un nom propre rare, une expression exacte que l'utilisateur cite mot pour mot. Une requête « code d'erreur E502 » a besoin d'un document qui contient littéralement « E502 » ; un modèle d'embedding, entraîné sur la similarité sémantique générale plutôt que sur la correspondance exacte d'identifiants, peut récupérer des documents qui parlent thématiquement de gestion d'erreurs sans faire remonter le seul document qui contient réellement le code précis que l'utilisateur a saisi. BM25 a l'angle mort inverse : exactement le cas contraire, « tuyau cassé » face à « conduit qui fuit », obtiendrait un score proche de zéro avec BM25, puisque les deux n'ont aucun terme en commun, bien qu'ils veuillent dire la même chose. Chaque approche détecte ce que l'autre manque, ce qui justifie précisément de les combiner plutôt que d'en choisir une.

![Une grille de deux par deux. Première ligne : une requête à identifiant exact comme « code d'erreur E502 ». BM25 la trouve, puisque la chaîne littérale apparaît dans le document ; la recherche vectorielle peut la rater, puisque son modèle d'embedding a été entraîné pour la similarité sémantique, pas pour la correspondance exacte d'identifiants. Seconde ligne : une requête à formulation synonyme comme « tuyau cassé » face à un document qui dit « conduit qui fuit », sans aucun mot en commun. BM25 lui donne un score proche de zéro, puisqu'il ne compte que le recouvrement littéral des termes ; la recherche vectorielle la trouve, puisque les deux expressions veulent dire la même chose. L'angle mort de chaque méthode est la force de l'autre.](images/bm25-vs-vector-blindspots.svg)

## Pratique

1. ▢ Un utilisateur cherche le code d'erreur exact « E502 ». Pourquoi la recherche vectorielle seule pourrait-elle sous-récupérer le seul document qui contient cette chaîne, alors que le corpus compte plusieurs documents qui parlent thématiquement de gestion d'erreurs ?

<details markdown="1"><summary>Vérifier</summary>

Le modèle d'embedding a été entraîné à capturer la similarité sémantique, pas la correspondance exacte d'identifiants, donc « E502 » peut ne pas être bien représenté comme un point distinctif de l'espace d'embedding ; des documents thématiquement proches sur la gestion d'erreurs en général peuvent se retrouver plus près de l'embedding de la requête que le seul document qui contient la chaîne littérale « E502 ».

</details>

2. ▢ Une requête dit « comment réparer un tuyau cassé », et le document qui correspond le mieux est formulé « colmater un conduit qui fuit », sans aucun mot en commun avec la requête. BM25 donnerait-il un score élevé à cette paire ? Pourquoi ou pourquoi pas ?

<details markdown="1"><summary>Vérifier</summary>

Non, BM25 lui donnerait un score proche de zéro, puisqu'il note uniquement d'après les termes de la requête qui apparaissent littéralement dans le document, et que cette paire n'a aucun terme en commun. BM25 n'a aucun moyen de reconnaître que les deux formulations veulent dire la même chose ; c'est exactement le vide que la similarité sémantique de la recherche vectorielle est censée combler.

</details>

3. ▢ Pourquoi BM25 fait-il saturer la fréquence des termes (en atténuant le gain de score des occurrences répétées d'un terme) au lieu de la noter linéairement ?

<details markdown="1"><summary>Indice</summary>

Réfléchissez à ce qu'un document pourrait faire pour tricher avec un score de fréquence des termes linéaire.

</details>

<details markdown="1"><summary>Vérifier</summary>

Un score de fréquence des termes linéaire permettrait à un document de dominer le classement simplement en répétant un terme de la requête de nombreuses fois (bourrage de mots-clés), qu'il soit réellement plus pertinent ou non. Faire saturer la fréquence des termes signifie que chaque occurrence supplémentaire contribue moins que la précédente, de sorte que la pertinence reste récompensée sans que la seule répétition brute domine le score.

</details>

4. ▢ Pourquoi BM25 normalise-t-il la longueur des documents, et que se passerait-il de mal sans cette normalisation ?

<details markdown="1"><summary>Vérifier</summary>

Un document plus long a plus d'occasions de contenir un terme de requête donné du simple fait d'avoir plus de mots, indépendamment du fait qu'il soit réellement plus pertinent pour la requête. Sans normalisation de la longueur, les longs documents l'emporteraient systématiquement sur des documents plus courts, tout aussi pertinents ou davantage, uniquement à cause de leur taille et non de leur pertinence réelle.

</details>

5. ▢ Laquelle de ces affirmations est vraie à propos de BM25 par rapport à la recherche vectorielle ?

    - a) BM25 et la recherche vectorielle échouent sur exactement les mêmes types de requêtes, donc les combiner n'apporte rien
    - b) BM25 excelle à la correspondance exacte de termes mais rate les formulations synonymes sans mots en commun, alors que la recherche vectorielle fait l'inverse
    - c) BM25 exige un modèle d'embedding pour calculer la pertinence des termes
    - d) La recherche vectorielle fait toujours mieux que BM25 pour n'importe quelle requête, puisqu'elle capture le sens et pas seulement les mots

<details markdown="1"><summary>Vérifier</summary>

**b)** L'angle mort de chaque approche est la force de l'autre, ce qui est toute la base de la recherche hybride. (a) est fausse : leurs modes de défaillance sont opposés, pas identiques. (c) est fausse : BM25 est purement une méthode de statistiques de termes, sans aucun embedding. (d) est fausse : une correspondance exacte d'identifiant ou de code est précisément le cas où BM25 peut surpasser un embedding sémantique.

</details>

## Exercices en situation réelle

- [ ] Trouvez ou écrivez pour votre corpus une requête qui comporte un identifiant, un code ou une expression exacte précis, et vérifiez si votre configuration de récupération actuelle (si elle est uniquement vectorielle) fait réellement remonter le document qui le contient.
- [ ] Trouvez dans votre corpus une requête et un document correspondant qui partagent très peu de mots exacts, voire aucun, mais veulent dire la même chose, et prédisez quel score une recherche BM25 seule donnerait à cette paire.
- [ ] Demain : vérifiez si votre pile de recherche (recherche plein texte de Postgres, Elasticsearch ou équivalent) expose déjà une fonction de classement de type BM25 que vous pourriez comparer à vos résultats de recherche vectorielle.

## Pour aller plus loin

- [Article : "The Probabilistic Relevance Framework: BM25 and Beyond", Robertson and Zaragoza, 2009](https://www.staff.city.ac.uk/~sbrp622/papers/foundations_bm25_review.pdf)
- [Doc : "Reciprocal rank fusion (RRF)", Elasticsearch](https://www.elastic.co/guide/en/elasticsearch/reference/current/rrf.html)
- [Ressources](../RESOURCES.md)

---

Ça ne passe pas ? Relisez la source primaire en haut de page, car cette leçon la condense et c'est dans la condensation que la compréhension s'échappe. Consultez le [glossaire](../GLOSSARY.md) pour tout terme qui vous a paru glissant.

Si c'est la leçon elle-même qui n'est pas claire plutôt que la matière, c'est un défaut : [ouvrez une issue](https://github.com/TokenCemetery/teach/issues).
