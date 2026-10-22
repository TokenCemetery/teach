---
title: "26. Coût, latence et débit"
description: "Prefill contre decode, et où va réellement l'argent"
type: lesson
---

# Leçon 26. Coût, latence et débit

**Lien avec la mission :** « Mesurer ce que cela a coûté en qualité et en latence » figure sur la liste de la réussite. Le fine-tuning est fréquemment une décision de *coût*, et voici l'arithmétique qui est derrière.
**Source primaire :** [Blog : "LLM Inference Performance Engineering: Best Practices", Databricks](https://www.databricks.com/blog/llm-inference-performance-engineering-best-practices)
**Prérequis :** [Leçon 25](0025-serving-adapters.md)

## Échauffement

1. ▢ Quel est l'argument opérationnel en faveur du service non fusionné ?

<details markdown="1"><summary>Vérifier</summary>

Le retour arrière est un changement de routage plutôt qu'un déploiement, et le base model intact reste disponible comme solution de repli et point de comparaison.

</details>

2. ▢ Pourquoi faut-il évaluer l'artefact que vous livrez ?

<details markdown="1"><summary>Vérifier</summary>

La quantification au moment du service porte un coût permanent en qualité par requête. Les chiffres d'un modèle en bf16 ne décrivent pas un déploiement en 4 bits.

</details>

3. ▢ Qu'est-ce que le fine-tuning enseigne mal ?

<details markdown="1"><summary>Vérifier</summary>

De nouveaux faits, une capacité de raisonnement absente, des informations à jour, le calcul précis.

</details>

## À savoir

### La forme en deux phases de l'inférence

La génération a deux phases aux caractéristiques de performance complètement différentes, et les confondre rend incohérente toute discussion sur l'optimisation.

**Le prefill** traite l'ensemble du prompt d'entrée d'un coup. Tous les tokens sont disponibles, donc le travail est une grosse multiplication de matrices parallèle, ce qui le rend **limité par le calcul.** Le coût évolue avec la longueur du prompt.

**Le decode** génère un token à la fois, chacun dépendant du précédent. Chaque pas lit tous les poids du modèle pour produire un seul token, donc l'arithmétique par octet déplacé est minuscule, ce qui le rend **limité par la bande passante mémoire.** Le coût évolue avec la longueur de la sortie.

![Huit tokens de prompt alimentant tous une seule passe sur la ligne du prefill, contre quatre passes distinctes enchaînées sur la ligne du decode, une par token de sortie.](images/one-pass-or-one-each.svg)

Une boîte sur la ligne du haut contre quatre sur celle du bas, c'est toute l'asymétrie. Allonger le prompt élargit la passe unique ; allonger la sortie ajoute des boîtes à la chaîne.

Conséquences :

- **Les longs prompts sont bon marché par token ; les longues sorties sont chères par token.** Ce n'est pas symétrique, et l'asymétrie est grande.
- La vitesse du decode est fixée par la bande passante mémoire, donc un modèle plus petit est plus rapide presque en proportion de sa taille.
- Le batching aide énormément le decode, parce que les poids sont lus une fois pour tout le batch, et aide beaucoup moins le prefill.

### Les métriques qui comptent

| Métrique | Signification | Fixée par |
|---|---|---|
| Time to first token | Latence du prefill | Longueur du prompt, calcul |
| Inter-token latency | Temps par token de sortie | Bande passante mémoire, taille du modèle |
| Latence totale | De bout en bout | Les deux, plus l'attente en file |
| Débit | Tokens/seconde sur toutes les requêtes | Efficacité du batching |
| Coût par requête | Argent | Débit et coût du matériel |

La latence et le débit s'arbitrent via la batch size. Des batchs plus grands augmentent le débit et augmentent la latence par requête. Il n'y a pas de meilleur réglage unique : cela dépend de si un humain attend.

### Où le fine-tuning change l'économie

C'est la partie que les gens ratent. Le bénéfice en coût du fine-tuning n'a généralement rien à voir avec des poids qui seraient meilleurs.

**Des prompts plus courts.** Un modèle fine-tuné n'a besoin ni d'exemples few-shot, ni de longues instructions de format, ni d'un system prompt élaboré, parce que ce comportement est dans les poids. Si votre prompt passe de 2,000 tokens à 200, vous avez retiré 1,800 tokens de prefill de chaque requête, pour toujours. Sur un endpoint à fort volume, c'est souvent tout l'argumentaire économique.

**Des sorties plus courtes.** Un modèle entraîné à répondre dans le format requis cesse de meubler avec du préambule et des précautions oratoires. Comme le decode est la phase coûteuse, réduire la longueur de la sortie vaut plus par token que réduire celle de l'entrée.

**Un plus petit modèle devenant suffisant.** La version la plus forte de l'argument : un petit modèle fine-tuné qui égale un grand modèle généraliste sur votre tâche étroite est considérablement moins cher par requête et de latence plus basse, parce que le decode est limité par la bande passante et que la bande passante évolue avec la taille. Troquer un grand modèle généraliste contre un petit modèle spécialisé, c'est là que vivent les économies d'un ordre de grandeur.

**Moins de nouvelles tentatives.** Si le modèle généraliste produit une sortie invalide dans 15 % des cas et que vous réessayez, votre vrai coût est de 1.15× le coût visible. Un fine-tuning qui atteint 99 % de validité en supprime presque tout.

### La comptabilité honnête

Face à ces économies, comptez les coûts :

| Coût | Nature |
|---|---|
| Calcul d'entraînement | Ponctuel par version, généralement faible pour les adapters |
| Création des données | Souvent le coût dominant, et généralement du temps humain |
| Infrastructure d'évaluation | Ponctuelle, puis maintenance continue |
| Complexité du service | Continue : pile compatible avec les adapters, versionnage, routage |
| Ré-entraînement | Continu : modèles, données et exigences bougent tous |
| Expertise | Continue : quelqu'un doit en être responsable |

**Les coûts récurrents sont ce qui tranche, et ce sont ceux qu'on laisse hors de l'estimation initiale.** Un fine-tuning qui économise un peu d'argent par requête et exige une personne pour le maintenir est un mauvais échange à faible volume et un bon à fort volume. Le point de croisement est de l'arithmétique, donc faites l'arithmétique.

### Une comparaison calculée

Supposons un grand modèle généraliste avec un prompt de 2,000 tokens face à un petit modèle fine-tuné avec un prompt de 200 tokens, produisant tous deux 150 tokens de sortie.

```text
General:  2000 prefill + 150 decode, on a large model
Tuned:     200 prefill + 150 decode, on a small model
```

L'économie sur le prompt est de 1,800 tokens de prefill. L'économie liée à la taille du modèle s'applique aux deux phases et surtout au coût de bande passante du decode. Multipliez par le volume de requêtes, comparez aux coûts fixes et récurrents ci-dessus, et vous avez une vraie réponse plutôt qu'une intuition.

À mille requêtes par jour, cela peut ne pas rembourser le travail sur les données. À un million, c'est très probable. **Le volume est la variable décisive, et c'est celle qu'on énonce le moins souvent.**

### Mesurez, ne modélisez pas

Tout ce qui précède a la bonne forme et la mauvaise précision. Les chiffres réels dépendent du matériel, de la pile de service, de la batch size, des longueurs de séquence et du profil de trafic d'une manière qu'aucune formule ne capture. Mesurez :

- Time to first token et inter-token latency, à vos vraies longueurs de prompt
- Le débit à plusieurs batch sizes, pour trouver votre point latence/débit
- Le coût par millier de requêtes, avec votre vrai profil de trafic
- Les trois mêmes pour l'alternative à laquelle vous comparez

Et mesurez sous une charge réaliste. Un benchmark d'une requête à la fois ne dit rien d'un endpoint de production en batch, parce que le batching est le facteur dominant du débit.

## Pratique

1. ▢ Quelle phase est limitée par le calcul, laquelle par la bande passante, et qu'en découle-t-il ?

<details markdown="1"><summary>Vérifier</summary>

Le prefill est limité par le calcul, parce que tout le prompt est traité en parallèle. Le decode est limité par la bande passante mémoire, parce que chaque pas lit tous les poids pour produire un token.

Il en découle que les longs prompts sont relativement bon marché par token, que les longues sorties sont chères, que le batching aide bien plus le decode que le prefill, et que des modèles plus petits accélèrent le decode presque en proportion de la taille.

</details>

2. ▢ Votre fine-tuning réduit la longueur du prompt de 1,800 tokens à 150 et laisse la longueur de sortie inchangée. D'où vient l'économie ?

<details markdown="1"><summary>Vérifier</summary>

Du prefill : 1,650 tokens de moins de travail limité par le calcul à chaque requête. Le comportement qui était spécifié par des exemples few-shot et des instructions de format vit maintenant dans les poids.

C'est fréquemment tout l'argumentaire économique du fine-tuning, et cela n'a rien à voir avec le fait que le modèle soit plus intelligent.

</details>

3. ▢ Quel bénéfice du fine-tuning produit la plus grande réduction de coût ?

    - a) Le prompt devenant plus court de mille tokens
    - b) Un plus petit modèle devenant suffisant pour la tâche
    - c) La sortie devenant plus courte de cinquante tokens de sortie
    - d) Le taux de nouvelles tentatives passant de quinze pour cent à un

