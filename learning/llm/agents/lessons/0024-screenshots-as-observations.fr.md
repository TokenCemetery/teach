---
title: "24. Les captures d'écran comme observations"
description: "Comment les agents de computer use observent l'écran sous forme d'image plutôt que de données structurées, et pourquoi la structure de la boucle tient toujours"
type: lesson
---

# Leçon 24. Les captures d'écran comme observations

**Lien avec la mission :** Diagnostiquer un agent de computer use défaillant à partir de sa trajectoire exige de comprendre que ses observations sont visuelles et non structurées, de sorte qu'une erreur d'ancrage ne ressemble en rien à un argument d'outil manquant.
**Source primaire :** [Doc : "Computer use tool", Claude Platform Docs](https://platform.claude.com/docs/en/agents-and-tools/tool-use/computer-use-tool)
**Prérequis :** [Leçon 23](0023-code-execution-as-a-tool.md), [Boucle d'agent](../GLOSSARY.md)

## Échauffement

1. ▢ Dans les leçons précédentes, quand l'agent appelle un outil et reçoit un résultat, quelle forme prend ce résultat ? Est-il toujours structuré (JSON ou un schéma), toujours du texte non structuré, ou l'un ou l'autre ?

<details markdown="1"><summary>Vérifier</summary>

Structuré, dans tous les formats de transmission que ce parcours a couverts. Un résultat d'outil est toujours étiqueté avec l'identifiant de l'appel auquel il répond, et il porte toujours soit la sortie de l'outil, soit une erreur, même si les noms de champs exacts et la forme varient selon le fournisseur et le harness (voir la leçon 3). Le modèle n'a jamais à interpréter visuellement un résultat d'outil comme il le fait d'une capture d'écran.

</details>

2. ▢ Depuis la leçon 6 : quelles sont les quatre étapes centrales de la boucle d'agent, dans l'ordre ?

<details markdown="1"><summary>Vérifier</summary>

Appeler le modèle, ajouter la réponse au transcript, vérifier si c'est terminé, sinon exécuter les outils et ajouter leurs résultats, puis reboucler au début.

</details>

## À savoir

### L'observation change de type

Dans les leçons précédentes, l'observation d'un agent à appels d'outils après chaque action est un résultat structuré que le harness construit : un objet JSON avec des champs comme `tool_id`, `status` et `value`. L'observation d'un agent de computer use est radicalement différente. Après que l'agent a effectué une action d'écran (clic, saisie, défilement), l'observation est une capture d'écran : littéralement une image, au format PNG ou JPEG, de ce qui est affiché à l'écran à cet instant.

Le modèle doit interpréter visuellement cette image pour comprendre ce qui s'est passé, au lieu de lire un champ de données structuré. C'est un changement profond dans la façon dont l'agent comprend le monde.

La forme globale de la boucle de la leçon 6 survit sans changement : envoyer le transcript, recevoir la réponse, exécuter l'action, ajouter le résultat, recommencer. Mais maintenant « ajouter le résultat » signifie ajouter une image au transcript, et « recevoir la réponse » signifie que le modèle génère une description de ce qu'il voit dans cette image et décide quoi faire ensuite.

### Pourquoi cela compte : la généralité

La raison de cette conception est la puissance. Dans les leçons précédentes, un agent à appels d'outils ne peut appeler que les outils que le développeur a explicitement construits pour lui. Si vous voulez qu'un agent interagisse avec une application qui n'a pas d'API, vous devez écrire un outil qui enveloppe l'API de cette application. Mais que faire si l'application n'a aucune API ? Si ce n'est qu'une interface graphique ?

Un agent de computer use contourne ce problème. Au lieu d'avoir besoin d'une API ou d'un outil sur mesure pour chaque application, l'agent interagit par l'écran, comme le ferait un humain. L'espace d'actions est fixe et générique : déplacer la souris, cliquer, saisir du texte, appuyer sur des touches, faire défiler, prendre une capture d'écran. Ces mêmes actions fonctionnent dans n'importe quelle application graphique sur n'importe quel système d'exploitation, d'un navigateur web à une application de bureau en passant par une console cloud. Le modèle apprend à faire des choses d'écran, pas des choses propres à une application.

C'est là le gain : un agent qui peut manipuler littéralement n'importe quelle interface, même celles construites sans intégration d'agent en tête.

### La boucle tient toujours

Parce que la structure de la boucle est conceptuellement distincte du type d'observation, le cycle de base survit :

1. Envoyer le transcript (qui inclut désormais la capture d'écran courante) au modèle.
2. Le modèle regarde la capture d'écran, comprend ce qu'il y a à l'écran et décide quoi faire ensuite.
3. Le modèle émet une action : cliquer aux coordonnées (x, y), saisir la chaîne « hello », faire défiler vers le bas, ou prendre une autre capture d'écran.
4. Le harness exécute l'action.
5. Si l'action était une capture d'écran, le harness ajoute la nouvelle image au transcript.
6. Retourner à l'étape 1.

Le modèle décide toujours quand s'arrêter, le harness applique toujours les limites et met fin à la boucle, le transcript grandit toujours à chaque tour, et les conditions d'arrêt de la leçon 6 (plus d'actions, nombre maximal de tours, seuil d'erreurs) s'appliquent toujours. La seule chose qui a changé est le type de données de l'observation : d'un objet JSON à une image.

### Défis introduits par l'observation visuelle

Cette généralité a un coût. Un résultat d'outil structuré est non ambigu : le harness l'a construit, il a un schéma fixe, et le modèle peut lire les champs par leur nom. Une capture d'écran est ambiguë : le modèle doit localiser visuellement ce qu'il veut (un bouton, un champ de texte, un élément de menu) dans l'image courante, interpréter son emplacement et décider quelle action effectuer.

Dans la leçon 25, vous verrez cette ambiguïté se cristalliser en un problème précis appelé ancrage. Pour l'instant, sachez que ce compromis existe : les agents de computer use peuvent faire des choses que les agents à appels d'outils ne peuvent pas, parce qu'ils peuvent manipuler n'importe quelle interface graphique, mais l'observation exige une interprétation visuelle, ce qui introduit de nouveaux modes de défaillance que les observations structurées n'ont pas.

## Pratique

1. ▢ Vous construisez un agent de computer use pour interagir avec une application web. Votre collègue suggère d'ajouter un outil appelé `click_button` qui prend un nom de bouton comme argument chaîne, pour que l'agent puisse écrire `click_button("Submit")` au lieu d'avoir à manipuler des coordonnées. Est-ce une bonne idée ? Pourquoi, ou pourquoi pas ?

<details markdown="1"><summary>Vérifier</summary>

Non. Tout l'intérêt d'un agent de computer use est de fonctionner avec n'importe quelle interface graphique sans outillage sur mesure. Si vous ajoutez des outils propres à une tâche comme `click_button`, vous superposez une interface traditionnelle d'appels d'outils, ce qui défait le but. Le modèle devrait apprendre à effectuer des actions génériques (cliquer à des coordonnées, saisir) et à interpréter visuellement la capture d'écran. Ajouter des outils enveloppes ajoute du couplage et réduit la généralité de l'agent.

</details>

2. ▢ Un agent de computer use prend une capture d'écran, voit un formulaire de connexion et saisit son nom d'utilisateur dans le champ du mot de passe au lieu du champ du nom d'utilisateur. Est-ce un bug du modèle, du harness ou de l'espace d'actions lui-même ?

<details markdown="1"><summary>Indice</summary>

Le modèle a décidé de saisir le nom d'utilisateur. Le harness a exécuté l'action. Quelque chose s'est mal passé dans la liaison entre la décision et la bonne partie de l'écran.

</details>

<details markdown="1"><summary>Vérifier</summary>

C'est une erreur d'interprétation visuelle : le modèle a vu le formulaire mais a mal identifié quel champ était lequel. L'espace d'actions (saisir cette chaîne) a fonctionné correctement. Le harness a exécuté l'action correctement. La compréhension de la capture d'écran par le modèle était fausse. C'est ce qu'on appelle une erreur d'ancrage, et c'est le sujet de la leçon 25.

</details>

3. ▢ Un agent à appels d'outils qui lit des fichiers utilise un outil appelé `read_file(path)` et reçoit un résultat avec un champ de statut. Un agent de computer use qui lit des fichiers en les ouvrant dans un éditeur de texte prend une capture d'écran après avoir ouvert l'éditeur. Quelle observation est la plus facile à vérifier comme réussie pour le harness ?

    - a) L'agent à appels d'outils, parce que le champ de statut est explicite
    - b) L'agent de computer use, parce qu'une capture d'écran montre tout
    - c) Elles sont aussi faciles l'une que l'autre, juste dans des formats différents
    - d) Aucune des deux, parce que vérifier la réussite exige que le modèle interprète le résultat dans les deux cas

