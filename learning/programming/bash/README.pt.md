---
title: Bash
description: "Escreva shell que sobrevive à produção: quoting, exit status, os modos de falha e saber quando parar e usar uma linguagem de verdade"
type: topic
---

# Aprendizado: Bash

Seja capaz de escrever e manter scripts de shell para pipelines de CI, deployment e ferramentas operacionais que não quebrem em silêncio diante de uma entrada ruim ou de uma variável não definida, e de reconhecer quando um script já ultrapassou o shell e deveria estar em uma linguagem de verdade.

**Última lição:** [17. shellcheck, shfmt e testando um script](lessons/0017-shellcheck-shfmt-and-testing-a-script.md)

## O sucesso se parece com isto

- Escrever um script de CI/deployment ou um utilitário operacional que trate corretamente quoting, exit status e os modos de falha comuns, e explicar por que cada escolha foi necessária.
- Dado um script de shell, nomear a forma específica pela qual ele quebraria em um caso de borda (expansão sem aspas, variável não definida, exit status de um comando ignorado).
- Reconhecer quando um script ultrapassou a zona do shell em que não há decisões de julgamento e dizer por que o trabalho agora pertence a `programming/python`.

## Restrições

- Não exige experiência prévia com scripts de shell.
- Escrito visando a portabilidade para `sh` POSIX em vez de idiomas exclusivos do bash, embora o bash seja a casa do tópico; um recurso exclusivo do bash é sinalizado como tal quando usado.
- Toca em `awk`/`sed` apenas onde um script realmente precisa deles, e não como tópicos próprios.

## Fora do escopo

- Tudo o que vem depois do ponto em que um script deveria ter deixado de ser shell: veja [`programming/python`](../../programming/python/) para essa fronteira.

## O arco

Onze etapas, do quoting até shellcheck, shfmt e testes. Uma etapa leva várias lições e as fronteiras são flexíveis; o que torna uma etapa concluída é a capacidade, não a contagem de lições.

| Etapa | Lições | Cobre | Concluída quando |
|---|---|---|---|
| 1. Quoting | 0001 | O único hábito que evita a forma mais comum pela qual scripts de shell quebram em produção | Consegue usar aspas corretamente e explicar por que uma expansão sem aspas quebra |
| 2. Exit status e tratamento de erros | 0002 a 0003 | `$?`, o strict mode não oficial (`set -euo pipefail`), `trap` | Consegue escrever um script que trata exit status e falhas corretamente |
| 3. Armadilhas de word splitting e globbing | 0004 | A lista Bash Pitfalls, as armadilhas comuns além do quoting | Dado um script, consegue nomear o caso de borda específico em que ele quebraria |
| 4. Portabilidade | 0005 | `sh` POSIX contra idiomas exclusivos do bash, quando cada um importa | Consegue escrever `sh` portável e sinalizar explicitamente um recurso exclusivo do bash |
| 5. `awk`/`sed` onde necessário | 0006 | Usar cada um apenas onde um script realmente precisa dele | Consegue recorrer a `awk`/`sed` para uma necessidade real sem abusar deles |
| 6. Saber quando parar | 0007 | Reconhecer que o shell ultrapassou sua zona sem decisões de julgamento | Consegue dizer por que um dado trabalho agora pertence a `programming/python` |
| 7. Fundamentos do shell | 0008 a 0009 | Variáveis, substituição de comando, fluxo de controle (`if`/`case`/loops), funções, `local`, status de retorno contra saída | Consegue escrever um script usando variáveis, substituição de comando e fluxo de controle, e organizar trabalho repetido em funções com escopo correto |
| 8. Expansão de parâmetros e arrays | 0010 a 0011 | Valor padrão/erro para variável não definida (`${v:-}`, `${v:?}`), remoção (`${v%%}`), substituição, arrays indexados e associativos | Consegue definir um padrão, validar e transformar um valor inline, e guardar uma lista ou um mapa sem codificá-lo em uma string |
| 9. Redirecionamento e composição | 0012 a 0013 | Ordem dos redirecionamentos, file descriptors, here-docs, por que um loop `while` em pipe perde suas variáveis, process substitution | Consegue redirecionar streams corretamente e explicar por que uma variável definida dentro de um loop em pipe não sobrevive a ele |
| 10. Argumentos e controle de jobs | 0014 a 0015 | `getopts`, uma convenção de uso/ajuda, sinais, jobs em background, `wait` | Consegue fazer o parsing das flags e dos argumentos do próprio script, e gerenciar corretamente o trabalho em background e o próprio encerramento |
| 11. Segurança e ferramentas | 0016 a 0017 | `mktemp`, a superfície de `eval`/injeção, ShellCheck, `shfmt`, testes com bats/shunit2 | Consegue criar arquivos temporários e comandos dinâmicos com segurança, e usar análise estática e testes para pegar o que só a revisão deixaria passar |

## Lições

Siga estas na ordem.

