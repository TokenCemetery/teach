---
title: "19. Relire un rapport d'eval"
description: "Nommer précisément ce qui rendrait le chiffre d'un rapport d'eval peu fiable (contamination, juge non calibré, exécution unique sans estimation de variance, rang de classement tenant lieu de décision propre à la tâche), plutôt que dire que cela paraît léger"
type: lesson
---

# Leçon 19. Relire un rapport d'eval

**Lien avec la mission :** Chaque compétence de cet arc mène à une seule chose : un chiffre que vous pouvez défendre personnellement. Cette leçon est la compétence complémentaire : relire le chiffre de quelqu'un d'autre et dire, précisément et à partir de la matière, ce qui le rendrait peu fiable au lieu de simplement le sentir incomplet. Une suite d'evals, une fois construite, est une infrastructure partagée : d'autres équipes conditionnent leurs livraisons à son chiffre, et changer un juge, un seuil ou une métrique invalide en silence des décisions déjà prises. La relire et la maintenir honnêtement est un jugement de niveau senior.
**Source primaire :** [Article : "Judging LLM-as-a-Judge with MT-Bench and Chatbot Arena", Zheng et al., 2023](https://arxiv.org/abs/2306.05685)
**Prérequis :** [Leçon 6](0006-judge-bias-and-human-agreement.md), [Leçon 9](0009-statistical-significance-vs-noise.md), [Leçon 10](0010-defending-the-go-no-go-call.md), [Leçon 18](0018-public-benchmarks.md)

## Échauffement

1. ▢ Que signifie, pour un juge, être calibré, et quelle défaillance précise la leçon 5 décrit-elle comme compression des scores ?

<details markdown="1"><summary>Vérifier</summary>

Les scores d'un juge calibré suivent la qualité réelle de façon cohérente d'un exemple à l'autre. La compression des scores vers le plafond est une défaillance où le juge note presque tout haut quelles que soient les vraies différences de qualité, effaçant les distinctions qu'une eval existe pour repérer.

</details>

2. ▢ Quelle est la conclusion honnête quand un écart de score d'eval tombe dans le bruit estimé, et quelles sont deux façons d'obtenir une réponse plus nette ?

<details markdown="1"><summary>Vérifier</summary>

La conclusion honnête n'est pas « pas de différence » mais « pas encore assez de preuves pour trancher ». Deux façons de clarifier : exécuter l'eval sur plus d'exemples (ce qui réduit l'erreur standard), ou lancer un vrai test de significativité apparié sur les exemples précis où les variantes divergent.

</details>

3. ▢ Un rang de classement agrège des préférences issues de quelles trois choses qui pourraient ne pas correspondre à votre tâche réelle ?

<details markdown="1"><summary>Vérifier</summary>

Des utilisateurs, des tâches et des cas d'usage qui ne sont pas les vôtres. Une position dans un classement peut être un premier filtre raisonnable pour savoir quels modèles évaluer plus avant, mais elle échoue au test de l'OEC établi à la leçon 15 parce qu'elle n'est pas liée causalement à votre décision précise.

</details>

## À savoir

### La liste de relecture : ce qui rend un chiffre peu fiable

Quand quelqu'un présente un rapport d'eval ou la conception d'un harness, parcourez ces questions dans l'ordre. Là où le rapport n'a pas de réponse, vous avez trouvé la lacune qui rend le chiffre peu fiable, précisément et nommément.

**Étapes 1-2 : le jeu held-out est-il réellement held-out ?**

Demandez : quelle preuve y a-t-il que les données d'eval sont held-out ? L'équipe a-t-elle vérifié la contamination avec les techniques qu'a enseignées la leçon 2 (chaînes canari, tests de devinette de la suite de l'instance, ou les deux) ? Si le rapport dit « les données proviennent d'un benchmark public », il devrait aussi indiquer si la saturation (performance plafond sans amélioration réelle) ou la contamination de ce benchmark est déjà documentée dans la nature. Si ni contrôle de contamination ni preuve de saturation n'est rapporté, le chiffre pourrait être gonflé parce que le modèle a simplement déjà vu les questions à l'entraînement ou a mémorisé un benchmark très réglé au lieu d'apprendre la compétence sous-jacente.

**Étape 2 : la métrique correspond-elle réellement à la tâche ?**

