---
title: "37. Relire la conception d'agent de quelqu'un d'autre"
description: "Comment évaluer méthodiquement un système d'agents, et comment trancher une affirmation contestée en revenant à la source primaire"
type: lesson
---

# Leçon 37. Relire la conception d'agent de quelqu'un d'autre

**Lien avec la mission :** Qu'on vous fasse confiance pour relire la conception d'agent de quelqu'un d'autre et trancher les affirmations contestées à son sujet en consultant les sources primaires, sans choisir un camp par défaut ni couper la poire en deux de façon vague.
**Source primaire :** [Billet : "Building Effective Agents", Anthropic Engineering](https://www.anthropic.com/engineering/building-effective-agents)
**Prérequis :** [Leçon 36](0036-when-not-to-build-an-agent.md)

## Échauffement

1. ▢ Que teste le spectre d'autonomie de la leçon 2 pour distinguer un workflow d'un agent ?

<details markdown="1"><summary>Vérifier</summary>

Si le flux de contrôle est décidé à l'avance par le développeur, ou décidé à l'exécution par le modèle. Ni le nombre d'outils, ni la complexité, ni le nombre d'appels au modèle, mais qui a choisi le chemin.

</details>

2. ▢ Depuis la leçon 35, citez une façon dont un framework peut réduire le coût d'exécution d'un agent en production par rapport à l'écriture du harness à partir de zéro.

<details markdown="1"><summary>Vérifier</summary>

Mettre en cache le contexte stable (définitions d'outils, system prompt) pour que les tâches répétées ne renvoient pas ces tokens, mettre en œuvre un état durable pour qu'une exécution interrompue puisse reprendre, fournir du traçage et une gestion d'erreurs intégrés qui prendraient du temps à câbler à la main. Le framework achète du temps pour atteindre la fiabilité et une réduction de coût au détriment de la flexibilité ou au prix d'un enfermement chez un fournisseur.

</details>

## À savoir

### La liste de contrôle de relecture : les étapes dans l'ordre

Quand vous relisez une conception d'agent proposée ou existante, parcourez-la selon les étapes de ce parcours dans l'ordre, en posant la même question à chaque étape : ce choix est-il justifié, et est-il documenté ?

#### Étapes 1 et 2 : spectre d'autonomie et flux de contrôle

Où ce système se situe-t-il sur le spectre d'autonomie ? Est-ce un prompt unique, un workflow fixé par le développeur ou un agent dirigé par le modèle ? Cherchez l'affirmation dans la proposition ou la documentation. Si l'affirmation se limite à « ceci est un agent » sans expliquer pourquoi l'autonomie est nécessaire, demandez ce que l'alternative à chemin fixe aurait coûté. Une bonne conception ne se contente pas de nommer le choix ; elle le défend.

#### Étapes 3 et 4 : surface d'outils et schéma

Les outils sont-ils nommés et décrits de façon que le raisonnement d'un modèle les trouve utiles ? La leçon 8 a enseigné que les descriptions d'outils sont de la surface de prompt, pas de la documentation d'API. Les noms d'outils doivent décrire ce que fait l'outil du point de vue du modèle, pas l'endpoint sous-jacent. Les descriptions de paramètres doivent aider le modèle à décider quoi passer, pas seulement documenter le schéma technique. Le jeu d'outils est-il resserré (en évitant la surcharge de la leçon 9), ou a-t-il accumulé des outils rarement utilisés ?

#### Étapes 5 et 6 : stratégie de contexte et de mémoire

Pour une tâche de longue durée, quelle est la stratégie ? La conception distingue-t-elle le scratchpad (le transcript courant au sein d'une exécution) de la mémoire entre exécutions (faits persistés d'une exécution à l'autre) ? La leçon 11 a enseigné la compaction ; la conception a-t-elle un plan pour raccourcir le transcript à mesure qu'il grandit ? Si la tâche implique d'apprendre des faits et de les reporter, un mécanisme de mémoire est-il nommé, ou la conception s'appuie-t-elle sur le seul transcript ?

#### Étape 7 : réflexion et nouveaux essais

Quand une étape échoue, la conception prévoit-elle un nouvel essai, et inclut-elle une réflexion explicite (l'agent qui raisonne en langage naturel sur la raison de l'échec avant de réessayer) ? Ou se contente-t-elle de boucler en espérant que le modèle se corrige tout seul ? La leçon 17 a enseigné que le silence n'équivaut pas à apprendre ; un agent bien conçu réfléchit après un échec.

#### Étape 8 : décision multi-agent

Si la conception est multi-agent, justifie-t-elle ce choix face à l'alternative à agent unique ? La leçon 19 a enseigné le coût de coordination : un système orchestrateur et worker multiplie les tokens et fragmente le contexte entre les workers. La conception doit nommer le bénéfice précis qui justifie ce coût. Le bénéfice est-il le parallélisme (temps réel), l'isolation du contexte (le transcript de chaque worker reste propre) ou une véritable indépendance des sous-tâches ? Et ce bénéfice s'applique-t-il à cette tâche précise ?

#### Étape 14 : sécurité et triade

L'agent lit-il du contenu non fiable ? Accède-t-il à des données privées ? A-t-il une communication externe ? La leçon 31 a enseigné que ces trois conditions réunies le rendent exploitable. La conception doit nommer quelles conditions sont présentes et lesquelles ne le sont pas, ou comment elle en retire délibérément au moins une. Si la conception a les trois sans le reconnaître, c'est un signal d'alerte.

#### Étape 15 : coût et durabilité

Quelqu'un a-t-il estimé le coût en tokens par tâche terminée ? Ce coût est-il acceptable ? Si le système utilise un framework, le choix du framework est-il justifié, ou a-t-il été retenu par défaut ? La leçon 33 a enseigné que le coût réel par tâche inclut les nouveaux essais et l'amplification de tokens. Une bonne conception nomme une estimation de coût, même approximative.

### La compétence précise : trancher une affirmation contestée à partir de la source primaire

Ce parcours vous a présenté deux récits crédibles et opposés sur les systèmes multi-agents. La leçon 18 a décrit les schémas orchestrateur et worker et leurs bénéfices. La leçon 19 a présenté l'argument de Cognition selon lequel la plupart des systèmes multi-agents ne valent pas leur coût, et selon lequel un agent unique avec de meilleurs outils l'emporte souvent.

Les deux récits sont justes dans leur propre domaine. Un relecteur qui ne se souvient qu'à moitié des deux risque de choisir un camp par réflexe (« j'ai lu que les agents uniques sont toujours meilleurs, donc cette conception multi-agent est mauvaise ») ou de couper la poire en deux de façon vague (« le multi-agent est parfois bon »). Ni l'un ni l'autre ne fait avancer la conversation.

La vraie compétence consiste à retourner aux sources primaires et à vérifier si les circonstances précises de la conception correspondent aux conditions dans lesquelles l'argument de cette source tient.

Le billet d'Anthropic « How We Built Our Multi-Agent Research System » décrit un système multi-agent qui a fonctionné. Les conditions qui l'ont fait fonctionner, d'après la lecture de cet article, comprennent : les sous-tâches étaient réellement indépendantes (chaque chercheur se concentrait sur un angle distinct), le parallélisme apportait un vrai bénéfice en temps réel (les résultats devaient être synthétisés sous pression temporelle), et l'équipe a beaucoup investi dans l'orchestration pour garder la communication propre entre les workers.

Le billet de Cognition « Don't Build Multi-Agents » soutient que le coût n'en vaut pas la peine pour la plupart des tâches. Les conditions qui rendent leur argument le plus fort comprennent : quand les sous-tâches partagent du contexte ou s'affinent mutuellement, quand vous avez du temps et du budget de contexte pour qu'un agent unique explore des chemins en série, et quand la surcharge de coordination est élevée par rapport au problème.

Vous relisez maintenant une conception. La proposition dit : « Nous construisons un système de recherche avec un orchestrateur et trois workers chercheurs en parallèle. » Avant d'accepter ou de rejeter le multi-agent, demandez :

- Les trois angles de recherche sont-ils réellement indépendants, ou partagent-ils du contexte et s'affinent-ils mutuellement ?
- Y a-t-il une vraie échéance en temps réel, ou avez-vous le temps de faire explorer les trois angles en série par un seul agent ?
- L'équipe a-t-elle budgété le travail d'orchestration, ou la coordination est-elle une pensée après coup ?
- Que coûterait en tokens un agent unique avec des outils plus larges par rapport au système multi-agent ?

Les circonstances réelles de la conception déterminent l'argument de quelle source s'applique. Le travail d'un relecteur n'est pas d'arbitrer entre les deux sources, mais de vérifier si la situation de la conception correspond aux conditions où l'argument d'une source devient plus fort ou plus faible. Si la conception n'a pas de réponse à ces questions, elle n'a pas encore tranché la question à partir de la source primaire ; elle n'a fait qu'affirmer le choix.

### Ce qu'accomplit une bonne relecture de conception

Une bonne relecture ne dit pas « c'est bien » ou « c'est mal ». Elle dit :

« Cette conception choisit X parce que Y. J'ai rattaché ce choix à l'étape Z du parcours, où ces questions s'appliquent. La conception répond clairement à celles-ci et laisse celles-là ouvertes. Avant de s'engager, l'équipe devrait résoudre les questions ouvertes ou documenter les risques. »

Une relecture qui nomme des questions précises sans réponse est plus utile qu'une relecture qui prononce un verdict de réussite ou d'échec. Elle donne à l'équipe quelque chose à faire. Elle vous donne aussi un levier : vous pouvez poser des questions de suivi par écrit et tenir la conception responsable d'affirmations précises, plutôt que de seulement exprimer du scepticisme.

## Pratique

1. ▢ Vous relisez la conception d'un agent qui traite des documents financiers. La conception dit que l'agent aura accès à : un outil pour lire des documents depuis un stockage cloud, un outil pour interroger une base de données clients et obtenir l'historique des transactions, et un outil pour déposer des rapports dans un journal d'audit. La conception ne parle pas de sécurité. En utilisant le cadre de la leçon 31, quelles questions devriez-vous poser ?

<details markdown="1"><summary>Vérifier</summary>

Les trois conditions de la triade létale sont présentes : l'agent lit du contenu non fiable (documents financiers téléversés), accède à des données privées (historique des transactions des clients) et peut communiquer vers l'extérieur (déposer des rapports d'audit). Une bonne relecture demande : les trois conditions de la triade sont-elles nécessaires ? La conception peut-elle en retirer au moins une ? Par exemple, l'agent peut-il lire des documents sans déposer directement des rapports, en rédigeant plutôt des rapports soumis à l'approbation d'un humain ? Ou peut-il éviter de toucher à la base de données clients en ne travaillant que sur des données de synthèse ? La conception devrait soit justifier pourquoi les trois sont nécessaires, soit documenter les contrôles de sécurité précis (points d'approbation, journalisation d'audit, sandboxing) qui atténuent le risque.

</details>

2. ▢ Une conception propose un orchestrateur avec deux workers parallèles : l'un étudie les produits concurrents, l'autre étudie les besoins des clients. Les workers rapportent ensuite leurs constats à un analyste humain qui les synthétise. Vous soupçonnez que l'alternative à agent unique pourrait être moins chère. Quelle question de la leçon 19 devriez-vous poser pour tester ce soupçon ?

<details markdown="1"><summary>Indice</summary>

Pensez à ce que fait l'orchestrateur dans cette conception, et à s'il existe une tâche que l'agent unique ne saurait pas faire aussi bien ou aussi vite.

</details>

<details markdown="1"><summary>Vérifier</summary>

Estimez le coût en tokens : deux agents workers plus la surcharge de l'orchestrateur, comparés à un agent qui étudie les deux angles en série. Les deux workers parallèles terminent-ils plus vite qu'un agent en série (bénéfice du parallélisme) ? Ou l'agent unique, qui garde les deux fils de recherche dans un seul transcript, les intègre-t-il plus efficacement (bénéfice de cohérence du contexte) ? Si les workers terminent plus vite mais que le multiplicateur de coût en tokens est élevé, et que l'analyste humain n'est pas contraint par le temps, l'agent unique gagne. Si les chercheurs ont besoin de résultats urgents et que le parallélisme fait gagner des heures, le multi-agent justifie le coût. La conception aurait dû faire ce calcul ; si elle ne l'a pas fait, vous avez trouvé une question ouverte.

</details>

3. ▢ Vous relisez la définition d'un outil pour un agent. L'outil s'appelle query_customer_database et sa description est : « Connect to the customer database and execute any SQL query provided by the user. »

    - a) C'est un outil bien conçu parce qu'il est maximalement flexible
    - b) Cet outil viole le moindre privilège ; il devrait être reconçu pour n'exécuter que des requêtes précises et préalablement autorisées
    - c) Cet outil est acceptable parce que l'agent n'en abusera pas si le system prompt le lui interdit
    - d) Cet outil est acceptable tant que l'agent n'a aucune capacité de communication externe

