---
title: "10. Mettre en place vLLM"
description: "Installer vLLM, lancer son serveur, et trouver les options qui portent les concepts déjà enseignés"
type: lesson
---

# Leçon 10. Mettre en place vLLM

**Lien avec la mission :** Chaque formule des étapes 1 à 3, l'empreinte du cache, la taille de batch, le schéma de quantification, devient dans cette leçon une vraie option d'une vraie commande ; c'est ici que l'arithmétique se transforme en un serveur qui répond à des requêtes.
**Source primaire :** [Doc : vLLM Documentation, vLLM Project](https://docs.vllm.ai/en/latest/)
**Prérequis :** [Leçon 9](0009-picking-a-quantization-scheme.md), [KV cache](../GLOSSARY.md)

## Échauffement

1. ▢ Un serveur dépasse son budget de latence à la taille de batch actuelle. Quelle option, selon le raisonnement de la leçon 6, est la première à vérifier ?

<details markdown="1"><summary>Vérifier</summary>

Le réglage de taille de batch maximale : la plus grande taille de batch qui satisfait encore le budget de latence est ce que la leçon 6 a défendu, c'est donc le paramètre qui la contrôle directement.

</details>

2. ▢ Pourquoi un choix au moment du serving d'utiliser fp8 pour le KV cache, plutôt que la précision des poids du modèle, pourrait-il jamais avoir du sens (leçon 3) ?

<details markdown="1"><summary>Vérifier</summary>

La précision du cache est un levier indépendant de la précision des poids du modèle. Diviser par deux le `bytes_per_value` du cache divise d'emblée son empreinte par deux, sans rien changer au modèle lui-même, ce qui rachète de la capacité comme le ferait un modèle plus petit.

</details>

## À savoir

### Installer vLLM

vLLM s'installe comme un paquet Python, `pip install vllm`, et exige un GPU compatible CUDA ; c'est la moitié GPU de la mission de cet espace de travail, llama.cpp couvrant le CPU et l'edge à l'étape suivante. L'installation tire automatiquement un PyTorch et une chaîne d'outils CUDA correspondants pour les configurations courantes, ce qu'il vaut la peine de vérifier par rapport à la version du pilote CUDA installé avant de supposer qu'un échec d'installation vient d'autre chose.

### Lancer le serveur

`vllm serve <model>` démarre un serveur HTTP compatible OpenAI pour le modèle nommé (un chemin local ou un identifiant du Hugging Face Hub), qui écoute par défaut sur le port 8000 :

```text
vllm serve meta-llama/Llama-2-7b-hf
```

Cette commande unique effectue le téléchargement (si nécessaire), le chargement des poids et le démarrage du serveur, dont les étapes 1 à 3 raisonnaient sur les conséquences en mémoire et en latence.

### Envoyer une requête

Comme le serveur parle la forme de l'API OpenAI, une requête ressemble à n'importe quel appel de chat completion OpenAI, dirigé vers le serveur local :

```bash
curl http://localhost:8000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{"model": "meta-llama/Llama-2-7b-hf", "messages": [{"role": "user", "content": "Say hello"}]}'
```

### Où les concepts déjà enseignés apparaissent comme des options

La ligne de commande est l'endroit où les étapes 1 à 3 cessent d'être de l'arithmétique pour devenir de la configuration :

- `--max-num-seqs` : le plafond de taille de batch que la leçon 6 a appris à défendre face à un budget de latence.
- `--kv-cache-dtype` : la précision du cache que la leçon 3 a présentée comme un levier indépendant des poids du modèle (par exemple, `fp8`).
- `--quantization` : nomme le schéma, comme `gptq` ou `awq`, que les leçons 7 à 9 ont appris à choisir et à défendre, quand on sert un checkpoint déjà quantifié.
- Le continuous batching et le chunked prefill (leçons 4 et 5) sont activés par défaut ; il n'y a pas d'option pour désactiver le mécanisme de base, seulement pour le régler, comme la taille de morceau.

## Pratique

1. ▢ Une équipe exécute `vllm serve some-model --max-num-seqs 32 --kv-cache-dtype fp8`. En termes des leçons 6 et 3, que contrôle réellement chacune de ces deux options ?

<details markdown="1"><summary>Vérifier</summary>

`--max-num-seqs 32` plafonne la taille de batch à 32, le chiffre que la leçon 6 défendrait face à un budget de latence annoncé et au plafond de capacité de la leçon 2. `--kv-cache-dtype fp8` stocke le KV cache en fp8 au lieu de la valeur par défaut, ce qui divise par deux son empreinte par token indépendamment de la précision des poids du modèle, exactement le levier décrit à la leçon 3.

</details>

2. ▢ Une équipe démarre un serveur avec `vllm serve some-model`, sans nommer aucune option `--quantization`. Dans quelle précision le serveur sert-il le modèle, et pourquoi ?

<details markdown="1"><summary>Vérifier</summary>

Celle dans laquelle le checkpoint lui-même a été enregistré, le plus souvent fp16 ou bf16, puisqu'aucun schéma de quantification n'a été demandé. `--quantization` ne s'applique que pour servir un checkpoint quantifié à l'avance ou que l'option demande à vLLM de quantifier au chargement ; l'omettre signifie que rien n'est quantifié.

</details>

3. ▢ Prédisez, avant de vérifier : après avoir exécuté `vllm serve` avec succès, quelle information unique de la requête curl de la section « À savoir » de cette leçon doit correspondre à quelque chose avec quoi le serveur a réellement été démarré, sous peine d'échec de la requête ?

<details markdown="1"><summary>Indice</summary>

Regardez le champ `"model"` dans la commande curl.

</details>

<details markdown="1"><summary>Vérifier</summary>

Le champ `"model"` du corps de la requête doit correspondre au nom (ou au chemin) du modèle avec lequel le serveur a été démarré. Le serveur sert un seul modèle à la fois ; nommer un autre modèle dans la requête est ce qui produit le plus souvent une erreur sur un appel par ailleurs bien formé.

</details>

4. ▢ Laquelle de ces affirmations est vraie à propos du comportement par défaut de vLLM quand aucune option de batching ou de cache n'est donnée ?

    - a) Il se rabat sur le batching statique tant que `--max-num-seqs` n'est pas défini
    - b) Le continuous batching et le chunked prefill tournent par défaut ; les options ne font que les régler davantage
    - c) Il refuse de démarrer tant qu'un dtype de KV cache n'est pas explicitement choisi
    - d) Il sert par défaut à la précision la plus basse que le matériel prend en charge

