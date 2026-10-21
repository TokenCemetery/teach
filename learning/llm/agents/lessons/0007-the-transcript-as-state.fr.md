---
title: "7. Le transcript comme état"
description: "Comprendre que le transcript est la seule mémoire persistante de l'agent entre les tours"
type: lesson
---

# Leçon 7. Le transcript comme état

**Lien avec la mission :** Reconnaître le transcript comme l'unique état de l'agent aide à diagnostiquer un agent défaillant à partir de sa trajectoire au lieu de deviner pourquoi le modèle est perdu ou répétitif, ce qui sert la mission « diagnostiquer un agent défaillant à partir de sa trajectoire ».
**Source primaire :** [Billet : "Building Effective Agents", Anthropic Engineering](https://www.anthropic.com/engineering/building-effective-agents)
**Prérequis :** [Leçon 6](0006-writing-the-loop.md), [Trajectoire](../GLOSSARY.md)

## Échauffement

1. ▢ Depuis la leçon 6 : une fois que le harness a appelé le modèle et reçu une réponse, que doit-il se passer avant que le harness n'exécute le moindre appel d'outil ?

<details markdown="1"><summary>Vérifier</summary>

La réponse doit être ajoutée immédiatement au transcript, avant l'exécution de tout outil. Sinon la demande du modèle lui-même n'est jamais enregistrée, et un tour ultérieur ne montrera pas pourquoi un résultat d'outil est présent.

</details>

2. ▢ Depuis la leçon 6 : nommez deux conditions d'arrêt différentes qu'un harness peut vérifier pour mettre fin à la boucle d'agent.

<details markdown="1"><summary>Vérifier</summary>

Deux au choix parmi : le modèle renvoie un tour sans appel d'outil, une limite de nombre maximal de tours ou de budget de tokens est atteinte, le modèle appelle un outil d'arrêt explicite, ou un seuil de nombre d'erreurs est dépassé.

</details>

## À savoir

### Seul le transcript persiste

Entre un appel au modèle et le suivant, le harness conserve deux choses :

1. Le transcript : l'historique complet de la conversation, y compris chaque réponse du modèle, chaque appel d'outil et chaque résultat d'outil.
2. Les métadonnées du harness : compteurs (nombre de tours, nombre d'erreurs), limites (nombre maximal de tours, nombre maximal d'erreurs), enregistrements d'outils, configuration.

Le modèle ne voit pas les métadonnées du harness. Le modèle ne voit que le transcript. Si un fait n'est pas dans le transcript, le modèle ne sait pas qu'il s'est produit.

C'est à la fois simple et profond. Cela signifie que :

- Le modèle ne peut pas raisonner sur ce que le harness a décidé en interne, à moins que le harness ne le mette dans le transcript.
- Entre les tours, rien d'autre ne persiste. Pas de drapeaux internes, pas d'état caché, pas de variables en dehors des métadonnées du harness.
- Rejouer une exécution d'agent revient à renvoyer le même transcript au modèle et à continuer à partir de là.

### La trajectoire diverge du transcript

Une trajectoire est l'enregistrement complet de ce qui s'est passé : chaque tour, décision, log et effet de bord. Un transcript est ce qui a été montré au modèle. Ce n'est pas la même chose.

Par exemple :

- Le harness exécute un appel d'outil, obtient un résultat de 100 Ko, mais juge le résultat trop long et le tronque avant de l'ajouter au transcript. La trajectoire dit « l'appel d'outil a réussi, le résultat faisait 100 Ko » ; le transcript dit « l'appel d'outil a réussi, le résultat était les 10 premiers Ko ». Le modèle ne connaît que la seconde version.
- Le harness décide de réessayer un outil parce que la première tentative a échoué. Le journal de décision va dans un fichier pour qu'un humain le débogue plus tard. Mais le harness n'ajoute jamais « je vais réessayer » au transcript. Au tour suivant, le modèle ne sait pas qu'un nouvel essai a eu lieu ; il ne voit que les résultats.
- Un appel d'outil échoue silencieusement. Le harness le consigne mais n'ajoute aucun message d'erreur au transcript parce que le concepteur du harness l'a oublié. Le modèle n'apprend jamais que l'outil a échoué. Au tour suivant, le modèle risque de redemander le même outil, perplexe de ne pas l'avoir vu fonctionner.

La conséquence est qu'en regardant une trajectoire vous pouvez conclure « le harness a pris une décision sensée », alors que si vous ne regardez que le transcript, vous voyez un modèle perdu. Le modèle n'est pas perdu. On ne lui a simplement rien dit.

### Un exemple détaillé : le résultat d'outil qui n'a jamais existé

Imaginez ce scénario :

L'agent doit chercher un prix, appliquer une remise, puis confirmer. Au tour deux, le modèle appelle un outil pour récupérer le prix. L'outil renvoie « Item XYZ costs $100 ». Le harness exécute l'outil, obtient le résultat et l'ajoute au transcript :

```text
Agent turn 1: "I will find the price of item XYZ"
Agent turn 1 tool call: fetch_price(item="XYZ")
Tool result: "Item XYZ costs $100"

Agent turn 2: "I will apply a 10% discount. $100 - 10% = $90."
Agent turn 2 tool call: confirm_price(item="XYZ", price="$90")
```

Cela fonctionne. Le modèle a vu le résultat et a raisonné correctement.

Imaginez maintenant une variante : le harness consigne les résultats dans une base de données pour la supervision. L'insertion dans le log échoue. Le harness consigne l'erreur dans un fichier, mais le développeur n'a jamais rien ajouté au transcript. Le tour suivant commence ainsi :

```text
Agent turn 1: "I will find the price of item XYZ"
Agent turn 1 tool call: fetch_price(item="XYZ")

Agent turn 2: "I need to fetch the price. Let me call fetch_price again."
Agent turn 2 tool call: fetch_price(item="XYZ")
```

Le modèle redemande le prix. Il n'est ni têtu ni stupide. Le transcript ne montre jamais le résultat du tour un. Le modèle n'a aucun moyen de savoir que l'appel a réussi. C'est ce qu'on appelle une divergence : la trajectoire dit « le résultat a été obtenu et consigné », mais le transcript dit « rien ne s'est passé ».

La correction consiste à toujours ajouter au transcript avant de continuer, même si les effets de bord échouent :

```text
Tool result (appended immediately): "Item XYZ costs $100"

[Later, harness logs to database, but the append already happened]
Log to database failed [this error never goes in the transcript]
```

Maintenant le modèle sait que le résultat existe, quelles que soient les erreurs en aval.

### Pourquoi le transcript comme état facilite la reprise

Supposons qu'une exécution d'agent soit interrompue. Le harness plante, le réseau tombe, le quota est atteint. Vous voulez reprendre l'agent là où il s'est arrêté.

Si l'agent stocke son état dans des variables internes, des drapeaux et des décisions éparpillées dans le harness, la reprise est difficile. Il faut sauvegarder tout cet état, le restaurer, et espérer ne rien avoir oublié.

Si l'état de l'agent n'est que le transcript, la reprise est triviale : sauvegarder le transcript, puis démarrer une nouvelle exécution en renvoyant le même transcript au modèle et en continuant la boucle à partir du tour suivant. Le modèle verra tout ce qu'il avait vu avant, et continuera à raisonner. Pas d'état caché à reconstruire, pas de drapeaux à restaurer, pas de variables à suivre. Le transcript est le contrat.

De même, vous pouvez rejouer une exécution d'agent pour la déboguer. Renvoyez la trajectoire (le log complet de ce qui s'est passé) comme transcript, et voyez ce que le modèle ferait ensuite. Vous pouvez même modifier le transcript à la main pour tester ce que le modèle ferait dans une situation hypothétique.

