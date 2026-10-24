---
title: Conception d'API
description: "Concevoir une interface dont d'autres dépendent : le contrat, ses erreurs, et comment il évolue sans les casser"
type: topic
---

# Apprentissage : la conception d'API

Savoir concevoir de zéro une API publique versionnée (REST/HTTP ou gRPC), et faire évoluer une API existante en modifiant son contrat sans casser les clients qui en dépendent.

**Dernière leçon :** [19. La place de GraphQL](lessons/0019-where-graphql-fits.md)

## Objectif

- Concevoir le contrat d'une API REST/HTTP ou gRPC, y compris son modèle d'erreurs, pour un cas d'usage donné.
- Faire évoluer le contrat d'une API existante (ajouter, déprécier ou modifier un champ ou un endpoint) sans casser les clients, et expliquer la stratégie de versionnement ou de migration employée.
- Traiter l'authentification, l'autorisation et le rate limiting comme une partie du contrat dont dépend un client, et non comme un ajout boulonné après coup.

## Contraintes

- Suppose une expérience professionnelle de construction d'un service en HTTP ou en RPC ; aucune étude formelle préalable de la conception d'API n'est requise.
- Couvre à la fois REST/HTTP et gRPC, puisque les garanties de la mission s'appliquent aux deux.

## Hors périmètre

- Faire rejeter par le compilateur un état impossible au sein d'une même base de code : voir [`programming/typescript`](../../programming/typescript/) pour cette frontière. Ce parcours applique le même réflexe à travers une frontière où il n'existe aucun compilateur partagé.

## Le fil conducteur

Douze étapes, du contrat à la livraison asynchrone, jusqu'à la vérification du contrat lui-même face au comportement réel. Une étape comprend plusieurs leçons et les frontières sont souples ; ce qui termine une étape, c'est la capacité acquise, pas le nombre de leçons.

| Étape | Leçons | Contenu | Terminée quand |
|---|---|---|---|
| 1. Le contrat | 0001 | Ce sur quoi un client peut compter dépasse ce qui est documenté (loi de Hyrum) | Vous savez nommer la surface implicite d'un contrat au-delà de sa surface documentée |
| 2. Modèles d'erreurs | 0002 à 0003 | Codes de statut HTTP, Problem Details de la RFC 9457, codes de statut gRPC | Vous savez concevoir un modèle d'erreurs pour une API donnée |
| 3. Conception REST/HTTP | 0004 à 0005 | Modélisation des ressources, pagination et filtrage, recommandations de type AIP | Vous savez concevoir un contrat REST pour un cas d'usage donné |
| 4. Conception gRPC | 0006 à 0007 | proto3, conception de services, streaming | Vous savez concevoir un contrat gRPC pour le même cas d'usage |
| 5. Versionnement et évolution | 0008 à 0009 | Modifications additives, dépréciation, stratégie de migration | Vous savez faire évoluer le contrat d'une API existante sans casser ses clients |
| 6. Authentification, autorisation et rate limiting comme contrat | 0010 | Les traiter comme une partie de ce dont dépend un client, et non comme un ajout après coup | Vous savez concevoir l'authentification et le rate limiting comme contrat, et non comme un ajout boulonné à part |
| 7. Idempotence et nouveaux essais sûrs | 0011 | L'en-tête `Idempotency-Key`, les empreintes d'idempotence, et la distinction entre nouvel essai et requête concurrente | Vous savez concevoir un mécanisme d'idempotence qui rend une méthode non idempotente réellement sûre à réessayer |
| 8. Le cache HTTP comme contrat | 0012 | `ETag`, validateurs faibles contre forts, requêtes conditionnelles, concurrence optimiste avec `If-Match`, `Cache-Control` | Vous savez concevoir un contrat de cache et de contrôle de concurrence, et savez quelle force de comparaison exige chaque en-tête conditionnel |
| 9. Opérations de longue durée et livraison asynchrone | 0013 à 0014 | La ressource d'opération et le polling, la signature, les nouveaux essais et l'ordre des webhooks | Vous savez concevoir un contrat asynchrone (opération interrogée ou webhook poussé) et ses garanties d'échec, de nouvel essai et d'ordre |
| 10. Opérations en masse et réponses partielles | 0015 | Méthodes batch atomiques contre succès partiel, rapport d'erreur par élément, field masks | Vous savez concevoir la sémantique d'échec d'une méthode batch et un contrat de réponse partielle |
| 11. Le contrat lisible par machine | 0016 à 0017 | Documents OpenAPI et fichiers `.proto` comme artefacts générés, détection des changements cassants avec Buf, Spectral et oasdiff | Vous savez expliquer ce que permet un contrat lisible par machine, et en quoi un linter de style diffère d'un détecteur de changements cassants |
| 12. Tests de contrat et place de GraphQL | 0018 à 0019 | Les tests de contrat pilotés par le consommateur et `can-i-deploy`, et la place de GraphQL par rapport à REST et gRPC | Vous savez expliquer comment un test de contrat vérifie le comportement réel au-delà d'un schéma, et situer avec justesse l'évolution sans version de GraphQL par rapport au contenu REST/gRPC de ce fil conducteur |

