---
title: "33. Amplificação de tokens e custo por tarefa concluída"
description: "Por que sistemas agênticos consomem muito mais tokens por tarefa concluída do que um único prompt consumiria, e como orçar isso"
type: lesson
---

# Lição 33. Amplificação de tokens e custo por tarefa concluída

**Ligação com a missão:** Orçar o custo em tokens e a latência de um loop agêntico e dizer de qual parte do loop vem a amplificação.
**Fonte principal:** [Article: "How We Built Our Multi-Agent Research System", Anthropic Engineering](https://www.anthropic.com/engineering/multi-agent-research-system)
**Pré-requisitos:** [Lição 32](0032-least-privilege-and-the-confused-deputy.md), [Trajetória](../GLOSSARY.md)

## Aquecimento

1. ▢ Na Lição 10, você aprendeu que a transcrição cresce a cada turno em que o loop do agente roda. Por que isso cria um custo que se acumula ao longo de uma trajetória?

<details markdown="1"><summary>Verificação</summary>

A transcrição inteira é enviada ao modelo a cada turno do loop. Uma trajetória de 30 turnos significa que o conteúdo do primeiro turno é enviado ao modelo 30 vezes, o do segundo turno 29 vezes, e assim por diante. O custo em tokens de uma trajetória longa não é apenas a soma dos turnos; é a soma de todas as retransmissões repetidas dos turnos antigos.

</details>

2. ▢ Da Lição 19, lembre: quando um orquestrador dispara três workers em paralelo, quantos loops de agente rodam no total em comparação com um único agente resolvendo o mesmo problema?

<details markdown="1"><summary>Verificação</summary>

Três loops de agente separados rodam, um dentro de cada worker, mais o próprio loop do orquestrador. Então o total é de pelo menos três execuções completas de agente mais o custo do orquestrador, enquanto um único agente resolvendo o mesmo problema é uma execução. O custo em tokens é multiplicado, e não dividido, pelo paralelismo.

</details>

## Saiba isto

### As quatro fontes de amplificação de tokens

Um sistema agêntico consome muito mais tokens por tarefa concluída do que um único prompt bem informado consumiria. Isso acontece por causa de quatro fatores que se acumulam. Já nomeamos três deles em lições anteriores; esta lição os reúne e acrescenta o quarto.

### Fonte 1: recrescimento da transcrição (da Lição 10)

Cada turno do loop acrescenta algo à transcrição. No turno seguinte, a transcrição inteira é reenviada ao modelo. Isso significa que uma trajetória de 50 turnos paga o custo em tokens do turno 1 cinquenta vezes, o do turno 2 quarenta e nove vezes, e assim por diante. O total é aproximadamente a metade da soma: 1 + 2 + 3 + ... + 50 = 1.275, então cada turno é pago, em média, 25,5 vezes. Um prompt simples que você envia uma vez custa X tokens. O mesmo problema resolvido por um agente de 50 turnos custa não 50X (se cada turno fosse independente), mas algo mais próximo de 1.275X em transmissão bruta de tokens, mesmo que cada turno individual seja mais barato do que X porque o modelo está focado de forma estreita.

O artigo "Building Effective Agents", da Anthropic, observa que esse recrescimento é o maior multiplicador de custo isolado em agentes de longa duração, e é por isso que a Lição 11 (compactação e recuperação) existe como defesa contra ele.

### Fonte 2: duplicação multiagente (da Lição 19)

Se você decompõe um problema em subtarefas e roda três workers em paralelo (fan-out da Lição 18), você paga o custo completo de recrescimento da transcrição não uma, mas três vezes. Cada worker tem sua própria trajetória de 50 turnos, então cada um paga 1.275X. O orquestrador também roda seu próprio loop. O custo de coordenação multiplica o custo total em tokens. Se o seu agente único teria custado 50.000 tokens, três workers com custo um pouco menor cada um podem somar 130.000 tokens ou mais.

### Fonte 3: reflexão e retries (da Lição 17)

Se uma primeira tentativa de uma tarefa falha e o harness gera uma reflexão e depois roda o agente de novo, você agora tem duas trajetórias completas em vez de uma. Uma tarefa que leva três tentativas (uma falha, uma reflexão, um sucesso) custa aproximadamente três vezes o que uma única tentativa bem-sucedida custaria, porque cada tentativa é uma execução completa de agente com seu próprio recrescimento de transcrição. A Lição 17 ensina que a reflexão só vale esse custo quando o sinal de falha é claro e uma segunda tentativa provavelmente terá sucesso.

### Fonte 4: definições de ferramenta reenviadas a cada turno (novidade desta lição)

O system prompt e as definições de ferramenta fazem parte do contexto enviado ao modelo a cada turno do loop. As definições de ferramenta costumam ser grandes: cada ferramenta tem um nome, uma descrição legível por pessoas (do trabalho de nomeação da Lição 8), tipos de parâmetros, restrições e exemplos. Se você tem dez ferramentas com 200 tokens de descrição cada, são 2.000 tokens de definições de ferramenta. Em uma trajetória de 50 turnos, são 2.000 * 50 = 100.000 tokens gastos reenviando as mesmas definições de ferramenta, mesmo que elas nunca tenham mudado no meio da execução.

Esse custo é distinto do recrescimento da transcrição (Fonte 1) porque as definições de ferramenta não mudam; são um prefixo estável e repetido. Esse é exatamente o problema que a Lição 34 (prompt caching) trata.

### A unidade certa para orçar: custo por tarefa concluída

A maioria das discussões de custo foca em "custo por chamada de API" ou "custo por invocação do modelo". Mas a unidade certa para um sistema agêntico é "custo por tarefa concluída", que significa a soma completa de todas as tentativas, todos os retries, todos os workers, todos os turnos, até a tarefa estar pronta.

Uma tarefa que um único prompt poderia resolver em 5.000 tokens pode custar 50.000 tokens ou mais em um sistema agêntico se:

- O problema leva 20 turnos para ser resolvido (multiplicador de recrescimento: ~200x sobre o custo de um único turno)
- A primeira tentativa falha e um retry baseado em reflexão tem sucesso (multiplique por 2)
- A tarefa é dividida em três workers paralelos (multiplique por 3)
- As definições de ferramenta são grandes e reenviadas a cada turno (acrescente 10.000 tokens de desperdício)

A conta é aproximada, mas o princípio é real: 5.000 tokens-base podem virar de 50.000 a 150.000 tokens na prática, porque você não está pagando por uma chamada; está pagando pela conclusão de uma tarefa, que envolve muitas chamadas, muitas idas e voltas e muitos contextos repetidos.

### Por que "custo por tarefa concluída" muda suas decisões de design

Quando você pensa em termos de custo por chamada de API, um agente de longa duração parece caro pelo mero número de chamadas. Quando você pensa em termos de custo por tarefa concluída, a pergunta muda: um sistema multiagente resolve o problema mais depressa em tempo de relógio ou de forma mais confiável, de um jeito que justifique o multiplicador de tokens? A reflexão reduz o número de tarefas que falham, de um jeito que justifique o custo do retry? A decomposição simplifica o problema o bastante para que cada worker use menos tokens por tarefa do que o agente único teria usado?

Essas são as perguntas reais de trade-off. O orçamento por tarefa torna o trade-off visível.

### Exemplo ilustrativo: depurando uma falha de código

Suponha que a sua tarefa seja depurar um teste que falha. Uma pessoa bem informada poderia escrever um prompt: "Aqui está o teste, aqui está a saída do erro. Encontre o bug." Esse prompt e a resposta poderiam custar 10.000 tokens no total.

Agora suponha que você construa um loop de agente em vez disso:

- O agente lê o teste (1.000 tokens), lê o código (2.000 tokens), raciocina sobre o erro (500 tokens) = 3.500 tokens no turno 1. Reenviar esses 3.500 tokens mais as definições de ferramenta (2.000 tokens) no turno 2 = 5.500 tokens. Depois de 10 turnos depurando, você gastou aproximadamente 3.500 \* 10 + (definições de ferramenta \* 10) = 55.000 tokens, porque cada turno reenvia o teste, o código e as definições de ferramenta.
- A primeira tentativa do agente chuta a causa raiz errada. O harness gera uma reflexão e roda o agente de novo. Agora você tem duas execuções completas de 10 turnos, então aproximadamente 110.000 tokens, e não 55.000.
- A segunda tentativa tem sucesso.

Custo por tarefa concluída: 110.000 tokens. Custo por chamada de API bem-sucedida: 5.500 tokens (apenas a última chamada bem-sucedida). Esses números contam histórias diferentes. Orçar por tarefa concluída é mais honesto.

A correção não é evitar agentes; a correção é usar o prompt caching da Lição 34 para evitar reenviar as definições de ferramenta, projetar o planejamento da Lição 16 para reduzir o número de turnos e usar a reflexão da Lição 17 apenas quando os sinais de falha são claros.

## Prática

1. ▢ Um prompt de um único turno a um modelo custa 5.000 tokens e resolve um problema perfeitamente. Um loop de agente no mesmo problema leva 25 turnos, e o custo de recrescimento da transcrição faz com que cada token dos primeiros turnos seja pago, em média, cerca de 20 vezes. Aproximadamente quantos tokens o loop do agente custa no total?

<details markdown="1"><summary>Verificação</summary>

Aproximadamente 5.000 * 20 = 100.000 tokens. O multiplicador de recrescimento é o fator mais importante. (Esta é uma estimativa ilustrativa; o número exato depende de como os tokens se distribuem pelos turnos, mas a ordem de grandeza está certa.)

</details>

2. ▢ Você está construindo um agente que resume artigos de pesquisa. As definições de ferramenta do agente somam 3.000 tokens. Em uma única execução, o agente examina 10 artigos e produz 10 resumos, levando 40 turnos no total. As definições de ferramenta nunca mudam durante a execução. Quantos tokens são gastos reenviando as definições de ferramenta, e por que esse desperdício é tratável na Lição 34?

<details markdown="1"><summary>Dica</summary>

Conte quantas vezes as definições de ferramenta são enviadas ao modelo. Depois pense em que parte do contexto é estável e nunca muda no meio da execução.

</details>

<details markdown="1"><summary>Verificação</summary>

As definições de ferramenta são enviadas 40 vezes (uma por turno), então 3.000 * 40 = 120.000 tokens gastos reenviando exatamente as mesmas definições. Isso é desperdício porque as definições nunca mudam; são um prefixo estável. A Lição 34 ensina prompt caching, que guarda em cache exatamente esse tipo de prefixo estável e o cobra uma vez só, e não 40 vezes.

</details>

3. ▢ Uma tarefa exige três tentativas. A primeira tentativa falha, uma reflexão é gerada, a segunda tentativa falha, outra reflexão é gerada e a terceira tentativa tem sucesso. Cada tentativa é uma execução completa de agente de 15 turnos. O orquestrador que coordena as três tentativas custa 5 turnos. Aproximadamente quantos turnos tem a trajetória no total?

    - a) 15 turnos (apenas a tentativa bem-sucedida conta)
    - b) 35 turnos (15 + 15 + 5)
    - c) 50 turnos (15 + 15 + 15 + 5)
    - d) 150 turnos (as três tentativas vezes a sobrecarga do orquestrador)

