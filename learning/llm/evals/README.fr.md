---
title: "Evals"
description: "Prouver qu'une modification de modèle a aidé : construire l'eval, garder honnêtement les données held-out et défendre le chiffre face à la contamination"
type: topic
---

# Apprentissage : les evals

Savoir construire une eval qui attrape une régression qu'un simple test au feeling raterait, et s'en servir pour prendre, sur une modification de modèle (un fine-tuning, un changement de prompt, un changement de RAG), une décision go/no-go que vous pouvez défendre avec un chiffre plutôt qu'avec une impression.

**Dernière leçon :** [19. Relire un rapport d'eval](lessons/0019-reviewing-an-eval-report.md)

## Objectif

- Concevoir, pour une modification de modèle donnée, un jeu d'eval held-out qui résiste à la contamination et qui attraperait une régression qu'une relecture rapide raterait.
- Utiliser cette eval pour prendre et défendre une décision go/no-go sur la livraison du changement, en nommant le chiffre et ce qui le rend digne de confiance.
- Comparer une approche LLM-as-judge à des métriques propres à la tâche pour un cas donné, et choisir entre elles sur le fond plutôt que par défaut.
- Relire le rapport d'eval ou le harness de quelqu'un d'autre et nommer précisément ce qui rendrait son chiffre peu fiable (un jeu non held-out, un juge non calibré, une exécution unique sans estimation de variance, un rang de classement tenant lieu de décision propre à la tâche), plutôt que dire que cela paraît léger.

## Contraintes

- Aucune restriction de domaine : couvre l'évaluation des fine-tunings, des changements de prompt et des changements de RAG, puisque la même discipline d'eval s'applique aux trois.
- Aucune pile imposée ni expérience préalable supposée.

## Hors périmètre

- Juger une variante, la conception d'un jeu held-out, les métriques et le jeu de régression tels qu'enseignés dans un seul arc de fine-tuning : voir [`llm/finetuning`](../../llm/finetuning/) (leçons 0020-0024), subordonné spécifiquement au fine-tuning. Cet espace de travail traite l'évaluation comme sujet à part entière et y renvoie sans le répéter.
- Quantifier un modèle et juger ce que la quantification a coûté : voir [`llm/quantization`](../../llm/quantization/). Ce parcours utilise une eval pour mesurer la perte due à la quantification ; celui-ci enseigne comment l'eval est construite.
- Écrire et versionner le prompt testé : voir [`llm/prompting`](../../llm/prompting/). Ce parcours utilise une eval pour mesurer un changement de prompt ; celui-ci enseigne comment l'eval est construite.
- Distiller un modèle plus petit et mesurer ce qu'il a perdu face à son professeur : voir [`llm/distillation`](../../llm/distillation/). Ce parcours utilise une eval pour comparer un élève à son professeur ; celui-ci enseigne comment l'eval est construite.

## Le fil conducteur

Treize étapes, d'une eval digne de confiance à un go/no-go défendu qui tient compte des humains, de la sécurité, des agents, du RAG, de la production, du coût et de l'attrait d'un classement public, pour finir par le jugement nécessaire pour relire l'eval de quelqu'un d'autre et en maintenir une honnêtement comme infrastructure partagée. Une étape comprend plusieurs leçons et les frontières sont souples ; ce qui termine une étape, c'est la capacité acquise, pas le nombre de leçons.

| Étape | Leçons | Contenu | Terminée quand |
|---|---|---|---|
| 1. Données held-out et contamination | 0001 à 0002 | Discipline de partition entraînement/test, détection de la contamination et ses sources | Vous savez concevoir un jeu held-out qui résiste à la contamination |
| 2. Métriques propres à la tâche | 0003 à 0004 | Exact match, F1, BLEU/ROUGE, métriques par exécution de code, choix selon la tâche | Vous savez choisir et justifier une métrique pour une tâche donnée |
| 3. LLM-as-judge | 0005 à 0006 | Conception du prompt de juge, calibration, biais de position et de verbosité, accord avec les humains | Vous savez construire un prompt de juge et nommer ses modes de défaillance |
| 4. Construire le harness | 0007 à 0008 | Frameworks d'eval, exécutions reproductibles, transformer une conception en chiffre | Vous avez un harness d'eval exécutable qui produit un chiffre digne de confiance |
| 5. Le go/no-go | 0009 à 0010 | Significativité statistique contre bruit, seuils de régression, communiquer la décision | Vous savez défendre une décision de livrer ou non avec un chiffre et dire pourquoi il est digne de confiance |
| 6. L'évaluation humaine comme méthode | 0011 | Guides d'annotation, échantillonnage pour la relecture, kappa de Cohen, et ce que coûte une étiquette humaine | Vous savez mesurer précisément l'accord inter-annotateurs et diagnostiquer une valeur basse |
| 7. Évaluation de la sécurité et red-teaming | 0012 | Red-teaming, jailbreaks et taux de réussite des attaques, sur-refus et XSTest | Vous savez rapporter à la fois un taux de refus et une métrique de sur-refus, et expliquer pourquoi aucun des deux seul n'est une eval de sécurité |
| 8. Évaluer les agents et l'usage d'outils | 0013 | Trajectoires, réussite de la tâche contre précision par étape, fiabilité `pass^k` | Vous savez expliquer pourquoi la réussite de la tâche l'emporte sur la correspondance étape par étape, et pourquoi la réussite sur un seul essai n'est pas de la fiabilité sur essais répétés |
| 9. Évaluation propre au RAG | 0014 | Fidélité/groundedness, exactitude des citations, séparer un échec de récupération d'un échec de génération | Vous savez mesurer indépendamment la fidélité et l'exactitude des citations, et diagnostiquer de quel côté d'un pipeline RAG la défaillance vient réellement |
| 10. Évaluation en ligne | 0015 à 0016 | A/B tests, OEC et métriques garde-fous, télémétrie de production, dérive, décalage entraînement-service | Vous savez choisir un OEC défendable avec une métrique garde-fou, et attribuer correctement un écart hors ligne/en ligne à la variance, à la dérive ou à une erreur d'ingénierie |
| 11. Coût et latence comme dimensions d'eval | 0017 | Latence de queue contre moyenne, coût par requête/token, intégrer les deux au go/no-go | Vous savez défendre un go/no-go qui pèse ensemble qualité, latence de queue et coût, et pas la qualité seule |
| 12. Benchmarks publics | 0018 | Contamination/saturation des benchmarks statiques, divulgation sélective des arènes, biais de style à l'échelle d'un classement | Vous savez expliquer pourquoi un rang de classement échoue au test de l'OEC et ne remplace pas un go/no-go propre à la tâche |
| 13. Jugement | 0019 | Relire des rapports d'eval, trancher des affirmations contestées à partir de sources primaires, maintenir une suite d'evals dont d'autres dépendent | On vous fait confiance pour relire l'eval de quelqu'un d'autre et défendre son chiffre ou nommer ce qui le rend peu fiable, et pour maintenir une suite d'evals comme infrastructure partagée sans casser les décisions des autres |

## Leçons

Suivez-les dans l'ordre.

| # | Leçon | Enseigne |
|---|---|---|
| [0001](lessons/0001-held-out-and-contamination.md) | Données held-out et contamination | Pourquoi un chiffre d'eval ne vaut que ce que le modèle n'a jamais vu |
| [0002](lessons/0002-designing-contamination-resistance.md) | Concevoir la résistance à la contamination | Prévenir la contamination d'un jeu d'eval sur mesure dès le départ, au lieu de seulement la détecter après coup |
| [0003](lessons/0003-task-specific-metrics.md) | Métriques propres à la tâche | Exact match, F1 au niveau des tokens et BLEU/ROUGE, et le mode de défaillance de chacun |
| [0004](lessons/0004-code-execution-metrics.md) | Métriques par exécution de code et choix d'une métrique | Correction fonctionnelle, estimateur pass@k et principe de décision pour choisir une métrique par tâche |
| [0005](lessons/0005-judge-prompt-design-and-calibration.md) | Conception du prompt de juge et calibration | Comment écrire un prompt de juge qui note de façon cohérente, et ce que signifie, pour un juge, être calibré avant qu'on lui fasse confiance |
| [0006](lessons/0006-judge-bias-and-human-agreement.md) | Biais du juge et accord avec les humains | Biais de position et biais de verbosité dans le LLM-as-judge, et comment mesurer l'accord d'un juge avec des annotateurs humains |
| [0007](lessons/0007-eval-frameworks-and-harness.md) | Frameworks d'eval et construction d'un harness | Les quatre étapes de tout harness d'eval, et le choix entre construire une eval-as-code sur mesure et réutiliser un harness de benchmark standardisé |
| [0008](lessons/0008-reproducible-runs.md) | Exécutions reproductibles | Pourquoi la même eval peut produire des chiffres différents d'une exécution à l'autre, et ce qu'un résultat digne de confiance doit journaliser avec le score |
| [0009](lessons/0009-statistical-significance-vs-noise.md) | Significativité statistique et bruit | Pourquoi un écart de score doit se mesurer face au bruit qui pourrait le produire par hasard, et pourquoi la comparaison appariée l'emporte sur le traitement de deux scores comme indépendants |
| [0010](lessons/0010-defending-the-go-no-go-call.md) | Défendre le go/no-go | Comment fixer honnêtement un seuil de régression, et tout ce qu'une défense complète d'un go/no-go doit citer |
| [0011](lessons/0011-human-evaluation-as-a-method.md) | L'évaluation humaine comme méthode | La leçon 6 a mesuré un juge face à des annotateurs humains sans jamais enseigner comment une note humaine est réellement produite, et le chiffre d'accord brut sur lequel elle s'appuyait doit lui-même être corrigé du hasard avant de signifier quoi que ce soit |
| [0012](lessons/0012-safety-and-red-teaming-evaluation.md) | Évaluation de la sécurité et red-teaming | Une eval de sécurité qui ne mesure que la fréquence à laquelle un modèle refuse des prompts réellement dangereux ne mesure que la moitié d'un compromis, puisque le même réglage qui fait monter ce chiffre peut tout aussi bien faire monter la fréquence à laquelle le modèle refuse des prompts qui n'ont jamais été dangereux |
| [0013](lessons/0013-evaluating-agents-and-tool-use.md) | Évaluer les agents et l'usage d'outils | Une tâche d'agent a de nombreux chemins valables vers le même bon résultat, donc la noter face à une seule séquence d'actions de référence répète l'erreur de l'exact match à l'échelle de la trajectoire, et même le taux de réussite d'un seul essai cache la fréquence à laquelle le même agent échoue sur la même tâche au second essai |
| [0014](lessons/0014-rag-specific-evaluation.md) | Évaluation propre au RAG | llm/rag a tracé la ligne entre un échec de récupération et un échec de génération mais a laissé indéfini le contrôle côté génération, et ce contrôle demande en réalité deux chiffres distincts, pas un seul, puisqu'une affirmation fidèle et une affirmation correctement citée peuvent échouer indépendamment l'une de l'autre |
| [0015](lessons/0015-ab-tests-and-guardrail-metrics.md) | A/B tests et métriques garde-fous | Toutes les étapes jusqu'ici étaient hors ligne, mais livrer à de vrais utilisateurs demande sa propre métrique de décision, et cette métrique seule est exactement aussi dangereuse que les chiffres de sécurité isolés dont les étapes précédentes ont déjà dit de ne pas se fier à eux isolément |
| [0016](lessons/0016-production-telemetry-and-drift.md) | Télémétrie de production et dérive | Un chiffre hors ligne et un chiffre en production qui divergent ne sont pas un problème mais trois problèmes différents, et traiter un bug d'ingénierie comme une dérive, ou une dérive comme un bug d'ingénierie, envoie le correctif à la mauvaise équipe |
| [0017](lessons/0017-cost-and-latency-as-eval-dimensions.md) | Coût et latence comme dimensions d'eval | Un gain de qualité mesuré isolément de ce qu'il coûte à servir n'est que la moitié d'un go/no-go, et une latence moyenne cache précisément la queue qui détermine si les utilisateurs perçoivent réellement le système comme rapide |
| [0018](lessons/0018-public-benchmarks.md) | Benchmarks publics | Une position dans un classement est une métrique mobile optimisée par d'autres que vous, pour des utilisateurs qui ne sont pas les vôtres, notée par un processus aux vecteurs de manipulation documentés, ce qui en fait exactement le genre de métrique dont la leçon 15 déconseillait de se fier comme signal de go/no-go |
| [0019](lessons/0019-reviewing-an-eval-report.md) | Relire un rapport d'eval | Nommer précisément ce qui rendrait le chiffre d'un rapport d'eval peu fiable (contamination, juge non calibré, exécution unique sans estimation de variance, rang de classement tenant lieu de décision propre à la tâche), plutôt que dire que cela paraît léger |

## Référence

- [Glossaire](GLOSSARY.md) : termes de référence pour ce sujet
- [Ressources](RESOURCES.md) : sources fiables
- [Données held-out et contamination](reference/held-out-data-and-contamination.md) : les deux voies de contamination, le test d'instruction guidée et la boîte à outils de prévention pour un jeu d'eval sur mesure
- [Métriques](reference/metrics.md) : exact match, F1, BLEU/ROUGE et pass@k côte à côte, avec la formule de pass@k et le principe de décision pour choisir entre elles
- [LLM-as-Judge](reference/llm-as-judge.md) : la liste de contrôle de conception du prompt de juge, la calibration et la compression des scores, les biais de position et de verbosité, et la barre de l'accord humain-humain
- [Harness d'eval](reference/eval-harness.md) : le pipeline en quatre étapes, openai/evals contre lm-evaluation-harness, et ce qu'un chiffre défendable journalise avec le score
- [Go/No-Go](reference/go-no-go.md) : la formule de l'erreur standard, la comparaison appariée, fixer honnêtement un seuil et tout ce qu'une défense complète cite

## Comment cela fonctionne

Chaque leçon est courte et autonome. Les corrigés sont repliés : rappelez-vous d'abord, puis ouvrez-les. Les exercices en situation réelle comptent plus que la lecture, et les espacer dans le temps est justement le but. Tout ce qui reste flou à la fin d'une leçon mérite d'être suivi jusqu'à sa source primaire avant de passer à la suite.
