---
title: "7. Paralelismo de dados e all-reduce de gradientes"
description: "Dividir um batch entre dispositivos que guardam, cada um, uma cópia completa do modelo, e o que mantém todas as cópias idênticas"
type: lesson
---

# Lição 7. Paralelismo de dados e all-reduce de gradientes

**Ligação com a missão:** "Explicar o que o ZeRO/FSDP particionam, por que o paralelismo de dados sozinho fica sem memória antes de ficar sem compute e quando o paralelismo de tensor ou de pipeline vale o seu custo de comunicação" é o quarto item em O sucesso se parece com isto. Esta lição cobre o que é o paralelismo de dados e como ele se mantém correto; a Lição 8 cobre por que ele fica sem memória.
**Fonte principal:** [Artigo científico: "ZeRO: Memory Optimizations Toward Training Trillion Parameter Models", Rajbhandari et al., 2019](https://arxiv.org/abs/1910.02054)
**Pré-requisitos:** [Lição 6](0006-chinchilla-the-compute-optimal-correction.md)

## Aquecimento

1. ▢ Usando `FLOPs(N, D) ≈ 6ND`, aproximadamente quantos tokens um orçamento de compute de `6 × 10^21` FLOPs comporta para um modelo de 5 bilhões de parâmetros?

<details markdown="1"><summary>Verificação</summary>

200 bilhões de tokens: `6 × 10^21 / (6 × 5 × 10^9) = 2 × 10^11`.

</details>

## Saiba isto

### Dividir o batch, não o modelo

O **paralelismo de dados** é a forma mais simples de pôr mais de um dispositivo para trabalhar na mesma execução de treinamento: cada dispositivo guarda uma cópia completa e idêntica do modelo, e um único batch grande é dividido em pedaços menores por dispositivo, um para cada. Cada dispositivo executa o seu próprio forward e backward pass sobre o seu próprio pedaço, totalmente independente dos outros, calculando o seu próprio gradiente local.

### Mantendo todas as cópias idênticas

Se cada dispositivo simplesmente aplicasse o seu próprio gradiente local à sua própria cópia dos pesos, as cópias se afastariam após um passo, e "N dispositivos treinando um modelo" viraria silenciosamente "N dispositivos treinando N modelos diferentes". O paralelismo de dados evita isso com uma etapa de sincronização antes de o otimizador rodar: o gradiente local de cada dispositivo é calculado em média com os de todos os dispositivos, por meio de uma operação de comunicação coletiva chamada **all-reduce**, e cada dispositivo recebe de volta o mesmo gradiente médio. Como todo dispositivo aplica então o gradiente médio idêntico a uma cópia inicial idêntica dos pesos, todas as cópias permanecem idênticas após o passo do otimizador, passo após passo, sem nunca precisar comparar os próprios pesos.

Uma forma comum de implementar isso com eficiência é o **ring all-reduce**: os dispositivos são arranjados em um anel lógico, e cada um só troca dados com os seus dois vizinhos, em uma sequência de passos que garante que todo dispositivo termine com a soma completa (e depois a média) sem nunca precisar que um dispositivo colete tudo de todos os outros diretamente. Isso mantém o volume de comunicação por dispositivo aproximadamente constante à medida que mais dispositivos são adicionados, em vez de crescer com a contagem de dispositivos, e é isso que faz o paralelismo de dados escalar razoavelmente bem para começo de conversa.

### O que isso traz e no que não mexe

Todo o benefício do paralelismo de dados é o throughput: com `k` dispositivos, `k` vezes mais dados podem ser processados por unidade de tempo de relógio, já que cada dispositivo faz trabalho independente sobre a sua própria fatia do batch. Nada disso muda quanta memória um único dispositivo precisa. Cada dispositivo ainda guarda uma cópia completa dos parâmetros do modelo, dos seus gradientes e do seu estado do otimizador, exatamente como se estivesse treinando sozinho; adicionar mais dispositivos de dados paralelos adiciona mais cópias da mesma pegada de memória, e não menos dela por dispositivo. O paralelismo de dados é uma forma de processar mais rápido o treinamento de um modelo de tamanho fixo; sozinho, não é uma forma de encaixar um modelo maior do que um único dispositivo conseguiria guardar. A Lição 8 torna esse limite concreto.

## Prática

1. ▢ Quatro dispositivos treinam um modelo com paralelismo de dados. O dispositivo 3 calcula um gradiente local que por acaso é incomumente grande em comparação com os gradientes dos outros três dispositivos naquele passo, por causa do que quer que estivesse na sua fatia do batch. O que impede isso de fazer a cópia dos pesos do dispositivo 3 se afastar das outras três?

<details markdown="1"><summary>Verificação</summary>

A etapa de all-reduce. O gradiente local de cada dispositivo, incluindo o incomumente grande do dispositivo 3, é calculado em média com os dos quatro dispositivos antes de qualquer dispositivo aplicar uma atualização, de modo que todo dispositivo aplica o mesmo gradiente médio a uma cópia inicial idêntica dos pesos, mantendo as quatro cópias idênticas.

</details>

2. ▢ Qual destas descreve melhor o que adicionar mais dispositivos de dados paralelos muda em uma execução de treinamento?

    - a) Reduz a quantidade de memória de que cada dispositivo precisa para guardar o modelo
    - b) Permite que mais do batch seja processado por unidade de tempo, sem mudar quanta memória um único dispositivo precisa
    - c) Elimina por completo a necessidade de um passo do otimizador
    - d) Aumenta automaticamente a contagem de parâmetros do modelo

