---
title: "15. GKD e MiniLLM"
description: "Amostrar do aluno e pontuar com o professor, e as escolhas de divergência e de mistura que vêm junto"
type: lesson
---

# Lição 15. GKD e MiniLLM

**Ligação com a missão:** A missão pede que você execute a destilação on-policy e escolha as suas configurações, o que exige saber o que os dois botões do GKD fazem, o que o MiniLLM faz de diferente e quais resultados vieram de qual tarefa.
**Fonte principal:** [Artigo científico: "On-Policy Distillation of Language Models: Learning from Self-Generated Mistakes", Agarwal et al., 2023](https://arxiv.org/abs/2306.13649), seções 2 a 4
**Pré-requisitos:** [Lição 5](0005-forward-and-reverse-kl.md), [Lição 14](0014-exposure-bias.md), [Generalized knowledge distillation](../GLOSSARY.md), [Destilação on-policy](../GLOSSARY.md), [Reverse KL](../GLOSSARY.md)

## Aquecimento

1. ▢ Em quais sequências um passo de destilação on-policy treina, e qual modelo as decide?

<details markdown="1"><summary>Verificação</summary>

Em sequências que o aluno gera durante o treinamento, então o aluno as decide. O professor apenas pontua cada token que o aluno escolheu. Treinar em sequências fixas, sejam humanas ou escritas pelo professor, é [off-policy](../GLOSSARY.md).

</details>

2. ▢ O forward KL empurra o aluno a cobrir todos os modos do professor e o reverse KL o empurra a se comprometer com um. Qual dos dois corre o risco de pôr probabilidade em texto que o professor considera improvável?

<details markdown="1"><summary>Verificação</summary>

O forward KL, porque ele penaliza deixar de cobrir qualquer região que o professor cobre, então um aluno pequeno se estica sobre regiões que não consegue modelar bem. O reverse KL penaliza probabilidade onde o professor tem pouca, então evita isso ao custo da diversidade.

</details>

3. ▢ Qual é a diferença entre o exposure bias e um aluno simplesmente ser pequeno demais?

<details markdown="1"><summary>Verificação</summary>

O exposure bias é sobre os prefixos: o aluno treina em prefixos que outra pessoa escreveu e gera a partir dos seus. Um aluno pequeno demais tem um limite de capacidade sobre o que consegue representar, que permaneceria mesmo que todo prefixo fosse o seu. O treinamento on-policy trata o primeiro e não consegue remover o segundo.

</details>

## Saiba isto

### GKD: um loop com dois botões

A generalized knowledge distillation (GKD) é um algoritmo com dois hiperparâmetros (Agarwal et al., Algoritmo 1). A cada passo ele sorteia um número aleatório. Com probabilidade lambda, ele gera sequências a partir do aluno para um batch de prompts. Caso contrário, pega um batch de um dataset fixo de sequências de verdade de referência ou escritas pelo professor. Depois atualiza o aluno para minimizar uma divergência entre as distribuições de tokens do professor e do aluno, tirando a média sobre as posições, sem gradiente através da amostragem.

Lambda é a **fração de dados do aluno**. Lambda 0 é a destilação supervisionada comum e lambda 1 é puramente on-policy. As variantes "mistas" do artigo usam 0,5. Durante o treinamento, o aluno amostra com temperatura 1 para manter as suas sequências diversas.

O segundo botão é a divergência. O GKD usa a divergência de Jensen-Shannon generalizada, JSD(beta), uma mistura limitada das duas direções do KL. Com a convenção do artigo, beta perto de 0 se comporta como o forward KL e beta perto de 1 como o reverse KL, então 0,1, 0,5 e 0,9 são pontos ao longo dessa linha. O trainer do TRL documenta a mesma direção: beta 0.0 aproxima o forward KL e beta 1.0 o reverse KL.

### O que o artigo encontrou, tarefa por tarefa

Os alunos têm T5-small (77M), T5-base (250M) e T5-large (800M) parâmetros, destilados de um T5-XL com fine-tuning de cerca de 3B, então o professor é 38 vezes, 12 vezes e 3,8 vezes maior. Os resultados são do próprio artigo em T5, não fatos gerais sobre LLMs.

| Tarefa | Métrica | O que funcionou | Fonte no artigo |
|---|---|---|---|
| Resumo XSum | ROUGE-2 | O GKD on-policy com JSD(0.9) superou os baselines adicionais ImitKD e f-distill com decodificação greedy e com amostragem por temperatura. As divergências que buscam modos se saíram melhor com amostragem por temperatura, e a divergência importou pouco com decodificação greedy | Seção 4.1, Figuras 3 e 4 |
| WMT14 inglês para alemão | BLEU | A JSD generalizada superou o forward e o reverse KL, com uma diferença menor para o aluno maior. Apenas dados gerados pelo aluno superaram as outras misturas de dados. A Figura 1 usou JSD(0.1) | Seção 4.2, Figura 6 |
| GSM8K com chain of thought | acurácia | Apenas cadeias geradas pelo aluno superaram dados fixos ou mistos. O forward KL se saiu bem, e o reverse KL também. Os ganhos se mantiveram quando pelo menos 25% dos dados eram on-policy | Seção 4.3, Figuras 8 e 9 |
| Instruction tuning no FLAN | MMLU e BBH held-out | O GKD on-policy com reverse KL superou claramente o forward KL | Seção 4.4, Figura 10 |

O resumo dos autores é que a melhor divergência depende da tarefa, enquanto os dados on-policy e mistos superam consistentemente os dados fixos. Dois outros resultados valem ser conhecidos. No XSum com T5-small, o GKD on-policy em uma subamostra de 5%, sem resumos de verdade de referência, superou o KD supervisionado e o ImitKD treinados no dataset completo (seção 4.1). Tirada a média sobre os tamanhos de aluno, os ganhos de desempenho sobre o aluno inicial foram 2,1 vezes os do KD baseline em resumo, 1,7 vezes em tradução e 1,9 vezes em raciocínio aritmético (Introdução).

Para o instruction tuning, o texto do artigo e a legenda da sua Figura 10 discordam sobre se o aluno é T5-base ou T5-large, então esta lição não cita um tamanho de aluno para essa tarefa. O professor chegou a 52,4% no MMLU e 41% no BBH. Os autores levantam a hipótese de que o reverse KL funciona ali porque a sua natureza de buscar modos faz o modelo se concentrar na intenção principal da instrução, e a apresentam como hipótese, não como achado.

### MiniLLM: reverse KL otimizado como uma política

Gu et al. (MiniLLM) chegam ao treinamento on-policy por outra direção. Eles argumentam que o forward KL faz um aluno de baixa capacidade superestimar regiões de baixa probabilidade do professor e, em vez disso, minimizam o reverse KL sobre sequências inteiras. Como a esperança é sob a própria distribuição do aluno, eles derivam o gradiente com o teorema do policy gradient e o treinam como reinforcement learning, com o log da razão entre as probabilidades do professor e do aluno como sinal por token.

O policy gradient simples tem problemas, e o artigo acrescenta três correções:

| Problema | Correção | Detalhe |
|---|---|---|
| Alta variância | Decomposição em passo único | O termo por token é calculado somando sobre o vocabulário em vez de amostrando |
| Reward hacking: texto degenerado, como frases repetidas, pontua bem com o professor | Amostragem mista com o professor | Amostrar de alpha vezes o professor mais (1 menos alpha) vezes o aluno a cada passo, com alpha 0,2 nos experimentos |
| Saídas longas recebem pequenas recompensas acumuladas, então o aluno aprende a produzir respostas muito curtas ou vazias | Normalização por comprimento | Normalizar a recompensa acumulada pelo comprimento restante |

Ele também acrescenta clipping e uma loss de language modeling em texto de pré-treinamento para manter o desempenho nos benchmarks gerais. O treinamento começa de um aluno com fine-tuning nos dados da tarefa. Note a diferença em relação ao GKD: as amostras do MiniLLM vêm em parte do professor por meio da mistura, então ele não é puramente on-policy, e otimiza um objetivo em nível de sequência onde o GKD tira a média de uma divergência em nível de token.

### Resultados do MiniLLM

O cenário é seguimento de instruções em 15K exemplos do Dolly, cerca de 12,5K para treinamento, com alunos do GPT-2 (120M a 760M, professor GPT-2 1,5B), OPT (1,3B a 6,7B, professor OPT 13B) e LLaMA (7B, professor LLaMA 13B). Algumas células da Tabela 1, a pontuação média de feedback do GPT-4 no DollyEval:

| Aluno | Só fine-tuning | KD padrão | SeqKD | MiniLLM | Professor |
|---|---|---|---|---|---|
| OPT 1.3B | 52,6 | 52,7 | 51,0 | 60,7 | 70,3 |
| OPT 6.7B | 67,9 | 68,6 | 69,6 | 70,8 | 70,3 |
| LLaMA 7B | 73,0 | 73,7 | 73,6 | 76,4 | 79,0 |

A métrica do GPT-4 é a razão entre a pontuação do GPT-4 para a resposta do modelo e a sua pontuação para a resposta de referência, então é relativa, não absoluta. Os autores também relatam que os alunos às vezes superam o professor no Rouge-L e conjecturam que isso reflete exposure bias no professor. Quanto à calibração, o MiniLLM aluno teve erro menor do que os baselines com forward KL, mas ainda acima do professor: no SST2, ECE de 0,099 contra 0,025 do professor e 0,191 do KD padrão (Tabela 2).

### O que você não pode concluir

Cada artigo ajustou o seu próprio método nos seus próprios alunos, professores e métricas, então os números acima não classificam o GKD contra o MiniLLM. Não encontrei comparação direta em nenhum dos artigos. Compare as ideias deles e teste as duas no seu próprio par.

### Uma configuração executável

O `GKDTrainer` do TRL expõe os dois botões como `lmbda` e `beta` no `GKDConfig`. Os seus padrões documentados são 0.5 para cada um, com `temperature` 0.9 e `max_new_tokens` 128 para a geração, e `seq_kd` desligado. O exemplo da documentação abaixo destila o Qwen2-1.5B-Instruct no Qwen2-0.5B-Instruct. Eu não o executei, então confira o caminho de import contra a versão do TRL que você instalar, já que a documentação atual coloca o GKD em `trl.experimental`.

```python
from datasets import Dataset
from transformers import AutoModelForCausalLM, AutoTokenizer
from trl.experimental.gkd import GKDConfig, GKDTrainer

tokenizer = AutoTokenizer.from_pretrained("Qwen/Qwen2-0.5B-Instruct")
student = AutoModelForCausalLM.from_pretrained("Qwen/Qwen2-0.5B-Instruct")
teacher = AutoModelForCausalLM.from_pretrained("Qwen/Qwen2-1.5B-Instruct")

train = Dataset.from_dict({"messages": [[
    {"role": "user", "content": "Hi, how are you?"},
    {"role": "assistant", "content": "I'm great thanks"},
]] * 100})

args = GKDConfig(
    output_dir="gkd-model",
    per_device_train_batch_size=1,
    lmbda=1.0,  # purely on-policy: every batch is student-generated
    beta=1.0,   # generalized JSD at the reverse-KL end
)
trainer = GKDTrainer(model=student, teacher_model=teacher, args=args,
                     processing_class=tokenizer, train_dataset=train)
trainer.train()
```

Os dois modelos compartilham um tokenizer porque são da mesma família, o que a lição 6 explicou ser exigido para a destilação de logits. A própria orientação da página do TRL combina com o artigo: dados on-policy (`lmbda` alto) têm desempenho melhor, e o melhor `beta` depende da tarefa e do método de avaliação.

## Prática

1. ▢ No GKD, quais configurações de lambda e da divergência reproduzem (a) a destilação supervisionada e (b) o KD on-policy como o artigo os define?

<details markdown="1"><summary>Verificação</summary>

Ambos usam forward KL. Lambda 0 dá o KD supervisionado, em que o aluno nunca gera, e lambda 1 dá o KD on-policy, em que toda sequência é do aluno. Os valores intermediários são as variantes mistas. A divergência e a fonte dos dados são botões independentes, e é por isso que o mesmo forward KL aparece nos dois.

</details>

2. ▢ No experimento de instruction tuning do GKD no FLAN, qual combinação o artigo constatou ser claramente melhor do que a sua contraparte com forward KL?

    - a) Forward KL, amostras do aluno
    - b) Reverse KL, amostras do aluno
    - c) Forward KL, sequências fixas
    - d) Reverse KL, sequências fixas