## Pratique

1. ▢ Un agent est censé chercher un document, le lire et le résumer. Au tour deux, il appelle un outil de recherche et l'outil renvoie 10 résultats. Avant d'ajouter le résultat au transcript, le harness filtre les résultats pour ne garder que les trois plus pertinents et n'ajoute que ceux-là. Que voit le modèle, et pourquoi ce choix de conception est-il visible quand vous lisez le transcript ?

<details markdown="1"><summary>Vérifier</summary>

Le modèle voit trois résultats, pas dix. Il ne sait pas que le harness a filtré ; il ne connaît que ce qui est dans le transcript. C'est une conception acceptable si elle est intentionnelle : le harness a choisi de réduire l'usage de tokens en filtrant. L'essentiel est qu'en lisant le transcript, vous voyez exactement ce que le modèle a vu (trois résultats) et pouvez juger si sa décision suivante était sensée compte tenu de cette information. Le fait que dix résultats aient existé ne vous perturbe pas ; le transcript montre le monde du point de vue du modèle.

</details>

2. ▢ Un développeur de harness veut consigner quels outils ont été appelés et combien de fois. Doit-il stocker ce compte dans une variable réservée au harness, ou ajouter un résumé au transcript avant chaque appel du modèle ?

<details markdown="1"><summary>Indice</summary>

Pensez à ce que le modèle a besoin de savoir pour décider, et à quelle information ne servirait qu'au débogage après l'exécution par un humain.

