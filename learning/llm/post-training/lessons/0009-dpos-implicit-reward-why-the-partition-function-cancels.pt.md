---
title: "9. A recompensa implícita do DPO: por que a função de partição se cancela"
description: "Um termo normalizador intratável fica entre uma recompensa e a sua policy ótima, até que uma diferença de duas recompensas o faz desaparecer"
type: lesson
---

# Lição 9. A recompensa implícita do DPO: por que a função de partição se cancela

**Ligação com a missão:** "Derivar a recompensa implícita do DPO a partir dos mesmos dados de preferência que o RLHF usa e dizer o que ele abre mão ao remover o loop de RL" é o quarto item de O sucesso se parece com isto. Esta lição cobre a derivação em si; a lição 10 cobre a loss resultante e o que ela deixa de fora em relação ao PPO.
**Fonte principal:** [Artigo científico: "Direct Preference Optimization: Your Language Model is Secretly a Reward Model", Rafailov et al., 2023](https://arxiv.org/abs/2305.18290)
**Pré-requisitos:** [Lição 8](0008-why-ppo-is-expensive-and-unstable.md)

## Aquecimento

1. ▢ Cite os quatro (ou cinco, contando a função de valor separadamente) modelos envolvidos em um passo de treinamento de PPO para RLHF, e para que cada um é usado.

<details markdown="1"><summary>Verificação</summary>

A policy sendo treinada; um modelo SFT congelado, para a penalidade de KL; o reward model, que pontua as saídas; e a função de valor (inicializada a partir do reward model), que produz as estimativas de vantagem de que o corte do PPO precisa.

</details>

2. ▢ Segundo a própria descoberta de Ouyang et al., um reward model maior e com loss menor era sempre a melhor escolha prática para o PPO?

<details markdown="1"><summary>Verificação</summary>

Não. O reward model de 175B deles teve treinamento mais instável e custo de compute maior como inicialização da função de valor do que o de 6B, que eles constataram ser estável e igualmente eficaz, então usaram o modelo menor para todos os tamanhos de policy.

</details>

## Saiba isto

### O mesmo objetivo de partida do RLHF

Rafailov et al. partem exatamente do objetivo de maximização de recompensa com restrição de KL que a lição 6 já cobre: maximizar a recompensa esperada `r(x, y)` sob a policy, menos uma penalidade de KL (escalada por `β`) contra uma policy de referência fixa `π_ref`. Trabalhos anteriores, nos quais Rafailov et al. se baseiam diretamente, mostraram que esse objetivo tem uma solução ótima conhecida, em forma fechada:

```text
π_r(y|x) = (1 / Z(x)) · π_ref(y|x) · exp((1/β) · r(x, y))
```

onde `Z(x)` é uma **função de partição**, uma soma normalizadora sobre toda completion `y` possível para o prompt `x`, necessária para fazer de `π_r` uma distribuição de probabilidade válida. Calcular `Z(x)` exatamente significaria somar sobre toda completion possível que um modelo de linguagem poderia gerar, o que é tão intratável quanto parece, e é exatamente por isso que essa forma fechada, correta como é, não era diretamente utilizável como método de treinamento por si só.

### Invertendo a relação

O movimento de Rafailov et al. é reorganizar essa mesma equação para resolver a recompensa em vez da policy. Tomar o logaritmo dos dois lados e reorganizar dá:

```text
r(x, y) = β · log( π_r(y|x) / π_ref(y|x) ) + β · log Z(x)
```

Isso expressa a recompensa implicada por qualquer policy `π_r`, em termos dessa policy, da policy de referência e da mesma função de partição problemática, ainda presente como um termo aditivo.

### Por que a função de partição deixa de importar

É aqui que a loss de Bradley-Terry (lição 4) faz trabalho de verdade. As probabilidades de preferência de Bradley-Terry dependem apenas da *diferença* entre as recompensas de duas completions, `r(x, y_1) - r(x, y_2)`, nunca do valor absoluto de qualquer uma delas. Como `Z(x)` depende apenas do prompt `x`, e não de qual completion está sendo pontuada, ele é exatamente o mesmo termo aditivo em `r(x, y_1)` e em `r(x, y_2)`. Substituir a expressão invertida da recompensa em uma diferença de duas recompensas para o mesmo prompt faz todo termo `β · log Z(x)` se cancelar por completo. O que sobra é uma probabilidade de preferência expressa puramente em termos da policy `π_r` e da policy de referência fixa `π_ref`, sem nenhum reward model e sem nenhuma função de partição aparecendo nela.

### A recompensa implícita

Isso é exatamente o que o termo do glossário **recompensa implícita** nomeia: a função de recompensa `r(x, y) = β · log(π_r(y|x) / π_ref(y|x))` (o termo da função de partição pode ser descartado quando só as diferenças importam) que uma policy define matematicamente, só por ser a policy que é, em relação a uma referência. Nenhum reward model separado foi treinado para produzi-la; ela decorre diretamente da mesma relação de policy ótima sobre a qual o RLHF já era construído. Treinar uma policy para satisfazer diretamente os dados de preferência humana, usando essa recompensa implícita no lugar de uma treinada separadamente, é toda a ideia que dá nome ao DPO.

## Prática

1. ▢ Por que a função de partição `Z(x)` é descrita como intratável de calcular diretamente?

<details markdown="1"><summary>Verificação</summary>

Porque calculá-la exatamente exige somar sobre toda completion `y` que um modelo de linguagem poderia gerar para um dado prompt `x`, uma soma sobre um espaço enorme que não pode ser avaliada diretamente.

</details>

2. ▢ Por que `Z(x)` se cancela ao calcular a diferença `r(x, y_1) - r(x, y_2)` para duas completions do mesmo prompt, mas não se cancelaria se a recompensa de uma única completion fosse necessária isoladamente?

<details markdown="1"><summary>Dica</summary>

Pergunte de que `Z(x)` realmente depende, e se essa dependência difere entre `y_1` e `y_2`.

</details>

<details markdown="1"><summary>Verificação</summary>

`Z(x)` depende apenas do prompt `x`, e não de qual completion está sendo pontuada, então aparece como exatamente o mesmo termo aditivo (`β · log Z(x)`) tanto em `r(x, y_1)` quanto em `r(x, y_2)`. Subtrair um do outro o remove por completo. Uma recompensa isolada ainda carregaria esse mesmo termo não removido.

</details>

3. ▢ O que significa "recompensa implícita", no sentido específico em que esta lição a deriva?

<details markdown="1"><summary>Verificação</summary>

A função de recompensa `β · log(π(y|x) / π_ref(y|x))` que qualquer policy define matematicamente, em relação a uma policy de referência fixa, puramente como consequência da mesma relação de policy ótima que o objetivo do RLHF já implica. Ela nunca é treinada como um modelo separado; decorre diretamente da própria policy e da policy de referência.

</details>

4. ▢ Qual destas descreve melhor o que a derivação do DPO realiza, em relação a precisar estimar `Z(x)` diretamente?

    - a) Encontra um método numérico mais rápido para aproximar `Z(x)`
    - b) Reestrutura o problema de modo que `Z(x)` se cancele por completo sempre que só uma diferença de duas recompensas for necessária, evitando a necessidade de calculá-lo
    - c) Substitui `Z(x)` por uma segunda função de partição, mais simples
    - d) Mostra que `Z(x)` é sempre igual a 1 para modelos de linguagem

