---
title: Java
description: "Domine um serviço em Java: modele-o em Java moderno e depois opere o que a JVM faz com ele"
type: topic
---

# Aprendizado: Java

Torne-se o engenheiro em quem a equipe confia para ser dono de um serviço em Java: capaz de modelar um domínio em Java moderno em vez das hierarquias de herança que a linguagem costumava exigir, raciocinar sobre concorrência a partir do modelo de memória e não por experimentação, ler um profile e um log de garbage collection até chegar a uma decisão, e revisar o Java de alguém e nomear concretamente o que uma abstração está custando.

**Comece aqui:** [0001. Referências são valores](lessons/0001-references-are-values.md)
**Última lição:** [0052. Reflection e anotações](lessons/0052-reflection-and-annotations.md)

## O sucesso se parece com isto

- Prever o que a igualdade de referência, um `hashCode` quebrado e um campo mutável compartilhado fazem, antes de executar o código.
- Modelar um domínio com records, sealed interfaces e enums, e dizer por que uma hierarquia de herança teria sido pior.
- Dizer o que `synchronized`, `volatile` e uma coleção concorrente garantem cada um, no vocabulário do modelo de memória do Java.
- Usar virtual threads onde elas compensam, e nomear o que ainda bloqueia uma carrier thread.
- Ler um log de garbage collection e um profile, e então dimensionar um heap a partir dessa evidência e não de um padrão.
- Entregar um build que outra pessoa consiga executar: dependências declaradas, uma suíte de testes, um artefato executável.
- Revisar um pull request e dizer com precisão por que uma hierarquia de classes, uma checked exception ou uma cadeia de streams é a ferramenta errada ali.
- Resolver uma discussão sobre a linguagem a partir da especificação e da JEP que introduziu o recurso.

## Restrições

- Não pressupõe Java prévio. Experiência em outra linguagem encurta as primeiras etapas, mas não é exigida, e traz hábitos que o Java pune em silêncio: um getter para cada campo, uma interface com uma única implementação, uma class onde um record diria melhor.
- A base é a versão atual de suporte de longo prazo. Cada recurso da linguagem é apresentado com a versão em que chegou, porque código Java é lido através de muitas versões e o "Java moderno" envelhece.
- Precisa apenas de um JDK e de um terminal em qualquer sistema operacional suportado. Uma IDE ajuda e nunca é exigida, e nada no arco exige ferramentas pagas ou uma conta na nuvem.
- A maior parte das práticas são programas pequenos que cabem em uma sessão. A etapa 6 é a exceção: um profile precisa de um programa que rode tempo suficiente para ser perfilado.
- Afirmações sensíveis à versão são verificadas contra a especificação, a documentação da API e o índice de JEPs, e não contra um livro, porque o ciclo de lançamentos semestral ultrapassa todos os livros listados.

## Fora do escopo

- Frameworks como assuntos próprios: Spring, Jakarta EE, Quarkus, Hibernate. Julgar se um framework merece seu lugar é uma habilidade de revisão e pertence à etapa 7.
- Outras linguagens da JVM: Kotlin, Scala, Clojure, Groovy.
- Android, e plataformas móveis em geral.
- Comparação de ferramentas de build. O arco ensina as tarefas que um build precisa realizar e usa uma ferramenta para realizá-las, em vez de discutir qual.
- Internos da JVM além do ponto em que deixam de prever o comportamento do programa: implementação do JIT, engenharia de bytecode, escrever um garbage collector.
- Kubernetes e infraestrutura além do que um serviço precisa para rodar. Colocar o artefato executável em uma imagem de contêiner, e executar, proteger e depurar esse contêiner, fica em [`infrastructure/containers`](../../infrastructure/containers/). Executá-lo em um cluster fica em [`infrastructure/kubernetes`](../../infrastructure/kubernetes/).

## O arco

Sete etapas, do zero ao nível sênior. Não é uma lista de lições: uma etapa leva várias lições e as fronteiras são flexíveis.

