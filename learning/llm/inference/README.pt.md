---
title: "Inferência"
description: "Sirva um modelo: o KV cache, o batching, a quantização no serving e um orçamento de latência que você consegue defender"
type: topic
---

# Aprendizado: Inferência

Seja capaz de montar um servidor de inferência para um modelo real, primeiro em GPU e depois em CPU/edge, e de defender os números de latência e throughput que ele produz, em vez de citar o que os defaults do framework acabam dando.

**Última lição:** [25. Revisando uma configuração de serving](lessons/0025-reviewing-a-serving-configuration.md)

## O sucesso se parece com isto

- Montar uma stack de serving (vLLM em GPU, depois llama.cpp em CPU/edge) para um dado modelo e fazê-la responder a requisições.
- Citar um orçamento de latência p99 para um dado batch size e modelo, e defender o número a partir das escolhas de KV cache, batching e quantização que o produziram.
- Revisar a configuração de serving de outra pessoa e dizer especificamente o que ela custa (um parâmetro mal ajustado em relação ao gargalo da carga de trabalho declarada, uma topologia escolhida sem um gargalo que a justifique, um rollout que quebra um chamador no meio do caminho), em vez de dizer que algo parece errado.

## Restrições

- Pressupõe conforto em rodar um ambiente Python de ML e familiaridade básica com o que é um modelo de linguagem; não exige experiência prévia com infraestrutura de serving.
- Stacks principais: vLLM (GPU) e llama.cpp (CPU/edge), vistas nessa ordem. Outras stacks (TGI, TensorRT-LLM) só são mencionadas onde um conceito se transfere de outra forma.

## Fora do escopo

- Treinar ou fazer fine-tuning de um modelo ou adapter: veja [`llm/finetuning`](../../llm/finetuning/) (lições 0025, servindo adapters, e 0026, custo, latência e throughput), com link para lá em vez de repetir o conteúdo.
- Julgar a qualidade da saída ou construir um eval para um modelo servido: veja [`llm/evals`](../../llm/evals/) para essa fronteira.
- Como os métodos de quantização funcionam e como julgá-los, dos formatos numéricos e do mapeamento afim até GPTQ, AWQ, SmoothQuant, QAT e a medição da perda de qualidade: veja [`llm/quantization`](../../llm/quantization/). A etapa 3 aqui mantém a decisão de serving, escolher um esquema para um orçamento de latência, e aponta para lá para os fundamentos; essa fronteira foi definida quando a trilha de quantização foi escrita.
- Pedir saída estruturada pelo lado do prompt: veja [`llm/prompting`](../../llm/prompting/). Esta trilha é dona da decodificação restrita, o lado do serving do mesmo objetivo.

## O arco

Quatorze etapas, da primeira requisição até uma configuração de serving defendida, em escala de frota, monitorada em produção e revisada. Uma etapa leva várias lições e as fronteiras são flexíveis; o que torna uma etapa concluída é a capacidade, não a contagem de lições.

