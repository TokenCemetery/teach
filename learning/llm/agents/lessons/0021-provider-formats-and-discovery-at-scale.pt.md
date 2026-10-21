---
title: "21. Formatos de provedor e descoberta de ferramentas em escala"
description: "Como o MCP e os formatos de rede específicos de provedor são camadas separadas e por que carregar toda ferramenta no contexto não escala para muitos servidores conectados"
type: lesson
---

# Lição 21. Formatos de provedor e descoberta de ferramentas em escala

**Ligação com a missão:** Entender os limites da descoberta ingênua de ferramentas quando um agente se conecta a muitos servidores MCP e reconhecer quando trocar o carregamento antecipado de ferramentas por uma descoberta preguiçosa ou programática.
**Fonte principal:** [Article: "Code Execution with MCP", Anthropic Engineering](https://www.anthropic.com/engineering/code-execution-with-mcp)
**Pré-requisitos:** [Lição 20](0020-mcp-tools-resources-and-prompts.md)

## Aquecimento

1. ▢ Na Lição 3 você aprendeu dois formatos de rede: a Anthropic representa uma chamada de ferramenta com `input_schema`, e a OpenAI usa um formato diferente chamado `function.parameters`. Se você muda da API da Anthropic para a da OpenAI, precisa mudar o seu servidor MCP, o seu cliente MCP ou ambos?

<details markdown="1"><summary>Verificação</summary>

Nenhum dos dois. O seu servidor MCP continua o mesmo (ele sabe expor ferramentas no formato MCP). O seu harness muda, porque precisa traduzir as definições de ferramenta MCP para o formato de rede do provedor que o modelo espera. O provedor do modelo muda, mas o protocolo MCP não.

</details>

2. ▢ Na Lição 9, você aprendeu sobre o inchaço do conjunto de ferramentas: se você apresenta ao modelo definições de ferramenta demais, ele fica mais lento, se confunde ou esquece qual ferramenta usar. Quando um agente se conecta a cinco servidores MCP com dez ferramentas cada, o modelo vê cinquenta definições de ferramenta logo de início?

<details markdown="1"><summary>Verificação</summary>

Só se o harness carregar as cinquenta definições no contexto antes de o loop começar. Essa é a abordagem ingênua. Mas há outros jeitos: o harness poderia carregar as ferramentas apenas quando o modelo as pedisse, ou traduzir as definições de ferramenta em código que o modelo pode explorar e chamar programaticamente.

</details>

## Saiba isto

### Duas camadas independentes

O MCP é um protocolo entre um harness de agente e ferramentas ou fontes de dados externas. Ele define como um cliente e um servidor conversam e que capacidades um servidor pode expor. Mas o MCP não se importa com o formato de rede que o modelo usa.

Ao mesmo tempo, o modelo tem um provedor, e esse provedor tem uma maneira específica de representar chamadas de ferramenta. A API da Anthropic aceita ferramentas em um formato. A API da OpenAI as aceita em outro. Esse formato de rede é uma camada separada entre o harness e o modelo.

Essas duas camadas são independentes:

- O cliente MCP (lado do harness) fala MCP com o servidor MCP. O servidor MCP é agnóstico sobre qual modelo acabará usando essas ferramentas.
- O harness então traduz as definições de ferramenta MCP para o formato de rede do provedor que o modelo espera. Anthropic? Use `input_schema`. OpenAI? Use `function.parameters`.

O harness precisa fazer a tradução, porque fica no meio. Mas mudar uma camada não exige reescrever a outra. Se você troca de provedor de modelo, não reescreve seus servidores MCP. Se você se conecta a um novo servidor MCP, o formato de rede entre o harness e o modelo não muda.

### Descoberta de ferramentas em escala

Em um único agente, você pode ligar à mão duas ou três ferramentas no contexto no início. O inchaço do conjunto de ferramentas (Lição 9) aparece por volta de cinco a dez ferramentas. Mas e se o harness está conectado a uma dúzia de servidores MCP, cada um com dez a vinte ferramentas? Centenas de definições de ferramenta.

A abordagem ingênua é carregar toda definição de ferramenta na inicialização, traduzir cada uma para o formato de rede do provedor e entregar todas ao modelo no contexto inicial. Isso reproduz o inchaço do conjunto de ferramentas em uma escala muito maior. O modelo lê centenas de definições, desperdiça tokens com descrições de que não precisa e fica mais lento a cada turno porque toda ferramenta está no contexto. E, se uma nova ferramenta é adicionada a um servidor conectado, o contexto inteiro e o comportamento do modelo mudam.

Esse é o problema da descoberta de ferramentas em escala: você pode se conectar a muitos servidores, mas não carregando tudo de antemão.

### A ideia da execução de código

O artigo da Anthropic Engineering "Code Execution with MCP" propõe uma solução: em vez de carregar definições de ferramenta no contexto, apresentar as ferramentas disponíveis como código que o agente pode descobrir e chamar programaticamente.

Por exemplo:

- O harness define uma função auxiliar list_available_tools() que consulta os servidores MCP conectados e devolve um diretório de funções chamáveis: seus nomes, descrições e parâmetros.
- O harness define uma função auxiliar call_tool(name, args) que recebe o nome de uma ferramenta e argumentos, encontra a ferramenta nos servidores conectados e a invoca.
- Em vez de dar ao modelo cinquenta definições de ferramenta de início, o harness diz ao modelo: "Você pode chamar list_available_tools() para ver o que pode fazer, ou call_tool(name, args) para fazer algo específico."

Agora o modelo tem duas meta-ferramentas: ferramentas para descobrir e chamar outras ferramentas. Ele pode explorar o espaço de ferramentas sem carregar todas as definições no contexto no início. Chama list_available_tools() quando precisa encontrar uma ferramenta, aprende o que está disponível naquele momento e então usa o que precisa. O contexto residente continua pequeno.

Isso troca o carregamento antecipado pela descoberta preguiçosa. O modelo precisa gastar um turno chamando list_available_tools() antes de poder chamar uma ferramenta específica, então há um custo de latência. Mas, se o harness está conectado a cinquenta servidores, os tokens economizados por não manter toda definição de ferramenta no contexto superam o custo do turno extra.

### Quando usar cada abordagem

O carregamento antecipado (pôr toda ferramenta no contexto na inicialização) funciona quando:

- Você tem um pequeno conjunto fixo de ferramentas (duas a dez).
- As ferramentas são relevantes para toda tarefa do agente.
- O contexto não é restrito.

O carregamento preguiçoso (definir list_available_tools() e call_tool() e deixar o modelo descobrir o que precisa) funciona quando:

- Você tem muitas ferramentas (dezenas ou mais).
- As ferramentas são especializadas e nem todas são relevantes para toda tarefa.
- O contexto é restrito e cada token importa.
- O custo de latência de um turno extra é aceitável.

A descoberta programática (apresentar ferramentas como código que o modelo pode ler e executar) combina as duas ideias: contexto inicial pequeno (apenas as funções de descoberta) e a capacidade de explorar o espaço de ferramentas sem carregar definições à mão.

## Prática

1. ▢ Você está usando a API da Anthropic com três servidores MCP. Você muda para a API da OpenAI. Você precisa atualizar os seus servidores MCP, o seu harness ou ambos?

<details markdown="1"><summary>Verificação</summary>

Apenas o seu harness. Os servidores MCP não mudam; eles continuam expondo ferramentas no formato MCP. O seu harness já traduzia definições MCP para o formato de rede da Anthropic; agora as traduz para o formato da OpenAI. A camada de tradução muda, mas os servidores e o protocolo não.

</details>

2. ▢ Seu agente está conectado a dez servidores MCP com um total de cento e cinquenta ferramentas. Você quer usar a ideia de "code execution with MCP": definir list_available_tools() e deixar o modelo descobrir o que precisa. Quais são duas consequências desse design?

<details markdown="1"><summary>Dica</summary>

Pense no tamanho do contexto e na latência. Quando o modelo pede a lista? O que isso custa?

</details>

<details markdown="1"><summary>Verificação</summary>

O contexto fica menor porque você não está carregando cento e cinquenta definições de ferramenta de antemão, apenas duas funções e talvez uma breve descrição do que elas fazem. A latência aumenta porque o modelo precisa chamar list_available_tools() em um turno em que quer explorar, acrescentando pelo menos um turno extra antes de poder chamar uma ferramenta específica. É uma troca que vale a pena se o contexto é apertado ou se as ferramentas raramente são todas necessárias juntas.

</details>

3. ▢ O seu harness tem apenas três ferramentas, e todas são relevantes para toda tarefa que o agente executa. Você deve usar carregamento antecipado, carregamento preguiçoso ou descoberta programática?

    - a) Carregamento preguiçoso com list_available_tools()
    - b) Carregamento antecipado: pôr as três no contexto no início
    - c) Descoberta programática com funções call_tool()
    - d) Alternar quais ferramentas estão no contexto para economizar tokens

