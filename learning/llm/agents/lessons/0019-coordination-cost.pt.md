---
title: "19. Custo de coordenação"
description: "Entender por que construir vários agentes é mais caro do que um único agente bem equipado e como decidir quando o ganho de paralelismo compensa o custo"
type: lesson
---

# Lição 19. Custo de coordenação

**Ligação com a missão:** Para escolher entre um único agente bem equipado e um sistema multiagente, você precisa saber o que sistemas orquestrador-worker custam em tokens, raciocínio e contexto fragmentado, e como julgar se um segundo agente compra algo que o primeiro agente não poderia ter recebido diretamente.
**Fonte principal:** [Article: "Don't Build Multi-Agents", Cognition](https://cognition.ai/blog/dont-build-multi-agents)
**Pré-requisitos:** [Lição 18](0018-orchestrator-and-worker.md)

## Aquecimento

1. ▢ Da Lição 18, lembre: em um sistema orquestrador-worker, um worker consegue ver a trajetória completa de raciocínio de outro worker enquanto o outro worker está rodando?

<details markdown="1"><summary>Verificação</summary>

Não. Cada worker roda seu próprio loop de agente com sua própria transcrição isolada. Os workers só veem as descobertas uns dos outros se o orquestrador as passar explicitamente, e apenas os relatórios finais, não o raciocínio completo. Esse isolamento é uma característica (mantém o contexto limpo) e um custo (os workers não conseguem compartilhar percepções no meio da tarefa).

</details>

2. ▢ Da Lição 18, lembre: qual é a diferença entre fan-out e handoff?

<details markdown="1"><summary>Verificação</summary>

O fan-out dispara vários workers sobre variações do mesmo problema em paralelo, explorando ângulos diferentes ao mesmo tempo para obter cobertura mais ampla e paralelismo. O handoff é sequencial: um agente termina sua tarefa e passa um contexto limpo a um segundo agente especializado na fase seguinte. Ambos são padrões multiagente; o fan-out usa o tempo, o handoff usa a especialização.

</details>

## Saiba isto

### Custo em tokens: muitos agentes custam muitas vezes mais

Toda execução de agente tem um custo. Um sistema orquestrador-worker paga esse custo várias vezes.

Suponha que um único agente resolva um problema em 10.000 tokens: digamos, 20 turnos com 500 tokens por turno. Agora suponha que o mesmo problema seja dividido em três subtarefas independentes, cada uma resolvida por um worker em 8.000 tokens (um pouco menos, porque cada worker tem um foco mais estreito). O próprio orquestrador usa 2.000 tokens para dividir a tarefa e sintetizar os resultados.

Custo total: 8.000 + 8.000 + 8.000 + 2.000 = 26.000 tokens. O sistema multiagente custou 2,6x o que o agente único custou, mesmo que cada worker tenha sido um pouco mais eficiente do que o agente único teria sido apenas na sua parte. Os workers exploram em paralelo, então o tempo de relógio é menor, mas o custo em tokens é multiplicado.

Essa conta piora se os workers rodam de forma ineficiente ou se o orquestrador precisa coordenar mais de uma vez (por exemplo, o orquestrador percebe que os workers deixaram passar uma dependência, dispara novos workers ou pede que os workers rodem de novo com novas instruções). O artigo da Cognition aponta isso como a pergunta central: o ganho de velocidade do paralelismo vale pagar várias vezes o custo em tokens?

### Contexto fragmentado: os workers não veem uns aos outros

Quando um único agente roda uma tarefa longa, ele constrói contexto: sabe o que tentou, o que funcionou, o que não funcionou e por quê. Um sistema multiagente fragmenta esse contexto. Os workers A e B podem pesquisar terreno sobreposto (por exemplo, ambos tentando entender uma restrição), mas o Worker A não vê o raciocínio do Worker B sobre essa restrição; vê apenas o relatório final.

Concretamente: o Worker A percebe no meio da tarefa que uma restrição tem uma implicação sutil. O Worker A raciocina sobre isso, constrói intuição e reporta. O orquestrador lê o relatório e o passa ao Worker B. O Worker B agora conhece a conclusão, mas não o raciocínio que levou a ela. O Worker B não consegue refinar nem contestar esse raciocínio no meio da tarefa, porque não vê o pensamento do Worker A. O Worker B ou aceita o relatório e o usa (perdendo a chance de refiná-lo) ou o ignora e rederiva a mesma percepção (desperdiçando tokens).

Para tarefas em que a melhor resposta emerge de um vaivém de refinamento entre várias linhas de raciocínio, o contexto fragmentado é uma limitação real. Um único agente com turnos suficientes consegue manter todo o seu raciocínio em um só lugar e integrar as percepções conforme se desenvolvem.

### Conclusões conflitantes: a exploração independente leva a divergências

Quando dois workers exploram o mesmo terreno de forma independente, podem chegar a conclusões diferentes. Isso não é necessariamente errado; podem ter encontrado interpretações genuinamente diferentes (e ambas válidas). Mas também pode significar que um worker cometeu um erro ou deixou passar algo que o outro pegou.

O orquestrador vê os dois relatórios e precisa reconciliá-los. Se o conflito é semântico ou factual, o orquestrador tem um problema: ele tem apenas os resumos dos workers, e não o raciocínio completo deles, então não consegue rastrear com facilidade de onde veio a divergência. O orquestrador pode disparar um novo agente (um subagente "juiz" ou "sintetizador") para reconciliar, o que acrescenta mais custo.

A alternativa do agente único evita isso: um único agente passando pelo mesmo terreno em série integra cada nova descoberta ao seu modelo mental corrente, então pode identificar contradições conforme surgem e resolvê-las dentro do próprio loop de raciocínio.

### O princípio de decisão: quando o multiagente é mais barato?

A fonte principal, da Cognition, argumenta que a maioria dos sistemas multiagente não é mais barata, em tokens ou em qualidade de raciocínio, do que um único agente com ferramentas melhores. A pergunta não é "o paralelismo é mais rápido?" (sim), mas "o paralelismo compra algo que um único agente não poderia ter por menos custo?"

Aplique este princípio de decisão:

**O multiagente faz sentido quando:**

- As subtarefas são verdadeiramente independentes (sem contexto compartilhado, sem dependência dos resultados uns dos outros no meio da tarefa).
- As subtarefas são, cada uma, mais simples do que a tarefa original (cada worker resolve um problema genuinamente mais estreito, de modo que a soma do ganho de eficiência dos workers supera o custo da duplicação).
- Você precisa do ganho de velocidade do paralelismo (a economia de tempo justifica o multiplicador de tokens; você tem um prazo de tempo de relógio que não consegue cumprir com um agente e mais turnos).
- As ferramentas de cada worker são especializadas o bastante para que um conjunto de ferramentas compartilhado atrasasse cada worker com opções irrelevantes.

**Um único agente com mais recursos geralmente vence quando:**

- As subtarefas compartilham contexto ou se refinam mutuamente (um único agente mantém todo o seu raciocínio conectado; um sistema multiagente precisa rederivar ou recomunicar).
- Você tem folga no orçamento de contexto (dê ao agente único uma janela de contexto maior, melhor recuperação, mais ferramentas, mais turnos).
- As subtarefas são interdependentes ou exigem vaivém de refinamento entre várias linhas de raciocínio.
- A sobrecarga de coordenação (tempo do orquestrador, comunicação, reconciliação de conclusões conflitantes) é alta em relação ao problema.

Dito sem rodeios: um único agente com ferramentas melhores, um contexto mais longo e mais turnos muitas vezes resolve o mesmo problema mais barato e com melhor qualidade de raciocínio do que vários agentes com contexto fragmentado. O ganho de velocidade do paralelismo é real, mas não é de graça.

## Prática

1. ▢ Você está construindo um sistema de perguntas e respostas. Opção A: um agente com ferramentas de busca, execução de código e documentação. Opção B: um orquestrador que dispara três workers em paralelo, cada um com uma ferramenta especializada (worker de busca, worker de código, worker de documentação). Ambos visam responder perguntas complexas de usuários. Em que circunstâncias o custo em tokens da Opção B se torna mais barato do que o da Opção A?

<details markdown="1"><summary>Verificação</summary>

Isto é uma armadilha. Na maioria das circunstâncias, a Opção B custa mais em tokens: você paga três execuções completas de agente mais a sobrecarga do orquestrador, como no exemplo desta lição de 26.000 tokens contra 10.000. A Opção B só fica mais barata num caso estreito: as três subtarefas são de fato independentes, e cada uma é tão mais simples do que a pergunta inteira que os três workers e o orquestrador juntos usam menos tokens do que o agente único (por exemplo, três workers de 2.500 tokens cada mais um orquestrador de 2.000, 9.500 no total, contra um agente único de 10.000). Isso só acontece quando o agente único desperdiça muitos turnos no problema combinado. Nos demais casos, a Opção A é mais barata. O trade-off é tempo de relógio (a Opção B é mais rápida por causa do paralelismo) contra tokens (a Opção A é mais barata). Você escolhe a Opção B pela velocidade, não pelo custo.

</details>

2. ▢ No sistema orquestrador-worker da Lição 18 (workers de pesquisa em paralelo), suponha que dois workers acabem pesquisando a mesma fonte e cheguem a conclusões diferentes sobre o que ela diz. O orquestrador tem os dois relatórios. O que falta ao orquestrador que um único agente teria tido?

<details markdown="1"><summary>Dica</summary>

Pense no que está na transcrição de cada worker em comparação com o que está na transcrição de um único agente no momento de raciocinar sobre aquela fonte.

</details>

<details markdown="1"><summary>Verificação</summary>

O orquestrador vê duas conclusões, mas não o raciocínio que levou a cada uma. Um único agente, tendo lido a mesma fonte, teria todo o seu raciocínio sobre ela em uma transcrição: como interpretou o texto, que nuance notou, o que considerou e rejeitou. O raciocínio do agente único é totalmente rastreável. O orquestrador só pode perguntar "por que você chegou a essa conclusão?" e um worker teria de explicar de novo, ou o orquestrador teria de disparar um novo agente para rastrear a divergência. Isso é contexto fragmentado.

</details>

3. ▢ Você está decidindo se usa fan-out (orquestrador-worker) ou um único agente para uma tarefa. A tarefa é: dado um conjunto de dados e uma pergunta, limpar os dados, explorá-los, construir um modelo e relatar as descobertas. As fases (limpeza, exploração, modelagem, relatório) rodarão em paralelo sob fan-out, ou em sequência?

    - a) Em paralelo, porque o fan-out dispara todos os workers de uma vez.
    - b) Em sequência, porque a exploração depende da limpeza e a modelagem depende da exploração.
    - c) Em paralelo, mas o trabalho pode ser dividido de modo que cada worker faça todas as fases de forma independente.
    - d) Depende de os workers terem acesso ao mesmo conjunto de dados.

