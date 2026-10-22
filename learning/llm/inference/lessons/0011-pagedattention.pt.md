---
title: "11. PagedAttention"
description: "O mecanismo de block table por trás do vLLM, o seu trade-off de tamanho de bloco e como ele permite que sequências compartilhem o cache de um prefixo comum"
type: lesson
---

# Lição 11. PagedAttention

**Ligação com a missão:** O gerenciador de memória do vLLM é o mecanismo que transforma o teto de capacidade da lição 2 em um alvo móvel e compartilhável, em vez de um custo fixo por sequência, e é nesta lição que esse mecanismo recebe o seu nome completo.
**Fonte principal:** [Artigo científico: "Efficient Memory Management for Large Language Model Serving with PagedAttention", Kwon et al., SOSP 2023](https://arxiv.org/abs/2309.06180)
**Pré-requisitos:** [Lição 10](0010-standing-up-vllm.md), [KV cache](../GLOSSARY.md)

## Aquecimento

1. ▢ De que dois tipos de fragmentação sofria uma alocação de KV cache ingênua, contígua e dimensionada para o comprimento máximo (lição 1)?

<details markdown="1"><summary>Verificação</summary>

Fragmentação interna: uma sequência que termina curta continua segurando memória reservada para o comprimento máximo que nunca usou. Fragmentação externa: lacunas entre blocos reservados de tamanhos diferentes, onde o cache de nenhuma outra sequência cabe.

</details>

2. ▢ Em uma frase, o que a lição 1 disse que o PagedAttention toma emprestado da memória virtual dos sistemas operacionais?

<details markdown="1"><summary>Verificação</summary>

Dividir o cache em blocos de tamanho fixo, armazenados de forma não contígua, endereçados por uma tabela por sequência que mapeia posições lógicas para blocos físicos, a mesma ideia das page tables do SO.

</details>

## Saiba isto

### A block table, um nível de detalhe mais fundo

O KV cache de cada sequência é dividido em **blocos** de tamanho fixo, cada um guardando as keys e values de um número definido de tokens. A **block table** de uma sequência mapeia as suas posições lógicas de token para localizações físicas de bloco na memória, onde quer que estejam. A atenção de uma dada sequência busca os seus blocos por essa tabela, em vez de presumir que são contíguos, e é isso que permite ao gerenciador de memória subjacente colocar blocos em qualquer lugar onde haja espaço, exatamente como uma page table de SO permite que as páginas de memória de um processo fiquem em qualquer lugar da RAM física.

### O tamanho do bloco é um trade-off, e não um parâmetro livre

Um tamanho de bloco maior significa menos blocos por sequência e menos contabilidade da block table, mas mais espaço desperdiçado no último bloco, parcialmente preenchido, de uma sequência cujo comprimento não divide por igual (fragmentação interna, só que em uma escala muito menor do que a versão ingênua da lição 1, de sequência inteira). Um tamanho de bloco menor desperdiça menos espaço por sequência, mas significa mais blocos, e mais entradas de block table, para acompanhar. O tamanho de bloco padrão do vLLM (16 tokens) é um meio-termo escolhido entre esses dois custos, e não um número arbitrário.

### Compartilhando blocos entre sequências

Como os blocos de uma sequência são alcançados indiretamente, pela sua block table, em vez de presumir um layout físico fixo, as block tables de duas sequências diferentes podem apontar para o *mesmo* bloco físico quando o seu conteúdo é idêntico, mais comumente um prefixo de prompt compartilhado. A amostragem paralela (pedir várias completions do mesmo prompt) ou o beam search são os casos mais claros: todas as amostras compartilham o cache idêntico dos tokens do prompt, então os blocos do prompt precisam existir fisicamente uma só vez, com a block table de cada amostra apontando para eles. Quando a geração de uma amostra diverge das demais (qualquer token novo, específico da amostra), um **copy-on-write** cria a cópia privada dessa amostra do bloco que está sendo modificado, exatamente o mecanismo que um sistema operacional usa quando dois processos compartilham páginas de memória até que um deles escreva.

![Duas block tables, a sequência A à esquerda e a sequência B à direita, cada uma mapeando quatro posições lógicas para números de bloco físico. Nas posições 0 a 2, as duas tabelas apontam para os mesmos três blocos físicos compartilhados, que guardam um prefixo de prompt idêntico, então o cache desse prefixo existe uma só vez na memória. Na posição 3, as duas sequências geraram tokens diferentes, então um copy-on-write deu a cada uma o seu próprio bloco privado: o bloco 9 da sequência A e o bloco 3 da sequência B, nenhum compartilhado com o outro.](images/block-table-sharing.svg)

## Prática

1. ▢ Com um tamanho de bloco de 16 tokens, uma sequência gera 40 tokens de saída. Quantos blocos ela usa, e quanto espaço é desperdiçado no último?

<details markdown="1"><summary>Dica</summary>

Divida 40 por 16 e arredonde para cima até um número inteiro de blocos; o desperdício é o que sobra sem uso no último bloco, parcialmente preenchido.

</details>

<details markdown="1"><summary>Verificação</summary>

`40 / 16 = 2,5`, arredondado para cima para 3 blocos. Os dois primeiros guardam 32 tokens; o terceiro guarda os 8 restantes, desperdiçando os outros 8 espaços desse bloco, fragmentação interna na escala de um bloco em vez de uma sequência inteira.

</details>

2. ▢ Por que um tamanho de bloco menor reduz esse espaço desperdiçado, e o que ele custa em troca?

<details markdown="1"><summary>Verificação</summary>

Um tamanho de bloco menor significa que o último bloco, parcialmente preenchido, tem menos espaços sem uso para desperdiçar, já que há menos posições em cada bloco para começar. O custo é mais blocos por sequência no total e, portanto, mais entradas de block table que o gerenciador de memória precisa acompanhar e consultar.

</details>

3. ▢ Dez amostras paralelas são pedidas para o mesmo prompt de 200 tokens, com um tamanho de bloco de 16 tokens. De quantos blocos físicos o cache do prompt precisa, com compartilhamento de blocos e sem ele?

<details markdown="1"><summary>Dica</summary>

Calcule de quantos blocos uma cópia do prompt de 200 tokens precisa e depois decida quantas cópias existem em cada caso.

</details>

<details markdown="1"><summary>Verificação</summary>

`200 / 16 = 12,5`, arredondado para cima para 13 blocos para uma cópia do prompt. Sem compartilhamento, cada uma das 10 amostras guarda a sua própria cópia: `13 × 10 = 130` blocos. Com compartilhamento, a block table de cada amostra aponta para os mesmos 13 blocos físicos do prompt compartilhado, então só 13 blocos são necessários até que alguma amostra comece a gerar os seus próprios tokens divergentes.

</details>

4. ▢ Uma das dez amostras da questão 3 gera um token diferente do que qualquer outra amostra gerou naquela posição. O que acontece com o cache dessa amostra nesse ponto?

<details markdown="1"><summary>Verificação</summary>

Um copy-on-write é acionado: essa amostra recebe a sua própria cópia privada do bloco em que está escrevendo, em vez de modificar o bloco compartilhado para o qual a tabela de todas as outras amostras ainda aponta. Só a amostra divergente paga por um novo bloco; as outras nove continuam compartilhando o original.

</details>

5. ▢ Qual afirmação é verdadeira sobre a escolha de tamanho de bloco do vLLM?

    - a) Blocos maiores sempre desperdiçam mais memória do que menores, sem nenhum benefício compensatório
    - b) O tamanho do bloco troca fragmentação interna por overhead de contabilidade da block table
    - c) O tamanho do bloco só afeta cargas de amostragem paralela, e não o serving de uma única requisição
    - d) Um tamanho de bloco menor sempre aumenta o uso total de memória

