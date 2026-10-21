---
title: "15. ReAct : entrelacer raisonnement et action"
description: "Schéma qui associe de courtes étapes de raisonnement à chaque action, pour que le modèle puisse observer et s'adapter"
type: lesson
---

# Leçon 15. ReAct : entrelacer raisonnement et action

**Lien avec la mission :** Pour diagnostiquer un agent défaillant, vous reconnaîtrez s'il exécute des actions sans raisonnement visible (là où se cache la cause racine), s'il suit un plan rigide établi en amont (là où les surprises de l'environnement provoquent des défaillances en cascade), ou s'il entrelace raisonnement et observation (là où les signaux d'échec remontent dans la décision suivante).
**Source primaire :** [Article : "ReAct: Synergizing Reasoning and Acting in Language Models", Yao et al., 2022](https://arxiv.org/abs/2210.03629)
**Prérequis :** [Leçon 14](0014-files-as-memory.md), [Boucle d'agent](../GLOSSARY.md)

## Échauffement

1. ▢ Quand vous stockez la mémoire d'un agent dans un fichier d'une exécution à l'autre (disons un transcript de conversation ou un journal des décisions passées), qu'est-ce qui devient plus facile à déboguer et à vérifier dans le comportement de l'agent ?

<details markdown="1"><summary>Vérifier</summary>

Une mémoire à base de fichiers permet de lire l'état exact que l'agent a vu avant chaque décision, pour rejouer son raisonnement et vérifier s'il a fait un choix sensé compte tenu de l'information disponible à ce moment-là. Si l'agent semble défaillant, vous pouvez lire sa trajectoire antérieure pour trouver l'étape exacte où il a dérapé, plutôt que de deviner.

</details>

2. ▢ Nommez un risque du stockage de grandes mémoires dans des fichiers : que se passe-t-il si l'agent n'élague ni ne compacte jamais le fichier ?

<details markdown="1"><summary>Vérifier</summary>

Le fichier grandit sans limite, consommant de l'espace disque et du budget de contexte quand il est transmis au modèle. L'agent finit par ne plus pouvoir faire tenir tout l'historique dans la fenêtre de contexte, ce qui force le harness à choisir quels souvenirs plus anciens abandonner et lesquels garder.

</details>

## À savoir

### Trois formes de raisonnement et d'action

La boucle d'agent prend naturellement en charge plusieurs schémas différents quant au moment où le raisonnement a lieu par rapport au moment où les actions s'exécutent. L'article ReAct en identifie trois, et comprendre les compromis entre eux est essentiel pour diagnostiquer les défaillances d'agents.

**Act-only :** le modèle reçoit la tâche et l'état courants, et émet immédiatement un appel d'outil sans raisonnement énoncé. Le harness exécute l'outil, ajoute le résultat et reboucle. C'est la structure la plus simple.

Le risque : quand quelque chose tourne mal, on ne peut pas savoir pourquoi le modèle a choisi cette action. A-t-il mal compris la tâche ? Croyait-il appeler un autre outil ? Sans trace de raisonnement, le débogage tient de la devinette. Vous finissez par ajouter des précisions au prompt (« Réfléchis étape par étape », « Vérifie ta réponse »), mais le modèle ne produit toujours aucun raisonnement visible à inspecter, donc les précisions risquent de ne pas aider.

**Reason-then-act-once :** le modèle lit la tâche, raisonne sur l'ensemble du plan en amont en texte (appelons cela la phase de « thought »), puis s'engage sur une séquence d'appels d'outils pour exécuter le plan. Une fois le plan engagé, le harness exécute toutes les étapes sans replanifier.

Cela évite les devinettes à page blanche de l'act-only, puisque vous pouvez voir tout le raisonnement du modèle. Mais il y a un coût caché : le plan est fait avant qu'aucun outil ne s'exécute. Si un appel d'outil échoue ou renvoie des données inattendues, le plan devient périmé. Le modèle ne peut pas réagir aux surprises parce qu'il s'est déjà engagé sur la séquence. Vous finissez par devoir relancer l'agent en espérant que la nouvelle phase de raisonnement se corrige d'elle-même.

**ReAct (raisonner, agir, observer en entrelacé) :** le modèle raisonne à voix haute sur ce qu'il faut faire ensuite (un court texte de « thought » ou de « reasoning »), puis émet un appel d'outil. Le harness exécute l'outil, ajoute le résultat au transcript et reboucle. Au tour suivant, le modèle lit la pensée précédente, l'action qu'il a choisie et le résultat réel, puis raisonne sur l'étape suivante d'après ce qu'il voit maintenant.

C'est le schéma ReAct. Le raisonnement du modèle est visible (vous pouvez le déboguer), mais surtout, le raisonnement à chaque étape peut intégrer le résultat réel de l'étape précédente. Si une recherche n'a renvoyé aucun résultat, la pensée suivante peut bifurquer vers une autre recherche. Si un appel d'API a échoué, la pensée suivante peut en tenir compte et essayer un contournement. Le raisonnement n'est pas un plan rigide établi en amont ; c'est une observation de ce qui vient de se passer, qui alimente ce qui se passe ensuite.

### Pourquoi ReAct l'emporte quand l'environnement vous surprend

Reason-then-act-once fonctionne bien dans les scénarios en monde clos où les hypothèses du plan sont garanties de tenir. Les vrais appels d'outils se produisent en monde ouvert : des fichiers manquent, des recherches ne renvoient rien, des API sont indisponibles, des utilisateurs donnent des instructions contradictoires. Dans ces cas, l'adaptation pas à pas de ReAct est moins chère et plus robuste que de relancer tout le cycle raisonner puis agir.

Pensez à la boucle d'agent elle-même, de la leçon 6. Un tour du modèle produit du texte (qui peut inclure du raisonnement) et un appel d'outil. Cet appel d'outil est exécuté, et le résultat est ajouté au transcript. Au tour suivant, le modèle voit le résultat et émet un nouveau texte et un nouvel appel d'outil. Par construction, la boucle d'agent prend déjà en charge ReAct : tout texte de raisonnement émis par le modèle est conservé dans le transcript, le tour suivant peut l'observer, et le tour suivant peut émettre un nouveau raisonnement qui réagit au résultat observé.

« Mon harness prend-il en charge ReAct ? » revient en réalité à « Mon harness garde-t-il le texte de raisonnement du modèle dans le transcript et le réinjecte-t-il au tour suivant ? » La réponse, dans presque tous les harness qui valent la peine d'être utilisés, est oui.

### Diagnostiquer les défaillances de l'act-only et du plan puis exécution en une fois

Si vous inspectez la trajectoire d'un agent et ne voyez aucun texte de raisonnement avant les appels d'outils, vous avez un agent act-only. Les défaillances sont difficiles à diagnostiquer. Ajouter plus de données au contexte (descriptions de tâche plus longues, plus d'exemples) peut aider, mais sans texte de raisonnement, vous n'avez aucune visibilité. La correction consiste à demander au modèle d'émettre du raisonnement (un champ « thought », une section « reasoning » dans l'appel d'outil, n'importe quoi) et à le conserver dans le transcript. Vous passez alors à ReAct et le débogage devient possible.

Si vous voyez un gros bloc de raisonnement au début, suivi d'une séquence d'actions sans raisonnement intermédiaire, vous avez du plan puis exécution en une fois. Quand l'agent échoue, vous voyez probablement un plan qui n'a pas survécu au contact de la réalité. La correction consiste à autoriser la replanification : après chaque résultat d'outil, émettre un nouveau raisonnement avant l'action suivante. Là encore, cela vous fait passer à ReAct. Certaines défaillances disparaîtront parce que le modèle peut désormais s'adapter.

## Pratique

1. ▢ On dit à un agent : « Cherche des informations sur le changement climatique, puis résume les 5 premiers résultats. » Il émet un appel d'outil de recherche sans texte de raisonnement préalable. La recherche renvoie 10 résultats sur la science du climat, et l'agent émet ensuite un appel d'outil de résumé sans raisonnement intermédiaire. Le résumé est inexact. Pourquoi est-il difficile de dire si le modèle a mal compris la tâche, mal compris les résultats ou commis une vraie erreur de raisonnement ?

<details markdown="1"><summary>Vérifier</summary>

Il n'y a aucun texte de raisonnement dans le transcript, donc vous ne pouvez pas voir quel était l'« objectif » interne du modèle ni comment il a interprété les résultats de la recherche. L'absence de raisonnement rend impossible de distinguer, par exemple, « le modèle n'a pas réalisé que la recherche avait renvoyé 10 résultats et a cru devoir chercher à nouveau » de « le modèle a vu les 10 résultats et a mal compris la tâche en résumant tous les résultats, pas les 5 premiers ». Ajouter du texte de raisonnement avant l'étape de résumé (une pensée à la ReAct) vous permettrait de voir quelle méprise s'est produite et de corriger le prompt en conséquence.

</details>

2. ▢ Vous construisez un agent qui prend les retours d'un utilisateur et affine un document. Le plan de l'agent (émis en amont) est « Corriger la grammaire, puis ajouter des exemples, puis vérifier la longueur. » La première passe réussit. Mais le retour de l'utilisateur lors de la deuxième exécution est « Je n'aime pas les nouveaux exemples que vous avez ajoutés, mais gardez les corrections de grammaire. » L'agent réutilise le plan établi en amont sans changement et ajoute à nouveau des exemples, en ignorant le retour.

<details markdown="1"><summary>Indice</summary>

Qu'est-ce qui rend le plan périmé dans ce scénario ? Quelle information l'agent ne voit-il pas quand il planifie ?

</details>

<details markdown="1"><summary>Vérifier</summary>

Le plan a été fait sans voir le retour de l'utilisateur. Dans le plan puis exécution en une fois, la phase de raisonnement a lieu avant l'exécution de tout outil, donc elle ne peut pas intégrer de nouvelle information qui arrive en cours de trajectoire. La correction consiste à autoriser le raisonnement et la replanification après chaque résultat d'outil (ici, après chaque étape d'affinage), pour que le plan de l'agent puisse s'adapter quand le retour de l'utilisateur contredit les hypothèses d'origine.

</details>

3. ▢ Lequel des signes suivants indique qu'il faut faire passer un agent de l'act-only à ReAct ?

    - a) L'agent est trop lent et vous devez accélérer les appels d'outils.
    - b) Les défaillances de l'agent sont difficiles à diagnostiquer parce que vous ne pouvez pas voir pourquoi il a choisi chaque action.
    - c) L'agent doit utiliser 10 outils au lieu de 5.
    - d) La fenêtre de contexte de l'agent est presque pleine.

