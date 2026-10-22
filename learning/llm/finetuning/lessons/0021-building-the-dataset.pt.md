---
title: "21. Construindo o dataset"
description: "Os dados vencem todo hiperparâmetro deste workspace"
type: lesson
---

# Lição 21. Construindo o dataset

**Ligação com a missão:** A qualidade dos dados domina todo hiperparâmetro deste workspace. A etapa 3 ensinou você a girar um botão; esta etapa ensina o que de fato move o resultado.
**Fonte principal:** [Artigo científico: "LIMA: Less Is More for Alignment", Zhou et al., arXiv:2305.11206](https://arxiv.org/abs/2305.11206)
**Pré-requisitos:** [Lição 3](0003-tokenizers-and-chat-templates.md), [Lição 12](0012-reading-a-training-run.md)

## Aquecimento

1. ▢ Qual é a verificação de maior valor a executar antes de um trabalho de treinamento?

<details markdown="1"><summary>Verificação</summary>

Decodificar um exemplo de treinamento real e lê-lo, contando posições pontuadas versus mascaradas. Ela pega de uma vez incompatibilidade de template, tokens de fim de turno ausentes, bugs de mascaramento e truncamento.

</details>

2. ▢ O que significa uma curva de loss em escada com quedas nas fronteiras de epoch?

<details markdown="1"><summary>Verificação</summary>

Memorização: o modelo está reconhecendo exemplos que já viu.

</details>

3. ▢ Qual variante de loss o instruction tuning normalmente deve usar?

<details markdown="1"><summary>Verificação</summary>

Apenas da completion. As posições do prompt são mascaradas com `-100` para que só a resposta do assistant seja pontuada.

</details>

## Saiba isto

### A razão incômoda

Se você tem pouco tempo, gaste-o com os dados. A distância entre um dataset medíocre e um bom é maior do que a distância entre rank 8 e rank 128, maior do que LoRA versus DoRA, e maior do que a maioria das coisas que você poderia ajustar. Os hiperparâmetros são legíveis e satisfatórios de ajustar, e é por isso que absorvem atenção fora de proporção ao seu efeito.

O resultado do LIMA é a declaração publicada mais incisiva disso: um pequeno número de exemplos cuidadosamente curados, da ordem de mil, produziu um seguimento de instruções forte, sustentando a visão de que o supervised fine-tuning ensina principalmente *formato e estilo*, enquanto a capacidade vem do pré-treinamento. Trate o número exato como específico do cenário; leve a direção a sério.

### O que o fine-tuning ensina bem, e mal

| Ensina bem | Ensina mal |
|---|---|
| Formato e estrutura de saída | Fatos novos sobre o mundo |
| Tom, registro, voz do domínio | Capacidade de raciocínio que ainda não existe |
| Adesão consistente a um schema | Qualquer coisa que exija informação atual |
| Classificação e extração estreitas | Conhecimento de cauda longa com uma única menção |
| Sintaxe de chamadas de ferramenta e de função | Aritmética e cálculo preciso |

A coluna da direita é o motivo de a [Lição 27](0027-when-not-to-fine-tune.md) existir. Um dataset construído para instalar fatos está fazendo aquilo em que o fine-tuning é pior, e cada fato precisaria de muitos exemplos variados para fixar, ponto em que a recuperação é mais barata, mais precisa e atualizável.

### Projetando exemplos

**Combine com a distribuição de implantação.** Suas entradas de treinamento devem se parecer com entradas reais. Prompts de treinamento limpos, bem formados e de comprimento uniforme produzem um modelo que se degrada diante da realidade bagunçada que ele encontra em produção, e a sua divisão held-out, tirada do mesmo conjunto limpo, não vai avisar.

**Inclua os casos difíceis de propósito.** Entradas ambíguas, casos extremos e os casos em que a resposta correta é uma recusa ou "informação insuficiente". Se toda resposta de treinamento é confiante e completa, você treinou confiança e completude, inclusive em entradas que não as justificam.

**Seja consistente no formato.** Se metade dos seus exemplos termina com ponto e metade não, o modelo aprende a inconsistência. Toda variação arbitrária que você deixa é capacidade gasta com ruído.

**Faça as saídas serem exemplares.** O modelo imita os seus alvos. Um dataset de respostas adequadas produz respostas adequadas, e nenhum hiperparâmetro se recupera disso.

**Varie a superfície, e não a substância.** Várias formulações do mesmo pedido ensinam robustez à formulação. Vários exemplos quase idênticos ensinam memorização.

### Deduplicação

As quase duplicatas são o defeito sério mais comum em datasets montados, e causam dois danos ao mesmo tempo: dar peso excessivo ao que o conteúdo duplicado ensina e, se as duplicatas caem dos dois lados da sua divisão, uma pontuação held-out que mede recordação e não generalização.

A deduplicação por correspondência exata não basta. Use hashing normalizado e depois uma medida de similaridade como MinHash ou distância de embeddings para as quase duplicatas. Faça isso *antes* de dividir, e não depois.

### Tamanho e balanceamento

Uma orientação aproximada, e não uma regra:

| Exemplos | Alvo realista |
|---|---|
| 50 a 200 | Estilo, tom, um formato de saída fixo |
| 500 a 2,000 | Uma tarefa bem definida de escopo estreito |
| 5,000 a 50,000 | Uma tarefa ampla, ou várias capacidades ao mesmo tempo |
| 100,000+ | Retornos decrescentes para adapters; considere se a tarefa é mesmo uma só |

Onde existem categorias, o desbalanceamento vira um viés. Um dataset com 90% de uma classe ensina o modelo a chutar essa classe. Balanceie-o ou leve o desbalanceamento em conta na sua métrica, conforme a Lição 23.

### Dados sintéticos

Gerar dados de treinamento com um modelo mais forte é padrão, eficaz e tem dois riscos específicos.

**Erros herdados.** Os erros e vieses do gerador viram os seus alvos de treinamento, e serão fluentes e consistentes, o que os torna difíceis de perceber ao dar uma passada de olho. Amostre e leia.

**Colapso de distribuição.** Dados gerados tendem a ser mais uniformes do que dados reais: estruturas parecidas, comprimentos parecidos, registro parecido. Você treina um modelo que lida bem com uma fatia estreita e mal com a variação real. Parta de entradas reais na geração sempre que puder e varie os prompts de propósito.

Além disso: confira a licença e os termos do modelo de que você gera. Saber se as saídas podem ser usadas para treinar outro modelo é uma restrição real, não uma formalidade.

### Formatação

Acerte a mecânica, uma vez:

- Renderize pelo próprio chat template do modelo (Lição 3). Verifique com `repr`.
- Mascare as posições do prompt, a menos que você queira de propósito que sejam pontuadas.
- Inclua o token de fim de turno, ou o modelo não vai aprender a parar.
- Confira a distribuição de comprimento em tokens e defina o `max_length` a partir do seu percentil alto, e não do máximo nem de um chute.
- Confirme que o truncamento não está cortando respostas ao meio. Um alvo truncado em silêncio ensina o modelo a parar no meio da frase.

## Prática

1. ▢ Você quer que o modelo conheça os 400 SKUs de produtos da sua empresa. Um dataset de fine-tuning é a ferramenta certa?

<details markdown="1"><summary>Verificação</summary>

Não. Isso são fatos, que o fine-tuning instala de forma pouco confiável: cada um precisaria de muitos exemplos variados, e o resultado é inverificável e desatualizado no instante em que o catálogo muda.

A recuperação é a ferramenta certa: precisa, citável e atualizada editando um documento em vez de retreinar. O que o fine-tuning *poderia* ensinar de útil aqui é o formato para apresentar informações de produto.

</details>

2. ▢ Todos os seus prompts de treinamento são frases limpas e bem pontuadas. As entradas de produção são lacônicas e cheias de erros de digitação. O que acontece, e por que o seu conjunto held-out não vai pegar isso?

<details markdown="1"><summary>Verificação</summary>

O modelo vai bem em entrada limpa e se degrada em entrada real, porque nunca viu entrada real.

A sua divisão held-out é tirada do mesmo conjunto limpo, então compartilha o defeito. Ela mede o desempenho na distribuição errada e reporta sucesso. A correção é dados de treinamento e de avaliação tirados do tráfego real de implantação.

</details>

3. ▢ Por que deduplicar antes de dividir, e não depois?

<details markdown="1"><summary>Verificação</summary>

Porque um par duplicado atravessando a divisão coloca um exemplo de treinamento no conjunto held-out. O desempenho held-out passa a medir memorização e a reportá-la como generalização, que é a forma mais eficaz de se enganar sobre um fine-tune.

Deduplicar depois da divisão deixa intactos os pares entre as divisões, que é exatamente o caso que importa.

</details>

4. ▢ Qual defeito de dataset tem mais chance de produzir um modelo que nunca diz "não sei"?

    - a) Um desbalanceamento de classes que favorece fortemente uma categoria
    - b) Cada uma das respostas ser confiante e completa
    - c) Exemplos quase duplicados aparecendo dos dois lados da divisão
    - d) Uma distribuição de comprimento em tokens com cauda muito longa