| Etapa | Lições | Cobre | Concluída quando |
|---|---|---|---|
| 1. O KV cache | 0001 a 0003 | Por que a geração autorregressiva é cara, o que o cache troca por memória, como o tamanho do cache cresce com o contexto e o batch | Consegue calcular a pegada de memória do KV cache de um modelo para um dado comprimento de contexto e batch size |
| 2. Batching | 0004 a 0006 | Batching estático vs contínuo, scheduling de requisições, o trade-off entre throughput e latência | Consegue defender uma configuração de batching para uma carga de trabalho declarada |
| 3. Quantização no serving | 0007 a 0009 | int8/int4/AWQ/GPTQ no momento da inferência, acurácia vs velocidade vs memória | Consegue escolher um esquema de quantização para o serving e defender o trade-off |
| 4. vLLM na prática | 0010 a 0012 | Colocar o vLLM no ar, PagedAttention, os parâmetros de ajuste que importam | Uma stack vLLM está rodando e respondendo a requisições reais |
| 5. llama.cpp em CPU/edge | 0013 a 0015 | GGUF, a arquitetura do llama.cpp, o que muda fora da GPU | Uma stack llama.cpp está rodando em CPU e respondendo a requisições reais |
| 6. O orçamento de latência | 0016 a 0017 | Metodologia de medição de p99, ligar o número de volta às escolhas de cache, batching e quantização | Consegue citar e defender um orçamento de latência p99 de ponta a ponta |
| 7. Speculative decoding | 0018 | Speculative decoding com modelo draft, n-gram, Medusa e EAGLE | Consegue explicar por que a verificação paralela é quase gratuita e escolher uma variante de speculative decoding para uma carga de trabalho |
| 8. Amostragem e decodificação restrita no serving | 0019 | Parâmetros de amostragem por requisição em um batch compartilhado, decodificação restrita indexada por FSM | Consegue explicar por que a garantia da decodificação restrita é estrutural e por que o seu custo por token continua pequeno |
| 9. Prefix caching | 0020 | O prefix caching automático como compartilhamento de blocos entre requisições, cargas de documentos longos e de vários turnos, o seu limite de só acelerar o prefill | Consegue explicar quando o prefix caching ajuda uma carga de trabalho e por que ele nunca acelera o decode |
| 10. Paralelismo multi-GPU e multi-nó | 0021 | O mecanismo real do paralelismo de tensor além da flag única da lição 12, o paralelismo de pipeline e um procedimento de decisão sobre qual deles (ou os dois) um deployment precisa | Consegue explicar o que um passo de combinação do paralelismo de tensor e uma bolha de pipeline custam, cada um, e escolher a divisão certa para uma dada interconexão e um dado número de nós |
| 11. Serving no nível da frota | 0022 | Roteamento informado pela localidade do cache, autoscaling guiado pela profundidade da fila e por que o tempo de carga do modelo em um cold start limita a rapidez com que uma nova réplica realmente ajuda | Consegue explicar como roteamento, autoscaling e latência de cold start precisam ser pensados como um só pipeline e não ajustados separadamente |
| 12. Observabilidade e custo em produção | 0023 | Métricas exportadas continuamente, SLIs/SLOs/orçamentos de erro que transformam uma métrica em uma meta, e o custo por milhão de tokens derivado do throughput medido | Consegue defender uma configuração de produção citando o seu p99, o SLO e o orçamento de erro a que ela está sujeita e o seu custo por milhão de tokens |
| 13. Contexto longo no serving | 0024 | RoPE scaling versus atenção de janela deslizante e attention sinks, e o que cada um realmente faz com a fórmula de crescimento do cache da lição 2 | Consegue explicar se uma técnica de contexto longo estende o comprimento utilizável, limita o tamanho do cache a uma constante ou corrige o modo de falha de um cache limitado |
| 14. Julgamento | 0025 | Revisar a configuração de outra pessoa em busca de parâmetros incompatíveis, rollouts seguros em relação ao que outros dependem e dizer quando a speculative decoding não é uma vitória de graça | Tem confiança para revisar uma configuração de serving e dizer o que cada escolha custa, e não apenas que parece errada |

## Lições

Siga estas na ordem.

