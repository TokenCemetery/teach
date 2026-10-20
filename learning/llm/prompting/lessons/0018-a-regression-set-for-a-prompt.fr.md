---
title: "18. Un jeu de régression pour un prompt"
description: "Construire le petit ensemble de cas qu'une modification de prompt ne doit pas casser, en partant de vrais échecs"
type: lesson
---

# Leçon 18. Un jeu de régression pour un prompt

**Lien avec la mission :** Une modification de prompt est une affirmation, et un jeu de régression permet de la vérifier en quelques secondes au lieu de la juger d'après les trois sorties que vous avez lues par hasard.
**Source primaire :** [Billet : "Your AI Product Needs Evals", Hamel Husain](https://hamel.dev/blog/posts/evals/)
**Prérequis :** [Leçon 17](0017-prompt-caching-and-layout.md), [Jeu de régression](../GLOSSARY.md)

## Échauffement

1. ▢ La leçon 11 demandait une sortie structurée puis la validait. Pourquoi une vérification de validité est-elle une première assertion naturelle dans un jeu de régression ?

<details markdown="1"><summary>Vérifier</summary>

Demander un format n'est pas une garantie, donc la sortie peut échouer à l'analyse. Une vérification d'analyse ou de schéma est peu coûteuse, ne demande aucun jugement et s'exécute sur chaque cas, ce qui en fait une assertion facile à écrire.

</details>

2. ▢ La leçon 5 a montré qu'une modification de formatage sans signification peut changer la précision. Qu'est-ce que cela implique sur la part d'une modification de prompt que vous pouvez juger en lisant quelques sorties ?

<details markdown="1"><summary>Vérifier</summary>

Très peu. Une petite modification peut déplacer les résultats d'une façon que quelques sorties ne montreront pas : la modification doit donc être exécutée sur un ensemble fixe de cas et comptée.

</details>

## À savoir

### Partir des échecs déjà vus

Un **jeu de régression** est un ensemble fixe d'entrées, chacune avec une vérification sur la sortie, qu'une modification de prompt ne doit pas casser. Les meilleurs premiers cas sont des cas réels. Le récit de Hamel Husain sur la construction d'évaluations pour un assistant immobilier dit d'examiner de façon critique les traces et les modes d'échec quand on ne trouve pas d'assertions, et que les centaines de tests unitaires de l'équipe étaient mis à jour en continu à partir de nouveaux échecs observés dans les données. Une trace est une conversation journalisée : journalisez-les donc, lisez-les, et transformez chaque échec en cas, avec l'entrée qui l'a déclenché et une vérification qui l'aurait détecté.

Le guide d'Anthropic sur la construction d'évaluations s'accorde sur la cible : concevoir des tests qui reflètent la distribution réelle de votre tâche, inclure des cas limites et automatiser la notation quand c'est possible. Vous n'avez pas besoin du trafic de production pour commencer. Hamel note que vous pouvez écrire des suppositions éclairées, ou faire générer des entrées par un modèle, et laisser les premiers utilisateurs les affiner.

### Une assertion par propriété

Hamel décrit les vérifications comme des assertions, du genre de celles qu'on écrirait avec pytest, gardées rapides et peu coûteuses pour pouvoir s'exécuter à chaque modification. Chaque cas liste les propriétés que sa sortie doit avoir.

```python
CASES = [
    {"id": "refund-not-complaint", "ticket": "I want my money back for order 118.",
     "must_contain": ["refund"], "must_not_contain": ["complaint"]},
    {"id": "no-uuid", "ticket": "Account 3f2b8c1e-9d4a-4e7b-a1c2-5d6e7f8a9b0c is locked.",
     "must_contain": [], "must_not_contain": ["3f2b8c1e"]},
]


def run_case(case: dict, call_model) -> bool:
    output = call_model(case["ticket"]).lower()
    has_all = all(s in output for s in case["must_contain"])
    has_none = not any(s in output for s in case["must_not_contain"])
    return has_all and has_none


def run_set(call_model) -> dict:
    return {c["id"]: run_case(c, call_model) for c in CASES}
```

`call_model` rend le gabarit de la leçon 15, appelle le modèle épinglé de la leçon 16 et renvoie son texte. L'exemple de Hamel lui-même est une vérification semblable que la sortie n'expose jamais un UUID interne. Lorsqu'une propriété ne peut pas être un test de chaîne ou d'expression régulière, un modèle peut la noter, et le parcours sur les évaluations traite de quand faire confiance à ce juge.

### Petit, croissant et pas tout ou rien

Commencez avec la poignée d'échecs que vous avez sous les yeux et ajoutez un cas chaque fois qu'un nouvel échec apparaît. L'ensemble doit être représentatif des échecs qui vous importent, pas grand pour le plaisir : le guide d'Anthropic privilégie le volume à la qualité notée à la main, et l'équipe de Hamel a atteint des centaines de tests, donc petit est un point de départ, pas un objectif. Deux mises en garde de Hamel : un bon ensemble contient des cas avec lesquels le modèle peine, et contrairement aux tests unitaires ordinaires, vous n'avez pas nécessairement besoin d'un taux de réussite de 100 %, car le taux de réussite est une décision produit sur les échecs que vous tolérez. Suivez les résultats par rapport à la version du prompt pour voir si vous progressez.

## Pratique

1. ▢ Un utilisateur signale que le résumeur qualifie une demande de remboursement de « complaint ». Transformez ce signalement en cas : que met-on dans l'entrée, et de quelles assertions la sortie a-t-elle besoin ?

<details markdown="1"><summary>Vérifier</summary>

L'entrée est le texte réel du ticket de l'utilisateur, ou un texte proche. Les assertions sont `must_contain` le mot refund et `must_not_contain` le mot complaint, comme dans le cas `refund-not-complaint` ci-dessus. Le cas échoue désormais avec l'ancien prompt et réussit avec la correction.

</details>

2. ▢ Prédisez `run_case` pour le cas `no-uuid` quand le modèle produit `Account 3f2b8c1e is locked.`

<details markdown="1"><summary>Indice</summary>

Comparez la sortie avec l'unique chaîne de `must_not_contain`.

</details>

<details markdown="1"><summary>Vérifier</summary>

Elle renvoie `False`. `must_contain` est vide, donc `has_all` est vrai, mais la sortie inclut `3f2b8c1e`, donc `has_none` est faux et le cas échoue. Le prompt a divulgué une partie de l'identifiant.

</details>

3. ▢ Un coéquipier veut attendre d'avoir 500 cas de qualité production avant de construire un jeu de régression. Qu'est-ce qui ne va pas là-dedans, d'après les sources de cette leçon ?

<details markdown="1"><summary>Vérifier</summary>

Rien ne s'exécute d'ici là, donc les modifications entre-temps sont jugées au feeling. Les sources décrivent des ensembles qui ont grandi à partir d'échecs observés, et Hamel dit qu'on peut partir de suppositions éclairées. Commencez avec les échecs que vous avez et ajoutez des cas à mesure que de nouveaux apparaissent.

</details>

4. ▢ Un jeu de régression réussit 18 cas sur 20 avec le prompt actuel et l'équipe exige 20 sur 20 avant toute livraison. Quel point de vue correspond à l'article de Hamel ?

    - a) Le taux de réussite est une décision produit sur les échecs tolérés, donc 100 % n'est pas exigé
    - b) Chaque cas doit réussir sinon l'ensemble ne vaut rien comme barrière avant la livraison
    - c) Les deux cas en échec devraient être supprimés pour que l'ensemble reflète le prompt actuel
    - d) Le taux de réussite compte moins que le nombre de cas, qu'il faudrait toujours minimiser

