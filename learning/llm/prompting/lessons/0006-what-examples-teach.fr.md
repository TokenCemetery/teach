---
title: "6. Ce qu'enseignent les exemples few-shot"
description: "Les démonstrations enseignent surtout le format, l'espace des labels et la distribution des entrées, ce qui change la façon de les choisir"
type: lesson
---

# Leçon 6. Ce qu'enseignent les exemples few-shot

**Lien avec la mission :** Bien choisir des exemples few-shot commence par savoir ce que le modèle en retire, et les preuves disent que ce sont moins les réponses que la forme de la tâche.
**Source primaire :** [Article : "Rethinking the Role of Demonstrations", Min et al., 2022](https://arxiv.org/abs/2202.12837)
**Prérequis :** [Leçon 5](0005-format-sensitivity.md), [Prompt few-shot](../GLOSSARY.md), [Prompt zero-shot](../GLOSSARY.md)

## Échauffement

1. ▢ La leçon 4 séparait les instructions des données avec des balises. Nommez un élément d'un prompt few-shot qui devrait se trouver dans sa propre balise, et pourquoi.

<details markdown="1"><summary>Vérifier</summary>

Les exemples, regroupés (par exemple dans une balise examples avec une balise par exemple), pour que le modèle puisse distinguer les démonstrations des instructions et de l'entrée réelle. Sans balises, un exemple peut être lu comme une instruction, ou l'entrée réelle comme un exemple de plus.

</details>

2. ▢ La leçon 5 disait qu'un changement de formatage sans signification peut faire varier la précision. Que prédit cela pour deux prompts few-shot dont les exemples sont identiques mais dont l'un écrit `Label:` et l'autre `Answer:` ?

<details markdown="1"><summary>Vérifier</summary>

Que leur précision peut différer, donc qu'on ne sait pas lequel est meilleur tant que les deux ne sont pas testés. La modification ne change aucun sens, mais elle change la séquence de tokens que le modèle prolonge, ce qui est le propos de la leçon 5.

</details>

## À savoir

### Le résultat surprenant

Un **prompt few-shot** montre au modèle des paires entrée-sortie avant l'entrée réelle. L'hypothèse évidente est que le modèle apprend à partir d'elles la correspondance entrée-sortie, comme un classifieur apprend à partir de données étiquetées. Min et al. ont testé cette hypothèse en remplaçant les labels des démonstrations par des labels aléatoires. Sur 12 modèles, dont GPT-3, la performance n'a presque pas baissé : de 0 à 5 % en absolu pour presque tous les modèles, 2,6 % en moyenne pour les tâches de classification et 1,7 % pour les tâches à choix multiples.

Si ce ne sont pas les labels corrects qui aident, quelque chose d'autre dans les démonstrations doit le faire. L'article en nomme trois, chacun testé en le supprimant :

| Ce que fournit la démonstration | Ce qui se passe quand on le supprime |
|---|---|
| L'espace des labels : l'ensemble des réponses que le modèle peut donner | Remplacer les labels par des mots anglais aléatoires a coûté de 5 à 16 % en absolu pour les modèles directs |
| La distribution des entrées : du texte qui ressemble aux entrées réelles | Remplacer les entrées par du texte aléatoire d'un corpus a coûté de 3 à 16 % en absolu pour la plupart des modèles testés |
| Le format : entrée puis label, répétés | Supprimer l'appariement a laissé la performance proche de l'absence de démonstrations, voire pire |

### Ce que cela ne dit pas

Trois limites empêchent d'en faire « les labels n'ont pas d'importance ».

Les modèles allaient de GPT-2 Large à GPT-3 (de 774 M à 175 Md de paramètres), et les tâches étaient de la classification et du choix multiple. L'article ne teste pas si un modèle de chat actuel se comporte de la même façon : traitez-le donc comme un a priori solide, puis testez votre propre modèle.

Des labels aléatoires coûtent quand même quelque chose, et le coût n'était pas uniforme : un modèle en classification a chuté de près de 10 % quand tous les labels étaient faux. « Ne nuit presque pas » est une moyenne sur les modèles et les tâches testés.

Les auteurs notent aussi que l'apprentissage en contexte peut ne pas fonctionner sur une tâche dont le modèle n'a pas déjà capturé la correspondance entrée-label. Les démonstrations localisent une tâche que le modèle sait déjà largement faire. Elles sont un moyen plus faible de lui enseigner une correspondance qu'il n'a jamais vue.

### Comment cela change le choix des exemples

Si le modèle lit le format, l'espace des labels et la distribution des entrées dans les exemples, ce sont ces trois éléments qu'il faut soigner.

- **Dans le format cible.** Chaque exemple doit ressembler exactement à l'entrée réelle et à la sortie voulue, jusqu'à la casse et la ponctuation. La leçon 5 explique pourquoi de petites différences ne sont pas gratuites.
- **Couvrant l'espace des labels.** Montrez chaque label que le modèle peut produire, pour qu'aucun ne soit une surprise.
- **Comme les entrées réelles.** Utilisez du texte issu de la distribution réelle, pas des phrases inventées et soignées.

Le guide des bonnes pratiques d'Anthropic dit la même chose en termes de praticien : rendre les exemples pertinents (refléter le cas d'usage réel), variés (couvrir les cas limites et varier assez pour que le modèle ne capte pas des motifs involontaires) et structurés (enveloppés dans des balises), et il suggère 3 à 5 exemples. C'est le conseil documenté d'un seul éditeur, pas un résultat mesuré.

