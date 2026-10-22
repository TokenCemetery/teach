---
title: "3. Le format de transmission d'un appel d'outil"
description: "À quoi ressemblent réellement un appel d'outil et son résultat dans le protocole entre votre harness et le fournisseur du modèle"
type: lesson
---

# Leçon 3. Le format de transmission d'un appel d'outil

**Lien avec la mission :** Écrire la boucle d'agent pour une tâche donnée, et nommer ce que fait chaque message de son contexte et ce qui met fin à la boucle.
**Source primaire :** [Doc : "Tool use with Claude", Claude Platform Docs](https://platform.claude.com/docs/en/agents-and-tools/tool-use/overview)
**Prérequis :** [Leçon 2](0002-agent-workflow-or-prompt.md), [Outil](../GLOSSARY.md)

## Échauffement

1. ▢ Quelle est la différence entre un harness qui appelle un modèle et un harness qui exécute un outil ?

<details markdown="1"><summary>Vérifier</summary>

Le harness appelle le modèle en lui envoyant une requête (le transcript plus les outils) par le réseau à l'API d'un fournisseur ; le modèle tourne dans l'infrastructure du fournisseur et renvoie une sortie structurée. Un outil est appelé quand le modèle le demande en émettant un bloc structuré d'appel d'outil ; le harness l'exécute, en général en invoquant une fonction dans la même base de code ou sur le même réseau.

</details>

2. ▢ Dans quel cas le modèle peut-il envoyer du texte simple plutôt qu'un appel d'outil ?

<details markdown="1"><summary>Vérifier</summary>

Quand le modèle a terminé la tâche sur laquelle il travaillait et est prêt à renvoyer une réponse finale à l'utilisateur, ou quand il décide (dans les limites que vous avez fixées) qu'il n'a pas besoin d'appeler d'outil pour ce tour.

</details>

## À savoir

### L'appel d'outil sur le réseau

Quand vous envoyez à un fournisseur de modèle une requête qui lui demande d'utiliser des outils, la requête comprend trois éléments : le nom du modèle, la liste des outils disponibles (avec leurs noms, descriptions et schémas de paramètres) et le transcript de la conversation jusque-là.

Une définition d'outil ressemble à ceci : un nom, une description lisible par un humain et un JSON Schema qui contraint les paramètres que le modèle peut envoyer. Voici une requête Anthropic avec un seul outil :

```json
{
  "model": "claude-sonnet-5",
  "max_tokens": 1024,
  "tools": [
    {
      "name": "get_weather",
      "description": "Get the current weather for a given city",
      "input_schema": {
        "type": "object",
        "properties": {
          "city": {"type": "string", "description": "The city name"}
        },
        "required": ["city"]
      }
    }
  ],
  "messages": [
    {"role": "user", "content": "What's the weather in Lisbon?"}
  ]
}
```

Quand le modèle décide d'appeler un outil, il ne l'exécute pas. Il renvoie à la place un bloc structuré qui décrit quel outil appeler et quels arguments lui passer. Le fournisseur cesse d'envoyer de la sortie et le signale par un champ `stop_reason`. Voici la réponse Anthropic complète :

```json
{
  "id": "msg_01ABC",
  "type": "message",
  "role": "assistant",
  "content": [
    {"type": "text", "text": "I'll check that for you."},
    {
      "type": "tool_use",
      "id": "toolu_01XYZ",
      "name": "get_weather",
      "input": {"city": "Lisbon"}
    }
  ],
  "stop_reason": "tool_use"
}
```

Remarquez : le champ `input` est déjà du JSON analysé, pas une chaîne. Chaque appel d'outil reçoit un identifiant unique (ici `toolu_01XYZ`) pour que le harness puisse dire au modèle quel résultat répond à quel appel. L'assistant peut aussi inclure du texte simple avant ou après le bloc d'appel d'outil.

### Du réseau à l'exécution

Votre harness voit cette réponse et sait qu'il doit exécuter `get_weather` avec l'argument `{"city": "Lisbon"}`. La façon de le faire dépend de votre outil :

- S'il s'agit d'un **outil client** (une fonction de votre propre code), vous l'appelez directement : `weather_result = get_weather(city="Lisbon")`.
- S'il s'agit d'un **outil serveur** (quelque chose que le fournisseur exécute pour vous, comme une recherche web hébergée), le fournisseur l'a déjà exécuté avant de répondre. Vous extrayez le résultat de la réponse.

### Renvoyer le résultat

Une fois que le harness a un résultat (obtenu en exécutant la fonction ou en lisant la réponse du fournisseur), il le renvoie au modèle dans un nouveau message, étiqueté avec l'identifiant de l'appel d'outil. Le format Anthropic l'imbrique dans un message de rôle `user` :

```json
{
  "role": "user",
  "content": [
    {
      "type": "tool_result",
      "tool_use_id": "toolu_01XYZ",
      "content": "18C, partly cloudy"
    }
  ]
}
```

Ce message entre dans le transcript comme un nouveau tour. Le modèle a maintenant à la fois l'appel d'outil qu'il a fait et le résultat, et il décide de la suite : appeler un autre outil, appeler le même outil avec d'autres arguments, ou renvoyer une réponse finale.

### Le format de transmission d'OpenAI (la différence)

L'API d'OpenAI utilise les mêmes concepts mais avec des noms de champs et des formes différents. Plutôt que de reprendre tout l'échange, voici ce qui diffère :

Les paramètres de l'outil s'imbriquent sous `function.parameters` au lieu d'un `input_schema` nu. Les arguments d'appel d'outil du modèle arrivent sous forme de chaîne encodée en JSON dans `function.arguments`, pas d'objet déjà analysé, donc votre harness doit l'analyser. Le signal d'arrêt est `finish_reason: "tool_calls"` au lieu de `stop_reason: "tool_use"`. Le résultat revient dans un message dédié `role: "tool"` qui porte le `tool_call_id`, et non enveloppé dans un message `user`. Voici un exemple abrégé pour la même tâche météo :

```json
{
  "choices": [{
    "message": {
      "role": "assistant",
      "content": null,
      "tool_calls": [{
        "id": "call_abc123",
        "type": "function",
        "function": {"name": "get_weather", "arguments": "{\"city\": \"Lisbon\"}"}
      }]
    },
    "finish_reason": "tool_calls"
  }]
}
```

Suivi du résultat sous forme de message `role: "tool"` :

```json
{"role": "tool", "tool_call_id": "call_abc123", "content": "18C, partly cloudy"}
```

Le schéma est identique : définition d'outil, appel d'outil avec identifiant, résultat étiqueté avec le même identifiant. Les noms et les formes diffèrent, mais tout harness qui gère l'un peut être adapté à l'autre en faisant correspondre ces champs.

## Pratique

1. ▢ Dans la réponse Anthropic montrée plus haut, pourquoi le champ `input` contient-il un objet JSON analysé plutôt qu'une chaîne JSON ?

<details markdown="1"><summary>Vérifier</summary>

L'API Anthropic analyse les arguments de l'appel d'outil côté fournisseur avant de les renvoyer, ce qui réduit le travail du harness. Votre code reçoit des valeurs prêtes à l'emploi, pas une chaîne à analyser. OpenAI envoie au contraire les arguments sous forme de chaîne, donc vous devez appeler `json.parse()` ou l'équivalent dans votre harness avant de les utiliser.

</details>

2. ▢ Quand vous renvoyez le résultat de l'outil au modèle, pourquoi inclut-il le champ `tool_use_id` ?

<details markdown="1"><summary>Vérifier</summary>

Le modèle a pu demander plusieurs outils en un seul tour. L'identifiant permet au modèle de faire correspondre chaque résultat à l'appel qu'il avait fait, pour savoir quelle réponse vient de quelle requête.

</details>

3. ▢ Dans le protocole d'Anthropic, un résultat d'outil voyage dans un message de rôle `user`. Dans celui d'OpenAI, il voyage dans un message `role: "tool"`. Pourquoi cette différence n'a-t-elle pas d'importance pour la logique de la boucle d'agent ?

    - a) Parce que le harness n'a pas besoin de les distinguer pour construire le transcript
    - b) Parce que le modèle les traite toujours de la même façon quel que soit le rôle
    - c) Parce que l'un des protocoles est manifestement faux et à éviter
    - d) Parce que les résultats d'outils ne font pas partie du transcript officiel

