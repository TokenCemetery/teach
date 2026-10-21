---
title: "15. GKD et MiniLLM"
description: "Échantillonner à partir de l'élève et évaluer avec l'enseignant, et les choix de divergence et de mélange qui vont avec"
type: lesson
---

# Leçon 15. GKD et MiniLLM

**Lien avec la mission :** La mission vous demande de mener une distillation on-policy et d'en choisir les réglages, ce qui exige de savoir ce que font les deux boutons de GKD, ce que MiniLLM fait différemment, et quels résultats viennent de quelle tâche.
**Source primaire :** [Article : "On-Policy Distillation of Language Models: Learning from Self-Generated Mistakes", Agarwal et al., 2023](https://arxiv.org/abs/2306.13649), sections 2 à 4
**Prérequis :** [Leçon 5](0005-forward-and-reverse-kl.md), [Leçon 14](0014-exposure-bias.md), [Distillation généralisée des connaissances](../GLOSSARY.md), [Distillation on-policy](../GLOSSARY.md), [KL inverse](../GLOSSARY.md)

## Échauffement

1. ▢ Sur quelles séquences un pas de distillation on-policy s'entraîne-t-il, et quel modèle les décide ?

<details markdown="1"><summary>Vérifier</summary>

Sur des séquences que l'élève génère pendant l'entraînement, donc c'est l'élève qui les décide. L'enseignant ne fait qu'évaluer chaque token que l'élève a choisi. Entraîner sur des séquences fixes, écrites par des humains ou par l'enseignant, est de l'[off-policy](../GLOSSARY.md).

</details>

2. ▢ La KL directe pousse l'élève à couvrir tous les modes de l'enseignant et la KL inverse le pousse à s'engager sur un seul. Laquelle des deux risque de mettre de la probabilité sur du texte que l'enseignant juge improbable ?

<details markdown="1"><summary>Vérifier</summary>

La KL directe, parce qu'elle pénalise de manquer toute région que couvre l'enseignant, si bien qu'un petit élève s'étire sur des régions qu'il ne sait pas bien modéliser. La KL inverse pénalise la probabilité là où l'enseignant en a peu, donc elle évite cela au prix de la diversité.

</details>

3. ▢ Quelle est la différence entre le biais d'exposition et un élève simplement trop petit ?

<details markdown="1"><summary>Vérifier</summary>

Le biais d'exposition concerne les préfixes : l'élève s'entraîne sur des préfixes écrits par quelqu'un d'autre et génère à partir des siens. Un élève trop petit a une limite de capacité sur ce qu'il peut représenter, qui subsisterait même si chaque préfixe était le sien. L'entraînement on-policy s'attaque au premier et ne peut pas supprimer le second.

</details>

## À savoir

### GKD : une boucle, deux boutons

La distillation généralisée des connaissances (GKD) est un algorithme avec deux hyperparamètres (Agarwal et al., algorithme 1). À chaque pas, il tire un nombre aléatoire. Avec la probabilité lambda, il génère des séquences à partir de l'élève pour un batch de prompts. Sinon, il prend un batch dans un jeu fixe de séquences de vérité terrain ou écrites par l'enseignant. Puis il met à jour l'élève pour minimiser une divergence entre les distributions de tokens de l'enseignant et de l'élève, moyennée sur les positions, sans gradient à travers l'échantillonnage.

Lambda est la **fraction de données de l'élève**. Lambda 0 est la distillation supervisée ordinaire et lambda 1 est purement on-policy. Les variantes « mixed » de l'article utilisent 0.5. Pendant l'entraînement, l'élève échantillonne à la température 1 pour garder ses séquences diverses.

Le second bouton est la divergence. GKD utilise la divergence de Jensen-Shannon généralisée, JSD(beta), un mélange borné des deux directions de la KL. Avec la convention de l'article, beta proche de 0 se comporte comme la KL directe et beta proche de 1 comme la KL inverse, donc 0.1, 0.5 et 0.9 sont des points le long de cette ligne. Le trainer de TRL documente la même direction : beta 0.0 approche la KL directe et beta 1.0 la KL inverse.

### Ce qu'a trouvé l'article, tâche par tâche

Les élèves ont T5-small (77M), T5-base (250M) et T5-large (800M) de paramètres, distillés à partir d'un T5-XL affiné d'environ 3B, donc l'enseignant est 38 fois, 12 fois et 3.8 fois plus grand. Les résultats sont ceux de l'article sur T5, pas des faits généraux sur les LLM.

| Tâche | Métrique | Ce qui a fonctionné | Source dans l'article |
|---|---|---|---|
| Résumé XSum | ROUGE-2 | GKD on-policy avec JSD(0.9) a battu les références supplémentaires ImitKD et f-distill en décodage glouton et en échantillonnage à température. Les divergences qui cherchent un mode ont fait mieux en échantillonnage à température, et la divergence comptait peu en décodage glouton | Section 4.1, figures 3 et 4 |
| WMT14 anglais vers allemand | BLEU | La JSD généralisée a battu la KL directe et la KL inverse, avec un écart plus petit pour l'élève plus grand. Les données générées par l'élève seules ont battu les autres mélanges de données. La figure 1 utilisait JSD(0.1) | Section 4.2, figure 6 |
| GSM8K avec chaîne de raisonnement | précision | Les chaînes générées par l'élève seules ont battu les données fixes ou mixtes. La KL directe a bien fonctionné, et la KL inverse aussi. Les gains se maintenaient dès qu'au moins 25 % des données étaient on-policy | Section 4.3, figures 8 et 9 |
| Instruction tuning sur FLAN | MMLU et BBH held-out | GKD on-policy avec KL inverse a nettement battu la KL directe | Section 4.4, figure 10 |

Le résumé des auteurs est que la meilleure divergence dépend de la tâche, alors que les données on-policy et mixtes battent systématiquement les données fixes. Deux autres résultats valent d'être connus. Sur XSum avec T5-small, GKD on-policy sur un sous-échantillon de 5 %, sans résumés de vérité terrain, a battu le KD supervisé et ImitKD entraînés sur le jeu complet (section 4.1). En moyenne sur les tailles d'élève, les gains de performance par rapport à l'élève initial étaient de 2.1 fois ceux du KD de référence sur le résumé, 1.7 fois sur la traduction et 1.9 fois sur le raisonnement arithmétique (introduction).

Pour l'instruction tuning, le texte de l'article et la légende de sa figure 10 ne s'accordent pas sur le fait que l'élève soit T5-base ou T5-large, cette leçon ne cite donc pas de taille d'élève pour cette tâche. L'enseignant a atteint 52.4 % sur MMLU et 41 % sur BBH. Les auteurs font l'hypothèse que la KL inverse fonctionne là parce que sa nature de recherche de mode amène le modèle à se concentrer sur l'intention principale de l'instruction, et ils la présentent comme une hypothèse, pas comme un constat.

### MiniLLM : la KL inverse optimisée comme une politique

Gu et al. (MiniLLM) arrivent à l'entraînement on-policy par une autre direction. Ils soutiennent que la KL directe pousse un élève de faible capacité à surestimer les régions de faible probabilité de l'enseignant, et minimisent à la place la KL inverse sur des séquences entières. Comme l'espérance est sous la propre distribution de l'élève, ils dérivent le gradient avec le théorème du gradient de politique et l'entraînent comme de l'apprentissage par renforcement, avec le log-rapport des probabilités enseignant sur élève comme signal par token.

Le gradient de politique simple a des problèmes, et l'article ajoute trois correctifs :

| Problème | Correctif | Détail |
|---|---|---|
| Variance élevée | Décomposition en une seule étape | Le terme par token est calculé en sommant sur le vocabulaire au lieu d'échantillonner |
| Détournement de la récompense : du texte dégénéré, comme des phrases répétées, obtient de bons scores auprès de l'enseignant | Échantillonnage mêlé à l'enseignant | Échantillonner à partir de alpha fois l'enseignant plus (1 moins alpha) fois l'élève à chaque étape, avec alpha 0.2 dans les expériences |
| Les longues sorties reçoivent de petites récompenses cumulées, donc l'élève apprend à produire des réponses très courtes ou vides | Normalisation par la longueur | Normaliser la récompense cumulée par la longueur restante |

Il ajoute aussi un écrêtage et une loss de modélisation de langage sur du texte de pré-entraînement pour garder la performance sur les benchmarks généraux. L'entraînement part d'un élève affiné sur les données de la tâche. Notez la différence avec GKD : les échantillons de MiniLLM viennent en partie de l'enseignant à cause du mélange, il n'est donc pas purement on-policy, et il optimise un objectif au niveau de la séquence là où GKD moyenne une divergence au niveau du token.

### Les résultats de MiniLLM

Le cadre est le suivi d'instructions sur 15K exemples de Dolly, environ 12.5K pour l'entraînement, avec des élèves GPT-2 (120M à 760M, enseignant GPT-2 1.5B), OPT (1.3B à 6.7B, enseignant OPT 13B) et LLaMA (7B, enseignant LLaMA 13B). Quelques cellules du tableau 1, le score moyen de retour de GPT-4 sur DollyEval :

| Élève | Fine-tuning seul | KD standard | SeqKD | MiniLLM | Enseignant |
|---|---|---|---|---|---|
| OPT 1.3B | 52.6 | 52.7 | 51.0 | 60.7 | 70.3 |
| OPT 6.7B | 67.9 | 68.6 | 69.6 | 70.8 | 70.3 |
| LLaMA 7B | 73.0 | 73.7 | 73.6 | 76.4 | 79.0 |

La métrique GPT-4 est le rapport entre le score de GPT-4 pour la réponse du modèle et son score pour la réponse de référence, elle est donc relative, pas absolue. Les auteurs rapportent aussi que les élèves battent parfois l'enseignant sur Rouge-L et conjecturent que cela reflète un biais d'exposition chez l'enseignant. Sur la calibration, l'élève MiniLLM avait une erreur plus faible que les références à KL directe mais toujours supérieure à celle de l'enseignant : sur SST2, ECE 0.099 contre 0.025 pour l'enseignant et 0.191 pour le KD standard (tableau 2).

### Ce que vous ne pouvez pas conclure

Chaque article a réglé sa propre méthode sur ses propres élèves, enseignants et métriques, donc les nombres ci-dessus ne classent pas GKD par rapport à MiniLLM. Je n'ai trouvé de comparaison directe dans aucun des deux articles. Comparez leurs idées, et testez les deux sur votre propre paire.

### Une configuration exécutable

Le `GKDTrainer` de TRL expose les deux boutons sous les noms `lmbda` et `beta` dans `GKDConfig`. Ses valeurs par défaut documentées sont 0.5 pour chacun, avec `temperature` 0.9 et `max_new_tokens` 128 pour la génération, et `seq_kd` désactivé. L'exemple de la documentation ci-dessous distille Qwen2-1.5B-Instruct dans Qwen2-0.5B-Instruct. Je ne l'ai pas exécuté, vérifiez donc le chemin d'import par rapport à la version de TRL que vous installez, puisque la documentation actuelle place GKD sous `trl.experimental`.

```python
from datasets import Dataset
from transformers import AutoModelForCausalLM, AutoTokenizer
from trl.experimental.gkd import GKDConfig, GKDTrainer

tokenizer = AutoTokenizer.from_pretrained("Qwen/Qwen2-0.5B-Instruct")
student = AutoModelForCausalLM.from_pretrained("Qwen/Qwen2-0.5B-Instruct")
teacher = AutoModelForCausalLM.from_pretrained("Qwen/Qwen2-1.5B-Instruct")

train = Dataset.from_dict({"messages": [[
    {"role": "user", "content": "Hi, how are you?"},
    {"role": "assistant", "content": "I'm great thanks"},
]] * 100})

args = GKDConfig(
    output_dir="gkd-model",
    per_device_train_batch_size=1,
    lmbda=1.0,  # purely on-policy: every batch is student-generated
    beta=1.0,   # generalized JSD at the reverse-KL end
)
trainer = GKDTrainer(model=student, teacher_model=teacher, args=args,
                     processing_class=tokenizer, train_dataset=train)
trainer.train()
```

Les deux modèles partagent un tokenizer parce qu'ils sont de la même famille, ce que la leçon 6 a expliqué être nécessaire pour la distillation de logits. Les propres indications de la page TRL concordent avec l'article : les données on-policy (`lmbda` élevé) donnent de meilleurs résultats, et le meilleur `beta` dépend de la tâche et de la méthode d'évaluation.

## Pratique

1. ▢ Dans GKD, quels réglages de lambda et de la divergence reproduisent (a) la distillation supervisée et (b) le KD on-policy tels que l'article les définit ?

<details markdown="1"><summary>Vérifier</summary>

Les deux utilisent la KL directe. Lambda 0 donne le KD supervisé, où l'élève ne génère jamais, et lambda 1 donne le KD on-policy, où chaque séquence est celle de l'élève. Les valeurs intermédiaires sont les variantes mixtes. La divergence et la source des données sont des boutons indépendants, c'est pourquoi la même KL directe apparaît dans les deux.

</details>

2. ▢ Dans l'expérience d'instruction tuning de GKD sur FLAN, quel appariement l'article a-t-il trouvé nettement meilleur que son équivalent en KL directe ?

    - a) KL directe, échantillons de l'élève
    - b) KL inverse, échantillons de l'élève
    - c) KL directe, séquences fixes
    - d) KL inverse, séquences fixes

