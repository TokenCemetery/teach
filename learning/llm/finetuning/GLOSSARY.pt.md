---
title: "Glossário"
description: "Termos canônicos de fine-tuning com adapters"
type: glossary
---

# Glossário de Fine-Tuning com Adapters

Termos canônicos deste workspace. Um termo entra aqui quando já pode ser usado corretamente, e não quando é mencionado pela primeira vez, então este glossário cresce conforme as lições são conquistadas.

## Uso neste workspace

Três palavras são usadas de forma imprecisa em toda a área, de maneiras que deixariam as lições seguintes ambíguas, então ficam fixadas desde o início:

**Fine-tuning**:
Treinar em uma tarefa um pequeno conjunto de parâmetros adicionados ou selecionados, enquanto os pesos do base model ficam congelados. Quando todos os pesos são treinados, este workspace sempre diz _full fine-tuning_ de forma explícita.
_Evite_: treinamento, retreinamento, ensinar o modelo

**Adapter**:
O pequeno conjunto de pesos treináveis adicionado ao lado de um base model congelado, junto com a configuração que descreve onde ele se acopla.
_Evite_: fine-tune (como substantivo), LoRA (quando o método não é especificamente o LoRA), checkpoint

**Quantização**:
Armazenar os pesos com precisão numérica menor do que aquela em que foram treinados. Neste workspace ela sempre se refere ao _base model congelado_, salvo indicação em contrário: os adapters permanecem em precisão maior, e a quantização para inferência é um assunto separado.
_Evite_: compressão, encolhimento, otimização

## Termos

**Base model**:
Um modelo treinado com um único objetivo, prever o próximo token em um corpus grande. Ele continua o texto em vez de respondê-lo, e não tem _chat template_.
_Evite_: modelo bruto, modelo pré-treinado (quando a distinção em relação a um _modelo instruct_ importa)

**Esquecimento catastrófico**:
A degradação, durante o fine-tuning, de habilidades que os dados de treino não reforçaram, como seguir instruções de forma geral. Ela não aparece na loss da tarefa nem na métrica held-out, que podem melhorar enquanto isso acontece.
_Evite_: overfitting (uma falha diferente, visível no próprio _conjunto held-out_ da tarefa)

**Chat template**:
O formato exato de string em que as conversas de treino de um modelo de chat foram renderizadas, transformando papéis e mensagens em uma única sequência plana de tokens. O treino e o serving precisam usar a mesma renderização.
_Evite_: formato de prompt, formato de chat

**Contaminação**:
Exemplos de teste que o modelo já viu. A contaminação _própria_ são exemplos de teste que também aparecem, exata ou quase exatamente, no seu conjunto de treino; a contaminação _herdada_ são exemplos de teste que estavam no corpus de pré-treino do _base model_.
_Evite_: vazamento (diga qual dos dois tipos se quer dizer)

**DoRA**:
Uma variante de _LoRA_ que divide cada matriz de pesos congelada em um vetor de magnitude, treinado diretamente, e uma direção, que recebe a atualização de baixo rank e é renormalizada depois. No PEFT é uma flag na configuração do LoRA, não um método separado.
_Evite_: LoRA com decomposição de pesos (escreva por extenso só uma vez, depois diga DoRA)

**Dupla quantização**:
_Quantização_ das próprias escalas por bloco: as escalas fp32 de primeiro nível são agrupadas e armazenadas em 8 bits, com a sua própria escala de segundo nível.
_Evite_: quantização aninhada, quantização de 2 bits

**Batch size efetivo**:
O número de exemplos cujos gradientes são promediados em um único passo do otimizador: batch size por dispositivo × passos de acumulação de gradiente × número de dispositivos.
_Evite_: batch size (quando se quer dizer o número por dispositivo)

**Gradient checkpointing**:
Guardar apenas a entrada de cada bloco durante o forward pass e executar o bloco de novo quando o backward pass chega a ele, de modo que as ativações armazenadas crescem com aproximadamente a raiz quadrada da profundidade em vez de linearmente, ao custo de cerca de um forward pass extra por passo.
_Evite_: checkpointing (sozinho, pois um checkpoint de treino são pesos salvos em disco), recomputação de ativações

