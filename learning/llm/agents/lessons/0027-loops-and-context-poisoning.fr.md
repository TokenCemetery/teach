---
title: "27. Boucles et empoisonnement du contexte"
description: "Deux modes de défaillance visibles dans une trajectoire, les boucles répétitives et l'empoisonnement silencieux du contexte, et comment repérer chacun"
type: lesson
---

# Leçon 27. Boucles et empoisonnement du contexte

**Lien avec la mission :** Diagnostiquer un agent défaillant à partir de sa trajectoire exige de reconnaître quand un agent est bloqué à répéter la même action et quand il s'appuie en silence sur une affirmation fausse, pour corriger la cause racine plutôt que d'ajouter des instructions.
**Source primaire :** [Billet : "Effective Context Engineering for AI Agents", Anthropic Engineering](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents)
**Prérequis :** [Leçon 26](0026-why-browser-agents-fail-differently.md), [Trajectoire](../GLOSSARY.md)

## Échauffement

1. ▢ Depuis la leçon 26 : pourquoi un agent piloté par l'écran échoue-t-il plus souvent qu'un agent à appels d'outils au raisonnement identique ?

<details markdown="1"><summary>Vérifier</summary>

Un agent piloté par l'écran observe à travers des pixels et agit à travers des coordonnées, qui sont des références fragiles que cassent les changements de mise en page, les états de chargement et les obstacles. Ces modes de défaillance sont structurels et persistent même avec un meilleur prompting.

</details>

2. ▢ Depuis la leçon 7 : si un harness ajoute un résultat d'outil à ses logs internes mais ne l'ajoute jamais au transcript, que sait le modèle de ce résultat ?

<details markdown="1"><summary>Vérifier</summary>

Rien. Le modèle ne voit que le transcript. Consigner dans un log ne suffit pas ; le résultat doit être ajouté au transcript pour que le modèle sache qu'il s'est produit au tour suivant.

</details>

## À savoir

### Boucles répétitives : quand un agent se retrouve bloqué

Une boucle répétitive, c'est quand un agent appelle le même outil avec des arguments identiques ou presque identiques tour après tour, alors que la tâche ne progresse pas. C'est bruyant et visible dans une trajectoire.

La cause sous-jacente est généralement l'une de deux :

D'abord, l'agent ne remarque pas qu'un résultat a contredit ou n'a pas soutenu son plan. Le modèle a émis une commande en attendant un certain résultat, en a reçu un différent ou nul, mais n'a pas mis à jour son modèle interne du monde. Au tour suivant, il essaie la même chose, en espérant un résultat différent.

Exemple : un agent veut créer un fichier `config.json` dans un répertoire. L'appel d'outil échoue avec « permission denied ». Le harness ajoute cette erreur. Mais au tour suivant, le modèle appelle le même outil avec le même chemin, comme si l'erreur ne s'était jamais produite. Le raisonnement du modèle était quelque chose comme « je vais essayer de créer le fichier », et quand cela a renvoyé une erreur, il n'est pas passé à « je devrais essayer un autre chemin ou demander la permission ». C'est une défaillance de raisonnement rendue visible par la répétition.

Ensuite, les conditions d'arrêt du harness sont trop lâches. La boucle continue de tourner parce qu'aucune condition ne s'est déclenchée pour l'arrêter. Avec des gardes serrées sur le nombre d'erreurs (leçon 6), la boucle sort après quelques tentatives échouées et expose l'échec pour le diagnostic. Avec des gardes lâches, la boucle continue, répétant dix ou vingt fois la même action en échec avant de s'arrêter enfin.

Comment repérer une boucle répétitive dans une trajectoire :

1. Chercher des tours consécutifs avec le même nom d'outil.
2. Comparer les arguments : sont-ils identiques ou presque identiques ?
3. Vérifier les résultats : sont-ils identiques, inchangés ou tous des échecs ?
4. Chercher du texte de raisonnement répété : le modèle emploie-t-il la même formulation et le même raisonnement sur plusieurs tours ?

