---
title: "3. Métriques propres à la tâche"
description: "Exact match, F1 au niveau des tokens et BLEU/ROUGE, et le mode de défaillance de chacun"
type: lesson
---

# Leçon 3. Métriques propres à la tâche

**Lien avec la mission :** L'étape 2 ouvre la moitié « construire l'eval » de la mission : une métrique propre à la tâche transforme un jeu held-out (étape 1) en un vrai chiffre, et chaque métrique de cette leçon convient bien à certaines tâches et ment discrètement sur d'autres.
**Source primaire :** [Doc : Evaluate, Hugging Face](https://huggingface.co/docs/evaluate/index)
**Prérequis :** [Leçon 2](0002-designing-contamination-resistance.md), [Contamination des données](../GLOSSARY.md)

## Échauffement

1. ▢ Contre quoi l'intégration d'une chaîne canari dans un jeu d'eval sur mesure protège-t-elle réellement ?

<details markdown="1"><summary>Vérifier</summary>

Elle signale aux crawlers qui assemblent un corpus d'entraînement que le contenu marqué doit être exclu, et elle offre un moyen de détecter une fuite plus tard si la chaîne apparaît dans la sortie d'un modèle ou dans un corpus accessible. C'est une demande, pas une garantie : elle dépend du respect de la convention par les crawlers.

</details>

2. ▢ Quand un contrôle de recouvrement de n-grammes face à un corpus connu est-il utilisable, et quand cesse-t-il d'être une option ?

<details markdown="1"><summary>Vérifier</summary>

Il est utilisable quand le corpus de pré-entraînement est connu et accessible. Il cesse d'être une option pour un modèle fermé dont les données d'entraînement ne sont pas divulguées, où le test d'instruction guidée reste l'outil disponible.

</details>

## À savoir

### Exact match : strict, et fragile face à tout ce qui est superficiel

L'**exact match** ne juge une prédiction correcte que si elle correspond à une réponse de référence caractère pour caractère (souvent après une normalisation légère comme le passage en minuscules ou la suppression des espaces). Il convient aux tâches qui n'ont qu'une seule réponse clairement correcte : choix multiple, extraction de span, résultat mathématique. Son mode de défaillance est exactement ce que sa rigueur implique : une réponse correcte formulée autrement (`"Paris"` face à une référence `"Paris, France"`) est notée fausse, ce qui pénalise la justesse au lieu de la mesurer, à moins que la normalisation appliquée soit assez généreuse pour absorber cette variation sans absorber aussi des réponses réellement fausses.

### F1 au niveau des tokens : un crédit partiel, au prix de l'indifférence à l'ordre

Le **F1** (tel qu'utilisé pour les tâches extractives comme le question-réponse par span) traite une prédiction et une référence comme des sacs de tokens au lieu d'exiger une correspondance exacte de chaîne, en calculant la précision (quelle fraction des tokens de la prédiction est correcte) et le rappel (quelle fraction des tokens de la référence a été produite), puis leur moyenne harmonique. La référence "the cat sat on the mat" (tokens : `the, cat, sat, on, the, mat`) face à la prédiction "a cat sat on the mat" (tokens : `a, cat, sat, on, the, mat`) partage cinq tokens (`cat, sat, on, the, mat`) sur six de chaque côté : précision `5/6`, rappel `5/6`, F1 `5/6 ≈ 0.83`. C'est plus indulgent que l'exact match, qui noterait cette paire franchement fausse. Le mode de défaillance, c'est ce que coûte cette indulgence : un F1 sur un sac de tokens est aveugle à l'ordre et au fait que les mots communs forment ou non une réponse correcte, si bien qu'une prédiction qui brouille les bons mots en une mauvaise affirmation peut quand même obtenir un score élevé.

![Référence "the cat sat on the mat" et prédiction "a cat sat on the mat" disposées en cases de tokens. cat, sat, on, mat et une occurrence de the sont communs aux deux. Le second the de la référence et le a de la prédiction restent chacun sans correspondance. Cinq tokens sur six correspondent de chaque côté, donc la précision vaut 5/6, le rappel vaut 5/6 et le F1 vaut 5/6.](images/f1-token-overlap.svg)

### BLEU et ROUGE : recouvrement de n-grammes avec une référence, conçus pour la traduction et le résumé

**BLEU** (à l'origine pour la traduction automatique) et **ROUGE** (à l'origine pour le résumé) notent tous deux un texte généré selon l'importance du recouvrement de ses n-grammes (séquences contiguës de n tokens) avec un ou plusieurs textes de référence, au lieu d'exiger une correspondance exacte ou de noter des tokens isolés. Leur mode de défaillance apparaît le plus nettement sur la génération ouverte : une paraphrase valide qui dit la même chose avec d'autres mots, "Critics praised the show" face à une référence "The show received positive reviews from critics", partage très peu de n-grammes avec la référence bien qu'elle soit une réponse tout aussi bonne, et obtient de ce fait un score bas. Utiliser plusieurs textes de référence par exemple atténue le problème, mais il existe rarement assez de références pour couvrir chaque formulation valable, ce qui explique en grande partie pourquoi ces métriques ne corrèlent que vaguement avec le jugement humain sur du texte ouvert, et pourquoi le LLM-as-judge de l'étape 3 existe comme alternative pour ce cas précis.

### Choisir une métrique, c'est la faire correspondre à ce que « correct » veut dire pour la tâche

L'exact match et le F1 conviennent aux tâches où la justesse est un petit ensemble de réponses bien défini : classification, extraction, arithmétique. BLEU et ROUGE conviennent aux tâches où le recouvrement de surface avec une référence corrèle, vaguement, avec la qualité, utiles comme filtre grossier et peu coûteux en première passe plutôt que comme verdict final. Aucune des deux familles ne convient à une tâche où la justesse est comportementale plutôt que textuelle (le code généré s'exécute-t-il réellement et produit-il la bonne sortie), sujet de la leçon 4, ni à la génération ouverte où le sens compte plus que la formulation, sujet de l'étape 3.

## Pratique

1. ▢ Un modèle répond à une question de géographie par "Paris" alors que la réponse de référence est "Paris, France". L'exact match note cela faux. Est-ce un résultat de notation correct ? Pourquoi ou pourquoi pas ?

<details markdown="1"><summary>Vérifier</summary>

Non, pas vraiment : la réponse est correcte, simplement formulée plus sèchement que la référence. C'est la fragilité de l'exact match face à la variation superficielle. Le remède est soit de normaliser les deux chaînes avant de les comparer (ce qui n'aide que si la normalisation est conçue pour absorber ce type précis de variation), soit de choisir une métrique plus indulgente pour une tâche où la formulation varie à ce point.

</details>

2. ▢ Référence : "a fast red fox jumps". Prédiction : "a red fox jumps fast". Avec le F1 en sac de tokens (en ignorant l'ordre des mots), quels sont la précision, le rappel et le score F1 ?

<details markdown="1"><summary>Indice</summary>

Listez les tokens de chaque côté comme un ensemble et comptez combien sont communs, quelle que soit leur position.

</details>

<details markdown="1"><summary>Vérifier</summary>

Les deux côtés ont les mêmes 5 tokens (`a, fast, red, fox, jumps` contre `a, red, fox, jumps, fast`), simplement réordonnés, donc les 5 sont communs. Précision `5/5 = 1.0`, rappel `5/5 = 1.0`, F1 `1.0`. Cela illustre aussi l'aveuglement du F1 à l'ordre : une prédiction à l'ordre des mots brouillé obtient le même score que celle qui le préserve, alors que l'ordre des mots peut changer le sens d'une manière que le F1 ne sait pas détecter.

</details>

3. ▢ Un modèle de résumé produit "Critics praised the show" pour un résumé de référence "The show received positive reviews from critics." ROUGE noterait-il probablement cette paire haut ou bas, et ce résultat reflète-t-il équitablement la qualité de la prédiction ?

<details markdown="1"><summary>Vérifier</summary>

Bas, puisque les deux phrases partagent très peu de n-grammes contigus bien qu'elles disent essentiellement la même chose avec d'autres mots. Ce n'est pas un reflet équitable de la qualité : la prédiction est une paraphrase valide, mais ROUGE mesure le recouvrement de n-grammes de surface, pas le sens, donc une réponse correcte formulée autrement que la référence est pénalisée comme le serait une réponse fausse.

</details>

4. ▢ Une équipe évalue un modèle sur un benchmark à choix multiple avec une seule lettre correcte par question. Quelle métrique de cette leçon convient le mieux, et pourquoi ?

<details markdown="1"><summary>Vérifier</summary>

L'exact match. La tâche a exactement une réponse correcte par question, sans variation de surface significative à absorber (la réponse est une seule lettre), ce qui est exactement la forme de tâche pour laquelle l'exact match est conçu, sans qu'on ait aucun besoin de l'indulgence du F1 ou de BLEU/ROUGE pour un recouvrement partiel ou paraphrasé.

</details>

5. ▢ Laquelle de ces affirmations est vraie de BLEU et ROUGE par rapport à l'exact match et au F1 ?

    - a) Ils exigent une réponse correcte unique et sans ambiguïté, comme l'exact match
    - b) Ils notent le recouvrement avec un texte de référence au niveau des n-grammes, ce qui ne corrèle que vaguement avec la qualité sur de la génération ouverte
    - c) Ils sont à l'abri du problème de paraphrase qui touche l'exact match
    - d) Il vaut mieux les utiliser comme verdict final pour toute tâche de génération, en remplacement d'un jugement humain ou d'un juge LLM

