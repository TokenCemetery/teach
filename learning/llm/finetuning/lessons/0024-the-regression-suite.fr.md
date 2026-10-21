---
title: "24. Le jeu de régression"
description: "Attraper les dégâts que tous les autres chiffres cachent"
type: lesson
---

# Leçon 24. Le jeu de régression

**Lien avec la mission :** « Construire une eval qui attrape une régression avant la livraison » est la formulation même de la mission. C'est cette leçon.
**Source primaire :** [Article : "An Empirical Study of Catastrophic Forgetting in Large Language Models During Continual Fine-tuning", Luo et al., arXiv:2308.08747](https://arxiv.org/abs/2308.08747)
**Prérequis :** [Leçon 23](0023-metrics-that-mean-something.md), [Leçon 22](0022-contamination-and-held-out-design.md)

## Échauffement

1. ▢ Pourquoi la loss est-elle une mauvaise base pour une décision ?

<details markdown="1"><summary>Vérifier</summary>

Elle note l'accord avec une suite de référence, pénalisant les alternatives correctes et récompensant les erreurs fluides. Utilisez-la pour sélectionner les checkpoints, pas pour décider.

</details>

2. ▢ Deux biais documentés des modèles-juges, et leurs atténuations ?

<details markdown="1"><summary>Vérifier</summary>

Biais de position : randomiser l'ordre et évaluer les deux ordres. Biais de verbosité : comparer à longueurs égales ou demander au juge de ne pas tenir compte de la longueur.

</details>

3. ▢ Pourquoi le jeu held-out de votre tâche est-il aveugle à l'oubli catastrophique ?

<details markdown="1"><summary>Vérifier</summary>

Il est tiré de la distribution de votre tâche, donc il ne peut pas observer la dégradation de capacités extérieures à cette distribution.

</details>

## À savoir

### La défaillance que ceci existe pour attraper

Le fine-tuning déplace les poids vers votre tâche. Les capacités qui n'ont pas été renforcées peuvent se dégrader, et c'est l'**oubli catastrophique**. La littérature empirique constate que ce n'est pas un cas marginal rare dans le fine-tuning continu des modèles de langage : les capacités générales, dont le suivi d'instructions, déclinent de façon mesurable, et l'effet peut grandir avec l'échelle du modèle au lieu de diminuer.

La propriété dangereuse est que **chaque chiffre que vous regardez déjà va dans le bon sens.** La loss d'entraînement baisse, votre métrique de tâche held-out s'améliore, vos sondes ont l'air bonnes, et le modèle est devenu moins bon sur des choses que vous n'avez jamais mesurées. Vous livrez, et les retours viennent d'une direction que votre évaluation ne pouvait pas voir.

Un jeu held-out mesure si vous avez appris la tâche. Un jeu de régression mesure si vous avez cassé autre chose. **Ce sont des instruments différents et il vous faut les deux.**

### Ce qu'il contient

Quatre catégories. Les quatre, pas une sélection.

**1. Suivi d'instructions général.** Peut-il toujours suivre une instruction ordinaire sans rapport avec votre tâche ? Résumer quelque chose, répondre à une question générale, suivre une demande en plusieurs étapes.

**2. Respect du format et du comportement.** Respecte-t-il toujours un system prompt ? Produit-il toujours du JSON valide quand on le demande ? S'arrête-t-il toujours quand il le doit ? Un modèle entraîné sur un format rigide perd parfois la capacité d'en produire un autre.

**3. Sécurité et comportement de refus.** Si le base model refusait certaines requêtes, le fine-tuning les refuse-t-il toujours ? **Le fine-tuning sur des données bénignes peut dégrader l'alignement de sécurité comme effet secondaire.** C'est un résultat documenté et reproduit à plusieurs reprises, pas une hypothèse. Si vous avez hérité d'un comportement d'alignement d'un modèle instruct, vous avez hérité de la responsabilité de vérifier qu'il a survécu.

**4. Capacité voisine.** Des choses proches de votre tâche que vous n'avez pas entraînées. Fine-tuning sur des tickets de support en anglais ? Vérifiez une autre langue. Fine-tuning sur un type de document ? Vérifiez-en un autre.

### Le construire

Petit, fixe, et lu par un humain.

```text
regression/
├── instruction-following.jsonl   # 20 general instructions
├── format-compliance.jsonl       # 20 schema and system-prompt cases
├── safety.jsonl                  # 20 cases the base refused
├── adjacent.jsonl                # 20 near-task, untrained cases
└── baseline/                     # base model outputs, committed
```

Quatre-vingts exemples au total. C'est délibérément petit : assez pour attraper une vraie régression, assez petit pour qu'une personne lise réellement les différences.

L'étape cruciale, fréquemment omise : **enregistrer les sorties du base model avant d'entraîner, et les committer.** Une régression est un *changement*, donc il vous faut l'avant. Sans référence stockée, il ne vous reste qu'à comparer au souvenir que vous avez du comportement antérieur du modèle, ce qui n'est pas une preuve.

```python
# Run once, before any training. Commit the result.
for case in regression_cases:
    out = base_model.generate(**tok(case["prompt"]), do_sample=False, max_new_tokens=256)
    baseline[case["id"]] = tok.decode(out[0], skip_special_tokens=True)
```

Décodage glouton, pour qu'une différence signifie un changement de poids plutôt qu'un tirage de l'échantillonneur.

### Le lire

Exécutez le jeu sur chaque checkpoint candidat. Comparez à la référence. Puis classez chaque changement :

| Verdict | Signification |
|---|---|
| Inchangé | Correct |
| Changé, toujours correct | À noter ; correct |
| Changé, maintenant faux | **Régression, bloque la livraison** |
| Changé, maintenant meilleur | Un bonus, qui mérite d'être compris |

La troisième ligne est tout l'enjeu. Une seule régression nette en sécurité ou en suivi d'instructions pèse plus que quelques points sur votre métrique de tâche, parce que le mode de défaillance n'est pas borné et que le gain l'est.

### Réduire l'oubli, quand vous le trouvez

Options à peu près dans l'ordre de ce qu'elles vous coûtent :

1. **Moins de pas, ou un checkpoint plus précoce.** L'oubli croît avec l'entraînement. Souvent le correctif le moins cher, et il coûte généralement peu de performance sur la tâche.
2. **Learning rate plus bas.** Des mises à jour plus petites perturbent moins.
3. **Rank plus bas, ou moins de target modules.** Moins de capacité pour écraser.
4. **Mélanger des données d'instructions générales.** Quelques pour cent d'exemples de suivi d'instructions général à côté de vos données de tâche. Efficace et bien établi, et cela vous coûte de la pureté de dataset plutôt que de la qualité de modèle.
5. **Garder l'adapter non fusionné et router.** La réponse la plus complète : n'appliquer l'adapter que pour les requêtes qui en ont besoin, et servir le base model intact pour tout le reste. L'oubli devient sans importance parce que le base model est toujours là. Leçon 25.

L'option 5 est celle que les gens négligent, et c'est souvent la bonne architecture. Si votre fine-tuning sert un seul but étroit à l'intérieur d'un produit plus vaste, vous n'avez pas besoin d'un seul modèle qui fait tout.

### L'automatiser

Le jeu devrait s'exécuter sur chaque checkpoint, sans qu'on le demande, et refuser de passer en cas de régression. Une évaluation qui dépend de quelqu'un qui pense à la lancer sera sautée sur le run où elle comptait, celui qui est sous pression de délai.

## Pratique

1. ▢ Pourquoi une métrique de tâche held-out qui s'améliore de façon monotone n'exclut-elle pas une régression ?

<details markdown="1"><summary>Vérifier</summary>

Elle est tirée de la distribution de votre tâche et n'observe donc que votre tâche. Les capacités extérieures à cette distribution lui sont invisibles, et ce sont précisément celles que l'oubli abîme.

Il vous faut un instrument séparé dirigé vers ce que vous n'entraînez *pas*.

</details>

2. ▢ Nommez les quatre catégories de régression.

<details markdown="1"><summary>Vérifier</summary>

Suivi d'instructions général, respect du format et du comportement, sécurité et comportement de refus, capacité voisine non entraînée.

La sécurité est celle qu'on laisse le plus souvent de côté, et le fine-tuning sur des données entièrement bénignes peut la dégrader.

</details>

3. ▢ Vous avez un jeu de régression mais pas de référence stockée. Que pouvez-vous conclure en l'exécutant ?

<details markdown="1"><summary>Vérifier</summary>

Très peu. Une régression est un changement par rapport au comportement antérieur, donc sans ce comportement antérieur vous ne pouvez pas en identifier une, seulement juger les sorties isolément, ce qui ne révélera pas une dégradation subtile.

Enregistrez et committez les sorties du base model avant d'entraîner. C'est l'étape qui fait fonctionner le jeu.

</details>

4. ▢ Métrique de tâche en hausse de 3 points ; le modèle ne refuse plus une requête que le base model refusait. Livrer ?

<details markdown="1"><summary>Vérifier</summary>

Non. Une régression de sécurité bloque la livraison quels que soient les gains sur la tâche : le risque n'est pas borné, alors que trois points le sont.

Enquêtez : essayez un checkpoint plus précoce, un learning rate plus bas, le mélange de données d'instructions générales, ou garder l'adapter non fusionné et ne lui router que le trafic pertinent.

</details>

5. ▢ Qu'est-ce qui élimine le plus complètement le problème de l'oubli ?

    - a) Mélanger des données d'instructions générales au jeu d'entraînement
    - b) Servir le base model non fusionné et router par requête
    - c) Baisser le learning rate et entraîner moins de pas
    - d) Réduire le rank de l'adapter et le nombre de target modules

