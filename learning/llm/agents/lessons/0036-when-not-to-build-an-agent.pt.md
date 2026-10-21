---
title: "36. Quando não construir um agente"
description: "O julgamento para decidir se uma tarefa realmente precisa de um agente e a disciplina de dizer não quando ele não vale o custo"
type: lesson
---

# Lição 36. Quando não construir um agente

**Ligação com a missão:** Construir o julgamento para decidir se uma dada tarefa precisa mesmo de um agente em vez de um workflow fixo, e defender essa decisão contra a pressão organizacional e o fascínio das soluções em forma de agente.
**Fonte principal:** [Article: "Building Effective Agents", Anthropic Engineering](https://www.anthropic.com/engineering/building-effective-agents)
**Pré-requisitos:** [Lição 35](0035-durability-and-what-frameworks-buy.md), [Espectro de autonomia](../GLOSSARY.md)

## Aquecimento

1. ▢ Lembre da Lição 2: qual é a diferença que define um workflow e um agente em termos de fluxo de controle?

<details markdown="1"><summary>Verificação</summary>

Um workflow tem um caminho que o desenvolvedor fixou de antemão; todos os ramos e sequências são ligados pelo desenvolvedor. Um agente tem o fluxo de controle decidido em tempo de execução pelo modelo, inclusive se continua ou para.

</details>

2. ▢ Lembre da Lição 2: no espectro de autonomia, que teste concreto você pode aplicar para decidir se o número de ramos de uma tarefa é de fato enumerável?

<details markdown="1"><summary>Verificação</summary>

Se você consegue listar todos os caminhos distintos de que um workflow precisaria para cobrir a tarefa, o número de ramos é enumerável e um workflow pode bastar. Se novos caminhos chegam mais depressa do que você consegue ligá-los, ou se o caminho certo genuinamente depende de informação disponível apenas no meio da tarefa, o número de ramos é efetivamente ilimitado e um agente é mais defensável.

</details>

## Saiba isto

### Por que a decisão é mais difícil do que a Lição 2 fez parecer

A Lição 2 ensinou o espectro de autonomia como uma escolha técnica limpa: o formato da tarefa é conhecido ou desconhecido, enumerável ou ilimitado? Na prática, essa escolha fica sob pressão real.

Um gerente de produto viu uma demo convincente de um agente resolvendo um problema complexo e pergunta: "Podemos construir isso para o nosso produto?" Uma organização se sente atrasada em IA e quer "adicionar agentes" à sua plataforma. Um stakeholder aponta uma tarefa e diz "isto parece digno de um agente", sem checar se a alternativa mais simples foi de fato tentada. Um workflow que resolve o mesmo problema é menos empolgante de apresentar, mesmo quando o workflow é a melhor decisão de engenharia.

O papel desta lição não é reensinar o arcabouço da Lição 2; o arcabouço está certo. O papel é nomear por que aplicá-lo corretamente é uma decisão de julgamento sob pressão e dar a você sinais de alerta concretos que indicam que um agente não se justifica, cada um ligado a uma lição anterior específica, para que você reconheça o padrão quando o vir em uma proposta ou em uma revisão de arquitetura.

### Sinal de alerta 1: Ninguém tentou antes o workflow mais simples

O sinal de alerta mais forte é este: um stakeholder ou uma proposta diz que um agente é necessário, mas ninguém de fato construiu a alternativa em workflow para testar essa afirmação.

A Lição 2 defende cada escolha nomeando o que a opção rejeitada teria custado. Essa defesa só funciona se você de fato testou a opção rejeitada. Se uma proposta afirma "um agente é necessário" sem mostrar uma tentativa de workflow e explicar por que o workflow falhou, a afirmação não foi testada contra a alternativa. Pedem a você que aceite um aumento de complexidade sem evidência de que a complexidade é necessária.

Como isso se parece na prática: uma proposta diz "Precisamos de um agente para tratar estes tickets de suporte ao cliente porque eles se ramificam em quarenta categorias distintas." Sem uma tentativa de workflow, você não sabe se quarenta categorias é de fato demais para ligar, ou se o autor da proposta apenas ainda não tentou. Depois de construir um roteador de workflow e testá-lo em tickets reais, você pode descobrir que quarenta categorias é administrável, ou pode descobrir que a acurácia do workflow sofre porque um classificador baseado em regras não consegue distinguir entre duas categorias em casos extremos. Testar o workflow contra a mesma tarefa diz o que você realmente está comprando ao trocar para um agente.

A disciplina: antes de se comprometer com um agente, pergunte "que workflow foi tentado, e por que falhou?" Se a resposta é "nenhum foi", insista em construir um primeiro. Você pode descobrir que o workflow resolve o problema bem o bastante, ou pode descobrir que o workflow falha de maneiras específicas que um agente de fato melhoraria.

### Sinal de alerta 2: O modo de falha é confiabilidade, e não capacidade

A Lição 2 disse que um agente merece sua imprevisibilidade quando você precisa de flexibilidade. Mas a flexibilidade tem custos em confiabilidade que as etapas 11-12 desta trilha gastaram lições nomeando: erros de grounding em agentes de computer use (Lição 25), erros de ferramenta em cascata, em que a falha de uma ferramenta derruba o passo seguinte (Lição 28), envenenamento de contexto, em que uma afirmação falsa entra na transcrição e é tratada em silêncio como fato por todos os turnos seguintes (Lição 27).

Se o modo de falha de uma tarefa é uma dessas classes de confiabilidade, e a tarefa é algo em que um workflow fixo e bem testado simplesmente nunca cometeria essa classe de erro, então um agente compra imprevisibilidade ao custo de um problema de confiabilidade que antes não existia.

Exemplo: um sistema de classificação de documentos que precisa encaminhar documentos a exatamente uma de cinco categorias conhecidas. Um agente pode encaminhar com flexibilidade e até recategorizar se ler algo no documento que o faça mudar de ideia. Mas, se a tarefa é classificar um documento financeiro com um processo fixo e auditável, e a penalidade por uma classificação errada é uma violação regulatória, então a flexibilidade de um agente não vale o risco de o envenenamento de contexto fazer o agente duvidar do próprio raciocínio anterior e enviar um documento à categoria errada. Um workflow com uma única decisão de roteamento por documento, auditável passo a passo, custa previsibilidade, mas ganha confiabilidade onde importa.

A disciplina: para tarefas em que a falha é cara ou em que a confiabilidade é inegociável, nomeie que problema de confiabilidade um agente introduziria e um workflow não teria. Se esse problema é grave o bastante, o workflow é a melhor escolha, mesmo que pareça menos sofisticado.

### Sinal de alerta 3: A tríade letal está toda presente sem nenhum benefício

A Lição 31 nomeou a tríade letal: acesso a dados privados, exposição a conteúdo não confiável e capacidade de comunicar-se com o exterior. Um agente tem as três condições quando lê entrada não confiável e tem ferramentas que podem usar dados de forma indevida ou exfiltrá-los.

Remover qualquer uma das condições quebra o ataque. Mas um agente que tem as três condições é explorável mesmo que uma injeção só tenha sucesso às vezes. A Lição 32 ensinou que a defesa não é pedir ao modelo com mais força no prompt, mas estreitar o acesso das ferramentas.

Se um agente proposto tem as três condições da tríade e a tarefa não se beneficia da imprevisibilidade do agente, então você está comprando exploração sem nenhum ganho. Uma integração mais estreita baseada em workflow, ou um conjunto de ferramentas que deliberadamente não tem uma das três condições, alcança o mesmo objetivo sem montar a exposição.

Exemplo: um mecanismo de recomendação de conteúdo lê perfis de usuários e fontes externas de conteúdo para sugerir itens. Se o mecanismo é implementado como um agente com ferramentas para buscar conteúdo externo, consultar dados de usuários e enviar recomendações a um sistema de mensagens, ele tem as três condições da tríade. Mas, se o trabalho do mecanismo é selecionar de um conjunto fixo de tipos de recomendação com base em regras simples (se o usuário viu A, recomende B), então um workflow faz o trabalho sem expor os dados do usuário e o sistema de recomendação a um canal de injeção de prompt que antes não existia.

A disciplina: para cada condição da tríade, pergunte se a tarefa de fato precisa dela. Se um agente tem as três para uma tarefa que não exige a flexibilidade do agente, redesenhe o conjunto de ferramentas para remover deliberadamente pelo menos uma condição. O sistema será menos impressionante como demo, mas será menos explorável e mais confiável.

### Sinal de alerta 4: O custo em tokens excede o valor da tarefa

A Lição 33 ensinou a amplificação de tokens e o custo por tarefa concluída, incluindo o multiplicador multiagente. A Lição 19 mostrou que um sistema orquestrador-worker custa várias vezes mais em tokens do que um único agente resolvendo o mesmo problema.

Uma pergunta concreta: estime o custo real por tarefa concluída, incluindo retries, coordenação multiagente se aplicável e qualquer amplificação de tokens pelo comprimento do contexto ou pela sobrecarga de caching. Esse custo é aceitável para o que a tarefa produz?

Essa pergunta muitas vezes não é feita até ser tarde demais. Uma equipe constrói um agente, o lança e descobre que o custo por tarefa excede o que a tarefa vale em valor de negócio. O agente funciona, mas operá-lo é caro demais.

A disciplina: antes de se comprometer com um agente (especialmente um sistema multiagente), estime o custo em tokens por tarefa concluída usando turnos ou trajetórias reais de um protótipo. Confronte essa estimativa com o valor da tarefa. Se o custo em tokens excede o valor, o agente não se justifica, por mais elegante que seja o sistema.

### Juntando tudo: faça estas quatro perguntas antes de se comprometer com um agente

1. Um workflow mais simples foi de fato tentado e considerado insuficiente?
2. O modo de falha da tarefa é um em que um agente introduz um novo problema de confiabilidade que um workflow não teria?
3. O agente tem as três condições da tríade, e essa exposição é necessária para a tarefa?
4. O custo em tokens por tarefa concluída é aceitável para o que a tarefa produz?

Se a resposta a qualquer uma dessas é "não" ou "não sabemos", o agente pode não se justificar. Dizer não a um agente não é fracasso; é disciplina. Você está escolhendo previsibilidade, confiabilidade, segurança ou custo em vez da flexibilidade que um agente compraria. Essa é uma escolha defensável, e é a escolha que permite dizer sim com confiança quando um agente de fato se justifica.

## Prática

1. ▢ Uma equipe de produto propõe construir um agente para resumir tickets de suporte ao cliente para relatórios internos. O agente leria o ticket (conteúdo de usuário não confiável), acessaria o banco de dados de clientes da empresa para buscar contexto e postaria resumos em um canal do Slack. Uma alternativa em workflow teria uma pessoa classificando manualmente os tickets em categorias e depois rodando um sumarizador baseado em template em cada categoria. A equipe diz "um agente é mais eficiente". Sem rodar o workflow, que pergunta você deve fazer primeiro?

<details markdown="1"><summary>Verificação</summary>

Peça que eles de fato construam e testem o workflow em tickets reais. Meça quanto mais rápido o agente é e se o ganho de eficiência justifica o custo em consumo de tokens e a exposição da tríade letal (o agente lê conteúdo não confiável, acessa dados privados de clientes e envia mensagens externas). Se o workflow é 90 por cento tão bom e custa 10 por cento do preço, o workflow vence. Sem testar o workflow, a afirmação "um agente é mais eficiente" não foi testada.

</details>

2. ▢ Você está revisando uma proposta de um agente que ajuda analistas a depurar testes que falham em uma base de código grande. O agente teria acesso ao código do repositório, aos resultados de testes e aos logs. Ele chamaria ferramentas para pesquisar o código, rodar testes individuais e registrar relatórios de bug. A proposta diz: "Um agente consegue explorar a base de código com mais flexibilidade do que um script." Que preocupação de confiabilidade a Lição 27 ensina que é relevante para avaliar essa proposta?

<details markdown="1"><summary>Dica</summary>

Pense no que acontece quando um agente está lendo as saídas de chamadas de ferramenta e construindo um modelo do que o código diz e faz. Que padrão de erro é exclusivo de agentes?

</details>

<details markdown="1"><summary>Verificação</summary>

Envenenamento de contexto (Lição 27). Se o agente interpreta mal um log ou um trecho de código e embute uma afirmação falsa em seu modelo do bug (por exemplo, "esta função retorna None"), todo passo de raciocínio posterior tratará essa afirmação falsa como fato estabelecido. Um script com um caminho fixo não duvidará da própria saída dessa forma. A flexibilidade de um agente para mudar de ideia com base em novas evidências é um ativo, mas também abre a porta para uma confiança silenciosa em conclusões erradas carregadas de um passo para o seguinte. Avalie se o modo de falha da tarefa (depurar um teste) é mais prejudicado pela flexibilidade (melhor em encontrar bugs inéditos) ou pelo risco de o envenenamento de contexto levar o agente por um caminho falso.

</details>

3. ▢ Qual destes cenários indica com mais clareza que um agente proposto não se justifica?

    - a) A tarefa pode ser resolvida por um workflow, mas o workflow exigiria ligar um novo ramo toda vez que chega um novo tipo de documento
    - b) A tarefa foi tentada como workflow e não atingiu as metas de acurácia, mas um agente protótipo testado no mesmo conjunto de dados se sai melhor
    - c) A tarefa nunca foi tentada como workflow, mas um stakeholder insiste que um agente é necessário porque uma demo de IA que viu foi impressionante
    - d) A tarefa exige ler conteúdo não confiável e acessar dados privados, mas o conjunto de ferramentas do agente deliberadamente não tem comunicação externa

