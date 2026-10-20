---
title: "17. Prompt caching et disposition"
description: "Ordonner un prompt avec les parties stables en premier pour que le fournisseur puisse mettre le préfixe en cache"
type: lesson
---

# Leçon 17. Prompt caching et disposition

**Lien avec la mission :** Un gabarit de prompt qui place son texte stable en premier permet au fournisseur de ne pas le retraiter à chaque appel. La disposition est donc une décision de coût et de latence prise dans le gabarit, pas une réflexion après coup.
**Source primaire :** [Doc : "Prompt caching", Claude Platform Docs](https://platform.claude.com/docs/en/build-with-claude/prompt-caching)
**Prérequis :** [Leçon 16](0016-versioning-prompts.md), [Prompt caching](../GLOSSARY.md)

## Échauffement

1. ▢ La leçon 13 disait où placer un long document et la question dans un prompt. Lequel vient en premier, et cet ordre s'accorde-t-il avec le fait de placer le contenu stable en premier pour le cache ?

<details markdown="1"><summary>Vérifier</summary>

Les longs documents viennent en premier et la question en dernier. Cela s'accorde : un document réutilisé d'une requête à l'autre est stable, et la question change à chaque fois, donc les deux objectifs vont dans le même sens.

</details>

2. ▢ Le gabarit de la leçon 15 a du texte fixe et des emplacements. Lequel des deux est candidat au préfixe mis en cache, et lequel ne peut jamais l'être ?

<details markdown="1"><summary>Vérifier</summary>

Le texte fixe est candidat, puisqu'il est identique à chaque appel. Les valeurs d'emplacement propres à la requête changent, donc tout ce qui en contient une ne peut pas faire partie d'un préfixe réutilisé.

</details>

## À savoir

### C'est le préfixe qui est mis en cache

Le **prompt caching** conserve l'état traité d'un préfixe de prompt pour qu'un appel ultérieur partageant exactement ce préfixe évite de le recalculer. La documentation d'Anthropic décrit sa version : le préfixe mis en cache couvre toute la requête dans un ordre fixe, `tools`, puis `system`, puis `messages`, jusqu'au bloc marqué par `cache_control` inclus. Le hash derrière une entrée de cache est cumulatif : modifier n'importe quel bloc situé au niveau du bloc marqué ou avant produit donc un hash différent à la requête suivante, et l'entrée ne correspond plus.

Les autres fournisseurs implémentent le cache différemment, vérifiez donc leurs règles. Le principe ici, un préfixe exact réutilisé, est la partie à retenir.

### La disposition en découle

Placez en premier ce qui ne change jamais et en dernier ce qui change à chaque requête : les définitions d'outils, puis le system prompt, puis les longs documents et les exemples few-shot, puis la question propre à la requête. La documentation dit de placer le contenu statique au début et de marquer la fin de la partie réutilisable.

```python
def build_request(system: str, documents: str, question: str) -> dict:
    return {
        "system": system,
        "messages": [
            {
                "role": "user",
                "content": [
                    # stable: the end of this block is where a cache marker goes
                    {"type": "text", "text": documents},
                    # per request: after the marker, never part of the prefix
                    {"type": "text", "text": question},
                ],
            },
        ],
    }
```

Ici `documents` est partagé entre les appels et `question` ne l'est pas : le texte partagé passe donc en premier, et ce sont des blocs séparés pour que le marqueur puisse se trouver après les documents et avant la question. Dans l'API d'Anthropic, ce marqueur est un champ `cache_control` sur le bloc des documents, l'autre partie propre à un éditeur de cette esquisse. L'exemple d'erreur de la documentation est un bloc qui contient un horodatage et le message de l'utilisateur, avec le marqueur de cache dessus : le hash du préfixe inclut l'horodatage, donc chaque requête écrit une nouvelle entrée et n'en lit jamais. Gardez un horodatage, un identifiant de requête ou un nom d'utilisateur hors de la partie stable. Le correctif d'Anthropic consiste à placer le marqueur sur le dernier bloc identique d'une requête à l'autre.

### Ce qui casse un hit, et les limites

- Un préfixe plus court que le minimum du modèle n'est pas mis en cache, et aucune erreur n'est renvoyée. Le minimum documenté dépend du modèle et va de 512 à 4 096 tokens. Si `cache_creation_input_tokens` et `cache_read_input_tokens` dans l'usage de la réponse valent tous deux 0, le prompt n'a pas été mis en cache.
- Modifier les définitions d'outils invalide tout le cache. Le tableau d'invalidation de la documentation liste aussi les changements du réglage de choix d'outil, des images et de certains réglages de thinking et d'effort, qui invalident la partie messages.
- La durée de vie par défaut est de 5 minutes, rafraîchie à chaque lecture de l'entrée. Une option d'1 heure existe moyennant un coût supplémentaire.
- Une entrée de cache n'est disponible qu'une fois la première réponse commencée, donc des premières requêtes parallèles ne la partagent pas. Pour les charges concurrentes et d'agents, voir la [leçon 34 du parcours agents](../../agents/lessons/0034-prompt-caching-and-concurrency.md).

Les lectures sont moins chères que l'entrée non mise en cache et les écritures coûtent plus : la documentation indique les écritures de 5 minutes à 1,25 fois le prix d'entrée de base et les lectures à 0,1 fois, avec des exceptions par modèle sur les lectures. Une disposition qui n'obtient jamais de hit coûte donc légèrement plus que pas de cache du tout.

## Pratique

1. ▢ Un gabarit commence par `Current time: {now}`, puis un guide de style de 3 000 tokens, puis la question de l'utilisateur. Pourquoi le cache ne l'aide-t-il jamais, et quel est le correctif ?

<details markdown="1"><summary>Vérifier</summary>

L'horodatage est le premier bloc, donc le hash du préfixe change à chaque requête et aucun bloc ultérieur ne peut être lu depuis le cache. Déplacez le guide de style et tout autre texte fixe avant l'horodatage, ou retirez l'horodatage du prompt si la tâche n'en a pas besoin, et gardez la question en dernier.

</details>

2. ▢ Première requête : `cache_read_input_tokens` vaut 0, `cache_creation_input_tokens` vaut 2 400, `input_tokens` vaut 60. Seconde requête, même préfixe, une question de 75 tokens : que montrent les trois champs si le cache a fonctionné, et quelle est l'entrée totale ?

<details markdown="1"><summary>Indice</summary>

La documentation dit que `input_tokens` ne compte que ce qui vient après le dernier point d'arrêt du cache.

</details>

<details markdown="1"><summary>Vérifier</summary>

`cache_read_input_tokens` vaut 2 400, `cache_creation_input_tokens` vaut 0 et `input_tokens` vaut 75. L'entrée totale est la somme, 2 475 tokens. Le préfixe a été lu depuis le cache au lieu d'être réécrit, et seule la nouvelle question a été traitée à neuf.

</details>

3. ▢ Une équipe ajoute un system prompt de 600 tokens sur un modèle dont le minimum est de 1 024 tokens, le marque pour le cache, et voit les deux compteurs d'usage à 0. Que s'est-il passé, et quelque chose est-il cassé ?

<details markdown="1"><summary>Vérifier</summary>

Le prompt est sous le minimum, donc il a été traité sans cache et aucune erreur n'a été renvoyée. Rien n'est cassé. Ajoutez du contenu stable, comme des exemples, pour atteindre le minimum, ou acceptez des appels sans cache.

</details>

4. ▢ Quelle disposition de prompt est la meilleure pour mettre en cache un bot de support qui répond à de nombreuses questions sur un long document de politique ?

    - a) La question, puis le document de politique, puis le system prompt
    - b) Le system prompt, puis la question, puis le document de politique
    - c) Le system prompt, puis le document de politique, puis la question
    - d) Le system prompt, puis le nom de l'utilisateur, puis le document de politique

