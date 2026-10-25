---
title: Kafka
description: "Domine o log: partições, consumer groups, garantias de entrega e quanto \"exactly once\" realmente custa"
type: topic
---

# Aprendizado: Kafka

Seja capaz de projetar um layout de tópicos e partições para uma carga de trabalho real e de diagnosticar consumer lag, tempestades de rebalanceamento ou perda inesperada de mensagens, em vez de chutar uma correção.

**Última lição:** [16. As métricas que importam para operar um cluster](lessons/0016-the-metrics-that-matter-for-operating-a-cluster.md)

## O sucesso se parece com isto

- Projetar um layout de tópicos, partições e consumer groups para uma carga de trabalho declarada e defender a escolha de garantia de entrega por trás dele.
- Dado um consumidor que fica para trás ou rebalanceia repetidamente, diagnosticar qual configuração ou padrão de uso é o culpado.
- Dizer quanto "exactly once" realmente custa e quando at-least-once com tratamento idempotente é a melhor troca.

## Restrições

- Não pressupõe experiência prévia com Kafka nem com sistemas de mensageria.
- O Apache Kafka é a implementação de referência; alternativas (Redpanda, serviços gerenciados) não são cobertas.
- Toca brevemente no ecossistema ao redor (Schema Registry, o básico do Kafka Connect), onde as garantias do log sozinhas não explicam como um pipeline real é construído.

## Fora do escopo

- O modelo de falhas por trás das próprias garantias de entrega: veja [`architecture/distributed-systems`](../../architecture/distributed-systems/), referenciado em vez de derivado de novo aqui.
- Kafka Streams e a computação sobre o log (topologias, estado, janelas, joins): veja [`data/stream-processing`](../../data/stream-processing/), que aponta de volta para cá para a semântica de entrega. ksqlDB como tópico por si só.

## O arco

Dez etapas, do log à operação do cluster em produção. Uma etapa leva várias lições e as fronteiras são flexíveis; o que torna uma etapa concluída é a capacidade, não a contagem de lições.

| Etapa | Lições | Cobre | Concluída quando |
|---|---|---|---|
| 1. Partições e o log | 0001 | A unidade em torno da qual todo o resto (ordenação, paralelismo, consumer groups) é construído | Consegue explicar por que uma partição é a unidade de ordenação e de paralelismo |
| 2. Consumer groups e rebalanceamento | 0002 a 0003 | Coordenação de grupos, rebalanceamento cooperativo, consumer lag | Consegue diagnosticar um consumidor que fica para trás ou rebalanceia repetidamente |
| 3. Garantias de entrega | 0004 a 0005 | Semântica at-most/at-least/exactly-once, produtores idempotentes, transações | Consegue defender uma escolha de garantia de entrega e dizer quanto custa o exactly-once |
| 4. Projetando o layout | 0006 a 0007 | Escolha da chave, trade-offs da quantidade de partições, garantias de ordenação | Consegue projetar um layout de tópicos e partições para uma carga de trabalho declarada |
| 5. O ecossistema ao redor | 0008 a 0009 | Schema Registry, o básico do Kafka Connect | Consegue explicar como eles se encaixam em torno do log em um pipeline real |
| 6. Retenção e replicação | 0010 a 0011 | `cleanup.policy`, log compaction, fator de replicação, ISR, `acks`, `min.insync.replicas`, unclean leader election | Consegue defender por quanto tempo os dados de um tópico vivem e qual durabilidade as suas configurações de replicação realmente garantem |
| 7. Configuração de clientes sob carga | 0012 | `batch.size`, `linger.ms`, `fetch.min.bytes`, `max.poll.interval.ms` | Consegue associar um sintoma de throughput, de latência ou de rebalanceamento espúrio à configuração de cliente específica que o resolve |
| 8. Coordenação do cluster | 0013 | KRaft, o quórum de controllers, `process.roles`, o que substituiu o ZooKeeper | Consegue explicar o que o quórum de controllers faz e por que o failover no KRaft não precisa buscar de novo todos os metadados |
| 9. Segurança e multi-tenancy | 0014 a 0015 | TLS, SASL, `security.protocol`, ACLs, negação por padrão, cotas | Consegue nomear qual mecanismo (criptografia, autenticação, autorização ou isolamento de recursos) uma dada questão de segurança realmente envolve |
| 10. Operando o cluster | 0016 | `UnderReplicatedPartitions`, `UnderMinIsr`, folga de disco, latência de requisições, saturação dos request handlers | Consegue nomear a qual das três famílias de sinais um dado sintoma operacional pertence, e fazer a triagem entre broker isolado e cluster inteiro |

## Lições

Siga estas na ordem.