<details markdown="1"><summary>Verificação</summary>

**b)** Esta tarefa não é um bom caso para fan-out porque as fases são sequenciais: você não consegue explorar bem dados sujos, não consegue modelar sem entender os dados, e assim por diante. Cada fase depende da anterior. O fan-out brilha em tarefas com subtarefas independentes (pesquisar o ângulo A, o ângulo B e o ângulo C em paralelo). Para trabalho sequencial, o handoff (Lição 18) é um encaixe melhor do que o fan-out, ou um único agente com turnos suficientes é mais simples. (a) está errada: o paralelismo não faz mágica; as dependências continuam existindo. (c) é possível, mas anula o propósito da especialização; cada worker precisaria de todas as ferramentas e de todo o conhecimento. (d) é uma pista falsa; o acesso aos dados não é o fator limitante aqui.

</details>

4. ▢ O artigo da Cognition argumenta que um único agente com melhor recuperação ou ferramentas mais capazes muitas vezes resolve problemas mais barato em tokens do que um sistema orquestrador-worker. Qual é a razão central dessa afirmação?

<details markdown="1"><summary>Verificação</summary>

Um único agente mantém todo o seu raciocínio em uma transcrição, então integra descobertas, identifica contradições e refina conclusões dentro de um único loop de raciocínio. Um sistema orquestrador-worker paga o custo em tokens de muitos loops de agente e fragmenta o contexto entre eles, então os workers rederivam ou recomunicam percepções. O ganho de eficiência do agente único por manter o contexto unificado e o raciocínio conectado muitas vezes supera o ganho de velocidade do paralelismo do sistema multiagente, especialmente quando a pergunta tem dependências ou se beneficia de raciocínio integrado. Dar a um agente mais ferramentas ou melhor recuperação (ambos mais baratos do que rodar vários agentes) muitas vezes vence.

