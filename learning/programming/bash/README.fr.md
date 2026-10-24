---
title: Bash
description: "Écrire du shell qui survit à la production : quoting, code de sortie, modes de défaillance, et savoir quand s'arrêter pour passer à un vrai langage"
type: topic
---

# Apprentissage : Bash

Savoir écrire et maintenir des scripts shell pour des pipelines de CI, du déploiement et de l'outillage d'exploitation qui ne cassent pas discrètement sur une mauvaise entrée ou une variable non définie, et reconnaître quand un script a dépassé le shell et doit plutôt passer à un vrai langage.

**Dernière leçon :** [17. shellcheck, shfmt et tester un script](lessons/0017-shellcheck-shfmt-and-testing-a-script.md)

## Objectif

- Écrire un script de CI ou de déploiement, ou un utilitaire d'exploitation, qui gère correctement le quoting, le code de sortie et les modes de défaillance courants, et expliquer pourquoi chaque choix était nécessaire.
- Face à un script shell, nommer la façon précise dont il casserait sur un cas limite (expansion non quotée, variable non définie, code de sortie d'une commande ignoré).
- Reconnaître quand un script a quitté la zone où le shell ne demande aucun jugement, et dire pourquoi la tâche relève désormais plutôt de `programming/python`.

## Contraintes

- Ne suppose aucune expérience préalable des scripts shell.
- Écrit pour la portabilité POSIX `sh` plutôt que pour des idiomes propres à bash, même si bash est le cœur du sujet ; une fonctionnalité propre à bash est signalée comme telle lorsqu'elle est utilisée.
- N'aborde `awk`/`sed` que là où un script en a réellement besoin, pas comme des sujets à part entière.

## Hors périmètre

- Tout ce qui se trouve au-delà du point où un script aurait dû cesser d'être du shell : voir [`programming/python`](../../programming/python/) pour cette frontière.

## Le fil conducteur

Onze étapes, du quoting jusqu'à shellcheck, shfmt et aux tests. Une étape comprend plusieurs leçons et les frontières sont souples ; ce qui termine une étape, c'est la capacité acquise, pas le nombre de leçons.

| Étape | Leçons | Contenu | Terminée quand |
|---|---|---|---|
| 1. Quoting | 0001 | L'unique habitude qui évite la façon la plus courante dont les scripts shell cassent en production | Vous savez quoter correctement et expliquer pourquoi une expansion non quotée casse |
| 2. Code de sortie et gestion des erreurs | 0002 à 0003 | `$?`, le mode strict officieux (`set -euo pipefail`), `trap` | Vous savez écrire un script qui gère correctement le code de sortie et les échecs |
| 3. Pièges du word splitting et du globbing | 0004 | La liste des Bash Pitfalls, les pièges courants au-delà du quoting | Face à un script, vous savez nommer le cas limite précis sur lequel il casserait |
| 4. Portabilité | 0005 | POSIX `sh` contre idiomes propres à bash, quand chacun compte | Vous savez écrire du `sh` portable et signaler explicitement une fonctionnalité propre à bash |
| 5. `awk`/`sed` là où il le faut | 0006 | N'utiliser chacun que là où un script en a réellement besoin | Vous savez recourir à `awk`/`sed` pour un vrai besoin sans en abuser |
| 6. Savoir quand s'arrêter | 0007 | Reconnaître que le shell a quitté sa zone sans jugement | Vous savez dire pourquoi une tâche donnée relève désormais de `programming/python` |
| 7. Fondamentaux du shell | 0008 à 0009 | Variables, substitution de commande, structures de contrôle (`if`/`case`/boucles), fonctions, `local`, code de retour contre sortie | Vous savez écrire un script avec des variables, des substitutions de commande et des structures de contrôle, et organiser le travail répété en fonctions à la portée correcte |
| 8. Expansion de paramètres et tableaux | 0010 à 0011 | Valeur par défaut ou erreur si non défini (`${v:-}`, `${v:?}`), suppression (`${v%%}`), substitution, tableaux indexés et associatifs | Vous savez donner une valeur par défaut, valider et transformer une valeur en ligne, et stocker une liste ou une table sans l'encoder dans une chaîne |
| 9. Redirection et composition | 0012 à 0013 | Ordre des redirections, descripteurs de fichiers, here-docs, pourquoi une boucle `while` dans un pipe perd ses variables, substitution de processus | Vous savez rediriger les flux correctement et expliquer pourquoi une variable définie dans une boucle d'un pipe n'y survit pas |
| 10. Arguments et contrôle des jobs | 0014 à 0015 | `getopts`, une convention d'usage et d'aide, signaux, jobs en arrière-plan, `wait` | Vous savez analyser les options et arguments propres à un script, et gérer correctement le travail en arrière-plan et son propre arrêt |
| 11. Sûreté et outillage | 0016 à 0017 | `mktemp`, la surface `eval`/injection, ShellCheck, `shfmt`, tests avec bats/shunit2 | Vous savez créer des fichiers temporaires et des commandes dynamiques en toute sûreté, et utiliser l'analyse statique et les tests pour attraper ce que la relecture seule manquerait |

## Leçons

Suivez-les dans l'ordre.

| # | Leçon | Enseigne |
|---|---|---|
| [0001](lessons/0001-quoting.md) | Quoting | L'unique habitude qui évite la façon la plus courante dont les scripts shell cassent en production |
| [0002](lessons/0002-exit-status.md) | Code de sortie | Ce que rapporte réellement $?, pourquoi bash continue par défaut après une commande en échec, et la deuxième façon la plus courante dont un script casse en production |
| [0003](lessons/0003-strict-mode-and-trap.md) | Mode strict et trap | Ce que change réellement chaque option de set -euo pipefail, ses vraies lacunes, et l'usage de trap pour nettoyer de façon fiable quand un script échoue |
| [0004](lessons/0004-word-splitting-and-globbing-pitfalls.md) | Pièges du word splitting et du globbing | Les pièges courants au-delà d'un simple guillemet manquant, là où le quoting seul ne suffit pas à corriger |
| [0005](lessons/0005-portability.md) | Portabilité | Ce que garantit réellement POSIX sh, quelles fonctionnalités courantes de bash n'en font pas partie, et quand la différence compte vraiment |
| [0006](lessons/0006-awk-and-sed-where-needed.md) | awk et sed là où il le faut | Reconnaître la forme de tâche à laquelle conviennent respectivement sed et awk, et n'y recourir que lorsqu'un script en a réellement besoin, pas par habitude |
| [0007](lessons/0007-knowing-when-to-stop.md) | Savoir quand s'arrêter | Les signaux concrets indiquant qu'un script a quitté la zone sans jugement du shell, et pourquoi la tâche relève désormais plutôt d'un vrai langage |
| [0008](lessons/0008-variables-command-substitution-and-control-flow.md) | Variables, substitution de commande et structures de contrôle | Le vocabulaire propre au shell pour stocker une valeur, capturer la sortie d'une commande, et brancher ou boucler dessus |
| [0009](lessons/0009-functions-local-and-return-status-vs-output.md) | Fonctions, local, et code de retour contre sortie | Organiser le travail répété en une fonction, et la différence la plus marquée entre une fonction shell et une fonction de presque tous les autres langages |
| [0010](lessons/0010-parameter-expansion.md) | Expansion de paramètres | Donner une valeur par défaut, lever une erreur et retirer une partie d'une valeur en ligne, sans recourir à une commande séparée |
| [0011](lessons/0011-arrays.md) | Tableaux (indexés et associatifs) | Stocker plus d'une valeur sans encoder de structure dans une chaîne, et la forme de quoting qui garde chaque élément intact |
| [0012](lessons/0012-redirection-file-descriptors-and-here-docs.md) | Redirection, descripteurs de fichiers et here-docs | Envoyer précisément la sortie d'une commande ailleurs qu'à l'écran, et lui fournir un bloc d'entrée en ligne |
| [0013](lessons/0013-pipes-subshells-and-process-substitution.md) | Pipes, sous-shells et substitution de processus | Pourquoi une variable définie dans une boucle d'un pipe disparaît dès que le pipe se termine, et la correction propre à bash qui la conserve |
| [0014](lessons/0014-argument-parsing-with-getopts.md) | Analyse des arguments avec getopts et une convention d'usage | Analyser les options et arguments propres à un script avec la même discipline que celle avec laquelle il est censé analyser tout le reste |
| [0015](lessons/0015-signals-background-jobs-and-wait.md) | Signaux, jobs en arrière-plan et wait | Exécuter du travail en concurrence au sein d'un même script, et veiller à ce que l'arrêt du script ne laisse pas ce travail orphelin |
| [0016](lessons/0016-mktemp-safe-temp-files-and-the-eval-injection-surface.md) | mktemp, fichiers temporaires sûrs et la surface eval/injection | Créer un fichier temporaire impossible à prédire ou à détourner, et pourquoi eval transforme une entrée non fiable en code arbitraire |
| [0017](lessons/0017-shellcheck-shfmt-and-testing-a-script.md) | shellcheck, shfmt et tester un script | L'outil qui attrape la plupart des cassures silencieuses d'un script avant même son exécution, et comment tester le reste |

## Référence

- [Glossaire](GLOSSARY.md) : termes de référence pour ce sujet
- [Ressources](RESOURCES.md) : sources fiables
- [Quoting et pièges](reference/quoting-and-pitfalls.md) : la règle du quoting, là où elle mord, et les Bash Pitfalls qui survivent à un quoting soigneux
- [Code de sortie et gestion des erreurs](reference/exit-status-and-error-handling.md) : `$?`, les options de `set -euo pipefail` et leurs vraies exceptions, et `trap` pour un nettoyage garanti
- [Portabilité](reference/portability.md) : POSIX `sh` contre fonctionnalités propres à bash, la règle d'honnêteté du shebang, et quand le compromis en vaut la peine
- [awk, sed et savoir quand s'arrêter](reference/awk-sed-and-when-to-stop.md) : adapter l'outil à la forme de la tâche, et les signaux concrets indiquant qu'un script a dépassé le shell

## Comment cela fonctionne

Chaque leçon est courte et autonome. Les corrigés sont repliés : rappelez-vous d'abord, puis ouvrez-les. Les exercices en situation réelle comptent plus que la lecture, et les espacer dans le temps est justement le but. Tout ce qui reste flou à la fin d'une leçon mérite d'être suivi jusqu'à sa source primaire avant de passer à la suite.
