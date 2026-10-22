---
title: "16. Loss spikes y las inestabilidades propias del optimizador"
description: "El mismo spike puede venir de un mal batch o del propio optimizador, y distinguirlos exige una comparación controlada"
type: lesson
---

# Lección 16. Loss spikes y las inestabilidades propias del optimizador

**Vínculo con la misión:** "Dada una curva de loss, puedes decir si un spike es recuperable o exige reiniciar desde un checkpoint anterior" es la celda "Terminada cuando" de esta etapa en El arco. Esta lección cubre de dónde puede venir realmente un loss spike, y la mitigación estándar; la Lección 17 cubre el programa que da forma al entrenamiento en torno a él.
**Fuente principal:** [Paper: "Scaling Language Models: Methods, Analysis & Insights from Training Gopher", Rae et al., 2021](https://arxiv.org/abs/2112.11446)
**Requisitos previos:** [Lección 15](0015-mixed-precision-at-scale-bfloat16-and-stochastic-rounding.md), [Loss spike](../GLOSSARY.md)

## Calentamiento

1. ▢ ¿Por qué el rango de exponente más amplio de bf16 lo hace más indulgente durante el entrenamiento que fp16, aunque bf16 tenga menos precisión?

<details markdown="1"><summary>Comprobación</summary>

bf16 conserva los 8 bits de exponente completos de fp32, lo que le da el mismo rango dinámico que fp32, así que es menos probable que los valores grandes o pequeños que aparecen en los gradientes y las activaciones a escala lo desborden por arriba o por abajo, aunque represente los valores con menos precisión dentro de ese rango que fp16.

</details>

2. ▢ ¿Qué limitación informaron Rae et al. incluso tras usar redondeo estocástico en las actualizaciones de parámetros en bf16?

<details markdown="1"><summary>Comprobación</summary>

El redondeo estocástico no recupera por completo el rendimiento del entrenamiento de precisión mixta corriente; es una mitigación, no una solución completa.

</details>

## Qué debes saber

### Un loss spike no anuncia su propia causa

Un **loss spike**, una subida repentina y brusca de la loss de entrenamiento a mitad de una ejecución, puede venir de más de un lugar: un único batch inusualmente difícil o mal formado, un problema de precisión numérica como los que describió la Lección 15, o algo del propio optimizador que se vuelve inestable a la escala a la que se entrena. Leer un spike en una curva de loss te dice que ocurrió; por sí solo no te dice cuál de estas causas lo provocó, y la respuesta correcta, un reinicio, un cambio de hiperparámetros o nada en absoluto, depende de saber cuál fue.

### Un caso concreto: Adafactor frente a Adam a escala

Rae et al. dan un ejemplo resuelto de exactamente este tipo de investigación. Adafactor es un optimizador que usa menos memoria que Adam, lo que importa directamente para el presupuesto de memoria que contó la Lección 8: una huella menor del estado del optimizador podría significar que quepa un modelo mayor, o que quepa el mismo modelo con menos reparto. A escalas menores, Rae et al. encontraron que el preentrenamiento con Adafactor era estable y de buen rendimiento. Con 7.1 mil millones de parámetros, eso dejó de cumplirse: observaron divergencias de la loss al entrenar con Adafactor que no habían visto con 1.4 mil millones de parámetros, aunque la ejecución con Adafactor usó un learning rate máximo más bajo (`6 × 10^-5`) que la línea base estable con Adam con la que se comparó (`1.2 × 10^-4`). Un learning rate más bajo es normalmente lo primero que se prueba contra la inestabilidad; aquí no bastó, y eso es lo que permitió a Rae et al. concluir que la inestabilidad venía del propio optimizador a esta escala, y no simplemente de un learning rate fijado demasiado alto.

### La mitigación estándar: clipping por la norma global del gradiente

Sea cual sea la causa de fondo de una inestabilidad, la mitigación más directa que usan Rae et al. es el **gradient clipping** por norma global: calcular la norma (la magnitud global) del vector de gradiente completo a lo largo de todos los parámetros del modelo y, si esa norma supera un umbral elegido, reescalar todo el gradiente a la baja de forma proporcional para que su norma sea exactamente el umbral, antes de que el paso del optimizador lo use. Esto acota cuánto puede crecer la actualización de un solo paso, sin importar qué produjo en primer lugar un gradiente inusualmente grande. Rae et al. usan un valor de clipping de 1 para la mayoría de sus modelos, pero lo reducen a 0.25 específicamente para los dos más grandes, el modelo de 7.1B y el propio Gopher, para mejorar la estabilidad, un ejemplo directo y concreto de endurecer esta salvaguarda al aumentar la escala en lugar de dejarla fija.

## Práctica

1. ▢ Un equipo observa un loss spike a mitad de una ejecución de entrenamiento. Nombra dos causas de fondo distintas que describe esta lección y que podrían producir el mismo spike visible.

<details markdown="1"><summary>Comprobación</summary>

Dos cualesquiera de estas: un único batch inusualmente difícil o mal formado, un problema de precisión numérica (como un desbordamiento o un problema de redondeo en el entrenamiento con bf16), o una inestabilidad que viene del propio optimizador al volverse inestable a la escala a la que se entrena.

</details>

2. ▢ ¿Por qué bajar el learning rate no logró estabilizar la ejecución de Adafactor de 7.1B, y qué concluyeron Rae et al. de ese fracaso?

<details markdown="1"><summary>Pista</summary>

La ejecución con Adafactor ya usaba un learning rate más bajo que la línea base estable con Adam con la que se comparó.

</details>

<details markdown="1"><summary>Comprobación</summary>

La ejecución con Adafactor usó un learning rate máximo de `6 × 10^-5`, más bajo que el de `1.2 × 10^-4` de la línea base estable con Adam, y aun así mostró inestabilidades. Como un learning rate más bajo no lo arregló, Rae et al. concluyeron que la inestabilidad venía del propio optimizador a esta escala, y no simplemente de un learning rate demasiado alto.

</details>

3. ▢ ¿Qué hace realmente el clipping por norma global del gradiente con un gradiente cuya norma supera el umbral de clipping?

    - a) Descarta ese gradiente por completo y se salta el paso del optimizador para ese batch
    - b) Reescala el vector de gradiente completo de forma proporcional para que su norma sea igual al umbral
    - c) Redondea los valores del gradiente a un formato de menor precisión
    - d) Baja de forma permanente el learning rate durante el resto del entrenamiento

