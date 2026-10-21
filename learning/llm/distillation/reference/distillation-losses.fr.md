---
title: "Loss de distillation"
description: "Soft targets, température, loss combinée, loss au niveau du token, KL directe et inverse, contrainte du tokenizer et coût du stockage des logits"
type: reference
---

# Loss de distillation : étapes 1 et 2 pour la consultation

Les étapes 1 et 2 condensées pour la consultation. Les [leçons 1 à 3](../lessons/0001-what-distillation-buys.md) couvrent les soft targets et la température, la [leçon 4](../lessons/0004-token-level-distillation.md) la loss au niveau du token, la [leçon 5](../lessons/0005-forward-and-reverse-kl.md) la direction de la divergence, la [leçon 6](../lessons/0006-the-tokenizer-constraint.md) la contrainte du tokenizer et la [leçon 7](../lessons/0007-distilling-during-pretraining.md) le coût de la distribution de l'enseignant à grande échelle.

## Soft targets et température

| Terme | Définition | Source |
|---|---|---|
| Soft targets | Les probabilités de l'enseignant sur chaque classe, utilisées comme cible à la place du hard label ou à côté de lui | Hinton et al., 2015, section 1 |
| Softmax avec température | q_i = exp(z_i / T) / sum_j exp(z_j / T). T = 1 est le softmax normal, un T plus élevé donne une distribution plus douce | Hinton et al., équation 1 |
| Où T est utilisé | Le même T élevé pour l'enseignant et l'élève pendant l'entraînement. L'élève tourne ensuite à T = 1 | Hinton et al., section 2 |
| Gradient à la température T | dC/dz_i = (1/T)(q_i - p_i). Pour un grand T et des logits centrés sur zéro, il vaut environ (1/(N T^2))(z_i - v_i), donc faire correspondre les logits est un cas particulier | Hinton et al., section 2.1 |
| Le facteur T au carré | Les gradients des soft targets varient comme 1/T^2, donc multipliez la loss douce par T^2 en la combinant avec la loss dure | Hinton et al., section 2 |

Le facteur dans un run, avec les logits `[9, 4, 2, 0, -4]` face à `[6, 5, 0, 1, -2]` : la plus grande entrée du gradient vaut 0.2663 à T = 1 et 0.0017 à T = 20, et multipliée par T au carré elle reste entre 0.64 et 0.84 de T = 2 à T = 20 ([leçon 3](../lessons/0003-temperature.md)).

## La loss combinée

```text
loss = lambda * T^2 * CE(teacher at T, student at T) + (1 - lambda) * CE(label, student at 1)
```

La notation est celle de ce parcours. Hinton et al. décrivent une moyenne pondérée des deux entropies croisées et ont trouvé les meilleurs résultats en général avec un poids considérablement plus faible sur celle du hard label.

| Réglage | Valeur | Source et portée |
|---|---|---|
| Parole, poids relatif sur le terme dur | 0.5 | Hinton et al., section 4.1, un modèle acoustique |
| Parole, températures essayées | 1, 2, 5, 10 | Hinton et al., section 4.1 |
| MNIST, élève de 800 unités, soft targets à T = 20 | 74 erreurs de test, contre 146 seul et 67 pour l'enseignant | Hinton et al., section 3 |
| MNIST, élève de 30 unités, meilleures températures | 2.5 à 4 | Hinton et al., section 3 |
| Poids de mélange au niveau du mot de Kim et Rush essayés | 0.5 et 0.9, 0.5 meilleur | Kim et Rush, 2016, section 4 |
| Ré-entraînement de LLM élagué, températures essayées | 0.1, 0.5, 1.0, 3.0, meilleure à 1.0 | Muralidharan et al., 2024, annexe A.3 |
| Pré-entraînement de LLM, températures essayées | 0.5 à 10, meilleure à 1 sur toutes les échelles | Busbridge et al., 2025, annexe G.2 |
| Ré-entraînement de LLM élagué, mélange de loss | La loss sur les logits seule vaut mieux qu'un mélange avec la loss de modélisation de langage | Muralidharan et al., 2024, section 4 |

Chaque ligne est un article sur sa propre configuration. Les deux lignes de température pour les LLM sont en désaccord avec celles des classifieurs, balayez donc T, y compris 1, sur votre propre paire.

## La loss au niveau du token

| Élément | Choix |
|---|---|
| Formes des logits | Élève et enseignant, chacun (batch, positions, vocab) |
| Axe de la divergence | Le dernier, le vocabulaire, ce qui donne (batch, positions) |
| Préfixe | Une séquence fixe, texte humain ou texte de l'enseignant, fournie aux deux modèles (teacher forcing) |
| Enseignant | Passe avant avec gradients désactivés |
| Réduction | Kim et Rush somment sur les positions. GKD et Minitron divisent par la longueur. Masquez le padding et divisez par la somme du masque |
| Température | Divisez les deux logits par T avant le log-softmax, multipliez la loss par T^2 si elle est mélangée à un terme dur |

