---
title: "1. Chunking"
description: "Le premier choix du pipeline, dont hérite chaque étape suivante"
type: lesson
---

# Leçon 1. Chunking

**Lien avec la mission :** Le chunking est la première décision du pipeline qu'enseigne cet espace de travail, et chaque étape suivante (embeddings, recherche hybride, reranking) travaille avec ce qu'un chunk lui a donné. Un mauvais choix de chunking ne se rattrape pas par du reranking.
**Source primaire :** [Billet : "Chunking Strategies for LLM Applications", Pinecone](https://www.pinecone.io/learn/chunking-strategies/)
**Prérequis :** aucun

## À savoir

### Pourquoi on découpe un document

Un pipeline de récupération ne calcule pas l'embedding de documents entiers et ne cherche pas dedans. Il découpe d'abord chaque document en **chunks**, puis calcule l'embedding de ces chunks et les indexe. Deux raisons pratiques l'imposent :

- Un modèle d'embedding a une fenêtre de contexte limitée, donc un long document peut ne pas y tenir du tout.
- Même quand il y tient, calculer l'embedding d'un long passage thématiquement mélangé sous la forme d'un seul vecteur le rend flou. Le vecteur finit par représenter une moyenne de tout ce que touche le passage, ce qui en fait une moins bonne correspondance pour une requête portant sur un point précis qu'il contient.

Le chunking existe donc pour que chaque unité vectorisée reste assez ciblée pour que son vecteur représente réellement ce qu'une requête pourrait chercher.

### Le compromis central

La taille des chunks fait arbitrer entre deux modes de défaillance :

- **Chunks trop grands :** l'embedding mélange plusieurs sujets de façon floue, ce qui nuit à la précision, et une requête portant sur un détail à l'intérieur d'un long chunk peut ne pas le faire remonter comme une correspondance proche. La récupération renvoie aussi davantage de texte environnant non pertinent avec la partie pertinente.
- **Chunks trop petits :** chaque chunk peut perdre le contexte environnant qui le rend interprétable, ou qui répond à une question à cheval sur plusieurs petits morceaux. Une phrase isolée d'un paragraphe peut être ambiguë ou incomplète à elle seule.

Il n'existe pas de taille de chunk universellement bonne. Le bon choix dépend du corpus (les clauses d'un contrat juridique se lisent autrement qu'une transcription de chat) et du type de requêtes que le système doit servir (une requête qui demande un seul fait se comporte autrement qu'une requête qui demande une explication en plusieurs étapes).

### Stratégies de chunking courantes

- **Taille fixe.** Couper tous les N tokens ou caractères, généralement avec un certain chevauchement entre chunks consécutifs. Simple et prévisible, mais aveugle à la structure réelle du document : il peut couper une phrase, ou un tableau, en deux.
- **Récursif / tenant compte de la structure.** Couper d'abord aux frontières naturelles du document (sections, puis paragraphes, puis phrases), en ne se rabattant sur une coupe de taille fixe que lorsqu'un morceau délimité par une frontière reste trop grand. Cela respecte l'organisation de l'auteur au lieu d'en imposer une arbitraire.
- **Chunking sémantique.** Calculer l'embedding de phrases consécutives et couper là où la similarité entre voisines chute nettement, selon l'idée qu'un changement de sujet est l'endroit où doit se trouver une frontière de chunk. Plus coûteux à calculer, et il vise directement le mode de défaillance réel (des sujets mélangés dans un même chunk) plutôt que par approximation.
- **Tenant compte de la structure du document.** Traiter comme atomiques les unités structurelles que le format fournit déjà, comme la section d'un titre, un tableau ou un bloc de code : ne jamais en couper une à cheval sur une frontière de chunk, car cela détruit généralement son sens.

![Trois barres représentant le même document. La barre du haut montre sa structure naturelle : une section courte, une section longue et une section moyenne, marquées par des traits pointillés aux vraies frontières des sections. La barre du milieu montre le chunking de taille fixe, qui découpe le même document en quatre morceaux de largeur égale sans tenir compte de l'endroit où finissent réellement les sections, si bien qu'une coupe tombe au milieu de la section longue et la divise en deux. La barre du bas montre le chunking tenant compte de la structure, dont les frontières de chunks s'alignent exactement sur les frontières naturelles des sections de la barre du haut, si bien qu'aucune section n'est répartie sur deux chunks.](images/fixed-vs-structure-aware-chunking.svg)

### Chevauchement

Les chunks consécutifs se chevauchent couramment sur un certain nombre de tokens. Sans chevauchement, un fait ou une phrase qui se trouve exactement à l'endroit où deux chunks se séparent peut se retrouver fragmenté, impossible à retrouver en entier à partir de l'un ou l'autre chunk seul. Le chevauchement coûte un peu de stockage et de calcul d'embedding redondants, en échange de l'absence de perte d'information aux frontières des chunks.

## Pratique

1. ▢ En une phrase, pourquoi un pipeline de récupération découpe-t-il un document en chunks au lieu de calculer l'embedding du document entier ?

<details markdown="1"><summary>Vérifier</summary>

Parce qu'un long passage thématiquement mélangé produit un seul vecteur flou représentant une moyenne de tout ce qu'il touche, qui se récupère mal pour une requête portant sur un point précis qu'il contient (et il peut même ne pas tenir dans la fenêtre de contexte du modèle d'embedding).

