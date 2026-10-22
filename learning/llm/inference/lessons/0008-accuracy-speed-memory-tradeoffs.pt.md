---
title: "8. Trade-offs entre acurácia, velocidade e memória"
description: "Por que memória, velocidade e acurácia não se movem juntas quando um modelo é quantizado, e como cada uma é realmente medida"
type: lesson
---

# Lição 8. Trade-offs entre acurácia, velocidade e memória

**Ligação com a missão:** A lição 7 nomeou os esquemas; esta lição é o que torna defensável uma escolha de quantização, porque memória, velocidade e acurácia se movem, cada uma, por uma quantidade diferente e por um motivo diferente quando os pesos são quantizados.
**Fonte principal:** [Artigo científico: "GPTQ: Accurate Post-Training Quantization for Generative Pre-trained Transformers", Frantar et al., 2023](https://arxiv.org/abs/2210.17323)
**Pré-requisitos:** [Lição 7](0007-quantization-schemes.md), [KV cache](../GLOSSARY.md)

## Aquecimento

1. ▢ Por que quantizar os pesos de um modelo acelera especificamente o decode, e não a inferência em geral?

<details markdown="1"><summary>Verificação</summary>

O decode é limitado pela largura de banda de memória: cada passo lê os pesos de volta da memória, e quantizá-los reduz quantos bytes essa leitura precisa mover. O ganho de velocidade vem de menos tráfego de memória por passo, o gargalo exato que o decode tem.

</details>

2. ▢ Aproximadamente que fração da memória dos pesos em fp16 a quantização int4 usa?

<details markdown="1"><summary>Verificação</summary>

Cerca de um quarto: o int4 empacota dois pesos por byte onde o fp16 usava dois bytes por peso, uma redução de 4x, que é metade do tamanho do int8.

</details>

## Saiba isto

### A memória é a mais previsível das três

A economia de memória da quantização é quase aritmética: o int8 reduz a pegada do fp16 à metade, o int4 a um quarto, porque a largura de bits define diretamente quantos bytes um peso ocupa. Este é o único eixo a que os números da lição 7 se aplicam de forma limpa, e vale independentemente de qual esquema, arredondamento ingênuo, GPTQ ou AWQ, produziu os pesos quantizados.

### A velocidade não segue a mesma razão

Um peso quantizado muitas vezes precisa ser **dequantizado** de volta para uma precisão maior imediatamente antes de a multiplicação de matrizes de fato rodar, porque o hardware de multiplicação espera essa precisão. Quando esse próprio passo de dequantização custa tempo, o ganho de velocidade em tempo real pode ficar bem aquém da razão de economia de memória: um peso 4x menor não significa automaticamente um passo 4x mais rápido, apenas um passo com 4x menos dados para mover, antes de qualquer overhead que dequantizá-lo acrescente. As stacks de serving fecham essa lacuna com kernels escritos para operar diretamente sobre o formato quantizado, mas quanto do ganho teórico de memória sobrevive depende do kernel, e não apenas da largura de bits.

A velocidade também não se beneficia por igual ao longo de uma requisição. O decode, por ser limitado pela largura de banda de memória, é onde uma pegada de pesos menor compensa: menos a ler, menos tempo gasto lendo. O prefill, por ser limitado por compute (lição 3), gasta o seu tempo na própria multiplicação de matrizes, e não em ler pesos repetidamente, então a mesma quantização que acelera de forma significativa o decode rende muito menos ao prefill, às vezes quase nada.

### A acurácia precisa de um número, não de uma impressão

Um modelo quantizado produzindo texto com aparência plausível não é evidência de que a sua acurácia se manteve: fluência é barata, e um modelo pode parecer coerente e ainda assim estar mensuravelmente pior do que o seu original em fp16 na tarefa que importa. A perda de acurácia da quantização é medida, tipicamente como **perplexidade** (quão bem o modelo prevê texto held-out; maior significa pior) em um conjunto de avaliação padrão, ou como a mudança de pontuação em um benchmark específico da tarefa com que a carga de trabalho realmente se importa. A própria avaliação do GPTQ relata exatamente isso: a perplexidade medida contra o modelo não quantizado em cada largura de bits, e não uma leitura qualitativa de saídas de exemplo.

### Os três eixos fazem trade-off, mas não em sincronia

Ir de fp16 para int8 costuma custar muito pouca acurácia medida para uma redução à metade completa da memória. Ir de int8 para int4 compra outra grande redução de memória, mas costuma custar desproporcionalmente mais acurácia do que o passo para int8 custou, e é exatamente por isso que GPTQ e AWQ existem: para manter esse custo de acurácia do int4 tão pequeno quanto o arredondamento ingênuo não consegue. Nenhum dos três eixos é gratuito, e nenhum escala com os outros em uma razão fixa, e é por isso que uma escolha defensável precisa de um número para cada um, e não da suposição de que reduzir um reduz os outros na mesma proporção.

## Prática

1. ▢ Uma equipe quantiza um modelo para int4 e observa que ele ainda escreve texto fluente e coerente em um punhado de prompts manuais. Isso é evidência suficiente de que a quantização não prejudicou a acurácia? Por que sim ou por que não?

<details markdown="1"><summary>Verificação</summary>

Não. Fluência não é o mesmo que correção ou acurácia na tarefa; um modelo pode parecer coerente e ainda assim pontuar mensuravelmente pior em perplexidade ou em um benchmark de tarefa. A perda de acurácia precisa de um número medido, como a perplexidade contra o modelo não quantizado ou a variação da pontuação em um benchmark, e não de uma leitura qualitativa de algumas saídas.

</details>

2. ▢ Um modelo é quantizado para int4, dando uma redução teórica de memória de 4x em relação ao fp16. Por que o ganho medido de velocidade no decode poderia ser menor que 4x?

<details markdown="1"><summary>Dica</summary>

Pense no que precisa acontecer com um peso quantizado imediatamente antes da multiplicação de matrizes que o usa.

</details>

<details markdown="1"><summary>Verificação</summary>

Os pesos quantizados muitas vezes precisam ser dequantizados de volta para uma precisão maior logo antes de a multiplicação rodar, já que o hardware de multiplicação espera essa precisão. Se esse passo de dequantização em si leva tempo, ele consome o ganho que a pegada de memória menor compraria, então o ganho em tempo real pode ficar aquém da razão de memória, a menos que o kernel opere diretamente sobre o formato quantizado.

</details>

3. ▢ A mesma quantização int4 é aplicada à fase de prefill e à fase de decode de uma requisição. Qual fase vê o maior ganho de velocidade, e por quê?

<details markdown="1"><summary>Verificação</summary>

O decode. Ele é limitado pela largura de banda de memória, então ler uma pegada de pesos menor encurta diretamente o passo. O prefill é limitado por compute: o seu tempo é dominado pela própria multiplicação de matrizes, e não pela leitura dos pesos, então a mesma redução de memória rende muito menos ganho, às vezes quase nenhum.

</details>

4. ▢ Qual afirmação é verdadeira sobre o trade-off entre acurácia, velocidade e memória ao passar de int8 para int4?

    - a) Os três melhoram pelo mesmo fator, já que os dois são passos de 8 bits abaixo do fp16
    - b) A memória melhora de forma previsível, mas o ganho de velocidade e o custo de acurácia não escalam com ela na mesma razão
    - c) Velocidade e memória melhoram juntas, e a acurácia não é afetada abaixo de 8 bits
    - d) A perda de acurácia é fixa, independentemente da largura de bits, então só memória e velocidade fazem trade-off

