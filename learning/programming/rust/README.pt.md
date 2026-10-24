---
title: Rust
description: "Domine Rust: projete com ownership em vez de brigar com o borrow checker, depois publique o crate"
type: topic
---

# Aprendizado: Rust

Torne-se o engenheiro de confiança para assumir Rust em um time: capaz de projetar com ownership em vez de negociar com o borrow checker, moldar erros e APIs para que os tipos carreguem as invariantes, recorrer a `unsafe` apenas atrás de uma fronteira que possa ser justificada e publicar um crate do qual outras pessoas dependem e que conseguem atualizar.

**Comece aqui:** [0001. Ownership e drop](lessons/0001-ownership-and-drop.md)
**Última lição:** [0067. Testes baseados em propriedades e testes de snapshot](lessons/0067-property-based-and-snapshot-testing.md)

## O sucesso se parece com isto

- Prever qual empréstimo o compilador vai rejeitar, e por quê, antes de compilar.
- Escolher entre possuir, emprestar, contagem de referências e mutabilidade interior a partir de quanto tempo os dados realmente precisam viver.
- Projetar um tipo de erro que quem chama consiga tratar, e dizer quando entrar em panic é a escolha correta.
- Remover duplicação com traits e generics sem tornar as assinaturas ilegíveis, e saber quando o dispatch dinâmico é a resposta melhor.
- Escrever código assíncrono que não trava, e explicar o que acontece ao segurar um lock através de um ponto de `await`.
- Justificar cada bloco `unsafe` pela invariante que ele sustenta, mantê-lo atrás de uma interface segura e verificá-lo com uma ferramenta em vez de pela leitura.
- Publicar um crate com documentação, testes e uma API pública que você consiga evoluir sem quebrar quem depende dele.
- Revisar Rust e nomear com precisão por que uma anotação de lifetime, um `clone` ou um mutex compartilhado está encobrindo um problema de design.

## Restrições

- Não pressupõe Rust prévio nem experiência com programação de sistemas. A stack, o heap e o layout de memória são ensinados dentro do arco, porque ownership não se ensina sem eles.
- Precisa apenas da toolchain estável e de um terminal em qualquer sistema operacional suportado. Nada no arco exige ferramentas pagas, uma conta de nuvem ou Rust nightly.
- **Espera-se que as práticas falhem ao compilar.** Esse é o ciclo de feedback, não um revés: preveja o que o compilador vai dizer, depois descubra, e trate a diferença como a lição.
- As práticas são programas pequenos que cabem em uma sessão. Espaçá-las ao longo de dias é o mecanismo, não um inconveniente.
- Edições e releases importam aqui. Quando uma lição depende de uma edição ou de um recurso estabilizado, ela diz qual, e afirmações sensíveis à versão são conferidas contra as release notes em vez de lembradas de memória.

## Fora do escopo

- Alvos embarcados e `no_std` como assuntos por si só.
- WebAssembly, interfaces gráficas e engines de jogos.
- Frameworks web como assuntos. O código assíncrono precisa de exemplos, e eles continuam tão pequenos quanto o conceito permite.
- Escrita de macros procedurais. Macros declarativas aparecem onde é preciso ler o uso que a própria biblioteca padrão faz delas.
- Interfaces de funções estrangeiras além do que o material sobre a fronteira de `unsafe` precisa. Encapsular uma biblioteca C real é um empreendimento separado.
- Internos do compilador e do borrow checker além do ponto em que deixam de prever o que o compilador vai aceitar.

## O arco

Oito etapas, do zero ao nível sênior. Não é uma lista de lições: uma etapa leva várias lições e as fronteiras são flexíveis.

