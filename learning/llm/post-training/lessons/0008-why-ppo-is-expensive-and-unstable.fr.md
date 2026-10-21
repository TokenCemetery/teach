---
title: "8. Pourquoi PPO est coûteux et instable"
description: "Quatre modèles, et non un seul, doivent tenir en mémoire en même temps, et les deux qui passent le plus mal à l'échelle sont précisément ceux que RLHF ajoute"
type: lesson
---

# Leçon 8. Pourquoi PPO est coûteux et instable

**Lien avec la mission :** Dériver l'objectif RLHF et son mécanisme de clipping (leçons 6 et 7) explique ce que PPO optimise ; cette leçon explique ce qu'il coûte réellement à exécuter, ce qui rend DPO (étape 5) digne d'être envisagé comme alternative.
**Source primaire :** [Article : "Training language models to follow instructions with human feedback", Ouyang et al., 2022](https://arxiv.org/abs/2203.02155)
**Prérequis :** [Leçon 7](0007-ppo-why-the-update-gets-clipped.md)

## Échauffement

1. ▢ Pourquoi PPO clippe-t-il le rapport de probabilités entre la nouvelle et l'ancienne policy, plutôt que de laisser l'objectif de substitution croître sans borne ?

<details markdown="1"><summary>Vérifier</summary>

Parce qu'un grand avantage estimé issu d'un batch échantillonné n'est pas une preuve fiable qu'une mise à jour de policy tout aussi grande est sûre ; le clipping borne la distance dont une seule mise à jour peut déplacer la policy en réponse, ce qui empêche un pas destructivement grand.

</details>

2. ▢ Quelle différence d'échelle y a-t-il entre la pénalité KL (leçon 6) et le clipping par pas de PPO (leçon 7) ?

<details markdown="1"><summary>Vérifier</summary>

La pénalité KL limite la distance dont la policy dérive du modèle de référence SFT figé sur tout le run d'entraînement. Le clipping limite la taille de chaque pas d'optimisation par rapport à l'état de la policy elle-même juste avant ce pas. Aucun ne remplace l'autre.

</details>

## À savoir

### Quatre modèles, pas un

RLHF via PPO n'est pas un seul modèle qu'on entraîne ; il exige la présence simultanée de plusieurs modèles, chacun faisant un travail différent : la **policy** entraînée (initialisée à partir du modèle SFT) ; une copie figée du **modèle SFT** lui-même, gardée uniquement pour calculer la pénalité KL (leçon 6) ; le **reward model** (leçon 4), qui note les sorties échantillonnées de la policy ; et une **value function**, utilisée pour produire les estimations d'avantage dont dépend l'objectif clippé de PPO (leçon 7). Ouyang et al. indiquent directement que leur value function est initialisée à partir du reward model, ce qui en fait une cinquième copie complète des paramètres d'un grand modèle, distincte du reward model lui-même malgré son point de départ commun. Quatre à cinq grands modèles qui occupent la mémoire et consomment du calcul simultanément, au lieu d'un seul, c'est un coût réel et structurel, sans rapport avec le bon ou le mauvais déroulement de l'entraînement.

### D'où vient précisément l'instabilité

Ouyang et al. donnent un récit concret de l'endroit où l'échelle interagit mal avec ce montage. Ils ont constaté qu'un reward model de 175 milliards de paramètres pouvait atteindre une loss de validation plus faible qu'un plus petit, mais à deux coûts : son entraînement était plus instable, ce qui en faisait un moins bon choix pour initialiser une value function PPO, et utiliser ensemble un reward model et une value function de 175 milliards de paramètres augmentait sensiblement les besoins de calcul de PPO, en plus du coût propre de la policy. Leur résolution a été pratique plutôt que théorique : ils ont trouvé qu'un reward model de 6 milliards de paramètres était stable sur une large plage de learning rates et tout aussi efficace pour entraîner de bons modèles PPO, et ont utilisé ce seul reward model de 6B pour toutes les tailles de policy qu'ils ont entraînées, y compris leur policy de 175B.

### Pourquoi ce compromis précis vaut d'être retenu

C'est un résultat réellement contre-intuitif qui mérite d'être retenu : un reward model plus petit n'était pas un compromis imposé par un manque de ressources, c'était le choix le plus fiable à l'échelle testée par Ouyang et al. L'entraînement d'un reward model et d'une value function, à très grande échelle, n'hérite pas automatiquement du comportement d'échelle plus lisse et plus prévisible que montre une loss de pré-entraînement simple (les lois d'échelle de l'étape 3, d'un autre parcours). L'instabilité à l'échelle n'est pas qu'un inconvénient à contourner ; elle a directement façonné ce qu'Ouyang et al. ont réellement construit, et c'est une vraie raison pour laquelle le montage complet à quatre ou cinq modèles de PPO, exécuté à la plus grande échelle possible partout, est coûteux à tenter et peu fiable une fois tenté.

## Pratique

1. ▢ Nommez les quatre modèles (ou cinq, si l'on compte la value function séparément du reward model dont elle est initialisée) impliqués dans un pas d'entraînement PPO pour RLHF, et à quoi sert chacun.

<details markdown="1"><summary>Vérifier</summary>

La policy entraînée ; un modèle SFT figé, utilisé pour calculer la pénalité KL ; le reward model, qui note les sorties de la policy ; et la value function (initialisée à partir du reward model mais entraînée séparément), qui produit les estimations d'avantage dont l'objectif clippé de PPO a besoin.

</details>

2. ▢ D'après Ouyang et al., quels deux coûts accompagnaient l'utilisation d'un reward model et d'une value function de 175B, bien qu'il ait atteint une loss de validation plus faible qu'un plus petit ?

<details markdown="1"><summary>Vérifier</summary>

Son entraînement était plus instable, ce qui en faisait un moins bon choix pour initialiser une value function PPO, et son utilisation augmentait sensiblement les besoins de calcul de PPO, en plus du coût de la policy elle-même.

</details>

3. ▢ Une équipe suppose qu'un reward model plus grand et plus précis est toujours le meilleur choix pour RLHF, puisqu'il atteint une loss de validation plus faible. D'après la propre constatation d'Ouyang et al., cette hypothèse est-elle sûre ?

    - a) Oui, un reward model à plus faible loss est toujours le meilleur choix quelle que soit l'échelle
    - b) Non ; un reward model de 175B avait un entraînement plus instable et un coût de calcul plus élevé, et un reward model de 6B plus petit était stable et tout aussi efficace pour entraîner de bons modèles PPO
    - c) Non, car les reward models plus grands ne peuvent pas du tout être utilisés avec PPO
    - d) Oui, mais seulement parce qu'Ouyang et al. n'ont jamais réellement testé de reward model de 175B

