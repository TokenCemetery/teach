---
title: "Glossário"
description: "Termos canônicos de quantização de LLMs"
type: glossary
---

# Glossário de Quantização

Termos canônicos para formatos numéricos, métodos de quantização, o hardware em que eles rodam e como o seu custo é medido. Neste workspace, "quantização" sempre significa reduzir a precisão dos números de um modelo treinado; nunca significa discretizar entradas.

## Termos

**Quantização absmax**:
Quantização simétrica cuja faixa de clipping é o maior valor absoluto entre os valores que compartilham uma scale, de modo que nada sofre clipping e a scale é esse valor dividido pelo maior nível inteiro.
_Evite_: max scaling, quantização ingênua

**Act-order**:
Uma opção do GPTQ que quantiza as colunas de uma camada em ordem decrescente de tamanho da ativação, ordenando-as pela diagonal da Hessiana. Está documentada no código dos autores, não no artigo.
_Evite_: desc_act sem apresentá-lo, truque de reordenação (o nome que o artigo do AWQ dá a uma variante do GPTQ)

**Ativação** (_activation_):
Um tensor calculado durante o forward pass, como a entrada de uma camada linear, em oposição a um peso armazenado. Seus valores dependem da entrada, então sua faixa só é conhecida em tempo de execução ou estimada a partir de um calibration set.
_Evite_: hidden state (serve para o residual stream especificamente), feature map

**Quantização afim**:
Quantização com uma scale e um zero-point, de modo que a grade de inteiros pode ficar assimétrica em torno do zero e cobrir uma faixa como [-0.2, 1.5] sem desperdiçar níveis.
_Evite_: quantização assimétrica (apelido aceito, mas use um só termo), quantização uniforme (vale também para a simétrica)

**Intensidade aritmética**:
O número de operações aritméticas que uma computação realiza por byte que ela move da memória, o que decide se ela é limitada pela largura de banda de memória ou por compute em um dado chip.
_Evite_: intensidade operacional, razão FLOP por byte (aceita em uma fórmula)

**Largura em bits** (_bit width_):
O número de bits usado para armazenar um valor quantizado, sem contar os bits gastos com a sua scale e o seu zero-point. Veja bits efetivos por peso para o total.
_Evite_: precisão (ambígua com os bits de mantissa), profundidade de bits

**Formato com escala por bloco**:
Um formato em que um pequeno bloco de valores, como 32, compartilha uma scale guardada junto com eles, de modo que o tipo do elemento pode ser muito estreito. MXFP4 e NVFP4 são exemplos, assim como os tipos de bloco do GGUF.
_Evite_: microscaling (essa é uma família, a MX da OCP), formato agrupado

**Calibration set**:
Uma pequena amostra de entradas representativas passada pelo modelo para coletar estatísticas de ativação, que um método post-training usa para escolher faixas ou para ponderar erros de arredondamento. Não são dados de treinamento e a PTQ nunca faz backpropagation por ele.
_Evite_: conjunto de treinamento, dataset de calibração (serve, mas não "dados de calibração" para as estatísticas em si)

**Erro de clipping**:
O erro causado por valores fora da faixa de clipping serem limitados às extremidades dela.
_Evite_: erro de saturação, overflow

**Faixa de clipping**:
O intervalo de valores reais que um quantizador mapeia para a sua grade de inteiros; valores fora dele são limitados à extremidade mais próxima. Escolhê-la troca erro de clipping por erro de arredondamento.
_Evite_: faixa dinâmica (essa é uma propriedade do formato), faixa de quantização

**Limitado por compute**:
Uma carga de trabalho cuja velocidade é limitada pela vazão aritmética e não pelo movimento de bytes, típica do prefill e do decode com batch grande. Quantizar apenas os pesos não a acelera e pode deixá-la mais lenta.
_Evite_: limitado por FLOPs (serve, mas use um só termo)

