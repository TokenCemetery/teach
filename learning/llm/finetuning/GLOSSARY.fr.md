---
title: "Glossaire"
description: "Termes de référence pour le fine-tuning avec adapters"
type: glossary
---

# Glossaire du fine-tuning avec adapters

Termes de référence pour cet espace de travail. Un terme arrive ici quand on sait l'employer correctement, pas dès qu'il est mentionné pour la première fois : ce glossaire grandit donc au fil des leçons acquises.

## Usage dans cet espace de travail

Trois mots sont employés de façon floue dans le domaine, d'une manière qui rendrait les leçons suivantes ambiguës. Ils sont donc fixés dès le départ :

**Fine-tuning** :
Entraîner sur une tâche un petit ensemble de paramètres ajoutés ou sélectionnés, pendant que les poids du base model restent gelés. Quand tous les poids sont entraînés, cet espace de travail dit toujours _full fine-tuning_ explicitement.
_À éviter_ : entraînement, ré-entraînement, enseigner au modèle

**Adapter** :
Le petit ensemble de poids entraînables ajouté à côté d'un base model gelé, avec la configuration qui décrit où il se rattache.
_À éviter_ : fine-tune (comme nom), LoRA (quand la méthode n'est pas précisément LoRA), checkpoint

**Quantification** :
Stocker les poids avec une précision numérique plus basse que celle dans laquelle ils ont été entraînés. Dans cet espace de travail, elle désigne toujours le _base model gelé_, sauf mention contraire : les adapters restent à plus haute précision, et la quantification pour l'inférence est un sujet distinct.
_À éviter_ : compression, rétrécissement, optimisation

## Termes

**Base model** :
Un modèle entraîné sur un seul objectif, prédire le token suivant sur un grand corpus. Il prolonge le texte au lieu d'y répondre, et il n'a pas de _chat template_.
_À éviter_ : modèle brut, modèle pré-entraîné (quand la distinction avec un _instruct model_ compte)

**Oubli catastrophique** :
La dégradation, pendant le fine-tuning, des capacités que les données d'entraînement n'ont pas renforcées, comme le suivi d'instructions général. Elle n'apparaît ni dans la loss de la tâche ni dans la métrique held-out, qui peuvent s'améliorer pendant qu'elle se produit.
_À éviter_ : surapprentissage (une autre défaillance, visible sur le _jeu held-out_ de la tâche elle-même)

**Chat template** :
Le format de chaîne exact dans lequel les conversations d'entraînement d'un modèle de chat ont été rendues, qui transforme rôles et messages en une seule séquence plate de tokens. L'entraînement et le déploiement doivent utiliser le même rendu.
_À éviter_ : format de prompt, format de chat

**Contamination** :
Des exemples de test que le modèle a déjà vus. La contamination _propre_ désigne les exemples de test qui apparaissent aussi, à l'identique ou presque, dans votre jeu d'entraînement ; la contamination _héritée_ désigne les exemples de test qui figuraient dans le corpus de pré-entraînement du _base model_.
_À éviter_ : fuite (précisez laquelle des deux sortes est visée)

**DoRA** :
Une variante de _LoRA_ qui sépare chaque matrice de poids gelée en un vecteur de magnitude, entraîné directement, et une direction, qui reçoit la mise à jour de faible rang et est renormalisée ensuite. Dans PEFT, c'est un drapeau de la configuration LoRA, pas une méthode séparée.
_À éviter_ : LoRA à poids décomposés (ne l'écrire en toutes lettres qu'une fois, puis dire DoRA)

**Double quantification** :
La _quantification_ des échelles par blocs elles-mêmes : les échelles fp32 du premier niveau sont regroupées et stockées sur 8 bits avec leur propre échelle de second niveau.
_À éviter_ : quantification imbriquée, quantification sur 2 bits

**Taille de batch effective** :
Le nombre d'exemples dont les gradients sont moyennés en un pas d'optimiseur : batch size par appareil × pas d'accumulation de gradient × nombre d'appareils.
_À éviter_ : batch size (quand c'est le nombre par appareil qui est visé)

**Gradient checkpointing** :
Ne conserver que l'entrée de chaque bloc pendant la passe avant et relancer le bloc quand la passe arrière l'atteint, de sorte que les activations stockées croissent environ comme la racine carrée de la profondeur au lieu d'être linéaires, pour environ une passe avant supplémentaire par pas.
_À éviter_ : checkpointing (seul, puisqu'un checkpoint d'entraînement est un ensemble de poids sauvegardé sur disque), recalcul des activations

**Jeu held-out** :
Des données sur lesquelles le modèle n'est pas entraîné, utilisées pour mesurer s'il a appris la tâche. Dans cet espace de travail, il a deux parties : la validation, sur laquelle on choisit les réglages et les checkpoints, et le test, qu'on ne touche qu'une fois à la fin.
_À éviter_ : jeu d'éval, jeu de dev

**Instruct model** :
Un _base model_ entraîné plus avant sur des paires instruction-réponse, et en général ensuite sur des données de préférence. Modèle de chat a ici le même sens.
_À éviter_ : modèle aligné, modèle assistant

**LoRA** :
Low-rank adaptation (adaptation de faible rang) : un _adapter_ qui apprend la mise à jour d'une matrice de poids comme le produit de deux petites matrices, `ΔW = BA`, mis à l'échelle par `α/r`, pendant que la matrice elle-même reste gelée.
_À éviter_ : adapter (quand la méthode précise est visée), fine-tune de faible rang

**LoRA alpha** :
Le scalaire fixe `α` (`lora_alpha`) qui met à l'échelle une mise à jour _LoRA_ par `α/r`. Ce qui fixe l'échelle de la mise à jour, c'est le rapport `α/r`, pas l'un ou l'autre nombre seul.
_À éviter_ : facteur d'échelle (c'est `α/r`, pas `α`)

**Fusion** :
Intégrer une mise à jour _LoRA_ dans les poids de base, `W₀ + (α/r)BA`, et abandonner la structure de l'adapter. Elle est exacte face à une base en pleine précision et avec perte face à une base quantifiée.
_À éviter_ : export, incorporation

**Multi-adapter serving** :
Servir plusieurs _adapters_ sur une même base partagée en regroupant dans un même batch des requêtes qui utilisent des adapters différents : le calcul de la base est partagé dans le batch, et la contribution de l'adapter de chaque requête est calculée séparément.
_À éviter_ : permutation d'adapters (l'approche naïve qui sérialise les requêtes)

