---
title: "11. GRPO : l'avantage relatif au groupe au lieu d'une value function"
description: "Échantillonnez plusieurs réponses à la même question, et laissez la dispersion des récompenses du groupe dire lesquelles étaient meilleures"
type: lesson
---

# Leçon 11. GRPO : l'avantage relatif au groupe au lieu d'une value function

**Lien avec la mission :** « Expliquer l'avantage relatif au groupe dans GRPO et pourquoi une récompense vérifiable (un test unitaire, une réponse mathématique vérifiée) change ce que l'entraînement par RL peut viser » est la cinquième puce sous « Objectif ». Cette leçon couvre l'avantage relatif au groupe lui-même ; la leçon 12 couvre les récompenses vérifiables, l'association qui rend GRPO particulièrement adapté aux maths et au code.
**Source primaire :** [Article : "DeepSeekMath: Pushing the Limits of Mathematical Reasoning in Open Language Models", Shao et al., 2024](https://arxiv.org/abs/2402.03300)
**Prérequis :** [Leçon 10](0010-the-dpo-loss-and-what-it-drops-relative-to-ppo.md)

## Échauffement

1. ▢ De quoi la loss de DPO a-t-elle besoin, en termes de modèles, que le montage de PPO n'exige pas ?

<details markdown="1"><summary>Vérifier</summary>

De rien de plus ; DPO a besoin strictement de moins de modèles que PPO. Il n'a besoin que de la policy et d'un modèle de référence figé, sans reward model séparé ni value function.

</details>

2. ▢ Supprimer le reward model séparé et la boucle de RL dans DPO supprime-t-il aussi le compromis de la pénalité KL entre rester proche du modèle de référence et aller vers ce que récompensent les données de préférence ?

<details markdown="1"><summary>Vérifier</summary>

Non. Le même compromis, piloté par le même `β`, est toujours présent ; il est simplement intégré directement au terme de récompense implicite au lieu d'être gardé comme une pénalité visuellement séparée.

</details>

## À savoir

### Le coût que la value function de PPO ajoute précisément

L'étape 4 (leçon 8) a déjà établi que PPO a besoin d'une value function en plus du reward model, initialisée à partir de lui, pour produire les estimations d'avantage dont dépend son objectif clippé. Shao et al. nomment exactement pourquoi cet élément précis est coûteux : la value function est typiquement un autre modèle de taille comparable à celle de la policy elle-même, ce qui ajoute un vrai coût de mémoire et de calcul à tout ce dont PPO a déjà besoin. Ils ajoutent un second problème propre aux modèles de langage : dans ce cadre, seul le tout dernier token d'une complétion reçoit en général un score de récompense, ce qui rend plus difficile qu'avec un retour de récompense à chaque pas l'entraînement d'une value function précise à chaque token antérieur de cette complétion.

### Le substitut de GRPO : laisser un groupe d'échantillons fournir sa propre baseline

**Group Relative Policy Optimization (GRPO)** supprime entièrement la value function, en la remplaçant par quelque chose qui n'exige aucun modèle supplémentaire : pour une question `q` donnée, GRPO échantillonne un **groupe** de `G` sorties, `{o_1, o_2, ..., o_G}`, toutes issues de la même (ancienne) policy. Un reward model note chacune des `G` sorties, ce qui donne `G` récompenses, `r_1` à `r_G`. Au lieu de demander à une value function entraînée séparément « cette sortie précise était-elle meilleure que prévu », GRPO pose une question plus simple, à laquelle le groupe lui-même peut répondre directement : cette sortie était-elle meilleure que les autres échantillonnées pour la même question. L'**avantage relatif au groupe** de la sortie `i` est la récompense normalisée par le groupe :

```text
A_i = (r_i - mean(r_1, ..., r_G)) / std(r_1, ..., r_G)
```

appliquée uniformément à chaque token de cette sortie. Une sortie qui a scoré au-dessus de la moyenne du groupe reçoit un avantage positif ; une sortie qui a scoré en dessous reçoit un avantage négatif ; la taille de l'avantage est mise à l'échelle par la dispersion des récompenses du groupe. Aucune value function n'est entraînée, et le coût de mémoire et de calcul que la leçon 8 lui attribuait disparaît avec elle.

### Pourquoi cela convient particulièrement bien aux reward models

Shao et al. font une remarque de plus qui mérite d'être retenue : cette comparaison relative au groupe n'est pas qu'un raccourci qui économise du coût, elle correspond à la forme des données sur lesquelles un reward model a été entraîné au départ. Un reward model de Bradley-Terry (leçon 4) est entraîné sur des comparaisons entre des sorties à la même question ; noter plusieurs sorties à la même question et les comparer entre elles, plutôt qu'à une baseline absolue apprise séparément, demande au reward model de faire le même type de jugement relatif que celui qu'il a réellement été entraîné à faire.

### Où se déplace la pénalité KL

GRPO change aussi l'endroit où se situe la pénalité KL, par rapport à l'objectif RLHF de la leçon 6. L'objectif d'Ouyang et al. ajoutait la pénalité KL directement dans la récompense par token, avant que les avantages en soient jamais calculés. Shao et al. ajoutent à la place la divergence KL entre la policy entraînée et la policy de référence comme terme séparé directement dans la loss, à côté de l'objectif de substitution clippé, au lieu de la mêler à la récompense dont l'avantage est calculé. Cela garde la partie du calcul fondée sur la récompense (et l'avantage relatif au groupe qui en est tiré) non compliquée par le terme KL, tout en appliquant le même type de retenue sur la distance dont la policy dérive de sa référence.

## Pratique

1. ▢ Un groupe de 4 sorties échantillonnées pour la même question reçoit les récompenses `{2, 4, 6, 8}` du reward model. Grosso modo, quelle(s) sortie(s) reçoivent un avantage relatif au groupe positif, et lesquelles un avantage négatif ?

<details markdown="1"><summary>Indice</summary>

Calculez d'abord la moyenne du groupe, puis demandez-vous quelles récompenses sont au-dessus et lesquelles en dessous.

</details>

<details markdown="1"><summary>Vérifier</summary>

La moyenne est 5. Les sorties qui ont scoré 6 et 8 sont au-dessus de la moyenne et reçoivent un avantage positif ; celles qui ont scoré 2 et 4 sont en dessous et reçoivent un avantage négatif.

</details>

2. ▢ D'après Shao et al., nommez deux problèmes précis de la value function de PPO que l'avantage relatif au groupe de GRPO évite.

<details markdown="1"><summary>Vérifier</summary>

La value function est typiquement un autre modèle de taille comparable à celle de la policy, ce qui ajoute un coût substantiel de mémoire et de calcul ; et dans le cadre des LLM, où seul le dernier token reçoit en général un score de récompense, entraîner une value function précise à chaque token antérieur est plus difficile que dans des cadres avec un retour de récompense à chaque pas.

</details>

3. ▢ Pourquoi Shao et al. décrivent-ils la comparaison relative au groupe comme particulièrement adaptée aux reward models, au-delà du simple fait d'être moins chère qu'une value function ?

<details markdown="1"><summary>Vérifier</summary>

Parce que les reward models sont typiquement entraînés dès le départ sur des comparaisons entre des sorties à la même question (la même forme que celle qu'utilise la loss de Bradley-Terry de la leçon 4) ; noter plusieurs sorties à une même question et les comparer entre elles demande au reward model de faire le même type de jugement relatif que celui qu'il a réellement été entraîné à faire.

</details>

4. ▢ Où se situe la pénalité KL de GRPO, par rapport à l'endroit où elle se situe dans l'objectif RLHF d'Ouyang et al. (leçon 6) ?

    - a) Au même endroit : ajoutée directement dans la récompense par token avant le calcul des avantages
    - b) GRPO n'a aucune pénalité KL
    - c) GRPO ajoute la divergence KL comme terme séparé directement dans la loss, à côté de l'objectif clippé, au lieu de la mêler à la récompense
    - d) GRPO remplace la pénalité KL par un second reward model

