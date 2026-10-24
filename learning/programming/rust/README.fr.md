---
title: Rust
description: "Maîtriser Rust : concevoir avec l'ownership au lieu de lutter contre le borrow checker, puis livrer la crate"
type: topic
---

# Apprentissage : Rust

Devenir l'ingénieur à qui l'on confie Rust au sein d'une équipe : capable de concevoir avec l'ownership plutôt que de négocier avec le borrow checker, de façonner les erreurs et les API pour que les types portent les invariants, de ne recourir à `unsafe` que derrière une frontière justifiable, et de livrer une crate dont d'autres dépendent et qu'ils peuvent mettre à jour.

**Commencez ici :** [0001. Ownership et drop](lessons/0001-ownership-and-drop.md)
**Dernière leçon :** [0067. Property-based testing et tests de snapshot](lessons/0067-property-based-and-snapshot-testing.md)

## Objectif

- Prédire quel emprunt le compilateur va rejeter, et pourquoi, avant de compiler.
- Choisir entre posséder, emprunter, compter les références et la mutabilité intérieure en fonction de la durée de vie réelle des données.
- Concevoir un type d'erreur que les appelants peuvent traiter, et dire quand paniquer est au contraire le bon choix.
- Supprimer la duplication avec des traits et des génériques sans rendre les signatures illisibles, et savoir quand le dispatch dynamique est la meilleure réponse.
- Écrire du code async qui ne se bloque pas, et expliquer ce que provoque le fait de garder un verrou à travers un point `await`.
- Justifier chaque bloc `unsafe` par l'invariant qu'il préserve, le garder derrière une interface sûre, et le vérifier avec un outil plutôt qu'à la lecture.
- Publier une crate avec de la documentation, des tests et une API publique que vous pouvez faire évoluer sans casser ceux qui en dépendent.
- Relire du Rust et nommer précisément pourquoi une annotation de lifetime, un `clone` ou un mutex partagé masque un problème de conception.

## Contraintes

- Ne suppose aucune connaissance préalable de Rust ni aucun bagage en programmation système. La pile, le tas et la disposition en mémoire sont enseignés dans le fil conducteur, car l'ownership est impossible à enseigner sans eux.
- Ne nécessite que la toolchain stable et un terminal sur n'importe quel système d'exploitation pris en charge. Rien dans le fil conducteur n'exige d'outillage payant, de compte cloud ni de Rust nightly.
- **On s'attend à ce que les exercices échouent à la compilation.** C'est la boucle de feedback, pas un revers : prédisez ce que le compilateur va dire, puis vérifiez, et considérez la différence comme la leçon.
- Les exercices sont de petits programmes qui tiennent en une séance. Les espacer sur plusieurs jours est le mécanisme, pas un inconvénient.
- Les éditions et les versions comptent ici. Lorsqu'une leçon dépend d'une édition ou d'une fonctionnalité stabilisée, elle indique laquelle, et les affirmations sensibles aux versions sont vérifiées dans les notes de version plutôt que de mémoire.

## Hors périmètre

- Les cibles embarquées et `no_std` en tant que sujets à part entière.
- WebAssembly, les interfaces graphiques et les moteurs de jeu.
- Les frameworks web en tant que sujets. L'async a besoin d'exemples, et ils restent aussi petits que le concept le permet.
- L'écriture de macros procédurales. Les macros déclaratives apparaissent là où il faut lire l'usage qu'en fait la bibliothèque standard elle-même.
- Les interfaces de fonctions étrangères au-delà de ce dont a besoin le contenu sur la frontière `unsafe`. Envelopper une vraie bibliothèque C est une entreprise à part.
- Le fonctionnement interne du compilateur et du borrow checker au-delà du point où il cesse de prédire ce que le compilateur acceptera.

## Le fil conducteur

Huit étapes, de zéro jusqu'au niveau senior. Pas une liste de leçons : une étape comprend plusieurs leçons, et les frontières sont souples.

