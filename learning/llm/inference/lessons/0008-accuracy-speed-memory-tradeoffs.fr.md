---
title: "8. Compromis entre précision, vitesse et mémoire"
description: "Pourquoi la mémoire, la vitesse et la précision n'évoluent pas ensemble quand un modèle est quantifié, et comment chacune se mesure réellement"
type: lesson
---

# Leçon 8. Compromis entre précision, vitesse et mémoire

**Lien avec la mission :** La leçon 7 a nommé les schémas ; cette leçon est ce qui rend un choix de quantification défendable, parce que la mémoire, la vitesse et la précision évoluent chacune d'une quantité différente et pour une raison différente quand les poids sont quantifiés.
**Source primaire :** [Article : "GPTQ: Accurate Post-Training Quantization for Generative Pre-trained Transformers", Frantar et al., 2023](https://arxiv.org/abs/2210.17323)
**Prérequis :** [Leçon 7](0007-quantization-schemes.md), [KV cache](../GLOSSARY.md)

## Échauffement

1. ▢ Pourquoi quantifier les poids d'un modèle accélère-t-il spécifiquement le decode, plutôt que l'inférence en général ?

<details markdown="1"><summary>Vérifier</summary>

Le decode est limité par la bande passante mémoire : chaque étape relit les poids depuis la mémoire, et les quantifier réduit le nombre d'octets que cette lecture doit déplacer. L'accélération vient d'un trafic mémoire moindre par étape, le goulot d'étranglement exact du decode.

</details>

2. ▢ Quelle fraction de la mémoire des poids fp16 la quantification int4 utilise-t-elle à peu près ?

<details markdown="1"><summary>Vérifier</summary>

Environ un quart, puisque int4 empaquette deux poids par octet là où fp16 utilisait deux octets par poids, une réduction de 8x : jusqu'au quart de fp16, puis divisée de nouveau par deux à partir de int8.

</details>

## À savoir

### La mémoire est la plus prévisible des trois

Les économies de mémoire de la quantification relèvent presque de l'arithmétique : int8 divise par deux l'empreinte de fp16, int4 la divise par quatre, parce que la largeur de bits fixe directement le nombre d'octets qu'occupe un poids. C'est le seul axe auquel les chiffres de la leçon 7 s'appliquent proprement, et cela tient quel que soit le schéma, arrondi naïf, GPTQ ou AWQ, qui a produit les poids quantifiés.

### La vitesse ne suit pas le même rapport

Un poids quantifié doit souvent être **déquantifié** vers une précision plus haute juste avant l'exécution de la multiplication matricielle proprement dite, parce que le matériel de multiplication attend cette précision. Quand cette étape de déquantification coûte elle-même du temps, l'accélération en temps réel peut rester bien en deçà du rapport d'économie de mémoire : un poids 4 fois plus petit ne signifie pas automatiquement une étape 4 fois plus rapide, seulement une étape avec 4 fois moins de données à déplacer avant le surcoût que la déquantification ajoute. Les piles de serving comblent cet écart avec des kernels écrits pour opérer directement sur le format quantifié, mais la part de l'accélération mémoire théorique qui survit dépend du kernel, pas seulement de la largeur de bits.

La vitesse ne profite pas non plus uniformément à toute une requête. Le decode, limité par la bande passante mémoire, est l'endroit où une empreinte de poids plus petite paie : moins à lire, moins de temps passé à le lire. Le prefill, limité par le calcul (leçon 3), passe son temps dans la multiplication matricielle elle-même, pas à lire des poids de façon répétée, si bien que la même quantification qui accélère sensiblement le decode rapporte bien moins au prefill, parfois presque rien.

### La précision demande un chiffre, pas une impression

Un modèle quantifié qui produit un texte à l'air plausible n'est pas la preuve que sa précision a tenu : la fluidité ne coûte rien, et un modèle peut paraître cohérent tout en étant mesurablement moins bon que son original fp16 sur la tâche qui compte. La perte de précision due à la quantification se mesure, typiquement par la **perplexité** (la façon dont le modèle prédit un texte held-out ; plus elle est haute, pire c'est) sur un jeu d'évaluation standard, ou par la variation de score sur un benchmark propre à la tâche dont la charge de travail se soucie réellement. L'évaluation de GPTQ rapporte exactement cela : la perplexité mesurée par rapport au modèle non quantifié à chaque largeur de bits, et non une lecture qualitative d'exemples de sorties.

### Les trois axes s'échangent, mais pas au même pas

Passer de fp16 à int8 coûte généralement très peu de précision mesurée pour une division par deux complète de la mémoire. Passer de int8 à int4 achète une autre grande réduction de mémoire mais coûte généralement de façon disproportionnée plus de précision que l'étape int8, ce qui est exactement la raison d'être de GPTQ et d'AWQ : maintenir ce coût de précision int4 aussi petit que l'arrondi naïf ne le peut pas. Aucun des trois axes n'est gratuit, et aucun n'évolue avec les autres selon un rapport fixe, c'est pourquoi un choix défendable a besoin d'un chiffre pour chacun, et non de l'hypothèse que réduire l'un réduit les autres de la même quantité.

## Pratique

1. ▢ Une équipe quantifie un modèle en int4 et constate qu'il écrit encore un texte fluide et cohérent sur une poignée de prompts manuels. Est-ce une preuve suffisante que la quantification n'a pas nui à la précision ? Pourquoi ou pourquoi pas ?

<details markdown="1"><summary>Vérifier</summary>

Non. La fluidité n'est pas la correction ni la précision sur la tâche ; un modèle peut paraître cohérent tout en obtenant un score mesurablement pire en perplexité ou sur un benchmark de tâche. La perte de précision demande un chiffre mesuré, comme la perplexité par rapport au modèle non quantifié ou un écart de score de benchmark, et non une lecture qualitative de quelques sorties.

</details>

2. ▢ Un modèle est quantifié en int4, ce qui donne une réduction théorique de la mémoire de 4x par rapport à fp16. Pourquoi l'accélération mesurée du decode pourrait-elle être inférieure à 4x ?

<details markdown="1"><summary>Indice</summary>

Pensez à ce qui doit arriver à un poids quantifié juste avant la multiplication matricielle qui l'utilise.

</details>

<details markdown="1"><summary>Vérifier</summary>

Les poids quantifiés doivent souvent être déquantifiés vers une précision plus haute juste avant l'exécution de la multiplication, puisque le matériel de multiplication attend cette précision. Si cette étape de déquantification prend elle-même du temps, elle grignote l'accélération que l'empreinte mémoire plus petite achèterait autrement, si bien que le gain en temps réel peut rester en deçà du rapport mémoire, à moins que le kernel opère directement sur le format quantifié.

</details>

3. ▢ La même quantification int4 est appliquée à la phase de prefill et à la phase de decode d'une requête. Quelle phase voit la plus grande accélération, et pourquoi ?

<details markdown="1"><summary>Vérifier</summary>

Le decode. Il est limité par la bande passante mémoire, donc lire une empreinte de poids plus petite raccourcit directement l'étape. Le prefill est limité par le calcul : son temps est dominé par la multiplication matricielle elle-même, pas par la lecture des poids, donc la même réduction de mémoire lui rapporte bien moins d'accélération, parfois presque aucune.

</details>

4. ▢ Laquelle de ces affirmations est vraie à propos du compromis entre précision, vitesse et mémoire en passant de int8 à int4 ?

    - a) Les trois s'améliorent du même facteur, puisque ce sont deux étapes de 8 bits en dessous de fp16
    - b) La mémoire s'améliore de façon prévisible, mais le gain de vitesse et le coût en précision n'évoluent pas avec elle selon le même rapport
    - c) La vitesse et la mémoire s'améliorent ensemble, et la précision n'est pas affectée en dessous de 8 bits
    - d) La perte de précision est fixe quelle que soit la largeur de bits, donc seuls la mémoire et la vitesse s'échangent