**Dequantização**:
Mapear um inteiro quantizado de volta a um valor real aproximado com a sua scale e o seu zero-point, seja para calcular em precisão maior, seja para inspecionar o erro.
_Evite_: desquantização, descompressão

**Quantização dinâmica**:
Calcular a scale de uma ativação em tempo de execução a partir dos valores realmente presentes, em vez de fixá-la antes a partir de um calibration set. Contraste com a quantização estática.
_Evite_: quantização on-the-fly, quantização em tempo de execução

**Bits efetivos por peso**:
O armazenamento médio por peso depois de incluir as scales, os zero-points e qualquer outro metadado por grupo, por exemplo cerca de 4.5 para pesos de 4 bits com uma scale de 16 bits por grupo de 32.
_Evite_: bpw sem defini-lo, largura em bits (que exclui os metadados)

**Bits de expoente**:
Os bits de um formato de ponto flutuante que definem a potência de dois pela qual um valor é escalado e, portanto, a sua faixa dinâmica.
_Evite_: bits de faixa

**Quantização fake**:
Quantizar e dequantizar imediatamente um tensor no forward pass, de modo que o treinamento enxerga o erro de arredondamento e de clamping enquanto a aritmética continua em ponto flutuante.
_Evite_: quantização simulada (apelido aceito, mas use um só termo), injeção de ruído de quantização

**Flip**:
Uma resposta que muda de correta para incorreta, ou de incorreta para correta, entre um modelo baseline e a sua versão quantizada na mesma pergunta. Flips nas duas direções se cancelam em uma média de acurácia, então são contados separadamente.
_Evite_: mudança de resposta (também conta incorreta para incorreta), regressão (só uma direção)

**GGUF**:
O formato de modelo em arquivo único do llama.cpp, que armazena tensores, muitas vezes nos seus próprios tipos de quantização em bloco, junto com o tokenizer e os metadados do modelo.
_Evite_: GGML (a biblioteca e um formato mais antigo), formato llama

**GPTQ**:
Um método de quantização de pesos post-training que quantiza os pesos de uma camada uma coluna por vez e atualiza os pesos ainda não quantizados para compensar cada erro de arredondamento, usando informação de segunda ordem das ativações de calibração.
_Evite_: quantização GPT, usar como genérico para qualquer checkpoint de 4 bits

**Granularidade**:
Quantos valores compartilham uma scale e um zero-point: um tensor inteiro (per-tensor), um canal de saída (per-channel), um token (per-token) ou um grupo de tamanho fixo dentro de um canal (per-group).
_Evite_: resolução, nível de quantização

**Tamanho do grupo** (_group size_):
O número de valores consecutivos que compartilham uma scale na quantização per-group, como 32 ou 128.
_Evite_: tamanho do bloco (aceito onde um formato o chama assim, como MX ou GGUF)

**Hessiana** (_Hessian_):
No GPTQ, a matriz `H = 2 X X^T` construída a partir das entradas de calibração de uma camada, com uma linha e uma coluna por feature de entrada. Ela registra quais features se movem juntas e é compartilhada por todas as linhas dos pesos da camada.
_Evite_: matriz de curvatura, matriz de covariância (próxima, mas não é o mesmo objeto)

**Matriz de importância**:
No llama.cpp, a importância por peso estimada a partir das ativações em um texto de calibração, usada para ponderar o erro de arredondamento ao escolher a scale de cada bloco.
_Evite_: imatrix em prosa sem apresentá-la

**Kernel**:
A rotina de GPU que executa uma operação, como uma multiplicação de matrizes em um dado esquema de quantização. Um esquema só roda rápido onde existe um kernel para ele no hardware.
_Evite_: operador (mais amplo), implementação

**Divergência KL** (_KL divergence_):
O quanto a distribuição de próximo token do modelo quantizado está distante da do baseline, em média sobre os tokens de um dataset. É 0 quando as duas coincidem exatamente e não precisa de respostas rotuladas.
_Evite_: KLD sem defini-la, distância (ambíguo)

