---
title: "19. Survivre à la panne d'un nœud"
description: "Mettre en pause, diagnostiquer, isoler ce qui est cassé et reprendre depuis le dernier checkpoint, quel qu'en soit le coût"
type: lesson
---

# Leçon 19. Survivre à la panne d'un nœud

**Lien avec la mission :** « Concevoir un schéma de checkpointing qui borne la progression perdue après la panne d'un nœud » est la case « Terminée quand » de cette étape dans « Le fil conducteur ». La leçon 18 a couvert ce qu'un checkpoint doit contenir et à quelle fréquence en sauvegarder un ; cette leçon couvre ce qui se passe réellement une fois qu'une panne survient.
**Source primaire :** [Article : "OPT: Open Pre-trained Transformer Language Models", Zhang et al., 2022](https://arxiv.org/abs/2205.01068)
**Prérequis :** [Leçon 18](0018-what-a-checkpoint-has-to-hold.md)

## Échauffement

1. ▢ Nommez les quatre éléments qu'un checkpoint doit contenir pour reprendre un run correctement, et non pas seulement approximativement.

<details markdown="1"><summary>Vérifier</summary>

Les paramètres du modèle, l'état de l'optimizer, le nombre de pas et la position dans le schéma de learning rate et, pour une reproductibilité exacte, la position du data loader et l'état du générateur de nombres aléatoires.

</details>

2. ▢ Sur environ deux mois d'entraînement d'OPT-175B, qu'ont rapporté Zhang et al. sur la fréquence des pannes matérielles ?

<details markdown="1"><summary>Vérifier</summary>

Au moins 35 redémarrages manuels et le remplacement cyclique de plus de 100 hôtes, plus une estimation de plus de 70 redémarrages automatiques supplémentaires, bien plus d'un redémarrage tous les deux jours soutenu sur le run.

</details>

## À savoir

### La procédure qu'OPT a réellement suivie

Zhang et al. décrivent une séquence précise et répétable plutôt qu'une course improvisée à chaque panne : quand un problème matériel était soupçonné, le run d'entraînement était **mis en pause** ; une série de **tests de diagnostic** était exécutée pour identifier quels nœuds précis se comportaient mal ; tout nœud signalé par les diagnostics était **isolé** (cordoned off), c'est-à-dire exclu du pool de nœuds que le run utiliserait par la suite ; et l'entraînement **reprenait depuis le dernier checkpoint sauvegardé**, sur les nœuds restants et sains. C'est le même schéma, que la panne ait été repérée manuellement ou ait déclenché un redémarrage automatique : diagnostiquer, exclure le matériel défaillant, reprendre depuis l'état sauvegardé le plus récent.

### Redémarrages manuels contre automatiques, et pourquoi la différence compte en exploitation

Zhang et al. distinguent plus de 35 redémarrages **manuels**, où une personne a reconnu un problème et est intervenue, d'une estimation de plus de 70 redémarrages **automatiques**, déduite de l'écart entre le nombre d'hôtes remplacés et le nombre plus petit de redémarrages manuels enregistrés. Un redémarrage automatique suppose un outillage qui détecte une panne et reprend l'entraînement sans attendre qu'une personne la remarque et agisse, ce qui compte directement pour la quantité de progression qu'une panne coûte réellement : une panne qui attend une détection manuelle perd tout le temps qui s'écoule avant qu'une personne n'intervienne, en plus de ce que coûte le cycle checkpoint-et-reprise lui-même, alors qu'une panne détectée et reprise automatiquement perd plutôt seulement l'équivalent de progression d'un intervalle de checkpoint dont parlait la leçon 18.

### La divergence de la loss, une défaillance voisine mais distincte dont il faut se remettre

Zhang et al. décrivent aussi des redémarrages pour une tout autre raison : la divergence de la loss, et non une panne matérielle. Quand la loss d'entraînement divergeait, baisser le learning rate et redémarrer depuis un checkpoint antérieur permettait au run de se rétablir et de continuer. Ils ont remarqué que cela était corrélé à deux autres signaux : leur loss scalar dynamique (une partie de la configuration en précision mixte) tombant à zéro, et la norme des activations de la dernière couche qui faisait un pic. Plutôt que de redémarrer juste avant la divergence, ils ont choisi des points de redémarrage où le loss scalar était encore en bon état et où les normes d'activation avaient tendance à baisser plutôt qu'à croître sans borne, et ont trouvé séparément que ramener le gradient clipping de 1,0 à 0,3 aidait. C'est une seconde raison, réellement différente, d'utiliser un checkpoint pour reprendre un run, distincte de la mort d'un nœud : le matériel va bien, mais le processus d'entraînement lui-même doit revenir en arrière et continuer différemment, ce que seul un historique conservé de checkpoints (et pas seulement le plus récent) rend possible.

## Pratique

1. ▢ Mettez ces quatre étapes de la procédure de panne de nœud d'OPT dans l'ordre que décrivent Zhang et al. : (a) reprendre l'entraînement sur les nœuds restants, (b) mettre le run d'entraînement en pause, (c) exécuter des tests de diagnostic pour identifier les mauvais nœuds, (d) isoler les nœuds signalés.

<details markdown="1"><summary>Vérifier</summary>

b, c, d, a : mettre en pause, diagnostiquer, isoler ce que les diagnostics ont signalé, puis reprendre depuis le dernier checkpoint sauvegardé sur les nœuds sains restants.

</details>

2. ▢ Pourquoi une panne détectée et reprise automatiquement coûte-t-elle en général moins de progression qu'une panne détectée manuellement, même si les deux finissent par reprendre depuis le même checkpoint ?

<details markdown="1"><summary>Vérifier</summary>

Un redémarrage manuel perd tout le temps qui s'écoule avant qu'une personne remarque le problème et intervienne, en plus du cycle checkpoint-et-reprise lui-même. Un redémarrage automatique saute ce délai de détection, si bien que le coût total se rapproche de la seule progression d'un intervalle de checkpoint.

</details>

3. ▢ La loss d'entraînement d'une équipe diverge, mais il n'y a aucune panne matérielle : tous les nœuds sont sains. D'après le récit de Zhang et al., un checkpoint est-il encore utile ici, et si oui, comment ?

    - a) Non ; les checkpoints n'aident que pour les pannes matérielles, pas pour la divergence de la loss
    - b) Oui ; redémarrer depuis un checkpoint antérieur, en baissant le learning rate, est exactement la manière dont Zhang et al. se sont remis d'une divergence de la loss
    - c) Oui, mais seul le checkpoint le plus récent peut jamais être utilisé, quel que soit le moment où la divergence a commencé
    - d) Non ; la divergence de la loss exige de réentraîner le modèle à partir de zéro

