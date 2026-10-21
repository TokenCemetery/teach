---
title: "3. Le byte-pair encoding depuis zéro"
description: "L'algorithme qui transforme les mots rares et inconnus en séquences d'unités de sous-mots apprises, déroulé à la main"
type: lesson
---

# Leçon 3. Le byte-pair encoding depuis zéro

**Lien avec la mission :** « Entraîner un tokenizer et défendre une taille de vocabulaire au regard de son effet sur la longueur des séquences et sur la taille de la table d'embeddings » est le deuxième point sous Objectif. Cette leçon construit l'algorithme que la plupart des tokenizers utilisent encore ; la leçon 4 couvre le compromis sur la taille du vocabulaire lui-même.
**Source primaire :** [Article : "Neural Machine Translation of Rare Words with Subword Units", Sennrich et al., 2015](https://arxiv.org/abs/1508.07909)
**Prérequis :** [Leçon 2](0002-deduplication-and-quality-filtering.md)

## Échauffement

1. ▢ Nommez une chose que la déduplication retire d'un corpus, et une chose que le filtrage de qualité retire et que la déduplication n'attraperait pas.

<details markdown="1"><summary>Vérifier</summary>

La déduplication retire le texte répété ou quasi répété qui existe déjà ailleurs dans le corpus. Le filtrage de qualité retire le texte de faible valeur qui n'est la copie de rien, comme le texte générique ou généré par machine, que la déduplication n'a aucun moyen de détecter.

</details>

## À savoir

### Pourquoi un vocabulaire fixe de mots se brise

Un modèle qui prédit un mot parmi une liste fixe de mots entiers n'a aucun moyen de gérer un mot qui ne figurait pas dans cette liste : un nom rare, un mot composé nouveau, une faute de frappe, un mot dans une écriture que la liste n'avait pas anticipée. Sennrich et al. l'ont dit sans détour pour la traduction, où c'est inévitable, puisque la traduction est fondamentalement un problème à vocabulaire ouvert : aucune liste fixe de mots, aussi grande soit-elle, ne couvre tous les noms, nombres et néologismes qu'un vrai texte contiendra. Leur solution a été de cesser complètement de tokeniser en mots entiers, et de tokeniser plutôt en **unités de sous-mots** : des morceaux plus petits qu'un mot, construits pour qu'un mot rare ou jamais vu puisse tout de même s'épeler à partir de morceaux que le modèle a déjà rencontrés.

### L'algorithme : fusionner la paire la plus fréquente, recommencer

Le byte-pair encoding était à l'origine un algorithme de compression de données, réutilisé ici pour un autre travail. Il part du plus petit vocabulaire possible, les caractères individuels, et construit vers le haut :

1. Partir de chaque mot du texte d'entraînement découpé en ses caractères individuels, plus un marqueur de fin de mot.
2. Compter la fréquence de chaque paire de symboles adjacents, sur l'ensemble du texte (pondéré par les fréquences).
3. Fusionner la paire unique la plus fréquente en un nouveau symbole, partout où elle apparaît.
4. Répéter les étapes 2 et 3 pour un nombre fixe de fusions.

Le nombre de fusions est le seul hyperparamètre, et il fixe directement la taille du vocabulaire : le vocabulaire final est le jeu de caractères de départ plus un nouveau symbole par fusion effectuée. Un mot qui n'est jamais entièrement fusionné en un seul symbole est représenté par une courte séquence des morceaux en lesquels il a été fusionné, ce qui est exactement ce qui permet d'encoder un mot jamais vu : il retombe sur des morceaux plus petits, déjà connus, plutôt que sur un unique symbole de mot inconnu.

### Un exemple détaillé

L'article de Sennrich et al. donne directement ce corpus jouet : quatre mots, déjà découpés en caractères avec `</w>` marquant la fin de chaque mot, chacun portant une fréquence :

```text
{'l o w </w>': 5, 'l o w e r </w>': 2, 'n e w e s t </w>': 6, 'w i d e s t </w>': 3}
```

En comptant chaque paire adjacente, pondérée par la fréquence de chaque mot, trois paires arrivent à égalité pour la plus fréquente, avec un compte pondéré de 9 chacune : `(e, s)`, `(s, t)` et `(t, </w>)`. Chacun des deux mots contenant « est » (`newest`, de fréquence 6, et `widest`, de fréquence 3) apporte une occurrence de chaque paire de cette sous-chaîne commune, donc `6 + 3 = 9` pour les trois. La règle de l'algorithme, « fusionner la paire unique la plus fréquente », ne dit pas à elle seule laquelle de trois paires exactement à égalité fusionner d'abord : ce détail est laissé à ce que fait l'implémentation quand elle doit départager une égalité, et non à la définition de l'algorithme. Fusionner l'une des trois ne lève pas non plus l'égalité : comme les trois paires proviennent de la même sous-chaîne répétée « est », fusionner l'une d'elles (disons `e`+`s` en `es`) ne fait que rebaptiser les autres en nouvelles paires adjacentes au même compte (`es`+`t` et `t`+`</w>` restent à égalité à 9), de sorte que les trois sont réunies en quelques fusions quelle que soit celle choisie en premier, et que `newest` et `widest` finissent tous deux par partager un seul morceau `est`.

## Pratique

1. ▢ À partir du corpus de l'exemple détaillé, `{'l o w </w>': 5, 'l o w e r </w>': 2, 'n e w e s t </w>': 6, 'w i d e s t </w>': 3}`, calculez le compte pondéré de la paire adjacente `(l, o)`.

<details markdown="1"><summary>Indice</summary>

`(l, o)` apparaît une fois par occurrence d'un mot commençant par « lo… ». De quels mots s'agit-il, et avec quelles fréquences ?

</details>

<details markdown="1"><summary>Vérifier</summary>

`(l, o)` apparaît dans `low` (fréquence 5) et dans `lower` (fréquence 2), ce qui donne `5 + 2 = 7`.

</details>

2. ▢ Pourquoi la définition même de l'algorithme, « fusionner la paire unique la plus fréquente », ne détermine-t-elle pas complètement quelle paire est fusionnée en premier dans ce corpus ?

<details markdown="1"><summary>Vérifier</summary>

Parce que trois paires, `(e, s)`, `(s, t)` et `(t, </w>)`, sont exactement à égalité au compte pondéré le plus élevé, 9. La règle dit quoi faire quand il existe une paire la plus fréquente unique ; elle ne dit rien sur laquelle choisir parmi plusieurs paires à égalité, si bien que ce choix vient de ce que fait l'implémentation en cas d'égalité, et non de l'algorithme tel qu'énoncé.

</details>

3. ▢ On donne à un tokenizer entraîné avec 500 fusions un mot qu'il n'a jamais vu pendant l'entraînement. Que se passe-t-il, et en quoi cela diffère-t-il de ce que ferait un vocabulaire fixe de mots entiers ?

    - a) Il est remplacé par un unique symbole générique de « mot inconnu », le même résultat que produirait un vocabulaire de mots entiers
    - b) L'entraînement échoue, puisque le tokenizer n'a aucune règle pour une entrée inconnue
    - c) Il est épelé comme une courte séquence de morceaux plus petits que le tokenizer a déjà appris, au lieu de se réduire à un unique symbole de mot inconnu
    - d) Le tokenizer ajoute automatiquement une nouvelle règle de fusion pour lui sur-le-champ