<details markdown="1"><summary>Verificação</summary>

**b)** O GKD on-policy com reverse KL superou as outras abordagens na seção 4.4. (a) é a escolha do artigo para o XSum e o GSM8K com decodificação greedy, não para o instruction tuning. (c) e (d) usam dados fixos, que o artigo constatou serem consistentemente mais fracos do que dados gerados pelo aluno.

</details>

3. ▢ Associe cada correção do MiniLLM à falha que ela previne: (1) amostragem mista com o professor, (2) normalização por comprimento, (3) decomposição em passo único. Falhas: A, o aluno devolve respostas muito curtas ou vazias. B, alta variância no gradiente. C, o aluno encontra texto degenerado que o professor pontua bem.

<details markdown="1"><summary>Verificação</summary>

(1) vai com C, (2) com A, (3) com B. A amostragem mista com o professor suprime amostras degeneradas misturando o professor na distribuição de amostragem. A normalização por comprimento impede que sequências longas sejam penalizadas por pequenas recompensas acumuladas. A decomposição em passo único calcula o termo por token sobre todo o vocabulário em vez de amostrando, o que reduz a variância.

</details>

4. ▢ Um aluno treinado com um objetivo ao estilo MiniLLM começa a emitir uma frase repetida à qual o professor atribui alta probabilidade. Qual truque ataca isso, e que valor o artigo usou?

