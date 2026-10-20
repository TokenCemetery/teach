---
title: Glossário
description: "Termos canônicos de prompting"
type: glossary
---

# Glossário de Prompting

Termos canônicos para escrever, estruturar, versionar, medir e proteger os prompts por trás de um recurso baseado em LLM.

## Termos

**Chain-of-thought**:
Raciocínio intermediário que o modelo escreve antes da resposta final, provocado por exemplos que o mostram ou por uma instrução que o pede.
_Evite_: CoT em texto corrido (tudo bem em um título ou tabela), thinking (reservado aqui para a fase de raciocínio embutida de um modelo de raciocínio)

**Chat template**:
A regra específica de cada modelo que transforma uma lista de mensagens marcadas por papel na única sequência de tokens com a qual o modelo foi treinado, incluindo os tokens especiais que marcam onde cada papel começa e termina.
_Evite_: formato de prompt

**Decodificação restrita**:
Limitar quais tokens o modelo pode gerar a cada passo, de modo que a saída precise obedecer a uma gramática ou a um schema, como faz o recurso de saída estruturada imposto por um provedor.
_Evite_: grammar sampling

**Delimitador**:
Marcação em um prompt, como uma tag em estilo XML ou um bloco cercado, que indica onde um tipo de conteúdo termina e outro começa, na maioria das vezes para manter os dados separados das instruções.
_Evite_: separador

**Prompt few-shot**:
Um prompt que inclui, antes da entrada real, exemplos resolvidos da tarefa, cada um com uma entrada pareada com a saída desejada.
_Evite_: prompt multishot, treinamento em contexto

**Injeção de prompt indireta**:
Injeção de prompt transportada por conteúdo que o modelo lê em nome do usuário, como uma página web, um e-mail ou um documento recuperado, e não digitada por quem conversa com ele.
_Evite_: injeção de segunda ordem

**Hierarquia de instruções**:
A ordem de prioridade que o modelo é treinado para aplicar quando instruções entram em conflito: system prompt acima do turno do usuário, e turno do usuário acima do conteúdo devolvido por ferramentas ou por recuperação.
_Evite_: ordem de prioridade

**Jailbreak**:
Entrada construída para fazer o modelo produzir aquilo que seu treinamento de segurança recusa. Ele ataca os limites do próprio modelo, enquanto a injeção de prompt ataca as instruções da aplicação.
_Evite_: injeção de prompt (alvo diferente)

**Tríade letal**:
A combinação de acesso a dados privados, exposição a conteúdo não confiável e um meio de enviar dados para fora, que juntos tornam a injeção de prompt explorável. Remover qualquer um dos três fecha o caminho.
_Evite_: risco de injeção (vago demais para agir)

**Snapshot do modelo**:
Uma versão fixa de um modelo, identificada por um ID de modelo exato, cujos pesos o provedor não altera. Um alias de conveniência pode apontar, com o tempo, para um snapshot mais novo.
_Evite_: versão do modelo (ambíguo com a geração do modelo)

**Comparação pareada**:
Comparar dois prompts ou modelos sobre as mesmas entradas pelos casos em que seus resultados diferem, e não pelos dois totais.
_Evite_: comparação de pontuação A/B

**Prompt**:
Tudo o que o modelo recebe em uma chamada: o system prompt, cada mensagem da conversa até aquele ponto e qualquer conteúdo inserido, renderizados pelo chat template em uma única sequência de tokens.
_Evite_: query (essa é a pergunta do usuário dentro do prompt)

**Prompt caching**:
Recurso de provedor que guarda o estado processado de um prefixo de prompt, para que chamadas posteriores com exatamente esse prefixo evitem recalculá-lo, reduzindo custo e latência.
_Evite_: cache de respostas (outra coisa: guardar respostas inteiras)

**Injeção de prompt**:
Entrada que faz o modelo seguir instruções diferentes das que o autor do prompt pretendia.
_Evite_: jailbreak (o jailbreak ataca o treinamento de segurança do modelo; a injeção ataca as instruções da aplicação)

**Template de prompt**:
O texto fixo de um prompt com campos nomeados que são preenchidos com valores de cada requisição, como a mensagem do usuário ou um documento recuperado, no momento da chamada.
_Evite_: string de prompt

**Modelo de raciocínio**:
Um modelo treinado para produzir uma fase interna de raciocínio antes da resposta visível, de modo que raciocina sem que lhe peçam.
_Evite_: thinking model

**Conjunto de regressão**:
Um conjunto fixo de entradas, cada uma com uma verificação sobre a saída, que uma mudança de prompt não pode quebrar, construído principalmente a partir de falhas vistas em uso real.
_Evite_: prompts de teste, golden set

**Papel**:
O rótulo de cada mensagem em uma conversa, geralmente system, user ou assistant, que o chat template transforma em tokens especiais. Um papel é formatação à qual o modelo aprendeu a dar peso, não um canal de entrada separado.
_Evite_: persona (essa é a descrição de quem o modelo deve interpretar)

**Autoconsistência**:
Amostrar várias completions de chain-of-thought para o mesmo prompt e ficar com a resposta final mais comum.
_Evite_: ensembling

**Saída estruturada**:
Uma resposta em formato legível por máquina, geralmente JSON que segue um schema, que um programa interpreta em vez de uma pessoa ler.
_Evite_: JSON mode (um recurso específico de um provedor)

**System prompt**:
A mensagem, no papel system, que define a tarefa, as restrições e o contexto do modelo para toda a conversa, e fica no topo da hierarquia de instruções.
_Evite_: mensagem de sistema, preâmbulo

**Prompt zero-shot**:
Um prompt que descreve a tarefa sem nenhum exemplo resolvido.
_Evite_: prompt simples
