---
title: "6. El objetivo de RLHF: recompensa menos una penalización KL"
description: "Un término persigue la puntuación del reward model; un segundo término es la correa que impide que la policy se escape con ella"
type: lesson
---

# Lección 6. El objetivo de RLHF: recompensa menos una penalización KL

**Vínculo con la misión:** "Derivar el objetivo de RLHF (recompensa menos una penalización KL frente a un modelo de referencia) y decir qué le pasa a la policy cuando se afloja la penalización KL" es el tercer punto de Cómo se ve el éxito. Esta lección cubre el objetivo en sí; la lección 7 cubre PPO, el algoritmo que se usa para optimizarlo, y la lección 8 cubre lo que cuesta ejecutar todo esto.
**Fuente principal:** [Paper: "Training language models to follow instructions with human feedback", Ouyang et al., 2022](https://arxiv.org/abs/2203.02155)
**Requisitos previos:** [Lección 5](0005-reward-hacking.md)

## Calentamiento

1. ▢ ¿En qué convergieron las policies de Bai et al. cuando se optimizaron en exceso para la inocuidad, y por qué ese comportamiento era una manera barata de puntuar bien?

<details markdown="1"><summary>Comprobación</summary>

En la evasión generalizada: recomendar a los usuarios buscar terapia o ayuda profesional ante casi cualquier pregunta mínimamente sensible. Requería muy poca sofisticación, esencialmente solo clasificar una petición como sensible y rechazarla, que es mucho más fácil que ser genuinamente matizado, útil e inocuo.

</details>

2. ▢ ¿Qué indicó la divergencia entre train PM y test PM de Bai et al. cuando apareció?

<details markdown="1"><summary>Comprobación</summary>

Que la policy probablemente estaba optimizada en exceso específicamente contra el train PM, aprovechando un comportamiento que este recompensa y que un reward model held-out, nunca entrenado para esperar esta policy exacta, no recompensa tanto.

</details>

## Qué debes saber

### El objetivo completo

Ouyang et al. enuncian el objetivo exacto que maximiza su entrenamiento con PPO:

```text
objective(φ) = E[(x,y) ~ policy] [ r(x, y) − β · log( policy(y|x) / SFT(y|x) ) ]
             + γ · E[x ~ pretraining data] [ log( policy(x) ) ]
```

Tres piezas hacen aquí tres trabajos distintos, y conviene tomarlas de una en una.

### El término de recompensa

`r(x, y)` es la puntuación escalar del reward model entrenado (lección 4) para la propia salida `y` de la policy al prompt `x`. Maximizar solo este término es lo que empuja a la policy hacia las salidas que el reward model puntúa alto, exactamente el objetivo al que sirve el modelado de recompensa.

### El término de penalización KL

`β · log( policy(y|x) / SFT(y|x) )` compara la probabilidad de que la policy entrenada produzca `y` con la probabilidad de que el modelo SFT original produzca la misma `y`, y resta una penalización proporcional a cuánto mayor se ha vuelto la probabilidad de la propia policy. Ouyang et al. lo describen directamente como una **penalización KL por token respecto del modelo SFT**, añadida específicamente **para mitigar la sobreoptimización del reward model**, el fallo exacto que describió la lección 5. El término de recompensa solo da a la policy todos los incentivos para desviarse tanto como necesite para maximizar `r(x, y)`; el término KL es lo que hace que alejarse de la distribución de SFT cueste algo, en lugar de ser gratis.

### Qué pasa cuando β se afloja o se aprieta

`β` es un dial, y ambas direcciones tienen un costo real:

- A medida que `β` se acerca a cero, la penalización por divergir de la policy SFT casi desaparece, y el objetivo se reduce a perseguir la puntuación del reward model con casi nada que frene a la policy. Esta es precisamente la optimización sin restricciones de la que es evidencia la divergencia entre train PM y test PM de la lección 5: cuanto menos restringe la penalización KL a la policy, más margen tiene para aprovechar lo que el reward model recompense, en lugar de lo que sus diseñadores querían realmente.
- A medida que `β` crece, la penalización por alejarse de la policy SFT domina el objetivo, y la policy entrenada es arrastrada de vuelta a reproducir casi exactamente el modelo SFT. Llevado lo bastante lejos, esto anula por completo el propósito de la fase de RL: si la policy no puede alejarse de forma significativa de lo que SFT ya producía, RLHF no tiene nada que añadir encima.

Elegir `β` es elegir un punto de este compromiso, no eliminarlo: una `β` menor arriesga el reward hacking que describió la lección 5; una `β` mayor arriesga que RLHF aporte poco más allá de lo que SFT solo ya conseguía.

### El término del gradiente de preentrenamiento, y su conexión con la lección 1

El último término, `γ · E[log(policy(x))]`, es independiente por completo del compromiso entre recompensa y KL: mezcla un objetivo ordinario de modelado de lenguaje sobre la distribución de preentrenamiento original, aumentando la verosimilitud que la policy da al tipo de texto con el que se preentrenó. Ouyang et al. fijan `γ = 0` para lo que llaman modelos "PPO" simples, y usan una `γ` distinta de cero para lo que llaman modelos "PPO-ptx". Este término es el mecanismo real detrás de la mitigación del impuesto de alineación de la lección 1: volver a mezclar en el entrenamiento con PPO los gradientes de los datos de preentrenamiento es lo que recuperó buena parte de la regresión de rendimiento en benchmarks públicos de NLP que introducía el entrenamiento con PPO puro, sin renunciar a las ganancias de preferencia para las que se construyó RLHF.

## Práctica

1. ▢ Un equipo fija `β` en un valor muy pequeño en el objetivo de RLHF. ¿De qué pone esto más directamente en riesgo a la policy, y por qué?

<details markdown="1"><summary>Comprobación</summary>

Del reward hacking: con la penalización KL casi eliminada, el término de recompensa domina el objetivo casi sin oposición, y da a la policy poca razón para no desviarse hacia lo que el reward model puntúe alto, sea o no ese comportamiento lo que el reward model pretendía representar.

</details>

2. ▢ Un equipo fija en cambio `β` en un valor muy grande. ¿Cuál es el costo más probable de esta elección?

<details markdown="1"><summary>Comprobación</summary>

La policy es arrastrada de vuelta a reproducir de cerca el modelo SFT, ya que toda desviación significativa se penaliza con fuerza; llevado lo bastante lejos, esto deja poco margen para que RLHF añada ningún comportamiento más allá de lo que SFT solo ya producía.

</details>

3. ▢ ¿Cuál es la diferencia entre lo que Ouyang et al. llaman "PPO" y "PPO-ptx", y qué término del objetivo los distingue?

<details markdown="1"><summary>Comprobación</summary>

"PPO" fija en 0 el coeficiente del gradiente de preentrenamiento `γ`; "PPO-ptx" usa una `γ` distinta de cero, que mezcla en las actualizaciones de PPO los gradientes de la log-verosimilitud de los datos de preentrenamiento. Este es el término responsable de reducir el impuesto de alineación que presentó la lección 1.

</details>

4. ▢ ¿Cuál de estas describe mejor el papel que juegan en el objetivo el término de recompensa y el término de penalización KL?

    - a) El término de recompensa empuja a la policy hacia lo que el reward model puntúa alto; la penalización KL la arrastra de vuelta hacia el modelo SFT, y el objetivo equilibra ambos
    - b) Ambos términos empujan a la policy en la misma dirección, hacia las preferencias del reward model
    - c) La penalización KL solo se usa durante la evaluación, no durante el entrenamiento
    - d) El término de recompensa y el término de penalización KL son matemáticamente idénticos, solo que escalados de forma distinta

