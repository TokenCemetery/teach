---
title: "Glosario"
description: "Términos canónicos de la cuantización de LLM"
type: glossary
---

# Glosario de la cuantización

Términos canónicos para los formatos numéricos, los métodos de cuantización, el hardware en el que se ejecutan y cómo se mide su costo. En este espacio de trabajo "cuantización" siempre significa reducir la precisión de los números de un modelo entrenado; nunca significa discretizar entradas.

## Términos

**Act-order**:
Una opción de GPTQ que cuantiza las columnas de una capa en orden decreciente de tamaño de activación, ordenándolas según la diagonal de la Hessiana. Está documentada en el código de los autores, no en el paper.
_Evitar_: desc_act sin presentarlo antes, reorder trick (el nombre que el paper de AWQ da a una variante de GPTQ)

**Activación**:
Un tensor que se calcula durante el forward pass, como la entrada de una capa lineal, a diferencia de un peso almacenado. Sus valores dependen de la entrada, así que su rango solo se conoce en tiempo de ejecución o se estima a partir de un calibration set.
_Evitar_: hidden state (válido para el residual stream en concreto), feature map

**Activación masiva**:
Un único valor de activación en un LLM que es varios órdenes de magnitud mayor que el resto, y que aparece en una dimensión fija y en tokens concretos, como el primero.
_Evitar_: outlier feature (un patrón relacionado pero distinto), pico

**Ancho de bits**:
El número de bits que se usa para almacenar un valor cuantizado, sin contar los bits que se gastan en su scale y su zero-point. Consulta bits efectivos por peso para el total.
_Evitar_: precisión (ambiguo respecto de los bits de mantisa), profundidad de bits

**Bits de exponente**:
Los bits de un formato de punto flotante que fijan la potencia de dos por la que se escala un valor, y por tanto su rango dinámico.
_Evitar_: bits de rango

**Bits de mantisa**:
Los bits de un formato de punto flotante que fijan con qué finura se espacian los valores dentro de una potencia de dos, y por tanto su precisión.
_Evitar_: significando (correcto, pero usa un solo término), bits de fracción

**Bits efectivos por peso**:
El almacenamiento medio por peso una vez incluidos los scales, los zero-points y cualquier otro metadato por grupo, por ejemplo unos 4.5 para pesos de 4 bits con un scale de 16 bits por grupo de 32.
_Evitar_: bpw sin definirlo, ancho de bits (que excluye los metadatos)

**Calibration set**:
Una muestra pequeña de entradas representativas que se pasa por el modelo para recoger estadísticas de activaciones, que un método post-entrenamiento usa para elegir rangos o para ponderar los errores de redondeo. No son datos de entrenamiento y la PTQ nunca hace backpropagation a través de él.
_Evitar_: conjunto de entrenamiento, dataset de calibración (válido, pero no "datos de calibración" para las propias estadísticas)

**Canal saliente**:
Un canal de entrada de una matriz de pesos cuyo error de cuantización importa más, y que AWQ encuentra por el tamaño de la activación con la que se encuentra y no por el tamaño de sus propios pesos.
_Evitar_: peso importante (válido en la prosa), canal outlier (el nombre del lado de los pesos para una outlier feature)

**Configuración de cuantización**:
La entrada `quantization_config` del `config.json` de un modelo, cuyas claves `quant_method` y otras le dicen a un cargador qué método, ancho de bits y tamaño de grupo usan los tensores almacenados.
_Evitar_: quantize config (un archivo aparte que escriben algunas herramientas), metadatos

**Cuantización**:
Representar los números de valor real de un modelo en un conjunto menor de niveles con menos bits, al precio de un error de aproximación acotado.
_Evitar_: compresión (más amplio), discretización

**Cuantización absmax**:
Cuantización simétrica cuyo rango de recorte es el mayor valor absoluto entre los valores que comparten un scale, de modo que no se recorta nada y el scale es ese valor dividido por el mayor nivel entero.
_Evitar_: escalado por máximo, cuantización ingenua

