---
title: "12. Construction du prompt et budget de la fenêtre de contexte"
description: "Pourquoi les chunks récupérés se disputent un budget de fenêtre de contexte partagé, et pourquoi l'emplacement d'un chunk dans le prompt compte autant que le fait qu'il ait été récupéré"
type: lesson
---

# Leçon 12. Construction du prompt et budget de la fenêtre de contexte

**Lien avec la mission :** L'étape 7 ouvre la dernière partie de la mission : même un pipeline de récupération parfaitement diagnostiqué et bien réglé (étapes 1 à 6) peut encore décevoir l'utilisateur si les chunks récupérés sont mal assemblés dans un prompt, ce qui est un point de défaillance distinct de la récupération elle-même.
**Source primaire :** [Article : "Lost in the Middle: How Language Models Use Long Contexts", Liu et al., 2023](https://arxiv.org/abs/2307.03172)
**Prérequis :** [Leçon 11](0011-diagnosing-the-pipeline.md), [Chunk](../GLOSSARY.md)

## Échauffement

1. ▢ Quelle est la première étape à vérifier quand on diagnostique un contexte récupéré faux, et pourquoi la vérifie-t-on avant tout le reste ?

<details markdown="1"><summary>Vérifier</summary>

Le chunking : sortez le chunk qui aurait dû répondre à la requête et vérifiez si l'information pertinente existe de façon cohérente en un seul endroit. Si le chunking a coupé ou enfoui la réponse, aucune étape ultérieure (embedding, index, pondération hybride, reranking) ne peut récupérer ce qui n'a jamais reçu de représentation exploitable au départ.

</details>

2. ▢ Pourquoi diagnostiquer sur un petit ensemble de requêtes en échec connues est-il plus fiable que de déboguer un seul échec anecdotique ?

<details markdown="1"><summary>Vérifier</summary>

Une seule requête en échec peut échouer pour une raison inhabituelle et ponctuelle qui ne reflète pas un problème systémique. Mesurer recall@k et MRR sur un ensemble représentatif d'échecs révèle où se produit la plus grosse chute globale, ce qui désigne une étape qui perd systématiquement de l'information.

</details>

## À savoir

### Les chunks récupérés sont une ligne d'un budget partagé

Une fois les chunks récupérés et classés (étapes 1 à 6), ils doivent encore devenir une partie d'un vrai prompt : typiquement un message système ou d'instructions, les chunks récupérés eux-mêmes et la question de l'utilisateur, le tout dans une seule **fenêtre de contexte** finie. Cette fenêtre est un budget réel et partagé : les chunks récupérés se disputent la place avec le system prompt, l'éventuel historique de conversation et la question elle-même, pas seulement entre eux. Récupérer plus de chunks (un *k* plus grand) n'est pas gratuit, même quand chacun d'eux est réellement pertinent, puisque chacun consomme du budget de fenêtre de contexte que quelque chose d'autre, davantage d'historique de conversation, un system prompt plus long, pourrait utiliser autrement.

### Être dans le prompt ne veut pas dire être utilisé

La capacité d'un modèle à utiliser une information dépend de plus que du fait que cette information soit techniquement présente dans la fenêtre de contexte. Le constat « **lost in the middle** » de Liu et al. montre que les modèles exploitent bien plus fiablement l'information placée tout près du début ou de la fin d'un long contexte que celle enfouie au milieu, même quand l'information enfouie se trouve entièrement dans la limite de contexte annoncée du modèle. Un chunk très pertinent placé au milieu d'un long prompt bourré de chunks peut être effectivement invisible pour la génération, ce qui produit une réponse fausse ou incomplète qui ressemble à un échec de récupération mais n'en est pas un : le chunk a été correctement récupéré ; il n'était simplement pas positionné à un endroit où le modèle lit de façon fiable.

![Une courbe qui trace la fiabilité avec laquelle un modèle utilise une information récupérée selon l'endroit où cette information se situe dans le prompt assemblé. La courbe commence haut quand l'information est près du début, descend à son point le plus bas quand l'information est au milieu du contexte, puis remonte quand l'information est près de la fin, une forme de vallée plutôt qu'une ligne droite ou plate. Un chunk placé au milieu d'un long prompt bourré de chunks est le moins fiablement utilisé, alors qu'il est techniquement présent dans la fenêtre de contexte tout du long.](images/lost-in-the-middle.svg)

### La conséquence pratique pour l'assemblage d'un prompt

Deux conséquences en découlent directement. Premièrement, bourrer le contexte de nombreux chunks marginaux, de moindre pertinence, « par précaution » a un coût qui dépasse le budget de tokens : cela peut enfouir un chunk réellement bon au milieu du prompt, ce qui dégrade la réponse au lieu de seulement la renchérir. Deuxièmement, l'emplacement des chunks est un choix délibéré, pas un accident de l'ordre d'insertion : placer le chunk le plus pertinent (ou les chunks) près du début ou de la fin du contexte assemblé, plutôt que là où il a atterri après concaténation, détermine si la génération s'appuie réellement dessus.

## Pratique

1. ▢ Pourquoi le budget de la fenêtre de contexte est-il une préoccupation de la requête entière plutôt que quelque chose que la récupération peut raisonner seule ?

<details markdown="1"><summary>Vérifier</summary>

Les chunks récupérés partagent la fenêtre de contexte avec le system prompt, l'éventuel historique de conversation et la question de l'utilisateur ; le budget disponible pour les chunks récupérés dépend de ce que tout le reste de la requête utilise, et pas seulement de la qualité de la récupération.

</details>

2. ▢ Décrivez le phénomène « lost in the middle » et une implication pratique qu'il a pour construire un prompt RAG.

<details markdown="1"><summary>Vérifier</summary>

Les modèles exploitent bien plus fiablement l'information au début ou à la fin d'un long contexte que celle enfouie au milieu, même quand elle se trouve techniquement dans la fenêtre de contexte. Une implication pratique : le chunk récupéré le plus pertinent doit être placé près du début ou de la fin du prompt assemblé, et non laissé là où l'ordre de concaténation l'a mis, et remplir le prompt de nombreux chunks supplémentaires marginaux risque d'en enfouir un réellement utile au milieu.

</details>

3. ▢ Une équipe récupère les 20 premiers chunks « par précaution », les place par ordre de pertinence, mais les concatène de sorte que le chunk le plus pertinent se retrouve au milieu du contexte assemblé. La génération rate une réponse qui était pourtant présente dans ce chunk. Qu'est-ce qui a probablement mal tourné, et quelle est une correction ?

<details markdown="1"><summary>Indice</summary>

Demandez-vous s'il s'agit d'un échec de récupération ou de quelque chose qui se produit après la réussite de la récupération.

</details>

<details markdown="1"><summary>Vérifier</summary>

Ce n'est pas un échec de récupération : le bon chunk a été récupéré. C'est un échec de construction du prompt causé par l'effet lost-in-the-middle, puisque le chunk le plus pertinent s'est retrouvé positionné au milieu d'un long contexte, là où les modèles sont les moins fiables pour utiliser l'information. Une correction : réordonner le prompt assemblé pour que le chunk le plus pertinent se trouve près du début ou de la fin, ou réduire le nombre de chunks inclus pour que le bon ne soit pas enfoui parmi de nombreux chunks de moindre pertinence.

</details>

4. ▢ Pourquoi « la récupération a-t-elle trouvé le bon chunk » (la question de l'étape 6) et « le prompt assemblé a-t-il conduit le modèle à l'utiliser réellement » sont-ils des points de défaillance différents, même si tous deux peuvent produire le même symptôme (une réponse finale fausse) ?

<details markdown="1"><summary>Vérifier</summary>

La procédure de diagnostic de l'étape 6 vérifie si le bon chunk a été récupéré et classé assez haut pour atteindre la génération ; elle porte entièrement sur le pipeline jusqu'à ce point. Savoir si le modèle utilise réellement un chunk qui a atteint le prompt est une question distincte, régie par l'endroit où ce chunk se situe dans le contexte assemblé, ce que lost-in-the-middle montre comme comptant indépendamment de la qualité de la récupération. Une réponse fausse peut résulter de l'une ou l'autre défaillance, mais elles demandent des corrections différentes.

</details>

5. ▢ Laquelle de ces affirmations est vraie à propos du budget de la fenêtre de contexte et de l'emplacement des chunks dans un prompt RAG ?

    - a) Récupérer plus de chunks est toujours mieux, puisque plus de contexte ne peut qu'aider le modèle
    - b) Un chunk techniquement à l'intérieur de la fenêtre de contexte est garanti d'être utilisé de la même façon quel que soit son emplacement
    - c) Les chunks récupérés se disputent un budget partagé avec le reste de la requête, et l'endroit où un chunk est placé dans le prompt assemblé influe sur le fait que le modèle l'utilise réellement
    - d) Lost-in-the-middle n'affecte que de très longs documents, pas un prompt assemblé à partir de plusieurs chunks récupérés séparés

