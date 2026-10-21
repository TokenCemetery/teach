---
title: "11. Votre premier adapter"
description: "Un run qui prouve le pipeline avant de prouver quoi que ce soit d'autre"
type: lesson
---

# Leçon 11. Votre premier adapter

**Lien avec la mission :** « Le lancer » fait partie de la mission. Tout ce qui précède était de la lecture ; ceci est le run.
**Source primaire :** [Doc : SFTTrainer, Hugging Face TRL](https://huggingface.co/docs/trl/main/en/sft_trainer)
**Prérequis :** [Leçon 3](0003-tokenizers-and-chat-templates.md), [Leçon 9](0009-rank-alpha-and-initialisation.md), [Leçon 10](0010-choosing-target-modules.md)

## Échauffement

1. ▢ Quelle est la valeur par défaut moderne pour les target modules, et pourquoi est-elle abordable ?

<details markdown="1"><summary>Vérifier</summary>

Toutes les couches linéaires, à rank généreux. Les paramètres d'adapter sont négligeables face à la mémoire des activations, donc les restreindre n'apporte plus grand-chose.

</details>

2. ▢ Quelle ligne de code attrape un nom de target module qui ne correspondait à rien ?

<details markdown="1"><summary>Vérifier</summary>

`model.print_trainable_parameters()`. Un nombre proche de zéro signifie que l'adapter ne s'est rattaché à rien.

</details>

3. ▢ Entraînement ou inférence : où `add_generation_prompt=True` a-t-il sa place ?

<details markdown="1"><summary>Vérifier</summary>

L'inférence. À l'entraînement, le tour de l'assistant est déjà dans le texte, donc ajouter le prompt duplique le marqueur.

</details>

## À savoir

### Choisissez la plus petite chose qui puisse échouer de façon instructive

Le but de votre premier run n'est **pas** un bon modèle. C'est de prouver que le pipeline est correctement câblé. Rendez-le donc assez bon marché pour qu'une erreur coûte quelques minutes :

- Un base model de la classe 0.5B à 3B. Les petits modèles s'entraînent vite et révèlent les bugs de données aussi bien que les gros.
- Quelques centaines d'exemples. Assez pour voir la loss bouger.
- `max_steps` autour de 20 à 50, pas des epochs. Vous voulez qu'il se termine vite.

Optimiser quoi que ce soit avant que le pipeline soit prouvé est un effort perdu, et cela masque quel changement a causé quel effet.

### Un run minimal

```text
dataset := load_dataset("<a small instruction dataset>", split: "train[:500]")

adapter_config := {
    rank: 16,
    alpha: 32,
    dropout: 0.05,
    adapt_bias: false,
    target_modules: "all-linear",
}

run_config := {
    output_dir: "runs/first-adapter",
    max_steps: 50,
    per_device_batch_size: 1,
    gradient_accumulation_steps: 8,      # effective batch size 8
    learning_rate: 2e-4,
    warmup_steps: 5,
    lr_schedule: "cosine",
    logging_steps: 1,                    # every step, for the first run
    max_length: 1024,
    gradient_checkpointing: true,
    precision: "bf16",
}

trainer := new_trainer(
    model: "<a small base model>",
    train_dataset: dataset,
    adapter_config: adapter_config,
    run_config: run_config,
)

trainer.train()
trainer.save("runs/first-adapter/final")
```

Deux remarques sur cette surface d'API. `SFTTrainer` accepte une *chaîne* pour le modèle et le chargera pour vous. La longueur de séquence est `max_length` dans `SFTConfig`. Ces deux points ont changé d'une version à l'autre, donc **lisez la documentation de la version installée plutôt que de vous fier à cet extrait ou à votre mémoire.** Cette consigne n'est pas une formule de politesse ; c'est la source la plus fiable d'après-midis perdus de tout cet espace de travail.

### Précision, matériel, et ce qui varie réellement

`bf16=True` exige une prise en charge matérielle de bfloat16, répandue sur les accélérateurs modernes mais pas universelle. Sur des appareils plus anciens, vous aurez peut-être besoin de fp16 avec loss scaling, et sur certains backends le fp32 complet est la seule option. Le principe de la leçon 5 est inchangé ; seuls les formats disponibles diffèrent.

De même, l'accélérateur précis qui se trouve derrière ce script ne fait pas partie de la méthode. Les concepts, l'arithmétique et les modes de défaillance sont identiques sur CUDA, ROCm, Intel, Apple Silicon et CPU. Ce qui diffère, c'est quels kernels sont optimisés, quelles précisions sont prises en charge, et la vitesse d'un pas. Là où un backend contraint réellement la méthode, cet espace de travail le dit explicitement ; voir la [Leçon 16](0016-training-through-a-quantized-base.md).

### Les quatre vérifications, dans l'ordre

Faites-les avant de vous soucier de la courbe de loss.

**1. L'adapter existe-t-il ?**

```python
trainer.model.print_trainable_parameters()
```

Comparez avec votre arithmétique de la leçon 8. Un nombre de zéro, ou qui diffère de plus qu'un arrondi, signifie qu'il faut s'arrêter et corriger.

**2. Les données sont-elles ce que vous croyez ?**

```python
example = trainer.train_dataset[0]
print(repr(tokenizer.decode(example["input_ids"])))
labels = example["labels"]
print(sum(1 for l in labels if l != -100), "of", len(labels), "positions scored")
```

Décodez un vrai exemple d'entraînement et lisez-le. Cette seule vérification attrape les chat templates incompatibles, les tokens de fin de tour manquants, un bug de masquage et une troncature au milieu d'une réponse : quatre des cinq causes les plus courantes d'un mauvais fine-tuning. **Ne la sautez pas.** Ce sont les dix secondes les plus rentables du processus.

**3. La loss bouge-t-elle ?**

Sur 50 pas avec `logging_steps=1`, la loss doit visiblement baisser. Une loss plate dès le premier pas signifie que l'adapter n'est pas attaché, que le learning rate est beaucoup trop bas, ou que rien n'est noté.

**4. Peut-il surapprendre deux exemples ?**

Le meilleur test de fumée disponible. Entraînez sur deux exemples pendant cent pas. La loss doit approcher zéro. S'il ne peut pas mémoriser deux exemples, le pipeline est cassé, et vous l'avez appris en deux minutes plutôt qu'après un run de six heures.

### Sauvegardez ce dont vous aurez besoin pour le reproduire

Le répertoire de l'adapter est petit, généralement de quelques mégaoctets à quelques centaines, et contient seulement les poids de l'adapter plus une configuration qui enregistre le base model, le rank, alpha et les target modules. Il est inutilisable sans ce base model exact, donc notez l'identifiant du base model et sa révision à côté.

Notez aussi les versions des bibliothèques. Une configuration qui s'est entraînée proprement il y a six mois peut ne pas se charger de la même façon, et « quelle version était-ce » ne se retrouve pas après coup.

## Pratique

1. ▢ Vous avez 50 000 exemples et un gros base model disponible. Pourquoi est-ce le mauvais premier run ?

<details markdown="1"><summary>Vérifier</summary>

Parce que le travail du premier run est de prouver le pipeline, et qu'un long run coûteux donne la même information qu'un run court et bon marché, simplement bien plus tard et à un coût plus élevé.

Pire, si quelque chose cloche, vous l'apprenez après des heures au lieu de quelques minutes, et vous ne pouvez pas dire lequel de plusieurs changements a compté.

</details>

2. ▢ La loss est complètement plate dès le premier pas. Nommez trois causes dans l'ordre où vous les vérifieriez.

<details markdown="1"><summary>Vérifier</summary>

1. L'adapter ne s'est rattaché à rien ; vérifiez `print_trainable_parameters()`.
2. Chaque label vaut `-100`, donc rien n'est noté ; vérifiez le nombre de labels sur un vrai exemple.
3. Le learning rate est trop bas de plusieurs ordres de grandeur ; vérifiez qu'il se situe autour de `1e-4`, et non `1e-5` ou moins.

Les trois s'écartent en une ligne, c'est pourquoi elles passent avant tout ce qui est subtil.

</details>

3. ▢ Pourquoi décoder un exemple d'entraînement plutôt que de faire confiance au dataset ?

<details markdown="1"><summary>Vérifier</summary>

Parce que les défaillances qui comptent sont invisibles dans le dataset et visibles dans le texte décodé : un mauvais chat template, un token de fin de tour manquant, des tokens de prompt qui devaient être masqués et ne le sont pas, une réponse tronquée au milieu d'une phrase par `max_length`.

Aucune ne lève d'erreur. Toutes produisent un run qui a l'air correct et un modèle qui ne l'est pas.

</details>

4. ▢ Votre adapter ne parvient pas à amener la loss près de zéro sur deux exemples en cent pas. Qu'est-ce que cela vous dit ?

<details markdown="1"><summary>Vérifier</summary>

Que le pipeline est cassé, pas que la tâche est difficile. Deux exemples sont trivialement mémorisables par n'importe quel adapter qui fonctionne.

Cherchez un adapter non attaché, des labels entièrement masqués, un learning rate proche de zéro, ou un data collator qui produit autre chose que ce que vous attendez.

</details>

5. ▢ Vous avez le répertoire de l'adapter et rien d'autre. Pouvez-vous l'utiliser ?

<details markdown="1"><summary>Vérifier</summary>

Seulement si vous pouvez identifier le base model exact face auquel il a été entraîné, ce que la configuration de l'adapter enregistre par son nom. Appliqué à un autre base model, même un autre checkpoint de la même famille, le résultat est au mieux dégradé et au pire absurde.

Notez l'identifiant du base model, sa révision et les versions de vos bibliothèques. Un adapter est un diff, et un diff a besoin de sa base.

</details>

6. ▢ Batch size effective pour `per_device_train_batch_size=2`, `gradient_accumulation_steps=8`, sur 4 appareils ?

<details markdown="1"><summary>Vérifier</summary>

2 × 8 × 4 = 64.

Rapportez ce chiffre, pas celui par appareil. Comparer des runs par batch size par appareil est une manière fiable de tirer une fausse conclusion.

</details>

## Exercices en situation réelle

- [ ] Exécutez le test de surapprentissage sur deux exemples avant tout entraînement réel. Confirmez que la loss approche zéro.
- [ ] Décodez et lisez un exemple d'entraînement en entier. Comptez combien de positions sont notées contre masquées.
- [ ] Menez un run de 50 pas de bout en bout et sauvegardez l'adapter. Notez sa taille sur disque.
- [ ] Demain : écrivez l'identifiant du base model, sa révision et chaque version de bibliothèque, dans un fichier à côté de l'adapter.

## Pour aller plus loin

- [Doc : SFTTrainer, Hugging Face TRL](https://huggingface.co/docs/trl/main/en/sft_trainer)
- [Doc : LoRA, Hugging Face PEFT](https://huggingface.co/docs/peft/main/en/developer_guides/lora)
- [Modes de défaillance](../reference/failure-modes.md) : gardez-le ouvert pendant le run
- [Leçon 12. Lire un run d'entraînement](0012-reading-a-training-run.md)

---

Ça ne passe pas ? Relisez la source primaire en haut de page, car cette leçon la condense et c'est dans la condensation que la compréhension s'échappe. Consultez le [glossaire](../GLOSSARY.md) pour tout terme qui vous a paru glissant.

Si c'est la leçon elle-même qui n'est pas claire plutôt que la matière, c'est un défaut : [ouvrez une issue](https://github.com/TokenCemetery/teach/issues).