Si les trois premières vérifications sont vraies, l'agent est dans une boucle répétitive. Un texte de raisonnement répété (vérification 4) le confirme, mais n'est pas requis.

### Empoisonnement du contexte : quand des affirmations fausses deviennent la vérité de référence

L'empoisonnement du contexte est différent. Contrairement à une boucle répétitive, bruyante et visible, l'empoisonnement est silencieux : le modèle énonce une fois quelque chose de faux ou d'halluciné, puis chaque tour suivant le traite comme un fait établi.

Voici comment cela se produit :

Au tour cinq, le modèle dit : « J'ai consulté la base de données et trouvé que l'identifiant du client est 12345. » Mais aucun appel d'outil n'a récupéré ce fait. Rien dans aucun résultat d'outil précédent ne disait l'identifiant du client. Le modèle l'a inventé, ou mal retenu, ou deviné d'après un motif.

Cette affirmation est ajoutée au transcript comme n'importe quoi d'autre. Elle ressemble à une vérité de référence : elle est là, dans l'historique de la conversation, énoncée comme un fait.

Au tour six, le modèle s'appuie dessus : « Je vais maintenant chercher le compte du client 12345. » Il appelle un outil avec cet identifiant. L'outil peut échouer (« customer 12345 does not exist »), ou pire, réussir et agir sur le mauvais client.

Au tour sept, le modèle s'est engagé plus loin : « Je vois que le compte du client 12345 affiche un solde de... » et la cascade continue.

Au tour quinze, vous lisez la trajectoire et voyez une énorme chaîne de raisonnements et de décisions, tous ancrés sur l'affirmation fausse que l'identifiant du client est 12345. Le modèle n'est pas stupide. Le modèle est cohérent : le transcript dit que l'identifiant du client est 12345, donc le modèle raisonne à partir de cela. Mais le transcript est empoisonné.

Pourquoi c'est différent d'un argument d'outil halluciné (leçon 28) : quand un modèle invente un argument de fonction comme un chemin de fichier, l'outil échoue généralement avec une erreur explicite (« file not found »). L'empoisonnement est pire parce qu'il n'est souvent pas attrapé immédiatement. Une affirmation fausse en langage naturel peut rester dans le transcript sans être contestée, et le modèle s'appuiera dessus.

Comment repérer l'empoisonnement dans une trajectoire :

1. Chercher un tour où le modèle énonce un fait précis (un nombre, un nom, une date, un identifiant) avec une grande assurance et sans réserve.
2. Remonter : un appel d'outil ou un résultat d'outil antérieur soutenait-il réellement cette affirmation ? Ou le modèle l'a-t-il énoncée de nulle part ?
3. Si elle n'était pas étayée, redescendre : des tours ultérieurs dépendent-ils de cette affirmation ? Des appels d'outils ultérieurs utilisent-ils cette valeur comme argument ?
4. Si oui sur les deux points, le contexte est empoisonné.

La discipline de diagnostic que cette leçon construit : une boucle se diagnostique en regardant ce qui se répète ; l'empoisonnement se diagnostique en remontant une affirmation fausse jusqu'à son origine et en la suivant jusqu'à ses conséquences.

### Pourquoi la dégradation du contexte aggrave l'empoisonnement

La dégradation du contexte (leçon 11) est le problème plus large : à mesure que le transcript grandit, les anciens tours deviennent moins pertinents, l'attention du modèle se déplace et la précision se dégrade. La dégradation du contexte arrive à toute longue exécution d'agent, même saine.

L'empoisonnement est plus grave. Une seule affirmation fausse dans le transcript peut ancrer tout le raisonnement en aval, et si l'affirmation est enfouie parmi des dizaines de tours, elle est difficile à repérer. Le modèle ne peut pas facilement rejeter une affirmation déjà présente dans son propre transcript ; il la traite plutôt comme un fait établi.

