---
title: Glossaire
description: "Termes de référence pour le prompting"
type: glossary
---

# Glossaire du prompting

Termes de référence pour écrire, structurer, versionner, mesurer et sécuriser les prompts qui se trouvent derrière une fonctionnalité LLM.

## Termes

**Chain-of-thought** (chaîne de raisonnement) :
Raisonnement intermédiaire que le modèle écrit avant sa réponse finale, obtenu grâce à des exemples qui le montrent ou à une consigne qui le demande.
_À éviter_ : CoT dans le texte courant (acceptable dans un titre ou un tableau), thinking (réservé ici à la phase de raisonnement intégrée d'un modèle de raisonnement)

**Chat template** (gabarit de conversation) :
Règle propre à chaque modèle qui transforme une liste de messages étiquetés par rôle en la séquence unique de tokens sur laquelle le modèle a été entraîné, y compris les tokens spéciaux qui marquent le début et la fin de chaque rôle.
_À éviter_ : format de prompt

**Décodage contraint** :
Limitation des tokens que le modèle peut générer à chaque étape, pour que la sortie respecte une grammaire ou un schéma, comme le fait la fonctionnalité de sortie structurée imposée par un fournisseur.
_À éviter_ : échantillonnage par grammaire

**Délimiteur** :
Balisage dans un prompt, comme une balise de style XML ou un bloc délimité, qui marque où un type de contenu se termine et où un autre commence, le plus souvent pour séparer les données des instructions.
_À éviter_ : séparateur

**Prompt few-shot** :
Prompt qui inclut, avant l'entrée réelle, des exemples travaillés de la tâche, chacun associant une entrée à la sortie souhaitée.
_À éviter_ : prompt multishot, entraînement en contexte

**Injection de prompt indirecte** :
Injection de prompt véhiculée par un contenu que le modèle lit pour le compte de l'utilisateur, comme une page web, un e-mail ou un document récupéré, plutôt que saisie par la personne qui dialogue avec lui.
_À éviter_ : injection de second ordre

**Hiérarchie des instructions** :
Ordre de priorité que le modèle est entraîné à appliquer quand les instructions entrent en conflit : le system prompt prime sur le tour de l'utilisateur, et le tour de l'utilisateur prime sur le contenu renvoyé par les outils ou la récupération.
_À éviter_ : ordre de priorité

**Jailbreak** :
Entrée conçue pour faire produire à un modèle ce que son entraînement à la sécurité refuse. Elle vise les limites du modèle lui-même, alors que l'injection de prompt vise les instructions de l'application.
_À éviter_ : injection de prompt (une autre cible)

**Triade létale** (lethal trifecta) :
Combinaison de l'accès à des données privées, de l'exposition à du contenu non fiable et d'un moyen d'envoyer des données à l'extérieur, qui rend ensemble l'injection de prompt exploitable. Supprimer l'un des trois éléments ferme la voie d'attaque.
_À éviter_ : risque d'injection (trop vague pour agir)

**Snapshot de modèle** :
Version figée d'un modèle, désignée par un identifiant de modèle exact, dont le fournisseur ne modifie pas les poids. Un alias pratique peut pointer vers un snapshot plus récent au fil du temps.
_À éviter_ : version du modèle (ambigu avec une génération de modèle)

**Comparaison appariée** :
Comparaison de deux prompts ou de deux modèles sur les mêmes entrées, à partir des cas où leurs résultats diffèrent plutôt qu'à partir de leurs deux totaux.
_À éviter_ : comparaison de scores A/B

**Prompt** :
Tout ce que le modèle reçoit pour un appel : le system prompt, chaque message de la conversation jusque-là et tout contenu inséré, le tout rendu par le chat template en une seule séquence de tokens.
_À éviter_ : requête (c'est la question de l'utilisateur au sein du prompt)

**Prompt caching** (mise en cache de prompt) :
Fonctionnalité d'un fournisseur qui conserve l'état traité d'un préfixe de prompt, afin que les appels suivants partageant exactement ce préfixe évitent de le recalculer, ce qui réduit le coût et la latence.
_À éviter_ : cache de réponses (autre chose : stocker des réponses entières)

**Injection de prompt** :
Entrée qui pousse le modèle à suivre des instructions autres que celles voulues par l'auteur du prompt.
_À éviter_ : jailbreak (un jailbreak vise l'entraînement à la sécurité du modèle, l'injection vise les instructions de l'application)

**Gabarit de prompt** (prompt template) :
Texte fixe d'un prompt comportant des emplacements nommés, remplis au moment de l'appel avec des valeurs propres à chaque requête, comme le message de l'utilisateur ou un document récupéré.
_À éviter_ : chaîne de prompt

**Modèle de raisonnement** :
Modèle entraîné à produire une phase de raisonnement interne avant sa réponse visible, de sorte qu'il raisonne sans qu'on le lui demande.
_À éviter_ : modèle thinking

**Jeu de régression** :
Ensemble fixe d'entrées, chacune avec une vérification sur la sortie, qu'une modification de prompt ne doit pas casser, construit surtout à partir d'échecs observés en usage réel.
_À éviter_ : prompts de test, golden set

**Rôle** :
Étiquette de chaque message d'une conversation, généralement system, user ou assistant, que le chat template transforme en tokens spéciaux. Un rôle est un formatage que le modèle a appris à pondérer, pas un canal d'entrée distinct.
_À éviter_ : persona (c'est la description de qui le modèle doit incarner)

**Self-consistency** (auto-cohérence) :
Échantillonnage de plusieurs complétions chain-of-thought pour un même prompt, puis choix de la réponse finale la plus fréquente.
_À éviter_ : ensembling

**Sortie structurée** :
Réponse dans un format lisible par une machine, généralement du JSON conforme à un schéma, qu'un programme analyse au lieu qu'une personne la lise.
_À éviter_ : mode JSON (une fonctionnalité propre à un fournisseur)

**System prompt** :
Message, dans le rôle system, qui fixe la tâche, les contraintes et le contexte du modèle pour toute la conversation, et qui se situe au plus haut de la hiérarchie des instructions.
_À éviter_ : message système, préambule

**Prompt zero-shot** :
Prompt qui énonce la tâche sans aucun exemple travaillé.
_À éviter_ : prompt simple
