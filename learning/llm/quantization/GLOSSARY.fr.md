---
title: "Glossaire"
description: "Termes de référence pour la quantification des LLM"
type: glossary
---

# Glossaire de la quantification

Termes de référence pour les formats de nombres, les méthodes de quantification, le matériel sur lequel elles tournent et la façon dont leur coût se mesure. Dans cet espace de travail, « quantification » désigne toujours la réduction de la précision des nombres d'un modèle entraîné ; elle ne désigne jamais la discrétisation d'entrées.

## Termes

**Quantification absmax** (absmax quantization) :
Quantification symétrique dont la plage d'écrêtage est la plus grande valeur absolue parmi les valeurs qui partagent un scale, si bien que rien n'est écrêté et que le scale vaut cette valeur divisée par le plus grand niveau entier.
_À éviter_ : max scaling, quantification naïve

**Act-order** :
Option de GPTQ qui quantifie les colonnes d'une couche par taille d'activation décroissante, en les triant selon la diagonale de la hessienne. Elle est documentée dans le code des auteurs, pas dans l'article.
_À éviter_ : desc_act sans l'avoir introduit, astuce de réordonnancement (le nom que l'article d'AWQ donne à une variante de GPTQ)

**Activation** :
Tenseur calculé pendant la passe avant, comme l'entrée d'une couche linéaire, par opposition à un poids stocké. Ses valeurs dépendent de l'entrée, donc sa plage n'est connue qu'à l'exécution ou estimée à partir d'un calibration set.
_À éviter_ : état caché (acceptable pour le flux résiduel en particulier), feature map

**Quantification affine** (affine quantization) :
Quantification avec à la fois un scale et un zero-point, de sorte que la grille d'entiers peut être placée de façon asymétrique autour de zéro et couvrir une plage comme [-0.2, 1.5] sans gaspiller de niveaux.
_À éviter_ : quantification asymétrique (alias accepté, mais n'employez qu'un seul terme), quantification uniforme (vrai aussi de la quantification symétrique)

**Intensité arithmétique** (arithmetic intensity) :
Nombre d'opérations arithmétiques qu'un calcul effectue par octet déplacé depuis la mémoire, ce qui décide s'il est limité par la mémoire ou par le calcul sur une puce donnée.
_À éviter_ : intensité opérationnelle, ratio FLOP par octet (accepté dans une formule)

**Largeur en bits** (bit width) :
Nombre de bits utilisés pour stocker une valeur quantifiée, sans compter les bits consacrés à son scale et à son zero-point. Voir les bits effectifs par poids pour le total.
_À éviter_ : précision (ambigu avec les bits de mantisse), profondeur en bits

**Format à échelle par bloc** (block-scaled format) :
Format dans lequel un petit bloc de valeurs, par exemple 32, partage un scale stocké à côté d'elles, ce qui permet un type d'élément très étroit. MXFP4 et NVFP4 en sont des exemples, tout comme les types par blocs de GGUF.
_À éviter_ : microscaling (c'est une seule famille, le MX de l'OCP), format groupé

**Calibration set** :
Petit échantillon d'entrées représentatives passé dans le modèle pour collecter des statistiques d'activation, qu'une méthode post-entraînement utilise pour choisir des plages ou pour pondérer les erreurs d'arrondi. Ce n'est pas un jeu d'entraînement et le PTQ ne rétropropage jamais à travers lui.
_À éviter_ : jeu d'entraînement, jeu de données de calibration (acceptable, mais pas « données de calibration » pour les statistiques elles-mêmes)

**Erreur d'écrêtage** (clipping error) :
Erreur due aux valeurs hors de la plage d'écrêtage qui sont ramenées à ses extrémités.
_À éviter_ : erreur de saturation, dépassement

