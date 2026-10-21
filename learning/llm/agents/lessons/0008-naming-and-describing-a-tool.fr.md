---
title: "8. Nommer et décrire un outil"
description: "Le nom et la description d'un outil sont ce que le modèle lit pour décider quand et comment l'appeler"
type: lesson
---

# Leçon 8. Nommer et décrire un outil

**Lien avec la mission :** Concevoir la surface d'outils d'un agent (noms, descriptions, formes de retour et frontière de permissions qui décide ce qu'il peut faire sans surveillance) commence par comprendre que les noms et les descriptions ne sont pas de la documentation d'API pour un humain : c'est une surface de prompt que le modèle lit pour décider quand et comment appeler un outil.
**Source primaire :** [Billet : "Writing Effective Tools for Agents", Anthropic Engineering](https://www.anthropic.com/engineering/writing-tools-for-agents)
**Prérequis :** [Leçon 7](0007-the-transcript-as-state.md), [Outil](../GLOSSARY.md)

## Échauffement

1. ▢ Depuis la leçon 7 : comment le modèle « se souvient »-il de ce qui s'est passé à un tour précédent de la boucle d'agent ?

<details markdown="1"><summary>Vérifier</summary>

Il ne se souvient pas de lui-même. Le harness renvoie le transcript complet à chaque appel, donc ce qui ressemble à de la mémoire est en réalité le modèle qui relit tout ce qu'on lui a montré avant.

</details>

2. ▢ Depuis la leçon 7 : pourquoi le transcript est-il l'état complet de l'agent, et pas une autre structure de données que le harness détiendrait à part ?

<details markdown="1"><summary>Vérifier</summary>

Parce que le modèle ne voit jamais que le transcript. Tout fait que le harness connaît mais n'y ajoute jamais est invisible pour le modèle, quoi que le harness suive d'autre en interne.

</details>

## À savoir

### Une description d'outil n'est pas de la documentation d'API

Une erreur que tout concepteur commet une fois : écrire une description d'outil comme on écrirait la docstring d'un endpoint REST.

```text
Bad:
name: fetch_user
description: Fetches user data
```

C'est trop laconique pour un modèle qui choisit parmi plusieurs outils. Le modèle n'a aucun contexte pour savoir quand utiliser `fetch_user` plutôt que `get_user` ou `lookup_user`. Il ne sait pas quelles données reviennent ni ce qu'il faut fournir. Il ne peut pas décider s'il faut l'appeler maintenant ou plus tard. Quand le modèle voit trois outils sans indication claire, il devine, et devine faux plus souvent qu'un humain.

Voici le même outil décrit pour un modèle :

```text
Better:
name: fetch_user
description: Look up a user profile by their numeric ID. Returns the user's name, email, account status, and the current version number of their profile. Use this before calling update_user, since update_user requires you to pass the profile's current version number to prevent write conflicts. Returns null if the user ID does not exist.
```

Le modèle voit maintenant le tableau complet : quand l'appeler (avant update_user), ce dont il a besoin (un identifiant numérique) et ce qu'il obtient en retour (assez d'information pour décider de la suite). Cette description sert la prise de décision du modèle, pas un humain qui lit de la documentation d'API.

La différence est la suivante : une docstring REST explique à un programmeur humain comment utiliser un outil. Une description d'outil dans le prompt d'un agent dit à un modèle quand et pourquoi appeler un outil, quoi lui passer et quel résultat attendre. Le modèle n'a pas de manuel ; votre description est son seul guide.

### Se distinguer nettement des autres outils

Le modèle choisit parmi les outils en lisant leurs noms et leurs descriptions, sans autre signal. Si deux outils se ressemblent, le modèle appellera le mauvais ou appellera les deux par précaution.

```text
Bad:
- name: list_files
  description: Lists files in a directory
- name: list_file_contents
  description: Lists the contents of a file
```

Le modèle risque de les confondre ou d'appeler les deux alors qu'il n'en faut qu'un. Les noms sont trop proches.

```text
Better:
- name: list_directory
  description: List all files and subdirectories in a directory. Shows names and file sizes. Does not show file contents.
- name: read_file
  description: Read the complete contents of a single file. Returns text as a string.
```

Maintenant les noms sont distincts (list_directory contre read_file) et les descriptions précisent ce que chacun fait et ne fait pas. Le modèle choisira le bon.

La règle : le nom d'un outil doit dire ce qu'il fait d'une façon qui ne puisse être confondue avec aucun autre outil du même jeu d'outils. Si vous avez plusieurs outils de recherche, ne les appelez pas tous `search`. Appelez-les `search_documentation`, `search_code`, `search_logs`.

### Les descriptions de paramètres comptent de la même façon

La description de l'outil au niveau supérieur attire le plus d'attention, mais les descriptions de paramètres sont tout aussi importantes pour la justesse.

```text
Bad:
name: create_issue
description: Creates a GitHub issue
parameters:
  - name: title
    type: string
    description: Issue title
  - name: body
    type: string
    description: Issue body
```

Le modèle ne sait pas quel format doit avoir le titre, quelle longueur il peut avoir, s'il doit être une question ou une affirmation. Le corps est pire encore : est-ce du Markdown ? Du texte brut ? Avec quel niveau de détail ? Le modèle décrit-il le problème ou la solution ?

```text
Better:
name: create_issue
description: Create a new issue in the repository
parameters:
  - name: title
    type: string
    description: A one-line summary of the problem or feature request. Be specific and actionable. Examples: "Handle null config values in startup" or "Add support for JSON output format".
  - name: body
    type: string
    description: Detailed description in Markdown. Include what you tried, what failed, and what you expect to happen. If it is a feature request, explain why it matters. If it is a bug, include steps to reproduce.
```

Maintenant le modèle sait quel genre de titre écrire et quel niveau de détail mettre dans le corps. Il produira de meilleurs résultats.

### Un échec courant : des outils semblables qui perturbent le modèle

Le pire cas est celui où deux outils sont assez semblables pour que le modèle ne puisse pas les distinguer, même avec des descriptions.

```text
Very bad:
- name: update_user
  description: Update user information
- name: change_user
  description: Modify user data
```

Ces noms et ces descriptions disent presque la même chose. Le modèle risque d'appeler les deux, d'appeler le mauvais ou de perdre du temps à demander. Vous ne lui avez donné aucun moyen de choisir.

La correction consiste à rendre les noms et les descriptions si différents qu'un seul a du sens pour la tâche en cours :

```text
Better:
- name: update_user_profile
  description: Change a user's displayed name, email, or profile picture. Requires the profile version number to prevent conflicts.
- name: update_user_permissions
  description: Grant or revoke access roles for a user, such as admin, editor, or viewer. Only callable by the current account's admin.
```

Maintenant le modèle voit que le premier outil sert aux informations personnelles et le second au contrôle d'accès. Il choisira le bon.

## Pratique

1. ▢ Vous avez deux outils : `send_email` et `send_notification`. Le modèle appelle parfois les deux alors qu'il n'en faut qu'un. Écrivez une phrase pour chaque outil qui indique clairement au modèle lequel utiliser et quand.

<details markdown="1"><summary>Vérifier</summary>

Réponses possibles : `send_email` pourrait être « Send an email message to an email address. Use this for messages longer than a few lines or when you need to include attachments or formatted text. » `send_notification` pourrait être « Send a brief in-app notification to a user. Use this for short status updates or alerts that do not require the user to leave the application. » L'essentiel est que la description dise au modèle quel type de message chaque outil attend, pour qu'il puisse choisir correctement.

</details>

2. ▢ Votre outil `get_user` renvoie tous les champs d'un enregistrement utilisateur : id, nom, e-mail, téléphone, adresse, entreprise, biographie, préférences, niveau d'abonnement, et dix autres. Une description de paramètre doit guider le modèle sur ce qu'il faut passer. Que ne faut-il PAS mettre dans la description ?

<details markdown="1"><summary>Indice</summary>

Pensez à ce dont le modèle a besoin pour appeler correctement l'outil, par opposition à ce qui est agréable à savoir mais pas nécessaire pour l'appel lui-même.

</details>

<details markdown="1"><summary>Vérifier</summary>

Il ne faut PAS lister tous les champs que l'outil renvoie. La description de l'outil dit ce que le modèle obtient en retour ; la description du paramètre dit ce que le modèle doit fournir pour l'appeler. Pour un paramètre `user_id`, la description devrait dire quelque chose comme « The numeric ID of the user. If you do not have the ID, call search_users first. » Ne listez pas les champs renvoyés dans la description du paramètre ; cela va dans la description de l'outil au niveau supérieur.

</details>

3. ▢ Laquelle des raisons suivantes est la meilleure pour écrire des descriptions détaillées des paramètres d'un outil ?

    - a) Se conformer aux standards de documentation d'API
    - b) Aider les ingénieurs humains qui liront le code plus tard
    - c) Aider le modèle à décider quelle valeur passer et s'il faut même appeler l'outil
    - d) Réduire le nombre d'appels d'outils que l'utilisateur doit faire

