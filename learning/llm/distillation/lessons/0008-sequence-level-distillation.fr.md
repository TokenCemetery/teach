---
title: "8. Distillation au niveau de la séquence"
description: "Entraîner l'élève sur les sorties décodées de l'enseignant plutôt que sur ses distributions"
type: lesson
---

# Leçon 8. Distillation au niveau de la séquence

**Lien avec la mission :** La mission vous demande de distiller au niveau de la séquence et de dire ce que cela transmet que les logits ne transmettent pas, ce qui commence par la méthode d'origine : entraîner sur ce que décode l'enseignant, et voir pourquoi cela fonctionne.
**Source primaire :** [Article : "Sequence-Level Knowledge Distillation", Kim et Rush, 2016](https://arxiv.org/abs/1606.07947)
**Prérequis :** [Leçon 7](0007-distilling-during-pretraining.md), [Distillation au niveau du token](../GLOSSARY.md), [Distillation au niveau de la séquence](../GLOSSARY.md), [Enseignant](../GLOSSARY.md), [Élève](../GLOSSARY.md)

## Échauffement

1. ▢ La distillation au niveau du token exige deux choses de l'enseignant à chaque position. Lesquelles ?

<details markdown="1"><summary>Vérifier</summary>

La distribution complète du token suivant de l'enseignant (ses logits), et un vocabulaire que l'élève partage, pour que les deux distributions s'alignent index par index. La leçon 6 a traité le second : avec des tokenizers différents, il n'y a pas d'index partagé à comparer.

</details>

2. ▢ La KL directe et la KL inverse font toutes deux correspondre l'élève à l'enseignant. Laquelle étale l'élève sur tous les modes de l'enseignant, et laquelle l'oblige à s'engager sur un seul ?

<details markdown="1"><summary>Vérifier</summary>

La [KL directe](../GLOSSARY.md) couvre tous les modes, parce qu'elle punit l'élève quand il met peu de probabilité là où l'enseignant en met beaucoup. La [KL inverse](../GLOSSARY.md) s'engage sur un mode, parce qu'elle punit l'élève quand il met de la probabilité là où l'enseignant en met peu. Gardez cela en tête ci-dessous : la méthode de cette leçon s'engage aussi sur un seul mode, par un autre chemin.

</details>

## À savoir

### La loss, et pourquoi elle est hors d'atteinte

Kim et Rush travaillaient sur la traduction automatique neuronale, où un modèle produit une phrase cible entière un mot à la fois. Leur loss au niveau du mot est la loss [au niveau du token](../GLOSSARY.md) que vous connaissez : à chaque position, entropie croisée par rapport à la distribution de l'enseignant sur le mot suivant (section 3.1).

Une phrase n'est pourtant pas une prédiction unique. La probabilité d'une phrase entière est le produit des probabilités de ses mots, si bien que l'enseignant définit aussi une distribution sur toutes les phrases possibles. La loss au niveau de la séquence ferait correspondre l'élève à cette distribution. La somme porte sur un nombre exponentiel de phrases, elle ne peut donc pas être calculée (section 3.2).

### L'approximation : le mode de l'enseignant

Leur correctif le plus simple remplace la distribution de séquences de l'enseignant par un seul point : sa phrase la plus probable. Trouver exactement cette phrase est aussi intractable, ils utilisent donc le [beam search](../GLOSSARY.md), qui garde à chaque étape les quelques phrases partielles aux meilleurs scores. La recette comporte trois étapes (section 3.2) :

1. Entraîner un enseignant.
2. Lancer un beam search avec l'enseignant sur les entrées d'entraînement, en gardant la meilleure phrase pour chacune.
3. Entraîner l'élève avec une entropie croisée ordinaire sur ces sorties.

L'étape 3 est la boucle d'entraînement simple que vous avez déjà, exécutée sur un nouveau jeu de données. L'élève ne voit jamais les probabilités de l'enseignant. La contribution de l'enseignant est le texte qu'il a choisi.

```mermaid
flowchart LR
    A[Training inputs] --> B[Teacher with beam search]
    B --> C[Teacher output per input]
    C --> D[Student trained with cross-entropy]
```

### Pourquoi un échantillon peut suffire

Remplacer une distribution sur des phrases par une seule phrase semble une mauvaise approximation. Les auteurs soutiennent que ce n'est pas le cas, parce que la plus grande partie de la masse de l'enseignant se trouve près d'une seule sortie. Ils l'ont mesuré : avec un faisceau de taille 1, la meilleure phrase porte en moyenne 1.3 % de la probabilité de l'enseignant sur l'allemand vers l'anglais et 2.3 % sur le thaï vers l'anglais, et un faisceau de 5 porte cela à 2.8 % et 3.8 % (section 3.2 et sa note 5). Ce sont de petites parts du total, mais elles sont grandes à côté de toute autre phrase prise seule.

C'est le même compromis que la KL inverse de la leçon 5 : on demande à l'élève de modéliser la région autour d'un mode et non toute l'étendue. Kim et Rush le disent directement. Leur hypothèse est que l'élève ne « gaspille » pas de paramètres sur tout l'espace des traductions, et les données la soutiennent : l'élève 2×500 entraîné ainsi met en moyenne 16.9 % de sa masse sur sa propre meilleure phrase, contre 0.9 % pour le même élève entraîné sur les données d'origine (tableau 1, colonne p(t = ŷ)).

### Ce que cela a apporté

Tous les nombres ci-dessous sont ceux de cet article, sur ses configurations : anglais vers allemand (WMT 2014) avec un enseignant LSTM 4×1000 de 221m de paramètres, et des tailles d'élève de 2×500 (84m) et 2×300. BLEU est le score de traduction. K=1 est le décodage glouton et K=5 est le beam search avec un faisceau de 5 (tableau 1).

| Modèle | BLEU, K=1 | BLEU, K=5 |
|---|---|---|
| Enseignant, 4×1000 | 17.7 | 19.5 |
| Élève 2×500, entraîné sur les données d'origine | 14.7 | 17.6 |
| Élève 2×500, distillation au niveau du mot | 15.4 | 17.7 |
| Élève 2×500, distillation au niveau de la séquence | 18.9 | 19.0 |

La distillation au niveau du mot a ajouté 0.7 BLEU en décodage glouton. La distillation au niveau de la séquence en a ajouté 4.2, et l'élève glouton a dépassé la propre sortie gloutonne de l'enseignant. Sur le thaï vers l'anglais, l'article rapporte que les deux méthodes ont donné à peu près le même résultat (section 5).

### La surprise : pas besoin de beam search

La distribution de l'élève est piquée autour du mode, si bien que sa meilleure estimation unique est déjà ce mode. Le décodage glouton le trouve, et la recherche coûteuse n'est plus nécessaire. Le tableau 2 mesure la vitesse : sur un GPU, l'élève 2×500 en décodage glouton a traduit 1051.3 mots source par seconde, contre 101.9 pour l'enseignant avec un faisceau de 5, soit environ 10 fois plus vite, avec un BLEU similaire (section 5.1).

Un détail étrange mérite d'être retenu. L'élève 2×500 au niveau de la séquence a une perplexité de test de 22.7 contre 8.2 pour la référence, et pourtant il obtient plus de BLEU. Les auteurs notent qu'une perplexité plus basse ne signifie pas nécessairement un BLEU plus haut. Une lecture plausible est que l'élève a été entraîné à s'engager sur le choix de l'enseignant, pas à répartir la probabilité sur d'autres traductions raisonnables, bien que l'article ne teste pas cette explication.

### Limites à garder en vue

C'est un article sur une tâche, avec des LSTM et un enseignant dont les sorties pouvaient être décodées pour tout le jeu d'entraînement. Les auteurs ont aussi essayé d'échantillonner à partir de l'enseignant au lieu de prendre le mode et ont trouvé que le mode fonctionnait bien en pratique (note 5) ; c'est leur constat pour la traduction, pas une règle pour les modèles de chat. Ils ont aussi essayé une température dans {1, 1.5, 2} pour la distillation au niveau du mot et ont trouvé que 1 fonctionnait le mieux (note 4), un rappel de la leçon 3 : la meilleure température est une expérience.

L'article a une troisième méthode, l'interpolation au niveau de la séquence, qui choisit dans le faisceau de l'enseignant la phrase la plus proche de la référence humaine selon BLEU. Elle exige une référence par entrée, elle ne se transpose donc pas au cadre des données générées de la leçon 10, et la leçon suivante la laisse de côté.

## Pratique

1. ▢ Dans la recette de Kim et Rush, sur quoi l'élève s'entraîne-t-il à l'étape 3, et que ne voit-il jamais ?

    - a) Le texte de l'enseignant, plus ses probabilités à chaque mot
    - b) Les probabilités de l'enseignant seules, jamais de texte de l'enseignant
    - c) Le texte de l'enseignant seul, jamais de probabilités de l'enseignant
    - d) Du texte humain seul, plus une loss sur les logits de l'enseignant

