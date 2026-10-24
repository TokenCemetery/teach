---
title: SQL
description: "Maîtriser la base de données : écrire la requête, lire le plan, concevoir le schéma, survivre à la concurrence"
type: topic
---

# Apprentissage : SQL

Devenir l'ingénieur à qui une équipe confie sa base de données : capable d'exprimer une question sous forme d'une requête qui y répond exactement, de lire un plan de requête pour découvrir pourquoi cette requête est lente, de choisir un index à partir de preuves plutôt que d'intuition, de raisonner sur ce que des transactions concurrentes peuvent observer, et de concevoir et migrer un schéma qui tient les mauvaises données à l'écart et reste rapide à mesure que la table grandit.

**Commencez ici :** [0001. Tables, lignes et types](lessons/0001-tables-rows-and-types.md)
**Dernière leçon :** [0053. Triggers, procédures stockées, et où placer la logique](lessons/0053-triggers-stored-procedures-and-where-logic-belongs.md)

## Objectif

- Écrire une requête avec des jointures, des agrégations et des fonctions de fenêtrage qui répond à la question posée, et expliquer pourquoi le résultat contient exactement ces lignes, `NULL` compris.
- Lire un plan d'exécution avec les temps réels et nommer l'étape qui pose problème.
- Choisir un index, ou en écarter un, à partir du plan et de la sélectivité, puis prouver la différence par une mesure.
- Dire ce qu'une transaction à un niveau d'isolation donné peut observer, et nommer l'anomalie dont dépend un bug de concurrence.
- Concevoir un schéma où les mauvaises données sont impossibles plutôt que simplement découragées, à l'aide de clés, de types et de contraintes.
- Modifier un schéma sur un système en production sans interruption de service et sans file de verrous derrière la migration.
- Prendre une requête lente générée par un ORM, expliquer pourquoi elle est lente, et la réécrire.
- Relire la requête ou le schéma de quelqu'un et nommer concrètement ce qu'il coûtera avec dix fois plus de lignes.

## Contraintes

- Ne suppose aucune connaissance préalable de SQL, ni aucune expérience de l'administration de bases de données.
- PostgreSQL est le moteur de référence, car sa documentation est la description librement accessible la plus complète du comportement d'un vrai planificateur et d'un vrai modèle de concurrence. SQLite est utilisé là où un exercice ne devrait nécessiter aucun serveur. Là où les moteurs diffèrent réellement, la leçon le dit et nomme le comportement standard s'il en existe un.
- Ne nécessite qu'un moteur local et un terminal sur n'importe quel système d'exploitation pris en charge. Rien dans le fil conducteur n'exige d'outillage payant, de compte cloud ni de base de données managée.
- Les exercices ont besoin de données, et une table de dix lignes enseigne une mauvaise leçon sur les index. Le fil conducteur utilise un seul jeu de données qui devient assez grand pour que les choix du planificateur soient réels.
- Le comportement du planificateur change entre versions majeures. Les affirmations sensibles aux versions sont vérifiées dans la documentation actuelle, et toute leçon qui dépend d'une version indique laquelle.

## Hors périmètre

- L'administration de bases de données en tant que sujet : sauvegardes et restauration, réplication, basculement, pooling de connexions, mises à niveau de version. Voir [`data/postgres`](../../data/postgres/), qui prend en charge l'instance en fonctionnement.
- Les ORM et les query builders en tant que sujets à part entière. Leur sortie est lue et critiquée à l'étape 7 ; la façon d'en configurer un n'est pas enseignée.
- L'exécution des migrations depuis un pipeline de déploiement : quand une migration s'exécute par rapport au code qui en a besoin, et comment expand and contract répartit une modification sur plusieurs déploiements. C'est le rôle de [`infrastructure/ci-cd`](../../infrastructure/ci-cd/), dont la fiche [Déploiements](../../infrastructure/ci-cd/reference/deployments.md) contient l'ordre des migrations.
- Les entrepôts analytiques et leurs dialectes : BigQuery, Snowflake, Redshift, Spark SQL. L'exécution en colonnes change les conseils de performance, et le fil conducteur ne s'y aventure pas.
- Les stockages non relationnels comme alternatives à comparer. Celui qui a son propre parcours est [`data/redis`](../../data/redis/).
- Le fonctionnement interne des moteurs au-delà du point où il cesse d'expliquer le comportement des requêtes et des transactions : formats sur disque, fonctionnement interne du write-ahead log, code source du planificateur.