<details markdown="1"><summary>Vérifier</summary>

**b)** La mémoire baisse selon un rapport prévisible, arithmétique, mais l'accélération en temps réel dépend du surcoût de déquantification et de la prise en charge par les kernels, et le coût en précision croît généralement plus vite qu'à l'étape int8. (a) est fausse : de int8 à int4 il y a une seule étape, pas deux étapes égales de 8 bits, et les gains ne sont pas uniformes d'un axe à l'autre. (c) est fausse : la perte de précision en int4 est mesurable et généralement plus grande que celle de int8, ce qui est la raison d'être de GPTQ et d'AWQ. (d) est fausse : la perte de précision croît en général quand la largeur de bits baisse, elle n'est pas fixe.

</details>

## Exercices en situation réelle

- [ ] Trouvez un benchmark publié qui compare la perplexité ou le score de tâche d'un modèle en fp16, int8 et int4 (une fiche de modèle ou le tableau d'évaluation d'un article) et notez combien chaque étape a réellement coûté, dans les chiffres de l'article lui-même.
- [ ] Trouvez le benchmark ou la page de documentation de votre pile de serving qui compare le débit mesuré à différents niveaux de quantification, et comparez l'accélération rapportée au rapport de mémoire théorique que vous attendriez.
- [ ] Demain : pour une charge de travail que vous avez en tête, écrivez quelle métrique de précision vous vérifieriez réellement avant de livrer un modèle quantifié, et quelle baisse de score vous jugeriez acceptable.

## Pour aller plus loin

- [Article : "GPTQ: Accurate Post-Training Quantization for Generative Pre-trained Transformers", Frantar et al., 2023](https://arxiv.org/abs/2210.17323)
- [Doc : "Optimizing inference", Hugging Face Transformers](https://huggingface.co/docs/transformers/main/en/llm_optims)
- [Ressources](../RESOURCES.md)

---

Ça ne passe pas ? Relisez la source primaire en haut de page, car cette leçon la condense et c'est dans la condensation que la compréhension s'échappe. Consultez le [glossaire](../GLOSSARY.md) pour tout terme qui vous a paru glissant.

Si c'est la leçon elle-même qui n'est pas claire plutôt que la matière, c'est un défaut : [ouvrez une issue](https://github.com/TokenCemetery/teach/issues).
