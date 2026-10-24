---
title: C#
description: "Maîtriser un service C# : le système de types, l'async, et ce que fait le CLR de ce que vous avez écrit, en partant de zéro"
type: topic
---

# Apprentissage : C\#

Devenir l'ingénieur à qui l'on confie un service C# au sein d'une équipe : capable de modéliser un domaine en choisissant correctement entre une struct, une classe et un record, d'écrire du code `async`/`await` et de raisonner dessus, d'interroger et de transformer des données avec aisance grâce à LINQ, de livrer un backend ASP.NET Core typé et testé, et d'expliquer ce que le CLR fait du code que vous avez écrit.

**Dernière leçon :** [45. Packaging et versionnement NuGet](lessons/0045-nuget-packaging-and-versioning.md)

## Objectif

- Modéliser un domaine en choisissant correctement entre une struct, une classe et un record, et défendre ce choix à partir du comportement réel du CLR.
- Écrire du code `async`/`await` et expliquer ce qui arrive à l'exécution d'une méthode à chaque `await`.
- Interroger et transformer des données avec aisance grâce à LINQ.
- Livrer un service backend ASP.NET Core typé et testé, conçu de façon idiomatique pour C#.
- Face à du C# écrit avec une habitude qui se contente de compiler (une classe là où une struct s'impose, un callback au lieu de `async`/`await`), nommer l'habitude et la réécrire de façon idiomatique.

## Contraintes

- Ne suppose aucune connaissance préalable de C#. Une expérience dans un autre langage orienté objet (Java, Kotlin) raccourcit les premières étapes sans être requise, et elle apporte des habitudes que C# punit en silence : une classe là où une struct ou un record s'impose, un callback là où `async`/`await` se lit mieux.
- Contexte ASP.NET Core / service backend ; pas .NET en général sans cette orientation.

## Hors périmètre

- Unity et le développement de jeux en C# : un contexte suffisamment différent pour ne pas être couvert ici.
- Le fonctionnement interne du JIT, et l'écriture ou le réglage manuel d'un garbage collector : l'étape 8 couvre le tas générationnel, les modes de GC et le profilage au niveau dont un responsable de service a besoin pour mesurer et défendre un choix, pas au niveau de leur implémentation.
- Les images de conteneur : placer un service publié dans une image, puis exécuter, sécuriser et déboguer ce conteneur, relève de [`infrastructure/containers`](../../infrastructure/containers/).
- Faire tourner le service sur un cluster, y compris ce que Kubernetes fait de ses checks de liveness et de readiness, relève de [`infrastructure/kubernetes`](../../infrastructure/kubernetes/).

## Le fil conducteur

Onze étapes, de zéro jusqu'au niveau senior. Pas une liste de leçons : une étape comprend plusieurs leçons, et les frontières sont souples.

