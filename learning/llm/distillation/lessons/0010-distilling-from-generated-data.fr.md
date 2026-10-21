---
title: "10. Distiller à partir de données générées"
description: "Construire un jeu d'instructions à partir des générations d'un enseignant, comme l'ont fait Self-Instruct et Alpaca"
type: lesson
---

# Leçon 10. Distiller à partir de données générées

**Lien avec la mission :** La mission vous demande de distiller à partir des données générées d'un enseignant, ce qui veut dire construire les entrées autant que collecter les sorties, et savoir ce que coûte cette construction.
**Source primaire :** [Article : "Self-Instruct: Aligning Language Models with Self-Generated Instructions", Wang et al., 2022](https://arxiv.org/abs/2212.10560)
**Prérequis :** [Leçon 9](0009-token-or-sequence.md), [Données synthétiques](../GLOSSARY.md), [Distillation au niveau de la séquence](../GLOSSARY.md), [Enseignant](../GLOSSARY.md), [Élève](../GLOSSARY.md)

## Échauffement

1. ▢ Dans la recette de Kim et Rush, d'où venaient les entrées, et qu'a ajouté l'enseignant ?

<details markdown="1"><summary>Vérifier</summary>

Les entrées étaient les phrases d'entraînement existantes. L'enseignant n'a ajouté que les sorties : sa traduction par beam search de chaque entrée. L'élève s'est entraîné sur ces paires entrée-sortie (leçon 8).

</details>

2. ▢ Un enseignant se trouve derrière une API et ne renvoie que du texte. Quel niveau de distillation vous est ouvert ?

<details markdown="1"><summary>Vérifier</summary>

Le niveau de la séquence, sur le texte que vous pouvez collecter (leçon 9). Le niveau du token a besoin de la distribution de l'enseignant à chaque position, ce que le texte seul ne vous donne pas.

</details>

## À savoir

### La distillation à partir de données générées est de la distillation au niveau de la séquence avec un choix de plus

Dans la leçon 8, les entrées étaient données : le jeu d'entraînement d'une tâche de traduction. Pour un modèle d'instructions généraliste, il n'y a pas d'ensemble fixe d'entrées. Quelqu'un doit écrire les prompts.

La distillation à partir de données générées est de la [distillation au niveau de la séquence](../GLOSSARY.md) où vous choisissez aussi les entrées. L'enseignant écrit les prompts ou c'est vous qui les écrivez, l'enseignant écrit les réponses, et l'élève s'entraîne avec une entropie croisée simple sur les paires. Tout ce que reçoit l'élève est décidé par ces données : un élève ne peut apprendre que les comportements que montrent les paires.

### Self-Instruct : le pipeline

Self-Instruct (Wang et al., 2022) construit un jeu d'instructions à partir des propres générations d'un modèle, en partant de 175 tâches de départ écrites par des humains, chacune avec une instruction et une instance. Il comporte quatre étapes (section 2.2) :

1. **Générer des instructions.** Échantillonner 8 instructions du pool de tâches comme exemples en contexte, 6 écrites par des humains et 2 générées lors de tours précédents, et demander au modèle d'en produire de nouvelles.
2. **Classifier la tâche.** Demander au modèle, avec quelques exemples (12 instructions de départ de classification et 19 de non-classification), si l'instruction est une tâche de classification, c'est-à-dire une tâche avec un ensemble de sorties petit et limité.
3. **Générer des instances.** Pour la plupart des tâches, l'entrée d'abord : écrire une entrée, puis la sortie. Pour les tâches de classification, la sortie d'abord : écrire le label de classe, puis une entrée pour ce label. Les auteurs ont ajouté cela parce que la génération entrée d'abord produisait des entrées biaisées vers un seul label, par exemple des phrases grammaticalement correctes pour une tâche de détection d'erreurs de grammaire.
4. **Filtrer.** Ne garder une nouvelle instruction que si sa similarité ROUGE-L avec chaque instruction déjà dans le pool est inférieure à 0.7. Écarter les instructions contenant des mots-clés comme image, picture ou graph qu'un modèle de langage ne sait pas traiter. Écarter les instances en double et les instances ayant la même entrée mais des sorties différentes. Écarter les instances qui échouent à des heuristiques simples, comme une instruction trop longue ou trop courte, ou une sortie qui ne fait que répéter l'entrée.

La boucle se rebranche sur elle-même : les instructions acceptées rejoignent le pool et deviennent des exemples en contexte pour les tours suivants. Les règles de filtrage sont le sujet de la leçon 12.

Le résultat, sur le modèle GPT-3 `davinci`, a été 52,445 instructions et 82,439 instances après filtrage, dont 11,584 instructions étaient des tâches de classification (tableau 1). Le fine-tuning de GPT-3 sur l'ensemble a coûté 338 $ via le service de fine-tuning du fournisseur (annexe A.3). Le même modèle a généré les données puis a été affiné dessus, si bien que l'enseignant et l'élève sont partis d'un seul modèle.

Leur évaluation, sur des tâches non vues de SuperNI mesurées par ROUGE-L (tableau 3) : GPT-3 brut a obtenu 6.8, le modèle Self-Instruct 39.9, et le modèle d'OpenAI ajusté par instructions InstructGPT001 40.8. Les auteurs y lisent un gain de 33.1 points qui égale presque InstructGPT001. C'est leur résultat sur leur benchmark et leur métrique.

### Alpaca : la même recette à plus petite échelle

L'équipe Stanford CRFM a construit Alpaca à partir de l'idée de Self-Instruct, mais a changé l'enseignant et l'élève (billet d'Alpaca, « Training recipe ») :

- Ils sont partis des mêmes 175 paires de départ et ont demandé à text-davinci-003 d'OpenAI d'en générer davantage.
- Ils ont simplifié le pipeline de génération par rapport à Self-Instruct, et disent que cela a réduit le coût.
- Les données sont 52K instructions uniques avec leurs sorties, qui ont coûté moins de 500 $ via l'API d'OpenAI.
- Ils ont fait un fine-tuning de LLaMA 7B par apprentissage supervisé. Le premier run a pris 3 heures sur 8 A100 de 80 Go, ce qu'ils estiment à moins de 100 $ chez la plupart des fournisseurs cloud.

Leur phrase de synthèse est qu'Alpaca 7B peut être reproduit pour moins de 600 $. Sur une évaluation préliminaire à un seul tour, ils rapportent qu'il se comporte qualitativement de façon similaire à text-davinci-003. Traitez cela comme l'impression des auteurs sur une petite évaluation, pas comme une égalité mesurée ; la leçon 18 revient sur la raison pour laquelle de telles impressions peuvent tromper.

| | Self-Instruct | Alpaca |
|---|---|---|
| Enseignant | GPT-3 `davinci` (le modèle qui a ensuite été affiné) | text-davinci-003 |
| Élève | GPT-3 `davinci` | LLaMA 7B |
| Ensemble de départ | 175 tâches | Les mêmes 175 paires |
| Données | 52,445 instructions, 82,439 instances | 52K instructions avec sorties |
| Coût déclaré | 338 $ pour le fine-tuning | Moins de 500 $ pour les données, moins de 100 $ pour le run |

### Ce que décide la conception des données

Quatre choix façonnent ce que l'élève apprend, et chacun est le vôtre quand vous générez des données :

- **L'ensemble de départ.** Tout est généré à partir de 175 exemples, donc ce qu'ils couvrent limite ce en quoi le pool peut grandir.
- **Le prompt.** Les exemples en contexte et le gabarit orientent le style et le mélange de tâches.
- **Les réglages d'échantillonnage.** La température et les réglages similaires fixent la variété des sorties.
- **Le filtre.** Ce que vous gardez est le jeu d'entraînement. Un filtre faible laisse les erreurs de l'enseignant devenir les leçons de l'élève.

Un élève ne peut égaler que ce que l'enseignant a écrit, donc une erreur qui survit au filtre est apprise comme si elle était correcte.

### Des restrictions sont venues avec les données

Le billet d'Alpaca est explicite : le modèle est réservé à la recherche académique. Il donne trois raisons : LLaMA a une licence non commerciale, les données viennent de text-davinci-003 dont les conditions interdisent de développer des modèles concurrents d'OpenAI, et ils n'avaient pas mis en place de mesures de sécurité adéquates. La leçon 13 lit ces restrictions de près. Pour l'instant, notez que le coût des données était la plus petite partie de ce qui les accompagnait.

## Pratique

1. ▢ Les données d'Alpaca ont coûté moins de 500 $ pour 52K paires instruction-sortie. Quel est le coût par exemple au maximum, et pourquoi n'est-ce pas le coût complet du modèle ?

<details markdown="1"><summary>Vérifier</summary>

Moins de 500 $ divisé par 52,000 fait environ 0,0096 $, moins d'un centime par exemple. Ce n'est pas le coût complet : le billet compte séparément le run de fine-tuning (3 heures sur 8 A100 de 80 Go, moins de 100 $ chez la plupart des clouds), et aucun des deux chiffres ne compte l'effort humain des 175 exemples de départ, l'évaluation ou la démo. La leçon 21 compte correctement le coût de l'enseignant.

</details>

2. ▢ Self-Instruct génère les données de classification sortie d'abord. Quel problème de la génération entrée d'abord cela corrige-t-il ?

    - a) Les entrées sortent biaisées vers un seul label de classe
    - b) Les sorties sortent bien plus longues que toute réponse humaine
    - c) Les instructions répètent le même texte d'entrée sans aucun changement
    - d) Les labels sortent écrits dans un format totalement incohérent

