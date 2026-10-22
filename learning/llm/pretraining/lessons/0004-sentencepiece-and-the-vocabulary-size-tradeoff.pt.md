---
title: "4. SentencePiece e o tradeoff do tamanho do vocabulário"
description: "Tokenizar texto bruto sem um pré-tokenizer e o que um vocabulário maior ou menor realmente custa"
type: lesson
---

# Lição 4. SentencePiece e o tradeoff do tamanho do vocabulário

**Ligação com a missão:** "Treinar um tokenizer e defender um tamanho de vocabulário em função do seu efeito no comprimento das sequências e no tamanho da tabela de embeddings" é o segundo item em O sucesso se parece com isto. A Lição 3 construiu o algoritmo de fusão; esta lição cobre como treiná-lo sem supor fronteiras de palavras e a própria decisão do tamanho.
**Fonte principal:** [Artigo científico: "SentencePiece: A simple and language independent subword tokenizer and detokenizer for Neural Text Processing", Kudo e Richardson, 2018](https://arxiv.org/abs/1808.06226)
**Pré-requisitos:** [Lição 3](0003-byte-pair-encoding-from-scratch.md)

## Aquecimento

1. ▢ No algoritmo de byte-pair encoding, o que o número de operações de fusão realizadas determina?

<details markdown="1"><summary>Verificação</summary>

O tamanho final do vocabulário: ele é igual ao conjunto inicial de caracteres mais um símbolo novo por fusão realizada.

</details>

2. ▢ Por que três pares do exemplo trabalhado da Lição 3 (`(e, s)`, `(s, t)`, `(t, </w>)`) acabaram todos fundidos em poucos passos uns dos outros, qualquer que tenha sido o primeiro a ser fundido?

<details markdown="1"><summary>Verificação</summary>

Todos estavam empatados na mesma frequência porque todos vinham da mesma substring repetida, "est". Fundir qualquer um deles reetiquetava os outros como novos pares com a mesma contagem em vez de desfazer o empate, então os três foram fundidos juntos em pouco tempo, não importa qual tenha sido fundido primeiro.

</details>

## Saiba isto

### Por que supor fronteiras de palavras deixa de funcionar

O byte-pair encoding, como a Lição 3 o descreveu, costuma rodar sobre um **pré-tokenizer**: algo que primeiro divide o texto bruto em palavras, de modo que o BPE só precise aprender fusões dentro de uma palavra. Para o inglês, dividir por espaços em branco é um pré-tokenizer fácil e na maior parte confiável. Ele não é independente de idioma: muitas línguas escritas amplamente usadas, incluindo o japonês e o chinês, não delimitam palavras com espaços, então um pré-tokenizer de espaços em branco não tem nada sensato para dividir antes mesmo de o BPE começar. Construir um pré-tokenizer diferente por idioma, ou por alfabeto, mina a ideia de um único procedimento de treinamento de tokenizer que funcione em qualquer lugar.

### Treinando direto em sentenças brutas

O SentencePiece de Kudo e Richardson elimina a etapa de pré-tokenização em vez de tentar consertá-la para cada idioma: ele treina o seu modelo de subpalavras diretamente sobre texto bruto de sentenças, sem nenhuma suposição embutida de fronteiras de palavras preexistentes. O próprio espaço em branco é tratado como um símbolo comum da entrada, em geral representado com um marcador dedicado para que o espaçamento original possa ser reproduzido exatamente na destokenização, e não como algo em que dividir antes de o treinamento começar. Isso torna o mesmo procedimento de treinamento independente de idioma, o que o artigo sustenta com um experimento de tradução automática inglês-japonês: treinar de ponta a ponta em sentenças brutas alcançou acurácia comparável à de treinar em texto que já tinha sido segmentado em palavras por uma ferramenta separada.

### Um toolkit, dois algoritmos de treinamento

O SentencePiece não é um segundo algoritmo concorrente do BPE; é um toolkit que implementa o BPE (o procedimento de fusão da Lição 3) junto com um segundo algoritmo de treinamento, um treinador de **modelo de linguagem unigram**, que trabalha na direção oposta. Em vez de partir de caracteres individuais e fazer as fusões crescerem para cima, ele parte de um grande conjunto de subpalavras candidatas e poda repetidamente até o tamanho de vocabulário alvo, removendo a cada passo os pedaços de que a verossimilhança do modelo sentiria menos falta. Qualquer um dos algoritmos de treinamento produz o mesmo formato de resultado: um vocabulário fixo de pedaços de subpalavras e uma forma determinística de dividir texto bruto novo neles.

### O tradeoff do tamanho do vocabulário

O tamanho de vocabulário alvo, seja qual for a forma como foi treinado, é um único número que puxa em mais de uma direção ao mesmo tempo:

- Um vocabulário **maior** codifica o mesmo texto em menos tokens, em média, já que mais substrings comuns ganham o seu próprio símbolo. Sequências de tokens mais curtas significam menos compute gasto para fazer atenção e gerar sobre a mesma entrada.
- Um vocabulário **maior** também significa uma tabela de embeddings maior e uma projeção de saída maior (em geral a mesma matriz, amarrada), o que é contagem de parâmetros que escala diretamente com o tamanho do vocabulário, independentemente da profundidade ou largura do resto do modelo.
- Um vocabulário **maior** espalha o sinal de treinamento de forma mais rarefeita: com o mesmo corpus fatiado em mais pedaços distintos para escolher, qualquer token específico, especialmente um mais raro, é visto menos vezes por passada pelos dados.
- Um vocabulário **menor** inverte as três coisas: sequências de tokens mais longas por entrada, uma tabela de embeddings e de saída menor e sinal de treinamento mais denso por token, ao custo de dividir palavras comuns em mais pedaços cada.

Nenhum tamanho de vocabulário vence em todos os eixos ao mesmo tempo, então ele é escolhido em função do formato e do orçamento de um modelo específico, e não lido de uma fórmula. Um exemplo real e verificável: o artigo do LLaMA relata que tokenizou os seus dados de treinamento com byte-pair encoding por meio da implementação do SentencePiece, dividindo todos os números em dígitos individuais e recorrendo a bytes brutos para representar qualquer caractere UTF-8 que o vocabulário treinado não cobrisse de outra forma, de modo que nenhum caractere de entrada seja realmente irrepresentável, qualquer que seja o tamanho de vocabulário escolhido.

## Prática

1. ▢ Um tokenizer construído sobre um pré-tokenizer de espaços em branco, treinado só em inglês, é aplicado sem modificação a texto em japonês, que não tem espaços entre as palavras. O que dá errado e o que o SentencePiece faz de diferente que evita isso?

<details markdown="1"><summary>Verificação</summary>

O pré-tokenizer de espaços em branco não tem nada sensato para dividir, já que o japonês não delimita palavras com espaços, então ele não consegue entregar ao BPE pedaços razoáveis do tamanho de palavras dentro dos quais fundir. O SentencePiece evita isso treinando diretamente em texto bruto de sentenças, sem suposição de fronteiras de palavras preexistentes, tratando o espaço em branco como um símbolo comum em vez de uma divisão prévia obrigatória.

</details>

2. ▢ Uma equipe dobra o tamanho do vocabulário do seu tokenizer mantendo exatamente a mesma dimensão oculta e a mesma profundidade do modelo. Qual destas descreve melhor o resultado?

    - a) As sequências ficam mais curtas em média e as tabelas de embeddings e de saída encolhem
    - b) As sequências ficam mais curtas em média, mas as tabelas de embeddings e de saída crescem
    - c) As sequências ficam mais longas em média, mas as tabelas de embeddings e de saída encolhem
    - d) Nem o comprimento das sequências nem a contagem de parâmetros são afetados pelo tamanho do vocabulário

