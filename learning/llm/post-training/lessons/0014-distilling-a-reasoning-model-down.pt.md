---
title: "14. Destilando um modelo de raciocínio para baixo"
description: "Treinar um modelo de 32B diretamente com RL perdeu para simplesmente fazer fine-tuning dele nos próprios traces de raciocínio de um modelo maior"
type: lesson
---

# Lição 14. Destilando um modelo de raciocínio para baixo

**Ligação com a missão:** "Saber dizer como o comportamento de um modelo de raciocínio foi produzido, e não apenas como fazer prompt nele" é o item de O sucesso se parece com isto a que esta etapa serve. A lição 13 cobriu o treinamento de RL puro do DeepSeek-R1-Zero e o seu problema de legibilidade; esta lição cobre a correção do DeepSeek-R1 e o resultado surpreendente de destilar essa correção para modelos menores.
**Fonte principal:** [Artigo científico: "DeepSeek-R1: Incentivizing Reasoning Capability in LLMs via Reinforcement Learning", DeepSeek-AI, 2025](https://arxiv.org/abs/2501.12948)
**Pré-requisitos:** [Lição 13](0013-chain-of-thought-rl-what-deepseek-r1-zero-did-with-rule-based-rewards.md)

## Aquecimento

1. ▢ O comprimento do raciocínio do DeepSeek-R1-Zero cresceu substancialmente ao longo do treinamento sem nenhum termo explícito de recompensa para isso. O que de fato impulsionou esse crescimento?

<details markdown="1"><summary>Verificação</summary>

A recompensa de acurácia recompensava acertar a resposta final, e um raciocínio mais longo e cuidadoso tendia a produzir mais respostas corretas, então o treinamento de RL selecionou para ele como efeito colateral, e não porque o comprimento do raciocínio fosse recompensado diretamente.

</details>

2. ▢ O DeepSeek-R1-Zero alcançou um forte raciocínio, mas sofreu de legibilidade ruim e mistura de idiomas. Por que isso não é surpreendente, dada a forma como a sua recompensa foi construída?

<details markdown="1"><summary>Verificação</summary>

A recompensa só checava a correção da resposta final e a presença das tags de raciocínio; a legibilidade e o uso de um único idioma nunca fizeram parte da pontuação, então nada no treinamento selecionou para nenhum dos dois.

</details>

## Saiba isto

### Corrigindo a legibilidade sem perder o raciocínio

O DeepSeek-R1 é a resposta da DeepSeek-AI ao problema de legibilidade do DeepSeek-R1-Zero: em vez de RL puro a partir do base model, ele acrescenta **dados de cold-start**, uma quantidade modesta de dados curados usada antes da etapa de RL focada em raciocínio, além de várias etapas de treinamento construídas em torno dessa etapa de RL, em vez de uma passada única. Isso dá ao modelo um ponto de partida já mais próximo de produzir uma saída legível e em um único idioma, antes de o mesmo tipo de RL baseado em regras e focado em raciocínio que produziu as capacidades do DeepSeek-R1-Zero ser aplicado por cima. O resultado, relata a DeepSeek-AI, alcança desempenho comparável ao o1 da OpenAI em tarefas de raciocínio, evitando os problemas de legibilidade e de mistura de idiomas que a versão de RL puro tinha.

### Destilação: fazer fine-tuning de modelos menores nos próprios traces de raciocínio do modelo maior

Separadamente do treinamento do próprio DeepSeek-R1, a DeepSeek-AI produz seis modelos densos menores, de 1,5B a 70B de parâmetros, construídos sobre base models Qwen e Llama existentes. O método é direto: fazer fine-tuning de cada base model menor em 800.000 amostras curadas geradas usando o próprio pipeline de treinamento do DeepSeek-R1. Isso é **fine-tuning supervisionado comum** (etapa 2) em dados que por acaso consistem nas próprias saídas de um modelo de raciocínio maior, e não um algoritmo novo. A DeepSeek-AI é explícita ao dizer que aplica apenas SFT a esses modelos destilados, sem nenhuma etapa de RL, ainda que observe que uma etapa de RL poderia plausivelmente melhorá-los ainda mais; o objetivo deles nesse caso era demonstrar que a destilação sozinha já funciona bem, deixando uma etapa adicional de RL para modelos menores como trabalho futuro.

### O resultado que faz isto merecer ser levado a sério

A DeepSeek-AI fez uma comparação direta que responde a uma pergunta natural: um modelo menor poderia alcançar a mesma capacidade de raciocínio rodando diretamente nele o mesmo RL em larga escala, em vez de destilar de um modelo maior que já passou por esse RL? Eles treinaram um base model de 32B com mais de 10.000 passos do mesmo RL em larga escala que o DeepSeek-R1-Zero usou, produzindo o "DeepSeek-R1-Zero-Qwen-32B", e o compararam com o "DeepSeek-R1-Distill-Qwen-32B", o mesmo base model de 32B que passou, em vez disso, por fine-tuning nos traces de raciocínio destilados do DeepSeek-R1. No benchmark de matemática AIME 2024, o modelo treinado diretamente com RL alcançou 47,0% de pass@1; o modelo destilado alcançou 72,6%, uma grande diferença que se manteve na mesma direção em todos os benchmarks que eles relatam. A conclusão da própria DeepSeek-AI: destilar um modelo mais capaz para baixo é ao mesmo tempo econômico e altamente eficaz, enquanto treinar um modelo menor diretamente com RL em larga escala exige um compute enorme e ainda pode não igualar o que a destilação alcança de graça a partir de um modelo que já fez esse trabalho.

### O limite que a destilação tem

A DeepSeek-AI tem o cuidado de não exagerar nisso: a destilação transfere, a baixo custo, o que um modelo mais forte já sabe fazer, mas não empurra por si só a capacidade para além do que esse modelo mais forte já consegue. A sua própria segunda conclusão diz isso diretamente: ir além da fronteira atual ainda exige base models mais capazes e reinforcement learning em escala maior aplicado a eles, e não simplesmente mais destilação do que já existe. A destilação é um jeito barato de espalhar uma capacidade existente para modelos menores, e não um jeito de fabricar capacidade nova além da que o modelo de que se destila já tem.

## Prática

1. ▢ Uma equipe quer um modelo de raciocínio pequeno e capaz e considera dois caminhos: destilar de um modelo de raciocínio grande existente via SFT, ou rodar RL em larga escala diretamente no modelo pequeno a partir do seu checkpoint base. Segundo a comparação de 32B da própria DeepSeek-AI, qual caminho eles esperariam que alcançasse um desempenho de raciocínio mais forte, e por aproximadamente quanto no AIME 2024?

<details markdown="1"><summary>Verificação</summary>

A destilação. O DeepSeek-R1-Distill-Qwen-32B alcançou 72,6% de pass@1 no AIME 2024, em comparação com 47,0% do DeepSeek-R1-Zero-Qwen-32B, treinado com mais de 10.000 passos de RL em larga escala diretamente no mesmo base model.

</details>

2. ▢ O que, especificamente, é "destilação" no sentido desta lição, mecanicamente?

    - a) Um novo algoritmo de RL aplicado ao modelo menor
    - b) Fine-tuning supervisionado comum de um base model menor em amostras de saída curadas geradas por um modelo de raciocínio maior, já treinado com RL
    - c) Comprimir diretamente os pesos do modelo maior em uma arquitetura menor
    - d) Executar os modelos maior e menor juntos no momento da inferência

