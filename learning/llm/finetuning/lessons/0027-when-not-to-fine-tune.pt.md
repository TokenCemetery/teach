---
title: "27. Quando não fazer fine-tuning"
description: "O fine-tuning é o sexto da lista, e por que isso importa"
type: lesson
---

# Lição 27. Quando não fazer fine-tuning

**Ligação com a missão:** A missão termina aqui: *"que também consegue defender com argumentos convincentes o prompting ou a recuperação quando eles resolveriam melhor o problema."* A habilidade sênior é recusar o trabalho.
**Fonte principal:** [Docs: "LoRA Without Regret", Hugging Face TRL](https://huggingface.co/docs/trl/main/en/lora_without_regret)
**Pré-requisitos:** todas as lições anteriores, já que esta é a síntese.

## Aquecimento

1. ▢ Qual fase da inferência é limitada pela largura de banda, e por que isso favorece modelos menores?

<details markdown="1"><summary>Verificação</summary>

O decode. Cada passo lê todos os pesos para produzir um token, então a velocidade acompanha a largura de banda de memória e um modelo menor é mais rápido quase na proporção do seu tamanho.

</details>

2. ▢ Nomeie as quatro categorias de regressão.

<details markdown="1"><summary>Verificação</summary>

Seguimento geral de instruções, conformidade de formato e de comportamento, comportamento de segurança e de recusa, capacidade adjacente não treinada.

</details>

3. ▢ Qual é o baseline que uma nova variante de PEFT precisa superar?

<details markdown="1"><summary>Verificação</summary>

LoRA com rank adequado em todas as camadas lineares, com um learning rate ajustado.

</details>

## Saiba isto

### A decisão, em ordem

Desça por esta lista. Pare na primeira linha que resolver o seu problema.

| Abordagem | Resolve | Custo |
|---|---|---|
| Prompt melhor | A maioria dos problemas de formato e comportamento | Minutos |
| Exemplos few-shot | Consistência de formato, formato da saída | Tokens de prompt por requisição |
| Recuperação | Conhecimento ausente ou em mudança | Infraestrutura de recuperação |
| Uso de ferramentas | Cálculo, consulta, ações | Infraestrutura de ferramentas |
| Decodificação restrita | Validade de schema, de forma absoluta | Suporte no serving |
| **Fine-tuning** | Comportamento consistente, custo de prompt, suficiência de modelo pequeno | Dados, avaliação, manutenção |
| Full fine-tuning | Mudanças comportamentais muito grandes | Substancialmente mais de tudo |

O fine-tuning é o sexto. **A maioria das pessoas que querem fazer fine-tuning tem um problema que um dos cinco primeiros resolve, mais rápido e com mais confiabilidade.** Chegar à linha seis antes de esgotar as linhas um a cinco é o erro caro mais comum desta área.

Note em especial que **a decodificação restrita resolve a validade de schema por completo**, porque a geração restrita por gramática não consegue emitir JSON inválido. Se todo o seu problema é saída malformada, você não precisa treinar nada.

### As três perguntas que decidem

**1. O problema é de conhecimento ou de comportamento?**

Conhecimento, ou seja, fatos, documentos e qualquer coisa que mude, é trabalho da recuperação. O fine-tuning instala fatos de forma pouco confiável, inverificável, e a defasagem exige retreinamento. A recuperação é precisa, citável e atualizada editando um documento.

Comportamento, ou seja, formato, tom, estrutura, consistência e uma fronteira de decisão, é trabalho do fine-tuning. É onde ele genuinamente se destaca e onde nada mais funciona tão bem.

A armadilha: "o modelo não conhece o nosso produto" soa como um problema de treinamento e é um problema de recuperação. "O modelo não responde de forma consistente no nosso estilo da casa, não importa como eu faça o prompt" soa como um problema de prompting e é um problema de treinamento.

**2. Você realmente esgotou o prompting?**

Não "tentou alguns prompts". Esgotou: iteração sistemática, exemplos few-shot, um system prompt estruturado e **medido no mesmo conjunto held-out que você usaria para avaliar um fine-tune.** A maioria das alegações de que o prompting falhou são alegações de que um punhado de tentativas não medidas falhou.

Se você não consegue declarar a pontuação do prompting no seu conjunto held-out, você não tem baseline, e sem um baseline você não consegue demonstrar que o fine-tune ajudou.

**3. Você vai manter isso?**

Um fine-tune é um artefato vivo. Base models são superados, requisitos mudam, distribuições derivam, avaliações precisam ser atualizadas. Se ninguém é dono dele, você está construindo algo que vai decair em silêncio enquanto parece funcionar, e um fine-tune defasado é pior do que nenhum fine-tune, porque é confiável.

### Quando o fine-tuning está claramente certo

Para ser justo com o método, estes casos são reais e comuns:

- **Alto volume com um prompt longo.** Mover o conteúdo do prompt para os pesos se paga em toda requisição (Lição 26).
- **Um modelo menor passa a ser suficiente.** O caso mais forte, porque reduz custo e latência juntos.
- **Comportamento que resiste ao prompting.** Um tom, um formato ou uma fronteira de decisão que o modelo não mantém de forma consistente, não importa como você peça.
- **Uma tarefa estreita com exemplos abundantes.** Classificação, extração, transformação estruturada: o fine-tuning é excelente e muitas vezes vence um modelo muito maior com prompt.
- **Caminhos críticos de latência.** Prompts mais curtos e modelos menores ajudam, diretamente.
- **Uma notação ou sintaxe específica de domínio** genuinamente sub-representada no pré-treinamento.

### Combinar, em vez de escolher

O enquadramento "fazer fine-tuning ou recuperar" costuma estar errado. Os sistemas mais fortes fazem os dois, para trabalhos diferentes:

**A recuperação fornece os fatos. O fine-tuning ensina o que fazer com eles.**

Um modelo com fine-tuning para usar bem o contexto recuperado, citando-o, respeitando-o, admitindo quando ele é insuficiente e recusando-se a inventar além dele, combinado com uma recuperação que fornece fatos atuais e precisos, vence qualquer um dos dois sozinho. Isso é uma arquitetura, e reconhecê-la é a versão sênior desta decisão.

### A posição calibrada sobre capacidade

Você conquistou uma visão matizada aqui, então mantenha-a com precisão.

O velho enquadramento, "o LoRA é uma aproximação barata, o full fine-tuning é o de verdade", está em grande parte obsoleto. Com rank adequado em todas as camadas lineares e um learning rate bem ajustado, o LoRA iguala o full fine-tuning em cargas típicas de supervised fine-tuning. **A diferença de capacidade em grande parte se fechou para o regime em que a maioria das pessoas trabalha.**

O que significa: se você decidiu fazer fine-tuning, os adapters quase certamente são o método certo. O full fine-tuning é para mudanças comportamentais muito grandes, pré-treinamento continuado em um novo domínio ou idioma em escala, ou pesquisa em que você precisa de todo o espaço de parâmetros. A pergunta que resta não é "adapter ou completo", e sim "isto deve ser treinado".

### Como soa um bom julgamento

> "As falhas relatadas são todas defasagem factual, então isto é recuperação, não treinamento. Deixe-me medir primeiro um baseline com prompt no conjunto held-out. Se o problema residual depois da recuperação for consistência de formato a 40,000 requisições por dia, então um adapter all-linear de rank 32 em um modelo de 3B vale ser orçado, incluindo a pessoa que vai retreiná-lo daqui a seis meses. Eu gostaria de um conjunto de regressão cobrindo segurança e seguimento geral de instruções antes de entregar, porque estaríamos adaptando um modelo instruct."

Nada ali é um fato que você pesquisou. É o formato de raciocínio para o qual este workspace existia.

## Prática

1. ▢ "O nosso bot de suporte não conhece os produtos lançados neste trimestre." Fazer fine-tuning ou não?

<details markdown="1"><summary>Verificação</summary>

Não. Isso é conhecimento, e conhecimento que muda a cada trimestre é o pior encaixe possível para o fine-tuning, que instala fatos de forma pouco confiável e fica defasado de imediato.

Recuperação: precisa, citável, atualizada editando um catálogo. O fine-tuning poderia valer a pena à parte para ensinar o bot a *usar* bem os dados recuperados de produtos.

</details>

2. ▢ "O prompting não funcionou." O que você pergunta?

<details markdown="1"><summary>Verificação</summary>

O que foi medido, em qual conjunto held-out, com qual pontuação. Além disso: foram testados exemplos few-shot, foi testado um system prompt estruturado, foi testada a decodificação restrita para um problema de formato.

Sem um baseline com prompt medido, não há nada com que comparar um fine-tune, então você não consegue demonstrar melhora mesmo que a consiga.

</details>

3. ▢ Todo o seu problema é que 12% das saídas são JSON inválido. Correção mais barata?

<details markdown="1"><summary>Verificação</summary>

Decodificação restrita. A geração restrita por gramática não consegue produzir JSON inválido, e é uma mudança do lado do serving, sem nenhum treinamento.

O fine-tuning pode chegar a 99% de validade. A decodificação restrita chega a 100% por construção. Faça fine-tuning só se os *valores* também estiverem errados, o que é um problema diferente.

</details>

4. ▢ Qual situação mais favorece o fine-tuning?

    - a) O modelo não conhece a sua documentação interna
    - b) Alto volume de requisições com um system prompt muito longo
    - c) O modelo comete erros ocasionais de aritmética na saída
    - d) O modelo precisa de informações sobre eventos desta semana