<details markdown="1"><summary>Vérifier</summary>

**b)** est exactement la constatation d'Ouyang et al. : une loss de validation plus faible ne s'est pas traduite en meilleur choix pratique une fois pris en compte la stabilité de l'entraînement et le coût de calcul. (a) ignore leur propre compromis rapporté. (c) exagère la constatation ; le problème était la stabilité et le coût, pas une incompatibilité. (d) est factuellement faux ; ils rapportent explicitement avoir testé et écarté l'option 175B pour ces raisons.

</details>

## Exercices en situation réelle

- [ ] Trouvez un rapport technique ou un billet de blog décrivant un montage d'entraînement RLHF réel, et regardez s'il indique les tailles relatives de sa policy, de son reward model et de sa value function. Notez si le reward model a la taille de la policy ou s'il est délibérément plus petit.
- [ ] Lisez la section de l'annexe C d'Ouyang et al. sur l'entraînement du reward model (liée plus haut) et écrivez une phrase sur ce à quoi ils ont trouvé l'entraînement sensible, par opposition à ce à quoi il n'était pas très sensible.
- [ ] Demain : sans regarder la suite, écrivez une prédiction d'une phrase pour l'étape 5 : sachant que PPO a besoin d'un reward model, d'une value function et d'une boucle de RL en plus de la policy elle-même, que devrait faire différemment, en pratique, une méthode qui produit un résultat similaire sans reward model séparé ni boucle de RL ?

## Pour aller plus loin

- [Article : "Training language models to follow instructions with human feedback", Ouyang et al., 2022](https://arxiv.org/abs/2203.02155)
- [Ressources](../RESOURCES.md)

---

L'étape 4 a couvert ce que RLHF-PPO optimise et ce qu'il coûte à exécuter. L'étape 5 couvre une alternative conçue précisément pour avoir besoin de moins des deux : pas de reward model séparé, et aucune boucle de RL.

Ça ne passe pas ? Relisez la source primaire en haut de page, car cette leçon la condense et c'est dans la condensation que la compréhension s'échappe. Consultez le [glossaire](../GLOSSARY.md) pour tout terme qui vous a paru glissant.

Si c'est la leçon elle-même qui n'est pas claire plutôt que la matière, c'est un défaut : [ouvrez une issue](https://github.com/TokenCemetery/teach/issues).
