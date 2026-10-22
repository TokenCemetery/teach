---
title: "25. Servindo adapters"
description: "Faça merge para uma tarefa, roteie para muitas"
type: lesson
---

# Lição 25. Servindo adapters

**Ligação com a missão:** "Entregar" está na missão. Um adapter em um diretório não foi entregue.
**Fonte principal:** [Docs: LoRA adapters, vLLM](https://docs.vllm.ai/en/latest/features/lora.html)
**Pré-requisitos:** [Lição 13](0013-merging-and-shipping.md), [Lição 24](0024-the-regression-suite.md)

## Aquecimento

1. ▢ Qual escolha de serving torna o esquecimento catastrófico irrelevante?

<details markdown="1"><summary>Verificação</summary>

Manter o adapter sem merge e rotear só as requisições relevantes por ele, deixando o base intocado disponível para todo o resto.

</details>

2. ▢ Onde deve ser feito o merge de um adapter treinado contra um base quantizado?

<details markdown="1"><summary>Verificação</summary>

No base de precisão total, e quantizar depois, se for preciso um artefato quantizado.

</details>

3. ▢ Por que decodificação gulosa ao verificar um merge?

<details markdown="1"><summary>Verificação</summary>

Para que qualquer diferença de saída seja atribuível aos pesos e não à amostragem.

</details>

## Saiba isto

### Três formatos de implantação

**Modelo com merge.** Um único artefato, indistinguível de qualquer outro modelo. Qualquer stack de serving o carrega. Zero maquinário de adapter.

**Sem merge, adapter único.** Base mais adapter aplicado no carregamento. Soma dois matmuls pequenos por camada adaptada.

**Sem merge, vários adapters.** Um base na memória, muitos adapters, selecionados por requisição. É o formato que torna os adapters economicamente interessantes e precisa de suporte explícito em tempo de execução.

### Escolhendo

| | Com merge | Sem merge, multi-adapter |
|---|---|---|
| Memória para N tarefas | N modelos completos | Um base + N adapters pequenos |
| Overhead por requisição | Nenhum | Pequeno, e maior com batching misto |
| Stack de serving | Qualquer uma | Precisa suportar adapters |
| Trocar de tarefa | Carregar outro modelo | Mudar um campo da requisição |
| Adicionar uma tarefa | Implantar outro modelo | Soltar um arquivo |
| Base ainda disponível | Não | Sim |
| Rollback | Reimplantar | Parar de rotear para aquele adapter |

Regra de decisão: **uma tarefa e operação simples → faça merge. Várias tarefas, ou o base ainda é necessário → não faça merge.**

Aquela última linha é subestimada. Com um adapter sem merge, reverter um fine-tune ruim é uma mudança de roteamento e não uma implantação, e o base model está sempre lá como fallback.

### Como funciona o serving multi-adapter

A abordagem ingênua, trocar os pesos do adapter entre requisições, serializa tudo e destrói o throughput, porque o batching é de onde vem a eficiência da inferência.

As implementações reais agrupam em batch requisições que usam adapters *diferentes*. O cálculo do base model é compartilhado por todo o batch, já que é idêntico para todos, e as contribuições dos adapters são calculadas por requisição com kernels especializados que tratam um batch de pequenos matmuls heterogêneos. O trabalho do S-LoRA ([arXiv:2311.03285](https://arxiv.org/abs/2311.03285)) é o ponto de referência para servir muitos adapters de forma concorrente, incluindo manter os adapters inativos na memória do host e paginá-los para dentro.

O que isso significa na prática:

- Servir dezenas de adapters a partir de um único base é um problema resolvido, com implementações reais, e não uma ideia de pesquisa.
- O overhead é pequeno mas real, e cresce com quantos adapters *distintos* aparecem em um batch.
- Os adapters devem compartilhar rank e target modules sempre que possível. Formatos heterogêneos são mais difíceis de agrupar com eficiência.

No vLLM o formato é, grosso modo: ativar o suporte a LoRA, registrar os adapters e nomear um por requisição. Confira as flags atuais e os limites de rank máximo e de número máximo de adapters na documentação da versão instalada, porque essa superfície muda e os limites são definidos na inicialização do servidor.

### Quantização no momento do serving, mantida separada

Uma decisão independente de tudo o que está acima, e que vale reenunciar porque as duas costumam ser confundidas:

- A **quantização do momento do treinamento** (etapa 4) é um orçamento de memória para a execução de treinamento.
- A **quantização do momento do serving** encolhe o modelo que você implanta, e o seu custo em qualidade é permanente em toda requisição.

Você pode treinar contra um base de 4 bits e servir em bf16. Pode treinar em bf16 e servir quantizado. São escolhas sem relação, com trocas sem relação, e nenhuma implica a outra.

Se você serve quantizado, avalie o artefato quantizado. Avaliar um modelo em bf16 e entregar um de 4 bits significa que os seus números descrevem algo que você não implantou, o que é um erro surpreendentemente comum.

### Essenciais operacionais

**Versione tudo.** Base model e revisão, adapter, tokenizer, stack de serving. Uma resposta deve ser rastreável até a configuração exata que a produziu.

**Fixe os parâmetros de amostragem.** Temperature, top-p, max tokens, sequências de parada. Eles mudam a qualidade da saída tanto quanto o fine-tuning, e uma deriva de padrão não documentada será diagnosticada errado como uma regressão do modelo.

**Registre entradas e saídas.** O tráfego de produção é a melhor fonte do seu próximo conjunto de treinamento e do seu próximo conjunto held-out, porque é tirado da distribuição real e não da que você imaginou. Observe as restrições óbvias de privacidade e retenção; o ponto é coletar de propósito em vez de descobrir depois que você não coletou.

**Monitore a distribuição, e não só a latência.** Comprimento de entrada, comprimento de saída, taxa de recusa, validade do schema. Uma deriva na distribuição de entrada é o indicador antecedente de que as suposições do seu fine-tune expiraram.

**Mantenha o base alcançável.** Seja como rota de fallback, endpoint de comparação ou os dois. Poder fazer A/B do base contra o fine-tune em produção é a evidência mais forte disponível sobre se o fine-tune ajuda.

### A amostragem não é uma correção

Uma ressalva, porque é uma armadilha comum. Se um fine-tune rende pouco, temperature e top-p não são o reparo. Eles mudam o formato da distribuição, e não o seu conteúdo. Ajustar a amostragem para compensar um problema de treinamento o esconde e torna a próxima comparação ininterpretável: você deixa de saber qual de duas variáveis produziu uma diferença.

Corrija o treinamento no treinamento. Fixe a amostragem e deixe-a em paz.

## Prática

1. ▢ Cinco tarefas, um base model. Com merge ou sem merge, e o que a escolha custa?

<details markdown="1"><summary>Verificação</summary>

Sem merge. Um base na memória mais cinco adapters pequenos, contra cinco cópias completas do modelo.

Custos: a stack de serving precisa suportar adapters, e há um pequeno overhead por requisição que cresce com o número de adapters distintos em um batch.

</details>

2. ▢ Por que trocar adapters de forma ingênua entre requisições destrói o throughput?

<details markdown="1"><summary>Verificação</summary>

Isso serializa as requisições por adapter, impedindo o batching de que a eficiência da inferência depende.

As implementações reais agrupam em batch requisições com adapters diferentes, compartilhando o cálculo do base e calculando as contribuições dos adapters por requisição com kernels especializados.

</details>

3. ▢ Você treinou contra um base de 4 bits. É obrigatório servir em 4 bits?

<details markdown="1"><summary>Verificação</summary>

Não. A precisão de treinamento e a precisão de serving são independentes. Faça o merge no base de precisão total e sirva em bf16 se você tiver a memória.

A quantização do momento do treinamento era um orçamento para a execução. Ela não precisa acompanhar o artefato até a produção.

</details>

4. ▢ O seu fine-tune rende pouco em produção. Um colega sugere baixar a temperature. Avalie.

<details markdown="1"><summary>Verificação</summary>

Pode melhorar as saídas, e não resolve o problema. A amostragem remodela a distribuição que o modelo produziu; não consegue adicionar capacidade que o modelo não tem.

Pior, ela introduz uma segunda variável alterada, então a próxima comparação fica ininterpretável. Fixe a amostragem, diagnostique o treinamento.

</details>

5. ▢ Qual vantagem do serving sem merge mais importa operacionalmente?

    - a) A pegada de memória reduzida ao servir muitas tarefas
    - b) A capacidade de reverter mudando uma regra de roteamento
    - c) A ausência de qualquer overhead computacional por requisição
    - d) A compatibilidade com todo servidor de inferência existente

