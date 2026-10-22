---
title: "7. PPO: por que a atualização é cortada"
description: "Uma grande vitória em um batch de dados amostrados não é evidência confiável para um grande passo; o PPO se recusa a acreditar totalmente nela"
type: lesson
---

# Lição 7. PPO: por que a atualização é cortada

**Ligação com a missão:** Derivar o objetivo do RLHF (lição 6) significa pouco sem saber o que "otimizar a policy contra ele usando PPO" realmente faz. Esta lição fornece esse mecanismo, que o restante da etapa 4 e a etapa de julgamento da missão dependem de você conseguir nomear de forma concreta, e não tratar como uma caixa-preta.
**Fonte principal:** [Artigo científico: "Proximal Policy Optimization Algorithms", Schulman et al., 2017](https://arxiv.org/abs/1707.06347)
**Pré-requisitos:** [Lição 6](0006-the-rlhf-objective-reward-minus-a-kl-penalty.md)

## Aquecimento

1. ▢ No objetivo do RLHF, o que acontece com a policy quando o coeficiente da penalidade de KL `β` diminui em direção a zero?

<details markdown="1"><summary>Verificação</summary>

A penalidade por divergir da policy do SFT quase desaparece, então o objetivo se reduz a perseguir a pontuação do reward model com quase nada segurando a policy, expondo-a ao reward hacking que a lição 5 descreveu.

</details>

2. ▢ Qual é a diferença entre "PPO" e "PPO-ptx" na nomenclatura de Ouyang et al., e qual termo as distingue?

<details markdown="1"><summary>Verificação</summary>

O "PPO" define o coeficiente do gradiente de pré-treinamento `γ` como 0; o "PPO-ptx" usa um `γ` diferente de zero, misturando no treinamento gradientes da log-verossimilhança dos dados de pré-treinamento, o que reduz o alignment tax.

</details>

## Saiba isto

### O problema que uma atualização sem restrição tem

Schulman et al. partem de um objetivo substituto mais simples, aquele que um método de policy gradient "vanilla" maximizaria diretamente: `L^CPI(θ) = E[r_t(θ) · Â_t]`, onde `r_t(θ) = policy(a|s) / policy_old(a|s)` é a razão entre a probabilidade da policy nova e da antiga para a ação de fato tomada, e `Â_t` é a **vantagem** estimada, grosso modo, o quanto melhor ou pior do que o esperado aquela ação acabou sendo. Maximizar `L^CPI` sem nenhuma restrição adicional dá ao otimizador todo incentivo para empurrar `r_t(θ)` o mais longe que puder na direção que aumenta o objetivo. Schulman et al. enunciam o problema diretamente: "sem uma restrição, a maximização de `L^CPI` levaria a uma atualização de policy excessivamente grande." Uma vantagem estimada grande em um batch amostrado não é evidência confiável de que um passo igualmente grande seja seguro em todo lugar; reagir demais a ela pode desestabilizar o treinamento.

### A correção do PPO: cortar a razão e depois tomar o caso pessimista

O objetivo real de Schulman et al. é:

```text
L^CLIP(θ) = E[ min( r_t(θ)·Â_t, clip(r_t(θ), 1-ε, 1+ε)·Â_t ) ]
```

com `ε` uma constante pequena (eles usam `0.2`). O termo `clip(...)` limita a razão `r_t(θ)` ao intervalo `[1-ε, 1+ε]`, o que remove o incentivo para empurrá-la mais para fora desse intervalo. Tomar o `min` entre as versões cortada e não cortada, em vez de apenas a versão cortada, é o que faz disso um **limite pessimista**: Schulman et al. explicam que esse esquema "só ignora a mudança na razão de probabilidade quando ela faria o objetivo melhorar, e a inclui quando ela piora o objetivo." Em termos simples, um movimento que parece estar ajudando é limitado em vez de plenamente recompensado, de modo que o otimizador não consegue extrair crédito ilimitado de um batch animador, enquanto um movimento que de fato está prejudicando não é protegido pelo mesmo limite, e o seu custo integral continua contando.

### Por que este é um tipo diferente de controle de estabilidade em relação à penalidade de KL

A penalidade de KL da lição 6 e o corte desta lição são ambos mecanismos de estabilidade, mas operam em escopos diferentes e não devem ser confundidos. A penalidade de KL mede a policy treinada contra o **modelo de referência SFT** original e fixo, e limita o quanto a execução inteira de treinamento pode se afastar desse ponto fixo ao longo de todo o seu curso. O corte do PPO compara a policy com **ela mesma imediatamente antes da atualização atual** (`policy_old`), e limita o tamanho que qualquer passo de otimização isolado pode ter, independentemente de onde a policy esteja no momento em relação ao modelo SFT. Um controla a deriva total ao longo da execução; o outro controla o tamanho de cada passo individual pelo caminho. Os dois são necessários, e nenhum substitui o outro: um corte pequeno por passo não impede que muitos passos pequenos acabem se afastando muito do modelo de referência, e uma penalidade de KL contra o modelo de referência não faz nada para impedir que um único passo seja destrutivamente grande.

## Prática

1. ▢ Um único batch de completions amostradas produz uma vantagem estimada incomumente grande para uma ação, puramente por causa de como aquele batch foi amostrado. Por que é arriscado deixar a policy se atualizar totalmente em proporção a essa vantagem, sem nenhum limite?

<details markdown="1"><summary>Verificação</summary>

Porque a vantagem estimada de um batch não é evidência confiável de que uma mudança igualmente grande seja segura em todo lugar; reagir demais a uma única amostra animadora (ou desanimadora) pode empurrar a policy uma distância excessivamente grande em um só passo, que é exatamente a instabilidade que o corte do PPO foi feito para evitar.

</details>

2. ▢ Por que o PPO toma o mínimo entre os termos substitutos cortado e não cortado, em vez de usar apenas o termo cortado?

    - a) Tomar o mínimo faz do objetivo um limite pessimista: um movimento que parece uma melhora é limitado, enquanto um movimento que parece prejudicial não é protegido pelo mesmo limite e continua contando integralmente
    - b) O mínimo só é usado por eficiência computacional e não tem efeito na policy aprendida
    - c) Usar apenas o termo cortado deixaria a razão sem limites
    - d) O mínimo garante que a razão seja sempre exatamente 1

