---
title: "Glosario"
description: "Términos canónicos de la inferencia"
type: glossary
---

# Glosario de la inferencia

Términos canónicos para servir un modelo entrenado: qué guarda un servidor en memoria y qué palancas tiene sobre la latencia y el throughput.

## Términos

**Attention sink**:
La puntuación de atención desproporcionadamente alta que reciben los primeros tokens de una secuencia sin importar su contenido real, y por eso quitarlos de una caché de ventana deslizante provoca un colapso de calidad en lugar de una pérdida gradual del contexto antiguo. Mantener de forma permanente en la caché solo las entradas KV de esos tokens iniciales, junto con la ventana deslizante habitual, recupera la mayor parte del rendimiento de la atención completa (la técnica StreamingLLM).
_Evitar_: asumir que cualquier token antiguo descartado causa el mismo daño (solo los tokens iniciales "sink" tienen este peso desproporcionado; perder otros tokens antiguos fuera de la ventana degrada la calidad de forma gradual en lugar de colapsarla)

**Arranque en frío (serving)**:
El intervalo entre que un autoscaler decide añadir una réplica y que esa réplica puede atender de verdad una solicitud, dominado por el tiempo que tarda en cargarse en memoria el checkpoint de un modelo grande, que puede ser de decenas de segundos y supera con creces el tiempo de generar un solo token.
_Evitar_: tratarlo como un problema de colas de solicitudes (un scheduler o un router no tienen efecto sobre él; lo fijan por completo el tamaño del checkpoint y la ruta de almacenamiento que debe recorrer)

**Decodificación restringida (guiada)**:
Enmascarar todo token que violaría una estructura exigida (JSON válido, una gramática) antes de que ocurra el muestreo, de modo que la estructura de la salida quede garantizada por construcción y no meramente fomentada. Se mantiene barata por token replanteando la gramática como una máquina de estados finitos y precalculando, una sola vez, un índice de qué tokens son válidos desde cada estado.
_Evitar_: comprobar la validez de la salida cuando la generación ya terminó (no garantiza nada, porque el modelo siempre pudo muestrear un token inválido; enmascarar antes de muestrear es lo que vuelve estructural la garantía)

**Costo por millón de tokens**:
El costo horario de alquilar una GPU dividido por su throughput medido (tokens/s, convertido a tokens/hora), escalado a un millón de tokens. Se deriva del mismo throughput medido que produce el compromiso del tamaño de lote de la lección 6, no de un precio por token anunciado por un proveedor y medido con el tamaño de lote de otra carga de trabajo.
_Evitar_: un precio por token fijo citado por un proveedor (el throughput, y por tanto el costo por token, depende del tamaño de lote y de la carga de trabajo con que se midió, y no se transfiere entre configuraciones)

**Modelo borrador (draft model)**:
Un modelo pequeño y barato (o un mecanismo que no es un modelo, como la coincidencia de n-gramas, o cabezas adicionales en el propio modelo objetivo) que propone varios tokens siguientes candidatos para que el modelo objetivo los verifique en una sola pasada paralela, en lugar de generarlos él mismo uno a uno.
_Evitar_: una alternativa más pequeña y de menor calidad al modelo objetivo (la salida de un modelo borrador nunca se usa directamente; el modelo objetivo solo la verifica y, en su caso, la corrige)

**Presupuesto de error**:
1 menos un objetivo de nivel de servicio: la cantidad de fallos permitidos frente a ese objetivo antes de considerar que un servicio incumple. Una sola solicitud fallida no es un problema por sí misma; lo que importa es si la tasa de fallos consume el presupuesto más rápido de lo que permite la ventana de medición del SLO.
_Evitar_: tratar cualquier medición fallida aislada como un problema (el presupuesto existe precisamente porque se espera y se tolera cierta tasa de fallos; solo importa la tasa de consumo frente a la ventana)

**KV cache**:
Los vectores key y value almacenados de cada token ya generado, en cada capa, que se conservan para que un servidor nunca tenga que recalcularlos para los tokens posteriores. Su tamaño crece de forma lineal con la longitud de la secuencia y a menudo es el cuello de botella de memoria al servir, y no los pesos del propio modelo.
_Evitar_: caché de atención, almacén clave-valor

**Enrutamiento consciente de la KV cache**:
Una política de enrutamiento de solicitudes a nivel de flota que envía una solicitud nueva al servidor que ya tiene la mayor tasa de aciertos de caché para ella, en lugar de enrutar solo según la carga (round-robin, menos conexiones). Extiende el beneficio por servidor del prefix caching a una flota de varios servidores, haciendo que la propia decisión de enrutamiento sepa dónde vive ya una caché coincidente.
_Evitar_: el balanceo de carga ordinario (el round-robin o el de menos conexiones ignoran por completo la localidad de la caché y pueden enviar una solicitud favorable a la caché a un servidor que tiene que rehacer el prefill desde cero)

**Limitado por el ancho de banda de memoria**:
Un cálculo cuyo costo dominante es mover datos (como los pesos de un modelo) de la memoria a la unidad de cómputo, y no la aritmética que se hace una vez que llegan esos datos. La decodificación autorregresiva ordinaria está limitada por el ancho de banda de memoria, y eso es exactamente lo que permite a la speculative decoding verificar varios tokens candidatos en una pasada por aproximadamente el costo de generar uno solo.
_Evitar_: limitado por cómputo (el régimen opuesto, donde domina la aritmética; confundirlos hace perder de vista por qué el trabajo extra de verificación es casi gratis específicamente durante el decode)

