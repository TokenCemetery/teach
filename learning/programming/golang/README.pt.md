---
title: Go
description: "Seja o dono de Go em um time: projete, entregue e opere um serviço de produção"
type: topic
---

# Aprendizado: Go

Torne-se o engenheiro em quem o time confia para ser dono de Go: capaz de projetar, entregar e operar um serviço Go de produção, de revisar o Go de outra pessoa e nomear concretamente por que um design está errado, e de reconhecer quando um design importado de outra linguagem está brigando com Go em vez de usá-lo.

**Última lição:** [0041. Testando contra um banco de dados real](lessons/0041-testing-against-a-real-database.md)

## O sucesso se parece com isto

- Projetar e entregar um serviço de produção: configuração, logging estruturado, encerramento gracioso, health checks, acesso a banco de dados.
- Depurar uma data race e um vazamento de goroutine em código que você não escreveu, usando `-race` e `pprof`.
- Revisar o PR de um colega e dizer com precisão por que uma interface, um pointer receiver ou um channel é a ferramenta errada ali.
- Prever o que um programa concorrente faz antes de rodá-lo, a partir do scheduler e do modelo de memória, e não de experimentação.
- Cortar alocações com evidências do `pprof` e do `benchstat`, e não no chute.
- Projetar a API de um pacote que você consiga manter retrocompatível, e saber quando *não* recorrer a uma goroutine.

## Restrições

- Não exige conhecimento prévio de Go. Experiência em outra linguagem encurta as primeiras etapas mas não é obrigatória, e traz hábitos que Go pune em silêncio, porque um instinto errado aqui ainda compila.
- Precisa apenas da toolchain padrão em qualquer sistema operacional suportado. Nada até a etapa 5 exige ferramentas pagas, conta de nuvem ou uma segunda máquina.
- As práticas são programas pequenos que cabem em uma sessão. Espaçá-las ao longo de dias é o mecanismo, e não um incômodo.
- Material sensível a versão envelhece rápido. Afirmações sobre o release atual são verificadas contra as release notes, e não contra livros.

## Fora do escopo

- Outras linguagens como assuntos próprios. Comparações aparecem só onde impedem que um hábito seja levado para Go.
- Frameworks de terceiros como assuntos próprios: routers, ORMs, contêineres de injeção de dependência, toolkits de CLI. A biblioteca padrão cobre diretamente roteamento, logging estruturado e acesso a banco de dados, então as lições se apoiam nela; onde um time já escolheu um framework, julgar se ele merece seu lugar é uma habilidade de revisão e pertence à etapa 6.
- Alvos de frontend, WASM e mobile.
- Kubernetes e infraestrutura além do que um serviço Go precisa para rodar. Colocar o binário em uma imagem de contêiner, e executar, proteger e depurar esse contêiner, é [`infrastructure/containers`](../../infrastructure/containers/). Rodá-lo em um cluster, incluindo o que o cluster faz com seus health checks e seu sinal de encerramento, é [`infrastructure/kubernetes`](../../infrastructure/kubernetes/).
- Internos do compilador e do runtime além do ponto em que deixam de prever o comportamento do programa.

## O arco

Sete etapas, do zero ao nível sênior. Não é uma lista de lições: uma etapa leva várias lições e as fronteiras são flexíveis.

| Etapa | Lições | Cobre | Concluída quando |
|---|---|---|---|
| 1. Fundamentos | 0001 a 0007 | Tipos, zero values, semântica de valor contra ponteiro, mecânica de slices e maps incluindo aliasing, strings contra runes contra bytes, básico de pacotes | Consegue prever aliasing e o comportamento de cópia sem rodar o código |
| 2. Idioma | 0008 a 0014 | Erros como valores, wrapping com `%w`, `errors.Is`/`As`, satisfação implícita de interfaces, interfaces pequenas, struct embedding, layout e nomenclatura de pacotes | Escreve Go que um revisor não descreveria como "Java com sintaxe de Go" |
| 3. Concorrência | 0015 a 0021 | Goroutines, channels, `select`, primitivas de `sync`, cancelamento com `context`, `errgroup`, o race detector, o modelo de memória, padrões de vazamento | Consegue encontrar um vazamento e uma race em código desconhecido e explicar a garantia que foi violada |
| 4. Produção | 0022 a 0027 | Serviços HTTP, configuração, `slog`, encerramento gracioso, health checks, acesso a banco de dados, generics onde se pagam | Estruturou um serviço que sobrevive a ser operado; a etapa 7 o completa com métricas, tracing e testes em torno dos handlers e do banco de dados, e não só em torno de funções |
| 5. Desempenho e ferramentas | 0028 a 0033 | Testes table-driven, fuzzing, benchmarks, `pprof`, escape analysis, redução de alocações, módulos e versionamento, builds de release | Otimiza a partir de um profile e prova o ganho com `benchstat` |
| 6. Julgamento | 0034 a 0037 | Design de API e compatibilidade, quando *não* usar uma goroutine, revisão, ler o código-fonte da stdlib em busca de respostas | Tem a confiança para tomar a decisão e explicá-la a outra pessoa |
| 7. Observabilidade e testes em produção | 0038 a 0041 | Middleware e valores com escopo de requisição, métricas e tracing (RED/USE, OpenTelemetry), testar um handler HTTP, testes de integração contra um banco de dados real | Entrega um serviço com o terceiro e o quarto sinal que a etapa 4 não chegou a cobrir: métricas, tracing e testes em torno dos handlers e do banco de dados, e não só em torno de funções |

