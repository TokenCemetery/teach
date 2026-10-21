---
title: "8. Nomeando e descrevendo uma ferramenta"
description: "O nome e a descrição de uma ferramenta são o que o modelo lê para decidir quando e como chamá-la"
type: lesson
---

# Lição 8. Nomeando e descrevendo uma ferramenta

**Ligação com a missão:** Projetar a superfície de ferramentas de um agente (nomes, descrições, formatos de retorno e a fronteira de permissão que decide o que ele pode fazer sem supervisão) começa por entender que nomes e descrições não são documentação de API para uma pessoa: são superfície de prompt que o modelo lê para decidir quando e como chamar uma ferramenta.
**Fonte principal:** [Article: "Writing Effective Tools for Agents", Anthropic Engineering](https://www.anthropic.com/engineering/writing-tools-for-agents)
**Pré-requisitos:** [Lição 7](0007-the-transcript-as-state.md), [Ferramenta](../GLOSSARY.md)

## Aquecimento

1. ▢ Da Lição 7: Como o modelo "lembra" o que aconteceu em um turno anterior do loop do agente?

<details markdown="1"><summary>Verificação</summary>

Ele não lembra por conta própria. O harness reenvia a transcrição inteira a cada chamada, então o que parece memória é na verdade o modelo relendo tudo o que lhe foi mostrado antes.

</details>

2. ▢ Da Lição 7: Por que a transcrição é todo o estado do agente, e não alguma outra estrutura de dados que o harness guarda separadamente?

<details markdown="1"><summary>Verificação</summary>

Porque o modelo só vê a transcrição. Qualquer fato que o harness conhece mas nunca anexa a ela é invisível ao modelo, não importa o que mais o harness acompanhe internamente.

</details>

## Saiba isto

### Uma descrição de ferramenta não é documentação de API

Um erro que todo construtor comete uma vez: escrever a descrição de uma ferramenta como você escreveria a docstring de um endpoint REST.

```text
Bad:
name: fetch_user
description: Fetches user data
```

Isso é terso demais para um modelo que decide entre várias ferramentas. O modelo não tem contexto sobre quando usar `fetch_user` em vez de `get_user` ou `lookup_user`. Não sabe que dados voltam nem o que entra. Não consegue raciocinar sobre chamá-la agora ou depois. Quando o modelo vê três ferramentas e nenhuma orientação clara, ele chuta, e chuta errado com mais frequência do que uma pessoa chutaria.

Aqui está a mesma ferramenta descrita para um modelo:

```text
Better:
name: fetch_user
description: Look up a user profile by their numeric ID. Returns the user's name, email, account status, and the current version number of their profile. Use this before calling update_user, since update_user requires you to pass the profile's current version number to prevent write conflicts. Returns null if the user ID does not exist.
```

Agora o modelo enxerga o quadro completo: quando chamá-la (antes de update_user), do que ela precisa (um ID numérico) e o que devolve (informação suficiente para decidir o próximo passo). Essa descrição serve à tomada de decisão do modelo, e não a uma pessoa lendo documentação de API.

A diferença é esta: uma docstring REST diz a um programador como usar uma ferramenta. A descrição de uma ferramenta no prompt de um agente diz a um modelo quando e por que chamá-la, o que passar e que resultado esperar. O modelo não tem um manual; a sua descrição é o único guia dele.

### Nomear de forma distinta das outras ferramentas

O modelo escolhe entre ferramentas lendo seus nomes e descrições, sem nenhum outro sinal. Se duas ferramentas soam parecidas, o modelo vai chamar a errada ou chamar as duas por segurança.

```text
Bad:
- name: list_files
  description: Lists files in a directory
- name: list_file_contents
  description: Lists the contents of a file
```

O modelo pode confundir essas duas ou chamar ambas quando só precisa de uma. Os nomes estão próximos demais.

```text
Better:
- name: list_directory
  description: List all files and subdirectories in a directory. Shows names and file sizes. Does not show file contents.
- name: read_file
  description: Read the complete contents of a single file. Returns text as a string.
```

Agora os nomes são distintos (list_directory contra read_file) e as descrições deixam claro o que cada uma faz e não faz. O modelo escolherá a certa.

A regra: o nome de uma ferramenta deve dizer o que ela faz de um jeito que não possa ser confundido com nenhuma outra ferramenta do mesmo conjunto. Se você tem várias ferramentas de busca, não chame todas de `search`. Chame-as de `search_documentation`, `search_code`, `search_logs`.

### Descrições de parâmetros importam da mesma forma

A descrição de nível superior da ferramenta recebe mais atenção, mas as descrições dos parâmetros são igualmente importantes para a correção.

```text
Bad:
name: create_issue
description: Creates a GitHub issue
parameters:
  - name: title
    type: string
    description: Issue title
  - name: body
    type: string
    description: Issue body
```

O modelo não sabe em que formato o título deve estar, quão longo pode ser, se deve ser uma pergunta ou uma afirmação. O corpo é ainda pior: é Markdown? Texto simples? Quão detalhado? O modelo descreve o problema ou a solução?

```text
Better:
name: create_issue
description: Create a new issue in the repository
parameters:
  - name: title
    type: string
    description: A one-line summary of the problem or feature request. Be specific and actionable. Examples: "Handle null config values in startup" or "Add support for JSON output format".
  - name: body
    type: string
    description: Detailed description in Markdown. Include what you tried, what failed, and what you expect to happen. If it is a feature request, explain why it matters. If it is a bug, include steps to reproduce.
```

Agora o modelo sabe que tipo de título escrever e que nível de detalhe incluir no corpo. Ele produzirá resultados melhores.

### Uma falha comum: ferramentas parecidas confundindo o modelo

O pior caso é quando duas ferramentas são parecidas o bastante para que o modelo não consiga distingui-las, mesmo com descrições.

```text
Very bad:
- name: update_user
  description: Update user information
- name: change_user
  description: Modify user data
```

Esses nomes e descrições dizem quase a mesma coisa. O modelo pode chamar ambas, ou chamar a errada, ou perder tempo perguntando. Você não lhe deu como escolher.

A correção é tornar os nomes e as descrições tão diferentes que só um faça sentido para a tarefa em questão:

```text
Better:
- name: update_user_profile
  description: Change a user's displayed name, email, or profile picture. Requires the profile version number to prevent conflicts.
- name: update_user_permissions
  description: Grant or revoke access roles for a user, such as admin, editor, or viewer. Only callable by the current account's admin.
```

Agora o modelo vê que a primeira ferramenta é para informações pessoais e a segunda é para controle de acesso. Ele escolherá a certa.

## Prática

1. ▢ Você tem duas ferramentas: `send_email` e `send_notification`. O modelo às vezes chama as duas quando só precisa de uma. Escreva uma frase para cada ferramenta que deixe claro ao modelo qual usar e quando.

<details markdown="1"><summary>Verificação</summary>

Respostas possíveis: `send_email` poderia ser "Send an email message to an email address. Use this for messages longer than a few lines or when you need to include attachments or formatted text." `send_notification` poderia ser "Send a brief in-app notification to a user. Use this for short status updates or alerts that do not require the user to leave the application." O ponto-chave é que a descrição diz ao modelo que tipo de mensagem cada ferramenta espera, para que ele escolha corretamente.

</details>

2. ▢ A sua ferramenta `get_user` devolve todos os campos de um registro de usuário: id, nome, e-mail, telefone, endereço, empresa, biografia, preferências, nível de assinatura e mais dez. A descrição de um parâmetro deve orientar o modelo sobre o que passar. O que você NÃO deve colocar na descrição?

<details markdown="1"><summary>Dica</summary>

Pense no que o modelo precisa saber para chamar a ferramenta corretamente, em contraste com o que é bom saber mas não é necessário para a chamada em si.

</details>

<details markdown="1"><summary>Verificação</summary>

Você NÃO deve listar todos os campos que a ferramenta devolve. A descrição da ferramenta diz o que o modelo recebe de volta; a descrição do parâmetro diz o que o modelo precisa fornecer para chamá-la. Para um parâmetro `user_id`, a descrição deve dizer algo como "The numeric ID of the user. If you do not have the ID, call search_users first." Não liste na descrição do parâmetro quais campos voltam; isso vai na descrição de nível superior da ferramenta.

</details>

3. ▢ Qual é a melhor razão para escrever descrições detalhadas dos parâmetros de uma ferramenta?

    - a) Para cumprir padrões de documentação de API
    - b) Para ajudar engenheiros que leiam o código depois
    - c) Para ajudar o modelo a decidir que valor passar e quando chamar a ferramenta, afinal
    - d) Para reduzir o número de chamadas de ferramenta que o usuário precisa fazer