<details markdown="1"><summary>Vérifier</summary>

**b)** Un plus petit modèle devenant suffisant pour la tâche.

Il réduit les deux phases à la fois, et le decode, la phase coûteuse, évolue avec la taille du modèle parce qu'il est limité par la bande passante. Les autres sont réels et cumulables, mais un changement de taille de modèle est multiplicatif sur tout.

</details>

4. ▢ Quels coûts sont le plus souvent omis de l'estimation initiale ?

<details markdown="1"><summary>Vérifier</summary>

Les coûts récurrents : le ré-entraînement à mesure que les modèles et les exigences bougent, la complexité du service, la maintenance de l'évaluation, et l'expertise d'une personne qui en est responsable.

Le calcul d'entraînement est faible pour les adapters et c'est lui qu'on cite. Le coût humain continu est élevé et on l'oublie, et c'est généralement lui qui tranche la question.

</details>

5. ▢ Vous mesurez la latence d'une seule requête et concluez que votre endpoint est assez rapide. Qu'est-ce qui ne va pas ?

<details markdown="1"><summary>Vérifier</summary>

La production sert des requêtes concurrentes en batchs. La batch size domine à la fois le débit et la latence par requête, et une mesure à une seule requête n'observe ni l'un ni l'autre.

Mesurez sous une concurrence réaliste, à plusieurs batch sizes, et choisissez délibérément votre point sur la courbe latence/débit.

