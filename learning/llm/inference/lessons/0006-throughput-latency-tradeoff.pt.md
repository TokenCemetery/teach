---
title: "6. O trade-off entre throughput e latência"
description: "Como o batch size troca throughput por latência por token, e como defender uma configuração de batching contra um orçamento de latência declarado"
type: lesson
---

# Lição 6. O trade-off entre throughput e latência

**Ligação com a missão:** Este é o capstone da etapa 2: defender uma configuração de batching para uma carga de trabalho declarada significa pôr um número no trade-off entre throughput e latência que as lições 4 e 5 descreveram, contra um orçamento de latência e o teto de capacidade que a lição 2 calculou.
**Fonte principal:** [Documentação: vLLM Documentation, vLLM Project](https://docs.vllm.ai/en/latest/)
**Pré-requisitos:** [Lição 5](0005-request-scheduling.md), [Lição 2](0002-capacity-and-batch-size.md), [KV cache](../GLOSSARY.md)

## Aquecimento

1. ▢ Por que agrupar os passos de decode de mais sequências aumenta o throughput sem um aumento proporcional no tráfego de memória?

<details markdown="1"><summary>Verificação</summary>

O tráfego de memória de um passo de decode, que lê os pesos e os KV caches residentes, quase não muda se ele calcula o próximo token de uma sequência ou de várias. O batching espalha esse mesmo tráfego por mais compute útil.

</details>

2. ▢ O que é o teto de capacidade da lição 2, em uma frase?

<details markdown="1"><summary>Verificação</summary>

`(total memory − weights − overhead) / (bytes per token × context length)`: o número máximo de sequências concorrentes que o orçamento de KV cache permite, independentemente de qualquer coisa sobre latência.

</details>

## Saiba isto

### Batches maiores fazem duas coisas ao mesmo tempo, e elas puxam em direções opostas

Acrescentar mais uma sequência a um batch aumenta o throughput: mais tokens são produzidos por segundo, agregados entre todas as sequências do passo. Mas toda sequência de um passo de batch avança junto (lição 5), então empilhar o trabalho de decode de mais sequências em um passo também faz esse próprio passo demorar mais. O atraso entre os tokens sucessivos de uma única sequência, a sua latência entre tokens, cresce com o batch com o qual ela divide um passo. Throughput e latência por token se movem juntos, e não contra um ao outro de forma independente: empurrar um para cima empurra o outro para cima também.

### A curva tem dois regimes

Em batch sizes pequenos, o decode é limitado pela largura de banda de memória (lição 4): as mesmas leituras de pesos e de cache já dominam o custo do passo, então acrescentar outra sequência é quase de graça. O throughput sobe de forma aproximadamente linear com o batch size, enquanto a latência do passo mal se move. A partir de certo batch size, há trabalho empilhado suficiente para que o compute bruto da GPU, e não a sua largura de banda de memória, vire o gargalo: a latência do passo começa a subir visivelmente a cada sequência acrescentada, e cada sequência a mais compra menos throughput adicional do que a anterior. Essa inflexão é a mesma distinção entre limitado pela largura de banda de memória e limitado por compute que a lição 3 traçou entre o prefill e o decode, agora acontecendo dentro do próprio decode conforme o batch cresce.

![Latência por token contra batch size: 15 ms com 8, 25 ms com 32, 45 ms com 64, 90 ms com 128. A curva fica plana enquanto o decode é limitado pela largura de banda de memória e depois sobe de forma íngreme quando o compute vira o gargalo. Um orçamento de latência de 30 ms, marcado por uma linha tracejada, é cruzado entre os batch sizes 32 e 64.](images/throughput-latency-tradeoff.svg)

### Defender uma configuração significa escolher um ponto nessa curva, e não o maior número disponível

Uma carga de trabalho declarada traz duas restrições independentes, e a configuração que vale defender é o maior batch size que satisfaz as duas:

- **Um orçamento de latência**: um teto declarado para a latência entre tokens (por exemplo, nenhum token de saída deve levar mais do que certo número de milissegundos para chegar).
- **O teto de capacidade**: o máximo derivado de memória da lição 2, que não diz nada sobre latência e diz tudo sobre se o cache cabe ou não.

Um batch size abaixo das duas restrições deixa na mesa um throughput que o orçamento poderia ter pagado. Um batch size acima do orçamento de latência troca uma violação de latência por um throughput que ninguém pediu. O número defendido é o menor entre o que o orçamento permite e o que a capacidade permite, e o raciocínio para escolhê-lo é a resposta a "por que este número e não outro", que é o que defender uma configuração realmente significa.

## Prática

1. ▢ Uma stack de serving foi medida em quatro batch sizes: 8 (15 ms/token), 32 (25 ms/token), 64 (45 ms/token), 128 (90 ms/token). O orçamento de latência declarado é 30 ms/token. Qual desses batch sizes é o maior que satisfaz o orçamento?

<details markdown="1"><summary>Verificação</summary>

32, com 25 ms/token. 64 e 128 excedem o orçamento de 30 ms; 32 é o maior dos quatro que fica abaixo dele.

</details>

2. ▢ Continuando a questão 1: o teto de capacidade de KV cache para essa carga de trabalho, calculado como a lição 2 o faz, dá 100 sequências concorrentes. Que batch size deve realmente ser defendido, e qual restrição está limitando?

<details markdown="1"><summary>Dica</summary>

O número defendido é o menor entre o que cada restrição permite sozinha.

</details>

<details markdown="1"><summary>Verificação</summary>

Um batch size de 32. O orçamento de latência é quem limita aqui, já que 32 está muito abaixo do teto de capacidade de 100 sequências; o cache ainda tem bastante espaço, mas o orçamento de latência não.

</details>

3. ▢ Suponha que, em vez disso, o teto de capacidade tivesse dado 20 sequências, com todo o resto da questão 1 inalterado. Que batch size deve ser defendido agora, e por quê?

<details markdown="1"><summary>Verificação</summary>

Um batch size de 20. Agora o teto de capacidade limita no lugar do orçamento de latência: 32 satisfaria o orçamento de 30 ms/token, mas o cache não consegue guardar tantas sequências concorrentes, então a restrição de memória limita o número abaixo do que a latência sozinha teria permitido.

</details>

4. ▢ Uma equipe escolhe um batch size de 8 para a carga de trabalho da questão 1, bem abaixo tanto da escolha de 32, guiada pelo orçamento de latência, quanto do teto de capacidade de 100 sequências. Qual é o custo dessa escolha?

<details markdown="1"><summary>Verificação</summary>

Throughput deixado na mesa. Com 8, a latência do passo (15 ms/token) fica bem abaixo do orçamento de 30 ms, o que significa que o orçamento comportaria um batch maior, e o cache tem muito mais espaço do que 8 sequências usam. Nada está sendo violado, mas o servidor atende menos requisições concorrentes do que poderia defender.

</details>

## Prática no mundo real

- [ ] Encontre a flag da sua stack de serving para o batch size máximo (vLLM: `--max-num-seqs`) e leia o que a documentação diz sobre ajustá-lo contra uma meta de latência.
- [ ] Se você tiver acesso a um servidor em execução ou aos benchmarks dele, faça o gráfico (ou encontre) do throughput e da latência por token em alguns batch sizes e localize aproximadamente onde começa o regime limitado por compute.
- [ ] Amanhã: escolha um orçamento de latência que você de fato quereria defender para uma carga de trabalho que lhe interessa e escreva, em uma frase, por que esse número e não um mais estrito ou mais folgado.

## Para ir além

- [Documentação: vLLM Documentation, vLLM Project](https://docs.vllm.ai/en/latest/)
- [Artigo: "How continuous batching enables 23x throughput in LLM inference while reducing p50 latency", Anyscale](https://www.anyscale.com/blog/continuous-batching-llm-inference)
- [Recursos](../RESOURCES.md)

---

Não ficou claro? Releia a fonte principal no topo, já que esta lição a comprime e é na compressão que o entendimento escapa. Consulte o [glossário](../GLOSSARY.md) para qualquer termo que pareceu escorregadio.

Se o problema é a lição em si, e não o material, isso é um defeito: [abra uma issue](https://github.com/TokenCemetery/teach/issues).