<details markdown="1"><summary>Vérifier</summary>

**c)** Le system prompt et le document sont identiques d'une requête à l'autre et passent en premier, et la question vient en dernier. (a) et (b) placent la question changeante avant le texte stable, donc le préfixe diffère à chaque appel. (d) place une valeur propre à l'utilisateur avant le document, ce qui casse le préfixe partagé pour chaque utilisateur différent.

</details>

## Exercices en situation réelle

- [ ] Prenez un prompt que vous exécutez et marquez chaque partie comme stable, changeant chaque jour, ou changeant à chaque requête, puis vérifiez que les parties stables passent en premier.
- [ ] Faites un appel deux fois avec le même préfixe chez un fournisseur qui rapporte l'usage du cache et lisez les compteurs des deux appels.
- [ ] Demain : trouvez tout horodatage, identifiant ou nom dans la zone stable d'un prompt et déplacez-le à la fin.

## Pour aller plus loin

- [Doc : "Prompt caching", Claude Platform Docs](https://platform.claude.com/docs/en/build-with-claude/prompt-caching)
- [Leçon 34 du parcours agents : Prompt caching et concurrence](../../agents/lessons/0034-prompt-caching-and-concurrency.md)
- [Prompts en production](../reference/prompts-in-production.md)
- [Ressources](../RESOURCES.md)

---

Ça ne passe pas ? Relisez la source primaire en haut de page, car cette leçon la condense et c'est dans la condensation que la compréhension s'échappe. Consultez le [glossaire](../GLOSSARY.md) pour tout terme qui vous a paru glissant.

Si c'est la leçon elle-même qui n'est pas claire plutôt que la matière, c'est un défaut : [ouvrez une issue](https://github.com/TokenCemetery/teach/issues).
