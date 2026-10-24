---
title: TypeScript
description: "Maîtriser une base de code TypeScript : faire rejeter par le compilateur les états qui ne devraient pas exister"
type: topic
---

# Apprentissage : TypeScript

Devenir l'ingénieur à qui l'on confie une base de code TypeScript au sein d'une équipe : capable de modéliser un domaine pour que le compilateur rejette les états qui ne devraient pas exister, de tenir les assertions de type à l'écart du code qui porte une charge réelle, de valider ce qui franchit une frontière d'exécution plutôt que de supposer que les types tenaient, et de relire les types de quelqu'un en disant concrètement pourquoi un générique astucieux coûte plus qu'il ne rapporte.

**Commencez ici :** [0001. Valeurs et coercition](lessons/0001-values-and-coercion.md)
**Dernière leçon :** [0049. Digne de confiance pour trancher](lessons/0049-trusted-to-make-the-call.md), qui clôt le fil conducteur

## Objectif

- Prédire ce que fait JavaScript avec la coercition, les closures, `this` et l'event loop, avant d'exécuter le code et sans l'aide du système de types.
- Transformer un ensemble d'états illégaux en un type que le compilateur rejette, et prouver l'exhaustivité avec `never`.
- Remonter le message d'erreur d'un générique jusqu'à sa cause au lieu de recourir à `as`.
- Dire exactement ce qui survit à la compilation et ce qui est effacé, et valider chaque valeur qui entre dans le programme depuis l'extérieur.
- Configurer le compilateur en connaissance de cause : nommer ce qu'apporte chaque option de sévérité et pourquoi les paramètres de module et de target sont ce qu'ils sont.
- Écrire une fonction générique dont l'inférence fonctionne, pour que les appelants n'annotent rien.
- Publier un paquet dont les types sont utilisables par ses consommateurs, y compris la sortie de déclarations et les exports qu'il annonce.
- Relire une pull request et dire précisément pourquoi un type conditionnel, une assertion ou un `enum` n'est pas le bon outil à cet endroit.

## Contraintes

- Ne suppose aucune connaissance préalable de TypeScript, et pas plus de JavaScript que ce qu'enseigne le fil conducteur. TypeScript est un système de types posé sur JavaScript, donc la sémantique de JavaScript est enseignée partout où elle explique un comportement qu'un type ne peut pas expliquer.
- La frontière entre compilation et exécution est traitée comme une ligne infranchissable tout au long du parcours, car presque toutes les erreurs sérieuses en TypeScript sont une affirmation sur l'exécution que seul le compilateur a jamais vérifiée.
- Ne nécessite qu'un runtime JavaScript et un terminal sur n'importe quel système d'exploitation pris en charge, le playground en ligne remplaçant les deux quand un exercice n'a besoin que de voir un type. Aucun outillage payant, aucun compte cloud, aucun framework.
- Les exercices sont de petits programmes et de petites expériences sur les types qui tiennent en une séance.
- TypeScript sort une version tous les quelques mois, et le système de types gagne une réelle expressivité dans ces versions. Les affirmations sensibles aux versions sont vérifiées dans les notes de version, et toute leçon qui dépend d'une version indique laquelle.

## Hors périmètre

- Les frameworks et les bibliothèques d'interface en tant que sujets à part entière : React, Angular, Vue, Svelte, Next.js.
- Les bundlers et l'outillage de monorepo en tant que sujets : webpack, Vite, esbuild, Turborepo. La résolution des modules est enseignée à partir du modèle propre au compilateur, auquel ces outils doivent se conformer.
- Les autres runtimes en tant que sujets : Deno, Bun, la plateforme du navigateur. Ils n'apparaissent que là où le comportement diffère réellement.
- Node.js en tant que plateforme à part entière : streams, clustering, addons natifs.
- La programmation au niveau des types comme sport. Les types mappés et conditionnels sont enseignés jusqu'au point où ils servent un appelant, et l'étape 6 dit explicitement où se situe ce point.

## Le fil conducteur

Sept étapes, de zéro jusqu'au niveau senior. Pas une liste de leçons : une étape comprend plusieurs leçons, et les frontières sont souples.

