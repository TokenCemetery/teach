---
title: "2. Données d'instruction et chat template"
description: "Un token spécial marque l'endroit où un prompt se termine et où une réponse commence, et cette frontière doit être la même à l'entraînement et au déploiement"
type: lesson
---

# Leçon 2. Données d'instruction et chat template

**Lien avec la mission :** « Écrire une boucle d'entraînement SFT qui masque la loss sur les tokens hors assistant, et expliquer ce qui casse dans un modèle de chat entraîné sans ce masque » est la première puce sous « Objectif ». Cette leçon couvre l'aspect des données SFT et la façon dont leurs segments sont marqués ; la leçon 3 couvre le masquage lui-même.
**Source primaire :** [Article : "Llama 2: Open Foundation and Fine-Tuned Chat Models", Touvron et al., 2023](https://arxiv.org/abs/2307.09288)
**Prérequis :** [Leçon 1](0001-what-post-training-buys.md)

## Échauffement

1. ▢ Qu'est-ce qu'une taxe d'alignement, et qu'ont trouvé Ouyang et al. qui pouvait la compenser en partie ?

<details markdown="1"><summary>Vérifier</summary>

Une baisse mesurée de performance sur certains benchmarks NLP publics, qui accompagnait les gains d'alignement du post-training. Mélanger les mises à jour PPO avec des mises à jour qui augmentent la vraisemblance des données de pré-entraînement d'origine (PPO-ptx) a récupéré une grande part de cette performance perdue sans renoncer aux gains de préférence.

</details>

## À savoir

### À quoi ressemblent réellement les données SFT

Les données de **supervised fine-tuning (SFT)** sont un ensemble de paires prompt-réponse, exactement la forme que décrivait l'étape 1 de la leçon 1. Touvron et al. donnent de vrais exemples tirés de l'annotation SFT propre à Llama 2 : un prompt demandant un poème sur les dix premiers éléments du tableau périodique, associé à un poème écrit par un annotateur qui y répond ; un prompt demandant un « roast » volontairement cruel, associé à un refus écrit par un annotateur qui explique pourquoi. Chacun n'est qu'un prompt et la réponse exacte que l'annotateur veut que le modèle apprenne à produire pour lui.

### Marquer où un segment se termine et où le suivant commence

Entraîner sur ces données revient à concaténer de nombreuses paires prompt-réponse dans le corpus d'entraînement, et le modèle a besoin d'un moyen de savoir où un prompt se termine et où sa réponse commence, puisque rien dans un texte brut ne marque cette frontière de lui-même. Touvron et al. décrivent exactement cela : « un token spécial est utilisé pour séparer les segments de prompt et de réponse ». C'est le germe de ce qu'on appelle un **chat template** : une manière fixe et cohérente de marquer les frontières de rôle (un segment de prompt, un segment de réponse et, dans une conversation multi-tours, un message système et chaque tour successif) avec des tokens spéciaux, pour que la même structure apparaisse à chaque fois à l'entraînement et puisse être reproduite à l'identique au déploiement.

### Pourquoi la frontière doit être la même à l'entraînement et au déploiement

Un chat template n'est pas qu'une commodité de mise en forme ; il fait partie de ce sur quoi le modèle a réellement été entraîné. Le modèle a appris à associer les tokens spéciaux marquant « c'est ici que commence une réponse » à la production du type de réponse qui suivait ces tokens pendant l'entraînement. Déployer le modèle avec un autre template, d'autres tokens spéciaux, un autre ordre des rôles ou sans la convention du message système, lui présente une structure qu'il n'a jamais vue associée au comportement appris, et son comportement se dégrade ou devient imprévisible. Reproduire au déploiement le template exact de l'entraînement n'est pas un nettoyage facultatif ; cela fait partie de l'utilisation correcte du modèle tout court.

### Le multi-tours est la même idée, répétée

Une conversation multi-tours étend cette même idée de marquage de segments à plus d'un échange : un message système (s'il y en a un), puis des tours alternés d'utilisateur et d'assistant, chacun marqué avec le même type de tokens spéciaux que ceux qui séparent n'importe quel prompt de sa réponse. Rien de nouveau n'est inventé pour le cas multi-tours ; c'est le même principe de marquage des frontières, appliqué une fois par tour au lieu d'une fois par exemple.