**Cuantización afín**:
Cuantización con un scale y un zero-point, de modo que la rejilla de enteros puede quedar asimétrica en torno a cero y cubrir un rango como [-0.2, 1.5] sin desperdiciar niveles.
_Evitar_: cuantización asimétrica (alias aceptado, pero usa un solo término), cuantización uniforme (también es cierto de la simétrica)

**Cuantización de la KV cache**:
Almacenar las keys y los values de atención en caché con menos bits, para recortar la memoria que crece con la longitud del contexto y el tamaño de lote.
_Evitar_: compresión de la caché (abarca también el desalojo), cuantización KV de pesos

**Cuantización dinámica**:
Calcular el scale de una activación en tiempo de ejecución a partir de los valores realmente presentes, en lugar de fijarlo de antemano con un calibration set. Contrasta con la cuantización estática.
_Evitar_: cuantización al vuelo, cuantización en runtime

**Cuantización estática**:
Fijar el scale de una activación de antemano con un calibration set, de modo que no se calcula ninguna estadística en tiempo de ejecución. Contrasta con la cuantización dinámica.
_Evitar_: cuantización offline

**Cuantización post-entrenamiento**:
Cuantizar un modelo ya entrenado sin entrenamiento adicional, usando como mucho un calibration set pequeño.
_Evitar_: PTQ en la prosa sin presentarla antes, cuantización one-shot

**Cuantización simétrica**:
Cuantización con el zero-point fijado en cero, de modo que la rejilla queda centrada en cero y solo se almacena un scale.
_Evitar_: cuantización solo con scale

**Cuantización solo de pesos**:
Almacenar los pesos en baja precisión y descuantizarlos dentro del kernel, mientras las activaciones y la aritmética siguen en 16 bits. Se escribe WxA16, como W4A16.
_Evitar_: cuantización de precisión mixta (más amplio)

**Descomposición de precisión mixta**:
Dividir una multiplicación de matrices de modo que las pocas dimensiones outlier se calculen en 16 bits y el resto en int8, el núcleo de LLM.int8().
_Evitar_: división de outliers, precisión mixta (más amplio)

**Descuantización**:
Llevar un entero cuantizado de vuelta a un valor real aproximado con su scale y su zero-point, ya sea para calcular en mayor precisión o para inspeccionar el error.
_Evitar_: descuantificar, descompresión

**Divergencia KL**:
Cuánto se aleja la distribución del siguiente token del modelo cuantizado de la del baseline, promediada sobre los tokens de un dataset. Vale 0 cuando ambas coinciden exactamente y no necesita respuestas etiquetadas.
_Evitar_: KLD sin definirla, distancia (ambiguo)

**Error de recorte**:
El error que se produce cuando los valores fuera del rango de recorte se fijan en sus extremos.
_Evitar_: error de saturación, desbordamiento

**Error de redondeo**:
El error que se produce cuando un valor dentro del rango de recorte se mueve al nivel más cercano de la rejilla; como mucho medio paso con round-to-nearest.
_Evitar_: ruido de cuantización (aceptado para el error combinado), pérdida de precisión

**Escalado de la pérdida**:
Multiplicar la pérdida por una constante antes de la backpropagation para que los gradientes pequeños sigan siendo representables en un formato de rango estrecho como fp16, y luego dividir la constante antes de la actualización de los pesos.
_Evitar_: escalado de gradientes (ambiguo respecto del gradient clipping)

**Fake quantization**:
Cuantizar y descuantizar de inmediato un tensor en el forward pass, de modo que el entrenamiento ve el error de redondeo y de recorte mientras la aritmética sigue en punto flotante.
_Evitar_: cuantización simulada (alias aceptado, pero usa un solo término), inyección de ruido de cuantización

**Flip**:
Una respuesta que pasa de correcta a incorrecta, o de incorrecta a correcta, entre un modelo baseline y su versión cuantizada ante la misma pregunta. Los flips en ambos sentidos se cancelan en un promedio de accuracy, así que se cuentan por separado.
_Evitar_: cambio de respuesta (también cuenta incorrecta a incorrecta), regresión (solo un sentido)

