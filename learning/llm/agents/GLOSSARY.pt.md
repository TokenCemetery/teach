---
title: Glossário
description: "Termos canônicos de agentes de LLM"
type: glossary
---

# Glossário de Agentes de LLM

Termos canônicos para construir agentes: de que é feito o loop e como chamar cada parte, em uma área que costuma usar quatro palavras para a mesma coisa.

## Termos

**Memória entre execuções**:
Fatos guardados fora de qualquer trajetória individual e carregados de volta, de propósito, no contexto inicial de uma nova execução, já que uma execução nova começa com a transcrição vazia.
_Evite_: scratchpad (os dois são mecanismos separados e confundi-los é o erro mais comum aqui), estado (genérico demais)

**Agente**:
Um sistema que executa um modelo de linguagem em um loop com ferramentas, deixando que o modelo decida qual ferramenta chamar, quando chamá-la e quando parar, em vez de seguir um caminho que o desenvolvedor fixou de antemão.
_Evite_: assistente, bot, copilot (palavras de produto que não dizem nada sobre o fluxo de controle ser fixo ou decidido pelo modelo)

**Loop do agente**:
O ciclo que um agente em execução repete: enviar a transcrição ao modelo, executar a chamada de ferramenta que voltar, anexar o resultado à transcrição e repetir até que uma condição de parada dispare.
_Evite_: chain, pipeline (ambos nomeiam uma sequência fixa, que é exatamente o que um loop de agente não é)

**Portão de aprovação**:
Um ponto de verificação no nível do harness que pausa o loop antes de executar uma chamada de uma categoria arriscada, até que uma pessoa a aprove ou rejeite.
_Evite_: human-in-the-loop (amplo demais; portão de aprovação nomeia este mecanismo específico)

**Espectro de autonomia**:
A faixa que vai de um único prompt, passando por um workflow fixado pelo desenvolvedor, até um agente dirigido pelo modelo, ordenada por quanto do fluxo de controle o modelo escolhe em tempo de execução, em vez de o desenvolvedor escolher de antemão.
_Evite_: "quão agêntico" algo é (trata a autonomia como uma quantidade única e difusa, e não como uma pergunta sobre fluxo de controle com resposta verificável)

**Ferramenta de cliente**:
Uma ferramenta cuja implementação roda no código do próprio harness, de modo que o harness a executa diretamente quando o modelo a solicita.
_Evite_: ferramenta local, ferramenta customizada

**Compactação**:
Substituir um trecho antigo da transcrição por um resumo condensado sobre o qual o modelo ainda consegue agir, trocando alguma perda de informação por um contexto residente menor.
_Evite_: sumarização (genérico demais; compactação mira especificamente a transcrição do próprio agente, e não um texto qualquer)

**Confused deputy**:
Um componente com autoridade legítima que é induzido, por conteúdo não confiável, a usar mal essa autoridade em nome de um atacante, em vez de ser ele próprio comprometido.
_Evite_: "o modelo foi hackeado" (nada foi comprometido; a ferramenta fez exatamente o que foi construída para permitir)

**Envenenamento de contexto**:
Uma afirmação sem fundamento ou falsa que entra na transcrição e passa a ser tratada em silêncio como fato estabelecido por todos os turnos seguintes.
_Evite_: alucinação (ampla demais; este termo nomeia especificamente uma afirmação que entrou e persiste na transcrição, e não qualquer saída errada isolada)

**Context rot**:
A atenção e a acurácia do modelo se degradando conforme conteúdo de baixa relevância se acumula no contexto, mesmo quando nenhuma informação necessária foi truncada.
_Evite_: "o contexto está cheio" (mistura um limite rígido de tokens com um problema mais suave de acurácia, que começa bem antes do limite)

**Custo por tarefa concluída**:
O custo em tokens de toda tentativa, repetição e worker de que uma tarefa realmente precisou para ter sucesso, e não apenas o custo da última chamada bem-sucedida.
_Evite_: custo por chamada de API (subestima uma tarefa que precisou de mais de uma tentativa para dar certo)

**Fan-out**:
Um orquestrador disparando vários workers ao mesmo tempo sobre variações do mesmo problema, trocando custo em tokens por tempo real de relógio paralelo.
_Evite_: paralelismo (genérico demais; fan-out é a forma multiagente específica que o produz aqui)

**Grounding**:
Traduzir a intenção do modelo em uma coordenada de tela ou em um alvo visível de fato, um passo que pode falhar por conta própria mesmo quando a decisão subjacente do modelo estava correta.
_Evite_: acurácia de clique (estreito demais; grounding cobre qualquer mapeamento de observação para ação, não só o clique)

**Handoff**:
Um agente terminando sua parte de uma tarefa e passando um contexto limpo e delimitado, e não a trajetória completa, a um segundo agente especializado para a fase seguinte.
_Evite_: fan-out (handoff é sequencial, fan-out é paralelo; veja o contraste nesta lição)

**Harness**:
O código ao redor do modelo que guarda a transcrição, executa as chamadas de ferramenta, impõe limites e decide quando o loop termina. O modelo escolhe; o harness age.
_Evite_: runtime, framework (um framework é um harness possível, não o conceito)

**Privilégio mínimo**:
Restringir cada ferramenta ao acesso de que ela realmente precisa, em vez de um acesso amplo concedido "só por precaução".
_Evite_: sandboxing (um sandbox impõe uma fronteira; privilégio mínimo é o princípio de projeto que decide quão estreita essa fronteira deve ser)

