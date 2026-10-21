---
title: "15. NF4 et double quantification"
description: "Les deux idées que QLoRA a réellement apportées"
type: lesson
---

# Leçon 15. NF4 et double quantification

**Lien avec la mission :** Ce sont les deux idées qu'a apportées QLoRA. Les connaître, c'est ce qui sépare le fait d'avoir compris l'article du fait d'avoir lu le résumé.
**Source primaire :** [Article : "QLoRA: Efficient Finetuning of Quantized LLMs", Dettmers et al., arXiv:2305.14314](https://arxiv.org/abs/2305.14314)
**Prérequis :** [Leçon 14](0014-quantisation-from-first-principles.md)

## Échauffement

1. ▢ Pourquoi la quantification par blocs plutôt que par tenseur ?

<details markdown="1"><summary>Vérifier</summary>

Une valeur aberrante ne fixe l'échelle qu'au sein de son propre bloc, ce qui confine les dégâts à 64 ou 128 valeurs au lieu du tenseur entier.

</details>

2. ▢ Octets réels par paramètre pour des poids en 4 bits avec des échelles fp32 et des blocs de 64 ?

<details markdown="1"><summary>Vérifier</summary>

0.5625, donc 4.5 bits, avec 0.5 bit de pur surcoût de comptabilité.

</details>

3. ▢ Dans quelle précision se fait la multiplication de matrices, pour un base model en 4 bits ?

<details markdown="1"><summary>Vérifier</summary>

Une précision plus élevée, typiquement bf16. Les blocs sont déquantifiés à la volée et les copies déquantifiées jetées.

</details>

## À savoir

QLoRA a apporté trois choses : NF4, la double quantification et les paged optimizers. Les deux premières sont des idées de représentation et ce sont les intéressantes. La troisième est une atténuation d'ingénierie, traitée à la leçon 16.

### NF4, ou NormalFloat

Avec 4 bits, vous avez 16 niveaux. Où faut-il les placer ?

Un espacement uniforme, comme dans l'int4 simple, les place à intervalles égaux sur toute la plage. C'est optimal si les valeurs sont uniformément distribuées. **Les poids des réseaux de neurones ne sont pas uniformément distribués.** Ils sont à peu près centrés sur zéro et distribués normalement, donc la plupart des valeurs se regroupent près de zéro et peu se trouvent près des extrêmes.

Des niveaux uniformes gaspillent donc de la résolution : de nombreux niveaux se trouvent loin dans les queues où presque aucun poids ne vit, alors que la région dense près de zéro en reçoit trop peu.

La réponse de NF4 : placer les 16 niveaux aux **quantiles d'une loi normale standard**, pour que chaque niveau couvre la même quantité de *masse de probabilité* plutôt que la même quantité de plage. Les niveaux sont denses près de zéro et clairsemés dans les queues, ce qui correspond à l'endroit où se trouvent réellement les poids. L'article décrit cela comme optimal au sens de la théorie de l'information pour des données normalement distribuées de moyenne nulle.

Pour que cela fonctionne, chaque bloc doit d'abord être normalisé dans `[−1, 1]` en le divisant par son absmax, ce que la quantification par blocs stockait déjà. NF4 n'est donc pas un mécanisme supplémentaire ; c'est un meilleur choix des 16 niveaux dans le schéma de la leçon 14.

```text
int4:  levels evenly spaced        → resolution wasted in empty tails
nf4:   levels at normal quantiles  → resolution where the weights are
```

La conséquence est que NF4 bat int4 à largeur de bits égale, gratuitement. Pas de stockage supplémentaire, juste un meilleur dictionnaire de niveaux.

Deux limites honnêtes :

- Le gain dépend du fait que les poids soient réellement proches d'une loi normale. C'est généralement le cas, bloc par bloc, après le préentraînement. C'est une propriété empirique, pas une garantie.
- NF4 est un format de *poids*. Ce n'est pas le bon outil pour les activations, dont les distributions sont différentes et moins bien comportées.

### Double quantification

Revenons au surcoût de la leçon 14. Par paramètre, avec des blocs de 64 et des échelles fp32 :

```text
weights            0.5     bytes
scales   4/64  =   0.0625  bytes
                  ────────
                   0.5625  bytes  (4.5 bits)
```

Ces échelles ne sont elles-mêmes que des nombres dans un tenseur, et il y en a beaucoup. Alors quantifions-les aussi.

La double quantification prend les échelles de bloc en fp32, les regroupe (l'article utilise des blocs de 256), et les stocke sur 8 bits avec leur propre échelle de second niveau. Le résultat :

```text
first-level scales at 8 bits:   1/64      = 0.015625 bytes/param
second-level scales:            4/(64·256) ≈ 0.000244 bytes/param
weights:                                     0.5      bytes/param
                                            ──────────
                                             0.5159   bytes/param  (~4.13 bits)
```

L'article rapporte une économie d'environ **0.37 bit par paramètre** en moyenne, ce qui pour un modèle 65B représente environ 3 Go. C'est une vraie quantité de mémoire récupérée sur de la pure comptabilité.

![Trois barres de bits par paramètre. Le segment du poids sur quatre bits est identique dans les trois. Seul, il fait 4 bits ; avec des échelles de bloc en fp32, un segment d'un demi-bit s'ajoute, pour atteindre 4.5 ; avec la double quantification, ce segment se réduit à environ un huitième de bit, pour atteindre environ 4.13.](images/the-tax-not-the-payload.svg)

Notez la forme de l'idée : les constantes de quantification étaient une taxe fixe sur le schéma, et la double quantification a réduit la taxe plutôt que la charge utile.

Les barres disent la même chose sans l'arithmétique. Le segment gris a la même longueur trois fois, parce que rien n'a changé aux poids ; toute différence entre 4, 4.5 et 4.13 bits est le petit morceau accentué au bout. Un schéma qui aurait réduit la charge utile aurait déplacé le gris. C'est un gain petit, astucieux et entièrement mécanique, et c'est pourquoi QLoRA en 4 bits atterrit en pratique près de 4.1 bits par paramètre plutôt que 4.5.

### Le résultat sur la mémoire

Recalculons l'exemple de la leçon 6 avec un base model en 4 bits. Un modèle 7B avec un adapter de 20M paramètres :

| | Base model en bf16 | Base model en 4 bits |
|---|---|---|
| Poids de base gelés | 14.0 Go | ~3.6 Go |
| État de l'adapter (16 o/paramètre) | 0.32 Go | 0.32 Go |
| **Sous-total** | **14.3 Go** | **3.9 Go** |

Face aux 112 Go du full fine-tuning, le coût fixe du run avec adapter en 4 bits est inférieur à 4 Go. Les activations (leçon 7) sont maintenant de façon décisive le terme dominant, ce qui signifie que le gradient checkpointing compte ici plus que partout ailleurs dans l'espace de travail.

C'est le résultat qui a rendu QLoRA important : il a fait passer le fine-tuning de grands modèles des clusters à des appareils uniques.

### La configuration

```text
quant_config := {
    load_in_4bit: true,
    quant_type: "nf4",            # not "fp4"
    use_double_quant: true,       # the 0.37 bits/param saving
    compute_dtype: "bfloat16",    # storage is 4-bit; compute is not
}
```

Quatre réglages, chacun correspondant à quelque chose de cette leçon. `bnb_4bit_compute_dtype` est celui que les gens laissent à sa valeur par défaut et qu'il ne faut pas : c'est la précision dans laquelle les blocs déquantifiés sont multipliés, et le laisser en fp32 abandonne une grande partie du bénéfice de vitesse.

Comme toujours, confirmez ces noms dans la documentation de la version installée.

## Pratique

1. ▢ Pourquoi NF4 bat-il int4 à largeur de bits égale ?

<details markdown="1"><summary>Vérifier</summary>

Il place ses 16 niveaux aux quantiles d'une loi normale plutôt qu'à intervalles uniformes, donc la résolution est concentrée là où les poids se regroupent réellement, près de zéro, au lieu d'être dépensée sur des queues vides.

Même stockage, meilleur dictionnaire de niveaux. La précondition est de normaliser d'abord chaque bloc dans `[−1, 1]`, ce que la quantification par blocs fait déjà.

</details>

2. ▢ Que compresse exactement la double quantification, et combien économise-t-elle à peu près ?

<details markdown="1"><summary>Vérifier</summary>

Les échelles de bloc du premier niveau, c'est-à-dire les constantes de quantification plutôt que les poids. Elles sont stockées sur 8 bits par groupes de 256, avec une petite échelle de second niveau.

L'article rapporte environ 0.37 bit par paramètre en moyenne, soit environ 3 Go pour un modèle 65B. Elle fait passer le 4 bits avec surcoût d'environ 4.5 bits à environ 4.1.

</details>

3. ▢ Calculez la mémoire fixe totale pour un base model 13B en NF4 avec double quantification, plus un adapter de 30M.

<details markdown="1"><summary>Vérifier</summary>

Base : 13e9 × 0.5159 ≈ 6.7 Go. Adapter : 3e7 × 16 = 0.48 Go. Environ 7.2 Go fixes.

Comparez aux 26 Go d'un base model en bf16 plus l'adapter, et aux 208 Go du full fine-tuning. Les activations viennent ensuite s'ajouter aux 7.2 Go.

</details>

4. ▢ Quel composant de QLoRA économise le plus de mémoire ?

    - a) NF4 plutôt que la quantification uniforme int4 simple
    - b) Stocker le base model gelé en 4 bits plutôt qu'en bf16
    - c) La double quantification des échelles de bloc du premier niveau
    - d) Les paged optimizers qui déversent l'état pendant les pics de mémoire

