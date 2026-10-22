---
title: "La boucle d'entraînement"
description: "Loss d'entropie croisée sur le vocabulaire, passe arrière et autograd, et pas d'optimiseur AdamW, des logits aux poids mis à jour"
type: reference
---

# La boucle d'entraînement : loss, passe arrière et optimiseur

L'étape 4 condensée pour la consultation. La [leçon 9](../lessons/0009-cross-entropy-loss.md) couvre la transformation des logits en une seule loss scalaire ; la [leçon 10](../lessons/0010-backward-pass-and-autograd.md) couvre la transformation de ce scalaire en un gradient pour chaque poids ; la [leçon 11](../lessons/0011-adamw-optimizer.md) couvre la transformation des gradients en mises à jour des poids. Cette fiche rassemble les trois formules, dans l'ordre où l'entraînement les utilise réellement.

## Loss d'entropie croisée

```text
loss = -log(p_correct)
```

| `p_correct` | Loss | Se lit comme |
|---|---|---|
| 0.8 | `-log(0.8) ≈ 0.223` | Confiant et dans le vrai, petite pénalité |
| 0.1 | `-log(0.1) ≈ 2.303` | Confiant et dans le faux, pénalité plus de 10x plus grande pour une baisse de probabilité de 10x |

`-log(p)` croît sans borne quand `p` tend vers 0 ; une pénalité plus simple `1 - p` sature à 1 et ne peut pas distinguer « un peu faux » de « catastrophiquement assuré et faux ». Elle a aussi un gradient propre par rapport aux logits (`softmax_output - one_hot_true_label`), ce qui explique pourquoi le softmax et l'entropie croisée sont presque toujours associés, souvent sous forme d'une seule opération fusionnée, numériquement stable, sur les logits bruts.

**Teacher forcing.** L'entraînement fournit toujours en contexte les vrais tokens précédents, jamais les propres prédictions du modèle. Comme le masquage causal restreint déjà chaque position à ne porter son attention que vers l'arrière, la prédiction de chaque position, et donc la loss de chaque position, se calcule en une seule passe avant plutôt qu'une passe par position. Les loss par position et par batch sont moyennées en un seul scalaire, puisque la descente de gradient a besoin d'une seule quantité à minimiser.

## La passe arrière et autograd

Chaque opération de la passe avant (produit matriciel, softmax, addition résiduelle) est enregistrée dans un **graphe de calcul** (computation graph). `loss.backward()` le parcourt en sens inverse, en appliquant automatiquement la règle de la chaîne avec la règle locale de rétropropagation déjà implémentée de chaque opération, et remplit le `.grad` de chaque paramètre entraînable.

Exemple travaillé de règle de la chaîne : `y = 3x + 1`, `z = y^2`, pour `x = 2` : `y = 7`, `dz/dy = 2y = 14`, `dy/dx = 3`, donc `dz/dx = 14 x 3 = 42`.

| Approche | Comment elle obtient un gradient | Coût |
|---|---|---|
| Différentiation symbolique | Dérive une formule sous forme fermée à la main ou par calcul formel | Ce n'est pas ce que fait autograd |
| Différentiation numérique | Perturbe chaque paramètre, relance la passe avant | Imprécise, une passe avant supplémentaire par paramètre |
| Différentiation automatique (autograd) | Enchaîne la règle locale de rétropropagation déjà implémentée de chaque opération sur le graphe enregistré | Exacte, un seul parcours en arrière pour tous les paramètres à la fois |

**Pourquoi les résiduels empêchent réellement la disparition du gradient.** Pour `y = x + Sublayer(x)`, `d(loss)/d(x) = d(loss)/d(y) x 1 + [a term through Sublayer]`. La dérivée locale du chemin identité vaut exactement 1, donc le terme direct passe sans mise à l'échelle quelle que soit la petitesse de la dérivée propre de `Sublayer`. C'est la raison mécanique, pas seulement une intuition.

**Les gradients s'accumulent, ils n'écrasent pas.** `.grad` s'ajoute à ce qui s'y trouvait déjà, donc une boucle d'entraînement doit remettre explicitement les gradients à zéro avant chaque nouvel appel à `backward()`, sans quoi le gradient d'un pas est contaminé par les restes du pas précédent.

## Le pas de l'optimiseur AdamW

```text
plain gradient descent:  w = w - lr * grad
Adam's moments:           m = beta1 * m + (1 - beta1) * grad          (momentum)
                          v = beta2 * v + (1 - beta2) * grad^2        (adaptive scale)
Adam's update:            w = w - lr * m_hat / (sqrt(v_hat) + eps)
AdamW's update:           w = w - lr * (m_hat / (sqrt(v_hat) + eps) + weight_decay * w)
```

(`m_hat`, `v_hat` sont `m`, `v` avec une correction de biais pour le fait que les deux démarrent à zéro.)

| Pièce | Ajoute | Corrige |
|---|---|---|
| Momentum (`m`) | Une moyenne mobile des gradients passés | Les gradients bruités de chaque batch ; la mise à jour suit une direction cohérente au lieu de trembler |
| Échelle adaptative (`v`) | Une estimation par paramètre de l'amplitude typique du gradient | Un seul learning rate fixe pour chaque poids ; les paramètres à petits gradients reçoivent des pas relativement plus grands, ceux à grands gradients des pas plus petits |
| Weight decay découplé (AdamW) | Un weight decay appliqué directement à `w`, sans jamais passer par `m`, `v` ni le dénominateur adaptatif | Intégrer la décroissance au gradient (Adam d'origine) fait dépendre son rétrécissement effectif de l'amplitude typique du gradient de chaque paramètre, au lieu du rétrécissement uniforme que la décroissance est censée être |

Exemple travaillé : `w = 5.0`, `grad = 2.0`, `lr = 0.1`, descente de gradient simple : `w = 5.0 - 0.1 x 2.0 = 4.8`.

## Avant de faire confiance à une implémentation de boucle d'entraînement

- [ ] L'entropie croisée prend directement les logits bruts (une opération fusionnée softmax + log-probabilité négative), et non un softmax manuel suivi d'une étape de logarithme séparée.
- [ ] L'entraînement fournit les vrais tokens précédents (teacher forcing), et la loss est calculée pour chaque position en une seule passe avant, et non une passe par position.
- [ ] Les gradients sont explicitement remis à zéro avant chaque appel à `backward()`.
- [ ] L'optimiseur est AdamW, et non Adam simple, si un weight decay est utilisé, et le weight decay est appliqué directement aux poids, et non intégré au gradient.

## Sources

- [Doc : "torch.nn.functional.cross_entropy", PyTorch](https://pytorch.org/docs/stable/generated/torch.nn.functional.cross_entropy.html)
- [Doc : "Autograd mechanics", PyTorch](https://pytorch.org/docs/stable/notes/autograd.html)
- [Article : "Decoupled Weight Decay Regularization", Loshchilov et Hutter, 2019](https://arxiv.org/abs/1711.05101)
- [Article : "Adam: A Method for Stochastic Optimization", Kingma et Ba, 2015](https://arxiv.org/abs/1412.6980)
- [Ressources](../RESOURCES.md)