## Le fil conducteur

Sept étapes, de zéro jusqu'au niveau senior. Pas une liste de leçons : une étape comprend plusieurs leçons, et les frontières sont souples.

| Étape | Leçons | Contenu | Terminée quand |
|---|---|---|---|
| 1. Le modèle relationnel | 0001 à 0006 | Tables, lignes et types, `NULL` et la logique à trois valeurs, `SELECT`, filtrage, tri, ensembles contre multi-ensembles, ce qu'est une clé | Vous savez dire pourquoi une requête a renvoyé exactement ces lignes, y compris celles que `NULL` a écartées |
| 2. Interroger | 0007 à 0013 | Tous les types de jointure, l'agrégation et `GROUP BY`, `HAVING`, les sous-requêtes, les common table expressions, les opérations ensemblistes | Vous exprimez une question en une seule requête sans tâtonner |
| 3. Au-delà des bases | 0014 à 0020 | Fonctions de fenêtrage et frames, jointures latérales, requêtes récursives, colonnes `JSON` là où elles se justifient | Vous résolvez les problèmes de classement et de total cumulé en SQL plutôt que dans le code applicatif |
| 4. Conception de schéma | 0021 à 0027 | La normalisation et quand s'arrêter, clés primaires et étrangères, contraintes, choix délibéré des types, clés de substitution contre clés naturelles | Les mauvaises données sont impossibles plutôt que simplement découragées |
| 5. Transactions | 0028 à 0034 | ACID comme quatre promesses distinctes, les niveaux d'isolation et les anomalies que chacun permet, le contrôle de concurrence multiversion, le verrouillage, les deadlocks, les verrous explicites sur les lignes, l'idempotence | Vous savez nommer l'anomalie dont dépend un bug de concurrence, avant de le reproduire |
| 6. Performance | 0035 à 0041 | Les index B-tree d'abord et les autres ensuite, sélectivité et cardinalité, statistiques, lecture d'un plan avec les temps, stratégies de jointure, pagination, quand la requête n'est pas le problème | Vous optimisez à partir d'un plan et prouvez le gain par une mesure |
| 7. Exploitation et jugement | 0042 à 0048 | Migrations sans interruption de service, relecture des requêtes et des schémas, lecture de la sortie d'un ORM, portabilité entre moteurs, quand SQL est le mauvais outil | On vous fait confiance pour trancher et l'expliquer à quelqu'un d'autre ; l'étape 8 complète cela avec les questions de relecture sur l'autorisation et la logique procédurale que supposait la liste de contrôle de cette étape |
| 8. Sécurité et outils spécialisés | 0049 à 0053 | Injection SQL et requêtes paramétrées, rôles et moindre privilège, row-level security, recherche plein texte, triggers et procédures stockées | Vous relisez une frontière d'autorisation et un morceau de logique procédurale aussi concrètement qu'une requête ou une modification de schéma |

## Leçons

Suivez-les dans l'ordre.