<details markdown="1"><summary>Vérifier</summary>

**c)** Le mot inconnu retombe sur les morceaux plus petits, jusqu'aux caractères individuels si nécessaire, que les fusions d'entraînement ont déjà produits. (a) décrit exactement le mode d'échec que la tokenisation en sous-mots a été conçue pour éviter. (b) et (d) ne décrivent pas le comportement d'un jeu fixe de règles de fusion entraîné au moment du test.

</details>

4. ▢ Quelle raison propre au domaine Sennrich et al. ont-ils donnée pour justifier le besoin d'une approche à vocabulaire ouvert ?

<details markdown="1"><summary>Vérifier</summary>

La traduction est fondamentalement un problème à vocabulaire ouvert : les noms, les mots composés et les emprunts font qu'aucune liste fixe de mots, aussi grande soit-elle, ne peut couvrir tous les mots qu'un vrai texte d'entrée contiendra.

</details>

## Exercices en situation réelle

- [ ] À la main ou dans un tableur, prenez le corpus de l'exemple détaillé et calculez le compte pondéré de chaque paire adjacente après que `(e, s)` a été fusionnée en `es` (de sorte que `newest` devient `n e w es t </w>` et `widest` devient `w i d es t </w>`). Confirmez quelle(s) paire(s) sont maintenant à égalité pour la plus fréquente.
- [ ] Trouvez le fichier de vocabulaire du tokenizer de n'importe quel modèle ouvert auquel vous avez accès (beaucoup sont publiés avec le modèle). Cherchez-y un mot courant de votre propre nom ou d'un nom que vous connaissez, et regardez s'il existe comme un seul token ou s'il est découpé en morceaux.
- [ ] Demain : choisissez cinq mots de votre propre langue que vous pensez mal servis par un petit vocabulaire de sous-mots (termes techniques rares, noms, mots composés), et prédisez, en une phrase par mot, comment un tokenizer BPE découperait probablement chacun d'eux.

## Pour aller plus loin

- [Article : "Neural Machine Translation of Rare Words with Subword Units", Sennrich et al., 2015](https://arxiv.org/abs/1508.07909)
- [Ressources](../RESOURCES.md)

---

Ça ne passe pas ? Relisez la source primaire en haut de page, car cette leçon la condense et c'est dans la condensation que la compréhension s'échappe. Consultez le [glossaire](../GLOSSARY.md) pour tout terme qui vous a paru glissant.

Si c'est la leçon elle-même qui n'est pas claire plutôt que la matière, c'est un défaut : [ouvrez une issue](https://github.com/TokenCemetery/teach/issues).