| Etapa | Lições | Cobre | Concluída quando |
|---|---|---|---|
| 1. Ownership | 0001 a 0006 | Valores, stack e heap, moves, `Copy`, empréstimos e suas regras, slices, `String` contra `&str`, shadowing | Consegue prever um erro de move ou de empréstimo antes que o compilador o reporte |
| 2. Dados e controle | 0007 a 0013 | Structs, enums, `Option` e `Result`, pattern matching e exaustividade, iteradores, closures, as coleções que vale conhecer | Modela com enums e trata a ausência sem recorrer a `unwrap` |
| 3. Erros e formato da API | 0014 a 0020 | Propagação com `?`, tipos de erro próprios, conversões `From`, panic contra erro, módulos e visibilidade, escrever documentação que compila | Escreve uma biblioteca cujas falhas quem chama consegue de fato tratar |
| 4. Traits, generics e lifetimes | 0021 a 0028 | Trait bounds, tipos associados, generics contra dispatch dinâmico, a orphan rule, anotações de lifetime e elisão, por que um lifetime não é uma duração | Lê um erro de lifetime como informação em vez de obstáculo |
| 5. Compartilhamento e threads | 0029 a 0036 | `Box`, `Rc` e `Arc`, `RefCell` e `Mutex`, `Send` e `Sync`, threads, channels, deadlock e poisoning | Escolhe uma estratégia de compartilhamento a partir dos dados em vez do hábito |
| 6. Async | 0037 a 0045 | Futures e executors, tasks e cancelamento, por que uma chamada bloqueante em código assíncrono é um bug, locks através de `await`, para que serve o pinning | Escreve código assíncrono que não trava, e consegue explicar onde travaria |
| 7. Unsafe e desempenho | 0046 a 0054 | O que `unsafe` realmente promete, comportamento indefinido, encapsular uma invariante, verificar com Miri, benchmarking, custos de alocação e de cópia | Consegue defender uma fronteira de `unsafe`, e prova uma afirmação de desempenho com uma medição |
| 8. Julgamento | 0055 a 0063 | Publicação, versionamento semântico de uma API pública, as API guidelines, revisão, ler a biblioteca padrão e as RFCs em busca de respostas | Tem a confiança para tomar a decisão e explicá-la a outra pessoa; a etapa 9 completa o primeiro passo do próprio procedimento de release, a suíte de testes passa, com a suíte que este arco ainda não tinha ensinado a escrever |
| 9. Testes | 0064 a 0067 | `#[test]` e `cargo test`, testes unitários contra testes de integração, organizar testes para uma biblioteca, testes baseados em propriedades e testes de snapshot | Escreve e organiza uma suíte de testes do jeito que a própria biblioteca padrão faz, não só doctests e benchmarks |

## Lições

Siga estas na ordem.