| Etapa | Lições | Cobre | Concluída quando |
|---|---|---|---|
| 1. Fundamentos | 0001 a 0006 | Primitivos e referências, `null`, strings e seu pool, arrays, o collections framework, `equals` e `hashCode`, `Comparable` | Consegue prever identidade contra igualdade e aliasing sem executar o código |
| 2. Modelagem | 0007 a 0014 | Classes e interfaces, records, sealed types, enums, generics e erasure, pattern matching, imutabilidade como padrão | Modela um domínio sem recorrer primeiro à herança |
| 3. Idioma e a biblioteca | 0015 a 0021 | Exceções e o que fazer com as checked, `Optional`, streams e collectors, iteração, arquivos e IO, a API de tempo, text blocks | Escreve Java que um revisor não descreveria como não idiomático |
| 4. Concorrência | 0022 a 0028 | Threads, o modelo de memória, `synchronized` e `volatile`, `java.util.concurrent`, executors, virtual threads, structured concurrency, as armadilhas | Consegue nomear a garantia que um programa concorrente quebrado violou |
| 5. Testes e build | 0029 a 0035 | JUnit 6, testes parametrizados, test doubles e quando não usar um, declaração de dependências, um artefato executável reproduzível | Outra pessoa consegue clonar, compilar, testar e executar |
| 6. O runtime | 0036 a 0042 | Áreas de memória, layout de objetos e escape analysis, garbage collectors e seus trade-offs, ler um log de GC, JMH, profiling, redução de alocações | Otimiza a partir de um profile e prova o ganho com um benchmark confiável |
| 7. Julgamento | 0043 a 0049 | Design de API e compatibilidade retroativa, depreciação, revisão, ler a especificação e as JEPs em busca de respostas | Tem a confiança para tomar a decisão e explicá-la a outra pessoa; a etapa 8 a completa com o mecanismo, reflection e anotações, a partir do qual todo framework julgado foi de fato construído |
| 8. Módulos e reflection | 0050 a 0052 | O sistema de módulos, `module-info.java`, `requires` e `exports`, encapsulamento forte, imagens de runtime com `jlink` e `jpackage`, reflection e anotações | Declara uma fronteira de módulo de propósito, entrega uma imagem de runtime construída a partir dela, e lê o que a reflection de um framework realmente toca antes de julgar se ele merece seu lugar |

## Lições

Siga estas na ordem.

