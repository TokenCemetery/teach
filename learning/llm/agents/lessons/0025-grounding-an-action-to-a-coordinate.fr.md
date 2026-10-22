---
title: "25. Ancrer une action à une coordonnée"
description: "Pourquoi traduire une intention visuelle en coordonnée de pixel est plus difficile et plus fragile qu'un argument typé d'appel d'outil"
type: lesson
---

# Leçon 25. Ancrer une action à une coordonnée

**Lien avec la mission :** Diagnostiquer un agent de computer use défaillant exige de reconnaître les erreurs d'ancrage (une coordonnée manquée) comme distinctes d'un mauvais usage d'outil ou d'une erreur de logique, pour corriger le bon problème.
**Source primaire :** [Doc : "Computer use tool", Claude Platform Docs](https://platform.claude.com/docs/en/agents-and-tools/tool-use/computer-use-tool)
**Prérequis :** [Leçon 24](0024-screenshots-as-observations.md)

## Échauffement

1. ▢ Dans un agent à appels d'outils, quand le modèle veut mettre à jour un utilisateur, que envoie-t-il au harness, et comment le harness sait-il quel utilisateur précis mettre à jour ?

<details markdown="1"><summary>Vérifier</summary>

Le modèle envoie un appel d'outil avec un argument comme `user_id: "u_123"`, un identifiant stable et unique. Le harness lit cet identifiant et met à jour l'utilisateur par son identifiant, sans ambiguïté.

</details>

2. ▢ Dans un agent de computer use, quand le modèle veut cliquer sur un bouton qu'il voit sur la capture d'écran, que envoie-t-il au harness, et comment le harness sait-il sur quel bouton cliquer ?

<details markdown="1"><summary>Vérifier</summary>

Le modèle envoie une action de clic à une coordonnée de pixel, comme `click(x=450, y=200)`. Le harness lit la coordonnée et clique à cette position exacte de l'écran.

</details>

## À savoir

### Le problème de l'ancrage

L'ancrage (grounding) est l'étape qui traduit l'intention du modèle en une coordonnée d'écran réelle. Quand un agent à appels d'outils veut mettre à jour un enregistrement, il le désigne par un identifiant stable, un nom ou un identifiant unique sur lequel le harness peut agir directement. Il n'y a aucune ambiguïté : le harness trouve l'enregistrement ou ne le trouve pas.

Quand un agent de computer use veut cliquer sur un bouton, il doit localiser visuellement ce bouton dans la capture d'écran courante, estimer ses coordonnées en pixels et émettre un tuple de coordonnées comme `(x, y)`. C'est plus difficile à quatre égards.

**Premièrement, il n'y a aucune référence stable.** Un bouton au pixel 450, 200 sur une capture d'écran est un autre bouton (ou aucun bouton) si la fenêtre est redimensionnée, si la page défile ou si le contenu se décale. Un identifiant persiste d'un changement de mise en page à l'autre ; une coordonnée non. Un agent à appels d'outils demanderait un bouton par son nom ; un agent de computer use demande un bouton par sa position, ce qui est fragile.

**Deuxièmement, le modèle ne peut pas demander de l'aide.** Dans un agent à appels d'outils, si le harness ne comprend pas un argument, il renvoie une erreur claire : « user_id u_999 not found » ou « invalid format for date_field ». Le modèle lit l'erreur et corrige son argument. Dans un agent de computer use, un clic à la mauvaise coordonnée touche simplement la mauvaise chose (ou de l'espace vide). Le modèle ne reçoit aucun message d'erreur. Il ne découvre qu'à la capture d'écran suivante que le clic est tombé au mauvais endroit, et même alors, il doit déduire par inspection visuelle que le clic a manqué.

