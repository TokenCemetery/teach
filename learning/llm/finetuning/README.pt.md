---
title: "Fine-Tuning com Adapters"
description: "Decida se vale a pena fazer fine-tuning, execute, prove que funcionou e coloque em produção"
type: topic
---

# Aprendizado: Fine-Tuning com Adapters (LoRA, QLoRA, DoRA)

Seja a pessoa capaz de pegar um base model e uma tarefa, decidir se o fine-tuning com adapters é de fato a resposta certa, executá-lo, provar que funcionou com um eval que pegaria uma regressão e colocá-lo em produção, e que também consegue defender com argumentos convincentes o prompting ou a recuperação quando eles resolveriam melhor o problema.

**Comece aqui:** [0001. O que um base model realmente é](lessons/0001-what-a-base-model-is.md)
**Última lição:** [0027. Quando não fazer fine-tuning](lessons/0027-when-not-to-fine-tune.md)

## O sucesso se parece com isto

- Derivar o custo de memória do full fine-tuning em comparação com o LoRA para um dado modelo e explicar cada byte.
- Escolher rank, alpha, target modules e learning rate para uma nova tarefa e justificar cada um a partir da tarefa, e não dos valores padrão do post de algum blog.
- Treinar adapters LoRA, QLoRA e DoRA na mesma tarefa e explicar as diferenças medidas, e não as anunciadas.
- Construir um eval que pega uma regressão antes do lançamento, em vez de ler uma curva de loss e torcer.
- Servir um adapter por meio de uma stack de inferência e medir o que isso custou em qualidade e latência.
- Diagnosticar uma execução que falhou e nomear a causa: overfitting, esquecimento catastrófico, chat template errado, incompatibilidade de tokenizer, target modules errados.
- Ler um novo artigo sobre PEFT e julgar se o ganho que ele alega sobreviveria na sua própria tarefa.

## Restrições

- Não pressupõe nenhuma formação prévia em machine learning. A multiplicação de matrizes é a única matemática dada como sabida; tudo acima dela é ensinado onde for necessário.
- O treinamento de adapters sobre um base model da classe de 1B a 3B cabe em aproximadamente 16 GB de memória de acelerador ou memória unificada, o que coloca o arco inteiro ao alcance de um hardware comum de um único dispositivo.
- O suporte entre backends é desigual, não exclusivo. O CUDA continua sendo o caminho mais completo e mais otimizado e é onde os números publicados se reproduzem com mais confiabilidade; os outros backends funcionam, com cobertura de kernels variável e passos mais lentos. Todo conceito se transfere sem alteração; só mudam a velocidade e a disponibilidade de kernels.
- As repetições têm alta latência: uma execução de treinamento leva de minutos a horas, então as sessões são agrupadas em vez de caber em uma noite, com leitura no intervalo.
- As ferramentas evoluem mais rápido do que qualquer livro. As APIs das bibliotecas são lidas na documentação da versão instalada, nunca de memória.
- Nada no arco exige infraestrutura paga, embora alugar um acelerador maior deixe algumas comparações mais rápidas.

## Fora do escopo

- Full fine-tuning em escala, pré-treinamento e treinar um modelo do zero: veja [`llm/pretraining`](../../llm/pretraining/).
- RLHF, DPO e otimização de preferências: veja [`llm/post-training`](../../llm/post-training/). Esta trilha é dona de como uma mudança é aplicada a menos parâmetros; aquela trilha é dona do objetivo de treinamento.
- Quantização como assunto por si só: veja [`llm/quantization`](../../llm/quantization/). A etapa 4 daqui mantém a fatia de que o QLoRA precisa e aponta para lá para a teoria geral; essa fronteira foi definida quando a trilha de quantização foi escrita. A quantização no momento de servir é coberta em [`llm/inference`](../../llm/inference/).
- Destilação como assunto por si só: veja [`llm/distillation`](../../llm/distillation/). Esta trilha é dona de como uma execução de treinamento é aplicada a menos parâmetros; aquela trilha é dona do objetivo e dos dados da destilação.
- Construir infraestrutura de serving, além de executar um adapter por meio de uma stack existente: veja [`llm/inference`](../../llm/inference/).

## O arco

Sete etapas, de zero a sênior. Uma etapa leva várias lições e as fronteiras são flexíveis; o que torna uma etapa concluída é a capacidade, não a contagem de lições.

| Etapa | Lições | Cobre | Concluída quando |
|---|---|---|---|
| 1. O térreo | 0001 a 0004 | O que um forward pass calcula, onde ficam as matrizes de pesos, tokenizers, chat templates, o que o treinamento muda | Consegue apontar quais tensores um adapter tocaria e por quê |
| 2. O argumento da memória | 0005 a 0007 | Parâmetros vs gradientes vs estado do otimizador, os dois momentos do AdamW, memória de ativações, gradient checkpointing | Consegue calcular, em bytes, por que o full fine-tuning falha em um dado dispositivo |
| 3. LoRA | 0008 a 0013 | `ΔW = BA`, rank, alpha e escala, inicialização, escolha dos target modules, executar, ler a execução, merge | Treina um adapter e consegue defender cada hiperparâmetro |
| 4. Quantização e QLoRA | 0014 a 0017 | int8/int4, NF4, dupla quantização, backprop através de um base quantizado congelado, o que se degrada | Executou NF4 de verdade e sabe dizer o que isso custou em qualidade |
| 5. DoRA e o panorama de variantes | 0018 a 0020 | Decomposição em magnitude/direção, por que ajuda mais em rank baixo, como avaliar a alegação de uma nova variante | Consegue prever quando o DoRA vence o LoRA antes de executar |
| 6. Dados e avaliação | 0021 a 0024 | Construção de dataset, contaminação, design held-out, métricas da tarefa vs loss, conjuntos de regressão | Tem um eval que de fato pegou uma regressão |
| 7. Operar e julgar | 0025 a 0027 | Servir adapters vs merged, serving multi-adapter, custo e latência, quando *não* fazer fine-tuning | Tem a confiança para decidir se uma tarefa deve passar por fine-tuning |

