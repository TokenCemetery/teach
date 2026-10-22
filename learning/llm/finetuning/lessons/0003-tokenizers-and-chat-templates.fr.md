---
title: "3. Tokenizers et chat templates"
description: "Entraînez sur le rendu que vous servirez"
type: lesson
---

# Leçon 3. Tokenizers et chat templates

**Lien avec la mission :** La cause la plus courante d'un fine-tuning qui s'entraîne proprement mais se comporte mal est un chat template incompatible, pas un hyperparamètre.
**Source primaire :** [Doc : Chat Templates, Hugging Face Transformers](https://huggingface.co/docs/transformers/main/en/chat_templating)
**Prérequis :** [Leçon 1](0001-what-a-base-model-is.md), [Leçon 2](0002-where-the-weights-live.md)

## Échauffement

1. ▢ Qu'est-ce qui contient le plus de paramètres dans un bloc moderne, l'attention ou le MLP ?

<details markdown="1"><summary>Vérifier</summary>

Le MLP, parce que sa dimension intermédiaire fait plusieurs fois la taille cachée, et que la grouped-query attention rétrécit encore `k_proj` et `v_proj`.

</details>

2. ▢ Comment trouve-t-on les vrais noms de modules d'un modèle ?

<details markdown="1"><summary>Vérifier</summary>

On les affiche à partir du modèle chargé avec `named_modules()`. Ne les rappelez jamais de mémoire ; ils varient selon l'architecture.

</details>

3. ▢ Que mesure la loss d'entropie croisée ?

<details markdown="1"><summary>Vérifier</summary>

La probabilité que le modèle a attribuée au token qui est réellement venu ensuite. Une loss basse signifie que la vraie suite était peu surprenante pour le modèle.

</details>

## À savoir

Le modèle ne voit pas de texte. Il voit des entiers. Le tokenizer est la correspondance entre les deux, et il fait partie du modèle : le tokenizer d'un checkpoint n'est pas interchangeable avec celui d'un autre, même au sein d'une même famille.

### Ce qu'est un tokenizer

Les modèles modernes utilisent une tokenisation en sous-mots, généralement le byte-pair encoding. Entraîner le tokenizer consiste à partir des octets et à fusionner de façon répétée la paire adjacente la plus fréquente, ce qui produit un vocabulaire où les mots courants sont des tokens uniques et où les mots rares se découpent en morceaux.

Trois propriétés posent problème en pratique :

**Les tokens ne sont pas des mots.** ` the` (avec une espace initiale) et `the` sont des tokens différents. La casse change la tokenisation. Un nombre comme `1234` peut former un token ou quatre, et c'est pourquoi les modèles sont mauvais en arithmétique de façons qui paraissent arbitraires.

**Le nombre de tokens n'est pas le nombre de caractères.** L'anglais compte en moyenne environ quatre caractères par token ; le code, les écritures non latines et les mises en forme inhabituelles sont bien moins efficaces. Votre budget de longueur de séquence de la leçon 7 se mesure en tokens, donc vous devez mesurer, pas estimer.

**Les tokens spéciaux portent de la structure.** Début de séquence, fin de séquence, remplissage, et les marqueurs de rôle ci-dessous sont des entrées de vocabulaire ordinaires que le modèle a appris à traiter comme structurelles. Les émettre à la main de façon incorrecte n'est pas une erreur de syntaxe ; c'est un décalage de distribution silencieux.

### Chat templates

Un modèle de chat a été entraîné sur des conversations rendues en une seule séquence plate de tokens par un format de chaîne précis et exact. Par exemple, un modèle peut avoir été entraîné sur quelque chose qui ressemble à ceci :

```text
<|im_start|>system
You are helpful.<|im_end|>
<|im_start|>user
Hello<|im_end|>
<|im_start|>assistant
Hi.<|im_end|>
```

Une autre famille utilise des marqueurs entièrement différents. Le format n'est pas une convention que l'on peut approximer : c'est la distribution sur laquelle les poids ont été ajustés. Se tromper d'un marqueur, ajouter un saut de ligne parasite, ou omettre le bloc system alors que le modèle en attend un, et le modèle fonctionne désormais légèrement hors distribution. Il produira toujours du texte fluide, et c'est précisément pourquoi cet échec est difficile à repérer.

Le gabarit est livré avec le tokenizer, sous forme d'une chaîne Jinja. Utilisez-le plutôt que d'écrire le format vous-même :

```text
tokenizer := load_tokenizer("<model>")
messages := [
    {role: "system", content: "You are helpful."},
    {role: "user", content: "Hello"},
]

# For inference: leaves the sequence ready for the model to continue.
prompt := tokenizer.render(messages, add_generation_prompt: true)

# For training: the assistant turn is already present, so no generation prompt.
full := tokenizer.render(messages + [{role: "assistant", content: "Hi."}])

print(exact(prompt))
print(exact(full))
```

Afficher la chaîne exacte, et non une vue résumée, est important. La différence entre un gabarit correct et un gabarit cassé tient souvent à un seul caractère d'espacement, et un affichage ordinaire peut le masquer. En Python, cela veut dire `repr`, pas `print`, sur la chaîne.

### La règle unique

**Entraînez sur le même rendu que celui que vous servirez.** Si vous faites le fine-tuning sur votre propre format artisanal puis servez via le gabarit officiel du modèle, vous avez entraîné une distribution et déployé une autre. La courbe de loss aura l'air correcte. Le modèle sera subtilement moins bon, et vous passerez une journée à incriminer le rank.

`add_generation_prompt` est l'endroit où cela tourne le plus souvent mal : il a sa place à l'inférence, où l'on veut que le modèle continue en tant qu'assistant, et pas dans un exemple d'entraînement, où le texte de l'assistant fait partie de la séquence apprise.

![Une conversation rendue deux fois sous la forme d'une bande de morceaux de gabarit. Les deux partagent les trois mêmes morceaux qui se terminent par le marqueur de l'assistant ; le rendu d'inférence s'arrête là, tandis que le rendu d'entraînement comporte un morceau de plus, le texte de l'assistant lui-même et son marqueur de fin.](images/where-the-turn-begins.svg)

Les deux rendus sont les mêmes morceaux aux mêmes endroits jusqu'au marqueur de l'assistant. Celui qui diffère est le morceau qui suit, qui est exactement ce que le modèle est censé produire à l'inférence et exactement ce qu'il est censé apprendre pendant l'entraînement.

### Les base models n'ont pas de gabarit

Si le tokenizer d'un base model n'a pas de chat template, ce n'est pas un bug, parce qu'il n'y a pas de format de conversation à préserver. C'est vous qui choisissez le format : choisissez-en un, écrivez-le, et utilisez-le à l'identique à l'entraînement et au service.

## Pratique

1. ▢ Pourquoi ne peut-on pas échanger un tokenizer entre deux checkpoints d'une même famille de modèles ?

<details markdown="1"><summary>Vérifier</summary>

Les identifiants de tokens indexent directement la matrice d'embeddings. Un vocabulaire différent associe le même entier à une autre ligne, donc chaque entrée est silencieusement mal traduite. La sortie est du charabia fluide, ou un plantage si les tailles de vocabulaire diffèrent.

</details>

2. ▢ Vous construisez un exemple d'entraînement. `add_generation_prompt` doit-il valoir `True` ou `False`, et pourquoi ?

<details markdown="1"><summary>Vérifier</summary>

`False`. Le generation prompt est le marqueur d'ouverture qui dit au modèle « l'assistant parle ensuite », utile à l'inférence, quand le tour de l'assistant n'existe pas encore. À l'entraînement, le tour de l'assistant est présent dans le texte, donc ajouter le prompt duplique le marqueur et décale la séquence hors du format que le modèle connaît.

</details>

3. ▢ Votre fine-tuning s'entraîne jusqu'à une loss basse, mais au moment du service le modèle divague au-delà de la fin de sa réponse au lieu de s'arrêter. Nommez la cause la plus probable.

<details markdown="1"><summary>Vérifier</summary>

Le token de fin de tour manquait dans vos exemples d'entraînement, donc le modèle n'a jamais appris que les réponses se terminent.

La loss ne peut pas l'attraper : prédire une suite fluide est exactement ce pour quoi le modèle a été récompensé sur vos données. C'est un bug de construction des données que seule une vraie génération révèle, ce qui est l'une des raisons pour lesquelles la leçon 24 insiste pour générer plutôt que de seulement noter.

</details>

4. ▢ Un prompt fait 700 mots d'anglais. Environ combien de tokens, et feriez-vous confiance à cette estimation pour un budget d'entraînement ?

<details markdown="1"><summary>Vérifier</summary>

Environ 900 à 1000 tokens, en comptant à peu près 1.3 token par mot d'anglais. Non, vous ne lui feriez pas confiance : le rapport varie fortement avec le code, le JSON, les écritures non latines et les mises en forme inhabituelles, qui sont tous courants dans les données de fine-tuning.

Mesurez la vraie distribution avec le vrai tokenizer. La leçon 7 transforme cette distribution en un chiffre de mémoire.

</details>

5. ▢ Lequel de ces éléments peut-on changer sans danger entre l'entraînement et le service ?

    - a) La chaîne exacte du chat template utilisé
    - b) Le tokenizer livré avec le modèle
    - c) La temperature d'échantillonnage utilisée à la génération
    - d) Le token spécial qui marque la fin d'un tour

