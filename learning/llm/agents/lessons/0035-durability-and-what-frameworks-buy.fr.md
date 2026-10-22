---
title: "35. Durabilité et ce qu'apporte un framework"
description: "L'exécution durable et reprenable d'un agent comme problème d'ingénierie, ce que les frameworks offrent concrètement, et un principe de décision pour en adopter un"
type: lesson
---

# Leçon 35. Durabilité et ce qu'apporte un framework

**Lien avec la mission :** Décider d'écrire soi-même un harness d'agent ou d'adopter un framework, d'après les garanties dont on a réellement besoin pour le déploiement.
**Source primaire :** [Billet : "Building Effective Agents", Anthropic Engineering](https://www.anthropic.com/engineering/building-effective-agents)
**Prérequis :** [Leçon 34](0034-prompt-caching-and-concurrency.md), [Harness](../GLOSSARY.md)

## Échauffement

1. ▢ Dans la leçon 7, vous avez appris que, le transcript étant l'état complet d'un agent, reprendre une exécution revient à renvoyer au modèle le transcript sauvegardé. Que signifie cela quant au fait qu'une exécution est « reprenable en principe » ?

<details markdown="1"><summary>Vérifier</summary>

En principe, toute exécution d'agent est reprenable parce que le transcript capture tout ce que l'agent sait. Si vous sauvegardez le transcript après chaque tour et qu'un plantage survient, vous pouvez charger le transcript sauvegardé, ajouter le dernier tour échoué ou incomplet, et continuer. Le transcript est l'état complet, donc la reprise n'exige rien d'autre.

</details>

2. ▢ Dans la leçon 33, vous avez appris qu'un budget par tâche additionne le coût complet de toutes les tentatives, nouveaux essais et réflexions jusqu'à la réussite d'une tâche. Si un agent plante en cours d'exécution et que vous devez recommencer depuis le début, comment cela affecte-t-il le budget par tâche ?

<details markdown="1"><summary>Vérifier</summary>

Le redémarrage ajoute une tentative complète supplémentaire au budget. Si un agent plante au tour 15 d'une exécution de 30 tours, vous avez perdu 15 tours de travail et devez payer à nouveau les 30 tours. Le budget par tâche est maintenant à peu près doublé (deux exécutions complètes de 30 tours au lieu d'une). C'est une pénalité de coût importante, et c'est pourquoi la durabilité (éviter les plantages et reprendre automatiquement depuis le dernier état sauvegardé) compte pour la maîtrise des coûts.

</details>

## À savoir

### La durabilité est distincte de la reprenabilité en principe

La leçon 7 a établi que les exécutions d'agents sont reprenables en principe : le transcript est l'état. Mais « reprenable en principe » et « reprenable en production » sont deux choses différentes. La reprenabilité en principe dit « si un humain sauvegarde le transcript à la main et relance l'agent, celui-ci continuera ». La durabilité en production dit :

- Le transcript est automatiquement persisté dans un stockage durable (une base de données, un système de fichiers avec sauvegardes, pas seulement la mémoire) après chaque tour.
- Si le processus plante, le dernier état persisté est automatiquement chargé et l'exécution reprend sans intervention manuelle.
- Si plusieurs agents s'exécutent en concurrence, l'état de chacun est suivi indépendamment, de sorte qu'un plantage de l'un ne fait pas perdre le travail d'un autre.
- Si un appel d'outil dépasse le délai ou si le réseau tombe, l'agent réessaie ou annule proprement, sans laisser d'état partiel.

Ce travail d'infrastructure est distinct de la boucle d'agent elle-même (leçon 6). La boucle ne se soucie pas de la durabilité ; elle traite simplement ce qu'on lui donne. Le harness (le code autour de la boucle) doit faire de la durabilité une préoccupation explicite.

### À quoi ressemblent plantages et défaillances sans durabilité

Sans état durable, voici les modes de défaillance :

