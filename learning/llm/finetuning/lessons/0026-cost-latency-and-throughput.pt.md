---
title: "26. Custo, latência e throughput"
description: "Prefill versus decode, e para onde o dinheiro realmente vai"
type: lesson
---

# Lição 26. Custo, latência e throughput

**Ligação com a missão:** "Medir o que isso custou em qualidade e latência" está na lista de sucesso. O fine-tuning é com frequência uma decisão de *custo*, e esta é a aritmética por trás dela.
**Fonte principal:** [Artigo: "LLM Inference Performance Engineering: Best Practices", Databricks](https://www.databricks.com/blog/llm-inference-performance-engineering-best-practices)
**Pré-requisitos:** [Lição 25](0025-serving-adapters.md)

## Aquecimento

1. ▢ Qual é o argumento operacional a favor do serving sem merge?

<details markdown="1"><summary>Verificação</summary>

O rollback é uma mudança de roteamento e não uma implantação, e o base intocado continua disponível como fallback e ponto de comparação.

</details>

2. ▢ Por que você precisa avaliar o artefato que entrega?

<details markdown="1"><summary>Verificação</summary>

A quantização do momento do serving carrega um custo permanente em qualidade por requisição. Números de um modelo em bf16 não descrevem uma implantação em 4 bits.

</details>

3. ▢ Em que o fine-tuning é ruim para ensinar?

<details markdown="1"><summary>Verificação</summary>

Fatos novos, capacidade de raciocínio ausente, informação atual, cálculo preciso.

</details>

## Saiba isto

### O formato em duas fases da inferência

A geração tem duas fases com características de desempenho completamente diferentes, e confundi-las torna incoerente toda discussão de otimização.

O **prefill** processa o prompt de entrada inteiro de uma vez. Todos os tokens estão disponíveis, então o trabalho é uma grande multiplicação de matrizes em paralelo, o que o torna **limitado por computação.** O custo escala com o comprimento do prompt.

O **decode** gera um token por vez, cada um dependendo do anterior. Cada passo lê todos os pesos do modelo para produzir um único token, então a aritmética por byte movido é minúscula, o que o torna **limitado pela largura de banda de memória.** O custo escala com o comprimento da saída.

![Oito tokens de prompt alimentando uma única passada na linha do prefill, contra quatro passadas encadeadas separadas na linha do decode, uma por token de saída.](images/one-pass-or-one-each.svg)

Uma caixa na linha de cima contra quatro na de baixo é toda a assimetria. Alongar o prompt alarga a passada única; alongar a saída adiciona caixas à cadeia.

Consequências:

- **Prompts longos são baratos por token; saídas longas são caras por token.** Não é simétrico, e a assimetria é grande.
- A velocidade do decode é definida pela largura de banda de memória, então um modelo menor é mais rápido quase na proporção do seu tamanho.
- O batching ajuda enormemente o decode, porque os pesos são lidos uma vez para o batch inteiro, e ajuda muito menos o prefill.

### As métricas que importam

| Métrica | Significado | Definida por |
|---|---|---|
| Time to first token | Latência do prefill | Comprimento do prompt, computação |
| Inter-token latency | Tempo por token de saída | Largura de banda de memória, tamanho do modelo |
| Latência total | Ponta a ponta | As duas, mais fila |
| Throughput | Tokens/segundo em todas as requisições | Eficiência do batching |
| Custo por requisição | Dinheiro | Throughput e custo do hardware |

Latência e throughput se trocam entre si pelo batch size. Batches maiores elevam o throughput e elevam a latência por requisição. Não existe uma única melhor configuração: depende de haver ou não um humano esperando.

### Onde o fine-tuning muda a economia

Esta é a parte que as pessoas perdem. O benefício de custo do fine-tuning geralmente não tem nada a ver com os pesos serem melhores.

**Prompts mais curtos.** Um modelo com fine-tuning não precisa de exemplos few-shot, nem de longas instruções de formato, nem de um system prompt elaborado, porque esse comportamento está nos pesos. Se o seu prompt cai de 2,000 tokens para 200, você removeu 1,800 tokens de prefill de cada requisição, para sempre. Em um endpoint de alto volume isso costuma ser todo o caso de negócio.

**Saídas mais curtas.** Um modelo treinado para responder no formato exigido para de encher a resposta com preâmbulo e ressalvas. Como o decode é a fase cara, reduzir o comprimento da saída vale mais por token do que reduzir o comprimento da entrada.

**Um modelo menor passando a ser suficiente.** A versão mais forte do argumento: um modelo pequeno com fine-tuning que iguala um modelo grande geral na sua tarefa estreita é dramaticamente mais barato por requisição e tem menor latência, porque o decode é limitado pela largura de banda e a largura de banda escala com o tamanho. Trocar um modelo grande geral por um pequeno especializado é onde moram as economias de ordem de grandeza.

**Menos tentativas repetidas.** Se o modelo geral produz saída inválida 15% das vezes e você tenta de novo, o seu custo real é 1.15× o custo visível. Um fine-tune que chega a 99% de validade remove quase tudo isso.

### A contabilidade honesta

Contra essas economias, conte os custos:

| Custo | Natureza |
|---|---|
| Computação de treinamento | Pontual por versão, geralmente pequena para adapters |
| Criação de dados | Muitas vezes o custo dominante, e em geral tempo humano |
| Infraestrutura de avaliação | Pontual, depois manutenção contínua |
| Complexidade de serving | Contínua: stack com suporte a adapters, versionamento, roteamento |
| Retreinamento | Contínuo: modelos, dados e requisitos todos se movem |
| Expertise | Contínua: alguém precisa ser o dono disto |

**Os custos recorrentes é que decidem, e são os que ficam de fora da estimativa inicial.** Um fine-tune que economiza um pouco de dinheiro por requisição e exige uma pessoa para mantê-lo é uma troca ruim em baixo volume e uma boa em alto volume. O ponto de cruzamento é aritmética, então faça a aritmética.

### Uma comparação calculada

Suponha um modelo grande geral com um prompt de 2,000 tokens contra um modelo pequeno com fine-tuning e um prompt de 200 tokens, ambos produzindo 150 tokens de saída.

```text
General:  2000 prefill + 150 decode, on a large model
Tuned:     200 prefill + 150 decode, on a small model
```

A economia de prompt é de 1,800 tokens de prefill. A economia de tamanho de modelo vale para as duas fases e especialmente para o custo de largura de banda do decode. Multiplique pelo volume de requisições, compare com os custos fixos e recorrentes acima, e você tem uma resposta de verdade em vez de uma intuição.

Com mil requisições por dia isso pode não pagar o trabalho de dados. Com um milhão, muito provavelmente paga. **O volume é a variável decisiva, e é a menos declarada.**

### Meça, não modele

Tudo o que está acima tem o formato certo e a precisão errada. Os números reais dependem de hardware, stack de serving, batch size, comprimentos de sequência e padrão de tráfego de formas que nenhuma fórmula captura. Meça:

- Time to first token e inter-token latency, nos seus comprimentos reais de prompt
- Throughput em vários batch sizes, para achar o seu ponto de latência/throughput
- Custo por mil requisições, no seu formato real de tráfego
- As mesmas três para a alternativa contra a qual você está comparando

E meça sob carga realista. Um benchmark com uma requisição por vez não diz nada sobre um endpoint de produção com batching, porque o batching é o fator dominante no throughput.

## Prática

1. ▢ Qual fase é limitada por computação, qual é limitada pela largura de banda, e o que decorre disso?

<details markdown="1"><summary>Verificação</summary>

O prefill é limitado por computação, porque o prompt inteiro é processado em paralelo. O decode é limitado pela largura de banda de memória, porque cada passo lê todos os pesos para produzir um token.

Decorre que prompts longos são relativamente baratos por token, saídas longas são caras, o batching ajuda o decode muito mais do que o prefill, e modelos menores aceleram o decode quase na proporção do tamanho.

</details>

2. ▢ O seu fine-tune reduz o comprimento do prompt de 1,800 tokens para 150 e deixa o comprimento da saída inalterado. De onde vem a economia?

<details markdown="1"><summary>Verificação</summary>

Do prefill: 1,650 tokens a menos de trabalho limitado por computação em toda requisição. O comportamento antes especificado por exemplos few-shot e instruções de formato agora mora nos pesos.

Esse costuma ser todo o caso econômico do fine-tuning, e não tem nada a ver com o modelo ser mais inteligente.

</details>

3. ▢ Qual benefício do fine-tuning produz a maior redução de custo?

    - a) O prompt ficando mil tokens mais curto
    - b) Um modelo menor passando a ser suficiente para a tarefa
    - c) A saída ficando cinquenta tokens de saída mais curta
    - d) A taxa de tentativas repetidas caindo de quinze por cento para um

