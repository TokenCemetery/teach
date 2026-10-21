---
title: "27. Quand la réponse habituelle est fausse"
description: "Reconnaître quand la distillation est le mauvais choix, et trancher une affirmation contestée à partir de la source primaire"
type: lesson
---

# Leçon 27. Quand la réponse habituelle est fausse

**Lien avec la mission :** Le parcours s'achève sur le fait qu'on vous fasse confiance pour trancher sur une distillation et l'expliquer à quelqu'un d'autre. « Distillez le grand modèle en un petit » et « la KL directe est la loss standard » sont les réponses habituelles, et chacune est vraie dans certains cadres et fausse dans d'autres. Cette leçon présente les cas où la distillation est le mauvais choix, et une méthode pour trancher un différend à partir des propres tableaux de l'article.
**Source primaire :** [Article : "On the Efficacy of Knowledge Distillation", Cho et Hariharan, 2019](https://arxiv.org/abs/1910.01348), sections 5.1 et 5.2
**Prérequis :** [Leçon 19](0019-capacity-gap-and-hidden-traits.md), [Leçon 24](0024-distill-quantize-or-fine-tune.md), [Leçon 26](0026-replacing-a-model-others-depend-on.md), [Écart de capacité](../GLOSSARY.md), [KL directe](../GLOSSARY.md), [KL inverse](../GLOSSARY.md)

## Échauffement

1. ▢ La leçon 5 a opposé la KL directe et la KL inverse. Laquelle étale l'élève sur tous les modes de l'enseignant, et laquelle s'engage sur un seul mode ?

<details markdown="1"><summary>Vérifier</summary>

La [KL directe](../GLOSSARY.md) étale l'élève sur tous les modes, parce qu'elle pénalise de mettre peu de probabilité là où l'enseignant en met beaucoup. La [KL inverse](../GLOSSARY.md) s'engage sur un mode, parce qu'elle pénalise de mettre de la probabilité là où l'enseignant en met peu.

</details>

2. ▢ La leçon 16 a couvert ce que coûte la distillation on-policy par pas. Que doit faire l'enseignant qu'il ne fait pas quand l'élève s'entraîne sur des sorties fixes de l'enseignant ?

<details markdown="1"><summary>Vérifier</summary>

Évaluer les tokens de séquences que l'élève génère pendant l'entraînement, si bien que chaque pas exige de nouveaux échantillons de l'élève et une passe avant de l'enseignant sur eux. Les sorties fixes de l'enseignant sont générées une fois, et les pas d'entraînement de l'élève n'attendent pas l'enseignant. Voir [distillation on-policy](../GLOSSARY.md).

</details>

3. ▢ La leçon 13 a couvert les conditions d'utilisation et les licences. Que devez-vous vérifier avant de générer des données d'entraînement à partir d'un modèle qui ne vous appartient pas ?

<details markdown="1"><summary>Vérifier</summary>

Si les conditions du fournisseur ou la licence du modèle autorisent l'usage de ses sorties pour entraîner un autre modèle, et à quelles conditions. Ce sont deux documents qui changent, donc lisez le texte actuel, pas un résumé.

</details>

## À savoir

### La méthode

Une réponse habituelle arrive comme un slogan sans ses conditions. Cinq étapes décident si elle tient pour vous.

1. **Trouver la source primaire.** L'article, pas le billet qui le cite.
2. **Vérifier le cadre.** Modèles, tailles, données, année, et ce qui a été mesuré.
3. **Lire le montage derrière le tableau.** Références, nombre d'essais, et comment le nombre rapporté a été choisi.
4. **Comparer l'écart avec le bruit.** Un écart d'un point sans dispersion prouve peu de chose.
5. **Tester sur votre tâche**, comme le décrit la leçon 23.

Aucun des cas ci-dessous ne dit que la distillation est mauvaise. Chacun dit ce que sa source soutient et où elle s'arrête.

### Là où la réponse habituelle échoue

| Réponse habituelle | Fausse quand | Source et limite |
|---|---|---|
| Distillez le grand modèle | Aucun enseignant n'est meilleur que l'élève sur votre tâche, donc il n'y a rien à imiter | Article R1, annexe F : dépasser la frontière de l'enseignant peut exiger des base models plus forts et du RL à plus grande échelle. Gudibande et al. concluent que des capacités de base plus fortes, et non plus de données d'imitation, sont la manière dont les modèles ouverts s'améliorent. Mon raisonnement en plus : l'imitation ne peut pas battre sa source sur la tâche |
| Utilisez le meilleur enseignant disponible | Les conditions ou la licence l'interdisent | Les Terms of Use d'OpenAI comptent l'usage de la sortie pour développer des modèles concurrents parmi ce qu'un utilisateur ne peut pas faire. La licence Llama 3.1 vous permet d'entraîner sur les sorties mais exige « Llama » au début du nom du modèle obtenu quand il est distribué. Lisez le texte actuel |
| Un enseignant plus grand donne un meilleur élève | L'élève ne peut pas l'absorber, l'écart de capacité | Cho et Hariharan, tableau 1, Mirzadeh et al., figure 2, Busbridge et al., section 4.2, ci-dessous |
| Un élève peut absorber ce que sait l'enseignant | La tâche exige une connaissance que l'élève ne peut pas contenir | Gudibande et al. : l'imitation a amélioré le style et le suivi d'instructions mais pas la factualité, le code ni la résolution de problèmes, les résultats sur Natural Questions régressant à mesure que les données d'imitation augmentaient |
| Faire un fine-tuning sur les sorties de l'enseignant une seule fois | L'entraînement on-policy de l'élève sur ses propres échantillons fait mieux | Agarwal et al., section 4.1 : les variantes on-policy et mixtes ont systématiquement surpassé les variantes supervisées dans leurs ablations de résumé, et sur GSM8K, GKD on-policy a nettement surpassé les autres approches (figure 9, section 4.3). Cela coûte plus par pas (leçon 16) |
| Distiller plutôt que quantifier | Quantifier le modèle tient déjà dans le budget | La fiche de quantification rapporte W8A8-FP effectivement sans perte à toutes les tailles chez Kurtic et al., sur une famille de modèles : voir sa [liste de contrôle de relecture de la quantification](../../quantization/reference/quantization-review-checklist.md) |
| Distiller plutôt qu'entraîner directement un petit modèle | Beaucoup de données de tâche et pas d'enseignant gratuit | Busbridge et al. : l'apprentissage supervisé surpasse la distillation avec assez de calcul ou de tokens pour l'élève. Un résultat de pré-entraînement, donc une inférence pour le fine-tuning de tâche (leçon 24) |

Deux lignes vont à l'encontre des espoirs du parcours lui-même. L'article R1 trouve la distillation battant le RL sur la même base de 32B (leçon 24), donc « le RL sur le petit modèle gagne » n'est pas un cas que cette leçon peut soutenir, et aucune source lue pour cette leçon ne montre qu'un simple fine-tuning sur des données humaines batte la distillation sur une tâche. Les deux restent hors du tableau.

### L'écart de capacité, d'après les tableaux

Cho et Hariharan ont fait tourner un élève ImageNet, ResNet18, avec trois enseignants (tableau 1, erreur top-1, plus bas est mieux). L'entraînement de l'élève de zéro a donné 30.24. Avec des enseignants ResNet18, ResNet34 et ResNet50, dont les propres erreurs étaient de 30.24, 26.70 et 23.85, les élèves ont obtenu 30.57, 30.79 et 30.95. Plus l'enseignant devenait bon, plus l'élève devenait mauvais, et chaque élève distillé était moins bon que celui entraîné sans enseignant. Le texte dit que ResNet152 était aussi un enseignant, mais le tableau que j'ai lu liste trois lignes. Les auteurs rapportent aussi une version CIFAR-10 dans laquelle la précision de l'élève monte puis baisse à mesure que l'enseignant grandit, et que l'adoucissement des probabilités de l'enseignant par une température plus élevée n'a pas changé ce résultat (section 5.1).

Mirzadeh et al. montrent la même montée et la même chute pour un élève CNN à 2 couches sous des enseignants de 4, 6, 8 et 10 couches sur CIFAR-10 et CIFAR-100, et donnent trois facteurs concurrents, le troisième étant qu'un enseignant plus certain donne des soft targets moins douces (figure 2). Busbridge et al. ajustent l'effet pour les modèles de langage : l'entropie croisée de l'élève diminue jusqu'à un optimum puis remonte avec la taille de l'enseignant, et ils soutiennent que l'écart est un écart de capacité d'apprentissage, d'espace d'hypothèses et d'aptitude à optimiser, dont la taille relative est un cas particulier (sections 1 et 4.2, figure 4).

Trois sources, trois cadres, une direction. Aucune n'est votre paire de modèles, donc « plus grand n'est pas toujours meilleur » est une raison de tester un enseignant d'une taille en dessous, pas une règle selon laquelle le plus grand a tort.

### Trancher un différend : « la KL directe est la loss standard »

Un collègue dit que la KL directe est standard. Commencez par les articles qui l'ont testée et lisez ce que chacun a mesuré.

| Source | Cadre | Ce qui a été mesuré | Résultat |
|---|---|---|---|
| Busbridge et al., annexe G.5, tableau 7 | Enseignant de 1.82B vers élève de 546M, C4 | Entropie croisée sur les données, plus bas est mieux | Directe 2.42, inverse 2.70 |
| Muralidharan et al. (Minitron), annexe A.3, tableau 16 | Minitron 8B élagué en profondeur, ré-entraîné avec distillation | Loss LM sur des jeux de validation | KL directe 2.155, KL inverse 2.665 |
| Gu et al. (MiniLLM), résumé | Suivi d'instructions, élèves GPT-2 et OPT | Retour de GPT-4 et autres mesures | KL inverse rapportée comme plus adaptée et élèves de meilleure qualité |
| Agarwal et al., section 4.4 | FLAN-T5-XL vers base, instruction tuning, MMLU et BBH | Score few-shot sur tâches held-out | On-policy avec KL inverse bien meilleur que la KL directe |
| Agarwal et al., section 4.1 | Résumé XSum, élèves T5 | Qualité contre diversité | La meilleure divergence dépendait de la tâche et de l'échantillonnage : la recherche de mode a fait mieux avec un échantillonnage à température, et le choix comptait à peine en décodage glouton |

Lisez les colonnes de haut en bas. Les deux premières mesurent une loss sur du texte, dans des cadres proches du pré-entraînement, et la KL directe gagne. Les trois dernières mesurent la qualité de sorties de suivi d'instructions ou de résumé, et la KL inverse gagne ou le gagnant dépend du décodage. Le propre texte de Minitron nomme la séparation : il cite la KL inverse comme mieux adaptée au suivi d'instructions et Agarwal et al. pour la dépendance à la tâche, et trouve la KL directe la meilleure pour son base model élagué.

Une lecture, qui est mon inférence et non quelque chose que ces articles ont testé, est qu'une métrique de loss sur du texte favorise la divergence la plus proche de cette loss, et qu'une métrique de qualité de sortie favorise celle qui évite les suites de faible probabilité. Ce que les tableaux soutiennent est plus modeste et suffisant : « la KL directe est standard » est vrai des cadres de type pré-entraînement lus ici, faux dans d'autres, et l'affirmation doit porter son cadre. Pour un élève ajusté par instructions, les preuves de ces tableaux orientent vers le test de la KL inverse aussi, avec votre propre décodage.

Remarquez ce qui a tranché. Personne n'a consulté sa mémoire. La réponse est venue de la recherche du tableau de chaque source, de la lecture de ce dont le nombre était un nombre, et de la constatation que les cadres se séparaient nettement.

## Pratique

1. ▢ En vous appuyant sur le tableau 1 de Cho et Hariharan, prédisez lequel des trois enseignants donne le meilleur élève et si un élève distillé bat l'entraînement de zéro, puis exécutez.

    ```python
    scratch = 30.24
    for teacher, teacher_err, student_err in [
        ("ResNet18", 30.24, 30.57),
        ("ResNet34", 26.70, 30.79),
        ("ResNet50", 23.85, 30.95),
    ]:
        print(f"{teacher:9s} teacher {teacher_err:5.2f} student {student_err:5.2f} vs scratch {student_err - scratch:+.2f}")
    ```

<details markdown="1"><summary>Indice</summary>

Comparez l'erreur de chaque élève avec 30.24, l'erreur de l'élève entraîné sans enseignant.

</details>

<details markdown="1"><summary>Vérifier</summary>

L'enseignant ResNet18 donne le meilleur élève, 30.57, et chaque élève est moins bon que l'entraînement de zéro : de 0.33, 0.55 et 0.71 points d'erreur. L'enseignant le plus précis a donné le pire élève. C'est une configuration ImageNet avec un élève, c'est donc un contre-exemple à « plus grand est toujours meilleur », pas une mesure de l'ampleur de l'effet ailleurs.

</details>

2. ▢ Une équipe prévoit de distiller un modèle hébergé dans un modèle qu'elle vendra. Les conditions du fournisseur interdisent d'utiliser la sortie pour développer des modèles concurrents du fournisseur. Que recommandez-vous ?

<details markdown="1"><summary>Vérifier</summary>

De ne pas poursuivre avec cet enseignant pour ce produit, et de chercher une autre voie : un enseignant dont la licence l'autorise, des données écrites par des personnes, ou la quantification du modèle qu'ils ont déjà. Si l'alternative est un modèle ouvert comme Llama 3.1, sa licence autorise l'entraînement sur les sorties mais exige que le nom du modèle obtenu commence par « Llama » et que « Built with Llama » soit affiché quand il est distribué, lisez donc le texte actuel de la licence au regard du plan du produit. Aucun des deux documents n'est un avis juridique, demandez donc à un juriste avant de livrer.

</details>

3. ▢ Un collègue dit « la KL directe est la loss standard, utilisons-la pour notre élève ajusté par instructions ». Répondez à partir du tableau.

<details markdown="1"><summary>Vérifier</summary>

La KL directe a gagné là où la métrique était une loss sur du texte dans des cadres de type pré-entraînement (Busbridge et al., Minitron), et la KL inverse a gagné ou le gagnant dépendait du décodage là où la qualité de sortie de suivi d'instructions ou de résumé était la métrique (MiniLLM, Agarwal et al.). Votre élève est ajusté par instructions, donc les preuves orientent vers le test des deux avec votre décodage, plutôt que vers la valeur par défaut.

</details>

4. ▢ Quelle preuve trancherait la question de savoir si l'écart de capacité s'applique à votre enseignant et à votre élève ?

    - a) La courbe de loss d'entraînement de l'élève à convergence
    - b) Les scores propres de l'enseignant sur les classements publics
    - c) Le score de votre élève sous deux tailles d'enseignant
    - d) Un article rapportant une autre famille de modèles

