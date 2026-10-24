---
title: Go
description: "Maîtriser Go au sein d'une équipe : concevoir, livrer et exploiter un service de production"
type: topic
---

# Apprentissage : Go

Devenir l'ingénieur à qui l'on confie Go au sein d'une équipe : capable de concevoir, livrer et exploiter un service Go de production, de relire le Go de quelqu'un d'autre et de nommer concrètement pourquoi une conception est mauvaise, et de reconnaître quand une conception importée d'un autre langage lutte contre Go au lieu de s'en servir.

**Dernière leçon :** [0041. Tester contre une vraie base de données](lessons/0041-testing-against-a-real-database.md)

## Objectif

- Concevoir et livrer un service de production : configuration, logging structuré, arrêt propre, health checks, accès à la base de données.
- Déboguer une data race et une fuite de goroutine dans du code que vous n'avez pas écrit, à l'aide de `-race` et de `pprof`.
- Relire la PR d'un collègue et dire précisément pourquoi une interface, un receiver pointeur ou un channel n'est pas le bon outil à cet endroit.
- Prédire ce que fait un programme concurrent avant de l'exécuter, à partir de l'ordonnanceur et du modèle mémoire plutôt que par l'expérience.
- Réduire les allocations avec des preuves issues de `pprof` et de `benchstat`, pas au jugé.
- Concevoir une API de package que vous pouvez garder rétrocompatible, et savoir quand *ne pas* recourir à une goroutine.

## Contraintes

- Ne suppose aucune connaissance préalable de Go. Une expérience dans un autre langage raccourcit les premières étapes sans être requise, et elle apporte des habitudes que Go punira en silence, car un mauvais réflexe compile quand même ici.
- Ne nécessite que la toolchain standard sur n'importe quel système d'exploitation pris en charge. Jusqu'à l'étape 5 incluse, rien n'exige d'outillage payant, de compte cloud ni de seconde machine.
- Les exercices sont de petits programmes qui tiennent en une séance. Les espacer sur plusieurs jours est le mécanisme, pas un inconvénient.
- Les contenus sensibles aux versions vieillissent vite. Les affirmations sur la version actuelle sont vérifiées dans les notes de version plutôt que dans des livres.

## Hors périmètre

- Les autres langages en tant que sujets à part entière. Les comparaisons n'apparaissent que là où elles empêchent une habitude d'être transportée dans Go.
- Les frameworks tiers en tant que sujets à part entière : routeurs, ORM, conteneurs d'injection de dépendances, boîtes à outils CLI. La bibliothèque standard couvre directement le routage, le logging structuré et l'accès à la base de données, donc les leçons s'appuient sur elle ; lorsqu'une équipe a déjà choisi un framework, juger s'il mérite sa place est une compétence de relecture qui relève de l'étape 6.
- Le frontend, WASM et les cibles mobiles.
- Kubernetes et l'infrastructure au-delà de ce dont un service Go a besoin pour tourner. Placer le binaire dans une image de conteneur, puis exécuter, sécuriser et déboguer ce conteneur, relève de [`infrastructure/containers`](../../infrastructure/containers/). Le faire tourner sur un cluster, y compris ce que le cluster fait de ses health checks et de son signal d'arrêt, relève de [`infrastructure/kubernetes`](../../infrastructure/kubernetes/).
- Le fonctionnement interne du compilateur et du runtime au-delà du point où il cesse de prédire le comportement des programmes.

## Le fil conducteur

Sept étapes, de zéro jusqu'au niveau senior. Pas une liste de leçons : une étape comprend plusieurs leçons, et les frontières sont souples.