<details markdown="1"><summary>Vérifier</summary>

**c)** Aider le modèle à décider quelle valeur passer et s'il faut même appeler l'outil. Le modèle lit les descriptions de paramètres pour comprendre quels arguments un outil attend et ce qui se passera s'il passe la mauvaise valeur. (a) est hors sujet : c'est du prompt engineering, pas de la conception d'API. (b) peut être un bénéfice secondaire, mais ce n'est pas la raison principale. (d) manque l'essentiel : des descriptions détaillées aident le modèle à faire moins d'appels erronés, pas moins d'appels en tout.

</details>

4. ▢ Vous construisez un outil appelé `search`. Vous avez aussi des outils appelés `search_documents`, `search_issues` et `search_users`. Pourquoi ce nommage pose-t-il problème, et que faut-il faire à la place ?

<details markdown="1"><summary>Vérifier</summary>

L'outil `search` est trop générique. Le modèle ne saura pas quel outil de recherche appeler quand il doit chercher. Il risque de tous les appeler, ou d'en choisir un au hasard. Renommez plutôt `search` en quelque chose de précis comme `search_logs`, `search_comments` ou `search_code`. La règle : chaque nom d'outil doit être assez précis pour que le modèle sache ce qu'il fait, et assez différent des autres noms d'outils pour que le modèle ne le confonde pas.