- Plantage du processus en cours d'exécution : tout le transcript de l'agent est perdu (s'il n'était qu'en mémoire). L'utilisateur doit recommencer la tâche depuis le début. Le budget par tâche est doublé.
- Délai dépassé sur un appel d'outil : le harness ne sait pas si l'outil a réussi ou échoué. Il peut réessayer, ou non. Le transcript peut avoir un résultat ajouté, ou non, selon la gestion d'erreurs du harness. L'état devient incohérent.
- L'agent se bloque en attendant un résultat d'outil : le processus est coincé et doit être tué à la main. Aucun point de reprise n'est sauvegardé. Toute l'exécution est perdue.
- Plusieurs agents s'exécutent en concurrence, l'un plante : les autres agents continuent, mais on n'a aucune visibilité sur quelle partie du système a échoué ni sur la façon de reprendre celle qui a échoué.

Chacun de ces cas est un vrai problème de déploiement. L'« exécution durable » est la pratique qui consiste à construire des systèmes qui gèrent ces défaillances automatiquement et correctement.

### Ce qu'un framework apporte concrètement

Quand vous adoptez un framework pour le développement d'agents, il comprend typiquement tout ou partie de ces garanties :

**État durable et checkpointing automatique.** Le framework persiste automatiquement le transcript (et tout état de l'agent) dans un stockage durable après chaque tour. Si le processus plante, l'exécution suivante charge automatiquement le dernier checkpoint et reprend à partir de là. Vous n'avez pas à écrire vous-même la logique de persistance.

**Flux de contrôle en graphe.** Au lieu d'écrire une boucle à la main (leçon 6), vous décrivez la structure de l'agent comme un graphe : « Après cette étape, si le résultat est X, aller ici ; si Y, aller là. » Le framework gère le flux de contrôle et la persistance, pour que vous vous concentriez sur les nœuds (les étapes) plutôt que sur la boucle elle-même. C'est utile pour les agents à logique ramifiée ou conditionnelle complexe.

**Politiques intégrées de nouvel essai et de backoff.** Quand un appel d'outil échoue (erreur réseau, délai dépassé, limite de débit), le framework a une stratégie de nouvel essai configurée : attendre un peu, réessayer, backoff exponentiel. Vous n'avez pas à implémenter les nouveaux essais dans votre propre harness.

**Traçage et observabilité intégrés.** Le framework génère automatiquement les traces structurées de la leçon 29 : événements horodatés, spans, métadonnées sur chaque étape. Vous pouvez interroger cette trace sans la câbler vous-même. Certains frameworks s'intègrent à des backends d'observabilité (comme un service de traçage) pour que vous puissiez voir les exécutions d'agents dans un tableau de bord.

**Annulation et compensation.** Certains frameworks permettent de définir des actions de compensation : si l'étape A a réussi mais que l'étape B a échoué, annuler automatiquement A. C'est utile pour les agents qui modifient des systèmes externes et doivent se rétablir si des étapes ultérieures échouent.

Tous les frameworks n'offrent pas tout cela. Certains sont minimaux (checkpointing plus nouveaux essais). D'autres sont complets (tout ce qui précède et plus). Le principe de décision (plus bas) porte sur les capacités dont vous avez réellement besoin.

### Ce que les frameworks n'apportent PAS

Il est important d'être clair sur ce que les frameworks ne résolvent pas :

- La boucle d'agent elle-même reste la même (leçon 6). Le framework ne rend pas la boucle plus simple ni plus rapide ; il l'enveloppe simplement de durabilité et d'observabilité.
- Le coût en tokens n'est pas réduit par l'usage d'un framework. Un framework ne rend pas les agents moins chers ; il les rend plus fiables et plus observables.
- La qualité du raisonnement de l'agent n'est pas améliorée par un framework. Un framework ne rend pas le modèle meilleur pour décider ; vous devez toujours concevoir vous-même les outils, les prompts et la planification (leçons 8, 9, 16).
- Le framework n'est pas neutre. Adopter un framework vous engage dans ses abstractions (flux de contrôle en graphe, son format de configuration, son modèle d'observabilité, ses contraintes de déploiement). Changer de framework plus tard coûte cher.

### Le principe de décision : quand adopter un framework

Le billet « Building Effective Agents » note que de nombreuses équipes construisent d'abord une boucle d'agent minimale (leçon 6) et ne réalisent que plus tard qu'elles ont besoin de durabilité. La décision d'adopter un framework doit reposer sur le fait que les garanties du framework résolvent un problème de déploiement que vous avez, et non sur le fait qu'écrire la boucle vous ait semblé difficile (la boucle est la partie facile).

Adoptez un framework quand :

- **Vous avez besoin d'une exécution durable.** Vos agents s'exécuteront assez longtemps (ou seront assez importants) pour que perdre du travail à cause de plantages soit inacceptable. Une simple boucle sans persistance ne convient pas aux tâches de production.
- **Vous avez besoin d'observabilité à grande échelle.** Vous avez plusieurs agents qui s'exécutent en concurrence et devez voir ce que fait chacun, tracer les défaillances et corréler les logs. Un harness à base d'instructions print ne passera pas à l'échelle.
- **Vous avez un flux de contrôle complexe.** Votre agent a besoin de branchements ou de boucles conditionnels (par exemple « si cette condition, appeler cet ensemble d'outils ; sinon appeler cet autre ensemble »). Le modèle en graphe d'un framework est plus propre que des conditionnelles écrites à la main.
- **Vous voulez des nouveaux essais et un backoff intégrés.** Vous appelez des API externes susceptibles d'échouer temporairement, et vous voulez que le framework gère automatiquement les nouveaux essais avec un backoff exponentiel. Écrire cela vous-même est fastidieux et sujet aux erreurs.

N'adoptez PAS un framework quand :

- **Vous expérimentez.** En recherche ou en prototypage, une simple boucle est plus rapide à itérer que d'apprendre un framework. Revenez à la décision de framework une fois l'approche stable.
- **Votre agent est simple.** Un agent unique avec quelques appels d'outils et un objectif direct n'a pas besoin de la complexité d'un framework. Une boucle plus un fichier de transcript peut suffire.
- **Vous avez des contraintes de déploiement inhabituelles.** Certains frameworks supposent des environnements précis (cloud, Docker, etc.) ou ont des caractéristiques de performance qui ne conviennent pas à vos contraintes. Il vous faudra peut-être un harness sur mesure.
- **Le framework est immature ou étroitement lié à un fournisseur.** Les schémas d'exécution durable évoluent encore. Certains frameworks sont bien établis et documentés (cherchez des avis et des déploiements en production) ; d'autres non. Et certains sont étroitement liés à l'API d'un seul fournisseur, ce qui limite votre flexibilité par la suite.

### Comment évaluer un framework

Si vous décidez d'adopter un framework, voici les questions à poser :

- Prend-il en charge le checkpointing et la reprise ? À quelle fréquence ? La granularité des checkpoints (par tour, par tentative, par tâche) est-elle celle dont vous avez besoin ?
- Quelle observabilité fournit-il ? Pouvez-vous interroger les traces ? Pouvez-vous l'intégrer à vos outils existants de journalisation et de supervision ?
- Quelles abstractions de flux de contrôle prend-il en charge ? Correspondent-elles à la structure de votre agent, ou devriez-vous plier votre agent pour qu'il y rentre ?
- Quel est le mode de défaillance si le framework plante ? Pouvez-vous récupérer vos transcripts et continuer sans le framework ?
- Comment gère-t-il la concurrence ? Plusieurs agents peuvent-ils s'exécuter indépendamment sans interférer ?
- Quel enfermement chez un fournisseur y a-t-il ? Si vous devez en changer plus tard, quelle quantité de travail cela représenterait-il ?

La dernière question est importante : il n'existe pas de source unique faisant autorité et indépendante des fournisseurs pour l'exécution durable d'agents, comme il en existe une pour, disons, la spécification MCP (leçon 20). Les schémas d'exécution durable sont documentés principalement dans les guides propres à chaque framework. Traitez donc cette leçon comme le vocabulaire et le cadre de décision, pas comme une comparaison de frameworks. Quand vous évaluez un framework précis, lisez sa propre documentation pour comprendre ses garanties spécifiques.

### L'histoire de bout en bout : de la boucle à la production

Voici l'arc d'un système d'agent typique :

1. **Développement (leçon 6).** Écrire une boucle qui envoie le transcript au modèle et exécute des outils. C'est rapide à prototyper.
2. **Test (leçon 29).** Construire des traces et du diagnostic pour comprendre ce que fait votre agent, quand il échoue et pourquoi. Apprendre où votre agent est fragile.
3. **Optimisation (leçons 10 à 34).** Mettre en œuvre la gestion du contexte, le prompt caching, une meilleure planification. Réduire le coût en tokens et la latence.
4. **Déploiement.** Vous devez maintenant décider : à quoi ressemble la production ? Si c'est une tâche ponctuelle ou une expérience, un script plus un fichier de transcript peut suffire. Si c'est un service qui sert des utilisateurs, une simple boucle ne convient pas. Il vous faut de la durabilité, de l'observabilité, des politiques de nouvel essai et un moyen de suivre de nombreux agents concurrents. C'est là qu'intervient la décision de framework.

Un framework n'est pas le point de départ ; c'est la réponse à « qui construit et maintient la couche de durabilité et d'observabilité ? » Vous la construisez vous-même (un harness sur mesure plus l'infrastructure), ou vous adoptez la réponse d'un framework (en acceptant ses abstractions et ses contraintes). Les deux sont des choix légitimes. La décision de framework n'est pas « puis-je écrire une boucle d'agent » (la leçon 6 y a déjà répondu oui). La question est « veux-je construire moi-même cette infrastructure de production, ou adopter la solution d'un framework existant ? »

## Pratique

1. ▢ Vous exécutez un agent pour traiter 1 000 tickets de support client. Chaque ticket prend 20 tours à un agent. Si l'agent plante au tour 10 du ticket 500 et que vous n'avez aucun checkpointing, combien de tours au total sont perdus ou gaspillés ?

<details markdown="1"><summary>Vérifier</summary>

Vous perdez 10 tours de travail sur le ticket 500. Au redémarrage du processus, vous devez relancer entièrement le ticket depuis le début, ce qui gaspille 20 tours de plus. Vous devez aussi relancer les tickets 1 à 499 (qui s'étaient terminés mais sont toujours en mémoire, donc perdus si le processus a planté). Avec un checkpointing, vous sauvegarderiez après chaque ticket, donc perdre un ticket coûte 20 tours, pas plus. Pour 1 000 tickets * 20 tours = 20 000 tours au total. Sans checkpointing, un plantage en cours de tâche gaspille à peu près 10 000 tours (la moitié du travail restant plus la relance de la tâche qui a planté). C'est pourquoi la durabilité compte pour les tâches à grande échelle.

</details>

2. ▢ Vous avez deux options pour votre système d'agents : l'option A consiste à écrire un harness sur mesure avec durabilité (checkpointing, nouveaux essais, observabilité). Cela prend 2 semaines à construire et à déboguer. L'option B consiste à adopter un framework existant (qui gère tout cela pour vous) et à passer 1 semaine à l'apprendre. Les deux systèmes exécuteront la même logique d'agent. Pourquoi l'option B pourrait-elle quand même être plus coûteuse à long terme ?

<details markdown="1"><summary>Indice</summary>

Pensez à la flexibilité, à la maintenance, et à ce qui se passe si vos besoins changent ou si vous voulez changer de système.

</details>

<details markdown="1"><summary>Vérifier</summary>

L'option B vous engage dans les abstractions et l'implémentation du framework. Si vos besoins changent (par exemple vous avez besoin d'un autre flux de contrôle ou d'un autre backend de stockage), vous êtes contraint par ce que le framework prend en charge. Si vous voulez changer de framework plus tard, vous devez porter toutes vos définitions d'agents et vos workflows. L'option A (harness sur mesure) est plus flexible mais plus coûteuse au départ et à maintenir. Le compromis est : l'option B fait gagner du temps au départ mais vous enferme ; l'option A coûte plus au départ mais vous donne de la flexibilité à long terme. Le seuil de rentabilité dépend de vos attentes sur la durée de vie du système et sur la probabilité que les besoins changent.

</details>

3. ▢ Vous évaluez deux frameworks pour le développement d'agents. Le framework X fournit du checkpointing et des nouveaux essais mais pas d'observabilité intégrée (vous devez câbler le traçage vous-même). Le framework Y fournit tout cela plus un constructeur de flux de contrôle en graphe, mais exige que tous les agents soient définis dans son DSL propriétaire. Quel framework choisir si votre principale préoccupation est d'éviter de perdre du travail quand un agent plante et de reprendre automatiquement ?

    - a) Le framework X, parce qu'il est plus simple et vous force à apprendre moins.
    - b) Le framework Y, parce que son observabilité intégrée vous aidera à déboguer les plantages plus vite.
    - c) L'un comme l'autre fournit la fonctionnalité centrale de checkpointing dont vous avez besoin ; le choix dépend de vos autres contraintes.
    - d) Aucun des deux ; vous devriez construire un harness sur mesure pour ne pas être enfermé.

