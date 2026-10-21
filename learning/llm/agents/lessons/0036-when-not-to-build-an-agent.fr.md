---
title: "36. Quand ne pas construire d'agent"
description: "Le jugement pour décider si une tâche a réellement besoin d'un agent, et la discipline de dire non quand il ne vaut pas son coût"
type: lesson
---

# Leçon 36. Quand ne pas construire d'agent

**Lien avec la mission :** Construire le jugement nécessaire pour décider si une tâche donnée a vraiment besoin d'un agent plutôt que d'un workflow fixe, et pour défendre cette décision face à la pression de l'organisation et à l'attrait des solutions en forme d'agent.
**Source primaire :** [Billet : "Building Effective Agents", Anthropic Engineering](https://www.anthropic.com/engineering/building-effective-agents)
**Prérequis :** [Leçon 35](0035-durability-and-what-frameworks-buy.md), [Spectre d'autonomie](../GLOSSARY.md)

## Échauffement

1. ▢ Rappelez-vous la leçon 2 : quelle est la différence déterminante entre un workflow et un agent en termes de flux de contrôle ?

<details markdown="1"><summary>Vérifier</summary>

Un workflow a un chemin que le développeur a fixé à l'avance ; toutes les branches et séquences sont câblées par le développeur. Un agent a un flux de contrôle décidé à l'exécution par le modèle, y compris le choix de continuer ou de s'arrêter.

</details>

2. ▢ Rappelez-vous la leçon 2 : sur le spectre d'autonomie, quel test concret pouvez-vous appliquer pour décider si le nombre de branches d'une tâche est réellement énumérable ?

<details markdown="1"><summary>Vérifier</summary>

Si vous pouvez lister tous les chemins distincts qu'un workflow devrait couvrir pour la tâche, le nombre de branches est énumérable et un workflow peut suffire. Si de nouveaux chemins arrivent plus vite que vous ne pouvez les câbler, ou si le bon chemin dépend réellement d'une information disponible seulement en cours de tâche, le nombre de branches est en pratique illimité et un agent est plus défendable.

</details>

## À savoir

### Pourquoi la décision est plus difficile que la leçon 2 ne l'a laissé paraître

La leçon 2 a enseigné le spectre d'autonomie comme un choix technique net : la forme de la tâche est-elle connue ou inconnue, énumérable ou illimitée ? En pratique, ce choix se fait sous une vraie pression.

Un chef de produit a vu une démo convaincante d'un agent qui résout un problème complexe et demande : « Peut-on construire ça pour notre produit ? » Une organisation se sent en retard sur l'IA et veut « ajouter des agents » à sa plateforme. Une partie prenante pointe une tâche et dit : « Ça a l'air digne d'un agent », sans vérifier si l'alternative plus simple a vraiment été essayée. Un workflow qui résout le même problème est moins exaltant à présenter, même quand c'est le meilleur choix d'ingénierie.

Le rôle de cette leçon n'est pas de réenseigner le cadre de la leçon 2 ; le cadre est juste. Le rôle est de dire pourquoi l'appliquer correctement est un jugement à porter sous pression, et de vous donner des signaux d'alerte concrets qui indiquent qu'un agent n'est pas justifié, chacun relié à une leçon précédente précise pour que vous puissiez repérer le motif quand vous le voyez dans une proposition ou une revue d'architecture.

### Signal d'alerte 1 : personne n'a essayé d'abord le workflow plus simple

Le signal d'alerte le plus fort est celui-ci : une partie prenante ou une proposition dit qu'un agent est nécessaire, mais personne n'a réellement construit l'alternative en workflow pour tester cette affirmation.

La leçon 2 défend chaque choix en nommant ce que l'option écartée aurait coûté. Cette défense ne fonctionne que si vous avez réellement testé l'option écartée. Si une proposition affirme qu'« un agent est nécessaire » sans montrer une tentative de workflow ni expliquer pourquoi le workflow a échoué, l'affirmation n'a pas été confrontée à l'alternative. On vous demande d'accepter une hausse de complexité sans preuve que cette complexité est nécessaire.

À quoi cela ressemble en pratique : une proposition dit « Il nous faut un agent pour traiter ces tickets de support client parce qu'ils se ramifient en quarante catégories distinctes. » Sans tentative de workflow, vous ne savez pas si quarante catégories est réellement trop pour être câblé, ou si l'auteur de la proposition n'a simplement pas encore essayé. Après avoir construit un routeur en workflow et l'avoir testé sur de vrais tickets, vous pourriez constater que quarante catégories sont gérables, ou que la précision du workflow en souffre parce qu'un classifieur à base de règles ne peut pas distinguer deux catégories sur les cas limites. Tester le workflow sur la même tâche vous dit ce que vous achetez réellement en passant à un agent.

La discipline : avant de s'engager sur un agent, demandez « quel workflow a été essayé, et pourquoi a-t-il échoué ? » Si la réponse est « aucun », insistez pour en construire un d'abord. Vous découvrirez peut-être que le workflow résout assez bien le problème, ou qu'il échoue de façons précises qu'un agent améliorerait réellement.

### Signal d'alerte 2 : le mode de défaillance est la fiabilité, pas la capacité

La leçon 2 a dit qu'un agent mérite son imprévisibilité quand on a besoin de flexibilité. Mais la flexibilité a des coûts en fiabilité que les étapes 11 et 12 de ce parcours ont passé des leçons à nommer : erreurs d'ancrage des agents de computer use (leçon 25), erreurs d'outils en cascade où l'échec d'un outil entraîne l'étape suivante (leçon 28), empoisonnement du contexte où une affirmation fausse entre dans le transcript et est traitée en silence comme un fait par chaque tour suivant (leçon 27).

Si le mode de défaillance d'une tâche relève de l'une de ces classes de fiabilité, et que la tâche est de celles où un workflow fixe et bien testé ne commettrait tout simplement jamais cette classe d'erreur, alors un agent achète de l'imprévisibilité au prix d'un problème de fiabilité qui n'existait pas auparavant.

Exemple : un système de classification de documents qui doit router les documents vers exactement l'une de cinq catégories connues. Un agent peut router avec flexibilité et même recatégoriser s'il lit quelque chose dans le document qui lui fait changer d'avis. Mais si la tâche est de classer un document financier selon un processus fixe et auditable, et que la sanction d'une erreur de classification est une infraction réglementaire, alors la flexibilité d'un agent ne vaut pas le risque que l'empoisonnement du contexte l'amène à remettre en cause son propre raisonnement antérieur et à envoyer un document dans la mauvaise catégorie. Un workflow avec une seule décision de routage par document, auditable étape par étape, coûte de la prévisibilité mais gagne de la fiabilité là où cela compte.

La discipline : pour les tâches où l'échec coûte cher ou où la fiabilité n'est pas négociable, nommez quel problème de fiabilité un agent introduirait qu'un workflow n'aurait pas. Si ce problème est assez grave, le workflow est le meilleur choix même s'il paraît moins sophistiqué.

### Signal d'alerte 3 : la triade létale est entièrement présente sans bénéfice

La leçon 31 a nommé la triade létale : l'accès à des données privées, l'exposition à du contenu non fiable et la capacité à communiquer vers l'extérieur. Un agent réunit les trois conditions quand il lit une entrée non fiable et dispose d'outils capables de détourner des données ou de les exfiltrer.

Supprimer une seule condition brise l'attaque. Mais un agent qui réunit les trois conditions est exploitable même si une injection ne réussit que parfois. La leçon 32 a enseigné que la défense n'est pas de prompter le modèle plus fort, mais de réduire l'accès des outils.

Si un agent proposé réunit les trois conditions de la triade et que la tâche ne profite pas de l'imprévisibilité de l'agent, vous achetez de l'exploitabilité pour rien. Une intégration plus étroite à base de workflow, ou un jeu d'outils qui manque délibérément de l'une des trois conditions, atteint le même but sans assembler l'exposition.

Exemple : un moteur de recommandation de contenu lit des profils d'utilisateurs et des sources de contenu externes pour suggérer des éléments. Si le moteur est implémenté comme un agent avec des outils pour récupérer du contenu externe, interroger des données d'utilisateurs et envoyer des recommandations à un système de messagerie, il réunit les trois conditions de la triade. Mais si le travail du moteur est de choisir dans un ensemble fixe de types de recommandation selon des règles simples (si l'utilisateur a vu A, recommander B), alors un workflow fait le travail sans exposer les données d'utilisateurs et le système de recommandation à un canal d'injection de prompt qui n'existait pas auparavant.

La discipline : pour chaque condition de la triade, demandez-vous si la tâche en a réellement besoin. Si un agent a les trois pour une tâche qui n'exige pas la flexibilité de l'agent, reconcevez le jeu d'outils pour retirer délibérément au moins une condition. Le système sera moins impressionnant en démo, mais il sera moins exploitable et plus fiable.

### Signal d'alerte 4 : le coût en tokens dépasse la valeur de la tâche

La leçon 33 a enseigné l'amplification de tokens et le coût par tâche terminée, y compris le multiplicateur multi-agent. La leçon 19 a montré qu'un système orchestrateur et worker coûte plusieurs fois plus de tokens qu'un agent unique qui résout le même problème.

Une question concrète : estimez le coût réel par tâche terminée, y compris les nouveaux essais, la coordination multi-agent le cas échéant, et toute amplification de tokens due à la longueur du contexte ou à la surcharge du caching. Ce coût est-il acceptable au regard de ce que produit la tâche ?

Cette question n'est souvent posée que lorsqu'il est trop tard. Une équipe construit un agent, le lance, et découvre que le coût par tâche dépasse ce que la tâche vaut en valeur métier. L'agent fonctionne, mais l'exploiter coûte trop cher.

La discipline : avant de s'engager sur un agent (surtout un système multi-agent), estimez le coût en tokens par tâche terminée à partir de tours ou de trajectoires réels d'un prototype. Confrontez cette estimation à la valeur de la tâche. Si le coût en tokens dépasse la valeur, l'agent n'est pas justifié, aussi élégant que soit le système.

### En résumé : posez ces quatre questions avant de s'engager sur un agent

1. Un workflow plus simple a-t-il réellement été tenté et jugé insuffisant ?
2. Le mode de défaillance de la tâche est-il de ceux où un agent introduit un nouveau problème de fiabilité qu'un workflow n'aurait pas ?
3. L'agent réunit-il les trois conditions de la triade, et cette exposition est-elle nécessaire pour la tâche ?
4. Le coût en tokens par tâche terminée est-il acceptable au regard de ce que produit la tâche ?

Si la réponse à l'une de ces questions est « non » ou « nous ne savons pas », l'agent n'est peut-être pas justifié. Dire non à un agent n'est pas un échec ; c'est de la discipline. Vous choisissez la prévisibilité, la fiabilité, la sécurité ou le coût plutôt que la flexibilité qu'un agent achèterait. C'est un choix défendable, et c'est le choix qui vous permet de dire oui avec assurance quand un agent est réellement justifié.

## Pratique

1. ▢ Une équipe produit propose de construire un agent pour résumer des tickets de support client pour du reporting interne. L'agent lirait le ticket (contenu d'utilisateur non fiable), accéderait à la base de données clients de l'entreprise pour chercher du contexte, et publierait des résumés dans un canal Slack. Une alternative en workflow ferait trier les tickets par catégories à la main par un humain, puis lancerait un résumeur à base de gabarit sur chaque catégorie. L'équipe dit qu'« un agent est plus efficace ». Sans exécuter le workflow, quelle question devriez-vous poser en premier ?

<details markdown="1"><summary>Vérifier</summary>

Demandez-leur de construire réellement le workflow et de le tester sur de vrais tickets. Mesurez de combien l'agent est plus rapide, et si le gain d'efficacité justifie le coût en consommation de tokens et l'exposition à la triade létale (l'agent lit du contenu non fiable, accède à des données clients privées et envoie des messages externes). Si le workflow est bon à 90 pour cent et coûte 10 pour cent, le workflow gagne. Sans test du workflow, l'affirmation « un agent est plus efficace » n'est pas vérifiée.

</details>

2. ▢ Vous relisez une proposition d'agent qui aide des analystes à déboguer des tests en échec dans une grande base de code. L'agent aurait accès au code du dépôt, aux résultats des tests et aux logs. Il appellerait des outils pour chercher dans le code, exécuter des tests individuels et déposer des rapports de bug. La proposition dit : « Un agent peut explorer la base de code plus souplement qu'un script. » Quelle préoccupation de fiabilité la leçon 27 enseigne-t-elle qui soit pertinente pour évaluer cette proposition ?

<details markdown="1"><summary>Indice</summary>

Pensez à ce qui se passe quand un agent lit les sorties d'appels d'outils et se construit un modèle de ce que le code dit et fait. Quel motif d'erreur est propre aux agents ?

</details>

<details markdown="1"><summary>Vérifier</summary>

L'empoisonnement du contexte (leçon 27). Si l'agent interprète mal un log ou un extrait de code et intègre une affirmation fausse dans son modèle du bug (par exemple « cette fonction renvoie None »), chaque étape de raisonnement ultérieure traitera cette affirmation fausse comme un fait établi. Un script à chemin fixe ne remettra pas ainsi en cause sa propre sortie. La flexibilité d'un agent à changer d'avis sur la base de nouveaux éléments est un atout, mais elle ouvre aussi la porte à une confiance silencieuse dans de mauvaises conclusions reportées d'une étape à l'autre. Évaluez si le mode de défaillance de la tâche (déboguer un test) est plus pénalisé par la flexibilité (meilleure pour trouver des bugs inédits) ou par le risque que l'empoisonnement du contexte mène l'agent sur une fausse piste.

</details>

3. ▢ Lequel de ces scénarios indique le plus clairement qu'un agent proposé n'est pas justifié ?

    - a) La tâche peut être résolue par un workflow, mais le workflow exigerait de câbler une nouvelle branche chaque fois qu'un nouveau type de document arrive
    - b) La tâche a été essayée en workflow et n'a pas atteint les objectifs de précision, mais un agent prototype testé sur le même jeu de données fait mieux
    - c) La tâche n'a jamais été essayée en workflow, mais une partie prenante insiste sur la nécessité d'un agent parce qu'une démo d'IA qu'elle a vue était impressionnante
    - d) La tâche exige de lire du contenu non fiable et d'accéder à des données privées, mais le jeu d'outils de l'agent n'a délibérément aucune communication externe