## Leçons

Suivez-les dans l'ordre.

| # | Leçon | Enseigne |
|---|---|---|
| [0001](lessons/0001-the-contract.md) | Le contrat | Ce sur quoi un client peut compter dépasse ce que vous avez documenté, et la conception doit tenir compte des deux |
| [0002](lessons/0002-http-status-codes-and-error-semantics.md) | Codes de statut HTTP et sémantique des erreurs | Ce qu'un code de statut promet réellement à un client en matière de sûreté, d'idempotence et de marche à suivre, au-delà du vague regroupement 2xx/4xx/5xx |
| [0003](lessons/0003-problem-details-and-grpc-status-codes.md) | Problem Details de la RFC 9457 et codes de statut gRPC | Un format d'erreur structuré et lisible par machine pour HTTP, le vocabulaire parallèle des codes de statut de gRPC, et la conception d'un modèle d'erreurs unique qui fonctionne pour les deux |
| [0004](lessons/0004-resource-modeling-for-rest.md) | Modélisation des ressources pour REST | Pourquoi REST modélise une API autour de noms et d'états, et non de verbes, et comment une hiérarchie de ressources façonne le sens d'une URL |
| [0005](lessons/0005-pagination-and-filtering.md) | Pagination, filtrage et conception d'un contrat REST | Pourquoi la pagination par curseur l'emporte sur les offsets à grande échelle, comment le filtrage reste un contrat stable, et comment assembler la modélisation des ressources en une conception REST complète |
| [0006](lessons/0006-proto3-and-grpc-service-design.md) | Proto3 et conception de services gRPC | Pourquoi ce sont les numéros de champ de proto3, et non les noms de champ, qui forment le vrai contrat sur le réseau, et comment un service gRPC s'organise autour de méthodes RPC plutôt que de ressources |
| [0007](lessons/0007-grpc-streaming.md) | Le streaming gRPC et la conception du même cas d'usage | Les quatre types de RPC gRPC, quand chacun convient, et la conception d'un même cas d'usage à la fois comme contrat REST et comme contrat gRPC |
| [0008](lessons/0008-additive-changes-and-deprecation.md) | Modifications additives et dépréciation | Pourquoi ajouter est généralement sûr alors que supprimer ou changer le sens ne l'est généralement pas, et comment déprécier un champ ou un endpoint sans casser les clients du jour au lendemain |
| [0009](lessons/0009-versioning-and-migration-strategy.md) | Stratégie de versionnement et de migration | Comment livrer un véritable changement cassant sans casser d'un coup toutes les intégrations existantes, avec la stratégie de versionnement de Stripe comme exemple détaillé |
| [0010](lessons/0010-auth-authz-and-rate-limiting-as-contract.md) | Authentification, autorisation et rate limiting comme contrat | Pourquoi ce sont les scopes, et pas seulement les tokens, et un état de rate limit visible, et pas seulement un 429, qui font du contrôle d'accès et des quotas une partie délibérée du contrat |
| [0011](lessons/0011-idempotency-keys-and-safe-retries.md) | Clés d'idempotence et nouveaux essais sûrs | Une clé seule ne fait que dédupliquer ; c'est une empreinte qui indique au serveur si une clé répétée correspond à la même requête réessayée ou à une autre requête qui la réutilise par erreur, et un nouvel essai qui arrive pendant que l'original tourne encore reçoit un conflit, pas un rejeu |
| [0012](lessons/0012-http-caching-as-contract.md) | Le cache HTTP comme contrat | Le même validateur ETag remplit deux rôles différents selon la comparaison dont il a besoin : une comparaison faible suffit pour éviter un téléchargement redondant, mais seule une comparaison forte permet de détecter sans risque l'écriture concurrente de quelqu'un d'autre |
| [0013](lessons/0013-the-operation-resource-and-polling.md) | La ressource d'opération et le polling | Une méthode de longue durée renvoie une ressource en forme de promesse au lieu de bloquer, et un échec pendant l'exécution se signale autrement qu'un échec qui empêche l'opération de démarrer |
| [0014](lessons/0014-webhooks-and-callbacks-as-delivery.md) | Webhooks et callbacks comme mode de livraison | Pousser une notification au lieu d'attendre d'être interrogé inverse qui initie la requête, et c'est précisément cette inversion qui oblige la signature, les nouveaux essais et l'ordre à avoir chacun leur propre contrat explicite côté réception |
| [0015](lessons/0015-bulk-operations-and-partial-responses.md) | Opérations en masse et réponses partielles | Une méthode batch doit choisir d'avance si elle échoue en tout-ou-rien ou si elle rapporte le succès et l'échec élément par élément, et un client qui demande un sous-ensemble de champs doit formuler cette demande en dehors du corps qu'elle façonne |
| [0016](lessons/0016-openapi-and-protobuf-as-artifacts.md) | OpenAPI et Protobuf comme artefacts | Dès que le contrat existe sous forme de document lisible par machine et plus seulement en prose, le document lui-même devient quelque chose à versionner, à relire et à partir duquel générer d'autres choses, plutôt qu'une description écrite après coup |
| [0017](lessons/0017-breaking-change-linting.md) | Linting des changements cassants | Un linter qui vérifie le style d'un contrat et un outil de diff qui vérifie s'il a cassé un client répondent à deux questions différentes, et il faut encore poser à l'outil de diff la bonne question parmi trois |
| [0018](lessons/0018-contract-testing.md) | Tests de contrat | Un artefact de schéma vérifie la forme et un linter de changements cassants vérifie la compatibilité, mais aucun des deux ne confirme qu'un fournisseur se comporte réellement comme l'attendent les tests d'un vrai consommateur, ce que vérifie un test de contrat au moyen d'interactions d'exemple enregistrées |
| [0019](lessons/0019-where-graphql-fits.md) | La place de GraphQL | GraphQL résout le même problème de versionnement auquel ce parcours a consacré deux leçons en faisant de chaque requête un field mask d'emblée, au prix d'un contrat auquel les outils de ce parcours ne s'appliquent pas |