<details markdown="1"><summary>Vérifier</summary>

**c)** L'étape 3 est de l'entropie croisée sur la sortie par beam search de l'enseignant. (b) et (d) décrivent la distillation au niveau du mot ou du token, qui lit la distribution de l'enseignant. (a) est la combinaison des deux niveaux, que l'article a testée comme variante séparée et que la leçon 9 couvre.

</details>

2. ▢ Le tableau 1 donne à l'élève 2×500 une référence de 14.7 BLEU et 18.9 après la distillation au niveau de la séquence en décodage glouton, mais 17.6 et 19.0 en beam search. Pourquoi le gain de la distillation est-il bien plus faible avec le beam search ?

<details markdown="1"><summary>Indice</summary>

Demandez-vous lequel des deux élèves a besoin du faisceau pour trouver sa meilleure phrase.

</details>

<details markdown="1"><summary>Vérifier</summary>

La distribution de la référence est étalée (sa meilleure phrase porte 0.9 % de la masse), donc le décodage glouton rate souvent la meilleure phrase et le beam search en récupère beaucoup. L'élève distillé est piqué sur le mode de l'enseignant (16.9 %), donc le décodage glouton atterrit déjà près de sa meilleure sortie et un faisceau n'ajoute presque rien. Le gain est de 4.2 BLEU en décodage glouton et de 1.4 en beam search parce que la référence profite davantage de la recherche.