<details markdown="1"><summary>Vérifier</summary>

**b)** GKD on-policy avec KL inverse a surpassé les autres approches à la section 4.4. (a) est le choix de l'article pour XSum et GSM8K en décodage glouton, pas pour l'instruction tuning. (c) et (d) utilisent des données fixes, que l'article a trouvées systématiquement plus faibles que les données générées par l'élève.

</details>

3. ▢ Associez chaque correctif de MiniLLM à l'échec qu'il évite : (1) échantillonnage mêlé à l'enseignant, (2) normalisation par la longueur, (3) décomposition en une seule étape. Échecs : A, l'élève renvoie des réponses très courtes ou vides. B, variance élevée du gradient. C, l'élève trouve du texte dégénéré que l'enseignant note bien.

<details markdown="1"><summary>Vérifier</summary>

(1) va avec C, (2) avec A, (3) avec B. L'échantillonnage mêlé à l'enseignant supprime les échantillons dégénérés en mêlant l'enseignant à la distribution d'échantillonnage. La normalisation par la longueur empêche les longues séquences d'être pénalisées par de petites récompenses cumulées. La décomposition en une seule étape calcule le terme par token sur tout le vocabulaire au lieu d'échantillonner, ce qui réduit la variance.

</details>

4. ▢ Un élève entraîné avec un objectif de style MiniLLM se met à émettre une phrase répétée à laquelle l'enseignant attribue une forte probabilité. Quelle astuce vise cela, et quelle valeur l'article a-t-il utilisée ?

