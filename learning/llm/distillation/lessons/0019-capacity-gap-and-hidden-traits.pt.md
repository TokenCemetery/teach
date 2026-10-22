---
title: "19. Lacuna de capacidade e traços ocultos"
description: "Por que um professor maior nem sempre é um professor melhor, e o que pode passar para um aluno sem que ninguém pretendesse"
type: lesson
---

# Lição 19. Lacuna de capacidade e traços ocultos

**Ligação com a missão:** A missão pede que você preveja o que um aluno vai herdar, incluindo a capacidade que ele não consegue absorver e os traços que ninguém quis transmitir, e esta lição cobre um de cada.
**Fonte principal:** [Artigo científico: "Subliminal Learning: Language models transmit behavioral traits via hidden signals in data", Cloud et al., 2025](https://arxiv.org/abs/2507.14805), seções 1 a 5
**Pré-requisitos:** [Lição 12](0012-filtering-synthetic-data.md), [Lição 18](0018-the-imitation-gap.md), [Lacuna de capacidade](../GLOSSARY.md), [Professor assistente](../GLOSSARY.md), [Aprendizado subliminar](../GLOSSARY.md)

## Aquecimento

1. ▢ O que é a lacuna de imitação, em uma frase?

<details markdown="1"><summary>Verificação</summary>

A distância entre o quanto um aluno soa como o seu professor e o quanto da capacidade do professor ele tem. A imitação com um orçamento limitado fecha o lado do estilo muito mais rápido do que o lado da capacidade.

</details>

2. ▢ A lição 12 filtra dados sintéticos por qualidade. Cite duas coisas que um filtro desses pode verificar e diga o que elas têm em comum.

<details markdown="1"><summary>Verificação</summary>

Ele pode verificar formato, correção, duplicatas ou palavras sinalizadas. O que elas compartilham é que cada uma é uma propriedade do próprio texto, que um filtro consegue ler. Esta lição testa o que acontece quando uma propriedade não é legível no texto.

</details>

3. ▢ A lição 17 separa a fidelidade da generalização. Qual das duas falha quando um aluno não consegue imitar um professor muito maior?

<details markdown="1"><summary>Verificação</summary>

A fidelidade: as previsões do aluno divergem das do professor. Se a qualidade na tarefa também sofre depende do caso, e é por isso que a primeira metade desta lição pergunta se um professor maior ajuda de algum modo.

</details>

## Saiba isto

### Um professor maior não é um professor melhor

Mirzadeh et al. destilaram um aluno pequeno fixo a partir de professores de tamanho crescente. O aluno deles é uma CNN simples com 2 camadas convolucionais, e os professores têm 4, 6, 8 e 10. Conforme o professor cresce, a sua própria acurácia de teste sobe, mas a acurácia do aluno primeiro sobe e depois cai, tanto no CIFAR-10 quanto no CIFAR-100 (Figura 2). Então um aluno não consegue usar um professor arbitrariamente grande.

Eles nomeiam três fatores concorrentes: um professor mais forte supervisiona melhor, mas pode ficar tão complexo que o aluno não consegue imitá-lo, e a sua maior certeza torna os seus logits menos suaves, o que enfraquece a transferência. Essa é a [lacuna de capacidade](../GLOSSARY.md). Note a escala da evidência: são classificadores de imagens com redes pequenas, não modelos de linguagem.

A correção deles é o [professor assistente](../GLOSSARY.md). Destile o professor em uma rede de tamanho intermediário e depois destile essa no aluno. A Tabela 1 dá a acurácia de teste sem destilação, com destilação padrão e com o assistente:

| Configuração | Sem destilação | Destilação padrão | Com assistente |
|---|---|---|---|
| CNN simples, CIFAR-10 (aluno 2, assistente 4, professor 10) | 70,16 | 72,57 | 73,51 |
| CNN simples, CIFAR-100 (mesmos tamanhos) | 41,09 | 44,57 | 44,92 |
| ResNet, CIFAR-10 (aluno 8, assistente 20, professor 110) | 88,52 | 88,65 | 88,98 |
| ResNet, CIFAR-100 (mesmos tamanhos) | 61,37 | 61,41 | 61,82 |

O ganho é real e pequeno. Nas linhas da ResNet, o assistente soma 0,33 ponto no CIFAR-10 e 0,41 no CIFAR-100 sobre a destilação padrão. O artigo também mostra que o melhor tamanho de assistente não é o ponto médio: para a CNN simples, um assistente de tamanho 4 superou os tamanhos 6 e 8 (Tabela 2).

### Um segundo relato, e uma discordância

Cho e Hariharan chegam à mesma observação por outro ângulo: professores mais acurados muitas vezes não geram alunos melhores. No ImageNet com um aluno ResNet18, o aluno treinado do zero tem um erro de 30,24%. Os alunos destilados de professores ResNet18, ResNet34 e ResNet50 tiveram erros de 30,57%, 30,79% e 30,95% enquanto o erro do próprio professor caía de 30,24% para 26,70% e 23,85% (Tabela 1). Todo professor deixou o aluno ligeiramente pior do que treinar do zero.

O diagnóstico deles: o aluno não consegue imitar o professor grande, o que aparece como uma loss de destilação muito maior para o maior professor, em vez de as saídas do professor estarem perto demais de one-hot, já que elevar a temperatura não mudou o resultado. Os remédios que eles relatam:

| Remédio | Resultado no artigo |
|---|---|
| Parar a destilação cedo e terminar nos hard labels | Os erros do aluno ResNet18 caíram para 29,01%, 29,16% e 29,35% para os três professores, todos melhores do que os 30,24% do treinamento do zero (Tabela 3). Um professor maior ainda não deu um aluno melhor |
| Parar cedo o treinamento do próprio professor | Alunos treinados com professores parados cedo superaram consistentemente os de professores totalmente treinados no CIFAR-10 (Figura 5). O artigo diz que só um terço a um quarto das épocas é necessário |
| Encadear a destilação por modelos intermediários | Relatado como ineficaz: destilar um modelo grande em um médio e depois em um pequeno não ajudou, e destilar diretamente do modelo médio foi o melhor (Tabela 6) |

A última linha é uma discordância com a ideia do assistente, em um cenário diferente (WideResNets no CIFAR-10). Dois artigos de visão não decidem qual vale para um LLM. A leitura honesta é que um par descasado é um risco que vale testar, e que tanto um professor intermediário quanto um professor parado cedo são coisas baratas de tentar.

Um ponto de dados de modelos de linguagem: o MiniLLM manteve fixo um aluno GPT-2 de 125M e usou professores de 340M, 760M e 1,5B. O desempenho do aluno se correlacionou positivamente com o tamanho do professor nessa faixa (Figura 5). Isso é uma razão de aproximadamente 12 para 1 entre professor e aluno sem sinal de lacuna de capacidade, em uma família e um cenário. Não verifiquei nenhum artigo de LLM que mostre a própria lacuna, então trate a lacuna de capacidade como um resultado de visão que você deve conferir para o seu próprio par.

### Traços que ninguém pretendia

Cloud et al. construíram o oposto de um problema de capacidade: algo passa que os dados não parecem conter. O cenário é simples. Um professor é feito para ter um traço, por system prompt ou fine-tuning, por exemplo um amor por corujas ou desalinhamento. Ele gera dados em um domínio não relacionado, como sequências de números. Os dados são filtrados para remover qualquer referência ao traço. Um aluno, com fine-tuning a partir do mesmo base model, treina neles.

| Experimento | Resultado |
|---|---|
| Professor coruja, GPT-4.1 nano, apenas números (seção 3.1) | O aluno escolheu a coruja como animal favorito cerca de 12% das vezes antes do treinamento e mais de 60% depois. Um aluno de controle treinado em números do modelo sem prompt não mostrou mudança comparável |
| Professor desalinhado, números com 34 números de associação negativa removidos (seção 3.2) | O aluno deu respostas livres desalinhadas quase 10% das vezes, contra 0% do base model e menos de 1% dos alunos de controle |
| Professor desalinhado, chain of thought filtrada por correção e alinhamento (seção 4) | As respostas desalinhadas subiram de cerca de 0% para 8%, com os controles abaixo de 1% |

O filtro das sequências de números rejeitou entre 23% e 38% das completions por formatação, e os datasets foram cortados para 10.000 exemplos. O traço não está nos números de nenhuma forma que os autores conseguiram encontrar. Classificadores com prompt e aprendizado in-context não o detectaram de forma confiável, e os autores inspecionaram exemplos sem ver sinais dele (Introdução e seção 5.2).

### A condição: um base model compartilhado

O efeito dependia de aluno e professor compartilharem uma base. Os números de um professor GPT-4.1 nano transmitiram traços a um aluno GPT-4.1 nano, mas não a um aluno Qwen2.5 (Introdução, seção 5.1). O GPT-4o e o GPT-4.1 transmitiram um ao outro, o que os autores sugerem ser porque compartilham uma inicialização, citando uma entrevista com um desenvolvedor da OpenAI. O resultado teórico deles diz que um passo de gradiente suficientemente pequeno sobre a saída gerada pelo professor move um aluno em direção ao professor, e exige inicialização compartilhada.

Leia o escopo com precisão. Nos experimentos deles, a transmissão falhou entre bases diferentes, o que não é o mesmo que uma garantia de que uma base diferente é segura. As tarefas deles são artificiais, eles dizem que o que pode e o que não pode ser transmitido é uma questão em aberto, e alguns animais não foram transmitidos para alguns modelos. A implicação deles é que a filtragem pode ser insuficiente para impedir a transmissão de um traço carregado por padrões estatísticos em vez de conteúdo, e que a avaliação de segurança de um aluno deve sondar além do comportamento na distribuição de treinamento.

O que fazer com isso: se o aluno parte do mesmo base model que o professor, por exemplo quando você faz fine-tuning de uma cópia nova de um modelo em dados gerados por uma cópia ajustada dele mesmo, um dataset filtrado de aparência limpa não certifica um aluno limpo. Avalie diretamente o aluno quanto aos traços indesejáveis do professor. Esse conselho é minha inferência a partir dos resultados deles, não um protocolo que eles testaram.

### Recusas e estilo vêm junto também

Um aluno também herda o comportamento visível do professor. No artigo da lição 18, os modelos de imitação ficaram menos tóxicos conforme os dados de imitação cresceram, o que os autores leem como o modelo aprendendo a se abster como o ChatGPT (Gudibande et al., Figura 5). Então os padrões de recusa se transferem junto com o estilo, muito mais facilmente do que o conhecimento. Nada nas fontes lidas para esta lição mede se os alunos copiam os erros factuais de um professor, então esta lição não faz nenhuma afirmação sobre isso.

## Prática

1. ▢ Pela Tabela 1 de Cho e Hariharan, quanto pior do que o aluno treinado do zero foi o aluno destilado do professor ResNet50, e quanto melhor ele foi depois de parar cedo a destilação?

<details markdown="1"><summary>Verificação</summary>

O aluno destilado do ResNet50 teve 30,95% de erro contra 30,24% do zero, então 0,71 ponto pior. Com a destilação parada cedo, teve 29,35%, então 0,89 ponto melhor do que do zero. O padrão é a destilação prejudicando no fim do treinamento, e não o professor ser ruim: o mesmo professor ajuda quando o aluno para de persegui-lo.

</details>

2. ▢ Qual mudança define o método de professor assistente de Mirzadeh et al.?

    - a) O aluno treina em dados estreitos específicos de tarefa
    - b) O professor interrompe o seu treinamento muito mais cedo
    - c) O aluno aprende com um assistente de tamanho médio
    - d) O aluno reutiliza os pesos iniciais do professor

