---
title: "18. Orchestrateur et worker"
description: "Concevoir un système multi-agent où un agent planifie et délègue pendant que les workers exécutent en parallèle"
type: lesson
---

# Leçon 18. Orchestrateur et worker

**Lien avec la mission :** Pour choisir entre un agent unique bien équipé et un système multi-agent, il faut comprendre ce que les systèmes multi-agents peuvent faire et que les agents uniques ne peuvent pas, en commençant par le schéma orchestrateur et worker qui fait tourner la plupart des systèmes multi-agents de recherche et de planification.
**Source primaire :** [Billet : "How We Built Our Multi-Agent Research System", Anthropic Engineering](https://www.anthropic.com/engineering/multi-agent-research-system)
**Prérequis :** [Leçon 17](0017-self-critique-and-reasoning-models.md), [Sous-agent](../GLOSSARY.md)

## Échauffement

1. ▢ Depuis la leçon 17, rappelez-vous : que fait une boucle de réflexion explicite après une tentative échouée, et pourquoi un modèle à raisonnement interne étendu a-t-il moins besoin de cette boucle externe qu'un modèle standard ?

<details markdown="1"><summary>Vérifier</summary>

Une boucle de réflexion explicite génère une critique en langage naturel de la raison de l'échec de la tentative et reporte cette critique dans la tentative suivante, comme une étape distincte du tour du modèle. Un modèle qui fait un raisonnement interne étendu avant de répondre peut attraper certaines des mêmes erreurs à l'intérieur d'un seul tour, donc la boucle externe justifie moins souvent son coût, même si elle aide encore quand le signal d'échec (une erreur d'outil, un résultat de test) n'existe qu'après que le modèle a déjà agi.

</details>

2. ▢ Depuis la leçon 12, rappelez-vous : qu'est-ce qu'un sous-agent, et quel problème son transcript distinct résout-il ?

<details markdown="1"><summary>Vérifier</summary>

Un sous-agent est une exécution d'agent distincte, avec son propre harness et son propre transcript. Il résout l'isolation du contexte : vous pouvez lancer un sous-agent ciblé sur une tâche bornée sans que le transcript de cette tâche ne gonfle le contexte de l'agent parent, ce qui garde clair le raisonnement du parent pour la synthèse et la coordination.

</details>

## À savoir

### Le schéma orchestrateur et worker

Quand une tâche est trop vaste pour le contexte d'un seul agent ou exige une exploration parallèle, le schéma orchestrateur et worker répartit le travail : un agent (l'orchestrateur) découpe la tâche en sous-tâches bornées, décide quel worker reçoit quelle sous-tâche, puis synthétise leurs résultats en une réponse finale. Chaque worker est un sous-agent avec son propre transcript et ses propres outils, qui s'exécute indépendamment (et souvent en parallèle).

Pensez à un chef d'équipe qui ne fait pas le travail directement mais coordonne : il découpe un projet, attribue des morceaux aux membres de l'équipe et rassemble leurs livrables. Les workers ne voient jamais le raisonnement complet les uns des autres ; l'orchestrateur ne voit que leurs rapports finaux.

### Ce que font les workers

Les workers ne sont pas interchangeables. Chaque worker a typiquement :

- Une mission bornée et précise (par exemple « recherche cet angle précis », « évalue cette approche candidate »)
- Des outils adaptés à cette mission (par exemple de la récupération pour un worker de recherche, de l'exécution de code pour un worker d'évaluation)
- Sa propre boucle d'agent et son propre transcript, isolés des autres workers

Parce que les workers exécutent leurs propres boucles, ils peuvent explorer indépendamment. Un worker n'a pas besoin de savoir ce que font les autres ; il ne connaît que sa propre tâche. Cette indépendance est ce qui rend le parallélisme possible : de nombreux workers peuvent tourner en même temps, le temps réel est borné par le worker le plus lent, pas par la somme des temps de tous les workers.

### Fan-out : exploration parallèle

Le fan-out est un sous-cas de l'orchestrateur et worker où l'orchestrateur lance plusieurs workers sur des variantes d'une même question. Par exemple :

- Un worker étudie l'angle A, un autre l'angle B, un troisième l'angle C, tous en parallèle, pour obtenir une couverture plus large plus vite qu'un seul agent qui les traiterait en série.
- Trois workers essaient chacun de résoudre le même problème de code avec des stratégies différentes, et l'orchestrateur choisit la meilleure solution ou combine les enseignements.

Le gain de vitesse est réel : au lieu d'un agent unique qui passe 10 tours sur le problème A, puis 10 tours sur le problème B, puis 10 tours sur le problème C (30 tours au total), trois workers s'attaquent à A, B et C en parallèle (10 tours de latence au lieu de 30). Le revers (exploré dans la leçon 19) est que vous payez le coût en tokens de l'exécution complète des trois workers, pas seulement celle d'un agent.

### Passation : spécialisation séquentielle

La passation est un autre schéma multi-agent, qui utilise aussi des sous-agents mais avec des phases séquentielles au lieu de workers parallèles. Dans la passation :

1. L'agent A termine sa part de la tâche.
2. L'agent A passe la main à l'agent B en lui donnant un contexte propre et borné : typiquement seulement la définition de la tâche et les constats finaux de l'agent A, pas toute la trajectoire de l'agent A.
3. L'agent B reprend à partir de là, avec ses propres outils spécialisés et son propre raisonnement.

La passation est utile quand une tâche se découpe naturellement en phases séquentielles traitées par différents spécialistes. Par exemple : un orchestrateur constate qu'un problème exige à la fois de la recherche approfondie et de l'implémentation, et passe donc les constats à un codeur spécialisé ; ou un planificateur termine un plan et le passe à un exécutant avec seulement le plan, pas le raisonnement brouillon sur la raison du choix de ce plan.

La passation et le fan-out sont opposés par leur rythme : le fan-out est du multiple en parallèle, la passation du un après l'autre. Tous deux sont multi-agents ; tous deux isolent le contexte grâce aux sous-agents ; tous deux sont enseignés dans cette leçon parce qu'ils répondent tous deux à la question « quand un seul agent ne suffit-il pas ? »

### Pourquoi les systèmes orchestrateur et worker apportent de la valeur en pratique

La source primaire détaille un système multi-agent de recherche concret construit chez Anthropic : découper une tâche de recherche complexe en de nombreuses sous-tâches de recherche indépendantes, lancer un worker pour chacune, récupérer et analyser les sources en parallèle, puis synthétiser les constats en une réponse cohérente. Les principaux gains ont été :

- Le parallélisme en temps réel : une recherche complexe qu'un agent unique aurait passé plus de 50 tours à mener pourrait aller plus vite avec 5 workers, chacun sur 15 tours, s'exécutant simultanément.
- Des outils spécialisés par worker : un worker de récupération peut se concentrer sur la recherche et le classement sans l'encombrement de contexte de l'exécution de code ; un worker de synthèse a un autre objectif et d'autres outils.
- Un raisonnement indépendant : chaque worker raisonne sur sa propre tranche du problème ; les workers ne sont pas distraits par de l'information destinée à d'autres workers.

Ce schéma est apparu comme une solution pratique à une vraie contrainte : la capacité d'un modèle à bien raisonner sur une tâche complexe est bornée en partie par la longueur du contexte et en partie par la nécessité de garder le raisonnement ciblé. Répartir le travail permet d'ajouter de la puissance de raisonnement (plus de workers, chacun avec son propre budget de contexte) sans qu'un agent unique perde le fil ou manque de contexte.

## Pratique

1. ▢ Vous construisez un système pour répondre aux questions des utilisateurs sur une grande base de code. Vous envisagez deux conceptions : (A) un agent unique avec accès à des outils de recherche de code et à des outils de documentation, ou (B) un orchestrateur qui délègue en parallèle à un worker de recherche et à un worker de documentation. Quelle conception correspond le plus naturellement au schéma orchestrateur et worker, et pourquoi ?

<details markdown="1"><summary>Vérifier</summary>

La conception (B) correspond au schéma. Le worker de recherche et le worker de documentation ont des tâches indépendantes : l'un cherche dans le code, l'autre dans la documentation. Ils peuvent tourner en parallèle sans avoir besoin des résultats l'un de l'autre en cours de tâche. Le travail de l'orchestrateur est clair : formuler des requêtes pour chaque worker, puis combiner leurs constats.

La conception (A) pourrait aussi fonctionner, mais l'agent unique devrait décider en cours de tâche quel outil utiliser ensuite ; il n'y a aucun gain de parallélisme. Vous choisiriez (B) quand vous vous attendez à ce que les requêtes de recherche et de documentation soient indépendantes et bénéficient d'une exploration parallèle ; vous choisiriez (A) si les requêtes dépendent les unes des autres (les résultats de la recherche indiquent quelle documentation aller chercher) ou si la surcharge de lancement de deux sous-agents l'emporte sur le gain de vitesse (une tâche plus simple).

</details>

2. ▢ Dans un système orchestrateur et worker, pourquoi un worker ne peut-il pas voir directement le raisonnement d'un autre worker en cours de tâche ?

<details markdown="1"><summary>Indice</summary>

Pensez à la structure : chaque worker a son propre transcript et son propre harness. Qu'est-ce que cet isolement empêche ?

</details>

<details markdown="1"><summary>Vérifier</summary>

Chaque worker exécute sa propre boucle d'agent avec son propre transcript. Le raisonnement du worker A est enregistré dans le transcript du worker A, et celui du worker B dans le transcript du worker B. Le harness ne les fusionne pas. Les workers n'ont pas accès aux transcripts des autres pendant leurs exécutions ; ils ne peuvent lire que les rapports finaux que l'orchestrateur leur donne (si l'orchestrateur les leur transmet). Cet isolement garde le contexte de chaque worker ciblé et explique pourquoi les sous-agents résolvent des problèmes de contexte. Le revers est la fragmentation : une décision qui exige le raisonnement complet des deux workers ne peut être prise par aucun des deux seul (traité dans la leçon 19).

