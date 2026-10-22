---
title: "27. Quando a resposta de sempre está errada"
description: "Reconhecer quando pesos de 4 bits ou uma receita padrão é a escolha errada e resolver a disputa a partir da fonte primária"
type: lesson
---

# Lição 27. Quando a resposta de sempre está errada

**Ligação com a missão:** A trilha termina confiando a você a decisão sobre uma quantização e a tarefa de explicá-la a outra pessoa. "Use pesos de 4 bits" e "o AWQ supera o GPTQ" são as respostas de sempre, e cada uma é verdadeira para alguns modelos, tarefas e hardware e falsa para outros. Esta lição é o método para descobrir qual, e os casos em que a resposta de sempre falha.
**Fonte principal:** [Artigo científico: "Scaling Laws for Precision", Kumar et al., 2024](https://arxiv.org/abs/2411.04330), seções 1 a 3
**Pré-requisitos:** [Lição 25](0025-choosing-a-scheme.md), [Lição 26](0026-reviewing-a-quantization-claim.md), [Quantização pós-treinamento](../GLOSSARY.md), [Limitado por compute](../GLOSSARY.md), [Quantização somente de pesos](../GLOSSARY.md)

## Aquecimento

1. ▢ Por que uma ativação massiva ou uma feature outlier arruína uma scale per-tensor, e qual correção diminui o grupo em vez de manter os outliers em alta precisão?

<details markdown="1"><summary>Verificação</summary>

A scale é definida pelo maior valor, então um valor enorme deixa quase todos os outros em poucos níveis perto de zero. Scales per-group diminuem o grupo para que o outlier desperdice apenas os níveis do seu próprio grupo (lições 7, 8 e 6).

</details>

2. ▢ O que um calibration set contribui para o GPTQ e para o AWQ, e como um incompatível aparece?

<details markdown="1"><summary>Verificação</summary>

Estatísticas de ativação de entradas representativas: o GPTQ as usa para a compensação de erro de segunda ordem, o AWQ para encontrar quais canais de pesos encontram ativações grandes. Um conjunto incompatível aparece como um modelo que pontua bem em texto parecido com os dados de calibração e pior no tráfego a que não se parecia (lições 10, 11 e 12).

</details>

3. ▢ O que é um flip, e por que ele pode ser grande quando a acurácia não muda?

<details markdown="1"><summary>Verificação</summary>

Uma resposta que mudou de correta para incorreta ou o inverso entre o baseline e o modelo quantizado. Ganhos e perdas se cancelam na média, então a acurácia pode ser igual enquanto muitas respostas individuais se movem (lições 21 e 26).

</details>

## Saiba isto

### O método

Uma resposta de sempre chega como um slogan sem as suas condições. Quatro passos decidem se ela vale para você.

1. **Encontre a fonte primária.** O artigo, não a postagem que o cita, lido pelo que foi realmente medido.
2. **Confira o modelo, o tamanho e a data.** Quais famílias de modelos, quão grandes, treinadas com quanto, medidas quando. Um resultado em modelos de 2022 diz pouco sobre uma receita de 2024.
3. **Confira o que a alegação cobre.** Acurácia zero-shot contra bits totais não é throughput de serving, e uma média sobre tarefas acadêmicas não é chat aberto.
4. **Teste nas suas próprias tarefas.** Se a fonte e o seu caso diferem, o resultado que resolve é o seu (lição 22).

Nenhum dos casos abaixo diz que a resposta de sempre está sempre errada. Cada um diz o que a sua fonte sustenta e onde ela para.

### Caso 1: um modelo muito treinado

Kumar et al. ajustam leis de escala "cientes de precisão" e descobrem que a degradação da quantização pós-treinamento aumenta conforme um modelo é treinado com mais dados, "eventualmente tornando os dados de pré-treinamento adicionais ativamente prejudiciais" ([resumo](https://arxiv.org/abs/2411.04330)). A intuição deles: um modelo treinado com mais dados comprime mais informação nos seus pesos, então perturbá-los machuca mais. Eles chamam de "overtrained" os modelos com uma razão muito alta entre tokens de treinamento e parâmetros e observam que o Llama-3-8B é treinado até uma razão de cerca de 2000.

Leia o escopo. Eles ajustam as suas leis em mais de 465 execuções de pré-treinamento e validam em modelos de até 1.7B de parâmetros treinados com até 26B de tokens. Eles observam que é preciso uma quantidade absurda de dados para o pré-treinamento extra se tornar prejudicial em precisões comumente usadas, como 8 bits, mas que em modelos muito overtrained os efeitos de degradação se tornam não triviais em torno de 5 bits e dominantes abaixo disso. Então a alegação é que a resposta usual de 4 bits fica mais arriscada conforme o orçamento de treinamento por parâmetro cresce, e a evidência são modelos de pequena escala mais uma lei ajustada. Não é uma medição de quanto um checkpoint específico do Llama 3 perde.

Existe um resultado contrastante. Kurtic et al. mediram modelos Llama 3.1 quantizados de 8B, 70B e 405B e descobriram o W4A16 recuperando 99.36 por cento da média do bf16 nas tarefas do Open LLM Leaderboard V1, usando um GPTQ ajustado ([Kurtic et al., 2024](https://arxiv.org/abs/2411.02355)). Os dois não se resolvem mutuamente. Um é uma lei ajustada em modelos pequenos, o outro uma medição de uma família com uma receita ajustada e tarefas promediadas. A lição é tratar um modelo muito treinado como motivo para medir com mais cuidado, não como um veredito para nenhum dos lados.

### Caso 2: um modelo pequeno, ou um modelo de raciocínio

Kurtic et al. relatam que os menores modelos perdem um pouco mais em INT4. Os benchmarks de raciocínio deles, executados em modelos DeepSeek-R1-Distill, mostram isso em números: a recuperação da média do bf16 para o W4A16-INT foi 99.5 por cento para o Qwen-32B e 98.3 por cento para o Llama-70B, 97.2 por cento para o Llama-8B e 93.5 por cento para o Qwen-1.5B, para o qual o W8A8-INT recuperou 96.9 por cento e o W8A8-FP 100.3 por cento. Um estudo separado de modelos de raciocínio quantizados, [Liu et al., 2025](https://arxiv.org/abs/2504.04823), conclui que a quantização sem perdas é alcançável com W8A8 ou W4A16, mas há riscos significativos de acurácia em larguras em bits menores. O resumo dele nomeia tamanho do modelo, origem do modelo e dificuldade da tarefa como os determinantes.

Note o ruído também. No AIME24, o modelo de 1.5B marcou 30.1 com uma margem reportada de 5.3 em bf16 e 24.6 com uma margem de 5.1 em W4A16, então diferenças em um único benchmark com conjuntos pequenos se sobrepõem às suas próprias margens. A média sobre as tarefas diz que o modelo pequeno perdeu mais. A tarefa isolada não provaria isso.

### Caso 3: contexto longo, onde a preocupação não se sustenta

É fácil supor que o contexto longo quebra sob quantização. No benchmark de contexto longo RULER, avaliado de 4k a 128k tokens, Kurtic et al. relatam recuperação média de pontuação de pelo menos 98 por cento nos três formatos, com o modelo de 405B não avaliado por ser proibitivamente caro. Esse é um benchmark no Llama 3.1 e não cobre a quantização do KV cache, que o artigo lista entre as coisas que não estudou. É um bom exemplo de uma preocupação usual que a fonte não sustenta, para o caso que ela mediu.

### Caso 4: serving limitado por compute

O 4 bits somente de pesos é a resposta de sempre para pressão de memória, e pressupõe que o trabalho é limitado pela largura de banda de memória. Os autores do MARLIN dão a aritmética: um token de entrada leva 2 FLOPs por peso e a GPU consegue executar cerca de 100 FLOPs no tempo que leva para carregar um peso de 4 bits, então o carregamento de memória só domina enquanto o batch fica abaixo de cerca de 50 ([Frantar et al., 2024](https://arxiv.org/abs/2408.11743)). A mesma razão entre compute e largura de banda faz um peso de 16 bits levar quatro vezes mais para carregar, então o ponto de cruzamento para o bf16 fica perto do batch 200. Quantizar os pesos move o ponto de cruzamento para baixo, e é por isso que o ganho diminui conforme os batches crescem.

Os métodos INT4 existentes, relata o QServe, sofrem de 20 a 90 por cento de overhead de dequantização e aceleram apenas a inferência com batch baixo ([Lin et al., 2024](https://arxiv.org/abs/2405.04532)). Nos resultados de serving assíncrono de Kurtic et al., o W8A8 domina o throughput. Para um serviço limitado por throughput em hardware moderno, a resposta usual de 4 bits é a errada.

### Caso 5: quando o fp8 é o padrão mais seguro

Se a GPU calcula fp8 nativamente, o W8A8-FP é efetivamente sem perdas em todo tamanho de modelo nos dados de Kurtic et al., e não precisa de dados de calibração porque eles quantizam com round-to-nearest. Um W8A8-INT bem ajustado perdeu de 1 a 3 por cento, e precisou de SmoothQuant e de dados de calibração melhores em 70B. Então, onde o hardware suporta e a memória cabe, o fp8 é a primeira tentativa de menor risco, e os 4 bits precisam conquistar o seu lugar com uma necessidade de memória ou de latência de decode.

### Resolvendo uma disputa a partir da fonte primária

Dois colegas dizem duas coisas.

- **"O AWQ sempre supera o GPTQ."** Abra a Tabela 1 de Kurtic et al. em vez de discutir. Nos benchmarks acadêmicos, o AWQ liderou o GPTQ por apenas 0.23 e 0.35 ponto em 8B e 70B, um quase empate. Nos benchmarks do mundo real (Arena-Hard, HumanEval, MBPP), o GPTQ liderou o AWQ por 2.9 pontos em 8B (52.3 contra 49.4) e por 0.8 em 70B. Eles atribuem achados anteriores que favoreciam o AWQ a hiperparâmetros subótimos e dão o seu próprio setup: GPTQ com clipping ótimo por MSE onde a comparação anterior usou abs-max, um calibration set melhor que o padrão C4 e tamanho de grupo 128 para ambos. Depois confira o ruído: no Arena-Hard em 8B, as duas execuções do modelo bf16 marcaram 25.1 e 26.5, então uma diferença perto de 1 ponto está dentro da variação entre execuções. O que a fonte sustenta: nenhum método vence sempre, o ranking se moveu com a receita e o tipo de tarefa, e os autores são uma equipe que também escolheu o GPTQ como método. Execute os dois nas suas tarefas.
- **"A perplexity subiu 0.1, então está tudo bem."** Pergunte: em relação a qual baseline, em qual texto e janela, e o que aconteceu com as respostas individuais? Dutta et al. encontraram esquemas com acurácia a 0 a 2 por cento do baseline e flips de até 13.6 por cento, e modelos comprimidos com muitos flips pontuando significativamente pior no MT-Bench. Uma mudança de perplexity de 0.1 é uma média e pode ser pequena ou grande dependendo do que ela promedia. A fonte sustenta "confira os flips e uma tarefa aberta", não "0.1 é pequeno demais para importar" nem "0.1 é grande demais".

## Prática

1. ▢ Um colega diz "o AWQ sempre supera o GPTQ." Qual tabela você abre, e o que confere nela?

<details markdown="1"><summary>Verificação</summary>

Abra a comparação direta em Kurtic et al. (Tabela 1) e confira o setup por trás dela: o mesmo tamanho de grupo, o método de clipping, o calibration set e se as tarefas são acadêmicas ou abertas. Ela mostra um quase empate em tarefas acadêmicas e uma liderança do GPTQ nas do mundo real. Não mostra que o GPTQ sempre vence, só que a alegação sobre o AWQ tem condições.

</details>

2. ▢ Um colega diz "Kumar et al. provaram que os 4 bits post-training vão destruir o nosso modelo muito treinado." O que o artigo sustenta?

    - a) Uma lei ajustada, então meça o seu modelo
    - b) Uma prova de que todo esquema de 4 bits falha
    - c) Um resultado apenas sobre treinar em fp4
    - d) Uma medição do checkpoint exato do seu modelo

<details markdown="1"><summary>Verificação</summary>

**a)** O artigo ajusta leis em execuções de até 1.7B de parâmetros e 26B de tokens e descobre que mais dados aumentam a degradação da quantização pós-treinamento, o que é um motivo para medir o seu modelo, não um veredito sobre ele. (b) exagera uma lei ajustada até uma prova. (c) está errada porque cobre a quantização pós-treinamento além da precisão de treinamento. (d) está errada porque ele não mediu nenhum checkpoint seu.

</details>

3. ▢ Preveja e depois execute. Usando o número do MARLIN de cerca de 100 FLOPs por carregamento de peso de 4 bits e 2 FLOPs por token por peso, preveja o batch size abaixo do qual a memória domina para pesos de 4 bits e para pesos de 16 bits se a razão entre compute e largura de banda da máquina for a mesma. Depois execute isto.

    ```python
    flops_per_weight_load_4bit = 100
    flops_per_token_per_weight = 2
    for name, bytes_per_weight in [("4-bit weights", 0.5), ("16-bit weights", 2.0)]:
        flops_per_byte = flops_per_weight_load_4bit / 0.5
        crossover = flops_per_byte * bytes_per_weight / flops_per_token_per_weight
        print(f"{name:15s} memory-bound below batch about {crossover:.0f}")
    ```

<details markdown="1"><summary>Dica</summary>

Um peso de 16 bits tem quatro vezes os bytes de um de 4 bits, então leva quatro vezes mais FLOPs para cobrir o seu carregamento.

</details>

<details markdown="1"><summary>Verificação</summary>

```text
4-bit weights   memory-bound below batch about 50
16-bit weights  memory-bound below batch about 200
```

O número de 4 bits é a própria estimativa do MARLIN, e o de 16 bits é esta aritmética sob a mesma suposição, não uma medição. O ponto se sustenta sem números exatos: quantizar os pesos reduz o batch size em que um serviço se torna limitado por compute, então um serviço que roda batches grandes ganha menos com 4 bits somente de pesos.

</details>

4. ▢ Da tabela de raciocínio de Kurtic et al.: o Qwen-1.5B marcou 30.1 (margem 5.3) no AIME24 em bf16 e 24.6 (margem 5.1) em W4A16-INT, com 93.5 por cento de recuperação média. Um colega diz "o AIME24 prova que os 4 bits o quebraram". O que você diz?

<details markdown="1"><summary>Verificação</summary>

Só no AIME24, as duas pontuações ficam dentro das margens reportadas uma da outra, então esse benchmark não prova isso. A recuperação média de 93.5 por cento em três tarefas, posta ao lado de 98 a 99 por cento para os modelos maiores, é a evidência mais forte de que o menor modelo perdeu mais. Nenhuma das duas diz que o modelo é inutilizável: o próximo passo é executar as suas próprias tarefas com amostras suficientes para distinguir a diferença do ruído.

</details>

5. ▢ Uma equipe tem GPUs H100, memória suficiente para um modelo de 8B em bf16 e um job em lote em que só o throughput importa. Um colega propõe AWQ de 4 bits "porque 4 bits é o padrão". Faça o argumento contra e diga o que mudaria a sua opinião.

<details markdown="1"><summary>Verificação</summary>

O job é limitado por compute em batches grandes, onde o 4 bits somente de pesos ganha pouco e a sua dequantização pode custar throughput (MARLIN, QServe), enquanto o W8A8-FP é efetivamente sem perdas nos dados de Kurtic et al. e domina os resultados de throughput assíncrono deles em hardware com fp8 nativo. A memória não é uma restrição. O que mudaria a sua opinião: uma comparação medida de throughput e qualidade no seu próprio batch size e nas suas tarefas mostrando o kernel de 4 bits na frente, ou um limite de memória que forçasse um modelo maior do que cabe em 8 bits.

</details>

## Prática no mundo real

- [ ] Pegue uma regra prática de quantização em que você confia (por exemplo "4 bits está bom") e rastreie-a até o artigo. Anote os modelos, os tamanhos, o ano e o que foi medido, e onde o seu caso difere.
- [ ] Abra a Tabela 1 de Kurtic et al. e anote em uma linha as diferenças de setup entre as execuções de GPTQ e de AWQ deles, para poder responder ao próximo argumento de "qual é melhor" a partir da tabela.
- [ ] Amanhã: para o modelo que você mais gostaria de quantizar, escreva o caso desta lição com maior chance de se aplicar a ele e a medição que mostraria se ele se aplica.

## Para ir além

- [Checklist de Revisão de Quantização](../reference/quantization-review-checklist.md)
- [Artigo científico: "Scaling Laws for Precision", Kumar et al., 2024](https://arxiv.org/abs/2411.04330)
- [Artigo científico: "Give Me BF16 or Give Me Death? Accuracy-Performance Trade-Offs in LLM Quantization", Kurtic et al., 2024](https://arxiv.org/abs/2411.02355)
- [Artigo científico: "Quantization Hurts Reasoning? An Empirical Study on Quantized Reasoning Models", Liu et al., 2025](https://arxiv.org/abs/2504.04823)
- [Recursos](../RESOURCES.md)

---

Este é o fim da trilha, e o hábito para o qual ela foi construída é o desta lição: um modelo quantizado é uma alegação sobre um formato numérico, um método, um kernel e um conjunto de tarefas, então encontre de onde a alegação vem, confira o que ela cobriu e meça nas suas próprias tarefas antes de defendê-la perante qualquer outra pessoa.

Não ficou claro? Releia a fonte principal no topo, já que esta lição a comprime e é na compressão que o entendimento escapa. Consulte o [glossário](../GLOSSARY.md) para qualquer termo que pareceu escorregadio.

Se o problema é a lição em si, e não o material, isso é um defeito: [abra uma issue](https://github.com/TokenCemetery/teach/issues).