<details markdown="1"><summary>Verificação</summary>

**b)** é exatamente a derivação que esta lição percorre. As alternativas (a) e (c) pressupõem que `Z(x)` ainda precise ser calculado ou aproximado de alguma forma, o que a derivação real evita fazer. A alternativa (d) não é uma afirmação que a derivação faça ou de que precise.

</details>

## Prática no mundo real

- [ ] Leia a seção de derivação do artigo do DPO (linkado acima), do objetivo com restrição de KL até o cancelamento da função de partição, e escreva, com as suas palavras, uma frase por equação nomeando o que mudou entre ela e a anterior.
- [ ] Escreva, símbolo por símbolo, a que `β · log(π(y|x) / π_ref(y|x))` seria avaliado se a policy e a policy de referência atribuíssem exatamente a mesma probabilidade a `y`. Confirme que isso bate com a sua intuição de como "nenhum sinal de preferência vindo dessa completion" deveria se parecer.
- [ ] Amanhã: sem olhar adiante, escreva uma previsão de uma frase para a lição 10: dado que a recompensa implícita é definida puramente a partir da policy e do modelo de referência, sem reward model nem função de partição restando no quadro, que loop de treinamento você espera que o DPO precise, em comparação com o loop de amostragem e otimização do PPO?

## Para ir além

- [Artigo científico: "Direct Preference Optimization: Your Language Model is Secretly a Reward Model", Rafailov et al., 2023](https://arxiv.org/abs/2305.18290)
- [Recursos](../RESOURCES.md)

---

Não ficou claro? Releia a fonte principal no topo, já que esta lição a comprime e é na compressão que o entendimento escapa. Consulte o [glossário](../GLOSSARY.md) para qualquer termo que pareceu escorregadio.

Se o problema é a lição em si, e não o material, isso é um defeito: [abra uma issue](https://github.com/TokenCemetery/teach/issues).
