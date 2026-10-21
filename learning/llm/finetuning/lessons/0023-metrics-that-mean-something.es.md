---
title: "23. Métricas que significan algo"
description: "La pérdida selecciona checkpoints; las métricas de la tarea toman decisiones"
type: lesson
---

# Lección 23. Métricas que significan algo

**Vínculo con la misión:** "Demostrar que funcionó" está en la misión. Un número que no puedes defender no es una prueba.
**Fuente principal:** [Paper: "Judging LLM-as-a-Judge with MT-Bench and Chatbot Arena", Zheng et al., arXiv:2306.05685](https://arxiv.org/abs/2306.05685)
**Requisitos previos:** [Lección 22](0022-contamination-and-held-out-design.md), [Lección 12](0012-reading-a-training-run.md)

## Calentamiento

1. ▢ ¿Por qué tres particiones y no dos?

<details markdown="1"><summary>Comprobación</summary>

Seleccionar contra un conjunto se ajusta a él. La validación absorbe tu selección; el test queda intacto para poder dar una estimación sin sesgo.

</details>

2. ▢ ¿Aproximadamente cuántos ejemplos held-out hacen falta para detectar una diferencia de 2 puntos?

<details markdown="1"><summary>Comprobación</summary>

Miles. El requisito crece de forma cuadrática a medida que se reduce la diferencia.

</details>

3. ▢ Nombra dos cosas que la pérdida no puede ver.

<details markdown="1"><summary>Comprobación</summary>

Si las generaciones son utilizables, y si las capacidades fuera de la distribución de la tarea se han degradado.

</details>

## Qué debes saber

### Por qué la pérdida no es la métrica

La pérdida de entropía cruzada sobre datos held-out es genuinamente útil: es barata, es estable y es lo correcto para vigilar durante una ejecución. No es una medida de si el modelo hace tu trabajo.

La pérdida mide la sorpresa del siguiente token frente a una continuación de referencia concreta. Por tanto penaliza una respuesta correcta formulada con otras palabras y premia una equivocada pero fluida. Dos modelos con la misma pérdida held-out pueden diferir sustancialmente en utilidad, y la dirección no es predecible.

**Usa la pérdida para seleccionar checkpoints. Usa una métrica de la tarea para las decisiones.**

### Elegir según la forma de la tarea

| Forma de la tarea | Métrica | Atención a |
|---|---|---|
| Clasificación | Accuracy; precisión y recall por clase; F1 | El desequilibrio de clases vuelve sin sentido a la accuracy |
| Extracción | Coincidencia exacta en el campo; F1 sobre spans | Normaliza antes de comparar |
| Salida estructurada | Tasa de validez del esquema, luego corrección a nivel de campo | Dos fallos separados, mide ambos |
| Código | Ejecución contra tests | Que pasen los tests, no que se parezca a la referencia |
| Generación de texto libre | Puntuación con rúbrica, por humano o por modelo | El caso difícil; ver más abajo |
| Cercana a la recuperación | Groundedness, precisión de las citas | La fluidez enmascara afirmaciones sin respaldo |

Observa lo que falta: para cualquier cosa con una respuesta comprobable, **comprueba la respuesta.** Ejecuta el código. Valida el esquema. Compara el campo extraído. Es barato, objetivo y muy superior a cualquier puntuación de similitud.

### Sobre las métricas de similitud superficial

BLEU, ROUGE y sus parientes miden el solapamiento de n-gramas con una referencia. Se construyeron para traducción automática y resumen, y para las tareas de seguimiento de instrucciones son débiles: una respuesta correcta formulada de otra manera puntúa mal, una equivocada que reutiliza el vocabulario de la referencia puntúa bien.

Úsalas solo cuando el solapamiento sea genuinamente lo que te importa, y nunca como única métrica. Si te descubres optimizando ROUGE en una tarea que no es de resumen, detente.

### Salida estructurada: dos fallos, dos números

Para JSON o cualquier esquema, reporta siempre ambos:

1. **Validez.** ¿Se parseó y cumplió el esquema?
2. **Corrección.** Dado que se parseó, ¿son correctos los valores?

Colapsarlos oculta qué problema tienes. Un modelo con 99% de validez y 60% de corrección necesita mejores datos. Uno con 60% de validez y 95% de corrección necesita entrenamiento de formato, o decodificación restringida en el momento de servir, que puede hacer desaparecer el problema sin reentrenar en absoluto.

### Modelo como juez, usado con cuidado

Para salida de texto libre, que un modelo fuerte puntúe contra una rúbrica suele ser la única opción escalable. Funciona, y tiene sesgos documentados que debes controlar:

- **Sesgo de posición.** Los jueces favorecen la respuesta que se presenta primero. Mitígalo aleatorizando el orden y, en la comparación por pares, evaluando ambos órdenes.
- **Sesgo de verbosidad.** Las respuestas más largas puntúan más alto con independencia de la calidad. Vigila si tu fine-tune simplemente se volvió más verboso.
- **Autopreferencia.** Los jueces tienden a favorecer el texto que se parece a su propia salida.
- **Sensibilidad a la rúbrica.** Pequeños cambios de redacción en la rúbrica desplazan las puntuaciones de forma material.

El paso innegociable: **calibra el juez contra etiquetas humanas.** Puntúa tú mismo de 50 a 100 ejemplos, ejecuta el juez sobre los mismos y mide el acuerdo. Si el acuerdo es pobre, los números del juez son decoración. Si es bueno, te has ganado el derecho a escalarlo, y tienes un número que cuantifica cuánto confiar en él.

Una configuración concreta y robusta: comparación por pares de la salida del base frente a la del fine-tune, en ambos órdenes, con una rúbrica que nombre los criterios concretos que te importan, reportada como win rate. El juicio por pares es más fiable que la puntuación absoluta, que deriva.

### Reporta la incertidumbre o no reportes nada

Un número suelto sin dispersión no es un resultado. Estándar mínimo:

- **Intervalos de confianza** sobre la métrica. Para una proporción, bootstrap o un intervalo binomial.
- **Varias seeds** al comparar configuraciones de entrenamiento, ya que la varianza de una ejecución a otra suele ser mayor que el efecto.
- **Comparación pareada** sobre ejemplos idénticos (lección 22).
- **La n** sobre la que se calcula el número, declarada.

"71.2 frente a 70.8" no es un hallazgo. "71.2 ± 2.1 frente a 70.8 ± 1.9 sobre n=340, tres seeds" es un hallazgo, y el hallazgo es que no has detectado una diferencia.

### Lee las salidas

Sea cual sea tu métrica, lee cada vez una muestra de generaciones reales, incluidos los fallos. Las métricas comprimen, y lo que comprimen suele ser lo que necesitabas saber: el modelo ha empezado a rechazar, o a emitir un preámbulo, o a truncar, o a responder una pregunta sutilmente distinta. Ningún agregado lo revela. Diez minutos de lectura sí.

## Práctica

1. ▢ Dos modelos tienen idéntica pérdida held-out. ¿Puede uno ser sustancialmente más útil?

<details markdown="1"><summary>Comprobación</summary>

Sí. La pérdida mide el acuerdo con una continuación de referencia, así que penaliza respuestas correctas formuladas de otro modo y premia las equivocadas pero fluidas.

Una pérdida igual es compatible con una gran diferencia en el rendimiento en la tarea, en cualquier dirección. Por eso la pérdida selecciona checkpoints y las métricas de la tarea toman decisiones.

</details>

2. ▢ Tu modelo emite JSON. ¿Qué dos números reportas, y por qué no uno?

<details markdown="1"><summary>Comprobación</summary>

Tasa de validez del esquema, y corrección a nivel de campo entre las salidas válidas.

Un único número combinado oculta qué problema tienes. Alta validez con baja corrección es un problema de datos; baja validez con alta corrección es un problema de formato que la decodificación restringida puede resolver sin reentrenar.

</details>

3. ▢ La puntuación del juez de tu fine-tune subió de 6.2 a 7.1. La longitud media de las respuestas subió de 90 a 340 tokens. ¿Preocupación?

<details markdown="1"><summary>Comprobación</summary>

Sí: sesgo de verbosidad. Los jueces favorecen de forma fiable las respuestas más largas con independencia de la calidad, así que buena parte de esa mejora puede ser longitud.

Contrólalo: compara con longitudes igualadas, indica expresamente al juez que ignore la longitud, o comprueba si los usuarios prefieren de verdad la salida más larga. La puntuación por sí sola no distingue "mejor" de "más largo".

</details>

4. ▢ ¿Qué métrica evalúa mejor un fine-tune de generación de código?

    - a) ROUGE contra la implementación de referencia proporcionada
    - b) Ejecución contra una suite de tests para cada problema
    - c) Pérdida de entropía cruzada held-out sobre los tokens de código
    - d) Un modelo juez que puntúe legibilidad y corrección

