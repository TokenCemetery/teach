---
title: "22. Contaminação e design de dados held-out"
description: "Dividir pela chave certa e dimensionar para a pergunta"
type: lesson
---

# Lição 22. Contaminação e design de dados held-out

**Ligação com a missão:** Um conjunto held-out em que você não pode confiar é pior do que nenhum, porque produz decisões erradas com confiança.
**Fonte principal:** [Código: lm-evaluation-harness, EleutherAI](https://github.com/EleutherAI/lm-evaluation-harness)
**Pré-requisitos:** [Lição 21](0021-building-the-dataset.md)

## Aquecimento

1. ▢ Por que deduplicar antes de dividir?

<details markdown="1"><summary>Verificação</summary>

Um par duplicado atravessando a divisão coloca um exemplo de treinamento no conjunto held-out, então o desempenho held-out mede memorização.

</details>

2. ▢ O que o fine-tuning ensina mal?

<details markdown="1"><summary>Verificação</summary>

Fatos novos, raciocínio que ainda não existe, informação atual e cálculo preciso. Ele ensina bem formato, tom e consistência.

</details>

3. ▢ Qual checkpoint você entrega?

<details markdown="1"><summary>Verificação</summary>

O do mínimo held-out, o que pressupõe um conjunto held-out em que você possa confiar.

</details>

## Saiba isto

### Dois tipos de contaminação

**A sua contaminação.** Exemplos de teste que também aparecem, de forma exata ou quase, no seu conjunto de treinamento. Inteiramente sob o seu controle, e inteiramente culpa sua quando acontece.

**Contaminação herdada.** Exemplos de teste que apareceram no corpus de *pré-treinamento* do base model. Fora do seu controle, em grande parte indetectável de fora, e o motivo de as pontuações de benchmarks públicos deverem ser lidas com desconfiança. Se um benchmark é anterior ao base model e vive na web pública, suponha alguma exposição.

A consequência prática: **um benchmark público é um sinal fraco para a sua decisão.** Ele pode medir a recordação de algo que o base já viu. Os seus próprios dados held-out, recém-construídos, são o sinal forte, e são a única coisa em que você de fato pode confiar.

### Dividindo direito

A divisão aleatória é o padrão e com frequência está errada. Aquilo *pelo qual* você divide determina que generalização você está medindo.

| Dividir por | Mede | Use quando |
|---|---|---|
| Exemplo aleatório | Generalização para novos exemplos | Os exemplos são genuinamente independentes |
| Grupo ou entidade | Generalização para novas entidades | Vários exemplos compartilham um cliente, documento, autor |
| Tempo | Generalização para o futuro | Os dados têm qualquer estrutura temporal |

O **vazamento por grupo** é a falha silenciosa clássica. Dez exemplos derivados de um único documento de origem, divididos de forma aleatória, colocam alguns no treino e alguns no teste. O modelo viu o conteúdo desse documento e a sua pontuação held-out reflete isso. Divida por documento.

![Seis exemplos, quatro do documento A e dois do B, divididos de duas formas. Dividindo ao acaso, os exemplos de A caem tanto na caixa de treino quanto na de teste; dividindo por documento, todo o A fica em uma caixa e todo o B na outra.](images/on-both-sides.svg)

Os mesmos seis exemplos estão nos dois painéis; só muda a atribuição. À esquerda, um documento está nas duas caixas, que é o vazamento, e nenhuma disciplina held-out em outro lugar o desfaz.

O **vazamento temporal** é o outro. Treinar com dados posteriores ao seu período de teste significa que o modelo viu o futuro, e a sua pontuação é otimista de um modo que não sobrevive à implantação. Qualquer dataset com dimensão temporal deve ser dividido por tempo, e essa é a divisão que as pessoas mais pulam porque o aleatório é mais fácil.

### Três divisões, e não duas

- **Treino.** O que o modelo ajusta.
- **Validação.** O que você usa para escolher checkpoints, rank, learning rate e todo o resto.
- **Teste.** Tocado uma vez, no fim, para estimar o desempenho real.

O motivo para três é que selecionar contra um conjunto é se ajustar a ele. Escolha o seu checkpoint pela validação, compare vinte configurações na validação, escolha a melhor, e a pontuação de validação agora é otimista em uma quantidade proporcional ao número de escolhas que você fez contra ela. É por isso que o conjunto de teste existe e por que ele é usado uma vez.

**Na prática as pessoas usam duas, e depois se perguntam por que a implantação rende menos do que a avaliação.** A diferença é exatamente a quantidade de seleção que fizeram.

### Detectando a sua própria contaminação

Deduplique contra o conjunto de teste de forma explícita, e não só dentro do conjunto de treinamento:

1. Normalize: minúsculas, colapse espaços em branco, remova a pontuação.
2. Hash de correspondência exata entre treino e teste. Remova do treino qualquer colisão.
3. Detecção de quase duplicatas com MinHash ou similaridade de embeddings, usando um limiar que você tenha examinado à mão.
4. **Leia você mesmo os pares de maior similaridade.** Limiares são chutes; os seus olhos são a calibração.

O passo 4 é o que as pessoas pulam e é o que encontra os problemas reais.

### Dimensionando o conjunto held-out

Conjuntos held-out costumam ser pequenos demais para sustentar as conclusões tiradas deles. O formato aproximado: distinguir pequenas diferenças exige muitos exemplos, e o número cresce de forma quadrática à medida que a diferença que lhe importa diminui.

| Diferença que você quer detectar | Escala aproximada necessária |
|---|---|
| 10 pontos percentuais | Algumas centenas |
| 5 pontos percentuais | Várias centenas a mil |
| 1 a 2 pontos percentuais | Milhares |

Então um conjunto held-out de 50 exemplos pode dizer se o modelo funciona, e só isso. Ele não consegue dizer se o rank 32 superou o rank 16 por dois pontos, e tratá-lo como se conseguisse é um erro muito comum.

O corolário: se você tem 200 exemplos held-out, não faça uma varredura de doze configurações. O vencedor da varredura é em grande parte ruído, e você gastou computação para selecionar uma configuração aleatória.

### Comparação pareada

Ao comparar dois modelos, avalie os dois nos **mesmos exemplos** e compare por exemplo. A comparação pareada remove a variância da dificuldade dos exemplos e detecta diferenças menores com menos exemplos do que comparar duas médias independentes. Não custa nada além de contabilidade.

Guarde os resultados por exemplo, e não só o agregado. "O modelo B é 3 pontos melhor" é muito menos útil do que "o B consertou 14 exemplos que o A errou e quebrou 6 que o A acertou", e os seis são onde você aprende alguma coisa.

## Prática

1. ▢ Distinga a sua contaminação da contaminação herdada e diga o que cada uma implica.

<details markdown="1"><summary>Verificação</summary>

A sua: exemplos de teste que também estão no seu conjunto de treinamento. Evitável, detectável, sua responsabilidade.

Herdada: exemplos de teste no corpus de pré-treinamento do base model. Incontrolável, em grande parte indetectável, e o motivo de as pontuações de benchmarks públicos serem evidência fraca para a sua decisão.

A implicação é confiar em dados held-out privados recém-construídos acima de qualquer benchmark público.

</details>

2. ▢ O seu dataset tem 500 exemplos derivados de 50 documentos de origem. Você divide de forma aleatória e obtém 96% de acurácia held-out. O que está errado?

<details markdown="1"><summary>Verificação</summary>

Vazamento por grupo. Exemplos do mesmo documento estão nas duas divisões, então o modelo viu o conteúdo desse documento e a pontuação reflete recordação.

Divida por documento: todos os exemplos de um documento vão para um lado. Espere que o número honesto seja substancialmente menor.

</details>

3. ▢ Por que três divisões, e não duas?

<details markdown="1"><summary>Verificação</summary>

Porque selecionar contra um conjunto é se ajustar a ele. Toda escolha de checkpoint e comparação de configurações feita na validação torna a pontuação de validação otimista.

O conjunto de teste fica intocado até o fim, então dá uma estimativa não enviesada. Com apenas duas divisões, o número que você reporta inclui toda a sua seleção, que é precisamente a diferença que as pessoas veem entre avaliação e implantação.

</details>

4. ▢ Você tem 80 exemplos held-out e quer saber se o rank 64 supera o rank 16. Consegue?

<details markdown="1"><summary>Verificação</summary>

Não, a menos que a diferença seja muito grande. Oitenta exemplos podem sustentar a detecção de uma oscilação de dez pontos ou mais; a diferença entre dois ranks razoáveis costuma ser de poucos pontos, no máximo.

Consiga mais dados held-out ou aceite que esta pergunta não pode ser respondida com o que você tem. Respondê-la mesmo assim produz uma decisão errada com confiança.

</details>

5. ▢ Qual divisão é mais frequentemente pulada, e o que pulá-la custa?

    - a) Dividir os dados por tempo quando eles têm ordem temporal
    - b) Dividir os dados de forma aleatória entre todos os exemplos disponíveis
    - c) Dividir os dados por comprimento de saída em faixas balanceadas
    - d) Dividir os dados por qual anotador produziu o label