<details markdown="1"><summary>Verificação</summary>

**c)** O cenário em que uma tarefa nunca foi tentada como workflow e a proposta é movida pelo entusiasmo com uma demo, e não por evidência de que a alternativa mais simples falha. O cenário (a) descreve uma tarefa em que um agente compra flexibilidade contínua; o número de ramos está crescendo, então um agente se justifica. O cenário (b) mostra que o workflow foi testado e falhou, tornando o melhor desempenho do agente uma evidência a seu favor. O cenário (d) descreve uma arquitetura fundamentada que remove uma condição da tríade, o que é uma escolha de design justificada. Apenas (c) não tem base em testes.

</details>

4. ▢ Você estima que um agente para uma tarefa custaria 5.000 tokens por execução concluída, incluindo retries, e a tarefa produz valor de negócio equivalente a 2.000 tokens de computação aos preços de mercado atuais. Defenda uma escolha entre construir o agente ou escolher uma alternativa, nomeando o que você está aceitando ao fazer essa escolha.

<details markdown="1"><summary>Verificação</summary>

A alternativa (um workflow, um sistema mais simples ou deixar a tarefa manual) se justifica. O agente custa 2,5x o seu valor, o que significa que cada execução custa ao negócio mais em computação do que devolve em valor. Construir o agente mesmo assim só é defensável se você espera que o custo em tokens caia (modelos mais baratos, estratégias de caching, convergência mais rápida em tarefas repetidas), ou se o valor de negócio é maior do que o estimado. Se nenhuma das duas coisas é verdade, a disciplina é dizer não. O custo que você está aceitando é perder a flexibilidade que um agente daria, mas você ganha previsibilidade e eficiência de custo. Essa é a troca certa nesses números.

