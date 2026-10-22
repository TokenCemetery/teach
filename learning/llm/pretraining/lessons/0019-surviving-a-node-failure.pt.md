---
title: "19. Sobrevivendo à falha de um nó"
description: "Pausar, diagnosticar, isolar o que quebrou e retomar do último checkpoint, ao custo que for"
type: lesson
---

# Lição 19. Sobrevivendo à falha de um nó

**Ligação com a missão:** "Consegue projetar um esquema de checkpointing que limita o progresso perdido após a falha de um nó" é o item de O sucesso se parece com isto que esta etapa atende. A Lição 18 cobriu o que um checkpoint precisa guardar e com que frequência salvar um; esta lição cobre o que de fato acontece quando uma falha acontece.
**Fonte principal:** [Artigo científico: "OPT: Open Pre-trained Transformer Language Models", Zhang et al., 2022](https://arxiv.org/abs/2205.01068)
**Pré-requisitos:** [Lição 18](0018-what-a-checkpoint-has-to-hold.md)

## Aquecimento

1. ▢ Nomeie as quatro coisas que um checkpoint precisa guardar para retomar uma execução corretamente, e não apenas de forma aproximada.

<details markdown="1"><summary>Verificação</summary>

Os parâmetros do modelo, o estado do otimizador, a contagem de passos e a posição no schedule de learning rate e, para reprodutibilidade exata, a posição do data loader e o estado do gerador de números aleatórios.

</details>

2. ▢ Ao longo de aproximadamente dois meses de treinamento do OPT-175B, o que Zhang et al. relataram sobre a frequência com que as falhas de hardware ocorreram?

<details markdown="1"><summary>Verificação</summary>

Pelo menos 35 reinícios manuais e a rotação de mais de 100 hosts, mais uma estimativa de mais de 70 reinícios automáticos adicionais, bem mais de um reinício a cada dois dias, sustentado ao longo da execução.

</details>

## Saiba isto

### O procedimento que o OPT de fato seguiu

Zhang et al. descrevem uma sequência específica e repetível, e não uma correria improvisada cada vez que uma falha acontecia: quando se suspeitava de um problema de hardware, a execução de treinamento era **pausada**; uma série de **testes de diagnóstico** era executada para identificar quais nós específicos estavam se comportando mal; qualquer nó sinalizado pelo diagnóstico era **isolado**, ou seja, excluído do pool de nós que a execução usaria dali em diante; e o treinamento então **retomava do último checkpoint salvo**, agora rodando nos nós restantes e saudáveis. É o mesmo padrão independentemente de a falha ter sido pega manualmente ou ter disparado um reinício automático: diagnosticar, excluir o hardware ruim, retomar do estado salvo mais recente.

### Reinícios manuais contra automáticos, e por que a diferença importa operacionalmente

Zhang et al. distinguem mais de 35 reinícios **manuais**, em que uma pessoa reconheceu um problema e interveio, de uma estimativa de mais de 70 reinícios **automáticos**, inferida da diferença entre o número de hosts rotacionados e o número menor de reinícios manuais registrados. Um reinício automático implica uma ferramenta que detecta uma falha e retoma o treinamento sem esperar que uma pessoa perceba e aja, o que importa diretamente para quanto progresso uma falha de fato custa: uma falha que espera a detecção manual perde todo o tempo que passa antes de uma pessoa intervir, além do que o próprio ciclo de checkpoint e retomada custa, enquanto uma falha detectada e retomada automaticamente perde algo mais próximo de apenas o progresso de um intervalo de checkpoint de que a Lição 18 tratou.

### A divergência de loss como uma falha relacionada, mas distinta, de que se recuperar

Zhang et al. também descrevem reiniciar por um motivo inteiramente diferente: a divergência de loss, e não a falha de hardware. Quando a loss de treinamento divergia, baixar a learning rate e reiniciar de um checkpoint anterior permitia que a execução se recuperasse e continuasse. Eles notaram que isso se correlacionava com dois outros sinais: o seu loss scalar dinâmico (parte da configuração de precisão mista) caindo a zero e a norma das ativações da última camada disparando. Em vez de reiniciar de imediatamente antes da divergência, escolhiam pontos de reinício em que o loss scalar ainda estava em um estado saudável e as normas das ativações estavam tendendo a cair em vez de crescer sem limite e, separadamente, constataram que baixar o gradient clipping de 1.0 para 0.3 ajudou. Essa é uma segunda razão, genuinamente diferente, para um checkpoint ser usado para retomar uma execução, distinta da morte de um nó: o hardware está bem, mas o próprio processo de treinamento precisa voltar atrás e continuar de forma diferente, o que só um histórico mantido de checkpoints (e não apenas o único mais recente) torna possível.

## Prática

1. ▢ Coloque estes quatro passos do procedimento de falha de nó do OPT na ordem que Zhang et al. descrevem: (a) retomar o treinamento nos nós restantes, (b) pausar a execução de treinamento, (c) executar testes de diagnóstico para identificar os nós ruins, (d) isolar os nós sinalizados.

<details markdown="1"><summary>Verificação</summary>

b, c, d, a: pausar, diagnosticar, isolar o que o diagnóstico sinalizou e então retomar do último checkpoint salvo nos nós restantes e saudáveis.

</details>

2. ▢ Por que uma falha detectada e retomada automaticamente costuma custar menos progresso do que uma detectada manualmente, mesmo que ambas acabem retomando do mesmo checkpoint?

<details markdown="1"><summary>Verificação</summary>

Um reinício manual perde todo o tempo que passa antes de uma pessoa perceber o problema e intervir, além do próprio ciclo de checkpoint e retomada. Um reinício automático pula esse atraso de detecção, então o custo total fica mais próximo de apenas o progresso de um intervalo de checkpoint.

</details>

3. ▢ A loss de treinamento de uma equipe diverge, mas não há falha de hardware: todos os nós estão saudáveis. Segundo o relato de Zhang et al., um checkpoint ainda é útil aqui e, se for, como?

    - a) Não; os checkpoints só ajudam com falhas de hardware, e não com a divergência de loss
    - b) Sim; reiniciar de um checkpoint anterior, junto com baixar a learning rate, é exatamente como Zhang et al. se recuperaram da divergência de loss
    - c) Sim, mas só o único checkpoint mais recente pode ser usado, não importa quando a divergência começou
    - d) Não; a divergência de loss exige retreinar o modelo do zero

