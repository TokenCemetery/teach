---
title: "11. PagedAttention"
description: "El mecanismo de tabla de bloques detrás de vLLM, su compromiso de tamaño de bloque y cómo permite que las secuencias compartan la caché de un prefijo común"
type: lesson
---

# Lección 11. PagedAttention

**Vínculo con la misión:** El gestor de memoria de vLLM es el mecanismo que convierte el techo de capacidad de la lección 2 en un objetivo móvil y compartible en lugar de un costo fijo por secuencia, y esta lección es donde ese mecanismo se nombra por completo.
**Fuente principal:** [Paper: "Efficient Memory Management for Large Language Model Serving with PagedAttention", Kwon et al., SOSP 2023](https://arxiv.org/abs/2309.06180)
**Requisitos previos:** [Lección 10](0010-standing-up-vllm.md), [KV cache](../GLOSSARY.md)

## Calentamiento

1. ▢ ¿Qué dos tipos de fragmentación sufría una asignación de KV cache ingenua, contigua y dimensionada a la longitud máxima (lección 1)?

<details markdown="1"><summary>Comprobación</summary>

Fragmentación interna: una secuencia que termina corta sigue reteniendo memoria reservada para la longitud máxima que nunca usó. Fragmentación externa: huecos entre bloques reservados de tamaños distintos donde no cabe la caché de ninguna otra secuencia.

</details>

2. ▢ En una frase, ¿qué dijo la lección 1 que PagedAttention toma prestado de la memoria virtual de los sistemas operativos?

<details markdown="1"><summary>Comprobación</summary>

Dividir la caché en bloques de tamaño fijo, almacenados de forma no contigua, direccionados mediante una tabla por secuencia que asigna posiciones lógicas a bloques físicos, la misma idea que las tablas de páginas de un SO.

</details>

## Qué debes saber

### La tabla de bloques, un nivel más de detalle

La KV cache de cada secuencia se divide en **bloques** de tamaño fijo, cada uno con los keys y values de un número determinado de tokens. La **tabla de bloques** de una secuencia asigna sus posiciones lógicas de token a ubicaciones físicas de bloque en memoria, donde sea que estén. La atención de una secuencia dada busca sus bloques a través de esta tabla en lugar de asumir que son contiguos, y eso es lo que permite al gestor de memoria subyacente colocar bloques en cualquier sitio donde tenga espacio, exactamente igual que una tabla de páginas de un SO permite que las páginas de memoria de un proceso estén en cualquier parte de la RAM física.

### El tamaño de bloque es un compromiso, no un parámetro libre

Un tamaño de bloque mayor significa menos bloques por secuencia y menos contabilidad de tabla de bloques, pero más espacio desperdiciado en el último bloque, parcialmente lleno, de una secuencia cuya longitud no se divide exactamente (fragmentación interna, solo que a una escala mucho menor que la de la versión ingenua, de secuencia entera, de la lección 1). Un tamaño de bloque menor desperdicia menos espacio por secuencia pero significa más bloques, y más entradas de la tabla de bloques que seguir. El tamaño de bloque por defecto de vLLM (16 tokens) es un término medio elegido entre estos dos costos, no un número arbitrario.

### Compartir bloques entre secuencias

Como a los bloques de una secuencia se llega de forma indirecta, a través de su tabla de bloques, en lugar de asumir una disposición física fija, las tablas de bloques de dos secuencias distintas pueden apuntar al *mismo* bloque físico cuando su contenido es idéntico, lo más habitual un prefijo de prompt compartido. El muestreo paralelo (pedir varias completions del mismo prompt) o el beam search son los casos más claros: cada muestra comparte la caché de los mismos tokens del prompt, así que los bloques del prompt solo tienen que existir físicamente una vez, y la tabla de bloques de cada muestra apunta a ellos. Cuando la generación de una muestra diverge de las demás (cualquier token nuevo específico de la muestra), un **copy-on-write** crea la copia privada de esa muestra del bloque que se modifica, exactamente el mecanismo que usa un sistema operativo cuando dos procesos comparten páginas de memoria hasta que uno de ellos escribe.

![Dos tablas de bloques, la secuencia A a la izquierda y la secuencia B a la derecha, cada una asignando cuatro posiciones lógicas a números de bloque físico. Para las posiciones 0 a 2, ambas tablas apuntan a los mismos tres bloques físicos compartidos que contienen un prefijo de prompt idéntico, así que la caché de ese prefijo existe una sola vez en memoria. En la posición 3 las dos secuencias han generado tokens distintos, así que un copy-on-write ha dado a cada una su propio bloque privado: el bloque 9 de la secuencia A y el bloque 3 de la secuencia B, ninguno compartido con el otro.](images/block-table-sharing.svg)

## Práctica

1. ▢ Con un tamaño de bloque de 16 tokens, una secuencia genera 40 tokens de salida. ¿Cuántos bloques usa, y cuánto espacio se desperdicia en el último?

<details markdown="1"><summary>Pista</summary>

Divide 40 entre 16 y redondea hacia arriba a un número entero de bloques; el desperdicio es lo que queda sin usar en el último bloque, parcialmente lleno.

</details>

<details markdown="1"><summary>Comprobación</summary>

`40 / 16 = 2.5`, redondeado hacia arriba a 3 bloques. Los dos primeros contienen 32 tokens; el tercero contiene los 8 restantes y desperdicia los otros 8 huecos de ese bloque, fragmentación interna a la escala de un bloque en lugar de una secuencia entera.

</details>

2. ▢ ¿Por qué un tamaño de bloque menor reduce ese espacio desperdiciado, y qué cuesta a cambio?

<details markdown="1"><summary>Comprobación</summary>

Un tamaño de bloque menor significa que el último bloque, parcialmente lleno, tiene menos huecos sin usar que desperdiciar, ya que hay menos posiciones en cada bloque desde el principio. El costo es más bloques por secuencia en total, y por tanto más entradas de la tabla de bloques que el gestor de memoria tiene que seguir y consultar.

</details>

3. ▢ Se piden diez muestras paralelas del mismo prompt de 200 tokens, con un tamaño de bloque de 16 tokens. ¿Cuántos bloques físicos necesita la caché del prompt, con compartición de bloques y sin ella?

<details markdown="1"><summary>Pista</summary>

Calcula cuántos bloques necesita una copia del prompt de 200 tokens, y luego decide cuántas copias existen en cada caso.

</details>

<details markdown="1"><summary>Comprobación</summary>

`200 / 16 = 12.5`, redondeado hacia arriba a 13 bloques para una copia del prompt. Sin compartición, las 10 muestras retienen cada una su propia copia: `13 × 10 = 130` bloques. Con compartición, la tabla de bloques de cada muestra apunta a los mismos 13 bloques físicos del prompt compartido, así que solo hacen falta 13 bloques hasta que alguna muestra empiece a generar sus propios tokens divergentes.

</details>

4. ▢ Una de las diez muestras de la pregunta 3 genera un token distinto de lo que generó cualquier otra muestra en esa posición. ¿Qué pasa con la caché de esa muestra en ese punto?

<details markdown="1"><summary>Comprobación</summary>

Se dispara un copy-on-write: esa muestra obtiene su propia copia privada del bloque en el que se escribe, en lugar de modificar el bloque compartido al que sigue apuntando la tabla de todas las demás. Solo la muestra divergente paga un bloque nuevo; las otras nueve siguen compartiendo el original.

</details>

5. ▢ ¿Qué afirmación es verdadera de la elección del tamaño de bloque de vLLM?

    - a) Los bloques mayores siempre desperdician más memoria que los menores, sin ningún beneficio que lo compense
    - b) El tamaño de bloque intercambia fragmentación interna por sobrecarga de contabilidad de la tabla de bloques
    - c) El tamaño de bloque solo afecta a las cargas de muestreo paralelo, no al serving de una sola solicitud
    - d) Un tamaño de bloque menor siempre aumenta el uso total de memoria