</details>

<details markdown="1"><summary>Vérifier</summary>

Cela dépend du cas d'usage. Si le modèle a besoin de savoir « vous avez déjà appelé la recherche trois fois, essayez peut-être un autre outil », alors le compte doit aller dans le transcript. Si le compte ne sert qu'à la supervision et que le modèle n'a pas besoin d'ajuster son comportement en fonction de lui, une variable réservée au harness suffit. Mais si le modèle peut tirer profit de connaître le compte, mettez-le dans le transcript pour qu'il le voie au tour suivant. Un bon réglage par défaut est d'ajouter tout ce qui peut influer sur la prochaine décision du modèle.

</details>

3. ▢ Vous déboguez une exécution d'agent. Vous lisez la trajectoire et voyez qu'un appel d'outil a réussi et que le résultat a été ajouté. Vous lisez le transcript que le modèle a réellement vu et le résultat n'y est pas. Que s'est-il passé ?

    - a) Le harness a ajouté le résultat, puis l'a retiré du transcript avant de rappeler le modèle
    - b) La trajectoire et le transcript sont censés être différents ; le transcript est un résumé et la trajectoire est complète
    - c) Le résultat a été ajouté aux logs du harness mais pas au transcript ; le modèle ne l'a jamais vu
    - d) L'appel d'outil a en fait échoué et la trajectoire est fausse

<details markdown="1"><summary>Vérifier</summary>

**c)** Le résultat a été ajouté aux logs du harness mais pas au transcript ; le modèle ne l'a jamais vu. Du point de vue du modèle, trajectoires et transcripts devraient être presque identiques (même si les transcripts peuvent être tronqués ou échantillonnés par souci d'efficacité). Si la trajectoire dit que quelque chose s'est produit mais que le transcript ne le montre pas, la cause la plus probable est que le harness l'a consigné mais ne l'a pas ajouté au transcript. C'est le bug de l'exemple détaillé. Retirer du transcript après l'ajout (a) serait inhabituel et irait à l'encontre du but. Les transcripts ne sont pas des résumés ; ils doivent être l'historique de la conversation (b). Une erreur de trajectoire (d) est possible mais moins courante qu'un bug de journalisation.

</details>

4. ▢ Vous voulez construire un agent reprenable. L'exécution est interrompue après cinq tours. Écrivez en une phrase ce qu'il faut persister sur disque pour reprendre l'agent au tour six.

<details markdown="1"><summary>Vérifier</summary>

Il faut persister le transcript (l'historique de la conversation jusqu'au tour cinq, y compris chaque réponse du modèle, chaque appel d'outil et chaque résultat d'outil). À la reprise, donnez ce transcript au modèle comme contexte de départ, appelez le modèle et continuez la boucle. Les métadonnées du harness (compteur de tours, compteur d'erreurs, etc.) peuvent être reconstruites ou réinitialisées ; seul le transcript est essentiel.

</details>

## Exercices en situation réelle

- [ ] Exécutez un agent (issu d'une bibliothèque que vous utilisez ou écrit par vous) qui fait au moins trois appels d'outils. Inspectez le transcript qu'il a généré. Pour chaque résultat d'outil, vérifiez qu'il est présent dans ce que le modèle verrait au tour suivant. Si un résultat manque, cherchez pourquoi (n'a-t-il pas été ajouté, a-t-il été tronqué, ou filtré ?).

- [ ] Trouvez dans le code de votre agent ou de votre harness un endroit où une information est consignée mais pas ajoutée au transcript. Demandez-vous : le modèle a-t-il besoin de le savoir pour mieux décider ? Si oui, ajoutez-la au transcript. Sinon, laissez-la comme log réservé au harness.

- [ ] Demain : concevez un agent reprenable à partir de zéro. Écrivez le pseudocode de la fonction run qui prend un transcript en entrée et reprend au tour suivant. Vérifiez que vous ne vous appuyez sur aucun état réservé au harness pour décider.

## Pour aller plus loin

- [Billet : "Building Effective Agents", Anthropic Engineering](https://www.anthropic.com/engineering/building-effective-agents)
- [Ressources](../RESOURCES.md)

---

Ça ne passe pas ? Relisez la source primaire en haut de page, car cette leçon la condense et c'est dans la condensation que la compréhension s'échappe. Consultez le [glossaire](../GLOSSARY.md) pour tout terme qui vous a paru glissant.

Si c'est la leçon elle-même qui n'est pas claire plutôt que la matière, c'est un défaut : [ouvrez une issue](https://github.com/TokenCemetery/teach/issues).
