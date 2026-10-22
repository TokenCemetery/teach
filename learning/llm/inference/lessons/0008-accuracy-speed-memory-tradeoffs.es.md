---
title: "8. Compromisos entre precisión, velocidad y memoria"
description: "Por qué la memoria, la velocidad y la precisión no se mueven juntas cuando se cuantiza un modelo, y cómo se mide realmente cada una"
type: lesson
---

# Lección 8. Compromisos entre precisión, velocidad y memoria

**Vínculo con la misión:** La lección 7 nombró los esquemas; esta lección es lo que hace defendible una elección de cuantización, porque la memoria, la velocidad y la precisión se mueven cada una en una cantidad distinta y por una razón distinta cuando se cuantizan los pesos.
**Fuente principal:** [Paper: "GPTQ: Accurate Post-Training Quantization for Generative Pre-trained Transformers", Frantar et al., 2023](https://arxiv.org/abs/2210.17323)
**Requisitos previos:** [Lección 7](0007-quantization-schemes.md), [KV cache](../GLOSSARY.md)

## Calentamiento

1. ▢ ¿Por qué cuantizar los pesos de un modelo acelera específicamente el decode, y no la inferencia en general?

<details markdown="1"><summary>Comprobación</summary>

El decode está limitado por el ancho de banda de memoria: cada paso vuelve a leer los pesos de la memoria, y cuantizarlos reduce cuántos bytes tiene que mover esa lectura. La aceleración viene de menos tráfico de memoria por paso, el cuello de botella exacto que tiene el decode.

</details>

2. ▢ ¿Aproximadamente qué fracción de la memoria de pesos en fp16 usa la cuantización int4?

<details markdown="1"><summary>Comprobación</summary>

Aproximadamente una cuarta parte, ya que int4 empaqueta dos pesos por byte donde fp16 usaba dos bytes por peso, una reducción de 8x: a una cuarta parte de fp16, y luego a la mitad otra vez desde int8.

</details>

## Qué debes saber

### La memoria es la más predecible de las tres

El ahorro de memoria de la cuantización es casi aritmético: int8 reduce a la mitad la huella de fp16, int4 la reduce a una cuarta parte, porque el ancho de bits fija directamente cuántos bytes ocupa un peso. Es el único eje al que las cifras de la lección 7 se aplican con limpieza, y se cumple sin importar qué esquema, redondeo ingenuo, GPTQ o AWQ, produjo los pesos cuantizados.

### La velocidad no sigue la misma proporción

A menudo hay que **descuantizar** un peso cuantizado a una precisión mayor justo antes de que se ejecute la multiplicación de matrices real, porque el hardware de multiplicación espera esa precisión. Cuando ese paso de descuantización cuesta tiempo por sí mismo, la aceleración en tiempo real puede quedar muy por debajo de la proporción de ahorro de memoria: un peso 4x más pequeño no significa automáticamente un paso 4x más rápido, sino solo un paso con 4x menos datos que mover antes de la sobrecarga que añada descuantizarlo. Los stacks de serving cierran esa brecha con kernels escritos para operar directamente sobre el formato cuantizado, pero cuánto de la aceleración teórica de memoria sobrevive depende del kernel, no solo del ancho de bits.

La velocidad tampoco se beneficia por igual a lo largo de una solicitud. El decode, al estar limitado por el ancho de banda de memoria, es donde compensa una huella de pesos menor: menos que leer, menos tiempo leyéndolo. El prefill, al estar limitado por cómputo (lección 3), gasta su tiempo en la propia multiplicación de matrices, no en leer pesos repetidamente, así que la misma cuantización que acelera de forma notable el decode compra mucho menos al prefill, a veces casi nada.

### La precisión necesita una cifra, no una impresión

Que un modelo cuantizado produzca texto de aspecto plausible no es evidencia de que su precisión se haya mantenido: la fluidez es barata, y un modelo puede parecer coherente y seguir siendo medible peor que su original en fp16 en la tarea que importa. La pérdida de precisión de la cuantización se mide, normalmente como **perplejidad** (perplexity, lo bien que el modelo predice texto held-out; más alta significa peor) en un conjunto de evaluación estándar, o como el cambio de puntuación en un benchmark específico de la tarea que le importa de verdad a la carga de trabajo. La propia evaluación de GPTQ reporta exactamente esto: la perplejidad medida frente al modelo sin cuantizar con cada ancho de bits, no una lectura cualitativa de salidas de muestra.

### Los tres ejes se compensan, pero no al unísono

Pasar de fp16 a int8 suele costar muy poca precisión medida a cambio de reducir la memoria a la mitad. Pasar de int8 a int4 compra otra gran reducción de memoria pero suele costar desproporcionadamente más precisión que el paso a int8, que es exactamente por lo que existen GPTQ y AWQ: para mantener ese costo de precisión de int4 tan pequeño como no puede el redondeo ingenuo. Ninguno de los tres ejes es gratis, y ninguno escala con los otros en una proporción fija, por lo que una elección defendible necesita una cifra para cada uno, y no la suposición de que reducir uno reduce los demás en la misma cantidad.

## Práctica

1. ▢ Un equipo cuantiza un modelo a int4 y observa que sigue escribiendo texto fluido y coherente con un puñado de prompts manuales. ¿Es evidencia suficiente de que la cuantización no dañó la precisión? ¿Por qué sí o por qué no?

<details markdown="1"><summary>Comprobación</summary>

No. La fluidez no es lo mismo que la corrección o la precisión en la tarea; un modelo puede parecer coherente y puntuar medible peor en perplejidad o en un benchmark de la tarea. La pérdida de precisión necesita una cifra medida, como la perplejidad frente al modelo sin cuantizar o una diferencia de puntuación en un benchmark, no una lectura cualitativa de unas pocas salidas.

</details>

2. ▢ Un modelo se cuantiza a int4, lo que da una reducción teórica de memoria de 4x frente a fp16. ¿Por qué podría la aceleración medida del decode ser menor que 4x?

<details markdown="1"><summary>Pista</summary>

Piensa en qué tiene que ocurrir con un peso cuantizado justo antes de la multiplicación de matrices que lo usa.

</details>

<details markdown="1"><summary>Comprobación</summary>

Los pesos cuantizados a menudo necesitan descuantizarse a una precisión mayor justo antes de que se ejecute la multiplicación, ya que el hardware de multiplicación espera esa precisión. Si ese paso de descuantización tarda tiempo por sí mismo, se come la aceleración que la menor huella de memoria compraría de otro modo, así que la ganancia en tiempo real puede quedar por debajo de la proporción de memoria a menos que el kernel opere directamente sobre el formato cuantizado.

</details>

3. ▢ La misma cuantización a int4 se aplica a la fase de prefill y a la fase de decode de una solicitud. ¿Qué fase ve la mayor aceleración, y por qué?

<details markdown="1"><summary>Comprobación</summary>

El decode. Está limitado por el ancho de banda de memoria, así que leer una huella de pesos menor acorta directamente el paso. El prefill está limitado por cómputo: su tiempo lo domina la propia multiplicación de matrices, no la lectura de pesos, así que la misma reducción de memoria le compra mucha menos aceleración, a veces casi ninguna.

</details>

4. ▢ ¿Qué afirmación es verdadera del compromiso entre precisión, velocidad y memoria al pasar de int8 a int4?

    - a) Las tres mejoran en el mismo factor, ya que ambos son pasos de 8 bits por debajo de fp16
    - b) La memoria mejora de forma predecible, pero la ganancia de velocidad y el costo de precisión no escalan con ella en la misma proporción
    - c) La velocidad y la memoria mejoran juntas, y la precisión no se ve afectada por debajo de 8 bits
    - d) La pérdida de precisión es fija sin importar el ancho de bits, así que solo se compensan la memoria y la velocidad

