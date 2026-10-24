---
title: Java
description: "Maîtriser un service Java : le modéliser en Java moderne, puis exploiter ce qu'en fait la JVM"
type: topic
---

# Apprentissage : Java

Devenir l'ingénieur à qui l'on confie un service Java au sein d'une équipe : capable de modéliser un domaine en Java moderne plutôt qu'avec les hiérarchies d'héritage qu'exigeait autrefois le langage, de raisonner sur la concurrence à partir du modèle mémoire plutôt que par l'expérience, de lire un profil et un log de garbage collection jusqu'à une décision, et de relire le Java de quelqu'un en nommant concrètement ce que lui coûte une abstraction.

**Commencez ici :** [0001. Les références sont des valeurs](lessons/0001-references-are-values.md)
**Dernière leçon :** [0052. Réflexion et annotations](lessons/0052-reflection-and-annotations.md)

## Objectif

- Prédire ce que font l'égalité de référence, un `hashCode` cassé et un champ mutable partagé, avant d'exécuter le code.
- Modéliser un domaine avec des records, des sealed interfaces et des enums, et dire pourquoi une hiérarchie d'héritage aurait été pire.
- Énoncer ce que garantissent respectivement `synchronized`, `volatile` et une collection concurrente, dans le vocabulaire du modèle mémoire de Java.
- Utiliser les virtual threads là où ils rapportent, et nommer ce qui bloque encore un carrier thread.
- Lire un log de garbage collection et un profil, puis dimensionner un tas à partir de ces éléments plutôt que d'une valeur par défaut.
- Livrer un build que quelqu'un d'autre peut exécuter : dépendances déclarées, suite de tests, artefact exécutable.
- Relire une pull request et dire précisément pourquoi une hiérarchie de classes, une checked exception ou une chaîne de streams n'est pas le bon outil à cet endroit.
- Trancher un débat sur le langage à partir de la spécification et de la JEP qui a introduit la fonctionnalité.

## Contraintes

- Ne suppose aucune connaissance préalable de Java. Une expérience dans un autre langage raccourcit les premières étapes sans être requise, et elle apporte des habitudes que Java punit en silence : un getter pour chaque champ, une interface avec une seule implémentation, une classe là où un record le dirait mieux.
- La référence est la version actuelle à support long terme. Chaque fonctionnalité du langage est présentée avec la version qui l'a introduite, car le code Java se lit à travers de nombreuses versions et le « Java moderne » vieillit.
- Ne nécessite qu'un JDK et un terminal sur n'importe quel système d'exploitation pris en charge. Un IDE aide sans jamais être requis, et rien dans le fil conducteur n'exige d'outillage payant ni de compte cloud.
- La plupart des exercices sont de petits programmes qui tiennent en une séance. L'étape 6 fait exception : un profil a besoin d'un programme qui tourne assez longtemps pour être profilé.
- Les affirmations sensibles aux versions sont vérifiées dans la spécification, la documentation de l'API et l'index des JEP plutôt que dans un livre, car le rythme de publication semestriel dépasse tous les livres listés.

## Hors périmètre

- Les frameworks en tant que sujets à part entière : Spring, Jakarta EE, Quarkus, Hibernate. Juger si un framework mérite sa place est une compétence de relecture qui relève de l'étape 7.
- Les autres langages de la JVM : Kotlin, Scala, Clojure, Groovy.
- Android, et les cibles mobiles en général.
- La comparaison des outils de build. Le fil conducteur enseigne les tâches qu'un build doit accomplir et utilise un seul outil pour les réaliser, au lieu de débattre duquel choisir.
- Le fonctionnement interne de la JVM au-delà du point où il cesse de prédire le comportement des programmes : implémentation du JIT, ingénierie du bytecode, écriture d'un garbage collector.
- Kubernetes et l'infrastructure au-delà de ce dont un service a besoin pour tourner. Placer l'artefact exécutable dans une image de conteneur, puis exécuter, sécuriser et déboguer ce conteneur, relève de [`infrastructure/containers`](../../infrastructure/containers/). Le faire tourner sur un cluster relève de [`infrastructure/kubernetes`](../../infrastructure/kubernetes/).