<details markdown="1"><summary>Indice</summary>

Le score de l'enseignant est la récompense. Un échantillon dégénéré que l'enseignant aime exploite cette récompense.

</details>

<details markdown="1"><summary>Vérifier</summary>

L'échantillonnage mêlé à l'enseignant, que l'article introduit contre le détournement de la récompense, avec alpha 0.2 dans toutes ses expériences (section 3.1). La valeur est le choix de cet article sur sa configuration, traitez-la donc comme un point de départ, pas comme une constante.

</details>

5. ▢ D'après le tableau 1 ci-dessus, quelle part de l'écart entre l'élève au fine-tuning seul et l'enseignant MiniLLM comble-t-il pour OPT 1.3B et pour LLaMA 7B ? Que ne pouvez-vous pas conclure de la ligne OPT 6.7B ?

<details markdown="1"><summary>Vérifier</summary>

OPT 1.3B : l'écart est 70.3 moins 52.6, soit 17.7, et MiniLLM gagne 8.1, environ 46 %. LLaMA 7B : l'écart est 6.0 et MiniLLM gagne 3.4, environ 57 %. Dans la ligne OPT 6.7B, MiniLLM obtient 70.8 contre 70.3 pour l'enseignant, mais cela ne montre pas que l'élève est meilleur : la métrique est relative aux réponses de référence, la différence est d'un demi-point, et c'est une seule paire de modèles.