</details>

3. ▢ L'enseignant traduit 101.9 mots par seconde sur le GPU avec un faisceau de 5, et l'élève 2×500 traduit 1051.3 mots par seconde en décodage glouton. Combien de fois l'élève est-il plus rapide, et quelle est la principale source de l'accélération ?

<details markdown="1"><summary>Vérifier</summary>

1051.3 divisé par 101.9 fait environ 10.3, donc à peu près 10 fois. Deux effets sont mêlés dans ce nombre. Le tableau 2 montre que l'enseignant seul atteint 425.5 mots par seconde en décodage glouton, donc abandonner le faisceau vaut environ 4 fois à lui seul, et le modèle plus petit (84m de paramètres contre 221m) explique l'essentiel du reste. Le propos de l'article est que l'élève peut abandonner le faisceau et garder une qualité similaire.

</details>

4. ▢ Un élève entraîné avec la distillation au niveau de la séquence a une perplexité de test plus élevée sur les traductions de référence d'origine que la référence, et pourtant un BLEU plus élevé. Un coéquipier appelle cela un bug. Que lui dites-vous ?

<details markdown="1"><summary>Vérifier</summary>

C'est attendu ici (22.7 contre 8.2 dans le tableau 1). L'élève a été entraîné à mettre sa masse sur le choix de l'enseignant, pas à couvrir les références, il attribue donc moins de probabilité aux variantes écrites par des humains tout en produisant une bonne sortie unique. La perplexité sur les références mesure l'étalement, et le BLEU sur la sortie décodée mesure une phrase. Vérifiez la métrique qui correspond à l'usage du modèle.

</details>

5. ▢ La leçon 5 disait que la KL inverse oblige un élève à s'engager sur un mode de l'enseignant. Nommez une chose que la distillation au niveau de la séquence a en commun avec cela, et une chose qu'elle fait différemment.

<details markdown="1"><summary>Vérifier</summary>

En commun : les deux visent une région de la distribution de l'enseignant pour l'élève, pas toute la distribution. Différent : la KL inverse lit encore les distributions de tokens de l'enseignant et évalue les propres échantillons de l'élève par rapport à elles, alors que la distillation au niveau de la séquence ne lit aucune probabilité et imite un échantillon décodé avec de l'entropie croisée.

</details>

## Exercices en situation réelle

- [ ] Ouvrez l'article et trouvez la figure 1. En une phrase chacune, notez sur quoi l'élève est entraîné dans les panneaux de gauche, du centre et de droite.
- [ ] Prenez un petit modèle instruct ouvert que vous pouvez exécuter. Décodez dix prompts de façon gloutonne et dix avec un échantillonnage à haute température, et notez quel ensemble vous préféreriez pour entraîner un élève, et pourquoi.
- [ ] Demain : sans notes, écrivez les trois étapes de la recette et le seul nombre qui explique pourquoi un unique échantillon peut tenir lieu de distribution de l'enseignant.

## Pour aller plus loin

- [Séquences et données synthétiques](../reference/sequence-and-synthetic-data.md)
- [Article : "Sequence-Level Knowledge Distillation", Kim et Rush, 2016](https://arxiv.org/abs/1606.07947)
- [Ressources](../RESOURCES.md)

---

Ça ne passe pas ? Relisez la source primaire en haut de page, car cette leçon la condense et c'est dans la condensation que la compréhension s'échappe. Consultez le [glossaire](../GLOSSARY.md) pour tout terme qui vous a paru glissant.

Si c'est la leçon elle-même qui n'est pas claire plutôt que la matière, c'est un défaut : [ouvrez une issue](https://github.com/TokenCemetery/teach/issues).
