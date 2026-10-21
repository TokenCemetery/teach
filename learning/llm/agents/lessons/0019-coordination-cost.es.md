---
title: "19. Costo de coordinación"
description: "Entender por qué construir varios agentes es más caro que un solo agente bien equipado, y cómo decidir cuándo vale la pena la ganancia del paralelismo"
type: lesson
---

# Lección 19. Costo de coordinación

**Vínculo con la misión:** Para elegir entre un solo agente bien equipado y un sistema multiagente, necesitas saber qué cuestan los sistemas orquestador-worker en tokens, en razonamiento y en contexto fragmentado, y cómo juzgar si un segundo agente aporta algo que no se le habría podido dar directamente al primer agente.
**Fuente principal:** [Article: "Don't Build Multi-Agents", Cognition](https://cognition.ai/blog/dont-build-multi-agents)
**Requisitos previos:** [Lección 18](0018-orchestrator-and-worker.md)

## Calentamiento

1. ▢ De la lección 18, recuerda: en un sistema orquestador-worker, ¿puede un worker ver la trayectoria completa de razonamiento de otro worker mientras el otro worker está corriendo?

<details markdown="1"><summary>Comprobación</summary>

No. Cada worker corre su propio bucle de agente con su propia transcripción aislada. Los workers solo ven los hallazgos de los demás si el orquestador se los pasa de forma explícita, y solo los informes finales, no el razonamiento completo. Este aislamiento es una ventaja (mantiene limpio el contexto) y un costo (los workers no pueden compartir ideas a mitad de la tarea).

</details>

2. ▢ De la lección 18, recuerda: ¿cuál es la diferencia entre el fan-out y el traspaso?

<details markdown="1"><summary>Comprobación</summary>

El fan-out lanza varios workers sobre variaciones del mismo problema en paralelo, explorando distintos ángulos a la vez para una cobertura más amplia y paralelismo. El traspaso es secuencial: un agente termina su tarea y pasa un contexto limpio a un segundo agente especializado en la siguiente fase. Ambos son patrones multiagente; el fan-out usa el tiempo, el traspaso usa la especialización.

</details>

## Qué debes saber

### Costo en tokens: muchos agentes cuestan muchas veces más

Cada ejecución de un agente tiene un costo. Un sistema orquestador-worker paga ese costo varias veces.

Supón que un solo agente resuelve un problema con 10.000 tokens: digamos, 20 turnos con 500 tokens por turno. Ahora supón que el mismo problema se divide en tres subtareas independientes, cada una resuelta por un worker con 8.000 tokens (un poco menos, porque cada worker tiene un foco más estrecho). El propio orquestador usa 2.000 tokens para descomponer la tarea y sintetizar los resultados.

Costo total: 8.000 + 8.000 + 8.000 + 2.000 = 26.000 tokens. El sistema multiagente costó 2,6 veces lo que costó el agente único, aunque cada worker fue un poco más eficiente de lo que habría sido el agente único en su parte por separado. Los workers exploran en paralelo, así que el tiempo real es más rápido, pero el costo en tokens se multiplica.

Esta cuenta empeora si los workers corren de forma ineficiente o si el orquestador tiene que coordinar más de una vez (por ejemplo, el orquestador se da cuenta de que los workers pasaron por alto una dependencia, lanza nuevos workers o les pide que vuelvan a correr con nuevas instrucciones). El artículo de Cognition señala esto como la pregunta central: ¿vale la aceleración del paralelismo pagar varias veces el costo en tokens?

### Contexto fragmentado: los workers no pueden verse entre sí

Cuando un solo agente ejecuta una tarea larga, va construyendo contexto: sabe qué ha probado, qué funcionó, qué no y por qué. Un sistema multiagente fragmenta ese contexto. Los workers A y B pueden investigar terreno que se solapa (por ejemplo, ambos intentando entender una restricción), pero el worker A no ve el razonamiento del worker B sobre esa restricción; solo ve el informe final.

En concreto: el worker A se da cuenta a mitad de la tarea de que una restricción tiene una implicación sutil. El worker A razona sobre ello, construye intuición y reporta. El orquestador lee el informe y se lo pasa al worker B. El worker B ahora conoce la conclusión pero no el razonamiento que llevó a ella. El worker B no puede refinar ni cuestionar ese razonamiento a mitad de la tarea, porque no ve el pensamiento del worker A. El worker B o bien acepta el informe y lo usa (perdiendo la oportunidad de refinarlo) o lo ignora y vuelve a derivar la misma idea (desperdiciando tokens).

Para las tareas en las que la mejor respuesta surge de un ir y venir de refinamiento entre varias líneas de razonamiento, el contexto fragmentado es una limitación real. Un solo agente con suficientes turnos puede tener todo su razonamiento en un solo lugar e integrar las ideas a medida que se desarrollan.

### Conclusiones en conflicto: la exploración independiente lleva al desacuerdo

Cuando dos workers exploran el mismo terreno de forma independiente, pueden llegar a conclusiones distintas. Esto no es necesariamente un error; podrían haber encontrado interpretaciones genuinamente distintas (y ambas válidas). Pero también podría significar que un worker cometió un error, o pasó por alto algo que el otro detectó.

El orquestador ve ambos informes y tiene que conciliarlos. Si el conflicto es semántico o factual, el orquestador tiene un problema: solo tiene los resúmenes de los workers, no su razonamiento completo, así que no puede rastrear con facilidad de dónde vino el desacuerdo. El orquestador podría lanzar un nuevo agente (un subagente "juez" o "sintetizador") para conciliar, lo que añade más costo.

La alternativa del agente único evita esto: un solo agente que recorre el mismo terreno en serie integra cada nuevo hallazgo en su modelo mental en curso, así que puede detectar contradicciones a medida que surgen y resolverlas dentro de su propio bucle de razonamiento.

### El principio de decisión: ¿cuándo es más barato lo multiagente?

La fuente principal de Cognition sostiene que la mayoría de los sistemas multiagente no son más baratos, ni en tokens ni en calidad de razonamiento, que un solo agente con mejores herramientas. La pregunta no es "¿es más rápido el paralelismo?" (sí) sino "¿compra el paralelismo algo que un solo agente no habría podido tener por menos costo?"

Aplica este principio de decisión:

**Lo multiagente tiene sentido cuando:**

- Las subtareas son realmente independientes (sin contexto compartido, sin dependencia de los resultados de las demás a mitad de la tarea).
- Cada subtarea es más simple que la tarea original (cada worker resuelve un problema genuinamente más estrecho, de modo que la ganancia de eficiencia sumada de los workers supera el costo de la duplicación).
- Necesitas la aceleración del paralelismo (el ahorro de tiempo justifica el multiplicador de tokens; tienes un plazo en tiempo real que no puedes cumplir con un agente y más turnos).
- Las herramientas de cada worker están lo bastante especializadas como para que un conjunto de herramientas compartido ralentizara a cada worker con opciones irrelevantes.

**Un solo agente con más recursos suele ganar cuando:**

- Las subtareas comparten contexto o se refinan entre sí (un solo agente mantiene conectado todo su razonamiento; un sistema multiagente tiene que volver a derivar o a comunicar).
- Tienes margen en el presupuesto de contexto (dale al agente único una ventana de contexto mayor, mejor recuperación, más herramientas, más turnos).
- Las subtareas son interdependientes o requieren un ir y venir de refinamiento entre varias líneas de pensamiento.
- La sobrecarga de coordinación (tiempo del orquestador, comunicación, conciliación de conclusiones en conflicto) es alta en relación con el problema.

Dicho sin rodeos: un solo agente con mejores herramientas, un contexto más largo y más turnos a menudo resuelve el mismo problema más barato y con mejor calidad de razonamiento que varios agentes con contexto fragmentado. La aceleración del paralelismo es real pero no es gratis.

## Práctica

1. ▢ Estás construyendo un sistema de preguntas y respuestas. Opción A: un agente con herramientas de búsqueda, ejecución de código y documentación. Opción B: un orquestador que lanza tres workers en paralelo, cada uno con una herramienta especializada (worker de búsqueda, worker de código, worker de documentación). Ambos buscan responder preguntas complejas de usuarios. ¿En qué circunstancias el costo en tokens de la opción B se vuelve más barato que el de la opción A?

<details markdown="1"><summary>Comprobación</summary>

Esto es una trampa. En la mayoría de las circunstancias, la opción B cuesta más en tokens porque pagas el costo completo de un agente tres veces, más la sobrecarga del orquestador. El costo en tokens de la opción B solo se vuelve más barato que el de la opción A si la ganancia por especialización es enorme, o si los tres workers pueden terminar cada uno tan rápido (menos turnos) que 3 veces barato supere a 1 vez caro. Más probable: la opción A (un agente con varias herramientas) es más cara en tokens que cualquiera de las dos opciones, porque el agente único tiene que deliberar sobre qué herramienta usar. La opción B podría superar a una opción C (un agente más lento) pero rara vez supera a un solo agente de igual calidad y acceso a herramientas. El intercambio es tiempo real (la opción B es más rápida por el paralelismo) frente a tokens (la opción A es más barata). Eliges la opción B por velocidad, no por costo.

</details>

2. ▢ En el sistema orquestador-worker de la lección 18 (workers de investigación en paralelo), supón que dos workers acaban investigando la misma fuente y llegan a conclusiones distintas sobre lo que dice. El orquestador tiene ambos informes. ¿Qué le falta al orquestador que habría tenido un solo agente?

<details markdown="1"><summary>Pista</summary>

Piensa en qué hay en la transcripción de cada worker frente a qué hay en la transcripción de un solo agente en el momento de razonar sobre esa fuente.

</details>

<details markdown="1"><summary>Comprobación</summary>

El orquestador ve dos conclusiones pero no el razonamiento que llevó a cada una. Un solo agente, tras leer la misma fuente, habría tenido todo su razonamiento sobre esa fuente en una transcripción: cómo interpretó el texto, qué matiz notó, qué consideró y descartó. El razonamiento del agente único es totalmente rastreable. El orquestador solo puede preguntar "¿por qué llegaste a esa conclusión?" y un worker tendría que volver a explicarlo, o el orquestador tendría que lanzar un nuevo agente para rastrear el desacuerdo. Esto es contexto fragmentado.

</details>

3. ▢ Estás decidiendo si usar fan-out (orquestador-worker) o un solo agente para una tarea. La tarea es: dado un conjunto de datos y una pregunta, limpiar los datos, explorarlos, construir un modelo e informar de los hallazgos. ¿Correrán las fases (limpieza, exploración, modelado, informe) en paralelo bajo fan-out, o de forma secuencial?

    - a) En paralelo, porque el fan-out lanza todos los workers a la vez.
    - b) De forma secuencial, porque explorar depende de limpiar y modelar depende de explorar.
    - c) En paralelo, pero el trabajo se puede dividir para que cada worker haga todas las fases de forma independiente.
    - d) Depende de si los workers tienen acceso al mismo conjunto de datos.

