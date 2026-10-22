---
title: "21. Construire le dataset"
description: "Les données l'emportent sur tous les hyperparamètres de cet espace de travail"
type: lesson
---

# Leçon 21. Construire le dataset

**Lien avec la mission :** La qualité des données domine tous les hyperparamètres de cet espace de travail. L'étape 3 vous a appris à tourner un bouton ; cette étape vous apprend ce qui fait réellement bouger le résultat.
**Source primaire :** [Article : "LIMA: Less Is More for Alignment", Zhou et al., arXiv:2305.11206](https://arxiv.org/abs/2305.11206)
**Prérequis :** [Leçon 3](0003-tokenizers-and-chat-templates.md), [Leçon 12](0012-reading-a-training-run.md)

## Échauffement

1. ▢ Quelle est la vérification la plus rentable à faire avant un travail d'entraînement ?

<details markdown="1"><summary>Vérifier</summary>

Décoder un vrai exemple d'entraînement et le lire, en comptant les positions notées contre masquées. Elle attrape d'un seul coup le chat template incompatible, les tokens de fin de tour manquants, les bugs de masquage et la troncature.

</details>

2. ▢ Que signifie une courbe de loss en escalier avec des chutes aux frontières d'epoch ?

<details markdown="1"><summary>Vérifier</summary>

De la mémorisation : le modèle reconnaît des exemples qu'il a déjà vus.

</details>

3. ▢ Quelle variante de loss l'instruction tuning doit-il normalement utiliser ?

<details markdown="1"><summary>Vérifier</summary>

La complétion seule. Les positions du prompt sont masquées à `-100` pour que seule la réponse de l'assistant soit notée.

</details>

## À savoir

### Le rapport inconfortable

Si vous avez peu de temps, dépensez-le sur les données. L'écart entre un dataset médiocre et un bon dataset est plus grand que l'écart entre le rank 8 et le rank 128, plus grand que LoRA contre DoRA, et plus grand que la plupart des choses que vous pourriez régler. Les hyperparamètres sont lisibles et plaisants à ajuster, ce qui explique qu'ils absorbent de l'attention hors de proportion avec leur effet.

Le résultat de LIMA est l'énoncé publié le plus tranchant à ce sujet : un petit nombre d'exemples soigneusement choisis, de l'ordre de mille, a produit un solide suivi d'instructions, ce qui soutient l'idée que le fine-tuning supervisé enseigne surtout le *format et le style* tandis que la capacité vient du préentraînement. Considérez le chiffre exact comme propre à ce cadre ; prenez la direction au sérieux.

### Ce que le fine-tuning enseigne bien, et mal

| Enseigne bien | Enseigne mal |
|---|---|
| Format et structure de sortie | De nouveaux faits sur le monde |
| Ton, registre, voix de domaine | Une capacité de raisonnement qui n'est pas déjà présente |
| Respect constant d'un schéma | Tout ce qui demande une information à jour |
| Classification et extraction étroites | Des connaissances de longue traîne mentionnées une seule fois |
| Syntaxe d'appel d'outil et de fonction | Arithmétique et calcul précis |

La colonne de droite est la raison d'être de la [Leçon 27](0027-when-not-to-fine-tune.md). Un dataset construit pour installer des faits fait ce que le fine-tuning fait le plus mal, et chaque fait demanderait de nombreux exemples variés pour s'ancrer, et à ce stade la récupération est moins chère, plus exacte et mise à jour facilement.

### Concevoir les exemples

**Correspondre à la distribution de déploiement.** Vos entrées d'entraînement doivent ressembler aux entrées réelles. Des prompts d'entraînement propres, bien formés et de longueur uniforme produisent un modèle qui se dégrade face à la réalité désordonnée qu'il rencontre en production, et votre découpage held-out, tiré du même réservoir propre, ne vous avertira pas.

**Inclure délibérément les cas difficiles.** Entrées ambiguës, cas limites, et cas où la bonne réponse est un refus ou « informations insuffisantes ». Si chaque réponse d'entraînement est assurée et complète, vous avez entraîné de l'assurance et de l'exhaustivité, y compris sur des entrées qui ne les justifient pas.

**Être cohérent sur le format.** Si la moitié de vos exemples se terminent par un point et l'autre moitié non, le modèle apprend l'incohérence. Chaque variation arbitraire que vous laissez est de la capacité dépensée sur du bruit.

**Rendre les sorties exemplaires.** Le modèle imite ses cibles. Un dataset de réponses passables produit des réponses passables, et aucun hyperparamètre ne s'en remet.

**Varier la surface, pas le fond.** Plusieurs formulations d'une même requête enseignent la robustesse à la formulation. Plusieurs exemples quasi identiques enseignent la mémorisation.

### Déduplication

Les quasi-doublons sont le défaut grave le plus courant des datasets assemblés, et ils causent deux dommages à la fois : surpondérer ce qu'enseigne le contenu dupliqué et, si des doublons tombent des deux côtés de votre découpage, un score held-out qui mesure du rappel plutôt que de la généralisation.

La déduplication par correspondance exacte ne suffit pas. Utilisez un hachage normalisé, puis une mesure de similarité comme MinHash ou une distance d'embeddings pour les quasi-doublons. Faites-le *avant* de découper, pas après.

### Taille et équilibre

Une orientation approximative, pas une règle :

| Exemples | Objectif réaliste |
|---|---|
| 50 à 200 | Style, ton, un format de sortie fixe |
| 500 à 2,000 | Une tâche bien définie à périmètre étroit |
| 5,000 à 50,000 | Une tâche large, ou plusieurs capacités à la fois |
| 100,000+ | Rendements décroissants pour les adapters ; demandez-vous si la tâche est vraiment une seule tâche |

Là où il existe des catégories, le déséquilibre devient un biais. Un dataset qui est à 90 % d'une seule classe apprend au modèle à deviner cette classe. Équilibrez-le ou tenez compte du déséquilibre dans votre métrique, selon la leçon 23.

### Données synthétiques

Générer des données d'entraînement avec un modèle plus fort est standard, efficace, et comporte deux dangers précis.

**Erreurs héritées.** Les erreurs et les biais du générateur deviennent vos cibles d'entraînement, et elles seront fluides et cohérentes, ce qui les rend difficiles à repérer en survolant. Échantillonnez et lisez.

**Effondrement de la distribution.** Les données générées ont tendance à être plus uniformes que les données réelles : structures semblables, longueurs semblables, registre semblable. Vous entraînez un modèle qui traite proprement une tranche étroite et mal la variation réelle. Amorcez la génération à partir d'entrées réelles quand vous le pouvez, et variez délibérément les prompts.

Aussi : vérifiez la licence et les conditions du modèle à partir duquel vous générez. Le fait que les sorties puissent servir à entraîner un autre modèle est une vraie contrainte, pas une formalité.

### Mise en forme

Soignez la mécanique, une fois pour toutes :

- Rendez via le chat template propre au modèle (leçon 3). Vérifiez avec `repr`.
- Masquez les positions du prompt sauf si vous voulez délibérément qu'elles soient notées.
- Incluez le token de fin de tour, sinon le modèle n'apprendra pas à s'arrêter.
- Examinez la distribution des longueurs en tokens et fixez `max_length` d'après son percentile élevé, pas son maximum et pas une supposition.
- Confirmez que la troncature ne coupe pas les réponses en deux. Une cible tronquée silencieusement apprend au modèle à s'arrêter au milieu d'une phrase.

## Pratique

1. ▢ Vous voulez que le modèle connaisse les 400 références produit de votre entreprise. Un dataset de fine-tuning est-il le bon outil ?

<details markdown="1"><summary>Vérifier</summary>

Non. Ce sont des faits, que le fine-tuning installe de façon peu fiable : chacun demanderait de nombreux exemples variés, et le résultat est invérifiable et périmé dès que le catalogue change.

La récupération est le bon outil : exacte, citable, et mise à jour en modifiant un document plutôt qu'en ré-entraînant. Ce que le fine-tuning *pourrait* utilement enseigner ici, c'est le format de présentation des informations produit.

</details>

2. ▢ Tous vos prompts d'entraînement sont des phrases propres et bien ponctuées. Les entrées de production sont laconiques et pleines de fautes de frappe. Que se passe-t-il, et pourquoi votre jeu held-out ne l'attrapera-t-il pas ?

<details markdown="1"><summary>Vérifier</summary>

Le modèle se comporte bien sur des entrées propres et se dégrade sur des entrées réelles, parce qu'il n'a jamais vu d'entrées réelles.

Votre découpage held-out est tiré du même réservoir propre, donc il partage le défaut. Il mesure la performance sur la mauvaise distribution et rapporte un succès. Le correctif est des données d'entraînement et d'évaluation tirées du trafic de déploiement réel.

</details>

3. ▢ Pourquoi dédupliquer avant de découper plutôt qu'après ?

<details markdown="1"><summary>Vérifier</summary>

Parce qu'une paire de doublons à cheval sur le découpage met un exemple d'entraînement dans le jeu held-out. La performance held-out mesure alors de la mémorisation et la rapporte comme de la généralisation, ce qui est le moyen le plus efficace de se tromper soi-même sur un fine-tuning.

Dédupliquer après le découpage laisse intactes les paires inter-découpages, qui sont exactement le cas qui compte.

</details>

4. ▢ Quel défaut de dataset est le plus susceptible de produire un modèle qui ne dit jamais « je ne sais pas » ?

    - a) Un déséquilibre de classes qui favorise fortement une catégorie
    - b) Chaque réponse sans exception étant assurée et complète
    - c) Des exemples quasi dupliqués apparaissant de part et d'autre du découpage
    - d) Une distribution des longueurs en tokens avec une très longue queue

