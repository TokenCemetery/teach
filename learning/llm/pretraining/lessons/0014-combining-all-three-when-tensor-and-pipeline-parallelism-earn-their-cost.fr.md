---
title: "14. Combiner les trois : quand les parallélismes tensoriel et de pipeline justifient leur coût"
description: "Faire correspondre chaque stratégie de parallélisme à l'interconnexion qu'elle tolère, et quand le partitionnement seul ne suffit pas"
type: lesson
---

# Leçon 14. Combiner les trois : quand les parallélismes tensoriel et de pipeline justifient leur coût

**Lien avec la mission :** « Expliquer ce que ZeRO/FSDP partitionnent, pourquoi le parallélisme de données seul manque de mémoire avant de manquer de calcul, et quand le parallélisme tensoriel ou de pipeline vaut son coût de communication » est le quatrième point sous Objectif, et cette leçon est celle où il se referme : quand l'ingénierie supplémentaire du parallélisme tensoriel et de pipeline vaut la peine d'être envisagée.
**Source primaire :** [Article : "Efficient Large-Scale Language Model Training on GPU Clusters Using Megatron-LM", Narayanan et al., 2021](https://arxiv.org/abs/2104.04473)
**Prérequis :** [Leçon 13](0013-pipeline-parallelism-splitting-the-models-layers.md)

## Échauffement

1. ▢ Qu'est-ce que la bulle de pipeline, et qu'échange une vidange de pipeline contre elle ?

<details markdown="1"><summary>Vérifier</summary>

La bulle de pipeline est le temps d'inactivité au début et à la fin d'un batch, pendant que le pipeline se remplit ou se vide. Une vidange de pipeline laisse le pipeline se vider et synchronise le pas d'optimizer de chaque appareil, ce qui est la cause de la bulle ; l'alternative risquerait que la passe arrière d'un micro-batch voie une version des poids différente de celle qu'a utilisée sa passe avant.

</details>

2. ▢ Dans le découpage du MLP en parallélisme tensoriel, de combien d'opérations all-reduce le bloc entier a-t-il besoin, et où a-t-elle lieu ?

<details markdown="1"><summary>Vérifier</summary>

Une, après la seconde multiplication matricielle, qui combine la somme partielle de chaque appareil en résultat complet.

</details>

## À savoir

### Trois axes, combinés

Narayanan et al. appellent **PTD-P** la combinaison des trois à la fois : parallélisme tensoriel, parallélisme de pipeline et parallélisme de données. Chaque axe découpe une chose différente : le parallélisme tensoriel découpe ce que calcule une seule couche (leçon 12), le parallélisme de pipeline découpe les couches dont un appareil est responsable (leçon 13), et le parallélisme de données (leçons 7 et 8, éventuellement partitionné davantage avec ZeRO, leçons 9 à 11) répartit le batch entre des réplicas de la configuration en parallélisme tensoriel et de pipeline qui est répliquée. Combinés ainsi, Narayanan et al. rapportent l'entraînement d'un modèle de mille milliards de paramètres à 502 petaFLOP/s sur 3 072 GPU, chaque GPU soutenant 52 % de son débit crête théorique, une fraction réellement importante à tenir à cette échelle.

### Pourquoi le découpage suit l'interconnexion, pas seulement le modèle

Narayanan et al. donnent une raison directe et pratique à la manière dont ils affectent les appareils à chaque axe : l'all-reduce du parallélisme tensoriel, nécessaire une fois par couche comme l'a décrit la leçon 12, est assez coûteux pour qu'il donne ses meilleurs résultats confiné à des appareils reliés par l'interconnexion la plus rapide possible, au sein d'un seul nœud (leurs propres expériences utilisent un serveur DGX A100 à 8 GPU). Le parallélisme de pipeline, à l'inverse, ne fait jamais que transmettre des activations entre une poignée de frontières d'étages, au moyen d'une communication point à point que Narayanan et al. décrivent comme « bien moins chère », et qui tolère d'être répartie entre des nœuds distincts sans goulot d'étranglement pour l'ensemble du calcul, au prix de la bulle couverte par la leçon 13. Ils rapportent des performances maximales précisément quand la taille du parallélisme tensoriel correspond au nombre de GPU d'un seul nœud, ce qui confirme que ce n'est pas un détail accessoire : c'est la configuration que leurs propres résultats disent de viser.

### Pourquoi ne pas simplement utiliser ZeRO partout et éviter l'ingénierie supplémentaire

L'article ZeRO de Rajbhandari et al. plaide lui-même directement, en soutenant que, pour le but précis de faire tenir un grand modèle en mémoire, ZeRO-DP (leçons 9 à 11) est au moins aussi efficace que le parallélisme de modèle, parfois plus, avec une efficacité de mise à l'échelle comparable ou meilleure, tout en étant bien plus facile à appliquer : le parallélisme de données, notent-ils, est largement utilisable sur des charges de travail différentes sans changements, alors que les approches en parallélisme de modèle comme le parallélisme tensoriel et de pipeline demandent souvent un vrai travail d'ingénierie, réviser le modèle lui-même et construire pour lui des opérateurs distribués. Le parallélisme tensoriel et de pipeline ne sont pas des alternatives gratuites au partitionnement ; ils coûtent un vrai effort de développement en plus de leur coût de communication.

En réunissant les positions des deux articles, la réponse pratique à « quand le parallélisme tensoriel ou de pipeline vaut-il son coût » est : commencer par un partitionnement de type ZeRO, puisqu'il résout le problème de mémoire avec le moins d'effort d'ingénierie et sans travail propre au modèle. Se tourner vers le parallélisme tensoriel et de pipeline précisément quand un run d'entraînement doit passer à une échelle que le partitionnement seul ne gère plus efficacement, couramment à un nombre d'appareils et une taille de modèle où le surcoût de communication des all-gathers du partitionnement lui-même devient le goulot d'étranglement, ou où les poids reconstruits d'une seule couche restent trop grands pour un appareil même après partitionnement. À ce stade, la combinaison est choisie délibérément pour faire correspondre le schéma de communication à l'interconnexion : les all-reduces fréquents et coûteux du parallélisme tensoriel confinés au sein d'un nœud, les transferts point à point rares et bon marché du parallélisme de pipeline à travers les nœuds, et le parallélisme de données (partitionné ou non) occupant le nombre d'appareils restant.

## Pratique

1. ▢ Une équipe dispose de 64 GPU répartis en 8 nœuds de 8 GPU chacun, avec une interconnexion intra-nœud rapide et des liens inter-nœuds bien plus lents. En suivant la configuration crête rapportée par Narayanan et al., comment affecteraient-ils les degrés de parallélisme tensoriel et de pipeline à ce matériel ?

<details markdown="1"><summary>Vérifier</summary>

Une taille de parallélisme tensoriel de 8, correspondant aux GPU d'un seul nœud, tenue à l'écart des liens inter-nœuds plus lents ; des étages de pipeline répartis sur les 8 nœuds, puisque la communication point à point du parallélisme de pipeline tolère la connexion inter-nœuds plus lente sans goulot d'étranglement pour le calcul.

</details>

2. ▢ D'après l'argument même de l'article ZeRO, pourquoi une équipe pourrait-elle choisir ZeRO-DP plutôt que le parallélisme tensoriel ou de pipeline, alors que tous deux passent à l'échelle de très grands modèles ?

    - a) ZeRO-DP est toujours plus rapide, à n'importe quel nombre d'appareils, pour tous les modèles
    - b) ZeRO-DP atteint une efficacité mémoire comparable ou meilleure sans exiger le travail d'ingénierie propre au modèle (code du modèle révisé, opérateurs distribués) que demandent les approches en parallélisme de modèle
    - c) Le parallélisme tensoriel et de pipeline ne peuvent pas du tout faire tenir des modèles plus grands que la mémoire d'un seul appareil
    - d) ZeRO-DP élimine entièrement le besoin de toute forme de parallélisme

