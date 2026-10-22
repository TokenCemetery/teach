---
title: "33. Amplification de tokens et coût par tâche terminée"
description: "Pourquoi les systèmes agentiques consomment bien plus de tokens par tâche terminée qu'un prompt unique, et comment le budgéter"
type: lesson
---

# Leçon 33. Amplification de tokens et coût par tâche terminée

**Lien avec la mission :** Budgéter le coût en tokens et la latence d'une boucle agentique, et dire de quelle partie de la boucle vient l'amplification.
**Source primaire :** [Billet : "How We Built Our Multi-Agent Research System", Anthropic Engineering](https://www.anthropic.com/engineering/multi-agent-research-system)
**Prérequis :** [Leçon 32](0032-least-privilege-and-the-confused-deputy.md), [Trajectoire](../GLOSSARY.md)

## Échauffement

1. ▢ Dans la leçon 10, vous avez appris que le transcript grandit à chaque tour de la boucle d'agent. Pourquoi cela crée-t-il un coût qui se cumule sur une trajectoire ?

<details markdown="1"><summary>Vérifier</summary>

Le transcript entier est envoyé au modèle à chaque tour de boucle. Une trajectoire de 30 tours signifie que le contenu du premier tour est envoyé 30 fois au modèle, celui du deuxième tour 29 fois, et ainsi de suite. Le coût en tokens d'une longue trajectoire n'est pas seulement la somme des tours ; c'est la somme de toutes les retransmissions répétées des anciens tours.

</details>

2. ▢ Depuis la leçon 19, rappelez-vous : quand un orchestrateur lance trois workers en parallèle, combien de boucles d'agent s'exécutent au total par rapport à un agent unique qui résout le même problème ?

<details markdown="1"><summary>Vérifier</summary>

Trois boucles d'agent distinctes s'exécutent, une dans chaque worker, plus la boucle propre de l'orchestrateur. Le total est donc d'au moins trois exécutions d'agent complètes plus le coût de l'orchestrateur, alors qu'un agent unique qui résout le même problème est une seule exécution. Le coût en tokens est multiplié, et non divisé, par le parallélisme.

</details>

## À savoir

### Les quatre sources d'amplification de tokens

Un système agentique consomme bien plus de tokens par tâche terminée qu'un prompt unique bien informé. Cela vient de quatre facteurs qui se cumulent. Nous en avons déjà nommé trois dans des leçons précédentes ; cette leçon les rassemble et ajoute le quatrième.

### Source 1 : la recroissance du transcript (leçon 10)

Chaque tour de boucle ajoute au transcript. Au tour suivant, le transcript entier est renvoyé au modèle. Cela signifie qu'une trajectoire de 50 tours paie cinquante fois le coût en tokens du tour 1, quarante-neuf fois celui du tour 2, et ainsi de suite. Le total est à peu près la moitié de la somme : 1 + 2 + 3 + ... + 50 = 1 275, donc chaque tour est payé en moyenne 25,5 fois. Un prompt simple envoyé une fois coûte X tokens. Le même problème résolu par un agent de 50 tours ne coûte pas 50X (si chaque tour était indépendant), mais quelque chose de plus proche de 1 275X en transmission brute de tokens, même si chaque tour pris individuellement coûte moins que X parce que le modèle est étroitement ciblé.

Le billet « Building Effective Agents » d'Anthropic note que cette recroissance est le plus gros multiplicateur de coût sur les agents de longue durée, et c'est pourquoi la leçon 11 (compaction et récupération) existe comme défense contre elle.

### Source 2 : la duplication multi-agent (leçon 19)

Si vous décomposez un problème en sous-tâches et lancez trois workers en parallèle (le fan-out de la leçon 18), vous payez le coût complet de recroissance du transcript non pas une fois, mais trois fois. Chaque worker a sa propre trajectoire de 50 tours, donc chacun paie 1 275X. L'orchestrateur exécute aussi sa propre boucle. Le coût de coordination multiplie le coût global en tokens. Si votre agent unique avait coûté 50 000 tokens, trois workers à un coût un peu plus bas chacun pourraient totaliser 130 000 tokens ou plus.

### Source 3 : la réflexion et les nouveaux essais (leçon 17)

Si une première tentative sur une tâche échoue et que le harness génère une réflexion puis relance l'agent, vous avez maintenant deux trajectoires complètes au lieu d'une. Une tâche qui demande trois tentatives (un échec, une réflexion, une réussite) coûte à peu près trois fois ce que coûterait une tentative unique réussie, parce que chaque tentative est une exécution d'agent complète avec sa propre recroissance du transcript. La leçon 17 enseigne que la réflexion ne vaut ce coût que si le signal d'échec est clair et si une deuxième tentative a de bonnes chances de réussir.

### Source 4 : les définitions d'outils renvoyées à chaque tour (nouveau dans cette leçon)

Le system prompt et les définitions d'outils font partie du contexte envoyé au modèle à chaque tour de boucle. Les définitions d'outils sont généralement volumineuses : chaque outil a un nom, une description lisible par un humain (issue du travail de nommage de la leçon 8), des types de paramètres, des contraintes et des exemples. Si vous avez dix outils avec 200 tokens de description chacun, cela fait 2 000 tokens de définitions d'outils. Sur une trajectoire de 50 tours, cela fait 2 000 * 50 = 100 000 tokens dépensés à renvoyer les mêmes définitions d'outils, alors qu'elles n'ont jamais changé en cours d'exécution.

Ce coût est distinct de la recroissance du transcript (source 1) parce que les définitions d'outils ne changent pas ; elles forment un préfixe stable et répété. C'est exactement le problème que traite la leçon 34 (prompt caching).

### La bonne unité de budget : le coût par tâche terminée

La plupart des discussions de coût se concentrent sur le « coût par appel d'API » ou le « coût par invocation du modèle ». Mais la bonne unité pour un système agentique est le « coût par tâche terminée », c'est-à-dire la somme complète de toutes les tentatives, tous les nouveaux essais, tous les workers, tous les tours, jusqu'à ce que la tâche soit faite.

Une tâche qu'un prompt unique pourrait résoudre en 5 000 tokens peut coûter 50 000 tokens ou plus dans un système agentique si :

- Le problème prend 20 tours à résoudre (multiplicateur de recroissance : environ 200 fois le coût d'un seul tour)
- La première tentative échoue et un nouvel essai fondé sur la réflexion réussit (multiplier par 2)
- La tâche est découpée en trois workers parallèles (multiplier par 3)
- Les définitions d'outils sont volumineuses et renvoyées à chaque tour (ajouter 10 000 tokens de gaspillage)

Le calcul est approximatif, mais le principe est réel : 5 000 tokens de base peuvent devenir 50 000 à 150 000 tokens en pratique, parce que vous ne payez pas pour un appel ; vous payez pour l'achèvement d'une tâche, qui implique de nombreux appels, de nombreux allers-retours et de nombreux contextes répétés.

### Pourquoi « coût par tâche terminée » change vos décisions de conception

Quand vous raisonnez en coût par appel d'API, un agent de longue durée semble cher à cause du simple nombre d'appels. Quand vous raisonnez en coût par tâche terminée, la question change : un système multi-agent résout-il le problème plus vite en temps réel ou plus fiablement, d'une manière qui justifie le multiplicateur de tokens ? La réflexion réduit-elle le nombre de tâches en échec, d'une manière qui justifie le coût des nouveaux essais ? La décomposition simplifie-t-elle assez le problème pour que chaque worker utilise moins de tokens par tâche que l'agent unique ne l'aurait fait ?

Ce sont les vraies questions de compromis. Le budget par tâche rend le compromis visible.

### Exemple illustratif : déboguer une défaillance de code

Supposons que votre tâche soit de déboguer un test en échec. Un humain bien informé pourrait écrire un prompt : « Voici le test, voici la sortie d'erreur. Trouve le bug. » Ce prompt et sa réponse pourraient coûter 10 000 tokens au total.

Supposons maintenant que vous construisiez plutôt une boucle d'agent :

- L'agent lit le test (1 000 tokens), lit le code (2 000 tokens), raisonne sur l'erreur (500 tokens) = 3 500 tokens au tour 1. Renvoyer ces 3 500 tokens plus les définitions d'outils (2 000 tokens) au tour 2 = 5 500 tokens. Après 10 tours de débogage, vous avez dépensé environ 3 500 \* 10 + (définitions d'outils \* 10) = 55 000 tokens, parce que chaque tour renvoie le test, le code et les définitions d'outils.
- La première tentative de l'agent devine la mauvaise cause racine. Le harness génère une réflexion et relance l'agent. Vous avez maintenant deux exécutions complètes de 10 tours, donc environ 110 000 tokens, pas 55 000.
- La deuxième tentative réussit.

Coût par tâche terminée : 110 000 tokens. Coût par appel d'API réussi : 5 500 tokens (seulement le dernier appel réussi). Ces nombres racontent des histoires différentes. Budgéter par tâche terminée est plus honnête.

La solution n'est pas d'éviter les agents ; la solution est d'utiliser le prompt caching de la leçon 34 pour éviter de renvoyer les définitions d'outils, de concevoir la planification de la leçon 16 pour réduire le nombre de tours, et de n'utiliser la réflexion de la leçon 17 que lorsque les signaux d'échec sont clairs.

## Pratique

1. ▢ Un prompt à un seul tour envoyé à un modèle coûte 5 000 tokens et résout parfaitement un problème. Une boucle d'agent sur le même problème prend 25 tours, et le coût de recroissance du transcript fait que chaque token des premiers tours est payé environ 20 fois en moyenne. À peu près combien de tokens la boucle d'agent coûte-t-elle au total ?

<details markdown="1"><summary>Vérifier</summary>

À peu près 5 000 * 20 = 100 000 tokens. Le multiplicateur de recroissance est le facteur le plus important. (C'est une estimation illustrative ; le nombre exact dépend de la répartition des tokens entre les tours, mais l'ordre de grandeur est le bon.)

</details>

2. ▢ Vous construisez un agent qui résume des articles de recherche. Les définitions d'outils de l'agent totalisent 3 000 tokens. Sur une exécution, l'agent examine 10 articles et produit 10 résumés, en 40 tours au total. Les définitions d'outils ne changent jamais pendant l'exécution. Combien de tokens sont dépensés à renvoyer les définitions d'outils, et pourquoi ce gaspillage peut-il être traité par la leçon 34 ?

<details markdown="1"><summary>Indice</summary>

Comptez combien de fois les définitions d'outils sont envoyées au modèle. Puis demandez-vous quelle partie du contexte est stable et ne change jamais en cours d'exécution.

</details>

<details markdown="1"><summary>Vérifier</summary>

Les définitions d'outils sont envoyées 40 fois (une fois par tour), donc 3 000 * 40 = 120 000 tokens dépensés à renvoyer exactement les mêmes définitions. C'est du gaspillage parce que les définitions ne changent jamais ; elles forment un préfixe stable. La leçon 34 enseigne le prompt caching, qui met en cache exactement ce genre de préfixe stable et ne le facture qu'une fois, pas 40.

</details>

3. ▢ Une tâche demande trois tentatives. La première échoue, une réflexion est générée, la deuxième échoue, une autre réflexion est générée, et la troisième réussit. Chaque tentative est une exécution d'agent complète de 15 tours. L'orchestrateur qui coordonne les trois tentatives coûte 5 tours. À peu près combien de tours fait la trajectoire au total ?

    - a) 15 tours (seule la tentative réussie compte)
    - b) 35 tours (15 + 15 + 5)
    - c) 50 tours (15 + 15 + 15 + 5)
    - d) 150 tours (les trois tentatives multipliées par la surcharge de l'orchestrateur)

<details markdown="1"><summary>Vérifier</summary>

**c)** Les trois tentatives vont jusqu'au bout, donc 15 + 15 + 15 = 45 tours, plus 5 tours d'orchestration = 50 tours. L'option a est fausse parce que les échecs consomment quand même des tours complets. L'option b oublie la deuxième tentative échouée. L'option d se trompe en multipliant au lieu d'additionner. La trajectoire inclut chaque tour de chaque tentative, pas seulement ceux de la tentative réussie.

