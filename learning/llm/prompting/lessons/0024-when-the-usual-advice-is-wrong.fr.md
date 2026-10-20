---
title: "24. Quand le conseil habituel est faux"
description: "Reconnaître quand le conseil de prompting standard échoue pour un modèle ou une tâche donnés, et trancher le différend à partir de la source primaire"
type: lesson
---

# Leçon 24. Quand le conseil habituel est faux

**Lien avec la mission :** Le parcours se termine sur le fait qu'on vous fasse confiance pour trancher sur un prompt et l'expliquer à quelqu'un d'autre. Les conseils de prompting se propagent sous forme de slogans, et un slogan est vrai pour certains modèles, tâches et dates, et faux pour d'autres. Cette leçon est la méthode pour savoir lesquels.
**Source primaire :** [Article : "When 'A Helpful Assistant' Is Not Really Helpful: Personas in System Prompts Do Not Improve Performances of Large Language Models", Zheng et al., 2023](https://arxiv.org/abs/2311.10054)
**Prérequis :** [Leçon 2](0002-system-prompts-and-roles.md), [Leçon 7](0007-few-shot-biases.md), [Leçon 10](0010-prompting-reasoning-models.md), [Leçon 18](0018-a-regression-set-for-a-prompt.md), [Leçon 23](0023-reviewing-a-production-prompt.md)

## Échauffement

1. ▢ Pourquoi un prompt pour un modèle de raisonnement donne-t-il des objectifs et des contraintes plutôt que des étapes scénarisées ?

<details markdown="1"><summary>Vérifier</summary>

Le modèle produit déjà sa propre phase de raisonnement, donc un plan écrit à la main peut le contraindre à un chemin pire que celui qu'il trouverait lui-même. Dites ce que la réponse doit satisfaire et laissez-le décider comment y parvenir.

</details>

2. ▢ Que font surtout apprendre les exemples few-shot, selon la leçon 6 ?

<details markdown="1"><summary>Vérifier</summary>

Le format, l'espace des labels et la distribution des entrées, plus que la justesse de chaque label. C'est pourquoi les choisir pour la couverture et l'ordre compte plus que de peaufiner chacun.

</details>

3. ▢ Que contient un jeu de régression, et à quoi sert-il dans un différend sur un prompt ?

<details markdown="1"><summary>Vérifier</summary>

Des entrées construites surtout à partir de vrais échecs, chacune avec une vérification sur la sortie. Dans un différend, c'est le terrain neutre : deux personnes qui argumentent à partir de papiers différents peuvent toutes deux y exécuter leur prompt préféré et comparer.

</details>

## À savoir

### La méthode

Un slogan comme « donnez un rôle au modèle » ou « ajoutez toujours une instruction pas à pas » arrive sans ses conditions. La méthode pour décider s'il tient pour vous comporte quatre étapes :

1. **Trouvez la source primaire.** Pas le billet de blog qui la cite. L'article ou la documentation de l'éditeur, lus pour ce qui a réellement été mesuré.
2. **Vérifiez le modèle et la date.** Quels modèles, quelle tâche, quelle année. Un conseil de 2022 sur une famille de modèles peut ne pas décrire le modèle que vous appelez aujourd'hui, et le guide d'un éditeur décrit les modèles de cet éditeur.
3. **Vérifiez ce que couvre l'affirmation.** La précision sur des questions factuelles n'est pas le ton. Un résultat sur une courte classification n'est pas un résultat sur la rédaction.
4. **Testez sur votre jeu de régression.** Si la source et votre cas peuvent différer, le résultat qui tranche est le vôtre (leçons 18 et 19).

Les cas ci-dessous appliquent chacun cette méthode. Aucun ne dit que le conseil habituel est toujours faux. Chacun dit ce que la source primaire soutient.

### Cas 1 : « Donnez un rôle au modèle »

Le guide d'Anthropic dit : « Définir un rôle dans le system prompt concentre le comportement et le ton de Claude pour votre cas d'usage » ([Anthropic : prompting best practices](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/claude-prompting-best-practices)). Zheng et al. ont testé si les personas aident sur des tâches objectives. Ils ont constitué 162 rôles couvrant 6 types de relations interpersonnelles et 8 domaines d'expertise et testé 4 familles de LLM sur 2 410 questions factuelles. Leur constat : ajouter un persona « n'améliore pas la performance du modèle sur un éventail de questions par rapport à la situation de contrôle où aucun persona n'est ajouté ». Le genre, le type et le domaine du persona peuvent encore changer la précision, de sorte que l'effet « peut être largement aléatoire », et choisir automatiquement le meilleur persona pour une question n'était « souvent pas meilleur qu'une sélection au hasard ».

Les deux ne se contredisent pas, car ils affirment des choses différentes : le ton et le comportement d'un côté, la précision sur des questions factuelles de l'autre. La lecture qui survit aux deux : gardez un rôle quand vous voulez une voix ou un périmètre, n'attendez pas qu'il rende les faits plus exacts, et quand quelqu'un dit qu'un persona « améliore la précision », demandez le test. Les modèles de l'article sont ceux de 2023, donc la partie datée de la réponse est « pour ces modèles et ces questions ».

### Cas 2 : « Think step by step »

La formule vient du résultat de raisonnement zero-shot (Kojima et al., 2022, listé dans les [Ressources](../RESOURCES.md)), qui précède les modèles dotés de thinking intégré. Pour un modèle qui réfléchit avant de répondre, le guide actuel d'Anthropic recommande l'habitude inverse : « Un prompt comme "think thoroughly" produit souvent un meilleur raisonnement qu'un plan pas à pas écrit à la main », et pour plusieurs modèles nommés, il dit de s'appuyer sur le thinking intégré, car un prompt qui demande au modèle d'écrire son raisonnement « peut être décliné ». Il ne garde le chain-of-thought manuel qu'en solution de repli quand le thinking est désactivé. La leçon 10 traite de la mécanique.

Le différend à trancher est donc « quel modèle, avec thinking activé ou désactivé ». La réponse vient de la documentation du modèle lui-même, datée, puis de votre jeu de régression.

### Cas 3 : « Criez les règles importantes »

L'emphase en majuscules est une façon courante d'insister sur une règle. Le guide d'Anthropic dit que les modèles plus récents sont « plus sensibles au system prompt que les modèles précédents », et que des prompts écrits pour réduire le sous-déclenchement « peuvent désormais sur-déclencher ». Son correctif : « atténuez tout langage agressif », donc là où vous auriez écrit « CRITICAL: You MUST use this tool when... », utilisez « Use this tool when... ». Le guide nomme Claude Opus 4.5 et Claude Opus 4.6 pour cela, et l'exemple porte sur l'usage d'outils.

Lisez la portée. L'affirmation concerne deux modèles nommés et le déclenchement d'outils, pas « les majuscules ne marchent jamais ». Un prompt écrit pour un modèle plus ancien et déplacé vers un plus récent est le cas où l'emphase héritée mérite d'être testée, avec la version simple comme comparaison. La leçon 23 liste la formulation emphatique comme un coût à interroger pour la même raison.

### Cas 4 : « Plus d'exemples, c'est mieux »

Le guide d'Anthropic recommande d'inclure 3 à 5 exemples et de les rendre pertinents, variés et structurés. Deux articles ajoutent ce qu'un nombre ne peut pas dire. Lu et al. montrent que « l'ordre dans lequel les échantillons sont fournis peut faire la différence entre une performance proche de l'état de l'art et une performance au niveau du hasard », que cela vaut « pour toutes les tailles de modèles », et qu'une bonne permutation pour un modèle n'est pas transférable à un autre. Sclar et al. constatent que la sensibilité au formatage « subsiste même lorsqu'on augmente... le nombre d'exemples few-shot ».

Le nombre n'est donc pas le levier que le slogan laisse entendre. Les mêmes exemples dans un autre ordre, ou dans un autre format, peuvent compter autant qu'en ajouter davantage, et un ordre réglé sur un modèle ne se reporte pas sur le suivant. Traitez l'ordre et le format comme des variables à tester, ce qui est la conclusion de la leçon 7, renforcée.

### Trancher dans une conversation

Deux ingénieurs citent le même article. Ne choisissez pas le plus sûr de lui, et ne coupez pas la poire en deux. Demandez quatre choses : le passage, les modèles et la date, ce qui a été mesuré, et une exécution sur le jeu de régression. Si l'affirmation et votre cas correspondent, la source s'applique. Sinon, la source n'est pas une preuve sur votre cas, et l'exécution l'est.

## Pratique

1. ▢ Un collègue dit « Zheng et al. ont prouvé que les rôles sont inutiles, donc supprimez la ligne de rôle de chaque system prompt. » Qu'est-ce que l'article soutient, et que feriez-vous ?

<details markdown="1"><summary>Vérifier</summary>

L'article rapporte qu'ajouter un persona n'a pas amélioré la performance sur 2 410 questions factuelles pour 4 familles de LLM, par rapport à l'absence de persona. Il ne mesure ni le ton ni le périmètre, et il rapporte que l'effet varie selon le persona, pas qu'il est nul dans tous les cas. « Inutile pour la précision factuelle sur ces modèles » est donc soutenu, et « supprimer partout » ne l'est pas. Exécutez le prompt avec et sans le rôle sur le jeu de régression et ne supprimez la ligne que là où les chiffres ne montrent rien, puisque la retirer économise aussi des tokens.

</details>

2. ▢ Vous héritez d'un prompt qui dit « CRITICAL: you MUST call the search tool before every answer », réglé sur un modèle plus ancien, et le modèle plus récent cherche maintenant pour des questions triviales. Quelle action suit la source ?

    - a) Tester une version simple « Use the search tool when » contre l'ancienne formulation
    - b) Ajouter une seconde règle en majuscules lui disant de ne pas chercher pour les questions triviales
    - c) Revenir au modèle plus ancien et garder la formulation telle quelle
    - d) Supprimer l'instruction et s'attendre à ce que le modèle plus récent déduise la politique