<details markdown="1"><summary>Vérifier</summary>

**c)** C'est l'expérience qu'ont menée les trois articles, sur votre paire et votre tâche. (b) est la qualité de l'enseignant, et Cho et Hariharan montrent qu'une qualité d'enseignant croissante a coexisté avec une qualité d'élève décroissante. (a) est un signal d'entraînement, pas la qualité sur la tâche. (d) montre que l'effet existe ailleurs, pas pour vous.

</details>

5. ▢ Mirzadeh et al. rapportent, pour un ResNet sur CIFAR-10 (tableau 1), 88.65 pour la distillation simple et 88.98 pour leur méthode d'assistant enseignant, et disent que chaque nombre rapporté est la meilleure précision top-1 au test atteinte par l'optimiseur d'hyperparamètres sur 120 essais. Que dites-vous de l'écart de 0.33 ?

<details markdown="1"><summary>Vérifier</summary>

Choisir la meilleure précision au test sur de nombreux essais avantage les deux méthodes, et le tableau ne montre aucune dispersion, donc un tiers de point ne peut pas être appelé une victoire à partir de ce seul tableau. Ce n'est pas une preuve que la méthode échoue : les écarts plus grands du même tableau, comme 66.60 contre 67.36 sur ImageNet, sont un meilleur endroit où regarder, avec la même réserve. Demandez des runs répétés avec des graines fixées et une précision au test qui ne serve pas à la sélection.

