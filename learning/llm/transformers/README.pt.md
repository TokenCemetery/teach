---
title: "Transformers"
description: "Construa a atenção do zero, para que a arquitetura deixe de ser uma caixa-preta por trás do script de treinamento"
type: topic
---

# Aprendizado: Transformers

Seja capaz de implementar o forward pass de um transformer e o seu loop de treinamento a partir de tensores brutos, e de ler ou modificar código real de modelos sem que a arquitetura seja uma caixa-preta por trás dele.

**Última lição:** [23. Revisando uma mudança no código de um modelo](lessons/0023-reviewing-a-change-to-model-code.md)

## O sucesso se parece com isto

- Implementar a scaled dot-product attention, a multi-head attention e um bloco transformer completo a partir de tensores brutos, batendo com a saída de uma implementação de referência.
- Escrever do zero o loop de treinamento que se encaixa ao redor desse bloco e explicar o que cada peça (loss, backward pass, passo do otimizador) está fazendo com os pesos.
- Ler o código de um modelo real (uma biblioteca como a `transformers` ou o `llama.cpp`) e apontar onde cada peça derivada vive.
- Revisar a mudança de outra pessoa no código de um modelo e nomear especificamente o que ela quebra ou custa (um bug de formato que só aparece duas camadas adiante, um ganho de velocidade alegado sem saída correspondente, uma alegação arquitetural que não sobrevive a uma releitura das equações reais do artigo), em vez de confiar na descrição do pull request.

## Restrições

- Pressupõe familiaridade com Python e com operações básicas de tensores do PyTorch, e a multiplicação de matrizes como a única matemática tomada como dada; não exige conhecimento prévio de deep learning.
- Implementação em PyTorch, usando operações com tensores brutos em vez de `nn.Transformer` ou outros módulos de atenção pré-construídos; o autograd e o suporte a GPU são mantidos, apenas a arquitetura em si é construída à mão.

## Fora do escopo

- Variantes de otimizador e de scheduler além do loop básico necessário para ver o bloco treinar, e o treinamento distribuído: veja [`llm/pretraining`](../../llm/pretraining/), que continua a partir do ponto em que este loop precisa rodar em muitas GPUs.
- O mecanismo de baixo rank/adapters construído sobre o bloco: veja [`llm/finetuning`](../../llm/finetuning/) para essa fronteira. Este workspace deriva o que aquele workspace nomeia de passagem (tokenizers na sua lição 0003, a ideia de baixo rank na sua lição 0008) em vez de reafirmá-lo.

## O arco

Doze etapas, de uma equação até ler e gerar a partir de código real de modelos em qualquer escala. Uma etapa leva várias lições e as fronteiras são flexíveis; o que torna uma etapa concluída é a capacidade, não a contagem de lições.

| Etapa | Lições | Cobre | Concluída quando |
|---|---|---|---|
| 1. Atenção | 0001 a 0003 | Scaled dot-product attention, multi-head attention, máscara causal | A multi-head attention está implementada a partir de tensores brutos, batendo com uma implementação de referência |
| 2. O bloco transformer | 0004 a 0006 | Codificação posicional, layer norm e conexões residuais, o bloco feed-forward | Um bloco transformer completo está implementado a partir de tensores brutos |
| 3. O modelo completo | 0007 a 0008 | Empilhar blocos, camadas de embedding e de saída, weight tying | Um forward pass completo bate com a saída de uma implementação de referência |
| 4. O loop de treinamento | 0009 a 0011 | Loss de cross-entropy sobre o vocabulário, o backward pass, o passo do otimizador AdamW | O modelo treina do zero e a loss diminui como esperado |
| 5. Lendo código real de modelos | 0012 a 0013 | Mapear cada peça derivada para uma biblioteca real (`transformers` ou `llama.cpp`), tokenizers e adapters de baixo rank mencionados de passagem | Consegue apontar onde cada peça derivada vive em código real de modelos |
| 6. Codificação posicional e normalização modernas | 0014 a 0015 | Rotary position embeddings, RMSNorm | Consegue derivar a propriedade de posição relativa do RoPE e explicar o que a RMSNorm abandona da layer norm |
| 7. Variantes modernas de feed-forward e de atenção | 0016 a 0017 | SwiGLU/o feed-forward com gate, grouped-query e multi-query attention, KV caching | Consegue derivar um bloco feed-forward com gate e explicar por que menos heads de KV trocam qualidade por tamanho de cache |
| 8. Geração e amostragem | 0018 | Greedy decoding, temperatura, top-k e top-p sampling, rodar o modelo para a frente para produzir texto | Consegue gerar texto a partir do modelo construído à mão e explicar por que o greedy decoding degenera |
| 9. Os detalhes práticos do loop de treinamento | 0019 a 0020 | Inicialização de Xavier, warm-up e decay da learning rate, gradient clipping, precisão mista, gradient accumulation | Consegue explicar contra o que cada detalhe prático protege e adicioná-los a um loop de treinamento funcional |
| 10. Arquiteturas encoder-decoder e encoder-only | 0021 | O encoder bidirecional do BERT, o encoder-decoder do T5 com cross-attention, situar o modelo decoder-only deste workspace | Consegue explicar por que cada arquitetura usa ou não uma máscara causal e onde a cross-attention se encaixa |
| 11. Mixture-of-experts e FlashAttention | 0022 | Roteamento MoE de ativação esparsa, tiling ciente de IO da FlashAttention | Consegue explicar como o MoE desacopla parâmetros do compute por token e por que a FlashAttention é exata, e não aproximada |
| 12. Julgamento | 0023 | Revisar mudanças de outra pessoa no código de um modelo, conferir formatos e a exatidão da saída, resolver alegações contestadas a partir da fonte primária | Tem a confiança para revisar mudanças na arquitetura do modelo e no loop de treinamento e para explicar o que uma mudança custa ou arrisca, em vez de aceitar a descrição |

