---
title: "34. Prompt caching e concorrência"
description: "Como o caching reduz o custo em tokens por tarefa e como a concorrência aumenta o throughput, e por que confundir os dois é um erro de orçamento"
type: lesson
---

# Lição 34. Prompt caching e concorrência

**Ligação com a missão:** Orçar o custo em tokens e a latência de um loop agêntico e dizer de qual parte do loop vem a amplificação.
**Fonte principal:** [Docs: "Prompt caching", Claude Platform Docs](https://platform.claude.com/docs/en/build-with-claude/prompt-caching)
**Pré-requisitos:** [Lição 33](0033-token-amplification-and-cost.md)

## Aquecimento

1. ▢ Da Lição 33, você aprendeu que as definições de ferramenta são reenviadas ao modelo a cada turno do loop, consumindo tokens mesmo que nunca mudem. Que parte do contexto é essa, e por que o caching ajudaria?

<details markdown="1"><summary>Verificação</summary>

As definições de ferramenta são um prefixo estável de toda mensagem ao modelo: não mudam no meio da execução. O caching ajuda porque um cache guarda esse prefixo estável depois da primeira requisição e o reutiliza nas requisições seguintes da mesma trajetória, cobrando apenas pelo conteúdo novo anexado a ele.

</details>

2. ▢ Da Lição 19, lembre: rodar três agentes em paralelo reduz o custo em tokens de resolver um problema em comparação com rodar um agente em série?

<details markdown="1"><summary>Verificação</summary>

Não. Rodar três agentes em paralelo aumenta o custo total em tokens porque cada agente paga seu custo completo de forma independente. O paralelismo reduz o tempo de relógio, mas não o custo em tokens. Cada agente paralelo ainda precisa ler a tarefa, rodar seu loop e transmitir sua transcrição ao modelo.

</details>

## Saiba isto

### Como o prompt caching funciona

O prompt caching é um mecanismo que guarda um prefixo estável de uma requisição depois da primeira chamada e o reutiliza nas chamadas seguintes sem cobrar o preço cheio por ele de novo. O cache é específico de uma sequência de requisições; requisições de usuários diferentes ou de execuções de agente diferentes não compartilham um cache.

Eis a mecânica:

1. Na primeira mensagem de uma trajetória, você envia uma requisição completa: system prompt, definições de ferramenta e a tarefa.
2. O modelo a processa normalmente e cobra o custo cheio em tokens.
3. A resposta inclui metadados: "Cached 4,000 tokens" (ou qualquer que tenha sido o prefixo estável).
4. Na segunda mensagem da mesma trajetória, você acrescenta conteúdo novo à requisição: talvez um resultado de ferramenta, a próxima instrução ou um turno de acompanhamento.
5. O modelo reutiliza o prefixo em cache (system prompt, ferramentas, tarefa) e cobra apenas pelo conteúdo recém-anexado.
6. Isso se repete: cada novo turno da mesma trajetória paga apenas pelo que mudou desde o turno anterior.

O cache tem um custo: o primeiro turno paga o preço cheio, e há uma pequena sobrecarga de cobrança pelas consultas e pelo armazenamento do cache. Mas, em uma trajetória longa, essa sobrecarga se justifica com facilidade. Se você tem 30 turnos e as definições de ferramenta somam 2.000 tokens, o cache economiza aproximadamente 2.000 * 28 = 56.000 tokens (as definições não são reenviadas nos turnos 2 a 29, então você economiza o custo delas 28 vezes).

### O que invalida um cache

Um cache só é útil se o prefixo é de fato estável. Várias coisas invalidam um cache em silêncio, o que importa para o design do harness:

**Reordenar as definições de ferramenta.** Se você serializa sua lista de ferramentas de forma diferente no turno 1 e no turno 2 (por exemplo, em ordem alfabética no turno 1, por frequência no turno 2), o prefixo não corresponde mais e o cache fica inválido. Um harness precisa sempre serializar as ferramentas na mesma ordem, a cada turno.

**Interpolar valores dinâmicos no system prompt.** Se o seu system prompt inclui um timestamp ("Current time: 2024-09-13"), um ID de usuário ou qualquer valor por chamada, esse valor muda entre turnos e o prefixo deixa de ser estável. O cache fica inválido em todo turno. Isso anula o caching por completo. Se você precisa de valores dinâmicos, ponha-os depois das ferramentas (na parte não cacheada da requisição).

**Editar mensagens anteriores.** Se um harness faz edição no lugar de mensagens antigas (em oposição a apenas anexar), o cache é invalidado a partir desse ponto de edição. A Lição 7 ensinou que a transcrição é o estado do agente; essa filosofia defende apenas anexar e nunca mexer em mensagens antigas. O prompt caching reforça isso: qualquer edição quebra o cache.

### O caching resolve o custo de "definições de ferramenta reenviadas a cada turno" da Lição 33

A documentação "Prompt caching", a fonte principal, observa que definições de ferramenta e system prompts são exatamente o tipo de conteúdo estável, grande e repetido para o qual o caching foi construído. Um harness de 10 ferramentas com 2.000 tokens de descrições de ferramenta agora custa esses 2.000 tokens apenas uma vez por trajetória, e não uma vez por turno. Em uma trajetória de 50 turnos, só isso economiza aproximadamente 98.000 tokens (as definições aparecem 50 vezes sem caching, 1 vez com caching, então 49 * 2.000 = 98.000 tokens economizados).

É por isso que a Lição 33 e a Lição 34 são pareadas: a Lição 33 identifica o desperdício, a Lição 34 nomeia a correção.

### Concorrência: uma alavanca separada e complementar

O prompt caching reduz o custo de qualquer execução individual de agente. A concorrência é uma questão separada: rodar várias instâncias de agente em paralelo.

A concorrência pode assumir várias formas:

- Rodar a mesma tarefa na mesma entrada com vários agentes em paralelo, para ver se produzem respostas diferentes (útil para tarefas em que existem várias soluções válidas).
- Rodar variações de uma tarefa em paralelo (fan-out da Lição 19), em que cada agente resolve uma subtarefa.
- Rodar várias tarefas independentes de usuários em paralelo (um sistema que atende muitos usuários, cada um com sua própria instância de agente).

Em cada caso, a concorrência aumenta o throughput: mais tarefas são concluídas por unidade de tempo de relógio. Mas a concorrência NÃO reduz o custo em tokens de nenhuma tarefa individual. Se você roda três agentes em paralelo e cada um custa 100.000 tokens, o total é 300.000 tokens, e não 100.000 dividido por 3. O paralelismo troca tempo por tokens.

### O erro: confundir caching e concorrência

Um erro comum de orçamento é presumir que rodar vários agentes em paralelo, de algum modo, torna cada um mais barato em tokens. Não torna. Eis a confusão:

- Correto: O caching reduz o custo em tokens da longa trajetória de um único agente ao evitar reenviar prefixos estáveis.
- Correto: A concorrência reduz o tempo de relógio ao rodar agentes em paralelo.
- Incorreto: "Rodamos os agentes de forma concorrente, então o custo em tokens por agente é menor."

A concorrência reduz tempo, e não tokens. Rodar agentes mais depressa (em paralelo) não os torna mais baratos (em tokens). Se você precisa reduzir o custo e já tem caching, as alavancas são:

- Melhor planejamento (Lição 16) para reduzir o número de turnos.
- Melhor recuperação (Lição 11) para reduzir o tamanho da transcrição.
- Menos workers (Lição 19) para reduzir a duplicação multiagente.
- Falhar mais depressa (o diagnóstico da Lição 29) para reduzir tentativas desperdiçadas.

### Orçamento de tokens: duas perguntas

Ao projetar um sistema agêntico, faça duas perguntas separadas:

1. **Custo por tarefa concluída:** Quantos tokens um agente precisará para resolver uma tarefa de forma confiável? É aqui que o caching ajuda, o planejamento ajuda e a reflexão custa.
2. **Throughput:** Quantas tarefas você precisa concluir por segundo ou por minuto? É aqui que a concorrência ajuda. Se você precisa de 10 tarefas por segundo e cada tarefa leva 1 segundo para ser concluída em série, você precisa de pelo menos 10 agentes rodando em paralelo.

Confundir essas perguntas leva a decisões erradas. Se você está tentando reduzir o custo por tarefa, adicionar mais agentes concorrentes não ajuda. Se você está tentando aumentar o throughput e tem um prazo, adicionar concorrência é a alavanca certa (mas você paga em tokens totais: 10 agentes * custo por tarefa = orçamento total).

## Prática

1. ▢ O system prompt e as definições de ferramenta do seu agente somam 5.000 tokens. O agente roda por 30 turnos em uma única tarefa. Sem prompt caching, quantas vezes esses 5.000 tokens são enviados ao modelo? Com caching, quantas vezes?

<details markdown="1"><summary>Verificação</summary>

Sem caching: 30 vezes (uma por turno), para um total de 150.000 tokens de sobrecarga de definições. Com caching: uma vez no primeiro turno, depois reutilizados em todos os turnos seguintes, então efetivamente uma vez. (Mais precisamente, há uma pequena sobrecarga para recuperar o cache em cada turno, mas os 5.000 tokens completos não são retransmitidos.) O caching economiza aproximadamente 145.000 tokens neste caso.

</details>

2. ▢ Você está implementando prompt caching no seu harness. A lista de ferramentas é gerada dinamicamente: no turno 1, o agente tem acesso às ferramentas A, B, C; no turno 3, o harness adiciona a ferramenta D. As ferramentas são serializadas na ordem em que são geradas (A, B, C no turno 1; A, B, C, D no turno 3). O cache do turno 1 ainda será válido no turno 3? Por que sim ou por que não?

<details markdown="1"><summary>Dica</summary>

O que mudou entre a requisição do turno 1 e a do turno 3? Essa mudança faz parte do prefixo em cache, ou fica depois dele?

</details>

<details markdown="1"><summary>Verificação</summary>

Não, o cache é inválido. No turno 1, o prefixo contém "tools: A, B, C". No turno 3, o prefixo contém "tools: A, B, C, D". Os prefixos não correspondem, então o cache não se aplica. O harness precisa enviar as definições completas de novo. É por isso que a adição dinâmica de ferramentas (adicionar uma ferramenta no meio da execução com base nas decisões do agente) quebra o caching. Um harness que quer caching deve ou se comprometer com um conjunto fixo de ferramentas de antemão, ou aceitar que adicionar ferramentas no meio da execução invalida o cache.

</details>

3. ▢ Você está projetando o system prompt de um agente com cache. O prompt inclui "Current date: 2024-09-13" para situar o modelo no tempo. Por que isso é um problema de caching?

    - a) A data não é relevante para o modelo e deveria ser removida.
    - b) A data muda todo dia, então o prefixo em cache ficaria obsoleto depois de um dia.
    - c) A data é um valor dinâmico que muda entre execuções, o que invalida o cache a cada execução porque o prefixo deixa de corresponder.
    - d) Datas não podem ser guardadas em cache por nenhum sistema.