</details>

3. ▢ Vous concevez un système de recherche. Scénario : un worker étudie l'histoire d'une technologie, et un second étudie les applications actuelles de cette technologie. Les tâches de ces workers peuvent-elles s'exécuter en parallèle ?

    - a) Non, parce que le worker des applications a besoin de connaître d'abord l'histoire.
    - b) Oui, les deux workers peuvent faire leurs recherches indépendamment ; l'orchestrateur peut synthétiser les constats sur l'histoire et les applications quel que soit l'ordre.
    - c) Non, parce qu'ils étudient la même technologie.
    - d) Oui, seulement si le worker de l'histoire termine avant que le worker des applications ne commence.

<details markdown="1"><summary>Vérifier</summary>

**b)** Les deux tâches sont indépendantes : un worker qui étudie l'histoire n'a pas besoin des constats de l'autre worker pour bien faire sa recherche sur l'histoire, et inversement. L'orchestrateur aura les deux résultats quand les deux workers auront terminé et pourra les synthétiser en une réponse complète. (a) est faux : des dépendances s'exécuteraient l'une après l'autre (passation), pas en fan-out ; ici il n'y a pas de dépendance. (c) est faux : étudier la même technologie n'empêche pas le parallélisme ; c'est même la raison pour laquelle le fan-out est utile, obtenir plusieurs angles sur un même sujet. (d) est faux : le parallélisme signifie qu'ils s'exécutent en même temps, pas l'un après l'autre.

