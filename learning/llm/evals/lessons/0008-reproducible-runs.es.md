---
title: "8. Ejecuciones reproducibles"
description: "Por qué la misma eval puede producir números distintos en ejecuciones distintas, y qué tiene que registrar un resultado fiable junto con la puntuación"
type: lesson
---

# Lección 8. Ejecuciones reproducibles

**Vínculo con la misión:** Esta es la lección que cierra la etapa 4: un harness (lección 7) es solo la mitad del trabajo. Un número que produce solo es fiable una vez que se entiende su varianza entre ejecuciones y se registra qué lo produjo, que es lo que permite que una comparación posterior signifique algo.
**Fuente principal:** [Repo: lm-evaluation-harness, EleutherAI](https://github.com/EleutherAI/lm-evaluation-harness)
**Requisitos previos:** [Lección 7](0007-eval-frameworks-and-harness.md), [Contaminación de datos](../GLOSSARY.md)

## Calentamiento

1. ▢ Nombra las cuatro etapas que tiene todo harness de eval.

<details markdown="1"><summary>Comprobación</summary>

Cargar el conjunto de eval held-out, generar las salidas del modelo, calificarlas con la métrica o el juez elegidos y agregar las puntuaciones por ejemplo en un único número resumen.

</details>

2. ▢ ¿Cuándo debería un equipo recurrir a openai/evals en lugar de a lm-evaluation-harness?

<details markdown="1"><summary>Comprobación</summary>

Al evaluar una capacidad específica de la misión que ningún benchmark estandarizado existente cubre, ya que openai/evals está pensado para definir una eval propia como código, mientras que lm-evaluation-harness está pensado para ejecutar configuraciones de benchmarks ya existentes.

</details>

## Qué debes saber

### Por qué la misma eval puede dar dos números distintos

Un modelo muestreado con una temperatura distinta de cero produce completaciones diferentes en ejecuciones diferentes, incluso contra el prompt idéntico, lo que significa puntuaciones por ejemplo distintas y un número agregado distinto cada vez que se ejecuta la eval, sin que haya ocurrido nada malo. Si la calificación además usa un juez LLM (etapa 3), eso añade una segunda capa de ruido de muestreo encima de la varianza propia del modelo bajo prueba. Nada de esto es un error del harness; es el harness reportando fielmente un proceso estocástico, y significa que el número de una sola ejecución es una muestra de una distribución, no un hecho fijo sobre el modelo.

### El compromiso del determinismo

Fijar la temperatura en 0 (decodificación voraz) elimina la aleatoriedad del lado de la generación y hace las ejecuciones mucho más repetibles, lo que resulta atractivo para una eval cuya calificación depende de una reproducibilidad exacta, como la coincidencia exacta. El costo: la decodificación voraz puede no reflejar cómo se comporta realmente el modelo en el despliegue, si el sistema desplegado muestrea con una temperatura distinta de cero. Una eval ejecutada por completo en modo voraz puede estar midiendo un modo que el sistema real rara vez usa. Donde el comportamiento desplegado realmente muestrea, el enfoque más honesto es ejecutar varias muestras por ejemplo con la temperatura del despliegue (la misma idea que usó el pass@k de la lección 4 para el código) y reportar la dispersión entre ellas, no solo el valor puntual de una única ejecución.

### Una semilla ayuda, pero no garantiza resultados idénticos

Fijar una semilla aleatoria para la generación reduce la varianza entre ejecuciones con la misma configuración, pero no garantiza resultados idénticos bit a bit entre hardware distinto, versiones de biblioteca distintas o composiciones de lote distintas, ya que el cálculo en coma flotante no es perfectamente asociativo en todos esos casos. Una semilla es un control real y útil, no uno absoluto; tratar "fijamos una semilla" como prueba de que dos ejecuciones son directamente comparables es exagerar lo que una semilla puede prometer.

### Qué hace defendible más tarde un número reportado

Un número solo, sin nada sobre cómo se produjo, no puede compararse con honestidad con un número posterior, de una nueva ejecución, de un checkpoint distinto o de un ciclo de eval distinto: cualquier diferencia entre ellos podría ser un cambio real o simple varianza del pipeline, y nada en una puntuación a secas puede decir cuál. Un resultado defendible registra, junto con la puntuación, lo que realmente lo produjo: la semilla aleatoria usada, la temperatura de generación, las versiones del modelo y del framework, la versión del conjunto de eval y, cuando se ejecutaron varias muestras, la dispersión entre ellas, no solo su media. Es lo que una comparación posterior, o la decisión de go/no-go hacia la que construye la etapa 5, realmente necesita para ser honesta sobre si una diferencia observada refleja al modelo o al ruido.

## Práctica

1. ▢ Un equipo ejecuta la misma eval contra el mismo modelo dos veces, con temperatura 0.7, y obtiene dos puntuaciones agregadas distintas. ¿Es esto evidencia de que el harness está roto? ¿Por qué sí o por qué no?

<details markdown="1"><summary>Comprobación</summary>

No. Una temperatura distinta de cero vuelve estocástica la generación, así que son de esperar completaciones distintas, y por tanto puntuaciones por ejemplo distintas, entre ejecuciones sin que nada esté mal. El harness reporta fielmente un proceso estocástico; el número de una sola ejecución es una muestra, no un hecho fijo.

</details>

2. ▢ ¿Qué compra fijar la temperatura en 0 para una eval, y qué cuesta, si el sistema desplegado realmente muestrea con temperatura 0.7?

<details markdown="1"><summary>Comprobación</summary>

Compra repetibilidad: la decodificación voraz elimina la aleatoriedad del lado de la generación, así que las ejecuciones se vuelven mucho más consistentes. Cuesta realismo: la eval mide un modo de decodificación (voraz) que el sistema real rara vez usa, así que el resultado puede no reflejar cómo se comporta realmente el modelo desplegado con 0.7.

</details>

3. ▢ ¿Por qué fijar una semilla aleatoria no garantiza que dos ejecuciones de una eval produzcan resultados idénticos?

<details markdown="1"><summary>Pista</summary>

Piensa en qué más podría diferir entre dos ejecuciones además de la semilla.

</details>

<details markdown="1"><summary>Comprobación</summary>

Una semilla controla la aleatoriedad dentro de una configuración dada, pero el cálculo en coma flotante no es perfectamente asociativo entre hardware distinto, versiones de biblioteca distintas o composiciones de lote distintas, así que esas diferencias aún pueden producir resultados distintos con la misma semilla. Una semilla es un control real, no una garantía absoluta de salida idéntica bit a bit.

</details>

4. ▢ El equipo A reporta una puntuación de eval de 72.3 para un modelo. Un mes después, el equipo B vuelve a ejecutar "la misma eval" sobre el mismo modelo y obtiene 69.8, sin ninguna información de semilla, temperatura o versión registrada de la ejecución original del equipo A. ¿Qué se puede concluir con honestidad de la brecha de 2.5 puntos?

<details markdown="1"><summary>Comprobación</summary>

Muy poco, por sí sola. Sin conocer la temperatura, la semilla, las versiones del modelo y del framework y la versión del conjunto de eval que usó el equipo A, no hay manera de saber si la brecha refleja un cambio real (un checkpoint distinto, una versión distinta del conjunto de eval) o la varianza ordinaria entre ejecuciones por el muestreo. La conclusión honesta es que la comparación aún no es significativa hasta que se conozcan y se igualen los detalles de producción de ambas ejecuciones, o se mida directamente la varianza entre ejecuciones repetidas.

</details>

5. ▢ ¿Qué afirmación es cierta sobre lo que hace defendible un número de eval reportado?

    - a) La puntuación de una sola ejecución basta por sí sola, siempre que el harness se haya ejecutado sin errores
    - b) La puntuación debe reportarse junto con lo que la produjo (semilla, temperatura, versiones, versión del conjunto de eval) y, cuando corresponda, su dispersión entre varias ejecuciones
    - c) Fijar una semilla aleatoria garantiza resultados idénticos en cualquier hardware o versión de biblioteca
    - d) Siempre debería usarse decodificación voraz en las evals, sin importar la temperatura de muestreo real del sistema desplegado

