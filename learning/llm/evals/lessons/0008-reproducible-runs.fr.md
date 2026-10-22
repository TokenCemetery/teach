---
title: "8. Exécutions reproductibles"
description: "Pourquoi la même eval peut produire des chiffres différents d'une exécution à l'autre, et ce qu'un résultat digne de confiance doit journaliser avec le score"
type: lesson
---

# Leçon 8. Exécutions reproductibles

**Lien avec la mission :** C'est le point d'orgue de l'étape 4 : un harness (leçon 7) n'est que la moitié du travail. Un chiffre qu'il produit n'est digne de confiance qu'une fois sa variance d'une exécution à l'autre comprise et ce qui l'a produit journalisé, ce qui permet à une comparaison ultérieure de signifier quelque chose.
**Source primaire :** [Dépôt : lm-evaluation-harness, EleutherAI](https://github.com/EleutherAI/lm-evaluation-harness)
**Prérequis :** [Leçon 7](0007-eval-frameworks-and-harness.md), [Contamination des données](../GLOSSARY.md)

## Échauffement

1. ▢ Nommez les quatre étapes de tout harness d'eval.

<details markdown="1"><summary>Vérifier</summary>

Charger le jeu d'eval held-out, générer les sorties du modèle, les noter avec la métrique ou le juge choisi, et agréger les scores par exemple en un chiffre de synthèse.

</details>

2. ▢ Quand une équipe doit-elle choisir openai/evals plutôt que lm-evaluation-harness ?

<details markdown="1"><summary>Vérifier</summary>

Quand elle évalue une capacité propre à la mission qu'aucun benchmark standardisé existant ne couvre, puisque openai/evals est conçu pour définir une eval sur mesure sous forme de code, alors que lm-evaluation-harness est conçu pour exécuter des configurations de benchmarks préexistantes.

</details>

## À savoir

### Pourquoi la même eval peut donner deux chiffres différents

Un modèle échantillonné à une température non nulle produit des complétions différentes d'une exécution à l'autre, même pour un prompt identique, ce qui signifie des scores par exemple différents et un chiffre agrégé différent à chaque exécution de l'eval, sans que rien d'anormal se soit produit. Si la notation utilise aussi un juge LLM (étape 3), cela ajoute une seconde couche de bruit d'échantillonnage par-dessus la variance propre au modèle testé. Rien de tout cela n'est un bug du harness ; c'est le harness qui rapporte fidèlement un processus stochastique, et cela signifie que le chiffre d'une seule exécution est un échantillon tiré d'une distribution, pas un fait fixe sur le modèle.

### Le compromis du déterminisme

Régler la température sur 0 (décodage greedy) retire l'aléa côté génération et rend les exécutions bien plus répétables, ce qui est attrayant pour une eval dont la notation dépend d'une reproductibilité exacte, comme l'exact match. Le coût : le décodage greedy peut ne pas refléter le comportement réel du modèle en déploiement, si le système déployé échantillonne à une température non nulle. Une eval exécutée entièrement en greedy peut mesurer un mode que le système réel utilise rarement. Là où le comportement déployé échantillonne vraiment, l'approche la plus honnête est d'exécuter plusieurs échantillons par exemple à la température de déploiement (la même idée que le pass@k de la leçon 4 pour le code) et de rapporter la dispersion entre eux, pas seulement la valeur ponctuelle d'une seule exécution.

### Un seed aide, mais ne garantit pas des résultats identiques

Fixer un seed aléatoire pour la génération réduit la variance entre exécutions sur une même configuration, mais ne garantit pas des résultats identiques bit à bit entre matériels, versions de bibliothèques ou compositions de batch différents, puisque le calcul en virgule flottante n'est pas parfaitement associatif dans tous ces cas. Un seed est un contrôle réel et utile, pas un contrôle absolu ; traiter « on a fixé un seed » comme la preuve que deux exécutions sont directement comparables, c'est surestimer ce qu'un seed peut promettre.

### Ce qui rend un chiffre rapporté défendable par la suite

Un chiffre seul, sans rien sur la façon dont il a été produit, ne peut pas être comparé honnêtement à un chiffre ultérieur, issu d'une réexécution, d'un autre checkpoint ou d'un autre cycle d'eval : toute différence entre eux peut être un vrai changement ou simplement de la variance de pipeline, et rien dans un score nu ne permet de trancher. Un résultat défendable journalise, avec le score, ce qui l'a réellement produit : le seed aléatoire utilisé, la température de génération, les versions du modèle et du framework, la version du jeu d'eval et, quand plusieurs échantillons ont été exécutés, la dispersion entre eux, pas seulement leur moyenne. C'est ce dont une comparaison ultérieure, ou le go/no-go vers lequel l'étape 5 conduit, a réellement besoin pour être honnête sur le fait qu'une différence observée reflète le modèle ou le bruit.

## Pratique

1. ▢ Une équipe exécute deux fois la même eval sur le même modèle, à la température 0,7, et obtient deux scores agrégés différents. Est-ce la preuve que le harness est cassé ? Pourquoi ou pourquoi pas ?

<details markdown="1"><summary>Vérifier</summary>

Non. Une température non nulle rend la génération stochastique, donc des complétions différentes, et donc des scores par exemple différents, sont attendus d'une exécution à l'autre sans que rien soit anormal. Le harness rapporte fidèlement un processus stochastique ; le chiffre d'une seule exécution est un échantillon, pas un fait fixe.

</details>

2. ▢ Qu'apporte le réglage de la température sur 0 pour une eval, et que coûte-t-il, si le système déployé échantillonne en réalité à la température 0,7 ?

<details markdown="1"><summary>Vérifier</summary>

Il apporte de la répétabilité : le décodage greedy retire l'aléa côté génération, donc les exécutions deviennent bien plus cohérentes. Il coûte du réalisme : l'eval mesure un mode de décodage (greedy) que le système réel utilise rarement, donc le résultat peut ne pas refléter le comportement réel du modèle déployé à 0,7.

</details>

3. ▢ Pourquoi fixer un seed aléatoire ne garantit-il pas que deux exécutions d'eval produiront des résultats identiques ?

<details markdown="1"><summary>Indice</summary>

Pensez à ce qui d'autre pourrait différer entre deux exécutions en dehors du seed.

</details>

<details markdown="1"><summary>Vérifier</summary>

Un seed contrôle l'aléa au sein d'une configuration donnée, mais le calcul en virgule flottante n'est pas parfaitement associatif entre matériels, versions de bibliothèques ou compositions de batch différents, donc ces différences peuvent quand même produire des résultats différents avec le même seed. Un seed est un contrôle réel, pas une garantie absolue de sortie identique bit à bit.

</details>

4. ▢ L'équipe A rapporte un score d'eval de 72,3 pour un modèle. Un mois plus tard, l'équipe B relance « la même eval » sur le même modèle et obtient 69,8, sans aucune information de seed, de température ou de version journalisée lors de l'exécution d'origine de l'équipe A. Que peut-on honnêtement conclure de l'écart de 2,5 points ?

<details markdown="1"><summary>Vérifier</summary>

Très peu, en soi. Sans connaître la température, le seed, les versions du modèle et du framework, ni la version du jeu d'eval qu'a utilisés l'équipe A, il n'y a aucun moyen de dire si l'écart reflète un vrai changement (un autre checkpoint, une autre version du jeu d'eval) ou la variance ordinaire d'une exécution à l'autre due à l'échantillonnage. La conclusion honnête est que la comparaison n'a pas encore de sens tant que les détails de production des deux exécutions ne sont pas connus et appariés, ou que la variance sur des exécutions répétées n'est pas mesurée directement.

