---
title: "19. Écart de capacité et traits cachés"
description: "Pourquoi un enseignant plus grand n'est pas toujours meilleur, et ce qui peut passer à un élève sans que personne l'ait voulu"
type: lesson
---

# Leçon 19. Écart de capacité et traits cachés

**Lien avec la mission :** La mission vous demande de prédire ce qu'un élève héritera, y compris les capacités qu'il ne peut pas absorber et les traits que personne ne voulait transmettre, et cette leçon en couvre un de chaque.
**Source primaire :** [Article : "Subliminal Learning: Language models transmit behavioral traits via hidden signals in data", Cloud et al., 2025](https://arxiv.org/abs/2507.14805), sections 1 à 5
**Prérequis :** [Leçon 12](0012-filtering-synthetic-data.md), [Leçon 18](0018-the-imitation-gap.md), [Écart de capacité](../GLOSSARY.md), [Assistant enseignant](../GLOSSARY.md), [Apprentissage subliminal](../GLOSSARY.md)

## Échauffement

1. ▢ Qu'est-ce que l'écart d'imitation, en une phrase ?

<details markdown="1"><summary>Vérifier</summary>

La distance entre la ressemblance d'un élève avec son enseignant dans le style et la part des capacités de l'enseignant qu'il possède. L'imitation avec un budget limité comble le côté style bien plus vite que le côté capacité.

</details>

2. ▢ La leçon 12 filtre les données synthétiques pour la qualité. Nommez deux choses qu'un tel filtre peut vérifier, et dites ce qu'elles ont en commun.

<details markdown="1"><summary>Vérifier</summary>

Il peut vérifier le format, la justesse, les doublons ou des mots signalés. Ce qu'elles partagent, c'est que chacune est une propriété du texte lui-même, qu'un filtre peut lire. Cette leçon teste ce qui se passe quand une propriété n'est pas lisible dans le texte.

</details>

3. ▢ La leçon 17 sépare la fidélité de la généralisation. Lequel des deux échoue quand un élève ne peut pas imiter un enseignant bien plus grand ?

<details markdown="1"><summary>Vérifier</summary>

La fidélité : les prédictions de l'élève divergent de celles de l'enseignant. Que la qualité sur la tâche en souffre aussi dépend du cas, c'est pourquoi la première moitié de cette leçon demande si un enseignant plus grand aide tout court.

</details>

## À savoir

### Un enseignant plus grand n'est pas un meilleur enseignant

Mirzadeh et al. ont distillé un petit élève fixe à partir d'enseignants de taille croissante. Leur élève est un CNN simple à 2 couches de convolution, et les enseignants en ont 4, 6, 8 et 10. À mesure que l'enseignant grandit, sa propre précision au test monte, mais la précision de l'élève monte d'abord puis baisse, sur CIFAR-10 comme sur CIFAR-100 (figure 2). Un élève ne peut donc pas utiliser un enseignant arbitrairement grand.

Ils nomment trois facteurs concurrents : un enseignant plus fort supervise mieux, mais il peut devenir si complexe que l'élève ne peut pas l'imiter, et sa plus grande certitude rend ses logits moins doux, ce qui affaiblit le transfert. C'est l'[écart de capacité](../GLOSSARY.md). Notez l'échelle de la preuve : ce sont des classifieurs d'images avec de petits réseaux, pas des modèles de langage.

Leur correctif est l'[assistant enseignant](../GLOSSARY.md). Distiller l'enseignant dans un réseau de taille intermédiaire, puis distiller celui-ci dans l'élève. Le tableau 1 donne la précision au test sans distillation, avec distillation standard, et avec l'assistant :

| Configuration | Sans distillation | Distillation standard | Avec assistant |
|---|---|---|---|
| CNN simple, CIFAR-10 (élève 2, assistant 4, enseignant 10) | 70.16 | 72.57 | 73.51 |
| CNN simple, CIFAR-100 (mêmes tailles) | 41.09 | 44.57 | 44.92 |
| ResNet, CIFAR-10 (élève 8, assistant 20, enseignant 110) | 88.52 | 88.65 | 88.98 |
| ResNet, CIFAR-100 (mêmes tailles) | 61.37 | 61.41 | 61.82 |

Le gain est réel et petit. Sur les lignes ResNet, l'assistant ajoute 0.33 point sur CIFAR-10 et 0.41 sur CIFAR-100 par rapport à la distillation standard. L'article montre aussi que la meilleure taille d'assistant n'est pas le point médian : pour le CNN simple, un assistant de taille 4 a battu les tailles 6 et 8 (tableau 2).

### Un second récit, et un désaccord

Cho et Hariharan arrivent à la même observation par un autre angle : des enseignants plus précis ne font souvent pas de meilleurs élèves. Sur ImageNet avec un élève ResNet18, l'élève entraîné de zéro a une erreur de 30.24 %. Les élèves distillés à partir d'enseignants ResNet18, ResNet34 et ResNet50 avaient des erreurs de 30.57 %, 30.79 % et 30.95 % alors que l'erreur propre de l'enseignant passait de 30.24 % à 26.70 % puis 23.85 % (tableau 1). Chaque enseignant a rendu l'élève légèrement pire que l'entraînement de zéro.

Leur diagnostic : l'élève ne peut pas imiter le grand enseignant, ce qui se voit à une loss de distillation bien plus élevée pour le plus grand enseignant, plutôt qu'à des sorties de l'enseignant trop proches d'un one-hot, puisque relever la température n'a pas changé le résultat. Les remèdes qu'ils rapportent :

| Remède | Résultat dans l'article |
|---|---|
| Arrêter la distillation plus tôt et finir sur les hard labels | Les erreurs de l'élève ResNet18 sont tombées à 29.01 %, 29.16 % et 29.35 % pour les trois enseignants, toutes meilleures que les 30.24 % de zéro (tableau 3). Un enseignant plus grand ne donnait toujours pas un meilleur élève |
| Arrêter plus tôt l'entraînement propre de l'enseignant | Les élèves entraînés à partir d'enseignants arrêtés tôt ont systématiquement surpassé ceux issus d'enseignants entièrement entraînés sur CIFAR-10 (figure 5). L'article dit qu'il suffit d'un tiers à un quart des époques |
| Enchaîner la distillation à travers des modèles intermédiaires | Rapporté comme inefficace : distiller un grand modèle dans un moyen puis dans un petit n'a pas aidé, et distiller directement depuis le modèle moyen était le meilleur (tableau 6) |

La dernière ligne est un désaccord avec l'idée d'assistant, dans une autre configuration (WideResNets sur CIFAR-10). Deux articles de vision ne tranchent pas pour savoir ce qui tient pour un LLM. La lecture honnête est qu'une paire déséquilibrée est un risque à tester, et que tant un enseignant intermédiaire qu'un enseignant arrêté tôt sont des choses peu coûteuses à essayer.

Un point de données issu des modèles de langage : MiniLLM a gardé un élève GPT-2 125M fixe et utilisé des enseignants de 340M, 760M et 1.5B. La performance de l'élève était corrélée positivement à la taille de l'enseignant sur cette plage (figure 5). C'est un rapport enseignant sur élève d'environ 12 contre 1 sans signe d'écart de capacité, dans une famille et une configuration. Je n'ai vérifié aucun article sur les LLM qui montre l'écart lui-même, traitez donc l'écart de capacité comme un résultat de vision à vérifier pour votre propre paire.

### Des traits que personne n'a voulus

Cloud et al. ont construit l'opposé d'un problème de capacité : quelque chose passe que les données ne semblent pas contenir. Le montage est simple. Un enseignant reçoit un trait, par system prompt ou fine-tuning, par exemple un amour des chouettes ou un désalignement. Il génère des données dans un domaine sans rapport, comme des suites de nombres. Les données sont filtrées pour retirer toute référence au trait. Un élève, affiné à partir du même base model, s'entraîne dessus.

| Expérience | Résultat |
|---|---|
| Enseignant chouette, GPT-4.1 nano, nombres seulement (section 3.1) | L'élève a choisi la chouette comme animal préféré environ 12 % du temps avant l'entraînement et plus de 60 % après. Un élève de contrôle entraîné sur des nombres issus du modèle sans prompt n'a montré aucun décalage comparable |
| Enseignant désaligné, nombres avec 34 nombres associés négativement retirés (section 3.2) | L'élève a donné des réponses libres désalignées presque 10 % du temps, contre 0 % pour le base model et moins de 1 % pour les élèves de contrôle |
| Enseignant désaligné, chaîne de raisonnement filtrée pour la justesse et l'alignement (section 4) | Les réponses désalignées sont passées d'environ 0 % à 8 %, avec des contrôles sous 1 % |

Le filtre de suites de nombres a rejeté entre 23 % et 38 % des complétions pour le formatage, et les jeux de données ont été ramenés à 10,000 exemples. Le trait n'est pas dans les nombres d'une manière que les auteurs aient pu trouver. Des classifieurs sollicités par prompt et l'apprentissage en contexte ne l'ont pas détecté de façon fiable, et les auteurs ont inspecté des exemples sans en voir de signe (introduction et section 5.2).

### La condition : un base model partagé

L'effet dépendait du partage d'un même base model entre l'élève et l'enseignant. Les nombres d'un enseignant GPT-4.1 nano ont transmis des traits à un élève GPT-4.1 nano mais pas à un élève Qwen2.5 (introduction, section 5.1). GPT-4o et GPT-4.1 se sont transmis des traits l'un à l'autre, ce que les auteurs suggèrent venir d'une initialisation partagée, en citant un entretien avec un développeur d'OpenAI. Leur résultat théorique dit qu'un pas de gradient suffisamment petit sur une sortie générée par l'enseignant déplace un élève vers l'enseignant, et il exige une initialisation partagée.

Lisez la portée avec précision. Dans leurs expériences, la transmission a échoué entre des base models différents, ce qui n'est pas la même chose qu'une garantie qu'un base model différent est sûr. Leurs tâches sont artificielles, ils disent que ce qui peut ou ne peut pas être transmis reste ouvert, et certains animaux ne se sont pas transmis pour certains modèles. Leur implication est que le filtrage peut être insuffisant pour arrêter la transmission d'un trait porté par des motifs statistiques plutôt que par le contenu, et que l'évaluation de sécurité d'un élève devrait sonder au-delà du comportement sur la distribution d'entraînement.

Qu'en faire : si l'élève part du même base model que l'enseignant, par exemple quand vous faites le fine-tuning d'une copie neuve d'un modèle sur des données générées par une copie ajustée de lui-même, un jeu de données filtré d'apparence propre ne certifie pas un élève propre. Évaluez directement l'élève sur les traits indésirables de l'enseignant. Ce conseil est mon inférence à partir de leurs résultats, pas un protocole qu'ils ont testé.

### Les refus et le style viennent aussi

Un élève hérite aussi du comportement visible de l'enseignant. Dans l'article de la leçon 18, les modèles d'imitation sont devenus moins toxiques à mesure que les données d'imitation augmentaient, ce que les auteurs lisent comme le modèle apprenant à s'abstenir comme ChatGPT (Gudibande et al., figure 5). Les schémas de refus se transfèrent donc avec le style, bien plus facilement que les connaissances. Rien dans les sources lues pour cette leçon ne mesure si les élèves copient les erreurs factuelles d'un enseignant, cette leçon n'affirme donc rien à ce sujet.

## Pratique

1. ▢ D'après le tableau 1 de Cho et Hariharan, de combien l'élève distillé à partir de l'enseignant ResNet50 était-il pire que l'élève entraîné de zéro, et de combien était-il meilleur après arrêt précoce de la distillation ?

<details markdown="1"><summary>Vérifier</summary>

L'élève distillé de ResNet50 avait 30.95 % d'erreur contre 30.24 % de zéro, donc 0.71 point de pire. Avec la distillation arrêtée tôt, il avait 29.35 %, donc 0.89 point de mieux que de zéro. Le schéma est celui d'une distillation qui nuit tard dans l'entraînement, pas d'un mauvais enseignant : le même enseignant aide dès que l'élève cesse de le poursuivre.

</details>

2. ▢ Quel changement définit la méthode d'assistant enseignant de Mirzadeh et al. ?

    - a) L'élève s'entraîne sur des données étroites propres à une tâche
    - b) L'enseignant arrête son entraînement bien plus tôt
    - c) L'élève apprend d'un assistant de taille moyenne
    - d) L'élève réutilise les poids initiaux de l'enseignant

