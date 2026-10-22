---
title: "Formats de nombres"
description: "Agencements de bits, plage et précision de chaque format, et arithmétique de la mémoire"
type: reference
---

# Formats de nombres : agencements, plage, précision et mémoire

L'étape 1 condensée pour la consultation. La [leçon 1](../lessons/0001-what-quantization-buys.md) couvre ce que la quantification apporte et l'arithmétique de la mémoire, la [leçon 2](../lessons/0002-floating-point-formats.md) les formats à virgule flottante fp32, fp16 et bf16, et la [leçon 3](../lessons/0003-low-bit-formats.md) le fp8, l'int8, l'int4 et les formats à échelle par bloc.

## Lire un agencement à virgule flottante

```text
value = (-1)^sign × 2^(e - bias) × (1 + m / 2^M)
```

- `e` est le champ d'exposant, `m` le champ de mantisse, `M` le nombre de bits de mantisse.
- Champ d'exposant entièrement à zéro : zéro et valeurs subnormales, `(m / 2^M) × 2^(1 - bias)`.
- Champ d'exposant entièrement à un : infini et NaN dans les formats IEEE. Le E4M3 fait exception et l'utilise pour des valeurs ordinaires.
- Les bits d'exposant fixent la plage. Les bits de mantisse fixent la précision. L'epsilon machine est `2^-M`.
- Entre `2^k` et `2^(k+1)`, les valeurs voisines sont distantes de `2^(k-M)` : l'écart double à chaque puissance de deux.

## Formats à virgule flottante

|Format|Bits|Signe / exposant / mantisse|Biais|Plus grande valeur finie|Plus petite valeur normale|Epsilon machine|
|---|---|---|---|---|---|---|
|fp32|32|1 / 8 / 23|127|3.4 × 10^38|1.2 × 10^-38|2^-23, environ 1.2 × 10^-7|
|fp16|16|1 / 5 / 10|15|65,504|6.1 × 10^-5|2^-10, environ 9.8 × 10^-4|
|bf16|16|1 / 8 / 7|127|3.4 × 10^38|1.2 × 10^-38|2^-7, environ 7.8 × 10^-3|
|fp8 E4M3|8|1 / 4 / 3|7|448|2^-6|2^-3|
|fp8 E5M2|8|1 / 5 / 2|15|57,344|2^-14|2^-2|
|FP4 E2M1|4|1 / 2 / 1|1|6|1|2^-1|

- Le fp16 a une plus petite valeur subnormale de `2^-24`. Les valeurs plus petites deviennent zéro.
- Plus petite valeur subnormale du E4M3 : `2^-9`, du E5M2 : `2^-16`.
- Le E4M3 n'a pas d'infinis et un seul motif de NaN (S.1111.111). Le E5M2 suit l'IEEE avec des infinis et des NaN.
- Le bf16 est du fp32 dont on a retiré les 16 bits de poids faible.
- Les lignes E4M3, E5M2 et fp16 viennent des sources des leçons. La ligne FP4 E2M1 est dérivée de son agencement et du biais de 1 utilisé à la leçon 3. L'epsilon machine des lignes fp8 et FP4 est `2^-M` par la même règle.

## Quel format pour quoi

|Format|Vu dans|Pourquoi|
|---|---|---|
|fp32|Référence, et accumulation en précision mixte|Large plage et espacement fin, 4 octets|
|fp16|Entraînement en précision mixte avec loss scaling|Espacement fin, plage étroite : l'entraînement a besoin de loss scaling|
|bf16|Entraînement sans loss scaling|Plage du fp32, donc pas de loss scaling, mantisse grossière|
|E4M3|Poids et activations|Espacement plus fin, plage jusqu'à 448|
|E5M2|Gradients|Plage plus large, espacement grossier|

## Grilles d'entiers

|Format|Niveaux|Plage|Espacement|
|---|---|---|---|
|int8|256|-128 à 127|1 partout|
|int4|16|-8 à 7|1 partout|

- Les valeurs sont `scale × entier`. Sans scale, une grille d'entiers ne contient que des nombres entiers.
- Une grille flottante apporte sa propre plage et a besoin d'un scale pour la placer. Une grille d'entiers tire toute sa plage du scale.
- Les valeurs plus petites qu'un demi-pas sont arrondies à zéro, avec ou sans scale.

## Formats à échelle par bloc

|Format|Taille de bloc|Scale|Élément|Bits de l'élément|Bits effectifs par poids|
|---|---|---|---|---|---|
|MXFP8|32|E8M0|E4M3 ou E5M2|8|8.25|
|MXFP6|32|E8M0|E2M3 ou E3M2|6|6.25|
|MXFP4|32|E8M0|E2M1|4|4.25|
|MXINT8|32|E8M0|int8|8|8.25|
|NVFP4|16|E4M3, plus un scale FP32 par tenseur|E2M1|4|4.5, scalaire par tenseur ignoré|

- La valeur de chaque élément est `X × P` : le scale partagé multiplié par l'élément stocké.
- Le E8M0 est un exposant seul, donc un scale MX est toujours une puissance de deux. Un scale E4M3 dans NVFP4 peut être un multiple fractionnaire.
- Les valeurs positives du E2M1 : 0, 0.5, 1, 1.5, 2, 3, 4, 6.
- Une grande valeur dans un bloc fixe le scale de tout le bloc et peut arrondir ses voisines à zéro.
- Les détails de NVFP4 viennent du billet de blog de NVIDIA lui-même, qui est de la documentation de fournisseur.

## Arithmétique de la mémoire

La mémoire des poids en GB vaut `paramètres en milliards × bits effectifs par poids / 8`. Les bits effectifs par poids sont la largeur en bits plus les bits de scale divisés par la taille de groupe ou de bloc.

|Format|Bits effectifs|Modèle 8B|Modèle 70B|
|---|---|---|---|
|fp32|32|32 GB|280 GB|
|fp16 ou bf16|16|16 GB|140 GB|
|fp8 ou int8|8|8 GB|70 GB|
|MXFP4|4.25|4.25 GB|environ 37.2 GB|
|NVFP4|4.5|4.5 GB|environ 39.4 GB|
|int4, scale de 16 bits par 128|4.125|4.125 GB|environ 36.1 GB|
|int4, scale de 16 bits par 32|4.5|4.5 GB|environ 39.4 GB|

- Ce sont les poids seuls. Le KV cache et les activations s'y ajoutent.
- Surcoût du scale : `bits du scale / taille de groupe`. Un scale de 16 bits par 128 poids ajoute 0.125 bit, et par 32 ajoute 0.5 bit.
