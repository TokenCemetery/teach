---
title: "19. Quando o DoRA vence, e quando não"
description: "Prever o ganho antes de executar"
type: lesson
---

# Lição 19. Quando o DoRA vence, e quando não

**Ligação com a missão:** "Consegue prever quando o DoRA vence o LoRA antes de executar" é a barra desta etapa. Previsão, não experimento.
**Fonte principal:** [Artigo científico: "DoRA: Weight-Decomposed Low-Rank Adaptation", Liu et al., arXiv:2402.09353](https://arxiv.org/abs/2402.09353)
**Pré-requisitos:** [Lição 18](0018-dora-magnitude-and-direction.md), [Lição 17](0017-what-qlora-costs.md)

## Aquecimento

1. ▢ O que a renormalização do DoRA impede `BA` de fazer?

<details markdown="1"><summary>Verificação</summary>

Mudar a magnitude. Depois da renormalização, `BA` afeta apenas a direção, e a magnitude vem do `m` treinado separadamente.

</details>

2. ▢ Por que a norma por coluna não pode ser guardada em cache entre passos?

<details markdown="1"><summary>Verificação</summary>

Ela é a norma de `W₀ + BA`, e `BA` muda a cada passo do otimizador.

</details>

3. ▢ Por que uma comparação de qualidade precisa usar várias seeds?

<details markdown="1"><summary>Verificação</summary>

Porque a variação de seed para seed com frequência supera o efeito que está sendo medido, então uma diferença de seed única não pode ser distinguida de ruído.

</details>

## Saiba isto

### O padrão relatado

Os ganhos do DoRA sobre o LoRA são **maiores em rank baixo e diminuem conforme o rank aumenta.**

O raciocínio decorre diretamente do mecanismo. Em rank 4 ou 8, a atualização de baixo rank tem muito pouca capacidade, e qualquer parte dessa capacidade gasta em ajuste de magnitude é capacidade não gasta em direção. O DoRA entrega a magnitude a um parâmetro separado, barato e dedicado, liberando o orçamento de baixo rank inteiro para a direção. Em rank 128 o orçamento já não é escasso, então liberar um pouco dele muda menos.

Assim a regra de previsão não é "o DoRA é melhor", e sim:

> **O DoRA ajuda mais exatamente onde a capacidade do LoRA é mais apertada.**

### Quando esperar um ganho

| Situação | Espere | Porque |
|---|---|---|
| Rank muito baixo (4 a 16) | Ganho significativo | A capacidade é escassa; o desacoplamento libera um pouco |
| Rank forçado para baixo por restrições | Ganho significativo | Mesmo motivo, e você não tem alternativa |
| Rank médio (32 a 64) | Ganho menor | A capacidade é menos escassa |
| Rank alto (128+) | Pouco ou nenhum | A capacidade não é o limite que manda |
| Você poderia simplesmente aumentar o rank | Aumente o rank | Mais barato em tempo real do que o custo por passo do DoRA |
| O tempo por passo é a sua restrição | Pule o DoRA | Você estaria pagando dezenas de por cento por um ganho pequeno |

Essa quinta linha é a que vale internalizar. Se o rank é uma variável livre, **aumentar o rank costuma ser uma jogada melhor do que trocar para o DoRA**, porque rank extra custa quase nada de memória (Lição 7) e quase nada de tempo, enquanto o DoRA custa tempo real a cada passo. O DoRA conquista o seu lugar quando o rank *não* é livre, quando algo além da memória o está mantendo baixo.

### O que de fato mantém o rank baixo

Vale ser concreto, já que toda a recomendação depende disso:

- **Overfitting em um dataset pequeno.** Mais rank significa mais memorização. Aqui você de fato não pode aumentar o rank, e o DoRA é uma opção real: você aproveita melhor um rank que está mantendo pequeno de propósito.
- **Uma restrição de serving sobre o tamanho do adapter.** Rara, mas se você distribui adapters ou guarda muitos na memória ao mesmo tempo, o tamanho pode pesar.
- **Reproduzir uma configuração publicada.** Você fica preso ao rank deles.
- **Orçamento total de tempo de treinamento.** Note que este corta *contra* o DoRA em vez de a favor, porque o DoRA é mais lento por passo.

Se nenhum deles se aplica, o rank é livre, e a ação mais simples está disponível.

### Lendo a alegação com senso crítico

O artigo do DoRA relata ganhos em várias tarefas e famílias de modelos, com a análise de magnitude e direção como seu argumento mecanístico. Essa análise é genuinamente esclarecedora e o método é bem motivado.

Três coisas a ter em mente:

**Os ganhos relatados costumam ser pequenos em termos absolutos**, um ponto ou dois em um benchmark. Compare isso com o seu ruído de seed antes de tratá-lo como real na sua tarefa.

**O baseline da comparação importa.** DoRA em rank 8 versus LoRA em rank 8 é a comparação do artigo e é a certa para isolar o mecanismo. DoRA em rank 8 versus LoRA em rank 32 é a comparação que *você* enfrenta ao decidir o que executar, e é uma pergunta diferente, com uma resposta possivelmente diferente.

**A replicação independente é mais escassa do que para o LoRA ou o QLoRA.** O LoRA tem anos de evidência de profissionais em incontáveis tarefas. O DoRA tem menos. Isso não é uma crítica ao método; é um motivo para medir na sua própria tarefa em vez de importar uma conclusão.

### O procedimento de decisão

1. O rank é livre para aumentar? → Aumente-o. Não use o DoRA.
2. O rank está fixado em valor baixo, e por quê? → Se por risco de overfitting ou uma restrição rígida, o DoRA é um candidato real.
3. O tempo por passo já é a restrição que manda? → Não use o DoRA.
4. Caso contrário: execute os dois, mesmo conjunto de seeds, todo o resto igual, e compare com o ruído de seed.

O passo 4 não é uma falha do procedimento. Ser capaz de dizer "o efeito esperado aqui é pequeno e preciso medir" *é* a resposta sênior, e é uma posição muito melhor do que acreditar no artigo sem crítica ou descartá-lo.

## Prática

1. ▢ Por que os ganhos do DoRA diminuem conforme o rank sobe?

<details markdown="1"><summary>Verificação</summary>

Seu benefício é liberar a capacidade de baixo rank da obrigação de representar mudanças de magnitude. Quando o rank é escasso, essa capacidade liberada importa proporcionalmente muito; quando o rank é generoso, a capacidade não era o fator limitante, então liberar um pouco dela muda pouco.

</details>

2. ▢ Você está em rank 8 e pode aumentar o rank livremente. DoRA ou mais rank?

<details markdown="1"><summary>Verificação</summary>

Mais rank. Custa quase nada de memória e quase nada de tempo, enquanto o DoRA custa uma penalidade por passo em todo passo de toda execução futura.

Recorra ao DoRA quando o rank estiver fixado por algo, em geral risco de overfitting em um dataset pequeno, e não quando ele for uma variável livre.

</details>

3. ▢ 600 exemplos de treinamento, rank mantido em 8 para limitar a memorização. Vale tentar o DoRA?

<details markdown="1"><summary>Verificação</summary>

Sim. Este é o caso a que o método melhor se adequa: o rank é baixo de propósito por um motivo que você não pode remover, então aproveitá-lo melhor é a única melhoria disponível.

Meça contra o LoRA no mesmo rank com várias seeds, já que o efeito esperado é pequeno.

</details>

4. ▢ Distinga a comparação do artigo da sua.

<details markdown="1"><summary>Verificação</summary>

O artigo compara DoRA e LoRA com rank igualado, o que isola corretamente o mecanismo.

A sua decisão é entre o DoRA no rank que você pode bancar e o LoRA no rank que você pode bancar, e como o LoRA é mais rápido por passo você talvez consiga bancar mais rank com ele. Mesmos números, pergunta diferente.

</details>

5. ▢ O que prevê com mais confiabilidade uma vitória do DoRA?

    - a) Um dataset de treinamento grande com muitos exemplos diversos
    - b) Um rank baixo que não pode ser aumentado por outros motivos
    - c) Um base model quantizado em precisão NF4 de quatro bits
    - d) Um conjunto de target modules cobrindo todas as camadas lineares