</details>

## Exercices en situation réelle

- [ ] Trouvez les définitions d'outils (nom et description) d'une application LLM ou d'un framework d'agents que vous utilisez. Lisez la description de chaque outil. Notez un outil dont la description est assez claire pour que vous compreniez quand le modèle doit l'appeler, et un outil dont la description est trop vague. Notez pourquoi le premier fonctionne et ce qui manque au second.

- [ ] Choisissez un outil que vous utilisez régulièrement en ligne de commande (comme `grep` ou `find`). Imaginez que vous deviez le décrire à un modèle qui ne sait rien de votre système de fichiers. Écrivez une description d'une phrase qui dit au modèle ce que fait l'outil et quand l'utiliser plutôt qu'un outil semblable.

- [ ] Demain : prenez une description d'outil tirée d'un vrai agent ou d'une documentation d'API que vous jugez mal écrite. Réécrivez-la pour un modèle qui choisit parmi plusieurs outils semblables. Rendez-la au moins deux fois plus longue, incluez un exemple de cas où l'utiliser, et dites une chose pour laquelle il n'est PAS adapté.

## Pour aller plus loin

- [Billet : "Writing Effective Tools for Agents", Anthropic Engineering](https://www.anthropic.com/engineering/writing-tools-for-agents)
- [Ressources](../RESOURCES.md)

---

Ça ne passe pas ? Relisez la source primaire en haut de page, car cette leçon la condense et c'est dans la condensation que la compréhension s'échappe. Consultez le [glossaire](../GLOSSARY.md) pour tout terme qui vous a paru glissant.

Si c'est la leçon elle-même qui n'est pas claire plutôt que la matière, c'est un défaut : [ouvrez une issue](https://github.com/TokenCemetery/teach/issues).