Demandez : pourquoi cette métrique est-elle utilisée pour cette tâche ? Si le rapport dit « exactitude », est-ce la bonne métrique (la leçon 3 couvre les modes de défaillance de chaque métrique), ou le F1, BLEU, l'exécution de code ou autre chose mesurerait-il réellement ce qui compte ? Si une métrique sur mesure a été construite, quelle preuve montre qu'elle corrèle avec le vrai résultat (par exemple la préférence humaine, la réussite de la tâche) ? Un rapport qui ne justifie pas son choix de métrique a fait une supposition déguisée en décision.

**Étapes 3 et 6 : si un juge LLM est utilisé, est-il réellement digne de confiance ?**

Posez trois questions :

- **Conception :** quel est le prompt du juge, et qu'a fait l'équipe pour le calibrer avant de l'exécuter à grande échelle ? Le prompt donne-t-il au juge une réponse de référence quand il y en a une ? La leçon 5 enseigne la calibration ; si le rapport n'en parle pas, le juge souffre peut-être de compression des scores ou d'autres défaillances de non-calibration.
- **Contrôles de biais :** le juge a-t-il été vérifié pour le biais de position (la même comparaison par paires bascule-t-elle si l'on inverse l'ordre) ? Le biais de verbosité a-t-il été vérifié (le juge préfère-t-il la longueur indépendamment de la justesse) ? La leçon 6 couvre ces biais ; si le rapport ne mentionne pas leur vérification, ils pourraient gonfler ou dégonfler discrètement les chiffres.
- **Accord humain :** quel est le taux d'accord du juge avec des annotateurs humains sur un échantillon, et quel est l'accord humain-humain sur ce même échantillon ? Un juge à 82 % d'accord paraît faible jusqu'à ce qu'on apprenne que les annotateurs humains s'accordent à 80 % entre eux, auquel cas le juge fait à peu près aussi bien qu'un autre humain. Un rapport qui revendique un juge LLM sans le mesurer face au jugement humain revendique un raccourci sans preuve qu'il fonctionne.

**Étapes 5 et 9-10 : le chiffre est-il appuyé par une variance, ou est-ce une seule exécution ?**

Demandez : combien de fois l'eval a-t-elle été exécutée, et quelle était la dispersion ? Si c'est un chiffre unique issu d'une seule exécution à une température non nulle, le bruit de ce chiffre (l'erreur standard de la leçon 9) est invisible. L'équipe a-t-elle mesuré une erreur standard ou lancé un test de significativité pour confirmer que l'écart observé est nettement plus grand que le bruit ? Si une amélioration est rapportée sans estimation de significativité, impossible de dire s'il s'agit d'un vrai gain ou d'une coïncidence statistique. Vérifiez aussi si le seuil a été fixé avant ou après l'exécution de l'eval, et s'il respecte le plancher de bruit : la leçon 10 enseigne qu'un seuil plus serré que ce que l'eval sait réellement résoudre est un pile ou face déguisé en décision.

**Étape 11 : tient-il compte du coût et de la latence ?**

Demandez : l'amélioration rapportée est-elle pesée face à ce qu'elle coûte à servir ? Le coût par requête et le coût par token pour des modèles à répartition entrée/sortie différente : sont-ils mentionnés, et le gain de qualité vaut-il réellement ce multiplicateur ? Si la latence a été mesurée, était-ce la latence de queue (p95/p99) ou seulement une moyenne ? La leçon 17 enseigne pourquoi une moyenne inchangée peut cacher une queue nettement pire. Si le rapport dit « la qualité s'est améliorée » sans coût ni latence, la moitié du go/no-go manque.

**Étape 12 : s'appuie-t-il sur un classement plutôt que sur un chiffre propre à la tâche ?**

Demandez : le rapport dit-il « ce modèle est classé X sur MMLU » ou « ce modèle obtient X à notre eval propre à la tâche » ? S'il s'appuie sur un benchmark public ou une position de classement comme preuve, la leçon 18 établit qu'un rang de classement échoue au test dont un vrai OEC a besoin : il n'est pas lié causalement à votre décision précise, et il porte des vecteurs de manipulation documentés (divulgation sélective, biais de style). Un go/no-go propre à la tâche ne remplace pas une vérification de classement, mais une position de classement ne remplace pas non plus un chiffre propre à la tâche.

### La compétence précise : trancher si un juge LLM peut tenir lieu de go/no-go propre à la tâche

Cet espace de travail a présenté deux récits crédibles sur les juges LLM. Les leçons 5 et 6 ont enseigné à en construire et à en calibrer un, en les trouvant utiles pour les tâches ouvertes quand ils sont construits avec soin. Mais une question légitime plane sur toute l'idée : un juge LLM est-il jamais assez digne de confiance pour tenir lieu d'eval propre à la tâche, ou est-il fondamentalement limité au pré-tri ou à la vérification de corrélation ?

