---
title: "20. Leer una curva de loss"
description: "La curva de loss de entrenamiento por sí sola subestima los problemas; otras dos señales detectan lo que se le escapa, y lo detectan antes"
type: lesson
---

# Lección 20. Leer una curva de loss

**Vínculo con la misión:** "Puedes leer un dashboard de entrenamiento y decir si la ejecución va bien encaminada" es el punto de Cómo se ve el éxito al que sirve esta etapa. Esta lección cubre qué vigilar realmente en un dashboard en vivo; la Lección 21 cubre cómo evaluar con datos held-out los checkpoints guardados.
**Fuente principal:** [Paper: "Scaling Language Models: Methods, Analysis & Insights from Training Gopher", Rae et al., 2021](https://arxiv.org/abs/2112.11446)
**Requisitos previos:** [Lección 19](0019-surviving-a-node-failure.md)

## Calentamiento

1. ▢ ¿Qué notaron Zhang et al. que se correlacionaba con la divergencia de la loss durante el entrenamiento de OPT-175B, además de la propia curva de loss?

<details markdown="1"><summary>Comprobación</summary>

Que su loss scalar dinámico (parte de la configuración de precisión mixta) se desplomaba a cero, y que la norma de las activaciones de la última capa se disparaba.

</details>

2. ▢ ¿Por qué recuperarse de una divergencia de la loss aboga por conservar más que solo el checkpoint más reciente?

<details markdown="1"><summary>Comprobación</summary>

Porque el mejor punto de reinicio se eligió según la salud del loss scalar y la tendencia de la norma de las activaciones, y no siempre era el checkpoint más reciente; conservar solo el más nuevo eliminaría la opción de retroceder más.

</details>

## Qué debes saber

### La curva de loss de entrenamiento, y qué significa "sana" para ella

Lo más básico que muestra un dashboard de entrenamiento es la propia loss de entrenamiento, representada frente al paso de entrenamiento o al número de tokens. Las leyes de escalado de la etapa 3 dan una expectativa real sobre su forma: la loss debería caer de forma suave, siguiendo aproximadamente una curva de tipo ley de potencias a medida que se acumulan cómputo y tokens, no en línea recta ni en una serie de saltos inconexos. Una curva que sigue esta forma general se comporta como se espera; una curva que se aplana mucho antes de lo que predeciría la trayectoria de la ley de escalado, o una que muestra una subida brusca repentina (un loss spike, Lección 16), es una curva de loss de entrenamiento que informa de algo que merece investigarse, antes de dar por supuesto que la ejecución va simplemente bien encaminada.

### Dos señales que detectan problemas antes de que la curva de loss los muestre con claridad

Vigilar solo la loss de entrenamiento no basta, porque cuando un spike es visible en la propia loss, el problema de fondo puede llevar ya un tiempo gestándose. El relato de Zhang et al. sobre OPT-175B da otras dos señales que avisaron antes del mismo problema que la curva de loss acabó mostrando: su **loss scalar dinámico**, parte de la configuración de precisión mixta, que se desplomaba hacia cero, y la **norma de las activaciones de la última capa**, que se disparaba hacia arriba. Ambas son síntomas de una ejecución de entrenamiento que se encamina hacia la inestabilidad, visibles antes de que la propia loss diverja con claridad, o a la vez que ella, que es exactamente por lo que Zhang et al. las usaron, y no solo la curva de loss, para juzgar si un punto dado del entrenamiento era seguro para reiniciar desde él.

### La norma del gradiente, vigilada a lo largo del tiempo

La Lección 16 cubrió el clipping por norma del gradiente como una salvaguarda por paso, que acota cuánto puede crecer cualquier actualización individual. La misma norma del gradiente, vigilada como una curva a lo largo del entrenamiento y no solo comprobada en cada paso frente al umbral de clipping, es en sí misma una señal útil: una norma del gradiente que tiende a subir con el tiempo, o que se dispara repetidamente incluso tras el clipping, puede ser una señal temprana del mismo tipo de inestabilidad que un loss spike acabaría mostrando de forma más dramática, y da la oportunidad de intervenir, por ejemplo bajando el learning rate, antes de que una divergencia completa obligue a reiniciar.

### Vigilar, de forma continua

Ninguna de estas señales ayuda si nadie, o nada automatizado, las está mirando realmente. La etapa 8 estableció que las fallas y las inestabilidades son una parte rutinaria y frecuente de una ejecución de entrenamiento grande, no un suceso raro; un dashboard que muestre la loss, la norma del gradiente y una señal de estabilidad numérica como un loss scalar solo es útil si se revisa con la frecuencia suficiente, o avisa de forma automática con la rapidez suficiente, para detectar un problema en desarrollo antes de que cueste mucho más progreso de lo que habría costado detectarlo antes.

## Práctica

1. ▢ La curva de loss de entrenamiento de un equipo está bajando, pero de forma notablemente más lenta de lo que predecirían las relaciones de ley de escalado de la etapa 3 para su tamaño de modelo y su número de tokens hasta ahora. ¿Es necesariamente señal de un problema, o podría ser coherente con una ejecución sana?

<details markdown="1"><summary>Pista</summary>

Las leyes de escalado son ajustes empíricos con varianza real, no una garantía exacta para cada ejecución individual.

</details>

<details markdown="1"><summary>Comprobación</summary>

Merece investigarse en lugar de darse por bueno, pero no es automáticamente prueba de un problema; las leyes de escalado son tendencias ajustadas con varianza, no una garantía exacta por ejecución. Una brecha significativa y sostenida respecto de la trayectoria esperada es una razón legítima para revisar otras señales (la norma del gradiente, un loss scalar si se usa precisión mixta, o el propio pipeline de datos) en lugar de suponer que la curva por sí sola zanja la cuestión en un sentido u otro.

</details>

2. ▢ ¿Por qué un loss scalar que se desploma hacia cero, o una norma de activaciones que se dispara, podrían avisar antes de la inestabilidad que la propia curva de loss de entrenamiento?

<details markdown="1"><summary>Comprobación</summary>

Son síntomas del problema numérico de fondo en desarrollo, que pueden aparecer antes de que crezca lo bastante como para perturbar visiblemente la curva de loss. Cuando un spike es claramente visible en la propia loss, el problema puede llevar ya algún tiempo gestándose.

</details>

3. ▢ ¿Cuál de estas opciones describe mejor por qué un dashboard que sigue la loss, la norma del gradiente y una señal de estabilidad como un loss scalar solo es útil en la práctica si se monitoriza con frecuencia?

    - a) Estas métricas solo tienen sentido una vez por ejecución de entrenamiento, al final del todo
    - b) Las fallas y las inestabilidades son sucesos frecuentes y rutinarios a escala (etapa 8), así que un problema detectado tarde cuesta mucho más progreso perdido que el mismo problema detectado pronto
    - c) Las propias métricas cambian de significado si se revisan con demasiada frecuencia
    - d) La monitorización frecuente solo sirve para modelos muy pequeños

