---
title: "Glossário"
description: "Termos canônicos do pós-treinamento de LLMs"
type: glossary
---

# Glossário de Pós-treinamento de LLMs

Termos canônicos para alinhar um modelo pré-treinado: o que cada objetivo de treinamento maximiza e o que muda quando o objetivo deixa de ser imitar texto e passa a ser otimizar uma recompensa.

## Termos

**Alignment tax**:
A perda de capacidade (normalmente medida em benchmarks no estilo do pré-treinamento) que o pós-treinamento pode introduzir como efeito colateral de otimizar para utilidade ou segurança.
_Evite_: regressão (uma regressão é qualquer queda de capacidade; o alignment tax nomeia a específica que se troca por alinhamento)

**Loss de Bradley-Terry**:
A função de loss usada para treinar um reward model em dados de preferência pareados, tratando a probabilidade de uma completion ser preferida a outra como função da diferença entre as suas pontuações escalares de recompensa.
_Evite_: loss de preferência (usada de forma frouxa para vários objetivos nesta área, incluindo o do DPO; Bradley-Terry nomeia o modelo específico de comparação pareada que a modelagem de recompensa usa)

**Vantagem relativa ao grupo**:
A substituta da função de valor aprendida no GRPO: para um grupo de completions amostradas para o mesmo prompt, a vantagem de uma completion é a sua recompensa menos a recompensa média do grupo, dividida pelo desvio padrão do grupo, aplicada a cada token dessa completion.
_Evite_: baseline (um baseline é o conceito geral de RL que a média do grupo cumpre; este workspace usa o nome específico quando o GRPO entra em cena)

**Recompensa implícita**:
A função de recompensa que o DPO mostra estar matematicamente implicada por uma policy e um modelo de referência, sem nunca treinar um reward model separado para calculá-la.
_Evite_: reward model (todo o argumento do DPO é que ele não precisa de um separado; confundir os dois apaga a distinção que a etapa 5 existe para ensinar)

**Penalidade de KL**:
Um termo somado a um objetivo de RL que penaliza a policy treinada por divergir da distribuição de saída de um modelo de referência fixo, evitando que a otimização contra um reward model produza texto degenerado.
_Evite_: regularização (correto, mas genérico; use o nome da penalidade específica quando o RLHF entra em cena)

**Loss masking**:
Zerar a loss de treinamento nos tokens que o modelo não deve aprender a produzir, como um prompt ou uma mensagem de sistema, de modo que as atualizações de gradiente venham apenas dos tokens que o modelo deve gerar.
_Evite_: prompt masking (o mascaramento se aplica a mais do que o prompt, incluindo qualquer turno que não seja do assistente em um exemplo de várias voltas)

**Par de preferência**:
Duas completions para o mesmo prompt, uma marcada como preferida em relação à outra, a unidade de dados com que treinam tanto a modelagem de recompensa quanto o DPO.
_Evite_: comparação (usada em toda a literatura para a mesma coisa; este workspace padroniza em par de preferência)

**Reward hacking**:
Uma policy que encontra um jeito de pontuar bem contra um reward model ou um sinal de recompensa verificável sem produzir de fato o comportamento que a recompensa pretendia medir.
_Evite_: gaming, overoptimization (ambos apontam para a mesma falha; este workspace usa reward hacking como o termo único em todo lugar)

**RLAIF**:
Reinforcement learning from AI feedback: rótulos de preferência ou um sinal de recompensa produzidos por um modelo em vez de por um humano, usados no lugar do RLHF ou junto com ele.
_Evite_: autoaperfeiçoamento (RLAIF é um método específico de rotulagem; autoaperfeiçoamento é uma alegação mais ampla e vaga sobre o que o resultado é)

**Recompensa verificável**:
Um sinal de recompensa calculado por um verificador determinístico, como o resultado de um teste unitário ou uma resposta numérica final que confere, em vez de por um reward model aprendido.
_Evite_: ground truth (ground truth é a resposta contra a qual se verifica; recompensa verificável é o sinal derivado dessa verificação)
