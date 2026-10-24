---
title: Kotlin
description: "Maîtriser Kotlin sur la JVM : null safety, coroutines, et du Kotlin idiomatique en partant de zéro"
type: topic
---

# Apprentissage : Kotlin

Devenir l'ingénieur à qui l'on confie Kotlin au sein d'une équipe, dans un service backend ou une application Android : capable de modéliser un domaine de façon idiomatique, d'écrire des coroutines et des `Flow` et de raisonner dessus, de livrer un service Kotlin ou un composant Android typé et testé, et de relire le Kotlin de quelqu'un en nommant concrètement ce que lui coûte une construction.

**Dernière leçon :** [44. Tester les coroutines au-delà de runTest](lessons/0044-testing-coroutines-beyond-runtest.md)

## Objectif

- Modéliser un domaine avec des data classes, des sealed classes et des enums, et savoir quand la null safety, et non une exception, est le bon signal.
- Écrire des coroutines et des `Flow` et raisonner dessus, et comparer ce modèle aux virtual threads de Java.
- Livrer un service backend Kotlin ou un composant Android typé et testé, conçu de façon idiomatique.
- Face à du Kotlin écrit avec une habitude qui se contente de compiler (des vérifications défensives de null au lieu du système de types, un callback au lieu d'une coroutine), nommer l'habitude et la réécrire de façon idiomatique.

## Contraintes

- Ne suppose aucune connaissance préalable de Kotlin. Une expérience en Java ou dans un autre langage de la JVM raccourcit les premières étapes sans être requise, et elle apporte des habitudes que Kotlin punit en silence : des vérifications défensives de null au lieu du système de types, une classe là où une data class ou un sealed type le dirait mieux.
- Couvre à la fois le contexte backend/côté serveur et le contexte Android, en abordant chacun là où ils divergent.
- Ne nécessite qu'un JDK, la toolchain Kotlin et un terminal ; Android Studio seulement là où le contenu propre à Android l'exige.

## Hors périmètre

- Le fonctionnement interne de la JVM au-delà de ce qui explique le comportement compilé de Kotlin lui-même (réglage complet du garbage collector, profilage, ingénierie du bytecode) : voir [`programming/java`](../../programming/java/), vers lequel on renvoie pour approfondir plutôt que de le réenseigner.
- Les autres langages de la JVM (Java, Scala, Clojure, Groovy) en tant que sujets à part entière, même si un contraste apparaît là où il éclaire un idiome Kotlin.
- Kotlin Multiplatform : cibler JS, Native ou Wasm, structurer des déclarations `expect`/`actual` entre source sets, et les différences de stdlib propres à chaque plateforme qu'introduisent ces cibles. Ce fil conducteur est entièrement limité à la JVM, conformément à la formulation même de la mission ; une leçon sur ce sujet demanderait sa propre configuration Gradle et son propre ensemble d'idiomes, et non une leçon JVM avec une note de bas de page sur le multiplateforme. `kotlinx.serialization` (leçon 38) est le seul endroit où la portée multiplateforme est mentionnée, comme raison documentée d'un choix de conception côté JVM, et non comme contenu multiplateforme à part entière.

## Le fil conducteur

Onze étapes, de zéro jusqu'au niveau senior. Pas une liste de leçons : une étape comprend plusieurs leçons, et les frontières sont souples.

| Étape | Leçons | Contenu | Terminée quand |
|---|---|---|---|
| 1. Fondations | 0001 à 0006 | Null safety, `val`/`var` et immuabilité, valeurs contre références, types de base et string templates, bases des collections (`List`/`Set`/`Map`, mutables contre en lecture seule), structures de contrôle (`when`, ranges, `for`) | Vous savez prédire la nullabilité et la mutabilité sans exécuter le code |
| 2. Modélisation | 0007 à 0012 | Classes et propriétés, data classes, sealed classes et `when` exhaustif, enums, déclarations object et companion objects, interfaces avec méthodes par défaut | Vous modélisez un domaine sans recourir d'abord à une hiérarchie d'une classe par concept |
| 3. Idiomes | 0013 à 0018 | Fonctions d'extension, scope functions (`let`/`run`/`with`/`apply`/`also`), fonctions d'ordre supérieur et lambdas, fonctions inline et génériques reified, délégation (`by`), surcharge d'opérateurs | Vous écrivez du Kotlin qu'un relecteur ne qualifierait pas de Java traduit |
| 4. Collections et séquences | 0019 à 0021 | Les opérateurs de collection de Kotlin, `Sequence` paresseuse contre collections avides, regroupement et fold | Vous choisissez entre un pipeline de collection et une séquence, et savez défendre le coût de chacun |
| 5. Concurrence | 0022 à 0027 | Threads et bases du modèle mémoire de la JVM, fonctions suspend et coroutine builders, concurrence structurée, contexte de coroutine et dispatchers, `Flow`, annulation et gestion des exceptions | Vous savez prédire ce que fait un programme concurrent à base de coroutines avant de l'exécuter, et comparer ce modèle aux virtual threads de Java |
| 6. Tests et build | 0028 à 0030 | Frameworks de test Kotlin, mocking, le Kotlin DSL de Gradle et la gestion des dépendances | Quelqu'un d'autre peut le cloner, le construire, le tester et l'exécuter |
| 7. Livrer un service | 0031 à 0033 | Structurer un service backend typé et testé, idiomes propres à Android là où la plateforme diverge, génériques et variance (`in`/`out`) | Vous avez structuré un service backend Kotlin ou un composant Android typé et testé ; l'étape 10 le complète avec une couche HTTP, la configuration, le logging et la persistance |
| 8. Jugement | 0034 à 0035 | L'interopérabilité avec Java, relire du Kotlin et nommer précisément ce que coûte une construction | On vous fait confiance pour trancher et l'expliquer à quelqu'un d'autre |
| 9. Idiomes avancés | 0036 à 0039 | Type-safe builders et DSL, `value class`/`@JvmInline`, `kotlinx.serialization`, `Result` et idiomes de gestion des erreurs | Vous écrivez de façon idiomatique un petit DSL de type-safe builder, un type enveloppe sans coût et un chemin d'erreur fondé sur `Result` |
| 10. Compléter le service | 0040 à 0043 | Une couche HTTP, la configuration, le logging et la persistance pour le service backend Kotlin que l'étape 7 a commencé à structurer | Vous livrez un service backend Kotlin avec une couche HTTP routée, une configuration externalisée, un logging structuré et un accès à la base de données, pas seulement une coquille structurée |
| 11. Tester les coroutines au-delà de runTest | 0044 | Le `cancelAndIgnoreRemainingEvents()` de Turbine pour un flow qui ne se termine jamais, et ce qu'un test d'annulation doit réellement vérifier étant donné que l'annulation est coopérative | Vous testez un flow infini sans blocage, et testez l'annulation par ses preuves réelles et documentées plutôt que par un seul indicateur de `Job` |

## Leçons

Suivez-les dans l'ordre.

| # | Leçon | Enseigne |
|---|---|---|
| [0001](lessons/0001-null-safety.md) | Null safety | Faire passer « est-ce que ça peut être null » d'une surprise à l'exécution à une question de compilation, et comment l'habitude Java défait cela |
| [0002](lessons/0002-val-var-and-immutability.md) | val/var et immuabilité | Pourquoi val est la valeur par défaut qui mérite d'être défendue, ce qu'il garantit réellement (et ne garantit pas), et l'habitude Java de recourir à var par réflexe |
| [0003](lessons/0003-values-vs-references.md) | Valeurs contre références | Pourquoi == signifie autre chose en Kotlin qu'en Java, et le bug précis que produit l'habitude Java d'écrire == |
| [0004](lessons/0004-basic-types-and-string-templates.md) | Types de base et string templates | Pourquoi Kotlin n'a pas de primitifs au niveau du langage, et les string templates comme fonctionnalité du langage plutôt que comme une concaténation avec une syntaxe en plus |
| [0005](lessons/0005-collections-basics.md) | Bases des collections | List, Set et Map comme collections en lecture seule par leur interface, et pourquoi une collection mutable détenue par un val reste mutable |
| [0006](lessons/0006-control-flow.md) | Structures de contrôle | if et when comme expressions qui produisent des valeurs, ce qu'est réellement un range, et la synthèse de l'étape 1 consistant à prédire nullabilité et mutabilité sans exécuter le code |
| [0007](lessons/0007-classes-and-properties.md) | Classes et propriétés | Les propriétés comme remplacement du code répétitif getter/setter de Java, et pourquoi la documentation de Kotlin elle-même conseille de recourir à une classe en dernier |
| [0008](lessons/0008-data-classes.md) | Data classes | Ce que génère réellement data class, et la règle subtile selon laquelle seules les propriétés du constructeur primaire y participent |
| [0009](lessons/0009-sealed-classes-and-exhaustive-when.md) | Sealed classes et when exhaustif | Comment sceller une hiérarchie transforme l'exhaustivité d'un when d'une promesse manuelle en une garantie vérifiée par le compilateur |
| [0010](lessons/0010-enums.md) | Enums | Chaque constante d'enum comme un vrai objet doté de son propre état et de son propre comportement, et précisément quand une enum convient mieux qu'une sealed class |
| [0011](lessons/0011-object-declarations-and-companion-objects.md) | Déclarations object et companion objects | Des singletons déclarés, et non implémentés à la main, et les companion objects comme véritable remplacement par Kotlin des membres static de Java |
| [0012](lessons/0012-interfaces-with-default-methods.md) | Interfaces avec méthodes par défaut | Pourquoi une interface Kotlin peut implémenter un comportement sans jamais détenir d'état, et comment résoudre explicitement un conflit en diamant |
| [0013](lessons/0013-extension-functions.md) | Fonctions d'extension | Ajouter un comportement à un type sans héritage, et le piège de la liaison statique qui surprend la première fois qu'on le rencontre |
| [0014](lessons/0014-scope-functions.md) | Scope functions | Choisir entre let, run, with, apply et also selon ce que chacune renvoie et la façon dont elle expose l'objet, pas par habitude |
| [0015](lessons/0015-higher-order-functions-and-lambdas.md) | Fonctions d'ordre supérieur et lambdas | Les types fonction comme de vrais types, la syntaxe de lambda finale, et le mécanisme de receiver sur lequel les scope functions sont réellement construites |
| [0016](lessons/0016-inline-functions-and-reified-generics.md) | Fonctions inline et génériques reified | Pourquoi inline existe pour supprimer un coût réel, pourquoi il permet les retours non locaux, et pourquoi les paramètres de type reified ne fonctionnent que grâce à l'inlining |
| [0017](lessons/0017-delegation.md) | Délégation | Implémenter une interface en déléguant à un objet détenu sans aucun code répétitif, et un comportement de propriété réutilisable via by lazy et des délégués personnalisés |
| [0018](lessons/0018-operator-overloading.md) | Surcharge d'opérateurs | Les opérateurs comme fonctions nommées ordinaires avec une correspondance fixe vers un symbole, et la vraie discipline consistant à n'en implémenter un que là où il signifie ce que le symbole signifie déjà |
| [0019](lessons/0019-collection-operators.md) | Opérateurs de collection | Les opérateurs de collection comme fonctions d'extension qui renvoient avidement une nouvelle collection, et l'habitude des Streams Java qui évalue mal le coût d'une chaîne de ces opérateurs |
| [0020](lessons/0020-sequences-and-laziness.md) | Séquences et paresse | Pourquoi la même chaîne d'opérateurs se comporte différemment sur une Sequence, à quoi sert réellement une opération terminale, et quand la paresse coûte plus qu'elle ne fait gagner |
| [0021](lessons/0021-grouping-and-folding.md) | Regroupement et fold | Agréger avec fold et reduce, regrouper sans construire les groupes, et la synthèse de l'étape 4 consistant à défendre ce que coûte un pipeline |
| [0022](lessons/0022-threads-and-the-memory-model.md) | Threads et modèle mémoire | Pourquoi Kotlin n'a pas de modèle mémoire propre sur la JVM, les trois constructions qu'il exprime par des annotations plutôt que par des mots-clés, et les deux garanties qu'un val ne vous donne pas |
| [0023](lessons/0023-suspend-functions-and-coroutine-builders.md) | Fonctions suspend et coroutine builders | Ce que suspend change réellement à une fonction, les trois builders et ce que chacun renvoie, et pourquoi du code suspendu se lit toujours de haut en bas |
| [0024](lessons/0024-structured-concurrency.md) | Concurrence structurée | L'arbre parent-enfant qui rend l'annulation prévisible, pourquoi un scope que vous possédez est un scope que vous devez annuler, et ce que coûte réellement GlobalScope |
| [0025](lessons/0025-coroutine-context-and-dispatchers.md) | Contexte de coroutine et dispatchers | Le contexte comme ensemble d'éléments combinés avec plus, quel dispatcher convient à quel type de travail, et le seul élément de contexte qui casse silencieusement la concurrence structurée |
| [0026](lessons/0026-flows.md) | Flows | Un flow comme troisième option asynchrone après une liste et une séquence, ce que « cold » signifie réellement pour chaque collecteur, et la règle de contexte qu'un flow builder fait respecter à l'exécution |
| [0027](lessons/0027-cancellation-and-exception-handling.md) | Annulation et gestion des exceptions | Pourquoi l'annulation est coopérative et ce qui fait que du code l'ignore, pourquoi une CancellationException n'est pas un échec, et comment le modèle des coroutines se compare aux virtual threads de Java |
| [0028](lessons/0028-test-frameworks.md) | Frameworks de test | Les couches sur lesquelles repose réellement un test Kotlin, pourquoi le temps virtuel de runTest s'arrête à la frontière du dispatcher, et ce que cela impose à la conception du code testé |
| [0029](lessons/0029-mocking.md) | Mocking | Pourquoi le final par défaut change ce que signifie le mocking en Kotlin, ce que fait MockK pour les constructions qui ne sont pas des méthodes d'un objet, et quand le caractère final vous signale qu'une jointure manque |
| [0030](lessons/0030-gradle-and-dependency-management.md) | Gradle et gestion des dépendances | Les accesseurs type-safe du Kotlin DSL et leurs limites, pourquoi une configuration Gradle n'est pas un scope Maven, et la règle de résolution qui décide quelle version atteint le classpath |
| [0031](lessons/0031-structuring-a-service.md) | Structurer un service | Où vont réellement les fichiers Kotlin et ce qui va dans une classe, et les quatre décisions des étapes précédentes qui décident si un service est testable |
| [0032](lessons/0032-android-divergences.md) | Divergences d'Android | Les scopes qu'Android possède pour vous, la main-safety comme contrat que respecte l'appelé, et pourquoi la durée de vie d'une composition n'est pas celle d'un cycle de vie |
| [0033](lessons/0033-generics-and-variance.md) | Génériques et variance | La variance au site de déclaration à la place des wildcards, ce que out et in promettent réellement sur un paramètre de type, et comment lire une signature projetée |
| [0034](lessons/0034-java-interop.md) | Interopérabilité avec Java | Pourquoi la frontière est asymétrique, ce que vous coûte un platform type et comment rembourser ce coût, et quelles annotations vous devez à un appelant Java |
| [0035](lessons/0035-reviewing-kotlin.md) | Relire du Kotlin | Transformer le fil conducteur en instrument de relecture : le coût que cache chaque habitude, la forme d'un commentaire qui le nomme, et ce qu'il ne faut pas relire |
| [0036](lessons/0036-type-safe-builders-and-dsls.md) | Type-safe builders et DSL | La leçon 15 a enseigné le type fonction avec receiver qui permet à run et apply d'exposer this ; un type-safe builder est exactement ce mécanisme imbriqué récursivement, et @DslMarker est l'unique attribut qui empêche un builder imbriqué d'atteindre silencieusement le mauvais receiver |
| [0037](lessons/0037-value-classes.md) | value class et @JvmInline | Une value class est le remède à la primitive obsession que la JVM vous laisse généralement avoir gratuitement, représentée comme sa propre valeur sous-jacente sans aucun objet enveloppe, sauf dans les cas précis et documentés où le compilateur doit encore la boxer |
| [0038](lessons/0038-kotlinx-serialization.md) | kotlinx.serialization | Une habitude Java recourt à une bibliothèque qui inspecte la forme d'une classe par réflexion à l'exécution ; kotlinx.serialization génère plutôt cette même logique à la compilation, via un plugin du compilateur, ce qui est précisément ce qui lui permet de fonctionner sur des cibles Kotlin dépourvues de toute API de réflexion à l'exécution |
| [0039](lessons/0039-result-and-error-handling.md) | Result et idiomes de gestion des erreurs | runCatching enveloppe n'importe quel Throwable dans un Result, ce qui est précisément le problème dans une coroutine, puisque l'annulation coopérative de la leçon 27 dépend d'une CancellationException qui se propage sans être attrapée, et que runCatching l'avale en un échec ordinaire à moins qu'un appelant ne la relance explicitement d'abord |
| [0040](lessons/0040-http-layer.md) | Couche HTTP | La leçon 31 a délibérément laissé le routage au framework choisi ; le bloc routing de Ktor s'avère être le DSL de type-safe builder de la leçon 36 appliqué à HTTP, rien n'est installé par défaut, et l'extraction des paramètres de requête échoue bruyamment plutôt que de lier silencieusement la mauvaise valeur |
| [0041](lessons/0041-configuration.md) | Configuration | Le comportement réel d'un service, son port, l'URL de sa base de données, ses secrets, doit changer d'un environnement à l'autre sans recompiler une seule ligne, et le fichier de configuration de Ktor associé à un idiome de substitution précis et facile à manquer est la façon dont une valeur par défaut et une surcharge par environnement vivent en un seul et même endroit |
| [0042](lessons/0042-logging.md) | Logging | SLF4J ne fait silencieusement rien tant qu'un vrai backend de logging n'est pas ajouté comme dépendance, et les valeurs MDC par requête de CallLogging restent silencieusement invisibles tant que le pattern de log lui-même n'est pas mis à jour pour les afficher : le même type de piège apparaît deux fois dans la même leçon |
| [0043](lessons/0043-persistence.md) | Persistance | Le DSL d'Exposed est un autre type-safe builder, et il est essentiellement bloquant en dessous, puisqu'il enveloppe JDBC ; la synthèse de l'étape 10 consiste à répartir correctement ce travail bloquant au lieu de bloquer le thread qui traitait la requête, et à revenir sur ce dont le service livré à l'étape 7 avait réellement besoin depuis le début |
| [0044](lessons/0044-testing-coroutines-beyond-runtest.md) | Tester les coroutines au-delà de runTest | La leçon 28 a enseigné l'awaitItem de Turbine et le blocage qu'il provoque si rien ne le termine ; cette leçon couvre l'outil précis pour un flow qui ne se termine jamais de lui-même, et ce qu'un test d'annulation doit réellement vérifier, étant donné que l'annulation est coopérative et ne met pas tout à jour à l'instant où cancel() est appelé |

## Référence

- [Glossaire](GLOSSARY.md) : termes de référence pour ce sujet
- [Ressources](RESOURCES.md) : sources fiables
- [Null safety et mutabilité](reference/null-safety-and-mutability.md) : null safety, `val`/`var`, valeurs contre références, prédire la nullabilité et la mutabilité
- [Modélisation](reference/modelling.md) : data classes, sealed classes et `when` exhaustif, déclarations object et companion objects, interfaces avec méthodes par défaut
- [Idiomes](reference/idiom.md) : fonctions d'extension, scope functions (`let`/`run`/`with`/`apply`/`also`), délégation (`by`), surcharge d'opérateurs
- [Collections et séquences](reference/collections-and-sequences.md) : les opérateurs de collection de Kotlin, `Sequence` paresseuse contre collections avides, regroupement et fold
- [Concurrence](reference/concurrency.md) : fonctions suspend et coroutine builders, concurrence structurée, contexte de coroutine et dispatchers, `Flow`, comparaison avec les virtual threads de Java
- [Tests et build](reference/testing-and-build.md) : frameworks de test Kotlin, mocking, le Kotlin DSL de Gradle et la gestion des dépendances
- [Livrer un service](reference/shipping-a-service.md) : structurer un backend typé et testé, idiomes propres à Android, génériques et variance
- [Jugement](reference/judgment.md) : l'interopérabilité avec Java, relire du Kotlin et nommer précisément ce que coûte une construction

## Comment cela fonctionne

Chaque leçon est courte et autonome. Les corrigés sont repliés : rappelez-vous d'abord, puis ouvrez-les. Les exercices en situation réelle comptent plus que la lecture, et les espacer dans le temps est justement le but. Tout ce qui reste flou à la fin d'une leçon mérite d'être suivi jusqu'à sa source primaire avant de passer à la suite.