## Le fil conducteur

Sept étapes, de zéro jusqu'au niveau senior. Pas une liste de leçons : une étape comprend plusieurs leçons, et les frontières sont souples.

| Étape | Leçons | Contenu | Terminée quand |
|---|---|---|---|
| 1. Fondations | 0001 à 0006 | Types primitifs et références, `null`, les strings et leur pool, les tableaux, le collections framework, `equals` et `hashCode`, `Comparable` | Vous savez prédire l'identité face à l'égalité, et l'aliasing, sans exécuter le code |
| 2. Modélisation | 0007 à 0014 | Classes et interfaces, records, sealed types, enums, génériques et effacement de type, pattern matching, l'immuabilité par défaut | Vous modélisez un domaine sans recourir d'abord à l'héritage |
| 3. Idiomes et bibliothèque | 0015 à 0021 | Les exceptions et que faire des checked, `Optional`, streams et collectors, itération, fichiers et IO, l'API de dates et heures, text blocks | Vous écrivez du Java qu'un relecteur ne qualifierait pas de non idiomatique |
| 4. Concurrence | 0022 à 0028 | Threads, le modèle mémoire, `synchronized` et `volatile`, `java.util.concurrent`, executors, virtual threads, concurrence structurée, les pièges | Vous savez nommer la garantie qu'un programme concurrent défaillant a violée |
| 5. Tests et build | 0029 à 0035 | JUnit 6, tests paramétrés, doublures de test et quand ne pas en utiliser, déclaration des dépendances, un artefact exécutable reproductible | Quelqu'un d'autre peut le cloner, le construire, le tester et l'exécuter |
| 6. Le runtime | 0036 à 0042 | Zones mémoire, disposition des objets et escape analysis, garbage collectors et leurs compromis, lecture d'un log de GC, JMH, profilage, réduction des allocations | Vous optimisez à partir d'un profil et prouvez le gain avec un benchmark digne de confiance |
| 7. Jugement | 0043 à 0049 | Conception d'API et rétrocompatibilité, dépréciation, relecture, lecture de la spécification et des JEP pour trouver des réponses | On vous fait confiance pour trancher et l'expliquer à quelqu'un d'autre ; l'étape 8 complète cela avec le mécanisme dont chaque framework jugé est réellement construit, la réflexion et les annotations |
| 8. Modules et réflexion | 0050 à 0052 | Le système de modules, `module-info.java`, `requires` et `exports`, l'encapsulation forte, les images de runtime `jlink` et `jpackage`, la réflexion et les annotations | Vous déclarez délibérément une frontière de module, livrez une image de runtime construite à partir d'elle, et lisez ce que touche réellement la réflexion d'un framework avant de juger s'il mérite sa place |

## Leçons

Suivez-les dans l'ordre.

