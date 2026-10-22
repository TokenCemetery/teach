---
title: "Glossaire"
description: "Termes de référence pour l'inférence"
type: glossary
---

# Glossaire de l'inférence

Termes de référence pour servir un modèle entraîné : ce qu'un serveur garde en mémoire, et les leviers dont il dispose sur la latence et le débit.

## Termes

**Attention sink** (puits d'attention) :
Score d'attention démesurément élevé que reçoivent les tout premiers tokens d'une séquence, quel que soit leur contenu réel. C'est pourquoi les retirer d'un cache à fenêtre glissante provoque un effondrement de la qualité plutôt qu'une perte progressive du contexte ancien. Conserver en permanence dans le cache les entrées KV de ces seuls tokens initiaux, en plus de la fenêtre glissante habituelle, permet de retrouver l'essentiel des performances de l'attention complète (la technique StreamingLLM).
_À éviter_ : supposer que n'importe quel ancien token retiré cause le même dommage (seuls les tokens initiaux « sink » portent ce poids disproportionné ; perdre d'autres anciens tokens hors de la fenêtre dégrade la qualité progressivement au lieu de la faire s'effondrer)

**Cold start** (démarrage à froid, en serving) :
Délai entre le moment où un autoscaler décide d'ajouter une réplique et celui où cette réplique est réellement capable de traiter une requête. Il est dominé par le temps de chargement en mémoire du checkpoint d'un grand modèle, qui peut prendre des dizaines de secondes et dépasse de très loin le temps de génération d'un seul token.
_À éviter_ : le traiter comme un problème de file d'attente des requêtes (un ordonnanceur ou un routeur n'a aucun effet dessus ; il est entièrement fixé par la taille du checkpoint et par le chemin de stockage qu'il doit traverser)

**Décodage contraint (guidé)** :
Masquage de chaque token qui violerait une structure exigée (JSON valide, une grammaire) avant l'échantillonnage, de sorte que la structure de la sortie est garantie par construction plutôt que simplement encouragée. Rendu peu coûteux par token en reformulant la grammaire comme un automate à états finis et en précalculant, une seule fois, un index des tokens valides depuis chaque état.
_À éviter_ : vérifier la validité de la sortie une fois la génération terminée (cela ne garantit rien, puisque le modèle a toujours été libre d'échantillonner un token invalide ; c'est le masquage avant l'échantillonnage qui rend la garantie structurelle)

**Coût par million de tokens** :
Coût horaire de location d'un GPU divisé par son débit mesuré (tokens/s, converti en tokens/heure), ramené à un million de tokens. Il est dérivé du même débit mesuré que produit le compromis sur la taille de batch de la leçon 6, et non repris du prix par token annoncé par un fournisseur, mesuré avec la taille de batch d'une autre charge de travail.
_À éviter_ : un prix par token fixe, cité par un fournisseur (le débit, et donc le coût par token, dépend de la taille de batch et de la charge de travail sous lesquelles il a été mesuré, et ne se transpose pas d'une configuration à l'autre)

**Draft model** (modèle de brouillon) :
Petit modèle peu coûteux (ou mécanisme qui n'est pas un modèle, comme la correspondance de n-grammes, ou des têtes supplémentaires sur le modèle cible lui-même) qui propose plusieurs tokens suivants candidats que le modèle cible vérifie en une seule passe parallèle, au lieu de les générer lui-même un par un.
_À éviter_ : une alternative plus petite et de moindre qualité au modèle cible (la sortie d'un draft model n'est jamais utilisée directement ; elle est toujours vérifiée, et éventuellement corrigée, par le modèle cible)

**Budget d'erreur** (error budget) :
1 moins un objectif de niveau de service : la quantité d'écarts tolérés par rapport à cette cible avant qu'un service soit considéré comme non conforme. Une seule requête manquée n'est pas un problème en soi ; ce qui compte, c'est de savoir si le taux d'écarts consomme le budget plus vite que la fenêtre de mesure du SLO ne le permet.
_À éviter_ : traiter chaque mesure manquée isolée comme un problème (le budget existe précisément parce qu'un certain taux d'écarts est attendu et toléré ; seul compte le rythme de consommation sur la fenêtre)

**KV cache** :
Vecteurs de clés et de valeurs stockés pour chaque token déjà généré, à chaque couche, conservés pour qu'un serveur n'ait jamais à les recalculer pour les tokens suivants. Sa taille croît linéairement avec la longueur de la séquence et il est souvent le goulot d'étranglement mémoire du serving, plus que les poids du modèle eux-mêmes.
_À éviter_ : cache d'attention, magasin clé-valeur

**Routage sensible au KV cache** (KV-cache aware routing) :
Politique de routage des requêtes à l'échelle d'une flotte, qui envoie une nouvelle requête vers le serveur qui détient déjà le taux de réussite de cache le plus élevé pour elle, plutôt que de router uniquement selon la charge (round-robin, moins de connexions). Elle étend à une flotte de plusieurs serveurs le bénéfice du prefix caching sur un seul serveur, en rendant la décision de routage elle-même consciente de l'endroit où se trouve déjà un cache correspondant.
_À éviter_ : l'équilibrage de charge ordinaire (le round-robin ou le moins de connexions ignorent entièrement la localité du cache, et peuvent envoyer une requête favorable au cache vers un serveur qui doit refaire le prefill depuis zéro)

**Limité par la bande passante mémoire** (memory-bandwidth-bound) :
Calcul dont le coût dominant est le déplacement de données (comme les poids d'un modèle) de la mémoire vers l'unité de calcul, plutôt que l'arithmétique effectuée une fois ces données arrivées. Le décodage autorégressif ordinaire est limité par la bande passante mémoire, ce qui permet précisément au décodage spéculatif de vérifier plusieurs tokens candidats en une passe pour à peu près le coût d'en générer un seul.
_À éviter_ : limité par le calcul (le régime opposé, où l'arithmétique domine ; confondre les deux fait manquer pourquoi le travail de vérification supplémentaire est presque gratuit pendant le décodage en particulier)

**Bulle de pipeline** (pipeline bubble) :
Temps d'inactivité que les appareils d'une configuration à parallélisme de pipeline passent à attendre, au début (pendant que le pipeline se remplit) et à la fin (pendant qu'il se vide) du traitement d'un batch, puisque tous les appareils n'ont pas de travail à ces moments. Découper un batch en davantage de micro-batchs réduit cette fraction d'inactivité sans jamais l'éliminer.
_À éviter_ : supposer que le micro-batching supprime entièrement la bulle (il ne fait que réduire la fraction d'inactivité par rapport au travail total ; un délai de démarrage et de vidange subsiste quel que soit le nombre de micro-batchs)

**Parallélisme de pipeline** (pipeline parallelism) :
Partition de la suite de couches d'un modèle en groupes consécutifs placés sur des appareils distincts, de sorte que les données traversent les appareils dans le même ordre que celui dans lequel les couches s'exécuteraient sur un seul. La communication n'a lieu qu'à la frontière entre le groupe d'un appareil et le suivant, ce qui lui permet de tolérer une liaison entre appareils plus lente que celle qu'exige le parallélisme tensoriel, et de s'étendre sur plusieurs nœuds.
_À éviter_ : découper le calcul à l'intérieur d'une seule couche (c'est le parallélisme tensoriel ; le parallélisme de pipeline ne divise jamais ce qui se passe à l'intérieur d'une couche, seulement quelles couches vont où)

**Prefix caching** (mise en cache de préfixe) :
Réutilisation du KV cache déjà calculé d'un préfixe partagé entre des requêtes par ailleurs sans lien (un system prompt commun, un document interrogé à répétition, les tours précédents d'une conversation). C'est le même mécanisme de partage de blocs que PagedAttention utilise au sein des échantillons parallèles d'une seule requête, étendu à plusieurs requêtes. Il accélère le prefill uniquement ; le temps de decode n'est pas modifié.
_À éviter_ : supposer qu'il accélère aussi le decode (il évite seulement le calcul de prefill redondant pour un préfixe qui correspond ; générer de nouveaux tokens ensuite coûte exactement la même chose dans les deux cas)

**RoPE scaling** :
Extension de la longueur de contexte qu'un modèle peut traiter au-delà de sa longueur d'entraînement, en redimensionnant la façon dont les embeddings de position rotatifs encodent la distance entre les tokens (l'approche de YaRN : mettre moins à l'échelle les dimensions à haute fréquence et davantage les dimensions à basse fréquence), plutôt qu'en réentraînant depuis zéro. Cela ne change rien au nombre de clés et de valeurs de tokens mis en cache ; un contexte plus long traité ainsi coûte toujours en entier la croissance linéaire ordinaire du KV cache.
_À éviter_ : supposer qu'il réduit ou plafonne la mémoire du KV cache (il ne fait qu'étendre la longueur de contexte maximale utilisable ; le cache pour ce contexte plus long croît exactement comme il le ferait sans aucune mise à l'échelle)

**SLI (service level indicator, indicateur de niveau de service)** :
Ratio quantitatif, pertinent pour l'utilisateur, choisi parmi une métrique brute exportée, par exemple la fraction de requêtes dont le TTFT est inférieur à un seuil donné, formulé du point de vue de l'expérience de l'utilisateur plutôt que de l'état interne du serveur.
_À éviter_ : l'histogramme brut d'une métrique lui-même (un histogramme est une donnée mesurée ; un SLI est le ratio précis, pertinent pour l'utilisateur, choisi dedans pour y rattacher une cible)

**Attention à fenêtre glissante** (sliding-window attention) :
Restriction de chaque token à un maximum de `W` tokens précédents, au lieu de toute la séquence jusque-là, associée à un cache à tampon circulaire qui ne contient jamais que les clés et les valeurs de `W` tokens. Elle plafonne le KV cache d'une séquence à une taille constante, quelle que soit la longueur que la séquence atteint réellement, contrairement à la croissance linéaire inchangée du RoPE scaling.
_À éviter_ : supposer qu'elle étend la distance utile que voit un modèle comme le fait le RoPE scaling (elle plafonne le cache et borne l'attention directe aux `W` derniers tokens ; ce qui se trouve au-delà n'est atteint qu'indirectement, par l'empilement des couches, et subit seul un effondrement de la qualité sans attention sinks)

**SLO (service level objective, objectif de niveau de service)** :
Cible énoncée pour un SLI, par exemple « 99 % des requêtes ont un TTFT inférieur à 300 ms sur 28 jours glissants ». Ce qui reste, 1 moins le SLO, est le budget d'erreur.
_À éviter_ : un résultat de benchmark ponctuel (le p99 mesuré une seule fois dans la leçon 16 est un instantané ; un SLO est une cible permanente tenue face à des métriques exportées en continu)

**Décodage spéculatif** (speculative decoding) :
Rédaction à bas coût de plusieurs tokens suivants candidats, puis vérification de tous en une seule passe avant parallèle dans le modèle cible : les bonnes suppositions sont acceptées et les mauvaises rééchantillonnées, de sorte que la distribution de sortie finale correspond exactement à celle obtenue en exécutant seul le modèle cible. Un pur levier de latence, sans compromis sur la qualité.
_À éviter_ : une technique d'approximation (elle ne change que le nombre de passes avant coûteuses que prend la génération, jamais ce qui est généré)

**Parallélisme tensoriel** (tensor parallelism) :
Répartition entre des appareils des grosses multiplications matricielles à l'intérieur d'une seule couche (les blocs d'attention et de MLP d'un transformer), par colonnes ou par lignes : chaque appareil calcule sa propre tranche en parallèle, et une étape de communication recombine le vrai résultat à des points précis à l'intérieur de chaque couche. Elle exige une interconnexion rapide (comme NVLink), puisque cette recombinaison a lieu sur le chemin critique, à chaque couche, à chaque passe avant.
_À éviter_ : répartir des couches entières entre des appareils (c'est le parallélisme de pipeline ; le parallélisme tensoriel découpe le calcul à l'intérieur d'une couche, sans jamais attribuer des couches entières à des appareils différents)