| # | Lição | Ensina |
|---|---|---|
| [0001](lessons/0001-partitions-and-the-log.md) | Partições e o log | A unidade em torno da qual todo o resto desta trilha (ordenação, paralelismo, consumer groups) é construído |
| [0002](lessons/0002-consumer-group-coordination.md) | Coordenação de consumer groups | Como um group coordinator e um group leader dividem as partições entre os consumidores, e como os offsets acompanham o progresso de cada grupo |
| [0003](lessons/0003-cooperative-rebalancing-and-lag.md) | Rebalanceamento cooperativo e diagnóstico de consumer lag | Por que o protocolo de rebalanceamento original causa uma tempestade de rebalanceamentos, como o rebalanceamento cooperativo a reduz, e uma ordem de diagnóstico para o consumer lag |
| [0004](lessons/0004-delivery-semantics.md) | At-most-once, at-least-once e exactly-once | Onde cada garantia de entrega é de fato ganha ou perdida ao longo das etapas de produção, do broker e de consumo do caminho |
| [0005](lessons/0005-idempotent-producers-and-transactions.md) | Produtores idempotentes e transações | Por que a idempotência é quase de graça, mas as transações carregam o custo real do exactly-once |
| [0006](lessons/0006-partition-key-choice.md) | Escolha da chave de partição e garantias de ordenação | Escolher uma chave de partição significa escolher, na mesma decisão, tanto a ordenação que você obtém quanto o paralelismo do qual abre mão |
| [0007](lessons/0007-partition-count-and-topic-layout.md) | Trade-offs da quantidade de partições e o design de um layout de tópicos | Por que mais partições não são de graça, e o que um layout de tópicos totalmente defendido precisa nomear de cada etapa anterior |
| [0008](lessons/0008-schema-registry.md) | Schema Registry | Como pegar uma mudança de schema incompatível no momento da produção substitui uma quebra silenciosa, a jusante, no momento do consumo |
| [0009](lessons/0009-kafka-connect-basics.md) | O básico do Kafka Connect | Como as tasks e os modos de worker do Connect oferecem paralelismo e tolerância a falhas, e por que o Connect não concede nenhuma garantia que a API de produtor ou de consumidor por baixo já não oferecesse |
| [0010](lessons/0010-retention-and-log-compaction.md) | Retenção e log compaction | Por quanto tempo uma mensagem realmente sobrevive em um tópico, e a outra política de limpeza que mantém o histórico de uma chave em vez da sua idade |
| [0011](lessons/0011-replication-isr-acks-and-unclean-leader-election.md) | Replicação, ISR, acks e unclean leader election | O que acks=all realmente espera, o piso que impede que ele signifique em silêncio menos do que parece, e o trade-off quando todas as réplicas em sincronia se foram |
| [0012](lessons/0012-producer-and-consumer-configuration-under-load.md) | Configuração de produtores e consumidores sob carga | Os ajustes do lado do cliente que trocam latência por throughput, e aquele que pode disparar um rebalanceamento para um consumidor que nunca esteve de fato morto |
| [0013](lessons/0013-kraft-and-what-replaced-zookeeper.md) | KRaft e o que substituiu o ZooKeeper | Como o cluster entra em acordo sobre os seus próprios metadados agora que o serviço de coordenação externo se foi, e por que buscar de novo o estado completo no failover era o problema que valia resolver |
| [0014](lessons/0014-tls-and-sasl-authenticating-to-a-cluster.md) | TLS e SASL: autenticando-se em um cluster | Criptografar o canal e autenticar o cliente são dois trabalhos separados que security.protocol combina em uma única configuração, e confundi-los é onde começa a maior parte da confusão |
| [0015](lessons/0015-acls-and-quotas-authorization-and-multi-tenancy.md) | ACLs e cotas: autorização e multi-tenancy | Um principal autenticado ainda não está autorizado a fazer nada até que uma ACL diga que sim, e um principal autorizado a agir ainda não está impedido de privar todos os outros tenants da capacidade do cluster |
| [0016](lessons/0016-the-metrics-that-matter-for-operating-a-cluster.md) | As métricas que importam para operar um cluster | Partições sub-replicadas, folga de disco e latência de requisições são os três sinais que vale observar, e cada um aponta para um tipo diferente de problema |

## Referência

- [Glossário](GLOSSARY.md): termos canônicos deste tópico
- [Recursos](RESOURCES.md): fontes confiáveis
- [Consumer groups e rebalanceamento](reference/consumer-groups-and-rebalancing.md): os dois protocolos de rebalanceamento, os dois timeouts de liveness independentes e uma ordem de diagnóstico para o consumer lag com a configuração que governa cada passo
- [Garantias de entrega](reference/delivery-guarantees.md): qual configuração decide cada etapa do caminho, por que a idempotência pode estar desligada em silêncio e o que um consumidor read_committed realmente espera
- [Design de tópicos e partições](reference/topic-and-partition-design.md): como um registro realmente chega a uma partição, qual ordenação isso compra e não compra, e as duas direções em que a quantidade de partições é cara de mudar
- [Ecossistema](reference/ecosystem.md): os sete tipos de compatibilidade com quem precisa atualizar primeiro em cada um, e o que o Kafka Connect acrescenta em torno do log, incluindo a garantia que vem desligada por padrão

## Como isto funciona

Cada lição é curta e autocontida. Os gabaritos ficam recolhidos: primeiro lembre, depois abra. A prática no mundo real importa mais do que a leitura, e espaçá-la é o ponto. Tudo o que ainda estiver confuso no fim de uma lição vale ser perseguido até a fonte primária antes de seguir adiante.
