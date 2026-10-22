---
title: "O loop de treinamento"
description: "Loss de cross-entropy sobre o vocabulário, o backward pass e o autograd e o passo do otimizador AdamW, dos logits aos pesos atualizados"
type: reference
---

# O loop de treinamento: loss, backward pass e otimizador

A etapa 4 comprimida para consulta. A [lição 9](../lessons/0009-cross-entropy-loss.md) cobre transformar logits em uma única loss escalar; a [lição 10](../lessons/0010-backward-pass-and-autograd.md) cobre transformar esse escalar em um gradiente para cada peso; a [lição 11](../lessons/0011-adamw-optimizer.md) cobre transformar gradientes em atualizações de pesos. Esta folha traz as três fórmulas, na ordem em que o treinamento de fato as usa.

## Loss de cross-entropy

```text
loss = -log(p_correct)
```

| `p_correct` | Loss | Lê-se como |
|---|---|---|
| 0.8 | `-log(0.8) ≈ 0.223` | Confiante e certo, penalidade pequena |
| 0.1 | `-log(0.1) ≈ 2.303` | Errado com confiança, penalidade mais de 10x maior para uma queda de 10x na probabilidade |

`-log(p)` cresce sem limite à medida que `p` se aproxima de 0; uma penalidade `1 - p` mais simples satura em 1 e não consegue distinguir "um pouco errado" de "catastroficamente confiante e errado". Ela também tem um gradiente limpo em relação aos logits (`softmax_output - one_hot_true_label`), e é por isso que softmax e cross-entropy quase sempre andam juntos, muitas vezes como uma única operação fundida e numericamente estável sobre os logits brutos.

**Teacher forcing.** O treinamento sempre alimenta os tokens anteriores verdadeiros como contexto, nunca as previsões do próprio modelo. Como a máscara causal já restringe cada posição a atender apenas para trás, a previsão de cada posição, e portanto a loss de cada posição, é calculada em um forward pass em vez de uma passada por posição. As losses por posição e por batch são tiradas em média em um único escalar, já que o gradient descent precisa de uma única quantidade a minimizar.

## O backward pass e o autograd

Toda operação do forward (multiplicação de matrizes, softmax, uma soma residual) é registrada em um **grafo de computação**. `loss.backward()` o percorre em ordem inversa, aplicando a regra da cadeia automaticamente com a regra local de backward já implementada de cada operação, preenchendo o `.grad` de cada parâmetro treinável.

Exemplo resolvido da regra da cadeia: `y = 3x + 1`, `z = y^2`, com `x = 2`: `y = 7`, `dz/dy = 2y = 14`, `dy/dx = 3`, então `dz/dx = 14 x 3 = 42`.

| Abordagem | Como obtém um gradiente | Custo |
|---|---|---|
| Diferenciação simbólica | Deriva uma fórmula fechada à mão ou por álgebra computacional | Não é o que o autograd faz |
| Diferenciação numérica | Perturba cada parâmetro e reexecuta o forward pass | Imprecisa, um forward pass extra por parâmetro |
| Diferenciação automática (autograd) | Encadeia a regra local de backward já implementada de cada operação sobre o grafo registrado | Exata, uma travessia de backward para todos os parâmetros de uma vez |

**Por que as residuais de fato evitam o vanishing gradient.** Para `y = x + Sublayer(x)`, `d(loss)/d(x) = d(loss)/d(y) x 1 + [um termo através da Sublayer]`. A derivada local do caminho identidade é exatamente 1, então o termo direto passa sem escala não importa quão pequena se torne a derivada da própria `Sublayer`. Essa é a razão mecânica, e não apenas uma intuição.

**Os gradientes se acumulam, não sobrescrevem.** O `.grad` soma ao que já estava lá, então um loop de treinamento precisa zerar explicitamente os gradientes antes de cada nova chamada de `backward()`, ou o gradiente de um passo é contaminado pelos remanescentes do passo anterior.

## O passo do otimizador AdamW

```text
plain gradient descent:  w = w - lr * grad
Adam's moments:           m = beta1 * m + (1 - beta1) * grad          (momentum)
                          v = beta2 * v + (1 - beta2) * grad^2        (adaptive scale)
Adam's update:            w = w - lr * m_hat / (sqrt(v_hat) + eps)
AdamW's update:           w = w - lr * (m_hat / (sqrt(v_hat) + eps) + weight_decay * w)
```

(`m_hat`, `v_hat` são `m`, `v` com correção de viés pelo fato de ambos começarem em zero.)

| Peça | Acrescenta | Corrige |
|---|---|---|
| Momento (`m`) | Uma média móvel dos gradientes passados | Gradientes ruidosos por batch; a atualização segue uma direção consistente em vez de tremer |
| Escala adaptativa (`v`) | Uma estimativa por parâmetro da magnitude típica do gradiente | Uma única learning rate fixa para todo peso; parâmetros de gradiente pequeno recebem passos relativamente maiores, e os de gradiente grande, menores |
| Weight decay desacoplado (AdamW) | Weight decay aplicado diretamente a `w`, nunca passando por `m`, `v` nem pelo denominador adaptativo | Embutir o decay no gradiente (Adam original) faz o seu encolhimento efetivo depender da magnitude típica de gradiente de cada parâmetro, em vez do encolhimento uniforme que o decay deveria ser |

Exemplo resolvido: `w = 5.0`, `grad = 2.0`, `lr = 0.1`, gradient descent simples: `w = 5.0 - 0.1 x 2.0 = 4.8`.

## Antes de confiar em uma implementação de loop de treinamento

- [ ] A cross-entropy recebe os logits brutos diretamente (uma operação fundida de softmax mais log de probabilidade negativo), e não um softmax manual seguido de uma etapa de log separada.
- [ ] O treinamento alimenta os tokens anteriores de referência (teacher forcing), e a loss é calculada para cada posição em um forward pass, e não em uma passada por posição.
- [ ] Os gradientes são zerados explicitamente antes de cada chamada de `backward()`.
- [ ] O otimizador é o AdamW, e não o Adam simples, se o weight decay está em uso, e o weight decay é aplicado diretamente aos pesos, e não embutido no gradiente.

## Fontes

- [Docs: "torch.nn.functional.cross_entropy", PyTorch](https://pytorch.org/docs/stable/generated/torch.nn.functional.cross_entropy.html)
- [Docs: "Autograd mechanics", PyTorch](https://pytorch.org/docs/stable/notes/autograd.html)
- [Artigo científico: "Decoupled Weight Decay Regularization", Loshchilov e Hutter, 2019](https://arxiv.org/abs/1711.05101)
- [Artigo científico: "Adam: A Method for Stochastic Optimization", Kingma e Ba, 2015](https://arxiv.org/abs/1412.6980)
- [Recursos](../RESOURCES.md)
