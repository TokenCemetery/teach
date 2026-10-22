---
title: "9. Formes de retour et surcharge du jeu d'outils"
description: "La valeur de retour d'un outil consomme du budget de contexte, et trop d'outils nuit à la capacité du modèle à choisir correctement"
type: lesson
---

# Leçon 9. Formes de retour et surcharge du jeu d'outils

**Lien avec la mission :** Concevoir la surface d'outils d'un agent inclut de choisir ce qu'un outil renvoie (sa forme de retour) et de décider combien d'outils offrir, car ce sont deux choix de conception qui affectent la capacité du modèle à décider correctement parmi ses options et le coût de chaque tour qui suit.
**Source primaire :** [Billet : "Writing Effective Tools for Agents", Anthropic Engineering](https://www.anthropic.com/engineering/writing-tools-for-agents)
**Prérequis :** [Leçon 8](0008-naming-and-describing-a-tool.md)

## Échauffement

1. ▢ Depuis la leçon 8 : pourquoi la description d'un outil doit-elle dire au modèle quand et comment l'utiliser plutôt que de simplement lister les paramètres qu'il accepte ?

<details markdown="1"><summary>Vérifier</summary>

Parce que le modèle n'a aucune autre source d'orientation pour choisir parmi les outils. Une simple liste de paramètres explique comment appeler un outil mais pas pourquoi ni quand le choisir, alors que c'est la vraie décision que le modèle doit prendre.

</details>

2. ▢ Depuis la leçon 8 : quel problème créez-vous si deux outils du même jeu d'outils ont des noms et des descriptions très semblables ?

<details markdown="1"><summary>Vérifier</summary>

Le modèle ne peut pas les distinguer de façon fiable, donc il peut appeler le mauvais ou appeler les deux par précaution. Ce bruit dégrade aussi la capacité du modèle à choisir correctement parmi tous les autres outils du jeu, pas seulement les deux qui se ressemblent.

</details>

## À savoir

### La valeur de retour d'un outil coûte du budget de contexte

Chaque message du transcript consomme des tokens. Quand un outil renvoie un résultat, ce résultat est ajouté au transcript, et le modèle le voit à chaque tour suivant jusqu'à la fin de l'exécution ou jusqu'à ce que le transcript soit tronqué. Un outil qui renvoie une petite réponse ciblée coûte peu. Un outil qui renvoie cinq mille lignes de base de données coûte de vrais tokens à chaque tour pour le reste de l'exécution, que le modèle ait eu besoin de toutes ou non.

```text
Bad:
Tool: fetch_user_records
Returns: [complete User record, complete User record, ...]
# 5000 rows, 50KB of JSON, ~10,000 tokens consumed per turn after this call
```

Une fois l'outil revenu, le transcript gonfle. Le modèle doit maintenant traiter les cinq mille lignes au tour suivant rien que pour lire son propre contexte. Cela alourdit le budget de tokens et ralentit la boucle.

### Concevoir les formes de retour pour la décision, pas pour l'exhaustivité

Au lieu de renvoyer tout ce que le système sous-jacent contient, concevez une forme de retour qui donne au modèle ce dont il a besoin pour décider de l'étape suivante.

```text
Better: Option 1 - Return a summary
Tool: fetch_user_records
Returns:
  total_count: 5000
  sample_results: [User, User, User, ...] # top 5 results
  query_was_too_broad: true
  suggestion: "Your query matches 5000 users. Narrow it with a company_id or email domain filter."

# ~500 tokens consumed per turn after this call
```

Le modèle voit maintenant que la requête était trop large et sait quoi faire ensuite : rappeler l'outil avec de meilleurs filtres. Cela renvoie un dixième des tokens de l'export complet.

```text
Better: Option 2 - Let the model ask for more
Tool: fetch_user_records
Returns:
  count: 50  # number of results returned
  total_matching: 5000  # number of results if the query was not limited
  results: [User, User, ...] # just the first 50
  next_page_token: "abc123xyz"

# Model sees it got 50 of 5000. It can decide to refine the query or ask for the next page.
```

Dans les deux cas, le modèle reçoit assez d'information pour décider en connaissance de cause sans être enseveli sous les données.

### Surcharge du jeu d'outils : plus d'outils, c'est de moins bons choix

Ajouter un outil à un agent n'est pas gratuit. Chaque outil parmi lesquels le modèle peut choisir rend le choix plus difficile pour le modèle. C'est ce qu'on appelle la surcharge du jeu d'outils.

Avec trois outils, le modèle choisit correctement la plupart du temps :

```text
Tools:
- search_documentation
- read_file
- list_directory
```

Avec dix outils, le modèle commence à douter de lui-même et appelle plusieurs outils quand un seul suffirait :

```text
Tools:
- search_documentation
- search_issues
- search_code
- read_file
- read_logs
- list_directory
- list_repos
- get_git_history
- get_git_diff
- get_git_status
```

Chaque nouvel outil ajoute du bruit à la décision. Le modèle doit lire et considérer les dix descriptions avant d'en choisir une. Si deux se ressemblent (search_code et search_documentation), le modèle risque d'appeler les deux. L'effet est discret : chaque outil existant en souffre légèrement, pas seulement le nouveau.

Le coût est réel : plus d'appels d'outils, plus de tokens dans le transcript, plus de tours gaspillés sur de l'information redondante.

### Ajouter un nouvel outil ou ajouter un paramètre

Quand vous êtes tenté d'ajouter un outil, demandez-vous d'abord : cela pourrait-il être un paramètre d'un outil existant ?

```text
Bad: Two tools
- name: list_files
- name: list_directories
```

Mieux : un seul outil avec un paramètre

```text
Good: One tool with a parameter
- name: list_contents
  parameters:
    - name: path
    - name: type
      type: enum
      values: [files, directories, all]
```

Le modèle choisit le type qu'il veut, et vous n'avez pas ajouté de bruit au jeu d'outils.

Mais parfois un nouvel outil se justifie. Si les outils sont fondamentalement différents (ils sont appelés dans des situations différentes, ils renvoient des formes différentes, ils exigent des permissions différentes), alors un nouvel outil au nom clair vaut mieux qu'un paramètre surchargé :

```text
Good: Two specialized tools
- name: search_database_by_id
  parameters:
    - id
    # Fast, returns a single record
- name: search_database_by_query
  parameters:
    - query
    # Might return many records
```

Le modèle connaît la différence : by_id est rapide et précis, by_query est flexible mais peut renvoyer beaucoup de choses. Les noms rendent la décision claire.

La règle : ajoutez un nouvel outil quand il serait appelé pour des raisons fondamentalement différentes, ou quand vous ne pouvez pas exprimer la distinction par des paramètres. Ajoutez un paramètre quand l'outil est essentiellement la même opération avec une variation de l'entrée ou du format de sortie.

### Observer la surcharge du jeu d'outils en pratique

Un signe subtil : le modèle se met à dire des choses comme « je devrais d'abord appeler search pour voir si cela existe, puis fetch si oui » alors qu'un seul outil aurait fait tout le travail. C'est le modèle qui cherche à être prudent parce qu'il n'est pas sûr de ce que fait chaque outil. Le problème n'est pas le modèle ; c'est le jeu d'outils.

Un autre signe : les appels d'outils répétés. Le modèle appelle plusieurs fois le même outil au cours d'une exécution, par exemple en cherchant deux fois ou en listant deux fois. Cela signifie souvent que le jeu d'outils ne donne pas au modèle le moyen de restreindre les résultats en un seul appel, donc il doit rappeler l'outil avec d'autres paramètres pour trouver ce dont il a besoin.

## Pratique

1. ▢ Un outil appelé `get_user_history` renvoie un tableau JSON de 100 000 événements d'action utilisateur du mois passé, chacun détaillé. Le modèle appellera probablement cet outil, regardera les dix premiers événements et ignorera le reste. Quel changement de conception réduit le coût en tokens à chaque tour après cet appel ?

<details markdown="1"><summary>Vérifier</summary>

Limiter le retour aux N premiers événements (par exemple les 20 premiers) et inclure un total_count ainsi qu'un moyen pour le modèle d'en demander davantage. Ainsi le modèle voit ce dont il a besoin sans payer pour les 100 000 événements. Autre possibilité : renvoyer un résumé (« 50 événements la semaine passée, 50 la semaine d'avant. Le plus récent : connexion de l'utilisateur ») plutôt que le détail complet, et laisser le modèle demander des précisions si besoin.

</details>

2. ▢ Vous avez un jeu de 15 outils. Le modèle appelle search_by_name et search_by_id dans la même exécution alors qu'il aurait pu exprimer les deux recherches comme des paramètres d'un seul outil. Quel est le tort d'avoir gardé deux outils séparés ?

<details markdown="1"><summary>Indice</summary>

Pensez au travail du modèle : il doit lire quinze descriptions et décider quel outil appeler. En quoi la présence d'outils semblables rend-elle ce travail plus difficile ?

</details>

<details markdown="1"><summary>Vérifier</summary>

La surcharge du jeu d'outils. Le modèle doit choisir parmi quinze outils. Des outils semblables comme search_by_name et search_by_id rendent le choix plus difficile. Le modèle risque d'appeler les deux alors qu'un seul suffirait, ou de perdre du temps à décider lequel convient. Chaque outil existant en souffre un peu parce que le jeu est devenu plus bruyant. La correction consiste à les fusionner en un seul outil de recherche avec un paramètre pour le champ de recherche.

</details>

3. ▢ Lequel des signes suivants indique que la forme de retour d'un outil est trop verbeuse ?

    - a) L'outil est appelé très fréquemment
    - b) Le modèle lit le résultat et demande un résumé avant de l'utiliser
    - c) L'outil met longtemps à s'exécuter
    - d) L'outil exige une authentification