<details markdown="1"><summary>Verificação</summary>

**a)** Dividir os dados por tempo quando eles têm ordem temporal.

O aleatório é mais fácil e é o padrão, então a estrutura temporal é ignorada. O custo é treinar com dados posteriores ao período de teste: o modelo viu o futuro, e a pontuação não sobrevive à implantação.

</details>

6. ▢ Por que a comparação pareada é melhor do que comparar duas médias?

<details markdown="1"><summary>Verificação</summary>

Ela remove a variância devida à dificuldade dos exemplos ao comparar os dois modelos nos mesmos itens, então detecta diferenças menores com menos exemplos.

Também produz o artefato mais útil: quais exemplos específicos melhoraram e quais regrediram. As regressões são onde está o aprendizado.

</details>

## Prática no mundo real

- [ ] Verifique se o seu dataset tem uma estrutura de agrupamento: documento, cliente, autor, sessão. Se existir, divida de novo por ela e compare os dois números held-out.
- [ ] Execute a detecção de quase duplicatas entre treino e teste. Leia à mão os vinte pares de maior similaridade.
- [ ] Divida em três conjuntos e escreva a regra do que cada um pode ser usado. Depois mantenha-se nela.
- [ ] Amanhã: calcule quantos exemplos held-out você precisaria para detectar a diferença que de fato lhe importa. Compare com quantos você tem.

## Para ir além

- [Código: lm-evaluation-harness, EleutherAI](https://github.com/EleutherAI/lm-evaluation-harness)
- [Docs: Splitting datasets, Hugging Face Datasets](https://huggingface.co/docs/datasets/main/en/process)
- [Lição 23. Métricas que significam alguma coisa](0023-metrics-that-mean-something.md)

---

Não ficou claro? Releia a fonte principal no topo, já que esta lição a comprime e é na compressão que o entendimento escapa. Consulte o [glossário](../GLOSSARY.md) para qualquer termo que pareceu escorregadio.

Se o problema é a lição em si, e não o material, isso é um defeito: [abra uma issue](https://github.com/TokenCemetery/teach/issues).