<details markdown="1"><summary>Verificação</summary>

**b)** Cada uma das respostas ser confiante e completa.

O modelo imita os seus alvos. Sem nenhum exemplo de incerteza ou recusa apropriada, confiança e completude são o único comportamento que lhe foi mostrado, inclusive para entradas que não as sustentam.

</details>

5. ▢ Nomeie os dois riscos dos dados sintéticos e uma mitigação para cada um.

<details markdown="1"><summary>Verificação</summary>

Erros herdados: os erros do gerador viram alvos de treinamento fluentes e consistentes. Mitigue amostrando e lendo uma fração real, e validando contra a verdade de referência onde houver alguma.

Colapso de distribuição: os dados gerados são mais uniformes do que os reais. Mitigue partindo de entradas reais na geração e variando os prompts de geração de propósito.

</details>

6. ▢ Os comprimentos em tokens do seu dataset vão de 50 a 8000, com o percentil 95 em 1200. Qual `max_length` você define, e o que você confere?

<details markdown="1"><summary>Verificação</summary>

Em torno de 1200 a 1500. Definir 8000 desperdiça memória de ativações com padding em quase todo exemplo; definir 512 trunca uma fração substancial.

Depois confira o que o truncamento de fato faz aos exemplos acima do limite. Se corta respostas ao meio, você está ensinando o modelo a parar no meio da frase, então ou aumente o limite ou descarte esses exemplos de propósito.

