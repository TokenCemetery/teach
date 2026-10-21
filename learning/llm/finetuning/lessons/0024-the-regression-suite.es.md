---
title: "24. El conjunto de regresión"
description: "Detectar el daño que esconden todos los demás números"
type: lesson
---

# Lección 24. El conjunto de regresión

**Vínculo con la misión:** "Construir una eval que detecte una regresión antes de desplegar" es la redacción propia de la misión. Esta es esa lección.
**Fuente principal:** [Paper: "An Empirical Study of Catastrophic Forgetting in Large Language Models During Continual Fine-tuning", Luo et al., arXiv:2308.08747](https://arxiv.org/abs/2308.08747)
**Requisitos previos:** [Lección 23](0023-metrics-that-mean-something.md), [Lección 22](0022-contamination-and-held-out-design.md)

## Calentamiento

1. ▢ ¿Por qué la pérdida es una base equivocada para una decisión?

<details markdown="1"><summary>Comprobación</summary>

Puntúa el acuerdo con una continuación de referencia, penalizando alternativas correctas y premiando errores fluidos. Úsala para seleccionar checkpoints, no para decisiones.

</details>

2. ▢ ¿Dos sesgos documentados de los modelos juez, y sus mitigaciones?

<details markdown="1"><summary>Comprobación</summary>

Sesgo de posición: aleatoriza el orden y evalúa ambos órdenes. Sesgo de verbosidad: compara con longitudes igualadas o indica al juez que ignore la longitud.

</details>

3. ▢ ¿Por qué el conjunto held-out de tu tarea es ciego al olvido catastrófico?

<details markdown="1"><summary>Comprobación</summary>

Sale de la distribución de tu tarea, así que no puede observar la degradación en capacidades fuera de esa distribución.

</details>

## Qué debes saber

### El fallo que esto existe para detectar

El fine-tuning mueve los pesos hacia tu tarea. Las capacidades que no se reforzaron pueden degradarse, y eso es el **olvido catastrófico**. La literatura empírica encuentra que no es un caso límite raro en el fine-tuning continuo de modelos de lenguaje: las capacidades generales, incluido el seguimiento de instrucciones, decaen de forma medible, y el efecto puede crecer con la escala del modelo en lugar de reducirse.

La propiedad peligrosa es que **cada número que ya estás mirando va en la dirección correcta.** La pérdida de entrenamiento cae, tu métrica held-out de la tarea mejora, tus probes se ven bien, y el modelo ha empeorado en cosas que nunca mediste. Despliegas, y los reportes llegan desde una dirección que tu evaluación no podía ver.

Un conjunto held-out mide si aprendiste la tarea. Un conjunto de regresión mide si rompiste algo más. **Son instrumentos distintos y necesitas ambos.**

### Qué contiene

Cuatro categorías. Las cuatro, no una selección.

**1. Seguimiento general de instrucciones.** ¿Sigue pudiendo seguir una instrucción ordinaria sin relación con tu tarea? Resumir algo, responder una pregunta general, seguir una petición de varios pasos.

**2. Cumplimiento de formato y de comportamiento.** ¿Sigue respetando un system prompt? ¿Sigue produciendo JSON válido cuando se le pide? ¿Sigue deteniéndose cuando debe? Un modelo entrenado con un formato rígido a veces pierde la capacidad de producir cualquier otro.

**3. Comportamiento de seguridad y de rechazo.** Si el base model rechazaba ciertas peticiones, ¿el fine-tune las sigue rechazando? **El fine-tuning con datos benignos puede degradar la alineación de seguridad como efecto secundario.** Es un resultado documentado y reproducido repetidamente, no una hipótesis. Si heredaste el comportamiento de alineación de un modelo instruct, heredaste la responsabilidad de comprobar que sobrevivió.

**4. Capacidad adyacente.** Cosas cercanas a tu tarea que no entrenaste. ¿Fine-tuning con tickets de soporte en inglés? Comprueba otro idioma. ¿Fine-tuning con un tipo de documento? Comprueba otro.

### Construirlo

Pequeño, fijo y leído por una persona.

```text
regression/
├── instruction-following.jsonl   # 20 general instructions
├── format-compliance.jsonl       # 20 schema and system-prompt cases
├── safety.jsonl                  # 20 cases the base refused
├── adjacent.jsonl                # 20 near-task, untrained cases
└── baseline/                     # base model outputs, committed
```

Ochenta ejemplos en total. Es pequeño a propósito: suficiente para detectar una regresión real, lo bastante pequeño como para que una persona lea de verdad los diffs.

El paso crítico y con frecuencia omitido: **registra las salidas del base model antes de entrenar, y haz commit de ellas.** Una regresión es un *cambio*, así que necesitas el antes. Sin una baseline almacenada te quedas comparando contra tu recuerdo de cómo se comportaba el modelo, que no es evidencia.

```python
# Run once, before any training. Commit the result.
for case in regression_cases:
    out = base_model.generate(**tok(case["prompt"]), do_sample=False, max_new_tokens=256)
    baseline[case["id"]] = tok.decode(out[0], skip_special_tokens=True)
```

Decodificación greedy, para que un diff signifique un cambio de pesos y no una tirada del sampler.

### Leerlo

Ejecuta la suite en cada checkpoint candidato. Compara con la baseline. Luego clasifica cada cambio:

| Veredicto | Significado |
|---|---|
| Sin cambios | Bien |
| Cambió, sigue siendo correcto | Anótalo; bien |
| Cambió, ahora es incorrecto | **Regresión, bloquea el despliegue** |
| Cambió, ahora es mejor | Un extra, y merece entenderse |

La tercera fila es todo el sentido. Una regresión clara en seguridad o en seguimiento de instrucciones pesa más que un par de puntos en tu métrica de la tarea, porque el modo de fallo no tiene límite y la ganancia sí.

### Reducir el olvido, cuando lo encuentres

Opciones aproximadamente en orden de lo que te cuestan:

1. **Menos pasos, o un checkpoint anterior.** El olvido crece con el entrenamiento. A menudo es la solución más barata, y normalmente cuesta poco rendimiento en la tarea.
2. **Learning rate más bajo.** Las actualizaciones más pequeñas perturban menos.
3. **Rank más bajo, o menos target modules.** Menos capacidad con la que sobrescribir.
4. **Mezclar datos generales de instrucciones.** Unos pocos por ciento de ejemplos generales de seguimiento de instrucciones junto con los datos de tu tarea. Eficaz y bien establecido, y te cuesta pureza del dataset en lugar de calidad del modelo.
5. **Mantener el adapter sin fusionar y enrutar.** La respuesta más completa: aplica el adapter solo a las peticiones que lo necesitan, y sirve el base intacto para todo lo demás. El olvido se vuelve irrelevante porque el base sigue ahí. Lección 25.

La opción 5 es la que la gente pasa por alto, y a menudo es la arquitectura correcta. Si tu fine-tune sirve a un único propósito estrecho dentro de un producto mayor, no necesitas un modelo que lo haga todo.

### Automatízalo

La suite debería ejecutarse en cada checkpoint, sin que nadie lo pida, y negarse a pasar ante una regresión. Una evaluación que depende de que alguien se acuerde de ejecutarla se saltará en la ejecución en la que importaba, la que va con presión de plazo.

## Práctica

1. ▢ ¿Por qué una métrica held-out de la tarea que mejora de forma monótona no descarta una regresión?

<details markdown="1"><summary>Comprobación</summary>

Sale de la distribución de tu tarea y por tanto solo observa tu tarea. Las capacidades fuera de esa distribución le son invisibles, y son exactamente lo que daña el olvido.

Necesitas un instrumento aparte dirigido a lo que *no* estás entrenando.

</details>

2. ▢ Nombra las cuatro categorías de regresión.

<details markdown="1"><summary>Comprobación</summary>

Seguimiento general de instrucciones, cumplimiento de formato y de comportamiento, comportamiento de seguridad y de rechazo, capacidad adyacente no entrenada.

La seguridad es la que se deja fuera con más frecuencia, y el fine-tuning con datos totalmente benignos puede degradarla.

</details>

3. ▢ Tienes un conjunto de regresión pero ninguna baseline almacenada. ¿Qué puedes concluir al ejecutarlo?

<details markdown="1"><summary>Comprobación</summary>

Muy poco. Una regresión es un cambio respecto al comportamiento previo, así que sin el comportamiento previo no puedes identificar una, solo juzgar salidas de forma aislada, lo que no revelará una degradación sutil.

Registra y haz commit de las salidas del base model antes de entrenar. Este es el paso que hace funcionar la suite.

</details>

4. ▢ Métrica de la tarea +3 puntos; el modelo ya no rechaza una petición que el base rechazaba. ¿Despliegas?

<details markdown="1"><summary>Comprobación</summary>

No. Una regresión de seguridad bloquea el despliegue con independencia de las ganancias en la tarea: el riesgo no tiene límite y tres puntos sí.

Investiga: prueba un checkpoint anterior, un learning rate más bajo, mezclar datos generales de instrucciones, o mantener el adapter sin fusionar y enrutar solo el tráfico pertinente hacia él.

</details>

5. ▢ ¿Qué elimina de forma más completa el problema del olvido?

    - a) Mezclar datos generales de instrucciones en el conjunto de entrenamiento
    - b) Servir el base model sin fusionar y enrutar por petición
    - c) Bajar el learning rate y entrenar durante menos pasos
    - d) Reducir el rank del adapter y el número de target modules

