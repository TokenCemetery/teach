---
title: "4. SentencePiece et le compromis sur la taille du vocabulaire"
description: "Tokeniser du texte brut sans pré-tokenizer, et ce que coûte réellement un vocabulaire plus grand ou plus petit"
type: lesson
---

# Leçon 4. SentencePiece et le compromis sur la taille du vocabulaire

**Lien avec la mission :** « Entraîner un tokenizer et défendre une taille de vocabulaire au regard de son effet sur la longueur des séquences et sur la taille de la table d'embeddings » est le deuxième point sous Objectif. La leçon 3 a construit l'algorithme de fusion ; cette leçon couvre son entraînement sans supposer de frontières de mots, ainsi que la décision sur la taille elle-même.
**Source primaire :** [Article : "SentencePiece: A simple and language independent subword tokenizer and detokenizer for Neural Text Processing", Kudo et Richardson, 2018](https://arxiv.org/abs/1808.06226)
**Prérequis :** [Leçon 3](0003-byte-pair-encoding-from-scratch.md)

## Échauffement

1. ▢ Dans l'algorithme de byte-pair encoding, qu'est-ce que le nombre d'opérations de fusion effectuées détermine ?

<details markdown="1"><summary>Vérifier</summary>

La taille finale du vocabulaire : elle est égale au jeu de caractères de départ plus un nouveau symbole par fusion effectuée.

</details>

2. ▢ Pourquoi trois paires de l'exemple détaillé de la leçon 3 (`(e, s)`, `(s, t)`, `(t, </w>)`) ont-elles toutes fini fusionnées en quelques pas les unes des autres, quelle que soit celle fusionnée en premier ?

<details markdown="1"><summary>Vérifier</summary>

Elles étaient toutes à égalité à la même fréquence parce qu'elles provenaient toutes de la même sous-chaîne répétée, « est ». Fusionner l'une d'elles rebaptisait les autres en nouvelles paires au même compte au lieu de lever l'égalité, de sorte que les trois se sont réunies en peu de temps quelle que soit celle fusionnée en premier.

</details>

## À savoir

### Pourquoi supposer des frontières de mots ne tient pas

Le byte-pair encoding, tel que la leçon 3 l'a décrit, est généralement exécuté par-dessus un **pré-tokenizer** : quelque chose qui découpe d'abord le texte brut en mots, de sorte que le BPE n'a jamais à apprendre que des fusions à l'intérieur d'un mot. Pour l'anglais, découper sur les espaces est un pré-tokenizer simple et le plus souvent fiable. Il n'est pas indépendant de la langue : de nombreuses langues écrites très répandues, dont le japonais et le chinois, ne délimitent pas du tout les mots par des espaces, si bien qu'un pré-tokenizer par espaces n'a rien de sensé à découper avant même que le BPE ne commence. Construire un pré-tokenizer différent par langue, ou par écriture, sape l'idée d'une procédure unique d'entraînement du tokenizer qui fonctionne partout.

### S'entraîner directement sur des phrases brutes

SentencePiece, de Kudo et Richardson, supprime l'étape de pré-tokenisation au lieu d'essayer de la corriger langue par langue : il entraîne son modèle de sous-mots directement sur du texte de phrases brutes, sans aucune hypothèse intégrée de frontières de mots préexistantes. L'espace lui-même est traité comme un symbole ordinaire de l'entrée, généralement représenté par un marqueur dédié pour que l'espacement d'origine puisse être reproduit exactement à la détokenisation, plutôt que comme quelque chose sur lequel découper avant le début de l'entraînement. Cela rend la même procédure d'entraînement indépendante de la langue, ce que l'article appuie par une expérience de traduction automatique anglais-japonais : l'entraînement de bout en bout sur des phrases brutes a atteint une précision comparable à celle d'un entraînement sur du texte déjà segmenté en mots par un outil distinct.

### Une boîte à outils, deux algorithmes d'entraînement

SentencePiece n'est pas un second algorithme concurrent du BPE ; c'est une boîte à outils qui implémente le BPE (la procédure de fusion de la leçon 3) aux côtés d'un second algorithme d'entraînement, un entraîneur de **modèle de langue unigramme**, qui travaille dans le sens opposé. Au lieu de partir des caractères individuels et de faire croître les fusions vers le haut, il part d'un grand ensemble de sous-mots candidats et élague de façon répétée jusqu'à la taille de vocabulaire cible, en retirant à chaque pas les morceaux dont l'absence coûterait le moins à la vraisemblance du modèle. L'un ou l'autre algorithme d'entraînement produit la même forme de résultat : un vocabulaire fixe de morceaux de sous-mots et une manière déterministe de découper un nouveau texte brut en ces morceaux.

### Le compromis sur la taille du vocabulaire

La taille cible du vocabulaire, quelle que soit la manière dont il a été entraîné, est un nombre unique qui tire dans plusieurs directions à la fois :

- Un vocabulaire **plus grand** encode le même texte en moins de tokens en moyenne, puisque davantage de sous-chaînes courantes méritent leur propre symbole. Des séquences de tokens plus courtes signifient moins de calcul dépensé à attendre et générer la même entrée.
- Un vocabulaire **plus grand** signifie aussi une table d'embeddings plus grande et une projection de sortie plus grande (généralement la même matrice, liée), ce qui représente un nombre de paramètres qui croît directement avec la taille du vocabulaire, indépendamment de la profondeur ou de la largeur du reste du modèle.
- Un vocabulaire **plus grand** dilue le signal d'entraînement : avec le même corpus découpé en davantage de morceaux distincts parmi lesquels choisir, un token précis, surtout un plus rare, est vu moins de fois par passe sur les données.
- Un vocabulaire **plus petit** inverse les trois : des séquences de tokens plus longues par entrée, une table d'embeddings et de sortie plus petite, et un signal d'entraînement par token plus dense, au prix de découper chaque mot ordinaire en davantage de morceaux.

Aucune taille de vocabulaire ne gagne sur tous les axes à la fois, elle se choisit donc en fonction de la forme et du budget d'un modèle précis plutôt qu'en la lisant dans une formule. Un exemple réel et vérifiable : l'article LLaMA indique avoir tokenisé ses données d'entraînement avec du byte-pair encoding via l'implémentation SentencePiece, en découpant tous les nombres en chiffres individuels et en retombant sur des octets bruts pour représenter tout caractère UTF-8 que le vocabulaire entraîné ne couvre pas autrement, de sorte qu'aucun caractère d'entrée n'est jamais réellement impossible à représenter, quelle que soit la taille de vocabulaire choisie.

## Pratique

1. ▢ Un tokenizer construit sur un pré-tokenizer par espaces, entraîné uniquement sur de l'anglais, est appliqué sans modification à du texte japonais, qui n'a pas d'espaces entre les mots. Qu'est-ce qui se passe mal, et que fait SentencePiece différemment pour l'éviter ?

<details markdown="1"><summary>Vérifier</summary>

Le pré-tokenizer par espaces n'a rien de sensé à découper, puisque le japonais ne délimite pas les mots par des espaces, et il ne peut donc pas fournir au BPE des morceaux de la taille d'un mot raisonnables à l'intérieur desquels fusionner. SentencePiece l'évite en s'entraînant directement sur du texte de phrases brutes sans hypothèse de frontières de mots préexistantes, en traitant l'espace comme un symbole ordinaire plutôt que comme un pré-découpage obligatoire.

</details>

2. ▢ Une équipe double la taille du vocabulaire de son tokenizer tout en gardant exactement la même dimension cachée et la même profondeur pour le modèle. Laquelle de ces affirmations décrit le mieux le résultat ?

    - a) Les séquences raccourcissent en moyenne, et les tables d'embeddings et de sortie rétrécissent
    - b) Les séquences raccourcissent en moyenne, mais les tables d'embeddings et de sortie grandissent
    - c) Les séquences s'allongent en moyenne, mais les tables d'embeddings et de sortie rétrécissent
    - d) Ni la longueur des séquences ni le nombre de paramètres ne sont affectés par la taille du vocabulaire