<details markdown="1"><summary>Vérifier</summary>

**b)** Cet outil viole le moindre privilège et devrait être reconçu. Il accorde à l'agent un accès large à la base de données, ce qui viole le principe de la leçon 32 selon lequel chaque outil doit se limiter exactement à ce dont il a besoin. L'option (a) est fausse : la flexibilité pour le développeur n'est pas la même chose qu'une bonne conception d'outil. L'option (c) est fausse : la leçon 31 a enseigné que les instructions de prompt ne sont pas une défense fiable contre l'injection de prompt ; la défense est architecturale. L'option (d) est fausse : retirer la communication externe briserait une condition de la triade, mais l'outil resterait surdimensionné par rapport à ce dont un agent a réellement besoin. Une meilleure conception : un outil appelé get_customer_orders qui prend un customer_id et renvoie ses commandes, sans aucun vecteur d'injection SQL.

</details>

4. ▢ Une équipe relit deux propositions pour la même tâche. Proposition A : un agent unique avec accès à la recherche web, à l'exécution de code et à des outils de documentation. Proposition B : un orchestrateur avec trois workers (spécialiste de la recherche, spécialiste du code, spécialiste de la documentation), chacun avec un seul outil. L'équipe a lu la leçon 19 et est divisée. Deux ingénieurs soutiennent que la proposition A est meilleure parce que « Cognition dit que les agents uniques gagnent ». Deux soutiennent que la proposition B est meilleure parce que « le système de recherche d'Anthropic était multi-agent ». On vous demande de trancher. Quelle devrait être votre première étape ?

