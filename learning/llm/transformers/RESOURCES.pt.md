---
title: "Recursos"
description: "Fontes confiáveis sobre transformers"
type: resources
---

# Recursos de Transformers

## Conhecimento

- [Artigo científico: "Attention Is All You Need", Vaswani et al., 2017](https://arxiv.org/abs/1706.03762)
  O artigo original do transformer: scaled dot-product attention, multi-head attention e o bloco encoder-decoder completo que este workspace deriva a partir de tensores brutos. Use para: a definição primária de cada peça que este workspace implementa.
- [Artigo: "The Illustrated Transformer", Jay Alammar](https://jalammar.github.io/illustrated-transformer/)
  Um passo a passo visual e guiado pela intuição da atenção e do bloco transformer, feito para ser lido antes da notação do artigo científico. Use para: um modelo mental funcional antes de implementar qualquer coisa.
- [Artigo: "The Annotated Transformer", Harvard NLP](http://nlp.seas.harvard.edu/annotated-transformer/)
  Implementação em PyTorch do artigo científico, linha por linha, a partir de operações com tensores brutos, confrontada diretamente com as equações que as produzem. Use para: conferir uma implementação feita do zero contra uma referência, linha a linha.
- [Repositório: nanoGPT, Karpathy](https://github.com/karpathy/nanoGPT)
  Implementação mínima e legível em PyTorch de um transformer estilo GPT, com o seu loop de treinamento, pequena o bastante para ser lida por inteiro. Use para: a metade de loop de treinamento da missão, depois que o bloco em si funcionar.
- [Vídeo: "Let's build GPT: from scratch, in code, spelled out", Karpathy](https://www.youtube.com/watch?v=kCc8FmEb1nY)
  Constrói a atenção e um loop de treinamento de GPT a partir de tensores brutos na tela, passo a passo, derivando cada peça em vez de apresentá-la pronta. Use para: ver a derivação acontecer antes de escrever o código você mesmo, ou enquanto o escreve.
- [Docs: "Autograd mechanics", PyTorch](https://pytorch.org/docs/stable/notes/autograd.html)
  Explicação oficial de como o autograd do PyTorch realmente calcula gradientes através de um grafo de computação. Use para: entender o que o backward pass faz com os pesos, e não apenas chamar `.backward()`.
- [Repositório: transformers, Hugging Face](https://github.com/huggingface/transformers)
  Uma biblioteca de modelos real, de produção, útil depois que as peças feitas do zero existirem. Use para: localizar a atenção, a projeção multi-head e o bloco transformer dentro de um código escrito para produção, e não para o ensino.
- [Artigo científico: "Layer Normalization", Ba, Kiros e Hinton, 2016](https://arxiv.org/abs/1607.06450)
  Introduz a layer normalization: normalizar as ativações de cada exemplo ao longo da dimensão de features, independentemente do batch size, ao contrário da batch normalization. Use para: entender o que a layer norm realmente calcula e por que ela se ajusta a sequências de comprimento variável e a batch sizes pequenos.
- [Artigo científico: "On Layer Normalization in the Transformer Architecture", Xiong et al., 2020](https://arxiv.org/abs/2002.04745)
  Compara colocar a layer norm depois da soma residual (a escolha do artigo original, post-norm) com colocá-la antes de cada subcamada, dentro do ramo residual (pre-norm), e mostra por que a pre-norm treina de forma mais estável em maior profundidade. Use para: entender por que a maioria dos grandes modelos atuais usa pre-norm, apesar de o artigo original do transformer usar post-norm.
- [Artigo científico: "Using the Output Embedding to Improve Language Models", Press e Wolf, 2017](https://arxiv.org/abs/1608.05859)
  Defende amarrar as matrizes de pesos do embedding de entrada e da projeção de saída, já que ambas relacionam um token à mesma representação subjacente, cortando uma grande fração dos parâmetros de um modelo de vocabulário grande. Use para: entender o weight tying como uma escolha de design deliberada, e não apenas um truque para economizar parâmetros.
- [Docs: "torch.nn.functional.cross_entropy", PyTorch](https://pytorch.org/docs/stable/generated/torch.nn.functional.cross_entropy.html)
  Documentação oficial da operação fundida de softmax mais log-likelihood negativo, que recebe os logits brutos diretamente, por estabilidade numérica, em vez de exigir antes uma etapa de softmax separada. Use para: como a loss de cross-entropy é realmente calculada na prática, e não apenas a sua fórmula.
- [Artigo científico: "Adam: A Method for Stochastic Optimization", Kingma e Ba, 2015](https://arxiv.org/abs/1412.6980)
  Introduz o momento do Adam (primeiro momento) e o escalonamento adaptativo por parâmetro (segundo momento) sobre o gradient descent simples, com correção de viés para ambos. Use para: entender o que a regra de atualização do Adam calcula e por quê, antes da correção de weight decay do AdamW.
- [Artigo científico: "Decoupled Weight Decay Regularization", Loshchilov e Hutter, 2019](https://arxiv.org/abs/1711.05101)
  Identifica por que embutir o weight decay no gradiente, como no Adam original, interage mal com o seu escalonamento adaptativo, e corrige isso aplicando o decay diretamente aos pesos. Use para: por que o AdamW, e não o Adam simples, é o otimizador padrão para treinar transformers.
- [Artigo científico: "Neural Machine Translation of Rare Words with Subword Units", Sennrich, Haddow e Birch, 2016](https://arxiv.org/abs/1508.07909)
  Introduz o byte-pair encoding para tokenização em subpalavras: mesclar iterativamente o par adjacente de símbolos mais frequente para construir um vocabulário dos bytes brutos para cima. Use para: derivar o mecanismo de tokenizer que `llm/finetuning` menciona de passagem, em vez de reafirmá-lo.
- [Artigo científico: "RoFormer: Enhanced Transformer with Rotary Position Embedding", Su et al., 2021](https://arxiv.org/abs/2104.09864)
  Introduz o RoPE: rotacionar os vetores de query e key projetados por um ângulo proporcional à posição, produzindo um score de atenção que depende apenas do deslocamento relativo. Use para: o mecanismo que quase todo modelo aberto atual usa no lugar da codificação posicional sinusoidal ou aprendida.
- [Artigo científico: "Root Mean Square Layer Normalization", Zhang e Sennrich, 2019](https://arxiv.org/abs/1910.07467)
  Introduz a RMSNorm, levantando a hipótese de que a operação de recentralização (subtração da média) da layer norm é dispensável e de que o reescalonamento sozinho responde pela maior parte do seu benefício. Use para: a normalização mais barata que os modelos atuais colocam dentro do ramo pre-norm que a lição 5 deriva.
- [Artigo científico: "GLU Variants Improve Transformer", Shazeer, 2020](https://arxiv.org/abs/2002.05202)
  Testa variantes de gated linear unit (incluindo o SwiGLU, com gate de Swish) na subcamada feed-forward do transformer, constatando que algumas superam a ReLU ou a GELU normalmente usadas. Use para: o desenho com gate e duas projeções de expansão que substitui, nos modelos atuais, o bloco feed-forward de projeção única da lição 6.
- [Artigo científico: "GQA: Training Generalized Multi-Query Transformer Models from Multi-Head Checkpoints", Ainslie et al., 2023](https://arxiv.org/abs/2305.13245)
  Introduz a grouped-query attention como meio-termo entre a multi-head attention completa e o único head de key/value compartilhado da multi-query attention, além de uma receita barata para fazer o uptraining de um checkpoint multi-head existente até ela. Use para: por que menos heads de key/value trocam uma pequena quantidade de qualidade por um KV cache bem menor e uma inferência mais rápida.
- [Artigo científico: "The Curious Case of Neural Text Degeneration", Holtzman et al., 2019](https://arxiv.org/abs/1904.09751)
  Documenta por que maximizar a likelihood no momento da decodificação (greedy decoding) produz texto insípido e repetitivo, apesar de a likelihood ser um bom objetivo de treinamento, e introduz o nucleus sampling (top-p) como correção. Use para: a razão precisa de um corte dinâmico, por probabilidade acumulada, superar tanto o greedy decoding quanto uma contagem fixa de top-k.
- [Artigo científico: "On the difficulty of training Recurrent Neural Networks", Pascanu, Mikolov e Bengio, 2013](https://arxiv.org/abs/1211.5063)
  Analisa os problemas de gradiente que desaparece e que explode e propõe o gradient norm clipping como correção do segundo. Use para: por que o clipping reescala o vetor de gradiente inteiro pela sua norma, em vez de limitar o gradiente de cada parâmetro de forma independente.
- [Artigo científico: "Mixed Precision Training", Micikevicius et al., 2018](https://arxiv.org/abs/1710.03740)
  Introduz o treinamento em meia precisão com uma cópia master dos pesos em precisão completa e loss scaling para contrabalançar a faixa numérica limitada da meia precisão, reduzindo o uso de memória em quase metade. Use para: exatamente o que é preciso acrescentar ao treinamento simples em meia precisão para impedir que pequenas atualizações e gradientes sofram underflow até zero.
- [Artigo científico: "BERT: Pre-training of Deep Bidirectional Transformers for Language Understanding", Devlin et al., 2018](https://arxiv.org/abs/1810.04805)
  Introduz a arquitetura encoder-only: atenção bidirecional que condiciona conjuntamente o contexto da esquerda e da direita em todas as camadas, sem máscara causal. Use para: por que um modelo encoder-only constrói uma representação de uma entrada completa em vez de gerar texto de forma autorregressiva, e não consegue fazer o que o modelo decoder-only deste workspace faz.
- [Artigo científico: "Exploring the Limits of Transfer Learning with a Unified Text-to-Text Transformer" (T5), Raffel et al., 2019](https://arxiv.org/abs/1910.10683)
  Reformula uma ampla gama de tarefas de NLP em um único formato consistente de texto para texto, encoder-decoder. Use para: a subcamada de cross-attention da forma encoder-decoder e por que ela se ajusta a uma tarefa com uma divisão nítida e fixa entre entrada e saída.
- [Artigo científico: "FlashAttention: Fast and Memory-Efficient Exact Attention with IO-Awareness", Dao et al., 2022](https://arxiv.org/abs/2205.14135)
  Diagnostica a lentidão da atenção padrão em sequências longas como um problema de IO (leituras e escritas de memória entre HBM e SRAM), e não de compute, e introduz um algoritmo exato, em blocos, que evita materializar a matriz completa de scores. Use para: por que uma implementação real de atenção tem aparência estruturalmente diferente da versão da lição 1 e calcula o resultado idêntico.
- [Artigo científico: "Switch Transformers: Scaling to Trillion Parameter Models with Simple and Efficient Sparsity", Fedus, Zoph e Shazeer, 2021](https://arxiv.org/abs/2101.03961)
  Introduz um esquema simplificado de roteamento MoE com um expert por token, desacoplando a contagem total de parâmetros do custo de compute por token. Use para: a troca específica que os modelos de ativação esparsa fazem e por que simplificar o roteamento para um expert resolveu instabilidades que desenhos de MoE mais complexos encontravam.

## Lacunas

- Ainda não há fonte sobre o cronograma exato de warm-up da learning rate seguido de decay; a lição 19 o deriva a partir do formato descrito nos próprios detalhes de treinamento do artigo original do transformer (warm-up linear, depois decay proporcional ao inverso da raiz quadrada do número do passo), mas um trecho direto e recém-verificado dessa seção não pôde ser obtido com as ferramentas disponíveis nesta sessão (a página de resumo do artigo não traz a seção de detalhes de treinamento, e outras fontes em PDF dela não foram extraídas como texto legível). Revisite se surgir uma fonte mais limpa.
