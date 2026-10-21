---
title: "28. Erreurs d'outils en cascade et arguments hallucinés"
description: "Une erreur d'outil qui mène à de mauvaises décisions et à une spirale de confusion, et des arguments bien typés mais faux que les schémas ne peuvent pas attraper"
type: lesson
---

# Leçon 28. Erreurs d'outils en cascade et arguments hallucinés

**Lien avec la mission :** Identifier les défaillances en cascade et les arguments hallucinés dans une trajectoire permet de diagnostiquer les défaillances d'agents à leur véritable origine, en brisant la chaîne avant qu'elle ne s'emballe, plutôt que de rafistoler des symptômes en aval.
**Source primaire :** [Billet : "Building Effective Agents", Anthropic Engineering](https://www.anthropic.com/engineering/building-effective-agents)
**Prérequis :** [Leçon 27](0027-loops-and-context-poisoning.md)

## Échauffement

1. ▢ Depuis la leçon 27 : quelle est la différence entre une boucle répétitive et l'empoisonnement du contexte ?

<details markdown="1"><summary>Vérifier</summary>

Une boucle répétitive est bruyante : l'agent appelle le même outil avec les mêmes arguments de façon répétée, sans progresser. L'empoisonnement est silencieux : le modèle énonce une fois un fait faux ou halluciné, et chaque tour suivant le traite en silence comme une vérité établie.

</details>

2. ▢ Depuis la leçon 4 : que valide le schéma JSON d'un outil ?

<details markdown="1"><summary>Vérifier</summary>

Un schéma valide la structure et le type d'un argument : que les champs obligatoires sont présents, que les valeurs correspondent au type déclaré (chaîne, nombre, booléen), que les listes ont le bon type d'élément, et que des contraintes comme enum ou minLength sont respectées. Il ne valide pas si la valeur est vraie ni si elle renvoie à quelque chose de réel.

</details>

## À savoir

### Défaillances en cascade : une erreur en entraîne une autre

Une défaillance en cascade, c'est quand une erreur d'outil mène à une décision de suivi incorrecte, qui mène à une autre erreur, et ainsi de suite en s'éloignant de la tâche. Chaque défaillance aggrave la confusion au lieu de la résoudre.

Voici un exemple pas à pas :

Tour 2 : l'agent appelle search_files(directory="/config") pour trouver un fichier de configuration. Le répertoire n'existe pas. L'outil renvoie une erreur : « directory not found ».

Le harness ajoute cette erreur au transcript. Jusqu'ici, tout va bien.

Tour 3 : le modèle lit l'erreur et décide : « Le répertoire personnel standard n'existe pas. Je dois être dans un autre environnement. Essayons /etc/config à la place. » C'est un raisonnement raisonnable à partir d'une information incomplète. Le modèle appelle search_files(directory="/etc/config").

Tour 4 : la recherche réussit, mais renvoie des résultats qui ne correspondent pas à ce que l'agent cherche. Le modèle, déjà engagé sur le chemin /etc/config depuis le tour 3, décide : « Ces résultats sont assez proches. J'utiliserai le premier. » Le modèle a maintenant le mauvais fichier.

Tour 5 : l'agent lit le mauvais fichier. Le contenu ne correspond pas à ce qu'il attend. Au lieu de reconnaître l'écart, le modèle décide : « Le format du fichier a dû changer. Je vais l'analyser de façon plus tolérante. » L'agent continue, toujours bâti sur de mauvaises fondations.

Tours 6 à N : chaque décision aggrave l'erreur d'origine. L'agent raisonne maintenant à partir d'une base fausse et ne peut pas se rétablir sans revenir nettement en arrière.

La raison pour laquelle les défaillances en cascade se produisent : quand un outil renvoie une erreur, le modèle doit faire une hypothèse sur la raison. Le répertoire manque-t-il ? Est-ce une erreur de permission ? La syntaxe du chemin est-elle fausse ? Le modèle fait une supposition et poursuit. Si la supposition est fausse, l'appel d'outil suivant est bâti sur cette mauvaise hypothèse. Et la chaîne descend à partir de là.

La garde sur le nombre d'erreurs de la leçon 6 finira par arrêter la boucle, mais elle l'arrête après que la cascade a grandi, pas à l'origine.

### Arguments hallucinés : bien typés mais faux

Un argument halluciné, c'est quand le modèle invente une valeur d'argument d'outil d'apparence plausible mais factuellement fausse. La valeur est bien formée et passe la validation du schéma, mais elle ne correspond tout simplement à rien de réel.

C'est différent d'une erreur de champ obligatoire manquant (leçons 3 à 5). Un champ manquant produit une erreur explicite de validation de schéma que le modèle peut voir et à laquelle il peut réagir. Un argument halluciné passe la validation en silence.

Exemples :

- Le modèle doit chercher un utilisateur par son nom d'utilisateur. Il appelle get_user(username="alice_smith"), mais le vrai nom d'utilisateur est « asmith ». Le schéma accepte la chaîne ; l'appel échoue en aval parce que le nom d'utilisateur n'existe pas.
- Le modèle doit appeler un endpoint d'API et invente le chemin : call_api(endpoint="/api/v2/users/search"). L'endpoint n'existe pas, mais il a l'air plausible. Le schéma le valide comme une chaîne ; l'appel HTTP échoue avec une erreur 404.
- On demande au modèle d'appeler une fonction par son nom et il invente un nom : call_function(name="validate_order"). La fonction n'existe pas, mais la chaîne est bien formée. L'appel n'échoue avec « function not found » qu'à l'exécution.

Pourquoi c'est pire qu'une erreur de validation de schéma : quand le schéma rejette quelque chose (champ manquant, mauvais type), le modèle reçoit un retour immédiat et peut le corriger. Quand un argument est bien typé mais faux, l'erreur survient en aval, souvent sous une forme cryptique (« user not found », « 404 not found », « function not found »). Le modèle ne comprend pas immédiatement que sa valeur inventée était le problème ; il peut plutôt blâmer le service (« la base d'utilisateurs est cassée ») ou l'environnement (« l'API ne tourne pas ») et prendre une mauvaise décision sur la base de ce mauvais diagnostic.

