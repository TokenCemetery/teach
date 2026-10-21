---
title: "23. L'exécution de code comme outil"
description: "Donner à un agent un unique outil d'exécution de code en sandbox plutôt que de nombreux outils étroits et individuels"
type: lesson
---

# Leçon 23. L'exécution de code comme outil

**Lien avec la mission :** Pour décider si une tâche donnée a vraiment besoin d'un agent, il faut comprendre qu'un seul outil d'exécution de code peut remplacer des dizaines d'outils étroits, ce qui réduit le coût en tokens et la latence tout en exigeant un sandbox robuste face à du code arbitraire.
**Source primaire :** [Billet : "Code Execution with MCP", Anthropic Engineering](https://www.anthropic.com/engineering/code-execution-with-mcp)
**Prérequis :** [Leçon 22](0022-sandboxing-and-approval-gates.md)

## Échauffement

1. ▢ Dans la leçon 22, nous avons distingué un sandbox d'un point d'approbation. Que fait chacun, et lequel utiliseriez-vous pour empêcher le modèle de supprimer un fichier par accident ?

<details markdown="1"><summary>Vérifier</summary>

Un sandbox est une frontière d'exécution qui empêche le code d'atteindre certaines ressources (comme des fichiers hors d'un répertoire autorisé). Un point d'approbation est un point de contrôle humain avant des actions risquées. Pour empêcher une suppression accidentelle, vous utiliseriez un sandbox qui restreint l'outil à n'écrire que dans une arborescence sûre, de sorte que même si le modèle demande la suppression, le sandbox la rejette. Un point d'approbation mettrait en pause et demanderait l'approbation d'un humain avant de tenter la suppression, mais ne l'empêcherait pas si elle est approuvée.

</details>

2. ▢ La leçon 21 a introduit l'idée de la découverte d'outils à grande échelle : le modèle peut inspecter quels outils existent plutôt que de charger chaque définition en contexte. Quel problème cela résout-il ?

<details markdown="1"><summary>Vérifier</summary>

Quand vous avez des centaines d'outils, précharger la définition, le nom, la description et le schéma de paramètres de chaque outil dans la fenêtre de contexte du modèle épuise les tokens et rend plus difficile pour le modèle de raisonner sur l'outil à appeler. La découverte d'outils permet au modèle de demander des informations sur les outils disponibles à la demande ou d'appeler un point d'introspection pour explorer les capacités, de sorte que la liste complète n'a pas à vivre dans le contexte initial.

</details>

## À savoir

### L'exécution de code comme alternative à de nombreux outils étroits

Prenons un scénario d'analyse de données. Sans exécution de code, vous pourriez exposer ces outils au modèle :

- list_files : renvoie une liste de fichiers d'un répertoire
- read_csv : lit un fichier CSV et renvoie les N premières lignes
- compute_mean : calcule la moyenne d'une colonne
- compute_median : calcule la médiane d'une colonne
- filter_rows : filtre un tableau selon une condition
- sort_by : trie un tableau selon une colonne
- write_csv : réécrit un tableau dans un fichier

Le modèle doit maintenant décider quel outil appeler dans quel ordre. Il peut appeler read_csv, puis filter_rows, puis compute_mean : trois allers-retours dans la boucle du modèle. Chaque aller-retour consomme des tokens pour raisonner sur l'outil à appeler ensuite, et chaque définition d'outil coûte des tokens dans la fenêtre de contexte initiale.

Donnez plutôt au modèle un seul outil : un interpréteur de code en sandbox. Le modèle écrit un court programme Python :

```python
import pandas as pd

data = pd.read_csv('data.csv')
filtered = data[data['age'] > 30]
result = filtered['salary'].mean()
print(result)
```

Le modèle l'exécute une fois et obtient la réponse. Avantages : un appel d'outil au lieu de trois, une définition d'outil au lieu de sept, et le modèle peut enchaîner les opérations en un seul tour sans raisonner à nouveau sur l'outil à appeler ensuite.

### Bénéfices en coût et en latence

Cette approche réduit à la fois le coût en tokens et la latence :

- Coût en tokens : vous payez une définition d'outil au lieu de plusieurs, et la surcharge de raisonnement du modèle sur l'outil à appeler s'effondre en simple écriture de code, ce que le modèle fait déjà efficacement.
- Latence : un aller-retour d'appel d'outil au lieu de trois ou sept signifie que le temps réel de l'agent baisse proportionnellement.

Pour des agents qui tournent à grande échelle ou avec des exigences de temps réel, ces gains se cumulent.

### Lien avec la découverte d'outils à grande échelle

La leçon 21 a introduit l'idée qu'au lieu de précharger chaque définition d'outil en contexte, le modèle peut explorer dynamiquement les capacités disponibles. L'exécution de code en est une instanciation concrète : le modèle n'a pas besoin que chaque outil de transformation de données soit préchargé, parce qu'il peut écrire du code pour faire lui-même la transformation. Les capacités disponibles (fonctions, bibliothèques, utilitaires système) sont découvertes quand le code s'exécute, pas dans le contexte initial.

Dans certains systèmes, l'outil d'exécution de code peut lui-même avoir un mécanisme de découverte : une fonction que le modèle peut appeler pour lister les bibliothèques disponibles, les sources de données qu'il peut atteindre ou les commandes système disponibles. Cela superpose de la découverte à de la découverte.

### Ce qu'un sandbox doit imposer face à du code arbitraire

Dans la leçon 22, nous avons vu qu'un sandbox impose des frontières autour de ce que l'exécution d'un outil peut atteindre : chemins du système de fichiers, hôtes réseau, limites de ressources. Quand l'outil est « exécuter du code arbitraire que le modèle a écrit », le sandbox doit imposer ces frontières face à du code bien plus expressif et imprévisible qu'un appel d'outil fixe doté d'un schéma JSON connu.

Le modèle peut écrire du code qui :

- Tente de s'échapper de la frontière du système de fichiers en utilisant des liens symboliques, des astuces de traversée de chemin (/../..), ou en appelant des utilitaires système comme find ou ls pour sonder hors de la frontière.
- Écrit du code réseau qui essaie de joindre des hôtes hors de la liste autorisée.
- Lance des boucles infinies, des fonctions récursives ou des boucles d'allocation mémoire qui tentent d'épuiser les ressources.
- Appelle des fonctions ou des méthodes que le code croit exister mais que le harness entend interdire.

Le sandbox doit être assez robuste pour contenir tout cela. C'est plus difficile que de mettre dans un sandbox un outil fixe, parce que la surface du code est illimitée. Un vrai sandbox d'exécution de code exécute souvent le code dans un conteneur ou un processus isolé avec des règles seccomp, des espaces de noms réseau et des cgroups de ressources, et pas seulement des vérifications de permissions sur le système de fichiers.

### Exécution de code ou outils étroits : quand choisir quoi

L'exécution de code est puissante mais introduit de la complexité de sandbox. Vous devriez la préférer quand :

- Le modèle doit combiner de nombreuses petites opérations qui exigeraient autrement de nombreux allers-retours.
- Les opérations sont algorithmiques ou centrées sur la transformation de données (filtrage, agrégation, calcul, conversion de format).
- Les capacités disponibles sont bien définies et relativement stables.

Vous devriez vous en tenir à des outils étroits, conçus pour un but précis, quand :

- L'opération est réellement à enjeux élevés et bénéficie d'une supervision humaine explicite (envoyer un e-mail, publier publiquement, dépenser de l'argent).
- La sûreté de l'opération dépend de la validation des entrées ou des sorties d'une manière propre au domaine que le harness comprend mais que le code ne comprend pas.
- L'opération est rare et les économies de tokens d'un outil unique ne compensent pas la complexité du sandbox.

Les deux approches peuvent coexister : un agent peut avoir un outil d'exécution de code pour le traitement de données et des outils étroits soumis à un point d'approbation pour envoyer des e-mails ou publier des résultats.

## Pratique

1. ▢ Vous avez un agent qui utilise actuellement sept outils distincts pour la manipulation de chaînes : split_string, join_strings, uppercase, lowercase, replace_substring, reverse_string et trim_whitespace. Pourriez-vous remplacer les sept par un seul outil d'exécution de code ? Que gagneriez-vous et que perdriez-vous ?

<details markdown="1"><summary>Vérifier</summary>

Oui, vous le pourriez. Le modèle gagnerait : une définition d'outil au lieu de sept, un appel d'outil pour réaliser une opération complexe sur des chaînes au lieu de sept allers-retours, et la possibilité d'écrire du code lisible (« result = text.upper() ») au lieu de deviner des noms d'outils. Vous perdriez : des garde-fous explicites pour chaque opération (chaque outil pourrait valider l'entrée), et une latence déterministe (l'exécution de code devient variable selon ce que le modèle écrit). Pour la manipulation de chaînes, l'approche par exécution de code l'emporte généralement parce que les opérations sont simples et que le harness peut imposer une frontière de système de fichiers ou de ressources sans logique propre au domaine.

</details>

2. ▢ Vous concevez un agent pour un système de santé qui peut lire des dossiers de patients et générer des suggestions de diagnostic. Faut-il l'exposer via un outil d'exécution de code où le modèle écrit son propre code d'accès aux données, ou via des outils étroits comme read_patient_record, filter_by_condition et compute_risk_score ?

<details markdown="1"><summary>Indice</summary>

Réfléchissez à ce que signifie « sûreté » dans un contexte de santé. Que doit imposer le harness, et un sandbox de code généraliste peut-il l'imposer, ou faut-il une logique propre au domaine ?

</details>

<details markdown="1"><summary>Vérifier</summary>

Les outils étroits sont meilleurs ici. Un système de santé a des exigences de conformité strictes (HIPAA, journalisation d'audit, contrôle d'accès aux données) que le harness impose probablement par une logique propre au domaine, pas par un sandbox du système de fichiers. Un outil étroit read_patient_record peut inclure des vérifications d'autorisation, une journalisation d'audit et une rédaction des données ; un outil d'exécution de code ne peut pas facilement les imposer, parce que le harness devrait inspecter le code que le modèle a écrit, ce qui défait l'intérêt de l'exécution de code. Les enjeux élevés rendent aussi les points d'approbation plus précieux. Préférez des outils étroits et auditables quand la sûreté de l'opération dépend d'une logique métier propre au domaine, pas de frontières de système de fichiers.

</details>

3. ▢ Lequel de ces énoncés sur l'exécution de code est vrai ?

    - a) L'exécution de code est toujours plus rapide que des outils séparés parce qu'elle réduit les allers-retours, même pour de simples opérations uniques.
    - b) L'exécution de code réduit le coût en tokens parce qu'une définition d'outil en remplace plusieurs, mais ne fait gagner de la latence que si le modèle enchaîne plusieurs opérations.
    - c) L'exécution de code élimine le besoin de sandboxes parce que le code est de confiance.
    - d) L'exécution de code n'exige aucun point d'approbation parce que le harness peut inspecter le code avant son exécution.

