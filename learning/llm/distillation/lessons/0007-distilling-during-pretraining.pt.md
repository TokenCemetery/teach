---
title: "7. Destilando durante o pré-treinamento"
description: "Como o Gemma 2 e o Minitron usaram a distribuição de um professor como sinal de treinamento em escala, e o que custa armazenar logits"
type: lesson
---

# Lição 7. Destilando durante o pré-treinamento

**Ligação com a missão:** A missão pede que você escreva a loss em nível de token e diga quando ela não pode ser usada, e esta lição mostra essa loss como o sinal de treinamento de duas famílias reais de modelos, com o custo de guardar as distribuições do professor contado em bytes.
**Fonte principal:** [Artigo científico: "Gemma 2: Improving Open Language Models at a Practical Size", Gemma Team, 2024](https://arxiv.org/abs/2408.00118)
**Pré-requisitos:** [Lição 6](0006-the-tokenizer-constraint.md), [Destilação em nível de token](../GLOSSARY.md), [Logit](../GLOSSARY.md), [Logits top-k](../GLOSSARY.md)

## Aquecimento

1. ▢ Por que um aluno Llama com um professor Qwen descarta a loss simples em nível de token, mesmo quando ambos lhe dão os logits completos?

<details markdown="1"><summary>Verificação</summary>

A loss compara a probabilidade i da linha do aluno com a probabilidade i da linha do professor, e tokenizers diferentes fazem do índice i um token diferente, com tamanhos e posições possivelmente diferentes. As soluções alternativas da etapa 2 são uma loss entre tokenizers ou um aluno da família do professor.

</details>

2. ▢ Qual direção do KL um aluno que cobre modos minimiza, e em qual cenário o Minitron a achou melhor?

<details markdown="1"><summary>Verificação</summary>

[Forward KL](../GLOSSARY.md). O Minitron o achou melhor do que o reverse KL ao retreinar base models podados, com uma loss de LM de 2,155 contra 2,665 para um Minitron 8B podado em profundidade (Tabela 16 do artigo deles). Esse é um cenário, e a lição 5 dá a evidência de instruction tuning para a outra direção.

</details>

## Saiba isto

Esta lição ensina a metade de destilação de duas receitas de treinamento. Como uma execução de pré-treinamento é organizada, dos dados ao hardware, pertence à trilha de [Pré-treinamento](../../pretraining/), e a poda como método não pertence a nenhuma das duas.

### A destilação como objetivo de pré-treinamento: Gemma 2

O relatório do Gemma 2 treina os seus modelos de 2B e 9B com destilação de conhecimento em vez de previsão do próximo token. A motivação é que o treinamento de próximo token escala apenas logaritmicamente com os dados, e os modelos pequenos precisam de execuções muito longas para melhorar. A destilação substitui o vetor one-hot em cada token pela distribuição de próximos tokens de um modelo grande, o que, diz o relatório, dá gradientes mais ricos. O seu objetivo declarado é treinar por números muito grandes de tokens com destilação para simular o treinamento além do número de tokens disponíveis (introdução).

Os fatos que o relatório dá:

- O modelo de 2B foi treinado em 2 trilhões de tokens, o de 9B em 8 trilhões e o de 27B em 13 trilhões (seção 3.1). O de 27B foi treinado do zero, sem destilação.
- As contagens de tokens do 2B e do 9B são mais de 50 vezes a quantidade compute-optimal prevista por Hoffmann et al. (introdução).
- A loss é a log-verossimilhança negativa entre a probabilidade do professor para cada token dado o seu contexto e a do aluno, minimizada sobre o aluno: a soma de -P_T(x | x_c) log P_S(x | x_c) (seção 3.2). Essa é a loss da lição 4 com temperatura 1.
- O vocabulário tem 256.128 entradas (Tabela 1), herdadas do Gemini, e o comprimento de contexto é de 8.192 tokens (seção 2).

As ablações dele usam um professor de 7B, não o final. Um aluno de 2B treinado em 500B tokens, que o relatório diz ser 10 vezes o número compute-optimal para 2B, obteve uma média de 60,3 em três benchmarks treinado do zero e 67,7 destilado (Tabela 6). Com o professor fixo em 7B, a perplexidade de validação com 200M, 400M e 1B de parâmetros foi 23, 19 e 17 do zero e 21, 17 e 15 destilado (Tabela 7). O relatório também diz que o novo 2B, com 2T tokens, melhora significativamente o 2B do Gemma 1 com 3T tokens (seção 6.1). Essas são comparações do próprio Google.

### O que o relatório não diz

O relatório não nomeia o professor dos modelos finais de 2B e 9B nem dá o seu tamanho. Ele não descreve como a distribuição do professor foi fornecida ao aluno: armazenada, calculada junto com o treinamento ou aproximada. Afirmações sobre um top-k amostrado ou truncado no Gemma 2 não estão no relatório. A próxima seção calcula o que cada opção custa, para que você possa raciocinar sobre isso sem uma fonte para a escolha.

### O que custa armazenar o professor

Uma distribuição sobre o vocabulário para cada token de treinamento é grande. O script usa o vocabulário e as contagens de tokens do Gemma 2 e duas suposições desta lição: probabilidades em bf16 com 2 bytes e, para a versão truncada, um k ilustrativo de 256 com um índice de token de 4 bytes.

```python
vocab = 256_128            # Gemma 2 vocabulary size (Table 1 of the report)
tokens = {"2B run": 2e12, "9B run": 8e12}

full = vocab * 2           # bf16: 2 bytes per probability
k = 256                    # an illustrative k, not a number from any paper
topk = k * (2 + 4)         # 2-byte probability + 4-byte token index

print("full per token: %d bytes" % full)
print("top-%d per token: %d bytes (%.1fx smaller)" % (k, topk, full / topk))
print("full per 8192-token sequence: %.2f GB" % (full * 8192 / 1e9))
for name, n in tokens.items():
    print(name, "full: %.2f EB" % (full * n / 1e18), " top-%d: %.2f PB" % (k, topk * n / 1e15))
```

Preveja a ordem de grandeza do custo da distribuição completa para a execução de 2B antes de rodar. A saída:

```text
full per token: 512256 bytes
top-256 per token: 1536 bytes (333.5x smaller)
full per 8192-token sequence: 4.20 GB
2B run full: 1.02 EB  top-256: 3.07 PB
9B run full: 4.10 EB  top-256: 12.29 PB
```

Armazenar distribuições completas para a execução de 2B dá cerca de um exabyte, e para a de 9B cerca de quatro. Manter 256 entradas por token corta isso por um fator de 333,5, para petabytes, e o número ainda conta cada token de treinamento uma só vez, sem épocas repetidas. O truncamento também custa algo. A massa da cauda que é descartada precisa ser tratada, renormalizando ou tratando-a como um único bucket, e a escolha muda o alvo.

Há uma alternativa que não armazena nada: rodar o professor junto com o aluno e ler a sua distribuição do forward pass. O Minitron segue esse caminho e observa que a destilação adiciona o overhead de um forward pass adicional no professor, então eles comparam as suas execuções destilada e convencional com compute igual (seção 4). Qual caminho um dado laboratório usou não é algo que esta lição afirma.

Os autores do Minitron também testaram o truncamento diretamente. No apêndice deles sobre destilação (A.3), manter apenas os K maiores logits do professor e do aluno, para K até 100, causou uma queda significativa de acurácia. A queda desapareceu para K maiores, mas os resultados não foram melhores do que não truncar. Esse é um cenário de retreinamento de modelo podado, e o K em que o truncamento deixa de prejudicar vai diferir conforme o vocabulário e o modelo.

### Poda mais destilação: Minitron

O Minitron (Muralidharan et al., 2024) comprime o Nemotron-4 15B podando-o e recuperando a acurácia por retreinamento com o original como professor. O seu aluno começa como uma cópia podada, então compartilha o tokenizer do professor por construção. Esta lição toma apenas a metade da destilação.

- **Tokens.** Os modelos Minitron 8B e 4B foram retreinados, cada um, em 94 bilhões de tokens. O artigo compara o Minitron 8B com o Nemotron-3 8B, treinado em 3,8 trilhões, e enuncia a economia como 40 vezes menos tokens (Tabela 2).
- **Destilação contra retreinamento convencional.** Para um modelo de 4B, eles comparam com compute igual (Tabela 11). Treinar do zero em 150B tokens deu HellaSwag 46,22 e MMLU 24,36. Podar o 15B para 4B e retreinar de forma convencional em 150B deu 50,85 e 24,57. Podar e retreinar com destilação em 100B tokens deu 51,04 e 37,81. A execução destilada usa 100B tokens contra 150B por causa do forward pass extra do professor. Isso é um ganho de 4,8 pontos no HellaSwag e de 13,5 no MMLU sobre treinar do zero.
- **Loss.** Forward KL nos logits, com temperatura 1, com a loss de logits sozinha melhor do que uma mistura ponderada com a loss de language modeling, e sem ganho ao truncar para os K maiores (seção 4 e apêndice A.3).

O artigo de acompanhamento (Sreenivas et al., 2024) aplica a receita ao Llama 3.1 8B e ao Mistral NeMo 12B. Ele acrescenta um passo antes da destilação: a correção do professor. Quando os dados originais de pré-treinamento não estão disponíveis, o professor dá uma orientação subótima em um dataset diferente, o que os autores atribuem a uma mudança na distribuição dos tokens de subpalavras. Então eles fazem fine-tuning do professor em cerca de 100B tokens dos dados de destilação primeiro, com warm-up e learning rates baixos. Depois podam e destilam com forward KL apenas nos logits. O Llama-3.1-Minitron 4B foi retreinado em 94B tokens e o MN-Minitron-8B em 380B (Tabela 4). O artigo diz que o 4B se compara favoravelmente ao Llama 3.1 8B usando 150 vezes menos tokens, 94B contra 15T, e o 8B supera o Llama 3.1 8B usando 40 vezes menos, 380B contra 15T (seção 5.1). Essas são comparações da NVIDIA na sua própria avaliação.

## Prática

1. ▢ No relatório, quais modelos do Gemma 2 foram treinados com destilação, e quantos tokens cada um viu?

    - a) O 2B em 8T e o 27B em 2T
    - b) O 9B em 8T e o 27B em 13T
    - c) Os três modelos foram treinados em 13T tokens cada
    - d) O 2B em 2T e o 9B em 8T

