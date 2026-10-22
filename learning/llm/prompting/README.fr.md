---
title: Prompting
description: "Écrire, versionner et livrer les prompts d'une fonctionnalité LLM, prouver qu'une modification de prompt a aidé, et relire le prompt de production de quelqu'un d'autre"
type: topic
---

# Apprentissage : le prompting

Écrire les prompts qui se trouvent derrière une fonctionnalité LLM pour qu'ils fassent ce qui était prévu, qu'ils vivent dans le code sous forme de gabarits versionnés, et qu'ils ne changent que lorsqu'un jeu de régression montre que la modification a aidé. Terminer capable de relire le prompt de production de quelqu'un d'autre et de nommer ce que coûte chacun de ses choix, au lieu de dire qu'il paraît bizarre.

**Dernière leçon :** [24. Quand le conseil habituel est faux](lessons/0024-when-the-usual-advice-is-wrong.md)

## Objectif

- Écrire un prompt dont les rôles, les instructions et la structure sont lisibles par un collègue et suivis par le modèle, et dire ce que le modèle reçoit réellement.
- Choisir, ordonner et auditer des exemples few-shot, en nommant le biais que chaque choix risque d'introduire.
- Décider quand demander du raisonnement, prompter un modèle de raisonnement autrement qu'un modèle standard, et expliquer pourquoi le raisonnement écrit n'est pas une explication de la réponse.
- Obtenir une sortie structurée qu'un programme peut analyser, et organiser un long contexte pour que le modèle utilise ce qu'il contient.
- Garder les prompts dans une base de code sous forme de gabarits versionnés, ordonnés pour que le préfixe stable puisse être mis en cache.
- Montrer avec un jeu de régression et une comparaison appariée si une modification de prompt a aidé, plutôt que d'en juger à partir de quelques sorties.
- Concevoir un prompt qui traite une entrée non fiable, et dire de quels risques le prompt ne peut pas se défendre seul.
- Choisir entre un meilleur prompt, la récupération (retrieval) et le fine-tuning pour un échec donné, et relire le prompt de production de quelqu'un d'autre en nommant ce que coûte chaque choix.

## Contraintes

- D'abord l'application, utilisable depuis une fenêtre de chat : les étapes 1 à 6 fonctionnent dans n'importe quelle interface de chat, les étapes 7 à 10 supposent que le prompt vit dans le code.
- Aucun fournisseur ni modèle imposé. Les exemples sont neutres vis-à-vis des fournisseurs ; lorsqu'une technique relève du comportement documenté d'un seul éditeur, la leçon le dit.
- Aucune connaissance préalable du prompting n'est supposée. Savoir ce qu'est un LLM, au niveau de « il prédit le token suivant », suffit.

## Hors périmètre

- La construction de prompts sur un contexte récupéré et le budget de la fenêtre de contexte : voir [`llm/rag`](../../llm/rag/) et sa [fiche sur la génération à partir de la récupération](../../llm/rag/reference/generation-from-retrieval.md). Ce parcours enseigne le prompting en général et renvoie vers cette fiche pour le cas de la récupération.
- Les descriptions d'outils comme surface de prompt, l'injection de prompt dans un agent doté d'outils et le prompt caching sous concurrence : voir [`llm/agents`](../../llm/agents/). Ce parcours couvre le prompting sans outils et renvoie vers ces leçons plutôt que de les répéter.
- La conception de prompts de juge et la méthodologie d'évaluation : voir [`llm/evals`](../../llm/evals/) et sa [fiche go/no-go](../../llm/evals/reference/go-no-go.md). Ce parcours utilise une évaluation pour mesurer une modification de prompt et n'enseigne pas comment en construire une.
- Le décodage contraint, le côté serving de la sortie structurée : voir [`llm/inference`](../../llm/inference/). Ce parcours demande de la structure du côté du prompt.
- La façon dont le suivi d'instructions et le raisonnement sont entraînés dans un modèle : voir [`llm/post-training`](../../llm/post-training/). Ce parcours couvre la façon de les utiliser de l'extérieur.

## Le fil conducteur

Dix étapes, de ce qu'est un prompt pour le modèle jusqu'au jugement nécessaire pour relire celui d'un autre. Une étape comprend plusieurs leçons et les frontières sont souples ; ce qui termine une étape, c'est la capacité acquise, pas le nombre de leçons.

