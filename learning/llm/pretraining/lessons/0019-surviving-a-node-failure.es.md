---
title: "19. Sobrevivir a la falla de un nodo"
description: "Pausar, diagnosticar, aislar lo que está roto y reanudar desde el último checkpoint, al costo que sea"
type: lesson
---

# Lección 19. Sobrevivir a la falla de un nodo

**Vínculo con la misión:** "Puedes diseñar un esquema de checkpointing que acote el progreso perdido tras la falla de un nodo" es la celda "Terminada cuando" de esta etapa en El arco. La Lección 18 cubrió qué tiene que guardar un checkpoint y cada cuánto guardar uno; esta lección cubre qué ocurre realmente cuando llega una falla.
**Fuente principal:** [Paper: "OPT: Open Pre-trained Transformer Language Models", Zhang et al., 2022](https://arxiv.org/abs/2205.01068)
**Requisitos previos:** [Lección 18](0018-what-a-checkpoint-has-to-hold.md)

## Calentamiento

1. ▢ Nombra las cuatro cosas que necesita guardar un checkpoint para reanudar una ejecución correctamente, y no solo de forma aproximada.

<details markdown="1"><summary>Comprobación</summary>

Los parámetros del modelo, el estado del optimizador, el número de paso y la posición en el programa del learning rate y, para una reproducibilidad exacta, la posición del data loader y el estado del generador de números aleatorios.

</details>

2. ▢ A lo largo de unos dos meses de entrenamiento de OPT-175B, ¿qué informaron Zhang et al. sobre con qué frecuencia ocurrían las fallas de hardware?

<details markdown="1"><summary>Comprobación</summary>

Al menos 35 reinicios manuales y la rotación de más de 100 hosts, además de una estimación de más de 70 reinicios automáticos adicionales, bastante más de un reinicio cada dos días sostenido durante toda la ejecución.

</details>

## Qué debes saber

### El procedimiento que siguió realmente OPT

Zhang et al. describen una secuencia concreta y repetible, y no una carrera improvisada cada vez que llegaba una falla: cuando se sospechaba un problema de hardware, la ejecución de entrenamiento se **pausaba**; se corría una serie de **pruebas de diagnóstico** para identificar qué nodos concretos se comportaban mal; cualquier nodo que señalaran los diagnósticos se **aislaba**, es decir, se excluía del conjunto de nodos que usaría la ejecución en adelante; y el entrenamiento **se reanudaba entonces desde el último checkpoint guardado**, ya sobre los nodos restantes y sanos. Es el mismo patrón tanto si una falla se detectó de forma manual como si disparó un reinicio automático: diagnosticar, excluir el hardware defectuoso, reanudar desde el estado guardado más reciente.

### Reinicios manuales frente a automáticos, y por qué importa operativamente la diferencia

Zhang et al. distinguen más de 35 reinicios **manuales**, en los que una persona reconoció un problema e intervino, de una estimación de más de 70 reinicios **automáticos**, inferida a partir de la diferencia entre el número de hosts rotados y el número menor de reinicios manuales registrados. Un reinicio automático implica herramientas que detectan una falla y reanudan el entrenamiento sin esperar a que una persona lo note y actúe, lo cual importa directamente para cuánto progreso cuesta realmente una falla: una falla que espera a la detección manual pierde todo el tiempo que pasa antes de que una persona intervenga, además de lo que cueste en sí el ciclo de checkpoint y reanudación, mientras que una falla detectada y reanudada de forma automática pierde algo más cercano al progreso de un intervalo de checkpoint que discutió la Lección 18.

### La divergencia de la loss como una falla relacionada pero distinta de la que recuperarse

Zhang et al. describen también reiniciar por una razón completamente distinta: la divergencia de la loss, no una falla de hardware. Cuando la loss de entrenamiento divergía, bajar el learning rate y reiniciar desde un checkpoint anterior permitía que la ejecución se recuperara y continuara. Notaron que esto se correlacionaba con otras dos señales: que su loss scalar dinámico (parte de la configuración de precisión mixta) se desplomaba a cero, y que la norma de las activaciones de la última capa se disparaba. En lugar de reiniciar desde justo antes de la divergencia, eligieron puntos de reinicio en los que el loss scalar seguía en un estado sano y las normas de las activaciones tendían a bajar en lugar de crecer sin límite, y encontraron aparte que bajar el gradient clipping de 1.0 a 0.3 ayudaba. Esta es una segunda razón, genuinamente distinta, por la que se usa un checkpoint para reanudar una ejecución, distinta de que muera un nodo: el hardware está bien, pero el propio proceso de entrenamiento necesita retroceder y continuar de otra manera, lo que solo hace posible un historial conservado de checkpoints (y no solo el más reciente).

## Práctica

1. ▢ Pon en el orden que describen Zhang et al. estos cuatro pasos del procedimiento de OPT ante la falla de un nodo: (a) reanudar el entrenamiento en los nodos restantes, (b) pausar la ejecución de entrenamiento, (c) correr pruebas de diagnóstico para identificar los nodos defectuosos, (d) aislar los nodos señalados.

<details markdown="1"><summary>Comprobación</summary>

b, c, d, a: pausar, diagnosticar, aislar lo que señalaron los diagnósticos y luego reanudar desde el último checkpoint guardado en los nodos sanos restantes.

</details>

2. ▢ ¿Por qué una falla detectada y reanudada de forma automática suele costar menos progreso que una detectada de forma manual, aunque ambas acaben reanudando desde el mismo checkpoint?

<details markdown="1"><summary>Comprobación</summary>

Un reinicio manual pierde todo el tiempo que pasa antes de que una persona note el problema e intervenga, además del ciclo de checkpoint y reanudación en sí. Un reinicio automático se salta ese retraso de detección, así que el costo total se acerca más al progreso de un intervalo de checkpoint.

</details>

3. ▢ La loss de entrenamiento de un equipo diverge, pero no hay ninguna falla de hardware: todos los nodos están sanos. Según el relato de Zhang et al., ¿sigue siendo útil un checkpoint aquí, y de ser así, cómo?

    - a) No; los checkpoints solo ayudan con las fallas de hardware, no con la divergencia de la loss
    - b) Sí; reiniciar desde un checkpoint anterior, junto con bajar el learning rate, es exactamente como se recuperaron Zhang et al. de la divergencia de la loss
    - c) Sí, pero solo se puede usar el checkpoint más reciente, sin importar cuándo empezó la divergencia
    - d) No; la divergencia de la loss exige reentrenar el modelo desde cero