<details markdown="1"><summary>Verificação</summary>

**a)** é o raciocínio declarado pelo próprio Schulman et al. A alternativa (b) subestima um efeito real sobre o comportamento da otimização. A alternativa (c) tem o propósito real do corte de trás para a frente; o corte limita a razão, não a deixa sem limites. A alternativa (d) entende mal o que o corte faz; a razão é limitada a um intervalo em torno de 1, e não forçada a ser exatamente 1.

</details>

3. ▢ A configuração de RLHF de uma equipe usa um coeficiente de penalidade de KL `β` grande, mas nenhum corte por passo (um objetivo substituto sem corte). Essa configuração está protegida contra uma única atualização de policy destrutivamente grande?

<details markdown="1"><summary>Verificação</summary>

Não. Um `β` grande limita o quanto a policy pode se afastar do modelo de referência SFT ao longo do treinamento, mas não faz nada para impedir que uma atualização individual, baseada na vantagem estimada de um batch, seja excessivamente grande. São dois controles de estabilidade diferentes, e remover um não é compensado pelo outro.

</details>

## Prática no mundo real

- [ ] Encontre onde uma implementação de PPO a que você tenha acesso expõe o parâmetro de corte (muitas vezes chamado de `epsilon`, `clip_range` ou algo parecido) e anote o seu valor padrão em comparação com o `0.2` que Schulman et al. relatam usar.
- [ ] Leia o parágrafo do artigo do PPO (linkado acima) que descreve por que `L^CPI` sozinho levaria a uma atualização excessivamente grande e escreva uma frase, com as suas palavras, explicando o que exatamente em um objetivo substituto sem restrição causa isso.
- [ ] Amanhã: sem olhar adiante, escreva uma previsão de uma frase para a lição 8: dado que o RLHF agora precisa de uma policy, de um modelo de referência (SFT) congelado para a penalidade de KL, de um reward model e de algo que produza as estimativas de vantagem de que a fórmula de corte desta lição depende, quantos modelos grandes separados você espera que estejam envolvidos em um único passo de treinamento com PPO?

## Para ir além

- [Artigo científico: "Proximal Policy Optimization Algorithms", Schulman et al., 2017](https://arxiv.org/abs/1707.06347)
- [Recursos](../RESOURCES.md)

---

Não ficou claro? Releia a fonte principal no topo, já que esta lição a comprime e é na compressão que o entendimento escapa. Consulte o [glossário](../GLOSSARY.md) para qualquer termo que pareceu escorregadio.

Se o problema é a lição em si, e não o material, isso é um defeito: [abra uma issue](https://github.com/TokenCemetery/teach/issues).
