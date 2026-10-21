---
title: "16. Plan puis exécution et décomposition"
description: "La planification explicite en amont comme alternative à ReAct, quand l'utiliser et comment gérer la replanification"
type: lesson
---

# Leçon 16. Plan puis exécution et décomposition

**Lien avec la mission :** Pour choisir entre un prompt unique, un workflow fixe et un agent pour une tâche donnée, il faut reconnaître quand la structure supplémentaire d'un plan explicite vaut son coût et quand la flexibilité de ReAct est moins chère.
**Source primaire :** [Billet : "Building Effective Agents", Anthropic Engineering](https://www.anthropic.com/engineering/building-effective-agents)
**Prérequis :** [Leçon 15](0015-react-interleaving-reasoning-and-acting.md)

## Échauffement

1. ▢ Dans ReAct, que se passe-t-il après l'exécution d'un appel d'outil et l'ajout du résultat au transcript par le harness ?

<details markdown="1"><summary>Vérifier</summary>

Le tour suivant du modèle reçoit le transcript, y compris l'appel d'outil et son résultat. Le modèle peut alors émettre un nouveau raisonnement qui réagit à ce que l'outil a réellement renvoyé, plutôt que de s'en tenir à un plan préétabli.

</details>

2. ▢ Décrivez un scénario où l'adaptation pas à pas de ReAct est un avantage sur un plan rigide établi en amont.

<details markdown="1"><summary>Vérifier</summary>

Tout scénario où l'environnement peut surprendre l'agent : une recherche ne renvoie rien (pas les données attendues), un outil échoue, un utilisateur donne un retour qui contredit les hypothèses, ou une nouvelle information arrive en cours de tâche. Dans ces cas, ReAct permet au modèle d'observer la surprise et de s'adapter, alors qu'un plan rigide établi en amont exécuterait aveuglément les étapes d'origine et échouerait ou produirait des résultats faux.

</details>

## À savoir

### Planification explicite et décomposition

Plan puis exécution est une approche distincte de ReAct. Au lieu d'entrelacer raisonnement et action, la première étape de l'agent est de produire une liste explicite et ordonnée de sous-tâches ou d'actions. Le modèle (ou un planificateur distinct) produit un plan en langage naturel ou sous forme structurée. Le harness exécute ensuite le plan étape par étape. Si la replanification est prise en charge, le harness peut demander un nouveau plan si une étape échoue.

La décomposition est l'idée générale derrière cela : découper une grande tâche ambiguë en plusieurs tâches plus petites et bien définies. Une sous-tâche plus petite est plus facile à exécuter correctement pour le modèle, et plus facile à vérifier pour un humain. Que la décomposition se fasse explicitement (avec un plan écrit) ou implicitement (dans le raisonnement de ReAct à chaque étape), le principe est le même.

### Quand la planification explicite justifie son coût

Un plan explicite occupe de la place dans le transcript et exige un tour de modèle supplémentaire (au moins un) avant qu'aucune action ne s'exécute. C'est de la surcharge. Quand vaut-elle d'être payée ?

**Revue humaine avant l'exécution :** si une tâche comporte des enjeux élevés (appeler une API qui coûte de l'argent, envoyer un e-mail, supprimer des données), un humain peut lire le plan avant que le harness n'exécute le moindre outil. L'humain peut rejeter le plan, demander des modifications ou l'approuver en confiance. À l'inverse, ReAct exécute la première action avant qu'un humain ait de la visibilité sur ce qui va se passer. Pour les tâches où l'approbation humaine est requise ou réduit le risque, un plan explicite est un bon compromis.

**Tâches en plusieurs étapes où une mauvaise action coûte cher :** si chaque étape est coûteuse à annuler ou présente un risque élevé, s'engager sur un plan en amont et le faire relire par un humain avant l'exécution réduit le risque d'erreurs coûteuses. Une tâche exploratoire dont les étapes sont bon marché (lire des données, faire des requêtes qui ne coûtent rien) n'a pas besoin de cette surcharge.

**Tâches à structure claire et stable :** certaines tâches se décomposent en une séquence évidente qui ne change pas : « Télécharger le fichier A, l'analyser, le transformer, téléverser le résultat. » Si les étapes ont peu de chances de changer en cours d'exécution, les écrire en amont et les exécuter est plus simple et moins cher que de raisonner de nouveau sur chaque étape.

### Le problème du plan périmé et la replanification