<details markdown="1"><summary>Vérifier</summary>

Retourner aux sources primaires, pas aux résumés à moitié mémorisés. Relisez les deux articles et identifiez les conditions précises que chacun décrit : quelles étaient les caractéristiques de la tâche, du budget de contexte, de la pression temporelle et de la complexité de coordination dans chaque source ? Examinez ensuite la proposition A et la proposition B par rapport à ces conditions. Correspondent-elles mieux aux conditions de l'agent unique ou du multi-agent ? Les propositions décrivent-elles elles-mêmes les caractéristiques de la tâche et justifient-elles leur choix par rapport à ces conditions ? Votre relecture devrait dire quelque chose comme : « La proposition B correspond aux conditions où le système de recherche d'Anthropic a réussi (sous-tâches indépendantes, échéance en temps réel), si elle peut justifier le coût de coordination. La proposition A correspond au scénario de Cognition (travail d'affinage de contexte, budget de temps ouvert), si le menu d'outils de l'agent unique est assez large pour éviter la surcharge de décision d'outils. » Le travail n'est pas d'arbitrer entre les sources mais d'appliquer chacune à la tâche précise.

</details>

## Exercices en situation réelle

- [ ] Trouvez un système que vous utilisez ou connaissez et qui se décrit comme un agent. Essayez de le confronter à la liste de contrôle de cette leçon : où se situe-t-il sur le spectre d'autonomie ? Les outils sont-ils décrits pour le raisonnement du modèle ou comme de la documentation d'API ? Parle-t-il de sécurité ? Notez les points de la liste que le système traite clairement et ceux sur lesquels il reste silencieux.
- [ ] Choisissez une affirmation de la leçon 19 que Cognition ou Anthropic fait sur les systèmes multi-agents. Relisez la source et identifiez les conditions précises dans lesquelles cette affirmation tient. Notez : quelles caractéristiques de la tâche rendent l'affirmation vraie ou fausse ? Comment testeriez-vous cette affirmation sur un système que vous concevez ?
- [ ] Demain : relisez la conception d'agent de quelqu'un d'autre (issue du travail, d'un projet open source ou d'une proposition technique). Utilisez la liste de contrôle de cette leçon. Notez une question ouverte pour chaque étape que la conception ne traite pas pleinement. Partagez la relecture avec l'auteur de la conception et voyez si vos questions rejoignent ses propres préoccupations.

## Pour aller plus loin

- [Billet : "Building Effective Agents", Anthropic Engineering](https://www.anthropic.com/engineering/building-effective-agents)
- [Ressources](../RESOURCES.md)

---

Ça ne passe pas ? Relisez la source primaire en haut de page, car cette leçon la condense et c'est dans la condensation que la compréhension s'échappe. Consultez le [glossaire](../GLOSSARY.md) pour tout terme qui vous a paru glissant.

Si c'est la leçon elle-même qui n'est pas claire plutôt que la matière, c'est un défaut : [ouvrez une issue](https://github.com/TokenCemetery/teach/issues).