| Étape | Leçons | Contenu | Terminée quand |
|---|---|---|---|
| 1. Fondations | 0001 à 0006 | Types valeur contre types référence (struct contre classe), types valeur nullables, types de base et interpolation de chaînes, collections (`List`, `Dictionary`, `IEnumerable`), structures de contrôle, exceptions | Vous savez prédire le comportement par copie ou par référence sans exécuter le code |
| 2. Modélisation | 0007 à 0011 | Propriétés, types `record`, pattern matching et switch expressions, interfaces avec implémentations par défaut, génériques | Vous modélisez un domaine en choisissant le bon type au lieu d'une classe pour tout |
| 3. Idiomes | 0012 à 0016 | Méthodes d'extension, syntaxe de requête et syntaxe de méthode de LINQ, délégués et événements, types référence nullables, membres à corps d'expression | Vous écrivez du C# qu'un relecteur ne qualifierait pas de Java traduit |
| 4. Async | 0017 à 0021 | Le modèle `Task`, la mécanique de `async`/`await`, la composition de `Task`, les cancellation tokens, `IAsyncEnumerable` | Vous savez expliquer ce que `await` fait à l'exécution d'une méthode et prédire le comportement d'un programme asynchrone |
| 5. Tests et build | 0022 à 0024 | xUnit/NUnit, mocking, la CLI `dotnet` et la gestion des projets et des paquets | Quelqu'un d'autre peut le cloner, le construire, le tester et l'exécuter |
| 6. Livrer le service | 0025 à 0029 | Routage et middleware ASP.NET Core, injection de dépendances, configuration, bases d'Entity Framework Core, structuration d'un backend typé et testé | Vous livrez un service ASP.NET Core typé et testé |
| 7. Jugement | 0030 à 0031 | Comparer `async`/`await` aux virtual threads de Java et LINQ à la Stream API, relire du C# à la recherche d'une habitude qui se contente de compiler | On vous fait confiance pour trancher et l'expliquer à quelqu'un d'autre |
| 8. Le runtime CLR et la performance | 0032 à 0037 | La conception générationnelle du tas managé, les modes de GC, `Span<T>`/`Memory<T>`, `stackalloc`/`ArrayPool<T>`, la mesure de struct contre classe avec BenchmarkDotNet, et le profilage | Vous optimisez à partir d'un profil et défendez le gain avec un benchmark fiable, rattaché au comportement générationnel et d'allocation réel du CLR |
| 9. Durée de vie des ressources | 0038 | Implémenter `IDisposable` et `IAsyncDisposable` : le dispose pattern, le paramètre `disposing`, les finaliseurs et `DisposeAsyncCore` | Vous implémentez un dispose pattern correct et idempotent au lieu de seulement en consommer un via `using` |
| 10. Exploiter et sécuriser le service | 0039 à 0042 | Logging structuré avec `ILogger`, health checks de liveness/readiness, OpenTelemetry, authentification et autorisation, et sérialisation avec `System.Text.Json` | Vous livrez un service qui peut être observé, vérifié, sécurisé et correctement sérialisé, pas seulement construit |
| 11. Évolution de l'API et packaging | 0043 à 0045 | Compatibilité binaire, source et comportementale, `[Obsolete]` et la dépréciation, packaging NuGet et versionnement sémantique | Vous classez précisément l'impact d'une modification sur la compatibilité et faites évoluer une API publiée sans casser les appelants par surprise |

## Leçons

Suivez-les dans l'ordre.

