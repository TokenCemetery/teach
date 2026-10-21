---
title: "9. Formatos de retorno e inchaço do conjunto de ferramentas"
description: "O valor de retorno de uma ferramenta custa orçamento de contexto, e ferramentas demais prejudicam a capacidade do modelo de escolher corretamente"
type: lesson
---

# Lição 9. Formatos de retorno e inchaço do conjunto de ferramentas

**Ligação com a missão:** Projetar a superfície de ferramentas de um agente inclui escolher o que uma ferramenta devolve (seu formato de retorno) e decidir quantas ferramentas oferecer, porque ambas são escolhas de design que afetam a capacidade do modelo de decidir corretamente entre suas opções e o custo de cada turno que vem depois.
**Fonte principal:** [Article: "Writing Effective Tools for Agents", Anthropic Engineering](https://www.anthropic.com/engineering/writing-tools-for-agents)
**Pré-requisitos:** [Lição 8](0008-naming-and-describing-a-tool.md)

## Aquecimento

1. ▢ Da Lição 8: Por que a descrição de uma ferramenta deve dizer ao modelo quando e como usá-la, em vez de apenas listar os parâmetros que ela aceita?

<details markdown="1"><summary>Verificação</summary>

Porque o modelo não tem outra fonte de orientação para escolher entre ferramentas. Uma lista simples de parâmetros explica como chamar uma ferramenta, mas não por que nem quando recorrer a ela, que é a decisão de fato que o modelo precisa tomar.

</details>

2. ▢ Da Lição 8: Que problema você cria se tem, no mesmo conjunto de ferramentas, duas ferramentas com nomes e descrições muito parecidos?

<details markdown="1"><summary>Verificação</summary>

O modelo não consegue distingui-las de forma confiável, então pode chamar a errada ou chamar as duas por segurança. O ruído também degrada a capacidade do modelo de escolher corretamente entre todas as outras ferramentas do conjunto, e não só entre as duas parecidas.

</details>

## Saiba isto

### O valor de retorno de uma ferramenta custa orçamento de contexto

Toda mensagem na transcrição consome tokens. Quando uma ferramenta devolve um resultado, ele é anexado à transcrição, e o modelo o vê em todos os turnos seguintes até a execução terminar ou a transcrição ser truncada. Uma ferramenta que devolve uma resposta pequena e focada custa pouco. Uma ferramenta que devolve cinco mil linhas de banco de dados custa tokens de verdade em cada turno pelo resto da execução, quer o modelo tenha precisado de todas ou não.

```text
Bad:
Tool: fetch_user_records
Returns: [complete User record, complete User record, ...]
# 5000 rows, 50KB of JSON, ~10,000 tokens consumed per turn after this call
```

Depois que a ferramenta devolve, a transcrição incha. O modelo agora precisa processar as cinco mil linhas no turno seguinte só para ler o próprio contexto. Isso incha o orçamento de tokens e deixa o loop mais lento.

### Projete formatos de retorno para a tomada de decisão, não para a completude

Em vez de devolver tudo o que o sistema subjacente tem, projete um formato de retorno que dê ao modelo o que ele precisa para decidir o próximo passo.

```text
Better: Option 1 - Return a summary
Tool: fetch_user_records
Returns:
  total_count: 5000
  sample_results: [User, User, User, ...] # top 5 results
  query_was_too_broad: true
  suggestion: "Your query matches 5000 users. Narrow it with a company_id or email domain filter."

# ~500 tokens consumed per turn after this call
```

O modelo agora vê que a consulta foi ampla demais e sabe o que fazer em seguida: pode chamar a ferramenta de novo com filtros melhores. Isso devolve um décimo dos tokens do despejo completo.

```text
Better: Option 2 - Let the model ask for more
Tool: fetch_user_records
Returns:
  count: 50  # number of results returned
  total_matching: 5000  # number of results if the query was not limited
  results: [User, User, ...] # just the first 50
  next_page_token: "abc123xyz"

# Model sees it got 50 of 5000. It can decide to refine the query or ask for the next page.
```

Nos dois casos, o modelo recebe informação suficiente para tomar uma decisão informada sem ser soterrado por dados.

### Inchaço do conjunto de ferramentas: mais ferramentas significam escolhas piores

Acrescentar uma ferramenta a um agente não é de graça. Cada ferramenta entre as quais o modelo pode escolher torna a escolha mais difícil para ele. Isso se chama inchaço do conjunto de ferramentas.

Com três ferramentas, o modelo escolhe corretamente na maior parte das vezes:

```text
Tools:
- search_documentation
- read_file
- list_directory
```

Com dez ferramentas, o modelo começa a duvidar de si mesmo, chamando várias ferramentas quando uma bastaria:

```text
Tools:
- search_documentation
- search_issues
- search_code
- read_file
- read_logs
- list_directory
- list_repos
- get_git_history
- get_git_diff
- get_git_status
```

Cada nova ferramenta acrescenta ruído à decisão. O modelo precisa ler e considerar as dez descrições antes de escolher uma. Se duas são parecidas (search_code e search_documentation), o modelo pode chamar ambas. O efeito é silencioso: toda ferramenta existente sofre um pouco, e não só a nova.

O custo é real: mais chamadas de ferramenta, mais tokens na transcrição, mais turnos desperdiçados com informação redundante.

### Adicionar uma ferramenta nova contra adicionar um parâmetro

Quando você for tentado a adicionar uma ferramenta, primeiro pergunte: isso poderia ser um parâmetro de uma ferramenta existente?

```text
Bad: Two tools
- name: list_files
- name: list_directories
```

Melhor: Uma ferramenta com um parâmetro

```text
Good: One tool with a parameter
- name: list_contents
  parameters:
    - name: path
    - name: type
      type: enum
      values: [files, directories, all]
```

O modelo escolhe o tipo que quer, e você não acrescentou ruído ao conjunto de ferramentas.

Mas às vezes uma ferramenta nova faz sentido. Se as ferramentas são fundamentalmente diferentes (são chamadas em situações diferentes, devolvem formatos diferentes, exigem permissões diferentes), então uma ferramenta nova com um nome claro é melhor do que um parâmetro sobrecarregado:

```text
Good: Two specialized tools
- name: search_database_by_id
  parameters:
    - id
    # Fast, returns a single record
- name: search_database_by_query
  parameters:
    - query
    # Might return many records
```

O modelo conhece a diferença: by_id é rápida e precisa, by_query é flexível, mas pode devolver muito. Os nomes deixam a decisão clara.

A regra: adicione uma ferramenta nova quando ela seria chamada por razões fundamentalmente diferentes, ou quando você não consegue expressar a distinção em parâmetros. Adicione um parâmetro quando a ferramenta é basicamente a mesma operação com uma variação no formato de entrada ou de saída.

### Observando o inchaço do conjunto de ferramentas na prática

Um sinal sutil é quando o modelo começa a dizer coisas como "devo chamar search primeiro para ver se existe, depois fetch se existir" quando uma ferramenta poderia ter feito todo o trabalho. Isso é o modelo tentando ser seguro porque não tem confiança sobre o que cada ferramenta faz. O problema não é o modelo; é o conjunto de ferramentas.

Outro sinal são chamadas de ferramenta repetidas: o modelo chama a mesma ferramenta várias vezes em uma única execução, como buscar duas vezes ou listar duas vezes. Isso muitas vezes significa que o conjunto de ferramentas não dá ao modelo um jeito de restringir os resultados em uma chamada, então ele precisa chamar a ferramenta com parâmetros diferentes para encontrar o que precisa.

## Prática

1. ▢ Uma ferramenta chamada `get_user_history` devolve um array JSON de 100.000 eventos de ação do usuário do último mês, cada um detalhado. O modelo provavelmente vai chamar essa ferramenta, olhar os dez primeiros eventos e ignorar o resto. Que mudança de design reduz o custo em tokens em cada turno depois dessa chamada?

<details markdown="1"><summary>Verificação</summary>

Limite o retorno aos primeiros N eventos (por exemplo, os primeiros 20) e inclua um total_count e um jeito de o modelo pedir mais. Assim o modelo vê o que precisa sem pagar pelos 100.000 eventos. Alternativamente, devolva um resumo: "50 events in the past week, 50 in the week before. Most recent: user logged in" em vez do detalhe completo, e deixe o modelo pedir os detalhes se precisar.

</details>

2. ▢ Você tem um conjunto de ferramentas com 15 ferramentas. O modelo está chamando search_by_name e search_by_id na mesma execução, mesmo podendo expressar as duas buscas como parâmetros de uma única ferramenta. Qual é o dano de tê-las mantido como duas ferramentas separadas?

<details markdown="1"><summary>Dica</summary>

Pense no trabalho do modelo: ele precisa ler quinze descrições e decidir qual ferramenta chamar. Como ter ferramentas parecidas torna esse trabalho mais difícil?

</details>

<details markdown="1"><summary>Verificação</summary>

Inchaço do conjunto de ferramentas. O modelo precisa escolher entre quinze ferramentas. Ferramentas parecidas como search_by_name e search_by_id tornam a escolha mais difícil. O modelo pode chamar as duas quando uma bastaria, ou perder tempo decidindo qual é a apropriada. Toda ferramenta existente sofre um pouquinho porque o conjunto ficou mais ruidoso. A correção é fundi-las em uma única ferramenta de busca com um parâmetro para o campo da busca.

</details>

3. ▢ Qual destes é um sinal de que o formato de retorno de uma ferramenta é verboso demais?

    - a) A ferramenta é chamada com muita frequência
    - b) O modelo lê o resultado e pede um resumo antes de usá-lo
    - c) A ferramenta demora muito para executar
    - d) A ferramenta exige autenticação