```python
import torch.nn.functional as F

def token_kd_loss(student_logits, teacher_logits, mask, T=1.0):
    s = F.log_softmax(student_logits / T, dim=-1)
    t = F.log_softmax(teacher_logits / T, dim=-1)
    kl = (t.exp() * (t - s)).sum(dim=-1)
    return (kl * mask).sum() / mask.sum()
```

L'entropie croisée par rapport à l'enseignant et la KL directe diffèrent par l'entropie de l'enseignant, une constante pour l'élève, donc elles ont les mêmes gradients. Gemma 2 écrit la somme des -P_T(x | x_c) log P_S(x | x_c) (section 3.2).

## KL directe et KL inverse

| | KL directe | KL inverse |
|---|---|---|
| Expression | KL(p \|\| q) = sum p log(p / q) | KL(q \|\| p) = sum q log(q / p) |
| p est l'enseignant, q l'élève | Pondérée par l'enseignant | Pondérée par l'élève |
| Punit | Un élève qui donne peu de masse là où l'enseignant en a beaucoup | Un élève qui donne de la masse là où l'enseignant en a peu |
| Comportement | Couverture des modes, s'étale sur chaque mode | Recherche de mode, s'engage sur un seul |
| Sur le jouet de la leçon 5 | Préfère l'élève étalé, 0.595 contre 1.572 | Préfère l'élève engagé, 0.623 contre 1.273 |

| Source | Constat | Portée |
|---|---|---|
| MiniLLM, Gu et al., 2023 | KL inverse pour la distillation générative, puisque la KL directe donne de la masse aux régions vides de l'enseignant | Suivi d'instructions, gradient de politique sur des échantillons de l'élève |
| GKD, Agarwal et al., 2023 | La meilleure divergence dépend de la tâche. La JSD(beta) généralisée interpole, proche de la directe près de 0, proche de l'inverse près de 1. KL inverse bien meilleure que la directe sur l'instruction tuning FLAN | Élèves T5, XSum, WMT, GSM8K, FLAN |
| Minitron, Muralidharan et al., 2024 | KLD directe la meilleure : loss LM 2.155 contre 2.665 pour l'inverse sur un 8B élagué en profondeur | Ré-entraînement de base models élagués |

La `GKDConfig` de TRL expose le choix sous le nom `beta` : 0.0 est la divergence KL, 1.0 la KL inverse, avec 0.5 par défaut.

## La contrainte du tokenizer

| Situation | Ce qui fonctionne | Ce que cela coûte |
|---|---|---|
| Même tokenizer | Loss au niveau du token | Exige les logits de l'enseignant |
| Élève construit à partir de l'enseignant (DistilBERT, Minitron) | Loss au niveau du token | Élève contraint par la conception de l'enseignant |
| Tokenizers différents, logits disponibles | Loss ULD, ou le trainer GOLD de TRL | Perd l'identité des tokens dans le terme de distance, hypothèse de coût uniforme, alignement grossier des positions |
| Seulement le texte de l'enseignant | Entraîner sur ses séquences générées (étape 3) | L'élève ne voit jamais les distributions de l'enseignant |

ULD (Boizard et al., 2024) : L = somme sur t de CE(t) + lambda * W1(élève, enseignant), lambda 1.5, avec W1 comme somme des différences absolues des vecteurs de probabilités triés par ordre décroissant (section 3). Un élève qui met sa masse sur le mauvais token peut obtenir 0 sur W1, c'est donc l'entropie croisée sur le token de référence qui porte le signal d'identité.

TRL, tel que lu pour la leçon 6 : `GKDTrainer` prend un seul tokenizer comme `processing_class` et n'a pas d'argument de tokenizer d'enseignant. GOLD est documenté comme prenant en charge des tokenizers différents, avec `use_uld_loss=True` et `teacher_tokenizer_name_or_path`, et se trouve dans `trl.experimental`.

## Le coût du stockage des logits de l'enseignant

Arithmétique de la [leçon 7](../lessons/0007-distilling-during-pretraining.md), avec le vocabulaire de Gemma 2 de 256,128 (tableau 1). Les 2 octets par probabilité et le k = 256 avec un index de 4 octets sont des hypothèses, pas des chiffres du rapport.

| Grandeur | Valeur |
|---|---|
| Distribution complète par token, bf16 | 512,256 octets |
| Distribution complète par séquence de 8,192 tokens | 4.20 Go |
| Complète pour 2T tokens (le run 2B) | 1.02 Eo |
| Complète pour 8T tokens (le run 9B) | 4.10 Eo |
| Top-256 par token, 6 octets par entrée | 1,536 octets, 333.5 fois plus petit |
| Top-256 pour 2T tokens | 3.07 Po |
| Top-256 pour 8T tokens | 12.29 Po |

Le rapport de Gemma 2 ne décrit pas comment la distribution de l'enseignant a été fournie. Minitron calcule l'enseignant dans une passe avant en parallèle de l'entraînement et compare les runs à calcul égal. Le test de top-K de Minitron a trouvé une baisse de précision significative pour K jusqu'à 100 et aucun gain à tronquer à de plus grands K, sur une seule configuration de ré-entraînement de modèle élagué.

## Pour en savoir plus

- [Ressources](../RESOURCES.md)
- [Glossaire](../GLOSSARY.md)
