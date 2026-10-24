---
title: C#
description: "Domine um serviço em C#: o sistema de tipos, async e o que o CLR faz com o que você escreveu, do zero"
type: topic
---

# Aprendizado: C\#

Torne-se o engenheiro em quem a equipe confia para ser dono de um serviço em C#: capaz de modelar um domínio escolhendo corretamente entre uma struct, uma class e um record, escrever e raciocinar sobre `async`/`await`, consultar e transformar dados com fluência usando LINQ, entregar um backend ASP.NET Core tipado e testado, e explicar o que o CLR faz com o código que você escreveu.

**Última lição:** [45. Empacotamento e versionamento com NuGet](lessons/0045-nuget-packaging-and-versioning.md)

## O sucesso se parece com isto

- Modelar um domínio escolhendo corretamente entre uma struct, uma class e um record, e defender a escolha a partir do comportamento real do CLR.
- Escrever código com `async`/`await` e explicar o que acontece com a execução de um método em cada `await`.
- Consultar e transformar dados com fluência usando LINQ.
- Entregar um serviço de backend ASP.NET Core tipado e testado, projetado de forma idiomática para C#.
- Dado um código C# escrito com um hábito que apenas compila (uma class onde cabe uma struct, um callback em vez de `async`/`await`), nomear o hábito e reescrevê-lo de forma idiomática.

## Restrições

- Não pressupõe C# prévio. Experiência em outra linguagem orientada a objetos (Java, Kotlin) encurta as primeiras etapas, mas não é exigida, e traz hábitos que o C# pune em silêncio: uma class onde cabe uma struct ou um record, um callback onde `async`/`await` se lê melhor.
- Contexto de ASP.NET Core / serviço de backend; não .NET em geral sem esse foco.

## Fora do escopo

- Unity e desenvolvimento de jogos com C#: um contexto diferente o bastante para não ser coberto aqui.
- Internos do JIT, e escrever ou ajustar à mão um garbage collector: a etapa 8 cobre o heap geracional, os modos de GC e o profiling no nível de que o dono de um serviço precisa para medir e defender uma escolha, não no nível de implementar um.
- Imagens de contêiner: colocar um serviço publicado em uma imagem, e executar, proteger e depurar esse contêiner, fica em [`infrastructure/containers`](../../infrastructure/containers/).
- Executar o serviço em um cluster, incluindo o que o Kubernetes faz com suas verificações de liveness e readiness, fica em [`infrastructure/kubernetes`](../../infrastructure/kubernetes/).

## O arco

Onze etapas, do zero ao nível sênior. Não é uma lista de lições: uma etapa leva várias lições e as fronteiras são flexíveis.

