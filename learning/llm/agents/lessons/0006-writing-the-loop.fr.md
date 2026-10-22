---
title: "6. Écrire la boucle"
description: "Construire la boucle d'agent à partir de pseudocode et choisir délibérément les conditions d'arrêt"
type: lesson
---

# Leçon 6. Écrire la boucle

**Lien avec la mission :** Écrire la boucle d'agent est la compétence centrale pour construire soi-même un agent, ce qui sert directement la mission « écrire la boucle d'agent pour une tâche donnée, et nommer ce que fait chaque message de son contexte et ce qui met fin à la boucle ».
**Source primaire :** [Billet : "Building Effective Agents", Anthropic Engineering](https://www.anthropic.com/engineering/building-effective-agents)
**Prérequis :** [Leçon 5](0005-parallel-calls-and-errors-as-results.md), [Boucle d'agent](../GLOSSARY.md)

## Échauffement

1. ▢ Depuis la leçon 5 : qu'est-ce qui est ajouté au transcript quand un appel d'outil échoue ?

<details markdown="1"><summary>Vérifier</summary>

Un résultat d'outil en erreur, étiqueté avec l'identifiant de l'appel en échec et marqué comme erreur, ajouté exactement comme le serait un résultat réussi. La boucle ne plante pas ; le modèle voit l'échec comme un tour normal.

</details>

2. ▢ Depuis la leçon 5 : pourquoi un modèle peut-il demander deux outils en parallèle plutôt que l'un après l'autre sans risque ?

<details markdown="1"><summary>Vérifier</summary>

Parce que chaque appel d'outil reçoit son propre identifiant unique, et que le harness renvoie chaque résultat étiqueté avec ce même identifiant. Le modèle peut toujours rattacher un résultat à l'appel qui l'a produit, quel que soit l'ordre d'exécution.

</details>

## À savoir

### La boucle d'agent sous forme de code

Dans son principe, une boucle d'agent est simple. La voici en pseudocode :

```text
function run_agent(model, tools, transcript, max_turns):
    for turn_count in range(max_turns):
        response = call_model(model, transcript)
        transcript.append(response)

        if response.has_no_tool_calls():
            return response.text

        for tool_call in response.tool_calls:
            result = execute_tool(tools, tool_call)
            transcript.append(result)

    return "Max turns reached"
```

C'est le harness. Le modèle choisit quel outil demander et quand arrêter de demander. Le harness applique les limites et la mécanique.

Remarquez la structure : **appeler le modèle, ajouter la réponse, vérifier si c'est terminé, sinon exécuter les outils et ajouter leurs résultats, puis revenir en haut de la boucle**. À chaque tour, le transcript grandit. Rien n'est conservé en mémoire en dehors du transcript.

### Pourquoi le transcript doit grandir à chaque tour

Les débutants construisent parfois une boucle qui ressemble à ceci :

```text
function run_agent_wrong(model, tools, transcript, max_turns):
    for turn_count in range(max_turns):
        response = call_model(model, transcript)

        if response.has_no_tool_calls():
            return response.text

        for tool_call in response.tool_calls:
            result = execute_tool(tools, tool_call)
            transcript.append(result)  # Only append results, not the model's request
```

C'est un bug. Si vous n'ajoutez pas au transcript la réponse d'appel d'outil du modèle avant d'exécuter l'outil, le modèle ne se « souviendra » pas, au tour suivant, d'avoir demandé l'outil. Quand le harness rappelle le modèle, le transcript ne dit pas « le modèle a demandé une recherche » ni « le modèle a demandé la calculatrice ». Le modèle risque de redemander le même outil, perplexe. La littérature appelle cela oublier la requête. Le transcript devient incohérent.

La correction consiste à ajouter la réponse **immédiatement** après l'appel du modèle, avant de faire quoi que ce soit d'autre :

```text
function run_agent_correct(model, tools, transcript, max_turns):
    for turn_count in range(max_turns):
        response = call_model(model, transcript)
        transcript.append(response)  # Append right away

        if response.has_no_tool_calls():
            return response.text

        for tool_call in response.tool_calls:
            result = execute_tool(tools, tool_call)
            transcript.append(result)
```

Maintenant, quand la boucle se répète et rappelle le modèle, le transcript contient « le modèle a dit qu'il appellerait la recherche », et le modèle peut raisonner sur le résultat.

### Conditions d'arrêt : choisir délibérément

Une boucle d'agent doit s'arrêter. Plusieurs endroits sont possibles :

**Nombre maximal de tours** : la boucle externe compte les tours et sort si le compte dépasse une limite. C'est un garde-fou. Sans lui, un modèle ou un outil défaillant pourrait boucler indéfiniment.

**Aucun appel d'outil** : la réponse du modèle ne contient aucun appel d'outil. C'est l'arrêt du « chemin heureux » : le modèle a décidé de répondre. Vérifiez cela après avoir ajouté la réponse du modèle.

**Outil d'arrêt explicite** : vous pouvez proposer un outil nommé `stop` ou `finish` que le modèle peut appeler pour sortir explicitement. Le harness le vérifie et retourne. C'est utile si la tâche est ouverte et que le modèle a besoin d'une action explicite « j'ai terminé ». Si vous proposez cet outil, documentez-le clairement pour que le modèle comprenne quand l'utiliser.

**Garde sur le nombre d'erreurs** : si un appel d'outil échoue, le harness ajoute l'erreur comme résultat. Si trop d'appels d'outils échouent à la suite, le harness s'arrête et renvoie une trajectoire d'erreur au lieu de continuer indéfiniment. Cela évite les boucles de nouveaux essais.

Elles ne s'excluent pas mutuellement. Un harness de production peut toutes les vérifier :

```text
function run_agent_with_guards(model, tools, transcript, max_turns, max_errors):
    error_count = 0

    for turn_count in range(max_turns):
        response = call_model(model, transcript)
        transcript.append(response)

        if response.has_no_tool_calls():
            return response.text

        if response.has_explicit_stop_tool_call():
            return response.text

        for tool_call in response.tool_calls:
            result = execute_tool(tools, tool_call)

            if result.is_error():
                error_count += 1
                if error_count > max_errors:
                    return "Too many errors"
            else:
                error_count = 0

            transcript.append(result)

    return "Max turns reached"
```

L'essentiel est que ces décisions soient visibles dans votre code, ni cachées ni accidentelles. Vous choisissez quand arrêter, et combien de chances l'agent a de se rétablir.

## Pratique

1. ▢ Dans la boucle en pseudocode montrée plus haut, pourquoi `transcript.append(response)` doit-il avoir lieu avant la vérification `if response.has_no_tool_calls()` ?

<details markdown="1"><summary>Vérifier</summary>

Le transcript doit contenir la réponse du modèle pour que les tours suivants (ou un observateur qui lit la trajectoire) puissent voir ce que le modèle a dit et décidé. Si vous vérifiez l'arrêt avant d'ajouter, vous renvoyez le texte du modèle, mais le transcript ne montre jamais que le modèle a répondu. De plus, d'autres informations de la réponse (comme les outils que le modèle a envisagés mais décidé de ne pas appeler) seraient perdues.

</details>

2. ▢ Un modèle appelle un outil et le harness l'exécute avec succès, ce qui renvoie un résultat. Le résultat est ajouté au transcript. À l'itération suivante de la boucle, le harness rappelle le modèle. Que voit le modèle dans le transcript qu'il ne voyait pas au tour précédent ?

<details markdown="1"><summary>Indice</summary>

Pensez à ce qui a été ajouté à l'itération précédente de la boucle, juste après le premier appel du modèle.

</details>

<details markdown="1"><summary>Vérifier</summary>

Le modèle voit sa propre réponse d'appel d'outil, ajoutée avant que la boucle n'exécute l'outil. Au deuxième tour, le transcript contient à la fois cette réponse et le résultat de l'outil. Sans l'ajout préalable de la réponse, le modèle ne verrait que le résultat, comme si l'outil avait été appelé par autre chose que le modèle.

</details>

3. ▢ Vous construisez un harness avec une garde sur le nombre maximal d'erreurs : si trois appels d'outils échouent à la suite, arrêter la boucle. Quand faut-il remettre le compteur d'erreurs à zéro ?

    - a) Quand le nombre maximal de tours est atteint
    - b) Quand un appel d'outil réussit et renvoie un résultat sans erreur
    - c) Quand la boucle démarre
    - d) Quand la réponse du modèle ne contient aucun appel d'outil

