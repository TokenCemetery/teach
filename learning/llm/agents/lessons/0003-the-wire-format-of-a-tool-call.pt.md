---
title: "3. O formato na rede de uma chamada de ferramenta"
description: "Como uma chamada de ferramenta e seu resultado realmente aparecem no protocolo entre o seu harness e o provedor do modelo"
type: lesson
---

# Lição 3. O formato na rede de uma chamada de ferramenta

**Ligação com a missão:** Escrever o loop de agente para uma tarefa dada e nomear o que cada mensagem do contexto está fazendo e o que encerra o loop.
**Fonte principal:** [Docs: "Tool use with Claude", Claude Platform Docs](https://platform.claude.com/docs/en/agents-and-tools/tool-use/overview)
**Pré-requisitos:** [Lição 2](0002-agent-workflow-or-prompt.md), [Ferramenta](../GLOSSARY.md)

## Aquecimento

1. ▢ Qual é a diferença entre um harness chamar um modelo e um harness executar uma ferramenta?

<details markdown="1"><summary>Verificação</summary>

O harness chama o modelo enviando-lhe uma requisição (a transcrição mais as ferramentas) pela rede à API de um provedor; o modelo roda dentro da infraestrutura do provedor e devolve uma saída estruturada. Uma ferramenta é chamada quando o modelo a pede emitindo um bloco estruturado de chamada de ferramenta; o harness a executa, em geral invocando uma função na mesma base de código ou na mesma rede.

</details>

2. ▢ Em que caso o modelo poderia enviar texto simples em vez de uma chamada de ferramenta?

<details markdown="1"><summary>Verificação</summary>

Quando o modelo terminou a tarefa em que estava trabalhando e está pronto para devolver uma resposta final ao usuário, ou quando decide (dentro dos limites que você definiu) que não precisa chamar uma ferramenta neste turno.

</details>

## Saiba isto

### A chamada de ferramenta na rede

Quando você envia a um provedor de modelos uma requisição pedindo que ele use ferramentas, a requisição inclui três coisas: o nome do modelo, a lista de ferramentas disponíveis (com seus nomes, descrições e schemas de parâmetros) e a transcrição da conversa até ali.

A definição de uma ferramenta tem este aspecto: um nome, uma descrição legível por pessoas e um JSON Schema que restringe os parâmetros que o modelo pode enviar. Aqui está uma requisição da Anthropic com uma única ferramenta:

```json
{
  "model": "claude-sonnet-5",
  "max_tokens": 1024,
  "tools": [
    {
      "name": "get_weather",
      "description": "Get the current weather for a given city",
      "input_schema": {
        "type": "object",
        "properties": {
          "city": {"type": "string", "description": "The city name"}
        },
        "required": ["city"]
      }
    }
  ],
  "messages": [
    {"role": "user", "content": "What's the weather in Lisbon?"}
  ]
}
```

Quando o modelo decide chamar uma ferramenta, ele não a executa. Em vez disso, devolve um bloco estruturado que descreve qual ferramenta chamar e quais argumentos passar. O provedor para de enviar saída e sinaliza isso com um campo `stop_reason`. Aqui está a resposta completa da Anthropic:

```json
{
  "id": "msg_01ABC",
  "type": "message",
  "role": "assistant",
  "content": [
    {"type": "text", "text": "I'll check that for you."},
    {
      "type": "tool_use",
      "id": "toolu_01XYZ",
      "name": "get_weather",
      "input": {"city": "Lisbon"}
    }
  ],
  "stop_reason": "tool_use"
}
```

Repare: o campo `input` já é JSON interpretado, e não uma string. Cada chamada de ferramenta recebe um id único (aqui `toolu_01XYZ`) para que o harness possa dizer ao modelo qual resultado responde a qual chamada. O assistente também pode incluir texto simples antes ou depois do bloco da chamada de ferramenta.

### Da rede à execução

O seu harness vê essa resposta e sabe que precisa executar `get_weather` com o argumento `{"city": "Lisbon"}`. Como fazer isso depende da sua ferramenta:

- Se é uma **ferramenta de cliente** (uma função no seu próprio código), você a chama diretamente: `weather_result = get_weather(city="Lisbon")`.
- Se é uma **ferramenta de servidor** (algo que o provedor executa para você, como uma busca na web hospedada), o provedor já a executou antes de devolver a resposta. Você extrai o resultado da resposta.

### Enviando o resultado de volta

Quando o harness tem um resultado (seja por executar a função ou por ler a resposta do provedor), ele o envia de volta ao modelo em uma nova mensagem, marcada com o id da chamada de ferramenta. O formato da Anthropic o aninha dentro de uma mensagem com papel `user`:

```json
{
  "role": "user",
  "content": [
    {
      "type": "tool_result",
      "tool_use_id": "toolu_01XYZ",
      "content": "18C, partly cloudy"
    }
  ]
}
```

Essa mensagem entra na transcrição como um novo turno. O modelo agora tem tanto a chamada de ferramenta que fez quanto o resultado, e decide o que fazer em seguida: chamar outra ferramenta, chamar a mesma ferramenta com argumentos diferentes ou devolver uma resposta final.

### O formato na rede da OpenAI (a diferença)

A API da OpenAI usa os mesmos conceitos, mas com nomes e formatos de campo diferentes. Em vez de repetir a troca inteira, eis o que difere:

Os parâmetros da ferramenta ficam aninhados em `function.parameters` em vez de um `input_schema` solto. Os argumentos da chamada de ferramenta do modelo chegam como uma string codificada em JSON em `function.arguments`, e não como um objeto já interpretado, então o seu harness precisa interpretá-la. O sinal de parada é `finish_reason: "tool_calls"` em vez de `stop_reason: "tool_use"`. O resultado volta como uma mensagem dedicada `role: "tool"` que carrega o `tool_call_id`, e não embrulhado em uma mensagem `user`. Aqui está um exemplo abreviado com a mesma tarefa do clima:

```json
{
  "choices": [{
    "message": {
      "role": "assistant",
      "content": null,
      "tool_calls": [{
        "id": "call_abc123",
        "type": "function",
        "function": {"name": "get_weather", "arguments": "{\"city\": \"Lisbon\"}"}
      }]
    },
    "finish_reason": "tool_calls"
  }]
}
```

Seguido do resultado como uma mensagem `role: "tool"`:

```json
{"role": "tool", "tool_call_id": "call_abc123", "content": "18C, partly cloudy"}
```

O padrão é idêntico: definição da ferramenta, chamada de ferramenta com id, resultado marcado com o mesmo id. Os nomes e formatos diferem, mas qualquer harness que lide com um pode ser adaptado ao outro mapeando esses campos.

## Prática

1. ▢ Na resposta da Anthropic mostrada acima, por que o campo `input` contém um objeto JSON interpretado em vez de uma string JSON?

<details markdown="1"><summary>Verificação</summary>

A API da Anthropic interpreta os argumentos da chamada de ferramenta no lado do provedor antes de devolvê-los, reduzindo o trabalho do harness. O seu código recebe valores prontos para uso, e não uma string para interpretar. A OpenAI envia os argumentos como string, então você precisa chamar `json.parse()` ou equivalente no seu harness antes de usá-los.

</details>

2. ▢ Quando você envia o resultado da ferramenta de volta ao modelo, por que ele inclui o campo `tool_use_id`?

<details markdown="1"><summary>Verificação</summary>

O modelo pode ter pedido várias ferramentas em um único turno. O id permite ao modelo associar cada resultado à chamada correspondente que ele fez, para saber qual resposta veio de qual requisição.

</details>

3. ▢ No protocolo da Anthropic, o resultado de uma ferramenta viaja dentro de uma mensagem com papel `user`. No da OpenAI, viaja como uma mensagem `role: "tool"`. Por que essa diferença não importa para a lógica do loop do agente?

    - a) Porque o harness não precisa distingui-las ao montar a transcrição
    - b) Porque o modelo sempre as processa do mesmo jeito, qualquer que seja o papel
    - c) Porque um dos protocolos está claramente errado e deve ser evitado
    - d) Porque resultados de ferramenta não fazem parte da transcrição oficial