<details markdown="1"><summary>Verificação</summary>

**b)** O modelo lê o resultado e pede um resumo antes de usá-lo. Isso significa que a ferramenta está devolvendo informação demais; o modelo precisa filtrar ou resumir o que recebeu antes de poder tomar uma decisão. (a) não tem relação com o formato de retorno; uma ferramenta muito chamada pode ser estreita por design. (c) é sobre velocidade de execução, não sobre tokens. (d) é sobre permissões, não sobre o formato de retorno.

</details>

4. ▢ Você está projetando ferramentas para um agente de busca em código. `search_code` e `get_code_diff` devem ser uma ferramenta ou duas? Explique em uma ou duas frases.

<details markdown="1"><summary>Verificação</summary>

Duas ferramentas separadas. São chamadas por razões diferentes (a busca procura arquivos que casam com um padrão, o diff mostra mudanças entre versões), devolvem formatos diferentes (uma lista de arquivos contra um diff estruturado) e resolvem problemas diferentes. Uma única ferramenta sobrecarregada tornaria a escolha do modelo mais difícil. Se fossem variações da mesma operação (como search_code com parâmetros de consulta diferentes), poderiam ser uma ferramenta com um parâmetro.

</details>

## Prática no mundo real

- [ ] Encontre um conjunto de ferramentas em uma aplicação com LLM ou agente a que você tem acesso. Conte as ferramentas. Leia a trajetória do modelo e marque todo turno em que o modelo chamou uma ferramenta. Estime: o modelo alguma vez chamou duas ferramentas parecidas quando uma teria resolvido? Escreva uma frase sobre se o conjunto de ferramentas pareceu inchado ou bem projetado.

- [ ] Escolha uma ferramenta que devolve dados estruturados. Leia um exemplo de valor de retorno. Há alguma parte do retorno que o modelo provavelmente ignoraria? Reescreva o formato de retorno para excluir esses dados ou movê-los para uma segunda chamada, estimando quantos tokens você economizou.

- [ ] Amanhã: Projete uma ferramenta que poderia ir para qualquer lado (uma ferramenta nova ou um parâmetro de uma existente). Para a sua escolha, escreva duas frases sobre por que você escolheu uma ferramenta separada ou um parâmetro, o que a alternativa custaria e quando você poderia reconsiderar.

## Para ir além

- [Article: "Writing Effective Tools for Agents", Anthropic Engineering](https://www.anthropic.com/engineering/writing-tools-for-agents)
- [Recursos](../RESOURCES.md)

---

Não ficou claro? Releia a fonte principal no topo, já que esta lição a comprime e é na compressão que o entendimento escapa. Consulte o [glossário](../GLOSSARY.md) para qualquer termo que pareceu escorregadio.

Se o problema é a lição em si, e não o material, isso é um defeito: [abra uma issue](https://github.com/TokenCemetery/teach/issues).