</details>

4. ▢ En quoi une passation diffère-t-elle d'un fan-out ?

<details markdown="1"><summary>Vérifier</summary>

Le fan-out est parallèle : l'orchestrateur lance plusieurs workers sur des variantes d'un même problème en même temps. La passation est séquentielle : un agent termine, puis transmet ses constats à un second agent adapté à la phase suivante. Le fan-out demande « comment explorer plus d'angles en parallèle ? » ; la passation demande « comment découper un processus séquentiel en phases spécialisées ? » Tous deux utilisent des sous-agents ; tous deux isolent le contexte ; tous deux répondent à « quand un seul agent ne suffit-il pas ? » mais à des rythmes différents.

</details>

## Exercices en situation réelle

- [ ] La prochaine fois que vous verrez une tâche complexe (recherche, planification, débogage), esquissez si elle relève de l'orchestrateur et worker (y a-t-il des sous-tâches indépendantes qui peuvent s'exécuter en parallèle ?), de la passation (y a-t-il des phases séquentielles pour différents spécialistes ?), ou d'un agent unique avec plus d'outils (un seul agent peut-il le faire avec de meilleurs outils et plus de tours ?). Ne construisez rien ; entraînez-vous seulement à reconnaître la forme.
- [ ] Lisez l'article source primaire : "How We Built Our Multi-Agent Research System". Concentrez-vous sur la section qui décrit ce qu'a fait l'orchestrateur, ce qu'a fait chaque worker, et ce qui aurait changé avec un agent unique. Prenez des notes sur un gain concret du parallélisme qu'ils rapportent.
- [ ] Demain : décrivez une vraie tâche de votre travail ou de vos études qui bénéficierait du fan-out (plusieurs workers explorant le même problème en parallèle). Quel angle prendrait chaque worker ? De quels outils chacun aurait-il besoin ?

## Pour aller plus loin

- [Billet : "How We Built Our Multi-Agent Research System", Anthropic Engineering](https://www.anthropic.com/engineering/multi-agent-research-system)
- [Ressources](../RESOURCES.md)

---

Ça ne passe pas ? Relisez la source primaire en haut de page, car cette leçon la condense et c'est dans la condensation que la compréhension s'échappe. Consultez le [glossaire](../GLOSSARY.md) pour tout terme qui vous a paru glissant.

Si c'est la leçon elle-même qui n'est pas claire plutôt que la matière, c'est un défaut : [ouvrez une issue](https://github.com/TokenCemetery/teach/issues).
