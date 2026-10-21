---
title: "11. Compaction et récupération à la demande"
description: "Deux stratégies pour garder dans le budget le contexte d'un agent de longue durée tout en préservant ce qui compte encore"
type: lesson
---

# Leçon 11. Compaction et récupération à la demande

**Lien avec la mission :** Budgéter le coût en tokens et la latence d'une boucle agentique, et dire de quelle partie de la boucle vient l'amplification.
**Source primaire :** [Billet : "Effective Context Engineering for AI Agents", Anthropic Engineering](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents)
**Prérequis :** [Leçon 10](0010-the-context-window-as-budget.md)

## Échauffement

1. ▢ Pourquoi la troncature naïve (abandonner les tours les plus anciens dès qu'une limite de taille est atteinte) est-elle risquée ?

<details markdown="1"><summary>Vérifier</summary>

La troncature naïve peut abandonner un résultat d'outil, une contrainte ou une instruction dont le modèle a encore besoin, et le modèle ne saura pas que l'information manque. Il travaillera en silence à partir d'une compréhension incomplète et échouera de manière inattendue.

</details>

2. ▢ Qu'est-ce que la dégradation du contexte ?

<details markdown="1"><summary>Vérifier</summary>

À mesure que du contenu peu pertinent s'accumule dans le contexte, l'attention du modèle devient plus bruitée et il a du mal à distinguer ce qui compte encore des anciennes impasses et des raisonnements abandonnés. Un contexte gonflé est à la fois coûteux et moins précis.

</details>

## À savoir

### Compaction : remplacer les anciens tours par un résumé

Une stratégie consiste à remplacer périodiquement un passage ancien du transcript par un résumé condensé sur lequel le modèle peut encore agir. Au lieu de conserver « J'ai lu file1.py et trouvé ces 50 lignes », vous pourriez remplacer toute cette séquence par « file1.py contient une classe de base de données ; les méthodes clés sont init, query, close ».

Le harness détecte quand le transcript est devenu long et confie les anciens tours à un résumeur (souvent un autre appel au modèle, ou une extraction plus simple). Le résumé est inséré dans le transcript à la place des tours d'origine, ce qui maintient la taille du transcript sous contrôle.

**Le risque :** le résumé peut omettre un détail qui s'avère important plus tard. Si l'agent a ensuite besoin de savoir que file1.py définissait aussi une fonction utilitaire, mais que le résumé l'a omise, l'agent a perdu cette information définitivement. Contrairement à la troncature naïve (toujours risquée), la compaction est délibérée et réversible en théorie, mais la perte d'information est réelle et difficile à prévoir.

### Récupération à la demande : donner à l'agent un outil pour retrouver le détail

Une autre stratégie consiste à ne pas garder le détail complet en contexte du tout. Au lieu de charger et de stocker le contenu de chaque fichier, le harness ne garde qu'un résumé (nom du fichier, taille, date de modification, une brève note sur le nombre de lignes). Quand le modèle a besoin de voir le contenu complet, il appelle un outil comme « read_file » ou « re_fetch_detail ». Le modèle obtient le détail à la demande, et seulement pour le fichier qu'il examine à ce moment.

Le compromis : chaque récupération ajoute de la latence (un appel d'outil de plus, un aller-retour de plus). Mais le contexte résident reste beaucoup plus petit. Sur une longue tâche qui examine de nombreux fichiers mais n'en manipule que quelques-uns à la fois, la récupération à la demande est bien moins chère en tokens totaux que garder chaque fichier en contexte pour toujours.

### Combinées : compaction et récupération à la demande

L'approche la plus puissante combine les deux. Le harness maintient un contexte petit et soigneusement géré qui contient :

- L'objectif et les dernières contraintes
- Un résumé de ce qui a été fait jusqu'ici
- Les noms de fichiers et les métadonnées
- Les constats récents qui comptent

Les anciens résultats détaillés sont compressés en résumés (compaction). Si le modèle a besoin de voir le détail complet d'un ancien fichier ou résultat, il peut le récupérer avec un outil de récupération (à la demande). La mémoire de travail du modèle est petite et rapide, mais il a un moyen de remonter chercher le détail dont il a besoin.

Dans un agent de revue de code qui examine 100 fichiers sur 200 tours :

- Un agent naïf garde en contexte chaque fichier jamais lu, jusqu'à atteindre 500 000 tokens au tour 50. Les tours 51 à 200 sont lents et coûteux.
- Un agent malin ne garde en contexte que les chemins de fichiers et un résumé (5 000 tokens), avec un outil « read_file ». Il va chercher chaque fichier à la demande au fil de ses comparaisons. Le tour 50 coûte à peu près autant que le tour 200. Le coût total en tokens sur toute l'exécution n'est qu'une fraction de celui de l'approche naïve.

## Pratique

1. ▢ Vous résumez les 20 premiers tours du transcript d'un agent en un paragraphe : « L'agent a exploré trois bases de code et trouvé des goulots d'étranglement de performance dans le caching. » Ce résumé remplace les 20 tours d'origine. Plus tard, au tour 50, le modèle dit vouloir comprendre la requête exacte qui était lente. Quel risque la compaction présente-t-elle ici ?

    - a) Le modèle refusera de travailler sans les tours d'origine
    - b) Le résumé n'a peut-être pas consigné les détails exacts de la requête, et ils sont peut-être perdus pour toujours
    - c) La compaction est toujours sans perte, donc ce n'est pas un risque
    - d) Le modèle relira le résumé et se souviendra de la requête

