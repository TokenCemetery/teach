---
title: "13. Licences et conditions d'utilisation"
description: "Ce que les conditions d'un fournisseur et la licence d'un modèle ouvert vous autorisent à faire de ses sorties"
type: lesson
---

# Leçon 13. Licences et conditions d'utilisation

**Lien avec la mission :** La mission vous demande de vérifier que l'usage d'un jeu de distillation est permis, ce qui veut dire lire les documents qui régissent l'enseignant avant de générer des données avec lui, et consigner ce que vous avez trouvé.
**Source primaire :** [Conditions : "Terms of Use", OpenAI](https://openai.com/policies/row-terms-of-use/)
**Prérequis :** [Leçon 12](0012-filtering-synthetic-data.md), [Leçon 10](0010-distilling-from-generated-data.md), [Données synthétiques](../GLOSSARY.md), [Enseignant](../GLOSSARY.md)

Cette leçon n'est pas un conseil juridique. Elle lit deux documents, cite ce qu'ils disent, et propose une liste de contrôle de ce qu'il faut chercher. Elle n'affirme rien sur ce qu'un document signifie pour votre cas, sur le caractère exécutoire d'une clause, ni sur le document qui vous régit. Les conditions d'utilisation et les licences changent sans version qu'une leçon puisse épingler, donc les citations ci-dessous portent la date à laquelle elles ont été lues, et vous devez lire le texte actuel avant de vous fier à l'une d'elles. Pour une vraie décision, demandez à un juriste.

## Échauffement

1. ▢ Les auteurs de phi-1 ont élagué leurs exercices par rapport à HumanEval avec des n-grammes, des embeddings et une correspondance d'AST. Pourquoi ne se sont-ils pas arrêtés au recouvrement de n-grammes ?

<details markdown="1"><summary>Vérifier</summary>

Un contrôle par 13-grammes n'a signalé que quatre questions, toutes des faux positifs, et était trop grossier pour trouver du code similaire, ils ont donc ajouté des comparaisons par embedding et par AST (leçon 12).

</details>

2. ▢ Les données d'Alpaca venaient de text-davinci-003 et son modèle a été affiné à partir de LLaMA 7B. De quelles deux choses dépend-il donc que quelqu'un d'autre possède ou contrôle ?

<details markdown="1"><summary>Vérifier</summary>

L'enseignant qui a généré les données (text-davinci-003 d'OpenAI, sous les conditions d'OpenAI) et le base model (LLaMA, sous sa licence). Les deux sont des entrées de l'élève, et chacune vient avec ses propres conditions (leçon 10).

</details>

3. ▢ Nommez le filtre qui vérifie par une règle une réponse générée par rapport à la vérité terrain, et une chose qu'il ne sait pas juger.

<details markdown="1"><summary>Vérifier</summary>

L'échantillonnage par rejet avec un vérificateur, où seuls les échantillons qui passent sont gardés. Il ne sait pas juger les réponses ouvertes ni le style, où il n'y a rien à quoi se référer (leçon 12).

</details>

## À savoir

### Trois documents, trois questions

Quand vous générez des données à partir d'un enseignant, vous pouvez être lié par jusqu'à trois types de documents différents, et chacun répond à une question différente.

| Document | Question à laquelle il répond |
|---|---|
| Les conditions d'utilisation du fournisseur, pour un modèle hébergé | Que puis-je faire des sorties que j'obtiens de ce service ? |
| La licence de poids ouverts | Que puis-je faire du modèle, et de ce qu'il produit ? |
| La licence ou les conditions des prompts et des données de départ | Que puis-je faire des entrées que je lui ai fournies, et des données que j'ai construites à partir d'elles ? |

Chacun est un texte distinct avec sa propre date et sa propre portée. Lire l'un ne vous dit pas ce que dit un autre.

### Ce que disent les conditions d'un fournisseur hébergé

Les Terms of Use d'OpenAI pour le reste du monde, en vigueur au 1er janvier 2026, listent des choses qu'un utilisateur ne peut pas faire. Parmi elles figure cette ligne, telle que lue quand ce parcours a été écrit, en octobre 2026. Le site bloque les lectures scriptées, revérifiez donc la page dans un navigateur :

> "Use Output to develop models that compete with OpenAI."

Trois choses à noter, et pas plus. La phrase se trouve dans la section des usages interdits. Elle parle de développer des modèles qui concurrencent OpenAI, ce qui est plus étroit que de développer n'importe quel modèle. Et c'est un seul document : votre usage peut relever d'une autre édition, ou d'un accord séparé pour une API ou un service d'entreprise, et cette leçon ne les a pas lus.

### Ce que dit une licence à poids ouverts

La Llama 3.1 Community License Agreement de Meta dit, à la section 1.b.i (Redistribution and Use), telle que lue dans le texte du dépôt le 17 octobre 2026 :

> "If you use the Llama Materials or any outputs or results of the Llama Materials to create, train, fine tune, or otherwise improve an AI model, which is distributed or made available, you shall also include “Llama” at the beginning of any such AI model name."

Le même paragraphe exige aussi que, si vous distribuez les Llama Materials, ou un produit ou service qui les contient, y compris un autre modèle d'IA, vous fournissiez une copie de l'accord et affichiez bien en évidence « Built with Llama » sur un site web associé, une interface utilisateur, un billet de blog, une page « à propos » ou la documentation du produit. Séparément, la licence dit que l'usage des Llama Materials doit respecter les lois applicables et une Acceptable Use Policy qu'elle incorpore par référence.

Le texte attache une condition sur le nom du modèle à l'usage des sorties de cette manière quand le modèle obtenu est distribué ou rendu disponible. Cette leçon n'affirme rien au-delà des mots. Les autres versions de Llama et les autres modèles ouverts ont leurs propres licences, et certaines disent des choses différentes.

### Comment un projet s'en est occupé

Les auteurs d'Alpaca déclarent que leur modèle est destiné uniquement à la recherche académique et que tout usage commercial est interdit, et donnent trois facteurs : LLaMA a une licence non commerciale, ils en héritent donc ; les données d'instruction viennent de text-davinci-003, dont les conditions d'utilisation, disent-ils, interdisent de développer des modèles concurrents d'OpenAI ; et ils n'avaient pas mis en place de mesures de sécurité adéquates. Ils écrivent aussi que leur démo était restreinte aux usages non commerciaux et aux usages qui respectent la licence de LLaMA (billet d'Alpaca, « Overview » et « Release decision »). Notez ce qu'ils ont fait : ils ont nommé chaque source de restriction et lié la publication à celle-ci. C'est l'habitude à copier, quoi que disent vos propres documents.

