---
title: "5. Chamadas paralelas e erros como resultados"
description: "Como um modelo pode pedir várias ferramentas de uma vez e por que erros de ferramenta são resultados, e não exceções"
type: lesson
---

# Lição 5. Chamadas paralelas e erros como resultados

**Ligação com a missão:** Escrever o loop de agente para uma tarefa dada e nomear o que cada mensagem do contexto está fazendo e o que encerra o loop.
**Fonte principal:** [Docs: "Tool use with Claude", Claude Platform Docs](https://platform.claude.com/docs/en/agents-and-tools/tool-use/overview)
**Pré-requisitos:** [Lição 4](0004-schemas-and-who-executes.md)

## Aquecimento

1. ▢ Em um único turno do modelo, ele pode pedir mais de uma chamada de ferramenta ao mesmo tempo?

<details markdown="1"><summary>Verificação</summary>

Sim. O modelo pode emitir vários blocos de uso de ferramenta em uma resposta, cada um com um id único. O harness executa todos eles (possivelmente em paralelo) e reúne os resultados antes de enviá-los de volta como a mensagem seguinte.

</details>

2. ▢ Quando uma ferramenta falha, o que o harness faz: lança uma exceção que derruba o loop ou devolve o erro ao modelo?

<details markdown="1"><summary>Verificação</summary>

Devolve o erro ao modelo como resultado de ferramenta. O loop continua; o modelo tem a chance de tentar de novo, usar outra ferramenta ou explicar a falha.

</details>

## Saiba isto

### Chamadas paralelas de ferramenta em um turno

O loop do agente é enviar, executar, anexar, repetir. Uma única resposta do modelo pode incluir várias chamadas de ferramenta:

```json
{
  "role": "assistant",
  "content": [
    {"type": "text", "text": "I'll gather that data for you."},
    {
      "type": "tool_use",
      "id": "toolu_01XYZ",
      "name": "get_weather",
      "input": {"city": "Lisbon"}
    },
    {
      "type": "tool_use",
      "id": "toolu_02ABC",
      "name": "get_weather",
      "input": {"city": "Madrid"}
    }
  ],
  "stop_reason": "tool_use"
}
```

Cada chamada tem seu próprio id único. O modelo decidiu: "Preciso do clima de Lisboa e de Madri." O seu harness agora pode:

1. Executar as duas ferramentas em sequência (uma depois da outra), ou
2. Executá-las em paralelo (as duas ao mesmo tempo), dependendo da sua implementação.

A escolha é sua. Se são independentes e rápidas, o paralelo economiza latência. Se competem por recursos ou uma depende da outra, o sequencial é mais simples.

### Reunindo os resultados antes do próximo turno

Quando todas as chamadas de ferramenta terminam, o harness coleta os resultados e os envia de volta em uma única mensagem. Cada resultado é marcado com o id da chamada que ele responde:

```json
{
  "role": "user",
  "content": [
    {
      "type": "tool_result",
      "tool_use_id": "toolu_01XYZ",
      "content": "18C, partly cloudy"
    },
    {
      "type": "tool_result",
      "tool_use_id": "toolu_02ABC",
      "content": "22C, sunny"
    }
  ]
}
```

O modelo agora tem os dois resultados, sabe qual é qual (pelo id) e decide o que fazer em seguida. Esta é a chave: todos os resultados voltam juntos em uma mensagem, então o modelo os processa como um par.

### Tratando erros como resultados

Quando uma ferramenta falha, o harness não derruba o loop. Em vez disso, captura o erro e o envia de volta ao modelo como um resultado, exatamente como um resultado bem-sucedido. O resultado de ferramenta de um erro tem este aspecto:

```json
{
  "type": "tool_result",
  "tool_use_id": "toolu_01XYZ",
  "content": "Error: city not found",
  "is_error": true
}
```

O campo `is_error` diz ao modelo que esse resultado representa uma falha, e não um sucesso. O modelo o lê e precisa decidir: tentar a mesma ferramenta com outra cidade, tentar uma ferramenta diferente ou desistir e explicar o erro ao usuário.

### Por que erros são resultados, e não exceções

Em muitos sistemas, uma chamada de função que falha levanta uma exceção e interrompe a execução. Em um loop de agente, uma chamada de ferramenta que falha é apenas informação: dados devolvidos ao modelo. Por que esse design?

Porque o modelo está no comando. O modelo chamou a ferramenta; ele deve decidir o que fazer se a ferramenta falhar. Talvez queira tentar de novo. Talvez queira usar outra ferramenta. Talvez queira pedir mais informações ao usuário. Uma exceção tiraria essa escolha dele.

Isso não é tolerar código ruim. É uma escolha de design: tratar o modelo como o orquestrador, e não como mais uma função em uma pilha de chamadas. O trabalho do harness é executar o que o modelo pede, coletar o resultado (sucesso ou falha) e devolvê-lo para o modelo interpretar.

### Erros vêm de muitos lugares

Uma chamada de ferramenta pode falhar por muitos motivos:

- O código da ferramenta de cliente levantou uma exceção (banco fora do ar, entrada inválida, timeout).
- Uma ferramenta de servidor executou, mas devolveu um erro (limite de taxa da API, arquivo não encontrado, permissão negada).
- O próprio harness rejeitou a chamada (a validação do schema falhou, campo obrigatório ausente).
- A rede falhou (provedor inalcançável, conexão interrompida).

Todos eles viram resultados de ferramenta carregando mensagens de erro, e não falhas.

## Prática

1. ▢ Um modelo faz duas chamadas de ferramenta em um turno: uma tem sucesso, uma falha. Como o harness envia os dois resultados de volta ao modelo?

<details markdown="1"><summary>Verificação</summary>

Em uma única mensagem de papel user com dois blocos tool_result, cada um marcado com o id da chamada correspondente. Um resultado tem `is_error: true` ou uma mensagem de erro; o outro carrega os dados de sucesso. O modelo recebe os dois em um turno e decide o que fazer em seguida.

</details>

2. ▢ Você tem uma ferramenta que pesquisa um banco de dados. O modelo a chama com uma busca que estoura o tempo. O que o seu harness deve fazer?

<details markdown="1"><summary>Dica</summary>

Pense em de quem é o trabalho de tratar o timeout e no que o modelo precisa saber.

</details>

<details markdown="1"><summary>Verificação</summary>

Capturar o timeout, guardar a mensagem de erro (por exemplo, "Error: search timed out after 30s") e enviá-la de volta ao modelo como resultado de ferramenta com `is_error: true`. O modelo então decide: tentar com uma consulta mais simples, tentar outra ferramenta ou desistir. O loop não falha.

</details>

3. ▢ O modelo faz três chamadas de ferramenta paralelas. O harness deve:

    - a) Executá-las uma após a outra para poder parar mais cedo se uma falhar
    - b) Executá-las em paralelo e esperar todos os resultados antes de enviá-los de volta
    - c) Devolver os resultados bem-sucedidos imediatamente e só enviar os que falharam depois
    - d) Cancelar as chamadas restantes assim que uma falhar