<details markdown="1"><summary>Verificação</summary>

**c)** Para ajudar o modelo a decidir que valor passar e quando chamar a ferramenta, afinal. O modelo lê as descrições dos parâmetros para entender que argumentos uma ferramenta espera e o que acontece se passar o valor errado. (a) é irrelevante; isto é prompt engineering, não design de API. (b) pode ser um benefício colateral, mas não é a razão principal. (d) perde o ponto: descrições detalhadas ajudam o modelo a fazer menos chamadas erradas, não menos chamadas no total.

</details>

4. ▢ Você está construindo uma ferramenta chamada `search`. Você também tem ferramentas chamadas `search_documents`, `search_issues` e `search_users`. Por que esse nome de ferramenta é um problema, e o que você deveria fazer em vez disso?

<details markdown="1"><summary>Verificação</summary>

A ferramenta `search` é genérica demais. O modelo não saberá qual ferramenta de busca chamar quando precisar buscar. Pode chamar todas, ou escolher ao acaso. Em vez disso, renomeie `search` para algo específico como `search_logs`, `search_comments` ou `search_code`. A regra é: cada nome de ferramenta deve ser específico o bastante para que o modelo saiba o que ela faz, e diferente o bastante dos outros nomes de ferramenta para que o modelo não a confunda.