### Avant de générer : une liste de contrôle

Lisez et consignez, dans cet ordre :

1. **Les conditions de l'enseignant.** Trouvez le document exact qui s'applique à la manière dont vous accédez au modèle. Notez son nom, son URL, sa date ou sa version, et les phrases sur l'usage des sorties pour entraîner d'autres modèles.
2. **La licence des poids, si l'enseignant est ouvert.** Notez la version, toute clause sur l'entraînement à partir des sorties, toute exigence de nom ou d'attribution, et toute politique d'usage qu'elle incorpore.
3. **Les prompts et les données de départ.** La licence de tout ce que vous fournissez à l'enseignant, comme des tâches de départ, des documents ou du texte aspiré, régit les entrées. Vérifiez-la séparément de l'enseignant.
4. **Nom et attribution.** Si un document exige un préfixe de nom de modèle ou une mention de crédit, décidez-le maintenant, avant que le modèle ait un nom.
5. **Comment l'élève sera utilisé et partagé.** De nombreuses clauses dépendent du fait que le modèle soit distribué, rendu disponible ou vendu, et de ce avec quoi il est en concurrence. Écrivez votre usage prévu.
6. **La date.** Consignez quand vous avez lu chaque document et quand vous avez généré chaque lot, parce que les conditions en vigueur au moment de la génération peuvent différer des conditions d'aujourd'hui.

Gardez ce registre à côté du jeu de données, une ligne par source, pour que la question « d'où cela vient-il ? » ait une réponse un an plus tard. Un champ de provenance sur chaque exemple, nommant l'enseignant, la version et la date de génération, ne coûte presque rien.

```text
teacher: <name and version>
access: <hosted service or local weights>
terms read: <document, URL, date read, effective date if stated>
license: <name and version, if open weights>
prompt and seed data: <source, license>
naming or attribution duties: <list, or none found>
intended use: <research, internal, distributed, commercial>
generated on: <date range>
```

Les entrées `<...>` sont des champs à remplir pour votre propre projet.

### Ce que cette leçon ne peut pas vous dire

Elle ne peut pas dire si un projet donné enfreint une clause. Cela dépend du texte complet, des faits, de la juridiction et de ce que feront le fournisseur et le titulaire de la licence, dont rien ne figure dans une citation. Le but de l'exercice est plus étroit : vous assurer d'avoir lu les documents, de savoir ce qu'ils disent littéralement, et d'en avoir un enregistrement daté.

## Pratique

1. ▢ Une équipe fait un fine-tuning d'un modèle sur des sorties de Llama 3.1 et le rendra disponible. D'après le texte de licence cité, que doit-il en être du nom du nouveau modèle ?

    - a) Il doit se terminer par le mot « Llama »
    - b) Il ne doit contenir aucune mention de Llama
    - c) Il doit commencer par le mot « Llama »
    - d) Il doit être enregistré auprès du concédant

