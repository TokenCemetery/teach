---
title: "Modes de défaillance"
description: "Du symptôme à la cause, et les défaillances silencieuses"
type: reference
---

# Modes de défaillance

Fiche de diagnostic. Gardez-la ouverte pendant un run.

## Les quatre vérifications, avant toute autre chose

```python
# 1. Did the adapter attach?
model.print_trainable_parameters()          # compare to your arithmetic

# 2. Is the data what you think?
print(repr(tokenizer.decode(ds[0]["input_ids"])))
print(sum(1 for l in ds[0]["labels"] if l != -100), "of", len(ds[0]["labels"]), "scored")

# 3. Does loss move?                        # logging_steps=1 over 50 steps

# 4. Can it overfit two examples?           # loss → ~0 in 100 steps, or the pipeline is broken
```

La vérification 2 attrape en une seule lecture le chat template incompatible, les tokens de fin de tour manquants, les bugs de masquage et la troncature. Ce sont les dix secondes les plus rentables du processus.

## Symptôme → cause

![Six esquisses de la loss en fonction des pas : plate dès le pas 1, une baisse qui s'arrête bien au-dessus de zéro, des courbes train et held-out qui se séparent avec celle du held-out qui remonte, un escalier de paliers plats et de chutes brutales, une descente interrompue par un seul pic, et une descente qui se termine brutalement en NaN.](images/loss-curve-shapes.svg)

Les onze premières lignes ci-dessous nomment une courbe plutôt qu'un événement, et plusieurs d'entre elles partagent une forme : trois disent plate, deux disent bouge à peine. Repérez l'esquisse, puis lisez chaque ligne qui la nomme, puisqu'une même forme peut avoir plus d'une cause. À partir de la ligne douze, le symptôme a été observé ailleurs, dans une sortie, une erreur de chargement ou un jeu de régression, et il n'y a pas de courbe à repérer.

| Symptôme | Cause probable | Vérification |
|---|---|---|
| Loss exactement plate dès le pas 1 | L'adapter n'a rien trouvé à cibler | `print_trainable_parameters()` |
| Loss exactement plate dès le pas 1 | Tous les labels valent `-100` | Compter les positions notées |
| Loss exactement plate dès le pas 1 | Learning rate trop bas de plusieurs ordres de grandeur | Devrait être ~`1e-4` |
| La loss bouge à peine | Noms de target modules faux pour cette architecture | `named_modules()` |
| La loss bouge à peine | `α/r` minuscule par accident | `r` augmenté, `α` oublié |
| La loss plafonne haut | Plafond de capacité | Plus de rank ou plus de cibles, pas plus d'epochs |
| Le held-out monte, le train baisse | Surapprentissage | Livrer le minimum du held-out |
| Le train tombe vers 0 vite, le held-out monte aussitôt | Dataset beaucoup trop petit pour la capacité | Plus de données, moins de capacité |
| La loss monte en escalier aux frontières d'epoch | Mémorisation | Moins d'epochs |
| La loss pique puis se rétablit | Un batch pathologique | Trouver l'exemple aberrant |
| Loss → `NaN` | Débordement, ou mauvaises données | Préférer bf16 ; baisser le learning rate ; ajouter un warm-up |
| Held-out suspectement bon | Contamination à travers le découpage | Dédupliquer train contre test, lire les paires les plus similaires |
| Le modèle ne s'arrête jamais de générer | Pas de token de fin de tour dans les données d'entraînement | Décoder un exemple |
| La sortie ignore le format demandé | Chat template différent entre entraînement et service | Comparer avec `repr` |
| Réponses coupées au milieu d'une phrase | `max_length` tronque les cibles | Vérifier la distribution des longueurs |
| Réponses à des questions non posées | Le packing a cassé le masquage de la loss ou les frontières | Vérifier que `-100` survit au packing |
| Moins bon sur des sujets sans rapport | Oubli catastrophique | Jeu de régression face à la référence enregistrée |
| Ne refuse plus ce que le base model refusait | Régression de sécurité | **Bloque la livraison** |
| Sortie fusionnée ≠ sortie non fusionnée | Bug de fusion, ou l'échantillonnage était activé | Revérifier en décodage glouton |
| Modèle fusionné dégradé | Fusionné dans un base model quantifié | Fusionner en pleine précision, puis quantifier |
| L'adapter ne se charge pas | Mauvais base model ou mauvaise révision | Un adapter est un diff ; il lui faut exactement son base model |
| Erreurs de gradient sur un base model 4 bits | `prepare_model_for_kbit_training` sauté | L'ajouter |
| Excellente eval, mauvaise production | Distributions différentes entre entraînement et service | Entraîner sur des entrées réelles, pas propres |
| Le résultat a disparu au second run | Bruit de seed, jamais un vrai effet | Plusieurs seeds, comparaison appariée |

## Défaillances silencieuses : aucune erreur, mauvais résultat

L'ensemble dangereux. Rien ne lève d'erreur, tout semble correct.

1. **Chat template différent** entre l'entraînement et le service.
2. **Token de fin de tour manquant.** L'entraînement se passe bien, le modèle ne s'arrête jamais.
3. **Masquage de la loss incorrect.** Entraînement sur les prompts sans le vouloir.
4. **Contamination.** Le held-out mesure la mémorisation, rapporte de la généralisation.
5. **Fuite par groupe ou temporelle.** Découpage selon la mauvaise clé.
6. **Oubli catastrophique.** Chaque chiffre que vous surveillez s'améliore.
7. **Adapter attaché à rien.** S'entraîne, journalise une loss, n'apprend rien.
8. **Évaluer un artefact différent de celui que vous livrez**, par exemple une eval en bf16 et un déploiement en 4 bits.

Chacune a une étape de détection précise plus haut. Aucune ne s'annonce d'elle-même.

## Réduire l'oubli

Le moins cher d'abord :

1. Moins de pas, ou un checkpoint plus précoce
2. Learning rate plus bas
3. Rank plus bas, ou moins de target modules
4. Mélanger quelques pour cent de données d'instructions générales à l'entraînement
5. **Garder l'adapter non fusionné et router**, pour que le base model reste intact et que l'oubli cesse d'avoir de l'importance

## Hygiène de comparaison

- Une seule variable à la fois ; fixer la seed, les données et le découpage
- Plusieurs seeds, puisque la variance dépasse souvent l'effet
- Comparaison appariée sur des exemples identiques
- Rapporter `n` et un intervalle, jamais un chiffre nu
- Lire à chaque fois les vraies générations, échecs compris

## Quoi enregistrer pour chaque run

Base model **et révision** · configuration de l'adapter telle quelle · dataset et découpage exact · seed · batch size effective · learning rate et schedule · pas · checkpoint choisi et le chiffre qui le justifie · versions des bibliothèques · résultats de l'eval et du jeu de régression.

## Voir aussi

- [Leçon 11](../lessons/0011-your-first-adapter.md), [Leçon 12](../lessons/0012-reading-a-training-run.md), [Leçon 22](../lessons/0022-contamination-and-held-out-design.md), [Leçon 24](../lessons/0024-the-regression-suite.md)