<details markdown="1"><summary>Vérifier</summary>

**c)** Les deux frameworks fournissent du checkpointing et une reprise automatique, ce qui est votre principale préoccupation. Les différences (observabilité, DSL) sont secondaires. Si vous avez besoin d'observabilité intégrée ou aimez le modèle en graphe, le framework Y peut valoir l'enfermement. Si vous préférez câbler vous-même l'observabilité ou si vous avez du code d'agent existant en Python/Go/etc., le framework X convient. Aucun n'a tort ; cela dépend de vos autres contraintes. L'option a est fausse parce que la simplicité seule n'est pas le critère décisif. L'option b confond l'observabilité (agréable à avoir) avec la durabilité (l'exigence que vous avez énoncée). L'option d n'est pas fausse (un harness sur mesure donne toujours de la flexibilité) mais elle esquive la question ; si la durabilité est importante, il vous faut une solution, et la décision est de savoir si cette solution est un framework ou du sur mesure.

</details>

4. ▢ Vous avez construit un agent avec une simple boucle (leçon 6) sans persistance. L'agent fonctionne bien en test. Vous voulez maintenant le déployer en production pour traiter de vraies demandes d'utilisateurs. Quelle est l'infrastructure minimale à ajouter avant de pouvoir dire en confiance que l'agent est durable en production ?

