---
title: "23. Des métriques qui veulent dire quelque chose"
description: "La loss sélectionne les checkpoints ; les métriques de tâche prennent les décisions"
type: lesson
---

# Leçon 23. Des métriques qui veulent dire quelque chose

**Lien avec la mission :** « Prouver que cela a fonctionné » fait partie de la mission. Un chiffre qu'on ne peut pas défendre n'est pas une preuve.
**Source primaire :** [Article : "Judging LLM-as-a-Judge with MT-Bench and Chatbot Arena", Zheng et al., arXiv:2306.05685](https://arxiv.org/abs/2306.05685)
**Prérequis :** [Leçon 22](0022-contamination-and-held-out-design.md), [Leçon 12](0012-reading-a-training-run.md)

## Échauffement

1. ▢ Pourquoi trois découpages plutôt que deux ?

<details markdown="1"><summary>Vérifier</summary>

Sélectionner face à un ensemble s'ajuste à lui. La validation absorbe votre sélection ; le test reste intact pour pouvoir donner une estimation non biaisée.

</details>

2. ▢ Combien d'exemples held-out faut-il à peu près pour détecter une différence de 2 points ?

<details markdown="1"><summary>Vérifier</summary>

Des milliers. Le besoin croît de façon quadratique à mesure que la différence diminue.

</details>

3. ▢ Nommez deux choses que la loss ne peut pas voir.

<details markdown="1"><summary>Vérifier</summary>

Si les générations sont utilisables, et si des capacités extérieures à la distribution de la tâche se sont dégradées.

</details>

## À savoir

### Pourquoi la loss n'est pas la métrique

La loss d'entropie croisée sur des données held-out est réellement utile : elle est bon marché, stable, et c'est la bonne chose à surveiller pendant un run. Ce n'est pas une mesure de si le modèle fait votre travail.

La loss mesure la surprise sur le token suivant face à une suite de référence précise. Elle pénalise donc une réponse correcte formulée autrement et récompense une réponse fausse mais fluide. Deux modèles à loss held-out égale peuvent différer substantiellement en utilité, et le sens n'est pas prévisible.

**Utilisez la loss pour sélectionner les checkpoints. Utilisez une métrique de tâche pour les décisions.**

### Choisir selon la forme de la tâche

| Forme de la tâche | Métrique | À surveiller |
|---|---|---|
| Classification | Précision globale (accuracy) ; precision et recall par classe ; F1 | Un déséquilibre de classes rend l'accuracy sans signification |
| Extraction | Exact match sur le champ ; F1 sur les segments | Normaliser avant de comparer |
| Sortie structurée | Taux de validité du schéma, puis exactitude au niveau des champs | Deux défaillances distinctes, mesurez les deux |
| Code | Exécution face à des tests | Réussir les tests, pas ressembler à la référence |
| Génération libre | Notation par grille, par un humain ou par un modèle | Le cas difficile ; voir plus bas |
| Voisin de la récupération | Fidélité (groundedness), exactitude des citations | La fluidité masque les affirmations non étayées |

Notez ce qui manque : pour tout ce qui a une réponse vérifiable, **vérifiez la réponse.** Exécutez le code. Validez le schéma. Comparez le champ extrait. C'est peu coûteux, objectif, et bien meilleur que n'importe quel score de similarité.

### Sur les métriques de similarité de surface

BLEU, ROUGE et leurs cousines mesurent le recouvrement de n-grammes avec une référence. Elles ont été construites pour la traduction automatique et le résumé, et pour les tâches de suivi d'instructions elles sont faibles : une bonne réponse formulée autrement obtient un mauvais score, une mauvaise réponse qui réutilise le vocabulaire de la référence obtient un bon score.

Ne les utilisez que lorsque le recouvrement est réellement ce qui vous importe, et jamais comme seule métrique. Si vous vous surprenez à optimiser ROUGE sur une tâche qui n'est pas du résumé, arrêtez-vous.

### Sortie structurée : deux défaillances, deux chiffres

Pour du JSON ou n'importe quel schéma, rapportez toujours les deux :

1. **Validité.** A-t-il été analysé et satisfait-il le schéma ?
2. **Exactitude.** Étant donné qu'il a été analysé, les valeurs sont-elles justes ?

Les fusionner masque le problème que vous avez. Un modèle à 99 % de validité et 60 % d'exactitude a besoin de meilleures données. Un autre à 60 % de validité et 95 % d'exactitude a besoin d'un entraînement au format, ou d'un décodage contraint au moment du service, qui peut faire disparaître le problème sans ré-entraînement du tout.

### Modèle-juge, utilisé avec soin

Pour une sortie libre, faire noter par un modèle fort selon une grille est souvent la seule option qui passe à l'échelle. Cela fonctionne, et cela a des biais documentés qu'il faut contrôler :

- **Biais de position.** Les juges favorisent la réponse présentée en premier. Atténuez en randomisant l'ordre et, pour une comparaison par paires, en évaluant les deux ordres.
- **Biais de verbosité.** Les réponses plus longues obtiennent de meilleurs scores quelle que soit leur qualité. Surveillez si votre fine-tuning est simplement devenu plus bavard.
- **Auto-préférence.** Les juges ont tendance à favoriser un texte qui ressemble à leur propre sortie.
- **Sensibilité à la grille.** De petits changements de formulation dans la grille déplacent sensiblement les scores.

L'étape non négociable : **calibrer le juge face à des étiquettes humaines.** Notez vous-même 50 à 100 exemples, faites passer le juge sur les mêmes, et mesurez l'accord. Si l'accord est faible, les chiffres du juge ne sont que de la décoration. S'il est bon, vous avez gagné le droit de le faire passer à l'échelle, et vous avez un chiffre qui quantifie à quel point lui faire confiance.

Une configuration concrète et robuste : comparaison par paires entre la sortie du base model et celle du modèle fine-tuné, dans les deux ordres, avec une grille qui nomme les critères précis qui vous importent, rapportée sous forme de taux de victoire. Le jugement par paires est plus fiable que la notation absolue, qui dérive.

### Rapportez l'incertitude ou ne rapportez rien

Un chiffre isolé sans dispersion n'est pas un résultat. Norme minimale :

- **Intervalles de confiance** sur la métrique. Pour une proportion, bootstrap ou intervalle binomial.
- **Plusieurs seeds** quand on compare des configurations d'entraînement, puisque la variance d'un run à l'autre dépasse souvent l'effet.
- **Comparaison appariée** sur des exemples identiques (leçon 22).
- **Le n** sur lequel le chiffre est calculé, indiqué.

« 71.2 contre 70.8 » n'est pas une conclusion. « 71.2 ± 2.1 contre 70.8 ± 1.9 sur n=340, trois seeds » est une conclusion, et la conclusion est que vous n'avez pas détecté de différence.

### Lisez les sorties

Quelle que soit votre métrique, lisez à chaque fois un échantillon de vraies générations, échecs compris. Les métriques compressent, et ce qu'elles compressent est généralement ce qu'il fallait savoir : le modèle s'est mis à refuser, ou à émettre un préambule, ou à tronquer, ou à répondre à une question subtilement différente. Aucun agrégat ne le révèle. Dix minutes de lecture, si.

## Pratique

1. ▢ Deux modèles ont une loss held-out identique. L'un peut-il être substantiellement plus utile ?

<details markdown="1"><summary>Vérifier</summary>

Oui. La loss mesure l'accord avec une suite de référence, donc elle pénalise les bonnes réponses formulées autrement et récompense les mauvaises mais fluides.

Une loss égale est compatible avec une grande différence de performance sur la tâche, dans un sens comme dans l'autre. C'est pourquoi la loss sélectionne les checkpoints et les métriques de tâche prennent les décisions.

</details>

2. ▢ Votre modèle émet du JSON. Quels deux chiffres rapportez-vous, et pourquoi pas un seul ?

<details markdown="1"><summary>Vérifier</summary>

Le taux de validité du schéma, et l'exactitude au niveau des champs parmi les sorties valides.

Un chiffre combiné masque le problème que vous avez. Une validité élevée avec une exactitude faible est un problème de données ; une validité faible avec une exactitude élevée est un problème de format que le décodage contraint peut résoudre sans ré-entraînement.

</details>

3. ▢ Le score du juge de votre fine-tuning est passé de 6.2 à 7.1. La longueur moyenne des réponses est passée de 90 à 340 tokens. Une réserve ?

<details markdown="1"><summary>Vérifier</summary>

Oui : le biais de verbosité. Les juges favorisent de façon fiable les réponses plus longues quelle que soit leur qualité, donc une grande partie de ce gain peut être de la longueur.

Contrôlez-la : comparez à longueurs égales, demandez explicitement au juge de ne pas tenir compte de la longueur, ou vérifiez si les utilisateurs préfèrent réellement la sortie plus longue. Le score seul ne distingue pas « meilleur » de « plus long ».

</details>

4. ▢ Quelle métrique évalue le mieux un fine-tuning de génération de code ?

    - a) ROUGE face à l'implémentation de référence fournie
    - b) L'exécution face à une suite de tests pour chaque problème
    - c) La loss d'entropie croisée held-out sur les tokens de code
    - d) Un modèle-juge qui note la lisibilité et l'exactitude

