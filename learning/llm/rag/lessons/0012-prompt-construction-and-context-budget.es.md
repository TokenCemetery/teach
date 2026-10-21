---
title: "12. Construcción del prompt y presupuesto de la ventana de contexto"
description: "Por qué los chunks recuperados compiten por un presupuesto compartido de la ventana de contexto, y por qué el lugar que ocupa un chunk en el prompt importa tanto como que se haya recuperado"
type: lesson
---

# Lección 12. Construcción del prompt y presupuesto de la ventana de contexto

**Vínculo con la misión:** La etapa 7 abre el último tramo de la misión: incluso un pipeline de recuperación perfectamente diagnosticado y bien ajustado (etapas 1 a 6) puede fallarle al usuario si los chunks recuperados se ensamblan mal en un prompt, que es un punto de fallo distinto de la propia recuperación.
**Fuente principal:** [Paper: "Lost in the Middle: How Language Models Use Long Contexts", Liu et al., 2023](https://arxiv.org/abs/2307.03172)
**Requisitos previos:** [Lección 11](0011-diagnosing-the-pipeline.md), [Chunk](../GLOSSARY.md)

## Calentamiento

1. ▢ ¿Cuál es la primera etapa que hay que comprobar al diagnosticar un contexto recuperado erróneo, y por qué se comprueba antes que nada?

<details markdown="1"><summary>Comprobación</summary>

El chunking: saca el chunk que debería haber respondido la consulta y comprueba si la información relevante existe de forma coherente en un solo lugar. Si el chunking partió o enterró la respuesta, ninguna etapa posterior (embedding, índice, ponderación híbrida, reranking) puede recuperar lo que nunca recibió una representación utilizable.

</details>

2. ▢ ¿Por qué diagnosticar sobre un conjunto pequeño de consultas fallidas conocidas es más fiable que depurar un único fallo anecdótico?

<details markdown="1"><summary>Comprobación</summary>

Una sola consulta fallida puede fallar por una razón inusual y aislada que no refleja un problema sistemático. Medir recall@k y MRR sobre un conjunto representativo de fallos revela dónde ocurre la mayor caída agregada y señala una etapa que pierde información de forma sistemática.

</details>

## Qué debes saber

### Los chunks recuperados son una partida de un presupuesto compartido

Una vez recuperados y ordenados los chunks (etapas 1 a 6), todavía tienen que pasar a formar parte de un prompt real: normalmente un mensaje de sistema o de instrucciones, los propios chunks recuperados y la pregunta del usuario, todo dentro de una única **ventana de contexto** finita. Esa ventana es un presupuesto real y compartido: los chunks recuperados compiten por espacio con el system prompt, con cualquier historial de conversación y con la propia pregunta, no solo entre ellos. Recuperar más chunks (una *k* mayor) no es gratis aunque todos sean genuinamente relevantes, ya que cada uno consume presupuesto de la ventana de contexto que otra cosa, más historial de conversación o un system prompt más largo, podría usar.

### Estar en el prompt no significa ser usado

La capacidad de un modelo para usar información depende de más que de que esa información esté técnicamente presente en la ventana de contexto. El hallazgo **"lost in the middle"** de Liu et al. muestra que los modelos usan la información situada muy cerca del principio o del final de un contexto largo con mucha más fiabilidad que la enterrada en el medio, incluso cuando la información enterrada está enteramente dentro del límite de contexto declarado del modelo. Un chunk muy relevante colocado en medio de un prompt largo y abarrotado de chunks puede ser en la práctica invisible para la generación, y producir una respuesta errónea o incompleta que parece un fallo de recuperación pero no lo es: el chunk se recuperó correctamente; simplemente no se colocó en un lugar desde el que el modelo lea de forma fiable.

![Una curva que traza cuán fiablemente usa un modelo una pieza de información recuperada según el lugar que ocupa esa información en el prompt ensamblado. La curva empieza alta cuando la información está cerca del principio, baja hasta su punto más bajo cuando la información está en medio del contexto y vuelve a subir cuando la información está cerca del final, una forma de valle y no una línea recta o plana. Un chunk colocado en medio de un prompt largo y abarrotado de chunks es el que se usa con menos fiabilidad, aunque esté técnicamente presente dentro de la ventana de contexto todo el tiempo.](images/lost-in-the-middle.svg)

### La consecuencia práctica al ensamblar un prompt

De ahí se siguen directamente dos consecuencias. Primera: meter muchos chunks marginales y de menor relevancia en el contexto "por si acaso" tiene un costo más allá del presupuesto de tokens: puede enterrar un chunk genuinamente bueno en medio del prompt y empeorar la respuesta, no solo encarecerla. Segunda: la posición de los chunks es una decisión deliberada, no un accidente del orden de inserción: colocar el chunk (o los chunks) más relevante cerca del principio o del final del contexto ensamblado, en lugar de donde haya caído tras la concatenación, importa para que la generación se apoye realmente en él.

## Práctica

1. ▢ ¿Por qué el presupuesto de la ventana de contexto es una preocupación de toda la petición y no algo sobre lo que la recuperación pueda razonar por sí sola?

<details markdown="1"><summary>Comprobación</summary>

Los chunks recuperados comparten la ventana de contexto con el system prompt, con cualquier historial de conversación y con la pregunta del usuario; el presupuesto disponible para los chunks recuperados depende de cuánto use todo lo demás de la petición, no solo de la calidad de la recuperación.

</details>

2. ▢ Describe el fenómeno "lost in the middle" y una implicación práctica que tiene para construir un prompt de RAG.

<details markdown="1"><summary>Comprobación</summary>

Los modelos usan la información del principio o del final de un contexto largo con mucha más fiabilidad que la enterrada en el medio, incluso cuando está técnicamente dentro de la ventana de contexto. Una implicación práctica: el chunk recuperado más relevante debería colocarse cerca del inicio o del final del prompt ensamblado, no dejarse donde el orden de concatenación lo haya puesto, y rellenar el prompt con muchos chunks extra marginales arriesga enterrar uno genuinamente útil en el medio.

</details>

3. ▢ Un equipo recupera los 20 primeros chunks "por si acaso", los coloca en orden de relevancia, pero los concatena de modo que el chunk más relevante queda en medio del contexto ensamblado. La generación pasa por alto una respuesta que sí estaba presente en ese chunk. ¿Qué salió probablemente mal y cuál es una solución?

<details markdown="1"><summary>Pista</summary>

Considera si esto es un fallo de recuperación o algo que ocurre después de que la recuperación tuvo éxito.

</details>

<details markdown="1"><summary>Comprobación</summary>

Esto no es un fallo de recuperación: el chunk correcto se recuperó. Es un fallo de construcción del prompt causado por el efecto lost-in-the-middle, ya que el chunk más relevante quedó situado en medio de un contexto largo, donde los modelos son menos fiables al usar información. Una solución: reordenar el prompt ensamblado para que el chunk más relevante quede cerca del principio o del final, o reducir el número de chunks incluidos para que el bueno no quede enterrado entre muchos de menor relevancia.

</details>

4. ▢ ¿Por qué "¿encontró la recuperación el chunk correcto?" (la pregunta de la etapa 6) y "¿hizo el prompt ensamblado que el modelo lo usara realmente?" son puntos de fallo distintos, aunque ambos puedan producir el mismo síntoma (una respuesta final errónea)?

<details markdown="1"><summary>Comprobación</summary>

El procedimiento de diagnóstico de la etapa 6 comprueba si el chunk correcto se recuperó y se ordenó lo bastante alto como para llegar siquiera a la generación; trata por completo del pipeline hasta ese punto. Si el modelo usa realmente un chunk que sí llegó al prompt es una pregunta aparte, regida por el lugar que ocupa ese chunk en el contexto ensamblado, que lost-in-the-middle muestra que importa con independencia de la calidad de la recuperación. Una respuesta errónea puede resultar de cualquiera de los dos fallos, pero requieren soluciones distintas.

</details>

5. ▢ ¿Qué afirmación es cierta sobre el presupuesto de la ventana de contexto y la posición de los chunks en un prompt de RAG?

    - a) Recuperar más chunks siempre es mejor, ya que más contexto solo puede ayudar al modelo
    - b) Un chunk técnicamente dentro de la ventana de contexto tiene garantizado que se usará igual sin importar dónde esté
    - c) Los chunks recuperados compiten por un presupuesto compartido con el resto de la petición, y el lugar donde se coloca un chunk en el prompt ensamblado afecta a si el modelo lo usa realmente
    - d) Lost-in-the-middle solo afecta a documentos muy largos, no a un prompt ensamblado con varios chunks recuperados separados

