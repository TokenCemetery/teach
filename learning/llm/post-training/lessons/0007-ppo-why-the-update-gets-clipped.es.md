---
title: "7. PPO: por qué se recorta la actualización"
description: "Una gran victoria en un lote de datos muestreados no es evidencia fiable para dar un gran paso; PPO se niega a creérsela del todo"
type: lesson
---

# Lección 7. PPO: por qué se recorta la actualización

**Vínculo con la misión:** Derivar el objetivo de RLHF (lección 6) significa poco sin saber qué hace realmente "optimizar la policy contra él con PPO". Esta lección aporta ese mecanismo, que el resto de la etapa 4 y la etapa de criterio de la misión necesitan que sepas nombrar de forma concreta en lugar de tratarlo como una caja negra.
**Fuente principal:** [Paper: "Proximal Policy Optimization Algorithms", Schulman et al., 2017](https://arxiv.org/abs/1707.06347)
**Requisitos previos:** [Lección 6](0006-the-rlhf-objective-reward-minus-a-kl-penalty.md)

## Calentamiento

1. ▢ En el objetivo de RLHF, ¿qué le pasa a la policy cuando el coeficiente de la penalización KL `β` se acerca a cero?

<details markdown="1"><summary>Comprobación</summary>

La penalización por divergir de la policy SFT casi desaparece, así que el objetivo se reduce a perseguir la puntuación del reward model con casi nada que frene a la policy, y la pone en riesgo del reward hacking que describió la lección 5.

</details>

2. ▢ ¿Cuál es la diferencia entre "PPO" y "PPO-ptx" en la nomenclatura de Ouyang et al., y qué término los distingue?

<details markdown="1"><summary>Comprobación</summary>

"PPO" fija en 0 el coeficiente del gradiente de preentrenamiento `γ`; "PPO-ptx" usa una `γ` distinta de cero, que mezcla en el entrenamiento los gradientes de la log-verosimilitud de los datos de preentrenamiento, lo que reduce el impuesto de alineación.

</details>

## Qué debes saber

### El problema de una actualización sin restricciones

Schulman et al. parten de un objetivo sustituto más simple, el que maximizaría directamente un método "vanilla" de policy gradient: `L^CPI(θ) = E[r_t(θ) · Â_t]`, donde `r_t(θ) = policy(a|s) / policy_old(a|s)` es el cociente entre la probabilidad que la policy nueva y la antigua dan a la acción realmente tomada, y `Â_t` es la **ventaja** estimada, a grandes rasgos, cuánto mejor o peor resultó esa acción de lo esperado. Maximizar `L^CPI` sin ninguna restricción más da al optimizador todos los incentivos para empujar `r_t(θ)` tan lejos como pueda en la dirección que aumente el objetivo. Schulman et al. enuncian directamente el problema: "sin una restricción, la maximización de `L^CPI` llevaría a una actualización de la policy excesivamente grande". Una ventaja estimada grande en un lote muestreado no es evidencia fiable de que sea seguro dar en todas partes un paso igual de grande; reaccionar en exceso a ella puede desestabilizar el entrenamiento.

### El arreglo de PPO: recortar el cociente y tomar el caso pesimista

El objetivo real de Schulman et al. es:

```text
L^CLIP(θ) = E[ min( r_t(θ)·Â_t, clip(r_t(θ), 1-ε, 1+ε)·Â_t ) ]
```

con `ε` una constante pequeña (usan `0.2`). El término `clip(...)` limita el cociente `r_t(θ)` al intervalo `[1-ε, 1+ε]`, lo que elimina el incentivo para empujarlo más allá de ese rango. Tomar el `min` de las versiones recortada y sin recortar, en lugar de solo la versión recortada, es lo que hace de esto una **cota pesimista**: Schulman et al. explican que este esquema "solo ignora el cambio en el cociente de probabilidades cuando haría que el objetivo mejorase, y lo incluye cuando hace que el objetivo empeore". En términos llanos, un movimiento que parece estar ayudando queda limitado en lugar de recompensado por completo, de modo que el optimizador no puede extraer crédito ilimitado de un solo lote alentador, mientras que un movimiento que en realidad perjudica no queda protegido por el mismo límite, y su costo completo sigue contando.

### Por qué este es un tipo de control de estabilidad distinto de la penalización KL

La penalización KL de la lección 6 y el recorte de esta lección son ambos mecanismos de estabilidad, pero operan en ámbitos distintos y no deben confundirse. La penalización KL mide la policy entrenada frente al **modelo de referencia SFT** original y fijo, y limita cuánto se le permite a toda la ejecución de entrenamiento desviarse de ese punto fijo a lo largo de todo su curso. El recorte de PPO compara la policy con **ella misma justo antes de la actualización actual** (`policy_old`), y limita lo grande que puede ser cualquier paso de optimización individual, con independencia de dónde esté la policy en ese momento respecto del modelo SFT. Uno controla la deriva total de la ejecución; el otro controla el tamaño de cada paso individual por el camino. Se necesitan ambos, y ninguno sustituye al otro: un recorte pequeño por paso no impide que muchos pasos pequeños acaben desviándose lejos del modelo de referencia, y una penalización KL contra el modelo de referencia no hace nada para impedir que un paso cualquiera sea destructivamente grande.

## Práctica

1. ▢ Un solo lote de completions muestreadas produce una ventaja estimada inusualmente grande para una acción, solo por cómo se muestreó casualmente ese lote. ¿Por qué es arriesgado dejar que la policy se actualice por completo en proporción a esa ventaja, sin ningún límite?

<details markdown="1"><summary>Comprobación</summary>

Porque la ventaja estimada de un lote no es evidencia fiable de que un cambio igual de grande sea seguro en todas partes; reaccionar en exceso a una sola muestra alentadora (o desalentadora) puede empujar a la policy una distancia excesivamente grande en un paso, que es exactamente la inestabilidad que el recorte de PPO está hecho para evitar.

</details>

2. ▢ ¿Por qué PPO toma el mínimo de los términos sustitutos recortado y sin recortar, en lugar de usar solo el término recortado?

    - a) Tomar el mínimo hace del objetivo una cota pesimista: un movimiento que parece una mejora queda limitado, mientras que un movimiento que parece perjudicial no queda protegido por el mismo límite y sigue contando por completo
    - b) El mínimo solo se usa por eficiencia computacional y no tiene efecto en la policy aprendida
    - c) Usar solo el término recortado dejaría el cociente sin acotar
    - d) El mínimo garantiza que el cociente sea siempre exactamente 1

