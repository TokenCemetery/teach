---
title: "20. MCP : outils, ressources et prompts"
description: "Le Model Context Protocol comme interface standardisée permettant aux harness d'agents de découvrir et d'invoquer des outils externes, de lire des données et d'utiliser des gabarits"
type: lesson
---

# Leçon 20. MCP : outils, ressources et prompts

**Lien avec la mission :** Comprendre MCP comme un protocole neutre vis-à-vis des fournisseurs qui résout le problème d'intégration, afin de pouvoir raisonner sur les outils auxquels un agent peut accéder et sur la façon d'en ajouter de nouveaux sans réécrire le harness.
**Source primaire :** [Spécification : Model Context Protocol](https://modelcontextprotocol.io/specification)
**Prérequis :** [Leçon 19](0019-coordination-cost.md), [Outil](../GLOSSARY.md)

## Échauffement

1. ▢ Dans la leçon 3, vous avez appris qu'un outil a un nom, une description et un schéma de paramètres. Quand votre harness s'exécute, d'où tire-t-il ces définitions : du modèle, du code du harness, ou d'ailleurs ?

<details markdown="1"><summary>Vérifier</summary>

Du code du harness. L'auteur du harness écrit les définitions d'outils à la main ou les charge depuis un fichier de configuration, puis les présente au modèle avant le début de la boucle.

</details>

2. ▢ Quand vous connectez un agent à une nouvelle source de données (une base de données, une API, un stockage de fichiers), qui fait le travail : le modèle, le harness, ou les deux ?

<details markdown="1"><summary>Vérifier</summary>

Les deux. L'auteur du harness écrit du code pour intégrer la source de données (la récupérer, l'analyser, gérer les erreurs), puis la présente au modèle en ajoutant une définition d'outil. Le modèle décide si et quand l'appeler.

</details>

## À savoir

### Le problème M fois N

Sans standard partagé, connecter un harness d'agent à des outils et à des sources de données externes exige un travail d'intégration sur mesure. Si votre harness peut invoquer N outils ou sources de données différents, et qu'il existe M équipes ou frameworks de construction d'agents différents, vous obtenez M*N intégrations distinctes : chaque équipe écrit du code spécifique pour dialoguer avec chaque outil ou source de données.

MCP (Model Context Protocol) résout cela en créant une interface partagée que le côté harness comme le côté outil peuvent implémenter. Un outil ou une source de données implémente un serveur MCP. N'importe quel harness compatible MCP peut s'y connecter. Un harness implémente un client MCP. N'importe quel serveur compatible MCP peut lui exposer des capacités. On a alors M+N intégrations au lieu de M*N.

Cela compte parce que sans cela, faire utiliser davantage d'outils à un agent signifie une croissance quadratique du code sur mesure. Avec MCP, cela signifie construire des serveurs standard supplémentaires ou s'y connecter.

### Trois primitives

MCP définit trois sortes de capacités qu'un serveur peut exposer à un client :

**Outils** (comparables aux outils de la leçon 3) : des actions que le modèle peut invoquer. Un outil a un nom, une description et un schéma d'entrée. Quand le modèle décide de l'appeler, le client envoie la requête au serveur, qui exécute l'action et renvoie un résultat. Le modèle voit le résultat et continue. C'est exactement comme les outils client et serveur que vous connaissez déjà, mais l'interface est standardisée, de sorte que l'un ou l'autre côté peut être remplacé.

**Ressources** : des données que le client MCP peut lire directement sans que le modèle les invoque comme un appel d'outil. Une ressource peut être un fichier, un enregistrement de base de données, une page web ou une réponse d'API en direct. Le client peut lister les ressources disponibles et en récupérer une par son nom. C'est différent d'un outil parce que le modèle ne l'invoque pas ; le harness la lit et décide s'il faut mettre les données en contexte ou quoi en faire. Les ressources permettent au harness de tirer des informations pertinentes sans bloquer le tour du modèle ni ajouter la surcharge d'un appel d'outil.

**Prompts** (gabarits de prompt) : des gabarits de prompt réutilisables qu'un serveur MCP expose pour qu'un client les remplisse et les utilise. Un gabarit de prompt peut être « analyse ce code à la recherche de problèmes de sécurité » ou « résume ce document ». Le client peut lister les gabarits de prompt disponibles, en récupérer un par son nom et en remplir les paramètres. C'est distinct des outils et des ressources : au lieu d'exécuter une action ou de récupérer des données, le harness utilise le gabarit pour construire un message à envoyer au modèle, en l'intégrant aux propres instructions ou étapes de raisonnement de l'agent.

### Cycle de vie de base

Un client se connecte à un serveur. Ils négocient les capacités : lesquelles parmi les outils, les ressources et les prompts ce serveur particulier prend réellement en charge. Le serveur annonce ce qu'il a ; le client décide de ce qu'il utilise.

Ensuite, selon ce que le client prend en charge et ce dont le harness a besoin :

- Le client peut lister les outils disponibles et récupérer leurs schémas, puis les présenter au modèle.
- Le client peut lister les ressources disponibles et récupérer des données de façon proactive, en se servant de ce qu'il apprend pour éclairer les décisions de l'agent.
- Le client peut lister les gabarits de prompt disponibles et s'en servir pour construire des instructions ou des étapes de réflexion.

Un même serveur peut exposer les trois, ou seulement un ou deux. Le protocole est symétrique : le client comme le serveur connaissent l'interface, donc chaque côté peut être générique.