<details markdown="1"><summary>Vérifier</summary>

**c)** La phrase citée dit « Llama » au début du nom du modèle d'IA, pour un modèle qui est distribué ou rendu disponible. (a) inverse la position. (b) est le contraire de ce qu'elle dit. (d) ne figure pas dans le texte cité.

</details>

2. ▢ La ligne d'OpenAI citée porte sur l'usage de la sortie « to develop models that compete with OpenAI ». Un collègue la résume par « OpenAI interdit d'entraîner sur ses sorties ». Qu'est-ce qui ne va pas dans ce résumé ?

<details markdown="1"><summary>Vérifier</summary>

La ligne est plus étroite que le résumé : elle concerne le développement de modèles qui concurrencent OpenAI, pas tout développement de modèle. C'est aussi un seul document, d'une seule édition des conditions, à une seule date. Citez la phrase et sa date plutôt qu'une paraphrase, et vérifiez ce qui s'applique à votre voie d'accès. Savoir si votre projet est en concurrence est une question juridique à laquelle cette leçon ne répond pas.

</details>

3. ▢ Vous avez généré 200,000 exemples à partir d'un modèle hébergé en mars. En octobre, le fournisseur change ses conditions. Que faites-vous en premier ?

<details markdown="1"><summary>Vérifier</summary>

Lisez les nouvelles conditions et celles en vigueur quand vous avez généré les données, toutes deux depuis la page du fournisseur lui-même, et regardez ce que dit votre registre sur la version que vous avez lue. Le registre est la raison pour laquelle vous avez noté la date. Ce qui suit est une question juridique sur les conditions qui s'appliquent à des données déjà générées, portez-la donc à quelqu'un de qualifié, pas à une supposition.

</details>

4. ▢ Les auteurs d'Alpaca donnent trois facteurs pour une publication réservée à la recherche. Lequel dépend du choix de l'enseignant, et lequel du choix du base model de l'élève ?

<details markdown="1"><summary>Vérifier</summary>

Le facteur de l'enseignant est que les données viennent de text-davinci-003, dont les conditions interdisent de développer des modèles concurrents d'OpenAI. Le facteur du base model est que LLaMA a une licence non commerciale, qu'Alpaca hérite donc. Le troisième, l'absence de mesures de sécurité, ne concerne ni l'un ni l'autre.

</details>

5. ▢ Vos prompts de départ viennent d'un jeu de données public et votre enseignant est un modèle ouvert sous licence permissive. Nommez deux documents que vous devez encore lire avant de livrer l'élève.

<details markdown="1"><summary>Vérifier</summary>

La licence du jeu de données de départ, puisqu'elle régit les entrées, et la propre licence du modèle ouvert, pour toute clause sur l'entraînement à partir de ses sorties, le nom, l'attribution ou la politique d'usage. Vérifiez aussi la licence de tout base model dont part l'élève. Une licence permissive sur une source ne se transmet pas aux autres.

</details>

## Exercices en situation réelle

- [ ] Ouvrez les Terms of Use d'OpenAI et la licence Llama 3.1 et trouvez les phrases exactes citées ci-dessus. Copiez la date d'entrée en vigueur de chacune dans une note.
- [ ] Choisissez un jeu de données synthétiques public sur un hub que vous utilisez. Trouvez de quel enseignant il dit avoir été généré, et notez les conditions ou la licence de cet enseignant telles qu'indiquées sur la page du jeu de données.
- [ ] Demain : remplissez le registre de la liste de contrôle ci-dessus pour un jeu de données hypothétique issu d'un enseignant de votre choix, et marquez chaque champ que vous n'avez pas pu remplir à partir d'un document primaire.

## Pour aller plus loin

- [Séquences et données synthétiques](../reference/sequence-and-synthetic-data.md)
- [Conditions : "Terms of Use", OpenAI](https://openai.com/policies/row-terms-of-use/)
- [Licence : "Llama 3.1 Community License Agreement", Meta](https://github.com/meta-llama/llama-models/blob/main/models/llama3_1/LICENSE)
- [Billet : "Alpaca: A Strong, Replicable Instruction-Following Model", Stanford CRFM, 2023](https://crfm.stanford.edu/2023/03/13/alpaca.html)
- [Ressources](../RESOURCES.md)

---

Ça ne passe pas ? Relisez la source primaire en haut de page, car cette leçon la condense et c'est dans la condensation que la compréhension s'échappe. Consultez le [glossaire](../GLOSSARY.md) pour tout terme qui vous a paru glissant.

Si c'est la leçon elle-même qui n'est pas claire plutôt que la matière, c'est un défaut : [ouvrez une issue](https://github.com/TokenCemetery/teach/issues).
