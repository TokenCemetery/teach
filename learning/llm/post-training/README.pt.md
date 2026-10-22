---
title: "Pós-treinamento de LLMs"
description: "Alinhe um base model: SFT, modelagem de recompensa, RLHF, DPO e GRPO, e saiba qual escolher"
type: topic
---

# Pós-treinamento de LLMs

Seja capaz de levar um base model pré-treinado a um assistente alinhado que segue instruções: escrever corretamente os objetivos de SFT, de recompensa e de preferência, escolher entre RLHF-PPO, DPO e GRPO para o orçamento e os dados de uma dada equipe e defender essa escolha, inclusive o que ela custou em alignment tax e onde ela fica exposta a reward hacking.

**Última lição:** [0020. Revisando a receita de alinhamento de outra pessoa](lessons/0020-reviewing-someone-elses-alignment-recipe.md)

## O sucesso se parece com isto

- Escrever um loop de treinamento de SFT que mascara a loss nos tokens que não são do assistente e explicar o que quebra em um chat model treinado sem essa máscara.
- Treinar um reward model em pares de preferência usando a loss de Bradley-Terry e identificar uma completion com reward hacking vinda de uma policy treinada contra ele.
- Derivar o objetivo do RLHF (recompensa menos uma penalidade de KL contra um modelo de referência) e dizer o que acontece com a policy quando a penalidade de KL é afrouxada.
- Derivar a recompensa implícita do DPO a partir dos mesmos dados de preferência que o RLHF usa e dizer o que ele abre mão ao remover o loop de RL.
- Explicar a vantagem relativa ao grupo no GRPO e por que uma recompensa verificável (um teste unitário, uma resposta matemática conferida) muda o que o treinamento de RL pode ter como alvo.
- Dados os dados, o orçamento e o comportamento-alvo de uma equipe, escolher entre SFT sozinho, DPO, RLHF-PPO e GRPO, e defender a escolha contra a rejeitada.
- Ler os resultados de avaliação de um modelo alinhado e separar um ganho genuíno de capacidade de um artefato de reward hacking ou de viés do juiz.

## Restrições

- Algoritmo primeiro, e não um levantamento de artigos. Cada etapa ensina um objetivo de treinamento a partir da sua função de loss para fora, o que está sendo maximizado e o que o gradiente faz, em vez de resumir uma lista de artigos; os artigos ancoram cada etapa como a sua fonte principal.
- Práticas em pequena escala: os labs executam SFT e DPO em um modelo aberto pequeno, a mesma disciplina de escala que `llm/finetuning` usa, e raciocinam a partir daí até o que os artigos de fronteira citados relatam.
- Pressupõe `llm/transformers` (a loss de cross-entropy, o backward pass, o AdamW) e familiaridade com a mecânica de adapters de `llm/finetuning`, já que esta trilha a reutiliza em vez de rederivar a eficiência de parâmetros.
- Nenhuma lição treina um pipeline completo de RLHF de ponta a ponta em escala de fronteira; o custo do PPO é demonstrado em pequena escala e depois raciocinado na escala que os artigos citados relatam.

## Fora do escopo

- A mecânica de eficiência de parâmetros (rank e alpha do LoRA, QLoRA, DoRA, módulos-alvo): veja [`llm/finetuning`](../../llm/finetuning/). Esta trilha é dona do objetivo de treinamento; `llm/finetuning` é dono de como ele é aplicado a menos parâmetros.
- A loss de cross-entropy, o backward pass e o AdamW: veja [`llm/transformers`](../../llm/transformers/). Pressupostos aqui, e não reensinados.
- A mecânica de LLM-as-judge e a metodologia de avaliação humana: veja [`llm/evals`](../../llm/evals/). Tratadas aqui apenas como a única capacidade de que um modelo alinhado precisa, a de julgar se o treinamento de alinhamento ajudou, e linkadas em vez de reafirmadas.
- Fazer prompt em um modelo de raciocínio, ou construir um agente em torno dele: veja [`llm/agents`](../../llm/agents/) (lição 0017). Esta trilha cobre como o comportamento de raciocínio é produzido pelo treinamento de RL, e não como usá-lo de fora.
- Treinar um modelo a partir de uma inicialização aleatória: veja [`llm/pretraining`](../../llm/pretraining/).
- A destilação em geral, além do caso do modelo de raciocínio: veja [`llm/distillation`](../../llm/distillation/). A lição 0014 aqui continua sendo o caso do modelo de raciocínio e aponta para lá para o método geral.
- Usar o seguimento de instruções e o raciocínio de fora, por meio de prompts: veja [`llm/prompting`](../../llm/prompting/). Esta trilha cobre como esses comportamentos são treinados.

