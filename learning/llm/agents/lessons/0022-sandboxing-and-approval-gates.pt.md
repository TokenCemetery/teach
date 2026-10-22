---
title: "22. Sandboxing e portões de aprovação"
description: "Fronteiras de execução e pontos de verificação humanos que protegem contra erros do modelo"
type: lesson
---

# Lição 22. Sandboxing e portões de aprovação

**Ligação com a missão:** Para decidir o que o agente pode fazer sem supervisão, você precisa entender os dois mecanismos complementares que protegem contra erros: sandboxes impõem o que o código consegue alcançar, não importa o que o modelo peça, e portões de aprovação acrescentam um ponto de verificação humano antes de ações de alto risco.
**Fonte principal:** [Article: "Building Effective Agents", Anthropic Engineering](https://www.anthropic.com/engineering/building-effective-agents)
**Pré-requisitos:** [Lição 21](0021-provider-formats-and-discovery-at-scale.md), [Harness](../GLOSSARY.md)

## Aquecimento

1. ▢ Qual é a diferença entre uma ferramenta de cliente e uma ferramenta de servidor, em termos de onde o código roda e de quem o controla?

<details markdown="1"><summary>Verificação</summary>

Uma ferramenta de cliente roda no código do próprio harness, então você controla sua execução por inteiro. Uma ferramenta de servidor roda na infraestrutura do provedor em nome do harness, então o provedor controla a fronteira de execução. Isso importa para a segurança porque o comportamento de uma ferramenta de cliente depende do seu código, enquanto o comportamento de uma ferramenta de servidor depende do que o provedor permite.

</details>

2. ▢ Na Lição 21, aprendemos que, em vez de pré-carregar toda definição de ferramenta no contexto, o modelo pode descobrir e chamar ferramentas dinamicamente. Nomeie um benefício dessa abordagem e um custo que ela introduz.

<details markdown="1"><summary>Verificação</summary>

Benefício: o contexto do modelo não explode com centenas de definições de ferramenta, então ele pode raciocinar com mais clareza e as definições de ferramenta podem ser mantidas pequenas ou buscadas sob demanda. Custo: o modelo agora precisa chamar primeiro uma ferramenta de descoberta ou introspecção antes de saber o que está disponível, o que acrescenta uma ida e volta, ou chama uma ferramenta que supõe existir e falha se ela não existe, exigindo tratamento de erros e retries.

</details>

## Saiba isto

### O julgamento de um modelo não é uma fronteira de segurança

Você pode esperar: "O modelo vai ser esperto com o que faz com o acesso que eu dou. Posso contar com o modelo decidindo não apagar dados de produção nem enviar e-mails sem permissão."

Essa esperança se quebra de várias formas. Um modelo pode estar errado: pode entender mal as consequências de uma chamada de ferramenta. Um modelo pode ser manipulado por conteúdo que lê: se uma prévia de arquivo ou uma mensagem do usuário contém texto adversário projetado para enganar o modelo, esse texto pode influenciar o raciocínio dele. Um modelo pode simplesmente cometer um erro: o raciocínio pode falhar em escala, especialmente em cenários de muita ramificação ou sob pressão de tempo. Por essas razões, tudo o que o seu harness de fato permite que uma ferramenta toque (quais arquivos em disco, quais hosts de rede, quais comandos executar) precisa ser imposto por código, e não pela esperança de que o modelo se comporte corretamente.

É por isso que o harness, e não o modelo, é a fronteira de segurança.

### O que é um sandbox

Um sandbox é uma fronteira de execução que o harness impõe ao que o código de uma ferramenta consegue alcançar, independentemente dos argumentos que o modelo enviou. As instruções do modelo nunca são, em si, uma propriedade de segurança.

Fronteiras comuns de sandbox incluem:

- **Fronteira de sistema de arquivos**: A ferramenta só pode ler ou escrever arquivos dentro de uma árvore de diretórios específica (por exemplo, `/home/user/work`, mas não `/etc` nem `/home/other_user`). Mesmo que o modelo peça à ferramenta que acesse um caminho fora dessa árvore, o sandbox o rejeita em tempo de execução.
- **Isolamento de rede**: A ferramenta não tem nenhum acesso à rede, ou só alcança uma lista de permissão de hosts específicos. O modelo não consegue convencer o harness a deixá-lo alcançar domínios arbitrários.
- **Limites de recursos**: Tempo de CPU, memória e tempo de relógio têm teto. Se o código do modelo fica preso em um loop infinito, o sandbox o encerra em vez de consumir todos os recursos.
- **Isolamento de processo**: A ferramenta roda em um processo ou contêiner separado com privilégios reduzidos, de modo que não consegue afetar o harness nem acessar recursos do sistema que não lhe foram explicitamente concedidos.

A ideia-chave é que essas fronteiras são impostas em tempo de execução, no código do harness, e não no nível da linguagem. Uma ferramenta não consegue escapar de um sandbox escrevendo código esperto. O sandbox é a regra que o harness aplica, e não um recurso que a ferramenta respeita.

### O que é um portão de aprovação

Um portão de aprovação é um mecanismo complementar: antes de executar uma chamada de ferramenta de uma categoria arriscada, o harness pausa e espera uma pessoa revisar a chamada específica e aprová-la ou rejeitá-la.

Portões de aprovação se aplicam a ações com estas propriedades:

- Irreversíveis ou difíceis de desfazer: apagar arquivos, enviar e-mails, fazer transações financeiras, publicar na internet.
- De alta consequência se erradas: o que está em jogo é dinheiro de verdade, dano de verdade ou exposição real de privacidade.
- Genuinamente difíceis de prever: a decisão do modelo é razoável, mas não obviamente correta, então vale a pena acrescentar julgamento humano.

Um portão pausa o loop do agente e apresenta a chamada de ferramenta pendente (com seus argumentos e o efeito esperado) a uma pessoa, espera a aprovação ou a rejeição e depois retoma ou interrompe o loop de acordo.

### Sandboxes e portões de aprovação são complementares, não alternativas

São duas proteções diferentes que trabalham juntas:

- Um sandbox limita o dano que qualquer chamada pode causar, mesmo se aprovada ou executada automaticamente. Se uma chamada der errado de algum jeito, o sandbox contém o raio da explosão. "Roda em um ambiente restrito" é sempre verdade.
- Um portão de aprovação acrescenta um ponto de decisão humano para as chamadas de maior risco. Ele não evita todo dano; apenas garante que as chamadas com maior probabilidade de causar arrependimento passem primeiro por olhos humanos.

Se você coloca todas as chamadas em sandbox mas nunca coloca portão em nada, um erro não detectado do modelo ainda pode causar dano dentro das fronteiras do sandbox. Se você coloca portão em toda chamada de ferramenta, o agente deixa de ser autônomo e vira uma pessoa fazendo todo o trabalho com passos extras, anulando o ponto da automação.

O equilíbrio certo: coloque portão em uma classe estreita de ações genuinamente de alto risco (apagar, enviar, publicar, gastar), em que o julgamento humano vale o custo de latência, e coloque tudo em sandbox para que qualquer coisa fora desse portão não consiga escapar de suas fronteiras mesmo se algo der errado.

## Prática

1. ▢ Você está construindo um agente que pode ler e resumir documentos de um repositório compartilhado. O repositório tem 10.000 arquivos, e alguns deles contêm dados sensíveis de clientes que o agente não deve acessar. Você quer adicionar uma ferramenta de cliente que deixa o agente ler arquivos. Que fronteira de sandbox você deve impor, e por quê?

<details markdown="1"><summary>Verificação</summary>

Você deve impor uma fronteira de sistema de arquivos: a ferramenta só pode ler arquivos dentro de uma árvore de diretórios específica e aprovada (por exemplo, todos os arquivos na pasta "public_docs", mas nada na pasta "confidential"). Essa fronteira é verificada em tempo de execução quando o modelo chama a ferramenta; mesmo que o modelo peça à ferramenta que leia um caminho na pasta confidencial, o sandbox o rejeita. Isso protege contra o modelo ser enganado pelo conteúdo de um arquivo ou cometer um erro de raciocínio sobre o que é seguro ler. O julgamento do modelo ("isto parece público") não é a fronteira; o código é.

</details>

2. ▢ Seu agente pode escrever código e executá-lo em um interpretador Python em sandbox. O sandbox limita a CPU a 30 segundos e a memória a 1 GB. O modelo escreve um programa que começa um loop infinito. O sandbox vai pará-lo?

<details markdown="1"><summary>Dica</summary>

Pense no que acontece quando o limite de CPU é excedido enquanto o código está rodando e se o harness consegue detectar e impor esse limite.

</details>

<details markdown="1"><summary>Verificação</summary>

Sim, o sandbox vai pará-lo. Quando o limite de CPU de 30 segundos é atingido, o harness encerra o processo. O código do modelo nunca roda para sempre; o sandbox impõe o limite de recursos em tempo de execução, e não em tempo de interpretação ou compilação. Essa é uma razão pela qual limites de recursos são essenciais em um sandbox: eles impedem que até um código bem-intencionado consuma todos os recursos.

</details>

3. ▢ Você está projetando um agente que pode enviar e-mails em nome de um usuário. Qual destas é uma boa razão para adicionar um portão de aprovação antes de o agente enviar um e-mail?

    - a) O modelo pode escrever uma linha de assunto gramaticalmente incorreta.
    - b) O modelo pode enviar um e-mail ao destinatário errado ou com o conteúdo errado, e, uma vez enviado, o e-mail não pode ser desenviado.
    - c) O modelo pode deixar o servidor de e-mail lento.
    - d) O modelo pode ficar sem ideias sobre qual e-mail enviar em seguida.

