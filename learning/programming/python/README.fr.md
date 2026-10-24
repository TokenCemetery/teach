---
title: Python
description: "Maîtriser Python en production : le livrer typé, testé, empaqueté et profilé"
type: topic
---

# Apprentissage : Python

Devenir l'ingénieur à qui l'on confie Python au sein d'une équipe : capable de livrer un service ou un outil Python typé, testé et empaqueté, de remonter une traceback ou un profil jusqu'à sa cause racine au lieu de deviner, et de dire concrètement pourquoi l'usage astucieux que fait quelqu'un du dynamisme de Python va lui faire mal.

**Commencez ici :** [0001. Les noms sont des liaisons, pas des boîtes](lessons/0001-names-are-bindings.md)
**Dernière leçon :** [0044. Jugement](lessons/0044-judgment.md)

## Objectif

- Prédire ce que font un argument par défaut mutable, une closure sur une variable de boucle et une liste partagée, avant d'exécuter le code.
- Livrer un paquet qui s'installe et s'exécute sur une machine qui n'est pas celle sur laquelle il a été écrit.
- Ajouter des annotations de type qu'un vérificateur contrôle, et corriger ce qu'il signale plutôt que de le faire taire.
- Écrire des tests `pytest` qui échouent de façon informative, à l'aide de fixtures et de paramétrisation plutôt que de corps de test copiés.
- Trouver la partie lente avec un profileur et prouver la correction par une mesure.
- Choisir entre threads, processus et `asyncio` à partir de la forme de la charge de travail, et dire ce que le GIL empêche et n'empêche pas.
- Implémenter une méthode dunder ou un context manager quand le data model l'exige, et reconnaître quand une simple fonction est la meilleure réponse.
- Relire le Python de quelqu'un et nommer précisément pourquoi une classe, une métaclasse ou une chaîne d'héritage n'est pas le bon outil à cet endroit.

## Contraintes

- Ne suppose aucune connaissance préalable de Python. Une expérience dans un autre langage raccourcit les premières étapes sans être requise, et elle apporte des habitudes que Python punit en silence : une classe là où une fonction suffirait, une boucle là où une compréhension se lit mieux, une copie défensive que le langage a déjà faite.
- Ne nécessite que CPython et un terminal sur n'importe quel système d'exploitation pris en charge. Rien dans le fil conducteur n'exige d'outillage payant, de compte cloud ni de seconde machine.
- CPython est l'implémentation de référence tout au long du parcours. Les autres implémentations n'apparaissent que là où le comportement diffère réellement.
- Les exercices sont de petits programmes qui tiennent en une séance. Les espacer sur plusieurs jours est le mécanisme, pas un inconvénient.
- Le typage et le packaging évoluent plus vite que le langage. Les affirmations sensibles aux versions sont vérifiées dans la documentation actuelle et dans la PEP concernée, et toute leçon qui dépend d'une version indique laquelle.

## Hors périmètre

- Les frameworks web en tant que sujets à part entière : Django, FastAPI, Flask.
- La pile scientifique et de machine learning en tant que sujet : NumPy, pandas, PyTorch. Voir [`llm/finetuning`](../../llm/finetuning/) pour cette frontière.
- La distribution au-delà des wheels publiées sur un index : conda, paquets du système d'exploitation, binaires figés en un seul fichier.
- Le fonctionnement interne de CPython au-delà du point où il cesse de prédire le comportement des programmes : bytecode, API C, écriture de modules d'extension.
- Python 2, et la migration depuis Python 2.
- Les images de conteneur : placer une wheel et son interpréteur dans une image, puis exécuter, sécuriser et déboguer ce conteneur, relève de [`infrastructure/containers`](../../infrastructure/containers/).

## Le fil conducteur

Sept étapes, de zéro jusqu'au niveau senior. Pas une liste de leçons : une étape comprend plusieurs leçons, et les frontières sont souples.