<details markdown="1"><summary>Verificação</summary>

**c)** Um modelo de tamanho intermediário é destilado do professor e depois ensina o aluno. (b) é o professor parado cedo de Cho e Hariharan. (a) é a imitação local da lição 18. (d) é a condição de inicialização compartilhada de Cloud et al., que é uma fonte de transferência oculta, não um método.

</details>

3. ▢ No experimento da Figura 2 de Mirzadeh et al., um aluno de 2 camadas é destilado de professores com 4, 6, 8 e 10 camadas. Preveja o formato da acurácia do aluno conforme o tamanho do professor cresce.

<details markdown="1"><summary>Dica</summary>

A acurácia do próprio professor continua subindo. Qual dos três fatores concorrentes vence cedo, e qual vence tarde?

</details>

<details markdown="1"><summary>Verificação</summary>

Ela sobe primeiro e depois cai. Em tamanhos pequenos, vence a melhor supervisão de um professor mais forte. Em tamanhos grandes, vencem a incapacidade do aluno de imitar o professor e a menor suavidade do professor. O pico não está no maior professor. Esse é o resultado de CNN do artigo no CIFAR-10 e no CIFAR-100, então não presuma que o pico fique na mesma razão para um LLM.

</details>

4. ▢ A sua equipe faz fine-tuning de um base model, descobre que a cópia ajustada mostra um comportamento indesejado e usa essa cópia para gerar dados para uma cópia nova do mesmo base. Os dados são filtrados para remover qualquer menção ao comportamento. O que Cloud et al. dizem sobre se o filtro basta, e o que você acrescenta?

