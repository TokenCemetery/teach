---
title: "8. Por qué PPO es caro e inestable"
description: "Cuatro modelos, y no uno, tienen que caber a la vez en memoria, y los dos que peor escalan son exactamente los que añade RLHF"
type: lesson
---

# Lección 8. Por qué PPO es caro e inestable

**Vínculo con la misión:** Derivar el objetivo de RLHF y su mecanismo de recorte (lecciones 6 y 7) explica qué optimiza PPO; esta lección explica lo que cuesta realmente ejecutarlo, que es lo que hace que DPO (etapa 5) merezca siquiera considerarse como alternativa.
**Fuente principal:** [Paper: "Training language models to follow instructions with human feedback", Ouyang et al., 2022](https://arxiv.org/abs/2203.02155)
**Requisitos previos:** [Lección 7](0007-ppo-why-the-update-gets-clipped.md)

## Calentamiento

1. ▢ ¿Por qué PPO recorta el cociente de probabilidades entre la policy nueva y la antigua, en lugar de dejar que el objetivo sustituto crezca sin límite?

<details markdown="1"><summary>Comprobación</summary>

Porque una ventaja estimada grande de un lote muestreado no es evidencia fiable de que una actualización de la policy igual de grande sea segura; el recorte acota cuánto puede mover la policy una sola actualización en respuesta a ella, y evita un paso destructivamente grande.

</details>

2. ▢ ¿Cuál es la diferencia de ámbito entre la penalización KL (lección 6) y el recorte por paso de PPO (lección 7)?

<details markdown="1"><summary>Comprobación</summary>

La penalización KL limita cuánto se desvía la policy del modelo de referencia SFT fijo a lo largo de toda la ejecución de entrenamiento. El recorte limita lo grande que puede ser cualquier paso de optimización individual respecto del propio estado de la policy justo antes de ese paso. Ninguno sustituye al otro.

</details>

## Qué debes saber

### Cuatro modelos, no uno

RLHF con PPO no es un solo modelo que se entrena; requiere varios modelos presentes a la vez, cada uno con un trabajo distinto: la **policy** que se entrena (inicializada desde el modelo SFT); una copia congelada del propio **modelo SFT**, mantenida solo para calcular la penalización KL (lección 6) contra ella; el **reward model** (lección 4), que puntúa las salidas muestreadas de la policy; y una **función de valor**, que se usa para producir las estimaciones de ventaja de las que depende el objetivo recortado de PPO (lección 7). Ouyang et al. enuncian directamente que su función de valor se inicializa desde el reward model, lo que la convierte en una copia completa de los parámetros de un modelo grande por derecho propio, distinta del propio reward model pese a compartir su punto de partida. Cuatro modelos grandes que ocupan memoria y consumen cómputo a la vez, en lugar de uno, es un costo real y estructural que nada tiene que ver con lo bien o mal que vaya el entrenamiento.

### De dónde viene concretamente la inestabilidad

Ouyang et al. dan un relato concreto de dónde interactúa mal la escala con esta configuración. Encontraron que un reward model de 175 mil millones de parámetros podía lograr una pérdida de validación menor que uno más pequeño, pero con dos costos: su entrenamiento era más inestable, lo que lo convertía en una peor opción para inicializar una función de valor de PPO, y usar a la vez un reward model y una función de valor de 175 mil millones de parámetros aumentaba sustancialmente los requisitos de cómputo de PPO además del costo de la propia policy. Su resolución fue práctica y no teórica: encontraron que un reward model de 6 mil millones de parámetros era estable en un amplio rango de learning rates y igual de eficaz para entrenar modelos PPO fuertes, y usaron ese único reward model de 6B para todos los tamaños de policy que entrenaron, incluida su policy de 175B.

### Por qué merece recordarse este compromiso concreto

Este es un resultado genuinamente contraintuitivo que conviene retener: un reward model más pequeño no fue un compromiso forzado por falta de recursos, fue la opción más fiable a la escala que probaron Ouyang et al. El entrenamiento de reward models y de funciones de valor, a muy gran escala, no hereda automáticamente el comportamiento de escalado más suave y predecible que muestra una pérdida directa de preentrenamiento (las leyes de escalado de la etapa 3, de otro track). La inestabilidad a escala no es solo una molestia que rodear; moldeó directamente lo que Ouyang et al. construyeron realmente, y es una razón real de que la configuración completa de PPO con cuatro o cinco modelos, ejecutada a la mayor escala posible en cada parte, sea cara de intentar y poco fiable aun cuando se intenta.

## Práctica

1. ▢ Nombra los cuatro modelos que intervienen en un paso de entrenamiento de PPO para RLHF, y para qué se usa cada uno.

<details markdown="1"><summary>Comprobación</summary>

La policy que se entrena; un modelo SFT congelado, que se usa para calcular la penalización KL; el reward model, que puntúa las salidas de la policy; y la función de valor (inicializada desde el reward model pero entrenada por separado), que produce las estimaciones de ventaja que necesita el objetivo recortado de PPO.

</details>

2. ▢ Según Ouyang et al., ¿qué dos costos venían con usar un reward model y una función de valor de 175B, aunque lograra una pérdida de validación menor que uno más pequeño?

<details markdown="1"><summary>Comprobación</summary>

Su entrenamiento era más inestable, lo que lo hacía una peor opción para inicializar una función de valor de PPO, y usarlo aumentaba sustancialmente los requisitos de cómputo de PPO, además del costo de la propia policy.

</details>

3. ▢ Un equipo supone que un reward model más grande y más preciso es siempre la mejor opción para RLHF, ya que logra una pérdida de validación menor. Según el propio hallazgo de Ouyang et al., ¿es segura esta suposición?

    - a) Sí, un reward model con menor pérdida es siempre la mejor opción sea cual sea la escala
    - b) No; un reward model de 175B tenía un entrenamiento más inestable y un mayor costo de cómputo, y un reward model más pequeño de 6B era estable e igual de eficaz para entrenar modelos PPO fuertes
    - c) No, porque los reward models más grandes no pueden usarse con PPO en absoluto
    - d) Sí, pero solo porque Ouyang et al. nunca probaron realmente un reward model de 175B

