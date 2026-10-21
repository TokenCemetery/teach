---
title: "Destilação"
description: "Destile um modelo grande em um menor e defenda o resultado: soft targets, losses de logits e em nível de sequência, dados sintéticos, treinamento on-policy e o que o aluno perdeu"
type: topic
---

# Aprendizado: Destilação

Treine um modelo menor para fazer o que um maior faz, aprendendo com as saídas do modelo maior, e saiba o que cada forma de destilação transfere e o que ela não consegue transferir. Termine capaz de escolher entre destilar, quantizar e treinar diretamente um modelo pequeno para uma dada tarefa e um dado orçamento, medir com honestidade o que o aluno perdeu e revisar a alegação de outra pessoa de que um modelo destilado "se iguala ao professor".

**Última lição:** [27. Quando a resposta de sempre está errada](lessons/0027-when-the-usual-answer-is-wrong.md)

## O sucesso se parece com isto

- Explicar por que os soft targets de um professor carregam mais sinal de treinamento do que os hard labels e definir a temperatura e os pesos da loss de uma execução de destilação.
- Escrever a loss de destilação em nível de token para um LLM, escolher entre forward e reverse KL e dizer quando uma incompatibilidade de tokenizer descarta a destilação de logits.
- Destilar em nível de sequência ou a partir dos dados gerados por um professor e dizer o que cada abordagem transfere que a outra não transfere.
- Construir um conjunto sintético de destilação filtrado por qualidade e verificar se a licença e os termos do professor permitem treinar com as suas saídas.
- Explicar o exposure bias e dizer quando a destilação on-policy compensa o seu custo em relação a treinar com saídas fixas do professor.
- Prever o que um aluno vai e o que não vai herdar do seu professor, incluindo a capacidade que ele não consegue absorver e os traços que ninguém pretendia transmitir.
- Escolher um tamanho de aluno e um volume de dados contando o próprio custo do professor no orçamento.
- Medir o que um aluno perdeu em relação ao seu professor e em relação a um modelo do mesmo tamanho treinado sem um professor.
- Escolher entre destilar, quantizar e fazer fine-tuning direto de um modelo pequeno, revisar a alegação de destilação de outra pessoa apontando o que ela esconde, substituir um modelo de que outros dependem por um aluno e dizer quando a resposta de sempre é a errada.

## Restrições

- Pressupõe familiaridade com a leitura de Python e PyTorch e com o que são a loss de cross-entropy, um softmax e um loop de treinamento. Não pressupõe conhecimento prévio de destilação, nem de reinforcement learning além da ideia de amostrar de um modelo.
- Baseada em artigos científicos e relatórios de modelos. Quando um número é o resultado de um único artigo no seu próprio cenário, a lição diz isso, porque os resultados de destilação dependem muito do professor, do aluno e dos dados.
- A prática roda em um laptop nas etapas 1 e 2, com um classificador pequeno o bastante para uma CPU. As repetições posteriores destilam entre dois modelos abertos pequenos, para o que um notebook com GPU gratuita é suficiente.

## Fora do escopo

- Destilar um modelo de raciocínio por fine-tuning em suas longas chains of thought: veja [`llm/post-training`](../../llm/post-training/), lição 0014. Aquela lição continua sendo o caso do modelo de raciocínio; esta trilha ensina a destilação em geral e aponta para ela em vez de repeti-la.
- Executar o supervised fine-tuning por meio de adapters LoRA ou QLoRA: veja [`llm/finetuning`](../../llm/finetuning/). Esta trilha é dona do objetivo e dos dados da destilação; como o treinamento é aplicado a menos parâmetros fica lá.
- Executar uma execução de pré-treinamento: veja [`llm/pretraining`](../../llm/pretraining/). A destilação como sinal de pré-treinamento é ensinada aqui como uma escolha de loss e de dados (lição 0007), e não como uma execução de pré-treinamento.
- Construir um eval: veja [`llm/evals`](../../llm/evals/) e a sua [folha de go/no-go](../../llm/evals/reference/go-no-go.md). Esta trilha usa um eval para comparar um aluno com o seu professor e não reensina como construir um.
- Encolher um modelo reduzindo a sua precisão: veja [`llm/quantization`](../../llm/quantization/). Esta trilha é a outra forma de encolher um modelo, com menos parâmetros, e a comparação entre as duas faz parte da etapa 9.
- A poda (pruning) como método por si só. A lição 0007 a mostra combinada com a destilação no Minitron e ensina apenas a metade da destilação.

## O arco

Nove etapas, desde por que um modelo pequeno consegue aprender com um grande até o julgamento para revisar a destilação de outra pessoa. Uma etapa leva várias lições e as fronteiras são flexíveis; o que torna uma etapa concluída é a capacidade, não a contagem de lições.

