---
title: "16. Metodologia de medição de latência p99"
description: "Por que o p99 vence uma média, por que TTFT e latência entre tokens precisam de números separados e o que torna confiável uma medição de p99"
type: lesson
---

# Lição 16. Metodologia de medição de latência p99

**Ligação com a missão:** A missão deste workspace é defender um orçamento de latência p99, e um número defendido precisa vir de uma medição bem feita; esta lição é o que "bem feita" significa, antes de a lição 17 ligar esse número de volta a todas as escolhas anteriores.
**Fonte principal:** [Documentação: vLLM Documentation, vLLM Project](https://docs.vllm.ai/en/latest/)
**Pré-requisitos:** [Lição 15](0015-what-changes-off-gpu.md), [KV cache](../GLOSSARY.md)

## Aquecimento

1. ▢ Por que o prefill reivindica a maior parte da pegada final de cache de uma requisição em um só passo, enquanto o decode acrescenta o resto aos poucos?

<details markdown="1"><summary>Verificação</summary>

O prefill processa o prompt inteiro em uma única passada forward, calculando e colocando em cache as keys e values de todos os tokens do prompt juntos. O decode gera um token de saída por passo, então o cache cresce apenas um token por passo.

</details>

2. ▢ No continuous batching, o que faz uma requisição grande admitida travar todas as outras sequências que dividem o seu passo de batch?

<details markdown="1"><summary>Verificação</summary>

Um passo de batch é atômico: toda sequência que o compartilha avança junto, então um prefill grande incorporado a um passo atrasa o próximo token de todas as outras sequências até esse passo terminar. Isso é o head-of-line blocking.

</details>

## Saiba isto

### Por que p99, e não a média

O **p99** de uma distribuição de latência é o valor abaixo do qual caem 99% das requisições medidas; só o 1% pior é mais lento. Uma média pode parecer boa e esconder um problema real: o head-of-line blocking da lição 5, por exemplo, só atinge a pequena fração de requisições azaradas o bastante para dividir um passo com um prefill grande, então mal move uma média entre milhares de requisições que de resto são rápidas, enquanto pode tornar esse 1% azarado dramaticamente mais lento. Um orçamento de latência defendido por uma média perderia exatamente o modo de falha que este workspace passou a etapa 2 explicando.

![Um histograma de latência de requisições. A maioria das requisições se agrupa em baixa latência, formando um bloco alto à esquerda que decai rapidamente. Um grupo separado e esparso de requisições fica bem à direita, em latência muito mais alta, a cauda lenta. Uma linha tracejada marcando a média fica dentro do bloco da esquerda, mal deslocada pelas raras requisições do extremo direito, já que são poucas demais para movê-la. Um marcador do p99, em vez disso, fica lá na cauda do extremo direito, já que o p99 é definido pelo pior um por cento, que é precisamente onde estão as requisições raras e lentas.](images/p99-vs-average-latency.svg)

### Qual latência, medida separadamente

"Latência da requisição" não é um número só para um servidor de LLM; no mínimo ela se divide em **time to first token (TTFT)**, dominado pelo prefill, e **latência entre tokens (ITL, inter-token latency)**, às vezes chamada de tempo por token de saída, dominada pelo decode. Os dois se comportam de forma diferente (lição 3) e são moldados por alavancas diferentes (batching e scheduling para o TTFT, batch size e quantização para a ITL), então fundi-los em um único número misturado obscurece para qual alavanca um p99 ruim realmente aponta. Um orçamento que vale defender nomeia o p99 do TTFT e o p99 da ITL (ou o p99 da latência total de ponta a ponta, quando é isso que a carga de trabalho realmente importa) como números separados, e não uma média de duas coisas diferentes.

### O que torna confiável uma medição de p99

Um p99 é uma estimativa de um evento raro, por definição apenas o pior 1% de uma amostra, então precisa de amostras suficientes para significar algo: um p99 calculado a partir de 20 requisições na verdade está reportando sobre uma única requisição (o pior 1º percentil de 20 fica perto do máximo, e não é uma estimativa estável da cauda), enquanto uma estimativa estável tipicamente precisa de amostras na casa das centenas a milhares. A carga que gera essas amostras também precisa se parecer com a carga de trabalho real: concorrência realista (não tão baixa que o comportamento de batching e de scheduling nunca seja de fato exigido) e uma mistura realista de comprimentos de prompt e de saída (o desperdício do batching estático da lição 4 e o head-of-line blocking da lição 5 dependem da variância de comprimento das requisições, que um benchmark com requisições de comprimento uniforme nunca traria à tona). Um p99 medido sob uma carga irreal é um número real sobre uma carga de trabalho que não é a que está sendo servida.

## Prática

1. ▢ A latência média das requisições de um servidor parece boa, mas os usuários relatam de vez em quando requisições que demoram bem mais do que o esperado. O que esse padrão sugere sobre onde o problema apareceria na distribuição de latência, e por que a média pode não tê-lo captado?

<details markdown="1"><summary>Verificação</summary>

Sugere um problema de cauda, algo como o head-of-line blocking da lição 5, que afeta apenas uma pequena fração das requisições. Uma média entre muitas requisições na maioria não afetadas mal se move mesmo quando essa pequena fração fica dramaticamente mais lenta, e é exatamente por isso que um p99 (ou um percentil igualmente alto) é necessário para enxergá-lo.

</details>

2. ▢ Por que TTFT e latência entre tokens devem ser medidos e reportados como números de p99 separados, em vez de fundidos em um único número de "latência média da requisição"?

<details markdown="1"><summary>Verificação</summary>

O TTFT é dominado pelo prefill e moldado por scheduling e chunking; a latência entre tokens é dominada pelo decode e moldada por batch size e quantização. Um único número misturado não consegue dizer para qual dessas alavancas um mau resultado realmente aponta, e melhorar uma pode mover uma média misturada sem revelar se a outra piorou.

</details>

3. ▢ Uma equipe calcula um número de latência p99 a partir de 20 requisições medidas. Esse número é confiável? Por que sim ou por que não?

<details markdown="1"><summary>Dica</summary>

Pense em quantas dessas 20 requisições o percentil 99 está realmente descrevendo.

</details>

<details markdown="1"><summary>Verificação</summary>

Não, não de forma confiável. Com apenas 20 amostras, o percentil 99 está perto de reportar sobre a única requisição mais lenta da amostra, e não uma estimativa estável de uma cauda genuína. Um p99 confiável precisa de uma amostra bem maior, tipicamente centenas a milhares de requisições, para diluir o ruído de quais requisições em particular calharam de cair nesse 1% de cima.

</details>

4. ▢ Um benchmark mede a latência p99 usando requisições que têm todas o mesmo comprimento uniforme de prompt e de saída. Por que isso poderia subestimar o p99 que uma carga de trabalho de produção com comprimentos de requisição variados realmente veria?

<details markdown="1"><summary>Verificação</summary>

As lições 4 e 5 mostraram que a variância no comprimento das requisições é o que cria os modos de falha que prejudicam a latência de cauda: o desperdício do batching estático escala com a dispersão entre os comprimentos das requisições, e o head-of-line blocking é disparado por um prefill incomumente grande chegando entre outros menores. Um benchmark de comprimento uniforme nunca produz essa variância, então nunca exercita as condições de onde a latência de cauda da carga de trabalho real realmente vem.

</details>

5. ▢ Qual afirmação é verdadeira sobre uma medição de latência p99 defensável?

    - a) Uma única execução de benchmark de qualquer tamanho basta, desde que reporte um número de p99
    - b) Ela deve ser medida com concorrência e variância de comprimento de requisição realistas, e reportada separadamente para TTFT e latência entre tokens
    - c) A média e o p99 sempre se movem juntos, então medir um já basta
    - d) O p99 só importa para serving em CPU/edge, e não para serving em GPU