**Plage d'écrêtage** (clipping range) :
Intervalle de valeurs réelles qu'un quantificateur fait correspondre à sa grille d'entiers ; les valeurs hors de cet intervalle sont ramenées à l'extrémité la plus proche. La choisir revient à arbitrer entre erreur d'écrêtage et erreur d'arrondi.
_À éviter_ : plage dynamique (c'est une propriété du format), plage de quantification

**Limité par le calcul** (compute-bound) :
Charge de travail dont la vitesse est bornée par le débit arithmétique plutôt que par le déplacement d'octets, typique du prefill et du décodage à grand batch. Ne quantifier que les poids ne l'accélère pas, et peut la ralentir.
_À éviter_ : limité par les FLOP (acceptable, mais n'employez qu'un seul terme)

**Déquantification** (dequantification) :
Faire correspondre un entier quantifié à une valeur réelle approchée avec son scale et son zero-point, soit pour calculer en plus haute précision, soit pour inspecter l'erreur.
_À éviter_ : dé-quantifier, décompression

**Quantification dynamique** (dynamic quantization) :
Calculer le scale d'une activation à l'exécution à partir des valeurs réellement présentes, plutôt que de le fixer à l'avance à partir d'un calibration set. À opposer à la quantification statique.
_À éviter_ : quantification à la volée, quantification à l'exécution

**Bits effectifs par poids** (effective bits per weight) :
Stockage moyen par poids une fois comptés les scales, les zero-points et toute autre métadonnée par groupe, par exemple environ 4.5 pour des poids en 4 bits avec un scale de 16 bits par groupe de 32.
_À éviter_ : bpw sans le définir, largeur en bits (qui exclut les métadonnées)

**Bits d'exposant** (exponent bits) :
Bits d'un format à virgule flottante qui fixent la puissance de deux par laquelle une valeur est mise à l'échelle, et donc sa plage dynamique.
_À éviter_ : bits de plage

**Fake quantization** (quantification simulée) :
Quantifier puis déquantifier aussitôt un tenseur dans la passe avant, pour que l'entraînement voie l'erreur d'arrondi et d'écrêtage tandis que l'arithmétique reste en virgule flottante.
_À éviter_ : quantification simulée (alias accepté, mais n'employez qu'un seul terme), injection de bruit de quantification

**Flip** :
Réponse qui passe de correcte à incorrecte, ou d'incorrecte à correcte, entre un modèle de référence et sa version quantifiée sur la même question. Les flips dans les deux sens s'annulent dans une moyenne d'accuracy, donc on les compte séparément.
_À éviter_ : changement de réponse (compte aussi incorrecte vers incorrecte), régression (un seul sens)

**GGUF** :
Format de modèle en un seul fichier de llama.cpp, qui stocke les tenseurs, souvent dans ses propres types de quantification par blocs, avec le tokenizer et les métadonnées du modèle.
_À éviter_ : GGML (la bibliothèque et un format plus ancien), format llama

**GPTQ** :
Méthode de quantification des poids post-entraînement qui quantifie les poids d'une couche une colonne à la fois et met à jour les poids pas encore quantifiés pour compenser chaque erreur d'arrondi, avec l'information du second ordre tirée des activations de calibration.
_À éviter_ : quantification GPT, terme générique pour tout checkpoint en 4 bits

**Granularité** (granularity) :
Nombre de valeurs qui partagent un scale et un zero-point : un tenseur entier (per-tensor), un canal de sortie (per-channel), un token (per-token) ou un groupe de taille fixe au sein d'un canal (per-group).
_À éviter_ : résolution, niveau de quantification

**Taille de groupe** (group size) :
Nombre de valeurs consécutives qui partagent un scale dans la quantification per-group, par exemple 32 ou 128.
_À éviter_ : taille de bloc (accepté là où un format l'appelle ainsi, comme MX ou GGUF)

**Hessienne** (Hessian) :
Dans GPTQ, la matrice `H = 2 X X^T` construite à partir des entrées de calibration d'une couche, avec une ligne et une colonne par feature d'entrée. Elle enregistre quelles features varient ensemble et elle est partagée par toutes les lignes des poids de la couche.
_À éviter_ : matrice de courbure, matrice de covariance (proche, mais ce n'est pas le même objet)

**Matrice d'importance** (importance matrix) :
Dans llama.cpp, importance par poids estimée à partir des activations sur un texte de calibration, utilisée pour pondérer l'erreur d'arrondi quand on choisit le scale de chaque bloc.
_À éviter_ : imatrix en prose sans l'avoir introduit

**Kernel** :
Routine GPU qui réalise une opération, comme une multiplication de matrices dans un schéma de quantification donné. Un schéma ne tourne vite que là où un kernel existe pour lui sur le matériel.
_À éviter_ : opérateur (plus large), implémentation

**Divergence KL** (KL divergence) :
Écart entre la distribution du token suivant du modèle quantifié et celle du modèle de référence, moyenné sur les tokens d'un jeu de données. Elle vaut 0 quand les deux concordent exactement et n'a pas besoin de réponses étiquetées.
_À éviter_ : KLD sans la définir, distance (ambigu)

**Quantification du KV cache** (KV-cache quantization) :
Stocker en moins de bits les clés et valeurs d'attention mises en cache, pour réduire la mémoire qui croît avec la longueur de contexte et la taille de batch.
_À éviter_ : compression du cache (couvre aussi l'éviction), quantification KV des poids

**Loss scaling** :
Multiplier la loss par une constante avant la rétropropagation pour que les petits gradients restent représentables dans un format à plage étroite comme fp16, puis diviser la constante avant la mise à jour des poids.
_À éviter_ : gradient scaling (ambigu avec l'écrêtage du gradient)

**Epsilon machine** (machine epsilon) :
Écart entre 1 et la valeur représentable suivante au-dessus de lui dans un format à virgule flottante, égal à 2 à la puissance moins le nombre de bits de mantisse.
_À éviter_ : arrondi unitaire (la moitié de cette valeur avec l'arrondi au plus proche), précision

**Bits de mantisse** (mantissa bits) :
Bits d'un format à virgule flottante qui fixent la finesse de l'espacement des valeurs au sein d'une même puissance de deux, et donc sa précision.
_À éviter_ : significande (correct mais n'employez qu'un seul terme), bits de fraction

**Activation massive** (massive activation) :
Valeur d'activation unique dans un LLM, supérieure de plusieurs ordres de grandeur aux autres, qui apparaît à une dimension fixe et à des tokens précis comme le premier.
_À éviter_ : feature outlier (un motif voisin mais différent), pic

**Limité par la mémoire** (memory-bound) :
Charge de travail dont la vitesse est bornée par la rapidité avec laquelle les octets quittent la mémoire plutôt que par l'arithmétique, typique du décodage à petit batch, où chaque poids est lu une fois par token généré.
_À éviter_ : limité par la bande passante (acceptable, mais n'employez qu'un seul terme), limité par les E/S

**Décomposition en précision mixte** (mixed-precision decomposition) :
Découper une multiplication de matrices pour que les quelques dimensions de features outlier soient calculées en 16 bits et le reste en int8, le cœur de LLM.int8().
_À éviter_ : découpage des outliers, précision mixte (plus large)

**Format natif** (native format) :
Format de nombres dans lequel les unités matricielles d'une puce multiplient directement, par opposition à un format de stockage seul qui doit être converti en format natif avant la multiplication.
_À éviter_ : format pris en charge (ambigu entre stockage et calcul)

**Seuil de bruit** (noise floor) :
Variation d'un score d'une exécution à l'autre et due à l'échantillonnage, en dessous de laquelle on ne peut pas distinguer du hasard une différence entre un modèle de référence et un modèle quantifié.
_À éviter_ : marge d'erreur (l'intervalle est la façon de rapporter le seuil), tolérance

**Feature outlier** (outlier feature) :
Dimension d'état caché dans laquelle les activations d'un transformer sont systématiquement bien plus grandes que dans les autres, sur la plupart des tokens et des couches.
_À éviter_ : canal outlier (accepté pour le canal de poids correspondant), feature émergente sans le mot outlier

**Perplexity** :
Exponentielle de la log-vraisemblance négative moyenne qu'un modèle attribue à un texte, utilisée comme indicateur rapide de ce qu'un changement a coûté au modèle.
_À éviter_ : PPL en prose sans l'avoir introduit, accuracy

**Quantification post-entraînement** (post-training quantization) :
Quantifier un modèle déjà entraîné sans entraînement supplémentaire, avec au plus un petit calibration set.
_À éviter_ : PTQ en prose sans l'avoir introduit, quantification one-shot

**Quantification** (quantization) :
Représenter les nombres réels d'un modèle sur un ensemble plus petit de niveaux avec moins de bits, au prix d'une erreur d'approximation bornée.
_À éviter_ : compression (plus large), discrétisation

**Config de quantification** (quantization config) :
L'entrée `quantization_config` du `config.json` d'un modèle, dont `quant_method` et les autres clés indiquent à un chargeur quelle méthode, quelle largeur en bits et quelle taille de groupe utilisent les tenseurs stockés.
_À éviter_ : quantize config (un fichier distinct que certains outils écrivent), métadonnées

**Quantization-aware training** (entraînement conscient de la quantification) :
Entraîner ou affiner un modèle avec de la fake quantization dans la passe avant, pour que les poids s'adaptent à l'arrondi qu'ils subiront.
_À éviter_ : QAT en prose sans l'avoir introduit, entraînement quantifié (qui calcule en basse précision)

**Point de crête** (ridge point) :
Intensité arithmétique à laquelle le débit arithmétique maximal d'une puce et sa bande passante mémoire prennent le même temps ; en dessous, un calcul est limité par la mémoire, au-dessus, il est limité par le calcul.
_À éviter_ : coude du roofline, point de croisement

**Rotation** :
Multiplier les activations et les poids d'une couche par une matrice orthogonale et sa transposée, ce qui laisse la sortie de la couche inchangée mais répartit les outliers sur de nombreux canaux pour qu'ils se quantifient mieux.
_À éviter_ : transformée de Hadamard (un choix de rotation), traitement d'incohérence (l'idée générale)

**Arrondi au plus proche** (round-to-nearest) :
Quantifier chaque valeur indépendamment vers son niveau de grille le plus proche, sans données et sans compensation d'erreur. C'est la référence à laquelle toute autre méthode post-entraînement est comparée.
_À éviter_ : RTN en prose sans l'avoir introduit, quantification naïve

**Erreur d'arrondi** (rounding error) :
Erreur due au déplacement d'une valeur située dans la plage d'écrêtage vers le niveau de grille le plus proche ; au plus un demi-pas pour l'arrondi au plus proche.
_À éviter_ : bruit de quantification (accepté pour l'erreur combinée), perte de précision

**Safetensors** :
Format de fichier de tenseurs avec une longueur d'en-tête sur 8 octets, un en-tête JSON de noms de tenseurs, de dtypes, de formes et de décalages, puis les données brutes. Il ne stocke que des tenseurs, donc le schéma de quantification est décrit dans la config de quantification.
_À éviter_ : checkpoint (l'ensemble des fichiers), fichier de poids

**Canal saillant** (salient channel) :
Canal d'entrée d'une matrice de poids dont l'erreur de quantification compte le plus, repéré dans AWQ par la taille de l'activation qu'il rencontre plutôt que par la taille de ses propres poids.
_À éviter_ : poids important (acceptable en prose), canal outlier (le nom côté poids d'une feature outlier)

**Scale** :
Taille de pas, en valeur réelle, entre deux niveaux entiers adjacents d'un quantificateur, de sorte qu'une valeur réelle vaut approximativement le scale multiplié par son entier.
_À éviter_ : pas (acceptable dans une formule), multiplicateur

**Quantification statique** (static quantization) :
Fixer le scale d'une activation à l'avance à partir d'un calibration set, si bien qu'aucune statistique n'est calculée à l'exécution. À opposer à la quantification dynamique.
_À éviter_ : quantification hors ligne

**Estimateur straight-through** (straight-through estimator) :
Traiter l'étape d'arrondi comme la fonction identité dans la passe arrière, pour qu'un gradient puisse traverser une opération dont la vraie dérivée est nulle presque partout.
_À éviter_ : STE en prose sans l'avoir introduit, gradient de substitution (plus large)

**Super-bloc** (super-block) :
Dans un k-quant GGUF, groupe de 256 poids découpé en sous-blocs qui ont chacun leur propre scale, ces scales étant quantifiés par rapport à un scale de super-bloc de 16 bits.
_À éviter_ : bloc (l'unité de 32 poids des types historiques)

**Quantification symétrique** (symmetric quantization) :
Quantification dont le zero-point est fixé à zéro, de sorte que la grille est centrée sur zéro et que seul un scale est stocké.
_À éviter_ : quantification à scale seul

**Quantification weight-only** (weight-only quantization) :
Stocker les poids en basse précision et les déquantifier à l'intérieur du kernel, tandis que les activations et l'arithmétique restent en 16 bits. Notée WxA16, par exemple W4A16.
_À éviter_ : quantification en précision mixte (plus large)

**Notation WxAy** (WxAy notation) :
Raccourci pour les largeurs en bits des poids et des activations d'un schéma, comme W8A8 pour des poids et des activations en 8 bits, parfois avec KVz pour le KV cache.
_À éviter_ : écrire int4 quand les activations ne sont pas aussi en int4

**Zero-point** :
Entier qui représente le zéro réel dans la quantification affine, choisi pour que zéro soit exactement représentable.
_À éviter_ : décalage, biais