<details markdown="1"><summary>Verificação</summary>

**c)** As três tentativas rodam até o fim, então 15 + 15 + 15 = 45 turnos, mais 5 turnos de orquestração = 50 turnos. A opção a está errada porque as falhas também consomem turnos completos. A opção b ignora a segunda tentativa que falhou. A opção d erra a conta ao multiplicar em vez de somar. A trajetória inclui todos os turnos de todas as tentativas, e não apenas os da bem-sucedida.

</details>

4. ▢ Você está decidindo se usa um único agente ou três workers em fan-out para uma tarefa de pesquisa. O agente único levaria 60 turnos e custaria aproximadamente 100.000 tokens. Cada worker levaria 25 turnos e custaria aproximadamente 35.000 tokens, e o orquestrador leva 10 turnos e custa 3.000 tokens. Qual é o custo total em tokens do sistema multiagente, e ele é mais barato do que o agente único?

<details markdown="1"><summary>Verificação</summary>

Total: (35.000 * 3) + 3.000 = 108.000 tokens. O sistema multiagente é, na verdade, um pouco mais caro em tokens (108.000 contra 100.000), embora cada worker seja mais eficiente. Esse é o custo de coordenação da Lição 19. O sistema multiagente vence em tempo de relógio (os três workers rodam em paralelo, então o worker mais lento determina o tempo, e não a soma), e não em tokens. Isso mostra por que o orçamento por tarefa é importante: se você precisa de velocidade, o multiagente vence; se você precisa economizar tokens, o agente único vence.

