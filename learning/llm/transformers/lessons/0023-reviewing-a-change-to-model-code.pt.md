---
title: "23. Revisando uma mudança no código de um modelo"
description: "Revise a mudança de outra pessoa no código de um modelo e nomeie o que ela quebra ou custa, em vez de confiar na descrição"
type: lesson
---

# Lição 23. Revisando uma mudança no código de um modelo

**Ligação com a missão:** A missão termina em ler ou modificar código real de modelos sem que a arquitetura seja uma caixa-preta; a versão sênior dessa habilidade é revisar a mudança de outra pessoa nele e nomear exatamente o que ela custa, em vez de confiar na descrição.
**Fonte principal:** [Artigo científico: "FlashAttention: Fast and Memory-Efficient Exact Attention with IO-Awareness", Dao et al., 2022](https://arxiv.org/abs/2205.14135), cuja afirmação de exatidão (lição 22) é o modelo desta lição de como verificar qualquer alegação de "mais rápido, saída inalterada".
**Pré-requisitos:** [0001-0003](0001-scaled-dot-product-attention.md) (atenção), [0004-0011](0004-positional-encoding.md) (blocos transformer e treinamento), [0012](0012-reading-real-model-code.md) (lendo código real), [0014, 0017](0014-rotary-position-embeddings.md) (variantes modernas), [0022](0022-mixture-of-experts-and-flashattention.md) (exatidão)

## Aquecimento

1. ▢ Um pull request alega "substituiu a atenção lenta por atenção rápida, saída inalterada". O que você confere primeiro antes de confiar nessa alegação?

<details markdown="1"><summary>Verificação</summary>

Se a saída de fato bate numericamente com a original, dentro da tolerância de ponto flutuante. "Mais rápido" muitas vezes quer dizer, discretamente, "diferente": uma computação simplificada ou uma aproximação que está levemente errada. A lição 22 fez da exatidão o teste da FlashAttention especificamente porque esse erro é comum.

</details>

2. ▢ Um diff muda a codificação posicional de sinusoidal para rotary. Você consegue identificar o que a mudança de fato custa sem ler o artigo?

<details markdown="1"><summary>Verificação</summary>

Você consegue derivar o que as codificações rotary fazem a partir da lição 14: elas rotacionam os vetores de query e key antes de a atenção rodar, que é como obtêm produtos escalares relativos à posição. Você pode então conferir se o diff implementa essa rotação corretamente e testar se as saídas batem com uma referência (a equação da lição 0001).

</details>

3. ▢ Uma mudança alega uma ablação: "removemos o termo de weight decay e o treinamento ainda converge". Que pergunta você faz?

<details markdown="1"><summary>Verificação</summary>

O autor mediu isso? A alegação é respaldada pela própria execução de treinamento dele, ou foi repetida a partir do resumo de um artigo em um post de blog? Uma alegação de ablação é tão forte quanto a medição por trás dela.

</details>

## Saiba isto

### O checklist de revisão: quatro coisas de que toda mudança no código de um modelo precisa

Um revisor que construiu um transformer a partir de tensores brutos tem uma vantagem que a maioria dos revisores de código não tem: você pode conferir uma alegação contra a matemática de fato, e não apenas se o código parece plausível.

**1. Os formatos se propagam corretamente?**

A convenção recorrente deste workspace: toda operação preserva o comprimento da sequência e a dimensão do embedding. Uma mudança na atenção (a máscara da lição 3, o RoPE da lição 14, a grouped-query da lição 17) não pode quebrar isso. Confira:

- Entrada da operação: formato `(batch, seq_len, d_model)` ou componentes como `(batch, num_heads, seq_len, d_k)`.
- Saída: o mesmo formato na saída.
- Duas camadas a jusante, algum bug que quebre o formato se esconde? Um rotary embedding que rotaciona pelo ângulo errado pode não falhar até que os produtos escalares da atenção virem um absurdo. Confira os testes a jusante ou rode o modelo para a frente com uma entrada conhecida e verifique os formatos intermediários.

**2. Se alega um ganho de velocidade, a saída bate numericamente?**

A lição 22 insistiu nisso: a FlashAttention é exata, e não aproximada. Ela calcula a equação idêntica, apenas tocando a memória de modo diferente. Ela **precisa** produzir a mesma `output` dentro da tolerância de ponto flutuante.

Quando um diff alega mais rápido sem mudar a saída:

- Rode o modelo com o código antigo e com o novo sobre a mesma entrada aleatória. Extraia as saídas de atenção (ou o forward pass completo, se o diff estiver a montante disso).
- Compare as saídas elemento a elemento. Elas precisam bater dentro do arredondamento de ponto flutuante, tipicamente de 1e-5 a 1e-4, dependendo da precisão. Se diferirem mais do que isso, a mudança não é um ganho de velocidade transparente; é uma computação diferente alegando ser a mesma.

**3. A mudança se justifica em relação ao que ela substitui?**

As lições 5 (layer norm, residuais) e 19 (inicialização, warm-up, gradient clipping, precisão mista) são salvaguardas: cada uma protege contra algo em que o loop de treinamento pode falhar sem ela. Uma mudança em qualquer uma delas precisa justificar por que a nova proteção é suficiente.

Exemplos:

- "Substituímos a layer norm pela RMSNorm": a RMSNorm abandona a recentralização. O código mostra que ela ainda é usada como pre-norm (lição 5), em que a centralização já era opcional?
- "Aumentamos o cronograma da learning rate": a mudança leva em conta contra o que o warm-up, o gradient clipping e a precisão mista protegiam?
- "Removemos o gradient clipping": você de fato fazia clipping antes? Você está preparado para ver loss spikes ou instabilidade de treinamento agora?

Um erro comum: copiar um valor de configuração de um modelo sem relação e não ajustar mais nada. "Nosso modelo tem 7B de parâmetros; vou usar a learning rate de um modelo de 70B que encontrei." Essa taxa foi escolhida para 70B; contexto, batch size e curvatura da loss são todos diferentes.

A mudança justificada ou explica o propósito da salvaguarda antiga e por que o novo arranjo não precisa dela, ou mostra uma medição de que o loop de treinamento sobrevive sem ela.

**4. Uma alegação de ablação é respaldada por medição real?**

De novo a lição 22: "a FlashAttention produz saída idêntica" é uma alegação que você pode verificar comparando saídas. Mas "removemos o weight decay e o treinamento é igualmente bom" é diferente: é um resultado experimental alegando que o componente removido não importava.

Confira:

- O autor da mudança é quem mediu? Medido em que dataset, com que seed aleatória, por quantos passos?
- Ou a alegação foi repetida a partir do resumo de um artigo, de um post de blog ou do experimento de outra pessoa? Se sim, o novo contexto (o tamanho do seu modelo, a arquitetura, a learning rate, o batch size, o dataset) corresponde à medição original?

Uma ablação real é arriscada de aceitar por autoridade de segunda mão, especialmente se a nova execução de treinamento é cara e a falha é custosa.

### Como soa um bom julgamento

Ao revisar uma mudança no código de um modelo, um engenheiro sênior nomeia especificamente o que uma escolha custa ou arrisca, em vez de confiar na descrição.

**Em vez de:** "Isto me parece errado."

**Melhor:** "A lição 14 deriva que o RoPE rotaciona Q e K por um ângulo proporcional a `position * dimension_index`. Este diff rotaciona por `position * constant`. Essa é uma função diferente. A propriedade de posição relativa do artigo não vai valer. Eu gostaria de ver as saídas baterem com uma referência antes de fazer o merge."

**Em vez de:** "Deveria funcionar."

**Melhor:** "A mudança remove um fator `residual_scale` antes de somar as residuais de volta. A lição 7 mostrou que escalar a residual é como a variante pre-norm da lição 5 evita o inchaço das ativações em modelos profundos. Eu gostaria de ver histogramas de gradiente em cada camada durante o treinamento, ou entender por que este modelo específico permanece estável sem o escalonamento."

**Em vez de:** "Os autores dizem que funciona."

**Melhor:** "Isto é RMSNorm, que o artigo aplica como pre-norm. O nosso código usa post-norm (lição 5). A RMSNorm sem recentralização pode estar bem como pre-norm, mas ser arriscada como post-norm. Eu gostaria ou de mudar para pre-norm ou de comparar as saídas com cuidado."

A diferença: nomear o que a mudança faz, contra o que ela protege ou o que ela custa, e que evidência resolveria a questão, em vez de dizer que a mudança parece certa ou errada.

## Prática

1. ▢ Um diff substitui a codificação posicional sinusoidal (lição 4) pela rotary (lição 14). As suas verificações: quais formatos ainda precisam bater e o que você testa primeiro?

<details markdown="1"><summary>Verificação</summary>

Formatos: entrada `(batch, seq_len, d_model)`, saída `(batch, seq_len, d_model)`. A rotação é aplicada a Q e K antes da atenção, então os formatos de entrada da atenção não mudam, e o formato de saída da atenção continua sendo `(batch, seq_len, d_model)`.

Teste primeiro: compare as saídas de atenção (ou as saídas do forward pass completo, se você conseguir isolá-las de forma limpa) entre o código antigo e o novo sobre a mesma entrada aleatória. Se baterem dentro da tolerância, a mudança preserva a computação. Se diferirem, algo está errado na matemática da rotação.

</details>

2. ▢ Uma mudança alega "multi-head attention → grouped-query attention (lição 17), sem diferença de saída". Qual é a sua primeira pergunta cética?

<details markdown="1"><summary>Verificação</summary>

A grouped-query attention tem menos heads de key e de value do que de query, então a computação é genuinamente diferente, mesmo que seja desenhada para aproximar a saída da multi-head. A alegação "sem diferença de saída" é *forte demais*. A alegação certa é "a saída é próxima o bastante para que o desempenho a jusante não sofra".

A sua verificação: as saídas batem numericamente dentro de uma tolerância que você esteja disposto a aceitar? Provavelmente 1e-4 ou mais estreita. Se baterem exatamente, provavelmente algo está errado (você pode ter deixado código multi-head ativo em algum lugar por acidente).

</details>

3. ▢ Um PR remove o warm-up da learning rate (lição 19). O autor diz "o modelo treina bem sem ele". O que você pergunta?

<details markdown="1"><summary>Verificação</summary>

- Eles mediram? Neste modelo, dataset e batch size?
- Qual era a learning rate antes de o warm-up entrar em ação? Se a taxa inicial agora é menor, a mudança talvez não esteja de fato removendo o benefício do warm-up.
- Eles viram picos de gradiente, camadas mortas ou curvas de loss incomuns? O warm-up os evita. Se o autor não olhou, pode não ter notado.

Sem medição no seu setup de fato, você está chutando. O warm-up é barato; se funciona, mantenha-o.

</details>

4. ▢ Qual afirmação sobre revisar uma mudança no código de um modelo é a diretriz mais útil?

    - a) Confiar na descrição do autor e se concentrar no estilo do código
    - b) Rejeitar qualquer mudança na atenção ou no loop de treinamento; são arriscadas demais para modificar
    - c) Comparar as saídas numericamente quando a mudança alega não alterar a saída e nomear o custo específico quando ela altera
    - d) Exigir que todo resultado de ablação seja respaldado por um artigo publicado antes de aceitá-lo

