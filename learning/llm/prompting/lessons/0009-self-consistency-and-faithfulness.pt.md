---
title: "9. Autoconsistência e fidelidade"
description: "Amostrar vários caminhos de raciocínio para votar em uma resposta, e por que o raciocínio escrito não é uma explicação fiel"
type: lesson
---

# Lição 9. Autoconsistência e fidelidade

**Ligação com a missão:** Duas coisas decorrem de pedir raciocínio: você pode gastar mais tokens para obter uma resposta mais estável, e não deve ler o raciocínio como prova de por que o modelo respondeu o que respondeu.
**Fonte principal:** [Paper: "Self-Consistency Improves Chain of Thought Reasoning in Language Models", Wang et al., 2022](https://arxiv.org/abs/2203.11171)
**Pré-requisitos:** [Lição 8](0008-chain-of-thought.md), [Autoconsistência](../GLOSSARY.md), [Chain-of-thought](../GLOSSARY.md)

## Aquecimento

1. ▢ A lição 7 disse que um prompt few-shot pode pender para uma resposta conforme os exemplos e a ordem deles. Por que isso torna uma única resposta amostrada menos confiável do que parece?

<details markdown="1"><summary>Verificação</summary>

Uma resposta é uma amostra de uma distribuição que o prompt já inclinou. Se a inclinação decide o resultado em um caso limítrofe, executar de novo ou reordenar pode invertê-lo, então uma resposta isolada não traz nenhuma informação sobre o quanto é frágil.

</details>

2. ▢ A lição 8 disse que o raciocínio ajuda mais em tarefas de vários passos. Cite uma tarefa do seu trabalho em que ele ajudaria e uma em que não ajudaria.

<details markdown="1"><summary>Verificação</summary>

Qualquer par que separe vários passos dependentes (um cálculo em várias partes, uma agenda com restrições) de uma consulta ou rótulo de um só passo (extrair uma data, marcar o sentimento). A primeira merece tokens de raciocínio; a segunda só paga por eles.

</details>

## Saiba isto

### Autoconsistência: amostrar e depois votar

A decodificação gulosa pega um chain-of-thought e confia nele. Wang et al., em vez disso, amostram um conjunto de caminhos de raciocínio a partir do mesmo prompt e ficam com a resposta final que aparece com mais frequência. A intuição que eles dão é que um problema difícil tem muitas formas de pensar e uma única resposta correta, então os caminhos errados tendem a discordar entre si, enquanto os certos convergem. Eles relatam ganhos sobre o chain-of-thought guloso de +17,9% no GSM8K, +11,0% no SVAMP, +12,2% no AQuA, +6,4% no StrategyQA e +3,9% no ARC-challenge.

Isso é a **autoconsistência**. Três condições decorrem de como ela funciona:

- **Precisa haver uma resposta final para comparar.** A votação roda sobre respostas tiradas de um conjunto fixo, como um número ou uma escolha, então serve a tarefas com uma resposta verificável, não a escrita aberta.
- **As amostras precisam diferir.** O método do artigo funciona com métodos de amostragem como a amostragem por temperatura. Amostras idênticas votam todas do mesmo jeito e não acrescentam nada.
- **Custa mais.** Os autores apontam o cálculo extra como a limitação e sugerem começar com 5 ou 10 caminhos, já que na maioria dos casos o desempenho satura rápido.

Em uma janela de chat, você pode aproximar isso fazendo a mesma pergunta em vários chats novos e ficando com a maioria, supondo que a interface amostre com alguma aleatoriedade.

### Fidelidade: o raciocínio não é a causa

É tentador ler o raciocínio escrito como o processo real do modelo. Turpin et al. testaram isso acrescentando ao prompt uma característica enviesadora, como reordenar os exemplos few-shot para que a resposta correta seja sempre "(A)", ou sugerir uma resposta no prompt, e verificando se o raciocínio escrito mencionava isso.

Não mencionava. Em 13 tarefas do BIG-Bench Hard com GPT-3.5 e Claude 1.0, as características enviesadoras derrubaram a acurácia em até 36%, e o raciocínio nunca se referiu à característica. Quando os modelos eram empurrados para uma resposta errada, muitas vezes escreviam um raciocínio que a justificava. Os autores chamam essas explicações de plausíveis, porém enganosas.

Duas regras práticas decorrem disso:

- **Não use o raciocínio escrito como auditoria de por que a resposta foi dada.** Ele pode ser um relato fluente que deixa de fora o que levou à resposta.
- **Teste a influência diretamente.** Para saber se algo no prompt afeta a resposta, mude essa coisa e execute de novo, como nos artigos, em vez de pedir ao modelo que se explique.

Isso não torna o raciocínio inútil. Os ganhos da lição 8 continuam valendo. Significa que o raciocínio ajuda a resposta e é uma testemunha fraca sobre a causa.

## Prática

1. ▢ Preveja e depois execute. Faça esta pergunta a um modelo de chat em três chats novos separados e anote as três respostas finais. Preveja se surge uma maioria.

    ```text
    A bat and a ball cost 1.10 dollars together. The bat costs 1.00
    dollar more than the ball. How much does the ball cost?
    Think it through, then end with "Answer:" and the amount.
    ```

<details markdown="1"><summary>Dica</summary>

A autoconsistência só ajuda se os caminhos diferirem e se a resposta mais comum for a certa.

</details>

<details markdown="1"><summary>Verificação</summary>

A resposta correta é 5 centavos. Se os três chats concordarem, a votação é unânime e as amostras extras só aumentaram a sua confiança. Se um discordar, a maioria é a sua resposta, e a discordância mostra que a pergunta não era segura para responder com uma única amostra. Uma maioria errada também é possível, e é por isso que a votação é uma forma de gastar tokens em estabilidade, não uma garantia. Tente uma pergunta de vários passos mais difícil para ver discordância com mais frequência.

</details>

2. ▢ Por que a autoconsistência serve melhor a "quanto é 17 por cento de 240" do que a "escreva uma descrição de produto"?

<details markdown="1"><summary>Verificação</summary>

A votação precisa de respostas finais que possam ser comparadas por igualdade. Um número pode, então o mais comum vence. Uma descrição de produto não tem resposta única: toda amostra é diferente, então não há nada em que votar, só textos entre os quais escolher.

</details>

3. ▢ Seu app pede a um modelo uma decisão de sim ou não e mostra o raciocínio escrito dele ao usuário como a explicação. Usando Turpin et al., descreva o risco e uma mudança.

<details markdown="1"><summary>Verificação</summary>

O risco é que o raciocínio pode omitir o que de fato levou à decisão, ou racionalizar uma decisão moldada por algo no prompt, como a ordem dos exemplos ou uma resposta sugerida, de modo que os usuários veriam um relato plausível que pode não ser a causa. Uma mudança: parar de apresentar o raciocínio escrito como a causa e rotulá-lo como a justificativa do modelo, ou testar diretamente executando de novo com a entrada suspeita alterada. Qual correção é a certa depende do que os usuários esperam da explicação.

</details>

4. ▢ Qual par descreve corretamente o que cada técnica oferece?

    - a) A autoconsistência traz uma resposta mais estável; verificações de fidelidade não se aplicam
    - b) A autoconsistência traz uma resposta mais estável; o raciocínio pode omitir a causa verdadeira
    - c) A autoconsistência explica a resposta; o raciocínio sempre nomeia sua causa verdadeira
    - d) A autoconsistência reduz o custo ao amostrar uma vez; o raciocínio pode omitir a causa