</details>

5. ▢ Você está construindo um sistema para depurar um programa que falha. Você considera fan-out: disparar três workers, cada um tentando uma estratégia de depuração diferente em paralelo, e fazer o orquestrador escolher a melhor percepção. Que custo esse design não captura que a Lição 19 ensina?

<details markdown="1"><summary>Verificação</summary>

Custo em tokens multiplicado por três (cada worker é uma execução completa de agente), contexto fragmentado (nenhum worker vê as explorações dos outros, então podem rederivar o mesmo beco sem saída três vezes em vez de aprender uns com os outros) e o orquestrador precisa reconciliar conclusões potencialmente conflitantes sobre qual é o bug. Um único agente tentando as três estratégias em série construiria um modelo unificado do bug conforme avança. Os três workers não conseguem fazer isso sem o orquestrador rodar uma etapa de reconciliação (outro agente, mais custo). O fan-out compra velocidade (os três workers terminam no tempo do worker mais lento, e não na soma dos três), mas os custos são altos para uma tarefa como a depuração, em que uma percepção se constrói sobre outra.

</details>

## Prática no mundo real

- [ ] Pegue um problema que você já resolveu (depuração, análise, planejamento, pesquisa, o que for). Percorra-o mentalmente como um único agente com muitos turnos contra três workers em fan-out. Onde o paralelismo ganharia tempo de relógio para você? Onde o contexto fragmentado custaria a você e forçaria rederivação ou trabalho de reconciliação?
- [ ] Leia o artigo da Cognition "Don't Build Multi-Agents" pelo menos uma vez. Procure a seção em que o autor argumenta que um único agente mais ferramentas melhores vence orquestrador-worker. Anote um exemplo concreto que eles dão e o que tornou o agente único mais barato.
- [ ] Amanhã: esboce uma tarefa que você poderia construir em um sistema de agentes. Para essa tarefa, estime: quantos tokens um único agente usaria? Quantos um sistema com fan-out custaria (chute três workers, cada um com custo em tokens ligeiramente menor do que a fatia por tarefa do agente único)? O ganho de velocidade vale o multiplicador de tokens para você?

## Para ir além

- [Article: "Don't Build Multi-Agents", Cognition](https://cognition.ai/blog/dont-build-multi-agents)
- [Article: "How We Built Our Multi-Agent Research System", Anthropic Engineering](https://www.anthropic.com/engineering/multi-agent-research-system)
- [Recursos](../RESOURCES.md)

---

Não ficou claro? Releia a fonte principal no topo, já que esta lição a comprime e é na compressão que o entendimento escapa. Consulte o [glossário](../GLOSSARY.md) para qualquer termo que pareceu escorregadio.

Se o problema é a lição em si, e não o material, isso é um defeito: [abra uma issue](https://github.com/TokenCemetery/teach/issues).
