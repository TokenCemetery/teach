---
title: "15. Précision mixte à grande échelle : bfloat16 et arrondi stochastique"
description: "Un format numérique avec la plage du fp32 mais moins de précision, et ce que coûte la mise à jour directe des paramètres dans ce format"
type: lesson
---

# Leçon 15. Précision mixte à grande échelle : bfloat16 et arrondi stochastique

**Lien avec la mission :** « Étant donné une courbe de loss, savoir dire si un pic est récupérable ou impose un redémarrage depuis un checkpoint antérieur » est la case « Terminée quand » de cette étape dans « Le fil conducteur », et elle commence par le format numérique dans lequel le run d'entraînement tourne. La leçon 16 couvre directement les pics de loss ; la leçon 17 couvre le schéma de learning rate.
**Source primaire :** [Article : "Scaling Language Models: Methods, Analysis & Insights from Training Gopher", Rae et al., 2021](https://arxiv.org/abs/2112.11446)
**Prérequis :** [Leçon 14](0014-combining-all-three-when-tensor-and-pipeline-parallelism-earn-their-cost.md)

## Échauffement

1. ▢ D'après Narayanan et al., pourquoi le parallélisme tensoriel est-il mieux confiné au sein d'un seul nœud, alors que le parallélisme de pipeline tolère d'être réparti entre des nœuds ?

<details markdown="1"><summary>Vérifier</summary>

Le parallélisme tensoriel a besoin d'un all-reduce coûteux pour chaque couche, qui exige l'interconnexion la plus rapide disponible pour rester efficace. Le parallélisme de pipeline ne fait que transmettre des activations entre une poignée de frontières d'étages, au moyen d'une communication point à point bien moins chère qui ne crée pas de goulot d'étranglement pour l'ensemble du calcul, même sur des liens plus lents et de plus longue distance.

</details>

## À savoir

### Deux manières de faire tenir un nombre de 32 bits dans 16 bits

Un nombre à virgule flottante de 32 bits (`fp32`) répartit ses bits entre une plage (l'exposant) et une précision (la mantisse, les chiffres après le premier un). Deux formats différents de 16 bits compressent cela différemment. `fp16` garde 10 bits de mantisse mais seulement 5 bits d'exposant, sacrifiant une grande partie de la plage du `fp32` pour gagner en précision dans une plage plus étroite ; un gradient très grand ou très petit peut le faire déborder par le haut ou par le bas (overflow ou underflow). **`bfloat16`** (`bf16`) fait l'échange inverse : il garde les 8 bits d'exposant complets du `fp32`, donc la même plage dynamique, mais seulement 7 bits de mantisse, donc il est plus grossier dans cette plage. Cette plage plus large est exactement la raison pour laquelle le bf16 tend à être plus indulgent pendant l'entraînement : les valeurs grandes ou minuscules qui apparaissent dans les gradients et les activations à grande échelle ont moins de chances de le faire déborder en premier lieu.

### Ce que Gopher en a réellement fait

Rae et al. décrivent l'usage du bfloat16 précisément pour réduire la mémoire et augmenter le débit d'entraînement, mais ils ne l'ont pas appliqué uniformément à toutes les tailles de modèle qu'ils ont entraînées. Les modèles de moins de 7,1 milliards de paramètres ont été entraînés en précision mixte ordinaire : paramètres `fp32`, activations `bf16`. Leurs deux plus grands modèles, le modèle de 7,1B et Gopher lui-même (280B), sont allés plus loin et ont utilisé `bf16` pour les paramètres autant que pour les activations, et pas seulement pour les activations.

### Pourquoi des paramètres en bf16 demandent un traitement particulier

Mettre à jour directement un paramètre stocké en bf16 se heurte à un problème que l'entraînement ordinaire en précision mixte évite en gardant une copie maître `fp32` : la précision plus grossière du bf16 signifie qu'une petite mise à jour peut tout simplement disparaître à l'arrondi, si elle est plus petite que l'écart entre des valeurs bf16 représentables adjacentes près de la valeur courante du paramètre. Rae et al. y répondent par l'**arrondi stochastique** : au lieu de toujours arrondir une valeur à la valeur bf16 représentable la plus proche (ce qui écarterait silencieusement les petites mises à jour de façon biaisée et dans un seul sens), l'arrondi stochastique arrondit vers le haut ou vers le bas avec une probabilité proportionnelle à la proximité de la vraie valeur de chaque voisin, si bien qu'une petite mise à jour n'est pas perdue d'emblée ; elle est préservée en moyenne sur de nombreux pas, même si l'arrondi d'un pas donné est aléatoire. Rae et al. sont explicites : cela ne résout pas complètement le problème, ils rapportent que l'arrondi stochastique ne retrouve pas entièrement les performances de l'entraînement ordinaire en précision mixte, une limite honnête plutôt qu'une solution propre.

## Pratique

1. ▢ Une valeur de gradient pendant l'entraînement est anormalement grande, assez grande pour poser un souci de débordement numérique. Quel format de 16 bits, fp16 ou bf16, est le plus susceptible de la représenter sans débordement, et pourquoi ?

<details markdown="1"><summary>Vérifier</summary>

Le bf16. Il garde les mêmes 8 bits d'exposant que le fp32, ce qui lui donne la même plage dynamique, si bien qu'une grande valeur qui déborderait la plage d'exposant plus étroite de 5 bits du fp16 a moins de chances de déborder le bf16.

</details>

2. ▢ Pourquoi mettre à jour un paramètre stocké directement en bf16 (au lieu de garder une copie maître fp32) risque-t-il de perdre silencieusement de petites mises à jour ?

<details markdown="1"><summary>Vérifier</summary>

Le bf16 n'a que 7 bits de mantisse, il est donc grossier dans sa plage ; une petite mise à jour peut être plus petite que l'écart entre des valeurs bf16 représentables adjacentes près de la valeur courante du paramètre, et l'arrondi à la valeur représentable la plus proche l'écarterait tout simplement.

</details>

3. ▢ Comment l'arrondi stochastique y répond-il, et quelle limite Rae et al. ont-ils rapportée même après l'avoir utilisé ?

<details markdown="1"><summary>Vérifier</summary>

L'arrondi stochastique arrondit vers le haut ou vers le bas avec une probabilité proportionnelle à la proximité de la vraie valeur de chaque valeur représentable voisine, au lieu de toujours arrondir à la plus proche, si bien qu'une petite mise à jour est préservée en moyenne sur de nombreux pas plutôt qu'écartée à chaque fois. Malgré cela, Rae et al. ont constaté qu'il ne retrouve pas entièrement les performances de l'entraînement ordinaire en précision mixte.

</details>

4. ▢ Parmi les tailles de modèle de Gopher, lesquelles ont utilisé bf16 pour les paramètres autant que pour les activations, d'après Rae et al. ?

    - a) Toutes les tailles de modèle qu'ils ont entraînées
    - b) Seulement les modèles de moins de 7,1 milliards de paramètres
    - c) Seulement le modèle de 7,1B et le modèle Gopher de 280B
    - d) Aucune ; le bf16 n'a été utilisé que pour les activations, à toutes les tailles