| # | Lição | Ensina |
|---|---|---|
| [0001](lessons/0001-ownership-and-drop.md) | Ownership e drop | Todo valor tem exatamente um dono, e o compilador o libera quando esse dono sai de escopo |
| [0002](lessons/0002-moves-and-copy.md) | Moves e Copy | A atribuição move o ownership a menos que o tipo seja Copy, e é por isso que o nome antigo para de funcionar |
| [0003](lessons/0003-borrowing.md) | Empréstimos | Muitos empréstimos compartilhados ou um empréstimo mutável, nunca os dois, e um empréstimo termina no seu último uso |
| [0004](lessons/0004-slices-string-and-str.md) | Slices, String e str | Um slice é uma visão emprestada com um comprimento, e receber &str em uma API não custa nada a quem chama |
| [0005](lessons/0005-bindings-and-mutability.md) | Bindings e mutabilidade | Imutável por padrão, mut vale por binding, e shadowing é um novo binding, não uma alteração |
| [0006](lessons/0006-reading-a-borrow-error.md) | Lendo um erro de empréstimo | Cinco códigos de erro cobrem a maior parte da etapa 1, e cada um tem uma correção honesta e um contorno |
| [0007](lessons/0007-structs.md) | Structs e seus métodos | Uma struct é dona de seus campos, então o que você coloca nela decide quem precisa mantê-lo vivo |
| [0008](lessons/0008-enums.md) | Enums que carregam dados | Um enum diz que um valor tem exatamente uma destas formas, e essa é a ferramenta de modelagem sobre a qual o resto da etapa se apoia |
| [0009](lessons/0009-option.md) | Option e o tratamento da ausência | A ausência é um valor de outro tipo, então o compilador obriga você a dizer o que acontece quando ela chega |
| [0010](lessons/0010-result.md) | Result e a falha como valor | Uma falha é um valor de retorno e não um evento, então a assinatura diz o que pode dar errado antes de você ler o corpo |
| [0011](lessons/0011-pattern-matching.md) | Pattern matching | Um match precisa cobrir todos os casos, e o padrão decide se você emprestou o valor ou o moveu |
| [0012](lessons/0012-iterators-and-closures.md) | Iteradores e closures | Um iterador não faz nada até que algo o consuma, e uma closure captura exatamente o que usa |
| [0013](lessons/0013-collections.md) | As coleções que vale conhecer | Vec e HashMap cobrem a maior parte, e a entry API é a única coisa que vale aprender direito |
| [0014](lessons/0014-propagating-errors.md) | Propagando erros | O ponto de interrogação converte ao retornar, então o tipo de erro na sua assinatura decide o que ele vai aceitar |
| [0015](lessons/0015-designing-an-error-type.md) | Projetando um tipo de erro | Quem chama só consegue tratar o que o seu erro permite distinguir, então o formato dele é uma decisão de API |
| [0016](lessons/0016-conversions-and-boundaries.md) | Conversões e fronteiras | Uma implementação de From é onde a falha de uma camada vira a de outra, e um derive escreve as que você já entende |
| [0017](lessons/0017-panic-or-error.md) | Panic ou erro | Um panic diz que o programa está quebrado e um erro diz que a entrada estava, e uma biblioteca raramente pode decidir o primeiro |
| [0018](lessons/0018-modules-and-visibility.md) | Módulos e visibilidade | O que você torna público é o que você prometeu manter, então a árvore de módulos é uma decisão de API antes de ser uma decisão de organização |
| [0019](lessons/0019-documentation-that-compiles.md) | Documentação que compila | Um exemplo em um doc comment é um teste, então a documentação que apodrece é a que ninguém executou |
| [0020](lessons/0020-a-library-callers-can-handle.md) | Uma biblioteca que quem chama consegue tratar | Divida o crate, nomeie as falhas e decida o que o binário faz e a biblioteca não pode fazer |
| [0021](lessons/0021-traits-as-shared-behaviour.md) | Traits como comportamento compartilhado | Como um trait nomeia um comportamento que vários tipos podem fornecer, e por que o trait precisa estar em escopo antes de você poder usá-lo |
| [0022](lessons/0022-trait-bounds-and-generic-functions.md) | Trait bounds e funções genéricas | O que um bound promete ao corpo e exige de quem chama, e o que o compilador faz com ele |
| [0023](lessons/0023-associated-types.md) | Tipos associados | Por que Iterator nomeia seu Item como um tipo associado e não como um parâmetro, e o que isso decide para quem o implementa |
| [0024](lessons/0024-generics-or-dyn-trait.md) | Generics ou dyn Trait | As duas estratégias de dispatch, o que cada uma custa e a pergunta que de fato decide entre elas |
| [0025](lessons/0025-implementing-traits-you-do-not-own.md) | Implementando traits que não são seus | Coerência, o padrão newtype e por que uma implementação blanket é um compromisso e não uma conveniência |
| [0026](lessons/0026-lifetimes-are-not-durations.md) | Lifetimes não são durações | O que um parâmetro de lifetime diz sobre a relação entre empréstimos, e o que a elisão vinha fazendo por você o tempo todo |
| [0027](lessons/0027-types-that-borrow.md) | Tipos que emprestam | Colocar um parâmetro de lifetime em uma struct, e decidir se o tipo deveria ser dono dos seus dados |
| [0028](lessons/0028-reading-a-lifetime-error.md) | Lendo um erro de lifetime | As formas que um erro de lifetime assume, cada uma com a correção honesta e o contorno que ela tenta você a usar |
| [0029](lessons/0029-threads-joining-and-panics.md) | Threads, join e panics | O que criar uma thread realmente exige dos dados que você entrega a ela, e o que acontece com uma thread que entra em panic sozinha |
| [0030](lessons/0030-scoped-threads.md) | Scoped threads | Por que uma thread que não pode sobreviver ao seu escopo pode emprestar, e por que esta é a primeira coisa a recorrer, não a última |
| [0031](lessons/0031-shared-ownership.md) | Ownership compartilhado com Rc e Arc | Quando um valor precisa de vários donos em vez de um, o que a contagem custa e como um ciclo vaza |
| [0032](lessons/0032-interior-mutability.md) | Mutabilidade interior | Levar a regra de empréstimo do tempo de compilação para o tempo de execução, o que isso compra e o que custa quando você erra |
| [0033](lessons/0033-mutex-rwlock-and-poisoning.md) | Mutex, RwLock e poisoning | O que um lock realmente protege, por que o escopo do guard é a decisão de design e o que um panic enquanto se segura um lock deixa para trás |
| [0034](lessons/0034-send-and-sync.md) | Send e Sync | Os dois traits que ninguém escreve e que decidem o que pode cruzar a fronteira de uma thread, e como ler os erros que eles causam |
| [0035](lessons/0035-channels.md) | Channels | Enviar valores entre threads em vez de compartilhá-los, e o que as pontas de um channel fazem quando a outra ponta desaparece |
| [0036](lessons/0036-choosing-a-sharing-strategy.md) | Escolhendo uma estratégia de compartilhamento | As falhas que decorrem de escolher por hábito, e as perguntas que escolhem a estratégia a partir dos dados |
| [0037](lessons/0037-what-a-future-is.md) | O que é uma future | Uma máquina de estados com um único método, conduzida por quem faz o poll dela, e o que isso significa para código que parece sequencial |
| [0038](lessons/0038-wakers-executors-and-runtimes.md) | Wakers, executors e runtimes | Como uma future avisa que está pronta para receber poll de novo, e o que um runtime faz além de fazer o poll |
| [0039](lessons/0039-tasks-and-the-send-bound.md) | Tasks e o bound Send | O que criar uma task assíncrona exige da future que você entrega, e por que um método de trait assíncrono não vai satisfazer isso |
| [0040](lessons/0040-blocking-is-a-bug.md) | Bloquear é um bug | Por que uma única chamada bloqueante em uma task assíncrona trava trabalho que não tem nada a ver com ela, e o que fazer com as chamadas que você não consegue evitar |
| [0041](lessons/0041-shared-state-across-an-await.md) | Estado compartilhado através de um await | Por que um lock guard mantido através de um ponto de await é recusado, e como escolher entre os dois tipos de mutex |
| [0042](lessons/0042-cancellation.md) | Cancelamento | Parar uma future significa descartá-la, e é por isso que ninguém é avisado e o trabalho simplesmente para onde estava |
| [0043](lessons/0043-cancellation-safety.md) | Segurança de cancelamento | Se uma future pode ser descartada no meio do caminho sem perder o que já tinha pegado, e onde essa pergunta é respondida |
| [0044](lessons/0044-pinning.md) | Pinning | Por que a memória de uma future precisa parar de se mover depois que recebe poll, e o que Pin faz a respeito |
| [0045](lessons/0045-reading-an-async-failure.md) | Lendo uma falha assíncrona | As cinco maneiras como código assíncrono falha sem mensagem de erro, e como saber qual delas você está vendo |
| [0046](lessons/0046-what-unsafe-promises.md) | O que unsafe promete | As cinco coisas que um bloco unsafe permite fazer, e a obrigação que você assume ao escrever um |
| [0047](lessons/0047-raw-pointers.md) | Ponteiros crus | O que um ponteiro cru não é, o que ele custa em garantias e como criar um que seja de fato válido |
| [0048](lessons/0048-undefined-behaviour.md) | Comportamento indefinido | O que o compilador pode presumir, por que um programa que funciona ainda pode estar errado, e a lista que vale saber de cor |
| [0049](lessons/0049-checking-with-miri.md) | Verificando com Miri | A ferramenta que transforma um bug invisível de soundness em um relatório, o que ela pega e o que não consegue pegar |
| [0050](lessons/0050-encapsulating-an-invariant.md) | Encapsulando uma invariante | Envolver código unsafe em uma interface segura, e o que precisa ser verdade para que essa interface mereça o nome |
| [0051](lessons/0051-memory-orderings.md) | Memory orderings | O que um ordering realmente restringe, por que você não consegue testá-lo executando, e como verificar o que você escolheu |
| [0052](lessons/0052-measuring-before-optimising.md) | Medir antes de otimizar | Como obter um número que você consiga defender, o que o compilador faz com um benchmark que não mede nada, e o que uma medição não consegue dizer |
| [0053](lessons/0053-allocation-and-copying-costs.md) | Custos de alocação e de cópia | Onde um programa Rust realmente gasta seu tempo, e quais das correções óbvias se pagam |
| [0054](lessons/0054-defending-an-unsafe-boundary.md) | Defendendo uma fronteira de unsafe | O argumento que você precisa conseguir apresentar antes que um bloco unsafe vá para produção, e a medição que precisa vir junto |
| [0055](lessons/0055-variance.md) | Variância | Quais lifetimes podem substituir quais, por que o seu próprio tipo decide, e com o que isso compromete você |
| [0056](lessons/0056-higher-ranked-bounds.md) | Higher-ranked bounds | Escrever o quantificador que o compilador vinha imprimindo para você, e os formatos de API que precisam dele |
| [0057](lessons/0057-what-breaks-a-caller.md) | O que quebra quem chama | As mudanças que exigem uma versão major, as que só parecem seguras, e a ferramenta que diz qual é qual |
| [0058](lessons/0058-designing-for-change.md) | Projetando para a mudança | As decisões que deixam espaço para se mover depois, e as que prometem em silêncio mais do que você queria |
| [0059](lessons/0059-features-and-the-minimum-version.md) | Features e a versão mínima | Por que uma feature deve apenas acrescentar, o que a unificação faz com as suas suposições, e o que declarar uma versão mínima realmente promete |
| [0060](lessons/0060-workspaces-and-release.md) | Workspaces e release | Levar um crate ao ponto em que publicar é um único comando, e o que esse comando realmente faz |
| [0061](lessons/0061-the-api-guidelines.md) | As API guidelines | O checklist com que o ecossistema já concordou, quais itens importam mais e como usá-lo sem seguir no automático |
| [0062](lessons/0062-reading-the-source-and-the-rfcs.md) | Lendo o código-fonte e as RFCs | Responder a uma pergunta que a documentação não responde, a partir da biblioteca padrão, das tracking issues e das RFCs |
| [0063](lessons/0063-reviewing-rust.md) | Revisando Rust | O que procurar no Rust de outra pessoa, em que ordem, e quais comentários vale a pena fazer |
| [0064](lessons/0064-the-test-attribute-and-cargo-test.md) | O atributo test e cargo test | Um doctest vive em um doc comment e executa um exemplo; uma função #[test] vive no próprio código-fonte do crate e é a forma comum que quase todo teste em Rust de fato assume, e cargo test executa os dois sob o mesmo comando sem que sejam o mesmo mecanismo |
| [0065](lessons/0065-unit-versus-integration-tests.md) | Testes unitários contra testes de integração | Onde uma função #[test] vive decide o que ela enxerga, o mesmo arquivo do código sob #[cfg(test)] com acesso a todo item privado, ou um diretório tests/ separado que só enxerga o que você de fato tornou público |
| [0066](lessons/0066-organising-tests-for-a-library.md) | Organizando testes para uma biblioteca | O formato de uma suíte de integração é imposto por tudo o que você já tornou pub, o setup compartilhado vai especificamente em tests/common/mod.rs, e um binário sem lib.rs não pode ter testes de integração de forma alguma |
| [0067](lessons/0067-property-based-and-snapshot-testing.md) | Testes baseados em propriedades e testes de snapshot | Este é o fechamento da etapa 9, o proptest gera centenas de entradas e reduz uma falha à menor entrada que ainda quebra a propriedade, enquanto um teste de snapshot compara a saída de uma entrada escolhida com uma referência que um humano já revisou |