| Étape | Leçons | Contenu | Terminée quand |
|---|---|---|---|
| 1. Ownership | 0001 à 0006 | Valeurs, pile et tas, moves, `Copy`, les emprunts et leurs règles, slices, `String` face à `&str`, shadowing | Vous savez prédire une erreur de move ou d'emprunt avant que le compilateur ne la signale |
| 2. Données et contrôle | 0007 à 0013 | Structs, enums, `Option` et `Result`, pattern matching et exhaustivité, itérateurs, closures, les collections qui valent d'être connues | Vous modélisez avec des enums, et gérez l'absence sans recourir à `unwrap` |
| 3. Erreurs et forme de l'API | 0014 à 0020 | Propagation avec `?`, types d'erreur personnalisés, conversions `From`, panic face à erreur, modules et visibilité, écrire une documentation qui compile | Vous écrivez une bibliothèque dont un appelant peut réellement traiter les échecs |
| 4. Traits, génériques et lifetimes | 0021 à 0028 | Trait bounds, types associés, génériques face au dispatch dynamique, la règle orpheline, annotations de lifetime et élision, pourquoi une lifetime n'est pas une durée | Vous lisez une erreur de lifetime comme une information plutôt que comme un obstacle |
| 5. Partage et threads | 0029 à 0036 | `Box`, `Rc` et `Arc`, `RefCell` et `Mutex`, `Send` et `Sync`, threads, channels, deadlock et empoisonnement | Vous choisissez une stratégie de partage à partir des données plutôt que par habitude |
| 6. Async | 0037 à 0045 | Futures et executors, tâches et annulation, pourquoi un appel bloquant en async est un bug, les verrous à travers `await`, à quoi sert le pinning | Vous écrivez du code async qui ne se bloque pas, et savez expliquer où il se bloquerait |
| 7. Unsafe et performance | 0046 à 0054 | Ce que promet réellement `unsafe`, le comportement indéfini, encapsuler un invariant, vérifier avec Miri, benchmarking, coûts d'allocation et de copie | Vous savez défendre une frontière `unsafe`, et prouvez une affirmation de performance par une mesure |
| 8. Jugement | 0055 à 0063 | Publication, versionnement sémantique d'une API publique, les API guidelines, relecture, lecture de la bibliothèque standard et des RFC pour trouver des réponses | On vous fait confiance pour trancher et l'expliquer à quelqu'un d'autre ; l'étape 9 complète la première étape de la procédure de release elle-même, la suite de tests passe, avec la suite que ce fil conducteur n'avait pas encore appris à écrire |
| 9. Tests | 0064 à 0067 | `#[test]` et `cargo test`, tests unitaires face aux tests d'intégration, organiser les tests d'une bibliothèque, property-based testing et tests de snapshot | Vous écrivez et organisez une suite de tests comme le fait la bibliothèque standard elle-même, pas seulement des doctests et des benchmarks |

## Leçons

Suivez-les dans l'ordre.

