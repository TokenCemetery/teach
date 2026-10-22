---
title: "Quantização"
description: "Quantize um LLM e defenda o resultado: formatos numéricos, métodos de PTQ e QAT, o que roda mais rápido e como medir o que isso custou"
type: topic
---

# Aprendizado: Quantização

Pegue um LLM treinado e deixe-o menor e mais rápido com quantização, sabendo o que cada formato numérico e cada método faz com os seus pesos, ativações e KV cache. Termine capaz de escolher um esquema para um dado modelo, hardware e nível de qualidade, medir com honestidade o que ele custou e revisar a alegação de outra pessoa de que um modelo quantizado "não perde nada".

**Última lição:** [27. Quando a resposta de sempre está errada](lessons/0027-when-the-usual-answer-is-wrong.md)

## O sucesso se parece com isto

- Ler o layout de bits de um formato numérico, dizer que faixa e que precisão ele oferece e calcular a pegada de memória de um modelo nesse formato.
- Quantizar um tensor à mão: escolher a scale, o zero-point, a faixa de clipping e a granularidade, e prever de onde virá o erro.
- Explicar por que os LLMs têm features e ativações outliers e qual técnica trata cada um deles.
- Explicar o que o round-to-nearest, o GPTQ e o AWQ fazem com os pesos e o que o calibration set contribui e pode errar.
- Decidir quando as ativações e o KV cache podem ser quantizados além dos pesos, e com qual técnica.
- Dizer quando o treinamento ciente de quantização compensa o seu custo em relação à quantização pós-treinamento.
- Prever se um esquema realmente vai rodar mais rápido em um dado hardware e com um dado batch size, em vez de supor que menos bits significa mais velocidade.
- Medir a qualidade que uma quantização custou, além da perplexity, contra um baseline honesto.
- Ler um checkpoint quantizado, em safetensors com a sua configuração de quantização ou em GGUF, e dizer o que há armazenado nele.
- Escolher um esquema para um dado modelo, hardware e nível de qualidade, revisar a alegação de quantização de outra pessoa apontando o que ela esconde e dizer quando a resposta de sempre é a errada.

## Restrições

- Pressupõe familiaridade com a leitura de Python e NumPy e com o que é uma camada de transformer no nível de "multiplicações de matrizes mais atenção". Não pressupõe conhecimento prévio de quantização nem dos detalhes internos do ponto flutuante.
- Neutra em relação a hardware sempre que possível. Quando uma afirmação é o comportamento documentado de um fornecedor ou de uma biblioteca, a lição os nomeia, porque o suporte de kernels muda mais rápido do que a teoria.
- A prática roda em um laptop com NumPy nas etapas 1 a 3. As repetições posteriores quantizam um modelo aberto pequeno, para o que um notebook com GPU gratuita é suficiente.

## Fora do escopo

- QLoRA, treinar um adapter através de um base de 4 bits: veja [`llm/finetuning`](../../llm/finetuning/), etapa 4 (lições 0014 a 0017). Esta trilha ensina a teoria geral que essas lições aplicam e aponta para elas em vez de repetir o QLoRA.
- Escolher um esquema para um orçamento de latência de serving e executá-lo no vLLM ou no llama.cpp: veja [`llm/inference`](../../llm/inference/), etapa 3 (lições 0007 a 0009) e a sua [folha de Quantização no Serving](../../llm/inference/reference/quantization-at-serve-time.md). Esta trilha ensina como os métodos funcionam e como julgá-los; a decisão de serving fica lá.
- Construir um eval: veja [`llm/evals`](../../llm/evals/) e a sua [folha de go/no-go](../../llm/evals/reference/go-no-go.md). Esta trilha usa um eval para medir a perda de quantização e não reensina como construir um.
- Poda (pruning), esparsidade e destilação, as outras formas de encolher um modelo. Elas se combinam com a quantização, mas são tópicos separados. A destilação tem a sua própria trilha, [`llm/distillation`](../../llm/distillation/), que a compara com a quantização na sua etapa de julgamento.
- Escrever kernels de quantização. A etapa 7 ensina o que um kernel precisa fazer para que um esquema rode mais rápido, não como escrever um.

A fronteira com as duas trilhas vizinhas foi definida quando esta trilha foi escrita: as lições de finetuning e de inference continuam como estão, cada uma ensinando a fatia de que o seu caso de uso precisa, e apontam para cá para os fundamentos.

## O arco

Dez etapas, desde o que é um formato numérico até o julgamento para revisar a quantização de outra pessoa. Uma etapa leva várias lições e as fronteiras são flexíveis; o que torna uma etapa concluída é a capacidade, não a contagem de lições.

