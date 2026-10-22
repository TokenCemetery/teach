---
title: "22. Sandboxing et points d'approbation"
description: "Frontières d'exécution et points de contrôle humains qui protègent contre les erreurs du modèle"
type: lesson
---

# Leçon 22. Sandboxing et points d'approbation

**Lien avec la mission :** Pour décider ce que l'agent peut faire sans surveillance, il faut comprendre les deux mécanismes complémentaires qui protègent contre les erreurs : les sandboxes imposent ce que le code peut atteindre quoi que le modèle demande, et les points d'approbation ajoutent un point de contrôle humain avant les actions à enjeux élevés.
**Source primaire :** [Billet : "Building Effective Agents", Anthropic Engineering](https://www.anthropic.com/engineering/building-effective-agents)
**Prérequis :** [Leçon 21](0021-provider-formats-and-discovery-at-scale.md), [Harness](../GLOSSARY.md)

## Échauffement

1. ▢ Quelle est la différence entre un outil client et un outil serveur, en termes d'endroit où le code s'exécute et de qui le contrôle ?

<details markdown="1"><summary>Vérifier</summary>

Un outil client s'exécute dans le code propre du harness, donc vous contrôlez entièrement son exécution. Un outil serveur s'exécute sur l'infrastructure du fournisseur pour le compte du harness, donc c'est le fournisseur qui contrôle la frontière d'exécution. Cela compte pour la sécurité, parce que le comportement d'un outil client dépend de votre code, alors que celui d'un outil serveur dépend de ce que le fournisseur autorise.

</details>

2. ▢ Dans la leçon 21, nous avons appris qu'au lieu de précharger chaque définition d'outil en contexte, le modèle peut découvrir et appeler des outils dynamiquement. Nommez un bénéfice de cette approche et un coût qu'elle introduit.

<details markdown="1"><summary>Vérifier</summary>

Bénéfice : le contexte du modèle n'explose pas sous des centaines de définitions d'outils, donc il peut raisonner plus clairement et les définitions d'outils peuvent rester petites ou être récupérées à la demande. Coût : le modèle doit maintenant appeler d'abord un outil de découverte ou d'introspection avant de savoir ce qui est disponible, ce qui ajoute un aller-retour, ou bien il appelle un outil dont il devine l'existence et échoue s'il n'existe pas, ce qui exige une gestion d'erreurs et des nouveaux essais.

</details>

## À savoir

### Le jugement d'un modèle n'est pas une frontière de sécurité

Vous pourriez espérer : « Le modèle saura se montrer malin avec l'accès que je lui donne. Je peux compter sur le modèle pour décider de ne pas supprimer de données de production ni d'envoyer des e-mails sans permission. »

Cet espoir se brise de plusieurs façons. Un modèle peut se tromper : il peut mal comprendre les conséquences d'un appel d'outil. Un modèle peut être manipulé par le contenu qu'il lit : si l'aperçu d'un fichier ou un message d'utilisateur contient du texte hostile conçu pour tromper le modèle, ce texte peut influencer son raisonnement. Un modèle peut simplement faire une erreur : le raisonnement peut échouer à grande échelle, surtout dans des scénarios très ramifiés ou sous pression temporelle. Pour ces raisons, tout ce que votre harness autorise réellement un outil à toucher (quels fichiers sur le disque, quels hôtes réseau, quelles commandes exécuter) doit être imposé par du code, pas par l'espoir que le modèle se comporte correctement.

C'est pourquoi la frontière de sécurité est le harness, pas le modèle.

### Ce qu'est un sandbox

Un sandbox est une frontière d'exécution que le harness impose autour de ce que le code d'un outil peut atteindre, quels que soient les arguments envoyés par le modèle. Les instructions du modèle ne sont jamais elles-mêmes une propriété de sécurité.

Les frontières de sandbox courantes comprennent :

- **Frontière du système de fichiers** : l'outil ne peut lire ou écrire que des fichiers dans une arborescence de répertoires précise (par exemple `/home/user/work` mais pas `/etc` ni `/home/other_user`). Même si le modèle demande à l'outil d'accéder à un chemin hors de cette arborescence, le sandbox le rejette à l'exécution.
- **Isolation réseau** : l'outil n'a aucun accès réseau, ou ne peut joindre qu'une liste blanche d'hôtes précis. Le modèle ne peut pas convaincre le harness de le laisser joindre des domaines arbitraires.
- **Limites de ressources** : le temps CPU, la mémoire et le temps réel sont plafonnés. Si le code du modèle se retrouve bloqué dans une boucle infinie, le sandbox le termine au lieu de consommer toutes les ressources.
- **Isolation des processus** : l'outil s'exécute dans un processus ou un conteneur distinct avec des privilèges réduits, de sorte qu'il ne peut pas affecter le harness ni accéder à des ressources système qui ne lui ont pas été explicitement accordées.

L'idée clé est que ces frontières sont imposées à l'exécution, dans le code du harness, pas au niveau du langage. Un outil ne peut pas s'échapper d'un sandbox en écrivant du code astucieux. Le sandbox est la règle que le harness applique, pas une fonctionnalité que l'outil respecte.

### Ce qu'est un point d'approbation

Un point d'approbation est un mécanisme complémentaire : avant d'exécuter un appel d'outil appartenant à une catégorie risquée, le harness se met en pause et attend qu'un humain examine l'appel précis et l'approuve ou le rejette.

Les points d'approbation s'appliquent aux actions qui présentent ces propriétés :

- Irréversibles ou difficiles à annuler : supprimer des fichiers, envoyer des e-mails, effectuer des transactions financières, publier sur internet.
- À forte conséquence en cas d'erreur : l'enjeu est de l'argent réel, des dégâts réels ou une exposition réelle de la vie privée.
- Réellement difficiles à prévoir : la décision du modèle est raisonnable mais pas manifestement correcte, donc le jugement humain vaut d'être ajouté.

Un point d'approbation met la boucle d'agent en pause et présente à un humain l'appel d'outil en attente (avec ses arguments et son effet attendu), attend l'approbation ou le rejet, puis reprend ou arrête la boucle en conséquence.

### Sandboxes et points d'approbation sont complémentaires, pas des alternatives

Ce sont deux protections différentes qui fonctionnent ensemble :

- Un sandbox limite les dégâts que n'importe quel appel peut causer, même approuvé ou exécuté automatiquement. Si un appel tourne mal d'une manière ou d'une autre, le sandbox contient le rayon d'action. « Cela s'exécute dans un environnement restreint » est toujours vrai.
- Un point d'approbation ajoute un point de décision humain pour les appels aux enjeux les plus élevés. Il n'empêche pas tous les dégâts ; il garantit seulement que les appels les plus susceptibles de causer des regrets passent d'abord sous des yeux humains.

Si vous placez chaque appel dans un sandbox mais ne mettez jamais de point d'approbation, une erreur de modèle non détectée peut encore causer du tort dans les limites du sandbox. Si vous mettez un point d'approbation sur chaque appel d'outil, l'agent cesse d'être autonome et devient un humain qui fait tout le travail avec des étapes en plus, ce qui défait l'intérêt de l'automatisation.

Le bon équilibre : mettre un point d'approbation sur une classe étroite d'actions réellement à enjeux élevés (supprimer, envoyer, publier, dépenser) où le jugement humain vaut le coût de latence, et placer tout dans un sandbox pour que tout ce qui est hors de ce point d'approbation ne puisse pas sortir de ses frontières même si quelque chose tourne mal.

## Pratique

1. ▢ Vous construisez un agent qui peut lire et résumer des documents d'un dépôt partagé. Le dépôt contient 10 000 fichiers, et certains contiennent des données clients sensibles auxquelles l'agent ne doit pas accéder. Vous voulez ajouter un outil client qui permet à l'agent de lire des fichiers. Quelle frontière de sandbox faut-il imposer, et pourquoi ?

<details markdown="1"><summary>Vérifier</summary>

Il faut imposer une frontière du système de fichiers : l'outil ne peut lire que des fichiers d'une arborescence de répertoires approuvée précise (par exemple tous les fichiers du dossier « public_docs » mais rien dans le dossier « confidential »). Cette frontière est vérifiée à l'exécution quand le modèle appelle l'outil ; même si le modèle demande à l'outil de lire un chemin du dossier confidentiel, le sandbox le rejette. Cela protège contre le modèle trompé par le contenu d'un fichier ou commettant une erreur de raisonnement sur ce qu'il est sûr de lire. Le jugement du modèle (« cela a l'air public ») n'est pas la frontière ; c'est le code.