Voici le risque : le plan a été fait avant qu'aucun outil ne s'exécute. Si l'étape 1 devait trouver un fichier mais qu'il n'existe pas, le plan de l'étape 2 suppose que le fichier est là. L'étape 2 échouera ou produira des résultats faux. Le harness a alors deux choix : continuer aveuglément à exécuter le plan périmé (et échouer probablement) ou déclencher la replanification (demander au modèle d'émettre un nouveau plan compte tenu du nouvel état).

La replanification n'est pas gratuite : elle coûte un tour de modèle de plus, et la trajectoire montre alors plusieurs étapes de plan, ce qui consomme du contexte. Mais la replanification est souvent moins chère que ReAct pour les tâches très structurées, parce que le modèle peut réfléchir rapidement au nouveau chemin au lieu de raisonner pas à pas.

Si la replanification n'est pas prise en charge, un harness de plan puis exécution échouera, silencieusement ou bruyamment, quand la réalité ne correspond pas au plan. C'est pourquoi « prenez-vous en charge la replanification ? » est une question de conception clé pour les agents de plan puis exécution.

### Décomposition sans planification explicite

Notez que la décomposition et la planification explicite sont deux idées distinctes. Un agent peut décomposer des tâches implicitement, par un raisonnement à la ReAct à chaque étape. Le modèle raisonne « pour résoudre cela, je dois faire X, puis Y, puis Z », puis fait X, observe le résultat, raisonne de nouveau et passe à Y. C'est de la décomposition implicite. Un plan explicite écrit cette liste « X, Y, Z » comme un artefact structuré avant le début de l'exécution.

Pour beaucoup de tâches, la décomposition implicite (ReAct) est plus simple et plus robuste. Utilisez la planification explicite quand la surcharge (revue humaine, clarté, structure) vaut le coût.

### Comparer les trois schémas

L'act-only est le plus simple mais le plus difficile à déboguer. ReAct ajoute raisonnement et observation, ce qui le rend visible et adaptatif. Plan puis exécution ajoute une structure en amont qui peut être relue avant l'exécution de toute action, au prix d'un tour de modèle supplémentaire et d'un risque de péremption si les hypothèses du plan se brisent.

Choisissez selon votre tâche et vos contraintes :

- Tâche exploratoire courte, sans enjeu élevé ? Utilisez ReAct.
- Tâche aux étapes claires qui ont peu de chances de changer ? Utilisez plan puis exécution.
- Tâche où un humain doit relire avant le début de l'exécution ? Utilisez plan puis exécution avec un point d'approbation.
- Tâche où les étapes sont coûteuses et où les échecs coûtent cher ? Utilisez plan puis exécution avec prise en charge de la replanification.

## Pratique

1. ▢ Une tâche consiste à « déposer une plainte auprès de la ville, vérifier qu'elle a été reçue et prévenir l'utilisateur ». Cela implique de remplir un formulaire (pas gratuit à refaire), de vérifier un e-mail de confirmation et d'envoyer un e-mail. La planification explicite ou ReAct conviendrait-elle mieux pour cette tâche ? Pourquoi ?

<details markdown="1"><summary>Vérifier</summary>

La planification explicite convient mieux. Les étapes sont claires et stables : remplir le formulaire, vérifier la confirmation, envoyer l'e-mail. Il n'y a aucune raison de s'attendre à ce que cette séquence change en cours d'exécution. Un humain devrait relire le plan avant que le formulaire ne soit rempli, puisque cette étape n'est pas facile à annuler. ReAct fonctionnerait mais exécuterait l'étape de remplissage du formulaire avant qu'un humain puisse relire, ce qui ajoute du risque.

</details>

2. ▢ Vous construisez un agent qui enquête sur la raison pour laquelle le compte d'un utilisateur est verrouillé. L'agent peut vérifier l'état du compte, chercher dans les logs des échecs de connexion, chercher un indicateur de sécurité ou interroger les tickets de support, selon ce qu'il trouve. La planification explicite ou ReAct conviendrait-elle mieux ?

<details markdown="1"><summary>Indice</summary>

Demandez-vous si la séquence d'étapes est connue à l'avance ou si elle dépend de ce que renvoient les étapes précédentes.

</details>

<details markdown="1"><summary>Vérifier</summary>

