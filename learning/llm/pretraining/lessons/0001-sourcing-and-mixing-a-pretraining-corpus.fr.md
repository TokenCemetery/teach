---
title: "1. Sourcer et mélanger un corpus de pré-entraînement"
description: "Ce qui entre dans un corpus de pré-entraînement, et pourquoi le mélange des sources compte plus que le nombre total d'octets"
type: lesson
---

# Leçon 1. Sourcer et mélanger un corpus de pré-entraînement

**Lien avec la mission :** « Construire un corpus de pré-entraînement dédupliqué et filtré sur la qualité à partir de sources brutes, et dire ce que retire chaque étape de filtrage et pourquoi » est le premier point sous Objectif. Cette leçon couvre la moitié sourcing et mélange ; la leçon 2 couvre la déduplication et le filtrage de qualité.
**Source primaire :** [Article : "The Pile: An 800GB Dataset of Diverse Text for Language Modeling", Gao et al., 2020](https://arxiv.org/abs/2101.00027)
**Prérequis :** aucun

## À savoir

### De quoi se compose un corpus de pré-entraînement

Un corpus de pré-entraînement est la collection brute de documents sur laquelle un modèle s'entraîne avant que quoi que ce soit en soit tokenisé : crawls du web, livres, dépôts de code, articles académiques, messages de forums, sites de référence, et bien d'autres, rassemblés à partir de nombreuses sources distinctes plutôt que collectés dans un seul crawl géant. Traiter « le corpus » comme un tas de texte unique et indifférencié cache la décision qui façonne réellement ce que le modèle apprend, c'est-à-dire quelles sources sont entrées et quelle part du corpus final chacune représente.

### Sourcer est une décision de mélange, pas seulement une décision d'inclusion

The Pile est un exemple détaillé utile parce que ses auteurs ont documenté leur raisonnement au lieu de simplement livrer le jeu de données. Il assemble 825 GiB de texte à partir de 22 sous-ensembles variés et de grande qualité, dont beaucoup proviennent de sources académiques ou professionnelles (dossiers juridiques, articles académiques, documentation technique) qu'un crawl web généraliste sous-représente. L'évaluation de l'article rend le propos concret : GPT-2 et GPT-3, qui ne se sont entraînés ni l'un ni l'autre sur The Pile, peinent sur plusieurs de ses composantes, « comme l'écriture académique », alors que les modèles entraînés sur The Pile s'améliorent nettement par rapport aux modèles entraînés sur Raw Common Crawl ou CC-100, sur chacune des composantes de The Pile comme sur les évaluations en aval.

Ce résultat ne porte pas vraiment sur la taille totale. Il porte sur les domaines qui ont été inclus, et c'est pourquoi « quelle est la taille du corpus » est la mauvaise première question à poser sur un run de pré-entraînement.

### La proportion est le levier, pas seulement la présence

Une fois une source incluse, une seconde décision reste à prendre : quelle part du budget final de tokens elle obtient. Une source qui domine le nombre d'octets bruts d'internet (bavardage de forums, textes marketing, texte de navigation générique) n'a pas automatiquement droit à dominer le corpus, et une source petite en octets bruts mais dense en information (texte académique sélectionné, documentation de référence) n'est pas condamnée à la part qu'elle occupe naturellement. Le concepteur d'un corpus choisit de suréchantillonner certaines sources par rapport à leur taille naturelle et d'en plafonner d'autres bien en dessous, et ce choix est indépendant de la décision d'inclure la source, et pris après elle.

Deux corpus peuvent inclure exactement la même liste de sources et se comporter pourtant différemment une fois entraînés, si leurs proportions diffèrent. C'est pourquoi « mélange » et « sourcing » sont deux décisions distinctes qui méritent d'être nommées séparément, même si un tableau de noms de jeux de données les fait passer pour la même chose.

### Le corpus est un artefact de conception

Le sourcing et le mélange ont lieu avant qu'un seul token d'entraînement ne tourne, et ils pèsent autant que n'importe quel hyperparamètre choisi ensuite. Un modèle entraîné sur un corpus mal composé gaspille du calcul à réapprendre des motifs redondants ou de faible valeur, aussi bien exécutées que soient les étapes ultérieures d'un run de pré-entraînement (le partitionnement ZeRO de l'étape 5, le schéma de learning rate de l'étape 7). Ces étapes ultérieures rendent l'entraînement efficace ; cette étape-ci décide de ce qu'il y aura à apprendre efficacement.

## Pratique

1. ▢ The Pile a assemblé 825 GiB de texte à partir de 22 sources variées plutôt que de collecter un seul crawl web de cette même taille. D'après l'évaluation de l'article lui-même, qu'ont fait GPT-2 et GPT-3 (qui ne se sont pas entraînés sur The Pile) sur plusieurs composantes de The Pile, et que dit ce résultat sur le fait de s'appuyer uniquement sur du texte issu de crawls web ?

<details markdown="1"><summary>Vérifier</summary>

Ils ont peiné, en particulier sur des composantes comme l'écriture académique. C'est une preuve directe qu'un corpus construit surtout à partir de texte web généraliste laisse un modèle avec une exposition mince à des genres entiers, quelle que soit la quantité de texte web qu'il a vue.

</details>

2. ▢ Une équipe double le nombre d'octets bruts de sa composante crawl web tout en laissant fixe le nombre d'octets de chaque autre source, sans autre changement dans la conception du corpus. Que devient le mélange ?

    - a) Le mélange est inchangé, puisque le sourcing ne concerne que les sources incluses, pas la quantité de chacune
    - b) La part du crawl web dans le corpus final augmente, même si personne n'a délibérément décidé d'en faire une fraction plus grande de ce dont le modèle apprend
    - c) Le mélange ne compte que pour l'entraînement du tokenizer, pas pour le modèle lui-même
    - d) Doubler la taille d'une source quelconque améliore toujours les performances en aval

