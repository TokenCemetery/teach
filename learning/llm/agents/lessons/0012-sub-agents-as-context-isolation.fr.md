---
title: "12. Les sous-agents comme isolation du contexte"
description: "Lancer un sous-agent isole un long travail d'exploration du budget de contexte du parent"
type: lesson
---

# Leçon 12. Les sous-agents comme isolation du contexte

**Lien avec la mission :** Diagnostiquer un agent défaillant à partir de sa trajectoire au lieu d'ajouter une instruction de plus à son prompt.
**Source primaire :** [Billet : "How We Built Our Multi-Agent Research System", Anthropic Engineering](https://www.anthropic.com/engineering/multi-agent-research-system)
**Prérequis :** [Leçon 11](0011-compaction-and-retrieval-on-demand.md)

## Échauffement

1. ▢ Quelle est la différence entre la compaction et la récupération à la demande ?

<details markdown="1"><summary>Vérifier</summary>

La compaction remplace les anciens tours par un résumé, ce qui économise des tokens mais risque de perdre de l'information. La récupération à la demande garde le détail ancien hors du contexte et ne le récupère que quand le modèle le demande, en échangeant un peu de latence contre un contexte résident plus petit.

</details>

2. ▢ Dans la compaction plus récupération à la demande, quelles trois choses le contexte toujours résident contient-il ?

<details markdown="1"><summary>Vérifier</summary>

L'objectif et les contraintes, un résumé de l'avancement, et des métadonnées (noms de fichiers, outils disponibles, titres de documents). Le détail complet est compressé (compaction) ou à la demande (récupération).

</details>

## À savoir

### Les sous-agents comme outil de gestion du contexte

Jusqu'ici, les leçons 10 et 11 se sont concentrées sur la gestion du transcript d'un seul agent. Mais il existe une autre approche : lancer un agent distinct pour accomplir un travail borné. C'est l'étape 8 (multi-agent), mais ici limitée à l'angle du budget de contexte uniquement.

Un sous-agent est une exécution d'agent neuve avec son propre transcript, son propre harness et son propre jeu d'outils. Il explore, fait des appels d'outils, accumule sa propre trajectoire. L'agent parent, lui, n'a payé le coût d'aucune de ces explorations. Aucun des tours du sous-agent n'apparaît dans le transcript du parent.

Quand le sous-agent termine, il produit un résultat final ou un résumé. Ce résumé (quelques phrases ou une structure de données) est ajouté au transcript du parent. Tout le raisonnement interne du sous-agent, toutes ses impasses, tous ses appels d'outils et ses échecs, restent hors du contexte du parent.

### L'idée clé : une trajectoire volumineuse et isolée ne coûte rien au parent

Supposons qu'un sous-agent passe 100 tours à lire des fichiers, comparer des motifs, buter sur des impasses et affiner son analyse. Sa trajectoire est énorme. Mais du point de vue du parent, tout ce travail est invisible. Le parent ne voit que le rapport final, quelques centaines de tokens. Pendant ce temps, le contexte du parent reste petit et bon marché.

C'est différent de la compaction et de la récupération à la demande, qui opèrent toutes deux à l'intérieur d'un seul transcript. Un sous-agent opère entièrement en dehors du transcript du parent. Son coût est supporté par le harness du sous-agent, pas par celui du parent.

### Le compromis : un raisonnement invisible signifie des détails perdus

Parce que le raisonnement interne du sous-agent est invisible pour le parent, l'information que le parent n'a pas pensé à demander peut être perdue. Si le parent lance un sous-agent pour « lire ces fichiers et les résumer », le sous-agent peut découvrir quelque chose d'intéressant mais périphérique : « J'ai aussi remarqué une fuite mémoire dans util.cpp. » Si le parent ne l'a pas demandé, le sous-agent peut l'omettre du rapport, et le parent ne l'apprend jamais.

C'est différent du risque de la compaction, où le harness contrôle ce qui est résumé. Avec un sous-agent, la frontière entre « ce qu'il faut rapporter » et « ce qu'il faut garder en interne » est le choix du sous-agent lui-même. Si le sous-agent est un modèle de langage, il estimera ce qui intéresse le parent d'après les instructions reçues. Cette estimation peut être fausse.

### Quand un sous-agent vaut le coup, et quand non

Un sous-agent vaut le coût de coordination quand :

- La sous-tâche est vaste et accumulera une longue trajectoire (beaucoup de tours, beaucoup d'appels d'outils, beaucoup d'impasses).
- La sous-tâche est bornée : il y a un point d'arrêt clair et le parent n'aura pas besoin du raisonnement du sous-agent pour le travail en aval.
- Le coût de lancement d'un nouvel agent (latence, surcharge de coordination) est bien plus petit que le coût de garder l'exploration du sous-agent dans le contexte du parent.

Par exemple : « Recherche l'historique de cette base de code, lis le git log et les principales PR, et donne-moi un résumé en trois phrases. » C'est une tâche vaste et bornée. Un sous-agent qui explore pendant 50 tours épargne au parent 50 tours de coût de contexte.

Un sous-agent ne vaut pas le coup quand :

- La tâche est petite (elle ne prendra de toute façon que quelques tours).
- La tâche exige une coordination étroite avec le parent (le parent posera des questions de clarification, le sous-agent devra affiner son travail).
- Le parent aura besoin plus tard de tout le raisonnement du sous-agent (pour comprendre pourquoi une conclusion a été atteinte, repérer une hypothèse, déboguer une erreur).

Par exemple : « Va chercher la température de demain. » C'est une tâche de quelques tours ; lancer un sous-agent coûte plus que de la faire dans le parent.

## Pratique

1. ▢ Un agent a pour tâche de relire le code de 50 fichiers et de produire un rapport. Le développeur a réparti le travail : l'agent principal relit 5 fichiers, et lance un sous-agent pour relire les 45 autres. Pourquoi est-ce un bon usage d'un sous-agent ?

    - a) Les sous-agents sont toujours plus rapides que les agents uniques
    - b) La longue trajectoire du sous-agent (relire 45 fichiers) est isolée du contexte de l'agent principal, ce qui garde le contexte principal petit et bon marché
    - c) Les sous-agents ne font jamais d'erreurs
    - d) L'agent principal peut voir immédiatement tout le raisonnement du sous-agent

