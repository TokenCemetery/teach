---
title: "5. Appels parallèles et erreurs comme résultats"
description: "Comment un modèle peut demander plusieurs outils à la fois, et pourquoi les erreurs d'outils sont des résultats et non des exceptions"
type: lesson
---

# Leçon 5. Appels parallèles et erreurs comme résultats

**Lien avec la mission :** Écrire la boucle d'agent pour une tâche donnée, et nommer ce que fait chaque message de son contexte et ce qui met fin à la boucle.
**Source primaire :** [Doc : "Tool use with Claude", Claude Platform Docs](https://platform.claude.com/docs/en/agents-and-tools/tool-use/overview)
**Prérequis :** [Leçon 4](0004-schemas-and-who-executes.md)

## Échauffement

1. ▢ Au cours d'un même tour du modèle, celui-ci peut-il demander plus d'un appel d'outil en même temps ?

<details markdown="1"><summary>Vérifier</summary>

Oui. Le modèle peut émettre plusieurs blocs tool-use dans une même réponse, chacun avec un identifiant unique. Le harness les exécute tous (éventuellement en parallèle) et rassemble les résultats avant de les renvoyer dans le message suivant.

</details>

2. ▢ Quand un outil échoue, que fait le harness : lever une exception qui plante la boucle, ou renvoyer l'erreur au modèle ?

<details markdown="1"><summary>Vérifier</summary>

Renvoyer l'erreur au modèle comme résultat d'outil. La boucle continue ; le modèle a une chance de réessayer, d'utiliser un autre outil ou d'expliquer l'échec.

</details>

## À savoir

### Appels d'outils parallèles dans un même tour

La boucle d'agent consiste à envoyer, exécuter, ajouter, recommencer. Une seule réponse du modèle peut contenir plusieurs appels d'outils :

```json
{
  "role": "assistant",
  "content": [
    {"type": "text", "text": "I'll gather that data for you."},
    {
      "type": "tool_use",
      "id": "toolu_01XYZ",
      "name": "get_weather",
      "input": {"city": "Lisbon"}
    },
    {
      "type": "tool_use",
      "id": "toolu_02ABC",
      "name": "get_weather",
      "input": {"city": "Madrid"}
    }
  ],
  "stop_reason": "tool_use"
}
```

Chaque appel a son propre identifiant unique. Le modèle a décidé : « J'ai besoin de la météo de Lisbonne et de Madrid. » Votre harness peut alors :

1. Exécuter les deux outils en séquence (l'un après l'autre), ou
2. Les exécuter en parallèle (les deux en même temps), selon votre implémentation.

Le choix vous appartient. S'ils sont indépendants et rapides, le parallèle économise de la latence. S'ils se disputent des ressources ou si l'un dépend de l'autre, le séquentiel est plus simple.

### Rassembler les résultats avant le tour suivant

Une fois tous les appels d'outils terminés, le harness collecte les résultats et les renvoie dans un seul message. Chaque résultat est étiqueté avec l'identifiant de l'appel auquel il répond :

```json
{
  "role": "user",
  "content": [
    {
      "type": "tool_result",
      "tool_use_id": "toolu_01XYZ",
      "content": "18C, partly cloudy"
    },
    {
      "type": "tool_result",
      "tool_use_id": "toolu_02ABC",
      "content": "22C, sunny"
    }
  ]
}
```

Le modèle a maintenant les deux résultats, sait lequel est lequel (grâce à l'identifiant) et décide de la suite. C'est le point clé : tous les résultats reviennent ensemble dans un seul message, donc le modèle les traite comme une paire.

### Traiter les erreurs comme des résultats

Quand un outil échoue, le harness ne plante pas la boucle. Il capture l'erreur et la renvoie au modèle comme un résultat, exactement comme un résultat réussi. Un résultat d'outil en erreur ressemble à ceci :

```json
{
  "type": "tool_result",
  "tool_use_id": "toolu_01XYZ",
  "content": "Error: city not found",
  "is_error": true
}
```

Le champ `is_error` indique au modèle que ce résultat représente un échec, pas un succès. Le modèle le lit et doit décider : réessayer le même outil avec une autre ville, essayer un autre outil, ou abandonner et expliquer l'erreur à l'utilisateur.

### Pourquoi les erreurs sont des résultats et non des exceptions

Dans beaucoup de systèmes, un appel de fonction qui échoue lève une exception et arrête l'exécution. Dans une boucle d'agent, un appel d'outil qui échoue n'est qu'une information : des données renvoyées au modèle. Pourquoi cette conception ?

Parce que c'est le modèle qui commande. Le modèle a appelé l'outil ; c'est à lui de décider quoi faire si l'outil échoue. Peut-être veut-il réessayer. Peut-être veut-il utiliser un autre outil. Peut-être veut-il demander plus d'informations à l'utilisateur. Une exception lui retirerait ce choix.

Il ne s'agit pas d'excuser du mauvais code. C'est un choix de conception : traiter le modèle comme l'orchestrateur, pas comme une fonction de plus dans une pile d'appels. Le rôle du harness est d'exécuter ce que le modèle demande, de collecter le résultat (succès ou échec) et de le lui rendre pour qu'il l'interprète.

### Les erreurs viennent de bien des endroits

Un appel d'outil peut échouer pour de nombreuses raisons :

- Le code de l'outil client a levé une exception (base de données indisponible, entrée invalide, délai dépassé).
- Un outil serveur s'est exécuté mais a renvoyé une erreur (limite de débit de l'API, fichier introuvable, permission refusée).
- Le harness lui-même a rejeté l'appel (échec de la validation du schéma, champ obligatoire manquant).
- Le réseau a échoué (fournisseur injoignable, connexion coupée).

Tout cela devient des résultats d'outils qui portent des messages d'erreur, pas des plantages.

## Pratique

1. ▢ Un modèle fait deux appels d'outils dans un même tour : l'un réussit, l'autre échoue. Comment le harness renvoie-t-il les deux résultats au modèle ?

<details markdown="1"><summary>Vérifier</summary>

Dans un seul message de rôle user avec deux blocs tool_result, chacun étiqueté avec l'identifiant de l'appel correspondant. Un résultat porte `is_error: true` ou un message d'erreur ; l'autre porte les données du succès. Le modèle reçoit les deux en un seul tour et décide de la suite.

</details>

2. ▢ Vous avez un outil qui recherche dans une base de données. Le modèle l'appelle avec une recherche qui dépasse le délai. Que doit faire votre harness ?

<details markdown="1"><summary>Indice</summary>

Réfléchissez à qui revient la gestion du délai dépassé et à ce que le modèle a besoin de savoir.

</details>

<details markdown="1"><summary>Vérifier</summary>

Attraper le délai dépassé, capturer le message d'erreur (par exemple « Error: search timed out after 30s ») et le renvoyer au modèle comme résultat d'outil avec `is_error: true`. Le modèle décide alors : réessayer avec une requête plus simple, essayer un autre outil, ou abandonner. La boucle ne plante pas.

</details>

3. ▢ Le modèle fait trois appels d'outils parallèles. Le harness devrait :

    - a) Les exécuter l'un après l'autre pour pouvoir s'arrêter tôt si l'un échoue
    - b) Les exécuter en parallèle et attendre tous les résultats avant de les renvoyer
    - c) Renvoyer immédiatement les résultats réussis et n'envoyer les résultats en échec que plus tard
    - d) Annuler les appels restants dès que l'un échoue