| # | Lição | Ensina |
|---|---|---|
| [0001](lessons/0001-quoting.md) | Quoting | O único hábito que evita a forma mais comum pela qual scripts de shell quebram em produção |
| [0002](lessons/0002-exit-status.md) | Exit status | O que $? realmente reporta, por que o bash continua rodando por padrão depois de um comando que falhou, e a segunda forma mais comum pela qual um script quebra em produção |
| [0003](lessons/0003-strict-mode-and-trap.md) | Strict mode e trap | O que cada flag de set -euo pipefail realmente muda, suas lacunas reais, e usar trap para limpar de forma confiável quando um script falha |
| [0004](lessons/0004-word-splitting-and-globbing-pitfalls.md) | Armadilhas de word splitting e globbing | Armadilhas comuns além de uma simples aspa faltando, em que o quoting sozinho não é a correção inteira |
| [0005](lessons/0005-portability.md) | Portabilidade | O que o sh POSIX realmente garante, quais recursos comuns do bash não fazem parte dele e quando a diferença realmente importa |
| [0006](lessons/0006-awk-and-sed-where-needed.md) | awk e sed onde necessário | Reconhecer o formato de tarefa em que sed e awk se encaixam cada um, e recorrer a um deles só quando um script realmente precisa, e não por hábito |
| [0007](lessons/0007-knowing-when-to-stop.md) | Saber quando parar | Os sinais concretos de que um script ultrapassou a zona do shell sem decisões de julgamento, e por que o trabalho agora pertence a uma linguagem de verdade |
| [0008](lessons/0008-variables-command-substitution-and-control-flow.md) | Variáveis, substituição de comando e fluxo de controle | O vocabulário próprio do shell para guardar um valor, capturar a saída de um comando e ramificar ou iterar sobre ela |
| [0009](lessons/0009-functions-local-and-return-status-vs-output.md) | Funções, local e status de retorno contra saída | Organizar trabalho repetido em uma função, e a diferença mais marcante entre uma função de shell e uma função em quase qualquer outra linguagem |
| [0010](lessons/0010-parameter-expansion.md) | Expansão de parâmetros | Definir um padrão, gerar um erro e remover partes de um valor inline, sem recorrer a um comando separado |
| [0011](lessons/0011-arrays.md) | Arrays (indexados e associativos) | Guardar mais de um valor sem codificar estrutura em uma string, e a única forma de quoting que mantém cada elemento intacto |
| [0012](lessons/0012-redirection-file-descriptors-and-here-docs.md) | Redirecionamento, file descriptors e here-docs | Enviar a saída de um comando para outro lugar que não a tela, com precisão, e alimentá-lo com um bloco de entrada inline |
| [0013](lessons/0013-pipes-subshells-and-process-substitution.md) | Pipes, subshells e process substitution | Por que uma variável definida dentro de um loop em pipe desaparece no momento em que o pipe termina, e a correção exclusiva do bash que a preserva |
| [0014](lessons/0014-argument-parsing-with-getopts.md) | Parsing de argumentos com getopts e uma convenção de uso | Fazer o parsing das flags e dos argumentos do próprio script com a mesma disciplina com que ele deveria fazer o parsing de todo o resto |
| [0015](lessons/0015-signals-background-jobs-and-wait.md) | Sinais, jobs em background e wait | Rodar trabalho concorrente dentro de um único script, e garantir que o próprio encerramento do script não o deixe órfão |
| [0016](lessons/0016-mktemp-safe-temp-files-and-the-eval-injection-surface.md) | mktemp, arquivos temporários seguros e a superfície de eval/injeção | Criar um arquivo temporário que não possa ser previsto nem sequestrado, e por que eval transforma entrada não confiável em código arbitrário |
| [0017](lessons/0017-shellcheck-shfmt-and-testing-a-script.md) | shellcheck, shfmt e testando um script | A ferramenta que pega a maior parte das quebras silenciosas de um script antes mesmo de ele rodar, e como testar o resto |

## Referência

- [Glossário](GLOSSARY.md): termos canônicos deste tópico
- [Recursos](RESOURCES.md): fontes confiáveis
- [Quoting e armadilhas](reference/quoting-and-pitfalls.md): a regra do quoting, onde ela morde e as Bash Pitfalls que sobrevivem a um quoting cuidadoso
- [Exit status e tratamento de erros](reference/exit-status-and-error-handling.md): `$?`, as flags de `set -euo pipefail` e suas exceções reais, e `trap` para limpeza garantida
- [Portabilidade](reference/portability.md): `sh` POSIX contra recursos exclusivos do bash, a regra da honestidade do shebang e quando o trade-off vale a pena
- [awk, sed e saber quando parar](reference/awk-sed-and-when-to-stop.md): casar a ferramenta com o formato da tarefa, e os sinais concretos de que um script ultrapassou o shell

## Como isto funciona

Cada lição é curta e autocontida. Os gabaritos ficam recolhidos: primeiro lembre, depois abra. A prática no mundo real importa mais do que a leitura, e espaçá-la é o ponto. Tudo o que ainda estiver confuso no fim de uma lição vale ser perseguido até a fonte primária antes de seguir adiante.
