---
title: "19. Revisar un informe de eval"
description: "Nombrar con precisión qué volvería poco fiable el número de un informe de eval (contaminación, un juez sin calibrar, una sola ejecución sin estimación de varianza, una posición en una tabla de clasificación que sustituye a una decisión específica de la tarea), en lugar de decir que se siente flojo"
type: lesson
---

# Lección 19. Revisar un informe de eval

**Vínculo con la misión:** Cada habilidad de este arco construye hacia una sola cosa: un número que puedas defender tú mismo. Esta lección es la habilidad complementaria: revisar el número de otra persona y decir, de forma específica y a partir del material, qué lo volvería poco fiable, en lugar de limitarte a sentirlo incompleto. Una suite de evals, una vez construida, es infraestructura compartida: otros equipos condicionan sus lanzamientos a su número, y cambiar un juez, un umbral o una métrica invalida en silencio decisiones ya tomadas. Revisar y mantener una con honestidad es una decisión de criterio propia de un perfil senior.
**Fuente principal:** [Paper: "Judging LLM-as-a-Judge with MT-Bench and Chatbot Arena", Zheng et al., 2023](https://arxiv.org/abs/2306.05685)
**Requisitos previos:** [Lección 6](0006-judge-bias-and-human-agreement.md), [Lección 9](0009-statistical-significance-vs-noise.md), [Lección 10](0010-defending-the-go-no-go-call.md), [Lección 18](0018-public-benchmarks.md)

## Calentamiento

1. ▢ ¿Qué significa que un juez esté calibrado, y qué fallo específico describe la lección 5 como compresión de las puntuaciones?

<details markdown="1"><summary>Comprobación</summary>

Las puntuaciones de un juez calibrado siguen la calidad real de forma consistente entre ejemplos. La compresión de las puntuaciones hacia el techo es un fallo en el que el juez califica casi todo alto sin importar las diferencias reales de calidad, y borra las distinciones que una eval existe para detectar.

</details>

2. ▢ ¿Cuál es la conclusión honesta cuando una diferencia de puntuación de una eval cae dentro del ruido estimado, y cuáles son dos formas de obtener una respuesta más clara?

<details markdown="1"><summary>Comprobación</summary>

La conclusión honesta no es "no hay diferencia" sino "todavía no hay evidencia suficiente para decirlo". Dos formas de aclararlo: ejecutar la eval con más ejemplos (reduciendo el error estándar), o ejecutar una prueba de significancia pareada como es debido sobre los ejemplos concretos en que las variantes discrepan.

</details>

3. ▢ Una posición en una tabla de clasificación agrega preferencias a través de qué tres cosas que podrían no coincidir con tu tarea real?

<details markdown="1"><summary>Comprobación</summary>

Usuarios, tareas y casos de uso que no son los tuyos. Una posición en una tabla de clasificación puede ser un primer filtro razonable para decidir qué modelos evaluar más a fondo, pero no pasa la prueba del OEC que estableció la lección 15 porque no está ligada causalmente a tu decisión concreta.

</details>

## Qué debes saber

### La lista de revisión: qué vuelve poco fiable un número

Cuando alguien presenta un informe de eval o el diseño de un harness, recorre estas preguntas en orden. Donde el informe no tenga respuesta, habrás encontrado la brecha que vuelve poco fiable el número, de forma específica y con nombre.

**Etapas 1-2: ¿Es el conjunto realmente held-out?**

Pregunta: ¿Qué evidencia hay de que los datos de eval son held-out? ¿Ha comprobado el equipo la contaminación con las técnicas que enseñó la lección 2 (canary strings, pruebas de adivinar el resto de la instancia, o ambas)? Si el informe dice "los datos son de un benchmark público", también debería informar de si la saturación de ese benchmark (rendimiento en el techo sin mejora real) o su contaminación ya están documentadas en la práctica. Si no se reporta ni una comprobación de contaminación ni evidencia de saturación, el número podría estar inflado porque el modelo simplemente ya había visto las preguntas en el entrenamiento, o por memorizar un benchmark muy ajustado en lugar de aprender la habilidad de fondo.

**Etapa 2: ¿Está la métrica realmente ajustada a la tarea?**

Pregunta: ¿Por qué se usa esta métrica para esta tarea? Si el informe dice "exactitud", ¿es esa la métrica correcta (la lección 3 cubre cuáles son los modos de fallo de cada métrica), o F1, BLEU, ejecución de código u otra cosa mediría realmente lo que importa? Si se construyó una métrica propia, ¿qué evidencia hay de que se correlaciona con el resultado real (p. ej., preferencia humana, éxito de la tarea)? Un informe que no justifica su elección de métrica ha hecho una suposición disfrazada de decisión.

**Etapas 3 y 6: Si se usa un juez LLM, ¿es realmente fiable?**

Pregunta tres cosas:

- **Diseño:** ¿Cuál es el prompt del juez, y qué hizo el equipo para calibrarlo antes de ejecutarlo a escala? ¿Le da el prompt al juez una respuesta de referencia cuando la hay? La lección 5 enseña la calibración; si el informe no la menciona, el juez puede estar sufriendo compresión de las puntuaciones u otros modos de fallo de falta de calibración.
- **Comprobaciones de sesgo:** ¿Se comprobó el sesgo de posición del juez (¿cambia la misma comparación pareada si se intercambia el orden?)? ¿Se comprobó el sesgo de verbosidad (¿prefiere el juez la longitud con independencia de la corrección?)? La lección 6 cubre estos sesgos; si el informe no menciona haberlos comprobado, podrían estar inflando o desinflando los números en silencio.
- **Acuerdo humano:** ¿Cuál es la tasa de acuerdo del juez con evaluadores humanos sobre una muestra, y cuál es el acuerdo entre humanos sobre la misma muestra? Un juez con un 82% de acuerdo suena flojo hasta que te enteras de que los evaluadores humanos coinciden entre sí en un 80%, en cuyo caso el juez rinde aproximadamente tan bien como lo haría otro humano. Un informe que afirma usar un juez LLM sin medirlo contra el juicio humano afirma un atajo sin evidencia de que funcione.

**Etapas 5 y 9-10: ¿Está el número respaldado por la varianza, o es una sola ejecución?**

Pregunta: ¿Cuántas veces se ejecutó la eval, y cuál fue la dispersión? Si es un número de una sola ejecución con una temperatura distinta de cero, el ruido de ese número (el error estándar de la lección 9) es invisible. ¿Midió el equipo un error estándar o ejecutó una prueba de significancia para confirmar que la brecha observada es claramente mayor que el ruido? Si se reporta una mejora sin una estimación de significancia, no puedes saber si es una victoria real o una coincidencia estadística. Comprueba también si el umbral se fijó antes de que se ejecutara la eval o después, y si respeta el piso de ruido: la lección 10 enseña que un umbral más estrecho de lo que la eval puede resolver realmente es una moneda al aire disfrazada de decisión.

**Etapa 11: ¿Tiene en cuenta el costo y la latencia?**

Pregunta: ¿Se sopesa la mejora reportada frente a lo que cuesta servirla? El costo por petición y el costo por token para modelos con una división distinta entre entrada y salida: ¿se mencionan, y vale realmente la mejora de calidad ese multiplicador? Si se midió la latencia, ¿fue la latencia de cola (p95/p99) o solo un promedio? La lección 17 enseña por qué un promedio sin cambios puede esconder una cola claramente peor. Si el informe dice "la calidad mejoró" sin costo ni latencia, falta la mitad de la decisión de go/no-go.

**Etapa 12: ¿Se apoya en una tabla de clasificación en lugar de en un número específico de la tarea?**

Pregunta: ¿Dice el informe "este modelo ocupa el puesto X en MMLU" o "este modelo puntúa X en nuestra eval específica de la tarea"? Si se apoya en un benchmark público o en una posición en una tabla de clasificación como evidencia, la lección 18 establece que una posición en una tabla de clasificación no pasa la prueba que necesita un OEC real: no está ligada causalmente a tu decisión concreta, y conlleva vectores de manipulación documentados (divulgación selectiva, sesgo de estilo). Una decisión de go/no-go específica de la tarea no sustituye a una comprobación de la tabla de clasificación, pero una posición en una tabla de clasificación tampoco sustituye a un número específico de la tarea.

### La habilidad concreta: zanjar si un juez LLM puede sustituir a una decisión de go/no-go específica de la tarea

Este espacio de trabajo ha presentado dos relatos creíbles sobre los jueces LLM. Las lecciones 5 y 6 enseñaron cómo construir y calibrar uno, y los encontraron útiles para tareas abiertas cuando se construyen con cuidado. Pero una pregunta legítima planea sobre toda la idea: ¿es un juez LLM alguna vez lo bastante fiable para sustituir a una eval específica de la tarea, o está fundamentalmente limitado a un cribado previo o a una comprobación de correlación?

El paper de Zheng et al. de 2023, "Judging LLM-as-a-Judge", establece que los jueces LLM pueden medir bien las preferencias humanas en tareas abiertas (en Chatbot Arena, la preferencia pareada de un juez coincide con las preferencias humanas alrededor del 80% de las veces), y que esto es lo bastante bueno para usarlo en la práctica, pero *solo* cuando se comprueban y se corrigen los sesgos conocidos (posición, verbosidad, autopromoción) y solo cuando se mide el juez frente al acuerdo humano y no frente a un estándar perfecto imaginado.

Esta es la jugada que necesita hacer un revisor cuando esta pregunta surge en una conversación real. Dos personas, ambas citando fuentes plausibles, discrepan:

**El ingeniero A dice:** "Zheng et al. mostraron que los jueces funcionan; podemos usar un juez LLM para nuestra decisión de go/no-go."

**El ingeniero B dice:** "Sí, pero Zheng también mostró que los jueces tienen sesgos; una métrica específica de la tarea sería más honesta."

Ambos citan el mismo paper. La diferencia está en lo que cada uno extrae de él.

La jugada correcta no es elegir un bando por intuición, ni repartir la diferencia de forma vaga ("a veces los jueces funcionan, usa tu criterio"). La jugada correcta es volver al paper y comprobar si las condiciones bajo las que se sostienen los hallazgos de Zheng coinciden con tu situación real:

**Las condiciones de Zheng:** Los jueces midieron mejor en comparaciones de preferencia pareadas para tareas abiertas (escritura, razonamiento, creatividad). La comparación fue pareada, no puntual (no calificar en una escala de 1 a 10). Los evaluadores humanos de la misma tarea coincidían ellos mismos entre sí en torno al 80%. Se comprobaron en el juez varios sesgos y se aplicaron correcciones. El veredicto se usó como un filtro o una señal, no como una decisión final de go/no-go sin revisar.

**Ahora, tu situación:** ¿Es tu tarea abierta, o tiene una respuesta correcta nítida? ¿Calificas por pares o en una escala numérica? ¿Has medido el acuerdo humano en esta tarea y, si es así, cuál es? ¿Has comprobado en el juez el sesgo de posición, de verbosidad y de autopromoción, y tienes un plan para corregirlos si se encuentran? ¿La salida de este juez la revisa una persona antes de que impulse una decisión, o se sostiene sola?

Si tu situación coincide estrechamente con las condiciones de Zheng, el hallazgo de que "los jueces funcionan cuando se construyen con cuidado" se aplica de forma más directa. Si tu tarea es nítida, o si no has medido el acuerdo humano en ella, o si la salida del juez impulsa la decisión sin revisión, el peso de la evidencia cambia. La habilidad no es "recordar lo que dice Zheng" sino "comprobar si las condiciones que hicieron cierto ese hallazgo se aplican a lo que estás construyendo".

### Cómo suena el buen criterio al revisar un informe de eval

> "El informe afirma una mejora de 5 puntos en su eval específica de la tarea con un juez LLM, pero no dice cuántas ejecuciones se hicieron ni cuál es el error estándar en un conjunto de 100 ejemplos con una línea base del 70%; eso son probablemente de 4 a 5 puntos de ruido, lo que significa que esta brecha puede ser real o puede no serlo. Tampoco mencionaron haber comprobado en el juez el sesgo de posición o de verbosidad, y no citan el acuerdo humano sobre las mismas muestras. Antes de lanzar basándonos en este número, necesitamos el error estándar calculado, una comprobación de sesgos del juez y una medición frente al acuerdo humano sobre una muestra de la tarea. O, si la tarea es lo bastante nítida, deberían haber usado desde el principio una métrica específica de la tarea en lugar de un juez."

Nada de eso es un dato que hayas buscado. Es la forma del escepticismo para el que existía este espacio de trabajo.

### Mantener una suite de evals de la que otros dependen

Una vez que has construido una eval, y otros equipos condicionan sus lanzamientos a su número, la eval se convierte en infraestructura compartida. Cambiar el juez, la métrica, el umbral o la forma del conjunto de datos invalida en silencio decisiones ya tomadas sobre la versión antigua. Un equipo que lanzó basándose en "la versión 1.0 de la eval mostró una mejora de 3 puntos" ha tomado una decisión ligada a esa eval concreta. Si cambias el juez y vuelves a ejecutar la versión 2.0 de la eval, una mejora de 2 puntos no es comparable: el equipo se apoyó en el número de la versión 1.0, no en el de la 2.0.

Cuando necesites cambiar una suite de evals:

**Opción 1: Ejecuta lo antiguo y lo nuevo en paralelo.** Antes de hacer el cambio, mide una muestra razonable de cambios recientes de modelo contra el juez/la métrica/la versión antiguos y contra los nuevos. Esto da a los demás equipos un factor de conversión y les muestra el impacto. Un informe que diga "cambiar de juez modifica la puntuación unos 2 puntos en promedio en estos modelos" es honesto y accionable; cambiar en silencio es un cambio que rompe.

**Opción 2: Versiona la eval de manera formal.** Si lanzas la versión 2.0 de la eval con un juez, una métrica o un umbral distintos, versiónala con claridad. Los demás equipos pueden seguir ejecutando la 1.0 hasta que estén listos para migrar. Documenta qué cambió y por qué. Así lo hacen las herramientas estables.

**Opción 3: No cambies aquello de lo que otros dependen sin comunicarlo.** Si un cambio es necesario (el juez antiguo está demostrablemente roto, una métrica ya no es adecuada), anúncialo. Da tiempo a los equipos para volver a evaluar sus últimas decisiones de lanzamiento bajo ambas versiones. Un cambio por sorpresa en lo que significa una eval es como se pierde por completo la confianza en las evals.

## Práctica

1. ▢ Un equipo reporta que un modelo mejoró 6 puntos en su eval, con un juez LLM que puntúa comparaciones pareadas. El informe no menciona cuántos ejemplos tiene la eval ni si el juez se contrastó con el acuerdo humano. ¿Qué deberías preguntar?

<details markdown="1"><summary>Comprobación</summary>

¿Con qué tamaño de conjunto de eval? El error estándar en un conjunto de 100 ejemplos con una línea base típica es de 4 a 5 puntos; una brecha de 6 puntos puede ser real o puede ser ruido. ¿Han medido el acuerdo del juez con evaluadores humanos sobre una muestra de vuestra tarea? Sin conocer el acuerdo entre humanos, no puedes saber si un acuerdo del 80% entre juez y humano es bueno o mediocre. Y además: ¿se comprobó en el juez el sesgo de posición (orden intercambiado) y el sesgo de verbosidad? Sin esas comprobaciones, la mejora podría ser un artefacto de cómo se le dio el prompt al juez.

</details>

2. ▢ Un equipo dice "usamos un juez LLM porque Zheng et al. mostraron que los jueces funcionan". Pero no han medido el acuerdo humano en su propia tarea, y usan puntuación puntual (escala de 1 a 10), no pareada. ¿Se aplica directamente el hallazgo de Zheng a su situación?

<details markdown="1"><summary>Comprobación</summary>

No directamente. Los hallazgos de Zheng se sostuvieron para comparaciones de preferencia pareadas en tareas abiertas donde los propios evaluadores humanos tenían un 80% de acuerdo. La puntuación puntual es un modo distinto (más propenso a problemas de interpretación de la escala), y sin medir el acuerdo humano en esta tarea concreta, no sabes qué línea base esperar del juez. El equipo debería medir el acuerdo humano en su tarea y comparar el juez con él, o pasarse a una métrica específica de la tarea si la tarea lo permite.

</details>

3. ▢ Tu suite de evals lleva seis meses ejecutándose y otros equipos condicionan sus lanzamientos a ella. Quieres cambiar a un juez distinto y mejor calibrado porque el actual tiene compresión de las puntuaciones. ¿Qué deberías hacer antes de hacer el cambio?

<details markdown="1"><summary>Comprobación</summary>

Ejecutar el juez antiguo y el nuevo en paralelo sobre una muestra de cambios recientes de modelo. Mostrar a los demás equipos qué le hace el cambio de juez a las puntuaciones en las que se han apoyado. Si es un desplazamiento de 2 puntos en promedio, pueden recalibrar; si es un desplazamiento de 10 puntos, necesitan reevaluar decisiones recientes. Anunciar el cambio con claridad y considerar versionar la eval (la eval 1.0 con el juez antiguo, la eval 2.0 con el nuevo) para que los demás equipos puedan migrar a su propio ritmo en lugar de verse sorprendidos por un cambio que rompe.

</details>

4. ▢ Un ingeniero que revisa un informe de eval dice: "El informe afirma una mejora de 4 puntos sin ninguna prueba de significancia reportada. El conjunto de eval tiene 50 ejemplos y la línea base es del 68%. ¿Deberíamos fiarnos de este número?" ¿Cuál es tu análisis?

<details markdown="1"><summary>Comprobación</summary>

No sin más información. Con N=50 y p=0.68, el error estándar es aproximadamente `sqrt(0.68 × 0.32 / 50) ≈ 0.066`, o unos 6.6 puntos porcentuales. Una brecha de 4 puntos cae bien dentro del ruido; no es claramente mayor que lo que el muestreo por sí solo podría producir. El equipo debería ejecutar más ejemplos (reduciendo el error estándar) o ejecutar una prueba de significancia pareada sobre los ejemplos concretos en que discrepan, y no limitarse a reportar la diferencia cruda y esperar que parezca convincente.

</details>

5. ▢ ¿Qué situación te haría desconfiar más de un informe de eval que afirma una mejora?

    - a) La eval usa una métrica específica de la tarea, ejecutó 500 ejemplos y reporta una mejora de 3 puntos con una prueba de significancia pareada que muestra p < 0.05
    - b) La eval usa un juez LLM, ejecutó 100 ejemplos, reporta una mejora de 4 puntos, pero no menciona si se comprobó el sesgo de posición del juez ni si se midió el acuerdo humano
    - c) La eval reporta una posición en la clasificación de MMLU como la evidencia principal de mejora
    - d) La eval incluyó el costo y la latencia junto con la calidad en la decisión de go/no-go

