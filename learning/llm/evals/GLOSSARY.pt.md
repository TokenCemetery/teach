---
title: "Glossário"
description: "Termos canônicos de evals"
type: glossary
---

# Glossário de Evals

Termos canônicos para provar se uma mudança no modelo ajudou e para defender que um número realmente reflete isso.

## Termos

**Diretriz de anotação**:
Uma definição escrita de cada categoria de avaliação, com exemplos concretos de casos limítrofes e de como foram resolvidos, entregue a cada avaliador humano antes de ele começar. Uma concordância baixa entre avaliadores muitas vezes sinaliza uma diretriz ausente ou ambígua, e não avaliadores pouco confiáveis.
_Evite_: rubrica de avaliação (usada como sinônimo em outros lugares; este workspace usa "diretriz de anotação" como termo)

**Correção de citações**:
Se a passagem específica citada para uma afirmação de fato sustenta essa afirmação, uma verificação por citação, mais rigorosa que a fidelidade. Uma afirmação pode ser fiel (fundamentada em algum ponto do conjunto recuperado) e mesmo assim ser atribuída à citação errada, ou a nenhuma.
_Evite_: fidelidade (uma verificação relacionada, porém separada; a fidelidade pergunta se uma afirmação é sustentada pelo contexto recuperado, e a correção de citações pergunta se a fonte específica citada de fato a sustenta)

**Kappa de Cohen**:
Uma estatística que mede a concordância entre dois avaliadores depois de corrigir a concordância esperada apenas pelo acaso: `κ = (p_o − p_e) / (1 − p_e)`. Um kappa de 0 significa que não é melhor que o acaso; um kappa pode ser negativo. Sabidamente subestima a concordância quando uma categoria de avaliação é muito mais rara que as outras.
_Evite_: concordância percentual (o número bruto, sem correção; o kappa é especificamente a versão corrigida pelo acaso, e os dois podem contar histórias diferentes)

**Contaminação de dados**:
Dados de eval, ou uma paráfrase próxima deles, acabarem dentro dos dados de treinamento de um modelo (tipicamente no pré-treinamento, via um benchmark raspado para dentro de dados de web-crawl), ou um modelo ser ajustado iterativamente contra o mesmo conjunto de eval até deixar de medir a habilidade de fundo.
_Evite_: vazamento, trapaça

**Drift**:
A relação do mundo real entre features e resultados mudando ao longo do tempo, de modo que um modelo ou eval construído sobre dados mais antigos deixa progressivamente de corresponder à realidade atual. É especificamente o que uma grande diferença entre dados held-out e dados mais recentes ("do dia seguinte") indica; uma diferença entre resultados offline e ao vivo sobre exatamente a mesma entrada é outro problema, um erro de engenharia, e não drift.
_Evite_: training-serving skew (um termo mais amplo que cobre qualquer discrepância entre treino e serving; drift é especificamente o caso baseado no tempo, em que o mundo real mudou por baixo do modelo)

**Fidelidade (groundedness)**:
Se cada afirmação de uma resposta gerada é de fato sustentada pelo contexto recuperado em que deveria se apoiar, em vez de inventada, contradita ou enfeitada com um detalhe sem sustentação. Uma verificação no nível da afirmação: uma resposta quase toda fiel ainda pode esconder uma afirmação sem sustentação.
_Evite_: correção de citações (uma verificação mais rigorosa e separada, sobre se a passagem específica citada para uma afirmação é a que de fato a sustenta, distinta de a afirmação estar ou não fundamentada)

**Métrica guardrail**:
Uma métrica que um experimento ou um sistema em produção não está tentando otimizar, acompanhada especificamente para pegar uma mudança que a degrada em silêncio enquanto outra métrica (o OEC) está sendo melhorada. Reportar o ganho de um OEC sem uma métrica guardrail verificada ao lado pode esconder uma regressão real.
_Evite_: OEC (uma métrica guardrail explicitamente não está sendo otimizada; misturar as duas anula o propósito de acompanhar cada uma separadamente)

**Dados held-out**:
Exemplos de eval, ou paráfrases próximas deles, que o modelo sendo avaliado nunca viu durante o treinamento ou o fine-tuning. Uma pontuação só é informativa quando os dados por trás dela são held-out.
_Evite_: conjunto de teste (ambíguo com uma divisão de pipeline de treinamento), dados não vistos