## Pratique

1. ▢ Pourquoi un modèle ne peut-il pas apprendre où un prompt se termine et où sa réponse commence à partir du seul texte concaténé, sans une forme de marqueur ?

<details markdown="1"><summary>Vérifier</summary>

Parce que le texte brut ne porte aucun signal propre distinguant « voici ce qui a été demandé » de « voici la réponse que je dois apprendre à produire » ; sans marqueur, la frontière entre les deux n'est représentée nulle part dans les données d'entraînement elles-mêmes.

</details>

2. ▢ Une équipe fine-tune un modèle avec un chat template, mais le déploie en production avec un autre template (d'autres tokens spéciaux marquant les frontières de rôle). Quelle est la conséquence la plus probable ?

    - a) Aucun effet ; le modèle ignore entièrement la mise en forme
    - b) Le comportement du modèle se dégrade ou devient imprévisible, puisqu'on lui présente une structure qu'il n'a jamais vue associée au comportement appris pendant l'entraînement
    - c) Le modèle détecte automatiquement le nouveau template et s'y adapte
    - d) Seul le message système est affecté ; les tours d'utilisateur et d'assistant fonctionnent toujours normalement

<details markdown="1"><summary>Vérifier</summary>

**b)** est la conséquence réelle : le chat template fait partie de ce sur quoi le modèle a été entraîné, ce n'est pas un emballage cosmétique, donc une incohérence présente une structure jamais entraînée. (a), (c) et (d) supposent toutes une robustesse à l'incohérence de template que l'entraînement ne donne aucune raison d'attendre.

</details>

3. ▢ Quel rapport y a-t-il entre le chat template d'une conversation multi-tours et le template simple prompt-réponse que décrivent Touvron et al. pour le SFT ?

<details markdown="1"><summary>Vérifier</summary>

C'est la même idée de marquage de segments, appliquée de façon répétée : un message système s'il y en a un, puis chaque tour d'utilisateur et d'assistant à la suite, chacun marqué avec le même type de tokens spéciaux que ceux qui séparent un prompt unique de sa réponse, sans qu'il faille un mécanisme fondamentalement différent.

</details>

## Exercices en situation réelle

- [ ] Trouvez le chat template d'un modèle ouvert auquel vous avez accès (beaucoup sont publiés sous forme de fichier de template ou documentés directement), et identifiez les tokens spéciaux qu'il utilise pour marquer un message système, un tour d'utilisateur et un tour d'assistant.
- [ ] Lisez les deux exemples d'annotations SFT de Touvron et al. (liés plus haut, tableau 5) et écrivez, avec vos propres mots, ce qui distingue une bonne réponse SFT d'une réponse simplement plausible, à partir de l'exemple du refus de « roast ».
- [ ] Demain : sans regarder la suite, écrivez une prédiction d'une phrase pour la leçon 3 : si un chat template concatène un prompt et une réponse en une seule séquence sans espace, et que l'entraînement utilise une loss ordinaire de prédiction du token suivant sur toute la séquence, que commencerait à apprendre le modèle à faire des tokens du prompt eux-mêmes, alors qu'il ne devrait pas ?

## Pour aller plus loin

- [Article : "Llama 2: Open Foundation and Fine-Tuned Chat Models", Touvron et al., 2023](https://arxiv.org/abs/2307.09288)
- [Ressources](../RESOURCES.md)

---

Ça ne passe pas ? Relisez la source primaire en haut de page, car cette leçon la condense et c'est dans la condensation que la compréhension s'échappe. Consultez le [glossaire](../GLOSSARY.md) pour tout terme qui vous a paru glissant.

Si c'est la leçon elle-même qui n'est pas claire plutôt que la matière, c'est un défaut : [ouvrez une issue](https://github.com/TokenCemetery/teach/issues).
