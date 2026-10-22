---
title: "14. Quantização desde os primeiros princípios"
description: "Escalas por bloco, e por que um único outlier arruína um tensor"
type: lesson
---

# Lição 14. Quantização desde os primeiros princípios

**Ligação com a missão:** O QLoRA é o LoRA mais uma ideia. Esta lição é essa ideia, ensinada à parte para que a próxima seja curta.
**Fonte principal:** [Artigo científico: "LLM.int8(): 8-bit Matrix Multiplication for Transformers at Scale", Dettmers et al., arXiv:2208.07339](https://arxiv.org/abs/2208.07339)
**Pré-requisitos:** [Lição 5](0005-counting-parameters-and-bytes.md), [quantização](../GLOSSARY.md)

## Aquecimento

1. ▢ Bytes por parâmetro em fp32, bf16 e 4 bits?

<details markdown="1"><summary>Verificação</summary>

Quatro, dois e meio, mais as constantes de quantização no caso de 4 bits, que esta lição explica.

</details>

2. ▢ Para um base de 7B com um adapter de 20M, para onde vai a memória de treinamento?

<details markdown="1"><summary>Verificação</summary>

14 GB de pesos congelados do base, ~0.3 GB de estado do adapter e ativações que podem superar os dois. O base congelado é o maior termo fixo, e esta etapa o ataca.

</details>

3. ▢ Por que fazer merge em um base quantizado perde qualidade?

<details markdown="1"><summary>Verificação</summary>

Exige desquantizar, somar a atualização e requantizar. O passo de requantização descarta informação.

</details>

## Saiba isto

A quantização armazena números usando menos bits do que aqueles em que foram treinados. Lembre, pelo [glossário](../GLOSSARY.md), que neste workspace ela sempre se refere ao **base congelado**, e não ao adapter.

### O mecanismo

Para armazenar um tensor de alta precisão em um tipo inteiro pequeno, você precisa de um mapeamento entre a faixa real e a faixa inteira. Dois esquemas:

**Simétrico, absmax.** Pegue o maior valor absoluto e escale de modo que ele caia no máximo inteiro.

```text
s = absmax(x) / 127          # for int8
q = round(x / s)             # store q, an int8
x̂ = q · s                    # recover, approximately
```

**Assimétrico, afim.** Armazene também um deslocamento de ponto zero, para que a faixa não precise estar centrada em zero.

```text
s = (max(x) − min(x)) / 255
z = round(−min(x) / s)
q = round(x / s) + z
```

As distribuições de pesos em transformers são aproximadamente simétricas e centradas perto de zero, então o absmax simétrico é a escolha comum para pesos.

De qualquer forma, o erro é **erro de arredondamento**: cada valor vai para o nível representável mais próximo. Dezesseis níveis para 4 bits, 256 para 8 bits.

### O problema dos outliers

Eis o que faz a quantização ingênua falhar em transformers. Um único valor muito grande em um tensor define o `absmax`, que define a escala, que espalha todos os níveis representáveis para cobrir uma faixa que quase todos os outros valores nunca usam. Os valores típicos então são todos arredondados para um punhado de níveis, e a maior parte da informação do tensor é destruída por um único outlier.

Isso não é hipotético. As ativações de transformers desenvolvem features sistemáticas de grande magnitude, e essa observação é o núcleo do trabalho do LLM.int8(): um pequeno número de dimensões outlier carrega importância desproporcional, e tratá-las de forma ingênua destrói a qualidade em escala.

### Quantização por bloco, a correção

Não quantize um tensor inteiro com uma única escala. Divida-o em pequenos **blocos** contíguos de 64, 128 ou 256 elementos e dê a cada bloco a sua própria escala.

```text
per-tensor:  one absmax  → one outlier ruins everything
per-block:   one absmax per 64 → one outlier ruins 64 values
```

![Duas retas numéricas com os mesmos dezesseis níveis. Na primeira, a escala é definida por um outlier, e cinco valores típicos colapsam em dois níveis perto do centro. Na segunda, um bloco sem outlier define a sua própria escala e os mesmos cinco valores caem em cinco níveis distintos.](images/outlier-sets-the-scale.svg)

As duas linhas têm dezesseis níveis, espaçados de forma idêntica. A única coisa que mudou é quanta faixa numérica esses dezesseis níveis são chamados a cobrir, e isso é definido pelo maior valor do que quer que a escala seja calculada sobre. Gaste a grade em uma faixa que os dados nunca visitam e os dados chegam a um punhado de níveis; gaste-a na faixa que os dados de fato ocupam e cada valor mantém um nível só seu.

O dano fica contido. É por isso que a quantização por bloco é o padrão e a quantização por tensor não é.

Ela tem um custo, e esse custo é o assunto inteiro da próxima lição. Cada bloco precisa ter a sua escala armazenada, e essa escala é um número real:

```text
4-bit weights, block size 64, fp32 scales:
  weights = 0.5 bytes/param
  scales  = 4 bytes per 64 params = 0.0625 bytes/param
  total   = 0.5625 bytes/param, i.e. 4.5 bits, not 4
```

Doze por cento de overhead sobre um orçamento de 4 bits, puramente por contabilidade. Guarde esse número.

### Precisão de armazenamento versus precisão de cálculo

Um peso quantizado não é usado na sua forma quantizada. O forward pass **desquantiza um bloco de volta para bf16, faz o matmul e descarta a cópia desquantizada.**

```text
stored:   4-bit + per-block scale
computed: bf16
```

Então a quantização compra memória e custa computação: um passo de desquantização por bloco, por forward pass. Se o efeito líquido é mais rápido ou mais lento depende inteiramente de você estar limitado por memória ou por computação, e de quão bem o kernel de desquantização está otimizado para o hardware em que você está.

Esse último ponto é onde o hardware de fato entra. A *aritmética* é idêntica em todo lugar. O que difere por backend é se existe um kernel fundido e otimizado para uma dada largura de bits e tamanho de bloco, ou se a biblioteca recorre a um caminho genérico mais lento. A Lição 16 dá o panorama atual.

### Para que serve a quantização, aqui

Dois usos que não devem ser confundidos:

**Quantização para inferência** encolhe um modelo para que ele caiba e sirva barato. Os pesos são quantizados e esse é o artefato que você entrega. Isso está fora do escopo deste workspace como assunto por si só.

**Quantização para treinamento**, que é o que o QLoRA faz, encolhe o *base congelado* para que o treinamento do adapter caiba. O adapter permanece em precisão maior, e o artefato que você entrega pode depois passar por merge em um base de precisão total. A precisão do base é uma decisão de orçamento do momento do treinamento, e não uma propriedade do resultado.

## Prática

1. ▢ Quantize os valores `[0.1, −0.3, 0.2, 8.0]` para int8 com absmax simétrico. O que acontece com os três primeiros?

<details markdown="1"><summary>Verificação</summary>

`absmax = 8.0`, então `s = 8.0/127 ≈ 0.063`. Os valores são mapeados para `round(0.1/0.063) = 2`, `round(−0.3/0.063) = −5`, `round(0.2/0.063) = 3` e `127`.

Recuperados: 0.126, −0.315, 0.189, 8.0. Os valores pequenos agora carregam um erro relativo substancial, porque um único outlier consumiu a faixa. Em 4 bits, com dezesseis níveis, os três primeiros colapsariam em valores quase iguais.

</details>

2. ▢ Por que a quantização por bloco ajuda, e o que ela custa?

<details markdown="1"><summary>Verificação</summary>

Um outlier só define a escala do seu próprio bloco, então prejudica 64 valores em vez do tensor inteiro.

O custo é armazenar uma escala por bloco. Com bloco de 64 e escalas em fp32, são 0.0625 bytes por parâmetro, cerca de 12% de overhead sobre um orçamento de 4 bits.

</details>

3. ▢ Total de bytes por parâmetro para pesos de 4 bits, bloco de 128, escalas em fp32?

<details markdown="1"><summary>Verificação</summary>

0.5 + 4/128 = 0.5 + 0.03125 = 0.53125 bytes, ou 4.25 bits.

Blocos maiores significam menos overhead de escalas e pior contenção de outliers. Essa é a troca que o tamanho do bloco define.

</details>

4. ▢ Em um forward pass quantizado, em qual precisão o matmul é feito?

<details markdown="1"><summary>Verificação</summary>

Em uma mais alta, tipicamente bf16. Cada bloco é desquantizado para bf16, multiplicado, e a cópia desquantizada é descartada.

A quantização é uma decisão de *armazenamento*. A precisão de cálculo é separada e é configurada separadamente.

</details>

5. ▢ Por que a quantização de transformers é mais difícil do que parece só pela aritmética?

<details markdown="1"><summary>Verificação</summary>

Por causa das features outlier sistemáticas. Algumas dimensões carregam magnitudes muito grandes e importância desproporcional, então um esquema que trata todos os valores como intercambiáveis, com uma escala por tensor, destrói os valores comuns enquanto preserva os outliers.

A quantização por bloco, e no caso do LLM.int8() a separação das dimensões outlier em precisão mais alta por completo, é a resposta.

</details>

6. ▢ Distinga a quantização para inferência da quantização para treinamento.

<details markdown="1"><summary>Verificação</summary>

Para inferência, os pesos quantizados *são* o artefato: você os entrega, e o custo em qualidade é permanente.

Para treinamento, quantizar o base congelado é uma decisão de orçamento de memória. O adapter permanece em alta precisão, e o resultado entregue pode passar por merge em um base de precisão total, então o custo da quantização não precisa sobreviver no artefato.

</details>

## Prática no mundo real

- [ ] Implemente à mão, em poucas linhas, a quantização e a desquantização absmax em int8 de um tensor. Meça o erro máximo e o erro médio.
- [ ] Insira um único outlier grande e meça o erro de novo. Depois refaça por bloco, com bloco de 64, e compare.
- [ ] Amanhã: calcule os bytes por parâmetro reais para 4 bits com blocos de 32, 64, 128 e 256, e anote onde o overhead se torna desprezível.

## Para ir além

- [Artigo científico: "LLM.int8(): 8-bit Matrix Multiplication for Transformers at Scale", Dettmers et al., arXiv:2208.07339](https://arxiv.org/abs/2208.07339)
- [Artigo científico: "8-bit Optimizers via Block-wise Quantization", Dettmers et al., arXiv:2110.02861](https://arxiv.org/abs/2110.02861)
- [Lição 15. NF4 e dupla quantização](0015-nf4-and-double-quantisation.md)

---

Não ficou claro? Releia a fonte principal no topo, já que esta lição a comprime e é na compressão que o entendimento escapa. Consulte o [glossário](../GLOSSARY.md) para qualquer termo que pareceu escorregadio.

Se o problema é a lição em si, e não o material, isso é um defeito: [abra uma issue](https://github.com/TokenCemetery/teach/issues).
