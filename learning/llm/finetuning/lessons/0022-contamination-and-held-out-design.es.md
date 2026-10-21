---
title: "22. Contaminación y diseño held-out"
description: "Dividir por la clave correcta y dimensionar para la pregunta"
type: lesson
---

# Lección 22. Contaminación y diseño held-out

**Vínculo con la misión:** Un conjunto held-out en el que no puedes confiar es peor que ninguno, porque produce decisiones equivocadas con total seguridad.
**Fuente principal:** [Code: lm-evaluation-harness, EleutherAI](https://github.com/EleutherAI/lm-evaluation-harness)
**Requisitos previos:** [Lección 21](0021-building-the-dataset.md)

## Calentamiento

1. ▢ ¿Por qué deduplicar antes de dividir?

<details markdown="1"><summary>Comprobación</summary>

Una pareja de duplicados a caballo de la partición mete un ejemplo de entrenamiento en el conjunto held-out, así que el rendimiento held-out mide memorización.

</details>

2. ▢ ¿Qué enseña mal el fine-tuning?

<details markdown="1"><summary>Comprobación</summary>

Hechos nuevos, razonamiento que no estuviera ya, información actual y cálculo preciso. Enseña bien formato, tono y consistencia.

</details>

3. ▢ ¿Qué checkpoint despliegas?

<details markdown="1"><summary>Comprobación</summary>

El del mínimo held-out, lo que presupone un conjunto held-out en el que puedas confiar.

</details>

## Qué debes saber

### Dos tipos de contaminación

**Tu contaminación.** Ejemplos de prueba que también aparecen, de forma exacta o casi, en tu conjunto de entrenamiento. Enteramente bajo tu control, y enteramente culpa tuya cuando ocurre.

**Contaminación heredada.** Ejemplos de prueba que aparecieron en el corpus de *preentrenamiento* del base model. No está bajo tu control, es en gran medida indetectable desde fuera y es la razón por la que las puntuaciones de los benchmarks públicos deben leerse con sospecha. Si un benchmark es anterior al base model y vive en la web pública, asume cierta exposición.

La consecuencia práctica: **un benchmark público es una señal débil para tu decisión.** Puede medir el recuerdo de algo que el base ya vio. Tus propios datos held-out, construidos de cero, son la señal fuerte, y son lo único en lo que de verdad puedes confiar.

### Dividir bien

La división aleatoria es el valor por defecto y con frecuencia es errónea. Aquello *por lo que* divides determina qué generalización estás midiendo.

| Dividir por | Mide | Úsalo cuando |
|---|---|---|
| Ejemplo aleatorio | Generalización a ejemplos nuevos | Los ejemplos son genuinamente independientes |
| Grupo o entidad | Generalización a entidades nuevas | Varios ejemplos comparten un cliente, documento, autor |
| Tiempo | Generalización al futuro | Los datos tienen alguna estructura temporal en absoluto |

La **fuga por grupo** es el fallo silencioso clásico. Diez ejemplos derivados de un mismo documento fuente, divididos al azar, ponen unos en train y otros en test. El modelo ha visto el contenido de ese documento y su puntuación held-out lo refleja. Divide por documento.

![Seis ejemplos, cuatro del documento A y dos del B, divididos de dos maneras. Divididos al azar, los ejemplos de A caen tanto en el recipiente de entrenamiento como en el de prueba; divididos por documento, todo A está en un recipiente y todo B en el otro.](images/on-both-sides.svg)

Los mismos seis ejemplos están en ambos paneles; solo cambia la asignación. A la izquierda un documento está en ambos recipientes, que es la fuga, y ninguna disciplina held-out en otro lugar la deshace.

La **fuga temporal** es la otra. Entrenar con datos posteriores a tu periodo de prueba significa que el modelo ha visto el futuro, y tu puntuación es optimista de un modo que no puede sobrevivir al despliegue. Cualquier dataset con una dimensión temporal debería dividirse por tiempo, y esta es la división que la gente más a menudo se salta porque lo aleatorio es más fácil.

### Tres particiones, no dos

- **Train.** Aquello a lo que se ajusta el modelo.
- **Validación.** Lo que usas para elegir checkpoints, rank, learning rate y todo lo demás.
- **Test.** Se toca una vez, al final, para estimar el rendimiento real.

La razón de tres es que seleccionar contra un conjunto se ajusta a él. Elige tu checkpoint por validación, compara veinte configuraciones en validación, escoge la mejor, y la puntuación de validación es ahora optimista en una cantidad proporcional a cuántas decisiones tomaste contra ella. Por eso existe el conjunto de test y por eso se usa una sola vez.

**En la práctica la gente usa dos, y luego se pregunta por qué el despliegue rinde menos que su evaluación.** La brecha es exactamente la cantidad de selección que hicieron.

### Detectar tu propia contaminación

Deduplica contra el conjunto de test de forma explícita, no solo dentro del conjunto de entrenamiento:

1. Normaliza: minúsculas, colapsa espacios en blanco, quita puntuación.
2. Hash de coincidencia exacta entre train y test. Elimina de train cualquier colisión.
3. Detección de casi duplicados con MinHash o similitud de embeddings, con un umbral que hayas mirado a mano.
4. **Lee tú mismo las parejas de mayor similitud.** Los umbrales son conjeturas; tus ojos son la calibración.

El paso 4 es el que la gente se salta y es el que encuentra los problemas reales.

### Dimensionar el conjunto held-out

Los conjuntos held-out suelen ser demasiado pequeños para sostener las conclusiones que se sacan de ellos. La forma aproximada: distinguir diferencias pequeñas requiere muchos ejemplos, y el número crece de forma cuadrática a medida que se reduce la diferencia que te importa.

| Diferencia que quieres detectar | Escala aproximada necesaria |
|---|---|
| 10 puntos porcentuales | Unos pocos cientos |
| 5 puntos porcentuales | Varios cientos a mil |
| 1 a 2 puntos porcentuales | Miles |

Así que un conjunto held-out de 50 ejemplos puede decirte si el modelo funciona siquiera. No puede decirte si el rank 32 superó al rank 16 por dos puntos, y tratarlo como si pudiera es un error muy común.

El corolario: si tienes 200 ejemplos held-out, no ejecutes un barrido de doce configuraciones. El ganador del barrido es sobre todo ruido, y has gastado cómputo para seleccionar una configuración al azar.

### Comparación pareada

Al comparar dos modelos, evalúa ambos sobre **los mismos ejemplos** y compara por ejemplo. La comparación pareada elimina la varianza debida a la dificultad de los ejemplos y detecta diferencias menores con menos ejemplos que comparar dos promedios independientes. No cuesta más que contabilidad.

Conserva los resultados por ejemplo, no solo el agregado. "El modelo B es 3 puntos mejor" es mucho menos útil que "B arregló 14 ejemplos que A erró y rompió 6 que A acertó", y en esos seis es donde aprendes algo.

## Práctica

1. ▢ Distingue tu contaminación de la contaminación heredada, y di qué implica cada una.

<details markdown="1"><summary>Comprobación</summary>

La tuya: ejemplos de prueba que también están en tu conjunto de entrenamiento. Prevenible, detectable, responsabilidad tuya.

La heredada: ejemplos de prueba en el corpus de preentrenamiento del base model. No controlable, en gran medida indetectable, y la razón por la que las puntuaciones de los benchmarks públicos son una evidencia débil para tu decisión.

La implicación es confiar en datos held-out privados construidos de cero antes que en cualquier benchmark público.

</details>

2. ▢ Tu dataset tiene 500 ejemplos derivados de 50 documentos fuente. Divides al azar y obtienes un 96% de precisión held-out. ¿Qué falla?

<details markdown="1"><summary>Comprobación</summary>

Fuga por grupo. Los ejemplos del mismo documento están en ambas particiones, así que el modelo ha visto el contenido de ese documento y la puntuación refleja recuerdo.

Divide por documento: todos los ejemplos de un documento van a un solo lado. Espera que el número honesto sea sustancialmente menor.

</details>

3. ▢ ¿Por qué tres particiones y no dos?

<details markdown="1"><summary>Comprobación</summary>

Porque seleccionar contra un conjunto se ajusta a él. Cada elección de checkpoint y cada comparación de configuraciones hecha en validación vuelve optimista la puntuación de validación.

El conjunto de test queda intacto hasta el final, así que da una estimación sin sesgo. Con solo dos particiones, tu número reportado incluye toda tu selección, que es precisamente la brecha que la gente ve entre la evaluación y el despliegue.

</details>

4. ▢ Tienes 80 ejemplos held-out y quieres saber si el rank 64 supera al rank 16. ¿Puedes?

<details markdown="1"><summary>Comprobación</summary>

No, a menos que la diferencia sea muy grande. Ochenta ejemplos pueden sostener la detección de una oscilación de diez puntos o más; la diferencia entre dos ranks razonables suele ser de unos pocos puntos como mucho.

O consigues más datos held-out o aceptas que esta pregunta no tiene respuesta con lo que tienes. Responderla de todos modos produce una decisión equivocada con total seguridad.

</details>

5. ▢ ¿Qué división se omite con más frecuencia, y qué cuesta omitirla?

    - a) Dividir los datos por tiempo cuando tienen orden temporal
    - b) Dividir los datos al azar entre todos los ejemplos disponibles
    - c) Dividir los datos por longitud de salida en recipientes equilibrados
    - d) Dividir los datos según qué anotador produjo la etiqueta

