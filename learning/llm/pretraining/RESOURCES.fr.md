---
title: "Ressources"
description: "Sources fiables pour le pré-entraînement des LLM"
type: resources
---

# Ressources sur le pré-entraînement des LLM

## Connaissances

- [Article : "Scaling Laws for Neural Language Models", Kaplan et al., 2020](https://arxiv.org/abs/2001.08361)
  Ajuste les relations en loi de puissance d'origine entre la loss, le calcul, le nombre de paramètres et les données, et plaide pour faire croître les paramètres plus vite que les données. À utiliser pour : l'étape 3, comme point de départ que Chinchilla révise ensuite.
- [Article : "Training Compute-Optimal Large Language Models", Hoffmann et al., 2022](https://arxiv.org/abs/2203.15556)
  L'article Chinchilla. Réajuste les lois d'échelle avec un balayage plus large et conclut que les paramètres et les tokens doivent croître ensemble, à raison d'environ vingt tokens par paramètre, ce qui renverse la recommandation de Kaplan, lourde en paramètres. À utiliser pour : le résultat central de l'étape 3, et le budget de tokens que la plupart des runs d'entraînement modernes utilisent réellement.
- [Article : "ZeRO: Memory Optimizations Toward Training Trillion Parameter Models", Rajbhandari et al., 2019](https://arxiv.org/abs/1910.02054)
  Définit les trois stages ZeRO, qui partitionnent l'état de l'optimizer, puis les gradients, puis les paramètres entre des appareils en parallélisme de données. À utiliser pour : la technique centrale de l'étape 5, que FSDP implémente.
- [Documentation : "Fully Sharded Data Parallel", PyTorch](https://pytorch.org/docs/stable/fsdp.html)
  La référence de l'API du partitionnement de type ZeRO stage 3 de PyTorch, y compris les stratégies de partitionnement et les politiques d'enveloppement (wrapping) que le lab d'une leçon fait réellement tourner. À utiliser pour : les exercices pratiques de l'étape 5.
- [Article : "Efficient Large-Scale Language Model Training on GPU Clusters Using Megatron-LM", Narayanan et al., 2021](https://arxiv.org/abs/2104.04473)
  Combine le parallélisme tensoriel, le parallélisme de pipeline et le parallélisme de données dans un seul système, avec les compromis de débit et de mémoire de chacun mesurés les uns face aux autres. À utiliser pour : la technique centrale de l'étape 6 et ses chiffres détaillés.
- [Documentation : "DeepSpeed", Microsoft](https://github.com/microsoft/DeepSpeed)
  Une seconde implémentation de production de ZeRO accompagnée du parallélisme 3D, avec des exemples de configuration qu'une leçon peut citer comme second système concret à côté de FSDP et de Megatron-LM. À utiliser pour : les étapes 5 et 6, comme recoupement pour vérifier qu'une affirmation porte sur la technique plutôt que sur l'API d'une seule bibliothèque.
- [Article : "The Pile: An 800GB Dataset of Diverse Text for Language Modeling", Gao et al., 2020](https://arxiv.org/abs/2101.00027)
  Un corpus de pré-entraînement entièrement documenté : quelles sources y sont entrées, dans quelles proportions, et pourquoi. À utiliser pour : l'étape 1, comme exemple détaillé d'une décision de mélange de données rendue explicite.
- [Article : "Deduplicating Training Data Makes Language Models Better", Lee et al., 2021](https://arxiv.org/abs/2107.06499)
  Montre que les textes quasi dupliqués et les longues sous-chaînes répétées provoquent une mémorisation mot pour mot, et donne deux techniques de déduplication (correspondance exacte de sous-chaînes via un suffix array, et correspondance de quasi-doublons via MinHash), chacune mesurée sur un vrai corpus. À utiliser pour : le contenu sur la déduplication de l'étape 1, avec des chiffres concrets avant/après.
- [Article : "Language Models are Few-Shot Learners", Brown et al., 2020](https://arxiv.org/abs/2005.14165)
  L'article GPT-3. L'annexe A documente un pipeline concret de filtrage de qualité : un classifieur entraîné à distinguer un texte sélectionné du Common Crawl brut, utilisé pour rééchantillonner celui-ci vers les documents les mieux notés, accompagné d'une passe distincte de déduplication floue. À utiliser pour : le contenu sur le filtrage de qualité de l'étape 1, comme exemple détaillé que l'article sur la déduplication ci-dessus ne fournit pas lui-même.
- [Article : "Neural Machine Translation of Rare Words with Subword Units", Sennrich et al., 2015](https://arxiv.org/abs/1508.07909)
  Introduit le byte-pair encoding pour la tokenisation en sous-mots, l'algorithme sur lequel s'appuient encore la plupart des tokenizers modernes. À utiliser pour : l'algorithme central de l'étape 2.
- [Article : "SentencePiece: A simple and language independent subword tokenizer and detokenizer for Neural Text Processing", Kudo et Richardson, 2018](https://arxiv.org/abs/1808.06226)
  Traite la tokenisation comme opérant directement sur du texte brut, sans étape de pré-tokenisation propre à une langue, et couvre la tokenisation par modèle de langue unigramme comme alternative au BPE. À utiliser pour : le second algorithme de l'étape 2 et le compromis sur la taille du vocabulaire.
- [Article : "Scaling Language Models: Methods, Analysis & Insights from Training Gopher", Rae et al., 2021](https://arxiv.org/abs/2112.11446)
  Un récit détaillé et honnête d'un grand run d'entraînement, y compris les endroits où des pics de loss et de l'instabilité sont apparus et ce que les auteurs en ont fait. À utiliser pour : l'étude de cas centrale de l'étape 7.
- [Article : "LLaMA: Open and Efficient Foundation Language Models", Touvron et al., 2023](https://arxiv.org/abs/2302.13971)
  Une recette d'entraînement publiée et reproductible : mélange de données, tokenizer, schéma et hyperparamètres, énoncés assez clairement pour y confronter les affirmations d'une leçon. À utiliser pour : recouper les étapes 1 à 3 et 7 avec une vraie recette complète.
- [Article : "OPT: Open Pre-trained Transformer Language Models", Zhang et al., 2022](https://arxiv.org/abs/2205.01068)
  Publié avec un journal de bord public des problèmes d'infrastructure que les auteurs ont réellement rencontrés en entraînant un modèle de 175B : pannes matérielles, redémarrages manuels et automatiques, divergences de la loss, et la procédure de reprise concrète employée pour chacun. À utiliser pour : l'étude de cas centrale de l'étape 8, et un second exemple réel du schéma de divergence de la loss que couvre l'étape 7.
- [Article : "Don't Stop Pretraining: Adapt Language Models to Domains and Tasks", Gururangan et al., 2020](https://arxiv.org/abs/2004.10964)
  Montre que poursuivre le pré-entraînement d'un modèle existant à large couverture (pré-entraînement adaptatif au domaine) améliore systématiquement les performances sur le domaine cible, sur quatre domaines et huit tâches, dans des contextes riches comme pauvres en ressources, sans entraîner un nouveau modèle à partir de zéro. À utiliser pour : l'argument central de l'étape 10 selon lequel pré-entraîner à partir de zéro est généralement le mauvais choix par défaut.

## Lacunes

- L'article OPT documente la fréquence réelle des pannes et la procédure de reprise, mais n'énonce pas de politique précise d'intervalle entre checkpoints (à quelle fréquence les checkpoints ont réellement été sauvegardés). Le compromis sur la fréquence des checkpoints de l'étape 8 est enseigné à partir d'un raisonnement d'ingénierie général plutôt que d'une politique énoncée ; une source primaire avec un intervalle concret le renforcerait.
- Le filtrage par classifieur de GPT-3 (2020) est le seul exemple détaillé de filtrage de qualité listé à ce jour. Les corpus construits depuis 2023 (FineWeb, Dolma) filtrent bien plus agressivement et le documentent plus en profondeur ; une source primaire plus récente renforcerait l'étape 1.
