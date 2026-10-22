---
title: "Ressources"
description: "Sources fiables pour les transformers"
type: resources
---

# Ressources sur les transformers

## Connaissances

- [Article : "Attention Is All You Need", Vaswani et al., 2017](https://arxiv.org/abs/1706.03762)
  L'article d'origine du transformer : la scaled dot-product attention, la multi-head attention et le bloc encodeur-décodeur complet que cet espace de travail dérive à partir de tenseurs bruts. À utiliser pour : la définition primaire de chaque pièce que cet espace de travail implémente.
- [Billet : "The Illustrated Transformer", Jay Alammar](https://jalammar.github.io/illustrated-transformer/)
  Parcours visuel, fondé d'abord sur l'intuition, de l'attention et du bloc transformer, conçu pour être lu avant la notation de l'article. À utiliser pour : se faire un modèle mental opérationnel avant d'implémenter quoi que ce soit.
- [Billet : "The Annotated Transformer", Harvard NLP](http://nlp.seas.harvard.edu/annotated-transformer/)
  Implémentation PyTorch de l'article ligne par ligne, à partir d'opérations brutes sur les tenseurs, rapprochée directement des équations qui les produisent. À utiliser pour : vérifier ligne par ligne une implémentation à partir de zéro par rapport à une référence.
- [Dépôt : nanoGPT, Karpathy](https://github.com/karpathy/nanoGPT)
  Implémentation PyTorch minimale et lisible d'un transformer de style GPT avec sa boucle d'entraînement, assez petite pour être lue en entier. À utiliser pour : la moitié boucle d'entraînement de la mission, une fois que le bloc lui-même fonctionne.
- [Vidéo : "Let's build GPT: from scratch, in code, spelled out", Karpathy](https://www.youtube.com/watch?v=kCc8FmEb1nY)
  Construit à l'écran l'attention et une boucle d'entraînement de GPT à partir de tenseurs bruts, pas à pas, en dérivant chaque pièce au lieu de la présenter terminée. À utiliser pour : regarder la dérivation se faire avant d'écrire le code vous-même, ou en même temps.
- [Doc : "Autograd mechanics", PyTorch](https://pytorch.org/docs/stable/notes/autograd.html)
  Explication officielle de la façon dont l'autograd de PyTorch calcule réellement les gradients à travers un graphe de calcul. À utiliser pour : comprendre ce que la passe arrière fait aux poids, au lieu de seulement appeler `.backward()`.
- [Dépôt : transformers, Hugging Face](https://github.com/huggingface/transformers)
  Une vraie bibliothèque de modèles de production, utile une fois que les pièces à partir de zéro existent. À utiliser pour : repérer l'attention, la projection multi-head et le bloc transformer dans du code écrit pour la production plutôt que pour l'enseignement.
- [Article : "Layer Normalization", Ba, Kiros et Hinton, 2016](https://arxiv.org/abs/1607.06450)
  Introduit la layer normalization : normaliser les activations propres à chaque exemple sur la dimension des features, indépendamment de la taille du batch, contrairement à la batch normalization. À utiliser pour : comprendre ce que la layer norm calcule réellement et pourquoi elle convient aux séquences de longueur variable et aux petites tailles de batch.
- [Article : "On Layer Normalization in the Transformer Architecture", Xiong et al., 2020](https://arxiv.org/abs/2002.04745)
  Compare le placement de la layer norm après l'addition résiduelle (le choix de l'article d'origine, post-norm) au placement avant chaque sous-couche, à l'intérieur de la branche résiduelle (pre-norm), et montre pourquoi le pre-norm s'entraîne de façon plus stable à plus grande profondeur. À utiliser pour : comprendre pourquoi la plupart des grands modèles actuels utilisent le pre-norm alors que l'article du transformer d'origine utilisait le post-norm.
- [Article : "Using the Output Embedding to Improve Language Models", Press et Wolf, 2017](https://arxiv.org/abs/1608.05859)
  Plaide pour lier les matrices de poids de l'embedding d'entrée et de la projection de sortie, puisque les deux rattachent un token à la même représentation sous-jacente, ce qui retire une grande fraction des paramètres d'un modèle à grand vocabulaire. À utiliser pour : comprendre le weight tying comme un choix de conception délibéré, et pas seulement comme une astuce d'économie de paramètres.
- [Doc : "torch.nn.functional.cross_entropy", PyTorch](https://pytorch.org/docs/stable/generated/torch.nn.functional.cross_entropy.html)
  Documentation officielle de l'opération fusionnée softmax plus log-vraisemblance négative, qui prend directement les logits bruts par souci de stabilité numérique au lieu d'exiger d'abord une étape softmax séparée. À utiliser pour : comment la loss d'entropie croisée est réellement calculée en pratique, et pas seulement sa formule.
- [Article : "Adam: A Method for Stochastic Optimization", Kingma et Ba, 2015](https://arxiv.org/abs/1412.6980)
  Introduit le momentum d'Adam (premier moment) et la mise à l'échelle adaptative par paramètre (second moment) par rapport à la descente de gradient simple, avec une correction de biais pour les deux. À utiliser pour : comprendre ce que calcule la règle de mise à jour d'Adam et pourquoi, avant la correction du weight decay d'AdamW.
- [Article : "Decoupled Weight Decay Regularization", Loshchilov et Hutter, 2019](https://arxiv.org/abs/1711.05101)
  Identifie pourquoi intégrer le weight decay au gradient dans l'Adam d'origine interagit mal avec sa mise à l'échelle adaptative, et le corrige en appliquant la décroissance directement aux poids. À utiliser pour : pourquoi AdamW, et non Adam simple, est l'optimiseur standard pour entraîner les transformers.
- [Article : "Neural Machine Translation of Rare Words with Subword Units", Sennrich, Haddow et Birch, 2016](https://arxiv.org/abs/1508.07909)
  Introduit le byte-pair encoding pour la tokenisation en sous-mots : fusionner itérativement la paire de symboles adjacents la plus fréquente pour construire un vocabulaire à partir des octets bruts. À utiliser pour : dériver le mécanisme de tokenizer que `llm/finetuning` nomme en passant au lieu de le répéter.
- [Article : "RoFormer: Enhanced Transformer with Rotary Position Embedding", Su et al., 2021](https://arxiv.org/abs/2104.09864)
  Introduit RoPE : faire tourner les vecteurs de requête et de clé projetés d'un angle proportionnel à la position, ce qui produit un score d'attention qui ne dépend que du décalage relatif. À utiliser pour : le mécanisme que presque tous les modèles ouverts actuels utilisent à la place de l'encodage positionnel sinusoïdal ou appris.
- [Article : "Root Mean Square Layer Normalization", Zhang et Sennrich, 2019](https://arxiv.org/abs/1910.07467)
  Introduit RMSNorm, en faisant l'hypothèse que l'opération de recentrage de la layer norm (soustraction de la moyenne) est superflue et que la remise à l'échelle seule explique l'essentiel de son bénéfice. À utiliser pour : la normalisation moins coûteuse que les modèles actuels placent dans la branche pre-norm que dérive la leçon 5.
- [Article : "GLU Variants Improve Transformer", Shazeer, 2020](https://arxiv.org/abs/2002.05202)
  Teste des variantes de gated linear unit (dont SwiGLU, à porte Swish) dans la sous-couche feed-forward du transformer, et trouve que certaines surpassent le ReLU ou le GELU habituellement utilisés. À utiliser pour : la conception à porte, à deux projections vers le haut, qui remplace dans les modèles actuels le bloc feed-forward à projection unique de la leçon 6.
- [Article : "GQA: Training Generalized Multi-Query Transformer Models from Multi-Head Checkpoints", Ainslie et al., 2023](https://arxiv.org/abs/2305.13245)
  Introduit la grouped-query attention comme compromis entre la multi-head attention complète et la tête unique de clés et de valeurs partagée de la multi-query attention, plus une recette peu coûteuse pour convertir par uptraining un checkpoint multi-head existant en un tel modèle. À utiliser pour : pourquoi moins de têtes de clés et de valeurs échangent un peu de qualité contre un KV cache bien plus petit et une inférence plus rapide.
- [Article : "The Curious Case of Neural Text Degeneration", Holtzman et al., 2019](https://arxiv.org/abs/1904.09751)
  Documente pourquoi maximiser la vraisemblance au moment du décodage (décodage glouton) produit un texte fade et répétitif alors que la vraisemblance est un bon objectif d'entraînement, et introduit l'échantillonnage nucleus (top-p) comme remède. À utiliser pour : la raison précise pour laquelle une coupure dynamique, fondée sur la probabilité cumulée, bat à la fois le décodage glouton et un nombre top-k fixe.
- [Article : "On the difficulty of training Recurrent Neural Networks", Pascanu, Mikolov et Bengio, 2013](https://arxiv.org/abs/1211.5063)
  Analyse les problèmes de disparition et d'explosion du gradient et propose l'écrêtage de la norme du gradient comme remède au second. À utiliser pour : pourquoi l'écrêtage remet à l'échelle tout le vecteur gradient par sa norme au lieu de plafonner indépendamment le gradient de chaque paramètre.
- [Article : "Mixed Precision Training", Micikevicius et al., 2018](https://arxiv.org/abs/1710.03740)
  Introduit l'entraînement en demi-précision avec une copie maître des poids en pleine précision et un loss scaling pour contrer la plage numérique limitée de la demi-précision, ce qui réduit l'usage mémoire de près de moitié. À utiliser pour : ce qu'il faut exactement ajouter à un entraînement en demi-précision simple pour éviter que les petites mises à jour et les petits gradients tombent à zéro par underflow.
- [Article : "BERT: Pre-training of Deep Bidirectional Transformers for Language Understanding", Devlin et al., 2018](https://arxiv.org/abs/1810.04805)
  Introduit l'architecture encoder-only : une attention bidirectionnelle conditionnée conjointement sur le contexte de gauche et de droite à chaque couche, sans masque causal. À utiliser pour : pourquoi un modèle encoder-only construit une représentation d'une entrée complète au lieu de générer du texte de façon autorégressive, et ne peut pas faire ce que fait le modèle decoder-only de cet espace de travail.
- [Article : "Exploring the Limits of Transfer Learning with a Unified Text-to-Text Transformer" (T5), Raffel et al., 2019](https://arxiv.org/abs/1910.10683)
  Ramène un large éventail de tâches de NLP à un seul format text-to-text cohérent, de type encodeur-décodeur. À utiliser pour : la sous-couche de cross-attention de la forme encodeur-décodeur, et pourquoi elle convient à une tâche à séparation entrée puis sortie nette et fixe.
- [Article : "FlashAttention: Fast and Memory-Efficient Exact Attention with IO-Awareness", Dao et al., 2022](https://arxiv.org/abs/2205.14135)
  Diagnostique la lenteur de l'attention standard sur les longues séquences comme un problème d'entrées-sorties (lectures et écritures mémoire entre la HBM et la SRAM), et non de calcul, et introduit un algorithme exact, découpé en tuiles, qui évite de matérialiser la matrice complète des scores. À utiliser pour : pourquoi une vraie implémentation de l'attention paraît structurellement différente de la version de la leçon 1 tout en calculant le même résultat.
- [Article : "Switch Transformers: Scaling to Trillion Parameter Models with Simple and Efficient Sparsity", Fedus, Zoph et Shazeer, 2021](https://arxiv.org/abs/2101.03961)
  Introduit un schéma de routage MoE simplifié, un expert par token, qui découple le nombre total de paramètres du coût de calcul par token. À utiliser pour : le compromis précis que font les modèles à activation parcimonieuse, et pourquoi simplifier le routage à un seul expert a réglé des instabilités que des conceptions de MoE plus complexes avaient rencontrées.

## Lacunes

- Aucune source pour l'instant sur le calendrier exact de warmup du learning rate suivi d'une décroissance ; la leçon 19 le dérive de la forme indiquée dans les propres détails d'entraînement de l'article du transformer d'origine (warmup linéaire, puis décroissance proportionnelle à l'inverse de la racine carrée du numéro de pas), mais un extrait direct et fraîchement vérifié de cette section n'a pas pu être obtenu avec les outils disponibles pendant cette session (la page de résumé de l'article ne contient pas la section sur les détails d'entraînement, et les autres sources PDF ne se sont pas extraites en texte lisible). À revoir si une source plus propre devient disponible.
