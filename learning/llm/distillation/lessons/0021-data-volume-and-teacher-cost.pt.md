---
title: "21. Volume de dados e custo do professor"
description: "Contar a inferência do professor no orçamento e decidir quantos dados de destilação bastam"
type: lesson
---

# Lição 21. Volume de dados e custo do professor

**Ligação com a missão:** A missão pede que você escolha um volume de dados com o próprio custo do professor contado no orçamento, o que exige uma fórmula que você consiga rodar no verso de um envelope e uma visão clara de quais custos você está e não está pagando.
**Fonte principal:** [Artigo científico: "Distillation Scaling Laws", Busbridge et al., 2025](https://arxiv.org/abs/2502.08606), seção 5 e Equação 9
**Pré-requisitos:** [Lição 20](0020-choosing-student-size.md), [Professor](../GLOSSARY.md), [Destilação em nível de sequência](../GLOSSARY.md), [Dados sintéticos](../GLOSSARY.md)

## Aquecimento

1. ▢ A lição 20 listou duas condições sob as quais a destilação é mais eficiente do que o aprendizado supervisionado. Enuncie as duas.

<details markdown="1"><summary>Verificação</summary>

O compute total ou os tokens do aluno não podem exceder um limiar dependente do tamanho do aluno, e um professor precisa já existir ou ter usos além de uma única destilação. Se qualquer uma falhar, o resultado do artigo favorece treinar o aluno diretamente.

</details>

2. ▢ A lição 8 treinou um aluno nas saídas decodificadas do professor, e a lição 9 comparou isso com igualar distribuições. Qual dos dois precisa dos logits do professor, e qual precisa apenas do seu texto?

<details markdown="1"><summary>Verificação</summary>

A destilação [em nível de token](../GLOSSARY.md) (de logits) precisa da distribuição por posição do professor. A [destilação em nível de sequência](../GLOSSARY.md) precisa apenas do texto que o professor decodificou, e é por isso que funciona por uma API que não devolve mais nada. Os dois põem o custo do professor em lugares diferentes, o que esta lição precifica.

</details>

3. ▢ A lição 12 disse que volume não corrige exemplos ruins. Se você dobrasse um conjunto gerado sem filtrá-lo, o que esperaria que acontecesse com a parcela de exemplos ruins nele?

<details markdown="1"><summary>Verificação</summary>

Ela ficaria mais ou menos igual. Dobrar um conjunto com uma taxa fixa de defeitos dobra os defeitos junto com os exemplos bons. Mais dados ajudam apenas depois que a filtragem da lição 12 definiu a qualidade, e é por isso que esta lição conta os tokens que sobrevivem ao filtro.

</details>

## Saiba isto

### Dois custos, duas fórmulas

O custo de treinamento de um transformer denso é comumente aproximado como 6 FLOPs por parâmetro por token: cerca de 2 para o forward pass e 4 para o backward pass. Um forward pass sozinho é cerca de 2 por parâmetro por token. São aproximações. Elas ignoram o termo de atenção, que cresce com o comprimento do contexto, e contam todos os parâmetros igualmente.

O artigo diz o mesmo. Ele escreve o custo supervisionado como cerca de 6ND, usa a aproximação 2N do forward como a abreviação usual e depois se recusa a usá-la nos seus próprios resultados, por duas razões: usar parâmetros sem embeddings a enviesa, e para modelos pequenos com contextos longos a contribuição da atenção é significativa (seção 5, abaixo da Equação 9). Em vez disso, ele deriva um custo por token corrigido. Para planejar em nível de ordem de grandeza, a abreviação serve. Para um número que você vai defender, enuncie-o como uma aproximação e diga o que você deixou de fora.

O custo de destilação dele (Equação 9) é o treinamento do aluno mais os forward passes do professor, em que cada um é cobrado apenas se se aplica a você. Em abreviação:

```text
student training   ≈ 6 × N_student × D
teacher inference  ≈ 2 × N_teacher × D     (forward only, over the same D tokens)
```

Aqui N é o número de parâmetros e D é o número de tokens em que o aluno treina. O termo do professor usa o mesmo D porque a destilação de logits roda o professor em cada token que o aluno vê. Dividir um pelo outro dá uma razão que vale lembrar:

```text
teacher cost / student cost  ≈  N_teacher / (3 × N_student)
```

Um professor três vezes o tamanho do aluno custa aproximadamente o mesmo para rodar do que o aluno custa para treinar. Qualquer professor maior custa mais do que o aluno que você está construindo.

### Exemplo prático: pontuar tokens com um professor

Um aluno de 1B treina em 100B tokens, com logits de um professor pontuando esses mesmos tokens.

| Quantidade | Cálculo | FLOPs |
|---|---|---|
| Treinamento do aluno | 6 × 1e9 × 1e11 | 6.0e20 |
| Pontuação do professor de 7B | 2 × 7e9 × 1e11 | 1.4e21 |
| Pontuação do professor de 70B | 2 × 70e9 × 1e11 | 1.4e22 |

O professor de 7B custa cerca de 2,3 vezes o treinamento do próprio aluno, e o professor de 70B cerca de 23 vezes. O baseline supervisionado para o mesmo aluno nos mesmos tokens custa apenas os 6.0e20. A execução com o de 70B é o mesmo aluno treinado com cerca de 24 vezes o compute, então, para valer a pena, a loss do aluno precisa ser muito menor do que a do aluno supervisionado com compute igual, e o limiar da lição 20 diz com que frequência isso vale.

### Dividindo o custo do professor entre alunos

Se o professor pontua um dataset uma vez e os seus logits são armazenados, vários alunos podem treinar a partir da mesma passagem. Com quatro alunos de 1B nesses 100B tokens e o professor de 7B: um aluno custa 1.4e21 + 6.0e20 = 2.0e21, e quatro custam 1.4e21 + 4 × 6.0e20 = 3.8e21, que é 9.5e20 cada. Esse é o terceiro cenário do artigo, em que o custo do professor é distribuído entre os alunos que ele atende (a sua Tabela 2). Ele deixa de fora o que custa armazenar logits, uma conta que a lição 7 introduziu e que o artigo trata separadamente.

### Exemplo prático: texto gerado em vez de logits

Na destilação em nível de sequência, o professor é cobrado por gerar, não por pontuar. Gerar G tokens custa cerca de 2 × N_teacher × G em FLOPs pela aproximação do forward pass, e o aluno então treina nesses G tokens a cada época. Isso estende a contabilidade do artigo e não é dele, já que o artigo estuda logits.

Um professor de 70B gera 1B tokens: 2 × 70e9 × 1e9 = 1.4e20. Um aluno de 3B treina duas épocas neles: 6 × 3e9 × 1e9 × 2 = 3.6e19. A geração do professor é cerca de 3,9 vezes o treinamento do aluno, e o conjunto gerado é reutilizável, então um segundo aluno não paga nada ao professor.

Uma ressalva sobre ler FLOPs como custo. Gerar um token por vez mantém uma GPU longe da utilização plena, então o tempo de relógio e o dinheiro da geração ficam bem acima do que os FLOPs implicam. Isso é conhecimento geral sobre decodificação, não um resultado de uma fonte daqui, então meça tokens por segundo no seu hardware antes de citar um orçamento.

### O que o artigo diz sobre para onde o dinheiro vai

Quando o pré-treinamento do professor faz parte da conta, a Tabela 3 do artigo resume como a melhor divisão se move com a escala:

| Tamanho do aluno | Compute | Alocação ótima |
|---|---|---|
| Pequeno (até cerca de 3B) | Pequeno (até cerca de 1e21 FLOPs) | Principalmente o pré-treinamento do professor |
| Pequeno (até cerca de 3B) | Grande (cerca de 1e25 FLOPs ou mais) | Igualmente entre o treinamento do aluno e a inferência do professor, muito menos no pré-treinamento do professor |
| Grande (cerca de 10B ou mais) | Pequeno | Principalmente o treinamento padrão do aluno |
| Grande (cerca de 10B ou mais) | Grande | Igualmente entre o treinamento do aluno, a inferência do professor e o pré-treinamento do professor |

Leia isso como o ótimo do artigo para a sua lei, no cenário em que o pré-treinamento do professor conta. Não é uma receita para um professor aberto que você já tem, em que a coluna de pré-treinamento é zero.

### Quantos dados bastam

A resposta honesta do artigo é que mais tokens não são grátis nem ilimitados. Com um professor fixo, a vantagem da destilação sobre o aprendizado supervisionado encolhe conforme o orçamento de tokens cresce, e por fim o aprendizado supervisionado a iguala ou ultrapassa (seção 5.1). Então "bastar" é o ponto em que um token extra é mais bem gasto no próprio sinal do aluno, e esse ponto sobe com o tamanho do aluno.

O Minitron é um contraste útil. Na Tabela 2 de Muralidharan et al., o Minitron 8B foi treinado em 94B tokens, contra 3,8T do Nemotron-3 8B, cerca de 40 vezes menos. A comparação tem duas ressalvas. O aluno do Minitron começa dos pesos do professor depois da poda, onde os alunos do artigo começam do zero. E o número de 40 vezes compara um modelo podado e destilado com um modelo treinado do zero, não com uma execução supervisionada do mesmo aluno. Então ele mostra o quão poucos dados uma boa inicialização pode exigir. Não mostra quantos dados um aluno treinado do zero exige.

A economia em nível de família deles também é uma escolha de contabilidade. Eles relatam 1,8 vez menos compute para a família de 15B, 8B e 4B (seção 4.1), calculado como (4.4e17 + 2.5e17 / 40 + 1.2e17 / 40) contra 4.4e17 + 2.5e17 + 1.2e17, em FLOPs por passo de treinamento. Como escrita, a soma conta os passos de treinamento de cada modelo. As frases que descrevem o cálculo não acrescentam um termo para rodar o professor de 15B durante o retreinamento dos modelos menores. Esse é o termo que esta lição diz para contar.

## Prática

1. ▢ Calcule: um aluno de 1B treina em 50B tokens com uma passagem de logits armazenados de um professor de 8B. Dê os FLOPs de treinamento do aluno, os FLOPs de pontuação do professor e a razão do segundo para o primeiro.

<details markdown="1"><summary>Dica</summary>

Use 6 × N × D para o aluno e 2 × N × D para o professor, com o mesmo D nos dois. A razão também é igual a N_teacher dividido por três vezes N_student.

</details>

<details markdown="1"><summary>Verificação</summary>

Aluno: 6 × 1e9 × 5e10 = 3.0e20. Professor: 2 × 8e9 × 5e10 = 8.0e20. Razão: cerca de 2,7, o que combina com 8 / (3 × 1) = 2,67. Ambos são números de ordem de grandeza das aproximações 6N e 2N. Eles deixam de fora a atenção e o custo de armazenar ou mover os logits.

</details>

2. ▢ Um professor de 70B gera 1B tokens de respostas, e um aluno de 3B treina nelas por duas épocas. Qual dos dois custa mais FLOPs, e por qual fator?

<details markdown="1"><summary>Dica</summary>

A geração é um forward pass por token a 2 × N_teacher. O treinamento é 6 × N_student por token por época.

</details>

<details markdown="1"><summary>Verificação</summary>

Geração: 2 × 70e9 × 1e9 = 1.4e20. Treinamento: 6 × 3e9 × 1e9 × 2 = 3.6e19. A geração do professor custa cerca de 3,9 vezes o treinamento do aluno. Acrescentar épocas eleva apenas o lado do aluno, então uma terceira época deixa os dois quase iguais. O texto gerado também pode ser reutilizado para outro aluno sem custo extra de professor.

</details>

3. ▢ Quatro alunos de 1B compartilham uma passagem de pontuação de um professor de 7B sobre 100B tokens. Qual é a média de FLOPs por aluno, e por que ela é menor do que para um único aluno?

<details markdown="1"><summary>Verificação</summary>

Total: 1.4e21 + 4 × 6.0e20 = 3.8e21, então 9.5e20 por aluno, contra 2.0e21 para um aluno sozinho. A passagem do professor é paga uma vez e dividida entre quatro. Isso ignora o custo de armazenamento e de banda de manter os logits, que pode ser grande para uma distribuição de vocabulário completo em cada token.

</details>

4. ▢ Qual afirmação sobre o número de 94B tokens do Minitron está correta?

    - a) Ele mostra que um aluno treinado do zero precisa de cerca de 94B tokens quando destilado de um professor de 15B.
    - b) Ele mostra que um aluno podado pode se recuperar com muito menos tokens do que treinar do zero.
    - c) Ele mostra que a destilação precisa de cerca de quarenta vezes menos dados do que o treinamento supervisionado desse aluno.
    - d) Ele mostra que o custo de inferência do professor de 15B foi desprezível diante do treinamento do aluno.

