---
title: "18. Orquestrador e worker"
description: "Projetar um sistema multiagente em que um agente planeja e delega e os workers executam em paralelo"
type: lesson
---

# Lição 18. Orquestrador e worker

**Ligação com a missão:** Para escolher entre um único agente bem equipado e um sistema multiagente, você precisa entender o que sistemas multiagente conseguem fazer que agentes únicos não conseguem, começando pelo padrão orquestrador-worker que sustenta a maioria dos sistemas multiagente de pesquisa e planejamento.
**Fonte principal:** [Article: "How We Built Our Multi-Agent Research System", Anthropic Engineering](https://www.anthropic.com/engineering/multi-agent-research-system)
**Pré-requisitos:** [Lição 17](0017-self-critique-and-reasoning-models.md), [Subagente](../GLOSSARY.md)

## Aquecimento

1. ▢ Da Lição 17, lembre: o que um loop de reflexão explícito faz depois de uma tentativa que falhou, e por que um modelo com raciocínio interno estendido precisa menos desse loop externo do que um modelo padrão?

<details markdown="1"><summary>Verificação</summary>

Um loop de reflexão explícito gera uma crítica em linguagem natural de por que a tentativa falhou e leva essa crítica para a próxima tentativa, como um passo separado do próprio turno do modelo. Um modelo que faz raciocínio interno estendido antes de responder consegue pegar alguns dos mesmos erros dentro de um único turno, então o loop externo compensa o custo com menos frequência, embora ainda ajude quando o sinal de falha (um erro de ferramenta, um resultado de teste) só existe depois de o modelo já ter agido.

</details>

2. ▢ Da Lição 12, lembre: o que é um subagente, e que problema a transcrição separada dele resolve?

<details markdown="1"><summary>Verificação</summary>

Um subagente é uma execução de agente separada, com seu próprio harness e sua própria transcrição. Ele resolve o isolamento de contexto: você pode iniciar um subagente focado em uma tarefa delimitada sem que a transcrição dessa tarefa infle o contexto do agente pai, mantendo o raciocínio do pai limpo para a síntese e a coordenação.

</details>

## Saiba isto

### O padrão orquestrador-worker

Quando uma tarefa é ampla demais para o contexto de um agente ou precisa de exploração paralela, o padrão orquestrador-worker divide o trabalho: um agente (o orquestrador) quebra a tarefa em subtarefas delimitadas, decide qual worker recebe qual subtarefa e depois sintetiza os resultados em uma resposta final. Cada worker é um subagente com sua própria transcrição e suas próprias ferramentas, rodando de forma independente (e muitas vezes em paralelo).

Pense em um líder de equipe que não faz o trabalho diretamente, mas coordena: o líder divide um projeto, atribui partes aos membros da equipe e reúne as entregas deles. Os workers nunca veem o raciocínio completo uns dos outros; o orquestrador só vê os relatórios finais deles.

### O que os workers fazem

Workers não são intercambiáveis. Cada worker normalmente tem:

- Uma missão delimitada e específica (por exemplo, "pesquise este ângulo", "avalie esta abordagem candidata")
- Ferramentas sob medida para essa missão (por exemplo, recuperação para um worker de pesquisa, execução de código para um worker de avaliação)
- Seu próprio loop de agente e sua própria transcrição, isolados dos demais workers

Como os workers rodam seus próprios loops, eles podem explorar de forma independente. Um worker não precisa saber o que os outros estão fazendo; só conhece a própria tarefa. Essa independência é o que torna o paralelismo possível: muitos workers podem rodar ao mesmo tempo, e o tempo de relógio é limitado pelo worker mais lento, não pela soma dos tempos de todos.

### Fan-out: exploração paralela

Fan-out é um subcaso de orquestrador-worker em que o orquestrador dispara vários workers sobre variações da mesma pergunta. Por exemplo:

- Um worker pesquisa o ângulo A, outro pesquisa o ângulo B, um terceiro pesquisa o ângulo C, todos em paralelo, para obter cobertura mais ampla mais depressa do que um agente passando por eles em série.
- Três workers tentam, cada um, resolver o mesmo problema de código com estratégias diferentes, e o orquestrador escolhe a melhor solução ou combina as percepções.

O ganho de velocidade é real: em vez de um único agente gastar 10 turnos no problema A, depois 10 turnos no problema B, depois 10 turnos no problema C (30 turnos no total), três workers atacam A, B e C em paralelo (10 turnos de latência em vez de 30). O porém (explorado na Lição 19) é que você paga o custo em tokens das execuções completas dos três workers, e não de apenas uma execução de agente.

### Handoff: especialização sequencial

Handoff é um padrão multiagente diferente, que também usa subagentes, mas com fases sequenciais em vez de workers paralelos. No handoff:

1. O agente A termina sua parte da tarefa.
2. O agente A faz o handoff ao agente B dando-lhe um contexto limpo e delimitado: tipicamente apenas a definição da tarefa e as descobertas finais do agente A, e não a trajetória completa do agente A.
3. O agente B continua dali, usando suas próprias ferramentas e raciocínio especializados.

O handoff é útil quando uma tarefa se divide naturalmente em fases sequenciais tratadas por especialistas diferentes. Por exemplo: um orquestrador descobre que um problema precisa de pesquisa profunda e de implementação, então faz o handoff das descobertas a um programador especializado; ou um planejador termina um plano e o entrega a um executor com apenas o plano, e não o raciocínio bagunçado sobre por que aquele plano foi escolhido.

Handoff e fan-out são opostos no ritmo: fan-out é muitos em paralelo, handoff é um depois do outro. Ambos são multiagente; ambos isolam contexto usando subagentes; ambos são ensinados nesta lição porque ambos respondem à pergunta "quando um agente não basta?"

### Por que sistemas orquestrador-worker entregam valor na prática

A fonte principal detalha um sistema concreto de pesquisa multiagente construído na Anthropic: quebrar uma tarefa de pesquisa complexa em muitas subtarefas de pesquisa independentes, disparar um worker para cada uma, recuperar e analisar fontes em paralelo e depois sintetizar as descobertas em uma resposta coesa. Os principais ganhos foram:

- Paralelismo no tempo de relógio: uma pesquisa complexa em que um único agente gastaria mais de 50 turnos podia acontecer mais depressa com 5 workers, cada um em 15 turnos, rodando simultaneamente.
- Ferramentas especializadas por worker: um worker de recuperação pode se concentrar em busca e ranqueamento sem o inchaço de contexto da execução de código; um worker de síntese tem um objetivo diferente e ferramentas diferentes.
- Raciocínio independente: cada worker raciocina sobre a sua fatia do problema; os workers não se distraem com informação destinada a outros workers.

Esse padrão surgiu como solução prática para uma restrição real: a capacidade de um modelo de raciocinar bem em uma tarefa complexa é limitada em parte pelo comprimento do contexto e em parte pela necessidade de manter o raciocínio focado. Dividir o trabalho permite acrescentar mais poder de raciocínio (mais workers, cada um com seu próprio orçamento de contexto) sem que um único agente perca o foco ou fique sem contexto.

## Prática

1. ▢ Você está construindo um sistema para responder perguntas de usuários sobre uma base de código grande. Você considera dois designs: (A) um único agente com acesso a ferramentas de busca de código e de documentação, ou (B) um orquestrador que delega a um worker de busca e a um worker de documentação em paralelo. Qual design se encaixa mais naturalmente no padrão orquestrador-worker, e por quê?

<details markdown="1"><summary>Verificação</summary>

O design (B) se encaixa no padrão. O worker de busca e o worker de documentação têm tarefas independentes: um busca no código, o outro busca na documentação. Podem rodar em paralelo sem precisar dos resultados um do outro no meio da tarefa. O trabalho do orquestrador é claro: formular consultas para cada worker e depois combinar as descobertas deles.

O design (A) também poderia funcionar, mas o agente único teria de decidir no meio da tarefa qual ferramenta usar em seguida; não há ganho de paralelismo. Você escolheria (B) quando espera que as consultas de busca e de documentação sejam independentes e se beneficiem de exploração paralela; escolheria (A) se as consultas dependem uma da outra (os resultados da busca informam qual documentação buscar) ou se a sobrecarga de iniciar dois subagentes supera o ganho de velocidade (uma tarefa mais simples).

</details>

2. ▢ Em um sistema orquestrador-worker, por que um worker não pode ver diretamente o raciocínio de outro worker no meio da tarefa?

<details markdown="1"><summary>Dica</summary>

Pense na estrutura: cada worker tem sua própria transcrição e seu próprio harness. O que esse isolamento impede?

</details>

<details markdown="1"><summary>Verificação</summary>

Cada worker roda seu próprio loop de agente com sua própria transcrição. O raciocínio do Worker A é registrado na transcrição do Worker A, e o raciocínio do Worker B está na transcrição do Worker B. O harness não as mescla. Os workers não têm acesso às transcrições uns dos outros durante suas execuções; só podem ler os relatórios finais que o orquestrador lhes der (se o orquestrador os passar). Esse isolamento mantém o contexto de cada worker focado e é a razão de os subagentes resolverem problemas de contexto. O trade-off é a fragmentação: uma decisão que precisa do raciocínio completo dos dois workers não pode ser tomada por nenhum deles sozinho (coberto na Lição 19).

</details>

3. ▢ Você está projetando um sistema de pesquisa. Cenário: um worker está pesquisando a história de uma tecnologia, e um segundo worker está pesquisando as aplicações atuais dessa tecnologia. As tarefas desses workers podem rodar em paralelo?

    - a) Não, porque o worker de aplicações precisa conhecer primeiro a história.
    - b) Sim, os dois workers podem pesquisar de forma independente; o orquestrador pode sintetizar as descobertas sobre história e aplicações independentemente da ordem.
    - c) Não, porque eles estão pesquisando a mesma tecnologia.
    - d) Sim, apenas se o worker de história terminar antes de o worker de aplicações começar.