</details>

2. ▢ Un corpus de longs contrats juridiques est découpé en morceaux de taille fixe de 512 tokens, sans chevauchement. Les utilisateurs posent des questions sur des clauses précises, et la récupération rate sans cesse des clauses coupées à cheval sur une frontière de chunk. Nommez deux changements de stratégie de chunking qui aideraient, et ce que chacun corrige.

<details markdown="1"><summary>Indice</summary>

Un changement s'attaque à la coupure aux frontières elle-même ; l'autre s'attaque à ce qui se passe quand une coupure est inévitable.

</details>

<details markdown="1"><summary>Vérifier</summary>

Passer à une stratégie tenant compte de la structure (ou de la structure du document) qui coupe aux frontières des clauses ou des sections plutôt qu'à un nombre brut de tokens, pour qu'une clause ne soit pas coupée en pleine phrase dès le départ. Par ailleurs, ajouter un chevauchement entre chunks, pour que, même là où une coupure tombe près d'une frontière de clause, le texte complet de la clause apparaisse intact dans au moins un chunk.

</details>

3. ▢ Une équipe découpe un corpus en morceaux très courts d'une seule phrase pour maximiser la précision. Quel est l'inconvénient probable, et quand apparaîtrait-il ?

<details markdown="1"><summary>Vérifier</summary>

Chaque chunk peut perdre le contexte environnant qui le rend interprétable ou complet : une phrase prise isolément peut être ambiguë, et une question dont la réponse s'étend sur plus d'une phrase ne pourra être traitée à partir d'aucun chunk récupéré seul. Cela se manifeste par une récupération qui trouve techniquement « la bonne phrase » alors que le système ne parvient quand même pas à produire une réponse correcte ou complète à partir d'elle.

</details>

4. ▢ Pourquoi les chunks consécutifs se chevauchent-ils couramment ?

    - a) Pour rendre l'index vectoriel plus gros et plus exhaustif
    - b) Pour qu'un fait ou une phrase à cheval sur une frontière de chunk ne soit pas fragmenté et irrécupérable à partir de l'un ou l'autre chunk
    - c) Parce que les modèles d'embedding exigent une longueur d'entrée minimale
    - d) Pour permettre au reranker de comparer des chunks adjacents entre eux

<details markdown="1"><summary>Vérifier</summary>

**b)** Pour qu'un fait ou une phrase à cheval sur une frontière de chunk ne soit pas fragmenté et irrécupérable à partir de l'un ou l'autre chunk. (a) décrit un coût du chevauchement, pas son but. (c) et (d) ne sont pas la raison d'être du chevauchement.

</details>

## Exercices en situation réelle

- [ ] Choisissez un vrai document d'un corpus sur lequel vous feriez de la récupération. Découpez-le à la main de deux façons (taille fixe, et selon la structure à partir de ses vrais titres ou sections) et comparez où chaque stratégie coupe en pleine phrase.
- [ ] Pour ce même document, choisissez une requête qu'un utilisateur pourrait réalistement poser, et vérifiez quelle sortie de stratégie de chunking contiendrait réellement une réponse complète et récupérable.
- [ ] Demain : lisez en entier le billet sur les stratégies de chunking lié ci-dessous, et notez quelle stratégie vous choisiriez par défaut pour votre propre corpus et pourquoi.

## Pour aller plus loin

- [Billet : "Chunking Strategies for LLM Applications", Pinecone](https://www.pinecone.io/learn/chunking-strategies/)
- [Ressources](../RESOURCES.md)

---

Ça ne passe pas ? Relisez la source primaire en haut de page, car cette leçon la condense et c'est dans la condensation que la compréhension s'échappe. Consultez le [glossaire](../GLOSSARY.md) pour tout terme qui vous a paru glissant.

Si c'est la leçon elle-même qui n'est pas claire plutôt que la matière, c'est un défaut : [ouvrez une issue](https://github.com/TokenCemetery/teach/issues).