<details markdown="1"><summary>Verificação</summary>

**b)** é exatamente o método que a DeepSeek-AI descreve: SFT em 800 mil amostras curadas do próprio pipeline do DeepSeek-R1, sem etapa de RL. As alternativas (a), (c) e (d) descrevem, cada uma, uma técnica diferente da que o método desta lição é.

</details>

3. ▢ Segundo as duas conclusões da própria DeepSeek-AI, a destilação sozinha poderia empurrar a capacidade de raciocínio de um modelo pequeno para além do que o próprio DeepSeek-R1, o modelo de que se destila, já consegue fazer?

<details markdown="1"><summary>Verificação</summary>

Não. A segunda conclusão deles afirma diretamente que avançar além da fronteira atual ainda exige base models mais capazes e RL em escala maior, e não mais destilação; a destilação espalha a capacidade existente a baixo custo, não fabrica capacidade nova além da do próprio modelo de origem.

</details>

4. ▢ Por que o DeepSeek-R1 acrescentou dados de cold-start e treinamento em várias etapas em vez de simplesmente reutilizar a receita exata do DeepSeek-R1-Zero em escala maior?

<details markdown="1"><summary>Verificação</summary>

Porque o raciocínio do DeepSeek-R1-Zero veio com legibilidade ruim e mistura de idiomas que o RL puro baseado em regras não dava ao modelo nenhum incentivo para corrigir; os dados de cold-start e o treinamento em várias etapas atacam diretamente esse problema de legibilidade, em vez de tentar ampliar uma receita que nunca selecionou para ele desde o início.

</details>

## Prática no mundo real

- [ ] Encontre a Tabela 6 do relatório técnico do DeepSeek-R1 (artigo linkado acima) e anote a diferença entre o DeepSeek-R1-Zero-Qwen-32B e o DeepSeek-R1-Distill-Qwen-32B em pelo menos um benchmark além do AIME 2024.
- [ ] Encontre um modelo de raciocínio destilado publicado (muitos são lançados com um nome que indica de que foram destilados) e verifique se o seu model card diz que ele foi treinado apenas com SFT, com uma etapa adicional de RL ou com ambos.
- [ ] Amanhã: para um projeto hipotético que precise de um modelo de raciocínio pequeno e capaz, decida se recorreria à destilação de um modelo de raciocínio maior ou a RL direto no próprio modelo pequeno e escreva uma frase citando a evidência desta lição para a sua escolha.

## Para ir além

- [Artigo científico: "DeepSeek-R1: Incentivizing Reasoning Capability in LLMs via Reinforcement Learning", DeepSeek-AI, 2025](https://arxiv.org/abs/2501.12948)
- [Destilação: Sequência e Dados Sintéticos](../../distillation/reference/sequence-and-synthetic-data.md): a destilação em geral, da qual esta lição é o caso do modelo de raciocínio
- [Recursos](../RESOURCES.md)

---

A etapa 7 cobriu como o comportamento de raciocínio é produzido por RL e com que baixo custo ele pode ser espalhado para modelos menores depois de existir. A etapa 8 passa a um alvo diferente para a mesma família de técnicas: não a capacidade de raciocínio, mas o comportamento de segurança e de recusa.

Não ficou claro? Releia a fonte principal no topo, já que esta lição a comprime e é na compressão que o entendimento escapa. Consulte o [glossário](../GLOSSARY.md) para qualquer termo que pareceu escorregadio.

Se o problema é a lição em si, e não o material, isso é um defeito: [abra uma issue](https://github.com/TokenCemetery/teach/issues).