## Lições

Siga estas na ordem.

| # | Lição | Ensina |
|---|---|---|
| [0001](lessons/0001-values-and-the-zero-value.md) | Valores e o zero value | Toda variável declarada já é utilizável, e nil é um valor, e não uma ausência |
| [0002](lessons/0002-value-semantics-and-pointers.md) | Semântica de valor e ponteiros | Toda atribuição e todo argumento são uma cópia, e um ponteiro é como você abre mão disso |
| [0003](lessons/0003-slices-and-the-backing-array.md) | Slices e o array subjacente | Um slice é um cabeçalho de três palavras sobre um array que outra pessoa também pode estar segurando |
| [0004](lessons/0004-maps-and-their-rules.md) | Maps e suas regras | Comma-ok, elementos não endereçáveis, iteração aleatorizada e o erro fatal que um map compartilhado dispara |
| [0005](lessons/0005-strings-bytes-and-runes.md) | Strings, bytes e runes | Uma string é uma sequência imutável de bytes UTF-8, então len não é uma contagem de caracteres e indexar não devolve um caractere |
| [0006](lessons/0006-methods-and-method-sets.md) | Métodos e method sets | O receiver que você escolhe decide quais tipos satisfazem uma interface, e não apenas quem pode mutar |
| [0007](lessons/0007-packages-and-modules.md) | Pacotes e módulos | Um diretório é um pacote, uma letra maiúscula é todo o sistema de visibilidade, e internal é imposto |
| [0008](lessons/0008-errors-are-values.md) | Erros são valores | error é uma interface comum, então falhas são dados que você trata, e não fluxo de controle que escapa |
| [0009](lessons/0009-wrapping-is-and-as.md) | Wrapping, Is e As | %w constrói uma cadeia, Is e As a percorrem, e fazer wrapping é um compromisso de API |
| [0010](lessons/0010-defer-panic-and-recover.md) | defer, panic e recover | Os argumentos congelam na instrução defer, e panic é para bugs, e não para falhas |
| [0011](lessons/0011-implicit-interfaces.md) | Interfaces são satisfeitas implicitamente | Quem consome declara a interface, a implementação nunca a menciona, e ser pequena é o ponto |
| [0012](lessons/0012-the-nil-interface-trap.md) | A armadilha da interface nil | Uma interface guarda um tipo e um valor, então um ponteiro nil dentro dela não é uma interface nil |
| [0013](lessons/0013-embedding-is-not-inheritance.md) | Embedding não é herança | A promoção parece subclasse até que um método embutido se recusa a chamar a sua sobrescrita |
| [0014](lessons/0014-designing-a-package.md) | Projetando um pacote | Doc comments, uma superfície exportada pequena e uma seta de dependência que aponta para um só lado |
| [0015](lessons/0015-goroutines-and-what-they-cost.md) | Goroutines e quanto custam | Baratas o bastante para iniciar milhares, nunca de graça o bastante para iniciar sem um plano para pará-las |
| [0016](lessons/0016-channels.md) | Channels | Sem buffer significa encontro marcado, fechar é um broadcast, e só quem envia pode fechar |
| [0017](lessons/0017-select-and-timeouts.md) | select e timeouts | Esperar por vários channels ao mesmo tempo, escolher aleatoriamente entre os prontos e desativar um case com nil |
| [0018](lessons/0018-context-cancellation.md) | context e cancelamento | Um único valor que leva um deadline e um sinal de parada por toda chamada que ele toca |
| [0019](lessons/0019-sync-primitives.md) | sync e errgroup | Quando compartilhar memória é melhor do que passá-la, e as quatro primitivas que cobrem quase tudo |
| [0020](lessons/0020-memory-model-and-races.md) | O modelo de memória e races | Uma data race é comportamento indefinido, e não um cara ou coroa, e o detector só enxerga o que roda |
| [0021](lessons/0021-goroutine-leaks.md) | Vazamentos de goroutine | Uma goroutine bloqueada para sempre nunca é coletada, e nada do que ela segura também é |
| [0022](lessons/0022-an-http-server.md) | Um servidor HTTP que vale a pena operar | Handlers, padrões de roteamento e os quatro timeouts que o servidor padrão não define |
| [0023](lessons/0023-configuration-and-startup.md) | Configuração e inicialização | Um main que só conecta as peças, uma função run que devolve um erro e validação antes da primeira requisição |
| [0024](lessons/0024-structured-logging-with-slog.md) | Logging estruturado com slog | Atributos chave-valor, um único logger passado como dependência e níveis que você pode mudar sem um deploy |
| [0025](lessons/0025-graceful-shutdown.md) | Encerramento gracioso e saúde | Capturar o sinal, parar de aceitar, drenar o trabalho em andamento e então fechar as dependências em ordem |
| [0026](lessons/0026-talking-to-a-database.md) | Conversando com um banco de dados | sql.DB é um pool, toda chamada recebe um context, e um Rows não fechado segura uma conexão |
| [0027](lessons/0027-generics-that-earn-their-keep.md) | Generics que se pagam | Parâmetros de tipo removem duplicação entre tipos, e uma interface continua sendo a resposta certa para comportamento |
| [0028](lessons/0028-table-driven-tests.md) | Testes table-driven | Uma função de teste, um slice de casos, subtestes que se nomeiam e falham de forma independente |
| [0029](lessons/0029-fuzzing.md) | Fuzzing | Declarar uma propriedade que precisa valer sempre e deixar a toolchain procurar a entrada que a quebra |
| [0030](lessons/0030-benchmarks-you-can-trust.md) | Benchmarks em que dá para confiar | b.Loop, execuções repetidas e benchstat, porque um número de uma única execução não é uma medição |
| [0031](lessons/0031-reading-a-pprof-profile.md) | Lendo um profile do pprof | Descobrir para onde o tempo e a memória realmente vão, antes de mudar uma única linha |
| [0032](lessons/0032-escape-analysis-and-allocation.md) | Escape analysis e alocação | Por que um valor vai parar no heap, como perguntar ao compilador e quais correções realmente compensam |
| [0033](lessons/0033-modules-and-release-builds.md) | Módulos e builds de release | Minimal version selection, a regra do caminho v2 e as flags que tornam um binário reproduzível |
| [0034](lessons/0034-api-design-and-compatibility.md) | Design de API e compatibilidade | O que você pode adicionar sem quebrar quem chama, e as três mudanças que sempre quebram |
| [0035](lessons/0035-when-not-to-use-a-goroutine.md) | Quando não usar uma goroutine | Concorrência é uma estrutura, e não um ganho de velocidade, e a versão sequencial muitas vezes é a resposta certa |
| [0036](lessons/0036-reviewing-go.md) | Revisando Go | Deixe as ferramentas acharem questões de estilo e gaste sua atenção com ciclo de vida, fronteiras e o que o compilador não consegue verificar |
| [0037](lessons/0037-reading-the-standard-library.md) | Lendo a biblioteca padrão | O código-fonte está na sua máquina, resolve discussões que a documentação não resolve, e é a referência de estilo |
| [0038](lessons/0038-middleware-and-request-scoped-values.md) | Middleware e valores com escopo de requisição | A lição 22 mostrou um middleware gravando um valor no context; esta lição é a outra metade, lê-lo de volta com segurança, e o mecanismo de que aquele exemplo nunca precisou, um middleware que decide nem chamar o próximo handler |
| [0039](lessons/0039-metrics-and-tracing.md) | Métricas e tracing | O pprof faz o profile da CPU e da memória de um único processo localmente; métricas e tracing são os dois sinais de produção que respondem a um par diferente de perguntas, como o serviço está agora no agregado e o que aconteceu com esta requisição específica em cada serviço que ela tocou |
| [0040](lessons/0040-testing-an-http-handler.md) | Testando um handler HTTP | A lição 22 mencionou de passagem que um ResponseRecorder torna um handler testável sem rede; esta lição torna essa afirmação concreta, mostra por que a costura da interface é o que torna isso possível, e apresenta a ferramenta diferente, e fácil de confundir, para testar um cliente em vez de um handler |
| [0041](lessons/0041-testing-against-a-real-database.md) | Testando contra um banco de dados real | Este é o fechamento da etapa 7: testing.Short() tira um teste lento de banco de dados do loop local rápido, uma transação iniciada e nunca confirmada dá a cada teste uma base limpa e isolada, e um teste de integração finalmente exercita juntos um middleware, um handler e um banco de dados real |

## Referência

- [Glossário](GLOSSARY.md): termos canônicos deste tópico
- [Recursos](RESOURCES.md): fontes confiáveis, cada uma anotada com o que cobre
- [Slices e maps](reference/slice-and-map-mechanics.md): aliasing, capacidade e as operações que causam panic
- [Tratamento de erros](reference/error-handling.md): verbos de wrapping, funções de comparação e as armadilhas que compilam
- [Padrões de concorrência](reference/concurrency-patterns.md): regras de channels, construtores de context, checklist de vazamentos
- [Comandos da toolchain](reference/toolchain-commands.md): flags de teste, benchmark, profile e build de release
- [Checklist de revisão](reference/review-checklist.md): o que as ferramentas pegam e o que cabe a você pegar

## Como isto funciona

Cada lição é curta e autocontida. Os gabaritos ficam recolhidos: primeiro lembre, depois abra. A prática no mundo real importa mais do que a leitura, e espaçá-la é o ponto. Tudo o que ainda estiver confuso no fim de uma lição vale ser perseguido até a fonte primária antes de seguir adiante.
