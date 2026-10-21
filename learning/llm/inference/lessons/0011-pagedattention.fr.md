---
title: "11. PagedAttention"
description: "Le mécanisme de table de blocs derrière vLLM, son compromis sur la taille de bloc, et comment il permet à des séquences de partager le cache d'un préfixe commun"
type: lesson
---

# Leçon 11. PagedAttention

**Lien avec la mission :** Le gestionnaire de mémoire de vLLM est le mécanisme qui fait du plafond de capacité de la leçon 2 une cible mouvante et partageable plutôt qu'un coût fixe par séquence, et cette leçon est celle où ce mécanisme est nommé en entier.
**Source primaire :** [Article : "Efficient Memory Management for Large Language Model Serving with PagedAttention", Kwon et al., SOSP 2023](https://arxiv.org/abs/2309.06180)
**Prérequis :** [Leçon 10](0010-standing-up-vllm.md), [KV cache](../GLOSSARY.md)

## Échauffement

1. ▢ De quels deux types de fragmentation souffrait une allocation de KV cache naïve, contiguë et dimensionnée à la longueur maximale (leçon 1) ?

<details markdown="1"><summary>Vérifier</summary>

La fragmentation interne : une séquence qui termine courte détient quand même de la mémoire réservée pour la longueur maximale qu'elle n'a jamais utilisée. La fragmentation externe : des trous entre des blocs réservés de tailles différentes dans lesquels le cache d'aucune autre séquence ne peut tenir.

</details>

2. ▢ En une phrase, qu'a dit la leçon 1 que PagedAttention emprunte à la mémoire virtuelle des systèmes d'exploitation ?

<details markdown="1"><summary>Vérifier</summary>

Le découpage du cache en blocs de taille fixe, stockés de façon non contiguë, adressés par une table propre à chaque séquence qui fait correspondre les positions logiques aux blocs physiques, la même idée que les tables de pages d'un OS.

</details>

## À savoir

### La table de blocs, un niveau de détail de plus

Le KV cache de chaque séquence est divisé en **blocs** de taille fixe, chacun contenant les clés et les valeurs d'un nombre donné de tokens. La **table de blocs** d'une séquence fait correspondre ses positions logiques de tokens à des emplacements physiques de blocs en mémoire, où qu'ils se trouvent. L'attention d'une séquence donnée cherche ses blocs à travers cette table plutôt que de supposer qu'ils sont contigus, ce qui permet au gestionnaire de mémoire sous-jacent de placer les blocs partout où il a de la place, exactement comme une table de pages d'OS laisse les pages mémoire d'un processus se trouver n'importe où dans la RAM physique.

### La taille de bloc est un compromis, pas un paramètre gratuit

Une taille de bloc plus grande signifie moins de blocs par séquence et moins de comptabilité de table de blocs, mais davantage d'espace gaspillé dans le dernier bloc, partiellement rempli, d'une séquence dont la longueur ne se divise pas exactement (de la fragmentation interne, mais à une échelle bien plus petite que la version naïve de la leçon 1, qui portait sur toute la séquence). Une taille de bloc plus petite gaspille moins d'espace par séquence mais signifie plus de blocs, et plus d'entrées de table de blocs, à suivre. La taille de bloc par défaut de vLLM (16 tokens) est un juste milieu choisi entre ces deux coûts, pas un nombre arbitraire.

### Partager des blocs entre séquences

Parce que les blocs d'une séquence sont atteints indirectement, par sa table de blocs, plutôt qu'en supposant une disposition physique fixe, les tables de blocs de deux séquences différentes peuvent pointer vers le *même* bloc physique quand son contenu est identique, le plus souvent un préfixe de prompt partagé. L'échantillonnage parallèle (demander plusieurs complétions du même prompt) ou la beam search en sont les cas les plus clairs : chaque échantillon partage le cache des mêmes tokens de prompt, donc les blocs du prompt n'ont besoin d'exister physiquement qu'une seule fois, la table de blocs de chaque échantillon pointant vers eux. Quand la génération d'un échantillon diverge des autres (tout nouveau token propre à l'échantillon), un **copy-on-write** crée la propre copie privée de cet échantillon pour le bloc modifié, exactement le mécanisme qu'un système d'exploitation utilise quand deux processus partagent des pages mémoire jusqu'à ce que l'un d'eux écrive.

![Deux tables de blocs, la séquence A à gauche et la séquence B à droite, chacune faisant correspondre quatre positions logiques à des numéros de blocs physiques. Pour les positions 0 à 2, les deux tables pointent vers les trois mêmes blocs physiques partagés contenant un préfixe de prompt identique, si bien que le cache de ce préfixe n'existe qu'une seule fois en mémoire. À la position 3, les deux séquences ont généré des tokens différents, donc un copy-on-write a donné à chacune son propre bloc privé : le bloc 9 de la séquence A et le bloc 3 de la séquence B, aucun n'étant partagé avec l'autre.](images/block-table-sharing.svg)

## Pratique

1. ▢ Avec une taille de bloc de 16 tokens, une séquence génère 40 tokens de sortie. Combien de blocs utilise-t-elle, et combien d'espace est gaspillé dans le dernier ?

<details markdown="1"><summary>Indice</summary>

Divisez 40 par 16 et arrondissez à un nombre entier de blocs supérieur ; le gaspillage est ce qui reste inutilisé dans le dernier bloc, partiellement rempli.

