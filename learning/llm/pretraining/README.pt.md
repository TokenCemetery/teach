---
title: "Pré-treinamento de LLMs"
description: "Treine um modelo do zero em escala: dados, tokenizer, treinamento distribuído e um orçamento de compute defensável"
type: topic
---

# Pré-treinamento de LLMs

Seja capaz de planejar e executar um job de pré-treinamento a partir da inicialização aleatória: construir o pipeline de dados, treinar o tokenizer, escolher um orçamento de tokens compute-optimal para uma dada contagem de parâmetros, impedir que uma execução distribuída de vários dias divirja ou trave por causa da falha de um nó e defender esse conjunto de escolhas diante de quem, de outra forma, teria simplesmente feito fine-tuning de um modelo base existente.

**Última lição:** [0024. Revisando a configuração de execução de treinamento de outra pessoa](lessons/0024-reviewing-someone-elses-training-run-config.md)

## O sucesso se parece com isto

- Construir um corpus de pré-treinamento deduplicado e filtrado por qualidade a partir de fontes brutas e dizer o que cada etapa de filtragem remove e por quê.
- Treinar um tokenizer e defender um tamanho de vocabulário em função do seu efeito no comprimento das sequências e no tamanho da tabela de embeddings.
- Dados uma contagem de parâmetros e um orçamento de compute, calcular a contagem de tokens compute-optimal e defendê-la contra uma alternativa subtreinada no estilo de Kaplan.
- Explicar o que o ZeRO/FSDP particionam, por que o paralelismo de dados sozinho fica sem memória antes de ficar sem compute e quando o paralelismo de tensor ou de pipeline vale o seu custo de comunicação.
- Ler a curva de loss e as normas de gradiente de uma execução de treinamento e dizer se um spike é recuperável ou se significa recomeçar de um checkpoint anterior.
- Projetar um esquema de checkpointing para uma execução de vários dias que sobreviva à falha de um nó sem perder mais do que alguns minutos de progresso.
- Decidir se uma tarefa declarada pede pré-treinamento, pré-treinamento continuado ou fine-tuning de um modelo base existente e defender a escolha pelo custo.

## Restrições

- Próxima de frameworks, e não agnóstica a eles. As técnicas de treinamento distribuído (particionamento do ZeRO, paralelismo de tensor e de pipeline) são estáveis o bastante para que as lições citem a biblioteca e a API reais que descrevem, ao contrário do pseudocódigo neutro em relação a provedores que `llm/agents` usa para uma superfície que muda mais rápido.
- Nenhuma lição treina um modelo em escala de fronteira. As repetições rodam em pequena escala (um modelo do porte do GPT-2 em poucas GPUs, ou uma configuração simulada de vários nós) e raciocinam a partir daí até o que muda na escala descrita pelos artigos citados.
- Pressupõe `llm/transformers`: o mecanismo de atenção, o loop de treinamento, a loss de cross-entropy, o AdamW, a precisão mista e o gradient clipping são pré-requisitos, e não revisão.
- Pressupõe acesso a várias GPUs (até duas, ou uma simulação multiprocesso em CPU das operações coletivas) para as repetições de treinamento distribuído.

## Fora do escopo

- A arquitetura transformer em si, a loss de cross-entropy, o backward pass, o AdamW, a precisão mista e o gradient clipping: veja [`llm/transformers`](../../llm/transformers/). Esta trilha começa quando esse loop precisa rodar em centenas de GPUs contra trilhões de tokens, e não antes.
- Adaptar um modelo base existente com LoRA, QLoRA ou DoRA: veja [`llm/finetuning`](../../llm/finetuning/). O pré-treinamento parte de pesos aleatórios, e não de um checkpoint, e os dois são as duas formas de os pesos de um modelo mudarem, tratadas como irmãs e não como uma contendo a outra.
- Paralelismo e quantização no momento de servir: veja [`llm/inference`](../../llm/inference/). Esta trilha cobre as versões de treinamento do paralelismo (sincronização de gradientes, particionamento de ativações e do estado do otimizador), e não o serving.
- Metodologia de avaliação e design de dados held-out: veja [`llm/evals`](../../llm/evals/). Aparece aqui apenas como a única capacidade de que uma execução de pré-treinamento precisa, validar um checkpoint no meio da execução, e é referenciada em vez de reexplicada.
- Alinhar um modelo pré-treinado em um assistente: veja [`llm/post-training`](../../llm/post-training/).
- A destilação como sinal de treinamento, incluindo a distribuição de um professor usada durante o pré-treinamento: veja [`llm/distillation`](../../llm/distillation/). Aquela trilha ensina a loss e a escolha de dados; executar o job de pré-treinamento fica aqui.

## O arco