</details>

## Prática no mundo real

- [ ] Leia vinte exemplos do seu dataset por inteiro, decodificados pelo chat template. Anote cada inconsistência que encontrar.
- [ ] Execute a detecção de quase duplicatas no conjunto inteiro antes de dividir. Registre quantas encontrou e remova-as.
- [ ] Trace a distribuição de comprimento em tokens e escolha o `max_length` a partir dela. Inspecione três exemplos que seriam truncados.
- [ ] Amanhã: adicione dez exemplos deliberadamente difíceis: ambíguos, de casos extremos, ou em que a resposta certa é uma recusa.

## Para ir além

- [Artigo científico: "LIMA: Less Is More for Alignment", Zhou et al., arXiv:2305.11206](https://arxiv.org/abs/2305.11206)
- [Docs: Dataset formats, Hugging Face TRL](https://huggingface.co/docs/trl/main/en/dataset_formats)
- [Lição 22. Contaminação e design de dados held-out](0022-contamination-and-held-out-design.md)

---

Não ficou claro? Releia a fonte principal no topo, já que esta lição a comprime e é na compressão que o entendimento escapa. Consulte o [glossário](../GLOSSARY.md) para qualquer termo que pareceu escorregadio.

Se o problema é a lição em si, e não o material, isso é um defeito: [abra uma issue](https://github.com/TokenCemetery/teach/issues).
