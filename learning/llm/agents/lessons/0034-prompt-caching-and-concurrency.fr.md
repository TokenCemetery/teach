---
title: "34. Prompt caching et concurrence"
description: "Comment le caching réduit le coût en tokens par tâche et comment la concurrence augmente le débit, et pourquoi les confondre est une erreur de budget"
type: lesson
---

# Leçon 34. Prompt caching et concurrence

**Lien avec la mission :** Budgéter le coût en tokens et la latence d'une boucle agentique, et dire de quelle partie de la boucle vient l'amplification.
**Source primaire :** [Doc : "Prompt caching", Claude Platform Docs](https://platform.claude.com/docs/en/build-with-claude/prompt-caching)
**Prérequis :** [Leçon 33](0033-token-amplification-and-cost.md)

## Échauffement

1. ▢ Depuis la leçon 33, vous avez appris que les définitions d'outils sont renvoyées au modèle à chaque tour de boucle, en consommant des tokens alors qu'elles ne changent jamais. De quelle partie du contexte s'agit-il, et pourquoi le caching aiderait-il ?

<details markdown="1"><summary>Vérifier</summary>

Les définitions d'outils sont un préfixe stable de chaque message envoyé au modèle : elles ne changent pas en cours d'exécution. Le caching aide parce qu'un cache stocke ce préfixe stable après la première requête et le réutilise lors des requêtes suivantes de la même trajectoire, en ne facturant que le contenu nouveau qui lui est ajouté.

</details>

2. ▢ Depuis la leçon 19, rappelez-vous : exécuter trois agents en parallèle réduit-il le coût en tokens de la résolution d'un problème par rapport à l'exécution d'un seul agent en série ?

<details markdown="1"><summary>Vérifier</summary>

Non. Exécuter trois agents en parallèle augmente le coût total en tokens parce que chaque agent paie son coût complet indépendamment. Le parallélisme réduit le temps réel mais pas le coût en tokens. Chaque agent parallèle doit toujours lire la tâche, exécuter sa boucle et transmettre son transcript au modèle.

</details>

## À savoir

### Comment fonctionne le prompt caching

Le prompt caching est un mécanisme qui stocke un préfixe stable d'une requête après le premier appel et le réutilise lors des appels suivants sans le facturer de nouveau plein tarif. Le cache est propre à une séquence de requêtes ; les requêtes de différents utilisateurs ou de différentes exécutions d'agents ne partagent pas de cache.

Voici la mécanique :

1. Au premier message d'une trajectoire, vous envoyez une requête complète : system prompt, définitions d'outils et tâche.
2. Le modèle la traite normalement et facture le coût complet en tokens.
3. La réponse inclut des métadonnées : « Cached 4,000 tokens » (ou quelle que soit la taille du préfixe stable).
4. Au deuxième message de la même trajectoire, vous ajoutez du contenu nouveau à la requête : peut-être un résultat d'outil, l'instruction suivante ou un tour de suivi.
5. Le modèle réutilise le préfixe en cache (system prompt, outils, tâche) et ne facture que le contenu nouvellement ajouté.
6. Cela se répète : chaque nouveau tour de la même trajectoire ne paie que ce qui a changé depuis le tour précédent.

Le cache a un coût : le premier tour paie plein tarif, et il y a une petite surcharge pour les consultations et le stockage du cache. Mais sur une longue trajectoire, cette surcharge se justifie aisément. Si vous avez 30 tours et que les définitions d'outils font 2 000 tokens, le cache économise environ 2 000 * 28 = 56 000 tokens (les définitions ne sont pas renvoyées aux tours 2 à 29, donc vous économisez leur coût 28 fois).

### Ce qui invalide un cache

Un cache n'est utile que si le préfixe est réellement stable. Plusieurs choses invalident un cache en silence, ce qui compte pour la conception du harness :

**Réordonner les définitions d'outils.** Si vous sérialisez votre liste d'outils différemment au tour 1 et au tour 2 (par exemple par ordre alphabétique au tour 1, par fréquence au tour 2), le préfixe ne correspond plus et le cache est invalide. Un harness doit toujours sérialiser les outils dans le même ordre, à chaque tour.

**Interpoler des valeurs dynamiques dans le system prompt.** Si votre system prompt inclut un horodatage (« Current time: 2024-09-13 »), un identifiant d'utilisateur ou n'importe quelle valeur propre à l'appel, cette valeur change d'un tour à l'autre et le préfixe n'est plus stable. Le cache est invalide à chaque tour. Cela défait entièrement le caching. Si vous avez besoin de valeurs dynamiques, placez-les après les outils (dans la partie non mise en cache de la requête).

**Modifier des messages antérieurs.** Si un harness modifie en place d'anciens messages (par opposition à un ajout pur), le cache est invalidé à partir du point de modification. La leçon 7 a enseigné que le transcript est l'état de l'agent ; cette philosophie plaide pour l'ajout pur et pour ne jamais toucher aux anciens messages. Le prompt caching renforce cela : toute modification brise le cache.

### Le caching résout le coût des « définitions d'outils renvoyées à chaque tour » de la leçon 33

La documentation source « Prompt caching » note que les définitions d'outils et les system prompts sont exactement le genre de contenu stable, volumineux et répété pour lequel le caching est conçu. Un harness à 10 outils avec 2 000 tokens de descriptions d'outils ne paie désormais ces 2 000 tokens qu'une fois par trajectoire, et non une fois par tour. Sur une trajectoire de 50 tours, cela seul économise environ 98 000 tokens (les définitions apparaissent 50 fois sans caching, 1 fois avec caching, donc 49 * 2 000 = 98 000 tokens économisés).

C'est pourquoi la leçon 33 et la leçon 34 vont de pair : la leçon 33 repère le gaspillage, la leçon 34 nomme le remède.

### La concurrence : un levier distinct et complémentaire

Le prompt caching réduit le coût de toute exécution d'agent isolée. La concurrence est une question distincte : exécuter plusieurs instances d'agent en parallèle.

La concurrence peut prendre plusieurs formes :

- Exécuter la même tâche sur la même entrée avec plusieurs agents en parallèle, pour voir s'ils produisent des réponses différentes (utile pour les tâches où plusieurs solutions valides existent).
- Exécuter des variantes d'une tâche en parallèle (le fan-out de la leçon 19), où chaque agent résout une sous-tâche.
- Exécuter plusieurs tâches d'utilisateurs indépendantes en parallèle (un système qui sert de nombreux utilisateurs, chacun avec sa propre instance d'agent).

