---
title: "17. O que o QLoRA realmente custa"
description: "Separar a degradação do base da degradação do treinamento"
type: lesson
---

# Lição 17. O que o QLoRA realmente custa

**Ligação com a missão:** A missão diz "explicar as diferenças medidas, e não as anunciadas". Esta lição é a medição.
**Fonte principal:** [Artigo científico: "QLoRA: Efficient Finetuning of Quantized LLMs", Dettmers et al., arXiv:2305.14314](https://arxiv.org/abs/2305.14314)
**Pré-requisitos:** [Lição 16](0016-training-through-a-quantized-base.md)

## Aquecimento

1. ▢ Por que um base de 4 bits congelado ainda consegue repassar gradientes?

<details markdown="1"><summary>Verificação</summary>

Ele é uma constante no grafo. Propagar o gradiente exige lê-lo em alta precisão, e não derivar em relação a ele, e nenhum gradiente é armazenado para ele.

</details>

2. ▢ Qual componente do QLoRA é genuinamente específico do CUDA?

<details markdown="1"><summary>Verificação</summary>

Os paged optimizers, que dependem da memória unificada da NVIDIA. E eles importam menos no treinamento de adapters, em que o estado do otimizador é pequeno.

</details>

3. ▢ Onde você faz o merge de um adapter treinado contra um base de 4 bits?

<details markdown="1"><summary>Verificação</summary>

No base de precisão total, e depois quantiza, se necessário.

</details>

## Saiba isto

### A alegação do artigo, enunciada com precisão

O resultado de destaque do QLoRA é que o fine-tuning com adapter em NF4 de 4 bits pode igualar o desempenho do fine-tuning em 16 bits nas tarefas medidas. É um resultado forte e genuíno.

Mas é também uma alegação sobre **uma configuração específica em benchmarks específicos**. O que ele não estabelece:

- Que o NF4 é de graça na *sua* tarefa. Benchmarks de seguimento de instruções não são a sua distribuição de produção.
- Que a quantização é de graça em toda escala. O erro de quantização é uma perturbação relativa fixa, e modelos pequenos têm menos redundância para absorvê-la, então a degradação costuma ser mais visível em modelos pequenos do que em grandes.
- Que toda implementação de 4 bits é equivalente. Tipo de quantização, tamanho de bloco, dupla quantização ligada ou não, compute dtype e qualidade do kernel variam.

Ler a alegação de um artigo como "a quantização é de graça" é exatamente o modo de falha a que a expressão da missão, *medido, e não anunciado*, se dirige.

### Separando os dois custos

Há duas perguntas de qualidade distintas, e confundi-las torna os resultados ininterpretáveis.

**Custo 1. O base quantizado é um modelo pior, antes de qualquer treinamento.** Puramente uma propriedade da representação.

**Custo 2. Treinar contra um base quantizado gera um adapter pior.** Uma propriedade do processo de treinamento, além do custo 1.

Meça-os separadamente:

| Configuração | Isola |
|---|---|
| Base em bf16, sem adapter | O ponto de referência |
| Base em 4 bits, sem adapter | Custo 1, só o dano da quantização |
| Base em bf16 + adapter | O teto do treinamento |
| Base em 4 bits + adapter | Custo 1 e 2 combinados |
| Adapter treinado em 4 bits com merge no base em bf16 | Se o custo 1 sobrevive no artefato |

![Precisão do base contra adapter como uma grade dois por dois contendo o ponto de referência, o teto do treinamento, o custo 1 sozinho e os dois custos juntos, com uma quinta caixa abaixo da grade para um adapter treinado em 4 bits e com merge em um base bf16.](images/the-one-that-is-not-a-cell.svg)

Quatro das cinco configurações são células de uma única grade. A quinta não é, porque usa um base diferente para o treinamento e para a implantação, e uma configuração sem célula onde se encaixar é fácil de esquecer de executar.

Essa última linha é a interessante e é rotineiramente pulada. Você treinou contra um base degradado, mas pode *implantar* contra o de precisão total. Se o adapter aprendeu a compensar o erro de quantização, e portanto fica descasado quando o erro desaparece, é uma pergunta empírica com uma resposta real para a sua tarefa. Meça em vez de presumir qualquer um dos lados.

### Como medir com honestidade

**Mantenha todo o resto fixo.** Mesmos dados, mesma divisão, mesma seed, mesmo rank, alpha, learning rate, schedule e passos. Uma variável: a precisão do base. Uma comparação com duas mudanças nela não é uma comparação.

**Use uma métrica da tarefa, e não a loss.** A loss não é comparável entre configurações do jeito que você quer, e não é o que lhe importa. A Lição 23 cobre a escolha de métrica.

**Reporte uma dispersão, e não um ponto.** Execute cada configuração com três seeds. Se a sua variação de seed para seed é de 2 pontos e o seu efeito de quantização é de 1 ponto, você não mediu nada, e isso acontece o tempo todo. Uma comparação de seed única entre duas configurações é uma anedota.

**Meça também velocidade e memória.** Elas são o motivo de você estar considerando a quantização, então pertencem à mesma tabela que a qualidade.

### Uma tabela de resultados que vale produzir

| Config | Métrica da tarefa | Memória de pico | Seg/passo |
|---|---|---|---|
| base em bf16 + adapter | | | |
| base em NF4 + adapter | | | |
| NF4 sem dupla quantização | | | |
| int4 em vez de NF4 | | | |
| NF4, com merge em bf16 para o eval | | | |

Preencher isto uma vez, em uma tarefa que importa para você, vale mais do que qualquer quantidade de leitura sobre quantização. A última linha em particular vai dizer algo que você não consegue pesquisar.

### O que esperar, para poder se surpreender

Expectativas aproximadas da literatura e da prática comum, como um prior a ser atualizado, e não como um resultado:

- **Memória:** redução de aproximadamente 4× nos pesos do base. Confiável, é aritmética.
- **Velocidade:** mais lento por passo, muitas vezes de forma perceptível. A desquantização é trabalho de verdade.
- **Qualidade:** pequena degradação, muitas vezes dentro do ruído de seed em modelos maiores, mais visível em modelos menores e em tarefas com margens estreitas.
- **NF4 versus int4:** NF4 melhor com armazenamento idêntico.
- **Dupla quantização:** economia de memória com efeito desprezível na qualidade.

Se as suas medições discordam bastante destas, vale investigar em vez de descartar. A causa mais comum é um caminho de kernel não otimizado no seu backend, ou uma comparação em que mais de uma coisa mudou.

### Quando recorrer ao QLoRA

**Use-o quando a memória for a restrição que manda**, ou seja, quando um base em bf16 mais ativações não cabe e a alternativa é não treinar, ou treinar um modelo menor. Um modelo grande em 4 bits costuma vencer um pequeno em bf16.

**Não o use quando a memória não for a restrição.** Se o bf16 cabe, quantizar custa velocidade e um pouco de qualidade à toa. O reflexo de tutorial de sempre carregar em 4 bits é um custo sem benefício quando você tinha a memória de qualquer jeito.

## Prática

1. ▢ Enuncie a alegação de destaque do QLoRA e depois enuncie o que ela não estabelece.

<details markdown="1"><summary>Verificação</summary>

Alegação: o fine-tuning com adapter em NF4 de 4 bits pode igualar o desempenho do fine-tuning em 16 bits nos benchmarks medidos.

Não estabelece: que isso vale na sua tarefa e distribuição, que vale igualmente em escala pequena de modelo, ou que qualquer implementação de 4 bits é equivalente à do artigo.

</details>

2. ▢ Nomeie os dois custos de qualidade separados e como você os isola.

<details markdown="1"><summary>Verificação</summary>

Custo 1: o base quantizado é um modelo pior antes do treinamento, então meça o base sem adapter, quantizado versus não.

Custo 2: treinar contra um base quantizado gera um adapter pior, então compare adapters treinados em bases quantizados versus de precisão total, com todo o resto fixo.

</details>

3. ▢ Você mede 71.2 para bf16 e 70.8 para NF4. A quantização está custando 0.4 ponto a você?

<details markdown="1"><summary>Verificação</summary>

Não se sabe. Sem uma dispersão de seeds você não consegue distinguir 0.4 de ruído, e a variação de seed para seed em uma execução de fine-tuning com frequência a supera.

Execute três seeds por configuração e compare as distribuições. Uma diferença de seed única desse tamanho não é um resultado.

</details>

4. ▢ Qual comparação é a mais frequentemente pulada, e o que ela diz a você?

<details markdown="1"><summary>Verificação</summary>

Avaliar um adapter treinado em 4 bits com merge no base de precisão total.

Ela diz se o custo da quantização precisa sobreviver no seu artefato implantado. Você treinou barato, mas nada obriga você a servir barato. Ela também revela se o adapter se adaptou ao próprio erro de quantização.

</details>

5. ▢ Sua execução em bf16 cabe na memória com folga. Você deve passar para 4 bits mesmo assim?

<details markdown="1"><summary>Verificação</summary>

Não. Você pagaria passos mais lentos e um pequeno risco de qualidade para economizar memória que não estava faltando.

A quantização é uma resposta a uma restrição de memória que manda. Aplicá-la por reflexo, porque o tutorial fez isso, é um custo sem o benefício correspondente.

</details>

6. ▢ O NF4 degrada de forma perceptível a sua tarefa de modelo de 1B, mas o artigo relatou nenhuma degradação. Você está contradizendo o artigo?

<details markdown="1"><summary>Verificação</summary>

Não. O erro de quantização é uma perturbação relativa fixa e modelos pequenos têm menos redundância para absorvê-la, então a degradação costuma ser mais visível em escala pequena. A sua tarefa e a sua métrica também diferem dos benchmarks medidos.

Os dois resultados podem estar certos. É exatamente por isso que a missão pede diferenças medidas, e não anunciadas.

</details>

## Prática no mundo real

- [ ] Preencha a tabela de comparação de cinco linhas em uma tarefa que importa para você. Três seeds por linha.
- [ ] Meça a memória de pico e os segundos por passo de cada linha, junto com o número de qualidade.
- [ ] Avalie o adapter treinado em 4 bits com merge no base em bf16. Anote se ele superou, igualou ou perdeu para a versão servida em 4 bits.
- [ ] Amanhã: escreva um parágrafo dizendo o que a quantização custou a *você*, com números, e como isso difere do que você esperava.

## Para ir além

- [Artigo científico: "QLoRA: Efficient Finetuning of Quantized LLMs", Dettmers et al., arXiv:2305.14314](https://arxiv.org/abs/2305.14314): leia a seção de limitações
- [r/LocalLLaMA](https://www.reddit.com/r/LocalLLaMA/): o maior conjunto de medições de profissionais em hardware de consumo, e vale confrontar os seus números com ele
- [Lição 23. Métricas que significam alguma coisa](0023-metrics-that-mean-something.md)

---

Não ficou claro? Releia a fonte principal no topo, já que esta lição a comprime e é na compressão que o entendimento escapa. Consulte o [glossário](../GLOSSARY.md) para qualquer termo que pareceu escorregadio.

Se o problema é a lição em si, e não o material, isso é um defeito: [abra uma issue](https://github.com/TokenCemetery/teach/issues).
