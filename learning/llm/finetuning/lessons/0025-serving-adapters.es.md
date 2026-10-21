---
title: "25. Servir adapters"
description: "Fusiona para una tarea, enruta para muchas"
type: lesson
---

# Lección 25. Servir adapters

**Vínculo con la misión:** "Desplegarlo" está en la misión. Un adapter en un directorio no está desplegado.
**Fuente principal:** [Docs: LoRA adapters, vLLM](https://docs.vllm.ai/en/latest/features/lora.html)
**Requisitos previos:** [Lección 13](0013-merging-and-shipping.md), [Lección 24](0024-the-regression-suite.md)

## Calentamiento

1. ▢ ¿Qué decisión de serving vuelve irrelevante el olvido catastrófico?

<details markdown="1"><summary>Comprobación</summary>

Mantener el adapter sin fusionar y enrutar a través de él solo las peticiones pertinentes, dejando el base intacto disponible para todo lo demás.

</details>

2. ▢ ¿Dónde debe fusionarse un adapter entrenado contra un base cuantizado?

<details markdown="1"><summary>Comprobación</summary>

En el base de precisión completa, y cuantizar después si hace falta un artefacto cuantizado.

</details>

3. ▢ ¿Por qué decodificación greedy al verificar una fusión?

<details markdown="1"><summary>Comprobación</summary>

Para que cualquier diferencia de salida sea atribuible a los pesos y no al muestreo.

</details>

## Qué debes saber

### Tres formas de despliegue

**Modelo fusionado.** Un artefacto, indistinguible de cualquier otro modelo. Cualquier stack de serving lo carga. Cero maquinaria de adapters.

**Sin fusionar, un solo adapter.** Base más adapter aplicado en la carga. Añade dos matmuls pequeños por capa adaptada.

**Sin fusionar, varios adapters.** Un base en memoria, muchos adapters, seleccionados por petición. Esta es la forma que hace económicamente interesantes a los adapters y necesita soporte explícito en tiempo de ejecución.

### Elegir

| | Fusionado | Sin fusionar, multi-adapter |
|---|---|---|
| Memoria para N tareas | N modelos completos | Un base + N adapters pequeños |
| Sobrecarga por petición | Ninguna | Pequeña, y mayor con batching mixto |
| Stack de serving | Cualquiera | Debe soportar adapters |
| Cambiar de tarea | Cargar un modelo distinto | Cambiar un campo de la petición |
| Añadir una tarea | Desplegar otro modelo | Soltar un archivo |
| Base aún disponible | No | Sí |
| Rollback | Redesplegar | Dejar de enrutar a ese adapter |

Regla de decisión: **una tarea y operaciones simples → fusiona. Varias tareas, o el base aún necesario → no fusiones.**

Esa última fila está infravalorada. Con un adapter sin fusionar, deshacer un mal fine-tune es un cambio de enrutamiento y no un despliegue, y el base model siempre está ahí como alternativa.

### Cómo funciona el serving multi-adapter

El enfoque ingenuo, intercambiar los pesos del adapter entre peticiones, serializa todo y destruye el throughput, porque el batching es de donde viene la eficiencia de la inferencia.

Las implementaciones reales agrupan en batch peticiones que usan adapters *distintos* a la vez. El cómputo del base model se comparte en todo el batch, ya que es idéntico para todos, y las contribuciones de los adapters se calculan por petición con kernels especializados que manejan un batch de matmuls pequeños y heterogéneos. El trabajo de S-LoRA ([arXiv:2311.03285](https://arxiv.org/abs/2311.03285)) es el punto de referencia para servir muchos adapters de forma concurrente, incluido mantener los adapters inactivos en la memoria del host y paginarlos al entrar.

Lo que esto significa en la práctica:

- Servir decenas de adapters desde un solo base es un problema resuelto con implementaciones reales, no una idea de investigación.
- La sobrecarga es pequeña pero real, y crece con cuántos adapters *distintos* aparecen en un batch.
- Los adapters deberían compartir rank y target modules cuando sea posible. Las formas heterogéneas son más difíciles de agrupar en batch con eficiencia.

En vLLM la forma es aproximadamente: activar el soporte de LoRA, registrar los adapters y nombrar uno por petición. Comprueba los flags actuales y los límites de rank máximo y de adapters máximos en la documentación de la versión instalada, porque esta superficie cambia y los límites se fijan al arrancar el servidor.

### Cuantización en el momento de servir, mantenida aparte

Una decisión independiente de todo lo anterior, y que merece repetirse porque las dos se confunden:

- La **cuantización del momento del entrenamiento** (etapa 4) es un presupuesto de memoria para la ejecución de entrenamiento.
- La **cuantización del momento de servir** encoge el modelo que despliegas, y su costo en calidad es permanente en cada petición.

Puedes entrenar contra un base de 4 bits y servir en bf16. Puedes entrenar en bf16 y servir cuantizado. Son decisiones sin relación con compromisos sin relación, y ninguna implica a la otra.

Si sirves cuantizado, evalúa el artefacto cuantizado. Evaluar un modelo en bf16 y desplegar uno de 4 bits significa que tus números describen algo que no desplegaste, un error sorprendentemente común.

### Esenciales operativos

**Versiona todo.** Base model y revisión, adapter, tokenizer, stack de serving. Una respuesta debería poder rastrearse hasta la configuración exacta que la produjo.

**Fija los parámetros de muestreo.** Temperature, top-p, max tokens, stop sequences. Cambian la calidad de la salida tanto como el fine-tuning, y una deriva de valores por defecto sin documentar se diagnosticará mal como una regresión del modelo.

**Registra inputs y outputs.** El tráfico de producción es la mejor fuente de tu próximo conjunto de entrenamiento y de tu próximo conjunto held-out, porque sale de la distribución real y no de la que imaginaste. Respeta las restricciones evidentes de privacidad y retención; el punto es recoger de forma deliberada en lugar de descubrir más tarde que no lo hiciste.

**Monitoriza la distribución, no solo la latencia.** Longitud de entrada, longitud de salida, tasa de rechazo, validez del esquema. Una deriva en la distribución de entrada es el indicador adelantado de que las suposiciones de tu fine-tune han caducado.

**Mantén el base accesible.** Ya sea como ruta alternativa, como endpoint de comparación o ambas. Poder hacer un A/B del base frente al fine-tune en producción es la evidencia más fuerte disponible de si el fine-tune ayuda.

### El muestreo no es una solución

Una advertencia, porque es una trampa común. Si un fine-tune rinde por debajo, la temperature y el top-p no son la reparación. Cambian la forma de la distribución, no su contenido. Ajustar el muestreo para compensar un problema de entrenamiento lo oculta y vuelve ininterpretable la comparación siguiente: ya no sabes cuál de dos variables produjo una diferencia.

Arregla el entrenamiento en el entrenamiento. Fija el muestreo y déjalo en paz.

## Práctica

1. ▢ Cinco tareas, un base model. ¿Fusionado o sin fusionar, y qué cuesta la elección?

<details markdown="1"><summary>Comprobación</summary>

Sin fusionar. Un base en memoria más cinco adapters pequeños, frente a cinco copias completas del modelo.

Costos: el stack de serving debe soportar adapters, y hay una pequeña sobrecarga por petición que crece con el número de adapters distintos en un batch.

</details>

2. ▢ ¿Por qué el intercambio ingenuo de adapters entre peticiones destruye el throughput?

<details markdown="1"><summary>Comprobación</summary>

Serializa las peticiones por adapter, impidiendo el batching del que depende la eficiencia de la inferencia.

Las implementaciones reales agrupan en batch peticiones con adapters distintos a la vez, compartiendo el cómputo del base y calculando las contribuciones de los adapters por petición con kernels especializados.

</details>

3. ▢ Entrenaste contra un base de 4 bits. ¿Debes servir en 4 bits?

<details markdown="1"><summary>Comprobación</summary>

No. La precisión de entrenamiento y la de serving son independientes. Fusiona en el base de precisión completa y sirve en bf16 si tienes la memoria.

La cuantización del momento del entrenamiento fue un presupuesto para la ejecución. No tiene por qué seguir al artefacto hasta producción.

</details>

4. ▢ Tu fine-tune rinde por debajo en producción. Un colega sugiere bajar la temperature. Evalúalo.

<details markdown="1"><summary>Comprobación</summary>

Puede mejorar las salidas, y no aborda el problema. El muestreo remodela la distribución que produjo el modelo; no puede añadir capacidad de la que el modelo carece.

Peor aún, introduce una segunda variable cambiada, así que la comparación siguiente es ininterpretable. Fija el muestreo, diagnostica el entrenamiento.

</details>

5. ▢ ¿Qué ventaja del serving sin fusionar importa más operativamente?

    - a) La menor huella de memoria al servir muchas tareas
    - b) La capacidad de hacer rollback cambiando una regla de enrutamiento
    - c) La ausencia de cualquier sobrecarga computacional por petición
    - d) La compatibilidad con todos los servidores de inferencia existentes