<details markdown="1"><summary>Vérifier</summary>

**b)** Quand un appel d'outil réussit. La garde sert à repérer un schéma d'échecs répétés. Si un outil échoue puis que le suivant réussit, la boucle de nouveaux essais est rompue et vous voulez autoriser davantage d'échecs. Si vous ne remettez à zéro qu'au démarrage (c), vous ne pourriez jamais vous arrêter ; si vous remettez à zéro au nombre maximal de tours ou à l'absence d'appels d'outils (a, d), la garde ne fonctionne pas. Remettre à zéro en cas de succès est le bon schéma : un succès remet le compteur à zéro.

</details>

4. ▢ Votre modèle est censé chercher, lire un document, puis le résumer. Au troisième tour, il redemande le même outil de recherche. La recherche avait réussi la première fois. Quel est le bug le plus probable de votre harness, d'après ce que vous savez du fonctionnement des transcripts ?

<details markdown="1"><summary>Vérifier</summary>

Le harness n'ajoute pas au transcript la réponse d'appel d'outil du modèle après l'appel du modèle. Le modèle ne voit jamais sa propre demande de l'outil de recherche du premier tour. Quand il est appelé au troisième tour, le transcript montre le résultat de la recherche mais pas la requête, donc le modèle ne sait pas pourquoi le résultat est là et redemande une recherche. La correction consiste à ajouter la réponse immédiatement après l'appel du modèle, avant d'exécuter l'outil.