<details markdown="1"><summary>Verificação</summary>

**d)** O 27B foi treinado do zero em 13T tokens, então (b) e (c) o incluem por engano. A alternativa (a) troca as contagens de tokens. O relatório enuncia as contagens na seção 3.1.

</details>

2. ▢ Com um vocabulário de 256.128 e 2 bytes por probabilidade, quantos bytes ocupa uma distribuição completa de próximo token, e quantos gigabytes isso dá para uma única sequência de 8.192 tokens?

<details markdown="1"><summary>Dica</summary>

Multiplique o vocabulário pelos bytes por entrada, depois pelo comprimento da sequência, e então divida por um bilhão.

</details>

<details markdown="1"><summary>Verificação</summary>

256.128 vezes 2 dá 512.256 bytes por token. Vezes 8.192 dá 4.196.401.152 bytes, cerca de 4,20 GB para uma sequência. Uma execução de treinamento tem muitos milhões dessas sequências, e é por isso que existe a questão de armazenar versus recalcular.

</details>

3. ▢ Mantendo as 256 maiores entradas, cada uma com uma probabilidade de 2 bytes e um índice de 4 bytes, qual o tamanho do registro de um token, e quantas vezes menor do que a distribuição completa isso é?

<details markdown="1"><summary>Verificação</summary>

