---
title: Sistemas distribuidos
description: "Razona sobre el fallo parcial: lo que una red te puede hacer, qué consistencia estás comprando de verdad y por qué el consenso es caro"
type: topic
---

# Aprendizaje: Sistemas distribuidos

Sé capaz de elegir y defender un modelo de consistencia para un sistema que estás diseñando, y de razonar sobre un incidente de producción causado por un fallo parcial en lugar de tratar la red como fiable.

**Última lección:** [19. Verificar una afirmación](lessons/0019-verifying-a-claim.md)

## Cómo se ve el éxito

- Dado un diseño de sistema, elegir un modelo de consistencia y defender el compromiso frente a las alternativas.
- Dado un incidente causado por un fallo parcial (una partición de red, un nodo lento confundido con uno muerto), nombrar el mecanismo responsable.
- Explicar lo que te da un protocolo de consenso y por qué cuesta lo que cuesta, sin necesidad de demostrar su corrección desde los primeros principios.

## Restricciones

- Se asume experiencia profesional construyendo un servicio en red; no se requiere estudio formal previo de sistemas distribuidos.
- Énfasis práctico y operativo: el costo y los compromisos importan más que una demostración formal de la corrección de un protocolo.

## Fuera de alcance

- La concurrencia dentro de un proceso (goroutines, hilos, `Send`/`Sync`): corresponde a los espacios de trabajo de cada lenguaje. Este espacio de trabajo empieza donde se cruza el límite del proceso.
- Ejecutar cargas de trabajo en un orquestador de clústeres: corresponde a [`infrastructure/kubernetes`](../../infrastructure/kubernetes/), que enseña lo que significan en la práctica etcd y la reconciliación y enlaza aquí para la teoría.
- El procesamiento de streams sobre un log: corresponde a [`data/stream-processing`](../../data/stream-processing/), que enseña lo que la recuperación de los state stores y el rebalanceo cambian para una aplicación de Kafka Streams y enlaza aquí para la teoría.

## El arco

Doce etapas, del fallo parcial a un incidente diagnosticado y a los mecanismos que los sistemas de producción usan realmente para sobrevivir a uno, y cómo verificar que algo de eso se cumple de verdad. Una etapa abarca varias lecciones y los límites son difusos; lo que da una etapa por terminada es la capacidad, no el número de lecciones.

| Etapa | Lecciones | Cubre | Terminada cuando |
|---|---|---|---|
| 1. Fallo parcial | 0001 | El único problema al que responden todos los temas posteriores de este espacio de trabajo | Puedes explicar por qué una red no se puede tratar como fiable |
| 2. Tiempo y orden | 0002 a 0003 | Relojes, orden, por qué un timeout es la única señal de fallo disponible | Puedes explicar por qué un timeout no puede distinguir un nodo lento de uno muerto |
| 3. Modelos de consistencia | 0004 a 0006 | CAP, linealizabilidad, consistencia secuencial y eventual | Puedes elegir y defender un modelo de consistencia para un diseño planteado |
| 4. Consenso | 0007 a 0009 | Raft, elección de líder, lo que da el consenso y por qué cuesta lo que cuesta | Puedes explicar lo que da y lo que cuesta un protocolo de consenso sin demostrar su corrección |
| 5. Diagnosticar incidentes | 0010 | Aplicar los mecanismos anteriores a un incidente de producción real | Dado un incidente causado por un fallo parcial, puedes nombrar el mecanismo responsable |
| 6. Replicación y quórums | 0011 | Replicación con líder frente a sin líder, quórums de lectura/escritura, la condición `R + W > N` | Puedes explicar cómo un quórum garantiza que una lectura vea la última escritura, y elegir R y W para una carga de trabajo planteada |
| 7. Particionado y sharding | 0012 | Hashing consistente, nodos virtuales, replicación de claves calientes, enrutamiento de peticiones | Puedes explicar por qué el hashing consistente acota el costo de un redimensionamiento, y lo que un anillo desnudo todavía necesita para manejar fallos y claves calientes |
| 8. Resolución de conflictos con consistencia eventual | 0013 | Last-write-wins y lo que pierde, vectores de versión, CRDT | Puedes distinguir detectar un conflicto de resolverlo, y explicar cómo un CRDT fusiona sin pérdida |
| 9. Transacciones entre servicios | 0014 a 0015 | Two-phase commit y su modo de fallo bloqueante, sagas y compensación, el transactional outbox, consumidores idempotentes | Puedes explicar por qué 2PC se bloquea, a qué renuncia una saga para evitarlo y cómo el patrón outbox evita el problema de la doble escritura |
| 10. La caja de herramientas de resiliencia | 0016 a 0017 | Presupuestos de timeout, reintentos con backoff y jitter, tormentas de reintentos, circuit breakers, load shedding, backpressure | Puedes explicar qué hacer después de que salte un timeout, y asociar una dependencia que falla, un servidor sobrecargado o una cola que se llena con el mecanismo adecuado |
| 11. Observabilidad del fallo parcial | 0018 | Spans, trazas, propagación a través de un límite de red, tipos de span | Puedes explicar cómo una traza une los spans de una petición entre servicios, y por qué la propagación tiene que hacerse explícitamente en cada salto |
| 12. Verificar una afirmación | 0019 | Las pruebas de caja opaca con verificación de modelos de Jepsen, la inyección de fallos en producción de la ingeniería del caos, la reproducibilidad de la simulación determinista | Puedes explicar qué compromiso hace cada técnica de verificación, y qué demuestra y qué no un resultado de prueba dado |

