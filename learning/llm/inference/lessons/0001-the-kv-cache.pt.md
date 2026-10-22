---
title: "1. O KV cache"
description: "Por que a geração fica cara, e o que o cache devolve"
type: lesson
---

# Lição 1. O KV cache

**Ligação com a missão:** Todo número de latência e throughput que este workspace defende remonta ao que o KV cache custa em memória e a quão bem um servidor gerencia esse custo.
**Fonte principal:** [Documentação: "Optimizing inference", Hugging Face Transformers](https://huggingface.co/docs/transformers/main/en/llm_optims)
**Pré-requisitos:** nenhum

## Saiba isto

### Por que a decodificação precisa de um cache

Um transformer gera um token por vez. Para produzir o token *N*, a self-attention precisa dos vetores de key e value de cada token de 1 a *N*, em cada camada. Sem um cache, cada novo token obriga o modelo a recalcular as keys e values do prefixo *inteiro* outra vez, embora esses vetores nunca mudem depois que um token é gerado. Isso é trabalho quadrático gasto recalculando coisas já calculadas.

O **KV cache** armazena os vetores de key e value de cada token, por camada, no instante em que são calculados pela primeira vez, de modo que gerar o token *N+1* só calcula um novo conjunto de vetores K/V e reaproveita o resto. É isso que torna a geração autorregressiva viável: ela troca recomputação por memória.

### O que essa memória realmente custa

O cache não é gratuito, e o seu tamanho é o que governa quantas requisições um servidor consegue manter na memória ao mesmo tempo. Por token, por camada, ele guarda um vetor de key e um de value, cada um com tamanho igual à dimensão oculta do modelo (`d_model`, a dimensão do residual stream do modelo). Em meia precisão (2 bytes por valor):

```text
bytes per token = 2 (K and V) × num_layers × d_model × 2 bytes
```

Tome o Llama-2-7B como caso concreto: 32 camadas, `d_model` = 4096.

```text
2 × 32 × 4096 × 2 bytes = 524,288 bytes ≈ 512 KB per token
```

Com um contexto de 4096 tokens, isso dá `512 KB × 4096 ≈ 2 GB`, para uma *única* sequência. Mantenha 16 dessas sequências ao mesmo tempo e só o cache precisa de ~32 GB, mais do que os 14 GB que os pesos do próprio modelo ocupam em fp16. Essa é a aritmética por trás de "é só aumentar o KV cache" ser o instinto errado, e de as stacks de serving serem obcecadas por memória de cache em vez de tratá-la como um detalhe (veja o [Transformer Inference Arithmetic](https://kipp.ly/transformer-inference-arithmetic/) de Kipply para a derivação completa, incluindo como isso escala com esquemas de compartilhamento de attention heads como GQA/MQA).

### Onde o cache ingênuo desperdiça memória

Uma implementação ingênua reserva um bloco contíguo de memória por sequência, dimensionado para o comprimento máximo que ela poderia alcançar. Disso decorrem dois modos de falha:

- **Fragmentação interna**: uma sequência que acaba curta continua segurando memória reservada para um comprimento máximo que ela nunca usou.
- **Fragmentação externa**: sequências de comprimentos reais diferentes deixam lacunas entre os seus blocos reservados, onde o cache de nenhuma outra sequência cabe.

O artigo do PagedAttention mediu sistemas ingênuos mantendo apenas de 20 a 40% da memória de KV cache alocada realmente guardando dados úteis. A sua solução vem direto da memória virtual dos sistemas operacionais: dividir o cache em blocos de tamanho fixo, armazená-los de forma não contígua e manter uma block table por sequência que mapeia posições lógicas para blocos físicos. Essa é a ideia em que o vLLM é construído, e é por isso que o framework importa tanto quanto a aritmética: o mesmo cache, bem alocado, atende muito mais requisições concorrentes.

![Em cima: blocos contíguos ingênuos, dimensionados para o comprimento máximo, desperdiçam memória como fragmentação interna (reservada mas não usada) e fragmentação externa (uma lacuna entre blocos). Embaixo: os blocos de tamanho fixo e não contíguos do PagedAttention se intercalam livremente, então uma sequência guarda apenas tantos blocos quantos ela realmente usou.](images/paged-attention-fragmentation.svg)

## Prática

1. ▢ Em uma frase, o que o KV cache permite a um servidor pular a cada token gerado depois do primeiro?

<details markdown="1"><summary>Verificação</summary>

Recalcular os vetores de key e value de todos os tokens anteriores da sequência, em cada camada. Só os K/V do novo token precisam ser calculados; o resto é lido do cache.

</details>

2. ▢ Um modelo tem 40 camadas e `d_model` = 5120, servido em fp16. Estime o tamanho do KV cache de uma sequência com contexto de 2048 tokens.

<details markdown="1"><summary>Dica</summary>

Use `2 × num_layers × d_model × 2 bytes` e depois multiplique pelo número de tokens.

</details>

<details markdown="1"><summary>Verificação</summary>

Por token: `2 × 40 × 5120 × 2 = 819,200 bytes ≈ 800 KB`.
Com 2048 tokens: `800 KB × 2048 ≈ 1,6 GB` para uma sequência.

</details>

3. ▢ Duas sequências seguram blocos de KV cache ingênuos, contíguos e dimensionados para o comprimento máximo. Uma delas termina muito aquém do comprimento máximo que reservou. O que acontece com a memória que ela reservou mas não usou, e o que isso custa ao servidor?

<details markdown="1"><summary>Verificação</summary>

Ela fica reservada e inutilizável por qualquer outra sequência até o cache dessa sequência ser liberado: fragmentação interna. O custo é um número menor de sequências concorrentes que o servidor consegue de fato atender, já que a memória que parece "alocada" não está fazendo trabalho útil.

</details>

4. ▢ Qual afirmação é verdadeira sobre a solução do PagedAttention?

    - a) Ela reduz o tamanho total do KV cache para um dado modelo e comprimento de contexto
    - b) Ela remove o KV cache e recalcula a atenção sob demanda
    - c) Ela reduz a memória desperdiçada ao armazenar o cache em blocos de tamanho fixo e não contíguos
    - d) Ela só ajuda stacks de serving em CPU como o llama.cpp