| Étape | Leçons | Contenu | Terminée quand |
|---|---|---|---|
| 1. Le JavaScript en dessous | 0001 à 0007 | Valeurs et coercition, objets et prototypes, closures, `this`, modules, l'event loop, promesses et async | Vous savez prédire ce que fait un programme à l'exécution, sans aucun type en jeu |
| 2. Des types sur des valeurs | 0008 à 0014 | Primitifs, tableaux et tuples, unions, types littéraux, assignabilité structurelle, narrowing, types fonction, `readonly`, ce que l'inférence sait déjà | Vous n'annotez que là où l'inférence ne peut pas aller |
| 3. La sévérité et le compilateur | 0015 à 0021 | La famille `strict` option par option, les options de type strict que `strict` omet encore, `unknown` face à `any`, assertions face aux déclarations, `tsconfig`, résolution des modules, `target` et `lib` | Vous gardez la sévérité activée et corrigez ce qu'elle signale au lieu de le masquer, et activez les vérifications que `strict` laisse de côté |
| 4. Modélisation | 0022 à 0028 | Unions discriminées, exhaustivité avec `never`, types brandés, génériques et contraintes, `satisfies`, interface face à type alias | Les états illégaux sont irreprésentables, et c'est le compilateur qui le prouve |
| 5. La frontière d'exécution | 0029 à 0035 | Ce qui est effacé, fichiers de déclaration, validation des entrées à la périphérie, les erreurs comme valeurs, consommer des dépendances non typées ou mal typées | Aucune valeur n'entre dans le programme sans être validée, et aucune assertion ne porte de charge |
| 6. Outils au niveau des types | 0036 à 0042 | Types mappés et conditionnels, `infer`, types template literal, variance et assignabilité, inférence pour les API de bibliothèque, performance du compilateur | Vous écrivez une API dont les types servent ses appelants, et vous arrêtez avant de tomber dans l'astuce |
| 7. Jugement | 0043 à 0049 | Publier une surface de types publique, ce qui compte comme changement cassant dans les types, relecture, lecture des notes de version et des déclarations propres au compilateur | On vous fait confiance pour trancher et l'expliquer à quelqu'un d'autre |

## Leçons

Suivez-les dans l'ordre.