<details markdown="1"><summary>Indice</summary>

La taille du vocabulaire affecte deux choses différentes : en combien de tokens un morceau de texte se transforme, et la taille de la table qui associe chaque token à un vecteur. Considérez chacune séparément.

</details>

<details markdown="1"><summary>Vérifier</summary>

**b)** Un vocabulaire plus grand signifie que davantage de sous-chaînes courantes obtiennent leur propre token, ce qui raccourcit les séquences, tandis que les tables d'embeddings et de projection de sortie (généralement liées) croissent directement avec la taille du vocabulaire, et grandissent donc. (a) et (c) se trompent chacune de sens sur l'un des deux effets, et (d) ignore les deux.

</details>

3. ▢ Nommez un axe sur lequel un vocabulaire plus petit est meilleur qu'un plus grand, et un axe sur lequel il est pire.

<details markdown="1"><summary>Vérifier</summary>

Meilleur : un signal d'entraînement par token plus dense (chaque token est vu plus souvent par passe sur le même corpus), ou une table d'embeddings et de sortie plus petite. Pire : des séquences de tokens plus longues par entrée, puisque les mots ordinaires sont découpés en davantage de morceaux, ce qui coûte plus de calcul à attendre et à générer.

</details>

4. ▢ Laquelle de ces affirmations décrit le mieux ce qu'est SentencePiece, en tant que logiciel ?

    - a) Un nouvel algorithme de tokenisation unique qui remplace le byte-pair encoding
    - b) Une boîte à outils qui implémente à la fois le byte-pair encoding et un entraîneur de modèle de langue unigramme, directement sur du texte brut sans étape de pré-tokenisation requise
    - c) Seulement un pré-tokenizer, destiné à être exécuté avant une implémentation BPE distincte
    - d) Une manière d'entraîner un modèle sans aucun vocabulaire fixe