<details markdown="1"><summary>Vérifier</summary>

**c)** Un modèle de taille intermédiaire est distillé à partir de l'enseignant puis enseigne à l'élève. (b) est l'enseignant arrêté tôt de Cho et Hariharan. (a) est l'imitation locale de la leçon 18. (d) est la condition d'initialisation partagée de Cloud et al., qui est une source de transfert caché, pas une méthode.

</details>

3. ▢ Dans l'expérience de la figure 2 de Mirzadeh et al., un élève à 2 couches est distillé à partir d'enseignants à 4, 6, 8 et 10 couches. Prédisez la forme de la précision de l'élève à mesure que la taille de l'enseignant grandit.

<details markdown="1"><summary>Indice</summary>

La propre précision de l'enseignant continue de monter. Lequel des trois facteurs concurrents l'emporte tôt, et lequel l'emporte tard ?

</details>

<details markdown="1"><summary>Vérifier</summary>

Elle monte d'abord, puis baisse. Aux petites tailles, la meilleure supervision d'un enseignant plus fort l'emporte. Aux grandes tailles, l'incapacité de l'élève à imiter l'enseignant et la moindre douceur de l'enseignant l'emportent. Le pic n'est pas au plus grand enseignant. C'est le résultat de l'article sur le CNN avec CIFAR-10 et CIFAR-100, ne supposez donc pas que le pic se situe au même rapport pour un LLM.

