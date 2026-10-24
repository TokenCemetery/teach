---
title: Kotlin
description: "Domine Kotlin na JVM: null safety, coroutines e Kotlin idiomático do zero"
type: topic
---

# Aprendizado: Kotlin

Torne-se o engenheiro em quem a equipe confia para ser dono de Kotlin, em um serviço de backend ou em um app Android: capaz de modelar um domínio de forma idiomática, escrever e raciocinar sobre coroutines e `Flow`, entregar um serviço Kotlin ou um componente Android tipado e testado, e revisar o Kotlin de alguém e nomear concretamente o que uma construção está custando.

**Última lição:** [44. Testando coroutines além do runTest](lessons/0044-testing-coroutines-beyond-runtest.md)

## O sucesso se parece com isto

- Modelar um domínio com data classes, sealed classes e enums, e saber quando a null safety, e não uma exceção, é o sinal correto.
- Escrever e raciocinar sobre coroutines e `Flow`, e comparar o modelo com as virtual threads do Java.
- Entregar um serviço de backend Kotlin ou um componente Android tipado e testado, projetado de forma idiomática.
- Dado um código Kotlin escrito com um hábito que apenas compila (verificações defensivas de null em vez do sistema de tipos, um callback em vez de uma coroutine), nomear o hábito e reescrevê-lo de forma idiomática.

## Restrições

- Não pressupõe Kotlin prévio. Experiência em Java ou em outra linguagem da JVM encurta as primeiras etapas, mas não é exigida, e traz hábitos que o Kotlin pune em silêncio: verificações defensivas de null em vez do sistema de tipos, uma class onde uma data class ou um sealed type diria melhor.
- Cobre os contextos de backend/servidor e de Android, tocando em cada um onde eles divergem.
- Precisa apenas de um JDK, do toolchain do Kotlin e de um terminal; o Android Studio só onde o material específico de Android exige.

## Fora do escopo

- Internos da JVM além do que explica o comportamento compilado do próprio Kotlin (ajuste completo do garbage collector, profiling, engenharia de bytecode): veja [`programming/java`](../../programming/java/), referenciado para mais profundidade em vez de reensinado.
- Outras linguagens da JVM (Java, Scala, Clojure, Groovy) como assuntos próprios, embora um contraste apareça onde esclarece um idioma do Kotlin.
- Kotlin Multiplatform: mirar JS, Native ou Wasm, estruturar declarações `expect`/`actual` entre source sets, e as diferenças de stdlib específicas de plataforma que esses alvos introduzem. Este arco é só JVM do início ao fim, conforme o próprio enquadramento da missão; uma lição aqui precisaria de sua própria configuração de Gradle e de seu próprio conjunto de idiomas, e não de uma lição de JVM com uma nota de rodapé sobre multiplataforma. `kotlinx.serialization` (lição 38) é o único lugar em que o alcance multiplataforma é mencionado, como razão documentada para uma escolha de design do lado da JVM, e não como material de multiplataforma em si.

## O arco

Onze etapas, do zero ao nível sênior. Não é uma lista de lições: uma etapa leva várias lições e as fronteiras são flexíveis.

