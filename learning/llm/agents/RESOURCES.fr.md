---
title: "Ressources"
description: "Sources fiables sur les agents LLM"
type: resources
---

# Ressources sur les agents LLM

## Connaissances

- [Billet : "Building Effective Agents", Anthropic Engineering](https://www.anthropic.com/engineering/building-effective-agents)
  Établit la distinction entre workflow et agent sur laquelle ce parcours est construit, puis nomme les schémas composables courants (prompt chaining, routage, parallélisation, orchestrateur et workers, évaluateur et optimiseur) et plaide pour le plus simple qui fonctionne. À utiliser pour : le vocabulaire de l'étape 1, et l'argument de l'étape 16 pour ne pas construire d'agent.
- [Guide : "A Practical Guide to Building Agents", OpenAI](https://cdn.openai.com/business-guides-and-resources/a-practical-guide-to-building-agents.pdf)
  Le cadrage d'un second éditeur sur la même matière, qui couvre quand une tâche justifie un agent, les catégories d'outils, l'orchestration pour un agent ou plusieurs, et les garde-fous. À utiliser pour : vérifier qu'une affirmation de l'étape 1 ou de l'étape 8 porte sur les agents et non sur le produit d'un seul fournisseur.
- [Billet : "Writing Effective Tools for Agents", Anthropic Engineering](https://www.anthropic.com/engineering/writing-tools-for-agents)
  Traite le nom, la description, le schéma de paramètres et la forme de retour d'un outil comme une surface de prompt plutôt que comme un contrat d'API, y compris la façon dont la sortie d'un outil consomme le budget de contexte. À utiliser pour : l'étape 4, et pour comprendre pourquoi un outil conçu comme un endpoint REST est un moins bon outil.
- [Billet : "Effective Context Engineering for AI Agents", Anthropic Engineering](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents)
  Plaide pour traiter la fenêtre de contexte comme un budget fini à gérer, et couvre la compaction, la prise de notes dans une mémoire externe et les sous-agents comme isolation du contexte. À utiliser pour : les étapes 5 et 6.
- [Article : "ReAct: Synergizing Reasoning and Acting in Language Models", Yao et al., 2022](https://arxiv.org/abs/2210.03629)
  Introduit l'entrelacement de traces de raisonnement et d'actions d'outils dans une seule boucle, plutôt qu'une planification entièrement en amont ou une action sans raisonnement. À utiliser pour : l'étape 7, et le nom du schéma que la plupart des boucles d'agents implémentent encore.
- [Article : "Reflexion: Language Agents with Verbal Reinforcement Learning", Shinn et al., 2023](https://arxiv.org/abs/2303.11366)
  Introduit l'auto-critique comme étape explicite de la boucle : l'agent réfléchit en langage naturel à une tentative échouée et reporte cette réflexion dans le nouvel essai. À utiliser pour : la matière sur la réflexion de l'étape 7, et ce que l'auto-critique coûte en tokens.
- [Article : "Toolformer: Language Models Can Teach Themselves to Use Tools", Schick et al., 2023](https://arxiv.org/abs/2302.04761)
  Montre l'usage d'outils appris par le modèle plutôt que sollicité par le prompt, ce qui marque la frontière entre ce parcours et `llm/finetuning`. À utiliser pour : l'explication de l'étape 2 sur la raison pour laquelle un modèle émet un appel d'outil.
- [Doc : "Tool use with Claude", Claude Platform Docs](https://platform.claude.com/docs/en/agents-and-tools/tool-use/overview)
  Le récit d'un fournisseur sur son propre format de transmission d'appel d'outil : le schéma JSON que prend la définition d'un outil, comment une requête d'appel d'outil et son résultat sont représentés sous forme de messages, et les appels d'outils parallèles. À utiliser pour : la paire requête et réponse capturée de l'étape 2, lue avec le guide OpenAI ci-dessous comme différence.
- [Guide : "Function calling", OpenAI](https://developers.openai.com/api/docs/guides/function-calling)
  Le format de transmission d'un second fournisseur pour la même mécanique, y compris le passage d'un appel de fonction unique à une convention générale d'appel d'outils. À utiliser pour : l'étape 2, comme second fournisseur dont le format n'apparaît que sous forme de différence avec le premier.
- [Spécification : Model Context Protocol](https://modelcontextprotocol.io/specification)
  La spécification normative de MCP : outils, ressources, prompts, sampling, les transports et le cycle de vie du serveur. À utiliser pour : l'étape 9, et pour trancher toute affirmation sur MCP à partir de la source plutôt que de la documentation d'un client.
- [Billet : "Code Execution with MCP", Anthropic Engineering](https://www.anthropic.com/engineering/code-execution-with-mcp)
  Soutient que présenter les outils comme du code que l'agent écrit, plutôt que comme des définitions d'outils individuelles chargées en contexte, change ce que coûte un grand jeu d'outils. À utiliser pour : le problème de découverte d'outils à grande échelle de l'étape 9 et la matière sur l'exécution de code de l'étape 10.
- [Billet : "How We Built Our Multi-Agent Research System", Anthropic Engineering](https://www.anthropic.com/engineering/multi-agent-research-system)
  Un récit de production d'un système orchestrateur et workers, y compris le multiple de coût en tokens par rapport à un agent unique et l'endroit où la coordination a réellement cassé. À utiliser pour : l'argument de l'étape 8 selon lequel le multi-agent achète du parallélisme et de l'isolation du contexte, à un prix mesuré.
- [Billet : "Don't Build Multi-Agents", Cognition](https://cognition.ai/blog/dont-build-multi-agents)
  Le plaidoyer opposé, qui soutient que répartir le travail entre agents fragmente le contexte et produit des décisions qui entrent en conflit. À utiliser pour : l'étape 8, à lire en regard du récit d'Anthropic ci-dessus et non à sa place.
- [Billet : "The Lethal Trifecta for AI Agents", Simon Willison](https://simonwillison.net/2025/Jun/16/the-lethal-trifecta/)
  Nomme la combinaison qui rend un agent exploitable : l'accès à des données privées, l'exposition à du contenu non fiable et la capacité à communiquer vers l'extérieur. À utiliser pour : le cadrage central de l'étape 14, et pour comprendre pourquoi les instructions du prompt ne sont pas une défense.
- [Référence : "OWASP Top 10 for LLM Applications", OWASP GenAI Security Project](https://genai.owasp.org/llm-top-10/)
  Le catalogue consensuel des risques des applications LLM, y compris l'injection de prompt, l'agentivité excessive et l'exposition de la chaîne d'approvisionnement, chacun avec ses mesures d'atténuation. À utiliser pour : la liste de contrôle de l'étape 14, et le vocabulaire qu'un relecteur sécurité emploiera déjà.
- [Spécification : "Semantic Conventions for Generative AI", OpenTelemetry](https://opentelemetry.io/docs/specs/semconv/gen-ai/)
  Des conventions indépendantes des fournisseurs pour les spans et les attributs qu'émet une exécution d'agent, ce qui permet de lire dans un backend de traçage la vue de trajectoire d'un autre. À utiliser pour : l'étape 12, comme réponse neutre vis-à-vis des fournisseurs à la question de ce qu'une trace doit contenir.
- [Article : "tau-bench: A Benchmark for Tool-Agent-User Interaction in Real-World Domains", Yao et al., 2024](https://arxiv.org/abs/2406.12045)
  Évalue des agents sur de l'usage d'outils multi-tours face à un utilisateur simulé et à une politique de domaine, et introduit une mesure de fiabilité sur essais répétés plutôt que la réussite sur un seul essai. À utiliser pour : la distinction de l'étape 13 entre réussir une fois et réussir de façon fiable.
- [Article : "SWE-bench: Can Language Models Resolve Real-World GitHub Issues?", Jimenez et al., 2023](https://arxiv.org/abs/2310.06770)
  Évalue des agents sur de vraies issues de dépôts, avec les propres tests du projet comme vérification du résultat. À utiliser pour : l'exemple de l'étape 13 d'un benchmark noté sur le résultat où la trajectoire n'est pas contrainte.
- [Doc : "Computer use tool", Claude Platform Docs](https://platform.claude.com/docs/en/agents-and-tools/tool-use/computer-use-tool)
  Décrit la boucle capture d'écran et action qu'exécute un agent de computer use : une observation est une capture d'écran plutôt qu'un résultat d'outil, et une action est une coordonnée d'écran ou une touche pressée plutôt qu'un argument de fonction. À utiliser pour : la matière sur l'ancrage d'une action à une coordonnée de l'étape 11, et pour comprendre pourquoi cette boucle demande une autre histoire de fiabilité qu'une boucle d'appels d'outils.
- [Article : "WebArena: A Realistic Web Environment for Building Autonomous Agents", Zhou et al., 2023](https://arxiv.org/abs/2307.13854)
  Un environnement web auto-hébergé avec des vérifications de correction fonctionnelle, construit pour des agents qui agissent à travers un navigateur. À utiliser pour : l'étape 11, comme étalon à l'aune duquel se font les affirmations sur la fiabilité des agents de navigateur.
- [Article : "GAIA: A Benchmark for General AI Assistants", Mialon et al., 2023](https://arxiv.org/abs/2311.12983)
  Des questions faciles pour une personne et difficiles pour un agent, qui exigent de l'usage d'outils en plusieurs étapes avec une unique réponse non ambiguë. À utiliser pour : l'étape 13, en contrepoids aux benchmarks qu'un modèle peut réussir sans agir.
- [Doc : "Prompt caching", Claude Platform Docs](https://platform.claude.com/docs/en/build-with-claude/prompt-caching)
  La mise en cache d'un préfixe de prompt pour réduire le coût et la latence répétés, y compris pourquoi les définitions d'outils stables et le system prompt d'un agent sont exactement le préfixe qui vaut la peine d'être mis en cache et ce qui invalide silencieusement le cache. À utiliser pour : la matière sur l'amplification de tokens et le coût de l'étape 15.

## Lacunes

- Il n'existe aucune référence neutre vis-à-vis des fournisseurs pour les formats de transmission d'appels d'outils. Chaque fournisseur ne documente que le sien, donc les paires requête et réponse capturées que ce parcours montre doivent être tirées de la documentation des fournisseurs et réconciliées à la main.
- L'exécution durable et reprenable d'un agent est documentée surtout à l'intérieur de frameworks individuels, ce qui n'est ni neutre vis-à-vis des fournisseurs ni assez stable pour être listé pour l'instant. L'étape 15 a besoin d'une source qui ne soit ni l'un ni l'autre.
- Le computer use et les agents de navigateur évoluent plus vite que tout ce qui s'écrit à leur sujet. Les articles de benchmark listés couvrent la façon d'en évaluer un, pas la pratique actuelle pour en construire un, donc l'étape 11 est la partie de l'arc dont les sources sont les plus minces.
- Rien de ce qui est listé ne couvre encore la mémoire d'un agent entre exécutions comme système conçu plutôt que comme fonctionnalité de produit. L'étape 6 en a besoin d'une.
