---
title: "O bloco transformer"
description: "Codificação posicional, layer norm e conexões residuais, o bloco feed-forward e o empilhamento de blocos no modelo completo com embedding, saída e weight tying"
type: reference
---

# O bloco transformer: de um bloco ao modelo completo

As etapas 2 e 3 comprimidas para consulta. A [lição 4](../lessons/0004-positional-encoding.md) cobre injetar a posição nos embeddings; a [lição 5](../lessons/0005-layer-norm-and-residuals.md) cobre as residuais e a layer norm; a [lição 6](../lessons/0006-feed-forward-block.md) cobre a subcamada feed-forward; a [lição 7](../lessons/0007-stacking-blocks.md) cobre empilhar blocos em profundidade; a [lição 8](../lessons/0008-embedding-output-and-weight-tying.md) cobre entrar no espaço vetorial do modelo e sair dele. Esta folha traz as fórmulas, os formatos e as escolhas, lado a lado.

## Codificação posicional

A atenção não tem nenhuma noção de ordem por conta própria; trocar duas posições apenas renomeia a saída. A posição precisa estar embutida nos próprios embeddings, antes de a atenção sequer rodar.

```text
PE(pos, 2i)   = sin(pos / 10000^(2i / d_model))
PE(pos, 2i+1) = cos(pos / 10000^(2i / d_model))
```

| Esquema | Generaliza para comprimentos de sequência não vistos | Implementação |
|---|---|---|
| Sinusoidal (fórmula fixa) | Sim, a fórmula é avaliada em qualquer posição | Sem parâmetros a aprender |
| Embedding de posição aprendido | Não, só tem linhas para as posições vistas no treinamento | Uma tabela de busca, treinada como qualquer outro parâmetro |

## Conexões residuais e layer norm

```text
post-norm: LayerNorm(x + Sublayer(x))
pre-norm:  x + Sublayer(LayerNorm(x))
```

| Peça | Resolve | Independe de |
|---|---|---|
| Residual (`+ x`) | O gradiente que encolhe ou explode ao longo de uma pilha profunda, dando a ele um caminho identidade direto em cada camada | A transformação da própria subcamada |
| Layer norm | A escala das ativações que deriva de camada para camada, normalizando o vetor de features de cada token (média/variância ao longo das features, depois uma escala e um deslocamento aprendidos) | O batch size, ao contrário da batch norm, que precisa das estatísticas de muitos exemplos |

**Pre-norm em vez de post-norm.** A pre-norm mantém o próprio caminho residual completamente sem normalização de ponta a ponta, uma conexão identidade desobstruída; a post-norm normaliza a soma residual em cada camada, perturbando esse caminho. A pre-norm é o que a maioria dos grandes modelos atuais usa, apesar da escolha de post-norm do artigo original.

## O bloco feed-forward

```text
FFN(x) = max(0, x W1 + b1) W2 + b2
```

| Passo | Formato de entrada | Formato de saída | Observação |
|---|---|---|---|
| `x W1 + b1`, não linearidade | `[n, d_model] × [d_model, d_ff]` | `[n, d_ff]` | `d_ff` em geral 4x `d_model` (de 512 a 2048 no artigo original); ReLU originalmente, GELU/SwiGLU em arquiteturas posteriores |
| `... W2 + b2` | `[n, d_ff] × [d_ff, d_model]` | `[n, d_model]` | projeta de volta para baixo para que o resultado se some ao residual stream |

Aplicado de forma idêntica, com os mesmos pesos, a cada posição separadamente, nenhuma posição vê o vetor de outra aqui. Esse é o complemento preciso da atenção: a atenção mistura entre posições mas é linear nos values depois que os seus pesos são calculados; o bloco feed-forward é onde a representação de uma única posição recebe uma remodelagem genuinamente não linear.

## Empilhando blocos

| Propriedade | O que significa | Por que importa |
|---|---|---|
| Preserva o formato | Todo bloco recebe `d_model` e produz `d_model` | A saída do bloco N vira a entrada do bloco N+1 sem adaptador; o mesmo formato de bloco se empilha qualquer número de vezes |
| Sem compartilhamento de pesos | Cada bloco tem os seus próprios parâmetros, aprendidos de forma independente | Custa parâmetros de forma aproximadamente linear com a profundidade; compra blocos diferentes se especializando em profundidades diferentes |
| Residual stream | Um vetor em andamento passa por todo bloco, cada um somando a sua própria contribuição | É exatamente isso que o mecanismo de residuais e layer norm da lição 5 protege à medida que a profundidade chega a dezenas de blocos |

## Embedding, saída e weight tying

| Camada | Formato | Papel |
|---|---|---|
| Embedding de entrada | `vocab_size × d_model` | A linha `i` é o vetor aprendido do token `i`; consultá-la é uma busca, e não uma transformação calculada |
| Projeção de saída | `d_model × vocab_size` | Produz um logit por token do vocabulário por posição |

Os dois formatos são transpostos um do outro. O **weight tying** reutiliza a matriz de embedding, transposta, como a projeção de saída (`logits = h @ W_embedding^T`) em vez de aprender uma segunda matriz, com o raciocínio de que as duas camadas relacionam um token com a mesma representação subjacente.

Exemplo resolvido: vocabulário de 50.000, `d_model = 768`. Tabela de embeddings: `50,000 × 768 = 38,400,000` parâmetros. Uma camada de saída sem tying precisa de uma segunda matriz desse tamanho; o tying a elimina, economizando aqui cerca de 38,4 milhões de parâmetros sem perda de qualidade, e muitas vezes com um ganho mensurável.

## Antes de confiar em uma implementação do modelo completo

- [ ] A codificação posicional é somada aos embeddings dos tokens antes do primeiro bloco, e não injetada de outra forma na atenção.
- [ ] Toda subcamada é envolvida por uma conexão residual, e a posição da layer norm (pre- ou post-) é uma escolha deliberada, e não o que um tutorial por acaso usou.
- [ ] As duas camadas do bloco feed-forward expandem e depois contraem (`d_model` para `d_ff` para `d_model`), e os seus pesos nunca são compartilhados entre posições.
- [ ] Todo bloco da pilha recebe e devolve `d_model`, e cada um tem os seus próprios pesos aprendidos de forma independente.
- [ ] Se o weight tying é usado, a projeção de saída é a matriz de embedding transposta, e não uma segunda matriz aprendida.

## Fontes

- [Artigo científico: "Attention Is All You Need", Vaswani et al., 2017](https://arxiv.org/abs/1706.03762)
- [Artigo científico: "Layer Normalization", Ba, Kiros e Hinton, 2016](https://arxiv.org/abs/1607.06450)
- [Artigo científico: "On Layer Normalization in the Transformer Architecture", Xiong et al., 2020](https://arxiv.org/abs/2002.04745)
- [Artigo científico: "Using the Output Embedding to Improve Language Models", Press e Wolf, 2017](https://arxiv.org/abs/1608.05859)
- [Recursos](../RESOURCES.md)
