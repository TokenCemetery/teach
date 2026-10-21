---
title: "23. Défendre un budget de calcul"
description: "Un plan de pré-entraînement est un pari composé de nombreuses décisions distinctes, et le défendre revient à défendre chacune selon ses propres termes"
type: lesson
---

# Leçon 23. Défendre un budget de calcul

**Lien avec la mission :** « Décider si une tâche donnée appelle un pré-entraînement, un pré-entraînement continu ou le fine-tuning d'un modèle de base existant, et défendre ce choix sur le coût » est le point d'Objectif que clôt l'étape 10. La leçon 22 a couvert les cas où le pré-entraînement est le mauvais choix ; cette leçon couvre la défense du plan une fois qu'il est réellement le bon.
**Source primaire :** [Article : "Training Compute-Optimal Large Language Models", Hoffmann et al., 2022](https://arxiv.org/abs/2203.15556)
**Prérequis :** [Leçon 22](0022-pretraining-is-usually-the-wrong-default.md)

## Échauffement

1. ▢ D'après Gururangan et al., le pré-entraînement adaptatif au domaine aide-t-il plus, moins ou à peu près autant, selon que le domaine cible était déjà proche ou non des données d'entraînement d'origine du modèle de base ?

<details markdown="1"><summary>Vérifier</summary>

Il aide davantage précisément quand le domaine cible n'était pas déjà bien représenté dans le pré-entraînement d'origine du modèle de base ; les cibles déjà proches du domaine en profitent moins, puisque le modèle de base les couvre déjà raisonnablement bien.

</details>

2. ▢ Nommez une raison légitime de pré-entraîner à partir de zéro plutôt que d'adapter un modèle existant, d'après la leçon 22.

<details markdown="1"><summary>Vérifier</summary>

N'importe laquelle : la langue ou le domaine cible est si éloigné des données d'entraînement et du tokenizer de tout modèle de base disponible que l'adaptation ne peut pas combler l'écart, une exigence de licence ou de provenance écarte tous les modèles de base disponibles, ou un changement d'architecture délibéré dans lequel un checkpoint existant ne peut pas être adapté.

</details>

## À savoir

### Un plan de pré-entraînement n'est pas un seul nombre

Une fois que le pré-entraînement est réellement le bon choix, le défendre devant quelqu'un qui contrôle le budget revient à défendre plus qu'un seul chiffre de coût total. Chaque étape antérieure de ce parcours a produit une pièce de ce plan, et chaque pièce est une affirmation qui peut être vérifiée, et contestée, selon ses propres termes :

- **Le ratio tokens par paramètre (étape 3).** Le nombre de paramètres et le nombre de tokens prévus sont-ils proches de la plage d'environ 20 à 25 tokens par paramètre de Hoffmann et al. pour le budget de calcul choisi, ou penchent-ils vers l'allocation de Kaplan et al., lourde en paramètres et comparativement légère en données ? Un plan qui s'écarte de la plage compute-optimal a besoin d'une raison énoncée, pas du silence.
- **Le pipeline de données (étapes 1 et 2).** Le nombre de tokens est-il atteignable à partir d'un corpus qui a réellement été sourcé, dédupliqué et filtré sur la qualité, ou suppose-t-il des données qui n'existent pas encore à l'échelle et à la qualité requises ?
- **Le plan de parallélisme (étapes 4 à 6).** Le nombre d'appareils du plan, sa stratégie de partitionnement et tout découpage en parallélisme tensoriel ou de pipeline correspondent-ils à l'interconnexion réelle du matériel, d'après le raisonnement de la leçon 14, ou supposent-ils des schémas de communication que le matériel ne peut pas supporter efficacement ?
- **Le plan de stabilité et de surveillance (étapes 7 à 9).** Le plan dit-il quelle précision, quel clipping et quel schéma seront utilisés, et inclut-il un checkpointing assez fréquent, et une surveillance assez poussée, pour les taux de panne que la preuve de l'étape 8 a montrés normaux à cette échelle, et non exceptionnels ?

### Pourquoi les regrouper en un seul nombre invite la mauvaise question

Un budget présenté seulement comme un coût total unique invite exactement une question en retour : peut-on le rendre moins cher. Un budget présenté comme les affirmations précises ci-dessus invite un ensemble de questions plus utile : ce ratio tokens par paramètre est-il réellement compute-optimal pour l'objectif énoncé, les données existent-elles pour le soutenir, le plan de parallélisme correspond-il au matériel, et le run est-il protégé contre le taux de panne auquel un run de cette durée doit s'attendre. Défendre chaque affirmation séparément est aussi ce qui permet de dire honnêtement où le plan est incertain (une source de données non éprouvée, une hypothèse d'interconnexion non vérifiée) plutôt que de présenter une confiance uniforme sur un plan qui n'en a pas.

### Ce que « défendable » ne veut pas dire

Défendre un budget de calcul ne veut pas dire garantir que le run d'entraînement réussira du premier coup, ni qu'un comité de relecture doive l'approuver. Cela veut dire que chaque nombre important du plan remonte à une raison énoncée, fondée sur la matière que ce parcours a couverte, si bien qu'une contestation de l'un d'eux (« pourquoi ce ratio », « pourquoi ce découpage de parallélisme », « pourquoi cet intervalle de checkpoint ») a une réponse autre que « c'est ce que nous faisons toujours ».

## Pratique

1. ▢ Un plan de pré-entraînement proposé entraîne un modèle de 30 milliards de paramètres sur 200 milliards de tokens. En utilisant la plage d'environ 20 à 25 tokens par paramètre de l'étape 3, le ratio de ce plan est-il dans cette plage ou en dehors, et quelle question de suivi cela soulève-t-il ?

<details markdown="1"><summary>Indice</summary>

Divisez le nombre de tokens par le nombre de paramètres et comparez à la plage.

</details>

<details markdown="1"><summary>Vérifier</summary>

Environ 6,7 tokens par paramètre (`200 / 30`), bien en dessous de la plage d'environ 20 à 25. Cela soulève la question de suivi de savoir pourquoi le plan est entraîné sur comparativement peu de données relativement à sa taille, le même schéma de sous-entraînement que la leçon 6 a diagnostiqué chez GPT-3, et si cet écart par rapport à la plage compute-optimal est délibéré et justifié ou simplement non examiné.

</details>

2. ▢ Une équipe présente un budget de pré-entraînement sous la forme d'un seul chiffre en dollars total, sans autre décomposition. D'après cette leçon, quel est le principal problème de cette présentation ?

    - a) Un seul nombre est toujours inexact
    - b) Elle n'invite en retour que « peut-on le rendre moins cher », au lieu de faire apparaître quelles affirmations précises (ratio, données, parallélisme, plan de stabilité) sont réellement solides ou fragiles
    - c) Les relecteurs ne peuvent pas comprendre les chiffres en dollars
    - d) Il est illégal de présenter un budget ainsi