**Formato con scale por bloque**:
Un formato en el que un bloque pequeño de valores, como 32, comparte un scale almacenado junto a ellos, de modo que el tipo del elemento puede ser muy estrecho. MXFP4 y NVFP4 son ejemplos, igual que los tipos por bloque de GGUF.
_Evitar_: microscaling (es una sola familia, la MX de OCP), formato agrupado

**Formato nativo**:
Un formato numérico en el que las unidades de matrices de un chip multiplican directamente, a diferencia de un formato solo de almacenamiento, que debe convertirse a uno nativo antes de la multiplicación.
_Evitar_: formato soportado (ambiguo entre almacenamiento y cómputo)

**GGUF**:
El formato de modelo de un solo archivo de llama.cpp, que almacena tensores, a menudo en sus propios tipos de cuantización por bloque, junto con el tokenizer y los metadatos del modelo.
_Evitar_: GGML (la biblioteca y un formato anterior), formato llama

**GPTQ**:
Un método de cuantización de pesos post-entrenamiento que cuantiza los pesos de una capa columna por columna y actualiza los pesos aún no cuantizados para compensar cada error de redondeo, usando información de segundo orden de las activaciones de calibración.
_Evitar_: cuantización GPT, genérico para cualquier checkpoint de 4 bits

**Granularidad**:
Cuántos valores comparten un scale y un zero-point: un tensor entero (per-tensor), un canal de salida (per-channel), un token (per-token) o un grupo de tamaño fijo dentro de un canal (per-group).
_Evitar_: resolución, nivel de cuantización

**Hessiana**:
En GPTQ, la matriz `H = 2 X X^T` construida con las entradas de calibración de una capa, con una fila y una columna por cada feature de entrada. Registra qué features se mueven juntas y la comparten todas las filas de los pesos de la capa.
_Evitar_: matriz de curvatura, matriz de covarianza (cercana, pero no es el mismo objeto)

**Intensidad aritmética**:
El número de operaciones aritméticas que realiza un cálculo por cada byte que mueve desde la memoria, y que decide si está limitado por el ancho de banda de memoria o por cómputo en un chip dado.
_Evitar_: intensidad operacional, razón FLOP por byte (aceptada en una fórmula)

**Kernel**:
La rutina de GPU que realiza una operación, como una multiplicación de matrices en un esquema de cuantización dado. Un esquema solo corre rápido donde existe un kernel para él en el hardware.
_Evitar_: operador (más amplio), implementación

**Limitado por cómputo**:
Una carga de trabajo cuya velocidad está limitada por el throughput aritmético y no por mover bytes, típica del prefill y del decode con lotes grandes. Cuantizar solo los pesos no la acelera, y puede ralentizarla.
_Evitar_: limitado por FLOP (válido, pero usa un solo término)

**Limitado por el ancho de banda de memoria**:
Una carga de trabajo cuya velocidad está limitada por lo rápido que se mueven los bytes desde la memoria y no por la aritmética, típica del decode con lotes pequeños, donde cada peso se lee una vez por cada token generado.
_Evitar_: limitado por el ancho de banda (válido, pero usa un solo término), limitado por E/S

**Matriz de importancia**:
En llama.cpp, la importancia por peso estimada a partir de las activaciones sobre un texto de calibración, que se usa para ponderar el error de redondeo al elegir el scale de cada bloque.
_Evitar_: imatrix en la prosa sin presentarlo antes

**Notación WxAy**:
Abreviatura de los anchos de bits de pesos y activaciones de un esquema, como W8A8 para pesos y activaciones de 8 bits, a veces con KVz para la KV cache.
_Evitar_: escribir int4 cuando las activaciones no son también int4

**Outlier feature**:
Una dimensión del hidden state en la que las activaciones de un transformer son sistemáticamente mucho mayores que en las demás, en la mayoría de los tokens y las capas.
_Evitar_: canal outlier (aceptado para el canal de pesos correspondiente), feature emergente sin la palabra outlier