<details markdown="1"><summary>Vérifier</summary>

**b)** La compaction abandonne des détails qui pourraient compter plus tard. Le résumé est concis mais peut omettre des précisions dont le modèle a besoin en aval. Contrairement à la troncature, la compaction est délibérée, mais la perte d'information est réelle. L'option a est fausse parce que le modèle travaillera avec le résumé, mais peut produire des résultats faux. L'option c est fausse parce que la compaction est avec perte par conception. L'option d est fausse parce que le modèle ne travaille qu'avec le nouveau résumé, pas avec l'original.

</details>

2. ▢ Un agent traite 200 documents et résume chacun. Pourquoi la récupération à la demande est-elle préférable à garder le contenu des 200 documents en contexte dès le départ ?

<details markdown="1"><summary>Indice</summary>

De combien de documents le modèle a-t-il typiquement besoin dans son contexte en même temps ? S'il résume le document 45, a-t-il besoin que le contenu des documents 1 à 44 soit disponible à cet instant ?

</details>

<details markdown="1"><summary>Vérifier</summary>

Le modèle se concentre généralement sur un ou quelques documents à la fois. Garder les 200 en contexte gaspille des tokens sur du contenu que le modèle n'examine pas en ce moment. Avec la récupération à la demande, le harness ne garde en contexte que le document courant et un résumé des constats précédents. Si le modèle a besoin de réexaminer un ancien document, il va le chercher. Le coût total en tokens sur 200 documents est bien inférieur à celui de les garder tous en mémoire en permanence.

</details>

3. ▢ Dans un système de compaction plus récupération à la demande, quelles trois choses le contexte toujours résident doit-il contenir ?

<details markdown="1"><summary>Vérifier</summary>

L'objectif et les contraintes, un résumé de l'avancement jusqu'ici, et des métadonnées sur les ressources disponibles (noms de fichiers, titres de documents, listes d'outils). Le détail complet est soit compressé en résumés (compaction), soit disponible à la demande (récupération). Cela garde le contexte résident petit et centré sur ce dont le modèle a besoin pour agir maintenant.

</details>

4. ▢ Vous concevez un agent qui lit des articles techniques et en extrait des résumés. Après la lecture de 50 articles, le contexte fait 60 000 tokens. Comparez deux approches :
    - Approche A : compacter les anciens contenus d'articles en résumés d'un paragraphe tous les 10 articles. Garder tous les résumés en contexte.
    - Approche B : ne garder en contexte que les titres, les auteurs et les constats des articles. Donner à l'agent un outil « re_read_paper » s'il a besoin du texte complet.

Quelle approche utilise le moins de tokens à l'article 100, et pourquoi ?

<details markdown="1"><summary>Vérifier</summary>

L'approche B utilise moins de tokens. Avec l'approche A, vous accumulez 10 résumés de 200 à 300 tokens chacun, soit 2 000 à 3 000 tokens de contenu compacté à l'article 100. Avec l'approche B, vous ne gardez que les métadonnées (100 à 200 tokens) plus le texte de l'article courant (500 tokens), et le modèle a rarement besoin de relire un ancien article. L'approche B économise des tokens en ne stockant pas en permanence chaque ancien résumé.

</details>

## Exercices en situation réelle

- [ ] Auditez un long transcript d'un agent que vous avez utilisé ou écrit. Identifiez quelles parties sont encore pertinentes (objectif, contraintes récentes, problèmes en suspens) et lesquelles peuvent être compactées ou supprimées sans risque. Écrivez un résumé d'une phrase qui pourrait remplacer les premiers 30 % des tours.
- [ ] Concevez un agent hypothétique pour une tâche qui vous tient à cœur (recherche, code, analyse). Esquissez si vous utiliseriez la compaction, la récupération à la demande ou les deux, et pourquoi.
- [ ] Demain : prenez une version « naïve » d'un agent qui garde tout en contexte, estimez son coût en tokens sur 100 tours, puis reconcevez-la avec compaction et récupération à la demande et estimez le nouveau coût.

## Pour aller plus loin

- [Billet : "Effective Context Engineering for AI Agents", Anthropic Engineering](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents)
- [Ressources](../RESOURCES.md)

---

Ça ne passe pas ? Relisez la source primaire en haut de page, car cette leçon la condense et c'est dans la condensation que la compréhension s'échappe. Consultez le [glossaire](../GLOSSARY.md) pour tout terme qui vous a paru glissant.

Si c'est la leçon elle-même qui n'est pas claire plutôt que la matière, c'est un défaut : [ouvrez une issue](https://github.com/TokenCemetery/teach/issues).