</details>

<details markdown="1"><summary>Vérifier</summary>

`40 / 16 = 2.5`, arrondi à 3 blocs. Les deux premiers contiennent 32 tokens ; le troisième contient les 8 restants, gaspillant les 8 autres emplacements de ce bloc, de la fragmentation interne à l'échelle d'un bloc au lieu d'une séquence entière.

</details>

2. ▢ Pourquoi une taille de bloc plus petite réduit-elle cet espace gaspillé, et que coûte-t-elle en échange ?

<details markdown="1"><summary>Vérifier</summary>

Une taille de bloc plus petite signifie que le dernier bloc, partiellement rempli, a moins d'emplacements inutilisés à gaspiller, puisqu'il y a moins de positions dans chaque bloc au départ. Le coût est un plus grand nombre de blocs par séquence au total, et donc plus d'entrées de table de blocs que le gestionnaire de mémoire doit suivre et consulter.

</details>

3. ▢ Dix échantillons parallèles sont demandés à partir du même prompt de 200 tokens, avec une taille de bloc de 16 tokens. De combien de blocs physiques le cache du prompt a-t-il besoin, avec partage de blocs, par rapport à sans partage ?

<details markdown="1"><summary>Indice</summary>

Déterminez combien de blocs une copie du prompt de 200 tokens demande, puis décidez combien de copies existent dans chaque cas.

</details>

<details markdown="1"><summary>Vérifier</summary>

`200 / 16 = 12.5`, arrondi à 13 blocs pour une copie du prompt. Sans partage, les 10 échantillons détiennent chacun leur propre copie : `13 × 10 = 130` blocs. Avec partage, la table de blocs de chaque échantillon pointe vers les mêmes 13 blocs physiques pour le prompt partagé, donc seuls 13 blocs sont nécessaires jusqu'à ce qu'un échantillon commence à générer ses propres tokens divergents.

</details>

4. ▢ L'un des dix échantillons de la question 3 génère un token différent de ce qu'a généré tout autre échantillon à cette position. Qu'arrive-t-il au cache de cet échantillon à ce moment ?

<details markdown="1"><summary>Vérifier</summary>

Un copy-on-write se déclenche : cet échantillon obtient sa propre copie privée du bloc dans lequel il écrit, au lieu de modifier le bloc partagé vers lequel les tables de tous les autres échantillons pointent toujours. Seul l'échantillon qui diverge paie un nouveau bloc ; les neuf autres continuent de partager l'original.

</details>

5. ▢ Laquelle de ces affirmations est vraie à propos du choix de taille de bloc de vLLM ?

    - a) Des blocs plus grands gaspillent toujours plus de mémoire que des plus petits, sans bénéfice en contrepartie
    - b) La taille de bloc échange la fragmentation interne contre le surcoût de comptabilité de la table de blocs
    - c) La taille de bloc n'affecte que les charges de travail d'échantillonnage parallèle, pas le serving d'une requête unique
    - d) Une taille de bloc plus petite augmente toujours l'utilisation totale de la mémoire

<details markdown="1"><summary>Vérifier</summary>

**b)** Des blocs plus petits gaspillent moins d'espace dans un dernier bloc partiellement rempli mais exigent de suivre plus d'entrées de table de blocs ; des blocs plus grands, c'est l'inverse. (a) est fausse : des blocs plus grands réduisent le surcoût de comptabilité, ce qui est un vrai bénéfice. (c) est fausse : chaque séquence, partagée ou non, est divisée en blocs et paie le compromis fragmentation/comptabilité. (d) est fausse : des blocs plus petits réduisent la fragmentation interne, ce qui peut diminuer l'utilisation totale de la mémoire, pas toujours l'augmenter.

</details>

## Exercices en situation réelle

- [ ] Trouvez l'option ou le paramètre de configuration de taille de bloc de vLLM dans sa documentation et lisez quelle est sa valeur par défaut et ce que la documentation dit sur le fait de la changer.
- [ ] Si vous pouvez exécuter un serveur, envoyez plusieurs requêtes d'échantillonnage parallèle (`n` supérieur à 1) pour le même prompt, et voyez si la documentation ou les journaux rapportent quelque chose sur le partage de préfixe ou de blocs.
- [ ] Demain : lisez un paragraphe sur le prefix caching (réutiliser les blocs d'un system prompt partagé entre des requêtes par ailleurs sans lien) et notez en quoi c'est la même idée de partage de blocs appliquée entre requêtes au lieu d'à l'intérieur d'une seule.

## Pour aller plus loin

- [Article : "Efficient Memory Management for Large Language Model Serving with PagedAttention", Kwon et al., SOSP 2023](https://arxiv.org/abs/2309.06180)
- [Doc : vLLM Documentation, vLLM Project](https://docs.vllm.ai/en/latest/)
- [Ressources](../RESOURCES.md)

---

Ça ne passe pas ? Relisez la source primaire en haut de page, car cette leçon la condense et c'est dans la condensation que la compréhension s'échappe. Consultez le [glossaire](../GLOSSARY.md) pour tout terme qui vous a paru glissant.

Si c'est la leçon elle-même qui n'est pas claire plutôt que la matière, c'est un défaut : [ouvrez une issue](https://github.com/TokenCemetery/teach/issues).