Le papier de Zheng et al. de 2023, « Judging LLM-as-a-Judge », établit que les juges LLM peuvent bien mesurer les préférences humaines sur des tâches ouvertes (sur Chatbot Arena, la préférence par paires d'un juge coïncide avec les préférences humaines environ 80 % du temps), et que c'est assez bon pour un usage pratique, mais *seulement* quand on recherche et corrige les biais connus (position, verbosité, auto-valorisation) et seulement quand on mesure le juge face à l'accord humain plutôt qu'à un étalon parfait imaginaire.

Voici le mouvement qu'un relecteur doit faire quand cette question surgit dans une vraie conversation. Deux personnes, citant toutes deux des sources plausibles, ne sont pas d'accord :

**L'ingénieur A dit :** « Zheng et al. ont montré que les juges fonctionnent ; nous pouvons utiliser un juge LLM pour notre go/no-go. »

**L'ingénieur B dit :** « Oui, mais Zheng a aussi montré que les juges sont biaisés ; une métrique propre à la tâche serait plus honnête. »

Les deux citent le même papier. La différence tient à ce qu'ils en extraient.

Le bon mouvement n'est pas de choisir un camp au feeling, ni de couper la poire en deux vaguement (« parfois les juges fonctionnent, faites appel à votre jugement »). Le bon mouvement est de retourner au papier et de vérifier si les conditions dans lesquelles les constats de Zheng tiennent correspondent à votre situation réelle :

**Les conditions de Zheng :** les juges ont été mesurés au mieux sur des comparaisons de préférence par paires pour des tâches ouvertes (écriture, raisonnement, créativité). La comparaison était par paires, pas ponctuelle (pas une notation sur une échelle de 1 à 10). Les annotateurs humains sur la même tâche étaient eux-mêmes à environ 80 % d'accord entre eux. Le juge a été vérifié pour plusieurs biais et des corrections ont été appliquées. Le verdict servait de filtre ou de signal, pas de go/no-go final non relu.

**Maintenant, votre situation :** votre tâche est-elle ouverte, ou a-t-elle une réponse nette ? Notez-vous par paires ou sur une échelle numérique ? Avez-vous mesuré l'accord humain sur cette tâche, et si oui, quel est-il ? Avez-vous vérifié le juge pour les biais de position, de verbosité et d'auto-valorisation, et avez-vous un plan pour les corriger s'ils sont trouvés ? La sortie de ce juge est-elle relue par un humain avant de piloter une décision, ou est-elle livrée seule ?

Si votre situation correspond de près aux conditions de Zheng, le constat « les juges fonctionnent quand ils sont construits avec soin » s'applique plus directement. Si votre tâche est nette, ou si vous n'avez pas mesuré l'accord humain dessus, ou si la sortie du juge pilote la décision sans relecture, le poids des preuves bascule. La compétence n'est pas « retenir ce que dit Zheng » mais « vérifier si les conditions qui ont rendu ce constat vrai s'appliquent à ce que vous construisez ».

### À quoi ressemble un bon jugement en relisant un rapport d'eval

> « Le rapport revendique une amélioration de 5 points sur leur eval propre à la tâche avec un juge LLM, mais il ne dit pas combien d'exécutions ont été faites ni quelle est l'erreur standard sur un jeu de 100 exemples à une baseline de 70 % ; cela fait probablement 4 à 5 points de bruit, ce qui signifie que cet écart peut être réel ou ne pas l'être. Ils n'ont pas non plus mentionné avoir vérifié le juge pour le biais de position ou de verbosité, et ils ne citent aucun accord humain sur les mêmes échantillons. Avant de livrer sur la base de ce chiffre, il nous faut l'erreur standard calculée, un contrôle de biais sur le juge, et une mesure face à l'accord humain sur un échantillon de la tâche. Ou, si la tâche est assez nette, ils auraient dû utiliser dès le départ une métrique propre à la tâche au lieu d'un juge. »

Rien là-dedans n'est un fait que vous avez cherché. C'est la forme du scepticisme pour lequel cet espace de travail existait.

### Maintenir une suite d'evals dont d'autres dépendent

Une fois que vous avez construit une eval, et que d'autres équipes conditionnent leurs livraisons à son chiffre, l'eval devient une infrastructure partagée. Changer le juge, la métrique, le seuil ou la forme du jeu de données invalide en silence des décisions déjà prises sur l'ancienne version. Une équipe qui a livré sur « l'eval version 1.0 a montré une amélioration de 3 points » a pris une décision liée à cette eval précise. Si vous changez le juge et relancez l'eval version 2.0, une amélioration de 2 points n'est pas comparable : l'équipe s'est fiée au chiffre de la version 1.0, pas de la 2.0.

Quand vous devez changer une suite d'evals :

**Option 1 : exécuter l'ancienne et la nouvelle côte à côte.** Avant de basculer, mesurez un échantillon raisonnable de modifications récentes de modèles face à l'ancien juge/métrique/version et face au nouveau. Cela donne aux autres équipes un facteur de conversion et leur montre l'impact. Un rapport qui dit « changer de juge modifie le score d'environ 2 points en moyenne sur ces modèles » est honnête et exploitable ; changer en silence est un changement cassant.

**Option 2 : versionner formellement l'eval.** Si vous publiez l'eval 2.0 avec un autre juge, une autre métrique ou un autre seuil, versionnez-la clairement. Les autres équipes peuvent continuer à exécuter la 1.0 jusqu'à ce qu'elles soient prêtes à migrer. Documentez ce qui a changé et pourquoi. C'est ainsi que font les outils stables.

**Option 3 : ne changez pas ce dont d'autres dépendent sans communication.** Si un changement est nécessaire (l'ancien juge est manifestement défaillant, une métrique n'est plus appropriée), annoncez-le. Laissez aux équipes le temps de réévaluer leurs dernières décisions de livraison sous les deux versions. Un changement surprise de ce que signifie une eval est la façon de perdre toute confiance dans les evals.

## Pratique

1. ▢ Une équipe rapporte qu'un modèle s'est amélioré de 6 points sur son eval, avec un juge LLM qui note des comparaisons par paires. Le rapport ne mentionne ni le nombre d'exemples de l'eval ni si le juge a été vérifié face à l'accord humain. Que devez-vous demander ?

<details markdown="1"><summary>Vérifier</summary>

Sur quelle taille de jeu d'eval ? L'erreur standard sur un jeu de 100 exemples à une baseline typique est de 4 à 5 points ; un écart de 6 points peut être réel ou du bruit. Avez-vous mesuré l'accord du juge avec des annotateurs humains sur un échantillon de votre tâche ? Sans connaître l'accord humain-humain, impossible de dire si un accord juge-humain de 80 % est bon ou médiocre. Aussi : le juge a-t-il été vérifié pour le biais de position (ordre inversé) et le biais de verbosité ? Sans ces contrôles, l'amélioration pourrait être un artefact de la façon dont le juge a été promptée.

</details>

2. ▢ Une équipe dit « nous utilisons un juge LLM parce que Zheng et al. ont montré que les juges fonctionnent ». Mais elle n'a pas mesuré l'accord humain sur sa propre tâche, et elle utilise une notation ponctuelle (échelle de 1 à 10), pas par paires. Le constat de Zheng s'applique-t-il directement à sa situation ?

<details markdown="1"><summary>Vérifier</summary>

Pas directement. Les constats de Zheng valaient pour des comparaisons de préférence par paires sur des tâches ouvertes où les annotateurs humains eux-mêmes étaient à 80 % d'accord. La notation ponctuelle est un autre mode (plus sujet aux problèmes d'interprétation de l'échelle), et sans mesurer l'accord humain sur cette tâche précise, on ne sait pas quelle baseline attendre du juge. L'équipe devrait soit mesurer l'accord humain sur sa tâche et y comparer le juge, soit passer à une métrique propre à la tâche si la tâche en admet une.

</details>

3. ▢ Votre suite d'evals tourne depuis six mois, et d'autres équipes conditionnent leurs livraisons à son chiffre. Vous voulez passer à un autre juge, mieux calibré, parce que l'actuel souffre de compression des scores. Que devez-vous faire avant de procéder au changement ?

<details markdown="1"><summary>Vérifier</summary>

Exécuter l'ancien et le nouveau juge côte à côte sur un échantillon de modifications récentes de modèles. Montrer aux autres équipes ce que le changement de juge fait aux scores sur lesquels elles s'appuyaient. Si c'est un décalage de 2 points en moyenne, elles peuvent recalibrer ; si c'est un décalage de 10 points, elles doivent réévaluer les décisions récentes. Annoncer clairement le changement, et envisager de versionner l'eval (eval 1.0 avec l'ancien juge, eval 2.0 avec le nouveau) pour que les autres équipes migrent à leur rythme au lieu d'être surprises par un changement cassant.

