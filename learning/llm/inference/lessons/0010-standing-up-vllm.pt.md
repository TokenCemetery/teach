---
title: "10. Colocando o vLLM no ar"
description: "Instalar o vLLM, iniciar o seu servidor e achar as flags que carregam os conceitos já ensinados"
type: lesson
---

# Lição 10. Colocando o vLLM no ar

**Ligação com a missão:** Toda fórmula das etapas 1 a 3, a pegada do cache, o batch size, o esquema de quantização, vira uma flag real em um comando real nesta lição; é aqui que a aritmética vira um servidor respondendo a requisições.
**Fonte principal:** [Documentação: vLLM Documentation, vLLM Project](https://docs.vllm.ai/en/latest/)
**Pré-requisitos:** [Lição 9](0009-picking-a-quantization-scheme.md), [KV cache](../GLOSSARY.md)

## Aquecimento

1. ▢ Um servidor está acima do seu orçamento de latência no batch size atual. Qual flag, pelo raciocínio da lição 6, é a primeira a verificar?

<details markdown="1"><summary>Verificação</summary>

A configuração do batch size máximo: o maior batch size que ainda satisfaz o orçamento de latência é o que a lição 6 defendeu, então esse é o parâmetro que o controla diretamente.

</details>

2. ▢ Por que uma escolha de tempo de serving de usar fp8 para o KV cache, e não a precisão dos pesos do próprio modelo, chegaria a fazer sentido (lição 3)?

<details markdown="1"><summary>Verificação</summary>

A precisão do cache é uma alavanca independente da precisão dos pesos do próprio modelo. Reduzir `bytes_per_value` do cache pela metade reduz a sua pegada pela metade de imediato, sem mudança no modelo em si, devolvendo capacidade do mesmo modo que um modelo menor devolveria.

</details>

## Saiba isto

### Instalando o vLLM

O vLLM se instala como um pacote Python, `pip install vllm`, e exige uma GPU com suporte a CUDA; ele é a metade de GPU da missão deste workspace, com o llama.cpp cobrindo CPU e edge na etapa seguinte. A instalação traz automaticamente um PyTorch e um toolchain CUDA compatíveis para as configurações comuns, o que vale conferir contra a versão instalada do driver CUDA antes de presumir que uma instalação que falhou é outra coisa.

### Iniciando o servidor

`vllm serve <model>` inicia um servidor HTTP compatível com a OpenAI para o modelo indicado (um caminho local ou um identificador do Hugging Face Hub), escutando na porta 8000 por padrão:

```text
vllm serve meta-llama/Llama-2-7b-hf
```

Esse único comando faz o download (se necessário), o carregamento dos pesos e a inicialização do servidor, cujas consequências de memória e de latência tudo nas etapas 1 a 3 estava raciocinando.

### Enviando uma requisição

Como o servidor fala o formato da API da OpenAI, uma requisição se parece com qualquer chamada de chat completion da OpenAI, apontada para o servidor local:

```bash
curl http://localhost:8000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{"model": "meta-llama/Llama-2-7b-hf", "messages": [{"role": "user", "content": "Say hello"}]}'
```

### Onde os conceitos já ensinados aparecem como flags

A linha de comando é onde as etapas 1 a 3 deixam de ser aritmética e viram configuração:

- `--max-num-seqs`: o teto de batch size que a lição 6 ensinou a defender contra um orçamento de latência.
- `--kv-cache-dtype`: a precisão do cache que a lição 3 introduziu como uma alavanca independente dos pesos do próprio modelo (por exemplo, `fp8`).
- `--quantization`: nomeia o esquema, como `gptq` ou `awq`, que as lições 7 a 9 ensinaram a escolher e defender, ao servir um checkpoint já quantizado.
- O continuous batching e o chunked prefill (lições 4 e 5) estão ligados por padrão; não há flag para desligar o mecanismo básico, só para ajustar em torno dele, como o tamanho do chunk.

## Prática

1. ▢ Uma equipe roda `vllm serve some-model --max-num-seqs 32 --kv-cache-dtype fp8`. Em termos das lições 6 e 3, o que cada uma dessas duas flags realmente controla?

<details markdown="1"><summary>Verificação</summary>

`--max-num-seqs 32` limita o batch size a 32, o número que a lição 6 defenderia contra um orçamento de latência declarado e o teto de capacidade da lição 2. `--kv-cache-dtype fp8` armazena o KV cache em fp8 em vez do padrão, reduzindo pela metade a sua pegada por token, independentemente da precisão dos pesos do próprio modelo, exatamente a alavanca que a lição 3 descreveu.

</details>

2. ▢ Uma equipe inicia um servidor com `vllm serve some-model`, sem nomear nenhuma flag `--quantization`. Em que precisão o servidor serve o modelo, e por quê?

<details markdown="1"><summary>Verificação</summary>

Na precisão em que o próprio checkpoint foi salvo, mais comumente fp16 ou bf16, já que nenhum esquema de quantização foi solicitado. `--quantization` só se aplica ao servir um checkpoint que foi quantizado de antemão ou que a flag manda o vLLM quantizar no carregamento; omiti-la significa que nada é quantizado.

</details>

3. ▢ Preveja, antes de conferir: depois de rodar `vllm serve` com sucesso, qual única informação da requisição curl da seção Saiba isto desta lição precisa coincidir com algo com que o servidor foi realmente iniciado, ou a requisição vai falhar?

<details markdown="1"><summary>Dica</summary>

Olhe o campo `"model"` no comando curl.

</details>

<details markdown="1"><summary>Verificação</summary>

O campo `"model"` no corpo da requisição precisa coincidir com o nome (ou caminho) do modelo com que o servidor foi iniciado. O servidor atende um modelo por vez; nomear outro na requisição é o que mais comumente produz um erro em uma chamada, de resto, bem formada.

</details>

4. ▢ Qual afirmação é verdadeira sobre o comportamento padrão do vLLM quando nenhuma flag de batching ou de cache é dada?

    - a) Ele recua para o batching estático até `--max-num-seqs` ser definido
    - b) O continuous batching e o chunked prefill rodam por padrão; as flags apenas os ajustam melhor
    - c) Ele se recusa a iniciar até que um dtype de KV cache seja escolhido explicitamente
    - d) Ele serve por padrão na menor precisão que o hardware suporta

