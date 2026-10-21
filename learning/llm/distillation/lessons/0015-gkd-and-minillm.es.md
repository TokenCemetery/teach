---
title: "15. GKD y MiniLLM"
description: "Muestrear del estudiante y puntuar con el profesor, y las elecciones de divergencia y de mezcla que lo acompañan"
type: lesson
---

# Lección 15. GKD y MiniLLM

**Vínculo con la misión:** La misión te pide ejecutar destilación on-policy y elegir sus ajustes, lo que exige saber qué hacen los dos mandos de GKD, qué hace MiniLLM de forma distinta y qué resultados vinieron de qué tarea.
**Fuente principal:** [Paper: "On-Policy Distillation of Language Models: Learning from Self-Generated Mistakes", Agarwal et al., 2023](https://arxiv.org/abs/2306.13649), secciones 2 a 4
**Requisitos previos:** [Lección 5](0005-forward-and-reverse-kl.md), [Lección 14](0014-exposure-bias.md), [Generalized knowledge distillation](../GLOSSARY.md), [Destilación on-policy](../GLOSSARY.md), [KL inversa](../GLOSSARY.md)

## Calentamiento

1. ▢ ¿Con qué secuencias entrena un paso de destilación on-policy, y qué modelo las decide?

<details markdown="1"><summary>Comprobación</summary>

Con secuencias que el estudiante genera durante el entrenamiento, así que las decide el estudiante. El profesor solo puntúa cada token que el estudiante eligió. Entrenar con secuencias fijas, ya sean humanas o escritas por el profesor, es [off-policy](../GLOSSARY.md).

</details>

2. ▢ La KL directa empuja al estudiante a cubrir cada modo del profesor y la KL inversa lo empuja a comprometerse con uno. ¿Cuál de las dos arriesga poner probabilidad en texto que el profesor considera improbable?

<details markdown="1"><summary>Comprobación</summary>

La KL directa, porque penaliza dejar de cubrir cualquier región que cubre el profesor, así que un estudiante pequeño se estira sobre regiones que no puede modelar bien. La KL inversa penaliza la probabilidad donde el profesor tiene poca, así que lo evita a costa de la diversidad.

</details>

3. ▢ ¿Cuál es la diferencia entre el exposure bias y que un estudiante sea simplemente demasiado pequeño?

<details markdown="1"><summary>Comprobación</summary>

El exposure bias trata de los prefijos: el estudiante entrena con prefijos que escribió otro y genera a partir de los suyos. Un estudiante demasiado pequeño tiene un límite de capacidad sobre lo que puede representar, que seguiría ahí aunque cada prefijo fuera suyo. El entrenamiento on-policy aborda lo primero y no puede eliminar lo segundo.

</details>

## Qué debes saber

### GKD: un bucle con dos mandos

Generalized knowledge distillation (GKD) es un algoritmo con dos hiperparámetros (Agarwal et al., Algoritmo 1). En cada paso saca un número aleatorio. Con probabilidad lambda genera secuencias del estudiante para un batch de prompts. En caso contrario toma un batch de un dataset fijo de secuencias de referencia o escritas por el profesor. Luego actualiza al estudiante para minimizar una divergencia entre las distribuciones de tokens del profesor y del estudiante, promediada sobre las posiciones, sin gradiente a través del muestreo.

Lambda es la **fracción de datos del estudiante**. Lambda 0 es la destilación supervisada ordinaria y lambda 1 es puramente on-policy. Las variantes "mixtas" del paper usan 0.5. Durante el entrenamiento el estudiante muestrea con temperatura 1 para mantener diversas sus secuencias.

El segundo mando es la divergencia. GKD usa la divergencia de Jensen-Shannon generalizada, JSD(beta), una mezcla acotada de las dos direcciones de la KL. Con la convención del paper, beta cerca de 0 se comporta como la KL directa y beta cerca de 1 como la KL inversa, así que 0.1, 0.5 y 0.9 son puntos a lo largo de esa línea. El trainer de TRL documenta la misma dirección: beta 0.0 aproxima la KL directa y beta 1.0 la KL inversa.

### Lo que encontró el paper, tarea por tarea

Los estudiantes son T5-small (77M), T5-base (250M) y T5-large (800M) de parámetros, destilados de un T5-XL afinado de unos 3B, así que el profesor es 38 veces, 12 veces y 3.8 veces mayor. Los resultados son los del propio paper sobre T5, no hechos generales sobre los LLM.

| Tarea | Métrica | Qué funcionó | Fuente en el paper |
|---|---|---|---|
| Resumen XSum | ROUGE-2 | GKD on-policy con JSD(0.9) superó a los baselines adicionales ImitKD y f-distill con decodificación voraz y con muestreo con temperatura. Las divergencias que buscan modos funcionaron mejor con muestreo con temperatura, y la divergencia importó poco con decodificación voraz | Sección 4.1, Figuras 3 y 4 |
| WMT14 inglés a alemán | BLEU | La JSD generalizada superó a la KL directa y a la inversa, con una brecha menor para el estudiante mayor. Solo los datos generados por el estudiante superaron a las otras mezclas de datos. La Figura 1 usó JSD(0.1) | Sección 4.2, Figura 6 |
| GSM8K con chain of thought | exactitud | Las cadenas generadas solo por el estudiante superaron a los datos fijos o mixtos. La KL directa funcionó bien, y la inversa también. Las mejoras se mantuvieron una vez que al menos el 25% de los datos era on-policy | Sección 4.3, Figuras 8 y 9 |
| Instruction tuning con FLAN | MMLU y BBH held-out | GKD on-policy con KL inversa superó claramente a la KL directa | Sección 4.4, Figura 10 |

El resumen de los autores es que la mejor divergencia depende de la tarea, mientras que los datos on-policy y mixtos superan de forma consistente a los datos fijos. Otros dos resultados merecen conocerse. En XSum con T5-small, GKD on-policy sobre una submuestra del 5%, sin resúmenes de referencia, superó a la KD supervisada y a ImitKD entrenadas con el dataset completo (sección 4.1). Promediadas sobre los tamaños de estudiante, las mejoras de rendimiento sobre el estudiante inicial fueron 2.1 veces las de la KD baseline en resumen, 1.7 veces en traducción y 1.9 veces en razonamiento aritmético (introducción).

Para el instruction tuning, el texto del paper y el pie de su Figura 10 discrepan sobre si el estudiante es T5-base o T5-large, así que esta lección no cita un tamaño de estudiante para esa tarea. El profesor alcanzó un 52.4% en MMLU y un 41% en BBH. Los autores hipotetizan que la KL inversa funciona ahí porque su naturaleza de búsqueda de modos hace que el modelo se centre en la intención principal de la instrucción, y lo presentan como una hipótesis, no como un hallazgo.

### MiniLLM: la KL inversa optimizada como una política

Gu et al. (MiniLLM) llegan al entrenamiento on-policy desde otra dirección. Sostienen que la KL directa hace que un estudiante de baja capacidad sobreestime las regiones de baja probabilidad del profesor, y en su lugar minimizan la KL inversa sobre secuencias completas. Como la esperanza es bajo la propia distribución del estudiante, derivan el gradiente con el teorema del policy gradient y lo entrenan como aprendizaje por refuerzo, con la razón logarítmica de la probabilidad del profesor y la del estudiante como señal por token.

El policy gradient simple tiene problemas, y el paper añade tres soluciones:

| Problema | Solución | Detalle |
|---|---|---|
| Varianza alta | Descomposición de un solo paso | El término por token se calcula sumando sobre el vocabulario en lugar de muestreando |
| Reward hacking: texto degenerado, como frases repetidas, que puntúa bien con el profesor | Muestreo mezclado con el profesor | Muestrear de alfa por el profesor más (1 menos alfa) por el estudiante en cada paso, con alfa 0.2 en los experimentos |
| Las salidas largas obtienen recompensas acumuladas pequeñas, así que el estudiante aprende a producir respuestas muy cortas o vacías | Normalización por longitud | Normalizar la recompensa acumulada por la longitud restante |

También añade recorte (clipping) y una pérdida de modelado de lenguaje sobre texto de preentrenamiento para mantener el rendimiento en benchmarks generales. El entrenamiento parte de un estudiante afinado con los datos de la tarea. Fíjate en la diferencia con GKD: las muestras de MiniLLM vienen en parte del profesor a través de la mezcla, así que no es puramente on-policy, y optimiza un objetivo a nivel de secuencia donde GKD promedia una divergencia a nivel de token.

### Los resultados de MiniLLM

La configuración es seguimiento de instrucciones sobre 15K ejemplos de Dolly, unos 12.5K para entrenamiento, con estudiantes de GPT-2 (120M a 760M, profesor GPT-2 1.5B), OPT (1.3B a 6.7B, profesor OPT 13B) y LLaMA (7B, profesor LLaMA 13B). Unas cuantas celdas de la Tabla 1, la puntuación media de retroalimentación de GPT-4 en DollyEval:

| Estudiante | Solo fine-tuning | KD estándar | SeqKD | MiniLLM | Profesor |
|---|---|---|---|---|---|
| OPT 1.3B | 52.6 | 52.7 | 51.0 | 60.7 | 70.3 |
| OPT 6.7B | 67.9 | 68.6 | 69.6 | 70.8 | 70.3 |
| LLaMA 7B | 73.0 | 73.7 | 73.6 | 76.4 | 79.0 |

La métrica de GPT-4 es la razón entre la puntuación de GPT-4 para la respuesta del modelo y su puntuación para la respuesta de referencia, así que es relativa, no absoluta. Los autores también informan de que los estudiantes a veces superan al profesor en Rouge-L y conjeturan que esto refleja exposure bias en el profesor. En calibración, el estudiante MiniLLM tuvo menos error que los baselines de KL directa pero aún por encima del profesor: en SST2, ECE 0.099 frente a 0.025 del profesor y 0.191 de la KD estándar (Tabla 2).

### Lo que no puedes concluir

Cada paper afinó su propio método con sus propios estudiantes, profesores y métricas, así que los números de arriba no clasifican a GKD frente a MiniLLM. No encontré una comparación directa en ninguno de los dos papers. Compara sus ideas, y prueba ambos en tu propio par.

### Una configuración ejecutable

El `GKDTrainer` de TRL expone ambos mandos como `lmbda` y `beta` en `GKDConfig`. Sus valores por defecto documentados son 0.5 para cada uno, con `temperature` 0.9 y `max_new_tokens` 128 para la generación, y `seq_kd` desactivado. El ejemplo de la documentación de abajo destila Qwen2-1.5B-Instruct en Qwen2-0.5B-Instruct. No lo ejecuté, así que comprueba la ruta de importación con la versión de TRL que instales, ya que la documentación actual sitúa GKD bajo `trl.experimental`.

```python
from datasets import Dataset
from transformers import AutoModelForCausalLM, AutoTokenizer
from trl.experimental.gkd import GKDConfig, GKDTrainer

tokenizer = AutoTokenizer.from_pretrained("Qwen/Qwen2-0.5B-Instruct")
student = AutoModelForCausalLM.from_pretrained("Qwen/Qwen2-0.5B-Instruct")
teacher = AutoModelForCausalLM.from_pretrained("Qwen/Qwen2-1.5B-Instruct")

train = Dataset.from_dict({"messages": [[
    {"role": "user", "content": "Hi, how are you?"},
    {"role": "assistant", "content": "I'm great thanks"},
]] * 100})

args = GKDConfig(
    output_dir="gkd-model",
    per_device_train_batch_size=1,
    lmbda=1.0,  # purely on-policy: every batch is student-generated
    beta=1.0,   # generalized JSD at the reverse-KL end
)
trainer = GKDTrainer(model=student, teacher_model=teacher, args=args,
                     processing_class=tokenizer, train_dataset=train)
trainer.train()
```

Los dos modelos comparten tokenizer porque son de la misma familia, lo que la lección 6 explicó que es necesario para la destilación de logits. La propia guía de la página de TRL coincide con el paper: los datos on-policy (`lmbda` alto) rinden mejor, y el mejor `beta` depende de la tarea y del método de evaluación.

## Práctica

1. ▢ En GKD, ¿qué ajustes de lambda y de la divergencia reproducen (a) la destilación supervisada y (b) la KD on-policy tal como las define el paper?

<details markdown="1"><summary>Comprobación</summary>

Ambas usan KL directa. Lambda 0 da la KD supervisada, donde el estudiante nunca genera, y lambda 1 da la KD on-policy, donde cada secuencia es del estudiante. Los valores intermedios son las variantes mixtas. La divergencia y la fuente de datos son mandos independientes, por eso aparece la misma KL directa en ambas.

</details>

2. ▢ En el experimento de instruction tuning de GKD con FLAN, ¿qué emparejamiento encontró el paper claramente mejor que su contraparte de KL directa?

    - a) KL directa, muestras del estudiante
    - b) KL inversa, muestras del estudiante
    - c) KL directa, secuencias fijas
    - d) KL inversa, secuencias fijas