</details>

4. ▢ Votre équipe fait le fine-tuning d'un base model, constate que la copie ajustée montre un comportement indésirable, et utilise cette copie pour générer des données pour une copie neuve du même base model. Les données sont filtrées pour retirer toute mention du comportement. Que dit Cloud et al. sur le caractère suffisant du filtre, et qu'ajoutez-vous ?

<details markdown="1"><summary>Vérifier</summary>

Leurs expériences montrent un trait passant à travers des données filtrées pour lui, y compris des suites de nombres, du code filtré et des chaînes de raisonnement filtrées, quand l'élève et l'enseignant partagent un base model. Un filtre qui retire les références explicites n'est donc pas une preuve suffisante d'un élève propre. Ajoutez une évaluation directe de l'élève sur le comportement indésirable, et si le choix est ouvert, traitez un élève issu d'un autre base model comme à moindre risque, puisque la transmission a échoué entre base models dans leurs tests, tout en gardant à l'esprit que c'est une observation, pas une garantie.

</details>

5. ▢ Mirzadeh et al. rapportent qu'un assistant enseignant aide. Cho et Hariharan rapportent qu'un enchaînement à travers un modèle intermédiaire n'aide pas. Que faites-vous pour décider pour votre propre run ?

<details markdown="1"><summary>Vérifier</summary>