</details>

2. ▢ Votre agent peut écrire du code et l'exécuter dans un interpréteur Python en sandbox. Le sandbox limite le CPU à 30 secondes et la mémoire à 1 Go. Le modèle écrit un programme qui démarre une boucle infinie. Le sandbox l'arrêtera-t-il ?

<details markdown="1"><summary>Indice</summary>

Pensez à ce qui se passe quand la limite de CPU est dépassée pendant l'exécution du code, et à la possibilité pour le harness de détecter et d'imposer cette limite.

</details>

<details markdown="1"><summary>Vérifier</summary>

Oui, le sandbox l'arrêtera. Quand la limite de CPU de 30 secondes est atteinte, le harness termine le processus. Le code du modèle ne s'exécute jamais indéfiniment ; le sandbox impose la limite de ressources à l'exécution, pas à l'analyse ou à la compilation. C'est l'une des raisons pour lesquelles les limites de ressources sont essentielles dans un sandbox : elles empêchent même un code bien intentionné de consommer toutes les ressources.

</details>

3. ▢ Vous concevez un agent qui peut envoyer des e-mails pour le compte d'un utilisateur. Laquelle de ces raisons justifie bien d'ajouter un point d'approbation avant que l'agent n'envoie un e-mail ?

    - a) Le modèle pourrait écrire une ligne d'objet grammaticalement incorrecte.
    - b) Le modèle pourrait envoyer un e-mail au mauvais destinataire ou avec le mauvais contenu, et une fois envoyé, l'e-mail ne peut pas être « désenvoyé ».
    - c) Le modèle pourrait ralentir le serveur de messagerie.
    - d) Le modèle pourrait manquer d'idées sur l'e-mail à envoyer ensuite.

