---
title: "15. O que muda fora da GPU"
description: "Colocar o servidor do llama.cpp no ar, e como batching, gerenciamento de cache e quantização ficam diferentes em escala de CPU/edge"
type: lesson
---

# Lição 15. O que muda fora da GPU

**Ligação com a missão:** Este é o capstone da etapa 5 e a segunda metade dos critérios de sucesso da missão: uma stack llama.cpp rodando em CPU e respondendo a requisições reais, com todo conceito das etapas 1 a 4 reexaminado para ver o que de fato ainda se aplica nessa escala.
**Fonte principal:** [Repositório: llama.cpp, ggml-org](https://github.com/ggml-org/llama.cpp)
**Pré-requisitos:** [Lição 14](0014-llamacpp-architecture.md), [KV cache](../GLOSSARY.md)

## Aquecimento

1. ▢ O que `--threads` controla no llama.cpp, e como isso difere do `--max-num-seqs` do vLLM?

<details markdown="1"><summary>Verificação</summary>

`--threads` divide as multiplicações de matrizes de uma única sequência entre os cores físicos da CPU. `--max-num-seqs`, em vez disso, limita quantas sequências concorrentes dividem um passo de batch da GPU, amortizando entre elas o tráfego de memória. Uma acelera o compute de uma única sequência; a outra espalha o custo de largura de banda de memória por muitas.

</details>

2. ▢ Decodifique o nome de quantização `Q4_K_M` em suas três partes.

<details markdown="1"><summary>Verificação</summary>

`Q4`: aproximadamente 4 bits por peso. `K`: um tipo k-quant, uma única largura de bits para todos os pesos de um tensor, com escalas por sub-bloco dentro de superblocos de 256. `M`: a receita medium, que mistura tipos k-quant entre tensores.

</details>

## Saiba isto

### Colocando o servidor no ar

O servidor próprio do llama.cpp, o `llama-server`, carrega um arquivo GGUF e expõe um endpoint HTTP compatível com a OpenAI, o mesmo formato de requisição que a lição 10 usou contra o vLLM:

```text
llama-server -m model.Q4_K_M.gguf --threads 8
```

```bash
curl http://localhost:8080/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{"model": "model.Q4_K_M.gguf", "messages": [{"role": "user", "content": "Say hello"}]}'
```

O formato da requisição e da resposta é familiar. O que muda é tudo o que está por baixo.

![Uma comparação em três linhas. Batching: em uma GPU, o continuous batching amortiza a largura de banda de memória entre centenas de requisições concorrentes; em escala de CPU/edge, com apenas de um dígito a algumas dezenas de requisições concorrentes, threads dividindo o compute de uma sequência entre cores o substituem. Gerenciamento de cache: em uma GPU, o PagedAttention gerencia um pool compartilhado grande e em constante mudança; em escala de CPU/edge, um cache contíguo simples por sequência é adequado. Momento da quantização: em uma GPU com vLLM, o esquema é uma flag de tempo de serving escolhida no lançamento; no llama.cpp, a decisão já estava travada quando um nível específico de quantização GGUF foi escolhido, antes de o servidor sequer iniciar.](images/gpu-vs-cpu-edge-mechanisms.svg)

### O batching importa menos nessa escala

O continuous batching do vLLM (lições 4 e 5) existe para amortizar o custo de largura de banda de memória de uma GPU entre as requisições de centenas de estranhos concorrentes. Uma CPU não tem equivalente a milhares de cores paralelos entre os quais espalhar esse custo; o servidor do llama.cpp suporta, sim, um punhado de slots de requisição em paralelo, mas em uma escala de um dígito a algumas dezenas, e não centenas. Isso não é uma funcionalidade ausente: a carga de trabalho típica de um deployment em edge, um dispositivo servindo o seu próprio usuário, raramente tem centenas de requisições concorrentes para agrupar em primeiro lugar. O batching pesado resolve um problema que o serving em CPU/edge geralmente não tem.

### O cache também não precisa de paginação nessa escala

O PagedAttention (lição 11) existe para permitir que muitas sequências compartilhem memória com eficiência e para evitar fragmentação em um pool grande e em constante mudança de requisições concorrentes. Em escala de CPU/edge, com poucas sequências concorrentes e nenhum pool compartilhado grande para fragmentar, uma alocação de cache contígua e mais simples por sequência é comum e adequada. O problema que o PagedAttention resolve não desaparece em princípio, só raramente chega à escala em que a sua complexidade se paga.

### A decisão de quantização já aconteceu

No vLLM, `--quantization` é uma flag de tempo de serving: o esquema é escolhido quando o servidor inicia, a partir de um checkpoint já quantizado ou de um a quantizar no carregamento. No llama.cpp, essa decisão foi tomada antes, quando um arquivo GGUF foi escolhido (ou produzido) em um nível específico de quantização, como `Q4_K_M`. Não existe flag de tempo de serving para mudá-la; mudar a quantização significa baixar ou produzir outro arquivo GGUF. O trade-off das lições 7 a 9, memória contra acurácia contra velocidade, ainda se aplica, só que é resolvido antes de o servidor sequer iniciar, e não configurado na inicialização.

## Prática

1. ▢ Três requisições chegam ao mesmo tempo a uma instância do `llama-server`, todas dos próprios usuários de um único dispositivo edge. Preveja, antes de conferir: o que acontece com o throughput de cada requisição, e por que isso difere do que o continuous batching faz em uma GPU?

<details markdown="1"><summary>Verificação</summary>

O throughput de cada requisição cai aproximadamente em proporção a quantas threads ela agora precisa dividir, já que a contagem fixa de cores da CPU é repartida entre as requisições concorrentes, em vez de cada uma ficar com a contagem de threads inteira para si. Isso difere do continuous batching em GPU, que amortiza um custo de largura de banda de memória já necessário entre sequências concorrentes a pouco custo extra por sequência; dividir o compute da CPU entre requisições não tem um custo equivalente de "já estou pagando por isso de qualquer jeito" a amortizar.

</details>

2. ▢ Por que o continuous batching pesado, no estilo do vLLM, importa menos para um deployment típico de CPU/edge do que para um servidor de GPU?

<details markdown="1"><summary>Verificação</summary>

O continuous batching justifica a sua complexidade quando as requisições de muitos estranhos concorrentes dividem o custo de largura de banda de memória de uma GPU. Um deployment típico em edge, um dispositivo servindo o seu próprio usuário, raramente tem tantas requisições concorrentes para agrupar em primeiro lugar, então o problema que o mecanismo resolve geralmente não está presente nessa escala.

</details>

3. ▢ Onde a decisão de quantização foi tomada em um deployment com llama.cpp, em comparação com onde ela é tomada em um deployment com vLLM?

<details markdown="1"><summary>Verificação</summary>

No llama.cpp, ela foi tomada quando um arquivo GGUF específico (em um nível específico de quantização, como `Q4_K_M`) foi escolhido ou produzido, antes de o servidor sequer iniciar; mudá-la significa usar outro arquivo. No vLLM, é uma flag de tempo de serving, `--quantization`, escolhida quando o servidor é lançado. O trade-off em si é o mesmo que as lições 7 a 9 ensinaram; só muda o momento em que a decisão fica travada.

</details>

4. ▢ Qual afirmação é verdadeira sobre por que o gerenciamento de memória no estilo PagedAttention é menos necessário em escala de CPU/edge?

    - a) O hardware de CPU torna a paginação tecnicamente impossível
    - b) A carga de trabalho típica tem tão poucas sequências concorrentes que um cache contíguo e mais simples por sequência é adequado
    - c) O formato GGUF do llama.cpp é incompatível com qualquer forma de memória paginada
    - d) KV caches não existem de jeito nenhum no serving em CPU