<details markdown="1"><summary>Verificação</summary>

**b)** As duas tarefas são independentes: um worker pesquisando história não precisa das descobertas do outro worker para fazer uma boa pesquisa sobre história, e vice-versa. O orquestrador terá os dois resultados quando os dois workers terminarem e poderá sintetizá-los em uma resposta completa. (a) está errada: dependências rodariam uma depois da outra (handoff), e não em fan-out; aqui não há dependência. (c) está errada: pesquisar a mesma tecnologia não é um bloqueio ao paralelismo; na verdade, é por isso que o fan-out é útil, para obter vários ângulos sobre o mesmo tópico. (d) está errada: paralelismo significa que rodam ao mesmo tempo, e não um depois do outro.

</details>

4. ▢ Um handoff difere de um fan-out em quê?

<details markdown="1"><summary>Verificação</summary>

O fan-out é paralelo: o orquestrador dispara vários workers sobre variações do mesmo problema ao mesmo tempo. O handoff é sequencial: um agente termina e depois passa suas descobertas a um segundo agente sob medida para a fase seguinte. O fan-out pergunta "como podemos explorar mais ângulos em paralelo?"; o handoff pergunta "como podemos dividir um processo sequencial em fases especializadas?" Ambos usam subagentes; ambos isolam contexto; ambos respondem "quando um agente não basta?", mas em ritmos diferentes.

