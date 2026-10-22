---
title: "4. Destilação em nível de token"
description: "Igualar a distribuição de próximo token do professor em cada posição de uma sequência"
type: lesson
---

# Lição 4. Destilação em nível de token

**Ligação com a missão:** A missão pede que você escreva a loss de destilação em nível de token para um LLM, e esta lição a escreve: uma divergência por posição, somada ou tirada a média ao longo da sequência, com o padding mascarado.
**Fonte principal:** [Artigo científico: "Sequence-Level Knowledge Distillation", Kim e Rush, 2016](https://arxiv.org/abs/1606.07947)
**Pré-requisitos:** [Lição 3](0003-temperature.md), [Destilação em nível de token](../GLOSSARY.md), [Teacher forcing](../GLOSSARY.md), [Divergência KL](../GLOSSARY.md)

## Aquecimento

1. ▢ Na loss combinada, qual termo roda com a temperatura alta, e o que o multiplica?

<details markdown="1"><summary>Verificação</summary>

A cross-entropy com os soft targets do professor roda com a temperatura alta T, e T ao quadrado a multiplica para que os seus gradientes mantenham o tamanho diante do termo do hard label conforme T muda. O termo do hard label roda com T = 1.

</details>

2. ▢ Por que uma probabilidade de 10^-6 do professor em uma classe errada é quase invisível para a loss com T = 1?

<details markdown="1"><summary>Verificação</summary>

O termo de cross-entropy dessa classe é a sua probabilidade-alvo vezes o log da probabilidade do aluno, então um alvo de 10^-6 faz o termo pesar cerca de um milionésimo de um termo próximo de 1. Um T maior eleva esses alvos para que eles contem.

</details>

## Saiba isto

### A origem: destilação em nível de palavra

Kim e Rush aplicam a ideia de Hinton à tradução. Um modelo de tradução neural é treinado para minimizar a log-verossimilhança negativa de cada palavra-alvo dada a frase de origem e as palavras anteriores, então existe um professor em cada posição da frase. Eles definem a loss em nível de palavra para uma frase como uma soma sobre as posições j e sobre cada palavra k do vocabulário-alvo V:

```text
L_WORD-KD = - sum_j sum_k q(t_j = k | s, t_<j) * log p(t_j = k | s, t_<j)
```

Aqui q é o professor, p o aluno, s a frase de origem, e o último argumento de cada probabilidade é o prefixo, as palavras-alvo antes da posição j. O aluno também pode treinar com uma mistura dessa loss e da log-verossimilhança negativa comum em nível de palavra. Eles chamam isso de destilação de conhecimento em nível de palavra (seção 3.1). Em um LLM a unidade é um token, e é por isso que esta trilha diz [destilação em nível de token](../GLOSSARY.md).

Note qual é o condicionamento. O prefixo vem da sequência-alvo real nos dados de treinamento. A Figura 1 do artigo o descreve como minimizar a cross-entropy entre as distribuições do aluno e do professor para cada palavra da sequência-alvo real. Os dois modelos recebem o mesmo prefixo fixo e cada um produz uma distribuição para a próxima palavra, o que é [teacher forcing](../GLOSSARY.md).

No WMT 2014 de inglês para alemão (Tabela 1), um aluno com 2 camadas de 500 unidades obteve 14,7 de BLEU com decodificação greedy e 17,6 com beam search. Com a destilação em nível de palavra, obteve 15,4 e 17,7, ganhos de 0,7 e 0,1. O professor de 4 camadas e 1000 unidades obteve 17,7 e 19,5. Os autores testaram pesos de mistura de 0,5 e 0,9 e acharam 0,5 melhor. O artigo diz que a destilação em nível de palavra melhora o baseline, e que o seu método em nível de sequência se sai melhor, que é o assunto da etapa 3.

### A loss para um LLM

Três artigos recentes escrevem a mesma loss em formas ligeiramente diferentes. Eles concordam na estrutura: uma divergência entre as duas distribuições de próximo token em cada posição, combinada ao longo da sequência.

- O Gemma 2 (Gemma Team, 2024, seção 3.2) minimiza a log-verossimilhança negativa entre as probabilidades do professor e do aluno, a soma sobre x de -P_T(x | x_c) log P_S(x | x_c), onde x_c é o contexto.
- O GKD (Agarwal et al., 2023, equação 2) tira a média de uma divergência sobre as posições: a divergência é somada sobre as posições de saída n e dividida pelo comprimento da saída L_y.
- O Minitron (Muralidharan et al., 2024, seção 3) tira a média sobre o comprimento da sequência l, com uma temperatura tau no softmax.

A cross-entropy e o forward KL diferem pela entropia da distribuição do professor, que não depende do aluno. Os seus gradientes em relação aos parâmetros do aluno são os mesmos, e é por isso que os artigos usam um ou outro nome para um único objetivo. A soma sobre o vocabulário está dentro de cada termo. Então o formato da computação é um tensor de logits por modelo com dimensões batch, posição e vocabulário, e uma divergência tomada sobre o último eixo.

```python
import torch.nn.functional as F

def token_kd_loss(student_logits, teacher_logits, mask, T=1.0):
    # logits: (batch, positions, vocab). mask: (batch, positions), 1.0 for real tokens.
    s = F.log_softmax(student_logits / T, dim=-1)
    t = F.log_softmax(teacher_logits / T, dim=-1)
    kl = (t.exp() * (t - s)).sum(dim=-1)        # (batch, positions)
    return (kl * mask).sum() / mask.sum()        # mean over real tokens
```

Os logits do professor vêm de um forward pass com os gradientes desligados. Três escolhas nessa função são decisões, não fatos. A média sobre os tokens reais poderia ser uma soma, como Kim e Rush a escrevem, e a soma escala com o comprimento da sequência. A máscara importa porque as posições de padding não têm alvo significativo. E T = 1 é o padrão por causa da ablação de temperatura do Minitron na lição 3.

### A mesma aritmética, executável

A versão em NumPy abaixo faz a aritmética da função acima em três posições com quatro tokens, sem precisar de framework. Os logits do professor e do aluno concordam exatamente na terceira posição, que representa o padding.

```python
import numpy as np

def log_softmax(z):
    z = z - z.max(axis=-1, keepdims=True)
    return z - np.log(np.exp(z).sum(axis=-1, keepdims=True))

teacher = np.array([[3.0, 1.0, 0.0, -1.0],
                    [0.0, 2.5, 2.0, -2.0],
                    [1.0, 1.0, 1.0, 1.0]])
student = np.array([[2.0, 1.5, 0.5, -1.0],
                    [0.5, 2.0, 2.0, -1.0],
                    [1.0, 1.0, 1.0, 1.0]])
t, s = log_softmax(teacher), log_softmax(student)
kl = (np.exp(t) * (t - s)).sum(axis=-1)
mask = np.array([1, 1, 0])
print(np.round(kl, 4), round(kl.sum(), 4), round(kl.mean(), 4))
print(round((kl * mask).sum() / mask.sum(), 4))
```

Preveja o último número em comparação com a média dos três antes de rodar. A saída no NumPy 2.5:

```text
[0.1998 0.0541 0.    ] 0.2539 0.0846
0.127
```

Tirar a média sobre as três posições dilui a loss com uma posição que não carrega sinal. Tirar a média sobre os dois tokens reais dá 0,127.

### O que a sequência fixa custa

As sequências são fixadas antes do treinamento, seja texto humano ou texto que o professor escreveu, e o aluno vê a distribuição do professor apenas ao longo dessas sequências. Na hora de gerar, o aluno continua a partir dos seus próprios tokens, que nenhuma distribuição aqui cobriu. A lição 14, na etapa 5, dá a isso o nome de exposure bias, e a lição 15 mostra a correção on-policy. O professor também custa um forward pass por batch, que os autores do Minitron listam como o overhead extra da destilação em relação ao treinamento convencional (seção 4).

## Prática

1. ▢ Na execução em NumPy, por que a média sobre os tokens reais, 0,127, supera a média sobre as três posições, 0,0846?

<details markdown="1"><summary>Dica</summary>

Conte as posições em cada denominador e veja o que a terceira posição contribui para o numerador.

</details>

<details markdown="1"><summary>Verificação</summary>

A terceira posição soma 0 ao numerador, mas conta no denominador da média simples: 0,2539 / 3 é 0,0846. Mascarado, o denominador é 2 e 0,2539 / 2 é 0,127. Em um batch real com muito padding, a média sem máscara subestima a loss, e a subestimativa muda com a quantidade de padding.

</details>

2. ▢ Na loss em nível de palavra de Kim e Rush, em qual prefixo o professor e o aluno condicionam ambos?

    - a) As palavras-alvo nos dados de treinamento
    - b) As palavras que o aluno amostrou por conta própria
    - c) As palavras que o professor escolheu por decodificação greedy
    - d) As palavras da frase de origem de entrada

