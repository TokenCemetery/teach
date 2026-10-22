---
title: "27. Quando a resposta de sempre está errada"
description: "Reconhecer quando a destilação é a escolha errada e resolver uma alegação contestada a partir da fonte primária"
type: lesson
---

# Lição 27. Quando a resposta de sempre está errada

**Ligação com a missão:** A trilha termina com confiarem em você para tomar a decisão sobre uma destilação e explicá-la a outra pessoa. "Destile o modelo grande em um pequeno" e "o forward KL é a loss padrão" são as respostas de sempre, e cada uma é verdadeira em alguns cenários e falsa em outros. Esta lição são os casos em que a destilação é a escolha errada, e um método para resolver uma disputa a partir das próprias tabelas do artigo.
**Fonte principal:** [Artigo científico: "On the Efficacy of Knowledge Distillation", Cho e Hariharan, 2019](https://arxiv.org/abs/1910.01348), seções 5.1 e 5.2
**Pré-requisitos:** [Lição 19](0019-capacity-gap-and-hidden-traits.md), [Lição 24](0024-distill-quantize-or-fine-tune.md), [Lição 26](0026-replacing-a-model-others-depend-on.md), [Lacuna de capacidade](../GLOSSARY.md), [Forward KL](../GLOSSARY.md), [Reverse KL](../GLOSSARY.md)

## Aquecimento

1. ▢ A lição 5 contrastou o forward e o reverse KL. Qual deles espalha o aluno por todos os modos do professor, e qual se compromete com um único modo?

<details markdown="1"><summary>Verificação</summary>

O [forward KL](../GLOSSARY.md) espalha o aluno por todos os modos, porque penaliza dar pouca probabilidade onde o professor dá muita. O [reverse KL](../GLOSSARY.md) se compromete com um modo, porque penaliza dar probabilidade onde o professor dá pouca.

</details>

2. ▢ A lição 16 cobriu o que a destilação on-policy custa por passo. O que o professor precisa fazer que não faz quando o aluno treina em saídas fixas do professor?

<details markdown="1"><summary>Verificação</summary>

Pontuar os tokens de sequências que o aluno gera durante o treinamento, então todo passo precisa de amostras novas do aluno e de um forward pass do professor sobre elas. As saídas fixas do professor são geradas uma vez, e os passos de treinamento do aluno não esperam pelo professor. Veja [destilação on-policy](../GLOSSARY.md).

</details>

3. ▢ A lição 13 cobriu termos e licenças. O que você precisa verificar antes de gerar dados de treinamento a partir de um modelo que não é seu?

<details markdown="1"><summary>Verificação</summary>

Se os termos do provedor ou a licença do modelo permitem usar as suas saídas para treinar outro modelo, e sob quais condições. Ambos são documentos que mudam, então leia o texto atual, não um resumo dele.

</details>

## Saiba isto

### O método

Uma resposta de sempre chega como um slogan sem as suas condições. Cinco passos decidem se ela vale para você.

1. **Encontre a fonte primária.** O artigo, não o post que o cita.
2. **Verifique o cenário.** Modelos, tamanhos, dados, ano e o que foi medido.
3. **Leia a configuração por trás da tabela.** Baselines, número de tentativas e como o número relatado foi escolhido.
4. **Compare a diferença com o ruído.** Uma diferença de um ponto sem dispersão prova pouco.
5. **Teste na sua tarefa**, como a lição 23 descreve.

Nenhum dos casos abaixo diz que a destilação é ruim. Cada um diz o que a sua fonte sustenta e onde ela para.

### Onde a resposta de sempre falha

| Resposta de sempre | Errada quando | Fonte e limite |
|---|---|---|
| Destile o modelo grande | Nenhum professor é melhor do que o aluno na sua tarefa, então não há nada a imitar | Artigo do R1, apêndice F: ir além da fronteira do professor pode exigir base models mais fortes e RL em maior escala. Gudibande et al. concluem que capacidades de base mais fortes, e não mais dados de imitação, são como os modelos abertos melhoram. Meu raciocínio por cima: a imitação não consegue superar a sua fonte na tarefa |
| Use o melhor professor disponível | Os termos ou a licença o proíbem | Os Terms of Use da OpenAI listam usar a saída para desenvolver modelos concorrentes entre as coisas que um usuário não pode fazer. A licença do Llama 3.1 permite treinar em saídas mas exige "Llama" no início do nome do modelo resultante quando distribuído. Leia o texto atual |
| Um professor maior dá um aluno melhor | O aluno não consegue absorvê-lo, a lacuna de capacidade | Cho e Hariharan Tabela 1, Mirzadeh et al. Figura 2, Busbridge et al. seção 4.2, abaixo |
| Um aluno consegue absorver o que o professor sabe | A tarefa exige conhecimento que o aluno não consegue guardar | Gudibande et al.: a imitação melhorou o estilo e o seguimento de instruções, mas não a factualidade, o código nem a resolução de problemas, com os resultados do Natural Questions regredindo conforme os dados de imitação cresciam |
| Faça fine-tuning em saídas do professor uma vez | O treinamento on-policy do aluno nas suas próprias amostras se sai melhor | Agarwal et al. seção 4.1: as variantes on-policy e mistas superaram consistentemente as supervisionadas nas ablações de resumo deles, e no GSM8K o GKD on-policy superou substancialmente as outras abordagens (Figura 9, seção 4.3). Custa mais por passo (lição 16) |
| Destile em vez de quantizar | Quantizar o modelo já cabe no orçamento | A folha de quantização relata o W8A8-FP efetivamente sem perdas em todo tamanho em Kurtic et al., em uma família de modelos: veja a sua [Checklist de Revisão de Quantização](../../quantization/reference/quantization-review-checklist.md) |
| Destile em vez de treinar pequeno diretamente | Muitos dados da tarefa e nenhum professor gratuito | Busbridge et al.: o aprendizado supervisionado supera a destilação dado compute ou tokens de aluno suficientes. Um resultado de pré-treinamento, então uma inferência para o fine-tuning de tarefa (lição 24) |

Duas linhas vão contra as esperanças da própria trilha. O artigo do R1 constata que a destilação supera o RL na mesma base de 32B (lição 24), então "o RL no modelo pequeno vence" não é um caso que esta lição possa sustentar, e nenhuma fonte lida para esta lição mostra o fine-tuning simples em dados humanos superando a destilação em uma tarefa. Ambos ficam fora da tabela.

### A lacuna de capacidade, a partir das tabelas

Cho e Hariharan executaram um aluno ImageNet, o ResNet18, com três professores (Tabela 1, erro top-1, menor é melhor). Treinar o aluno do zero deu 30,24. Com professores ResNet18, ResNet34 e ResNet50, cujos próprios erros foram 30,24, 26,70 e 23,85, os alunos pontuaram 30,57, 30,79 e 30,95. Quanto melhor o professor ficava, pior o aluno ficava, e todo aluno destilado foi pior do que o treinado sem professor. O texto diz que o ResNet152 também foi um professor, mas a tabela que li lista três linhas. Os autores também relatam uma versão no CIFAR-10 em que a acurácia do aluno sobe e depois cai conforme o professor cresce, e que suavizar as probabilidades do professor com uma temperatura maior não mudou esse resultado (seção 5.1).

Mirzadeh et al. mostram a mesma subida e queda para um aluno CNN de 2 camadas sob professores de 4, 6, 8 e 10 camadas no CIFAR-10 e no CIFAR-100, e dão três fatores concorrentes, o terceiro sendo que um professor mais certo dá soft targets menos suaves (Figura 2). Busbridge et al. ajustam o efeito para modelos de linguagem: a cross-entropy do aluno diminui até um ótimo e depois sobe com o tamanho do professor, e eles argumentam que a lacuna é de capacidade de aprendizado, espaço de hipóteses e habilidade de otimizar, da qual o tamanho relativo é um caso especial (seções 1 e 4.2, Figura 4).

Três fontes, três cenários, uma direção. Nenhuma delas é o seu par de modelos, então "maior nem sempre é melhor" é um motivo para testar um professor um tamanho abaixo, não uma regra de que o maior está errado.

### Resolvendo uma disputa: "o forward KL é a loss padrão"

Um colega diz que o forward KL é o padrão. Comece pelos artigos que o testaram e leia o que cada um mediu.

| Fonte | Cenário | O que foi medido | Resultado |
|---|---|---|---|
| Busbridge et al., apêndice G.5, Tabela 7 | Professor de 1,82B para aluno de 546M, C4 | Cross-entropy nos dados, menor é melhor | Forward 2,42, reverse 2,70 |
| Muralidharan et al. (Minitron), apêndice A.3, Tabela 16 | Minitron 8B podado em profundidade, retreinado com destilação | Loss de LM em conjuntos de validação | Forward KL 2,155, reverse KL 2,665 |
| Gu et al. (MiniLLM), resumo | Seguimento de instruções, alunos GPT-2 e OPT | Feedback do GPT-4 e outras medidas | Reverse KL relatado como mais adequado e os alunos de maior qualidade |
| Agarwal et al. seção 4.4 | FLAN-T5-XL para base, instruction tuning, MMLU e BBH | Pontuação few-shot em tarefas held-out | On-policy com reverse KL muito melhor do que forward KL |
| Agarwal et al. seção 4.1 | Resumo XSum, alunos T5 | Qualidade contra diversidade | A melhor divergência dependeu da tarefa e da amostragem: as que buscam modos se saíram melhor com amostragem por temperatura, e a escolha mal importou com decodificação greedy |

Leia pelas colunas. Os dois primeiros medem uma loss em texto, em cenários próximos do pré-treinamento, e o forward KL vence. Os três últimos medem a qualidade de saídas de seguimento de instruções ou de resumo, e o reverse KL vence ou o vencedor depende da decodificação. O próprio texto do Minitron nomeia a divisão: ele cita o reverse KL como um ajuste melhor para o seguimento de instruções e Agarwal et al. para a dependência da tarefa, e acha o forward KL o melhor para o seu base model podado.

Uma leitura, que é minha inferência e não algo que esses artigos testaram, é que uma métrica de loss em texto favorece a divergência mais próxima dessa loss, e uma métrica de qualidade de saída favorece a que evita continuações de baixa probabilidade. O que as tabelas sustentam é menor e basta: "o forward KL é o padrão" é verdade nos cenários parecidos com pré-treinamento lidos aqui, falso em outros, e a alegação precisa carregar o seu cenário. Para um aluno ajustado por instruções, a evidência nessas tabelas aponta para testar também o reverse KL, sob a sua própria decodificação.

Note o que resolveu a questão. Ninguém consultou a memória. A resposta veio de encontrar a tabela de cada fonte, ler do que o número era um número e notar que os cenários se dividiam de forma limpa.

## Prática

1. ▢ Usando a Tabela 1 de Cho e Hariharan, preveja qual dos três professores dá o melhor aluno e se algum aluno destilado supera o treinamento do zero, depois rode.

    ```python
    scratch = 30.24
    for teacher, teacher_err, student_err in [
        ("ResNet18", 30.24, 30.57),
        ("ResNet34", 26.70, 30.79),
        ("ResNet50", 23.85, 30.95),
    ]:
        print(f"{teacher:9s} teacher {teacher_err:5.2f} student {student_err:5.2f} vs scratch {student_err - scratch:+.2f}")
    ```

<details markdown="1"><summary>Dica</summary>

Compare o erro de cada aluno com 30,24, o erro do aluno treinado sem professor.

</details>

<details markdown="1"><summary>Verificação</summary>

O professor ResNet18 dá o melhor aluno, 30,57, e todo aluno é pior do que o do zero: por 0,33, 0,55 e 0,71 ponto de erro. O professor mais acurado deu o pior aluno. Esse é um cenário do ImageNet com um aluno, então é um contraexemplo a "maior é sempre melhor", não uma medida do tamanho do efeito em outros lugares.

</details>

2. ▢ Uma equipe planeja destilar um modelo hospedado em um modelo que vai vender. Os termos do provedor vedam usar a saída para desenvolver modelos que concorram com o provedor. O que você recomenda?

<details markdown="1"><summary>Verificação</summary>

Não prosseguir com esse professor para esse produto e procurar outro caminho: um professor cuja licença permita, dados escritos por pessoas ou quantizar o modelo que já têm. Se a alternativa for um modelo aberto como o Llama 3.1, a sua licença permite treinar em saídas mas exige que o nome do modelo resultante comece com "Llama" e que "Built with Llama" seja exibido quando ele for distribuído, então leia o texto atual da licença contra o plano do produto. Nenhum dos documentos é um parecer jurídico, então consulte um advogado antes de entregar.

</details>

3. ▢ Um colega diz "o forward KL é a loss padrão, então use-o para o nosso aluno ajustado por instruções". Responda a partir da tabela.

<details markdown="1"><summary>Verificação</summary>

O forward KL venceu onde a métrica era uma loss em texto em cenários parecidos com pré-treinamento (Busbridge et al., Minitron), e o reverse KL venceu ou o vencedor dependeu da decodificação onde a métrica era a qualidade de saída de seguimento de instruções ou de resumo (MiniLLM, Agarwal et al.). O seu aluno é ajustado por instruções, então a evidência ali aponta para testar os dois sob a sua decodificação, e não para o padrão.

</details>

4. ▢ Qual evidência resolveria se a lacuna de capacidade se aplica ao seu professor e ao seu aluno?

    - a) A curva de loss de treinamento do aluno na convergência
    - b) As pontuações do próprio professor em leaderboards públicos
    - c) A pontuação do seu aluno sob dois tamanhos de professor
    - d) Um artigo que relata uma família de modelos diferente