<details markdown="1"><summary>Verificação</summary>

**b)** Votar entre caminhos amostrados estabiliza a resposta final, e Turpin et al. mostram que o raciocínio escrito pode deixar de fora o que o levou a ela. (a) está errada porque a fidelidade se aplica a qualquer raciocínio que você mostre. (c) está errada duas vezes: votar não explica, e o raciocínio nem sempre nomeia sua causa. (d) está errada porque a autoconsistência custa mais amostras, não menos.

</details>

## Prática no mundo real

- [ ] Pegue uma pergunta que importa para você e que tenha uma resposta verificável. Faça-a em três chats novos e anote se as respostas concordam.
- [ ] Encontre um lugar em que você leu o raciocínio de um modelo como o motivo da resposta e anote o que você testaria para verificar isso.
- [ ] Amanhã: pegue um prompt de múltipla escolha e reordene as opções para que a certa mude de lugar, depois veja se o raciocínio do modelo menciona a mudança.

## Para ir além

- [Few-Shot e Raciocínio](../reference/few-shot-and-reasoning.md)
- [Paper: "Language Models Don't Always Say What They Think", Turpin et al., 2023](https://arxiv.org/abs/2305.04388)
- [Recursos](../RESOURCES.md)

---

Não ficou claro? Releia a fonte primária no topo, já que esta lição a comprime e é na compressão que o entendimento escapa. Consulte o [glossário](../GLOSSARY.md) para qualquer termo que tenha parecido escorregadio.

Se o problema é a própria lição e não o material, isso é um defeito: [abra uma issue](https://github.com/TokenCemetery/teach/issues).
