---
title: "3. Des instructions claires"
description: "Écrire une instruction qu'un débutant capable pourrait suivre : le contexte, la tâche, les contraintes et à quoi ressemble « terminé »"
type: lesson
---

# Leçon 3. Des instructions claires

**Lien avec la mission :** La plupart des prompts qui échouent ne piègent ni ne troublent le modèle : ce sont des demandes sous-spécifiées. L'amélioration la moins coûteuse de n'importe quel prompt consiste donc à dire ce qu'un inconnu compétent aurait besoin de savoir.
**Source primaire :** [Doc : "Prompting best practices", Claude Platform Docs](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/claude-prompting-best-practices#be-clear-and-direct)
**Prérequis :** [Leçon 2](0002-system-prompts-and-roles.md), [Prompt zero-shot](../GLOSSARY.md)

## Échauffement

1. ▢ Une ligne dit « Reply in at most three sentences. » Relève-t-elle du system prompt ou du tour de l'utilisateur, et pourquoi ?

<details markdown="1"><summary>Vérifier</summary>

Du system prompt, parce qu'elle doit tenir à chaque requête, pas seulement à celle-ci.

</details>

2. ▢ Le prompt rendu pour un chat se termine par le marqueur de rôle de l'assistant. Que fait le modèle à partir de là ?

<details markdown="1"><summary>Vérifier</summary>

Il prolonge la séquence de tokens à partir de ce point, et c'est ainsi qu'il écrit la réponse.

</details>

## À savoir

### Le test du collègue

Le guide d'Anthropic vous demande de voir le modèle comme un employé brillant mais nouveau, qui ne connaît ni vos normes ni vos flux de travail. Sa règle d'or : montrez votre prompt à un collègue qui connaît très peu la tâche et demandez-lui de le suivre. S'il serait perdu, le modèle le sera aussi.

Le modèle ne peut pas demander ce que vous avez voulu dire, donc tout ce que vous omettez, il le comble par une supposition. Le guide dit aussi que si vous voulez un comportement « au-delà du minimum », vous devez le demander explicitement plutôt que de compter sur le modèle pour l'inférer d'un prompt vague.

### Quatre parties d'une instruction claire

| Partie | Répond à | Exemple |
|---|---|---|
| Contexte | À qui est-ce destiné, et pourquoi est-ce important ? | « Ces résumés vont à des responsables du support très occupés qui lisent sur leur téléphone. » |
| Tâche | Que faut-il faire exactement ? | « Résumez le ticket ci-dessous. » |
| Contraintes | Quelles limites s'appliquent ? | « 40 mots au maximum. Aucun nom de client. » |
| À quoi ressemble « terminé » | Comment saurez-vous que cela a fonctionné ? | « Un responsable peut décider d'ouvrir ou non le ticket à partir du seul résumé. » |

Le guide d'Anthropic dit que donner la motivation derrière une instruction, par exemple pourquoi un comportement compte, peut aider le modèle à fournir des réponses plus ciblées. Les recommandations de Google sur la conception de prompts citent de même les contraintes et le format de réponse parmi les éléments à préciser. « À quoi ressemble terminé » est la partie la plus souvent absente, et c'est aussi celle dont vous aurez besoin plus tard quand vous testerez une modification de prompt contre un jeu de régression.

### Dire quoi faire, et numéroter les étapes qui doivent se dérouler dans l'ordre

Le guide d'Anthropic recommande de dire au modèle ce qu'il doit faire plutôt que ce qu'il ne doit pas faire : au lieu de « Do not use markdown », écrire « Your response should be composed of smoothly flowing prose paragraphs. » Il suggère aussi des étapes numérotées séquentielles quand l'ordre ou l'exhaustivité des étapes compte.

### Un avant et un après

```text
Summarise this ticket.
```

```text
You are helping a support team triage tickets. The summaries are read by managers on their phones, who decide from the summary alone whether to open the ticket.
Summarise the ticket below in at most 40 words, in plain prose, leaving out customer names. State the problem first and the customer's requested outcome last.
```

Le second prompt est plus long parce qu'il porte du contexte, des contraintes et un but. Sa longueur supplémentaire est de l'information, pas de la décoration.

## Pratique

1. ▢ Nommez les quatre parties d'une instruction claire de cette leçon et, pour le prompt « Write a product description. », dites lesquelles manquent.

<details markdown="1"><summary>Vérifier</summary>

Le contexte, la tâche, les contraintes et à quoi ressemble « terminé ». Le prompt n'a qu'une tâche, et vague. Il manque : à qui s'adresse la description et où elle apparaît, ses limites de longueur et de ton, et le critère qu'elle doit satisfaire.

</details>

2. ▢ Réécrivez « Don't write long answers. » pour qu'il dise au modèle ce qu'il doit faire à la place.

<details markdown="1"><summary>Vérifier</summary>

Par exemple : « Answer in two or three sentences. » Cela nomme le comportement souhaité et donne une limite mesurable, ce qui le rend aussi vérifiable. Une instruction négative dit ce qu'il faut éviter mais laisse le modèle deviner l'alternative.

</details>

3. ▢ Quelle réécriture de « Make this email better » est la plus claire ?

    - a) Improve this email so that it reads more professionally, clearly and persuasively overall
    - b) Rewrite this email for an upset customer in under 120 words, apologising first
    - c) Fix any problems in this email and make it sound good to the reader
    - d) Edit this email as an expert writer would, with attention to quality