<details markdown="1"><summary>Vérifier</summary>

**b)** Le continuous batching et le chunked prefill sont le mécanisme par défaut, et non quelque chose qu'une option active ; les options disponibles règlent des paramètres autour d'eux, comme la taille de batch maximale ou une taille de morceau. (a) est fausse : il n'y a pas de repli sur le batching statique. (c) est fausse : un dtype de cache par défaut est utilisé si aucun n'est nommé. (d) est fausse : la valeur par défaut est la précision enregistrée du checkpoint lui-même, pas la plus basse que le matériel prend en charge.

</details>

## Exercices en situation réelle

- [ ] Installez vLLM (`pip install vllm`) sur une machine avec un GPU compatible CUDA, et exécutez `vllm serve` avec un petit modèle que vous pouvez vous permettre de télécharger.
- [ ] Envoyez la requête curl de cette leçon à votre serveur en fonctionnement, et confirmez que vous obtenez une vraie complétion en retour, et non une erreur.
- [ ] Demain : redémarrez le serveur avec `--max-num-seqs` réglé sur un petit nombre (comme 2) puis sur un grand, et voyez si vous pouvez observer une différence dans son comportement sous quelques requêtes concurrentes.

## Pour aller plus loin

- [Doc : vLLM Documentation, vLLM Project](https://docs.vllm.ai/en/latest/)
- [Ressources](../RESOURCES.md)

---

Ça ne passe pas ? Relisez la source primaire en haut de page, car cette leçon la condense et c'est dans la condensation que la compréhension s'échappe. Consultez le [glossaire](../GLOSSARY.md) pour tout terme qui vous a paru glissant.

Si c'est la leçon elle-même qui n'est pas claire plutôt que la matière, c'est un défaut : [ouvrez une issue](https://github.com/TokenCemetery/teach/issues).