Rien de tout cela n'autorise à livrer de mauvais labels. Des labels corrects ne coûtent rien et évitent le pire cas de l'article.

## Pratique

1. ▢ Prédisez, puis exécutez. Collez ce prompt dans une fenêtre de chat. Les labels des trois exemples sont volontairement faux. Prédisez ce que le modèle produit pour le dernier avis, puis exécutez.

    ```text
    Classify each review as Positive or Negative.

    Review: The battery lasts all day and the screen is gorgeous.
    Label: Negative

    Review: It stopped working after two days and support never replied.
    Label: Positive

    Review: Arrived on time and works exactly as described.
    Label: Negative

    Review: Terrible fit, the zipper broke on the first use.
    Label:
    ```

<details markdown="1"><summary>Indice</summary>

Demandez-vous ce que les exemples enseignent encore même quand leurs labels sont faux : le format, les deux mots autorisés et à quoi ressemble un avis.

</details>

<details markdown="1"><summary>Vérifier</summary>

Min et al. prédisent une réponse d'un mot parmi la paire autorisée, et pour un avis sans ambiguïté, très probablement la bonne (Negative), parce que le sens propre que le modèle a de la tâche survit à de faux labels. Un modèle qui copie plutôt la correspondance inversée est un constat sur ce modèle, pas une erreur de l'article. Dans les deux cas, le format de sortie (un seul mot après `Label:`) devrait tenir, puisque c'est ce que les exemples ont enseigné de façon fiable.

</details>

2. ▢ Quelle modification d'un prompt few-shot qui fonctionne l'article prédit-il comme la plus nuisible ?

    - a) Permuter les labels pour que certains exemples portent une mauvaise réponse
    - b) Remplacer les entrées des exemples par des phrases aléatoires d'un corpus
    - c) Réordonner les mêmes exemples en gardant chaque label correct
    - d) Ajouter un exemple de plus qui respecte le format existant

<details markdown="1"><summary>Vérifier</summary>

**b)** Remplacer les entrées par du texte hors distribution a coûté de 3 à 16 % en absolu pour la plupart des modèles testés, plus que de mauvais labels (0 à 5 % pour presque tous). (a) est le résultat phare de l'article : un coût faible. (c) n'est pas testé dans cet article ; l'ordre est le sujet de la leçon 7, et il n'est pas anodin. (d) ajoute une démonstration au bon format, ce qui, selon l'article, ne change plus beaucoup les résultats une fois qu'on en a 8 environ.

</details>