| Étape | Leçons | Contenu | Terminée quand |
|---|---|---|---|
| 1. Ce qu'est un prompt pour le modèle | 0001 à 0002 | Tokens, chat templates, rôles, system prompt et hiérarchie des instructions | Vous savez dire quelle séquence le modèle reçoit pour une conversation donnée et où chaque instruction doit se placer |
| 2. Instructions et structure | 0003 à 0005 | Instructions claires, délimiteurs et balises, sensibilité au formatage | Vous savez écrire un prompt qu'un débutant pourrait suivre et qui sépare les instructions des données |
| 3. Exemples few-shot | 0006 à 0007 | Ce qu'enseignent les démonstrations, biais de label majoritaire, de récence et d'ordre | Vous savez choisir et ordonner des exemples et nommer le biais que chaque choix risque d'introduire |
| 4. Raisonnement | 0008 à 0010 | Chain-of-thought, self-consistency, fidélité, prompter des modèles de raisonnement | Vous savez décider s'il faut demander du raisonnement et comment, pour un modèle et une tâche donnés |
| 5. Sortie structurée | 0011 à 0012 | Demander un schéma, le valider, contraintes de format contre qualité du raisonnement | Vous obtenez une sortie qu'un programme analyse, sans la payer en qualité de réponse |
| 6. Long contexte | 0013 à 0014 | Effets de position, disposition des documents, extraction de citations | Vous savez organiser un long contexte pour que le modèle utilise ce qui se trouve en son milieu |
| 7. Prompts dans une base de code | 0015 à 0017 | Gabarits, versionnement par rapport à un snapshot de modèle, disposition pour le prompt caching | Vous gardez les prompts sous forme de gabarits versionnés dont le préfixe stable est cacheable |
| 8. Mesurer une modification de prompt | 0018 à 0019 | Jeux de régression issus de vrais échecs, comparaison appariée face au bruit | Vous savez montrer avec un chiffre si le prompt B bat le prompt A |
| 9. Sécurité des prompts | 0020 à 0021 | Injection de prompt directe et indirecte, ce que le prompt peut et ne peut pas défendre | Vous savez concevoir un prompt pour une entrée non fiable et nommer les risques qu'il laisse au système |
| 10. Jugement | 0022 à 0024 | Prompt contre RAG contre fine-tuning, relire un prompt de production, modifier un prompt dont d'autres dépendent, quand le conseil habituel est faux | On vous fait confiance pour trancher sur un prompt et l'expliquer à quelqu'un d'autre |

## Leçons

Suivez-les dans l'ordre.

