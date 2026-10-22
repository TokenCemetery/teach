---
title: "17. Prompt caching e layout"
description: "Ordene um prompt com as partes estáveis primeiro, para que o provedor possa fazer cache do prefixo"
type: lesson
---

# Lição 17. Prompt caching e layout

**Ligação com a missão:** Um template de prompt que coloca o seu texto estável primeiro permite que o provedor pule o reprocessamento a cada chamada, então o layout é uma decisão de custo e latência tomada no template, e não um detalhe de última hora.
**Fonte principal:** [Docs: "Prompt caching", Claude Platform Docs](https://platform.claude.com/docs/en/build-with-claude/prompt-caching)
**Pré-requisitos:** [Lição 16](0016-versioning-prompts.md), [Prompt caching](../GLOSSARY.md)

## Aquecimento

1. ▢ A lição 13 disse onde vão um documento longo e a pergunta em um prompt. Qual vem primeiro, e essa ordem concorda com colocar o conteúdo estável primeiro para o caching?

<details markdown="1"><summary>Verificação</summary>

Os documentos longos vêm primeiro e a pergunta por último. Concorda: um documento reutilizado entre requisições é estável, e a pergunta muda a cada vez, então os dois objetivos apontam para o mesmo lado.

</details>

2. ▢ O template da lição 15 tem texto fixo e campos. Qual dos dois é candidato ao prefixo em cache, e qual nunca pode ser?

<details markdown="1"><summary>Verificação</summary>

O texto fixo é candidato, pois é idêntico em toda chamada. Os valores dos campos por requisição mudam, então nada que contenha um deles pode fazer parte de um prefixo reutilizado.

</details>

## Saiba isto

### O prefixo é o que entra no cache

O **prompt caching** guarda o estado processado de um prefixo de prompt para que uma chamada posterior que compartilhe exatamente esse prefixo pule o recálculo. A documentação da Anthropic descreve a sua versão: o prefixo em cache cobre a requisição inteira em uma ordem fixa, `tools`, depois `system`, depois `messages`, até o bloco marcado com `cache_control`, inclusive. O hash por trás de uma entrada de cache é cumulativo, então mudar qualquer bloco no marcado ou antes dele produz um hash diferente na próxima requisição, e a entrada não corresponde.

Outros provedores implementam o caching de formas diferentes, então confira as regras deles. O princípio aqui, um prefixo exato reutilizado, é a parte a levar consigo.

### O layout decorre disso

Coloque o que nunca muda primeiro e o que muda por requisição por último: definições de ferramentas, depois o system prompt, depois documentos longos e exemplos few-shot, depois a pergunta por requisição. A documentação diz para colocar o conteúdo estático no início e marcar o fim da parte reutilizável.

```python
def build_request(system: str, documents: str, question: str) -> dict:
    return {
        "system": system,
        "messages": [
            {
                "role": "user",
                "content": [
                    # stable: the end of this block is where a cache marker goes
                    {"type": "text", "text": documents},
                    # per request: after the marker, never part of the prefix
                    {"type": "text", "text": question},
                ],
            },
        ],
    }
```

Aqui `documents` é compartilhado entre as chamadas e `question` não é, então o texto compartilhado vem na frente, e eles são blocos separados para que o marcador possa ficar depois dos documentos e antes da pergunta. Na API da Anthropic, esse marcador é um campo `cache_control` no bloco dos documentos, a outra parte deste esboço específica de um fornecedor. O exemplo de erro da própria documentação é um bloco que contém um timestamp e a mensagem do usuário, com o marcador de cache nele: o hash do prefixo inclui o timestamp, então toda requisição grava uma nova entrada e nunca lê uma. Mantenha um timestamp, um ID de requisição ou um nome de usuário fora da parte estável. A correção da Anthropic é colocar o marcador no último bloco que é idêntico entre as requisições.

### O que quebra um hit, e os limites

- Um prefixo menor que o mínimo do modelo não entra no cache, e nenhum erro é retornado. O mínimo documentado depende do modelo e vai de 512 a 4.096 tokens. Se `cache_creation_input_tokens` e `cache_read_input_tokens` no usage da resposta forem ambos 0, o prompt não foi cacheado.
- Mudar as definições de ferramentas invalida o cache inteiro. A tabela de invalidação da documentação também lista mudanças na configuração de tool-choice, em imagens e em algumas configurações de thinking e effort, que invalidam a parte das mensagens.
- A duração padrão é de 5 minutos, renovada a cada leitura da entrada. Existe uma opção de 1 hora, com custo adicional.
- Uma entrada de cache só fica disponível depois que a primeira resposta começa, então primeiras requisições paralelas não a compartilham. Para cargas concorrentes e de agentes, veja a [lição 34 da trilha de agentes](../../agents/lessons/0034-prompt-caching-and-concurrency.md).

As leituras são mais baratas que a entrada sem cache e as gravações custam mais: a documentação lista gravações de 5 minutos a 1,25 vez o preço base de entrada e leituras a 0,1 vez, com exceções por modelo nas leituras. Assim, um layout que nunca acerta custa um pouco mais do que não usar caching.

## Prática

1. ▢ Um template começa com `Current time: {now}`, depois um guia de estilo de 3.000 tokens, depois a pergunta do usuário. Por que o caching nunca ajuda aqui, e qual é a correção?

<details markdown="1"><summary>Verificação</summary>

O timestamp é o primeiro bloco, então o hash do prefixo muda a cada requisição e nenhum bloco seguinte pode ser lido do cache. Mova o guia de estilo e qualquer outro texto fixo para antes do timestamp, ou tire o timestamp do prompt se a tarefa não precisa dele, e mantenha a pergunta por último.

</details>

2. ▢ Primeira requisição: `cache_read_input_tokens` é 0, `cache_creation_input_tokens` é 2.400, `input_tokens` é 60. Segunda requisição, mesmo prefixo, uma pergunta de 75 tokens: o que os três campos mostram se o caching funcionou, e qual é a entrada total?

<details markdown="1"><summary>Dica</summary>

A documentação diz que `input_tokens` conta apenas o que vem depois do último breakpoint de cache.

</details>

<details markdown="1"><summary>Verificação</summary>

`cache_read_input_tokens` é 2.400, `cache_creation_input_tokens` é 0 e `input_tokens` é 75. A entrada total é a soma, 2.475 tokens. O prefixo foi lido do cache em vez de gravado de novo, e só a pergunta nova foi processada do zero.

</details>

3. ▢ Uma equipe adiciona um system prompt de 600 tokens em um modelo cujo mínimo é 1.024 tokens, marca-o para cache e vê os dois contadores de usage em 0. O que aconteceu, e algo está quebrado?

<details markdown="1"><summary>Verificação</summary>

O prompt está abaixo do mínimo, então foi processado sem caching e nenhum erro foi retornado. Nada está quebrado. Adicione mais conteúdo estável, como exemplos, para atingir o mínimo, ou aceite chamadas sem cache.

</details>

4. ▢ Qual layout de prompt é o melhor para fazer cache de um bot de suporte que responde a muitas perguntas sobre um único documento de políticas longo?

    - a) Pergunta, depois o documento de políticas, depois o system prompt
    - b) System prompt, depois a pergunta, depois o documento de políticas
    - c) System prompt, depois o documento de políticas, depois a pergunta
    - d) System prompt, depois o nome do usuário, depois o documento de políticas