<details markdown="1"><summary>Comprobación</summary>

**b)** es exactamente el mecanismo: un reescalado proporcional para llevar la norma hasta el umbral, no un descarte, un cambio de precisión ni un cambio permanente del programa. (a), (c) y (d) describen cada una una intervención distinta y sin relación.

</details>

4. ▢ Rae et al. usan un valor de clipping de 1 para la mayoría de los tamaños de modelo, pero lo reducen a 0.25 específicamente para el modelo de 7.1B y Gopher (280B). ¿Qué ilustra esta elección concreta sobre cómo se fijan las salvaguardas de estabilidad?

<details markdown="1"><summary>Comprobación</summary>

Que una salvaguarda como el gradient clipping no es necesariamente una constante fija en todas las escalas; aquí se endureció específicamente para los modelos más grandes, donde el riesgo de inestabilidad era mayor, en lugar de dejarla en el mismo valor usado en ejecuciones más pequeñas y más estables.

</details>

## Prácticas en el mundo real

- [ ] Busca dónde se expone el gradient clipping como opción de configuración en un framework de entrenamiento al que tengas acceso, y anota su valor de clipping por defecto, si se fija alguno.
- [ ] Lee el párrafo del paper de Gopher (enlazado arriba) que describe la comparación entre Adafactor y Adam, y escribe una oración que enuncie qué evidencia, en concreto, descartó que "el learning rate fuera simplemente demasiado alto" como explicación.
- [ ] Mañana: sin adelantarte, escribe una predicción de una oración para la Lección 17: dado que Rae et al. suben el learning rate despacio al comienzo mismo del entrenamiento en lugar de empezar de inmediato en el valor máximo, ¿qué problema podría causar empezar con el learning rate completo desde una red recién inicializada y sin entrenar?

## Para profundizar

- [Paper: "Scaling Language Models: Methods, Analysis & Insights from Training Gopher", Rae et al., 2021](https://arxiv.org/abs/2112.11446)
- [Recursos](../RESOURCES.md)

---

¿No termina de quedar claro? Vuelve a leer la fuente primaria de arriba, ya que esta lección la comprime y en la compresión es donde se escapa la comprensión. Consulta el [glosario](../GLOSSARY.md) por si algún término te resultó resbaladizo.

Si lo poco claro es la propia lección y no el material, eso es un defecto: [abre un issue](https://github.com/TokenCemetery/teach/issues).