<details markdown="1"><summary>Comprobación</summary>

**b)** La capacidad de hacer rollback cambiando una regla de enrutamiento.

(a) es real y a menudo la razón principal, pero (b) es lo que quieres a las dos de la madrugada. (c) es falsa, puesto que sin fusionar añade una pequeña sobrecarga. (d) es lo contrario; fusionado es la opción universalmente compatible.

</details>

6. ▢ Evaluaste en bf16 y desplegaste un modelo cuantizado a 4 bits. ¿Qué falla?

<details markdown="1"><summary>Comprobación</summary>

Tus números describen un modelo que no desplegaste. La cuantización del momento de servir lleva un costo permanente de calidad en cada petición, y nunca se midió.

Evalúa el artefacto que despliegas. Siempre.

</details>

## Prácticas en el mundo real

- [ ] Sirve tu adapter a través de un servidor de inferencia y consigue una completion real por todo el camino.
- [ ] Carga dos adapters sobre un base y cambia entre ellos por campo de la petición. Confirma que las salidas difieren como corresponde.
- [ ] Mide la latencia para fusionado, sin fusionar con un solo adapter y sin fusionar multi-adapter. Registra la sobrecarga.
- [ ] Mañana: anota cada versión y parámetro de muestreo de tu ruta de serving, en un solo archivo.

## Para profundizar

- [Docs: LoRA adapters, vLLM](https://docs.vllm.ai/en/latest/features/lora.html)
- [Paper: "S-LoRA: Serving Thousands of Concurrent LoRA Adapters", Sheng et al., arXiv:2311.03285](https://arxiv.org/abs/2311.03285)
- [Lección 26. Costo, latencia y throughput](0026-cost-latency-and-throughput.md)

---

¿No termina de quedar claro? Vuelve a leer la fuente primaria de arriba, ya que esta lección la comprime y en la compresión es donde se escapa la comprensión. Consulta el [glosario](../GLOSSARY.md) por si algún término te resultó resbaladizo.

Si lo poco claro es la propia lección y no el material, eso es un defecto: [abre un issue](https://github.com/TokenCemetery/teach/issues).
