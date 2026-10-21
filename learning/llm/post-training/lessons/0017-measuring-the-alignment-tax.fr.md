---
title: "17. Mesurer la taxe d'alignement"
description: "La taxe n'apparaît pas partout en même temps, et un axe a même mesuré une amélioration à la place"
type: lesson
---

# Leçon 17. Mesurer la taxe d'alignement

**Lien avec la mission :** « Savoir distinguer un vrai gain de capacité d'un artefact de reward hacking ou de biais du juge » est la puce d'« Objectif » que sert cette étape. Cette leçon couvre la façon dont la taxe d'alignement est réellement mesurée, et pas seulement ce qu'elle est ; la leçon 18 couvre la détection du reward hacking une fois l'entraînement terminé, et passe le relais à `llm/evals` pour la méthodologie complète.
**Source primaire :** [Article : "Training language models to follow instructions with human feedback", Ouyang et al., 2022](https://arxiv.org/abs/2203.02155)
**Prérequis :** [Leçon 16](0016-rlaif-how-well-ai-feedback-actually-matches-human-feedback.md), [Taxe d'alignement](../GLOSSARY.md)

## Échauffement

1. ▢ Qu'est-ce que direct-RLAIF (d-RLAIF), et comment sa performance se comparait-elle à celle du RLAIF canonique, d'après Lee et al. ?

<details markdown="1"><summary>Vérifier</summary>

Une technique qui saute l'entraînement d'un reward model séparé, en interrogeant directement un modèle de langage prêt à l'emploi pour obtenir un score de récompense pendant le RL. Lee et al. ont constaté qu'elle atteignait une meilleure performance que le RLAIF canonique, pas simplement une performance comparable à moindre coût.

</details>

2. ▢ Pour laquelle des trois tâches testées par Lee et al. RLAIF a-t-il surpassé RLHF, au lieu de simplement l'égaler ?

<details markdown="1"><summary>Vérifier</summary>

La génération de dialogue inoffensif.

</details>

## À savoir

### La taxe n'est pas un nombre unique ; c'est un ensemble de mesures séparées

La leçon 1 a présenté la taxe d'alignement comme un coût réel et mesuré, sans détailler comment on la mesure. Ouyang et al. l'ont fait en confrontant leur modèle aligné à une batterie de benchmarks NLP publics existants et en comparant le résultat au modèle de base non aligné, sur chaque benchmark séparément, au lieu de tout ramener à un chiffre unique de taxe. Ils rapportent des régressions précises sur certains benchmarks, notamment SQuAD, DROP, HellaSwag et la traduction WMT 2015 du français vers l'anglais, et, point important, **aucun changement significatif** sur deux autres qu'ils ont aussi vérifiés, Winogender et CrowSPairs (benchmarks liés aux biais). La taxe est apparue sur certains axes et pas sur d'autres ; la traiter comme un coût uniforme aurait masqué ce motif.

### L'alignement a aussi produit un gain mesuré, pas seulement un coût

La même batterie d'évaluation incluait un axe où l'entraînement à l'alignement s'est mesuré comme une amélioration plutôt que comme un coût : avec le jeu de données RealToxicityPrompts, Ouyang et al. rapportent qu'InstructGPT génère environ 25 % de sorties toxiques en moins que GPT-3 quand on lui demande d'être respectueux. Un compte rendu honnête de ce que l'entraînement à l'alignement a fait aux capacités mesurées d'un modèle doit inclure ce type de résultat à côté des régressions ; ne rapporter que la taxe et ignorer les endroits où le même entraînement a aidé serait tout aussi trompeur que de ne rapporter aucune taxe.

### Le correctif, et ce qu'il n'a pas coûté

La leçon 6 a déjà nommé le mécanisme : mélanger les mises à jour PPO avec des mises à jour qui augmentent la vraisemblance de la distribution de pré-entraînement d'origine (PPO-ptx) a fortement réduit les régressions mesurées sur SQuAD, DROP, HellaSwag et WMT. Ouyang et al. précisent que cette récupération s'est faite **sans compromettre les scores de préférence des annotateurs**, c'est-à-dire que le correctif n'a pas simplement échangé les gains d'alignement contre la performance de benchmark perdue ; les deux ont été mesurés, séparément, et le correctif en a amélioré un sans coûter visiblement à l'autre.

### Une autre vérification de généralisation, plus difficile à truquer : les annotateurs mis de côté

Au-delà des régressions de benchmark, Ouyang et al. mènent une vérification qui vise une autre question : le comportement aligné du modèle se généralise-t-il au-delà des personnes précises dont les préférences l'ont façonné, ou a-t-il simplement appris à plaire aux annotateurs particuliers de ses données d'entraînement ? Ils le testent avec des **annotateurs mis de côté** (held-out), des personnes qui n'ont fourni aucune donnée servant à entraîner le modèle, et constatent que ces annotateurs préféraient quand même les sorties d'InstructGPT. C'est la même idée sous-jacente pour laquelle `llm/pretraining` et `llm/evals` utilisent tous deux des données held-out : un résultat ne signifie ce qu'il prétend signifier que s'il n'a pas pu être produit par un simple ajustement aux données (ou aux personnes) précises qui ont façonné l'entraînement.

## Pratique

1. ▢ Ouyang et al. rapportent des régressions sur SQuAD, DROP, HellaSwag et la traduction WMT, mais aucun changement significatif sur Winogender et CrowSPairs. Qu'aurait masqué, dans ce résultat, le fait de traiter la taxe d'alignement comme un nombre global unique ?

<details markdown="1"><summary>Vérifier</summary>

Que la taxe ne s'appliquait pas uniformément ; elle est apparue nettement sur certains benchmarks et pas du tout sur d'autres. Un nombre unique, tout ramené à un seul chiffre, présenterait ce motif inégal comme un seul coût cohérent sur chaque capacité.

</details>

2. ▢ Pourquoi la réduction de 25 % des sorties toxiques compte-t-elle pour un compte rendu honnête de la taxe d'alignement, plutôt que de ne rapporter que les régressions sur SQuAD, DROP, HellaSwag et WMT ?

<details markdown="1"><summary>Vérifier</summary>

Parce que l'entraînement à l'alignement a mesurablement aidé sur cet axe au lieu de coûter quoi que ce soit ; ne rapporter que les régressions et omettre ce résultat sous-estimerait ce que l'entraînement a réellement fait, de la même façon que ne rapporter aucune taxe le surestimerait.

</details>

3. ▢ Qu'ont précisément vérifié Ouyang et al. sur le correctif PPO-ptx de la taxe d'alignement, au-delà de la simple réduction des régressions de benchmark ?

<details markdown="1"><summary>Vérifier</summary>

Qu'il y parvenait sans compromettre les scores de préférence des annotateurs ; la récupération de performance sur les benchmarks n'a pas été payée en rendant les gains d'alignement par-dessus lesquels PPO-ptx a été ajouté.

</details>

4. ▢ Pourquoi tester avec des annotateurs mis de côté, des personnes qui n'ont fourni aucune donnée d'entraînement, répond-il à une autre question que les mesures de régression de benchmark ?

<details markdown="1"><summary>Vérifier</summary>

Les régressions de benchmark mesurent si des capacités précises ont empiré. Les annotateurs mis de côté testent si le comportement aligné du modèle se généralise réellement à des préférences au-delà des personnes précises qui ont façonné l'entraînement, au lieu de simplement s'ajuster étroitement à ce groupe particulier ; un résultat qui ne tiendrait que pour les annotateurs d'origine ne soutiendrait pas la même affirmation de généralisation.

</details>

## Exercices en situation réelle

- [ ] Trouvez un rapport technique de post-training publié et vérifiez s'il rapporte à la fois des régressions et des améliorations sur une batterie de benchmarks, ou une seule direction. Notez quels benchmarks, le cas échéant, n'ont montré aucun changement significatif.
- [ ] Lisez le paragraphe de l'article InstructGPT (lié plus haut) qui décrit l'expérience avec des annotateurs mis de côté, et écrivez une phrase disant quel résultat vous aurait fait douter que l'alignement du modèle se généralise au-delà de ses annotateurs d'entraînement.
- [ ] Demain : sans regarder la suite, écrivez une prédiction d'une phrase pour la leçon 18 : sachant qu'un reward model ou un juge IA peut être détourné (leçon 5), que devrait vérifier l'évaluation d'un modèle aligné *terminé*, une fois l'entraînement fini, qu'une comparaison train PM contre test PM pendant l'entraînement ne pouvait pas vérifier ?

## Pour aller plus loin

- [Article : "Training language models to follow instructions with human feedback", Ouyang et al., 2022](https://arxiv.org/abs/2203.02155)
- [Ressources](../RESOURCES.md)

---

Ça ne passe pas ? Relisez la source primaire en haut de page, car cette leçon la condense et c'est dans la condensation que la compréhension s'échappe. Consultez le [glossaire](../GLOSSARY.md) pour tout terme qui vous a paru glissant.

Si c'est la leçon elle-même qui n'est pas claire plutôt que la matière, c'est un défaut : [ouvrez une issue](https://github.com/TokenCemetery/teach/issues).