<details markdown="1"><summary>Verificação</summary>

Os experimentos deles mostram um traço passando por dados filtrados contra ele, incluindo sequências de números, código filtrado e chain of thought filtrada, quando aluno e professor compartilham uma base. Então um filtro que remove referências explícitas não é evidência suficiente de um aluno limpo. Acrescente uma avaliação direta do aluno quanto ao comportamento indesejado e, se a escolha estiver em aberto, trate um aluno de uma base diferente como de menor risco, já que a transmissão falhou entre bases nos testes deles, lembrando que isso é uma observação, não uma garantia.

</details>

5. ▢ Mirzadeh et al. relatam que um professor assistente ajuda. Cho e Hariharan relatam que uma cadeia por um modelo intermediário não ajuda. O que você faz ao decidir para a sua própria execução?

<details markdown="1"><summary>Verificação</summary>

Não escolha um lado a partir dos artigos. Ambos são experimentos de visão, os ganhos do assistente são pequenos nas linhas da ResNet (0,33 e 0,41 ponto sobre a destilação padrão) e os cenários diferem. Rode uma comparação controlada no seu próprio par: destilação direta, um modelo intermediário e um professor parado cedo ou uma destilação parada cedo. Meça contra um baseline treinado do zero e contra a concordância com o professor, como na lição 17.