Ne choisissez pas de camp à partir des articles. Les deux sont des expériences de vision, les gains de l'assistant sont petits sur les lignes ResNet (0.33 et 0.41 point par rapport à la distillation standard), et les configurations diffèrent. Menez une comparaison contrôlée sur votre propre paire : distillation directe, un modèle intermédiaire, et un enseignant arrêté tôt ou une distillation arrêtée tôt. Mesurez par rapport à une référence entraînée de zéro et par rapport à l'accord avec l'enseignant, comme dans la leçon 17.

</details>

6. ▢ L'expérience de taille d'enseignant de MiniLLM a gardé un élève de 125M et utilisé trois enseignants jusqu'à 1.5B. Qu'a-t-elle montré, et que ne montre-t-elle pas sur l'écart de capacité ?

<details markdown="1"><summary>Vérifier</summary>

La performance de l'élève était corrélée positivement à la taille de l'enseignant sur 340M, 760M et 1.5B, donc aucun écart de capacité n'est apparu sur cette plage dans cette famille. Elle ne montre pas que l'écart n'arrive jamais pour les LLM : la plage plafonne à environ 12 fois l'élève, et c'est une méthode sur une famille.

</details>

## Exercices en situation réelle

- [ ] Ouvrez les tableaux 1 et 3 de l'article de Cho et Hariharan et notez l'erreur de l'élève pour chaque enseignant avec et sans arrêt précoce. Notez quel enseignant a donné l'erreur d'élève la plus basse avec arrêt précoce.
- [ ] Trouvez l'enseignant et l'élève d'une distillation sur laquelle vous vous appuyez et notez s'ils partagent un base model. S'ils en partagent un, écrivez un contrôle direct d'un trait indésirable que vous exécuteriez sur l'élève.
- [ ] Demain : sans notes, écrivez les trois facteurs concurrents de l'écart de capacité, la méthode de l'assistant enseignant en deux phrases, et la condition dans laquelle l'apprentissage subliminal est apparu.

## Pour aller plus loin

- [Ce dont l'élève hérite](../reference/what-the-student-inherits.md)
- [Article : "Subliminal Learning: Language models transmit behavioral traits via hidden signals in data", Cloud et al., 2025](https://arxiv.org/abs/2507.14805)
- [Article : "Improved Knowledge Distillation via Teacher Assistant", Mirzadeh et al., 2019](https://arxiv.org/abs/1902.03393)
- [Article : "On the Efficacy of Knowledge Distillation", Cho et Hariharan, 2019](https://arxiv.org/abs/1910.01348)
- [Ressources](../RESOURCES.md)

---

Ça ne passe pas ? Relisez la source primaire en haut de page, car cette leçon la condense et c'est dans la condensation que la compréhension s'échappe. Consultez le [glossaire](../GLOSSARY.md) pour tout terme qui vous a paru glissant.

Si c'est la leçon elle-même qui n'est pas claire plutôt que la matière, c'est un défaut : [ouvrez une issue](https://github.com/TokenCemetery/teach/issues).