<details markdown="1"><summary>Vérifier</summary>

a). Le guide d'Anthropic décrit ce sur-déclenchement pour des modèles récents nommés et conseille d'atténuer le langage agressif, donc la formulation simple est la candidate, et le jeu de régression tranche. b) empile l'emphase sur l'emphase. c) jette le modèle plus récent. d) supprime une politique dont vous pouvez avoir besoin, sans test.

</details>

3. ▢ Un billet de blog dit « ajoutez "think step by step" à chaque prompt. » Vous utilisez un modèle avec thinking intégré activé. Donnez les deux premières vérifications que vous faites avant de toucher au prompt.

<details markdown="1"><summary>Vérifier</summary>

D'abord, trouvez le résultat d'origine et voyez quels modèles et quelle année il couvre : l'article sur le raisonnement zero-shot date de 2022, avant les modèles dotés de thinking intégré. Ensuite, lisez la documentation de votre modèle : le guide d'Anthropic recommande des instructions générales plutôt que des étapes prescrites quand le thinking est activé, et dit que demander un raisonnement écrit peut être décliné sur certains modèles nommés. Testez ensuite avec et sans la formule sur le jeu de régression, car le guide est le compte rendu d'un éditeur sur ses propres modèles.

</details>

4. ▢ Votre prompt a cinq exemples avec le label rare en dernier, et la précision change quand vous les mélangez. Quelle source l'a prédit, et qu'est-ce que cela change au conseil d'utiliser 3 à 5 exemples ?