<details markdown="1"><summary>Comprobación</summary>

**b)** GKD on-policy con KL inversa superó a los otros enfoques en la sección 4.4. (a) es la elección del paper para XSum y GSM8K con decodificación voraz, no para el instruction tuning. (c) y (d) usan datos fijos, que el paper encontró consistentemente más débiles que los datos generados por el estudiante.

</details>

3. ▢ Empareja cada solución de MiniLLM con el fallo que previene: (1) muestreo mezclado con el profesor, (2) normalización por longitud, (3) descomposición de un solo paso. Fallos: A, el estudiante devuelve respuestas muy cortas o vacías. B, varianza alta en el gradiente. C, el estudiante encuentra texto degenerado que el profesor puntúa bien.

<details markdown="1"><summary>Comprobación</summary>

(1) va con C, (2) con A, (3) con B. El muestreo mezclado con el profesor suprime las muestras degeneradas al mezclar al profesor en la distribución de muestreo. La normalización por longitud evita que las secuencias largas se penalicen por recompensas acumuladas pequeñas. La descomposición de un solo paso calcula el término por token sobre todo el vocabulario en lugar de muestreando, lo que reduce la varianza.

</details>

4. ▢ Un estudiante entrenado con un objetivo al estilo MiniLLM empieza a emitir una frase repetida a la que el profesor asigna alta probabilidad. ¿Qué truco apunta a esto, y qué valor usó el paper?