| # | Leçon | Enseigne |
|---|---|---|
| [0001](lessons/0001-structs-and-classes.md) | Structs et classes | Le choix de système de types que Java ne vous a jamais offert, et ce que le CLR fait réellement de chacun |
| [0002](lessons/0002-nullable-value-types.md) | Types valeur nullables | Pourquoi int? reste un type valeur, la règle de comparaison qui rend les deux sens faux, et ce que le boxing fait à l'enveloppe |
| [0003](lessons/0003-basic-types-and-string-interpolation.md) | Types de base et interpolation de chaînes | Les mots-clés comme alias de types .NET, pourquoi decimal est intégré au langage plutôt qu'une classe, et les règles de largeur, de format et d'effets de bord d'un trou d'interpolation |
| [0004](lessons/0004-collections.md) | Collections | IEnumerable comme abstraction sur laquelle s'appuie le reste du fil conducteur, et la recherche dans un dictionnaire qui lève une exception là où la map de Java renvoie null |
| [0005](lessons/0005-control-flow.md) | Structures de contrôle | Les trois endroits où les structures de contrôle ne se transposent pas depuis Java : l'énumérateur à duck typing de foreach, le switch sans fall-through, et goto comme saut légal |
| [0006](lessons/0006-exceptions.md) | Exceptions | Les filtres d'exception et la stack trace que détruit un catch suivi d'un rethrow, using pour un nettoyage déterministe, et la synthèse de l'étape 1 |
| [0007](lessons/0007-properties.md) | Propriétés | Les accesseurs comme fonctionnalité du langage, les trois promesses orthogonales de required, d'init et d'un type non nullable, et les propriétés calculées sans champ de stockage |
| [0008](lessons/0008-record-types.md) | Types record | Ce que génère réellement le modificateur record, pourquoi l'égalité dépend du type à l'exécution, et l'immuabilité superficielle qu'une expression with ne corrige pas |
| [0009](lessons/0009-pattern-matching.md) | Pattern matching | Le vocabulaire des patterns, l'exhaustivité de la switch expression et son unique trou silencieux, et pourquoi l'ordre des branches est une question de compilation |
| [0010](lessons/0010-interfaces.md) | Interfaces | Ce qu'une interface peut contenir maintenant qu'elle peut porter des implémentations, l'auto-propriété qui n'en est pas une, et le membre que l'on ne peut appeler qu'à travers l'interface |
| [0011](lessons/0011-generics.md) | Génériques | Les contraintes comme vocabulaire de ce que doit être un paramètre de type, la variance comme règle portant sur les positions, et la synthèse de l'étape 2 sur le choix du bon type |
| [0012](lessons/0012-extension-methods.md) | Méthodes d'extension | Deux syntaxes qui compilent vers le même IL, la règle de liaison qui empêche une extension de remplacer quoi que ce soit, et ce que cela coûte à un site d'appel |
| [0013](lessons/0013-linq.md) | LINQ | Un seul langage de requête avec deux syntaxes et aucune différence sémantique, pourquoi rien ne s'exécute tant que vous n'itérez pas, et l'arbre d'expression qui permet à la même requête d'atteindre une base de données |
| [0014](lessons/0014-delegates-and-events.md) | Délégués et événements | Un délégué comme type dont la signature inclut son type de retour, la liste d'invocation où un gestionnaire qui lève une exception arrête les suivants, et ce que le mot-clé event retire aux appelants |
| [0015](lessons/0015-nullable-reference-types.md) | Types référence nullables | Des annotations plutôt que des types, l'état de nullité que le compilateur suit à travers vos structures de contrôle, et la seule bibliothèque qui transforme votre annotation en comportement à l'exécution |
| [0016](lessons/0016-expression-bodied-members.md) | Membres à corps d'expression | Le second rôle du jeton flèche, la règle des expressions-instructions pour les membres void, et la synthèse de l'étape 3 consistant à réécrire du Java traduit |
| [0017](lessons/0017-the-task-model.md) | Le modèle Task | Une task comme opération asynchrone plutôt que comme thread, les quatre façons dont elle peut naître, et l'AggregateException qui peut terminer un processus que vous croyiez fini |
| [0018](lessons/0018-async-and-await.md) | async et await | Ce que await fait à la méthode englobante, les trois endroits où il est interdit, et pourquoi async void casse le seul mécanisme dont dispose un appelant |
| [0019](lessons/0019-task-composition.md) | Composition de tasks | Lancer un travail avant de l'attendre, le ToArray qui fait réellement tourner une liste de tasks construite avec LINQ, et le double await qu'exige WhenAny |
| [0020](lessons/0020-cancellation-tokens.md) | Cancellation tokens | L'annulation coopérative avec un demandeur et de nombreux écouteurs, pourquoi un retour anticipé signale un succès, et la comparaison de tokens qui décide si une task se déclare annulée |
| [0021](lessons/0021-async-streams.md) | Flux asynchrones | Les trois interfaces derrière await foreach, l'attribut qui permet au token d'un consommateur d'atteindre le corps d'un itérateur asynchrone, et la synthèse de l'étape 4 consistant à prédire un programme asynchrone |
| [0022](lessons/0022-xunit-and-nunit.md) | xUnit et NUnit | La règle d'une instance par test qui dispense xUnit de tout attribut de setup, le mot theory qui désigne deux choses différentes, et le parallélisme que coûte discrètement une fixture partagée |
| [0023](lessons/0023-mocking.md) | Mocking | Le proxy à l'exécution derrière chaque bibliothèque de substitution, la valeur par défaut de C# qui décide de ce qu'elle a le droit de remplacer, et l'assertion sur un mock qui passe sans que l'appel ait jamais eu lieu |
| [0024](lessons/0024-the-dotnet-cli-and-packages.md) | La CLI dotnet et les paquets | La seule commande dont un clone tout neuf a besoin, pourquoi une version de paquet est un plancher plutôt qu'un épinglage, la version du SDK qui a réordonné les commandes, et la synthèse de l'étape 5 |
| [0025](lessons/0025-routing-and-middleware.md) | Routage et middleware | Deux systèmes qui partagent un même Program.cs, l'un réglé par l'ordre dans lequel vous avez écrit, l'autre par la priorité des templates, et les deux positions qui décident de ce qu'un middleware peut savoir et s'il s'exécute seulement |
| [0026](lessons/0026-dependency-injection.md) | Injection de dépendances | Trois durées de vie comme affirmations que le conteneur ne fait respecter que là où il peut les voir, le service de longue durée qui promeut en silence un service de courte durée, et pourquoi personne ne libère ce que le conteneur a créé |
| [0027](lessons/0027-configuration.md) | Configuration | Un unique dictionnaire plat de chaînes où le dernier fournisseur l'emporte, trois interfaces d'options séparées par la durée de vie plutôt que par goût, et une validation qui attend la première requête sauf si vous lui demandez le contraire |
| [0028](lessons/0028-entity-framework-core.md) | Entity Framework Core | Un contexte qui se souvient de ce que vous avez interrogé, si bien qu'une affectation devient une mise à jour, le seul endroit où une requête a le droit de se replier côté client, et pourquoi l'habitude de l'étape 4 de faire se chevaucher les travaux le corrompt |
| [0029](lessons/0029-structuring-a-typed-tested-backend.md) | Structurer un backend typé et testé | Le conteneur comme jointure par laquelle un test remplace des enregistrements, la règle documentée pour choisir entre un test unitaire et un test d'intégration, et la synthèse de l'étape 6 avec quatre défauts qui compilent tous |
| [0030](lessons/0030-two-comparisons-with-java.md) | Deux comparaisons avec Java | Le même problème d'attente résolu à deux couches différentes, pourquoi la réponse de Java supprime le style que C# exige au lieu de l'adopter, et l'arbre d'expression qui n'a pas d'équivalent dans un Stream |
| [0031](lessons/0031-reviewing-csharp.md) | Relire une base de code C# | La différence entre une opinion de style et un coût que l'on peut nommer, une passe de relecture ordonnée selon ce que le compilateur ne vous dira jamais, et les habitudes que ce fil conducteur collectionne depuis la leçon 1 |
| [0032](lessons/0032-the-managed-heap-and-generations.md) | Le tas managé et les générations | La leçon 1 disait qu'une instance de classe vit sur le tas managé ; cette leçon ouvre ce qui lui arrive là-bas, pourquoi le tas est divisé en trois générations, et pourquoi la plupart des objets sont censés mourir dans la plus jeune sans jamais être promus |
| [0033](lessons/0033-gc-modes-and-tradeoffs.md) | Modes de GC et compromis | La leçon 32 a posé le tas générationnel ; cette leçon couvre la façon dont une collecte s'y exécute réellement, un thread dédié ou un par cœur, en bloquant tous les threads managés ou en laissant la plupart continuer, et le seul moment où même le mode non bloquant doit encore tout arrêter |
| [0034](lessons/0034-span-and-memory.md) | Span et Memory | Une vue sans allocation sur une mémoire existante qui n'entre jamais dans le système générationnel de la leçon 32, les restrictions du compilateur qui la confinent en toute sûreté à la pile, et l'équivalent sûr pour le tas conçu précisément pour la seule chose qu'elle ne peut pas faire : traverser un await |
| [0035](lessons/0035-stackalloc-and-arraypool.md) | stackalloc et ArrayPool | La leçon 34 a permis à un Span<T> de voir une mémoire allouée par stackalloc ; cette leçon couvre ce que stackalloc alloue réellement, pourquoi l'associer à une ref struct est ce qui le rend sûr, son vrai risque (un dépassement de pile, pas le garbage collection), et ArrayPool<T> comme repli pour un buffer trop grand ou trop durable pour la pile |
| [0036](lessons/0036-struct-vs-class-measured.md) | Struct contre classe, mesuré | La leçon 1 soutenait qu'une struct peut éviter une allocation sur le tas qu'une classe de même forme exigerait ; cette leçon est celle où cet argument est mesuré au lieu d'être raisonné, et où l'on voit pourquoi la façon évidente de le mesurer produit un chiffre qui ne signifie rien du tout |
| [0037](lessons/0037-profiling-a-csharp-service.md) | Profiler un service C# | dotnet-counters attrape le symptôme et dotnet-trace trouve la pile chaude qui se cache derrière, profiler seulement après le préchauffage pour que ce ne soit pas le JIT qui soit mesuré, et la synthèse de l'étape 8 consistant à renvoyer la conclusion d'un profil vers l'un des leviers de cette même étape |
| [0038](lessons/0038-idisposable-and-iasyncdisposable.md) | IDisposable et IAsyncDisposable | La leçon 6 a enseigné using du point de vue du consommateur, et la leçon 26 qu'un conteneur libère ce qu'il crée ; cette leçon traite de l'autre côté, implémenter réellement IDisposable et IAsyncDisposable, le pattern qui rend un type sûr à libérer plus d'une fois, sûr à finaliser et sûr à attendre |
| [0039](lessons/0039-logging-and-health-checks.md) | Logging et health checks | Un backend typé et testé que personne ne peut observer ni interroger avec « est-ce que tu fonctionnes » n'a pas fini d'être livré ; cette leçon branche le logging structuré d'ILogger et la séparation liveness/readiness dans Program.cs, de la même façon que la leçon 25 a branché le routage et la leçon 26 le conteneur |
| [0040](lessons/0040-opentelemetry.md) | OpenTelemetry | L'ILogger de la leçon 39 est déjà l'un des trois piliers d'OpenTelemetry ; cette leçon ajoute les deux autres, les métriques et les traces, au moyen d'API déjà intégrées au framework, et branche les trois dans un service avec le même pattern AddX que les leçons 25, 26 et 39 ont déjà enseigné |
| [0041](lessons/0041-authentication-and-authorization.md) | Authentification et autorisation | L'authentification répond à qui vous êtes et l'autorisation à ce que vous avez le droit de faire, documentées comme des préoccupations distinctes même si l'une s'appuie sur l'autre, branchées avec la discipline d'ordonnancement des middlewares de la leçon 25 et la dérogation AllowAnonymous dont les health checks de la leçon 39 ont réellement besoin |
| [0042](lessons/0042-system-text-json.md) | System.Text.Json | Les valeurs par défaut du sérialiseur nu (PascalCase, sensible à la casse) ne sont pas celles qu'ASP.NET Core utilise réellement à la frontière HTTP (camelCase, insensible à la casse), une vraie divergence qu'il vaut la peine de nommer avant qu'elle ne produise un résultat de test déroutant, plus la génération de source comme alternative à la réflexion au moment de la compilation |
| [0043](lessons/0043-api-compatibility.md) | Compatibilité d'API | Une modification qui recompile proprement peut quand même faire échouer chaque appelant qui ne recompile pas, une modification qui ne compile pas peut convenir parfaitement aux appelants qui ont déjà un binaire fonctionnel, et une modification qui ne fait ni l'un ni l'autre peut encore faire silencieusement autre chose, précisément le cas dont le versionnement sémantique existe pour avertir un appelant |
| [0044](lessons/0044-obsolete-and-deprecation.md) | Obsolete et dépréciation | La leçon 43 a nommé ce qui compte comme changement cassant ; ObsoleteAttribute est la façon dont une API publiée annonce qu'il arrive, en passant d'un avertissement masquable à une vraie erreur de compilation sur le même membre, avec un identifiant de diagnostic personnalisé pour que l'avertissement d'une dépréciation puisse être réduit au silence sans faire taire tous les autres du projet |
| [0045](lessons/0045-nuget-packaging-and-versioning.md) | Packaging et versionnement NuGet | La dernière leçon de ce fil conducteur relie l'ensemble de l'étape 11 : le numéro de version que justifient réellement les catégories de compatibilité de la leçon 43, le suffixe de préversion sur lequel NuGet n'impose rien d'autre que de l'appeler préversion, le conseil sur la borne supérieure qui va à l'encontre de l'intuition, et le paquet périmé qu'une reconstruction peut vous laisser tester |

