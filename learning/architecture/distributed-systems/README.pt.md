---
title: Sistemas Distribuídos
description: "Raciocine sobre falha parcial: o que uma rede pode fazer com você, qual consistência você está de fato comprando e por que o consenso é caro"
type: topic
---

# Aprendizado: Sistemas Distribuídos

Seja capaz de escolher e defender um modelo de consistência para um sistema que você está projetando, e de raciocinar sobre um incidente de produção causado por uma falha parcial em vez de tratar a rede como confiável.

**Última lição:** [19. Verificando uma afirmação](lessons/0019-verifying-a-claim.md)

## O sucesso se parece com isto

- Dado o design de um sistema, escolher um modelo de consistência e defender o trade-off contra as alternativas.
- Dado um incidente causado por uma falha parcial (uma partição de rede, um nó lento confundido com um nó morto), nomear o mecanismo responsável.
- Explicar o que um protocolo de consenso compra e por que custa o que custa, sem precisar provar a sua corretude a partir de primeiros princípios.

## Restrições

- Pressupõe experiência profissional construindo um serviço em rede; não exige estudo formal prévio de sistemas distribuídos.
- Ênfase prática e operacional: o custo e os trade-offs importam mais do que uma prova formal da corretude de um protocolo.

## Fora do escopo

- Concorrência dentro de um único processo (goroutines, threads, `Send`/`Sync`): fica com as trilhas de linguagem. Esta trilha começa onde a fronteira do processo é atravessada.
- Executar workloads em um orquestrador de cluster: fica com [`infrastructure/kubernetes`](../../infrastructure/kubernetes/), que ensina o que etcd e reconciliação significam na prática e aponta de volta para cá para a teoria.

## O arco

Doze etapas, da falha parcial a um incidente diagnosticado, aos mecanismos que os sistemas de produção de fato usam para sobreviver a um, e a como verificar que tudo isso realmente se sustenta. Uma etapa leva várias lições e as fronteiras são flexíveis; o que torna uma etapa concluída é a capacidade, não a contagem de lições.

| Etapa | Lições | Cobre | Concluída quando |
|---|---|---|---|
| 1. Falha parcial | 0001 | O único problema ao qual todo tópico posterior desta trilha responde | Consegue explicar por que uma rede não pode ser tratada como confiável |
| 2. Tempo e ordem | 0002 a 0003 | Relógios, ordenação, por que um timeout é o único sinal de falha disponível | Consegue explicar por que um timeout não consegue distinguir um nó lento de um nó morto |
| 3. Modelos de consistência | 0004 a 0006 | CAP, linearizabilidade, consistência sequencial e eventual | Consegue escolher e defender um modelo de consistência para um design declarado |
| 4. Consenso | 0007 a 0009 | Raft, eleição de líder, o que o consenso compra e por que custa o que custa | Consegue explicar o que um protocolo de consenso compra e custa sem provar a sua corretude |
| 5. Diagnóstico de incidentes | 0010 | Aplicar os mecanismos acima a um incidente real de produção | Dado um incidente causado por falha parcial, consegue nomear o mecanismo responsável |
| 6. Replicação e quóruns | 0011 | Replicação baseada em líder contra sem líder, quóruns de leitura/escrita, a condição `R + W > N` | Consegue explicar como um quórum garante que uma leitura veja a escrita mais recente, e escolher R e W para uma carga de trabalho declarada |
| 7. Particionamento e sharding | 0012 | Consistent hashing, nós virtuais, replicação de hot keys, roteamento de requisições | Consegue explicar por que o consistent hashing limita o custo de um redimensionamento, e do que um anel puro ainda precisa para lidar com falhas e hot keys |
| 8. Resolução de conflitos sob consistência eventual | 0013 | Last-write-wins e o que ele perde, version vectors, CRDTs | Consegue distinguir detectar um conflito de resolvê-lo, e explicar como um CRDT faz o merge sem perda |
| 9. Transações entre serviços | 0014 a 0015 | Two-phase commit e o seu modo de falha bloqueante, sagas e compensação, o transactional outbox, consumidores idempotentes | Consegue explicar por que o 2PC bloqueia, do que uma saga abre mão para evitá-lo e como o padrão outbox evita o problema da escrita dupla |
| 10. O kit de resiliência | 0016 a 0017 | Orçamentos de timeout, retries com backoff e jitter, tempestades de retries, circuit breakers, load shedding, backpressure | Consegue explicar o que fazer depois que um timeout dispara, e associar uma dependência que falha, um servidor sobrecarregado ou uma fila enchendo ao mecanismo certo |
| 11. Observabilidade da falha parcial | 0018 | Spans, traces, propagação através de uma fronteira de rede, tipos de span | Consegue explicar como um trace liga os spans de uma requisição entre serviços, e por que a propagação precisa acontecer explicitamente em cada salto |
| 12. Verificando uma afirmação | 0019 | Os testes opaque-box verificados por modelo do Jepsen, a injeção de falhas em produção da chaos engineering, a reprodutibilidade da simulação determinística | Consegue explicar qual trade-off cada técnica de verificação faz, e o que um dado resultado de teste prova e não prova |

