---
title: Python
description: "Domine Python em produção: entregue-o tipado, testado, empacotado e perfilado"
type: topic
---

# Aprendizado: Python

Torne-se o engenheiro em quem a equipe confia para ser dono de Python: capaz de entregar um serviço ou uma ferramenta Python tipados, testados e empacotados, levar um traceback ou um profile até a causa raiz em vez de chutar, e dizer concretamente por que o uso esperto que alguém faz do dinamismo do Python vai machucá-lo.

**Comece aqui:** [0001. Nomes são vínculos, não caixas](lessons/0001-names-are-bindings.md)
**Última lição:** [0044. Julgamento](lessons/0044-judgment.md)

## O sucesso se parece com isto

- Prever o que um argumento padrão mutável, uma closure sobre uma variável de loop e uma lista compartilhada fazem, antes de executar o código.
- Entregar um pacote que instala e roda em uma máquina que não é aquela em que foi escrito.
- Acrescentar type hints que um checker verifica, e corrigir o que ele reporta em vez de silenciá-lo.
- Escrever testes `pytest` que falham de forma informativa, usando fixtures e parametrização em vez de corpos de teste copiados.
- Encontrar a parte lenta com um profiler e provar a correção com uma medição.
- Escolher entre threads, processos e `asyncio` a partir da forma da carga de trabalho, e dizer o que o GIL impede e o que não impede.
- Implementar um método dunder ou um context manager quando o data model pede um, e reconhecer quando uma função simples é a melhor resposta.
- Revisar o Python de alguém e nomear com precisão por que uma class, uma metaclass ou uma cadeia de herança é a ferramenta errada ali.

## Restrições

- Não pressupõe Python prévio. Experiência em outra linguagem encurta as primeiras etapas, mas não é exigida, e traz hábitos que o Python pune em silêncio: uma class onde uma função bastaria, um loop onde uma comprehension se lê melhor, uma cópia defensiva que a linguagem já fez.
- Precisa apenas do CPython e de um terminal em qualquer sistema operacional suportado. Nada no arco exige ferramentas pagas, uma conta na nuvem ou uma segunda máquina.
- O CPython é a implementação de referência do início ao fim. Outras implementações aparecem apenas onde o comportamento realmente difere.
- As práticas são programas pequenos que cabem em uma sessão. Espaçá-las ao longo dos dias é o mecanismo, não um inconveniente.
- Tipagem e empacotamento mudam mais rápido do que a linguagem. Afirmações sensíveis à versão são verificadas contra a documentação atual e a PEP relevante, e toda lição que depende de uma versão diz qual.

## Fora do escopo

- Frameworks web como assuntos próprios: Django, FastAPI, Flask.
- A stack científica e de machine learning como assunto: NumPy, pandas, PyTorch. Veja [`llm/finetuning`](../../llm/finetuning/) para essa fronteira.
- Distribuição além de wheels publicados em um índice: conda, pacotes de sistema operacional, binários congelados de arquivo único.
- Internos do CPython além do ponto em que deixam de prever o comportamento do programa: bytecode, a C API, escrever módulos de extensão.
- Python 2, e a migração a partir dele.
- Imagens de contêiner: colocar um wheel e seu interpretador em uma imagem, e executar, proteger e depurar esse contêiner, fica em [`infrastructure/containers`](../../infrastructure/containers/).

## O arco

Sete etapas, do zero ao nível sênior. Não é uma lista de lições: uma etapa leva várias lições e as fronteiras são flexíveis.

| Etapa | Lições | Cobre | Concluída quando |
|---|---|---|---|
| 1. Fundamentos | 0001 a 0007 | Objetos e nomes, mutabilidade e aliasing, listas, dicts, sets, tuplas, truthiness, comprehensions, funções e passagem de argumentos | Consegue prever aliasing e mutação sem executar o código |
| 2. Idioma | 0008 a 0014 | Iteradores e generators, context managers, exceções como fluxo de controle, `dataclasses`, módulos e pacotes, a biblioteca padrão que vale conhecer | Recorre a um generator ou a um context manager em vez de escrever à mão o loop e o `try/finally` |
| 3. Tipos e ferramentas | 0015 a 0021 | Anotações, generics, `Protocol`, rigor do checker, linting e formatação, ambientes virtuais, gerenciamento de dependências e de projeto, construir um wheel | Um checker rigoroso passa, e outra pessoa consegue instalar o resultado |
| 4. O data model | 0022 a 0027 | Métodos dunder, `__init__` contra `__new__`, properties, descriptors, atributos de class contra de instância, method resolution order, por que metaclasses quase nunca são a resposta | Implementa o protocolo de que um tipo precisa, e consegue dizer quando não fazê-lo |
| 5. Testes | 0028 a 0033 | Mecânica do `pytest`, fixtures e escopo, parametrização, property-based testing, o que merece um mock e o que não merece, cobertura como sinal e não como meta | Tem uma suíte de testes que pegou uma regressão antes de um humano |
| 6. Concorrência e desempenho | 0034 a 0039 | Threads, processos, `asyncio`, o que o GIL realmente serializa, chamadas bloqueantes dentro de um event loop, profiling, o custo da busca de atributos e da alocação | Escolhe o modelo de concorrência a partir da carga de trabalho e prova o ganho a partir de um profile |
| 7. Julgamento | 0040 a 0044 | Design de API e de pacotes, depreciação, revisão, ler a biblioteca padrão e as PEPs em busca de respostas | Tem a confiança para tomar a decisão e explicá-la a outra pessoa |

