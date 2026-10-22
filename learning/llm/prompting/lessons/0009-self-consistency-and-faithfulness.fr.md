---
title: "9. Self-consistency et fidélité"
description: "Échantillonner plusieurs chemins de raisonnement pour voter sur une réponse, et pourquoi le raisonnement écrit n'est pas une explication fidèle"
type: lesson
---

# Leçon 9. Self-consistency et fidélité

**Lien avec la mission :** Deux choses découlent du fait de demander du raisonnement : vous pouvez dépenser plus de tokens pour obtenir une réponse plus stable, et vous ne devez pas lire le raisonnement comme la preuve de la raison pour laquelle le modèle a répondu ainsi.
**Source primaire :** [Article : "Self-Consistency Improves Chain of Thought Reasoning in Language Models", Wang et al., 2022](https://arxiv.org/abs/2203.11171)
**Prérequis :** [Leçon 8](0008-chain-of-thought.md), [Self-consistency](../GLOSSARY.md), [Chain-of-thought](../GLOSSARY.md)

## Échauffement

1. ▢ La leçon 7 disait qu'un prompt few-shot peut pencher vers une réponse selon ses exemples et leur ordre. Pourquoi cela rend-il une réponse échantillonnée unique moins fiable qu'elle n'en a l'air ?

<details markdown="1"><summary>Vérifier</summary>

Une réponse est un tirage unique dans une distribution que le prompt a déjà inclinée. Si cette inclinaison décide du résultat sur un cas limite, relancer ou réordonner peut le faire basculer : une réponse isolée n'apporte donc aucune information sur sa propre fragilité.

</details>

2. ▢ La leçon 8 disait que le raisonnement aide surtout sur les tâches en plusieurs étapes. Nommez une tâche de votre travail où il aiderait et une où il n'aiderait pas.

<details markdown="1"><summary>Vérifier</summary>

Toute paire qui oppose plusieurs étapes dépendantes (un calcul en plusieurs parties, un planning avec contraintes) à une recherche ou un label en une étape (extraire une date, étiqueter le sentiment). La première mérite des tokens de raisonnement ; la seconde ne fait que les payer.

</details>

## À savoir

### Self-consistency : échantillonner, puis voter

Le décodage glouton prend une seule chaîne de raisonnement et lui fait confiance. Wang et al. échantillonnent à la place un ensemble de chemins de raisonnement à partir du même prompt et retiennent la réponse finale qui apparaît le plus souvent. L'intuition qu'ils donnent est qu'un problème difficile admet de nombreuses façons de réfléchir et une seule bonne réponse, donc les mauvais chemins tendent à diverger entre eux tandis que les bons convergent. Ils rapportent des gains par rapport au chain-of-thought glouton de +17,9 % sur GSM8K, +11,0 % sur SVAMP, +12,2 % sur AQuA, +6,4 % sur StrategyQA et +3,9 % sur ARC-challenge.

C'est la **self-consistency**. Trois conditions découlent de son fonctionnement :

- **Il doit y avoir une réponse finale à comparer.** Le vote porte sur des réponses tirées d'un ensemble fixe, comme un nombre ou un choix, donc il convient aux tâches à réponse unique vérifiable, pas à l'écriture libre.
- **Les échantillons doivent différer.** La méthode de l'article fonctionne avec des méthodes d'échantillonnage comme l'échantillonnage par température. Des échantillons identiques votent tous pareil et n'apportent rien.
- **Cela coûte plus cher.** Les auteurs citent le calcul supplémentaire comme la limite et suggèrent de commencer avec 5 ou 10 chemins, puisque dans la plupart des cas la performance sature vite.

Dans une fenêtre de chat, vous pouvez l'approcher en posant la même question dans plusieurs chats neufs et en prenant la majorité, à condition que l'interface échantillonne avec un peu d'aléa.

### Fidélité : le raisonnement n'est pas la cause

Il est tentant de lire le raisonnement écrit comme le processus réel du modèle. Turpin et al. l'ont testé en ajoutant au prompt un facteur de biais, comme réordonner les exemples few-shot pour que la bonne réponse soit toujours « (A) », ou suggérer une réponse dans le prompt, puis en vérifiant si le raisonnement écrit le mentionnait.

Ce n'était pas le cas. Sur 13 tâches BIG-Bench Hard avec GPT-3.5 et Claude 1.0, les facteurs de biais ont fait baisser la précision jusqu'à 36 %, et le raisonnement ne faisait jamais référence au facteur. Quand les modèles étaient poussés vers une mauvaise réponse, ils écrivaient souvent un raisonnement qui la justifiait. Les auteurs qualifient ces explications de plausibles mais trompeuses.

Deux règles pratiques en découlent :

- **N'utilisez pas le raisonnement écrit comme un audit de la raison pour laquelle la réponse a été donnée.** Ce peut être un récit fluide qui omet ce qui a motivé la réponse.
- **Testez l'influence directement.** Pour savoir si un élément du prompt affecte la réponse, changez cet élément et relancez, comme dans les articles, au lieu de demander au modèle de s'expliquer.

Cela ne rend pas le raisonnement inutile. Les gains de la leçon 8 tiennent toujours. Cela signifie que le raisonnement aide la réponse et qu'il est un témoin faible de la cause.

## Pratique

1. ▢ Prédisez, puis exécutez. Posez cette question à un modèle de chat dans trois chats neufs distincts et notez les trois réponses finales. Prédisez si une majorité se dégage.

    ```text
    A bat and a ball cost 1.10 dollars together. The bat costs 1.00
    dollar more than the ball. How much does the ball cost?
    Think it through, then end with "Answer:" and the amount.
    ```

<details markdown="1"><summary>Indice</summary>

La self-consistency n'aide que si les chemins diffèrent et si la réponse la plus fréquente est la bonne.

</details>

<details markdown="1"><summary>Vérifier</summary>

La bonne réponse est 5 cents. Si les trois chats s'accordent, le vote est unanime et les échantillons supplémentaires n'ont fait qu'augmenter votre confiance. Si l'un diverge, la majorité est votre réponse, et le désaccord montre que la question n'était pas sûre à trancher à partir d'un seul échantillon. Une mauvaise majorité est aussi possible, ce qui explique que le vote soit une façon de dépenser des tokens pour de la stabilité, pas une garantie. Essayez une question plus difficile en plusieurs étapes pour voir plus souvent des désaccords.

</details>

2. ▢ Pourquoi la self-consistency convient-elle mieux à « quel est 17 pour cent de 240 » qu'à « écrire une description de produit » ?

<details markdown="1"><summary>Vérifier</summary>

Le vote a besoin de réponses finales comparables par égalité. Un nombre l'est, donc le plus fréquent l'emporte. Une description de produit n'a pas de réponse unique : chaque échantillon est différent, donc il n'y a rien sur quoi voter, seulement du texte entre lequel choisir.

</details>

3. ▢ Votre application demande à un modèle une décision oui ou non et montre son raisonnement écrit à l'utilisateur comme explication. En vous appuyant sur Turpin et al., énoncez le risque et un changement.

<details markdown="1"><summary>Vérifier</summary>

Le risque est que le raisonnement peut omettre ce qui a réellement motivé la décision, ou rationaliser une décision façonnée par un élément du prompt comme l'ordre des exemples ou une réponse suggérée, de sorte que les utilisateurs verraient un récit plausible qui n'est peut-être pas la cause. Un changement : cesser de présenter le raisonnement écrit comme la cause et l'étiqueter comme la justification du modèle, ou tester directement en relançant avec l'entrée suspecte modifiée. Le bon correctif dépend de ce pour quoi les utilisateurs s'appuient sur l'explication.

</details>

4. ▢ Quelle paire décrit correctement ce que chaque technique vous apporte ?

    - a) La self-consistency apporte une réponse plus stable ; les vérifications de fidélité ne s'appliquent pas
    - b) La self-consistency apporte une réponse plus stable ; le raisonnement peut omettre la vraie cause
    - c) La self-consistency explique la réponse ; le raisonnement nomme toujours sa vraie cause
    - d) La self-consistency réduit le coût en n'échantillonnant qu'une fois ; le raisonnement peut omettre la cause

