---
title: "Glossário"
description: "Termos canônicos da destilação de conhecimento de LLMs"
type: glossary
---

# Glossário de Destilação

Termos canônicos para treinar um modelo menor a partir das saídas de um maior, as losses e os dados que carregam o sinal e a forma de julgar o resultado. Neste workspace, "destilação" sempre significa destilação de conhecimento de um modelo professor para um modelo aluno; nunca significa destilação de dataset nem destilar um prompt.

## Termos

**Aluno** (_student_):
O modelo que está sendo treinado em uma destilação, geralmente menor ou mais barato de executar do que o professor.
_Evite_: modelo destilado antes de o treinamento terminar, modelo filho

**Aprendizado subliminar**:
Um aluno adquirir uma característica do seu professor a partir de dados semanticamente não relacionados a essa característica, observado por Cloud et al. quando os dois compartilham o mesmo base model.
_Evite_: destilação oculta, envenenamento de dados (esse é deliberado)

**Baseline supervisionado**:
Um modelo do tamanho do aluno treinado sem destilação, com os mesmos dados ou o mesmo compute, usado como a comparação que mostra se a destilação causou um resultado.
_Evite_: modelo de controle (amplo demais), modelo simples

**Beam search**:
Um método de decodificação que mantém, a cada passo, as poucas sequências parciais de maior pontuação e devolve a melhor sequência completa, como aproximação da sequência mais provável.
_Evite_: greedy search (que é o beam de tamanho 1), decodificação best-first

**Concordância top-1**:
A fração das entradas em que a resposta de maior probabilidade do aluno é a mesma do professor, uma das duas métricas de fidelidade em Stanton et al.
_Evite_: acurácia (essa é em relação à resposta correta), taxa de coincidência

**Dados sintéticos**:
Exemplos de treinamento gerados por um modelo em vez de escritos por pessoas. Neste workspace, significa dados gerados pelo professor para o aluno.
_Evite_: dados falsos, dados aumentados (o aumento de dados transforma exemplos já existentes)

**Descontaminação**:
Remover dos dados de treinamento os exemplos que coincidem com um conjunto de avaliação ou se parecem muito com ele, para que a pontuação de um benchmark não meça itens memorizados.
_Evite_: limpeza (ampla demais), deduplicação (que remove repetições dentro do conjunto de treinamento)

**Destilação**:
Treinar um modelo aluno para reproduzir o comportamento de um modelo professor, usando as distribuições de saída ou o texto gerado pelo professor como sinal de treinamento.
_Evite_: compressão (ampla demais), cópia de modelo

**Destilação em nível de sequência**:
Destilação em que o aluno é treinado com cross-entropy comum sobre sequências inteiras que o professor decodificou, e não sobre as distribuições por token do professor.
_Evite_: destilação hard, destilação black-box (que também cobre a destilação a partir de dados gerados)

**Destilação em nível de token**:
Destilação de logits aplicada a cada posição de uma sequência, minimizando uma divergência entre as distribuições de próximo token do professor e do aluno.
_Evite_: destilação em nível de palavra (o nome do artigo original), KD por token

**Destilação de logits**:
Destilação cujo sinal de treinamento é a distribuição de saída completa do professor em cada posição, o que exige acesso aos logits do professor e um vocabulário compartilhado.
_Evite_: destilação white-box (apelido aceito, mas use um só termo), destilação soft

**Destilação entre tokenizers**:
Destilação de logits entre um professor e um aluno cujos vocabulários diferem, feita alinhando ou comparando suas distribuições sem um índice de tokens compartilhado.
_Evite_: destilação sem tokenizer, transferência de vocabulário

**Destilação off-policy**:
Destilação sobre sequências que o aluno não gerou: dados humanos ou as próprias saídas do professor, fixados antes do treinamento.
_Evite_: destilação offline, destilação supervisionada

**Destilação on-policy**:
Destilação sobre sequências que o aluno gera durante o treinamento, com o professor pontuando cada token que o aluno escolheu, de modo que o aluno treina com os próprios erros.
_Evite_: destilação online (também usada para professores treinados junto com o aluno), autodestilação

**Divergência KL** (_KL divergence_):
Para duas distribuições P e Q sobre os mesmos tokens, a soma sobre os tokens de P log(P / Q): uma medida de quão distante Q está de P que não é simétrica. Suas duas direções na destilação são o forward KL e o reverse KL.
_Evite_: distância KL, entropia relativa sem apresentar o termo

**Exposure bias**:
A incompatibilidade entre treinar em prefixos que outra pessoa escreveu e gerar a partir de prefixos que o próprio modelo escreveu, de modo que seus primeiros erros o levam a estados em que ele nunca treinou.
_Evite_: incompatibilidade entre treino e teste (ampla demais), drift

**Fidelidade**:
O quanto as previsões de um aluno concordam com as do seu professor, medido nas mesmas entradas, em oposição a quão bem cada um se sai na tarefa.
_Evite_: acurácia, faithfulness