<details markdown="1"><summary>Vérifier</summary>

**c)** Seulement leurs deux plus grands modèles. Les modèles de moins de 7,1B utilisaient la précision mixte ordinaire, paramètres fp32 avec activations bf16, selon la description de (b), ce qui explique pourquoi (a) et (d) sont toutes deux fausses : des activations bf16 ont été utilisées largement, mais des paramètres bf16 ont été réservés aux deux plus grands modèles.

</details>

## Exercices en situation réelle

- [ ] Trouvez où un framework d'entraînement auquel vous avez accès expose un choix entre fp16 et bf16 (beaucoup proposent les deux comme options pour l'entraînement en précision mixte). Notez ce que dit la documentation sur le moment de préférer l'un à l'autre, et confrontez-le au raisonnement sur la plage dynamique de cette leçon.
- [ ] Cherchez la disposition exacte des bits (signe, exposant, mantisse) du fp32, du fp16 et du bf16, et vérifiez par vous-même que le bf16 et le fp32 partagent la même largeur d'exposant alors que le fp16 non.
- [ ] Demain : sans regarder la suite, écrivez une prédiction d'une phrase pour la leçon 16 : sachant que les deux plus grands modèles de Gopher ont demandé le traitement numérique le plus soigné, vous attendriez-vous à ce que les pics de loss et les instabilités deviennent plus ou moins fréquents à mesure que la taille du modèle croît, et pourquoi ?

## Pour aller plus loin

- [Article : "Scaling Language Models: Methods, Analysis & Insights from Training Gopher", Rae et al., 2021](https://arxiv.org/abs/2112.11446)
- [Ressources](../RESOURCES.md)

---

Ça ne passe pas ? Relisez la source primaire en haut de page, car cette leçon la condense et c'est dans la condensation que la compréhension s'échappe. Consultez le [glossaire](../GLOSSARY.md) pour tout terme qui vous a paru glissant.

Si c'est la leçon elle-même qui n'est pas claire plutôt que la matière, c'est un défaut : [ouvrez une issue](https://github.com/TokenCemetery/teach/issues).
