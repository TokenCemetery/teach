---
title: "26. Pourquoi les agents de navigateur échouent différemment"
description: "Les agents pilotés par l'écran échouent de façons que les agents à appels d'outils ne connaissent pas, et pourquoi WebArena a créé un benchmark pour mesurer et étudier ces échecs"
type: lesson
---

# Leçon 26. Pourquoi les agents de navigateur échouent différemment

**Lien avec la mission :** Construire et diagnostiquer des agents pilotés par l'écran exige de comprendre que leurs modes de défaillance sont structurels, et pas seulement une question de meilleur prompting, afin d'investir dans des stratégies d'atténuation plutôt que dans des retouches de prompt.
**Source primaire :** [Article : "WebArena: A Realistic Web Environment for Building Autonomous Agents", Zhou et al., 2023](https://arxiv.org/abs/2307.13854)
**Prérequis :** [Leçon 25](0025-grounding-an-action-to-a-coordinate.md)

## Échauffement

1. ▢ Depuis la leçon 24 : pourquoi un agent de computer use doit-il travailler avec des pixels et des captures d'écran plutôt qu'avec des appels d'outils nommés ?

<details markdown="1"><summary>Vérifier</summary>

Parce qu'il doit manipuler n'importe quelle application graphique, y compris celles qui n'ont jamais été conçues avec une API ou une intégration d'agent en tête. Un agent de computer use interagit par l'écran comme le fait un humain, donc il fonctionne partout.

</details>

2. ▢ Depuis la leçon 25 : nommez une raison pour laquelle une coordonnée de pixel est une référence plus fragile qu'un argument d'appel d'outil.

<details markdown="1"><summary>Vérifier</summary>

Une coordonnée casse quand la mise en page change (redimensionnement de la fenêtre, défilement de la page, niveau de zoom), alors qu'un argument comme un identifiant d'utilisateur ou un nom d'enregistrement persiste. Une coordonnée casse aussi en silence quand elle tombe sur la mauvaise chose, alors qu'un appel d'outil reçoit une erreur explicite.

</details>

## À savoir

### Modes de défaillance propres aux agents pilotés par l'écran

Un agent à appels d'outils échoue quand il appelle le mauvais outil, passe des arguments incorrects ou manque de tours. Un agent piloté par l'écran (à base de navigateur ou de computer use) échoue de toutes ces façons, et aussi de façons que les agents à appels d'outils ne peuvent tout simplement pas connaître.

**Erreurs d'ancrage** (leçon 25) : l'intention du modèle est correcte mais les coordonnées sont fausses, ce qui fait tomber le clic sur le mauvais élément ou sur de l'espace vide. Un agent à appels d'outils n'a pas ce problème parce qu'il désigne les choses par leur nom.

**Obstacles environnementaux** : une fenêtre popup, une bannière de cookies, un indicateur de chargement, une boîte de dialogue modale ou un message d'erreur peut bloquer la prochaine action de l'agent. Un agent à appels d'outils peut ne jamais en rencontrer parce qu'un appel d'API réussit ou échoue simplement proprement. Un agent piloté par l'écran doit contourner les obstacles avant de pouvoir poursuivre la tâche proprement dite.

**Complexité de la vérification** : quand un appel d'outil se termine, le harness récupère un résultat structuré avec un champ de statut. Le harness sait instantanément s'il a réussi. Quand un agent de computer use clique sur un bouton, rien ne se passe immédiatement sauf que l'écran change. Le harness doit prendre une nouvelle capture d'écran, l'envoyer au modèle, et faire raisonner le modèle sur la réussite ou non du clic. Cette étape d'interprétation est plus lente et moins fiable qu'un code de statut structuré.

**Variance de la mise en page** : la même application web s'affiche différemment selon la taille d'écran, le navigateur, le niveau de zoom, le framework CSS et l'état du serveur. Un agent entraîné ou testé sur un bureau au zoom normal peut échouer sur un téléphone mobile ou avec un zoom à 150 pour cent. Les changements de mise en page cassent les coordonnées et exigent de réancrer.

Ces défaillances ne sont pas dues à un mauvais modèle ni à un prompting insuffisant. Ce sont des conséquences structurelles du fait d'observer et d'agir à travers des pixels plutôt que des API.

### Pourquoi WebArena compte

Pendant des années, les agents de computer use ont été évalués sur des anecdotes : un éditeur montrait une vidéo d'un agent faisant quelque chose d'impressionnant, mais il n'existait aucun moyen systématique de mesurer si les agents progressaient réellement, ni où se situaient les plus gros problèmes de fiabilité. Différents éditeurs utilisaient différents environnements, donc les résultats n'étaient pas comparables. Il était difficile de séparer le vrai progrès du marketing.

L'article WebArena (Zhou et al., 2023) a créé un environnement de benchmark standardisé et auto-hébergé : un ensemble réaliste de sites web et d'applications web installé sur un serveur privé, avec des consignes de tâches et des vérifications de correction. Le travail d'un agent est d'accomplir des tâches comme réserver un vol, publier un avis ou configurer un paramètre. Une tâche n'est considérée comme réussie que si les actions de l'agent produisent le résultat correct et vérifiable (un vol est réservé, un avis est publié).

WebArena a rendu trois choses possibles :

D'abord, il a exposé le véritable écart de fiabilité. Les agents pilotés par l'écran qui semblaient impressionnants dans les vidéos marketing avaient des taux de réussite de l'ordre de 10 à 20 pour cent sur des tâches web réalistes en plusieurs étapes. Ce fut un électrochoc : la technologie était bien moins fiable que ne le suggéraient les anecdotes.

Ensuite, il a permis aux chercheurs de mesurer quels modes de défaillance dominent. En exécutant de nombreuses trajectoires d'agents et en catégorisant les échecs, les chercheurs ont constaté que les erreurs d'ancrage, les obstacles environnementaux et les décalages de mise en page représentaient une grande part des échecs, pas les erreurs de logique ni le manque de raisonnement. Cela a orienté l'effort vers des atténuations qui aident réellement.

Enfin, il a fourni un standard partagé. Différentes équipes pouvaient exécuter leurs agents sur le même benchmark et comparer les résultats. Le progrès est devenu mesurable au lieu d'être déclaré.

### Atténuations et compromis

Plusieurs stratégies réduisent les défaillances des agents pilotés par l'écran, chacune avec ses coûts :

**Outils conscients de la structure** (mentionnés dans la leçon 25) : au lieu d'une simple capture d'écran brute, l'outil renvoie de l'information structurée sur les éléments de la page (boutons, champs de formulaire, leurs noms et positions). Le modèle désigne les éléments par leur nom plutôt que par des coordonnées. Le harness traduit le nom en coordonnées au moment de l'action. Cela retrouve de la fiabilité parce que le harness peut recalculer les coordonnées si la mise en page change, sans demander au modèle de réestimer.

Compromis : vous perdez la généralité « fonctionne sur n'importe quelle interface graphique ». Les outils conscients de la structure fonctionnent pour les pages web à HTML sémantique mais échouent pour les applications de bureau, les PDF, les jeux ou les interfaces pour lesquelles l'outil n'a pas été conçu.

**Interaction explicite avec les éléments** : au lieu d'émettre des coordonnées de pixels, le modèle émet une référence comme « clique sur l'élément d'identifiant submit_button » ou « remplis le champ intitulé email ». Le harness utilise les API du navigateur (JavaScript, arbres d'accessibilité ou inspection du DOM) pour trouver l'élément et interagir avec lui.