<details markdown="1"><summary>Vérifier</summary>

**c)** Le point du budget partagé comme celui de l'emplacement sont établis dans cette leçon. (a) est fausse : plus de chunks coûtent du budget et peuvent enfouir un bon chunk au milieu, ce qui nuit au lieu d'aider. (b) est fausse : c'est exactement ce que lost-in-the-middle réfute. (d) est fausse : l'effet porte sur la position au sein du contexte global, que ce contexte provienne d'un long document ou de plusieurs chunks concaténés.

</details>

## Exercices en situation réelle

- [ ] Pour un système RAG que vous exploitez ou prévoyez d'exploiter, vérifiez où se retrouve typiquement le chunk récupéré le plus pertinent dans le prompt assemblé, et si c'est un choix délibéré ou un accident de l'ordre de concaténation.
- [ ] Calculez quelle part du budget total de votre fenêtre de contexte est dépensée pour le system prompt et l'historique de conversation, par rapport aux chunks récupérés, pour une requête typique.
- [ ] Demain : essayez de réduire le nombre de chunks que vous récupérez pour une requête où la génération semble actuellement rater de l'information pertinente, et vérifiez si cela seul change la qualité de la réponse.

## Pour aller plus loin

- [Article : "Lost in the Middle: How Language Models Use Long Contexts", Liu et al., 2023](https://arxiv.org/abs/2307.03172)
- [Billet : "Evaluation Measures for Search and Recommender Systems", Pinecone](https://www.pinecone.io/learn/offline-evaluation/)
- [Ressources](../RESOURCES.md)

---

Ça ne passe pas ? Relisez la source primaire en haut de page, car cette leçon la condense et c'est dans la condensation que la compréhension s'échappe. Consultez le [glossaire](../GLOSSARY.md) pour tout terme qui vous a paru glissant.

Si c'est la leçon elle-même qui n'est pas claire plutôt que la matière, c'est un défaut : [ouvrez une issue](https://github.com/TokenCemetery/teach/issues).
