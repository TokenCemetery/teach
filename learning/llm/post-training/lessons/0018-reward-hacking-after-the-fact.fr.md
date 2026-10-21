---
title: "18. Le reward hacking après coup"
description: "Un reward model mis de côté peut détecter la dérive pendant l'entraînement ; un modèle terminé demande un autre type de vérification"
type: lesson
---

# Leçon 18. Le reward hacking après coup

**Lien avec la mission :** « Savoir distinguer un vrai gain de capacité d'un artefact de reward hacking ou de biais du juge » est la puce d'« Objectif » que sert cette étape, et cette leçon la conclut, en passant la méthodologie complète à `llm/evals` plutôt qu'en la répétant.
**Source primaire :** Référence : [LLM-as-Judge](../../evals/reference/llm-as-judge.md) (`llm/evals`)
**Prérequis :** [Leçon 17](0017-measuring-the-alignment-tax.md), [Sur-refus](../../evals/GLOSSARY.md)

## Échauffement

1. ▢ Pourquoi Ouyang et al. ont-ils testé InstructGPT avec des annotateurs mis de côté, des personnes qui n'ont fourni aucune donnée d'entraînement ?

<details markdown="1"><summary>Vérifier</summary>

Pour vérifier si le comportement aligné du modèle se généralise au-delà des personnes précises dont les préférences ont façonné l'entraînement, au lieu de simplement s'ajuster étroitement à ce groupe particulier.

</details>

2. ▢ Qu'a ajouté la réduction de 25 % des sorties toxiques à un compte rendu honnête de la taxe d'alignement, au-delà des régressions sur SQuAD, DROP, HellaSwag et WMT ?

<details markdown="1"><summary>Vérifier</summary>

La preuve que l'entraînement à l'alignement a mesurablement aidé sur au moins un axe, et pas seulement coûté quelque chose ; un compte rendu honnête a besoin des deux directions, pas seulement des régressions.

</details>

## À savoir

### Une autre question que la vérification pendant l'entraînement

La divergence train PM contre test PM de la leçon 5 est une vérification menée *pendant* l'entraînement, qui compare une policy à un reward model contre lequel elle n'a jamais été optimisée. Évaluer un modèle aligné *terminé* pose une question voisine mais distincte : étant donné seulement le modèle et ses scores d'évaluation, sans second reward model avec lequel comparer, comment savoir si un score élevé reflète une vraie amélioration plutôt qu'un artefact de la façon dont l'évaluation elle-même a été construite ?

### Un symptôme concret : le sur-refus

`llm/evals` nomme un échec précis et bien documenté dont cette question parle réellement : le **sur-refus** (over-refusal), un modèle qui décline un prompt en réalité sans danger, en général parce qu'il ressemble en surface à un prompt dangereux. Un modèle qui refuse agressivement peut obtenir un score trompeusement bon sur un benchmark de sécurité construit surtout à partir de prompts dangereux, puisque refuser presque tout a exactement l'air d'un modèle réellement prudent sur ce test précis, tout en échouant discrètement sur l'ensemble bien plus vaste de prompts sans danger auxquels il aurait dû répondre. C'est l'échec d'esquive généralisée des leçons 5 et 15, vu du côté de l'évaluation plutôt que du côté de l'entraînement : une eval de type red-team qui ne vérifie que des prompts dangereux ne peut pas le détecter, parce que le sur-refus est un échec sur les prompts sans danger que l'eval n'a jamais posés.

### Le biais du juge est le même problème, un niveau plus haut

Quand une évaluation utilise elle-même un modèle, plutôt qu'un benchmark fixe, pour juger les sorties (un montage de plus en plus courant dont dépendent déjà les leçons RLAIF et Constitutional AI de ce parcours), ce juge peut être dupé de façons qui lui sont propres : préférer les réponses plus longues quelle que soit leur qualité, ou se laisser influencer par la réponse qui se trouve montrée en premier. La fiche de référence de `llm/evals` sur la conception d'un LLM-as-judge couvre en détail ces modes d'échec et les vérifications de calibration qui les détectent. Un score élevé attribué par un juge n'est digne de confiance que dans la mesure où la calibration du juge face à ces biais connus l'est ; un juge non calibré peut être détourné par une policy d'une façon qui ressemble, de l'extérieur, exactement à une vraie amélioration.

