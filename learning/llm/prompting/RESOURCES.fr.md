---
title: Ressources
description: "Sources fiables pour le prompting"
type: resources
---

# Ressources sur le prompting

## Connaissances

- [Doc : "Prompting best practices", Claude Platform Docs](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/claude-prompting-best-practices)
  Le guide consolidé d'un éditeur : instructions claires, exemples, balises XML, rôles, thinking, long contexte et format de sortie, avec des prompts avant et après. À utiliser pour : la base de référence des praticiens pour les étapes 2 à 6, à lire comme le comportement documenté d'un seul éditeur.
- [Doc : "Prompt engineering overview", Claude Platform Docs](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/overview)
  Le conseil de définir des critères de succès et des tests avant d'itérer, et une courte remarque : tout échec d'évaluation ne se corrige pas au mieux par le prompting. À utiliser pour : l'habitude de mesurer d'abord.
- [Doc : "Long context prompting", section de Prompting best practices, Claude Platform Docs](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/claude-prompting-best-practices#long-context-prompting)
  Placer les longs documents avant la requête, envelopper chacun dans des balises avec ses métadonnées et demander d'abord les citations pertinentes. À utiliser pour : organiser une longue entrée.
- [Doc : "Structured outputs", Claude Platform Docs](https://platform.claude.com/docs/en/build-with-claude/structured-outputs)
  Une fonctionnalité de fournisseur qui impose un schéma JSON à la réponse, documentée avec ce que le prompt seul ne garantit pas. À utiliser pour : la frontière entre demander de la structure et l'imposer.
- [Doc : "Prompt caching", Claude Platform Docs](https://platform.claude.com/docs/en/build-with-claude/prompt-caching)
  Comment un préfixe en cache est reconnu, ce qui l'invalide et l'ordre que le prompt doit respecter pour obtenir un hit. À utiliser pour : organiser un prompt de façon à ce que ses parties stables soient mises en cache.
- [Doc : "Model IDs and versioning", Claude Platform Docs](https://platform.claude.com/docs/en/about-claude/models/model-ids-and-versions)
  Comment un éditeur nomme des snapshots figés et des alias mobiles, et le fait que chaque identifiant a son propre calendrier de retrait. À utiliser pour : épingler un prompt au modèle contre lequel il a été testé.
- [Doc : "Extended thinking", Claude Platform Docs](https://platform.claude.com/docs/en/build-with-claude/extended-thinking)
  La mécanique d'API d'une phase de thinking : le budget de tokens, son minimum, et la façon dont le thinking compte dans la limite de sortie. À utiliser pour : les faits de budget derrière le prompting d'un modèle de raisonnement ; les conseils de formulation se trouvent dans le guide des bonnes pratiques.
- [Doc : "Define success criteria and build evaluations", Claude Platform Docs](https://platform.claude.com/docs/en/test-and-evaluate/develop-tests)
  Transformer « ce prompt est-il meilleur » en critères de succès et en conception d'évaluation, avec cas limites et comparaison à une référence. À utiliser pour : décider à quoi une modification de prompt doit être jugée avant de changer quoi que ce soit.
- [Doc : "Mitigate jailbreaks and prompt injections", Claude Platform Docs](https://platform.claude.com/docs/en/test-and-evaluate/strengthen-guardrails/mitigate-jailbreaks)
  Des mesures d'atténuation au niveau du prompt et du système, dont le filtrage des entrées et la limitation de ce que le modèle peut faire. À utiliser pour : savoir quelles défenses relèvent de l'auteur du prompt.
- [Doc : "Prompt design strategies", Gemini API, Google](https://ai.google.dev/gemini-api/docs/prompting-strategies)
  Le guide d'un second éditeur sur les instructions, les exemples few-shot, les préfixes et la décomposition d'une tâche. À utiliser pour : vérifier si une technique est générale ou propre au comportement d'un éditeur.
- [Doc : "Chat templates", Hugging Face Transformers](https://huggingface.co/docs/transformers/main/en/chat_templating)
  Comment une liste de messages étiquetés par rôle est transformée en la séquence unique de tokens sur laquelle un modèle a été entraîné, avec de vraies sorties de gabarit. À utiliser pour : ce que le modèle voit réellement.
- [Dépôt : "Prompt engineering interactive tutorial", Anthropic](https://github.com/anthropics/prompt-eng-interactive-tutorial)
  Des exercices en notebook couvrant les rôles, la séparation des données et des instructions, les exemples, le raisonnement pas à pas et l'évitement des hallucinations. À utiliser pour : s'entraîner sur les étapes 1 à 4.
- [Article : "The Prompt Report: A Systematic Survey of Prompting Techniques", Schulhoff et al., 2024](https://arxiv.org/abs/2406.06608)
  Une revue et une taxonomie des techniques de prompting avec un vocabulaire cohérent. À utiliser pour : situer une technique rencontrée dans la nature et trancher le sens d'un terme.
- [Article : "Quantifying Language Models' Sensitivity to Spurious Features in Prompt Design", Sclar et al., 2023](https://arxiv.org/abs/2310.11324)
  Montre que des changements de formatage qui préservent le sens (séparateurs, casse, espacement) font varier la précision du few-shot dans de grandes proportions. À utiliser pour : comprendre pourquoi une modification de prompt est une affirmation à tester, pas un choix de style.
- [Article : "Rethinking the Role of Demonstrations", Min et al., 2022](https://arxiv.org/abs/2202.12837)
  Constate que remplacer aléatoirement les labels des démonstrations nuit à peine, alors que le format, l'espace des labels et la distribution des entrées comptent. À utiliser pour : ce qu'enseignent réellement les exemples few-shot.
- [Article : "Calibrate Before Use: Improving Few-Shot Performance of Language Models", Zhao et al., 2021](https://arxiv.org/abs/2102.09690)
  Nomme les biais de label majoritaire, de récence et de token commun dans les prompts few-shot et propose une calibration contextuelle. À utiliser pour : les biais qu'apporte un ensemble d'exemples.
- [Article : "Fantastically Ordered Prompts and Where to Find Them", Lu et al., 2021](https://arxiv.org/abs/2104.08786)
  Montre que l'ordre des mêmes exemples few-shot fait passer la précision d'un niveau proche de l'état de l'art à un niveau proche du hasard. À utiliser pour : comprendre pourquoi l'ordre des exemples est une variable à contrôler.
- [Article : "Chain-of-Thought Prompting Elicits Reasoning in Large Language Models", Wei et al., 2022](https://arxiv.org/abs/2201.11903)
  Le résultat d'origine du chain-of-thought few-shot, et sa conclusion que le gain n'apparaît qu'à partir d'une échelle de modèle suffisante. À utiliser pour : savoir quand demander du raisonnement aide.
- [Article : "Large Language Models are Zero-Shot Reasoners", Kojima et al., 2022](https://arxiv.org/abs/2205.11916)
  Le chain-of-thought zero-shot : une seule phrase déclencheuse suscite du raisonnement sans exemples. À utiliser pour : raisonner sans démonstrations écrites à la main.
- [Article : "Self-Consistency Improves Chain of Thought Reasoning in Language Models", Wang et al., 2022](https://arxiv.org/abs/2203.11171)
  Échantillonner plusieurs chemins de raisonnement et retenir la réponse majoritaire. À utiliser pour : échanger des tokens contre de la précision sur une tâche à réponse unique vérifiable.
- [Article : "Language Models Don't Always Say What They Think", Turpin et al., 2023](https://arxiv.org/abs/2305.04388)
  Montre un chain-of-thought de modèle qui omet le facteur de biais ayant réellement motivé sa réponse. À utiliser pour : comprendre pourquoi le raisonnement écrit n'est pas une explication fidèle.
- [Article : "Let Me Speak Freely? A Study on the Impact of Format Restrictions on Performance of Large Language Models", Tam et al., 2024](https://arxiv.org/abs/2408.02442)
  Mesure la baisse de précision du raisonnement sous des contraintes strictes de format de sortie. À utiliser pour : le coût d'un format imposé, et la façon d'ordonner les champs.
- [Article : "Lost in the Middle: How Language Models Use Long Contexts", Liu et al., 2023](https://arxiv.org/abs/2307.03172)
  La courbe en U : l'information au début et à la fin d'un long contexte est mieux utilisée que celle du milieu. À utiliser pour : décider où placer les documents et la question.
- [Article : "The Instruction Hierarchy: Training LLMs to Prioritize Privileged Instructions", Wallace et al., 2024](https://arxiv.org/abs/2404.13208)
  Définit les niveaux de privilège system, user et sortie d'outil et entraîne un modèle à suivre le plus élevé en cas de conflit. À utiliser pour : comprendre pourquoi l'emplacement d'une instruction change son poids.
- [Article : "When 'A Helpful Assistant' Is Not Really Helpful: Personas in System Prompts Do Not Improve Performances of Large Language Models", Zheng et al., 2023](https://arxiv.org/abs/2311.10054)
  Teste 162 personas dans des system prompts sur quatre familles de modèles et 2 410 questions factuelles, et ne trouve aucune amélioration par rapport à l'absence de persona, l'effet d'un persona étant largement aléatoire. À utiliser pour : trancher à partir de données le débat sur le role prompting.
- [Article : "Not what you've signed up for: Compromising Real-World LLM-Integrated Applications with Indirect Prompt Injection", Greshake et al., 2023](https://arxiv.org/abs/2302.12173)
  Introduit l'injection de prompt indirecte via du contenu récupéré et la démontre sur de vraies applications. À utiliser pour : comprendre comment un attaquant atteint un prompt dans lequel il ne saisit jamais rien.
- [Article : "Fine-Tuning or Retrieval? Comparing Knowledge Injection in LLMs", Ovadia et al., 2023](https://arxiv.org/abs/2312.05934)
  Compare le fine-tuning non supervisé à la récupération pour ajouter des connaissances et trouve la récupération systématiquement meilleure, aussi bien pour les connaissances vues à l'entraînement que pour les faits nouveaux. À utiliser pour : trancher entre prompt, RAG et fine-tuning.
- [Billet : "LLM01:2025 Prompt Injection", OWASP Gen AI Security Project](https://genai.owasp.org/llmrisk/llm01-prompt-injection/)
  La fiche de risque de référence de l'industrie : injection directe et indirecte, impacts, et mesures d'atténuation classées selon leur emplacement. À utiliser pour : le vocabulaire partagé et la liste des mesures d'atténuation.
- [Billet : "The lethal trifecta for AI agents", Simon Willison](https://simonwillison.net/2025/Jun/16/the-lethal-trifecta/)
  Des données privées, du contenu non fiable et un canal d'exfiltration rendent ensemble l'injection exploitable, et supprimer l'un des trois est la défense. À utiliser pour : comprendre pourquoi la vraie défense se situe en dehors du prompt.
- [Billet : "Your AI Product Needs Evals", Hamel Husain](https://hamel.dev/blog/posts/evals/)
  Un plaidoyer de praticien pour des vérifications de type test unitaire et des traces réelles journalisées comme base pour itérer sur un prompt. À utiliser pour : construire un jeu de régression à partir de vrais échecs.

## Lacunes

- Les guides d'OpenAI sur le prompt engineering, le raisonnement et la sortie structurée offriraient la vue d'un troisième éditeur, mais chaque page de `platform.openai.com` et de `developers.openai.com` a répondu 403 à une vérification par script et à une vérification par navigateur, donc aucune n'a pu être confirmée comme résolvable. À ajouter dès que l'une le pourra.
- Aucune source évaluée par les pairs ne mesure directement le versionnement de prompts ni la pratique des gabarits. Les leçons 15 et 16 l'enseignent à partir de la documentation des éditeurs et de la pratique ordinaire de l'ingénierie logicielle, et le disent.