<details markdown="1"><summary>Vérifier</summary>

**b)** Le modèle lit le résultat et demande un résumé avant de l'utiliser. Cela signifie que l'outil renvoie trop d'information ; le modèle doit filtrer ou résumer ce qu'il a reçu avant de pouvoir décider. (a) n'a pas de rapport avec la forme de retour ; un outil très appelé peut être étroit par conception. (c) concerne la vitesse d'exécution, pas les tokens. (d) concerne les permissions, pas la forme de retour.

</details>

4. ▢ Vous concevez des outils pour un agent de recherche de code. `search_code` et `get_code_diff` doivent-ils être un seul outil ou deux ? Expliquez en une ou deux phrases.

<details markdown="1"><summary>Vérifier</summary>

Deux outils distincts. Ils sont appelés pour des raisons différentes (la recherche cherche des fichiers qui correspondent à un motif, le diff montre les changements entre versions), ils renvoient des formes différentes (une liste de fichiers contre un diff structuré) et ils résolvent des problèmes différents. Un seul outil surchargé rendrait le choix du modèle plus difficile. S'ils étaient des variantes de la même opération (comme search_code avec différents paramètres de requête), ils pourraient être un seul outil avec un paramètre.

</details>

## Exercices en situation réelle

- [ ] Trouvez un jeu d'outils dans une application LLM ou un agent auquel vous avez accès. Comptez les outils. Lisez la trajectoire du modèle et marquez chaque tour où le modèle a appelé un outil. Estimez : le modèle a-t-il déjà appelé deux outils semblables alors qu'un seul aurait fait le travail ? Écrivez une phrase pour dire si le jeu d'outils vous a semblé surchargé ou bien conçu.