<details markdown="1"><summary>Verificação</summary>

**b)** Executá-las em paralelo e esperar todos os resultados. O modelo pediu três coisas; deve receber três resultados (sucesso ou falha). Parar mais cedo (a) ou cancelar (d) impede o modelo de saber o que aconteceu. Devolver resultados em momentos diferentes (c) quebra o protocolo: os resultados voltam juntos em uma mensagem.

</details>

4. ▢ Você escreve uma ferramenta de cliente que multiplica dois números. Um modelo a chama com `x=5, y="hello"`. O harness tenta executá-la, e a função levanta um erro de tipo. Qual é o próximo passo do harness?

<details markdown="1"><summary>Verificação</summary>

Capturar a exceção, formatar o erro (por exemplo, "Error: cannot multiply number by string") e enviá-lo de volta ao modelo como resultado de ferramenta. O modelo agora sabe que a chamada falhou e pode tentar de novo com entradas válidas ou tentar outra abordagem. O loop continua.

</details>

## Prática no mundo real

- [ ] Escreva ou encontre um agente que faça chamadas paralelas de ferramenta. Percorra uma execução em que o modelo pede duas ferramentas ao mesmo tempo. Verifique que os dois resultados voltam juntos em uma mensagem e carregam cada um o seu id.
- [ ] Faça uma ferramenta falhar de propósito (chame um banco que está fora do ar, dispare um erro de validação ou envie a uma ferramenta uma entrada inválida). Observe como o harness formata o erro e o envia ao modelo. Veja o que o modelo faz em seguida.
- [ ] Amanhã: escreva um harness que execute chamadas de ferramenta em paralelo (use threads, async ou o modelo de concorrência da sua linguagem) e colete os resultados. Verifique que ele envia todos os resultados de volta em uma mensagem mesmo que algumas ferramentas falhem.

## Para ir além

- [Docs: "Tool use with Claude", Claude Platform Docs](https://platform.claude.com/docs/en/agents-and-tools/tool-use/overview)
- [Recursos](../RESOURCES.md)

---

Não ficou claro? Releia a fonte principal no topo, já que esta lição a comprime e é na compressão que o entendimento escapa. Consulte o [glossário](../GLOSSARY.md) para qualquer termo que pareceu escorregadio.

Se o problema é a lição em si, e não o material, isso é um defeito: [abra uma issue](https://github.com/TokenCemetery/teach/issues).
