---
title: "2. Déduplication et filtrage de qualité"
description: "Pourquoi les textes quasi dupliqués et les documents de faible qualité sont retirés avant l'entraînement, et ce que coûte le fait de sauter cette étape"
type: lesson
---

# Leçon 2. Déduplication et filtrage de qualité

**Lien avec la mission :** « Construire un corpus de pré-entraînement dédupliqué et filtré sur la qualité à partir de sources brutes, et dire ce que retire chaque étape de filtrage et pourquoi » est le premier point sous Objectif. La leçon 1 a couvert le sourcing et le mélange ; cette leçon couvre la moitié déduplication et filtrage.
**Source primaire :** [Article : "Deduplicating Training Data Makes Language Models Better", Lee et al., 2021](https://arxiv.org/abs/2107.06499)
**Prérequis :** [Leçon 1](0001-sourcing-and-mixing-a-pretraining-corpus.md)

## Échauffement

1. ▢ Quelle est la différence entre une décision de sourcing et une décision de mélange pour un corpus de pré-entraînement ?

<details markdown="1"><summary>Vérifier</summary>

Le sourcing décide quelles sources sont incluses. Le mélange décide quelle part du budget final de tokens chaque source incluse obtient, indépendamment des sources choisies.

</details>

2. ▢ D'après l'article The Pile, pourquoi « quelle est la taille du corpus » est-elle la mauvaise première question à poser sur un run de pré-entraînement ?

<details markdown="1"><summary>Vérifier</summary>

Parce que GPT-2 et GPT-3, entraînés sur d'énormes quantités de texte web, peinaient quand même sur des composantes comme l'écriture académique, qu'un crawl web généraliste sous-représente. Ce sont les sources incluses, et non le nombre total d'octets, qui déterminent les domaines qu'un modèle apprend réellement.

</details>

## À savoir

### Les doublons ne sont pas qu'un gaspillage d'espace disque

Un corpus assemblé à partir de nombreuses sources, surtout dès qu'il touche au web ouvert, finit par contenir le même texte plusieurs fois : articles de presse syndiqués, mentions légales standard, e-mails types où seul un nom change. Lee et al. ont constaté que ce n'est pas une inefficacité mineure. Dans C4, un corpus très utilisé dérivé d'un crawl web, une seule phrase anglaise de 61 mots apparaît plus de 60 000 fois. Plus frappant encore, plus de 1 % de la sortie non sollicitée des modèles de langage entraînés sur de tels jeux de données est copié mot pour mot depuis les données d'entraînement : le modèle ne généralise pas à cet endroit, il cite quelque chose qu'il a vu assez de fois pour le mémoriser.

### Deux manières différentes de trouver un doublon

La déduplication doit attraper deux formes différentes de répétition, et une seule technique ne les attrape pas toutes les deux :

- **La correspondance exacte de sous-chaînes** trouve les passages de texte répétés mot pour mot, même ceux qui ne représentent qu'une partie d'un document ou qui traversent les frontières entre documents. Lee et al. l'implémentent efficacement avec un suffix array, ce qui permet de trouver un passage répété de n'importe quelle longueur sans comparer directement chaque document à tous les autres.
- **La correspondance de quasi-doublons** trouve les documents qui sont en grande partie identiques mais diffèrent par de petits détails, comme un e-mail type avec le nom d'un autre destinataire, ou une dépêche d'agence reprise avec de légères modifications par de nombreux médias. Lee et al. utilisent MinHash : une technique qui estime la similarité de deux documents sans les comparer token par token, en comparant plutôt des résumés compacts fondés sur des hashes.

Les deux comptent, parce qu'un corpus peut être exempt d'un type de duplication tout en étant plein de l'autre.

### Ce que la déduplication apporte réellement

Lee et al. donnent des preuves concrètes plutôt qu'une intuition. Dédupliquer les données d'entraînement a fait émettre aux modèles du texte mémorisé environ dix fois moins souvent, et leur a permis d'atteindre la même précision, voire une meilleure, en moins de pas d'entraînement. Cela réduit aussi le chevauchement entre entraînement et test, qui, selon l'article, touche plus de 4 % de l'ensemble de validation dans des benchmarks standards ; un texte qui a fui de l'ensemble de validation d'un benchmark vers l'entraînement fait paraître un chiffre d'évaluation meilleur que ne le mérite la vraie généralisation du modèle, une préoccupation que ce parcours retrouvera quand il renverra au traitement de la contamination dans `llm/evals`.

### Le filtrage de qualité est une étape distincte, plus tardive

La déduplication retire les copies redondantes d'un texte déjà présent. Le filtrage de qualité retire le texte de faible valeur même sans qu'il soit le doublon de quoi que ce soit : spam, menus de navigation génériques, texte généré par machine, ou documents si brouillés qu'ils portent peu de signal. Les auteurs de GPT-3 décrivent une version concrète de cela dans leur annexe sur le filtrage de Common Crawl : ils ont entraîné un classifieur, une régression logistique sur des features simples de type sac de mots, pour distinguer un texte sélectionné (WebText, Wikipedia, un corpus de livres) du Common Crawl brut non filtré. Le score de ce classifieur a ensuite servi à rééchantillonner Common Crawl pour que les documents prédits de meilleure qualité soient conservés plus souvent, tout en gardant quelques documents moins bien notés au lieu de les écarter d'emblée. La même annexe décrit aussi une passe distincte de déduplication floue avec MinHash, qui à elle seule a réduit la taille de leur jeu de données d'environ 10 %.

Le filtrage de qualité et la déduplication sont fréquemment exécutés comme des passes séparées sur le même corpus, dans un ordre ou dans l'autre, et aucun ne remplace l'autre : un corpus peut être exempt de doublons exacts et rester plein de texte générique de faible valeur, et il peut être une prose uniformément de grande qualité tout en contenant le même paragraphe répété soixante mille fois.

## Pratique

1. ▢ Un jeu de données contient 61 mots répétés mot pour mot dans plus de 60 000 documents différents, à chaque fois avec un texte environnant différent. La correspondance exacte de sous-chaînes ou la correspondance de quasi-doublons (MinHash) serait-elle l'outil adapté pour trouver et retirer uniquement ce passage répété, et pourquoi ?

<details markdown="1"><summary>Indice</summary>

Demandez-vous ce que MinHash compare réellement : des documents entiers entre eux, ou des passages de texte qui peuvent ne représenter qu'une partie d'un document.

</details>

<details markdown="1"><summary>Vérifier</summary>

La correspondance exacte de sous-chaînes. MinHash estime la similarité entre documents entiers ; un passage de 61 mots répété au sein de documents par ailleurs différents est exactement le genre de répétition partielle, entre documents, qu'une recherche exacte de sous-chaînes fondée sur un suffix array est conçue pour attraper, alors que deux documents qui ne partagent que 61 mots sur plusieurs milliers pourraient ne pas être enregistrés comme quasi-doublons l'un de l'autre.

</details>

2. ▢ Laquelle de ces affirmations est la plus proche de ce que Lee et al. ont réellement mesuré, plutôt que simplement avancé ?

    - a) La déduplication rend un modèle philosophiquement plus original
    - b) L'entraînement sur données dédupliquées a permis aux modèles d'atteindre la même précision, voire une meilleure, en moins de pas, et d'émettre du texte mémorisé environ dix fois moins souvent
    - c) La déduplication ne sert qu'à réduire les coûts de stockage, sans effet sur le comportement du modèle
    - d) La correspondance de quasi-doublons seule suffit à retirer toutes les formes de texte répété

