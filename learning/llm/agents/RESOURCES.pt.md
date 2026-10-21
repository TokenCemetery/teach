---
title: Recursos
description: "Fontes confiáveis sobre agentes de LLM"
type: resources
---

# Recursos de Agentes de LLM

## Conhecimento

- [Article: "Building Effective Agents", Anthropic Engineering](https://www.anthropic.com/engineering/building-effective-agents)
  Traça a distinção entre workflow e agente sobre a qual esta trilha é construída, depois nomeia os padrões componíveis mais comuns (prompt chaining, roteamento, paralelização, orquestrador e workers, avaliador e otimizador) e defende o mais simples que funcione. Use para: o vocabulário da etapa 1 e o argumento da etapa 16 para não construir um agente.
- [Guide: "A Practical Guide to Building Agents", OpenAI](https://cdn.openai.com/business-guides-and-resources/a-practical-guide-to-building-agents.pdf)
  O enquadramento de um segundo fornecedor para o mesmo material, cobrindo quando uma tarefa justifica um agente, categorias de ferramentas, orquestração com um agente contra vários e guardrails. Use para: verificar se uma afirmação da etapa 1 ou da etapa 8 é sobre agentes, e não sobre o produto de um único provedor.
- [Article: "Writing Effective Tools for Agents", Anthropic Engineering](https://www.anthropic.com/engineering/writing-tools-for-agents)
  Trata o nome, a descrição, o schema de parâmetros e o formato de retorno de uma ferramenta como superfície de prompt, e não como um contrato de API, incluindo como a saída de uma ferramenta consome o orçamento de contexto. Use para: a etapa 4 e para entender por que uma ferramenta desenhada como um endpoint REST dá uma ferramenta pior.
- [Article: "Effective Context Engineering for AI Agents", Anthropic Engineering](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents)
  Defende tratar a janela de contexto como um orçamento finito a ser curado, e cobre compactação, anotações em memória externa e subagentes como isolamento de contexto. Use para: as etapas 5 e 6.
- [Paper: "ReAct: Synergizing Reasoning and Acting in Language Models", Yao et al., 2022](https://arxiv.org/abs/2210.03629)
  Introduz o intercalar de traços de raciocínio com ações de ferramenta em um mesmo loop, em vez de planejar tudo de antemão ou agir sem raciocinar. Use para: a etapa 7 e o nome do padrão que a maioria dos loops de agente ainda implementa.
- [Paper: "Reflexion: Language Agents with Verbal Reinforcement Learning", Shinn et al., 2023](https://arxiv.org/abs/2303.11366)
  Introduz a autocrítica como uma etapa explícita do loop: o agente reflete em linguagem natural sobre uma tentativa que falhou e leva essa reflexão para a nova tentativa. Use para: o material de reflexão da etapa 7 e o que a autocrítica custa em tokens.
- [Paper: "Toolformer: Language Models Can Teach Themselves to Use Tools", Schick et al., 2023](https://arxiv.org/abs/2302.04761)
  Mostra o uso de ferramentas sendo aprendido pelo modelo em vez de induzido por prompt, que é a fronteira entre esta trilha e `llm/finetuning`. Use para: a explicação da etapa 2 de por que um modelo emite uma chamada de ferramenta, afinal.
- [Docs: "Tool use with Claude", Claude Platform Docs](https://platform.claude.com/docs/en/agents-and-tools/tool-use/overview)
  O relato de um provedor sobre o formato de uma chamada de ferramenta na rede: o schema JSON que a definição de uma ferramenta assume, como uma requisição de chamada de ferramenta e seu resultado são representados como mensagens e as chamadas paralelas de ferramentas. Use para: o par de requisição e resposta capturado na etapa 2, lido contra o guia da OpenAI abaixo como a diferença.
- [Guide: "Function calling", OpenAI](https://developers.openai.com/api/docs/guides/function-calling)
  O formato na rede de um segundo provedor para a mesma mecânica, incluindo a passagem de uma única chamada de função para uma convenção geral de chamada de ferramentas. Use para: a etapa 2, como o segundo provedor cujo formato aparece apenas como a diferença em relação ao primeiro.
- [Specification: Model Context Protocol](https://modelcontextprotocol.io/specification)
  A especificação normativa do MCP: ferramentas, recursos, prompts, sampling, os transportes e o ciclo de vida do servidor. Use para: a etapa 9 e para resolver qualquer afirmação sobre MCP pela fonte, e não pela documentação de um cliente.
- [Article: "Code Execution with MCP", Anthropic Engineering](https://www.anthropic.com/engineering/code-execution-with-mcp)
  Defende que apresentar ferramentas como código contra o qual o agente escreve, em vez de definições individuais de ferramentas carregadas no contexto, muda o que um grande conjunto de ferramentas custa. Use para: o problema de descoberta de ferramentas em escala da etapa 9 e o material de execução de código da etapa 10.
- [Article: "How We Built Our Multi-Agent Research System", Anthropic Engineering](https://www.anthropic.com/engineering/multi-agent-research-system)
  Um relato de produção de um sistema de orquestrador e workers, incluindo o múltiplo de custo em tokens em relação a um único agente e onde a coordenação de fato quebrou. Use para: o argumento da etapa 8 de que multiagente compra paralelismo e isolamento de contexto, a um preço medido.
- [Article: "Don't Build Multi-Agents", Cognition](https://cognition.ai/blog/dont-build-multi-agents)
  O caso oposto, argumentando que dividir o trabalho entre agentes fragmenta o contexto e produz decisões que entram em conflito. Use para: a etapa 8, lido contra o relato da Anthropic acima e não no lugar dele.
- [Article: "The Lethal Trifecta for AI Agents", Simon Willison](https://simonwillison.net/2025/Jun/16/the-lethal-trifecta/)
  Nomeia a combinação que torna um agente explorável: acesso a dados privados, exposição a conteúdo não confiável e capacidade de comunicar-se com o exterior. Use para: o enquadramento central da etapa 14 e para entender por que instruções no prompt não são uma defesa.
- [Reference: "OWASP Top 10 for LLM Applications", OWASP GenAI Security Project](https://genai.owasp.org/llm-top-10/)
  O catálogo de consenso dos riscos de aplicações com LLM, incluindo injeção de prompt, agência excessiva e exposição na cadeia de suprimentos, cada um com mitigações. Use para: o checklist da etapa 14 e o vocabulário que um revisor de segurança já estará usando.
- [Specification: "Semantic Conventions for Generative AI", OpenTelemetry](https://opentelemetry.io/docs/specs/semconv/gen-ai/)
  Convenções neutras quanto a fornecedor para os spans e atributos que uma execução de agente emite, o que faz a visão de trajetória de um backend de tracing ser legível em outro. Use para: a etapa 12, como a resposta neutra quanto a provedor para o que um trace deve conter.
- [Paper: "tau-bench: A Benchmark for Tool-Agent-User Interaction in Real-World Domains", Yao et al., 2024](https://arxiv.org/abs/2406.12045)
  Avalia agentes em uso de ferramentas em vários turnos contra um usuário simulado e uma política de domínio, e introduz uma medida de confiabilidade com tentativas repetidas em vez do sucesso em uma única tentativa. Use para: a distinção da etapa 13 entre ter sucesso uma vez e ter sucesso de forma confiável.
- [Paper: "SWE-bench: Can Language Models Resolve Real-World GitHub Issues?", Jimenez et al., 2023](https://arxiv.org/abs/2310.06770)
  Avalia agentes em issues reais de repositórios, com os próprios testes do projeto como verificação do resultado. Use para: o exemplo da etapa 13 de um benchmark avaliado pelo resultado em que a trajetória não tem restrições.
- [Docs: "Computer use tool", Claude Platform Docs](https://platform.claude.com/docs/en/agents-and-tools/tool-use/computer-use-tool)
  Descreve o loop de screenshot e ação que um agente de computer use executa: uma observação é um screenshot, e não um resultado de ferramenta, e uma ação é uma coordenada de tela ou o pressionar de uma tecla, e não um argumento de função. Use para: o material de grounding de uma ação em uma coordenada da etapa 11 e para entender por que esse loop precisa de uma história de confiabilidade diferente da de um loop de chamada de ferramentas.
- [Paper: "WebArena: A Realistic Web Environment for Building Autonomous Agents", Zhou et al., 2023](https://arxiv.org/abs/2307.13854)
  Um ambiente web auto-hospedado com verificações de correção funcional, construído para agentes que agem por meio de um navegador. Use para: a etapa 11, como o padrão contra o qual se fazem afirmações sobre a confiabilidade de agentes de navegador.
- [Paper: "GAIA: A Benchmark for General AI Assistants", Mialon et al., 2023](https://arxiv.org/abs/2311.12983)
  Perguntas fáceis para uma pessoa e difíceis para um agente, que exigem uso de ferramentas em vários passos com uma única resposta inequívoca. Use para: a etapa 13, como contrapeso a benchmarks que um modelo consegue passar sem agir.
- [Docs: "Prompt caching", Claude Platform Docs](https://platform.claude.com/docs/en/build-with-claude/prompt-caching)
  Colocar em cache um prefixo de prompt para cortar custo e latência repetidos, incluindo por que as definições estáveis de ferramentas e o system prompt de um agente são exatamente o prefixo que vale a pena guardar e o que invalida o cache em silêncio. Use para: o material de amplificação de tokens e custo da etapa 15.

## Lacunas

- Não existe referência neutra quanto a provedor para os formatos de chamada de ferramenta na rede. Cada provedor documenta apenas o seu, então os pares de requisição e resposta capturados que esta trilha mostra precisam ser tirados da documentação dos provedores e conciliados à mão.
- A execução durável e retomável de agentes está documentada principalmente dentro de frameworks individuais, o que não é neutro quanto a provedor nem estável o bastante para ser listado ainda. A etapa 15 precisa de uma fonte que não seja nenhuma das duas coisas.
- Computer use e agentes de navegador avançam mais depressa do que qualquer coisa escrita sobre eles. Os papers de benchmark listados cobrem como avaliar um agente, e não a prática atual para construir um, então a etapa 11 é a parte do arco com menos fontes.
- Nada listado até agora cobre a memória de agentes entre execuções como um sistema projetado, e não como um recurso de produto. A etapa 6 precisa de uma.
