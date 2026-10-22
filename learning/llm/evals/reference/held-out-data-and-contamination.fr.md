---
title: "Données held-out et contamination"
description: "Discipline de partition entraînement/test pour un jeu d'eval, les deux voies de contamination, comment détecter chacune, et comment concevoir un jeu sur mesure qui leur résiste"
type: reference
---

# Données held-out et contamination

L'étape 1 condensée pour la consultation. La [leçon 1](../lessons/0001-held-out-and-contamination.md) couvre les deux voies de contamination et le test d'instruction guidée pour les détecter ; la [leçon 2](../lessons/0002-designing-contamination-resistance.md) couvre la conception d'un jeu d'eval sur mesure qui résiste à la contamination dès le départ. Cette fiche contient les définitions, les voies et la boîte à outils de prévention, côte à côte.

## Ce qu'exige « held-out »

Un jeu d'eval est held-out quand le modèle jugé n'a jamais vu ces exemples exacts, ni de paraphrases proches, pendant l'entraînement ou le fine-tuning. Cette seule propriété permet à un bon score de vouloir dire « cela généralise » plutôt que « cela a été mémorisé ». Avant de citer un score comme preuve, répondez : *pourquoi le modèle n'aurait-il pas pu obtenir la bonne réponse par mémorisation, ou parce qu'il a été réglé sur ce jeu précis ?* Sans réponse, le chiffre décrit l'eval, pas le modèle.

## Deux voies de contamination

| Voie | Ce qui se passe | Fuite littérale ? | Remède |
|---|---|---|---|
| Absorption au pré-entraînement | Un benchmark est aspiré dans des données d'entraînement issues du crawl du web avant que quiconque construise une eval dessus | Oui | Choisir ou construire des données peu susceptibles d'apparaître dans un corpus de pré-entraînement, ou tester leur présence |
| Surapprentissage itératif | Le même jeu d'eval est exécuté à répétition pendant le réglage d'un modèle ou d'un prompt, façonnant peu à peu le système pour réussir ces exemples précis | Non | Renouveler le jeu, ou garder en réserve une tranche intacte |

Les deux produisent le même symptôme : un chiffre qui a l'air bon et ne prédit pas le comportement en situation réelle. Les remèdes diffèrent parce que les causes diffèrent ; traiter l'une comme substitut de l'autre laisse la voie non traitée ouverte.

## Détecter l'absorption au pré-entraînement : le test d'instruction guidée

Donnez au modèle le début d'une instance de benchmark et demandez-lui de compléter le reste mot pour mot. Reproduire des détails qu'une supposition plausible ne retrouverait pas, une formulation exacte, un nombre inhabituel, un nom propre rare, est une forte preuve que cette instance figurait dans ses données d'entraînement (Golchin et Surdeanu, 2023). Ce test ne détecte que l'absorption ; il ne dit rien du surapprentissage itératif, qui ne laisse aucune trace de ce genre.

## Prévenir la contamination en construisant un jeu sur mesure

| Technique | Ce qu'elle fait | Quand elle s'applique | Limites |
|---|---|---|---|
| Postdater la date limite d'entraînement | Tirer les données d'eval de contenus créés après la date limite d'entraînement déclarée du modèle | Exige une date limite exacte et vérifiée, pas une affirmation marketing | Ne protège que de l'absorption ; un jeu d'eval périmé risque toujours le surapprentissage itératif |
| Chaîne canari (convention BIG-bench) | Intégrer une phrase-marqueur unique demandant à tout crawler d'exclure le contenu marqué | Tout jeu publié | Une demande, pas un mécanisme d'application ; dépend de la coopération des crawlers |
| Contrôle de recouvrement de n-grammes | Mesurer le recouvrement direct entre les données d'eval et un corpus connu | Seulement quand le corpus de pré-entraînement est connu et accessible | Inutilisable pour un modèle fermé aux données d'entraînement non divulguées |
| Garder le jeu non publié | Ne jamais le publier | Toujours disponible | La prévention la plus forte, au prix de la reproductibilité et du regard extérieur |

Les trois premières dépendent d'une condition (une date limite exacte, la coopération des crawlers, l'accès au corpus) ; garder un jeu privé est la seule technique sans prérequis, c'est pourquoi c'est le recours quand les autres ne s'appliquent pas.

## Avant de faire confiance à un score

- L'histoire de la contamination du jeu d'eval est énoncée, pas supposée : quelle voie a été vérifiée, et comment.
- Un benchmark public emprunté a été testé avec la méthode d'instruction guidée, ou il existe une raison documentée de juger ce risque faible.
- Un jeu d'eval sur mesure nomme la ou les techniques de prévention qui s'y appliquent, et leurs limites sont connues, pas seulement leur présence.
- Un jeu d'eval réutilisé pendant des mois de réglage a été renouvelé, ou il existe une tranche gardée en réserve et jamais touchée.

## Sources

- [Doc : "Define success criteria and build evaluations", Claude Platform Docs](https://platform.claude.com/docs/en/test-and-evaluate/develop-tests)
- [Article : "Time Travel in LLMs: Tracing Data Contamination in Large Language Models", Golchin and Surdeanu, 2023](https://arxiv.org/abs/2308.08493)
- [Article : "Beyond the Imitation Game: Quantifying and Extrapolating the Capabilities of Language Models" (BIG-bench), Srivastava et al., 2022](https://arxiv.org/abs/2206.04615)
- [Ressources](../RESOURCES.md)