<details markdown="1"><summary>Comprobación</summary>

**b)** Ejecución contra una suite de tests para cada problema.

El código tiene un criterio objetivo de corrección, así que úsalo. Las métricas de solapamiento premian parecerse a la referencia en lugar de funcionar; la pérdida tiene el mismo problema; un juez es una indirección innecesaria cuando puedes simplemente ejecutar el código.

</details>

5. ▢ ¿Qué único paso te gana el derecho a confiar en un modelo juez a escala?

<details markdown="1"><summary>Comprobación</summary>

Calibrarlo contra etiquetas humanas, puntuando tú mismo de 50 a 100 ejemplos y midiendo el acuerdo con el juez sobre los mismos elementos.

Sin eso, los números del juez no están validados. Con eso, tienes tanto justificación como un grado cuantificado de confianza.

</details>

6. ▢ Tu fine-tune de clasificador reporta un 94% de accuracy. ¿Qué necesitas saber antes de creer que significa algo?

<details markdown="1"><summary>Comprobación</summary>

La distribución de clases. Si el 94% de los ejemplos pertenecen a una clase, un modelo que siempre adivina esa clase puntúa 94% y no ha aprendido nada.

Reporta precisión y recall por clase, o una métrica equilibrada. La accuracy sobre datos desequilibrados es uno de los números más engañosos de uso común.

