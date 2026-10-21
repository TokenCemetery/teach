---
title: "Recursos"
description: "Fontes e comunidades confiáveis sobre fine-tuning com adapters"
type: resources
---

# Recursos de Fine-Tuning com Adapters

## Conhecimento

### Os três métodos

- [Artigo científico: "LoRA: Low-Rank Adaptation of Large Language Models", Hu et al., arXiv:2106.09685](https://arxiv.org/abs/2106.09685)
  O método original de adapter de baixo rank e o argumento da dimensionalidade intrínseca para explicar por que ele funciona. Use para: a etapa 3, e para o que rank e alpha de fato controlam.

- [Artigo científico: "QLoRA: Efficient Finetuning of Quantized LLMs", Dettmers et al., arXiv:2305.14314](https://arxiv.org/abs/2305.14314)
  NF4, dupla quantização e otimizadores paginados, com a contabilidade de memória explicitada. Use para: a etapa 4, e como referência do que um base quantizado custa em qualidade. Leia a seção de limitações.

- [Artigo científico: "DoRA: Weight-Decomposed Low-Rank Adaptation", Liu et al., arXiv:2402.09353](https://arxiv.org/abs/2402.09353)
  Divide os pesos em magnitude e direção e adapta a direção. Use para: a etapa 5. A análise da seção 4 sobre como o full fine-tuning e o LoRA movem cada grandeza é o argumento de verdade.

- [Artigo científico: "Intrinsic Dimensionality Explains the Effectiveness of Language Model Fine-Tuning", Aghajanyan et al., arXiv:2012.13255](https://arxiv.org/abs/2012.13255)
  Por que a adaptação pode viver em um subespaço de baixa dimensão. Use para: a justificativa por baixo do LoRA, e não o mecanismo.

### Prática atual

- [Docs: "LoRA Without Regret", Hugging Face TRL](https://huggingface.co/docs/trl/main/en/lora_without_regret)
  O argumento de que targets all-linear com rank adequado fecham a diferença para o full fine-tuning. Use para: a escolha de target modules e de rank, e como o baseline que toda nova variante precisa superar. Isto substitui a convenção de só atenção herdada do artigo original.

- [Artigo: "Practical Tips for Finetuning LLMs Using LoRA", Sebastian Raschka, Ahead of AI](https://magazine.sebastianraschka.com/p/practical-tips-for-finetuning-llms)
  Ablações sobre rank, alpha e target modules, com os experimentos à mostra. Use para: conferir o folclore de hiperparâmetros contra medições.

- [Docs: PEFT, Hugging Face](https://huggingface.co/docs/peft)
  Implementação de referência dos três métodos e da superfície de configuração que eles expõem. Use para: saber como um hiperparâmetro se chama na prática e quais variantes estão estabelecidas o bastante para virar uma flag. Depende da versão, então confira com a release instalada em vez de confiar na memória.

- [Docs: SFTTrainer, Hugging Face TRL](https://huggingface.co/docs/trl/main/en/sft_trainer)
  O loop padrão de supervised fine-tuning e seus formatos de dataset. Use para: da etapa 3 em diante. Depende da versão; os nomes dos parâmetros mudaram entre releases.

### Fundamentos

- [Interativo: LLM Visualization, Brendan Bycroft](https://bbycroft.net/llm)
  Percorra o caminho de um único token com a contagem de parâmetros de cada matriz. Use para: a etapa 1, e a melhor resposta disponível para "onde ficam os parâmetros".

- [Artigo: "The Illustrated Transformer", Jay Alammar](https://jalammar.github.io/illustrated-transformer/)
  A explicação visual padrão da arquitetura. Use para: a etapa 1, quando a estrutura de blocos ainda não assentou.

- [Docs: Chat Templates, Hugging Face Transformers](https://huggingface.co/docs/transformers/main/en/chat_templating)
  Como as conversas são renderizadas em sequências de tokens e como aplicar o template do próprio modelo. Use para: a falha silenciosa mais comum no fine-tuning.

- [Artigo científico: "Decoupled Weight Decay Regularization" (AdamW), Loshchilov & Hutter, arXiv:1711.05101](https://arxiv.org/abs/1711.05101)
  O otimizador que tudo aqui usa, e por que seu weight decay difere do do Adam. Use para: o argumento de memória da etapa 2.

- [Artigo científico: "ZeRO: Memory Optimizations Toward Training Trillion Parameter Models", Rajbhandari et al., arXiv:1910.02054](https://arxiv.org/abs/1910.02054)
  A contabilidade canônica de pesos, gradientes e estado do otimizador como categorias separadas de memória. Use para: derivar o número de dezesseis bytes por parâmetro.

- [Artigo científico: "Training Deep Nets with Sublinear Memory Cost", Chen et al., arXiv:1604.06174](https://arxiv.org/abs/1604.06174)
  O gradient checkpointing e a troca de computação por memória que ele faz. Use para: a etapa 2, e para a configuração que você vai deixar ligada de forma permanente.

- [Artigo: "A Recipe for Training Neural Networks", Andrej Karpathy](https://karpathy.github.io/2019/04/25/recipe/)
  Como conduzir experimentos para que seus resultados signifiquem algo. Use para: a lição de diagnóstico da etapa 3, e o smoke test de overfitting em dois exemplos.

### Quantização

- [Artigo científico: "LLM.int8(): 8-bit Matrix Multiplication for Transformers at Scale", Dettmers et al., arXiv:2208.07339](https://arxiv.org/abs/2208.07339)
  O problema das features outlier que torna a quantização de transformers mais difícil do que a aritmética sugere. Use para: por que por bloco vence por tensor.

- [Docs: bitsandbytes quantization, Hugging Face Transformers](https://huggingface.co/docs/transformers/main/en/quantization/bitsandbytes)
  A superfície de configuração de 4 bits na prática. Use para: a configuração da etapa 4.

- [Código: bitsandbytes, bitsandbytes-foundation](https://github.com/bitsandbytes-foundation/bitsandbytes)
  O diretório `backends/` é a autoridade sobre qual hardware suporta qual operação. Use para: resolver uma dúvida de suporte de hardware contra o código-fonte, e não contra um tutorial, que nesta área costuma estar desatualizado.

### Dados e avaliação

- [Artigo científico: "LIMA: Less Is More for Alignment", Zhou et al., arXiv:2305.11206](https://arxiv.org/abs/2305.11206)
  Evidência de que um dataset pequeno e cuidadosamente curado supera um grande e descuidado, e de que o SFT ensina em grande parte o formato. Use para: o argumento de abertura da etapa 6.

- [Artigo científico: "Judging LLM-as-a-Judge with MT-Bench and Chatbot Arena", Zheng et al., arXiv:2306.05685](https://arxiv.org/abs/2306.05685)
  Avaliação com modelo como juiz, com seus vieses caracterizados: posição, verbosidade, autopreferência. Use para: métricas de geração de texto livre, e para entender por que o juiz precisa ser calibrado contra rótulos humanos.

- [Artigo científico: "An Empirical Study of Catastrophic Forgetting in Large Language Models During Continual Fine-tuning", Luo et al., arXiv:2308.08747](https://arxiv.org/abs/2308.08747)
  Que o esquecimento é mensurável, comum e não restrito a casos extremos. Use para: justificar o conjunto de regressão para quem acha que ele é custo extra.

- [Artigo científico: "Fine-tuning Aligned Language Models Compromises Safety, Even When Users Do Not Intend To!", Qi et al., arXiv:2310.03693](https://arxiv.org/abs/2310.03693)
  O comportamento de segurança se degradando com o fine-tuning em dados benignos. Use para: por que o conjunto de regressão precisa incluir casos de recusa.

- [Código: lm-evaluation-harness, EleutherAI](https://github.com/EleutherAI/lm-evaluation-harness)
  Implementações padrão de benchmarks e os problemas de contaminação que elas documentam. Use para: construir um eval, e para ler pontuações publicadas com ceticismo.

### Serving

- [Docs: LoRA adapters, vLLM](https://docs.vllm.ai/en/latest/features/lora.html)
  Servir adapters em produção, incluindo o roteamento multi-adapter. Use para: a etapa 7. Confira os limites de rank máximo e de número máximo de adapters contra a versão instalada.

- [Artigo científico: "S-LoRA: Serving Thousands of Concurrent LoRA Adapters", Sheng et al., arXiv:2311.03285](https://arxiv.org/abs/2311.03285)
  Como muitos adapters são agrupados em batch de forma eficiente sobre um único base compartilhado. Use para: entender por que o serving multi-adapter é um problema resolvido, e não uma ideia de pesquisa.

- [Artigo: "LLM Inference Performance Engineering: Best Practices", Databricks](https://www.databricks.com/blog/llm-inference-performance-engineering-best-practices)
  Prefill versus decode, e a que cada fase está limitada. Use para: a aritmética de custo da etapa 7.

### A alternativa

- [Artigo científico: "Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks", Lewis et al., arXiv:2005.11401](https://arxiv.org/abs/2005.11401)
  A formulação canônica da abordagem que normalmente deve ser preferida quando o problema é de conhecimento. Use para: o argumento da lição final, e para defender com credibilidade o caso contra o fine-tuning.

## Sabedoria (Comunidades)

- [r/LocalLLaMA](https://www.reddit.com/r/LocalLLaMA/)
  A maior concentração de pessoas fazendo fine-tuning em hardware de consumo, em todos os backends. Use para: pesquisar o que já funcionou dentro de um orçamento de memória, qual folclore vale testar e relatos de replicação de métodos novos. Leia o arquivo; postar é uma repetição, não uma fonte.

- [Hugging Face Forums](https://discuss.huggingface.co/)
  Pesquisável e arquivado, com autores das bibliotecas presentes. Use para: o comportamento do PEFT, do TRL e do `transformers` que a documentação deixa ambíguo.

- [EleutherAI Blog](https://blog.eleuther.ai/)
  Textos de um grupo que lê criticamente a própria área, incluindo resultados negativos. Use para: os julgamentos das etapas 5 e 7 sobre se um resultado alegado se generaliza. O Discord deles é onde isso é discutido primeiro, e deliberadamente não está listado: nada do que se diz lá pode ser recuperado depois.

- [MLX Discussions, ml-explore/mlx](https://github.com/ml-explore/mlx/discussions)
  Público, pesquisável e respondido pelos mantenedores. Use para: ler se uma dada operação já é suportada no Apple Silicon, o que normalmente já foi perguntado.

## Lacunas

- Nenhuma fonte acompanha quais versões de `torch`, PEFT, TRL e de bibliotecas de quantização de fato funcionam juntas em uma dada versão de Python e plataforma. Isso bloqueia uma primeira execução com mais frequência do que qualquer conceito, e cada ambiente precisa ser verificado contra as notas de release em vez de presumido.
- A cobertura de backends de hardware para operações de 4 bits muda de release para release. Nenhum documento é confiável aqui; o código-fonte da biblioteca é a única autoridade, e qualquer afirmação de tutorial sobre requisitos de hardware deve ser tratada como expirada.
- Ainda não há fonte confiável sobre design de avaliação específico para a adaptação de modelos pequenos a tarefas. Este é o elo mais fraco da etapa 6 e a parte mais difícil da missão. A literatura geral de avaliação mira o benchmarking de foundation models, não a prova de que um adapter estreito ajudou.
- A maior parte dos conselhos publicados sobre hiperparâmetros de LoRA mira modelos de 7B para cima. Pouco trata de saber se eles se transferem para a classe de 1B a 3B, que é onde a maioria das pessoas de fato começa.
- Nenhuma replicação independente foi levantada para o DoRA na escala de que o LoRA e o QLoRA desfrutam. Trate os ganhos relatados dele como algo que precisa de medição local.
- Nenhuma fonte foi escolhida para decodificação restrita, que a Lição 27 recomenda como a resposta correta para problemas de validade de schema. Ela é nomeada sem uma referência por trás.