Compromis : le harness redevient propre à une application. Il faut construire l'outillage pour la plateforme qui vous intéresse (web, bureau, mobile).

**Détection et récupération d'obstacles** : l'agent vérifie périodiquement si une fenêtre popup ou une bannière bloque l'interface et prend des mesures pour la fermer ou l'écarter avant de poursuivre.

Compromis : ajoute de la complexité et de la latence ; exige que l'agent reconnaisse des obstacles dont on ne lui a pas explicitement parlé.

**Vérification en plusieurs étapes** : après chaque action, l'agent prend une capture d'écran et un tour de raisonnement supplémentaire (non compté dans les tours de la tâche principale) pour vérifier que l'action a réussi comme prévu avant de continuer.

Compromis : augmente l'usage de tokens et la latence.

L'idée clé est qu'aucune atténuation unique ne corrige toutes les défaillances. Chacune traite un ou deux modes de défaillance mais introduit de la complexité ou perd en généralité. Un système de production en combine souvent plusieurs.

### Comment cela façonne le diagnostic

Quand un agent piloté par l'écran échoue, connaître ces modes de défaillance façonne la façon de diagnostiquer :

- Si la trajectoire montre une suite de clics qui ont du sens mais tombent aux mauvais endroits, soupçonnez des erreurs d'ancrage et de la variance de mise en page.
- Si la trajectoire montre l'agent effectuant une action qui aurait dû fonctionner mais que la capture d'écran suivante ne montre aucun changement, cherchez des obstacles (popups, indicateurs de chargement) ou vérifiez que l'action s'est réellement exécutée.
- Si l'agent a fonctionné sur une machine ou à un niveau de zoom mais échoue sur une tâche identique dans une autre configuration, soupçonnez un rendu propre à l'environnement.
- Si l'agent accomplit la même tâche avec succès 80 pour cent du temps mais échoue parfois dans des conditions identiques, soupçonnez une instabilité due au timing (un élément dynamique pas encore chargé) ou à une variante de mise en page que vous n'avez pas encore vue.