<details markdown="1"><summary>Verificação</summary>

**b)** Um rank baixo que não pode ser aumentado por outros motivos.

Tamanho do dataset, precisão do base e cobertura dos target modules são todos ortogonais ao mecanismo. A escassez de capacidade de baixo rank é o que o DoRA alivia.

</details>

6. ▢ O seu ganho medido do DoRA é 0.6 ponto, com dispersão de seeds de 1.4 ponto. O que você conclui e o que faz?

<details markdown="1"><summary>Verificação</summary>

Que você não detectou um efeito. A diferença está bem dentro do ruído.

Ou execute seeds suficientes para resolver uma diferença tão pequena, o que pode ser muitas, ou aceite que o efeito é pequeno demais para importar aqui e fique com o método mais rápido. Decidir que não vale a pena resolver é um resultado legítimo e muitas vezes correto.

</details>

## Prática no mundo real

- [ ] Execute LoRA e DoRA em rank 8, três seeds cada, todo o resto fixo. Compare a diferença com a dispersão de seeds.
- [ ] Execute o LoRA em rank 32 pelo mesmo orçamento de tempo real que o DoRA em rank 8. Anote qual produziu o melhor modelo por unidade de tempo.
- [ ] Amanhã: escreva, antes de executar qualquer coisa, a sua previsão de se o DoRA vai ajudar na sua tarefa real e por quê. Guarde-a e confira depois.

## Para ir além

- [Artigo científico: "DoRA: Weight-Decomposed Low-Rank Adaptation", Liu et al., arXiv:2402.09353](https://arxiv.org/abs/2402.09353)
- [Hiperparâmetros do LoRA](../reference/lora-hyperparameters.md)
- [Lição 20. Julgando uma nova variante de PEFT](0020-judging-a-new-variant.md)

---

Não ficou claro? Releia a fonte principal no topo, já que esta lição a comprime e é na compressão que o entendimento escapa. Consulte o [glossário](../GLOSSARY.md) para qualquer termo que pareceu escorregadio.

Se o problema é a lição em si, e não o material, isso é um defeito: [abra uma issue](https://github.com/TokenCemetery/teach/issues).
