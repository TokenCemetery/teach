---
title: Design de APIs
description: "Projete uma interface da qual outros dependem: o contrato, os seus erros e como ele muda sem quebrá-los"
type: topic
---

# Aprendizado: Design de APIs

Seja capaz de projetar do zero uma API pública versionada (REST/HTTP ou gRPC) e de evoluir uma existente, mudando o seu contrato sem quebrar os clientes que dependem dele.

**Última lição:** [19. Onde o GraphQL se encaixa](lessons/0019-where-graphql-fits.md)

## O sucesso se parece com isto

- Projetar o contrato de uma API REST/HTTP ou gRPC, incluindo o seu modelo de erros, para um caso de uso declarado.
- Evoluir o contrato de uma API existente (adicionando, depreciando ou mudando um campo ou endpoint) sem quebrar clientes, e explicar a estratégia de versionamento ou de migração usada.
- Tratar autenticação, autorização e rate limiting como parte do contrato do qual um cliente depende, e não como algo pensado depois e acoplado à parte.

## Restrições

- Pressupõe experiência profissional construindo um serviço com HTTP ou RPC; não exige estudo formal prévio de design de APIs.
- Cobre tanto REST/HTTP quanto gRPC, já que as garantias da missão valem para ambos.

## Fora do escopo

- Fazer o compilador rejeitar um estado impossível dentro de uma única base de código: veja [`programming/typescript`](../../programming/typescript/) para essa fronteira. Esta trilha é o mesmo instinto aplicado através de uma fronteira em que não há um compilador compartilhado.

## O arco

Doze etapas, do contrato à entrega assíncrona e à verificação do próprio contrato contra o comportamento real. Uma etapa leva várias lições e as fronteiras são flexíveis; o que torna uma etapa concluída é a capacidade, não a contagem de lições.

| Etapa | Lições | Cobre | Concluída quando |
|---|---|---|---|
| 1. O contrato | 0001 | Aquilo em que um cliente pode confiar é maior do que o que está documentado (Lei de Hyrum) | Consegue nomear a superfície implícita de um contrato além da documentada |
| 2. Modelos de erro | 0002 a 0003 | Códigos de status HTTP, RFC 9457 Problem Details, códigos de status do gRPC | Consegue projetar um modelo de erros para uma API declarada |
| 3. Design REST/HTTP | 0004 a 0005 | Modelagem de recursos, paginação e filtragem, orientações no estilo AIP | Consegue projetar um contrato REST para um caso de uso declarado |
| 4. Design gRPC | 0006 a 0007 | proto3, design de serviços, streaming | Consegue projetar um contrato gRPC para o mesmo caso de uso |
| 5. Versionamento e evolução | 0008 a 0009 | Mudanças aditivas, depreciação, estratégia de migração | Consegue evoluir o contrato de uma API existente sem quebrar os seus clientes |
| 6. Autenticação, autorização e rate limiting como contrato | 0010 | Tratá-los como parte do que um cliente depende, e não como algo pensado depois | Consegue projetar autenticação e rate limiting como contrato, e não acoplados à parte |
| 7. Idempotência e retries seguros | 0011 | O header `Idempotency-Key`, fingerprints de idempotência e a distinção entre retry e requisição concorrente | Consegue projetar um mecanismo de idempotência que torna um método não idempotente genuinamente seguro para retry |
| 8. Caching HTTP como contrato | 0012 | `ETag`, validadores fracos contra fortes, requisições condicionais, concorrência otimista com `If-Match`, `Cache-Control` | Consegue projetar um contrato de caching e de controle de concorrência, e sabe qual força de comparação cada header condicional exige |
| 9. Operações de longa duração e entrega assíncrona | 0013 a 0014 | O recurso de operação e o polling, assinatura de webhooks, retries e ordenação | Consegue projetar um contrato assíncrono (operação consultada por polling ou webhook enviado) e as suas garantias de falha, retry e ordenação |
| 10. Operações em lote e respostas parciais | 0015 | Métodos em lote atômicos contra de sucesso parcial, relato de erros por item, field masks | Consegue projetar a semântica de falha de um método em lote e um contrato de resposta parcial |
| 11. O contrato legível por máquina | 0016 a 0017 | Documentos OpenAPI e arquivos `.proto` como artefatos gerados, detecção de breaking changes com Buf, Spectral e oasdiff | Consegue explicar o que um contrato legível por máquina possibilita, e como um linter de estilo difere de um detector de breaking changes |
| 12. Testes de contrato e o lugar do GraphQL | 0018 a 0019 | Testes de contrato orientados ao consumidor e `can-i-deploy`, e onde o GraphQL fica em relação a REST e gRPC | Consegue explicar como um teste de contrato verifica o comportamento real além de um schema, e situar com precisão a evolução sem versões do GraphQL frente ao material de REST/gRPC deste arco |