</details>

## Prácticas en el mundo real

- [ ] Elige tu métrica principal y escribe un párrafo defendiendo por qué mide lo que te importa. Nombra lo que se le escapa.
- [ ] Calcula un intervalo de confianza sobre tu métrica actual. Decide si tu conjunto held-out puede sostener la comparación que quieres.
- [ ] Si usas un modelo juez: etiqueta a mano 50 ejemplos, ejecuta el juez sobre los mismos y reporta el acuerdo.
- [ ] Mañana: lee veinte generaciones reales, incluido cada fallo. Anota una cosa que la métrica no te dijo.

## Para profundizar

- [Paper: "Judging LLM-as-a-Judge with MT-Bench and Chatbot Arena", Zheng et al., arXiv:2306.05685](https://arxiv.org/abs/2306.05685)
- [Code: lm-evaluation-harness, EleutherAI](https://github.com/EleutherAI/lm-evaluation-harness)
- [Lección 24. El conjunto de regresión](0024-the-regression-suite.md)

---

¿No termina de quedar claro? Vuelve a leer la fuente primaria de arriba, ya que esta lección la comprime y en la compresión es donde se escapa la comprensión. Consulta el [glosario](../GLOSSARY.md) por si algún término te resultó resbaladizo.

Si lo poco claro es la propia lección y no el material, eso es un defecto: [abre un issue](https://github.com/TokenCemetery/teach/issues).