<details markdown="1"><summary>Vérifier</summary>

Lu et al. montrent que l'ordre des exemples seul peut faire passer les résultats d'un niveau proche de l'état de l'art à un niveau proche du hasard, et qu'un bon ordre pour un modèle n'est pas transférable à un autre. Le conseil sur le nombre reste un point de départ, mais il ne suffit pas : l'ordre et le format font partie du comportement du prompt, donc consignez l'ordre qui a réussi et retestez-le quand le snapshot du modèle change (leçon 16).

</details>

5. ▢ Écrivez les trois questions que vous poseriez avant d'accepter « les personas améliorent la précision » lors d'une revue de conception, et le seul résultat qui trancherait pour votre produit.

<details markdown="1"><summary>Vérifier</summary>

Sur quels modèles et quelles questions cela a-t-il été mesuré ? La référence était-elle un prompt sans persona ? La mesure portait-elle sur la précision ou sur le ton ? Ce qui tranche pour votre produit est une comparaison appariée sur votre jeu de régression du prompt avec et sans le persona, la différence étant jugée face au bruit d'une exécution à l'autre (leçon 19). Une source qui ne correspond à aucune de vos conditions est du contexte, pas une preuve.

</details>

## Exercices en situation réelle

- [ ] Choisissez un conseil de prompting que vous suivez sans en connaître la source et remontez-le jusqu'à un article ou un document d'éditeur. Écrivez les modèles, la date et ce qui a été mesuré.
- [ ] Prenez un persona ou une instruction emphatique dans un prompt que vous maintenez et écrivez la comparaison de deux prompts qui le testerait, même si vous ne l'exécutez pas encore.
- [ ] Demain : exécutez cette comparaison sur un jeu de régression, ou esquissez-en cinq cas, et consignez le résultat dans les notes de modification du prompt.

## Pour aller plus loin

- [Liste de contrôle de relecture d'un prompt](../reference/prompt-review-checklist.md)
- [Article : "When 'A Helpful Assistant' Is Not Really Helpful: Personas in System Prompts Do Not Improve Performances of Large Language Models", Zheng et al., 2023](https://arxiv.org/abs/2311.10054)
- [Doc : "Prompting best practices", Claude Platform Docs](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/claude-prompting-best-practices)
- [Article : "Fantastically Ordered Prompts and Where to Find Them", Lu et al., 2021](https://arxiv.org/abs/2104.08786)
- [Ressources](../RESOURCES.md)

---

C'est la fin du parcours, et l'habitude pour laquelle il a été construit est celle de cette leçon : un prompt est une affirmation sur un modèle, donc trouvez d'où vient l'affirmation, vérifiez ce qu'elle couvrait, et testez-la sur vos propres cas avant de la défendre devant qui que ce soit.

Ça ne passe pas ? Relisez la source primaire en haut de page, car cette leçon la condense et c'est dans la condensation que la compréhension s'échappe. Consultez le [glossaire](../GLOSSARY.md) pour tout terme qui vous a paru glissant.

Si c'est la leçon elle-même qui n'est pas claire plutôt que la matière, c'est un défaut : [ouvrez une issue](https://github.com/TokenCemetery/teach/issues).