**Quantização do KV cache**:
Armazenar as keys e values de atenção em cache em menos bits, para reduzir a memória que cresce com o tamanho do contexto e o batch size.
_Evite_: compressão de cache (também cobre a remoção de entradas), quantização de KV dos pesos

**Loss scaling**:
Multiplicar a loss por uma constante antes da backpropagation para que gradientes pequenos continuem representáveis em um formato de faixa estreita como o fp16, e depois dividir a constante antes da atualização dos pesos.
_Evite_: gradient scaling (ambíguo com gradient clipping)

**Epsilon de máquina** (_machine epsilon_):
A distância entre 1 e o próximo valor representável acima dele em um formato de ponto flutuante, igual a 2 elevado ao negativo do número de bits de mantissa.
_Evite_: unit roundoff (metade deste valor com round-to-nearest), precisão

**Bits de mantissa**:
Os bits de um formato de ponto flutuante que definem o quão fino é o espaçamento dos valores dentro de uma potência de dois e, portanto, a sua precisão.
_Evite_: significando (correto, mas use um só termo), bits de fração

**Ativação massiva**:
Um único valor de ativação em um LLM que é ordens de grandeza maior que o resto, aparecendo em uma dimensão fixa e em tokens específicos, como o primeiro.
_Evite_: feature outlier (um padrão relacionado, mas diferente), spike

**Limitado pela largura de banda de memória**:
Uma carga de trabalho cuja velocidade é limitada pela rapidez com que os bytes saem da memória e não pela aritmética, típica do decode com batch pequeno, em que cada peso é lido uma vez por token gerado.
_Evite_: limitado por banda (serve, mas use um só termo), limitado por IO

**Decomposição em precisão mista**:
Dividir uma multiplicação de matrizes para que as poucas dimensões de feature outlier sejam calculadas em 16 bits e o resto em int8, o núcleo do LLM.int8().
_Evite_: divisão de outliers, precisão mista (mais amplo)

**Formato nativo**:
Um formato numérico em que as unidades de matriz de um chip multiplicam diretamente, em oposição a um formato só de armazenamento, que precisa ser convertido para um formato nativo antes da multiplicação.
_Evite_: formato suportado (ambíguo entre armazenamento e compute)

**Piso de ruído** (_noise floor_):
A variação de uma pontuação entre execuções e entre amostras, abaixo da qual uma diferença entre um modelo baseline e um modelo quantizado não pode ser distinguida do acaso.
_Evite_: margem de erro (o intervalo é a forma de reportar o piso), tolerância

**Feature outlier**:
Uma dimensão do hidden state em que as ativações de um transformer são consistentemente muito maiores do que nas outras, na maioria dos tokens e das camadas.
_Evite_: canal outlier (aceito para o canal de pesos correspondente), feature emergente sem a palavra outlier

**Perplexity**:
A exponencial da média do log-likelihood negativo que um modelo atribui a um texto, usada como um proxy rápido de quanto uma mudança prejudicou o modelo.
_Evite_: PPL em prosa sem apresentá-la, acurácia

**Quantização pós-treinamento**:
Quantizar um modelo já treinado sem treinamento adicional, usando no máximo um pequeno calibration set.
_Evite_: PTQ em prosa sem apresentá-la, quantização one-shot

**Quantização**:
Representar os números reais de um modelo em um conjunto menor de níveis, com menos bits, ao custo de um erro de aproximação limitado.
_Evite_: compressão (mais ampla), discretização

**Configuração de quantização**:
A entrada `quantization_config` no `config.json` de um modelo, cujas chaves `quant_method` e outras dizem a um loader qual método, largura em bits e tamanho de grupo os tensores armazenados usam.
_Evite_: quantize config (um arquivo separado que algumas ferramentas escrevem), metadados

**Treinamento ciente de quantização**:
Treinar ou fazer fine-tuning de um modelo com quantização fake no forward pass, para que os pesos se adaptem ao arredondamento que vão enfrentar.
_Evite_: QAT em prosa sem apresentá-la, treinamento quantizado (esse calcula em baixa precisão)

