---
title: "5. KL directe et KL inverse"
description: "Pourquoi la KL directe étale l'élève sur tous les modes de l'enseignant et la KL inverse l'oblige à s'engager sur un seul"
type: lesson
---

# Leçon 5. KL directe et KL inverse

**Lien avec la mission :** La mission vous demande de choisir entre KL directe et KL inverse, et cette leçon donne les deux directions, le cas jouet qui les sépare, et les articles qui divergent sur celle à utiliser.
**Source primaire :** [Article : "MiniLLM: On-Policy Distillation of Large Language Models", Gu et al., 2023](https://arxiv.org/abs/2306.08543)
**Prérequis :** [Leçon 4](0004-token-level-distillation.md), [KL directe](../GLOSSARY.md), [KL inverse](../GLOSSARY.md), [Divergence KL](../GLOSSARY.md)

## Échauffement

1. ▢ Dans `token_kd_loss`, sur quel axe la divergence est-elle prise, et que fait le masque à la moyenne finale ?

<details markdown="1"><summary>Vérifier</summary>

La divergence est prise sur l'axe du vocabulaire, le dernier, ce qui donne un nombre par position. Le masque met à zéro les positions de padding et la division finale par la somme du masque moyenne sur les vrais tokens seulement.

</details>

2. ▢ Dans la leçon 2, une probabilité de 10^-6 de l'enseignant sur une mauvaise classe bougeait à peine une loss d'entropie croisée. Quel facteur du terme le rend petit ?

<details markdown="1"><summary>Vérifier</summary>

Le terme est la probabilité de l'enseignant multipliée par un log de rapport, si bien qu'une cible de 10^-6 le réduit d'un millionième. Gardez cela en tête : la direction de la KL décide de la probabilité de qui fait la mise à l'échelle.

</details>

## À savoir

### Deux directions d'une même divergence

La divergence KL n'est pas symétrique. Avec p l'enseignant et q l'élève, la [KL directe](../GLOSSARY.md) est KL(p || q), la somme sur les tokens de p log(p / q). La [KL inverse](../GLOSSARY.md) est KL(q || p), la somme de q log(q / p). La seule différence est de savoir la probabilité de qui multiplie le log de rapport, et cela décide de ce que chacune punit. GKD (Agarwal et al., 2023, section 2) utilise ces mêmes noms.

La KL directe pondère chaque token par la probabilité de l'enseignant. Un token que l'enseignant aime et auquel l'élève donne presque aucune probabilité coûte cher, parce que le rapport p / q est énorme. Un token auquel l'enseignant ne donne presque rien et que l'élève aime coûte peu, puisque p est petit. L'élève est poussé à mettre de la masse partout où l'enseignant en a, ce qui est la couverture des modes.

La KL inverse pondère chaque token par la probabilité de l'élève. L'élève est puni s'il met de la masse là où l'enseignant n'en a presque pas, parce que q log(q / p) est grand à cet endroit. Ignorer un mode de l'enseignant ne coûte rien, donc l'élève est libre d'en prendre un. C'est la recherche de mode.

### Deux modes, deux élèves

L'enseignant ci-dessous a deux suites également probables et un peu de probabilité sur deux autres. Le premier élève étale sa masse. Le second s'engage sur un seul mode.

```python
import numpy as np

p = np.array([0.49, 0.01, 0.01, 0.49])        # teacher: two modes
students = {
    "spread": np.array([0.25, 0.25, 0.25, 0.25]),
    "commit": np.array([0.97, 0.01, 0.01, 0.01]),
}

def kl(a, b):
    return float(np.sum(a * np.log(a / b)))

for name, q in students.items():
    print(name, "forward %.3f" % kl(p, q), "reverse %.3f" % kl(q, p))
```

Prédisez quel élève chaque direction préfère, puis exécutez. La sortie avec NumPy 2.5 :

```text
spread forward 0.595 reverse 1.273
commit forward 1.572 reverse 0.623
```

La KL directe préfère l'élève étalé (0.595 contre 1.572), qui met de la probabilité sur les deux modes et en gaspille un peu sur les deux tokens rares. La KL inverse préfère l'élève engagé (0.623 contre 1.273), qui se place sur un mode et ignore l'autre. Aucun des deux élèves n'égale l'enseignant. L'échec que vous voulez dépend de ce que l'élève fera ensuite, ce qui est l'argument des deux articles suivants.

### Le plaidoyer pour la KL inverse

Gu et al. soutiennent que les objectifs de distillation standard minimisent une KL directe approchée, ce qui force l'élève à couvrir tous les modes de l'enseignant. Pour la classification, avec un nombre fini de classes, les deux distributions ont peu de modes et cela fonctionne bien. Pour la génération ouverte, l'enseignant peut avoir bien plus de modes qu'un petit élève ne peut en exprimer. L'article dit que la KL directe pousse alors l'élève à attribuer une probabilité déraisonnablement élevée aux régions où l'enseignant n'en a presque pas, et produit des échantillons très improbables sous l'enseignant pendant la génération libre (introduction). Leur remède est la KL inverse, qui cherche les modes principaux et donne une faible probabilité aux régions vides de l'enseignant. Dans le texte, disent-ils, l'élève évite d'apprendre trop de variantes de longue traîne de la distribution de l'enseignant et se concentre sur la justesse.

Ils montrent l'effet sur un jouet : un mélange de gaussiennes ajusté avec une seule gaussienne par chaque divergence (figure 2). Ils optimisent la KL inverse avec un gradient de politique sur des échantillons de l'élève, avec des étapes supplémentaires pour la stabilité, ce qui en fait une méthode on-policy. La leçon 15 la traite. La loss elle-même est simple. Avec les log-probabilités du fragment précédent, la KL inverse par position est `(s.exp() * (s - t)).sum(dim=-1)` à la place de la ligne de la KL directe.

### Le plaidoyer pour choisir

GKD ne choisit pas de camp. Il fait de la divergence un paramètre. Sa JSD généralisée, pour un coefficient beta entre 0 et 1, est :

```text
JSD(beta)(P || Q) = beta * KL(P || beta*P + (1-beta)*Q) + (1-beta) * KL(Q || beta*P + (1-beta)*Q)
```

Avec P l'enseignant, elle interpole entre les deux directions. Les gradients se comportent comme la KL directe quand beta tend vers 0 et comme la KL inverse quand beta tend vers 1. Elle est aussi bornée même quand les supports sont disjoints, ce que la KL n'est pas (section 2). Sur le même jouet, avec la fonction `jsd` écrite à partir de cette formule (qui n'est pas dans l'article), les trois valeurs de JSD donnent un croisement :

| Élève | JSD(0.1) | JSD(0.5) | JSD(0.9) |
|---|---|---|---|
| étalé | 0.055 | 0.177 | 0.091 |
| engagé | 0.102 | 0.189 | 0.058 |

À beta = 0.1 l'élève étalé gagne et à beta = 0.9 c'est l'élève engagé, ce qui correspond à la direction que chaque extrémité est censée préférer. À 0.5, ils sont proches. Les nombres viennent du jouet, pas d'un run.

Les expériences de GKD disent que la meilleure divergence dépend de la tâche. Sur le résumé XSum, passer de la KL directe à la KL inverse à travers la famille JSD a réduit la diversité de la sortie (figure 4). Dans les ablations, les divergences qui cherchent un mode ont fait mieux évaluées avec un échantillonnage à température, et le choix comptait peu avec un décodage glouton (section 4.1). Sur l'instruction tuning indépendant de la tâche avec FLAN, GKD on-policy avec KL inverse a nettement surpassé le KD supervisé et ImitKD, et la KL inverse a fait bien mieux que la KL directe (figure 10). Sur GSM8K, la KL directe a plutôt bien fonctionné, et la KL inverse aussi, surtout en entraînant sur un jeu de données fixe seulement. Le résumé de l'article est que la divergence doit être choisie selon le compromis diversité-qualité sur la tâche.

L'implémentation TRL expose ce choix sous le nom `beta` dans `GKDConfig` : à 0.0 la loss est la divergence KL, à 1.0 la KL inverse, avec 0.5 par défaut ([documentation de GKD](https://huggingface.co/docs/trl/main/en/gkd_trainer), lue pour cette leçon).

### Des preuves dans l'autre sens

Les auteurs de Minitron ré-entraînent des base models élagués à partir de leur enseignant non élagué et ont testé directement les directions. Sur un Minitron 8B élagué en profondeur, la loss sur les logits avec KLD directe a atteint une loss LM de 2.155 contre 2.665 pour la KLD inverse (leur tableau 16, annexe A.3). Sur la génération précédente, Nemotron-3 8B, la loss combinée a donné 2.117 avec la KLD directe et 2.140 avec l'inverse (tableau 15). Ils notent que des travaux antérieurs ont trouvé la KLD inverse mieux adaptée au fine-tuning supervisé et au suivi d'instructions, qu'Agarwal et al. disent que le choix dépend de la tâche, et que la KLD directe est le meilleur choix pour leur cadre de base model (section 4).

Les preuves ne forment donc pas une règle unique. La KL inverse s'appuie sur les résultats d'instruction tuning sur de petits élèves dans GKD, et la KL directe s'appuie sur le ré-entraînement de base models dans Minitron. Les deux sont des articles isolés sur leurs propres modèles.

## Pratique

1. ▢ Dans le run à deux modes, quel élève la KL directe préfère-t-elle, et lequel la KL inverse préfère-t-elle ?

<details markdown="1"><summary>Indice</summary>

Demandez-vous quel élève a mis de la probabilité sur les deux gros tokens de l'enseignant, et lequel en ignore un.

</details>

<details markdown="1"><summary>Vérifier</summary>

La KL directe préfère l'élève étalé (0.595 contre 1.572) et la KL inverse l'élève engagé (0.623 contre 1.273). La KL directe punit l'élève engagé pour un q proche de 0.01 là où p vaut 0.49. La KL inverse punit l'élève étalé pour avoir mis 0.25 là où p vaut 0.01.

</details>

2. ▢ Quel est l'argument de l'article contre la KL directe pour la génération ouverte ?

    - a) La loss ne peut pas être calculée à partir de la distribution complète
    - b) L'élève doit couvrir plus de modes qu'il ne peut en exprimer
    - c) Le gradient s'annule toujours quand l'enseignant est très confiant
    - d) Les logits de l'enseignant doivent être adoucis pour que cela fonctionne

