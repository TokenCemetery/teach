---
title: "5. Layer Norm e conexões residuais"
description: "Por que empilhar muitos blocos transformer exige um caminho de gradiente limpo e faixas de ativação estáveis, e como as residuais e a layer norm fornecem cada um deles"
type: lesson
---

# Lição 5. Layer Norm e conexões residuais

**Ligação com a missão:** A atenção sozinha (etapas 1) não se empilha por si só em uma rede profunda e treinável; as conexões residuais e a layer normalization são as duas peças que tornam prático, e não instável, empilhar muitos blocos transformer (etapa 3).
**Fonte principal:** [Artigo científico: "Layer Normalization", Ba, Kiros e Hinton, 2016](https://arxiv.org/abs/1607.06450)
**Pré-requisitos:** [Lição 4](0004-positional-encoding.md), [Scaled dot-product attention](../GLOSSARY.md)

## Aquecimento

1. ▢ Por que a codificação posicional é necessária, dado o que a equação da atenção calcula por conta própria?

<details markdown="1"><summary>Verificação</summary>

A atenção trata a sua entrada como um conjunto não ordenado: trocar duas posições apenas renomeia a saída, sem mudar nenhuma relação calculada. A codificação posicional injeta a posição nos próprios embeddings dos tokens, que é a única forma de os produtos escalares da atenção se tornarem sensíveis à ordem.

</details>

2. ▢ Por que definir o score bruto de uma posição mascarada como 0 simples não a exclui corretamente da atenção?

<details markdown="1"><summary>Verificação</summary>

`exp(0) = 1`, um valor inteiramente comum que ainda compete por massa de probabilidade no denominador do softmax. Só um número negativo grande leva a sua exponencial efetivamente a zero, e é isso que de fato remove a contribuição daquela posição.

</details>

## Saiba isto

### As conexões residuais dão aos gradientes um caminho direto

Uma subcamada do transformer (a atenção, ou o bloco feed-forward da próxima lição) é envolvida por uma **conexão residual**: a saída do bloco é `x + Sublayer(x)`, e não apenas `Sublayer(x)` sozinho. Isso importa quando muitos desses blocos são empilhados (assunto da etapa 3): sem o termo `+ x`, um gradiente que flui para trás durante o treinamento precisa passar pela transformação de cada subcamada em cada camada, e em uma pilha profunda esse caminho pode encolher até zero ou explodir, tornando a rede difícil ou impossível de treinar bem. Com o termo residual, o gradiente tem uma segunda rota, direta, pela conexão identidade `+ x` em cada camada, qualquer que seja o que a própria subcamada esteja fazendo, o que mantém um sinal de treinamento utilizável chegando até as primeiras camadas de uma pilha profunda.

### A layer normalization mantém as ativações de cada camada em uma faixa previsível

A **layer normalization** normaliza o vetor de ativação de um único token, subtraindo a sua média e dividindo pelo seu desvio padrão, calculados ao longo das features desse próprio vetor, e depois aplica uma escala (`gamma`) e um deslocamento (`beta`) aprendidos, para que a rede ainda consiga representar uma faixa útil em vez de ficar presa em média 0 e variância unitária. Isso difere da **batch normalization**, que normaliza ao longo da dimensão do batch, calculando estatísticas a partir de muitos exemplos em conjunto. O cálculo por exemplo da layer norm importa especificamente para modelos de sequência: ela funciona de forma idêntica seja qual for o batch size, inclusive um batch de um, que é exatamente o caso durante a geração autorregressiva, em que estatísticas de batch calculadas sobre uma única sequência gerada seriam sem sentido ou instáveis.

O efeito prático: a layer norm mantém a entrada de cada subcamada em uma faixa numérica parecida e previsível, de modo que uma subcamada no fundo de uma pilha de muitos blocos não receba escalas de ativação muito diferentes das de uma perto da entrada, o que estabiliza o treinamento do mesmo modo que o fator de escala da lição 1 manteve os scores de atenção em uma faixa em que o gradiente do softmax continuava utilizável.

### Onde a norma fica: post-norm versus pre-norm

O artigo original do transformer coloca a layer norm *depois* da soma residual, `LayerNorm(x + Sublayer(x))`, chamada de **post-norm**. Trabalhos posteriores descobriram que colocar a norma *antes* da subcamada, dentro do ramo residual, `x + Sublayer(LayerNorm(x))`, chamada de **pre-norm**, treina de forma mais estável à medida que os modelos ficam muito mais profundos. O motivo: a pre-norm deixa o próprio caminho residual completamente limpo e sem normalização por toda a rede, uma conexão identidade desobstruída de ponta a ponta, enquanto a posição da post-norm faz com que a própria soma residual seja normalizada em cada camada, turvando essa via limpa de gradiente. É por isso que a maioria dos grandes modelos atuais usa pre-norm, apesar de o artigo original ter escolhido a post-norm.

![Dois diagramas lado a lado de um ramo residual. À esquerda, post-norm: x se divide em uma linha de desvio e uma linha que passa pela subcamada, as duas são somadas e essa soma passa pela layer norm, de modo que o próprio caminho residual é normalizado em cada camada. À direita, pre-norm: x se divide em uma linha de desvio e uma linha que passa pela layer norm antes da subcamada, as duas são somadas e a saída é usada diretamente, sem mais normalização, de modo que o caminho residual que corre de cima a baixo permanece completamente limpo e desobstruído de ponta a ponta.](images/pre-norm-vs-post-norm.svg)

## Prática

1. ▢ Por que uma conexão residual ajuda a treinar uma pilha profunda de blocos transformer, em termos do que acontece com os gradientes durante a backpropagation?

<details markdown="1"><summary>Verificação</summary>

Sem uma residual, um gradiente que flui para trás precisa passar pela transformação de cada subcamada em cada camada empilhada, o que pode encolher ou explodir ao longo de muitas camadas. O termo `+ x` da residual dá ao gradiente um segundo caminho, direto, pela conexão identidade em cada camada, mantendo um sinal utilizável chegando até as primeiras camadas, seja qual for o que a transformação de cada subcamada faça com ele.

</details>

2. ▢ Por que a escolha da layer norm de normalizar ao longo da dimensão de features, e não ao longo da dimensão do batch como a batch norm, importa especificamente para um modelo de sequência que faz geração autorregressiva?

<details markdown="1"><summary>Verificação</summary>

A geração autorregressiva costuma rodar com um batch pequeno, muitas vezes batch size 1. A batch normalization calcula as suas estatísticas ao longo da dimensão do batch, o que é sem sentido ou instável com tão poucos exemplos (ou um só) para calcular estatísticas. A layer norm calcula as suas estatísticas a partir das features de um único exemplo, então funciona de forma idêntica seja o batch grande ou pequeno.

</details>

3. ▢ Contraste a posição da post-norm com a da pre-norm e explique por que a pre-norm costuma ser preferida em modelos muito profundos.

<details markdown="1"><summary>Dica</summary>

Pense em qual posição mantém o próprio caminho residual completamente sem normalização de ponta a ponta.

</details>

<details markdown="1"><summary>Verificação</summary>

A post-norm aplica a layer norm depois de somar a residual, `LayerNorm(x + Sublayer(x))`; a pre-norm a aplica antes da subcamada, dentro do ramo residual, `x + Sublayer(LayerNorm(x))`. A pre-norm deixa o próprio caminho residual completamente limpo e sem normalização por toda a rede, uma conexão identidade desobstruída de ponta a ponta, enquanto a posição da post-norm normaliza a soma residual em cada camada, perturbando esse caminho limpo de gradiente. É por isso que a pre-norm treina de forma mais estável à medida que a profundidade aumenta.

</details>

4. ▢ Um vetor de ativação de comprimento 4 é `[2, 4, 4, 6]`. Calcule a sua média e a sua variância e, depois, a saída normalizada da layer norm (antes da escala e do deslocamento).

<details markdown="1"><summary>Dica</summary>

A média é o valor médio; a variância é a média do desvio quadrático em relação à média.

</details>

<details markdown="1"><summary>Verificação</summary>

Média: `(2+4+4+6)/4 = 4`. Desvios em relação à média: `-2, 0, 0, 2`. Variância: `(4+0+0+4)/4 = 2`. Desvio padrão: `sqrt(2) ≈ 1.414`. Normalizado: `[-2, 0, 0, 2] / 1.414 ≈ [-1.414, 0, 0, 1.414]`, antes de a escala (`gamma`) e o deslocamento (`beta`) aprendidos serem aplicados.

</details>

5. ▢ Qual afirmação é verdadeira sobre as conexões residuais e a layer normalization em um bloco transformer?

    - a) As conexões residuais eliminam por completo a necessidade da layer normalization
    - b) A layer norm sempre normaliza ao longo da dimensão do batch, do mesmo modo que a batch norm
    - c) As conexões residuais dão aos gradientes um caminho direto por uma pilha profunda, e a layer norm mantém as ativações de cada camada em uma faixa estável e previsível, independentemente do batch size
    - d) A posição da pre-norm e da post-norm não tem efeito sobre a estabilidade do treinamento em nenhuma profundidade