| Étape | Leçons | Contenu | Terminée quand |
|---|---|---|---|
| 1. Fondations | 0001 à 0007 | Objets et noms, mutabilité et aliasing, listes, dicts, sets, tuples, valeur de vérité, compréhensions, fonctions et passage d'arguments | Vous savez prédire l'aliasing et la mutation sans exécuter le code |
| 2. Idiomes | 0008 à 0014 | Itérateurs et générateurs, context managers, les exceptions comme flux de contrôle, `dataclasses`, modules et paquets, la bibliothèque standard qui vaut d'être connue | Vous recourez à un générateur ou à un context manager plutôt que d'écrire à la main la boucle et le `try/finally` |
| 3. Types et outillage | 0015 à 0021 | Annotations, génériques, `Protocol`, sévérité du vérificateur, linting et formatage, environnements virtuels, gestion des dépendances et du projet, construction d'une wheel | Un vérificateur strict passe, et quelqu'un d'autre peut installer le résultat |
| 4. Le data model | 0022 à 0027 | Méthodes dunder, `__init__` face à `__new__`, propriétés, descripteurs, attributs de classe face aux attributs d'instance, ordre de résolution des méthodes, pourquoi les métaclasses ne sont presque jamais la réponse | Vous implémentez le protocole dont un type a besoin, et savez dire quand ne pas le faire |
| 5. Tests | 0028 à 0033 | Mécanique de `pytest`, fixtures et leur portée, paramétrisation, property-based testing, ce qui mérite un mock et ce qui ne le mérite pas, la couverture comme signal plutôt que comme objectif | Vous avez une suite de tests qui a attrapé une régression avant un humain |
| 6. Concurrence et performance | 0034 à 0039 | Threads, processus, `asyncio`, ce que le GIL sérialise réellement, les appels bloquants dans une boucle d'événements, le profilage, le coût de la recherche d'attributs et des allocations | Vous choisissez le modèle de concurrence à partir de la charge de travail et prouvez le gain à partir d'un profil |
| 7. Jugement | 0040 à 0044 | Conception d'API et de paquets, dépréciation, relecture, lecture de la bibliothèque standard et des PEP pour trouver des réponses | On vous fait confiance pour trancher et l'expliquer à quelqu'un d'autre |

## Leçons

Suivez-les dans l'ordre.