<details markdown="1"><summary>Verificação</summary>

**b)** Um modelo menor passando a ser suficiente para a tarefa.

Ele reduz as duas fases de uma vez, e o decode, a fase cara, escala com o tamanho do modelo porque é limitado pela largura de banda. As outras são reais e aditivas, mas uma mudança de tamanho de modelo é multiplicativa sobre tudo.

</details>

4. ▢ Quais custos são mais frequentemente omitidos da estimativa inicial?

<details markdown="1"><summary>Verificação</summary>

Os recorrentes: retreinamento conforme modelos e requisitos se movem, complexidade de serving, manutenção da avaliação e a expertise de uma pessoa que seja dona disso.

A computação de treinamento é barata para adapters e é a que se cita. O custo humano contínuo é caro e é esquecido, e costuma ser o que decide a questão.

</details>

5. ▢ Você mede a latência de uma única requisição e conclui que o seu endpoint é rápido o bastante. O que está errado?

<details markdown="1"><summary>Verificação</summary>

A produção atende requisições concorrentes em batches. O batch size domina tanto o throughput quanto a latência por requisição, e uma medição de requisição única não observa nenhum dos dois.

Meça sob concorrência realista, em vários batch sizes, e escolha o seu ponto na curva de latência/throughput de propósito.

</details>