<details markdown="1"><summary>Comprobación</summary>

**b)** La memoria baja en una proporción aritmética predecible, pero la aceleración en tiempo real depende de la sobrecarga de descuantización y del soporte del kernel, y el costo de precisión suele crecer más rápido de lo que lo hizo en el paso a int8. (a) es falsa: de int8 a int4 es un solo paso, no dos pasos iguales de 8 bits, y las ganancias no son uniformes entre ejes. (c) es falsa: la pérdida de precisión de int4 es medible y normalmente mayor que la de int8, que es por lo que existen GPTQ y AWQ. (d) es falsa: la pérdida de precisión generalmente crece a medida que baja el ancho de bits, no es fija.

</details>

## Prácticas en el mundo real

- [ ] Encuentra un benchmark publicado que compare la perplejidad o la puntuación en una tarea de un modelo en fp16, int8 e int4 (un model card o la tabla de evaluación de un paper) y anota cuánto costó realmente cada paso, en las cifras del propio paper.
- [ ] Encuentra la página de benchmark o de documentación de tu stack de serving que compare el throughput medido con distintos niveles de cuantización, y compara la aceleración reportada con la proporción teórica de memoria que esperarías.
- [ ] Mañana: para una carga de trabajo que tengas en mente, anota qué métrica de precisión comprobarías realmente antes de lanzar un modelo cuantizado, y qué caída de puntuación considerarías aceptable.

## Para profundizar

- [Paper: "GPTQ: Accurate Post-Training Quantization for Generative Pre-trained Transformers", Frantar et al., 2023](https://arxiv.org/abs/2210.17323)
- [Docs: "Optimizing inference", Hugging Face Transformers](https://huggingface.co/docs/transformers/main/en/llm_optims)
- [Recursos](../RESOURCES.md)

---

¿No termina de quedar claro? Vuelve a leer la fuente primaria de arriba, ya que esta lección la comprime y en la compresión es donde se escapa la comprensión. Consulta el [glosario](../GLOSSARY.md) por si algún término te resultó resbaladizo.

Si lo poco claro es la propia lección y no el material, eso es un defecto: [abre un issue](https://github.com/TokenCemetery/teach/issues).
