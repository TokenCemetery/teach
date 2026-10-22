---
title: "21. Evaluación periódica con datos held-out"
description: "La loss de entrenamiento dice que el modelo se ajusta a sus propios datos de entrenamiento; solo una comprobación held-out dice algo sobre el resto"
type: lesson
---

# Lección 21. Evaluación periódica con datos held-out

**Vínculo con la misión:** "Puedes leer un dashboard de entrenamiento y decir si la ejecución va bien encaminada" es la celda "Terminada cuando" de esta etapa en El arco. La Lección 20 cubrió vigilar las señales internas de la propia ejecución de entrenamiento; esta lección cubre comprobar los checkpoints guardados frente a algo que la loss de entrenamiento no puede decirte, y entrega esa medición a donde se enseña por completo.
**Fuente principal:** [Paper: "Scaling Language Models: Methods, Analysis & Insights from Training Gopher", Rae et al., 2021](https://arxiv.org/abs/2112.11446)
**Requisitos previos:** [Lección 20](0020-reading-a-loss-curve.md), [Datos held-out](../../evals/GLOSSARY.md)

## Calentamiento

1. ▢ ¿Por qué un loss scalar que se desploma hacia cero, o una norma de activaciones que se dispara, podrían avisar antes de la inestabilidad que la propia curva de loss de entrenamiento?

<details markdown="1"><summary>Comprobación</summary>

Son síntomas del problema numérico de fondo en desarrollo, que pueden aparecer antes de que crezca lo bastante como para perturbar visiblemente la curva de loss; cuando un spike es claramente visible en la propia loss, el problema puede llevar ya algún tiempo gestándose.

</details>

2. ▢ ¿Por qué un dashboard que sigue la loss, la norma del gradiente y una señal de estabilidad solo es útil en la práctica si se monitoriza con frecuencia?

<details markdown="1"><summary>Comprobación</summary>

Porque las fallas y las inestabilidades son sucesos frecuentes y rutinarios a escala (etapa 8), así que un problema detectado tarde cuesta mucho más progreso perdido que el mismo problema detectado pronto.

</details>

## Qué debes saber

### Lo que la loss de entrenamiento no puede decirte

La loss de entrenamiento mide qué tan bien se ajusta un modelo a los batches concretos con los que se está entrenando en ese momento. Una loss de entrenamiento que baja de forma suave es necesaria para una ejecución sana, pero no es lo mismo que el modelo sea bueno en algo que una persona fuera del bucle de entrenamiento le vaya a pedir realmente, y no dice nada en absoluto sobre si esa mejora se sostendría con texto con el que el modelo nunca se ha entrenado. Una curva de loss de entrenamiento de aspecto perfectamente sano puede seguir apoyada sobre un modelo que se está sobreajustando en silencio a rarezas propias de su mezcla de entrenamiento.

### Cómo fue la propia evaluación periódica de Gopher

Rae et al. no esperaron a que terminara el entrenamiento para comprobar esto. Informan de curvas de evaluación calculadas periódicamente durante el entrenamiento, en cuatro benchmarks de modelado de lenguaje (Wikitext103, LAMBADA, Curation Corpus y C4) que filtraron de forma explícita del conjunto de entrenamiento de antemano, precisamente para que una buena puntuación en ellos no pudiera explicarse porque el modelo hubiera visto simplemente ese texto exacto durante el entrenamiento. Comprobar periódicamente un benchmark así, y no solo una vez al final del todo, es lo que de verdad permite a un equipo detectar un problema, un error en el pipeline de datos, una regresión por un cambio de configuración, una divergencia inesperada de capacidad, mientras la ejecución sigue en curso y todavía se puede hacer algo al respecto, en lugar de descubrirlo solo después de haber gastado ya todo el presupuesto de cómputo.

### Por qué "filtrado del conjunto de entrenamiento" hace un trabajo real

La expresión que usan Rae et al., benchmarks "filtrados de forma explícita del conjunto de entrenamiento", es la misma idea en torno a la cual se construyó la Lección 1 del material de pipeline de datos de este track, aplicada a la evaluación en lugar de al entrenamiento: una puntuación solo significa algo sobre la generalización si el modelo no pudo haber acertado por haber memorizado el texto exacto que se está probando. Esto es precisamente lo que significa **datos held-out**, y es un tema lo bastante grande, con sus propias vías de contaminación, métodos de detección y técnicas de diseño, como para que haya un track entero construido en torno a él.

### Dónde se entrega el relevo

`llm/evals` es dueño de la metodología de evaluación por completo: cómo construir un conjunto held-out que resista la contaminación, qué hace fiable a una métrica y cómo convertir un número en una decisión defendible. La única reclamación de este track sobre ese material es la que se hace en esta lección: una ejecución de preentrenamiento necesita comprobaciones periódicas con datos held-out, sobre checkpoints guardados, y no solo al final. Para todo lo que va más allá, la hoja [Datos held-out y contaminación](../../evals/reference/held-out-data-and-contamination.md) de `llm/evals` es la que hay que leer a continuación, y no una repetición de ella aquí.

## Práctica

1. ▢ La loss de entrenamiento de un modelo ha bajado de forma suave durante toda la ejecución. ¿Te dice esto, por sí solo, si el modelo rinde bien en tareas a cuyo ajuste no se entrenó directamente?

<details markdown="1"><summary>Comprobación</summary>

No. La loss de entrenamiento mide el ajuste a los propios batches de entrenamiento del modelo; una loss de entrenamiento que baja de forma suave es necesaria para una ejecución sana, pero por sí sola no dice nada sobre el rendimiento con datos o tareas con los que el modelo no se ha entrenado, que es para lo que sirve una evaluación held-out.

</details>

2. ▢ ¿Por qué filtraron Rae et al. de forma explícita Wikitext103, LAMBADA, Curation Corpus y C4 del conjunto de entrenamiento de Gopher antes de usarlos como benchmarks de evaluación periódica?

<details markdown="1"><summary>Comprobación</summary>

Para que una buena puntuación en esos benchmarks no pudiera explicarse porque el modelo hubiera visto y memorizado simplemente ese texto exacto durante el entrenamiento. Un benchmark con el que se entrenó el modelo no puede distinguir la capacidad genuina de la memorización, que es lo que hace de un benchmark held-out una evidencia significativa de una manera en que no lo es uno contaminado.

</details>

3. ▢ ¿Qué compra realmente a un equipo evaluar periódicamente durante el entrenamiento, y no solo una vez al final, dado lo cara que es una ejecución de entrenamiento completa?

    - a) No tiene ninguna ventaja frente a una única evaluación al final; lo que importa es el resultado final
    - b) Permite detectar y, con suerte, abordar un error, una regresión o una divergencia de capacidad mientras la ejecución sigue en curso, en lugar de descubrirlo solo cuando el presupuesto de cómputo completo ya está gastado
    - c) Sustituye por completo la necesidad de datos held-out
    - d) Solo importa para ejecuciones de entrenamiento muy cortas