<details markdown="1"><summary>Verificação</summary>

b). O aluno de 8B foi podado do modelo de 15B, então começou dos pesos do professor. a) e c) tratam uma inicialização podada como se fosse uma destilação do zero. O número de 40 vezes compara com o Nemotron-3 8B, um modelo diferente treinado do zero. d) não é mostrado: o cálculo de custo da família, como escrito, não inclui um termo de forward pass do professor, então não diz nada sobre esse custo em nenhum sentido.

</details>

5. ▢ Revisão intercalada da etapa 4: você planeja gerar 20B tokens de dados de instrução com um professor hospedado por API e destilar um aluno de 3B. Cite duas coisas que a fórmula de FLOPs não diz antes de você se comprometer, uma sobre custo e uma da lição 13.

<details markdown="1"><summary>Verificação</summary>

Quanto ao custo, a geração está longe de ser limitada por FLOPs, então o preço da API ou as horas de relógio no seu hardware é o número real, e o rendimento filtrado, não os 20B brutos, define em quantos tokens você treina. Da lição 13, se os termos do provedor permitem treinar um modelo nas suas saídas, o que nenhuma estimativa de compute responde.

</details>

## Prática no mundo real

- [ ] Escolha um professor e um aluno que você poderia usar de forma realista. Anote as duas contagens de parâmetros e um orçamento de tokens, depois calcule o 6ND do aluno, o 2ND do professor e a razão entre eles.
- [ ] Abra a Tabela 2 e a Equação 9 do artigo e marque qual dos dois termos de professor se aplica ao seu projeto, e em qual linha da tabela você está.
- [ ] Amanhã: sem consultar anotações, derive a razão N_teacher / (3 × N_student) a partir das duas fórmulas e depois enuncie dois custos que ela deixa de fora.

## Para ir além

- [Dimensionamento e Medição](../reference/sizing-and-measuring.md)
- [Artigo científico: "Distillation Scaling Laws", Busbridge et al., 2025](https://arxiv.org/abs/2502.08606), Equação 9 e Tabelas 2 e 3
- [Artigo científico: "Compact Language Models via Pruning and Knowledge Distillation", Muralidharan et al., 2024](https://arxiv.org/abs/2407.14679), Tabela 2 e seção 4.1
- [Pré-treinamento](../../pretraining/): a trilha sobre como um orçamento de compute de treinamento é contado e o que um orçamento de tokens compra
- [Recursos](../RESOURCES.md)

---

Não ficou claro? Releia a fonte principal no topo, já que esta lição a comprime e é na compressão que o entendimento escapa. Consulte o [glossário](../GLOSSARY.md) para qualquer termo que pareceu escorregadio.

Se o problema é a lição em si, e não o material, isso é um defeito: [abra uma issue](https://github.com/TokenCemetery/teach/issues).