</details>

5. ▢ Laquelle de ces affirmations est vraie de ce qui rend un chiffre d'eval rapporté défendable ?

    - a) Le score d'une seule exécution suffit à lui seul, tant que le harness s'est exécuté sans erreur
    - b) Le score doit être rapporté avec ce qui l'a produit (seed, température, versions, version du jeu d'eval) et, le cas échéant, sa dispersion sur plusieurs exécutions
    - c) Fixer un seed aléatoire garantit des résultats identiques sur n'importe quel matériel ou version de bibliothèque
    - d) Le décodage greedy devrait toujours être utilisé pour les evals, quelle que soit la température d'échantillonnage réelle du système déployé

<details markdown="1"><summary>Vérifier</summary>

**b)** Journaliser les détails de production et, là où il y a échantillonnage, la dispersion entre exécutions, est ce qui permet à une comparaison ultérieure de distinguer un vrai changement du bruit. (a) est faux : un chiffre isolé ne peut être comparé à rien plus tard sans savoir ce qui l'a produit. (c) est faux : un seed réduit la variance entre matériels ou versions différents sans l'éliminer. (d) est faux : le décodage greedy sacrifie du réalisme quand le système déployé échantillonne vraiment, ce qui est un vrai coût, pas un choix gratuit.

</details>

## Exercices en situation réelle

- [ ] Pour une eval que vous exécutez, vérifiez si son harness journalise aujourd'hui le seed, la température et les versions du modèle/framework avec le score, et ajoutez ce qui manque.
- [ ] Si votre eval échantillonne à une température non nulle, exécutez-la plusieurs fois (ou avec plusieurs échantillons par exemple) et notez la dispersion entre exécutions, pas seulement un chiffre.
- [ ] Demain : retrouvez un ancien résultat d'eval que vous ou votre équipe avez rapporté, et vérifiez si assez de choses ont été journalisées avec lui pour savoir si une future réexécution serait directement comparable.

## Pour aller plus loin

- [Dépôt : lm-evaluation-harness, EleutherAI](https://github.com/EleutherAI/lm-evaluation-harness)
- [Dépôt : openai/evals, OpenAI](https://github.com/openai/evals)
- [Ressources](../RESOURCES.md)

---

Ça ne passe pas ? Relisez la source primaire en haut de page, car cette leçon la condense et c'est dans la condensation que la compréhension s'échappe. Consultez le [glossaire](../GLOSSARY.md) pour tout terme qui vous a paru glissant.

Si c'est la leçon elle-même qui n'est pas claire plutôt que la matière, c'est un défaut : [ouvrez une issue](https://github.com/TokenCemetery/teach/issues).