Dez etapas, desde nenhum conhecimento prévio até o julgamento sênior. Não é uma lista de lições: uma etapa leva várias lições e as fronteiras são flexíveis.

| Etapa | Lições | Cobre | Concluída quando |
| --- | --- | --- | --- |
| 1. Pipeline de dados | 0001 a 0002 | Obtenção, deduplicação, filtragem de qualidade | Consegue construir um corpus filtrado e deduplicado a partir de fontes brutas e defender o que cada etapa removeu |
| 2. Treinamento do tokenizer | 0003 a 0004 | BPE e SentencePiece do zero, tradeoffs do tamanho do vocabulário | Consegue treinar um tokenizer e defender a escolha de um tamanho de vocabulário |
| 3. Leis de escala | 0005 a 0006 | Kaplan contra Chinchilla, a razão compute-optimal entre tokens e parâmetros | Dado um orçamento de compute, consegue derivar uma contagem de tokens compute-optimal e defendê-la |
| 4. Paralelismo de dados | 0007 a 0008 | All-reduce de gradientes, por que ele para de escalar sozinho | Consegue dizer por que o paralelismo de dados sozinho fica sem memória antes de ficar sem compute |
| 5. Particionando a memória | 0009 a 0011 | Estágios 1 a 3 do ZeRO, FSDP, particionamento de ativações e do estado do otimizador | Consegue dizer o que cada estágio do ZeRO particiona e o que ele custa em comunicação |
| 6. Paralelismo de modelo | 0012 a 0014 | Paralelismo de tensor e de pipeline para treinamento | Consegue decidir quando o paralelismo de tensor ou de pipeline compensa o seu custo de comunicação em relação ao particionamento sozinho |
| 7. Numérica e estabilidade em escala | 0015 a 0017 | Precisão mista em escala, loss spikes, normas de gradiente, schedules de warm-up e decaimento | Dada uma curva de loss, consegue dizer se um spike é recuperável ou exige recomeçar de um checkpoint anterior |
| 8. Checkpointing e tolerância a falhas | 0018 a 0019 | Salvar e retomar uma execução de vários dias, sobreviver à falha de um nó | Consegue projetar um esquema de checkpointing que limita o progresso perdido após a falha de um nó |
| 9. Monitorando uma execução de treinamento | 0020 a 0021 | Curvas de loss, checkpoints de avaliação periódica, ligação com `llm/evals` | Consegue ler um dashboard de treinamento e dizer se a execução está no caminho certo |
| 10. Julgamento | 0022 a 0024 | Pré-treinar contra continuar o pré-treinamento contra fazer fine-tuning, defender um orçamento de compute, revisar a configuração de execução de treinamento de outra pessoa | Tem a confiança para tomar a decisão e explicá-la a outra pessoa |

## Lições

Siga estas na ordem.