| Etapa | Lições | Cobre | Concluída quando |
|---|---|---|---|
| 1. Fundamentos | 0001 a 0006 | Tipos de valor contra tipos de referência (struct contra class), tipos de valor anuláveis, tipos básicos e interpolação de strings, coleções (`List`, `Dictionary`, `IEnumerable`), fluxo de controle, exceções | Consegue prever o comportamento de cópia contra referência sem executar o código |
| 2. Modelagem | 0007 a 0011 | Properties, tipos `record`, pattern matching e switch expressions, interfaces com implementações padrão, generics | Modela um domínio escolhendo o tipo certo em vez de uma class para tudo |
| 3. Idioma | 0012 a 0016 | Extension methods, sintaxe de consulta e de métodos do LINQ, delegates e events, tipos de referência anuláveis, membros com corpo de expressão | Escreve C# que um revisor não descreveria como Java traduzido |
| 4. Async | 0017 a 0021 | O modelo de `Task`, a mecânica de `async`/`await`, composição de `Task`, cancellation tokens, `IAsyncEnumerable` | Consegue explicar o que `await` faz com a execução de um método e prever o comportamento de um programa assíncrono |
| 5. Testes e build | 0022 a 0024 | xUnit/NUnit, mocking, a CLI `dotnet` e o gerenciamento de projetos e pacotes | Outra pessoa consegue clonar, compilar, testar e executar |
| 6. Entregando o serviço | 0025 a 0029 | Roteamento e middleware do ASP.NET Core, injeção de dependência, configuração, o básico do Entity Framework Core, estruturar um backend tipado e testado | Entrega um serviço ASP.NET Core tipado e testado |
| 7. Julgamento | 0030 a 0031 | Comparar `async`/`await` com as virtual threads do Java e o LINQ com a Stream API, revisar C# em busca de um hábito que apenas compila | Tem a confiança para tomar a decisão e explicá-la a outra pessoa |
| 8. O runtime do CLR e desempenho | 0032 a 0037 | O design geracional do managed heap, modos de GC, `Span<T>`/`Memory<T>`, `stackalloc`/`ArrayPool<T>`, medir struct contra class com BenchmarkDotNet, e profiling | Otimiza a partir de um profile e defende o ganho com um benchmark confiável, ligado de volta ao comportamento geracional e de alocação real do CLR |
| 9. Tempo de vida de recursos | 0038 | Implementar `IDisposable` e `IAsyncDisposable`: o dispose pattern, o parâmetro `disposing`, finalizers e `DisposeAsyncCore` | Implementa um dispose pattern correto e idempotente, em vez de apenas consumir um por meio de `using` |
| 10. Operando e protegendo o serviço | 0039 a 0042 | Logging estruturado com `ILogger`, health checks de liveness/readiness, OpenTelemetry, autenticação e autorização, e serialização com `System.Text.Json` | Entrega um serviço que pode ser observado, verificado quanto à saúde, protegido e serializado corretamente, e não apenas compilado |
| 11. Evolução de API e empacotamento | 0043 a 0045 | Compatibilidade binária contra de código-fonte contra comportamental, `[Obsolete]` e depreciação, empacotamento NuGet e versionamento semântico | Classifica com precisão o impacto de compatibilidade de uma mudança e evolui uma API publicada sem quebrar quem a chama de surpresa |

## Lições

Siga estas na ordem.

