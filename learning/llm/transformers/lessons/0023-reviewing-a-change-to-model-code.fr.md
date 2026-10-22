---
title: "23. Relire une modification du code d'un modèle"
description: "Relire la modification du code d'un modèle faite par quelqu'un d'autre et nommer ce qu'elle casse ou ce qu'elle coûte, au lieu de se fier à sa description"
type: lesson
---

# Leçon 23. Relire une modification du code d'un modèle

**Lien avec la mission :** La mission s'arrête à lire ou modifier du vrai code de modèle sans que l'architecture soit une boîte noire ; la version senior de cette compétence est de relire la modification que quelqu'un d'autre y apporte et de nommer exactement ce qu'elle coûte, au lieu de se fier à la description.
**Source primaire :** [Article : "FlashAttention: Fast and Memory-Efficient Exact Attention with IO-Awareness", Dao et al., 2022](https://arxiv.org/abs/2205.14135), dont l'affirmation d'exactitude (leçon 22) sert de modèle à cette leçon pour vérifier toute affirmation du type « plus rapide, sortie inchangée ».
**Prérequis :** [0001-0003](0001-scaled-dot-product-attention.md) (attention), [0004-0011](0004-positional-encoding.md) (blocs transformer et entraînement), [0012](0012-reading-real-model-code.md) (lire du vrai code), [0014, 0017](0014-rotary-position-embeddings.md) (variantes modernes), [0022](0022-mixture-of-experts-and-flashattention.md) (exactitude)

## Échauffement

1. ▢ Une pull request affirme « attention lente remplacée par une attention rapide, sortie inchangée ». Que vérifiez-vous d'abord avant de croire cette affirmation ?

<details markdown="1"><summary>Vérifier</summary>

Si la sortie correspond réellement numériquement à l'originale, dans la tolérance de la virgule flottante. « Plus rapide » veut souvent dire discrètement « différent » : un calcul simplifié ou une approximation légèrement fausse. La leçon 22 a fait de l'exactitude le test de FlashAttention précisément parce que cette erreur est courante.

</details>

2. ▢ Un diff change l'encodage positionnel de sinusoïdal à rotatif. Pouvez-vous repérer ce que le changement coûte réellement sans lire l'article ?

<details markdown="1"><summary>Vérifier</summary>

Vous pouvez dériver ce que font les encodages rotatifs à partir de la leçon 14 : ils font tourner les vecteurs de requête et de clé avant l'exécution de l'attention, ce qui est la façon dont ils obtiennent des produits scalaires relatifs à la position. Vous pouvez ensuite vérifier si le diff implémente correctement cette rotation, et tester si les sorties correspondent à une référence (l'équation de la leçon 0001).

</details>

3. ▢ Une modification affirme une ablation : « nous avons supprimé le terme de weight decay et l'entraînement converge toujours ». Quelle question posez-vous ?

<details markdown="1"><summary>Vérifier</summary>

L'auteur l'a-t-il mesuré ? L'affirmation repose-t-elle sur son propre run d'entraînement, ou est-elle reprise du résumé d'un article par un billet de blog ? Une affirmation d'ablation n'est aussi solide que la mesure qui la soutient.

</details>

## À savoir

### La liste de contrôle de relecture : quatre choses dont toute modification de code de modèle a besoin

Un relecteur qui a construit un transformer à partir de tenseurs bruts a un avantage que la plupart des relecteurs de code n'ont pas : il peut vérifier une affirmation par rapport aux mathématiques réelles, et pas seulement juger si le code a l'air plausible.

**1. Les formes se propagent-elles correctement ?**

La convention récurrente de cet espace de travail : chaque opération conserve la longueur de séquence et la dimension d'embedding. Une modification de l'attention (le masque de la leçon 3, le RoPE de la leçon 14, la grouped-query de la leçon 17) ne doit pas casser cela. Vérifiez :

- L'entrée de l'opération : forme `(batch, seq_len, d_model)` ou des composantes comme `(batch, num_heads, seq_len, d_k)`.
- La sortie : la même forme en sortie.
- Deux couches en aval, un bug qui casse la forme se cache-t-il ? Un embedding rotatif qui tourne du mauvais angle peut ne pas échouer avant que les produits scalaires de l'attention deviennent absurdes. Vérifiez les tests en aval ou exécutez le modèle vers l'avant avec une entrée connue et vérifiez les formes intermédiaires.

**2. Si une accélération est affirmée, la sortie correspond-elle numériquement ?**

La leçon 22 l'a martelé : FlashAttention est exacte, pas approchée. Elle calcule la même équation, simplement en touchant la mémoire différemment. Elle **doit** produire la même `output` dans la tolérance de la virgule flottante.

Quand un diff affirme plus rapide sans changer la sortie :

- Exécutez le modèle avec l'ancien code et le nouveau code sur la même entrée aléatoire. Extrayez les sorties d'attention (ou la passe avant complète si le diff est en amont).
- Comparez les sorties élément par élément. Elles doivent correspondre à l'arrondi de la virgule flottante près, typiquement 1e-5 à 1e-4 selon la précision. Si elles diffèrent davantage, la modification n'est pas une accélération transparente ; c'est un calcul différent qui prétend être le même.

**3. La modification est-elle justifiée par rapport à ce qu'elle remplace ?**

Les leçons 5 (layer norm, résiduels) et 19 (initialisation, warmup, écrêtage du gradient, précision mixte) sont des garde-fous : chacun protège contre quelque chose sur quoi la boucle d'entraînement peut échouer sans lui. Une modification de l'un d'eux doit justifier pourquoi la nouvelle protection suffit.

Exemples :

- « Nous avons remplacé la layer norm par RMSNorm » : RMSNorm supprime le recentrage. Le code montre-t-il qu'elle est toujours utilisée en pre-norm (leçon 5), où le centrage était déjà facultatif ?
- « Nous avons augmenté le calendrier de learning rate » : la modification tient-elle compte de ce que protégeaient le warmup, l'écrêtage du gradient et la précision mixte ?
- « Nous avons supprimé l'écrêtage du gradient » : écrêtiez-vous réellement avant ? Êtes-vous prêt à voir des pics de loss ou de l'instabilité d'entraînement maintenant ?

Une erreur courante : copier une valeur de config d'un modèle sans rapport et ne rien ajuster d'autre. « Notre modèle a 7 milliards de paramètres ; je vais utiliser le learning rate d'un modèle de 70 milliards que j'ai trouvé. » Ce taux a été choisi pour 70 milliards ; le contexte, la taille de batch et la courbure de la loss sont tous différents.

La modification justifiée explique soit le rôle de l'ancien garde-fou et pourquoi la nouvelle configuration n'en a pas besoin, soit montre par une mesure que la boucle d'entraînement survit sans lui.

**4. Une affirmation d'ablation est-elle étayée par une vraie mesure ?**

La leçon 22 encore : « FlashAttention produit une sortie identique » est une affirmation que vous pouvez vérifier en comparant les sorties. Mais « nous avons supprimé le weight decay et l'entraînement est aussi bon » est différent : c'est un résultat expérimental qui affirme que le composant supprimé n'avait pas d'importance.

Vérifiez :

- L'auteur de la modification est-il celui qui l'a mesuré ? Mesuré sur quel jeu de données, avec quelle graine aléatoire, pendant combien de pas ?
- Ou l'affirmation est-elle reprise du résumé d'un article, d'un billet de blog ou de l'expérience de quelqu'un d'autre ? Si oui, le nouveau contexte (taille de votre modèle, architecture, learning rate, taille de batch, jeu de données) correspond-il à la mesure d'origine ?

Il est risqué d'accepter une vraie ablation sur la foi d'une autorité de seconde main, surtout si le nouveau run d'entraînement est coûteux et qu'un échec coûte cher.

### À quoi ressemble un bon jugement

En relisant une modification du code d'un modèle, un ingénieur senior nomme précisément ce qu'un choix coûte ou risque, au lieu de se fier à la description.

**Au lieu de :** « Ça me paraît faux. »

**Mieux :** « La leçon 14 dérive que RoPE fait tourner Q et K d'un angle proportionnel à `position * dimension_index`. Ce diff tourne de `position * constant`. C'est une fonction différente. La propriété de position relative de l'article ne tiendra pas. Je voudrais voir les sorties correspondre à une référence avant de fusionner. »

**Au lieu de :** « Ça devrait marcher. »

**Mieux :** « La modification supprime un facteur `residual_scale` avant de rajouter les résiduels. La leçon 7 a montré que mettre à l'échelle le résiduel est la façon dont la variante pre-norm de la leçon 5 évite le gonflement des activations dans les modèles profonds. Je voudrais voir les histogrammes de gradient à chaque couche pendant l'entraînement, ou comprendre pourquoi ce modèle précis reste stable sans mise à l'échelle. »

**Au lieu de :** « Les auteurs disent que ça marche. »

**Mieux :** « C'est RMSNorm, que l'article applique en pre-norm. Notre code utilise le post-norm (leçon 5). RMSNorm sans recentrage peut convenir en pre-norm mais être risquée en post-norm. Je voudrais soit passer en pre-norm, soit comparer soigneusement les sorties. »

La différence : nommer ce que fait la modification, ce contre quoi elle protège ou ce qu'elle coûte, et quelle preuve trancherait la question, au lieu de dire que la modification paraît juste ou fausse.

## Pratique

1. ▢ Un diff remplace l'encodage positionnel sinusoïdal (leçon 4) par du rotatif (leçon 14). Vos vérifications : quelles formes doivent toujours correspondre, et que testez-vous d'abord ?

<details markdown="1"><summary>Vérifier</summary>

Formes : entrée `(batch, seq_len, d_model)`, sortie `(batch, seq_len, d_model)`. La rotation s'applique à Q et K avant l'attention, donc les formes d'entrée de l'attention sont inchangées, et la forme de sortie de l'attention reste `(batch, seq_len, d_model)`.

À tester d'abord : comparez les sorties d'attention (ou les sorties de la passe avant complète si vous pouvez les isoler proprement) entre l'ancien code et le nouveau code sur la même entrée aléatoire. Si elles correspondent dans la tolérance, la modification préserve le calcul. Si elles diffèrent, quelque chose ne va pas dans les mathématiques de la rotation.

</details>

2. ▢ Une modification affirme « multi-head attention → grouped-query attention (leçon 17), aucune différence de sortie ». Quelle est votre première question sceptique ?

<details markdown="1"><summary>Vérifier</summary>

La grouped-query attention a moins de têtes de clés et de valeurs que de têtes de requêtes, donc le calcul est réellement différent, même s'il est conçu pour approcher la sortie de la multi-head. L'affirmation « aucune différence de sortie » est *trop forte*. La bonne affirmation est « la sortie est assez proche pour que la performance en aval n'en souffre pas ».

Votre vérification : les sorties correspondent-elles numériquement dans une tolérance que vous êtes prêt à accepter ? Probablement 1e-4 ou plus serré. Si elles correspondent exactement, quelque chose ne va probablement pas (vous avez peut-être laissé du code multi-head actif quelque part par accident).

</details>

3. ▢ Une PR supprime le warmup du learning rate (leçon 19). L'auteur dit « le modèle s'entraîne très bien sans ». Que demandez-vous ?

<details markdown="1"><summary>Vérifier</summary>

- L'ont-ils mesuré ? Sur ce modèle, ce jeu de données et cette taille de batch ?
- Quel était le learning rate avant que le warmup démarre ? Si le taux initial est plus bas maintenant, la modification ne supprime peut-être pas réellement le bénéfice du warmup.
- Ont-ils vu des pics de gradient, des couches mortes ou des courbes de loss inhabituelles ? Le warmup les prévient. Si l'auteur n'a pas regardé, il ne les a peut-être pas remarqués.

Sans mesure sur votre configuration réelle, vous devinez. Le warmup coûte peu ; s'il fonctionne, gardez-le.

</details>

4. ▢ Quelle affirmation sur la relecture d'une modification de code de modèle est la ligne directrice la plus utile ?

    - a) Se fier à la description de l'auteur et se concentrer plutôt sur le style du code
    - b) Rejeter toute modification de l'attention ou de la boucle d'entraînement ; elles sont trop risquées à modifier
    - c) Comparer numériquement les sorties quand la modification affirme ne pas altérer la sortie, et nommer le coût précis quand elle l'altère
    - d) Exiger que chaque résultat d'ablation soit étayé par un article publié avant de l'accepter

