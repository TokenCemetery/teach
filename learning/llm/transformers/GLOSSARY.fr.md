---
title: "Glossaire"
description: "Termes de référence pour les transformers"
type: glossary
---

# Glossaire des transformers

Termes de référence pour l'architecture transformer, dérivée à partir de tenseurs bruts plutôt que d'un module préconstruit.

## Termes

**Cross-attention** (attention croisée) :
Sous-couche d'attention dont les requêtes viennent d'une séquence (la sortie déjà générée par un décodeur) mais dont les clés et les valeurs viennent d'une autre séquence (la sortie d'un encodeur distinct), ce qui permet à un décodeur de consulter une entrée complète, déjà encodée, pendant qu'il génère. Absente d'un modèle decoder-only, qui n'a ni encodeur distinct ni séquence d'entrée séparée sur laquelle porter son attention.
_À éviter_ : self-attention (une sous-couche différente dont les requêtes, les clés et les valeurs viennent toutes de la même séquence ; la cross-attention tire précisément ses clés et ses valeurs d'une autre séquence que celle de ses requêtes)

**Encoder-decoder** (encodeur-décodeur) :
Architecture (comme celle du transformer d'origine, ou T5) qui associe un encodeur bidirectionnel, sans masque causal, qui traite une entrée complète, à un décodeur qui génère la sortie de façon autorégressive grâce à une self-attention causale plus une cross-attention vers la sortie de l'encodeur. Adaptée aux tâches dont la séparation entrée puis sortie est nette et fixe, comme la traduction.
_À éviter_ : decoder-only (l'architecture que cet espace de travail construit, sans encodeur distinct ni cross-attention, puisque son flux unique sert à la fois de contexte de conditionnement et de sortie générée)

**Encoder-only** (encodeur seul) :
Architecture (comme BERT) qui utilise une attention bidirectionnelle, conditionnée conjointement sur le contexte de gauche et de droite à chaque couche, sans aucun masque causal. Elle construit une représentation d'une entrée complète, déjà donnée, pour des tâches de compréhension (classification, extraction), plutôt que de générer du texte de façon autorégressive, ce que son architecture ne peut pas faire.
_À éviter_ : decoder-only (une architecture à masque causal construite précisément pour générer un token à la fois ; l'attention bidirectionnelle d'un encoder-only n'a jamais été entraînée à prédire à partir d'un simple préfixe)

**FlashAttention** :
Implémentation exacte et sensible aux entrées-sorties de la scaled dot-product attention, qui découpe le calcul en tuiles pour rester dans la mémoire rapide du GPU située sur la puce (SRAM), sans jamais matérialiser dans la mémoire principale plus lente (HBM) la matrice complète des scores d'attention, dont la taille est quadratique. Elle calcule exactement le même résultat mathématique que l'équation de la leçon 1 ; l'accélération vient entièrement des accès mémoire, pas d'une approximation.
_À éviter_ : attention approchée (une autre famille de méthodes qui sacrifient de la qualité pour de la vitesse ; FlashAttention est exacte et ne tire son accélération que de l'efficacité des entrées-sorties)

**Gated linear unit (GLU)** (unité linéaire à porte) :
Produit élément par élément de deux projections linéaires de la même entrée, après avoir appliqué une non-linéarité (à l'origine une sigmoïde) à l'une d'elles. Cette projection joue le rôle de porte : elle module la sortie de l'autre projection élément par élément, au lieu d'appliquer uniformément une seule non-linéarité fixe.
_À éviter_ : SwiGLU (une variante précise de GLU, à porte Swish/SiLU ; « GLU » est la famille générale, pas ce seul membre)

**Accumulation de gradient** (gradient accumulation) :
Exécution de passes avant et de passes arrière sur plusieurs micro-batchs plus petits, l'un après l'autre, sans remettre les gradients à zéro entre eux, de sorte que le gradient de chaque micro-batch s'ajoute aux précédents, puis un seul pas d'optimiseur sur le total combiné. Simule une taille de batch effective plus grande que ce que la mémoire pourrait contenir d'un coup, sans changer ce qui est calculé.
_À éviter_ : augmenter la taille réelle du batch (le but que l'accumulation de gradient atteint sans que le batch plus grand ait jamais besoin de tenir en mémoire en une seule fois)

**Écrêtage de la norme du gradient** (gradient norm clipping) :
Remise à l'échelle de tout le vecteur gradient, vers le bas, pour que sa norme globale ne dépasse pas un seuil choisi, en laissant sa direction inchangée, chaque fois que cette norme serait sinon plus grande. Protège contre un gradient qui explose de temps à autre et provoquerait une mise à jour destructrice d'ampleur excessive.
_À éviter_ : écrêter indépendamment le gradient de chaque paramètre (déforme la direction du gradient combiné ; l'écrêtage par la norme remet à l'échelle tout le vecteur de façon uniforme)

**Décodage glouton** (greedy decoding) :
Choix, à chaque étape de génération, du seul token de plus forte probabilité dans la distribution prédite par le modèle. Déterministe, et bien qu'il maximise la même quantité que celle que le modèle a été entraîné à bien prédire, il produit en pratique un texte fade et étrangement répétitif.
_À éviter_ : supposer que l'objectif d'entraînement (la vraisemblance) est automatiquement le bon objectif de décodage ; ce sont deux questions différentes, avec des réponses différentes

**Grouped-query attention (GQA)** (attention par requêtes groupées) :
Variante d'attention qui utilise un nombre intermédiaire de têtes de clés et de valeurs, plus d'une et moins que le nombre de têtes de requêtes, chaque groupe de têtes de requêtes partageant une tête de clés et de valeurs. Un compromis entre les clés et valeurs propres à chaque tête de la multi-head attention complète et la tête partagée unique de la multi-query attention.
_À éviter_ : multi-query attention (MQA) (le cas plus extrême, avec une seule tête de clés et de valeurs partagée ; la GQA est la généralisation qui en garde plusieurs)

**KV cache** :
Vecteurs de clés et de valeurs conservés pour chaque position précédente pendant la génération autorégressive, réutilisés à chaque nouvelle étape de génération au lieu d'être recalculés depuis zéro. Sa taille dépend du nombre d'ensembles distincts de têtes de clés et de valeurs du modèle, ce que réduisent précisément la grouped-query attention et la multi-query attention.
_À éviter_ : recalculer les clés et les valeurs à chaque étape de génération (correct mais gaspilleur ; le cache existe précisément pour l'éviter)

**Warmup du learning rate** (learning rate warmup) :
Augmentation progressive du learning rate (souvent linéaire) pendant un nombre fixe de pas d'entraînement initiaux avant qu'il atteigne sa valeur cible, plutôt que de l'appliquer à pleine force dès le départ. Répond au fait que les estimations de moments d'Adam sont peu fiables dans les tout premiers pas, avant d'avoir vu assez de gradients pour les calibrer.
_À éviter_ : appliquer le learning rate cible dès le premier pas (risque une mise à jour importante et mal orientée avant que les statistiques propres à l'optimiseur se soient stabilisées)

**Entraînement en précision mixte** (mixed precision training) :
Stockage des poids, des activations et des gradients en demi-précision pendant la majeure partie de l'entraînement au lieu de la pleine précision (simple), ce qui réduit l'usage mémoire de près de moitié. Exige une copie maître des poids en pleine précision (pour conserver les petites mises à jour qui subiraient sinon un underflow) et un loss scaling (pour éviter que les petits gradients tombent à zéro par underflow).
_À éviter_ : entraîner en demi-précision seule, sans copie maître des poids ni loss scaling (risque de perdre silencieusement de petites mises à jour et de petits gradients par underflow)

**Mixture-of-experts (MoE)** (mélange d'experts) :
Couche qui remplace un unique bloc feed-forward par plusieurs blocs feed-forward experts en parallèle, plus un routeur qui choisit quels experts traitent un token donné. À activation parcimonieuse : le nombre total de paramètres croît avec le nombre d'experts, mais le coût de calcul par token reste à peu près constant, puisque seuls les experts choisis s'exécutent réellement.
_À éviter_ : supposer que plus d'experts signifie plus de calcul par token (seul le calcul de l'expert choisi par le routeur compte dans le coût d'un token donné, quel que soit le nombre total d'experts)

**Échantillonnage nucleus (top-p)** (nucleus sampling) :
Échantillonnage dans le plus petit ensemble de tokens de plus forte probabilité dont la probabilité cumulée dépasse un seuil `p`, ensemble dont la taille varie d'une étape à l'autre selon que la distribution est plus ou moins piquée. S'oppose à la troncature de taille fixe du top-k, qui ne peut pas s'adapter à cette variation.
_À éviter_ : échantillonnage top-k (une troncature à nombre fixe ; la coupure du nucleus est au contraire un ensemble de taille dynamique, fondé sur la probabilité cumulée)

**RMSNorm** :
Normalisation qui divise un vecteur d'activation par sa racine carrée moyenne quadratique (RMS) et applique une échelle apprise. Elle garde l'opération de remise à l'échelle de la layer norm tout en supprimant entièrement son étape de recentrage (soustraction de la moyenne). Moins coûteuse que la layer norm, avec des performances comparables sur les tâches en pratique.
_À éviter_ : layer norm (la normalisation fondée sur la moyenne et la variance que simplifie RMSNorm ; RMSNorm ne calcule ni ne soustrait jamais de moyenne)

**Rotary position embedding (RoPE)** (embedding de position rotatif) :
Mécanisme de position qui fait tourner les vecteurs de requête et de clé projetés d'un angle proportionnel à leur position, au lieu d'ajouter au préalable un vecteur fixe à l'embedding. Comme les rotations se composent en additionnant les angles, le score d'attention obtenu ne dépend que du décalage relatif entre deux positions, et d'aucune des deux positions absolues.
_À éviter_ : encodage sinusoïdal (un mécanisme différent, additif, appliqué à l'embedding avant la projection ; RoPE est multiplicatif et s'applique à Q et K après la projection, à l'intérieur même du calcul d'attention)

**Scaled dot-product attention** (attention par produit scalaire normalisé) :
L'opération `softmax(QK^T / sqrt(d_k)) V` : comparer une requête à un ensemble de clés par produit scalaire, normaliser pour compenser la croissance de la variance avec `d_k`, transformer les scores en poids avec softmax, puis renvoyer la somme pondérée des valeurs correspondantes.
_À éviter_ : mécanisme d'attention (trop vague dès qu'on parle de cette forme précise)

**Self-attention** (auto-attention) :
Scaled dot-product attention dont les requêtes, les clés et les valeurs viennent toutes de la même séquence d'entrée, de sorte que chaque position porte son attention sur toutes les positions de cette même séquence, y compris elle-même.
_À éviter_ : intra-attention

**SwiGLU** :
La variante de GLU à porte Swish (SiLU), utilisée dans la sous-couche feed-forward de la plupart des modèles ouverts actuels à la place d'une non-linéarité simple comme ReLU ou GELU. Utilise trois matrices de poids (deux projections vers le haut, une projection vers le bas) au lieu des deux d'un bloc feed-forward simple.
_À éviter_ : GELU, ReLU (les non-linéarités fixes, à projection unique, que remplace dans les modèles actuels la conception à porte et à deux projections de SwiGLU)

**Température** (temperature) :
Valeur qui divise les logits avant le softmax produisant la distribution du token suivant pendant la génération. En dessous de 1, elle accentue la distribution vers le comportement du décodage glouton ; au-dessus de 1, elle l'aplatit. Elle modifie à quel point la distribution est piquée sans décider quels tokens sont éligibles à l'échantillonnage.
_À éviter_ : top-k, top-p (la température ne fait que remettre à l'échelle l'acuité des probabilités ; décider de l'ensemble éligible est une étape distincte, ultérieure, que réalisent ces méthodes)

**Échantillonnage top-k** (top-k sampling) :
Troncature d'une distribution du token suivant à ses `k` tokens de plus forte probabilité, en écartant les autres, puis échantillonnage dans cet ensemble de taille fixe renormalisé. Contrairement à l'échantillonnage nucleus (top-p), la taille de l'ensemble éligible ne s'adapte jamais au caractère plus ou moins piqué de la distribution à une étape donnée.
_À éviter_ : échantillonnage nucleus (top-p) (une alternative de taille dynamique ; le nombre de coupure du top-k est fixe, quelle que soit la forme réelle de la distribution)

**Initialisation de Xavier (Glorot)** (Xavier initialization) :
Mise à l'échelle de la variance initiale des poids d'une couche selon son fan-in et son fan-out (le nombre d'entrées et de sorties auxquelles elle est reliée), au lieu d'employer une variance fixe pour toutes les couches, afin que la variance des activations et des gradients reste à peu près constante d'une couche à l'autre d'un réseau profond, au lieu de diminuer ou de croître de façon cumulative à chaque couche.
_À éviter_ : une seule variance d'initialisation fixe pour toutes les couches, quelle que soit leur taille (le problème que l'initialisation de Xavier a été conçue précisément pour corriger)