<details markdown="1"><summary>Comprobación</summary>

**b)** Esta tarea no encaja bien con el fan-out porque las fases son secuenciales: no puedes explorar bien datos sucios, no puedes modelar sin entender los datos, etc. Cada fase depende de la anterior. El fan-out brilla en tareas con subtareas independientes (investigar el ángulo A, el ángulo B y el ángulo C en paralelo). Para trabajo secuencial, el traspaso (lección 18) encaja mejor que el fan-out, o un solo agente con suficientes turnos es más simple. (a) es incorrecta: el paralelismo no crea magia; las dependencias siguen existiendo. (c) es posible pero anula el propósito de la especialización; cada worker necesitaría todas las herramientas y todo el conocimiento. (d) es una pista falsa; el acceso a los datos no es el factor limitante aquí.

</details>

4. ▢ El artículo de Cognition sostiene que un solo agente con mejor recuperación o herramientas más capaces a menudo resuelve problemas más barato en tokens que un sistema orquestador-worker. ¿Cuál es la razón central de esta afirmación?

<details markdown="1"><summary>Comprobación</summary>

Un solo agente tiene todo su razonamiento en una transcripción, así que integra hallazgos, detecta contradicciones y refina conclusiones dentro de un solo bucle de razonamiento. Un sistema orquestador-worker paga el costo en tokens de muchos bucles de agente, y fragmenta el contexto entre ellos, de modo que los workers vuelven a derivar o a comunicar ideas. La ganancia de eficiencia del agente único por mantener unificado el contexto y conectado el razonamiento a menudo supera la aceleración por paralelismo del sistema multiagente, sobre todo cuando la pregunta tiene dependencias o se beneficia de un razonamiento integrado. Darle a un agente más herramientas o mejor recuperación (ambas más baratas que correr varios agentes) a menudo gana.