<details markdown="1"><summary>Comprobación</summary>

**b)** Los bloques menores desperdician menos espacio en un último bloque parcialmente lleno pero exigen seguir más entradas de la tabla de bloques; los bloques mayores son lo contrario. (a) es falsa: los bloques mayores reducen la sobrecarga de contabilidad, que es un beneficio real. (c) es falsa: toda secuencia, compartida o no, se divide en bloques y paga el compromiso de fragmentación y contabilidad. (d) es falsa: los bloques menores reducen la fragmentación interna, lo que puede bajar el uso total de memoria, no siempre subirlo.

</details>

## Prácticas en el mundo real

- [ ] Encuentra en su documentación el parámetro u opción de configuración del tamaño de bloque de vLLM y lee cuál es su valor por defecto y qué dice la documentación sobre cambiarlo.
- [ ] Si puedes ejecutar un servidor, envía varias solicitudes de muestreo paralelo (`n` mayor que 1) del mismo prompt, y comprueba si la documentación o los logs reportan algo sobre compartición de prefijos o de bloques.
- [ ] Mañana: lee un párrafo sobre el prefix caching (reutilizar los bloques de un system prompt compartido entre solicitudes por lo demás no relacionadas) y anota cómo es la misma idea de compartir bloques aplicada entre solicitudes en lugar de dentro de una.

## Para profundizar

- [Paper: "Efficient Memory Management for Large Language Model Serving with PagedAttention", Kwon et al., SOSP 2023](https://arxiv.org/abs/2309.06180)
- [Docs: vLLM Documentation, vLLM Project](https://docs.vllm.ai/en/latest/)
- [Recursos](../RESOURCES.md)

---

¿No termina de quedar claro? Vuelve a leer la fuente primaria de arriba, ya que esta lección la comprime y en la compresión es donde se escapa la comprensión. Consulta el [glosario](../GLOSSARY.md) por si algún término te resultó resbaladizo.

Si lo poco claro es la propia lección y no el material, eso es un defecto: [abre un issue](https://github.com/TokenCemetery/teach/issues).