</details>

## Prática no mundo real

- [ ] Pegue uma tarefa que você fez com um agente (ou uma trajetória que você viu). Percorra uma iteração do loop desse agente e conte os tokens: tamanho da transcrição, tamanho das definições de ferramenta, tamanho da saída do modelo. Multiplique pelo número de turnos. Agora estime quanto um único prompt bem informado ao modelo teria custado e compare os dois números. Registre o multiplicador.
- [ ] Projete uma pequena tarefa de agente (algo que você poderia rodar você mesmo). Estime o custo por tarefa concluída chutando: número de turnos necessários, número de retries, quaisquer workers em fan-out. Some o orçamento completo usando a fórmula (transcript_regrowth_factor) \* (number_of_attempts) \* (number_of_workers) \* (tokens_per_turn).
- [ ] Amanhã: Encontre ou gere a trajetória de uma execução de agente (pelo menos 10 turnos). Calcule o custo por tarefa em tokens somando todos os custos em tokens de todos os turnos e todas as tentativas. Depois encontre o custo por chamada de API bem-sucedida (apenas o turno final bem-sucedido). Anote quanto maior é o custo por tarefa do que o custo por chamada bem-sucedida e explique por que a diferença importa para o orçamento.

## Para ir além

- [Article: "How We Built Our Multi-Agent Research System", Anthropic Engineering](https://www.anthropic.com/engineering/multi-agent-research-system)
- [Recursos](../RESOURCES.md)

---

Não ficou claro? Releia a fonte principal no topo, já que esta lição a comprime e é na compressão que o entendimento escapa. Consulte o [glossário](../GLOSSARY.md) para qualquer termo que pareceu escorregadio.

Se o problema é a lição em si, e não o material, isso é um defeito: [abra uma issue](https://github.com/TokenCemetery/teach/issues).