## Lições

Siga estas na ordem.

| # | Lição | Ensina |
|---|---|---|
| [0001](lessons/0001-partial-failure.md) | Falha parcial | O único problema ao qual todo tópico posterior desta trilha responde |
| [0002](lessons/0002-clocks-and-ordering.md) | Relógios e ordenação | Por que não se pode confiar em timestamps de relógio de parede de máquinas diferentes para ordenar eventos, e como um relógio lógico os ordena sem precisar de tempo sincronizado |
| [0003](lessons/0003-timeouts-as-failure-detectors.md) | Timeouts como detectores de falha | Por que todo detector de falha prático é construído sobre um timeout, e o vocabulário formal para o trade-off entre precisão e velocidade que decorre disso |
| [0004](lessons/0004-the-cap-theorem-precisely.md) | O teorema CAP, com precisão | O que o CAP de fato prova, por que a tolerância a partições nunca foi opcional e as leituras equivocadas específicas que tornam "escolha dois" a maneira errada de enunciá-lo |
| [0005](lessons/0005-linearizability.md) | Linearizabilidade | O que a linearizabilidade de fato garante, por que é o modelo de consistência comum mais forte e quanto custa oferecê-la durante uma partição |
| [0006](lessons/0006-sequential-and-eventual-consistency.md) | Consistência sequencial e eventual | Dois modelos mais fracos que a linearizabilidade, o que cada um ainda garante e como escolher entre os três para um design declarado |
| [0007](lessons/0007-what-consensus-is-for.md) | Para que serve o consenso | O problema da máquina de estados replicada que os protocolos de consenso resolvem, e por que ele é o mecanismo por baixo da coordenação de um sistema linearizável |
| [0008](lessons/0008-raft-leader-election-and-log-replication.md) | Raft, eleição de líder e replicação de log | Como o Raft elege um único líder e replica um log através dele, os dois mecanismos que transformam o problema da máquina de estados replicada em algo concreto |
| [0009](lessons/0009-what-consensus-costs.md) | Quanto custa o consenso | Por que toda escrita paga uma ida e volta até uma maioria, por que uma partição minoritária perde disponibilidade em vez de consistência e como pesar esse custo contra o que o consenso compra |
| [0010](lessons/0010-diagnosing-a-production-incident.md) | Diagnosticando um incidente de produção | Aplicar falha parcial, detecção de falhas, modelos de consistência e consenso para nomear o mecanismo por trás de um incidente real, em vez de raciocinar sobre "a rede" ou "a consistência" no abstrato |
| [0011](lessons/0011-replication-and-quorums.md) | Replicação e quóruns | Um protocolo de consenso não é a única forma de replicar dados, e a condição de quórum por trás da sua alternativa mais barata é uma única garantia de sobreposição, e não uma noção vaga de acordo da maioria |
| [0012](lessons/0012-partitioning-and-sharding.md) | Particionamento e sharding | O consistent hashing existe porque o particionamento ingênuo por hash-mod-N remapeia quase tudo no momento em que um nó entra ou sai, e mesmo o consistent hashing precisa de nós virtuais antes de parar de despejar toda a carga de um nó que falhou sobre um único vizinho azarado |
| [0013](lessons/0013-conflict-resolution-under-eventual-consistency.md) | Resolução de conflitos sob consistência eventual | Detectar que duas escritas foram concorrentes e decidir o que fazer a respeito são dois problemas diferentes, e o last-write-wins não resolve nenhum dos dois, ele apenas escolhe um sobrevivente e joga o perdedor fora |
| [0014](lessons/0014-two-phase-commit-and-sagas.md) | Two-phase commit e sagas | O two-phase commit parece consenso (um coordenador, uma votação, um commit), mas resolve um problema diferente e paga um preço pior por isso, bloqueando para sempre se o coordenador morre no meio da votação, e é exatamente por isso que os sistemas de produção recorrem a sagas |
| [0015](lessons/0015-the-transactional-outbox-and-idempotent-consumers.md) | O transactional outbox e consumidores idempotentes | Atualizar um banco de dados e publicar um evento não podem acontecer ambos de forma atômica sem uma transação distribuída, então o padrão outbox contorna isso inteiramente escrevendo o evento como uma linha comum na mesma transação local, e paga por isso com uma mensagem que pode ser enviada duas vezes |
| [0016](lessons/0016-timeouts-retries-and-backoff.md) | Timeouts, retries e backoff | A lição 3 estabeleceu que um timeout é o único sinal de falha disponível, mas disparar um e fazer retry imediatamente é exatamente o que transforma o dia ruim de um serviço em recuperação em um amontoado de requisições, que é o problema específico que backoff e jitter existem para evitar |
| [0017](lessons/0017-circuit-breakers-load-shedding-and-backpressure.md) | Circuit breakers, load shedding e backpressure | Um retry com backoff e jitter ainda pressupõe que vale a pena tentar a chamada que falha, e circuit breaker, load shedding e backpressure são as três respostas para quando deixa de valer, voltadas respectivamente a uma dependência que falha, a um servidor sobrecarregado e a uma fila sobrecarregada |
| [0018](lessons/0018-distributed-tracing-and-correlation.md) | Tracing distribuído e correlação | Todo mecanismo que esta trilha cobriu até aqui diz o que um sistema faz sob falha, mas nenhum diz qual salto de uma requisição específica de fato falhou, que é a única coisa que um trace é construído para responder |
| [0019](lessons/0019-verifying-a-claim.md) | Verificando uma afirmação | Jepsen, chaos engineering e simulação determinística tentam todos encontrar um bug real antes que um cliente o encontre, mas fazem trocas opostas entre realismo e reprodutibilidade para chegar lá, e saber qual é qual é o que diz o que um dado teste de fato provou |

