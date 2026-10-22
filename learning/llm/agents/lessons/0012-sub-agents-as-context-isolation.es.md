---
title: "12. Subagentes como aislamiento de contexto"
description: "Lanzar un subagente aísla el trabajo exploratorio largo del presupuesto de contexto del padre"
type: lesson
---

# Lección 12. Subagentes como aislamiento de contexto

**Vínculo con la misión:** Diagnosticar un agente que falla a partir de su trayectoria en lugar de añadir una instrucción más a su prompt.
**Fuente principal:** [Article: "How We Built Our Multi-Agent Research System", Anthropic Engineering](https://www.anthropic.com/engineering/multi-agent-research-system)
**Requisitos previos:** [Lección 11](0011-compaction-and-retrieval-on-demand.md)

## Calentamiento

1. ▢ ¿Cuál es la diferencia entre la compactación y la recuperación bajo demanda?

<details markdown="1"><summary>Comprobación</summary>

La compactación reemplaza los turnos antiguos por un resumen, ahorrando tokens pero con riesgo de perder información. La recuperación bajo demanda mantiene el detalle antiguo fuera del contexto y lo trae solo cuando el modelo lo pide, cambiando un poco de latencia por un contexto residente más pequeño.

</details>

2. ▢ En la compactación más la recuperación bajo demanda, ¿qué tres cosas contiene el contexto siempre residente?

<details markdown="1"><summary>Comprobación</summary>

El objetivo y las restricciones, un resumen del progreso y metadatos (nombres de archivos, herramientas disponibles, títulos de documentos). El detalle completo está comprimido (compactación) o disponible bajo demanda (recuperación).

</details>

## Qué debes saber

### Los subagentes como herramienta de gestión del contexto

Hasta ahora, las lecciones 10 y 11 se centraron en gestionar la transcripción de un solo agente. Pero hay otro enfoque: lanzar un agente aparte para hacer una parte acotada del trabajo. Esto es la etapa 8 (multiagente), pero aquí se acota estrictamente al ángulo del presupuesto de contexto.

Un subagente es una ejecución de agente nueva con su propia transcripción, su propio harness y su propio conjunto de herramientas. Explora, hace llamadas a herramientas, acumula su propia trayectoria. El agente padre, mientras tanto, no ha pagado el costo de nada de esa exploración. Ninguno de los turnos del subagente aparece en la transcripción del padre.

Cuando el subagente termina, produce un resultado final o un resumen. Ese resumen (apenas unas frases o una estructura de datos) se añade a la transcripción del padre. Todo el razonamiento interno del subagente, todos sus callejones sin salida, todas sus llamadas a herramientas y sus fallos, quedan fuera del contexto del padre.

### La idea clave: una trayectoria grande y aislada no le cuesta nada al padre

Supón que un subagente gasta 100 turnos leyendo archivos, comparando patrones, topando con callejones sin salida y refinando su análisis. Su trayectoria es enorme. Pero desde la perspectiva del padre, todo ese trabajo es invisible. El padre solo ve el informe final, unos cientos de tokens. Mientras tanto, el contexto del padre se mantiene pequeño y barato.

Esto es distinto de la compactación y de la recuperación bajo demanda, que operan ambas dentro de una sola transcripción. Un subagente opera por completo fuera de la transcripción del padre. Su costo lo asume el harness del subagente, no el del padre.

### El intercambio: el razonamiento invisible significa detalles perdidos

Como el razonamiento interno del subagente es invisible para el padre, se puede perder información que el padre no pensó en pedir. Si el padre lanza un subagente para "leer estos archivos y resumirlos", el subagente podría descubrir algo interesante pero periférico: "también noté una fuga de memoria en util.cpp". Si el padre no pidió eso, el subagente podría omitirlo del informe, y el padre nunca se entera.

Esto es distinto del riesgo de la compactación, donde el harness controla qué se resume. Con un subagente, la frontera entre "qué reportar" y "qué dejar interno" es elección del propio subagente. Si el subagente es un modelo de lenguaje, estimará qué le importa al padre a partir de las instrucciones que recibió. Esa estimación puede ser errónea.

### Cuándo vale la pena un subagente y cuándo no

Un subagente vale el costo de coordinación cuando:

- La subtarea es grande y acumulará una trayectoria larga (muchos turnos, muchas llamadas a herramientas, muchos callejones sin salida).
- La subtarea está acotada: hay un punto de parada claro y el padre no necesitará el razonamiento del subagente para el trabajo posterior.
- El costo de lanzar un agente nuevo (latencia, sobrecarga de coordinación) es mucho menor que el costo de mantener la exploración del subagente en el contexto del padre.

Por ejemplo: "Investiga la historia de este código base, lee el git log y los PR principales, y dame un resumen de tres frases". Esa es una tarea grande y acotada. Un subagente que explora durante 50 turnos le ahorra al padre 50 turnos de costo de contexto.

Un subagente no vale la pena cuando:

- La tarea es pequeña (de todos modos solo llevará unos pocos turnos).
- La tarea requiere una coordinación estrecha con el padre (el padre hará preguntas aclaratorias, el subagente tendrá que refinar su trabajo).
- El padre necesitará más adelante el razonamiento completo del subagente (para entender por qué se llegó a una conclusión, para detectar una suposición, para depurar un error).

Por ejemplo: "Obtén la temperatura de mañana". Es una tarea de pocos turnos; lanzar un subagente cuesta más que hacerlo en el padre.

## Práctica

1. ▢ A un agente se le encarga revisar código en 50 archivos y producir un informe. El desarrollador ha dividido el trabajo: el agente principal revisa 5 archivos y lanza un subagente para revisar los otros 45. ¿Por qué es este un buen uso de un subagente?

    - a) Los subagentes siempre son más rápidos que los agentes individuales
    - b) La larga trayectoria del subagente (revisar 45 archivos) queda aislada del contexto del agente principal, manteniendo el contexto principal pequeño y barato
    - c) Los subagentes nunca cometen errores
    - d) El agente principal puede ver de inmediato todo el razonamiento del subagente