### Transports

Les serveurs MCP peuvent s'exécuter localement (via stdio, un simple canal de processus à tube entre le harness et le serveur sur la même machine) ou à distance (via un transport basé sur HTTP, où le serveur tourne sur une autre machine ou un service cloud). Le transport affecte la latence, le déploiement et les modes de défaillance, mais pas le protocole lui-même. Un harness qui prend en charge les deux transports peut se connecter à un serveur MCP local pour itérer vite et à un serveur MCP distant pour la résilience ou la collaboration entre équipes.

## Pratique

1. ▢ Vous construisez un agent qui doit lire dans une base de données et appeler une API web. La base de données de votre équipe a un serveur MCP. L'API web n'en a pas. Devez-vous écrire du code d'intégration sur mesure pour les deux, ou pour un seul ?

<details markdown="1"><summary>Vérifier</summary>

Un seul. Le harness peut se connecter au serveur MCP de la base de données sans code sur mesure. Pour l'API web, votre équipe écrit toujours un wrapper (dans le harness ou sous forme d'un nouveau serveur MCP autour de l'API). C'est le principe M+N : le serveur MCP a fait la moitié du travail pour vous.

</details>

2. ▢ Votre agent doit consulter la météo puis décider de suggérer ou non une activité de plein air. Cela doit-il être un outil (que le modèle invoque) ou une ressource (que le harness lit de façon proactive) ?

<details markdown="1"><summary>Indice</summary>

Pensez au moment où le harness apprend la météo et au moment où le modèle a besoin de la connaître. Le modèle décide-t-il de la demander, ou le harness la récupère-t-il toujours ?

</details>

<details markdown="1"><summary>Vérifier</summary>

Cela dépend. Si la météo est toujours pertinente pour la décision, faites-en une ressource : le harness la récupère avant chaque tour et l'inclut en contexte. Si la météo n'est pertinente que lorsque le modèle envisage des activités de plein air, faites-en un outil : le modèle la demande quand il en a besoin. Un outil laisse le modèle décider quand regarder ; une ressource fournit une information que le harness veut toujours que le modèle ait.

</details>

3. ▢ Votre agent utilise trois serveurs MCP : un pour l'e-mail, un pour un calendrier et un pour un stockage de documents. Le serveur d'e-mail prend en charge les outils et les ressources. Le serveur de calendrier ne prend en charge que les outils. Le serveur de documents prend en charge les outils, les ressources et les prompts. Lequel des énoncés suivants le harness peut-il réaliser ?

    - a) Utiliser les ressources des trois serveurs, puisque les trois prennent en charge au moins les outils
    - b) Utiliser les outils des trois, les ressources de l'e-mail et des documents seulement, et les prompts des documents seulement
    - c) Utiliser les prompts des trois serveurs
    - d) Utiliser indifféremment les outils et les ressources de tous les serveurs

<details markdown="1"><summary>Vérifier</summary>

b) Le harness ne peut utiliser que ce que chaque serveur expose réellement. L'e-mail prend en charge les outils et les ressources, donc le harness peut utiliser les deux depuis l'e-mail. Le calendrier ne prend en charge que les outils. Les documents prennent en charge les outils, les ressources et les prompts. Le harness négocie les capacités serveur par serveur et n'appelle que ce qui est annoncé. Les prompts ne sont disponibles que sur le serveur de documents, donc c est faux. Tous les serveurs ne prennent pas en charge les ressources, donc a et d sont faux.

</details>

4. ▢ Vous hésitez à déployer un serveur MCP en local (stdio) ou à distance (HTTP). Quel compromis devez-vous considérer ?

<details markdown="1"><summary>Vérifier</summary>

Le local (stdio) est plus rapide et plus simple à mettre en place sur la même machine, mais couple le harness au processus du serveur. Le distant (HTTP) signifie que le serveur peut tourner n'importe où et survivre aux plantages du harness, mais ajoute de la latence réseau et des modes de défaillance (le serveur peut être lent ou injoignable). Ni l'un ni l'autre ne change le protocole MCP lui-même ; les deux fonctionnent de la même façon pour le client. Choisissez selon la latence que vous pouvez tolérer et selon que vous avez besoin de résilience ou d'un accès entre machines.

</details>

## Exercices en situation réelle

- [ ] Lisez la spécification du Model Context Protocol sur modelcontextprotocol.io et identifiez un serveur MCP qui existe déjà pour quelque chose de votre domaine (e-mail, documents, bases de données, dépôts de code).
- [ ] Esquissez la comparaison M*N contre M+N pour votre propre travail : listez M harness ou équipes et N outils ou sources de données qui vous intéressent, puis estimez combien de code d'intégration sur mesure l'approche M+N économiserait.
- [ ] Demain : essayez de vous connecter à un serveur MCP existant (via un client qui le prend en charge) et observez comment les trois primitives (outils, ressources, prompts) sont réellement utilisées en pratique.

## Pour aller plus loin

- [Spécification : Model Context Protocol](https://modelcontextprotocol.io/specification)
- [Ressources](../RESOURCES.md)

---

Ça ne passe pas ? Relisez la source primaire en haut de page, car cette leçon la condense et c'est dans la condensation que la compréhension s'échappe. Consultez le [glossaire](../GLOSSARY.md) pour tout terme qui vous a paru glissant.

Si c'est la leçon elle-même qui n'est pas claire plutôt que la matière, c'est un défaut : [ouvrez une issue](https://github.com/TokenCemetery/teach/issues).