<details markdown="1"><summary>Vérifier</summary>

**b)** Le recouvrement de n-grammes est un indicateur approximatif de la qualité, surtout quand les réponses valables peuvent se formuler de nombreuses manières. (a) est faux : ils sont conçus pour des tâches à texte ouvert, pas pour une réponse unique et fixe. (c) est faux : une paraphrase valide peut obtenir un score bas en BLEU/ROUGE pour la même raison de fond qui lui fait échouer l'exact match, une formulation de surface différente. (d) est faux : leur faible corrélation avec le jugement humain sur du texte ouvert est précisément la raison pour laquelle l'étape 3 introduit le LLM-as-judge comme alternative.

</details>

## Exercices en situation réelle

- [ ] Choisissez une tâche que vous évaluez (ou prévoyez d'évaluer) et décidez lequel de l'exact match, du F1 ou de BLEU/ROUGE correspond à sa notion de « correct », en notant pourquoi.
- [ ] Pour une eval qui utilise actuellement BLEU ou ROUGE, trouvez un exemple où une réponse clairement correcte, formulée autrement, obtiendrait un mauvais score, et notez-le.
- [ ] Demain : lisez un paragraphe de la doc Hugging Face Evaluate sur une métrique que vous n'avez pas encore utilisée et notez le mode de défaillance qu'elle indique.

## Pour aller plus loin

- [Doc : Evaluate, Hugging Face](https://huggingface.co/docs/evaluate/index)
- [Doc : "Define success criteria and build evaluations", Claude Platform Docs](https://platform.claude.com/docs/en/test-and-evaluate/develop-tests)
- [Ressources](../RESOURCES.md)

---

Ça ne passe pas ? Relisez la source primaire en haut de page, car cette leçon la condense et c'est dans la condensation que la compréhension s'échappe. Consultez le [glossaire](../GLOSSARY.md) pour tout terme qui vous a paru glissant.

Si c'est la leçon elle-même qui n'est pas claire plutôt que la matière, c'est un défaut : [ouvrez une issue](https://github.com/TokenCemetery/teach/issues).
