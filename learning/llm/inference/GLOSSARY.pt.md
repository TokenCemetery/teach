---
title: "Glossário"
description: "Termos canônicos de inferência"
type: glossary
---

# Glossário de Inferência

Termos canônicos para servir um modelo treinado: o que um servidor mantém na memória e as alavancas que ele tem sobre latência e throughput.

## Termos

**Attention sink**:
A pontuação de atenção desproporcionalmente alta que os primeiros tokens de uma sequência recebem, independentemente do conteúdo real deles, e por isso removê-los de um cache de janela deslizante causa um colapso de qualidade em vez de uma perda gradual de contexto antigo. Manter permanentemente em cache apenas as entradas de KV desses tokens iniciais, junto com a janela deslizante usual, recupera a maior parte do desempenho da atenção completa (a técnica StreamingLLM).
_Evite_: supor que qualquer token antigo descartado causa o mesmo dano (só os tokens iniciais "sink" carregam esse peso desproporcional; perder outros tokens antigos fora da janela degrada de forma gradual em vez de colapsar)

**Cold start (serving)**:
O intervalo entre um autoscaler decidir adicionar uma réplica e essa réplica realmente conseguir atender uma requisição, dominado pelo tempo de carregar na memória o checkpoint de um modelo grande, que pode levar dezenas de segundos e supera de longe o tempo de gerar um único token.
_Evite_: tratá-lo como um problema de fila de requisições (um scheduler ou um roteador não tem efeito sobre ele; ele é determinado inteiramente pelo tamanho do checkpoint e pelo caminho de armazenamento que ele precisa atravessar)

**Decodificação restrita (guiada)**:
Mascarar todo token que violaria uma estrutura exigida (JSON válido, uma gramática) antes de a amostragem acontecer, de modo que a estrutura da saída seja garantida por construção e não apenas incentivada. Mantida barata por token ao reformular a gramática como uma máquina de estados finitos e pré-computar, uma única vez, um índice de quais tokens são válidos a partir de cada estado.
_Evite_: verificar a validade da saída depois que a geração termina (não garante nada, já que o modelo sempre foi livre para amostrar um token inválido; mascarar antes da amostragem é o que torna a garantia estrutural)

**Custo por milhão de tokens**:
O custo horário de aluguel de uma GPU dividido pelo seu throughput medido (tokens/s, convertido em tokens/hora), escalado para um milhão de tokens. Derivado do mesmo throughput medido que o trade-off de batch size da lição 6 produz, e não citado a partir do preço por token anunciado por um fornecedor e medido com o batch size de outra carga de trabalho.
_Evite_: um preço por token fixo, citado por um fornecedor (o throughput, e portanto o custo por token, depende do batch size e da carga de trabalho sob os quais foi medido, e não se transfere entre configurações)

**Modelo draft**:
Um modelo pequeno e barato (ou um mecanismo que não é um modelo, como a correspondência de n-gramas, ou cabeças extras no próprio modelo alvo) que propõe vários próximos tokens candidatos para o modelo alvo verificar em uma única passada paralela, em vez de o modelo alvo gerá-los um de cada vez.
_Evite_: uma alternativa menor e de qualidade inferior ao modelo alvo (a saída de um modelo draft nunca é usada diretamente; ela só é verificada, e possivelmente corrigida, pelo modelo alvo)

**Orçamento de erro**:
1 menos um objetivo de nível de serviço: a quantidade de falhas permitidas em relação a essa meta antes de o serviço ser considerado fora de conformidade com ela. Uma única requisição que falhou não é um problema por si só; o que importa é se a taxa de falhas está consumindo o orçamento mais depressa do que a janela de medição do SLO permite.
_Evite_: tratar qualquer medição isolada que falhou como um problema (o orçamento existe justamente porque alguma taxa de falhas é esperada e tolerada; só importa a taxa de consumo em relação à janela)

**KV cache**:
Os vetores de key e value armazenados de cada token já gerado, em cada camada, mantidos para que um servidor nunca precise recalculá-los para os tokens seguintes. O seu tamanho cresce linearmente com o comprimento da sequência e costuma ser o gargalo de memória no serving, e não os pesos do próprio modelo.
_Evite_: cache de atenção, key-value store

**Roteamento ciente do KV cache**:
Uma política de roteamento de requisições no nível da frota que envia uma nova requisição ao servidor que já tem a maior taxa de acerto de cache para ela, em vez de rotear apenas pela carga (round-robin, least-connections). Estende o benefício do prefix caching de um servidor para uma frota de vários servidores, ao tornar a própria decisão de roteamento ciente de onde já existe um cache correspondente.
_Evite_: balanceamento de carga comum (round-robin ou least-connections ignoram totalmente a localidade do cache e podem rotear uma requisição favorável ao cache para um servidor que precisa refazer o prefill do zero)

**Limitado pela largura de banda de memória**:
Uma computação cujo custo dominante é mover dados (como os pesos de um modelo) da memória para a unidade de computação, e não a aritmética realizada depois que esses dados chegam. A decodificação autorregressiva comum é limitada pela largura de banda de memória, e é exatamente isso que permite à speculative decoding verificar vários tokens candidatos em uma passada pelo custo aproximado de gerar apenas um.
_Evite_: limitado por compute (o regime oposto, em que a aritmética domina; confundir os dois faz perder a razão de o trabalho extra de verificação ser quase gratuito especificamente durante o decode)