| Etapa | Lições | Cobre | Concluída quando |
|---|---|---|---|
| 1. Por que a destilação funciona | 0001 a 0003 | Professor e aluno, soft targets e o que eles carregam, temperatura e a loss combinada | Consegue dizer por que os soft targets ensinam mais do que os hard labels e definir a temperatura |
| 2. Destilação de logits para LLMs | 0004 a 0007 | Destilação em nível de token, forward e reverse KL, a restrição do tokenizer compartilhado, a destilação como sinal de pré-treinamento | Consegue escrever a loss em nível de token e dizer quando ela não pode ser usada |
| 3. Destilação em nível de sequência | 0008 a 0009 | Treinar nas saídas decodificadas do professor e escolher entre o nível de token e o de sequência | Consegue dizer o que cada nível transfere e escolher um a partir do que o professor expõe |
| 4. Destilação com dados sintéticos | 0010 a 0013 | Dados de instrução gerados, rationales e traces de explicação, filtragem, licenciamento e termos | Consegue construir um conjunto de destilação filtrado e verificar que o seu uso é permitido |
| 5. Destilação on-policy | 0014 a 0016 | Exposure bias, GKD e MiniLLM, o que o treinamento on-policy custa e o que ele traz | Consegue dizer quando a destilação on-policy compensa o seu custo |
| 6. O que o aluno herda | 0017 a 0019 | Fidelidade versus generalização, a lacuna de imitação, a lacuna de capacidade, traços transmitidos sem intenção | Consegue prever o que um aluno vai e o que não vai absorver do seu professor |
| 7. Dimensionamento | 0020 a 0021 | Leis de escala da destilação, volume de dados, o custo do professor no orçamento | Consegue escolher um tamanho de aluno e um volume de dados e defender o compute |
| 8. Medindo o que se perdeu | 0022 a 0023 | Concordância com o professor versus qualidade na tarefa, baselines, tarefas held-out, contaminação | Consegue medir o que um aluno perdeu e defender o número |
| 9. Julgamento | 0024 a 0027 | Destilar, quantizar ou fazer fine-tuning de um modelo pequeno, revisar uma alegação, substituir um modelo de que outros dependem, quando a resposta de sempre está errada | Tem a confiança para decidir sobre uma destilação e explicá-la a outra pessoa |

## Lições

Siga estas na ordem.