<details markdown="1"><summary>Dica</summary>

O tamanho do vocabulário afeta duas coisas diferentes: em quantos tokens um pedaço de texto se transforma e o tamanho da tabela que mapeia cada token a um vetor. Considere cada uma separadamente.

</details>

<details markdown="1"><summary>Verificação</summary>

**b)** Um vocabulário maior significa que mais substrings comuns ganham o seu próprio token, o que encurta as sequências, enquanto as tabelas de embeddings e de projeção de saída (em geral amarradas) escalam diretamente com o tamanho do vocabulário, então crescem. (a) e (c) erram cada uma uma das duas direções, e (d) ignora as duas.

</details>

3. ▢ Nomeie um eixo em que um vocabulário menor é melhor do que um maior e um eixo em que ele é pior.

<details markdown="1"><summary>Verificação</summary>

Melhor: sinal de treinamento mais denso por token (cada token é visto mais vezes por passada pelo mesmo corpus) ou uma tabela de embeddings e de saída menor. Pior: sequências de tokens mais longas por entrada, já que palavras comuns são divididas em mais pedaços, o que custa mais compute para fazer atenção e gerar.

</details>

4. ▢ Qual destas descreve melhor o que o SentencePiece é, como software?

    - a) Um único algoritmo de tokenização novo que substitui o byte-pair encoding
    - b) Um toolkit que implementa tanto o byte-pair encoding quanto um treinador de modelo de linguagem unigram, direto sobre texto bruto, sem exigir uma etapa de pré-tokenização
    - c) Apenas um pré-tokenizer, feito para rodar antes de uma implementação de BPE separada
    - d) Uma forma de treinar um modelo sem nenhum vocabulário fixo

