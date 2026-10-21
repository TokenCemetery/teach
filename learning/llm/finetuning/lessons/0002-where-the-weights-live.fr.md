---
title: "2. Où vivent les poids"
description: "Nommer chaque projection à laquelle un adapter pourrait se rattacher"
type: lesson
---

# Leçon 2. Où vivent les poids

**Lien avec la mission :** Un adapter se rattache à des matrices de poids précises. Vous ne pouvez pas choisir lesquelles tant que vous ne savez pas les nommer et dire ce que fait chacune.
**Source primaire :** [The Illustrated Transformer, Jay Alammar](https://jalammar.github.io/illustrated-transformer/)
**Prérequis :** [Leçon 1](0001-what-a-base-model-is.md)

## Échauffement

1. ▢ Que calcule un modèle de langage, énoncé comme une fonction ?

<details markdown="1"><summary>Vérifier</summary>

Une séquence de tokens en entrée, un score pour chaque token du vocabulaire en sortie. La génération est une boucle autour de cette fonction, elle n'en fait pas partie.

</details>

2. ▢ Pourquoi un base model ne suit-il pas une instruction ?

<details markdown="1"><summary>Vérifier</summary>

Le suivi d'instructions est un comportement entraîné, ajouté par-dessus la prédiction du token suivant. Un base model n'a que l'objectif du token suivant, donc il continue le texte au lieu d'obéir.

</details>

## À savoir

Presque tous les paramètres d'un modèle moderne de type decoder-only vivent dans l'un de trois endroits : la table d'embeddings, une pile de blocs de transformer identiques, et la projection de sortie. Les blocs en contiennent l'écrasante majorité, et c'est là que les adapters se rattachent.

### À l'intérieur d'un bloc

Chaque bloc a deux sous-couches, chacune précédée d'une normalisation et enveloppée dans une connexion résiduelle.

**Attention.** Quatre projections linéaires, nommées par convention d'après ce qu'elles produisent :

| Nom | Rôle |
|---|---|
| `q_proj` | Queries : ce que cette position cherche |
| `k_proj` | Keys : ce que chaque position offre comme correspondance |
| `v_proj` | Values : le contenu effectivement récupéré |
| `o_proj` | Remélange le résultat de l'attention dans le flux résiduel |

**MLP** (aussi appelé réseau feed-forward). Dans les modèles actuels, ce sont généralement trois projections plutôt que deux, à cause des activations à porte :

| Nom | Rôle |
|---|---|
| `gate_proj` | Produit la porte, passée dans une activation |
| `up_proj` | Projette vers le haut jusqu'à la dimension intermédiaire, plus large |
| `down_proj` | Reprojette vers le bas jusqu'à la dimension cachée |

Le MLP est plus large que la dimension cachée, couramment de 2.5× à 4×, si bien que, malgré moins de matrices qu'on ne l'imagine, **le MLP contient plus de paramètres que l'attention.** Ce fait guide le choix des target modules dans la leçon 10.

### Compter

Une couche linéaire de dimension d'entrée `d_in` et de dimension de sortie `d_out` contient `d_in × d_out` poids. Pour un modèle de taille cachée 2048, 24 couches et taille intermédiaire 5632 :

- Attention par couche, en ignorant la grouped-query attention : 4 × 2048 × 2048 ≈ 16.8M
- MLP par couche : 3 × 2048 × 5632 ≈ 34.6M
- Total par couche ≈ 51.4M, fois 24 couches ≈ 1.23B
- Embeddings, avec un vocabulaire de 32k : 32000 × 2048 ≈ 65.5M, doublé si la projection de sortie n'est pas liée

Cela rend compte de pratiquement tout le modèle. Il n'y a pas de réservoir caché de paramètres quelque part ailleurs.

### Un piège à connaître dès maintenant

La plupart des modèles actuels utilisent la **grouped-query attention**, où plusieurs têtes de query partagent un même jeu de keys et de values. Cela rend `k_proj` et `v_proj` *plus étroites* que `q_proj` et `o_proj`, souvent d'un facteur quatre ou huit. Tout calcul qui suppose que les quatre projections d'attention sont carrées surestimera, et toute hypothèse selon laquelle elles ont la même taille produira un mauvais nombre de paramètres d'adapter dans la leçon 8.

### Trouver les vrais noms

Ne vous fiez jamais à une liste de noms de modules retenue de mémoire. Ils sont fixés par l'implémentation du modèle et diffèrent d'une architecture à l'autre. Affichez-les :

```text
model := load_model("<some-small-model>")
for name, module in model.modules():
    if module is a linear layer:
        print(name, module.weight.shape)
```

C'est le diagnostic le plus utile de tout cet espace de travail. Un fine-tuning qui n'entraîne silencieusement rien signifie généralement un nom de target module qui ne correspondait à rien.

## Pratique

1. ▢ Nommez les sept projections linéaires d'un bloc de transformer moderne typique.

<details markdown="1"><summary>Vérifier</summary>

`q_proj`, `k_proj`, `v_proj`, `o_proj` dans l'attention ; `gate_proj`, `up_proj`, `down_proj` dans le MLP.

Les architectures plus anciennes ou sans porte n'ont que deux projections de MLP. C'est pourquoi on affiche les noms au lieu de les réciter.

</details>

2. ▢ Pour un modèle de taille cachée 4096 et de taille intermédiaire 11008, qu'est-ce qui contient le plus de paramètres par couche, l'attention ou le MLP ? Environ dans quel rapport ?

<details markdown="1"><summary>Vérifier</summary>

Le MLP, environ deux contre un. L'attention (projections carrées) fait 4 × 4096² ≈ 67M. Le MLP fait 3 × 4096 × 11008 ≈ 135M.

Avec la grouped-query attention, l'écart s'élargit encore, parce que `k_proj` et `v_proj` rétrécissent alors que le MLP non.

</details>

3. ▢ Vous configurez votre adapter pour cibler `["query", "value"]` sur un modèle dont les modules s'appellent `q_proj` et `v_proj`. Que se passe-t-il ?

<details markdown="1"><summary>Vérifier</summary>

Rien ne correspond, donc soit la bibliothèque lève une erreur, soit, pire selon la version, vous obtenez un modèle sans aucun poids d'adapter entraînable. L'entraînement tourne alors, la loss bouge à peine, et le run a l'air simplement décevant plutôt que cassé.

Vérifiez le nombre de paramètres entraînables immédiatement après avoir construit l'adapter. La leçon 11 en fait une habitude.

</details>

4. ▢ Pourquoi la structure du flux résiduel compte-t-elle pour les adapters ?

<details markdown="1"><summary>Vérifier</summary>

Parce qu'un adapter modifie la sortie d'une projection, et que la connexion résiduelle fait que ce changement s'ajoute à un flux courant au lieu de le remplacer. Une petite contribution d'adapter peut orienter le flux sans détruire ce que les couches gelées y ont déjà écrit, ce qui explique pourquoi démarrer un adapter à exactement zéro (leçon 9) est sûr.

</details>

5. ▢ Grouped-query attention : vos notes supposent que les quatre projections d'attention font toutes 2048 × 2048, mais le modèle a 32 têtes de query et 4 têtes key-value avec une dimension de tête de 64. Quelles sont les vraies formes ?

<details markdown="1"><summary>Vérifier</summary>

`q_proj` et `o_proj` restent à 2048 × 2048 (32 × 64 = 2048). `k_proj` et `v_proj` font 2048 × 256 (4 × 64 = 256).

L'attention contient donc environ 2 × 2048² + 2 × 2048 × 256 ≈ 9.4M par couche, et non 16.8M. Presque la moitié de votre estimation.

</details>

## Exercices en situation réelle

- [ ] Exécutez la boucle de listage des modules ci-dessus, en utilisant le véritable appel d'inspection de modèle de votre bibliothèque (par exemple `named_modules()` dans PyTorch), sur le plus petit modèle que vous pouvez télécharger. Écrivez à la main les sept noms et leurs formes dans vos propres notes.
- [ ] À partir des seules formes, calculez le nombre total de paramètres du modèle. Comparez-le au chiffre de sa fiche de modèle et expliquez tout écart.
- [ ] Demain : recommencez avec un modèle d'une autre famille. Notez chaque nom de module qui diffère.

## Pour aller plus loin

- [The Illustrated Transformer, Jay Alammar](https://jalammar.github.io/illustrated-transformer/)
- [LLM Visualization, Brendan Bycroft](https://bbycroft.net/llm) : les nombres de paramètres sont affichés par matrice
- [Article : "Attention Is All You Need", Vaswani et al., arXiv:1706.03762](https://arxiv.org/abs/1706.03762)
- [Leçon 10. Choisir les target modules](0010-choosing-target-modules.md) est l'endroit où cela porte ses fruits

---

Ça ne passe pas ? Relisez la source primaire en haut de page, car cette leçon la condense et c'est dans la condensation que la compréhension s'échappe. Consultez le [glossaire](../GLOSSARY.md) pour tout terme qui vous a paru glissant.

Si c'est la leçon elle-même qui n'est pas claire plutôt que la matière, c'est un défaut : [ouvrez une issue](https://github.com/TokenCemetery/teach/issues).
