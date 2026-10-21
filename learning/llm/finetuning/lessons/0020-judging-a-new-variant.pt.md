---
title: "20. Julgando uma nova variante de PEFT"
description: "Seis perguntas de triagem, e o baseline a superar"
type: lesson
---

# Lição 20. Julgando uma nova variante de PEFT

**Ligação com a missão:** "Ler um novo artigo sobre PEFT e julgar se o ganho que ele alega sobreviveria na sua própria tarefa" é o último item da lista de sucesso. Esta lição é essa habilidade.
**Fonte principal:** [Docs: LoRA variants, Hugging Face PEFT](https://huggingface.co/docs/peft/main/en/developer_guides/lora)
**Pré-requisitos:** [Lição 19](0019-when-dora-wins.md), [Lição 17](0017-what-qlora-costs.md)

## Aquecimento

1. ▢ Sob qual condição o DoRA é a escolha certa em vez de mais rank?

<details markdown="1"><summary>Verificação</summary>

Quando o rank está fixado em valor baixo por algo que você não pode remover, em geral risco de overfitting em um dataset pequeno.

</details>

2. ▢ O que precisa ser igual para duas execuções serem comparáveis?

<details markdown="1"><summary>Verificação</summary>

Tudo, exceto a única variável sob teste: dados, divisão, seed, rank, alpha, learning rate, schedule, passos.

</details>

3. ▢ Quais dois custos de qualidade a quantização tem, e como eles são separados?

<details markdown="1"><summary>Verificação</summary>

Degradação do base antes do treinamento, e um treinamento de adapter pior sobre um base degradado. Isole o primeiro avaliando bases quantizados e não quantizados sem adapter.

</details>

## Saiba isto

Novos métodos de fine-tuning eficiente em parâmetros aparecem o tempo todo. A maioria não importa para você. A habilidade é a triagem, não o entusiasmo.

### O panorama, organizado pelo que eles mudam

Em vez de decorar métodos, aprenda os eixos. Quase toda variante modifica uma de quatro coisas.

**A escala.** O rsLoRA ([arXiv:2312.03732](https://arxiv.org/abs/2312.03732)) substitui o divisor `α/r` por `α/√r`, argumentando que `α/r` amortece demais em rank alto. Barato, uma flag, importa quando você trabalha com rank alto.

**Os learning rates.** O LoRA+ ([arXiv:2402.12354](https://arxiv.org/abs/2402.12354)) usa um learning rate maior para `B` do que para `A`, argumentando que os dois fatores não deveriam compartilhar uma única taxa, dados os seus papéis e escalas diferentes. Barato, e um botão genuinamente diferente de qualquer coisa da Lição 9.

**A inicialização.** Em vez de `A` aleatória e `B` zero:

- O **PiSSA** ([arXiv:2404.02948](https://arxiv.org/abs/2404.02948)) inicializa a partir dos componentes singulares principais de `W₀`, de modo que o adapter começa alinhado com as direções dominantes do peso.
- O **OLoRA** inicializa por meio de decomposição QR de `W₀`.
- O **LoftQ** ([arXiv:2310.08659](https://arxiv.org/abs/2310.08659)) inicializa o adapter para compensar o erro de quantização, especificamente para o cenário do QLoRA.

Note que todos esses abrem mão da propriedade de inicialização em zero da Lição 9: o modelo já não começa idêntico ao base. Essa é uma troca deliberada, e é a coisa a examinar com atenção.

**A estrutura.**

- O **AdaLoRA** ([arXiv:2303.10512](https://arxiv.org/abs/2303.10512)) aloca o rank de forma adaptativa entre as camadas em vez de usar um único rank em todo lugar, com o argumento de que as camadas diferem em quanta adaptação precisam.
- O **VeRA** ([arXiv:2310.11454](https://arxiv.org/abs/2310.11454)) compartilha `A` e `B` aleatórias congeladas entre as camadas e treina apenas pequenos vetores de escala, reduzindo drasticamente o tamanho do adapter.
- O **DoRA** desacopla a magnitude da direção, como na Lição 18.

No PEFT, a maioria deles é uma flag de configuração ou um valor de `init_lora_weights` em vez de um caminho de código separado, o que torna barato experimentá-los e faz da leitura da superfície de configuração um modo rápido de ver o que a biblioteca considera estabelecido.

### As perguntas de triagem

Quando um novo método aparece, faça estas em ordem. Em geral você pode parar cedo.

**1. O que ele muda, em qual dos quatro eixos?** Se você não consegue responder isso a partir do abstract e de uma figura, o artigo ou está mal escrito ou você ainda não é o público. Só essa pergunta filtra a maior parte das coisas.

**2. Qual é o baseline?** A forma mais comum de inflar um resultado é um baseline fraco. Fique atento a: LoRA em um rank que os autores escolheram, targets só de atenção quando all-linear é o padrão moderno, um learning rate ajustado para o novo método mas herdado para o baseline. **Um método que vence um LoRA não ajustado não foi mostrado como superior ao LoRA.**

**3. O ganho é maior do que o ruído?** Procure variância de seed ou intervalos de confiança. Se o artigo reporta números únicos sem dispersão, e o ganho é de um ponto ou dois, o resultado ainda não é distinguível de ruído. Isso é extremamente comum.

**4. O que ele custa?** Tempo por passo, complexidade de implementação, se faz merge de forma limpa, se se compõe com quantização, se existe uma implementação em que você confie. Um ganho de 1% por uma lentidão de 30% é uma troca ruim na maioria dos cenários.

**5. O mecanismo dele se aplica ao seu regime?** O benefício do DoRA mora em rank baixo. O do LoftQ mora no treinamento quantizado. O do rsLoRA mora em rank alto. Um método cujo mecanismo trata de uma restrição que você não tem não vai ajudar, e isso é previsível *antes* de executar qualquer coisa.

**6. Alguém independente o reproduziu?** As comunidades de profissionais testam métodos em tarefas reais rapidamente e são diretas sobre o que não replica. Isso costuma ser mais rápido e mais informativo do que ler o artigo duas vezes.

### Três sinais de alerta confiáveis

- **Ganhos relatados só em benchmarks, nunca em uma tarefa com implantação.** Benchmarks são proxies e são muito otimizados contra.
- **Comparação com um baseline de LoRA só de atenção** em um artigo escrito depois de o all-linear se tornar prática padrão. Ou é desinformado ou é conveniente.
- **Nenhuma contabilidade de custo.** Todo método tem um custo. Um artigo que não declara o seu não está sendo franco com você, e a omissão costuma ser a parte interessante.

### A posição padrão

**LoRA com rank adequado em todas as camadas lineares, com um learning rate ajustado, é um baseline forte e difícil de superar por muito.** Essa é a conclusão prática da linha de trabalhos "LoRA without regret", e deve ser o seu ponto de partida e a sua comparação.

Uma nova variante precisa superar *isso*, na sua tarefa, por mais do que o seu ruído de seed, por um custo menor do que aumentar o rank teria. A maioria não passa da barra. Saber isso não é cinismo. É o que permite gastar atenção nas poucas que passam.

## Prática

1. ▢ Nomeie os quatro eixos que uma variante de PEFT pode modificar, com um exemplo de cada.

<details markdown="1"><summary>Verificação</summary>

Escala (rsLoRA), learning rates (LoRA+), inicialização (PiSSA, OLoRA, LoftQ), estrutura (AdaLoRA, VeRA, DoRA).

Conhecer os eixos significa que um novo método é classificável à primeira vista, em vez de precisar ser aprendido do zero.

</details>

2. ▢ Um artigo relata que o seu método vence o LoRA por 2.1 pontos, com o LoRA em rank 8 só em módulos de atenção. Qual é a sua preocupação?

<details markdown="1"><summary>Verificação</summary>

O baseline é fraco pelos padrões atuais. Targets all-linear em rank mais alto é o padrão moderno e é substancialmente mais forte do que só atenção em rank 8.

O método pode muito bem vencer esse baseline fraco e ainda assim perder para um LoRA configurado corretamente. A comparação como publicada não diz isso a você.

</details>

3. ▢ Qual propriedade de um artigo mais enfraquece um ganho alegado de 1.5 ponto?

    - a) A ausência de qualquer variância de seed ou intervalos reportados
    - b) O uso de um modelo menor do que o que você pretende usar
    - c) A ausência de uma implementação de referência liberada
    - d) A avaliação em apenas três tarefas downstream distintas

<details markdown="1"><summary>Verificação</summary>

**a)** A ausência de qualquer variância de seed ou intervalos reportados.

Sem uma dispersão, um ganho de 1.5 ponto não pode ser distinguido do ruído de execução para execução, que muitas vezes tem esse tamanho. As outras são limitações reais, mas não minam a alegação central como a variância ausente faz.

</details>

4. ▢ O LoftQ inicializa o adapter para compensar o erro de quantização. Em qual regime você preveria que ele ajuda, e onde preveria que não faz nada?

<details markdown="1"><summary>Verificação</summary>

Ele deve ajudar ao treinar contra um base quantizado, de forma mais visível com quantização agressiva e em modelos menores, onde o erro de quantização é proporcionalmente mais danoso.

Ele deve não fazer nada com um base em bf16 não quantizado, porque não há erro de quantização a compensar, então o mecanismo não tem onde se apoiar.

</details>

5. ▢ O PiSSA abre mão da inicialização em zero. Por que isso importa, e o que você verificaria?

<details markdown="1"><summary>Verificação</summary>

A inicialização em zero garante que o modelo adaptado começa idêntico ao base, então o treinamento começa de pesos sabidamente bons e qualquer degradação é atribuível ao treinamento.

Abrir mão disso significa que o modelo começa perturbado. Verifique instabilidade precoce e verifique se a perturbação danificou capacidades fora da sua tarefa. Um conjunto de regressão (Lição 24) executado no passo zero, antes do treinamento, é o teste direto.

</details>

6. ▢ Qual é o baseline que toda nova variante precisa superar, e por que ele é difícil?

<details markdown="1"><summary>Verificação</summary>

LoRA com rank adequado em todas as camadas lineares, com um learning rate ajustado.

É difícil porque ele já tem capacidade e cobertura suficientes para se aproximar do full fine-tuning em muitas tarefas supervisionadas. Quando o baseline está perto de um teto, sobra pouca folga para um refinamento de mecanismo reivindicar.

</details>

## Prática no mundo real

- [ ] Escolha uma variante desta lição que você não tenha usado. Execute as seis perguntas de triagem contra o artigo dela e escreva um veredicto de um parágrafo para a sua própria tarefa.
- [ ] Leia as opções de `init_lora_weights` na sua versão instalada do PEFT. Associe cada uma a um método e a um eixo.
- [ ] Pesquise relatos independentes sobre esse método em uma comunidade de profissionais. Compare o que eles encontraram com o que o artigo alegava.
- [ ] Amanhã: execute a variante escolhida contra um baseline de LoRA all-linear bem ajustado, três seeds cada. Registre se o ganho sobrevive.

## Para ir além

- [Docs: LoRA variants, Hugging Face PEFT](https://huggingface.co/docs/peft/main/en/developer_guides/lora)
- [Docs: "LoRA Without Regret", Hugging Face TRL](https://huggingface.co/docs/trl/main/en/lora_without_regret)
- [EleutherAI Blog](https://blog.eleuther.ai/): um grupo que publica seus resultados negativos, que é a metade mais rara desta pergunta
- [r/LocalLLaMA](https://www.reddit.com/r/LocalLLaMA/): relatos de replicação rápidos e diretos

---

Não ficou claro? Releia a fonte principal no topo, já que esta lição a comprime e é na compressão que o entendimento escapa. Consulte o [glossário](../GLOSSARY.md) para qualquer termo que pareceu escorregadio.

Se o problema é a lição em si, e não o material, isso é um defeito: [abra uma issue](https://github.com/TokenCemetery/teach/issues).
