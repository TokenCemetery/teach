---
title: "10. O backward pass e o autograd"
description: "Como a regra da cadeia, automatizada sobre um grafo de computação registrado, transforma uma loss escalar em um gradiente para cada peso"
type: lesson
---

# Lição 10. O backward pass e o autograd

**Ligação com a missão:** A loss escalar da lição 9 é inútil para o treinamento por si só; o backward pass é o que a transforma em um gradiente para cada peso do modelo, que é o sinal de fato usado pelo otimizador (lição 11) para melhorá-los.
**Fonte principal:** [Docs: "Autograd mechanics", PyTorch](https://pytorch.org/docs/stable/notes/autograd.html)
**Pré-requisitos:** [Lição 9](0009-cross-entropy-loss.md), [Scaled dot-product attention](../GLOSSARY.md)

## Aquecimento

1. ▢ Por que a cross-entropy usa `-log(p)` em vez de algo como `1 - p` como penalidade para uma previsão errada?

<details markdown="1"><summary>Verificação</summary>

`-log(p)` cresce sem limite à medida que a probabilidade atribuída ao token correto se aproxima de 0, penalizando o erro confiante de forma cada vez mais severa. `1 - p` satura em 1 não importa quão confiantemente errada seja a previsão, sem dar sinal extra para distinguir uma previsão meramente errada de uma catastrófica.

</details>

2. ▢ Por que as conexões residuais ajudam a treinar uma pilha profunda de blocos transformer?

<details markdown="1"><summary>Verificação</summary>

Elas dão aos gradientes um caminho direto pela conexão identidade `+ x` em cada camada, seja qual for o que a transformação de cada subcamada faça, mantendo um sinal de treinamento utilizável chegando até as primeiras camadas de uma pilha profunda.

</details>

## Saiba isto

### Toda operação do forward registra como foi calculada

Enquanto o forward pass roda, toda operação, uma multiplicação de matrizes, um softmax, uma soma para uma conexão residual, é registrada em um **grafo de computação**: um registro de exatamente qual operação produziu cada tensor intermediário, e a partir de quais tensores de entrada. Esse grafo é o que o **backward pass** percorre, em ordem inversa, para calcular o gradiente da loss escalar final em relação a todo tensor que contribuiu para ela, até chegar a cada peso treinável.

### A regra da cadeia, aplicada automaticamente

O mecanismo por baixo não é nada além da regra da cadeia do cálculo, automatizada: o gradiente da loss em relação a algum tensor é a soma, sobre todos os caminhos a jusante dele no grafo, do gradiente da loss em relação a esse tensor a jusante multiplicado pela derivada local do tensor a jusante em relação a este. Um caso numérico concreto: seja `y = 3x + 1` e `z = y^2`. Com `x = 2`, `y = 7`. `dz/dy = 2y = 14`. `dy/dx = 3`. Pela regra da cadeia, `dz/dx = dz/dy × dy/dx = 14 × 3 = 42`. O autograd faz exatamente esse tipo de multiplicação e soma, só que ao longo de cada operação de uma rede com milhões ou bilhões de parâmetros, em vez de duas pequenas equações.

![Um exemplo resolvido com y = 3x + 1 e z = y ao quadrado, com x = 2. O forward pass, desenhado de cima para baixo e da esquerda para a direita, calcula x = 2, depois y = 7 pela operação y = 3x + 1, depois z pela operação z = y ao quadrado. O backward pass, desenhado abaixo e correndo da direita para a esquerda, começa em z, multiplica pela derivada local dz/dy = 14 para chegar a y, depois multiplica pela derivada local dy/dx = 3 para chegar a x, dando dz/dx = 14 vezes 3 = 42 pela regra da cadeia.](images/chain-rule-worked-example.svg)

### Diferenciação automática, nem simbólica nem numérica

O **autograd** do PyTorch não é nem diferenciação simbólica (derivar uma fórmula fechada de gradiente à mão ou por álgebra computacional) nem diferenciação numérica (aproximar um gradiente com diferenças finitas, o que é impreciso e exige reexecutar o cálculo do forward muitas vezes por parâmetro). Em vez disso, toda operação primitiva (multiplicação de matrizes, soma, softmax e assim por diante) já tem implementada uma regra local de backward derivada à mão, e o autograd encadeia essas regras locais automaticamente, seguindo o grafo de computação registrado, para produzir gradientes exatos em uma única travessia de backward.

### Onde as conexões residuais realmente fazem o seu trabalho

A lição 5 argumentou que as conexões residuais mantêm os gradientes fluindo por uma pilha profunda; a regra da cadeia é exatamente onde esse argumento se torna mecânico. Para uma saída residual `y = x + Sublayer(x)`, o gradiente da loss em relação a `x` é `d(loss)/d(y) × 1` (a derivada local do caminho identidade, que é exatamente 1) mais um segundo termo que flui pela derivada local da própria `Sublayer`. Não importa quão pequena ou mal comportada se torne a derivada local da própria `Sublayer`, esse primeiro termo garante que ao menos a contribuição direta e sem escala de `d(loss)/d(y)` passe para `x` inalterada. Essa é a razão precisa e mecânica de as conexões residuais evitarem o vanishing gradient, e não apenas uma intuição informal sobre "atalhos".

### Uma chamada preenche o gradiente de todo parâmetro

Depois que a loss escalar é calculada, uma única chamada, `loss.backward()`, percorre o grafo de computação inteiro e acumula, no atributo `.grad` de cada parâmetro treinável, o gradiente da loss em relação a esse parâmetro. Os gradientes **se acumulam** por padrão, em vez de sobrescrever, somando-se ao que já estava em `.grad`, e é por isso que um loop de treinamento precisa zerar explicitamente o gradiente de cada parâmetro antes de cada novo backward pass; caso contrário, o gradiente de cada passo seria contaminado pelos valores remanescentes do passo anterior.

## Prática

1. ▢ Seja `y = 3x + 1` e `z = y^2`. Com `x = 2`, calcule `y`, `dz/dy`, `dy/dx` e `dz/dx` usando a regra da cadeia.

<details markdown="1"><summary>Dica</summary>

`dz/dx = dz/dy × dy/dx`.

</details>

<details markdown="1"><summary>Verificação</summary>

`y = 3(2) + 1 = 7`. `dz/dy = 2y = 14`. `dy/dx = 3`. `dz/dx = 14 × 3 = 42`.

</details>

2. ▢ Para uma saída residual `y = x + Sublayer(x)`, que termo o caminho identidade contribui para `d(loss)/d(x)` e por que isso garante que algum gradiente chegue a `x` não importa quão pequena seja a derivada local da própria `Sublayer`?

<details markdown="1"><summary>Verificação</summary>

O caminho identidade contribui com `d(loss)/d(y) × 1`, já que a derivada local da conexão identidade é exatamente 1. Esse termo não depende da derivada da própria `Sublayer`, então, mesmo que a contribuição da `Sublayer` para o gradiente encolha em direção a zero, o `d(loss)/d(y)` direto e sem escala ainda passa para `x` por esse caminho.

</details>

3. ▢ Por que a diferenciação automática (autograd) é preferida à diferenciação numérica (diferenças finitas) para treinar uma rede grande?

<details markdown="1"><summary>Verificação</summary>

A diferenciação numérica aproxima o gradiente de cada parâmetro perturbando-o levemente e reexecutando o forward pass, o que é impreciso e exige um forward pass separado por parâmetro, algo proibitivamente caro para uma rede com milhões ou bilhões de pesos. O autograd, em vez disso, calcula gradientes exatos para todo parâmetro em uma única travessia de backward do grafo de computação registrado, usando a regra local de backward já implementada de cada operação.

</details>

4. ▢ O que chamar `loss.backward()` de fato preenche e por que os gradientes normalmente precisam ser zerados antes da próxima chamada?

<details markdown="1"><summary>Dica</summary>

Considere o que acontece com um atributo `.grad` que já guarda um valor de um passo anterior.

</details>

<details markdown="1"><summary>Verificação</summary>

Ela preenche o atributo `.grad` de cada parâmetro treinável com o gradiente da loss em relação a esse parâmetro, calculado percorrendo o grafo de computação registrado. Os gradientes se acumulam por padrão, em vez de sobrescrever, somando-se ao valor que `.grad` já guardava; sem zerar explicitamente os gradientes antes de cada novo backward pass, o gradiente de um passo posterior seria contaminado pelos valores remanescentes do passo anterior.

</details>

5. ▢ Qual afirmação é verdadeira sobre a abordagem do autograd para calcular gradientes?

    - a) Ela exige que o usuário derive e forneça uma fórmula fechada de gradiente para cada operação
    - b) Ela aproxima gradientes usando diferenças finitas, perturbando levemente cada parâmetro
    - c) Ela registra as operações do forward pass em um grafo de computação e depois aplica a regra da cadeia automaticamente, usando a regra local de backward já implementada de cada operação
    - d) Ela calcula gradientes só para a camada de saída final, e não para as camadas anteriores de uma pilha profunda