**Ridge point**:
A intensidade aritmética em que a taxa aritmética de pico de um chip e a sua largura de banda de memória levam o mesmo tempo, abaixo da qual uma computação é limitada pela largura de banda de memória e acima da qual é limitada por compute.
_Evite_: roofline knee, ponto de cruzamento

**Rotação**:
Multiplicar as ativações e os pesos de uma camada por uma matriz ortogonal e pela sua transposta, o que deixa a saída da camada inalterada, mas espalha os outliers por muitos canais para que quantizem melhor.
_Evite_: transformada de Hadamard (uma escolha de rotação), incoherence processing (a ideia geral)

**Round-to-nearest**:
Quantizar cada valor de forma independente para o nível da grade mais próximo, sem dados e sem compensação de erro. É o baseline com que todo outro método post-training é comparado.
_Evite_: RTN em prosa sem apresentá-lo, quantização ingênua

**Erro de arredondamento**:
O erro causado por um valor dentro da faixa de clipping ser movido para o nível da grade mais próximo; no máximo meio passo no round-to-nearest.
_Evite_: ruído de quantização (aceito para o erro combinado), perda de precisão

**Safetensors**:
Um formato de arquivo de tensores com um cabeçalho de 8 bytes com o tamanho, um cabeçalho JSON com nomes de tensores, dtypes, shapes e offsets, e depois os dados brutos. Ele armazena apenas tensores, então o esquema de quantização é descrito na configuração de quantização.
_Evite_: checkpoint (o conjunto inteiro de arquivos), arquivo de pesos

**Canal saliente** (_salient channel_):
Um canal de entrada de uma matriz de pesos cujo erro de quantização mais importa, encontrado no AWQ pelo tamanho da ativação que ele encontra e não pelo tamanho dos seus próprios pesos.
_Evite_: peso importante (serve em prosa), canal outlier (o nome do lado dos pesos para uma feature outlier)

**Scale**:
O tamanho do passo, em valor real, entre níveis inteiros adjacentes de um quantizador, de modo que um valor real é aproximadamente a scale vezes o seu inteiro.
_Evite_: passo (serve em uma fórmula), multiplicador

**Quantização estática**:
Fixar a scale de uma ativação antes, a partir de um calibration set, de modo que nenhuma estatística seja calculada em tempo de execução. Contraste com a quantização dinâmica.
_Evite_: quantização offline

**Straight-through estimator**:
Tratar a etapa de arredondamento como a função identidade no backward pass, para que um gradiente possa fluir por uma operação cuja derivada verdadeira é zero quase em toda parte.
_Evite_: STE em prosa sem apresentá-lo, gradiente substituto (mais amplo)

**Super-block**:
Em uma k-quant do GGUF, um grupo de 256 pesos dividido em sub-blocos que têm cada um a sua própria scale, com essas scales quantizadas em relação a uma scale de super-block de 16 bits.
_Evite_: bloco (a unidade de 32 pesos dos tipos legados)

**Quantização simétrica**:
Quantização com o zero-point fixado em zero, de modo que a grade fica centrada no zero e só uma scale é armazenada.
_Evite_: quantização só com scale

**Quantização somente de pesos**:
Armazenar os pesos em baixa precisão e dequantizá-los dentro do kernel, enquanto as ativações e a aritmética ficam em 16 bits. Escreve-se WxA16, como W4A16.
_Evite_: quantização de precisão mista (mais ampla)

**Notação WxAy**:
Abreviação para as larguras em bits de pesos e ativações de um esquema, como W8A8 para pesos e ativações de 8 bits, às vezes com KVz para o KV cache.
_Evite_: escrever int4 quando as ativações não são também int4

**Zero-point**:
O inteiro que representa o zero real na quantização afim, escolhido para que o zero seja exatamente representável.
_Evite_: offset, bias