## Referência

- [Glossário](GLOSSARY.md): termos canônicos deste tópico
- [Recursos](RESOURCES.md): fontes confiáveis, cada uma anotada com o que cobre
- [Ownership e empréstimos](reference/ownership-and-borrowing.md): as regras, a lista de Copy, os códigos de erro e a correção honesta para cada um
- [O projeto](reference/the-project.md): o crate que as práticas constroem ao longo do arco, e em que estado ele deve estar ao fim de cada etapa
- [Dados e controle](reference/data-and-control.md): a folha da etapa 2, com as decisões de enum, Option e Result, as regras de padrões e as coleções
- [Erros e formato da API](reference/errors-and-api-shape.md): a folha da etapa 3, com as decisões de tipo de erro, as regras de conversão e com o que uma API pública se compromete
- [Traits e lifetimes](reference/traits-and-lifetimes.md): a folha da etapa 4, com a decisão de dispatch, as regras de coerência e a tabela de erros de lifetime
- [Compartilhamento e threads](reference/sharing-and-threads.md): a folha da etapa 5, com o procedimento de estratégia, o que cada tipo de compartilhamento custa e a tabela de falhas
- [Async](reference/async.md): a folha da etapa 6, com o modelo de poll, os bounds, a tabela de falhas e onde a segurança de cancelamento está documentada
- [Unsafe e desempenho](reference/unsafe-and-performance.md): a folha da etapa 7, com a tabela de comportamento indefinido, o que cada ferramenta pega e a disciplina de medição
- [Julgamento](reference/judgment.md): a folha da etapa 8, com as regras de variância, a tabela de mudanças incompatíveis, o checklist de release e a ordem de autoridade

## Como isto funciona

Cada lição é curta e autocontida. Os gabaritos ficam recolhidos: primeiro lembre, depois abra. A prática no mundo real importa mais do que a leitura, e espaçá-la é o ponto. Tudo o que ainda estiver confuso no fim de uma lição vale ser perseguido até a fonte primária antes de seguir adiante.