| Étape | Leçons | Contenu | Terminée quand |
|---|---|---|---|
| 1. Fondations | 0001 à 0007 | Types, valeurs zéro, sémantique de valeur contre sémantique de pointeur, mécanique des slices et des maps y compris l'aliasing, strings contre runes contre bytes, bases des packages | Vous savez prédire l'aliasing et le comportement de copie sans exécuter le code |
| 2. Idiomes | 0008 à 0014 | Les erreurs comme valeurs, l'enveloppement avec `%w`, `errors.Is`/`As`, la satisfaction implicite des interfaces, les petites interfaces, l'embedding de structs, l'organisation et le nommage des packages | Vous écrivez du Go qu'un relecteur ne qualifierait pas de « Java en syntaxe Go » |
| 3. Concurrence | 0015 à 0021 | Goroutines, channels, `select`, primitives `sync`, annulation par `context`, `errgroup`, le race detector, le modèle mémoire, les schémas de fuite | Vous savez trouver une fuite et une race dans du code inconnu et expliquer la garantie qui a été violée |
| 4. Production | 0022 à 0027 | Services HTTP, configuration, `slog`, arrêt propre, health checks, accès à la base de données, génériques là où ils se justifient | Vous avez structuré un service qui survit à l'exploitation ; l'étape 7 le complète avec des métriques, du tracing, et des tests autour des handlers et de la base de données, pas seulement autour des fonctions |
| 5. Performance et outillage | 0028 à 0033 | Tests pilotés par table, fuzzing, benchmarks, `pprof`, escape analysis, réduction des allocations, modules et versionnement, builds de release | Vous optimisez à partir d'un profil et prouvez le gain avec `benchstat` |
| 6. Jugement | 0034 à 0037 | Conception d'API et compatibilité, quand *ne pas* utiliser de goroutine, relecture, lecture du code source de la stdlib pour trouver des réponses | On vous fait confiance pour trancher et l'expliquer à quelqu'un d'autre |
| 7. Observabilité et tests en production | 0038 à 0041 | Middleware et valeurs propres à la requête, métriques et tracing (RED/USE, OpenTelemetry), tester un handler HTTP, tests d'intégration contre une vraie base de données | Vous livrez un service avec le troisième et le quatrième signal auxquels l'étape 4 s'était arrêtée : métriques, tracing, et tests autour des handlers et de la base de données, pas seulement autour des fonctions |

## Leçons

Suivez-les dans l'ordre.