3. ▢ Ce prompt est censé étiqueter des tickets de support. Nommez toutes les façons dont ses exemples échouent à enseigner le format, l'espace des labels ou la distribution des entrées, et dites ce que vous changeriez.

    ```text
    Tag the ticket as billing, bug or account.

    Ticket: I was charged twice this month.
    Tag: billing

    This one is a bug report: The export button does nothing.
    bug

    Ticket: How do I change my email address?
    Tag: Account.
    ```

<details markdown="1"><summary>Indice</summary>

Comparez les trois exemples ligne à ligne. Partagent-ils une même mise en page ? Partagent-ils l'orthographe et la ponctuation du label ? Comptez les labels.

</details>

<details markdown="1"><summary>Vérifier</summary>

Format : le deuxième exemple abandonne `Ticket:` et `Tag:` et ajoute une phrase de commentaire, donc le motif est rompu une fois. Espace des labels : `billing`, `bug` et `Account.` diffèrent par la casse et la ponctuation, donc le modèle voit trois orthographes de label là où la tâche a trois labels exacts. Le label `Account.` avec un point enseigne que la ponctuation fait partie de la réponse. Distribution des entrées : les tickets tiennent chacun sur une courte ligne et ne ressemblent peut-être pas à de vrais tickets (plus longs et plus désordonnés). Correction : une seule mise en page pour chaque exemple, l'orthographe exacte du label à chaque fois, et des tickets copiés de vrais tickets.

</details>

4. ▢ Un classifieur doit produire l'un de Billing, Bug, Account. Dans ce lot, choisissez les trois exemples que vous utiliseriez et dites pourquoi vous avez écarté les autres.

    ```text
    A. "I was charged twice for May" -> Billing
    B. "Why did my card get billed two times in May??" -> Billing
    C. "app crashes when I tap export, iOS 17, v4.2" -> Bug
    D. "Our blog post explains how crashes can be diagnosed" -> Bug
    E. "can't log in after changing my phone number" -> Account
    F. "Please update the invoice address" -> Billing
    ```

<details markdown="1"><summary>Vérifier</summary>

Un choix raisonnable est A, C et E : un exemple par label couvre l'espace des labels, ils partagent une mise en page, et leur formulation brute, d'allure réelle, correspond à la distribution des entrées. B est presque un doublon de A, donc n'apporte rien de varié. D est une prose soignée qui ne ressemble pas à un ticket (un décalage de distribution des entrées) et est étiquetée Bug pour la mauvaise raison. F est correct en soi, mais un second exemple Billing avant tout autre label risque le biais que traite la leçon 7. D'autres choix sont défendables s'ils couvrent les trois labels et évitent D.

</details>

## Exercices en situation réelle

- [ ] Prenez un prompt few-shot que vous utilisez déjà. Listez lesquels du format, de l'espace des labels et de la distribution des entrées chaque exemple montre, et signalez tout exemple qui n'en montre aucun.
- [ ] Exécutez un prompt deux fois, une fois avec de vrais exemples et une fois avec les mêmes exemples étiquetés au hasard, sur cinq entrées. Notez combien de réponses ont changé.
- [ ] Demain : réécrivez un prompt few-shot pour que chaque exemple partage une même mise en page et l'orthographe exacte du label, puis exécutez-le sur les cinq mêmes entrées et comparez.

## Pour aller plus loin

- [Few-shot et raisonnement](../reference/few-shot-and-reasoning.md)
- [Article : "Rethinking the Role of Demonstrations", Min et al., 2022](https://arxiv.org/abs/2202.12837)
- [Doc : "Prompting best practices", Claude Platform Docs](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/claude-prompting-best-practices#use-examples-effectively)
- [Ressources](../RESOURCES.md)

---

Ça ne passe pas ? Relisez la source primaire en haut de page, car cette leçon la condense et c'est dans la condensation que la compréhension s'échappe. Consultez le [glossaire](../GLOSSARY.md) pour tout terme qui vous a paru glissant.

Si c'est la leçon elle-même qui n'est pas claire plutôt que la matière, c'est un défaut : [ouvrez une issue](https://github.com/TokenCemetery/teach/issues).