## Lições

Siga estas na ordem.

| # | Lição | Ensina |
|---|---|---|
| [0001](lessons/0001-names-are-bindings.md) | Nomes são vínculos, não caixas | A atribuição vincula um nome a um objeto e nunca o copia, então dois nomes podem significar uma coisa só |
| [0002](lessons/0002-mutability-and-copying.md) | Mutabilidade e cópia | A mutabilidade pertence ao objeto, então um contêiner imutável ainda pode guardar algo que muda |
| [0003](lessons/0003-lists-and-slicing.md) | Listas e slicing | Uma fatia copia, métodos in-place retornam None, e += muta o que + reconstruiria |
| [0004](lessons/0004-dicts-and-sets.md) | Dicts e sets | Chaves precisam ser hashable, a busca tem um idioma certo para cada intenção, e uma view não é um snapshot |
| [0005](lessons/0005-truthiness-none-and-equality.md) | Truthiness, None e igualdade | Vazio é falsy mas não é None, então o idioma de padrão errado rejeita zero e a string vazia |
| [0006](lessons/0006-functions-and-arguments.md) | Funções e argumentos | Os valores padrão são avaliados uma vez na definição, e quem chama vê cada mutação que você faz |
| [0007](lessons/0007-comprehensions.md) | Comprehensions | Uma expressão que constrói um contêiner, com seu próprio escopo e um limite que vale respeitar |
| [0008](lessons/0008-the-iteration-protocol.md) | O protocolo de iteração | Por que for funciona com qualquer coisa, e por que algumas dessas coisas só podem ser percorridas uma vez |
| [0009](lessons/0009-generators.md) | Generators | Uma função que pausa, mantém seu estado local e produz valores só quando pedido |
| [0010](lessons/0010-exceptions.md) | Exceções | Pedir perdão em vez de permissão, e capturar exatamente o que você consegue tratar |
| [0011](lessons/0011-context-managers.md) | Context managers | Um bloco com saída garantida, e como escrever um em seis linhas |
| [0012](lessons/0012-dataclasses.md) | Dataclasses | init, repr e igualdade gerados, e escolher a forma certa para um pacote de dados |
| [0013](lessons/0013-modules-and-packages.md) | Módulos e pacotes | Um módulo roda uma vez, um import vincula um nome, e como os dois produzem todo erro de import que você já viu |
| [0014](lessons/0014-the-standard-library.md) | A biblioteca padrão | Os módulos que apagam código que você estava prestes a escrever, e os que evitam uma dependência |
| [0015](lessons/0015-annotations-are-claims.md) | Anotações são afirmações | O interpretador as guarda e nunca as verifica, e é isso que faz valer a pena escrevê-las |
| [0016](lessons/0016-making-a-checker-useful.md) | Tornando um checker útil | Configurar o rigor, ler os códigos de erro, e estreitar em vez de silenciar |
| [0017](lessons/0017-generics-and-protocols.md) | Generics e protocols | Manter o tipo do elemento através de uma função, e tipar uma forma em vez de uma class |
| [0018](lessons/0018-types-at-the-boundary.md) | Tipos na fronteira | Transformar o Any vindo de JSON, do ambiente e de linhas de banco de dados em algo sobre o que um checker consegue raciocinar |
| [0019](lessons/0019-environments-and-dependencies.md) | Ambientes e dependências | Isolamento por projeto, a diferença entre um requisito e um lock, e quem fixa o quê |
| [0020](lessons/0020-building-a-package.md) | Construindo um pacote | O que é um wheel, o que os metadados precisam dizer, e provar que o artefato instala |
| [0021](lessons/0021-lint-and-format.md) | Lint e formatação | Encerrar a discussão sobre estilo, e as famílias de regras que encontram defeitos reais |
| [0022](lessons/0022-attribute-lookup.md) | Busca de atributos | Onde a notação de ponto realmente procura, e por que um atributo de class é compartilhado por toda instância |
| [0023](lessons/0023-properties-and-descriptors.md) | Properties e descriptors | Transformar um atributo em código sem mudar um único ponto de chamada |
| [0024](lessons/0024-dunder-methods.md) | Métodos dunder | Quais protocolos um tipo deveria implementar, e quais recorrem a outros como alternativa |
| [0025](lessons/0025-construction.md) | Construção | O que `__init__` não controla, quando `__new__` é necessário, e dar nome aos seus construtores |
| [0026](lessons/0026-inheritance-and-mro.md) | Herança e o MRO | O que super realmente faz, por que a ordem é calculada, e quando a composição vence |
| [0027](lessons/0027-metaclasses-and-why-not.md) | Metaclasses, e por que não | O que uma instrução class realmente faz, e os quatro hooks que substituem quase toda metaclass |
| [0028](lessons/0028-what-a-test-asserts.md) | O que um teste afirma | Um comportamento por teste, uma mensagem de falha que dispensa debugger, e o assert simples |
| [0029](lessons/0029-fixtures.md) | Fixtures | O setup como uma dependência que o teste pede, com um teardown que roda aconteça o que acontecer |
| [0030](lessons/0030-parametrisation.md) | Parametrização | Um corpo de teste, muitos casos, e uma falha que nomeia o caso que quebrou |
| [0031](lessons/0031-test-doubles.md) | Test doubles | O que substituir, o que deixar em paz, e por que o patch recebe o caminho onde o nome é usado |
| [0032](lessons/0032-property-based-testing.md) | Property-based testing | Declarar o que sempre precisa valer, e deixar uma biblioteca encontrar a entrada que quebra isso |
| [0033](lessons/0033-coverage-and-confidence.md) | Cobertura e confiança | Por que 100 por cento não prova nada, para que serve o número, e em quais testes confiar |
| [0034](lessons/0034-the-gil-precisely.md) | O GIL, com precisão | O que ele serializa, o que ele não protege, e o que muda sem ele |
| [0035](lessons/0035-threads-and-shared-state.md) | Threads e estado compartilhado | Um pool em vez de threads cruas, uma fila em vez de um lock, e a exceção que ninguém viu |
| [0036](lessons/0036-processes-and-interpreters.md) | Processos e interpretadores | Paralelismo real para computação, e o que custa enviar dados através de uma fronteira |
| [0037](lessons/0037-asyncio.md) | asyncio | Uma thread, milhares de esperas, e a chamada bloqueante que trava todas elas |
| [0038](lessons/0038-choosing-a-model.md) | Escolhendo um modelo | Uma pergunta decide, e a medição resolve o resto |
| [0039](lessons/0039-measuring-before-optimising.md) | Medindo antes de otimizar | Para onde o tempo realmente vai, e por que as micro-otimizações que te ensinaram já não valem |
| [0040](lessons/0040-designing-an-api.md) | Projetando uma API | A assinatura é o contrato, e tudo o que é observável vira parte dele, quer você queira ou não |
| [0041](lessons/0041-changing-a-published-api.md) | Mudando uma API publicada | Uma depreciação que os usuários realmente veem, e o que conta como breaking change |
| [0042](lessons/0042-reviewing-python.md) | Revisando Python | O que procurar, em que ordem, e como separar um defeito de uma preferência |
| [0043](lessons/0043-reading-the-source.md) | Lendo o código-fonte | Obter a resposta da biblioteca padrão e das PEPs quando a documentação para |
| [0044](lessons/0044-judgment.md) | Julgamento | Quando quebrar as regras das etapas anteriores, e como defender a decisão |