<details markdown="1"><summary>Vérifier</summary>

**a)** L'exemple de l'article : à qui l'on demande d'écrire une entrée pour la détection d'erreurs de grammaire, le modèle tend à écrire une entrée grammaticalement correcte, si bien qu'une classe domine. Écrire d'abord le label puis une entrée pour ce label les équilibre. (b), (c) et (d) ne sont pas le problème que nomment les auteurs.

</details>

3. ▢ Une nouvelle instruction générée a une similarité ROUGE-L de 0.74 avec une instruction déjà dans le pool et de 0.2 avec toutes les autres. Self-Instruct la garde-t-il, et pourquoi ?

<details markdown="1"><summary>Indice</summary>

La règle porte sur le maximum sur le pool, pas sur la moyenne.

</details>

<details markdown="1"><summary>Vérifier</summary>

Non. L'instruction n'est gardée que si sa similarité ROUGE-L avec toute instruction existante est inférieure à 0.7, et 0.74 dépasse ce seuil. La règle maintient la diversité du pool en rejetant une quasi-copie d'un seul membre, quelle que soit la différence avec le reste du pool.

</details>

4. ▢ Votre équipe veut copier Alpaca mais avec un enseignant qui produit des réponses courtes et sèches. Qu'attendez-vous de l'élève, et quelle partie du pipeline changeriez-vous en premier ?

