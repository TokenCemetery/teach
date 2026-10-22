---
title: "13. Scratchpad contre mémoire"
description: "La différence entre les notes qu'un agent garde pendant une exécution et les faits dont il a besoin sur plusieurs exécutions"
type: lesson
---

# Leçon 13. Scratchpad contre mémoire

**Lien avec la mission :** Diagnostiquer un agent défaillant à partir de sa trajectoire au lieu d'ajouter une instruction de plus à son prompt, en comprenant quelle information persiste d'une exécution à l'autre et laquelle disparaît à la fin d'une exécution.
**Source primaire :** [Billet : "Effective Context Engineering for AI Agents", Anthropic Engineering](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents)
**Prérequis :** [Leçon 12](0012-sub-agents-as-context-isolation.md), [Trajectoire](../GLOSSARY.md)

## Échauffement

1. ▢ Qu'enregistre une trajectoire ?

<details markdown="1"><summary>Vérifier</summary>

L'enregistrement complet et ordonné d'une exécution d'agent : chaque message envoyé au modèle, chaque appel d'outil fait par le modèle et chaque résultat que le harness a ajouté en retour.

</details>

2. ▢ Quand vous lancez un sous-agent pour traiter un travail borné, le sous-agent voit-il le transcript complet du parent ?

<details markdown="1"><summary>Vérifier</summary>

Non. Le sous-agent reçoit son propre transcript neuf avec un historique vide. Il peut recevoir un résumé ou un contexte précis que l'agent parent lui transmet comme prompt initial, mais il n'hérite pas de la trajectoire complète du parent.

</details>

## À savoir

Un **scratchpad** (bloc-notes) n'est en réalité qu'une partie du transcript, ou une note que l'agent écrit puis relit au sein d'une seule exécution. Pendant une longue tâche, l'agent peut utiliser un scratchpad pour suivre un total courant, un plan en plusieurs étapes ou des constats intermédiaires, afin que le modèle n'ait pas à les redériver à chaque tour. Le scratchpad est éphémère : quand le harness arrête la boucle et que l'exécution se termine, le scratchpad vit dans la trajectoire mais nulle part ailleurs. Si vous lancez une nouvelle exécution d'agent une heure plus tard pour poursuivre le travail, le scratchpad a disparu.

C'est là que s'installe une confusion courante. Un agent a tenu un scratchpad pendant une exécution et « s'est souvenu » de quelque chose. Ce même agent, relancé à neuf, ne s'en souviendra pas. Le modèle peut utiliser le même nom pour l'outil ou le fichier du scratchpad, mais le contenu a disparu parce que l'exécution a disparu.

La **mémoire entre exécutions** est fondamentalement différente. Une nouvelle exécution démarre avec un transcript vide, donc tout ce que le modèle doit savoir d'une exécution précédente doit vivre quelque part en dehors de toute trajectoire isolée et être rechargé délibérément au démarrage de l'exécution suivante. Le harness lit un stockage durable, un fichier, une base de données ou un système de récupération, avant que la boucle ne commence, et place les faits pertinents dans le prompt ou le contexte initial pour que le modèle puisse agir dessus.

Voici un exemple concret : un agent fait la revue de code d'une grande pull request. Pendant l'exécution d'une heure, il tient un scratchpad qui liste chaque fichier déjà vérifié, de sorte que lorsque le modèle considère un nouveau fichier, il peut jeter un œil au scratchpad et éviter de réanalyser un travail déjà fait. Le scratchpad fait partie du transcript. Quand l'exécution se termine, la revue est faite, et le scratchpad est archivé avec la trajectoire.

Imaginez maintenant un autre scénario : un assistant de code aide un même utilisateur à écrire du code sur de nombreuses sessions distinctes pendant des semaines. L'utilisateur a une forte préférence pour un certain style de code, une convention de nommage et une bibliothèque. Si l'assistant est relancé à chaque session, il commence sans aucune connaissance de ces préférences. L'assistant a besoin d'une mémoire entre exécutions : un fichier ou une note que le harness lit au début de chaque session et qui dit « L'utilisateur préfère X, utilise Y, évite Z. » Ce fait n'est dans aucune trajectoire isolée ; il est stocké durablement et chargé au démarrage de l'exécution.

L'idée clé de [Effective Context Engineering for AI Agents](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents) est qu'il s'agit de deux mécanismes distincts. Un scratchpad est un outil ou un artefact que l'agent manipule pendant une exécution. La mémoire entre exécutions est une couche de données en dehors de la boucle d'agent, gérée par le harness.

## Pratique