**Burbuja de pipeline**:
El tiempo ocioso que pasan esperando los dispositivos de una configuración de pipeline parallelism, al comienzo (mientras el pipeline se llena) y al final (mientras se vacía) del procesamiento de un lote, ya que no todos los dispositivos tienen trabajo en esos momentos. Dividir un lote en más micro-lotes reduce esta fracción ociosa, pero nunca la elimina.
_Evitar_: asumir que los micro-lotes eliminan por completo la burbuja (solo reducen la fracción ociosa respecto del trabajo total; un retraso de arranque y de vaciado permanece sin importar el número de micro-lotes)

**Pipeline parallelism**:
Repartir la secuencia de capas de un modelo en grupos consecutivos colocados en dispositivos distintos, de modo que los datos fluyen por los dispositivos en el mismo orden en que las capas se ejecutarían en uno solo. La comunicación ocurre únicamente en la frontera entre el grupo de un dispositivo y el siguiente, lo que le permite tolerar un enlace entre dispositivos más lento que el que necesita el tensor parallelism y abarcar varios nodos.
_Evitar_: dividir el cálculo dentro de una sola capa (eso es tensor parallelism; el pipeline parallelism nunca divide lo que ocurre dentro de una capa, solo qué capas van adónde)

**Prefix caching**:
Reutilizar la KV cache ya calculada de un prefijo compartido entre solicitudes por lo demás no relacionadas (un system prompt común, un documento consultado repetidamente, turnos anteriores de una conversación), con el mismo mecanismo de compartición de bloques que PagedAttention usa dentro de las muestras paralelas de una solicitud, extendido entre solicitudes. Acelera solo el prefill; el tiempo de decode no cambia.
_Evitar_: asumir que también acelera el decode (solo evita el cálculo de prefill redundante para un prefijo coincidente; generar tokens nuevos después cuesta exactamente lo mismo en ambos casos)

**Escalado de RoPE**:
Ampliar la longitud de contexto que un modelo puede manejar más allá de su longitud de entrenamiento reescalando cómo los rotary position embeddings codifican la distancia entre tokens (el enfoque de YaRN: escalar menos las dimensiones de alta frecuencia y más las de baja frecuencia), en lugar de reentrenar desde cero. No cambia nada sobre cuántos keys y values de tokens se guardan en la caché; un contexto más largo manejado así sigue costando por completo el crecimiento lineal habitual de la KV cache.
_Evitar_: asumir que reduce o limita la memoria de la KV cache (solo amplía la longitud máxima de contexto utilizable; la caché de ese contexto más largo crece exactamente como lo haría sin ningún escalado)

**SLI (indicador de nivel de servicio)**:
Una razón cuantitativa y relevante para el usuario, elegida a partir de una métrica exportada en bruto, por ejemplo la fracción de solicitudes con un TTFT por debajo de un umbral declarado, formulada desde la experiencia del usuario y no desde el estado interno del servidor.
_Evitar_: el propio histograma de una métrica en bruto (un histograma son datos medidos; un SLI es la razón concreta, relevante para el usuario, que se elige de él para fijarle un objetivo)

**Atención de ventana deslizante (sliding-window attention)**:
Restringir cada token a atender como máximo a un número fijo, `W`, de tokens precedentes, en lugar de a toda la secuencia hasta ese momento, junto con una caché de buffer rotativo que solo guarda en todo momento los keys y values de `W` tokens. Limita la KV cache de una secuencia a un tamaño constante sin importar cuánto crezca la secuencia, a diferencia del crecimiento lineal intacto del escalado de RoPE.
_Evitar_: asumir que amplía hasta dónde puede ver útilmente un modelo igual que el escalado de RoPE (limita la caché y acota la atención directa a los últimos `W` tokens; lo que queda más allá solo se alcanza de forma indirecta, a través de capas apiladas, y por sí sola sufre un colapso de calidad sin attention sinks)

**SLO (objetivo de nivel de servicio)**:
Un objetivo declarado para un SLI, por ejemplo "el 99% de las solicitudes tienen un TTFT inferior a 300 ms en 28 días móviles". Lo que sobra, 1 menos el SLO, es el presupuesto de error.
_Evitar_: el resultado de un benchmark puntual (el único p99 medido de la lección 16 es una instantánea; un SLO es un objetivo permanente frente a métricas exportadas de forma continua)

**Speculative decoding**:
Redactar varios tokens siguientes candidatos de forma barata y luego verificarlos todos en una sola pasada forward paralela por el modelo objetivo, aceptando las conjeturas correctas y volviendo a muestrear las incorrectas, de modo que la distribución de salida final coincide exactamente con la de ejecutar solo el modelo objetivo. Una palanca de latencia pura, sin compromiso de calidad.
_Evitar_: una técnica de aproximación (cambia solo cuántas pasadas forward costosas toma la generación, nunca lo que se genera)

**Tensor parallelism**:
Dividir las grandes multiplicaciones de matrices dentro de una sola capa (los bloques de atención y MLP de un transformer) entre dispositivos por columnas o por filas, de modo que cada dispositivo calcula su propia porción en paralelo y un paso de comunicación recombina el resultado verdadero en puntos concretos dentro de cada capa. Necesita una interconexión rápida (como NVLink), porque esa recombinación ocurre en la ruta crítica, en cada capa y en cada pasada forward.
_Evitar_: dividir capas enteras entre dispositivos (eso es pipeline parallelism; el tensor parallelism divide el cálculo dentro de una capa, nunca asigna capas enteras a dispositivos distintos)