<details markdown="1"><summary>Pista</summary>

La puntuación del profesor es la recompensa. Una muestra degenerada que le gusta al profesor está explotando esa recompensa.

</details>

<details markdown="1"><summary>Comprobación</summary>

El muestreo mezclado con el profesor, que el paper introduce contra el reward hacking, con alfa 0.2 en todos sus experimentos (sección 3.1). El valor es la elección de ese paper en su configuración, así que trátalo como punto de partida, no como una constante.

</details>

5. ▢ Con la Tabla 1 de arriba, ¿qué proporción de la brecha entre el estudiante solo con fine-tuning y el profesor cierra MiniLLM para OPT 1.3B y para LLaMA 7B? ¿Qué no puedes concluir de la fila de OPT 6.7B?

<details markdown="1"><summary>Comprobación</summary>

OPT 1.3B: la brecha es 70.3 menos 52.6, que es 17.7, y MiniLLM gana 8.1, alrededor del 46%. LLaMA 7B: la brecha es 6.0 y MiniLLM gana 3.4, alrededor del 57%. En la fila de OPT 6.7B MiniLLM puntúa 70.8 frente a 70.3 del profesor, pero eso no muestra que el estudiante sea mejor: la métrica es relativa a respuestas de referencia, la diferencia es de medio punto, y es un par de modelos.