</details>

6. ▢ Vous voulez un run purement on-policy avec KL inverse dans TRL. Quelles deux valeurs de configuration réglez-vous, et pourriez-vous l'exécuter si vous n'aviez que le texte de l'enseignant ?

<details markdown="1"><summary>Vérifier</summary>

`lmbda=1.0` et `beta=1.0`. Non : la divergence a besoin de la distribution de l'enseignant à chaque position de la séquence de l'élève, il vous faut donc le modèle enseignant lui-même, pas un export de texte stocké. Avec seulement du texte, vous seriez de retour au niveau de la séquence (leçon 8). L'option `seq_kd` de TRL n'y change rien, puisque l'enseignant donne toujours un retour spécifique à chaque token.

</details>

## Exercices en situation réelle

- [ ] Lisez la section 3.1 de l'article GKD. Écrivez la loss en une ligne, puis entourez où lambda et la divergence interviennent chacun.
- [ ] Ouvrez le tableau 1 de l'article MiniLLM et choisissez un élève pour lequel MiniLLM n'a pas battu l'enseignant sur toutes les colonnes. Notez sur quelle métrique il a perdu et de combien.
- [ ] Demain : sans notes, écrivez ce que contrôlent lambda et beta, nommez une tâche où la KL inverse a gagné dans GKD, et nommez les trois correctifs de MiniLLM.

## Pour aller plus loin

- [Distillation on-policy](../reference/on-policy-distillation.md)
- [Article : "On-Policy Distillation of Language Models: Learning from Self-Generated Mistakes", Agarwal et al., 2023](https://arxiv.org/abs/2306.13649)
- [Article : "MiniLLM: On-Policy Distillation of Large Language Models", Gu et al., 2023](https://arxiv.org/abs/2306.08543)
- [Doc : "Generalized Knowledge Distillation Trainer", Hugging Face TRL](https://huggingface.co/docs/trl/main/en/gkd_trainer)
- [Ressources](../RESOURCES.md)

---

Ça ne passe pas ? Relisez la source primaire en haut de page, car cette leçon la condense et c'est dans la condensation que la compréhension s'échappe. Consultez le [glossaire](../GLOSSARY.md) pour tout terme qui vous a paru glissant.

Si c'est la leçon elle-même qui n'est pas claire plutôt que la matière, c'est un défaut : [ouvrez une issue](https://github.com/TokenCemetery/teach/issues).