**Troisièmement, la boucle de retour est lente.** Après qu'un agent à appels d'outils a commis une erreur, il reçoit un message d'erreur typé. Après qu'un agent de computer use a commis une erreur, il doit prendre une autre capture d'écran complète, l'envoyer au modèle, attendre que le modèle interprète la nouvelle image et raisonne sur ce qui a mal tourné, puis réessayer. Chaque erreur d'ancrage coûte un aller-retour complet avec le modèle pour être découverte et corrigée.

**Quatrièmement, de petits changements d'environnement brisent des séquences qui fonctionnaient.** Un appel d'outil qui désigne un utilisateur par son identifiant fonctionne encore si le nom, l'e-mail ou le service de l'utilisateur change. Un clic à des coordonnées casse si le bouton bouge ne serait-ce que de quelques pixels. Un écran de portable de 13 pouces, un moniteur de 27 pouces, le zoom du navigateur, le rendu des polices et les points de rupture CSS peuvent tous déplacer le même bouton à des coordonnées différentes. Une trajectoire qui fonctionnait parfaitement sur une machine peut échouer en silence sur une autre.

### Ce qui rend l'ancrage fragile

Imaginez qu'un agent clique avec succès sur une zone de recherche en (300, 150) dans un navigateur de bureau au zoom normal. La même page web vue sur un téléphone mobile ou avec le zoom du navigateur réglé à 125 pour cent peut afficher la zone de recherche en (225, 112) ou en (375, 188). La coordonnée n'est plus correcte. Le clic peut tomber sur rien, ou sur un tout autre élément.

La logique de l'agent était saine. Le modèle a pris une décision raisonnable. Le type d'action (clic) était correct. Mais la coordonnée était fausse, parce que l'environnement a changé. Un agent à appels d'outils qui demande un outil nommé `search` n'a pas ce problème, puisque le nom de l'outil est stable.

C'est pourquoi les erreurs d'ancrage sont une catégorie de défaillance propre aux agents pilotés par l'écran. Elles ne se produisent pas dans les agents à appels d'outils, parce que ceux-ci désignent les choses par leur nom, pas par leur position.

### Atténuation partielle : les outils conscients de la structure

Certains outils de navigateur ou de computer use essaient de réduire la fragilité de l'ancrage en offrant un compromis : au lieu d'une simple capture d'écran, l'outil renvoie aussi de l'information structurée sur les éléments de la page : les noms, les rôles, les positions et les cadres englobants de chaque bouton, lien et champ de formulaire.

Le modèle peut alors dire « clique sur le bouton intitulé "Submit" » ou « clique sur le champ de texte de la ligne e-mail », et le harness traduit cette référence nommée en coordonnée au moment du clic, au lieu de demander au modèle d'estimer des coordonnées à partir des pixels. Cela retrouve un peu de stabilité : si le bouton bouge, le harness calcule automatiquement de nouvelles coordonnées, sans que le modèle ait à réestimer.

C'est un compromis. Vous gagnez en fiabilité et perdez une partie de la généralité « fonctionne sur n'importe quelle interface graphique » qu'offre l'action purement fondée sur les captures d'écran. Un outil conscient de la structure fonctionne bien pour les pages web, où les éléments HTML ont des rôles sémantiques et des identifiants stables, mais peut ne pas fonctionner pour les applications de bureau, les jeux ou les applications obscures pour lesquelles l'outil n'a pas été conçu. Les actions purement fondées sur les captures d'écran n'ont pas cette limite, mais elles sont plus fragiles.

### Comment repérer les erreurs d'ancrage dans une trajectoire

Quand vous lisez la trajectoire d'un agent de computer use, cherchez des motifs :

- L'intention du modèle a du sens (il a décidé de chercher quelque chose, de remplir un champ, etc.), mais l'action n'a pas produit le résultat attendu.
- Plusieurs clics de suite tombent au mauvais endroit.
- La même action fonctionne sur une capture d'écran mais échoue sur la suivante.
- Les coordonnées sont loin de tout élément visible.