**Épsilon de máquina**:
La distancia entre 1 y el siguiente valor representable por encima de él en un formato de punto flotante, igual a 2 elevado a menos el número de bits de mantisa.
_Evitar_: unit roundoff (la mitad de esto con round-to-nearest), precisión

**Perplexity**:
La exponencial de la log-verosimilitud negativa promedio que un modelo asigna a un texto, usada como proxy rápido de cuánto dañó un cambio al modelo.
_Evitar_: PPL en la prosa sin presentarla antes, accuracy

**Piso de ruido**:
La variación entre ejecuciones y de muestreo de una puntuación, por debajo de la cual una diferencia entre un baseline y un modelo cuantizado no se distingue del azar.
_Evitar_: margen de error (el intervalo es cómo se reporta el piso), tolerancia

**Quantization-aware training**:
Entrenar o hacer fine-tuning de un modelo con fake quantization en el forward pass, de modo que los pesos se adapten al redondeo que enfrentarán.
_Evitar_: QAT en la prosa sin presentarlo antes, entrenamiento cuantizado (que calcula en baja precisión)

**Ridge point**:
La intensidad aritmética a la que la tasa aritmética máxima de un chip y su ancho de banda de memoria tardan lo mismo, por debajo de la cual un cálculo está limitado por el ancho de banda de memoria y por encima de la cual está limitado por cómputo.
_Evitar_: roofline knee, punto de cruce

**Rango de recorte**:
El intervalo de valores reales que un cuantizador asigna a su rejilla de enteros; los valores fuera de él se fijan en el extremo más cercano. Elegirlo intercambia error de recorte por error de redondeo.
_Evitar_: rango dinámico (es una propiedad del formato), rango de cuantización

**Rotación**:
Multiplicar las activaciones y los pesos de una capa por una matriz ortogonal y su transpuesta, lo que deja intacta la salida de la capa pero reparte los outliers entre muchos canales para que se cuanticen mejor.
_Evitar_: transformada de Hadamard (una elección de rotación), incoherence processing (la idea general)

**Round-to-nearest**:
Cuantizar cada valor de forma independiente a su nivel más cercano de la rejilla, sin datos y sin compensación de errores. Es el baseline con el que se compara todo otro método post-entrenamiento.
_Evitar_: RTN en la prosa sin presentarlo antes, cuantización ingenua

**Safetensors**:
Un formato de archivo de tensores con una longitud de encabezado de 8 bytes, un encabezado JSON con nombres de tensores, dtypes, formas y offsets, y luego los datos en bruto. Almacena solo tensores, así que el esquema de cuantización se describe en la configuración de cuantización.
_Evitar_: checkpoint (el conjunto completo de archivos), archivo de pesos

**Scale**:
El tamaño de paso de valor real entre niveles enteros adyacentes de un cuantizador, de modo que un valor real es aproximadamente el scale por su entero.
_Evitar_: paso (válido en una fórmula), multiplicador

**Straight-through estimator**:
Tratar el paso de redondeo como la función identidad en el backward pass, para que un gradiente pueda fluir a través de una operación cuya derivada real es cero casi en todas partes.
_Evitar_: STE en la prosa sin presentarlo antes, gradiente sustituto (más amplio)

**Super-bloque**:
En un k-quant de GGUF, un grupo de 256 pesos dividido en sub-bloques que tienen cada uno su propio scale, y esos scales se cuantizan frente a un scale de super-bloque de 16 bits.
_Evitar_: bloque (la unidad de 32 pesos de los tipos heredados)

**Tamaño de grupo**:
El número de valores consecutivos que comparten un scale en la cuantización per-group, como 32 o 128.
_Evitar_: tamaño de bloque (aceptado donde un formato lo llama así, como MX o GGUF)

**Zero-point**:
El entero que representa el cero real en la cuantización afín, elegido para que el cero sea exactamente representable.
_Evitar_: offset, sesgo