<details markdown="1"><summary>Comprobación</summary>

**c)** Tanto el punto del presupuesto compartido como el de la posición quedan establecidos en esta lección. (a) es falsa: más chunks cuestan presupuesto y pueden enterrar un chunk bueno en el medio, lo que perjudica en lugar de ayudar. (b) es falsa: eso es exactamente lo que lost-in-the-middle refuta. (d) es falsa: el efecto depende de la posición dentro del contexto en su conjunto, sin importar si ese contexto vino de un documento largo o de varios chunks concatenados.

</details>

## Prácticas en el mundo real

- [ ] Para un sistema RAG que ejecutes o pienses ejecutar, comprueba en qué lugar del prompt ensamblado suele acabar el chunk recuperado más relevante y si es una decisión deliberada o un accidente del orden de concatenación.
- [ ] Calcula, para una petición típica, qué parte del presupuesto total de tu ventana de contexto se gasta en el system prompt y el historial de conversación frente a los chunks recuperados.
- [ ] Mañana: prueba a reducir el número de chunks que recuperas para una consulta en la que la generación ahora parece pasar por alto información relevante y comprueba si eso solo cambia la calidad de la respuesta.

## Para profundizar

- [Paper: "Lost in the Middle: How Language Models Use Long Contexts", Liu et al., 2023](https://arxiv.org/abs/2307.03172)
- [Article: "Evaluation Measures for Search and Recommender Systems", Pinecone](https://www.pinecone.io/learn/offline-evaluation/)
- [Recursos](../RESOURCES.md)

---

¿No termina de quedar claro? Vuelve a leer la fuente principal de arriba, ya que esta lección la comprime y en la compresión es donde se escapa la comprensión. Consulta el [glosario](../GLOSSARY.md) por si algún término te resultó resbaladizo.

Si lo poco claro es la propia lección y no el material, eso es un defecto: [abre un issue](https://github.com/TokenCemetery/teach/issues).