1. ▢ Un agent résout un problème de mathématiques en plusieurs étapes. Pendant l'exécution, il écrit ses notes de travail dans un fichier scratchpad. À la fin, il ajoute la réponse finale à un fichier de résultats. Des jours plus tard, vous relancez le même agent avec un autre problème. Qu'est-ce qui sera encore là ?

    - a) Les notes du scratchpad.
    - b) Le fichier de résultats.
    - c) Les deux, parce que ce sont tous deux des fichiers.
    - d) Aucun des deux, parce que les fichiers sont effacés à chaque exécution.

<details markdown="1"><summary>Vérifier</summary>

**b)** Le fichier de résultats sera encore là parce que c'est un stockage durable en dehors de l'exécution. Les notes du scratchpad, même écrites dans un fichier, ne concernent que l'ancienne exécution et ne sont pas chargées automatiquement dans le nouveau transcript. Si l'agent a besoin de ces anciennes notes dans la nouvelle exécution, le harness doit délibérément les lire et les inclure dans le prompt initial.

</details>

2. ▢ Vous concevez un agent qui doit se souvenir des noms des fichiers qu'il a déjà traités. Utiliseriez-vous un scratchpad ou une mémoire entre exécutions ?

<details markdown="1"><summary>Indice</summary>

Demandez-vous si l'information sert au sein d'une seule exécution ou sur plusieurs exécutions distinctes.

</details>

<details markdown="1"><summary>Vérifier</summary>

Si tous les fichiers sont traités dans une seule longue exécution, un scratchpad suffit. L'agent consulte le scratchpad à chaque fois et évite de retraiter. Si le travail est réparti sur plusieurs exécutions d'agent, peut-être relancées chaque jour ou une exécution par demande d'utilisateur, alors il faut une mémoire entre exécutions pour qu'une nouvelle exécution puisse voir ce qui a été fait avant.

</details>

3. ▢ Quelle est la raison fondamentale pour laquelle un agent relancé avec un harness neuf ne peut pas voir les notes qu'il avait écrites dans un scratchpad lors de l'exécution précédente ?

<details markdown="1"><summary>Vérifier</summary>

Parce que le scratchpad fait partie du transcript, et qu'une nouvelle exécution démarre avec un transcript vide. L'ancienne trajectoire est archivée mais pas chargée dans la nouvelle exécution. Pour rendre le contenu du scratchpad visible dans une nouvelle exécution, le harness devrait le lire depuis le stockage et l'insérer dans le prompt initial, ce qui le fait passer de scratchpad à mémoire délibérée entre exécutions.

</details>

4. ▢ Vous construisez un agent qui aide un utilisateur à gérer une liste de tâches personnelle. L'agent ajoute des tâches, les termine et filtre par étiquette. La liste de tâches doit-elle être un scratchpad, local à une exécution, ou une mémoire entre exécutions, persistée d'une exécution à l'autre ? Pourquoi ?

<details markdown="1"><summary>Vérifier</summary>

Une mémoire entre exécutions. Une liste de tâches doit persister au-delà d'une session. Si l'utilisateur lance l'agent demain et demande « montre-moi mes tâches », l'agent doit encore voir la liste d'aujourd'hui. Un scratchpad disparaîtrait à la fin de l'exécution, et les données de l'utilisateur seraient perdues.

</details>

## Exercices en situation réelle

- [ ] Passez deux minutes à parcourir le code de votre propre agent. Trouvez où le harness crée un transcript neuf, vide ou avec seulement un prompt initial. Notez ce que vous voyez.
- [ ] Cherchez toute « mémoire » ou tout « état » que votre agent sauvegarde actuellement. Est-il chargé par le harness avant le début de la boucle, ou seulement référencé pendant l'exécution ? S'il ne l'est que pendant l'exécution, c'est un scratchpad. S'il est chargé au démarrage, c'est de la mémoire entre exécutions.
- [ ] Demain : trouvez ou écrivez un usage de scratchpad, où un agent écrit une note, la relit, puis l'exécution se termine. Séparément, trouvez ou imaginez un usage entre exécutions, où un agent a besoin d'un fait de l'exécution de la semaine dernière pour répondre à la question d'aujourd'hui.

## Pour aller plus loin

- [Billet : "Effective Context Engineering for AI Agents", Anthropic Engineering](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents)
- [Ressources](../RESOURCES.md)

---

Ça ne passe pas ? Relisez la source primaire en haut de page, car cette leçon la condense et c'est dans la condensation que la compréhension s'échappe. Consultez le [glossaire](../GLOSSARY.md) pour tout terme qui vous a paru glissant.

Si c'est la leçon elle-même qui n'est pas claire plutôt que la matière, c'est un défaut : [ouvrez une issue](https://github.com/TokenCemetery/teach/issues).