<details markdown="1"><summary>Vérifier</summary>

**b)** Les agents act-only ne produisent aucun texte de raisonnement, donc leurs défaillances sont opaques. Passer à ReAct (ajouter une étape de raisonnement avant chaque action) rend le raisonnement du modèle visible, ce qui est le principal gain pour le débogage. a) est faux parce que ReAct n'accélère pas les appels d'outils, il ajoute du texte de raisonnement qui prend du temps. c) est faux, le nombre d'outils n'a pas de rapport. d) est faux, la pression sur le contexte est un souci distinct de celui de savoir si l'agent raisonne à voix haute.

</details>

4. ▢ Un agent cherche « best pizza restaurants in Portland » et reçoit 5 résultats. Si l'agent fonctionne en mode ReAct, que doit-il se passer ensuite dans le transcript ?

<details markdown="1"><summary>Vérifier</summary>

L'agent doit émettre une étape de raisonnement (une section « thought » ou « reasoning ») qui observe les résultats de la recherche et décide de la suite (par exemple « Ces résultats ont l'air bons, j'ai maintenant assez d'information pour répondre. Je vais les résumer » ou « J'ai besoin de plus de détails sur les horaires des restaurants, je vais les chercher ensuite »). Ce raisonnement repose sur ce que la recherche a réellement renvoyé, pas sur un plan établi en amont. En l'incluant dans le transcript, l'appel d'outil suivant (s'il y en a un) peut s'appuyer sur le résultat réel.

</details>

## Exercices en situation réelle

- [ ] Prenez un agent existant que vous avez construit ou que vous connaissez. Lisez sa trajectoire (une exécution complète). Comptez combien d'appels d'outils sont immédiatement précédés de texte de raisonnement. Si moins de 80 % le sont, réécrivez le prompt ou le schéma d'outil pour qu'il émette du raisonnement, puis relancez-le.
- [ ] Cassez délibérément un outil dont dépend un agent (par exemple, faites renvoyer un résultat vide à une API de recherche). Lancez l'agent sur une tâche qu'il réussirait normalement. Lisez la trajectoire. L'agent a-t-il émis un raisonnement qui reconnaît l'outil cassé et a-t-il bifurqué vers une autre approche ? Sinon, ajoutez une instruction de prompt pour le raisonnement et réessayez.
- [ ] Demain : demandez à un collègue de lire la trajectoire d'un agent sans voir la tâche. Peut-il déduire ce que l'agent essayait de faire à chaque étape à partir du seul texte de raisonnement ? S'il ne le peut pas, ajoutez des prompts de raisonnement.

## Pour aller plus loin

- [Article : "ReAct: Synergizing Reasoning and Acting in Language Models", Yao et al., 2022](https://arxiv.org/abs/2210.03629)
- [Ressources](../RESOURCES.md)

---

Ça ne passe pas ? Relisez la source primaire en haut de page, car cette leçon la condense et c'est dans la condensation que la compréhension s'échappe. Consultez le [glossaire](../GLOSSARY.md) pour tout terme qui vous a paru glissant.

Si c'est la leçon elle-même qui n'est pas claire plutôt que la matière, c'est un défaut : [ouvrez une issue](https://github.com/TokenCemetery/teach/issues).