| # | Lição | Ensina |
|---|---|---|
| [0001](lessons/0001-structs-and-classes.md) | Structs e classes | A escolha de sistema de tipos que o Java nunca te deu, e o que o CLR realmente faz com cada uma |
| [0002](lessons/0002-nullable-value-types.md) | Tipos de valor anuláveis | Por que int? continua sendo um tipo de valor, a regra de comparação que torna as duas direções falsas, e o que o boxing faz com o wrapper |
| [0003](lessons/0003-basic-types-and-string-interpolation.md) | Tipos básicos e interpolação de strings | Palavras-chave como aliases de tipos .NET, por que decimal é embutido em vez de ser uma class, e as regras de largura, formato e efeito colateral do espaço de interpolação |
| [0004](lessons/0004-collections.md) | Coleções | IEnumerable como a abstração em que o resto do arco se apoia, e a consulta ao dicionário que lança exceção onde o map do Java devolve null |
| [0005](lessons/0005-control-flow.md) | Fluxo de controle | Os três lugares em que o fluxo de controle não se transfere do Java: o enumerador com duck typing do foreach, o switch sem fall-through, e o goto como salto legal |
| [0006](lessons/0006-exceptions.md) | Exceções | Exception filters e o stack trace que capturar e relançar destrói, using para limpeza determinística, e o projeto final da etapa 1 |
| [0007](lessons/0007-properties.md) | Properties | Acessores como recurso da linguagem, as três promessas ortogonais de required, init e um tipo não anulável, e properties calculadas sem campo de apoio |
| [0008](lessons/0008-record-types.md) | Tipos record | O que o modificador record realmente gera, por que a igualdade depende do tipo em tempo de execução, e a imutabilidade rasa que uma expressão with não corrige |
| [0009](lessons/0009-pattern-matching.md) | Pattern matching | O vocabulário de padrões, a exaustividade da switch expression e sua única lacuna silenciosa, e por que a ordem dos braços é uma questão de tempo de compilação |
| [0010](lessons/0010-interfaces.md) | Interfaces | O que uma interface pode conter agora que pode carregar implementações, a auto-property que não é uma, e o membro que você só consegue chamar através da interface |
| [0011](lessons/0011-generics.md) | Generics | Constraints como o vocabulário do que um parâmetro de tipo deve ser, variância como uma regra sobre posições, e o projeto final da etapa 2 de escolher o tipo certo |
| [0012](lessons/0012-extension-methods.md) | Extension methods | Duas sintaxes compilando para o mesmo IL, a regra de binding que impede uma extensão de sobrescrever qualquer coisa, e o que isso custa em um ponto de chamada |
| [0013](lessons/0013-linq.md) | LINQ | Uma linguagem de consulta com duas sintaxes e nenhuma diferença semântica, por que nada roda até você iterar, e a árvore de expressão que permite à mesma consulta chegar a um banco de dados |
| [0014](lessons/0014-delegates-and-events.md) | Delegates e events | Um delegate como um tipo cuja assinatura inclui o tipo de retorno, a lista de invocação em que um handler que lança exceção interrompe os demais, e o que a palavra-chave event tira de quem chama |
| [0015](lessons/0015-nullable-reference-types.md) | Tipos de referência anuláveis | Anotações em vez de tipos, o estado de nulidade que o compilador rastreia ao longo do seu fluxo de controle, e a única biblioteca que transforma sua anotação em comportamento em tempo de execução |
| [0016](lessons/0016-expression-bodied-members.md) | Membros com corpo de expressão | O segundo trabalho do token de seta, a regra de statement-expression para membros void, e o projeto final da etapa 3 de reescrever Java traduzido |
| [0017](lessons/0017-the-task-model.md) | O modelo de Task | Uma task como uma operação assíncrona e não como uma thread, as quatro formas pelas quais uma passa a existir, e a AggregateException que pode encerrar um processo que você achava que tinha terminado |
| [0018](lessons/0018-async-and-await.md) | async e await | O que await faz com o método que o envolve, os três lugares em que é proibido, e por que async void quebra o único mecanismo que quem chama tem |
| [0019](lessons/0019-task-composition.md) | Composição de tasks | Iniciar o trabalho antes de aguardá-lo, o ToArray que faz uma lista de tasks construída com LINQ realmente rodar, e o await duplo que o WhenAny exige |
| [0020](lessons/0020-cancellation-tokens.md) | Cancellation tokens | Cancelamento cooperativo com um solicitante e muitos ouvintes, por que retornar cedo reporta sucesso, e a comparação de tokens que decide se uma task diz que foi cancelada |
| [0021](lessons/0021-async-streams.md) | Async streams | As três interfaces por trás de await foreach, o atributo que deixa o token de um consumidor chegar ao corpo de um iterador assíncrono, e o projeto final da etapa 4 de prever um programa assíncrono |
| [0022](lessons/0022-xunit-and-nunit.md) | xUnit e NUnit | A regra de uma instância por teste que deixa o xUnit sem precisar de atributo de setup, a palavra theory significando duas coisas diferentes, e o paralelismo que uma fixture compartilhada custa em silêncio |
| [0023](lessons/0023-mocking.md) | Mocking | O proxy em tempo de execução por trás de toda biblioteca de substituição, o padrão do C# que decide o que ela pode substituir, e a asserção mockada que passa sem que a chamada jamais aconteça |
| [0024](lessons/0024-the-dotnet-cli-and-packages.md) | A CLI dotnet e pacotes | O único comando de que um clone recém-feito precisa, por que uma versão de pacote é um piso e não um pin, a versão do SDK que reordenou os comandos, e o projeto final da etapa 5 |
| [0025](lessons/0025-routing-and-middleware.md) | Roteamento e middleware | Dois sistemas dividindo um Program.cs, um decidido pela ordem em que você escreveu e outro pela precedência de templates, e as duas posições que decidem o que um middleware pode saber e se ele chega a rodar |
| [0026](lessons/0026-dependency-injection.md) | Injeção de dependência | Três tempos de vida como afirmações que o container só impõe onde consegue enxergá-las, o serviço de vida longa que promove em silêncio um de vida curta, e por que ninguém faz dispose do que o container criou |
| [0027](lessons/0027-configuration.md) | Configuração | Um único dicionário plano de strings em que o último provider vence, três interfaces de options separadas por tempo de vida e não por gosto, e uma validação que espera a primeira requisição a menos que você peça o contrário |
| [0028](lessons/0028-entity-framework-core.md) | Entity Framework Core | Um contexto que lembra o que você consultou para que uma atribuição vire um update, o único lugar em que uma consulta pode recorrer ao cliente, e por que o hábito da etapa 4 de sobrepor trabalho o corrompe |
| [0029](lessons/0029-structuring-a-typed-tested-backend.md) | Estruturando um backend tipado e testado | O container como a junção por onde um teste substitui registros, a regra documentada para escolher entre um teste unitário e um teste de integração, e o projeto final da etapa 6 com quatro defeitos que todos compilam |
| [0030](lessons/0030-two-comparisons-with-java.md) | Duas comparações com Java | O mesmo problema de espera resolvido em duas camadas diferentes, por que a resposta do Java remove o estilo que o C# exige em vez de adotá-lo, e a árvore de expressão que não tem equivalente em uma Stream |
| [0031](lessons/0031-reviewing-csharp.md) | Revisando um codebase C# | A diferença entre uma opinião de estilo e um custo que você consegue nomear, uma passada de revisão ordenada pelo que o compilador nunca vai te dizer, e os hábitos que este arco vem colecionando desde a lição 1 |
| [0032](lessons/0032-the-managed-heap-and-generations.md) | O managed heap e as gerações | A lição 1 disse que uma instância de class vive no managed heap; esta lição abre o que acontece com ela lá, por que o heap é dividido em três gerações, e por que a maioria dos objetos deve morrer na mais jovem sem nunca ser promovida |
| [0033](lessons/0033-gc-modes-and-tradeoffs.md) | Modos de GC e trade-offs | A lição 32 estabeleceu o heap geracional; esta lição cobre como uma coleta realmente roda sobre ele, uma thread dedicada ou uma por núcleo, bloqueando toda thread gerenciada ou deixando a maioria continuar, e o único momento em que até o modo não bloqueante ainda precisa parar tudo |
| [0034](lessons/0034-span-and-memory.md) | Span e Memory | Uma visão sem alocação sobre memória existente que nunca entra no sistema geracional da lição 32, as restrições do compilador que a mantêm com segurança apenas na pilha, e a contraparte segura no heap construída exatamente para a única coisa que ela não consegue fazer: atravessar um await |
| [0035](lessons/0035-stackalloc-and-arraypool.md) | stackalloc e ArrayPool | A lição 34 deixou um Span<T> enxergar memória alocada com stackalloc; esta lição cobre o que stackalloc realmente aloca, por que combiná-lo com uma ref struct é o que o torna seguro, seu risco real (um stack overflow, não a coleta de lixo), e ArrayPool<T> como alternativa para um buffer grande demais ou duradouro demais para a pilha |
| [0036](lessons/0036-struct-vs-class-measured.md) | Struct contra class, medido | A lição 1 argumentou que uma struct pode evitar uma alocação no heap que uma class de mesmo formato exigiria; esta lição é onde esse argumento é medido em vez de raciocinado, e por que a forma óbvia de medi-lo produz um número que não significa nada |
| [0037](lessons/0037-profiling-a-csharp-service.md) | Fazendo profiling de um serviço C# | O dotnet-counters pega o sintoma e o dotnet-trace encontra a pilha quente por trás dele, fazer profiling só depois do warm-up para que não seja o JIT o que é medido, e o projeto final da etapa 8 de levar a descoberta de um profile de volta por uma das alavancas desta própria etapa |
| [0038](lessons/0038-idisposable-and-iasyncdisposable.md) | IDisposable e IAsyncDisposable | A lição 6 ensinou using como consumidor, e a lição 26 ensinou que um container faz dispose do que cria; esta lição é para o outro lado, implementar de fato IDisposable e IAsyncDisposable, o padrão que torna um tipo seguro para receber dispose mais de uma vez, seguro para ser finalizado e seguro para ser aguardado |
| [0039](lessons/0039-logging-and-health-checks.md) | Logging e health checks | Um backend tipado e testado que ninguém consegue observar nem perguntar "você está funcionando" ainda não terminou de ser entregue; esta lição liga o logging estruturado do ILogger e a separação entre liveness e readiness no Program.cs, do mesmo jeito que a lição 25 ligou o roteamento e a lição 26 ligou o container |
| [0040](lessons/0040-opentelemetry.md) | OpenTelemetry | O ILogger da lição 39 já é um dos três pilares do OpenTelemetry; esta lição adiciona os outros dois, métricas e traces, por meio de APIs já embutidas no framework, e liga os três em um serviço com o mesmo padrão AddX que as lições 25, 26 e 39 já ensinaram |
| [0041](lessons/0041-authentication-and-authorization.md) | Autenticação e autorização | A autenticação responde quem você é e a autorização responde o que você tem permissão para fazer, documentadas como preocupações separadas mesmo que uma dependa da outra, ligadas com a própria disciplina de ordenação de middleware da lição 25 e a sobrescrita AllowAnonymous de que os health checks da lição 39 realmente precisam |
| [0042](lessons/0042-system-text-json.md) | System.Text.Json | Os padrões do serializador puro (PascalCase, sensível a maiúsculas) não são o que o ASP.NET Core realmente usa na fronteira HTTP (camelCase, insensível a maiúsculas), uma divergência real que vale nomear antes que produza um resultado de teste confuso, além da geração de código-fonte como alternativa em tempo de compilação à reflection |
| [0043](lessons/0043-api-compatibility.md) | Compatibilidade de API | Uma mudança que recompila sem erros ainda pode quebrar todo chamador que não recompila, uma mudança que não compila pode ser perfeitamente aceitável para chamadores que já têm um binário funcionando, e uma mudança que não faz nenhuma das duas ainda pode fazer algo diferente em silêncio, que é justamente aquela sobre a qual o versionamento semântico existe para avisar quem chama |
| [0044](lessons/0044-obsolete-and-deprecation.md) | Obsolete e depreciação | A lição 43 nomeou o que conta como uma breaking change; ObsoleteAttribute é como uma API publicada anuncia que uma está chegando, escalando de um aviso que pode ser suprimido para um erro de compilação real no mesmo membro, com um ID de diagnóstico próprio para que o aviso de uma depreciação possa ser silenciado sem silenciar todos os outros do projeto |
| [0045](lessons/0045-nuget-packaging-and-versioning.md) | Empacotamento e versionamento com NuGet | A lição final deste arco amarra a etapa 11, o número de versão que as categorias de compatibilidade da lição 43 realmente justificam, o sufixo de pré-lançamento sobre o qual o NuGet não impõe nada além de chamá-lo de pré-lançamento, o conselho sobre limite superior que vai contra o instinto, e o pacote desatualizado que um rebuild pode deixar você testando |