</details>

## Exercices en situation réelle

- [ ] Écrivez de mémoire le pseudocode de la boucle d'agent de base sans regarder la leçon. Comparez-le avec le pseudocode montré sous « La boucle d'agent sous forme de code ». Vérifiez : ajoutez-vous la réponse avant de tester l'absence d'appels d'outils ?

- [ ] Trouvez une implémentation d'agent dans un projet open source quelconque (une bibliothèque que vous utilisez ou un dépôt public). Lisez le code de la boucle. Identifiez où le transcript est construit et où la condition d'arrêt est vérifiée. Notez si les conditions d'arrêt sont explicites (visibles dans un if) ou cachées (dans une condition enfouie dans l'appel d'une autre fonction).

- [ ] Demain : esquissez en pseudocode les quatre conditions d'arrêt (nombre maximal de tours, aucun appel d'outil, arrêt explicite, garde sur le nombre d'erreurs). Pour chacune, écrivez une phrase sur son importance : quel problème résout-elle ?

## Pour aller plus loin

- [Billet : "Building Effective Agents", Anthropic Engineering](https://www.anthropic.com/engineering/building-effective-agents)
- [Ressources](../RESOURCES.md)

---

Ça ne passe pas ? Relisez la source primaire en haut de page, car cette leçon la condense et c'est dans la condensation que la compréhension s'échappe. Consultez le [glossaire](../GLOSSARY.md) pour tout terme qui vous a paru glissant.

Si c'est la leçon elle-même qui n'est pas claire plutôt que la matière, c'est un défaut : [ouvrez une issue](https://github.com/TokenCemetery/teach/issues).