<details markdown="1"><summary>Vérifier</summary>

**c)** Comparer numériquement les sorties quand la modification affirme ne pas altérer la sortie, et nommer le coût précis quand elle l'altère.

(a) est la façon dont les erreurs partent en production. (b) est trop prudent ; tout l'intérêt est de pouvoir juger les modifications avec soin. (d) est trop strict ; une modification utile peut précéder la publication, et une mesure sur votre configuration réelle est souvent plus pertinente que la mesure d'un article à une autre échelle.

</details>

5. ▢ Un diff change le placement de RMSNorm (leçon 15) de post-norm à pre-norm (leçon 5). Que vérifiez-vous avant de croire la modification ?

<details markdown="1"><summary>Indice</summary>

Pensez à ce que la leçon 5 dit de la raison d'être de chaque placement, et à ce que RMSNorm supprime par rapport à la layer norm.

</details>

<details markdown="1"><summary>Vérifier</summary>

RMSNorm en pre-norm fonctionne parce que RMSNorm ne fait que remettre à l'échelle (elle ne recentre pas), et que le pre-norm n'a pas besoin du recentrage pour empêcher le gonflement des activations : le résiduel qui entre dans le bloc suivant n'est pas borné, mais la normalisation de *ce* bloc s'en charge.

Le post-norm est différent : la sortie résiduelle n'est pas bornée, et le recentrage de la layer norm était en partie ce qui gardait le post-norm stable. RMSNorm supprime le recentrage. Vous voudriez comparer des histogrammes d'activations (gonflent-elles ?), des courbes d'entraînement (montrent-elles de l'instabilité ?), ou au moins faire un test rapide pour voir si les courbes de loss correspondent avant et après la modification.

