---
title: "5. Scheduling de requisições"
description: "Como um scheduler de continuous batching escolhe a próxima requisição, e por que um prefill grande pode travar todas as outras"
type: lesson
---

# Lição 5. Scheduling de requisições

**Ligação com a missão:** O continuous batching, da lição 4, só ajuda se o scheduler que admite requisições nele não criar por conta própria um novo problema de latência; é nesta lição que esse trade-off mora.
**Fonte principal:** [Documentação: vLLM Documentation, vLLM Project](https://docs.vllm.ai/en/latest/)
**Pré-requisitos:** [Lição 4](0004-static-vs-continuous-batching.md), [KV cache](../GLOSSARY.md)

## Aquecimento

1. ▢ No continuous batching, o que acontece no instante em que uma sequência do batch termina de gerar?

<details markdown="1"><summary>Verificação</summary>

O seu slot é liberado imediatamente, e uma nova requisição que estava esperando é admitida nele no passo seguinte, em vez de o slot ficar ocioso até que um grupo fixo de requisições termine todo junto.

</details>

2. ▢ Por que o prefill é limitado por compute enquanto o decode é limitado pela largura de banda de memória?

<details markdown="1"><summary>Verificação</summary>

O prefill processa um prompt inteiro em uma única passada forward grande e paralela, então há trabalho suficiente por byte lido para manter o compute da GPU ocupado. O decode calcula apenas um novo token por passo, então o tráfego de memória de cada passo (ler o cache e os pesos) domina a pequena quantidade de compute novo.

</details>

## Saiba isto

### Qual requisição em espera vai a seguir

Um scheduler que mantém uma fila de requisições em espera precisa de uma política para decidir qual delas admitir em um slot que acabou de ser liberado. O padrão simples, e o que o vLLM usa na ausência de outra configuração, é o **first-come, first-served (FCFS)**: as requisições são admitidas na ordem de chegada. Não é a única política possível (um scheduler poderia priorizar pelo comprimento esperado, ou por um orçamento de latência declarado), mas o FCFS é o padrão certo para conhecer primeiro: é simples, é justo no sentido de que nenhuma requisição espera atrás de uma que chegou depois, e toda política mais elaborada é uma variação do mesmo mecanismo de admitir em um slot liberado que a lição 4 descreveu.

### Um passo de batch é atômico, e isso cria um novo problema

Toda sequência que compartilha um passo de batch avança junto: a latência do passo inteiro é definida pelo trabalho mais caro que houver nele. Admitir uma nova requisição significa que o trabalho de prefill dela precisa acontecer em algum lugar, e o lugar direto é o passo de batch seguinte, junto com os passos de decode de que as sequências já em execução precisam.

Isso é bom quando o prompt da nova requisição é curto. Não é bom quando ele é longo: um prefill de 6.000 tokens incorporado a um passo passa a dominar a latência desse passo, e todas as outras sequências do batch, sequências que só precisavam de um passo de decode pequeno e rápido, esperam que ele termine antes de qualquer uma delas receber o seu próximo token. Uma admissão grande trava o progresso de todas as outras. Esse é um problema de **head-of-line blocking**: a fila está bem, mas o que está rodando agora não está.

### O chunked prefill limita o estrago

O **chunked prefill** divide o prefill de um prompt grande em pedaços menores e intercala cada pedaço com os passos de decode em andamento do batch, em vez de rodar o prefill inteiro em um passo. Cada passo de batch agora admite apenas uma quantidade limitada de novo trabalho de prefill, aquilo que couber no orçamento de latência do passo, em vez de tudo o que o prompt de uma requisição recém-admitida contiver. A troca é que o prefill da própria nova requisição agora leva vários passos para terminar em vez de um, mas nenhuma outra sequência do batch fica travada esperando por ele.

![Em cima: sem chunking, o prefill inteiro de um prompt grande é incorporado a um passo, inflando a sua latência muito além dos passos de decode constantes de 20 ms enquanto todas as outras sequências esperam. Embaixo: o chunked prefill divide o prefill do mesmo prompt em pedaços pequenos intercalados com o decode, mantendo todo passo perto de 20 ms ao custo de o prefill da nova requisição levar mais passos para terminar.](images/chunked-prefill.svg)

## Prática

1. ▢ Um batch contínuo está rodando passos constantes só de decode, de cerca de 20 ms cada. Um prompt de 6.000 tokens é admitido e o seu prefill completo é incorporado ao passo seguinte, sem chunking. O que acontece com a latência desse passo, e quem sente o efeito?

<details markdown="1"><summary>Verificação</summary>

Esse passo agora precisa completar o compute de prefill dos 6.000 tokens do prompt, além do trabalho de decode de todas as outras sequências do batch, porque o batch inteiro avança junto em um só passo. A latência do passo infla bem além de 20 ms, e todas as outras sequências do batch, inclusive as que só precisavam de um passo de decode rápido, esperam esse único passo terminar antes de receber o seu próximo token.

</details>

2. ▢ Como o chunked prefill evita a trava descrita na questão 1?

<details markdown="1"><summary>Dica</summary>

Pense no que muda por passo, e não no que muda na quantidade total de trabalho de prefill necessária.

</details>

<details markdown="1"><summary>Verificação</summary>

Em vez de rodar o prompt inteiro da nova requisição em um passo, o scheduler divide o prefill dela em pedaços menores e intercala cada pedaço com os passos de decode regulares do batch, admitindo apenas uma quantidade limitada de novo trabalho de prefill por passo. A latência de qualquer passo isolado permanece limitada; o prefill da nova requisição apenas leva mais passos no total para terminar.

</details>

3. ▢ Qual afirmação é verdadeira sobre o chunked prefill?

    - a) Ele remove o prefill por completo, tratando todo token como um passo de decode
    - b) Ele limita a latência adicionada a um passo ao dividir um prefill grande em pedaços
    - c) É uma técnica específica de stacks de serving em CPU como o llama.cpp
    - d) Ele reduz o quanto de KV cache um prompt longo precisa depois de totalmente processado