| # | Lição | Ensina |
|---|---|---|
| [0001](lessons/0001-the-kv-cache.md) | O KV cache | Por que a geração fica cara, e o que o cache devolve |
| [0002](lessons/0002-capacity-and-batch-size.md) | Capacidade e batch size | Como o compartilhamento de heads (GQA/MQA) e o batch size mudam a pegada real do cache |
| [0003](lessons/0003-growth-prefill-decode-precision.md) | Crescimento, prefill, decode e precisão | Como o cache cresce ao longo do prefill e do decode, e o que reduzir a sua precisão devolve |
| [0004](lessons/0004-static-vs-continuous-batching.md) | Batching estático vs contínuo | Por que agrupar requisições ajuda o throughput, e por que o continuous batching supera o estático |
| [0005](lessons/0005-request-scheduling.md) | Scheduling de requisições | Como um scheduler de continuous batching escolhe a próxima requisição, e por que um prefill grande pode travar todas as outras |
| [0006](lessons/0006-throughput-latency-tradeoff.md) | O trade-off entre throughput e latência | Como o batch size troca throughput por latência por token, e como defender uma configuração de batching contra um orçamento de latência declarado |
| [0007](lessons/0007-quantization-schemes.md) | Esquemas de quantização no serving | O que int8, int4, GPTQ e AWQ realmente fazem com os pesos de um modelo, e por que a versão ingênua da quantização em poucos bits precisa de uma correção |
| [0008](lessons/0008-accuracy-speed-memory-tradeoffs.md) | Trade-offs entre acurácia, velocidade e memória | Por que memória, velocidade e acurácia não se movem juntas quando um modelo é quantizado, e como cada uma é realmente medida |
| [0009](lessons/0009-picking-a-quantization-scheme.md) | Escolhendo e defendendo um esquema de quantização | Um framework de decisão para escolher um esquema de quantização para o serving, e os três números que o defendem |
| [0010](lessons/0010-standing-up-vllm.md) | Colocando o vLLM no ar | Instalar o vLLM, iniciar o seu servidor e achar as flags que carregam os conceitos já ensinados |
| [0011](lessons/0011-pagedattention.md) | PagedAttention | O mecanismo de block table por trás do vLLM, o seu trade-off de tamanho de bloco e como ele permite que sequências compartilhem o cache de um prefixo comum |
| [0012](lessons/0012-vllm-tuning-knobs.md) | Os parâmetros de ajuste do vLLM que importam | Mais duas flags, gpu-memory-utilization e tensor-parallel-size, e um procedimento de decisão sobre qual parâmetro um sintoma realmente aponta |
| [0013](lessons/0013-gguf.md) | GGUF | O que o formato de modelo em arquivo único do llama.cpp reúne, a sua nomenclatura de quantização e por que ele pode ser mapeado em memória em vez de carregado |
| [0014](lessons/0014-llamacpp-architecture.md) | A arquitetura do llama.cpp | A biblioteca de tensores ggml por baixo do llama.cpp, a sua abstração de backends e como o threading em CPU difere do batching em GPU |
| [0015](lessons/0015-what-changes-off-gpu.md) | O que muda fora da GPU | Colocar o servidor do llama.cpp no ar, e como batching, gerenciamento de cache e quantização ficam diferentes em escala de CPU/edge |
| [0016](lessons/0016-p99-latency-methodology.md) | Metodologia de medição de latência p99 | Por que o p99 vence uma média, por que TTFT e latência entre tokens precisam de números separados e o que torna confiável uma medição de p99 |
| [0017](lessons/0017-defending-a-latency-budget-end-to-end.md) | Defendendo um orçamento de latência de ponta a ponta | Uma ordem de diagnóstico para um orçamento de p99 estourado, e as três coisas que uma configuração final defendida precisa citar |
| [0018](lessons/0018-speculative-decoding.md) | Speculative decoding | Verificar vários tokens candidatos em uma única passada forward paralela custa aproximadamente o que custa gerar um token normalmente, já que o decode é limitado por mover pesos e não pela aritmética, que é o único fato sobre o qual toda variante de speculative decoding é construída |
| [0019](lessons/0019-sampling-and-constrained-decoding-at-serve-time.md) | Amostragem e decodificação restrita no serving | Um batch contínuo já passa muitas requisições por uma única passada forward compartilhada, e dar a cada uma as suas próprias configurações de amostragem, ou forçar uma delas a produzir apenas JSON válido, precisa acontecer por linha dentro dessa mesma passada compartilhada, sem atrasar as demais |
| [0020](lessons/0020-prefix-caching.md) | Prefix caching | A lição 11 deixou amostras paralelas da mesma requisição compartilharem os blocos em cache de um prompt; o prefix caching é o mesmo compartilhamento aplicado entre requisições sem relação entre si, e ele acelera exatamente a fase que o prefill redundante desperdiça, nunca a fase que gera a resposta |
| [0021](lessons/0021-tensor-and-pipeline-parallelism.md) | Paralelismo de tensor e de pipeline | A lição 12 apresentou tensor-parallel-size como uma flag que divide um modelo entre GPUs; esta lição abre o que essa divisão realmente faz dentro de uma camada, apresenta o paralelismo de pipeline como outra divisão do mesmo problema e dá um procedimento de decisão sobre qual deles (ou os dois) uma carga de trabalho realmente precisa |
| [0022](lessons/0022-fleet-level-serving.md) | Serving no nível da frota | O scheduler da lição 5 escolhe a próxima requisição da fila de um servidor; uma frota acrescenta uma decisão antes dessa, qual servidor recebe a requisição, uma decisão sobre quando adicionar mais servidores e um custo de cold start que deixa um servidor recém-adicionado inútil por dezenas de segundos |
| [0023](lessons/0023-production-observability-and-cost.md) | Observabilidade e custo em produção | A lição 17 defendeu um único p99 medido para uma única configuração; esta lição trata do que precisa ser exportado continuamente para pegar uma regressão automaticamente, do SLO e do orçamento de erro que transformam "bom o bastante" em uma meta e não em uma impressão, e do número de custo por milhão de tokens que precisa ser defendido junto com o p99, e não no lugar dele |
| [0024](lessons/0024-long-context-at-serve-time.md) | Contexto longo no serving | A fórmula de capacidade da lição 2 cobra memória linearmente com o comprimento do contexto; o RoPE scaling estende o tamanho que um contexto pode ter sem mudar essa cobrança em nada, enquanto a atenção de janela deslizante e os attention sinks mudam a própria fórmula, limitando o comprimento do contexto a uma constante |
| [0025](lessons/0025-reviewing-a-serving-configuration.md) | Revisando uma configuração de serving | Revisar a configuração de serving de outra pessoa e dizer especificamente o que ela custa (um parâmetro mal ajustado em relação ao gargalo da carga de trabalho declarada, uma topologia escolhida sem um gargalo que a justifique, um rollout que quebra um chamador no meio do caminho), em vez de dizer que algo parece errado |

