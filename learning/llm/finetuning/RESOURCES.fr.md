---
title: "Ressources"
description: "Sources et communautés fiables pour le fine-tuning avec adapters"
type: resources
---

# Ressources sur le fine-tuning avec adapters

## Connaissances

### Les trois méthodes

- [Article : "LoRA: Low-Rank Adaptation of Large Language Models", Hu et al., arXiv:2106.09685](https://arxiv.org/abs/2106.09685)
  La méthode originale d'adapter de faible rang et l'argument de la dimension intrinsèque qui explique pourquoi elle fonctionne. À utiliser pour : l'étape 3, et ce que rank et alpha contrôlent réellement.

- [Article : "QLoRA: Efficient Finetuning of Quantized LLMs", Dettmers et al., arXiv:2305.14314](https://arxiv.org/abs/2305.14314)
  NF4, double quantification et optimizers paginés, avec le décompte de la mémoire détaillé. À utiliser pour : l'étape 4, et comme référence de ce qu'un base model quantifié coûte en qualité. Lisez la section sur les limites.

- [Article : "DoRA: Weight-Decomposed Low-Rank Adaptation", Liu et al., arXiv:2402.09353](https://arxiv.org/abs/2402.09353)
  Sépare les poids en magnitude et en direction, puis adapte la direction. À utiliser pour : l'étape 5. L'analyse de la section 4 sur la façon dont le full fine-tuning et LoRA déplacent chaque grandeur est l'argument véritable.

- [Article : "Intrinsic Dimensionality Explains the Effectiveness of Language Model Fine-Tuning", Aghajanyan et al., arXiv:2012.13255](https://arxiv.org/abs/2012.13255)
  Pourquoi l'adaptation peut tenir dans un sous-espace de faible dimension. À utiliser pour : la justification qui se trouve sous LoRA plutôt que son mécanisme.

### Pratique actuelle

- [Doc : "LoRA Without Regret", Hugging Face TRL](https://huggingface.co/docs/trl/main/en/lora_without_regret)
  L'argument selon lequel cibler toutes les couches linéaires avec un rank suffisant comble l'écart avec le full fine-tuning. À utiliser pour : le choix des target modules et du rank, et comme référence que toute nouvelle variante doit battre. Il remplace la convention « attention seule » héritée de l'article original.

- [Blog : "Practical Tips for Finetuning LLMs Using LoRA", Sebastian Raschka, Ahead of AI](https://magazine.sebastianraschka.com/p/practical-tips-for-finetuning-llms)
  Des ablations sur le rank, alpha et les target modules, avec les expériences montrées. À utiliser pour : confronter le folklore des hyperparamètres à des mesures.

- [Doc : PEFT, Hugging Face](https://huggingface.co/docs/peft)
  L'implémentation de référence des trois méthodes et la surface de configuration qu'elles exposent. À utiliser pour : savoir comment s'appelle un hyperparamètre en pratique, et quelles variantes sont assez établies pour être un simple flag. Sensible à la version : vérifiez dans la version installée plutôt que de mémoire.

- [Doc : SFTTrainer, Hugging Face TRL](https://huggingface.co/docs/trl/main/en/sft_trainer)
  La boucle standard de fine-tuning supervisé et ses formats de dataset. À utiliser pour : l'étape 3 et les suivantes. Sensible à la version : les noms de paramètres ont changé d'une version à l'autre.

### Fondations

- [Interactif : LLM Visualization, Brendan Bycroft](https://bbycroft.net/llm)
  Suivre pas à pas le trajet d'un seul token, avec le nombre de paramètres de chaque matrice. À utiliser pour : l'étape 1, et la meilleure réponse disponible à « où vivent les paramètres ».

- [Blog : "The Illustrated Transformer", Jay Alammar](https://jalammar.github.io/illustrated-transformer/)
  L'explication visuelle standard de l'architecture. À utiliser pour : l'étape 1 quand la structure des blocs n'est pas encore claire.

- [Doc : Chat Templates, Hugging Face Transformers](https://huggingface.co/docs/transformers/main/en/chat_templating)
  Comment les conversations sont transformées en séquences de tokens, et comment appliquer le gabarit propre au modèle. À utiliser pour : l'échec silencieux le plus fréquent du fine-tuning.

- [Article : "Decoupled Weight Decay Regularization" (AdamW), Loshchilov & Hutter, arXiv:1711.05101](https://arxiv.org/abs/1711.05101)
  L'optimizer que tout ce parcours utilise, et pourquoi son weight decay diffère de celui d'Adam. À utiliser pour : l'argument mémoire de l'étape 2.

- [Article : "ZeRO: Memory Optimizations Toward Training Trillion Parameter Models", Rajbhandari et al., arXiv:1910.02054](https://arxiv.org/abs/1910.02054)
  Le décompte canonique des poids, des gradients et de l'état de l'optimizer comme catégories de mémoire distinctes. À utiliser pour : dériver le chiffre de seize octets par paramètre.

- [Article : "Training Deep Nets with Sublinear Memory Cost", Chen et al., arXiv:1604.06174](https://arxiv.org/abs/1604.06174)
  Le gradient checkpointing, et l'échange de calcul contre de la mémoire qu'il opère. À utiliser pour : l'étape 2, et pour le réglage que vous laisserez activé en permanence.

- [Blog : "A Recipe for Training Neural Networks", Andrej Karpathy](https://karpathy.github.io/2019/04/25/recipe/)
  Comment mener des expériences dont les résultats veulent dire quelque chose. À utiliser pour : la leçon de diagnostic de l'étape 3, et le test de fumée qui consiste à faire surapprendre deux exemples.

### Quantification

- [Article : "LLM.int8(): 8-bit Matrix Multiplication for Transformers at Scale", Dettmers et al., arXiv:2208.07339](https://arxiv.org/abs/2208.07339)
  Le problème des features aberrantes qui rend la quantification des transformers plus difficile que l'arithmétique ne le laisse penser. À utiliser pour : pourquoi la quantification par blocs l'emporte sur la quantification par tenseur.

- [Doc : bitsandbytes quantization, Hugging Face Transformers](https://huggingface.co/docs/transformers/main/en/quantization/bitsandbytes)
  La surface de configuration 4 bits en pratique. À utiliser pour : la mise en place de l'étape 4.

- [Code : bitsandbytes, bitsandbytes-foundation](https://github.com/bitsandbytes-foundation/bitsandbytes)
  Le répertoire `backends/` fait autorité sur le matériel qui prend en charge chaque opération. À utiliser pour : trancher une question de prise en charge matérielle d'après le code source plutôt que d'après un tutoriel, qui dans ce domaine est le plus souvent périmé.

### Données et évaluation

- [Article : "LIMA: Less Is More for Alignment", Zhou et al., arXiv:2305.11206](https://arxiv.org/abs/2305.11206)
  La preuve qu'un petit dataset soigneusement constitué fait mieux qu'un grand dataset négligé, et que le SFT enseigne surtout le format. À utiliser pour : l'argument d'ouverture de l'étape 6.

- [Article : "Judging LLM-as-a-Judge with MT-Bench and Chatbot Arena", Zheng et al., arXiv:2306.05685](https://arxiv.org/abs/2306.05685)
  L'évaluation par modèle-juge avec ses biais caractérisés : position, verbosité, auto-préférence. À utiliser pour : les métriques de génération libre, et pour comprendre pourquoi le juge doit être calibré face à des étiquettes humaines.

- [Article : "An Empirical Study of Catastrophic Forgetting in Large Language Models During Continual Fine-tuning", Luo et al., arXiv:2308.08747](https://arxiv.org/abs/2308.08747)
  L'oubli est mesurable, courant, et ne se limite pas à des cas marginaux. À utiliser pour : justifier le jeu de régression auprès de quelqu'un qui y voit une charge inutile.

- [Article : "Fine-tuning Aligned Language Models Compromises Safety, Even When Users Do Not Intend To!", Qi et al., arXiv:2310.03693](https://arxiv.org/abs/2310.03693)
  Le comportement de sécurité se dégrade après un fine-tuning sur des données bénignes. À utiliser pour : comprendre pourquoi le jeu de régression doit inclure des cas de refus.

- [Code : lm-evaluation-harness, EleutherAI](https://github.com/EleutherAI/lm-evaluation-harness)
  Les implémentations standard de benchmarks et les problèmes de contamination qu'elles documentent. À utiliser pour : construire une eval, et lire les scores publiés avec scepticisme.

### Mise en service

- [Doc : LoRA adapters, vLLM](https://docs.vllm.ai/en/latest/features/lora.html)
  Servir des adapters en production, y compris le routage multi-adapters. À utiliser pour : l'étape 7. Vérifiez les limites de rank maximal et de nombre maximal d'adapters dans la version installée.

- [Article : "S-LoRA: Serving Thousands of Concurrent LoRA Adapters", Sheng et al., arXiv:2311.03285](https://arxiv.org/abs/2311.03285)
  Comment regrouper en batch de nombreux adapters sur un base model partagé de façon efficace. À utiliser pour : comprendre pourquoi servir plusieurs adapters est un problème résolu et non une idée de recherche.

- [Blog : "LLM Inference Performance Engineering: Best Practices", Databricks](https://www.databricks.com/blog/llm-inference-performance-engineering-best-practices)
  Prefill contre decode, et ce qui limite chaque phase. À utiliser pour : l'arithmétique des coûts de l'étape 7.

### L'alternative

- [Article : "Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks", Lewis et al., arXiv:2005.11401](https://arxiv.org/abs/2005.11401)
  L'énoncé canonique de l'approche qu'il faut généralement préférer quand le problème est une question de connaissances. À utiliser pour : l'argument de la dernière leçon, et pour plaider de façon crédible contre le fine-tuning.

## Sagesse (communautés)

- [r/LocalLLaMA](https://www.reddit.com/r/LocalLLaMA/)
  La plus grande concentration de personnes qui font du fine-tuning sur du matériel grand public, sur tous les backends. À utiliser pour : chercher ce qui a déjà fonctionné dans un budget mémoire donné, repérer le folklore qui mérite d'être testé, et lire des comptes rendus de réplication de nouvelles méthodes. Lisez les archives : poster est un exercice, pas une source.

- [Hugging Face Forums](https://discuss.huggingface.co/)
  Consultables et archivés, avec la présence des auteurs des bibliothèques. À utiliser pour : le comportement de PEFT, de TRL et de `transformers` que la documentation laisse ambigu.

- [EleutherAI Blog](https://blog.eleuther.ai/)
  Des comptes rendus d'un groupe qui lit son propre domaine de façon critique, résultats négatifs compris. À utiliser pour : les jugements des étapes 5 et 7 sur la généralisation d'un résultat annoncé. Leur Discord est l'endroit où cela se discute en premier, et il n'est volontairement pas listé : rien de ce qui s'y dit n'est retrouvable plus tard.

- [MLX Discussions, ml-explore/mlx](https://github.com/ml-explore/mlx/discussions)
  Public, consultable, avec des réponses des mainteneurs. À utiliser pour : vérifier si une opération donnée est déjà prise en charge sur Apple Silicon, la question ayant généralement déjà été posée.

## Lacunes

- Aucune source ne suit quelles versions de `torch`, PEFT, TRL et des bibliothèques de quantification fonctionnent réellement ensemble sur une version de Python et une plateforme données. Cela bloque un premier run plus souvent que n'importe quel concept, et chaque environnement doit être vérifié dans les notes de version plutôt que supposé.
- La couverture des opérations 4 bits par les backends matériels change d'une version à l'autre. Aucun document n'est fiable ici : le code source de la bibliothèque est la seule autorité, et toute affirmation de tutoriel sur le matériel requis doit être considérée comme périmée.
- Aucune source fiable pour l'instant sur la conception d'évaluations propres à l'adaptation de petits modèles à une tâche. C'est le maillon le plus faible de l'étape 6 et la partie la plus difficile de la mission. La littérature générale sur l'évaluation vise le benchmarking des foundation models, pas la preuve qu'un adapter étroit a aidé.
- La plupart des conseils publiés sur les hyperparamètres de LoRA visent des modèles de 7B et plus. Peu d'entre eux examinent s'ils se transposent à la classe 1B à 3B, où la plupart des gens commencent réellement.
- Aucune réplication indépendante recensée pour DoRA à l'échelle dont bénéficient LoRA et QLoRA. Considérez ses gains annoncés comme devant être mesurés localement.
- Aucune source retenue pour le décodage contraint, que la leçon 27 recommande comme bonne réponse aux problèmes de validité de schéma. Il est nommé sans référence derrière lui.