<details markdown="1"><summary>Verificação</summary>

**b)** O modelo pode enviar um e-mail ao destinatário errado ou com o conteúdo errado, e, uma vez enviado, o e-mail não pode ser desenviado. Esta é uma ação irreversível e de alta consequência, em que o julgamento humano vale o custo de latência. A opção a não tem consequência alta o bastante (o modelo consegue redigir bem). A opção c não é um erro do modelo (é sobre carga do sistema). A opção d não faz sentido (o modelo para quando lhe pedem).

</details>

4. ▢ Explique por que um sandbox não consegue evitar todos os erros mas ainda assim pode ser essencial. Dê um exemplo.

<details markdown="1"><summary>Verificação</summary>

Um sandbox impõe fronteiras sobre que recursos o código consegue alcançar, e não sobre que erros o código comete. Por exemplo, um sandbox pode impedir que uma ferramenta escreva em `/etc/passwd` rejeitando a escrita em tempo de execução, mas não consegue impedir o modelo de escrever o conteúdo errado em um arquivo aprovado, como sobrescrever um arquivo de configuração em `/home/user/config/` com sintaxe inválida. O trabalho do sandbox é conter o dano, e não garantir a correção. Os portões de aprovação tratam das decisões de alto risco que precisam de julgamento humano; os sandboxes tratam das fronteiras de execução que impedem o raio da explosão de se expandir além do controle.

</details>

## Prática no mundo real

- [ ] Desenhe um diagrama de uma chamada de ferramenta: mostre o modelo, o harness, o código da ferramenta e o sandbox em volta dele. Rotule o que o modelo controla (seu raciocínio e a escolha da ferramenta) e o que o harness controla (a fronteira).
- [ ] Liste três ferramentas do seu próprio trabalho ou de um sistema que você usa todo dia. Para cada uma, identifique uma ação arriscada (se houver) que se beneficiaria de um portão de aprovação e uma fronteira de sandbox que faria sentido.
- [ ] Amanhã: Leia o artigo "Building Effective Agents" e anote um exemplo concreto de sandbox ou de portão. Explique em uma frase por que essa escolha de design importa.

## Para ir além

- [Article: "Building Effective Agents", Anthropic Engineering](https://www.anthropic.com/engineering/building-effective-agents)
- [Recursos](../RESOURCES.md)

---

Não ficou claro? Releia a fonte principal no topo, já que esta lição a comprime e é na compressão que o entendimento escapa. Consulte o [glossário](../GLOSSARY.md) para qualquer termo que pareceu escorregadio.

Se o problema é a lição em si, e não o material, isso é um defeito: [abra uma issue](https://github.com/TokenCemetery/teach/issues).