<details markdown="1"><summary>Verificação</summary>

**c)** O system prompt faz parte do prefixo em cache. Se você inclui uma data fixa no código que é diferente na execução 1 e na execução 2, o prefixo em cache da execução 1 não corresponde à requisição da execução 2, então o cache é inútil. A solução é excluir a data do prefixo em cache (pô-la depois das ferramentas, no conteúdo por turno), ou usar uma data fixa para todas as execuções se a data não for de fato crítica. Esse é um erro comum: incluir metadados por execução na parte cacheada anula o caching.

</details>

4. ▢ Você tem duas opções para escalar o seu sistema de agentes: a Opção A é otimizar o custo por tarefa de um agente via caching e planejamento, reduzindo-o de 100.000 tokens para 60.000 tokens. A Opção B é rodar dez agentes em paralelo sem otimização, cada um ainda custando 100.000 tokens. Se você precisa concluir 10 tarefas e tem computação ilimitada, qual opção minimiza o custo em tokens?

<details markdown="1"><summary>Verificação</summary>

Opção A: 10 tarefas \* 60.000 tokens por tarefa = 600.000 tokens no total. Opção B: 10 tarefas \* 100.000 tokens por tarefa = 1.000.000 de tokens no total, mesmo rodando em paralelo. A concorrência aumenta a velocidade (a Opção B termina no tempo de uma tarefa, enquanto a Opção A termina em 10 vezes essa duração, em série), mas não o custo. A Opção A é mais barata em tokens. Se você precisa concluir 10 tarefas o mais depressa possível, combinaria as duas: otimizar cada agente para 60.000 tokens (a abordagem da Opção A) e rodar 10 agentes otimizados em paralelo, para um total de 600.000 tokens e o menor tempo de relógio.