<details markdown="1"><summary>Comprobación</summary>

**b)** Servir el base model sin fusionar y enrutar por petición.

Las demás reducen cuánto olvido ocurre. El enrutamiento significa que el base sin modificar sigue disponible para todo lo que quede fuera de tu tarea, así que el olvido en la ruta adaptada deja de importar.

</details>

6. ▢ ¿Por qué decodificación greedy para el conjunto de regresión?

<details markdown="1"><summary>Comprobación</summary>

Para que una diferencia respecto a la baseline sea atribuible a pesos cambiados y no al muestreo. Con una temperature por encima de cero, cada ejecución difiere y el diff no lleva información.

</details>

## Prácticas en el mundo real

- [ ] Escribe 20 casos de regresión, cinco en cada categoría. Incluye al menos uno que el base model rechace.
- [ ] Genera y haz commit de las salidas baseline del base model, de forma greedy, antes de cualquier entrenamiento.
- [ ] Ejecuta la suite sobre tu adapter actual y compara. Clasifica cada cambio en los cuatro veredictos.
- [ ] Mañana: conecta la suite a tu script de entrenamiento para que se ejecute en cada checkpoint sin que se lo pidan.

## Para profundizar

- [Paper: "An Empirical Study of Catastrophic Forgetting in Large Language Models During Continual Fine-tuning", Luo et al., arXiv:2308.08747](https://arxiv.org/abs/2308.08747)
- [Paper: "Fine-tuning Aligned Language Models Compromises Safety, Even When Users Do Not Intend To!", Qi et al., arXiv:2310.03693](https://arxiv.org/abs/2310.03693)
- [Modos de fallo](../reference/failure-modes.md)
- [Lección 25. Servir adapters](0025-serving-adapters.md)

---

¿No termina de quedar claro? Vuelve a leer la fuente primaria de arriba, ya que esta lección la comprime y en la compresión es donde se escapa la comprensión. Consulta el [glosario](../GLOSSARY.md) por si algún término te resultó resbaladizo.

Si lo poco claro es la propia lección y no el material, eso es un defecto: [abre un issue](https://github.com/TokenCemetery/teach/issues).
