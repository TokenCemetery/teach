---
title: "20. Relire un pipeline de récupération"
description: "Relire la conception du pipeline de récupération de quelqu'un d'autre et nommer précisément ce qui ira de travers avant sa mise en production, et dire quand le RAG lui-même (et non une étape du pipeline) est la mauvaise réponse au problème posé"
type: lesson
---

# Leçon 20. Relire un pipeline de récupération

**Lien avec la mission :** Une compétence de senior consiste à relire le travail de quelqu'un d'autre, à nommer ce que coûte un choix plutôt que de dire qu'il paraît mauvais, et à savoir quand toute l'approche est la mauvaise pour le problème (et pas seulement quelle étape est cassée).
**Source primaire :** [Article : "Lost in the Middle: How Language Models Use Long Contexts", Liu et al., 2023](https://arxiv.org/abs/2307.03172)
**Prérequis :** [Leçon 1](0001-chunking.md), [Leçon 2](0002-embedding-models-and-similarity.md), [Leçon 4](0004-ann-indexes.md), [Leçon 6](0006-bm25-and-lexical-search.md), [Leçon 9](0009-when-reranking-earns-its-cost.md), [Leçon 11](0011-diagnosing-the-pipeline.md), [Leçon 15](0015-metadata-filtering-and-access-control.md), [Leçon 17](0017-freshness.md)

## Échauffement

1. ▢ Que mesure une métrique de récupération, et pourquoi les poids hybrides et le reranking en ont-ils besoin ?

<details markdown="1"><summary>Vérifier</summary>

Une métrique de récupération comme Recall@k ou MRR mesure si la bonne information a été récupérée, avant même que l'étape de génération ne commence. Le réglage des poids hybrides et du reranking dépend de la connaissance du fait qu'une modification a réellement amélioré ce qui a été récupéré, donc ils ont besoin d'une mesure sur laquelle décider plutôt que d'un simple feeling.

</details>

2. ▢ Pourquoi le post-filtrage échoue-t-il pour le contrôle d'accès en particulier, d'une façon qui ne vaut pas pour les autres filtres de métadonnées ?

<details markdown="1"><summary>Vérifier</summary>

Le post-filtrage exécute d'abord la recherche ANN sur tout l'index, puis rejette les résultats après coup. Pour les filtres de métadonnées ordinaires, ce n'est qu'une régression de recall : le filtre écarte certains résultats. Pour le contrôle d'accès, du contenu non autorisé existe brièvement dans le pipeline avant d'être écarté, ce qui est une défaillance de sécurité, pas seulement de qualité. Le pré-filtrage restreint l'ensemble des candidats avant l'exécution de la recherche, de sorte que le contenu interdit n'entre jamais dans le pipeline.

</details>

3. ▢ Nommez une façon dont un corpus peut devenir périmé, et une façon dont la fraîcheur se gère différemment pour ce cas par rapport à un autre.

<details markdown="1"><summary>Vérifier</summary>

Un corpus devient périmé par l'ajout de documents, leur suppression ou le changement du modèle d'embedding. L'ajout et la suppression peuvent utiliser l'indexation incrémentale, HNSW gère assez bien les deux. Changer de modèle exige une réindexation complète à partir de zéro : les anciens vecteurs ne partagent aucune distance comparable avec les nouveaux, donc ils doivent être entièrement reconstruits.

</details>

## À savoir

### La liste de contrôle de relecture : ce qu'il faut réellement chercher dans une conception

Quand quelqu'un propose un pipeline de récupération ou vous en montre un déjà construit, parcourez ces questions dans l'ordre. Chacune correspond à une étape de ce fil conducteur. Pour chacune, cherchez : (1) le choix a-t-il été fait délibérément pour ce corpus et ce cas d'usage, (2) a-t-il été mesuré par rapport à une métrique de récupération, ou a-t-il été retenu par défaut ou au feeling ?

**Étape 1 : stratégie de chunking.** La conception a-t-elle choisi une stratégie de chunking parce qu'elle correspond à la structure réelle du corpus (taille fixe pour de la prose, récursif pour du markdown imbriqué, sémantique pour des articles avec des changements de sujet, ou tenant compte de la structure du document pour des PDF dont la mise en page compte) ? Ou une taille de chunk par défaut (512, 1024 tokens) a-t-elle simplement été recopiée ? Un corpus de PDF médicaux demande un chunking différent d'un dépôt rempli de documentation d'API.

**Étapes 2 et 3 : modèle d'embedding et métrique de similarité.** Le modèle d'embedding et la métrique (cosinus, L2, produit scalaire) ont-ils été choisis pour ce corpus, testés sur des corpus similaires ou au moins sur des exemples de celui-ci ? Ou ont-ils été retenus par défaut d'après ce que recommandait la documentation de la base vectorielle ? Un embedding entraîné sur des actualités pourrait mal classer des articles de finance.

**Étapes 4, 5, 6 : recherche hybride, reranking et évaluation de la récupération.** La conception a-t-elle une vraie métrique de récupération sur laquelle elle a été réglée (Recall@k, MRR, nDCG) ? Ou les poids hybrides et le reranking ont-ils été ajoutés au feeling, sans mesure de leur effet réel sur ce qui est récupéré ? Une étape de reranking qui coûte de la latence a besoin d'une preuve qu'elle a mérité ce coût sur le cas d'usage réel.

**Étape 9 : filtrage respectueux des permissions.** Si le corpus a un contrôle d'accès, la conception utilise-t-elle le pré-filtrage pour restreindre l'ensemble des candidats avant la recherche ANN, en gardant entièrement le contenu non autorisé hors du pipeline ? Ou récupère-t-elle sur tout l'index et filtre-t-elle après coup, au risque à la fois d'une régression de recall et d'un moment où du contenu non autorisé existe dans le pipeline ?

**Étapes 10 et 11 : ingestion et fraîcheur.** La conception a-t-elle pris en compte la façon dont les documents sources sont réellement extraits et analysés en amont du chunking ? A-t-elle un plan pour garder l'index à jour à mesure que des documents sont ajoutés, supprimés ou modifiés, ou suppose-t-elle des données statiques ? Les mises à jour incrémentales conviennent bien à HNSW, mais changer de modèle d'embedding exige toujours une réindexation complète.

**Retour à l'étape 6 : distinguer un échec de récupération d'un échec de génération.** Quand quelque chose tourne mal, la conception a-t-elle un moyen de dire si le modèle a reçu un mauvais contexte ou a mal utilisé un bon contexte ? Une conception qui incrimine par défaut l'étape de récupération pour n'importe quelle mauvaise réponse manque d'un diagnostic essentiel.

### La question disputée : le long contexte rend-il la récupération obsolète ?

C'est un désaccord toujours vivant. Un récit dit que les modèles à long contexte éliminent désormais le besoin de récupération : pourquoi construire un pipeline de récupération quand les modèles peuvent maintenant contenir tout le corpus dans le prompt ? Pourquoi payer une infrastructure de récupération quand on peut simplement envoyer 100K tokens à chaque requête ?

L'autre récit dit que la récupération l'emporte encore pour la plupart des corpus et des cas d'usage réels, malgré les progrès du long contexte. L'article de recherche « Lost in the Middle » montre que les modèles utilisent bien moins bien l'information placée au milieu d'un long contexte que celle placée au début ou à la fin, même dans la fenêtre de contexte. Renvoyer un corpus entier à chaque requête concentre tous les tokens qu'il n'utilise pas au milieu de l'attention, exactement là où les modèles utilisent mal l'information. La récupération n'envoie au contraire que les parties pertinentes, en les gardant près du haut de la fenêtre de contexte, là où les modèles y prêtent bien attention.

Mais c'est le cadre de décision, pas la décision elle-même. Pour trancher si la récupération est la bonne réponse à un problème précis, posez trois questions :

**1. Quelles sont la taille du corpus et la fréquence de mise à jour ?**

Un corpus petit, statique et qui tient dans un seul prompt peut légitimement mieux fonctionner envoyé en entier : le manuel complet d'une entreprise (50K tokens, modifié chaque trimestre) peut être moins cher et plus simple à inclure à chaque requête qu'à maintenir derrière un index de récupération. Un corpus grand (des millions de documents), qui change constamment (ingestion quotidienne) ou dont l'accès est contrôlé (des utilisateurs différents voient des sous-ensembles différents) fonctionne dans l'autre sens : le coût de le renvoyer à chaque requête est prohibitif, ou le contrôle d'accès est impossible à appliquer après la récupération (la leçon de l'étape 9).

