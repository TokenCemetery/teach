---
title: "13. Fusionner, sauvegarder et livrer un adapter"
description: "La fusion est exacte ; un adapter est un diff qui a besoin de son base model"
type: lesson
---

# Leçon 13. Fusionner, sauvegarder et livrer un adapter

**Lien avec la mission :** Un adapter qui n'existe que dans un script d'entraînement n'est pas livré. Cette leçon clôt l'étape 3.
**Source primaire :** [Doc : LoRA merging, Hugging Face PEFT](https://huggingface.co/docs/peft/main/en/developer_guides/lora)
**Prérequis :** [Leçon 8](0008-the-low-rank-idea.md), [Leçon 12](0012-reading-a-training-run.md)

## Échauffement

1. ▢ Quel checkpoint livrez-vous à partir d'un run en surapprentissage ?

<details markdown="1"><summary>Vérifier</summary>

Celui du minimum de la loss held-out, pas le dernier pas.

</details>

2. ▢ Que ne peut jamais vous montrer une courbe de loss ?

<details markdown="1"><summary>Vérifier</summary>

Si les générations sont utilisables, et si des capacités extérieures à la distribution de votre tâche se sont dégradées. Les deux demandent de générer pour de bon face à des sondes fixes.

</details>

3. ▢ Écrivez la mise à jour de LoRA, avec la mise à l'échelle.

<details markdown="1"><summary>Vérifier</summary>

`ΔW = (α/r) · BA`, ajoutée au `W₀` gelé.

</details>

## À savoir

### Ce que contient le répertoire

Un adapter sauvegardé contient, en gros :

```text
adapter_model.safetensors   # the A and B matrices, nothing else
adapter_config.json         # base model name, r, alpha, target_modules, task_type
README.md                   # generated model card
```

Petit, souvent quelques dizaines de mégaoctets. Et **incomplet par construction** : c'est un diff, dépourvu de sens sans le base model exact nommé dans sa configuration. Perdre la trace du base model, ou de sa révision, fait de l'adapter un déchet.

### Deux façons de livrer

**Non fusionné.** Charger le base model, appliquer l'adapter au chargement.

```text
base := load_model("<base model>", dtype: "bfloat16")
model := load_adapter(base, "runs/first-adapter/final")
```

**Fusionné.** Refondre la mise à jour dans les poids et jeter la structure de l'adapter.

```python
merged = model.merge_and_unload()
merged.save_pretrained("runs/first-adapter/merged")
tokenizer.save_pretrained("runs/first-adapter/merged")
```

Sauvegardez le tokenizer à côté. Un répertoire de modèle sans son tokenizer est un ticket de support en puissance.

### Choisir entre les deux

| | Non fusionné | Fusionné |
|---|---|---|
| Disque | Le base model une fois, les adapters en mégaoctets | Une copie complète du modèle par tâche |
| Vitesse d'inférence | Deux petites multiplications de matrices en plus par couche adaptée | Identique au base model |
| Plusieurs tâches | Un base model, plusieurs adapters, commutables | Un modèle complet chacun |
| Déploiement | La pile de service doit prendre en charge les adapters | N'importe quelle pile qui charge un modèle |
| Composabilité | Les adapters peuvent être échangés ou pondérés à l'exécution | Figé au moment de la fusion |

![Servir trois tâches. Fusionnés, trois modèles complets contiennent chacun leur propre copie des poids de base à côté d'un delta. Non fusionnés, une seule copie des poids de base se trouve au-dessus des trois mêmes deltas.](images/how-many-copies-of-the-base.svg)

Les trois deltas sont les mêmes trois des deux côtés. Ce qui se multiplie, c'est la partie grisée, qui est aussi la partie volumineuse.

La règle empirique : **fusionner pour un déploiement mono-usage, rester non fusionné quand on sert plusieurs tâches à partir d'un même base model.** La leçon 25 traite correctement du service multi-adapters.

### La fusion est exacte, avec deux exceptions

Comme la mise à jour est additive et linéaire, la fusion est arithmétiquement exacte. `W₀ + (α/r)BA` est la même fonction que celle que calculait le modèle non fusionné. Il n'y a ni approximation ni perte de qualité.

Sauf dans deux cas, qu'il vaut la peine de connaître :

**Fusionner dans un base model quantifié entraîne des pertes.** Si le base model est en 4 bits, y ajouter une mise à jour en bf16 exige de déquantifier, d'ajouter, puis de requantifier, et l'étape de requantification perd de l'information. L'ordre correct est : entraîner face au base model quantifié, puis fusionner dans le base model en *pleine précision*, puis quantifier le résultat fusionné si nécessaire. Fusionner directement dans les poids quantifiés dégrade la qualité sans raison. L'étape 4 y revient.

**Le dropout change l'échelle effective.** `lora_dropout` est actif à l'entraînement et inactif à l'inférence. C'est le comportement standard du dropout et il est normalement inoffensif, mais cela signifie que le poids fusionné reflète le chemin sans dropout, qui est le bon.

### Vérifier la fusion

Ne supposez jamais. Comparez les sorties :

```python
prompt = "<one of your fixed probes>"
# Greedy decoding, so any difference is the weights and not the sampler.
out_unmerged = unmerged_model.generate(**inputs, do_sample=False, max_new_tokens=64)
out_merged   = merged_model.generate(**inputs, do_sample=False, max_new_tokens=64)
assert tokenizer.decode(out_unmerged[0]) == tokenizer.decode(out_merged[0])
```

Le décodage glouton est le point essentiel : avec l'échantillonnage activé, vous ne pouvez pas distinguer un bug de fusion d'un aléa ordinaire. De petites différences numériques peuvent encore provoquer une divergence tard dans une longue génération, donc comparez un nombre modeste de tokens et enquêtez sur une divergence *précoce* plutôt que tardive.

### Plusieurs adapters sur un même base model

PEFT peut conserver plusieurs adapters et passer de l'un à l'autre, et peut les combiner avec des poids :

```python
model.load_adapter("path/to/adapter-a", adapter_name="a")
model.load_adapter("path/to/adapter-b", adapter_name="b")
model.set_adapter("a")                       # use one
model.add_weighted_adapter(["a", "b"], weights=[0.7, 0.3], adapter_name="blend")
```

La combinaison pondérée est un outil réellement utile et ce n'est pas de la magie : deux adapters entraînés indépendamment sur des tâches différentes ne se composent pas de façon fiable en un adapter qui fait les deux. Cela vaut la peine d'être essayé et cela demande d'être mesuré, pas supposé. Considérez toute affirmation sur l'arithmétique des adapters comme quelque chose à vérifier sur votre propre tâche.

### Quoi enregistrer

Tout ce qu'il faut pour reproduire et déboguer plus tard :

- Identifiant du base model **et révision**
- Configuration de l'adapter, telle quelle
- Identité du dataset et découpage exact
- Seed, batch size effective, learning rate, schedule, pas
- Quel checkpoint vous avez choisi et pourquoi, c'est-à-dire le chiffre held-out qui l'a justifié
- Versions des bibliothèques
- Résultats de l'évaluation, sondes de régression comprises

Ce n'est pas du processus pour le processus. Dans six mois, la question « pourquoi l'ancien adapter est-il meilleur que le nouveau » n'aura de réponse que grâce à de tels enregistrements.

## Pratique

1. ▢ Pourquoi un fichier d'adapter de 40 Mo est-il inutile à lui seul ?

<details markdown="1"><summary>Vérifier</summary>

Il ne contient que les matrices `A` et `B` : un diff par rapport à un ensemble précis de poids de base. Sans ce base model exact et cette révision, il ne peut pas être appliqué, et appliqué à un base model presque identique il se dégrade silencieusement.

</details>

2. ▢ Vous servez cinq variantes fine-tunées d'un même base model. Fusionner ou non ?

<details markdown="1"><summary>Vérifier</summary>

Ne fusionnez pas. Non fusionné signifie une copie du base model en mémoire plus cinq petits adapters, commutables par requête. Fusionné signifie cinq copies complètes de modèle.

Le coût est deux petites multiplications de matrices en plus par couche adaptée et une pile de service qui prend en charge les adapters.

</details>

3. ▢ Vous avez entraîné face à un base model quantifié en 4 bits. Décrivez la procédure de fusion correcte.

<details markdown="1"><summary>Vérifier</summary>

Chargez le base model en pleine précision, appliquez l'adapter, fusionnez là, puis quantifiez le modèle fusionné ensuite si vous avez besoin d'un artefact quantifié.

Fusionner directement dans les poids quantifiés demande de déquantifier, d'ajouter puis de requantifier, et la requantification perd de l'information sans aucun bénéfice.

</details>

4. ▢ Vous fusionnez, puis comparez des générations avec échantillonnage à temperature 0.8. Les sorties diffèrent. Qu'avez-vous appris ?

<details markdown="1"><summary>Vérifier</summary>

Rien. Avec l'échantillonnage activé, des sorties différentes sont attendues, que la fusion soit correcte ou non.

Comparez en décodage glouton, où toute divergence est attribuable aux poids. Puis enquêtez sur les divergences précoces ; une différence qui n'apparaît qu'après de nombreux tokens peut être une simple dérive numérique.

</details>

5. ▢ Qu'est-ce qui est vrai de la fusion d'un LoRA non quantifié ?

    - a) Elle est exacte et ne coûte rien à l'inférence
    - b) Elle perd un peu de qualité mais accélère l'inférence
    - c) Elle est exacte mais demande plus de mémoire à l'inférence
    - d) Elle entraîne des pertes et doit être évitée en production