<details markdown="1"><summary>Indice</summary>

Rien n'a changé quant aux sources présentes ici. Demandez-vous ce qui a changé dans la part du total que chacune apporte.

</details>

<details markdown="1"><summary>Vérifier</summary>

**b)** La part du crawl web augmente par défaut, comme effet secondaire accidentel d'un changement de nombre d'octets, et non parce que quelqu'un a décidé que le modèle devait apprendre de façon disproportionnée davantage à partir de lui. (a) confond inclusion et proportion, ce qui est précisément la distinction que trace cette leçon. (c) est faux : le mélange façonne ce sur quoi le modèle est entraîné, pas seulement la manière dont le vocabulaire est construit. (d) est faux en général ; davantage d'une source pauvre en information peut diluer un corpus au lieu de l'améliorer.

</details>

3. ▢ Un corpus nouvellement assemblé répète plusieurs fois, par rapport à sa part naturelle, une petite collection de 2 Go de dossiers juridiques sélectionnés, tout en plafonnant bien en dessous de sa part naturelle une composante de 400 Go de crawl web brut. Les deux sources avaient déjà été retenues pour inclusion avant cette décision. S'agit-il d'une décision de sourcing ou d'une décision de mélange, et pourquoi ?

<details markdown="1"><summary>Vérifier</summary>

Une décision de mélange. L'ensemble des sources n'a pas changé ; les deux étaient déjà présentes. Ce qui a changé, c'est la part du budget final de tokens que chacune est autorisée à apporter, ce qui est précisément la question de proportion que cette leçon sépare de la question d'inclusion.

</details>

## Exercices en situation réelle

- [ ] Lisez la liste des sources composantes dans l'article The Pile (son tableau 1, dans l'article lié) et notez lesquelles, deux ou trois, vous semblent les plus surprenantes dans un corpus d'entraînement de modèle de langage, et pourquoi vous n'auriez pas pensé à les inclure.
- [ ] Trouvez la composition documentée d'un corpus de pré-entraînement ouvert connu que vous n'avez pas examiné auparavant (RedPajama, Dolma ou FineWeb sont tous documentés publiquement). Notez approximativement quelle fraction est du texte web généraliste issu de crawls et quelle fraction provient de sources sélectionnées ou structurées.
- [ ] Demain : esquissez un mélange de corpus hypothétique pour un modèle que vous voudriez exceptionnellement bon dans un domaine précis (raisonnement juridique, littérature scientifique, un langage de programmation). Nommez quatre ou cinq types de sources que vous inclueriez et, pour chacun, dites avec vos propres mots si vous le suréchantillonneriez au-dessus de sa part naturelle, le plafonneriez en dessous ou le laisseriez tel quel, et pourquoi.

## Pour aller plus loin

- [Article : "The Pile: An 800GB Dataset of Diverse Text for Language Modeling", Gao et al., 2020](https://arxiv.org/abs/2101.00027)
- [Ressources](../RESOURCES.md)

---

Ça ne passe pas ? Relisez la source primaire en haut de page, car cette leçon la condense et c'est dans la condensation que la compréhension s'échappe. Consultez le [glossaire](../GLOSSARY.md) pour tout terme qui vous a paru glissant.

Si c'est la leçon elle-même qui n'est pas claire plutôt que la matière, c'est un défaut : [ouvrez une issue](https://github.com/TokenCemetery/teach/issues).