<details markdown="1"><summary>Vérifier</summary>

**b)** Servir le base model non fusionné et router par requête.

Les autres réduisent la quantité d'oubli. Le routage fait que le base model non modifié reste disponible pour tout ce qui est extérieur à votre tâche, donc l'oubli dans le chemin adapté cesse d'avoir de l'importance.

</details>

6. ▢ Pourquoi le décodage glouton pour le jeu de régression ?

<details markdown="1"><summary>Vérifier</summary>

Pour qu'une différence par rapport à la référence soit attribuable à des poids modifiés plutôt qu'à l'échantillonnage. Avec une temperature supérieure à zéro, chaque run diffère et la comparaison ne porte aucune information.

</details>

## Exercices en situation réelle

- [ ] Écrivez 20 cas de régression, cinq par catégorie. Incluez-en au moins un que le base model refuse.
- [ ] Générez et committez les sorties de référence du base model, en décodage glouton, avant tout entraînement.
- [ ] Exécutez le jeu sur votre adapter existant et comparez. Classez chaque changement dans les quatre verdicts.
- [ ] Demain : câblez le jeu dans votre script d'entraînement pour qu'il s'exécute sur chaque checkpoint sans qu'on le demande.

## Pour aller plus loin

- [Article : "An Empirical Study of Catastrophic Forgetting in Large Language Models During Continual Fine-tuning", Luo et al., arXiv:2308.08747](https://arxiv.org/abs/2308.08747)
- [Article : "Fine-tuning Aligned Language Models Compromises Safety, Even When Users Do Not Intend To!", Qi et al., arXiv:2310.03693](https://arxiv.org/abs/2310.03693)
- [Modes de défaillance](../reference/failure-modes.md)
- [Leçon 25. Servir des adapters](0025-serving-adapters.md)

---

Ça ne passe pas ? Relisez la source primaire en haut de page, car cette leçon la condense et c'est dans la condensation que la compréhension s'échappe. Consultez le [glossaire](../GLOSSARY.md) pour tout terme qui vous a paru glissant.

Si c'est la leçon elle-même qui n'est pas claire plutôt que la matière, c'est un défaut : [ouvrez une issue](https://github.com/TokenCemetery/teach/issues).
