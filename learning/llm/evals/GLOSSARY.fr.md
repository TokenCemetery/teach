---
title: "Glossaire"
description: "Termes de référence pour les evals"
type: glossary
---

# Glossaire des evals

Termes de référence pour prouver qu'une modification de modèle a aidé, et pour défendre qu'un chiffre le reflète bien.

## Termes

**Guide d'annotation** (annotation guideline) :
Définition écrite de chaque catégorie de notation, avec des exemples limites concrets et la manière dont ils ont été tranchés, remise à chaque annotateur humain avant qu'il commence. Un faible accord inter-annotateurs signale souvent un guide manquant ou ambigu plutôt que des annotateurs peu fiables.
_À éviter_ : grille de notation (employée comme synonyme ailleurs ; cet espace de travail retient « guide d'annotation »)

**Exactitude des citations** (citation correctness) :
Vérification que le passage précis cité à l'appui d'une affirmation soutient réellement cette affirmation, un contrôle plus strict que la fidélité, fait citation par citation. Une affirmation peut être fidèle (fondée quelque part dans l'ensemble récupéré) tout en étant attribuée à la mauvaise citation, ou à aucune.
_À éviter_ : fidélité (un contrôle voisin mais distinct ; la fidélité demande si une affirmation est soutenue par le contexte récupéré tout court, l'exactitude des citations demande si sa source citée précise la soutient réellement)

**Kappa de Cohen** (Cohen's kappa) :
Statistique qui mesure l'accord entre deux annotateurs après correction de l'accord attendu du seul fait du hasard : `κ = (p_o − p_e) / (1 − p_e)`. Un kappa de 0 signifie pas mieux que le hasard ; un kappa peut devenir négatif. Connu pour sous-estimer l'accord quand une catégorie de notation est beaucoup plus rare que les autres.
_À éviter_ : pourcentage d'accord (le chiffre brut, non corrigé ; le kappa est précisément la version corrigée du hasard, et les deux peuvent raconter des histoires différentes)

**Contamination des données** (data contamination) :
Données d'eval, ou paraphrase proche de celles-ci, qui se retrouvent dans les données d'entraînement d'un modèle (typiquement le pré-entraînement, via un benchmark aspiré dans des données issues du crawl du web), ou modèle réglé de façon itérative sur le même jeu d'eval jusqu'à ce qu'il cesse de mesurer la compétence sous-jacente.
_À éviter_ : fuite, triche

**Dérive** (drift) :
Changement au fil du temps de la relation réelle entre les variables d'entrée et les résultats, si bien qu'un modèle ou une eval construits sur des données plus anciennes cessent progressivement de correspondre à la réalité actuelle. C'est précisément ce qu'indique un écart important entre des données held-out et des données plus récentes (celles du « lendemain ») ; un écart entre résultats hors ligne et résultats en production sur une entrée identique est un autre problème, une erreur d'ingénierie, pas une dérive.
_À éviter_ : décalage entraînement-service (un terme plus large qui couvre tout écart entre entraînement et service ; la dérive est précisément le cas temporel où le monde réel a changé sous le modèle)

**Fidélité** (faithfulness, groundedness) :
Vérification que chaque affirmation d'une réponse générée est réellement soutenue par le contexte récupéré sur lequel elle est censée reposer, plutôt qu'inventée, contredite ou enjolivée d'un détail non soutenu. Un contrôle au niveau de l'affirmation : une réponse en grande partie fidèle peut quand même cacher une affirmation non soutenue.
_À éviter_ : exactitude des citations (un contrôle plus strict et distinct, qui vérifie si le passage précis cité pour une affirmation est bien celui qui la soutient, indépendamment du fait que l'affirmation soit fondée ou non)

**Métrique garde-fou** (guardrail metric) :
Métrique qu'une expérience ou un système de production ne cherche pas à optimiser, suivie précisément pour détecter qu'un changement l'abîme en silence pendant qu'une autre métrique (l'OEC) s'améliore. Rapporter le gain d'un OEC sans vérifier en parallèle une métrique garde-fou peut cacher une vraie régression.
_À éviter_ : OEC (une métrique garde-fou n'est explicitement pas optimisée ; confondre les deux annule l'intérêt de suivre chacune séparément)

**Données held-out** (held-out data) :
Exemples d'eval, ou paraphrases proches de ceux-ci, que le modèle jugé n'a jamais vus pendant l'entraînement ou le fine-tuning. Un score n'est informatif que si les données qui le fondent sont held-out.
_À éviter_ : jeu de test (ambigu avec une partition du pipeline d'entraînement), données non vues

**OEC (Overall Evaluation Criterion, critère d'évaluation global)** :
Métrique précise, ou petite combinaison pondérée, qu'une expérience cherche réellement à faire bouger. Un bon candidat d'OEC est à la fois mobile (assez sensible pour changer dans une expérience réalisable) et lié causalement au résultat qui compte vraiment, pas seulement corrélé à lui.
_À éviter_ : toute métrique facile à faire bouger mais sans lien causal avec le vrai résultat (l'exemple de Kohavi lui-même : « photos viewed » bouge facilement mais a peu d'effet causal sur le chiffre d'affaires)

**Sur-refus** (over-refusal) :
Refus par un modèle d'un prompt qui est en réalité sûr, typiquement parce qu'il ressemble par sa formulation à un prompt dangereux ou touche un sujet à la tonalité sensible sans être nuisible. Un mode de défaillance réellement différent d'un jailbreak, et qu'une eval de red-teaming (limitée aux prompts dangereux) ne peut pas détecter.
_À éviter_ : faux refus (employé comme synonyme dans certaines sources ; cet espace de travail retient « sur-refus »)

**Red-teaming** :
Construction délibérée d'entrées conçues pour faire produire au modèle une sortie dangereuse, par un testeur humain ou par une méthode automatisée de génération d'attaques, puis mesure de la fréquence à laquelle ces entrées réussissent (un jailbreak) contre un modèle donné et ses défenses.
_À éviter_ : ne rapporter que le taux de réussite des attaques comme « l'eval de sécurité » ; il ne mesure rien du sur-refus, un mode de défaillance distinct qui demande son propre jeu de test

**Saturation** :
Benchmark qui atteint un plafond où les modèles y obtiennent des scores quasi parfaits tout en échouant encore sur le même type de tâche en usage réel, parce que le benchmark a cessé de mesurer la compétence sous-jacente pour mesurer la familiarité avec le benchmark lui-même.
_À éviter_ : contamination des données (une cause voisine mais distincte ; la saturation peut aussi résulter d'un réglage légitime et poussé sur un benchmark au fil du temps, pas seulement de questions du benchmark qui ont fui dans les données d'entraînement)

**Divulgation sélective** (selective disclosure) :
Test de plusieurs variantes de modèle privées et non publiées sur un benchmark ou une arène, en ne rapportant publiquement que la mieux notée. Transforme un classement en cible d'optimisation (loi de Goodhart) plutôt qu'en mesure neutre, et crée un écart entre le score que rapporte un classement et la version du modèle réellement publiée.
_À éviter_ : contamination des données (un autre vecteur de manipulation ; la divulgation sélective est une pratique de rapport, pas des données d'eval qui fuient dans l'entraînement)

**Latence de queue** (tail latency) :
Fraction des requêtes les plus lentes (couramment rapportée en p95 ou p99), par opposition à la moyenne. Une latence moyenne inchangée peut cacher une queue nettement pire, et à grande échelle, une requête qui se répartit sur de nombreux appels backend n'aboutit qu'une fois tous terminés, ce qui fait de la queue ce qui décide réellement du temps de réponse perçu.
_À éviter_ : latence moyenne (un agrégat qui peut rester stable pendant que la queue, qui domine l'expérience réelle de l'utilisateur, se dégrade nettement)

**Réussite de la tâche** (task success) :
Comparaison de l'état final réel d'une trajectoire d'agent avec un état cible annoté, en créditant toute séquence d'actions qui atteint le bon résultat plutôt que seulement une unique séquence de référence prédéterminée. Plus fidèle que la précision par étape, qui ne peut créditer que la seule trajectoire qu'on lui a donnée.
_À éviter_ : précision par étape (une mesure plus étroite et plus fragile : faire correspondre chaque action à une trajectoire de référence, ce qui pénalise à tort un chemin différent, tout aussi valable, vers le même bon résultat)

**Décalage entraînement-service** (training-serving skew) :
Tout écart entre la performance hors ligne d'un modèle (entraînement ou held-out) et sa performance en production. Les recommandations de Google distinguent plusieurs comparaisons aux causes différentes ; un écart sur l'entrée identique entre un score hors ligne et un résultat en production indique précisément une erreur d'ingénierie, ni une dérive ni un problème de modélisation.
_À éviter_ : dérive (le cas plus étroit, temporel, où le monde réel a changé depuis l'entraînement ; tout écart hors ligne/en ligne n'est pas une dérive)

**Trajectoire** (trajectory) :
Séquence complète d'appels d'outils, de décisions intermédiaires et de tours qu'un agent produit en travaillant une tâche, par opposition à la sortie unique que note une eval par réponse. Une métrique par réponse n'a ici rien à quoi se rattacher, ce qui explique que l'évaluation d'agents ait besoin de ses propres métriques.
_À éviter_ : réponse (trop étroit ; une trajectoire est tout le processus à plusieurs étapes, souvent à plusieurs tours, pas une sortie isolée en son sein)