</details>

## Prática no mundo real

- [ ] Pegue uma tarefa atualmente resolvida por um agente em um sistema que você conhece. Estime o custo em tokens por tarefa concluída e o valor de negócio de cada conclusão. A razão é aceitável? Se não, o que teria de mudar para um agente se justificar?
- [ ] Encontre uma proposta (interna, ou um artigo descrevendo um sistema) que defende um agente. Verifique se ela responde às quatro perguntas de sinal de alerta: um workflow foi tentado, o modo de falha é sensível à confiabilidade, as três condições da tríade são necessárias e o custo é aceitável? Anote quais sinais de alerta a proposta aborda e quais deixa em aberto.
- [ ] Amanhã: Imagine um recurso de produto que você construiria como agente. Agora projete-o como workflow. Compare: o que o workflow não consegue fazer que o agente consegue? Quão mais difícil é construir o workflow? Os ganhos justificam a complexidade adicional? Anote sua avaliação honesta.

## Para ir além

- [Article: "Building Effective Agents", Anthropic Engineering](https://www.anthropic.com/engineering/building-effective-agents)
- [Recursos](../RESOURCES.md)

---

Não ficou claro? Releia a fonte principal no topo, já que esta lição a comprime e é na compressão que o entendimento escapa. Consulte o [glossário](../GLOSSARY.md) para qualquer termo que pareceu escorregadio.

Se o problema é a lição em si, e não o material, isso é um defeito: [abra uma issue](https://github.com/TokenCemetery/teach/issues).