| Etapa | Lições | Cobre | Concluída quando |
|---|---|---|---|
| 1. Fundamentos | 0001 a 0006 | Null safety, `val`/`var` e imutabilidade, valores contra referências, tipos básicos e string templates, o básico de coleções (`List`/`Set`/`Map`, mutáveis contra somente leitura), fluxo de controle (`when`, ranges, `for`) | Consegue prever nulabilidade e mutabilidade sem executar o código |
| 2. Modelagem | 0007 a 0012 | Classes e properties, data classes, sealed classes e `when` exaustivo, enums, object declarations e companion objects, interfaces com métodos padrão | Modela um domínio sem recorrer primeiro a uma hierarquia de uma class por coisa |
| 3. Idioma | 0013 a 0018 | Extension functions, scope functions (`let`/`run`/`with`/`apply`/`also`), funções de ordem superior e lambdas, inline functions e reified generics, delegação (`by`), sobrecarga de operadores | Escreve Kotlin que um revisor não descreveria como Java traduzido |
| 4. Coleções e sequences | 0019 a 0021 | Os operadores de coleção do Kotlin, `Sequence` preguiçosa contra coleções ansiosas, agrupamento e fold | Escolhe entre um pipeline de coleção e uma sequence e consegue defender o custo de cada um |
| 5. Concorrência | 0022 a 0027 | Threads e o básico do modelo de memória da JVM, suspend functions e coroutine builders, structured concurrency, coroutine context e dispatchers, `Flow`, cancelamento e tratamento de exceções | Consegue prever o que um programa concorrente com coroutines faz antes de executá-lo, e comparar o modelo com as virtual threads do Java |
| 6. Testes e build | 0028 a 0030 | Frameworks de teste do Kotlin, mocking, o Gradle Kotlin DSL e o gerenciamento de dependências | Outra pessoa consegue clonar, compilar, testar e executar |
| 7. Entregando um serviço | 0031 a 0033 | Estruturar um serviço de backend tipado e testado, idiomas específicos de Android onde a plataforma diverge, generics e variância (`in`/`out`) | Estruturou um serviço de backend Kotlin ou um componente Android tipado e testado; a etapa 10 o completa com uma camada HTTP, configuração, logging e persistência |
| 8. Julgamento | 0034 a 0035 | Interoperabilidade com Java, revisar Kotlin e nomear com precisão o que uma construção está custando | Tem a confiança para tomar a decisão e explicá-la a outra pessoa |
| 9. Idioma avançado | 0036 a 0039 | Type-safe builders e DSLs, `value class`/`@JvmInline`, `kotlinx.serialization`, `Result` e idiomas de tratamento de erros | Escreve de forma idiomática uma pequena DSL de type-safe builder, um tipo wrapper de custo zero e um caminho de erro baseado em `Result` |
| 10. Completando o serviço | 0040 a 0043 | Uma camada HTTP, configuração, logging e persistência para o serviço de backend Kotlin que a etapa 7 começou a estruturar | Entrega um serviço de backend Kotlin com uma camada HTTP roteada, configuração externalizada, logging estruturado e acesso a banco de dados, e não apenas um esqueleto estruturado |
| 11. Testando coroutines além do runTest | 0044 | O `cancelAndIgnoreRemainingEvents()` do Turbine para um flow que nunca termina, e o que um teste de cancelamento realmente precisa afirmar, dado que o cancelamento é cooperativo | Testa um flow infinito sem travar, e testa o cancelamento pela evidência real e documentada, e não apenas por uma flag de `Job` |

## Lições

Siga estas na ordem.