Dans chaque cas, la concurrence augmente le débit : davantage de tâches se terminent par unité de temps réel. Mais la concurrence ne réduit PAS le coût en tokens d'une tâche isolée. Si vous exécutez trois agents en parallèle et que chacun coûte 100 000 tokens, le total est de 300 000 tokens, pas 100 000 divisé par 3. Le parallélisme échange du temps contre des tokens.

### L'erreur : confondre caching et concurrence

Une erreur de budget courante est de supposer qu'exécuter plusieurs agents en parallèle rend d'une façon ou d'une autre chacun moins cher en tokens. Ce n'est pas le cas. Voici la confusion :

- Correct : le caching réduit le coût en tokens de la longue trajectoire d'un seul agent en évitant de renvoyer des préfixes stables.
- Correct : la concurrence réduit le temps réel en exécutant des agents en parallèle.
- Incorrect : « Nous exécutons les agents en concurrence, donc le coût en tokens par agent est plus bas. »

La concurrence réduit le temps, pas les tokens. Exécuter les agents plus vite (en parallèle) ne les rend pas moins chers (en tokens). Si vous devez réduire le coût et que vous avez déjà le caching, les leviers sont :

- Une meilleure planification (leçon 16) pour réduire le nombre de tours.
- Une meilleure récupération (leçon 11) pour réduire la taille du transcript.
- Moins de workers (leçon 19) pour réduire la duplication multi-agent.
- Échouer plus vite (diagnostic de la leçon 29) pour réduire les tentatives gaspillées.

