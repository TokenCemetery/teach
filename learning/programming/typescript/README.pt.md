---
title: TypeScript
description: "Domine uma codebase TypeScript: faça o compilador rejeitar os estados que não deveriam existir"
type: topic
---

# Aprendizado: TypeScript

Torne-se o engenheiro de confiança para assumir uma codebase TypeScript em um time: capaz de modelar um domínio para que o compilador rejeite os estados que não deveriam existir, manter type assertions fora do código que carrega peso, validar o que cruza uma fronteira de runtime em vez de presumir que os tipos se mantiveram, e revisar os tipos de alguém e dizer concretamente por que um generic engenhoso está custando mais do que entrega.

**Comece aqui:** [0001. Valores e coerção](lessons/0001-values-and-coercion.md)
**Última lição:** [0049. De confiança para tomar a decisão](lessons/0049-trusted-to-make-the-call.md), que encerra o arco

## O sucesso se parece com isto

- Prever o que o JavaScript faz com coerção, closures, `this` e o event loop, antes de executar o código e sem a ajuda do sistema de tipos.
- Transformar um conjunto de estados ilegais em um tipo que o compilador rejeita, e provar a exaustividade com `never`.
- Ler a mensagem de erro de um generic até a causa, em vez de recorrer a `as`.
- Dizer exatamente o que sobrevive à compilação e o que é apagado, e validar todo valor que entra no programa vindo de fora dele.
- Configurar o compilador com intenção: nomear o que cada flag de rigor compra e por que as configurações de módulo e de target são o que são.
- Escrever uma função genérica cuja inferência funciona, para que quem chama não anote nada.
- Publicar um pacote cujos tipos sejam utilizáveis pelos consumidores, incluindo a saída de declarações e os exports que ele anuncia.
- Revisar um pull request e dizer com precisão por que um conditional type, uma assertion ou um `enum` é a ferramenta errada ali.

## Restrições

- Não pressupõe TypeScript prévio, nem mais JavaScript do que o arco ensina. TypeScript é um sistema de tipos sobre o JavaScript, então a semântica do JavaScript é ensinada onde quer que explique o comportamento que um tipo não consegue explicar.
- A fronteira entre tempo de compilação e runtime é tratada como uma linha rígida do começo ao fim, porque quase todo erro sério em TypeScript é uma afirmação sobre o runtime que só o compilador chegou a verificar.
- Precisa apenas de um runtime JavaScript e de um terminal em qualquer sistema operacional suportado, com o playground online substituindo os dois quando uma prática só precisa ver um tipo. Nenhuma ferramenta paga, nenhuma conta de nuvem, nenhum framework.
- As práticas são programas pequenos e pequenos experimentos com tipos que cabem em uma sessão.
- O TypeScript lança versões a cada poucos meses e o sistema de tipos ganha expressividade real nessas versões. Afirmações sensíveis à versão são conferidas contra as release notes, e toda lição que depende de uma versão diz qual.

## Fora do escopo

- Frameworks e bibliotecas de UI como assuntos por si só: React, Angular, Vue, Svelte, Next.js.
- Bundlers e ferramentas de monorepo como assuntos: webpack, Vite, esbuild, Turborepo. A resolução de módulos é ensinada a partir do próprio modelo do compilador, que é com o que essas ferramentas precisam concordar.
- Outros runtimes como assuntos: Deno, Bun, a plataforma do navegador. Eles aparecem apenas onde o comportamento de fato difere.
- Node.js como plataforma por si só: streams, clustering, addons nativos.
- Programação no nível de tipos como esporte. Mapped types e conditional types são ensinados até o ponto em que servem a quem chama, e a etapa 6 diz explicitamente onde fica esse ponto.

## O arco

Sete etapas, do zero ao nível sênior. Não é uma lista de lições: uma etapa leva várias lições e as fronteiras são flexíveis.

