---
title: "1. Ce qu'est réellement un base model"
description: "Le modèle est une seule fonction du token suivant ; base n'est pas instruct"
type: lesson
---

# Leçon 1. Ce qu'est réellement un base model

**Lien avec la mission :** Vous ne pouvez pas juger si le fine-tuning est la bonne réponse tant que vous ne savez pas exactement ce que fait le modèle quand on le laisse tranquille.
**Source primaire :** [LLM Visualization, Brendan Bycroft](https://bbycroft.net/llm)
**Prérequis :** aucun, c'est la première leçon.

## À savoir

Un modèle de langage est une seule fonction. Elle prend une séquence d'identifiants de tokens et renvoie un score pour chaque token de son vocabulaire, qui décrit ce qui pourrait venir ensuite. C'est toute l'opération. Le chat, les appels d'outils, les refus, les traces de raisonnement : tout cela est construit sur cette unique étape du token suivant.

Ces scores bruts s'appellent des **logits**. Softmax les transforme en distribution de probabilités. Un échantillonneur choisit un token dans cette distribution, le token est ajouté à la séquence, et la fonction s'exécute de nouveau. Le texte apparaît un token à la fois, et rien d'autre ne se passe.

Deux conséquences comptent pour tout ce qui suit.

**Les poids ne changent pas à l'inférence.** Quand un modèle semble se souvenir de quelque chose dit plus tôt dans une conversation, ce souvenir, ce sont les tokens présents dans sa fenêtre de contexte, pas une modification du modèle. Le fine-tuning est la seule chose de cet espace de travail qui modifie les poids, et il se fait hors ligne, avant la mise en service.

**L'échantillonnage n'est pas le modèle.** La temperature, top-p et top-k remodèlent la distribution après que le modèle l'a produite. Si la qualité de la sortie change quand vous changez la temperature, vous avez appris quelque chose sur votre échantillonneur, pas sur vos poids. Fixez l'échantillonnage avant d'attribuer quoi que ce soit à l'entraînement.

### Base contre instruct

Un modèle **base** a été entraîné sur un seul objectif : prédire le token suivant sur un très grand corpus. Il ne répond pas aux questions. Face à `What is the capital of France?`, il peut enchaîner avec trois autres questions d'examen, parce que c'est à cela que ressemblait le texte environnant dans ses données d'entraînement.

Un modèle **instruct** ou **chat** est un base model entraîné plus avant sur des paires d'instructions et de réponses, c'est-à-dire par fine-tuning supervisé, puis en général sur des données de préférences humaines ou issues d'un modèle. Le comportement de suivi d'instructions que vous tenez pour acquis est une couche entraînée, pas une propriété de l'architecture.

![La même question envoyée à un base model et au même modèle auquel on a ajouté l'instruction tuning. Le base model enchaîne avec d'autres questions d'examen ; le modèle ajusté produit une réponse.](images/one-prompt-two-continuations.svg)

Un prompt, deux suites, et la même fonction du token suivant sous les deux. La seconde boîte est la première plus de l'entraînement, et c'est là que vit la différence.

Choisir de partir de l'un ou de l'autre est une vraie décision :

| Point de départ | Vous héritez de | Vous devez fournir |
|---|---|---|
| Base | Rien d'autre que la capacité brute en langage | Chaque convention de format et de comportement |
| Instruct | Le format, le suivi d'instructions, le comportement de refus | Seulement votre tâche, mais vous risquez de dégrader ce qui est déjà là |

La plupart des fine-tunings avec adapter partent d'un modèle instruct, parce que reconstruire le suivi d'instructions de zéro sur un petit dataset est un échange perdant. Le coût, c'est que vos données d'entraînement entrent maintenant en concurrence avec l'entraînement déjà fait par l'éditeur, et cette concurrence est à l'origine de l'[oubli catastrophique](../GLOSSARY.md) que nous verrons plus tard.

### Le signal d'entraînement

Pendant l'entraînement, on montre au modèle une séquence réelle et on note la probabilité qu'il a attribuée au token qui est réellement venu ensuite. Ce score est la **loss d'entropie croisée**. Une loss basse signifie que le modèle a trouvé la vraie suite peu surprenante.

Retenez une réserve, car l'étape 6 repose dessus : la loss mesure la surprise sur le token suivant, sur un texte que vous avez déjà. Elle ne mesure pas si le modèle est utile.

## Pratique

1. ▢ Décrivez, en une phrase et sans le mot « comprendre », ce que calcule un modèle de langage.

<details markdown="1"><summary>Vérifier</summary>

À partir d'une séquence de tokens, il produit un score pour chaque token du vocabulaire, qui décrit ce qui pourrait venir ensuite.

Le mauvais réflexe est de décrire la génération (« il écrit du texte ») plutôt que la fonction. La génération est une boucle autour de la fonction, implémentée en dehors des poids. Garder les deux séparées permet de raisonner sur l'endroit où se trouve un problème.

</details>

2. ▢ Vous envoyez deux fois la même entrée à un modèle et obtenez deux réponses différentes. Nommez deux endroits d'où peut venir la différence, et dites lequel concerne les poids.

<details markdown="1"><summary>Vérifier</summary>

L'échantillonneur (une temperature supérieure à zéro choisit des tokens différents dans la même distribution) et le contexte (un autre system prompt, ou un historique de conversation que vous aviez oublié). Aucun des deux ne concerne les poids.

Les poids sont gelés à l'inférence. Si vous ne les avez pas modifiés, ils ne peuvent pas être l'explication, et c'est la première chose à écarter avant de conclure qu'un modèle est incohérent.

</details>

3. ▢ Vous donnez à un base model le prompt `Summarise this article:` suivi d'un article, et il produit un autre article au lieu d'un résumé. Le modèle est-il cassé ?

<details markdown="1"><summary>Vérifier</summary>

Non. Il fait exactement son travail : continuer un texte plausible. Dans son corpus d'entraînement, un article est bien plus souvent suivi d'un autre article que d'un résumé.

Le suivi d'instructions est un comportement entraîné. L'attendre d'un base model est l'erreur de débutant la plus courante, et elle est le plus souvent mal diagnostiquée comme un mauvais modèle ou un mauvais prompt.

</details>

4. ▢ Lequel de ces éléments le fine-tuning change-t-il ?

    - a) La temperature d'échantillonnage utilisée au moment du service
    - b) Les valeurs numériques stockées dans les poids du modèle
    - c) Les tokens présents dans la fenêtre de contexte du modèle
    - d) La taille du vocabulaire avec laquelle le modèle a été construit à l'origine