## O arco

Dez etapas, do nenhum conhecimento prévio ao julgamento sênior. Não é uma lista de lições: uma etapa leva várias lições e as fronteiras são flexíveis.

| Etapa | Lições | Cobre | Concluída quando |
| --- | --- | --- | --- |
| 1. O que o pós-treinamento oferece | 0001 a 0001 | Base model contra modelo instruct/chat, o panorama de SFT/RLHF/DPO/GRPO | Consegue situar o comportamento de um dado modelo alinhado em relação à etapa de pós-treinamento que o produziu |
| 2. SFT | 0002 a 0003 | Datasets de instrução, chat templates, loss masking em tokens que não são do assistente | Consegue escrever um loop de SFT com loss masking correto e explicar o que quebra sem ele |
| 3. Modelagem de recompensa | 0004 a 0005 | Coleta de dados de preferência, a loss de Bradley-Terry, reward hacking | Consegue treinar um reward model e identificar uma completion com reward hacking contra ele |
| 4. RLHF via PPO | 0006 a 0008 | O objetivo de RL, a penalidade de KL contra um modelo de referência, por que o PPO é caro e instável | Consegue derivar o objetivo do RLHF e dizer o que afrouxar a penalidade de KL faz com a policy |
| 5. Direct Preference Optimization | 0009 a 0010 | A recompensa implícita do DPO, o que ele deixa de fora em relação ao PPO e por que isso costuma ser aceitável | Consegue derivar a recompensa implícita do DPO e dizer o que ele abre mão em relação ao PPO |
| 6. GRPO e RL com recompensas verificáveis | 0011 a 0012 | Vantagem relativa ao grupo, por que ela serve a matemática e código | Consegue explicar a vantagem relativa ao grupo e por que uma recompensa verificável muda o que o RL pode ter como alvo |
| 7. Modelos de raciocínio | 0013 a 0014 | RL com chain-of-thought, o que o DeepSeek-R1 mudou, destilar um modelo de raciocínio para baixo | Consegue dizer como o comportamento de um modelo de raciocínio foi produzido, e não apenas como fazer prompt nele |
| 8. Segurança e ajuste de recusa | 0015 a 0016 | Dados de red-teaming, Constitutional AI, RLAIF | Consegue dizer de onde veio o feedback (humano ou de IA) em um dado pipeline de ajuste de segurança e o que isso implica em trocas |
| 9. Avaliando um modelo alinhado | 0017 a 0018 | Alignment tax, detecção de reward hacking, ligação com `llm/evals` | Consegue separar um ganho genuíno de capacidade de um artefato de reward hacking ou de viés do juiz |
| 10. Julgamento | 0019 a 0020 | DPO contra PPO contra GRPO para um dado orçamento, quando o SFT sozinho basta, revisar a receita de alinhamento de outra pessoa | Tem a confiança para tomar a decisão e explicá-la a outra pessoa |

## Lições

Siga estas na ordem.