## Referência

- [Glossário](GLOSSARY.md): termos canônicos deste tópico
- [Recursos](RESOURCES.md): fontes confiáveis
- [KV cache](reference/kv-cache.md): custo por token, compartilhamento de heads, crescimento ao longo de uma requisição e planejamento de capacidade
- [Batching](reference/batching.md): batching estático vs contínuo, scheduling de requisições e o trade-off entre throughput e latência
- [Quantização no Serving](reference/quantization-at-serve-time.md): int8/int4/GPTQ/AWQ, por que memória, velocidade e acurácia não se movem juntas e um framework de decisão para escolher um esquema
- [vLLM](reference/vllm.md): colocar o vLLM no ar, PagedAttention e os parâmetros de ajuste que importam
- [llama.cpp](reference/llama-cpp.md): GGUF, a arquitetura do llama.cpp e o que muda fora da GPU
- [Orçamento de Latência](reference/latency-budget.md): metodologia de medição de p99 e ligar um orçamento estourado de volta às escolhas de cache, batching e quantização

## Como isto funciona

Cada lição é curta e autocontida. Os gabaritos ficam recolhidos: primeiro lembre, depois abra. A prática no mundo real importa mais do que a leitura, e espaçá-la é o ponto. Tudo o que ainda estiver confuso no fim de uma lição vale ser perseguido até a fonte primária antes de seguir adiante.