<details markdown="1"><summary>Verificação</summary>

**b)** Blocos menores desperdiçam menos espaço em um último bloco parcialmente preenchido, mas exigem acompanhar mais entradas de block table; blocos maiores são o inverso. (a) é falsa: blocos maiores reduzem o overhead de contabilidade, que é um benefício real. (c) é falsa: toda sequência, compartilhada ou não, é dividida em blocos e paga o trade-off de fragmentação e contabilidade. (d) é falsa: blocos menores reduzem a fragmentação interna, o que pode diminuir o uso total de memória, e não aumentá-lo sempre.

</details>

## Prática no mundo real

- [ ] Encontre a flag ou a opção de configuração de tamanho de bloco do vLLM na documentação e leia qual é o valor padrão e o que a documentação diz sobre alterá-lo.
- [ ] Se você consegue rodar um servidor, envie várias requisições de amostragem paralela (`n` maior que 1) para o mesmo prompt e veja se a documentação ou os logs relatam algo sobre compartilhamento de prefixo ou de blocos.
- [ ] Amanhã: leia um parágrafo sobre prefix caching (reaproveitar os blocos de um system prompt compartilhado entre requisições que, fora isso, não têm relação entre si) e anote como é a mesma ideia de compartilhamento de blocos aplicada entre requisições, em vez de dentro de uma.

## Para ir além

- [Artigo científico: "Efficient Memory Management for Large Language Model Serving with PagedAttention", Kwon et al., SOSP 2023](https://arxiv.org/abs/2309.06180)
- [Documentação: vLLM Documentation, vLLM Project](https://docs.vllm.ai/en/latest/)
- [Recursos](../RESOURCES.md)

---

Não ficou claro? Releia a fonte principal no topo, já que esta lição a comprime e é na compressão que o entendimento escapa. Consulte o [glossário](../GLOSSARY.md) para qualquer termo que pareceu escorregadio.

Se o problema é a lição em si, e não o material, isso é um defeito: [abra uma issue](https://github.com/TokenCemetery/teach/issues).