<details markdown="1"><summary>Vérifier</summary>

**b)** Voter sur des chemins échantillonnés stabilise la réponse finale, et Turpin et al. montrent que le raisonnement écrit peut omettre ce qui l'a motivée. (a) est faux parce que la fidélité s'applique à tout raisonnement que vous montrez. (c) est faux deux fois : voter n'explique pas, et le raisonnement ne nomme pas toujours sa cause. (d) est faux parce que la self-consistency coûte plus d'échantillons, pas moins.

</details>

## Exercices en situation réelle

- [ ] Prenez une question qui vous importe et qui a une réponse unique vérifiable. Posez-la dans trois chats neufs et notez si les réponses concordent.
- [ ] Trouvez un endroit où vous avez lu le raisonnement d'un modèle comme la raison de sa réponse, et écrivez ce que vous testeriez pour le vérifier.
- [ ] Demain : prenez un prompt à choix multiples et réordonnez ses options pour que la bonne se déplace, puis regardez si le raisonnement du modèle mentionne le changement.

## Pour aller plus loin

- [Few-shot et raisonnement](../reference/few-shot-and-reasoning.md)
- [Article : "Language Models Don't Always Say What They Think", Turpin et al., 2023](https://arxiv.org/abs/2305.04388)
- [Ressources](../RESOURCES.md)

---

Ça ne passe pas ? Relisez la source primaire en haut de page, car cette leçon la condense et c'est dans la condensation que la compréhension s'échappe. Consultez le [glossaire](../GLOSSARY.md) pour tout terme qui vous a paru glissant.

Si c'est la leçon elle-même qui n'est pas claire plutôt que la matière, c'est un défaut : [ouvrez une issue](https://github.com/TokenCemetery/teach/issues).
