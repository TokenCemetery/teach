---
title: "22. El preentrenamiento suele ser la opción por defecto equivocada"
description: "Una segunda fase de preentrenamiento sobre un modelo existente logra la mayor parte del beneficio sin volver a pagar el costo completo"
type: lesson
---

# Lección 22. El preentrenamiento suele ser la opción por defecto equivocada

**Vínculo con la misión:** "Puedes decidir si una tarea dada requiere preentrenamiento, preentrenamiento continuado o fine-tuning de un base model existente, y defender la elección en términos de costo" es el punto de Cómo se ve el éxito que cierra la etapa 10. Esta lección argumenta contra la opción por defecto a la que recurren la mayoría de los recién llegados; la Lección 23 cubre defender un presupuesto una vez que el preentrenamiento sí es de verdad la decisión correcta, y la Lección 24 cubre revisar el de otra persona.
**Fuente principal:** [Paper: "Don't Stop Pretraining: Adapt Language Models to Domains and Tasks", Gururangan et al., 2020](https://arxiv.org/abs/2004.10964)
**Requisitos previos:** [Lección 21](0021-periodic-held-out-evaluation.md)

## Calentamiento

1. ▢ ¿Por qué filtraron Rae et al. de forma explícita ciertos benchmarks del conjunto de entrenamiento de Gopher antes de usarlos como comprobaciones de evaluación periódica?

<details markdown="1"><summary>Comprobación</summary>

Para que una buena puntuación en esos benchmarks no pudiera explicarse porque el modelo hubiera visto y memorizado simplemente ese texto exacto durante el entrenamiento; un benchmark con el que se entrenó el modelo no puede distinguir la capacidad genuina de la memorización.

</details>

2. ▢ ¿Qué compra realmente a un equipo evaluar periódicamente durante el entrenamiento, y no solo una vez al final?

<details markdown="1"><summary>Comprobación</summary>

Permite detectar y, con suerte, abordar un error, una regresión o una divergencia de capacidad mientras la ejecución sigue en curso, en lugar de descubrirlo solo cuando el presupuesto de cómputo completo ya está gastado.

</details>

## Qué debes saber

### Por qué "necesitamos nuestro propio modelo preentrenado" suele ser el instinto equivocado

Cada etapa de este track ha ido construyendo hacia un hecho honesto: preentrenar un modelo desde cero es extraordinariamente caro. La sola aritmética óptima en cómputo de la etapa 3, un modelo de 70 mil millones de parámetros que querría del orden de un billón de tokens, da una idea de la escala del cómputo que exige una sola ejecución desde cero, antes de contar el costo de ingeniería de la infraestructura de entrenamiento distribuido que cubrieron las etapas 4 a 6, o el costo operativo de la monitorización y la tolerancia a fallas que cubrieron las etapas 8 y 9. Querer un modelo que sea bueno en un dominio concreto, una tarea concreta o un estilo concreto no justifica, por sí solo, volver a pagar todo ese costo. La pregunta que vale la pena hacerse primero no es "cómo preentrenamos un modelo para esto", sino "esto necesita realmente un modelo preentrenado nuevo siquiera".

### La evidencia de una alternativa más barata

Gururangan et al. responden a esto directamente para un caso común: adaptar un modelo preentrenado existente de cobertura amplia a un dominio concreto, en lugar de preentrenar uno nuevo para ese dominio. Toman RoBERTa, un modelo preentrenado grande existente, y siguen preentrenándolo con texto sin etiquetar de un dominio objetivo, una **segunda fase de preentrenamiento** a la que llaman **preentrenamiento adaptativo al dominio (DAPT)**, antes de evaluar en tareas de ese dominio. En cuatro dominios (papers biomédicos, papers de informática, noticias y reseñas) y ocho tareas de clasificación, encuentran que esto mejora de forma consistente el rendimiento en las tareas del dominio objetivo, tanto con muchos como con pocos recursos, siempre que el dominio objetivo no estuviera ya bien representado en el preentrenamiento original del modelo. Encuentran además que adaptarse todavía más a los datos sin etiquetar de la propia tarea, el **preentrenamiento adaptativo a la tarea (TAPT)**, mejora de nuevo el rendimiento por encima del DAPT, y que incluso una alternativa más barata, adaptarse a un corpus de tarea construido con heurísticas simples de selección de datos, funciona bien cuando el preentrenamiento adaptativo al dominio completo no es asequible.

### A favor de qué aboga esto, y a favor de qué no

Nada de esto afirma que preentrenar desde cero nunca esté justificado; afirma que la suposición por defecto debería ir en el otro sentido. Continuar el preentrenamiento sobre un modelo existente y ya ampliamente capaz, con una pequeña fracción del cómputo que necesitaría una ejecución desde cero, captura de forma consistente una parte real del beneficio que podría haber ofrecido un modelo totalmente específico del dominio. Una tarea que parece pedir "un modelo bueno en nuestro dominio" está, según esta evidencia, muy a menudo mejor servida por un preentrenamiento continuado sobre un base model existente, o, si la tarea es todavía más estrecha, por el fine-tuning con adapters que cubre `llm/finetuning`, que por pagar una nueva ejecución de preentrenamiento. Recurrir al preentrenamiento completo antes de descartar estas opciones más baratas es el error concreto contra el que argumenta esta lección, la versión a escala de preentrenamiento de la misma disciplina que aplica un nivel más abajo la propia lección de criterio de `llm/finetuning`, cuando el fine-tuning con adapters tampoco es la decisión correcta.

### Cuándo preentrenar desde cero sigue siendo la decisión correcta

Los casos en que de verdad lo es incluyen: un idioma o dominio objetivo tan alejado de los datos de entrenamiento y del tokenizer de cualquier base model disponible que ninguna cantidad de preentrenamiento continuado o de fine-tuning puede cerrar la brecha; un requisito de licencia o de procedencia que descarta los datos de entrenamiento de todos los base models disponibles; o un cambio deliberado de arquitectura (las elecciones de paralelismo de la etapa 6, un mecanismo de atención fundamentalmente distinto) en el que no se puede convertir a posteriori un checkpoint existente. Estas son la excepción que esta lección espera que quien lee sea capaz de nombrar, no la regla.

## Práctica

1. ▢ Un equipo quiere un modelo que rinda bien con documentos jurídicos, y hay disponible un base model existente de cobertura amplia. Según la evidencia de Gururangan et al., ¿qué recomendaría probar esta lección antes de preentrenar un modelo nuevo desde cero?

<details markdown="1"><summary>Comprobación</summary>

Preentrenamiento adaptativo al dominio: seguir preentrenando el base model existente con texto jurídico sin etiquetar, que según encontraron Gururangan et al. mejora de forma consistente el rendimiento en el dominio objetivo tanto con muchos como con pocos recursos, a una fracción del costo de una nueva ejecución de preentrenamiento desde cero.

</details>

2. ▢ ¿Cuál de estas es una razón legítima para preentrenar desde cero de todos modos, según esta lección?

    - a) El dominio objetivo es ligeramente distinto del texto general de la web
    - b) Ningún tokenizer ni datos de entrenamiento de un base model disponible cubren en absoluto el idioma o dominio objetivo, y el preentrenamiento continuado no puede cerrar esa brecha
    - c) Una nueva ejecución de preentrenamiento quedaría más impresionante en un informe
    - d) Configurar un fine-tuning llevaría más de un día