<details markdown="1"><summary>Vérifier</summary>

**c)** Le scénario où une tâche n'a jamais été essayée en workflow, et où la proposition est motivée par l'enthousiasme pour une démo plutôt que par la preuve que l'alternative plus simple échoue. Le scénario (a) décrit une tâche où un agent achète une flexibilité durable ; le nombre de branches croît, donc un agent est justifié. Le scénario (b) montre que le workflow a été testé et a échoué, ce qui fait de la meilleure performance de l'agent un argument en sa faveur. Le scénario (d) décrit une architecture raisonnée qui retire une condition de la triade, ce qui est un choix de conception justifié. Seul (c) n'a aucune base dans un test.

</details>

4. ▢ Vous estimez qu'un agent pour une tâche coûterait 5 000 tokens par exécution terminée, nouveaux essais compris, et que la tâche produit une valeur métier équivalente à 2 000 tokens de calcul aux tarifs actuels du marché. Défendez un choix entre construire l'agent ou choisir une alternative, en nommant ce que vous acceptez en faisant ce choix.

<details markdown="1"><summary>Vérifier</summary>

L'alternative (un workflow, un système plus simple ou laisser la tâche manuelle) est justifiée. L'agent coûte 2,5 fois sa valeur, ce qui signifie que chaque exécution coûte à l'entreprise plus en calcul qu'elle ne rapporte en valeur. Construire quand même l'agent n'est défendable que si vous vous attendez à ce que le coût en tokens baisse (modèles moins chers, stratégies de caching, convergence plus rapide sur les tâches répétées), ou si la valeur métier est supérieure à l'estimation. Si aucun des deux n'est vrai, la discipline est de dire non. Le coût que vous acceptez est de perdre la flexibilité qu'un agent apporterait, mais vous gagnez en prévisibilité et en efficacité de coût. C'est le bon compromis à ces chiffres.