<details markdown="1"><summary>Verificação</summary>

**b)** Tanto o realismo da carga quanto a separação entre TTFT e latência entre tokens são necessários para que o número aponte para algo acionável. (a) é falsa: poucas amostras tornam um p99 instável, como a questão 3 mostrou. (c) é falsa: uma média pode esconder exatamente o comportamento de cauda que um p99 existe para captar. (d) é falsa: a latência de cauda e a sua medição importam para qualquer stack de serving, de GPU ou de CPU.

</details>

## Prática no mundo real

- [ ] Encontre a ferramenta de benchmark da sua stack de serving (o vLLM traz o `benchmark_serving.py`) e leia quais percentis ela reporta por padrão e que distribuição de comprimento de requisição ela usa.
- [ ] Para uma carga de trabalho que você tenha em mente, escreva como seria uma distribuição realista de comprimentos de prompt e de saída, e se um benchmark com comprimentos uniformes deixaria de captar algo sobre ela.
- [ ] Amanhã: se você tiver um servidor em execução, rode um benchmark contra ele com pelo menos algumas centenas de requisições e anote separadamente o p99 do TTFT e o p99 da latência entre tokens reportados.

## Para ir além

- [Documentação: vLLM Documentation, vLLM Project](https://docs.vllm.ai/en/latest/)
- [Artigo: "How continuous batching enables 23x throughput in LLM inference while reducing p50 latency", Anyscale](https://www.anyscale.com/blog/continuous-batching-llm-inference)
- [Recursos](../RESOURCES.md)

---

Não ficou claro? Releia a fonte principal no topo, já que esta lição a comprime e é na compressão que o entendimento escapa. Consulte o [glossário](../GLOSSARY.md) para qualquer termo que pareceu escorregadio.

Se o problema é a lição em si, e não o material, isso é um defeito: [abra uma issue](https://github.com/TokenCemetery/teach/issues).