Ce sont les marques d'une erreur d'ancrage. Le modèle raisonnait correctement sur ce qu'il fallait faire, mais les coordonnées ne correspondaient pas à l'écran. C'est distinct d'une erreur de logique (le modèle a décidé de faire la mauvaise chose) ou d'une défaillance d'outil (l'outil a planté).

## Pratique

1. ▢ Un agent clique aux coordonnées (500, 250) pour soumettre un formulaire. La capture d'écran avant le clic montre un bouton Submit centré à peu près en (500, 250). L'action réussit et le formulaire est soumis. Au tour suivant, l'agent essaie de cliquer à nouveau sur le même bouton Submit aux mêmes coordonnées (500, 250), mais le formulaire a disparu et un message de chargement s'affiche. Le deuxième clic tombe sur rien. Est-ce une erreur d'ancrage ?

<details markdown="1"><summary>Vérifier</summary>

Non. Le premier clic était correctement ancré. Le deuxième clic a manqué parce que l'écran a changé, pas parce que le modèle a mal estimé la coordonnée. Les erreurs d'ancrage se produisent quand la coordonnée ne correspond pas à la cible visée sur la capture d'écran que le modèle regarde en ce moment. Une fois le contenu de la page changé, la coordonnée est devenue périmée, mais ce n'est pas une erreur d'ancrage dans la décision de l'agent ; c'est un comportement correct : l'agent a essayé de cliquer sur quelque chose qui n'était plus là.

</details>

2. ▢ Un agent lit une capture d'écran d'une page de connexion avec deux champs : le nom d'utilisateur en haut et le mot de passe en dessous. L'agent décide de saisir le mot de passe, estime que le champ du mot de passe se trouve approximativement en (350, 180), et envoie l'action `type(x=350, y=180)`. Le harness clique en (350, 180), qui est en réalité le champ du nom d'utilisateur, et le mot de passe est saisi dans le champ du nom d'utilisateur. L'agent voit alors une nouvelle capture d'écran montrant le champ du nom d'utilisateur maintenant rempli avec le mot de passe. Est-ce une erreur d'ancrage, une erreur de logique, ou les deux ?

<details markdown="1"><summary>Indice</summary>

Posez séparément deux questions : (1) Le modèle a-t-il pris une décision raisonnable sur ce qu'il fallait faire ? (2) Le modèle a-t-il trouvé les bonnes coordonnées ?

</details>

<details markdown="1"><summary>Vérifier</summary>

C'est une erreur d'ancrage, pas une erreur de logique. La décision du modèle était correcte : il a décidé de saisir le mot de passe. Mais le modèle a mal estimé les coordonnées du champ du mot de passe. La coordonnée (350, 180) était fausse ; le champ du mot de passe était en réalité plus bas à l'écran, peut-être en (350, 240). Le modèle voulait viser la bonne cible mais a mal ancré l'action.

</details>

3. ▢ Un agent de computer use interagit avec deux applications web différentes à la suite. Dans la première application, il remplit avec succès un formulaire en cliquant sur un champ en (400, 300). Dans la seconde application, il essaie de cliquer sur un champ de saisie qui semble se trouver à une position similaire de l'écran, aussi en (400, 300), mais dans la seconde application cette coordonnée est de l'espace vide et le clic ne tombe nulle part. Le second clic est-il une erreur d'ancrage ?

    - a) Oui, parce que la coordonnée ne correspondait pas à la cible visée sur la capture d'écran de la seconde application
    - b) Non, parce que le modèle a utilisé le même raisonnement pour les deux applications
    - c) Non, parce que la coordonnée a bien fonctionné la première fois, donc la seconde application doit avoir un bug d'interface
    - d) Non, parce que les erreurs d'ancrage ne se produisent que lorsque le modèle essaie intentionnellement de cliquer sur la mauvaise chose

<details markdown="1"><summary>Vérifier</summary>