<details markdown="1"><summary>Vérifier</summary>

**b)** Un sous-agent permet à l'agent principal de déléguer une tâche vaste et bornée. Les 100 tours et plus d'exploration du sous-agent ne gonflent pas le contexte de l'agent principal. L'agent principal ne reçoit que le rapport final du sous-agent. L'option a est fausse parce que les sous-agents peuvent ajouter de la latence. L'option c est fausse parce que les sous-agents peuvent faire des erreurs. L'option d est fausse parce que le raisonnement interne du sous-agent est invisible pour l'agent principal.

</details>

2. ▢ Un sous-agent relit une base de code et découvre une vulnérabilité de sécurité. Elle n'est pas directement liée à la tâche demandée par le parent (une revue de style de code), mais elle est critique. Quel risque l'invisibilité du sous-agent crée-t-elle ici ?

<details markdown="1"><summary>Indice</summary>

Les instructions du sous-agent lui disaient de se concentrer sur le style du code. Qui décide de ce qui est rapporté au parent, et que risque-t-on de perdre ?

</details>

<details markdown="1"><summary>Vérifier</summary>

Le sous-agent décide de ce qu'il inclut dans son rapport final d'après ses instructions. Si les instructions mettent l'accent sur le style du code, le sous-agent risque de ne pas signaler du tout le problème de sécurité, ou de le mentionner en note de bas de page que le parent manque. L'information que le parent n'a pas pensé à demander peut être perdue parce que le parent ne voit jamais le raisonnement complet du sous-agent. Le parent doit être très explicite : « Signale tout ce que tu trouves de critique, style ou non. »

</details>

3. ▢ Comparez deux approches d'une longue tâche de recherche :
    - Approche A : un agent unique qui compacte les anciens tours et utilise la récupération à la demande. Il prend 80 tours, le contexte résident reste sous 30 000 tokens.
    - Approche B : l'agent principal lance 3 sous-agents qui explorent en parallèle. Chacun prend 40 tours en interne. L'agent principal reçoit un résumé de chacun. Le contexte final de l'agent principal fait 5 000 tokens plus la surcharge de coordination.

Quelle approche a le coût total en tokens le plus bas (en comptant toutes les exécutions d'agents), et pourquoi ?

    - a) L'approche A, parce qu'elle évite la surcharge des sous-agents
    - b) L'approche B, parce que les trois explorations sont isolées et bon marché pour l'agent principal
    - c) Elles ont le même coût
    - d) Cela dépend de l'importance de la surcharge de coordination

<details markdown="1"><summary>Vérifier</summary>

**d)** L'approche A envoie 30 000 tokens au modèle 80 fois, soit environ 2,4 M de tokens. L'approche B envoie environ 50 000 tokens au modèle 40 fois pour chaque sous-agent, plus la coordination avec l'agent principal. Si la coordination est minimale et que le travail des sous-agents est réellement parallèle et borné, l'approche B peut être moins chère. Mais si la coordination est coûteuse ou si les sous-agents doivent affiner leurs résultats de façon itérative, l'approche A peut être meilleure. La réponse dépend du coût réel de lancement et de coordination des sous-agents.

</details>

4. ▢ Vous concevez un agent pour « déboguer cette suite de tests en échec et proposer une correction ». Faut-il utiliser un sous-agent, et pourquoi ou pourquoi pas ?

<details markdown="1"><summary>Vérifier</summary>

Non. Le débogage est une tâche où le parent aura vraisemblablement besoin de tout le raisonnement du sous-agent pour juger si la correction proposée est sûre, repérer des hypothèses ou poser des questions de clarification. Ce n'est pas une tâche bornée avec un rapport simple ; elle exige une coordination étroite. Le raisonnement invisible du sous-agent serait un handicap. Mieux vaut garder le débogage dans la boucle principale du parent, où celui-ci peut suivre toute la trajectoire.

</details>

## Exercices en situation réelle

- [ ] Décrivez une tâche pour laquelle vous utiliseriez un sous-agent et expliquez pourquoi une longue trajectoire isolée vaut le coût de coordination.
- [ ] Décrivez une tâche pour laquelle vous n'utiliseriez pas de sous-agent, et expliquez quelle information serait perdue si vous en utilisiez un.
- [ ] Demain : esquissez les responsabilités du parent et du sous-agent pour une tâche en plusieurs parties (par exemple « étudier cette bibliothèque, puis l'intégrer à notre base de code »). Où passe la frontière, et que rapporte chaque agent à l'autre ?

## Pour aller plus loin

- [Billet : "How We Built Our Multi-Agent Research System", Anthropic Engineering](https://www.anthropic.com/engineering/multi-agent-research-system)
- [Ressources](../RESOURCES.md)

---

Ça ne passe pas ? Relisez la source primaire en haut de page, car cette leçon la condense et c'est dans la condensation que la compréhension s'échappe. Consultez le [glossaire](../GLOSSARY.md) pour tout terme qui vous a paru glissant.

Si c'est la leçon elle-même qui n'est pas claire plutôt que la matière, c'est un défaut : [ouvrez une issue](https://github.com/TokenCemetery/teach/issues).