<details markdown="1"><summary>Comprobación</summary>

**b)** es exactamente el propio hallazgo de Ouyang et al.: una pérdida de validación menor no se tradujo en la mejor opción práctica una vez consideradas la estabilidad del entrenamiento y el costo de cómputo. (a) ignora el compromiso que ellos mismos informan. (c) exagera el hallazgo; el problema era la estabilidad y el costo, no una incompatibilidad. (d) es factualmente falsa; informan explícitamente haber probado y descartado la opción de 175B por estas razones.

</details>

## Prácticas en el mundo real

- [ ] Busca un informe técnico o una entrada de blog que describa una configuración real de entrenamiento de RLHF, y mira si indica los tamaños relativos de su policy, su reward model y su función de valor. Anota si el reward model iguala el tamaño de la policy o es deliberadamente más pequeño.
- [ ] Lee la sección del Apéndice C de Ouyang et al. sobre el entrenamiento del reward model (enlazado arriba) y escribe una frase sobre a qué encontraron que era sensible el entrenamiento, frente a a qué no lo era mucho.
- [ ] Mañana: sin mirar adelante, escribe una predicción de una frase para la etapa 5: dado que PPO necesita un reward model, una función de valor y un bucle de RL además de la propia policy, ¿qué tendría que hacer realmente de otra manera un método que produzca un resultado parecido sin un reward model aparte ni un bucle de RL?

## Para profundizar

- [Paper: "Training language models to follow instructions with human feedback", Ouyang et al., 2022](https://arxiv.org/abs/2203.02155)
- [Recursos](../RESOURCES.md)

---

La etapa 4 cubrió qué optimiza RLHF-PPO y lo que cuesta ejecutarlo. La etapa 5 cubre una alternativa construida específicamente para necesitar menos de ambas cosas: ningún reward model aparte, y ningún bucle de RL en absoluto.

¿No termina de quedar claro? Vuelve a leer la fuente primaria de arriba, ya que esta lección la comprime y en la compresión es donde se escapa la comprensión. Consulta el [glosario](../GLOSSARY.md) por si algún término te resultó resbaladizo.

Si lo poco claro es la propia lección y no el material, eso es un defecto: [abre un issue](https://github.com/TokenCemetery/teach/issues).