## Lecciones

Recórrelas en orden.

| # | Lección | Enseña |
|---|---|---|
| [0001](lessons/0001-partial-failure.md) | Fallo parcial | El único problema al que responden todos los temas posteriores de este espacio de trabajo |
| [0002](lessons/0002-clocks-and-ordering.md) | Relojes y orden | Por qué no se puede confiar en las marcas de tiempo de reloj de pared de máquinas distintas para ordenar eventos, y cómo un reloj lógico los ordena sin necesitar tiempo sincronizado |
| [0003](lessons/0003-timeouts-as-failure-detectors.md) | Timeouts como detectores de fallos | Por qué todo detector de fallos práctico se construye sobre un timeout, y el vocabulario formal del compromiso entre precisión y velocidad que se deriva de ello |
| [0004](lessons/0004-the-cap-theorem-precisely.md) | El teorema CAP, con precisión | Lo que CAP demuestra realmente, por qué la tolerancia a particiones nunca fue opcional y las malas lecturas concretas que hacen de "elige dos" la forma equivocada de enunciarlo |
| [0005](lessons/0005-linearizability.md) | Linealizabilidad | Lo que garantiza realmente la linealizabilidad, por qué es el modelo de consistencia habitual más fuerte y lo que cuesta proporcionarla durante una partición |
| [0006](lessons/0006-sequential-and-eventual-consistency.md) | Consistencia secuencial y eventual | Dos modelos más débiles que la linealizabilidad, lo que cada uno sigue garantizando y cómo elegir entre los tres para un diseño planteado |
| [0007](lessons/0007-what-consensus-is-for.md) | Para qué sirve el consenso | El problema de la máquina de estados replicada que resuelven los protocolos de consenso, y por qué es el mecanismo que hay debajo de la coordinación de un sistema linealizable |
| [0008](lessons/0008-raft-leader-election-and-log-replication.md) | Raft, elección de líder y replicación del log | Cómo Raft elige un único líder y replica un log a través de él, los dos mecanismos que convierten el problema de la máquina de estados replicada en algo concreto |
| [0009](lessons/0009-what-consensus-costs.md) | Lo que cuesta el consenso | Por qué cada escritura paga un viaje de ida y vuelta a una mayoría, por qué una partición minoritaria pierde disponibilidad en lugar de consistencia y cómo sopesar ese costo frente a lo que da el consenso |
| [0010](lessons/0010-diagnosing-a-production-incident.md) | Diagnosticar un incidente de producción | Aplicar el fallo parcial, la detección de fallos, los modelos de consistencia y el consenso para nombrar el mecanismo que hay detrás de un incidente real, en lugar de razonar sobre "la red" o "la consistencia" en abstracto |
| [0011](lessons/0011-replication-and-quorums.md) | Replicación y quórums | Un protocolo de consenso no es la única forma de replicar datos, y la condición de quórum que hay detrás de su alternativa más barata es una única garantía de solapamiento, no una vaga noción de acuerdo mayoritario |
| [0012](lessons/0012-partitioning-and-sharding.md) | Particionado y sharding | El hashing consistente existe porque el particionado ingenuo con hash módulo N reubica casi todo en cuanto un nodo entra o sale, e incluso el hashing consistente necesita nodos virtuales antes de dejar de volcar toda la carga de un nodo caído sobre un único vecino desafortunado |
| [0013](lessons/0013-conflict-resolution-under-eventual-consistency.md) | Resolución de conflictos con consistencia eventual | Detectar que dos escrituras fueron concurrentes y decidir qué hacer al respecto son dos problemas distintos, y last-write-wins no resuelve ninguno: solo elige a un superviviente y descarta al perdedor |
| [0014](lessons/0014-two-phase-commit-and-sagas.md) | Two-phase commit y sagas | Two-phase commit parece consenso (un coordinador, una votación, un commit), pero resuelve un problema distinto y paga un precio peor por ello, bloqueándose para siempre si el coordinador muere a mitad de la votación, que es exactamente por lo que los sistemas de producción recurren a las sagas |
| [0015](lessons/0015-the-transactional-outbox-and-idempotent-consumers.md) | El transactional outbox y los consumidores idempotentes | Actualizar una base de datos y publicar un evento no pueden ocurrir ambos de forma atómica sin una transacción distribuida, así que el patrón outbox esquiva eso por completo escribiendo el evento como una fila corriente en la misma transacción local, y lo paga con un mensaje que podría enviarse dos veces |
| [0016](lessons/0016-timeouts-retries-and-backoff.md) | Timeouts, reintentos y backoff | La lección 3 estableció que un timeout es la única señal de fallo disponible, pero dispararlo y reintentar de inmediato es exactamente lo que convierte el mal día de un servicio que se está recuperando en una avalancha, que es el problema concreto que el backoff y el jitter existen para evitar |
| [0017](lessons/0017-circuit-breakers-load-shedding-and-backpressure.md) | Circuit breakers, load shedding y backpressure | Un reintento con backoff y jitter sigue asumiendo que vale la pena intentar la llamada que falla, y un circuit breaker, el load shedding y el backpressure son las tres respuestas para cuando deja de valer la pena, dirigidas respectivamente a una dependencia que falla, a un servidor sobrecargado y a una cola desbordada |
| [0018](lessons/0018-distributed-tracing-and-correlation.md) | Trazado distribuido y correlación | Todos los mecanismos que este espacio de trabajo ha cubierto hasta ahora te dicen qué hace un sistema ante un fallo, pero ninguno te dice qué salto de una petición concreta falló realmente, que es lo único que una traza está construida para responder |
| [0019](lessons/0019-verifying-a-claim.md) | Verificar una afirmación | Jepsen, la ingeniería del caos y la simulación determinista intentan encontrar un bug real antes de que lo haga un cliente, pero hacen compromisos opuestos entre realismo y reproducibilidad para lograrlo, y saber cuál es cuál es lo que te dice qué demostró realmente una prueba dada |