| # | Leçon | Enseigne |
|---|---|---|
| [0001](lessons/0001-what-the-model-sees.md) | Ce que voit le modèle | Un prompt parvient au modèle sous la forme d'une séquence unique de tokens construite par un chat template, donc les rôles sont un formatage sur lequel le modèle a été entraîné, pas des canaux séparés |
| [0002](lessons/0002-system-prompts-and-roles.md) | System prompts et rôles | Ce qui relève du system prompt et ce qui relève du tour de l'utilisateur, et pourquoi le modèle classe les instructions selon leur emplacement |
| [0003](lessons/0003-clear-instructions.md) | Des instructions claires | Écrire une instruction qu'un débutant capable pourrait suivre : le contexte, la tâche, les contraintes et à quoi ressemble « terminé » |
| [0004](lessons/0004-structure-and-delimiters.md) | Structure et délimiteurs | Séparer les instructions des données avec des balises et des sections pour que le modèle sache distinguer les unes des autres |
| [0005](lessons/0005-format-sensitivity.md) | Sensibilité au format | Pourquoi un changement de formatage sans signification peut faire varier la précision, et pourquoi chaque modification de prompt devient une affirmation à tester |
| [0006](lessons/0006-what-examples-teach.md) | Ce qu'enseignent les exemples few-shot | Les démonstrations enseignent surtout le format, l'espace des labels et la distribution des entrées, ce qui change la façon de les choisir |
| [0007](lessons/0007-few-shot-biases.md) | Biais du few-shot | Biais de label majoritaire, de récence et d'ordre dans les prompts few-shot, et comment choisir et ordonner les exemples pour s'en prémunir |
| [0008](lessons/0008-chain-of-thought.md) | Chain-of-thought | Quand demander un raisonnement intermédiaire améliore une réponse, et quand cela ne fait qu'ajouter des tokens |
| [0009](lessons/0009-self-consistency-and-faithfulness.md) | Self-consistency et fidélité | Échantillonner plusieurs chemins de raisonnement pour voter sur une réponse, et pourquoi le raisonnement écrit n'est pas une explication fidèle |
| [0010](lessons/0010-prompting-reasoning-models.md) | Prompter les modèles de raisonnement | Pourquoi un modèle qui réfléchit déjà a besoin d'objectifs et de contraintes plutôt que d'étapes scénarisées |
| [0011](lessons/0011-structured-output-from-the-prompt.md) | Sortie structurée depuis le prompt | Demander une sortie qu'un programme peut analyser, puis la valider, car demander n'est pas une garantie |
| [0012](lessons/0012-format-constraints-and-reasoning.md) | Contraintes de format et raisonnement | Un format de sortie strict peut coûter de la qualité de raisonnement, et comment ordonner les champs pour que la réponse vienne après la réflexion |
| [0013](lessons/0013-position-in-long-context.md) | La position dans un long contexte | Les modèles exploitent mieux l'information aux extrémités d'un long contexte qu'en son milieu, ce qui décide de l'emplacement des documents et de la question |
| [0014](lessons/0014-working-with-long-documents.md) | Travailler avec de longs documents | Baliser les documents avec leurs métadonnées et faire extraire des citations au modèle avant qu'il réponde |
| [0015](lessons/0015-prompt-templates.md) | Gabarits de prompt | Découper un prompt en un gabarit fixe et des variables remplies à chaque requête, et empêcher une entrée non fiable de casser la structure |
| [0016](lessons/0016-versioning-prompts.md) | Versionner les prompts | Traiter un prompt comme du code : épinglé à un snapshot de modèle, versionné, relu et annulé comme n'importe quelle autre modification |
| [0017](lessons/0017-prompt-caching-and-layout.md) | Prompt caching et disposition | Ordonner un prompt avec les parties stables en premier pour que le fournisseur puisse mettre le préfixe en cache |
| [0018](lessons/0018-a-regression-set-for-a-prompt.md) | Un jeu de régression pour un prompt | Construire le petit ensemble de cas qu'une modification de prompt ne doit pas casser, en partant de vrais échecs |
| [0019](lessons/0019-comparing-two-prompts.md) | Comparer deux prompts | Décider si le prompt B bat le prompt A grâce à une comparaison appariée qui sépare la modification du bruit d'une exécution à l'autre |
| [0020](lessons/0020-prompt-injection.md) | Injection de prompt | Comment du texte présent dans l'entrée peut écraser les instructions de l'auteur, directement ou caché dans un contenu que le modèle lit |
| [0021](lessons/0021-what-a-prompt-cannot-defend.md) | Ce qu'un prompt ne peut pas défendre | Quelles défenses relèvent du prompt, et pourquoi les vraies se situent dans ce que le système permet au modèle de faire |
| [0022](lessons/0022-prompt-rag-or-fine-tune.md) | Prompt, RAG ou fine-tuning | Choisir entre un meilleur prompt, la récupération et le fine-tuning selon ce qu'est réellement l'échec |
| [0023](lessons/0023-reviewing-a-production-prompt.md) | Relire un prompt de production | Relire le prompt de quelqu'un d'autre en nommant ce que coûte chaque choix, et modifier un prompt dont d'autres dépendent sans les casser |
| [0024](lessons/0024-when-the-usual-advice-is-wrong.md) | Quand le conseil habituel est faux | Reconnaître quand le conseil de prompting standard échoue pour un modèle ou une tâche donnés, et trancher le différend à partir de la source primaire |

## Référence

- [Glossaire](GLOSSARY.md) : termes de référence pour ce sujet
- [Ressources](RESOURCES.md) : sources fiables, chacune annotée avec ce qu'elle couvre
- [Anatomie d'un prompt](reference/prompt-anatomy.md) : les rôles, ce qui va où, et la liste de contrôle de structure des étapes 1 et 2
- [Few-shot et raisonnement](reference/few-shot-and-reasoning.md) : choisir et ordonner les exemples, et quand demander du raisonnement, issus des étapes 3 et 4
- [Sortie structurée et long contexte](reference/structured-output-and-long-context.md) : obtenir une sortie analysable et organiser de longues entrées, issus des étapes 5 et 6
- [Prompts en production](reference/prompts-in-production.md) : gabarits, versionnement, disposition adaptée au cache et boucle de mesure, issus des étapes 7 et 8
- [Sécurité des prompts](reference/prompt-security.md) : voies d'injection et emplacement de chaque défense, issus de l'étape 9
- [Liste de contrôle de relecture d'un prompt](reference/prompt-review-checklist.md) : les questions à poser au prompt de quelqu'un d'autre, et prompt contre RAG contre fine-tuning, issues de l'étape 10

## Comment cela fonctionne

Chaque leçon est courte et autonome. Les corrigés sont repliés : rappelez-vous d'abord, puis ouvrez-les. Les exercices en situation réelle comptent plus que la lecture, et les espacer dans le temps est justement le but. Tout ce qui reste flou à la fin d'une leçon mérite d'être suivi jusqu'à sa source primaire avant de passer à la suite.
