---
title: "10. La fenêtre de contexte comme budget"
description: "La fenêtre de contexte est une ressource finie que le harness gère activement au fil du temps, pas un journal inerte"
type: lesson
---

# Leçon 10. La fenêtre de contexte comme budget

**Lien avec la mission :** Budgéter le coût en tokens et la latence d'une boucle agentique, et dire de quelle partie de la boucle vient l'amplification.
**Source primaire :** [Billet : "Effective Context Engineering for AI Agents", Anthropic Engineering](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents)
**Prérequis :** [Leçon 9](0009-return-shapes-and-tool-set-bloat.md), [Trajectoire](../GLOSSARY.md)

## Échauffement

1. ▢ Dans la boucle d'agent de la leçon 6, à quel moment le harness décide-t-il quel appel d'outil exécuter ?

<details markdown="1"><summary>Vérifier</summary>

Le modèle produit un bloc d'appel d'outil (nom, paramètres), et le harness l'analyse et exécute l'outil. Le modèle décide quel outil en traitant le transcript qu'il reçoit.

</details>

2. ▢ Que devient le transcript chaque fois qu'un outil termine ?

<details markdown="1"><summary>Vérifier</summary>

Le résultat (ou l'erreur) est ajouté au transcript, et le nouveau transcript est renvoyé au modèle à l'itération suivante de la boucle.

</details>

## À savoir

### Le transcript grandit à chaque tour, et devient vite coûteux

Chaque itération de la boucle d'agent ajoute au transcript. Après 10, 20 ou 100 tours d'exécution d'un agent, le transcript contient chaque message, chaque appel d'outil et chaque résultat de toute l'exécution. À l'itération suivante, ce transcript entier repart vers le modèle. À l'itération d'après, il repart encore, plus long d'un tour.

Cela signifie que deux coûts croissent tous deux avec la longueur de la trajectoire, même quand rien de nouveau ne se passe :

- **Coût en tokens** : chaque message au modèle renvoie tous les anciens tours. Une trajectoire de cinq tours coûte 5 fois moins de tokens par appel qu'une trajectoire de 100 tours. Sur un agent de longue durée, cela devient le coût dominant.
- **Latence** : un contexte plus long signifie plus de tokens à traiter, donc plus lent. L'agent attend plus longtemps chaque réponse.

### Dégradation du contexte : l'attention du modèle se détériore à mesure que le fatras s'accumule

À mesure que du contenu peu pertinent s'accumule dans le contexte, l'attention du modèle devient plus bruitée. La capacité du modèle à distinguer ce qui compte encore (l'objectif, les contraintes récentes, les résultats sur lesquels il n'a pas encore agi) se détériore quand tout cela est enseveli sous un gros tas d'anciennes impasses et de lignes de raisonnement abandonnées. On parle parfois de « context rot ». Un contexte gonflé n'est pas seulement coûteux : il rend le modèle moins bon pour la tâche.

### La troncature naïve est risquée

L'instinct le plus simple est d'abandonner les tours les plus anciens dès que le contexte atteint une limite de taille. Mais la troncature naïve risque de perdre en silence des informations critiques. Si la frontière de troncature tombe au milieu de :

- Une instruction en plusieurs étapes que le modèle doit encore suivre
- Un résultat sur lequel le modèle n'a pas encore agi
- Un énoncé de contrainte ou d'objectif
- Une partie d'un system prompt ou d'un exemple

alors l'agent se met à dysfonctionner en silence, d'une façon que le harness n'a aucun moyen de détecter. Le modèle ne saura pas qu'une instruction clé a été retirée ; il travaillera simplement avec une compréhension incomplète et échouera de manière inattendue.

### La gestion active est un choix de conception délibéré

Parce que la troncature naïve est dangereuse et que le coût croît avec la longueur de la trajectoire, le harness ne peut pas traiter le transcript comme un journal inerte qui ne fait que grandir. « Ce qui reste dans le contexte et ce qui part » doit être une décision de conception délibérée, intégrée au harness. La trajectoire existe toujours, mais c'est le harness qui décide quelle portion le modèle voit à chaque appel.

Il y a deux stratégies principales pour cela (traitées dans la leçon suivante) : la compaction et la récupération à la demande.

## Pratique

1. ▢ Un agent fait 50 appels d'outils au cours d'une longue tâche de recherche. À l'appel 51, le modèle reçoit un transcript de 20 000 tokens. À l'appel 52, combien de tokens le modèle reçoit-il dans le transcript (approximativement) ?

    - a) 20 000 tokens
    - b) 20 000 plus les tokens du nouveau résultat de l'appel 51
    - c) 40 000 tokens
    - d) Cela dépend de la taille du résultat de l'appel 51

<details markdown="1"><summary>Vérifier</summary>