</details>

4. ▢ Un ingénieur qui relit un rapport d'eval dit : « Le rapport revendique une amélioration de 4 points sans test de significativité rapporté. Le jeu d'eval compte 50 exemples, et la baseline est à 68 %. Devons-nous faire confiance à ce chiffre ? » Quelle est votre analyse ?

<details markdown="1"><summary>Vérifier</summary>

Pas sans plus d'information. À N = 50 et p = 0,68, l'erreur standard vaut environ `sqrt(0.68 × 0.32 / 50) ≈ 0.066`, soit environ 6,6 points de pourcentage. Un écart de 4 points est bien dans le bruit ; il n'est pas nettement plus grand que ce que le seul échantillonnage pourrait produire. L'équipe devrait soit exécuter plus d'exemples (ce qui réduit l'erreur standard), soit lancer un test de significativité apparié sur les exemples précis où ils divergent, et non rapporter simplement l'écart brut en espérant qu'il paraisse convaincant.

</details>

5. ▢ Quelle situation vous rendrait le plus sceptique face à un rapport d'eval qui revendique une amélioration ?

    - a) L'eval utilise une métrique propre à la tâche, a exécuté 500 exemples, et rapporte une amélioration de 3 points avec un test de significativité apparié montrant p < 0.05
    - b) L'eval utilise un juge LLM, a exécuté 100 exemples, rapporte une amélioration de 4 points, mais ne mentionne ni si le juge a été vérifié pour le biais de position ni si l'accord humain a été mesuré
    - c) L'eval rapporte un classement sur MMLU comme principale preuve d'amélioration
    - d) L'eval a intégré le coût et la latence à côté de la qualité dans le go/no-go