</details>

## Exercices en situation réelle

- [ ] La prochaine fois que vous verrez une PR qui modifie l'attention, l'encodage positionnel ou la boucle d'entraînement d'un modèle que vous utilisez ou comprenez, appliquez la liste de contrôle en quatre points ci-dessus : formes, exactitude de la sortie, justification par rapport à ce qui est remplacé, et mesure étayant toute affirmation d'ablation.
- [ ] Sur cette même PR (ou sur la vôtre), entraînez-vous à écrire un commentaire de relecture qui nomme précisément ce que fait une modification et ce qui trancherait la question, au lieu de dire qu'elle paraît juste ou fausse.
- [ ] Demain : si vous modifiez votre propre code de modèle cette semaine (changer une couche, remplacer une activation, ajuster un calendrier), vérifiez si vous pouvez contrôler numériquement les formes et les sorties avant de soumettre. Si vous ne le pouvez pas, vous ne savez pas vraiment si vous avez changé quelque chose d'important ou rien du tout.
- [ ] Demain : revenez sur une affirmation que vous avez entendue sur l'attention, les embeddings ou une astuce d'entraînement. Allez à l'article d'origine (pas au résumé du billet de blog) et vérifiez si l'affirmation correspond aux équations réelles de l'article. La leçon 12 a montré comment trouver du vrai code ; utilisez maintenant cette compétence et les articles des [Ressources](../RESOURCES.md) pour trancher un point contesté.