| Etapa | Lições | Cobre | Concluída quando |
|---|---|---|---|
| 1. Formatos numéricos | 0001 a 0003 | O que a quantização oferece, fp32, fp16, bf16, fp8, int8, int4 e formatos com escala por bloco | Consegue ler o layout de bits de um formato e dimensionar um modelo nele |
| 2. O mapeamento de quantização | 0004 a 0006 | Quantizar e dequantizar, scale e zero-point, escolha da faixa de clipping, per-tensor, per-channel e per-group | Consegue quantizar um tensor à mão e prever o seu erro |
| 3. Outliers | 0007 a 0008 | Features outliers e ativações massivas em LLMs, e as famílias de correção | Consegue dizer por que um LLM em int8 ingênuo quebra e qual correção se aplica |
| 4. Quantização de pesos post-training | 0009 a 0012 | Round-to-nearest, GPTQ, AWQ, o calibration set | Consegue quantizar os pesos de um modelo para 4 bits e explicar o que cada método mudou |
| 5. Ativações e o KV cache | 0013 a 0016 | Somente pesos versus pesos e ativações, SmoothQuant, rotações, quantização do KV cache | Consegue decidir o que quantizar além dos pesos e com qual técnica |
| 6. Treinamento ciente de quantização | 0017 a 0018 | Quantização fake, o straight-through estimator, QAT para LLMs | Consegue dizer quando o QAT compensa o seu custo em relação à PTQ |
| 7. Hardware e kernels | 0019 a 0020 | Limitado pela largura de banda de memória versus limitado por compute, o que um kernel precisa suportar, qual hardware roda qual formato | Consegue prever se um esquema roda mais rápido em um dado hardware e batch size |
| 8. Medindo a perda de qualidade | 0021 a 0022 | Perplexity e seus limites, flips, suítes de tarefas, uma comparação honesta | Consegue medir o que uma quantização custou e defender o número |
| 9. Formatos de arquivo | 0023 a 0024 | Safetensors com configurações de quantização, tipos de quant do GGUF e a matriz de importância | Consegue ler um checkpoint quantizado e dizer o que ele armazena |
| 10. Julgamento | 0025 a 0027 | Escolher um esquema, revisar uma alegação, entregar um modelo quantizado de que outros dependem, quando a resposta de sempre está errada | Tem a confiança para decidir sobre uma quantização e explicá-la a outra pessoa |

## Lições

Siga estas na ordem.

