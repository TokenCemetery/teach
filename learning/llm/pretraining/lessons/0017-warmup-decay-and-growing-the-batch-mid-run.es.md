---
title: "17. Warmup, decay y aumentar el batch a mitad de la ejecución"
description: "Empezar despacio, decaer según un programa y dejar que el propio batch size cambie a mitad del entrenamiento"
type: lesson
---

# Lección 17. Warmup, decay y aumentar el batch a mitad de la ejecución

**Vínculo con la misión:** "Dada una curva de loss, puedes decir si un spike es recuperable o exige reiniciar desde un checkpoint anterior" es la celda "Terminada cuando" de esta etapa en El arco. La Lección 16 cubrió los spikes y el clipping que protege contra ellos; esta lección cubre el programa que da forma a la ejecución en torno a esa protección.
**Fuente principal:** [Paper: "Scaling Language Models: Methods, Analysis & Insights from Training Gopher", Rae et al., 2021](https://arxiv.org/abs/2112.11446)
**Requisitos previos:** [Lección 16](0016-loss-spikes-and-the-optimizers-own-instabilities.md)

## Calentamiento

1. ▢ ¿Qué hace el clipping por norma global del gradiente con un gradiente cuya norma supera el umbral de clipping, y por qué redujeron Rae et al. el umbral específicamente para sus dos modelos más grandes?

<details markdown="1"><summary>Comprobación</summary>

Reescala todo el gradiente de forma proporcional para que su norma sea igual al umbral, lo que acota cuánto puede crecer una sola actualización. Rae et al. redujeron el umbral de 1 a 0.25 específicamente para el modelo de 7.1B y Gopher (280B), para mejorar la estabilidad a esa escala.

</details>

2. ▢ ¿Por qué bajar el learning rate no logró estabilizar la ejecución de Adafactor de 7.1B de Rae et al., y qué indicó ese fracaso?

<details markdown="1"><summary>Comprobación</summary>

La ejecución con Adafactor ya usaba un learning rate más bajo que la línea base estable con Adam y aun así mostró inestabilidades, lo que indicó que la inestabilidad venía del propio optimizador a esa escala, y no simplemente de un learning rate demasiado alto.

</details>

## Qué debes saber

### Empezar despacio a propósito

Rae et al. no empiezan el entrenamiento con el learning rate máximo que usa su programa. En su lugar, suben el learning rate de forma gradual desde `10^-7` hasta el valor máximo durante los primeros 1,500 pasos, antes de dejar que siga el resto del programa. Las primeras actualizaciones de una red recién inicializada son las menos informadas de toda la ejecución: los pesos no han visto ningún dato todavía, así que una actualización calculada a partir de ellos tiene más probabilidades de ser una corrección inútil y desmesurada que una actualización posterior, calculada cuando la red ya se ajusta razonablemente a los datos. Empezar con el learning rate cerca de cero y subirlo da a esas primeras actualizaciones, las menos fiables, un efecto menor sobre los pesos, en lugar de dejar que muevan el modelo tan fuerte como lo haría una actualización con el warmup ya completado.

### Decaer después

Una vez termina el warmup, Rae et al. hacen decaer el learning rate en un factor de 10 durante el resto del entrenamiento, siguiendo un programa de coseno: una curva suave que parte del learning rate máximo y desciende hacia el valor final con la forma de un cuarto de onda de coseno, en lugar de caer en escalones bruscos. Es una decisión separada del warmup, dirigida a un punto distinto del entrenamiento: mientras el warmup protege el comienzo mismo de la ejecución, el decay consiste en dar pasos más pequeños y cuidadosos a medida que avanza el entrenamiento y el paisaje de la loss cerca de una buena solución suele pedir ajustes más finos que los pasos grandes útiles al principio.

### Modelos más grandes, learning rates máximos más bajos

Rae et al. enuncian esta relación con claridad: al aumentar el tamaño del modelo, reducen el learning rate máximo hasta el que sube el programa y desde el que decae. Un learning rate perfectamente razonable para un modelo pequeño no es automáticamente seguro para uno mucho mayor; elegir un learning rate máximo por modelo, en lugar de reutilizar un único valor fijo en todos los tamaños entrenados, es parte de lo que mantiene las ejecuciones más grandes dentro del rango que el clipping de la Lección 16 y el warmup de esta lección pretenden proteger.

### El propio batch size puede cambiar a mitad de la ejecución

Junto con el programa del learning rate, Rae et al. describen una palanca adicional: aumentar el batch size durante el propio entrenamiento. El batch size de Gopher creció de tres millones a seis millones de tokens por batch a lo largo de su ejecución de entrenamiento, y no se mantuvo fijo del primer paso al último. Un batch mayor da una estimación del gradiente menos ruidosa y más fiable en cada paso, y un mejor aprovechamiento del hardware, pero empezar toda una ejecución de inmediato con el batch size más grande no es necesariamente obligatorio para obtener esos beneficios en todo momento; crecer hacia él a mitad del camino es una decisión de programa por derecho propio, junto con el warmup y el decay del learning rate, y no algo que tenga que fijarse para toda la ejecución desde el principio.

## Práctica

1. ▢ ¿Por qué podría ser más arriesgado empezar el entrenamiento de inmediato con el learning rate máximo, sin warmup, que subirlo de forma gradual, dado cómo son las primeras actualizaciones de una red recién inicializada?

<details markdown="1"><summary>Comprobación</summary>

Las primeras actualizaciones de la red, calculadas antes de que haya visto ningún dato, son las menos informadas de toda la ejecución y tienen más probabilidades de ser correcciones desmesuradas e inútiles. Un learning rate de fuerza completa aplicado a una actualización así podría mover los pesos con fuerza en una mala dirección; el warmup limita cuánto efecto pueden tener esas primeras actualizaciones, las menos fiables.

</details>

2. ▢ ¿Cuál es la diferencia práctica entre contra qué protege el warmup y a qué apunta el decay de coseno?

<details markdown="1"><summary>Comprobación</summary>

El warmup protege el comienzo mismo del entrenamiento, cuando las actualizaciones de la red son las menos informadas. El decay de coseno trata del entrenamiento posterior, dando gradualmente pasos más pequeños porque el paisaje de la loss cerca de una buena solución suele pedir ajustes más finos que los pasos mayores útiles antes. Abordan puntos distintos de la misma ejecución, no el mismo problema dos veces.

</details>

3. ▢ Según Rae et al., ¿recibe un modelo más grande un learning rate máximo más alto o más bajo que uno más pequeño, a igualdad de lo demás?

<details markdown="1"><summary>Comprobación</summary>

Un learning rate máximo más bajo. Rae et al. enuncian directamente que al aumentar el tamaño del modelo reducen el learning rate máximo que usa el programa.

</details>

4. ▢ El batch size de Gopher creció de tres millones a seis millones de tokens por batch a lo largo del entrenamiento, en lugar de empezar en seis millones desde el primer paso. Nombra una razón plausible para crecer hacia el batch size mayor en lugar de empezar en él de inmediato.

<details markdown="1"><summary>Comprobación</summary>

Cualquier explicación razonable es aceptable, como: al principio del entrenamiento, cuando las actualizaciones ya son menos estables (según el razonamiento del warmup), añadir encima un batch muy grande puede no ser necesario para obtener una estimación útil del gradiente, y crecer el batch size más tarde aprovecha los beneficios del batch mayor (un gradiente menos ruidoso, mejor aprovechamiento del hardware) una vez que el entrenamiento ya ha llegado a una región más estable.

</details>

## Prácticas en el mundo real

- [ ] Busca la documentación de las opciones de planificador de learning rate de un framework de entrenamiento, e identifica si expone una fase de warmup, una fase de decay de coseno o ambas, y cómo se configura cada una.
- [ ] Esboza en papel una curva aproximada de learning rate frente a paso de entrenamiento que combine el warmup (una rampa corta desde casi cero) seguido de un decay de coseno (una curva suave hasta un valor final mucho menor), señalando aproximadamente dónde se situaría el warmup de 1,500 pasos que describen Rae et al. respecto a una ejecución de, digamos, 300,000 pasos en total.
- [ ] Mañana: para un tamaño de modelo que elijas (pequeño, mediano o grande, en tus propios términos), decide de forma cualitativa si esperarías que su learning rate máximo estuviera más cerca del de Gopher o del de un modelo mucho más pequeño, y escribe una oración sobre por qué, a partir de la relación con el tamaño del modelo de esta lección.

## Para profundizar

- [Paper: "Scaling Language Models: Methods, Analysis & Insights from Training Gopher", Rae et al., 2021](https://arxiv.org/abs/2112.11446)
- [Recursos](../RESOURCES.md)

---

La etapa 7 cubrió la numérica y el programa que mantienen estable una sola ejecución de entrenamiento. La etapa 8 se vuelve hacia lo que ocurre a lo largo de los muchos días que realmente dura una ejecución así: cómo sobrevive el progreso a que se guarde, se reanude y se interrumpa por una falla a mitad de camino.

¿No termina de quedar claro? Vuelve a leer la fuente primaria de arriba, ya que esta lección la comprime y en la compresión es donde se escapa la comprensión. Consulta el [glosario](../GLOSSARY.md) por si algún término te resultó resbaladizo.

Si lo poco claro es la propia lección y no el material, eso es un defecto: [abre un issue](https://github.com/TokenCemetery/teach/issues).