<details markdown="1"><summary>Vérifier</summary>

**b)** est le résultat réellement mesuré de l'article. (a) n'est pas une affirmation mesurable. (c) contredit directement les constats sur la mémorisation et l'efficacité de l'entraînement. (d) est faux, puisque la correspondance exacte de sous-chaînes attrape une autre forme de répétition que la correspondance de quasi-doublons, comme le montre le premier exercice de pratique de cette leçon.

</details>

3. ▢ Un document n'est le doublon de rien d'autre dans le corpus, mais il est en grande partie du texte générique auto-généré, presque sans contenu informatif. La déduplication le retirerait-elle ? Qu'est-ce qui le retirerait ?

<details markdown="1"><summary>Vérifier</summary>

Non, la déduplication ne le retirerait pas, puisqu'elle ne cible que le texte répété et que ce document est unique. Le filtrage de qualité, comme le rééchantillonnage par classifieur que décrivent les auteurs de GPT-3, est l'étape visée exactement pour ce cas : un texte de faible valeur qui n'est la copie de rien d'autre.

</details>

4. ▢ Le classifieur de qualité de Common Crawl de GPT-3 a été entraîné à distinguer lesquelles de ces paires de choses ?

    - a) Le texte anglais du texte non anglais
    - b) Le texte sélectionné (WebText, Wikipedia, un corpus de livres) du Common Crawl brut non filtré
    - c) Les documents longs des documents courts
    - d) Le texte dupliqué du texte unique

<details markdown="1"><summary>Vérifier</summary>

**b)** Le texte sélectionné contre le Common Crawl brut. (d) décrit la déduplication, que les auteurs de GPT-3 ont exécutée comme une passe MinHash distincte, et non ce que le classifieur de qualité lui-même a été entraîné à détecter.

</details>

## Exercices en situation réelle

- [ ] Choisissez une phrase ou une courte expression dont vous vous attendez à ce qu'elle soit courante dans le texte web (une mention légale, une formule toute faite, une consigne de recette courante) et cherchez-la mot pour mot en ligne. Notez approximativement sur combien de pages distinctes vous la trouvez, pour avoir une idée concrète de la façon dont la répétition se manifeste dans du texte réellement crawlé.
- [ ] Lisez le résumé et l'introduction de l'article de Lee et al. (lié plus haut) et écrivez, en une phrase chacune, ce que la correspondance exacte de sous-chaînes et la correspondance de quasi-doublons savent chacune attraper que l'autre n'attrape pas.
- [ ] Demain : reprenez un corpus dont vous avez esquissé un mélange dans l'exercice en situation réelle de la leçon 1, et pour chaque type de source, nommez une source plausible de duplication (syndication, texte générique issu de gabarits, republication) et une source plausible de faible qualité que la déduplication seule n'attraperait pas.

## Pour aller plus loin

- [Article : "Deduplicating Training Data Makes Language Models Better", Lee et al., 2021](https://arxiv.org/abs/2107.06499)
- [Ressources](../RESOURCES.md)

---

Ça ne passe pas ? Relisez la source primaire en haut de page, car cette leçon la condense et c'est dans la condensation que la compréhension s'échappe. Consultez le [glossaire](../GLOSSARY.md) pour tout terme qui vous a paru glissant.

Si c'est la leçon elle-même qui n'est pas claire plutôt que la matière, c'est un défaut : [ouvrez une issue](https://github.com/TokenCemetery/teach/issues).