<details markdown="1"><summary>Vérifier</summary>

**c)** est l'emplacement réel que décrivent Shao et al. (a) décrit l'approche d'Ouyang et al., que GRPO change précisément. (b) et (d) énoncent tous deux de travers ce que fait GRPO ; le même type de retenue est toujours présent, simplement déplacé.

</details>

## Exercices en situation réelle

- [ ] Trouvez une implémentation de GRPO dans une bibliothèque à laquelle vous avez accès, et vérifiez comment elle calcule l'avantage normalisé par le groupe : correspond-elle à la formule moyenne et écart-type que donne cette leçon ?
- [ ] Lisez le paragraphe de l'article DeepSeekMath (lié plus haut) qui décrit pourquoi la value function est coûteuse dans le cadre des LLM en particulier, et écrivez une phrase distinguant l'argument du coût mémoire de l'argument de la précision par token.
- [ ] Demain : sans regarder la suite, écrivez une prédiction d'une phrase pour la leçon 12 : si un reward model peut être remplacé par tout ce qui produit un score fiable pour chaque sortie échantillonnée, quel type de tâche permettrait que ce score vienne d'un vérificateur déterministe plutôt que d'un modèle entraîné ?

## Pour aller plus loin

- [Article : "DeepSeekMath: Pushing the Limits of Mathematical Reasoning in Open Language Models", Shao et al., 2024](https://arxiv.org/abs/2402.03300)
- [Ressources](../RESOURCES.md)

---

Ça ne passe pas ? Relisez la source primaire en haut de page, car cette leçon la condense et c'est dans la condensation que la compréhension s'échappe. Consultez le [glossaire](../GLOSSARY.md) pour tout terme qui vous a paru glissant.

Si c'est la leçon elle-même qui n'est pas claire plutôt que la matière, c'est un défaut : [ouvrez une issue](https://github.com/TokenCemetery/teach/issues).