| # | Leçon | Enseigne |
|---|---|---|
| [0001](lessons/0001-values-and-coercion.md) | Valeurs et coercition | Sept primitifs, deux valeurs vides, et un opérateur d'égalité qui convertit avant de comparer |
| [0002](lessons/0002-objects-are-references.md) | Les objets sont des références | const empêche la réaffectation, la décomposition copie un seul niveau, et readonly disparaît à l'exécution |
| [0003](lessons/0003-prototypes-and-classes.md) | Prototypes et classes | La recherche de propriété parcourt une chaîne, et la syntaxe class est une façon de construire cette chaîne |
| [0004](lessons/0004-this-and-the-call-site.md) | this est décidé par l'appel | this dépend de la façon dont une fonction est appelée, donc extraire une méthode le fait perdre |
| [0005](lessons/0005-scope-and-closures.md) | Portée et closures | Une closure capture la liaison plutôt que la valeur, et let en crée une par itération |
| [0006](lessons/0006-event-loop-and-promises.md) | L'event loop, les promesses et await | Les microtâches se vident avant le timer suivant, et deux await à la suite sont séquentiels |
| [0007](lessons/0007-modules.md) | Modules | Les imports sont remontés et liés en direct, et un fichier sans import ni export n'est pas un module |
| [0008](lessons/0008-the-types-you-write.md) | Les types que vous écrivez | Le vocabulaire des annotations, et un compilateur qui proteste déjà avant que vous ne le configuriez |
| [0009](lessons/0009-tuples-and-readonly.md) | Tuples et readonly | Une longueur fixe que le compilateur fait respecter à la lecture et oublie lors d'un push |
| [0010](lessons/0010-unions-and-literal-types.md) | Unions et types littéraux | Une valeur qui a plus d'un type possible, et l'élargissement qui jette le plus intéressant |
| [0011](lessons/0011-structural-assignability.md) | Assignabilité structurelle | La forme décide de ce qui va où, sauf pour la seule vérification qui ne se déclenche que sur un littéral d'objet frais |
| [0012](lessons/0012-narrowing.md) | Narrowing | Le flux de contrôle indique au compilateur ce qu'est devenue une union, et exactement deux choses le lui font oublier |
| [0013](lessons/0013-function-types.md) | Types fonction | Les paramètres sont vérifiés dans le sens que vous attendez, sauf si vous avez écrit une méthode |
| [0014](lessons/0014-what-inference-already-knows.md) | Ce que l'inférence sait déjà | Jusqu'où va l'inférence, pour qu'écrire une annotation ait un sens quand vous le faites |
| [0015](lessons/0015-what-strict-turns-on.md) | Ce qu'active strict | Sept vérifications derrière une seule option, chacune avec un échec qu'elle existe pour attraper |
| [0016](lessons/0016-the-checks-strict-leaves-out.md) | Les vérifications que strict laisse de côté | Six autres vérifications qui valent d'être activées, une que le compilateur refuse d'activer, et une qui ne fait rien du tout |
| [0017](lessons/0017-unknown-instead-of-any.md) | unknown au lieu de any | Un type accepte tout et ne vous laisse rien faire, l'autre accepte tout et ne vérifie rien |
| [0018](lessons/0018-an-assertion-is-not-a-check.md) | Une assertion n'est pas une vérification | Toutes les façons de dire au compilateur d'arrêter de vérifier, et ce que chacune coûte quand l'affirmation est fausse |
| [0019](lessons/0019-reading-a-tsconfig.md) | Lire un tsconfig | Quels fichiers le compilateur examine, d'où viennent les paramètres, et pourquoi le fichier généré dit ce qu'il dit |
| [0020](lessons/0020-target-and-lib.md) | target et lib | Un paramètre change ce qui est émis et l'autre change ce qui existe, et nommer le second jette la valeur par défaut |
| [0021](lessons/0021-module-resolution.md) | Résolution des modules | Les mêmes options du compilateur donnent des verdicts opposés selon un seul champ de package.json |
| [0022](lessons/0022-discriminated-unions.md) | Unions discriminées | Une propriété littérale partagée, et une union que le compilateur sait décomposer |
| [0023](lessons/0023-exhaustiveness-with-never.md) | Exhaustivité avec never | Ajouter un membre à une union devrait casser chaque switch qui l'ignorait, et une seule ligne y suffit |
| [0024](lessons/0024-illegal-states.md) | Rendre les états illégaux irreprésentables | Compter les états que votre type permet, puis supprimer ceux que votre domaine ne connaît pas |
| [0025](lessons/0025-branded-types.md) | Types brandés | Un typage nominal par-dessus un système structurel, et l'unique assertion qu'il coûte |
| [0026](lessons/0026-generics-and-constraints.md) | Génériques et contraintes | Un paramètre de type est une promesse faite à l'appelant, et une contrainte est ce qui vous permet de la tenir |
| [0027](lessons/0027-satisfies.md) | satisfies | Vérifier une valeur par rapport à un type sans laisser le type remplacer ce que vous avez écrit |
| [0028](lessons/0028-interface-or-type.md) | interface ou type | L'un signale un membre en conflit là où vous l'avez écrit, l'autre le signale ailleurs |
| [0029](lessons/0029-nothing-survives-to-run-time.md) | Rien ne survit jusqu'à l'exécution | Chaque type est une affirmation sur un programme qui n'existe plus au moment où l'affirmation compterait |
| [0030](lessons/0030-unknown-at-the-edge.md) | unknown à la périphérie | Trouver chaque endroit où une valeur arrive de l'extérieur, et donner à chacun le seul type honnête |
| [0031](lessons/0031-parsing-instead-of-asserting.md) | Parser au lieu d'affirmer | Une seule déclaration qui produit à la fois la vérification à l'exécution et le type statique |
| [0032](lessons/0032-type-predicates-and-assertion-functions.md) | Prédicats de type et fonctions d'assertion | Une signature qui promet une vérification, et un corps que rien ne compare à cette promesse |
| [0033](lessons/0033-errors-as-values.md) | Les erreurs comme valeurs | Un échec présent dans le type de retour est un échec que le compilateur peut vous obliger à traiter |
| [0034](lessons/0034-declaration-files.md) | Fichiers de déclaration | Des types pour du code que le compilateur ne voit jamais, et ce que vaut cette promesse |
| [0035](lessons/0035-when-the-declaration-lies.md) | Quand la déclaration ment | Le compilateur croit la déclaration et le runtime n'en a jamais entendu parler |
| [0036](lessons/0036-mapped-types.md) | Types mappés | Transformer toutes les propriétés d'un type à la fois, et supprimer celles dont vous ne voulez pas |
| [0037](lessons/0037-conditional-types.md) | Types conditionnels | Un type qui se ramifie, et une union qu'il décompose discrètement en premier |
| [0038](lessons/0038-infer.md) | infer | Extraire un type d'une position au lieu de demander à l'appelant de le nommer |
| [0039](lessons/0039-template-literal-types.md) | Types template literal | Un motif de chaîne que le compilateur vérifie, et les noms de clés qu'il peut construire |
| [0040](lessons/0040-variance-and-assignability.md) | Variance et assignabilité | Dans quel sens un type peut circuler, et le tableau qui se trompe exprès |
| [0041](lessons/0041-inference-for-library-apis.md) | L'inférence pour les API de bibliothèque | Concevoir la signature pour que l'appelant n'annote rien |
| [0042](lessons/0042-knowing-when-to-stop.md) | Savoir quand s'arrêter | Mesurer ce que coûte un type astucieux, puis le justifier auprès de quiconque le maintient |
| [0043](lessons/0043-what-counts-as-a-breaking-change.md) | Ce qui compte comme changement cassant | Quelles modifications d'un type publié cassent un consommateur, et dans quel sens chacune doit aller |
| [0044](lessons/0044-publishing-a-type-surface.md) | Publier une surface de types | Ce qu'un consommateur résout réellement quand il importe votre paquet, et comment le vérifier avant lui |
| [0045](lessons/0045-the-consumers-settings-are-not-yours.md) | Les paramètres du consommateur ne sont pas les vôtres | Un consommateur strict hérite des affirmations d'un auteur laxiste et n'a aucun moyen de s'en apercevoir |
| [0046](lessons/0046-the-typescript-that-does-not-erase.md) | Le TypeScript qui ne s'efface pas | Quatre fonctionnalités qui émettent du code que vous n'avez pas demandé, et l'option qui les nomme |
| [0047](lessons/0047-settling-it-from-the-source.md) | Trancher à partir de la source | Quel document répond à une question sur le compilateur, et comment lire les déclarations qu'il fournit |
| [0048](lessons/0048-reviewing-typescript.md) | Relire du TypeScript | Nommer ce que coûte un type, au lieu de dire qu'il paraît compliqué |
| [0049](lessons/0049-trusted-to-make-the-call.md) | Digne de confiance pour trancher | Le dernier jugement du fil conducteur, et ce que le compilateur n'allait jamais faire à votre place |