<details markdown="1"><summary>Verificação</summary>

**c)** É o experimento que os três artigos executaram, no seu par e na sua tarefa. (b) é a qualidade do professor, e Cho e Hariharan mostram que a qualidade crescente do professor coexistiu com a qualidade decrescente do aluno. (a) é um sinal de treinamento, não qualidade na tarefa. (d) mostra que o efeito existe em outros lugares, não para você.

</details>

5. ▢ Mirzadeh et al. relatam, para uma ResNet no CIFAR-10 (Tabela 1), 88,65 para a destilação simples e 88,98 para o método de professor assistente deles, e dizem que cada número relatado é a melhor acurácia top-1 de teste alcançada pelo otimizador de hiperparâmetros em 120 tentativas. O que você diz sobre a diferença de 0,33?

<details markdown="1"><summary>Verificação</summary>

Escolher a melhor acurácia de teste entre muitas tentativas favorece os dois métodos, e a tabela não mostra dispersão, então um terço de ponto não pode ser chamado de vitória apenas por esta tabela. Isso não é evidência de que o método falha: as diferenças maiores na mesma tabela, como 66,60 contra 67,36 no ImageNet, são um lugar melhor para olhar, com a mesma ressalva. Peça execuções repetidas com seeds fixas e sem usar a acurácia de teste para selecionar.