<details markdown="1"><summary>Dica</summary>

Zhang et al. escolheram pontos de reinício especificamente com base no estado do seu loss scalar e das normas das ativações, e não simplesmente o checkpoint mais recente disponível.

</details>

<details markdown="1"><summary>Verificação</summary>

**b)** é exatamente o que Zhang et al. descrevem. (a) é falsa; o mesmo mecanismo de checkpoint e retomada recupera de qualquer das duas causas. (c) está errada justamente porque eles escolheram um ponto de reinício com base em quando o loss scalar estava saudável e as normas das ativações tendiam a cair, o que pode não ser o único checkpoint mais recente, defendendo manter mais de um checkpoint recente à mão. (d) contradiz o próprio relato do artigo de recuperação sem um reinício completo.

</details>

4. ▢ Por que a recuperação de uma divergência de loss, como Zhang et al. a descrevem, defende manter mais do que apenas o único checkpoint mais recente?

<details markdown="1"><summary>Verificação</summary>

Porque o melhor ponto de reinício nem sempre era o checkpoint mais recente; era um escolhido com base na saúde do loss scalar e na direção para a qual as normas das ativações tendiam, o que podia estar mais atrás do que o último salvamento. Manter apenas o checkpoint mais novo removeria a opção de voltar a um ponto anterior e mais estável.

</details>

## Prática no mundo real

- [ ] Encontre onde um framework de treinamento ou ferramenta de orquestração a que você tenha acesso expõe a detecção e o reinício automáticos de falhas (health checks, drenagem de nós ou termos semelhantes são comuns). Anote se corresponde ao padrão de pausar, diagnosticar, isolar e retomar que esta lição descreve.
- [ ] Leia o parágrafo "Loss Divergences" do artigo do OPT (linkado acima) e escreva uma frase sobre que sinal, além da própria curva de loss, os autores usaram para julgar se um ponto de reinício era seguro para retomar.
- [ ] Amanhã: para a frequência de checkpoint que você escolheu na prática no mundo real da Lição 18, decida quantos checkpoints recentes você manteria à mão em vez de apenas o último e escreva uma frase dizendo por quê, dado o caso de recuperação de divergência de loss desta lição.

## Para ir além

- [Artigo científico: "OPT: Open Pre-trained Transformer Language Models", Zhang et al., 2022](https://arxiv.org/abs/2205.01068)
- [Recursos](../RESOURCES.md)

---

A etapa 8 cobriu sobreviver a uma falha dentro de uma única execução de treinamento. A etapa 9 se volta para uma pergunta de prazo mais longo: acompanhar o progresso dessa execução para começo de conversa e saber se ela está no caminho certo.

Não ficou claro? Releia a fonte principal no topo, já que esta lição a comprime e é na compressão que o entendimento escapa. Consulte o [glossário](../GLOSSARY.md) para qualquer termo que pareceu escorregadio.

Se o problema é a lição em si, e não o material, isso é um defeito: [abra uma issue](https://github.com/TokenCemetery/teach/issues).
