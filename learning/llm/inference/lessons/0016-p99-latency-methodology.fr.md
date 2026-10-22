---
title: "16. Méthodologie de mesure de la latence p99"
description: "Pourquoi le p99 vaut mieux qu'une moyenne, pourquoi le TTFT et la latence inter-token exigent des chiffres séparés, et ce qui rend une mesure du p99 digne de confiance"
type: lesson
---

# Leçon 16. Méthodologie de mesure de la latence p99

**Lien avec la mission :** La mission de cet espace de travail est de défendre un budget de latence p99, et un chiffre défendu doit venir d'une mesure bien faite ; cette leçon dit ce que « bien faite » veut dire avant que la leçon 17 ne rattache ce chiffre à chaque choix antérieur.
**Source primaire :** [Doc : vLLM Documentation, vLLM Project](https://docs.vllm.ai/en/latest/)
**Prérequis :** [Leçon 15](0015-what-changes-off-gpu.md), [KV cache](../GLOSSARY.md)

## Échauffement

1. ▢ Pourquoi le prefill réclame-t-il l'essentiel de l'empreinte de cache finale d'une requête en une seule étape, alors que le decode ajoute le reste progressivement ?

<details markdown="1"><summary>Vérifier</summary>

Le prefill traite tout le prompt en une seule passe avant, en calculant et en mettant en cache ensemble les clés et les valeurs de chaque token du prompt. Le decode génère un token de sortie par étape, si bien que le cache ne croît que de la taille d'un token par étape.

</details>

2. ▢ Dans le continuous batching, qu'est-ce qui fait qu'une grosse requête admise bloque toutes les autres séquences qui partagent son étape de batch ?

<details markdown="1"><summary>Vérifier</summary>

Une étape de batch est atomique : toutes les séquences qui la partagent avancent ensemble, donc un gros prefill intégré à une étape retarde le token suivant de toutes les autres séquences jusqu'à ce que cette étape se termine. C'est le head-of-line blocking.

</details>

## À savoir

### Pourquoi le p99, et pas la moyenne

Le **p99** d'une distribution de latence est la valeur en dessous de laquelle se situent 99 % des requêtes mesurées ; seul le pire 1 % est plus lent. Une moyenne peut avoir l'air correcte tout en cachant un vrai problème : le head-of-line blocking de la leçon 5, par exemple, ne frappe que la petite fraction de requêtes assez malchanceuses pour partager une étape avec un gros prefill, si bien qu'il déplace à peine une moyenne portant sur des milliers de requêtes par ailleurs rapides, alors qu'il peut rendre ce 1 % malchanceux considérablement plus lent. Un budget de latence défendu par une moyenne manquerait exactement le mode de défaillance que cet espace de travail a passé l'étape 2 à expliquer.

![Un histogramme de la latence des requêtes. La plupart des requêtes se regroupent à basse latence, formant à gauche un grand massif qui s'amenuise vite. Un amas distinct et clairsemé de requêtes se situe loin à droite, à bien plus haute latence : la queue lente. Une ligne en pointillés qui marque la moyenne se trouve à l'intérieur du massif de gauche, à peine déplacée par les rares requêtes de l'extrême droite, trop peu nombreuses pour la faire bouger. Un repère pour le p99 se situe au contraire dans cette queue de l'extrême droite, puisque le p99 est défini par le pire pour cent, qui est précisément là où se trouvent les requêtes rares et lentes.](images/p99-vs-average-latency.svg)

### Quelle latence, mesurée séparément

La « latence d'une requête » n'est pas un seul chiffre pour un serveur de LLM ; elle se divise au minimum en **temps jusqu'au premier token (TTFT)**, dominé par le prefill, et **latence inter-token (ITL)**, parfois appelée temps par token de sortie, dominée par le decode. Ils se comportent différemment (leçon 3) et sont façonnés par des leviers différents (batching et ordonnancement pour le TTFT, taille de batch et quantification pour l'ITL), donc les fondre en un seul chiffre mélangé masque quel levier un mauvais p99 désigne réellement. Un budget qui mérite d'être défendu nomme le p99 du TTFT et le p99 de l'ITL (ou le p99 de la latence totale de bout en bout, quand c'est réellement ce dont la charge de travail se soucie) comme des chiffres séparés, et non une moyenne de deux choses différentes.

### Ce qui rend une mesure du p99 digne de confiance

Un p99 est l'estimation d'un événement rare, par définition seulement le pire 1 % d'un échantillon, il faut donc assez d'échantillons pour qu'il signifie quelque chose : un p99 calculé à partir de 20 requêtes rapporte en réalité sur une seule requête (le pire 1er centile sur 20 est proche du maximum, pas une estimation stable de la queue), alors qu'une estimation stable demande généralement des échantillons de l'ordre de centaines à milliers. La charge qui génère ces échantillons doit aussi ressembler à la vraie charge de travail : une concurrence réaliste (pas si basse que le comportement du batching et de l'ordonnancement n'est jamais réellement sollicité) et un mélange réaliste de longueurs de prompt et de sortie (le gaspillage du batching statique de la leçon 4 et le head-of-line blocking de la leçon 5 dépendent tous deux d'une variance de longueur de requête qu'un benchmark à requêtes de longueur uniforme ne ferait jamais apparaître). Un p99 mesuré sous une charge irréaliste est un vrai chiffre sur une charge de travail qui n'est pas celle qui est servie.

## Pratique

1. ▢ La latence moyenne des requêtes d'un serveur a l'air correcte, mais des utilisateurs signalent de temps en temps des requêtes bien plus longues que prévu. Que suggère ce schéma sur l'endroit où le problème apparaîtrait dans la distribution de latence, et pourquoi la moyenne pourrait-elle ne pas l'avoir détecté ?

<details markdown="1"><summary>Vérifier</summary>

Il suggère un problème de queue, quelque chose comme le head-of-line blocking de la leçon 5, qui n'affecte qu'une petite fraction des requêtes. Une moyenne sur de nombreuses requêtes pour la plupart épargnées bouge à peine même quand cette petite fraction devient considérablement plus lente, ce qui est exactement la raison pour laquelle il faut un p99 (ou un centile élevé similaire) pour la voir.

</details>

2. ▢ Pourquoi le TTFT et la latence inter-token devraient-ils être mesurés et rapportés comme des p99 séparés, plutôt que fondus en un seul chiffre de « latence moyenne des requêtes » ?

<details markdown="1"><summary>Vérifier</summary>

Le TTFT est dominé par le prefill et façonné par l'ordonnancement et le découpage ; la latence inter-token est dominée par le decode et façonnée par la taille de batch et la quantification. Un seul chiffre mélangé ne peut pas dire lequel de ces leviers un mauvais résultat désigne réellement, et améliorer l'un peut déplacer une moyenne mélangée sans révéler si l'autre s'est dégradé.

</details>

3. ▢ Une équipe calcule un chiffre de latence p99 à partir de 20 requêtes mesurées. Ce chiffre est-il digne de confiance ? Pourquoi ou pourquoi pas ?

<details markdown="1"><summary>Indice</summary>

Pensez à combien de ces 20 requêtes le 99e centile décrit réellement.

</details>

<details markdown="1"><summary>Vérifier</summary>

Non, pas de façon fiable. Avec seulement 20 échantillons, le 99e centile rapporte quasiment sur la seule requête la plus lente de l'échantillon, et non sur une estimation stable d'une vraie queue. Un p99 digne de confiance demande un échantillon bien plus grand, généralement de centaines à milliers de requêtes, pour moyenner le bruit lié aux requêtes particulières qui se sont trouvées dans ce 1 % supérieur.

</details>

4. ▢ Un benchmark mesure la latence p99 avec des requêtes qui ont toutes la même longueur uniforme de prompt et de sortie. Pourquoi cela pourrait-il sous-estimer le p99 que verrait réellement une charge de production à longueurs de requêtes variées ?

<details markdown="1"><summary>Vérifier</summary>

Les leçons 4 et 5 ont toutes deux montré que la variance de longueur des requêtes est ce qui crée les modes de défaillance qui nuisent à la latence de queue : le gaspillage du batching statique croît avec l'écart entre les longueurs des requêtes, et le head-of-line blocking est déclenché par l'arrivée d'un prefill exceptionnellement gros parmi de plus petits. Un benchmark à longueur uniforme ne produit jamais cette variance, donc il n'exerce jamais les conditions dont la latence de queue de la vraie charge de travail provient réellement.

</details>

5. ▢ Laquelle de ces affirmations est vraie à propos d'une mesure défendable de la latence p99 ?

    - a) Une seule exécution de benchmark de n'importe quelle taille suffit, tant qu'elle rapporte un chiffre p99
    - b) Elle devrait être mesurée avec une concurrence et une variance de longueur de requêtes réalistes, et rapportée séparément pour le TTFT et la latence inter-token
    - c) La moyenne et le p99 évoluent toujours ensemble, donc en mesurer un suffit
    - d) Le p99 n'a d'importance que pour le serving CPU/edge, pas pour le serving GPU