L'atténuation est à la fois diagnostique et préventive :

- Lire attentivement les trajectoires et guetter les affirmations non étayées que le modèle fait en langage naturel.
- En concevant les outils, leur faire renvoyer en écho ce qui a été résolu : au lieu d'un simple « success », renvoyer « successfully updated customer ID 67890 », pour que le modèle confirme la valeur réelle.
- Utiliser des conditions d'arrêt et des comptes d'erreurs serrés pour que les boucles sortent vite et empêchent les cascades de mauvaises décisions bâties sur un empoisonnement précoce.

## Pratique

1. ▢ Vous lisez la trajectoire d'un agent et voyez le même appel d'outil, `get_user_by_email(email="bob@example.com")`, répété aux tours 3, 5, 7 et 9. À chaque fois, le résultat est « user not found ». Au tour 10, le modèle appelle `send_email(recipient="bob@example.com")`. Est-ce une boucle répétitive ?

<details markdown="1"><summary>Vérifier</summary>

Non, ce n'est pas une boucle répétitive. L'agent appelle de façon répétée le même outil de recherche et obtient le même échec, mais il a ensuite divergé et appelé un autre outil (send_email). L'agent a bien adapté sa stratégie après l'échec de la recherche. Une boucle répétitive serait que le modèle continue d'appeler get_user_by_email aux tours 10, 11, 12. C'est plus proche d'un empoisonnement du contexte : l'agent a peut-être fait une hypothèse fausse au tour 2 (comme « j'ai l'e-mail de l'utilisateur ») qui n'a jamais été confirmée, et agit maintenant dessus. Lisez tout le contexte de la trajectoire pour identifier si le tour 2 ou un tour antérieur a fait une affirmation non étayée sur l'e-mail de Bob.

</details>

2. ▢ Un agent écrit un fichier. Au tour trois, il appelle write_file(path="output.txt", content="...") et reçoit l'erreur « permission denied ». Au tour quatre, le modèle dit « Je vais essayer une approche différente » et appelle create_directory(path="/tmp/") qui réussit. Puis au tour cinq, il appelle write_file(path="/tmp/myfile.txt", content="..."). Est-ce une boucle répétitive ?

<details markdown="1"><summary>Indice</summary>

Regardez si le modèle appelle le même outil avec les mêmes arguments, et si son raisonnement a changé d'un tour à l'autre.

</details>

<details markdown="1"><summary>Vérifier</summary>

Non, ce n'est pas une boucle répétitive. Même si l'agent a rencontré une erreur, il s'est adapté : il a changé son raisonnement (« essayer une approche différente »), appelé un autre outil et changé le chemin de fichier dans la tentative d'écriture. La stratégie du modèle a évolué. Une boucle répétitive montrerait le même appel write_file avec « output.txt » répété sans changement. Cet agent a montré un cheminement raisonnable de résolution de problème, même si l'objectif final (écrire à l'emplacement d'origine) a été abandonné.

</details>

3. ▢ Vous lisez une trajectoire où, au tour 12, le modèle énonce « La clé d'API de ce service est sk-1234567890 ». Vous cherchez dans les tours 1 à 11 et ne trouvez aucun appel d'outil qui ait renvoyé cette clé. Vous cherchez dans les tours 13 à 20 et constatez que les tours 15, 17 et 19 utilisent tous cette clé dans des appels d'API. Que s'est-il passé ?

    - a) Le modèle a raisonné correctement et déduit la clé du contexte
    - b) Le contexte est empoisonné : une affirmation non étayée ancre maintenant plusieurs appels d'outils en aval
    - c) Le modèle est dans une boucle répétitive, qui appelle le même outil d'API de façon répétée
    - d) Le harness n'a pas ajouté un résultat d'outil qui contenait la clé