</details>

6. ▢ Quieres una ejecución puramente on-policy con KL inversa en TRL. ¿Qué dos valores de configuración fijas, y podrías ejecutarla si solo tuvieras el texto del profesor?

<details markdown="1"><summary>Comprobación</summary>

`lmbda=1.0` y `beta=1.0`. No: la divergencia necesita la distribución del profesor en cada posición de la secuencia del estudiante, así que necesitas el propio modelo profesor, no un volcado de texto almacenado. Con solo texto volverías al nivel de secuencia (lección 8). La opción `seq_kd` de TRL no cambia esto, ya que el profesor sigue dando retroalimentación específica por token.

</details>

## Prácticas en el mundo real

- [ ] Lee la sección 3.1 del paper de GKD. Escribe la pérdida en una línea, y luego rodea con un círculo dónde entran lambda y la divergencia.
- [ ] Abre la Tabla 1 del paper de MiniLLM y elige un estudiante en el que MiniLLM no superó al profesor en todas las columnas. Anota en qué métrica perdió y por cuánto.
- [ ] Mañana: sin apuntes, escribe qué controlan lambda y beta, nombra una tarea donde la KL inversa ganó en GKD, y nombra las tres soluciones de MiniLLM.

## Para profundizar

- [Destilación on-policy](../reference/on-policy-distillation.md)
- [Paper: "On-Policy Distillation of Language Models: Learning from Self-Generated Mistakes", Agarwal et al., 2023](https://arxiv.org/abs/2306.13649)
- [Paper: "MiniLLM: On-Policy Distillation of Large Language Models", Gu et al., 2023](https://arxiv.org/abs/2306.08543)
- [Documentation: "Generalized Knowledge Distillation Trainer", Hugging Face TRL](https://huggingface.co/docs/trl/main/en/gkd_trainer)
- [Recursos](../RESOURCES.md)

---

¿No termina de quedar claro? Vuelve a leer la fuente primaria de arriba, ya que esta lección la comprime y en la compresión es donde se escapa la comprensión. Consulta el [glosario](../GLOSSARY.md) por si algún término te resultó resbaladizo.

Si lo poco claro es la propia lección y no el material, eso es un defecto: [abre un issue](https://github.com/TokenCemetery/teach/issues).