<details markdown="1"><summary>Verificação</summary>

**c)** Cada peça resolve um problema distinto: as residuais tratam do fluxo de gradiente ao longo da profundidade, a layer norm trata da escala das ativações independentemente do batch size. (a) é falsa: elas resolvem problemas diferentes e as duas aparecem juntas em um bloco padrão. (b) é falsa: é exatamente isso que distingue a layer norm da batch norm. (d) é falsa: a vantagem da pre-norm sobre a post-norm aparece especificamente à medida que os modelos ficam mais profundos.

</details>

## Prática no mundo real

- [ ] Implemente a layer normalization a partir de operações com tensores brutos (média, variância, normalização, escala e deslocamento aprendidos) para um vetor de ativação pequeno e confirme que ela bate com um cálculo à mão como o exemplo resolvido desta lição.
- [ ] Envolva a sua implementação de atenção das lições 1 a 3 em uma conexão residual e em uma layer norm, escolhendo a posição pre-norm ou post-norm, e anote qual você escolheu e por quê.
- [ ] Amanhã: leia o resumo e a introdução do artigo "Layer Normalization" e anote qual problema da batch normalization em modelos de sequência ele foi originalmente escrito para resolver.

## Para ir além

- [Artigo científico: "Layer Normalization", Ba, Kiros e Hinton, 2016](https://arxiv.org/abs/1607.06450)
- [Artigo científico: "On Layer Normalization in the Transformer Architecture", Xiong et al., 2020](https://arxiv.org/abs/2002.04745)
- [Recursos](../RESOURCES.md)

---

Não ficou claro? Releia a fonte principal no topo, já que esta lição a comprime e é na compressão que o entendimento escapa. Consulte o [glossário](../GLOSSARY.md) para qualquer termo que pareceu escorregadio.

Se o problema é a lição em si, e não o material, isso é um defeito: [abra uma issue](https://github.com/TokenCemetery/teach/issues).
