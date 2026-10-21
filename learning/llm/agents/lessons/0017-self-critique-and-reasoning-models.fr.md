---
title: "17. L'auto-critique et ce que les modèles de raisonnement ont changé"
description: "La boucle de réflexion comme étape explicite, ses coûts, et comment le raisonnement interne étendu influe sur le moment de l'utiliser"
type: lesson
---

# Leçon 17. L'auto-critique et ce que les modèles de raisonnement ont changé

**Lien avec la mission :** Pour diagnostiquer un agent défaillant, il faut reconnaître quand ajouter une étape de réflexion (une boucle distincte qui évalue les échecs passés et reporte les leçons) et quand le raisonnement interne du modèle rend cette boucle redondante.
**Source primaire :** [Article : "Reflexion: Language Agents with Verbal Reinforcement Learning", Shinn et al., 2023](https://arxiv.org/abs/2303.11366)
**Prérequis :** [Leçon 16](0016-plan-then-execute-and-decomposition.md)

## Échauffement

1. ▢ Dans un agent de plan puis exécution, que se passe-t-il si une étape échoue et que le harness ne prend pas en charge la replanification ?

<details markdown="1"><summary>Vérifier</summary>

Le harness n'a aucun moyen de s'adapter. Soit il continue aveuglément avec le plan d'origine (qui échouera probablement à nouveau), soit il s'arrête. L'agent ne peut pas apprendre de l'échec ni bifurquer vers une autre approche, parce que le plan a été figé en amont et qu'aucun mécanisme ne permet de le mettre à jour.

</details>

2. ▢ Quel est l'avantage de la replanification explicite par rapport au simple fait de relancer l'agent depuis le début ?

<details markdown="1"><summary>Vérifier</summary>

La replanification permet au modèle de voir l'échec exact et de raisonner dessus en contexte. Si vous relancez simplement l'agent, il peut produire à nouveau le même plan. Avec la replanification, le harness ajoute l'échec au transcript et demande au modèle de faire un nouveau plan, pour que le modèle puisse voir ce qui a mal tourné et ajuster.

</details>

## À savoir

### Reflexion : ajouter une boucle de réflexion

L'article Reflexion introduit une étape de réflexion explicite dans la boucle d'agent. Après l'échec d'une tentative (la réponse de l'agent est fausse, une tâche ne se termine pas, un test échoue), le harness ne réessaie pas immédiatement. Il génère à la place une réflexion en langage naturel sur ce qui a mal tourné. Cette réflexion est stockée (souvent dans un fichier ou un tampon de mémoire) et incluse dans le contexte de la tentative suivante.

La boucle ressemble à ceci :

1. Lancer l'agent sur une tâche.
2. Vérifier si la tâche a réussi (un test passe, un humain juge la réponse correcte).
3. En cas d'échec, générer une réflexion : « J'ai essayé X, mais X a échoué parce que Y. »
4. Stocker la réflexion dans une mémoire persistante.
5. Relancer l'agent, cette fois en incluant la réflexion stockée dans le contexte.
6. Retourner à l'étape 2.

C'est différent d'un simple nouvel essai. Un simple nouvel essai relance l'agent avec le même contexte. Reflexion relance l'agent avec la réflexion en contexte, pour que la deuxième tentative puisse apprendre de l'échec de la première.

### Pourquoi la réflexion n'est pas gratuite

Reflexion coûte des appels au modèle supplémentaires. Si la première tentative échoue, il faut désormais un appel pour générer la réflexion, puis un autre pour exécuter la deuxième tentative. Pour les tâches à faible taux d'échec, cette surcharge ne vaut pas d'être payée. Pour les tâches qui demandent de nombreuses tentatives, le coût cumulé est élevé.

La réflexion consomme aussi du budget de contexte. Chaque réflexion prend des tokens dans la fenêtre de contexte. Si vous accumulez de nombreuses réflexions au fil des tentatives, il faudra finir par les élaguer ou les résumer. C'est une autre version du problème de gestion du contexte des leçons précédentes.

La réflexion n'a de sens que si elle s'appuie sur de l'information réelle : un test qui a échoué, un message d'erreur, une évaluation humaine. Si la tâche n'a aucun signal d'échec clair, la réflexion n'a rien de concret à quoi réagir et risque de se contenter de rationaliser la mauvaise réponse précédente.

### Les modèles à raisonnement interne étendu

Ces dernières années, certains modèles de pointe ont acquis la capacité de faire un raisonnement interne étendu avant de produire une réponse. Ce raisonnement n'est pas visible dans le transcript (il se déroule à l'intérieur d'un seul tour du modèle, avant que la sortie ne soit renvoyée) mais il permet au modèle de s'auto-corriger, de revérifier son travail et d'attraper les erreurs évidentes avant qu'elles n'apparaissent dans la sortie.

Cela change, sans l'éliminer, l'argument en faveur des boucles de réflexion explicites. Une partie de ce qu'une boucle de réflexion apportait (attraper une étape intermédiaire manifestement fausse) se produit désormais dans le raisonnement propre du modèle, donc ajouter une boucle de réflexion par-dessus apporte moins de bénéfice marginal qu'avant.

Cependant, la réflexion explicite garde un avantage que le raisonnement interne n'a pas : elle peut intégrer de l'information qui n'existe qu'après qu'un appel d'outil a été fait. Si un appel d'outil renvoie « Permission denied » ou si un test échoue, le raisonnement interne du modèle n'a pas pu voir ce signal d'échec pendant sa phase de raisonnement d'origine, parce que l'outil n'avait pas encore tourné. Une boucle de réflexion explicite peut observer le résultat réel de l'outil et l'intégrer dans la tentative suivante.

La question n'est donc pas « réflexion ou raisonnement interne », mais plutôt « quand le surcoût de la réflexion externe vaut-il son prix malgré le raisonnement interne ? »

### Quand l'auto-critique explicite justifie son coût

Utilisez la réflexion externe quand :

- La tâche a un signal d'échec clair et vérifiable (une suite de tests passe ou échoue, une API renvoie une erreur, un humain juge la réponse fausse ou juste).
- Une deuxième ou troisième tentative, éclairée par l'échec, a de bonnes chances de réussir là où la première a échoué.
- La tâche vaut d'être retentée : une valeur assez élevée pour justifier les appels au modèle supplémentaires.

N'ajoutez pas de réflexion quand :

- La tâche n'a aucun signal d'échec clair (par exemple « écris un résumé » sans test ni grille pour vérifier la justesse).
- L'échec n'est pas la faute du modèle (par exemple une API requise est indisponible, ce que le modèle ne peut pas corriger).
- La première tentative a déjà de très fortes chances de réussir et les échecs sont rares.

### Concevoir les signaux de réflexion

La réflexion vaut ce que vaut le signal qu'elle reçoit. Si vous dites au harness « cette tâche a échoué parce que l'utilisateur l'a dit », la réflexion risque de produire « J'ai essayé d'écrire un résumé mais l'utilisateur ne l'a pas aimé. » C'est trop vague pour que la tentative suivante puisse agir dessus. Un meilleur signal d'échec serait « le résumé omet les exigences exprimées par le client » ou « le résumé dépasse la limite de 100 mots ».

Quand vous construisez un agent qui réfléchit, concevez soigneusement la vérification d'échec. À quoi ressemble la réussite ? Quelle preuve concrète établit l'échec ? Cette preuve est ce à quoi la réflexion réagira.

## Pratique

1. ▢ Un agent écrit du code pour résoudre un problème LeetCode. La suite de tests exécute le code et rapporte soit « All tests pass », soit imprime un cas de test précis en échec. Après un échec, le harness génère une réflexion et relance l'agent avec la réflexion en contexte. Pourquoi est-ce bien adapté à Reflexion ?

<details markdown="1"><summary>Vérifier</summary>

Il y a un signal d'échec clair : la suite de tests. La réflexion peut dire « Le cas de test [entrée] attendait [sortie] mais j'ai produit [mauvaise_sortie]. » C'est concret et exploitable. Le modèle peut lire cela à la tentative suivante et déboguer précisément le cas en échec. La génération de code est aussi itérative par nature ; plusieurs tentatives sont attendues et valent le coût.

</details>

2. ▢ On demande à un agent d'écrire des textes produits pour un site e-commerce. L'agent produit le texte et le soumet. Il n'y a ni suite de tests, ni grille, ni vérification automatique. Un responsable marketing humain le lit et dit « Ce n'est pas bon, réessayez. » Reflexion aiderait-il ici ?

<details markdown="1"><summary>Indice</summary>

Quel retour la boucle de réflexion a-t-elle à sa disposition ? Est-il assez concret pour que la tentative suivante puisse agir dessus ?

</details>

<details markdown="1"><summary>Vérifier</summary>

Reflexion n'aiderait pas beaucoup. Le retour « Ce n'est pas bon » est trop vague. La réflexion serait quelque chose comme « Le responsable marketing n'a pas aimé mon texte. » La tentative suivante de l'agent n'aurait aucun changement concret à faire. Une meilleure approche serait d'obtenir un retour précis du responsable (par exemple « Faites plus court et ajoutez une comparaison de prix ») et de l'inclure dans le prompt suivant, plutôt que de compter sur une boucle de réflexion.

</details>

3. ▢ Un modèle à raisonnement interne étendu peut désormais s'auto-corriger pendant sa propre phase de raisonnement. Lequel des points suivants reste un avantage d'une boucle de réflexion externe explicite dans ce contexte ?

    - a) La réflexion externe est toujours plus rapide que le raisonnement interne.
    - b) La réflexion externe peut intégrer de l'information (comme une erreur d'outil ou un test en échec) qui n'existe qu'après la première tentative du modèle.
    - c) La réflexion externe est moins chère en tokens de contexte que le raisonnement interne.
    - d) La réflexion externe fonctionne avec tous les modèles, même ceux sans capacité de raisonnement interne.