| # | Lição | Ensina |
| --- | --- | --- |
| [0001](lessons/0001-sourcing-and-mixing-a-pretraining-corpus.md) | Obtendo e misturando um corpus de pré-treinamento | O que entra em um corpus de pré-treinamento e por que a mistura de fontes importa mais do que a contagem total de bytes |
| [0002](lessons/0002-deduplication-and-quality-filtering.md) | Deduplicação e filtragem de qualidade | Por que texto quase duplicado e documentos de baixa qualidade são removidos antes do treinamento e o que custa pular essa etapa |
| [0003](lessons/0003-byte-pair-encoding-from-scratch.md) | Byte-Pair Encoding do zero | O algoritmo que transforma palavras raras e desconhecidas em sequências de unidades de subpalavra aprendidas, resolvido à mão |
| [0004](lessons/0004-sentencepiece-and-the-vocabulary-size-tradeoff.md) | SentencePiece e o tradeoff do tamanho do vocabulário | Tokenizar texto bruto sem um pré-tokenizer e o que um vocabulário maior ou menor realmente custa |
| [0005](lessons/0005-scaling-laws-what-kaplan-predicted.md) | Leis de escala: o que Kaplan previu | Uma lei de potência empírica permite prever a loss de uma execução de treinamento antes de pagar por ela, e o que isso previa sobre como gastar um orçamento de compute |
| [0006](lessons/0006-chinchilla-the-compute-optimal-correction.md) | Chinchilla: a correção compute-optimal | Por que o tamanho do modelo e a contagem de tokens devem escalar juntos e como transformar um orçamento de compute em uma contagem de tokens |
| [0007](lessons/0007-data-parallelism-and-gradient-all-reduce.md) | Paralelismo de dados e all-reduce de gradientes | Dividir um batch entre dispositivos que guardam, cada um, uma cópia completa do modelo, e o que mantém todas as cópias idênticas |
| [0008](lessons/0008-why-data-parallelism-alone-runs-out-of-memory.md) | Por que só o paralelismo de dados fica sem memória | Contar exatamente o que um otimizador Adam de precisão mista guarda por parâmetro e onde isso bate em um muro |
| [0009](lessons/0009-zero-stage-1-and-2-partitioning-optimizer-state-and-gradients.md) | ZeRO estágios 1 e 2: particionando o estado do otimizador e os gradientes | Remover de graça as cópias redundantes do paralelismo de dados, antes que o custo de comunicação precise crescer |
| [0010](lessons/0010-zero-stage-3-and-fsdp-partitioning-parameters-too.md) | ZeRO estágio 3 e FSDP: particionando também os parâmetros | Particionar os próprios parâmetros significa reconstruí-los sob demanda, e esse é o primeiro custo disso |
| [0011](lessons/0011-activation-memory-and-zero-r.md) | Memória de ativações e ZeRO-R | Particionar os estados do modelo resolve um problema de memória e deixa de pé um segundo, as ativações |
| [0012](lessons/0012-tensor-parallelism-splitting-a-layers-matrices.md) | Paralelismo de tensor: dividindo as matrizes de uma camada | Escolher ao longo de qual eixo dividir uma matriz de pesos para que um bloco transformer inteiro precise de apenas um all-reduce |
| [0013](lessons/0013-pipeline-parallelism-splitting-the-models-layers.md) | Paralelismo de pipeline: dividindo as camadas do modelo | Atribuir camadas consecutivas a dispositivos diferentes e o tempo ocioso que isso custa no início e no fim de cada batch |
| [0014](lessons/0014-combining-all-three-when-tensor-and-pipeline-parallelism-earn-their-cost.md) | Combinando os três: quando o paralelismo de tensor e de pipeline compensam o seu custo | Associar cada estratégia de paralelismo à interconexão que ela tolera e quando o particionamento sozinho não basta |
| [0015](lessons/0015-mixed-precision-at-scale-bfloat16-and-stochastic-rounding.md) | Precisão mista em escala: bfloat16 e stochastic rounding | Um formato numérico com o intervalo do fp32 mas menos precisão, e o que custa atualizar parâmetros diretamente nele |
| [0016](lessons/0016-loss-spikes-and-the-optimizers-own-instabilities.md) | Loss spikes e as instabilidades do próprio otimizador | O mesmo spike pode vir de um batch ruim ou do próprio otimizador, e distingui-los exige uma comparação controlada |
| [0017](lessons/0017-warmup-decay-and-growing-the-batch-mid-run.md) | Warm-up, decaimento e aumento do batch no meio da execução | Começar devagar, decair segundo um schedule e deixar o próprio batch size mudar no meio do treinamento |
| [0018](lessons/0018-what-a-checkpoint-has-to-hold.md) | O que um checkpoint precisa guardar | Um checkpoint que salva apenas os pesos não consegue retomar uma execução com exatidão, e escolher a frequência de salvamento é um tradeoff à parte |
| [0019](lessons/0019-surviving-a-node-failure.md) | Sobrevivendo à falha de um nó | Pausar, diagnosticar, isolar o que quebrou e retomar do último checkpoint, ao custo que for |
| [0020](lessons/0020-reading-a-loss-curve.md) | Lendo uma curva de loss | A curva de loss de treinamento sozinha subestima os problemas; dois outros sinais pegam o que ela deixa passar, e pegam mais cedo |
| [0021](lessons/0021-periodic-held-out-evaluation.md) | Avaliação held-out periódica | A loss de treinamento diz que o modelo está se ajustando aos próprios dados de treinamento; só uma verificação held-out diz algo sobre o resto |
| [0022](lessons/0022-pretraining-is-usually-the-wrong-default.md) | Pré-treinar costuma ser o padrão errado | Uma segunda fase de pré-treinamento sobre um modelo existente traz a maior parte do benefício sem pagar o custo completo de novo |
| [0023](lessons/0023-defending-a-compute-budget.md) | Defendendo um orçamento de compute | Um plano de pré-treinamento é uma aposta feita de muitas decisões separadas, e defendê-lo significa defender cada uma nos seus próprios termos |
| [0024](lessons/0024-reviewing-someone-elses-training-run-config.md) | Revisando a configuração de execução de treinamento de outra pessoa | Percorrer o plano por todas as etapas que esta trilha cobriu, em ordem, e resolver uma alegação contestada a partir da fonte e não de um post de blog |

## Referência

- [Glossário](GLOSSARY.md): termos canônicos deste tópico
- [Recursos](RESOURCES.md): fontes confiáveis

## Como isto funciona

Cada lição é curta e autocontida. Os gabaritos ficam recolhidos: primeiro lembre, depois abra. A prática no mundo real importa mais do que a leitura, e espaçá-la é o ponto. Tudo o que ainda estiver confuso no fim de uma lição vale ser perseguido até a fonte primária antes de seguir adiante.