## Lições

Siga estas na ordem.

| # | Lição | Ensina |
|---|---|---|
| [0001](lessons/0001-scaled-dot-product-attention.md) | Scaled Dot-Product Attention | A equação única em torno da qual o resto da arquitetura é construído |
| [0002](lessons/0002-multi-head-attention.md) | Multi-Head Attention | Por que a atenção roda em vários subespaços menores ao mesmo tempo, em vez de um só com a dimensão completa |
| [0003](lessons/0003-causal-masking.md) | Máscara causal | Por que uma posição de query não deve atender às posições futuras, e por que a máscara é aplicada antes do softmax, e não depois |
| [0004](lessons/0004-positional-encoding.md) | Codificação posicional | Por que a atenção é cega à ordem por conta própria, e como a codificação sinusoidal dá a cada posição uma assinatura distinguível |
| [0005](lessons/0005-layer-norm-and-residuals.md) | Layer Norm e conexões residuais | Por que empilhar muitos blocos transformer exige um caminho de gradiente limpo e faixas de ativação estáveis, e como as residuais e a layer norm fornecem cada um deles |
| [0006](lessons/0006-feed-forward-block.md) | O bloco feed-forward por posição | O que a segunda subcamada do bloco transformer acrescenta além da atenção, e por que ela nunca mistura informação entre posições |
| [0007](lessons/0007-stacking-blocks.md) | Empilhando blocos transformer | Por que todo bloco preserva o mesmo formato, por que profundidade não é compartilhamento de pesos e por que o mecanismo residual da lição 5 importa mais quando muitos blocos são empilhados |
| [0008](lessons/0008-embedding-output-and-weight-tying.md) | Camadas de embedding e de saída, weight tying | Como os tokens entram e saem do espaço vetorial do transformer, e por que as duas camadas que fazem isso podem compartilhar uma só matriz |
| [0009](lessons/0009-cross-entropy-loss.md) | Loss de cross-entropy sobre o vocabulário | Como os logits viram um número treinável, e por que a loss é o log de probabilidade negativo do próximo token real |
| [0010](lessons/0010-backward-pass-and-autograd.md) | O backward pass e o autograd | Como a regra da cadeia, automatizada sobre um grafo de computação registrado, transforma uma loss escalar em um gradiente para cada peso |
| [0011](lessons/0011-adamw-optimizer.md) | O passo do otimizador AdamW | O que o momento e o escalonamento adaptativo do Adam acrescentam ao gradient descent simples, e por que o AdamW desacopla o weight decay da atualização por gradiente |
| [0012](lessons/0012-reading-real-model-code.md) | Lendo código real de modelos | Onde cada peça derivada vive em uma biblioteca de modelos de produção, e os pequenos desvios comuns em relação ao artigo original que vale reconhecer em vez de se confundir com eles |
| [0013](lessons/0013-tokenizers-and-low-rank-adapters.md) | Tokenizers e adapters de baixo rank | Derivando o byte-pair encoding, e onde um adapter de baixo rank de fato se acopla a uma matriz de pesos que este workspace construiu do zero |
| [0014](lessons/0014-rotary-position-embeddings.md) | Rotary position embeddings | A codificação sinusoidal soma um vetor fixo ao embedding antes de a atenção sequer rodar; o RoPE, em vez disso, rotaciona o próprio Q e o próprio K, e essa única mudança é o que faz o produto escalar entre dois vetores rotacionados depender apenas da distância relativa entre eles |
| [0015](lessons/0015-rmsnorm.md) | RMSNorm | A LayerNorm faz duas coisas, recentralizar e reescalar, e a RMSNorm existe porque a metade de recentralização se mostra dispensável, deixando uma normalização mais barata que os modelos atuais usam dentro do ramo pre-norm que a lição 5 já derivou |
| [0016](lessons/0016-swiglu-and-the-gated-feed-forward.md) | SwiGLU e o bloco feed-forward com gate | O bloco feed-forward da lição 6 expande, aplica uma não linearidade e contrai; uma variante com gate calcula duas projeções em vez de uma e as multiplica, permitindo que a rede aprenda quanto da sua própria computação deixar passar |
| [0017](lessons/0017-grouped-query-attention-and-kv-caching.md) | Grouped-query attention e KV caching | A geração autorregressiva faz a atenção recalcular keys e values que ela já tem, e, uma vez que armazená-los em cache se torna a correção óbvia, o próprio tamanho do cache é o que faz valer a pena trocar uma pequena quantidade de qualidade por menos heads de key/value |
| [0018](lessons/0018-generation-and-sampling.md) | Geração e amostragem | O modelo que este workspace construiu e treinou nunca produziu texto, porque o treinamento e a geração lhe fazem duas perguntas diferentes, e sempre pegar o único próximo token mais provável se revela uma resposta pior à segunda pergunta do que uma quantidade bem escolhida de aleatoriedade |
| [0019](lessons/0019-initialization-warmup-and-gradient-clipping.md) | Inicialização, warm-up e gradient clipping | Um modelo tão profundo pode falhar antes mesmo de o treinamento começar se os seus pesos iniciais forem escalados de forma errada, e o passo do AdamW que a lição 11 derivou ainda precisa de mais duas salvaguardas, um início lento e um teto rígido para o gradiente, para de fato sobreviver ao treinamento real |
| [0020](lessons/0020-mixed-precision-and-gradient-accumulation.md) | Precisão mista e gradient accumulation | As duas técnicas existem para encaixar uma execução de treinamento efetiva maior em um hardware menor do que a execução parece precisar, uma encolhendo a pegada de cada número, a outra simulando um batch maior do que a memória jamais comportaria de uma só vez |
| [0021](lessons/0021-encoder-decoder-and-encoder-only-architectures.md) | Arquiteturas encoder-decoder e encoder-only | Este workspace construiu um fluxo único com uma máscara causal porque só precisava fazer uma coisa, gerar o próximo token, e as outras duas formas de arquitetura existem porque o BERT e o modelo original de tradução precisavam, em vez disso, de uma garantia estruturalmente diferente |
| [0022](lessons/0022-mixture-of-experts-and-flashattention.md) | Mixture-of-experts e FlashAttention | O MoE faz crescer o total de parâmetros de um modelo sem fazer crescer o que um único token de fato paga para ser processado, e a FlashAttention calcula a mesma equação exata da lição 1 mais rápido reescrevendo como ela toca a memória, e não o que ela calcula |
| [0023](lessons/0023-reviewing-a-change-to-model-code.md) | Revisando uma mudança no código de um modelo | Revise a mudança de outra pessoa no código de um modelo e nomeie o que ela quebra ou custa, em vez de confiar na descrição |

## Referência

- [Glossário](GLOSSARY.md): termos canônicos deste tópico
- [Recursos](RESOURCES.md): fontes confiáveis
- [Atenção](reference/attention.md): scaled dot-product attention, multi-head attention e máscara causal, com os formatos dos tensores anotados em cada etapa
- [O bloco transformer](reference/the-transformer-block.md): codificação posicional, layer norm e residuais, o bloco feed-forward, o empilhamento e o weight tying
- [O loop de treinamento](reference/the-training-loop.md): loss de cross-entropy, o backward pass e o autograd e o passo do otimizador AdamW, com os exemplos resolvidos da regra da cadeia e do gradient descent
- [Mapeamento para o código real](reference/mapping-to-real-code.md): o mapeamento de nomes do transformers/llama.cpp, os três desvios padrão em relação ao artigo original, o byte-pair encoding e onde um adapter de baixo rank se acopla

## Como isto funciona

Cada lição é curta e autocontida. Os gabaritos ficam recolhidos: primeiro lembre, depois abra. A prática no mundo real importa mais do que a leitura, e espaçá-la é o ponto. Tudo o que ainda estiver confuso no fim de uma lição vale ser perseguido até a fonte primária antes de seguir adiante.