6. ▢ Mesma tarefa, mesma economia por requisição, 500 requisições por dia contra 5 milhões. Mesma decisão?

<details markdown="1"><summary>Verificação</summary>

Não. Os custos fixos e recorrentes de criação de dados, avaliação, complexidade de serving e manutenção são essencialmente independentes do volume, enquanto as economias escalam com ele.

Com 500 por dia, o custo humano recorrente quase certamente domina. Com 5 milhões, ele é desprezível diante das economias. O volume é a variável decisiva e pertence à primeira frase da proposta.

</details>

## Prática no mundo real

- [ ] Meça o time to first token e a inter-token latency do seu modelo nos seus comprimentos reais de prompt.
- [ ] Meça o throughput com batch sizes 1, 4, 16 e 64. Trace a troca entre latência e throughput e escolha o seu ponto.
- [ ] Calcule o custo por mil requisições do seu caminho com fine-tuning e da alternativa. Inclua os custos recorrentes.
- [ ] Amanhã: encontre o volume de requisições em que o seu fine-tune se paga. Compare com o seu volume real.

## Para ir além

- [Artigo: "LLM Inference Performance Engineering: Best Practices", Databricks](https://www.databricks.com/blog/llm-inference-performance-engineering-best-practices)
- [Docs: Optimization and tuning, vLLM](https://docs.vllm.ai/en/latest/configuration/optimization.html)
- [Lição 27. Quando não fazer fine-tuning](0027-when-not-to-fine-tune.md)

---

Não ficou claro? Releia a fonte principal no topo, já que esta lição a comprime e é na compressão que o entendimento escapa. Consulte o [glossário](../GLOSSARY.md) para qualquer termo que pareceu escorregadio.

Se o problema é a lição em si, e não o material, isso é um defeito: [abra uma issue](https://github.com/TokenCemetery/teach/issues).
