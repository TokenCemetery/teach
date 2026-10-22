---
title: "Losses de Destilação"
description: "Soft targets, temperatura, a loss combinada, a loss em nível de token, forward e reverse KL, a restrição do tokenizer e o custo de armazenar logits"
type: reference
---

# Losses de Destilação: Etapas 1 e 2 para Consulta

As etapas 1 e 2 condensadas para consulta. As [Lições 1 a 3](../lessons/0001-what-distillation-buys.md) cobrem soft targets e temperatura, a [lição 4](../lessons/0004-token-level-distillation.md) a loss em nível de token, a [lição 5](../lessons/0005-forward-and-reverse-kl.md) a direção da divergência, a [lição 6](../lessons/0006-the-tokenizer-constraint.md) a restrição do tokenizer e a [lição 7](../lessons/0007-distilling-during-pretraining.md) o custo da distribuição do professor em escala.

## Soft targets e temperatura

| Termo | Definição | Fonte |
|---|---|---|
| Soft targets | As probabilidades do professor sobre todas as classes, usadas como alvo no lugar do hard label ou ao lado dele | Hinton et al., 2015, seção 1 |
| Softmax com temperatura | q_i = exp(z_i / T) / sum_j exp(z_j / T). T = 1 é o softmax normal, um T maior dá uma distribuição mais suave | Hinton et al., equação 1 |
| Onde T é usado | O mesmo T alto para o professor e o aluno durante o treinamento. Depois, o aluno roda com T = 1 | Hinton et al., seção 2 |
| Gradiente com temperatura T | dC/dz_i = (1/T)(q_i - p_i). Para T grande e logits de média zero é cerca de (1/(N T^2))(z_i - v_i), então igualar logits é um caso especial | Hinton et al., seção 2.1 |
| O fator T ao quadrado | Os gradientes dos soft targets escalam como 1/T^2, então multiplique a loss soft por T^2 ao combiná-la com a loss hard | Hinton et al., seção 2 |

O fator em uma execução, com os logits `[9, 4, 2, 0, -4]` contra `[6, 5, 0, 1, -2]`: a maior entrada do gradiente é 0,2663 com T = 1 e 0,0017 com T = 20, e multiplicada por T ao quadrado ela fica entre 0,64 e 0,84 de T = 2 a T = 20 ([lição 3](../lessons/0003-temperature.md)).

## A loss combinada

```text
loss = lambda * T^2 * CE(teacher at T, student at T) + (1 - lambda) * CE(label, student at 1)
```

A notação é desta trilha. Hinton et al. descrevem uma média ponderada das duas cross-entropies e encontraram os melhores resultados, em geral, com um peso consideravelmente menor na do hard label.

| Configuração | Valor | Fonte e escopo |
|---|---|---|
| Fala, peso relativo no termo hard | 0,5 | Hinton et al., seção 4.1, um modelo acústico |
| Fala, temperaturas testadas | 1, 2, 5, 10 | Hinton et al., seção 4.1 |
| MNIST, aluno de 800 unidades, soft targets com T = 20 | 74 erros de teste, contra 146 sozinho e 67 do professor | Hinton et al., seção 3 |
| MNIST, aluno de 30 unidades, melhores temperaturas | 2,5 a 4 | Hinton et al., seção 3 |
| Pesos de mistura em nível de palavra de Kim e Rush testados | 0,5 e 0,9, 0,5 melhor | Kim e Rush, 2016, seção 4 |
| Retreinamento de LLM podado, temperaturas testadas | 0,1, 0,5, 1,0, 3,0, melhor em 1,0 | Muralidharan et al., 2024, apêndice A.3 |
| Pré-treinamento de LLM, temperaturas testadas | 0,5 a 10, melhor em 1 em todas as escalas | Busbridge et al., 2025, apêndice G.2 |
| Retreinamento de LLM podado, mistura de losses | A loss de logits sozinha melhor do que misturar a loss de language modeling | Muralidharan et al., 2024, seção 4 |

Cada linha é um artigo no seu próprio cenário. As duas linhas de temperatura de LLM discordam das de classificadores, então varra T, incluindo 1, no seu próprio par.

## A loss em nível de token

| Item | Escolha |
|---|---|
| Formatos dos logits | Aluno e professor, cada um (batch, positions, vocab) |
| Eixo da divergência | O último, o vocabulário, dando (batch, positions) |
| Prefixo | Uma sequência fixa, texto humano ou do professor, fornecida aos dois modelos (teacher forcing) |
| Professor | Forward pass com os gradientes desligados |
| Redução | Kim e Rush somam sobre as posições. GKD e Minitron dividem pelo comprimento. Mascare o padding e divida pela soma da máscara |
| Temperatura | Divida os dois logits por T antes do log-softmax, multiplique a loss por T^2 se misturada com um termo hard |

