---
title: "32. Privilégio mínimo e o confused deputy"
description: "Como restringir as capacidades do agente para que a injeção de prompt cause dano contido em vez de uma brecha catastrófica"
type: lesson
---

# Lição 32. Privilégio mínimo e o confused deputy

**Ligação com a missão:** Projetar as fronteiras de acesso de cada ferramenta do agente para que conteúdo não confiável possa enganar o agente, mas não consiga induzi-lo a usar mal capacidades que ele nunca deveria ter tido.
**Fonte principal:** [Reference: "OWASP Top 10 for LLM Applications", OWASP GenAI Security Project](https://genai.owasp.org/llm-top-10/)
**Pré-requisitos:** [Lição 31](0031-prompt-injection-and-the-lethal-trifecta.md), [Sandbox](../GLOSSARY.md)

## Aquecimento

1. ▢ Nomeie as três condições da tríade letal da Lição 31.

<details markdown="1"><summary>Verificação</summary>

Acesso a dados privados, exposição a conteúdo não confiável e capacidade de comunicar-se com o exterior. Remova qualquer uma e o ataque falha.

</details>

2. ▢ Na Lição 31, você projetou uma ferramenta para evitar um ataque de injeção de prompt quebrando uma condição da tríade. Se você tivesse quebrado a condição de comunicação externa, descreva como isso seria na prática.

<details markdown="1"><summary>Verificação</summary>

A ferramenta ou não conseguiria enviar informação para lugar nenhum, ou só para um canal que o atacante não alcança. Por exemplo, uma ferramenta draft_email que apenas guarda os e-mails localmente em vez de enviá-los, ou uma ferramenta que só consegue escrever em uma tabela de staging que exige revisão manual antes de os dados serem compartilhados.

</details>

## Saiba isto

### Privilégio mínimo: restrinja cada ferramenta exatamente ao que ela precisa

Privilégio mínimo é um princípio de segurança: cada ferramenta deve ter acesso apenas ao recurso ou à ação específica de que realmente precisa, e não a um acesso amplo "só por precaução, caso seja útil depois". Para um agente, isso significa projetar a fronteira de sandbox de cada ferramenta com permissão estreita.

Exemplos:

- Uma ferramenta que lê a agenda de hoje deve ler apenas do arquivo de calendário, e não do sistema de arquivos inteiro
- Uma ferramenta que consulta o pedido de um cliente deve consultar apenas os pedidos desse cliente, e não todos os pedidos da empresa
- Uma ferramenta que envia um e-mail de recibo deve conseguir enviar apenas de um endereço fixo, e não da caixa de correio inteira
- Uma ferramenta que edita um arquivo de configuração deve editar apenas esse arquivo, e não arquivos arbitrários do diretório de configuração

O princípio vale para credenciais também. Se uma ferramenta precisa se autenticar em um serviço externo, deve usar uma credencial restrita a esse serviço e a essa ação, e não uma conta de administrador ampla.

Por que isso importa para agentes? Porque o acesso amplo é exatamente o que torna um exploit custoso para a organização. Quando um agente é enganado por uma injeção a chamar uma ferramenta a que tem acesso, as consequências dependem do que essa ferramenta de fato consegue alcançar.

### O padrão confused deputy: autoridade legítima, mal usada

O confused deputy é um padrão clássico de segurança, nomeado pela primeira vez nos anos 1980, que se aplica diretamente a agentes. Um confused deputy é um programa que tem autoridade legítima e ampla e é induzido a usar mal essa autoridade em nome de um atacante. O programa não está comprometido no sentido de executar código malicioso; está fazendo exatamente o que suas ferramentas legítimas permitem, apenas em nome de instruções que nunca foram do usuário.

Um agente com uma vulnerabilidade de confused deputy se parece com isto:

1. O agente tem uma ferramenta ampla: send_email pode enviar de qualquer endereço da caixa de correio da empresa
2. O agente lê conteúdo não confiável: um convite de calendário com uma instrução injetada
3. A instrução pede ao agente que encaminhe uma conversa de e-mail confidencial a um endereço externo
4. O agente chama send_email com os parâmetros do atacante
5. A ferramenta executa a chamada porque é uma chamada legítima a send_email com parâmetros válidos. A ferramenta não sabe que o pedido se originou de uma injeção, e não da intenção real do usuário.

O e-mail agora foi exfiltrado, não porque o modelo foi "hackeado", mas porque você deu a um agente uma capacidade ampla e não a restringiu a uma tarefa estreita.

A correção não é pedir ao modelo com mais força no prompt. A correção é projetar a ferramenta de forma estreita: em vez de send_email para a caixa de correio inteira, projete uma ferramenta chamada send_receipt que só consegue enviar para endereços de e-mail de clientes com um template fixo. Agora uma injeção ainda pode induzir o modelo a chamar send_receipt, mas essa chamada fica restrita ao que send_receipt tem permissão para fazer.

### Cadeia de suprimentos do MCP: a confiança é transitiva

As lições 20-21 cobriram o Model Context Protocol (MCP) e como um agente se conecta a servidores MCP para acessar ferramentas. Do ângulo da segurança, conectar-se a um servidor MCP significa estender a sua fronteira de confiança para incluir quem opera esse servidor.

Um servidor MCP malicioso ou comprometido pode:

- Deturpar as descrições de ferramentas para fazer chamadas danosas parecerem benignas
- Devolver dados enganosos nos resultados de ferramenta, sobre os quais o agente então raciocinará
- Observar toda chamada de ferramenta que o agente faz e toda peça de contexto que ele envia

Quando o seu harness se conecta a um servidor MCP de terceiros, você está confiando no operador desse servidor tanto quanto confia no seu próprio código. Se o servidor está comprometido ou é operado por um adversário, ele se torna mais um canal de injeção.

A defesa é a mesma de qualquer risco de cadeia de suprimentos: conecte-se apenas a servidores em que você confia e restrinja a conexão. Por exemplo:

- Não dê a um agente acesso a todos os servidores MCP disponíveis; conecte-se apenas aos servidores específicos de que ele precisa
- Use autenticação e criptografia nas conexões MCP
- Audite as descrições de ferramentas que um servidor MCP fornece e entenda que acesso você está concedendo
- Presuma que os dados que você envia a uma ferramenta MCP podem se tornar públicos ou ser usados de forma indevida

Servidores MCP não são arriscados de forma singular; são apenas mais uma ferramenta. O princípio é o mesmo: restrinja o acesso.

### Juntando tudo: fronteiras de permissão por ferramenta, por tarefa

O princípio de design que une essas lições é que uma fronteira de permissão deve ser restrita de forma deliberada, por ferramenta e por tarefa, e não uma única credencial ampla que o agente inteiro compartilha.

Ao projetar um agente:

1. Liste cada ferramenta de que o agente precisa
2. Para cada ferramenta, pergunte: qual é o acesso mínimo de que essa ferramenta precisa para cumprir seu propósito?
3. Crie uma fronteira de sandbox para essa ferramenta que conceda exatamente esse acesso, e nada além
4. Se uma ferramenta precisa se autenticar (com um banco de dados, uma API, um sistema de arquivos), crie uma credencial restrita a essa ferramenta e a esse nível de acesso, e não uma credencial que alcance qualquer coisa

Uma ferramenta estritamente restrita é a coisa concreta que transforma "o modelo foi enganado por uma injeção" de um comprometimento catastrófico em um erro contido e de baixa consequência. O agente lê a injeção, o modelo a entende, o modelo chama a ferramenta injetada, e a ferramenta se recusa a executar a ação solicitada porque a ação está fora do seu escopo.

## Prática

1. ▢ Você está projetando uma ferramenta para um agente que gerencia contas de usuário. A ferramenta precisa atualizar o endereço de e-mail de um usuário no banco de dados da empresa. Seu primeiro rascunho dá a ela esta credencial: uma conta de banco de dados com permissão UPDATE na tabela users inteira.

Por que isso tem escopo excessivo, e qual seria um design melhor?

<details markdown="1"><summary>Verificação</summary>

A credencial concede permissão UPDATE na tabela inteira, o que significa que a ferramenta poderia atualizar as informações de qualquer usuário, e não apenas o endereço de e-mail específico do usuário específico que está sendo gerenciado. Um design melhor criaria uma stored procedure no banco de dados que aceita apenas o ID do usuário e o novo e-mail, e concederia à credencial da ferramenta permissão para executar somente essa procedure. Assim, mesmo que uma injeção induza o agente a chamar a ferramenta com parâmetros inesperados, o banco de dados se recusará a executar qualquer coisa fora do escopo da procedure.

</details>

2. ▢ Um agente tem acesso a uma ferramenta send_email restrita a enviar apenas de `support@company.com` e apenas para endereços de e-mail que casam com o padrão `*@customer-*.com`. Uma injeção tenta induzi-lo a enviar uma mensagem para `attacker@evil.com`. O que impede o ataque?

<details markdown="1"><summary>Dica</summary>

A própria ferramenta impõe o escopo. Pense em onde essa verificação acontece e por que nenhuma instrução de prompt está envolvida.

</details>

<details markdown="1"><summary>Verificação</summary>

A validação da ferramenta, que roda no harness antes de a mensagem ser enviada. A ferramenta valida o destinatário contra seu padrão permitido e se recusa a enviar porque `attacker@evil.com` não casa. A injeção teve sucesso em mudar o comportamento do agente (o agente pretendia enviar), mas falhou porque a fronteira de permissão da ferramenta impediu a ação danosa. Esse é um controle no nível da ferramenta, e não no nível do prompting, então é confiável.

</details>

3. ▢ Sua organização oferece um servidor MCP que expõe eventos do calendário da empresa. Você descobre que uma empresa terceira construiu um cliente MCP que se conecta ao seu servidor para ajudar a gerenciar reuniões. Qual destas afirmações é verdadeira?

    - a) Isso é seguro desde que o seu servidor MCP devolva apenas dados públicos de calendário
    - b) O cliente da terceira agora tem, na prática, acesso de leitura aos dados de calendário que o seu servidor devolve
    - c) Você deve usar criptografia entre o seu servidor e o cliente para garantir que nem os operadores do seu servidor consigam ver os dados
    - d) A empresa terceira não pode usar os dados de forma indevida porque são apenas eventos de calendário, e não credenciais de usuário

