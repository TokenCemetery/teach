---
title: "Ressources"
description: "Sources fiables pour l'inférence"
type: resources
---

# Ressources sur l'inférence

## Connaissances

- [Doc : vLLM Documentation, vLLM Project](https://docs.vllm.ai/en/latest/)
  La documentation officielle de la pile de serving GPU que cet espace de travail met en place en premier : installation, lancement du serveur, et réglages de batching et de mémoire du moteur. À utiliser pour : savoir comment exécuter et configurer vLLM lui-même.
- [Article : "Efficient Memory Management for Large Language Model Serving with PagedAttention", Kwon et al., SOSP 2023](https://arxiv.org/abs/2309.06180)
  L'article de PagedAttention : pourquoi le KV cache fragmente les allocateurs de mémoire ordinaires et comment la pagination règle ce problème, avec les chiffres de débit qui motivent la conception de vLLM. À utiliser pour : comprendre ce que coûte le KV cache et pourquoi le gestionnaire de mémoire de vLLM existe.
- [Dépôt : llama.cpp, ggml-org](https://github.com/ggml-org/llama.cpp)
  Le dépôt officiel de la pile de serving CPU/edge que cet espace de travail met en place en second : instructions de compilation, formats de quantification pris en charge (GGUF), et options du binaire serveur. À utiliser pour : savoir comment exécuter et configurer llama.cpp lui-même.
- [Pull request : "k-quants", ikawrakow, llama.cpp, 2023](https://github.com/ggml-org/llama.cpp/pull/1684)
  Introduit les types k-quant, leur disposition en super-blocs, et les recettes `S`, `M` et `L` qui mélangent les types selon les tenseurs. À utiliser pour : savoir ce que stocke réellement un nom GGUF comme `Q4_K_M`.
- [Article : "GPTQ: Accurate Post-Training Quantization for Generative Pre-trained Transformers", Frantar et al., 2023](https://arxiv.org/abs/2210.17323)
  Quantification des poids après entraînement en une seule passe jusqu'à 3-4 bits, avec un coût de précision mesuré. À utiliser pour : savoir ce que la quantification d'un modèle pour le serving sacrifie réellement, et comment ce compromis se mesure.
  Lisez d'abord le [guide transformers](https://huggingface.co/docs/transformers/main/en/llm_optims) ci-dessous si l'algèbre linéaire est ce qui vous bloque ici.
- [Doc : "Optimizing inference", Hugging Face Transformers](https://huggingface.co/docs/transformers/main/en/llm_optims)
  Un parcours au niveau praticien du KV cache, du batching statique contre dynamique et des backends de quantification, sans exiger d'abord les mathématiques des articles. À utiliser pour : se faire un modèle mental opérationnel avant les sources primaires ci-dessus.
- [Billet : "Transformer Inference Arithmetic", Kipply](https://kipp.ly/transformer-inference-arithmetic/)
  Dérive l'arithmétique réelle de FLOP et de bande passante mémoire derrière une passe avant, y compris l'origine du coût mémoire du KV cache. À utiliser pour : calculer un budget de latence ou de mémoire à partir des premiers principes plutôt que de citer un benchmark.
- [Billet : "How continuous batching enables 23x throughput in LLM inference while reducing p50 latency", Anyscale](https://www.anyscale.com/blog/continuous-batching-llm-inference)
  Écrit par des ingénieurs qui ont intégré le continuous batching dans un des premiers moteurs de serving ; explique pourquoi le batching statique gaspille du temps GPU sur un flux de requêtes de longueurs variées et comment le continuous batching y remédie. À utiliser pour : la moitié batching du compromis latence/débit que cet espace de travail défend.

- [Article : "Fast Inference from Transformers via Speculative Decoding", Leviathan et al., 2022](https://arxiv.org/abs/2211.17192)
  Introduit le décodage spéculatif : un petit modèle rédige plusieurs tokens, le grand modèle les vérifie tous en une seule passe parallèle, avec une méthode d'échantillonnage qui garantit exactement la même distribution de sortie que l'exécution du grand modèle seul. À utiliser pour : comprendre pourquoi c'est un pur levier de latence et non un compromis sur la qualité, et l'argument de bande passante mémoire qui explique pourquoi la vérification parallèle est presque gratuite.
- [Article : "Medusa: Simple LLM Inference Acceleration Framework with Multiple Decoding Heads", Cai et al., 2024](https://arxiv.org/abs/2401.10774)
  Remplace le draft model séparé du décodage spéculatif par des têtes de décodage supplémentaires ajoutées directement au modèle cible. À utiliser pour : lever la charge opérationnelle de maintenir un second modèle, tout en gardant la même garantie de vérification et de correction.
- [Article : "EAGLE: Speculative Sampling Requires Rethinking Feature Uncertainty", Li et al., 2024](https://arxiv.org/abs/2401.15077)
  Rédige au niveau des features internes du modèle plutôt que des tokens bruts, en résolvant l'incertitude de prédiction au niveau des features grâce à une séquence de tokens avancée d'un pas. À utiliser pour : un raffinement supplémentaire par rapport à Medusa, avec une accélération rapportée plus grande tout en préservant la distribution de sortie du modèle cible.
- [Article : "Efficient Guided Generation for Large Language Models" (Outlines), Willard et Louf, 2023](https://arxiv.org/abs/2307.09702)
  Reformule la génération contrainte comme des transitions entre états d'un automate à états finis, ce qui permet de précalculer un index du vocabulaire une seule fois par grammaire et de le réutiliser comme une recherche rapide par token. À utiliser pour : comprendre pourquoi le décodage contraint par une grammaire ou un schéma ajoute peu de surcoût par token et garantit la structure de la sortie par construction plutôt que par espoir.
- [Doc : "Automatic Prefix Caching", vLLM Project](https://docs.vllm.ai/en/latest/features/automatic_prefix_caching.html)
  La documentation propre de vLLM sur la réutilisation du KV cache d'un préfixe partagé entre des requêtes par ailleurs sans lien, ses deux charges de travail d'exemple nommées (questions-réponses sur de longs documents, conversation multi-tours), et sa limite annoncée (accélère le prefill uniquement, jamais le decode). À utiliser pour : le prefix caching vu comme le mécanisme de partage de blocs de PagedAttention étendu à plusieurs requêtes.
- [Article : "Megatron-LM: Training Multi-Billion Parameter Language Models Using Model Parallelism", Shoeybi et al., 2019](https://arxiv.org/abs/1909.08053)
  L'article de référence sur le parallélisme tensoriel : un schéma de parallélisme de modèle intra-couche qui répartit les multiplications matricielles d'une couche de transformer entre des GPU, ne nécessitant que quelques opérations de communication, explicitement orthogonal et complémentaire au parallélisme de pipeline. À utiliser pour : ce que fait réellement `--tensor-parallel-size` (leçon 12) à l'intérieur d'une couche.
- [Article : "GPipe: Efficient Training of Giant Neural Networks using Pipeline Parallelism", Huang et al., 2018](https://arxiv.org/abs/1811.06965)
  L'article de référence sur le parallélisme de pipeline : partitionne tout réseau exprimable comme une suite de couches en groupes consécutifs placés sur des accélérateurs distincts, et introduit le micro-batching pour réduire (sans l'éliminer) la bulle de pipeline qui en résulte. À utiliser pour : l'autre façon de découper par rapport au parallélisme tensoriel, et pourquoi elle tolère une liaison entre appareils plus lente.
- [Doc : "Welcome to production-stack" and use-case guides, vLLM Production Stack](https://docs.vllm.ai/projects/production-stack)
  La documentation officielle du déploiement de flotte de référence de vLLM, natif Kubernetes : routage des requêtes sensible au KV cache et autoscaling basé sur KEDA à partir de métriques de profondeur de file comme `vllm:num_requests_waiting`. À utiliser pour : comprendre comment le routage et l'autoscaling fonctionnent réellement à l'échelle d'une flotte, au-delà d'un seul serveur.
- [Article : "ServerlessLLM: Low-Latency Serverless Inference for Large Language Models", Fu et al., OSDI 2024](https://arxiv.org/abs/2401.14351)
  Mesure pourquoi les cold starts des LLM sont sévères (le temps de chargement du checkpoint dépasse de très loin le temps de génération par token, des dizaines de secondes dans les traces de production) et y remédie par un chargement de checkpoint multi-niveaux, proche du GPU. À utiliser pour : comprendre pourquoi ajouter une réplique à une flotte n'est pas instantané, et ce qui borne réellement la vitesse à laquelle elle devient utile.
- [Doc : "Metrics", vLLM Project](https://docs.vllm.ai/en/stable/design/metrics/)
  La liste propre de vLLM des métriques Prometheus exportées : TTFT, latence inter-token, latence de bout en bout, et histogrammes séparés des temps de prefill et de decode. À utiliser pour : ce qu'un serveur de production exporte réellement en continu, par opposition à un benchmark ponctuel.
- [Google SRE Workbook : "Implementing SLOs"](https://sre.google/workbook/implementing-slos/)
  La présentation de référence du SRE sur les SLI, les SLO et les budgets d'erreur : un ratio pertinent pour l'utilisateur, une cible énoncée pour lui, et la tolérance à manquer cette cible dérivée directement du SLO. À utiliser pour : transformer une métrique brute exportée en une cible de production exploitable.
- [Article : "YaRN: Efficient Context Window Extension of Large Language Models", Peng et al., ICLR 2024](https://arxiv.org/abs/2309.00071)
  Étend la longueur de contexte utilisable d'un modèle au-delà de sa longueur d'entraînement en redimensionnant de façon non uniforme les dimensions de fréquence de RoPE, pour une fraction du coût de fine-tuning des méthodes précédentes. À utiliser pour : comprendre pourquoi le RoPE scaling change la longueur de contexte maximale sans toucher à la croissance propre du KV cache.
- [Article : "Mistral 7B", Jiang et al., 2023](https://arxiv.org/abs/2310.06825)
  Introduit l'attention à fenêtre glissante et son cache à tampon circulaire associé : chaque token porte son attention sur une fenêtre fixe de tokens précédents au plus, ce qui plafonne la taille du cache quelle que soit la longueur de la séquence. À utiliser pour : le mécanisme qui transforme en constante la croissance linéaire du cache de la leçon 2.
- [Article : "Efficient Streaming Language Models with Attention Sinks", Xiao et al., ICLR 2024](https://arxiv.org/abs/2309.17453)
  Identifie le phénomène d'attention sink derrière l'effondrement de l'attention à fenêtre glissante simple dès que les anciens tokens sont retirés, et y remédie en conservant en permanence les entrées KV d'une poignée de tokens initiaux. À utiliser pour : comprendre pourquoi un cache borné peut quand même servir un flux effectivement illimité.

## Lacunes

- Pas encore de source sur la quantification adaptée au serving spécifiquement pour les formats GGUF de llama.cpp (par opposition à GPTQ/AWQ, qui visent les piles GPU) ; la mission a besoin d'une comparaison de quantification propre au CPU/edge une fois que la conception des leçons atteindra cette étape.