<details markdown="1"><summary>Vérifier</summary>

**b)** Chaque réponse sans exception étant assurée et complète.

Le modèle imite ses cibles. Sans aucun exemple d'incertitude ou de refus appropriés, l'assurance et l'exhaustivité sont le seul comportement qu'on lui a montré, y compris pour des entrées qui ne les justifient pas.

</details>

5. ▢ Nommez les deux dangers des données synthétiques et une atténuation pour chacun.

<details markdown="1"><summary>Vérifier</summary>

Erreurs héritées : les erreurs du générateur deviennent des cibles d'entraînement fluides et cohérentes. Atténuez en échantillonnant et en lisant une vraie fraction, et en validant face à une vérité terrain quand il en existe une.

Effondrement de la distribution : les données générées sont plus uniformes que les données réelles. Atténuez en amorçant la génération à partir d'entrées réelles et en variant délibérément les prompts de génération.

</details>

6. ▢ Les longueurs en tokens de votre dataset vont de 50 à 8000, avec le 95e percentile à 1200. Quel `max_length` réglez-vous, et que vérifiez-vous ?

<details markdown="1"><summary>Vérifier</summary>

Autour de 1200 à 1500. Régler 8000 gaspille de la mémoire d'activations en remplissage pour presque tous les exemples ; régler 512 tronque une fraction substantielle.