<details markdown="1"><summary>Vérifier</summary>

**b)** L'exécution de code réduit le coût en tokens parce qu'une définition d'outil en remplace plusieurs, mais ne fait gagner de la latence que si le modèle enchaîne plusieurs opérations. Les économies de tokens sont réelles (une définition au lieu de plusieurs). Les gains de latence ne comptent que si le modèle fait plusieurs opérations qui exigeraient autrement plusieurs allers-retours ; pour une seule opération, le temps est similaire ou pire. L'option a est fausse (les opérations uniques n'en profitent pas). L'option c est fausse (l'exécution de code a besoin de sandboxes robustes parce que le code est arbitraire). L'option d est fausse (les points d'approbation gardent leur sens pour les opérations à enjeux élevés, et l'inspection préalable n'empêche pas toutes les erreurs).

</details>

4. ▢ Expliquez pourquoi le travail du sandbox devient plus difficile quand l'outil est « exécution de code » au lieu d'un outil précis comme « delete_file ». Donnez un scénario concret où cette difficulté compte.

<details markdown="1"><summary>Vérifier</summary>

Avec un outil précis, le harness sait à l'avance ce que fera l'outil et peut imposer une frontière à ce point précis (l'outil delete_file ne peut toucher que des fichiers d'un répertoire sûr). Avec l'exécution de code, le harness ne sait pas ce que le code fera avant son exécution ; le code peut appeler des utilitaires système, ouvrir des sockets réseau ou utiliser des fonctionnalités du langage que le harness n'attend pas. Un scénario concret : le modèle écrit du code qui appelle subprocess.Popen pour exécuter une commande shell comme « ls /../.. » afin de sonder le système de fichiers au-delà de la frontière prévue. Un sandbox à base de permissions de système de fichiers ne l'arrêtera pas à lui seul ; le sandbox a besoin de règles seccomp ou d'un conteneur pour empêcher des appels système arbitraires. C'est pourquoi les sandboxes d'exécution de code sont généralement plus complexes que ceux d'outils étroits.

</details>

5. ▢ Votre agent utilise l'exécution de code pour analyser des données. Le modèle écrit du code qui devrait lire un fichier CSV, mais il écrit à la place du code qui tente de télécharger un fichier depuis internet. Le sandbox n'autorise aucun accès réseau. Que se passe-t-il, et est-ce un échec du sandbox ?

<details markdown="1"><summary>Vérifier</summary>

Le code s'exécute, tente l'appel réseau, et l'opération réseau est rejetée ou bloquée. Ce n'est pas un échec du sandbox ; c'est le sandbox qui fonctionne comme prévu. Le rôle du sandbox est d'empêcher le code d'atteindre des ressources hors de sa frontière, pas de garantir que le code est correct ni qu'il fait ce que le modèle voulait. Un échec du sandbox serait que l'appel réseau réussisse malgré la règle d'absence de réseau. L'erreur du modèle (écrire le mauvais code) est distincte du travail du harness (imposer les frontières).

</details>

## Exercices en situation réelle

- [ ] Listez les outils que votre travail ou un système familier utilise. Identifiez un groupe de trois outils étroitement liés ou plus et esquissez comment ils pourraient être remplacés par un outil d'exécution de code. De quoi auriez-vous besoin pour avoir confiance dans le sandbox et faire ce changement ?
- [ ] Écrivez un programme simple d'analyse de données (filtrer un tableau, calculer un agrégat, trier). Imaginez que vous êtes le modèle. Combien d'allers-retours dans une boucle d'appels d'outils cela prendrait-il avec des outils séparés, et combien avec de l'exécution de code ?
- [ ] Demain : relisez l'article « Code Execution with MCP » et identifiez un choix de conception du sandbox (limite de ressources, frontière du système de fichiers, restriction réseau) et expliquez pourquoi cette frontière précise compte pour le cas d'usage de l'article.

## Pour aller plus loin

- [Billet : "Code Execution with MCP", Anthropic Engineering](https://www.anthropic.com/engineering/code-execution-with-mcp)
- [Ressources](../RESOURCES.md)

---

Ça ne passe pas ? Relisez la source primaire en haut de page, car cette leçon la condense et c'est dans la condensation que la compréhension s'échappe. Consultez le [glossaire](../GLOSSARY.md) pour tout terme qui vous a paru glissant.

Si c'est la leçon elle-même qui n'est pas claire plutôt que la matière, c'est un défaut : [ouvrez une issue](https://github.com/TokenCemetery/teach/issues).