<details markdown="1"><summary>Verificação</summary>

**b)** Com poucas sequências concorrentes e nenhum pool compartilhado grande para fragmentar, um esquema de alocação mais simples costuma bastar; o problema que o PagedAttention resolve raramente chega à escala em que a sua complexidade se paga. (a) é falsa: nada no hardware de CPU descarta a paginação, é um trade-off de design, e não uma limitação. (c) é falsa: o GGUF descreve o arquivo do modelo, e não o layout de cache do runtime. (d) é falsa: o decode ainda precisa de um KV cache na CPU, pelo mesmo motivo que a lição 1 estabeleceu; ele só costuma ser gerenciado de forma mais simples.

</details>

## Prática no mundo real

- [ ] Compile ou instale o llama.cpp, baixe um modelo GGUF pequeno e rode o `llama-server` com uma contagem de threads compatível com a contagem de cores da sua CPU.
- [ ] Envie a requisição curl desta lição contra o seu servidor em execução e confirme que você recebe uma completion de verdade.
- [ ] Amanhã: envie duas ou três requisições ao mesmo tempo para o seu servidor em execução e observe, informalmente, se cada uma parece mais lenta do que quando é a única requisição em andamento.

## Para ir além

- [Repositório: llama.cpp, ggml-org](https://github.com/ggml-org/llama.cpp)
- [Documentação: vLLM Documentation, vLLM Project](https://docs.vllm.ai/en/latest/)
- [Recursos](../RESOURCES.md)

---

Não ficou claro? Releia a fonte principal no topo, já que esta lição a comprime e é na compressão que o entendimento escapa. Consulte o [glossário](../GLOSSARY.md) para qualquer termo que pareceu escorregadio.

Se o problema é a lição em si, e não o material, isso é um defeito: [abra uma issue](https://github.com/TokenCemetery/teach/issues).
