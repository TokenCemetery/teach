---
title: "21. Formats des fournisseurs et découverte d'outils à grande échelle"
description: "Pourquoi MCP et les formats de transmission propres à chaque fournisseur sont des couches distinctes, et pourquoi charger tous les outils en contexte ne passe pas à l'échelle avec de nombreux serveurs connectés"
type: lesson
---

# Leçon 21. Formats des fournisseurs et découverte d'outils à grande échelle

**Lien avec la mission :** Comprendre les limites de la découverte naïve d'outils quand un agent se connecte à de nombreux serveurs MCP, et reconnaître quand troquer le chargement anticipé des outils contre une découverte paresseuse ou programmatique.
**Source primaire :** [Billet : "Code Execution with MCP", Anthropic Engineering](https://www.anthropic.com/engineering/code-execution-with-mcp)
**Prérequis :** [Leçon 20](0020-mcp-tools-resources-and-prompts.md)

## Échauffement

1. ▢ Dans la leçon 3, vous avez appris deux formats de transmission : Anthropic représente un appel d'outil avec `input_schema`, et OpenAI utilise une autre forme appelée `function.parameters`. Si vous passez de l'API d'Anthropic à celle d'OpenAI, devez-vous changer votre serveur MCP, votre client MCP, ou les deux ?

<details markdown="1"><summary>Vérifier</summary>

Aucun des deux. Votre serveur MCP reste le même (il sait exposer des outils au format MCP). C'est votre harness qui change, parce qu'il doit traduire les définitions d'outils MCP dans le format de transmission du fournisseur que le modèle attend. Le fournisseur du modèle change, mais le protocole MCP non.

</details>

2. ▢ Dans la leçon 9, vous avez découvert la surcharge du jeu d'outils : si vous présentez trop de définitions d'outils au modèle, il ralentit, se perd ou oublie quel outil utiliser. Quand un agent se connecte à cinq serveurs MCP de dix outils chacun, le modèle voit-il d'emblée cinquante définitions d'outils ?

<details markdown="1"><summary>Vérifier</summary>

Seulement si le harness charge les cinquante définitions en contexte avant le début de la boucle. C'est l'approche naïve. Mais il existe d'autres façons : le harness pourrait ne charger les outils que lorsque le modèle les demande, ou traduire les définitions d'outils en code que le modèle peut explorer et appeler de façon programmatique.

</details>

## À savoir

### Deux couches indépendantes

MCP est un protocole entre un harness d'agent et des outils ou sources de données externes. Il définit comment un client et un serveur dialoguent et quelles capacités un serveur peut exposer. Mais MCP ne se soucie pas du format de transmission que le modèle utilise.

En même temps, le modèle a un fournisseur, et ce fournisseur a une façon précise de représenter les appels d'outils. L'API d'Anthropic accepte les outils sous une forme. L'API d'OpenAI les accepte sous une autre. Ce format de transmission est une couche distincte entre le harness et le modèle.

Ces deux couches sont indépendantes :

- Le client MCP (côté harness) parle MCP au serveur MCP. Le serveur MCP ne sait pas quel modèle utilisera finalement ces outils.
- Le harness traduit ensuite les définitions d'outils MCP dans le format de transmission du fournisseur que le modèle attend. Anthropic ? Utiliser `input_schema`. OpenAI ? Utiliser `function.parameters`.

Le harness doit faire la traduction, parce qu'il se trouve au milieu. Mais changer une couche n'oblige pas à réécrire l'autre. Si vous changez de fournisseur de modèle, vous ne réécrivez pas vos serveurs MCP. Si vous vous connectez à un nouveau serveur MCP, le format de transmission entre le harness et le modèle ne change pas.

### La découverte d'outils à grande échelle

Sur un seul agent, vous pouvez câbler à la main deux ou trois outils dans le contexte au démarrage. La surcharge du jeu d'outils (leçon 9) s'installe autour de cinq à dix outils. Mais que se passe-t-il si le harness est connecté à une douzaine de serveurs MCP, chacun avec dix à vingt outils ? Des centaines de définitions d'outils.

L'approche naïve consiste à charger toutes les définitions d'outils au démarrage, à traduire chacune dans le format de transmission du fournisseur et à toutes les remettre au modèle dans son contexte initial. Cela reproduit la surcharge du jeu d'outils à bien plus grande échelle. Le modèle lit des centaines de définitions, gaspille des tokens sur des descriptions dont il n'a pas besoin, et ralentit à chaque tour parce que chaque outil est en contexte. Et si un nouvel outil est ajouté à un serveur connecté, tout le contexte et le comportement du modèle changent.

C'est le problème de la découverte d'outils à grande échelle : on peut se connecter à de nombreux serveurs, mais pas en chargeant tout d'emblée.

### L'idée de l'exécution de code

Le billet d'Anthropic Engineering « Code Execution with MCP » propose une solution : au lieu de charger les définitions d'outils en contexte, présenter les outils disponibles comme du code que l'agent peut découvrir et appeler de façon programmatique.

Par exemple :

- Le harness définit une fonction utilitaire list_available_tools() qui interroge les serveurs MCP connectés et renvoie un répertoire de fonctions appelables : leurs noms, descriptions et paramètres.
- Le harness définit une fonction utilitaire call_tool(name, args) qui prend un nom d'outil et des arguments, trouve l'outil sur les serveurs connectés et l'invoque.
- Au lieu de donner d'emblée cinquante définitions d'outils au modèle, le harness lui dit : « Vous pouvez appeler list_available_tools() pour voir ce que vous pouvez faire, ou call_tool(name, args) pour faire quelque chose de précis. »

Le modèle a maintenant deux méta-outils : des outils pour découvrir et appeler d'autres outils. Il peut explorer l'espace des outils sans charger toutes les définitions en contexte au départ. Il appelle list_available_tools() quand il a besoin de trouver un outil, apprend ce qui est disponible à ce moment-là, puis utilise ce dont il a besoin. Le contexte résident reste petit.

Cela troque le chargement anticipé contre la découverte paresseuse. Le modèle doit dépenser un tour à appeler list_available_tools() avant de pouvoir appeler un outil précis, donc il y a un coût de latence. Mais si le harness est connecté à cinquante serveurs, les tokens économisés en ne gardant pas chaque définition d'outil en contexte l'emportent sur le coût du tour supplémentaire.

### Quand utiliser chaque approche

Le chargement anticipé (mettre chaque outil en contexte au démarrage) fonctionne quand :

- Vous avez un petit ensemble fixe d'outils (deux à dix).
- Les outils sont pertinents pour chaque tâche de l'agent.
- Le contexte n'est pas contraint.

Le chargement paresseux (définir list_available_tools() et call_tool() et laisser le modèle découvrir ce dont il a besoin) fonctionne quand :

- Vous avez beaucoup d'outils (des dizaines ou plus).
- Les outils sont spécialisés et ne sont pas tous pertinents pour chaque tâche.
- Le contexte est contraint et chaque token compte.
- Le coût de latence d'un tour supplémentaire est acceptable.

La découverte programmatique (présenter les outils comme du code que le modèle peut lire et exécuter) combine les deux idées : un petit contexte initial (juste les fonctions de découverte) et la capacité d'explorer l'espace des outils sans charger les définitions à la main.

## Pratique

1. ▢ Vous utilisez l'API d'Anthropic avec trois serveurs MCP. Vous passez à l'API d'OpenAI. Devez-vous mettre à jour vos serveurs MCP, votre harness, ou les deux ?

<details markdown="1"><summary>Vérifier</summary>

Seulement votre harness. Les serveurs MCP ne changent pas ; ils exposent toujours des outils au format MCP. Votre harness traduisait déjà les définitions MCP vers le format de transmission d'Anthropic ; il les traduit maintenant vers celui d'OpenAI. La couche de traduction change, mais les serveurs et le protocole non.

</details>

2. ▢ Votre agent est connecté à dix serveurs MCP pour un total de cent cinquante outils. Vous voulez appliquer l'idée de « l'exécution de code avec MCP » : définir list_available_tools() et laisser le modèle découvrir ce dont il a besoin. Quelles sont deux conséquences de cette conception ?

<details markdown="1"><summary>Indice</summary>

Pensez à la taille du contexte et à la latence. Quand le modèle demande-t-il la liste ? Combien cela coûte-t-il ?

</details>

<details markdown="1"><summary>Vérifier</summary>

Le contexte est plus petit parce que vous ne chargez pas d'emblée cent cinquante définitions d'outils, seulement deux fonctions et peut-être une brève description de ce qu'elles font. La latence augmente parce que le modèle doit appeler list_available_tools() à un tour où il veut explorer, ce qui ajoute au moins un tour supplémentaire avant de pouvoir appeler un outil précis. C'est un compromis valable si le contexte est serré ou si les outils sont rarement tous nécessaires ensemble.

</details>

3. ▢ Votre harness n'a que trois outils, et ils sont tous pertinents pour chaque tâche que l'agent effectue. Faut-il utiliser le chargement anticipé, le chargement paresseux ou la découverte programmatique ?

    - a) Le chargement paresseux avec list_available_tools()
    - b) Le chargement anticipé : mettre les trois en contexte au départ
    - c) La découverte programmatique avec des fonctions call_tool()
    - d) Faire tourner les outils présents en contexte pour économiser des tokens