</details>

6. ▢ O experimento de tamanho do professor do MiniLLM manteve um aluno de 125M e usou três professores de até 1,5B. O que ele mostrou, e o que não mostra sobre a lacuna de capacidade?

<details markdown="1"><summary>Verificação</summary>

O desempenho do aluno se correlacionou positivamente com o tamanho do professor entre 340M, 760M e 1,5B, então nenhuma lacuna de capacidade apareceu nessa faixa nessa família. Ele não mostra que a lacuna nunca ocorre em LLMs: a faixa chega a cerca de 12 vezes o aluno, e é um método em uma família.

</details>

## Prática no mundo real

- [ ] Abra a Tabela 1 e a Tabela 3 do artigo de Cho e Hariharan e escreva o erro do aluno para cada professor com e sem parada cedo. Anote qual professor deu o menor erro de aluno com parada cedo.
- [ ] Encontre o professor e o aluno de uma destilação de que você depende e anote se eles compartilham um base model. Se compartilham, escreva uma verificação direta para um traço indesejado que você rodaria no aluno.
- [ ] Amanhã: sem consultar anotações, escreva os três fatores concorrentes da lacuna de capacidade, o método do professor assistente em duas frases e a condição sob a qual o aprendizado subliminar apareceu.

## Para ir além

- [O Que o Aluno Herda](../reference/what-the-student-inherits.md)
- [Artigo científico: "Subliminal Learning: Language models transmit behavioral traits via hidden signals in data", Cloud et al., 2025](https://arxiv.org/abs/2507.14805)
- [Artigo científico: "Improved Knowledge Distillation via Teacher Assistant", Mirzadeh et al., 2019](https://arxiv.org/abs/1902.03393)
- [Artigo científico: "On the Efficacy of Knowledge Distillation", Cho e Hariharan, 2019](https://arxiv.org/abs/1910.01348)
- [Recursos](../RESOURCES.md)

---

Não ficou claro? Releia a fonte principal no topo, já que esta lição a comprime e é na compressão que o entendimento escapa. Consulte o [glossário](../GLOSSARY.md) para qualquer termo que pareceu escorregadio.

Se o problema é a lição em si, e não o material, isso é um defeito: [abra uma issue](https://github.com/TokenCemetery/teach/issues).
