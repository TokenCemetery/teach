---
title: "4. Batching estático vs contínuo"
description: "Por que agrupar requisições ajuda o throughput, e por que o continuous batching supera o estático"
type: lesson
---

# Lição 4. Batching estático vs contínuo

**Ligação com a missão:** O batching é a alavanca que transforma a capacidade de KV cache de um servidor, aquilo que as lições 1 a 3 ensinaram a calcular, em throughput servido de verdade; quão bem um servidor faz batching decide quanto dessa capacidade vai para trabalho útil.
**Fonte principal:** [Artigo: "How continuous batching enables 23x throughput in LLM inference while reducing p50 latency", Anyscale](https://www.anyscale.com/blog/continuous-batching-llm-inference)
**Pré-requisitos:** [Lição 3](0003-growth-prefill-decode-precision.md), [KV cache](../GLOSSARY.md)

## Aquecimento

1. ▢ Por que o decode é limitado pela largura de banda de memória e não por compute?

<details markdown="1"><summary>Verificação</summary>

Cada passo de decode lê o KV cache inteiro de volta para atender sobre ele, para calcular apenas um novo token. A quantidade de compute novo por passo é pequena em relação ao tráfego de memória necessário para ler o cache e os pesos.

</details>

2. ▢ A lição 3 distinguiu o prefill do decode. Qual dos dois processa um prompt inteiro em uma única passada forward?

<details markdown="1"><summary>Verificação</summary>

O prefill. O decode, em vez disso, gera um token de saída, e cresce o cache em um token, por passo.

</details>

## Saiba isto

### Por que agrupar passos de decode ajuda

O tráfego de memória de um passo de decode, que lê os pesos do modelo e o KV cache de toda sequência residente, quase não muda se ele calcula o próximo token de uma sequência ou os próximos tokens de várias sequências ao mesmo tempo. Agrupar em batch os passos de decode de várias sequências espalha esse mesmo tráfego de memória por mais compute útil, que é exatamente a correção de que um passo limitado pela largura de banda de memória precisa: mais trabalho feito por byte lido.

### O batching estático desperdiça esse ganho com términos desiguais

A forma óbvia de fazer batching é agrupar um conjunto fixo de requisições, rodar passos de decode até que todas tenham terminado e só então iniciar o próximo grupo. Isso é o **batching estático**, e ele tem uma falha séria: o grupo não termina até que a sua sequência mais longa termine. Toda sequência que termina cedo continua ocupando um slot do batch, sem contribuir com nada, até o grupo inteiro acabar.

Tome quatro requisições agrupadas, que precisam de 10, 20, 30 e 100 tokens de saída, respectivamente. O batch roda por 100 passos, porque é isso que a sequência mais longa precisa. Ao longo desses 100 passos, o batch consome `4 × 100 = 400` slot-steps de trabalho de GPU, mas só `10 + 20 + 30 + 100 = 160` desses slot-steps fizeram algo útil. Os outros 240 foram gastos em sequências que já tinham terminado, paradas até a fronteira do batch. São 60% de desperdício, e piora conforme cresce a dispersão entre os comprimentos das requisições, que é o caso normal: requisições reais variam enormemente no quanto geram.

### O continuous batching remove a fronteira do batch

O **continuous batching** (também chamado de scheduling em nível de iteração) faz o scheduling no nível de um único passo de decode, em vez de um grupo fixo. No instante em que uma sequência termina, o seu slot é liberado e uma nova requisição, que estava esperando, é admitida no batch já no passo seguinte, em vez de esperar que todas as outras sequências do seu antigo grupo também terminem. A composição do batch muda continuamente; é o seu tamanho, e não o tempo de vida de uma requisição qualquer, que permanece aproximadamente constante.

No exemplo das quatro requisições, a sequência que precisa de apenas 10 tokens libera o seu slot no passo 10. Um scheduler estático deixa esse slot ocioso por mais 90 passos. Um scheduler contínuo admite uma nova requisição nele imediatamente, então a GPU continua fazendo trabalho útil naquele slot em vez de carregar peso morto até uma fronteira arbitrária. Esse é o mecanismo por trás dos ganhos de throughput que a fonte principal desta lição relata: não uma computação por passo mais rápida, mas muito menos de cada passo desperdiçado em sequências que não tinham mais nada a fazer.

![Dois slots de batch ao longo de 100 passos de decode: o slot A precisa de 10 passos, o slot D precisa de 100. No batching estático, o slot A termina no passo 10 e fica ocioso por 90 passos até o batch inteiro terminar junto. No continuous batching, uma nova requisição é admitida no slot A no instante em que ele é liberado, no passo 10, então o slot continua fazendo trabalho útil.](images/static-vs-continuous-batching.svg)

## Prática

1. ▢ Um batch estático contém duas requisições que precisam de 15 e 60 tokens de saída. Quantos slot-steps o batch consome no total, quantos são úteis e que fração é desperdiçada?

<details markdown="1"><summary>Dica</summary>

O total de slot-steps é `batch size × steps until the longest sequence finishes`. Os slot-steps úteis são a soma do comprimento real de cada requisição.

</details>

<details markdown="1"><summary>Verificação</summary>

Total: `2 × 60 = 120` slot-steps. Úteis: `15 + 60 = 75`. Desperdiçados: `120 − 75 = 45`, que é `45 / 120 = 37,5%`.

</details>

2. ▢ Em um scheduler de continuous batching, o que acontece exatamente no passo em que uma sequência do batch termina de gerar?

<details markdown="1"><summary>Verificação</summary>

O seu slot é liberado imediatamente, e uma nova requisição que estava esperando é admitida nesse slot no passo seguinte, em vez de o slot ficar ocioso até que todas as outras sequências de algum grupo fixo também terminem.

</details>

3. ▢ Qual afirmação é verdadeira sobre o continuous batching em comparação com o batching estático?

    - a) Ele reduz o custo de compute por passo da própria atenção
    - b) Ele remove a exigência de KV cache das sequências terminadas antes de despejá-las
    - c) Ele mantém o batch cheio ao admitir novas requisições conforme os slots são liberados, em vez de esperar um grupo fixo terminar por completo
    - d) Ele só se aplica a stacks de serving em CPU como o llama.cpp