<details markdown="1"><summary>Vérifier</summary>

**c)** La temperature d'échantillonnage utilisée à la génération.

La temperature s'applique après que le modèle a produit sa distribution, c'est donc un choix de service. Les trois autres définissent la distribution sur laquelle les poids ont été ajustés ; en changer un, c'est servir un problème différent de celui sur lequel vous avez entraîné.

</details>

## Exercices en situation réelle

- [ ] Prenez un modèle et rendez un gabarit avec le véritable appel de chat template de votre bibliothèque (par exemple `apply_chat_template(..., tokenize=False)` dans Transformers), en affichant la chaîne exacte espacements compris (par exemple le `repr` de Python). Copiez-la dans vos notes.
- [ ] Tokenisez le même paragraphe dans deux familles de modèles différentes et comparez les nombres de tokens. Puis tokenisez un bloc de JSON et comparez de nouveau.
- [ ] Demain : cassez délibérément un gabarit en supprimant le marqueur de fin de tour, puis envoyez un prompt au modèle. Observez ce qu'il fait. C'est l'échec que vous apprenez à reconnaître.

## Pour aller plus loin

- [Doc : Chat Templates, Hugging Face Transformers](https://huggingface.co/docs/transformers/main/en/chat_templating)
- [Code : minbpe, Andrej Karpathy](https://github.com/karpathy/minbpe) : le byte-pair encoding sous une forme lisible
- [Modes de défaillance](../reference/failure-modes.md) : le chat template incompatible y figure
- [Leçon 21. Construire le dataset](0021-building-the-dataset.md)

---

Ça ne passe pas ? Relisez la source primaire en haut de page, car cette leçon la condense et c'est dans la condensation que la compréhension s'échappe. Consultez le [glossaire](../GLOSSARY.md) pour tout terme qui vous a paru glissant.

Si c'est la leçon elle-même qui n'est pas claire plutôt que la matière, c'est un défaut : [ouvrez une issue](https://github.com/TokenCemetery/teach/issues).