```python
import torch.nn.functional as F

def token_kd_loss(student_logits, teacher_logits, mask, T=1.0):
    s = F.log_softmax(student_logits / T, dim=-1)
    t = F.log_softmax(teacher_logits / T, dim=-1)
    kl = (t.exp() * (t - s)).sum(dim=-1)
    return (kl * mask).sum() / mask.sum()
```

A cross-entropy contra o professor e o forward KL diferem pela entropia do professor, uma constante para o aluno, então têm os mesmos gradientes. O Gemma 2 escreve a soma de -P_T(x | x_c) log P_S(x | x_c) (seção 3.2).

## Forward e reverse KL

| | Forward KL | Reverse KL |
|---|---|---|
| Expressão | KL(p \|\| q) = sum p log(p / q) | KL(q \|\| p) = sum q log(q / p) |
| p é o professor, q o aluno | Ponderado pelo professor | Ponderado pelo aluno |
| Pune | Um aluno que dá pouca massa onde o professor tem muita | Um aluno que dá massa onde o professor tem pouca |
| Comportamento | Cobre modos, espalha por todos os modos | Busca modos, se compromete com um |
| No brinquedo da lição 5 | Prefere o aluno espalhado, 0,595 contra 1,572 | Prefere o aluno comprometido, 0,623 contra 1,273 |

| Fonte | Achado | Escopo |
|---|---|---|
| MiniLLM, Gu et al., 2023 | Reverse KL para destilação generativa, já que o forward KL dá massa às regiões vazias do professor | Seguimento de instruções, policy gradient em amostras do aluno |
| GKD, Agarwal et al., 2023 | A melhor divergência depende da tarefa. A JSD(beta) generalizada interpola, parecida com o forward perto de 0, parecida com o reverse perto de 1. Reverse KL muito melhor do que forward no instruction tuning do FLAN | Alunos T5, XSum, WMT, GSM8K, FLAN |
| Minitron, Muralidharan et al., 2024 | Forward KLD melhor: loss de LM 2,155 contra 2,665 do reverse em um 8B podado em profundidade | Retreinamento de base models podados |

O `GKDConfig` do TRL expõe a escolha como `beta`: 0.0 é a divergência KL, 1.0 o KL inverso, padrão 0.5.

## A restrição do tokenizer

| Situação | O que funciona | O que custa |
|---|---|---|
| Mesmo tokenizer | Loss em nível de token | Precisa dos logits do professor |
| Aluno construído a partir do professor (DistilBERT, Minitron) | Loss em nível de token | Aluno restrito ao design do professor |
| Tokenizers diferentes, logits disponíveis | Loss ULD, ou o trainer GOLD do TRL | Perde a identidade do token no termo de distância, suposição de custo uniforme, alinhamento de posições grosseiro |
| Apenas o texto do professor | Treinar nas suas sequências geradas (etapa 3) | O aluno nunca vê as distribuições do professor |

ULD (Boizard et al., 2024): L = soma sobre t de CE(t) + lambda * W1(aluno, professor), lambda 1,5, com W1 como a soma das diferenças absolutas dos vetores de probabilidade ordenados em ordem decrescente (seção 3). Um aluno que põe a sua massa no token errado pode pontuar 0 no W1, então a cross-entropy do token gold carrega o sinal de identidade.

TRL, como lido para a lição 6: o `GKDTrainer` recebe um único tokenizer como `processing_class` e não tem argumento de tokenizer do professor. O GOLD é documentado como suportando tokenizers diferentes, com `use_uld_loss=True` e `teacher_tokenizer_name_or_path`, e está em `trl.experimental`.

## O custo de armazenar os logits do professor

Aritmética da [lição 7](../lessons/0007-distilling-during-pretraining.md), com o vocabulário de 256.128 do Gemma 2 (Tabela 1). Os 2 bytes por probabilidade e o k = 256 com um índice de 4 bytes são suposições, não números do relatório.

| Quantidade | Valor |
|---|---|
| Distribuição completa por token, bf16 | 512.256 bytes |
| Distribuição completa por sequência de 8.192 tokens | 4,20 GB |
| Completa para 2T tokens (a execução de 2B) | 1,02 EB |
| Completa para 8T tokens (a execução de 9B) | 4,10 EB |
| Top-256 por token, 6 bytes por entrada | 1.536 bytes, 333,5 vezes menor |
| Top-256 para 2T tokens | 3,07 PB |
| Top-256 para 8T tokens | 12,29 PB |

O relatório do Gemma 2 não descreve como a distribuição do professor foi fornecida. O Minitron calcula o professor em um forward pass junto com o treinamento e compara execuções com compute igual. O teste de top-K do Minitron encontrou uma queda significativa de acurácia para K até 100 e nenhum ganho ao truncar em K maiores, em um cenário de retreinamento de modelo podado.

## Para ler mais

- [Recursos](../RESOURCES.md)
- [Glossário](../GLOSSARY.md)