| Etapa | Lições | Cobre | Concluída quando |
|---|---|---|---|
| 1. O JavaScript por baixo | 0001 a 0007 | Valores e coerção, objetos e protótipos, closures, `this`, módulos, o event loop, promises e async | Consegue prever o que um programa faz em runtime, sem nenhum tipo envolvido |
| 2. Tipos sobre valores | 0008 a 0014 | Primitivos, arrays e tuplas, unions, literal types, atribuibilidade estrutural, narrowing, tipos de função, `readonly`, o que a inferência já sabe | Anota apenas onde a inferência não alcança |
| 3. Rigor e o compilador | 0015 a 0021 | A família `strict` flag por flag, as flags de rigor que `strict` ainda omite, `unknown` contra `any`, assertions contra declarações, `tsconfig`, resolução de módulos, `target` e `lib` | Mantém o rigor ligado e corrige o que ele reporta em vez de suprimi-lo, e liga as verificações que `strict` deixa de fora |
| 4. Modelagem | 0022 a 0028 | Discriminated unions, exaustividade com `never`, branded types, generics e restrições, `satisfies`, interface contra type alias | Estados ilegais são irrepresentáveis, e é o compilador que prova isso |
| 5. A fronteira de runtime | 0029 a 0035 | O que é apagado, arquivos de declaração, validar a entrada na borda, erros como valores, consumir dependências sem tipos ou com tipos errados | Nenhum valor entra no programa sem validação, e nenhuma assertion sustenta peso |
| 6. Ferramentas no nível de tipos | 0036 a 0042 | Mapped types e conditional types, `infer`, template literal types, variância e atribuibilidade, inferência para APIs de bibliotecas, desempenho do compilador | Escreve uma API cujos tipos servem a quem chama, e para antes da engenhosidade |
| 7. Julgamento | 0043 a 0049 | Publicar uma superfície de tipos pública, o que conta como mudança incompatível em tipos, revisão, ler as release notes e as próprias declarações do compilador | Tem a confiança para tomar a decisão e explicá-la a outra pessoa |

## Lições

Siga estas na ordem.

