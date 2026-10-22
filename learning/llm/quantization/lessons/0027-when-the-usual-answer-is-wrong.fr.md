---
title: "27. Quand la réponse habituelle est fausse"
description: "Reconnaître quand des poids en 4 bits ou une recette standard est le mauvais choix, et trancher le différend à partir de la source primaire"
type: lesson
---

# Leçon 27. Quand la réponse habituelle est fausse

**Lien avec la mission :** Le parcours se termine par la confiance qu'on vous accorde pour trancher sur une quantification et l'expliquer à quelqu'un d'autre. « Utilisez des poids en 4 bits » et « AWQ bat GPTQ » sont les réponses habituelles, et chacune est vraie pour certains modèles, tâches et matériels et fausse pour d'autres. Cette leçon est la méthode pour savoir lesquels, et les cas où la réponse habituelle échoue.
**Source primaire :** [Article : "Scaling Laws for Precision", Kumar et al., 2024](https://arxiv.org/abs/2411.04330), sections 1 à 3
**Prérequis :** [Leçon 25](0025-choosing-a-scheme.md), [Leçon 26](0026-reviewing-a-quantization-claim.md), [Quantification post-entraînement](../GLOSSARY.md), [Limité par le calcul](../GLOSSARY.md), [Quantification weight-only](../GLOSSARY.md)

## Échauffement

1. ▢ Pourquoi une activation massive ou une feature outlier isolée ruine-t-elle un scale par tenseur, et quelle parade réduit le groupe au lieu de garder les outliers en haute précision ?

<details markdown="1"><summary>Vérifier</summary>

Le scale est fixé par la plus grande valeur, donc une seule valeur énorme laisse presque toutes les autres sur quelques niveaux proches de zéro. Les scales par groupe réduisent le groupe, de sorte que l'outlier ne gaspille que les niveaux de son propre groupe (leçons 7, 8 et 6).

</details>

2. ▢ Qu'apporte un calibration set à GPTQ et à AWQ, et comment un jeu inadapté se manifeste-t-il ?

<details markdown="1"><summary>Vérifier</summary>

Des statistiques d'activation issues d'entrées représentatives : GPTQ les utilise pour la compensation d'erreur du second ordre, AWQ pour trouver quels canaux de poids rencontrent de grandes activations. Un jeu inadapté se manifeste par un modèle qui obtient de bons scores sur du texte semblable aux données de calibration et de moins bons sur le trafic auquel il ne ressemblait pas (leçons 10, 11 et 12).

</details>

3. ▢ Qu'est-ce qu'un flip, et pourquoi peut-il être grand quand l'accuracy est inchangée ?

<details markdown="1"><summary>Vérifier</summary>

Une réponse qui est passée de correcte à incorrecte ou l'inverse entre la référence et le modèle quantifié. Les gains et les pertes s'annulent dans la moyenne, donc l'accuracy peut être égale tandis que de nombreuses réponses individuelles bougent (leçons 21 et 26).

</details>

## À savoir

### La méthode

Une réponse habituelle arrive comme un slogan sans ses conditions. Quatre étapes décident si elle tient pour vous.

1. **Trouver la source primaire.** L'article, pas le billet qui le cite, lu pour ce qui a réellement été mesuré.
2. **Vérifier le modèle, la taille et la date.** Quelles familles de modèles, de quelle taille, entraînées sur combien, mesurées quand. Un résultat sur des modèles de 2022 dit peu de chose d'une recette de 2024.
3. **Vérifier ce que couvre l'affirmation.** La précision zero-shot par rapport au total de bits n'est pas du débit de serving, et une moyenne sur des tâches académiques n'est pas du chat ouvert.
4. **Tester sur vos propres tâches.** Si la source et votre cas diffèrent, le résultat qui tranche est le vôtre (leçon 22).

Aucun des cas ci-dessous ne dit que la réponse habituelle est toujours fausse. Chacun dit ce que sa source soutient, et où elle s'arrête.

### Cas 1 : un modèle très entraîné

Kumar et al. ajustent des lois d'échelle « conscientes de la précision » et constatent que la dégradation due à la quantification post-entraînement augmente à mesure qu'un modèle est entraîné sur plus de données, « finissant par rendre activement nuisibles des données de pré-entraînement supplémentaires » ([résumé](https://arxiv.org/abs/2411.04330)). Leur intuition : un modèle entraîné sur plus de données comprime plus d'information dans ses poids, donc les perturber fait plus de mal. Ils appellent « sur-entraînés » (overtrained) les modèles dont le rapport entre tokens d'entraînement et paramètres est très élevé, et notent que Llama-3-8B est entraîné à un rapport d'environ 2000.

Lisez la portée. Ils ajustent leurs lois sur plus de 465 runs de pré-entraînement et valident sur des modèles allant jusqu'à 1.7B paramètres entraînés sur jusqu'à 26B tokens. Ils notent qu'il faut une quantité déraisonnable de données pour qu'un pré-entraînement supplémentaire devienne nuisible aux précisions couramment utilisées comme le 8 bits, mais que sur des modèles fortement sur-entraînés, les effets de dégradation deviennent non négligeables vers 5 bits et dominants en dessous. L'affirmation est donc que la réponse habituelle du 4 bits devient plus risquée à mesure que le budget d'entraînement par paramètre croît, et la preuve est faite de modèles à petite échelle plus une loi ajustée. Ce n'est pas une mesure de ce que perd un checkpoint Llama 3 particulier.

Il existe un résultat contrasté. Kurtic et al. ont mesuré des modèles Llama 3.1 quantifiés de 8B, 70B et 405B et trouvé le W4A16 récupérant 99.36 pour cent de la moyenne bf16 sur les tâches de l'Open LLM Leaderboard V1, avec un GPTQ réglé ([Kurtic et al., 2024](https://arxiv.org/abs/2411.02355)). Les deux ne se départagent pas l'un l'autre. L'un est une loi ajustée sur de petits modèles, l'autre une mesure d'une famille avec une recette réglée et des tâches moyennées. La leçon est de traiter un modèle très entraîné comme une raison de mesurer plus soigneusement, pas comme un verdict dans un sens ou dans l'autre.

### Cas 2 : un petit modèle, ou un modèle de raisonnement

Kurtic et al. rapportent que les plus petits modèles perdent un peu plus en INT4. Leurs benchmarks de raisonnement, exécutés sur des modèles DeepSeek-R1-Distill, le montrent en chiffres : la récupération de la moyenne bf16 pour le W4A16-INT était de 99.5 pour cent pour Qwen-32B et 98.3 pour cent pour Llama-70B, 97.2 pour cent pour Llama-8B, et 93.5 pour cent pour Qwen-1.5B, pour lequel le W8A8-INT récupérait 96.9 pour cent et le W8A8-FP 100.3 pour cent. Une étude distincte sur des modèles de raisonnement quantifiés, [Liu et al., 2025](https://arxiv.org/abs/2504.04823), trouve qu'une quantification sans perte est atteignable avec W8A8 ou W4A16 mais qu'il y a des risques significatifs pour la précision aux largeurs en bits plus basses. Son résumé nomme la taille du modèle, l'origine du modèle et la difficulté de la tâche comme déterminants.

Notez aussi le bruit. Sur AIME24, le modèle 1.5B a obtenu 30.1 avec une marge rapportée de 5.3 en bf16 et 24.6 avec une marge de 5.1 en W4A16, donc les écarts sur un seul benchmark et sur de petits jeux recouvrent leurs propres marges. La moyenne sur les tâches dit que le petit modèle a perdu davantage. La tâche isolée ne le prouverait pas.

### Cas 3 : le contexte long, où l'inquiétude ne tient pas

Il est facile de supposer que le contexte long casse sous la quantification. Sur le benchmark de contexte long RULER, évalué de 4k à 128k tokens, Kurtic et al. rapportent une récupération moyenne du score d'au moins 98 pour cent pour les trois formats, le modèle 405B n'étant pas évalué parce que c'est d'un coût prohibitif. C'est un seul benchmark sur Llama 3.1 et cela ne couvre pas la quantification du KV cache, que l'article liste parmi ce qu'il n'a pas étudié. C'est un bon exemple d'une inquiétude habituelle que la source ne soutient pas, pour le cas qu'elle a mesuré.

### Cas 4 : le serving limité par le calcul

Le 4 bits weight-only est la réponse habituelle à la pression sur la mémoire, et il suppose que le travail est limité par la mémoire. Les auteurs de MARLIN donnent l'arithmétique : un token d'entrée demande 2 FLOP par poids et le GPU peut exécuter environ 100 FLOP pendant le temps qu'il faut pour charger un poids en 4 bits, donc le chargement mémoire ne domine que tant que le batch est inférieur à environ 50 ([Frantar et al., 2024](https://arxiv.org/abs/2408.11743)). Le même rapport entre calcul et bande passante fait qu'un poids en 16 bits met quatre fois plus de temps à charger, donc le point de croisement du bf16 se situe vers un batch de 200. Quantifier les poids fait descendre le point de croisement, ce qui explique que le gain diminue quand les batchs grandissent.

Les méthodes INT4 existantes, rapporte QServe, subissent un surcoût de déquantification de 20 à 90 pour cent et n'accélèrent que l'inférence à petit batch ([Lin et al., 2024](https://arxiv.org/abs/2405.04532)). Dans les résultats de serving asynchrone de Kurtic et al., le W8A8 domine le débit. Pour un service borné par le débit sur du matériel moderne, la réponse habituelle du 4 bits est la mauvaise.

### Cas 5 : quand le fp8 est la valeur par défaut la plus sûre

Si le GPU calcule nativement en fp8, le W8A8-FP est effectivement sans perte à chaque taille de modèle dans les données de Kurtic et al., et n'a besoin d'aucune donnée de calibration puisqu'ils quantifient avec l'arrondi au plus proche. Un W8A8-INT bien réglé a perdu 1 à 3 pour cent, et a demandé SmoothQuant et de meilleures données de calibration à 70B. Donc là où le matériel le permet et où la mémoire tient, le fp8 est le premier essai à moindre risque, et le 4 bits doit mériter sa place par un besoin de mémoire ou de latence de décodage.

### Trancher un différend à partir de la source primaire

Deux collègues disent deux choses.

- **« AWQ bat toujours GPTQ. »** Ouvrez le tableau 1 de Kurtic et al. plutôt que de débattre. Sur les benchmarks académiques, AWQ ne devançait GPTQ que de 0.23 et 0.35 point à 8B et 70B, presque une égalité. Sur les benchmarks réels (Arena-Hard, HumanEval, MBPP), GPTQ devançait AWQ de 2.9 points à 8B (52.3 contre 49.4) et de 0.8 à 70B. Ils attribuent les constats antérieurs favorables à AWQ à des hyperparamètres sous-optimaux, et donnent leur propre configuration : GPTQ avec un écrêtage optimal en MSE là où la comparaison antérieure utilisait l'abs-max, un meilleur calibration set que le C4 par défaut, et une taille de groupe de 128 pour les deux. Vérifiez ensuite le bruit : sur Arena-Hard à 8B, les deux exécutions du modèle bf16 ont obtenu 25.1 et 26.5, donc un écart proche de 1 point est dans la variation d'une exécution à l'autre. Ce que la source soutient : aucune méthode ne gagne toujours, le classement a bougé avec la recette et le type de tâche, et les auteurs sont une seule équipe qui a aussi choisi GPTQ comme méthode. Exécutez les deux sur vos tâches.
- **« La perplexity a monté de 0.1, donc c'est bon. »** Demandez : par rapport à quelle référence, sur quel texte et quelle fenêtre, et que s'est-il passé pour les réponses individuelles ? Dutta et al. ont trouvé des schémas avec une accuracy à 0 à 2 pour cent de la référence et des flips allant jusqu'à 13.6 pour cent, et des modèles compressés à nombreux flips obtenant des scores significativement pires sur MT-Bench. Un changement de perplexity de 0.1 est une moyenne et peut être petit ou grand selon ce sur quoi elle moyenne. La source soutient « vérifiez les flips et une tâche ouverte », pas « 0.1 est trop petit pour compter » ni « 0.1 est trop grand ».

## Pratique

1. ▢ Un collègue dit « AWQ bat toujours GPTQ ». Quel tableau ouvrez-vous, et que vérifiez-vous dedans ?

<details markdown="1"><summary>Vérifier</summary>

Ouvrez la comparaison face à face de Kurtic et al. (tableau 1) et vérifiez la configuration qui la sous-tend : la même taille de groupe, la méthode d'écrêtage, le calibration set, et si les tâches sont académiques ou ouvertes. Il montre une quasi-égalité sur les tâches académiques et une avance de GPTQ sur les tâches réelles. Il ne montre pas que GPTQ gagne toujours, seulement que l'affirmation en faveur d'AWQ a des conditions.

</details>

2. ▢ Un coéquipier dit « Kumar et al. ont prouvé que le 4 bits post-entraînement va ruiner notre modèle très entraîné. » Qu'est-ce que l'article soutient ?

    - a) Une loi ajustée, donc mesurez votre modèle
    - b) Une preuve que tout schéma 4 bits échoue
    - c) Un résultat portant seulement sur l'entraînement en fp4
    - d) Une mesure de votre checkpoint exact

<details markdown="1"><summary>Vérifier</summary>

**a)** L'article ajuste des lois sur des runs allant jusqu'à 1.7B paramètres et 26B tokens et constate que davantage de données augmente la dégradation de la quantification post-entraînement, ce qui est une raison de mesurer votre modèle, pas un verdict sur lui. (b) transforme une loi ajustée en preuve. (c) est faux parce que l'article couvre la quantification post-entraînement autant que la précision d'entraînement. (d) est faux parce qu'il n'a mesuré aucun de vos checkpoints.

</details>

3. ▢ Prédisez, puis exécutez. Avec le chiffre de MARLIN d'environ 100 FLOP par chargement de poids en 4 bits et 2 FLOP par token et par poids, prédisez la taille de batch en dessous de laquelle la mémoire domine pour des poids en 4 bits et pour des poids en 16 bits si le rapport calcul sur bande passante de la machine est le même. Exécutez ensuite ceci.

    ```python
    flops_per_weight_load_4bit = 100
    flops_per_token_per_weight = 2
    for name, bytes_per_weight in [("4-bit weights", 0.5), ("16-bit weights", 2.0)]:
        flops_per_byte = flops_per_weight_load_4bit / 0.5
        crossover = flops_per_byte * bytes_per_weight / flops_per_token_per_weight
        print(f"{name:15s} memory-bound below batch about {crossover:.0f}")
    ```

<details markdown="1"><summary>Indice</summary>

Un poids en 16 bits fait quatre fois les octets d'un poids en 4 bits, donc il faut quatre fois plus de FLOP pour couvrir son chargement.

</details>

<details markdown="1"><summary>Vérifier</summary>

```text
4-bit weights   memory-bound below batch about 50
16-bit weights  memory-bound below batch about 200
```

Le chiffre pour le 4 bits est l'estimation de MARLIN elle-même, et celui du 16 bits est cette arithmétique sur la même hypothèse, pas une mesure. Le point tient sans chiffres exacts : quantifier les poids abaisse la taille de batch à partir de laquelle un service devient limité par le calcul, donc un service qui exécute de grands batchs gagne moins au 4 bits weight-only.

</details>

4. ▢ D'après le tableau de raisonnement de Kurtic et al. : Qwen-1.5B a obtenu 30.1 (marge 5.3) sur AIME24 en bf16 et 24.6 (marge 5.1) en W4A16-INT, avec 93.5 pour cent de récupération moyenne. Un collègue dit « AIME24 prouve que le 4 bits l'a cassé ». Que dites-vous ?

<details markdown="1"><summary>Vérifier</summary>

Sur AIME24 seul, les deux scores sont dans leurs marges rapportées l'un de l'autre, donc ce benchmark ne le prouve pas. Les 93.5 pour cent de récupération moyenne sur trois tâches, mis à côté des 98 à 99 pour cent des plus grands modèles, sont la preuve plus forte que le plus petit modèle a perdu davantage. Ni l'un ni l'autre ne dit que le modèle est inutilisable : l'étape suivante est d'exécuter vos propres tâches avec assez d'échantillons pour distinguer la différence du bruit.

</details>

5. ▢ Une équipe a des GPU H100, assez de mémoire pour un modèle 8B en bf16, et un traitement par lots où seul le débit compte. Un collègue propose de l'AWQ en 4 bits « parce que le 4 bits est le standard ». Plaidez contre, et dites ce qui vous ferait changer d'avis.

<details markdown="1"><summary>Vérifier</summary>

Le traitement est limité par le calcul à grand batch, où le 4 bits weight-only gagne peu et où sa déquantification peut coûter du débit (MARLIN, QServe), alors que le W8A8-FP est effectivement sans perte dans les données de Kurtic et al. et domine leurs résultats de débit asynchrone sur du matériel à fp8 natif. La mémoire n'est pas une contrainte. Ce qui vous ferait changer d'avis : une comparaison mesurée du débit et de la qualité sur votre propre taille de batch et vos propres tâches montrant le kernel 4 bits devant, ou une limite de mémoire qui imposerait un modèle plus grand que ce qui tient en 8 bits.

</details>

## Exercices en situation réelle

- [ ] Prenez une règle empirique de quantification sur laquelle vous vous appuyez (par exemple « le 4 bits, ça va ») et remontez-la jusqu'à l'article. Notez les modèles, les tailles, l'année et ce qui a été mesuré, et en quoi votre cas diffère.
- [ ] Ouvrez le tableau 1 de Kurtic et al. et notez en une ligne les différences de configuration entre leurs exécutions GPTQ et AWQ, pour pouvoir répondre à la prochaine dispute « lequel est meilleur » à partir du tableau.
- [ ] Demain : pour le modèle que vous aimeriez le plus quantifier, écrivez le cas de cette leçon qui s'y applique le plus probablement, et la mesure qui montrerait si c'est le cas.

## Pour aller plus loin

- [Liste de contrôle de relecture d'une quantification](../reference/quantization-review-checklist.md)
- [Article : "Scaling Laws for Precision", Kumar et al., 2024](https://arxiv.org/abs/2411.04330)
- [Article : "Give Me BF16 or Give Me Death? Accuracy-Performance Trade-Offs in LLM Quantization", Kurtic et al., 2024](https://arxiv.org/abs/2411.02355)
- [Article : "Quantization Hurts Reasoning? An Empirical Study on Quantized Reasoning Models", Liu et al., 2025](https://arxiv.org/abs/2504.04823)
- [Ressources](../RESOURCES.md)

---

C'est la fin du parcours, et l'habitude pour laquelle il a été construit est celle de cette leçon : un modèle quantifié est une affirmation sur un format de nombres, une méthode, un kernel et un ensemble de tâches, donc trouvez d'où vient l'affirmation, vérifiez ce qu'elle couvrait, et mesurez sur vos propres tâches avant de la défendre devant quiconque.

Ça ne passe pas ? Relisez la source primaire en haut de page, car cette leçon la condense et c'est dans la condensation que la compréhension s'échappe. Consultez le [glossaire](../GLOSSARY.md) pour tout terme qui vous a paru glissant.

Si c'est la leçon elle-même qui n'est pas claire plutôt que la matière, c'est un défaut : [ouvrez une issue](https://github.com/TokenCemetery/teach/issues).