<details markdown="1"><summary>Comprobación</summary>

**a)** Dividir los datos por tiempo cuando tienen orden temporal.

Lo aleatorio es más fácil y es el valor por defecto, así que la estructura temporal se ignora. El costo es entrenar con datos posteriores al periodo de prueba: el modelo ha visto el futuro, y la puntuación no puede sobrevivir al despliegue.

</details>

6. ▢ ¿Por qué la comparación pareada es mejor que comparar dos promedios?

<details markdown="1"><summary>Comprobación</summary>

Elimina la varianza debida a la dificultad de los ejemplos al comparar los dos modelos sobre los mismos elementos, así que detecta diferencias menores con menos ejemplos.

También produce el artefacto más útil: qué ejemplos concretos mejoraron y cuáles retrocedieron. En las regresiones es donde está el aprendizaje.

</details>

## Prácticas en el mundo real

- [ ] Revisa tu dataset en busca de una estructura de agrupación: documento, cliente, autor, sesión. Si existe una, vuelve a dividir por ella y compara los dos números held-out.
- [ ] Ejecuta la detección de casi duplicados entre train y test. Lee a mano las veinte parejas de mayor similitud.
- [ ] Divide en tres conjuntos y anota la regla de para qué puede usarse cada uno. Luego cúmplela.
- [ ] Mañana: calcula cuántos ejemplos held-out necesitarías para detectar la diferencia que de verdad te importa. Compara con cuántos tienes.

## Para profundizar

- [Code: lm-evaluation-harness, EleutherAI](https://github.com/EleutherAI/lm-evaluation-harness)
- [Docs: Splitting datasets, Hugging Face Datasets](https://huggingface.co/docs/datasets/main/en/process)
- [Lección 23. Métricas que significan algo](0023-metrics-that-mean-something.md)

---

¿No termina de quedar claro? Vuelve a leer la fuente primaria de arriba, ya que esta lección la comprime y en la compresión es donde se escapa la comprensión. Consulta el [glosario](../GLOSSARY.md) por si algún término te resultó resbaladizo.

Si lo poco claro es la propia lección y no el material, eso es un defecto: [abre un issue](https://github.com/TokenCemetery/teach/issues).