<details markdown="1"><summary>Verificação</summary>

**b)** O cliente da terceira, e quem o opera, consegue ver e potencialmente usar de forma indevida todos os dados de calendário que o servidor devolve. Dados públicos continuam sendo dados; mesmo que os eventos do calendário não sejam secretos, o operador terceiro agora tem visibilidade da agenda da sua organização, o que poderia ser usado para espionagem corporativa ou engenharia social. A criptografia (opção c) protegeria os dados em trânsito, mas não impediria o operador do cliente de vê-los. O escopo do acesso (público contra privado) não muda a implicação de segurança: você estendeu sua fronteira de confiança para incluir o operador terceiro. Esse é o risco da cadeia de suprimentos do MCP.

</details>

4. ▢ Você está projetando uma ferramenta para um agente que processa tickets de suporte ao cliente. A ferramenta precisa enviar uma resposta por e-mail a um cliente. Descreva um design de privilégio mínimo que evitaria um ataque de confused deputy em que uma injeção induz o agente a encaminhar a um cliente uma conversa de e-mail interna e confidencial.

<details markdown="1"><summary>Verificação</summary>

Em vez de uma ferramenta send_email genérica, projete uma ferramenta chamada send_support_response que recebe apenas dois parâmetros: o ID do ticket e o texto da resposta. A ferramenta busca o endereço de e-mail do cliente a partir do ID do ticket, valida que o texto da resposta não excede um comprimento razoável e envia apenas a resposta (sem anexos, sem outros e-mails). A credencial da ferramenta só tem permissão para enviar do endereço de suporte e apenas para endereços de e-mail de clientes vinculados a tickets válidos. Agora uma injeção pode induzir o agente a chamar send_support_response, mas a chamada fica restrita pelo escopo da ferramenta. O agente não consegue encaminhar e-mails internos, não consegue enviar para endereços arbitrários e não consegue enviar nada que não seja uma resposta de suporte, porque a ferramenta não oferece um jeito de fazer essas coisas.