| # | Leçon | Enseigne |
|---|---|---|
| [0001](lessons/0001-ownership-and-drop.md) | Ownership et drop | Chaque valeur a exactement un propriétaire, et le compilateur la libère quand ce propriétaire sort de la portée |
| [0002](lessons/0002-moves-and-copy.md) | Moves et Copy | L'affectation déplace l'ownership sauf si le type est Copy, c'est pourquoi l'ancien nom cesse de fonctionner |
| [0003](lessons/0003-borrowing.md) | Emprunts | Plusieurs emprunts partagés ou un seul emprunt mutable, jamais les deux, et un emprunt se termine à sa dernière utilisation |
| [0004](lessons/0004-slices-string-and-str.md) | Slices, String et str | Une slice est une vue empruntée avec une longueur, et prendre un &str dans une API ne coûte rien aux appelants |
| [0005](lessons/0005-bindings-and-mutability.md) | Liaisons et mutabilité | Immuable par défaut, mut s'applique par liaison, et le shadowing est une nouvelle liaison plutôt qu'une modification |
| [0006](lessons/0006-reading-a-borrow-error.md) | Lire une erreur d'emprunt | Cinq codes d'erreur couvrent l'essentiel de l'étape 1, et chacun a une correction honnête et un contournement |
| [0007](lessons/0007-structs.md) | Les structs et leurs méthodes | Une struct possède ses champs, donc ce que vous y mettez décide de qui doit le maintenir en vie |
| [0008](lessons/0008-enums.md) | Des enums qui portent des données | Une enum dit qu'une valeur a exactement l'une de ces formes, l'outil de modélisation sur lequel repose le reste de l'étape |
| [0009](lessons/0009-option.md) | Option, et la gestion de l'absence | L'absence est une valeur d'un autre type, donc le compilateur vous oblige à dire ce qui se passe quand elle survient |
| [0010](lessons/0010-result.md) | Result, et l'échec comme valeur | Un échec est une valeur de retour plutôt qu'un événement, donc la signature dit ce qui peut mal tourner avant même que vous lisiez le corps |
| [0011](lessons/0011-pattern-matching.md) | Pattern matching | Un match doit couvrir tous les cas, et le pattern décide si vous avez emprunté la valeur ou si vous l'avez déplacée |
| [0012](lessons/0012-iterators-and-closures.md) | Itérateurs et closures | Un itérateur ne fait rien tant que quelque chose ne le consomme pas, et une closure capture exactement ce qu'elle utilise |
| [0013](lessons/0013-collections.md) | Les collections qui valent d'être connues | Vec et HashMap couvrent l'essentiel, et l'API entry est la seule chose qui mérite d'être bien apprise |
| [0014](lessons/0014-propagating-errors.md) | Propager les erreurs | Le point d'interrogation convertit en même temps qu'il retourne, donc le type d'erreur de votre signature décide de ce qu'il acceptera |
| [0015](lessons/0015-designing-an-error-type.md) | Concevoir un type d'erreur | Un appelant ne peut traiter que ce que votre erreur lui permet de distinguer, donc sa forme est une décision d'API |
| [0016](lessons/0016-conversions-and-boundaries.md) | Conversions et frontières | Une implémentation de From est l'endroit où l'échec d'une couche devient celui d'une autre, et un derive écrit celles que vous comprenez déjà |
| [0017](lessons/0017-panic-or-error.md) | Panic ou erreur | Un panic dit que le programme est cassé et une erreur dit que l'entrée l'était, et une bibliothèque a rarement à décider du premier cas |
| [0018](lessons/0018-modules-and-visibility.md) | Modules et visibilité | Ce que vous rendez public est ce que vous avez promis de conserver, donc l'arborescence des modules est une décision d'API avant d'être une décision d'organisation |
| [0019](lessons/0019-documentation-that-compiles.md) | Une documentation qui compile | Un exemple dans un commentaire de documentation est un test, donc la documentation qui pourrit est celle que personne n'a exécutée |
| [0020](lessons/0020-a-library-callers-can-handle.md) | Une bibliothèque qu'un appelant peut maîtriser | Découper la crate, nommer les échecs, et décider de ce que fait le binaire et que la bibliothèque ne doit pas faire |
| [0021](lessons/0021-traits-as-shared-behaviour.md) | Les traits comme comportement partagé | Comment un trait nomme un comportement que plusieurs types peuvent fournir, et pourquoi le trait doit être dans la portée avant que vous puissiez l'utiliser |
| [0022](lessons/0022-trait-bounds-and-generic-functions.md) | Trait bounds et fonctions génériques | Ce qu'un bound promet au corps et exige de l'appelant, et ce que le compilateur en fait |
| [0023](lessons/0023-associated-types.md) | Types associés | Pourquoi Iterator nomme son Item comme type associé plutôt que comme paramètre, et ce que cela décide pour quiconque l'implémente |
| [0024](lessons/0024-generics-or-dyn-trait.md) | Génériques ou dyn Trait | Les deux stratégies de dispatch, ce que chacune coûte, et la question qui tranche réellement entre elles |
| [0025](lessons/0025-implementing-traits-you-do-not-own.md) | Implémenter des traits qui ne vous appartiennent pas | La cohérence, le pattern newtype, et pourquoi une implémentation générale est un engagement plutôt qu'une commodité |
| [0026](lessons/0026-lifetimes-are-not-durations.md) | Les lifetimes ne sont pas des durées | Ce qu'un paramètre de lifetime dit de la relation entre emprunts, et ce que l'élision faisait pour vous depuis le début |
| [0027](lessons/0027-types-that-borrow.md) | Des types qui empruntent | Mettre un paramètre de lifetime sur une struct, et décider si le type devrait plutôt posséder ses données |
| [0028](lessons/0028-reading-a-lifetime-error.md) | Lire une erreur de lifetime | Les formes que prend une erreur de lifetime, chacune avec sa correction honnête et le contournement auquel elle vous incite |
| [0029](lessons/0029-threads-joining-and-panics.md) | Threads, join et panics | Ce que le lancement d'un thread exige réellement des données que vous lui confiez, et ce qui arrive à un thread qui panique seul |
| [0030](lessons/0030-scoped-threads.md) | Scoped threads | Pourquoi un thread qui ne peut pas survivre à sa portée peut emprunter, et pourquoi c'est la première chose à essayer plutôt que la dernière |
| [0031](lessons/0031-shared-ownership.md) | Ownership partagé avec Rc et Arc | Quand une valeur a besoin de plusieurs propriétaires plutôt que d'un seul, ce que coûte le compteur, et comment un cycle provoque une fuite |
| [0032](lessons/0032-interior-mutability.md) | Mutabilité intérieure | Déplacer la règle d'emprunt de la compilation vers l'exécution, ce que cela apporte, et ce que cela coûte quand on se trompe |
| [0033](lessons/0033-mutex-rwlock-and-poisoning.md) | Mutex, RwLock et empoisonnement | Ce qu'un verrou protège réellement, pourquoi la portée du guard est la décision de conception, et ce que laisse derrière lui un panic survenu pendant qu'on le détient |
| [0034](lessons/0034-send-and-sync.md) | Send et Sync | Les deux traits que personne n'écrit et qui décident de ce qui peut franchir la frontière d'un thread, et comment lire les erreurs qu'ils provoquent |
| [0035](lessons/0035-channels.md) | Channels | Envoyer des valeurs entre threads au lieu de les partager, et ce que font les extrémités d'un channel quand l'autre extrémité disparaît |
| [0036](lessons/0036-choosing-a-sharing-strategy.md) | Choisir une stratégie de partage | Les échecs qui découlent d'un choix fait par habitude, et les questions qui choisissent plutôt la stratégie à partir des données |
| [0037](lessons/0037-what-a-future-is.md) | Ce qu'est une future | Une machine à états avec une seule méthode, pilotée par celui qui la poll, et ce que cela signifie pour du code qui paraît séquentiel |
| [0038](lessons/0038-wakers-executors-and-runtimes.md) | Wakers, executors et runtimes | Comment une future signale qu'elle est prête à être pollée de nouveau, et ce que fait un runtime en plus de la poller |
| [0039](lessons/0039-tasks-and-the-send-bound.md) | Les tâches et le bound Send | Ce que le lancement d'une tâche async exige de la future que vous lui confiez, et pourquoi une méthode de trait async ne le satisfera pas |
| [0040](lessons/0040-blocking-is-a-bug.md) | Bloquer est un bug | Pourquoi un seul appel bloquant dans une tâche async fige un travail qui n'a rien à voir avec lui, et que faire des appels que vous ne pouvez pas éviter |
| [0041](lessons/0041-shared-state-across-an-await.md) | L'état partagé à travers un await | Pourquoi un guard de verrou gardé à travers un point await est refusé, et comment choisir entre les deux types de mutex |
| [0042](lessons/0042-cancellation.md) | Annulation | Arrêter une future signifie la dropper, c'est pourquoi personne n'est prévenu et pourquoi le travail s'arrête simplement là où il en était |
| [0043](lessons/0043-cancellation-safety.md) | Cancellation safety | Savoir si une future peut être droppée en cours de route sans perdre ce qu'elle avait déjà pris, et où cette question trouve sa réponse |
| [0044](lessons/0044-pinning.md) | Pinning | Pourquoi la mémoire d'une future doit cesser de bouger une fois qu'elle est pollée, et ce que Pin y fait |
| [0045](lessons/0045-reading-an-async-failure.md) | Lire un échec async | Les cinq façons dont du code async échoue sans message d'erreur, et comment savoir lequel vous avez sous les yeux |
| [0046](lessons/0046-what-unsafe-promises.md) | Ce que promet unsafe | Les cinq choses qu'un bloc unsafe vous permet de faire, et l'obligation que vous contractez en en écrivant un |
| [0047](lessons/0047-raw-pointers.md) | Pointeurs bruts | Ce qu'un pointeur brut n'est pas, ce qu'il vous coûte en garanties, et comment en fabriquer un qui soit réellement valide |
| [0048](lessons/0048-undefined-behaviour.md) | Comportement indéfini | Ce que le compilateur a le droit de supposer, pourquoi un programme qui fonctionne peut quand même être faux, et la liste qui vaut d'être connue par cœur |
| [0049](lessons/0049-checking-with-miri.md) | Vérifier avec Miri | L'outil qui transforme un bug de soundness invisible en rapport, ce qu'il attrape, et ce qu'il ne peut pas attraper |
| [0050](lessons/0050-encapsulating-an-invariant.md) | Encapsuler un invariant | Envelopper du code unsafe dans une interface sûre, et ce qui doit être vrai pour que cette interface mérite son nom |
| [0051](lessons/0051-memory-orderings.md) | Memory orderings | Ce que contraint réellement un ordering, pourquoi on ne peut pas le tester en l'exécutant, et comment vérifier celui que vous avez choisi |
| [0052](lessons/0052-measuring-before-optimising.md) | Mesurer avant d'optimiser | Comment obtenir un chiffre défendable, ce que le compilateur fait d'un benchmark qui ne mesure rien, et ce qu'une mesure ne peut pas vous dire |
| [0053](lessons/0053-allocation-and-copying-costs.md) | Coûts d'allocation et de copie | Où un programme Rust passe réellement son temps, et lesquelles des corrections évidentes sont rentables |
| [0054](lessons/0054-defending-an-unsafe-boundary.md) | Défendre une frontière unsafe | L'argument que vous devez pouvoir avancer avant qu'un bloc unsafe soit livré, et la mesure qui doit l'accompagner |
| [0055](lessons/0055-variance.md) | Variance | Quelles lifetimes peuvent se substituer à quelles autres, pourquoi c'est votre propre type qui décide, et ce à quoi cela vous engage |
| [0056](lessons/0056-higher-ranked-bounds.md) | Higher-ranked bounds | Écrire le quantificateur que le compilateur vous affiche depuis le début, et les formes d'API qui en ont besoin |
| [0057](lessons/0057-what-breaks-a-caller.md) | Ce qui casse un appelant | Les modifications qui exigent une version majeure, celles qui n'ont que l'air sûres, et l'outil qui vous dit lesquelles sont lesquelles |
| [0058](lessons/0058-designing-for-change.md) | Concevoir pour le changement | Les décisions qui vous laissent de la marge plus tard, et celles qui promettent discrètement plus que vous ne le vouliez |
| [0059](lessons/0059-features-and-the-minimum-version.md) | Les features et la version minimale | Pourquoi une feature ne doit qu'ajouter, ce que l'unification fait à vos hypothèses, et ce que promet réellement la déclaration d'une version minimale |
| [0060](lessons/0060-workspaces-and-release.md) | Workspaces et release | Amener une crate au point où la publication tient en une commande, et ce que fait réellement cette commande |
| [0061](lessons/0061-the-api-guidelines.md) | Les API guidelines | La liste de contrôle sur laquelle l'écosystème s'est déjà accordé, quels éléments comptent le plus, et comment l'utiliser sans l'appliquer aveuglément |
| [0062](lessons/0062-reading-the-source-and-the-rfcs.md) | Lire le code source et les RFC | Répondre à une question que la documentation ne traite pas, à partir de la bibliothèque standard, des tracking issues et des RFC |
| [0063](lessons/0063-reviewing-rust.md) | Relire du Rust | Quoi chercher dans le Rust de quelqu'un d'autre, dans quel ordre, et quels commentaires valent la peine d'être faits |
| [0064](lessons/0064-the-test-attribute-and-cargo-test.md) | L'attribut test et cargo test | Un doctest vit dans un commentaire de documentation et exécute un exemple ; une fonction #[test] vit dans le code source même de la crate et constitue la forme ordinaire de presque tous les tests Rust, et cargo test exécute les deux avec la même commande sans qu'il s'agisse du même mécanisme |
| [0065](lessons/0065-unit-versus-integration-tests.md) | Tests unitaires face aux tests d'intégration | L'endroit où vit une fonction #[test] décide de ce qu'elle peut voir : le même fichier que le code sous #[cfg(test)], avec accès à chaque élément privé, ou un répertoire tests/ séparé qui ne voit jamais que ce que vous avez réellement rendu public |
| [0066](lessons/0066-organising-tests-for-a-library.md) | Organiser les tests d'une bibliothèque | La forme d'une suite d'intégration est imposée par ce que vous avez déjà rendu pub, la mise en place partagée va précisément dans tests/common/mod.rs, et un binaire sans lib.rs ne peut pas du tout être testé en intégration |
| [0067](lessons/0067-property-based-and-snapshot-testing.md) | Property-based testing et tests de snapshot | Voici la synthèse de l'étape 9 : proptest génère des centaines d'entrées et réduit un échec à la plus petite entrée qui casse encore la propriété, tandis qu'un test de snapshot compare la sortie d'une entrée choisie à une référence qu'un humain a déjà relue |