| # | Lição | Ensina |
|---|---|---|
| [0001](lessons/0001-null-safety.md) | Null safety | Mover o "isto pode ser null" de uma surpresa em tempo de execução para uma pergunta em tempo de compilação, e como o hábito do Java desfaz isso |
| [0002](lessons/0002-val-var-and-immutability.md) | val/var e imutabilidade | Por que val é o padrão que vale defender, o que ele realmente garante (e o que não garante), e o hábito do Java de recorrer a var por reflexo |
| [0003](lessons/0003-values-vs-references.md) | Valores contra referências | Por que == significa algo diferente no Kotlin e no Java, e o bug específico que o hábito do Java de escrever == produz |
| [0004](lessons/0004-basic-types-and-string-templates.md) | Tipos básicos e string templates | Por que o Kotlin não tem primitivos no nível da linguagem, e string templates como recurso da linguagem e não como concatenação com sintaxe extra |
| [0005](lessons/0005-collections-basics.md) | O básico de coleções | List, Set e Map como coleções somente leitura pela interface, e por que uma coleção mutável guardada em um val continua mutável |
| [0006](lessons/0006-control-flow.md) | Fluxo de controle | if e when como expressões que produzem valores, o que um range realmente é, e o projeto final da etapa 1 de prever nulabilidade e mutabilidade sem executar código |
| [0007](lessons/0007-classes-and-properties.md) | Classes e properties | Properties como substitutas do boilerplate de getters/setters do Java, e por que a própria documentação do Kotlin diz para recorrer a uma class por último |
| [0008](lessons/0008-data-classes.md) | Data classes | O que data class realmente gera, e a regra sutil de que só as properties do construtor primário participam de qualquer parte disso |
| [0009](lessons/0009-sealed-classes-and-exhaustive-when.md) | Sealed classes e when exaustivo | Como selar uma hierarquia transforma a exaustividade de um when de uma promessa manual em uma garantia verificada pelo compilador |
| [0010](lessons/0010-enums.md) | Enums | Cada constante de enum como um objeto real com seu próprio estado e comportamento, e exatamente onde um enum se encaixa melhor que uma sealed class |
| [0011](lessons/0011-object-declarations-and-companion-objects.md) | Object declarations e companion objects | Singletons declarados, e não implementados à mão, e companion objects como o verdadeiro substituto do Kotlin para os membros static do Java |
| [0012](lessons/0012-interfaces-with-default-methods.md) | Interfaces com métodos padrão | Por que uma interface Kotlin pode implementar comportamento mas nunca guardar estado, e como resolver um conflito em diamante de forma explícita |
| [0013](lessons/0013-extension-functions.md) | Extension functions | Acrescentar comportamento a um tipo sem herança, e a pegadinha do despacho estático que derruba as pessoas na primeira vez que esbarram nela |
| [0014](lessons/0014-scope-functions.md) | Scope functions | Escolher entre let, run, with, apply e also pelo que cada uma retorna e por como expõe o objeto, e não por hábito |
| [0015](lessons/0015-higher-order-functions-and-lambdas.md) | Funções de ordem superior e lambdas | Tipos de função como tipos de verdade, a sintaxe de trailing lambda, e o mecanismo de receiver sobre o qual as scope functions são de fato construídas |
| [0016](lessons/0016-inline-functions-and-reified-generics.md) | Inline functions e reified generics | Por que inline existe para remover um custo real, por que ele permite retornos não locais, e por que parâmetros de tipo reified só funcionam por causa do inlining |
| [0017](lessons/0017-delegation.md) | Delegação | Implementar uma interface repassando para um objeto guardado sem nenhum boilerplate, e comportamento reutilizável de properties via by lazy e delegates personalizados |
| [0018](lessons/0018-operator-overloading.md) | Sobrecarga de operadores | Operadores como funções nomeadas comuns com um mapeamento fixo de símbolos, e a disciplina real de implementar um só onde ele significa o que o símbolo já significa |
| [0019](lessons/0019-collection-operators.md) | Operadores de coleção | Os operadores de coleção como extension functions que retornam uma nova coleção de forma ansiosa, e o hábito da Stream do Java que calcula mal o custo de uma cadeia deles |
| [0020](lessons/0020-sequences-and-laziness.md) | Sequences e preguiça | Por que a mesma cadeia de operadores se comporta de outro jeito em uma Sequence, para que serve de fato uma operação terminal, e quando a preguiça custa mais do que economiza |
| [0021](lessons/0021-grouping-and-folding.md) | Agrupamento e fold | Agregar com fold e reduce, agrupar sem construir os grupos, e o projeto final da etapa 4 de defender o que um pipeline custa |
| [0022](lessons/0022-threads-and-the-memory-model.md) | Threads e o modelo de memória | Por que o Kotlin não tem um modelo de memória próprio na JVM, as três construções que ele escreve como anotações em vez de palavras-chave, e as duas garantias que um val não te dá |
| [0023](lessons/0023-suspend-functions-and-coroutine-builders.md) | Suspend functions e coroutine builders | O que suspend realmente muda em uma função, os três builders e o que cada um retorna, e por que código que suspende ainda se lê de cima para baixo |
| [0024](lessons/0024-structured-concurrency.md) | Structured concurrency | A árvore de pai e filhos que torna o cancelamento previsível, por que um scope que você possui é um scope que você precisa cancelar, e o que GlobalScope realmente custa |
| [0025](lessons/0025-coroutine-context-and-dispatchers.md) | Coroutine context e dispatchers | O context como um conjunto de elementos combinados com plus, qual dispatcher pertence a qual tipo de trabalho, e o único elemento de context que quebra a structured concurrency em silêncio |
| [0026](lessons/0026-flows.md) | Flows | Um flow como a terceira opção assíncrona depois de uma lista e de uma sequence, o que frio realmente significa para cada coletor, e a regra de context que um flow builder impõe em tempo de execução |
| [0027](lessons/0027-cancellation-and-exception-handling.md) | Cancelamento e tratamento de exceções | Por que o cancelamento é cooperativo e o que faz um código ignorá-lo, por que uma CancellationException não é uma falha, e como o modelo de coroutines se compara às virtual threads do Java |
| [0028](lessons/0028-test-frameworks.md) | Frameworks de teste | As camadas sobre as quais um teste Kotlin realmente se apoia, por que o tempo virtual do runTest para na fronteira do dispatcher, e o que isso impõe ao design do código sob teste |
| [0029](lessons/0029-mocking.md) | Mocking | Por que o final por padrão muda o que mocking significa no Kotlin, o que o MockK faz pelas construções que não são métodos de um objeto, e quando a finalidade está te dizendo que falta uma junção |
| [0030](lessons/0030-gradle-and-dependency-management.md) | Gradle e gerenciamento de dependências | Os acessores type-safe do Kotlin DSL e onde eles acabam, por que uma configuration do Gradle não é um scope do Maven, e a regra de resolução que decide qual versão chega ao classpath |
| [0031](lessons/0031-structuring-a-service.md) | Estruturando um serviço | Onde os arquivos Kotlin realmente ficam e o que vai dentro de uma class, e as quatro decisões de etapas anteriores que decidem se um serviço é testável |
| [0032](lessons/0032-android-divergences.md) | Divergências do Android | Os scopes que o Android possui por você, a main-safety como um contrato que quem é chamado mantém, e por que o tempo de vida da composição não é o tempo de vida do lifecycle |
| [0033](lessons/0033-generics-and-variance.md) | Generics e variância | Variância no local da declaração no lugar de wildcards, o que out e in realmente prometem sobre um parâmetro de tipo, e como ler uma assinatura projetada |
| [0034](lessons/0034-java-interop.md) | Interoperabilidade com Java | Por que a fronteira é assimétrica, o que um platform type te custa e como pagar de volta, e quais anotações você deve a quem chama a partir do Java |
| [0035](lessons/0035-reviewing-kotlin.md) | Revisando Kotlin | Transformar o arco em um instrumento de revisão: o custo que cada hábito esconde, a forma de um comentário que o nomeia, e o que não revisar |
| [0036](lessons/0036-type-safe-builders-and-dsls.md) | Type-safe builders e DSLs | A lição 15 ensinou o tipo de função com receiver que permite a run e apply exporem this; um type-safe builder é exatamente esse mecanismo aninhado recursivamente, e @DslMarker é o único atributo que impede um builder aninhado de alcançar em silêncio o receiver errado |
| [0037](lessons/0037-value-classes.md) | value class e @JvmInline | Uma value class é a correção para a obsessão por primitivos que a JVM normalmente deixa você ter de graça, representada como seu próprio valor subjacente sem nenhum objeto wrapper, exceto nos casos específicos e documentados em que o compilador ainda precisa fazer boxing |
| [0038](lessons/0038-kotlinx-serialization.md) | kotlinx.serialization | Um hábito do Java recorre a uma biblioteca que inspeciona a forma de uma class via reflection em tempo de execução; o kotlinx.serialization gera essa mesma lógica em tempo de compilação, por meio de um plugin do compilador, que é exatamente o que permite que ele funcione em alvos Kotlin que não têm nenhuma API de reflection em tempo de execução |
| [0039](lessons/0039-result-and-error-handling.md) | Result e idiomas de tratamento de erros | runCatching embrulha qualquer Throwable em um Result, que é exatamente o problema dentro de uma coroutine, já que o cancelamento cooperativo da lição 27 depende de a CancellationException se propagar sem ser capturada, e runCatching a engole como uma falha comum a menos que quem chama a relance explicitamente antes |
| [0040](lessons/0040-http-layer.md) | Camada HTTP | A lição 31 adiou de propósito o roteamento para o framework que você escolhesse; o próprio bloco routing do Ktor acaba sendo a DSL de type-safe builder da lição 36 aplicada a HTTP, nada instalado por padrão, e uma extração de parâmetros da requisição que falha ruidosamente em vez de vincular a coisa errada em silêncio |
| [0041](lessons/0041-configuration.md) | Configuração | O comportamento real de um serviço, sua porta, a URL do banco de dados, seus segredos, precisa mudar entre ambientes sem recompilar uma única linha, e o arquivo de configuração do Ktor mais um idioma de substituição específico e fácil de deixar passar é como um padrão e uma sobrescrita por ambiente vivem em exatamente um lugar |
| [0042](lessons/0042-logging.md) | Logging | O SLF4J em silêncio não faz nada até que um backend de logging real seja adicionado como dependência, e os valores de MDC por requisição do CallLogging ficam em silêncio invisíveis até que o próprio padrão de log seja atualizado para imprimi-los, a mesma forma de armadilha aparecendo duas vezes na mesma lição |
| [0043](lessons/0043-persistence.md) | Persistência | A DSL do Exposed é mais um type-safe builder, e por baixo é em grande parte bloqueante, já que embrulha o JDBC; o projeto final da etapa 10 é despachar esse trabalho bloqueante corretamente em vez de travar qualquer thread que por acaso estivesse atendendo a requisição, e revisitar do que o serviço entregue na etapa 7 realmente precisava desde o início |
| [0044](lessons/0044-testing-coroutines-beyond-runtest.md) | Testando coroutines além do runTest | A lição 28 ensinou o awaitItem do Turbine e o travamento que ele causa se nada o encerra; esta lição cobre a ferramenta específica para um flow que nunca termina sozinho, e o que um teste de cancelamento realmente precisa afirmar, dado que o cancelamento é cooperativo e não atualiza tudo no instante em que cancel() é chamado |