| # | Leçon | Enseigne |
|---|---|---|
| [0001](lessons/0001-names-are-bindings.md) | Les noms sont des liaisons, pas des boîtes | L'affectation lie un nom à un objet et ne le copie jamais, donc deux noms peuvent désigner la même chose |
| [0002](lessons/0002-mutability-and-copying.md) | Mutabilité et copie | La mutabilité appartient à l'objet, donc un conteneur immuable peut quand même contenir quelque chose qui change |
| [0003](lessons/0003-lists-and-slicing.md) | Listes et slicing | Une slice copie, les méthodes en place renvoient None, et += modifie ce que + reconstruirait |
| [0004](lessons/0004-dicts-and-sets.md) | Dicts et sets | Les clés doivent être hashables, la recherche a un seul bon idiome par intention, et une vue n'est pas un instantané |
| [0005](lessons/0005-truthiness-none-and-equality.md) | Valeur de vérité, None et égalité | Vide est faux sans être None, donc le mauvais idiome de valeur par défaut rejette zéro et la chaîne vide |
| [0006](lessons/0006-functions-and-arguments.md) | Fonctions et arguments | Les valeurs par défaut sont évaluées une seule fois, à la définition, et un appelant voit chaque mutation que vous faites |
| [0007](lessons/0007-comprehensions.md) | Compréhensions | Une seule expression qui construit un conteneur, avec sa propre portée et une limite qu'il vaut la peine de respecter |
| [0008](lessons/0008-the-iteration-protocol.md) | Le protocole d'itération | Pourquoi for fonctionne sur n'importe quoi, et pourquoi certaines de ces choses ne peuvent être parcourues qu'une fois |
| [0009](lessons/0009-generators.md) | Générateurs | Une fonction qui se met en pause, conserve son état local, et ne produit des valeurs que lorsqu'on les lui demande |
| [0010](lessons/0010-exceptions.md) | Exceptions | Demander pardon plutôt que la permission, et attraper exactement ce que vous savez traiter |
| [0011](lessons/0011-context-managers.md) | Context managers | Un bloc avec une sortie garantie, et comment en écrire un en six lignes |
| [0012](lessons/0012-dataclasses.md) | Dataclasses | init, repr et égalité générés, et choisir la bonne forme pour un ensemble de données |
| [0013](lessons/0013-modules-and-packages.md) | Modules et paquets | Un module s'exécute une seule fois, un import lie un nom, et comment ces deux faits produisent toutes les erreurs d'import que vous avez vues |
| [0014](lessons/0014-the-standard-library.md) | La bibliothèque standard | Les modules qui suppriment du code que vous alliez écrire, et ceux qui vous évitent une dépendance |
| [0015](lessons/0015-annotations-are-claims.md) | Les annotations sont des affirmations | L'interpréteur les stocke et ne les vérifie jamais, ce qui est justement ce qui les rend utiles à écrire |
| [0016](lessons/0016-making-a-checker-useful.md) | Rendre un vérificateur utile | Configurer la sévérité, lire les codes d'erreur, et affiner les types au lieu de faire taire le vérificateur |
| [0017](lessons/0017-generics-and-protocols.md) | Génériques et protocoles | Conserver le type des éléments à travers une fonction, et typer une forme plutôt qu'une classe |
| [0018](lessons/0018-types-at-the-boundary.md) | Les types à la frontière | Transformer l'Any issu du JSON, de l'environnement et des lignes de base de données en quelque chose sur quoi un vérificateur peut raisonner |
| [0019](lessons/0019-environments-and-dependencies.md) | Environnements et dépendances | L'isolation par projet, la différence entre une exigence et un verrouillage, et qui épingle quoi |
| [0020](lessons/0020-building-a-package.md) | Construire un paquet | Ce qu'est une wheel, ce que doivent dire les métadonnées, et prouver que l'artefact s'installe |
| [0021](lessons/0021-lint-and-format.md) | Lint et formatage | Mettre fin au débat sur le style, et les familles de règles qui trouvent de vrais défauts |
| [0022](lessons/0022-attribute-lookup.md) | Recherche d'attributs | Où la notation pointée cherche réellement, et pourquoi un attribut de classe est partagé par toutes les instances |
| [0023](lessons/0023-properties-and-descriptors.md) | Propriétés et descripteurs | Transformer un attribut en code sans modifier un seul appelant |
| [0024](lessons/0024-dunder-methods.md) | Méthodes dunder | Quels protocoles un type doit implémenter, et lesquels se rabattent sur d'autres |
| [0025](lessons/0025-construction.md) | Construction | Ce que `__init__` ne contrôle pas, quand `__new__` est nécessaire, et nommer vos constructeurs |
| [0026](lessons/0026-inheritance-and-mro.md) | Héritage et MRO | Ce que fait réellement super, pourquoi l'ordre est calculé, et quand la composition l'emporte |
| [0027](lessons/0027-metaclasses-and-why-not.md) | Les métaclasses, et pourquoi s'en passer | Ce que fait réellement une instruction class, et les quatre hooks qui remplacent presque toutes les métaclasses |
| [0028](lessons/0028-what-a-test-asserts.md) | Ce qu'un test vérifie | Un comportement par test, un message d'échec qui ne demande aucun débogueur, et un simple assert |
| [0029](lessons/0029-fixtures.md) | Fixtures | La mise en place comme dépendance que le test demande, avec un nettoyage qui s'exécute quoi qu'il arrive |
| [0030](lessons/0030-parametrisation.md) | Paramétrisation | Un seul corps de test, de nombreux cas, et un échec qui nomme le cas qui a cassé |
| [0031](lessons/0031-test-doubles.md) | Doublures de test | Quoi remplacer, quoi laisser tranquille, et pourquoi patch prend le chemin où le nom est utilisé |
| [0032](lessons/0032-property-based-testing.md) | Property-based testing | Énoncer ce qui doit toujours tenir, et laisser une bibliothèque trouver l'entrée qui le casse |
| [0033](lessons/0033-coverage-and-confidence.md) | Couverture et confiance | Pourquoi 100 pour cent ne prouve rien, à quoi sert ce chiffre, et à quels tests se fier |
| [0034](lessons/0034-the-gil-precisely.md) | Le GIL, précisément | Ce qu'il sérialise, ce qu'il ne protège pas, et ce qui change sans lui |
| [0035](lessons/0035-threads-and-shared-state.md) | Threads et état partagé | Un pool plutôt que des threads bruts, une file plutôt qu'un verrou, et l'exception que personne n'a vue |
| [0036](lessons/0036-processes-and-interpreters.md) | Processus et interpréteurs | Un vrai parallélisme pour le calcul, et ce que coûte l'envoi de données à travers une frontière |
| [0037](lessons/0037-asyncio.md) | asyncio | Un seul thread, des milliers d'attentes, et l'appel bloquant qui les fige toutes |
| [0038](lessons/0038-choosing-a-model.md) | Choisir un modèle | Une seule question tranche, et la mesure règle le reste |
| [0039](lessons/0039-measuring-before-optimising.md) | Mesurer avant d'optimiser | Où passe réellement le temps, et pourquoi les micro-optimisations qu'on vous a apprises n'ont plus cours |
| [0040](lessons/0040-designing-an-api.md) | Concevoir une API | La signature est le contrat, et tout ce qui est observable en devient un, que vous l'ayez voulu ou non |
| [0041](lessons/0041-changing-a-published-api.md) | Modifier une API publiée | Une dépréciation que les utilisateurs voient réellement, et ce qui compte comme changement cassant |
| [0042](lessons/0042-reviewing-python.md) | Relire du Python | Quoi chercher, dans quel ordre, et comment distinguer un défaut d'une préférence |
| [0043](lessons/0043-reading-the-source.md) | Lire le code source | Obtenir la réponse de la bibliothèque standard et des PEP quand la documentation s'arrête |
| [0044](lessons/0044-judgment.md) | Jugement | Quand enfreindre les règles des étapes précédentes, et comment défendre cette décision |