<details markdown="1"><summary>Dica</summary>

Pergunte o que de fato é dividido entre os dispositivos no paralelismo de dados: o modelo ou o batch?

</details>

<details markdown="1"><summary>Verificação</summary>

**b)** O paralelismo de dados divide o batch, e não o modelo, então o throughput escala com a contagem de dispositivos enquanto a memória por dispositivo não encolhe. (a) é exatamente o contrário, o que a Lição 8 torna concreto. (c) e (d) descrevem mudanças que o paralelismo de dados não faz de jeito nenhum.

</details>

3. ▢ Em um ring all-reduce, por que cada dispositivo só se comunica com os seus dois vizinhos no anel, em vez de cada dispositivo enviar o seu gradiente a todos os outros diretamente?

<details markdown="1"><summary>Verificação</summary>

Para que o volume de comunicação que um único dispositivo precisa tratar permaneça aproximadamente constante à medida que mais dispositivos entram no anel, em vez de crescer com o número de dispositivos, e é isso que permite a essa abordagem escalar para muitos dispositivos sem que a própria comunicação se torne o gargalo.

</details>

## Prática no mundo real

- [ ] Encontre a documentação de uma API de treinamento de dados paralelos a que você tenha acesso (o `DistributedDataParallel` do PyTorch é uma comum) e localize onde ela descreve a etapa de sincronização de gradientes. Anote como ela chama a operação e se a descrição corresponde a "all-reduce" como esta lição a descreve.
- [ ] Esboce, no papel, quatro dispositivos arranjados em um anel e acompanhe à mão o que um único dispositivo envia e recebe em um ring all-reduce ao longo de alguns passos, usando um vetor de gradiente de brinquedo com 4 números dividido a um número por dispositivo.
- [ ] Amanhã: sem olhar adiante, escreva uma previsão de uma frase para a Lição 8: se todo dispositivo de dados paralelos precisa guardar uma cópia completa dos parâmetros, dos gradientes e do estado do otimizador do modelo, o que acontece à medida que o modelo cresce enquanto o número de dispositivos permanece fixo?

## Para ir além

- [Artigo científico: "ZeRO: Memory Optimizations Toward Training Trillion Parameter Models", Rajbhandari et al., 2019](https://arxiv.org/abs/1910.02054)
- [Recursos](../RESOURCES.md)

---

Não ficou claro? Releia a fonte principal no topo, já que esta lição a comprime e é na compressão que o entendimento escapa. Consulte o [glossário](../GLOSSARY.md) para qualquer termo que pareceu escorregadio.

Se o problema é a lição em si, e não o material, isso é um defeito: [abra uma issue](https://github.com/TokenCemetery/teach/issues).