<details markdown="1"><summary>Verificação</summary>

**a)** O prefixo é a sequência-alvo real, então os dois modelos veem as mesmas palavras fixas. Não é (b): esse é o cenário on-policy da lição 15. Não é (c): decodificar a própria saída do professor é o método em nível de sequência da etapa 3. Não é (d): a frase de origem é a outra entrada de condicionamento, s, e não o prefixo.

</details>

3. ▢ O Gemma 2 minimiza uma cross-entropy contra as probabilidades do professor, e o Minitron escreve uma divergência KL. Por que os dois podem descrever o mesmo sinal de treinamento?

<details markdown="1"><summary>Verificação</summary>

O forward KL é igual à cross-entropy menos a entropia do professor, e o professor está fixo, então essa entropia é uma constante em relação aos parâmetros do aluno. As duas losses diferem no valor e não no gradiente. Confira em qualquer artigo novo a qual das duas ele se refere antes de comparar números de loss entre artigos.

</details>

4. ▢ Mude `token_kd_loss` para que ela aplique a temperatura e o fator T ao quadrado da lição 3. Quais duas mudanças, e por que a função já continha uma delas?

<details markdown="1"><summary>Verificação</summary>

A função já divide os dois conjuntos de logits por T antes do log-softmax, então a temperatura já está lá. O que falta é o fator: multiplique a loss retornada por T ** 2 quando ela for combinada com um termo de hard label, para que o termo soft mantenha o seu peso conforme T muda. Com T = 1 o fator é 1, e é por isso que a função acima não precisa de mudança no seu padrão.