| # | Leçon | Enseigne |
|---|---|---|
| [0001](lessons/0001-references-are-values.md) | Les références sont des valeurs | Une variable contient un primitif ou une référence, et chaque affectation et chaque argument copie ce contenu |
| [0002](lessons/0002-identity-and-equality.md) | Identité et égalité | == compare des références, il répond donc à une autre question pour les strings et les nombres boxés |
| [0003](lessons/0003-equals-and-hashcode.md) | Le contrat equals et hashCode | Rompez le contrat et une collection à hachage perd votre objet sans rien signaler |
| [0004](lessons/0004-null.md) | null et d'où il vient | null est une référence qui ne désigne rien, et la correction consiste à le rejeter à la frontière |
| [0005](lessons/0005-arrays-and-collections.md) | Tableaux et collections | Les tableaux sont covariants et de taille fixe, et trois factories de listes diffèrent d'une façon que leurs noms cachent |
| [0006](lessons/0006-comparable-and-comparator.md) | Comparable et Comparator | Une collection triée utilise l'ordre plutôt qu'equals, donc un comparator incohérent perd des données |
| [0007](lessons/0007-classes-and-objects.md) | Classes et objets | Une classe est un modèle d'état et de comportement, et chaque champ démarre à une valeur par défaut que vous n'avez pas écrite |
| [0008](lessons/0008-records.md) | Records | Un conteneur transparent pour des données immuables, dont le constructeur, les accesseurs, equals, hashCode et toString sont dérivés de l'en-tête |
| [0009](lessons/0009-interfaces.md) | Interfaces | Un contrat sans état, plus les méthodes par défaut qui lui permettent de grandir sans casser chaque implémentation |
| [0010](lessons/0010-inheritance-and-composition.md) | Héritage et composition | Ce que extends vous donne réellement, et pourquoi la réponse est généralement un champ plutôt qu'une superclasse |
| [0011](lessons/0011-sealed-types-and-pattern-matching.md) | Sealed types et pattern matching | Un ensemble fermé d'alternatives, et un compilateur qui vérifie que vous les avez toutes traitées |
| [0012](lessons/0012-enums.md) | Enums | Un ensemble fixe d'instances garanti par le langage, avec de la place pour un état et un comportement sur chacune |
| [0013](lessons/0013-generics-and-erasure.md) | Génériques et effacement de type | Des paramètres de type que le compilateur vérifie et que le runtime oublie, et les wildcards qui les rendent utilisables |
| [0014](lessons/0014-immutability-as-a-default.md) | L'immuabilité par défaut | Rendez l'objet impossible à modifier et la plupart des questions difficiles cessent de se poser |
| [0015](lessons/0015-exceptions.md) | Exceptions | Quels échecs ont leur place dans une signature, lesquels dans une stack trace, et un nettoyage qui survit aux deux |
| [0016](lessons/0016-optional.md) | Optional | Un type de retour qui fait de l'absence une partie du contrat, et les quatre endroits où il n'a pas sa place |
| [0017](lessons/0017-streams.md) | Streams | Un pipeline qui décrit un travail, n'en fait rien tant qu'on ne le lui demande pas, et ne peut être sollicité qu'une fois |
| [0018](lessons/0018-collectors.md) | Collectors | Retransformer un pipeline en conteneur, et les trois collectors qui lèvent une exception là où vous ne l'attendez pas |
| [0019](lessons/0019-files-and-paths.md) | Fichiers et chemins | Des chemins qui ne sont pas des strings, des flux qui doivent être fermés, et un charset qui est enfin une valeur par défaut digne de ce nom |
| [0020](lessons/0020-dates-and-times.md) | Dates et heures | Lequel des six types temporels vous vouliez réellement dire, et les trois qui ne sont pas un point dans le temps |
| [0021](lessons/0021-strings-and-text.md) | Strings et texte | Les text blocks, le formatage à utiliser, et pourquoi la longueur n'est pas le nombre de caractères |
| [0022](lessons/0022-threads.md) | Threads | Un thread est une pile d'appels ordonnancée, et presque toutes les erreurs de cette étape commencent par le traiter comme gratuit |
| [0023](lessons/0023-the-memory-model.md) | Le modèle mémoire | Pourquoi une valeur écrite par un thread peut ne jamais être vue par un autre, et la règle exacte qui corrige cela |
| [0024](lessons/0024-mutual-exclusion.md) | Exclusion mutuelle | Un seul thread à la fois, les deux façons de l'exprimer, et le deadlock que vous pouvez trouver avant qu'il ne se produise |
| [0025](lessons/0025-concurrent-collections-and-atomics.md) | Collections concurrentes et atomiques | Les collections qui survivent aux accès concurrents, et le vérifier-puis-agir qui les met toutes en échec |
| [0026](lessons/0026-executors-and-futures.md) | Executors et futures | Soumettre du travail au lieu de créer des threads, et retrouver l'exception que submit a avalée |
| [0027](lessons/0027-virtual-threads.md) | Virtual threads | Des threads assez bon marché pour bloquer, et l'habitude du pooling qu'il faut maintenant désapprendre |
| [0028](lessons/0028-choosing-a-model.md) | Choisir un modèle | Une seule question choisit le modèle, et la défaillance que vous avez sous les yeux nomme la garantie qu'elle a rompue |
| [0029](lessons/0029-your-first-test.md) | Votre premier test | Où vivent les tests, ce que fait réellement le runner, et le schéma de versions que tous les articles décrivent mal |
| [0030](lessons/0030-assertions-that-name-the-failure.md) | Des assertions qui nomment l'échec | Un test en échec est un rapport de bug, et l'assertion que vous avez choisie décide de la qualité de ce rapport |
| [0031](lessons/0031-parameterised-tests.md) | Tests paramétrés | Une seule méthode de test, de nombreux cas, et la limite au-delà de laquelle une boucle dans un test ne suffit plus |
| [0032](lessons/0032-test-doubles.md) | Doublures de test | Cinq types de substituts, quand un vrai objet les bat tous, et ce qu'un mock cesse discrètement de tester |
| [0033](lessons/0033-declaring-dependencies.md) | Déclarer les dépendances | Coordonnées, scopes et graphe transitif, plus la version qui arrive sans avoir été demandée |
| [0034](lessons/0034-the-build-lifecycle.md) | Le cycle de vie du build | Des phases et des goals plutôt que des commandes apprises par cœur, et le wrapper qui rend le build identique partout |
| [0035](lessons/0035-a-runnable-artifact.md) | Un artefact exécutable | Empaqueter ce que vous avez construit pour que quelqu'un qui n'a rien d'autre qu'un JDK puisse l'exécuter |
| [0036](lessons/0036-where-memory-goes.md) | Où va la mémoire | Les cinq endroits où la JVM place la mémoire, et quelle OutOfMemoryError désigne lequel |
| [0037](lessons/0037-the-shape-of-an-object.md) | La forme d'un objet | Un petit objet est surtout un en-tête, et l'option qui le réduit est désactivée par défaut |
| [0038](lessons/0038-the-allocation-that-never-happened.md) | L'allocation qui n'a jamais eu lieu | L'escape analysis peut supprimer entièrement une allocation, et une seule écriture dans un champ la fait revenir |
| [0039](lessons/0039-collectors-and-the-trade.md) | Les collectors et le compromis que vous faites | Cinq collectors, un compromis à trois voies, et pourquoi la valeur par défaut est généralement la bonne réponse |
| [0040](lessons/0040-reading-a-gc-log.md) | Lire un log de garbage collection | Une seule ligne de log dit combien a été collecté, combien de temps cela a pris, et s'il faut s'en soucier |
| [0041](lessons/0041-a-benchmark-you-can-trust.md) | Un benchmark digne de confiance | Pourquoi la boucle de chronométrage évidente ment, et la configuration du harness qui ne mesure discrètement rien |
| [0042](lessons/0042-from-profile-to-proof.md) | Du profil à la preuve | Enregistrer l'exécution, lire où est passé le temps, changer une seule chose, et prouver le gain |
| [0043](lessons/0043-what-counts-as-breaking.md) | Ce qui compte comme cassant | Trois types de compatibilité, et la modification sûre à la compilation mais fatale à l'exécution |
| [0044](lessons/0044-designing-a-signature.md) | Concevoir une signature | Les types des paramètres et du retour décident de ce que peuvent faire les appelants, et l'essentiel des dégâts se fait à la frontière |
| [0045](lessons/0045-evolving-a-type.md) | Faire évoluer un type sans le casser | Comment enrichir une interface, un record, une enum et une hiérarchie sealed une fois que d'autres en dépendent |
| [0046](lessons/0046-deprecation-that-works.md) | Une dépréciation qui fonctionne | Marquer quelque chose comme déprécié ne change rien si vous ne dites pas ce qui se passe ensuite |
| [0047](lessons/0047-settling-it-from-the-source.md) | Trancher à partir de la source | Où chercher quand le débat porte sur ce que fait Java, et quel document répond à quelle question |
| [0048](lessons/0048-reviewing-java.md) | Relire du Java | Nommer ce que coûte une abstraction, au lieu de dire qu'elle paraît mauvaise |
| [0049](lessons/0049-does-this-framework-earn-its-place.md) | Ce framework mérite-t-il sa place | Le dernier jugement de l'étape 7, porté à partir des contraintes du service plutôt que des promesses du framework |
| [0050](lessons/0050-the-module-system.md) | Le système de modules | module-info.java remplace le JAR comme frontière que le compilateur et le runtime reconnaissent tous deux, requires et exports décident de ce qui la traverse, et l'encapsulation forte signifie qu'une classe publique dans un package non exporté est invisible au-delà de son propre module |
| [0051](lessons/0051-runtime-images.md) | Images de runtime | jlink assemble une image de runtime à partir de la seule fermeture transitive des modules par lesquels on lui dit de commencer, mais uniquement à partir de modules explicites : une application qui dépend ne serait-ce que d'un module automatique ne peut pas du tout être liée |
| [0052](lessons/0052-reflection-and-annotations.md) | Réflexion et annotations | Voici la synthèse de l'étape 8 : la réflexion lit et appelle la forme même d'une classe à l'exécution plutôt qu'à la compilation, une annotation est une donnée inerte tant que quelque chose ne la lit pas par réflexion, et chaque framework hors périmètre de ce fil conducteur est construit précisément à partir de ces deux mécanismes |