<details markdown="1"><summary>Verificação</summary>

**b)** Ele limita a latência adicionada a um passo ao dividir um prefill grande em pedaços intercalados com o decode. (a) é falsa: o prompt ainda precisa do processamento de prefill completo, só espalhado por mais passos. (c) é falsa: é uma técnica de scheduling de continuous batching em GPU. (d) é falsa: o tamanho final do cache de um prompt totalmente processado não muda; o chunking só muda como o trabalho para chegar lá se espalha no tempo.

</details>

4. ▢ A admissão FCFS sozinha (sem chunking) teria evitado a trava da questão 1?

<details markdown="1"><summary>Verificação</summary>

Não. O FCFS só decide qual requisição em espera é admitida em seguida; ele não diz nada sobre quanto do trabalho de prefill dessa requisição cai em um único passo depois de admitida. A trava vem de incorporar um prefill grande inteiro a um passo de batch atômico, e o que a corrige é o chunking, e não a ordem de admissão.

</details>

## Prática no mundo real

- [ ] Encontre a flag ou a opção de configuração da sua stack de serving para o chunked prefill (vLLM: habilitado por padrão nas versões recentes; veja na documentação o ajuste do tamanho do chunk) e leia qual é o tamanho de chunk padrão.
- [ ] Estime, para uma carga de trabalho de que você tenha dados de comprimento de requisição, com que frequência aproximada um prompt seria longo o bastante para travar visivelmente um passo de batch sem chunking.
- [ ] Amanhã: leia um parágrafo sobre como um scheduler decide entre admitir o pedaço de prefill de uma nova requisição e continuar um já em andamento, quando os dois competem pelo orçamento do mesmo passo.

## Para ir além

- [Documentação: vLLM Documentation, vLLM Project](https://docs.vllm.ai/en/latest/)
- [Artigo: "How continuous batching enables 23x throughput in LLM inference while reducing p50 latency", Anyscale](https://www.anyscale.com/blog/continuous-batching-llm-inference)
- [Recursos](../RESOURCES.md)

---

Não ficou claro? Releia a fonte principal no topo, já que esta lição a comprime e é na compressão que o entendimento escapa. Consulte o [glossário](../GLOSSARY.md) para qualquer termo que pareceu escorregadio.

Se o problema é a lição em si, e não o material, isso é um defeito: [abra uma issue](https://github.com/TokenCemetery/teach/issues).