<details markdown="1"><summary>Vérifier</summary>

**b)** Les valeurs numériques stockées dans les poids du modèle.

La temperature est un réglage de service. Le contexte est une entrée propre à chaque requête. La taille du vocabulaire est fixée par le tokenizer et la matrice d'embeddings, et la changer est une opération bien plus invasive que le fine-tuning. Seules les valeurs des poids sont ce que l'entraînement déplace.

</details>

5. ▢ Donnez une raison de fine-tuner un modèle instruct plutôt qu'un base model, et une raison de faire l'inverse.

<details markdown="1"><summary>Vérifier</summary>

Partez d'un instruct quand vous voulez conserver le suivi d'instructions et l'utilité générale que vous ne pouvez pas vous permettre de reconstruire à partir d'un petit dataset, ce qui est presque toujours le cas.

Partez d'un base model quand le format de sortie de votre tâche est si éloigné d'un chat ordinaire que le comportement de chat hérité gêne activement : sortie structurée rigide, une seule étiquette de classification, ou une notation de domaine où le remplissage conversationnel n'est que du bruit.

</details>

## Exercices en situation réelle

- [ ] Exécutez n'importe quel modèle auquel vous avez accès en local ou via une API. Envoyez deux fois un prompt à temperature 0, puis deux fois à temperature 1. Notez quelle paire a coïncidé et pourquoi.
- [ ] Trouvez sur le Hugging Face Hub un modèle qui a à la fois une variante base et une variante instruct. Lisez les deux fiches de modèle et notez ce que la fiche instruct prétend avoir ajouté.
- [ ] Demain : donnez une question directe à un base model et notez ce qu'il fait au lieu d'y répondre. Gardez la sortie. Vous reconnaîtrez cet échec à l'étape 6.

## Pour aller plus loin

- [LLM Visualization, Brendan Bycroft](https://bbycroft.net/llm) : suivez pas à pas le trajet d'un seul token de bout en bout
- [The Illustrated Transformer, Jay Alammar](https://jalammar.github.io/illustrated-transformer/)
- [Glossaire](../GLOSSARY.md) : `fine-tuning` dans cet espace de travail désigne toujours la variante à base model gelé
- [Ressources](../RESOURCES.md)

---

Ça ne passe pas ? Relisez la source primaire en haut de page, car cette leçon la condense et c'est dans la condensation que la compréhension s'échappe. Consultez le [glossaire](../GLOSSARY.md) pour tout terme qui vous a paru glissant.

Si c'est la leçon elle-même qui n'est pas claire plutôt que la matière, c'est un défaut : [ouvrez une issue](https://github.com/TokenCemetery/teach/issues).