## Lições

Siga estas na ordem.

| # | Lição | Ensina |
|---|---|---|
| [0001](lessons/0001-the-contract.md) | O contrato | Aquilo em que um cliente pode confiar é maior do que o que você documentou, e o design precisa levar ambos em conta |
| [0002](lessons/0002-http-status-codes-and-error-semantics.md) | Códigos de status HTTP e semântica de erros | O que um código de status realmente promete a um cliente sobre segurança, idempotência e o que fazer em seguida, além do agrupamento vago em 2xx/4xx/5xx |
| [0003](lessons/0003-problem-details-and-grpc-status-codes.md) | RFC 9457 Problem Details e códigos de status do gRPC | Um formato de erro estruturado e legível por máquina para HTTP, o vocabulário paralelo de códigos de status do gRPC e o design de um único modelo de erros que funcione nos dois |
| [0004](lessons/0004-resource-modeling-for-rest.md) | Modelagem de recursos para REST | Por que REST modela uma API em torno de substantivos e estado, e não de verbos, e como uma hierarquia de recursos molda o que uma URL significa |
| [0005](lessons/0005-pagination-and-filtering.md) | Paginação, filtragem e o design de um contrato REST | Por que a paginação baseada em cursor vence os offsets em escala, como a filtragem continua sendo um contrato estável, e juntar a modelagem de recursos em um design REST completo |
| [0006](lessons/0006-proto3-and-grpc-service-design.md) | Proto3 e design de serviços gRPC | Como os números de campo do proto3, e não os nomes de campo, são o verdadeiro contrato na rede, e como um serviço gRPC é estruturado em torno de métodos RPC e não de recursos |
| [0007](lessons/0007-grpc-streaming.md) | Streaming no gRPC e o design do mesmo caso de uso | Os quatro tipos de RPC do gRPC, quando cada um se encaixa, e projetar um mesmo caso de uso como contrato REST e como contrato gRPC |
| [0008](lessons/0008-additive-changes-and-deprecation.md) | Mudanças aditivas e depreciação | Por que adicionar costuma ser seguro e remover ou mudar o significado costuma não ser, e como depreciar um campo ou endpoint sem quebrar os clientes na hora |
| [0009](lessons/0009-versioning-and-migration-strategy.md) | Versionamento e estratégia de migração | Como lançar uma breaking change genuína sem quebrar todas as integrações existentes de uma vez, usando a estratégia de versionamento da Stripe como exemplo resolvido |
| [0010](lessons/0010-auth-authz-and-rate-limiting-as-contract.md) | Autenticação, autorização e rate limiting como contrato | Por que scopes, e não apenas tokens, e um estado visível de rate limit, e não apenas um 429, são o que torna o controle de acesso e as cotas parte deliberada do contrato |
| [0011](lessons/0011-idempotency-keys-and-safe-retries.md) | Chaves de idempotência e retries seguros | Uma chave sozinha só deduplica; um fingerprint é o que diz ao servidor se uma chave repetida é a mesma requisição em retry ou uma diferente reutilizando-a por engano, e um retry que chega enquanto a original ainda está em execução recebe um conflito, e não um replay |
| [0012](lessons/0012-http-caching-as-contract.md) | Caching HTTP como contrato | O mesmo validador ETag serve a dois trabalhos diferentes conforme a comparação de que precisa: a comparação fraca basta para pular um download redundante, mas só a comparação forte é segura para detectar a escrita concorrente de outra pessoa |
| [0013](lessons/0013-the-operation-resource-and-polling.md) | O recurso de operação e o polling | Um método de longa duração devolve um recurso com forma de promessa em vez de bloquear, e uma falha durante a execução é relatada de forma diferente de uma falha que impede a operação de sequer começar |
| [0014](lessons/0014-webhooks-and-callbacks-as-delivery.md) | Webhooks e callbacks como entrega | Enviar uma notificação em vez de esperar ser consultado por polling inverte quem inicia a requisição, e essa inversão é exatamente o motivo pelo qual assinatura, retries e ordenação precisam, cada um, do seu próprio contrato explícito no lado que recebe |
| [0015](lessons/0015-bulk-operations-and-partial-responses.md) | Operações em lote e respostas parciais | Um método em lote precisa escolher de antemão se falha no tudo ou nada ou se relata sucesso e falha por item, e um cliente que pede um subconjunto de campos precisa que esse subconjunto seja solicitado fora do corpo que ele está moldando |
| [0016](lessons/0016-openapi-and-protobuf-as-artifacts.md) | OpenAPI e Protobuf como artefatos | Quando o contrato existe como documento legível por máquina e não apenas como prosa, o próprio documento passa a ser algo a versionar, revisar e a partir do qual gerar outras coisas, em vez de uma descrição escrita depois do fato |
| [0017](lessons/0017-breaking-change-linting.md) | Linting de breaking changes | Um linter que verifica o estilo de um contrato e uma ferramenta de diff que verifica se ele quebrou um cliente respondem a duas perguntas diferentes, e a própria ferramenta de diff precisa receber a pergunta certa entre três |
| [0018](lessons/0018-contract-testing.md) | Testes de contrato | Um artefato de schema verifica a forma e um linter de breaking changes verifica a compatibilidade, mas nenhum dos dois confirma que um provedor se comporta de fato como os testes de um consumidor real esperam, que é o que um teste de contrato verifica, por meio de interações de exemplo gravadas |
| [0019](lessons/0019-where-graphql-fits.md) | Onde o GraphQL se encaixa | O GraphQL resolve o mesmo problema de versionamento ao qual esta trilha dedicou duas lições fazendo de toda requisição já uma field mask, ao custo de um contrato ao qual as ferramentas desta trilha não se aplicam |