<details markdown="1"><summary>Verificação</summary>

b) Com um conjunto pequeno de ferramentas sempre relevantes, o carregamento antecipado é o mais simples e rápido. Você não desperdiça tokens com funções de descoberta, não acrescenta latência e o modelo sempre tem as ferramentas de que precisa. A descoberta preguiçosa e a programática acrescentam sobrecarga sem benefício quando o conjunto de ferramentas é pequeno e universal. A opção d é um antipadrão: alternar ferramentas dentro e fora do contexto cria confusão e não determinismo.

</details>

4. ▢ Você define list_available_tools() para consultar todos os servidores MCP conectados e devolver os nomes e descrições de suas ferramentas. Quando o modelo chama essa função, a chamada conta para os seus tokens de API?

<details markdown="1"><summary>Verificação</summary>

Sim. Chamar list_available_tools() custa tokens exatamente como chamar qualquer outra função: o modelo envia a chamada, o harness a executa e o resultado volta na transcrição. Você está trocando os tokens gastos em definições de ferramenta de antemão pelos tokens gastos em chamadas de descoberta. Com muitas ferramentas, a troca costuma ser positiva.

</details>

## Prática no mundo real

- [ ] Desenhe um diagrama mostrando as duas camadas: o protocolo MCP de um lado (harness para servidores externos), o formato de rede do provedor do outro (harness para modelo). Rotule o que acontece se você trocar de provedor contra se trocar de servidor MCP.
- [ ] Estime a diferença de custo em tokens entre o carregamento antecipado (pôr cem ferramentas no contexto) e o carregamento preguiçoso (list_available_tools() sob demanda) para o seu próprio agente. A preguiça faz sentido?
- [ ] Amanhã: Implemente uma função list_available_tools() simples que consulta um servidor MCP real a que você tem acesso e devolve um resumo que o modelo possa ler.

## Para ir além

- [Article: "Code Execution with MCP", Anthropic Engineering](https://www.anthropic.com/engineering/code-execution-with-mcp)
- [Specification: Model Context Protocol](https://modelcontextprotocol.io/specification)
- [Recursos](../RESOURCES.md)

---

Não ficou claro? Releia a fonte principal no topo, já que esta lição a comprime e é na compressão que o entendimento escapa. Consulte o [glossário](../GLOSSARY.md) para qualquer termo que pareceu escorregadio.

Se o problema é a lição em si, e não o material, isso é um defeito: [abra uma issue](https://github.com/TokenCemetery/teach/issues).