<details markdown="1"><summary>Dica</summary>

A pontuação do professor é a recompensa. Uma amostra degenerada de que o professor gosta está explorando essa recompensa.

</details>

<details markdown="1"><summary>Verificação</summary>

A amostragem mista com o professor, que o artigo introduz contra o reward hacking, com alpha 0,2 em todos os seus experimentos (seção 3.1). O valor é a escolha daquele artigo no seu cenário, então trate-o como um ponto de partida, não como uma constante.

</details>

5. ▢ Usando a Tabela 1 acima, que parcela da distância entre o aluno só com fine-tuning e o professor o MiniLLM fecha para o OPT 1.3B e para o LLaMA 7B? O que você não pode concluir da linha do OPT 6.7B?

<details markdown="1"><summary>Verificação</summary>

OPT 1.3B: a distância é 70,3 menos 52,6, que dá 17,7, e o MiniLLM ganha 8,1, cerca de 46%. LLaMA 7B: a distância é 6,0 e o MiniLLM ganha 3,4, cerca de 57%. Na linha do OPT 6.7B, o MiniLLM pontua 70,8 contra 70,3 do professor, mas isso não mostra que o aluno é melhor: a métrica é relativa às respostas de referência, a diferença é de meio ponto e é um par de modelos.

</details>