<details markdown="1"><summary>Verificação</summary>

**c)** Comparar as saídas numericamente quando a mudança alega não alterar a saída e nomear o custo específico quando ela altera.

(a) é como os erros chegam à produção. (b) é cauteloso demais; todo o objetivo é conseguir julgar as mudanças com cuidado. (d) é estrito demais; uma mudança útil pode vir antes da publicação, e a medição no seu setup de fato muitas vezes é mais relevante do que a medição de um artigo em uma escala diferente.

</details>

5. ▢ Um diff muda a posição da RMSNorm (lição 15) de post-norm para pre-norm (lição 5). Que coisa você verifica antes de confiar na mudança?

<details markdown="1"><summary>Dica</summary>

Pense no que a lição 5 diz que cada posição serve e no que a RMSNorm abandona em comparação com a layer norm.

</details>

<details markdown="1"><summary>Verificação</summary>

A RMSNorm pre-norm funciona porque a RMSNorm apenas reescala (não recentraliza), e a pre-norm não precisa de recentralização para evitar o inchaço das ativações: a residual que entra no próximo bloco é ilimitada, mas a normalização *daquele* bloco cuida disso.

A post-norm é diferente: a saída residual é ilimitada, e a recentralização da layer norm era em parte o motivo de a post-norm permanecer estável. A RMSNorm abandona a recentralização. Você gostaria de comparar histogramas de ativação (estão inchando?), curvas de treinamento (mostram instabilidade?) ou, no mínimo, rodar um teste rápido para ver se as curvas de loss batem antes e depois da mudança.