Vérifiez ensuite ce que la troncature fait réellement aux exemples au-dessus de la limite. Si elle coupe les réponses en deux, vous apprenez au modèle à s'arrêter au milieu d'une phrase, donc soit relevez la limite, soit écartez délibérément ces exemples.

</details>

## Exercices en situation réelle

- [ ] Lisez vingt exemples de votre dataset en entier, décodés via le chat template. Notez chaque incohérence trouvée.
- [ ] Exécutez la détection de quasi-doublons sur tout l'ensemble avant de découper. Notez combien vous en avez trouvé et supprimez-les.
- [ ] Tracez la distribution des longueurs en tokens et choisissez `max_length` à partir d'elle. Inspectez trois exemples qui seraient tronqués.
- [ ] Demain : ajoutez dix exemples délibérément difficiles : ambigus, cas limites, ou dont la bonne réponse est un refus.

## Pour aller plus loin

- [Article : "LIMA: Less Is More for Alignment", Zhou et al., arXiv:2305.11206](https://arxiv.org/abs/2305.11206)
- [Doc : Dataset formats, Hugging Face TRL](https://huggingface.co/docs/trl/main/en/dataset_formats)
- [Leçon 22. Contamination et conception du jeu held-out](0022-contamination-and-held-out-design.md)

---

Ça ne passe pas ? Relisez la source primaire en haut de page, car cette leçon la condense et c'est dans la condensation que la compréhension s'échappe. Consultez le [glossaire](../GLOSSARY.md) pour tout terme qui vous a paru glissant.

Si c'est la leçon elle-même qui n'est pas claire plutôt que la matière, c'est un défaut : [ouvrez une issue](https://github.com/TokenCemetery/teach/issues).