<details markdown="1"><summary>Vérifier</summary>

**a)** L'agent à appels d'outils a un champ de statut explicite ; le harness peut vérifier `if result.status == "success"` sans ambiguïté. La capture d'écran de l'agent de computer use montre le contenu du fichier, mais le harness doit apporter cette capture au modèle et lui demander de vérifier que le fichier s'est ouvert correctement, ce qui est plus lent et moins fiable. Le type d'observation affecte la facilité de vérification.

</details>

4. ▢ Vous lisez la trajectoire d'un agent de computer use qui a tenté de remplir un formulaire. L'agent a effectué huit actions : clics sur des champs, saisie de texte et défilement. La dernière capture d'écran montre le formulaire avec des champs vides. Que devez-vous vérifier en premier pour diagnostiquer pourquoi l'agent a échoué ?

<details markdown="1"><summary>Vérifier</summary>

Regardez les coordonnées de chaque action de clic par rapport aux captures d'écran prises après chaque clic. L'agent a-t-il cliqué sur la bonne partie de l'écran, ou les clics sont-ils tombés aux mauvais endroits ? Même si le modèle a décidé de « cliquer sur le champ du nom d'utilisateur », la coordonnée réelle du clic a pu être décalée. C'est le problème d'ancrage : l'intention du modèle et l'emplacement réel à l'écran ont divergé.

