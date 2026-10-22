---
title: "3. Byte-Pair Encoding do zero"
description: "O algoritmo que transforma palavras raras e desconhecidas em sequências de unidades de subpalavra aprendidas, resolvido à mão"
type: lesson
---

# Lição 3. Byte-Pair Encoding do zero

**Ligação com a missão:** "Treinar um tokenizer e defender um tamanho de vocabulário em função do seu efeito no comprimento das sequências e no tamanho da tabela de embeddings" é o segundo item em O sucesso se parece com isto. Esta lição constrói o algoritmo que a maioria dos tokenizers ainda usa; a Lição 4 cobre o próprio tradeoff do tamanho do vocabulário.
**Fonte principal:** [Artigo científico: "Neural Machine Translation of Rare Words with Subword Units", Sennrich et al., 2015](https://arxiv.org/abs/1508.07909)
**Pré-requisitos:** [Lição 2](0002-deduplication-and-quality-filtering.md)

## Aquecimento

1. ▢ Nomeie uma coisa que a deduplicação remove de um corpus e uma coisa que a filtragem de qualidade remove e que a deduplicação não pegaria.

<details markdown="1"><summary>Verificação</summary>

A deduplicação remove texto repetido ou quase repetido que já existe em outro lugar do corpus. A filtragem de qualidade remove texto de baixo valor que não é cópia de nada, como texto padronizado ou gerado por máquina, que a deduplicação não tem como detectar.

</details>

## Saiba isto

### Por que um vocabulário fixo de palavras quebra

Um modelo que prevê uma palavra de uma lista fixa de palavras inteiras não tem como lidar com uma palavra que não estava na lista: um nome raro, um composto novo, um erro de digitação, uma palavra em um alfabeto que a lista não previu. Sennrich et al. nomearam isso diretamente para a tradução, onde é inevitável, já que a tradução é fundamentalmente um problema de vocabulário aberto: nenhuma lista fixa de palavras, por maior que seja, cobre todos os nomes, números e neologismos que um texto real vai conter. A solução deles foi parar de tokenizar em palavras inteiras e tokenizar em **unidades de subpalavra**: pedaços menores do que uma palavra, construídos de modo que uma palavra rara ou nunca vista ainda possa ser soletrada com pedaços que o modelo já viu antes.

### O algoritmo: fundir o par mais frequente, repetir

O byte-pair encoding era originalmente um algoritmo de compressão de dados, reaproveitado aqui para outro trabalho. Ele parte do menor vocabulário possível, os caracteres individuais, e constrói para cima:

1. Comece com cada palavra do texto de treinamento dividida em seus caracteres individuais, mais um marcador de fim de palavra.
2. Conte com que frequência cada par adjacente de símbolos ocorre lado a lado, em todo o texto (ponderado pela frequência).
3. Funda o par mais frequente em um único símbolo novo, em todos os lugares onde ele ocorre.
4. Repita os passos 2 e 3 por um número fixo de fusões.

O número de fusões é o único hiperparâmetro e define diretamente o tamanho do vocabulário: o vocabulário final é o conjunto inicial de caracteres mais um símbolo novo por fusão realizada. Uma palavra que nunca é totalmente fundida em um único símbolo é representada como uma sequência curta dos pedaços em que chegou a ser fundida, e é exatamente isso que permite codificar uma palavra nunca vista: ela recai sobre pedaços menores e já conhecidos, em vez de um único símbolo de palavra desconhecida.

### Um exemplo trabalhado

O artigo de Sennrich et al. dá diretamente este corpus de brinquedo: quatro palavras, já divididas em caracteres, com `</w>` marcando o fim de cada palavra, cada uma com uma frequência:

```text
{'l o w </w>': 5, 'l o w e r </w>': 2, 'n e w e s t </w>': 6, 'w i d e s t </w>': 3}
```

Contando cada par adjacente, ponderado pela frequência de cada palavra, três pares empatam como os mais frequentes, com contagem ponderada de 9 cada: `(e, s)`, `(s, t)` e `(t, </w>)`. Cada uma das duas palavras que contêm "est" (`newest`, frequência 6, e `widest`, frequência 3) contribui com uma ocorrência de cada par dentro dessa substring compartilhada, então `6 + 3 = 9` para os três. A regra do algoritmo, "fundir o par mais frequente", não diz por si só qual de três pares exatamente empatados fundir primeiro: esse detalhe fica por conta do que a implementação fizer ao desempatar, e não da definição do próprio algoritmo. Fundir qualquer um dos três também não desfaz o empate: como os três pares vêm da mesma substring repetida "est", fundir um deles (digamos `e`+`s` em `es`) apenas reetiqueta os outros como novos pares adjacentes com a mesma contagem (`es`+`t` e `t`+`</w>` ainda empatam em 9), de modo que os três acabam fundidos juntos nas próximas fusões, qualquer que seja o escolhido primeiro, e `newest` e `widest` terminam compartilhando um único pedaço `est`.

## Prática

1. ▢ Usando o corpus do exemplo trabalhado, `{'l o w </w>': 5, 'l o w e r </w>': 2, 'n e w e s t </w>': 6, 'w i d e s t </w>': 3}`, calcule a contagem ponderada do par adjacente `(l, o)`.

<details markdown="1"><summary>Dica</summary>

`(l, o)` aparece uma vez por ocorrência de uma palavra que começa com "lo...". Quais palavras são essas e com que frequências?

</details>

<details markdown="1"><summary>Verificação</summary>

`(l, o)` aparece em `low` (frequência 5) e em `lower` (frequência 2), dando `5 + 2 = 7`.

</details>

2. ▢ Por que a própria definição do algoritmo, "fundir o par mais frequente", não determina por completo qual par é fundido primeiro neste corpus?

<details markdown="1"><summary>Verificação</summary>

Porque três pares, `(e, s)`, `(s, t)` e `(t, </w>)`, estão exatamente empatados na maior contagem ponderada, 9. A regra diz o que fazer quando há um único par mais frequente; ela não diz nada sobre qual escolher entre vários pares empatados, então essa escolha vem do que a implementação fizer num empate, e não do algoritmo como enunciado.

</details>

3. ▢ Um tokenizer treinado com 500 fusões recebe uma palavra que nunca viu durante o treinamento. O que acontece e por que isso difere do que um vocabulário fixo de palavras inteiras faria?

    - a) Ela é substituída por um único símbolo genérico de "palavra desconhecida", o mesmo resultado que um vocabulário de palavras inteiras produziria
    - b) O treinamento falha, já que o tokenizer não tem regra para uma entrada nunca vista
    - c) Ela é soletrada como uma sequência curta de pedaços menores que o tokenizer já aprendeu, em vez de colapsar em um único símbolo de palavra desconhecida
    - d) O tokenizer adiciona automaticamente uma nova regra de fusão para ela na hora