</details>

## Prática no mundo real

- [ ] Na próxima vez que você vir uma tarefa complexa (pesquisa, planejamento, depuração), esboce se ela se encaixa em orquestrador-worker (há subtarefas independentes que podem rodar em paralelo?), handoff (há fases sequenciais para especialistas diferentes?) ou um único agente com mais ferramentas (um agente consegue com ferramentas melhores e mais turnos?). Não construa nada; apenas pratique o reconhecimento de formas.
- [ ] Leia o artigo da fonte principal: "How We Built Our Multi-Agent Research System". Foque na seção que descreve o que o orquestrador fez, o que cada worker fez e o que teria mudado se tivessem usado um único agente. Anote um ganho concreto de paralelismo que eles relataram.
- [ ] Amanhã: descreva uma tarefa real do seu trabalho ou estudo que se beneficiaria de fan-out (vários workers explorando o mesmo problema em paralelo). Que ângulo cada worker tomaria? De que ferramentas cada um precisaria?

## Para ir além

- [Article: "How We Built Our Multi-Agent Research System", Anthropic Engineering](https://www.anthropic.com/engineering/multi-agent-research-system)
- [Recursos](../RESOURCES.md)

---

Não ficou claro? Releia a fonte principal no topo, já que esta lição a comprime e é na compressão que o entendimento escapa. Consulte o [glossário](../GLOSSARY.md) para qualquer termo que pareceu escorregadio.

Se o problema é a lição em si, e não o material, isso é um defeito: [abra uma issue](https://github.com/TokenCemetery/teach/issues).