<details markdown="1"><summary>Vérifier</summary>

**a)** Elle est exacte et ne coûte rien à l'inférence.

La mise à jour est additive et linéaire, donc elle se refond en une matrice de poids ordinaire, avec la même fonction, la même mémoire et aucune multiplication de matrices en plus. Cette propriété est ce qui distinguait LoRA des méthodes à couches d'adaptation qui l'ont précédé.

</details>

6. ▢ Vous combinez un adapter de mise en forme et un adapter de connaissances de domaine avec `add_weighted_adapter` et le résultat est moins bon que chacun des deux. Est-ce surprenant ?

<details markdown="1"><summary>Vérifier</summary>

Non. Des mises à jour de faible rang entraînées indépendamment occupent des sous-espaces sans rapport, et leur somme pondérée n'est pas garantie d'être une bonne mise à jour pour l'une ou l'autre tâche, a fortiori pour les deux.

Cela marche parfois bien et cela vaut la peine d'être essayé. Ce n'est jamais quelque chose à supposer ; mesurez-le face à chaque adapter seul.

</details>

## Exercices en situation réelle

- [ ] Fusionnez votre adapter et vérifiez en décodage glouton sur vos sondes fixes. Confirmez que les sorties correspondent.
- [ ] Comparez les tailles de répertoire : adapter seul contre modèle fusionné. Notez le rapport.
- [ ] Rédigez la fiche de run décrite plus haut, en entier, pour un vrai run.
- [ ] Demain : chargez deux adapters sur un même base model et passez de l'un à l'autre pour le même prompt. Observez la différence.

## Pour aller plus loin

- [Doc : LoRA merging, Hugging Face PEFT](https://huggingface.co/docs/peft/main/en/developer_guides/lora)
- [Doc : Model merging, Hugging Face PEFT](https://huggingface.co/docs/peft/main/en/developer_guides/model_merging)
- [Leçon 25. Servir des adapters](0025-serving-adapters.md)
- [Modes de défaillance](../reference/failure-modes.md)

---

Ça ne passe pas ? Relisez la source primaire en haut de page, car cette leçon la condense et c'est dans la condensation que la compréhension s'échappe. Consultez le [glossaire](../GLOSSARY.md) pour tout terme qui vous a paru glissant.

Si c'est la leçon elle-même qui n'est pas claire plutôt que la matière, c'est un défaut : [ouvrez une issue](https://github.com/TokenCemetery/teach/issues).