## Référence

- [Glossaire](GLOSSARY.md) : termes de référence pour ce sujet
- [Ressources](RESOURCES.md) : sources fiables, chacune annotée avec ce qu'elle couvre
- [Égalité, hachage et ordre](reference/equality-hashing-and-ordering.md) : les trois contrats, et quelle comparaison écrire
- [Modélisation](reference/modelling.md) : quelle construction choisir, ce à quoi chacune vous engage, et les règles faciles à mal retenir
- [Idiomes et bibliothèque](reference/idiom-and-library.md) : les décisions sur la bibliothèque que remarque un relecteur, et les pièges qui lèvent des exceptions là où personne ne regarde
- [Concurrence](reference/concurrency.md) : quelle garantie donne chaque construction, quel modèle convient à la charge de travail, et ce que signifie le symptôme que vous avez sous les yeux
- [Tests et build](reference/testing-and-build.md) : la tâche de build que chaque commande accomplit réellement, la doublure à choisir, et l'échec qui signifie que l'artefact est faux
- [Le runtime](reference/the-runtime.md) : où va la mémoire, quel collector répond à quelle exigence, et la mesure qui étaye une affirmation
- [Jugement](reference/judgment.md) : quelles modifications cassent quoi, comment retirer une API, et comment défendre la décision à partir de la source
- [Le système de modules](reference/the-module-system.md) : la fiche de l'étape 8, avec les trois conditions de l'accès entre modules, ce que fait chaque directive, et où finit le code d'un jar

## Comment cela fonctionne

Chaque leçon est courte et autonome. Les corrigés sont repliés : rappelez-vous d'abord, puis ouvrez-les. Les exercices en situation réelle comptent plus que la lecture, et les espacer dans le temps est justement le but. Tout ce qui reste flou à la fin d'une leçon mérite d'être suivi jusqu'à sa source primaire avant de passer à la suite.
