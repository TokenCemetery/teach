---
title: "Modos de falha"
description: "Do sintoma à causa, e as falhas silenciosas"
type: reference
---

# Modos de falha

Folha de diagnóstico. Mantenha-a aberta durante uma execução.

## As quatro verificações, antes de qualquer outra coisa

```python
# 1. Did the adapter attach?
model.print_trainable_parameters()          # compare to your arithmetic

# 2. Is the data what you think?
print(repr(tokenizer.decode(ds[0]["input_ids"])))
print(sum(1 for l in ds[0]["labels"] if l != -100), "of", len(ds[0]["labels"]), "scored")

# 3. Does loss move?                        # logging_steps=1 over 50 steps

# 4. Can it overfit two examples?           # loss → ~0 in 100 steps, or the pipeline is broken
```

A verificação 2 pega, em uma única leitura, incompatibilidade de template, tokens de fim de turno ausentes, bugs de mascaramento e truncamento. São os dez segundos de maior valor em todo o processo.

## Sintoma → causa

![Seis esboços de loss contra passos: plana desde o passo 1, uma queda que para bem acima de zero, curvas de treino e held-out se separando com a held-out voltando a subir, uma escada de trechos planos e quedas bruscas, uma descida interrompida por um único pico e uma descida que termina de repente em NaN.](images/loss-curve-shapes.svg)

As primeiras onze linhas abaixo nomeiam uma curva e não um evento, e várias delas compartilham o mesmo formato: três dizem plana, duas dizem mal se move. Encontre o esboço correspondente e depois leia todas as linhas que o nomeiam, já que um mesmo formato pode ter mais de uma causa. A partir da linha doze, o sintoma foi observado em outro lugar, em uma saída, em um erro de carregamento ou em um conjunto de regressão, e não há curva para comparar.

| Sintoma | Causa provável | Verificação |
|---|---|---|
| Loss exatamente plana desde o passo 1 | O adapter não casou com nada | `print_trainable_parameters()` |
| Loss exatamente plana desde o passo 1 | Todos os labels em `-100` | Contar as posições pontuadas |
| Loss exatamente plana desde o passo 1 | LR ordens de grandeza baixo demais | Deveria ser ~`1e-4` |
| Loss mal se move | Nomes dos target modules errados para esta arquitetura | `named_modules()` |
| Loss mal se move | `α/r` acidentalmente minúsculo | Aumentou `r`, esqueceu `α` |
| Loss estaciona em valor alto | Teto de capacidade | Mais rank ou mais targets, não mais epochs |
| Held-out sobe, treino cai | Overfitting | Entregue o mínimo da held-out |
| Treino → 0 rápido, held-out sobe de imediato | Dataset pequeno demais para a capacidade | Mais dados, menos capacidade |
| Loss em escada nas fronteiras de epoch | Memorização | Menos epochs |
| Loss dá um pico e se recupera | Um batch patológico | Encontre o exemplo outlier |
| Loss → `NaN` | Overflow, ou dados ruins | Prefira bf16; LR menor; adicione warm-up |
| Held-out suspeitamente boa | Contaminação através da divisão | Deduplique treino vs teste, leia os pares de maior similaridade |
| O modelo nunca para de gerar | Sem token de fim de turno nos dados de treinamento | Decodifique um exemplo |
| A saída ignora o formato pedido | Incompatibilidade de template entre treino e serving | Compare com `repr` |
| Respostas cortadas no meio da frase | `max_length` truncando os alvos | Confira a distribuição de comprimento |
| Respostas a perguntas que não foram feitas | O packing quebrou o mascaramento da loss ou as fronteiras | Verifique se o `-100` sobrevive ao packing |
| Pior em coisas não relacionadas | Esquecimento catastrófico | Conjunto de regressão contra o baseline guardado |
| Não recusa mais o que o base recusava | Regressão de segurança | **Bloqueia o lançamento** |
| Saída do merged ≠ saída do não merged | Bug no merge, ou a amostragem estava ligada | Reverifique com decodificação gulosa |
| Modelo merged degradado | Merge feito em um base quantizado | Faça o merge em precisão total, depois quantize |
| O adapter não carrega | Modelo base ou revisão errados | Um adapter é um diff; precisa do seu base exato |
| Erros de gradiente em um base de 4 bits | Pulou o `prepare_model_for_kbit_training` | Adicione-o |
| Ótimo eval, produção ruim | Incompatibilidade de distribuição entre treino e serving | Treine com entradas reais, não com as limpas |
| O resultado sumiu ao repetir | Ruído de seed, nunca foi um efeito real | Várias seeds, comparação pareada |

## Falhas silenciosas: nenhum erro, resultado errado

O conjunto perigoso. Nada lança erro, tudo parece bem.

1. **Incompatibilidade de template** entre treinamento e serving.
2. **Token de fim de turno ausente.** Treina bem, nunca para.
3. **Mascaramento da loss errado.** Treinar nos prompts sem querer.
4. **Contaminação.** A held-out mede memorização, reporta generalização.
5. **Vazamento por grupo ou temporal.** Divisão feita pela chave errada.
6. **Esquecimento catastrófico.** Todo número que você acompanha melhora.
7. **Adapter acoplado a nada.** Treina, registra uma loss, não aprende nada.
8. **Avaliar um artefato diferente do que você entrega**, por exemplo eval em bf16 e deploy em 4 bits.

Cada uma tem um passo específico de detecção acima. Nenhuma se anuncia sozinha.

## Reduzindo o esquecimento

Do mais barato ao mais caro:

1. Menos passos, ou um checkpoint anterior
2. Learning rate menor
3. Rank menor, ou menos target modules
4. Misturar alguns por cento de dados gerais de instrução no treinamento
5. **Manter o adapter sem merge e rotear**, para que o base fique intacto e o esquecimento deixe de importar

## Higiene de comparação

- Uma variável por vez; fixe seed, dados e divisão
- Várias seeds, já que a variância muitas vezes supera o efeito
- Comparação pareada nos mesmos exemplos
- Reporte `n` e um intervalo, nunca um número solto
- Leia as gerações reais, incluindo as falhas, todas as vezes

## O que registrar por execução

Modelo base **e revisão** · configuração do adapter literal · dataset e a divisão exata · seed · batch size efetivo · LR e schedule · passos · checkpoint escolhido e o número que o justifica · versões das bibliotecas · resultados do eval e da regressão.

## Relacionado

- [Lição 11](../lessons/0011-your-first-adapter.md), [Lição 12](../lessons/0012-reading-a-training-run.md), [Lição 22](../lessons/0022-contamination-and-held-out-design.md), [Lição 24](../lessons/0024-the-regression-suite.md)