**Tríade letal**:
A combinação de acesso a dados privados, exposição a conteúdo não confiável e capacidade de comunicar-se com o exterior que, juntos, tornam um agente explorável. Remover qualquer um dos três quebra o ataque.
_Evite_: "risco de segurança" (vago demais para agir; a tríade nomeia as três condições específicas a verificar)

**Orquestrador**:
O agente de um sistema multiagente que decompõe uma tarefa, atribui subtarefas a workers e sintetiza os relatórios deles; ele mesmo não faz o trabalho das subtarefas.
_Evite_: gerente, coordenador (termos genéricos que não distinguem este papel de um worker)

**Injeção de prompt**:
Conteúdo lido por um agente que contém instruções projetadas para sequestrar seu comportamento, explorando o fato de que o modelo não consegue distinguir estruturalmente dados de instruções.
_Evite_: jailbreak (um jailbreak mira diretamente o treinamento de recusa do próprio modelo; a injeção esconde instruções dentro de conteúdo que o agente foi encarregado de processar)

**ReAct**:
O padrão de intercalar um passo curto de raciocínio com cada ação, para que o raciocínio de cada passo possa reagir ao resultado real do passo anterior.
_Evite_: chain-of-thought (esse termo nomeia apenas o texto de raciocínio; ReAct o intercala especificamente com ações de ferramenta e seus resultados observados)

**Reflexão**:
Uma etapa explícita em que o agente avalia em linguagem natural uma tentativa que falhou e leva essa avaliação para a tentativa seguinte, diferente de uma simples repetição com o mesmo contexto.
_Evite_: autocorreção (usada de forma solta para qualquer coisa que um modelo faça internamente; reflexão nomeia a versão externa, armazenada e carregada adiante)

**Recuperação sob demanda**:
Manter residente no contexto apenas um resumo ou uma referência e trazer o detalhe completo de volta com uma chamada de ferramenta somente quando o modelo realmente precisar dele.
_Evite_: RAG (o RAG recupera de um corpus externo; esta técnica recupera detalhes que o agente já produziu ou aos quais tem acesso direto)

**Sandbox**:
A fronteira de execução que o harness impõe ao que o código de uma ferramenta pode alcançar (sistema de arquivos, rede, recursos), independentemente do que o modelo pediu.
_Evite_: permissão (uma permissão é o que você concede; um sandbox é o mecanismo que faz a concessão valer mesmo contra uma chamada malformada ou adversária)

**Scratchpad**:
Notas que um agente escreve e relê dentro de uma única execução. Na prática é só parte da transcrição, e some quando a execução termina.
_Evite_: memória (um scratchpad não sobrevive além da execução em que foi escrito)

**Ferramenta de servidor**:
Uma ferramenta que um provedor executa em sua própria infraestrutura em nome do harness, como uma busca na web hospedada ou a execução de código em sandbox. O harness nunca roda sua implementação, apenas lê o resultado na resposta do provedor.
_Evite_: ferramenta hospedada, ferramenta embutida

**Subagente**:
Uma execução de agente separada, com sua própria transcrição e seu próprio harness, iniciada para fazer um trabalho delimitado, cujo único efeito sobre o contexto do pai é o resumo que ela devolve.
_Evite_: worker fora de um sistema orquestrador-worker (worker nomeia um subagente que recebeu uma tarefa delimitada de um orquestrador; o mecanismo é o mesmo, o termo destaca o papel)

**Amplificação de tokens**:
Quanto mais uma tarefa custa em tokens como loop agêntico do que como um único prompt, vindo do recrescimento da transcrição, da duplicação multiagente e de repetições se acumulando.
_Evite_: "agentes são caros" (vago demais; amplificação nomeia o multiplicador específico e de onde vem cada parte dele)

**Ferramenta**:
Uma capacidade oferecida ao modelo como um nome, uma descrição e um schema de parâmetros, que o modelo pode pedir e que o harness executa em seu nome.
_Evite_: chamada de função (isso nomeia a mensagem que o modelo emite, não a capacidade), plugin, skill

**Trace**:
Um registro estruturado e com marcas de tempo de uma execução de agente, feito de spans, usando convenções neutras quanto a fornecedor, para que o trace de uma ferramenta seja legível em outra.
_Evite_: log (um log não estruturado é o que um trace substitui; um trace tem um schema definido que uma ferramenta consegue consultar)

**Trajetória**:
O registro completo e ordenado de uma execução de agente: cada turno do modelo, chamada de ferramenta, resultado de ferramenta e decisão de parada. É o que se lê ao diagnosticar uma falha, e não apenas a resposta final.
_Evite_: transcrição (a lista de mensagens que o modelo de fato vê, que omite as decisões do próprio harness), histórico, log

**Worker**:
Um subagente que recebe de um orquestrador uma subtarefa delimitada e roda seu próprio loop e sua própria transcrição, isolado dos demais workers.
_Evite_: subagente para o papel de orquestração (subagente nomeia o mecanismo; worker nomeia este papel específico dentro dele)

**Workflow**:
Um sistema em que o desenvolvedor fixou de antemão a sequência de chamadas ao modelo e de chamadas de ferramenta. Pode conter ramificações e loops, mas o modelo não escolhe o caminho.
_Evite_: agente (a distinção entre os dois é o ponto da etapa 1), chain