<details markdown="1"><summary>Vérifier</summary>

**b)** L'exécution face à une suite de tests pour chaque problème.

Le code a un critère de correction objectif, alors utilisez-le. Les métriques de recouvrement récompensent la ressemblance avec la référence plutôt que le bon fonctionnement ; la loss a le même problème ; un juge est un détour inutile quand on peut simplement exécuter le code.

</details>

5. ▢ Quelle étape unique donne le droit de faire confiance à un modèle-juge à l'échelle ?

<details markdown="1"><summary>Vérifier</summary>

Le calibrer face à des étiquettes humaines, en notant vous-même 50 à 100 exemples et en mesurant l'accord avec le juge sur les mêmes éléments.

Sans cela, les chiffres du juge ne sont pas validés. Avec cela, vous avez à la fois une justification et un degré de confiance quantifié.

</details>

6. ▢ Votre fine-tuning de classifieur rapporte 94 % d'accuracy. Que devez-vous savoir avant de croire que cela veut dire quelque chose ?

<details markdown="1"><summary>Vérifier</summary>

La distribution des classes. Si 94 % des exemples appartiennent à une seule classe, un modèle qui devine toujours cette classe obtient 94 % et n'a rien appris.

Rapportez la precision et le recall par classe, ou une métrique équilibrée. L'accuracy sur des données déséquilibrées est l'un des chiffres les plus trompeurs d'usage courant.