## Référence

- [Glossaire](GLOSSARY.md) : termes de référence pour ce sujet
- [Ressources](RESOURCES.md) : sources fiables, chacune annotée avec ce qu'elle couvre
- [Mutabilité et copie](reference/mutability-and-copying.md) : quels types sont mutables, ce que copie chaque idiome de copie, et qui peut le voir
- [Itération et générateurs](reference/iteration-and-generators.md) : ce qui se consomme une seule fois, ce qui survit à un second passage, et quel outil d'itertools convient
- [Exceptions et nettoyage](reference/exceptions-and-cleanup.md) : la hiérarchie, ce que garantit chaque clause, et quelle exception intégrée lever
- [Typage](reference/typing.md) : les écritures actuelles, les formes d'affinage, les codes d'erreur, et quelle forme utiliser à une frontière
- [Projet et packaging](reference/project-and-packaging.md) : un pyproject.toml annoté, la grammaire des spécificateurs, et les vérifications avant publication
- [Data model](reference/data-model.md) : l'ordre de recherche des attributs, la carte des dunders, le protocole des descripteurs, et quel hook remplace une métaclasse
- [Tests](reference/testing.md) : portées des fixtures, formes de paramétrisation, quelle doublure choisir, et lire un rapport de couverture
- [Concurrence et performance](reference/concurrency-and-performance.md) : quel modèle pour quelle charge de travail, les chiffres mesurés qui le justifient, et comment lire un profil
- [API et relecture](reference/api-and-review.md) : décisions de signature, ce qui compte comme cassant, la liste de contrôle de relecture, et où trouver une réponse

## Comment cela fonctionne

Le fil conducteur est complet : les sept étapes sont écrites, de la leçon 0001 à la leçon 0044. Suivez-les dans l'ordre, ou commencez à l'étape dont vous ne pouvez pas encore démontrer le critère « Terminée quand ».

Chaque leçon est courte et autonome. Les corrigés sont repliés : rappelez-vous d'abord, puis ouvrez-les. Les exercices en situation réelle comptent plus que la lecture, et les espacer dans le temps est justement le but. Tout ce qui reste flou à la fin d'une leçon mérite d'être suivi jusqu'à sa source primaire avant de passer à la suite.
