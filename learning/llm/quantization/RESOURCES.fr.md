---
title: "Ressources"
description: "Sources fiables pour la quantification des LLM"
type: resources
---

# Ressources sur la quantification

## Connaissances

### Les fondations

- [Article : "A White Paper on Neural Network Quantization", Nagel et al., 2021](https://arxiv.org/abs/2106.08295)
  Une introduction de la taille d'un manuel par Qualcomm AI Research : la motivation matérielle, le quantificateur affine uniforme, le choix de la plage, la granularité, les pipelines PTQ et QAT, et une méthode de débogage. À utiliser pour : la correspondance et le choix de la plage des étapes 2 et 6, à la source plutôt que dans un résumé.
- [Article : "A Survey of Quantization Methods for Efficient Neural Network Inference", Gholami et al., 2021](https://arxiv.org/abs/2103.13630)
  Un large panorama des quantificateurs uniformes et non uniformes, de la granularité, du PTQ face au QAT et de la précision mixte. À utiliser pour : situer une méthode dans la famille plus large avant de lire son propre article.
- [Article : "Quantization and Training of Neural Networks for Efficient Integer-Arithmetic-Only Inference", Jacob et al., 2017](https://arxiv.org/abs/1712.05877)
  Le schéma d'inférence en entiers seuls derrière la plupart des déploiements int8 : la correspondance affine avec un zéro exactement représentable, et l'entraînement avec quantification simulée. À utiliser pour : l'origine de la convention du scale et du zero-point.

### Formats de nombres

- [Article : "Mixed Precision Training", Micikevicius et al., 2017](https://arxiv.org/abs/1710.03740)
  L'entraînement en fp16 avec une copie maître en fp32 et du loss scaling, et pourquoi la plage étroite du fp16 rend ce scaling nécessaire. À utiliser pour : ce que coûtent les cinq bits d'exposant du fp16.
- [Article : "A Study of BFLOAT16 for Deep Learning Training", Kalamkar et al., 2019](https://arxiv.org/abs/1905.12322)
  Le plaidoyer pour le bf16, qui garde l'exposant du fp32 et abandonne des bits de mantisse. À utiliser pour : pourquoi la plage comptait plus que la précision pour l'entraînement.
- [Article : "FP8 Formats for Deep Learning", Micikevicius et al., 2022](https://arxiv.org/abs/2209.05433)
  Les encodages à virgule flottante sur huit bits E4M3 et E5M2, leurs valeurs spéciales, et des résultats d'entraînement et d'inférence avec eux. À utiliser pour : à quoi sert chaque variante de fp8.
- [Article : "Microscaling Data Formats for Deep Learning", Rouhani et al., 2023](https://arxiv.org/abs/2310.10537)
  Des formats à échelle par bloc dans lesquels un bloc d'éléments étroits partage un scale en puissance de deux, la base des formats MX de l'OCP. À utiliser pour : comment MXFP4 et ses cousins stockent un bloc.
- [Billet : "Introducing NVFP4 for Efficient and Accurate Low-Precision Inference", NVIDIA Technical Blog](https://developer.nvidia.com/blog/introducing-nvfp4-for-efficient-and-accurate-low-precision-inference/)
  Le format à virgule flottante en 4 bits d'un fournisseur, avec un bloc plus petit et un scale plus fin que MXFP4. À utiliser pour : en quoi NVFP4 diffère de MXFP4, à lire comme de la documentation de fournisseur.

### Outliers

- [Article : "LLM.int8(): 8-bit Matrix Multiplication for Transformers at Scale", Dettmers et al., 2022](https://arxiv.org/abs/2208.07339)
  Découvre les dimensions de features outlier qui cassent l'int8 dans les grands transformers, et les garde en 16 bits avec une décomposition en précision mixte. À utiliser pour : où apparaissent les outliers et la première parade.
- [Article : "Massive Activations in Large Language Models", Sun et al., 2024](https://arxiv.org/abs/2402.17762)
  Des activations isolées supérieures de plusieurs ordres de grandeur aux autres, à des dimensions fixes et à des tokens précis, qui jouent le rôle de biais appris. À utiliser pour : le second motif d'outliers et pourquoi ce n'est pas du bruit.
- [Article : "Quantizable Transformers: Removing Outliers by Helping Attention Heads Do Nothing", Bondarenko et al., 2023](https://arxiv.org/abs/2306.12929)
  Relie les outliers à des têtes d'attention qui apprennent à ne rien faire, et les supprime par un changement d'architecture pendant l'entraînement. À utiliser pour : pourquoi les outliers existent.

### Quantification post-entraînement

- [Article : "The case for 4-bit precision: k-bit Inference Scaling Laws", Dettmers et Zettlemoyer, 2022](https://arxiv.org/abs/2212.09720)
  Plus de 35 000 expériences zero-shot sur des largeurs en bits, des types de données et des tailles de bloc, qui trouvent que 4 bits sont presque toujours optimaux pour un nombre de bits de modèle fixé, aidés seulement par les petits blocs et le choix du type de données. À utiliser pour : pourquoi les poids en 4 bits sont devenus la valeur par défaut, et ce qu'apporte la taille de bloc.
- [Article : "Up or Down? Adaptive Rounding for Post-Training Quantization", Nagel et al., 2020](https://arxiv.org/abs/2004.10568)
  Montre qu'arrondir chaque poids à son niveau le plus proche n'est pas optimal pour la sortie de la couche, et apprend plutôt le sens de l'arrondi. À utiliser pour : pourquoi l'arrondi au plus proche laisse de la précision de côté.
- [Article : "Optimal Brain Compression", Frantar et Alistarh, 2022](https://arxiv.org/abs/2208.11580)
  La méthode de quantification exacte couche par couche que GPTQ rend rapide, avec la mise à jour qui dépense l'erreur d'un poids sur les autres. À utiliser pour : la filiation de GPTQ.
- [Article : "GPTQ: Accurate Post-Training Quantization for Generative Pre-trained Transformers", Frantar et al., 2022](https://arxiv.org/abs/2210.17323)
  Quantification des poids en 3 et 4 bits en une passe avec de l'information approchée du second ordre, à l'échelle de modèles de 175 milliards de paramètres. À utiliser pour : comment fonctionne GPTQ et ce qu'est son calibration set.
- [Article : "AWQ: Activation-aware Weight Quantization for LLM Compression and Acceleration", Lin et al., 2023](https://arxiv.org/abs/2306.00978)
  Constate qu'une petite fraction des canaux de poids compte le plus, repérée par la grandeur de l'activation, et la protège par un scaling par canal plutôt que par la précision mixte. À utiliser pour : comment fonctionne AWQ et pourquoi il n'a pas besoin de rétropropagation.
- [Article : "SmoothQuant: Accurate and Efficient Post-Training Quantization for Large Language Models", Xiao et al., 2022](https://arxiv.org/abs/2211.10438)
  Déplace les outliers d'activation vers les poids avec un scale par canal mathématiquement équivalent, ce qui permet le W8A8. À utiliser pour : la quantification des poids et des activations en 8 bits.
- [Article : "QuaRot: Outlier-Free 4-Bit Inference in Rotated LLMs", Ashkboos et al., 2024](https://arxiv.org/abs/2404.00456)
  Fait pivoter les états cachés avec des transformées de Hadamard pour que les poids, les activations et le KV cache se quantifient tous en 4 bits. À utiliser pour : comment les rotations suppriment les outliers.
- [Article : "SpinQuant: LLM Quantization with Learned Rotations", Liu et al., 2024](https://arxiv.org/abs/2405.16406)
  Apprend les matrices de rotation au lieu de les fixer, et montre que la qualité des rotations aléatoires varie beaucoup. À utiliser pour : pourquoi le choix de la rotation compte.
- [Article : "KIVI: A Tuning-Free Asymmetric 2bit Quantization for KV Cache", Liu et al., 2024](https://arxiv.org/abs/2402.02750)
  Constate que les clés doivent être quantifiées par canal et les valeurs par token, et fait les deux en 2 bits. À utiliser pour : le choix de l'axe dans la quantification du KV cache.
- [Article : "KVQuant: Towards 10 Million Context Length LLM Inference with KV Cache Quantization", Hooper et al., 2024](https://arxiv.org/abs/2401.18079)
  Quantification des clés par canal avant l'embedding rotatif, types non uniformes et traitement des outliers pour des contextes très longs. À utiliser pour : ce que la quantification du KV cache apporte à contexte long.
- [Dépôt : gptq, IST-DASLab](https://github.com/IST-DASLab/gptq)
  L'implémentation de référence des auteurs de GPTQ, dont le README documente `--act-order` (quantifier les colonnes par taille d'activation décroissante), `--true-sequential` et `--static-groups`. À utiliser pour : l'act-order et le tenseur `g_idx`, que l'article ne décrit pas.

### Quantization-aware training

- [Article : "Estimating or Propagating Gradients Through Stochastic Neurons for Conditional Computation", Bengio et al., 2013](https://arxiv.org/abs/1308.3432)
  Introduit et compare des estimateurs de gradient à travers des seuils durs, dont l'estimateur straight-through. À utiliser pour : l'origine du STE.
- [Article : "LLM-QAT: Data-Free Quantization Aware Training for Large Language Models", Liu et al., 2023](https://arxiv.org/abs/2305.17888)
  Du QAT sur des LLM avec des données que le modèle génère lui-même, y compris la quantification du KV cache, comparé au PTQ en 4 bits. À utiliser pour : ce que le QAT récupère sur un LLM et à quel coût.
- [Article : "QLoRA: Efficient Finetuning of Quantized LLMs", Dettmers et al., 2023](https://arxiv.org/abs/2305.14314)
  NF4, double quantification et entraînement d'adapters à travers un modèle de base gelé en 4 bits. À utiliser pour : la frontière avec le QAT, et la source d'où part le parcours de fine-tuning.
- [Billet : "Quantization-Aware Training for Large Language Models with PyTorch", PyTorch Blog, 2024](https://pytorch.org/blog/quantization-aware-training/)
  Le flux QAT de torchao sur Llama 2 et Llama 3, avec la récupération mesurée face au PTQ et le surcoût de fine-tuning de la fake quantization. À utiliser pour : ce que le QAT récupère et coûte sur un vrai LLM, à lire comme les mesures d'une équipe.

### Matériel et mise en service

- [Article : "MARLIN: Mixed-Precision Auto-Regressive Parallel Inference on Large Language Models", Frantar et al., 2024](https://arxiv.org/abs/2408.11743)
  Un kernel GPU à poids en 4 bits et activations en 16 bits, et une analyse de quand la quantification des poids seuls accélère le décodage par batch. À utiliser pour : pourquoi le gain de vitesse dépend de la taille de batch.
- [Article : "QServe: W4A8KV4 Quantization and System Co-design for Efficient LLM Serving", Lin et al., 2024](https://arxiv.org/abs/2405.04532)
  Montre que le surcoût de déquantification peut effacer le gain des schémas 4 bits sur GPU, et co-conçoit un format et un kernel pour l'éviter. À utiliser pour : pourquoi moins de bits n'est pas automatiquement plus rapide.
- [Doc : "Quantization", vLLM](https://docs.vllm.ai/en/latest/features/quantization/)
  Les schémas pris en charge par un moteur de serving et sur quel matériel. À utiliser pour : vérifier qu'un schéma a un kernel avant de le choisir.
- [Doc : "Quantized KV Cache", vLLM](https://docs.vllm.ai/en/latest/features/quantization/quantized_kvcache/)
  Le KV cache en fp8 : scales par tenseur ou par tête, scales par défaut sans calibration, et leur calibration avec llm-compressor. À utiliser pour : ce dont un KV cache en 8 bits a besoin en pratique.
- [Doc : "Quantization overview", Hugging Face Transformers](https://huggingface.co/docs/transformers/main/en/quantization/overview)
  Les backends de quantification que Transformers intègre et comment choisir entre eux. À utiliser pour : une carte de l'outillage.
- [Dépôt : llm-compressor, projet vLLM](https://github.com/vllm-project/llm-compressor)
  Une bibliothèque qui applique des recettes GPTQ, AWQ, SmoothQuant et FP8 et écrit des checkpoints que vLLM charge. À utiliser pour : exécuter un PTQ de bout en bout sur un vrai modèle.
- [Dépôt : compressed-tensors, Neural Magic](https://github.com/neuralmagic/compressed-tensors)
  L'extension de safetensors qui enregistre dans sa config le schéma de quantification d'un checkpoint. À utiliser pour : ce que stocke un checkpoint safetensors quantifié.
- [Doc : exemple "int8 W8A8", llm-compressor](https://github.com/vllm-project/llm-compressor/blob/main/examples/quantization_w8a8_int8/README.md)
  Une recette W8A8 int8 détaillée : SmoothQuant, puis GPTQ avec des scales de poids par canal, puis des scales d'activation dynamiques par token. À utiliser pour : exécuter SmoothQuant sur un vrai modèle.
- [Doc : "Choosing a dataset", LLM Compressor](https://docs.vllm.ai/projects/llm-compressor/en/latest/steps/choosing-dataset/)
  Quels algorithmes ont besoin d'un calibration set, comment faire correspondre son domaine à l'usage visé, et les tailles typiques. À utiliser pour : des conseils pratiques sur un calibration set.
- [Doc : "GPTQ", Hugging Face Transformers](https://huggingface.co/docs/transformers/main/en/quantization/gptq)
  Exécuter GPTQ avec `GPTQConfig` sur un jeu de données intégré ou votre propre texte. À utiliser pour : quantifier avec GPTQ depuis Transformers.
- [Doc : "AWQ", Hugging Face Transformers](https://huggingface.co/docs/transformers/main/en/quantization/awq)
  Charger des checkpoints AWQ et les clés `quantization_config` qu'un checkpoint AWQ enregistre. À utiliser pour : lire la config d'un checkpoint AWQ.
- [Doc : "bitsandbytes", Hugging Face Transformers](https://huggingface.co/docs/transformers/main/en/quantization/bitsandbytes)
  Comment Transformers charge les modèles bitsandbytes en 8 et 4 bits, y compris le type de données de calcul. À utiliser pour : voir que des poids stockés en 4 bits sont calculés dans une précision plus haute.
- [Doc : fiche technique "NVIDIA A100 Tensor Core GPU", NVIDIA](https://www.nvidia.com/content/dam/en-zz/Solutions/Data-Center/a100/pdf/nvidia-a100-datasheet-nvidia-us-2188504-web.pdf)
  Le débit des tensor cores de l'A100 par format et sa bande passante mémoire. À utiliser pour : les chiffres d'Ampere dans un roofline, à lire comme de la documentation de fournisseur.
- [Doc : livre blanc "NVIDIA Ada GPU Architecture", NVIDIA](https://images.nvidia.com/aem-dam/Solutions/Data-Center/l4/nvidia-ada-gpu-architecture-whitepaper-v2.1.pdf)
  Les tensor cores d'Ada et leur prise en charge du FP8. À utiliser pour : quels GPU d'inférence ont des tensor cores FP8, à lire comme de la documentation de fournisseur.
- [Doc : "NVIDIA H100 Tensor Core GPU", NVIDIA](https://www.nvidia.com/en-us/data-center/h100/)
  Le tableau de spécifications du H100 avec les lignes de tensor cores FP8 et INT8 et la bande passante mémoire. À utiliser pour : les chiffres de Hopper, à lire comme de la documentation de fournisseur.
- [Billet : "NVIDIA Hopper Architecture In-Depth", NVIDIA Technical Blog](https://developer.nvidia.com/blog/nvidia-hopper-architecture-in-depth/)
  Les tensor cores FP8 et le Transformer Engine introduits avec Hopper. À utiliser pour : le moment où le calcul FP8 est arrivé dans les GPU de centre de données NVIDIA, à lire comme de la documentation de fournisseur.

### Formats de fichier

- [Doc : "Safetensors", Hugging Face](https://huggingface.co/docs/safetensors/index)
  Le format de fichier de tenseurs dans lequel la plupart des checkpoints sont distribués, et ce qu'il stocke ou non. À utiliser pour : le conteneur à côté duquel se trouve une config de quantification.
- [Doc : "GGUF", Hugging Face Hub](https://huggingface.co/docs/hub/gguf)
  Une vue d'ensemble du format GGUF et un tableau de ses types de quantification avec leur agencement de bits. À utiliser pour : décoder le nom d'un type GGUF.
- [Doc : README de l'outil quantize de llama.cpp, ggml-org](https://github.com/ggml-org/llama.cpp/blob/master/tools/quantize/README.md)
  Comment llama.cpp convertit un modèle vers ses types de quantification, la liste des types, et comment la matrice d'importance est fournie. À utiliser pour : produire vous-même une quantification GGUF.
- [Dépôt : safetensors, Hugging Face](https://github.com/huggingface/safetensors)
  Le format au niveau de l'octet : une longueur d'en-tête sur 8 octets en little-endian, un en-tête JSON de noms, de dtypes, de formes et de décalages, puis les données. À utiliser pour : lire l'en-tête d'un checkpoint sans charger ses tenseurs.
- [Doc : "compressed-tensors", Hugging Face Transformers](https://huggingface.co/docs/transformers/main/en/quantization/compressed_tensors)
  Charger des checkpoints compressed-tensors, avec un exemple `config_groups` en FP8 et sa liste de tenseurs. À utiliser pour : lire une config compressed-tensors et ses tenseurs de scales.
- [Carte de modèle : "TinyLlama-1.1B-Chat-v1.0-GPTQ", TheBloke](https://huggingface.co/TheBloke/TinyLlama-1.1B-Chat-v1.0-GPTQ)
  Un petit checkpoint public GPTQ en 4 bits dont la carte explique les bits, la taille de groupe, l'act order et le damping. À utiliser pour : un vrai checkpoint à inspecter.
- [Code : ggml-common.h, ggml-org](https://github.com/ggml-org/llama.cpp/blob/master/ggml/src/ggml-common.h)
  La struct C de chaque type de bloc GGUF. À utiliser pour : déduire les bits par poids d'un type à partir de son agencement plutôt que de les citer.
- [Pull request : "k-quants", ikawrakow, llama.cpp, 2023](https://github.com/ggml-org/llama.cpp/pull/1684)
  Introduit les k-quants, la nomenclature type-0 et type-1 et les mélanges S, M et L d'origine. À utiliser pour : ce que signifiaient les suffixes à leur introduction.
- [Pull request : "Importance Matrix calculation", ikawrakow, llama.cpp, 2024](https://github.com/ggml-org/llama.cpp/pull/4861)
  Dérive la matrice d'importance à partir des activations sur un texte de calibration et s'en sert pour pondérer l'erreur d'arrondi. À utiliser pour : pourquoi une matrice d'importance est un calibration set.
- [Doc : README de l'outil imatrix de llama.cpp, ggml-org](https://github.com/ggml-org/llama.cpp/blob/master/tools/imatrix/README.md)
  Comment calculer une matrice d'importance et la passer à l'outil quantize. À utiliser pour : en produire une vous-même.

### Mesurer la perte de qualité

- [Article : "Accuracy is Not All You Need", Dutta et al., 2024](https://arxiv.org/abs/2407.09141)
  Montre qu'un modèle quantifié peut égaler l'accuracy de sa référence tout en changeant beaucoup de réponses individuelles, et propose les flips et la divergence KL comme métriques de distance. À utiliser pour : pourquoi une moyenne inchangée peut cacher un modèle changé.
- [Article : "Give Me BF16 or Give Me Death? Accuracy-Performance Trade-Offs in LLM Quantization", Kurtic et al., 2024](https://arxiv.org/abs/2411.02355)
  Plus d'un demi-million d'évaluations de schémas FP8, INT8 et INT4 sur les tailles de Llama 3.1 et sur plusieurs tâches, avec des recommandations de déploiement par schéma. À utiliser pour : ce que coûte chaque schéma, mesuré avec soin.
- [Article : "Scaling Laws for Precision", Kumar et al., 2024](https://arxiv.org/abs/2411.04330)
  Constate que la quantification post-entraînement dégrade d'autant plus un modèle qu'il a été entraîné sur plus de données. À utiliser pour : pourquoi la réponse habituelle du 4 bits peut échouer sur un modèle très entraîné.
- [Dépôt : lm-evaluation-harness, EleutherAI](https://github.com/EleutherAI/lm-evaluation-harness)
  Le harness avec lequel la plupart des articles sur la quantification rapportent l'accuracy sur des tâches. À utiliser pour : exécuter les mêmes tâches sur une référence et sur un modèle quantifié.
- [Doc : "Perplexity of fixed-length models", Hugging Face Transformers](https://huggingface.co/docs/transformers/main/en/perplexity)
  Comment la perplexity se calcule avec une fenêtre glissante, et pourquoi la fenêtre change le chiffre. À utiliser pour : calculer la perplexity de sorte que deux exécutions soient comparables.
- [Article : "Quantization Hurts Reasoning? An Empirical Study on Quantized Reasoning Models", Liu et al., 2025](https://arxiv.org/abs/2504.04823)
  Des modèles de raisonnement quantifiés, en quantification des poids, du KV cache et des activations, sur des benchmarks de maths, de sciences et de code, qui constatent que W8A8 et W4A16 peuvent être sans perte et que des largeurs en bits plus basses sont risquées. À utiliser pour : savoir si la réponse habituelle du 4 bits tient pour un modèle de raisonnement.
- [Doc : README de l'outil perplexity de llama.cpp, ggml-org](https://github.com/ggml-org/llama.cpp/blob/master/tools/perplexity/README.md)
  Statistiques de perplexity, de divergence KL et d'accord sur le token de tête par rapport aux logits en 16 bits, avec un tableau de types GGUF. À utiliser pour : mesurer un GGUF quantifié face à sa référence au-delà de la perplexity.

## Lacunes

- Il n'existe pas de tableau unique, neutre vis-à-vis des fournisseurs et à jour, des générations de GPU qui calculent nativement dans tel ou tel format. La leçon 20 s'appuie sur des pages de fournisseurs et sur les matrices de prise en charge des moteurs de serving, qui changent à chaque version.