| # | Leçon | Enseigne |
|---|---|---|
| [0001](lessons/0001-tables-rows-and-types.md) | Tables, lignes et types | Un type de colonne est une contrainte que vous obtenez gratuitement, et un mauvais type est difficile à défaire |
| [0002](lessons/0002-select-and-evaluation-order.md) | SELECT et ordre d'évaluation | Les clauses s'exécutent dans un ordre différent de celui dans lequel elles sont écrites, ce qui explique la plupart des erreurs de débutant |
| [0003](lessons/0003-null-and-three-valued-logic.md) | NULL et la logique à trois valeurs | WHERE ne garde que ce qui est vrai, donc l'inconnu se comporte comme faux et NOT IN peut ne rien renvoyer |
| [0004](lessons/0004-sets-and-bags.md) | Ensembles et multi-ensembles | Une table est un multi-ensemble, donc les doublons sont réels et UNION paie discrètement pour les supprimer |
| [0005](lessons/0005-sorting-and-collation.md) | Tri et collation | L'ordre du texte dépend d'une collation, et un ex aequo sans clé unique n'est pas stable |
| [0006](lessons/0006-keys-and-constraints.md) | Clés et contraintes | Une clé est une affirmation que la base de données fait respecter, et chaque affirmation que vous omettez devient un bug |
| [0007](lessons/0007-joins-and-what-they-do.md) | Les jointures, et ce que fait réellement une jointure | Une jointure est un produit cartésien filtré, donc la condition ON décide quelles lignes existent avant que quoi que ce soit d'autre ne s'exécute |
| [0008](lessons/0008-outer-joins-and-missing-rows.md) | Les jointures externes et les lignes absentes | Une jointure externe garde les lignes qui ne correspondent à rien, et une seule clause WHERE les jette de nouveau en silence |
| [0009](lessons/0009-aggregation-and-group-by.md) | Agrégation et GROUP BY | Les agrégats ignorent NULL, et une jointure qui multiplie les lignes multiplie le total |
| [0010](lessons/0010-having-and-filter.md) | HAVING, FILTER et plusieurs regroupements à la fois | L'endroit où se trouve une condition décide quelles lignes elle peut encore voir, et un seul passage peut répondre à plusieurs regroupements |
| [0011](lessons/0011-subqueries.md) | Les sous-requêtes, et quel type répond à la question | Un scalaire, un IN, un EXISTS et une table dérivée répondent à quatre questions différentes, et l'un d'eux ment quand NULL apparaît |
| [0012](lessons/0012-common-table-expressions.md) | Common table expressions | WITH nomme une étape pour qu'une longue requête se lise de haut en bas, et dans cette version ce n'est pas une barrière d'optimisation |
| [0013](lessons/0013-set-operations.md) | Les opérations ensemblistes, et une question en une seule requête | UNION, INTERSECT et EXCEPT combinent des ensembles de résultats par position et suppriment les doublons sauf indication contraire |
| [0014](lessons/0014-window-functions.md) | Fonctions de fenêtrage | Une fonction de fenêtrage calcule sur d'autres lignes sans réduire celle sur laquelle elle se trouve |
| [0015](lessons/0015-window-frames.md) | Frames de fenêtrage | Le frame par défaut inclut toutes les lignes ex aequo avec la ligne courante, c'est pourquoi un total cumulé peut faire un saut |
| [0016](lessons/0016-navigating-within-a-window.md) | Naviguer dans une fenêtre | lag, lead et les fonctions de valeur atteignent directement d'autres lignes, et deux d'entre elles obéissent au frame |
| [0017](lessons/0017-lateral-joins.md) | Jointures latérales | LATERAL permet à une sous-requête dans FROM de voir la ligne voisine, c'est ainsi qu'on prend les premiers éléments de chaque groupe |
| [0018](lessons/0018-recursive-queries.md) | Requêtes récursives | Une CTE récursive réinjecte sa propre sortie jusqu'à ce que plus rien de nouveau n'en sorte, c'est ainsi qu'on parcourt une hiérarchie |
| [0019](lessons/0019-json-columns.md) | Colonnes JSON | Interroger une colonne de documents relève du SQL ordinaire une fois que vous savez quel opérateur renvoie du texte et lequel renvoie du JSON |
| [0020](lessons/0020-choosing-the-tool.md) | Choisir l'outil | Le top-N, les totaux cumulés et la déduplication ont chacun deux ou trois écritures correctes, et le choix dépend de ce que demande la question |
| [0021](lessons/0021-normalisation.md) | Normalisation | Chaque forme normale supprime une façon pour deux lignes d'être en désaccord sur le même fait |
| [0022](lessons/0022-choosing-a-key.md) | Choisir une clé | Une clé de substitution apporte la stabilité et renonce au sens, et le générateur que vous choisissez décide de ce qu'elle coûte par ailleurs |
| [0023](lessons/0023-foreign-keys.md) | Les clés étrangères et ce qui se passe à la suppression | Une clé étrangère est une promesse sur des lignes qui existent, et l'action que vous choisissez décide de qui paie quand l'une d'elles disparaît |
| [0024](lessons/0024-constraints-that-hold.md) | Des contraintes qui tiennent vraiment | Un CHECK n'échoue que lorsque sa condition est fausse, donc une valeur absente satisfait presque toutes les règles que vous avez écrites |
| [0025](lessons/0025-choosing-types.md) | Choisir les types délibérément | Un type décide de ce que la base de données acceptera, de ce qu'elle modifiera en silence, et de ce qu'elle ne pourra jamais rendre |
| [0026](lessons/0026-denormalising-on-purpose.md) | Dénormaliser à dessein | Une seconde copie d'un fait est une seconde occasion de se tromper, sauf si c'est la base de données qui l'entretient |
| [0027](lessons/0027-making-bad-data-impossible.md) | Rendre les mauvaises données impossibles | Prendre un schéma qui autorise une ligne fausse et combler chaque brèche, puis dire ce que la conception ne peut toujours pas promettre |
| [0028](lessons/0028-what-a-transaction-promises.md) | Ce que promet une transaction | Quatre promesses voyagent sous un seul acronyme, et une seule d'entre elles est à vous de négocier |
| [0029](lessons/0029-mvcc.md) | Contrôle de concurrence multiversion | Une mise à jour écrit une nouvelle version de ligne au lieu d'en modifier une, c'est pourquoi un lecteur n'attend jamais un écrivain |
| [0030](lessons/0030-isolation-levels.md) | Niveaux d'isolation | PostgreSQL vous donne trois niveaux distincts sous quatre noms, et chacun permet un ensemble différent de surprises |
| [0031](lessons/0031-the-anomalies.md) | Les anomalies, et comment reconnaître la vôtre | Chaque bug de concurrence a un nom, et le nommer vous dit quel niveau ou quel verrou l'aurait empêché |
| [0032](lessons/0032-locks.md) | Les verrous que l'on prend délibérément | Un verrou sur une ligne est la façon de figer une décision, et chacun d'eux a un mode de défaillance qu'il vaut la peine de choisir |
| [0033](lessons/0033-deadlocks.md) | Deadlocks | Deux transactions qui détiennent chacune ce dont l'autre a besoin, et le seul remède est de s'accorder à l'avance sur un ordre |
| [0034](lessons/0034-idempotency-and-retry.md) | L'idempotence et le nouvel essai correct | Un nouvel essai qui rejoue les mêmes instructions reproduit le bug qu'il devait corriger, il doit donc relire et redécider |
| [0035](lessons/0035-reading-a-plan.md) | Lire un plan | Le plan vous dit ce que la base de données a fait et ce qu'elle attendait, et c'est dans l'écart entre les deux que se trouve le travail |
| [0036](lessons/0036-what-an-index-does.md) | Ce que fait réellement un index | Un B-tree transforme le parcours de toutes les lignes en une descente à travers quelques pages, et le plan nomme laquelle des quatre façons a servi à les lire |
| [0037](lessons/0037-selectivity-and-statistics.md) | Sélectivité et statistiques | Chaque plan est construit à partir d'un échantillon de vos données, donc un mauvais plan est généralement une mauvaise estimation plutôt qu'un mauvais planificateur |
| [0038](lessons/0038-choosing-an-index.md) | Choisir un index | L'ordre des colonnes décide des requêtes auxquelles un index peut répondre, et le meilleur index est souvent celui que vous décidez de ne pas créer |
| [0039](lessons/0039-join-strategies.md) | Stratégies de jointure | Trois façons de joindre et le planificateur choisit selon le coût estimé, donc une mauvaise estimation apparaît comme une mauvaise stratégie |
| [0040](lessons/0040-pagination-and-counting.md) | Pagination et comptage | OFFSET lit et jette chaque ligne qu'il saute, et compter exactement coûte un passage complet sur la table |
| [0041](lessons/0041-when-the-query-is-not-the-problem.md) | Quand la requête n'est pas le problème | Prouver un gain demande une mesure que l'on peut répéter, et la cause est souvent la table, le trafic ou le client |
| [0042](lessons/0042-migrations-without-downtime.md) | Migrations sans interruption de service | Une migration qui prend une milliseconde peut quand même bloquer toutes les lectures de la table, à cause de ce qui fait la queue derrière elle |
| [0043](lessons/0043-changing-what-has-data.md) | Modifier ce qui contient déjà des données | Une contrainte sur une table pleine s'écrit en deux instructions, et un backfill est une boucle plutôt qu'un seul UPDATE |
| [0044](lessons/0044-reviewing-a-query.md) | Relire une requête | Lire la requête pour les lignes qu'elle renvoie avant de la lire pour sa vitesse, car une mauvaise réponse rapide est pire |
| [0045](lessons/0045-reviewing-a-schema-change.md) | Relire une modification de schéma | Demander ce que la migration verrouille, ce qu'elle réécrit, et ce qui tourne pendant que les deux versions du code sont en production |
| [0046](lessons/0046-portability.md) | La portabilité, et ce qu'elle coûte | L'essentiel de ce fil conducteur se transpose d'un moteur à l'autre, et les parties qui ne se transposent pas sont celles dont il vaut la peine de dépendre délibérément |
| [0047](lessons/0047-reading-orm-output.md) | Lire ce qu'émet un ORM | L'ORM écrit le SQL que vous n'avez pas écrit, et la seule façon de savoir ce qu'il a envoyé est de regarder |
| [0048](lessons/0048-trusted-with-the-database.md) | Digne de confiance avec la base de données | Sept étapes aboutissent à une seule habitude : nommer la ligne, le verrou ou le plan qui rend une décision défendable |
| [0049](lessons/0049-sql-injection-and-parameterised-statements.md) | Injection SQL et requêtes paramétrées | La concaténation de chaînes permet à une valeur de changer ce que signifie une instruction, et pas seulement ce qu'elle sélectionne, et une requête paramétrée supprime cette possibilité au lieu d'essayer d'assainir chaque cas |
| [0050](lessons/0050-roles-and-least-privilege.md) | Rôles et moindre privilège | Les rôles englobent les anciennes notions d'utilisateurs et de groupes, être propriétaire accorde déjà tous les privilèges sans aucun GRANT, et le moindre privilège porte entièrement sur ce que tous les autres ont le droit de faire |
| [0051](lessons/0051-row-level-security.md) | Row-level security | GRANT décide de l'accès à une table dans son ensemble, une politique de sécurité au niveau des lignes en décide ligne par ligne, et le moteur l'applique sur chaque chemin d'accès, pas seulement sur celui qu'un développeur a pensé à filtrer |
| [0052](lessons/0052-full-text-search.md) | Recherche plein texte | tsvector réduit un document à des lexèmes normalisés qu'un index GIN peut rechercher, tsquery demande s'ils sont présents, et la frontière avec un moteur de recherche dédié se situe là où le classement et l'échelle dépassent ce qu'une seule colonne peut offrir |
| [0053](lessons/0053-triggers-stored-procedures-and-where-logic-belongs.md) | Triggers, procédures stockées, et où placer la logique | Voici la synthèse de l'étape 8 : un trigger s'exécute sur chaque chemin qui atteint une table et une procédure peut valider ou annuler sa propre transaction, et le jugement consiste à décider quand cette invisibilité vaut réellement son coût |