C'est de la discipline de diagnostic : connaître les modes de défaillance probables vous évite d'ajouter des prompts à l'aveugle et vous oriente vers le vrai problème.

## Pratique

1. ▢ Un agent accomplit une tâche avec succès sur votre bureau au niveau de zoom normal. Quand vous lancez le même agent sur exactement le même site avec le zoom du navigateur réglé à 125 pour cent, il échoue dès le premier clic. Quel est le mode de défaillance le plus probable ?

<details markdown="1"><summary>Vérifier</summary>

Une erreur d'ancrage combinée à de la variance de mise en page. Au zoom normal, les coordonnées étaient correctes. À 125 pour cent de zoom, le même élément s'affichait à d'autres coordonnées. L'agent a estimé des coordonnées d'après l'apparence visuelle au nouveau niveau de zoom mais s'est probablement trompé, ou bien il a réutilisé les coordonnées d'une capture d'écran en cache au précédent niveau de zoom. La correction n'est pas un meilleur raisonnement ; c'est soit un outillage conscient de la structure qui recalcule les coordonnées, soit de s'assurer que l'agent prend une capture d'écran neuve au niveau de zoom courant.

</details>

2. ▢ La trajectoire d'un agent montre qu'il a cliqué avec succès sur un bouton au tour trois. Le bouton n'est plus visible sur la capture d'écran du tour quatre ; une boîte de dialogue modale est apparue. Au tour quatre, l'agent essaie de cliquer sur le même bouton aux mêmes coordonnées, et le clic tombe sur la modale. L'agent se plaint alors de ne pas trouver le bouton. La défaillance est-elle une erreur d'ancrage ?

<details markdown="1"><summary>Indice</summary>

L'ancrage était en fait correct au tour quatre ; les coordonnées pointaient toujours là où se trouvait le bouton auparavant. Le problème ne vient pas des coordonnées elles-mêmes.

</details>

<details markdown="1"><summary>Vérifier</summary>

Non, c'est un problème d'obstacle, pas une erreur d'ancrage. Le raisonnement de l'agent était sain : il a décidé que le bouton devait toujours être cliquable. L'ancrage était exact : les coordonnées pointaient correctement vers l'ancien emplacement du bouton. Mais l'environnement a changé (une modale est apparue), et l'agent n'a ni détecté ni géré l'obstacle. La correction est la détection et la récupération d'obstacles, pas une meilleure estimation des coordonnées.

</details>