<details markdown="1"><summary>Vérifier</summary>

**b)** Stocker le base model gelé en 4 bits plutôt qu'en bf16, une réduction de 4× sur le plus gros terme fixe.

NF4 améliore la qualité à stockage identique. La double quantification économise environ 0.37 bit par paramètre. Les paged optimizers évitent les plantages aux pics plutôt que d'abaisser l'utilisation en régime stable.

</details>

5. ▢ Pourquoi NF4 est-il inadapté à la quantification des activations ?

<details markdown="1"><summary>Vérifier</summary>

Le placement de ses niveaux découle de l'hypothèse que les valeurs sont de moyenne nulle et à peu près normales. Les poids après préentraînement s'y conforment raisonnablement ; les activations non, parce qu'elles portent des features aberrantes systématiques de grande amplitude, donc les quantiles normaux sont le mauvais dictionnaire pour elles.

</details>

6. ▢ Vous réglez `load_in_4bit=True` et laissez `bnb_4bit_compute_dtype` à sa valeur par défaut. À quoi avez-vous probablement renoncé ?

<details markdown="1"><summary>Vérifier</summary>

À la vitesse. Le stockage est toujours en 4 bits et la mémoire est toujours économisée, mais si le compute dtype vaut fp32 par défaut, chaque bloc déquantifié est multiplié en pleine précision, ce qui abandonne une grande partie de l'avantage de débit.

