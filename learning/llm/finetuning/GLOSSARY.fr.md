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

_Ajoutés au fur et à mesure que les leçons les établissent._