**2. De quoi la forme des requêtes a-t-elle réellement besoin ?**

Une requête qui exige une synthèse sur tout le corpus (quel est le consensus sur X dans tous nos articles) peut gagner à voir davantage de contexte. Une requête qui exige des faits précis (quelle est notre politique de remboursement pour les abonnements annuels) fonctionne mieux avec une récupération qui trouve le document exact de la politique et le place en haut, là où le modèle y prête bien attention. La récupération permet d'envoyer moins de contexte avec une meilleure fidélité.

**3. À combien revient réellement le calcul du coût ?**

L'article « Lost in the Middle » montre le compromis : quand l'information se trouve au milieu d'un prompt de 100K tokens, les modèles la perdent. Pour contourner cela, il faut soit ordonner soigneusement le contexte (ce que fait la récupération en plaçant les chunks les plus pertinents près du haut), soit en envoyer moins. Une récupération qui envoie 2K tokens des chunks les plus pertinents est moins chère et meilleure que 100K tokens dont la moitié est dans la zone morte. Cela suppose que votre récupération trouve réellement les chunks pertinents ; si le pipeline de récupération est cassé, tout envoyer est au moins une solution de repli. Mais quand la récupération fonctionne, elle l'emporte en coût, en latence et en qualité.

## Pratique