<details markdown="1"><summary>Vérifier</summary>

**b)** est l'argument que l'article ZeRO avance lui-même : une efficacité de mise à l'échelle comparable ou meilleure, pour un coût d'ingénierie bien moindre, puisque le parallélisme de données est largement applicable sans changements propres au modèle. (a) exagère un avantage de vitesse universel que l'article ne revendique pas. (c) est l'opposé du propos des deux articles, à savoir que le parallélisme de modèle existe précisément pour faire tenir de plus grands modèles. (d) contredit le fait que ZeRO-DP repose lui-même sur le parallélisme de données comme fondation.

</details>

3. ▢ D'après le raisonnement de cette leçon, nommez une situation concrète où recourir au parallélisme tensoriel ou de pipeline, malgré leur coût d'ingénierie supplémentaire, serait quand même le bon choix plutôt que ZeRO-DP seul.

<details markdown="1"><summary>Vérifier</summary>

Toute réponse dans cet esprit est défendable : quand le surcoût de communication du partitionnement lui-même devient le goulot d'étranglement à de très grands nombres d'appareils, ou quand les paramètres d'une seule couche restent trop grands pour tenir sur un appareil même après le partitionnement et la reconstruction à la demande de ZeRO, ce qui force le calcul lui-même, et pas seulement son stockage, à être réparti entre des appareils.

</details>

## Exercices en situation réelle

- [ ] Trouvez une configuration d'entraînement publiée pour un grand modèle ouvert (un rapport technique ou une model card qui indique sa configuration de parallélisme) et identifiez quelles parties, le cas échéant, correspondent au parallélisme tensoriel, au parallélisme de pipeline, et au parallélisme de données ou au partitionnement ZeRO.
- [ ] Lisez le paragraphe de l'article Megatron-LM (lié plus haut) qui explique pourquoi le parallélisme tensoriel est confiné au sein d'un nœud, et écrivez une phrase qui l'oppose à l'argument de l'article ZeRO en faveur du parallélisme de données quand c'est possible.
- [ ] Demain : pour un cluster hypothétique de votre choix (choisissez n'importe quel nombre de nœuds et de GPU par nœud), esquissez un plan de parallélisme : ce qui irait à l'intérieur d'un nœud, ce qui traverserait les nœuds, et où le partitionnement ZeRO s'insérerait, et écrivez une phrase pour défendre chaque choix.

## Pour aller plus loin

- [Article : "Efficient Large-Scale Language Model Training on GPU Clusters Using Megatron-LM", Narayanan et al., 2021](https://arxiv.org/abs/2104.04473)
- [Article : "ZeRO: Memory Optimizations Toward Training Trillion Parameter Models", Rajbhandari et al., 2019](https://arxiv.org/abs/1910.02054)
- [Ressources](../RESOURCES.md)

---

L'étape 6 a couvert la manière dont le calcul est réparti entre des appareils, en fonction de ce que l'interconnexion entre eux peut supporter. L'étape 7 aborde un autre genre de défaillance à grande échelle : le numérique du run d'entraînement lui-même, et que faire quand la courbe de loss cesse de se comporter.

Ça ne passe pas ? Relisez la source primaire en haut de page, car cette leçon la condense et c'est dans la condensation que la compréhension s'échappe. Consultez le [glossaire](../GLOSSARY.md) pour tout terme qui vous a paru glissant.

Si c'est la leçon elle-même qui n'est pas claire plutôt que la matière, c'est un défaut : [ouvrez une issue](https://github.com/TokenCemetery/teach/issues).