## Referência

- [Glossário](GLOSSARY.md): termos canônicos deste tópico
- [Recursos](RESOURCES.md): fontes confiáveis
- [Modelos de erro](reference/error-models.md): códigos de status HTTP, membros do Problem Details e códigos de status do gRPC lado a lado, para quando você está projetando um modelo de erros em vez de aprender por que ele é contrato
- [Design de recursos REST](reference/rest-resource-design.md): nomes de recursos, os métodos padrão e personalizados, paginação e filtragem, com a regra AIP que cada decisão precisa satisfazer
- [Design gRPC](reference/grpc-design.md): números de campo do proto3, quais mudanças de schema são seguras no formato binário e quais quebram o JSON, os quatro tipos de RPC e a semântica de chamada que um contrato gRPC herda
- [Versionamento e evolução](reference/versioning-and-evolution.md): quais mudanças quebram qual tipo de compatibilidade, os headers que tornam uma depreciação visível para as ferramentas e os modelos de versionamento entre os quais escolher
- [Autenticação e rate limiting](reference/auth-and-rate-limiting.md): scopes e grant types como contrato, os códigos de erro que um resource server deve a um cliente e os campos RateLimit que tornam uma cota visível antes de ela ser atingida

## Como isto funciona

Cada lição é curta e autocontida. Os gabaritos ficam recolhidos: primeiro lembre, depois abra. A prática no mundo real importa mais do que a leitura, e espaçá-la é o ponto. Tudo o que ainda estiver confuso no fim de uma lição vale ser perseguido até a fonte primária antes de seguir adiante.