## Referência

- [Glossário](GLOSSARY.md): termos canônicos deste tópico
- [Recursos](RESOURCES.md): fontes confiáveis
- [Null safety e mutabilidade](reference/null-safety-and-mutability.md): null safety, `val`/`var`, valores contra referências, prever nulabilidade e mutabilidade
- [Modelagem](reference/modelling.md): data classes, sealed classes e `when` exaustivo, object declarations e companion objects, interfaces com métodos padrão
- [Idioma](reference/idiom.md): extension functions, scope functions (`let`/`run`/`with`/`apply`/`also`), delegação (`by`), sobrecarga de operadores
- [Coleções e sequences](reference/collections-and-sequences.md): os operadores de coleção do Kotlin, `Sequence` preguiçosa contra coleções ansiosas, agrupamento e fold
- [Concorrência](reference/concurrency.md): suspend functions e coroutine builders, structured concurrency, coroutine context e dispatchers, `Flow`, comparação com as virtual threads do Java
- [Testes e build](reference/testing-and-build.md): frameworks de teste do Kotlin, mocking, o Gradle Kotlin DSL e o gerenciamento de dependências
- [Entregando um serviço](reference/shipping-a-service.md): estruturar um backend tipado e testado, idiomas específicos de Android, generics e variância
- [Julgamento](reference/judgment.md): interoperabilidade com Java, revisar Kotlin e nomear com precisão o que uma construção está custando

## Como isto funciona

Cada lição é curta e autocontida. Os gabaritos ficam recolhidos: primeiro lembre, depois abra. A prática no mundo real importa mais do que a leitura, e espaçá-la é o ponto. Tudo o que ainda estiver confuso no fim de uma lição vale ser perseguido até a fonte primária antes de seguir adiante.
