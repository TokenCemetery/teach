---
title: "6. Escrevendo o loop"
description: "Construir o loop do agente a partir de pseudocódigo e escolher as condições de parada de propósito"
type: lesson
---

# Lição 6. Escrevendo o loop

**Ligação com a missão:** Escrever o loop do agente é a habilidade central para construir um agente você mesmo, o que serve diretamente à missão de "escrever o loop de agente para uma tarefa dada e nomear o que cada mensagem do contexto está fazendo e o que encerra o loop".
**Fonte principal:** [Article: "Building Effective Agents", Anthropic Engineering](https://www.anthropic.com/engineering/building-effective-agents)
**Pré-requisitos:** [Lição 5](0005-parallel-calls-and-errors-as-results.md), [Loop do agente](../GLOSSARY.md)

## Aquecimento

1. ▢ Da Lição 5: O que é anexado à transcrição quando uma chamada de ferramenta falha?

<details markdown="1"><summary>Verificação</summary>

Um resultado de ferramenta de erro, marcado com o id da chamada que falhou e sinalizado como erro, anexado exatamente como um resultado bem-sucedido seria. O loop não falha; o modelo vê a falha como um turno normal.

</details>

2. ▢ Da Lição 5: Por que é seguro um modelo pedir duas ferramentas em paralelo em vez de uma depois da outra?

<details markdown="1"><summary>Verificação</summary>

Porque cada chamada de ferramenta recebe seu próprio id único, e o harness devolve cada resultado marcado com esse mesmo id. O modelo sempre consegue associar um resultado de volta à chamada que o produziu, qualquer que seja a ordem de execução.

</details>

## Saiba isto

### O loop do agente como código

No fundo, um loop de agente é simples. Aqui está ele como pseudocódigo:

```text
function run_agent(model, tools, transcript, max_turns):
    for turn_count in range(max_turns):
        response = call_model(model, transcript)
        transcript.append(response)

        if response.has_no_tool_calls():
            return response.text

        for tool_call in response.tool_calls:
            result = execute_tool(tools, tool_call)
            transcript.append(result)

    return "Max turns reached"
```

Isto é o harness. O modelo escolhe qual ferramenta pedir e quando parar de pedir. O harness impõe os limites e a mecânica.

Repare na estrutura: **chamar o modelo, anexar a resposta, verificar se terminamos, senão executar as ferramentas e anexar os resultados, depois voltar ao topo do loop**. A cada turno, a transcrição cresce. Nada é guardado em memória fora da transcrição.

### Por que a transcrição precisa crescer a cada turno

Iniciantes às vezes constroem um loop assim:

```text
function run_agent_wrong(model, tools, transcript, max_turns):
    for turn_count in range(max_turns):
        response = call_model(model, transcript)

        if response.has_no_tool_calls():
            return response.text

        for tool_call in response.tool_calls:
            result = execute_tool(tools, tool_call)
            transcript.append(result)  # Only append results, not the model's request
```

Isso é um bug. Se você não anexa a resposta com a chamada de ferramenta do modelo à transcrição antes de executar a ferramenta, o modelo não vai "lembrar" que pediu a ferramenta no turno seguinte. Quando o harness chama o modelo de novo, a transcrição não diz "o modelo pediu a busca" nem "o modelo pediu a calculadora". O modelo pode pedir a mesma ferramenta outra vez, confuso. Isso é chamado de esquecer o pedido na literatura. A transcrição fica incoerente.

A correção é anexar a resposta **imediatamente** depois de chamar o modelo, antes de fazer qualquer outra coisa:

```text
function run_agent_correct(model, tools, transcript, max_turns):
    for turn_count in range(max_turns):
        response = call_model(model, transcript)
        transcript.append(response)  # Append right away

        if response.has_no_tool_calls():
            return response.text

        for tool_call in response.tool_calls:
            result = execute_tool(tools, tool_call)
            transcript.append(result)
```

Agora, quando o loop se repete e chama o modelo de novo, a transcrição inclui "o modelo disse que chamaria a busca", e o modelo pode raciocinar sobre o resultado.

### Condições de parada: escolhendo de propósito

Um loop de agente precisa parar. Há vários lugares para escolher:

**Máximo de turnos**: O loop externo conta os turnos e sai se a contagem passa de um limite. É uma proteção de segurança. Sem ela, um modelo ou uma ferramenta com defeito poderia rodar para sempre.

**Sem chamadas de ferramenta**: A resposta do modelo não contém chamadas de ferramenta. Esta é a parada do "caminho feliz": o modelo decidiu responder. Verifique isso depois de anexar a resposta do modelo.

**Ferramenta de parada explícita**: Você pode oferecer uma ferramenta chamada `stop` ou `finish` que o modelo pode chamar para sair explicitamente. O harness verifica isso e retorna. Isso é útil se a tarefa é aberta e o modelo precisa de uma ação explícita de "terminei". Se você oferece essa ferramenta, documente-a com clareza para que o modelo entenda quando usá-la.

**Proteção por contagem de erros**: Se uma chamada de ferramenta falha, o harness anexa o erro como resultado. Se chamadas de ferramenta demais falham em sequência, o harness para e devolve uma trajetória de erro em vez de continuar para sempre. Isso evita loops de retry.

Elas não são mutuamente exclusivas. Um harness de produção pode verificar todas:

```text
function run_agent_with_guards(model, tools, transcript, max_turns, max_errors):
    error_count = 0

    for turn_count in range(max_turns):
        response = call_model(model, transcript)
        transcript.append(response)

        if response.has_no_tool_calls():
            return response.text

        if response.has_explicit_stop_tool_call():
            return response.text

        for tool_call in response.tool_calls:
            result = execute_tool(tools, tool_call)

            if result.is_error():
                error_count += 1
                if error_count > max_errors:
                    return "Too many errors"
            else:
                error_count = 0

            transcript.append(result)

    return "Max turns reached"
```

O ponto é que essas decisões devem ser visíveis no seu código, e não escondidas ou acidentais. Você escolhe quando parar e escolhe quantas chances o agente tem de se recuperar.

## Prática

1. ▢ No loop em pseudocódigo mostrado acima, por que `transcript.append(response)` precisa acontecer antes da verificação `if response.has_no_tool_calls()`?

<details markdown="1"><summary>Verificação</summary>

A transcrição precisa incluir a resposta do modelo para que turnos posteriores (ou um observador lendo a trajetória) possam ver o que o modelo disse e decidiu. Se você verifica a parada antes de anexar, você devolve o texto do modelo, mas a transcrição nunca mostra que o modelo respondeu. Além disso, outras informações da resposta (como quais ferramentas o modelo considerou mas decidiu não chamar) se perderiam.

</details>

2. ▢ Um modelo chama uma ferramenta e o harness a executa com sucesso, devolvendo um resultado. O resultado é anexado à transcrição. Na iteração seguinte do loop, o harness chama o modelo de novo. O que o modelo vê na transcrição que não via no turno anterior?

<details markdown="1"><summary>Dica</summary>

Pense no que foi anexado na iteração anterior do loop, logo depois que o modelo foi chamado pela primeira vez.

</details>

<details markdown="1"><summary>Verificação</summary>

O modelo vê a sua própria resposta com a chamada de ferramenta, anexada antes de o loop executar a ferramenta. No segundo turno, a transcrição inclui tanto essa resposta quanto o resultado da ferramenta. Sem a resposta ser anexada primeiro, o modelo veria apenas o resultado, como se a ferramenta tivesse sido chamada por algo que não fosse o modelo.

</details>

3. ▢ Você está construindo um harness com uma proteção de máximo de erros: se três chamadas de ferramenta falham em sequência, pare o loop. O que você precisa para zerar o contador de erros?

    - a) Quando o máximo de turnos é atingido
    - b) Quando uma chamada de ferramenta tem sucesso e devolve um resultado que não é erro
    - c) Quando o loop começa
    - d) Quando a resposta do modelo não contém chamadas de ferramenta