| # | Lição | Ensina |
|---|---|---|
| [0001](lessons/0001-what-quantization-buys.md) | O que a quantização oferece | Menos bits por parâmetro reduzem a memória e os bytes lidos por token, que é de onde vem a maior parte da velocidade |
| [0002](lessons/0002-floating-point-formats.md) | Formatos de ponto flutuante | Como os bits de sinal, expoente e mantissa dividem faixa e precisão em fp32, fp16 e bf16 |
| [0003](lessons/0003-low-bit-formats.md) | Formatos de poucos bits | O que fp8, int8, int4 e formatos com escala por bloco, como o MXFP4, conseguem e não conseguem representar |
| [0004](lessons/0004-quantize-and-dequantize.md) | Quantizar e dequantizar | O mapeamento afim de valores reais para inteiros: scale, zero-point, arredondamento e clamping |
| [0005](lessons/0005-choosing-the-range.md) | Escolhendo a faixa | Por que aplicar clipping à faixa troca um pouco de erro de clipping por muito menos erro de arredondamento |
| [0006](lessons/0006-granularity.md) | Granularidade | Scales per-tensor, per-channel e per-group, e o que cada uma custa em bits armazenados |
| [0007](lessons/0007-why-llms-have-outliers.md) | Por que os LLMs têm outliers | Dimensões de features outliers e ativações massivas, onde aparecem e por que um único valor arruína a scale de um tensor |
| [0008](lessons/0008-handling-outliers.md) | Lidando com outliers | As quatro famílias de correção: mantê-los em alta precisão, diminuir o grupo, migrá-los ou eliminá-los por rotação |
| [0009](lessons/0009-round-to-nearest.md) | Round-to-nearest | Quantizar os pesos um a um sem dados, por que ele se sustenta em 8 bits e escorrega em 4 ou menos |
| [0010](lessons/0010-gptq.md) | GPTQ | Quantizar os pesos de uma camada em sequência e gastar cada erro de arredondamento nos pesos ainda não quantizados |
| [0011](lessons/0011-awq.md) | AWQ | Proteger os pesos que encontram ativações grandes escalando os seus canais antes do arredondamento |
| [0012](lessons/0012-the-calibration-set.md) | O calibration set | Que dados de calibração um método lê, de quantos precisa e como um conjunto incompatível aparece |
| [0013](lessons/0013-weights-activations-or-both.md) | Pesos, ativações ou ambos | O que os esquemas somente de pesos e de pesos e ativações economizam cada um, e por que as ativações são mais difíceis |
| [0014](lessons/0014-smoothquant.md) | SmoothQuant | Mover a dificuldade de quantização das ativações para os pesos com uma scale por canal |
| [0015](lessons/0015-rotations.md) | Rotações | Multiplicar por uma matriz ortogonal para espalhar os outliers por vários canais e fazer as ativações de 4 bits sobreviverem |
| [0016](lessons/0016-kv-cache-quantization.md) | Quantização do KV cache | Por que keys e values quantizam ao longo de eixos diferentes, e o que isso oferece em contexto longo |
| [0017](lessons/0017-fake-quantization-and-the-ste.md) | Quantização fake e o STE | Como o treinamento enxerga a quantização: arredondamento simulado no forward pass, um gradiente straight-through no backward pass |
| [0018](lessons/0018-qat-for-llms.md) | QAT para LLMs | O que o treinamento ciente de quantização custa em um LLM, o que ele recupera e quando a PTQ basta |
| [0019](lessons/0019-what-actually-runs-faster.md) | O que realmente roda mais rápido | Por que a quantização somente de pesos acelera o decode com batch pequeno e pode deixar o prefill com batch grande mais lento |
| [0020](lessons/0020-hardware-and-kernel-support.md) | Hardware e suporte de kernel | Em quais formatos uma GPU calcula nativamente, quais ela só armazena e o que um kernel ausente custa |
| [0021](lessons/0021-perplexity-and-its-limits.md) | Perplexity e seus limites | O que a perplexity mede, por que uma pequena mudança pode esconder grandes flips de resposta e o que medir no lugar |
| [0022](lessons/0022-an-honest-quantization-eval.md) | Um eval honesto de quantização | Comparar um modelo quantizado com o seu baseline no mesmo harness e nas mesmas tarefas, e reportar o que ele perdeu e onde |
| [0023](lessons/0023-quantized-checkpoints.md) | Checkpoints quantizados | O que um checkpoint quantizado em safetensors armazena e como a sua configuração de quantização diz a um loader como lê-lo |
| [0024](lessons/0024-gguf-quant-types.md) | Tipos de quant do GGUF | O que significa o nome de um tipo GGUF como Q4_K_M e o que a matriz de importância muda |
| [0025](lessons/0025-choosing-a-scheme.md) | Escolhendo um esquema | Escolher um formato e um método a partir do modelo, do hardware, do formato do batch e do nível de qualidade |
| [0026](lessons/0026-reviewing-a-quantization-claim.md) | Revisando uma alegação de quantização | Revisar "4 bits sem perda de qualidade" apontando o que a medição escondeu, e fazer o rollout de um modelo quantizado de que outros dependem |
| [0027](lessons/0027-when-the-usual-answer-is-wrong.md) | Quando a resposta de sempre está errada | Reconhecer quando pesos de 4 bits ou uma receita padrão é a escolha errada e resolver a disputa a partir da fonte primária |

## Referência

- [Glossário](GLOSSARY.md): termos canônicos deste tópico
- [Recursos](RESOURCES.md): fontes confiáveis, cada uma anotada com o que cobre
- [Formatos Numéricos](reference/number-formats.md): layouts de bits, faixa e precisão de cada formato, e a aritmética de memória, da etapa 1
- [O Mapeamento de Quantização](reference/quantization-mapping.md): as fórmulas de quantizar e dequantizar, escolha da faixa, granularidade e correções de outliers, das etapas 2 e 3
- [Métodos de PTQ de Pesos](reference/weight-ptq-methods.md): round-to-nearest, GPTQ e AWQ lado a lado, e o que o calibration set faz, da etapa 4
- [Ativações e o KV Cache](reference/activations-and-kv-cache.md): somente pesos versus pesos e ativações, SmoothQuant, rotações e quantização do KV cache, da etapa 5
- [QAT e Hardware](reference/qat-and-hardware.md): como o QAT funciona e quando compensa, e o que faz um esquema rodar mais rápido, das etapas 6 e 7
- [Medindo e Armazenando](reference/measuring-and-storing.md): um eval honesto de quantização, e como ler um checkpoint quantizado ou um tipo GGUF, das etapas 8 e 9
- [Checklist de Revisão de Quantização](reference/quantization-review-checklist.md): escolher um esquema e as perguntas a fazer sobre a alegação de quantização de outra pessoa, da etapa 10

## Como isto funciona

Cada lição é curta e autocontida. Os gabaritos ficam recolhidos: primeiro lembre, depois abra. A prática no mundo real importa mais do que a leitura, e espaçá-la é o ponto. Tudo o que ainda estiver confuso no fim de uma lição vale ser perseguido até a fonte primária antes de seguir adiante.