## Referencia

- [Glosario](GLOSSARY.md): términos canónicos de este tema
- [Recursos](RESOURCES.md): fuentes de confianza
- [Tiempo y orden](reference/time-and-order.md): lo que happens-before puede y no puede decidir, lo que un reloj de Lamport se niega a decirte y el vocabulario de detectores de fallos del que un timeout es una instancia
- [Modelos de consistencia](reference/consistency-models.md): CAP enunciado tal como se demostró, los modelos lado a lado con lo que garantiza cada uno y cuáles de ellos pueden responder siquiera durante una partición
- [Consenso](reference/consensus.md): el problema de la máquina de estados replicada, las cinco propiedades de seguridad de Raft y las reglas que las producen, y lo que cuesta una mayoría en escrituras y en lecturas
- [Diagnosticar incidentes](reference/diagnosing-incidents.md): cuatro preguntas en orden, el vocabulario de anomalías con nombre para describir un síntoma con precisión y una tabla de síntoma a mecanismo indexada a las hojas anteriores

## Cómo funciona

Cada lección es corta y autocontenida. Las claves de respuesta están plegadas: primero recuerda, luego ábrelas. Las prácticas en el mundo real importan más que la lectura, y espaciarlas es el punto. Todo lo que siga sin estar claro al final de una lección merece rastrearse hasta su fuente primaria antes de seguir.