## Referência

- [Glossário](GLOSSARY.md): termos canônicos deste tópico
- [Recursos](RESOURCES.md): fontes confiáveis
- [Tempo e ordem](reference/time-and-order.md): o que o happens-before consegue e não consegue decidir, o que um relógio de Lamport se recusa a dizer e o vocabulário de detectores de falha do qual um timeout é uma instância
- [Modelos de consistência](reference/consistency-models.md): o CAP enunciado como foi provado, os modelos lado a lado com o que cada um garante e quais deles conseguem sequer responder durante uma partição
- [Consenso](reference/consensus.md): o problema da máquina de estados replicada, as cinco propriedades de segurança do Raft e as regras que as produzem, e quanto uma maioria custa nas escritas e nas leituras
- [Diagnóstico de incidentes](reference/diagnosing-incidents.md): quatro perguntas em ordem, o vocabulário nomeado de anomalias para descrever um sintoma com precisão e uma tabela de sintoma para mecanismo indexada às folhas acima

## Como isto funciona

Cada lição é curta e autocontida. Os gabaritos ficam recolhidos: primeiro lembre, depois abra. A prática no mundo real importa mais do que a leitura, e espaçá-la é o ponto. Tudo o que ainda estiver confuso no fim de uma lição vale ser perseguido até a fonte primária antes de seguir adiante.