<details markdown="1"><summary>Vérifier</summary>

b) Avec un petit ensemble d'outils toujours pertinents, le chargement anticipé est le plus simple et le plus rapide. Vous ne gaspillez aucun token sur des fonctions de découverte, vous n'ajoutez aucune latence, et le modèle a toujours les outils dont il a besoin. Le chargement paresseux et la découverte programmatique ajoutent de la surcharge sans bénéfice quand le jeu d'outils est petit et universel. L'option d est un anti-schéma : faire entrer et sortir des outils du contexte crée de la confusion et du non-déterminisme.

</details>

4. ▢ Vous définissez list_available_tools() pour interroger tous les serveurs MCP connectés et renvoyer leurs noms et descriptions d'outils. Quand le modèle appelle cette fonction, l'appel compte-t-il dans vos tokens d'API ?

<details markdown="1"><summary>Vérifier</summary>

Oui. Appeler list_available_tools() coûte des tokens comme n'importe quelle autre fonction : le modèle envoie l'appel, le harness l'exécute, et le résultat revient dans le transcript. Vous arbitrez entre les tokens dépensés en définitions d'outils initiales et les tokens dépensés en appels de découverte. Avec beaucoup d'outils, le compromis est généralement positif.

</details>

## Exercices en situation réelle

- [ ] Dessinez un schéma montrant les deux couches : le protocole MCP d'un côté (harness vers serveurs externes), le format de transmission du fournisseur de l'autre (harness vers modèle). Indiquez ce qui se passe si vous changez de fournisseur par rapport à si vous changez de serveurs MCP.
- [ ] Estimez la différence de coût en tokens entre le chargement anticipé (mettre cent outils en contexte) et le chargement paresseux (list_available_tools() à la demande) pour votre propre agent. La paresse a-t-elle du sens ?
- [ ] Demain : implémentez une fonction list_available_tools() simple qui interroge un vrai serveur MCP auquel vous avez accès et renvoie un résumé que le modèle peut lire.

## Pour aller plus loin

- [Billet : "Code Execution with MCP", Anthropic Engineering](https://www.anthropic.com/engineering/code-execution-with-mcp)
- [Spécification : Model Context Protocol](https://modelcontextprotocol.io/specification)
- [Ressources](../RESOURCES.md)

---

Ça ne passe pas ? Relisez la source primaire en haut de page, car cette leçon la condense et c'est dans la condensation que la compréhension s'échappe. Consultez le [glossaire](../GLOSSARY.md) pour tout terme qui vous a paru glissant.

Si c'est la leçon elle-même qui n'est pas claire plutôt que la matière, c'est un défaut : [ouvrez une issue](https://github.com/TokenCemetery/teach/issues).