</details>

4. ▢ Vous hésitez entre un agent unique et un fan-out de trois workers pour une tâche de recherche. L'agent unique prendrait 60 tours et coûterait environ 100 000 tokens. Chaque worker prendrait 25 tours et coûterait environ 35 000 tokens, plus l'orchestrateur prend 10 tours et coûte 3 000 tokens. Quel est le coût total en tokens du système multi-agent, et est-il moins cher que l'agent unique ?

<details markdown="1"><summary>Vérifier</summary>

Total : (35 000 * 3) + 3 000 = 108 000 tokens. Le système multi-agent est en réalité un peu plus cher en tokens (108 000 contre 100 000) alors même que chaque worker est plus efficace. C'est le coût de coordination de la leçon 19. Le système multi-agent gagne sur le temps réel (les trois workers s'exécutent en parallèle, donc c'est le plus lent qui détermine le temps, pas la somme), pas sur les tokens. Cela montre pourquoi le budget par tâche est important : si vous avez besoin de vitesse, le multi-agent gagne ; si vous avez besoin d'économiser des tokens, l'agent unique gagne.

</details>

## Exercices en situation réelle

- [ ] Prenez une tâche que vous avez faite avec un agent (ou une trajectoire que vous avez vue). Parcourez une itération de boucle de cet agent et comptez les tokens : taille du transcript, taille des définitions d'outils, taille de la sortie du modèle. Multipliez par le nombre de tours. Estimez maintenant ce qu'aurait coûté un seul prompt bien informé au modèle, et comparez les deux nombres. Notez le multiplicateur.
- [ ] Concevez une petite tâche d'agent (quelque chose que vous pourriez exécuter vous-même). Estimez le coût par tâche terminée en devinant : nombre de tours nécessaires, nombre de nouveaux essais, éventuels workers en fan-out. Additionnez le budget complet avec la formule (facteur_de_recroissance_du_transcript) \* (nombre_de_tentatives) \* (nombre_de_workers) \* (tokens_par_tour).
- [ ] Demain : trouvez ou générez la trajectoire d'une exécution d'agent (au moins 10 tours). Calculez le coût par tâche en tokens en additionnant tous les coûts en tokens sur tous les tours et toutes les tentatives. Trouvez ensuite le coût par appel d'API réussi (seulement le dernier tour réussi). Notez de combien le coût par tâche dépasse le coût par appel réussi, et expliquez pourquoi cet écart compte pour le budget.

## Pour aller plus loin

- [Billet : "How We Built Our Multi-Agent Research System", Anthropic Engineering](https://www.anthropic.com/engineering/multi-agent-research-system)
- [Ressources](../RESOURCES.md)

---

Ça ne passe pas ? Relisez la source primaire en haut de page, car cette leçon la condense et c'est dans la condensation que la compréhension s'échappe. Consultez le [glossaire](../GLOSSARY.md) pour tout terme qui vous a paru glissant.

Si c'est la leçon elle-même qui n'est pas claire plutôt que la matière, c'est un défaut : [ouvrez une issue](https://github.com/TokenCemetery/teach/issues).