<details markdown="1"><summary>Comprobación</summary>

**b)** es la excepción genuina que nombra esta lección. (a) es exactamente el caso que, según la evidencia de Gururangan et al., el preentrenamiento continuado maneja bien, no una razón para preentrenar desde cero. (c) y (d) no son razones defendibles bajo el argumento de costo de esta lección.

</details>

3. ▢ ¿Cuál es la diferencia entre el preentrenamiento adaptativo al dominio (DAPT) y el preentrenamiento adaptativo a la tarea (TAPT), según Gururangan et al.?

<details markdown="1"><summary>Comprobación</summary>

El DAPT continúa el preentrenamiento con texto sin etiquetar de un dominio objetivo amplio (como todos los papers biomédicos). El TAPT continúa el preentrenamiento específicamente con los propios datos sin etiquetar de una tarea dada, un corpus más estrecho, y Gururangan et al. encontraron que mejora el rendimiento incluso después de haber aplicado ya el DAPT.

</details>

4. ▢ Un equipo no puede permitirse una ejecución completa de preentrenamiento adaptativo al dominio pero aun así quiere parte de su beneficio. ¿Qué alternativa sugiere el trabajo de Gururangan et al.?

<details markdown="1"><summary>Comprobación</summary>

Adaptarse a un corpus de tarea construido con estrategias simples de selección de datos, que Gururangan et al. encontraron que era una alternativa eficaz y más barata cuando no se dispone de recursos para el preentrenamiento adaptativo al dominio completo.

</details>

## Prácticas en el mundo real

- [ ] Busca un ejemplo publicado de un modelo adaptado a un dominio (una ficha de modelo o un paper de un "BioBERT", "SciBERT", "FinBERT" o similar) e identifica si se construyó mediante preentrenamiento continuado sobre un base model existente o se preentrenó por completo desde cero.
- [ ] Lee la introducción de Gururangan et al. (enlazada arriba) y escribe una oración sobre por qué eligieron específicamente probar el preentrenamiento adaptativo al dominio con varios dominios, y no solo con uno, antes de sacar una conclusión general.
- [ ] Mañana: para un dominio o una tarea objetivo hipotéticos que elijas, escribe un párrafo que argumente a favor o en contra de preentrenar un modelo nuevo desde cero, citando al menos una evidencia de esta lección o de una etapa anterior de este track.

## Para profundizar

- [Paper: "Don't Stop Pretraining: Adapt Language Models to Domains and Tasks", Gururangan et al., 2020](https://arxiv.org/abs/2004.10964)
- [`llm/finetuning`](../../finetuning/): la misma disciplina aplicada un nivel más abajo, cuando el preentrenamiento continuado sigue siendo más de lo que necesita una tarea más estrecha
- [Recursos](../RESOURCES.md)

---

¿No termina de quedar claro? Vuelve a leer la fuente primaria de arriba, ya que esta lección la comprime y en la compresión es donde se escapa la comprensión. Consulta el [glosario](../GLOSSARY.md) por si algún término te resultó resbaladizo.

Si lo poco claro es la propia lección y no el material, eso es un defecto: [abre un issue](https://github.com/TokenCemetery/teach/issues).