</details>

## Prática no mundo real

- [ ] Pegue uma ferramenta que você projetou ou usa com frequência. Mapeie suas permissões atuais. Anote uma permissão que ela tem e que excede o que ela estritamente precisa para seu propósito principal, e um jeito de removê-la.
- [ ] Escolha um servidor MCP ao qual você estaria disposto a conectar um agente. Pesquise ou contate o operador e entenda: que dados o servidor vê, como são usados, como são protegidos, quem tem acesso aos logs? Anote seu nível de confiança e qualquer risco residual.
- [ ] Amanhã: Projete uma ferramenta que implementa o privilégio mínimo de forma deliberada recusando um pedido plausível mas fora do escopo. Escreva uma especificação que nomeie o pedido que ela receberia durante um ataque de confused deputy e explique por que o design da ferramenta impede que ele tenha sucesso.

## Para ir além

- [Reference: "OWASP Top 10 for LLM Applications", OWASP GenAI Security Project](https://genai.owasp.org/llm-top-10/)
- [Recursos](../RESOURCES.md)

---

Não ficou claro? Releia a fonte principal no topo, já que esta lição a comprime e é na compressão que o entendimento escapa. Consulte o [glossário](../GLOSSARY.md) para qualquer termo que pareceu escorregadio.

Se o problema é a lição em si, e não o material, isso é um defeito: [abra uma issue](https://github.com/TokenCemetery/teach/issues).
