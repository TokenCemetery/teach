---
title: Recursos
description: "Fontes confiáveis sobre prompting"
type: resources
---

# Recursos de Prompting

## Conhecimento

- [Docs: "Prompting best practices", Claude Platform Docs](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/claude-prompting-best-practices)
  O guia consolidado de um fornecedor: instruções claras, exemplos, tags XML, papéis, thinking, contexto longo e formato de saída, com prompts de antes e depois. Use para: a base prática dos estágios 2 a 6, lida como o comportamento documentado de um único fornecedor.
- [Docs: "Prompt engineering overview", Claude Platform Docs](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/overview)
  O conselho de definir critérios de sucesso e testes antes de iterar, e uma breve nota de que nem toda avaliação que falha é melhor corrigida com prompting. Use para: o hábito de medir primeiro.
- [Docs: "Long context prompting", section of Prompting best practices, Claude Platform Docs](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/claude-prompting-best-practices#long-context-prompting)
  Colocar documentos longos antes da consulta, envolver cada um em tags com seus metadados e pedir primeiro as citações relevantes. Use para: organizar uma entrada longa.
- [Docs: "Structured outputs", Claude Platform Docs](https://platform.claude.com/docs/en/build-with-claude/structured-outputs)
  Um recurso de provedor que impõe um schema JSON à resposta, documentado junto com o que apenas o prompt não garante. Use para: a fronteira entre pedir estrutura e impô-la.
- [Docs: "Prompt caching", Claude Platform Docs](https://platform.claude.com/docs/en/build-with-claude/prompt-caching)
  Como um prefixo em cache é correspondido, o que o invalida e a ordem que o prompt precisa manter para haver um hit. Use para: organizar um prompt de modo que suas partes estáveis fiquem em cache.
- [Docs: "Model IDs and versioning", Claude Platform Docs](https://platform.claude.com/docs/en/about-claude/models/model-ids-and-versions)
  Como um fornecedor nomeia snapshots fixos e aliases móveis, e que cada ID tem seu próprio cronograma de aposentadoria. Use para: fixar um prompt no modelo contra o qual foi testado.
- [Docs: "Extended thinking", Claude Platform Docs](https://platform.claude.com/docs/en/build-with-claude/extended-thinking)
  A mecânica de API de uma fase de thinking: o orçamento de tokens, seu mínimo e como o thinking conta para o limite de saída. Use para: os fatos de orçamento por trás do prompting de um modelo de raciocínio; o conselho sobre redação está no guia de boas práticas.
- [Docs: "Define success criteria and build evaluations", Claude Platform Docs](https://platform.claude.com/docs/en/test-and-evaluate/develop-tests)
  Transformar "este prompt é melhor?" em critérios de sucesso e um design de avaliação, incluindo casos extremos e comparação com uma baseline. Use para: decidir contra o que uma mudança de prompt deve ser julgada antes de mudar qualquer coisa.
- [Docs: "Mitigate jailbreaks and prompt injections", Claude Platform Docs](https://platform.claude.com/docs/en/test-and-evaluate/strengthen-guardrails/mitigate-jailbreaks)
  Mitigações no nível do prompt e do sistema, incluindo filtrar a entrada e limitar o que o modelo pode fazer. Use para: quais defesas pertencem a quem escreve o prompt.
- [Docs: "Prompt design strategies", Gemini API, Google](https://ai.google.dev/gemini-api/docs/prompting-strategies)
  O guia de um segundo fornecedor sobre instruções, exemplos few-shot, prefixos e decomposição de uma tarefa. Use para: verificar se uma técnica é geral ou comportamento de um único fornecedor.
- [Docs: "Chat templates", Hugging Face Transformers](https://huggingface.co/docs/transformers/main/en/chat_templating)
  Como uma lista de mensagens marcadas por papel é renderizada na sequência única de tokens com a qual um modelo foi treinado, com saídas reais de template. Use para: o que o modelo realmente vê.
- [Repo: "Prompt engineering interactive tutorial", Anthropic](https://github.com/anthropics/prompt-eng-interactive-tutorial)
  Exercícios em notebook sobre papéis, separar dados de instruções, exemplos, raciocínio passo a passo e evitar alucinação. Use para: repetições práticas dos estágios 1 a 4.
- [Paper: "The Prompt Report: A Systematic Survey of Prompting Techniques", Schulhoff et al., 2024](https://arxiv.org/abs/2406.06608)
  Um survey e taxonomia de técnicas de prompting com vocabulário consistente. Use para: situar uma técnica que você encontra por aí e esclarecer o que um termo significa.
- [Paper: "Quantifying Language Models' Sensitivity to Spurious Features in Prompt Design", Sclar et al., 2023](https://arxiv.org/abs/2310.11324)
  Mostra mudanças de formatação que preservam o significado (separadores, capitalização, espaçamento) movendo a acurácia few-shot em grandes margens. Use para: entender por que uma edição de prompt é uma afirmação a testar, não uma escolha de estilo.
- [Paper: "Rethinking the Role of Demonstrations", Min et al., 2022](https://arxiv.org/abs/2202.12837)
  Constata que trocar aleatoriamente os rótulos das demonstrações quase não prejudica, enquanto o formato, o espaço de rótulos e a distribuição das entradas importam. Use para: o que os exemplos few-shot realmente ensinam.
- [Paper: "Calibrate Before Use: Improving Few-Shot Performance of Language Models", Zhao et al., 2021](https://arxiv.org/abs/2102.09690)
  Nomeia os vieses de rótulo majoritário, de recência e de token comum em prompts few-shot e propõe a calibração contextual. Use para: os vieses que um conjunto de exemplos traz.
- [Paper: "Fantastically Ordered Prompts and Where to Find Them", Lu et al., 2021](https://arxiv.org/abs/2104.08786)
  Mostra a ordem dos mesmos exemplos few-shot levando a acurácia de perto do estado da arte a perto do acaso. Use para: entender por que a ordem dos exemplos é uma variável a controlar.
- [Paper: "Chain-of-Thought Prompting Elicits Reasoning in Large Language Models", Wei et al., 2022](https://arxiv.org/abs/2201.11903)
  O resultado original de chain-of-thought few-shot e a constatação de que o ganho só aparece em escala de modelo suficiente. Use para: quando pedir raciocínio ajuda.
- [Paper: "Large Language Models are Zero-Shot Reasoners", Kojima et al., 2022](https://arxiv.org/abs/2205.11916)
  Chain-of-thought zero-shot: uma única frase de gatilho que provoca raciocínio sem exemplos. Use para: raciocínio sem demonstrações escritas à mão.
- [Paper: "Self-Consistency Improves Chain of Thought Reasoning in Language Models", Wang et al., 2022](https://arxiv.org/abs/2203.11171)
  Amostrar vários caminhos de raciocínio e ficar com a resposta majoritária. Use para: trocar tokens por acurácia em uma tarefa com uma única resposta verificável.
- [Paper: "Language Models Don't Always Say What They Think", Turpin et al., 2023](https://arxiv.org/abs/2305.04388)
  Mostra o chain-of-thought de um modelo omitindo a característica de viés que de fato motivou sua resposta. Use para: entender por que o raciocínio escrito não é uma explicação fiel.
- [Paper: "Let Me Speak Freely? A Study on the Impact of Format Restrictions on Performance of Large Language Models", Tam et al., 2024](https://arxiv.org/abs/2408.02442)
  Mede a acurácia de raciocínio caindo sob restrições estritas de formato de saída. Use para: o custo de forçar um formato e como ordenar os campos.
- [Paper: "Lost in the Middle: How Language Models Use Long Contexts", Liu et al., 2023](https://arxiv.org/abs/2307.03172)
  A curva em U: a informação no início e no fim de um contexto longo é usada melhor que a informação no meio. Use para: decidir onde vão os documentos e a pergunta.
- [Paper: "The Instruction Hierarchy: Training LLMs to Prioritize Privileged Instructions", Wallace et al., 2024](https://arxiv.org/abs/2404.13208)
  Define os níveis de privilégio de system, user e saída de ferramentas e treina um modelo para seguir o mais alto em caso de conflito. Use para: entender por que o lugar de uma instrução muda o seu peso.
- [Paper: "When 'A Helpful Assistant' Is Not Really Helpful: Personas in System Prompts Do Not Improve Performances of Large Language Models", Zheng et al., 2023](https://arxiv.org/abs/2311.10054)
  Testa 162 personas em system prompts, em quatro famílias de modelos e 2.410 perguntas factuais, e não encontra melhora em relação a nenhuma persona, com o efeito de uma persona em grande parte aleatório. Use para: resolver com dados a disputa sobre role prompting.
- [Paper: "Not what you've signed up for: Compromising Real-World LLM-Integrated Applications with Indirect Prompt Injection", Greshake et al., 2023](https://arxiv.org/abs/2302.12173)
  Introduz a injeção de prompt indireta por meio de conteúdo recuperado e a demonstra contra aplicações reais. Use para: como um atacante alcança um prompt no qual nunca digita.
- [Paper: "Fine-Tuning or Retrieval? Comparing Knowledge Injection in LLMs", Ovadia et al., 2023](https://arxiv.org/abs/2312.05934)
  Compara o fine-tuning não supervisionado com a recuperação para acrescentar conhecimento e constata que a recuperação é consistentemente melhor, tanto para o conhecimento visto no treinamento quanto para fatos novos. Use para: a decisão entre prompt, RAG ou fine-tuning.
- [Article: "LLM01:2025 Prompt Injection", OWASP Gen AI Security Project](https://genai.owasp.org/llmrisk/llm01-prompt-injection/)
  A entrada de risco da indústria: injeção direta e indireta, impactos e mitigações ordenadas por onde ficam. Use para: o vocabulário compartilhado e a lista de mitigações.
- [Article: "The lethal trifecta for AI agents", Simon Willison](https://simonwillison.net/2025/Jun/16/the-lethal-trifecta/)
  Dados privados, conteúdo não confiável e um canal de exfiltração, juntos, tornam a injeção explorável, e remover um dos lados é a defesa. Use para: entender por que a defesa real fica fora do prompt.
- [Article: "Your AI Product Needs Evals", Hamel Husain](https://hamel.dev/blog/posts/evals/)
  Um argumento de praticante a favor de verificações no estilo de testes unitários e de traces reais registrados como base para iterar em um prompt. Use para: construir um conjunto de regressão a partir de falhas reais.

## Lacunas

- Os guias de prompt engineering, de raciocínio e de saída estruturada da OpenAI seriam uma terceira visão de fornecedor, mas todas as páginas em `platform.openai.com` e `developers.openai.com` responderam com 403 a uma verificação por script e a uma pelo navegador, então nenhuma pôde ser verificada como acessível. Adicione-as quando uma puder ser.
- Nenhuma fonte revisada por pares mede diretamente o versionamento de prompts nem as práticas de template. As lições 15 e 16 o ensinam a partir da documentação de fornecedores e da prática comum de engenharia de software, e dizem isso.