</details>

## Prática no mundo real

- [ ] Encontre as definições de ferramenta (nome e descrição) de uma aplicação com LLM ou de um framework de agentes que você usa. Leia a descrição de cada ferramenta. Anote uma ferramenta cuja descrição seja clara o bastante para você entender quando o modelo deve chamá-la e uma ferramenta cuja descrição seja vaga demais. Note por que a primeira funciona e o que falta na segunda.

- [ ] Escolha uma ferramenta que você usa com regularidade na linha de comando (como `grep` ou `find`). Imagine que você precisasse descrevê-la para um modelo que não sabe nada sobre o seu sistema de arquivos. Escreva uma descrição de uma frase que diga ao modelo o que a ferramenta faz e quando usá-la em vez de uma ferramenta parecida.

- [ ] Amanhã: Pegue a descrição de uma ferramenta de um agente real ou de uma documentação de API que você considera mal escrita. Reescreva-a para um modelo que está escolhendo entre várias ferramentas parecidas. Faça-a pelo menos duas vezes mais longa, inclua um exemplo de quando usá-la e diga uma coisa para a qual ela NÃO serve.

## Para ir além

- [Article: "Writing Effective Tools for Agents", Anthropic Engineering](https://www.anthropic.com/engineering/writing-tools-for-agents)
- [Recursos](../RESOURCES.md)

---

Não ficou claro? Releia a fonte principal no topo, já que esta lição a comprime e é na compressão que o entendimento escapa. Consulte o [glossário](../GLOSSARY.md) para qualquer termo que pareceu escorregadio.

Se o problema é a lição em si, e não o material, isso é um defeito: [abra uma issue](https://github.com/TokenCemetery/teach/issues).