<details markdown="1"><summary>Verificação</summary>

**b)** O continuous batching e o chunked prefill são o mecanismo padrão, e não algo que uma flag liga; as flags disponíveis ajustam parâmetros em torno deles, como o batch size máximo ou o tamanho de um chunk. (a) é falsa: não existe recuo para o batching estático. (c) é falsa: um dtype de cache padrão é usado se nenhum for indicado. (d) é falsa: o padrão é a precisão salva do próprio checkpoint, e não a menor que o hardware suporta.

</details>

## Prática no mundo real

- [ ] Instale o vLLM (`pip install vllm`) em uma máquina com uma GPU com suporte a CUDA e rode `vllm serve` com um modelo pequeno que você possa se dar ao luxo de baixar.
- [ ] Envie a requisição curl desta lição contra o seu servidor em execução e confirme que você recebe uma completion de verdade, e não um erro.
- [ ] Amanhã: reinicie o servidor com `--max-num-seqs` definido como um número pequeno (como 2) e como um grande, e veja se você consegue observar uma diferença em como ele se comporta sob algumas requisições concorrentes.

## Para ir além

- [Documentação: vLLM Documentation, vLLM Project](https://docs.vllm.ai/en/latest/)
- [Recursos](../RESOURCES.md)

---

Não ficou claro? Releia a fonte principal no topo, já que esta lição a comprime e é na compressão que o entendimento escapa. Consulte o [glossário](../GLOSSARY.md) para qualquer termo que pareceu escorregadio.

Se o problema é a lição em si, e não o material, isso é um defeito: [abra uma issue](https://github.com/TokenCemetery/teach/issues).