</details>

6. ▢ Même tâche, même économie par requête, 500 requêtes par jour contre 5 millions. Même décision ?

<details markdown="1"><summary>Vérifier</summary>

Non. Les coûts fixes et récurrents de création des données, d'évaluation, de complexité du service et de maintenance sont essentiellement indépendants du volume, alors que les économies évoluent avec lui.

À 500 par jour, le coût humain récurrent domine presque certainement. À 5 millions, il est négligeable face aux économies. Le volume est la variable décisive et sa place est dans la première phrase de la proposition.

</details>

## Exercices en situation réelle

- [ ] Mesurez time to first token et inter-token latency pour votre modèle à vos vraies longueurs de prompt.
- [ ] Mesurez le débit aux batch sizes 1, 4, 16 et 64. Tracez l'arbitrage latence/débit et choisissez votre point.
- [ ] Calculez le coût par millier de requêtes pour votre chemin fine-tuné et pour l'alternative. Incluez les coûts récurrents.
- [ ] Demain : trouvez le volume de requêtes auquel votre fine-tuning atteint le point d'équilibre. Comparez-le à votre volume réel.

## Pour aller plus loin

- [Blog : "LLM Inference Performance Engineering: Best Practices", Databricks](https://www.databricks.com/blog/llm-inference-performance-engineering-best-practices)
- [Doc : Optimization and tuning, vLLM](https://docs.vllm.ai/en/latest/configuration/optimization.html)
- [Leçon 27. Quand ne pas faire de fine-tuning](0027-when-not-to-fine-tune.md)

---

Ça ne passe pas ? Relisez la source primaire en haut de page, car cette leçon la condense et c'est dans la condensation que la compréhension s'échappe. Consultez le [glossaire](../GLOSSARY.md) pour tout terme qui vous a paru glissant.

Si c'est la leçon elle-même qui n'est pas claire plutôt que la matière, c'est un défaut : [ouvrez une issue](https://github.com/TokenCemetery/teach/issues).