<details markdown="1"><summary>Vérifier</summary>

**b)** Le réalisme de la charge et la séparation du TTFT et de la latence inter-token sont tous deux nécessaires pour que le chiffre désigne quelque chose d'exploitable. (a) est fausse : trop peu d'échantillons rendent un p99 instable, comme l'a montré la question 3. (c) est fausse : une moyenne peut cacher exactement le comportement de queue qu'un p99 existe pour détecter. (d) est fausse : la latence de queue et sa mesure comptent pour n'importe quelle pile de serving, GPU ou CPU.

</details>

## Exercices en situation réelle

- [ ] Trouvez l'outil de benchmark de votre pile de serving (vLLM fournit `benchmark_serving.py`) et lisez quels centiles il rapporte par défaut et quelle distribution de longueurs de requêtes il utilise.
- [ ] Pour une charge de travail que vous avez en tête, écrivez à quoi ressemblerait une distribution réaliste de longueurs de prompt et de sortie, et si un benchmark à longueurs uniformes manquerait quelque chose à son sujet.
- [ ] Demain : si vous avez un serveur en fonctionnement, exécutez un benchmark contre lui avec au moins quelques centaines de requêtes et notez séparément le p99 du TTFT et le p99 de la latence inter-token rapportés.

## Pour aller plus loin

- [Doc : vLLM Documentation, vLLM Project](https://docs.vllm.ai/en/latest/)
- [Billet : "How continuous batching enables 23x throughput in LLM inference while reducing p50 latency", Anyscale](https://www.anyscale.com/blog/continuous-batching-llm-inference)
- [Ressources](../RESOURCES.md)

---

Ça ne passe pas ? Relisez la source primaire en haut de page, car cette leçon la condense et c'est dans la condensation que la compréhension s'échappe. Consultez le [glossaire](../GLOSSARY.md) pour tout terme qui vous a paru glissant.

Si c'est la leçon elle-même qui n'est pas claire plutôt que la matière, c'est un défaut : [ouvrez une issue](https://github.com/TokenCemetery/teach/issues).
