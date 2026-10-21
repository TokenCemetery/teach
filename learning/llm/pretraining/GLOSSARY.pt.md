---
title: "Glossário"
description: "Termos canônicos do pré-treinamento de LLMs"
type: glossary
---

# Glossário de Pré-treinamento de LLMs

Termos canônicos para treinar um modelo a partir da inicialização aleatória em escala: do que são feitos os dados e o orçamento de compute e como memória e computação são divididas entre muitos dispositivos.

## Termos

**Checkpointing de ativações**:
Descartar as ativações intermediárias durante o forward pass e recalculá-las durante o backward pass, trocando compute extra por menor uso de memória.
_Evite_: gradient checkpointing (o nome mais comum na prática, mas o que se salva em checkpoint são as ativações, e não os gradientes, e o nome impreciso confunde sobre o que está sendo trocado)

**Compute-optimal**:
O ponto, na relação de troca entre contagem de parâmetros e tokens de treinamento, que minimiza a loss para um orçamento fixo de compute de treinamento, em oposição a um modelo maior treinado com menos tokens do que esse ponto indica.
_Evite_: ótimo (ambíguo sobre ótimo para quê; sempre o combine com "compute" ou "inferência" para dizer qual orçamento está fixo)

**Paralelismo de dados**:
Dividir um batch de treinamento entre dispositivos que guardam, cada um, uma cópia completa do modelo, calculando os gradientes de forma independente e sincronizando-os com um all-reduce antes do passo do otimizador.
_Evite_: treinamento distribuído (o paralelismo de dados é uma das suas formas; o termo geral esconde qual recurso está sendo dividido)

**Deduplicação**:
Remover documentos quase duplicados ou exatamente duplicados de um corpus de treinamento antes da tokenização, porque texto repetido é uma das principais causas de memorização e de compute desperdiçado.
_Evite_: dedup (aceitável informalmente, mas o glossário escreve o termo por extenso depois que o conceito está fixado)

**Gradient clipping**:
Reescalar um gradiente proporcionalmente, antes que o passo do otimizador o use, para que a sua norma global nunca exceda um limite escolhido, restringindo o tamanho de uma única atualização, não importa o que tenha produzido um gradiente incomumente grande.
_Evite_: gradient clamping (clamping costuma significar limitar cada valor de forma independente; o clipping aqui reescala o vetor de gradiente inteiro por um único fator para limitar a sua norma)

**Warm-up da learning rate**:
Aumentar a learning rate de perto de zero até o seu máximo pretendido ao longo da primeira parte do treinamento, em vez de começar imediatamente no máximo, para que as atualizações iniciais da rede, as menos informadas, tenham um efeito menor sobre os pesos.
_Evite_: burn-in (termo de outras áreas para um período de estabilização; este workspace usa warm-up especificamente para a rampa da learning rate)

**Loss spike**:
Um aumento súbito e acentuado da loss de treinamento no meio de uma execução, normalmente causado por um batch numericamente instável ou por uma deriva acumulada do estado do otimizador, e distinguido do ruído comum por a loss se recuperar ou não por conta própria.
_Evite_: divergência (a divergência é o resultado quando um loss spike não se recupera; os dois não são o mesmo evento)

**Paralelismo de pipeline**:
Dividir as camadas de um modelo entre dispositivos, com cada dispositivo guardando uma fatia contígua da pilha e passando as ativações ao próximo, fazendo vários micro-batches passarem em pipeline por ela para manter todos os dispositivos ocupados.
_Evite_: paralelismo de modelo (o termo mais amplo em que este e o paralelismo de tensor se enquadram; use o específico quando a distinção importar)

**Lei de escala**:
Uma relação empírica de lei de potência entre a loss de um modelo e o compute, a contagem de parâmetros ou os dados com que ele foi treinado, usada para prever a loss de uma execução de treinamento antes de pagar por ela.
_Evite_: curva de escala (uma lei de escala é a relação ajustada; uma curva é um gráfico dela)

**Paralelismo de tensor**:
Dividir as matrizes de pesos de uma camada individual entre dispositivos, de modo que uma única multiplicação de matrizes seja calculada como uma soma de produtos parciais de cada dispositivo, ao custo de uma etapa de comunicação por camada dividida.
_Evite_: paralelismo de modelo (o termo mais amplo em que este e o paralelismo de pipeline se enquadram)

**Razão tokens por parâmetro**:
O número de tokens de treinamento dividido pela contagem de parâmetros do modelo, o único número em torno do qual um plano de treinamento compute-optimal é construído.
_Evite_: razão dados-modelo (usada de forma inconsistente na literatura para a quantidade inversa; este workspace sempre quer dizer tokens divididos por parâmetros)

**Estágio do ZeRO**:
Um dos três níveis crescentes de estado particionado entre os dispositivos de dados paralelos: estado do otimizador (estágio 1), estado do otimizador e gradientes (estágio 2), ou estado do otimizador, gradientes e parâmetros (estágio 3), cada um trocando mais comunicação por menos memória por dispositivo.
_Evite_: FSDP (o FSDP é a implementação do PyTorch do particionamento no estilo do ZeRO estágio 3; o ZeRO é a técnica subjacente, e este workspace usa o nome da técnica ao discutir a ideia e FSDP ao discutir a API)