<details markdown="1"><summary>Vérifier</summary>

Au minimum : (1) Une persistance automatique du transcript dans un stockage durable (une base de données ou un système de fichiers avec sauvegardes) après chaque tour de boucle. (2) Un chargement automatique du dernier transcript persisté au redémarrage du processus, pour que l'agent reprenne depuis le dernier checkpoint, pas depuis le début. (3) Une gestion d'erreurs propre pour les appels d'outils : si un outil dépasse le délai ou renvoie une erreur, l'agent réessaie avec une politique de backoff ou consigne explicitement l'échec dans le transcript (pour que l'état soit cohérent). (4) Pour les agents concurrents, chaque agent doit avoir son propre transcript et son propre checkpoint isolés. Ces quatre éléments transforment une boucle de développement en quelque chose qui peut survivre aux plantages et servir du trafic de production.

</details>

## Exercices en situation réelle

- [ ] Relisez la documentation d'un framework d'agents de production (par exemple LangGraph, CrewAI, les Managed Agents d'Anthropic, ou un autre framework que vous connaissez). Notez les garanties de durabilité précises qu'il fournit : qu'est-ce qui est persisté, à quelle fréquence, et comment la reprise est-elle gérée ?
- [ ] Concevez la couche de durabilité d'un agent simple. Écrivez les éléments que vous devriez construire : checkpointing (quoi et quand), reprise (comment et quand), gestion d'erreurs (nouveaux essais, backoff), observabilité (quoi consigner). Estimez combien de lignes de code il faudrait pour le construire et le tester correctement.
- [ ] Demain : esquissez une tâche d'agent hypothétique et estimez ses exigences de déploiement. Une simple boucle plus un fichier de transcript serait-elle acceptable pour votre cas d'usage, ou auriez-vous besoin de durabilité et d'observabilité au niveau d'un framework ? Notez la décision et son raisonnement.

## Pour aller plus loin

- [Billet : "Building Effective Agents", Anthropic Engineering](https://www.anthropic.com/engineering/building-effective-agents)
- [Ressources](../RESOURCES.md)

---

Ça ne passe pas ? Relisez la source primaire en haut de page, car cette leçon la condense et c'est dans la condensation que la compréhension s'échappe. Consultez le [glossaire](../GLOSSARY.md) pour tout terme qui vous a paru glissant.

Si c'est la leçon elle-même qui n'est pas claire plutôt que la matière, c'est un défaut : [ouvrez une issue](https://github.com/TokenCemetery/teach/issues).
