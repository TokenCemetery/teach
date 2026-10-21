---
title: "Recursos"
description: "Fontes confiáveis sobre pré-treinamento de LLMs"
type: resources
---

# Recursos de Pré-treinamento de LLMs

## Conhecimento

- [Artigo científico: "Scaling Laws for Neural Language Models", Kaplan et al., 2020](https://arxiv.org/abs/2001.08361)
  Ajusta as relações originais de lei de potência entre loss, compute, contagem de parâmetros e dados, e defende escalar os parâmetros mais rápido do que os dados. Use para: a etapa 3, como o baseline que o Chinchilla depois revisa.
- [Artigo científico: "Training Compute-Optimal Large Language Models", Hoffmann et al., 2022](https://arxiv.org/abs/2203.15556)
  O artigo do Chinchilla. Reajusta as leis de escala com uma varredura mais ampla e conclui que parâmetros e tokens devem escalar juntos, em torno de vinte tokens por parâmetro, derrubando a recomendação de Kaplan, pesada em parâmetros. Use para: o resultado central da etapa 3 e o orçamento de tokens que a maioria das execuções de treinamento modernas realmente usa.
- [Artigo científico: "ZeRO: Memory Optimizations Toward Training Trillion Parameter Models", Rajbhandari et al., 2019](https://arxiv.org/abs/1910.02054)
  Define os três estágios do ZeRO, que particionam o estado do otimizador, depois os gradientes e depois os parâmetros entre os dispositivos de dados paralelos. Use para: a técnica central da etapa 5, que o FSDP implementa.
- [Documentação: "Fully Sharded Data Parallel", PyTorch](https://pytorch.org/docs/stable/fsdp.html)
  A referência da API do particionamento no estilo do ZeRO estágio 3 do PyTorch, incluindo as estratégias de particionamento e as políticas de wrapping que o laboratório de uma lição realmente executa. Use para: as repetições práticas da etapa 5.
- [Artigo científico: "Efficient Large-Scale Language Model Training on GPU Clusters Using Megatron-LM", Narayanan et al., 2021](https://arxiv.org/abs/2104.04473)
  Combina paralelismo de tensor, paralelismo de pipeline e paralelismo de dados em um só sistema, com os tradeoffs de throughput e de memória de cada um medidos em relação aos outros. Use para: a técnica central da etapa 6 e os seus números trabalhados.
- [Documentação: "DeepSpeed", Microsoft](https://github.com/microsoft/DeepSpeed)
  Uma segunda implementação de produção do ZeRO junto com o paralelismo 3D, com exemplos de configuração para que uma lição possa apontar um segundo sistema concreto ao lado do FSDP e do Megatron-LM. Use para: as etapas 5 e 6, como a verificação cruzada de que uma afirmação é sobre a técnica e não sobre a API de uma única biblioteca.
- [Artigo científico: "The Pile: An 800GB Dataset of Diverse Text for Language Modeling", Gao et al., 2020](https://arxiv.org/abs/2101.00027)
  Um corpus de pré-treinamento totalmente documentado: quais fontes entraram, em que proporções e por quê. Use para: a etapa 1, como um exemplo trabalhado de uma decisão de mistura de dados tornada explícita.
- [Artigo científico: "Deduplicating Training Data Makes Language Models Better", Lee et al., 2021](https://arxiv.org/abs/2107.06499)
  Mostra que texto quase duplicado e substrings longas repetidas causam memorização literal e apresenta duas técnicas de deduplicação (correspondência exata de substrings por meio de um suffix array e correspondência de quase duplicatas por meio de MinHash), cada uma medida em um corpus real. Use para: o material de deduplicação da etapa 1, com números concretos de antes e depois.
- [Artigo científico: "Language Models are Few-Shot Learners", Brown et al., 2020](https://arxiv.org/abs/2005.14165)
  O artigo do GPT-3. O Apêndice A documenta um pipeline concreto de filtragem de qualidade: um classificador treinado para distinguir texto curado do Common Crawl bruto, usado para reamostrá-lo em direção a documentos de maior pontuação, junto com uma passagem separada de deduplicação fuzzy. Use para: o material de filtragem de qualidade da etapa 1, como o exemplo trabalhado que o artigo de deduplicação acima não fornece por si só.
- [Artigo científico: "Neural Machine Translation of Rare Words with Subword Units", Sennrich et al., 2015](https://arxiv.org/abs/1508.07909)
  Introduz o byte-pair encoding para a tokenização em subpalavras, o algoritmo sobre o qual a maioria dos tokenizers modernos ainda se apoia. Use para: o algoritmo central da etapa 2.
- [Artigo científico: "SentencePiece: A simple and language independent subword tokenizer and detokenizer for Neural Text Processing", Kudo e Richardson, 2018](https://arxiv.org/abs/1808.06226)
  Trata a tokenização como uma operação direta sobre o texto bruto, sem uma etapa de pré-tokenização específica de cada idioma, e cobre a tokenização por modelo de linguagem unigram como alternativa ao BPE. Use para: o segundo algoritmo da etapa 2 e o tradeoff do tamanho do vocabulário.
- [Artigo científico: "Scaling Language Models: Methods, Analysis & Insights from Training Gopher", Rae et al., 2021](https://arxiv.org/abs/2112.11446)
  Um relato detalhado e honesto de uma execução de treinamento grande, incluindo onde apareceram loss spikes e instabilidade e o que os autores fizeram a respeito. Use para: o estudo de caso central da etapa 7.
- [Artigo científico: "LLaMA: Open and Efficient Foundation Language Models", Touvron et al., 2023](https://arxiv.org/abs/2302.13971)
  Uma receita de treinamento publicada e reproduzível: mistura de dados, tokenizer, schedule e hiperparâmetros, declarados com clareza suficiente para conferir as afirmações de uma lição. Use para: conferir as etapas 1 a 3 e 7 contra uma receita real e completa.
- [Artigo científico: "OPT: Open Pre-trained Transformer Language Models", Zhang et al., 2022](https://arxiv.org/abs/2205.01068)
  Lançado junto com um logbook público dos problemas de infraestrutura que os autores realmente enfrentaram ao treinar um modelo de 175B: falhas de hardware, reinícios manuais e automáticos, divergências de loss e o procedimento concreto de recuperação usado em cada uma. Use para: o estudo de caso central da etapa 8 e um segundo exemplo real do padrão de divergência de loss que a etapa 7 cobre.
- [Artigo científico: "Don't Stop Pretraining: Adapt Language Models to Domains and Tasks", Gururangan et al., 2020](https://arxiv.org/abs/2004.10964)
  Mostra que continuar o pré-treinamento sobre um modelo existente de cobertura ampla (pré-treinamento adaptativo ao domínio) melhora de forma consistente o desempenho no domínio-alvo em quatro domínios e oito tarefas, tanto em cenários de muitos quanto de poucos recursos, sem treinar um modelo novo do zero. Use para: o argumento central da etapa 10 de que pré-treinar do zero costuma ser o padrão errado.

## Lacunas

- O artigo do OPT documenta a frequência real de falhas e o procedimento de recuperação, mas não declara uma política específica de intervalo de checkpoint (com que frequência os checkpoints foram de fato salvos). O tradeoff de frequência de checkpoint da etapa 8 é ensinado a partir de raciocínio geral de engenharia e não de uma política declarada; uma fonte primária com um intervalo concreto o fortaleceria.
- A filtragem baseada em classificador do GPT-3 (2020) é o único exemplo trabalhado de filtragem de qualidade listado até agora. Os corpora construídos desde 2023 (FineWeb, Dolma) filtram de forma muito mais agressiva e documentam isso com mais profundidade; uma fonte primária mais recente fortaleceria a etapa 1.