<details markdown="1"><summary>Verificação</summary>

**b)** O SentencePiece reúne dois algoritmos de treinamento, o byte-pair encoding e um modelo de linguagem unigram, e a sua característica distintiva é treinar diretamente a partir de sentenças brutas. (a) está errada porque ele ainda implementa o BPE em vez de substituí-lo. (c) inverte a contribuição real do SentencePiece, que é eliminar a etapa de pré-tokenização. (d) não descreve nenhum tokenizer real discutido nesta trilha; os dois algoritmos ainda produzem um vocabulário fixo.

</details>

## Prática no mundo real

- [ ] Encontre o tamanho de vocabulário relatado de um tokenizer a que você tenha acesso, seja por uma biblioteca ou pelos arquivos de tokenizer publicados de um modelo hospedado.
- [ ] Se você conseguir acessar dois tokenizers com tamanhos de vocabulário notavelmente diferentes, codifique a mesma sentença com os dois e compare diretamente as contagens de tokens resultantes.
- [ ] Amanhã: para um projeto ou caso de uso específico cuja escala você conhece (um assistente de chat, um modelo focado em código, uma ferramenta para um idioma de poucos recursos), decida qualitativamente se você se inclinaria para um vocabulário maior ou menor do que o de um modelo convencional e anote qual único eixo do tradeoff motivou a sua resposta.

## Para ir além

- [Artigo científico: "SentencePiece: A simple and language independent subword tokenizer and detokenizer for Neural Text Processing", Kudo e Richardson, 2018](https://arxiv.org/abs/1808.06226)
- [Recursos](../RESOURCES.md)

---

A etapa 1 cobriu o que entra em um corpus e o que é removido dele; a etapa 2 cobriu como esse corpus é transformado em tokens. A etapa 3 se volta para a pergunta que está acima das duas: dada uma contagem de parâmetros, quantos desses tokens valem a pena para treinar.

Não ficou claro? Releia a fonte principal no topo, já que esta lição a comprime e é na compressão que o entendimento escapa. Consulte o [glossário](../GLOSSARY.md) para qualquer termo que pareceu escorregadio.

Se o problema é a lição em si, e não o material, isso é um defeito: [abra uma issue](https://github.com/TokenCemetery/teach/issues).