| # | Lição | Ensina |
|---|---|---|
| [0001](lessons/0001-references-are-values.md) | Referências são valores | Uma variável guarda um primitivo ou uma referência, e toda atribuição e todo argumento copiam isso |
| [0002](lessons/0002-identity-and-equality.md) | Identidade e igualdade | == compara referências, então responde a uma pergunta diferente para strings e números boxed |
| [0003](lessons/0003-equals-and-hashcode.md) | O contrato de equals e hashCode | Quebre o contrato e uma coleção hash perde o seu objeto sem acusar nada |
| [0004](lessons/0004-null.md) | null e de onde ele vem | null é uma referência que não aponta para nada, e a correção é rejeitá-lo na fronteira |
| [0005](lessons/0005-arrays-and-collections.md) | Arrays e coleções | Arrays são covariantes e fixos, e três factories de listas diferem de formas que seus nomes escondem |
| [0006](lessons/0006-comparable-and-comparator.md) | Comparable e Comparator | Uma coleção ordenada usa a ordenação e não equals, então um comparator inconsistente perde dados |
| [0007](lessons/0007-classes-and-objects.md) | Classes e objetos | Uma class é um molde de estado e comportamento, e todo campo começa com um valor padrão que você não escreveu |
| [0008](lessons/0008-records.md) | Records | Um portador transparente de dados imutáveis, com o construtor, os acessores, equals, hashCode e toString derivados do cabeçalho |
| [0009](lessons/0009-interfaces.md) | Interfaces | Um contrato sem estado, mais os default methods que permitem que ele cresça sem quebrar todo implementador |
| [0010](lessons/0010-inheritance-and-composition.md) | Herança e composição | O que extends realmente te dá, e por que a resposta costuma ser um campo em vez de uma superclasse |
| [0011](lessons/0011-sealed-types-and-pattern-matching.md) | Sealed types e pattern matching | Um conjunto fechado de alternativas, e um compilador que verifica se você tratou todas |
| [0012](lessons/0012-enums.md) | Enums | Um conjunto fixo de instâncias que a linguagem garante, com espaço para estado e comportamento em cada uma |
| [0013](lessons/0013-generics-and-erasure.md) | Generics e erasure | Parâmetros de tipo que o compilador verifica e o runtime esquece, e os wildcards que os tornam utilizáveis |
| [0014](lessons/0014-immutability-as-a-default.md) | Imutabilidade como padrão | Torne o objeto impossível de mudar e a maioria das perguntas difíceis deixa de ser feita |
| [0015](lessons/0015-exceptions.md) | Exceções | Quais falhas pertencem a uma assinatura, quais pertencem a um stack trace, e uma limpeza que sobrevive a ambas |
| [0016](lessons/0016-optional.md) | Optional | Um tipo de retorno que torna a ausência parte do contrato, e os quatro lugares onde ele não cabe |
| [0017](lessons/0017-streams.md) | Streams | Um pipeline que descreve trabalho, não faz nada dele até ser pedido, e só pode ser pedido uma vez |
| [0018](lessons/0018-collectors.md) | Collectors | Transformar um pipeline de volta em um contêiner, e os três collectors que lançam exceção onde você não espera |
| [0019](lessons/0019-files-and-paths.md) | Arquivos e paths | Paths que não são strings, streams que precisam ser fechados, e um charset que finalmente é um padrão que vale a pena ter |
| [0020](lessons/0020-dates-and-times.md) | Datas e horários | Qual dos seis tipos de tempo você realmente quis dizer, e os três que não são um ponto no tempo |
| [0021](lessons/0021-strings-and-text.md) | Strings e texto | Text blocks, a formatação que você deveria usar, e por que o comprimento não é o número de caracteres |
| [0022](lessons/0022-threads.md) | Threads | Uma thread é uma pilha de chamadas escalonada, e quase todo erro desta etapa começa por tratar uma como gratuita |
| [0023](lessons/0023-the-memory-model.md) | O modelo de memória | Por que um valor escrito por uma thread pode nunca ser visto por outra, e a regra exata que corrige isso |
| [0024](lessons/0024-mutual-exclusion.md) | Exclusão mútua | Uma thread por vez, as duas formas de dizer isso, e o deadlock que você consegue encontrar antes que aconteça |
| [0025](lessons/0025-concurrent-collections-and-atomics.md) | Coleções concorrentes e atomics | As coleções que sobrevivem ao acesso concorrente, e o check-then-act que derrota cada uma delas |
| [0026](lessons/0026-executors-and-futures.md) | Executors e futures | Submeta trabalho em vez de criar threads, e encontre a exceção que o submit engoliu |
| [0027](lessons/0027-virtual-threads.md) | Virtual threads | Threads baratas o bastante para bloquear, e o hábito de usar pools que agora você precisa desaprender |
| [0028](lessons/0028-choosing-a-model.md) | Escolhendo um modelo | Uma pergunta escolhe o modelo, e a falha que você está vendo nomeia a garantia que ela quebrou |
| [0029](lessons/0029-your-first-test.md) | Seu primeiro teste | Onde os testes ficam, o que o runner realmente faz, e o esquema de versões que todo artigo erra |
| [0030](lessons/0030-assertions-that-name-the-failure.md) | Asserções que nomeiam a falha | Um teste que falha é um relatório de bug, e a asserção que você escolheu decide quão bom é o relatório |
| [0031](lessons/0031-parameterised-tests.md) | Testes parametrizados | Um método de teste, muitos casos, e o ponto em que um loop dentro de um teste deixa de ser bom o bastante |
| [0032](lessons/0032-test-doubles.md) | Test doubles | Cinco tipos de substituto, quando um objeto real vence todos eles, e o que um mock deixa de testar em silêncio |
| [0033](lessons/0033-declaring-dependencies.md) | Declarando dependências | Coordenadas, escopos e o grafo transitivo, mais a versão que chega sem ser pedida |
| [0034](lessons/0034-the-build-lifecycle.md) | O ciclo de vida do build | Fases e goals em vez de comandos decorados, e o wrapper que torna o build igual em todo lugar |
| [0035](lessons/0035-a-runnable-artifact.md) | Um artefato executável | Empacotar o que você construiu para que alguém com nada além de um JDK consiga executá-lo |
| [0036](lessons/0036-where-memory-goes.md) | Para onde vai a memória | Os cinco lugares em que a JVM coloca memória, e qual OutOfMemoryError nomeia qual deles |
| [0037](lessons/0037-the-shape-of-an-object.md) | A forma de um objeto | Um objeto pequeno é quase todo cabeçalho, e a flag que o encolhe vem desligada por padrão |
| [0038](lessons/0038-the-allocation-that-never-happened.md) | A alocação que nunca aconteceu | A escape analysis pode eliminar uma alocação por completo, e uma única gravação em campo a traz de volta |
| [0039](lessons/0039-collectors-and-the-trade.md) | Collectors e o trade-off que você está fazendo | Cinco collectors, um trade-off de três vias, e por que o padrão costuma ser a resposta certa |
| [0040](lessons/0040-reading-a-gc-log.md) | Lendo um log de garbage collection | Uma linha de log diz quanto foi coletado, quanto tempo levou, e se você deve se importar |
| [0041](lessons/0041-a-benchmark-you-can-trust.md) | Um benchmark em que você pode confiar | Por que o loop de medição óbvio mente, e a configuração do harness que em silêncio não mede nada |
| [0042](lessons/0042-from-profile-to-proof.md) | Do profile à prova | Grave a execução, leia para onde foi o tempo, mude uma coisa e prove o ganho |
| [0043](lessons/0043-what-counts-as-breaking.md) | O que conta como quebra | Três tipos de compatibilidade, e a mudança que é segura para compilar contra e fatal para executar contra |
| [0044](lessons/0044-designing-a-signature.md) | Projetando uma assinatura | Os tipos de parâmetro e de retorno decidem o que quem chama pode fazer, e a maior parte do estrago é feita na fronteira |
| [0045](lessons/0045-evolving-a-type.md) | Evoluindo um tipo sem quebrá-lo | Como acrescentar algo a uma interface, um record, um enum e uma hierarquia sealed depois que outras pessoas dependem deles |
| [0046](lessons/0046-deprecation-that-works.md) | Depreciação que funciona | Marcar algo como deprecated não muda nada a menos que você diga o que acontece em seguida |
| [0047](lessons/0047-settling-it-from-the-source.md) | Resolvendo pela fonte | Onde procurar quando a discussão é sobre o que o Java faz, e qual documento responde a qual pergunta |
| [0048](lessons/0048-reviewing-java.md) | Revisando Java | Nomear o que uma abstração custa, em vez de dizer que ela parece errada |
| [0049](lessons/0049-does-this-framework-earn-its-place.md) | Este framework merece seu lugar | O último julgamento da etapa 7, feito a partir das restrições do serviço e não das promessas do framework |
| [0050](lessons/0050-the-module-system.md) | O sistema de módulos | O module-info.java substitui o JAR como a fronteira que o compilador e o runtime reconhecem, requires e exports decidem o que a atravessa, e o encapsulamento forte significa que uma class pública em um pacote não exportado é invisível fora do próprio módulo |
| [0051](lessons/0051-runtime-images.md) | Imagens de runtime | O jlink monta uma imagem de runtime a partir de nada além do fecho transitivo dos módulos com que mandam ele começar, mas apenas a partir de módulos explícitos, e uma aplicação que depende de um único módulo automático não pode ser linkada de jeito nenhum |
| [0052](lessons/0052-reflection-and-annotations.md) | Reflection e anotações | Este é o projeto final da etapa 8: a reflection lê e chama a própria forma de uma class em tempo de execução em vez de em tempo de compilação, uma anotação é um dado inerte até que algo a leia via reflection, e todo framework fora do escopo deste arco é construído exatamente a partir desses dois mecanismos |