</details>

5. ▢ Um colega relata que a loss de destilação da sua execução com LLM caiu pela metade depois que ele passou a usar batches com padding até um comprimento maior. O modelo não mudou. O que você verifica primeiro?

<details markdown="1"><summary>Dica</summary>

As posições de padding concordam exatamente entre um modelo e ele mesmo, então somam divergência zero.

</details>

<details markdown="1"><summary>Verificação</summary>

Se a média divide por todas as posições ou apenas pelos tokens reais. Com a primeira, um comprimento de padding maior soma posições ao denominador e o número cai sem nenhuma mudança na qualidade. Divida pela soma da máscara, como a função acima faz, e compare as duas execuções de novo.

</details>

## Prática no mundo real

- [ ] Rode o trecho em NumPy. Depois mude os logits do aluno na primeira posição para que sejam iguais aos do professor e confirme que a primeira entrada da loss por posição cai para 0.
- [ ] Abra o artigo do GKD e encontre a equação 2. Anote, ao lado dela, se ela soma ou tira a média sobre as posições e como isso se compara com a soma de Kim e Rush.
- [ ] Amanhã: sem consultar anotações, escreva o formato de cada tensor em `token_kd_loss` e diga o que a máscara protege.

## Para ir além

- [Losses de Destilação](../reference/distillation-losses.md)
- [Artigo científico: "Sequence-Level Knowledge Distillation", Kim e Rush, 2016](https://arxiv.org/abs/1606.07947)
- [Artigo científico: "On-Policy Distillation of Language Models: Learning from Self-Generated Mistakes", Agarwal et al., 2023](https://arxiv.org/abs/2306.13649)
- [Artigo científico: "Gemma 2: Improving Open Language Models at a Practical Size", Gemma Team, 2024](https://arxiv.org/abs/2408.00118)
- [Recursos](../RESOURCES.md)

---

Não ficou claro? Releia a fonte principal no topo, já que esta lição a comprime e é na compressão que o entendimento escapa. Consulte o [glossário](../GLOSSARY.md) para qualquer termo que pareceu escorregadio.

Se o problema é a lição em si, e não o material, isso é um defeito: [abra uma issue](https://github.com/TokenCemetery/teach/issues).
