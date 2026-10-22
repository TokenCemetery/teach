---
title: "Glossário"
description: "Termos canônicos de transformers"
type: glossary
---

# Glossário de Transformers

Termos canônicos da arquitetura transformer, derivados a partir de tensores brutos e não de um módulo pré-construído.

## Termos

**Cross-attention**:
Uma subcamada de atenção cujas queries vêm de uma sequência (a própria saída já gerada por um decoder), mas cujas keys e values vêm de uma sequência diferente (a saída de um encoder separado), permitindo que um decoder consulte uma entrada completa e já codificada enquanto gera. Ausente de um modelo decoder-only, que não tem encoder nem sequência de entrada separados sobre os quais atender.
_Evite_: self-attention (uma subcamada diferente, cujas queries, keys e values vêm todas da mesma sequência; a cross-attention extrai especificamente as suas keys e values de uma sequência diferente da das suas queries)

**Encoder-decoder**:
Uma arquitetura (como a do artigo original do transformer, ou o T5) que une um encoder bidirecional, sem máscara causal, que processa uma entrada completa, a um decoder que gera a saída de forma autorregressiva usando self-attention causal mais cross-attention de volta para a saída do encoder. Adequada a tarefas com uma divisão nítida e fixa entre entrada e saída, como a tradução.
_Evite_: decoder-only (a arquitetura que este workspace constrói, sem encoder separado nem cross-attention, já que o seu fluxo único serve tanto de contexto de condicionamento quanto de saída gerada)

**Encoder-only**:
Uma arquitetura (como a do BERT) que usa atenção bidirecional, condicionando-se conjuntamente ao contexto da esquerda e da direita em todas as camadas, sem nenhuma máscara causal. Constrói uma representação de uma entrada completa e já dada, para tarefas de compreensão (classificação, extração), e não gera texto de forma autorregressiva, algo que a sua arquitetura não consegue fazer.
_Evite_: decoder-only (uma arquitetura com máscara causal, construída especificamente para gerar um token por vez; a atenção bidirecional do encoder-only nunca foi treinada para prever a partir de apenas um prefixo)

**FlashAttention**:
Uma implementação exata e ciente de IO da scaled dot-product attention que divide a computação em blocos (tiling) para ficar na memória rápida da GPU dentro do chip (SRAM), sem nunca materializar a matriz completa de scores de atenção, de tamanho quadrático, na memória principal mais lenta (HBM). Calcula exatamente o mesmo resultado matemático da equação da lição 1; o ganho de velocidade vem inteiramente do acesso à memória, e não de aproximar qualquer coisa.
_Evite_: atenção aproximada (uma família diferente de métodos que trocam qualidade por velocidade; a FlashAttention é exata e obtém o seu ganho apenas da eficiência de IO)

**Gated linear unit (GLU)**:
O produto elemento a elemento de duas projeções lineares da mesma entrada, com uma não linearidade (originalmente a sigmoide) aplicada antes a uma delas. Essa projeção atua como um gate, escalando a saída da outra projeção elemento a elemento, em vez de aplicar uma única não linearidade fixa de modo uniforme.
_Evite_: SwiGLU (uma variante específica de GLU, com gate de Swish/SiLU; "GLU" é a família geral, e não este único membro dela)

**Gradient accumulation**:
Executar forward e backward passes em vários micro-batches menores em sequência, sem zerar os gradientes entre eles, deixando que os gradientes de cada micro-batch se somem aos anteriores, e então dar um único passo do otimizador sobre o total combinado. Simula um batch size efetivo maior do que a memória comportaria de uma só vez, sem mudar o que é calculado.
_Evite_: aumentar o batch size de fato (o objetivo que a gradient accumulation atinge sem exigir que o batch maior caiba na memória de uma só vez)