### Budget de tokens : deux questions

Quand vous concevez un système agentique, posez deux questions distinctes :

1. **Coût par tâche terminée :** combien de tokens un agent aura-t-il besoin pour résoudre une tâche de façon fiable ? C'est là que le caching aide, que la planification aide, et que la réflexion coûte.
2. **Débit :** combien de tâches devez-vous terminer par seconde ou par minute ? C'est là que la concurrence aide. Si vous avez besoin de 10 tâches par seconde et que chaque tâche prend 1 seconde à terminer en série, il vous faut au moins 10 agents qui s'exécutent en parallèle.

Confondre ces questions mène à de mauvaises décisions. Si vous essayez de réduire le coût par tâche, ajouter davantage d'agents concurrents n'aide pas. Si vous essayez d'augmenter le débit et que vous avez une échéance, ajouter de la concurrence est le bon levier (mais vous payez en tokens totaux : 10 agents * coût par tâche = budget total).

## Pratique

1. ▢ Le system prompt et les définitions d'outils de votre agent totalisent 5 000 tokens. L'agent s'exécute pendant 30 tours sur une seule tâche. Sans prompt caching, combien de fois ces 5 000 tokens sont-ils envoyés au modèle ? Avec le caching, combien de fois ?

<details markdown="1"><summary>Vérifier</summary>

Sans caching : 30 fois (une fois par tour), soit un total de 150 000 tokens de surcharge de définitions. Avec le caching : une fois au premier tour, puis réutilisés à tous les tours suivants, donc effectivement une fois. (Plus précisément, il y a une petite surcharge pour récupérer le cache à chaque tour, mais les 5 000 tokens complets ne sont pas retransmis.) Le caching économise environ 145 000 tokens dans ce cas.

</details>

2. ▢ Vous implémentez le prompt caching dans votre harness. La liste d'outils est générée dynamiquement : au tour 1, l'agent a accès aux outils A, B, C ; au tour 3, le harness ajoute l'outil D. Les outils sont sérialisés dans l'ordre où ils sont générés (A, B, C au tour 1 ; A, B, C, D au tour 3). Le cache du tour 1 sera-t-il encore valide au tour 3 ? Pourquoi, ou pourquoi pas ?

<details markdown="1"><summary>Indice</summary>

Qu'est-ce qui a changé entre la requête du tour 1 et celle du tour 3 ? Ce changement fait-il partie du préfixe en cache, ou vient-il après ?

</details>

<details markdown="1"><summary>Vérifier</summary>

Non, le cache est invalide. Au tour 1, le préfixe contient « tools: A, B, C ». Au tour 3, le préfixe contient « tools: A, B, C, D ». Les préfixes ne correspondent pas, donc le cache ne s'applique pas. Le harness doit renvoyer les définitions complètes. C'est pourquoi l'ajout dynamique d'outils (ajouter un outil en cours d'exécution selon les décisions de l'agent) brise le caching. Un harness qui veut du caching doit soit s'engager d'emblée sur un jeu d'outils fixe, soit accepter qu'ajouter des outils en cours d'exécution invalide le cache.

</details>

3. ▢ Vous concevez le system prompt d'un agent avec cache. Le prompt inclut « Current date: 2024-09-13 » pour situer le modèle dans le temps. Pourquoi est-ce un problème de caching ?

    - a) La date n'est pas pertinente pour le modèle et devrait être retirée.
    - b) La date change chaque jour, donc le préfixe en cache deviendrait périmé au bout d'un jour.
    - c) La date est une valeur dynamique qui change d'une exécution à l'autre, ce qui invalide le cache à chaque exécution parce que le préfixe ne correspond plus.
    - d) Les dates ne peuvent être mises en cache par aucun système.

