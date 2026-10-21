---
title: "20. Juger une nouvelle variante de PEFT"
description: "Six questions de triage, et la référence à battre"
type: lesson
---

# Leçon 20. Juger une nouvelle variante de PEFT

**Lien avec la mission :** « Lire un nouvel article sur PEFT et juger si le gain annoncé résisterait sur votre propre tâche » est le dernier point de la liste de la réussite. Cette leçon est cette compétence.
**Source primaire :** [Doc : LoRA variants, Hugging Face PEFT](https://huggingface.co/docs/peft/main/en/developer_guides/lora)
**Prérequis :** [Leçon 19](0019-when-dora-wins.md), [Leçon 17](0017-what-qlora-costs.md)

## Échauffement

1. ▢ Dans quelle condition DoRA est-il le bon choix plutôt que plus de rank ?

<details markdown="1"><summary>Vérifier</summary>

Quand le rank est maintenu bas par quelque chose que vous ne pouvez pas lever, généralement le risque de surapprentissage sur un petit dataset.

</details>

2. ▢ Que doit-il y avoir d'égal pour que deux runs soient comparables ?

<details markdown="1"><summary>Vérifier</summary>

Tout sauf l'unique variable testée : données, découpage, seed, rank, alpha, learning rate, schedule, pas.

</details>

3. ▢ Quels sont les deux coûts de qualité de la quantification, et comment les sépare-t-on ?

<details markdown="1"><summary>Vérifier</summary>

La dégradation du base model avant l'entraînement, et un entraînement d'adapter moins bon sur un base model dégradé. Isolez le premier en évaluant des base models quantifié et non quantifié sans adapter.

</details>

## À savoir

De nouvelles méthodes de fine-tuning efficaces en paramètres apparaissent constamment. La plupart ne comptent pas pour vous. La compétence, c'est le triage, pas l'enthousiasme.

### Le paysage, organisé selon ce qu'elles changent

Plutôt que de mémoriser des méthodes, apprenez les axes. Presque chaque variante modifie l'une de quatre choses.

**La mise à l'échelle.** rsLoRA ([arXiv:2312.03732](https://arxiv.org/abs/2312.03732)) remplace le diviseur `α/r` par `α/√r`, en soutenant que `α/r` amortit trop à rank élevé. Peu coûteux, un seul flag, utile quand on travaille à rank élevé.

**Les learning rates.** LoRA+ ([arXiv:2402.12354](https://arxiv.org/abs/2402.12354)) utilise un learning rate plus élevé pour `B` que pour `A`, en soutenant que les deux facteurs ne devraient pas partager un même taux étant donné leurs rôles et leurs échelles différents. Peu coûteux, et un réglage réellement différent de tout ce qui figure dans la leçon 9.

**L'initialisation.** Au lieu d'un `A` aléatoire et d'un `B` nul :

- **PiSSA** ([arXiv:2404.02948](https://arxiv.org/abs/2404.02948)) initialise à partir des composantes singulières principales de `W₀`, pour que l'adapter démarre aligné avec les directions dominantes du poids.
- **OLoRA** initialise via une décomposition QR de `W₀`.
- **LoftQ** ([arXiv:2310.08659](https://arxiv.org/abs/2310.08659)) initialise l'adapter pour compenser l'erreur de quantification, précisément pour le cadre de QLoRA.

Notez que toutes renoncent à la propriété d'initialisation à zéro de la leçon 9 : le modèle ne démarre plus identique au base model. C'est un échange délibéré, et c'est ce qu'il faut examiner de près.

**La structure.**

- **AdaLoRA** ([arXiv:2303.10512](https://arxiv.org/abs/2303.10512)) alloue le rank de façon adaptative entre les couches au lieu d'utiliser un même rank partout, au motif que les couches diffèrent par le degré d'adaptation dont elles ont besoin.
- **VeRA** ([arXiv:2310.11454](https://arxiv.org/abs/2310.11454)) partage des `A` et `B` aléatoires gelés entre les couches et n'entraîne que de petits vecteurs de mise à l'échelle, ce qui réduit drastiquement la taille de l'adapter.
- **DoRA** découple la magnitude de la direction, comme dans la leçon 18.

Dans PEFT, la plupart de ces méthodes sont un flag de configuration ou une valeur d'`init_lora_weights` plutôt qu'un chemin de code séparé, ce qui rend leur essai bon marché et fait de la lecture de la surface de configuration un moyen rapide de voir ce que la bibliothèque considère comme établi.

### Les questions de triage

Quand une nouvelle méthode apparaît, posez ces questions dans l'ordre. On peut généralement s'arrêter tôt.

**1. Que change-t-elle, sur lequel des quatre axes ?** Si vous ne pouvez pas y répondre d'après le résumé et une figure, soit l'article est mal écrit, soit vous n'êtes pas encore le public visé. Cette seule question filtre la plupart des choses.

**2. Quelle est la référence ?** La manière la plus courante de gonfler un résultat est une référence faible. Surveillez : LoRA à un rank choisi par les auteurs, des cibles limitées à l'attention alors que all-linear est la valeur par défaut moderne, un learning rate réglé pour la nouvelle méthode mais hérité pour la référence. **Une méthode qui bat un LoRA non réglé n'a pas montré qu'elle bat LoRA.**

**3. Le gain est-il plus grand que le bruit ?** Cherchez la variance sur les seeds ou des intervalles de confiance. Si l'article rapporte des chiffres isolés sans dispersion, et que le gain est d'un point ou deux, le résultat n'est pas encore distinguable du bruit. C'est extrêmement courant.

**4. Que coûte-t-elle ?** Temps par pas, complexité d'implémentation, fusion propre ou non, composition avec la quantification ou non, existence d'une implémentation en laquelle vous avez confiance. Un gain de 1 % pour un ralentissement de 30 % est un mauvais échange dans la plupart des cas.

**5. Son mécanisme s'applique-t-il à votre régime ?** Le bénéfice de DoRA se situe à bas rank. Celui de LoftQ, dans l'entraînement quantifié. Celui de rsLoRA, à rank élevé. Une méthode dont le mécanisme s'attaque à une contrainte que vous n'avez pas ne vous aidera pas, et c'est prévisible *avant* de lancer quoi que ce soit.

**6. Quelqu'un d'indépendant l'a-t-il reproduite ?** Les communautés de praticiens testent rapidement les méthodes sur de vraies tâches et sont directes sur ce qui ne se réplique pas. C'est souvent plus rapide et plus instructif que de lire l'article deux fois.

### Trois signaux d'alerte fiables

- **Des gains rapportés uniquement sur des benchmarks, jamais sur une tâche avec un déploiement.** Les benchmarks sont des substituts et sont très fortement optimisés contre.
- **Une comparaison à une référence LoRA limitée à l'attention** dans un article écrit après que all-linear est devenu la pratique standard. Soit mal informé, soit commode.
- **Aucun décompte des coûts.** Chaque méthode a un coût. Un article qui n'énonce pas le sien n'est pas franc avec vous, et l'omission est généralement la partie intéressante.

### La position par défaut

**LoRA à rank suffisant sur toutes les couches linéaires, avec un learning rate réglé, est une référence solide qu'il est difficile de battre de beaucoup.** C'est la conclusion pratique de la ligne de travaux « LoRA without regret », et ce devrait être votre point de départ et votre point de comparaison.

Une nouvelle variante doit battre *cela*, sur votre tâche, de plus que votre bruit de seeds, pour un coût inférieur à celui d'une augmentation du rank. La plupart ne franchissent pas la barre. Le savoir n'est pas du cynisme. C'est ce qui vous permet de consacrer votre attention aux quelques-unes qui la franchissent.

## Pratique

1. ▢ Nommez les quatre axes qu'une variante de PEFT peut modifier, avec un exemple chacun.

<details markdown="1"><summary>Vérifier</summary>

Mise à l'échelle (rsLoRA), learning rates (LoRA+), initialisation (PiSSA, OLoRA, LoftQ), structure (AdaLoRA, VeRA, DoRA).

Connaître les axes, c'est pouvoir classer une nouvelle méthode au premier regard au lieu de devoir l'apprendre de zéro.

</details>

2. ▢ Un article rapporte que sa méthode bat LoRA de 2.1 points, avec LoRA au rank 8 sur les seuls modules d'attention. Quelle est votre réserve ?

<details markdown="1"><summary>Vérifier</summary>

La référence est faible selon les standards actuels. Des cibles all-linear à rank plus élevé sont la valeur par défaut moderne et sont nettement plus fortes que l'attention seule au rank 8.

La méthode peut très bien battre cette référence faible et perdre quand même face à un LoRA correctement configuré. La comparaison telle que publiée ne vous le dit pas.

</details>

3. ▢ Quelle propriété d'un article sape le plus un gain annoncé de 1.5 point ?

    - a) L'absence de toute variance sur les seeds ou de tout intervalle rapporté
    - b) L'utilisation d'un modèle plus petit que celui que vous comptez utiliser
    - c) L'absence d'une implémentation de référence publiée
    - d) L'évaluation sur seulement trois tâches en aval distinctes

<details markdown="1"><summary>Vérifier</summary>

**a)** L'absence de toute variance sur les seeds ou de tout intervalle rapporté.

Sans dispersion, un gain de 1.5 point ne peut pas être distingué du bruit d'un run à l'autre, qui est souvent de cet ordre. Les autres sont de vraies limites mais ne sapent pas l'affirmation centrale comme le fait l'absence de variance.

</details>

4. ▢ LoftQ initialise l'adapter pour compenser l'erreur de quantification. Dans quel régime prédiriez-vous qu'il aide, et où prédiriez-vous qu'il ne fait rien ?

<details markdown="1"><summary>Vérifier</summary>

Il devrait aider quand on entraîne face à un base model quantifié, le plus visiblement avec une quantification agressive et sur des modèles plus petits où l'erreur de quantification est proportionnellement plus dommageable.

Il ne devrait rien faire pour un base model en bf16 non quantifié, parce qu'il n'y a pas d'erreur de quantification à compenser, donc le mécanisme n'a pas de prise.

</details>

5. ▢ PiSSA renonce à l'initialisation à zéro. Pourquoi cela compte-t-il, et que vérifieriez-vous ?

<details markdown="1"><summary>Vérifier</summary>

L'initialisation à zéro garantit que le modèle adapté démarre identique au base model, donc l'entraînement commence depuis des poids dont on sait qu'ils sont bons et toute dégradation est attribuable à l'entraînement.

Y renoncer signifie que le modèle démarre perturbé. Vérifiez l'instabilité précoce, et vérifiez si la perturbation a endommagé des capacités extérieures à votre tâche. Un jeu de régression (leçon 24) exécuté au pas zéro, avant l'entraînement, en est le test direct.

</details>

6. ▢ Quelle est la référence que toute nouvelle variante doit battre, et pourquoi est-elle difficile ?

<details markdown="1"><summary>Vérifier</summary>

LoRA à rank suffisant sur toutes les couches linéaires avec un learning rate réglé.

Elle est difficile parce qu'elle a déjà assez de capacité et de couverture pour approcher le full fine-tuning sur de nombreuses tâches supervisées. Quand la référence est proche d'un plafond, il reste peu de marge pour qu'un raffinement de mécanisme puisse la revendiquer.

</details>

## Exercices en situation réelle

- [ ] Choisissez une variante de cette leçon que vous n'avez pas utilisée. Appliquez les six questions de triage à son article et écrivez un verdict d'un paragraphe pour votre propre tâche.
- [ ] Lisez les options d'`init_lora_weights` dans votre version installée de PEFT. Associez chacune à une méthode et à un axe.
- [ ] Cherchez dans une communauté de praticiens des comptes rendus indépendants sur cette méthode. Comparez ce qu'ils ont constaté à ce que l'article affirmait.
- [ ] Demain : lancez la variante choisie face à une référence LoRA all-linear correctement réglée, trois seeds chacune. Notez si le gain survit.

## Pour aller plus loin

- [Doc : LoRA variants, Hugging Face PEFT](https://huggingface.co/docs/peft/main/en/developer_guides/lora)
- [Doc : "LoRA Without Regret", Hugging Face TRL](https://huggingface.co/docs/trl/main/en/lora_without_regret)
- [EleutherAI Blog](https://blog.eleuther.ai/) : un groupe qui publie ses résultats négatifs, ce qui est la moitié la plus rare de cette question
- [r/LocalLLaMA](https://www.reddit.com/r/LocalLLaMA/) : des comptes rendus de réplication rapides et directs

---

Ça ne passe pas ? Relisez la source primaire en haut de page, car cette leçon la condense et c'est dans la condensation que la compréhension s'échappe. Consultez le [glossaire](../GLOSSARY.md) pour tout terme qui vous a paru glissant.

Si c'est la leçon elle-même qui n'est pas claire plutôt que la matière, c'est un défaut : [ouvrez une issue](https://github.com/TokenCemetery/teach/issues).