## Referência

- [Glossário](GLOSSARY.md): termos canônicos deste tópico
- [Recursos](RESOURCES.md): fontes confiáveis, cada uma anotada com o que cobre
- [Mutabilidade e cópia](reference/mutability-and-copying.md): quais tipos mudam, o que cada idioma de cópia copia, e quem consegue ver
- [Iteração e generators](reference/iteration-and-generators.md): o que é consumido uma vez, o que sobrevive a uma segunda passada, e qual ferramenta do itertools se encaixa
- [Exceções e limpeza](reference/exceptions-and-cleanup.md): a hierarquia, o que cada cláusula garante, e qual built-in lançar
- [Tipagem](reference/typing.md): grafias atuais, formas de estreitamento, códigos de erro, e qual forma usar em uma fronteira
- [Projeto e empacotamento](reference/project-and-packaging.md): um pyproject.toml anotado, a gramática de especificadores, e as verificações antes de publicar
- [Data model](reference/data-model.md): a ordem de busca de atributos, o mapa de dunders, o protocolo de descriptors, e qual hook substitui uma metaclass
- [Testes](reference/testing.md): escopos de fixtures, formas de parametrização, qual double usar, e como ler um relatório de cobertura
- [Concorrência e desempenho](reference/concurrency-and-performance.md): qual modelo para qual carga de trabalho, os números medidos por trás disso, e como ler um profile
- [API e revisão](reference/api-and-review.md): decisões de assinatura, o que conta como quebra, o checklist de revisão, e onde encontrar uma resposta

## Como isto funciona

O arco está completo: as sete etapas estão escritas, da lição 0001 à lição 0044. Siga-as na ordem, ou comece pela etapa cujo "Concluída quando" você ainda não consegue demonstrar.

Cada lição é curta e autocontida. Os gabaritos ficam recolhidos: primeiro lembre, depois abra. A prática no mundo real importa mais do que a leitura, e espaçá-la é o ponto. Tudo o que ainda estiver confuso no fim de uma lição vale ser perseguido até a fonte primária antes de seguir adiante.