<details markdown="1"><summary>Verificação</summary>

**b)** A capacidade de reverter mudando uma regra de roteamento.

(a) é real e muitas vezes o motivo de destaque, mas (b) é o que você quer às duas da manhã. (c) é falsa, já que o sem merge soma um pequeno overhead. (d) é o contrário; o com merge é a opção universalmente compatível.

</details>

6. ▢ Você avaliou em bf16 e entregou um modelo quantizado em 4 bits. O que está errado?

<details markdown="1"><summary>Verificação</summary>

Os seus números descrevem um modelo que você não implantou. A quantização do momento do serving carrega um custo permanente em qualidade em toda requisição, e ele nunca foi medido.

Avalie o artefato que você entrega. Sempre.

</details>

## Prática no mundo real

- [ ] Sirva o seu adapter por um servidor de inferência e obtenha uma completion real pelo caminho completo.
- [ ] Carregue dois adapters em um único base e alterne entre eles por um campo da requisição. Confirme que as saídas diferem de forma apropriada.
- [ ] Meça a latência com merge, sem merge com adapter único e sem merge multi-adapter. Registre o overhead.
- [ ] Amanhã: escreva todas as versões e parâmetros de amostragem do seu caminho de serving em um único arquivo.

## Para ir além

- [Docs: LoRA adapters, vLLM](https://docs.vllm.ai/en/latest/features/lora.html)
- [Artigo científico: "S-LoRA: Serving Thousands of Concurrent LoRA Adapters", Sheng et al., arXiv:2311.03285](https://arxiv.org/abs/2311.03285)
- [Lição 26. Custo, latência e throughput](0026-cost-latency-and-throughput.md)

---

Não ficou claro? Releia a fonte principal no topo, já que esta lição a comprime e é na compressão que o entendimento escapa. Consulte o [glossário](../GLOSSARY.md) para qualquer termo que pareceu escorregadio.

Se o problema é a lição em si, e não o material, isso é um defeito: [abra uma issue](https://github.com/TokenCemetery/teach/issues).