Si la défaillance en cascade de la section précédente commence par un argument halluciné, la cascade est pire : le modèle bâtit une chaîne de raisonnement sur une valeur qu'il a inventée sans savoir qu'il l'a inventée.

### Atténuations : validation et écho

L'atténuation principale consiste à faire échouer les arguments hallucinés plus vite et plus clairement, et à donner au modèle une visibilité sur ce qui s'est réellement passé.

**Valider par rapport à un ensemble connu** : si un outil prend un argument censé renvoyer à quelque chose de réel (un nom d'utilisateur, un nom de fonction, un endpoint), l'outil devrait valider que cela existe. Au lieu d'échouer en silence en aval, l'outil renvoie une erreur explicite : « user alice_smith not found; valid users are: alice_s, alice_brown, alicia_m ». Cela donne au modèle un retour immédiat et un ensemble d'options parmi lesquelles choisir.

**Renvoyer en écho la valeur résolue** : après la réussite d'un appel d'outil, ne renvoyez pas simplement « success ». Renvoyez ce sur quoi on a réellement agi. Exemple :

Au lieu de :

```text
Tool result: Success
```

Renvoyez :

```text
Tool result: Successfully updated order 12345. Order status is now CONFIRMED.
```

Ainsi, si l'argument du modèle était halluciné mais correspondait par hasard à quelque chose d'involontaire, l'écho rend l'écart visible. Le modèle voit « j'ai appelé avec l'identifiant de commande 12345, et l'outil a rapporté la mise à jour de la commande 12345 », et peut remarquer si les deux correspondent.

**Exiger une confirmation explicite pour les opérations à enjeux élevés** : si un appel d'outil va modifier des données ou entreprendre une action, faire demander par le harness au modèle de confirmer la valeur réelle avant d'exécuter. Le modèle voit « vous êtes sur le point de mettre à jour l'utilisateur username_alice_smith ; confirmez ? » et peut attraper une hallucination à ce moment-là.

### Défaillances en cascade dans la trajectoire

Quand vous lisez une trajectoire et repérez une cascade :

1. Identifiez la première erreur (tour N) : un outil renvoie un résultat inattendu ou une erreur.
2. Vérifiez le tour N+1 : quelle hypothèse le modèle a-t-il faite sur la raison de l'erreur ?
3. Redescendez : la décision suivante du modèle découle-t-elle de cette hypothèse ?
4. Si l'hypothèse était fausse, la cascade a commencé.

La leçon de diagnostic : l'erreur du tour N n'est pas le problème que vous devriez essayer de corriger en re-prompter. Le problème est le mauvais diagnostic de l'erreur du tour N par le modèle au tour N+1. Corrigez l'outil pour qu'il soit plus clair sur ce qui n'a pas marché, ou donnez au modèle de meilleures options pour gérer cette classe d'erreurs, ou resserrez les conditions d'arrêt pour que la cascade ne grandisse pas.

## Pratique

1. ▢ Un agent importe des données d'un fichier CSV. Au tour trois, il appelle parse_csv(filename="data.csv"). L'outil renvoie une erreur : « file not found ». Au tour quatre, le modèle dit « Le fichier doit être compressé. Je vais d'abord le décompresser » et appelle decompress(filename="data.csv.gz"). Cet outil échoue aussi avec « file not found ». Au tour cinq, le modèle essaie une autre interprétation de l'erreur : « Peut-être que le fichier est dans un sous-répertoire » et appelle search_for_file(pattern="data*"). Cela réussit et trouve « data_backup.csv ». Au tour six, il analyse le fichier de sauvegarde, qui a d'autres colonnes que prévu, et l'analyse réussit mais produit une sortie absurde. Est-ce une défaillance en cascade, et où a-t-elle pris son origine ?

<details markdown="1"><summary>Vérifier</summary>

Oui, c'est une défaillance en cascade. Elle a pris son origine au tour 3, quand le parse_csv initial a échoué. Le modèle a mal diagnostiqué l'erreur : il a supposé que le fichier était compressé ou déplacé, alors que le vrai problème était probablement simplement le nom de fichier ou le chemin. À chaque tour, le modèle a fait une autre hypothèse, et chaque hypothèse a mené à une autre action, dont aucune n'a corrigé le problème sous-jacent. Au tour 6, l'agent travaille avec le mauvais fichier (data_backup.csv au lieu de data.csv), et la sortie absurde en est la conséquence. La correction n'est pas un meilleur raisonnement du modèle ; c'est de rendre le message d'erreur initial plus clair. L'outil devrait renvoyer « file data.csv not found in current directory; files found: data_backup.csv, old_data.csv ». Avec cette information, le modèle aurait pu choisir explicitement le fichier de sauvegarde au tour 4, au lieu de passer par les tours 4 et 5 de mauvais diagnostic.

</details>

2. ▢ Un agent met à jour des fiches clients. Au tour deux, le modèle appelle update_customer(customer_id=987654, status="inactive"). Le schéma accepte l'entier et la chaîne. L'outil renvoie « customer not found ». Au tour trois, le modèle, perplexe, appelle list_customers(). Cela renvoie une liste de tous les clients. Au tour quatre, le modèle choisit le premier client de la liste et appelle update_customer(customer_id=100001, status="inactive"). Cela réussit. Mais l'agent devait mettre à jour le client 987654, pas 100001. Pourquoi l'argument halluciné du tour deux n'a-t-il pas produit une erreur évidente à laquelle le modèle aurait pu réagir ?

<details markdown="1"><summary>Indice</summary>

Pensez à la différence entre une erreur de validation de schéma et le comportement d'exécution d'un outil face à une valeur bien typée mais invalide.

</details>

<details markdown="1"><summary>Vérifier</summary>

Le schéma n'a pas rejeté l'argument parce que 987654 est un entier valide. L'outil l'a accepté et l'a cherché, pour échouer à l'exécution avec « customer not found ». Le message d'erreur était clair (« customer not found »), mais le modèle l'a mal interprété : au lieu de conclure « le client 987654 n'existe pas, je dois trouver le bon identifiant », il a conclu « quelque chose cloche dans ma façon d'interroger, essayons une approche différente ». Une meilleure conception de l'outil renverrait : « customer 987654 not found; customers exist in the range 100001 to 150000 ». Cela rend l'écart explicite et donne au modèle une plage concrète avec laquelle travailler, ce qui empêche la cascade.

</details>

3. ▢ Vous construisez un outil qui prend un chemin de fichier comme argument. Le schéma dit que le chemin doit être une chaîne. Vous vous attendez à ce que les modèles inventent parfois des chemins qui n'existent pas. Lequel de ces choix de conception empêcherait le mieux que des arguments hallucinés ne créent des défaillances en cascade ?

    - a) Accepter n'importe quel chemin en chaîne et échouer avec un « file error » générique quand le chemin n'existe pas
    - b) Valider le chemin par rapport à une liste de répertoires autorisés ; rejeter les chemins hors de la liste avec une erreur claire
    - c) Accepter n'importe quel chemin et renvoyer un message de succès même si le fichier n'existe pas, pour que le modèle croie que l'opération a réussi
    - d) Exiger que le modèle passe deux arguments : le chemin et un booléen confirmant que le chemin est correct