## Référence

- [Glossaire](GLOSSARY.md) : termes de référence pour ce sujet
- [Ressources](RESOURCES.md) : sources fiables, chacune annotée avec ce qu'elle couvre
- [Coercition et égalité](reference/coercion-and-equality.md) : valeurs falsy, ce que `==` convertit, quel opérateur par défaut écrire
- [Event loop et promesses](reference/event-loop-and-promises.md) : ordre des files, combinateurs, et les erreurs d'async qu'aucun compilateur ne signale
- [Des types sur des valeurs](reference/types-over-values.md) : ce qu'apporte chaque annotation, jusqu'où va l'inférence, et les trous que le compilateur laisse ouverts exprès
- [La sévérité et le compilateur](reference/strictness-and-the-compiler.md) : quelle option attrape quel échec, d'où vient un paramètre, et comment un import se résout
- [Modélisation](reference/modelling.md) : quelle forme supprime l'état illégal, et quelle déclaration attrape l'erreur là où vous l'avez commise
- [La frontière d'exécution](reference/the-runtime-boundary.md) : où entrent les valeurs, ce qui les vérifie, et quelles affirmations rien ne vérifie du tout
- [Outils au niveau des types](reference/type-level-tools.md) : quelle construction calcule quel type, et le test qu'une construction astucieuse doit réussir
- [Jugement](reference/judgment.md) : quelles modifications cassent un consommateur, ce qui ne s'efface pas, et comment défendre la décision à partir de la source

## Comment cela fonctionne

Chaque leçon est courte et autonome. Les corrigés sont repliés : rappelez-vous d'abord, puis ouvrez-les. Les exercices en situation réelle comptent plus que la lecture, et les espacer dans le temps est justement le but. Tout ce qui reste flou à la fin d'une leçon mérite d'être suivi jusqu'à sa source primaire avant de passer à la suite.