| # | Leçon | Enseigne |
|---|---|---|
| [0001](lessons/0001-values-and-the-zero-value.md) | Les valeurs et la valeur zéro | Toute variable déclarée est déjà utilisable, et nil est une valeur plutôt qu'une absence |
| [0002](lessons/0002-value-semantics-and-pointers.md) | Sémantique de valeur et pointeurs | Chaque affectation et chaque argument est une copie, et un pointeur est le moyen d'y échapper |
| [0003](lessons/0003-slices-and-the-backing-array.md) | Les slices et le tableau sous-jacent | Une slice est un en-tête de trois mots sur un tableau que quelqu'un d'autre détient peut-être aussi |
| [0004](lessons/0004-maps-and-their-rules.md) | Les maps et leurs règles | Le comma-ok, les éléments non adressables, l'itération aléatoire, et l'erreur fatale que lève une map partagée |
| [0005](lessons/0005-strings-bytes-and-runes.md) | Strings, bytes et runes | Une string est une suite immuable d'octets UTF-8, donc len n'est pas un nombre de caractères et l'indexation ne renvoie pas un caractère |
| [0006](lessons/0006-methods-and-method-sets.md) | Méthodes et method sets | Le receiver que vous choisissez décide quels types satisfont une interface, et pas seulement qui peut modifier |
| [0007](lessons/0007-packages-and-modules.md) | Packages et modules | Un répertoire est un package, une majuscule constitue tout le système de visibilité, et internal est appliqué |
| [0008](lessons/0008-errors-are-values.md) | Les erreurs sont des valeurs | error est une interface ordinaire, donc les échecs sont des données que vous traitez plutôt qu'un flux de contrôle qui s'échappe |
| [0009](lessons/0009-wrapping-is-and-as.md) | Enveloppement, Is et As | %w construit une chaîne, Is et As la parcourent, et envelopper est un engagement d'API |
| [0010](lessons/0010-defer-panic-and-recover.md) | defer, panic et recover | Les arguments sont figés à l'instruction defer, et panic sert aux bugs plutôt qu'aux échecs |
| [0011](lessons/0011-implicit-interfaces.md) | Les interfaces sont satisfaites implicitement | Le consommateur déclare l'interface, l'implémentation ne la mentionne jamais, et la petitesse est tout l'intérêt |
| [0012](lessons/0012-the-nil-interface-trap.md) | Le piège de l'interface nil | Une interface contient un type et une valeur, donc un pointeur nil à l'intérieur n'est pas une interface nil |
| [0013](lessons/0013-embedding-is-not-inheritance.md) | L'embedding n'est pas l'héritage | La promotion ressemble à de l'héritage jusqu'à ce qu'une méthode embarquée refuse d'appeler votre redéfinition |
| [0014](lessons/0014-designing-a-package.md) | Concevoir un package | Commentaires de documentation, petite surface exportée, et une flèche de dépendance qui pointe dans un seul sens |
| [0015](lessons/0015-goroutines-and-what-they-cost.md) | Les goroutines et ce qu'elles coûtent | Assez bon marché pour en lancer des milliers, jamais assez gratuites pour en lancer une sans plan pour l'arrêter |
| [0016](lessons/0016-channels.md) | Channels | Sans buffer signifie rendez-vous, fermer est une diffusion, et seul l'émetteur peut fermer |
| [0017](lessons/0017-select-and-timeouts.md) | select et timeouts | Attendre sur plusieurs channels à la fois, choisir au hasard parmi ceux qui sont prêts, et désactiver un cas avec nil |
| [0018](lessons/0018-context-cancellation.md) | context et annulation | Une seule valeur qui transporte une échéance et un signal d'arrêt à travers chaque appel qu'elle touche |
| [0019](lessons/0019-sync-primitives.md) | sync et errgroup | Quand partager la mémoire vaut mieux que la transmettre, et les quatre primitives qui couvrent presque tout |
| [0020](lessons/0020-memory-model-and-races.md) | Le modèle mémoire et les races | Une data race est un comportement indéfini, pas un pile ou face, et le détecteur ne voit que ce qui s'exécute |
| [0021](lessons/0021-goroutine-leaks.md) | Fuites de goroutines | Une goroutine bloquée pour toujours n'est jamais collectée, pas plus que ce qu'elle détient |
| [0022](lessons/0022-an-http-server.md) | Un serveur HTTP digne d'être exploité | Les handlers, les patterns de routage et les quatre timeouts que le serveur par défaut ne fixe pas |
| [0023](lessons/0023-configuration-and-startup.md) | Configuration et démarrage | Un main qui ne fait que câbler, une fonction run qui renvoie une erreur, et une validation avant la première requête |
| [0024](lessons/0024-structured-logging-with-slog.md) | Logging structuré avec slog | Des attributs clé-valeur, un logger unique passé comme dépendance, et des niveaux que vous pouvez changer sans déploiement |
| [0025](lessons/0025-graceful-shutdown.md) | Arrêt propre et santé | Capter le signal, cesser d'accepter, vider le travail en cours, puis fermer les dépendances dans l'ordre |
| [0026](lessons/0026-talking-to-a-database.md) | Dialoguer avec une base de données | sql.DB est un pool, chaque appel prend un context, et un Rows non fermé retient une connexion |
| [0027](lessons/0027-generics-that-earn-their-keep.md) | Des génériques qui se justifient | Les paramètres de type suppriment la duplication entre types, et une interface reste la bonne réponse pour le comportement |
| [0028](lessons/0028-table-driven-tests.md) | Tests pilotés par table | Une seule fonction de test, une slice de cas, des sous-tests qui se nomment eux-mêmes et échouent indépendamment |
| [0029](lessons/0029-fuzzing.md) | Fuzzing | Énoncer une propriété qui doit toujours tenir, puis laisser la toolchain chercher l'entrée qui la casse |
| [0030](lessons/0030-benchmarks-you-can-trust.md) | Des benchmarks dignes de confiance | b.Loop, les exécutions répétées et benchstat, car un seul chiffre issu d'une seule exécution n'est pas une mesure |
| [0031](lessons/0031-reading-a-pprof-profile.md) | Lire un profil pprof | Trouver où partent réellement le temps et la mémoire, avant de modifier la moindre ligne |
| [0032](lessons/0032-escape-analysis-and-allocation.md) | Escape analysis et allocation | Pourquoi une valeur atterrit sur le tas, comment le demander au compilateur, et quelles corrections rapportent vraiment |
| [0033](lessons/0033-modules-and-release-builds.md) | Modules et builds de release | La sélection de version minimale, la règle du chemin v2, et les options qui rendent un binaire reproductible |
| [0034](lessons/0034-api-design-and-compatibility.md) | Conception d'API et compatibilité | Ce que vous pouvez ajouter sans casser les appelants, et les trois modifications qui les cassent toujours |
| [0035](lessons/0035-when-not-to-use-a-goroutine.md) | Quand ne pas utiliser de goroutine | La concurrence est une structure, pas une accélération, et la version séquentielle est souvent la bonne réponse |
| [0036](lessons/0036-reviewing-go.md) | Relire du Go | Laisser les outils trouver les problèmes de style, et consacrer votre attention au cycle de vie, aux frontières et à ce que le compilateur ne peut pas vérifier |
| [0037](lessons/0037-reading-the-standard-library.md) | Lire la bibliothèque standard | Le code source est sur votre machine, il tranche des débats que la documentation ne peut pas trancher, et c'est la référence de style |
| [0038](lessons/0038-middleware-and-request-scoped-values.md) | Middleware et valeurs propres à la requête | La leçon 22 a montré un middleware qui écrit une valeur dans le context ; cette leçon en est l'autre moitié, la relire en toute sûreté, ainsi que le mécanisme dont cet exemple n'a jamais eu besoin : un middleware qui décide de ne pas appeler du tout le handler suivant |
| [0039](lessons/0039-metrics-and-tracing.md) | Métriques et tracing | pprof profile localement le CPU et la mémoire d'un seul processus ; les métriques et le tracing sont les deux signaux de production qui répondent à une autre paire de questions : comment se porte le service en ce moment dans son ensemble, et ce qui est arrivé à cette requête précise à travers chaque service qu'elle a touché |
| [0040](lessons/0040-testing-an-http-handler.md) | Tester un handler HTTP | La leçon 22 mentionnait en passant qu'un ResponseRecorder rend un handler testable sans réseau ; cette leçon rend cette affirmation concrète, explique pourquoi c'est la jointure d'interface qui le permet, et présente l'outil différent, et facile à confondre, pour tester un client plutôt qu'un handler |
| [0041](lessons/0041-testing-against-a-real-database.md) | Tester contre une vraie base de données | Voici la synthèse de l'étape 7 : testing.Short() écarte un test lent de base de données de la boucle locale rapide, une transaction ouverte et jamais validée donne à chaque test une ardoise propre et isolée, et un test d'intégration fait enfin travailler ensemble un middleware, un handler et une vraie base de données |

## Référence

- [Glossaire](GLOSSARY.md) : termes de référence pour ce sujet
- [Ressources](RESOURCES.md) : sources fiables, chacune annotée avec ce qu'elle couvre
- [Slices et maps](reference/slice-and-map-mechanics.md) : aliasing, capacité, et les opérations qui provoquent un panic
- [Gestion des erreurs](reference/error-handling.md) : verbes d'enveloppement, fonctions de correspondance, et les pièges qui compilent
- [Schémas de concurrence](reference/concurrency-patterns.md) : règles des channels, constructeurs de context, liste de contrôle des fuites
- [Commandes de la toolchain](reference/toolchain-commands.md) : options de test, de benchmark, de profilage et de build de release
- [Liste de contrôle de relecture](reference/review-checklist.md) : ce que les outils attrapent et ce que vous devez attraper

## Comment cela fonctionne

Chaque leçon est courte et autonome. Les corrigés sont repliés : rappelez-vous d'abord, puis ouvrez-les. Les exercices en situation réelle comptent plus que la lecture, et les espacer dans le temps est justement le but. Tout ce qui reste flou à la fin d'une leçon mérite d'être suivi jusqu'à sa source primaire avant de passer à la suite.
