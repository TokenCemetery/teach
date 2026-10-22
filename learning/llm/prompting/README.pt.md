---
title: Prompting
description: "Escreva, versione e publique prompts para um recurso baseado em LLM, prove que uma mudança de prompt ajudou e revise o prompt de produção de outra pessoa"
type: topic
---

# Aprendizado: Prompting

Escreva os prompts por trás de um recurso baseado em LLM para que façam o que foi pretendido, vivam no código como templates versionados e mudem somente quando um conjunto de regressão disser que a mudança ajudou. Termine capaz de revisar o prompt de produção de outra pessoa e dizer o que cada escolha nele custa, em vez de dizer que ele parece estranho.

**Última lição:** [24. Quando o conselho de sempre está errado](lessons/0024-when-the-usual-advice-is-wrong.md)

## O sucesso se parece com isto

- Escrever um prompt cujos papéis, instruções e estrutura um colega consiga ler e o modelo siga, e dizer o que o modelo de fato recebe a partir dele.
- Escolher, ordenar e auditar exemplos few-shot, nomeando o viés que cada escolha arrisca.
- Decidir quando pedir raciocínio, fazer prompting de um modelo de raciocínio de forma diferente de um modelo padrão e explicar por que o raciocínio escrito não é uma explicação da resposta.
- Obter saída estruturada que um programa consiga interpretar e organizar um contexto longo para que o modelo use o que há nele.
- Manter prompts em um codebase como templates versionados, ordenados para que o prefixo estável possa ser colocado em cache.
- Mostrar, com um conjunto de regressão e uma comparação pareada, se uma mudança de prompt ajudou, em vez de julgá-la por um punhado de saídas.
- Projetar um prompt que lide com entrada não confiável e dizer de quais riscos o prompt sozinho não consegue se defender.
- Escolher entre um prompt melhor, recuperação e fine-tuning para uma determinada falha e revisar o prompt de produção de outra pessoa nomeando o que cada escolha custa.

## Restrições

- Primeiro o app, utilizável a partir de uma janela de chat: as etapas 1 a 6 funcionam em qualquer interface de chat, as etapas 7 a 10 pressupõem que o prompt vive no código.
- Sem provedor ou modelo fixo. Os exemplos são neutros quanto ao provedor; quando uma técnica é comportamento documentado de um único fornecedor, a lição diz isso.
- Nenhum conhecimento prévio de prompting é pressuposto. Saber o que é um LLM, no nível de "ele prevê o próximo token", é suficiente.

## Fora do escopo

- Construção de prompt sobre contexto recuperado e o orçamento da janela de contexto: veja [`llm/rag`](../../llm/rag/) e sua folha [Geração a partir da recuperação](../../llm/rag/reference/generation-from-retrieval.md). Esta trilha ensina prompting em geral e aponta para lá no caso de recuperação.
- Descrições de ferramentas como superfície de prompt, injeção de prompt em um agente com ferramentas e prompt caching sob concorrência: veja [`llm/agents`](../../llm/agents/). Esta trilha cobre prompting sem ferramentas e aponta para essas lições em vez de repeti-las.
- Design de prompts de juiz e metodologia de avaliação: veja [`llm/evals`](../../llm/evals/) e sua folha [Go/No-Go](../../llm/evals/reference/go-no-go.md). Esta trilha usa uma avaliação para medir uma mudança de prompt e não ensina como construir uma.
- Decodificação restrita, o lado de serving da saída estruturada: veja [`llm/inference`](../../llm/inference/). Esta trilha pede estrutura pelo lado do prompt.
- Como seguir instruções e raciocinar são treinados em um modelo: veja [`llm/post-training`](../../llm/post-training/). Esta trilha cobre como usá-los de fora.

## O arco

Dez etapas, do que um prompt é para o modelo até o julgamento para revisar o de outra pessoa. Uma etapa leva várias lições e as fronteiras são flexíveis; o que torna uma etapa concluída é a capacidade, não a contagem de lições.