<details markdown="1"><summary>Comprobación</summary>

**b)** Un subagente le permite al agente principal delegar una tarea grande y acotada. Los más de 100 turnos de exploración del subagente no inflan el contexto del agente principal. El agente principal solo recibe el informe final del subagente. La opción a es incorrecta porque los subagentes pueden añadir latencia. La opción c es incorrecta porque los subagentes pueden cometer errores. La opción d es incorrecta porque el razonamiento interno del subagente es invisible para el agente principal.

</details>

2. ▢ Un subagente está revisando un código base y descubre una vulnerabilidad de seguridad. No está directamente relacionada con la tarea que pidió el padre (revisión de estilo de código), pero es crítica. ¿Qué riesgo crea aquí la invisibilidad del subagente?

<details markdown="1"><summary>Pista</summary>

Las instrucciones del subagente le dijeron que se centrara en el estilo del código. ¿Quién decide qué se reporta al padre, y qué podría perderse?

</details>

<details markdown="1"><summary>Comprobación</summary>

El subagente decide qué incluir en su informe final según sus instrucciones. Si las instrucciones hacen hincapié en el estilo del código, el subagente podría no reportar el problema de seguridad en absoluto, o mencionarlo como una nota al pie que el padre pasa por alto. Se puede perder información que el padre no pensó en pedir porque el padre nunca ve el razonamiento completo del subagente. El padre tiene que ser muy explícito: "Reporta todo lo crítico que encuentres, sea de estilo o no".

</details>

3. ▢ Compara dos enfoques para una larga tarea de investigación:
    - Enfoque A: Un solo agente que compacta los turnos antiguos y usa recuperación bajo demanda. Tarda 80 turnos, el contexto residente se mantiene por debajo de 30.000 tokens.
    - Enfoque B: El agente principal lanza 3 subagentes para explorar en paralelo. Cada uno tarda 40 turnos internamente. El agente principal recibe un resumen de cada uno. El contexto final del agente principal es de 5.000 tokens más la sobrecarga de coordinación.

¿Qué enfoque tiene el menor costo total en tokens (contando todas las ejecuciones de agentes), y por qué?

    - a) El enfoque A, porque evita la sobrecarga de los subagentes
    - b) El enfoque B, porque las tres exploraciones están aisladas y son baratas para el agente principal
    - c) Cuestan lo mismo
    - d) Depende de cuánta sobrecarga de coordinación haya

<details markdown="1"><summary>Comprobación</summary>

**d)** El enfoque A envía 30.000 tokens al modelo 80 veces, aproximadamente 2,4 M de tokens. El enfoque B envía aproximadamente 50.000 tokens al modelo 40 veces en cada subagente, más la coordinación con el agente principal. Si la coordinación es mínima y el trabajo de los subagentes es realmente paralelo y acotado, el enfoque B puede ser más barato. Pero si la coordinación es cara o los subagentes necesitan refinar sus resultados de forma iterativa, el enfoque A puede ser mejor. La respuesta depende del costo real de lanzar y coordinar a los subagentes.

</details>

4. ▢ Estás diseñando un agente para "depurar este conjunto de pruebas que falla y proponer una solución". ¿Deberías usar un subagente, y por qué sí o por qué no?

<details markdown="1"><summary>Comprobación</summary>

No. La depuración es una tarea en la que el padre probablemente necesitará el razonamiento completo del subagente para juzgar si la solución propuesta es segura, para detectar suposiciones o para hacer preguntas aclaratorias. No es una tarea acotada con un informe simple; requiere una coordinación estrecha. El razonamiento invisible del subagente sería un lastre. Es mejor mantener la depuración en el bucle principal del padre, donde este puede seguir la trayectoria completa.

</details>

## Prácticas en el mundo real

- [ ] Describe una tarea en la que usarías un subagente y explica por qué una trayectoria grande y aislada vale el costo de coordinación.
- [ ] Describe una tarea en la que no usarías un subagente, y explica qué información se perdería si lo hicieras.
- [ ] Mañana: Esboza las responsabilidades del padre y del subagente para una tarea de varias partes (por ejemplo, "investiga esta biblioteca y luego intégrala en nuestro código base"). ¿Dónde pones la frontera, y qué le reporta cada agente al otro?

## Para profundizar

- [Article: "How We Built Our Multi-Agent Research System", Anthropic Engineering](https://www.anthropic.com/engineering/multi-agent-research-system)
- [Recursos](../RESOURCES.md)

---

¿No termina de quedar claro? Vuelve a leer la fuente primaria de arriba, ya que esta lección la comprime y en la compresión es donde se escapa la comprensión. Consulta el [glosario](../GLOSSARY.md) por si algún término te resultó resbaladizo.

Si lo poco claro es la propia lección y no el material, eso es un defecto: [abre un issue](https://github.com/TokenCemetery/teach/issues).