| # | Lição | Ensina |
|---|---|---|
| [0001](lessons/0001-what-distillation-buys.md) | O que a destilação oferece | Um aluno pequeno treinado para imitar um professor grande, e por que a imitação pode superar treinar o aluno só com os rótulos |
| [0002](lessons/0002-soft-targets.md) | Soft targets | O que as probabilidades que um professor dá às respostas erradas carregam, e por que elas são um sinal de treinamento mais rico do que um hard label |
| [0003](lessons/0003-temperature.md) | Temperatura | Suavizar as duas distribuições com uma temperatura, a correção por T ao quadrado e misturar a loss do hard label |
| [0004](lessons/0004-token-level-distillation.md) | Destilação em nível de token | Igualar a distribuição de próximo token do professor em cada posição de uma sequência |
| [0005](lessons/0005-forward-and-reverse-kl.md) | Forward e reverse KL | Por que o forward KL espalha o aluno por todos os modos do professor e o reverse KL o faz se comprometer com um só |
| [0006](lessons/0006-the-tokenizer-constraint.md) | A restrição do tokenizer | Por que a destilação de logits precisa de um vocabulário compartilhado, e o que os métodos entre tokenizers sacrificam |
| [0007](lessons/0007-distilling-during-pretraining.md) | Destilando durante o pré-treinamento | Como o Gemma 2 e o Minitron usaram a distribuição de um professor como sinal de treinamento em escala, e o que custa armazenar logits |
| [0008](lessons/0008-sequence-level-distillation.md) | Destilação em nível de sequência | Treinar o aluno nas saídas decodificadas do professor em vez de nas suas distribuições |
| [0009](lessons/0009-token-or-sequence.md) | Token ou sequência | O que cada nível transfere, combiná-los e escolher conforme o professor exponha logits ou apenas texto |
| [0010](lessons/0010-distilling-from-generated-data.md) | Destilando a partir de dados gerados | Construir um conjunto de instruções a partir das gerações de um professor, como fizeram o Self-Instruct e o Alpaca |
| [0011](lessons/0011-rationales-and-explanation-traces.md) | Rationales e traces de explicação | Treinar no raciocínio do professor além das suas respostas, como fizeram o Distilling Step-by-Step e o Orca |
| [0012](lessons/0012-filtering-synthetic-data.md) | Filtrando dados sintéticos | Verificar, filtrar e deduplicar dados gerados antes de treinar com eles, porque volume não corrige exemplos ruins |
| [0013](lessons/0013-licensing-and-terms.md) | Licenciamento e termos | O que os termos de um provedor e a licença de um modelo aberto permitem fazer com as suas saídas |
| [0014](lessons/0014-exposure-bias.md) | Exposure bias | Por que um aluno treinado em prefixos do professor encontra os próprios erros na inferência sem ter treinado neles |
| [0015](lessons/0015-gkd-and-minillm.md) | GKD e MiniLLM | Amostrar do aluno e pontuar com o professor, e as escolhas de divergência e de mistura que vêm junto |
| [0016](lessons/0016-on-policy-distillation-in-practice.md) | Destilação on-policy na prática | O que a destilação on-policy custa por passo, o que ela traz e como o Qwen3 a usou nos seus modelos pequenos |
| [0017](lessons/0017-fidelity-and-generalization.md) | Fidelidade e generalização | Por que um aluno que generaliza bem ainda pode discordar do seu professor, e de qual das duas você precisa |
| [0018](lessons/0018-the-imitation-gap.md) | A lacuna de imitação | Por que imitar um modelo mais forte copia o seu estilo muito mais rápido do que a sua capacidade |
| [0019](lessons/0019-capacity-gap-and-hidden-traits.md) | Lacuna de capacidade e traços ocultos | Por que um professor maior nem sempre é um professor melhor, e o que pode passar para um aluno sem que ninguém pretendesse |
| [0020](lessons/0020-choosing-student-size.md) | Escolhendo o tamanho do aluno | O que as leis de escala da destilação dizem sobre quando destilar supera treinar o aluno diretamente |
| [0021](lessons/0021-data-volume-and-teacher-cost.md) | Volume de dados e custo do professor | Contar a inferência do professor no orçamento e decidir quantos dados de destilação bastam |
| [0022](lessons/0022-student-against-teacher.md) | Aluno contra professor | Medir a concordância com o professor separadamente da qualidade na tarefa, uma capacidade por vez |
| [0023](lessons/0023-an-honest-distillation-eval.md) | Um eval honesto de destilação | Os baselines, as tarefas held-out e as verificações de contaminação que tornam defensável um número de "se iguala ao professor" |
| [0024](lessons/0024-distill-quantize-or-fine-tune.md) | Destilar, quantizar ou fazer fine-tuning | Escolher entre menos parâmetros, menos bits e treinar diretamente um modelo pequeno, a partir da tarefa e do orçamento |
| [0025](lessons/0025-reviewing-a-distillation-claim.md) | Revisando uma alegação de destilação | Revisar "o nosso modelo pequeno se iguala ao grande" apontando o que a medição escondeu |
| [0026](lessons/0026-replacing-a-model-others-depend-on.md) | Substituindo um modelo de que outros dependem | Colocar um aluno no lugar do seu professor sem prejudicar quem depende do comportamento dele |
| [0027](lessons/0027-when-the-usual-answer-is-wrong.md) | Quando a resposta de sempre está errada | Reconhecer quando a destilação é a escolha errada e resolver uma alegação contestada a partir da fonte primária |

## Referência

- [Glossário](GLOSSARY.md): termos canônicos deste tópico
- [Recursos](RESOURCES.md): fontes confiáveis, cada uma anotada com o que cobre
- [Losses de Destilação](reference/distillation-losses.md): soft targets, temperatura, a loss combinada, o KL em nível de token nas duas direções e a restrição do tokenizer, das etapas 1 e 2
- [Sequência e Dados Sintéticos](reference/sequence-and-synthetic-data.md): destilação em nível de sequência, dados gerados, rationales, filtragem e as questões de licença, das etapas 3 e 4
- [Destilação On-Policy](reference/on-policy-distillation.md): exposure bias, GKD e MiniLLM lado a lado, e quando o treinamento on-policy compensa, da etapa 5
- [O Que o Aluno Herda](reference/what-the-student-inherits.md): fidelidade, a lacuna de imitação, a lacuna de capacidade e os traços não intencionais, da etapa 6
- [Dimensionamento e Medição](reference/sizing-and-measuring.md): escolher o tamanho do aluno e o volume de dados com o custo do professor, e um eval honesto de aluno contra professor, das etapas 7 e 8
- [Checklist de Revisão de Destilação](reference/distillation-review-checklist.md): escolher entre destilar, quantizar e fazer fine-tuning, e as perguntas a fazer sobre a alegação de destilação de outra pessoa, da etapa 9

## Como isto funciona

Cada lição é curta e autocontida. Os gabaritos ficam recolhidos: primeiro lembre, depois abra. A prática no mundo real importa mais do que a leitura, e espaçá-la é o ponto. Tudo o que ainda estiver confuso no fim de uma lição vale ser perseguido até a fonte primária antes de seguir adiante.