<details markdown="1"><summary>Vérifier</summary>

**a)** Hamel dit qu'on n'a pas nécessairement besoin d'un taux de réussite de 100 % et que cela dépend des échecs qu'on tolère. (b) est l'habitude ordinaire des tests unitaires à laquelle il l'oppose. (c) supprime les échecs dont l'ensemble est censé garder la mémoire. (d) est à l'envers : l'ensemble n'est petit que comme point de départ.

</details>

## Exercices en situation réelle

- [ ] Relevez cinq échecs réels ou réalistes d'un prompt que vous exécutez, dans les logs, les rapports de bogues ou vos propres tests, et écrivez chacun sous forme d'une entrée et d'une assertion.
- [ ] Mettez les cinq cas dans un fichier du dépôt à côté du prompt et exécutez-les avec le prompt actuel, en notant lesquels réussissent.
- [ ] Demain : la prochaine fois que le prompt donne une mauvaise sortie, ajoutez-la comme cas avant de corriger le prompt, et confirmez qu'elle échoue d'abord.

## Pour aller plus loin

- [Billet : "Your AI Product Needs Evals", Hamel Husain](https://hamel.dev/blog/posts/evals/)
- [Doc : "Define success criteria and build evaluations", Claude Platform Docs](https://platform.claude.com/docs/en/test-and-evaluate/develop-tests)
- [Prompts en production](../reference/prompts-in-production.md)
- [Ressources](../RESOURCES.md)

---

Ça ne passe pas ? Relisez la source primaire en haut de page, car cette leçon la condense et c'est dans la condensation que la compréhension s'échappe. Consultez le [glossaire](../GLOSSARY.md) pour tout terme qui vous a paru glissant.

Si c'est la leçon elle-même qui n'est pas claire plutôt que la matière, c'est un défaut : [ouvrez une issue](https://github.com/TokenCemetery/teach/issues).
