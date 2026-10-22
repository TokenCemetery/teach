---
title: "Agents LLM"
description: "Construire la boucle soi-même : outils, contexte, mémoire, et savoir quand un agent est la mauvaise réponse"
type: topic
---

# Agents LLM

Être capable de construire soi-même une boucle d'agent, de décider si une tâche donnée a vraiment besoin d'un agent plutôt que d'un workflow fixe, et de diagnostiquer un agent défaillant à partir de sa trajectoire au lieu d'ajouter une instruction de plus à son prompt.

**Dernière leçon :** [0037. Relire la conception d'agent de quelqu'un d'autre](lessons/0037-reviewing-someone-elses-agent-design.md)

## Objectif

- Écrire la boucle d'agent pour une tâche donnée, et nommer ce que fait chaque message de son contexte et ce qui met fin à la boucle.
- Choisir entre un prompt unique, un workflow fixe et un agent pour une tâche donnée, et défendre ce choix face au coût de l'option écartée.
- Concevoir la surface d'outils d'un agent : noms, descriptions, formes de retour, et la frontière de permissions qui décide ce qu'il peut faire sans surveillance.
- Diagnostiquer un agent défaillant à partir de sa trajectoire, en nommant la cause (une boucle, un contexte empoisonné, un outil mal spécifié, une mauvaise condition d'arrêt) plutôt que de re-prompter au hasard.
- Expliquer pourquoi un agent qui lit du contenu non fiable ne peut pas être sécurisé par les seules instructions du prompt, et concevoir la frontière qui tient réellement.
- Budgéter le coût en tokens et la latence d'une boucle agentique, et dire de quelle partie de la boucle vient l'amplification.

## Contraintes

- Neutre vis-à-vis des fournisseurs. Les boucles, les schémas d'outils et le flux de contrôle sont donnés en pseudocode proche de Python, pour que le contenu survive aux changements incessants des API d'appel d'outils qui datent la plupart des textes sur les agents.
- Les formats de transmission sont l'exception, car l'aspect d'un message d'appel d'outil sur le réseau est un fait et non un algorithme. Une vraie paire requête et réponse capturée est montrée, et un second fournisseur n'apparaît que sous la forme de la différence avec la première.
- Aucun framework n'est supposé ni enseigné. Ce qu'un framework apporte (état durable, flux de contrôle en graphe, reprise) est traité une seule fois, vers la fin, comme une décision et non comme un tutoriel.
- Les exercices reposent davantage sur l'inspection que sur la construction : lire une vraie trace, un vrai schéma d'outil, un vrai manifeste de serveur MCP, et marquer la frontière de permissions d'un agent qui tourne déjà.
- Suppose de savoir ce qu'est un modèle de langage et d'être à l'aise avec la lecture de code proche de Python. Aucune expérience préalable de construction d'agents n'est requise.

## Hors périmètre

- L'évaluation comme discipline : voir [`llm/evals`](../../llm/evals/) (la leçon 0013 couvre les trajectoires, la réussite de la tâche face à la précision par étape, et `pass^k`). Elle n'est reprise ici que comme l'unique capacité dont un constructeur d'agents a besoin, avec un lien plutôt qu'une répétition.
- Les rouages internes du pipeline de récupération : voir [`llm/rag`](../../llm/rag/). La récupération apparaît ici comme un outil qu'un agent appelle, pas comme du chunking, de l'embedding et du reranking.
- Les rouages internes du serving et de l'inférence : voir [`llm/inference`](../../llm/inference/) pour la latence, le batching et le décodage contraint.
- Entraîner un modèle à utiliser des outils : voir [`llm/finetuning`](../../llm/finetuning/).
- Les nouveaux essais, l'idempotence et la défaillance partielle comme problèmes de systèmes distribués : voir [`architecture/distributed-systems`](../../architecture/distributed-systems/). Traités ici seulement pour ce qui distingue un appel d'outil d'un appel distant ordinaire.
- Le prompting comme sujet (instructions, exemples, raisonnement, sortie structurée, gabarits et mesure d'une modification de prompt) : voir [`llm/prompting`](../../llm/prompting/). Ce parcours garde les descriptions d'outils, l'injection avec outils et le caching sous concurrence, et renvoie vers ce parcours pour le prompting en général.

## Le fil conducteur

Seize étapes, de l'absence de connaissances préalables jusqu'au jugement d'un senior. Pas une liste de leçons : une étape comprend plusieurs leçons, et les frontières sont souples.

| Étape | Leçons | Contenu | Terminée quand |
| --- | --- | --- | --- |
| 1. Ce qu'est un agent | 0001 à 0002 | La boucle, agent contre workflow contre chaîne, le spectre d'autonomie | Vous savez classer un système et dire si « agent » est le bon mot pour le désigner |
| 2. Mécanique de l'appel d'outils | 0003 à 0005 | Le format de transmission d'un appel d'outil, les schémas de paramètres, qui exécute quoi, les appels parallèles, les erreurs renvoyées comme résultats | Vous savez lire un échange brut d'appel d'outil et dire ce que chaque message a fait |
| 3. La boucle à partir de zéro | 0006 à 0007 | Écrire la boucle, les conditions d'arrêt, le transcript comme état complet de l'agent | Vous savez écrire une boucle d'agent et défendre l'endroit où elle s'arrête |
| 4. La conception d'outils comme prompt engineering | 0008 à 0009 | Noms et descriptions comme surface de prompt, formes de retour, coût en tokens des résultats, surcharge du jeu d'outils | Vous savez concevoir une surface d'outils et dire pourquoi chaque description est formulée ainsi |
| 5. Gestion du contexte | 0010 à 0012 | La fenêtre comme budget central : troncature, compaction, récupération à la demande, sous-agents comme isolation du contexte | Vous savez planifier ce qui quitte le contexte, et quand, pour une tâche de longue durée |
| 6. Mémoire et état | 0013 à 0014 | Scratchpad intra-exécution contre mémoire entre exécutions, fichiers comme mémoire, pourquoi la récupération n'est pas de la mémoire | Vous savez choisir où vit un fait donné et dire ce qui se passe à la fin de l'exécution |
| 7. Planification et réflexion | 0015 à 0017 | ReAct, plan puis exécution, auto-critique, décomposition, ce que les modèles de raisonnement ont changé | Vous savez choisir un schéma de planification pour une tâche et nommer ce qu'il coûte en tokens et en latence |
| 8. Multi-agent | 0018 à 0019 | Orchestrateur et worker, passation, fan-out, coût de coordination, quand un seul agent mieux outillé l'emporte | Vous savez dire si un deuxième agent apporte quelque chose que le premier n'aurait pas pu recevoir |
| 9. Protocoles et interopérabilité | 0020 à 0021 | Outils, ressources, prompts et transports de MCP, formats d'appel de fonctions des fournisseurs, découverte d'outils à grande échelle | Vous savez lire le manifeste d'un serveur MCP et dire ce qu'il expose et ce qu'il ne standardise pas |
| 10. Environnements d'exécution | 0022 à 0023 | Sandboxing, exécution de code comme outil, accès au système de fichiers, points d'approbation humaine | Vous savez placer la frontière du sandbox pour un ensemble d'outils donné |
| 11. Computer use et agents de navigateur | 0024 à 0026 | Captures d'écran comme observations, ancrage d'une action à une coordonnée, le problème de fiabilité | Vous savez dire pourquoi un agent qui pilote l'écran échoue autrement qu'un agent qui appelle des outils |
| 12. Modes de défaillance et observabilité | 0027 à 0029 | Boucles, empoisonnement du contexte, erreurs d'outils en cascade, arguments hallucinés, traçage et rejeu de trajectoire | Face à une trajectoire, vous savez nommer l'étape fautive au lieu de re-prompter |
| 13. Évaluer un agent | 0030 à 0030 | Résultat contre trajectoire, fiabilité sur essais répétés, ce que mesurent réellement les benchmarks d'agents | Vous savez dire quoi mesurer pour un agent donné, et confier le reste à `llm/evals` |
| 14. Sécurité | 0031 à 0032 | L'injection de prompt comme problème qui définit les agents, la triade létale, le moindre privilège, le confused deputy, la chaîne d'approvisionnement MCP | Vous savez concevoir une frontière de permissions qui tient quand l'agent lit du contenu hostile |
| 15. Production, coût et ce qu'apportent les frameworks | 0033 à 0035 | Amplification de tokens, prompt caching, concurrence, durabilité et reprise, coût par tâche terminée | Vous savez budgéter le coût d'une boucle et dire quelle garantie de framework un déploiement exige vraiment |
| 16. Jugement | 0036 à 0037 | Quand ne pas construire d'agent, relire la conception d'agent de quelqu'un d'autre en nommant ce que coûte un choix, trancher une affirmation contestée à partir de la source primaire | On vous fait confiance pour trancher et l'expliquer à quelqu'un d'autre |

## Leçons

Suivez-les dans l'ordre.

| # | Leçon | Enseigne |
|---|---|---|
| [0001](lessons/0001-the-agent-loop.md) | La boucle d'agent | Ce qui fait d'un système un agent, et le cycle en quatre étapes qui tourne en dessous |
| [0002](lessons/0002-agent-workflow-or-prompt.md) | Agent, workflow ou simple prompt | Où se situe une tâche sur le spectre d'autonomie, et comment défendre ce choix |
| [0003](lessons/0003-the-wire-format-of-a-tool-call.md) | Le format de transmission d'un appel d'outil | À quoi ressemblent réellement un appel d'outil et son résultat dans le protocole entre votre harness et le fournisseur du modèle |
| [0004](lessons/0004-schemas-and-who-executes.md) | Schémas de paramètres et qui exécute quoi | Comment les schémas JSON contraignent ce qu'un modèle peut envoyer, et la différence entre outils client et outils serveur |
| [0005](lessons/0005-parallel-calls-and-errors-as-results.md) | Appels parallèles et erreurs comme résultats | Comment un modèle peut demander plusieurs outils à la fois, et pourquoi les erreurs d'outils sont des résultats et non des exceptions |
| [0006](lessons/0006-writing-the-loop.md) | Écrire la boucle | Construire la boucle d'agent à partir de pseudocode et choisir délibérément les conditions d'arrêt |
| [0007](lessons/0007-the-transcript-as-state.md) | Le transcript comme état | Comprendre que le transcript est la seule mémoire persistante de l'agent entre les tours |
| [0008](lessons/0008-naming-and-describing-a-tool.md) | Nommer et décrire un outil | Le nom et la description d'un outil sont ce que le modèle lit pour décider quand et comment l'appeler |
| [0009](lessons/0009-return-shapes-and-tool-set-bloat.md) | Formes de retour et surcharge du jeu d'outils | La valeur de retour d'un outil consomme du budget de contexte, et trop d'outils nuit à la capacité du modèle à choisir correctement |
| [0010](lessons/0010-the-context-window-as-budget.md) | La fenêtre de contexte comme budget | La fenêtre de contexte est une ressource finie que le harness gère activement au fil du temps, pas un journal inerte |
| [0011](lessons/0011-compaction-and-retrieval-on-demand.md) | Compaction et récupération à la demande | Deux stratégies pour garder dans le budget le contexte d'un agent de longue durée tout en préservant ce qui compte encore |
| [0012](lessons/0012-sub-agents-as-context-isolation.md) | Les sous-agents comme isolation du contexte | Lancer un sous-agent isole un long travail d'exploration du budget de contexte du parent |
| [0013](lessons/0013-scratchpad-versus-memory.md) | Scratchpad contre mémoire | La différence entre les notes qu'un agent garde pendant une exécution et les faits dont il a besoin sur plusieurs exécutions |
| [0014](lessons/0014-files-as-memory.md) | Les fichiers comme mémoire | Utiliser des fichiers durables comme forme la plus simple de mémoire entre exécutions pour les agents |
| [0015](lessons/0015-react-interleaving-reasoning-and-acting.md) | ReAct : entrelacer raisonnement et action | Schéma qui associe de courtes étapes de raisonnement à chaque action, pour que le modèle puisse observer et s'adapter |
| [0016](lessons/0016-plan-then-execute-and-decomposition.md) | Plan puis exécution et décomposition | La planification explicite en amont comme alternative à ReAct, quand l'utiliser et comment gérer la replanification |
| [0017](lessons/0017-self-critique-and-reasoning-models.md) | L'auto-critique et ce que les modèles de raisonnement ont changé | La boucle de réflexion comme étape explicite, ses coûts, et comment le raisonnement interne étendu influe sur le moment de l'utiliser |
| [0018](lessons/0018-orchestrator-and-worker.md) | Orchestrateur et worker | Concevoir un système multi-agent où un agent planifie et délègue pendant que les workers exécutent en parallèle |
| [0019](lessons/0019-coordination-cost.md) | Le coût de coordination | Comprendre pourquoi construire plusieurs agents coûte plus cher qu'un seul agent bien équipé, et comment décider quand le gain de parallélisme vaut ce coût |
| [0020](lessons/0020-mcp-tools-resources-and-prompts.md) | MCP : outils, ressources et prompts | Le Model Context Protocol comme interface standardisée permettant aux harness d'agents de découvrir et d'invoquer des outils externes, de lire des données et d'utiliser des gabarits |
| [0021](lessons/0021-provider-formats-and-discovery-at-scale.md) | Formats des fournisseurs et découverte d'outils à grande échelle | Pourquoi MCP et les formats de transmission propres à chaque fournisseur sont des couches distinctes, et pourquoi charger tous les outils en contexte ne passe pas à l'échelle avec de nombreux serveurs connectés |
| [0022](lessons/0022-sandboxing-and-approval-gates.md) | Sandboxing et points d'approbation | Frontières d'exécution et points de contrôle humains qui protègent contre les erreurs du modèle |
| [0023](lessons/0023-code-execution-as-a-tool.md) | L'exécution de code comme outil | Donner à un agent un unique outil d'exécution de code en sandbox plutôt que de nombreux outils étroits et individuels |
| [0024](lessons/0024-screenshots-as-observations.md) | Les captures d'écran comme observations | Comment les agents de computer use observent l'écran sous forme d'image plutôt que de données structurées, et pourquoi la structure de la boucle tient toujours |
| [0025](lessons/0025-grounding-an-action-to-a-coordinate.md) | Ancrer une action à une coordonnée | Pourquoi traduire une intention visuelle en coordonnée de pixel est plus difficile et plus fragile qu'un argument typé d'appel d'outil |
| [0026](lessons/0026-why-browser-agents-fail-differently.md) | Pourquoi les agents de navigateur échouent différemment | Les agents pilotés par l'écran échouent de façons que les agents à appels d'outils ne connaissent pas, et pourquoi WebArena a créé un benchmark pour mesurer et étudier ces échecs |
| [0027](lessons/0027-loops-and-context-poisoning.md) | Boucles et empoisonnement du contexte | Deux modes de défaillance visibles dans une trajectoire, les boucles répétitives et l'empoisonnement silencieux du contexte, et comment repérer chacun |
| [0028](lessons/0028-cascading-tool-errors.md) | Erreurs d'outils en cascade et arguments hallucinés | Une erreur d'outil qui mène à de mauvaises décisions et à une spirale de confusion, et des arguments bien typés mais faux que les schémas ne peuvent pas attraper |
| [0029](lessons/0029-tracing-and-trajectory-replay.md) | Traçage et rejeu de trajectoire | Utiliser des conventions de trace indépendantes des fournisseurs pour capturer les exécutions d'agents, et rejouer les trajectoires pour parcourir pas à pas les échecs |
| [0030](lessons/0030-evaluating-an-agent.md) | Évaluer un agent | Mesurer la réussite d'un agent au niveau du résultat plutôt qu'au niveau de la trajectoire, et pourquoi une seule exécution réussie ne prouve pas que l'agent est fiable |
| [0031](lessons/0031-prompt-injection-and-the-lethal-trifecta.md) | Injection de prompt et triade létale | Comment des agents qui lisent du contenu non fiable deviennent exploitables, et pourquoi le seul prompting ne les sécurise pas |
| [0032](lessons/0032-least-privilege-and-the-confused-deputy.md) | Moindre privilège et confused deputy | Comment limiter les capacités d'un agent pour qu'une injection de prompt cause des dégâts contenus plutôt qu'une brèche catastrophique |
| [0033](lessons/0033-token-amplification-and-cost.md) | Amplification de tokens et coût par tâche terminée | Pourquoi les systèmes agentiques consomment bien plus de tokens par tâche terminée qu'un prompt unique, et comment le budgéter |
| [0034](lessons/0034-prompt-caching-and-concurrency.md) | Prompt caching et concurrence | Comment le caching réduit le coût en tokens par tâche et comment la concurrence augmente le débit, et pourquoi les confondre est une erreur de budget |
| [0035](lessons/0035-durability-and-what-frameworks-buy.md) | Durabilité et ce qu'apporte un framework | L'exécution durable et reprenable d'un agent comme problème d'ingénierie, ce que les frameworks offrent concrètement, et un principe de décision pour en adopter un |
| [0036](lessons/0036-when-not-to-build-an-agent.md) | Quand ne pas construire d'agent | Le jugement pour décider si une tâche a réellement besoin d'un agent, et la discipline de dire non quand il ne vaut pas son coût |
| [0037](lessons/0037-reviewing-someone-elses-agent-design.md) | Relire la conception d'agent de quelqu'un d'autre | Comment évaluer méthodiquement un système d'agents, et comment trancher une affirmation contestée en revenant à la source primaire |

## Référence

- [Glossaire](GLOSSARY.md) : termes de référence pour ce sujet
- [Ressources](RESOURCES.md) : sources fiables

## Comment cela fonctionne

Chaque leçon est courte et autonome. Les corrigés sont repliés : rappelez-vous d'abord, puis ouvrez-les. Les exercices en situation réelle comptent plus que la lecture, et les espacer dans le temps est justement le but. Tout ce qui reste flou à la fin d'une leçon mérite d'être suivi jusqu'à sa source primaire avant de passer à la suite.