<details markdown="1"><summary>Verificação</summary>

**b)** Quando uma chamada de ferramenta tem sucesso. A proteção existe para pegar um padrão de falhas repetidas. Se uma ferramenta falha e a seguinte tem sucesso, o loop de retry foi quebrado e você quer permitir mais falhas. Se você zerasse só no início (c), nunca poderia parar; se zerasse no máximo de turnos ou na ausência de chamadas de ferramenta (a, d), a proteção não funcionaria. Zerar no sucesso é o padrão: um sucesso zera o contador.

</details>

4. ▢ O seu modelo deve buscar, ler um documento e depois resumir. No terceiro turno, ele pede de novo a mesma ferramenta de busca. A busca teve sucesso na primeira vez. Qual é o bug mais provável no seu harness, dado o que você sabe sobre como as transcrições funcionam?

<details markdown="1"><summary>Verificação</summary>

O harness não está anexando à transcrição a resposta com a chamada de ferramenta do modelo depois que o modelo é chamado. O modelo nunca vê o seu próprio pedido da ferramenta de busca do primeiro turno. Quando é chamado no terceiro turno, a transcrição mostra o resultado da busca, mas não o pedido, então o modelo não sabe por que o resultado está ali e pede a busca de novo. A correção é anexar a resposta imediatamente depois de chamar o modelo, antes de executar a ferramenta.

</details>

## Prática no mundo real

- [ ] Escreva de memória o pseudocódigo do loop básico de agente, sem olhar a lição. Compare com o pseudocódigo mostrado em "O loop do agente como código". Confira: você anexa a resposta antes de verificar a ausência de chamadas de ferramenta?

- [ ] Encontre uma implementação de agente em qualquer projeto de código aberto (uma biblioteca que você usa ou um repositório público). Leia o código do loop. Identifique onde a transcrição é montada e onde a condição de parada é verificada. Note se as condições de parada são explícitas (visíveis em um if) ou escondidas (em uma condição enterrada em uma chamada a outra função).

- [ ] Amanhã: Esboce as quatro condições de parada (máximo de turnos, sem chamadas de ferramenta, parada explícita, proteção por contagem de erros) em pseudocódigo. Para cada uma, escreva uma frase sobre por que ela importa: que problema ela resolve?

## Para ir além

- [Article: "Building Effective Agents", Anthropic Engineering](https://www.anthropic.com/engineering/building-effective-agents)
- [Recursos](../RESOURCES.md)

---

Não ficou claro? Releia a fonte principal no topo, já que esta lição a comprime e é na compressão que o entendimento escapa. Consulte o [glossário](../GLOSSARY.md) para qualquer termo que pareceu escorregadio.

Se o problema é a lição em si, e não o material, isso é um defeito: [abra uma issue](https://github.com/TokenCemetery/teach/issues).