| # | Lição | Ensina |
|---|---|---|
| [0001](lessons/0001-values-and-coercion.md) | Valores e coerção | Sete primitivos, dois vazios e um operador de igualdade que converte antes de comparar |
| [0002](lessons/0002-objects-are-references.md) | Objetos são referências | const impede a reatribuição, o spread copia um nível e readonly desaparece em runtime |
| [0003](lessons/0003-prototypes-and-classes.md) | Protótipos e classes | A busca de propriedades percorre uma cadeia, e a sintaxe de class é uma das maneiras de construir essa cadeia |
| [0004](lessons/0004-this-and-the-call-site.md) | this é decidido pela chamada | this vem de como uma função é chamada, então extrair um método o joga fora |
| [0005](lessons/0005-scope-and-closures.md) | Escopo e closures | Uma closure captura o binding e não o valor, e let cria um por iteração |
| [0006](lessons/0006-event-loop-and-promises.md) | O event loop, promises e await | As microtasks são esvaziadas antes do próximo timer, e dois awaits seguidos são sequenciais |
| [0007](lessons/0007-modules.md) | Módulos | Imports sofrem hoisting e são ligados ao vivo, e um arquivo sem import nem export não é um módulo |
| [0008](lessons/0008-the-types-you-write.md) | Os tipos que você escreve | O vocabulário de anotações, e um compilador que já reclama antes de você configurá-lo |
| [0009](lessons/0009-tuples-and-readonly.md) | Tuplas e readonly | Um comprimento fixo que o compilador impõe nas leituras e esquece no push |
| [0010](lessons/0010-unions-and-literal-types.md) | Unions e literal types | Um valor com mais de um tipo possível, e o alargamento que joga fora o tipo interessante |
| [0011](lessons/0011-structural-assignability.md) | Atribuibilidade estrutural | O formato decide o que vai para onde, exceto pela única verificação que só dispara em um object literal recém-criado |
| [0012](lessons/0012-narrowing.md) | Narrowing | O fluxo de controle diz ao compilador no que uma union se transformou, e exatamente duas coisas desfazem isso |
| [0013](lessons/0013-function-types.md) | Tipos de função | Os parâmetros são verificados na direção que você espera, a menos que você tenha escrito um método |
| [0014](lessons/0014-what-inference-already-knows.md) | O que a inferência já sabe | Até onde a inferência alcança, para que escrever uma anotação signifique algo quando você o faz |
| [0015](lessons/0015-what-strict-turns-on.md) | O que strict liga | Sete verificações atrás de uma flag, cada uma com uma falha que ela existe para pegar |
| [0016](lessons/0016-the-checks-strict-leaves-out.md) | As verificações que strict deixa de fora | Mais seis verificações que vale ter, uma que o compilador se recusa a habilitar e uma que não faz nada |
| [0017](lessons/0017-unknown-instead-of-any.md) | unknown em vez de any | Um tipo aceita tudo e não deixa você fazer nada, o outro aceita tudo e não verifica nada |
| [0018](lessons/0018-an-assertion-is-not-a-check.md) | Uma assertion não é uma verificação | Todas as maneiras de mandar o compilador parar de verificar, e o que cada uma custa quando a afirmação está errada |
| [0019](lessons/0019-reading-a-tsconfig.md) | Lendo um tsconfig | Quais arquivos o compilador olha, de onde vêm as configurações e por que o arquivo gerado diz o que diz |
| [0020](lessons/0020-target-and-lib.md) | target e lib | Uma configuração muda o que é emitido e a outra muda o que existe, e nomear a segunda joga fora o padrão |
| [0021](lessons/0021-module-resolution.md) | Resolução de módulos | As mesmas opções do compilador dão veredictos opostos dependendo de um único campo no package.json |
| [0022](lessons/0022-discriminated-unions.md) | Discriminated unions | Uma propriedade literal compartilhada, e uma union que o compilador consegue desmontar |
| [0023](lessons/0023-exhaustiveness-with-never.md) | Exaustividade com never | Adicionar um membro a uma union deveria quebrar todo switch que o ignorou, e uma linha faz isso acontecer |
| [0024](lessons/0024-illegal-states.md) | Tornando estados ilegais irrepresentáveis | Conte os estados que o seu tipo permite, depois remova os que o seu domínio não tem |
| [0025](lessons/0025-branded-types.md) | Branded types | Tipagem nominal em cima de um sistema estrutural, e a única assertion que ela custa |
| [0026](lessons/0026-generics-and-constraints.md) | Generics e restrições | Um parâmetro de tipo é uma promessa a quem chama, e uma restrição é o que permite cumpri-la |
| [0027](lessons/0027-satisfies.md) | satisfies | Verificar um valor contra um tipo sem deixar o tipo substituir o que você escreveu |
| [0028](lessons/0028-interface-or-type.md) | interface ou type | Um reporta um membro conflitante onde você o escreveu e o outro o reporta em outro lugar |
| [0029](lessons/0029-nothing-survives-to-run-time.md) | Nada sobrevive até o runtime | Todo tipo é uma afirmação sobre um programa que não existe mais no momento em que a afirmação importaria |
| [0030](lessons/0030-unknown-at-the-edge.md) | unknown na borda | Encontre todo lugar em que um valor chega de fora, e dê a cada um o único tipo honesto |
| [0031](lessons/0031-parsing-instead-of-asserting.md) | Fazer parsing em vez de afirmar | Uma única declaração que produz tanto a verificação em runtime quanto o tipo estático |
| [0032](lessons/0032-type-predicates-and-assertion-functions.md) | Type predicates e assertion functions | Uma assinatura que promete uma verificação, e um corpo com o qual nada a compara |
| [0033](lessons/0033-errors-as-values.md) | Erros como valores | Uma falha no tipo de retorno é uma que o compilador consegue obrigar você a tratar |
| [0034](lessons/0034-declaration-files.md) | Arquivos de declaração | Tipos para código que o compilador nunca vê, e quanto vale essa promessa |
| [0035](lessons/0035-when-the-declaration-lies.md) | Quando a declaração mente | O compilador acredita na declaração e o runtime nunca ouviu falar dela |
| [0036](lessons/0036-mapped-types.md) | Mapped types | Transformar todas as propriedades de um tipo de uma vez, e remover as que você não quer |
| [0037](lessons/0037-conditional-types.md) | Conditional types | Um tipo que se ramifica, e uma union que ele desmonta em silêncio primeiro |
| [0038](lessons/0038-infer.md) | infer | Extrair um tipo de uma posição em vez de pedir a quem chama que o nomeie |
| [0039](lessons/0039-template-literal-types.md) | Template literal types | Um padrão de string que o compilador verifica, e os nomes de chave que ele consegue construir |
| [0040](lessons/0040-variance-and-assignability.md) | Variância e atribuibilidade | Em qual direção um tipo pode viajar, e o array que erra isso de propósito |
| [0041](lessons/0041-inference-for-library-apis.md) | Inferência para APIs de bibliotecas | Projetar a assinatura para que quem chama não anote nada |
| [0042](lessons/0042-knowing-when-to-stop.md) | Saber quando parar | Medir o que um tipo engenhoso custa, depois justificá-lo para quem quer que o mantenha |
| [0043](lessons/0043-what-counts-as-a-breaking-change.md) | O que conta como mudança incompatível | Quais edições em um tipo publicado quebram um consumidor, e em qual direção cada uma precisa viajar |
| [0044](lessons/0044-publishing-a-type-surface.md) | Publicando uma superfície de tipos | O que um consumidor realmente resolve quando importa o seu pacote, e como verificar isso antes dele |
| [0045](lessons/0045-the-consumers-settings-are-not-yours.md) | As configurações do consumidor não são as suas | Um consumidor rigoroso herda as afirmações de um autor relaxado e não tem como perceber |
| [0046](lessons/0046-the-typescript-that-does-not-erase.md) | O TypeScript que não é apagado | Quatro recursos que emitem código que você não pediu, e a flag que os nomeia |
| [0047](lessons/0047-settling-it-from-the-source.md) | Resolvendo pela fonte | Qual documento responde a uma pergunta sobre o compilador, e como ler as declarações que ele distribui |
| [0048](lessons/0048-reviewing-typescript.md) | Revisando TypeScript | Nomear o que um tipo custa, em vez de dizer que ele parece complicado |
| [0049](lessons/0049-trusted-to-make-the-call.md) | De confiança para tomar a decisão | O último julgamento do arco, e o que o compilador nunca ia fazer por você |