## Référence

- [Glossaire](GLOSSARY.md) : termes de référence pour ce sujet
- [Ressources](RESOURCES.md) : sources fiables
- [Modèles d'erreurs](reference/error-models.md) : codes de statut HTTP, membres de Problem Details et codes de statut gRPC côte à côte, pour quand vous concevez un modèle d'erreurs plutôt que d'apprendre pourquoi il fait partie du contrat
- [Conception des ressources REST](reference/rest-resource-design.md) : noms de ressources, méthodes standard et personnalisées, pagination et filtrage, avec la règle AIP que chaque décision doit respecter
- [Conception gRPC](reference/grpc-design.md) : numéros de champ proto3, quelles modifications de schéma sont sûres sur le format binaire et lesquelles cassent le JSON, les quatre types de RPC, et la sémantique d'appel dont hérite un contrat gRPC
- [Versionnement et évolution](reference/versioning-and-evolution.md) : quelles modifications cassent quel type de compatibilité, les en-têtes qui rendent une dépréciation visible pour l'outillage, et les modèles de versionnement entre lesquels choisir
- [Authentification et rate limiting](reference/auth-and-rate-limiting.md) : scopes et types de grant comme contrat, les codes d'erreur qu'un serveur de ressources doit à un client, et les champs RateLimit qui rendent un quota visible avant qu'il soit atteint

## Comment cela fonctionne

Chaque leçon est courte et autonome. Les corrigés sont repliés : rappelez-vous d'abord, puis ouvrez-les. Les exercices en situation réelle comptent plus que la lecture, et les espacer dans le temps est justement le but. Tout ce qui reste flou à la fin d'une leçon mérite d'être suivi jusqu'à sa source primaire avant de passer à la suite.
