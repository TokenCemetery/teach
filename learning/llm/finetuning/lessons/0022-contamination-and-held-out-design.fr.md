---
title: "22. Contamination et conception du jeu held-out"
description: "Découper selon la bonne clé, et dimensionner pour la question"
type: lesson
---

# Leçon 22. Contamination et conception du jeu held-out

**Lien avec la mission :** Un jeu held-out auquel on ne peut pas se fier est pire que pas de jeu du tout, parce qu'il produit des décisions fausses prises avec assurance.
**Source primaire :** [Code : lm-evaluation-harness, EleutherAI](https://github.com/EleutherAI/lm-evaluation-harness)
**Prérequis :** [Leçon 21](0021-building-the-dataset.md)

## Échauffement

1. ▢ Pourquoi dédupliquer avant de découper ?

<details markdown="1"><summary>Vérifier</summary>

Une paire de doublons à cheval sur le découpage met un exemple d'entraînement dans le jeu held-out, donc la performance held-out mesure de la mémorisation.

</details>

2. ▢ Qu'est-ce que le fine-tuning enseigne mal ?

<details markdown="1"><summary>Vérifier</summary>

De nouveaux faits, un raisonnement qui n'est pas déjà présent, des informations à jour, et le calcul précis. Il enseigne bien le format, le ton et la constance.

</details>

3. ▢ Quel checkpoint livrez-vous ?

<details markdown="1"><summary>Vérifier</summary>

Celui du minimum held-out, ce qui présuppose un jeu held-out auquel on peut se fier.

</details>

## À savoir

### Deux sortes de contamination

**Votre contamination.** Des exemples de test qui figurent aussi, exactement ou presque, dans votre jeu d'entraînement. Entièrement sous votre contrôle, et entièrement votre faute quand elle se produit.

**Contamination héritée.** Des exemples de test qui figuraient dans le corpus de *préentraînement* du base model. Hors de votre contrôle, largement indétectable de l'extérieur, et la raison pour laquelle les scores de benchmarks publics doivent être lus avec méfiance. Si un benchmark est antérieur au base model et vit sur le web public, supposez une certaine exposition.

La conséquence pratique : **un benchmark public est un signal faible pour votre décision.** Il peut mesurer le rappel de quelque chose que le base model avait déjà vu. Vos propres données held-out, construites de zéro, sont le signal fort, et c'est la seule chose à laquelle vous pouvez réellement vous fier.

### Découper correctement

Le découpage aléatoire est la valeur par défaut et il est fréquemment faux. Ce *selon quoi* vous découpez détermine la généralisation que vous mesurez.

| Découper par | Mesure | À utiliser quand |
|---|---|---|
| Exemple aléatoire | Généralisation à de nouveaux exemples | Les exemples sont réellement indépendants |
| Groupe ou entité | Généralisation à de nouvelles entités | Plusieurs exemples partagent un client, un document, un auteur |
| Temps | Généralisation au futur | Les données ont la moindre structure temporelle |

**La fuite par groupe** est la défaillance silencieuse classique. Dix exemples dérivés d'un même document source, découpés aléatoirement, en mettent certains dans le train et certains dans le test. Le modèle a vu le contenu de ce document et son score held-out le reflète. Découpez par document.

![Six exemples, quatre du document A et deux du B, découpés de deux façons. Découpés au hasard, les exemples de A tombent à la fois dans le panier d'entraînement et dans le panier de test ; découpés par document, tout A est dans un panier et tout B dans l'autre.](images/on-both-sides.svg)

Les mêmes six exemples figurent dans les deux panneaux ; seule l'affectation change. À gauche, un document est dans les deux paniers, c'est la fuite, et aucune discipline held-out ailleurs ne la défait.

**La fuite temporelle** est l'autre. Entraîner sur des données postérieures à votre période de test signifie que le modèle a vu le futur, et votre score est optimiste d'une façon qui ne peut pas survivre au déploiement. Tout dataset ayant une dimension temporelle devrait être découpé par le temps, et c'est le découpage que les gens sautent le plus souvent parce que l'aléatoire est plus facile.

### Trois découpages, pas deux

- **Train.** Ce que le modèle ajuste.
- **Validation.** Ce que vous utilisez pour choisir les checkpoints, le rank, le learning rate et tout le reste.
- **Test.** Touché une seule fois, à la fin, pour estimer la performance réelle.

La raison des trois est que sélectionner face à un ensemble s'ajuste à lui. Choisissez votre checkpoint par la validation, comparez vingt configurations sur la validation, retenez la meilleure, et le score de validation est maintenant optimiste d'une quantité proportionnelle au nombre de choix que vous avez faits face à lui. C'est pourquoi le jeu de test existe et pourquoi il n'est utilisé qu'une fois.

**En pratique, les gens en utilisent deux, puis s'étonnent que le déploiement sous-performe par rapport à leur évaluation.** L'écart est exactement la quantité de sélection qu'ils ont faite.

### Détecter votre propre contamination

Dédupliquez explicitement face au jeu de test, pas seulement au sein du jeu d'entraînement :

1. Normaliser : minuscules, espaces réduits, ponctuation retirée.
2. Hachage par correspondance exacte entre train et test. Retirer du train toute collision.
3. Détection de quasi-doublons par MinHash ou similarité d'embeddings, avec un seuil que vous avez examiné à la main.
4. **Lire vous-même les paires de plus forte similarité.** Les seuils sont des suppositions ; vos yeux sont l'étalonnage.

L'étape 4 est celle que les gens sautent et c'est celle qui trouve les vrais problèmes.

### Dimensionner le jeu held-out

Les jeux held-out sont généralement trop petits pour soutenir les conclusions qu'on en tire. La forme approximative : distinguer de petites différences demande beaucoup d'exemples, et le nombre croît de façon quadratique à mesure que la différence qui vous importe diminue.

| Différence que vous voulez détecter | Échelle approximative nécessaire |
|---|---|
| 10 points de pourcentage | Quelques centaines |
| 5 points de pourcentage | Plusieurs centaines à mille |
| 1 à 2 points de pourcentage | Des milliers |

Un jeu held-out de 50 exemples peut donc vous dire si le modèle fonctionne tout court. Il ne peut pas vous dire si le rank 32 a battu le rank 16 de deux points, et le traiter comme s'il le pouvait est une erreur très courante.

Le corollaire : si vous avez 200 exemples held-out, ne lancez pas un balayage de douze configurations. Le gagnant du balayage est surtout du bruit, et vous avez dépensé du calcul pour sélectionner une configuration au hasard.

### Comparaison appariée

Pour comparer deux modèles, évaluez les deux sur **les mêmes exemples** et comparez exemple par exemple. La comparaison appariée supprime la variance due à la difficulté des exemples et détecte de plus petites différences avec moins d'exemples que la comparaison de deux moyennes indépendantes. Elle ne coûte que de la comptabilité.

Conservez les résultats par exemple, pas seulement l'agrégat. « Le modèle B est meilleur de 3 points » est bien moins utile que « B a corrigé 14 exemples que A avait faux et en a cassé 6 que A avait justes », et les six sont l'endroit où l'on apprend quelque chose.

## Pratique

1. ▢ Distinguez votre contamination de la contamination héritée, et dites ce qu'implique chacune.

<details markdown="1"><summary>Vérifier</summary>

La vôtre : des exemples de test aussi présents dans votre jeu d'entraînement. Évitable, détectable, votre responsabilité.

Héritée : des exemples de test présents dans le corpus de préentraînement du base model. Non contrôlable, largement indétectable, et la raison pour laquelle les scores de benchmarks publics sont une preuve faible pour votre décision.

L'implication est de faire plus confiance à des données held-out privées construites de zéro qu'à n'importe quel benchmark public.

</details>

2. ▢ Votre dataset compte 500 exemples dérivés de 50 documents sources. Vous découpez aléatoirement et obtenez 96 % de précision held-out. Qu'est-ce qui cloche ?

<details markdown="1"><summary>Vérifier</summary>

De la fuite par groupe. Des exemples d'un même document sont dans les deux découpages, donc le modèle a vu le contenu de ce document et le score reflète du rappel.

Découpez par document : tous les exemples d'un document vont du même côté. Attendez-vous à ce que le chiffre honnête soit nettement plus bas.

</details>

3. ▢ Pourquoi trois découpages plutôt que deux ?

<details markdown="1"><summary>Vérifier</summary>

Parce que sélectionner face à un ensemble s'ajuste à lui. Chaque choix de checkpoint et chaque comparaison de configurations faits sur la validation rendent le score de validation optimiste.

Le jeu de test est intact jusqu'à la fin, donc il donne une estimation non biaisée. Avec seulement deux découpages, votre chiffre rapporté inclut toute votre sélection, ce qui est précisément l'écart que les gens constatent entre l'évaluation et le déploiement.

</details>

4. ▢ Vous avez 80 exemples held-out et voulez savoir si le rank 64 bat le rank 16. Le pouvez-vous ?

<details markdown="1"><summary>Vérifier</summary>

Pas à moins que la différence soit très grande. Quatre-vingts exemples peuvent permettre de détecter un écart de dix points ou plus ; la différence entre deux rank raisonnables est généralement de quelques points au plus.

Obtenez plus de données held-out ou acceptez que cette question n'ait pas de réponse avec ce que vous avez. Y répondre quand même produit une décision fausse prise avec assurance.

</details>

5. ▢ Quel découpage est le plus souvent sauté, et que coûte de le sauter ?

    - a) Découper les données par le temps quand elles ont un ordre temporel
    - b) Découper les données aléatoirement sur tous les exemples disponibles
    - c) Découper les données par longueur de sortie en tranches équilibrées
    - d) Découper les données selon l'annotateur qui a produit le label

