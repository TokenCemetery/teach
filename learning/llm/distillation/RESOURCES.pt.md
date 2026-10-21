---
title: "Recursos"
description: "Fontes confiáveis sobre destilação de conhecimento de LLMs"
type: resources
---

# Recursos de Destilação

## Conhecimento

### Fundamentos

- [Artigo científico: "Distilling the Knowledge in a Neural Network", Hinton, Vinyals e Dean, 2015](https://arxiv.org/abs/1503.02531)
  O artigo que deu nome ao método: soft targets, temperatura, a correção do gradiente por T ao quadrado e a loss combinada, com experimentos em MNIST e em fala. Use para: a etapa 1, direto da fonte.
- [Artigo científico: "A Survey on Knowledge Distillation of Large Language Models", Xu et al., 2024](https://arxiv.org/abs/2402.13116)
  Um mapa da destilação de LLMs organizado pelo que se extrai do professor e por como o aluno é treinado com isso. Use para: situar um método na família mais ampla antes de ler o artigo do próprio método.
- [Artigo científico: "DistilBERT, a distilled version of BERT: smaller, faster, cheaper and lighter", Sanh et al., 2019](https://arxiv.org/abs/1910.01108)
  Uma destilação completa de um transformer durante o pré-treinamento, com uma loss tripla de termos de destilação, de modelagem de linguagem mascarada e de embedding por cosseno. Use para: uma receita completa com uma ablação de cada termo da loss.

### Destilação de logits e em nível de sequência

- [Artigo científico: "Sequence-Level Knowledge Distillation", Kim e Rush, 2016](https://arxiv.org/abs/1606.07947)
  Destilação em nível de palavra contra destilação em nível de sequência para tradução, e o treinamento na saída de beam search do professor. Use para: as etapas 2 e 3, o enquadramento original dos dois níveis.
- [Artigo científico: "MiniLLM: On-Policy Distillation of Large Language Models", Gu et al., 2023](https://arxiv.org/abs/2306.08543)
  O argumento a favor do reverse KL na destilação generativa, otimizado com um método de policy gradient sobre amostras do aluno. Use para: forward contra reverse KL, e uma forma de destilação on-policy.
- [Artigo científico: "Towards Cross-Tokenizer Distillation: the Universal Logit Distillation Loss for LLMs", Boizard et al., 2024](https://arxiv.org/abs/2402.12030)
  Uma loss baseada em transporte ótimo que compara vetores de probabilidade ordenados para que professor e aluno não precisem compartilhar um vocabulário. Use para: o que a destilação entre tokenizers faz e o que ela sacrifica.
- [Artigo científico: "Gemma 2: Improving Open Language Models at a Practical Size", Gemma Team, 2024](https://arxiv.org/abs/2408.00118)
  O treinamento dos modelos de 2B e 9B com destilação de conhecimento a partir de um professor maior, em vez de previsão do próximo token. Use para: a destilação como sinal de pré-treinamento.
- [Artigo científico: "Compact Language Models via Pruning and Knowledge Distillation", Muralidharan et al., 2024](https://arxiv.org/abs/2407.14679)
  Minitron: podar um modelo treinado e retreiná-lo com destilação a partir do original, em uma pequena fração dos tokens de treinamento originais. Use para: a destilação como etapa de recuperação depois da poda.
- [Artigo científico: "LLM Pruning and Distillation in Practice: The Minitron Approach", Sreenivas et al., 2024](https://arxiv.org/abs/2408.11796)
  A receita do Minitron aplicada ao Llama 3.1 8B e ao Mistral NeMo 12B, incluindo corrigir primeiro o professor nos dados de destilação. Use para: uma segunda execução, mais recente, da mesma receita.

### Destilação com dados sintéticos

- [Artigo científico: "Self-Instruct: Aligning Language Models with Self-Generated Instructions", Wang et al., 2022](https://arxiv.org/abs/2212.10560)
  Gerar dados de instrução a partir das próprias gerações de um modelo, com filtragem de quase duplicatas e de exemplos inválidos. Use para: como um conjunto de instruções gerado é construído.
- [Artigo: "Alpaca: A Strong, Replicable Instruction-Following Model", Stanford CRFM, 2023](https://crfm.stanford.edu/2023/03/13/alpaca.html)
  Fine-tuning do LLaMA 7B em 52 mil instruções geradas pelo text-davinci-003 com o método Self-Instruct, o seu custo e os seus limites e restrições de licença declarados. Use para: a execução de imitação barata canônica.
- [Artigo científico: "Distilling Step-by-Step! Outperforming Larger Language Models with Less Training Data and Smaller Model Sizes", Hsieh et al., 2023](https://arxiv.org/abs/2305.02301)
  Treinar um modelo pequeno para produzir os rationales do professor como uma segunda tarefa ao lado dos seus rótulos. Use para: o que os rationales acrescentam só aos rótulos.
- [Artigo científico: "Orca: Progressive Learning from Complex Explanation Traces of GPT-4", Mukherjee et al., 2023](https://arxiv.org/abs/2306.02707)
  Imitar traces de explicação obtidos com system prompts, com o ChatGPT como professor intermediário antes do GPT-4. Use para: traces de explicação e um professor assistente em escala de LLM.
- [Artigo científico: "Textbooks Are All You Need", Gunasekar et al., 2023](https://arxiv.org/abs/2306.11644)
  phi-1: um modelo pequeno de código treinado em dados filtrados da web e em livros-texto e exercícios sintéticos gerados pelo GPT-3.5. Use para: qualidade dos dados contra volume dos dados.
- [Artigo científico: "DeepSeek-R1: Incentivizing Reasoning Capability in LLMs via Reinforcement Learning", DeepSeek-AI, 2025](https://arxiv.org/abs/2501.12948)
  Destilar um modelo de raciocínio em modelos menores Qwen e Llama por fine-tuning nas suas amostras curadas, comparado com rodar RL diretamente no modelo pequeno (apêndice F.1). Use para: dados sintéticos obtidos por rejection sampling, e a lição de pós-treinamento para a qual esta trilha aponta.

### Destilação on-policy

- [Artigo científico: "On-Policy Distillation of Language Models: Learning from Self-Generated Mistakes", Agarwal et al., 2023](https://arxiv.org/abs/2306.13649)
  Generalized knowledge distillation: treinar em sequências geradas pelo aluno com uma divergência à escolha e uma mistura de dados fixos e on-policy. Use para: a etapa 5, direto da fonte.
- [Artigo científico: "Qwen3 Technical Report", Qwen Team, 2025](https://arxiv.org/abs/2505.09388)
  Destilação do forte para o fraco dos modelos pequenos do Qwen3, com uma etapa off-policy seguida de uma etapa on-policy, comparada com RL nos mesmos modelos. Use para: a destilação on-policy em uma família de modelos de produção.
- [Documentação: "Generalized Knowledge Distillation Trainer", Hugging Face TRL](https://huggingface.co/docs/trl/main/en/gkd_trainer)
  A implementação do GKD no TRL e os seus parâmetros `lmbda`, `beta` e `seq_kd`. Use para: executar a destilação on-policy em vez de apenas ler sobre ela.
- [Documentação: "General Online Logit Distillation (GOLD) Trainer", Hugging Face TRL](https://huggingface.co/docs/trl/main/en/gold_trainer)
  O trainer do TRL que estende o GKD com a Universal Logit Distillation loss, alinhando trechos de texto para que professor e aluno possam usar tokenizers diferentes. Use para: o que uma execução on-policy entre tokenizers exige.

### O que o aluno herda

- [Artigo científico: "Does Knowledge Distillation Really Work?", Stanton et al., 2021](https://arxiv.org/abs/2106.05945)
  Os alunos muitas vezes não conseguem igualar os seus professores mesmo quando têm capacidade para isso, e uma generalização melhor não exige uma fidelidade melhor. Os experimentos são em sua maioria de classificação de imagens, com uma tarefa de texto. Use para: separar a fidelidade da qualidade na tarefa.
- [Artigo científico: "The False Promise of Imitating Proprietary LLMs", Gudibande et al., 2023](https://arxiv.org/abs/2305.15717)
  Modelos de imitação avaliados por crowdworkers como próximos do ChatGPT fecharam pouco da lacuna em benchmarks direcionados. Use para: a lacuna de imitação e como as avaliações de preferência humana a esconderam.
- [Artigo científico: "Improved Knowledge Distillation via Teacher Assistant", Mirzadeh et al., 2019](https://arxiv.org/abs/1902.03393)
  A qualidade do aluno cai quando a distância entre professor e aluno fica grande demais, e um assistente de tamanho intermediário recupera parte dela; os ganhos nos seus experimentos de visão são pequenos. Use para: a lacuna de capacidade.
- [Artigo científico: "On the Efficacy of Knowledge Distillation", Cho e Hariharan, 2019](https://arxiv.org/abs/1910.01348)
  Professores mais precisos nem sempre geram alunos melhores, e interromper o treinamento do professor mais cedo pode ajudar. Use para: um segundo relato da lacuna de capacidade.
- [Artigo científico: "Subliminal Learning: Language models transmit behavioral traits via hidden signals in data", Cloud et al., 2025](https://arxiv.org/abs/2507.14805)
  Um aluno treinado em sequências de números de um professor adquiriu os traços do professor, quando os dois compartilhavam um base model. Use para: o que filtrar os dados não consegue remover.

### Dimensionamento

- [Artigo científico: "Distillation Scaling Laws", Busbridge et al., 2025](https://arxiv.org/abs/2502.08606)
  Uma lei de escala para a qualidade do aluno em função do tamanho do aluno, dos tokens de destilação e da qualidade do professor, e de quando a destilação supera o treinamento supervisionado do mesmo aluno. Também relata que a melhor temperatura de destilação foi 1 no seu cenário (apêndice G.2). Use para: a etapa 7 direto da fonte, e o contraponto a uma temperatura acima de 1 em um LLM.

### Licenciamento e termos

- [Termos: "Terms of Use", OpenAI](https://openai.com/policies/row-terms-of-use/)
  Os termos para consumidores da OpenAI para usuários fora do EEE, da Suíça e do Reino Unido, que listam usar a saída para desenvolver modelos que concorram com a OpenAI entre as coisas que um usuário não pode fazer. Use para: o que os termos de um provedor hospedado dizem sobre treinar com as suas saídas.
- [Licença: "Llama 3.1 Community License Agreement", Meta](https://github.com/meta-llama/llama-models/blob/main/models/llama3_1/LICENSE)
  Uma licença de pesos abertos que permite usar as saídas do modelo para melhorar outro modelo, com a condição de que o nome do modelo resultante comece com "Llama" quando ele for distribuído. Use para: o que a licença de um modelo aberto diz sobre treinar com as suas saídas.

## Lacunas

- O post da Thinking Machines sobre destilação on-policy é muito citado pela sua comparação de custo com o RL, mas o site recusa leituras por script e dentro do aplicativo, então nenhum número dele é usado aqui. A etapa 5 se apoia, em vez disso, nos artigos do GKD, do MiniLLM e do Qwen3.
- Termos de uso e licenças mudam sem uma versão que uma lição possa fixar. A lição 0013 os cita como foram lidos quando esta trilha foi escrita; reconfira a fonte antes de depender dela.