<details markdown="1"><summary>Comprobación</summary>

**b)** Registrar los detalles de producción y, donde hay muestreo, la dispersión entre ejecuciones, es lo que permite que una comparación posterior distinga un cambio real del ruido. (a) es falsa: un número aislado no puede compararse con nada posterior sin saber qué lo produjo. (c) es falsa: una semilla reduce pero no elimina la varianza entre hardware o versiones distintos. (d) es falsa: la decodificación voraz cede realismo cuando el sistema desplegado realmente muestrea, lo cual es un costo real, no una elección gratuita.

</details>

## Prácticas en el mundo real

- [ ] Para una eval que ejecutes, comprueba si su harness registra hoy la semilla, la temperatura y las versiones del modelo/framework junto con la puntuación, y añade lo que falte.
- [ ] Si tu eval muestrea con una temperatura distinta de cero, ejecútala varias veces (o con varias muestras por ejemplo) y registra la dispersión entre ejecuciones, no solo un número.
- [ ] Mañana: busca un resultado de eval pasado que tú o tu equipo hayan reportado y comprueba si se registró lo suficiente junto a él para saber si una futura nueva ejecución sería directamente comparable.

## Para profundizar

- [Repo: lm-evaluation-harness, EleutherAI](https://github.com/EleutherAI/lm-evaluation-harness)
- [Repo: openai/evals, OpenAI](https://github.com/openai/evals)
- [Recursos](../RESOURCES.md)

---

¿No termina de quedar claro? Vuelve a leer la fuente primaria de arriba, ya que esta lección la comprime y en la compresión es donde se escapa la comprensión. Consulta el [glosario](../GLOSSARY.md) por si algún término te resultó resbaladizo.

Si lo poco claro es la propia lección y no el material, eso es un defecto: [abre un issue](https://github.com/TokenCemetery/teach/issues).
