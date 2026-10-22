---
title: "19. Le coût de coordination"
description: "Comprendre pourquoi construire plusieurs agents coûte plus cher qu'un seul agent bien équipé, et comment décider quand le gain de parallélisme vaut ce coût"
type: lesson
---

# Leçon 19. Le coût de coordination

**Lien avec la mission :** Pour choisir entre un agent unique bien équipé et un système multi-agent, il faut savoir ce que coûtent les systèmes orchestrateur et worker en tokens, en raisonnement et en contexte fragmenté, et comment juger si un second agent apporte quelque chose que le premier n'aurait pas pu recevoir directement.
**Source primaire :** [Billet : "Don't Build Multi-Agents", Cognition](https://cognition.ai/blog/dont-build-multi-agents)
**Prérequis :** [Leçon 18](0018-orchestrator-and-worker.md)

## Échauffement

1. ▢ Depuis la leçon 18, rappelez-vous : dans un système orchestrateur et worker, un worker peut-il voir la trajectoire de raisonnement complète d'un autre worker pendant que cet autre worker s'exécute ?

<details markdown="1"><summary>Vérifier</summary>

Non. Chaque worker exécute sa propre boucle d'agent avec son propre transcript isolé. Les workers ne voient les constats les uns des autres que si l'orchestrateur les leur transmet explicitement, et seulement les rapports finaux, pas le raisonnement complet. Cet isolement est un atout (il garde le contexte propre) et un coût (les workers ne peuvent pas partager d'intuitions en cours de tâche).

</details>

2. ▢ Depuis la leçon 18, rappelez-vous : quelle est la différence entre le fan-out et la passation ?

<details markdown="1"><summary>Vérifier</summary>

Le fan-out lance en parallèle plusieurs workers sur des variantes d'un même problème, en explorant différents angles à la fois pour une couverture plus large et du parallélisme. La passation est séquentielle : un agent termine sa tâche et transmet un contexte propre à un second agent spécialisé pour la phase suivante. Les deux sont des schémas multi-agents ; le fan-out joue sur le temps, la passation sur la spécialisation.

</details>

## À savoir

### Coût en tokens : plusieurs agents coûtent plusieurs fois plus

Chaque exécution d'agent a un coût. Un système orchestrateur et worker paie ce coût plusieurs fois.

Supposons qu'un agent unique résolve un problème en 10 000 tokens : disons 20 tours à 500 tokens par tour. Supposons maintenant que le même problème soit découpé en trois sous-tâches indépendantes, chacune résolue par un worker en 8 000 tokens (un peu moins, parce que chaque worker a un objectif plus étroit). L'orchestrateur lui-même utilise 2 000 tokens pour découper la tâche et synthétiser les résultats.

Coût total : 8 000 + 8 000 + 8 000 + 2 000 = 26 000 tokens. Le système multi-agent a coûté 2,6 fois ce qu'a coûté l'agent unique, alors même que chaque worker était un peu plus efficace que l'agent unique ne l'aurait été sur sa seule part. Les workers explorent en parallèle, donc le temps réel est plus court, mais le coût en tokens est multiplié.

Ce calcul empire si les workers travaillent de façon inefficace ou si l'orchestrateur doit coordonner plus d'une fois (par exemple l'orchestrateur réalise que les workers ont manqué une dépendance, lance de nouveaux workers ou demande aux workers de relancer avec de nouvelles instructions). L'article de Cognition signale cela comme la question centrale : le gain de vitesse du parallélisme vaut-il de payer plusieurs fois le coût en tokens ?

### Contexte fragmenté : les workers ne se voient pas

Quand un agent unique exécute une longue tâche, il accumule du contexte : il sait ce qu'il a essayé, ce qui a marché, ce qui n'a pas marché, et pourquoi. Un système multi-agent fragmente ce contexte. Les workers A et B peuvent explorer des terrains qui se recoupent (par exemple, tous deux essaient de comprendre une contrainte), mais le worker A ne voit pas le raisonnement du worker B sur cette contrainte ; il ne voit que le rapport final.

Concrètement : le worker A réalise en cours de tâche qu'une contrainte a une implication subtile. Le worker A raisonne dessus, se construit une intuition et fait son rapport. L'orchestrateur lit le rapport et le transmet au worker B. Le worker B connaît maintenant la conclusion mais pas le raisonnement qui y a mené. Le worker B ne peut ni affiner ni contester ce raisonnement en cours de tâche, parce qu'il ne voit pas la réflexion du worker A. Le worker B soit accepte le rapport et l'utilise (perdant l'occasion de l'affiner), soit l'ignore et redérive la même intuition (gaspillant des tokens).

Pour les tâches où la meilleure réponse émerge d'allers-retours d'affinage entre plusieurs lignes de raisonnement, le contexte fragmenté est une vraie limite. Un agent unique avec assez de tours peut garder tout son raisonnement au même endroit et intégrer les intuitions à mesure qu'elles se développent.

### Conclusions contradictoires : l'exploration indépendante mène au désaccord

Quand deux workers explorent le même terrain indépendamment, ils peuvent arriver à des conclusions différentes. Ce n'est pas forcément faux ; ils ont pu trouver des interprétations réellement différentes (et toutes deux valables). Mais cela peut aussi signifier qu'un worker a fait une erreur, ou a manqué quelque chose que l'autre a vu.

L'orchestrateur voit les deux rapports et doit les concilier. Si le conflit est sémantique ou factuel, l'orchestrateur a un problème : il n'a que les résumés des workers, pas leur raisonnement complet, donc il ne peut pas facilement retracer l'origine du désaccord. L'orchestrateur peut lancer un nouvel agent (un sous-agent « juge » ou « synthétiseur ») pour concilier, ce qui ajoute du coût.

L'alternative de l'agent unique évite cela : un agent unique qui parcourt le même terrain en série intègre chaque nouveau constat à son modèle mental courant, donc il peut repérer les contradictions au fur et à mesure et les résoudre dans sa propre boucle de raisonnement.

### Le principe de décision : quand le multi-agent est-il moins cher ?

La source primaire de Cognition soutient que la plupart des systèmes multi-agents ne sont pas moins chers, en tokens ou en qualité de raisonnement, qu'un agent unique doté de meilleurs outils. La question n'est pas « le parallélisme est-il plus rapide ? » (oui) mais « le parallélisme achète-t-il quelque chose qu'un agent unique n'aurait pas pu avoir pour moins cher ? »

Appliquez ce principe de décision :

**Le multi-agent a du sens quand :**

- Les sous-tâches sont réellement indépendantes (pas de contexte partagé, pas de dépendance aux résultats des autres en cours de tâche).
- Les sous-tâches sont chacune plus simples que la tâche d'origine (chaque worker résout un problème réellement plus étroit, de sorte que la somme des gains d'efficacité des workers l'emporte sur le coût de duplication).
- Vous avez besoin du gain de vitesse du parallélisme (le temps gagné justifie le multiplicateur de tokens ; vous avez une échéance en temps réel que vous ne pouvez pas tenir avec un agent et plus de tours).
- Les outils de chaque worker sont assez spécialisés pour qu'une suite d'outils partagée ralentisse chaque worker avec des options non pertinentes.

**Un agent unique avec plus de ressources l'emporte généralement quand :**

- Les sous-tâches partagent du contexte ou s'affinent mutuellement (un agent unique garde tout son raisonnement connecté ; un système multi-agent doit redériver ou recommuniquer).
- Vous avez de la marge dans le budget de contexte (donnez à l'agent unique une fenêtre de contexte plus grande, une meilleure récupération, plus d'outils, plus de tours).
- Les sous-tâches sont interdépendantes ou exigent des allers-retours d'affinage entre plusieurs lignes de pensée.
- La surcharge de coordination (temps de l'orchestrateur, communication, conciliation de conclusions contradictoires) est élevée par rapport au problème.

Autrement dit : un agent unique avec de meilleurs outils, un contexte plus long et plus de tours résout souvent le même problème pour moins cher et avec une meilleure qualité de raisonnement que plusieurs agents au contexte fragmenté. Le gain de vitesse du parallélisme est réel mais pas gratuit.

## Pratique

1. ▢ Vous construisez un système de questions-réponses. Option A : un agent avec des outils de recherche, d'exécution de code et de documentation. Option B : un orchestrateur qui lance en parallèle trois workers, chacun avec un outil spécialisé (worker de recherche, worker de code, worker de documentation). Les deux visent à répondre à des questions complexes d'utilisateurs. Dans quelles circonstances le coût en tokens de l'option B devient-il inférieur à celui de l'option A ?

<details markdown="1"><summary>Vérifier</summary>

C'est un piège. Dans la plupart des circonstances, l'option B coûte plus de tokens : vous payez trois exécutions complètes d'agent plus la surcharge de l'orchestrateur, comme dans l'exemple de cette leçon, 26 000 tokens contre 10 000. L'option B ne devient moins chère que dans un cas étroit : les trois sous-tâches sont vraiment indépendantes, et chacune est tellement plus simple que la question entière que les trois workers et l'orchestrateur réunis consomment moins de tokens que l'agent unique (par exemple trois workers à 2 500 tokens chacun plus un orchestrateur à 2 000, soit 9 500 au total, contre un agent unique à 10 000). Cela n'arrive que si l'agent unique gaspille beaucoup de tours sur le problème combiné. Sinon, l'option A est moins chère. Le compromis oppose le temps réel (l'option B est plus rapide grâce au parallélisme) aux tokens (l'option A est moins chère). Vous choisissez l'option B pour la vitesse, pas pour le coût.

</details>

2. ▢ Dans le système orchestrateur et worker de la leçon 18 (workers de recherche en parallèle), supposons que deux workers finissent par étudier la même source et arrivent à des conclusions différentes sur ce qu'elle dit. L'orchestrateur a les deux rapports. Que manque-t-il à l'orchestrateur qu'un agent unique aurait eu ?

<details markdown="1"><summary>Indice</summary>

Pensez à ce qui se trouve dans le transcript de chaque worker par opposition à ce qui se trouve dans le transcript d'un agent unique au moment de raisonner sur cette source.

</details>

<details markdown="1"><summary>Vérifier</summary>

L'orchestrateur voit deux conclusions mais pas le raisonnement qui a mené à chacune. Un agent unique, ayant lu la même source, aurait tout son raisonnement sur cette source dans un seul transcript : comment il a interprété le texte, quelle nuance il a remarquée, ce qu'il a envisagé et rejeté. Le raisonnement de l'agent unique est entièrement traçable. L'orchestrateur ne peut que demander « pourquoi êtes-vous arrivé à cette conclusion ? » et un worker devrait réexpliquer, ou l'orchestrateur devrait lancer un nouvel agent pour retracer le désaccord. C'est le contexte fragmenté.

</details>

3. ▢ Vous décidez d'utiliser le fan-out (orchestrateur et worker) ou un agent unique pour une tâche. La tâche est : étant donné un jeu de données et une question, nettoyer les données, les explorer, construire un modèle et rapporter les constats. Les phases (nettoyage, exploration, modélisation, rapport) s'exécuteront-elles en parallèle avec le fan-out, ou séquentiellement ?

    - a) En parallèle, parce que le fan-out lance tous les workers à la fois.
    - b) Séquentiellement, parce que l'exploration dépend du nettoyage, la modélisation dépend de l'exploration.
    - c) En parallèle, mais le travail peut être réparti de sorte que chaque worker fasse toutes les phases indépendamment.
    - d) Cela dépend de si les workers ont accès au même jeu de données.