<details markdown="1"><summary>Comprobación</summary>

**a)** es la relación real: dos términos que tiran genuinamente en direcciones distintas, con `β` fijando el equilibrio entre ellos. (b), (c) y (d) describen mal la estructura del objetivo de maneras que la derivación de esta lección descarta directamente.

</details>

## Prácticas en el mundo real

- [ ] Busca dónde expone un framework de entrenamiento al que tengas acceso un coeficiente de penalización KL para RLHF (a menudo con un nombre como `beta` o `kl_coef`), y anota su valor por defecto y cualquier guía documentada para ajustarlo.
- [ ] Lee el párrafo del paper de InstructGPT (enlazado arriba) que describe el objetivo completo y escribe, en una frase cada una, qué le pasa al entrenamiento si `β` y `γ` se fijan ambas en cero a la vez.
- [ ] Mañana: sin mirar adelante, escribe una predicción de una frase para la lección 7: dado que este objetivo hay que maximizarlo ajustando los propios parámetros de la policy, y que una sola actualización basada en un lote de salidas muestreadas podría empujar a la policy muy lejos de golpe, ¿con qué problema podría toparse una optimización ingenua de este objetivo?

## Para profundizar

- [Paper: "Training language models to follow instructions with human feedback", Ouyang et al., 2022](https://arxiv.org/abs/2203.02155)
- [Recursos](../RESOURCES.md)

---

¿No termina de quedar claro? Vuelve a leer la fuente primaria de arriba, ya que esta lección la comprime y en la compresión es donde se escapa la comprensión. Consulta el [glosario](../GLOSSARY.md) por si algún término te resultó resbaladizo.

Si lo poco claro es la propia lección y no el material, eso es un defecto: [abre un issue](https://github.com/TokenCemetery/teach/issues).