<details markdown="1"><summary>Verificação</summary>

**c)** Ela reduz a memória desperdiçada ao armazenar o cache em blocos de tamanho fixo e não contíguos, endereçados por uma block table por sequência, a mesma ideia da paginação de memória virtual dos sistemas operacionais.

(a) é falsa: o custo por token não muda; só o desperdício em volta dele diminui. (b) é falsa: o cache continua lá, apenas alocado melhor. (d) é falsa: o PagedAttention é uma técnica de serving em GPU (vLLM); este workspace trata o llama.cpp separadamente.

</details>

## Prática no mundo real

- [ ] Escolha um modelo que você pretende servir. Calcule o tamanho do seu KV cache por token com a fórmula acima, a partir do `num_layers` e do tamanho oculto publicados.
- [ ] Calcule o tamanho total dos pesos desse mesmo modelo na precisão em que você o serviria e compare com o tamanho do KV cache no seu contexto máximo.
- [ ] Amanhã: encontre a documentação de uma stack de serving (vLLM ou llama.cpp) e localize a flag que controla quanta memória ela reserva para o KV cache.

## Para ir além

- [Artigo: "Transformer Inference Arithmetic", Kipply](https://kipp.ly/transformer-inference-arithmetic/)
- [Artigo científico: "Efficient Memory Management for Large Language Model Serving with PagedAttention", Kwon et al., SOSP 2023](https://arxiv.org/abs/2309.06180)
- [Recursos](../RESOURCES.md)

---

Não ficou claro? Releia a fonte principal no topo, já que esta lição a comprime e é na compressão que o entendimento escapa. Consulte o [glossário](../GLOSSARY.md) para qualquer termo que pareceu escorregadio.

Se o problema é a lição em si, e não o material, isso é um defeito: [abra uma issue](https://github.com/TokenCemetery/teach/issues).