<details markdown="1"><summary>Vérifier</summary>

**b)** Elle nomme le public, une limite de longueur et une exigence d'ordre, de sorte que quelqu'un d'autre pourrait vérifier le résultat. (a), (c) et (d) reformulent « mieux » avec d'autres mots sans dire ce que mieux veut dire.

</details>

4. ▢ Prédisez, puis exécutez. Choisissez une tâche que vous faites souvent, par exemple « Write a short bio. » Écrivez le prompt en cinq mots et envoyez-le. Prédisez trois choses que la réponse ratera pour votre usage, puis réécrivez le prompt avec les quatre parties et renvoyez-le. Lesquelles de vos trois prédictions ont été corrigées, et quels problèmes sont apparus que vous n'aviez pas prédits ?

<details markdown="1"><summary>Indice</summary>

Donnez d'abord le prompt de cinq mots à un collègue. Tout ce qu'il vous demanderait est ce que le modèle devine.

</details>

<details markdown="1"><summary>Vérifier</summary>

Résultats typiques : la première réponse devine le public, la longueur et le ton. La seconde supprime ces suppositions mais peut ajouter un nouveau problème, souvent une contrainte qui entre en conflit avec une autre. Gardez les deux réponses : la différence entre elles est la première comparaison que vous pouvez montrer à quelqu'un, et la leçon 18 transforme cette habitude en jeu de régression.

</details>

## Exercices en situation réelle

- [ ] Prenez un prompt que vous avez envoyé cette semaine et qui a donné une réponse décevante, et notez lesquels parmi le contexte, la tâche, les contraintes et « à quoi ressemble terminé » lui manquaient.
- [ ] Donnez un prompt que vous avez écrit à un collègue sans aucune connaissance préalable et demandez-lui ce qu'il aurait dû deviner. Ajoutez une ligne pour chaque supposition.
- [ ] Demain : remplacez un « ne pas » d'un prompt que vous utilisez par une instruction positive et comparez les réponses sur la même entrée.

## Pour aller plus loin

- [Doc : "Prompt design strategies", Gemini API, Google](https://ai.google.dev/gemini-api/docs/prompting-strategies) : les recommandations d'un second éditeur sur les contraintes et le format de réponse.
- [Anatomie d'un prompt](../reference/prompt-anatomy.md)
- [Ressources](../RESOURCES.md)

---

Ça ne passe pas ? Relisez la source primaire en haut de page, car cette leçon la condense et c'est dans la condensation que la compréhension s'échappe. Consultez le [glossaire](../GLOSSARY.md) pour tout terme qui vous a paru glissant.

Si c'est la leçon elle-même qui n'est pas claire plutôt que la matière, c'est un défaut : [ouvrez une issue](https://github.com/TokenCemetery/teach/issues).