## Referência

- [Glossário](GLOSSARY.md): termos canônicos deste tópico
- [Recursos](RESOURCES.md): fontes confiáveis, cada uma anotada com o que cobre
- [Coerção e igualdade](reference/coercion-and-equality.md): valores falsy, o que `==` converte, qual operador de padrão escrever
- [Event loop e promises](reference/event-loop-and-promises.md): ordem das filas, combinadores e os erros de async que nenhum compilador reporta
- [Tipos sobre valores](reference/types-over-values.md): o que cada anotação compra, até onde a inferência alcança e as brechas que o compilador deixa abertas de propósito
- [Rigor e o compilador](reference/strictness-and-the-compiler.md): qual flag pega qual falha, de onde vem uma configuração e como um import é resolvido
- [Modelagem](reference/modelling.md): qual formato remove o estado ilegal, e qual declaração pega o erro onde você o cometeu
- [A fronteira de runtime](reference/the-runtime-boundary.md): onde os valores entram, o que os verifica e quais afirmações nada verifica
- [Ferramentas no nível de tipos](reference/type-level-tools.md): qual construção calcula qual tipo, e o teste pelo qual uma construção engenhosa precisa passar
- [Julgamento](reference/judgment.md): quais edições quebram um consumidor, o que não é apagado e como argumentar a decisão a partir da fonte

## Como isto funciona

Cada lição é curta e autocontida. Os gabaritos ficam recolhidos: primeiro lembre, depois abra. A prática no mundo real importa mais do que a leitura, e espaçá-la é o ponto. Tudo o que ainda estiver confuso no fim de uma lição vale ser perseguido até a fonte primária antes de seguir adiante.