<details markdown="1"><summary>Vérifier</summary>

**b)** Les exécuter en parallèle et attendre tous les résultats. Le modèle a demandé trois choses ; il doit recevoir trois résultats (succès ou échec). S'arrêter tôt (a) ou annuler (d) empêche le modèle de savoir ce qui s'est passé. Renvoyer les résultats à des moments différents (c) rompt le protocole : les résultats reviennent ensemble dans un seul message.

</details>

4. ▢ Vous écrivez un outil client qui multiplie deux nombres. Un modèle l'appelle avec `x=5, y="hello"`. Le harness tente de l'exécuter, la fonction lève une erreur de type. Quelle est l'étape suivante du harness ?

<details markdown="1"><summary>Vérifier</summary>

Attraper l'exception, formater l'erreur (par exemple « Error: cannot multiply number by string ») et la renvoyer au modèle comme résultat d'outil. Le modèle sait maintenant que l'appel a échoué et peut réessayer avec des entrées valides ou tenter une autre approche. La boucle continue.

</details>

## Exercices en situation réelle

- [ ] Écrivez ou trouvez un agent qui fait des appels d'outils parallèles. Suivez une exécution où le modèle demande deux outils à la fois. Vérifiez que les deux résultats reviennent ensemble dans un seul message et portent chacun leur propre identifiant.
- [ ] Faites échouer volontairement un outil (appelez une base de données indisponible, déclenchez une erreur de validation ou envoyez à un outil une entrée invalide). Observez comment le harness formate l'erreur et l'envoie au modèle. Regardez ce que fait ensuite le modèle.
- [ ] Demain : écrivez un harness qui exécute des appels d'outils en parallèle (avec des threads, de l'async ou le modèle de concurrence de votre langage) et collecte les résultats. Vérifiez qu'il renvoie tous les résultats dans un seul message même si certains outils échouent.

## Pour aller plus loin

- [Doc : "Tool use with Claude", Claude Platform Docs](https://platform.claude.com/docs/en/agents-and-tools/tool-use/overview)
- [Ressources](../RESOURCES.md)

---

Ça ne passe pas ? Relisez la source primaire en haut de page, car cette leçon la condense et c'est dans la condensation que la compréhension s'échappe. Consultez le [glossaire](../GLOSSARY.md) pour tout terme qui vous a paru glissant.

Si c'est la leçon elle-même qui n'est pas claire plutôt que la matière, c'est un défaut : [ouvrez une issue](https://github.com/TokenCemetery/teach/issues).