**Gradient norm clipping**:
Reescalar um vetor de gradiente inteiro para baixo, de modo que a sua norma geral não ultrapasse um limite escolhido e a sua direção permaneça inalterada, sempre que essa norma seria maior do que isso. Protege contra um gradiente explosivo ocasional que provoque uma única atualização destrutivamente grande.
_Evite_: fazer o clipping do gradiente de cada parâmetro de forma independente (distorce a direção do gradiente combinado; o clipping por norma reescala o vetor inteiro de modo uniforme)

**Greedy decoding**:
Escolher sempre o único token de maior probabilidade da distribuição prevista pelo modelo a cada passo de geração. É determinístico e, apesar de maximizar a mesma quantidade que o modelo foi treinado para prever bem, produz na prática um texto insípido e estranhamente repetitivo.
_Evite_: supor que o objetivo de treinamento (a likelihood) é automaticamente o objetivo certo de decodificação; as duas são perguntas diferentes, com respostas diferentes

**Grouped-query attention (GQA)**:
Uma variante de atenção que usa um número intermediário de heads de key/value, mais de um e menos do que o número de heads de query, com grupos de heads de query compartilhando cada um um head de key/value. Um meio-termo entre os keys/values por head da multi-head attention completa e o único head compartilhado da multi-query attention.
_Evite_: multi-query attention (MQA) (o caso mais extremo, um único head de key/value compartilhado; a GQA é a generalização que mantém mais de um)

**KV cache**:
Os vetores de key e value armazenados de todas as posições anteriores durante a geração autorregressiva, reaproveitados a cada novo passo de geração em vez de recalculados do zero. O seu tamanho cresce com o número de conjuntos distintos de heads de key/value que um modelo tem, justamente o que a grouped-query e a multi-query attention reduzem.
_Evite_: recalcular keys e values a cada passo de geração (correto, mas desperdiçador; o cache existe especificamente para evitar isso)

**Warm-up da learning rate**:
Aumentar a learning rate gradualmente (muitas vezes de forma linear) ao longo de um número fixo de passos iniciais de treinamento até que ela atinja o valor-alvo, em vez de aplicar a força total imediatamente. Resolve o fato de as estimativas de momento do Adam não serem confiáveis nos primeiros passos, antes que gradientes suficientes tenham sido vistos para calibrá-las.
_Evite_: aplicar a learning rate-alvo desde o primeiro passo (arrisca uma atualização grande e mal direcionada antes que as próprias estatísticas do otimizador tenham se estabilizado)

**Treinamento em precisão mista**:
Armazenar pesos, ativações e gradientes em meia precisão durante a maior parte do treinamento, em vez de precisão completa (simples), reduzindo o uso de memória quase pela metade. Exige uma cópia master dos pesos em precisão completa (para preservar pequenas atualizações que de outro modo sofreriam underflow) e loss scaling (para impedir que gradientes pequenos sofram underflow até zero).
_Evite_: treinar apenas em meia precisão, sem cópia master dos pesos nem loss scaling (arrisca perder silenciosamente pequenas atualizações e gradientes por underflow)

**Mixture-of-experts (MoE)**:
Uma camada que substitui um único bloco feed-forward por vários blocos feed-forward de experts em paralelo, mais um router que seleciona qual(is) expert(s) processa(m) um dado token. Ativada de forma esparsa: a contagem total de parâmetros cresce com o número de experts, mas o custo de compute por token permanece aproximadamente constante, já que apenas o(s) expert(s) selecionado(s) realmente executa(m).
_Evite_: supor que mais experts significam mais compute por token (apenas o compute do expert escolhido pelo router conta para o custo de um dado token, não importa quantos experts existam no total)

**Nucleus sampling (top-p)**:
Amostrar do menor conjunto de tokens de maior probabilidade cuja probabilidade acumulada ultrapassa um limiar `p`, um conjunto cujo tamanho varia de passo a passo conforme a distribuição seja mais concentrada ou mais plana. Contrasta com o truncamento de tamanho fixo do top-k, que não consegue se adaptar a essa variação.
_Evite_: top-k sampling (um truncamento de contagem fixa; o corte do nucleus sampling é, em vez disso, um conjunto dinâmico, baseado em probabilidade acumulada)