</details>

## Exercices en situation réelle

- [ ] Prenez une règle empirique de distillation sur laquelle vous vous appuyez (par exemple « utilisez le plus grand enseignant ») et remontez-la jusqu'à l'article. Notez les modèles, les tailles, l'année, ce qui a été mesuré et où votre cas diffère.
- [ ] Ouvrez le tableau 7 de l'article Distillation Scaling Laws et l'annexe A.3 de l'article Minitron et notez en une ligne les différences de montage entre eux et MiniLLM, pour pouvoir répondre à la prochaine dispute sur « quelle loss » à partir des tableaux.
- [ ] Demain : pour la distillation que vous aimeriez le plus mener, écrivez le cas du tableau ci-dessus le plus susceptible de s'appliquer, et la mesure qui montrerait s'il s'applique.

## Pour aller plus loin

- [Liste de contrôle de relecture d'une distillation](../reference/distillation-review-checklist.md)
- [Article : "On the Efficacy of Knowledge Distillation", Cho et Hariharan, 2019](https://arxiv.org/abs/1910.01348)
- [Article : "Improved Knowledge Distillation via Teacher Assistant", Mirzadeh et al., 2019](https://arxiv.org/abs/1902.03393)
- [Article : "Distillation Scaling Laws", Busbridge et al., 2025](https://arxiv.org/abs/2502.08606)
- [Article : "MiniLLM: On-Policy Distillation of Large Language Models", Gu et al., 2023](https://arxiv.org/abs/2306.08543)
- [Article : "On-Policy Distillation of Language Models: Learning from Self-Generated Mistakes", Agarwal et al., 2023](https://arxiv.org/abs/2306.13649)
- [Post-training](../../post-training/)
- [Ressources](../RESOURCES.md)

---

C'est la fin du parcours, et l'habitude pour laquelle il a été construit est celle de cette leçon : un modèle distillé est une affirmation sur un enseignant, un élève, une loss, un jeu de données et un ensemble de tâches, alors trouvez d'où vient l'affirmation, vérifiez ce qu'elle a couvert, et mesurez sur vos propres tâches avant de la défendre devant quiconque.

Ça ne passe pas ? Relisez la source primaire en haut de page, car cette leçon la condense et c'est dans la condensation que la compréhension s'échappe. Consultez le [glossaire](../GLOSSARY.md) pour tout terme qui vous a paru glissant.

Si c'est la leçon elle-même qui n'est pas claire plutôt que la matière, c'est un défaut : [ouvrez une issue](https://github.com/TokenCemetery/teach/issues).