</details>

## Exercices en situation réelle

- [ ] Choisissez votre métrique principale et rédigez un paragraphe qui défend pourquoi elle mesure ce qui vous importe. Nommez ce qu'elle manque.
- [ ] Calculez un intervalle de confiance sur votre métrique actuelle. Décidez si votre jeu held-out peut soutenir la comparaison que vous voulez.
- [ ] Si vous utilisez un modèle-juge : étiquetez à la main 50 exemples, faites passer le juge sur les mêmes, et rapportez l'accord.
- [ ] Demain : lisez vingt vraies générations, chaque échec compris. Notez une chose que la métrique ne vous a pas dite.

## Pour aller plus loin

- [Article : "Judging LLM-as-a-Judge with MT-Bench and Chatbot Arena", Zheng et al., arXiv:2306.05685](https://arxiv.org/abs/2306.05685)
- [Code : lm-evaluation-harness, EleutherAI](https://github.com/EleutherAI/lm-evaluation-harness)
- [Leçon 24. Le jeu de régression](0024-the-regression-suite.md)

---

Ça ne passe pas ? Relisez la source primaire en haut de page, car cette leçon la condense et c'est dans la condensation que la compréhension s'échappe. Consultez le [glossaire](../GLOSSARY.md) pour tout terme qui vous a paru glissant.

Si c'est la leçon elle-même qui n'est pas claire plutôt que la matière, c'est un défaut : [ouvrez une issue](https://github.com/TokenCemetery/teach/issues).