## Référence

- [Glossaire](GLOSSARY.md) : termes de référence pour ce sujet
- [Ressources](RESOURCES.md) : sources fiables, chacune annotée avec ce qu'elle couvre
- [Le jeu de données](reference/the-dataset.md) : le schéma et les données qu'interroge chaque leçon à partir de l'étape 2, et comment les charger
- [NULL et la logique à trois valeurs](reference/null-and-three-valued-logic.md) : tables de vérité, où NULL compte comme égal, et les pièges avec leurs corrections
- [Ordre d'évaluation d'un SELECT](reference/select-evaluation-order.md) : ce qui s'exécute quand, ce que chaque clause peut voir, et quelles erreurs cela explique
- [Interroger](reference/querying.md) : la fiche de l'étape 2, avec chaque type de jointure, ce que chaque agrégat fait de NULL, et où placer une condition
- [Au-delà des bases](reference/beyond-the-basics.md) : la fiche de l'étape 3, avec les fonctions de fenêtrage, les modes de frame, et quel outil répond à quelle question
- [Conception de schéma](reference/schema-design.md) : la fiche de l'étape 4, avec les formes normales, chaque type de contrainte, et quel type refuse quoi
- [Transactions](reference/transactions.md) : la fiche de l'étape 5, avec chaque niveau d'isolation, les anomalies qu'il permet, les forces de verrou, et les erreurs qui justifient un nouvel essai
- [Performance](reference/performance.md) : la fiche de l'étape 6, avec les nœuds du plan, les chiffres auxquels se fier, les stratégies de parcours et de jointure, et les décisions d'indexation
- [Exploitation](reference/operating.md) : la fiche de l'étape 7, avec les migrations sûres, les questions de relecture, et ce qui se transpose d'un moteur à l'autre

## Comment cela fonctionne

Chaque leçon est courte et autonome. Les corrigés sont repliés : rappelez-vous d'abord, puis ouvrez-les. Les exercices en situation réelle comptent plus que la lecture, et les espacer dans le temps est justement le but. Tout ce qui reste flou à la fin d'une leçon mérite d'être suivi jusqu'à sa source primaire avant de passer à la suite.