<details markdown="1"><summary>Vérifier</summary>

**b)** Valider par rapport à une liste de répertoires autorisés et rejeter les chemins invalides avec une erreur claire. Cela fait échouer les chemins hallucinés vite et explicitement, en donnant au modèle un retour immédiat. Le modèle peut alors choisir dans la liste autorisée. **a)** laisse quand même la cascade grandir parce que l'erreur est générique et n'aide pas le modèle à comprendre ce qui n'a pas marché. **c)** est dangereux ; cela masque le problème et mène à des cascades parce que le modèle croit avoir réussi alors que non. **d)** exige de la logique supplémentaire dans le harness et ne résout pas le problème ; un modèle peut halluciner à la fois le chemin et sa confirmation.

</details>

4. ▢ Un agent doit récupérer des données d'une API. Au tour deux, il appelle fetch_api(endpoint="/api/v1/customers/123"). L'endpoint n'existe pas, et l'outil renvoie une erreur 404. Au tour trois, le modèle dit « Le serveur d'API doit être en panne » et appelle check_service_health(). Cela renvoie « service is up and responding ». Au tour quatre, le modèle dit « L'API a dû changer. Essayons sans le numéro de version » et appelle fetch_api(endpoint="/api/customers/123"). Cela échoue aussi avec une erreur 404. Quel changement de conception du premier outil aurait empêché la cascade ?