<details markdown="1"><summary>Vérifier</summary>

Attendez-vous à ce que l'élève réponde dans le même style sec, parce qu'il ne peut apprendre que ce que montrent les paires. Changez d'abord le prompt ou les réglages de l'enseignant, puisque c'est là que se fixe le style de réponse, puis relancez le filtre et comparez à l'œil un échantillon de paires générées avant d'entraîner. C'est une prédiction tirée de la façon dont les données déterminent l'élève, pas un résultat mesuré.

</details>

5. ▢ La leçon 8 a constaté qu'un élève au niveau de la séquence entraîné sur la meilleure sortie unique d'un enseignant finit piqué autour de cette sortie. Cela suggère-t-il de générer plusieurs sorties par prompt, ou une seule, et que coûterait chacune ?

<details markdown="1"><summary>Vérifier</summary>

Cela ne tranche pas la question. Une sortie par prompt est l'approche de style mode : peu chère et cohérente, mais un seul échantillon. Plusieurs sorties par prompt montrent à l'élève davantage de la variété de l'enseignant, pour plusieurs fois le coût de génération et avec plus de filtrage à faire. Kim et Rush ont essayé l'échantillonnage à la place du mode sur la traduction et ont gardé le mode. C'est un résultat pour leur tâche, testez donc les deux sur la vôtre.

</details>

## Exercices en situation réelle

- [ ] Ouvrez l'article Self-Instruct et trouvez le gabarit de prompt pour la génération d'instructions (tableau 5). Notez à quoi ressemblent les exemples en contexte et combien il y en a d'écrits par des humains et par le modèle.
- [ ] Ouvrez le billet d'Alpaca et trouvez la phrase qui liste les trois facteurs de la publication réservée à la recherche. Notez lequel dépend de votre choix d'enseignant.
- [ ] Demain : écrivez sans notes les quatre étapes du pipeline Self-Instruct et le seuil du filtre, puis comparez à l'article.

## Pour aller plus loin

- [Séquences et données synthétiques](../reference/sequence-and-synthetic-data.md)
- [Article : "Self-Instruct: Aligning Language Models with Self-Generated Instructions", Wang et al., 2022](https://arxiv.org/abs/2212.10560)
- [Billet : "Alpaca: A Strong, Replicable Instruction-Following Model", Stanford CRFM, 2023](https://crfm.stanford.edu/2023/03/13/alpaca.html)
- [Ressources](../RESOURCES.md)

---

Ça ne passe pas ? Relisez la source primaire en haut de page, car cette leçon la condense et c'est dans la condensation que la compréhension s'échappe. Consultez le [glossaire](../GLOSSARY.md) pour tout terme qui vous a paru glissant.

Si c'est la leçon elle-même qui n'est pas claire plutôt que la matière, c'est un défaut : [ouvrez une issue](https://github.com/TokenCemetery/teach/issues).