| # | Lição | Ensina |
|---|---|---|
| [0001](lessons/0001-what-post-training-buys.md) | O que o pós-treinamento oferece | Um modelo alinhado 100 vezes menor superou um base model bruto em fazer o que os usuários de fato queriam |
| [0002](lessons/0002-instruction-data-and-the-chat-template.md) | Dados de instrução e o chat template | Um token especial marca onde um prompt termina e uma resposta começa, e essa fronteira precisa ser a mesma no treinamento e no serving |
| [0003](lessons/0003-loss-masking-on-non-assistant-tokens.md) | Loss masking em tokens que não são do assistente | Zere a loss no prompt, ou gaste sinal de gradiente ensinando o modelo a prever um texto que ele não gerou |
| [0004](lessons/0004-training-a-reward-model-the-bradley-terry-loss.md) | Treinando um reward model: a loss de Bradley-Terry | Um reward model nunca vê uma pontuação absoluta no treinamento, apenas qual de duas completions um humano preferiu |
| [0005](lessons/0005-reward-hacking.md) | Reward hacking | Uma policy aprendeu a dizer "Não posso responder isso" para quase tudo, porque isso pontuava bem sem ser genuinamente útil nem inofensivo |
| [0006](lessons/0006-the-rlhf-objective-reward-minus-a-kl-penalty.md) | O objetivo do RLHF: recompensa menos uma penalidade de KL | Um termo persegue a pontuação do reward model; um segundo termo é a coleira que impede a policy de fugir com ela |
| [0007](lessons/0007-ppo-why-the-update-gets-clipped.md) | PPO: por que a atualização é cortada | Uma grande vitória em um batch de dados amostrados não é evidência confiável para um grande passo; o PPO se recusa a acreditar totalmente nela |
| [0008](lessons/0008-why-ppo-is-expensive-and-unstable.md) | Por que o PPO é caro e instável | Quatro modelos, e não um, precisam caber na memória ao mesmo tempo, e os dois que escalam pior são exatamente os que o RLHF acrescenta |
| [0009](lessons/0009-dpos-implicit-reward-why-the-partition-function-cancels.md) | A recompensa implícita do DPO: por que a função de partição se cancela | Um termo normalizador intratável fica entre uma recompensa e a sua policy ótima, até que uma diferença de duas recompensas o faz desaparecer |
| [0010](lessons/0010-the-dpo-loss-and-what-it-drops-relative-to-ppo.md) | A loss do DPO e o que ela deixa de fora em relação ao PPO | Uma loss, dois modelos, nenhum loop de amostragem e o mesmo beta que uma penalidade de KL teria usado |
| [0011](lessons/0011-grpo-group-relative-advantage-instead-of-a-value-function.md) | GRPO: vantagem relativa ao grupo em vez de uma função de valor | Amostre várias respostas para a mesma pergunta e deixe a própria dispersão das recompensas do grupo dizer quais foram melhores |
| [0012](lessons/0012-verifiable-rewards-when-a-checker-replaces-the-reward-model.md) | Recompensas verificáveis: quando um verificador substitui o reward model | Um reward model treinado é um palpite sobre o que um humano preferiria; um teste unitário ou uma resposta que confere não é palpite nenhum |
| [0013](lessons/0013-chain-of-thought-rl-what-deepseek-r1-zero-did-with-rule-based-rewards.md) | RL com chain-of-thought: o que o DeepSeek-R1-Zero fez com recompensas baseadas em regras | Nenhum reward model aprendido, nenhum passo de SFT antes, e mesmo assim o raciocínio estendido surgiu porque continuava acertando mais respostas |
| [0014](lessons/0014-distilling-a-reasoning-model-down.md) | Destilando um modelo de raciocínio para baixo | Treinar um modelo de 32B diretamente com RL perdeu para simplesmente fazer fine-tuning dele nos próprios traces de raciocínio de um modelo maior |
| [0015](lessons/0015-constitutional-ai-feedback-from-a-model-not-a-human.md) | Constitutional AI: feedback de um modelo, não de um humano | Zero rótulos humanos para dano, uma lista escrita de princípios no lugar, e um assistente que explica as suas objeções em vez de se esquivar |
| [0016](lessons/0016-rlaif-how-well-ai-feedback-actually-matches-human-feedback.md) | RLAIF: o quanto o feedback de IA realmente se iguala ao feedback humano | Um modelo julgando as próprias saídas, no seu próprio tamanho, ainda superou o fine-tuning supervisionado simples |
| [0017](lessons/0017-measuring-the-alignment-tax.md) | Medindo o alignment tax | O imposto não aparece em todo lugar ao mesmo tempo, e um eixo chegou a medir uma melhora em vez disso |
| [0018](lessons/0018-reward-hacking-after-the-fact.md) | Reward hacking depois do fato | Um reward model held-out consegue pegar a deriva durante o treinamento; um modelo finalizado precisa de outro tipo de checagem |
| [0019](lessons/0019-choosing-between-sft-dpo-ppo-and-grpo.md) | Escolhendo entre SFT, DPO, PPO e GRPO | Cada método só merece o custo adicional em relação ao anterior quando o mais barato genuinamente não consegue expressar o comportamento-alvo |
| [0020](lessons/0020-reviewing-someone-elses-alignment-recipe.md) | Revisando a receita de alinhamento de outra pessoa | Percorra o pipeline por todas as etapas que esta trilha cobriu, em ordem, e resolva uma alegação contestada a partir da fonte, e não de uma reafirmação confiante |

## Referência

- [Glossário](GLOSSARY.md): termos canônicos deste tópico
- [Recursos](RESOURCES.md): fontes confiáveis

## Como isto funciona

Cada lição é curta e autocontida. Os gabaritos ficam recolhidos: primeiro lembre, depois abra. A prática no mundo real importa mais do que a leitura, e espaçá-la é o ponto. Tudo o que ainda estiver confuso no fim de uma lição vale ser perseguido até a fonte primária antes de seguir adiante.