## Lições

Siga estas na ordem.

| # | Lição | Ensina |
|---|---|---|
| [0001](lessons/0001-what-a-base-model-is.md) | O que um base model realmente é | O modelo é uma única função de próximo token; base não é instruct |
| [0002](lessons/0002-where-the-weights-live.md) | Onde os pesos ficam | Nomear cada projeção a que um adapter poderia se acoplar |
| [0003](lessons/0003-tokenizers-and-chat-templates.md) | Tokenizers e chat templates | Treine na renderização que você vai servir |
| [0004](lessons/0004-what-training-changes.md) | O que o treinamento realmente muda | As quatro operações em um passo de treinamento |
| [0005](lessons/0005-counting-parameters-and-bytes.md) | Contando parâmetros e bytes | Transformar a configuração de um modelo em gigabytes |
| [0006](lessons/0006-gradients-and-optimizer-state.md) | Gradientes e estado do otimizador | Dezesseis bytes por parâmetro treinável, dois por parâmetro congelado |
| [0007](lessons/0007-activations-and-checkpointing.md) | Ativações, batch size e checkpointing | Por que uma execução com adapter ainda fica sem memória |
| [0008](lessons/0008-the-low-rank-idea.md) | A ideia de baixo rank | `ΔW = BA`, e como contar um adapter |
| [0009](lessons/0009-rank-alpha-and-initialisation.md) | Rank, alpha e inicialização | Só `α/r` importa, e por que `B` começa em zero |
| [0010](lessons/0010-choosing-target-modules.md) | Escolhendo os target modules | Só atenção é uma ablação de 2021, não um padrão |
| [0011](lessons/0011-your-first-adapter.md) | Seu primeiro adapter | Uma execução que prova o pipeline antes de provar qualquer outra coisa |
| [0012](lessons/0012-reading-a-training-run.md) | Lendo uma execução de treinamento | Diagnosticar pelo formato da curva, e o que a loss não enxerga |
| [0013](lessons/0013-merging-and-shipping.md) | Fazendo merge, salvando e entregando um adapter | O merged é exato; um adapter é um diff que precisa do seu base |
| [0014](lessons/0014-quantisation-from-first-principles.md) | Quantização desde os primeiros princípios | Escalas por bloco, e por que um único outlier arruína um tensor |
| [0015](lessons/0015-nf4-and-double-quantisation.md) | NF4 e dupla quantização | As duas ideias que o QLoRA de fato contribuiu |
| [0016](lessons/0016-training-through-a-quantized-base.md) | Treinando através de um base quantizado | Como os gradientes fluem por pesos de 4 bits congelados |
| [0017](lessons/0017-what-qlora-costs.md) | O que o QLoRA realmente custa | Separar a degradação do base da degradação do treinamento |
| [0018](lessons/0018-dora-magnitude-and-direction.md) | DoRA: magnitude e direção | A renormalização desacopla as duas, e isso é o método |
| [0019](lessons/0019-when-dora-wins.md) | Quando o DoRA vence, e quando não | Prever o ganho antes de executar |
| [0020](lessons/0020-judging-a-new-variant.md) | Julgando uma nova variante de PEFT | Seis perguntas de triagem, e o baseline a superar |
| [0021](lessons/0021-building-the-dataset.md) | Construindo o dataset | Os dados vencem todo hiperparâmetro deste workspace |
| [0022](lessons/0022-contamination-and-held-out-design.md) | Contaminação e design de dados held-out | Dividir pela chave certa e dimensionar para a pergunta |
| [0023](lessons/0023-metrics-that-mean-something.md) | Métricas que significam alguma coisa | A loss seleciona checkpoints; as métricas da tarefa tomam decisões |
| [0024](lessons/0024-the-regression-suite.md) | O conjunto de regressão | Pegar o dano que todos os outros números escondem |
| [0025](lessons/0025-serving-adapters.md) | Servindo adapters | Faça merge para uma tarefa, roteie para muitas |
| [0026](lessons/0026-cost-latency-and-throughput.md) | Custo, latência e throughput | Prefill versus decode, e para onde o dinheiro realmente vai |
| [0027](lessons/0027-when-not-to-fine-tune.md) | Quando não fazer fine-tuning | O fine-tuning é o sexto da lista, e por que isso importa |

## Referência

- [Glossário](GLOSSARY.md): termos canônicos deste tópico
- [Recursos](RESOURCES.md): fontes e comunidades confiáveis
- [Orçamento de memória](reference/memory-budget.md): a contabilidade de bytes e o que tentar quando uma execução não cabe
- [Hiperparâmetros do LoRA](reference/lora-hyperparameters.md): rank, alpha, targets, learning rate, variantes
- [Modos de falha](reference/failure-modes.md): do sintoma à causa, e as falhas silenciosas

## Como isto funciona

Cada lição é curta e autocontida. Os gabaritos ficam recolhidos: primeiro lembre, depois abra. A prática no mundo real importa mais do que a leitura, e espaçá-la é o ponto. Tudo o que ainda estiver confuso no fim de uma lição vale ser perseguido até a fonte primária antes de seguir adiante.