1. ▢ Une équipe a construit un pipeline qui découpe tous les documents en chunks d'une taille fixe de 1024 tokens. Vous relisez la conception et ne voyez aucune justification de ce choix. Quelle question devez-vous poser pour comprendre s'il était délibéré ou pris par défaut ?

<details markdown="1"><summary>Vérifier</summary>

Quel est le corpus ? S'agit-il de transcriptions de support client, d'articles universitaires, de documentation produit, ou d'autre chose ? Un chunk de 1024 tokens convient à certains types de documents et échoue pour d'autres. S'ils ont choisi cette taille parce qu'elle était facile à implémenter ou parce que le code d'exemple de la base vectorielle l'utilisait, c'est un signal d'alerte. S'ils ont testé différentes tailles de chunks sur une métrique de récupération mise de côté, avec des échantillons réels du corpus, et que 1024 l'a emporté, c'est un choix délibéré que vous pouvez retracer.

</details>

2. ▢ La conception utilise le modèle d'embedding d'OpenAI sans l'avoir testé sur le corpus réel. Qu'est-ce qui pourrait mal tourner ?

<details markdown="1"><summary>Vérifier</summary>

Le modèle d'embedding a été entraîné sur une large distribution de textes d'internet. Si le corpus est très spécialisé (documents juridiques, dépôts financiers, littérature médicale) ou dans une langue pour laquelle il y a moins de données de préentraînement, le modèle peut mal classer la similarité sémantique. Le bon test : calculer l'embedding d'un échantillon de documents de ce corpus, identifier à la main quelles paires sont réellement similaires, et vérifier si le classement par distance d'OpenAI concorde. Sinon, envisagez des embeddings spécifiques au domaine ou des modèles entraînés sur un contenu similaire.

</details>

3. ▢ Une conception utilise la recherche hybride (BM25 + vectoriel) mais l'équipe ne sait pas comment les pondérer. Elle demande : « devons-nous faire 50-50, ou 70-30 en faveur du vectoriel ? » Quelle information leur manque-t-il ?

<details markdown="1"><summary>Vérifier</summary>

Il leur manque une métrique de récupération. Les poids doivent être réglés d'après une mesure réelle sur un jeu de requêtes mis de côté, en mesurant quel mélange produit le meilleur Recall@k ou MRR sur la tâche. Hésiter entre 50-50 et 70-30 revient à jouer à pile ou face, et un mauvais mélange peut nuire davantage que l'une ou l'autre approche seule. La vraie question est : pour votre corpus et vos requêtes, quel mélange récupère réellement la bonne information ? Mesurez-le.

</details>