## Referência

- [Glossário](GLOSSARY.md): termos canônicos deste tópico
- [Recursos](RESOURCES.md): fontes confiáveis
- [Tipos de valor contra tipos de referência](reference/value-vs-reference-types.md): struct contra class, tipos de valor anuláveis, prever o comportamento de cópia contra referência
- [Modelagem](reference/modelling.md): tipos `record`, pattern matching e switch expressions, interfaces com implementações padrão, generics
- [Idioma](reference/idiom.md): extension methods, LINQ, delegates e events, tipos de referência anuláveis
- [Async](reference/async.md): o modelo de `Task`, a mecânica de `async`/`await`, cancellation tokens, `IAsyncEnumerable`
- [Testes e build](reference/testing-and-build.md): xUnit/NUnit, mocking, a CLI `dotnet` e o gerenciamento de projetos e pacotes
- [Entregando o serviço](reference/shipping-the-service.md): roteamento e middleware do ASP.NET Core, injeção de dependência, configuração, o básico do Entity Framework Core
- [Julgamento](reference/judgment.md): `async`/`await` contra virtual threads do Java, LINQ contra a Stream API, revisar C# em busca de um hábito que apenas compila

## Como isto funciona

Cada lição é curta e autocontida. Os gabaritos ficam recolhidos: primeiro lembre, depois abra. A prática no mundo real importa mais do que a leitura, e espaçá-la é o ponto. Tudo o que ainda estiver confuso no fim de uma lição vale ser perseguido até a fonte primária antes de seguir adiante.