## Pour aller plus loin

- [Article : "RoFormer: Enhanced Transformer with Rotary Position Embedding"](https://arxiv.org/abs/2104.09864), Su et al. À utiliser pour : les mathématiques d'origine des embeddings rotatifs, afin de vérifier les affirmations par rapport à ce que dit réellement l'article.
- [Article : "GQA: Training Generalized Multi-Query Transformer Models from Multi-Head Checkpoints"](https://arxiv.org/abs/2305.13245), Ainslie et al. À utiliser pour : la conception de la grouped-query attention, afin de vérifier l'affirmation d'approximation et de comprendre quel compromis elle fait.
- [Article : "FlashAttention: Fast and Memory-Efficient Exact Attention with IO-Awareness"](https://arxiv.org/abs/2205.14135), Dao et al. À utiliser pour : confirmer que FlashAttention est exacte et non approchée, et voir comment ils le vérifient par rapport aux implémentations de référence.
- Revenez aux [leçons sur la boucle d'entraînement](0019-initialization-warmup-and-gradient-clipping.md) quand vous relisez des modifications du learning rate, de l'écrêtage du gradient ou de la précision mixte. Les sections « Pour aller plus loin » de ces leçons renvoient aux articles qui sont derrière chaque garde-fou.
- [Glossaire](../GLOSSARY.md) pour tout terme qui vous a paru glissant.
- [Ressources](../RESOURCES.md)

---

Ça ne passe pas ? Relisez la source primaire en haut de page, car cette leçon la condense et c'est dans la condensation que la compréhension s'échappe. Consultez le [glossaire](../GLOSSARY.md) pour tout terme qui vous a paru glissant.

Si c'est la leçon elle-même qui n'est pas claire plutôt que la matière, c'est un défaut : [ouvrez une issue](https://github.com/TokenCemetery/teach/issues).
