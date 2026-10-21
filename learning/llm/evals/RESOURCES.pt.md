---
title: "Recursos"
description: "Fontes confiáveis sobre evals"
type: resources
---

# Recursos de Evals

## Conhecimento

- [Docs: "Define success criteria and build evaluations", Claude Platform Docs](https://platform.claude.com/docs/en/test-and-evaluate/develop-tests)
  Passo a passo de profissionais para transformar uma pergunta vaga como "melhorou?" em critérios de sucesso mensuráveis e em um conjunto de eval held-out. Use para: projetar o eval em si antes de recorrer a um framework.
- [Repositório: openai/evals, OpenAI](https://github.com/openai/evals)
  Framework oficial para definir e executar um eval como código: prompts, lógica de avaliação e um registro de evals existentes para ler como exemplos resolvidos. Use para: como estruturar e executar um eval customizado.
- [Repositório: lm-evaluation-harness, EleutherAI](https://github.com/EleutherAI/lm-evaluation-harness)
  O harness padrão de fato para executar um modelo contra benchmarks padronizados, com as configurações de tarefa mostrando como os conjuntos held-out são estruturados e pontuados na prática. Use para: executar ou adaptar um benchmark existente em vez de construir um eval do zero.
- [Artigo científico: "Judging LLM-as-a-Judge with MT-Bench and Chatbot Arena", Zheng et al., 2023](https://arxiv.org/abs/2306.05685)
  Introduz o LLM-as-judge para tarefas abertas e mede seus vieses contra a preferência humana: viés de posição, viés de verbosidade, viés de autopreferência. Use para: decidir se um juiz LLM é confiável para um dado caso, e o que corrigir se for.
- [Docs: Evaluate, Hugging Face](https://huggingface.co/docs/evaluate/index)
  Biblioteca de métricas padrão específicas da tarefa (BLEU, ROUGE, exact match, F1 e mais), com a definição e os modos de falha de cada uma. Use para: o lado das métricas específicas da tarefa na comparação entre métrica e LLM-as-judge.
- [Artigo científico: "Time Travel in LLMs: Tracing Data Contamination in Large Language Models", Golchin e Surdeanu, 2023](https://arxiv.org/abs/2308.08493)
  Um método concreto para testar se os dados de um benchmark vazaram para o conjunto de treinamento de um modelo, com a técnica de adivinhar o resto da instância que o detecta. Use para: defender a honestidade de um conjunto held-out contra a alegação específica de que "o modelo só memorizou isto".
- [Artigo científico: "Beyond the Imitation Game: Quantifying and Extrapolating the Capabilities of Language Models" (BIG-bench), Srivastava et al., 2022](https://arxiv.org/abs/2206.04615)
  Introduz a convenção da canary string (uma frase marcadora única embutida nos dados de um benchmark, pedindo que os crawlers a excluam dos corpora de treinamento) como técnica preventiva de resistência à contaminação para o lançamento do próprio benchmark. Use para: projetar um conjunto de eval customizado que resista à contaminação desde o início, em vez de detectá-la depois do fato.
- [Artigo científico: "Evaluating Large Language Models Trained on Code" (Codex), Chen et al., 2021](https://arxiv.org/abs/2107.03374)
  Introduz a correção funcional (executar o código gerado contra casos de teste em vez de comparar texto) e o estimador pass@k não enviesado, com a fórmula combinatória que evita a alta variância de reamostrar diretamente k completions. Use para: avaliar geração de código, e para o princípio geral de verificar comportamento em vez de similaridade de texto sempre que uma tarefa é executável.

- [Artigo: "Cohen's kappa", Wikipedia](https://en.wikipedia.org/wiki/Cohen%27s_kappa)
  A estatística de concordância entre avaliadores corrigida pelo acaso: sua fórmula, por que um kappa de 0 significa que não é melhor que o acaso e sua conhecida tendência a subestimar a concordância em uma categoria rara. Use para: medir a concordância entre avaliadores humanos com precisão, em vez de olhar a olho uma porcentagem de concordância bruta.
- [Artigo: "Inter-rater reliability", Wikipedia](https://en.wikipedia.org/wiki/Inter-rater_reliability)
  Cobre por que a concordância bruta por probabilidade conjunta engana (inflada pelo acaso, pior com menos categorias) e o alfa de Krippendorff como generalização da concordância corrigida pelo acaso para qualquer número de avaliadores e qualquer nível de medição. Use para: escolher a estatística de concordância certa para mais de dois avaliadores ou avaliações não categóricas.
- [Artigo científico: "HarmBench: A Standardized Evaluation Framework for Automated Red Teaming and Robust Refusal", Mazeika et al., 2024](https://arxiv.org/abs/2402.04249)
  Introduz um framework padronizado para avaliar métodos de red-teaming automatizado contra modelos e defesas, em escala e de forma comparável, onde antes a área não tinha um. Use para: a taxa de sucesso de ataque como métrica, e a distinção entre um método de geração de ataques e uma forma rigorosa de avaliá-lo.
- [Artigo científico: "XSTest: A Test Suite for Identifying Exaggerated Safety Behaviours in Large Language Models", Röttger et al., 2023](https://arxiv.org/abs/2308.01263)
  Uma suíte de testes com prompts seguros escritos para se parecer com prompts inseguros, especificamente para trazer à tona a recusa excessiva. Use para: a tensão precisa entre inocuidade (recusar prompts inseguros) e utilidade (não recusar os seguros), e uma forma concreta de medir um modelo que cai mal nesse trade-off.
- [Artigo científico: "τ-bench: A Benchmark for Tool-Agent-User Interaction in Real-World Domains", Yao et al., 2024](https://arxiv.org/abs/2406.12045)
  Avalia agentes comparando o estado do banco de dados ao fim da conversa com um estado-alvo anotado, e introduz o `pass^k` para medir a confiabilidade de um agente em tentativas repetidas da mesma tarefa. Use para: por que o sucesso na tarefa vence a comparação de trajetória passo a passo, e a distinção precisa, fácil de confundir, entre `pass^k` e o `pass@k` da lição 4.
- [Artigo científico: "AgentBench: Evaluating LLMs as Agents", Liu et al., 2023](https://arxiv.org/abs/2308.03688)
  Um benchmark multidimensional em 8 ambientes interativos distintos que testa o raciocínio e a tomada de decisão de um LLM como agente, encontrando uma diferença significativa entre os melhores modelos e os menores especificamente em cenários agênticos. Use para: evidência de que a capacidade agêntica é algo distinto a medir, e não está implícita no desempenho em benchmarks de turno único.
- [Artigo científico: "Ragas: Automated Evaluation of Retrieval Augmented Generation", Es et al., 2023](https://arxiv.org/abs/2309.15217)
  Um framework sem referência que separa as dimensões de qualidade de recuperação, fidelidade e qualidade de geração de um sistema RAG em métricas independentes. Use para: calcular uma pontuação de fidelidade sem precisar de uma resposta de referência escrita por humanos, e para manter a falha de recuperação e a falha de geração diagnosticáveis como perguntas separadas.
- [Artigo científico: "Enabling Large Language Models to Generate Text with Citations" (ALCE), Gao et al., 2023](https://arxiv.org/abs/2305.14627)
  Introduz métricas automáticas de qualidade de citação correlacionadas com o julgamento humano, e a constatação de que até os melhores sistemas carecem de sustentação completa por citação em cerca de metade de suas afirmações em um conjunto de teste. Use para: a correção de citações como verificação mais rigorosa e separada da fidelidade.
- [Artigo científico: "Seven Rules of Thumb for Web Site Experimenters", Kohavi et al., 2014](https://exp-platform.com/Documents/2014%20experimentersRulesOfThumb.pdf)
  A orientação prática de Kohavi e coautores para executar experimentos controlados online, incluindo o conceito de OEC (movível e causalmente ligado ao resultado real) e as métricas guardrail. Use para: escolher um OEC defensável em vez de uma métrica fácil de mover mas sem causalidade, e por que uma métrica guardrail precisa ser acompanhada ao lado dele.
- [Guia: "Rules of Machine Learning", Zinkevich, Google](https://developers.google.com/machine-learning/guides/rules-of-ml)
  A orientação interna de engenharia de ML do Google, incluindo a Regra 37 (medir o training/serving skew como várias comparações distintas, e não uma) e a Regra 8 (requisitos de atualidade). Use para: qual exatamente das várias causas possíveis de uma diferença offline/online, variância comum, drift ou um erro de engenharia, de fato se aplica, e por que cada uma exige uma correção diferente.
- [Artigo científico: "The Tail at Scale", Dean e Barroso, 2013](https://www.barroso.org/publications/TheTailAtScale.pdf)
  A explicação canônica de por que a latência de cauda, e não a latência média, determina a capacidade de resposta no mundo real em escala, especialmente quando uma requisição se espalha por muitas chamadas de backend. Use para: por que uma decisão de go/no-go precisa de um percentil (p95/p99), e não só de uma média, antes de descartar uma regressão de latência.
- [Artigo científico: "The Leaderboard Illusion", Singh et al., 2025](https://arxiv.org/abs/2504.20879)
  Documenta a divulgação seletiva no Chatbot Arena: testes privados pré-lançamento de muitas variantes de modelo (27 só para o Llama 4) e um acesso a dados grande e assimétrico favorecendo um punhado de provedores de modelos fechados. Use para: um exemplo concreto, atual e bem documentado de por que uma posição em leaderboard não é, por si só, uma medição neutra e confiável.
- [Artigo: "Does Style Matter?", LMArena](https://lmarena.ai/blog/style-control)
  A própria análise da arena mostrando que os rankings mudam de forma significativa quando o tamanho da resposta e a formatação em markdown são controlados. Use para: confirmar que o mecanismo de viés de verbosidade da lição 6 opera de forma idêntica em escala plena de leaderboard, com avaliadores humanos em vez de um único juiz LLM.

## Lacunas

- Ainda não há fonte dedicada sobre testes de significância estatística para diferenças de pontuação de eval (erro padrão de uma proporção, testes de significância pareados como o de McNemar). A missão precisa disso para a pergunta da etapa 5, "esta diferença é real ou ruído"; a lição 9 a ensina a partir de método estatístico estável e padrão, e não de uma única fonte citada, e esta lacuna deve se fechar quando uma boa fonte de nível prático for encontrada.
