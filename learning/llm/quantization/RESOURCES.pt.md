---
title: "Recursos"
description: "Fontes confiáveis sobre quantização de LLMs"
type: resources
---

# Recursos de Quantização

## Conhecimento

### Fundamentos

- [Artigo científico: "A White Paper on Neural Network Quantization", Nagel et al., 2021](https://arxiv.org/abs/2106.08295)
  Uma introdução do tamanho de um livro-texto, da Qualcomm AI Research: a motivação de hardware, o quantizador afim uniforme, a definição da faixa, a granularidade, os pipelines de PTQ e QAT e um fluxo de depuração. Use para: o mapeamento e a escolha da faixa nas etapas 2 e 6, direto da fonte e não de um resumo.
- [Artigo científico: "A Survey of Quantization Methods for Efficient Neural Network Inference", Gholami et al., 2021](https://arxiv.org/abs/2103.13630)
  Um levantamento amplo de quantizadores uniformes e não uniformes, granularidade, PTQ contra QAT e precisão mista. Use para: situar um método na família mais ampla antes de ler o artigo do próprio método.
- [Artigo científico: "Quantization and Training of Neural Networks for Efficient Integer-Arithmetic-Only Inference", Jacob et al., 2017](https://arxiv.org/abs/1712.05877)
  O esquema de inferência somente com inteiros por trás da maioria dos deployments em int8: o mapeamento afim com um zero exatamente representável e o treinamento com quantização simulada. Use para: de onde vem a convenção de scale e zero-point.

### Formatos numéricos

- [Artigo científico: "Mixed Precision Training", Micikevicius et al., 2017](https://arxiv.org/abs/1710.03740)
  Treinar em fp16 com uma cópia master em fp32 e loss scaling, e por que a faixa estreita do fp16 torna o scaling necessário. Use para: o que os cinco bits de expoente do fp16 custam.
- [Artigo científico: "A Study of BFLOAT16 for Deep Learning Training", Kalamkar et al., 2019](https://arxiv.org/abs/1905.12322)
  O argumento a favor do bf16, que mantém o expoente do fp32 e descarta bits de mantissa. Use para: por que a faixa importou mais do que a precisão no treinamento.
- [Artigo científico: "FP8 Formats for Deep Learning", Micikevicius et al., 2022](https://arxiv.org/abs/2209.05433)
  As codificações de ponto flutuante de oito bits E4M3 e E5M2, os seus valores especiais e os resultados de treinar e inferir com elas. Use para: para que serve cada variante de fp8.
- [Artigo científico: "Microscaling Data Formats for Deep Learning", Rouhani et al., 2023](https://arxiv.org/abs/2310.10537)
  Formatos com escala por bloco em que um bloco de elementos estreitos compartilha uma scale que é potência de dois, a base dos formatos MX da OCP. Use para: como o MXFP4 e os seus parentes armazenam um bloco.
- [Artigo: "Introducing NVFP4 for Efficient and Accurate Low-Precision Inference", NVIDIA Technical Blog](https://developer.nvidia.com/blog/introducing-nvfp4-for-efficient-and-accurate-low-precision-inference/)
  O formato de ponto flutuante de 4 bits de um fornecedor, com um bloco menor e uma scale mais fina do que as do MXFP4. Use para: como o NVFP4 difere do MXFP4, lido como documentação de fornecedor.

### Outliers

- [Artigo científico: "LLM.int8(): 8-bit Matrix Multiplication for Transformers at Scale", Dettmers et al., 2022](https://arxiv.org/abs/2208.07339)
  Descobre as dimensões de feature outlier que quebram o int8 em transformers grandes e as mantém em 16 bits com uma decomposição em precisão mista. Use para: onde os outliers aparecem e a primeira correção.
- [Artigo científico: "Massive Activations in Large Language Models", Sun et al., 2024](https://arxiv.org/abs/2402.17762)
  Ativações isoladas ordens de grandeza maiores do que o resto, em dimensões fixas e em tokens específicos, agindo como biases aprendidos. Use para: o segundo padrão de outlier e por que ele não é ruído.
- [Artigo científico: "Quantizable Transformers: Removing Outliers by Helping Attention Heads Do Nothing", Bondarenko et al., 2023](https://arxiv.org/abs/2306.12929)
  Liga os outliers a cabeças de atenção que aprendem a não fazer nada e os remove com uma mudança de arquitetura durante o treinamento. Use para: por que os outliers existem, afinal.

### Quantização pós-treinamento

- [Artigo científico: "The case for 4-bit precision: k-bit Inference Scaling Laws", Dettmers e Zettlemoyer, 2022](https://arxiv.org/abs/2212.09720)
  Mais de 35.000 experimentos zero-shot entre larguras em bits, tipos de dados e tamanhos de bloco, concluindo que 4 bits é quase universalmente o ótimo para um número fixo de bits do modelo, ajudado apenas por blocos pequenos e pela escolha do tipo de dado. Use para: por que os pesos de 4 bits se tornaram o padrão e o que o tamanho do bloco oferece.
- [Artigo científico: "Up or Down? Adaptive Rounding for Post-Training Quantization", Nagel et al., 2020](https://arxiv.org/abs/2004.10568)
  Mostra que arredondar cada peso para o seu nível mais próximo não é ótimo para a saída da camada e, em vez disso, aprende a direção do arredondamento. Use para: por que o round-to-nearest deixa acurácia para trás.
- [Artigo científico: "Optimal Brain Compression", Frantar e Alistarh, 2022](https://arxiv.org/abs/2208.11580)
  O método exato de quantização camada a camada que o GPTQ torna rápido, com a atualização que gasta o erro de um peso nos demais. Use para: a linhagem do GPTQ.
- [Artigo científico: "GPTQ: Accurate Post-Training Quantization for Generative Pre-trained Transformers", Frantar et al., 2022](https://arxiv.org/abs/2210.17323)
  Quantização de pesos one-shot em 3 e 4 bits usando informação aproximada de segunda ordem, na escala de modelos de 175B de parâmetros. Use para: como o GPTQ funciona e o que é o seu calibration set.
- [Artigo científico: "AWQ: Activation-aware Weight Quantization for LLM Compression and Acceleration", Lin et al., 2023](https://arxiv.org/abs/2306.00978)
  Descobre que uma pequena fração dos canais de pesos importa mais, identificada pela magnitude da ativação, e os protege por scaling por canal em vez de precisão mista. Use para: como o AWQ funciona e por que ele não precisa de backpropagation.
- [Artigo científico: "SmoothQuant: Accurate and Efficient Post-Training Quantization for Large Language Models", Xiao et al., 2022](https://arxiv.org/abs/2211.10438)
  Migra os outliers de ativação para os pesos com uma scale por canal matematicamente equivalente, viabilizando o W8A8. Use para: quantização de pesos e ativações em 8 bits.
- [Artigo científico: "QuaRot: Outlier-Free 4-Bit Inference in Rotated LLMs", Ashkboos et al., 2024](https://arxiv.org/abs/2404.00456)
  Rotaciona os hidden states com transformadas de Hadamard para que pesos, ativações e o KV cache quantizem todos para 4 bits. Use para: como as rotações removem outliers.
- [Artigo científico: "SpinQuant: LLM Quantization with Learned Rotations", Liu et al., 2024](https://arxiv.org/abs/2405.16406)
  Aprende as matrizes de rotação em vez de fixá-las e mostra que rotações aleatórias variam muito em qualidade. Use para: por que a escolha da rotação importa.
- [Artigo científico: "KIVI: A Tuning-Free Asymmetric 2bit Quantization for KV Cache", Liu et al., 2024](https://arxiv.org/abs/2402.02750)
  Descobre que as keys devem ser quantizadas por canal e os values por token, e faz as duas coisas em 2 bits. Use para: a escolha do eixo na quantização do KV cache.
- [Artigo científico: "KVQuant: Towards 10 Million Context Length LLM Inference with KV Cache Quantization", Hooper et al., 2024](https://arxiv.org/abs/2401.18079)
  Quantização das keys por canal antes do rotary embedding, tipos não uniformes e tratamento de outliers para contextos muito longos. Use para: o que a quantização do KV cache oferece em contexto longo.
- [Repositório: gptq, IST-DASLab](https://github.com/IST-DASLab/gptq)
  A implementação de referência dos autores do GPTQ, cujo README documenta `--act-order` (quantizar as colunas em ordem decrescente de tamanho da ativação), `--true-sequential` e `--static-groups`. Use para: o act-order e o tensor `g_idx`, que o artigo não descreve.

### Treinamento ciente de quantização

- [Artigo científico: "Estimating or Propagating Gradients Through Stochastic Neurons for Conditional Computation", Bengio et al., 2013](https://arxiv.org/abs/1308.3432)
  Apresenta e compara estimadores de gradientes através de limiares rígidos, incluindo o straight-through estimator. Use para: de onde vem o STE.
- [Artigo científico: "LLM-QAT: Data-Free Quantization Aware Training for Large Language Models", Liu et al., 2023](https://arxiv.org/abs/2305.17888)
  QAT em LLMs com dados que o próprio modelo gera, incluindo quantização do KV cache, comparado com a PTQ em 4 bits. Use para: o que o QAT recupera em um LLM e a que custo.
- [Artigo científico: "QLoRA: Efficient Finetuning of Quantized LLMs", Dettmers et al., 2023](https://arxiv.org/abs/2305.14314)
  NF4, dupla quantização e treinamento de adapters através de um base congelado de 4 bits. Use para: a fronteira com o QAT e a fonte a partir da qual a trilha de finetuning ensina.
- [Artigo: "Quantization-Aware Training for Large Language Models with PyTorch", PyTorch Blog, 2024](https://pytorch.org/blog/quantization-aware-training/)
  O fluxo de QAT do torchao no Llama 2 e no Llama 3, com a recuperação medida contra a PTQ e o overhead de fine-tuning da quantização fake. Use para: o que o QAT recupera e custa em um LLM real, lido como medições de uma equipe.

### Hardware e serving

- [Artigo científico: "MARLIN: Mixed-Precision Auto-Regressive Parallel Inference on Large Language Models", Frantar et al., 2024](https://arxiv.org/abs/2408.11743)
  Um kernel de GPU com pesos de 4 bits e ativações de 16 bits e uma análise de quando a quantização somente de pesos acelera o decode em batch. Use para: por que o ganho de velocidade depende do batch size.
- [Artigo científico: "QServe: W4A8KV4 Quantization and System Co-design for Efficient LLM Serving", Lin et al., 2024](https://arxiv.org/abs/2405.04532)
  Mostra que o overhead de dequantização pode apagar o ganho dos esquemas de 4 bits em GPUs e projeta em conjunto um formato e um kernel para evitá-lo. Use para: por que menos bits não é automaticamente mais rápido.
- [Docs: "Quantization", vLLM](https://docs.vllm.ai/en/latest/features/quantization/)
  Os esquemas que um motor de serving suporta e em qual hardware. Use para: conferir se um esquema tem um kernel antes de escolhê-lo.
- [Docs: "Quantized KV Cache", vLLM](https://docs.vllm.ai/en/latest/features/quantization/quantized_kvcache/)
  O KV cache em fp8: scales por tensor ou por head, scales padrão sem calibração e a sua calibração com o llm-compressor. Use para: o que um KV cache de 8 bits exige na prática.
- [Docs: "Quantization overview", Hugging Face Transformers](https://huggingface.co/docs/transformers/main/en/quantization/overview)
  Os backends de quantização que o Transformers integra e como escolher entre eles. Use para: um mapa das ferramentas.
- [Repositório: llm-compressor, vLLM project](https://github.com/vllm-project/llm-compressor)
  Uma biblioteca que aplica receitas de GPTQ, AWQ, SmoothQuant e FP8 e escreve checkpoints que o vLLM carrega. Use para: rodar a PTQ de ponta a ponta em um modelo real.
- [Repositório: compressed-tensors, Neural Magic](https://github.com/neuralmagic/compressed-tensors)
  A extensão do safetensors que registra o esquema de quantização de um checkpoint na sua configuração. Use para: o que um checkpoint quantizado em safetensors armazena.
- [Docs: "int8 W8A8" example, llm-compressor](https://github.com/vllm-project/llm-compressor/blob/main/examples/quantization_w8a8_int8/README.md)
  Uma receita W8A8 int8 completa: SmoothQuant, depois GPTQ com scales de pesos por canal, depois scales de ativação dinâmicas por token. Use para: rodar o SmoothQuant em um modelo real.
- [Docs: "Choosing a dataset", LLM Compressor](https://docs.vllm.ai/projects/llm-compressor/en/latest/steps/choosing-dataset/)
  Quais algoritmos precisam de um calibration set, como casar o domínio dele com o uso-alvo e quais são os tamanhos típicos. Use para: orientação prática sobre um calibration set.
- [Docs: "GPTQ", Hugging Face Transformers](https://huggingface.co/docs/transformers/main/en/quantization/gptq)
  Rodar o GPTQ por meio do `GPTQConfig` com um dataset embutido ou com o seu próprio texto. Use para: quantizar com GPTQ a partir do Transformers.
- [Docs: "AWQ", Hugging Face Transformers](https://huggingface.co/docs/transformers/main/en/quantization/awq)
  Carregar checkpoints AWQ e as chaves de `quantization_config` que um checkpoint AWQ registra. Use para: ler a configuração de um checkpoint AWQ.
- [Docs: "bitsandbytes", Hugging Face Transformers](https://huggingface.co/docs/transformers/main/en/quantization/bitsandbytes)
  Como o Transformers carrega modelos bitsandbytes de 8 e 4 bits, incluindo o tipo de dado de compute. Use para: ver que pesos de 4 bits armazenados são calculados em uma precisão maior.
- [Docs: "NVIDIA A100 Tensor Core GPU" datasheet, NVIDIA](https://www.nvidia.com/content/dam/en-zz/Solutions/Data-Center/a100/pdf/nvidia-a100-datasheet-nvidia-us-2188504-web.pdf)
  A vazão dos tensor cores da A100 por formato e a sua largura de banda de memória. Use para: os números da Ampere em um roofline, lidos como documentação de fornecedor.
- [Docs: "NVIDIA Ada GPU Architecture" whitepaper, NVIDIA](https://images.nvidia.com/aem-dam/Solutions/Data-Center/l4/nvidia-ada-gpu-architecture-whitepaper-v2.1.pdf)
  Os tensor cores da Ada e o seu suporte a FP8. Use para: quais GPUs de inferência têm tensor cores com FP8, lido como documentação de fornecedor.
- [Docs: "NVIDIA H100 Tensor Core GPU", NVIDIA](https://www.nvidia.com/en-us/data-center/h100/)
  A tabela de especificações da H100, com linhas de tensor cores FP8 e INT8 e a largura de banda de memória. Use para: os números da Hopper, lidos como documentação de fornecedor.
- [Artigo: "NVIDIA Hopper Architecture In-Depth", NVIDIA Technical Blog](https://developer.nvidia.com/blog/nvidia-hopper-architecture-in-depth/)
  Os tensor cores FP8 e o Transformer Engine introduzidos com a Hopper. Use para: quando o compute em FP8 chegou às GPUs de data center da NVIDIA, lido como documentação de fornecedor.

### Formatos de arquivo

- [Docs: "Safetensors", Hugging Face](https://huggingface.co/docs/safetensors/index)
  O formato de arquivo de tensores em que a maioria dos checkpoints é distribuída, e o que ele armazena e não armazena. Use para: o contêiner ao lado do qual fica uma configuração de quantização.
- [Docs: "GGUF", Hugging Face Hub](https://huggingface.co/docs/hub/gguf)
  Uma visão geral do formato GGUF e uma tabela dos seus tipos de quantização com os respectivos layouts de bits. Use para: decodificar o nome de um tipo GGUF.
- [Docs: llama.cpp quantize tool README, ggml-org](https://github.com/ggml-org/llama.cpp/blob/master/tools/quantize/README.md)
  Como o llama.cpp converte um modelo para os seus tipos de quant, a lista de tipos e como a matriz de importância é passada. Use para: produzir você mesmo uma quantização GGUF.
- [Repositório: safetensors, Hugging Face](https://github.com/huggingface/safetensors)
  O formato em nível de byte: um tamanho de cabeçalho de 8 bytes little-endian, um cabeçalho JSON com nomes, dtypes, shapes e offsets, e depois os dados. Use para: ler o cabeçalho de um checkpoint sem carregar os seus tensores.
- [Docs: "compressed-tensors", Hugging Face Transformers](https://huggingface.co/docs/transformers/main/en/quantization/compressed_tensors)
  Carregar checkpoints compressed-tensors, com um exemplo de `config_groups` em FP8 e a sua listagem de tensores. Use para: ler uma configuração compressed-tensors e os seus tensores de scale.
- [Model card: "TinyLlama-1.1B-Chat-v1.0-GPTQ", TheBloke](https://huggingface.co/TheBloke/TinyLlama-1.1B-Chat-v1.0-GPTQ)
  Um pequeno checkpoint público GPTQ de 4 bits cujo card explica bits, tamanho de grupo, act order e damping. Use para: um checkpoint real para inspecionar.
- [Código-fonte: ggml-common.h, ggml-org](https://github.com/ggml-org/llama.cpp/blob/master/ggml/src/ggml-common.h)
  A struct em C de cada tipo de bloco do GGUF. Use para: derivar os bits por peso de um tipo a partir do seu layout em vez de citá-los.
- [Pull request: "k-quants", ikawrakow, llama.cpp, 2023](https://github.com/ggml-org/llama.cpp/pull/1684)
  Introduz as k-quants, a nomenclatura type-0 e type-1 e as misturas S, M e L originais. Use para: o que os sufixos significavam quando foram introduzidos.
- [Pull request: "Importance Matrix calculation", ikawrakow, llama.cpp, 2024](https://github.com/ggml-org/llama.cpp/pull/4861)
  Deriva a matriz de importância a partir das ativações em um texto de calibração e a usa para ponderar o erro de arredondamento. Use para: por que uma matriz de importância é um calibration set.
- [Docs: llama.cpp imatrix tool README, ggml-org](https://github.com/ggml-org/llama.cpp/blob/master/tools/imatrix/README.md)
  Como calcular uma matriz de importância e passá-la à ferramenta de quantize. Use para: produzir uma você mesmo.

### Medindo a perda de qualidade

- [Artigo científico: "Accuracy is Not All You Need", Dutta et al., 2024](https://arxiv.org/abs/2407.09141)
  Mostra que um modelo quantizado pode igualar a acurácia do seu baseline enquanto muda muitas respostas individuais, e propõe flips e divergência KL como métricas de distância. Use para: por que uma média inalterada pode esconder um modelo alterado.
- [Artigo científico: "Give Me BF16 or Give Me Death? Accuracy-Performance Trade-Offs in LLM Quantization", Kurtic et al., 2024](https://arxiv.org/abs/2411.02355)
  Mais de meio milhão de avaliações de esquemas FP8, INT8 e INT4 entre tamanhos e tarefas do Llama 3.1, com orientação de deployment por esquema. Use para: o que cada esquema custa, medido com cuidado.
- [Artigo científico: "Scaling Laws for Precision", Kumar et al., 2024](https://arxiv.org/abs/2411.04330)
  Conclui que a quantização pós-treinamento degrada um modelo tanto mais quanto mais dados ele recebeu no treinamento. Use para: por que a resposta usual de 4 bits pode falhar em um modelo muito treinado.
- [Repositório: lm-evaluation-harness, EleutherAI](https://github.com/EleutherAI/lm-evaluation-harness)
  O harness com o qual a maioria dos artigos de quantização reporta a acurácia nas tarefas. Use para: rodar as mesmas tarefas em um baseline e em um modelo quantizado.
- [Docs: "Perplexity of fixed-length models", Hugging Face Transformers](https://huggingface.co/docs/transformers/main/en/perplexity)
  Como a perplexity é calculada com uma janela deslizante e por que a janela muda o número. Use para: calcular a perplexity de modo que duas execuções sejam comparáveis.
- [Artigo científico: "Quantization Hurts Reasoning? An Empirical Study on Quantized Reasoning Models", Liu et al., 2025](https://arxiv.org/abs/2504.04823)
  Modelos de raciocínio quantizados com quantização de pesos, do KV cache e de ativações em benchmarks de matemática, ciência e código, concluindo que W8A8 e W4A16 podem ser sem perdas e que larguras em bits menores são arriscadas. Use para: se a resposta usual de 4 bits vale para um modelo de raciocínio.
- [Docs: llama.cpp perplexity tool README, ggml-org](https://github.com/ggml-org/llama.cpp/blob/master/tools/perplexity/README.md)
  Estatísticas de perplexity, divergência KL e concordância do token principal contra logits de 16 bits, com uma tabela de tipos GGUF. Use para: medir um GGUF quantizado contra o seu baseline além da perplexity.

## Lacunas

- Não há uma única tabela atual e neutra em relação a fornecedores de quais gerações de GPU calculam nativamente em quais formatos. A lição 20 se apoia em páginas de fornecedores e em matrizes de suporte de motores de serving, que mudam a cada release.