| Etapa | Lições | Cobre | Concluída quando |
|---|---|---|---|
| 1. O que um prompt é para o modelo | 0001 a 0002 | Tokens, chat templates, papéis, o system prompt e a hierarquia de instruções | Consegue dizer qual sequência o modelo recebe para uma dada conversa e onde cada instrução pertence |
| 2. Instruções e estrutura | 0003 a 0005 | Instruções claras, delimitadores e tags, sensibilidade à formatação | Consegue escrever um prompt que um iniciante poderia seguir e que mantém as instruções separadas dos dados |
| 3. Exemplos few-shot | 0006 a 0007 | O que as demonstrações ensinam, rótulo majoritário, vieses de recência e de ordem | Consegue escolher e ordenar exemplos e nomear o viés que cada escolha arrisca |
| 4. Raciocínio | 0008 a 0010 | Chain-of-thought, autoconsistência, fidelidade, prompting de modelos de raciocínio | Consegue decidir se deve pedir raciocínio e como, para um dado modelo e tarefa |
| 5. Saída estruturada | 0011 a 0012 | Pedir um schema, validá-lo, restrições de formato contra qualidade de raciocínio | Obtém saída que um programa interpreta, sem pagar por isso em qualidade da resposta |
| 6. Contexto longo | 0013 a 0014 | Efeitos de posição, layout de documentos, extração de citações | Consegue organizar um contexto longo para que o modelo use o que está no meio dele |
| 7. Prompts em um codebase | 0015 a 0017 | Templates, versionamento contra um snapshot do modelo, layout para prompt caching | Mantém prompts como templates versionados cujo prefixo estável pode ser colocado em cache |
| 8. Medir uma mudança de prompt | 0018 a 0019 | Conjuntos de regressão a partir de falhas reais, comparação pareada contra ruído | Consegue mostrar com um número se o prompt B supera o prompt A |
| 9. Segurança de prompts | 0020 a 0021 | Injeção de prompt direta e indireta, o que o prompt pode e não pode defender | Consegue projetar um prompt para entrada não confiável e nomear os riscos que ele deixa para o sistema |
| 10. Julgamento | 0022 a 0024 | Prompt contra RAG contra fine-tune, revisar um prompt de produção, mudar um prompt do qual outros dependem, quando o conselho usual está errado | Tem a confiança para tomar a decisão sobre um prompt e explicá-la a outra pessoa |

## Lições

Siga estas na ordem.