<details markdown="1"><summary>Vérifier</summary>

**b)** est le vrai problème que soulève cette leçon : regrouper chaque décision en un seul nombre cache quelles parties du plan sont bien étayées et lesquelles sont des hypothèses, et invite une conversation bien moins utile que ne le ferait la défense de chaque affirmation. (a), (c) et (d) ne sont pas le raisonnement que donne cette leçon.

</details>

3. ▢ Nommez les quatre catégories d'affirmations en lesquelles cette leçon dit qu'un plan de pré-entraînement défendable devrait être découpé.

<details markdown="1"><summary>Vérifier</summary>

Le ratio tokens par paramètre, le pipeline de données (sourcing, déduplication, filtrage de qualité), le plan de parallélisme adapté à l'interconnexion du matériel, et le plan de stabilité et de surveillance (précision, clipping, schéma, fréquence de checkpointing).

</details>

## Exercices en situation réelle

- [ ] Trouvez un rapport technique publié pour un modèle pré-entraîné ouvert et regardez combien des quatre catégories d'affirmations de cette leçon il énonce réellement explicitement (ratio, pipeline de données, plan de parallélisme, plan de stabilité et de surveillance). Notez celles qu'il laisse non énoncées.
- [ ] Pour un budget de calcul de votre choix, écrivez les quatre catégories sous forme d'un court plan à puces, une phrase de justification chacune, comme cette leçon soutient qu'un budget défendable devrait être présenté.
- [ ] Demain : choisissez l'une de vos quatre puces de l'exercice précédent et notez quelle preuve, issue de ce parcours ou d'ailleurs, vous avanceriez si quelqu'un contestait cette affirmation précise.

## Pour aller plus loin

- [Article : "Training Compute-Optimal Large Language Models", Hoffmann et al., 2022](https://arxiv.org/abs/2203.15556)
- [Ressources](../RESOURCES.md)

---

Ça ne passe pas ? Relisez la source primaire en haut de page, car cette leçon la condense et c'est dans la condensation que la compréhension s'échappe. Consultez le [glossaire](../GLOSSARY.md) pour tout terme qui vous a paru glissant.

Si c'est la leçon elle-même qui n'est pas claire plutôt que la matière, c'est un défaut : [ouvrez une issue](https://github.com/TokenCemetery/teach/issues).