<details markdown="1"><summary>Comprobación</summary>

**c)** es la que más escepticismo despierta. Una posición en la tabla de clasificación de MMLU como prueba principal mide lo que no es: no es una señal de go/no-go específica de la tarea, y un benchmark público estático puede estar contaminado o saturado, así que ningún rigor alrededor del número lo convierte en prueba de este cambio. (b) también es una señal de alerta, pero menor: el juez puede estar puntuando la tarea correcta, y la comprobación de sesgo de posición y la medición del acuerdo humano que faltan todavía se pueden hacer para saber si es fiable. (a) acierta en todo: una métrica específica de la tarea, una muestra grande, una prueba de significancia. (d) es una buena práctica, no un motivo de escepticismo.

</details>

## Prácticas en el mundo real

- [ ] Busca un informe de eval de tu propio trabajo o del de un colega. Aplícale la lista de revisión de esta lección. Anota qué puntos de la lista aborda el informe con claridad y cuáles deja en silencio. Comparte la lista con el autor del informe.
- [ ] Sobre la pregunta "¿puede un juez LLM sustituir a una eval específica de la tarea?", vuelve a leer tú mismo el paper de Zheng et al. e identifica las condiciones concretas bajo las que se sostuvieron sus hallazgos. Anota: ¿qué características de las tareas, tamaños de muestra y prácticas de medición usaron? ¿Cómo comprobarías si esas condiciones se aplican a una situación nueva?
- [ ] Mañana: propón un cambio a una suite de evals que mantengas o conozcas. Escribe cómo comunicarías ese cambio a los demás equipos que condicionan sus lanzamientos a ella, y si ejecutarías lo antiguo y lo nuevo en paralelo, versionarías de manera formal, o ambas cosas.

## Para profundizar

- [Paper: "Judging LLM-as-a-Judge with MT-Bench and Chatbot Arena", Zheng et al., 2023](https://arxiv.org/abs/2306.05685)
- [Lección 6: Sesgo del juez y acuerdo con humanos](0006-judge-bias-and-human-agreement.md), para los sesgos que comprobar
- [Lección 10: Defender la decisión de go/no-go](0010-defending-the-go-no-go-call.md), para lo que tiene que citar una defensa completa
- [Lección 18: Benchmarks públicos](0018-public-benchmarks.md), para saber por qué una posición en una tabla de clasificación no sustituye a una decisión específica de la tarea
- [Recursos](../RESOURCES.md)

---

¿No termina de quedar claro? Vuelve a leer la fuente primaria de arriba, ya que esta lección la comprime y en la compresión es donde se escapa la comprensión. Consulta el [glosario](../GLOSSARY.md) por si algún término te resultó resbaladizo.

Si lo poco claro es la propia lección y no el material, eso es un defecto: [abre un issue](https://github.com/TokenCemetery/teach/issues).