</details>

## Prática no mundo real

- [ ] Olhe um harness de agente que você escreveu ou revisou. Encontre onde o system prompt e as definições de ferramenta são serializados. Verifique que são sempre serializados na mesma ordem e que nenhum valor dinâmico (timestamps, IDs de usuário, metadados específicos da execução) é interpolado nessa seção. Se forem, anote como isso quebra o caching.
- [ ] Estime a economia de tokens do prompt caching para uma tarefa que você conhece. Chute: tamanho do system prompt e das definições de ferramenta, número de turnos, tokens por turno. Calcule quantos tokens são economizados por não reenviar as definições. A economia vale a complexidade de implementar o caching?
- [ ] Amanhã: Projete uma tarefa que se beneficia de concorrência (seja vários usuários, várias subtarefas independentes ou várias tentativas da mesma tarefa). Estime o orçamento total de tokens se você roda os agentes em série (um de cada vez) contra em paralelo. Mostre que os dois orçamentos são o mesmo e explique o que você ganha e perde com cada abordagem.

## Para ir além

- [Docs: "Prompt caching", Claude Platform Docs](https://platform.claude.com/docs/en/build-with-claude/prompt-caching)
- [Recursos](../RESOURCES.md)

---

Não ficou claro? Releia a fonte principal no topo, já que esta lição a comprime e é na compressão que o entendimento escapa. Consulte o [glossário](../GLOSSARY.md) para qualquer termo que pareceu escorregadio.

Se o problema é a lição em si, e não o material, isso é um defeito: [abra uma issue](https://github.com/TokenCemetery/teach/issues).