<details markdown="1"><summary>Verificação</summary>

**b)** A memória cai por uma razão previsível, aritmética, mas o ganho de velocidade em tempo real depende do overhead de dequantização e do suporte do kernel, e o custo de acurácia tipicamente cresce mais rápido do que no passo para int8. (a) é falsa: de int8 para int4 é um passo, e não dois passos iguais de 8 bits, e os ganhos não são uniformes entre os eixos. (c) é falsa: a perda de acurácia do int4 é mensurável e normalmente maior que a do int8, e é por isso que GPTQ e AWQ existem. (d) é falsa: a perda de acurácia geralmente cresce conforme a largura de bits cai; ela não é fixa.

</details>

## Prática no mundo real

- [ ] Encontre um benchmark publicado que compare a perplexidade ou a pontuação em tarefa de um modelo em fp16, int8 e int4 (um model card ou a tabela de avaliação de um artigo) e anote quanto cada passo realmente custou, nos números do próprio artigo.
- [ ] Encontre a página de benchmark ou de documentação da sua stack de serving que compare o throughput medido em diferentes níveis de quantização e compare o ganho de velocidade reportado com a razão teórica de memória que você esperaria.
- [ ] Amanhã: para uma carga de trabalho que você tenha em mente, escreva qual métrica de acurácia você realmente verificaria antes de enviar um modelo quantizado para produção, e que queda de pontuação você consideraria aceitável.

## Para ir além

- [Artigo científico: "GPTQ: Accurate Post-Training Quantization for Generative Pre-trained Transformers", Frantar et al., 2023](https://arxiv.org/abs/2210.17323)
- [Documentação: "Optimizing inference", Hugging Face Transformers](https://huggingface.co/docs/transformers/main/en/llm_optims)
- [Recursos](../RESOURCES.md)

---

Não ficou claro? Releia a fonte principal no topo, já que esta lição a comprime e é na compressão que o entendimento escapa. Consulte o [glossário](../GLOSSARY.md) para qualquer termo que pareceu escorregadio.

Se o problema é a lição em si, e não o material, isso é um defeito: [abra uma issue](https://github.com/TokenCemetery/teach/issues).