<details markdown="1"><summary>Vérifier</summary>

**b)** Cette tâche ne se prête pas bien au fan-out parce que les phases sont séquentielles : on ne peut pas bien explorer des données sales, on ne peut pas modéliser sans comprendre les données, etc. Chaque phase dépend de la précédente. Le fan-out brille sur les tâches à sous-tâches indépendantes (étudier l'angle A, l'angle B, l'angle C en parallèle). Pour un travail séquentiel, la passation (leçon 18) convient mieux que le fan-out, ou bien un agent unique avec assez de tours est plus simple. (a) est faux : le parallélisme ne crée pas de magie ; les dépendances existent toujours. (c) est possible mais va à l'encontre de la spécialisation ; chaque worker aurait besoin de tous les outils et de toutes les connaissances. (d) est une fausse piste ; l'accès aux données n'est pas le facteur limitant ici.

</details>

4. ▢ L'article de Cognition soutient qu'un agent unique avec une meilleure récupération ou des outils plus capables résout souvent les problèmes pour moins de tokens qu'un système orchestrateur et worker. Quelle est la raison centrale de cette affirmation ?

<details markdown="1"><summary>Vérifier</summary>

Un agent unique garde tout son raisonnement dans un seul transcript, donc il intègre les constats, repère les contradictions et affine les conclusions dans une seule boucle de raisonnement. Un système orchestrateur et worker paie le coût en tokens de nombreuses boucles d'agent et fragmente le contexte entre elles, donc les workers redérivent ou recommuniquent les intuitions. Le gain d'efficacité de l'agent unique, qui garde le contexte unifié et le raisonnement connecté, l'emporte souvent sur le gain de vitesse du parallélisme du système multi-agent, surtout quand la question comporte des dépendances ou bénéficie d'un raisonnement intégré. Donner à un agent plus d'outils ou une meilleure récupération (tous deux moins chers que d'exécuter plusieurs agents) l'emporte souvent.

</details>

5. ▢ Vous construisez un système pour déboguer un programme défaillant. Vous envisagez le fan-out : lancer trois workers, chacun essayant une stratégie de débogage différente en parallèle, puis laisser l'orchestrateur choisir la meilleure intuition. Quel coût cette conception ne capture-t-elle pas, que la leçon 19 enseigne ?

<details markdown="1"><summary>Vérifier</summary>

Un coût en tokens multiplié par trois (chaque worker est une exécution d'agent complète), un contexte fragmenté (aucun worker ne voit les explorations des autres, donc ils risquent de redériver trois fois la même impasse au lieu d'apprendre les uns des autres), et l'orchestrateur doit concilier des conclusions potentiellement contradictoires sur la nature du bug. Un agent unique qui essaierait les trois stratégies en série construirait un modèle unifié du bug au fur et à mesure. Les trois workers ne peuvent pas le faire sans que l'orchestrateur exécute une étape de conciliation (un autre agent, plus de coût). Le fan-out achète de la vitesse (les trois workers finissent dans le temps du plus lent, pas de la somme des trois), mais les coûts sont élevés pour une tâche comme le débogage où une intuition s'appuie sur une autre.

</details>

## Exercices en situation réelle

- [ ] Prenez un problème que vous avez déjà résolu (débogage, analyse, planification, recherche, peu importe). Déroulez-le mentalement comme un agent unique avec beaucoup de tours, puis comme trois workers en fan-out. Où le parallélisme vous ferait-il gagner du temps réel ? Où le contexte fragmenté vous coûterait-il et imposerait-il un travail de redérivation ou de conciliation ?
- [ ] Lisez au moins une fois l'article de Cognition « Don't Build Multi-Agents ». Cherchez la section où l'auteur soutient qu'un agent unique plus de meilleurs outils bat l'orchestrateur et worker. Notez un exemple concret qu'il donne et ce qui a rendu l'agent unique moins cher.
- [ ] Demain : esquissez une tâche que vous pourriez intégrer dans un système d'agents. Pour cette tâche, estimez : combien de tokens utiliserait un agent unique ? Combien coûterait un système en fan-out (supposez trois workers, chacun à un coût en tokens légèrement inférieur à la part de tâche de l'agent unique) ? Le gain de vitesse vaut-il le multiplicateur de tokens pour vous ?

## Pour aller plus loin

- [Billet : "Don't Build Multi-Agents", Cognition](https://cognition.ai/blog/dont-build-multi-agents)
- [Billet : "How We Built Our Multi-Agent Research System", Anthropic Engineering](https://www.anthropic.com/engineering/multi-agent-research-system)
- [Ressources](../RESOURCES.md)

---

Ça ne passe pas ? Relisez la source primaire en haut de page, car cette leçon la condense et c'est dans la condensation que la compréhension s'échappe. Consultez le [glossaire](../GLOSSARY.md) pour tout terme qui vous a paru glissant.

Si c'est la leçon elle-même qui n'est pas claire plutôt que la matière, c'est un défaut : [ouvrez une issue](https://github.com/TokenCemetery/teach/issues).