6. ▢ Você quer uma execução puramente on-policy com reverse KL no TRL. Quais dois valores de configuração você define, e você conseguiria rodá-la se tivesse apenas o texto do professor?

<details markdown="1"><summary>Verificação</summary>

`lmbda=1.0` e `beta=1.0`. Não: a divergência precisa da distribuição do professor em cada posição da sequência do aluno, então você precisa do próprio modelo professor, não de um dump de texto armazenado. Só com texto você voltaria ao nível de sequência (lição 8). A opção `seq_kd` do TRL não muda isso, já que o professor ainda dá feedback específico por token.

</details>

## Prática no mundo real

- [ ] Leia a seção 3.1 do artigo do GKD. Escreva a loss em uma linha e depois circule onde lambda e a divergência entram, cada um.
- [ ] Abra a Tabela 1 do artigo do MiniLLM e escolha um aluno em que o MiniLLM não superou o professor em todas as colunas. Escreva em qual métrica ele perdeu e por quanto.
- [ ] Amanhã: sem consultar anotações, escreva o que lambda e beta controlam, cite uma tarefa em que o reverse KL venceu no GKD e nomeie as três correções do MiniLLM.

## Para ir além

- [Destilação On-Policy](../reference/on-policy-distillation.md)
- [Artigo científico: "On-Policy Distillation of Language Models: Learning from Self-Generated Mistakes", Agarwal et al., 2023](https://arxiv.org/abs/2306.13649)
- [Artigo científico: "MiniLLM: On-Policy Distillation of Large Language Models", Gu et al., 2023](https://arxiv.org/abs/2306.08543)
- [Documentação: "Generalized Knowledge Distillation Trainer", Hugging Face TRL](https://huggingface.co/docs/trl/main/en/gkd_trainer)
- [Recursos](../RESOURCES.md)

---

Não ficou claro? Releia a fonte principal no topo, já que esta lição a comprime e é na compressão que o entendimento escapa. Consulte o [glossário](../GLOSSARY.md) para qualquer termo que pareceu escorregadio.

Se o problema é a lição em si, e não o material, isso é um defeito: [abra uma issue](https://github.com/TokenCemetery/teach/issues).