## Référence

- [Glossaire](GLOSSARY.md) : termes de référence pour ce sujet
- [Ressources](RESOURCES.md) : sources fiables, chacune annotée avec ce qu'elle couvre
- [Ownership et emprunts](reference/ownership-and-borrowing.md) : les règles, la liste Copy, les codes d'erreur, et la correction honnête pour chacun
- [Le projet](reference/the-project.md) : la crate que construisent les exercices tout au long du fil conducteur, et l'état dans lequel elle doit se trouver à la fin de chaque étape
- [Données et contrôle](reference/data-and-control.md) : la fiche de l'étape 2, avec les décisions sur les enums, Option et Result, les règles des patterns, et les collections
- [Erreurs et forme de l'API](reference/errors-and-api-shape.md) : la fiche de l'étape 3, avec les décisions sur les types d'erreur, les règles de conversion, et ce à quoi engage une API publique
- [Traits et lifetimes](reference/traits-and-lifetimes.md) : la fiche de l'étape 4, avec la décision de dispatch, les règles de cohérence, et la table des erreurs de lifetime
- [Partage et threads](reference/sharing-and-threads.md) : la fiche de l'étape 5, avec la procédure de choix de stratégie, ce que coûte chaque type de partage, et la table des échecs
- [Async](reference/async.md) : la fiche de l'étape 6, avec le modèle de poll, les bounds, la table des échecs, et où la cancel safety est documentée
- [Unsafe et performance](reference/unsafe-and-performance.md) : la fiche de l'étape 7, avec la table du comportement indéfini, ce que chaque outil attrape, et la discipline de mesure
- [Jugement](reference/judgment.md) : la fiche de l'étape 8, avec les règles de variance, la table des changements cassants, la liste de contrôle de release, et l'ordre d'autorité

## Comment cela fonctionne

Chaque leçon est courte et autonome. Les corrigés sont repliés : rappelez-vous d'abord, puis ouvrez-les. Les exercices en situation réelle comptent plus que la lecture, et les espacer dans le temps est justement le but. Tout ce qui reste flou à la fin d'une leçon mérite d'être suivi jusqu'à sa source primaire avant de passer à la suite.