</details>

## Prática no mundo real

- [ ] Da próxima vez que você vir um PR que mude a atenção, a codificação posicional ou o loop de treinamento em um modelo em que você trabalha ou que entende, use o checklist de quatro pontos acima: formatos, exatidão da saída, justificativa em relação ao que ela substitui e medição que respalde qualquer alegação de ablação.
- [ ] Nesse mesmo PR (ou no seu próprio), pratique escrever um comentário de revisão que nomeie especificamente o que uma mudança faz e o que resolveria a questão, em vez de dizer que ela parece certa ou errada.
- [ ] Amanhã: se você modificar o seu próprio código de modelo esta semana (mudando uma camada, trocando uma ativação, ajustando um cronograma), confira se consegue verificar formatos e saídas numericamente antes de submeter. Se não conseguir, você na verdade não sabe se mudou algo importante ou nada.
- [ ] Amanhã: Revisite uma alegação que você ouviu sobre atenção, embeddings ou um truque de treinamento. Vá ao artigo original (e não ao resumo do post de blog) e confira se a alegação corresponde às equações de fato do artigo. A lição 12 mostrou como encontrar código real; agora use essa habilidade e os artigos em [Recursos](../RESOURCES.md) para resolver um ponto em disputa.

## Para ir além

- [Artigo científico: "RoFormer: Enhanced Transformer with Rotary Position Embedding"](https://arxiv.org/abs/2104.09864), Su et al. Use para: a matemática original dos rotary embeddings, para verificar alegações contra o que o artigo de fato diz.
- [Artigo científico: "GQA: Training Generalized Multi-Query Transformer Models from Multi-Head Checkpoints"](https://arxiv.org/abs/2305.13245), Ainslie et al. Use para: o design da grouped-query attention, para conferir a alegação de aproximação e entender que troca ela faz.
- [Artigo científico: "FlashAttention: Fast and Memory-Efficient Exact Attention with IO-Awareness"](https://arxiv.org/abs/2205.14135), Dao et al. Use para: confirmar que a FlashAttention é exata, e não aproximada, e ver como eles a verificam contra implementações de referência.
- Revisite as [lições do loop de treinamento](0019-initialization-warmup-and-gradient-clipping.md) quando estiver revisando mudanças na learning rate, no gradient clipping ou na precisão mista. As seções "Para ir além" dessas lições apontam para os artigos por trás de cada salvaguarda.
- [Glossário](../GLOSSARY.md) para qualquer termo que pareceu escorregadio.
- [Recursos](../RESOURCES.md)

---

Não ficou claro? Releia a fonte principal no topo, já que esta lição a comprime e é na compressão que o entendimento escapa. Consulte o [glossário](../GLOSSARY.md) para qualquer termo que pareceu escorregadio.

Se o problema é a lição em si, e não o material, isso é um defeito: [abra uma issue](https://github.com/TokenCemetery/teach/issues).