<details markdown="1"><summary>Verificação</summary>

**b)** Alto volume de requisições com um system prompt muito longo.

Mover o conteúdo do prompt para os pesos remove o custo de prefill em toda requisição, e a economia escala com o volume. (a) e (d) são recuperação. (c) é uso de ferramentas: dê uma calculadora a ele.

</details>

5. ▢ O LoRA é um meio-termo em relação ao full fine-tuning?

<details markdown="1"><summary>Verificação</summary>

Em grande parte não, no regime em que a maioria das pessoas trabalha. Com rank adequado em todas as camadas lineares e um learning rate ajustado, o LoRA iguala o full fine-tuning em cargas típicas de supervised fine-tuning.

O full fine-tuning continua apropriado para mudanças comportamentais muito grandes, pré-treinamento continuado em escala ou pesquisa que precisa de todo o espaço de parâmetros. Para uma adaptação de tarefa comum, os adapters são o método certo, e não uma concessão.

</details>

6. ▢ A sua recuperação funciona e o modelo ainda ignora o contexto recuperado e inventa respostas. E agora?

<details markdown="1"><summary>Verificação</summary>

Agora o fine-tuning está bem motivado, e esta é a arquitetura combinada, e não uma escolha entre abordagens.

O problema é de comportamento: ancorar-se no contexto fornecido, respeitá-lo, citá-lo e recusar quando ele é insuficiente. A recuperação fornece fatos; o treinamento ensina o que fazer com eles. Construa o dataset a partir de contextos recuperados reais com respostas ancoradas corretas, incluindo casos em que a resposta certa é "o contexto fornecido não cobre isto".