### Pourquoi on passe le relais au lieu de répéter

Concevoir un prompt de juge, vérifier la calibration d'un juge et mesurer l'accord d'un juge avec des évaluateurs humains sont le sujet propre de `llm/evals`, couvert là-bas avec la profondeur que ce parcours n'a pas à répéter. Ce que ce parcours possède est plus étroit et propre au post-training : savoir que l'évaluation même d'un pipeline de post-training est exposée précisément à ce risque, reconnaître un symptôme concret comme le sur-refus quand il apparaît, et traiter un score de sécurité ou de préférence suspectement élevé avec le même scepticisme que modélisait déjà, pendant l'entraînement, la comparaison train PM contre test PM de la leçon 5.

## Pratique

1. ▢ Un benchmark de sécurité entièrement composé de prompts dangereux rapporte qu'un modèle en refuse 98 %, un score en apparence excellent. Que ne vous dit pas ce benchmark, à lui seul, sur le modèle ?

<details markdown="1"><summary>Vérifier</summary>

Si le modèle refuse aussi des prompts qui sont en réalité sans danger. Un benchmark construit uniquement à partir de prompts dangereux ne peut pas détecter le sur-refus, puisqu'un modèle qui refuse presque tout a l'air identique à un modèle réellement prudent sur ce test précis.

</details>

2. ▢ Pourquoi qu'un modèle refuse un prompt en réalité sans danger est-il un échec réellement différent d'un jailbreak qui réussit ?

<details markdown="1"><summary>Vérifier</summary>

Un jailbreak est le modèle qui échoue à refuser quelque chose qu'il aurait dû refuser ; le sur-refus est le modèle qui refuse quelque chose qu'il n'aurait pas dû refuser. Ce sont des échecs de direction opposée, et une eval construite pour détecter l'un (un benchmark de type red-team, composé uniquement de prompts dangereux) ne peut pas détecter l'autre.

</details>

3. ▢ Une évaluation utilise un modèle de langage comme juge pour noter laquelle de deux sorties de modèles alignés est la meilleure. Que dit cette leçon qu'il faut vérifier avant de se fier à un grand écart entre les scores de deux modèles ?

<details markdown="1"><summary>Vérifier</summary>

Si le juge lui-même est calibré face aux biais connus (comme favoriser les réponses plus longues ou celle qui apparaît en premier), d'après le contenu LLM-as-judge de `llm/evals` ; un juge non calibré peut être détourné de façon à produire un écart de score qui ressemble à une vraie amélioration sans en être une.

</details>

## Exercices en situation réelle

- [ ] Lisez la fiche de référence [LLM-as-Judge](../../evals/reference/llm-as-judge.md) de `llm/evals` et identifiez une vérification de calibration qu'elle recommande et que vous appliqueriez à une évaluation de post-training avant de vous fier à ses résultats.
- [ ] Trouvez une évaluation de sécurité publiée pour un modèle aligné et vérifiez si elle rapporte un taux de sur-refus sur des prompts sans danger, en plus d'un taux de refus sur des prompts dangereux. Notez lequel des deux, le cas échéant, manque.
- [ ] Demain : pour une évaluation à laquelle vous avez accès ou que vous pouvez imaginer (un benchmark de sécurité, un montage de juge de préférence), nommez un symptôme concret, comme le sur-refus ou un biais de juge connu, que vous vérifieriez avant de vous fier à un score affiché par elle.

## Pour aller plus loin

- [LLM-as-Judge](../../evals/reference/llm-as-judge.md)
- [Ressources](../RESOURCES.md)

---

L'étape 9 a couvert la distinction entre un vrai gain d'alignement et un artefact, pendant l'entraînement et après coup. L'étape 10 clôt l'arc : choisir parmi tout ce que ce parcours a couvert, pour un budget donné, et défendre ce choix.

Ça ne passe pas ? Relisez la source primaire en haut de page, car cette leçon la condense et c'est dans la condensation que la compréhension s'échappe. Consultez le [glossaire](../GLOSSARY.md) pour tout terme qui vous a paru glissant.

Si c'est la leçon elle-même qui n'est pas claire plutôt que la matière, c'est un défaut : [ouvrez une issue](https://github.com/TokenCemetery/teach/issues).