## Référence

- [Glossaire](GLOSSARY.md) : termes de référence pour ce sujet
- [Ressources](RESOURCES.md) : sources fiables
- [Types valeur et types référence](reference/value-vs-reference-types.md) : struct contre classe, types valeur nullables, prédire le comportement par copie ou par référence
- [Modélisation](reference/modelling.md) : types `record`, pattern matching et switch expressions, interfaces avec implémentations par défaut, génériques
- [Idiomes](reference/idiom.md) : méthodes d'extension, LINQ, délégués et événements, types référence nullables
- [Async](reference/async.md) : le modèle `Task`, la mécanique de `async`/`await`, les cancellation tokens, `IAsyncEnumerable`
- [Tests et build](reference/testing-and-build.md) : xUnit/NUnit, mocking, la CLI `dotnet` et la gestion des projets et des paquets
- [Livrer le service](reference/shipping-the-service.md) : routage et middleware ASP.NET Core, injection de dépendances, configuration, bases d'Entity Framework Core
- [Jugement](reference/judgment.md) : `async`/`await` contre les virtual threads de Java, LINQ contre la Stream API, relire du C# à la recherche d'une habitude qui se contente de compiler

## Comment cela fonctionne

Chaque leçon est courte et autonome. Les corrigés sont repliés : rappelez-vous d'abord, puis ouvrez-les. Les exercices en situation réelle comptent plus que la lecture, et les espacer dans le temps est justement le but. Tout ce qui reste flou à la fin d'une leçon mérite d'être suivi jusqu'à sa source primaire avant de passer à la suite.
