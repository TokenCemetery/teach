---
title: "Glossaire"
description: "Termes de référence pour le pré-entraînement des LLM"
type: glossary
---

# Glossaire du pré-entraînement des LLM

Termes de référence pour entraîner un modèle à partir d'une initialisation aléatoire, à grande échelle : de quoi se composent les données et le budget de calcul, et comment la mémoire et le calcul se répartissent sur de nombreux appareils.

## Termes

**Activation checkpointing** (recalcul d'activations) :
Jeter les activations intermédiaires pendant la passe avant et les recalculer pendant la passe arrière, en échangeant du calcul supplémentaire contre une consommation de mémoire plus faible.
_À éviter_ : gradient checkpointing (le nom le plus courant en pratique, mais il s'agit de checkpointer des activations, pas des gradients, et ce nom imprécis induit en erreur sur ce qu'on échange)

**Compute-optimal** :
Le point du compromis entre nombre de paramètres et nombre de tokens d'entraînement qui minimise la loss pour un budget de calcul d'entraînement fixé, par opposition à un modèle plus grand entraîné sur moins de tokens que ce point ne l'implique.
_À éviter_ : optimal (ne dit pas optimal pour quoi ; associez-le toujours à « compute » ou à « inference » pour dire quel budget est fixé)

**Parallélisme de données** (data parallelism) :
Répartir un batch d'entraînement entre des appareils qui détiennent chacun une copie complète du modèle, calculer les gradients de façon indépendante, puis les synchroniser par un all-reduce avant le pas de l'optimizer.
_À éviter_ : entraînement distribué (le parallélisme de données n'en est qu'une forme ; le terme général cache la ressource qui est répartie)

**Déduplication** (deduplication) :
Retirer d'un corpus d'entraînement les documents quasi dupliqués ou exactement dupliqués avant la tokenisation, parce que le texte répété est une cause majeure de mémorisation et de calcul gaspillé.
_À éviter_ : dedup (acceptable à l'oral, mais le glossaire écrit le mot en entier une fois le concept posé)

**Gradient clipping** (écrêtage du gradient) :
Remettre un gradient à l'échelle de façon proportionnelle, avant que le pas de l'optimizer ne l'utilise, pour que sa norme globale ne dépasse jamais un seuil choisi, ce qui borne l'ampleur d'une seule mise à jour quelle que soit la cause d'un gradient anormalement grand.
_À éviter_ : gradient clamping (le clamping désigne en général le fait de borner chaque valeur indépendamment ; le clipping, ici, remet à l'échelle tout le vecteur gradient par un seul facteur pour borner sa norme)

**Warmup du learning rate** (learning rate warmup) :
Faire monter le learning rate depuis une valeur proche de zéro jusqu'à son maximum prévu pendant le premier segment de l'entraînement, au lieu de partir directement du maximum, pour que les premières mises à jour du réseau, les moins informées, pèsent moins sur les poids.
_À éviter_ : burn-in (un terme d'autres domaines pour une période de stabilisation ; cet espace de travail emploie warmup précisément pour la montée du learning rate)

**Pic de loss** (loss spike) :
Une hausse soudaine et brutale de la loss d'entraînement en cours de run, généralement causée par un batch numériquement instable ou par une dérive accumulée de l'état de l'optimizer, et qu'on distingue du bruit ordinaire selon que la loss se rétablit d'elle-même ou non.
_À éviter_ : divergence (la divergence est l'issue quand un pic de loss ne se rétablit pas ; les deux ne sont pas le même événement)

**Parallélisme de pipeline** (pipeline parallelism) :
Répartir les couches d'un modèle entre des appareils, chacun détenant une tranche contiguë de la pile et transmettant ses activations au suivant, en faisant circuler plusieurs micro-batches dans ce pipeline pour que chaque appareil reste occupé.
_À éviter_ : parallélisme de modèle (le terme plus large dont relèvent celui-ci et le parallélisme tensoriel ; employez le terme précis dès que la distinction compte)

**Loi d'échelle** (scaling law) :
Une relation empirique en loi de puissance entre la loss d'un modèle et le calcul, le nombre de paramètres ou les données avec lesquels il a été entraîné, utilisée pour prédire la loss d'un run d'entraînement avant de le payer.
_À éviter_ : courbe d'échelle (une loi d'échelle est la relation ajustée ; une courbe n'en est qu'un tracé)

**Parallélisme tensoriel** (tensor parallelism) :
Répartir les matrices de poids d'une couche entre des appareils, pour qu'une seule multiplication matricielle soit calculée comme la somme de produits partiels issus de chaque appareil, au prix d'une étape de communication par couche répartie.
_À éviter_ : parallélisme de modèle (le terme plus large dont relèvent celui-ci et le parallélisme de pipeline)

**Ratio tokens par paramètre** (tokens-per-parameter ratio) :
Le nombre de tokens d'entraînement divisé par le nombre de paramètres du modèle, le nombre unique autour duquel se construit un plan d'entraînement compute-optimal.
_À éviter_ : ratio données sur modèle (employé de façon incohérente dans la littérature pour la quantité inverse ; cet espace de travail désigne toujours les tokens divisés par les paramètres)

**Stage ZeRO** (ZeRO stage) :
L'un des trois niveaux croissants d'état réparti entre les appareils en parallélisme de données : l'état de l'optimizer (stage 1), l'état de l'optimizer et les gradients (stage 2), ou l'état de l'optimizer, les gradients et les paramètres (stage 3), chacun échangeant plus de communication contre moins de mémoire par appareil.
_À éviter_ : FSDP (FSDP est l'implémentation par PyTorch d'un partitionnement de type ZeRO stage 3 ; ZeRO est la technique sous-jacente, et cet espace de travail emploie le nom de la technique quand il parle de l'idée et FSDP quand il parle de l'API)