<details markdown="1"><summary>Vérifier</summary>

**c)** Le system prompt fait partie du préfixe en cache. Si vous incluez une date écrite en dur qui diffère entre l'exécution 1 et l'exécution 2, le préfixe en cache de l'exécution 1 ne correspond pas à la requête de l'exécution 2, donc le cache est inutile. La solution est d'exclure la date du préfixe en cache (la placer après les outils, dans le contenu propre à chaque tour), ou d'utiliser une date fixe pour toutes les exécutions si la date n'est pas réellement critique. C'est une erreur courante : inclure des métadonnées propres à une exécution dans la partie mise en cache défait le caching.

</details>

4. ▢ Vous avez deux options pour faire passer votre système d'agents à l'échelle : l'option A consiste à optimiser le coût par tâche d'un agent via le caching et la planification, en le faisant passer de 100 000 tokens à 60 000 tokens. L'option B consiste à exécuter dix agents en parallèle sans optimisation, chacun coûtant toujours 100 000 tokens. Si vous devez terminer 10 tâches et que vous disposez de calcul illimité, quelle option minimise le coût en tokens ?

<details markdown="1"><summary>Vérifier</summary>

Option A : 10 tâches \* 60 000 tokens par tâche = 600 000 tokens au total. Option B : 10 tâches \* 100 000 tokens par tâche = 1 000 000 tokens au total, même si elles s'exécutent en parallèle. La concurrence augmente la vitesse (l'option B se termine dans le temps d'une tâche, alors que l'option A se termine en 10 fois cette durée en série) mais pas le coût. L'option A est moins chère en tokens. Si vous devez terminer 10 tâches aussi vite que possible, vous combineriez les deux : optimiser chaque agent à 60 000 tokens (l'approche de l'option A) et exécuter 10 agents optimisés en parallèle, pour un total de 600 000 tokens et le temps réel le plus court.

</details>

## Exercices en situation réelle

- [ ] Regardez un harness d'agent que vous avez écrit ou relu. Trouvez où le system prompt et les définitions d'outils sont sérialisés. Vérifiez qu'ils sont toujours sérialisés dans le même ordre, et qu'aucune valeur dynamique (horodatages, identifiants d'utilisateurs, métadonnées propres à l'exécution) n'est interpolée dans cette section. Si c'est le cas, notez comment cela brise le caching.
- [ ] Estimez les économies de tokens du prompt caching pour une tâche que vous connaissez. Devinez : taille du system prompt et des définitions d'outils, nombre de tours, tokens par tour. Calculez combien de tokens sont économisés en ne renvoyant pas les définitions. L'économie vaut-elle la complexité de la mise en œuvre du caching ?
- [ ] Demain : concevez une tâche qui bénéficie de la concurrence (soit plusieurs utilisateurs, soit plusieurs sous-tâches indépendantes, soit plusieurs tentatives de la même tâche). Estimez le budget total de tokens si vous exécutez les agents en série (un à la fois) par rapport à en parallèle. Montrez que les deux budgets sont identiques, et expliquez ce que vous gagnez et perdez avec chaque approche.

## Pour aller plus loin

- [Doc : "Prompt caching", Claude Platform Docs](https://platform.claude.com/docs/en/build-with-claude/prompt-caching)
- [Ressources](../RESOURCES.md)

---

Ça ne passe pas ? Relisez la source primaire en haut de page, car cette leçon la condense et c'est dans la condensation que la compréhension s'échappe. Consultez le [glossaire](../GLOSSARY.md) pour tout terme qui vous a paru glissant.

Si c'est la leçon elle-même qui n'est pas claire plutôt que la matière, c'est un défaut : [ouvrez une issue](https://github.com/TokenCemetery/teach/issues).