</details>

## Prática no mundo real

- [ ] Pegue uma proposta de fine-tuning, sua ou de outra pessoa, e aplique a ela as três perguntas. Escreva um veredicto de um parágrafo.
- [ ] Meça um baseline com prompt no seu conjunto held-out, de forma correta. Registre o número antes de treinar qualquer coisa.
- [ ] Calcule o custo da vida inteira de um fine-tune: dados, avaliação, serving, retreinamento, titularidade. Compare com a economia.
- [ ] Amanhã: encontre um caso em que você se recusaria a fazer fine-tuning e escreva o argumento a favor da alternativa em um parágrafo que outra pessoa poderia executar.

## Para ir além

- [Docs: "LoRA Without Regret", Hugging Face TRL](https://huggingface.co/docs/trl/main/en/lora_without_regret)
- [Artigo científico: "Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks", Lewis et al., arXiv:2005.11401](https://arxiv.org/abs/2005.11401)
- [r/LocalLLaMA](https://www.reddit.com/r/LocalLLaMA/): pesquise ali os casos em que profissionais decidiram contra o fine-tuning, e o que entregaram no lugar
- [Modos de falha](../reference/failure-modes.md), [Hiperparâmetros do LoRA](../reference/lora-hyperparameters.md), [Orçamento de memória](../reference/memory-budget.md)

---

Esse é o arco. A partir daqui o trabalho são repetições em tarefas reais, e a última linha da missão é a que vale guardar: conseguir argumentar de forma convincente *contra* o fine-tuning é o que faz o argumento *a favor* dele valer alguma coisa.

Não ficou claro? Releia a fonte principal no topo, já que esta lição a comprime e é na compressão que o entendimento escapa. Consulte o [glossário](../GLOSSARY.md) para qualquer termo que pareceu escorregadio.

Se o problema é a lição em si, e não o material, isso é um defeito: [abra uma issue](https://github.com/TokenCemetery/teach/issues).