<details markdown="1"><summary>Vérifier</summary>

**b)** Un enseignant sur du texte a bien plus de modes qu'un petit élève ne peut en exprimer, et la KL directe force l'élève à les couvrir, si bien qu'il met de la masse sur des régions que l'enseignant considère comme vides. Ce n'est pas (a) : les deux directions peuvent se calculer à partir des distributions complètes. Ce n'est pas (c) : c'est l'observation de la leçon 2 sur les petites probabilités, un autre problème. Ce n'est pas (d) : la température est un choix distinct de la direction.

</details>

3. ▢ D'après le tableau JSD, quel élève JSD(0.9) préfère-t-elle, et cela correspond-il à l'affirmation de GKD selon laquelle beta proche de 1 se comporte comme la KL inverse ?

<details markdown="1"><summary>Vérifier</summary>

L'élève engagé (0.058 contre 0.091), et oui : la KL inverse le préfère aussi. À beta = 0.1 l'élève étalé gagne, comme le ferait la KL directe. Le tableau est un contrôle jouet de la description de l'article, pas un résultat d'un run d'entraînement.

</details>

4. ▢ Le tableau 16 de Minitron donne une loss LM de 2.155 avec la KLD directe et de 2.665 avec la KLD inverse pour un élève 8B élagué en profondeur. Est-ce que cela contredit MiniLLM et GKD ?