<details markdown="1"><summary>Pista</summary>

Zhang et al. eligieron los puntos de reinicio específicamente según el estado de su loss scalar y de las normas de las activaciones, y no simplemente el checkpoint más reciente disponible.

</details>

<details markdown="1"><summary>Comprobación</summary>

**b)** es exactamente lo que describen Zhang et al. (a) es falsa; el mismo mecanismo de checkpoint y reanudación se recupera de cualquiera de las dos causas. (c) es incorrecta precisamente porque eligieron un punto de reinicio según cuándo el loss scalar estaba sano y las normas de las activaciones tendían a bajar, que puede no ser el checkpoint más reciente, lo que aboga por tener a mano más de un checkpoint reciente. (d) contradice el propio relato del paper de recuperarse sin un reinicio completo.

</details>

4. ▢ ¿Por qué recuperarse de una divergencia de la loss, como la describen Zhang et al., aboga por conservar más que solo el checkpoint más reciente?

<details markdown="1"><summary>Comprobación</summary>

Porque el mejor punto de reinicio no siempre era el checkpoint más reciente; era uno elegido según la salud del loss scalar y la dirección en que tendían las normas de las activaciones, que podía estar más atrás que el último guardado. Conservar solo el checkpoint más nuevo eliminaría la opción de retroceder a un punto anterior y más estable.

</details>

## Prácticas en el mundo real

- [ ] Busca dónde expone la detección y el reinicio automáticos de fallas un framework de entrenamiento o una herramienta de orquestación a la que tengas acceso (health checks, drenado de nodos o términos similares son habituales). Anota si coincide con el patrón de pausar, diagnosticar, aislar y reanudar que describe esta lección.
- [ ] Lee el párrafo "Loss Divergences" del paper de OPT (enlazado arriba) y escribe una oración sobre qué señal, además de la propia curva de loss, usaron los autores para juzgar si era seguro reanudar desde un punto de reinicio.
- [ ] Mañana: para la frecuencia de checkpoints que elegiste en la práctica en el mundo real de la Lección 18, decide cuántos checkpoints recientes tendrías a mano en lugar de solo el último, y escribe una oración sobre por qué, dado el caso de recuperación de una divergencia de la loss de esta lección.

## Para profundizar

- [Paper: "OPT: Open Pre-trained Transformer Language Models", Zhang et al., 2022](https://arxiv.org/abs/2205.01068)
- [Recursos](../RESOURCES.md)

---

La etapa 8 cubrió sobrevivir a una falla dentro de una sola ejecución de entrenamiento. La etapa 9 se vuelve hacia una pregunta de más largo plazo: vigilar el progreso de esa ejecución para empezar, y saber si va bien encaminada en absoluto.

¿No termina de quedar claro? Vuelve a leer la fuente primaria de arriba, ya que esta lección la comprime y en la compresión es donde se escapa la comprensión. Consulta el [glosario](../GLOSSARY.md) por si algún término te resultó resbaladizo.

Si lo poco claro es la propia lección y no el material, eso es un defecto: [abre un issue](https://github.com/TokenCemetery/teach/issues).