- [ ] Choisissez un outil qui renvoie des données structurées. Lisez un exemple de valeur de retour. Y a-t-il une partie du retour que le modèle ignorerait probablement ? Réécrivez la forme de retour pour exclure ces données ou les déplacer vers un second appel, en estimant combien de tokens vous avez économisés.

- [ ] Demain : concevez un outil qui pourrait aller dans les deux sens (un nouvel outil ou un paramètre d'un outil existant). Pour votre choix, écrivez deux phrases sur la raison pour laquelle vous avez retenu un outil séparé ou un paramètre, ce que l'alternative aurait coûté, et quand vous pourriez reconsidérer.

## Pour aller plus loin

- [Billet : "Writing Effective Tools for Agents", Anthropic Engineering](https://www.anthropic.com/engineering/writing-tools-for-agents)
- [Ressources](../RESOURCES.md)

---

Ça ne passe pas ? Relisez la source primaire en haut de page, car cette leçon la condense et c'est dans la condensation que la compréhension s'échappe. Consultez le [glossaire](../GLOSSARY.md) pour tout terme qui vous a paru glissant.

Si c'est la leçon elle-même qui n'est pas claire plutôt que la matière, c'est un défaut : [ouvrez une issue](https://github.com/TokenCemetery/teach/issues).