<details markdown="1"><summary>Verificação</summary>

**c)** Ele mantém o batch cheio continuamente. (a) é falsa: a aritmética por passo não muda; o ganho são menos slot-steps desperdiçados. (b) é falsa e inverte as coisas: o cache de uma sequência terminada é liberado como parte do seu despejo, nos dois estilos de scheduling. (d) é falsa: o continuous batching é uma técnica de scheduling de serving em GPU, mais associada ao vLLM e a engines semelhantes.

</details>

4. ▢ Um batch estático de 8 requisições precisa de exatamente 50 tokens de saída cada uma. O continuous batching melhoraria o throughput em relação ao batching estático para esse batch em particular, e por que sim ou por que não?

<details markdown="1"><summary>Verificação</summary>

Quase nada, se é que melhoraria. O ganho do continuous batching vem de preencher os slots liberados por requisições que terminam cedo enquanto outras continuam rodando. Quando toda requisição do grupo precisa do mesmo número de tokens, não há quem termine cedo nem slots ociosos para preencher, então o batching estático já não desperdiça nada aqui.

</details>

## Prática no mundo real

- [ ] Encontre a flag ou a opção de configuração que a sua stack de serving de escolha usa para habilitar o continuous batching (o vLLM o habilita por padrão; veja como a documentação dele chama o mecanismo subjacente).
- [ ] Olhe uma amostra real de tráfego ou um log de requisições a que você tenha acesso (ou um dataset público de comprimentos de requisições de LLM) e estime a dispersão entre o menor e o maior comprimento de saída. Estime a fração de desperdício do batching estático que essa dispersão causaria.
- [ ] Amanhã: leia um parágrafo sobre como um scheduler de continuous batching decide qual requisição em espera admitir em seguida, e anote se é a simples ordem de chegada ou outra coisa.

## Para ir além

- [Artigo: "How continuous batching enables 23x throughput in LLM inference while reducing p50 latency", Anyscale](https://www.anyscale.com/blog/continuous-batching-llm-inference)
- [Documentação: vLLM Documentation, vLLM Project](https://docs.vllm.ai/en/latest/)
- [Recursos](../RESOURCES.md)

---

Não ficou claro? Releia a fonte principal no topo, já que esta lição a comprime e é na compressão que o entendimento escapa. Consulte o [glossário](../GLOSSARY.md) para qualquer termo que pareceu escorregadio.

Se o problema é a lição em si, e não o material, isso é um defeito: [abra uma issue](https://github.com/TokenCemetery/teach/issues).