</details>

## Exercices en situation réelle

- [ ] Ouvrez une application web dans un navigateur. Prenez une capture d'écran manuellement. Pour trois éléments à l'écran (un bouton, un champ de texte, un lien), estimez leurs coordonnées en pixels (x, y). Redimensionnez maintenant la fenêtre du navigateur ou faites défiler, prenez une nouvelle capture d'écran et réestimez ces mêmes coordonnées. Notez de combien les coordonnées ont changé et si une coordonnée fixe de la première capture fonctionnerait encore sur la seconde.

- [ ] Lisez la trajectoire d'un agent de computer use (issue d'un exemple public, d'une documentation d'outil ou de votre propre test). Choisissez une capture d'écran au milieu de l'exécution. Sans regarder les captures ni les actions suivantes, notez trois choses que l'agent pourrait faire ensuite. Regardez ensuite l'action que l'agent a réellement effectuée. Vos prédictions correspondaient-elles ?

- [ ] Demain : trouvez la description d'un échec d'agent de computer use (dans un billet de blog, une issue GitHub ou un résumé d'article). Avant de lire l'explication, faites l'hypothèse que l'échec est dû au modèle qui a mal compris la tâche, à une erreur de syntaxe d'appel d'outil, à une erreur d'ancrage (mauvaises coordonnées) ou à autre chose. Lisez ensuite l'explication et vérifiez si votre supposition était juste.

## Pour aller plus loin

- [Doc : "Computer use tool", Claude Platform Docs](https://platform.claude.com/docs/en/agents-and-tools/tool-use/computer-use-tool)
- [Ressources](../RESOURCES.md)

---

Ça ne passe pas ? Relisez la source primaire en haut de page, car cette leçon la condense et c'est dans la condensation que la compréhension s'échappe. Consultez le [glossaire](../GLOSSARY.md) pour tout terme qui vous a paru glissant.

Si c'est la leçon elle-même qui n'est pas claire plutôt que la matière, c'est un défaut : [ouvrez une issue](https://github.com/TokenCemetery/teach/issues).