<details markdown="1"><summary>Vérifier</summary>

**b)** Le contexte est empoisonné. Le modèle a énoncé un fait (la clé d'API) sans aucun appel d'outil antérieur pour l'étayer, et plusieurs tours ultérieurs dépendent de cette affirmation. C'est la définition de manuel de l'empoisonnement : une affirmation non étayée devient la base du raisonnement en aval. On ne peut pas dire, d'après la trajectoire seule, si le harness a omis d'ajouter un résultat (d) ou si le modèle a halluciné ; dans les deux cas, le transcript est désormais empoisonné. **a)** est faux parce qu'une déduction n'est pas la même chose qu'une vérification de la vérité de référence. **c)** est faux ; ce n'est pas une boucle répétitive parce que les appels d'outils ne sont pas identiques et que le modèle ne répète pas la même action.

</details>

4. ▢ Un collègue vous montre la trajectoire d'un agent défaillant. Les trois premiers tours ont réussi. Au tour quatre, le modèle est coincé dans une boucle qui appelle list_files(directory="/data") de façon répétée sans changement. Le texte de raisonnement du modèle dit « Je dois trouver le fichier cible ». Quelle est la cause racine la plus probable : une erreur de logique dans le raisonnement du modèle, ou une condition d'arrêt serrée qui devrait autoriser plus de tours ?

<details markdown="1"><summary>Vérifier</summary>

C'est une erreur de logique dans le raisonnement du modèle, pas un problème de condition d'arrêt. La condition d'arrêt n'est pas assez serrée (la boucle se répète), mais la correction n'est pas de la desserrer davantage. Le problème est que le modèle a appelé le même outil de façon répétée sans changer l'argument ni le raisonnement. Desserrer la condition d'arrêt ne ferait que lui permettre de répéter davantage. La correction consiste à diagnostiquer pourquoi le modèle n'a pas compris le résultat du premier appel à list_files, ou ne savait pas comment poursuivre. La condition d'arrêt devrait être resserrée pour sortir après une ou deux répétitions échouées, en exposant le problème au diagnostic humain plutôt que de le laisser se répéter sans fin.

</details>

## Exercices en situation réelle

- [ ] Trouvez la trajectoire d'un agent en ligne (dans une documentation, un dépôt GitHub ou un billet de blog). Lisez-la et identifiez : montre-t-elle des boucles répétitives ? Montre-t-elle de l'empoisonnement du contexte ? Écrivez un paragraphe décrivant ce que vous avez trouvé et comment vous l'avez repéré.

- [ ] Faites exécuter à un agent une tâche dont vous attendez qu'elle échoue. Examinez délibérément la trajectoire à la recherche d'affirmations non étayées que le modèle fait en langage naturel (affirmations non soutenues par des résultats d'outils antérieurs). Pour chacune, notez ce qui se passerait si l'agent poursuivait en s'appuyant sur cette affirmation fausse.

- [ ] Demain : concevez un outil qui aiderait à prévenir l'empoisonnement du contexte. Il pourrait renvoyer en écho les valeurs résolues, ajouter des sommes de contrôle, inclure des horodatages ou valider par rapport à un ensemble connu. Écrivez un paragraphe décrivant la conception de votre outil et expliquez comment il rend les affirmations empoisonnées plus faciles à repérer dans une trajectoire.

## Pour aller plus loin

- [Billet : "Effective Context Engineering for AI Agents", Anthropic Engineering](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents)
- [Ressources](../RESOURCES.md)

---

Ça ne passe pas ? Relisez la source primaire en haut de page, car cette leçon la condense et c'est dans la condensation que la compréhension s'échappe. Consultez le [glossaire](../GLOSSARY.md) pour tout terme qui vous a paru glissant.

Si c'est la leçon elle-même qui n'est pas claire plutôt que la matière, c'est un défaut : [ouvrez une issue](https://github.com/TokenCemetery/teach/issues).