<details markdown="1"><summary>Vérifier</summary>

Le premier appel d'outil aurait dû renvoyer plus d'information que simplement « 404 not found ». Il pourrait renvoyer : « endpoint /api/v1/customers/123 not found (404); valid endpoints include: /api/v2/customers/{id}, /api/v2/orders/{id} ». Avec cette information, le modèle aurait immédiatement compris que c'était le numéro de version qui était faux, pas le service, et aurait pu ajuster l'endpoint au tour 3 au lieu de passer par les tours 3 et 4 de cascade. La cascade s'est produite parce que le message d'erreur n'expliquait pas le vrai problème.

</details>

## Exercices en situation réelle

- [ ] Trouvez la trajectoire d'un agent qui montre un échec. Lisez-la et identifiez : y a-t-il une chaîne de décisions en cascade, où chaque décision aggrave la confusion ? Si oui, à quel tour la cascade a-t-elle pris son origine ? Qu'aurait changé un message d'erreur plus clair ?

- [ ] Concevez un outil (choisissez n'importe quel outil avec lequel vous travaillez ou que vous avez conçu). Écrivez le message d'erreur que l'outil renvoie actuellement dans un cas d'échec courant. Réécrivez-le maintenant pour y inclure : ce qui n'allait pas, ce qui était attendu et quelles sont les alternatives valides. Comment ce message d'erreur plus clair changerait-il la capacité d'un modèle à diagnostiquer le problème ?

- [ ] Demain : construisez un petit harness de test qui appelle un outil avec un argument halluciné (une valeur que l'outil ne reconnaît pas). Observez le message d'erreur que l'outil renvoie. Modifiez ensuite l'outil pour valider par rapport à un ensemble connu et renvoyer une erreur plus claire. Relancez le même argument halluciné et comparez les deux messages d'erreur. Écrivez un paragraphe décrivant comment l'erreur plus claire changerait le diagnostic de la défaillance par un agent.

## Pour aller plus loin

- [Billet : "Building Effective Agents", Anthropic Engineering](https://www.anthropic.com/engineering/building-effective-agents)
- [Ressources](../RESOURCES.md)

---

Ça ne passe pas ? Relisez la source primaire en haut de page, car cette leçon la condense et c'est dans la condensation que la compréhension s'échappe. Consultez le [glossaire](../GLOSSARY.md) pour tout terme qui vous a paru glissant.

Si c'est la leçon elle-même qui n'est pas claire plutôt que la matière, c'est un défaut : [ouvrez une issue](https://github.com/TokenCemetery/teach/issues).