<details markdown="1"><summary>Vérifier</summary>

**b)** Le modèle pourrait envoyer un e-mail au mauvais destinataire ou avec le mauvais contenu, et une fois envoyé, l'e-mail ne peut pas être « désenvoyé ». C'est une action irréversible et à forte conséquence où le jugement humain vaut le coût de latence. L'option a n'est pas assez conséquente (le modèle sait bien rédiger). L'option c n'est pas une erreur du modèle (cela relève de la charge du système). L'option d n'a pas de sens (le modèle s'arrête quand on le lui demande).

</details>

4. ▢ Expliquez pourquoi un sandbox ne peut pas empêcher toutes les erreurs mais peut quand même être essentiel. Donnez un exemple.

<details markdown="1"><summary>Vérifier</summary>

Un sandbox impose des frontières sur les ressources que le code peut atteindre, pas sur les erreurs que le code commet. Par exemple, un sandbox peut empêcher un outil d'écrire dans `/etc/passwd` en rejetant l'écriture à l'exécution, mais il ne peut pas empêcher le modèle d'écrire le mauvais contenu dans un fichier approuvé, comme écraser un fichier de configuration dans `/home/user/config/` avec une syntaxe invalide. Le rôle du sandbox est de contenir les dégâts, pas de garantir la justesse. Les points d'approbation gèrent les décisions à enjeux élevés qui exigent un jugement humain ; les sandboxes gèrent les frontières d'exécution qui empêchent le rayon d'action de s'étendre hors de tout contrôle.

</details>

## Exercices en situation réelle

- [ ] Dessinez un schéma d'un appel d'outil : montrez le modèle, le harness, le code de l'outil et le sandbox qui l'entoure. Indiquez ce que le modèle contrôle (son raisonnement et son choix d'outil) et ce que le harness contrôle (la frontière).
- [ ] Listez trois outils de votre travail ou d'un système que vous utilisez chaque jour. Pour chacun, identifiez une action risquée (le cas échéant) qui bénéficierait d'un point d'approbation, et une frontière de sandbox qui aurait du sens.
- [ ] Demain : lisez l'article « Building Effective Agents » et notez un exemple concret de sandbox ou de point d'approbation. Expliquez en une phrase pourquoi ce choix de conception compte.

## Pour aller plus loin

- [Billet : "Building Effective Agents", Anthropic Engineering](https://www.anthropic.com/engineering/building-effective-agents)
- [Ressources](../RESOURCES.md)

---

Ça ne passe pas ? Relisez la source primaire en haut de page, car cette leçon la condense et c'est dans la condensation que la compréhension s'échappe. Consultez le [glossaire](../GLOSSARY.md) pour tout terme qui vous a paru glissant.

Si c'est la leçon elle-même qui n'est pas claire plutôt que la matière, c'est un défaut : [ouvrez une issue](https://github.com/TokenCemetery/teach/issues).