**a)** Le clic a été mal ancré : la coordonnée ne correspondait pas à la cible visée sur la capture d'écran courante de la seconde application. Le fait que la même coordonnée ait fonctionné dans une autre application n'a aucune pertinence ; l'ancrage concerne la correspondance entre l'intention et la coordonnée sur l'écran qui se trouve devant le modèle en ce moment. **b)** est faux parce que ce n'est pas le raisonnement du modèle qui fait qu'un clic est ancré ou non, seulement le fait que la coordonnée tombe ou non sur la cible visée. **c)** est faux parce qu'une coordonnée qui a fonctionné une fois ne dit rien sur sa justesse sur un autre écran ; c'est le modèle qui a supposé une stabilité qu'il n'aurait pas dû supposer. **d)** est faux parce que les erreurs d'ancrage sont des erreurs, pas des choix intentionnels.

</details>

4. ▢ Vous lisez une trajectoire où un agent n'a pas réussi à accomplir une tâche. Au tour sept, l'agent a cliqué en (1200, 50), en haut à droite de l'écran. Rien de visible ne s'y trouve, et le clic n'a eu aucun effet. Le modèle a alors dit qu'il n'avait pas trouvé le bouton qu'il cherchait. Au tour suivant, l'agent a cliqué en (150, 50), en haut à gauche, et a trouvé le bouton. Formulez une hypothèse sur ce qui a mal tourné au tour sept.

<details markdown="1"><summary>Vérifier</summary>

L'agent s'est probablement trompé sur la position du bouton et a ancré le clic trop à droite. Le bouton se trouvait en réalité sur le côté gauche de l'écran, mais le modèle a estimé qu'il était à droite. C'est une erreur d'ancrage classique : l'intention du modèle (trouver et cliquer sur le bouton) était juste, mais la coordonnée était fausse. L'agent s'est corrigé au tour suivant, peut-être en relisant la capture d'écran ou en reconsidérant son estimation.

</details>

## Exercices en situation réelle

- [ ] Prenez une capture d'écran d'une page web au zoom normal. Choisissez un bouton et notez ses coordonnées en pixels telles que vous les estimez. Zoomez maintenant le navigateur de 25 pour cent et prenez une nouvelle capture d'écran. Cherchez les coordonnées du même bouton sur la capture zoomée avec les outils de développement de votre navigateur (inspectez l'élément et vérifiez son cadre englobant). Notez les nouvelles coordonnées. De combien votre estimation s'écartait-elle des coordonnées réelles sur la première capture ? Comment le zoom a-t-il changé la position ?

- [ ] Regardez ou lisez la trajectoire d'un agent de computer use (issue d'un blog, d'une documentation d'outil ou d'un exemple). Pour trois actions consécutives, comparez ce que l'agent voulait faire (d'après le contexte ou le prompt) avec les coordonnées qu'il a émises et la capture d'écran qui a suivi. L'ancrage correspondait-il à l'intention ? Sinon, qu'est-ce qui a changé les coordonnées ?

- [ ] Demain : concevez un formulaire web simple (mentalement ou en code) qui, selon vous, serait difficile à ancrer correctement pour un agent de computer use. Quelles propriétés du formulaire rendent l'ancrage fragile ? Concevez ensuite une seconde version du même formulaire qui serait plus facile à ancrer, et expliquez ce que vous avez changé.

## Pour aller plus loin

- [Doc : "Computer use tool", Claude Platform Docs](https://platform.claude.com/docs/en/agents-and-tools/tool-use/computer-use-tool)
- [Ressources](../RESOURCES.md)

---

Ça ne passe pas ? Relisez la source primaire en haut de page, car cette leçon la condense et c'est dans la condensation que la compréhension s'échappe. Consultez le [glossaire](../GLOSSARY.md) pour tout terme qui vous a paru glissant.

Si c'est la leçon elle-même qui n'est pas claire plutôt que la matière, c'est un défaut : [ouvrez une issue](https://github.com/TokenCemetery/teach/issues).