<details markdown="1"><summary>Comprobación</summary>

**a)** es el razonamiento enunciado por el propio Schulman et al. (b) resta importancia a un efecto real sobre el comportamiento de la optimización. (c) entiende al revés el propósito real del recorte; el recorte acota el cociente, no lo deja sin acotar. (d) interpreta mal lo que hace el recorte; el cociente se acota a un intervalo en torno a 1, no se fuerza a ser exactamente 1.

</details>

3. ▢ La configuración de RLHF de un equipo usa un coeficiente de penalización KL `β` grande pero ningún recorte por paso (un objetivo sustituto sin recortar). ¿Está esta configuración protegida contra una única actualización de la policy destructivamente grande?

<details markdown="1"><summary>Comprobación</summary>

No. Una `β` grande limita cuánto puede desviarse la policy del modelo de referencia SFT a lo largo del entrenamiento, pero no hace nada para impedir que una actualización individual, basada en la ventaja estimada de un lote, sea excesivamente grande. Son dos controles de estabilidad distintos, y quitar uno no lo compensa el otro.

</details>

## Prácticas en el mundo real

- [ ] Busca dónde expone el parámetro de recorte una implementación de PPO a la que tengas acceso (a menudo con un nombre como `epsilon`, `clip_range` o similar), y anota su valor por defecto frente al `0.2` que informan usar Schulman et al.
- [ ] Lee el párrafo del paper de PPO (enlazado arriba) que describe por qué `L^CPI` por sí solo llevaría a una actualización excesivamente grande, y escribe una frase con tus propias palabras que explique qué tiene concretamente un objetivo sustituto sin restricciones que lo causa.
- [ ] Mañana: sin mirar adelante, escribe una predicción de una frase para la lección 8: dado que RLHF necesita ahora una policy, un modelo de referencia (SFT) congelado para la penalización KL, un reward model y algo que produzca las estimaciones de ventaja de las que depende la fórmula de recorte de esta lección, ¿cuántos modelos grandes distintos esperas que intervengan en un solo paso de entrenamiento de PPO?

## Para profundizar

- [Paper: "Proximal Policy Optimization Algorithms", Schulman et al., 2017](https://arxiv.org/abs/1707.06347)
- [Recursos](../RESOURCES.md)

---

¿No termina de quedar claro? Vuelve a leer la fuente primaria de arriba, ya que esta lección la comprime y en la compresión es donde se escapa la comprensión. Consulta el [glosario](../GLOSSARY.md) por si algún término te resultó resbaladizo.

Si lo poco claro es la propia lección y no el material, eso es un defecto: [abre un issue](https://github.com/TokenCemetery/teach/issues).
