---
title: "Glossaire"
description: "Termes de référence pour la distillation des connaissances des LLM"
type: glossary
---

# Glossaire de la distillation

Termes de référence pour entraîner un modèle plus petit à partir des sorties d'un plus grand, les loss et les données qui portent le signal, et la façon de juger le résultat. Dans cet espace de travail, « distillation » désigne toujours la distillation des connaissances d'un modèle enseignant vers un modèle élève ; elle ne désigne jamais la distillation de dataset ni la distillation d'un prompt.

## Termes

**Beam search** (recherche en faisceau) :
Méthode de décodage qui garde, à chaque étape, les quelques séquences partielles ayant les meilleurs scores et renvoie la meilleure séquence complète, comme approximation de la séquence la plus probable.
_À éviter_ : recherche gloutonne (c'est un faisceau de taille 1), décodage best-first

**Écart de capacité** (capacity gap) :
Baisse de qualité de l'élève qui peut apparaître quand l'enseignant est bien plus grand que lui, si bien qu'un enseignant plus fort produit un élève moins bon qu'un enseignant plus faible.
_À éviter_ : enseignant trop intelligent, écart de taille

**Loss combinée** (combined loss) :
Loss de distillation qui ajoute l'entropie croisée par rapport aux hard labels à la divergence par rapport aux soft targets de l'enseignant, pondérées par un coefficient de mélange.
_À éviter_ : loss hybride, double loss

**Distillation inter-tokenizers** (cross-tokenizer distillation) :
Distillation de logits entre un enseignant et un élève dont les vocabulaires diffèrent, réalisée en alignant ou en comparant leurs distributions sans index de tokens partagé.
_À éviter_ : distillation sans tokenizer, transfert de vocabulaire

**Décontamination** (decontamination) :
Retrait des données d'entraînement des exemples qui correspondent à un jeu d'évaluation ou lui ressemblent de près, pour qu'un score de benchmark ne mesure pas des éléments mémorisés.
_À éviter_ : nettoyage (trop large), déduplication (elle retire les doublons à l'intérieur du jeu d'entraînement)

**Distillation** :
Entraîner un modèle élève à reproduire le comportement d'un modèle enseignant, en prenant comme signal d'entraînement les distributions de sortie ou le texte généré de l'enseignant.
_À éviter_ : compression (trop large), copie de modèle

**Loi d'échelle de la distillation** (distillation scaling law) :
Relation ajustée, due à Busbridge et al., qui prédit l'entropie croisée d'un élève à partir de sa taille, du nombre de tokens de distillation et de l'entropie croisée de l'enseignant.
_À éviter_ : loi de distillation, scaling du KD

**Biais d'exposition** (exposure bias) :
Écart entre un entraînement sur des préfixes écrits par quelqu'un d'autre et une génération à partir de préfixes que le modèle a écrits lui-même, si bien que ses propres erreurs précoces le placent dans des états sur lesquels il ne s'est jamais entraîné.
_À éviter_ : décalage entraînement-test (trop large), dérive

**Fidélité** (fidelity) :
Degré d'accord entre les prédictions d'un élève et celles de son enseignant, mesuré sur les mêmes entrées, par opposition à la qualité de l'un ou de l'autre sur la tâche.
_À éviter_ : exactitude (accuracy), faithfulness

**KL directe** (forward KL) :
Divergence KL(teacher ‖ student), moyennée sous la distribution de l'enseignant, qui pénalise l'élève quand il met peu de probabilité là où l'enseignant en met beaucoup, et le pousse donc à couvrir tous les modes.
_À éviter_ : KL qui couvre les modes sans nommer la direction, KL tout court

**Distillation généralisée des connaissances** (generalized knowledge distillation) :
Méthode on-policy d'Agarwal et al. qui entraîne l'élève sur un mélange de séquences fixes et de séquences générées par l'élève, évaluées token par token par rapport à l'enseignant avec une divergence au choix. Abrégée GKD.
_À éviter_ : KD généralisé, distillation générique

**Hard label** (label dur) :
La seule classe ou le seul token correct utilisé comme cible d'entraînement, avec toute sa probabilité sur une seule réponse.
_À éviter_ : vérité terrain (ground truth, ce peut être l'argmax de l'enseignant), cible one-hot sans contexte

**Écart d'imitation** (imitation gap) :
Distance entre la ressemblance d'un élève avec son enseignant dans le style et la part des capacités de l'enseignant qu'il possède réellement, l'imitation avec un budget limité comblant l'écart de style bien plus vite que celui des capacités.
_À éviter_ : fausse promesse (le titre de l'article, pas un terme), transfert de style

**Divergence KL** (KL divergence) :
Pour deux distributions P et Q sur les mêmes tokens, somme sur les tokens de P log(P / Q) : une mesure non symétrique de l'éloignement de Q par rapport à P. Ses deux directions en distillation sont la KL directe et la KL inverse.
_À éviter_ : distance KL, entropie relative sans présenter le terme

**Logit** :
Score brut, non normalisé, d'un modèle pour une classe ou un token avant que le softmax transforme les scores en probabilités.
_À éviter_ : score (ambigu), log-probabilité (elle vient après le softmax)

**Distillation de logits** (logit distillation) :
Distillation dont le signal d'entraînement est la distribution de sortie complète de l'enseignant à chaque position, ce qui exige l'accès aux logits de l'enseignant et un vocabulaire partagé.
_À éviter_ : distillation white-box (alias accepté, mais utilisez un seul terme), distillation douce

**Distillation off-policy** (off-policy distillation) :
Distillation sur des séquences que l'élève n'a pas générées : des données humaines ou les propres sorties de l'enseignant, fixées avant l'entraînement.
_À éviter_ : distillation hors ligne, distillation supervisée

**Distillation on-policy** (on-policy distillation) :
Distillation sur des séquences que l'élève génère pendant l'entraînement, l'enseignant évaluant chaque token choisi par l'élève, de sorte que l'élève s'entraîne sur ses propres erreurs.
_À éviter_ : distillation en ligne (aussi employée quand l'enseignant est entraîné en même temps que l'élève), auto-distillation

**Rationale** (justification de raisonnement) :
Raisonnement intermédiaire qu'un enseignant écrit avant sa réponse ou avec elle, utilisé comme cible d'entraînement supplémentaire pour que l'élève apprenne comment la réponse a été obtenue.
_À éviter_ : explication (correct dans le texte courant, pas comme terme), chain-of-thought (la technique de prompting qui le produit)

**Échantillonnage par rejet** (rejection sampling) :
Tirer plusieurs sorties candidates d'un modèle pour chaque prompt et ne garder que celles qui passent une vérification, comme une réponse finale correcte.
_À éviter_ : filtrage (trop large), best-of-n (qui garde un seul gagnant au lieu d'écarter selon une vérification)

**KL inverse** (reverse KL) :
Divergence KL(student ‖ teacher), moyennée sous la distribution de l'élève, qui pénalise l'élève quand il met de la probabilité là où l'enseignant en met peu, et le pousse donc à s'engager sur un seul mode.
_À éviter_ : KL qui cherche un mode sans nommer la direction, KL arrière (backward KL)

**Distillation au niveau de la séquence** (sequence-level distillation) :
Distillation dans laquelle l'élève est entraîné avec une entropie croisée ordinaire sur des séquences entières décodées par l'enseignant, plutôt que sur les distributions par token de l'enseignant.
_À éviter_ : distillation dure, distillation black-box (qui couvre aussi la distillation à partir de données générées)

**Soft targets** (cibles douces) :
La distribution de probabilité complète de l'enseignant sur les classes ou les tokens, utilisée comme cible d'entraînement à la place du hard label ou en plus de lui.
_À éviter_ : soft labels (alias accepté, mais utilisez un seul terme), dark knowledge (l'information qu'elles portent, pas les cibles)

**Élève** (student) :
Le modèle entraîné dans une distillation, généralement plus petit ou moins coûteux à exécuter que l'enseignant.
_À éviter_ : modèle distillé avant la fin de l'entraînement, modèle enfant

**Apprentissage subliminal** (subliminal learning) :
Fait pour un élève d'acquérir un trait de son enseignant à partir de données sémantiquement sans rapport avec ce trait, observé par Cloud et al. quand les deux partagent le même base model.
_À éviter_ : distillation cachée, empoisonnement de données (qui est délibéré)

**Référence supervisée** (supervised baseline) :
Modèle de la taille de l'élève entraîné sans distillation, sur les mêmes données ou avec le même calcul, utilisé comme comparaison qui montre si la distillation est la cause d'un résultat.
_À éviter_ : modèle de contrôle (trop large), modèle simple

**Données synthétiques** (synthetic data) :
Exemples d'entraînement générés par un modèle plutôt qu'écrits par des personnes. Dans cet espace de travail, il s'agit des données générées par l'enseignant pour l'élève.
_À éviter_ : fausses données, données augmentées (l'augmentation transforme des exemples existants)

**Enseignant** (teacher) :
Le modèle dont les sorties sont le signal d'entraînement d'une distillation. Il est fixe pendant l'entraînement et généralement plus grand ou plus capable que l'élève.
_À éviter_ : oracle, modèle parent

**Assistant enseignant** (teacher assistant) :
Modèle de taille intermédiaire distillé à partir de l'enseignant, puis utilisé comme enseignant d'un élève plus petit, pour combler un écart de capacité.
_À éviter_ : enseignant intermédiaire sans présenter le terme, modèle TA

**Teacher forcing** :
Fournir à un modèle un préfixe fixe plutôt que ses propres sorties précédentes, si bien qu'une seule passe avant donne une distribution du token suivant à chaque position d'une séquence.
_À éviter_ : décodage avec teacher forcing, free running (c'est l'inverse)

**Température** (temperature) :
Le diviseur T appliqué aux logits avant le softmax. Un T supérieur à 1 aplatit la distribution et élève les probabilités des réponses improbables pour que l'élève puisse en apprendre. C'était la valeur par défaut de l'ère des classifieurs ; les runs de distillation de LLM dans les sources de cet espace de travail ont trouvé que T égal à 1 était le meilleur.
_À éviter_ : température d'échantillonnage (même opération, but différent), douceur

**Distillation au niveau du token** (token-level distillation) :
Distillation de logits appliquée à chaque position d'une séquence, en minimisant une divergence entre les distributions du token suivant de l'enseignant et de l'élève.
_À éviter_ : distillation au niveau du mot (le nom de l'article d'origine), KD par token

**Accord top-1** (top-1 agreement) :
Part des entrées sur lesquelles la réponse de plus haute probabilité d'un élève est la même que celle de son enseignant, l'une des deux métriques de fidélité de Stanton et al.
_À éviter_ : exactitude (accuracy, qui se mesure par rapport à la bonne réponse), taux de correspondance

**Logits top-k** (top-k logits) :
Les k plus grandes entrées de la distribution de sortie d'un enseignant à une position, conservées avec leurs indices de tokens à la place de la ligne complète du vocabulaire, pour réduire le stockage.
_À éviter_ : logits creux, softmax tronqué sans dire ce que devient la masse écartée