**RMSNorm**:
Uma normalização que divide um vetor de ativação pela sua raiz do valor quadrático médio (root mean square) e aplica uma escala aprendida, mantendo a operação de reescalonamento da layer norm e abandonando por completo a sua etapa de recentralização (subtração da média). Mais barata que a layer norm, com desempenho comparável nas tarefas na prática.
_Evite_: layer norm (a normalização baseada em média e variância que a RMSNorm simplifica; a RMSNorm nunca calcula nem subtrai uma média)

**Rotary position embedding (RoPE)**:
Um mecanismo posicional que rotaciona os vetores de query e key projetados por um ângulo proporcional à sua posição, em vez de somar um vetor fixo ao embedding antes. Como as rotações se compõem somando ângulos, o score de atenção resultante depende apenas do deslocamento relativo entre duas posições, e não de nenhuma das posições absolutas.
_Evite_: codificação sinusoidal (um mecanismo diferente, aditivo, aplicado ao embedding antes da projeção; o RoPE é multiplicativo e aplicado a Q e K depois da projeção, dentro do próprio cálculo de atenção)

**Scaled dot-product attention**:
A operação `softmax(QK^T / sqrt(d_k)) V`: comparar uma query com um conjunto de keys por produto escalar, escalar para compensar o crescimento da variância com `d_k`, transformar os scores em pesos com softmax e devolver a soma ponderada dos values correspondentes.
_Evite_: mecanismo de atenção (vago demais quando se quer dizer esta forma específica)

**Self-attention**:
Scaled dot-product attention em que as queries, keys e values vêm todas da mesma sequência de entrada, de modo que cada posição atende a todas as posições dessa mesma sequência, incluindo ela mesma.
_Evite_: intra-attention

**SwiGLU**:
A variante de GLU com gate da ativação Swish (SiLU), usada na subcamada feed-forward da maioria dos modelos abertos atuais no lugar de uma não linearidade simples como ReLU ou GELU. Usa três matrizes de pesos (duas projeções de expansão e uma de contração), em vez das duas de um bloco feed-forward simples.
_Evite_: GELU, ReLU (as não linearidades fixas, de projeção única, que o desenho com gate e duas projeções do SwiGLU substitui nos modelos atuais)

**Temperatura**:
Um valor que divide os logits antes do softmax que produz uma distribuição de próximo token durante a geração. Abaixo de 1, ela afia a distribuição em direção ao comportamento do greedy; acima de 1, a achata. Remodela o quão concentrada a distribuição é, sem decidir quais tokens podem ser amostrados.
_Evite_: top-k, top-p (a temperatura apenas reescala a nitidez das probabilidades; decidir o conjunto elegível é uma etapa separada e posterior, executada por esses métodos)

**Top-k sampling**:
Truncar uma distribuição de próximo token para os seus `k` tokens de maior probabilidade, descartando o restante, e amostrar desse conjunto renormalizado de tamanho fixo. Ao contrário do nucleus sampling (top-p), o tamanho do conjunto elegível nunca se adapta ao quão concentrada ou plana a distribuição realmente é em um dado passo.
_Evite_: nucleus sampling (top-p) (uma alternativa de tamanho dinâmico; a contagem de corte do top-k é fixa, qualquer que seja o formato real da distribuição)

**Inicialização de Xavier (Glorot)**:
Escalar a variância inicial dos pesos de uma camada pelo seu fan-in e fan-out (o número de entradas e de saídas a que ela se conecta), em vez de usar uma variância fixa para todas as camadas, de modo que a variância das ativações e dos gradientes permaneça aproximadamente consistente ao longo das camadas de uma rede profunda, em vez de encolher ou crescer de forma composta a cada uma delas.
_Evite_: uma única variância de inicialização fixa para todas as camadas, independentemente do tamanho (o problema que a inicialização de Xavier foi projetada especificamente para resolver)