**Conjunto held-out**:
Dados nos quais o modelo não é treinado, usados para medir se ele aprendeu a tarefa. Neste workspace ele tem duas partes: validação, contra a qual configurações e checkpoints são escolhidos, e teste, tocado uma única vez no final.
_Evite_: conjunto de avaliação, conjunto de desenvolvimento

**Modelo instruct**:
Um _base model_ treinado mais a fundo em pares de instrução e resposta, e geralmente em dados de preferência depois disso. Modelo de chat significa a mesma coisa aqui.
_Evite_: modelo alinhado, modelo assistente

**LoRA**:
Low-rank adaptation: um _adapter_ que aprende a atualização de uma matriz de pesos como o produto de duas matrizes pequenas, `ΔW = BA`, escalada por `α/r`, enquanto a própria matriz permanece congelada.
_Evite_: adapter (quando se quer dizer o método específico), fine-tune de baixo rank

**LoRA alpha**:
O escalar fixo `α` (`lora_alpha`) que escala a atualização de um _LoRA_ por `α/r`. O que define a escala da atualização é a razão `α/r`, não qualquer um dos dois números isoladamente.
_Evite_: fator de escala (esse é `α/r`, não `α`)

**Merge**:
Incorporar a atualização de um _LoRA_ aos pesos base, `W₀ + (α/r)BA`, e descartar a estrutura do adapter. É exato contra um base model em precisão total e com perdas contra um quantizado.
_Evite_: exportar, embutir

**Serving multi-adapter**:
Servir vários _adapters_ sobre um único base compartilhado, agrupando em lote requisições que usam adapters diferentes: o cálculo do base é compartilhado pelo lote, e a contribuição do adapter de cada requisição é calculada separadamente.
_Evite_: troca de adapters (a abordagem ingênua que serializa as requisições)

**NF4**:
NormalFloat, um formato de 4 bits cujos 16 níveis são espaçados para valores distribuídos normalmente em torno de zero, como são os pesos, em vez de em intervalos iguais como no int4 simples. É usado dentro da _quantização_ por bloco, em blocos já normalizados pelo seu absmax.
_Evite_: int4 (um formato diferente, uniformemente espaçado)

**Estado do otimizador**:
Os tensores que um otimizador mantém por parâmetro treinável além do peso e do seu gradiente. Para o AdamW, são o primeiro e o segundo momentos, 4 bytes cada.
_Evite_: cache do otimizador, momentum (apenas o primeiro momento)

**Packing**:
Concatenar exemplos de treino curtos em sequências de comprimento total, de modo que um batch carregue quase nenhum padding.
_Evite_: agrupamento por comprimento (um remédio diferente, que agrupa em lote sequências de tamanho parecido)

**QLoRA**:
_LoRA_ treinado contra um base congelado armazenado em _NF4_ com _dupla quantização_, que é desquantizado a cada forward e backward pass. É LoRA com um base mais barato, não um método com hiperparâmetros próprios.
_Evite_: fine-tuning de 4 bits, LoRA quantizado (quando sugere que o adapter é quantizado)

**Rank**:
A dimensão interna `r` das duas matrizes do _LoRA_, sendo `A` de `r × d_in` e `B` de `d_out × r`. É a capacidade do adapter: limita a complexidade da atualização que o adapter consegue expressar.
_Evite_: tamanho, dimensão (sozinha)

**Conjunto de regressão**:
Um conjunto fixo de sondas fora da tarefa (seguir instruções em geral, conformidade de formato e de comportamento, segurança e comportamento de recusa, capacidade adjacente), executado antes e depois do treino para detectar o _esquecimento catastrófico_. É um instrumento diferente do _conjunto held-out_, e os dois são necessários.
_Evite_: benchmark, suíte de avaliação (quando se quer dizer este instrumento específico)

**Target modules**:
As matrizes de pesos às quais um _adapter_ se acopla, nomeadas pelos próprios nomes de módulo do modelo.
_Evite_: camadas (um adapter se acopla a matrizes específicas dentro de uma camada)