<details markdown="1"><summary>Vérifier</summary>

**b)** et **c)** sont des signaux d'alerte. (b) est incomplet : sans contrôles de biais ni mesure de l'accord humain, impossible de dire si le juge est digne de confiance. (c) est un défaut de mesure de ce qui compte : un rang de classement n'est pas un signal de go/no-go propre à la tâche. (a) coche toutes les bonnes cases : une métrique propre à la tâche, un grand échantillon, un test de significativité. (d) est une bonne pratique, pas une raison d'être sceptique. Le signal d'alerte le plus fort est un rapport qui ne répond pas aux questions que cette leçon enseigne à poser.

</details>

## Exercices en situation réelle

- [ ] Trouvez un rapport d'eval issu de votre propre travail ou de celui d'un collègue. Appliquez-lui la liste de relecture de cette leçon. Notez quels points de la liste le rapport traite clairement et lesquels il laisse silencieux. Partagez la liste avec l'auteur du rapport.
- [ ] Sur la question « un juge LLM peut-il tenir lieu d'eval propre à la tâche », relisez vous-même le papier de Zheng et al. et identifiez les conditions précises dans lesquelles leurs constats tenaient. Notez : quelles caractéristiques de tâche, tailles d'échantillon et pratiques de mesure ont-ils utilisées ? Comment testeriez-vous si ces conditions s'appliquent à une situation nouvelle ?
- [ ] Demain : proposez un changement à une suite d'evals que vous maintenez ou connaissez. Notez comment vous communiqueriez ce changement aux autres équipes qui conditionnent leurs livraisons à elle, et si vous exécuteriez l'ancienne et la nouvelle côte à côte, versionneriez formellement, ou les deux.

## Pour aller plus loin

- [Article : "Judging LLM-as-a-Judge with MT-Bench and Chatbot Arena", Zheng et al., 2023](https://arxiv.org/abs/2306.05685)
- [Leçon 6 : Biais du juge et accord avec les humains](0006-judge-bias-and-human-agreement.md), pour les biais à vérifier
- [Leçon 10 : Défendre le go/no-go](0010-defending-the-go-no-go-call.md), pour ce qu'une défense complète doit citer
- [Leçon 18 : Benchmarks publics](0018-public-benchmarks.md), pour savoir pourquoi un rang de classement ne remplace pas une décision propre à la tâche
- [Ressources](../RESOURCES.md)

---

Ça ne passe pas ? Relisez la source primaire en haut de page, car cette leçon la condense et c'est dans la condensation que la compréhension s'échappe. Consultez le [glossaire](../GLOSSARY.md) pour tout terme qui vous a paru glissant.

Si c'est la leçon elle-même qui n'est pas claire plutôt que la matière, c'est un défaut : [ouvrez une issue](https://github.com/TokenCemetery/teach/issues).
