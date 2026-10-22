---
title: "Recursos"
description: "Fontes confiáveis sobre pós-treinamento de LLMs"
type: resources
---

# Recursos de Pós-treinamento de LLMs

## Conhecimento

- [Artigo científico: "Training language models to follow instructions with human feedback", Ouyang et al., 2022](https://arxiv.org/abs/2203.02155)
  O artigo do InstructGPT. Define o pipeline de SFT, reward model e PPO que a maior parte do trabalho de RLHF desde então seguiu, e mede o alignment tax contra um modelo puramente pré-treinado. Use para: as etapas 1, 2 e 3, e o enquadramento do alignment tax da etapa 9.
- [Artigo científico: "Proximal Policy Optimization Algorithms", Schulman et al., 2017](https://arxiv.org/abs/1707.06347)
  Apresenta o PPO como um algoritmo geral de reinforcement learning, independente de modelos de linguagem. Use para: o algoritmo central da etapa 4, lido antes da sua aplicação específica a modelos de linguagem.
- [Artigo científico: "Training a Helpful and Harmless Assistant with Reinforcement Learning from Human Feedback", Bai et al., 2022](https://arxiv.org/abs/2204.05862)
  O relato da Anthropic sobre a mesma receita de SFT a RLHF em escala de produção, incluindo onde o reward hacking e a otimização excessiva contra o reward model apareceram na prática. Use para: o material de reward hacking da etapa 3 e o relato da etapa 4 sobre o que de fato dá errado.
- [Artigo científico: "Direct Preference Optimization: Your Language Model is Secretly a Reward Model", Rafailov et al., 2023](https://arxiv.org/abs/2305.18290)
  Deriva uma recompensa em forma fechada implicada por uma policy e um modelo de referência, substituindo o reward model separado e o loop de RL por uma única loss em estilo supervisionado sobre pares de preferência. Use para: a derivação central da etapa 5.
- [Artigo científico: "DeepSeekMath: Pushing the Limits of Mathematical Reasoning in Open Language Models", Shao et al., 2024](https://arxiv.org/abs/2402.03300)
  Apresenta o GRPO, substituindo a função de valor aprendida do PPO por um baseline relativo ao grupo calculado a partir de várias completions amostradas por prompt. Use para: o algoritmo central da etapa 6.
- [Artigo científico: "DeepSeek-R1: Incentivizing Reasoning Capability in LLMs via Reinforcement Learning", DeepSeek-AI, 2025](https://arxiv.org/abs/2501.12948)
  Treina chain-of-thought estendido principalmente por RL contra recompensas verificáveis e descreve a destilação do comportamento resultante em modelos menores. Use para: a fonte principal da etapa 7.
- [Artigo científico: "Constitutional AI: Harmlessness from AI Feedback", Bai et al., 2022](https://arxiv.org/abs/2212.08073)
  Substitui as preferências de inofensividade rotuladas por humanos por um modelo que critica e revisa as próprias saídas contra um conjunto escrito de princípios. Use para: o caso central da etapa 8 de feedback produzido por um modelo, e não por um humano.
- [Artigo científico: "RLAIF: Scaling Reinforcement Learning from Human Feedback with AI Feedback", Lee et al., 2023](https://arxiv.org/abs/2309.00267)
  Uma comparação direta e controlada do RLAIF com o RLHF nas mesmas tarefas, relatando onde o feedback de IA se iguala ao feedback humano e onde não. Use para: a etapa 8, como o complemento empírico do método do Constitutional AI.
- [Artigo científico: "Llama 2: Open Foundation and Fine-Tuned Chat Models", Touvron et al., 2023](https://arxiv.org/abs/2307.09288)
  Uma receita de RLHF publicada em escala de modelo aberto, incluindo detalhes do treinamento do reward model e um processo iterativo de RLHF em várias rodadas. Use para: conferir as etapas 3 e 4 contra uma receita completa e reproduzível.
- [Documentação: "TRL - Transformer Reinforcement Learning", Hugging Face](https://huggingface.co/docs/trl/index)
  A biblioteca que os labs de SFT e DPO desta trilha de fato executam, com configuração prática para cada trainer. Use para: a prática das etapas 2, 4 e 5.

## Lacunas

- Ainda não há fonte primária sobre a qualidade dos dados de preferência: discordância entre anotadores, instruções de rotulagem e como as escolhas de coleta de dados de preferência enviesam um reward model treinado. Necessária antes que o material de qualidade de dados da etapa 3 possa ser totalmente fundamentado.
- A medição do alignment tax além do próprio relato do InstructGPT é escassa; um tratamento mais recente e independente de modelo reforçaria a etapa 9.
- Ainda não há um relato de produção de uma comparação completa de custo entre DPO, PPO e GRPO feita a partir da infraestrutura de uma única equipe; a lição de julgamento da etapa 10 atualmente precisa sintetizar isso a partir de artigos separados, e não de uma fonte que já tenha feito a comparação.