| # | Lição | Ensina |
|---|---|---|
| [0001](lessons/0001-what-the-model-sees.md) | O que o modelo vê | Um prompt chega ao modelo como uma única sequência de tokens construída por um chat template, então papéis são formatação com a qual o modelo foi treinado, não canais separados |
| [0002](lessons/0002-system-prompts-and-roles.md) | System prompts e papéis | O que pertence ao system prompt e o que pertence ao turno do usuário, e por que o modelo hierarquiza instruções pelo lugar onde elas ficam |
| [0003](lessons/0003-clear-instructions.md) | Instruções claras | Escreva uma instrução que um iniciante capaz conseguiria seguir: contexto, a tarefa, as restrições e como é a tarefa concluída |
| [0004](lessons/0004-structure-and-delimiters.md) | Estrutura e delimitadores | Separe instruções de dados com tags e seções para que o modelo consiga distinguir qual é qual |
| [0005](lessons/0005-format-sensitivity.md) | Sensibilidade ao formato | Por que uma mudança de formatação sem significado pode mover a acurácia, e por que isso faz de cada edição de prompt uma afirmação a ser testada |
| [0006](lessons/0006-what-examples-teach.md) | O que os exemplos few-shot ensinam | As demonstrações ensinam principalmente o formato, o espaço de rótulos e a distribuição das entradas, o que muda como você as escolhe |
| [0007](lessons/0007-few-shot-biases.md) | Vieses do few-shot | Vieses de rótulo majoritário, de recência e de ordem em prompts few-shot, e como escolher e ordenar exemplos contra eles |
| [0008](lessons/0008-chain-of-thought.md) | Chain-of-thought | Quando pedir raciocínio intermediário melhora uma resposta, e quando só acrescenta tokens |
| [0009](lessons/0009-self-consistency-and-faithfulness.md) | Autoconsistência e fidelidade | Amostrar vários caminhos de raciocínio para votar em uma resposta, e por que o raciocínio escrito não é uma explicação fiel |
| [0010](lessons/0010-prompting-reasoning-models.md) | Prompting de modelos de raciocínio | Por que um modelo que já pensa precisa de objetivos e restrições em vez de passos roteirizados |
| [0011](lessons/0011-structured-output-from-the-prompt.md) | Saída estruturada a partir do prompt | Peça uma saída que um programa consiga interpretar e depois valide, porque pedir não é uma garantia |
| [0012](lessons/0012-format-constraints-and-reasoning.md) | Restrições de formato e raciocínio | Um formato de saída rígido pode custar qualidade de raciocínio, e como ordenar os campos para que a resposta venha depois do pensamento |
| [0013](lessons/0013-position-in-long-context.md) | Posição em contexto longo | Os modelos usam melhor a informação nas bordas de um contexto longo do que no meio, o que decide onde vão os documentos e a pergunta |
| [0014](lessons/0014-working-with-long-documents.md) | Trabalhando com documentos longos | Marque os documentos com seus metadados e faça o modelo extrair citações antes de responder |
| [0015](lessons/0015-prompt-templates.md) | Templates de prompt | Divida um prompt em um template fixo e as variáveis preenchidas a cada requisição, e impeça que entrada não confiável quebre a estrutura |
| [0016](lessons/0016-versioning-prompts.md) | Versionando prompts | Trate um prompt como código: fixado a um snapshot do modelo, versionado, revisado e revertido como qualquer outra mudança |
| [0017](lessons/0017-prompt-caching-and-layout.md) | Prompt caching e layout | Ordene um prompt com as partes estáveis primeiro para que o provedor possa colocar o prefixo em cache |
| [0018](lessons/0018-a-regression-set-for-a-prompt.md) | Um conjunto de regressão para um prompt | Construa o pequeno conjunto de casos que uma mudança de prompt não pode quebrar, começando por falhas reais |
| [0019](lessons/0019-comparing-two-prompts.md) | Comparando dois prompts | Decida se o prompt B supera o prompt A com uma comparação pareada que separa a mudança do ruído entre execuções |
| [0020](lessons/0020-prompt-injection.md) | Injeção de prompt | Como o texto na entrada pode sobrepor as instruções do autor, diretamente ou escondido em conteúdo que o modelo lê |
| [0021](lessons/0021-what-a-prompt-cannot-defend.md) | O que um prompt não consegue defender | Quais defesas pertencem ao prompt, e por que as reais ficam no que o sistema permite que o modelo faça |
| [0022](lessons/0022-prompt-rag-or-fine-tune.md) | Prompt, RAG ou fine-tuning | Escolha entre um prompt melhor, recuperação e fine-tuning pelo que a falha realmente é |
| [0023](lessons/0023-reviewing-a-production-prompt.md) | Revisando um prompt de produção | Revise o prompt de outra pessoa nomeando o que cada escolha custa, e mude um prompt do qual outros dependem sem quebrá-los |
| [0024](lessons/0024-when-the-usual-advice-is-wrong.md) | Quando o conselho de sempre está errado | Reconheça quando o conselho padrão de prompting falha para um dado modelo ou tarefa, e resolva a disputa pela fonte primária |

## Referência

- [Glossário](GLOSSARY.md): termos canônicos deste tópico
- [Recursos](RESOURCES.md): fontes confiáveis, cada uma anotada com o que cobre
- [Anatomia do Prompt](reference/prompt-anatomy.md): papéis, o que vai onde e o checklist de estrutura das etapas 1 e 2
- [Few-Shot e Raciocínio](reference/few-shot-and-reasoning.md): escolher e ordenar exemplos, e quando pedir raciocínio, das etapas 3 e 4
- [Saída Estruturada e Contexto Longo](reference/structured-output-and-long-context.md): obter saída interpretável e organizar entradas longas, das etapas 5 e 6
- [Prompts em Produção](reference/prompts-in-production.md): templates, versionamento, layout amigável ao cache e o ciclo de medição, das etapas 7 e 8
- [Segurança de Prompt](reference/prompt-security.md): rotas de injeção e qual defesa fica onde, da etapa 9
- [Checklist de Revisão de Prompt](reference/prompt-review-checklist.md): as perguntas a fazer sobre o prompt de outra pessoa, e prompt contra RAG contra fine-tune, da etapa 10

## Como isto funciona

Cada lição é curta e autocontida. Os gabaritos ficam recolhidos: primeiro lembre, depois abra. A prática no mundo real importa mais do que a leitura, e espaçá-la é o ponto. Tudo o que ainda estiver confuso no fim de uma lição vale ser perseguido até a fonte primária antes de seguir adiante.