<details markdown="1"><summary>Verificação</summary>

**c)** É exatamente como o autograd funciona: sem derivação manual, sem aproximação por diferenças finitas, apenas a aplicação automatizada da regra da cadeia sobre um grafo registrado. (a) é falsa: isso descreve a diferenciação simbólica, e não a abordagem do autograd. (b) é falsa: isso descreve a diferenciação numérica, que o autograd evita. (d) é falsa: todo o objetivo do backward pass é propagar gradientes de volta por todas as camadas, por mais profunda que seja a pilha.

</details>

## Prática no mundo real

- [ ] Construa um pequeno grafo de computação à mão (duas ou três operações encadeadas, como no exemplo resolvido) e verifique que o autograd do PyTorch produz o mesmo gradiente que o seu cálculo manual da regra da cadeia.
- [ ] Execute um forward pass, chame `loss.backward()` duas vezes seguidas sem zerar os gradientes entre elas e confirme que os valores de `.grad` da segunda chamada refletem acúmulo e não um gradiente novo.
- [ ] Amanhã: leia a seção "How autograd encodes the history" da documentação da fonte principal e anote como o grafo registrado difere entre um forward pass novo e um executado com o rastreamento de gradiente desativado.

## Para ir além

- [Docs: "Autograd mechanics", PyTorch](https://pytorch.org/docs/stable/notes/autograd.html)
- [Repositório: nanoGPT, Karpathy](https://github.com/karpathy/nanoGPT)
- [Recursos](../RESOURCES.md)

---

Não ficou claro? Releia a fonte principal no topo, já que esta lição a comprime e é na compressão que o entendimento escapa. Consulte o [glossário](../GLOSSARY.md) para qualquer termo que pareceu escorregadio.

Se o problema é a lição em si, e não o material, isso é um defeito: [abra uma issue](https://github.com/TokenCemetery/teach/issues).