<details markdown="1"><summary>Verificação</summary>

**c)** O system prompt e o documento são idênticos entre as requisições e vêm na frente, e a pergunta vem por último. (a) e (b) colocam a pergunta, que muda, antes do texto estável, então o prefixo difere a cada chamada. (d) coloca um valor por usuário antes do documento, o que quebra o prefixo compartilhado para cada usuário diferente.

</details>

## Prática no mundo real

- [ ] Pegue um prompt que você executa e marque cada parte como estável, muda diariamente ou muda por requisição, depois confira se as partes estáveis estão primeiro.
- [ ] Faça uma chamada duas vezes com o mesmo prefixo em um provedor que reporte o uso de cache e leia os contadores das duas chamadas.
- [ ] Amanhã: encontre qualquer timestamp, ID ou nome dentro da região estável de um prompt e mova-o para o fim.

## Para ir além

- [Docs: "Prompt caching", Claude Platform Docs](https://platform.claude.com/docs/en/build-with-claude/prompt-caching)
- [lição 34 da trilha de agentes](../../agents/lessons/0034-prompt-caching-and-concurrency.md)
- [Prompts em Produção](../reference/prompts-in-production.md)
- [Recursos](../RESOURCES.md)

---

Não está entrando? Releia a fonte principal no topo, pois esta lição a comprime e é na compressão que a compreensão vaza. Consulte o [glossário](../GLOSSARY.md) para qualquer termo que pareceu escorregadio.

Se o problema é a própria lição, e não o material, isso é um defeito: [abra uma issue](https://github.com/TokenCemetery/teach/issues).