<details markdown="1"><summary>Verificação</summary>

**b)** O modelo as processa do mesmo jeito, qualquer que seja o rótulo de papel ou a estrutura da mensagem. A lógica é: aqui está um resultado de uma chamada de ferramenta que você fez; o que você quer fazer agora? O detalhe do protocolo (dentro de uma mensagem de usuário ou como uma mensagem de ferramenta) não muda essa lógica. (a) chega perto, mas perde o ponto: o papel não importa para o loop em si.

</details>

4. ▢ Um harness recebe esta resposta da OpenAI: `"arguments": "{\"city\": \"Paris\"}"`. Como o harness precisa processar isso antes de passar para a ferramenta?

<details markdown="1"><summary>Verificação</summary>

Interpretando como JSON: `json.loads("{\"city\": \"Paris\"}") yields {"city": "Paris"}`. A OpenAI devolve uma string, e o harness precisa desserializá-la em um dicionário (ou objeto) antes de desempacotar os argumentos na chamada da função.

</details>

## Prática no mundo real

- [ ] Abra o código ou a documentação de um framework de agentes real (LangChain, Vercel AI ou o próprio SDK Python da Claude) e encontre onde ele envia uma definição de ferramenta ao modelo. Identifique o nome, a descrição e o schema de parâmetros. Marque de onde cada um vem no código.
- [ ] Percorra um ciclo completo de chamada de ferramenta nessa mesma base de código: encontre onde ele interpreta a resposta de uso de ferramenta do modelo, executa a ferramenta e envia o resultado de volta. Marque como o id é usado para associá-los.
- [ ] Amanhã: escreva um harness mínimo (20 linhas ou menos, pseudocódigo serve) que envia uma única ferramenta a um provedor de modelos, interpreta a resposta da chamada de ferramenta e envia o resultado de volta. Não use um framework.

## Para ir além

- [Docs: "Tool use with Claude", Claude Platform Docs](https://platform.claude.com/docs/en/agents-and-tools/tool-use/overview)
- [Guide: "Function calling", OpenAI](https://developers.openai.com/api/docs/guides/function-calling)
- [Recursos](../RESOURCES.md)

---

Não ficou claro? Releia a fonte principal no topo, já que esta lição a comprime e é na compressão que o entendimento escapa. Consulte o [glossário](../GLOSSARY.md) para qualquer termo que pareceu escorregadio.

Se o problema é a lição em si, e não o material, isso é um defeito: [abra uma issue](https://github.com/TokenCemetery/teach/issues).