<details markdown="1"><summary>Vérifier</summary>

**a)** Découper les données par le temps quand elles ont un ordre temporel.

L'aléatoire est plus facile et c'est la valeur par défaut, donc la structure temporelle est ignorée. Le coût est d'entraîner sur des données postérieures à la période de test : le modèle a vu le futur, et le score ne peut pas survivre au déploiement.

</details>

6. ▢ Pourquoi la comparaison appariée vaut-elle mieux que la comparaison de deux moyennes ?

<details markdown="1"><summary>Vérifier</summary>

Elle supprime la variance due à la difficulté des exemples en comparant les deux modèles sur les mêmes éléments, donc elle détecte de plus petites différences avec moins d'exemples.

Elle produit aussi l'artefact le plus utile : quels exemples précis se sont améliorés et lesquels ont régressé. Les régressions sont là où l'on apprend.

</details>

## Exercices en situation réelle

- [ ] Cherchez dans votre dataset une structure de regroupement : document, client, auteur, session. S'il y en a une, re-découpez selon elle et comparez les deux chiffres held-out.
- [ ] Exécutez la détection de quasi-doublons entre train et test. Lisez à la main les vingt paires de plus forte similarité.
- [ ] Découpez en trois ensembles et notez la règle sur ce à quoi chacun peut servir. Puis tenez-vous-y.
- [ ] Demain : calculez combien d'exemples held-out il vous faudrait pour détecter la différence qui vous importe réellement. Comparez à ce que vous avez.

## Pour aller plus loin

- [Code : lm-evaluation-harness, EleutherAI](https://github.com/EleutherAI/lm-evaluation-harness)
- [Doc : Splitting datasets, Hugging Face Datasets](https://huggingface.co/docs/datasets/main/en/process)
- [Leçon 23. Des métriques qui veulent dire quelque chose](0023-metrics-that-mean-something.md)

---

Ça ne passe pas ? Relisez la source primaire en haut de page, car cette leçon la condense et c'est dans la condensation que la compréhension s'échappe. Consultez le [glossaire](../GLOSSARY.md) pour tout terme qui vous a paru glissant.

Si c'est la leçon elle-même qui n'est pas claire plutôt que la matière, c'est un défaut : [ouvrez une issue](https://github.com/TokenCemetery/teach/issues).
