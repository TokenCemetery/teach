---
title: "Ressources"
description: "Sources fiables pour les evals"
type: resources
---

# Ressources sur les evals

## Connaissances

- [Doc : "Define success criteria and build evaluations", Claude Platform Docs](https://platform.claude.com/docs/en/test-and-evaluate/develop-tests)
  Démarche de praticien pour transformer une question vague du type « est-ce que ça s'est amélioré » en critères de réussite mesurables et en jeu d'eval held-out. À utiliser pour : concevoir l'eval elle-même avant de se tourner vers un framework.
- [Dépôt : openai/evals, OpenAI](https://github.com/openai/evals)
  Framework officiel pour définir et exécuter une eval sous forme de code : prompts, logique de notation et registre d'evals existantes à lire comme exemples travaillés. À utiliser pour : structurer et exécuter une eval sur mesure.
- [Dépôt : lm-evaluation-harness, EleutherAI](https://github.com/EleutherAI/lm-evaluation-harness)
  Le harness de référence de fait pour exécuter un modèle sur des benchmarks standardisés, dont les configurations de tâches montrent comment les jeux held-out sont structurés et notés en pratique. À utiliser pour : exécuter ou adapter un benchmark existant plutôt que de construire une eval de zéro.
- [Article : "Judging LLM-as-a-Judge with MT-Bench and Chatbot Arena", Zheng et al., 2023](https://arxiv.org/abs/2306.05685)
  Introduit le LLM-as-judge pour les tâches ouvertes et mesure ses biais par rapport à la préférence humaine : biais de position, biais de verbosité, biais d'auto-valorisation. À utiliser pour : décider si un juge LLM est digne de confiance pour un cas donné, et ce qu'il faut corriger si c'est le cas.
- [Doc : Evaluate, Hugging Face](https://huggingface.co/docs/evaluate/index)
  Bibliothèque de métriques standard propres aux tâches (BLEU, ROUGE, exact match, F1, et d'autres) avec la définition et les modes de défaillance de chacune. À utiliser pour : le côté métrique propre à la tâche de la comparaison entre métrique et juge LLM.
- [Article : "Time Travel in LLMs: Tracing Data Contamination in Large Language Models", Golchin and Surdeanu, 2023](https://arxiv.org/abs/2308.08493)
  Méthode concrète pour tester si les données d'un benchmark ont fui dans le jeu d'entraînement d'un modèle, avec la technique de devinette de la suite de l'instance qui la détecte. À utiliser pour : défendre l'honnêteté d'un jeu held-out face à l'affirmation précise « le modèle l'a simplement mémorisé ».
- [Article : "Beyond the Imitation Game: Quantifying and Extrapolating the Capabilities of Language Models" (BIG-bench), Srivastava et al., 2022](https://arxiv.org/abs/2206.04615)
  Introduit la convention de la chaîne canari (une phrase-marqueur unique intégrée aux données d'un benchmark, qui demande aux crawlers de l'exclure des corpus d'entraînement) comme technique préventive de résistance à la contamination lors de la publication d'un benchmark. À utiliser pour : concevoir un jeu d'eval sur mesure qui résiste à la contamination dès le départ, plutôt que de la détecter après coup.
- [Article : "Evaluating Large Language Models Trained on Code" (Codex), Chen et al., 2021](https://arxiv.org/abs/2107.03374)
  Introduit la correction fonctionnelle (exécuter le code généré sur des cas de test plutôt que comparer du texte) et l'estimateur non biaisé de pass@k, avec la formule combinatoire qui évite la forte variance d'un rééchantillonnage direct de k complétions. À utiliser pour : évaluer la génération de code, et pour le principe général de vérifier le comportement plutôt que la ressemblance textuelle partout où une tâche est exécutable.

- [Article : "Cohen's kappa", Wikipedia](https://en.wikipedia.org/wiki/Cohen%27s_kappa)
  La statistique d'accord inter-annotateurs corrigée du hasard : sa formule, pourquoi un kappa de 0 signifie pas mieux que le hasard, et sa tendance connue à sous-estimer l'accord sur une catégorie rare. À utiliser pour : mesurer précisément l'accord entre annotateurs humains au lieu d'estimer à l'œil un pourcentage d'accord brut.
- [Article : "Inter-rater reliability", Wikipedia](https://en.wikipedia.org/wiki/Inter-rater_reliability)
  Explique pourquoi l'accord brut en probabilité conjointe est trompeur (gonflé par le hasard, davantage encore avec peu de catégories) et présente l'alpha de Krippendorff comme généralisation de l'accord corrigé du hasard à un nombre quelconque d'annotateurs et à tout niveau de mesure. À utiliser pour : choisir la bonne statistique d'accord pour plus de deux annotateurs ou pour des notations non catégorielles.
- [Article : "HarmBench: A Standardized Evaluation Framework for Automated Red Teaming and Robust Refusal", Mazeika et al., 2024](https://arxiv.org/abs/2402.04249)
  Introduit un framework standardisé pour évaluer des méthodes de red-teaming automatisé contre des modèles et des défenses, à grande échelle et de façon comparable, là où le domaine n'en avait pas auparavant. À utiliser pour : le taux de réussite des attaques comme métrique, et la distinction entre une méthode de génération d'attaques et une manière rigoureuse de l'évaluer.
- [Article : "XSTest: A Test Suite for Identifying Exaggerated Safety Behaviours in Large Language Models", Röttger et al., 2023](https://arxiv.org/abs/2308.01263)
  Suite de test de prompts sûrs rédigés pour ressembler à des prompts dangereux, précisément pour faire apparaître le sur-refus. À utiliser pour : la tension exacte entre innocuité (refuser les prompts dangereux) et utilité (ne pas refuser les prompts sûrs), et une manière concrète de mesurer qu'un modèle se place mal sur ce compromis.
- [Article : "τ-bench: A Benchmark for Tool-Agent-User Interaction in Real-World Domains", Yao et al., 2024](https://arxiv.org/abs/2406.12045)
  Évalue des agents en comparant l'état de la base de données en fin de conversation à un état cible annoté, et introduit `pass^k` pour mesurer la fiabilité d'un agent sur des essais répétés de la même tâche. À utiliser pour : pourquoi la réussite de la tâche l'emporte sur la correspondance étape par étape de la trajectoire, et la distinction précise, facile à confondre, entre `pass^k` et le `pass@k` de la leçon 4.
- [Article : "AgentBench: Evaluating LLMs as Agents", Liu et al., 2023](https://arxiv.org/abs/2308.03688)
  Benchmark multidimensionnel sur 8 environnements interactifs distincts qui teste le raisonnement et la prise de décision d'un LLM en tant qu'agent, et constate un écart important entre les meilleurs modèles et les plus petits, précisément en contexte agentique. À utiliser pour : une preuve que la capacité agentique est une chose distincte à mesurer, que la performance à un benchmark à un seul tour n'implique pas.
- [Article : "Ragas: Automated Evaluation of Retrieval Augmented Generation", Es et al., 2023](https://arxiv.org/abs/2309.15217)
  Framework sans référence qui sépare en métriques indépendantes les dimensions qualité de la récupération, fidélité et qualité de la génération d'un système RAG. À utiliser pour : calculer un score de fidélité sans réponse de référence rédigée par un humain, et garder l'échec de récupération et l'échec de génération diagnostiquables comme deux questions séparées.
- [Article : "Enabling Large Language Models to Generate Text with Citations" (ALCE), Gao et al., 2023](https://arxiv.org/abs/2305.14627)
  Introduit des métriques automatiques de qualité des citations corrélées au jugement humain, et le constat que même les meilleurs systèmes n'apportent pas un soutien complet par les citations pour environ la moitié de leurs affirmations sur un jeu de test. À utiliser pour : l'exactitude des citations comme contrôle plus strict et distinct de la fidélité.
- [Article : "Seven Rules of Thumb for Web Site Experimenters", Kohavi et al., 2014](https://exp-platform.com/Documents/2014%20experimentersRulesOfThumb.pdf)
  Conseils de praticiens de Kohavi et de ses coauteurs sur la conduite d'expériences contrôlées en ligne, dont le concept d'OEC (mobile et lié causalement au vrai résultat) et les métriques garde-fous. À utiliser pour : choisir un OEC défendable plutôt qu'une métrique facile à faire bouger mais sans lien causal, et pourquoi une métrique garde-fou doit être suivie à ses côtés.
- [Guide : "Rules of Machine Learning", Zinkevich, Google](https://developers.google.com/machine-learning/guides/rules-of-ml)
  Recommandations internes de Google en ingénierie du ML, dont la règle n° 37 (mesurer le décalage entraînement-service comme plusieurs comparaisons distinctes, pas une seule) et la règle n° 8 (exigences de fraîcheur). À utiliser pour : savoir précisément laquelle des causes possibles d'un écart hors ligne/en ligne, variance ordinaire, dérive ou erreur d'ingénierie, s'applique réellement, et pourquoi chacune demande un correctif différent.
- [Article : "The Tail at Scale", Dean and Barroso, 2013](https://www.barroso.org/publications/TheTailAtScale.pdf)
  L'explication canonique de la raison pour laquelle la latence de queue, et non la latence moyenne, détermine la réactivité réelle à grande échelle, surtout quand une requête se répartit sur de nombreux appels backend. À utiliser pour : pourquoi un go/no-go demande un percentile (p95/p99), et pas seulement une moyenne, avant d'écarter une régression de latence.
- [Article : "The Leaderboard Illusion", Singh et al., 2025](https://arxiv.org/abs/2504.20879)
  Documente la divulgation sélective sur Chatbot Arena : tests privés avant publication de nombreuses variantes de modèle (27 pour Llama 4 seul) et accès aux données vaste et asymétrique, au profit d'une poignée de fournisseurs de modèles fermés. À utiliser pour : un exemple concret, récent et bien documenté de la raison pour laquelle un rang de classement n'est pas, à lui seul, une mesure neutre et digne de confiance.
- [Article : "Does Style Matter?", LMArena](https://lmarena.ai/blog/style-control)
  L'analyse de l'arène elle-même montrant que les classements changent sensiblement une fois la longueur des réponses et la mise en forme markdown contrôlées. À utiliser pour : confirmer que le mécanisme du biais de verbosité de la leçon 6 opère de façon identique à l'échelle complète d'un classement, avec des annotateurs humains au lieu d'un seul juge LLM.

## Lacunes

- Aucune source dédiée encore sur les tests de significativité statistique des écarts de score d'eval (erreur standard d'une proportion, tests de significativité appariés comme celui de McNemar). La mission en a besoin pour la question de l'étape 5, « cet écart est-il réel ou du bruit » ; la leçon 9 l'enseigne à partir d'une méthode statistique stable et standard plutôt que d'une seule source citée, et cette lacune devrait se refermer quand une bonne source de niveau praticien sera trouvée.