## Referência

- [Glossário](GLOSSARY.md): termos canônicos deste tópico
- [Recursos](RESOURCES.md): fontes confiáveis, cada uma anotada com o que cobre
- [Igualdade, hashing e ordenação](reference/equality-hashing-and-ordering.md): os três contratos, e qual comparação escrever
- [Modelagem](reference/modelling.md): qual construção usar, com o que cada uma te compromete, e as regras fáceis de lembrar errado
- [Idioma e a biblioteca](reference/idiom-and-library.md): as decisões de biblioteca que um revisor percebe, e as armadilhas que lançam exceção onde ninguém olha
- [Concorrência](reference/concurrency.md): qual garantia cada construção dá, qual modelo se encaixa na carga de trabalho, e o que significa o sintoma diante de você
- [Testes e build](reference/testing-and-build.md): a tarefa de build que cada comando realmente executa, o double a usar, e a falha que significa que o artefato está errado
- [O runtime](reference/the-runtime.md): para onde vai a memória, qual collector atende a qual requisito, e a medição que sustenta uma afirmação
- [Julgamento](reference/judgment.md): quais mudanças quebram o quê, como aposentar uma API, e como argumentar a decisão a partir da fonte
- [O sistema de módulos](reference/the-module-system.md): a folha da etapa 8, com as três condições para acesso entre módulos, o que cada diretiva faz, e onde o código de um jar vai parar

## Como isto funciona

Cada lição é curta e autocontida. Os gabaritos ficam recolhidos: primeiro lembre, depois abra. A prática no mundo real importa mais do que a leitura, e espaçá-la é o ponto. Tudo o que ainda estiver confuso no fim de uma lição vale ser perseguido até a fonte primária antes de seguir adiante.