<details markdown="1"><summary>Comprobación</summary>

**b)** es el beneficio práctico directo: detectar un problema pronto, mientras aún queda presupuesto de cómputo para responder a él, en lugar de enterarse solo una vez completada la ejecución. (a) lo ignora por completo. (c) invierte la relación; la evaluación periódica sigue necesitando ser held-out para significar algo. (d) es al revés, ya que una ejecución más larga y más cara tiene más que perder con un problema detectado tarde.

</details>

## Prácticas en el mundo real

- [ ] Busca cómo programa la evaluación periódica durante el entrenamiento un framework de entrenamiento o una configuración de seguimiento de experimentos a la que tengas acceso (es habitual un intervalo de evaluación medido en pasos o en tokens), y anota qué benchmarks o métricas evalúa por defecto.
- [ ] Lee la hoja de referencia [Datos held-out y contaminación](../../evals/reference/held-out-data-and-contamination.md) de `llm/evals` e identifica cuál de sus dos vías de contaminación (absorción durante el preentrenamiento, o sobreajuste iterativo) es contra la que protege la expresión "filtrados de forma explícita del conjunto de entrenamiento" de Gopher.
- [ ] Mañana: para una ejecución de preentrenamiento hipotética a tu elección, decide un intervalo de evaluación (cada cuánto, en tokens o pasos, comprobarías el rendimiento held-out) y nombra un benchmark o conjunto held-out con el que lo comprobarías, y por qué.

## Para profundizar

- [Paper: "Scaling Language Models: Methods, Analysis & Insights from Training Gopher", Rae et al., 2021](https://arxiv.org/abs/2112.11446)
- `llm/evals`: [Datos held-out y contaminación](../../evals/reference/held-out-data-and-contamination.md)
- [Recursos](../RESOURCES.md)

---

La etapa 9 cubrió vigilar una ejecución mientras ocurre, tanto sus propias entrañas como sus checkpoints frente a algo externo. La etapa 10 cierra el arco: decidir si ejecutar una de estas siquiera, y defender esa decisión ante otra persona.

¿No termina de quedar claro? Vuelve a leer la fuente primaria de arriba, ya que esta lección la comprime y en la compresión es donde se escapa la comprensión. Consulta el [glosario](../GLOSSARY.md) por si algún término te resultó resbaladizo.

Si lo poco claro es la propia lección y no el material, eso es un defecto: [abre un issue](https://github.com/TokenCemetery/teach/issues).