<details markdown="1"><summary>Vérifier</summary>

**b)** Le modèle les traite de la même façon quelle que soit l'étiquette de rôle ou la structure du message. La logique est : voici un résultat d'un appel d'outil que vous avez fait ; que voulez-vous faire maintenant ? Le détail du protocole (dans un message user ou sous forme de message tool) ne change pas cette logique. (a) s'en approche mais manque l'essentiel : le rôle n'a pas d'importance pour la boucle elle-même.

</details>

4. ▢ Un harness reçoit cette réponse OpenAI : `"arguments": "{\"city\": \"Paris\"}"`. Comment le harness doit-il la traiter avant de la passer à l'outil ?

<details markdown="1"><summary>Vérifier</summary>

L'analyser comme du JSON : `json.loads("{\"city\": \"Paris\"}") yields {"city": "Paris"}`. OpenAI renvoie une chaîne, et le harness doit la désérialiser en dictionnaire (ou en objet) avant de déballer les arguments pour l'appel de fonction.

</details>

## Exercices en situation réelle

- [ ] Ouvrez le code ou la documentation d'un vrai framework d'agents (LangChain, Vercel AI, ou le SDK Python de Claude lui-même) et trouvez où il envoie une définition d'outil au modèle. Identifiez le nom, la description et le schéma de paramètres. Marquez d'où vient chacun dans le code.
- [ ] Suivez un cycle complet d'appel d'outil dans cette même base de code : trouvez où il analyse la réponse tool-use du modèle, exécute l'outil et renvoie le résultat. Marquez comment l'identifiant sert à les faire correspondre.
- [ ] Demain : écrivez un harness minimal (20 lignes ou moins, le pseudocode convient) qui envoie un seul outil à un fournisseur de modèle, analyse la réponse d'appel d'outil et renvoie le résultat. N'utilisez pas de framework.

## Pour aller plus loin

- [Doc : "Tool use with Claude", Claude Platform Docs](https://platform.claude.com/docs/en/agents-and-tools/tool-use/overview)
- [Guide : "Function calling", OpenAI](https://developers.openai.com/api/docs/guides/function-calling)
- [Ressources](../RESOURCES.md)

---

Ça ne passe pas ? Relisez la source primaire en haut de page, car cette leçon la condense et c'est dans la condensation que la compréhension s'échappe. Consultez le [glossaire](../GLOSSARY.md) pour tout terme qui vous a paru glissant.

Si c'est la leçon elle-même qui n'est pas claire plutôt que la matière, c'est un défaut : [ouvrez une issue](https://github.com/TokenCemetery/teach/issues).