<details markdown="1"><summary>Verificação</summary>

**c)** A palavra nunca vista recai sobre os pedaços menores, até os caracteres individuais se necessário, que as fusões do treinamento já produziram. (a) descreve exatamente o modo de falha que a tokenização em subpalavras foi construída para evitar. (b) e (d) não descrevem como um conjunto fixo e treinado de regras de fusão se comporta em tempo de teste.

</details>

4. ▢ Qual foi a razão específica do campo que Sennrich et al. deram para precisar de uma abordagem de vocabulário aberto?

<details markdown="1"><summary>Verificação</summary>

A tradução é fundamentalmente um problema de vocabulário aberto: nomes, compostos e empréstimos linguísticos significam que nenhuma lista fixa de palavras, por maior que seja, pode cobrir toda palavra que um texto de entrada real vai conter.

</details>

## Prática no mundo real

- [ ] À mão ou em uma planilha, pegue o corpus do exemplo trabalhado e calcule a contagem ponderada de cada par adjacente depois que `(e, s)` foi fundido em `es` (de modo que `newest` vira `n e w es t </w>` e `widest` vira `w i d es t </w>`). Confirme qual(is) par(es) agora empata(m) como o mais frequente.
- [ ] Encontre o arquivo de vocabulário do tokenizer de qualquer modelo aberto a que você tenha acesso (muitos são publicados junto com o modelo). Procure nele uma palavra comum do seu próprio nome ou de um nome que você conhece e veja se ela existe como um único token ou é dividida em pedaços.
- [ ] Amanhã: escolha cinco palavras do seu próprio idioma que você acha que seriam mal atendidas por um vocabulário pequeno de subpalavras (termos técnicos raros, nomes, compostos) e preveja, em uma frase por palavra, como um tokenizer BPE provavelmente dividiria cada uma.

## Para ir além

- [Artigo científico: "Neural Machine Translation of Rare Words with Subword Units", Sennrich et al., 2015](https://arxiv.org/abs/1508.07909)
- [Recursos](../RESOURCES.md)

---

Não ficou claro? Releia a fonte principal no topo, já que esta lição a comprime e é na compressão que o entendimento escapa. Consulte o [glossário](../GLOSSARY.md) para qualquer termo que pareceu escorregadio.

Se o problema é a lição em si, e não o material, isso é um defeito: [abra uma issue](https://github.com/TokenCemetery/teach/issues).