**Bolha de pipeline**:
O tempo ocioso que os dispositivos de uma configuração com paralelismo de pipeline passam esperando, no início (enquanto o pipeline enche) e no fim (enquanto ele esvazia) do processamento de um batch, já que nem todo dispositivo tem trabalho nesses momentos. Dividir um batch em mais micro-batches reduz essa fração ociosa, mas nunca a elimina.
_Evite_: supor que o micro-batching remove a bolha por completo (ele só reduz a fração ociosa em relação ao trabalho total; um atraso de início e de esvaziamento permanece, qualquer que seja o número de micro-batches)

**Paralelismo de pipeline**:
Particionar a sequência de camadas de um modelo em grupos consecutivos colocados em dispositivos separados, de modo que os dados fluam pelos dispositivos na mesma ordem em que as camadas rodariam em um único dispositivo. A comunicação acontece apenas na fronteira entre o grupo de um dispositivo e o do seguinte, e é isso que lhe permite tolerar um link entre dispositivos mais lento do que o paralelismo de tensor exige e abranger vários nós.
_Evite_: dividir a computação dentro de uma única camada (isso é paralelismo de tensor; o paralelismo de pipeline nunca divide o que acontece dentro de uma camada, só decide quais camadas vão para onde)

**Prefix caching**:
Reaproveitar o KV cache já calculado de um prefixo compartilhado entre requisições que, fora isso, não têm relação entre si (um system prompt comum, um documento consultado repetidamente, turnos anteriores de uma conversa), com o mesmo mecanismo de compartilhamento de blocos que o PagedAttention usa entre as amostras paralelas de uma única requisição, estendido entre requisições. Acelera apenas o prefill; o tempo de decode não é afetado.
_Evite_: supor que ele também acelera o decode (ele apenas pula a computação redundante de prefill para um prefixo correspondente; gerar novos tokens depois custa exatamente o mesmo nos dois casos)

**RoPE scaling**:
Estender o tamanho de contexto que um modelo consegue tratar além do comprimento em que foi treinado, reescalando a forma como os rotary position embeddings codificam a distância entre tokens (a abordagem do YaRN: escalar menos as dimensões de alta frequência e mais as de baixa frequência), em vez de treinar do zero. Não muda nada em quantos tokens de keys e values são colocados em cache; um contexto mais longo tratado assim ainda paga por inteiro o crescimento linear usual do KV cache.
_Evite_: supor que ele reduz ou limita a memória do KV cache (ele só estende o comprimento máximo de contexto utilizável; o cache desse contexto mais longo ainda cresce exatamente como cresceria sem nenhuma escala aplicada)

**SLI (indicador de nível de serviço)**:
Uma razão quantitativa e relevante para o usuário, escolhida a partir de uma métrica bruta exportada, por exemplo a fração das requisições com TTFT abaixo de um limite declarado, formulada a partir da experiência do usuário e não do estado interno do servidor.
_Evite_: o próprio histograma da métrica bruta (um histograma são dados medidos; um SLI é a razão específica, relevante para o usuário, escolhida a partir dele para sustentar uma meta)

**Atenção de janela deslizante**:
Restringir cada token a atender no máximo a um número fixo, `W`, de tokens anteriores, em vez de toda a sequência até ali, combinada com um cache em buffer rotativo que guarda no máximo as keys e values de `W` tokens. Limita o KV cache de uma sequência a um tamanho constante, qualquer que seja o quanto a sequência realmente cresça, ao contrário do crescimento linear inalterado do RoPE scaling.
_Evite_: supor que ela estende o alcance útil do modelo da mesma forma que o RoPE scaling (ela limita o cache e restringe a atenção direta aos últimos `W` tokens; o que está além disso só é alcançado indiretamente, por camadas empilhadas, e sozinha sofre um colapso de qualidade sem attention sinks)

**SLO (objetivo de nível de serviço)**:
Uma meta declarada para um SLI, por exemplo "99% das requisições têm TTFT abaixo de 300 ms em 28 dias corridos". O que sobra, 1 menos o SLO, é o orçamento de erro.
_Evite_: o resultado de um benchmark isolado (o p99 medido uma única vez na lição 16 é um instantâneo; um SLO é uma meta permanente sustentada contra métricas exportadas continuamente)

**Speculative decoding**:
Redigir vários próximos tokens candidatos de forma barata e depois verificar todos em uma única passada forward paralela pelo modelo alvo, aceitando os palpites corretos e reamostrando os incorretos, de modo que a distribuição final da saída coincida exatamente com a de rodar o modelo alvo sozinho. Uma alavanca pura de latência, sem trade-off de qualidade.
_Evite_: uma técnica de aproximação (ela muda apenas quantas passadas forward caras a geração exige, nunca o que é gerado)

**Paralelismo de tensor**:
Dividir entre dispositivos, por colunas ou por linhas, as grandes multiplicações de matrizes dentro de uma única camada (os blocos de atenção e de MLP de um transformer), com cada dispositivo calculando a sua própria fatia em paralelo e um passo de comunicação recombinando o resultado verdadeiro em pontos específicos dentro de cada camada. Exige uma interconexão rápida (como NVLink), porque essa recombinação acontece no caminho crítico, a cada camada, a cada passada forward.
_Evite_: dividir camadas inteiras entre dispositivos (isso é paralelismo de pipeline; o paralelismo de tensor divide a computação dentro de uma camada, nunca atribui camadas inteiras a dispositivos diferentes)