**NF4** :
NormalFloat, un format 4 bits dont les 16 niveaux sont espacés pour des valeurs distribuées normalement autour de zéro, comme le sont les poids, au lieu de l'être à intervalles égaux comme dans int4 simple. Il est utilisé dans la _quantification_ par blocs, sur des blocs déjà normalisés par leur absmax.
_À éviter_ : int4 (un autre format, à espacement uniforme)

**État de l'optimizer** :
Les tenseurs qu'un optimizer conserve par paramètre entraînable en plus du poids et de son gradient. Pour AdamW, ce sont le premier et le second moment, 4 octets chacun.
_À éviter_ : cache de l'optimizer, momentum (seulement le premier moment)

**Packing** :
Concaténer des exemples d'entraînement courts en séquences de pleine longueur, pour qu'un batch ne contienne presque pas de padding.
_À éviter_ : regroupement par longueur (un autre remède, qui regroupe dans un même batch des séquences de tailles voisines)

**QLoRA** :
_LoRA_ entraîné contre une base gelée stockée en _NF4_ avec _double quantification_, qui est déquantifiée à chaque passe avant et arrière. C'est du LoRA avec une base moins chère, pas une méthode avec ses propres hyperparamètres.
_À éviter_ : fine-tuning 4 bits, LoRA quantifié (quand cela suggère que l'adapter est quantifié)

**Rank** :
La dimension interne `r` des deux matrices _LoRA_, `A` étant `r × d_in` et `B` étant `d_out × r`. C'est la capacité de l'adapter : elle borne la complexité de la mise à jour qu'il peut exprimer.
_À éviter_ : taille, dimension (seule)

**Jeu de régression** :
Un ensemble fixe de sondes hors de la tâche (suivi d'instructions général, respect du format et du comportement, sécurité et refus, capacités voisines), exécuté avant et après l'entraînement pour détecter l'_oubli catastrophique_. C'est un instrument différent du _jeu held-out_, et il faut les deux.
_À éviter_ : benchmark, suite d'évaluation (quand cet instrument précis est visé)

**Target modules** :
Les matrices de poids auxquelles un _adapter_ se rattache, désignées par les noms de modules du modèle lui-même.
_À éviter_ : couches (un adapter se rattache à des matrices précises à l'intérieur d'une couche)