4. ▢ Le corpus contient des articles de recherche médicale qui sont mis à jour constamment (de nouveaux articles ajoutés chaque jour, d'anciens parfois rétractés ou corrigés). Une proposition suggère de mettre tous les documents dans le prompt d'un modèle à long contexte à chaque requête. Quelles sont deux raisons pour lesquelles cela pourrait ne pas fonctionner ?

<details markdown="1"><summary>Indice</summary>

Réfléchissez à la nature du corpus (taille, rythme de changement) et à ce que fait le modèle de l'information placée au milieu d'un long contexte.

</details>

<details markdown="1"><summary>Vérifier</summary>

Deux raisons : (1) Le corpus est grand et change constamment, donc renvoyer tous les documents à chaque requête est coûteux, et mettre à jour la liste des documents présents dans le prompt est une charge de maintenance. La récupération permet de n'envoyer que ce qui est pertinent et se met à jour automatiquement quand l'index est rafraîchi. (2) Les modèles utilisent mal l'information placée au milieu d'un long contexte (« Lost in the Middle »). Envoyer 500 articles dont seuls quelques-uns sont pertinents pour la requête enfouit les pertinents au milieu de l'attention, là où les modèles y prêtent mal attention. Une récupération qui envoie les 5 articles pertinents, classés par pertinence en haut du contexte, est à la fois moins chère et plus précise.

</details>

5. ▢ Une équipe qui envisage le RAG demande : « Notre corpus fait 10 Mo de fichiers markdown, mis à jour une fois par an. Pourquoi ne pas simplement tout inclure dans le prompt ? » Laquelle des affirmations ci-dessous répond correctement à cette question ?

    - a) Les modèles à long contexte rendent le RAG complètement obsolète ; cette équipe ne devrait jamais utiliser la récupération, pour aucune raison
    - b) Le corpus est petit, statique et tient dans un prompt ; pour ce cas précis, tout inclure pourrait en réalité être plus simple et fonctionner très bien
    - c) Le RAG est toujours meilleur que le long contexte, quelle que soit la taille du corpus ou la fréquence de changement
    - d) L'article « Lost in the Middle » prouve qu'on ne devrait jamais rien mettre dans un prompt

<details markdown="1"><summary>Vérifier</summary>

**b)** C'est la position nuancée sur cette question. La taille du corpus (10 Mo, probablement sous la fenêtre de contexte), la fréquence de changement (annuelle) et les besoins de contrôle d'accès (aucun mentionné) pointent tous vers un long contexte qui fonctionne très bien, peut-être plus simplement. Le RAG a de vrais coûts d'infrastructure. Un petit corpus statique ne justifie pas ces coûts. (a) est fausse : on peut légitimement utiliser les modèles sans récupération quand le corpus est minuscule et statique. (c) est fausse : la décision dépend des caractéristiques du corpus et de la forme des requêtes, pas d'une règle absolue. (d) est fausse : l'article montre que les modèles utilisent mal le milieu du contexte, pas que tout ce qui se trouve dans un prompt est inutilisable.

</details>

## Exercices en situation réelle

- [ ] Trouvez un pipeline de récupération que vous avez construit ou relu. Parcourez-lui les six questions de la liste de contrôle. Pour chaque étape, écrivez une phrase : ce choix a-t-il été mesuré par rapport à une métrique de récupération, ou retenu par défaut ? Demandez-vous ensuite : que changeriez-vous si vous deviez l'améliorer ?
- [ ] Choisissez un corpus (le vôtre, un corpus public que vous connaissez, ou un corpus synthétique). Appliquez le cadre en trois questions : taille du corpus et fréquence de mise à jour, forme des requêtes, coût réel d'un renvoi complet par rapport à la récupération. Notez la réponse : la récupération ou le long contexte conviendrait-il le mieux, et pourquoi ?
- [ ] Demain : lisez la section des résultats de l'article « Lost in the Middle » et notez l'écart de performance précis entre l'information au début, au milieu et à la fin d'un contexte de 4K tokens. Estimez ensuite : si la forme de vos requêtes exigeait une synthèse sur 100 documents, combien tiendraient dans les zones de « haute qualité » du début et de la fin ?

## Pour aller plus loin

- [Article : "Lost in the Middle: How Language Models Use Long Contexts", Liu et al., 2023](https://arxiv.org/abs/2307.03172)
- [Leçon 24 : Contexte long au moment du serving](../../inference/lessons/0024-long-context-at-serve-time.md) : ce que les techniques de long contexte font réellement au coût de serving, plutôt qu'au coût de la récupération
- [Ressources](../RESOURCES.md)

---

Ça ne passe pas ? Relisez la source primaire en haut de page, car cette leçon la condense et c'est dans la condensation que la compréhension s'échappe. Consultez le [glossaire](../GLOSSARY.md) pour tout terme qui vous a paru glissant.

Si c'est la leçon elle-même qui n'est pas claire plutôt que la matière, c'est un défaut : [ouvrez une issue](https://github.com/TokenCemetery/teach/issues).