</details>

## Exercices en situation réelle

- [ ] Prenez une tâche actuellement résolue par un agent dans un système que vous connaissez. Estimez le coût en tokens par tâche terminée et la valeur métier de chaque achèvement. Le rapport est-il acceptable ? Sinon, que faudrait-il changer pour qu'un agent soit justifié ?
- [ ] Trouvez une proposition (interne, ou un article décrivant un système) qui plaide pour un agent. Vérifiez si elle répond aux quatre questions des signaux d'alerte : un workflow a-t-il été essayé, le mode de défaillance est-il sensible à la fiabilité, les trois conditions de la triade sont-elles nécessaires, et le coût est-il acceptable ? Notez quels signaux d'alerte la proposition traite et lesquels elle laisse ouverts.
- [ ] Demain : imaginez une fonctionnalité de produit que vous construiriez comme un agent. Concevez-la maintenant comme un workflow. Comparez-les : que ne peut pas faire le workflow que l'agent peut faire ? Combien le workflow est-il plus difficile à construire ? Les gains justifient-ils la complexité ajoutée ? Notez votre évaluation honnête.

## Pour aller plus loin

- [Billet : "Building Effective Agents", Anthropic Engineering](https://www.anthropic.com/engineering/building-effective-agents)
- [Ressources](../RESOURCES.md)

---

Ça ne passe pas ? Relisez la source primaire en haut de page, car cette leçon la condense et c'est dans la condensation que la compréhension s'échappe. Consultez le [glossaire](../GLOSSARY.md) pour tout terme qui vous a paru glissant.

Si c'est la leçon elle-même qui n'est pas claire plutôt que la matière, c'est un défaut : [ouvrez une issue](https://github.com/TokenCemetery/teach/issues).