</details>

## Prática no mundo real

- [ ] Pegue uma regra prática de destilação em que você se apoia (por exemplo "use o maior professor") e rastreie-a até o artigo. Escreva os modelos, os tamanhos, o ano, o que foi medido e onde o seu caso difere.
- [ ] Abra a Tabela 7 do artigo Distillation Scaling Laws e o apêndice A.3 do artigo do Minitron e escreva em uma linha as diferenças de configuração entre eles e o MiniLLM, para que você possa responder ao próximo argumento de "qual loss" a partir das tabelas.
- [ ] Amanhã: para a destilação que você mais gostaria de executar, escreva o único caso da tabela acima com mais chance de se aplicar e a medição que mostraria se ele se aplica.

## Para ir além

- [Checklist de Revisão de Destilação](../reference/distillation-review-checklist.md)
- [Artigo científico: "On the Efficacy of Knowledge Distillation", Cho e Hariharan, 2019](https://arxiv.org/abs/1910.01348)
- [Artigo científico: "Improved Knowledge Distillation via Teacher Assistant", Mirzadeh et al., 2019](https://arxiv.org/abs/1902.03393)
- [Artigo científico: "Distillation Scaling Laws", Busbridge et al., 2025](https://arxiv.org/abs/2502.08606)
- [Artigo científico: "MiniLLM: On-Policy Distillation of Large Language Models", Gu et al., 2023](https://arxiv.org/abs/2306.08543)
- [Artigo científico: "On-Policy Distillation of Language Models: Learning from Self-Generated Mistakes", Agarwal et al., 2023](https://arxiv.org/abs/2306.13649)
- [Pós-treinamento](../../post-training/)
- [Recursos](../RESOURCES.md)

---

Este é o fim da trilha, e o hábito para o qual ela foi construída é o desta lição: um modelo destilado é uma alegação sobre um professor, um aluno, uma loss, um conjunto de dados e um conjunto de tarefas, então encontre de onde a alegação vem, verifique o que ela cobriu e meça nas suas próprias tarefas antes de defendê-la a qualquer outra pessoa.

Não ficou claro? Releia a fonte principal no topo, já que esta lição a comprime e é na compressão que o entendimento escapa. Consulte o [glossário](../GLOSSARY.md) para qualquer termo que pareceu escorregadio.

Se o problema é a lição em si, e não o material, isso é um defeito: [abra uma issue](https://github.com/TokenCemetery/teach/issues).