3. ▢ Vous hésitez entre un outil de navigateur conscient de la structure (qui renvoie des noms et des positions d'éléments) et un outil de capture d'écran brute pour votre agent. Votre application est un tableau de bord JavaScript sur mesure aux éléments rendus dynamiquement, sans structure HTML sémantique, et dont les éléments bougent pendant les interactions. La documentation de l'outil dit que les outils conscients de la structure fonctionnent mieux sur des « applications web sémantiques et standard ». Lequel choisir ?

    - a) L'outil conscient de la structure, parce qu'il est plus récent et plus sophistiqué
    - b) L'outil de capture d'écran brute, parce que votre application n'est pas du HTML sémantique
    - c) L'outil conscient de la structure quand même, en l'augmentant de JavaScript sur mesure
    - d) L'un ou l'autre est équivalent pour des agents pilotés par l'écran

<details markdown="1"><summary>Vérifier</summary>

**b)** L'outil de capture d'écran brute est le meilleur choix pour une application sur mesure, non standard et dynamique. Les outils conscients de la structure reposent sur du HTML sémantique et des identifiants stables, que votre tableau de bord n'a peut-être pas. Une capture d'écran brute laisse le modèle interpréter visuellement l'interface dynamique. Le compromis est la fragilité de l'ancrage, mais tenter d'utiliser un outillage conscient de la structure sur une interface non prise en charge échouerait probablement de toute façon. **a)** est faux parce que plus récent ne veut pas dire meilleur pour votre cas. **c)** ajoute de la complexité ; si l'outil prend mal en charge votre interface, une augmentation sur mesure peut ne pas aider. **d)** est faux parce que les outils ont des modes de défaillance différents selon les types d'applications.

</details>

4. ▢ Vous faites passer un agent par le benchmark de WebArena et il réussit 15 pour cent des tâches. Vous améliorez le system prompt avec des instructions plus claires et des indications de raisonnement. À un nouveau test, il réussit 16 pour cent. Que vous dit cette petite amélioration sur la cause probable des échecs restants ?

<details markdown="1"><summary>Vérifier</summary>

Elle suggère que la plupart des échecs ne sont pas dus au raisonnement ni à la clarté des instructions. Les améliorations de prompting ont donné des gains minimes. Les échecs sont probablement structurels : erreurs d'ancrage, variance de mise en page, obstacles, problèmes de vérification ou d'autres facteurs que de meilleures instructions seules ne peuvent pas corriger. Pour progresser, il faudrait chercher quels modes de défaillance dominent réellement (en lisant des trajectoires) puis appliquer des atténuations ciblées comme un outillage conscient de la structure, la détection d'obstacles ou une meilleure estimation des coordonnées.

</details>

## Exercices en situation réelle

- [ ] Lisez le résumé et l'introduction de l'article WebArena (arxiv.org/abs/2307.13854). Listez les trois catégories de tâches mentionnées et notez un exemple de mode de défaillance décrit dans chacune.

- [ ] Prenez la trajectoire d'un agent de computer use ou de navigateur issue d'une source publique (documentation, blog, GitHub). Catégorisez chaque échec (le cas échéant) comme : erreur d'ancrage, obstacle environnemental, échec de vérification, variance de mise en page ou erreur de logique. Quelle catégorie apparaît le plus souvent ?

- [ ] Demain : concevez un scénario de test qui exposerait spécifiquement les erreurs d'ancrage. Quelles propriétés la page web ou l'interface de test devrait-elle avoir ? Concevez ensuite un autre scénario qui exposerait les échecs de gestion d'obstacles. Écrivez un paragraphe décrivant comment vous mesureriez si un agent gère correctement les obstacles.

## Pour aller plus loin

- [Article : "WebArena: A Realistic Web Environment for Building Autonomous Agents", Zhou et al., 2023](https://arxiv.org/abs/2307.13854)
- [Ressources](../RESOURCES.md)

---

Ça ne passe pas ? Relisez la source primaire en haut de page, car cette leçon la condense et c'est dans la condensation que la compréhension s'échappe. Consultez le [glossaire](../GLOSSARY.md) pour tout terme qui vous a paru glissant.

Si c'est la leçon elle-même qui n'est pas claire plutôt que la matière, c'est un défaut : [ouvrez une issue](https://github.com/TokenCemetery/teach/issues).
