---
title: "25. Relire une affirmation de distillation"
description: "Relire « notre petit modèle égale le grand » en nommant ce que la mesure a caché"
type: lesson
---

# Leçon 25. Relire une affirmation de distillation

**Lien avec la mission :** La mission s'achève sur la relecture de l'affirmation de quelqu'un d'autre selon laquelle un modèle distillé « égale l'enseignant ». Une relecture qui dit « je n'y crois pas » est ignorée, alors que celle qui nomme quelle partie de la mesure a caché quoi, et ce qu'il en coûterait de le découvrir, est suivie d'effet.
**Source primaire :** [Article : "The False Promise of Imitating Proprietary LLMs", Gudibande et al., 2023](https://arxiv.org/abs/2305.15717), sections 1 et 4
**Prérequis :** [Leçon 22](0022-student-against-teacher.md), [Leçon 23](0023-an-honest-distillation-eval.md), [Fidélité](../GLOSSARY.md), [Écart d'imitation](../GLOSSARY.md)

## Échauffement

1. ▢ La leçon 17 a séparé deux choses pour lesquelles un élève peut être bon. Nommez-les et dites laquelle Stanton et al. ont trouvée faible même quand l'élève pouvait égaler l'enseignant.

<details markdown="1"><summary>Vérifier</summary>

La [fidélité](../GLOSSARY.md), la façon dont les prédictions de l'élève s'accordent avec celles de l'enseignant, et la généralisation, la façon dont l'élève réussit la tâche. Stanton et al. rapportent qu'un grand écart entre les distributions prédictives de l'enseignant et de l'élève subsiste souvent même quand l'élève a la capacité d'égaler exactement l'enseignant, et qu'une meilleure généralisation n'exige pas une meilleure fidélité ([article](https://arxiv.org/abs/2106.05945), résumé).

</details>

2. ▢ La leçon 23 a listé des références qui rendent défendable un chiffre « égale l'enseignant ». Quelle référence vous dit ce qu'a apporté l'enseignant, par opposition à ce que la taille et les données de l'élève auraient donné de toute façon ?

<details markdown="1"><summary>Vérifier</summary>

Un modèle de la taille de l'élève entraîné sans l'enseignant, sur les mêmes données de tâche. Sans lui, un bon score peut être ce qu'atteint n'importe quel élève de cette taille, et l'enseignant se voit attribuer un travail qu'il n'a pas fait.

</details>

3. ▢ La leçon 18 a nommé l'écart d'imitation. En une phrase, que dit-il de la vitesse à laquelle un élève comble l'écart sur le style comparée à la capacité ?

<details markdown="1"><summary>Vérifier</summary>

L'imitation avec un budget limité comble l'écart sur le style bien plus vite que sur la capacité, si bien qu'un élève peut ressembler à son enseignant bien avant de pouvoir faire ce que fait l'enseignant.

</details>

## À savoir

### Une affirmation a des parties

« Notre 7B égale l'enseignant » est cinq affirmations dans une phrase : un modèle, une mesure, une référence, une population d'entrées et un coût. Une relecture la démonte et demande pour chaque partie ce qu'il faudrait pour que l'affirmation échoue. Les relectures les plus utiles disent aussi ce qui est bien, pour que l'auteur le garde.

### Ce que mesure un pourcentage : DistilBERT

Sanh et al. disent que DistilBERT est 40 % plus petit et 60 % plus rapide et « retains 97% of its language understanding capabilities » ([article](https://arxiv.org/abs/1910.01108), résumé). La section 4 et le tableau 1 disent ce que cette phrase mesure : les neuf tâches du benchmark GLUE, sur les jeux de dev, après fine-tuning de chaque modèle, les résultats de BERT et de DistilBERT étant des médianes de 5 runs avec des graines différentes. Les macro-scores imprimés sont 79.5 pour BERT-base et 77.0 pour DistilBERT, et 77.0 sur 79.5 fait 96.9 %.

Donc 97 % est un rapport de deux moyennes, sur une suite de benchmarks, face à un enseignant. Par tâche, le tableau 1 donne un autre tableau : DistilBERT obtient 51.3 sur CoLA contre 56.3 pour BERT, soit 91.1 %, et 59.9 sur RTE contre 69.3, soit 86.4 %. Sur WNLI, il obtient 56.3 contre 53.5, au-dessus de l'enseignant. Le titre n'est pas faux. C'est une moyenne dans laquelle deux tâches faibles et quelques quasi-égalités sont repliées, et un lecteur dont la charge de travail ressemble à RTE devrait lire la ligne RTE.

Trois autres faits de l'article ont leur place dans une relecture. L'élève a été initialisé à partir de l'enseignant en prenant une couche sur deux (section 3), ce qui est un choix de conception qu'une affirmation devrait divulguer. Il a été entraîné sur le même corpus que BERT, donc il n'y a pas de décalage entre les données de l'enseignant et celles de l'élève. Et le calcul était de 8 GPU V100 pendant environ 90 heures (section 3), l'enseignant étant déjà entraîné et non compté dans ce chiffre.

### Ce qu'une évaluation de préférence cache : Gudibande et al.

Gudibande et al. ont fait le fine-tuning de modèles de 1.5B à 13B de paramètres pour imiter ChatGPT et les ont évalués de deux façons. Des travailleurs de la foule, environ 70, ont jugé 255 prompts held-out, et à peu près 70 % des sorties des modèles d'imitation ont été jugées égales ou meilleures que celles de ChatGPT (section 4, figure 1 à gauche). Pour limiter la fuite, ils ont écarté les requêtes dont le score BLEU par rapport à n'importe quel exemple d'entraînement dépassait 20 %, et ils ont écarté les prompts de code et non anglais que les évaluateurs ne pouvaient pas juger.

Les évaluations automatiques ciblées ont raconté une autre histoire. Les auteurs rapportent que les modèles d'imitation ont comblé peu ou pas de l'écart entre le base model et ChatGPT sur les tâches peu soutenues dans les données d'imitation, et que plus de données d'imitation ne l'ont pas comblé, certains résultats comme les connaissances factuelles de Natural Questions régressant (figure 1 au centre). Leur explication est que les modèles ont appris le style de ChatGPT, assuré et bien structuré, et que des évaluateurs sans expertise du domaine ni temps pour vérifier les faits manquent les erreurs (section 4.4).

C'est le résultat d'un seul article, pour l'imitation de ChatGPT avec des modèles jusqu'à 13B de paramètres. Le point transférable n'est pas que les évaluations de préférence sont inutiles. C'est qu'une évaluation mesure ce que l'évaluateur peut juger, et que ce qu'un évaluateur peut juger en une minute est souvent le style.

### Les questions à poser

| Partie de l'affirmation | Demander | Pourquoi cela compte |
|---|---|---|
| Tâches | Quelles tâches, et la moyenne cache-t-elle les faibles ? | Les 97 % de DistilBERT reposent sur des lignes à 86 % et 91 % |
| Population | Les entrées de test sont-elles held-out, ou tirées de la distribution de distillation ? | Gudibande et al. constatent que l'écart apparaît sur les tâches que les données d'imitation ne soutiennent pas |
| Référence | Par rapport à quoi : l'enseignant, un modèle de même taille entraîné sans lui, le base model ? | La première dit jusqu'où, la deuxième dit ce qu'a ajouté l'enseignant |
| Contamination | Comment les données de test ont-elles été tenues hors des prompts de distillation ? | Un filtre de recouvrement BLEU est une réponse concrète, et une affirmation qui n'en a aucune est une lacune |
| Évaluateur | Des humains, un modèle juge ou une métrique, et pouvaient-ils vérifier les faits ? | Un juge ou la foule peuvent récompenser le style |
| Décodage | Glouton ou échantillonné, quelle température, la même pour les deux modèles ? | Agarwal et al. rapportent que les divergences qui cherchent un mode ont fait mieux sous échantillonnage à température alors que le choix comptait à peine en décodage glouton ([article](https://arxiv.org/abs/2306.13649), section 4.1), donc le décodage peut changer le classement |
| Bruit | Combien de graines, et quelle est la taille de l'écart par rapport à la dispersion d'un run à l'autre ? | DistilBERT rapporte des médianes de 5 runs, et beaucoup d'affirmations n'en rapportent qu'un |
| Coût | L'inférence de l'enseignant, la génération des données et le filtrage sont-ils comptés ? | Les 90 heures GPU de DistilBERT excluent le pré-entraînement de l'enseignant |

Deux des lignes sont des questions sur ce qui manque dans le compte rendu, pas sur ce qui y est faux. Traitez une réponse manquante comme un point ouvert, pas comme une faute : notez-le et demandez-le.

### Écrire la relecture

Dites d'abord ce qui est bien. Énoncez chaque partie cachée comme un coût : « la moyenne cache les tâches où le score a baissé de 10 points ou plus » est concret, et « je ne fais pas confiance à la moyenne » ne l'est pas. Nommez ensuite la mesure qui trancherait, avec son prix, pour que l'auteur puisse répondre oui ou non. Les références, les tâches held-out et les contrôles de contamination de la leçon 23 sont les réponses habituelles.

## Pratique

1. ▢ Prédisez lesquelles des neuf tâches GLUE de DistilBERT ont le plus bas rapport élève sur enseignant, puis exécutez ceci sur les nombres du tableau 1.

    ```python
    bert = dict(CoLA=56.3, MNLI=86.7, MRPC=88.6, QNLI=91.8, QQP=89.6,
                RTE=69.3, SST2=92.7, STSB=89.0, WNLI=53.5)
    distil = dict(CoLA=51.3, MNLI=82.2, MRPC=87.5, QNLI=89.2, QQP=88.5,
                  RTE=59.9, SST2=91.3, STSB=86.9, WNLI=56.3)
    for task in sorted(bert, key=lambda t: distil[t] / bert[t]):
        print(f"{task:5s} {100 * distil[task] / bert[task]:.1f}")
    print(f"mean of entries {sum(bert.values()) / 9:.1f} and {sum(distil.values()) / 9:.1f}")
    ```

<details markdown="1"><summary>Indice</summary>

Cherchez les tâches où l'enseignant a obtenu bien moins de 100 et où l'élève a chuté davantage.

</details>

<details markdown="1"><summary>Vérifier</summary>

RTE à 86.4 et CoLA à 91.1 sont les plus bas, et WNLI à 105.2 est le plus haut. La dernière ligne affiche 79.7 et 77.0. L'article imprime 79.5 pour BERT-base, proche de la moyenne de ses propres neuf entrées sans lui être égal, et je n'ai pas pu établir pourquoi. L'un ou l'autre chiffre donne environ 97 % au total, ce qui est le propos : recalculez un titre à partir du tableau avant de le citer.

</details>

2. ▢ Un article rapporte que des travailleurs de la foule ont jugé environ 70 % des sorties d'un élève égales ou meilleures que celles de son enseignant. Que concluez-vous sur la capacité, et que demanderiez-vous ?

<details markdown="1"><summary>Vérifier</summary>

Rien de ferme sur la capacité. Chez Gudibande et al., le même type d'évaluation a coexisté avec peu de comblement de l'écart sur les tâches que les données d'imitation ne soutenaient pas, parce que les évaluateurs récompensent le style que l'élève a copié. Demandez des évaluations automatiques ciblées sur des tâches held-out, et des évaluateurs ou un contrôle capables de vérifier les faits.

</details>

3. ▢ Affirmation hypothétique : « Notre élève de 7B égale l'enseignant. Sur 500 prompts, un modèle juge a préféré l'élève ou fait match nul dans 62 % des comparaisons. » Les prompts venaient du même générateur que les prompts de distillation, le décodage était glouton pour l'élève et échantillonné pour l'enseignant, et le coût n'est pas indiqué. Listez les questions que vous poseriez, la plus décisive d'abord.

<details markdown="1"><summary>Vérifier</summary>

D'abord, la population : des prompts du générateur de distillation sont dans la distribution, donc demandez des tâches held-out. Deuxièmement, le décodage : les deux modèles devraient être décodés de la même façon, parce que le réglage peut changer le classement. Troisièmement, le juge : quel modèle, vérifié pour le biais de style, et un taux de matchs nuls séparé de la préférence. Quatrièmement, la référence : un modèle de même taille entraîné sans l'enseignant. Enfin, le coût : la génération et le filtrage de l'enseignant comptés. Dites aussi ce qui est bien : une comparaison jugée sur 500 prompts est un premier regard raisonnable.

</details>

4. ▢ Quel contrôle est une preuve que les prompts de distillation n'ont pas fui dans le jeu de test ?

    - a) Un juge plus grand lui donnant un meilleur score
    - b) Un filtre de recouvrement sur les prompts de test
    - c) Une moyenne des scores sur plusieurs graines
    - d) Un run plus long sur les sorties de l'enseignant

<details markdown="1"><summary>Vérifier</summary>

**b)** Il vérifie la chose en question, comme l'ont fait Gudibande et al. avec un filtre BLEU à 20 % par rapport à n'importe quel exemple d'entraînement. (a) et (c) changent la façon dont le score est jugé ou moyenné, pas le fait que les entrées aient été vues. (d) ne teste pas le recouvrement, et davantage des mêmes prompts peut l'aggraver.

</details>

5. ▢ Deux articles comparent la KL directe et la KL inverse pour des élèves. L'un évalue en décodage glouton et trouve peu de différence, l'autre échantillonne à haute température et trouve la KL inverse nettement meilleure. Les deux peuvent-ils avoir raison, et que vérifiez-vous d'abord ?

<details markdown="1"><summary>Vérifier</summary>

Oui. Agarwal et al. rapportent que les divergences qui cherchent un mode ont fait mieux sous échantillonnage à température et que le choix comptait à peine en décodage glouton, ce qui est la même séparation. Vérifiez d'abord le réglage de décodage de chaque évaluation, puis la tâche et les tailles de modèle, avant de traiter les deux comme une contradiction.

</details>

## Exercices en situation réelle

- [ ] Trouvez une fiche de modèle ou un billet de blog qui affirme qu'un petit modèle égale un grand, et écrivez une ligne pour chaque ligne du tableau de questions : la réponse que donne le billet, ou « non indiqué ».
- [ ] Recalculez un pourcentage d'un tableau de résultats de ce billet, avec les propres nombres du tableau, et notez s'il se reproduit.
- [ ] Demain : écrivez la relecture de cette affirmation en cinq phrases, en commençant par ce qui est bien et en finissant par la seule mesure que vous demanderiez.

## Pour aller plus loin

- [Liste de contrôle de relecture d'une distillation](../reference/distillation-review-checklist.md)
- [Dimensionner et mesurer](../reference/sizing-and-measuring.md)
- [Article : "The False Promise of Imitating Proprietary LLMs", Gudibande et al., 2023](https://arxiv.org/abs/2305.15717)
- [Article : "DistilBERT, a distilled version of BERT: smaller, faster, cheaper and lighter", Sanh et al., 2019](https://arxiv.org/abs/1910.01108)
- [Article : "On-Policy Distillation of Language Models: Learning from Self-Generated Mistakes", Agarwal et al., 2023](https://arxiv.org/abs/2306.13649)
- [Ressources](../RESOURCES.md)

---

Ça ne passe pas ? Relisez la source primaire en haut de page, car cette leçon la condense et c'est dans la condensation que la compréhension s'échappe. Consultez le [glossaire](../GLOSSARY.md) pour tout terme qui vous a paru glissant.

Si c'est la leçon elle-même qui n'est pas claire plutôt que la matière, c'est un défaut : [ouvrez une issue](https://github.com/TokenCemetery/teach/issues).