**Forward KL**:
A divergência KL(professor ‖ aluno), calculada como média sob a distribuição do professor, que penaliza o aluno por dar pouca probabilidade onde o professor dá muita e, por isso, o empurra a cobrir todos os modos.
_Evite_: KL que cobre modos sem nomear a direção, KL simples

**Generalized knowledge distillation**:
O método on-policy de Agarwal et al. que treina o aluno com uma mistura de sequências fixas e geradas por ele, pontuadas token a token contra o professor com uma divergência escolhida. Abreviado como GKD.
_Evite_: KD generalizado, destilação genérica

**Hard label**:
A única classe ou token correto usado como alvo de treinamento, com toda a sua probabilidade em uma só resposta.
_Evite_: ground truth (pode ser o argmax do professor), alvo one-hot sem contexto

**Lacuna de capacidade** (_capacity gap_):
A queda de qualidade do aluno que pode aparecer quando o professor é muito maior do que ele, de modo que um professor mais forte produz um aluno pior do que um mais fraco produziria.
_Evite_: professor inteligente demais, incompatibilidade de tamanho

**Lacuna de imitação** (_imitation gap_):
A distância entre o quanto um aluno soa como seu professor e o quanto da capacidade do professor ele realmente tem, que a imitação com um orçamento limitado fecha muito mais rápido no estilo do que na capacidade.
_Evite_: falsa promessa (o título do artigo, não um termo), transferência de estilo

**Lei de escala da destilação**:
Uma relação ajustada, de Busbridge et al., que prevê a cross-entropy de um aluno a partir do seu tamanho, do número de tokens de destilação e da cross-entropy do professor.
_Evite_: lei da destilação, KD scaling

**Logit**:
A pontuação bruta e não normalizada de um modelo para uma classe ou token, antes de o softmax transformar as pontuações em probabilidades.
_Evite_: score (ambíguo), log-probabilidade (essa vem depois do softmax)

**Logits top-k**:
As k maiores entradas da distribuição de saída de um professor em uma posição, guardadas com seus índices de token no lugar da linha completa do vocabulário, para reduzir o armazenamento.
_Evite_: logits esparsos, softmax truncado sem dizer o que acontece com a massa descartada

**Loss combinada**:
Uma loss de destilação que soma a cross-entropy contra os hard labels à divergência em relação aos soft targets do professor, ponderadas por um coeficiente de mistura.
_Evite_: loss híbrida, loss dupla

**Professor** (_teacher_):
O modelo cujas saídas são o sinal de treinamento em uma destilação. Ele fica fixo durante o treinamento e costuma ser maior ou mais capaz do que o aluno.
_Evite_: oráculo, modelo pai

**Professor assistente** (_teacher assistant_):
Um modelo de tamanho intermediário, destilado a partir do professor e depois usado como professor de um aluno menor, para transpor uma lacuna de capacidade.
_Evite_: professor intermediário sem apresentar o termo, modelo TA

**Rationale**:
O raciocínio intermediário que um professor escreve antes da resposta ou junto com ela, usado como alvo de treinamento extra para que o aluno aprenda como a resposta foi alcançada.
_Evite_: explicação (serve em prosa, mas não como termo), chain of thought (a técnica de prompting que o produz)

**Rejection sampling**:
Tirar vários candidatos de saída de um modelo para cada prompt e manter apenas os que passam em uma verificação, como uma resposta final correta.
_Evite_: filtragem (ampla demais), best-of-n (que mantém um único vencedor em vez de descartar por uma verificação)

**Reverse KL**:
A divergência KL(aluno ‖ professor), calculada como média sob a distribuição do aluno, que penaliza o aluno por dar probabilidade onde o professor dá pouca e, por isso, o empurra a se comprometer com um único modo.
_Evite_: KL que busca modos sem nomear a direção, KL invertido

**Soft targets**:
A distribuição de probabilidade completa do professor sobre classes ou tokens, usada como alvo de treinamento no lugar do hard label ou junto com ele.
_Evite_: soft labels (apelido aceito, mas use um só termo), dark knowledge (a informação que eles carregam, não os alvos)

**Teacher forcing**:
Fornecer a um modelo um prefixo fixo em vez de suas próprias saídas anteriores, de modo que um único forward pass produza uma distribuição de próximo token em cada posição de uma sequência.
_Evite_: decodificação com teacher forcing, free running (o oposto)

**Temperatura**:
O divisor T aplicado aos logits antes do softmax. Um T acima de 1 achata a distribuição e aumenta as probabilidades das respostas improváveis para que o aluno possa aprender com elas. Esse era o padrão da era dos classificadores; as execuções de destilação de LLMs nas fontes deste workspace encontraram T igual a 1 como o melhor.
_Evite_: temperatura de amostragem (mesma operação, finalidade diferente), suavidade