<details markdown="1"><summary>Vérifier</summary>

**b)** SentencePiece regroupe deux algorithmes d'entraînement, le byte-pair encoding et un modèle de langue unigramme, et sa caractéristique distinctive est de s'entraîner directement à partir de phrases brutes. (a) est faux parce qu'il implémente toujours le BPE au lieu de le remplacer. (c) inverse l'apport réel de SentencePiece, qui est de supprimer l'étape de pré-tokenisation. (d) ne décrit aucun vrai tokenizer abordé dans ce parcours ; les deux algorithmes produisent toujours un vocabulaire fixe.

</details>

## Exercices en situation réelle

- [ ] Trouvez la taille de vocabulaire déclarée d'un tokenizer auquel vous avez accès, que ce soit via une bibliothèque ou via les fichiers de tokenizer publiés d'un modèle hébergé.
- [ ] Si vous pouvez accéder à deux tokenizers dont les tailles de vocabulaire diffèrent nettement, encodez la même phrase avec les deux et comparez directement les nombres de tokens obtenus.
- [ ] Demain : pour un projet ou un cas d'usage dont vous connaissez l'échelle (un assistant de chat, un modèle centré sur le code, un outil pour une langue peu dotée), décidez qualitativement si vous pencheriez pour un vocabulaire plus grand ou plus petit que celui d'un modèle courant, et notez quel axe unique du compromis a motivé votre réponse.

## Pour aller plus loin

- [Article : "SentencePiece: A simple and language independent subword tokenizer and detokenizer for Neural Text Processing", Kudo et Richardson, 2018](https://arxiv.org/abs/1808.06226)
- [Ressources](../RESOURCES.md)

---

L'étape 1 a couvert ce qui entre dans un corpus et ce qui en est retiré ; l'étape 2 a couvert la manière dont ce corpus est transformé en tokens. L'étape 3 aborde la question qui se pose au-dessus des deux : étant donné un nombre de paramètres, combien de ces tokens valent la peine d'être utilisés pour l'entraînement.

Ça ne passe pas ? Relisez la source primaire en haut de page, car cette leçon la condense et c'est dans la condensation que la compréhension s'échappe. Consultez le [glossaire](../GLOSSARY.md) pour tout terme qui vous a paru glissant.

Si c'est la leçon elle-même qui n'est pas claire plutôt que la matière, c'est un défaut : [ouvrez une issue](https://github.com/TokenCemetery/teach/issues).