**OEC (Overall Evaluation Criterion)**:
A métrica específica, ou a pequena combinação ponderada, que um experimento realmente tenta mover. Um bom candidato a OEC é ao mesmo tempo movível (sensível o bastante para se deslocar dentro de um experimento viável) e causalmente ligado ao resultado que de fato importa, e não apenas correlacionado com ele.
_Evite_: qualquer métrica que seja fácil de mover mas sem ligação causal com o resultado real (o próprio exemplo de Kohavi: "fotos visualizadas" move com facilidade, mas tem pouco efeito causal sobre a receita)

**Recusa excessiva**:
Um modelo recusar um prompt que na verdade é seguro, tipicamente porque ele se parece com um prompt inseguro na formulação ou toca um assunto que soa sensível sem ser danoso. Um modo de falha genuinamente diferente de um jailbreak, e que um eval de red-team (só com prompts inseguros) não consegue detectar.
_Evite_: recusa falsa (usada como sinônimo em algumas fontes; este workspace padroniza em "recusa excessiva")

**Red-teaming**:
Construir de propósito entradas desenhadas para fazer um modelo produzir uma saída insegura, seja por um testador humano ou por um método automatizado de geração de ataques, e depois medir com que frequência essas entradas têm sucesso (um jailbreak) contra um dado modelo e suas defesas.
_Evite_: reportar apenas a taxa de sucesso de ataque como "o eval de segurança"; ela não mede nada sobre a recusa excessiva, um modo de falha distinto que precisa de seu próprio conjunto de testes

**Saturação**:
Um benchmark chegar a um teto em que os modelos pontuam quase perfeitamente nele e continuam falhando no mesmo tipo de tarefa em uso real, porque o benchmark deixou de medir a habilidade de fundo e passou a medir a familiaridade com o próprio benchmark.
_Evite_: contaminação de dados (uma causa relacionada, porém distinta; a saturação também pode resultar de ajuste legítimo e extenso contra um benchmark ao longo do tempo, e não apenas de as perguntas do benchmark vazarem para os dados de treinamento)

**Divulgação seletiva**:
Testar várias variantes privadas e não lançadas de um modelo contra um benchmark ou arena e reportar publicamente apenas a de melhor pontuação. Transforma um leaderboard em um alvo de otimização (Lei de Goodhart), e não em uma medição neutra, e cria uma lacuna entre a pontuação que um leaderboard reporta e a versão do modelo de fato lançada.
_Evite_: contaminação de dados (outro vetor de manipulação; a divulgação seletiva é uma prática de reporte, não dados de eval vazando para o treinamento)

**Latência de cauda**:
A fração mais lenta das requisições (comumente reportada como p95 ou p99), em oposição à média. Uma latência média inalterada pode esconder uma cauda sensivelmente pior e, em escala, uma requisição que se espalha por muitas chamadas de backend só termina quando todas terminam, o que faz da cauda o que de fato decide o tempo de resposta no mundo real.
_Evite_: latência média (um agregado que pode ficar estável enquanto a cauda, que domina a experiência real do usuário, piora sensivelmente)

**Sucesso na tarefa**:
Comparar o estado final real da trajetória de um agente com um estado-alvo anotado, creditando qualquer sequência de ações que chegue ao resultado correto, e não apenas uma sequência de referência predeterminada. Mais fiel que a acurácia por passo, que só consegue creditar a única trajetória que recebeu.
_Evite_: acurácia por passo (uma medição mais estreita e frágil: comparar cada ação com uma trajetória de referência, o que penaliza indevidamente um caminho diferente e igualmente válido para o mesmo resultado correto)

**Training-serving skew**:
Qualquer discrepância entre o desempenho offline de um modelo (de treino ou held-out) e seu desempenho ao vivo, em produção. A orientação do próprio Google divide isso em comparações distintas com causas distintas; uma discrepância sobre a entrada idêntica entre uma pontuação offline e um resultado ao vivo indica especificamente um erro de engenharia, e não drift nem um problema de modelagem.
_Evite_: drift (o caso mais estreito, baseado no tempo, em que o mundo real mudou desde o treinamento; nem toda discrepância offline/online é drift)

**Trajetória**:
A sequência completa de chamadas de ferramenta, decisões intermediárias e turnos que um agente produz ao trabalhar uma tarefa, em oposição à saída única que um eval por resposta pontua. Uma métrica por resposta não tem onde se apoiar aqui, e é por isso que a avaliação de agentes precisa de suas próprias métricas.
_Evite_: resposta (estreito demais; uma trajetória é o processo inteiro, de vários passos e muitas vezes de vários turnos, e não qualquer saída isolada dentro dele)
