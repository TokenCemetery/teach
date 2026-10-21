---
title: "Recursos"
description: "Fontes confiáveis sobre inferência"
type: resources
---

# Recursos de Inferência

## Conhecimento

- [Documentação: vLLM Documentation, vLLM Project](https://docs.vllm.ai/en/latest/)
  Documentação oficial da stack de serving em GPU que este workspace monta primeiro: instalação, serve e as configurações de batching e de memória do engine. Use para: como rodar e configurar o próprio vLLM.
- [Artigo científico: "Efficient Memory Management for Large Language Model Serving with PagedAttention", Kwon et al., SOSP 2023](https://arxiv.org/abs/2309.06180)
  O artigo do PagedAttention: por que o KV cache fragmenta os alocadores de memória comuns e como paginá-lo resolve isso, com os números de throughput que motivam o design do vLLM. Use para: entender o que o KV cache custa e por que o gerenciador de memória do vLLM existe.
- [Repositório: llama.cpp, ggml-org](https://github.com/ggml-org/llama.cpp)
  Repositório oficial da stack de serving para CPU/edge que este workspace monta em segundo lugar: instruções de build, formatos de quantização suportados (GGUF) e as flags do binário do servidor. Use para: como rodar e configurar o próprio llama.cpp.
- [Pull request: "k-quants", ikawrakow, llama.cpp, 2023](https://github.com/ggml-org/llama.cpp/pull/1684)
  Introduz os tipos k-quant, o seu layout de super-blocos e as receitas `S`, `M` e `L` que misturam tipos entre tensores. Use para: o que um nome GGUF como `Q4_K_M` realmente armazena.
- [Artigo científico: "GPTQ: Accurate Post-Training Quantization for Generative Pre-trained Transformers", Frantar et al., 2023](https://arxiv.org/abs/2210.17323)
  Quantização de pesos pós-treinamento em uma só passada, até 3 a 4 bits, com um custo de acurácia medido. Use para: o que quantizar um modelo para serving realmente sacrifica, e como o trade-off é medido.
  Leia antes o [guia do transformers](https://huggingface.co/docs/transformers/main/en/llm_optims) abaixo se a álgebra linear daqui for o ponto de dificuldade.
- [Documentação: "Optimizing inference", Hugging Face Transformers](https://huggingface.co/docs/transformers/main/en/llm_optims)
  Passo a passo em nível de praticante do KV cache, do batching estático vs dinâmico e dos backends de quantização, sem exigir antes a matemática dos artigos. Use para: um modelo mental funcional antes das fontes primárias acima.
- [Artigo: "Transformer Inference Arithmetic", Kipply](https://kipp.ly/transformer-inference-arithmetic/)
  Deriva a aritmética real de FLOPs e de largura de banda de memória por trás de uma passada forward, incluindo de onde vem o custo de memória do KV cache. Use para: calcular um orçamento de latência ou de memória a partir dos primeiros princípios em vez de citar um benchmark.
- [Artigo: "How continuous batching enables 23x throughput in LLM inference while reducing p50 latency", Anyscale](https://www.anyscale.com/blog/continuous-batching-llm-inference)
  Escrito por engenheiros que construíram o continuous batching em um dos primeiros engines de serving; explica por que o batching estático desperdiça tempo de GPU em um fluxo de requisições de comprimentos mistos e como o continuous batching resolve isso. Use para: a metade de batching do trade-off entre latência e throughput que este workspace defende.

- [Artigo científico: "Fast Inference from Transformers via Speculative Decoding", Leviathan et al., 2022](https://arxiv.org/abs/2211.17192)
  Introduz a speculative decoding: um modelo pequeno redige vários tokens, o modelo grande os verifica todos em uma única passada paralela, com um método de amostragem que garante exatamente a mesma distribuição de saída que rodar apenas o modelo grande. Use para: por que isso é uma alavanca pura de latência e não um trade-off de qualidade, e o argumento de largura de banda de memória para a verificação paralela ser quase gratuita.
- [Artigo científico: "Medusa: Simple LLM Inference Acceleration Framework with Multiple Decoding Heads", Cai et al., 2024](https://arxiv.org/abs/2401.10774)
  Substitui o modelo draft separado da speculative decoding por cabeças de decodificação extras adicionadas diretamente ao modelo alvo. Use para: resolver o ônus operacional de manter um segundo modelo, mantendo a mesma garantia de verificar e corrigir.
- [Artigo científico: "EAGLE: Speculative Sampling Requires Rethinking Feature Uncertainty", Li et al., 2024](https://arxiv.org/abs/2401.15077)
  Redige no nível das features internas do modelo em vez de tokens brutos, resolvendo a incerteza da predição no nível de feature ao incorporar uma sequência de tokens um passo à frente. Use para: um refinamento adicional sobre o Medusa, com um speedup reportado maior, ainda preservando a distribuição de saída do modelo alvo.
- [Artigo científico: "Efficient Guided Generation for Large Language Models" (Outlines), Willard e Louf, 2023](https://arxiv.org/abs/2307.09702)
  Reformula a geração restrita como transições entre estados de uma máquina de estados finitos, permitindo que um índice do vocabulário seja pré-computado uma vez por gramática e reutilizado como uma consulta rápida por token. Use para: por que a decodificação restrita por gramática ou por schema acrescenta pouco overhead por token e garante a estrutura da saída por construção e não por esperança.
- [Documentação: "Automatic Prefix Caching", vLLM Project](https://docs.vllm.ai/en/latest/features/automatic_prefix_caching.html)
  A documentação do próprio vLLM sobre reutilizar o KV cache de um prefixo compartilhado entre requisições que, fora isso, não têm relação entre si, os seus dois exemplos de carga de trabalho nomeados (QA sobre documento longo, conversa de várias rodadas) e o seu limite declarado (acelera só o prefill, nunca o decode). Use para: o prefix caching como o mecanismo de compartilhamento de blocos do PagedAttention estendido entre requisições.
- [Artigo científico: "Megatron-LM: Training Multi-Billion Parameter Language Models Using Model Parallelism", Shoeybi et al., 2019](https://arxiv.org/abs/1909.08053)
  O artigo canônico do paralelismo de tensor: um esquema de paralelismo de modelo intra-camada que divide as multiplicações de matrizes de uma camada do transformer entre GPUs, precisando de apenas algumas operações de comunicação, e explicitamente ortogonal e complementar ao paralelismo de pipeline. Use para: o que `--tensor-parallel-size` (lição 12) realmente faz dentro de uma camada.
- [Artigo científico: "GPipe: Efficient Training of Giant Neural Networks using Pipeline Parallelism", Huang et al., 2018](https://arxiv.org/abs/1811.06965)
  O artigo canônico do paralelismo de pipeline: particiona qualquer rede expressável como uma sequência de camadas em grupos consecutivos colocados em aceleradores separados, e introduz o micro-batching para reduzir (e não eliminar) a bolha de pipeline resultante. Use para: a divisão alternativa ao paralelismo de tensor, e por que ela tolera um link entre dispositivos mais lento.
- [Documentação: "Welcome to production-stack" e guias de casos de uso, vLLM Production Stack](https://docs.vllm.ai/projects/production-stack)
  Documentação oficial do deployment de frota de referência do vLLM, nativo de Kubernetes: roteamento de requisições ciente do KV cache e autoscaling baseado em KEDA a partir de métricas de profundidade de fila como `vllm:num_requests_waiting`. Use para: como roteamento e autoscaling realmente funcionam em escala de frota, além de um único servidor.
- [Artigo científico: "ServerlessLLM: Low-Latency Serverless Inference for Large Language Models", Fu et al., OSDI 2024](https://arxiv.org/abs/2401.14351)
  Mede por que os cold starts de LLMs são severos (o tempo de carga do checkpoint supera de longe o tempo de geração por token, dezenas de segundos em traces de produção) e resolve isso com carga de checkpoint em várias camadas, perto da GPU. Use para: por que adicionar uma réplica à frota não é instantâneo, e o que realmente limita a rapidez com que ela se torna útil.
- [Documentação: "Metrics", vLLM Project](https://docs.vllm.ai/en/stable/design/metrics/)
  A lista do próprio vLLM de métricas Prometheus exportadas: TTFT, latência entre tokens, latência de ponta a ponta e histogramas separados de tempo de prefill e de decode. Use para: o que um servidor de produção realmente exporta de forma contínua, em oposição a um benchmark pontual.
- [Google SRE Workbook: "Implementing SLOs"](https://sre.google/workbook/implementing-slos/)
  O enquadramento canônico de SRE para SLIs, SLOs e orçamentos de erro: uma razão relevante para o usuário, uma meta declarada para ela e a tolerância a descumprir essa meta derivada diretamente do SLO. Use para: transformar uma métrica bruta exportada em uma meta de produção acionável.
- [Artigo científico: "YaRN: Efficient Context Window Extension of Large Language Models", Peng et al., ICLR 2024](https://arxiv.org/abs/2309.00071)
  Estende o comprimento de contexto utilizável de um modelo além do comprimento em que foi treinado, reescalando de forma não uniforme as dimensões de frequência do RoPE, a uma fração do custo de fine-tuning dos métodos anteriores. Use para: por que o RoPE scaling muda o comprimento máximo de contexto sem tocar no crescimento do próprio KV cache.
- [Artigo científico: "Mistral 7B", Jiang et al., 2023](https://arxiv.org/abs/2310.06825)
  Introduz a atenção de janela deslizante e o seu cache em buffer rotativo associado: cada token atende no máximo a uma janela fixa de tokens anteriores, limitando o tamanho do cache independentemente do comprimento da sequência. Use para: o mecanismo que transforma o crescimento linear do cache da lição 2 em uma constante.
- [Artigo científico: "Efficient Streaming Language Models with Attention Sinks", Xiao et al., ICLR 2024](https://arxiv.org/abs/2309.17453)
  Identifica o fenômeno do attention sink por trás de a atenção de janela deslizante simples colapsar quando tokens antigos são descartados, e o corrige mantendo permanentemente as entradas de KV de um punhado de tokens iniciais. Use para: por que um cache limitado ainda pode atender um fluxo efetivamente ilimitado.

## Lacunas

- Ainda não há fonte sobre serving com consciência de quantização especificamente para os formatos GGUF do llama.cpp (em oposição a GPTQ/AWQ, que miram stacks de GPU); a missão precisa de uma comparação de quantização específica para CPU/edge quando o desenho das lições chegar a essa etapa.