<details markdown="1"><summary>Vérifier</summary>

Non, pas directement. MiniLLM et GKD rapportent des résultats de suivi d'instructions et de résumé sur de petits élèves, avec la direction inverse souvent sur des séquences échantillonnées par l'élève. Minitron ré-entraîne un base model élagué sur un mélange de style pré-entraînement et mesure la loss LM. Le cadre diffère par la tâche, le point de départ de l'élève et la métrique, donc les preuves soutiennent un choix qui dépend de la tâche, comme le dit GKD. Testez les deux sur votre propre tâche avant de vous engager.

</details>

5. ▢ Quelle divergence est sourde à une minuscule probabilité de l'enseignant, comme dans la leçon 2, et laquelle punit l'élève pour la masse placée à cet endroit ?

<details markdown="1"><summary>Vérifier</summary>

La KL directe est presque sourde à une minuscule probabilité de l'enseignant parce que p multiplie le log de rapport, ce qui est le problème de la leçon 2. La KL inverse punit la masse de l'élève placée là où l'enseignant n'en a presque pas, parce que q multiplie le log de rapport. Les deux directions répondent à des questions opposées sur le même petit nombre.

</details>

## Exercices en situation réelle

- [ ] Exécutez le fragment, puis changez l'enseignant en `[0.45, 0.05, 0.05, 0.45]` et regardez si les préférences des deux directions changent.
- [ ] Ouvrez l'annexe A.7 de l'article GKD et lisez la légende de la figure sur la KL qui cherche un mode contre celle qui couvre les modes. Écrivez une phrase sur ce que fait l'élève unimodal sous chaque direction.
- [ ] Demain : sans notes, dites quelle direction recommandent MiniLLM, GKD et Minitron, et pour quel cadre.

## Pour aller plus loin

- [Loss de distillation](../reference/distillation-losses.md)
- [Article : "MiniLLM: On-Policy Distillation of Large Language Models", Gu et al., 2023](https://arxiv.org/abs/2306.08543)
- [Article : "On-Policy Distillation of Language Models: Learning from Self-Generated Mistakes", Agarwal et al., 2023](https://arxiv.org/abs/2306.13649)
- [Doc : "Generalized Knowledge Distillation Trainer", Hugging Face TRL](https://huggingface.co/docs/trl/main/en/gkd_trainer)
- [Article : "Compact Language Models via Pruning and Knowledge Distillation", Muralidharan et al., 2024](https://arxiv.org/abs/2407.14679)
- [Ressources](../RESOURCES.md)

---

Ça ne passe pas ? Relisez la source primaire en haut de page, car cette leçon la condense et c'est dans la condensation que la compréhension s'échappe. Consultez le [glossaire](../GLOSSARY.md) pour tout terme qui vous a paru glissant.

Si c'est la leçon elle-même qui n'est pas claire plutôt que la matière, c'est un défaut : [ouvrez une issue](https://github.com/TokenCemetery/teach/issues).