256 vezes 6 dá 1.536 bytes, que é 333,5 vezes menor do que 512.256. O k de 256 e os tamanhos em bytes são suposições desta lição, não números do Gemma 2. O registro também deixa de fora a cauda da distribuição, que precisa ser renormalizada ou agrupada em um bucket, e essa escolha muda o alvo.

</details>

4. ▢ Um post de fórum diz que o Gemma 2 treinou com uma distribuição do professor armazenada em top-256. O que você faz com essa alegação?

<details markdown="1"><summary>Verificação</summary>

Procure-a no relatório. O relatório enuncia a loss, as contagens de tokens e as ablações, e não descreve como a distribuição foi fornecida. Então a alegação não é verificável a partir do relatório. Trate-a como sem apoio, anote o que falta e procure uma fonte primária, como o texto dos autores, antes de depender dela.

</details>

5. ▢ Na Tabela 11 do Minitron, podar mais retreinar de forma convencional chegou a MMLU 24,57 e podar mais destilar chegou a 37,81, com a destilação em menos tokens. Por que as contagens de tokens são 150B e 100B, e qual é o limite da tabela?

<details markdown="1"><summary>Verificação</summary>

Eles comparam com compute igual, e a destilação gasta parte do seu orçamento no forward pass do professor, então recebe 100B tokens contra 150B. A tabela é de um único modelo de 4B podado do Nemotron-4 15B. Os autores a usam para mostrar que a destilação supera o retreinamento convencional depois da poda. Ela não mostra o ganho para outros professores, tamanhos ou benchmarks.