Réglez-le sur bf16 délibérément. La précision de stockage et la précision de calcul sont des décisions distinctes.

</details>

## Exercices en situation réelle

- [ ] Calculez sur papier les octets par paramètre en 4 bits avec et sans double quantification, avec des blocs de 64. Confirmez que la différence est proche de 0.37 bit.
- [ ] Chargez le même modèle en bf16 et en NF4, en mesurant la mémoire à chaque fois. Comparez à votre prédiction.
- [ ] Demain : générez le même prompt avec les deux, en décodage glouton, et lisez les sorties côte à côte. Formez une première impression du coût en qualité ; la leçon 17 en fait une mesure.

## Pour aller plus loin

- [Article : "QLoRA: Efficient Finetuning of Quantized LLMs", Dettmers et al., arXiv:2305.14314](https://arxiv.org/abs/2305.14314) : les sections 3 et 4 sont cette leçon
- [Doc : bitsandbytes quantization, Hugging Face Transformers](https://huggingface.co/docs/transformers/main/en/quantization/bitsandbytes)
- [Budget mémoire](../reference/memory-budget.md)

---

Ça ne passe pas ? Relisez la source primaire en haut de page, car cette leçon la condense et c'est dans la condensation que la compréhension s'échappe. Consultez le [glossaire](../GLOSSARY.md) pour tout terme qui vous a paru glissant.

Si c'est la leçon elle-même qui n'est pas claire plutôt que la matière, c'est un défaut : [ouvrez une issue](https://github.com/TokenCemetery/teach/issues).