**b)** Le modèle reçoit le transcript d'origine de 20 000 tokens plus le nouveau résultat ajouté. Si le résultat de l'appel 51 faisait 500 tokens, le modèle reçoit environ 20 500 tokens. Le coût en tokens croît à chaque tour, et sur de très longues exécutions cela devient une dépense sérieuse. L'option c est fausse parce que le modèle ne reçoit pas deux fois le résultat de l'appel 51 ; l'option a ignore le nouvel ajout ; l'option d est juste dans l'esprit (la taille du résultat compte) mais b est la réponse la plus précise.

</details>

2. ▢ Vous concevez un agent pour une tâche de revue de code. L'agent lit des fichiers, les compare, prend des notes et produit un résumé. Pourquoi est-il risqué de simplement abandonner les plus anciens résultats d'outils dès que le transcript atteint une limite de 50 000 tokens ?

<details markdown="1"><summary>Indice</summary>

Et si la frontière de troncature tombait entre une ancienne lecture de fichier et une comparaison que le modèle n'a pas terminée ? Et si une contrainte sur le périmètre des fichiers se trouvait dans la partie abandonnée ?

</details>

<details markdown="1"><summary>Vérifier</summary>

La troncature naïve peut abandonner un résultat d'outil (comme le contenu d'un fichier) auquel le modèle doit encore se référer, ou une contrainte (comme « only review files in src/core/ ») dont le modèle doit se souvenir. Le modèle ne saura pas que l'information manque ; il travaillera en silence à partir d'une image incomplète et tirera des conclusions fausses. Le harness doit être plus malin que couper à la limite de tokens.

</details>

3. ▢ Laquelle des affirmations suivantes est vraie à propos de la dégradation du contexte ?

    - a) La dégradation du contexte ne se produit que si le transcript contient des erreurs
    - b) La dégradation du contexte est évitée en formatant joliment les résultats d'outils
    - c) Un gros transcript contenant beaucoup d'anciens tours non pertinents rend le modèle moins précis, même si aucune information critique n'est tronquée
    - d) La dégradation du contexte n'est pas un vrai problème avec les modèles modernes

<details markdown="1"><summary>Vérifier</summary>

**c)** L'attention du modèle se détériore à mesure que du contenu peu pertinent s'accumule. Un gros transcript en désordre rend plus difficile pour le modèle de trouver et de hiérarchiser ce qui compte. L'option a est fausse parce que les impasses et les tâches terminées créent du bruit même sans erreurs. L'option b est fausse parce qu'un joli formatage ne résout pas le problème de rapport signal sur bruit. L'option d est fausse parce que la dégradation du contexte est bien documentée dans les tâches à long contexte.

</details>

4. ▢ Vous observez que la latence d'un agent augmente à mesure que sa trajectoire grandit. Nommez deux raisons à cela.

<details markdown="1"><summary>Vérifier</summary>

Premièrement, le modèle reçoit plus de tokens à chaque appel, ce qui prend plus de temps à traiter. Deuxièmement, le modèle doit trier davantage de contenu peu pertinent (dégradation du contexte) pour trouver l'information qui compte, ce qui affecte la qualité de son raisonnement et peut le faire commettre des erreurs qui gaspillent des tours.

</details>

## Exercices en situation réelle

- [ ] Expliquez à quelqu'un d'autre (ou dans une note) pourquoi on ne peut pas simplement continuer à abandonner les plus anciens tours d'un transcript quand il devient trop long. Utilisez un exemple tiré d'une vraie tâche que vous voudriez confier à un agent.
- [ ] Ouvrez le transcript d'une longue conversation à plusieurs tours que vous avez eue avec un modèle de langage, et notez à partir de combien de tours le modèle commence à avoir du mal à se rappeler les contraintes du début.
- [ ] Demain : planifiez une tâche de recherche qu'un agent pourrait faire (lire 20 fichiers, comparer des motifs, produire un résumé), et esquissez la taille qu'aurait le transcript si l'agent gardait en mémoire le contenu complet de chaque fichier en permanence, par rapport à s'il ne gardait que les chemins de fichiers et allait chercher le contenu à la demande.

## Pour aller plus loin

- [Billet : "Effective Context Engineering for AI Agents", Anthropic Engineering](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents)
- [Ressources](../RESOURCES.md)

---

Ça ne passe pas ? Relisez la source primaire en haut de page, car cette leçon la condense et c'est dans la condensation que la compréhension s'échappe. Consultez le [glossaire](../GLOSSARY.md) pour tout terme qui vous a paru glissant.

Si c'est la leçon elle-même qui n'est pas claire plutôt que la matière, c'est un défaut : [ouvrez une issue](https://github.com/TokenCemetery/teach/issues).