</details>

6. ▢ A correção do professor no artigo de acompanhamento do Minitron faz fine-tuning do professor em cerca de 100B tokens antes de destilar. Quando ela é necessária, e a quê os autores atribuem o problema quando ela é pulada?

<details markdown="1"><summary>Verificação</summary>

Ela é necessária quando os dados originais de pré-treinamento do professor não estão disponíveis, então os dados de destilação têm uma distribuição diferente. Os autores dizem que o professor dá então uma orientação subótima, e levantam a hipótese de que é porque a distribuição dos tokens de subpalavras difere entre os dados originais do professor e os dados usados para destilar. A explicação é hipótese deles.

</details>

## Prática no mundo real

- [ ] Rode o script de armazenamento com o seu próprio tamanho de vocabulário e com k definido como 64 e 1.024, e anote as três razões de custo.
- [ ] Abra a Tabela 11 do artigo do Minitron e encontre a marcação de iso-compute. Anote qual linha usou o professor e quantos tokens ela viu.
- [ ] Amanhã: sem consultar anotações, enuncie as três contagens de tokens do Gemma 2 e a aritmética de armazenamento para um token, e depois diga o que o relatório deixa sem dizer sobre o professor.

## Para ir além

- [Losses de Destilação](../reference/distillation-losses.md)
- [Artigo científico: "Gemma 2: Improving Open Language Models at a Practical Size", Gemma Team, 2024](https://arxiv.org/abs/2408.00118)
- [Artigo científico: "Compact Language Models via Pruning and Knowledge Distillation", Muralidharan et al., 2024](https://arxiv.org/abs/2407.14679)
- [Artigo científico: "LLM Pruning and Distillation in Practice: The Minitron Approach", Sreenivas et al., 2024](https://arxiv.org/abs/2408.11796)
- [Recursos](../RESOURCES.md)

---

Não ficou claro? Releia a fonte principal no topo, já que esta lição a comprime e é na compressão que o entendimento escapa. Consulte o [glossário](../GLOSSARY.md) para qualquer termo que pareceu escorregadio.

Se o problema é a lição em si, e não o material, isso é um defeito: [abra uma issue](https://github.com/TokenCemetery/teach/issues).