<details markdown="1"><summary>Vérifier</summary>

**b)** Le raisonnement interne se produit avant l'exécution de tout outil, donc il ne peut pas observer le résultat réel d'un outil ni l'échec d'un test. Une boucle de réflexion explicite peut intégrer cette information, donc elle apporte de la valeur même avec des modèles dotés de raisonnement interne. a) est faux, le raisonnement interne est souvent plus rapide que l'exécution d'une boucle supplémentaire. c) est faux, la réflexion externe consomme des tokens de contexte (le texte de la réflexion et la tentative suivante occupent tous deux de la place). d) est vrai mais n'est pas l'idée clé ; la question porte sur ce qu'apporte la réflexion quand un raisonnement interne est présent.

</details>

4. ▢ Vous construisez un agent qui traite des candidatures. Le harness a un signal clair : approuvée ou rejetée par un responsable du recrutement. Vous voulez utiliser Reflexion pour améliorer les décisions de l'agent sur plusieurs tentatives. Que doit capturer chaque réflexion pour être utile à la tentative suivante ?

<details markdown="1"><summary>Vérifier</summary>

La réflexion doit capturer les raisons précises du rejet ou de l'approbation, si elles sont disponibles. Par exemple : « Candidature rejetée parce que : certification requise manquante. À la prochaine tentative, vérifier les certifications requises avant d'approuver. » Ou : « Candidature approuvée parce que : solide expérience dans les compétences requises et bonne communication dans la lettre de motivation. » La réflexion doit être propre à la candidature, pas un conseil générique. Cela donne à la tentative suivante quelque chose de concret sur quoi agir. Si le responsable ne fournit qu'un oui ou un non sans raisons, la réflexion est moins exploitable.

