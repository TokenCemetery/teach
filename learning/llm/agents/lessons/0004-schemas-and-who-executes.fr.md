---
title: "4. Schémas de paramètres et qui exécute quoi"
description: "Comment les schémas JSON contraignent ce qu'un modèle peut envoyer, et la différence entre outils client et outils serveur"
type: lesson
---

# Leçon 4. Schémas de paramètres et qui exécute quoi

**Lien avec la mission :** Écrire la boucle d'agent pour une tâche donnée, et nommer ce que fait chaque message de son contexte et ce qui met fin à la boucle.
**Source primaire :** [Doc : "Tool use with Claude", Claude Platform Docs](https://platform.claude.com/docs/en/agents-and-tools/tool-use/overview)
**Prérequis :** [Leçon 3](0003-the-wire-format-of-a-tool-call.md)

## Échauffement

1. ▢ Quand vous envoyez une définition d'outil à un fournisseur de modèle, quel rôle joue le schéma JSON ?

<details markdown="1"><summary>Vérifier</summary>

Il décrit les arguments que l'outil accepte : noms, types et contraintes. Le modèle utilise le schéma pour décider quoi envoyer quand il appelle l'outil. Un schéma bien formé empêche le modèle d'envoyer des arguments invalides ou mal formés.

</details>

2. ▢ Quand un modèle appelle un outil et que le harness reçoit l'appel, comment le harness sait-il s'il doit l'exécuter localement ou l'envoyer à un fournisseur ?

<details markdown="1"><summary>Vérifier</summary>

Vous devez l'indiquer au harness quand vous définissez l'outil : le marquer comme outil client (exécuté localement) ou comme outil serveur (le fournisseur s'en charge). Le modèle ne connaît jamais la différence ; il ne voit que le nom et le schéma.

</details>

## À savoir

### Les schémas comme garde-fou

Un schéma JSON remplit deux fonctions. D'abord, il documente ce que l'outil attend : noms de propriétés, types, et si chaque propriété est facultative ou obligatoire. Voici un exemple simple :

```json
{
  "type": "object",
  "properties": {
    "city": {"type": "string", "description": "The city name"},
    "units": {"type": "string", "enum": ["celsius", "fahrenheit"], "description": "Temperature scale"}
  },
  "required": ["city"]
}
```

Ce schéma dit : un outil prend un objet avec un `city` obligatoire (chaîne) et un `units` facultatif (soit « celsius », soit « fahrenheit »). Le modèle le lit et sait qu'il doit toujours fournir une ville mais peut omettre les unités.

Ensuite, un schéma agit comme une contrainte. Quand un modèle appelle l'outil, il ne peut envoyer que des valeurs conformes au schéma. Si le schéma dit que `units` doit être l'une de deux chaînes, le modèle ne peut pas envoyer « kelvin » ni un nombre. Des schémas stricts préviennent des catégories entières d'appels mal formés sans que le harness ait à les valider.

### Que se passe-t-il quand des champs obligatoires manquent

Si un modèle omet un champ obligatoire, l'API du fournisseur lève une erreur. La plupart des frameworks l'attrapent et renvoient l'erreur au modèle comme résultat d'outil : « Error: missing required field 'city' ». Le modèle a alors une chance de la corriger. Ce n'est pas un plantage ; c'est une partie normale de la boucle. Un schéma bien décrit réduit la fréquence de ce cas, car le modèle lit attentivement le schéma.

### Outils client et outils serveur

Un **outil client** est une fonction de votre propre code que le harness exécute. L'implémentation vous appartient :

```python
def get_weather(city: str, units: str = "celsius"):
    # Your code to fetch weather
    return f"18{units[0]}, partly cloudy"
```

Quand le modèle appelle `get_weather`, votre harness exécute votre fonction et collecte le résultat.

Un **outil serveur** est quelque chose que le fournisseur exécute sur sa propre infrastructure : une recherche web, l'exécution de code dans un sandbox, l'accès au système de fichiers ou un appel d'API hébergé. Vous définissez ce qu'il fait (nom et schéma), mais vous n'écrivez jamais l'implémentation. Le fournisseur l'exécute, collecte le résultat, et le harness le lit dans la réponse.

### Pourquoi la distinction compte

Quand vous dites « le modèle a appelé un outil », vous parlez de façon approximative. Le modèle n'exécute jamais rien. Il émet une requête structurée qui dit « exécute cet outil avec ces arguments ». Un harness reçoit cette requête et l'exécute, soit en :

1. Appelant une fonction que vous avez écrite (outil client), soit en
2. Demandant au fournisseur d'exécuter quelque chose d'hébergé (outil serveur), soit en
3. L'envoyant à un service tiers par le réseau.

Le modèle ne se soucie pas duquel il s'agit. La distinction est la vôtre : elle détermine où vit le code, comment vous l'écrivez et où les défaillances peuvent survenir.

### Pourquoi cela compte pour la boucle

Dans une boucle d'agent, le modèle génère des appels d'outils et le harness les exécute. Si un outil échoue, le résultat est un résultat d'outil qui porte une erreur, pas une exception qui plante la boucle. C'est vrai que l'outil soit client ou serveur :

- Un outil client renvoie une erreur parce que le réseau était coupé, que la requête à la base de données a échoué ou que votre logique de validation a rejeté l'entrée.
- Un outil serveur renvoie une erreur parce que le sandbox du fournisseur a dépassé le délai, que le code a levé une exception ou que la limite de débit de l'API a été atteinte.

Dans les deux cas, l'erreur n'est qu'un résultat d'outil de plus, et le modèle décide de la suite.

### Permissions et outils serveur

Un outil serveur ajoute une question : le modèle a-t-il la permission de l'appeler ? Si vous donnez à un modèle l'accès à l'exécution de code, à la lecture de fichiers ou au web, vous lui faites confiance (dans la limite que fixe le schéma) pour utiliser cette capacité en toute sécurité. C'est une décision de sécurité, pas une décision technique. Le schéma impose quels arguments l'outil peut recevoir, mais il ne peut pas empêcher le modèle d'utiliser la capacité pour quelque chose que vous n'aviez pas prévu. C'est pourquoi la conception du jeu d'outils compte, et pourquoi tous les outils ne conviennent pas à tous les agents.

## Pratique

1. ▢ Un schéma d'outil exige un champ `query` (chaîne) mais ne définit aucun champ `max_results`. Le modèle peut-il envoyer un argument `max_results` ? Pourquoi, ou pourquoi pas ?

<details markdown="1"><summary>Vérifier</summary>

Non, dans un schéma strict. Les définitions de schéma JSON peuvent autoriser ou interdire des propriétés supplémentaires. Si le schéma ne mentionne pas `max_results`, le modèle ne peut pas l'envoyer (ou le fournisseur le rejettera). Le schéma est exhaustif : seules les propriétés listées peuvent apparaître, sauf si le schéma autorise explicitement des propriétés supplémentaires.

</details>

2. ▢ Vous avez un outil client qui interroge une base de données. Le schéma dit que `user_id` est obligatoire, mais le modèle envoie un appel sans lui. Que se passe-t-il ensuite ?

<details markdown="1"><summary>Indice</summary>

Que fait le harness quand le fournisseur rejette un appel mal formé ?

</details>

<details markdown="1"><summary>Vérifier</summary>

Le fournisseur le rejette, et le harness renvoie l'erreur au modèle comme résultat d'outil : « Error: missing required field 'user_id' ». Le modèle lit cette erreur et a une chance de corriger l'appel. La boucle ne plante pas ; l'erreur est un résultat normal.

</details>

3. ▢ Quelle affirmation décrit le mieux ce qui se passe quand un modèle appelle un outil serveur plutôt qu'un outil client ?

    - a) Un outil serveur s'exécute sur votre infrastructure ; un outil client s'exécute sur celle du fournisseur
    - b) Le modèle envoie une requête pour l'outil ; le harness décide où l'exécuter
    - c) Un outil serveur termine toujours plus vite parce que le fournisseur l'optimise
    - d) Vous écrivez l'implémentation des deux, mais différemment