<details markdown="1"><summary>Comprobación</summary>

**b)** es el razonamiento real: dada la frecuencia con que ocurren las fallas y las inestabilidades a escala, el valor de un dashboard está directamente ligado a la rapidez con que se nota un problema en desarrollo. (a), (c) y (d) no reflejan nada de lo que establecieron esta lección o la etapa 8.

</details>

## Prácticas en el mundo real

- [ ] Busca el dashboard de un framework de entrenamiento o de una herramienta de seguimiento de experimentos (Weights & Biases, TensorBoard o similar) e identifica cuáles de las señales de esta lección (loss, norma del gradiente, un indicador de estabilidad numérica) muestra por defecto, y cuáles habría que añadir de forma explícita.
- [ ] Lee el párrafo del paper de OPT (enlazado arriba) que conecta la divergencia de la loss con el loss scalar y la norma de las activaciones, y escribe una oración sobre qué señal revisarías primero si vieras un loss spike en un dashboard con las tres disponibles.
- [ ] Mañana: sin adelantarte, escribe una predicción de una oración para la Lección 21: si la loss de entrenamiento por sí sola no te dice qué tan bien rinde un modelo en las tareas para las que la gente lo va a usar realmente, ¿qué habría que medir de otra manera para comprobarlo durante el entrenamiento, y no solo después de que termine?

## Para profundizar

- [Paper: "Scaling Language Models: Methods, Analysis & Insights from Training Gopher", Rae et al., 2021](https://arxiv.org/abs/2112.11446)
- [Paper: "OPT: Open Pre-trained Transformer Language Models", Zhang et al., 2022](https://arxiv.org/abs/2205.01068)
- [Recursos](../RESOURCES.md)

---

¿No termina de quedar claro? Vuelve a leer la fuente primaria de arriba, ya que esta lección la comprime y en la compresión es donde se escapa la comprensión. Consulta el [glosario](../GLOSSARY.md) por si algún término te resultó resbaladizo.

Si lo poco claro es la propia lección y no el material, eso es un defecto: [abre un issue](https://github.com/TokenCemetery/teach/issues).