ReAct convient mieux. Les étapes dépendent de ce que l'agent trouve à chaque stade. Si l'état du compte montre un indicateur de sécurité, l'étape suivante est de le vérifier. S'il montre une autre erreur, l'étape suivante est différente. La séquence ne peut pas être écrite en amont. Le raisonnement et l'observation pas à pas de ReAct sont plus naturels que d'essayer de planifier toutes les branches possibles.

</details>

3. ▢ Laquelle des propositions suivantes décrit le mieux quand la replanification devient nécessaire dans un agent de plan puis exécution ?

    - a) Chaque fois que l'agent rencontre un appel d'outil avec un paramètre que le plan ne mentionnait pas.
    - b) Quand un appel d'outil échoue ou renvoie des données inattendues qui contredisent une hypothèse du plan d'origine.
    - c) Chaque fois que l'utilisateur change d'avis sur la tâche.
    - d) Après chaque appel d'outil, pour que le plan reste à jour.

<details markdown="1"><summary>Vérifier</summary>

**b)** La replanification est déclenchée par de vrais échecs ou de vraies surprises : un outil n'a rien renvoyé alors que le plan attendait des données, un appel d'API a échoué, ou une recherche n'a pas trouvé ce qui était attendu. a) est faux, les outils ont souvent des paramètres que le plan n'a pas listés ; ce n'est pas une erreur. c) est faux, les changements de l'utilisateur sont une question au niveau de la tâche, pas propre au plan puis exécution face à ReAct. d) est faux, replanifier après chaque étape va à l'encontre du but d'avoir un plan et est inefficace.

</details>

4. ▢ Le plan explicite d'un agent est « Étape 1 : chercher l'entrée de l'utilisateur. Étape 2 : résumer les résultats. Étape 3 : comparer le résumé à la question d'origine de l'utilisateur. » Après l'étape 1, la recherche ne renvoie aucun résultat. Le harness ne prend pas en charge la replanification. Que va-t-il probablement se passer ?

<details markdown="1"><summary>Vérifier</summary>

L'étape 2 (résumer les résultats) échouera ou produira une sortie fausse parce qu'il n'y a aucun résultat à résumer. L'agent se bloquera, renverra une erreur ou produira un résumé de rien. Le harness n'aura aucun moyen de bifurquer : il était engagé sur le plan dès le départ. C'est le coût d'un harness de plan puis exécution sans prise en charge de la replanification. La correction consiste soit à ajouter la replanification (demander au modèle de faire un nouveau plan quand l'étape 1 échoue), soit à passer à ReAct, où le modèle raisonnerait après le résultat de l'étape 1 et déciderait d'essayer une autre recherche.

</details>

## Exercices en situation réelle

- [ ] Prenez une tâche en plusieurs étapes que vous faites régulièrement (par exemple traiter une commande, enquêter sur un incident, relire un document pour la conformité). Écrivez les étapes que vous suivez réellement. Les étapes se déroulent-elles toujours dans le même ordre, ou l'ordre dépend-il de ce que vous trouvez à chaque étape ? Si l'ordre est fixe, c'est un candidat pour plan puis exécution avec approbation explicite. Si l'ordre est adaptatif, c'est un candidat pour ReAct.
- [ ] Construisez un petit agent de plan puis exécution pour une tâche à séquence fixe (par exemple télécharger un fichier, l'analyser, le transformer, le téléverser). Lancez-le cinq fois sur des entrées différentes et lisez les trajectoires. L'agent a-t-il déjà échoué parce que le plan d'origine ne correspondait pas à la réalité ? Si oui, ajoutez une porte de replanification après les appels d'outils susceptibles d'échouer.
- [ ] Demain : trouvez un agent existant que vous avez construit ou utilisé. Classez-le comme act-only, ReAct ou plan puis exécution d'après sa trajectoire. Écrivez une note d'une phrase sur la raison pour laquelle ce schéma convient à la tâche.

## Pour aller plus loin

- [Billet : "Building Effective Agents", Anthropic Engineering](https://www.anthropic.com/engineering/building-effective-agents)
- [Ressources](../RESOURCES.md)

---

Ça ne passe pas ? Relisez la source primaire en haut de page, car cette leçon la condense et c'est dans la condensation que la compréhension s'échappe. Consultez le [glossaire](../GLOSSARY.md) pour tout terme qui vous a paru glissant.

Si c'est la leçon elle-même qui n'est pas claire plutôt que la matière, c'est un défaut : [ouvrez une issue](https://github.com/TokenCemetery/teach/issues).