<details markdown="1"><summary>Vérifier</summary>

**b)** Le modèle émet la même requête structurée dans les deux cas. Le harness lit la définition de l'outil, détermine s'il est client ou serveur, et achemine l'exécution en conséquence. (a) est inversée : les outils client sont les vôtres, les outils serveur sont ceux du fournisseur. (c) est fausse : la vitesse dépend de l'implémentation, pas du fait que l'outil soit serveur ou client. (d) est en partie juste mais oublie que vous n'écrivez jamais les outils serveur, vous les définissez seulement.

</details>

4. ▢ Vous définissez un outil serveur « search_the_web » avec un schéma qui n'exige qu'un champ `query`. Le modèle l'appelle avec `query="python", limit=5`. Que fait le fournisseur ?

<details markdown="1"><summary>Vérifier</summary>

Soit il exécute l'appel avec la seule requête et ignore la limite, soit il rejette l'appel parce que le schéma n'autorise pas le champ supplémentaire `limit`. Le résultat dépend de ce que la définition du schéma autorise ou non comme propriétés supplémentaires. Si le schéma est strict (le comportement par défaut), le champ supplémentaire est une erreur.

</details>

## Exercices en situation réelle

- [ ] Trouvez ou écrivez un schéma d'outil pour une vraie tâche (recherche, récupération, calcul ou lecture). Marquez quels champs sont obligatoires, lesquels ont des contraintes (enums, longueur de chaîne, plages de nombres) et lesquels sont facultatifs. Réécrivez la description d'un champ pour qu'elle soit plus claire.
- [ ] Exécutez un agent ou écrivez un harness qui appelle un outil, et envoyez-lui volontairement un argument invalide (omettre un champ obligatoire, envoyer le mauvais type, envoyer une valeur hors d'un enum). Observez comment le fournisseur répond et comment votre harness ou framework le gère.
- [ ] Demain : concevez un outil client et un outil serveur pour la même tâche (par exemple « lister les fichiers »). Écrivez les schémas des deux. Expliquez un compromis lié à l'endroit où vit chaque outil.

## Pour aller plus loin

- [Doc : "Tool use with Claude", Claude Platform Docs](https://platform.claude.com/docs/en/agents-and-tools/tool-use/overview)
- [Ressources](../RESOURCES.md)

---

Ça ne passe pas ? Relisez la source primaire en haut de page, car cette leçon la condense et c'est dans la condensation que la compréhension s'échappe. Consultez le [glossaire](../GLOSSARY.md) pour tout terme qui vous a paru glissant.

Si c'est la leçon elle-même qui n'est pas claire plutôt que la matière, c'est un défaut : [ouvrez une issue](https://github.com/TokenCemetery/teach/issues).