</details>

5. ▢ Estás construyendo un sistema para depurar un programa que falla. Consideras el fan-out: lanzar tres workers, cada uno probando una estrategia de depuración distinta en paralelo, y luego hacer que el orquestador elija la mejor idea. ¿Qué costo no recoge este diseño y enseña la lección 19?

<details markdown="1"><summary>Comprobación</summary>

El costo en tokens multiplicado por tres (cada worker es una ejecución completa de un agente), el contexto fragmentado (ningún worker ve las exploraciones de los demás, así que podrían volver a derivar el mismo callejón sin salida tres veces en lugar de aprender unos de otros) y que el orquestador tiene que conciliar conclusiones potencialmente en conflicto sobre cuál es el error. Un solo agente que probara las tres estrategias en serie construiría un modelo unificado del error sobre la marcha. Los tres workers no pueden hacer eso sin que el orquestador ejecute un paso de conciliación (otro agente, más costo). El fan-out compra velocidad (los tres workers terminan en el tiempo del worker más lento, no en la suma de los tres), pero los costos son altos para una tarea como la depuración, donde una idea se construye sobre otra.

</details>

## Prácticas en el mundo real

- [ ] Toma un problema que hayas resuelto antes (depuración, análisis, planificación, investigación, lo que sea). Recórrelo mentalmente como un solo agente con muchos turnos frente a tres workers en fan-out. ¿Dónde te ganaría tiempo real el paralelismo? ¿Dónde te costaría el contexto fragmentado y te obligaría a volver a derivar o a conciliar?
- [ ] Lee al menos una vez el artículo de Cognition "Don't Build Multi-Agents". Busca la sección donde el autor sostiene que un solo agente más mejores herramientas supera al orquestador-worker. Anota un ejemplo concreto que dé y qué hizo más barato al agente único.
- [ ] Mañana: esboza una tarea que podrías convertir en un sistema de agentes. Para esa tarea, estima: ¿cuántos tokens usaría un solo agente? ¿Cuántos costaría un sistema de fan-out (supón tres workers, cada uno con un costo en tokens ligeramente menor que la porción por tarea del agente único)? ¿Te vale la pena la aceleración frente al multiplicador de tokens?

## Para profundizar

- [Article: "Don't Build Multi-Agents", Cognition](https://cognition.ai/blog/dont-build-multi-agents)
- [Article: "How We Built Our Multi-Agent Research System", Anthropic Engineering](https://www.anthropic.com/engineering/multi-agent-research-system)
- [Recursos](../RESOURCES.md)

---

¿No termina de quedar claro? Vuelve a leer la fuente primaria de arriba, ya que esta lección la comprime y en la compresión es donde se escapa la comprensión. Consulta el [glosario](../GLOSSARY.md) por si algún término te resultó resbaladizo.

Si lo poco claro es la propia lección y no el material, eso es un defecto: [abre un issue](https://github.com/TokenCemetery/teach/issues).