<details markdown="1"><summary>Indice</summary>

Zhang et al. ont choisi spécifiquement des points de redémarrage d'après l'état de leur loss scalar et des normes d'activation, et pas simplement le checkpoint disponible le plus récent.

</details>

<details markdown="1"><summary>Vérifier</summary>

**b)** est exactement ce que décrivent Zhang et al. (a) est faux ; le même mécanisme checkpoint-et-reprise permet de se remettre de l'une ou l'autre cause. (c) est faux précisément parce qu'ils ont choisi un point de redémarrage d'après le moment où le loss scalar était en bon état et où les normes d'activation baissaient, ce qui peut ne pas être le checkpoint le plus récent, et plaide pour garder à portée de main plus d'un checkpoint récent. (d) contredit le récit même de l'article sur la reprise sans redémarrage complet.

</details>

4. ▢ Pourquoi se remettre d'une divergence de la loss, comme le décrivent Zhang et al., plaide-t-il pour garder plus que le seul checkpoint le plus récent ?

<details markdown="1"><summary>Vérifier</summary>

Parce que le meilleur point de redémarrage n'était pas toujours le checkpoint le plus récent ; c'était un point choisi d'après la santé du loss scalar et la direction que prenaient les normes d'activation, qui pouvait être plus loin en arrière que la dernière sauvegarde. Ne garder que le checkpoint le plus récent supprimerait la possibilité de revenir à un point antérieur plus stable.

</details>

## Exercices en situation réelle

- [ ] Trouvez où un framework d'entraînement ou un outil d'orchestration auquel vous avez accès expose la détection et le redémarrage automatiques des pannes (health checks, drainage de nœuds ou termes similaires sont courants). Notez s'il correspond au schéma mise en pause, diagnostic, isolement, reprise que décrit cette leçon.
- [ ] Lisez le paragraphe « Loss Divergences » de l'article OPT (lié plus haut) et écrivez une phrase sur le signal, en dehors de la courbe de loss elle-même, que les auteurs ont utilisé pour juger si un point de redémarrage était sûr pour reprendre.
- [ ] Demain : pour la fréquence de checkpoint que vous avez choisie dans l'exercice en situation réelle de la leçon 18, décidez combien de checkpoints récents vous garderiez à portée de main plutôt que seulement le dernier, et écrivez une phrase sur la raison, compte tenu du cas de reprise après divergence de la loss de cette leçon.

## Pour aller plus loin

- [Article : "OPT: Open Pre-trained Transformer Language Models", Zhang et al., 2022](https://arxiv.org/abs/2205.01068)
- [Ressources](../RESOURCES.md)

---

L'étape 8 a couvert la survie à une panne au sein d'un seul run d'entraînement. L'étape 9 aborde une question de plus longue haleine : suivre la progression de ce run en premier lieu, et savoir s'il est sur la bonne voie.

Ça ne passe pas ? Relisez la source primaire en haut de page, car cette leçon la condense et c'est dans la condensation que la compréhension s'échappe. Consultez le [glossaire](../GLOSSARY.md) pour tout terme qui vous a paru glissant.

Si c'est la leçon elle-même qui n'est pas claire plutôt que la matière, c'est un défaut : [ouvrez une issue](https://github.com/TokenCemetery/teach/issues).
