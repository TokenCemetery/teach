---
title: "Méthodes PTQ pour les poids"
description: "Arrondi au plus proche, GPTQ et AWQ côte à côte, et ce que fait le calibration set"
type: reference
---

# Méthodes PTQ pour les poids : comparaison de l'arrondi au plus proche, de GPTQ et d'AWQ

L'étape 4 condensée pour la consultation. La [leçon 9](../lessons/0009-round-to-nearest.md) couvre l'arrondi au plus proche (RTN), la [leçon 10](../lessons/0010-gptq.md) GPTQ, la [leçon 11](../lessons/0011-awq.md) AWQ, et la [leçon 12](../lessons/0012-the-calibration-set.md) le calibration set.

## Les trois méthodes côte à côte

| | Arrondi au plus proche | GPTQ | AWQ |
|---|---|---|---|
| Idée | Arrondir chaque poids à son niveau le plus proche | Arrondir les colonnes dans l'ordre, reporter chaque erreur sur les colonnes pas encore arrondies | Mettre à l'échelle supérieure les canaux d'entrée saillants avant l'arrondi, diviser l'activation par le même scale |
| Lit dans les données | Rien | Les entrées de couche, sommées en `H = 2 X X^T` | La grandeur moyenne d'activation par canal, plus les sorties de couche pour noter chaque `alpha` |
| Change les valeurs des poids | Non | Oui, chaque colonne suivante après chaque arrondi | Oui, par le scale par canal `s = s_X^alpha`, puis arrondit au plus proche |
| Objectif | L'erreur propre de chaque poids | `argmin \|\| W X - Ŵ X \|\|^2` par couche | La même erreur de sortie de couche, cherchée sur `alpha` dans [0, 1] |
| Rétropropagation | Aucune | Aucune | Aucune |
| Coût | Négligeable | Environ 4 heures de GPU pour 175B paramètres (article) | Une grille de 20 valeurs de `alpha` par couche (article) |
| Grille | Un scale par ligne ou par groupe | Fixée avant la boucle ; scale par groupe fixé quand la boucle atteint le groupe | Par groupe, 128 dans l'article |
| Risque principal | S'effondre en 3 bits avec des scales par ligne | Surajuste un calibration set petit ou inadapté | Mettre trop à l'échelle nuit aux canaux non saillants |

## Ce que chacune fait aux chiffres

| Perplexity WikiText-2 | 16 bits | RTN | GPTQ | AWQ |
|---|---|---|---|---|
| OPT-175B, 4 bits, grille par ligne | 8.34 | 10.54 | 8.37 | non rapporté là |
| OPT-175B, 3 bits, grille par ligne | 8.34 | 7,300 | 8.68 | non rapporté là |
| Llama-2 7B, 4 bits, groupes de 128 | 5.47 | 5.73 | 5.69 | 5.60 |
| Llama-2 7B, 3 bits, groupes de 128 | 5.47 | 6.66 | 6.43 | 6.24 |

Les deux premières lignes viennent de l'article GPTQ et les deux dernières de l'article AWQ. Les grilles et les modèles diffèrent, donc comparez au sein d'une ligne et la forme entre les lignes, pas les chiffres d'une ligne à l'autre. Chaque article évalue sa propre méthode face à l'autre, donc lisez les écarts comme les exécutions des auteurs.

## Pourquoi l'erreur se comporte ainsi

| Fait | Conséquence |
|---|---|
| Chaque bit retiré double à peu près le pas | L'erreur de l'arrondi au plus proche double à peu près par bit |
| Dans le jouet de la leçon 9, les rapports d'erreur égalent les rapports de pas : 127 / 7 = 18.1 de 8 à 4 bits, 7 / 3 = 2.3 de 4 à 3 | Les derniers bits sont les coûteux |
| L'arrondi au plus proche minimise l'erreur de chaque poids, pas celle de la sortie de la couche | 919 arrondis aléatoires sur 2000 le battent sur une couche jouet corrélée |
| Le gain de GPTQ vient d'entrées corrélées | Avec des entrées indépendantes, il disparaît presque (0.2680 contre 0.2595 dans le jouet) |
| Un poids saillant se repère par son activation, pas par sa taille | Sur OPT-6.7B en 3 bits, 1 % choisi par activation donne 11.39, par taille de poids 22.37, arrondi au plus proche simple 23.54 |
| Mettre un canal à l'échelle `s` réduit son erreur relative d'environ `1 / s` | Un `s` trop grand augmente le pas des autres canaux du groupe |

## Les trois changements de passage à l'échelle de GPTQ et l'act-order

| Changement | Ce qu'il corrige |
|---|---|
| Même ordre de colonnes pour chaque ligne | Une mise à jour de l'inverse par colonne sert toutes les lignes |
| Mises à jour paresseuses par lots, 128 colonnes à la fois | La mise à jour est limitée par la mémoire, donc la traiter par lots exploite le GPU |
| Amortissement de 1 % de la diagonale moyenne, plus un facteur de Cholesky | L'erreur numérique qui peut rendre l'inverse indéfini |
| Act-order (code des auteurs, pas l'article) : colonnes triées selon la diagonale de `H`, la plus grande d'abord | Corrige de mauvais résultats comme OPT-66B en 3 bits (14.16 à 9.95) ; peut exiger des changements d'inférence sauf si des groupes statiques sont utilisés |

## Ce que fait le calibration set

| | GPTQ | AWQ |
|---|---|---|
| Taille typique | Article : 128 segments de 2048 tokens, issus de C4 | AWQ à 16 séquences bat GPTQ à 192 sur OPT-6.7B, 3 bits (exécution des auteurs) |
| llm-compressor | 128 à 512 échantillons est typique, commencer à 128 à 256 | Même conseil ; son exemple utilise 256 |
| A besoin de plus de données parce que | Il estime toute une matrice de covariation des features | Il estime une moyenne par canal |
| Pénalité d'inadéquation, OPT-6.7B, 3 bits (article AWQ) | 2.3 à 4.9 de perplexity en pire | 0.5 à 0.6 en pire |

- L'arrondi au plus proche ne demande pas de données. GPTQ et AWQ ont besoin d'un calibration set. Aucun ne rétropropage à travers lui.
- Un calibration set n'est pas un jeu d'entraînement, et son domaine se voit dans le résultat.
- Faites correspondre le jeu à l'usage visé : du texte général pour un modèle généraliste, des données d'instructions pour un modèle d'instructions, du code pour un modèle de programmation (llm-compressor).
- Évaluez sur du texte held-out du domaine de calibration et sur du texte des autres domaines que vous servez. Un gain dans l'un et une perte dans l'autre signalent une inadéquation.
- Une perplexity mesurée sur le texte dont le jeu a été tiré est flattée. L'article GPTQ dit que ses résultats sur C4 ne sont pas entièrement zero-shot pour cette raison.
- Dans le jouet de la leçon 12, trop peu d'échantillons (64 pour 128 features) ont rendu GPTQ pire que l'arrondi au plus proche même dans le domaine.

## Avant de faire confiance à un checkpoint PTQ de poids

- Quelle méthode, quelle largeur en bits, et quelle taille de groupe ou quelle grille.
- Quel calibration set, combien d'échantillons, et de quelle longueur. Si la fiche de modèle ne le dit pas, c'est une lacune.
- Si la perplexity citée porte sur le domaine de calibration.
- Si une référence sans données avec la même grille a été mesurée sur la même évaluation.
- Pour GPTQ avec act-order et des groupes, s'il exige des changements d'inférence qui peuvent coûter de la vitesse, ou s'il a été fait avec des groupes statiques.