</details>

## Exercices en situation réelle

- [ ] Prenez une tâche qui implique de l'itération et a un signal clair de réussite ou d'échec (par exemple résoudre un problème, faire passer un test, satisfaire une grille). Implémentez une boucle d'agent avec réflexion : tentative, vérification de l'échec, génération d'une réflexion, nouvel essai avec la réflexion en contexte. Lancez-la cinq fois et comptez combien de tentatives l'agent nécessite avec réflexion et sans. Notez la différence.
- [ ] Trouvez dans votre travail une tâche sans signal d'échec clair (par exemple rédaction, conception, travail créatif). Décrivez comment vous en ajouteriez un (par exemple « comparer à une grille », « faire relire par un pair », « vérifier des critères précis »). Ajouter un signal d'échec rendrait-il utile un agent qui réfléchit, ou la tâche est-elle mieux traitée avec une boucle humaine ?
- [ ] Demain : lisez une trajectoire Reflexion (tirée d'un article, d'un billet de blog ou de quelque chose que vous avez construit). Identifiez le texte de la réflexion. La réflexion aurait-elle été utile si le modèle avait eu un raisonnement interne ? Pourquoi, ou pourquoi pas ?

## Pour aller plus loin

- [Article : "Reflexion: Language Agents with Verbal Reinforcement Learning", Shinn et al., 2023](https://arxiv.org/abs/2303.11366)
- [Ressources](../RESOURCES.md)

---

Ça ne passe pas ? Relisez la source primaire en haut de page, car cette leçon la condense et c'est dans la condensation que la compréhension s'échappe. Consultez le [glossaire](../GLOSSARY.md) pour tout terme qui vous a paru glissant.

Si c'est la leçon elle-même qui n'est pas claire plutôt que la matière, c'est un défaut : [ouvrez une issue](https://github.com/TokenCemetery/teach/issues).
